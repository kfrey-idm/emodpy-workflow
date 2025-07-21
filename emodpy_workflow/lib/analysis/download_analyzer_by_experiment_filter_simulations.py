from typing import List

from idmtools.entities.simulation import Simulation

from emodpy_workflow.lib.analysis.download_analyzer_by_experiment import DownloadAnalyzerByExperiment


class DownloadAnalyzerByExperimentFilterSimulations(DownloadAnalyzerByExperiment):
    """
    This analyzer extends DownloadAnalyzerByExperiment by allowing filtering of results by simulation_ids, which allows
    a more selective set of results to be obtained (rather than all simulations in a given experiment).
    """

    def __init__(self, filenames, simulation_ids: List[str], output_path, use_run_number=True, use_sample_index=True):
        self.simulation_ids = simulation_ids
        super().__init__(filenames=filenames, output_path=output_path,
                         use_run_number=use_run_number, use_sample_index=use_sample_index)

    # process simulations only if they are in the provided list.
    def filter(self, item: Simulation) -> bool:
        selected = str(item.id) in self.simulation_ids
        return selected
