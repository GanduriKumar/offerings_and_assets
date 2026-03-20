from __future__ import annotations

import argparse
from datetime import datetime, timezone
from pathlib import Path
from xml.sax.saxutils import escape
import zipfile


ROOT = Path(__file__).resolve().parents[1]

PROFILES = {
    "finding_capture": {
        "headers": [
            "Section",
            "Finding To Capture",
            "Why It Matters",
            "Evidence / Observation",
            "Assessment View",
            "Notes / Gaps / Follow-Up",
        ],
        "sheet_names": ["Quickfire Findings", "Detailed Findings"],
        "widths": [30, 58, 42, 28, 20, 34],
        "why_map": {
            "Final Quickfire Readiness Check": "Confirms the Quickfire output is ready for synthesis and readout.",
            "Final Detailed Assessment Check": "Confirms the Detailed Assessment output is ready for synthesis and readout.",
        },
        "fallback_template": "Supports finding capture for {section}.",
        "default_source": ROOT / "docs/output/proposed/offerings/assets/Agentic_AI_Readiness_Assessment_Finding_Capture_Checklists.md",
        "default_target": ROOT / "docs/output/proposed/offerings/assets/Agentic_AI_Readiness_Assessment_Finding_Capture_Checklists.xlsx",
        "title": "Assessment Finding Capture Checklists",
    },
    "client_prep": {
        "headers": [
            "Section",
            "Checklist Item",
            "Why It Matters",
            "Client Owner",
            "Status",
            "Notes / Links / File Names",
        ],
        "sheet_names": ["Quickfire Checklist", "Detailed Checklist"],
        "widths": [28, 58, 44, 18, 14, 36],
        "why_map": {
            "Quickfire Completion Check": "Confirms the minimum inputs are in place before the assessment starts.",
            "Detailed Assessment Completion Check": "Confirms the minimum inputs are in place before the assessment starts.",
        },
        "fallback_template": "Supports preparation for {section}.",
        "default_source": ROOT / "docs/output/proposed/offerings/assets/Agentic_AI_Readiness_Assessment_Client_Preparation_Checklists.md",
        "default_target": ROOT / "docs/output/proposed/offerings/assets/Agentic_AI_Readiness_Assessment_Client_Preparation_Checklists.xlsx",
        "title": "Assessment Client Preparation Checklists",
    },
}


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Build a two-sheet checklist XLSX from markdown.")
    parser.add_argument("--profile", choices=sorted(PROFILES), default="finding_capture")
    parser.add_argument("--source", type=Path)
    parser.add_argument("--target", type=Path)
    parser.add_argument("--title")
    return parser.parse_args()


def parse_source(source: Path, profile: dict[str, object]) -> dict[str, list[tuple[str, str, str, str, str, str]]]:
    sheet_names = profile["sheet_names"]
    why_map = profile["why_map"]
    fallback_template = profile["fallback_template"]

    text = source.read_text(encoding="utf-8")
    lines = text.splitlines()
    mode = None
    section = None
    context = None
    rows = {sheet_names[0]: [], sheet_names[1]: []}

    for raw in lines:
        line = raw.strip()
        if line.startswith("## Section A."):
            mode = sheet_names[0]
            section = None
            context = None
            continue
        if line.startswith("## Section B."):
            mode = sheet_names[1]
            section = None
            context = None
            continue
        if not mode or not line or line.startswith("## ") or line.startswith("```"):
            continue
        if line.startswith("### "):
            section = line[4:].strip()
            context = None
            continue
        if line.startswith("- "):
            if section is None:
                raise ValueError(f"Found checklist item before a section heading in {source}")
            item = line[2:].strip()
            why = why_map.get(section, context or fallback_template.format(section=section.lower()))
            rows[mode].append((section, item, why, "", "", ""))
        else:
            context = line
    return rows


def col_name(n: int) -> str:
    out = ""
    while n:
        n, rem = divmod(n - 1, 26)
        out = chr(65 + rem) + out
    return out


def build_cols(widths: list[int]) -> str:
    return "".join(
        f'<col min="{idx}" max="{idx}" width="{width}" customWidth="1"/>'
        for idx, width in enumerate(widths, start=1)
    )


def sheet_xml(headers: list[str], widths: list[int], rows: list[tuple[str, ...]]) -> str:
    all_rows = [tuple(headers)] + rows
    xml_rows = []
    for r_idx, row in enumerate(all_rows, start=1):
        cells = []
        for c_idx, val in enumerate(row, start=1):
            ref = f"{col_name(c_idx)}{r_idx}"
            style = ' s="1"' if r_idx == 1 else ""
            cells.append(f'<c r="{ref}" t="inlineStr"{style}><is><t>{escape(str(val))}</t></is></c>')
        xml_rows.append(f'<row r="{r_idx}">' + "".join(cells) + "</row>")
    dim = f"A1:{col_name(len(headers))}{len(all_rows)}"
    return (
        '<?xml version="1.0" encoding="UTF-8" standalone="yes"?>'
        '<worksheet xmlns="http://schemas.openxmlformats.org/spreadsheetml/2006/main" '
        'xmlns:r="http://schemas.openxmlformats.org/officeDocument/2006/relationships">'
        f'<dimension ref="{dim}"/>'
        '<sheetViews><sheetView workbookViewId="0"><pane ySplit="1" topLeftCell="A2" activePane="bottomLeft" state="frozen"/></sheetView></sheetViews>'
        '<sheetFormatPr defaultRowHeight="18"/>'
        f'<cols>{build_cols(widths)}</cols>'
        '<sheetData>' + "".join(xml_rows) + "</sheetData>"
        f'<autoFilter ref="A1:{col_name(len(headers))}1"/>'
        "</worksheet>"
    )


def workbook_xml(sheet_names: list[str]) -> str:
    sheets = "\n".join(
        f'    <sheet name="{escape(name)}" sheetId="{idx}" r:id="rId{idx}"/>'
        for idx, name in enumerate(sheet_names, start=1)
    )
    return (
        '<?xml version="1.0" encoding="UTF-8" standalone="yes"?>\n'
        '<workbook xmlns="http://schemas.openxmlformats.org/spreadsheetml/2006/main" '
        'xmlns:r="http://schemas.openxmlformats.org/officeDocument/2006/relationships">\n'
        f"  <sheets>\n{sheets}\n  </sheets>\n</workbook>"
    )


def workbook_rels_xml(sheet_names: list[str]) -> str:
    relationships = [
        f'  <Relationship Id="rId{idx}" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/worksheet" Target="worksheets/sheet{idx}.xml"/>'
        for idx in range(1, len(sheet_names) + 1)
    ]
    relationships.append(
        f'  <Relationship Id="rId{len(sheet_names) + 1}" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/styles" Target="styles.xml"/>'
    )
    return (
        '<?xml version="1.0" encoding="UTF-8" standalone="yes"?>\n'
        '<Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships">\n'
        + "\n".join(relationships)
        + "\n</Relationships>"
    )


def content_types_xml(sheet_names: list[str]) -> str:
    overrides = [
        '  <Override PartName="/xl/workbook.xml" ContentType="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet.main+xml"/>'
    ]
    overrides.extend(
        f'  <Override PartName="/xl/worksheets/sheet{idx}.xml" ContentType="application/vnd.openxmlformats-officedocument.spreadsheetml.worksheet+xml"/>'
        for idx in range(1, len(sheet_names) + 1)
    )
    overrides.extend(
        [
            '  <Override PartName="/xl/styles.xml" ContentType="application/vnd.openxmlformats-officedocument.spreadsheetml.styles+xml"/>',
            '  <Override PartName="/docProps/core.xml" ContentType="application/vnd.openxmlformats-package.core-properties+xml"/>',
            '  <Override PartName="/docProps/app.xml" ContentType="application/vnd.openxmlformats-officedocument.extended-properties+xml"/>',
        ]
    )
    return (
        '<?xml version="1.0" encoding="UTF-8" standalone="yes"?>\n'
        '<Types xmlns="http://schemas.openxmlformats.org/package/2006/content-types">\n'
        '  <Default Extension="rels" ContentType="application/vnd.openxmlformats-package.relationships+xml"/>\n'
        '  <Default Extension="xml" ContentType="application/xml"/>\n'
        + "\n".join(overrides)
        + "\n</Types>"
    )


def app_xml(sheet_names: list[str]) -> str:
    title_parts = "".join(f"<vt:lpstr>{escape(name)}</vt:lpstr>" for name in sheet_names)
    return f"""<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<Properties xmlns="http://schemas.openxmlformats.org/officeDocument/2006/extended-properties" xmlns:vt="http://schemas.openxmlformats.org/officeDocument/2006/docPropsVTypes">
  <Application>Microsoft Excel</Application>
  <HeadingPairs><vt:vector size="2" baseType="variant"><vt:variant><vt:lpstr>Worksheets</vt:lpstr></vt:variant><vt:variant><vt:i4>{len(sheet_names)}</vt:i4></vt:variant></vt:vector></HeadingPairs>
  <TitlesOfParts><vt:vector size="{len(sheet_names)}" baseType="lpstr">{title_parts}</vt:vector></TitlesOfParts>
  <AppVersion>16.0300</AppVersion>
</Properties>"""


def core_xml(title: str) -> str:
    stamp = datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")
    return f"""<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<cp:coreProperties xmlns:cp="http://schemas.openxmlformats.org/package/2006/metadata/core-properties" xmlns:dc="http://purl.org/dc/elements/1.1/" xmlns:dcterms="http://purl.org/dc/terms/" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance">
  <dc:title>{escape(title)}</dc:title>
  <dc:creator>OpenAI Codex</dc:creator>
  <cp:lastModifiedBy>OpenAI Codex</cp:lastModifiedBy>
  <dcterms:created xsi:type="dcterms:W3CDTF">{stamp}</dcterms:created>
  <dcterms:modified xsi:type="dcterms:W3CDTF">{stamp}</dcterms:modified>
</cp:coreProperties>"""


def build_xlsx(target: Path, profile: dict[str, object], rows_by_sheet: dict[str, list[tuple[str, ...]]], title: str) -> None:
    sheet_names = profile["sheet_names"]
    headers = profile["headers"]
    widths = profile["widths"]

    root_rels = """<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships">
  <Relationship Id="rId1" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/officeDocument" Target="xl/workbook.xml"/>
  <Relationship Id="rId2" Type="http://schemas.openxmlformats.org/package/2006/relationships/metadata/core-properties" Target="docProps/core.xml"/>
  <Relationship Id="rId3" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/extended-properties" Target="docProps/app.xml"/>
</Relationships>"""
    styles = """<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<styleSheet xmlns="http://schemas.openxmlformats.org/spreadsheetml/2006/main">
  <fonts count="2">
    <font><sz val="11"/><color theme="1"/><name val="Aptos"/><family val="2"/></font>
    <font><b/><sz val="11"/><color rgb="FFFFFFFF"/><name val="Aptos"/><family val="2"/></font>
  </fonts>
  <fills count="3">
    <fill><patternFill patternType="none"/></fill>
    <fill><patternFill patternType="gray125"/></fill>
    <fill><patternFill patternType="solid"><fgColor rgb="FF0F6CBD"/><bgColor indexed="64"/></patternFill></fill>
  </fills>
  <borders count="2">
    <border><left/><right/><top/><bottom/><diagonal/></border>
    <border><left style="thin"><color rgb="FFD9E2EC"/></left><right style="thin"><color rgb="FFD9E2EC"/></right><top style="thin"><color rgb="FFD9E2EC"/></top><bottom style="thin"><color rgb="FFD9E2EC"/></bottom><diagonal/></border>
  </borders>
  <cellStyleXfs count="1"><xf numFmtId="0" fontId="0" fillId="0" borderId="0"/></cellStyleXfs>
  <cellXfs count="2">
    <xf numFmtId="0" fontId="0" fillId="0" borderId="1" xfId="0" applyBorder="1" applyAlignment="1"><alignment vertical="top" wrapText="1"/></xf>
    <xf numFmtId="0" fontId="1" fillId="2" borderId="1" xfId="0" applyFont="1" applyFill="1" applyBorder="1" applyAlignment="1"><alignment vertical="center" wrapText="1"/></xf>
  </cellXfs>
  <cellStyles count="1"><cellStyle name="Normal" xfId="0" builtinId="0"/></cellStyles>
</styleSheet>"""

    target.parent.mkdir(parents=True, exist_ok=True)
    with zipfile.ZipFile(target, "w", compression=zipfile.ZIP_DEFLATED) as zf:
        zf.writestr("[Content_Types].xml", content_types_xml(sheet_names))
        zf.writestr("_rels/.rels", root_rels)
        zf.writestr("docProps/core.xml", core_xml(title))
        zf.writestr("docProps/app.xml", app_xml(sheet_names))
        zf.writestr("xl/workbook.xml", workbook_xml(sheet_names))
        zf.writestr("xl/_rels/workbook.xml.rels", workbook_rels_xml(sheet_names))
        zf.writestr("xl/styles.xml", styles)
        for idx, sheet_name in enumerate(sheet_names, start=1):
            zf.writestr(f"xl/worksheets/sheet{idx}.xml", sheet_xml(headers, widths, rows_by_sheet[sheet_name]))


def main() -> None:
    args = parse_args()
    profile = PROFILES[args.profile]
    source = args.source or profile["default_source"]
    target = args.target or profile["default_target"]
    title = args.title or profile["title"]

    rows = parse_source(source, profile)
    build_xlsx(target, profile, rows, title)

    print(target)
    for sheet_name, values in rows.items():
        print(f"{sheet_name}: {len(values)}")


if __name__ == "__main__":
    main()
