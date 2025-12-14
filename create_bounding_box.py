"""
A simple script that demonstates the most basic setup for a custom script.

It simple Creates a panel under 'Craig Tools' with a button that when pressed 
simply shows an info warning in blender and print's to the console.


because i wanted a cube to easilly show the dimensions of something for 3d priting. 3d boxes can be easier to duplicate and view / arrange etc. just useful


make sure it's 1.0

Craig Tools - Bounding Box Addon
--------------------------------

This module demonstrates the basic structure of a Blender addon.

Features:
- Registers a custom panel under the 'Craig Tools' tab in the 3D View sidebar.
- Provides a button that, when pressed, creates a bounding box around the
  currently selected object.
- Reports success in Blender's Info area and prints a message to the console.

The script shows how to:
- Define and register a Panel (`OBJECT_PT_*`) for UI.
- Define and register an Operator (`OBJECT_OT_*`) for actions.
- Implement simple logic to manipulate Blender objects.
- Cleanly register and unregister classes for addon management.







"""
import bpy


bl_info = {
    "name": "Craig Tools - Create Bounding Box", # Used for installation
    "author": "Craig",
    "version": (1, 0),
    "blender": (5, 0, 0),
    "location": "View3D > Sidebar > Craig Tools",
    "description": "Adds a bounding box around around a object",
    "category": "Object",
}


#region Logic

def create_bounding_box(context, display_wireframe):
    """
    Creates a bounding box around a object matching it's location and 
    rotation, but will be of unit scale.
    """
    obj = context.active_object

    if obj is None:
        print("No active object selected.")
        return
    

    minx, miny, minz = obj.bound_box[0]
    maxx, maxy, maxz = obj.bound_box[6]

    # Create cube
    bpy.ops.mesh.primitive_cube_add()
    cube = bpy.context.active_object

    # Scale, move and apply
    cube.scale = ((maxx - minx)/2, (maxy - miny)/2, (maxz - minz)/2)
    cube.matrix_world = obj.matrix_world.copy()
    bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)

    if display_wireframe:
        bpy.context.object.display_type = 'WIRE'

#endregion


#region UI

bpy.types.Scene.craig_bbox_wireframe = bpy.props.BoolProperty(
    name="Display Wireframe",
    description="Display bounding box as wireframe",
    default=True
)


class OBJECT_PT_create_bounding_box_panel(bpy.types.Panel):
    bl_label = "Create Bounding Box"
    bl_idname = "OBJECT_PT_create_bounding_box_panel"
    bl_space_type = 'VIEW_3D'       # 3D Viewport
    bl_region_type = 'UI'           # Sidebar
    bl_category = "Craig Tools"     # Tab name in sidebar

    def draw(self, context):
        layout = self.layout

        layout.prop(context.scene, "craig_bbox_wireframe")
        layout.operator("object.create_bounding_box_button", icon='PLAY')


class OBJECT_OT_create_bounding_box_button(bpy.types.Operator):
    bl_label = "Create Bounding Box"
    bl_idname = "object.create_bounding_box_button"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        create_bounding_box(context, context.scene.craig_bbox_wireframe)

        self.report({'INFO'}, "Bounding box creation successful.")
        print("Craig Tools: Bounding box creation successful.")

        return {'FINISHED'}

#endregion


#region Register/Unregister

classes = [
	OBJECT_PT_create_bounding_box_panel, 
	OBJECT_OT_create_bounding_box_button,
]

def register():
    for cls in classes:
        bpy.utils.register_class(cls)

def unregister():
    for cls in classes:
        bpy.utils.unregister_class(cls)

#endregion


if __name__ == "__main__":
    register()