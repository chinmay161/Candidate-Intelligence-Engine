import pytest

from submission.pipeline_config import PipelineConfig
from submission.pipeline_runner import PipelineRunner


def test_pipeline_runner_missing_jd_path():
    config = PipelineConfig(jd_path=None, candidates_path="cands.jsonl")
    runner = PipelineRunner(config)
    result = runner.run()
    assert not result.success
    assert "jd_path not configured" in result.errors[0]


def test_pipeline_runner_missing_candidates_path(tmp_path):
    jd_file = tmp_path / "jd.txt"
    jd_file.write_text("dummy jd")
    config = PipelineConfig(jd_path=str(jd_file), candidates_path=None)
    runner = PipelineRunner(config)
    result = runner.run()
    assert not result.success
    assert "candidates_path not configured" in result.errors[0]
