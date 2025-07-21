import importlib
import json
import os
import random
import shutil
import sys
from collections import Counter
from pathlib import Path
from types import ModuleType
from typing import List, Callable, Iterable, Dict

from emodpy_workflow.lib.analysis.age_bin import AgeBin
from emodpy_workflow import scripts as standard_scripts
from emodpy_workflow.lib.analysis.channel import Channel
from emodpy_workflow.lib.analysis.population_obs import PopulationObs

from idmtools.assets import Asset
from idmtools.entities.itask import ITask
from idmtools.entities.simulation import Simulation

from emodpy_workflow.lib.utils.access_counting_dict import AccessCountingDict


class FrameExistsError(Exception):
    pass


class FrameDoesNotExistError(Exception):
    pass


class UnusedParameterException(Exception):
    pass


def add_post_channel_config_as_asset(task: ITask, channels: List[Channel], reference_data: PopulationObs,
                                     site_info: dict) -> None:
    """
    Construct a post_channel_config.json file to configure the EMOD post-processor for HIV analyzer input and ensure it
    is added to Task assets

    Args:
        task: Task object to add file as an asset to
        channels: list of Channels, model data channels to post-process
        reference_data: reference data from an ingest form for determining which provinces/ages/etc to post-process
            model results at.
        site_info: information related to scaling of simulations back to reference population

    Returns: None
    """
    channel_config = {channel.name: {} for channel in channels}

    # census_year is expected to be an integer year, as specified from an ingest form. We adjust to half-year to
    # compare to an approximate "year average" or "mid-year" population in EMOD.
    census_year = site_info['census_year'] + 0.5
    census_age_bin = site_info['census_age_bin']

    # construct channel config
    for channel in channels:
        is_population = channel.name == 'Population'

        # filter by channel
        channel_df = reference_data.filter(keep_only=channel.name)

        channel_config[channel.name]["Type"] = channel.type

        # include population scaling year for Population channel, only
        years = list(channel_df.get_years())
        if is_population and census_year not in years:
            years.append(census_year)
        channel_config[channel.name]["Year"] = sorted(years)

        channel_config[channel.name]["Gender"] = channel_df.get_genders()

        # include population scaling age bin for Population channel, only
        age_bins = [AgeBin.from_string(age_bin_str) for age_bin_str in channel_df.get_age_bins()]
        if is_population and census_age_bin not in age_bins:
            age_bins.append(census_age_bin)
        age_bins = sorted(age_bins, key=lambda age_bin: age_bin.start)
        age_bins = [age_bin.to_tuple() for age_bin in age_bins]
        channel_config[channel.name]["AgeBin"] = age_bins

    # add file to config_builder (as an asset file)
    asset = Asset(filename='post_channel_config.json', content=json.dumps(channel_config, sort_keys=True))
    task.common_assets.add_asset(asset, fail_on_duplicate=False)


def compute_num_cores(max_memory_mb: int) -> int:
    """
    Computes the number of cores to request for a simulation based on an assumption of one core per 8GB of requested
    memory for EMOD.
    Args:
        max_memory_mb: simulation max memory, in MB

    Returns: number of cores to request
    """
    from math import ceil
    return ceil(max_memory_mb/8000)


def get_embedded_python_paths(pre_processing_path: str = None, in_processing_path: str = None,
                             post_processing_path: str = None) -> List[str]:
    """
    Adds EMOD python pre/in/post-processing file(s) to the given task as assets and makes sure embedded python
    is turned off if none are given (it currently defaults to on).

    Args:
        pre_processing_path: Defines the pre-processor to use. If 'standard', use the in-code standard processor,
            if a path, the path to a custom pre-processor, including the filename, if None, no pre-processor will be used.
        in_processing_path: Defines the in-processor to use. If 'standard', use the in-code standard processor,
            if a path, the path to a custom in-processor, including the filename, if None, no in-processor will be used.
        post_processing_path: Defines the post-processor to use. If 'standard', use the in-code standard processor,
            if a path, the path to a custom post-processor, including the filename, if None, no post-processor will be used.

    Returns:
        List of paths to the python files, including the filename, to be used as embedded python scripts
    """
    standard_dir = standard_scripts.__path__[0]
    paths = []

    def validate_and_append_path(given_path, keyword, filename):
        if given_path is not None:
            if isinstance(given_path, str) and given_path.lower() == 'standard':
                paths.append(os.path.join(standard_dir, filename))
            else:
                path_obj = Path(given_path)
                if path_obj.name == filename:
                    paths.append(str(path_obj))
                else:
                    raise ValueError(f"Invalid {keyword} path: {given_path}, please make sure the path includes "
                                     f"the filename '{filename}' or is the keyword 'standard'.")

    validate_and_append_path(pre_processing_path, 'pre-processing', 'dtk_pre_process.py')
    validate_and_append_path(in_processing_path, 'in-processing', 'dtk_in_process.py')
    validate_and_append_path(post_processing_path, 'post-processing', 'dtk_post_process.py')

    return paths


def map_sample_to_model_input(simulation: Simulation, sample: dict, config_builder: Callable = None,
                              campaign_builder: Callable = None, demographics_builder: Callable = None,
                              random_run_number: bool = True, verbose: bool = True) -> dict:
    """
    This method builds config, campaign, and/or demographics objects and sets them on the provide simulation object.
    It consumes a sample, which is a dict of parameter key/values that are used as overrides to the default behavior
    of the provided builders.

    Args:
        simulation: simulation object to add built config/campaign/demographics objects to
        sample: dict of parameter names/values overrides to use during config/campaign/demographics building
        config_builder: reference to a function that builds an EMOD config object. None means do not build a config
            object.
        campaign_builder: reference to a function that builds an EMOD campaign object. None means do not build a
            campaign object.
        demographics_builder: reference to a function that builds an EMOD demographics object. None means do not build
            a demographics object.
        random_run_number: if True, run numbers will be randomly assigned, otherwise any pre-existing run number will
            be used
        verbose: if True, print out information about the sample and its usage

    Returns: a dict of simulation tag names/values
    """
    run_number_key = 'Run_Number'
    tags = {}
    tags.update(sample)

    # we now create a copy of the passed in samples dict, but using an AccessCountingDict to keep track of the number of
    #  times each key is accessed (checking for never-used or multiple-used parameters for user to be aware of)
    sample = AccessCountingDict.from_dict(d=sample)

    # Consume config parameters, both in-config parameters and project-defined ones (in builder function calls).
    if config_builder:
        simulation.task.config = config_builder(params=sample)
        # must always specify run number in the tags if a config is built (production run)
        tags.update({run_number_key: simulation.task.config.parameters.Run_Number})

    # Now consume parameters that go to the campaign
    if campaign_builder:
        # create_campaign_from_callback will expect to self-initialize a blank campaign with schema_path set, THEN it
        #  will pass that initialized blank campaign to this buiilder. So we're setting up for it's behavior here.
        def builder_with_params():
            return campaign_builder(params=sample)
        simulation.task.create_campaign_from_callback(builder=builder_with_params, bootstrapped=True)

    # Now consume parameters that go to the demographics. We sneak in getting a list of returned callables to be applied
    # to the config (for demographics/config consistency/compatibility)
    if demographics_builder:
        def builder_with_params():
            return demographics_builder(params=sample)
        simulation.task.create_demographics_from_callback(builder=builder_with_params, from_sweep=True)

    # Run number is a special case sometimes, so we handle it explicitly here AFTER building the config
    if random_run_number:
        # do not apply any provided run number in this case
        random_seed = random.randint(0, 65535)
        tags.update(simulation.task.set_parameter(run_number_key, random_seed))

    # finally, handle any implicit configuration settings
    simulation.task.handle_implicit_configs()

    if verbose:
        print('>'*80)
        print(f"Total parameter access counts:\n{sample.access_count}")
        # print(f"Sample: {sample}")
    for k in sample.keys():
        access_count = sample.access_count_for_key(k=k)
        if access_count > 1:
            print(f"WARNING: parameter: {k} was accessed {access_count} times.")
        elif access_count == 0:
            raise UnusedParameterException(f"Parameter: {k} is not used by the specified frame.")
    print('<'*80)
    return tags


def constrain_sample(sample: dict, custom_sample_constrainer: Callable) -> dict:
    """
    Calls the provided constraint function on the given sample. Its purpose is to ensure various logical properties
    in the sample.
    Args:
        sample: sample to check for logical constraints
        custom_sample_constrainer: function that accepts a sample and modifies it based on internal constraint logic
    Returns: the provide sample, modified
    """
    sample = custom_sample_constrainer(sample=sample)
    return sample


def load_frame(frame_name: str, frame_root: str = 'frames') -> ModuleType:
    """
    Loads a model directory by name
    Args:
        frame_name: name of frame (directory) to load
        frame_root: directory containing frame to load

    Returns:
        the loaded model frame
    """
    sys.path.append(os.getcwd())
    return importlib.import_module('.'.join([frame_root, frame_name])).model


def frame_exists(frame_name: str, frame_root: str = 'frames') -> bool:
    """
    Determines if a specified frame directory exists or not
    Args:
        frame_name: name of frame (directory) to load
        frame_root: directory containing frame to load

    Returns:
        whether the specified frame exists, boolean
    """
    frame_path = Path(frame_root, frame_name)
    return frame_path.exists()


def _read_and_write_frame_template(frame_template_name: str, new_frame_name: str, variables: Dict[str, str],
                                   frame_root: str = 'frames', dry_run: bool = False) -> None:
    print(f"Variables are: {variables}")
    if frame_exists(frame_name=new_frame_name, frame_root=frame_root) and not dry_run:
        raise FrameExistsError(f"Destination frame: {new_frame_name} already exists. Cannot overwrite it.")

    template_directory = Path(Path(__file__).absolute().parent.parent.parent, 'scripts', 'frame_templates',
                              frame_template_name)
    dest_directory = Path(frame_root, new_frame_name).absolute()
    try:
        if not dry_run:
            dest_directory.mkdir(parents=True)

        # read and write the frame template files into the new frame
        for source_filepath in template_directory.iterdir():
            if source_filepath.is_dir():
                if dry_run:
                    print(f'Skipping directory found in template dir: {source_filepath}')
                continue
            source_filepath = source_filepath.absolute()
            dest_filepath = dest_directory.joinpath(source_filepath.name)
            with open(str(source_filepath), 'r') as f:
                template_as_string = f.read()
            resolved_template_string = template_as_string.format(**variables)
            if not dry_run:
                with open(str(dest_filepath), 'w') as f:
                    f.write(resolved_template_string)
            print(f'-- Created file in frame: {new_frame_name} file: {dest_filepath.name}')
    except Exception as e:
        if not dry_run:
            shutil.rmtree(str(dest_directory), ignore_errors=True)  # ensure we don't leave a broken stub of a frame
        raise e


def create_new_frame_from_country_model(country_model: str, new_frame_name: str, frame_root: str = 'frames',
                                        dry_run: bool = False) -> None:
    variables = {'country': country_model}
    _read_and_write_frame_template(frame_template_name='new', new_frame_name=new_frame_name, variables=variables,
                                   frame_root=frame_root, dry_run=dry_run)


def create_new_frame_from_source_frame(source_frame_name: str, new_frame_name: str, frame_root: str = 'frames',
                                       dry_run: bool = False) -> None:
    """
    Creates a new frame directory, building off of an existing frame by imports
    Args:
        source_frame_name: name of the frame to build off of
        new_frame_name: name of the new frame building off of source_frame_name
        dry_run: If True, do not make a new frame, just do debugging output of what WOULD happen.
    Returns:
        None
    """
    if not frame_exists(frame_name=source_frame_name) and not dry_run:
        raise FrameDoesNotExistError(f"Source frame: {source_frame_name} does not exist.")
    variables = {'source_frame': source_frame_name}
    _read_and_write_frame_template(frame_template_name='extend', new_frame_name=new_frame_name, variables=variables,
                                   frame_root=frame_root, dry_run=dry_run)


def available_algorithms() -> List[str]:
    """
    Returns: a list of calibration algorithms available for use by name
    """
    import emodpy_workflow.lib.calibration.algorithms as algorithms
    return algorithms.available


def load_algorithm(algorithm_name: str, algorithm_root: str = 'emodpy_workflow.lib.calibration.algorithms') -> ModuleType:
    """
    Loads a calibration algorithm binding code by name relative to a code path
    Args:
        algorithm_name: the name of the algorithm to load binding code for.
        algorithm_root: the path to a module containing algorithm bindings to load

    Returns: the module of binding code for the specified calibration algorithm
    """
    return importlib.import_module('.'.join([algorithm_root, algorithm_name]))


def detect_duplicate_items_in(items: Iterable) -> List:
    """
    Simple function that detects and returns the duplicates in an provide iterable.
    Args:
        items: a collection of items to search for duplicates

    Returns: a list of duplicated items from the provided list
    """
    usage_count = Counter(items)
    return [item for item in usage_count.keys() if usage_count[item] > 1]


def load_manifest() -> ModuleType:
    try:
        return importlib.import_module(f'manifest')
    except ModuleNotFoundError:
        print(f"\n{os.path.basename(__file__)} must be run from a project version directory.\n")
        exit()
