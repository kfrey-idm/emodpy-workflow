# This frame built from frame: {source_frame} via script:
# python -m emodpy_workflow.scripts.extend_frame

from typing import List

import emod_api
import emod_api.campaign as campaign
from emodpy_hiv.parameterized_call import ParameterizedCall

from .. import {source_frame} as source_frame


def initialize_campaign(manifest) -> emod_api.campaign:
    campaign = source_frame.model.campaign_initializer(manifest)
    # Add any additional campaign initialization here
    return campaign


def get_campaign_parameterized_calls(campaign: emod_api.campaign) -> List[ParameterizedCall]:
    parameterized_calls = source_frame.model.campaign_parameterizer(campaign=campaign)
    # Add any additional ParameterizedCalls here
    return parameterized_calls
