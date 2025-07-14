"""
Creates a new, blank project directory for use

Sample usage:
python -m emod_workflow.scripts.new_project --directory DIRECTORY_PATH
"""
import shutil
from pathlib import Path

TEMPLATE_DIRECTORY = Path(Path(__file__).absolute().parent, "project_template")


class DirectoryExistsError(FileExistsError):
    pass


def main(args):
    project_directory = args.dest_dir.absolute()

    # attempt to copy the project template to the project path, erroring out on existence (prevent overwrite of data)
    error = False
    try:
        shutil.copytree(src=TEMPLATE_DIRECTORY, dst=project_directory)
        print(f'Created new project directory: {args.dest_dir}')
    except FileExistsError:
        error = True
    if error is True:
        msg = f"Directory already exists at: {args.dest_dir} . Please select a new project directory name."
        raise DirectoryExistsError(msg)


DEFAULTS = {
}


def parse_args():
    import argparse

    parser = argparse.ArgumentParser()

    parser.add_argument('-d', '--directory', dest='dest_dir', type=str, required=True,
                        help=f"Path of new project directory to create and populate with initial files and "
                             f"subdirectories. Required.")

    args = parser.parse_args()
    args.dest_dir = Path(args.dest_dir)
    return args


if __name__ == "__main__":
    args = parse_args()
    main(args=args)
