# https://docs.blender.org/manual/en/latest/scene_layout/object/types.html

# Remember, to see print outputs...
# Window -> Toggle System console

# A simple script to easilly set the origins of multiple selected objects to either world or local (geometry)
 
import bpy

WORLD_ORIGIN = (0.0, 0.0, 0.0)
ALLOWED_TYPES = ["MESH",
                 "CURVE",
                ]
          
def get_allowed_object_types(objects):
    return [object for object in objects if object.type in ALLOWED_TYPES]
  
def origin_to_world(object):
    # Store the cursor location
    cursor = bpy.context.scene.cursor
    original_cursor_location = (cursor.location[0], cursor.location[1], cursor.location[2])   

    # Move the cursor to the world origin and set the object's origin
    cursor.location = WORLD_ORIGIN
    bpy.ops.object.origin_set(type='ORIGIN_CURSOR', center='MEDIAN')

    # Restore the cursor
    cursor.location = original_cursor_location

def origin_to_geometry(object):
    bpy.ops.object.origin_set(type='ORIGIN_GEOMETRY', center='MEDIAN')
    
def print_debug_information(objects):
    counter, object_count = {}, len(objects)

    for object in objects:
        if object.type not in counter:
            counter[object.type] = 0
        counter[object.type] += 1
    
    if object_count == 1:
        print(f'{object_count} object selected') 
    else:
        print(f'{object_count} objects selected')   
    print(f'{counter}')     
    
def main(debug=True):
    #object = bpy.context.active_object
    #objects = bpy.context.scene.objects
    objects = get_allowed_object_types(bpy.context.selected_objects)

    if not objects: # Empty
        if debug:
            print(f'No objects selected') 
        return

    if debug:        
        print_debug_information(objects)
    
    for object in objects:
#        origin_to_world(object)
        origin_to_geometry(object)
    
if __name__ == '__main__':
    main()