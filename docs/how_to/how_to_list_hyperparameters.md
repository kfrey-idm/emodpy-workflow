# List hyperparameters

## List available hyperparameters

To find all hyperparameters that are available for use (like calibration, scenario design), execute the following:

```bash
python -m emodpy_workflow.scripts.available_parameters -f FRAME
```

... where FRAME is the name of the frame to be inspected.

---

## List duplicative hyperparameters

To find all hyperparameters that are used **more than once** in a frame, execute the following:

```bash
python -m emodpy_workflow.scripts.available_parameters -f FRAME
```

... where FRAME is the name of the frame to be inspected. Duplicated hyperparameters are listed at the bottom of the
result.

Duplicated hyperparameters can be **intentional** if a
hyperparameter is intended to modify more than one ParameterizedCall value. They can also be **unintentional** if an
existing hyperparameter name and label has been inadvertently reused. It is important to confirm that only intentional
duplication exists to ensure model hyperparameter values are set as expected.

