#!/usr/bin/env python3
"""Run text fixtures against parse_text.py. Stdlib only. cwd-independent."""
from __future__ import annotations

import json
import sys
from pathlib import Path

from parse_text import catalog_table, load_catalog, parse_voucher_text

ROOT = Path(__file__).resolve().parent
FIXTURES = ROOT / "fixtures"
CASES = FIXTURES / "cases.json"


def _fail(msg: str) -> None:
    print("FAIL", msg, file=sys.stderr)


def main() -> int:
    catalog = load_catalog()
    ids = [L["id"] for L in catalog["layouts"]]
    if catalog["detection_order"] != ids:
        # order may list specials first; just require all ids present
        missing = [i for i in catalog["detection_order"] if i not in ids]
        extra = [i for i in ids if i not in catalog["detection_order"]]
        if missing or extra:
            _fail("catalog detection_order mismatch: {0} vs {1}".format(missing, extra))
            return 1
    for L in catalog["layouts"]:
        cols = L["columns"]
        for req in catalog["canonical_required"]:
            if req not in cols:
                _fail("{0} missing column {1}".format(L["id"], req))
                return 1

    cases = json.loads(CASES.read_text(encoding="utf-8"))
    failed = 0
    for case in cases:
        path = FIXTURES / case["file"]
        text = path.read_text(encoding="utf-8")
        got = parse_voucher_text(text, source_name=path.name)
        checks = [
            ("layout", case["layout"]),
            ("cuit_emisor", case.get("cuit_emisor", "")),
            ("importe_total", case.get("importe_total", "")),
            ("nro_comprobante", case.get("nro_comprobante", "")),
            ("fecha_comprobante", case.get("fecha_comprobante", "")),
            ("fecha_status", case.get("fecha_status", "")),
        ]
        for optional in (
            "cuit_comprador",
            "razon_social_emisor",
            "fecha_vencimiento",
            "domicilio_vendedor",
        ):
            if optional in case:
                checks.append((optional, case[optional]))
        for key, expected in checks:
            actual = got.get(key, "")
            if actual != expected:
                _fail(
                    "{0} {1}: expected {2!r} got {3!r}".format(
                        case["file"], key, expected, actual
                    )
                )
                failed += 1
        if "items" in case:
            if got.get("items") != case["items"]:
                _fail(
                    "{0} items: expected {1!r} got {2!r}".format(
                        case["file"], case["items"], got.get("items")
                    )
                )
                failed += 1
        print("ok", case["file"], got["layout"])
    print()
    print("Layouts conocidos:")
    print(catalog_table(catalog))
    if failed:
        print("{0} assertion(s) failed".format(failed), file=sys.stderr)
        return 1
    print("all passed")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
