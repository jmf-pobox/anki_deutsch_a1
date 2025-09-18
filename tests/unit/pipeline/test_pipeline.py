import logging

import pytest

from langlearn.core.pipeline.pipeline import (
    Pipeline,
    PipelineObject,
    PipelineTask,
    PipelineTaskState,
    ReverseStringTask,
    ToUpperCaseTask,
)


# -----------------------------
# Helpers for testing
# -----------------------------
class NoOutputTask(PipelineTask[str, str]):
    """A task that forgets to set output to trigger error handling."""

    def _run(self) -> None:  # pragma: no cover - behavior validated via run()
        # Intentionally do nothing so output remains None
        return


class EchoTask(PipelineTask[str, str]):
    """Simple task returning the same input (identity)."""

    def _run(self) -> None:
        assert self.input is not None
        self.output = self.input


# -----------------------------
# PipelineObject tests
# -----------------------------


def test_pipeline_object_input_output_aliasing() -> None:
    holder: PipelineObject[str] = PipelineObject()
    assert holder.input is None
    assert holder.output is None

    holder.input = "x"
    assert holder.input == "x"
    # output is the same underlying value
    assert holder.output == "x"

    holder.output = "y"
    assert holder.output == "y"
    assert holder.input == "y"


# -----------------------------
# PipelineTaskState tests
# -----------------------------


def test_task_state_start_complete_toggles(caplog: pytest.LogCaptureFixture) -> None:
    state = PipelineTaskState()
    with caplog.at_level(logging.DEBUG):
        state.start("in")
        assert state.is_completed is False
        state.complete("out")
        assert state.is_completed is True
    # Ensure debug logs emitted
    start_logged = any("Starting task" in rec.message for rec in caplog.records)  # type: ignore[unreachable]
    complete_logged = any("Completed task" in rec.message for rec in caplog.records)
    assert start_logged
    assert complete_logged


# -----------------------------
# PipelineTask base behavior
# -----------------------------


def test_task_run_raises_on_invalid_input() -> None:
    t = EchoTask()
    # input remains None -> invalid
    with pytest.raises(ValueError, match=r"Invalid input"):
        t.run()


def test_task_run_raises_when_no_output_set() -> None:
    t = NoOutputTask()
    t.input = "abc"
    with pytest.raises(ValueError, match=r"produced no output"):
        t.run()


def test_task_run_sets_state_completed() -> None:
    t = EchoTask()
    t.input = "abc"
    t.run()
    assert t.is_completed() is True
    assert t.output == "abc"


# -----------------------------
# Concrete task tests
# -----------------------------
@pytest.mark.parametrize(
    "value,expected",
    [
        ("", ""),
        ("abc", "ABC"),
        ("AbC!", "ABC!"),
        ("straße", "STRASSE"),
        ("ümlaut", "ÜMLAUT"),
        ("123", "123"),
    ],
)
def test_to_upper_case_task(value: str, expected: str) -> None:
    # Note: .upper() behavior is Python/Unicode-specific; we assert common cases
    task = ToUpperCaseTask()
    task.input = value
    task.run()
    assert task.output == expected


@pytest.mark.parametrize(
    "value,expected",
    [
        ("", ""),
        ("abc", "cba"),
        ("🙂👍", "👍🙂"),
        ("AbC!", "!CbA"),
    ],
)
def test_reverse_string_task(value: str, expected: str) -> None:
    task = ReverseStringTask()
    task.input = value
    task.run()
    assert task.output == expected


# -----------------------------
# Pipeline orchestration
# -----------------------------


def test_pipeline_sequencing_and_result() -> None:
    holder: PipelineObject[str] = PipelineObject()
    holder.input = "Hello"
    pipe: Pipeline[str] = Pipeline(holder)
    pipe = pipe.add_task(ToUpperCaseTask()).add_task(ReverseStringTask())
    result = pipe.run()
    assert result == "OLLEH"
    assert holder.output == "OLLEH"


def test_pipeline_no_tasks_is_noop() -> None:
    holder: PipelineObject[str] = PipelineObject()
    holder.input = "stay"
    pipe: Pipeline[str] = Pipeline(holder)
    result = pipe.run()
    # No tasks -> output remains the initial value
    assert result == "stay"
    assert holder.output == "stay"


def test_pipeline_propagates_task_errors() -> None:
    holder: PipelineObject[str] = PipelineObject()
    holder.input = "abc"
    pipe: Pipeline[str] = Pipeline(holder)
    pipe = pipe.add_task(NoOutputTask())
    with pytest.raises(ValueError, match=r"no output"):
        pipe.run()


# -----------------------------
# main() demonstration
# -----------------------------


def test_main_prints_result(capsys: pytest.CaptureFixture[str]) -> None:
    # Configure holder to known value and run the sample pipeline inside main
    import logging

    from langlearn.core.pipeline import pipeline as mod

    logging.getLogger(__name__)  # ensure logging import exercised

    mod.main()
    captured = capsys.readouterr().out.strip().splitlines()
    # Expect the demo to print the reversed uppercase of "Hello World"
    assert captured[-1] == "DLROW OLLEH"


def test_pipeline_output_property() -> None:
    """Test the output property of PipelineObject."""
    # Create a simple pipeline to test the output property
    pipeline_obj: PipelineObject[str] = PipelineObject()

    # Test that initial output is None (covers the missing line 345)
    assert pipeline_obj.output is None

    # Set input and verify output property
    pipeline_obj.input = "test_value"
    assert pipeline_obj.output == "test_value"
