"""Behavior tests for cached Item/Album computed-field getters."""

from __future__ import annotations

from types import MappingProxyType

import pytest

from beets import plugins
from beets.library import Album, Item
from beets.test import _common
from beets.test.helper import TestHelper


class TestCachedFieldGetters(TestHelper):
    def test_item_getters_are_cached_and_immutable(self):
        first = Item._getters()
        second = Item._getters()
        assert first is second
        assert isinstance(first, MappingProxyType)
        with pytest.raises(TypeError):
            first["singleton"] = lambda _i: False  # type: ignore[index]

    def test_album_getters_are_cached_and_immutable(self):
        first = Album._getters()
        second = Album._getters()
        assert first is second
        assert isinstance(first, MappingProxyType)
        with pytest.raises(TypeError):
            first["path"] = lambda _a: b"/x"  # type: ignore[index]

    def test_builtin_computed_fields_still_work(self):
        item = _common.item()
        assert item.singleton is True
        assert "singleton" in item.keys(True)

    def test_invalidation_picks_up_new_plugin_field(self):
        calls = {"n": 0}

        def field_getters():
            calls["n"] += 1
            return {"plugin_foo": lambda _i: f"v{calls['n']}"}

        old = plugins.item_field_getters
        plugins.item_field_getters = field_getters
        try:
            plugins.clear_field_getter_cache()
            item = _common.item()
            assert item["plugin_foo"] == "v1"
            assert item["plugin_foo"] == "v1"
            assert calls["n"] == 1

            plugins.clear_field_getter_cache()
            assert item["plugin_foo"] == "v2"
            assert calls["n"] == 2
        finally:
            plugins.item_field_getters = old
            plugins.clear_field_getter_cache()
