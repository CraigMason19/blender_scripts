import bpy

def create_bounding_box():
    """
    Click on a onject and then under Craig click create bounding box
    """
    obj = bpy.context.active_object
    minx, miny, minz = obj.bound_box[0]
    maxx, maxy, maxz = obj.bound_box[6]

    # Create a cube
    bpy.ops.mesh.primitive_cube_add()
    cube = bpy.context.active_object

    # Resize and move to objects location
    cube.scale = ((maxx - minx)/2, (maxy - miny)/2, (maxz - minz)/2)

    # Move to object
    cube.location = obj.matrix_world.translation

    # -? APPLY SCALE AFTER
    # rotation



have a panel Craig. Have a tool make bounding box

blender script - bounding box - click button - Craig Add on panel