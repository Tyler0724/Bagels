import importlib
from types import SimpleNamespace

from bagels import config as bagels_config

if bagels_config.CONFIG is None:
    bagels_config.CONFIG = bagels_config.Config.get_default()

People = importlib.import_module("bagels.components.modules.people").People


def test_on_data_table_row_highlighted_updates_current_row():
    people = People()
    people.current_row = None

    event = SimpleNamespace(row_key=SimpleNamespace(value=42))
    people.on_data_table_row_highlighted(event)

    assert people.current_row == 42


def test_action_delete_person_without_selection_notifies(monkeypatch):
    people = People()
    called = {"notified": False}

    def fake_notify():
        called["notified"] = True

    monkeypatch.setattr(people, "_notify_no_select", fake_notify)
    people.current_row = None

    people.action_delete_person()

    assert called["notified"] is True


def test_action_edit_person_without_selection_notifies(monkeypatch):
    people = People()
    called = {"notified": False}

    def fake_notify():
        called["notified"] = True

    monkeypatch.setattr(people, "_notify_no_select", fake_notify)
    people.current_row = None

    people.action_edit_person()

    assert called["notified"] is True
