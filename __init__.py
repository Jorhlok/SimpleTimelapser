"""
Simple Timelapser
by Jorhlok
Written for 3.0.0
Partially working 2.80.0 (viewport capture not working)
https://github.com/Jorhlok/SimpleTimelapser

Renders from each (render enabled) camera at a regular interval for timelapses. 
Uses current render and output properties. Workbench renderer and jpg (or DWAA 
lossy half-float EXR) output recommended. Messing with cameras and render options 
while recording is not recommended. Unknown behavior if renders take longer than 
interval. Output for each camera saved in it\'s own subdirectory in the Output 
Properties output path. Video formats not supported.
--------
MIT License
Copyright (c) 2022 Jorhlok
Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:
The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.
THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
"""

bl_info = {
    # required
    'name': 'Simple Timelapser',
    'blender': (2, 80, 0),
    'category': 'Render',
    # optional
    'version': (1, 0, 2),
    'author': 'Jorhlok',
    'description': 'Captures window/viewport/cameras at a regular interval for timelapses.',
}

import bpy
import os
import glob
import re

strallcams = 'stlapse_all_cameras'
def get_collections_enum(self, context): #callback for dynamic camera collection dropdown menu
    output = [(strallcams,'All Cameras','Don\'t use a collection','OUTLINER_OB_CAMERA',0)]
    id = 1
    cols = bpy.data.collections
    for col in cols:
        output.append((col.name, col.name, '', 'GROUP', id))
        id += 1
    return output

#properties for N-panel menu
PROPS = [
    ('stlapse_interval', bpy.props.FloatProperty(name='Interval', default=1.0, min=0.001, options = {'HIDDEN'}, description='Time between captures in seconds (1/FPS)')),
    ('stlapse_lead_zeros', bpy.props.IntProperty(name='Leading Zeros', default=6, min=1, max=64, options = {'HIDDEN'}, description='Digits in saved sequence like viewport_000123.jpg')),
    ('stlapse_counter', bpy.props.IntProperty(name='Counter', default=1, min=0, options = {'HIDDEN'}, description='Starting counter of the sequence')),
    ('stlapse_count_auto', bpy.props.BoolProperty(name='Update Counter after Stop', default=True, options = {'HIDDEN'}, description='Save counter when you hit the stop button')),
    ('stlapse_count_from_files', bpy.props.BoolProperty(name='Update Counter from Files', default=True, options = {'HIDDEN'}, description='Disable to overwrite. Reads files in path and uses largest sequence number if larger than counter')),
    ('stlapse_window_capture', bpy.props.BoolProperty(name='Capture Window', default=True, options = {'HIDDEN'}, description='Capture screenshots of the window. Only saves as PNG')),
    ('stlapse_win_name', bpy.props.StringProperty(name='Save as', default='window', options = {'HIDDEN'}, description='Name window image sequence is saved as')),
    ('stlapse_viewport_capture', bpy.props.BoolProperty(name='Capture Viewport', default=False, options = {'HIDDEN'}, description='Render from the current 3D viewport. Doesn\'t play well with sculpt mode as of 3.0.0')),
    ('stlapse_view_name', bpy.props.StringProperty(name='Save as', default='viewport', options = {'HIDDEN'}, description='Name viewport image sequence is saved as')),
    ('stlapse_camera_capture', bpy.props.BoolProperty(name='Capture Cameras', default=False, options = {'HIDDEN'}, description='Render from selected cameras. A list of cameras that are not hidden is collected when you hit the start button. You\'re meant to stop recording to change cameras. Keep in mind cameras only see render enabled objects')),
    ('stlapse_cam_menu', bpy.props.EnumProperty(items=get_collections_enum,name='', options = {'HIDDEN'}, description='')),
    ('stlapse_animate', bpy.props.BoolProperty(name='Animate', default=False, options = {'HIDDEN'}, description='Sets frame to Counter + Offset before each render to use animated cameras or objects. Animation will be controlled by timelapse')),
    ('stlapse_anim_offset', bpy.props.IntProperty(name='Frame Offset', default=0, options = {'HIDDEN'}, description='Difference from counter animation frame should be')),
    ('stlapse_anim_loop', bpy.props.BoolProperty(name='Loop', default=True, options = {'HIDDEN'}, description='Loop between start and end frame')),
]

# == UTILS
isrecording = False
interval = 1.0
counter = 1
leadzero = 8
camlist = []

def get_isrecording():
    global isrecording
    return isrecording

def check_hidden(obj, cols): #recursivley check collections to see if obj is hidden
    for col in cols:
        incol = False
        for o in col.all_objects:
            if o is obj:
                incol = True
                break
        if incol:
            if col.hide_render:
                return True
            else:
                return check_hidden(obj, col.children)
    return False

def get_cameras(objs, scn): #get a list of names of valid cameras
    output = []
    obj=[ob for ob in objs if ob.type == 'CAMERA' and not ob.hide_render]
    for cam in obj:
        if not check_hidden(cam, scn.collection.children):
            output.append(cam.name)
    return output

def make_captures(num,zeros): #render and save a frame
    global camlist
    scn = bpy.context.scene
    path_dir = scn.render.filepath
    if scn.stlapse_window_capture:
        wintxt = scn.stlapse_win_name
        bpy.ops.screen.screenshot(filepath=os.path.join(path_dir, wintxt, wintxt + '_' + str(num).zfill(zeros) + '.png'))
    if scn.stlapse_viewport_capture:
        viewtxt = scn.stlapse_view_name
        if viewtxt != '':
            scn.render.filepath = os.path.join(path_dir, viewtxt, viewtxt + '_' + str(num).zfill(zeros))
            bpy.ops.render.opengl(write_still=True)
    if scn.stlapse_camera_capture:
        oldcam = scn.camera
        obj=[ob for ob in scn.objects if ob.type == 'CAMERA']
        for cam in obj:
            if cam.name in camlist:
                scn.camera = cam
                scn.render.filepath = os.path.join(path_dir, cam.name, cam.name + '_' + str(num).zfill(zeros))
                bpy.ops.render.render(write_still=True)
        scn.camera = oldcam
    scn.render.filepath = path_dir

def counter_from_files(): #read potential sequence files for largest sequence number
    global counter
    path_dir = bpy.context.scene.render.filepath
    filenames = glob.glob(path_dir + "/*/*") #searches all files one subdir deep (intended use case is timelapses in own folder)
    newcounter = -1
    if len(filenames) > 0:
        for file in filenames:
            s = re.findall("_\d+",file) #searches for '_000123' suffix added in make_captures
            if len(s) > 0:
                newcounter = max(newcounter, int(s[-1][1:])) #takes the last instance so naming your camera 'front_001' shouldn't confuse it
    if newcounter >= counter:
        counter = newcounter + 1

def interval_handler(): #called once an interval
    global counter
    global interval
    global leadzero
    
    if isrecording:
        scn = bpy.context.scene
        if scn.stlapse_animate:
            bpy.ops.screen.animation_cancel(restore_frame=False)
            frame = counter + scn.stlapse_anim_offset
            if scn.stlapse_anim_loop:
                begin = scn.frame_start
                end = scn.frame_end
                len = end-begin+1
                if len > 0:
                    tmpframe = frame - begin
                    frame = begin + tmpframe % len
                else:
                    frame = begin
            scn.frame_set(frame)
        make_captures(counter,leadzero)
        counter += 1
        return interval
    return None

def load_file_handler(): #probably a bad idea to keep going at this point
    stop()

def start():
    global isrecording
    global interval
    global counter
    global leadzero
    global camlist
    if not isrecording:
        scn = bpy.context.scene
        interval = scn.stlapse_interval
        leadzero = scn.stlapse_lead_zeros
        counter = scn.stlapse_counter
        if scn.stlapse_count_from_files:
            counter_from_files()
            scn.stlapse_counter = counter
        if scn.stlapse_camera_capture:
            if scn.stlapse_cam_menu == strallcams:
                camlist = get_cameras(scn.objects,scn)
            else:
                col = bpy.data.collections[scn.stlapse_cam_menu]
                camlist = get_cameras(col.all_objects,scn)
        bpy.app.timers.register(interval_handler)
        isrecording = True

def stop():
    global isrecording
    global counter
    if isrecording:
        isrecording = False
        if bpy.app.timers.is_registered(interval_handler):
            bpy.app.timers.unregister(interval_handler)
        scn = bpy.context.scene
        if scn.stlapse_count_auto:
            scn.stlapse_counter = counter

# == OPERATORS

class StartOperator(bpy.types.Operator):
    """Start recording timeslapse. This is like hitting the render button for the enabled viewport and cameras every Interval seconds. It uses the current render and output settings. Minor hitches while recording are normal"""
    bl_idname = 'opr.stlapse_start_operator'
    bl_label = 'Start Simple Timelapser'
    
    def execute(self, context):
        start()
            
        return {'FINISHED'}
    
class StopOperator(bpy.types.Operator):
    """Stop recording timelapse"""
    bl_idname = 'opr.stlapse_stop_operator'
    bl_label = 'Stop Simple Timelapser'
    
    def execute(self, context):
        stop()
            
        return {'FINISHED'}

# == PANELS
class SimpleTimelapserPanel(bpy.types.Panel):
    
    bl_idname = 'VIEW3D_PT_simple_timelapser'
    bl_label = 'Simple Timelapser'
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = 'Timelapse'
    
    def draw(self, context):
        col = self.layout.column()
        isrec = get_isrecording()
        txt = 'Stopped'
        if isrec:
            txt = 'Recording'
        self.layout.label(text=txt)
        col = self.layout.column()
        col.operator('opr.stlapse_start_operator', text='Start')
        col.operator('opr.stlapse_stop_operator', text='Stop')
        for (prop_name, _) in PROPS:
            row = col.row()
            row.prop(context.scene, prop_name)
            if prop_name[0:13] == 'stlapse_view_':
                row.enabled = bpy.context.scene.stlapse_viewport_capture and not isrec
            elif prop_name[0:12] == 'stlapse_win_':
                row.enabled = bpy.context.scene.stlapse_window_capture and not isrec
            elif prop_name[0:12] == 'stlapse_cam_':
                row.enabled = bpy.context.scene.stlapse_camera_capture and not isrec
            elif prop_name[0:13] == 'stlapse_anim_': 
                row.enabled = bpy.context.scene.stlapse_animate and not isrec
            else:
                row.enabled = not isrec

# == MAIN ROUTINE
CLASSES = [
    StartOperator,
    StopOperator,
    SimpleTimelapserPanel,
]

def register():
    for (prop_name, prop_value) in PROPS:
        setattr(bpy.types.Scene, prop_name, prop_value)
    
    for klass in CLASSES:
        bpy.utils.register_class(klass)
        
    bpy.app.handlers.load_pre.append(load_file_handler)

def unregister():
    stop()
    bpy.app.handlers.load_pre.remove(load_file_handler)
    
    for (prop_name, _) in PROPS:
        delattr(bpy.types.Scene, prop_name)

    for klass in CLASSES:
        bpy.utils.unregister_class(klass)

if __name__ == '__main__':
    register()
