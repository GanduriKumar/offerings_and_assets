# Offering Asset Generator User Guide

## 1. What This Guide Is For
This guide explains how to generate a full offering asset pack from a topic found in a source file.

The source can change over time. The file, section name, and topic names are inputs to the process, not fixed parts of the tool.

In simple terms, the process works like this:
- you point the tooling to a source file
- you tell it which section to use
- you choose one topic from that section
- the tooling generates the full asset pack for that topic

In the Python script, those inputs are passed as arguments:
- `--source` for the input file
- `--section` for the section heading inside that file
- `--topic` for the topic to generate

Example only:
- source file: `docs/input/AI_Readiness_Opportunity_Assessment_Expanded_Potato_Mode.html`
- section: `Potential Product Variants That Are Actually Worth Building`
- topic: `Functional AI Readiness Review`

Those values are examples. In future runs, you can use different source files, different sections, and different topics.

## 2. What Gets Generated
For each topic, the process is designed to create the full standard asset pack:

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

## 3. The Three Ways To Use This
There are three ways to use this process:

- use the Python script from a normal terminal
- use the Python script inside an active Codex session for preflight only
- ask the current Codex session to run the agent, skill, and workflow directly

Each method is explained separately below.

## 4. Files Used By This Process
Main script:
- `scripts/generate_offering_assets.py`

Checklist spreadsheet generator:
- `scripts/build_checklist_xlsx.py`

Agent definition:
- `agents/offering-asset-generator/AGENT.md`

Workflow definition:
- `agents/offering-asset-generator/workflows/generate_offering_assets.md`

Skill definition:
- `skills/offering-asset-packager/SKILL.md`

Supporting reference files:
- `skills/offering-asset-packager/references/brief-normalization.md`
- `skills/offering-asset-packager/references/validation-rules.md`

## 5. Before You Start
Before using the script in live generation mode, make sure:
- Python is available
- the `codex` CLI is installed
- the `codex` CLI is logged in and working
- you are in the repo root folder
- you are using a normal PowerShell terminal if you plan to use `--run`

The repo root folder is:

```powershell
C:\Users\kumar.gn\personalprojects\offerings_and_assets
```

## 6. Topic Status Meaning
When you check a topic, the script reports one of these states:

### `missing`
This means no asset pack exists yet for that topic.

What it means for you:
- generation can proceed

### `exists`
This means the full asset pack already exists.

What it means for you:
- the tooling will not silently replace it
- explicit permission is required before regeneration

### `partial`
This means some files exist, but the full asset pack is incomplete.

What it means for you:
- the tooling still treats this as protected content
- explicit permission is required before replacement

## 7. Mode 1: Python Script In A Normal Terminal
This is the best option when you want the script to manage the process and you want to use `--run`.

### What This Mode Is For
Use this mode when:
- you are not already inside Codex
- you want a command-based workflow
- you want the script to launch live generation

### What You Should Do
- open a normal PowerShell terminal
- go to the repo folder
- run a topic check first
- use `--run` only after preflight

### What You Should Not Do
- do not run this from inside an active Codex session
- do not use `--allow-replace` unless you have explicitly approved replacement

### Step 1. Open PowerShell
Open a normal PowerShell window. Do not do this from inside an active Codex session.

### Step 2. Go To The Repo Folder
Run:

```powershell
cd C:\Users\kumar.gn\personalprojects\offerings_and_assets
```

### Step 3. List Available Topics
Run:

```powershell
python scripts\generate_offering_assets.py --source docs\input\AI_Readiness_Opportunity_Assessment_Expanded_Potato_Mode.html --section "Potential Product Variants That Are Actually Worth Building" --list-topics
```

This shows the available topics and whether each one is `missing`, `exists`, or `partial`.

### Step 4. Check One Topic Before Generating
Run:

```powershell
python scripts\generate_offering_assets.py --source docs\input\AI_Readiness_Opportunity_Assessment_Expanded_Potato_Mode.html --section "Potential Product Variants That Are Actually Worth Building" --topic "Functional AI Readiness Review"
```

This does not generate files. It only checks:
- the topic name
- the slug
- whether the pack already exists

### Step 5. Generate A Missing Topic
If the status is `missing`, run:

```powershell
python scripts\generate_offering_assets.py --source docs\input\AI_Readiness_Opportunity_Assessment_Expanded_Potato_Mode.html --section "Potential Product Variants That Are Actually Worth Building" --topic "Functional AI Readiness Review" --run
```

### Step 6. Replace An Existing Topic Only After Approval
If the topic already exists and you have explicitly approved replacement, run:

```powershell
python scripts\generate_offering_assets.py --source docs\input\AI_Readiness_Opportunity_Assessment_Expanded_Potato_Mode.html --section "Potential Product Variants That Are Actually Worth Building" --topic "Agentic AI Readiness Assessment" --allow-replace --run
```

### Important Note
This is the only mode where `--run` should be used.

## 8. Mode 2: Python Script Inside A Codex Session
Use this mode when you are already inside Codex and want the script only for checking.

### What This Mode Is For
Use this mode when:
- you want preflight information
- you want to check whether a topic is missing, partial, or already exists
- you want to avoid nested Codex execution

### What You Should Do
- run the script without `--run`
- use it to check topic names, slugs, and status
- then ask the current Codex session to generate directly

### What You Should Not Do
- do not use `--run`
- do not try to start a nested `codex exec` from inside Codex

Reason:
- `--run` starts `codex exec`
- inside Codex, that creates a nested Codex session
- nested Codex sessions are not reliable and may fail because of session, auth, sandbox, or network constraints

### Step 1. Run Preflight Only
Run the script without `--run`:

```powershell
python scripts\generate_offering_assets.py --source docs\input\AI_Readiness_Opportunity_Assessment_Expanded_Potato_Mode.html --section "Potential Product Variants That Are Actually Worth Building" --topic "Functional AI Readiness Review"
```

This gives you preflight information such as:
- whether the topic exists
- whether replacement permission is needed
- what topic name and slug are being used

### Step 2. Do Not Use `--run`
Do not run:

```powershell
python scripts\generate_offering_assets.py --source docs\input\AI_Readiness_Opportunity_Assessment_Expanded_Potato_Mode.html --section "Potential Product Variants That Are Actually Worth Building" --topic "Functional AI Readiness Review" --run
```

inside Codex.

### Step 3. Ask The Current Codex Session To Generate
After preflight, ask the current Codex session to do the generation directly.

Use a prompt like:

```text
Use the offering asset generator agent and the offering asset packager skill to generate the full offering asset set for "Functional AI Readiness Review" from the "Potential Product Variants That Are Actually Worth Building" section in docs/input/AI_Readiness_Opportunity_Assessment_Expanded_Potato_Mode.html.
```

If the topic already exists and you want to replace it, make that explicit:

```text
Regenerate and replace the full offering asset set for "Agentic AI Readiness Assessment" using the offering asset generator agent and the offering asset packager skill.
```

## 9. Mode 3: Direct Codex Agent / Skill / Workflow Execution
This is the repo-native Codex path.

### What This Mode Is For
Use this mode when:
- you are already working inside Codex
- you want the current Codex session to perform the work directly
- you want to use the repo definitions without going through `--run`

### What You Should Do
- tell Codex which source file to use
- tell Codex which section to use
- tell Codex which topic to generate
- if replacement is intended, say that explicitly

### What You Should Not Do
- do not assume the source file, section, or topics are fixed
- do not ask for replacement indirectly when a topic already exists

Here, the mechanism is not a Python command. The mechanism is your prompt to the current Codex session.

The repo definitions used are:
- `agents/offering-asset-generator/AGENT.md`
- `agents/offering-asset-generator/workflows/generate_offering_assets.md`
- `skills/offering-asset-packager/SKILL.md`

### How It Works
You tell Codex:
- which source file to use
- which section to use
- which topic to generate

Codex then follows the agent, workflow, and skill definitions in the repo.

### Example Prompt
Use:

```text
Use the offering asset generator agent and the offering asset packager skill to generate the full offering asset set for "AI Governance and Trust Review" from the "Potential Product Variants That Are Actually Worth Building" section in docs/input/AI_Readiness_Opportunity_Assessment_Expanded_Potato_Mode.html.
```

### When To Use This Path
Use this path when:
- you are already working inside Codex
- you want the current Codex session to do the work directly
- you do not need the script to launch another process

## 10. Which Option Should You Choose
Use Mode 1 when:
- you are in a normal terminal
- you want to use `--run`

Use Mode 2 when:
- you are already inside Codex
- you only want preflight and status checks

Use Mode 3 when:
- you are already inside Codex
- you want the current session to perform the generation directly

## 11. Useful Commands
List topics:

```powershell
python scripts\generate_offering_assets.py --source docs\input\AI_Readiness_Opportunity_Assessment_Expanded_Potato_Mode.html --section "Potential Product Variants That Are Actually Worth Building" --list-topics
```

Check one topic:

```powershell
python scripts\generate_offering_assets.py --source docs\input\AI_Readiness_Opportunity_Assessment_Expanded_Potato_Mode.html --section "Potential Product Variants That Are Actually Worth Building" --topic "Functional AI Readiness Review"
```

Generate a missing topic from a normal terminal:

```powershell
python scripts\generate_offering_assets.py --source docs\input\AI_Readiness_Opportunity_Assessment_Expanded_Potato_Mode.html --section "Potential Product Variants That Are Actually Worth Building" --topic "AI Governance and Trust Review" --run
```

Replace an existing topic after approval:

```powershell
python scripts\generate_offering_assets.py --source docs\input\AI_Readiness_Opportunity_Assessment_Expanded_Potato_Mode.html --section "Potential Product Variants That Are Actually Worth Building" --topic "Agentic AI Readiness Assessment" --allow-replace --run
```

Save the extracted brief:

```powershell
python scripts\generate_offering_assets.py --source docs\input\AI_Readiness_Opportunity_Assessment_Expanded_Potato_Mode.html --section "Potential Product Variants That Are Actually Worth Building" --topic "Functional AI Readiness Review" --emit-brief docs\Functional_AI_Readiness_Review_brief.md
```

Save the final Codex response:

```powershell
python scripts\generate_offering_assets.py --source docs\input\AI_Readiness_Opportunity_Assessment_Expanded_Potato_Mode.html --section "Potential Product Variants That Are Actually Worth Building" --topic "Functional AI Readiness Review" --run --output-last-message docs\output\proposed\offerings\Functional_AI_Readiness_Review_generation_last_message.txt
```

## 12. Common Problems And Fixes
### Problem: Topic not found
What it means:
- the topic name you typed does not match a topic in the selected section

What to do:
- run `--list-topics`
- copy the topic name exactly as shown

### Problem: Section not found
What it means:
- the `--source` file is not the one you intended, or the `--section` value does not exactly match a heading in that file

What to do:
- check the exact source file path
- check the exact section title inside that file

### Problem: Existing topic is blocked
What it means:
- the topic already has files in the repo

What to do:
- only proceed after explicit approval
- then use `--allow-replace`

### Problem: Codex execution failed
What it usually means:
- Codex CLI is not logged in
- the machine cannot reach the OpenAI backend
- `--run` was used from inside an active Codex session

What to do:
- check Codex login
- check network connectivity
- rerun from a normal PowerShell terminal outside Codex

## 13. Recommended Beginner Flow
If you are new to this process, use this order:

1. Open a normal PowerShell terminal.
2. Change to the repo folder.
3. Run `--list-topics`.
4. Run a preflight check for one topic.
5. If the topic is `missing`, run with `--run`.
6. If the topic is `exists` or `partial`, do not replace it unless you have explicitly approved that replacement.
7. If you are already inside Codex, do not use `--run`; ask the current Codex session to generate the assets directly.

## 14. Short Summary
Remember these three rules:

1. `--run` is for a normal terminal outside Codex.
2. Inside Codex, use the script only for checking, then ask Codex to generate directly.
3. Existing or partial topic packs must not be replaced silently.
