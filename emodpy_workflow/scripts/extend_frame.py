"""
Creates a new frame built off of an existing frame, similar to "class inheritance"

Sample usage:
python -m emod_workflow.scripts.extend_frame --source SOURCE_FRAME --dest DEST_FRAME
"""

from emodpy_workflow.lib.utils.runtime import create_new_frame_from_source_frame


def main(args):
    create_new_frame_from_source_frame(source_frame_name=args.source_frame, new_frame_name=args.dest_frame)
    print(f'Created new frame: {args.dest_frame} which extends frame: {args.source_frame}')


DEFAULTS = {
}


def parse_args():
    import argparse

    parser = argparse.ArgumentParser()

    parser.add_argument('--source', dest='source_frame', type=str, required=True,
                        help=f"Name of model frame name extend from. Required.")
    parser.add_argument('--dest', dest='dest_frame', type=str, required=True,
                        help=f"Name of new model frame. Required.")

    args = parser.parse_args()
    return args


if __name__ == "__main__":
    args = parse_args()
    main(args=args)
