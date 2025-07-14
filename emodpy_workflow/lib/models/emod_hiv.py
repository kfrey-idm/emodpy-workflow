from idmtools.assets import Asset
from idmtools.entities.itask import ITask

from emodpy_workflow.lib.models.iemod_model import IEMODModel
from emodpy_workflow.lib.utils.project_data import get_ingest_information
from emodpy_workflow.lib.utils.runtime import add_post_channel_config_as_asset, get_embedded_python_paths


class EMOD_HIV(IEMODModel):

    def __init__(self, ingest_form_path=None, **kwargs):
        self.ingest_form_path = ingest_form_path
        if self.ingest_form_path is None:
            embedded_python_paths, self.post_processing_config_file_setter = self._handle_python_processing()
            calibration_parameters = None
            site = None
        else:
            ingest_info, site = get_ingest_information(ingest_filename=ingest_form_path)
            calibration_parameters = ingest_info['params']
            embedded_python_paths, self.post_processing_config_file_setter = self._handle_python_processing(channels=ingest_info['channels'],
                                                                                                            reference_data=ingest_info['reference'],
                                                                                                            site_info=ingest_info['site_info'],
                                                                                                            pre_processing_path=kwargs['manifest'].pre_processing_path,
                                                                                                            in_processing_path=kwargs['manifest'].in_processing_path,
                                                                                                            post_processing_path=kwargs['manifest'].post_processing_path)
        super().__init__(embedded_python_scripts_paths=embedded_python_paths, calibration_parameters=calibration_parameters,
                         site=site, **kwargs)

    @staticmethod
    def _handle_python_processing(channels=None, reference_data=None, site_info=None,
                                  pre_processing_path=None, in_processing_path=None, post_processing_path=None):
        # generate channel config as an asset if requested and add post processing to match
        if channels and reference_data and site_info:
            def post_processing_config_file_setter(task):
                add_post_channel_config_as_asset(task=task, channels=channels, reference_data=reference_data, site_info=site_info)

            embedded_python_paths = get_embedded_python_paths(pre_processing_path=pre_processing_path,
                                                                in_processing_path=in_processing_path,
                                                                post_processing_path=post_processing_path)
        else:
            post_processing_config_file_setter = None
            embedded_python_paths = get_embedded_python_paths(pre_processing_path=pre_processing_path,
                                                                in_processing_path=in_processing_path)
        return embedded_python_paths, post_processing_config_file_setter

    @staticmethod
    def add_ingest_form_to_assets(task: ITask, path: str) -> ITask:
        """
        Simply adds the ingest form specified as an asset to the provided task for logging purposes
        Args:
            task: the Task object to add the ingest form to
            path: path of the ingest form to add

        Returns: the provided task object, modified
        """
        task.common_assets.add_asset(Asset(path))
        return task

    def initialize_task(self):
        task = super().initialize_task()

        # add the post processor config file if post-processing is requested
        if self.post_processing_config_file_setter:
            self.post_processing_config_file_setter(task=task)
        if self.ingest_form_path is not None:
            self.add_ingest_form_to_assets(task, self.ingest_form_path)
        return task

    def initialize_executable(self, **kwargs):
        import emod_hiv.bootstrap as bootstrap
        super().initialize_executable(bootstrapper=bootstrap, **kwargs)
