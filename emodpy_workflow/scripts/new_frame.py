"""
Creates a new frame using the specified country model

Sample usage:
python -m emod_workflow.scripts.new_frame --country COUNTRY --dest DEST_FRAME
"""
import warnings

from emodpy_workflow.lib.utils.runtime import create_new_frame_from_country_model


def verify_country_model_exits(country_model: str):
    import importlib
    from emodpy_hiv.country_model import Country

    countries_module = importlib.import_module('emodpy_hiv.countries')

    # First, verify the requested country model exists as an attribute in 'countries'
    attr_exists = hasattr(countries_module, country_model)
    if attr_exists:
        # Second, verify the requested country model is a descendant of the Country class
        potential_country = getattr(countries_module, country_model)
        try:
            country_exists = True if Country in potential_country.mro() else False
        except AttributeError:
            # This occurs if potential_country has no method resolution order. It is not a country model class.
            country_exists = False
    else:
        country_exists = False
    return country_exists


def main(args):
    if not verify_country_model_exits(country_model=args.country_model):
        warnings.warn(f"Country model with name: {args.country_model} does not exist in emodpy-hiv. It must have the "
                      f"exact spelling "
                      f"and capitalization of an emodpy-hiv country model class or one that you create and import to"
                      f"your frame via manual frame edits.", stacklevel=2)
    create_new_frame_from_country_model(country_model=args.country_model, new_frame_name=args.dest_frame)
    print(f'Created new frame: {args.dest_frame} using country model: {args.country_model}')


DEFAULTS = {
}


def parse_args():
    import argparse

    parser = argparse.ArgumentParser()

    parser.add_argument('--country', dest='country_model', type=str, required=True,
                        help=f"Country model name to make new frame with. Required.")
    parser.add_argument('--dest', dest='dest_frame', type=str, required=True,
                        help=f"Name of new model frame. Required.")

    args = parser.parse_args()
    return args


if __name__ == "__main__":
    args = parse_args()
    main(args=args)
