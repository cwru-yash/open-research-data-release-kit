# AGENTS.md

## Purpose

This repository is a small research software engineering project. It converts small slices of real public scientific datasets into validated, normalized, documented, versioned data-release artifacts.

It is designed to demonstrate maintainable scientific Python, not notebook-only analysis.

## Project Domains

Initial adapters:

1. NOAA/NCEI climate daily summaries
2. NASA/SPDF CDAWeb or OMNI-style space physics data
3. PhysioNet PTB-XL ECG metadata
4. Optional: MLPerf inference benchmark summaries

## Stack

- Python 3.11
- Polars
- Pydantic
- Typer
- Rich
- Requests
- PyYAML
- pytest
- ruff
- Poetry

## Collaboration Rules

Do not generate the full project at once.

For every file or function, first explain:

1. What problem it solves.
2. Why we need it.
3. Why the design/library is appropriate.
4. What simpler alternative exists.
5. What can go wrong.
6. How to test it.

Use this workflow:

Spec → Predict → Generate → Inspect → Test → Explain → Manual Edit → Commit.

## Engineering Rules

- Prefer small modules.
- Prefer readable code over clever abstractions.
- Use Polars for table transformations.
- Use Pydantic for schema/record validation.
- Keep fetch logic separate from normalization logic.
- Do not commit large raw datasets.
- Do not commit protected or unclear-license medical data.
- Use tiny fixtures for tests.
- All release outputs should be reproducible.

## Definition of Done

A task is done only when:

1. Code is implemented.
2. Tests pass.
3. Linting passes.
4. The purpose is documented.
5. The user can explain the design in an interview.

Run before commit:

```bash
poetry run ruff check .
poetry run pytest