"""
    Script that translates one or more objects along an axis by a certain amount
"""

bl_info = {
    "name": "CRAIG - Translate Objects",
    "blender": (2, 80, 0),
    "category": "Object",
}

import bpy

class TranslateAlongAxisOperator(bpy.types.Operator):
    """Translates one or more objects along an axis by a certain amount"""
    bl_idname = "object.translate_along_axis" # Unique identifier for buttons and menu items to reference.
    bl_label = "Translate Along Axis"         # Display name in the interface.
    bl_options = {'REGISTER', 'UNDO'}         # Enable undo for the operator.

    @classmethod
    def poll(cls, context):
        """This method determines whether the operator is available"""
        return bool(context.selected_objects)

    # Define properties inside __annotations__ to avoid type checking issues in VSCode
    __annotations__ = {
        "amount": bpy.props.FloatProperty(
            name="Amount",
            description="Tranlation amount",
            default=1.0,
            min=-100.0,
            max=100.0
        ),
        "axis": bpy.props.EnumProperty(
            name="Axis",
            description="Translation axis",
            items=[
                ('X', "X Axis", "Move along X axis"),
                ('Y', "Y Axis", "Move along Y axis"),
                ('Z', "Z Axis", "Move along Z axis")
            ],
            default='X'
        ),
    }
    
    def execute(self, context):
        """called when running the operator"""        
        for obj in context.selected_objects:
            if self.axis == 'X':
                obj.location.x += self.amount
            elif self.axis == 'Y':
                obj.location.y += self.amount
            elif self.axis == 'Z':
                obj.location.z += self.amount

        # Lets Blender know the operator finished successfully.
        return {'FINISHED'}            
        

def menu_func(self, context):
    """Adds to the menu?"""
    self.layout.operator(TranslateAlongAxisOperator.bl_idname)

classes = [TranslateAlongAxisOperator]
    
def register():
    for cls in classes:
        bpy.utils.register_class(cls)
    
    bpy.types.VIEW3D_MT_object.append(menu_func)

def unregister():
    for cls in classes:
        bpy.utils.unregister_class(cls)
   
    bpy.types.VIEW3D_MT_object.remove(menu_func)      

if __name__ == "__main__":
    register()