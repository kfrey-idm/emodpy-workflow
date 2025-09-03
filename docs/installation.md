# Install

## Software prerequisites

- The following is required:
    - Windows or Linux
    - [Python 3.9.X (3.9.13 or higher) (64-bit)](https://www.python.org/downloads/release/python-3913/)

- Instructions assume Python was installed into C:\Python39 in Windows or /c/Python39 in Linux.

If you have Python installed to a different directory, please update the Python interpreter path below to match your 
installation of Python.

1. Create the virtual environment

    ```
    /c/Python39/python -m venv env
    ```

2. Activate the virtual environment:

    === "Windows"
        ```
        env\Scripts\activate.bat
        ```
    === "Linux"
        ```
        source env/bin/activate
        ```

3. Ensure pip is up to date:

    ```
    python -m pip install pip --upgrade
    ```

4. Install emodpy-workflow:
    ```
    python -m pip install emodpy-workflow --extra-index-url=https://packages.idmod.org/api/pypi/pypi-production/simple
    ```
