import os
from types import ModuleType
from typing import List, Callable, Dict, Any, Union

from idmtools.entities.itask import ITask

from emodpy.emod_task import EMODTask
from idmtools.assets import Asset
from idmtools.assets.asset_collection import AssetCollection

from emodpy_workflow.lib.models.imodel import IModel
from emodpy_workflow.lib.utils.builders.general import build_parameterized_object
from emodpy_workflow.lib.utils.wrappers import generate_demographics_builder_wrapper, \
    generate_map_sample_to_model_input_wrapper, generate_config_builder_wrapper, generate_campaign_builder_wrapper


class IEMODModel(IModel):

    def __init__(self,
                 manifest: ModuleType,
                 config_initializer: Callable,
                 config_parameterizer: Callable,
                 demographics_initializer: Callable,
                 demographics_parameterizer: Callable,
                 campaign_initializer: Callable,
                 campaign_parameterizer: Callable,
                 custom_sample_constrainer: Callable = None,
                 build_reports: Callable = None,
                 embedded_python_scripts_paths: Union[str, list[str]] = None,
                 site=None,
                 num_cores=1,
                 calibration_parameters=None):
        self.manifest = manifest
        self.kwargs = {} # TODO: either restore or carry-through its removal

        self.config_initializer = config_initializer
        self.config_parameterizer = config_parameterizer
        self.demographics_initializer = demographics_initializer
        self.demographics_parameterizer = demographics_parameterizer
        self.campaign_initializer = campaign_initializer
        self.campaign_parameterizer = campaign_parameterizer
        self.build_reports = build_reports
        self.site = site
        self.calibration_parameters = calibration_parameters
        if custom_sample_constrainer is None:
            custom_sample_constrainer = self._default_sample_constrainer
        self.custom_sample_constrainer = custom_sample_constrainer
        self.embedded_python_scripts_paths = embedded_python_scripts_paths
        self.asset_collection_of_container = self.manifest.asset_collection_of_container

    # TODO: make sure to document this and possibly add it to the frame template directory!
    @staticmethod
    def _default_sample_constrainer(sample):
        # This is a default, do-nothing-extra version of this method
        return sample

    def inputs_builder(self, random_run_number=True):
        builder = generate_map_sample_to_model_input_wrapper(
            config_builder=generate_config_builder_wrapper(config_builder=self.build_parameterized_config),
            campaign_builder=generate_campaign_builder_wrapper(campaign_builder=self.build_parameterized_campaign),
            demographics_builder=generate_demographics_builder_wrapper(demographics_builder=self.build_parameterized_demographics),
            random_run_number=random_run_number
        )
        return builder

    # TODO: add detection of in-config parameters? Build initial config and report? Or read schema?
    @property
    def available_parameters(self) -> Dict[str, List]:
        config = self.config_initializer(manifest=self.manifest)
        demographics = self.demographics_initializer(manifest=self.manifest)
        campaign = self.campaign_initializer(manifest=self.manifest)
        parameters = {
            'config': [p for pc in self.config_parameterizer(config)
                       for p in pc.labeled_hyperparameters.keys()],
            'demographics': [p for pc in self.demographics_parameterizer(demographics)
                             for p in pc.labeled_hyperparameters.keys()],
            'campaign': [p for pc in self.campaign_parameterizer(campaign)
                         for p in pc.labeled_hyperparameters.keys()],
        }
        return parameters

    def initialize_task(self):
        # initializing with no config, demographics, or campaign.
        # These will get built later per-simulation.
        return EMODTask.from_defaults(schema_path=self.manifest.schema_path,
                                      eradication_path=self.manifest.executable_path,
                                      embedded_python_scripts_path=self.embedded_python_scripts_paths,
                                      report_builder=self.build_reports)

    def initialize_executable(self, bootstrapper=None, **kwargs):
        # subclasses should import the appropriate emod model bootstrapper and pass it in, unless no building is
        # desired, of course.
        if bootstrapper is not None:
            # setup model binary in the models bin dir
            pwd = os.getcwd()
            bootstrapper.setup(os.path.dirname(self.manifest.executable_path))
            # because of bug in emod_pip_builder issue 1:
            # https://github.com/jonathanhhb/emod_pip_builders/issues/1
            os.chdir(pwd)

    #
    # methods to do actual building of configuration objects for EMOD
    #

    def build_parameterized_config(self, parameters_to_set: Dict[str, Any]):
        initialized_config = self.config_initializer(manifest=self.manifest)
        config = build_parameterized_object(parameters_to_set=parameters_to_set,
                                            parameterized_calls=self.config_parameterizer(config=initialized_config),
                                            obj=initialized_config)
        return config

    def build_parameterized_demographics(self, parameters_to_set: Dict[str, Any]):
        initialized_demographics = self.demographics_initializer(manifest=self.manifest)
        demographics = build_parameterized_object(parameters_to_set=parameters_to_set,
                                                  parameterized_calls=self.demographics_parameterizer(demographics=initialized_demographics),
                                                  obj=initialized_demographics)
        return demographics

    def build_parameterized_campaign(self, parameters_to_set: Dict[str, Any]):
        initialized_campaign = self.campaign_initializer(manifest=self.manifest)
        campaign = build_parameterized_object(parameters_to_set=parameters_to_set,
                                              parameterized_calls=self.campaign_parameterizer(campaign=initialized_campaign),
                                              obj=initialized_campaign)
        return campaign


