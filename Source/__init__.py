bl_info = {
    "name": "2d-plus-depth Stereo Renderer",
    "author": "Veronika",
    "description": "",
    "blender": (2, 80, 0),
    "version": (0, 0, 1),
    "location": "",
    "warning": "",
    "category": "Render",
} # Blender addon metadata

import bpy
import os
from PIL import Image
import tempfile

class RenderStereo2DPlusDepth(bpy.types.Operator):
    bl_idname = "render.stereo_2d_plus_depth"
    bl_label = "Render 2D Plus Depth Stereo"
    bl_options = {'REGISTER', 'UNDO'}

    result_dir, result_name = None, None
    header_relative_path = "images/3dtv.bmp"
    image_size_x = 1920
    image_size_y = 2160
    image2d_name = "2D"
    imageDepth_name = "Depth"

    # Filepath specified by the user
    filepath: bpy.props.StringProperty(
        name="Result Image Filepath",
        description="Choose the directory and filename for the result image",
        subtype='FILE_PATH'
    )

    # Open file browser for the user to select a directory and file name
    def invoke(self, context, event):
        context.window_manager.fileselect_add(self)
        return {'RUNNING_MODAL'}

    # Check filepath and execute the rendering process
    def execute(self, context):
        self.result_dir, self.result_name = os.path.split(self.filepath)

        # Check if the output file already exists
        if os.path.exists(self.filepath) or os.path.exists(self.filepath + ".bmp"):
            self.report({'ERROR'}, f"File name already exists.")
            return {'CANCELLED'}

        # Check if the file name ends with ".bmp"
        if self.result_name.endswith(".bmp"):
            # Extract ".bmp" from the result_name and the filepath
            self.result_name = self.result_name[:-4]
            self.filepath = self.filepath[:-4]

        # Run the rendering process
        self.render_stereo_2d_plus_depth(context)
        self.report({'INFO'}, f"Rendered image saved at {self.filepath}.bmp")
        return {'FINISHED'}

    # Configure Blender rendering settings
    def setup_blender_env(self, context):
        render = context.scene.render

        # Configure render settings
        render.resolution_x = self.image_size_x
        render.resolution_y = self.image_size_y

    def setup_blender_for_depth(self, context):
        render = context.scene.render

        render.image_settings.color_mode = 'BW' # Black and white color mode
        render.image_settings.color_depth = '8' # 8-bit color depth
        render.image_settings.compression = 0 # No compression

        # Ensure only depth pass is enabled for the view layer
        view_layer = context.view_layer
        view_layer.use_pass_combined = True # Disable usage of lighting, shadows, reflections, etc.
        view_layer.use_pass_z = True # Enable Z (depth) pass

    # Setup compositor nodes for depth map rendering
    def set_tree_nodes(self, tree, tmp_path):
        render_layer_node = tree.nodes.new('CompositorNodeRLayers')
        normalize_node = tree.nodes.new(type="CompositorNodeNormalize")
        invert_node = tree.nodes.new(type="CompositorNodeInvert")

        file_output_node = tree.nodes.new(type="CompositorNodeOutputFile")
        file_output_node.base_path = "" # Clear base path
        file_output_node.file_slots[0].path = os.path.join(tmp_path, self.imageDepth_name) # File path to save depth image
        file_output_node.format.file_format = 'BMP' # File format

        return render_layer_node, normalize_node, invert_node, file_output_node

    # Render the 2D color image
    def render_2d_image(self, context, tmp_path):
        render = context.scene.render

        # Set file path and format for the color image
        render.filepath = os.path.join(tmp_path, self.image2d_name)
        render.image_settings.file_format = 'BMP'

        # Render the 2D color image
        bpy.ops.render.render(write_still=True)

    # Link compositor nodes for depth map rendering
    def link_nodes(self, links, render_layer_node, normalize_node, invert_node, file_output_node):
        # Link the render layer depth output to the normalize node input
        links.new(render_layer_node.outputs[2], normalize_node.inputs[0])
        # Link the normalize node output to the invert node input color
        links.new(normalize_node.outputs[0], invert_node.inputs[1])
        # Link the invert node output to the file output node
        links.new(invert_node.outputs[0], file_output_node.inputs[0])

    # Render the depth map image
    def render_depth_image(self, context, tmp_path):
        scene = context.scene
        scene.use_nodes = True # Enable compositing nodes
        tree = scene.node_tree
        links = tree.links

        # Configure Blender rendering settings
        self.setup_blender_for_depth(context)

        # Clear any existing nodes in the node tree
        tree.nodes.clear()

        # Setup and link compositor nodes
        self.link_nodes(links, *self.set_tree_nodes(tree, tmp_path))

        # Render the abstracted depth map
        bpy.ops.render.render(write_still=True)

    # Combine 2D, depth, and header images into one file
    def render_combined_image(self, tmp_path, header_path):

        combined_image = Image.new("RGBA", (self.image_size_x * 2, self.image_size_y))

        image = Image.open(os.path.join(tmp_path, self.image2d_name + ".bmp"))
        depth = Image.open(os.path.join(tmp_path, self.imageDepth_name + "0000.bmp"))
        header = Image.open(header_path)

        combined_image.paste(image, (0, 0)) # Paste the 2D image to the right side of the combined image
        combined_image.paste(depth, (image.width, 0)) # Paste the depth image to the left side of the combined image
        combined_image.paste(header, (0, 0)) # Paste the header image to the top of the combined image

        # Save the combined image
        combined_image_path = self.filepath + ".bmp"
        combined_image.save(combined_image_path)

    # Main rendering function
    def render_stereo_2d_plus_depth(self, context):
        # Find header image in the addon directory
        addon_directory = os.path.dirname(os.path.realpath(__file__))
        header_path = os.path.join(addon_directory, self.header_relative_path)

        self.setup_blender_env(context)

        # Use temporary directory for the rendered images
        with tempfile.TemporaryDirectory() as tmp_path:
            self.render_2d_image(context, tmp_path)
            self.render_depth_image(context, tmp_path)
            self.render_combined_image(tmp_path, header_path)

# Add the operator to the Render menu
def menu_func(self, context):
    self.layout.operator(RenderStereo2DPlusDepth.bl_idname)

# Register the operator and menu item
def register():
    bpy.utils.register_class(RenderStereo2DPlusDepth)
    bpy.types.TOPBAR_MT_render.append(menu_func)

# Unregister the operator and menu item
def unregister():
    bpy.utils.unregister_class(RenderStereo2DPlusDepth)
    bpy.types.TOPBAR_MT_render.remove(menu_func)

if __name__ == "__main__":
    register()