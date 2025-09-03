# Calibrate a frame

The basic command to calibrate a frame to reference data in an ingest form using the optim_tool algorithm is:

```bash
python -m emodpy_workflow.scripts.calibrate -F FRAME -p PLATFORM optim_tool
```

... where FRAME is the name of the frame to calibrate and PLATFORM is the idmtools.ini platform name to run on.

There are numerous additional parameters that can be set to control the behavior of the process. They are specified
**before** the algorithm name (like optim_tool) on the command line. 

To see parameters for controlling the calibration process, run:

```bash
python -m emodpy_workflow.scripts.calibrate -h
```

Each optimization algorithm (like optim_tool) has its own parameters that are specified **after** the algorithm name. To 
see parameters for controlling the details of the chosen optimization algorithm, run:

```bash
python -m emodpy_workflow.scripts.calibrate optim_tool -h
```

---

## Resample a calibration

Resampling a calibration is the process of selecting one or more sets of parameters from a calibration. 
These parameter sets are effectively "a model calibration", the end result of a calibration process. They also contain
the random seed (Run_Number) to allow exact recreation of a simulation.

To resample a calibration, run the following:

```bash
python -m emodpy_workflow.scripts.resample -d CALIBRATION_DIR -m METHOD -n NUMBER -o FILE
```

... where CALIBRATION_DIR is the directory path of a calibration process that has been performed, METHOD is the
sampling algorithm, NUMBER is the count of parameter sets to select, and FILE is the file path to write CSV results to.

