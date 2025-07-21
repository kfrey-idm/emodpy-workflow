# This is a sample sweep/scenario file for use with run.py
#
# A sweep python file must contain a 'parameter_sets' attribute, which is a dict with keys being names of
# frames and values being dicts of param_name:value entries OR a generator of such dicts
parameter_sets = {
    # This key indicates the contained information is for building off the 'hiv_vaccine' frame
    'hiv_vaccine': {
        # Each dict in 'sweeps' list is a set of param: value overrides to be applied. A scenario.
        # Note that the parameter lists are arbitrary. Each scenario can include as many or few parameters
        # as you wish.
        # One experiment will be created per entry in 'sweeps'
        'sweeps': [
            # Optional: A provided 'experiment_name' in a sweep entry will name the corresponding experiment. Default
            #  experiment name is the name of the frame.
            {'experiment_name': 'hiv_vaccine_efficacy_1.0',  'vaccine_efficacy': 1.0},
            {'experiment_name': 'hiv_vaccine_efficacy_0.75', 'vaccine_efficacy': 0.75},
            {'experiment_name': 'hiv_vaccine_efficacy_0.5',  'vaccine_efficacy': 0.5},
        ]
    }
}
