"""Behavior tests for the items.path SQLite index."""

from __future__ import annotations

from beets.dbcore.query import MatchQuery
from beets.test.helper import BeetsTestCase


class TestItemPathIndex(BeetsTestCase):
    def test_index_created_on_library_open(self):
        rows = (
            self.lib._connection()
            .execute(
                "SELECT name FROM sqlite_master WHERE type='index' AND name=?",
                ("idx_item_path",),
            )
            .fetchall()
        )
        assert [row[0] for row in rows] == ["idx_item_path"]

    def test_exact_path_lookup_still_matches(self):
        item = self.add_item_fixture()
        item.path = b"/music/artist/album/track.mp3"
        item.store()
        results = list(self.lib.items(MatchQuery("path", item.path)))
        assert len(results) == 1
        assert results[0].id == item.id
