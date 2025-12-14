"""

"""

import bpy


bl_info = {
    "name": "Craig Tools - Change Background Color",
    "author": "Craig",
    "version": (1, 0),
    "blender": (5, 0, 0),
    "location": "View3D > Sidebar > Craig Tools",
    "description": "Easilly change the viewport background color",
    "category": "3D View",
}


#region Logic

colors = {
    'WHITE': (1, 1, 1),
    'LIGHT_GRAY': (0.5, 0.5, 0.5),
    'DARK_GRAY': (0.251, 0.251, 0.251),
    'CORNFLOWER_BLUE': (0.392, 0.584, 0.929),
}

def update_background_from_enum(self, context):
    themes = bpy.context.preferences.themes[0].view_3d.space.gradients
    themes.high_gradient = colors[self.background_color_enum]

def update_background_from_color(self, context):
    themes = bpy.context.preferences.themes[0].view_3d.space.gradients
    themes.high_gradient = self.background_color

#endregion


#region UI

class BackgroundColorChangePanel(bpy.types.Panel):
    bl_label = "Change Background Color"
    bl_idname = "VIEW3D_PT_change_background_color"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = "Craig Tools"

    def draw(self, context):
        layout = self.layout
        layout.prop(context.scene.background_color_change_props, "background_color_enum")
        layout.prop(context.scene.background_color_change_props, "background_color")

class BackgroundColorChangeProperties(bpy.types.PropertyGroup):
    background_color_enum: bpy.props.EnumProperty(
        name="Background Preset",
        description="The color to change the background to",
        items=[
            ('WHITE', "White", "Set background to white"),
            ('LIGHT_GRAY', "Light Gray", "Set background to light gray"),
            ('DARK_GRAY', "Dark Gray", "Set background to dark gray"),
            ('CORNFLOWER_BLUE', "Cornflower Blue", "Set background to cornflower blue")
        ],
        default='DARK_GRAY',
        update=update_background_from_enum
    ) # type: ignore
    
    background_color: bpy.props.FloatVectorProperty(
        name="Background Color",
        description="The color to change the background to",
        subtype='COLOR',
        size=3,
        min=0.0,
        max=1.0,
        default=(0.2, 0.2, 0.2),  # dark gray
        update=update_background_from_color
    ) # type: ignore

#endregion


#region Register/Unregister

classes = [
    BackgroundColorChangePanel, 
    BackgroundColorChangeProperties,
] 

def register():
    for cls in classes:
        bpy.utils.register_class(cls)

    bpy.types.Scene.background_color_change_props = bpy.props.PointerProperty(type=BackgroundColorChangeProperties)


def unregister():
    del bpy.types.Scene.background_color_change_props

    for cls in classes:
        bpy.utils.unregister_class(cls)

if __name__ == "__main__":
    register()

#endregion