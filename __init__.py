bl_info = {
    "name" : "bl_addon_test004",
    "author" : "klaus1",
    "description" : "Panel001",
    "blender" : (3, 1, 0),
    "version" : (0, 0, 1),
    "location" : "",
    "warning" : "",
    "category" : "Generic"
}

import bpy
import os


from .bl_ui_sidebar_panel import BL_UI_sidebar_Panel
from .bl_ui_glrun import BL_UI_OT_glrun


classes = ( BL_UI_sidebar_Panel, bl_ui_glrun)

#register and unregister all classes
def register():
    bpy.utils.register_class(BL_UI_sidebar_Panel)
    bpy.utils.register_class(BL_UI_OT_glrun)
       
    wm = bpy.types.WindowManager
    wm.run_opengl = bpy.props.BoolProperty(default=False)
    print("%s registration complete\n" % bl_info.get('name'))

def unregister():
    """
    wm = bpy.context.window_manager
    p = 'run_opengl'
    if p in wm:
        del wm[p]
    BL_UI_OT_glrun.handle_remove(BL_UI_OT_glrun, bpy.context)
    """
    
    bpy.utils.unregister_class(BL_UI_OT_glrun)
    bpy.utils.unregister_class(BL_UI_sidebar_Panel)
   
    print("%s unregister complete\n" % bl_info.get('name'))
    

if __name__ == "__main__":
    try:
        os.system('clear')
        unregister()
    except Exception as e:
        print(e)
        pass
    finally:
        register()
    
# Änderung 1

