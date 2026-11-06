import csv
import io
from collections import defaultdict

RESOURCES = ["locations", "assets", "subnets", "ip-addresses"]


def preview_csv(file_obj, resource):
    """Stub: validate CSV rows without saving. Returns summary + per-row errors."""
    decoded = file_obj.read().decode("utf-8-sig")
    reader = csv.DictReader(io.StringIO(decoded))
    rows = list(reader)

    errors = []
    valid_count = 0
    for idx, row in enumerate(rows, start=1):
        if row:
            valid_count += 1
        else:
            errors.append({"row": idx, "column": "", "code": "validation_error", "message": "Baris kosong atau tidak valid."})

    return {
        "mode": "preview",
        "resource": resource,
        "summary": {"rows": len(rows), "valid": valid_count, "errors": len(errors)},
        "errors": errors,
        "created": 0,
    }


def commit_csv(file_obj, resource):
    """Stub: validate again then save all rows in one transaction. All-or-nothing."""
    result = preview_csv(file_obj, resource)
    if result["errors"]:
        return {
            "mode": "commit",
            "resource": resource,
            "summary": result["summary"],
            "errors": result["errors"],
            "created": 0,
            "error": "import_invalid",
        }
    result["mode"] = "commit"
    result["created"] = result["summary"]["valid"]
    return result
