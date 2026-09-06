# System Design

## Current implementation

The current repository implements the deterministic control plane. It is intentionally usable without an LLM.

```mermaid
flowchart TD
    A["Synthetic BAS points"] --> C["Tag normalization"]
    B["Synthetic schedule"] --> D["Schedule validation"]
    C --> E["Identifier parser"]
    D --> F["Candidate index"]
    E --> G{"Conflict?"}
    F --> H{"Exact candidate?"}
    G -->|Yes| I["Human review"]
    G -->|No| H
    H -->|Yes| J["Mapped + evidence"]
    H -->|No| K["Abstain"]
```

## Proposed agent layer

An agent should operate only after deterministic candidate generation.

```mermaid
sequenceDiagram
    participant O as Orchestrator
    participant R as Retriever
    participant L as LLM ranker
    participant V as Validator
    participant H as Human reviewer
    O->>R: Fetch schedule and graph evidence
    R->>L: Valid candidates plus evidence
    L->>V: Ranked candidate and explanation
    V->>V: Schema and consistency checks
    alt Evidence and confidence pass
        V-->>O: Accept mapping
    else Uncertain or inconsistent
        V->>H: Review package
        H-->>O: Approved label
    end
```

## Production metrics

- selective precision among automated mappings;
- abstention validity and missed-mapping rate;
- equipment coverage;
- reviewer minutes per 100 points;
- schema-validation failure rate;
- drift by site, equipment family, and naming convention.
