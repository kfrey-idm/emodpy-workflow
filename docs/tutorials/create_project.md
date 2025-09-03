# Create Project

- a.Explain to the user that they always need to be working within the top level of a project
- b.Have them create a project and view what is included in a base project
- c.Point to reference data on projects
- d.Explain that they need a frame in order to run anything because that is where the simulation is defined
- e.Explain that they also need a default country model and point to the reference
- f.Have them create a frame and inspect the files that have been created.
- g.Explain that the frame is one of the places they can make changes to the simulations configuration.
- h.Point to reference data on frames


## Objective

The goal of this tutorial is to learn about "projects" and "frames".  All the commands
of emodpy-workflow must be used within a "project".  You will learn how to create a
new project and the files that exist in a project.  Most of the other commands require
a "frame".  A frame is an idea/scenario that involves changing parameters and/or code.
You will learn how to create a frame in this tutorial.

## Prerequisites


python 3.9


## Setup and Installation

1. Create directory for your training

```
mkdir my_training
cd my_training
```

2. Follow the installation instructions if not using Codespaces

Use the [installation](../installation.md) instructions to setup your virtual
environment and install emodpy-workflow.

If you are using Codespaces with the emodpy-workflow repository, you do not
need to create a virtual environment or install emodpy-workflow.

## General command format

emodpy-workflow provides you with a collection of [commands](../reference/reference_overview.md#commands)
that allow you to perform the tasks of creating projects, running EMOD, calibrating,
downloading data, and so on.  To use a command, you must be in the top-level
directory of your project and type the command similarly to the following:

```
python -m emodpy_workflow.scripts.XXX <arguments>
```

1. Test that you can execute a command

```
python -m emodpy_workflow.scripts.new_project -h
```

You should see output similar to the following:

```
usage: new_project.py [-h] -d DEST_DIR

optional arguments:
  -h, --help            show this help message and exit
  -d DEST_DIR, --directory DEST_DIR
                        Path of new project directory to create and populate with initial files and subdirectories. Required.
```

If you see this, you are ready!!

## Create your project

The 'new_project' command is use to create a
[new project directory](../reference/reference_overview.md#Projects).  It is assumed that all
of the other commands will be executed in this project directory.

1. Execute new_project command

```
python -m emodpy_workflow.scripts.new_project -d my_project
```

When the command is finished, you should something similar to the following:

```
Created new project directory: my_project
```

## Explore what is in the project

Let's look into the directory that was just created and learn about what is in it and why.

1. Look at what is in our training directory by executing the following command:

```
dir
```

You should see something similar to the following:

```

Directory of C:\work\my_training

08/12/2025  09:28 AM    <DIR>          .
08/12/2025  09:28 AM    <DIR>          ..
08/11/2025  09:49 AM    <DIR>          env
08/11/2025  09:54 AM    <DIR>          my_project
```

- env - This folder is the one that contains our python virtual environment.
It contains all of the python tools we need for running EMOD, plotting data, etc.
- my_project - This is the folder we just created with the **new_project**
command.  All future emodpy-workflow commands must be executed inside the
"my_project" folder.

2. Look at what is in the project directory by executing the following commands:

```
cd my_project
dir
```

You should see something similar to the following:

```
Directory of C:\work\my_training\my_project

08/12/2025  10:37 AM    <DIR>          .
08/12/2025  10:37 AM    <DIR>          ..
08/08/2025  02:41 PM             1,267 idmtools.ini
08/11/2025  09:54 AM             3,542 manifest.py
08/11/2025  09:54 AM               355 __init__.py
08/11/2025  09:54 AM    <DIR>          __pycache__
```

- idmtools.ini - This file contains information about the computing platforms
where you are running EMOD like where you want the simulation files to be created.
The [reference](../reference/reference_overview.md#idmtoolsini) contains the
details about this file.
- manifest.py - This file contains information about how you are running EMOD,
like where the EMOD binary is stored and if you are using simulation post processing.
The [reference](../reference/reference_overview.md#manifestpy) contains the
details about this file.
- __init__.py - ???
- __pycache__ - This folder is created by Python to store compiled bytecode files for
Python modules. 

## Create a baseline "frame"

In emodpy-workflow, a "frame" is used to define a collection of parameters and code.
This collection could be your definition of a scenario, like vaccinating people for
HIV on their 15th birthday.  See the [reference](../reference/reference_overview.md#frames)
for more information.

1. See the o

```



