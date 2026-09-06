# Portfolio and Interview Guide

## One-line project description

Built an auditable, agent-ready pipeline that maps BAS points to HVAC equipment using semantic-tag normalization, deterministic candidate constraints, abstention, and human validation.

## Resume bullets

- Redesigned an LLM-first HVAC metadata-mapping prototype into an auditable pipeline with source validation, deterministic candidate generation, explicit abstention, and human-review routing.
- Audited 2,294 private practicum BAS point records and reconstructed a 48-equipment schedule; produced 142 high-confidence candidate mappings covering 47 equipment entries while preventing an unsupported cross-floor assignment.
- Developed a public, synthetic-data Python package with reproducible CLI outputs, unit tests, GitHub Actions CI, data-governance controls, and an evaluation framework separating coverage from accuracy.

## 60-second interview explanation

My OMS Analytics practicum involved mapping building automation points to HVAC equipment. The initial idea was to give drawings, tags, and point names to an LLM. During testing, I found that the model could return clean JSON and a very plausible equipment reference even when the reference contradicted the source schedule. I treated that as a governance and systems-design problem, not just a prompt problem. I rebuilt the workflow so the schedule is validated first, candidates are constrained deterministically, conflicting metadata is routed to review, and the system abstains when evidence is insufficient. I also created a human-labeling and evaluation framework so we measure precision and missed mappings rather than confusing coverage with accuracy. This same architecture is relevant to energy-management agents and data-center cooling because operational recommendations are only trustworthy when equipment context is correct.

## Questions this project helps answer

- How do you prevent an AI agent from hallucinating equipment identifiers?
- When should a deterministic rule precede an LLM?
- How do you evaluate a system that is allowed to abstain?
- How do semantic building tags support energy analytics?
- How would this design extend to data-center cooling and GHG accounting?

## Honest limitations

- The public data is synthetic.
- Private candidate mappings have not yet been independently labeled.
- The repository implements the deterministic control plane, not a production BAS integration.
- Energy savings cannot be attributed until mapping outputs feed a validated operational measure and measurement-and-verification process.
