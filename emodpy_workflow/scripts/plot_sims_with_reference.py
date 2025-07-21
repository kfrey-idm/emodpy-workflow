"""
plot_sims_with_reference.py

This script plots 1+ timeseries figures of simulation data with overlain reference data.

Reference data without provincial stratification should have a 'Province' column with the value 'All'
"""

import math
from pathlib import Path

import matplotlib.pyplot as plt
import operator
import pandas as pd
import re
import sys

from matplotlib import collections as mc
import matplotlib.patches as mpatches
from emodpy_workflow.lib.analysis.age_bin import AgeBin
from emodpy_workflow.lib.analysis.base_distribution import BaseDistribution
from emodpy_workflow.lib.analysis.data_frame_wrapper import DataFrameWrapper
from emodpy_workflow.lib.analysis.population_obs import PopulationObs
from emodpy_workflow.lib.utils.analysis import model_population_in_year
from emodpy_workflow.lib.utils.project_data import parse_ingest_data_from_xlsm
from emodpy_workflow.lib.utils.runtime import load_frame

FIG_HEIGHT = 20
FIG_WIDTH = 10
TICK_SPACING = 3

ALLOWED_GENDERS = {'Male', 'Female', 'Both'}


class Colors:
    male = 'blue'
    female = 'red'
    both = 'black'


class MissingChannelException(Exception):
    pass


def get_gendered_color(gender):
    try:
        color = getattr(Colors, gender.lower())
    except AttributeError:
        raise Exception('Unknown gender for plot color selection: %s' % gender)
    return color


def read_sim_data(fn, node_map):
    sim_df = pd.read_csv(fn).sort_values(by='Year', ascending=True)

    # fix up Node-Province column
    if 'Node' in list(sim_df.columns):
        sim_df = sim_df.set_index('Node').rename(node_map).reset_index().rename(columns={'Node': 'Province'})
    return PopulationObs(dataframe=sim_df)


def make_collection(d, x='Year', y='Result'):
    try:
        zipped_data = zip(d[x], d[y])
    except TypeError:
        zipped_data = zip([d[x]], [d[y]])
    return zipped_data


def scale_to_census(df, pop_df, census_population, census_year, census_min_age, census_max_age, verbose=False):
    model_pop, census_to_model_ratio = model_population_in_year(year=census_year, obs_population=census_population,
                                                                df=pop_df,
                                                                low_age=census_min_age, high_age=census_max_age,
                                                                population_col='Result', verbose=verbose)
    df = df.assign(Result=df['Result'] * census_to_model_ratio)
    return df


def make_and_plot_collection(groups, provinces, figure_dict, channel, **kwargs):
    for group_tuple, data in groups:
        age_bin, province, gender = group_tuple
        if province in [1, '1']:  # kludgy fix for single-node simulations
            continue
        color = get_gendered_color(gender=gender)
        alpha = kwargs.get('alpha', 1.0)
        marker = kwargs.get('marker', '.')
        linewidth = kwargs.get('linewidth', 0.5)

        # Try to obtain the axis to add data to and create it on the fly if it does not exist
        if age_bin in figure_dict:
            fd = figure_dict[age_bin]
        else:
            figure, axis = plt.subplots(max(len(provinces), 2), 1, sharex=True, sharey=True,
                                        figsize=(FIG_WIDTH, FIG_HEIGHT))
            figure_dict[age_bin] = {'figure': figure, 'axis': axis}
            fd = figure_dict[age_bin]

        axis = fd['axis']
        province_index = provinces.index(province)

        # get simulation data and plot it
        if len(data.index) == 1:
            # a single data element
            axis[province_index].plot(data['Year'], data[channel], marker=marker, color=color, alpha=alpha, ms=15)
        else:
            # a line of data
            coll = list(make_collection(data, x='Year', y=channel))
            lc = mc.LineCollection([coll], linewidths=linewidth)
            lc.set_alpha(alpha)
            lc.set_color(color)
            axis[province_index].add_collection(lc)


def make_and_plot_bxp(groups, genders, provinces, figure_dict, channel, lower_channel, upper_channel):
    """
    Make a center-point and whisker plot (subset of a boxplot) for reference data.
    Args:
        groups: dataframe.groupby() result
        genders: list of genders available (needed for subplot identification)
        provinces: list of provinces available (needed for subplot identification)
        figure_dict: dict of figures and axes for plotting on
        channel: data channel name to plot
        lower_channel: data channel name of the lower-bound uncertainty of the central channel
        upper_channel: data channel name of the upper-bound uncertainty of the central channel

    Returns: no return
    """
    for group_tuple, data in groups:
        age_bin, province, gender = group_tuple

        fd = figure_dict[age_bin]
        axis = fd['axis']

        province_index = provinces.index(province)
        bxp_tuples = zip(data[lower_channel], data[channel], data[upper_channel])
        bxp_dicts = [
            {
                'q1': tup[0],  # required but dummy, will turn off
                'q3': tup[0],  # required but dummy, will turn off
                'whislo': tup[0],
                'med': tup[1],
                'whishi': tup[2],
            }
            for tup in bxp_tuples
        ]

        # Depending on gender, draw differently
        gender_index = genders.index(gender)
        gender_offset = TICK_SPACING / 5 if gender_index == 1 else -TICK_SPACING / 5
        positions = [p + gender_offset for p in data['Year']]
        color = get_gendered_color(gender=gender)
        drawing_props = dict(color=color)

        # Draw on the axis
        axis[province_index].bxp(bxpstats=bxp_dicts, showbox=False, showfliers=False, showmeans=False,
                                 positions=positions, medianprops=drawing_props, whiskerprops=drawing_props,
                                 capprops=drawing_props)


def generate_plot(reference, sim_filenames, pop_filenames, node_map, channel, census_population, census_year,
                  census_min_age, census_max_age, scaling, distribution, selected_genders,
                  start_year=None, end_year=None, verbose=False):
    # two-tailed two sigma error bars, p = 0.02275 and 0.97725 applied regardless of distribution
    p_low = (1 - 0.9545) / 2
    p_high = 1 - p_low

    p_low_channel = reference.add_percentile_values(channel=channel, distribution=distribution, p=p_low)[0]
    p_high_channel = reference.add_percentile_values(channel=channel, distribution=distribution, p=p_high)[0]

    # data always has provinces now; even if just the 'All' province
    reference_provinces = reference.get_provinces()
    for province in reference_provinces:
        if isinstance(province, str):
            continue
        if math.isnan(province):
            raise DataFrameWrapper.MissingRequiredData('')

    allowed_genders = set.intersection(ALLOWED_GENDERS, set(selected_genders))
    genders = [gender for gender in reference.get_genders() if gender in allowed_genders]

    # the rest of this method expects reference to be a multi-indexed DataFrame
    reference = reference._dataframe

    # population scaling for sim data, T/F
    if scaling:
        age_bin = AgeBin(start=census_min_age, end=census_max_age)
        print('-- Will perform scaling of channel: %s sim data to census population, age bin: %s.' % (channel, age_bin))
    else:
        print('-- No population scaling will be performed for channel: %s' % channel)

    # determine time bounds for plotted data
    time_conditions = []
    if start_year:
        time_conditions.append(['Year', operator.ge, start_year])
    if end_year:
        time_conditions.append(['Year', operator.le, end_year])

    # used for to group data for plotting
    multi_index = ['AgeBin', 'Province', 'Gender']

    n_sims = len(sim_filenames)
    n = 1
    figure_dict = {}
    all_years = set()  # we will use this for setting year ticks
    missing_files = 0
    for i in range(len(sim_filenames)):
        fn = sim_filenames[i]

        if verbose:
            print('Processing sim file %d/%d ...' % (n, n_sims))
            sys.stdout.flush()
        try:
            results = read_sim_data(fn, node_map=node_map).filter(conditions=time_conditions)
        except FileNotFoundError:
            print(f'File missing, post processing may have failed or is in-process for a sim: {fn}')
            missing_files += 1
            continue
        all_years = all_years.union(set(results.get_years()))
        results = results._dataframe

        # scale Results to census data
        if scaling:
            pop_filename = pop_filenames[i]
            pop = read_sim_data(pop_filename, node_map=node_map)._dataframe
            results = scale_to_census(results, pop, census_population, census_year, census_min_age, census_max_age,
                                      verbose=verbose)

        # determine the union of sim and reference provinces (their intersection can be empty, all, or between)
        sim_provinces = results['Province'].unique()  # ck4, define
        provinces = list(set(reference_provinces).union(set(sim_provinces)))

        # putting aggregated node at the end (RHS) of all plots
        if PopulationObs.AGGREGATED_PROVINCE in provinces:
            provinces.remove(PopulationObs.AGGREGATED_PROVINCE)
        provinces.append(PopulationObs.AGGREGATED_PROVINCE)

        groups = results[results['Gender'].isin(genders)].groupby(multi_index)
        make_and_plot_collection(groups=groups, provinces=provinces,
                                 channel='Result', figure_dict=figure_dict,
                                 alpha=0.1, linewidth=0.5, marker='.')
        n += 1

    if missing_files > 0:
        print(f'{missing_files} missing files detected, continuing with the data successfully retrieved...')

    # independent/year axis ticks
    ticks_start = math.ceil(min(all_years) / TICK_SPACING) * TICK_SPACING
    ticks_end = math.ceil(
        (max(all_years) + 1e-3) / TICK_SPACING) * TICK_SPACING  # one too far, but the range fixes this
    ticks = list(range(ticks_start, ticks_end, TICK_SPACING))

    # reference data point-and-whisker plots
    print('Plotting reference data...')
    groups = reference[reference['Gender'].isin(genders)].groupby(multi_index)
    make_and_plot_bxp(groups=groups, genders=genders, provinces=provinces,
                      channel=channel, lower_channel=p_low_channel, upper_channel=p_high_channel,
                      figure_dict=figure_dict)

    # finalize figures
    print('Finalizing figures...')
    sys.stdout.flush()
    for age_bin, fd in figure_dict.items():
        # set axis ticks & labels and make the plot pretty
        axis = fd['axis']
        for province_index in range(len(provinces)):
            axis[province_index].set_ylim(bottom=0)  # bottom of the plot should be 0
            axis[province_index].set_xticks(ticks)
            axis[province_index].set_xticklabels(ticks, rotation=75)

            if province_index == 0:
                axis[province_index].set_title('%s %s' % (channel, age_bin), fontsize=12)
            axis[province_index].set_ylabel('%s' % provinces[province_index].replace(' ', '\n'), fontsize=8)

            if province_index == len(provinces) - 1:
                axis[province_index].set_xlabel('Year')
                patches = {
                    'Female': mpatches.Patch(color=Colors.female, label='Female'),
                    'Male': mpatches.Patch(color=Colors.male, label='Male'),
                    'Both': mpatches.Patch(color=Colors.both, label='Both')
                }
                patches = [patch for gender, patch in patches.items() if gender in genders]
                axis[province_index].legend(handles=patches, loc='upper right')

        figure = fd['figure']
        figure.savefig('%s/%s_%s.png' % (args.output_dir, channel, age_bin.replace(':', '-')), bbox_inches='tight')


def detect_uncertainty_channel(dfw, channel):
    # the uncertainty channel should be the only channel that is not a stratifier or 'weight' or the channel itself
    df = dfw._dataframe.dropna(subset=[channel.name])
    df = df.dropna(axis='columns')
    possible_channels = list(set(df.columns) - set(dfw.stratifiers) - set([channel.name, dfw.WEIGHT_CHANNEL]))
    if len(possible_channels) != 1:
        raise Exception('Cannot determine the uncertainty channel. Possibilities: %s' % possible_channels)
    return possible_channels[0]


def main(args):
    validate_args(args=args)
    plt.tight_layout()

    # get reference data and site info from ingest form
    params, site_info, reference, analyzers, channels = parse_ingest_data_from_xlsm(filename=args.frame.ingest_form_path)

    obs_data_channels_by_name = {channel.name for channel in channels}
    analyzer_channels_by_name = {analyzer['channel'] for analyzer in analyzers}
    valid_channel_names = obs_data_channels_by_name.union(analyzer_channels_by_name)
    if args.channel not in valid_channel_names:
        valid_str = ', '.join(valid_channel_names)
        raise MissingChannelException(f"\nChannel: {args.channel} is invalid.\n"
                                      f"Channels must have an Obs sheet and 1+ associated analyzer(s) to be valid.\n"
                                      f"Current valid channels in current frame ingest form: {valid_str}")
    # now grab the verified user-selected channel for use
    channel = {channel.name: channel for channel in channels}[args.channel]

    # obtain output data file to get plotting data from
    output_file_root = Path('output', 'post_process')

    output_filename = f"{args.channel}.csv"
    output_file_paths = [Path(output_file_root, output_filename)]

    uncertainty_channel = detect_uncertainty_channel(dfw=reference, channel=channel)
    reference = reference.filter(keep_only=[args.channel, uncertainty_channel])

    distribution = BaseDistribution.from_uncertainty_channel(uncertainty_channel=uncertainty_channel)
    distribution.prepare(dfw=reference, channel=args.channel)

    # add in Population for computing the pop scaling factor
    if channel.needs_pop_scaling:
        print('Pop scaling will occur')
        output_file_paths.append(Path(output_file_root, 'Population.csv'))
        output_file_paths = list(set(output_file_paths))  # just in case the channel IS Population, no need to download twice
    else:
        print('Pop scaling will NOT occur')

    # Download the requisite files using the download script
    from argparse import Namespace
    from emodpy_workflow.scripts.download import main as download
    dl_args = {
        'files': [str(p) for p in output_file_paths],
        'platform': args.platform,
        'output_dir': args.output_dir,
        'receipt_file': None,
        'samples_file': None,
        'suite_id': None,
        'experiment_id': None
    }
    # pass information regarding the selected plot mode to downloader to get the right information
    if args.samples_file is not None:
        dl_args['samples_file'] = args.samples_file
    elif args.experiment_id is not None:
        dl_args['experiment_id'] = args.experiment_id
    dl_args = Namespace(**dl_args)
    downloaded_filepaths = download(args=dl_args)

    # identify the selected channel and (if downloaded) Population data files
    regex = re.compile(f"^{channel.name}.*\.csv$")
    result_filenames = sorted([fn for fn in downloaded_filepaths if regex.match(Path(fn).name)])
    regex = re.compile(f"^Population.*\.csv$")
    population_filenames = sorted([fn for fn in downloaded_filepaths if regex.match(Path(fn).name)])
    if len(result_filenames) == 0:
        raise Exception(f"No simulation files were downloaded. Is the provided samples file empty?: "
                        f"{args.samples_file}")

    # paranoid checks: if we are scaling, ensure that the sort order above has properly aligned the two lists of files
    if channel.needs_pop_scaling:
        if len(result_filenames) != len(population_filenames):
            raise Exception(f"Failed to obtain 1-1 counts of channel: {args.channel} and Population files for scaling.")
        for i, res_fn in enumerate(result_filenames):
            res_path = Path(res_fn).absolute()
            pop_path = Path(population_filenames[i]).absolute()

            res_exp_id = res_path.parent.parent.name
            pop_exp_id = pop_path.parent.parent.name
            if res_exp_id != pop_exp_id:
                raise Exception(f"Failed to properly align channel: {args.channel} and Population files (experiment id check).")

            res_name_parts = res_path.name.split('_')[1:]
            pop_name_parts = pop_path.name.split('_')[1:]
            if res_name_parts != pop_name_parts:
                raise Exception(f"Failed to properly align channel: {args.channel} and Population files (filename check)")

    min_age = site_info['census_age_bin'].start
    max_age = site_info['census_age_bin'].end
    node_map = site_info['node_map']
    # add the non-aggregated node to the node map
    node_map[PopulationObs.AGGREGATED_NODE] = PopulationObs.AGGREGATED_PROVINCE

    generate_plot(reference, result_filenames, population_filenames, node_map=node_map, channel=args.channel,
                  census_population=site_info['census_population'], census_year=site_info['census_year'],
                  census_min_age=min_age, census_max_age=max_age, scaling=channel.needs_pop_scaling,
                  distribution=distribution, start_year=args.start_year, end_year=args.end_year, verbose=args.verbose,
                  selected_genders=args.genders)
    plt.show()


DEFAULTS = {
    'genders': ','.join(ALLOWED_GENDERS),
    'output_dir': 'plot_sims_with_reference_output',
    'experiment_id': None,
    'samples_file': None,
    'start_year': None,
    'end_year': None
}


def parse_args():
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument('-F', '--frame', dest='frame', type=str, required=True,
                        help=f"Model frame name to calibration referenced data from. Required.")
    parser.add_argument('-s', '--samples', dest='samples_file', type=str, # default=DEFAULTS['samples_file'],
                        help='Resampled parameter sets csv file of simulations to plot '
                             '(Mutually exclusive with --exp-id).')
    parser.add_argument('--exp-id', dest='experiment_id', type=str, default=DEFAULTS['experiment_id'],
                        help='Experiment id from which to gather simulations for plotting '
                             '(Mutually exclusive with -s).')
    parser.add_argument('-c', '--channel', dest='channel', type=str, required=True,
                        help='Data channel with ingest form obs data and associated analyzer(s) to plot (Required).')
    parser.add_argument('-g', '--genders', dest='genders', type=str, default=DEFAULTS['genders'],
                        help=f"Comma-separated list of gender(s) to plot (Default: {DEFAULTS['genders']}). "
                             f"Available genders: {', '.join(ALLOWED_GENDERS)}")
    parser.add_argument('-o', '--output-dir', dest='output_dir', default=DEFAULTS['output_dir'],
                        help=f"Directory to download simulation data and write plotting images to (Default: {DEFAULTS['output_dir']}).")
    parser.add_argument('-p', '--platform', dest='platform', type=str, required=True,
                        help=f"Platform to obtain simulation data from (Required).")
    parser.add_argument('--start_year', dest='start_year', type=float, default=DEFAULTS['start_year'],
                        help='Plot data starting at this inclusive year (Default: beginning of all data).')
    parser.add_argument('--end_year', dest='end_year', type=float, default=DEFAULTS['end_year'],
                        help='Plot data through this inclusive year (Default: end of all data).')
    parser.add_argument('-v', '--verbose', dest='verbose', action='store_true',
                        help='Print more information during processing.')

    # now parse it all
    args = parser.parse_args()
    args.frame = load_frame(frame_name=args.frame)
    args.genders = args.genders.strip().split(',')
    return args


def validate_args(args):
    if not ((args.experiment_id is not None) ^ (args.samples_file is not None)):
        raise Exception(f"Must provide an experiment_id (--exp-id) or a samples file (-s) but not both.")


if __name__ == '__main__':
    args = parse_args()
    main(args=args)
