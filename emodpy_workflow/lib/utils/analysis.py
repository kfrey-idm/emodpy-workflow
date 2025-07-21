from emodpy_workflow.lib.analysis.age_bin import AgeBin
from emodpy_workflow.lib.analysis.population_obs import PopulationObs


class InvalidDateException(Exception): pass
class InvalidAgeBinException(Exception): pass
class InvalidDataframeColumnException(Exception): pass


def model_population_in_year(year, obs_population: int, df, low_age: float=None, high_age:float=None, age_bin=None,
                             year_col='Year', population_col='Population', verbose=False) -> (int, float):
    """

    Args:
        year:
        obs_population:
        df:
        low_age:
        high_age:
        age_bin:
        year_col:
        population_col:
        verbose:

    Returns:
        model_population - the population in the mode, population_ratio - ratio of observed to model population
    """

    # specify ages one way or the other, not both
    if not ((low_age is None and high_age is None) ^ (age_bin is None)):
        raise Exception('Must supply both low_age and high_age *OR* age_bin')
    if age_bin:
        low_age = age_bin.start
        high_age = age_bin.end

    if int(year) != year:
        raise InvalidDateException('Integer year required. Mid-year shifting is performed automatically.')
    year += 0.5

    if year not in list(df[year_col]):
        raise InvalidDateException('Requested year %s not in dataframe.' % year)

    # detect if ignoring an aggregated Province or Node
    if not (('Province' in df.columns) ^ ('Node' in df.columns)):
        raise Exception('Province or Node must be columns in the dataframe, not both or neither.')
    node_column = 'Province' if 'Province' in df.columns else 'Node'
    node_agg_value = PopulationObs.AGGREGATED_PROVINCE if node_column == 'Province' else PopulationObs.AGGREGATED_NODE

    if 'Age' in df.columns:
        age_col = 'Age'
        df = df[[year_col, age_col, population_col, node_column]]
        df = df.ix[
            (df[year_col] == year) &
            (df[age_col] >= low_age) &
            (df[age_col] < high_age) &
            (df[node_column] != node_agg_value)
            ]
    elif 'AgeBin' in df.columns:
        age_bin = str(AgeBin(start=low_age, end=high_age))
        age_bins = list(df['AgeBin'].unique())
        if age_bin not in age_bins:
            raise InvalidAgeBinException('AgeBin %s not found in dataframe. Available AgeBins: %s' % (age_bin, age_bins))

        age_col = 'AgeBin'
        df = df[[year_col, age_col, population_col, node_column]]
        df = df.loc[
            (df[year_col] == year) &
            (df[age_col] == age_bin) &
            (df[node_column] != node_agg_value)
            ]
    else:
        raise InvalidDataframeColumnException('No known age column in dataframe. Must have Age or AgeBin.')

    model_population = df[population_col].sum()
    population_ratio = obs_population / model_population

    if verbose:
        print('--- Pop: ref: %s model: %s ratio: %s' % (obs_population, model_population, population_ratio))

    return model_population, population_ratio
