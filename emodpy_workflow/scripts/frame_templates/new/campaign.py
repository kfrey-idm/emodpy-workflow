# This frame built via script:
# python -m emodpy_workflow.scripts.new_frame

from typing import List

import emod_api.campaign as api_campaign
from emodpy_hiv.countries import {country} as country_model
from emodpy_hiv.parameterized_call import ParameterizedCall


# This function initializes the campaign object at input building time. This is
# registered to the model-attribute object in __init__.py for discovery by core scripts.
# This function must take exactly one argument: manifest
def initialize_campaign(manifest) -> api_campaign:
    campaign = country_model.initialize_campaign(schema_path=manifest.schema_path)
    # Add any additional campaign initialization here
    return campaign


# This function generates a list of functions with parameterized values to call at input building time. All
# campaign parameters available for calibration and scenario design must be defined here via ParameterizedCall
# objects. This function is registered to the model-attribute object in __init__.py for discovery by core scripts.
# This function cannot accept any arguments.
def get_campaign_parameterized_calls(campaign: api_campaign) -> List[ParameterizedCall]:
    parameterized_calls = country_model.get_campaign_parameterized_calls(campaign=campaign)
    # Add any additional ParameterizedCalls here
    return parameterized_calls
