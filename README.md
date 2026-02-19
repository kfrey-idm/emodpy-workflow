# emodpy-workflow
<p>
emodpy-workflow is a collection of commands and interfaces intended to support data-driven scientific computing 
workflows. In particular, its core currently standardizes the system of creating, calibrating, running, and obtaining 
output from EMOD-HIV model scenarios. Teams of users can more easily work with each other's projects using 
emodpy-workflow as it provides standard way of using EMOD-HIV.
</p>

---
## Table of Contents
- [Installation](#installation)
    - [Software Prerequisites](#software-prerequisites)
    - [1. Create and activate a clean virtual environment](#create-and-activate-virtual-environment)
    - [2. Obtain and install emodpy-workflow](#obtain-and-install-emodpy-workflow)
- [Getting Started](#getting-started)
  - [Commands](#commands)
  - [Projects](#projects)
  - [Frames](#frames)
  - [Sweep Files](#sweep-files)
- [Community](#community)
- [Support and Contributions](#support)
- [Disclaimer](#disclaimer)

---

<a id="installation"></a>
# Installation

<a id="software-prerequisites"></a>
## Software Prerequisites

- This guide assumes Python 3.9.X (3.9.13 or higher) (64-bit) is installed 
(https://www.python.org/downloads/release/python-3913/) in Windows or Linux and assumes it is custom-installed into 
C:\Python39 in Windows or /c/Python39 in Linux.  (Downloads:  <a href="https://www.python.org/ftp/python/3.9.13/python-3.9.13-amd64.exe">exe</a>,  <a href="https://www.python.org/ftp/python/3.9.13/Python-3.9.13.tgz">tgz</a>)

- This guide further assumes a Linux-like command terminal is being used for Windows (for example, git bash in Windows), not the
built-in Windows cmd.

---

<a id="create-and-activate-virtual-environment"></a>
## 1. Create and activate a clean virtual environment

If you have Python installed to a different directory, please update the Python interpreter path below to match your 
installation of Python.

### > Create the virtual environment
```
/c/Python39/python -m venv ~/environments/emodpy-workflow
```

### > Activate the virtual environment:


#### _Bash in Windows:_
```
source ~/environments/emodpy-workflow/Scripts/activate
```


#### _In Linux:_
```
source ~/environments/emodpy-workflow/bin/activate
```

### > Ensure pip is up-to-date:
```
python -m pip install pip --upgrade
```

<a id="obtain-and-install-emodpy-workflow"></a>
## 2. Obtain and install emodpy-workflow:
```
python -m pip install emodpy-workflow --extra-index-url=https://packages.idmod.org/api/pypi/pypi-production/simple
```

---

<a id="getting-started"></a>
# Getting Started

<p>
For people who have been using EMOD-HIV with Dtk-Tools, emodpy-workflow will have a familiar feel as it replicates the 
Dtk-Tools workflow but with standardized commands in the package (not a project). Ingest forms of near-identical format 
are still used for reference data specification, calibration parameter specification, and calibration analyzer weights.
The primary change is that direct editing of JSON inputs (including the JSON KP-tagging system for parameters) 
has been completely replaced with Python editing, enhancing readability, usability, and testability, and shareability 
of projects.
</p>

<p>
The most basic core workflow supported follows the steps below:
</p>

1. define a model setup
2. calibrate the model setup to observations
3. define scientific model scenarios 
4. run scenarios 
5. obtain scenario results

---

<a id="commands"></a>
## Commands

**All commands are intended to be run in a project directory. This is the directory that directly contains your 
frames directory, manifest.py, and idmtools.ini file.**

<p>
All commands can be run via:
</p>

```
python -m emodpy_workflow.scripts.COMMAND_NAME_HERE < ARGUMENTS HERE >
```

<p>
Information on command arguments and their usage is available via:
</p>

```
python -m emodpy_workflow.scripts.COMMAND_NAME_HERE --help
```

- new_project
  - Creates a basic project directory with default files and settings. Platform-specific settings/files may still need 
  to be set/obtained. 
- new_frame
  - Creates a new frame that imports and uses a defined emodpy-hiv country model, which can then be altered or extended.
- extend_frame
  - Imports the input builders of an existing frame, which can then be altered or extended (without modifying the 
  source frame).
- available_parameters
  - Lists all currently defined and available hyperparameters of a specified frame. These are 
available for alteration by a user during calibration and scenarios if they so choose.
- calibrate
  - Calibrates a model specified in a frame to its reference data specified in a "calibration ingest form".
- resample
  - Selects one or more parameter sets (samples) from a calibration process. These parameter sets are the model 
  calibration. They can be used later on in scenarios when using the "run" command.
- run
  - Runs model simulations. Calibration samples and/or sweeps files can be provided as input as appropriate.
- download
  - Obtains specified output file(s) from previously run simulations and puts them into a structured local directory.
- plot_sims_with_reference
  - Plots model output against reference data to aid in calibration.

---

<a id="projects"></a>
## Projects

<p>
emodpy-workflow is organized around "projects". A "project" is a structured directory containing information related to 
model definition, inputs building, observational data, and scientific scenarios.

**All commands must be run with a project directory as the current directory.**

</p>

<p>
The most important structures in a "project" are "frames" and "sweep files". They also contain a manifest.py file (for 
specifying core file pathing) and an idmtools.ini file (for specifying how to utilize computing environments).
</p>

Minimum initial required files and directories:
- manifest.py
- idmtools.ini
- bin/ (empty)


---

<a id="frames"></a>
## Frames

<p>
A frame is a standard input to emodpy-workflow commands that functions as an interface to model input definition, 
discovery, and execution.
</p>

In particular, a frame defines:
- The model to be used (EMOD-HIV)
- Functions that initialize the model inputs
- Functions that define how to build inputs after initialization
- Available hyperparameters and how they modify model input building
- Reference observational data (for calibration)

<p>
Frames are designed to make it simple to extend them via code reuse similar to class inheritance in object oriented 
design. This enables a project to contain a "family tree" of frames, automatically propagating updates from "parent" 
frames to their descendants for frame and scenario consistency.
</p>

<p>
The built-in commands "new_frame" and "extend_frame" are convenience methods for generating new frames for use. They are
not strictly necessary to create a frame (they can be "handmade"). A frame simply needs to have one attribute, 
**model**, in its __init__.py file, where the value of **model** is an object of a descendent class of IModel.
</p>

<p>
A sample EMOD HIV frame __init__.py generated by the "new_frame" command:
</p>

```
# This frame built via command:
# python -m emodpy_workflow.scripts.new_frame

from emodpy_workflow.lib.models.emod_hiv import EMOD_HIV
from emodpy_workflow.lib.utils.runtime import load_manifest

# The manifest contains input file pathing information for the project
manifest = load_manifest()

# EMOD contains three main configuration objects: config, demographics, and campaign. The related information
# for generating these input objects is placed into concern-specific files in this directory.
from . import config
from . import demographics
from . import campaign

# 'model' is a required attribute of this file. All commands access frames by loading the 'model' attribute.
# The model attribute is assigned a model- and disease-specific object that contains all information regarding
# how to build the inputs for the model and generating its command line for execution.
model = EMOD_HIV(
    manifest=manifest,
    config_initializer=config.initialize_config,
    config_parameterizer=config.get_config_parameterized_calls,
    demographics_initializer=demographics.initialize_demographics,
    demographics_parameterizer=demographics.get_demographics_parameterized_calls,
    campaign_initializer=campaign.initialize_campaign,
    campaign_parameterizer=campaign.get_campaign_parameterized_calls,
    ingest_form_path=manifest.ingest_filename,
    build_reports=config.build_reports
)
```

---

<a id="sweep-files"></a>
## Sweep Files

A sweep file is a Python file that specifies sets of hyperparameter overrides, often referred to as "scenarios". 
Scenarios address specific scientific questions, typically (but not exclusively) related to predicting the outcome
of potential interventions and events.

These overrides are applied to simulation inputs building of specific frame(s) after any other parameter overrides 
(they have the highest precedence).

Sweep file format by example:

```
# A sweep Python file must contain a 'parameter_sets' attribute, which is a dict with keys being names of
# frames and values being dicts of param_name:value entries OR a generator of such dicts
parameter_sets = {
    # This key indicates the contained information is for building off the 'baseline' frame
    'baseline': {
        # Each dict in 'sweeps' list is a set of param: value overrides to be applied. A scenario.
        # Note that the parameter lists are arbitrary. Each scenario can include as many or few parameters
        # as you want.
        # One experiment will be created per entry in 'sweeps'
        'sweeps': [
            # Optional: A provided 'experiment_name' in a sweep entry will name the corresponding experiment. Default
            #  experiment name is the name of the frame.
            {'experiment_name': 'condom_maternal_higher', 'Condom_Transmission_Blocking_Probability': 0.9, 'Maternal_Infection_Transmission_Probability': 0.4},
            {'experiment_name': 'condom_maternal_lower', 'Condom_Transmission_Blocking_Probability': 0.7, 'Maternal_Infection_Transmission_Probability': 0.2},
            {'experiment_name': 'condom_higher', 'Condom_Transmission_Blocking_Probability': 0.9},
            {}  # This is a do nothing different, baseline scenario
        ]
    }
}
```

<a id="community"></a>
# Community

Please join us in [Discussions](https://github.com/orgs/EMOD-Hub/discussions)

<a id="support"></a>
# Support and Contributions

The code in this repository was developed by IDM to support our research in disease
transmission and managing epidemics. We’ve made it publicly available under the MIT
License to provide others with a better understanding of our research and an opportunity
to build upon it for their own work. We make no representations that the code works as
intended or that we will provide support, address issues that are found, or accept pull
requests. You are welcome to create your own fork and modify the code to suit your own
modeling needs as contemplated under the MIT License.

If you have feature requests, issues, or new code, please see our
'CONTRIBUTING <https://github.com/EMOD-Hub/emodpy-workflow/blob/main/CONTRIBUTING.rst>' page
for how to provide your feedback.

Questions or comments can be directed to [idmsupport@gatesfoundation.org](<mailto:idmsupport@gatesfoundation.org>).

<a id="disclaimer"></a>
# Disclaimer

The code in this repository was developed by IDM and other collaborators to support our joint research on flexible agent-based modeling.
 We've made it publicly available under the MIT License to provide others with a better understanding of our research and an opportunity to build upon it for 
 their own work. We make no representations that the code works as intended or that we will provide support, address issues that are found, or accept pull requests.
 You are welcome to create your own fork and modify the code to suit your own modeling needs as permitted under the MIT License.

