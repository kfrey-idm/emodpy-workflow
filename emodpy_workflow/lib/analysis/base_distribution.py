import importlib
from typing import List

import numpy as np
import os
import pandas as pd

from abc import ABCMeta, abstractmethod

from emodpy_workflow.lib.analysis.data_frame_wrapper import DataFrameWrapper


class BaseDistribution(object, metaclass=ABCMeta):

    class UnknownDistributionException(Exception): pass

    LOG_FLOAT_TINY = np.log(np.finfo(float).tiny)

    def __init__(self):
        self.additional_channels = []

    @abstractmethod
    def prepare(self, dfw: DataFrameWrapper, channel: str, weight_channel: str,
                additional_keep: List[str]) -> DataFrameWrapper:
        """
        Prepare a DataFrameWrapper and this distribution object for a compare() call together. This includes dataframe
        verification/data checking, adding additional distribution-specific channels/columns, and trimming the
        data columns to the minimum needed. Depending on the particular distribution type, additional attributes
        on self may be set to prepare it in addition to the dfw (e.g. setting self.alpha_channel and self.beta_channel,
        derived from arg channel on self for BetaDistribution).
        Args:
            dfw: DataFrameWrapper containing data that will be used in a future compare() call
            channel: data channel/column in dfw that the future compare() call be regarding
            weight_channel: an analyzer weighting channel that must be kept, if specified
            additional_keep: additional columns in the DataFrameWrapper to preserve

        Returns: a modified copy of the input DataFrameWrapper
        """
        pass

    @abstractmethod
    def compare(self, df: pd.DataFrame, reference_channel: str, data_channel: str) -> float:
        """
        Returns a score between -708.3964 and 100 (bad, good) for how well the dataframe (df) simulation data column
        (data_channel) matches the reference data column (reference_channel).
        Args:
            df: pandas DataFrame with columns of data to compare
            reference_channel: reference data channel in dataframe
            data_channel: simulation data channel to compare to the reference data channel

        Returns: a floating point score measuring the degree of data/reference fit, also known colloquially as
        'likelihood'
        """
        pass

    @abstractmethod
    def add_percentile_values(self, dfw: DataFrameWrapper, channel: str, p: float) -> List[str]:
        """
        Adds a new data channel to a DataFrameWrapper object that represents a requested probability threshold/value for
        a specified channel. Useful for creating uncertainty envelopes in plots.
        Args:
            dfw: DataFrameWrapper with data to construct percentiles and to add percentiles to
            channel: the column in dfw that percentiles will be constructed from/for
            p: the 0-1 percentile level for the given channel to add

        Returns: a list containing the new channel name in dfw
        """
        pass

    @classmethod
    def from_string(cls, distribution_name: str) -> 'BaseDistribution':
        """
        Loads and returns a distribution object of the type appropriate to the provided name, e.g. BetaDistribution
        from "beta".
        Args:
            distribution_name: name of distribution type to load
        Returns: a distribution object
        """
        distribution_name = distribution_name.lower()
        distribution_class_name = cls._construct_distribution_class_name(distribution_name=distribution_name)
        distribution_file_name = cls._construct_distribution_file_name(distribution_name=distribution_name)
        try:
            distribution_class = getattr(importlib.import_module('emodpy_workflow.lib.analysis.%s' % distribution_file_name),
                                         distribution_class_name)
        except ModuleNotFoundError:
            raise cls.UnknownDistributionException('No distribution class exists for: %s' % distribution_name)

        return distribution_class()

    @classmethod
    def from_uncertainty_channel(cls, uncertainty_channel: str) -> 'BaseDistribution':
        """
        Loads and returns a distribution object of the type appropriate to the provided uncertainty channel,
        e.g. BetaDistribution from 'effective_count'.
        WARNING: this method will return the FIRST MATCH from checking distribution types in a non-guaranteed order,
        so there could be an issue if there are ever distribution types that share an uncertainty channel name.
        Args:
            uncertainty_channel: name of uncertainty channel to detect a distribution from
        Returns: a distribution object
        """
        this_file = os.path.basename(__file__)
        potential_distribution_file_names = [os.path.splitext(f)[0] for f in os.listdir(os.path.dirname(__file__))
                                             if f.endswith('.py') and f != this_file]
        distribution = None
        # import the distribution classes one at a time and check if they are the right one
        for distribution_file_name in potential_distribution_file_names:
            distribution_class_name = ''.join([word.capitalize() for word in distribution_file_name.split('_')])
            try:
                distribution_class = getattr(importlib.import_module(f"emodpy_workflow.lib.analysis.{distribution_file_name}"),
                                             distribution_class_name)
                if distribution_class.UNCERTAINTY_CHANNEL == uncertainty_channel:
                    distribution = distribution_class()
                    break
            except AttributeError:
                pass  # not a valid class, so keep going
        if distribution is None:
            raise Exception('Unable to determine distribution that uses uncertainty channel: %s' % uncertainty_channel)
        return distribution

    @staticmethod
    def _construct_distribution_class_name(distribution_name):
        return distribution_name.lower().capitalize() + 'Distribution'

    @staticmethod
    def _construct_distribution_file_name(distribution_name):
        return distribution_name.lower() + '_distribution'
