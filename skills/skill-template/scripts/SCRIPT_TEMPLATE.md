# Script Specification Template

## Script Name
- File name:
- Version:
- Owner:

## Parent Skill
- Skill:
- Related skill file: `../SKILL.md`

## Purpose
State the job this script performs in one sentence.

## Business Value
Explain why this script exists and what manual effort or risk it removes.

## Inputs
- Required arguments:
- Optional arguments:
- Environment variables:
- Input files:

## Outputs
- Files created:
- Console output:
- Exit conditions:

## Execution
```bash
# Example
python scripts/<script_name>.py --input docs/input/<file> --output docs/output/<file>
```

## Processing Steps
1. Validate inputs.
2. Load the required source data.
3. Apply the transformation or generation logic.
4. Save outputs in the expected location.
5. Return a useful success or failure signal.

## Dependencies
- Runtime:
- External packages:
- Internal modules:

## Error Handling
- Fail fast when required inputs are missing.
- Provide actionable error messages.
- Avoid silent partial success.

## Validation
- How to test:
- Sample command:
- Expected result:

## Operational Notes
- Performance considerations:
- Security considerations:
- Idempotency expectations:

## Future Improvements
- Improvement 1:
- Improvement 2:

## Change Log
- YYYY-MM-DD:
