# emodpy-workflow vs DtkTools

If you have already been using EMOD-HIV via DtkTools, this overview will explain
what is the same and what is different.

Even though emodpy-workflow is designed to be a general workflow tool, its development
was driven by the need to port the pre-existing EMOD-HIV workflow tools using DtkTools
to idmtools and emodpy. As such, every feature of the prior workflow has been replicated.
There is nothing that could be done in DtkTools that cannot be done with emodpy-workflow.

For those already familiar with the DtkTools EMOD-HIV workfow, this section highlights 
the correspondence of its components and features with those of emodpy-workflow. 
**Bolded** items have changed the most.


| DtkTools | emodpy-workflow |
| --- | --- |
| EMOD JSON input files | **country models** (from emodpy-hiv) |
| directories of templated JSON input files | **frames** |
| JSON KP tag parameters | **ParameterizedCalls** (from emodpy-hiv) |
| optim_script.py (calibration and configuration) | built-in calibrate command |
| ingest form (reference data and calibration configuration) | ingest form (still used, little changed) |
| calibration resampling via run_scenarios.py | built-in resample command |
| resampled_parameter_sets.csv | resampled_parameter_sets.csv (same format) |
| run_scenarios.py (scenario running tool) | built-in run and download commands |
| scenarios.csv | **sweeps.py file format** |

### Country models

Country models are Python classes that define the default "baseline" behavior of an
EMOD-HIV configuration. They often correspond to countries, but can be localized
regions of interest. They contain all information (Python functions) needed to build
a default set of EMOD-HIV inputs (config, demographics, campaign).

Country models are standard **Python code** and live in the
[emodpy-hiv repository](https://github.com/EMOD-Hub/emodpy-hiv).
Usage of country models in a project is the domain of **frames**.

### Frames

Frames are a construct in emodpy-workflow that replace directories of KP-tagged
(templated) JSON files in a project. A frame is the central point where all Python
code for building EMOD-HIV config, demographics, and campaign inputs is found by
emodpy-workflow commands. Frames can **import** and **extend** other frames to
eliminate inconsistencies. With JSON, one had to copy and modify files, creating
duplicate information that could desynchronize.

For example, one could have a **baseline** frame and several **scenario** frames
that import the baseline and then add campaign interventions.

!!! note "Warning"
    Updating any frame automatically updates all dependent frames.

### Parameterized calls

ParameterizedCalls are Python objects that directly replace the functionality of
JSON KP tags. ParameterizedCall objects let a user define a "hyperparameter"
(an arbitrary string name) that connects to an arbitrary point in the EMOD-HIV
input building code to allow modification during calibration and scenarios.
Users can add contextual labels to ParameterizedCalls to distinguish very specific
values as could be done with KP tags.

For example, instead of this KP-tagged parameter name:

```
Society__KP_Central.TRANSITORY.Relationship_Parameters.Condom_Usage_Probability.Max 
```

... one could create a ParameterizedCall hyperparameter named the following:

```
condom_usage_max--COMMERCIAL-Central
```

... which uses a contextual label of "COMMERCIAL-Central"

One can also tie multiple values together by reusing (in Python code) a hyperparameter
name with identical context.

For example, one could define and reuse a ParameterizedCall hyperparameter that connects to
each model node individually

```
condom_usage_max--COMMERCIAL-ALL-NODES
```

... which would then apply any value changes to all nodes for COMMERCIAL relationships.

Each country model defines a starting set of ParameterizedCalls and hyperparameters
for use. **Additional ones can be added to project frames**.

### Ingest forms

Ingest forms are still used for specifying observational reference data and configuring
analyzers used in the calibration process. There is virtually no difference in its usage.

The **only** sheet in an older ingest form that would need updating for use is the 
**Model Parameters** sheet:

- **map_to** column can be present but now **ignored**
- **name** column values will need updating to new hyperparameter names from old KP-tag parameter names.

### Sweep files

Scenario CSV files (like scenarios.csv) has been replaced with a new sweep Python
file format. Instead of rows of parameter overrides with parameter-named columns,
one defines lists of hyperparameter/value dictionary overrides.  Because the file
is Python instead of csv, one can utilize code to simplify the generation of complex
or repetitive sets of overrides.

For example, instead of:
```
Scenario,Campaign,Base_Infectivity
baseline,campaign.json,
high_infectivity,campaign.json,0.1
low_infectivity,campaign.json,0.001
```

... one would define:
```
parameter_sets = {
    #  This indicates experiments start with the baseline frame
    'baseline': {
        'sweeps': [
            {},  # This runs with no modifications over the baseline and is auto-named "baseline"
            {'experiment_name': 'higher_infectivity', 'Base_Infectivity': 0.1},
            {'experiment_name': 'lower_infectivity', 'Base_Infectivity': 0.001},
        ]
    }
}
```
