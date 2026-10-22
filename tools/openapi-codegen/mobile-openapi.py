from __future__ import annotations

import json
from pathlib import Path
import sys


source, destination = map(Path, sys.argv[1:3])
spec = json.loads(source.read_text(encoding="utf-8"))
paths = {
    "/api/v1/alerts": {"get"},
    "/api/v1/alerts/{alert_id}/read": {"post"},
    "/api/v1/crops": {"get"},
}

for path in list(spec["paths"]):
    if path not in paths:
        del spec["paths"][path]
        continue
    for method in list(spec["paths"][path]):
        if method.lower() not in paths[path]:
            del spec["paths"][path][method]
            continue
        spec["paths"][path][method]["responses"].pop("422", None)

spec["components"]["schemas"] = {
    name: spec["components"]["schemas"][name]
    for name in (
        "AlertReadResponse",
        "AlertResponse",
        "CropListResponse",
    )
    if name in spec["components"]["schemas"]
}
destination.write_text(
    json.dumps(spec, indent=2, ensure_ascii=False) + "\n", encoding="utf-8"
)
