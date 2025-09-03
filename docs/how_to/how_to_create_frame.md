# Create a frame

To make a new frame of an existing emodpy-hiv country model, execute the following:

```bash
python -m emodpy_workflow.scripts.new_frame --country COUNTRY --dest FRAME
```

... where COUNTRY is the country model class name and FRAME is the desired name of the frame to create. The created
frame will be in the &lt;project_directory&gt;/frames/FRAME directory.

---

## Extend an existing frame

To extend an existing frame, which imports an existing frame as the starting point of a new frame, execute the 
following:

```bash
python -m emodpy_workflow.scripts.extend_frame --source SOURCE --dest FRAME
```

... where SOURCE is the name of the frame to be extended and FRAME is the name of the frame to create.
