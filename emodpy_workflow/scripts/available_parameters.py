from itertools import chain
from pprint import pprint

from emodpy_workflow.lib.utils.runtime import load_frame, detect_duplicate_items_in


def main(args):
    args.frame.initialize_executable()
    available_parameters = args.frame.available_parameters
    pprint(available_parameters)

    # detect duplicates as they can create undefined behavior as to how a parameter works
    line = ''.join('-'*80)
    all_parameters = list(chain(*available_parameters.values()))
    duplicate_arguments = detect_duplicate_items_in(items=all_parameters)
    if len(duplicate_arguments) > 0:
        duplicate_str = ', '.join(duplicate_arguments)
        print(f"{line}\nWARNING: Duplicate parameter(s) detected: {duplicate_str}\n{line}")
    else:
        print(f"{line}\nNo duplicate parameters detected.\n{line}")


def parse_args():
    import argparse

    parser = argparse.ArgumentParser()
    parser.add_argument('-f', '--frame', dest='frame', type=str, required=True,
                        help=f"Model frame name to search for available parameters in "
                             f"(directory of python input builders). Required.")

    args = parser.parse_args()
    args.frame = load_frame(frame_name=args.frame)

    return args


if __name__ == "__main__":
    args = parse_args()
    main(args)
