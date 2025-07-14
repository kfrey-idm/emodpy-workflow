# python files in this package/directory should be mentioned (no .py) in available attr below
#
# python files are expected to be small binding code libraries to external next-point algorithms for use with
# calibrate.py .
#
# binding library method requirements:
#
# def set_arguments(subparsers, entry_point)
#  This adds a parser to the given subparsers and then defines new available options on the new parser. Sets exe
#  entry point for the parser as provided.
#
# def initialize(args, params, model)
#  This returns the next-point algorithm object, as initialized by the provided args. params is a idmtools_calibra
#  defined dict of parameters for modifying, model is an object with references to input builders, sample constrainers,
#  etc.
#

available = ['optim_tool']
