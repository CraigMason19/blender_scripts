import bpy
import os

class EXPORT_OT_OneToOneSheet(bpy.types.Operator):
    bl_idname = "export.one_to_one_sheet"
    bl_label = "Export 1:1 Sheet"
    bl_description = "Capture orthographic view of selected object and save as 1:1 sheet"

    axis: bpy.props.EnumProperty(
        name="View Axis",
        items=[
            ('TOP', "Top", ""),
            ('FRONT', "Front", ""),
            ('RIGHT', "Right", ""),
            ('LEFT', "Left", ""),
            ('BACK', "Back", ""),
            ('BOTTOM', "Bottom", "")
        ],
        default='TOP'
    )

    filepath: bpy.props.StringProperty(
        name="Filepath",
        default="//sheet.png",
        subtype='FILE_PATH'
    )

    def execute(self, context):

        # Find VIEW_3D area
        area = next((a for a in context.screen.areas if a.type == 'VIEW_3D'), None)
        if not area:
            self.report({'ERROR'}, "No 3D View found")
            return {'CANCELLED'}

        region = next((r for r in area.regions if r.type == 'WINDOW'), None)
        if not region:
            self.report({'ERROR'}, "No VIEW_3D window region found")
            return {'CANCELLED'}

        space = area.spaces.active

        # Save settings
        old_overlay = space.overlay.show_overlays
        old_shading = space.shading.type

        # Prepare viewport
        space.overlay.show_overlays = False
        space.shading.type = 'WIREFRAME'

        # Use temp override (Blender 4+)
        with bpy.context.temp_override(area=area, region=region, space_data=space):

            bpy.ops.view3d.view_axis(type=self.axis)
            bpy.ops.view3d.view_persportho()
            bpy.ops.view3d.view_selected()

            # Correct operator for Blender 4/5
            bpy.ops.render.opengl(write_still=True)

        # Save image
        bpy.ops.render.opengl(write_still=True)
        bpy.data.images["Render Result"].save_render(
            filepath=bpy.path.abspath(self.filepath)
        )

        # Restore settings
        space.overlay.show_overlays = old_overlay
        space.shading.type = old_shading

        self.report({'INFO'}, f"Saved 1:1 sheet to {self.filepath}")
        return {'FINISHED'}


def menu_func(self, context):
    self.layout.operator(EXPORT_OT_OneToOneSheet.bl_idname)


def register():
    bpy.utils.register_class(EXPORT_OT_OneToOneSheet)
    bpy.types.VIEW3D_MT_view.append(menu_func)


def unregister():
    bpy.types.VIEW3D_MT_view.remove(menu_func)
    bpy.utils.unregister_class(EXPORT_OT_OneToOneSheet)


if __name__ == "__main__":
    register()
