"""Behavior tests for batched album-item loading."""

from __future__ import annotations

from beets import dbcore
from beets.test.helper import BeetsTestCase


class TestItemsByAlbumIds(BeetsTestCase):
    def setUp(self):
        super().setUp()
        self.i1 = self.add_item(title="t1", artist="a", album="A1")
        self.i2 = self.add_item(title="t2", artist="a", album="A1")
        self.i3 = self.add_item(title="t3", artist="b", album="A2")
        self.album1 = self.lib.add_album([self.i1, self.i2])
        self.album2 = self.lib.add_album([self.i3])

    def test_groups_items_by_album_id(self):
        by_id = self.lib._items_by_album_ids(
            [self.album1.id, self.album2.id]
        )
        assert set(by_id) == {self.album1.id, self.album2.id}
        assert {i.id for i in by_id[self.album1.id]} == {
            self.i1.id,
            self.i2.id,
        }
        assert {i.id for i in by_id[self.album2.id]} == {self.i3.id}

    def test_includes_albums_with_no_items(self):
        orphan_id = self.album2.id
        self.i3.remove(with_album=False)
        by_id = self.lib._items_by_album_ids([orphan_id])
        assert by_id[orphan_id] == []

    def test_empty_album_id_list(self):
        assert self.lib._items_by_album_ids([]) == {}

    def test_update_album_mode_uses_one_item_query(self):
        statements: list[str] = []
        original = dbcore.db.Transaction.query

        def wrapped(self_tx, statement, subvals=()):
            statements.append(statement)
            return original(self_tx, statement, subvals)

        dbcore.db.Transaction.query = wrapped
        try:
            albums = list(self.lib.albums())
            statements.clear()
            by_id = self.lib._items_by_album_ids([a.id for a in albums])
            item_selects = [
                s
                for s in statements
                if s.lstrip().upper().startswith("SELECT")
                and "item_attributes" not in s
                and "IN (" in s
            ]
            assert len(item_selects) == 1
            assert sum(len(v) for v in by_id.values()) == 3
        finally:
            dbcore.db.Transaction.query = original
