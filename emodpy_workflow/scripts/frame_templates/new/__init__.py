# This frame built via script:
# python -m emodpy_workflow.scripts.new_frame

from emodpy_workflow.lib.models.emod_hiv import EMOD_HIV
from emodpy_workflow.lib.utils.runtime import load_manifest

# The manifest contains input file pathing information for the project
manifest = load_manifest()

# EMOD contains three main configuration objects: config, demographics, and campaign. The related information
# for generating these input objects is placed into concern-specific files in this directory.
from . import config
from . import demographics
from . import campaign

# 'model' is a required attribute of this file. All core scripts access frames by loading the 'model' attribute.
# The model attribute is assigned a model- and disease-specific object that contains all information regarding
# how to build the inputs for the model and generating its command line for execution.
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
