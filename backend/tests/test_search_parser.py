import pytest
from datetime import datetime
from backend.app.core.search_parser import parse_search_query

def test_empty_query():
    res = parse_search_query("")
    assert res.is_empty is True

    res2 = parse_search_query("   ")
    assert res2.is_empty is True

def test_report_all():
    res = parse_search_query("alll")
    assert res.is_report_all is True

def test_bug_ids():
    res = parse_search_query("123")
    assert res.bug_ids == [123]

    res2 = parse_search_query("123, 456, 789")
    assert res2.bug_ids == [123, 456, 789]

def test_creator():
    res = parse_search_query("(15)")
    assert res.creator_id == 15

def test_assignee():
    res = parse_search_query("{8}")
    assert res.assignee_id == 8

def test_exclude_assignee():
    res = parse_search_query("!{8}")
    assert res.exclude_assignee_id == 8

def test_date_range():
    res = parse_search_query("{2026-01-01~2026-02-01}")
    assert res.time_start is not None
    assert res.time_end is not None
    assert res.time_start.year == 2026
    assert res.time_start.month == 1
    assert res.time_start.day == 1

def test_keyword():
    res = parse_search_query("登录弹窗遮挡")
    assert res.keyword == "登录弹窗遮挡"
