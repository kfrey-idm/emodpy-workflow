# Sweep files

A sweep file is a Python file that specifies sets of hyperparameter overrides,
often referred to as "scenarios". Scenarios address specific scientific questions,
typically (but not exclusively) related to predicting the outcome of potential
interventions and events.

These overrides are applied to simulation inputs building of specific frame(s)
after any other parameter overrides (they have the highest precedence).

Sweep file format by example:

```python linenums="1"
# A sweep Python file must contain a 'parameter_sets' attribute, which is a dict
# with keys being names of frames and values being dicts of param_name:value
# entries OR a generator of such dicts
parameter_sets = {
    # This key indicates the contained information is for building off
    # the 'baseline' frame
    'baseline': {
        # Each dict in 'sweeps' list is a set of param: value overrides to
        # be applied - a scenario.  Note that the parameter lists are arbitrary.
        # Each scenario can include as many or few parameters as you want.
        # One experiment will be created per entry in 'sweeps'
        'sweeps': [
            # Optional: A provided 'experiment_name' in a sweep entry will
            # name the corresponding experiment. Default experiment name is the
            # name of the frame.
            {
                'experiment_name': 'condom_maternal_higher',
                'Condom_Transmission_Blocking_Probability': 0.9,
                'Maternal_Infection_Transmission_Probability': 0.4
            }, {
                'experiment_name': 'condom_maternal_lower',
                'Condom_Transmission_Blocking_Probability': 0.7,
                'Maternal_Infection_Transmission_Probability': 0.2
            }, {
                'experiment_name': 'condom_higher',
                'Condom_Transmission_Blocking_Probability': 0.9
            },
            {}  # This is a do nothing different, baseline scenario
        ]
    }
}
```
