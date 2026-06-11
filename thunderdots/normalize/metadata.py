# -*- coding: utf-8 -*-

from __future__ import annotations
from typing import Any


MISSING = object()


def canonicalize_metadata_keys(src: dict[str, Any]) -> dict[str, Any]:
    """Canonicalize metadata keys by normalizing "dublinCore" to dublincore" and ensuring the structure is consistent.
    - If src is not a dict, return an empty dict.

    :param src: The input metadata dictionary to canonicalize
    :type src: dict[str, Any]
    :return: A new dictionary with canonicalized metadata keys
    :rtype: dict[str, Any]
    """

    if not isinstance(src, dict):
        return {}

    out = dict(src)

    if "dublincore" not in out and "dublinCore" in out:
        out["dublincore"] = out.pop("dublinCore")

    return out


def get_path(src: dict[str, Any], dotted_path: str) -> Any:
    """Get a value from a nested dictionary using a dotted path (e.g., "a.b.c").
    - If any part of the path is missing or not a dict, return None.

    :param src: The source dictionary to get the value from
    :type src: dict[str, Any]
    :param dotted_path: The dotted path string indicating the nested keys to access (e.g., "a.b.c")
    :type dotted_path: str
    :return: The value at the specified path, or None if the path is invalid
    :rtype: Any
    """
    cur: Any = src
    for part in dotted_path.split("."):
        if not isinstance(cur, dict) or part not in cur:
            return None
        cur = cur[part]
    return cur


def set_path(out: dict[str, Any], dotted_path: str, value: Any) -> None:
    """Set a value in a nested dictionary using a dotted path (e.g., "a.b.c").

    - Create intermediate dictionaries as needed.
    - Overwrite existing values if the path already exists.

    :param out: The output dictionary to set the value in
    :type out: dict[str, Any]
    :param dotted_path: The dotted path string indicating the nested keys to set (e.g
    "a.b.c")
    :type dotted_path: str
    :param value: The value to set at the specified path
    :type value: Any
    """
    cur = out
    parts = dotted_path.split(".")
    for part in parts[:-1]:
        cur = cur.setdefault(part, {})
    cur[parts[-1]] = value


def pick_keys(src: dict[str, Any], keys: list[str] | None) -> dict[str, Any]:
    """Pick selected paths from a nested dictionary based on a list of dotted paths.

    keys=None  -> keep everything
    keys=[]    -> keep nothing
    keys=[...] -> keep selected paths

    :param src: The source dictionary to pick values from
    :type src: dict[str, Any]
    :param keys: A list of dotted path strings indicating which paths to keep (e.g
    "a.b.c"), or None to keep all paths
    :type keys: list[str] | None
    :return: A new dictionary containing only the selected paths and their values
    :rtype: dict[str, Any]
    """
    if not isinstance(src, dict):
        return {}

    if keys is None:
        return dict(src)

    if not keys:
        return {}

    out: dict[str, Any] = {}
    for key in keys:
        value = get_path(src, key)
        if value is not None:
            set_path(out, key, value)
    return out


def build_metadata(
    raw_notice: dict[str, Any],
    *,
    metadata_dublincore: list[str] | None,
    metadata_extensions: list[str] | None,
) -> dict[str, Any]:
    """Build a normalized metadata dictionary from a raw notice, applying canonicalization and picking selected keys.

    :param raw_notice: The raw notice dictionary containing metadata to process
    :type raw_notice: dict[str, Any]
    :param metadata_dublincore: A list of dotted path strings indicating which dublincore paths to keep, or None to keep all
    :type metadata_dublincore: list[str] | None
    :param metadata_extensions: A list of dotted path strings indicating which extensions paths to keep, or None to keep all
    :type metadata_extensions: list[str] | None
    :return: A new dictionary containing the normalized metadata with selected dublincore and extensions paths
    :rtype: dict[str, Any]
    """
    raw_notice = canonicalize_metadata_keys(raw_notice)

    dc = raw_notice.get("dublincore") or {}
    ext = raw_notice.get("extensions") or {}

    metadata = {
        "dublincore": pick_keys(dc, metadata_dublincore),
        "extensions": pick_keys(ext, metadata_extensions),
    }

    return {key: value for key, value in metadata.items() if value}
