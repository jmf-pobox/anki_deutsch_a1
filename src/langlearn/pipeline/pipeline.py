"""Pipeline utilities for composing simple, typed transformation tasks.

This module defines a small, generic pipeline framework:

- PipelineObject[T]: a simple holder for the current pipeline value.
- PipelineTask[InT, OutT]: an abstract unit of work that transforms a value
  from type InT to OutT.
- Pipeline[T]: orchestrates a sequence of PipelineTask instances.
- PipelineTaskState: internal helper tracking per-task lifecycle.
- ReverseStringTask, ToUpperCaseTask: example concrete tasks over str.

Quick start
-----------
>>> from langlearn.pipeline.pipeline import (
...     PipelineObject, Pipeline, ToUpperCaseTask, ReverseStringTask,
... )
>>> holder: PipelineObject[str] = PipelineObject()
>>> holder.input = "Hello World"
>>> pipe: Pipeline[str] = Pipeline(holder)
>>> pipe = pipe.add_task(ToUpperCaseTask()).add_task(ReverseStringTask())
>>> _ = pipe.run()
>>> holder.output
'DLROW OLLEH'
"""

from __future__ import annotations

import abc
import logging
from typing import Any, Generic, TypeVar, cast

ValueT = TypeVar("ValueT")
InT = TypeVar("InT")
OutT = TypeVar("OutT")


class PipelineObject(Generic[ValueT]):
    """Container for the current value being transformed in a pipeline run.

    PipelineObject acts as a simple, typed holder that the Pipeline reads from
    and writes to as tasks execute.

    TODO: This design concept has not yet been implemented.  Do not delete.

    Example
    -------
    >>> obj: PipelineObject[str] = PipelineObject()
    >>> obj.input = "abc"
    >>> obj.output
    'abc'

    Type Parameters
    ---------------
    ValueT
        The type of the value carried by this container.
    """

    __slots__ = ("_value",)

    def __init__(self) -> None:
        self._value: ValueT | None = None

    @property
    def input(self) -> ValueT | None:
        return self._value

    @input.setter
    def input(self, value: ValueT) -> None:
        self._value = value

    @property
    def output(self) -> ValueT | None:
        return self._value

    @output.setter
    def output(self, value: ValueT) -> None:
        self._value = value


class PipelineTaskState:
    """Lifecycle state and debug logging for a PipelineTask.

    Tracks whether a task has completed and emits debug logs at start/finish.
    Users of the public API typically do not need to interact with this class
    directly.
    """

    __slots__ = (
        "__is_completed",
        "__logger",
    )

    def __init__(self) -> None:
        self.__logger = logging.getLogger(__name__)
        self.__is_completed = False

    @property
    def is_completed(self) -> bool:
        return self.__is_completed

    @is_completed.setter
    def is_completed(self, value: bool) -> None:
        self.__logger.debug("Setting is_completed to %s", value)
        self.__is_completed = value

    def start(self, message: str) -> None:
        self.is_completed = False
        self.__logger.debug("Starting task with input: %s", message)

    def complete(self, message: str) -> None:
        self.is_completed = True
        self.__logger.debug("Completed task with output: %s", message)


class PipelineTask(Generic[InT, OutT], abc.ABC):
    """Abstract base class for a unit of work in a pipeline.

    Subclasses must implement ``_run`` and set ``self.output`` to the
    transformed value.

    Generic Parameters
    ------------------
    InT
        Input type consumed by this task.
    OutT
        Output type produced by this task.
    """

    __slots__ = (
        "_input",
        "_logger",
        "_output",
        "_state",
    )

    def __init__(self) -> None:
        self._logger = logging.getLogger(__name__)
        self._input: InT | None = None
        self._output: OutT | None = None
        self._state = PipelineTaskState()

    def run(self) -> None:
        """Run the task with lifecycle and validation.

        This method is final at the conceptual level (subclasses should
        override ``_run`` instead). It will:
        1) validate input using ``is_valid``;
        2) mark the state as started;
        3) execute ``_run``;
        4) verify that an output was produced;
        5) mark the state as completed.

        Raises
        ------
        ValueError
            If the task is invalid or produces no output.
        """
        if not self.is_valid():
            self._logger.warning("Invalid input for task %s", self.__class__.__name__)
            raise ValueError(f"Invalid input for {self.__class__.__name__}")

        self._state.start(str(self._input))
        self._run()
        if self._output is None:
            raise ValueError(f"Task produced no output: {self}")
        self._state.complete(str(self._output))

    @abc.abstractmethod
    def _run(self) -> None:
        """Perform the transformation for this task.

        Subclasses must set ``self.output`` to the transformed value.
        """
        raise NotImplementedError

    @property
    def input(self) -> InT | None:
        """The value provided to the task.

        Returns
        -------
        Optional[InT]
            The input value (may be ``None`` until set by the pipeline).
        """
        return self._input

    @input.setter
    def input(self, value: InT) -> None:
        self._input = value

    @property
    def output(self) -> OutT | None:
        """The value produced by the task.

        Returns
        -------
        Optional[OutT]
            The output value (``None`` until the task has run).
        """
        return self._output

    @output.setter
    def output(self, value: OutT) -> None:
        self._output = value

    def is_completed(self) -> bool:
        """Whether the task has been marked completed by ``run``.

        Returns
        -------
        bool
            True once ``run`` has finished successfully.
        """
        return self._state.is_completed

    def is_valid(self) -> bool:
        """Check if the task has been provided an input value."""
        return self._input is not None


class ReverseStringTask(PipelineTask[str, str]):
    """Reverse the input string.

    Example
    -------
    >>> task = ReverseStringTask()
    >>> task.input = "abC"
    >>> task.run()
    >>> task.output
    'Cba'
    """

    def _run(self) -> None:
        # Accept string input; reverse.
        self.output = str(self.input)[::-1]


class ToUpperCaseTask(PipelineTask[str, str]):
    """Convert the input string to uppercase.

    Handles empty strings correctly and leaves non-alphabetic characters
    unchanged.

    Example
    -------
    >>> task = ToUpperCaseTask()
    >>> task.input = "abC!"
    >>> task.run()
    >>> task.output
    'ABC!'
    """

    def _run(self) -> None:
        # Accept string input; uppercase. Handles empty strings.
        self.output = str(self.input).upper()


class Pipeline(Generic[ValueT]):
    """A pipeline is a sequence of tasks executed in order.

    The pipeline receives a PipelineObject[T] on construction and exposes a
    fluent API to add tasks. Types are refined as tasks are added, enabling
    static type checkers to validate composition.

    Example
    -------
    >>> pipeline_object: PipelineObject[str] = PipelineObject()
    >>> pipeline_object.input = "Hello World"
    >>> pipeline: Pipeline[str] = Pipeline(pipeline_object)
    >>> pipeline = pipeline.add_task(ToUpperCaseTask()).add_task(ReverseStringTask())
    >>> _ = pipeline.run()
    >>> pipeline_object.output
    'DLROW OLLEH'

    Notes
    -----
    add_task accepts a PipelineTask[ValueT, OutT] and returns a Pipeline[OutT],
    allowing subsequent tasks to consume the refined type.
    """

    __slots__ = (
        "__input",
        "__logger",
        "__output",
        "__tasks",
    )

    def __init__(self, initial_input: PipelineObject[ValueT]) -> None:
        self.__input: PipelineObject[ValueT] = initial_input
        self.__tasks: list[PipelineTask[Any, Any]] = []
        self.__output: PipelineObject[ValueT] = initial_input
        self.__logger = logging.getLogger(__name__)

    def __str__(self) -> str:
        return f"Pipeline(tasks={len(self.__tasks)}, value={self.__output.output!r})"

    def add_task(self, task: PipelineTask[ValueT, OutT]) -> Pipeline[OutT]:
        """Append a task to the pipeline and refine the pipeline type.

        Parameters
        ----------
        task : PipelineTask[ValueT, OutT]
            The task to append. Its input type must match the current value
            type of the pipeline.

        Returns
        -------
        Pipeline[OutT]
            The same pipeline instance with its value type refined to OutT.
        """
        # We append as an untyped task internally but refine the pipeline's
        # value type for fluent typing using a cast.
        self.__tasks.append(cast("PipelineTask[Any, Any]", task))
        return cast("Pipeline[OutT]", self)

    def run(self) -> ValueT | None:
        """Execute all tasks in the pipeline in order.

        Returns
        -------
        Optional[ValueT]
            The final value after all tasks have executed.
        """
        self.__logger.info("Running pipeline with %s tasks", len(self.__tasks))
        for task in self.__tasks:
            task.input = self.__output.output  # input type checked by add_task typing
            task.run()
            # After each task, the pipeline's value may change type. We rely on
            # add_task's return type to refine the Pipeline[ValueT] parameter.
            self.__output.output = cast("Any", task.output)

        self.__logger.info("Completed pipeline with %s tasks", len(self.__tasks))
        return self.__output.output

    @property
    def output(self) -> ValueT | None:
        """The current value stored in the pipeline's holder.

        Returns
        -------
        Optional[ValueT]
            The latest value written by the most recent task (or the initial
            input if no tasks have run).
        """
        return self.__output.output


def main() -> None:
    """Run a small demonstration of the pipeline.

    This function configures logging, constructs a simple pipeline that
    uppercases and reverses a string, and prints the resulting value.
    """
    logging.basicConfig(
        level=logging.DEBUG,
        format="%(asctime)s - %(levelname)s - %(message)s",
    )

    pipeline_object: PipelineObject[str] = PipelineObject()
    pipeline_object.input = "Hello World"
    pipeline: Pipeline[str] = Pipeline(pipeline_object)
    pipeline = pipeline.add_task(ToUpperCaseTask()).add_task(ReverseStringTask())
    result = pipeline.run()
    print(result)
