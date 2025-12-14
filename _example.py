"""
A simple script that demonstates the most basic setup for a custom script.

It simple Creates a panel under 'Craig Tools' with a button that when pressed 
simply shows an info warning in blender and print's to the console.
"""
import bpy


bl_info = {
    "name": "Craig Tools - Basic Example",
    "author": "Craig",
    "version": (1, 0),
    "blender": (5, 0, 0),
    "location": "View3D > Sidebar > Craig Tools",
    "description": "Adds a Craig Tools panel with a button",
    "category": "Object",
}


#region Logic


#endregion


#region UI

class OBJECT_PT_craig_panel(bpy.types.Panel):
    bl_label = "Craig Tools"
    bl_idname = "OBJECT_PT_craig_panel"
    bl_space_type = 'VIEW_3D'       # 3D Viewport
    bl_region_type = 'UI'           # Sidebar
    bl_category = "Craig Tools"     # Tab name in sidebar

    def draw(self, context):
        layout = self.layout
        layout.operator("object.craig_button", icon='PLAY')


class OBJECT_OT_craig_button(bpy.types.Operator):
    bl_idname = "object.craig_button"
    bl_label = "Run Craig Script"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        # Replace this with your custom script logic
        self.report({'INFO'}, "Craig Button Executed!")
        print("Craig Tools: Button executed successfully.")

        return {'FINISHED'}

#endregion


#region Register/Unregister

classes = [
	OBJECT_PT_craig_panel, 
	OBJECT_OT_craig_button,
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