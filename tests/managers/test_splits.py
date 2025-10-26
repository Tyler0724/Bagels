from datetime import datetime
from typing import Dict

import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from bagels.managers import splits
from bagels.models.account import Account
from bagels.models.database.db import Base
from bagels.models.person import Person
from bagels.models.record import Record
from bagels.models.split import Split


@pytest.fixture
def split_env() -> Dict[str, int]:
    """Provide an isolated in-memory database and base record/person data."""
    engine = create_engine("sqlite:///:memory:")
    Base.metadata.create_all(engine)

    original_session_factory = splits.Session
    splits.Session = sessionmaker(bind=engine)

    with splits.Session() as session:
        account = Account(
            name="Test Account",
            description="For split tests",
            beginningBalance=0.0,
            repaymentDate=None,
            hidden=False,
        )
        session.add(account)
        session.commit()
        session.refresh(account)

        person = Person(name="Alice")
        session.add(person)
        session.commit()
        session.refresh(person)

        record = Record(
            label="Groceries",
            amount=100.0,
            date=datetime.now(),
            accountId=account.id,
            account=account,
            isIncome=False,
            isTransfer=False,
        )
        session.add(record)
        session.commit()
        session.refresh(record)

        record_id = record.id
        person_id = person.id
        account_id = account.id

    yield {
        "record_id": record_id,
        "person_id": person_id,
        "account_id": account_id,
    }

    Base.metadata.drop_all(engine)
    splits.Session = original_session_factory


def _create_split(record_id: int, person_id: int, account_id: int, amount=50.0):
    return splits.create_split(
        {
            "recordId": record_id,
            "personId": person_id,
            "accountId": account_id,
            "amount": amount,
            "isPaid": False,
            "paidDate": None,
        }
    )


def test_create_split_persists_new_entry(split_env):
    new_split = _create_split(
        split_env["record_id"],
        split_env["person_id"],
        split_env["account_id"],
        amount=45.5,
    )

    assert new_split.id is not None
    assert new_split.amount == 45.5

    with splits.Session() as session:
        stored = session.get(Split, new_split.id)
        assert stored is not None
        assert stored.personId == split_env["person_id"]


def test_get_splits_by_record_id_returns_all_matches(split_env):
    _create_split(split_env["record_id"], split_env["person_id"], split_env["account_id"])
    _create_split(
        split_env["record_id"],
        split_env["person_id"],
        split_env["account_id"],
        amount=30.0,
    )

    results = splits.get_splits_by_record_id(split_env["record_id"])
    assert len(results) == 2
    assert {split.amount for split in results} == {50.0, 30.0}


def test_get_split_by_id_returns_split(split_env):
    created = _create_split(
        split_env["record_id"], split_env["person_id"], split_env["account_id"]
    )

    fetched = splits.get_split_by_id(created.id)
    assert fetched is not None
    assert fetched.id == created.id


def test_get_split_by_id_returns_none_for_missing(split_env):
    assert splits.get_split_by_id(9999) is None


def test_update_split_updates_attributes(split_env):
    created = _create_split(
        split_env["record_id"], split_env["person_id"], split_env["account_id"]
    )

    updated = splits.update_split(created.id, {"amount": 75.0, "isPaid": True})
    assert updated is not None

    with splits.Session() as session:
        stored = session.get(Split, created.id)
        assert stored.amount == 75.0
        assert stored.isPaid is True


def test_delete_split_removes_entry(split_env):
    created = _create_split(
        split_env["record_id"], split_env["person_id"], split_env["account_id"]
    )

    deleted = splits.delete_split(created.id)
    assert deleted is not None
    assert deleted.id == created.id

    with splits.Session() as session:
        assert session.get(Split, created.id) is None


def test_delete_splits_by_record_id_clears_all(split_env):
    _create_split(split_env["record_id"], split_env["person_id"], split_env["account_id"])
    _create_split(split_env["record_id"], split_env["person_id"], split_env["account_id"])

    splits.delete_splits_by_record_id(split_env["record_id"])

    with splits.Session() as session:
        remaining = (
            session.query(Split)
            .filter(Split.recordId == split_env["record_id"])
            .all()
        )
        assert remaining == []
