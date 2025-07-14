import os

import pandas as pd

from emodpy_workflow.lib.utils.runtime import load_frame

from idmtools.builders.simulation_builder import SimulationBuilder
from idmtools.core.platform_factory import Platform
from idmtools.entities import Suite
from idmtools.entities.experiment import Experiment
from idmtools.entities.templated_simulation import TemplatedSimulations

from idmtools_calibra.utilities.mod_fn import ModFn
from idmtools_calibra.utilities.parameter_set import ParameterSet, NaNDetectedError


DOLPHIN = '''
                                  _
                             _.-~~.)
       _.--~~~~~---....__  .' . .,' 
     ,'. . . . . . . . . .~- ._ (
    ( .. .g. . . . . . . . . . .~-._
 .~__.-~    ~`. . . . . . . . . . . -. 
 `----..._      ~-=~~-. . . . . . . . ~-.  
           ~-._   `-._ ~=_~~--. . . . . .~.  
            | .~-.._  ~--._-.    ~-. . . . ~-.
             \ .(   ~~--.._~'       `. . . . .~-.                ,
              `._\         ~~--.._    `. . . . . ~-.    .- .   ,'/
 . _ . -~\        _ ..  _          ~~--.`_. . . . . ~-_     ,-','`  .
           ` ._           ~                ~--. . . . .~=.-'. /. `
     - . -~            -. _ . - ~ - _   - ~     ~--..__~ _,. /   \  -
             . __ ..                   ~-               ~~_. (  `
  _ _               `-       ..  - .    . - ~ ~ .    \    ~-` ` `  `.
                                               - .  `  .   \  \ `. 
'''


def build_scenario_experiment(platform, samples, experiment_name, frame, suite_id, sample_overrides=None):
    sample_overrides = {} if sample_overrides is None else sample_overrides

    # create our base task
    task = frame.initialize_task()
    inputs_builder = frame.inputs_builder(random_run_number=False)

    # now for each sample, make a simulation that uses task and the sample_mapping_function
    # TODO: test out the use of these kwargs, they SHOULD be being passed to SampleIndexWrapper objects, if I've traced the code correctly (confusing!)
    sweeps = [[ModFn(inputs_builder, idx=index, sample={**sample, **sample_overrides})
               for index, sample in enumerate(samples)]]
    builder = SimulationBuilder()
    builder.sweeps = sweeps
    builder.count = len(sweeps[0])

    # if a runtime environment container reference file is specified, make sure the task knows about it
    if frame.asset_collection_of_container:
        task.set_sif(path_to_sif=frame.asset_collection_of_container, platform=platform)

    experiment = Experiment(name=experiment_name,
                            simulations=TemplatedSimulations(base_task=task, builders={builder}), parent_id=suite_id)
    # doesn't work for now platform.num_cores = frame.num_cores  # TODO: this does set per-exp num_cores in comps (min/max cores is this) BUT it also does it on the sim config (breaks!)
    platform.create_items(experiment)
    return experiment


def get_samples(samples_file):
    if samples_file is None:
        samples = [{}]  # so we have one dummy sample (no sample overrides)
    else:
        # we need the original sample parameter set plus the run number (for reproducibility/comparability)
        samples_df = pd.read_csv(samples_file)
        try:
            samples = [ParameterSet.from_dict(d) for d in samples_df.to_dict(orient='records')]
        except NaNDetectedError as e:
            e.args = (f"One or more blank entries or lines found in samples file {args.samples_file} . "
                      f"Please fix/remove them. Enjoy this dolphin.\n{DOLPHIN}",)
            raise e

        for sample in samples:
            sample.param_dict['Run_Number'] = sample.run_number
        samples = [sample.param_dict for sample in samples]
    return samples


def make_a_suite(platform, suite_name):
    suite = Suite(name=suite_name)
    platform.create_items(suite)
    return suite


def write_receipt(receipt, receipt_path):
    df = pd.DataFrame(receipt)
    df.index.name = 'index'
    os.makedirs(os.path.dirname(os.path.abspath(receipt_path)), exist_ok=True)
    df.to_csv(receipt_path)
    print(f'Wrote {os.path.basename(__file__)} receipt to: {receipt_path}')


def main(args):
    # For consistency, we don't want to accidentally mix-and-match receipts and prior processed results.
    receipt_path = os.path.join(args.output_dir, 'experiment_index.csv')
    if os.path.exists(receipt_path):
        raise Exception(f'{os.path.basename(__file__)} receipt already exists at: {receipt_path} . '
                        f'Please delete it and related downloads and processed files or pick a different '
                        f'output directory.')

    # TODO: num_cores > 1 seems to be BUSTED
    platform = Platform(args.platform, max_running_jobs=1000000, array_batch_size=1000000)  # We will set num_cores on a per-experiment basis

    # load model frame python modules
    frames = {frame_name: load_frame(frame_name=frame_name) for frame_name in args.frames}

    # now determine the samples to use as overrides to the frames
    samples = get_samples(samples_file=args.samples_file)

    # Now generate and run one simulation per sample in each experiment
    # The number of experiments is one per sweep entry (if provided) or one per frame (default with no sweeping)
    suite = make_a_suite(platform=platform, suite_name=args.suite_name)
    experiments = []
    receipt = []
    for frame_name, frame in frames.items():
        frame.initialize_executable()
        for overrides in args.sweep_parameter_sets[frame_name]['sweeps']:
            # experiment_name:
            #  if not using a sweeps.py file, then it is the suite_name
            #  otherwise if 'experiment_name' is not in the overrides dict for a sweeps row, use the frame_name
            experiment_name = overrides.pop('experiment_name', frame_name) if args.doing_sweeps else args.suite_name
            experiment = build_scenario_experiment(platform=platform,
                                                   samples=samples,
                                                   experiment_name=experiment_name,
                                                   frame=frame,
                                                   suite_id=suite.id,
                                                   sample_overrides=overrides)
            experiments.append(experiment)

            # generate the receipt data for this experiment
            frame_and_experiment_info = {
                'frame': frame_name,
                'experiment_id': experiment.id,
                'experiment_name': experiment_name
            }
            # add the experiment directory to the receipt if it exists on the platform
            try:
                exp_directory = platform.get_directory(item=experiment)
                frame_and_experiment_info['experiment_directory'] = exp_directory
            except AttributeError:
                pass
            receipt.append({**frame_and_experiment_info, **overrides})

    # Necessary only due to idmtools bug, e.g.,
    # https://github.com/InstituteforDiseaseModeling/idmtools/issues/1653
    suite.experiments.extend(experiments)

    platform.run_items(experiments)
    write_receipt(receipt=receipt, receipt_path=receipt_path)

    print('Done with model experiment creation.')
    if args.download_filenames:
        from argparse import Namespace
        from emodpy_workflow.scripts.download import main as download
        platform.wait_till_done(item=suite)
        dl_args = Namespace(**{'files': args.download_filenames, 'receipt_file': receipt_path,
                               'platform': platform._config_block})
        download(args=dl_args)


DEFAULTS = {
}


def parse_args():
    import argparse
    parser = argparse.ArgumentParser()

    parser.add_argument('-s', '--samples', dest='samples_file', type=str, default=None,
                        help='csv file with base samples to use for simulation generation. Runs one sim per '
                             'frame with configs as-is if not provided.')
    parser.add_argument('-N', '--suite-name', dest='suite_name', type=str, required=True,
                        help='Name of suite for experiments to be run within (Required).')
    parser.add_argument('-F', '--frames', dest='frames', type=str, required=True,
                        help='Comma-separated list of model frames to run (Required).')
    parser.add_argument('-f', '--files', dest='download_filenames', type=str, default=None,
                        help='Filenames to download from scenario simulations. '
                             'Paths relative to simulation directories. Comma-separated list if more than one '
                             '(Default: do not download files)')
    parser.add_argument('-o', '--output-dir', dest='output_dir', type=str, required=True,
                        help='Directory to write receipt to (always) and scenario output files '
                             '(if downloading).')
    parser.add_argument('-p', '--platform', dest='platform', type=str, required=True,
                        help=f"Platform to run simulations on (Required).")
    parser.add_argument('-S', '--sweep', dest='sweep', type=str, default=None,
                        help='Python module to load with a sweep definition to generate extra experiments with '
                             '(Default: no sweeping).')

    args = parser.parse_args()
    args.frames = set(args.frames.strip().split(','))
    if args.sweep is None:
        # This means there are no swept value overrides
        args.sweep_parameter_sets = {frame_name: {'sweeps': [{}]} for frame_name in args.frames}
        args.doing_sweeps = False  # used later for figuring out how to name experiments
    else:
        import importlib.util
        spec = importlib.util.spec_from_file_location('user_sweep', args.sweep)
        mod = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(mod)
        args.sweep_parameter_sets = mod.parameter_sets

        # ensure every requested model frame has a sweeps entry
        missing_entries = [frame for frame in args.frames if frame not in args.sweep_parameter_sets.keys()]
        if len(missing_entries) > 0:
            text = ', '.join(missing_entries)
            raise KeyError(f'One or more requested model frames are missing sweep entries: {text}')
        args.doing_sweeps = True  # used later for figuring out how to name experiments
    if args.download_filenames:
        args.download_filenames = args.download_filenames.strip().split(',')
    return args


if __name__ == '__main__':
    args = parse_args()
    main(args)
