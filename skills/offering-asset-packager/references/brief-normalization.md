# Brief Normalization Rules

## Purpose
Convert a product variant block extracted from a source HTML section into a normalized offering brief before generating assets.

The source file path, section heading, and topic heading are inputs to the process. They are not fixed defaults.

## Expected Source Pattern
The source block should usually appear as:
- product variant heading
- one descriptive paragraph
- one bullet list

If the requested section or topic does not match that pattern closely enough to extract a credible brief, stop and surface the gap instead of guessing.

## Extracted Fields
Normalize the content into the following fields:
- `product_name`
- `positioning_summary`
- `use_when`
- `core_output`
- `why_it_sells`
- `buyer_context`
- `delivery_implication`
- `follow_on_implication`

## Mapping Guidance
- descriptive paragraph -> positioning summary and promise
- `Use it when` bullet -> use_when and buyer context
- `Core output` bullet -> output set emphasis
- `Why it sells` or equivalent bullet -> commercial rationale

## Inference Rules
- infer buyer context from the product wording if it is not stated directly
- infer delivery shape from existing repo patterns unless contradicted by the source
- keep inferences conservative and commercially plausible
- if a critical field cannot be inferred credibly, surface the gap instead of inventing it
- do not infer the source file, section, or topic from repo history or the current common examples

## Slug Rule
Convert `product_name` into the standard repo slug format:
- replace spaces with underscores
- preserve acronym capitalization already used in repo output files

## Downstream Requirement
Do not start asset generation until the brief is coherent enough to support:
- offering narrative
- delivery guidance
- checklists
- handcrafted html assets
