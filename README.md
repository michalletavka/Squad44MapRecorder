# Squad44MapRecorder
Unreal Engine 4 blueprint for recording orthomaps

# Taking screenshots
1. Prepare BP_MapRecorder
    1. Drag and drop the blueprint on a map
    2. Place it in the north-west corner of the map
    3. Select the actor and rotate it, so that the camera points directly under and the top edge of the camera points to north
2. In the World Outliner
    1. Delete BP_SQUAD_Sky
    2. Delete BP_WeatherSystem
    3. Delete ExponentialHeightFog
    4. In DirectionalLight, increase `Intensity` to `5,0 lux` (or to your liking)
    5. In DirectionalLight, adjust `Light Color` to `FFFFFF`
    6. In DirectionalLight, reset `Light Function Material` to `None`
3. Look around in Viewport and delete other stuff around landscape, mountains, background, ...
4. Calibrate BP_MapRecorder
    1. Place the BP_MapRecorder into top-left corner of the map, so that the blueprint's camera is looking at the map from sky (closer = more detailed map result, but also longer map capture and bigger map image file)
    2. Check the `Measuring` attribute
    3. Set `Time Between Steps` to `0.1`
    4. Measure the map size in steps
    5. Put the map size in steps into `Size X` and `Size Y` attributes of the BP_MapRecorder
5. Capture the map
    1. Sometimes the SDK screenshots the editor camera instead of the BP_MapRecorder blueprint camera, so place the editor camera so that it's facing a bright color, so it is later easier to detect the faulty screenshots.
    2. Uncheck the `Measuring` attribute
    3. Set `Time Between Steps` to `0.5`
    4. Play in Selected Viewport and go fullscreen (F11)
    5. Blueprint should take over the camera, cycle around the map and capture screenshots into *C:\Program Files\Epic Games\PostScriptumSDK\PostScriptum\Saved\Screenshots\Windows* This step may take hours.

# Stitching

## Prerequisites
- Tested with Python 3.12.0
- `pip install futures pillow`

## Stitching
Use the *process_screenshots_parallel.py* to process the individual screenshots into an image of the map.

`process_screenshots_parallel.py <input_folder> <output_folder> <images_per_row> <image_overlap>`

`<images_per_row>` is how many images were captured in one row, typically this equals the `Size X` attribute of the BP_MapRecorder
`<image_overlap` is how much percent should the cropped images overlap, adjust this if you see doubled objects on the map

example: `python .\process_screenshots_parallel.py .\_raw\ .\ 82 10`
