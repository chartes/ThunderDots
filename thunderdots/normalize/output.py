# -*- coding: utf-8 -*-

"""output.py

Build the final output dict with filtered metadata and results.
"""

from __future__ import annotations
from typing import Any
from .metadata import build_metadata


def build_output(
    collections: list[tuple[dict, list[str]]],
    resources: list[dict[str, Any]],
    stats,
    version: str,
    collection_metadata_dublincore: list[str] | None = None,
    collection_metadata_extensions: list[str] | None = None,
) -> dict[str, Any]:
    """Build the final output dict with filtered metadata and results.

    :param collections: List of tuples (collection_data, parent_ids) to include in the output
    :type collections: list[tuple[dict, list[str]]]
    :param resources: List of processed resources with extracted fragments to include in the output
    :type resources: list[dict[str, Any]]
    :param stats: Stats object to include in the output metadata
    :type stats: Any
    :param version: ThunderDots version string to include in the output metadata
    :type version: str
    :param collection_metadata_dublincore: Optional list of dublincore metadata fields to include in the output (default: None for all)
    :type collection_metadata_dublincore: list[str] | None, optional
    :param collection_metadata_extensions: Optional list of extension metadata fields to include in the output (default: None for all)
    :type collection_metadata_extensions: list[str] | None, optional
    :return: Final output dictionary with filtered metadata and results
    :rtype: dict[str, Any]
    """
    filtered_collections = []
    for data, parents in collections:
        metadata = build_metadata(
            data,
            metadata_dublincore=collection_metadata_dublincore,
            metadata_extensions=collection_metadata_extensions,
        )

        filtered_collections.append(
            {
                "@id": data.get("@id"),
                "@type": data.get("@type"),
                "title": data.get("title"),
                "linked_parents": parents,
                "metadata": {k: v for k, v in metadata.items() if v},
                "member": [
                    {
                        "@id": m.get("@id"),
                        "@type": m.get("@type"),
                        "title": m.get("title"),
                    }
                    for m in (data.get("member") or [])
                ],
            }
        )
    return {
        "dtsVersion": "1-alpha",
        "type": "All",
        "meta": {"thunderdots_version": version, **stats.to_dict()},
        "collection_results": filtered_collections,
        "resource_results": resources,
    }
