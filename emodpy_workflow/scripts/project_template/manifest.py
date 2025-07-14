import os

manifest_dir = os.path.dirname(__file__)

###############################################################################
# Ingest Form
#
# ingest_filename
#     The excel file with parameter, analyzer, and reference data to parse, for
#     calibration purposes
#
###############################################################################

ingest_forms_dir = os.path.join(os.getcwd(), 'calibration', 'ingest_forms')
ingest_filename = None  # os.path.join(ingest_forms_dir, "ADD-INGEST-FORM-FILENAME-HERE.xlsm")

###############################################################################
# EMOD Binary & Schema
#
# executable_path
#     Path to local model executable.  You can provide your own or use the one that gets installed
#     with emod_workflow.  (It is part of the emod_hiv package.)
#
# schema_path
#     Path to the model schema file, or path to where it will be at runtime.  You can provide one that
#     goes with your provided executable or you can use the one that gets installed with emod_workflow.
#     (It is part of the emod_hiv package.)
#
# asset_collection_of_container
#     Path of file with asset collection id of container to run in (if run environment uses containers)
#     If you are running on COMPS, asset_collection_of_container can be a filename with an asset
#     collection id of the SIF file to use.  If you are running on a different system using singularity
#     to manage execution environments, then asset_collection_of_container must be a path to a SIF file
#     to use instead.  Otherwise, asset_collection_of_container is None.
#
###############################################################################

bin_dir = 'bin'
executable_path = os.path.join(manifest_dir, bin_dir, 'Eradication')
schema_path = os.path.join(manifest_dir, bin_dir, 'schema.json')

# COMPS
# asset_collection_of_container = os.path.join(manifest_dir, bin_dir, 'dtk_centos_p39.id')

# COMPS2
# asset_collection_of_container = os.path.join(manifest_dir, bin_dir, "rocky_dtk_runner_py39.sif")

# SLURM cluster
# asset_collection_of_container = "/gpfs/data/bershteynlab/EMOD/singularity_images/centos_dtk-build.sif"

# Otherwise/ContainerPlatform
asset_collection_of_container = None


###############################################################################
# EMOD Pre/Post Processing
#
# post_processing_path
#     - Indicates the dtk_post_process.py script to be run at the end of a simulation.  EMOD will
#     run this script at the very end just before the executable exits.  This allows the user
#     to do post processing (for a single simulation) as part of the simulation process.  It allows
#     you to do things like compress output files, extract the data you want from large files
#     and delete the rest, etc.
#     - This parameter can have the following values:
#         - 'standard' to use the built-in EMOD python post-processor
#         - path to a custom post-processor
#         - None for no post-processing (currently calibration-only)
#
# pre_processing_path
#     - Indicates the dtk_pre_process.py script to be run by the simulation before an other
#     processing occurs.
#     - This parameter can have the following values:
#         - path to a custom post-processor
#         - None for no post-processing
#
# in_processing_path
#     - Not used in EMOD-HIV.  Set to None.
###############################################################################

post_processing_path = None  # 'standard'
pre_processing_path = None
in_processing_path = None
