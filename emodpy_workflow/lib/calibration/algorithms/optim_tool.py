import os

from emodpy_workflow.lib.utils.wrappers import constrain_sample_wrapper

DEFAULTS = {
    'volume_fraction': 0.01,
    'r_squared_threshold': 0.81
}

ALGORITHM_NAME, _ = os.path.splitext(os.path.basename(__file__))


def set_arguments(subparsers, entry_point):
    parser = subparsers.add_parser(ALGORITHM_NAME, help='Use the optim_tool next point algorithm.')
    parser.add_argument('-v', '--volume-fraction',
                        dest='volume_fraction',
                        type=float,
                        default=DEFAULTS['volume_fraction'],
                        help=f"Fraction of parameter space to explore per iteration "
                             f"(Default: {DEFAULTS['volume_fraction']})")
    parser.add_argument('-R', '--rsq-threshold',
                        dest='r_squared_threshold',
                        type=float,
                        default=DEFAULTS['r_squared_threshold'],
                        help=f"Variance threshold above which OptimTool selects next point by linear approximation "
                             f"(Default: {DEFAULTS['r_squared_threshold']})")
    parser.set_defaults(func=entry_point)


def initialize(args, params, frame):
    from idmtools_calibra.algorithms.optim_tool import OptimTool

    parameter_count = len([p for p in params if p['Dynamic']])
    if parameter_count == 0:
        warning_note = \
            "/!\\ WARNING /!\\ OptimTool requires at least one of params with Dynamic set to True. Exiting..."
        print(warning_note)
        exit()

    # Compute hypersphere radius as a function of the number of dynamic parameters
    r = OptimTool.get_r(parameter_count, args.volume_fraction)
    optim_tool = OptimTool(
        params,
        constrain_sample_wrapper(custom_sample_constrainer=frame.custom_sample_constrainer),
        # <-- Will not be saved in iteration state
        mu_r=r,
        # <-- Mean fraction of parameter range for numerical derivative.  Do not go too low with integer parameters
        sigma_r=r / 10.,  # <-- stddev of above radius
        samples_per_iteration=args.n_samples,
        center_repeats=args.n_center_repeats,
        rsquared_thresh=args.r_squared_threshold
        # <-- Linear regression goodness of fit threshold, [0:1].  Above this, regression is used.  Below, use best point. Best to be fairly high.
    )
    return optim_tool
