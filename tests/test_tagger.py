"""Tests for envdiff.tagger."""

import pytest

from envdiff.comparator import DiffResult
from envdiff.tagger import (
    TagConfig,
    TagResult,
    build_tag_config,
    tag_result,
)


@pytest.fixture
def sample_result() -> DiffResult:
    return DiffResult(
        missing_in_right=["DB_HOST", "DB_PORT"],
        missing_in_left=["REDIS_URL"],
        mismatched={"AWS_KEY": ("old", "new"), "LOG_LEVEL": ("DEBUG", "INFO")},
    )


@pytest.fixture
def config() -> TagConfig:
    return build_tag_config({
        "database": ["DB_*"],
        "aws": ["AWS_*"],
        "infra": ["DB_*", "REDIS_*"],
    })


def test_build_tag_config_stores_tags(config):
    assert "database" in config.tags
    assert "aws" in config.tags
    assert "infra" in config.tags


def test_tag_result_db_keys_get_database_tag(sample_result, config):
    tr = tag_result(sample_result, config)
    assert "database" in tr.tags_for("DB_HOST")
    assert "database" in tr.tags_for("DB_PORT")


def test_tag_result_aws_key_gets_aws_tag(sample_result, config):
    tr = tag_result(sample_result, config)
    assert "aws" in tr.tags_for("AWS_KEY")


def test_tag_result_redis_gets_infra_not_database(sample_result, config):
    tr = tag_result(sample_result, config)
    assert "infra" in tr.tags_for("REDIS_URL")
    assert "database" not in tr.tags_for("REDIS_URL")


def test_tag_result_log_level_untagged(sample_result, config):
    tr = tag_result(sample_result, config)
    assert tr.tags_for("LOG_LEVEL") == set()


def test_keys_for_tag_returns_correct_keys(sample_result, config):
    tr = tag_result(sample_result, config)
    db_keys = tr.keys_for_tag("database")
    assert "DB_HOST" in db_keys
    assert "DB_PORT" in db_keys
    assert "REDIS_URL" not in db_keys


def test_all_tags_returns_all_used_tags(sample_result, config):
    tr = tag_result(sample_result, config)
    tags = tr.all_tags()
    assert "database" in tags
    assert "aws" in tags
    assert "infra" in tags


def test_empty_result_produces_empty_tag_result():
    empty = DiffResult(missing_in_right=[], missing_in_left=[], mismatched={})
    config = build_tag_config({"database": ["DB_*"]})
    tr = tag_result(empty, config)
    assert tr.tagged == {}


def test_summary_no_keys_message():
    tr = TagResult(tagged={})
    assert tr.summary() == "No keys tagged."


def test_summary_lists_tags_and_counts(sample_result, config):
    tr = tag_result(sample_result, config)
    summary = tr.summary()
    assert "[database]" in summary
    assert "[aws]" in summary
