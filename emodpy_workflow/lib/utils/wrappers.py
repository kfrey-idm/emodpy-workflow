from functools import partial
from typing import Callable

from emodpy_workflow.lib.utils.runtime import map_sample_to_model_input, constrain_sample

from idmtools_calibra.calib_manager import SampleIndexWrapper


def generate_config_builder_wrapper(config_builder: Callable) -> Callable:
    def config_builder_wrapper(params: dict = None):
        config = config_builder(parameters_to_set=params)
        return config
    return config_builder_wrapper


def generate_campaign_builder_wrapper(campaign_builder: Callable) -> Callable:
    def campaign_builder_wrapper(params: dict = None):
        campaign = campaign_builder(parameters_to_set=params)
        return campaign
    return campaign_builder_wrapper


def generate_demographics_builder_wrapper(demographics_builder: Callable) -> Callable:
    def demographics_builder_wrapper(params: dict = None):
        demographics = demographics_builder(parameters_to_set=params)
        return demographics
    return demographics_builder_wrapper


def generate_map_sample_to_model_input_wrapper(config_builder: Callable, campaign_builder: Callable,
                                               demographics_builder: Callable,
                                               random_run_number: bool) -> SampleIndexWrapper:
    return SampleIndexWrapper(partial(map_sample_to_model_input,
                                      config_builder=config_builder,
                                      campaign_builder=campaign_builder,
                                      demographics_builder=demographics_builder,
                                      random_run_number=random_run_number))


def constrain_sample_wrapper(custom_sample_constrainer: Callable) -> Callable:
    return partial(constrain_sample, custom_sample_constrainer=custom_sample_constrainer)

