#!/usr/bin/env python3
"""Fingerprint → canonical fields for ARCA / vendor voucher text. Stdlib only.

Reference implementation for hermes-comprobantes-arca. Detection order and
column roles live in catalog.json; human anchors in layouts.md.
"""
from __future__ import annotations

import json
import re
import sys
from decimal import Decimal, InvalidOperation
from pathlib import Path

ROOT = Path(__file__).resolve().parent
CATALOG_PATH = ROOT / "catalog.json"

_RE_EJEMPLAR = re.compile(
    r"Fecha de Emisi[^\n\r]{0,40}[\n\r]{0,2}\s*(ORIGINAL|DUPLICADO|TRIPLICADO)",
    re.IGNORECASE,
)
_RE_CUIT_LABEL = re.compile(
    r"(?:C\.?\s*U\.?\s*I\.?\s*T\.?|CUIT)\s*:?\s*(\d{2}[\-\s]?\d{8}[\-\s]?\d|\d{11})",
    re.IGNORECASE,
)
_RE_CUIT_DASH = re.compile(r"(?<!\d)(\d{2})-(\d{8})-(\d)(?!\d)")
_RE_SUBTOTAL_PEGADO = re.compile(r"([\d.]+,\d{2})\s*Subtotal\s*:\s*\$?", re.I)
_RE_SUBTOTAL_LINE = re.compile(
    r"Subtotal(?:\s*\([^)]*\))?\s*:?\s*\$?\s*([\d.]+,\d{2})", re.I
)
_RE_PV_NRO = re.compile(
    r"Comp\.?\s*N(?:ro|umero|°|º)?\.?\s*:?\s*0*(\d+)\s+(\d+)", re.I
)
_RE_N_DASH = re.compile(r"N[°º]?\s*:\s*(\d{4,5})\s*[-/]\s*(\d{6,8})", re.I)
_RE_N_FACTURA = re.compile(r"N[°º]\s*(\d{4,5})\s*[-–]\s*(\d{6,8})", re.I)
_RE_DATE = re.compile(r"\b(\d{2}/\d{2}/\d{4})\b")
_RE_AMT_AR = re.compile(r"([\d.]+,\d{2})")
_RE_ORIGINAL_LINE = re.compile(r"(?m)^O\s*R\s*I\s*G\s*I\s*N\s*A\s*L\s*$", re.I)
_RE_DUPLICADO_LINE = re.compile(r"(?m)^D\s*U\s*P\s*L\s*I\s*C\s*A\s*D\s*O\s*$", re.I)

CANON = [
    "fecha_comprobante",
    "importe_total",
    "cuit_emisor",
    "nro_comprobante",
    "razon_social_emisor",
    "fecha_vencimiento",
    "domicilio_vendedor",
]


def load_catalog() -> dict:
    return json.loads(CATALOG_PATH.read_text(encoding="utf-8"))


def catalog_table(catalog: dict | None = None) -> str:
    catalog = catalog or load_catalog()
    req = catalog["canonical_required"]
    lines = [
        "| id | " + " | ".join(req) + " |",
        "| --- | " + " | ".join("---" for _ in req) + " |",
    ]
    for layout in catalog["layouts"]:
        cols = layout["columns"]
        cells = [layout["id"]]
        for name in req:
            cells.append(str(cols.get(name, "—")))
        lines.append("| " + " | ".join(cells) + " |")
    return "\n".join(lines)


def _empty(layout: str, errors: list[str]) -> dict:
    row = {
        "layout": layout,
        "fecha_comprobante": "",
        "fecha_status": "faltante",
        "importe_total": "",
        "importe_ancla": "",
        "cuit_emisor": "",
        "nro_comprobante": "",
        "razon_social_emisor": "",
        "fecha_vencimiento": "",
        "domicilio_vendedor": "",
        "cuit_comprador": "",
        "items": [],
        "errors": errors,
    }
    return row


def original_block_arca(text: str) -> str:
    matches = list(_RE_EJEMPLAR.finditer(text or ""))
    if not matches:
        return text or ""
    start = None
    for m in matches:
        if m.group(1).upper() == "ORIGINAL":
            start = m.start()
            break
    if start is None:
        start = matches[0].start()
    end = len(text)
    for m in matches:
        if m.start() <= start:
            continue
        if m.group(1).upper() in ("DUPLICADO", "TRIPLICADO"):
            end = m.start()
            break
    return text[start:end]


def original_block_suelto(text: str) -> str:
    m_or = _RE_ORIGINAL_LINE.search(text or "")
    if not m_or:
        return text or ""
    start = m_or.start()
    m_du = _RE_DUPLICADO_LINE.search(text[start + 8 :])
    end = start + 8 + m_du.start() if m_du else len(text)
    return text[start:end]


def _norm_cuit(raw: str) -> str:
    return re.sub(r"\D", "", raw or "")


def _join_nro(pv: str, nro: str) -> str:
    pv_d = re.sub(r"\D", "", pv or "") or "0"
    nro_d = re.sub(r"\D", "", nro or "") or "0"
    return "{0}-{1}".format(pv_d.zfill(5)[-5:], nro_d.zfill(8)[-8:])


def _parse_importe_ar(raw: str) -> str | None:
    if not raw:
        return None
    s = raw.strip()
    if not re.search(r",\d{2}$", s):
        return None
    return s


def _parse_importe_en_or_ar(raw: str) -> str | None:
    """236450.00 → 236450,00; 1.234,56 stays AR."""
    s = (raw or "").strip()
    if re.search(r",\d{2}$", s):
        return s
    m = re.fullmatch(r"(\d+)\.(\d{2})", s)
    if m:
        return "{0},{1}".format(m.group(1), m.group(2))
    return None


def _to_decimal(raw: str) -> Decimal | None:
    s = (raw or "").strip()
    if not s:
        return None
    try:
        if re.search(r",\d{2}$", s):
            return Decimal(s.replace(".", "").replace(",", "."))
        if re.fullmatch(r"\d+\.\d{2}", s):
            return Decimal(s)
        if re.fullmatch(r"\d+,\d{2,3}", s):
            return Decimal(s.replace(",", "."))
    except InvalidOperation:
        return None
    return None


def _mul_ok(qty: str, unit: str, sub: str, pct: str = "", imp: str = "") -> bool:
    q, u, s = _to_decimal(qty), _to_decimal(unit), _to_decimal(sub)
    if q is None or u is None or s is None:
        return False
    gross = q * u
    idec = _to_decimal(imp) if imp else Decimal("0")
    pdec = _to_decimal(pct) if pct else Decimal("0")
    if idec is None:
        idec = Decimal("0")
    if pdec is None:
        pdec = Decimal("0")
    if abs(gross - idec - s) <= Decimal("0.02"):
        return True
    if pdec != 0:
        if abs(gross * (Decimal("1") - pdec / Decimal("100")) - s) <= Decimal("0.02"):
            return True
    return abs(gross - s) <= Decimal("0.02") and idec == 0


def _item(
    codigo: str,
    producto: str,
    cantidad: str,
    u_medida: str,
    precio_unitario: str,
    subtotal: str,
    pct_bonificado: str = "",
    imp_bonif: str = "",
) -> dict:
    return {
        "codigo": codigo or "",
        "producto": (producto or "").strip(),
        "cantidad": cantidad or "",
        "u_medida": u_medida or "",
        "precio_unitario": precio_unitario or "",
        "pct_bonificado": pct_bonificado or "",
        "imp_bonif": imp_bonif or "",
        "subtotal": subtotal or "",
        "subtotal_ok": _mul_ok(
            cantidad, precio_unitario, subtotal, pct_bonificado, imp_bonif
        ),
    }


_RE_ARCA_UNIDADES = re.compile(
    r"(\d[\d.]*,\d{2})\s+(?:otras\s+)?unidades\s+(\d[\d.]*,\d{2})",
    re.I,
)
_RE_CUENTO_ITEM = re.compile(
    r"^([\d.]+),(\d{3})\s+(\d+,\d{3})\s*(\d+,\d{2})(\d+),(\d{3})(.+)\s+([\d.]+,\d{2})\s*$"
)
_RE_AMA_ITEM = re.compile(
    r"^(?:(\d{3,})\s+)?(\d+\.\d{2})\s+(.+?)\s+(\d+\.\d{2})\s+(\d+\.\d{2})(?:\d*)\s+(\d+\.\d{2})(?:\s+(\d+\.\d{2}))?\s*$"
)


def _flatten_unidades_wrap(block: str) -> str:
    """Keep 'unidades' between its two number columns even if the PDF wrapped."""
    t = block or ""

    def _join_antes(m: re.Match) -> str:
        otras = "otras " if m.group(2) else ""
        return "{0} {1}{2}".format(m.group(1), otras, m.group(3))

    t = re.sub(
        r"(\d[\d.]*,\d{2})\s+(otras)?\s*[\n\r]+\s*(unidades)\b",
        _join_antes,
        t,
        flags=re.I,
    )
    t = re.sub(
        r"\b(unidades)\s*[\n\r]+\s*(\d[\d.]*,\d{2})",
        r"\1 \2",
        t,
        flags=re.I,
    )
    return t


def _split_bonif_arca(qty: str, unit: str, amounts: list[str]) -> tuple[str, str, str]:
    """Return subtotal, pct_bonificado, imp_bonif. Extract order often: sub, % bonif, imp. bonif."""
    q, u = _to_decimal(qty), _to_decimal(unit)
    if q is None or u is None or not amounts:
        return "", "", ""
    gross = q * u
    ranked = sorted(
        enumerate(amounts),
        key=lambda iv: abs((_to_decimal(iv[1]) or Decimal("0")) - gross),
    )
    for i, sub in ranked:
        s = _to_decimal(sub)
        if s is None:
            continue
        leftovers = [a for j, a in enumerate(amounts) if j != i]
        if abs(gross - s) <= Decimal("0.02"):
            if len(leftovers) >= 2 and abs(_to_decimal(leftovers[1]) or Decimal("1")) <= Decimal(
                "0.02"
            ):
                return sub, leftovers[0], leftovers[1]
            return sub, "0,00", "0,00"
        for k, imp in enumerate(leftovers):
            others = [x for t, x in enumerate(leftovers) if t != k]
            pct = others[0] if others else ""
            if _mul_ok(qty, unit, sub, pct, imp):
                return sub, pct, imp
    return amounts[0], "", ""


def _subtotal_after_unit(rest: str, qty: str, unit: str) -> str:
    amounts = [m.group(0) for m in re.finditer(r"\d[\d.]*,\d{2}", rest or "")]
    sub, _, _ = _split_bonif_arca(qty, unit, amounts)
    if sub:
        return sub
    q, u = _to_decimal(qty), _to_decimal(unit)
    if q is None or u is None:
        return ""
    prod = (q * u).quantize(Decimal("0.01"))
    return format(prod, "f").replace(".", ",")


def parse_items_arca(block: str) -> list[dict]:
    items = []
    for ln in _flatten_unidades_wrap(block).splitlines():
        s = ln.strip()
        if re.search(r"TRANSPORTE\s*:", s, re.I):
            continue
        m = _RE_ARCA_UNIDADES.search(s)
        if not m:
            continue
        qty, unit = m.group(1), m.group(2)
        head = s[: m.start()].strip()
        hm = re.match(r"^(\d+)\s+(.+)$", head)
        if not hm:
            continue
        producto = hm.group(2).strip()
        amounts = [x.group(0) for x in re.finditer(r"\d[\d.]*,\d{2}", s[m.end() :])]
        sub, pct, imp = _split_bonif_arca(qty, unit, amounts)
        items.append(
            _item("", producto, qty, "unidades", unit, sub, pct, imp)
        )
    return items


def parse_items_cuento(block: str) -> list[dict]:
    items = []
    for ln in (block or "").splitlines():
        s = ln.strip()
        if re.search(r"Subtotal|Remito|General|Neto:", s, re.I):
            continue
        m = _RE_CUENTO_ITEM.match(s)
        if not m:
            continue
        unit = "{0},{1}".format(m.group(1), m.group(2)[:2])
        pct = m.group(3)
        if pct.endswith("0") and len(pct) > 4:
            pct = pct[:-1]
        qty = "{0},{1}".format(m.group(5), "00")
        desc = m.group(7).strip()
        sub = m.group(8)
        codigo = ""
        producto = desc
        m_code = re.search(r"^(.*?)(PAÑALES)$", desc, re.I)
        if m_code and m_code.group(1):
            producto = m_code.group(1).strip()
            codigo = m_code.group(2).upper()
        items.append(_item(codigo, producto, qty, "", unit, sub, pct, ""))
    return items


def parse_items_amasuno(text: str) -> list[dict]:
    items = []
    for ln in (text or "").splitlines():
        s = ln.strip()
        if re.search(r"transporte|cae:|total:|factura|cuit", s, re.I):
            continue
        m = _RE_AMA_ITEM.match(s)
        if not m:
            continue
        codigo = m.group(1) or ""
        qty = m.group(2)
        producto = m.group(3).strip()
        a, b = m.group(4), m.group(5)
        # corpus: cantidad, desc, subtotal, precio_unitario, iva
        if _mul_ok(qty, b, a):
            sub, unit = a, b
        elif _mul_ok(qty, a, b):
            sub, unit = b, a
        else:
            sub, unit = a, b
        dto = m.group(7) or ""
        items.append(
            _item(
                codigo,
                producto,
                _parse_importe_en_or_ar(qty) or qty,
                "",
                _parse_importe_en_or_ar(unit) or unit,
                _parse_importe_en_or_ar(sub) or sub,
                _parse_importe_en_or_ar(dto) or dto,
                "",
            )
        )
    return items


def is_cuento(text: str, source_name: str = "") -> bool:
    t = re.sub(r"\s+", " ", (text or "").lower())
    name = (source_name or "").lower()
    hits = 0
    if "fiscante" in t or "daniela guadalupe" in t:
        hits += 2
    if "subtotal general" in t and ("factura elect" in t or "fa c tu r a" in t):
        hits += 2
    if _RE_ORIGINAL_LINE.search(text or "") and not _RE_EJEMPLAR.search(text or ""):
        hits += 1
    if _RE_N_DASH.search(text or ""):
        hits += 1
    if "cuento" in name and "ada" in name:
        hits += 1
    return hits >= 2


def is_amasuno(text: str, source_name: str = "") -> bool:
    t = (text or "").lower()
    name = (source_name or "").lower()
    if "amasuno" in t or "amasuno" in name:
        return True
    if "fecha vencimiento cae" in t and re.search(r"n[°º]\s*\d+\s*[-–]\s*\d+", t, re.I):
        return True
    return False


def is_sdr(text: str, source_name: str = "") -> bool:
    t = (text or "").lower()
    name = (source_name or "").lower()
    if "resumen de cuenta" in t and "distribuidora sdr" in t:
        return True
    if name.startswith("sdr"):
        return "resumen de cuenta" in t
    return False


def is_arca(text: str) -> bool:
    t = text or ""
    if not _RE_EJEMPLAR.search(t):
        return False
    if not re.search(r"Subtotal|Importe\s+Total", t, re.I):
        return False
    if not (
        re.search(r"Comp\.?\s*N", t, re.I) or re.search(r"Punto\s+de\s+Venta", t, re.I)
    ):
        return False
    return True


def detect_layout(text: str, source_name: str = "") -> str:
    if not (text or "").strip():
        return "scan_sin_texto"
    if is_cuento(text, source_name):
        return "cuento_hadas_fiscante"
    if is_amasuno(text, source_name):
        return "amasuno_lauri"
    if is_sdr(text, source_name):
        return "sdr_resumen_cuenta"
    if is_arca(text):
        return "arca_estandar"
    return "layout_desconocido"


def _fecha_arca(block: str) -> tuple[str, str]:
    dates = []
    for m in _RE_DATE.finditer(block):
        ctx = block[max(0, m.start() - 80) : m.end() + 40]
        if re.search(r"Inicio\s+de\s+Actividades", ctx, re.I):
            continue
        if re.search(r"Vto\.?\s+de\s+CAE|Vencimiento\s+CAE", ctx, re.I):
            continue
        dates.append(m.group(1))
    if dates:
        return dates[0], "extraido"
    return "", "faltante"


def _fecha_vto_pago(text: str) -> str:
    """Payment due date only. Never CAE expiry."""
    for m in re.finditer(
        r"Fecha\s+(?:de\s+)?(?:vto\.?|vencimiento)\b",
        text or "",
        re.I,
    ):
        window = (text or "")[m.start() : m.start() + 120]
        if re.search(r"C\.?A\.?E", window, re.I):
            continue
        d = _RE_DATE.search(window)
        if d:
            return d.group(1)
    return ""


def _razon_amasuno(line: str) -> str:
    s = (line or "").strip()
    s = re.sub(r"^C(Renzo\b)", r"\1", s, flags=re.I)
    s = re.sub(r'["“”]?\s*A\s*\+\s*1\s*["“”]?', ' "A + 1"', s, flags=re.I)
    s = re.sub(r"\s+", " ", s).strip()
    return s


def _importe_arca(block: str) -> tuple[str, str]:
    wrap = list(
        re.finditer(
            r"([\d.]+,\d{2})\s*\n\s*\1\s*\n\s*Subtotal:\s*\$",
            block,
        )
    )
    if wrap:
        return wrap[-1].group(1), "importe_total_wrap"
    m = re.search(
        r"Importe\s+Total\s*:\s*\$?\s*([\d.]+,\d{2})", block, re.I
    )
    if m:
        return m.group(1), "importe_total_label"
    pegados = list(_RE_SUBTOTAL_PEGADO.finditer(block))
    if pegados:
        return _parse_importe_ar(pegados[-1].group(1)) or "", "subtotal_pegado"
    lined = [
        x
        for x in _RE_SUBTOTAL_LINE.finditer(block)
        if "TRANSPORTE" not in block[max(0, x.start() - 30) : x.start()].upper()
    ]
    if lined:
        val = _parse_importe_ar(lined[-1].group(1))
        return val or "", "subtotal_label"
    return "", ""


def parse_arca(text: str) -> dict:
    block = original_block_arca(text)
    errors: list[str] = []
    out = _empty("arca_estandar", errors)
    labeled = [_norm_cuit(m.group(1)) for m in _RE_CUIT_LABEL.finditer(block)]
    labeled = [c for c in labeled if len(c) == 11]
    out["cuit_comprador"] = labeled[0] if labeled else ""
    bare = []
    for ln in block.splitlines():
        s = ln.strip()
        if re.fullmatch(r"\d{11}", s):
            bare.append(s)
    for c in bare:
        if out["cuit_comprador"] and c == out["cuit_comprador"]:
            continue
        out["cuit_emisor"] = c
        break
    if out["cuit_emisor"] and out["cuit_emisor"] == out["cuit_comprador"]:
        errors.append("cuit_emisor_es_comprador")
        out["cuit_emisor"] = ""
    imp, ancla = _importe_arca(block)
    out["importe_total"] = imp or ""
    out["importe_ancla"] = ancla
    if not out["importe_total"]:
        errors.append("faltante_importe_total")
    m = _RE_PV_NRO.search(block)
    if m:
        out["nro_comprobante"] = _join_nro(m.group(1), m.group(2))
    else:
        errors.append("faltante_nro_comprobante")
    if len(out["cuit_emisor"]) != 11:
        errors.append("faltante_cuit_emisor")
    fecha, st = _fecha_arca(block)
    out["fecha_comprobante"] = fecha
    out["fecha_status"] = st
    if not fecha:
        errors.append("faltante_fecha_comprobante")
    out["fecha_vencimiento"] = _fecha_vto_pago(block)
    if not out["fecha_vencimiento"]:
        errors.append("fecha_vencimiento_unsupported")
    lines = block.splitlines()
    start = 0
    for i, ln in enumerate(lines[:12]):
        if re.search(r"ORIGINAL", ln, re.I):
            start = i + 1
            break
    razon = ""
    domicilio = ""
    for ln in lines[start : start + 10]:
        s = ln.strip()
        if not s:
            continue
        letters = [c for c in s if c.isalpha()]
        if not razon and len(letters) >= 3 and all(c.isupper() for c in letters) and not re.search(
            r"\d{5,}", s
        ):
            if re.match(r"^(FACTURA|CUIT|CONDICI|PUNTO|CODIGO)", s, re.I):
                continue
            razon = s
            continue
        if razon and not domicilio:
            if re.search(r"\d", s) or re.search(r"Acebal|Santa Fe", s, re.I):
                if not re.match(r"^\d{2}/\d{2}/\d{4}$", s):
                    domicilio = s
                    break
    out["razon_social_emisor"] = razon
    out["domicilio_vendedor"] = domicilio
    if not razon:
        errors.append("faltante_razon_social_emisor")
    if not domicilio:
        errors.append("faltante_domicilio_vendedor")
    out["items"] = parse_items_arca(block)
    if not out["items"]:
        errors.append("faltante_items")
    out["errors"] = errors
    return out


def parse_cuento(text: str) -> dict:
    block = original_block_suelto(text)
    errors: list[str] = []
    out = _empty("cuento_hadas_fiscante", errors)
    for m in _RE_CUIT_DASH.finditer(block):
        c = m.group(1) + m.group(2) + m.group(3)
        if c.startswith("27") and len(c) == 11:
            out["cuit_emisor"] = c
            break
    for ln in block.splitlines():
        s = ln.strip()
        if re.fullmatch(r"\d{11}", s) and s != out["cuit_emisor"]:
            out["cuit_comprador"] = s
            break
    m = _RE_N_DASH.search(block)
    if m:
        out["nro_comprobante"] = _join_nro(m.group(1), m.group(2))
    else:
        errors.append("faltante_nro_comprobante")
    lines = block.splitlines()
    for i, ln in enumerate(lines):
        if re.search(r"Subtotal\s+General\s*:", ln, re.I):
            m_same = re.search(r"Subtotal\s+General\s*:\s*([\d.]+,\d{2})", ln, re.I)
            if m_same:
                out["importe_total"] = _parse_importe_ar(m_same.group(1)) or ""
            if not out["importe_total"]:
                for j in range(i + 1, min(i + 4, len(lines))):
                    m_amt = _RE_AMT_AR.search(lines[j])
                    if m_amt:
                        out["importe_total"] = _parse_importe_ar(m_amt.group(1)) or ""
                        break
            out["importe_ancla"] = "subtotal_general"
            break
    if not out["importe_total"]:
        errors.append("faltante_importe_total")
        out["importe_ancla"] = ""
    if len(out["cuit_emisor"]) != 11:
        errors.append("faltante_cuit_emisor")
    for ln in block.splitlines():
        letters = re.sub(r"[^A-Za-z]", "", ln).upper()
        if "FISCANTE" in letters:
            out["razon_social_emisor"] = "Daniela Guadalupe Fiscante"
            break
    if not out["razon_social_emisor"]:
        errors.append("faltante_razon_social_emisor")
    compact = re.sub(r"\s+", "", block.upper())
    m_dom = re.search(r"GUEMES(\d+)", compact)
    if m_dom:
        out["domicilio_vendedor"] = "GUEMES {0}".format(m_dom.group(1))
    else:
        errors.append("faltante_domicilio_vendedor")
    header_dates = []
    for m in _RE_DATE.finditer(block):
        header_dates.append(m.group(1))
        if len(header_dates) >= 4:
            break
    # typical: inicio (2018), fecha comprobante (2026), then CAE vto later
    for d in header_dates:
        y = d.split("/")[-1]
        if y != "2018":
            out["fecha_comprobante"] = d
            out["fecha_status"] = "extraido"
            break
    if not out["fecha_comprobante"]:
        errors.append("faltante_fecha_comprobante")
        out["fecha_status"] = "faltante"
    out["fecha_vencimiento"] = _fecha_vto_pago(block)
    if not out["fecha_vencimiento"]:
        errors.append("fecha_vencimiento_unsupported")
    out["items"] = parse_items_cuento(block)
    if not out["items"]:
        errors.append("faltante_items")
    out["errors"] = errors
    return out


def parse_amasuno(text: str) -> dict:
    errors: list[str] = []
    out = _empty("amasuno_lauri", errors)
    # last ORIGINAL block ≈ full text (no DUPLICADO in corpus)
    lines = (text or "").splitlines()
    if lines:
        out["razon_social_emisor"] = _razon_amasuno(lines[0])
    if len(lines) > 1:
        out["domicilio_vendedor"] = lines[1].strip()
    cuits = [_norm_cuit(m.group(0)) for m in _RE_CUIT_DASH.finditer(text or "")]
    cuits = [c for c in cuits if len(c) == 11]
    if cuits:
        out["cuit_emisor"] = cuits[0]
        if len(cuits) > 1:
            out["cuit_comprador"] = cuits[1]
    m = _RE_N_FACTURA.search(text or "")
    if m:
        out["nro_comprobante"] = _join_nro(m.group(1), m.group(2))
    else:
        errors.append("faltante_nro_comprobante")
    m_f = re.search(r"Fecha:\s*(\d{2}/\d{2}/\d{4})", text or "", re.I)
    if m_f:
        out["fecha_comprobante"] = m_f.group(1)
        out["fecha_status"] = "extraido"
    else:
        errors.append("faltante_fecha_comprobante")
    out["fecha_vencimiento"] = _fecha_vto_pago(text or "")
    if not out["fecha_vencimiento"]:
        errors.append("fecha_vencimiento_unsupported")
    totals = re.findall(r"TOTAL:\s*([\d.]+)", text or "", re.I)
    if totals:
        out["importe_total"] = _parse_importe_en_or_ar(totals[-1]) or ""
        out["importe_ancla"] = "total_en"
    if not out["importe_total"]:
        errors.append("faltante_importe_total")
    if len(out["cuit_emisor"]) != 11:
        errors.append("faltante_cuit_emisor")
    if not out["razon_social_emisor"]:
        errors.append("faltante_razon_social_emisor")
    if not out["domicilio_vendedor"]:
        errors.append("faltante_domicilio_vendedor")
    out["items"] = parse_items_amasuno(text)
    if not out["items"]:
        errors.append("faltante_items")
    out["errors"] = errors
    return out


def parse_sdr(text: str) -> dict:
    errors: list[str] = []
    out = _empty("sdr_resumen_cuenta", errors)
    out["razon_social_emisor"] = "Distribuidora SDR"
    m_h = re.search(r"Hasta:\s*(\d{2}/\d{2}/\d{4})", text or "", re.I)
    if m_h:
        out["fecha_comprobante"] = m_h.group(1)
        out["fecha_status"] = "candidata"
    else:
        out["fecha_status"] = "faltante"
        errors.append("faltante_fecha_comprobante")
    m_imp = re.search(
        r"Resumen de Cuenta\s*\n\s*([\d.]+,\d{2})", text or "", re.I
    )
    if m_imp:
        out["importe_total"] = m_imp.group(1)
        out["importe_ancla"] = "primer_monto_resumen"
        out["fecha_status"] = out["fecha_status"] or "candidata"
    else:
        errors.append("faltante_importe_total")
    errors.append("cuit_emisor_unsupported")
    errors.append("nro_comprobante_unsupported")
    errors.append("fecha_vencimiento_unsupported")
    errors.append("domicilio_vendedor_unsupported")
    errors.append("items_unsupported")
    out["items"] = []
    out["errors"] = errors
    return out


def parse_voucher_text(text: str, source_name: str = "") -> dict:
    layout = detect_layout(text, source_name)
    if layout == "scan_sin_texto":
        return _empty(layout, ["scan_sin_texto"])
    if layout == "layout_desconocido":
        return _empty(layout, ["layout_desconocido"])
    if layout == "cuento_hadas_fiscante":
        return parse_cuento(text)
    if layout == "amasuno_lauri":
        return parse_amasuno(text)
    if layout == "sdr_resumen_cuenta":
        return parse_sdr(text)
    return parse_arca(text)


def main(argv: list[str]) -> int:
    if len(argv) >= 2 and argv[1] in ("--catalog", "--list"):
        print(catalog_table())
        return 0
    if len(argv) >= 2 and argv[1] == "--corpus":
        corpus = ROOT / "corpus"
        for path in sorted(corpus.rglob("*.txt")):
            if path.name.lower() == "readme.md":
                continue
            text = path.read_text(encoding="utf-8")
            out = parse_voucher_text(text, source_name=path.name)
            print("---", path.name)
            slim = {k: out[k] for k in ["layout"] + CANON + ["errors"]}
            slim["items_n"] = len(out.get("items") or [])
            slim["items"] = out.get("items") or []
            print(json.dumps(slim, ensure_ascii=False))
        return 0
    if len(argv) < 2:
        print(
            "uso: python parse_text.py <archivo.txt> | --catalog | --corpus",
            file=sys.stderr,
        )
        return 2
    path = Path(argv[1])
    text = path.read_text(encoding="utf-8")
    out = parse_voucher_text(text, source_name=path.name)
    json.dump(out, sys.stdout, ensure_ascii=False, indent=2)
    print()
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))
