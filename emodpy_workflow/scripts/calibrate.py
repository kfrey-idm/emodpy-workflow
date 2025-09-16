from emodpy_workflow.lib.utils.runtime import load_frame, load_algorithm, available_algorithms

from idmtools.core.platform_factory import Platform

from idmtools_calibra.calib_manager import CalibManager
from idmtools_calibra.plotters.likelihood_plotter import LikelihoodPlotter
from idmtools_calibra.plotters.optim_tool_plotter import OptimToolPlotter


def initialize_calib_manager(task, site, calibration_name, directory,
                             n_replicates, n_iterations, next_point_object, sample_mapping_function):
    calib_manager = CalibManager(
        name=calibration_name,
        directory=directory,
        task=task,
        map_sample_to_model_input_fn=None,  # we already wrap it with SampleIndexWrapper and set manually below
        sites=[site],
        next_point=next_point_object,
        sim_runs_per_param_set=n_replicates,
        max_iterations=n_iterations,
        plotters=[LikelihoodPlotter(), OptimToolPlotter()]  # TODO: add a way for user/model/manifest/something to specify these
    )
    calib_manager.map_sample_to_model_input_fn = sample_mapping_function
    return calib_manager


def main(args):
    # setup model frame binary, task, and inputs builder
    args.frame.initialize_executable()
    task = args.frame.initialize_task()
    inputs_builder = args.frame.inputs_builder(random_run_number=True)

    # setup the selected next point algorithm for use
    next_point_object = args.algorithm_initializer(args=args, params=args.frame.calibration_parameters,
                                                   frame=args.frame)

    calib_manager = initialize_calib_manager(task=task,
                                             site=args.frame.site,
                                             calibration_name=args.calibration_name,
                                             directory=args.output,
                                             n_replicates=args.n_replicates,
                                             n_iterations=args.n_iterations,
                                             next_point_object=next_point_object,
                                             sample_mapping_function=inputs_builder)
    calib_manager.platform = Platform(args.platform, max_running_jobs=1000000, array_batch_size=1000000) # doesn't work for now, num_cores=args.frame.num_cores)

    # if a runtime environment container reference file is specified, make sure the task knows about it
    if args.frame.asset_collection_of_container:
        task.set_sif(path_to_sif=args.frame.asset_collection_of_container, platform=calib_manager.platform)

    calib_manager.run_calibration()


DEFAULTS = {
    'calibration_name': 'testing-only',
    'output': '.',
    'n_iterations': 2,
    'n_replicates': 1,
    'n_samples': 3,
    'n_center_repeats': 2
}


def parse_args():
    import argparse

    parser = argparse.ArgumentParser()

    parser.add_argument('-f', '--frame', dest='frame', type=str, required=True,
                        help=f"Model frame name to calibrate (directory of python input builders). Required.")
    parser.add_argument('-N', '--name', dest='calibration_name', type=str, default=DEFAULTS['calibration_name'],
                        help=f"Name of calibration (Default: {DEFAULTS['calibration_name']})")
    parser.add_argument('-n', '--nsamples', dest='n_samples', type=int, default=DEFAULTS['n_samples'],
                        help=f"Number of samples to run per calibration iteration (Default: {DEFAULTS['n_samples']})")
    parser.add_argument('-r', '--replicates', dest='n_replicates', type=int, default=DEFAULTS['n_replicates'],
                        help=f"Number of replicates to use for parameter samples (Default: {DEFAULTS['n_replicates']})")
    parser.add_argument('-c', '--center-repeats', dest='n_center_repeats', type=int, default=DEFAULTS['n_center_repeats'],
                        help=f"Number of center repeats to run per iteration (Default: {DEFAULTS['n_center_repeats']})")
    parser.add_argument('-i', '--iterations', dest='n_iterations', type=int, default=DEFAULTS['n_iterations'],
                        help=f"Number iterations (in total) to run (Default: {DEFAULTS['n_iterations']})")
    parser.add_argument('-o', '--output', dest='output', type=str, default=DEFAULTS['output'],
                        help=f"Directory to put calibration directory inside of (Default: {DEFAULTS['output']})")
    parser.add_argument('-p', '--platform', dest='platform', type=str, required=True,
                        help=f"Platform to run calibration on (Required).")

    # and now the subparsers for the available next-point algorithms
    subparsers = parser.add_subparsers(dest='selected_algorithm')

    algorithm_modules = {}
    for algorithm_name in available_algorithms():
        mod = load_algorithm(algorithm_name=algorithm_name)
        mod.set_arguments(subparsers, entry_point=main)
        algorithm_modules[algorithm_name] = mod

    # now parse it all
    args = parser.parse_args()
    args.frame = load_frame(frame_name=args.frame)

    # set algorithm initializer
    args.algorithm_initializer = algorithm_modules[args.selected_algorithm].initialize

    return args


if __name__ == "__main__":
    args = parse_args()
    args.func(args=args)
