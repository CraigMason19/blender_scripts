"""
Craig Tools - Create Bounding Box
---------------------------------



Creates a bfoo panel under the 'Craig Tools' tab in the 3D View sidebar. 








A simple script that demonstrates the most basic setup for a custom script.

It simple Creates a panel under 'Craig Tools' with a button that when pressed 
simply shows an info warning in blender and print's to the console.


because i wanted a cube to easily show the dimensions of something for 3d printing. 3d boxes can be easier to duplicate and view / arrange etc. just useful


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

from dataclasses import dataclass
from mathutils import Vector

bl_info = {
    "name": "Craig Tools - Create Bounding Box", # Used for installation
    "author": "Craig",
    "version": (1, 0),
    "blender": (5, 0, 1),
    "location": "View3D > Sidebar > Craig Tools",
    "description": "Adds a bounding box around around a object",
    "category": "Object",
}


#region Logic

# -----------------------------
# Base class
# -----------------------------
@dataclass
class AABBBase:
    min: Vector
    max: Vector

    @property
    def verts(self):
        raise NotImplementedError

    @property
    def faces(self):
        raise NotImplementedError


# -----------------------------
# 3D AABB (cube)
# -----------------------------
@dataclass
class AABB_3D(AABBBase):

    @property
    def verts(self):
        min, max = self.min, self.max
        return [
            (min.x, min.y, min.z),
            (min.x, min.y, max.z),
            (min.x, max.y, min.z),
            (min.x, max.y, max.z),
            (max.x, min.y, min.z),
            (max.x, min.y, max.z),
            (max.x, max.y, min.z),
            (max.x, max.y, max.z),
        ]

    @property
    def faces(self):
        return [
            (0,1,3,2), (4,6,7,5),
            (0,4,5,1), (2,3,7,6),
            (0,2,6,4), (1,5,7,3)
        ]


# -----------------------------
# 2D AABB (plane)
# plane: "XY", "XZ", "YZ"
# -----------------------------
@dataclass
class AABB_2D(AABBBase):
    plane: str = "XY"   # XY, XZ, YZ

    @property
    def verts(self):
        min, max = self.min, self.max

        if self.plane == "XY":
            z = (min.z + max.z) * 0.5
            return [
                (min.x, min.y, z),
                (min.x, max.y, z),
                (max.x, max.y, z),
                (max.x, min.y, z),
            ]

        if self.plane == "XZ":
            y = (min.y + max.y) * 0.5
            return [
                (min.x, y, min.z),
                (min.x, y, max.z),
                (max.x, y, max.z),
                (max.x, y, min.z),
            ]

        if self.plane == "YZ":
            x = (min.x + max.x) * 0.5
            return [
                (x, min.y, min.z),
                (x, min.y, max.z),
                (x, max.y, max.z),
                (x, max.y, min.z),
            ]

        raise ValueError(f"Unknown plane type: {self.plane}")

    @property
    def faces(self):
        return [(0, 1, 2, 3)]

    
    
def create_AABB_bounding_box(context):
    """
    Creates a bounding box that is aligned to the world axis.

    Computed by converting all vertices of an object into world coordinates, then finding the minimum and maximum along each axis.
    """

    # Grab a reference to the object that the operator was used on.
    obj = context.active_object

    if obj is None:
        print("No active object selected.")
        return

    depsgraph = bpy.context.evaluated_depsgraph_get()
    eval_obj = obj.evaluated_get(depsgraph)
    mesh = eval_obj.to_mesh()  # use the evaluated mesh (with modifiers applied); use obj.data for the original base mesh without modifiers


    world_verts = [obj.matrix_world @ v.co for v in mesh.vertices]

    min_corner = Vector((
        min(v.x for v in world_verts),
        min(v.y for v in world_verts),
        min(v.z for v in world_verts)
    ))

    max_corner = Vector((
        max(v.x for v in world_verts),
        max(v.y for v in world_verts),
        max(v.z for v in world_verts)
    ))

    # Create cube or plane
    if context.scene.craig_bbox_3d_mode:
        aabb = AABB_3D(min_corner, max_corner)
        aabb_name = obj.name + "_bb"
    else:
        plane = context.scene.craig_bbox_plane  # XY / XZ / YZ
        aabb = AABB_2D(min_corner, max_corner, plane)
        aabb_name = f"{obj.name}_bb_{plane}"

    # Build the bounding box mesh:
    # 1. Create a new mesh datablock
    # 2. Create an object using that mesh
    # 3. Link the object into the active collection
    # 4. Fill the mesh with the AABB/OBB vertices and faces
    # 5. Finalize the mesh so Blender can use it
    aabb_mesh = bpy.data.meshes.new(aabb_name)
    aabb_obj = bpy.data.objects.new(aabb_name, aabb_mesh)
    bpy.context.collection.objects.link(aabb_obj)
    aabb_mesh.from_pydata(aabb.verts, [], aabb.faces)
    aabb_mesh.update()

    # Make it selected + active + set origin to geometry
    bpy.ops.object.select_all(action='DESELECT')
    aabb_obj.select_set(True)
    bpy.context.view_layer.objects.active = aabb_obj
    bpy.ops.object.origin_set(type='ORIGIN_GEOMETRY', center='BOUNDS')

    # Enable wireframe?
    if context.scene.craig_bbox_wireframe:
        aabb_obj.display_type = 'WIRE'

    # IMPORTANT: free the evaluated mesh
    eval_obj.to_mesh_clear()


def create_OBB_bounding_box(context):
    pass

#endregion


#region UI

bpy.types.Scene.craig_bbox_wireframe = bpy.props.BoolProperty(
    name="Wireframe",
    description="Display bounding box as wireframe",
    default=True
)

bpy.types.Scene.craig_bbox_3d_mode = bpy.props.BoolProperty(
    name="3D Mode",
    description="Create a bounding box. Cube (3D) or Plane (2D)",
    default=True
)

bpy.types.Scene.craig_bbox_plane = bpy.props.EnumProperty(
    name="2D Plane",
    description="Choose which plane the 2D AABB lies on",
    items=[
        ("XY", "XY Plane", "Top view"),
        ("XZ", "XZ Plane", "Front view"),
        ("YZ", "YZ Plane", "Side view"),
    ],
    default="XY"
)

bpy.types.Scene.craig_bbox_alignment = bpy.props.EnumProperty(
    name="Bounding Box Alignment",
    description="Choose between AABB (Axis Aligned Bounding Box) or OBB (Oriented Bounding Box)",
    items=[
        ("AABB", "AABB (Axis Aligned Bounding Box)", "Axis-aligned bounding box"),
        ("OBB", "OBB (Oriented Bounding Box)", "Oriented bounding box"),
    ],
    default="AABB"
)


class OBJECT_PT_create_bounding_box_panel(bpy.types.Panel):
    bl_label = "Create Bounding Box"
    bl_idname = "OBJECT_PT_create_bounding_box_panel"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = "Craig Tools"

    def draw(self, context):
        layout = self.layout
        scene = context.scene

        layout.prop(scene, "craig_bbox_wireframe")
        layout.prop(scene, "craig_bbox_3d_mode")

        # Disable plane selection when 3D mode is enabled
        row = layout.row()
        row.enabled = not scene.craig_bbox_3d_mode
        row.prop(scene, "craig_bbox_plane")
        
        row = layout.row()
        row.prop(scene, "craig_bbox_alignment")

        layout.operator("object.create_bounding_box_button", icon='PLAY')


class OBJECT_OT_create_bounding_box_button(bpy.types.Operator):
    bl_label = "Create Bounding Box"
    bl_idname = "object.create_bounding_box_button"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        if context.scene.craig_bbox_alignment == "AABB":
            create_AABB_bounding_box(context)

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