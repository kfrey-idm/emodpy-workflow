# This frame built from frame: {source_frame} via script:
# python -m emodpy_workflow.scripts.extend_frame

from typing import List

from emod_api.schema_to_class import ReadOnlyDict
from emodpy_hiv.parameterized_call import ParameterizedCall
from emodpy_hiv.reporters.reporters import Reporters

from .. import {source_frame} as source_frame


def initialize_config(manifest):
    config = source_frame.model.config_initializer(manifest=manifest)
    # easily accessible control to alter simulation population size for this frame (and importers of this frame)
    config.parameters.x_Base_Population = config.parameters.x_Base_Population
    # Add any additional config initialization here
    return config


def get_config_parameterized_calls(config: ReadOnlyDict) -> List[ParameterizedCall]:
    parameterized_calls = source_frame.model.config_parameterizer(config=config)
    # Add any additional ParameterizedCalls here
    return parameterized_calls


def build_reports(reporters: Reporters):
    reporters = source_frame.model.build_reports(reporters)
    # Add any additional report building here
    # Please note, reports of the ConfigReporter base class only allow for one reporter of each class to be added.
    # Trying to add another ConfigReporter of the same class will result in error.
    # If you do not wish to use the reports available in the source_frame, you can remove the line above
    # and add your own reporters here as needed.
    return reporters
