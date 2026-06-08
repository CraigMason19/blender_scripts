"""
Craig Tools - Collection to Mesh
--------------------------------

Copies all objects in a collection and joins them together. Optionally applies
modifiers and scale. The resultant mesh is placed into the root 'Scene Collection'.

This allows me to easily join multiple meshes into one for STL 3D printing. This 
means I can keep the originals to modify.

NOTE: Boolean cutters Should be in a collection different to the meshes.
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

def get_collection(
    context: bpy.types.Context,
    props: "CollectionToMeshProperties"
) -> bpy.types.Collection:

    if not props.collection:
        raise ValueError("No collection selected")
    
    return props.collection


def duplicate_objects(
    context : bpy.types.Context, 
    collection : bpy.types.Collection
) -> list[bpy.types.Object]:
    
    if not collection.objects: 
        raise ValueError("Collection is empty") 

    dupe_objects = []

    for obj in collection.objects:
        dupe = obj.copy()

        if obj.data:
            dupe.data = obj.data.copy()

        context.scene.collection.objects.link(dupe)
        dupe_objects.append(dupe)

    return dupe_objects


def apply_scale(
    context: bpy.types.Context,
    props: "CollectionToMeshProperties",
    objects: list[bpy.types.Object] | None
) -> None:

    if not objects:
        raise ValueError("Can't apply scale, No objects given") 
    
    if not props.apply_scale:
        return   
    
    for obj in objects:
        context.view_layer.objects.active = obj
        bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)


def apply_modifiers(
    context: bpy.types.Context,
    props: "CollectionToMeshProperties",
    objects: list[bpy.types.Object] | None
) -> None:

    if not objects:
        raise ValueError("Can't apply modifiers, No objects given") 
    
    for obj in objects:
        context.view_layer.objects.active = obj

        if props.apply_modifiers:
            for mod in obj.modifiers:
                try:
                    bpy.ops.object.modifier_apply(modifier=mod.name)
                except:
                    raise ValueError(f"Can't apply modifier for {obj.name}")
                
        else:
            for mod in obj.modifiers:
                obj.modifiers.remove(mod)






def collection_to_mesh(context : bpy.types.Context) -> None:
    # Deselect everything before deletion to avoid StructRNA errors
    bpy.ops.object.select_all(action='DESELECT')




    props = getattr(context.scene, IDS["props"])

    collection = get_collection(context, props)

    dupe_objects = duplicate_objects(context, collection)
    apply_scale(context, props, dupe_objects)
    apply_modifiers(context, props, dupe_objects)


    # Join
    for dupe in dupe_objects:
        dupe.select_set(True)

    context.view_layer.objects.active = dupe_objects[0]
    bpy.ops.object.join()

    # Joined object (created by join)
    joined_obj = context.view_layer.objects.active

    # Rename joined mesh after the collection
    joined_obj.name = f"{collection.name.lower()}_joined"
    if joined_obj.data:
        joined_obj.data.name = f"{collection.name.lower()}_joined_mesh"

    # Ensure it's in the Scene Collection (avoid double-link error)
    if joined_obj.name not in context.scene.collection.objects:
        context.scene.collection.objects.link(joined_obj)

    # # Deselect everything before deletion to avoid StructRNA errors
    # bpy.ops.object.select_all(action='DESELECT')

    # Delete duplicates safely
    # for dupe in dupe_objects:
    #     if dupe != joined_obj:
    #         bpy.data.objects.remove(dupe, do_unlink=True)

    # Select only the final mesh
    # joined_obj.select_set(True)
    # context.view_layer.objects.active = joined_obj


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
        try:
            collection_to_mesh(context)

        except Exception as e:
            self.report({'ERROR'}, f"Failed: {e}")
            return {'CANCELLED'}

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