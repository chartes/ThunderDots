#-*- coding: utf-8 -*-

"""models.py

Models for validation reports.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any


@dataclass(slots=True)
class ValidationIssue:
    """Represents a single validation issue found during the validation process."""
    level: str
    code: str
    message: str
    path: str | None = None
    expected: str | None = None
    actual: str | None = None


@dataclass(slots=True)
class ValidationReport:
    """Represents the validation report for a single resource, including whether it is valid and any issues found."""
    ok: bool
    issues: list[ValidationIssue] = field(default_factory=list)
    triple_count: int | None = None

    def to_dict(self) -> dict[str, Any]:
        """Convert the ValidationReport to a dictionary format, including the validation status, triple count, and a list of issues with their details."""
        return {
            "ok": self.ok,
            "triple_count": self.triple_count,
            "issues": [issue.__dict__ for issue in self.issues],
        }


@dataclass(slots=True)
class BatchValidationReport:
    """Represents a batch validation report for multiple resources, including a summary of the results and a list of individual validation reports."""
    reports: list[ValidationReport]

    def summary(self) -> dict[str, Any]:
        """Generate a summary of the batch validation results, including total resources, valid resources, invalid resources, and total issues found across all reports."""
        total = len(self.reports)
        valid = sum(1 for r in self.reports if r.ok)
        issues = sum(len(r.issues) for r in self.reports)
        return {
            "total": total,
            "valid": valid,
            "invalid": total - valid,
            "issues": issues,
        }
