# Install and set up

## Choose to run the tutorials locally or use [GitHub Codespaces](https://docs.github.com/en/codespaces/about-codespaces/what-are-codespaces).

- **Locally** - To run locally, you will need to install the prerequisites as well
as emodpy-workflow.  If this looks challenging, you run into issues, or is just
more than you want to do, consider using GitHub Codespaces

    !!! Note
        For the tutorials, "local" running assumes that you are running on
        you laptop/desktop/VM.  EMOD can run on a High Performance Computing (HPC)
        cluster, but the instructions here will not address that.

- **GitHub Codespaces** - It will allow you to run EMOD in the cloud and
skip installation.  Once you decide you want to do more with EMOD,
you can come back and install EMOD locally.

## Set up locally

1. Install any prerequisites according to the [installation](../installation.md#software-prerequisites) instructions.

2. Create a new directory for your project files.

    Like for your own projects, the tutorials assume that you will have a directory
    for the [virtual environment](../reference/virtual_environments.md) and the files
    for your project.  Create a directory using the following commands:

    ```
    mkdir my_tutorial
    cd my_tutorial
    ```

3. Go back to the [installation](../installation.md#setup-virtual-environment).
Set up the virtual environment and install **emodpy-workflow**.

4. Verify that you are in the correct directory using the command below:

    === "Windows"
        ```
        cd
        ```
    === "Linux"
        ```
        pwd
        ```
    
    You should see something like the following where the last name is the directory
    you created like `my_tutorial`.

    === "Windows"
        ```
        C:\work\my_tutorial
        ```
    === "Linux"
        ```
        /home/dbridenbecker/my_tutorial
        ```

    You should be ready to start the tutorial.

## Set up codespaces

!!! Costs
    Your personal GitHub account comes with 120 core hours of FREE usage.  Unless
    you have been using your free time on other products, this should be plenty of
    time to do the tutorials.  To find out more about the costs, see
    [GitHub Codespaces billing](https://docs.github.com/en/billing/concepts/product-billing/github-codespaces)

1. Login to your GitHub account.

    You must have a GitHub account to use Codespaces.

2. Navigate your browser to the following URL:

    https://github.com/EMOD-Hub/emodpy-workflow

3. Following the instructions at
[Creating a codespace for a repository](https://docs.github.com/en/codespaces/developing-in-a-codespace/creating-a-codespace-for-a-repository).

    You can ignore the section on "Recommended secrets".

    When it is done with the "post-creation setup," you should be able to use
    the codespace.

4. Test that the code space is ready to use by executing the following command:

    ```
    pip freeze
    ```

If you see a list of python packages, the code space is setup.

5. Create a new directory for your project files.

    Similarly to the local installation, we want to create a directory where we will
    be running the tutorial.  We won't have a virtual environment because we expect to
    throw everything away.  Execute the following commands:

    ```
    cd ..
    mkdir my_tutorial
    cd my_tutorial
    ```

### Stopping and restarting a codespace

You will have times that either you need to stop your codespace or it stops
automatically.  For example, if you need to quit working on a tutorial because
you have a meeting, you will want to stop the codespace and restart it when
you have time to work on it.  See the instructions on
[stopping and starting a codespace](https://docs.github.com/en/codespaces/developing-in-a-codespace/stopping-and-starting-a-codespace) to learn how.

### Deleting a codespace

Even if your codespace is stopped, you can still be charged for storage space.
Hence, if you are not going to be using your codespace for an extended period of time,
it is recommended that you delete it.  See the instructions on
[deleting a codespace](https://docs.github.com/en/codespaces/developing-in-a-codespace/deleting-a-codespace) to learn how.
