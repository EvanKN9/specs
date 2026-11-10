# SPECS UML Diagrams

These diagrams are based on `Business Plan — PC Build Optimizati.txt` and `Reqs.txt`. The `.puml` files are editable PlantUML sources.

## Use Case Diagram — `SPECS-Use-Case.puml`

Shows the SPECS system boundary, the primary PC builder/visitor and registered user actors, the administrator actor, and external catalog/pricing, authentication, and optional natural-language services. It covers the major capabilities without enumerating low-level requirements.

Functional requirements represented: FR-01 through FR-16, except the separate upgrade-recommendation requirement FR-17; FR-18 through FR-20; and the optional FR-22/FR-23 path.

## Activity Diagram — `SPECS-Generate-Optimized-Build.puml`

Models the optimized-build workflow from entering budget and workload constraints through candidate generation, deterministic compatibility validation, scoring, explanation, and user review. It includes invalid-input and no-valid-build alternatives.

Functional requirements represented: FR-08 through FR-13, plus FR-03, FR-04, FR-05, FR-10, FR-11, FR-12, and FR-23 when natural-language input is used. It also reflects NFR-02, NFR-04, NFR-05, NFR-17, and NFR-18 at a high level.

## Activity Diagram — `SPECS-Replace-Component.puml`

Models selecting a component replacement, updating the build, recalculating cost, checking the complete configuration, explaining any conflict, and either accepting, retrying, or cancelling the replacement.

Functional requirements represented: FR-01 through FR-07, FR-13, and FR-21. It also reflects NFR-01, NFR-04, and NFR-19 at a high level.

## Rendering

PlantUML sources are preserved here. No PlantUML renderer was available in the project environment when these files were created, so PNG/SVG exports were not generated.
