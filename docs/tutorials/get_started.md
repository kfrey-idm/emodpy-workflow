# Get Started with EMOD-HIV and emodpy-workflow

## Assumptions

The following tutorials assume you are familiar with the following:

- Python
- Linux or Windows command-line
- Have a basic understanding of EMOD is

If you have been using EMOD-HIV with DtkTools, this [comparison](../reference/dtktools_comparison.md)
page will help you to understand what is different from how you have been using EMOD-HIV.

## Installation

If you are doing the tutorials on your own computer or cluster, go to the
[installation guide](../installation.md) for creating a virtual environment
and installing emodpy-workflow in it.

If you are using the **GitHub Codespaces** with the emodpy-workflow repository,
everything should already be installed.

## Create a project

The ["create project"](create_project.md) tutorial will guide you through creating
your first emodpy-workflow project.  Everything you do with emodpy-workflow
must be done within a project.

## Run EMOD
The ["run EMOD"](run_emod.md) tutorial will get you changing parameters, running
the model, and plotting data.  It will not only show you how easy it is to run EMOD,
it will teach you how to run EMOD in a way that can help you quickly add new features
and find issues.

## Change report output
The ["change reports"](change_reports.md) tutorial will introduce you to the different
data out of EMOD via "reports".  EMOD can provide tons of information about the state
of the individuals in the simulation and reports are the way to get that information.

## Change the configuration

The ["change configuration"](change_configuration.md) tutorial will teach you how to
change parameters in a structured way so you can easily compare the new parameters to
the baseline.

## Change the demographics

The ["change demographics"](change_demographics.md) tutorial show you how you can
change the different aspects of the population and their behaviors.  You will learn
how to change the initial ages of the population, add an individual property, and
change how often people create commercial relationships.

## Change the campaign

The campaign is where users make most of their changes.  It is where you determine
the "when, why, where, to whom, and what" of interventions.
The ["change campaign"](change_campaign.md) tutorial will teach you how to things
like add an intervention or change a state of the cascade of care.

## Make a parameter calibrate-able or sweep-able - ParameterizedCalls

emodpy-workflow provides a standard way of calibrating or sweeping any parameter
that is "available".  The ["using ParameterizedCall"](using_parameterized_calls.md)
tutorial will how to make a parameter availabe.

## Sweep a parameter

The ["sweep parameter"](sweep_parameter.md) tutorial will show you how to sweep
a parameter that is "available".  Users typically do this to see how different
values of a parameter impact the simulation outcome.

## Run a simple calibration

The ["run calibration"](run_calibration.md) tutorial will teach you how to execute
a simple calibration on a couple of parameters using emodpy-workflow.  It is NOT
meant as an introduction to calibration, but if you understand calibration, it
provides you with the instructions on how to do it.

Clark - You will do your first simple calibration with emodpy-workflow.
You will learn how to specify reference data and the hyperparameters to calibrate.
You will also learn how to resample a calibration process (select calibrated
parameterizations). However, it is not intended to teach the art/science of 
calibration.

## Use a calibration

The ["Use a Calibration" tutorial](use_calibration.md) will show you how to use a calibration
as input to configure and run EMOD. 

