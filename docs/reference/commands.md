# Commands

!!! Warning
    All commands are intended to be run in a project directory. This is the 
    directory that directly contains your frames directory, manifest.py, and
    idmtools.ini file.

All commands can be run via:

```bash
python -m emod_workflow.scripts.COMMAND_NAME_HERE <ARGUMENTS_HERE>
```

Information on command arguments and their usage is available via:

```bash
python -m emod_workflow.scripts.COMMAND_NAME_HERE --help
```

## `new_project`

Creates a basic project directory with default files and settings.
Platform-specific settings/files may still need to be set/obtained. 

## `new_frame`

Creates a new frame that imports and uses a defined emodpy-hiv country model
which can then be altered or extended.

## `extend_frame`

Imports the input builders of an existing frame, which can then be altered or
extended (without modifying the source frame).

## `available_parameters`

Lists all currently defined and available hyperparameters of a specified frame.
These are available for alteration by a user during calibration and scenarios
if they so choose.

## `calibrate`

Calibrates a model specified in a frame to its reference data specified in
a "calibration ingest form".

## `resample`

Selects one or more parameter sets (samples) from a calibration process.
These parameter sets are the model calibration.  They can be used later on
in scenarios when using the `run` command.

## `run`

Runs model simulations. Calibration samples and/or sweeps files can be provided
as input as appropriate. 

## `download`

Obtains specified output file(s) from previously run simulations and puts them
into a structured local directory.

## `plot_sims_with_reference`

Plots model output against reference data to aid in calibration.
