import importlib
from types import SimpleNamespace

import pytest

from bagels import config as bagels_config

if bagels_config.CONFIG is None:
    bagels_config.CONFIG = bagels_config.Config.get_default()

table_builder = importlib.import_module(
    "bagels.components.modules.records._table_builder"
)


@pytest.fixture(autouse=True)
def default_config(monkeypatch):
    """Ensure CONFIG is available for the module under test."""
    monkeypatch.setattr(
        table_builder, "CONFIG", bagels_config.Config.get_default()
    )


def test_get_flow_icon_respects_split_visibility():
    builder = table_builder.RecordTableBuilder()
    builder.show_splits = False

    income_icon = builder._get_flow_icon(recordHasSplits=True, is_income=True)
    expense_icon = builder._get_flow_icon(recordHasSplits=True, is_income=False)

    assert income_icon == "[green]=[/green]"
    assert expense_icon == "[red]=[/red]"


def test_format_record_fields_uses_self_amount_when_splits_hidden(monkeypatch):
    builder = table_builder.RecordTableBuilder()
    builder.show_splits = False

    record = SimpleNamespace(
        isTransfer=False,
        category=SimpleNamespace(color="BLUE", name="Dining Out"),
        amount=100.0,
        splits=[object()],
        id=1,
        account=SimpleNamespace(name="Primary", hidden=False),
    )

    monkeypatch.setattr(
        table_builder, "get_record_total_split_amount", lambda record_id: 60.0
    )

    category_string, amount_string, account_string = builder._format_record_fields(
        record, "FLOW"
    )

    assert amount_string == "FLOW 40.0"
    assert account_string == "Primary"
    assert "Dining Out" in category_string


def test_format_record_fields_handles_transfers_with_hidden_accounts():
    builder = table_builder.RecordTableBuilder()
    builder.show_splits = True

    record = SimpleNamespace(
        isTransfer=True,
        account=SimpleNamespace(name="Hidden Source", hidden=True),
        transferToAccount=SimpleNamespace(name="Savings", hidden=False),
        amount=250.0,
    )

    category_string, amount_string, account_string = builder._format_record_fields(
        record, "FLOW"
    )

    assert "[italic]Hidden Source[/italic]" in category_string
    assert "Savings" in category_string
    assert amount_string == 250.0
    assert account_string == "-"
