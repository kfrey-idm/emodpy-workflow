# This frame built via script:
# python -m emodpy_workflow.scripts.new_frame

from typing import List

from emod_api.schema_to_class import ReadOnlyDict
from emodpy.reporters.base import ReportFilter
from emodpy_hiv.countries import {country} as country_model
from emodpy_hiv.parameterized_call import ParameterizedCall
from emodpy_hiv.reporters.reporters import Reporters, ReportHIVByAgeAndGender


# This function initializes the config object at input building time. This is
# registered to the model-attribute object in __init__.py for discovery by core scripts.
# This function must take exactly one argument: manifest
def initialize_config(manifest):
    config = country_model.initialize_config(schema_path=manifest.schema_path)
    # easily accessible control to alter simulation population size for this frame (and importers of this frame)
    config.parameters.x_Base_Population = config.parameters.x_Base_Population
    # Add any additional config initialization here
    return config


# All functions used with ParameterizedCall objects must have as a first argument: config/campaign/demographics
# This required because the code calling these will always pass an object to be modified as the first argument.
# Additional arguments can be used to provide calibration/scenario parameters or project-level static overrides.
# def modify_base_infectivity(config, Base_Infectivity: int = None):
#     if Base_Infectivity is not None:
#         config.parameters.Base_Infectivity = Base_Infectivity


# This function generates a list of functions with parameterized values to call at input building time. All
# config parameters available for calibration and scenario design must be defined here via ParameterizedCall
# objects. This function is registered to the model-attribute object in __init__.py for discovery by core scripts.
# This function cannot accept any arguments.
def get_config_parameterized_calls(config: ReadOnlyDict) -> List[ParameterizedCall]:
    parameterized_calls = country_model.get_config_parameterized_calls(config=config)
    # ParameterizedCall objects define what parameters are available for calibration and scenario design as well as
    # what code will be executed to generate the fully formed input object:
    # dict key: value means -> parameter_name: project_override_value . A value of None means use the existing default value.
    # Any function arguments in 'hyperparameters' will be available for calibration/scenarios. A value is a project default.
    # Any function arguments in 'non_hyperparameters' will be NOT available for calibration/scenarios. A value is a project default.
    # Any unmentioned function arguments run with existing default values.
    # At input building time, all hyperparameters and non_hyperparameters with non-None values will be passed to the
    # specified 'func' to update the input object being built.
    # If you need to disambiguate any hyperparameters, e.g. coverage (for node 1) and coverage (for node 2), you can
    # give each a separate label in two ParameterizedCall objects. Use e.g. label='node1', label='node2' .
    #
    # Add any additional ParameterizedCalls here
    # pc = ParameterizedCall(func=modify_base_infectivity, hyperparameters={{'Base_Infectivity': None}})
    # parameterized_calls.append(pc)
    return parameterized_calls


# this function adds the reports defined in the country_model to your simulations
def build_reports(reporters: Reporters):
    # reporters = country_model.build_reports(reporters)
    # Add any additional report building here
    # Please note, reports of the ConfigReporter base class only allow for one reporter of each class to be added.
    # Trying to add another ConfigReporter of the same class will result in error.
    # If you do not wish to use the reports available in the source_frame, you can remove the line above
    # and add your own reporters here as needed.
    reporters.add(ReportHIVByAgeAndGender(reporters_object=reporters,
                                          collect_gender_data=True,
                                          collect_age_bins_data=[15, 20, 25, 30, 35, 40, 45, 50],
                                          collect_circumcision_data=True,
                                          collect_hiv_data=True,
                                          collect_hiv_stage_data=False,  # default
                                          collect_on_art_data=True,
                                          collect_ip_data=None,  # default
                                          collect_intervention_data=["Traditional_MC"],
                                          collect_targeting_config_data=None,  # default
                                          add_transmitters=False,  # default
                                          stratify_infected_by_cd4=False,  # default
                                          event_counter_list=["NewInfectionEvent"],
                                          add_relationships=True,
                                          add_concordant_relationships=False,  # default
                                          reporting_period=182.5,
                                          report_filter=ReportFilter(start_year=1980,
                                                                     end_year=2050)))
    return reporters
