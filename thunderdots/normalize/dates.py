#-*- coding: utf-8 -*-

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


def _year_start_iso(year: int) -> str:
    """Convert a year to an ISO date string representing the start of that year.

    :param year: The year to convert (e.g., 2020 or -500)
    :type year: int
    :return: An ISO date string representing the start of the year (e.g., "
2020-01-01" or "-500")
    :rtype: str
    """
    return f"{year:04d}-01-01" if year >= 0 else str(year)


def _year_end_iso(year: int) -> str:
    """Convert a year to an ISO date string representing the end of that year.

    :param year: The year to convert (e.g., 2020 or -500)
    :type year: int
    :return: An ISO date string representing the end of the year (e.g., "
2020-12-31" or "-500")
    :rtype: str
    """
    return f"{year:04d}-12-31" if year >= 0 else str(year)


def parse_year_bounds(value: Any) -> tuple[int | None, int | None]:
    """Parse a year or year range from a string or integer value.

    Supported formats:
- Integer year (e.g., 2020)
- String year (e.g., "2020")
- Year range (e.g., "2020/2021", "2020/", "/
2021")
- Approximate years with "~" or "?" (e.g., "2020~",
"2020?")

    :param value: The value to parse, which can be an integer, string, or None
    :type value: Any
    :return: A tuple (start_year, end_year) where each is an integer or
None if not specified or invalid
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


def flatten_temporal_metadata(
    data: dict[str, Any],
    *,
    prefix: str = "",
) -> dict[str, Any]:
    """Flatten a nested metadata dictionary, extracting temporal fields and adding start/end year keys.

    This function recursively flattens a nested dictionary of metadata, concatenating keys with dots. For any keys that match known temporal fields (e.g., "date", "created", "issued", "coverage"), it attempts to parse the value as a year or year range and adds additional keys for the start and end years, as well as their ISO date representations.

    :param data: The nested metadata dictionary to flatten
    :type data: dict[str, Any]
    :param prefix: The prefix to use for keys in the flattened dictionary (used for recursion
    :type prefix: str, optional
    :return: A flattened dictionary with temporal metadata enriched with start/end year keys
    :rtype: dict[str, Any]
    """
    flat: dict[str, Any] = {}
    for key, value in data.items():
        full_key = f"{prefix}.{key}" if prefix else key
        if isinstance(value, dict):
            flat.update(flatten_temporal_metadata(value, prefix=full_key))
            continue
        flat[full_key] = value
        if full_key in TEMPORAL_FIELDS or key in {"date", "created", "issued", "coverage"}:
            start, end = parse_year_bounds(value)
            if start is not None:
                flat[f"{full_key}_start"] = start
                flat[f"{full_key}_start_iso"] = _year_start_iso(start)
            if end is not None:
                flat[f"{full_key}_end"] = end
                flat[f"{full_key}_end_iso"] = _year_end_iso(end)
    return flat


def enrich_temporal_metadata(metadata: dict[str, Any]) -> dict[str, Any]:
    """Enrich metadata with temporal fields by flattening and parsing year information.

    This function takes a nested metadata dictionary, flattens it, and enriches it by parsing any temporal fields to extract start and end years, as well as their ISO date representations. It returns a new dictionary with the enriched metadata.

    :param metadata: The original nested metadata dictionary to enrich
    :type metadata: dict[str, Any]
    :return: A new dictionary with enriched temporal metadata
    :rtype: dict[str, Any]
    """
    return flatten_temporal_metadata(metadata)
