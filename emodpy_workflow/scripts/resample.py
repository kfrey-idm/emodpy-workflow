import os

import numpy as np
import pandas as pd

from idmtools_calibra.calib_manager import CalibManager

ROULETTE = 'roulette'
BEST = 'best'
RESAMPLING_METHODS = [ROULETTE, BEST]


class UnknownResampleMethodException(Exception):
    pass


def set_parameterization_ids(samples):
    for index in range(len(samples)):
        samples[index].parameterization_id = index
    return samples


def get_samples_by_likelihood(calibration_dir):
    # obtain samples from the calibration sorted by likelihood
    calib_manager = CalibManager.open_for_reading(calibration_dir)
    parameter_sets = calib_manager.get_parameter_sets_with_likelihoods()
    sorted_parameter_sets = sorted(parameter_sets, key=lambda ps: ps.likelihood_exponentiated, reverse=True)
    return sorted_parameter_sets


def get_samples(args):
    resample_method = args.resample_method.lower()

    sorted_parameter_sets = get_samples_by_likelihood(calibration_dir=args.calibration_dir)
    if len(sorted_parameter_sets) < args.n_samples:
        raise ValueError(f"Insufficient parameter sets: {len(sorted_parameter_sets)} found in specified "
                         f"calibration: {args.calibration_dir} "
                         f"for requested sample count: {args.n_samples}.")

    if resample_method == ROULETTE:
        # determine distribution of top and probabilistically selected samples
        n_top_samples = int(np.ceil(args.n_samples / 3))
        n_roulette_samples = args.n_samples - n_top_samples

        # select the top samples - sorted_parameter_sets is sorted most<->least likely
        top_samples = sorted_parameter_sets[0:n_top_samples]

        # remove selected "top" samples and roulette sample the remaining to prevent duplication
        remaining_sorted_parameter_sets = sorted_parameter_sets[n_top_samples:-1]

        # normalize the parameter set likelihoods for probabilistic selection
        total_likelihood = sum([ps.likelihood_exponentiated for ps in remaining_sorted_parameter_sets])
        p = [ps.likelihood_exponentiated / total_likelihood for ps in remaining_sorted_parameter_sets]

        # probabilistically select the remaining samples - duplicates of top_samples are allowed
        roulette_samples = list(
            np.random.choice(remaining_sorted_parameter_sets, p=p, size=n_roulette_samples, replace=False))

        samples = top_samples + roulette_samples
    elif resample_method == BEST:
        samples = sorted_parameter_sets[0:args.n_samples]
    else:
        raise UnknownResampleMethodException(f'Unknown resample method: {resample_method}')

    # for readable logging purposes
    samples = set_parameterization_ids(samples)

    samples_df = pd.DataFrame(data=[s.to_dict() for s in samples])
    return samples_df


def main(args):
    if os.path.exists(args.output_file):
        raise FileExistsError(f'Specified output file already exists, cannot overwrite: {args.output_file}')

    # select samples as specified
    samples = get_samples(args)

    # write samples file
    os.makedirs(os.path.dirname(os.path.abspath(args.output_file)), exist_ok=True)
    samples.to_csv(args.output_file, index=False)
    print(f'Wrote resampled parameter sets to {args.output_file}')


DEFAULTS = {
    'n_samples': 3,
    'output_file': 'resampled_parameter_sets.csv'
}


def parse_args():
    import argparse

    parser = argparse.ArgumentParser()

    parser.add_argument('-d', '--calib-dir', dest='calibration_dir', type=str, required=True,
                        help='Directory of calibration to resample (containing CalibManager.json).')
    parser.add_argument('-m', '--resample-method', dest='resample_method', type=str, required=True,
                        help='Resampling methodology to use (Required) (Valid: %s)' % ', '.join(RESAMPLING_METHODS))
    parser.add_argument('-n', '--nsamples', dest='n_samples', type=int, default=DEFAULTS['n_samples'],
                        help='Number of resampled parameter sets to generate (Default: %d) ' % DEFAULTS['n_samples'])
    parser.add_argument('-o', '--output-file', dest='output_file', type=str, default=DEFAULTS['output_file'],
                        help='Path of file to write samples to (Default: %s).' % DEFAULTS['output_file'])

    args = parser.parse_args()
    return args


if __name__ == '__main__':
    args = parse_args()
    main(args)
