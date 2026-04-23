"""
Craig Tools - Change Background Color
---------------------------------

Allows you to easily change the background colour of the viewport.
"""

import bpy

from dataclasses import dataclass


bl_info = {
    "name": "Craig Tools - Change Background Color",
    "author": "Craig",
    "version": (1, 0),
    "blender": (5, 0, 1),
    "location": "View3D > Sidebar > Craig Tools",
    "description": "Easily change the viewport background color",
    "category": "3D View",
}


#region Logic


@dataclass
class Color:
    name: str
    value: tuple

    @property
    def desc(self) -> str:
        return f"Set the viewport background to {self.name}."
    
COLOR_MAP = {
    'CORNFLOWER_BLUE': Color("Cornflower Blue", (0.392, 0.584, 0.929)),
    'DARK_GRAY': Color("Dark Gray", (0.251, 0.251, 0.251)),
    'LIGHT_GRAY': Color("Light Gray", (0.5, 0.5, 0.5)),
    'WHITE': Color("White", (1, 1, 1)),
}

DEFAULT_ENUM =  'LIGHT_GRAY'
DEFAULT_COLOR = (0.5, 0.5, 0.5)

def generate_items():
    items = []

    for k, v in COLOR_MAP.items():
        items.append(
            (k, v.name, v.desc)
        )
    
    return items
        
def update_background_from_enum(self, context):
    themes = bpy.context.preferences.themes[0].view_3d.space.gradients
    themes.high_gradient = COLOR_MAP[self.background_color_enum].value

def update_background_from_color(self, context):
    themes = bpy.context.preferences.themes[0].view_3d.space.gradients
    themes.high_gradient = self.background_color

#endregion


#region UI

class BackgroundColorChangeProperties(bpy.types.PropertyGroup):
    background_color_enum: bpy.props.EnumProperty(
        name="Background Preset",
        description="The color to change the background to",
        items=generate_items(),
        default=DEFAULT_ENUM,
        update=update_background_from_enum
    ) # type: ignore
    
    background_color: bpy.props.FloatVectorProperty(
        name="Background Color",
        description="The color to change the background to",
        subtype='COLOR',
        size=3,
        min=0.0,
        max=1.0,
        default=DEFAULT_COLOR,
        update=update_background_from_color
    ) # type: ignore

    
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