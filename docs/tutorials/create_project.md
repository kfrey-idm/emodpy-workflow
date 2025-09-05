# Create Project

## Objective

The goal of this tutorial is to learn about "projects" and "frames."  All the commands
of emodpy-workflow must be used within a "project".  You will learn how to create a
new project and the files that exist in a project.  Most of the other commands require
a "frame".  A frame is an idea/scenario that involves changing parameters and/or code.
You will learn how to create a frame in this tutorial.

## Prerequisites

You must complete the [setup and installation instructions](setup.md) before you can
start this tutorial.

## General command format

emodpy-workflow provides you with a collection of [commands](../reference/commands.md)
that allow you to perform the tasks of creating projects, running EMOD, calibrating,
downloading data, and so on.  To use a command, you must be in the top-level
directory of your project and type the command similarly to the following:

```
python -m emodpy_workflow.scripts.XXX <arguments>
```

Test that you can execute a command:

```
python -m emodpy_workflow.scripts.new_project -h
```

You should see output similar to the following:

```doscon
usage: new_project.py [-h] -d DEST_DIR

optional arguments:
  -h, --help            show this help message and exit
  -d DEST_DIR, --directory DEST_DIR
                        Path of new project directory to create and populate with initial files and subdirectories. Required.
```

If you see this, you are ready!!

## Create your project

The 'new_project' command is use to create a
[new project directory](../reference/projects.md).  It is assumed that all
of the other commands will be executed in this project directory.

Execute new_project command:

```
python -m emodpy_workflow.scripts.new_project -d my_project
```

When the command is finished, you should see something similar to the following:

```
Created new project directory: my_project
```

## Explore what is in the project

Let's look into the directory that was just created and learn about what is in it and why.

1. Look at what is in our training directory by executing the following command:

    === "Windows"
        ```doscon
        dir
        ```
    === "Linux"
        ```bash
        ls -l
        ```

    You should see something similar to the following:

    === "Windows"
        ```doscon
        Directory of C:\work\my_tutorial

        08/12/2025  09:28 AM    <DIR>          .
        08/12/2025  09:28 AM    <DIR>          ..
        08/11/2025  09:49 AM    <DIR>          env
        08/11/2025  09:54 AM    <DIR>          my_project
        ```
    === "Linux"
        ```doscon
        total 8
        drwxrwxr-x 5 dbridenbecker dbridenbecker 4096 Sep  4 19:48 env
        drwxrwxr-x 3 dbridenbecker dbridenbecker 4096 Sep  4 19:49 my_project
        ```

    - `env` - This folder is the one that contains our Python virtual environment.
    It contains all of the Python tools we need for running EMOD, plotting data, etc.
    - `my_project` - This is the folder we just created with the **new_project**
    command.  All future emodpy-workflow commands must be executed inside the
    `my_project` folder.

2. Look at what is in the project directory by executing the following commands:

    === "Windows"
        ```doscon
        cd my_project
        dir
        ```
    === "Linux"
        ```bash
        cd my_project
        ls -l
        ```

    You should see something similar to the following:

    === "Windows"
        ```doscon
        Directory of C:\work\my_tutorial\my_project

        08/12/2025  10:37 AM    <DIR>          .
        08/12/2025  10:37 AM    <DIR>          ..
        08/08/2025  02:41 PM             1,267 idmtools.ini
        08/11/2025  09:54 AM             3,542 manifest.py
        08/11/2025  09:54 AM               355 __init__.py
        08/11/2025  09:54 AM    <DIR>          __pycache__
        ```
    === "Linux"
        ```doscon
        total 16
        -rw-rw-r-- 1 dbridenbecker dbridenbecker 1267 Sep  4 19:49 idmtools.ini
        -rw-rw-r-- 1 dbridenbecker dbridenbecker  355 Sep  4 19:49 __init__.py
        -rw-rw-r-- 1 dbridenbecker dbridenbecker 3542 Sep  4 19:49 manifest.py
        drwxrwxr-x 2 dbridenbecker dbridenbecker 4096 Sep  4 19:49 __pycache__
        ```

    - `idmtools.ini` - This file contains information about the computing platforms
    where you are running EMOD like where you want the simulation files to be created.
    The [reference](../reference/projects.md#idmtoolsini) contains the
    details about this file.
    - `manifest.py` - This file contains information about how you are running EMOD,
    like where the EMOD binary is stored and if you are using simulation post processing.
    The [reference](../reference/projects.md#manifestpy) contains the
    details about this file.
    - `__init__.py` - A normal Python file that defines the folder as a Python package.
    - `__pycache__` - This folder is created by Python to store compiled bytecode files for
    Python modules. 

## Create a baseline "frame"

In emodpy-workflow, a "frame" is used to define a collection of parameters and code.
This collection could be your definition of a scenario, like vaccinating people for
HIV on their 15th birthday.  See the [reference](../reference/frames.md)
for more information.

Before you start creating new scenarios, you will want to create the frame that you will
consider as your "baseline."  This is a scenario too, but it will be the scenario that
you will compare everything to.  Typically, you setup the baseline to be the standard
country model.

1. Execute the following to see the options of the 'new_frame' command:

    ```
    python -m emodpy_workflow.scripts.new_frame -h
    ```

    You should see something similar to the following:

    ```doscon
    (env) C:\work\my_tutorial\my_project>python -m emodpy_workflow.scripts.new_frame -h
    usage: new_frame.py [-h] --country COUNTRY_MODEL --dest DEST_FRAME

    optional arguments:
      -h, --help            show this help message and exit
      --country COUNTRY_MODEL
                            Country model name to make new frame with. Required.
      --dest DEST_FRAME     Name of new model frame. Required.
    ```

    For this tutorial, we will use the country model called "ZambiaForTraining" and
    will name this frame "baseline".

2. Execute the following to create the "baseline" frame

    ```
    python -m emodpy_workflow.scripts.new_frame --country ZambiaForTraining --dest baseline
    ```

    When the command is finished, you should see output similar to the following:

    ```doscon
    Variables are: {'country': 'ZambiaForTraining'}
    -- Created file in frame: baseline file: campaign.py
    -- Created file in frame: baseline file: config.py
    -- Created file in frame: baseline file: demographics.py
    -- Created file in frame: baseline file: __init__.py
    Created new frame: baseline using country model: ZambiaForTraining
    ```

3. Execute the following command to see that a new `frames` directory has been created

    === "Windows"
        ```
        dir
        ```
    === "Linux"
        ```
        ls -l
        ```

    You should see something similar to the following:

    === "Windows"
        ```doscon
        Directory of C:\work\my_tutorial\my_project

        09/02/2025  09:53 AM    <DIR>          .
        09/02/2025  09:53 AM    <DIR>          ..
        09/02/2025  09:53 AM    <DIR>          frames
        08/08/2025  02:41 PM             1,267 idmtools.ini
        08/11/2025  09:54 AM             3,542 manifest.py
        08/11/2025  09:54 AM               355 __init__.py
        08/11/2025  09:54 AM    <DIR>          __pycache__
        ```
    === "Linux"
        ```doscon
        total 20
        drwxrwxr-x 3 dbridenbecker dbridenbecker 4096 Sep  4 20:03 frames
        -rw-rw-r-- 1 dbridenbecker dbridenbecker 1267 Sep  4 19:49 idmtools.ini
        -rw-rw-r-- 1 dbridenbecker dbridenbecker  355 Sep  4 19:49 __init__.py
        -rw-rw-r-- 1 dbridenbecker dbridenbecker 3542 Sep  4 19:49 manifest.py
        drwxrwxr-x 2 dbridenbecker dbridenbecker 4096 Sep  4 19:49 __pycache__
        ```

4. Execute the following command to see what is in the `frames` directory:

    === "Windows"
        ```
        dir frames
        ```
    === "Linux"
        ```
        ls -l frames
        ```

    You should see something similar to the following:

    === "Windows"
        ```doscon
        Directory of C:\work\my_tutorial\my_project\frames

        09/02/2025  09:53 AM    <DIR>          .
        09/02/2025  09:53 AM    <DIR>          ..
        09/02/2025  09:53 AM    <DIR>          baseline
        ```
    === "Linux"
        ```doscon
        total 4
        drwxrwxr-x 2 dbridenbecker dbridenbecker 4096 Sep  4 20:03 baseline
        ```

    If you were to execute the `new_frame` command again or the `extend_frame`
    command a new directory will be created in the frames directory with
    the name you give the frame.

5. Execute the following command to see what is in the `baseline` directory:

    === "Windows"
        ```
        dir frames\baseline
        ```
    === "Linux"
        ```
        ls -l frames/baseline
        ```

    You should see something similar to the following:

    === "Windows"
        ```doscon
        Directory of C:\work\my_tutorial\my_project\frames\baseline

        09/02/2025  09:53 AM    <DIR>          .
        09/02/2025  09:53 AM    <DIR>          ..
        09/02/2025  09:53 AM             1,377 campaign.py
        09/02/2025  09:53 AM             5,446 config.py
        09/02/2025  09:53 AM             1,408 demographics.py
        09/02/2025  09:53 AM             1,427 __init__.py
        ```
    === "Linux"
        ```doscon
        total 20
        -rw-rw-r-- 1 dbridenbecker dbridenbecker 1350 Sep  4 20:03 campaign.py
        -rw-rw-r-- 1 dbridenbecker dbridenbecker 5365 Sep  4 20:03 config.py
        -rw-rw-r-- 1 dbridenbecker dbridenbecker 1381 Sep  4 20:03 demographics.py
        -rw-rw-r-- 1 dbridenbecker dbridenbecker 1398 Sep  4 20:03 __init__.py
        ```

    The `campaign.py`, `config.py`, and `demographics.py` files give you hooks
    into how these different elements of an EMOD simulation are configured.
    When using `new_frame`, they will all default to what is defined in the
    country model, in this case, `ZambiaForTraining`.  The `__init__.py` file
    contains the logic to tie them together for emodpy-workflow.  More information
    on `__init__.py` can be found in the [reference](../reference/frames.md#initpy).

6. View the contents of these files.

    Using a text editor, open these files and inspect their contents.  In each
    file, you should see two methods:

    - `initialize_XXX()`
    - `get_campaign_XXX_calls()`

    where "XXX" is replaced with config, campaign, or demographics depending on
    the file.  Depending on how you to modify the country model, these are the
    two methods that you will modify.

    See the other tutorials on modifying the configuration:

    - [Modify Configuration](modify_configuration.md)
    - [Modify Campaign](modify_campaign.md)
    - [Modify Demographics](modify_demographics.md)

## Next up: Running your baseline frame

Try the [Run EMOD](run_emod.md) next to run your new baseline frame.
