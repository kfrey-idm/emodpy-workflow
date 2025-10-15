# Use ParameterizedCalls

A ParameterizedCall is a mapping of a hyperparameter names (strings) to specific locations in the model input building
process. These mappings are used to map hyperparameter values to model changes during input build time, for example, during
model calibration or scenario running.

A ParameterizedCall is:

- **Parameterized** : It defines hyperparameters users can utilize during model input building.
- **Call** : It has a function that will be called at model input building time with any provided values for matching 
defined hyperparameters.

## By Example

Here we will explore the features and capabilities of ParameterizedCalls through a series of related examples.

They will refer to this function to be called at build time, which adds an HIV vaccine intervention to an 
EMOD-HIV campaign:

```python linenums="1"
def add_hiv_vaccine(campaign: api_campaign,
                    vaccine_efficacy: float = 1.0,
                    node_ids: List[int] = None):
    hiv_vaccine = ControlledVaccine(campaign=campaign,
                                    waning_config=Constant(constant_effect=vaccine_efficacy))
    add_intervention_triggered(campaign=campaign,
                               intervention_list=[hiv_vaccine],
                               triggers_list=["STIDebut"],
                               start_year=2026,
                               node_ids=node_ids)
    return campaign
```
### 1. Starting from scratch

This example shows a ParameterizedCall (in name only!), as it defines no hyperparameters. The result of this 
ParameterizedCall at input building time is simply the calling of function `add_hiv_vaccine` with full function 
defaults.

```python
    pc = ParameterizedCall(func=add_hiv_vaccine)
```

### 2. Adding a hyperparameter

A hyperparameter is essentially a named value. Specifically, it is the name of a parameter in one or more function
calls. Here we call out the parameter `vaccine_efficacy` of function `add_hiv_vaccine` as a hyperparameter.

```python linenums="1"
    hp = {'vaccine_efficacy': None}
    pc = ParameterizedCall(func=add_hiv_vaccine, hyperparameters=hp)
```

This example does exactly what the prior example does with one change: `vaccine_efficacy` is exposed to input building
as a hyperparameter for modification.

!!! Important
    The spelling of `vaccine_efficacy` in the ParameterizedCall
    and the `add_hiv_vaccine` function parameter must exactly match.

### 3. Hyperparameter default values

Note the prior example defined the dictionary of hyperparameters to be:

```python
hp = {'vaccine_efficacy': None}
```

What does that **None** mean?

!!! Important
    A None value for a hyperparameter defined in a ParameterizedCall means
    "use the function default". In other words, it means `vaccine_efficacy`
    is a hyperparameter, nothing else. The function `add_hiv_vaccine` still
    behaves exactly as defined with a default value of 1.0 .

But what if we want **don't** want the standard function default? We can instead do this:

```python linenums="1"
    hp = {'vaccine_efficacy': 0.8}
    pc = ParameterizedCall(func=add_hiv_vaccine, hyperparameters=hp)
```

This alternate usage indicates that `vaccine_efficacy` is a hyperparameter **and** the default value of it at input
building time should be **0.8**.

!!! Important
    Giving a hyperparameter definition a **non-None value** overrides the
    **default** behavior of the specified function.

### 4. Non-hyperparameter overrides

Sometimes you want to alter the default values of function parameters **without** making them hyperparameters. For
example, you might want to alter the default set of nodes `add_hiv_vaccine` applies to, but one would never calibrate
it. This is where non-hyperparameters come in:

```python linenums="1"
    nhp = {'node_ids': [1, 2]}
    pc = ParameterizedCall(func=add_hiv_vaccine, non_hyperparameters=nhp)
```

This indicates that `node_ids` is a not a hyperparameter **but** the default value of it at input
building time should be `[1, 2]` instead of its normal behavior.

!!! Important
    Non-hyperparameters override the **default** behavior of the specified function,
    but **do not** create hyperparameters for use, which is especially useful for
    **non-calibrateable** overrides.

### 5. Contextual labels

Sometimes you want to define more than one ParameterizedCall calling the same function. This is especially true when
non_hyperparameters are needed for context. For example:

```python linenums="1"
    pcs = []    

    nhp = {'node_ids': [1, 2]}
    hp = {'vaccine_efficacy': 0.8}
    pc = ParameterizedCall(func=add_hiv_vaccine,
                           hyperparameters=hp,
                           non_hyperparameters=nhp)
    pcs.append(pc)
    
    nhp = {'node_ids': [3, 4]}
    hp = {'vaccine_efficacy': 0.5}
    pc = ParameterizedCall(func=add_hiv_vaccine,
                           hyperparameters=hp,
                           non_hyperparameters=nhp)
    pcs.append(pc)
```

The intent of this is to define two hyperparameters named `vaccine_efficacy`,
one for nodes 1 and 2 and the second for nodes 3 and 4. 

!!! Important
    However, since they share the same name, `vaccine_efficacy`, the **actual**
    effect is a single hyperparameter named `vaccine_efficacy` that is applied
    to **both** ParameterizedCalls at input building time. They are tied together.

Tying multiple changes to a single hyperparameter **can** be a legitimate thing to
do. But not in this case. How do we fix this? We need to apply some context to 
the ParameterizedCalls.

```python linenums="1"
    pcs = []    

    nhp = {'node_ids': [1, 2]}
    hp = {'vaccine_efficacy': 0.8}
    label = 'nodes_1_and_2'
    pc = ParameterizedCall(func=add_hiv_vaccine,
                           hyperparameters=hp,
                           non_hyperparameters=nhp,
                           label=label)
    pcs.append(pc)
    
    nhp = {'node_ids': [3, 4]}
    hp = {'vaccine_efficacy': 0.5}
    label = 'nodes_3_and_4'
    pc = ParameterizedCall(func=add_hiv_vaccine,
                           hyperparameters=hp,
                           non_hyperparameters=nhp,
                           label=label)
    pcs.append(pc)
```

This shows the usage of contextual labels to disambiguate hyperparameters that otherwise have identical names. But one
needs to also specify the context when calibrating or running scenarios. The **full** names of these two hyperparameters
for calibration and scenario purposes are now:

```python linenums="1"
'vaccine_efficacy--nodes_1_and_2'
'vaccine_efficacy--nodes_3_and_4'
```

!!! Important
    The `'--'`, if present, separates the hyperparameter name (as a function
    parameter) and its contextual label, if defined.

### 6. Putting it all together (a quiz)

Now that you know about ParameterizedCalls, hyperparameters, non_hyperparameters, and their contextual labels, it is
time for a mixed up example to test your knowledge!

Try to identify in this example:

- all full hyperparameter names (including their label, if present)
- their default values
- all non_hyperparameter names (including their label, if present)
- their default values
- are any hyperparameters tied together? Might be a bug?

```python linenums="1"
    pcs = []    

    nhp = {'node_ids': [1, 2]}
    hp = {'vaccine_efficacy': 0.8}
    label = 'nodes_1_and_2'
    pc = ParameterizedCall(func=add_hiv_vaccine,
                           hyperparameters=hp,
                           non_hyperparameters=nhp,
                           label=label)
    pcs.append(pc)
    
    nhp = {'node_ids': [3, 4]}
    hp = {'vaccine_efficacy': 0.5}
    label = 'nodes_1_and_2'
    pc = ParameterizedCall(func=add_hiv_vaccine,
                           hyperparameters=hp,
                           non_hyperparameters=nhp,
                           label=label)
    pcs.append(pc)

    hp = {'vaccine_efficacy': None}
    label = 'all_nodes'
    pc = ParameterizedCall(func=add_hiv_vaccine,
                           hyperparameters=hp,
                           label=label)
    pcs.append(pc)

    hp = {'vaccine_efficacy': 0.4}
    pc = ParameterizedCall(func=add_hiv_vaccine, hyperparameters=hp)
    pcs.append(pc)

```

Answer below:

```text
hyperparameters: vaccine_efficacy--nodes_1_and_2, default 0.8
non_hyperparameters: nodes_ids, [1, 2]

hyperparameters: vaccine_efficacy--nodes_1_and_2, default 0.5
non_hyperparameters: node_ids, [3, 4]
Likely a bug here, tied to above, the nodes are different from
above but the label is shared. Probably meant to have
a label of 'nodes_3_and_4'.

hyperparameters: vaccine_efficacy--all_nodes, default 1.0 from function
non_hyperparameters: none in this ParameterizedCall, applies to all nodes
from function

hyperparameters: vaccine_efficacy, default 0.4
non_hyperparameters: none in this ParameterizedCall, applies to all nodes
from function

```
