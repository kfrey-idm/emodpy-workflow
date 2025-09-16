# Download data
There is a single download command to download files from simulations. However, there are multiple ways to specify
**which** simulations to download files from.

The following examples show ho to download file **output/ReportHIVByAgeAndGender.csv** on the Container Platform.

## From an experiment:

To download a report file from all simulations in an experiment, execute a command similar to the following:

```bash
python -m emodpy_workflow.scripts.download -d output/ReportHIVByAgeAndGender.csv -p ContainerPlatform --exp-id EXP_ID -o OUTPUT_DIR
```

... where EXP_ID is the unique id of an experiment and OUTPUT_DIR is the directory to store downloaded files.

---

## From a suite of experiments:

To download a report file from all simulations in a suite of experiments, execute a command similar to the following:

```bash
 python -m emodpy_workflow.scripts.download -d output/ReportHIVByAgeAndGender.csv -p ContainerPlatform --suite-id SUITE_ID -o OUTPUT_DIR
```

... where SUITE_ID is the unique id of a suite and OUTPUT_DIR is the directory to store downloaded files.

---

## From a resampled parameter set's CSV file:

To download a report file from all simulations where you used a resampled parameter set, execute a command similar to the following:

```bash
python -m emodpy_workflow.scripts.download -d output/ReportHIVByAgeAndGender.csv -p ContainerPlatform -o OUTPUT_DIR -s RESAMPLE_FILE
```

... where RESAMPLE_FILE is the path of a `resample` command result and OUTPUT_DIR is the directory to store downloaded 
files.

---

## From a receipt file:

To download a report file from a receipt file, execute a command similar to the following:


```bash
python -m emodpy_workflow.scripts.download -d output/ReportHIVByAgeAndGender.csv -p ContainerPlatform -r RECEIPT_FILE
```

... where RECEIPT_FILE is the path of a receipt created by a prior `run` command. Output will be stored in the
directory containing the receipt.

---

## Download multiple files

Downloading more than one file from simulations is a small modification of downloading a single file. For downloading a
single file, see: [Download a file from all simulations in an experiment](#from-an-experiment).

To specify more than one file for download, one specifies **all** files together as the value of the `-d flag`, 
separating them by a **comma with no spaces**.

For example, to download two files change the following:

```bash
python -m emodpy_workflow.scripts.download -d output/ReportHIVByAgeAndGender.csv -p ContainerPlatform --exp-id EXP_ID -o OUTPUT_DIR
```

to

```bash
python -m emodpy_workflow.scripts.download -d output/ReportHIVByAgeAndGender.csv,output/InsetChart.json -p ContainerPlatform --exp-id EXP_ID -o OUTPUT_DIR
```
