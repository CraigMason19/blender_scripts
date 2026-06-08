"""
Craig Tools - Collection to Mesh
--------------------------------

Copies all objects in a collection and joins them together. Optionally applies
modifiers and scale. The resultant mesh is placed into the root 'Scene Collection'.

This allows me to easily join multiple meshes into one for STL 3D printing. This 
means I can keep the originals to modify.
"""

import bpy

bl_info = {
    "name": "Craig Tools - Collection to Mesh",
    "author": "Craig",
    "version": (1, 0),
    "blender": (5, 0, 1),
    "location": "View3D > Sidebar > Craig Tools",
    "description": "Easily join objects in a collection into a single mesh.",
    "category": "3D View",
}

ADDON_PREFIX = "craig_collection_to_mesh"

IDS = {
    "props": f"{ADDON_PREFIX}_properties",
    "panel": f"{ADDON_PREFIX}_panel",
    "button": f"{ADDON_PREFIX}.button"
}

#region Logic
        
def foo(context):
    props = getattr(context.scene, IDS["props"])

    if props.apply_scale:
        print("Success!")

#endregion


#region UI

class CollectionToMeshProperties(bpy.types.PropertyGroup):
    collection: bpy.props.PointerProperty(
        name="Collection",
        type=bpy.types.Collection
    ) # type: ignore

    show_options: bpy.props.BoolProperty(
        name="Options",
        default=False
    ) # type: ignore

    apply_modifiers: bpy.props.BoolProperty(
        name="Apply Modifiers",
        default=True
    ) # type: ignore

    apply_scale: bpy.props.BoolProperty(
        name="Apply Scale",
        default=True
    ) # type: ignore


class CollectionToMeshPanel(bpy.types.Panel):
    bl_label = "Collection To Mesh"
    bl_idname = IDS['panel']
    bl_space_type = "VIEW_3D"
    bl_region_type = "UI"
    bl_category = "Craig Tools"

    def draw(self, context):
        layout = self.layout
        props = getattr(context.scene, IDS["props"])

        layout.prop(props, "collection")

        # Collapsible options section
        box = layout.box()
        header = box.row(align=True)

        header.prop(
            props,
            "show_options",
            text="Options",
            emboss=False,
            icon='TRIA_DOWN' if props.show_options else 'TRIA_RIGHT'
        )

        # Add extra labels to force the 'Options' text to the left
        header.label(text="")
        header.label(text="")

        if props.show_options:
            col = box.column(align=True)
            col.prop(props, "apply_modifiers")
            col.prop(props, "apply_scale")

        # Button
        layout.operator(IDS["button"], text="Convert", icon='PLAY')


class CollectionToMeshButton(bpy.types.Operator):
    bl_label = "Collection To Mesh Button"
    bl_idname = IDS['button']
    bl_description = "Converts a collection into one mesh via joining"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        foo(context)

        self.report({'INFO'}, "Converted collection to mesh successfully.")
        return {'FINISHED'}
    
#endregion


#region Register/Unregister

classes = (
    CollectionToMeshProperties,
    CollectionToMeshPanel,
    CollectionToMeshButton,
)

def register():
    for cls in classes:
        bpy.utils.register_class(cls)

    setattr(bpy.types.Scene, IDS["props"],
        bpy.props.PointerProperty(type=CollectionToMeshProperties)
    )

def unregister():
    delattr(bpy.types.Scene, IDS["props"])

    for cls in reversed(classes):
        bpy.utils.unregister_class(cls)

#endregion


if __name__ == "__main__":
    register()