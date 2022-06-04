import bpy
import bgl
import blf
import os
import bpy_extras
from bpy_extras import view3d_utils
import mathutils
import gpu
from gpu_extras.batch import batch_for_shader



class BL_UI_sidebar_Panel(bpy.types.Panel):
    bl_label = "Sidbar Panel"
    bl_idname = "glinfo.Panel"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = 'My Addon'
    #bl_options = {'REGISTER'}
    
    def draw(self, context):
        selflay = self.layout
        contscn = context.scene
        box = selflay.box()

        if context.window_manager.run_opengl is False:
            icon = 'PLAY'
            txt = 'Display or Acion'
        else:
            icon = 'PAUSE'
            txt = 'Hide'
        box.operator("glinfo.glrun", text=txt, icon=icon)
        box.prop(contscn,"gl_move_object", toggle=True, icon="UV_SYNC_SELECT")
        box.prop(contscn,"gl_display_names", toggle=True, icon="OUTLINER_OB_FONT")
        box.prop(contscn,"gl_display_lines", toggle=True, icon="IPO_LINEAR")
        row = selflay.row()
        row.label(text= "Add an Object", icon= 'CUBE')
        row = selflay.row()
        row.operator("mesh.primitive_cube_add", icon= 'CUBE')
        row = selflay.row()
        row.operator("mesh.primitive_uv_sphere_add" , icon = 'SPHERE')
        row = selflay.row()
        row.operator("object.text_add")
        row = selflay.row()
        selflay.prop(context.scene, 'my_float_vector_prop')
        row = selflay.row()
        
 
    @classmethod
    def register(cls):
        # Register properties related to the class here.,
        bpy.types.Scene.gl_move_object = bpy.props.BoolProperty(
            name="move object",
            description="Move object to a new position",
            default=True,
        )
               
        bpy.types.Scene.gl_display_names = bpy.props.BoolProperty(
            name="Names",
            description="Display names for selected meshes.",
            default=True,
        )
        bpy.types.Scene.gl_display_lines = bpy.props.BoolProperty(
            name="Lines",
            description="Display lines for selected vertices.",
            default=True,
        )


        print("Registered class:addon_test001-Panel001  %s " % cls.bl_label)

        
    @classmethod
    def unregister(cls):
        del bpy.types.Scene.gl_display_names
        del bpy.types.Scene.gl_display_lines
        del bpy.types.Scene.gl_move_object

        print("Unregistered class:addon_test001-Panel001  %s " % cls.bl_label)



