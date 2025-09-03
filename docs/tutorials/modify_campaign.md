# Modify Campaign

## Campaign Basics
(Explain how the campaign is the main tool for controlling how the simulation changes over time)

The **campaign** is the primary mechanism in EMOD for introducing changes in the simulation over time. It defines when, where, and to whom interventions are delivered. Through campaigns, we simulate programmatic activities such as HIV testing, ART initiation, PrEP rollout, and more. Campaigns control behavior through event-based triggers, targeting criteria, and time-based schedules.
ToDo: add more information about campaigns.

## Cascade of Care in the HIV Health System
(Explain how it comes with “cascade of care” that includes a model of an HIV health system)

The **cascade of care (CoC)** in `emodpy-hiv` models the journey of individuals through the HIV care continuum. 
ToDo: add more infotmation for CoC.

## Create a baseline frame with no health system

To create a frame without a health system:

```bash
python -m hiv_workflow.scripts.extend_frame --source baseline --dest no_health_system
```

This copies the `baseline` configuration and allows you to remove or simplify the CoC logic in `no_health_system`.


## Run EMOD

```bash
python -m hiv_workflow.scripts.run -N NoHealthSystem -F no_health_system -o results/no_health_system -p ContainerPlatform
```

Todo: reference to previous "Run EMOD" section.

## Plot InsetChart and compare to baseline

Download the InsetChart from the `results/no_health_system` directory:

```bash
python -m emodpy_workflow.scripts.download -f output/InsetChart.json -r results/no_health_system/experiment_index.csv -p ContainerPlatform
```

Use the plotting tool to compare the output:

```bash
python -m emodpy_hiv.plotting.plot_inset_chart -d ./InsetChart -t "InsetChart-no_health_system" -o images
```

This helps assess how removing the health system affects prevalence, incidence, and other metrics.

**ToDo: Update titles for the following sections**
## Explain that sometimes you want to include a change in care without getting into the details of how it is delivered

You may want to simulate a **change in outcomes** (like introducing a vaccine) without modeling every step in the delivery system.
ToDo: TBD.

## Use extend_frame to create vaccine_using_tracker

```bash
python -m hiv_workflow.scripts.extend_frame --source baseline --dest vaccine_using_tracker
```

## Add a HIV Vaccine using reference tracker

Modify `campaign.py` to include a function that adds a vaccine intervention using the reference tracker. This example adds:
- a vaccine with efficacy = 100% starting in 1990, scaling up to 60% by 2005.
- targeting HIV-negative individuals only.

```python linenums="1"
from emodpy_hiv.campaign.individual_intervention import ControlledVaccine
from emodpy_hiv.campaign.distributor import add_intervention_reference_tracking
from emodpy_hiv.campaign.common import ValueMap
from emodpy_hiv.campaign.waning_config import Constant
from emodpy_hiv.utils.targeting_config import IsHivPositive


def add_hiv_vaccine(campaign, vaccine_efficacy=1.0):
    vaccine = ControlledVaccine(
        campaign=campaign,
        waning_config=Constant(constant_effect=vaccine_efficacy)
    )
    add_intervention_reference_tracking(
        campaign=campaign,
        intervention_list=[vaccine],
        time_value_map=ValueMap(times=[1990, 2005], values=[0, 0.6]), 
        tracking_config=~IsHivPositive(), 
        start_year=1990
    )
    return campaign
```
In campaign.py, add the following line in the appropriate place to call the function.

```python linenums="1"
def get_campaign_parameterized_calls(campaign):
    parameterized_calls = source_frame.model.campaign_parameterizer(campaign=campaign)
    # Add any additional ParameterizedCalls here
    pc = ParameterizedCall(func=add_hiv_vaccine, hyperparameters={'vaccine_efficacy': None})
    parameterized_calls.append(pc)
    return parameterized_calls
```

## Run EMOD

```bash
python -m hiv_workflow.scripts.run -N VaccineTracker -F vaccine_using_tracker -o results/vaccine_using_tracker -p ContainerPlatform
```
- Check that 'vaccine_efficacy' becomes a hyperparameters for Campaign. TBD
- Check that ControlledVaccine is added to campaign,.json. TBD

## Plot InsetChart, compare to baseline, and show prevalence drops but costs go up

Visualize results:

```bash
python -m emodpy_hiv.plotting.plot_inset_chart -d ./InsetChart -t "InsetChart-vaccine_using_tracker" -o images
```

ToDo: Add screenshots of InsetChart comparing baseline and vaccine_using_tracker, and show prevalence drops but costs go up

## i. Consider also plotting ReportHIVByAgeAndGender so you can look at prevalence across age groups

```bash
python -m emodpy_hiv.plotting.plot_hiv_by_age_and_gender ./ReportHIVByAgeAndGender/ -p prevalence -a -m -o images
```

## Explain that sometimes you want to change how the health system works in the future say by distributing the vaccine when a person sexually debuts

For more control, modify the health system logic directly. For example, distribute a vaccine only when a person becomes sexually active.

Instructions: TBD.

## Explain what a country model is and how subclassing it allows you to override functionality in it

A **country model** in `emodpy-hiv` encapsulates campaign logic specific to a setting (like Zambia).
Subclassing allows you to override methods like `add_state_HCTUptakeAtDebut()` to customize intervention logic.

ToDo: add more information about country models.

## Use extend_frame to create modified_coc

```bash
python -m hiv_workflow.scripts.extend_frame --source baseline --dest modified_coc
```

## In the modified_coc directory, create a country model subclass that overrides HCT Update at Debut and distributes the vaccine when they debut

Example `eswatini.py`:

```python linenums="1"
# import necessary modules
class Eswatini(Country):
    country_name = "eSwatini"

    @classmethod
    def add_state_HCTUptakeAtDebut(
        cls,
        campaign: emod_api.campaign,
        start_year: float,
        node_ids: list[int] = None
    ):
        disqualifying_properties = [
            coc.CascadeState.LOST_FOREVER,
            coc.CascadeState.ON_ART,
            coc.CascadeState.LINKING_TO_ART,
            coc.CascadeState.ON_PRE_ART,
            coc.CascadeState.LINKING_TO_PRE_ART,
            coc.CascadeState.ART_STAGING
        ]
        initial_trigger = coc.CustomEvent.STI_DEBUT
        hct_upate_at_debut_pv = coc.CascadeState.HCT_UPTAKE_AT_DEBUT

        # set up health care testing uptake at sexual debut by time
        # stop listing for STIDebut after 35 years.
        female_multiplier = 1.0
        duration = 365 * 35
        uptake_choice = HIVSigmoidByYearAndSexDiagnostic(
            campaign,
            year_sigmoid=Sigmoid(min=-0.005, max=0.05, mid=2005, rate=1),
            positive_diagnosis_event=coc.HCT_TESTING_LOOP_TRIGGER,
            negative_diagnosis_event=coc.HCT_UPTAKE_POST_DEBUT_TRIGGER_1,
            female_multiplier=female_multiplier,
            common_intervention_parameters=CommonInterventionParameters(
                disqualifying_properties=disqualifying_properties,
                new_property_value=hct_upate_at_debut_pv
            )
        )
        add_intervention_triggered(
            campaign,
            intervention_list=[uptake_choice],
            triggers_list=[initial_trigger],
            start_year=start_year,
            property_restrictions=PropertyRestrictions(
                individual_property_restrictions=[['Accessibility:Yes']]
            ),
            node_ids=node_ids,
            event_name='HCTUptakeAtDebut: state 0 (decision, sigmoid by year and sex)',
            duration=duration
        )

        # insert a long-lasting ControlledVaccine
        laprep_start_year = start_year + duration / 365
        vaccine = ControlledVaccine(
            campaign,
            waning_config=Constant(0.99),
            common_intervention_parameters=CommonInterventionParameters(
                disqualifying_properties=disqualifying_properties,
                new_property_value=hct_upate_at_debut_pv
            )
        )
        broadcast_event = BroadcastEvent(
            campaign=campaign,
            broadcast_event="Enter_Health_Care_System",
            CommonInterventionParameters(
                disqualifying_properties=disqualifying_properties,
                new_property_value=hct_upate_at_debut_pv
            )
        )
        add_intervention_triggered(
            campaign=campaign,
            intervention_list=[vaccine, broadcast_event],
            triggers_list=[initial_trigger],
            start_year=laprep_start_year,
            property_restrictions=PropertyRestrictions(
                individual_property_restrictions=[['Accessibility:Yes']]
            ),
            node_ids=node_ids,
            event_name='HCTUptakeAtDebut: LA-PrEP on STI Debut'
        )
        # distribute the SigmoidByYearAndSexDiagnostic intervention by Enter_Health_Care_System event
        add_intervention_triggered(
            campaign,
            intervention_list=[uptake_choice],
            triggers_list=["Enter_Health_Care_System"],
            start_year=laprep_start_year,
            property_restrictions=PropertyRestrictions(
                individual_property_restrictions=[['Accessibility:Yes']]
            ),
            node_ids=node_ids,
            event_name='HCTUptakeAtDebut: state 0 triggered by Enter_Health_Care_System after 2025'
        )
        return (
            coc.HCT_TESTING_LOOP_TRIGGER,  # return the trigger for the HCTTestingLoop state
            coc.HCT_UPTAKE_POST_DEBUT_TRIGGER_1
        ) new_property_value=hct_update_at_debut_pv))
```

- todo: make a new frame with this country model.

## Run EMOD

TBD

## Plot InsetChart and compare against baseline and the vaccine distributed by reference tracker

TBD

## Plot prevalence in ReportHIVByAgeAndGender across ages to see how it takes a while before we see prevalence drop in the older groups

TBD

