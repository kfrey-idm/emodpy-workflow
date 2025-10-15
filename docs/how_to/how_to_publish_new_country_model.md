# Publish a new country model

To publish a new country model, you can follow the steps below. This example uses the `ZambiaWithLongLastingPrep` country model in 
[Modify Campaign 3: Modify Country Model](../tutorials/modify_campaign_3_modify_country_model.md) tutorial.

1. Move `zambia_withlong_lasting_prep.py` to `/emodpy-hiv/emodpy_hiv/countries/zambia_withlong_lasting_prep/zambia_withlong_lasting_prep.py`

2. Add a `__init__.py` file under `emodpy_hiv/countries/zambia_withlong_lasting_prep` folder with:
```python
from .zambia_withlong_lasting_prep import ZambiaWithLongLastingPrep # noqa: F401
```

3. Add this line to `__init__.py` file under `emodpy_hiv/countries` folder:
```python
from emodpy_hiv.countries.zambia_withlong_lasting_prep import ZambiaWithLongLastingPrep # noqa: F401
```

4. Go to `emodpy_workflow`, reinstall `emodpy-hiv` with the new change, verify you can use the new country `ZambiaWithLongLastingPrep` model 
by running:
```bash
python -m emodpy_workflow.scripts.new_frame --country ZambiaWithLongLastingPrep --dest ZambiaWithLongLastingPrep
python -m emodpy_workflow.scripts.available_parameters -F ZambiaWithLongLastingPrep
python -m emodpy_workflow.scripts.run -N ZambiaWithLongLastingPrep -F ZambiaWithLongLastingPrep -o results/ZambiaWithLongLastingPrep -p ContainerPlatform
```
You should not need to edit the `campaign.py`, `config.py` or `demographics.py` file in the frame anymore and no more 
warning message about country model not found when creating a new frame with `ZambiaWithLongLastingPrep` country model.
