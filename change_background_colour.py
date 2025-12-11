"""
Script that demonstrates how to add a side panel with a dropdown option in the text editor N panel 
"""

import bpy

def update_background(self, context):
    """Update the background color in the 3D Viewport"""
    themes = bpy.context.preferences.themes[0].view_3d.space.gradients

    colors = {
        'WHITE': (1, 1, 1),
        'DARK_GRAY': (0.251, 0.251, 0.251),
        'CORNFLOWER_BLUE': (0.392, 0.584, 0.929)
    }

    themes.high_gradient = colors[self.background_theme]

class BackgroundColorChangerPanel(bpy.types.Panel):
    bl_label = "Background Color Changer"
    bl_idname = "TEXTEDITOR_PT_background_color_changer"
    bl_space_type = 'TEXT_EDITOR'
    bl_region_type = 'UI'
    bl_category = "Background Color Changer"

    def draw(self, context):
        layout = self.layout
        layout.prop(context.scene.background_props, "background_theme")

class BackgroundProperties(bpy.types.PropertyGroup):
    background_theme: bpy.props.EnumProperty(# type: ignore
        name="Background Theme",
        description="Select a background theme",
        items=[
            ('WHITE', "White", "Set background to white"),
            ('DARK_GRAY', "Dark Gray", "Set background to dark gray"),
            ('CORNFLOWER_BLUE', "Cornflower Blue", "Set background to cornflower blue")
        ],
        default='DARK_GRAY',
        update=update_background
    )

classes = [
    BackgroundColorChangerPanel, 
    BackgroundProperties,
] 

def register():
    for cls in classes:
        bpy.utils.register_class(cls)

    bpy.types.Scene.background_props = bpy.props.PointerProperty(type=BackgroundProperties)
    update_background(bpy.context.scene.background_props, bpy.context)

def unregister():
    for cls in classes:
        bpy.utils.unregister_class(cls)

    del bpy.types.Scene.background_props

if __name__ == "__main__":
    register()