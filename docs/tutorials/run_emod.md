# Run EMOD

## Objective

The goal of this tutorial is for you to learn how to run a single simulation of EMOD-HIV
using emodpy-workflow.  There are many ways to run EMOD:
- from the command line
- using emodpy-hiv
- using emodpy-workflow
- on an HPC
- on your laptop
- as part of a parameter calibration
- as a parameter sweep
However, you will frequently want to run a single simulation when you creating different
behaviors in your simulation or debugging.

## Prerequisites

If you are running on your local machine, you must have Docker installed and running.
If you do not, please see [Installing Docker](../reference/installing_docker) for more information.

Before you can run EMOD, you must have an emodpy-workflow project and a frame.
If you don't have these, please see [Create project](create_project).

## Control how and where EMOD runs

Before we can start using the "run" command, we first need to know where we can control
the what and where EMOD runs.  The [manifest.py](../reference/manifest) file is used by
emopdy-workflow to know what EMOD executable binary to use, to specify a container for
the executable binary to run in, to specify any simulation post processing scripts, etc.
The [idmtools.ini](../reference/idmtools) file is used to specify how EMOD is run on
different platforms, where a "platform" is a computing device like an HPC or laptop.

### View manifest.py

1. In the root of your project directory, open the `manifest.py` file.
2. On about line 39, you should see a variable called `executable_path`.  This tells
emodpy-workflow where to get the EMOD executable binary.
3. Just below that you should also see a variable called "asset_collection_of_container".
This is variable is used by emodpy-workflow to know what container to run EMOD in.
(Containers reduce your need to install everything needed to run EMOD.)
4. For more information see [manifest.py](../reference/manifest).

### View idmtools.ini

1. In the root of your project directory, open the `idmtools.ini` file.
2. Towards the top of the file, you should see something similar to the following:

    ```
    [ContainerPlatform]
    type          = Container
    job_directory = emodpy-jobs
    ```

3. This tells emodpy-workflow that there is a platform called "ContainerPlatform" that is
of type "Container" and that simulation jobs should go in to the "emodpy-jobs" directory.
4. For more information see [idmtools.ini](../reference/idmtools).

## Create a `results` directory

Since we will be running EMOD multiple times, it is handy to put the results into their
own directory.

1. Execute the following command in the root of your project (the directory that contains the manifest.py file).

    ```
    mkdir results
    ```

    This should create a directory called 'results' in your project directory.

## Using the `run` command

To run EMOD, we will use the emodpy-workflow `run` command.

1. Execute the following command in the root of your project (the directory that contains the manifest.py file).

    ```
    python -m emodpy_workflow.scripts.run -h
    ```

    This should produce output similar to the following:

    ```
    usage: run.py [-h] [-s SAMPLES_FILE] -N SUITE_NAME -F FRAMES [-f DOWNLOAD_FILENAMES] -o OUTPUT_DIR -p PLATFORM
                [-S SWEEP]

    optional arguments:
    -h, --help            show this help message and exit
    -s SAMPLES_FILE, --samples SAMPLES_FILE
                            csv file with base samples to use for simulation generation. Runs one sim per frame with
                            configs as-is if not provided.
    -N SUITE_NAME, --suite-name SUITE_NAME
                            Name of suite for experiments to be run within (Required).
    -F FRAMES, --frames FRAMES
                            Comma-separated list of model frames to run (Required).
    -f DOWNLOAD_FILENAMES, --files DOWNLOAD_FILENAMES
                            Filenames to download from scenario simulations. Paths relative to simulation directories.
                            Comma-separated list if more than one (Default: do not download files)
    -o OUTPUT_DIR, --output-dir OUTPUT_DIR
                            Directory to write receipt to (always) and scenario output files (if downloading).
    -p PLATFORM, --platform PLATFORM
                            Platform to run simulations on (Required).
    -S SWEEP, --sweep SWEEP
                            Python module to load with a sweep definition to generate extra experiments with (Default: no
                            sweeping).
    ```

2. For our purposes, we are going to focus on the following arguments:
    - _suite name_ - This is the name you give to a collection of experiments, 'my_first_suite'.
    - _frame_ - This is the name of the frame who's configuration is what you want to use.
    In our case, it will be 'baseline'
    - _output directory_ - The path of the directory to put the data for your run, say 'results/my_first_run'.
    - _platform_ - This is the name of a platform defined in your 'idmtools.ini' file.
    We will be using 'ContainerPlatform'.

3. Execute the following command:

    ```
    python -m emodpy_workflow.scripts.run -N my_first_suite -F baseline -o results/my_first_run -p ContainerPlatform
    ```

    You should see output similar to the following:

    ```
    INI File Found: C:\work\emodpy-training\idmtools.ini
    ```

    ```
    Initializing ContainerPlatform with:
    {
    "job_directory": "emodpy-jobs"
    }
    Creating Suites: 100%|████████████████████████████████████████████████████████████████████████| 1/1 [00:00<?, ?suite/s]
    Creating Experiments:   0%|                                                              | 0/1 [00:00<?, ?experiment/s]>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
    Total parameter access counts:
    {}
    <<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<
    Creating Experiments: 100%|██████████████████████████████████████████████████████| 1/1 [00:06<00:00,  6.50s/experiment]
    Initializing objects for creation: 0simulation [00:00, ?simulation/s]>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
    Total parameter access counts:
    {}
    <<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<
    Commissioning Simulations: 100%|█████████████████████████████████████████████████| 1/1 [00:00<00:00, 17.86simulation/s]
    job_directory: C:\work\emodpy-training\emodpy-jobs
    suite: 2cf29edc-6b4d-459b-9542-3eae5c59a151
    experiment: 8ae683e4-8af6-4cd9-b8a3-5c63a5a10a17
    ```

    ```
    Experiment Directory:
    C:\work\emodpy-training\emodpy-jobs\my_first_suite_2cf29edc-6b4d-459b-9542-3eae5c59a151\my_first_suite_8ae683e4-8af6-4cd9-b8a3-5c63a5a10a17
    ```

    ```
    Container ID: c3a6a8de63be
    ```

    ```
    You may try the following command to check simulations running status:
    idmtools container status 8ae683e4-8af6-4cd9-b8a3-5c63a5a10a17
    Wrote run.py receipt to: results/my_first_run\experiment_index.csv
    Done with model experiment creation.
    ```

    !!! Note
        This means that the simulations have been submitted to start running.
        It does not mean they are done.

## Get status on your experiment

Notice how in the last four lines of the output that there is information about finding
the status of your output.  In this case, the following line

    ```
    idmtools container status 8ae683e4-8af6-4cd9-b8a3-5c63a5a10a17
    ```

says get status on experiment "8ae683e4-8af6-4cd9-b8a3-5c63a5a10a17".

If you execute that line, you should see something similar to:

```
INI File Found: C:\work\emodpy-training\idmtools.ini
```

```
Experiment Directory:
c:/work/emodpy-training/emodpy-jobs/my_first_suite_2cf29edc-6b4d-459b-9542-3eae5c59a151/my_first_suite_8ae683e4-8af6-4cd
9-b8a3-5c63a5a10a17
```

```
Simulation Count: 1
```

```
SUCCEEDED (1)
FAILED (0)
RUNNING (0)
PENDING (0)
```

!!! Note
    This only works when using the Container Platform.  To see status
    when using other platforms, please see the
    [Command Line Interface documentation](https://docs.idmod.org/projects/idmtools/en/latest/cli/cli_index.html)
    for your platform.

## View the files produced when running an experiment

When using the Container and SLURM platforms, you can access the directories where the
experiments and simulations are running.  In our case, we are using the Container Platform
and our idmtools.ini file told emodpy-workflow to put the files into a local folder
called "emodpy-jobs".  If we navigate into this folder, we can see all of the files
associated with running the experiment and simulations.  Let's go investigate.

1. From the main project directory execute the following commands:

    === "Windows"
        ```
        cd emodpy-jobs
        dir
        ```
    === "Linux"
        ```
        cd emodpy-jobs
        ls
        ```

    You should see something similar to:

    ```
    Volume in drive C is Windows
    Volume Serial Number is D277-F0D1
    ```

    ```
    Directory of C:\work\emodpy-training\emodpy-jobs
    ```

    ```
    07/22/2025  11:36 AM    <DIR>          .
    07/22/2025  11:36 AM    <DIR>          ..
    07/22/2025  11:36 AM    <DIR>          my_first_suite_2cf29edc-6b4d-459b-9542-3eae5c59a151
                0 File(s)              0 bytes
                3 Dir(s)  405,100,503,040 bytes free
    ```

    Notice the directory `my_first_suite_2cf29edc-6b4d-459b-9542-3eae5c59a151` starts
    with the name we gave the suite.

2. Look in the this directory by executing commands similar to the
following - your directory name is likely different:

    === "Windows"
        ```
        cd my_first_suite_2cf29edc-6b4d-459b-9542-3eae5c59a151
        dir
        ```
    === "Linux"
        ```
        cd my_first_suite_2cf29edc-6b4d-459b-9542-3eae5c59a151
        ls
        ```

    You should see something similar to the following:

    ```
    07/22/2025  11:36 AM    <DIR>          .
    07/22/2025  11:36 AM    <DIR>          ..
    07/22/2025  11:36 AM               476 metadata.json
    07/22/2025  11:36 AM    <DIR>          my_first_suite_8ae683e4-8af6-4cd9-b8a3-5c63a5a10a17
                1 File(s)            476 bytes
                3 Dir(s)  403,785,535,488 bytes free
    ```

    Yes, it looks very similar, but this is the experiment directory.

3. 




d.	Have the user inspect the suite, experiment, and simulation folders
e.	Point out where to look for error messages and where the output data can be found

## Download the results/output
f.	Use the download command to get the output data into their project

## Plot the results
g.	Use the plotting commands to plot InsetChart
