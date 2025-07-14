import unittest
from typing import List, Dict, Any

from emodpy_hiv.demographics.hiv_demographics import HIVDemographics
from emodpy_hiv.parameterized_call import ParameterizedCall

from emodpy_workflow.lib.utils.builders.general import _set_parameters


class MockDemographics(HIVDemographics):
    def __init__(self):
        # defaults
        self.a = 1
        self.b = 2
        self.c = 3
        self.d = 4


# A very simple function that accepts ANY parameters and sets them on the provided context object, providing that their
# values are not None.
def testing_func(demographics, **kwargs):
    for key, value in kwargs.items():
        if key is not None and value is not None:
            setattr(demographics, key, value)


class TestParameterizedCall(unittest.TestCase):
    def setUp(self) -> None:
        self.demographics = MockDemographics()

    def _check_values(self, obj: Any, check: Dict):
        for key, value in check.items():
            self.assertEqual(value, getattr(obj, key))

    def test_no_parameterized_calls_sets_nothing(self):
        pcs = []
        parameters = {'a': 11, 'b': 22}
        _set_parameters(on=self.demographics, parameters_to_set=parameters, parameterized_calls=pcs)
        self._check_values(obj=self.demographics, check={'a': 1, 'b': 2, 'c': 3, 'd': 4})

    def test_no_parameters_to_set_uses_pc_hyperparameter_defaults(self):
        pcs = [ParameterizedCall(func=testing_func, hyperparameters={'a': 11, 'b': 22})]
        parameters = {}
        _set_parameters(on=self.demographics, parameters_to_set=parameters, parameterized_calls=pcs)
        self._check_values(obj=self.demographics, check={'a': 11, 'b': 22, 'c': 3, 'd': 4})

    def test_parameters_to_set_override_everything(self):
        pcs = [ParameterizedCall(func=testing_func, hyperparameters={'a': 11, 'b': 22, 'c': None, 'd': None})]
        parameters = {'a': 111, 'd': 444}
        _set_parameters(on=self.demographics, parameters_to_set=parameters, parameterized_calls=pcs)
        self._check_values(obj=self.demographics, check={'a': 111, 'b': 22, 'c': 3, 'd': 444})


if __name__ == '__main__':
    unittest.main()
