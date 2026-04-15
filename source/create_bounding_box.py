"""
Craig Tools - Create Bounding Box
---------------------------------



Creates a bfoo panel under the 'Craig Tools' tab in the 3D View sidebar. 



("AABB", "AABB (Axis Aligned Bounding Box)", "Axis-aligned bounding box"),
("OBB", "OBB (Oriented Bounding Box)", "Oriented bounding box"),




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
from mathutils import Vector, Matrix

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

def eigenvectors_3x3(m):
    # Convert Matrix to nested lists
    a = [
        [m[0][0], m[0][1], m[0][2]],
        [m[1][0], m[1][1], m[1][2]],
        [m[2][0], m[2][1], m[2][2]],
    ]

    # Jacobi eigenvalue algorithm
    import math

    def max_offdiag(a):
        n = 3
        max_val = 0.0
        p = 0
        q = 1
        for i in range(n):
            for j in range(i+1, n):
                if abs(a[i][j]) > max_val:
                    max_val = abs(a[i][j])
                    p = i
                    q = j
        return p, q, max_val

    # Initialize eigenvectors as identity
    v = [[1,0,0],[0,1,0],[0,0,1]]

    for _ in range(50):  # iterations
        p, q, max_val = max_offdiag(a)
        if max_val < 1e-10:
            break

        theta = 0.5 * math.atan2(2*a[p][q], a[q][q] - a[p][p])
        c = math.cos(theta)
        s = math.sin(theta)

        # Rotate matrix A
        for i in range(3):
            api = a[p][i]
            aqi = a[q][i]
            a[p][i] = c*api - s*aqi
            a[q][i] = s*api + c*aqi

        for i in range(3):
            aip = a[i][p]
            aiq = a[i][q]
            a[i][p] = c*aip - s*aiq
            a[i][q] = s*aip + c*aiq

        # Rotate eigenvectors
        for i in range(3):
            vip = v[i][p]
            viq = v[i][q]
            v[i][p] = c*vip - s*viq
            v[i][q] = s*vip + c*viq

    # Convert back to mathutils.Vector
    return [
        Vector((v[0][0], v[1][0], v[2][0])),
        Vector((v[0][1], v[1][1], v[2][1])),
        Vector((v[0][2], v[1][2], v[2][2])),
    ]

# -----------------------------
# Base class
# -----------------------------
@dataclass
class AABB_Base:
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
class AABB_3D(AABB_Base):

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
class AABB_2D(AABB_Base):
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

# -----------------------------
# BlenderBB
# -----------------------------
class BlenderBB:
    def __init__(self, obj):
        # obj.bound_box is in local space
        local_corners = [Vector(corner) for corner in obj.bound_box]
        self.verts = local_corners

        # Transform to world space
        # self.verts = [obj.matrix_world @ v for v in local_corners]

    @property
    def faces(self):
        return [
            (0,1,2,3),
            (4,5,6,7),
            (0,1,5,4),
            (2,3,7,6),
            (0,3,7,4),
            (1,2,6,5),
        ]
    
# -----------------------------
# OBB_3D
# -----------------------------
@dataclass
class OBB_3D:
    verts_world: list[Vector]   # list of world-space vertices

    @property
    def rotation(self):
        """Compute PCA rotation matrix (3x3)."""
        # Compute centroid
        centroid = sum(self.verts_world, Vector()) / len(self.verts_world)

        # Build covariance matrix
        cov = Matrix(((0,0,0),(0,0,0),(0,0,0)))
        for v in self.verts_world:
            d = v - centroid
            cov[0][0] += d.x * d.x
            cov[0][1] += d.x * d.y
            cov[0][2] += d.x * d.z
            cov[1][0] += d.y * d.x
            cov[1][1] += d.y * d.y
            cov[1][2] += d.y * d.z
            cov[2][0] += d.z * d.x
            cov[2][1] += d.z * d.y
            cov[2][2] += d.z * d.z
        
        # Eigenvectors = principal axes
        eig = eigenvectors_3x3(cov)
        R = Matrix((eig[0], eig[1], eig[2])).transposed()
        return R, centroid

    def extents(self):
        """Return half-sizes along PCA axes (hx, hy, hz)."""
        R, centroid = self.rotation

        # Transform verts into PCA space
        local = [(R @ (v - centroid)) for v in self.verts_world]

        xs = [v.x for v in local]
        ys = [v.y for v in local]
        zs = [v.z for v in local]

        hx = (max(xs) - min(xs)) * 0.5
        hy = (max(ys) - min(ys)) * 0.5
        hz = (max(zs) - min(zs)) * 0.5

        return hx, hy, hz


    @property
    def verts(self):
        R, centroid = self.rotation

        # Transform verts into PCA space
        local = [(R @ (v - centroid)) for v in self.verts_world]

        # Compute min/max in PCA space
        xs = [v.x for v in local]
        ys = [v.y for v in local]
        zs = [v.z for v in local]

        mn = Vector((min(xs), min(ys), min(zs)))
        mx = Vector((max(xs), max(ys), max(zs)))

        # 8 corners in local PCA space
        corners_local = [
            Vector((mn.x, mn.y, mn.z)),
            Vector((mn.x, mn.y, mx.z)),
            Vector((mn.x, mx.y, mn.z)),
            Vector((mn.x, mx.y, mx.z)),
            Vector((mx.x, mn.y, mn.z)),
            Vector((mx.x, mn.y, mx.z)),
            Vector((mx.x, mx.y, mn.z)),
            Vector((mx.x, mx.y, mx.z)),
        ]

        # Transform back to world space
        corners_world = [(R.transposed() @ v) + centroid for v in corners_local]
        return corners_world

    @property
    def faces(self):
        return [
            (0,1,3,2), (4,6,7,5),
            (0,4,5,1), (2,3,7,6),
            (0,2,6,4), (1,5,7,3)
        ]
        
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
        aabb_name = obj.name + "_aabb"
    else:
        plane = context.scene.craig_bbox_plane  # XY / XZ / YZ
        aabb = AABB_2D(min_corner, max_corner, plane)
        aabb_name = f"{obj.name}_aabb_{plane}"


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
    
    return True


def create_blender_bounding_box(context):
    """
    Creates a bounding box using Blender's built-in bound_box.
    This matches the 'Bounds' display in the viewport.
    """
    obj = context.active_object

    if obj is None:
        print("No active object selected.")
        return

    blender_bb = BlenderBB(obj)

    blenderbb_name = obj.name + "_blender_bb"

    # Create mesh + object.
    blenderbb_mesh = bpy.data.meshes.new(blenderbb_name)
    blenderbb_obj = bpy.data.objects.new(blenderbb_name, blenderbb_mesh)
    blenderbb_obj.matrix_world = obj.matrix_world.copy()
    bpy.context.collection.objects.link(blenderbb_obj)

    blenderbb_mesh.from_pydata(blender_bb.verts, [], blender_bb.faces)
    blenderbb_mesh.update()

    # Select + set origin
    bpy.ops.object.select_all(action='DESELECT')
    blenderbb_obj.select_set(True)
    bpy.context.view_layer.objects.active = blenderbb_obj
    bpy.ops.object.origin_set(type='ORIGIN_GEOMETRY', center='BOUNDS')

    # Wireframe display?
    if context.scene.craig_bbox_wireframe:
        blenderbb_obj.display_type = 'WIRE'

    return True


def create_OBB_bounding_box(context):
    # Grab a reference to the object that the operator was used on.
    obj = context.active_object

    if obj is None:
        print("No active object selected.")
        return

    depsgraph = bpy.context.evaluated_depsgraph_get()
    eval_obj = obj.evaluated_get(depsgraph)
    mesh = eval_obj.to_mesh()  # use the evaluated mesh (with modifiers applied); use obj.data for the original base mesh without modifiers


    world_verts = [obj.matrix_world @ v.co for v in mesh.vertices]

    obb = OBB_3D(world_verts)
    obb_name = obj.name + "_obb"


    # Build the bounding box mesh:
    # 1. Create a new mesh datablock
    # 2. Create an object using that mesh
    # 3. Link the object into the active collection
    # 4. Fill the mesh with the AABB/OBB vertices and faces
    # 5. Finalize the mesh so Blender can use it
    obb_mesh = bpy.data.meshes.new(obb_name)
    obb_obj = bpy.data.objects.new(obb_name, obb_mesh)
    bpy.context.collection.objects.link(obb_obj)
    obb_mesh.from_pydata(obb.verts, [], obb.faces)
    obb_mesh.update()

    # Make it selected + active + set origin to geometry
    bpy.ops.object.select_all(action='DESELECT')
    obb_obj.select_set(True)
    bpy.context.view_layer.objects.active = obb_obj
    bpy.ops.object.origin_set(type='ORIGIN_GEOMETRY', center='BOUNDS')

    # Enable wireframe?
    if context.scene.craig_bbox_wireframe:
        obb_obj.display_type = 'WIRE'

    # IMPORTANT: free the evaluated mesh
    eval_obj.to_mesh_clear()

    return True

#endregion


#region UI

bpy.types.Scene.craig_bbox_alignment = bpy.props.EnumProperty(
    name="Bounding Box Alignment",
    description="Choose between AABB (Axis Aligned Bounding Box), BlenderBB (Blender Bounds Box) or OBB (Oriented Bounding Box)",
    items=[
        ("AABB", "AABB (Axis Aligned Bounding Box)", "Axis-aligned bounding box"),
        ("BlenderBB", "BlenderBB (Blender Bounds Box)", "Blender bounds box"),
        ("OBB", "OBB (Oriented Bounding Box)", "Oriented bounding box"),
    ],
    default="AABB"
)

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


class OBJECT_PT_create_bounding_box_panel(bpy.types.Panel):
    bl_label = "Create Bounding Box"
    bl_idname = "OBJECT_PT_create_bounding_box_panel"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = "Craig Tools"

    def draw(self, context):
        layout = self.layout
        scene = context.scene

        # Alignment selector (always enabled)
        row = layout.row()
        row.prop(scene, "craig_bbox_alignment")

        # Wireframe toggle
        layout.prop(scene, "craig_bbox_wireframe")

        # Disable 2D mode for OBB
        row = layout.row()
        row.enabled = scene.craig_bbox_alignment == "AABB"
        row.prop(scene, "craig_bbox_3d_mode")

        # Disable plane selection when 3D mode is enabled OR alignment is OBB
        row = layout.row()
        row.enabled = (not scene.craig_bbox_3d_mode) and (scene.craig_bbox_alignment == "AABB")
        row.prop(scene, "craig_bbox_plane")

        layout.operator("object.create_bounding_box_button", icon='PLAY')



class OBJECT_OT_create_bounding_box_button(bpy.types.Operator):
    bl_label = "Create Bounding Box"
    bl_idname = "object.create_bounding_box_button"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        ok = False

        match context.scene.craig_bbox_alignment:
            case "AABB":
                ok = create_AABB_bounding_box(context)
            case "OBB":
                ok = create_OBB_bounding_box(context)
            case "BlenderBB":
                ok = create_blender_bounding_box(context)

        if not ok:
            self.report({'ERROR'}, "Bounding box creation failed — no valid object selected.")
            return {'CANCELLED'}

        self.report({'INFO'}, "Bounding box creation successful.")
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