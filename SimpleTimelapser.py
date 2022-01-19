"""
Simple Timelapser
by Jorhlok
Confirmed working in 2.80.0 thru 3.0.0
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
    'version': (1, 0, 0),
    'author': 'Jorhlok',
    'description': 'Renders from each camera at a regular interval for timelapses.',
}

import bpy
from bpy.app.handlers import persistent
import os
import glob
import re

# == GLOBAL VARIABLES
PROPS = [
    ('stlapse_interval', bpy.props.FloatProperty(name='Interval (secs)', default=1.0)),
    ('stlapse_lead_zeros', bpy.props.IntProperty(name='Leading Zeros', default=8)),
    ('stlapse_counter', bpy.props.IntProperty(name='Counter', default=1)),
    ('stlapse_count_auto', bpy.props.BoolProperty(name='Update Counter after Stop', default=True)),
    ('stlapse_count_from_files', bpy.props.BoolProperty(name='Update Counter from Files', default=True)),
]

# == UTILS
isrecording = False
interval = 1.0
counter = 1
leadzero = 8

def get_isrecording():
    global isrecording
    return isrecording

def make_captures(num,zeros):
    path_dir = bpy.context.scene.render.filepath
    for cam in [obj for obj in bpy.data.objects if obj.type == 'CAMERA']:
        if not cam.hide_render:
            bpy.context.scene.camera = cam
            bpy.context.scene.render.filepath = os.path.join(path_dir, cam.name, cam.name + '_' + str(num).zfill(zeros))
            bpy.ops.render.render(write_still=True)
    bpy.context.scene.render.filepath = path_dir

def counter_from_files():
    global counter
    path_dir = bpy.context.scene.render.filepath
    filenames = glob.glob(path_dir + "/*/*") #searches all files one subdir deep (intended use case is timelapses in own folder)
    newcounter = -1
    if len(filenames) > 0:
        for file in filenames:
            s = re.findall("_\d+",file) #searches for '_00000123' suffix added in make_captures
            if len(s) > 0:
                newcounter = max(newcounter, int(s[-1][1:])) #takes the last instance so naming your camera 'front_001' shouldn't confuse it
    if newcounter >= counter:
        counter = newcounter + 1

@persistent
def interval_handler():
    global counter
    global interval
    global leadzero
    
    if isrecording:
        make_captures(counter,leadzero)
        counter += 1
        return interval
    return None

@persistent
def load_file_handler():
    stop()

bpy.app.handlers.load_pre.append(load_file_handler)

def start():
    global isrecording
    global interval
    global counter
    global leadzero
    if not isrecording:
        interval = bpy.context.scene.stlapse_interval
        leadzero = bpy.context.scene.stlapse_lead_zeros
        counter = bpy.context.scene.stlapse_counter
        if bpy.context.scene.stlapse_count_from_files:
            counter_from_files()
            bpy.context.scene.stlapse_counter = counter
        bpy.app.timers.register(interval_handler)
        isrecording = True

def stop():
    global isrecording
    global counter
    if isrecording:
        isrecording = False
        if bpy.context.scene.stlapse_count_auto:
            bpy.context.scene.stlapse_counter = counter

# == OPERATORS

class StartOperator(bpy.types.Operator):
    """Start recording timeslapse"""
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

def unregister():
    for (prop_name, _) in PROPS:
        delattr(bpy.types.Scene, prop_name)

    for klass in CLASSES:
        bpy.utils.unregister_class(klass)
        

if __name__ == '__main__':
    register()