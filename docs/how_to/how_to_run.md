# Make a single run

A single simulation of a default county model configuration can be run as follows:

```bash
python -m emodpy_workflow.scripts.run -F FRAME -p PLATFORM -o OUTPUT -N SUITE_NAME
```

where

- FRAME is the name of a frame **created with the "new_frame" command and has not been further modified**
- PLATFORM is the idmtools.ini platform name to run on
- OUTPUT is the directory for storing the run receipt file
- SUITE_NAME is a meaningful name/description of suite (of one experiment, of one simulation) for identification.

