# -*- coding: utf-8 -*-

"""dates.py

Functions for parsing and normalizing temporal metadata fields, especially those containing years or year ranges.
"""

from __future__ import annotations

import re
from typing import Any


YEAR_OR_RANGE_RE = re.compile(
    r"^\s*(?P<start>-?\d{1,4})(?P<start_approx>[~?])?"
    r"(?:/(?P<end>-?\d{1,4})?(?P<end_approx>[~?])?)?\s*$"
)


TEMPORAL_FIELDS = {
    "dublincore.date",
    "dublincore.created",
    "dublincore.issued",
    "dublincore.coverage",
    "extensions.dateCreated",
    "extensions.datePublished",
    "extensions.temporalCoverage",
}


TEMPORAL_KEYS = {
    "date",
    "created",
    "issued",
    "coverage",
    "temporal",
    "temporalCoverage",
    "dateCreated",
    "datePublished",
}


def _year_start_iso(year: int) -> str:
    """Convert a year to an ISO date string representing the start of that year.

    :param year: Year to convert.
    :type year: int
    :return: ISO date string representing the first day of the year.
    :rtype: str
    """
    return f"{year:04d}-01-01" if year >= 0 else str(year)


def _year_end_iso(year: int) -> str:
    """Convert a year to an ISO date string representing the end of that year.

    :param year: Year to convert.
    :type year: int
    :return: ISO date string representing the last day of the year.
    :rtype: str
    """
    return f"{year:04d}-12-31" if year >= 0 else str(year)


def parse_year_bounds(value: Any) -> tuple[int | None, int | None]:
    """Parse a year or year range from a value.

    Supported values include integer years, string years, and simple ranges such
    as ``1200/1499``.

    :param value: Value to parse.
    :type value: Any
    :return: Tuple containing start and end years when available.
    :rtype: tuple[int | None, int | None]
    """
    if value is None:
        return None, None

    if isinstance(value, int):
        return value, value

    if not isinstance(value, str):
        return None, None

    value = value.strip()
    if not value:
        return None, None

    match = YEAR_OR_RANGE_RE.match(value)
    if not match:
        return None, None

    start_raw = match.group("start")
    end_raw = match.group("end")

    start = int(start_raw) if start_raw is not None else None

    if "/" not in value:
        return start, start

    if end_raw is None:
        return start, None

    return start, int(end_raw)


def _is_temporal_field(full_key: str, key: str) -> bool:
    """Return True when a metadata field should be treated as temporal.

    :param full_key: Full dotted metadata path.
    :type full_key: str
    :param key: Local metadata key.
    :type key: str
    :return: True if the field is temporal, False otherwise.
    :rtype: bool
    """
    return full_key in TEMPORAL_FIELDS or key in TEMPORAL_KEYS


def flatten_temporal_metadata(
    data: dict[str, Any],
    *,
    prefix: str = "",
    include_unparsed_temporal_values: bool = True,
) -> dict[str, Any]:
    """Extract temporal metadata from a nested metadata dictionary.

    This function walks through a nested metadata dictionary and returns only
    temporal fields. For each temporal value that can be parsed as a year or
    year range, it adds ``_start``, ``_end``, ``_start_iso``, and ``_end_iso``
    fields.

    Non-temporal metadata fields are ignored.

    :param data: Nested metadata dictionary to inspect.
    :type data: dict[str, Any]
    :param prefix: Dotted path prefix used during recursion.
    :type prefix: str
    :param include_unparsed_temporal_values: Whether to keep temporal fields even when their values cannot be parsed as years.
    :type include_unparsed_temporal_values: bool
    :return: Dictionary containing only temporal metadata and parsed date bounds.
    :rtype: dict[str, Any]
    """
    temporal: dict[str, Any] = {}

    for key, value in data.items():
        full_key = f"{prefix}.{key}" if prefix else key

        if isinstance(value, dict):
            temporal.update(
                flatten_temporal_metadata(
                    value,
                    prefix=full_key,
                    include_unparsed_temporal_values=include_unparsed_temporal_values,
                )
            )
            continue

        if not _is_temporal_field(full_key, key):
            continue

        start, end = parse_year_bounds(value)

        if start is None and end is None:
            if include_unparsed_temporal_values:
                temporal[full_key] = value
            continue

        temporal[full_key] = value

        if start is not None:
            temporal[f"{full_key}_start"] = start
            temporal[f"{full_key}_start_iso"] = _year_start_iso(start)

        if end is not None:
            temporal[f"{full_key}_end"] = end
            temporal[f"{full_key}_end_iso"] = _year_end_iso(end)

    return temporal


def enrich_temporal_metadata(metadata: dict[str, Any]) -> dict[str, Any]:
    """Return temporal metadata enriched with parsed year bounds.

    Only temporal fields are returned. General descriptive metadata such as
    creators, publishers, titles, identifiers, and source records are excluded.

    :param metadata: Nested metadata dictionary to enrich.
    :type metadata: dict[str, Any]
    :return: Dictionary containing temporal metadata only.
    :rtype: dict[str, Any]
    """
    return flatten_temporal_metadata(metadata)
