import os
import pandas as pd

from emodpy_workflow.lib.analysis.download_analyzer_by_experiment import DownloadAnalyzerByExperiment


class DownloadAnalyzerByExperimentReceipt(DownloadAnalyzerByExperiment):
    """
    This analyzer is based on the DownloadAnalyzer and allows the download of files based on a Index and Repetition tags
    """

    def __init__(self, filenames, receipt_file, use_run_number=True, use_sample_index=True):
        self.receipt = pd.read_csv(receipt_file, index_col='index')
        output_path = os.path.dirname(os.path.abspath(receipt_file))
        super().__init__(filenames=filenames, output_path=output_path,
                         use_run_number=use_run_number, use_sample_index=use_sample_index)

    @staticmethod
    def _directory_name(experiment_name, sample_index):
        return f'{experiment_name}--{sample_index}'

    def _directory_for_experiment(self, experiment_id):
        receipt_row = self.receipt[self.receipt['experiment_id'] == experiment_id]
        return os.path.join(self.output_path, self._directory_name(
            experiment_name=receipt_row.experiment_name.values[0],
            sample_index=receipt_row.index.values[0]))
