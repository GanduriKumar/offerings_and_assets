from __future__ import annotations

import argparse
from dataclasses import dataclass
from html.parser import HTMLParser
from pathlib import Path
import re
import shutil
import subprocess
import sys


ROOT = Path(__file__).resolve().parents[1]
DEFAULT_SOURCE = ROOT / "docs/input/AI_Readiness_Opportunity_Assessment_Expanded_Potato_Mode.html"


@dataclass
class TopicBrief:
    raw_topic: str
    topic: str
    summary: str
    bullets: list[str]


def normalize_topic_heading(text: str) -> str:
    return re.sub(r"^\d+\.\s*", "", text).strip()


class SectionParser(HTMLParser):
    def __init__(self) -> None:
        super().__init__(convert_charrefs=True)
        self.items: list[tuple[str, str]] = []
        self._capture_tag: str | None = None
        self._buffer: list[str] = []

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        if tag in {"h2", "h3", "p", "li"}:
            self._capture_tag = tag
            self._buffer = []

    def handle_data(self, data: str) -> None:
        if self._capture_tag:
            self._buffer.append(data)

    def handle_endtag(self, tag: str) -> None:
        if self._capture_tag == tag:
            text = " ".join(part.strip() for part in self._buffer if part.strip())
            text = re.sub(r"\s+", " ", text).strip()
            if text:
                self.items.append((tag, text))
            self._capture_tag = None
            self._buffer = []


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Prepare an offering-generation request from a source HTML section.")
    parser.add_argument("--source", type=Path, default=DEFAULT_SOURCE, help="Source HTML file.")
    parser.add_argument("--section", required=True, help="Exact h2 section heading containing the product variants.")
    parser.add_argument("--topic", help="Exact h3 topic heading to generate.")
    parser.add_argument("--list-topics", action="store_true", help="List available topics in the section and exit.")
    parser.add_argument("--allow-replace", action="store_true", help="Allow regeneration if the full topic pack already exists.")
    parser.add_argument("--emit-brief", type=Path, help="Optional path to write the extracted topic brief as markdown.")
    parser.add_argument("--run", action="store_true", help="Invoke `codex exec` to run the generation workflow.")
    parser.add_argument("--codex-model", help="Optional model override passed to `codex exec`.")
    parser.add_argument("--output-last-message", type=Path, help="Optional file to store the last Codex message.")
    return parser.parse_args()


def slugify_topic(topic: str) -> str:
    slug = re.sub(r"[^A-Za-z0-9]+", "_", topic).strip("_")
    return re.sub(r"_+", "_", slug)


def expected_asset_paths(slug: str) -> list[Path]:
    offering_root = ROOT / "docs/output/proposed/offerings"
    assets_root = offering_root / "assets"
    return [
        offering_root / f"{slug}_Offering.md",
        offering_root / f"{slug}_Offer_Poster.html",
        offering_root / f"{slug}_Executive_Deck_Polished.html",
        assets_root / f"{slug}_Delivery_Guide.md",
        assets_root / f"{slug}_Delivery_Guide.html",
        assets_root / f"{slug}_Client_Report_Templates.md",
        assets_root / f"{slug}_Client_Preparation_Checklists.md",
        assets_root / f"{slug}_Client_Preparation_Checklists.xlsx",
        assets_root / f"{slug}_Finding_Capture_Checklists.md",
        assets_root / f"{slug}_Finding_Capture_Checklists.xlsx",
        assets_root / f"{slug}_Process_Infographic.html",
    ]


def parse_source(source: Path) -> list[tuple[str, str]]:
    parser = SectionParser()
    parser.feed(source.read_text(encoding="utf-8"))
    return parser.items


def get_section_items(items: list[tuple[str, str]], section_heading: str) -> list[tuple[str, str]]:
    in_section = False
    section_items: list[tuple[str, str]] = []
    for tag, text in items:
        if tag == "h2":
            if text == section_heading:
                in_section = True
                continue
            if in_section:
                break
        if in_section:
            section_items.append((tag, text))
    return section_items


def extract_topics(section_items: list[tuple[str, str]]) -> list[TopicBrief]:
    topics: list[TopicBrief] = []
    current_topic: str | None = None
    summary: str | None = None
    bullets: list[str] = []

    def flush() -> None:
        nonlocal current_topic, summary, bullets
        if current_topic:
            topics.append(TopicBrief(current_topic, normalize_topic_heading(current_topic), summary or "", bullets[:]))
        current_topic = None
        summary = None
        bullets = []

    for tag, text in section_items:
        if tag == "h3":
            flush()
            current_topic = text
        elif current_topic and tag == "p" and summary is None:
            summary = text
        elif current_topic and tag == "li":
            bullets.append(text)
    flush()
    return topics


def full_pack_status(slug: str) -> tuple[str, list[Path]]:
    expected = expected_asset_paths(slug)
    missing = [path for path in expected if not path.exists()]
    if not missing:
        return "exists", missing
    if len(missing) == len(expected):
        return "missing", missing
    return "partial", missing


def brief_markdown(source: Path, section: str, brief: TopicBrief, slug: str, status: str, missing: list[Path]) -> str:
    lines = [
        f"# Offering Generation Brief: {brief.topic}",
        "",
        f"- Source file: `{source}`",
        f"- Source section: `{section}`",
        f"- Topic: `{brief.topic}`",
        f"- Slug: `{slug}`",
        f"- Existing-pack status: `{status}`",
        "",
        "## Summary",
        brief.summary or "_No summary extracted._",
        "",
        "## Source Bullets",
    ]
    if brief.bullets:
        lines.extend(f"- {item}" for item in brief.bullets)
    else:
        lines.append("- _No bullets extracted._")
    if missing:
        lines.extend(["", "## Missing Files"])
        lines.extend(f"- `{path.relative_to(ROOT)}`" for path in missing)
    return "\n".join(lines) + "\n"


def build_prompt(source: Path, section: str, topic: str, allow_replace: bool) -> str:
    action = "regenerate and replace assets for" if allow_replace else "generate the full offering asset set for"
    return (
        f'Use the offering asset generator to {action} "{topic}" from the "{section}" section '
        f'in `{source.as_posix()}`.'
    )


def build_exec_prompt(source: Path, section: str, brief: TopicBrief, slug: str, allow_replace: bool) -> str:
    action = "Regenerate and replace the full asset set" if allow_replace else "Generate the full asset set"
    bullets = "\n".join(f"- {item}" for item in brief.bullets) or "- No source bullets extracted."
    replacement_line = (
        "Replacement of existing assets has been explicitly approved for this topic."
        if allow_replace
        else "Only generate if the topic pack is missing; do not replace existing assets."
    )
    return f"""Use the offering asset generator agent and the offering asset packager skill to complete this task.

{action} for the topic "{brief.topic}".

Source:
- file: `{source.as_posix()}`
- section: `{section}`
- topic heading: `{brief.raw_topic}`
- slug: `{slug}`

Extracted brief:
- summary: {brief.summary}
- source bullets:
{bullets}

Rules:
- Produce the full standard offering asset set under `docs/output/proposed/offerings`.
- HTML assets must be handcrafted.
- Use Google brand colors in refreshed HTML assets.
- Keep buyer-facing language client-facing.
- Regenerate dependent checklist xlsx files from markdown.
- {replacement_line}

Validate the finished asset set before stopping and summarize what changed.
"""


def run_codex(prompt: str, model: str | None, output_last_message: Path | None) -> int:
    codex_executable = shutil.which("codex.cmd") or shutil.which("codex")
    if not codex_executable:
        raise FileNotFoundError("Could not locate codex CLI on PATH.")

    command = [codex_executable, "exec", "--full-auto", "-C", str(ROOT)]
    if model:
        command.extend(["--model", model])
    if output_last_message:
        command.extend(["--output-last-message", str(output_last_message.resolve())])
    command.append("-")
    result = subprocess.run(command, input=prompt, text=True, cwd=ROOT)
    return result.returncode


def main() -> int:
    args = parse_args()
    source = args.source.resolve()
    if not source.exists():
        print(f"Source file not found: {source}", file=sys.stderr)
        return 1

    items = parse_source(source)
    section_items = get_section_items(items, args.section)
    if not section_items:
        print(f'Section not found: "{args.section}"', file=sys.stderr)
        return 1

    topics = extract_topics(section_items)
    if not topics:
        print(f'No topics found under section "{args.section}"', file=sys.stderr)
        return 1

    if args.list_topics:
        for brief in topics:
            slug = slugify_topic(brief.topic)
            status, _ = full_pack_status(slug)
            print(f"{brief.topic} [{status}]")
        return 0

    if not args.topic:
        print("--topic is required unless --list-topics is used.", file=sys.stderr)
        return 1

    wanted = normalize_topic_heading(args.topic)
    match = next((brief for brief in topics if brief.topic == wanted or brief.raw_topic == args.topic), None)
    if not match:
        print(f'Topic not found: "{args.topic}"', file=sys.stderr)
        return 1

    slug = slugify_topic(match.topic)
    status, missing = full_pack_status(slug)

    if args.emit_brief:
        target = args.emit_brief.resolve()
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text(brief_markdown(source, args.section, match, slug, status, missing), encoding="utf-8")

    print(f"Topic: {match.topic}")
    print(f"Slug: {slug}")
    print(f"Status: {status}")
    print(f"Source section: {args.section}")
    print(f"Summary: {match.summary}")
    print("Bullets:")
    for bullet in match.bullets:
        print(f"- {bullet}")
    print()

    if status == "exists" and not args.allow_replace:
        print("The full asset pack already exists for this topic.")
        print("Explicit user permission is required before regenerating and replacing it.")
        print()
        print("Suggested next request:")
        print(build_prompt(source, args.section, match.topic, allow_replace=True))
        return 2

    if status == "partial":
        print("A partial asset pack exists for this topic.")
        print("By the current workflow rules, replacement still requires explicit user permission.")
        print("Missing files:")
        for path in missing:
            print(f"- {path.relative_to(ROOT)}")
        print()
        if not args.allow_replace:
            print("Suggested next request:")
            print(build_prompt(source, args.section, match.topic, allow_replace=True))
            return 2

    if args.run:
        prompt = build_exec_prompt(source, args.section, match, slug, allow_replace=args.allow_replace)
        print("Invoking Codex...")
        exit_code = run_codex(prompt, args.codex_model, args.output_last_message)
        if exit_code != 0:
            print()
            print("Codex execution failed.")
            print("Check Codex CLI authentication, network connectivity to the OpenAI backend, and local execution permissions.")
        return exit_code

    print("Generation request:")
    print(build_prompt(source, args.section, match.topic, allow_replace=args.allow_replace))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
