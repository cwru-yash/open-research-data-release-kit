# Open Research Data Release Kit

Open Research Data Release Kit is a small Polars-based research software project for converting real public scientific datasets into validated, normalized, documented, versioned data-release artifacts.

Research data often starts in domain-specific formats: space physics telemetry, climate station records, biomedical signal metadata, benchmark logs, or simulation outputs. These datasets are useful, but they are often difficult to compare, validate, reproduce, and share across teams.

This project demonstrates a lightweight pattern for research data release engineering:

1. Fetch a small slice of a public dataset.
2. Normalize it into a common schema.
3. Validate required fields and numeric values.
4. Compute quality metrics.
5. Publish CSV, Parquet, metadata JSON, and a Markdown release report.
6. Test and lint the pipeline through CI.

The goal is not to replace domain-specific scientific tools. The goal is to show how research software can make public datasets easier to inspect, reproduce, and reuse.

![CI](https://github.com/cwru-yash/open-research-data-release-kit/actions/workflows/ci.yml/badge.svg)
