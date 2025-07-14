# This frame built from frame: {source_frame} via script:
# python -m emodpy_workflow.scripts.extend_frame

from emodpy_workflow.lib.models.emod_hiv import EMOD_HIV
from emodpy_workflow.lib.utils.runtime import load_manifest

manifest = load_manifest()

from . import config
from . import demographics
from . import campaign

model = EMOD_HIV(
    manifest=manifest,
    config_initializer=config.initialize_config,
    config_parameterizer=config.get_config_parameterized_calls,
    demographics_initializer=demographics.initialize_demographics,
    demographics_parameterizer=demographics.get_demographics_parameterized_calls,
    campaign_initializer=campaign.initialize_campaign,
    campaign_parameterizer=campaign.get_campaign_parameterized_calls,
    ingest_form_path=manifest.ingest_filename,
    build_reports=config.build_reports
)
