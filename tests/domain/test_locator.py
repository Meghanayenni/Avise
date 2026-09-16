"""Each locator kind accepts its own fields and rejects the others'."""

from __future__ import annotations

from uuid import uuid4

import pytest
from pydantic import BaseModel, ValidationError

from avise.domain.enums import LocatorKind
from avise.domain.locator import RecordField, RecordRow, SourceLocator, TextSpan


class Holder(BaseModel):
    """A stand-in for any model carrying a locator, so the union is exercised."""

    locator: SourceLocator


def test_text_span_round_trips() -> None:
    span = TextSpan(document_id=uuid4(), char_start=10, char_end=24)
    assert span.kind == LocatorKind.TEXT_SPAN
    assert span.length == 14
    assert Holder(locator=span).locator == span


def test_record_field_round_trips() -> None:
    locator = RecordField(record_id=uuid4(), field_name="caller_msisdn")
    assert Holder(locator=locator).locator == locator


def test_record_row_round_trips() -> None:
    locator = RecordRow(record_id=uuid4())
    assert Holder(locator=locator).locator == locator


def test_text_span_rejects_reversed_or_empty_range() -> None:
    for start, end in ((24, 10), (10, 10)):
        with pytest.raises(ValidationError):
            TextSpan(document_id=uuid4(), char_start=start, char_end=end)


def test_text_span_rejects_negative_offsets() -> None:
    with pytest.raises(ValidationError):
        TextSpan(document_id=uuid4(), char_start=-1, char_end=5)


def test_text_span_rejects_record_fields() -> None:
    """A CDR row has no character offsets, and a span has no field name."""
    with pytest.raises(ValidationError):
        TextSpan(document_id=uuid4(), char_start=0, char_end=5, field_name="caller")


def test_record_field_rejects_character_offsets() -> None:
    with pytest.raises(ValidationError):
        RecordField(record_id=uuid4(), field_name="amount", char_start=0, char_end=5)


def test_record_row_rejects_a_field_name() -> None:
    with pytest.raises(ValidationError):
        RecordRow(record_id=uuid4(), field_name="amount")


def test_record_field_requires_a_field_name() -> None:
    with pytest.raises(ValidationError):
        RecordField(record_id=uuid4(), field_name="")


def test_union_dispatches_on_kind() -> None:
    record_id = uuid4()
    holder = Holder.model_validate(
        {"locator": {"kind": "record_field", "record_id": str(record_id), "field_name": "tower_id"}}
    )
    assert isinstance(holder.locator, RecordField)
    assert holder.locator.field_name == "tower_id"


def test_unknown_kind_is_rejected() -> None:
    with pytest.raises(ValidationError):
        Holder.model_validate({"locator": {"kind": "page_number", "record_id": str(uuid4())}})


@pytest.mark.parametrize(
    "locator",
    [
        TextSpan(document_id=uuid4(), char_start=3, char_end=9),
        RecordField(record_id=uuid4(), field_name="amount"),
        RecordRow(record_id=uuid4()),
    ],
    ids=["text_span", "record_field", "record_row"],
)
def test_serialisation_always_keeps_the_discriminator(locator: object) -> None:
    """No serialiser flag may drop `kind` - a locator without it says nothing."""
    assert isinstance(locator, (TextSpan, RecordField, RecordRow))
    dumps = [
        locator.model_dump(),
        locator.model_dump(exclude_unset=True),
        locator.model_dump(exclude_none=True, exclude_defaults=False),
        locator.model_dump(mode="json"),
    ]
    for dumped in dumps:
        assert dumped["kind"] == locator.kind
    assert '"kind"' in locator.model_dump_json()
