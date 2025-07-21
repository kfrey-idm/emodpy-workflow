"""
Creates a new frame using the specified country model

Sample usage:
python -m emod_workflow.scripts.new_frame --country COUNTRY --dest DEST_FRAME
"""

from emodpy_workflow.lib.utils.runtime import create_new_frame_from_country_model


def main(args):
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
