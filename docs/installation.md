# Install

## Software prerequisites

The following is required:

- Windows or Linux (Mac is loosely supported)
- [Python 3.9.X (3.9.13 or higher) (64-bit)](https://www.python.org/downloads/release/python-3913/)

### Python

To verify you have the correct version, enter the following command:

```
python --version
```

You should see something similar to the following and it should start with "3.9":

```doscon
Python 3.9.19
```

If you do not get that, you may need to provide the full path to the python executable
or you may need to install it.  If you need the full path, please use the full path when creating the virtual environment below.

### Docker

If you want to run EMOD locally using the Container Platform, you will also need
to install Docker.  Installation will require administrative privileges.  Follow the instructions on the Docker website:

- [Windows](https://docs.docker.com/desktop/setup/install/windows-install/)
    (You might be able to install WSL via the Docker Desktop installer.)
- [Linux](https://docs.docker.com/desktop/setup/install/linux/)
- [Mac](https://docs.docker.com/desktop/setup/install/mac-install/)

!!! Warning
    Installing can require downloading close to one gigabyte of data.  The first time
    you use EMOD with the Container Platform it will download another half gigabyte.

## Setup virtual environment

The following commands will setup a
[virtual environment](reference/virtual_environments.md).  You will want to do this for all of your new projects.

1. Create the virtual environment

    ```
    python -m venv env
    ```

2. Activate the virtual environment:

    === "Windows"
        ```
        env\Scripts\activate.bat
        ```
    === "Linux"
        ```bash
        source env/bin/activate
        ```

3. Ensure pip is up to date:

    ```
    python -m pip install pip --upgrade
    ```

## Install emodpy-workflow:

Use the following command to install emodpy-workflow from IDM's Artifactory:

```
python -m pip install emodpy-workflow --extra-index-url=https://packages.idmod.org/api/pypi/pypi-production/simple
```
