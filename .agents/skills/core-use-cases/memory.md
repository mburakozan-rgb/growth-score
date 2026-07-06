# Skill memory (memory.md)

This file tracks lessons learned from executing this skill across conversations to continuously refine the output quality.

## Lessons Learned

### Lesson 1: Avoid Black-Box Operations
* *Observation*: Strategy consultants/advisors do not trust fully automated, end-to-end black-box scoring systems. They need the ability to edit scores and analysis text.
* *Correction*: Ensure at least one use case specifically covers a "Draft & Override" workspace where the user reviews, overrides, and approves the generated capability assessments before finalization.

### Lesson 2: Selective / On-Demand Auditing
* *Observation*: Running all 8 capability pillars simultaneously is slow and token-inefficient. Users often want to audit 1-2 pillars or run them progressively.
* *Correction*: Define a "Targeted Scan" use case allowing selective pillar execution, alongside an "On-Demand Deep-Dive" use case to audit individual remaining pillars on the fly.

### Lesson 3: Concrete Telemetry Inputs
* *Observation*: Use cases must specify real tools (e.g., BuiltWith, Trakkr.ai, Robots.txt parsers) rather than generic "fetch data" scripts.
* *Correction*: Acceptance criteria must explicitly test tool triggers and API schemas.
