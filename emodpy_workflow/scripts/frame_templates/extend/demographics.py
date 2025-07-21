# This frame built from frame: {source_frame} via script:
# python -m emodpy_workflow.scripts.extend_frame

from typing import List

from emodpy_hiv.demographics.hiv_demographics import HIVDemographics
from emodpy_hiv.parameterized_call import ParameterizedCall

from .. import {source_frame} as source_frame


def initialize_demographics(manifest):
    demographics = source_frame.model.demographics_initializer(manifest=manifest)
    # Add any additional demographics initialization here
    return demographics


def get_demographics_parameterized_calls(demographics: HIVDemographics) -> List[ParameterizedCall]:
    parameterized_calls = source_frame.model.demographics_parameterizer(demographics=demographics)
    # Add any additional ParameterizedCalls here
    return parameterized_calls
