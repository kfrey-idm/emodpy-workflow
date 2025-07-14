import numpy as np
import os
import pandas as pd
import unittest

import emodpy_workflow.lib.utils.project_data as ingest_utils

from emodpy_workflow.lib.analysis.age_bin import AgeBin
from emodpy_workflow.lib.analysis.base_distribution import BaseDistribution
from emodpy_workflow.lib.analysis.gaussian_distribution import GaussianDistribution
from emodpy_workflow.lib.analysis.hiv_analyzer import HIVAnalyzer
from emodpy_workflow.lib.analysis.hiv_calib_site import HIVCalibSite
from emodpy_workflow.lib.analysis.population_obs import PopulationObs

from idmtools.analysis.analyze_manager import AnalyzeManager
from idmtools.core import ItemType
from idmtools.core.platform_factory import Platform

"""
Even though it is less transparent than putting the reference data here in this test file and manually making pandas
Dataframes, I have opted to put the test reference data into a parsed xlsm ingest form to make sure that the parsed data
format works with HIVAnalyzer. Otherwise, we would end up in the situation where the parser has tests, HIVAnalyzer has
tests, and no tests that bridge the connection of the two.
"""


class TestHIVAnalyzer(unittest.TestCase):

    def setUp(self):
        self.data_directory = os.path.join(os.path.dirname(__file__), 'input', 'analyzers')
        filename = os.path.join(self.data_directory, 'valid_ingest_form.xlsm')
        params, site_info, reference, analyzers, channels = ingest_utils.parse_ingest_data_from_xlsm(filename=filename)
        self.params = params
        self.site_info = site_info
        self.reference = reference
        self.analyzers = analyzers
        self.site = HIVCalibSite(reference_data=self.reference, site_data=site_info, analyzers=self.analyzers,
                                  force_apply=True)

        self.population_only_cols = set(['Population', 'two_sigma'])

    def tearDown(self):
        pass

    def test_fail_if_invalid_provinciality(self):
        self.assertRaises(HIVAnalyzer.ProvincialityException,
                          HIVAnalyzer,
                          site=self.site, weight=1.0, channel='Prevalence',
                          distribution='Beta', scale_population=False, provinciality='not-a-provinciality')

    def test_verify_provinciality_set_properly(self):
        channel = 'Prevalence'

        # PROVINCIAL

        provinciality = PopulationObs.PROVINCIAL
        analyzer_dict = [a for a in self.analyzers if a['channel'] == channel and a['provinciality'] == provinciality][0]
        analyzer = HIVAnalyzer(site=self.site, weight=1.0,
                               channel=analyzer_dict['channel'],
                               distribution=analyzer_dict['distribution'],
                               provinciality=analyzer_dict['provinciality'],
                               scale_population=analyzer_dict['scale_population'],
                               age_bins=analyzer_dict['age_bins'])
        self.assertEqual(analyzer.provinciality, provinciality)

        # verify that analyzer.reference contains the right data now

        # First, hard-coded test in case other things have broken without notice
        expected_provinces = ['Antofagasta', 'Atacama', 'Coquimbo']
        provinces = analyzer.reference._dataframe['Province'].unique()
        self.assertEqual(sorted(provinces), sorted(expected_provinces))

        # now a full exactness check
        reference_df = self.reference._dataframe
        expected_df = reference_df.loc[reference_df['Province'] != PopulationObs.AGGREGATED_PROVINCE]\
            .reset_index(drop=True).sort_index(axis=1)
        expected_df = expected_df[list(set(expected_df.columns)-self.population_only_cols)].sort_index(axis=1)
        result_df = analyzer.reference._dataframe[expected_df.columns].sort_index(axis=1) # no need to compare beta cols that were added
        self.assertTrue(result_df.equals(expected_df))

        # NON-PROVINCIAL

        provinciality = PopulationObs.NON_PROVINCIAL
        analyzer_dict = [a for a in self.analyzers if a['channel'] == channel and a['provinciality'] == provinciality][0]
        analyzer = HIVAnalyzer(site=self.site, weight=1.0,
                               channel=analyzer_dict['channel'],
                               distribution=analyzer_dict['distribution'],
                               provinciality=analyzer_dict['provinciality'],
                               scale_population=analyzer_dict['scale_population'],
                               age_bins=analyzer_dict['age_bins'])
        self.assertEqual(analyzer.provinciality, provinciality)

        # verify that analyzer.reference contains the right data now

        # First, hard-coded test in case other things have broken without notice
        expected_provinces = [PopulationObs.AGGREGATED_PROVINCE]
        provinces = analyzer.reference._dataframe['Province'].unique()
        self.assertEqual(sorted(provinces), sorted(expected_provinces))

        # now a full exactness check
        if len(analyzer_dict['age_bins']) != 1:
            raise Exception('test is broken; currently expects there to be only ONE requested custom age bin')
        reference_df = self.reference._dataframe
        expected_df = reference_df.loc[(reference_df['Province'] == PopulationObs.AGGREGATED_PROVINCE) &
                                       (reference_df['AgeBin'] == analyzer_dict['age_bins'][0])]\
            .reset_index(drop=True).sort_index(axis=1)
        expected_df = expected_df[list(set(expected_df.columns)-self.population_only_cols)].sort_index(axis=1)
        result_df = analyzer.reference._dataframe[expected_df.columns].sort_index(axis=1) # no need to compare beta cols that were added
        self.assertTrue(result_df.equals(expected_df))

    def test_verify_all_age_bins_set_properly(self):
        channel = 'Prevalence'

        analyzer_dict = [a for a in self.analyzers
                         if a['channel'] == channel and
                         a['provinciality'] == PopulationObs.PROVINCIAL and
                         a['age_bins'] == AgeBin.ALL][0]
        analyzer = HIVAnalyzer(site=self.site, weight=1.0,
                               channel=analyzer_dict['channel'],
                               distribution=analyzer_dict['distribution'],
                               provinciality=analyzer_dict['provinciality'],
                               scale_population=analyzer_dict['scale_population'],
                               age_bins=analyzer_dict['age_bins'])

        # verify that analyzer.reference contains the right data now

        # First, hard-coded test in case other things have broken without notice
        expected_age_bins = [str(AgeBin(start=0, end=100)), str(AgeBin(start=15, end=50))]
        age_bins = analyzer.reference._dataframe['AgeBin'].unique()
        self.assertEqual(sorted(age_bins), sorted(expected_age_bins))

        # now a full exactness check
        reference_df = self.reference._dataframe
        expected_df = reference_df.loc[reference_df['Province'] != PopulationObs.AGGREGATED_PROVINCE].\
            reset_index(drop=True).sort_index(axis=1)
        expected_df = expected_df[list(set(expected_df.columns)-self.population_only_cols)].sort_index(axis=1)
        result_df = analyzer.reference._dataframe[expected_df.columns].sort_index(axis=1) # no need to compare beta cols that were added

        self.assertTrue(result_df.equals(expected_df))

    def test_verify_selected_age_bins_set_properly(self):
        channel = 'Prevalence'

        custom_age_bin = AgeBin(start=15, end=50)
        analyzer_dict = [a for a in self.analyzers
                         if a['channel'] == channel and
                         a['provinciality'] == PopulationObs.NON_PROVINCIAL and
                         a['age_bins'] == [str(custom_age_bin)]][0]
        analyzer = HIVAnalyzer(site=self.site, weight=1.0,
                               channel=analyzer_dict['channel'],
                               distribution=analyzer_dict['distribution'],
                               provinciality=analyzer_dict['provinciality'],
                               scale_population=analyzer_dict['scale_population'],
                               age_bins=analyzer_dict['age_bins'])

        # verify that analyzer.reference contains the right data now

        # First, hard-coded test in case other things have broken without notice
        expected_age_bins = [str(custom_age_bin)]
        age_bins = analyzer.reference._dataframe['AgeBin'].unique()
        self.assertEqual(sorted(age_bins), sorted(expected_age_bins))

        # now a full exactness check
        reference_df = self.reference._dataframe
        expected_df = reference_df.loc[(reference_df['Province'] == PopulationObs.AGGREGATED_PROVINCE) &
                                       (reference_df['AgeBin'] == str(custom_age_bin))].\
            reset_index(drop=True).sort_index(axis=1)
        expected_df = expected_df[list(set(expected_df.columns)-self.population_only_cols)].sort_index(axis=1)
        result_df = analyzer.reference._dataframe[expected_df.columns].sort_index(axis=1) # no need to compare beta cols that were added

        self.assertTrue(result_df.equals(expected_df))

    def test_verify_channel_set_properly(self):
        channel = 'Population'

        analyzer_dict = [a for a in self.analyzers
                         if a['channel'] == channel and
                         a['provinciality'] == PopulationObs.NON_PROVINCIAL and
                         a['age_bins'] == AgeBin.ALL][0]
        analyzer = HIVAnalyzer(site=self.site, weight=1.0,
                               channel=analyzer_dict['channel'],
                               distribution=analyzer_dict['distribution'],
                               provinciality=analyzer_dict['provinciality'],
                               scale_population=analyzer_dict['scale_population'],
                               age_bins=analyzer_dict['age_bins'])

        # expecting one data row to make it through with the channel of 'Population'
        self.assertEqual(len(analyzer.reference._dataframe.index), 1)
        self.assertEqual(analyzer.reference._dataframe['Population'][0], 1000)
        self.assertEqual(analyzer.reference._dataframe['two_sigma'][0], 50)

    def test_fail_if_missing_some_reference_years_in_sim_years(self):
        channel = 'Prevalence'

        custom_age_bin = AgeBin(start=15, end=50)
        analyzer_dict = [a for a in self.analyzers
                         if a['channel'] == channel and
                         a['provinciality'] == PopulationObs.NON_PROVINCIAL and
                         a['age_bins'] == [str(custom_age_bin)]][0]
        analyzer = HIVAnalyzer(site=self.site, weight=1.0,
                               channel=analyzer_dict['channel'],
                               distribution=analyzer_dict['distribution'],
                               provinciality=analyzer_dict['provinciality'],
                               scale_population=analyzer_dict['scale_population'],
                               age_bins=analyzer_dict['age_bins'])

        key = analyzer.filenames[0]
        # the matching reference data for this is actually 2010, not 2012, so should trigger a 'missing sim year' error
        data = {
            'Year': 2012,
            'Node': PopulationObs.AGGREGATED_NODE,
            'Gender': 'Female',
            'AgeBin': '[0:100)',
            'Result': 0.15}
        data = pd.DataFrame([data])
        made_up_sim_data_missing_2012 = {key: data}
        self.assertRaises(HIVAnalyzer.MissingDataException,
                          analyzer.map,
                          item=None,  # not needed in HIVAnalyzer currently
                          data=made_up_sim_data_missing_2012)

    class DummySiteClass(object):
        pass

    def _make_dummy_site(self, required_attributes):
        dummy_site = self.DummySiteClass()
        for att in required_attributes:
            setattr(dummy_site, att, 'arbitrary_value')
        return dummy_site

    def test_fail_if_site_missing_required_attributes(self):
        channel = 'Prevalence'
        analyzer_dict = [a for a in self.analyzers
                         if a['channel'] == channel and
                         a['provinciality'] == PopulationObs.PROVINCIAL and
                         a['age_bins'] == AgeBin.ALL][0]

        required_attributes = ['reference_population', 'reference_year', 'reference_age_bin', 'node_map']
        for exclusion in required_attributes:
            atts = set(required_attributes) - {exclusion}
            dummy_site = self._make_dummy_site(atts)
            self.assertRaises(HIVAnalyzer.InvalidSiteException,
                              HIVAnalyzer,
                              site=dummy_site,
                              weight=1.0,
                              channel=analyzer_dict['channel'],
                              distribution=analyzer_dict['distribution'],
                              provinciality=analyzer_dict['provinciality'],
                              scale_population=analyzer_dict['scale_population'],
                              age_bins=analyzer_dict['age_bins'])

    def test_verify_per_reference_data_weights_are_applied_properly(self):
        # test data to use
        reference_channel = 'Population'
        data = [
            {'Year': 2010, 'Gender': 'Male',   HIVAnalyzer.SIM_RESULT_CHANNEL: 5,  PopulationObs.WEIGHT_CHANNEL: 1,
             'two_sigma': 0.5, reference_channel: 6.5, 'Province': PopulationObs.AGGREGATED_PROVINCE},
            {'Year': 2010, 'Gender': 'Female', HIVAnalyzer.SIM_RESULT_CHANNEL: 6, PopulationObs.WEIGHT_CHANNEL: 4.0,
             'two_sigma': 0.7, reference_channel: 7.0, 'Province': PopulationObs.AGGREGATED_PROVINCE},
            {'Year': 2012, 'Gender': 'Male',   HIVAnalyzer.SIM_RESULT_CHANNEL: 7, PopulationObs.WEIGHT_CHANNEL: 0.6,
             'two_sigma': 0.8, reference_channel: 8.5, 'Province': PopulationObs.AGGREGATED_PROVINCE},
            {'Year': 2012, 'Gender': 'Female', HIVAnalyzer.SIM_RESULT_CHANNEL: 8, PopulationObs.WEIGHT_CHANNEL: 1,
             'two_sigma': 0.9, reference_channel: 7.5, 'Province': PopulationObs.AGGREGATED_PROVINCE}
        ]
        data = pd.DataFrame(data)
        stratifiers = ['Year', 'Province', 'Gender']
        dfw = PopulationObs(dataframe=data, stratifiers=stratifiers)
        distribution = BaseDistribution.from_string('Gaussian')
        dfw = distribution.prepare(dfw=dfw,
                                   channel=reference_channel,
                                   weight_channel=PopulationObs.WEIGHT_CHANNEL,
                                   additional_keep=[HIVAnalyzer.SIM_RESULT_CHANNEL])

        expected_weights_by_year = {
            2010: {'Male': 0.2, 'Female': 0.8},
            2012: {'Male': 0.375, 'Female': 0.625}
        }

        # Make sure normalized weights are computed properly
        normalized_weights_by_year = {}
        for year, expected_weights_by_gender in expected_weights_by_year.items():
            sample = dfw._dataframe.loc[data['Year'] == year]
            normalized_weights = HIVAnalyzer._compute_normalized_reference_weights(sample=sample,
                                                                                   stratifiers=stratifiers)
            for gender, expected_weight in expected_weights_by_gender.items():
                key = (year, PopulationObs.AGGREGATED_PROVINCE, gender)
                self.assertAlmostEqual(normalized_weights[key], expected_weight, places=12)
            normalized_weights_by_year[year] = normalized_weights

        # get the computed likelihoods
        likelihood_by_year = {}
        for year, expected_weights in expected_weights_by_year.items():
            sample = dfw._dataframe.loc[data['Year'] == year]
            likelihood_by_year[year] = HIVAnalyzer._compute_log_likelihood_values(sample=sample,
                                                                                  stratifiers=stratifiers,
                                                                                  distribution=distribution,
                                                                                  reference_channel=reference_channel,
                                                                                  data_channel=HIVAnalyzer.SIM_RESULT_CHANNEL)

        # dot product the likelihoods and normalized weights to verify correctness vs actual computation
        analyzer_weight = 1
        analyzer_weight_1_by_year = {}
        for year in expected_weights_by_year.keys():
            sample = dfw._dataframe.loc[data['Year'] == year]
            expected_value = np.dot(normalized_weights_by_year[year], likelihood_by_year[year])
            actual_value = HIVAnalyzer._compare(sample=sample,
                                                stratifiers=stratifiers,
                                                distribution=distribution,
                                                reference_channel=reference_channel,
                                                data_channel=HIVAnalyzer.SIM_RESULT_CHANNEL,
                                                weight=analyzer_weight)
            self.assertEqual(actual_value, expected_value)
            analyzer_weight_1_by_year[year] = actual_value

        # now vary the analyzer weight; still as expected?
        analyzer_weight = 0.5
        for year in expected_weights_by_year.keys():
            sample = dfw._dataframe.loc[data['Year'] == year]
            expected_value = analyzer_weight_1_by_year[year] * analyzer_weight
            actual_value = HIVAnalyzer._compare(sample=sample,
                                                stratifiers=stratifiers,
                                                distribution=distribution,
                                                reference_channel=reference_channel,
                                                data_channel=HIVAnalyzer.SIM_RESULT_CHANNEL,
                                                weight=analyzer_weight)
            self.assertEqual(actual_value, expected_value)

# TODO: revive this or remake result
#     def test_valid_garden_path_setup_regression(self):
#         # analyzing and comparing answer against pre-refactor analyzer results
#
#         regression_data_dir = os.path.join(self.data_directory, 'regression')
#         regression_filename = os.path.join(regression_data_dir, 'regression_ingest_form.xlsm')
#         params, site_info, reference, analyzers, channels = ingest_utils.parse_ingest_data_from_xlsm(filename=regression_filename)
#         site = HIVCalibSite(reference_data=reference, site_data=site_info, analyzers=analyzers, force_apply=True)
#
#         platform = Platform('Belegost')
#         exp_id = 'b04e1132-dbd0-e811-a2bd-c4346bcb1555'
#         am = AnalyzeManager(ids=[(exp_id, ItemType.EXPERIMENT)], platform=platform)
#         for a in site.analyzers:
#             am.add_analyzer(a)
#         analyzers = am.analyze(test_only=True)
#
#         # test the results of the 4 analyzers used in the test experiment
#         tests = {
#             'results_NationalPrevalenceAnalyzer.csv': {
#                 'channel': 'Prevalence',
#                 'provinciality': PopulationObs.NON_PROVINCIAL
#             },
#             'results_ProvincialPrevalenceAnalyzer.csv': {
#                 'channel': 'Prevalence',
#                 'provinciality': PopulationObs.PROVINCIAL
#             },
#             'results_PopulationAnalyzer.csv': {
#                 'channel': 'Population',
#                 'provinciality': PopulationObs.PROVINCIAL
#             },
#             'results_ProvincialARTAnalyzer.csv': {
#                 'channel': 'On_ART',
#                 'provinciality': PopulationObs.PROVINCIAL
#             },
#         }
#         for fn, test_dict in tests.items():
#             analyzer = [a for a in analyzers if a.channel.name == test_dict['channel'] and a.provinciality == test_dict['provinciality']][0]
#             regression_filename = os.path.join(regression_data_dir, fn)
#             regression_values = pd.read_csv(regression_filename, header=None, names=['Sample', 'Result']).set_index(keys='Sample').sort_index()['Result']
#             max_diff = (analyzer.results - regression_values).abs().max()
#             self.assertTrue(max_diff < 1e-12)

    # perhaps add these tests some day. Currently garden-path covered by the regression test
    # def test_verify_distribution_is_setup_properly(self):
    #     pass
    # def test_population_scaling_toggle_works(self):
    #     pass

    def test_fail_if_missing_non_provincial_data(self):
        filename = "missing_non-provincial_data.xlsm"
        filename = os.path.join(self.data_directory, filename)
        params, site_info, reference, analyzers, channels = ingest_utils.parse_ingest_data_from_xlsm(filename=filename)
        with self.assertRaises(HIVAnalyzer.MissingDataException) as cm:
            HIVCalibSite(reference_data=reference, site_data=site_info, analyzers=analyzers,force_apply=True)

        self.assertIn('channel: Prevalence, provinciality: Non-provincial', str(cm.exception))
        self.result = True

    def test_fail_if_missing_provincial_data(self):
        filename = "missing_provincial_data.xlsm"
        filename = os.path.join(self.data_directory, filename)
        params, site_info, reference, analyzers, channels = ingest_utils.parse_ingest_data_from_xlsm(filename=filename)
        with self.assertRaises(HIVAnalyzer.MissingDataException) as cm:
            HIVCalibSite(reference_data=reference, site_data=site_info, analyzers=analyzers,force_apply=True)

        self.assertIn('channel: Prevalence, provinciality: Provincial', str(cm.exception))
        self.result = True

    def test_fail_if_missing_Obs_sheet(self):
        filename = "missing_Obs_sheet.xlsm"
        filename = os.path.join(self.data_directory, filename)
        params, site_info, reference, analyzers, channels = ingest_utils.parse_ingest_data_from_xlsm(filename=filename)
        with self.assertRaises(GaussianDistribution.InvalidUncertaintyException) as cm:
            HIVCalibSite(reference_data=reference, site_data=site_info, analyzers=analyzers, force_apply=True)

        self.assertIn('gaussian distributions', str(cm.exception))
        self.result = True

    def test_fail_if_missing_Obs_metadata(self):
        filename = "missing_Obs_metadata.xlsm"
        filename = os.path.join(self.data_directory, filename)
        with self.assertRaises(ingest_utils.ObsMetadataException) as cm:
            params, site_info, reference, analyzers, channels = ingest_utils.parse_ingest_data_from_xlsm(filename=filename)

        self.assertIn('Population', str(cm.exception))
        self.result = True


if __name__ == '__main__':
    unittest.main()
