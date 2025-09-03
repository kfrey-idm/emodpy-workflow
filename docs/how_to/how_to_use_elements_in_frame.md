# Use elements in a frame

## Add additional config elements

To add a new hyperparameter to the config, add a new ParameterizedCall to config.py in the chosen frame.

For example, to add a hyperparameter named **Base_Infectivity** that allows modification to the same-named EMOD-HIV 
config parameter in a frame named **baseline**:

1. Add the following new function to frames/baseline/config.py:

    ```python linenums="1"
    def modify_base_infectivity(config, Base_Infectivity: int = None):
        if Base_Infectivity is not None:
            config.parameters.Base_Infectivity = Base_Infectivity
    ```

2. In the same frames/baseline/config.py file, modify the function **get_config_parameterized_calls**
by adding lines similar to line 5 and 6 below.  Line 5 will create a ParameterizedCall object using
the new function and line 6 will add it to the list of config ParameterizedCalls.

    ```python linenums="1"
    def get_config_parameterized_calls(config: ReadOnlyDict) -> List[ParameterizedCall]:
        parameterized_calls = country_model.get_config_parameterized_calls(config=config)

        # Add any additional ParameterizedCalls here
        pc = ParameterizedCall(func=modify_base_infectivity, hyperparameters={'Base_Infectivity': None})
        parameterized_calls.append(pc)

        return parameterized_calls
    ```

    The hyperparameter named **Base_Infectivity** will now be available for use.

## Add additional campaign elements

To add a new campaign element (often an intervention), create and add an appropriate intervention 
object in a function and then add a new ParameterizedCall using it in the campaign.py of the chosen frame.

For example:

1. Assume you created a new frame using the **extend_frame** command and called it **hiv_vaccine**.

2. Add the following new function creating a vaccine intervention to frames/hiv_vaccine/campaign.py:

    ```python linenums="1"
    from emodpy_hiv.campaign.individual_intervention import ControlledVaccine
    from emodpy_hiv.campaign.distributor import add_intervention_triggered
    from emodpy_hiv.campaign.waning_config import Constant

    def add_hiv_vaccine(campaign: emod_api.campaign, vaccine_efficacy: float = 1.0):
        hiv_vaccine = ControlledVaccine(campaign=campaign,
                                        waning_config=Constant(constant_effect=vaccine_efficacy))
        add_intervention_triggered(campaign=campaign,
                                intervention_list=[hiv_vaccine],
                                triggers_list=["STIDebut"],
                                start_year=2030)
        return campaign
    ```

3. In the same frames/hiv_vaccine/campaign.py file, modify the function **get_campaign_parameterized_calls**
by adding lines similar to line 5 and 6 below.  Line 5 will create a ParameterizedCall object using
the new function and line 6 will add it to the list of campaign ParameterizedCalls.

    ```python linenums="1"
    def get_campaign_parameterized_calls(campaign: emod_api.campaign) -> List[ParameterizedCall]:
        parameterized_calls = source_frame.model.campaign_parameterizer(campaign=campaign)

        # Add any additional ParameterizedCalls here
        pc = ParameterizedCall(func=add_hiv_vaccine, hyperparameters={'vaccine_efficacy': None})
        parameterized_calls.append(pc)

        return parameterized_calls
    ```

    The hyperparameter named **vaccine_efficacy** will now be available for use.

---

## Replace a campaign or demographics element of a frame

To override an element of an EMOD-HIV campaign or demographics, create a Python subclass of the country model
you want to use and add overriding function(s) of the same name(s) to the country model functions you want to replace.

For example, creating a Python country model subclass named **ZambiaModified** using an alternate 
**add_state_TestingOnChild6w** function for the Zambia model campaign in frame **zambia_modified**. 

1. Use the **new_frame** command to create a fresh Zambia country model starting point
(see [Make a new frame](how_to_create_frame.md#make-a-new-frame)):

    ```bash
    python -m emodpy_workflow.scripts.new_frame --country Zambia --dest zambia_modified
    ```

2. Update the original Zambia country model import near the top:

    Replace the following line:

    ```python
    from emodpy_hiv.countries import Zambia as country_model
    ```

    with

    ```python
    from emodpy_hiv.countries import Zambia
    ```

3. Add the following new Zambia country model Python subclass in frames/zambia_modified/campaign.py containing the
desired override/replacement. The additional naming line at the end updates the rest of the file to use the new country
model.

    In this example, we are copy/pasting the original Zambia **add_state_TestingOnChild6w** function and modifying the 
    internal **child_testing_time_value_map** values to be two years earlier than the original:

    ```python linenums="1"
    class ZambiaModified(Zambia):
        @classmethod
        def add_state_TestingOnChild6w(cls,
                                    campaign: emod_api.campaign,
                                    node_ids: Union[List[int], None] = None):
            child_testing_start_year = 2002
            child_testing_time_value_map = {"Times": [2002, 2003, 2004, 2006, 2007],
                                            "Values": [0, 0.03, 0.1, 0.2, 0.3365]}
            disqualifying_properties = [coc.CascadeState.LOST_FOREVER,
                                        coc.CascadeState.ON_ART,
                                        coc.CascadeState.LINKING_TO_ART,
                                        coc.CascadeState.ON_PRE_ART,
                                        coc.CascadeState.LINKING_TO_PRE_ART,
                                        coc.CascadeState.ART_STAGING,
                                        coc.CascadeState.TESTING_ON_SYMPTOMATIC]
            property_restrictions = 'Accessibility:Yes'
            coc.add_state_TestingOnChild6w(campaign=campaign,
                                        disqualifying_properties=disqualifying_properties,
                                        time_value_map=child_testing_time_value_map,
                                        node_ids=node_ids,
                                        property_restrictions=property_restrictions,
                                        start_year=child_testing_start_year)

    country_model = ZambiaModified
    ```

    The frame **zambia_modified** now is identical to a Zambia country model frame but with the targeted section of the
    campaign replaced.

The process for replacing demographics elements is identical, but frames/zambia_modified/demographics.py is edited 
instead.

---

## Specify an ingest form for a frame

The way to specify the [ingest form](../reference/ingest_forms.md) to use for **all**
[frames](../reference/frames.md) in a project is by editing the **ingest_filename** attribute in its
**manifest.py** file.

For example:

```python linenums="1"
ingest_forms_dir = os.path.join(os.getcwd(), 'calibration', 'ingest_forms')
ingest_filename = os.path.join(ingest_forms_dir,
    'Zambia_calibration_ingest_form_2022-05-19__source__edited_for_calibration_testing--ALL_NODE.xlsm')
```

... sets the ingest file to use to be the file at path:

&lt;project_directory&gt;/calibration/ingest_forms/Zambia_calibration_ingest_form_2022-05-19__source__edited_for_calibration_testing--ALL_NODE.xlsm

To **override** this ingest_filename path **for a specific frame only** requires an edit to the chosen frame's EMOD_HIV
object specification in its \_\_init__.py file. Change "manifest.ingest_filename" below in your chosen frame to the
desired path:

```python linenums="1"
model = EMOD_HIV(
    manifest=manifest,
    config_initializer=config.initialize_config,
    config_parameterizer=config.get_config_parameterized_calls,
    demographics_initializer=demographics.initialize_demographics,
    demographics_parameterizer=demographics.get_demographics_parameterized_calls,
    campaign_initializer=campaign.initialize_campaign,
    campaign_parameterizer=campaign.get_campaign_parameterized_calls,
    ingest_form_path=manifest.ingest_filename,  # <-- change the value here for single-frame update only
    build_reports=config.build_reports
)
```

