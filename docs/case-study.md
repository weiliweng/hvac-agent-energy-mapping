# Case Study: From LLM Prototype to Auditable HVAC Mapping

## Context

This work began as my Georgia Tech OMS Analytics practicum for an industry sponsor working on building-energy analytics. The business problem was to connect BAS points with the equipment they describe so downstream analytics can reason about systems rather than isolated time series.

## My contribution

I developed the data-preparation and equipment-mapping workflow, combined drawing extraction with structured BAS metadata, designed the model prompt used in the prototype, investigated token cost and response behavior, and documented where the approach failed.

The most important finding was not that an LLM could produce a mapping. It was that an unconstrained LLM could produce a mapping that looked credible while violating the source schedule.

## Failure analysis

The initial prototype had several reliability risks:

- source tables could be truncated during document extraction;
- nested data was sampled at the wrong structural level;
- prompt context was truncated before the relevant evidence;
- JSON parsing was not robust to nested output;
- null spreadsheet cells could become literal `nan` tags;
- no independent ground-truth set existed;
- the LLM was allowed to generate an equipment reference rather than choose from validated candidates.

One illustrative point encoded an unsupported upper floor. The model assigned it to equipment on a different floor. The answer was syntactically clean and semantically unsupported.

## Redesign

I rebuilt the workflow around four controls:

1. **Source completeness:** validate row counts, identifiers, and schedule continuity.
2. **Deterministic candidates:** construct only references that exist in the schedule.
3. **Abstention:** refuse to map when evidence is missing or inconsistent.
4. **Human evaluation:** separate coverage from accuracy and label mapped and abstained samples.

## Private-data findings

The private analysis audited 2,294 BAS point records and reconstructed a 48-entry equipment schedule. The deterministic baseline produced 142 high-confidence point-level candidate mappings covering 47 of the 48 schedule entries. It correctly abstained on the unsupported-floor example.

These results demonstrate improved data integrity and constraint enforcement. They do not establish production accuracy because independent human labels have not yet been completed.

## What I would build next

- retrieve only relevant drawing regions and BAS hierarchy neighbors;
- let an LLM rank a constrained candidate list, never invent identifiers;
- require structured evidence and confidence fields;
- route low-confidence cases to a reviewer;
- monitor precision, abstention validity, drift, and reviewer workload;
- connect validated equipment graphs to fault detection and energy-saving measures.

## Career relevance

The project sits at the intersection of AI agents, building energy management, semantic interoperability, and trustworthy climate technology. The same pattern applies to data-center cooling systems, where reliable equipment context is necessary before an agent can recommend operational changes or calculate energy and emissions impacts.
