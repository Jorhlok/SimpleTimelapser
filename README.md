# SimpleTimelapser
Blender 2.80+ Timelapse Capture Tool Addon
Developed for Blender 3.0.0, tested working on 2.80.0

It's no ZBrush undo history but it's pretty good.
If this causes too much performance trouble, consider recording a second window with OBS or something.

Renders from each (render enabled) camera at a regular interval for timelapses. Uses current render and output properties. Workbench renderer and jpg (or DWAA lossy half-float EXR) output recommended. Messing with cameras and render options while recording is not recommended. Unknown behavior if renders take longer than interval. Output for each camera saved in it's own subdirectory in the Output Properties output path. Video formats not supported.

The interface is in the N-panel in the 3D Viewport.
You can technically use animated cameras if you set the framerate to the interval time and remember to start and stop animating at the same time as recording.

Procedure to use:
- Download zip from github
- Install addon in Blender Preferences > Addons > Install > choose zip
- Set up cameras for timelapse capture
- Disable other cameras and unwanted objects for rendering in the Scene Collection tab
- Set up renderer options (workbench strongly recommended), color management, and resolution
- Set up export options like path (just choose a folder, not a file name) and format (jpeg recommended)
- Go to a 3D Viewport and in the right toolbar (default key is 'N') open the Timelapse tab
- Change options if needed
  - Interval (secs) - How long between frames.
  - Leading Zeros - How many digits in the image sequence files like cam1_00000001.jpg
  - Counter - What number to start the sequence at.
  - Update Counter After Stop - Sets the counter to 1 after the last image when you hit the stop button.
  - Update Counter From File - Tries to read what the counter should be from all files one subdir deep in '*_xyz*' format. Disable if overwriting desired.
- Press the start button to start recording. This is like hitting the render button every Interval second(s) for each enabled camera so might cause minor (or major) hitches.
- Do some stuff to be captured in the timelapse. Try to keep in frame and remember the timelapse only sees objects enabled for rendering.
- Press the stop button.
- Edit your dope timelapse or whatever!
