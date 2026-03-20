# Validation Rules

## Asset Completeness
Every generated offering should include:
- offering markdown
- offer poster html
- polished executive deck html
- delivery guide markdown
- delivery guide html
- client report templates markdown
- client preparation checklist markdown
- client preparation checklist xlsx
- finding capture checklist markdown
- finding capture checklist xlsx
- process infographic html

## Existence And Replacement Rules
- generate the full asset set automatically only for topics that are not yet available in the repo
- treat a topic as existing when its expected full asset set is already present for the slug
- treat a partially present pack as protected content that also requires explicit approval before replacement
- if a topic already exists, ask the user for permission before regenerating and replacing any of its assets
- do not partially replace an existing topic pack by default

## Language Rules
- use client-facing language in buyer-facing assets
- avoid `we`, `our`, and inward-looking phrasing in market-facing collateral
- avoid generic AI strategy wording when a more specific statement is available
- keep recommendations commercially clear and decision-oriented

## HTML Styling Rules
- use Google brand colors in refreshed html assets:
  - blue `#4285f4`
  - green `#34a853`
  - yellow `#fbbc04`
  - red `#ea4335`
- use a clean 16:9-safe layout for posters and decks
- avoid content overlap in posters
- ensure the polished deck includes a clear process flow

## Consistency Rules
- keep file naming aligned with repo conventions
- keep the delivery guide, poster, deck, and process infographic aligned in message
- regenerate xlsx outputs whenever the corresponding checklist markdown changes
- keep instructions, examples, and execution behavior aligned with the actual runtime inputs
- do not present any example source file, section, or topic as if it were a fixed workflow default

## Validation Pass
Run at least these checks before closing:
- required inputs were explicitly provided
- source file and section references used in commands or guidance match the actual requested inputs
- topic existence check completed
- replacement permission behavior followed correctly
- expected files exist
- markdown/html language scan passes
- xlsx regeneration completed
- git diff is limited to the intended offering assets and supporting scripts or docs
