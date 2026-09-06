"""Behavior tests for cached path-format query parsing."""

from __future__ import annotations

from unittest import mock

from beets.library import queries as library_queries
from beets.test import _common
from beets.test.helper import TestHelper
from beets.util import normpath as np


class TestCachedPathFormatQueries(TestHelper):
    def test_conditional_path_query_selects_template(self, setup):
        item = _common.item(self.lib)
        item.comp = True
        self.lib.directory = b"base"
        self.lib.path_formats = [
            ("comp:true", "comp/$title"),
            ("default", "other/$title"),
        ]
        assert item.destination() == np("base/comp/the title")

    def test_default_path_used_when_no_query_matches(self, setup):
        item = _common.item(self.lib)
        item.comp = False
        self.lib.directory = b"base"
        self.lib.path_formats = [
            ("comp:true", "comp/$title"),
            ("default", "other/$title"),
        ]
        assert item.destination() == np("base/other/the title")

    def test_parse_query_string_called_once_for_library_formats(self, setup):
        item = _common.item(self.lib)
        self.lib.directory = b"base"
        self.lib.path_formats = [
            ("comp:true", "comp/$title"),
            ("year:2001", "y/$title"),
            ("default", "other/$title"),
        ]
        with mock.patch(
            "beets.library.library.parse_query_string",
            wraps=library_queries.parse_query_string,
        ) as parsed:
            item.destination()
            item.destination()
            item.destination()
            # Two non-default queries, parsed once each across three calls.
            assert parsed.call_count == 2

    def test_explicit_path_formats_still_parse_each_call(self, setup):
        item = _common.item(self.lib)
        self.lib.directory = b"base"
        formats = [
            ("comp:true", "comp/$title"),
            ("default", "other/$title"),
        ]
        with mock.patch(
            "beets.library.models.parse_query_string",
            wraps=library_queries.parse_query_string,
        ) as parsed:
            item.destination(path_formats=formats)
            item.destination(path_formats=formats)
            assert parsed.call_count == 2

    def test_reassigned_path_formats_are_reparsed(self, setup):
        item = _common.item(self.lib)
        self.lib.directory = b"base"
        self.lib.path_formats = [("default", "one/$title")]
        assert item.destination() == np("base/one/the title")
        self.lib.path_formats = [("default", "two/$title")]
        assert item.destination() == np("base/two/the title")
