import os
import pandas as pd

from emodpy_workflow.lib.analysis.download_analyzer_by_experiment import DownloadAnalyzerByExperiment
from emodpy_workflow.lib.analysis.download_analyzer_by_experiment_filter_simulations import \
    DownloadAnalyzerByExperimentFilterSimulations
from emodpy_workflow.lib.analysis.download_analyzer_by_experiment_receipt import DownloadAnalyzerByExperimentReceipt

from idmtools.analysis.analyze_manager import AnalyzeManager
from idmtools.core import ItemType
from idmtools.core.platform_factory import Platform


def download_experiments(analyzer, experiment_ids, platform):
    am = AnalyzeManager(ids=[(exp_id, ItemType.EXPERIMENT) for exp_id in experiment_ids],
                        analyzers=[analyzer],
                        verbose=False,
                        platform=platform)
    am.analyze()
    return analyzer.results  # downloaded file list


def main(args):
    validate_args(args)
    platform = Platform(args.platform)
    if args.receipt_file:
        # using a receipt file to identify experiments to download
        receipt = pd.read_csv(args.receipt_file, index_col='index')
        experiment_ids = receipt['experiment_id'].unique()
        experiments = [platform.get_item(item_id=experiment_id, item_type=ItemType.EXPERIMENT)
                       for experiment_id in experiment_ids]
        analyzer = DownloadAnalyzerByExperimentReceipt(filenames=args.files, receipt_file=args.receipt_file)
    elif args.suite_id:
        # using a suite id to identify experiments for download
        experiments = platform.get_children(item_id=args.suite_id, item_type=ItemType.SUITE)
        experiment_ids = [experiment.id for experiment in experiments]
        analyzer = DownloadAnalyzerByExperiment(filenames=args.files, output_path=args.output_dir)
    elif args.experiment_id:
        # using an experiment id to identify a single experiment for download
        experiments = [platform.get_item(item_id=args.experiment_id, item_type=ItemType.EXPERIMENT)]
        experiment_ids = [experiment.id for experiment in experiments]
        analyzer = DownloadAnalyzerByExperiment(filenames=args.files, output_path=args.output_dir)
    else:
        # using a samples file to identify specific simulations (in experiments) to download (not full experiments)
        samples_df = pd.read_csv(args.samples_file)
        experiment_ids = {platform.get_parent(item_id=sim_id, item_type=ItemType.SIMULATION).id for sim_id in
                          samples_df['sim_id']}
        experiments = [platform.get_item(item_id=experiment_id, item_type=ItemType.EXPERIMENT)
                       for experiment_id in experiment_ids]
        analyzer = DownloadAnalyzerByExperimentFilterSimulations(filenames=args.files,
                                                                 simulation_ids=list(samples_df['sim_id']),
                                                                 output_path=args.output_dir)

    for experiment in experiments:
        platform.wait_till_done(item=experiment)
    downloaded_filepaths = download_experiments(analyzer=analyzer, experiment_ids=experiment_ids, platform=platform)
    print(f'Done downloading files to: {analyzer.output_path}')
    return downloaded_filepaths


DEFAULTS = {
    'files': os.path.join('output', 'ReportHIVByAgeAndGender.csv'),
    'receipt_file': None,
    'samples_file': None,
    'suite_id': None,
    'experiment_id': None,
    'output_dir': None
}


usage_str = 'Either set -r OR (--suite-id and -o) OR (--exp-id and -o) OR (-s and -o)'


def parse_args():
    import argparse
    parser = argparse.ArgumentParser()

    parser.add_argument('-d', '--files', dest='files', type=str, default=DEFAULTS['files'],
                        help=f"Comma-separated list of simulation directory relative file paths to download "
                             f"(Default: {DEFAULTS['files']})")

    parser.add_argument('-r', '--receipt', dest='receipt_file', type=str, default=DEFAULTS['receipt_file'],
                        help=f'Commissioning receipt file path. {usage_str}.')
    parser.add_argument('-s', '--samples', dest='samples_file', type=str, default=DEFAULTS['samples_file'],
                        help=f"Resampled parameter sets csv file of simulations to plot. {usage_str}.")
    parser.add_argument('--suite-id', dest='suite_id', type=str, default=DEFAULTS['suite_id'],
                        help=f'Id of suite to download simulations from. {usage_str}.')
    parser.add_argument('--exp-id', dest='experiment_id', type=str, default=DEFAULTS['experiment_id'],
                        help=f'Id of experiment to download simulations from. {usage_str}.')

    parser.add_argument('-o', '--output-dir', dest='output_dir', type=str, default=DEFAULTS['output_dir'],
                        help=f'Directory to write output into. {usage_str}.')
    parser.add_argument('-p', '--platform', dest='platform', type=str, required=True,
                        help=f"Platform to download from (Required).")

    args = parser.parse_args()
    args.files = args.files.strip().split(',')
    return args


def validate_args(args):
    # arg validation
    modes_selected = 0
    if args.receipt_file:
        # using a receipt file for experiment/simulation identification
        if args.suite_id or args.experiment_id or args.samples_file or args.output_dir:
            raise ValueError(usage_str)
        args.output_dir = os.path.dirname(os.path.abspath(args.receipt_file))
        modes_selected += 1

    if args.samples_file:
        # using a samples file for simulation identification
        if not args.output_dir:
            raise ValueError(usage_str)
        modes_selected += 1

    if args.suite_id:
        # using a suite id for experiment/simulation identification
        if not args.output_dir:
            raise ValueError(usage_str)
        modes_selected += 1

    if args.experiment_id:
        # using an experiment id for experiment/simulation identification
        if not args.output_dir:
            raise ValueError(usage_str)
        modes_selected += 1

    if modes_selected != 1:
        raise ValueError(usage_str)


if __name__ == '__main__':
    args = parse_args()
    main(args)
