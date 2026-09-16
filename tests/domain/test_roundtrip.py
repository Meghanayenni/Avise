"""Serialise, deserialise, compare. Every model, driven from the sample registry."""

from __future__ import annotations

import inspect
import json

import pytest
from pydantic import ValidationError

import avise.domain as domain_package
from avise.domain.base import AviseModel
from tests.domain.factories import SAMPLES

parametrize_models = pytest.mark.parametrize(
    "model",
    sorted(SAMPLES, key=lambda m: m.__name__),
    ids=lambda m: m.__name__,
)


def declared_models() -> set[type[AviseModel]]:
    """Every concrete AviseModel declared under avise.domain."""
    import importlib
    import pkgutil

    found: set[type[AviseModel]] = set()
    for module_info in pkgutil.iter_modules(domain_package.__path__):
        module = importlib.import_module(f"avise.domain.{module_info.name}")
        for _, obj in inspect.getmembers(module, inspect.isclass):
            if (
                issubclass(obj, AviseModel)
                and obj is not AviseModel
                and obj.__module__.startswith("avise.domain")
                and not obj.__name__.startswith("_")
            ):
                found.add(obj)
    return found


def test_every_model_has_a_sample() -> None:
    """A model added without a sample leaves the round-trip test blind to it."""
    missing = sorted(model.__name__ for model in declared_models() - set(SAMPLES))
    assert not missing, f"no sample registered for: {missing}"


@parametrize_models
def test_round_trip_python(model: type[AviseModel]) -> None:
    instance = SAMPLES[model]()
    assert model.model_validate(instance.model_dump()) == instance


@parametrize_models
def test_round_trip_json(model: type[AviseModel]) -> None:
    instance = SAMPLES[model]()
    assert model.model_validate_json(instance.model_dump_json()) == instance


@parametrize_models
def test_json_mode_dump_is_json_serialisable(model: type[AviseModel]) -> None:
    """The API returns these; a dump that json cannot encode is a broken contract."""
    json.dumps(SAMPLES[model]().model_dump(mode="json"))


@parametrize_models
def test_unknown_fields_are_rejected(model: type[AviseModel]) -> None:
    """extra="forbid": a stray field is a contract mismatch, not something to drop."""
    payload = SAMPLES[model]().model_dump(mode="json")
    payload["definitely_not_a_field"] = "x"
    with pytest.raises(ValidationError):
        model.model_validate(payload)
