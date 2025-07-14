import logging
from idmtools_calibra.calib_site import CalibSite

from emodpy_workflow.lib.analysis.hiv_analyzer import HIVAnalyzer

logger = logging.getLogger(__name__)


class HIVCalibSite(CalibSite):
    metadata = {}

    DEFAULT_OUTPUT_DIR = 'output'

    def __init__(self, **kwargs):
        # required kwargs first
        analyzers = kwargs.get('analyzers', None)
        if not analyzers:
            raise Exception('An analyzer dictionary must be provided to the \'analyzers\' argument.')

        # reference_data must be supplied as a kwarg and is simply stored for direct use by analyzers
        self.reference_data = kwargs.get('reference_data', None)
        if not self.reference_data:
            raise Exception('Obs/reference data object must be provided to the \'reference_data\' argument.')

        # half-year shift reference data to match EMOD. It puts annualized values on 0.5 year marks, as reference data
        # in the ingest form is expected to be on integer years. Incidence, as it is constructed in the post-processor,
        # does not need this adjustment.
        self.reference_data.adjust_years(exclude_channels=['Incidence'])

        # site_data must be supplied as a kwarg and is simply stored for direct use by analyzers
        self.site_data = kwargs.get('site_data', None)
        if not self.site_data:
            raise Exception('Site data object must be provided to the \'site_data\' argument.')

        # optional kwargs
        output_dir = kwargs.get('output_dir', self.DEFAULT_OUTPUT_DIR)

        self.reference_year = self.site_data['census_year']
        self.reference_population = self.site_data['census_population']
        self.reference_age_bin = self.site_data['census_age_bin']
        self.node_map = self.site_data['node_map']

        self.base_dir = '../../analysis'
        self.fig_format = 'png',
        self.fig_dpi = 600,
        self.verbose = True

        self.analyzers = [HIVAnalyzer(site=self, debug=False, output_dir=output_dir, **analyzer_config)
                          for analyzer_config in analyzers]

        super().__init__(self.site_data['site_name'])

    def get_setup_functions(self):
        return []

    def get_analyzers(self):
        return self.analyzers
