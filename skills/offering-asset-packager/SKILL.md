# Offering Asset Packager

## Skill Name
Offering Asset Packager

## Intent
Turn a product variant described in a source HTML section into a complete, reusable offering asset set using the repo’s established packaging pattern, while only generating missing topic packs by default.

## Best Fit
- Use this skill for:
  - generating a full offering package from a named product variant
  - regenerating an existing offering package only after the user has explicitly approved replacement
  - keeping markdown, html, and xlsx assets aligned for one offering topic
- Avoid this skill for:
  - one-off edits unrelated to a full offering pack
  - source material that is not anchored in a known HTML section
  - tasks where HTML output should be template-driven rather than handcrafted

## Required Context
- Business context:
  - the offering is a productized advisory asset, not a generic consulting note
- Technical context:
  - source content is provided at runtime as a file path and may live anywhere under repo-managed inputs
  - output content lives in `docs/output/proposed/offerings`
  - checklist spreadsheets are generated via `scripts/build_checklist_xlsx.py`
- Source files or folders:
  - user-specified source HTML file
  - `docs/output/proposed/offerings`
  - `scripts/build_checklist_xlsx.py`
  - `skills/offering-asset-packager/references`

## Inputs
- Required:
  - source html file path
  - source section heading
  - product variant heading
- Optional:
  - naming override
  - buyer-language override
  - extra positioning guidance
  - explicit permission to regenerate an already existing topic pack

## Outputs
- Main output:
  - complete offering asset set for one topic
- Optional output:
  - short validation summary with assumptions and residual risks
- Expected quality bar:
  - commercially credible, client-facing, visually consistent, and complete

## Owned Assets
- Primary script: `../../scripts/build_checklist_xlsx.py`
- Supporting assets:
  - `references/brief-normalization.md`
  - `references/validation-rules.md`

## Workflow
1. Confirm the requested source file, section heading, and product variant heading.
2. Stop immediately if any of those three inputs is missing; do not assume a default file, section, or topic.
3. Read only the source section and matching product variant block needed for the task.
4. Normalize the extracted content into a brief before writing any offering assets.
5. Check whether the topic’s full asset pack already exists in the repo.
6. If the topic is missing, continue.
7. If the topic already exists or is partial, stop and require explicit user approval before regenerating and replacing its assets.
8. Reuse existing repo patterns for file naming, asset structure, and checklist generation.
9. Generate the full asset set in markdown and handcrafted html.
10. Regenerate dependent xlsx checklist assets from the updated markdown sources.
11. Validate language, completeness, styling, and file consistency.

## Operating Rules
- Prefer repeatable structures over one-off content.
- Preserve existing terminology already adopted in the repo where it is still strong.
- Keep all buyer-facing assets productized and client-friendly.
- Handcraft html assets; do not fall back to generic templates.
- Treat checklist markdown as the source of truth for corresponding xlsx outputs.
- Do not replace an existing topic pack without explicit user permission.
- Do not treat the current example source file as a built-in default.
- Generate only those topics that are not already available in the repo.

## Reference Material
- Primary references:
  - `references/brief-normalization.md`
  - `references/validation-rules.md`
- Secondary references:
  - existing offering packs in `docs/output/proposed/offerings`
- Excluded references:
  - unrelated input sections not named in the request
  - any assumed default source file, section, or topic not explicitly provided by the user

## Output Template
```text
Objective:
Generate a complete offering asset set for the selected product variant.

Inputs used:
- source file
- source section
- product variant heading
- any explicit overrides

Result:
- files generated, or generation paused pending replacement approval
- xlsx assets regenerated
- validations completed

Risks or gaps:
- assumptions made from source content
- any unresolved ambiguity
```

## Example Tasks
- Generate an Executive AI Readiness and Opportunity Assessment asset pack from the product-variants section
- Regenerate the Agentic AI Readiness Assessment asset pack after explicit approval
- Produce a new Functional AI offering package from the same source section
- Generate an asset pack from a different HTML file and section without changing the skill definition

## Maintenance Notes
- Owner: Kumar G N
- Review frequency: whenever the offering asset contract changes
- Last reviewed: 2026-03-20
