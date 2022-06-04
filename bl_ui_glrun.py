

import bpy
import bgl
import blf
import os
import bpy_extras
from bpy_extras import view3d_utils
from bpy.props import IntProperty, FloatProperty
import mathutils
import gpu
from gpu_extras.batch import batch_for_shader
from mathutils import Vector
import bmesh

class BL_UI_OT_glrun(bpy.types.Operator):
    """Main operator, flicks handler on/off"""
    bl_idname = "glinfo.glrun"
    bl_label = "Display object data"
    bl_description = "Display additional information in the 3D Viewport"
    # For storing function handler
    
    def __init__(self):
        self.draw_handle_2d = None
        self.draw_handle_3d = None
        self.draw_event = None
        self.draw_initial_mouse = None
        self.mouse_vert = None
        
        self.vertices = []
        #self.create_batch()
        
        self.offset: bpy.props.FloatVectorProperty(
            name="Offset",
            size=3,
        )
        self.first_mouse_x : IntProperty()
        self.first_value: FloatProperty()
    
    @classmethod
    def poll(cls, context):
        if context.area.type == 'VIEW_3D':
            return True
        return False
        

    
    def register_handlers(self,args, context):
        #wm = bpy.types.WindowManager
        #wm.run_opengl = bpy.props.BoolProperty(default=False)
        context.window_manager.run_opengl = True
        if self.draw_handle_2d is None:
            self.draw_handle_2d = bpy.types.SpaceView3D.draw_handler_add(
                self.draw_2d, args, 'WINDOW', 'POST_PIXEL')
        if self.draw_handle_3d is None:
            self.draw_handle_3d = bpy.types.SpaceView3D.draw_handler_add(
               self.draw_3d, args, 'WINDOW', 'POST_VIEW')
        if self.draw_event is None:
            self.draw_event = context.window_manager.event_timer_add(0.1, window=context.window)
        
    
    def unregister_handlers(self, context):
        """
        wm = bpy.context.window_manager
        p = 'run_opengl'
        if p in wm:
           del wm[p]
        """
        if self.draw_event is not None:
            context.window_manager.event_timer_remove(self.draw_event)
        if self.draw_handle_2d is not None:
            bpy.types.SpaceView3D.draw_handler_remove(self.draw_handle_2d, "WINDOW")
        if self.draw_handle_3d is not None:
            bpy.types.SpaceView3D.draw_handler_remove(self.draw_handle_3d, "WINDOW")
        context.window_manager.run_opengl = False
        
        self.draw_handle_2d = None
        self.draw_handle_3d = None
        self.draw_event  = None
        self.bvhtree = None


    """
    # Enable GL drawing and add handler
    @staticmethod
    def register_handlers(self, context):
        
        if BL_UI_OT_glrun._handle_2d is None:
            BL_UI_OT_glrun._handle_2d = bpy.types.SpaceView3D.draw_handler_add(
                draw_2d, (self, context), 'WINDOW', 'POST_PIXEL')
                
        if BL_UI_OT_glrun._handle_3d is None:
            BL_UI_OT_glrun._handle_3d = bpy.types.SpaceView3D.draw_handler_add(
                draw_3d, (self, context), 'WINDOW', 'POST_VIEW')     
        
        context.window_manager.run_opengl = True
        
   
    # Disable GL drawing and remove handler
    @staticmethod
    def handle_remove(self, context):
        
        if BL_UI_OT_glrun._handle_2d is not None:
            bpy.types.SpaceView3D.draw_handler_remove(BL_UI_OT_glrun._handle_2d, 'WINDOW')
        BL_UI_OT_glrun._handle_2d = None

        if BL_UI_OT_glrun._handle_3d is not None:
            bpy.types.SpaceView3D.draw_handler_remove(BL_UI_OT_glrun._handle_3d, 'WINDOW')
        BL_UI_OT_glrun._handle_3d = None
              
        context.window_manager.run_opengl = False
    """

    # Flicks OpenGL handler on and off
    # Make sure to flick "off" before reloading script when live editing
    #def execute(self, context):
    def invoke(self,context,event):
        if context.area.type == 'VIEW_3D':
            if context.window_manager.run_opengl is False:
                print("handle draw2d_3d and mouse timer add")
                args = (self,context)
                self.register_handlers(args, context)
                context.window_manager.modal_handler_add(self)
                context.area.tag_redraw() 
                return {'RUNNING_MODAL'}
                
            else:
                print("handle draw2d_3d and mouse timer  remove")
                self.unregister_handlers( context)
                print("event_timer_remove self._timer:",self.draw_event)
                context.area.tag_redraw()
            return {'FINISHED'}
        else:
            print("3D Viewport not found, cannot run operator.")
            return {'CANCELLED'}

    
    
    # mouse events
    def modal(self,context,event):
        if event.type in {'RIGHTMOUSE', 'ESC'}:
            print("ESC or rightmouse pressed")
            self.unregister_handlers(context)
            #print("handle_remove self_timer:",self._timer)
            return {'CANCELLED'}

        
        if event.type == 'MOUSEMOVE':
            print("mouse move active")
            
            a = mouse_location(self,context,event)
            #b = object_location(self,context,event)
            b = self.draw_3d(self,context)
            #print("mouse_location:",a)
            print("object location",b)
            print("****************************************")
            #self.offset = a
            #context.area.header_text_set("Offset %.4f %.4f %.4f" % tuple(self.offset))
            """
            #self.execute(context)
            """
        
        if event.type == 'LEFTMOUSE':
            print("left mouse pressed")
            #context.area.header_text_set(None)
            #return{'FINISHED'}
        
        if event.type in {'WHEELUPMOUSE', 'WHELLDOWNMOUSE'}:
            print("wheelmouse active")
            color = context.preferences.themes[0].view_3d.space.gradients.high_gradient
            color.s = 1.0
            color.h += 0.01

        
        if event.type == 'TIMER':
            print("timer active")
            print("event._timer:",self.draw_event)
            # mouse events
           
       
        return {'PASS_THROUGH'}
        #return {'RUNNING_MODAL'}



        
    def draw_2d(self,op, context):
        """Main function, toggled by handler"""
        contscn = context.scene
        #indices = context.scene.gl_measure_indices
        
    
        # Draw name
        if contscn.gl_display_names :
            #bpy.context.object.matrix_world.
            #draw_name(context, ob, rgb_label, fsize)
            rgb_line = (0.173, 0.545, 1.0, 1.0)
            rgb_label = (1, 0, 0, 1)
            fsize = 16
            font_id = 1
            #contscn = bpy.context.scene
            #ob = bpy.context.object
            #bpy.context.area.ui_type == 'VIEW_3D'
            
            region = context.region
            rv3d = context.space_data.region_3d
            rv3d1 = bpy.types.RegionView3D
            v = context.object.data.vertices
            verts = []
            to_select = []
            
            world = context.active_object.matrix_world
            [verts.append((world @ v.co).to_tuple()) for v in v ]
            print(verts[0])


            for i in range(0,len(v)):
                a = view3d_utils.location_3d_to_region_2d(
                region,rv3d,verts[i])
                blf.color(0,1,1,1,.7)
                blf.size( 0, 15, 72)
                blf.position(0, a[0], a[1], 0)
                blf.draw(0, str(i))
                print(a)
            
            obj_active = context.active_object
            obj_loc = context.active_object.location
            obj_loc_2d = view3d_utils.location_3d_to_region_2d(
                region,rv3d,obj_loc)
            blf.color(0,1,1,1,.7)
            blf.size( 0, 15, 72)
            blf.position(0, obj_loc_2d[0], obj_loc_2d[1], 0)
            blf.draw(0, obj_active.name)

    def draw_3d(self, context):
        """Main function, toggled by handler"""
        contscn = context.scene

        if contscn.gl_move_object:
            test = 0
            if test == 0:
                print("move object active",context.object.location)
                region = context.region
                rv3d = context.region_data
                coord =  event.mouse_region_x, event.mouse_region_y
                # get the ray from the viewport and mouse
                depthLocation = view3d_utils.region_2d_to_vector_3d(region, rv3d, coord)
                loc = view3d_utils.region_2d_to_location_3d(region, rv3d, coord, depthLocation)
                bpy.context.object.location = loc
                a = bpy.context.object.location
                return a  

        if contscn.gl_display_lines:
            
            test = 0
            if test == 1:
                Cube01 = contscn.objects['Cube'].location
                Cube02 = contscn.objects['Cube.001'].location
                Cube03 = contscn.objects['Cube.002'].location
                #coords = [(1, 1, 1), (-2, 0, 0), (-2, -1, 3), (0, 1, 1)]
                coords001 = [Cube01,Cube02,Cube03,Cube01,(1,1,1)]
                bgl.glEnable(bgl.GL_BLEND)
                bgl.glEnable(bgl.GL_LINE_SMOOTH)
                bgl.glEnable(bgl.GL_DEPTH_TEST)
                #bgl.glLineWidth(1)
                #bgl.glPointSize(3)
                #bgl.glColorMask(1,0,0,1)
                shader = gpu.shader.from_builtin('3D_UNIFORM_COLOR')
                batch = batch_for_shader(shader, 'LINES', {"pos": coords001})
                shader.bind()
                shader.uniform_float("color", (0, 1, 0, .5))
                batch.draw(shader)
                #bgl.glEnd()
                # restore opengl defaults
                bgl.glLineWidth(1)
                bgl.glDisable(bgl.GL_BLEND)
                bgl.glDisable(bgl.GL_LINE_SMOOTH)
                bgl.glEnable(bgl.GL_DEPTH_TEST)
                #bgl.glColorMask(1,0,0,1)

            if test == 2:
                objects = []
                selobj = bpy.context.selected_objects
                verts1 = []
                verts2 = []
                
                if (len(selobj)) == 2:
                    v1 = selobj[0].data.vertices
                    v2 = selobj[1].data.vertices
                    world1 = selobj[0].matrix_world
                    [verts1.append((world1 @ v1.co).to_tuple()) for v1 in v1 ]
                    world2 = selobj[1].matrix_world
                    [verts2.append((world2 @ v2.co).to_tuple()) for v2 in v2 ]
                
                    coords001 = []
                    for i in range(0,len(verts1)):
                        coords001.append(verts1[i])
                    for i in range(0,len(verts2)):
                        coords001.append(verts2[i])

                
                    shader = gpu.shader.from_builtin('3D_UNIFORM_COLOR')
                    batch = batch_for_shader(shader, 'POINTS', {"pos": coords001})
                    shader.bind()
                    shader.uniform_float("color", (1, 0, 0, .5))
                    batch.draw(shader)
                    
            if test == 3:
                
                
                # draw bmesh points on vertices of active objects
                # Get the active mesh
                me = bpy.context.object.data


                # Get a BMesh representation
                bm = bmesh.new()   # create an empty BMesh
                bm.from_mesh(me)   # fill it in from a Mesh


                # Modify the BMesh, can do anything here...
                coords001 = []
                for v in bm.verts:
                    print("*****************************************")
                    print("v.co.x:",v.co.x)
                    #v.co.x += 1.0
                    coords001.append(v.co)
                    print("v.co.x+1.0:",v.co.x)
                    print("bmesh verts:",coords001)
                    print("*****************************************")
                shader = gpu.shader.from_builtin('3D_UNIFORM_COLOR')
                batch = batch_for_shader(shader, 'POINTS', {"pos": coords001})
                shader.bind()
                shader.uniform_float("color", (1, 0, 0, .5))
                batch.draw(shader)

                # Finish up, write the bmesh back to the mesh
                bm.to_mesh(me)
                bm.free()  # free and prevent further access


   
def mouse_location(self,context,event):
            region = context.region
            rv3d = context.region_data
             #coord = Vector((event.mouse_x,event.mouse_y, 0.0))
            coord =  event.mouse_region_x, event.mouse_region_y
            # get the ray from the viewport and mouse
            depthLocation = view3d_utils.region_2d_to_vector_3d(region, rv3d, coord)
            #ray_origin = view3d_utils.region_2d_to_origin_3d(region, rv3d, coord)
            #depthLocation = region_2d_to_vector_3d(region, rv3d, coord)
            loc = view3d_utils.region_2d_to_location_3d(region, rv3d, coord, depthLocation)
            bpy.context.scene.cursor.location = loc
            a = bpy.context.scene.cursor.location

            return a  

def object_location(self,context,event):
    region = context.region
    rv3d = context.region_data
    coord =  event.mouse_region_x, event.mouse_region_y
    # get the ray from the viewport and mouse
    depthLocation = view3d_utils.region_2d_to_vector_3d(region, rv3d, coord)
    loc = view3d_utils.region_2d_to_location_3d(region, rv3d, coord, depthLocation)
    bpy.context.object.location = loc
    a = bpy.context.object.location
    return a    



