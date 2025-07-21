from abc import ABC, abstractmethod
from typing import Callable

from idmtools.entities.itask import ITask


class IModel(ABC):

    @abstractmethod
    def inputs_builder(self, random_run_number: bool) -> Callable:
        pass

    @abstractmethod
    def initialize_task(self) -> ITask:
        pass

    @abstractmethod
    def initialize_executable(self, **kwargs) -> None:
        pass
