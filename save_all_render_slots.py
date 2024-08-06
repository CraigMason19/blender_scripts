# Saves all images in render slots at once
 
import bpy
import pathlib

scene = bpy.context.scene

desktop_path = pathlib.Path.home() / 'Desktop'
image_prefix = 'render_result_slot_'
extension = scene.render.file_extension

for image in bpy.data.images:
    if image.type == 'RENDER_RESULT':
        print(image.name)
        
        for i in range(8):
            image.render_slots.active_index = i
            image_name = f"{image_prefix}{i+1}{extension}"
            
            try:
                image.save_render(f"{desktop_path}\\{image_name}", scene=scene)
                print(f"{image_name} saved")
            except :
                print(f"Slot {i+1} is empty")