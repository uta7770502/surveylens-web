#!/usr/bin/env python3
"""Audit SurveyLens status metadata. Does not assert raw-row verification."""
import json
import pathlib
import sys

def audit(status):
    sources = {"pisa_records": status.get("pisa_records", 0),
               "piaac_records": status.get("piaac_records", 0),
               "core_microdata_records": status.get("core_microdata_records", 0)}
    issues = []
    for key, value in sources.items():
        if not isinstance(value, int) or value < 0:
            issues.append(f"{key}: invalid nonnegative integer")
    if not issues:
        reported = sum(sources.values())
        if reported != status.get("respondent_records_processed"):
            issues.append(f"source total {reported} != reported total {status.get('respondent_records_processed')}")
    if status.get("training_eligible_records", 0) > status.get("respondent_records_processed", 0):
        issues.append("training eligible exceeds total")
    return {"reported_source_counts": sources,
            "reported_total": status.get("respondent_records_processed"),
            "reported_training_eligible": status.get("training_eligible_records"),
            "raw_rows_verified": False,
            "predictive_accuracy_validated": False,
            "checks_passed": not issues,
            "issues": issues,
            "next_required": ["Locate original raw data files and provenance",
                              "Verify licenses, weights, dictionary and duplicates",
                              "Build task-relevant held-out validation dataset"]}

if __name__ == "__main__":
    source = pathlib.Path(sys.argv[1] if len(sys.argv) > 1 else "data/status.json")
    result = audit(json.loads(source.read_text(encoding="utf-8")))
    print(json.dumps(result, ensure_ascii=False, indent=2))
    sys.exit(0 if result["checks_passed"] else 1)
