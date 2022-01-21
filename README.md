# SimpleTimelapser
Blender 2.80+ Timelapse Capture Tool Addon
Developed for Blender 3.0.0, partly working on 2.80.0

It's no ZBrush undo history but it's pretty good.
If this causes too much performance trouble, consider recording a second window with OBS or something.

Renders from each (render enabled) camera at a regular interval for timelapses. Uses current render and output properties. Workbench renderer and jpg (or DWAA lossy EXR) output recommended. Messing with cameras and render options while recording is not recommended. Unknown behavior if renders take longer than interval. Output for each camera saved in it's own subdirectory in the Output Properties output path. Video formats not supported.

The interface is in the N-panel in the 3D Viewport.

Procedure to use:
- Download zip from github
- Install addon in Blender Preferences > Addons > Install > choose zip
- Set up cameras/animations for timelapse capture if desired
- Disable ounwanted objects for rendering in the Scene Collection tab
- Set up renderer options (workbench strongly recommended), color management, and resolution
- Set up export options like path (just choose a folder, not a file name) and format (jpeg recommended)
- Go to a 3D Viewport and in the right toolbar (default key is 'N') open the Timelapse tab
- Press the start button to start recording. This is like hitting the render button every Interval second(s) for each enabled camera so might cause minor (or major) hitches.
- Do some stuff to be captured in the timelapse. Try to keep in frame and remember the cameras only see objects enabled for rendering.
- Press the stop button.
- Edit your dope timelapse or whatever!
