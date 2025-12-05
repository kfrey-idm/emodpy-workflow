# Projects

emodpy-workflow is organized around "projects". A "project" is a structured directory
containing information related to model definition, inputs building, observational
data, and scientific scenarios. In other words, it contains all data 
for a related set of model configurations and any output obtained for analysis.

!!! Warning
    All commands must be run with a project directory as the current directory.

The minimum required components of a project are detailed below.

## manifest.py

**&lt;project_dir&gt;/manifest.py** : This file specifies the pathing needed for the
model executable to be run by the built-in commands as well as ingest form location
for calibration. For EMOD-HIV, the required attributes (paths) that must be set are:

- **ingest_filename** : Path to a default ingest form to use for calibration
of any frame in the project.
- **executable_path** : Path to the EMOD-HIV binary to use for all frames
in the project.
- **schema_path** : Path to the schema.json file compatible with the specified
EMOD-HIV binary.
- **asset_collection_of_container** : If the platform you intend to run simulations
on requires the specification and use of a .sif file (for Singularity) then specify
the path to an appropriate .sif file here. Otherwise, specify `None`.
- **post_processing_path** : The path of a dtk_post_process.py file to use with
EMOD-HIV. `standard` means to use a built-in post-processing script and `None`
means to skip post-processing. Post-processing is only required for 
calibration of EMOD-HIV.
- **pre_processing_path** : The path of a dtk_pre_process.py file to use with
EMOD-HIV. `standard` means to use a built-in pre-processing script and `None`
means to skip pre-processing. There is no current `standard` pre-processor 
for EMOD-HIV.
- **in_processing_path** : The path of a dtk_in_process.py file to use with
EMOD-HIV. `standard` means to use a built-in in-processing script and `None`
means to skip in-processing. There is no current `standard` in-processor for 
EMOD-HIV.

## bin directory

**&lt;project_dir&gt;/bin** : This is a directory intended to contain model
executables and any required files related to their basic execution. When running
EMOD-HIV, it is automatically created upon simulation creation (as needed) and is the 
directory that your Eradication binary and schema will be automatically
copied/installed into. It is also typically the  directory for a user to put any
needed container (.sif) files for execution.

## frames directory

**&lt;project_dir&gt;/frames** : This is a directory that contains the frames in a
project, where each frame is a subdirectory.  The frames directory will be created
automatically as needed by the command new_frame.

## idmtools.ini

**&lt;project_dir&gt;/idmtools.ini** : This file configures the idmtools Platform
object that manages the creation and running of simulations on compute resources.
All commands that need to communicate with a compute resource (for execution,
obtaining files, etc) accepts an idmtools.ini platform block name (like
ContainerPlatform) via argument to identify which resource to utilize.

The new_project command will automatically create one that can then be modified.
Details of the file format can be found [here][idmtools_config].
