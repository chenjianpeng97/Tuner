---
name: requirements-to-feature-files
description: Decompose raw requirements or user stories into hierarchical Gherkin .feature files with rule-based structure and folder parity. Use when asked to analyze product requirements, break down complex business logic, or map requirements into Behave-compatible feature files and directories.
---

# Requirements to Feature Files

## Overview

Turn a raw requirement into a Gherkin feature tree that mirrors file system structure. Emphasize declarative business intent, rule-driven logic, and Behave-compatible syntax.

## Workflow

1. Locate the requirement in the feature tree
	- Decide whether this is a top-level feature or a sub-requirement of an existing feature.
	- Default root folder is `features/` unless the user specifies another location.

2. Define the output path using hierarchy parity
	- Each `.feature` file is treated as a folder.
	- If a feature needs child requirements, create a folder named after the parent `.feature` file stem.
	- Place child `.feature` files inside that folder.

3. Extract business rules
	- Convert constraints, permissions, and edge conditions into `Rule` blocks.
	- Keep each rule focused and testable.

4. Write Gherkin scenarios
	- Use `Feature`, optional `Background`, and `Scenario` or `Example`.
	- Keep steps declarative and domain-level; avoid UI details.
	- Use `Background` only for shared context at the current feature level.

5. Provide a dry-run command
	- Always include a `behave <path> --dry-run` command at the end.

## Guardrails

- Do not describe UI interactions (clicks, buttons, pages, fields).
- Prefer short, domain-specific step phrasing.
- Use `Rule` when logic is more than a simple happy path.
- Ensure the output is valid Gherkin for Behave.

## Output Contract

- State the save path before the Gherkin content.
- Output only one feature file per request unless the user asks for multiple.
- Include the dry-run command after the Gherkin content.

## References

- Example inputs and outputs: references/examples.md
