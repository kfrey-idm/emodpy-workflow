import logging
import numpy as np
import os
import pandas as pd

from idmtools_calibra.analyzers.base_calibration_analyzer import BaseCalibrationAnalyzer

from emodpy_workflow.lib.utils.analysis import model_population_in_year

from emodpy_workflow.lib.analysis.age_bin import AgeBin
from emodpy_workflow.lib.analysis.base_distribution import BaseDistribution
from emodpy_workflow.lib.analysis.channel import Channel
from emodpy_workflow.lib.analysis.population_obs import PopulationObs

logger = logging.getLogger(__name__)


class HIVAnalyzer(BaseCalibrationAnalyzer):
    class ProvincialityException(Exception): pass
    class MissingDataException(Exception): pass
    class InvalidSiteException(Exception): pass

    SIM_RESULT_CHANNEL = 'Result'
    log_float_tiny = np.log(np.finfo(float).tiny)

    AGGREGATED_NODE_MAP = {PopulationObs.AGGREGATED_NODE: PopulationObs.AGGREGATED_PROVINCE}

    @classmethod
    def construct_post_process_filename(cls, channel):
        return channel + '.csv'

    def __init__(self, site, weight,
                 channel, scale_population,
                 distribution, provinciality, age_bins=AgeBin.ALL,
                 debug=False, verbose=True, output_dir='output'):
        super().__init__(weight=weight)

        post_process_dir = os.path.join('output', 'post_process')
        self.filenames = [os.path.join(post_process_dir, self.construct_post_process_filename(channel=channel)),
                          os.path.join(post_process_dir, self.construct_post_process_filename(channel='Population'))]
        self.weight = weight

        # verify the site object has some critical attributes so we can print a nice error if not
        self.site = site
        required_attributes = ['reference_population', 'reference_year', 'reference_age_bin', 'node_map']
        missing_attributes = [att for att in required_attributes if not hasattr(self.site, att)]
        if len(missing_attributes) > 0:
            raise self.InvalidSiteException('Site object missing required attributes: %s' % dir(self.site))

        self.site.node_map = {**self.site.node_map, **self.AGGREGATED_NODE_MAP}
        self.debug = debug
        self.output_dir = output_dir
        if self.debug:
            # we will only need this if debug is True
            os.makedirs(self.output_dir, exist_ok=True)

        typ = 'count' if scale_population else 'fraction'
        self.channel = Channel(channel, type=typ)
        self.distribution = BaseDistribution.from_string(distribution_name=distribution)
        self.provinciality = provinciality

        # make sure the age_bins are in a list if they are not AgeBin.ALL
        if age_bins == AgeBin.ALL:
            self.age_bins = age_bins
        else:
            self.age_bins = age_bins if isinstance(age_bins, list) else [age_bins]

        self.verbose = verbose

        self.reference = self.site.reference_data
        try:
            age_bins = self.age_bins if isinstance(self.age_bins, list) else [self.age_bins] # listifying AgeBin.ALL for uid only
            age_bins_str = ''.join([str(age_bin) for age_bin in age_bins])
            self.uid = '_'.join([self.site.__class__.__name__, self.channel.name, self.provinciality,
                                 age_bins_str, self.distribution.__class__.__name__])
        except AttributeError as e:
            raise AttributeError('Provided Site object has no attribute \'name\', but it needs one.') from e

        # now add in any distribution-specific columns; do not modify existing shared self.reference object
        # also make sure to trim off any unnecessary columns in the reference; keep it clean!
        self.reference = self.distribution.prepare(dfw=self.reference,
                                                   channel=self.channel.name,
                                                   weight_channel=PopulationObs.WEIGHT_CHANNEL)

        # trim off unnecessary age bins and node(s)
        self.reference = type(self.reference)(dataframe=self._trim_df(df=self.reference._dataframe),
                                              stratifiers=self.reference.stratifiers)
        if self.reference._dataframe.empty:
            raise self.MissingDataException(f"Missing reference data in ingest form for channel: {channel}, "
                                             f"provinciality: {provinciality}, ang_bins:  {age_bins_str}.")

    def _trim_df(self, df):
        # keep only provincial or non-provincial/agg data, not both, depending on request
        if self.provinciality == PopulationObs.PROVINCIAL:
            trimmed_df = df.loc[df['Province'] != PopulationObs.AGGREGATED_PROVINCE]
        elif self.provinciality == PopulationObs.NON_PROVINCIAL:
            trimmed_df = df.loc[df['Province'] == PopulationObs.AGGREGATED_PROVINCE]
        else:
            raise self.ProvincialityException('Unknown provinciality: %s' % self.provinciality)

        # now handle age bin selection if not using all bins
        if self.age_bins != AgeBin.ALL:
            # keep only specified age bins; reference bins will be trimmed in the merge
            age_bin_strs = [str(age_bin) for age_bin in self.age_bins]
            trimmed_df = trimmed_df.loc[trimmed_df['AgeBin'].isin(age_bin_strs)]
        return trimmed_df

    def map(self, data, item):
        # Separated out to facilitate unit testing

        # rename nodes according to the node map
        sim = data[self.filenames[0]].set_index('Node').rename(self.site.node_map).reset_index().rename(columns={'Node': 'Province'})
        sim = self._trim_df(df=sim)

        if self.channel.needs_pop_scaling:
            # drop non-provincial/agg data to prevent double counts with with provincial data
            pop_data = data[self.filenames[1]]
            pop_data = pop_data.loc[pop_data['Node'] != PopulationObs.AGGREGATED_NODE]
            pop_scaling_factor = self.compute_pop_scaling_factor(pop_data)
            sim[self.SIM_RESULT_CHANNEL] *= pop_scaling_factor

        sim_dfw = PopulationObs(dataframe=sim, stratifiers=self.reference.stratifiers)
        sim_dfw.fix_age_bins()  # back compatibility; change ', ' age bins to ':' delimited
        merged = self.reference.merge(sim_dfw,
                                      index=self.reference.stratifiers,
                                      keep_only=[self.channel.name, self.SIM_RESULT_CHANNEL,
                                                 PopulationObs.WEIGHT_CHANNEL, *self.distribution.additional_channels])

        missing_tuples = self.reference.find_missing_tuples(sim_dfw, value_column_base=self.channel.name,
                                                            value_column_target=self.SIM_RESULT_CHANNEL)
        if missing_tuples:
            raise self.MissingDataException("\n\n[%s] Missing some reference data in simulation output."%self.uid)
                                            # "\nThe following tuples are missing in the simulation data for the chanel {}:"
                                            # "\n\n{}".format(self.uid, self.channel.name, tabulate(missing_tuples, headers=self.reference.stratifiers))
                                            # )

        merged._dataframe.index.name = 'Index'
        result = {
            'df': merged._dataframe,
            'stratifiers': merged.stratifiers,
            'reference_channel': self.channel.name,
            'data_channel': self.SIM_RESULT_CHANNEL
        }
        return result

    @staticmethod
    def _compute_normalized_reference_weights(sample, stratifiers):
        reference_weights = sample.set_index(stratifiers).groupby(stratifiers).apply(lambda df: df.loc[df.index[0], PopulationObs.WEIGHT_CHANNEL])
        normalized_reference_weights = reference_weights / reference_weights.sum()
        return normalized_reference_weights

    @staticmethod
    def _compute_log_likelihood_values(sample, stratifiers, distribution, reference_channel, data_channel):
        log_likelihood = sample.set_index(stratifiers).groupby(stratifiers).apply(
            distribution.compare, reference_channel=reference_channel, data_channel=data_channel
        )
        return log_likelihood

    @classmethod
    def _compare(cls, sample, stratifiers, distribution, reference_channel, data_channel, weight):
        sample = sample.reset_index()
        log_likelihood = cls._compute_log_likelihood_values(sample=sample,
                                                            stratifiers=stratifiers,
                                                            distribution=distribution,
                                                            reference_channel=reference_channel,
                                                            data_channel=data_channel)

        # grab the weight for each stratified group (arbitrarily grabbing it off the first replicate) and normalize
        # assumes that by grouping by these stratifiers the ONLY difference by row is replicate number
        normalized_reference_weights = cls._compute_normalized_reference_weights(sample=sample,
                                                                                 stratifiers=stratifiers)

        # need to weight log_likelihood.values by individual reference weights before np.mean;
        # some obs are more important! Finally, weight by analyzer weight (self.weight)
        return np.dot(log_likelihood.values, normalized_reference_weights.values) * weight

    def compare(self, sample, stratifiers, distribution, reference_channel, data_channel):
        return self._compare(sample, stratifiers, distribution, reference_channel, data_channel, weight=self.weight)

    def reduce(self, all_data):
        """
        Combine the simulation data into a single table for all analyzed simulations.
        """
        data = {}

        # Create the data and key it with (sample,id)
        stratifiers = None
        reference_channel = None
        data_channel = None
        for simulation, mapping_dict in all_data.items():
            key = (int(simulation.tags.get("__sample_index__")), simulation.id)
            data[key] = mapping_dict['df']
            stratifiers = stratifiers or mapping_dict['stratifiers'] # only needs to be set once; they're identical
            reference_channel = reference_channel or mapping_dict['reference_channel']
            data_channel = data_channel or mapping_dict['data_channel']

        data = pd.concat(list(data.values()), axis=0,
                         keys=list(data.keys()),
                         names=['Sample', 'Sim_Id'])

        data.reset_index(level='Index', drop=True, inplace=True)

        if self.debug:
            results_path = os.path.join(self.output_dir, f"finalize_input_{self.uid}.csv")
            print(f'--> Writing to {results_path}')
            data.sort_index(axis=1).to_csv(results_path)

        # compare sim data to reference data and determine a match likelihood
        results = data.reset_index().groupby(['Sample']).apply(self.compare,
                                                               stratifiers=stratifiers, distribution=self.distribution,
                                                               reference_channel=reference_channel, data_channel=data_channel)

        if self.debug:
            results_path = os.path.join(self.output_dir, f"results_{self.uid}.csv")
            print(f'--> Writing to {results_path}')
            results.to_csv(results_path)

        return results

    def compute_pop_scaling_factor(self, pop_df):
        if isinstance(self.site.reference_population, float) or isinstance(self.site.reference_population, int):
            sim_pop, pop_scaling_factor = model_population_in_year(self.site.reference_year,
                                                                   obs_population=self.site.reference_population,
                                                                   age_bin=self.site.reference_age_bin,
                                                                   df=pop_df,
                                                                   population_col=self.SIM_RESULT_CHANNEL,
                                                                   verbose=False)
            if self.verbose:
                print('Pop scaling is %.4f' % pop_scaling_factor)
        else:
            raise Exception('dict (per-node) reference population not currently supported. '
                            'Please ask for a developer for assistance.')
            assert(isinstance(self.reference_population, dict))
            pop_df = pop_df.reset_index(drop=True).set_index('Node')
            pop_df.rename(self.node_map, inplace=True)
            pop_df = pop_df.reset_index().groupby(['Year', 'Node']).sum().loc[self.reference_year]
            ref = pd.DataFrame({'Reference': self.reference_population})
            pop_scaling_factor = ref['Reference']/pop_df['Result']
            if self.verbose:
                print('Progress: %d of %d (%.1f%%).  Pop scaling is provincially weighted from %.2f to %.2f.' %
                      (len(self.sim_ids)-num_outstanding,
                       len(self.sim_ids),
                       100*(len(self.sim_ids)-num_outstanding) / float(len(self.sim_ids)),
                       pop_scaling_factor.min(),
                       pop_scaling_factor.max()))

            for prov, pop_df in pop_scaling_factor.items():
                if prov in self.ps_ave:
                    self.ps_ave[prov] += pop_df
                else:
                    self.ps_ave[prov] = pop_df
            self.ps_ave['Count'] += 1

        return pop_scaling_factor
