#!/usr/bin/env python3
# SPDX-License-Identifier: MIT
"""Validate manifest examples and Phase 2A safety invariants."""

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
schema_path = ROOT / "schema/rp1-gpclk-compatibility-manifest-v1.schema.json"
example_path = ROOT / "schema/examples/unavailable-v1.json"
schema = json.loads(schema_path.read_text(encoding="utf-8"))
example = json.loads(example_path.read_text(encoding="utf-8"))


def validate_route_evidence(manifest):
    """Require every evidence record used by an entry to name that entry route."""
    for entry in manifest["entries"]:
        for evidence in entry["evidence"]:
            if entry["route"] not in evidence["routes"]:
                raise ValueError(
                    f"entry {entry['id']} uses evidence without route {entry['route']}"
                )

assert schema["$schema"].endswith("2020-12/schema")
assert schema["additionalProperties"] is False
assert schema["properties"]["defaultState"]["const"] == "Unavailable"
entry = schema["$defs"]["entry"]
assert entry["additionalProperties"] is False
assert set(schema["$defs"]["route"]["enum"]) == {"GPIO4", "GPIO20"}
assert set(schema["$defs"]["state"]["enum"]) == {
    "Qualified", "Experimental", "Compatible-unqualified", "Unavailable", "Rejected"
}
qualified = entry["allOf"][0]["then"]["properties"]
assert qualified["liveEligible"]["const"] is True
required_evidence = {item["$ref"] for item in qualified["evidence"]["allOf"]}
assert required_evidence == {
    "#/$defs/hasBuildEvidence",
    "#/$defs/hasClockDisabledEvidence",
    "#/$defs/hasTimingEvidence",
    "#/$defs/hasCleanupEvidence",
    "#/$defs/hasRecoveryEvidence",
    "#/$defs/hasRfEvidence",
}
assert entry["allOf"][1]["then"]["properties"]["liveEligible"]["const"] is False
assert example["schemaVersion"] == 1
assert example["defaultState"] == "Unavailable"
assert example["module"]["uapiAbi"] == 1
assert example["entries"] == []
validate_route_evidence(example)
try:
    validate_route_evidence({"entries": [{"id": "gpio20", "route": "GPIO20",
                                          "evidence": [{"routes": ["GPIO4"]}]}]})
except ValueError:
    pass
else:
    raise AssertionError("GPIO4-only evidence satisfied a GPIO20 entry")
validate_route_evidence({"entries": [{"id": "gpio20", "route": "GPIO20",
                                      "evidence": [{"routes": ["GPIO20"]}]}]})

try:
    import jsonschema
except ImportError:
    print("manifest schema: structural PASS (jsonschema unavailable)")
else:
    jsonschema.Draft202012Validator.check_schema(schema)
    jsonschema.validate(example, schema, format_checker=jsonschema.FormatChecker())
    invalid = json.loads(example_path.read_text(encoding="utf-8"))
    invalid["entries"] = [{"state": "Qualified", "liveEligible": False}]
    try:
        jsonschema.validate(invalid, schema)
    except jsonschema.ValidationError:
        pass
    else:
        raise AssertionError("Qualified manifest without eligibility/evidence passed")
    print("manifest schema: PASS")
