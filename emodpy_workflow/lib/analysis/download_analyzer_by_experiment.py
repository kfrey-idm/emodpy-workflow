import os

from idmtools.entities import IAnalyzer
from idmtools.entities.simulation import Simulation


class DownloadAnalyzerByExperiment(IAnalyzer):
    """
    This analyzer is based on the DownloadAnalyzer and allows the download of files based on a Index and Repetition tags
    """

    run_number = "Run_Number"
    sample_tag = "__sample_index__"

    def __init__(self, filenames, output_path, use_run_number=True, use_sample_index=True):
        super().__init__(filenames=filenames, parse=False)
        self.filenames = filenames
        self.output_path = output_path
        self.use_run_number = use_run_number
        self.use_sample_index = use_sample_index

    def _directory_for_experiment(self, experiment_id):
        return os.path.join(self.output_path, experiment_id)

    def directory_for_experiment_and_file(self, experiment_id, filename):
        return os.path.join(self._directory_for_experiment(experiment_id=experiment_id),
                            os.path.splitext(os.path.basename(filename))[0])

    def per_group(self, items):
        # Discover all experiment ids from the items
        experiment_ids = {str(item.experiment.id) for item_id, item in items.items()}

        # make a directory matching each experiment and filename to download
        for experiment_id in experiment_ids:
            for filename in self.filenames:
                os.makedirs(self.directory_for_experiment_and_file(experiment_id=experiment_id, filename=filename),
                            exist_ok=True)

    def _construct_output_file_path(self, item: Simulation, source_filename: str) -> str:
        # Sim files will be written to directories grouped by filename
        output_dir = self.directory_for_experiment_and_file(experiment_id=str(item.experiment.id),
                                                            filename=source_filename)
        # construct the full file destination path
        dest_filename = self._construct_filename(item.tags, source_filename)
        file_path = os.path.join(output_dir, os.path.basename(dest_filename))
        return file_path

    def map(self, data, item: Simulation):
        # Create the requested files
        file_paths = []
        for source_filename in self.filenames:
            file_path = self._construct_output_file_path(item=item, source_filename=source_filename)

            with open(file_path, 'wb') as outfile:
                try:
                    outfile.write(data[source_filename])
                except Exception as e:
                    print(f"Could not write the file {source_filename} for simulation {item.id}")
            file_paths.append(file_path)
        return file_paths  # returning file_paths written out so reduce() can report them to the caller

    def _construct_filename(self, simulation_tags, filename):
        infix = []
        try:
            if self.use_sample_index:
                sample_index = simulation_tags[self.sample_tag]
                infix.append('sample{:05d}'.format(int(sample_index)))
            if self.use_run_number:
                run_number = simulation_tags[self.run_number]
                infix.append("run{:05d}".format(int(run_number)))
        except KeyError:
            raise KeyError(f'Experiment simulations must have the following tags in order to be compatible:'
                           f'\n- {self.sample_tag} for the sample index'
                           f'\n- {self.run_number} for the repetition/run number')

        prefix, extension = os.path.splitext(filename)
        constructed_filename = '_'.join([prefix, *infix]) + extension
        return constructed_filename

    def reduce(self, all_data):
        # Returns all downloaded filepaths in one list
        flattened_filepaths = [filepath for filelist in all_data.values() for filepath in filelist]
        return flattened_filepaths
