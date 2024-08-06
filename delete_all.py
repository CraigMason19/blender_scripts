import bpy
from enum import Enum

# Made because I had issues with the BlenderKit Addon not deleting resources and having them hanging around


#delete all unused????
#delete_all(Resource.material)
#delete_unused_non_fakeuser(Resource.material)


class Resource(Enum):
    material = 0
    texture = 1

def delete_all_materials(all=True):
    if all:
        for material in bpy.data.materials:
            material.user_clear()
            bpy.data.materials.remove(material)
    else:
        #todo
        pass

def delete_all_textures():
    pass 

def delete_all(resource):
    if resource == Resource.material:
        delete_all_materials()

    if resource == Resource.texture:
        delete_all_textures()

delete_all(Resource.material)
#delete_all(Resource.texture)

# print(Resource.material)
# print(Resource.material.value)