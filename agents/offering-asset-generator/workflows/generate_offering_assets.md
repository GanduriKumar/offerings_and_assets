# Generate Offering Assets Workflow

## Objective
Create a complete offering asset set from a named product variant located within a specific section of a source HTML file, while generating only missing topic packs by default.

## Required Inputs
- source file path
- section heading
- product variant heading

Do not start this workflow if any required input is missing. Do not assume the current repo example file or section unless the user explicitly names them.

## Output Inventory
Generate all of the following for the selected offering:
- `<Slug>_Offering.md`
- `<Slug>_Offer_Poster.html`
- `<Slug>_Executive_Deck_Polished.html`
- `assets/<Slug>_Delivery_Guide.md`
- `assets/<Slug>_Delivery_Guide.html`
- `assets/<Slug>_Client_Report_Templates.md`
- `assets/<Slug>_Client_Preparation_Checklists.md`
- `assets/<Slug>_Client_Preparation_Checklists.xlsx`
- `assets/<Slug>_Finding_Capture_Checklists.md`
- `assets/<Slug>_Finding_Capture_Checklists.xlsx`
- `assets/<Slug>_Process_Infographic.html`

## Workflow
1. Read the source HTML file and locate the requested section heading.
2. Within that section, locate the requested product variant heading.
3. Extract the variant block using the expected pattern:
   - heading
   - descriptive paragraph
   - bullet list
4. Normalize the extracted content into an offering brief containing:
   - product name
   - promise
   - use when
   - core output
   - why it sells or why it builds leverage
   - implied buyer and buying context
   - likely delivery shape and follow-on path
5. Convert the product name into the expected repo slug and check whether the full asset set already exists for that topic.
6. If the topic pack does not exist, continue and generate it.
7. If the topic pack already exists, stop and ask the user for permission before regenerating and replacing any of its files.
8. Generate the core markdown files first:
   - offering
   - delivery guide
   - client report templates
   - client preparation checklist
   - finding capture checklist
9. Generate the handcrafted HTML assets from the same brief and markdown decisions:
   - offer poster
   - polished executive deck
   - process infographic
   - delivery guide html
10. Regenerate deterministic spreadsheet outputs from checklist markdown using `scripts/build_checklist_xlsx.py`.
11. Validate the finished asset set:
   - all required files exist
   - buyer-facing language is client-facing
   - no stale spreadsheet outputs remain
   - refreshed HTML assets use Google brand colors
   - poster layout is readable and does not visibly overlap
   - deck includes a clear process flow
12. Report assumptions, validations performed, and any open risks.

## Extraction Rules
- The source file path, section heading, and product variant heading are runtime inputs, not fixed workflow defaults.
- Prefer the exact named section and exact named product variant heading.
- If the section contains multiple `h3` product variants, extract only the matching one.
- Do not infer a product from unrelated sections.
- If the product heading exists but the expected descriptive paragraph or bullets are missing, state the gap and stop.
- If the source file exists but the requested section does not, stop instead of silently falling back to a different section.
- If the section exists but the requested topic does not, stop instead of choosing a nearby topic.

## Naming Rules
- Convert the product name into a repo-safe slug using underscores.
- Preserve the repo’s established capitalization and suffix conventions.
- Write outputs under `docs/output/proposed/offerings` and its `assets` subfolder.

## Existence Rules
- Treat a topic as already available if the expected full asset set is present for its slug.
- Do not regenerate a topic pack merely because one or two files could be improved; ask the user first.
- Missing topics may be generated without a separate confirmation step.
- Existing topics require explicit user permission before replacement.
- Partial topic packs also require explicit user permission before replacement.

## Quality Rules
- Make all buyer-facing language specific and commercially credible.
- Avoid `we`, `our`, and inward-looking phrasing in market-facing assets.
- Use Google brand colors for refreshed HTML assets:
  - blue `#4285f4`
  - green `#34a853`
  - yellow `#fbbc04`
  - red `#ea4335`
- Keep posters and decks readable at 16:9 presentation dimensions.

## Validation Checklist
- required inputs present
- source file found
- source section found
- product variant found
- offering brief normalized
- topic existence check completed
- missing topic generation or existing-topic permission path followed correctly
- markdown assets generated
- html assets generated
- xlsx assets regenerated
- language validation passed
- asset completeness validation passed
- instructions and examples used during the run are consistent with the actual input file, section, and topic
