# TODO: refactor/rename this file as the custom parameter API.
from inspect import getfullargspec
from typing import Callable, List, Dict, Any

from emodpy_hiv.parameterized_call import ParameterizedCall


class InvalidFunctionArgumentError(BaseException):
    pass


def _select_params(available, selection):
    # Returns sub-dict of available using values in selection as keys. Excludes all such keys not in selection.
    # Matching keys (in available) are get-ed not popped because we now allow 'parameter non-uniqueness' (reuse)
    return {parameter: available.get(parameter) for parameter in selection if parameter in available}


def _set_parameters(on: Any, parameters_to_set: Dict[str, Any], parameterized_calls: List[ParameterizedCall]):
    """
    Consumes user-exposed parameters and sets their values on the given object. This function is the write/execution
    component of the custom parameter API.
    Args:
        on: object to set parameter values on (type depends on context)
        parameters_to_set: a dict of key/value user-exposed model parameters that need to be set. Not all will
            necessarily be set during this invocation of set_parameters depending on the behavior of the model input
            building function(s) calling this method.
        parameterized_calls: a list of ParameterizedCall objects that represent the functions that need to be called
            to set the parameters on the object. Each ParameterizedCall object has a function, a set of labeled
            hyperparameters, and a set of fixed hyperparameters that are used to set the parameters on the object.

    Returns: None
    """
    # calls the given functions with their function-specific parameters, drawn from parameters_to_set,
    # defined by the function_arguments dict
    for pc in parameterized_calls:
        selected_params = _select_params(available=parameters_to_set,
                                         selection=pc.labeled_hyperparameters.keys())

        # we need to map from e.g. coverage--node1 to coverage because the ACTUAL ParameterizedCall function expects
        # coverage
        for parameter, value in selected_params.items():
            pc.set_labeled_hyperparameter(labeled_hyperparameter=parameter, value=value)

        # Now modify the provided object (on). "on" is passed as context to each successive ParameterizedCall.
        prepared_call = pc.prepare_call()
        prepared_call(on)


def build_parameterized_object(parameters_to_set: Dict[str, Any],
                               parameterized_calls: List[ParameterizedCall],
                               obj: Any = None,
                               initializer: Callable = None):
    if not ((obj is None) ^ (initializer is None)):
        raise ValueError('Set either obj or initializer, not both or neither.')

    if obj is None:
        obj = initializer()

    _set_parameters(on=obj, parameters_to_set=parameters_to_set,
                    parameterized_calls=parameterized_calls)

    return obj
