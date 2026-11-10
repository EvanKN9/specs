# SPECS Phased Implementation Plan

Planning baseline: 19 October 2026. Product: SPECS, formerly PCPartPicker Clone; some repository documentation still says PartsFoundry.

This document analyzes the supplied project and provides sequential implementation prompts. No phase has been executed. The existing React/Vite application is the starting point and must be extended incrementally. Proposed paths, endpoints, schemas, scripts, and test names below are implementation recommendations, not claims that those artifacts already exist.

## 1. Source authority and review boundaries

| Requested source | Workspace evidence | Status and authority |
| --- | --- | --- |
| Business Plan | `Business Plan — PC Build Optimizati.txt` | Readable. Establishes the product, audiences, optimization goals, potential stack, guest access, account benefits, and long-term opportunities. |
| Software Requirements Specification | `Reqs.txt` | Readable requirements baseline containing FR-01–FR-23 and NFR-01–NFR-20. No separate document titled Software Requirements Specification was found. The architecture explicitly recognizes `Reqs.txt` as its requirements input; use these actual IDs without inventing additional SRS content. |
| Use Case Specification | No corresponding document found among the workspace files | **Missing.** No authoritative use-case IDs, formal preconditions, alternate flows, or priorities can be claimed. Section 3 supplies provisional planning use cases derived from the available requirements and architecture. |
| Software Architecture Specification | `Software Architecture Specification.docx` | Readable via its document XML, including tables. Version 1.1, dated 5 October 2026, status Architecture baseline. Sections 4–10 establish layers, technology, data, workflows, integrations, security, and operations; section 13 reconciles the FR/NFR baseline. |
| Existing frontend and GUI | `src/App.jsx`, `src/logic/buildLogic.js`, `src/data/mockData.js`, CSS, assets, entry points, package/config files | Reviewed from source. GUI structure, handlers, state transitions, and styling were inspected statically; no running-browser, accessibility, build, or performance certification is implied. |
| Supporting context | `README.md`, `DESIGN_REFERENCES.md`, `Assignment.txt` | README describes an older PartsFoundry proof of concept. Design references establish the SPECS brand and existing visual direction. Assignment.txt describes the earlier frontend-only prototype assignment, not a prohibition on future full-stack phases requested here. |

The architecture is the implementation baseline; the business plan's technology list is initially described as potential, while the architecture adopts React/TypeScript, Python/FastAPI, PostgreSQL/SQLAlchemy, deterministic Python optimization, and Docker/GitHub Actions. The current frontend is JavaScript/JSX: migrate gradually to TypeScript without recreating the Vite app or replacing its GUI.

Where sources differ, preserve explicit requirements and record an architecture decision. For example, cooling is required by FR-02/FR-05 even though the architecture's open-decision category shortlist omits it. Include all eight required categories. The numerical NFR targets remain release gates even where the architecture discusses future SLO confirmation. Do not weaken them silently.

## 2. Project analysis

### 2.1 Functional requirements

| Capability | Authoritative requirements | Required behavior |
| --- | --- | --- |
| Catalog and cost | FR-01, FR-03, FR-21 | Browse/search/filter/specifications, estimated totals, and dated price/specification sources. |
| Manual build and compatibility | FR-02, FR-04–FR-07, FR-13 | Select eight component categories; reevaluate every mutation; cover socket, form factor, memory, power, physical fit, cooling, and storage; explain conflicts and suggest compatible replacements. |
| Automatic planning | FR-08–FR-12 | Accept budget, five workload profiles, storage, network, and other preferences; produce complete compatible constraint-satisfying configurations with workload/value optimization and reasons. |
| Build lifecycle | FR-14–FR-17 | Compare at least two builds; registered-user CRUD/rename/duplicate; read-only sharing; compatible upgrades to an existing PC. |
| Administration and access control | FR-18–FR-20 | Catalog CRUD/deactivation, compatibility-rule and scoring-data management, ownership and administrative authorization. |
| Optional language interface | FR-22, conditional FR-23 | Convert natural language into structured constraints, then require deterministic validation. |

Must requirements form the core baseline. This plan also includes all Should requirements in the main delivery sequence. Only FR-22 and its conditional safeguards are placed in the stretch phase. Architecture-supported ingestion, notifications, audit, and operational features are identified separately from numbered FR obligations.

### 2.2 Non-functional requirements

| Area | IDs | Required verification |
| --- | --- | --- |
| Responsiveness and scaling | NFR-01–NFR-03, NFR-20 | Compatibility p95 ≤1 second over ≥100 modifications with builds up to 15 components; generation p95 ≤10 seconds over ≥50 requests with up to 300 catalog components; normal API p95 ≤2 seconds at 100 concurrent users with error rate <1%; catalog growth 100→300 increases median optimization time by no more than 300%, with median <10 seconds. |
| Correctness and explanations | NFR-04, NFR-05, NFR-17 | 100% accuracy across ≥100 predefined compatibility cases; ≥100 generation scenarios satisfying every mandatory constraint, budget, and compatibility rule; a reason for CPU, GPU, motherboard, memory, and PSU in every generated build. |
| Reliability and availability | NFR-06, NFR-07 | ≥99% success in 1,000 requests with zero corrupt/partial saves; once-per-minute health checks for seven consecutive days showing ≥99.5% availability excluding announced maintenance. |
| Security and privacy | NFR-08, NFR-09 | Salted/hashed passwords where stored, HTTPS, private-resource authorization, zero unresolved high/critical scan findings; minimal personal data, no payment-card/government-ID/unrelated personal data, account data removed/anonymized within 24 hours of deletion. |
| UX and maintainability | NFR-10–NFR-13 | ≥80% of ≥10 representative first-time users generate a valid build and locate its explanation within seven minutes unaided; zero serious/critical automated accessibility violations plus keyboard workflows; latest stable Chrome/Edge/Firefox at 360–1440px; ≥80% backend compatibility/optimization coverage plus formatting/lint/CI gates. |
| Deployment, integrity, recovery | NFR-14–NFR-16 | Documented clean-environment deployment within 15 minutes plus health check; no orphan/incomplete transactions across CRUD, rollback, and concurrency tests; restoration ≤30 minutes and data loss ≤24 hours. |
| Conditional AI and price disclosure | NFR-18, NFR-19 | If natural-language input exists, ≥50 requests with 100% deterministic compatibility/budget validation before presentation; every total-price page displays the dataset update date and price uncertainty. |

These are source targets, not achieved measurements. Time-based, human-subject, deployment, provider, and recovery evidence requires later execution and must remain marked pending until collected.

### 2.3 Layers and component responsibilities

| Layer | Components to extend or implement | Boundary |
| --- | --- | --- |
| Presentation | Existing React/Vite screens, typed API client, accessible dialogs, accounts, shared view, upgrade flow, administration | Own interaction and transient client state; do not make the browser authoritative for authorization, prices, or compatibility. |
| API/application | FastAPI versioned JSON endpoints, DTO validation, command/query services, transaction orchestration, authentication/authorization, correlation IDs, idempotency | Orchestrate use cases, expose OpenAPI, return consistent safe errors; keep hardware rules out of route handlers. |
| Domain | Catalog, Offers, Builds, Compatibility, Accounts, Sharing, Notifications, Administration; an explicit optimizer/recommendation service as required by architecture section 13 | Own invariants, scoring, constraints, explanation evidence, rule versions, revisions, ownership, and lifecycle. |
| Data/integration | SQLAlchemy repositories, PostgreSQL, search/cache ports, approved feed adapters, identity adapter, message delivery, object storage and queue adapters | Implement persistence and provider-specific behavior without leaking vendors into domain modules. |
| Platform/operations | Separate API/worker processes sharing application code, Docker, CI, health/metrics/logs, secrets, backups, deployment and incident runbooks | Keep periodic/failure-prone ingestion and notifications off interactive request paths. |

Use a modular monolith, not premature microservices. Start with indexed PostgreSQL search behind the search port, with rebuildable derived indexing and database fallback. A separate search service/cache/broker should be added only when measured need or the selected deployment warrants it. This is a proposed economical realization of the architecture, to record in Phase 1, not an instruction to discard its search/cache/queue boundaries.

### 2.4 Persistence requirements

The architecture names User, Product, Offer, Build, Build item, Compatibility rule, Share snapshot, Alert subscription, and Audit event. Supporting tables/models are also needed for retailer/source identity, price history, scoring profiles/versions, import jobs, durable event delivery, and notification delivery state. These supporting structures are planning designs derived from the documented workflows, not additional supplied requirements.

Use PostgreSQL as the source of truth, SQLAlchemy repositories, and versioned migrations (Alembic is the proposed migration tool). Normalize category-specific facts with explicit units and typed validation rather than relying on free-text mock specifications. Store monetary values with decimal precision and currency. Record independent specification-source and offer-observation dates; never label an import timestamp as the original source observation date.

Build items require product foreign keys, quantities, role/category constraints, and atomic revision updates. Drafts may be incomplete or incompatible; distinguish those states from a complete validated build. Generated builds must be complete and valid. A schema should support the NFR-01 test size of 15 components even though the current GUI has eight category slots: model memory/storage quantities or multiple items without weakening category rules.

Use optimistic concurrency and transactional mutation/idempotency. Referenced products must be retired rather than destructively removed; allow hard deletion only for unreferenced records as FR-18 permits. Share snapshots embed visible fields and the applicable build/rule/scoring/source versions. Snapshots remain readable after later catalog changes, while explicit revocation/expiry controls access. Keep PII out of snapshot JSON and minimize retained personal data in audits/backups under a documented retention and deletion policy.

Search, cache, and generated artifacts are derived or auxiliary stores, never the only copy of builds/accounts. Migrations, indexes, rollback/recovery instructions, isolated test databases, backups, and restore verification are required.

### 2.5 External systems

| System | Source-supported purpose | Plan treatment |
| --- | --- | --- |
| OAuth/OIDC provider | Identity assertions; JWT or OAuth/OIDC baseline | Phase 4 adapter and provider-neutral tests. Choose provider through an ADR; no provider is named in the sources. |
| Retailer/marketplace feeds or APIs | Offers, availability, permitted shipping information and retailer destinations | Phase 12 approved-source registry, asynchronous ingestion, freshness, reconciliation. Actual providers/permissions are unresolved. No scraping assumed. |
| Email/notification service | Verification/recovery where applicable, price/build alerts | Phase 13 delivery port, retries and delivery state; use identity-provider flows where appropriate. |
| Affiliate network | Optional referral attribution | Phase 12 safe direct links required; affiliate adapter is optional and falls back to direct links. |
| Telemetry/analytics | Health, logs, metrics, traces, optional product usage events | Local operational telemetry from Phase 2, release monitoring in Phase 14; analytics consent/allowlists and optional external sinks. |
| Cloud platform | Managed relational database, containers, CDN/WAF, object storage, queue/cache/search where chosen | Phase 14 staging/release packaging after provider selection; isolated development/staging/production. |
| LLM API | Optional structured request extraction | Phase 15 only. No model/provider assumed. |
| Payment provider | Optional future premium subscriptions | Deferred; hosted checkout only if separately approved. Native retailer checkout, order fulfillment, and manufacturing inventory are outside initial scope. |

### 2.6 Existing implementation versus production readiness

| Evidence | Existing prototype behavior | Missing production work |
| --- | --- | --- |
| `src/App.jsx`, CSS, `src/assets/specs-hero.mp4` | SPECS home/hero, build journey, brief, simulated generation, recommendation/updated workspace, compatibility/replacement panels, catalog, manual builder, saved list, comparison; responsive breakpoints and reduced-motion handling | Preserve composition, assets and workflow. Add API lifecycle states, reliable URLs/deep links, full dialog focus behavior, keyboard/browser/accessibility validation. Source review is not a live GUI test. |
| Preferences and `generateMockBuild` | Budget, five workloads, gaming resolution, 1/2/4 TB, Wi-Fi inputs; threshold-based CPU/GPU swaps from one sample build and a 1.2-second UI timer | Real solver, mandatory constraint checks, infeasibility handling, actual storage/network/target enforcement and measured completion. Selecting 4 TB still selects the 2 TB mock drive; budget thresholds do not ensure an affordable result. |
| `src/data/mockData.js` | 19 sample component records in eight categories, one baseline build, illustrative USD prices and scores | Canonical products, sourced typed facts, offers/currency/freshness, larger validated fixtures, admin data maintenance. Sample values are not validated benchmarks or retailer data. |
| `checkCompatibility` in `src/logic/buildLogic.js` | Local socket, memory, simplified case/form-factor, power-headroom, GPU-fit, cooling and storage messages; local price/power/performance/upgradeability metrics | Cooling check always passes; storage checks a literal interface string, not actual board support; missing pairs are skipped; partial builds can appear compatible; power only checked when PSU and GPU exist; form-factor logic is simplistic. Build a versioned server rule engine with evidence and unknown/incomplete states. |
| Replacement and catalog views | Search by name/spec substring; category filter; details; category picker; replacement preview and price/performance deltas | Structured manufacturer/price/socket/etc. filters, pagination and source metadata. `getReplacementOptions` returns same-category alternatives without compatibility filtering. Catalog “Use in builder” navigates without adding that specific item. Incompatible replacements can be applied, so show draft errors honestly. |
| Saved reducer actions and localStorage effects | Save/open/rename/duplicate/delete and compare selections (up to three); localStorage key `specs-saved-builds` | Browser persistence exists, contrary to “local browser state” wording in one screen. It is not account-backed, isolated per user, revisioned or transactional. Rename appends a fixed suffix rather than requesting a name. Initial read/write effects and unguarded JSON parsing need recovery tests; manual-builder compatibility panel can receive null before a current build exists. |
| `CompareBuilds`, `getBuildMetrics` | At least two selected local builds compared for total, illustrative performance/power/upgrade room/component count | Stable sourced/versioned metrics, server-owned data, timestamps on every total-price view. Empty component sets can produce invalid averaged metrics; guard explicitly. |
| `package.json`, Vite/ESLint config | React 19, Vite 8, JS/JSX; `dev`, `build`, `lint`, `preview` scripts; React and React DOM runtime dependencies | No TypeScript setup, backend, database/migrations, tests/test script, API client, auth, shared URLs, upgrades, real ingestion, admin, containers or CI found in reviewed files. `node_modules` and `dist` exist but do not prove tests or deployment readiness. |

No reviewed feature is certified production-ready. Existing UI and local logic are useful prototype functionality and regression references. Preserve them while replacing their authoritative data paths incrementally. Git status could not be obtained because this checkout did not expose Git repository metadata; do not infer a clean Git worktree from this review.

## 3. Actors and provisional use cases

These `PUC-*` identifiers are **plan-local derived labels**, not IDs from the missing Use Case Specification. Reconcile them with that document if it becomes available; preserve the FR/NFR mapping.

| ID | Actor and use case | Preconditions and significant outcomes/alternates | Basis |
| --- | --- | --- | --- |
| PUC-01 | Guest/user discovers components | Catalog available; search/filter/details return paged products and dated offers; empty or stale/unavailable data is explicit. | FR-01, FR-21 |
| PUC-02 | Guest/user creates or edits a manual build | Public planning permitted; select/remove/replace items, see totals, incomplete states and current validation; reject invalid category IDs. | FR-02–FR-06 |
| PUC-03 | Guest/user understands and repairs a conflict | A draft exists; show rule evidence/responsible parts, preview compatible replacements; report when no safe replacement exists. | FR-04–FR-07, FR-13 |
| PUC-04 | Guest/user requests an optimized build | Structured budget/workload/preferences supplied; return validated complete build/reasons or honest infeasible/unknown/timeout result. | FR-08–FR-12 |
| PUC-05 | Visitor registers/signs in; user manages account | Identity service available; secure account mapping/session, sign-out and deletion; failed login creates no partial account. | FR-15, FR-20; NFR-08, NFR-09 |
| PUC-06 | Registered owner manages saved builds | Authenticated owner; save/open/rename/update/duplicate/delete with revision checks; forbidden or stale updates fail safely. | FR-15, FR-20 |
| PUC-07 | User compares builds | At least two accessible builds; compare dated cost, estimated performance/power/upgradeability with common assumptions. | FR-14 |
| PUC-08 | Owner publishes/revokes; recipient reads share | Owner authorized; immutable read-only snapshot, opaque link, no owner PII; expired/revoked links fail and edits do not change snapshot. | FR-16; architecture 7.3 |
| PUC-09 | Guest/user seeks upgrades | Existing system and retained components supplied; suggest compatible upgrades and trade-offs, or explain infeasibility/unknown facts. | FR-17 |
| PUC-10 | Administrator maintains products/rules/scores | Privileged identity; validated changes, rule/scoring versions, audits; referenced products retire and unsafe rules are rejected. | FR-18–FR-20 |
| PUC-11 | Source operator/worker refreshes offers | Source approved; normalize/match/update/history; quarantine ambiguity, retry outages, expose stale state and job health. | FR-21; architecture 7.2 |
| PUC-12 | Registered user subscribes to alerts; worker delivers | Owned target and consent; threshold event queues deduplicated delivery, retry/failure/unsubscribe visible. | Architecture Accounts/Notifications/Offers workflows; no dedicated FR |
| PUC-13 | Operator validates/deploys/recovers system | Isolated environment and authorized infrastructure; release checks, monitoring, migration and restore evidence. | NFR-03, NFR-06–NFR-08, NFR-14–NFR-16 |
| PUC-14 | Guest/user submits natural-language brief | Optional feature enabled; inspect extracted constraints, run deterministic generation/validation; uncertain parsing asks for correction. | FR-22, FR-23; NFR-18 |

Primary human audiences are first-time builders, gamers, students/professionals, experienced enthusiasts, and people upgrading PCs. They act as guests or registered users. Administrators/catalog operators form a privileged actor. Shared-link recipients require only access to the published snapshot. External identity, offer, email, and telemetry systems are supporting actors; payment/AI actors are conditional.

## 4. Execution rules and dependency order

Run phases in order. A prerequisite means its acceptance criteria passed, not merely that files were created. All production ownership controls precede private persistence; normalized facts precede hardware rules; validated rules precede optimization; versioned builds precede snapshots; durable workers precede provider delivery. Tests and security start early and are expanded throughout.

| Phase | Outcome | Dependencies |
| --- | --- | --- |
| 1 | Preserve prototype; establish architecture, TypeScript and frontend quality baseline | Sources and repository review |
| 2 | Versioned FastAPI/application foundation | 1 |
| 3 | PostgreSQL schema, migrations and repositories | 2 |
| 4 | Identity, ownership, roles and account privacy | 3 |
| 5 | Catalog/search/offers API and first frontend integration | 4 |
| 6 | Build aggregate, costs, revisions and mutations | 5 |
| 7 | Deterministic compatibility and conflict repair | 6 |
| 8 | Deterministic optimization and explanations | 7 |
| 9 | Complete manual/guided frontend integration | 8 |
| 10 | Account-backed saved builds, comparison and immutable sharing | 9 |
| 11 | Existing-PC upgrades | 10 |
| 12 | Durable ingestion and retailer/pricing adapters | 11 |
| 13 | Administrative GUI and notifications | 12 |
| 14 | System qualification, deployment package and operations documentation | 13 |
| 15 | Optional natural-language constraint extraction | 14; optional authorization |

### Command and artifact conventions for future implementation

Only `npm run lint` and `npm run build` among the validation commands below exist today. Do not execute phase commands as part of preparing this plan. Future phases establish the following reproducible conventions; if an existing implementation later uses equivalent names, document the mapping and provide executable commands in its handoff rather than silently skipping validation.

- Phase 1 adds `npm run typecheck`, `npm test -- --run` (Vitest/React Testing Library proposed), `npm run format:check`, and `npm run test:e2e -- <spec>` (Playwright proposed). Tooling is justified by the prescribed frontend/browser quality obligations; avoid overlapping test frameworks.
- Phase 2 adds `backend/pyproject.toml`, pytest, Python formatting/lint via Ruff, and commands run from `backend`: `python -m pytest`, `python -m ruff check .`, `python -m ruff format --check .`. A documented prepared Python environment is a prerequisite; do not assume global packages.
- Phase 3 adds `backend/alembic.ini`, versioned migrations and a local/test database service. From repository root use `docker compose up -d db` only for a documented disposable local database. From `backend`, use `python -m alembic upgrade head` only against that configured database. Never run migration downgrade or destructive fixture setup against user/production data.
- Tests under `backend/tests/{unit,integration,contract,performance,reliability,security}` and `tests/e2e` are proposed paths. The owning phase must create the suites/fixtures it references. Database tests use an explicitly isolated `TEST_DATABASE_URL` and must refuse a production URL. Browser fixtures must launch/configure local frontend and API consistently.
- Every phase with UI changes runs lint, typecheck, frontend tests and build; backend changes run the relevant pytest suites and Ruff. Run the phase-specific commands below in addition. A skipped command is a limitation with a reason, never a pass.
- Future implementers may add files required by their authorized phase. The present planning task authorizes creation of this Markdown file only. No package installation, application edits, database mutation or deployment was performed for this plan.

## 5. Phase prompts

Each fenced block is the complete copy-ready request for that phase. It repeats the governing restrictions so it can be used independently after its prerequisites pass. Expected paths are architectural destinations and may be adjusted to equivalent existing modules after inspection.

### Phase 1 — Preserve the prototype and establish the project foundation

**Objective:** Establish a maintainable structure and regression baseline around the existing frontend.

**Requirements/use cases:** NFR-11–NFR-14; foundation for all FRs and PUCs, especially PUC-01–PUC-04 and PUC-06–PUC-07.

**Prerequisites:** Available sources reviewed; missing use-case document explicitly recorded.

**Expected components:** Existing Vite configuration and application; `src/features`, `src/domain`, `src/api`, `src/test`; TypeScript/test configuration; `docs/architecture`, ADRs, requirement registry and validation instructions. Paths are proposals, not a mandatory cosmetic reorganization.

**Copy-ready implementation prompt:**

```text
Implement only Phase 1 of PHASED_IMPLEMENTATION_PLAN.md for SPECS. Inspect the existing code, local instructions, Business Plan, Reqs.txt, architecture DOCX and DESIGN_REFERENCES.md before modifying anything. Preserve working functionality, the SPECS visual direction, assets, React/Vite project and existing guided/manual/catalog/save/compare workflows. Follow the approved layered modular-monolith architecture; avoid unnecessary dependencies and broad rewrites. Do not implement later phases.

Record the actual baseline and missing formal Use Case Specification; use the plan's PUC labels only as provisional derived labels. Establish architecture decisions for module boundaries, API/persistence ports, gradual JavaScript-to-TypeScript migration, indexed PostgreSQL search initially, identity strategy selection in Phase 4, and future provider choices. Include all eight component categories. Do not invent provider credentials or benchmark facts.

Add incremental TypeScript support and typed frontend domain contracts while keeping existing JSX working. Extract modules only where needed for testability. Add a minimal frontend unit/component harness and browser smoke harness with documented npm scripts: typecheck, test (supporting --run), format:check and test:e2e. Retain dev/build/lint/preview. Capture meaningful workflow regression tests. Fix phase-local baseline defects needed for a reliable foundation: malformed/unavailable localStorage handling, initial hydration/write ordering, empty-build metric safety, and the manual-builder compatibility dialog's null-build path. Do not turn prototype rules into production claims. Preserve local saved data with a validated/versioned envelope and graceful recovery; do not silently erase unreadable records.

Add/update appropriate tests, including repeated page reload, corrupt stored JSON, empty builds, navigation and manual dialog behavior. Run npm run lint, npm run typecheck, npm test -- --run, npm run format:check, npm run build, and npm run test:e2e -- tests/e2e/prototype.spec.ts. Establish those commands in this phase and document prerequisites. Do not add a backend, real authentication, database, retailer integration or optimizer yet. Report files changed, tests performed with results, and remaining limitations.
```

**Acceptance criteria:** Existing screens and navigation still function; saved-data corruption cannot crash startup; empty/manual drafts render safely; TypeScript can coexist with JSX; repeatable scripts and regression tests exist; architecture boundaries and missing sources are documented.

**Tests/commands:** Commands in prompt, including new `tests/e2e/prototype.spec.ts`; manually check existing hero, keyboard navigation, and eight manual slots at narrow/wide widths. This is a regression baseline, not final NFR-11/12 certification.

**Deliverables:** Foundation refactor, typed contracts, test harness, baseline evidence, ADRs and setup documentation.

### Phase 2 — Backend API and application foundation

**Objective:** Introduce a runnable FastAPI modular monolith without connecting unfinished services to the UI.

**Requirements/use cases:** NFR-03, NFR-06, NFR-08, NFR-13, NFR-14; application boundaries supporting all PUCs.

**Prerequisites:** Phase 1 quality scripts and architectural decisions pass.

**Expected components:** `backend/app/{api,application,domain,infrastructure}`, settings, dependency injection, `backend/tests`, `backend/pyproject.toml`, API contract tooling and CI skeleton.

**Copy-ready implementation prompt:**

```text
Implement only Phase 2 of PHASED_IMPLEMENTATION_PLAN.md. Inspect the existing frontend, Phase 1 contracts/tests, source documents, ADRs and local instructions first. Preserve working functionality. Follow the approved React/TypeScript plus Python/FastAPI layered modular-monolith architecture. Avoid unnecessary dependencies; implement only this phase; add/update appropriate tests, run relevant validation, and report files changed, tests performed and remaining limitations.

Create the Python backend with explicit API, application, domain and infrastructure boundaries, dependency-injected services/ports and environment-validated settings. Use /api/v1 JSON routes. Establish typed DTO conventions, safe validation/error envelopes (code, message, correlation ID, field details), correlation middleware, structured redacted logs, bounded request sizes and configurable CORS allowing only intended origins. Define the idempotency and optimistic-revision contract for later commands without inventing business implementations. Never put secrets in VITE variables.

Implement liveness and readiness endpoints; readiness must reflect configured dependency health rather than claim a nonexistent database is ready. Publish OpenAPI and establish deterministic contract validation/client-generation or equivalent typed-client checks. Add a harmless frontend API health adapter without replacing prototype data yet. Add a CI skeleton for existing frontend checks and backend unit/contract/lint checks; keep database and external calls out of this phase. Document Python setup and local launch (python -m uvicorn app.main:app --reload from backend).

Establish pytest and Ruff commands in backend. Test health behavior, settings, invalid payloads, correlation propagation, redaction, allowed/disallowed origins and OpenAPI/error schema. Run each command from backend:
python -m pytest tests/unit tests/contract
python -m ruff check .
python -m ruff format --check .
Run root frontend lint/typecheck/test/build after adapter changes. Do not add fake successful catalog/build/auth endpoints. Report unfinished dependency readiness accurately.
```

**Acceptance criteria:** Backend launches independently; versioned contracts and safe errors exist; readiness is truthful; no business logic in routers; CI validates both code areas without real provider secrets.

**Tests/commands:** Backend commands in prompt; root baseline checks and frontend API-adapter unit tests.

**Deliverables:** API skeleton, health endpoints, contracts, observability baseline, CI and local setup.

### Phase 3 — Database schema, migrations and persistence

**Objective:** Establish transactional source-of-truth storage and schema lifecycle before feature services.

**Requirements/use cases:** FR-02, FR-03, FR-15, FR-16, FR-18, FR-19, FR-21; NFR-09, NFR-15, NFR-16; persistence foundation for PUC-01–PUC-13.

**Prerequisites:** Phase 2 settings, application ports and contract conventions.

**Expected components:** SQLAlchemy models/repositories, Alembic migrations, `compose.yaml`, synthetic fixtures, isolated database tests, schema/data dictionary.

**Copy-ready implementation prompt:**

```text
Implement only Phase 3 of PHASED_IMPLEMENTATION_PLAN.md. Inspect existing code, architecture section 6, Reqs.txt, Phase 1-2 contracts and local instructions before modifying files. Preserve working functionality, follow the approved modular monolith and repository boundaries, avoid unnecessary dependencies, and do not implement later phases. Add/update appropriate tests, run relevant validation, and report changed files, test results and limitations.

Introduce PostgreSQL, SQLAlchemy and Alembic with local disposable DB configuration and no committed credentials. Create versioned schema for users/roles, canonical products and validated category facts/source references, retailers/sources, offers/history, builds/items/revisions, compatibility-rule versions, workload/scoring versions, immutable share snapshots, alert subscriptions, audit events, import jobs and durable event/delivery state. Supporting ingestion/notification tables may be minimal foundations, not working integrations. Document choices and units. Use decimal money/currency, quantities, timestamps and indexes for the documented search/filter paths.

Implement repositories/unit-of-work and constraints: product references, category/cardinality validation, atomic item+revision updates, optimistic concurrency, deduplicated commands/events, safe retirement of referenced products, unique share tokens and no PII in snapshot payloads. Support incomplete drafts and up to 15 items for required tests. Add representative explicitly synthetic seed fixtures; do not treat mock strings as verified hardware facts. Do not expose private data through unauthenticated endpoints.

Create database tests that refuse non-isolated database targets. Test empty-schema migration to head, representative prior-schema upgrade, repeated upgrade, repository CRUD, foreign keys, rollback, duplicate requests and conflicting revisions. Verify migration reversal/recovery only in a disposable database, including preservation strategy for irreversible changes. Use docker compose up -d db at root only for the documented local environment; from backend run python -m alembic upgrade head and python -m pytest tests/integration/test_migrations.py tests/integration/test_repositories.py; then backend lint and unit/contract regressions. Do not touch any existing remote database or deploy.
```

**Acceptance criteria:** Fresh and upgraded databases work; schema supports all required entities, ownership and timestamps; rollback/concurrent writes cannot leave orphaned/incomplete relationships; historical references survive retirement.

**Tests/commands:** Prompt commands against local/test DB only; record schema version and migration evidence. Restoration performance remains Phase 14 work.

**Deliverables:** ER/data dictionary, migrations, repositories, local DB service, test fixtures and integrity evidence.

### Phase 4 — Authentication, authorization and account privacy

**Objective:** Secure user/admin boundaries before private builds or operator writes become available.

**Requirements/use cases:** FR-15, FR-20; NFR-08, NFR-09; PUC-05, authorization foundations for PUC-06/08/10/12.

**Prerequisites:** Phase 3 User/role and repository model; Phase 2 API security conventions.

**Expected components:** Accounts module, identity-provider port/adapter, session/token validation, ownership/RBAC dependencies, account UI and deletion workflow.

**Copy-ready implementation prompt:**

```text
Implement only Phase 4 of PHASED_IMPLEMENTATION_PLAN.md. Inspect existing code, prior phases, source security/privacy requirements and local instructions first. Preserve guest planning and all working prototype functionality. Follow the approved architecture, avoid unnecessary dependencies, implement only this phase, add/update appropriate tests and run relevant validation. Report files changed, tests performed and remaining limitations.

Record an identity ADR: prefer standards-based OIDC with authorization-code/PKCE and a maintained provider integration. No provider is named in the source documents; implement the provider boundary and isolated test provider without pretending it is a production identity service. If a real provider is not configured, report that readiness dependency. Do not implement a custom password system merely to fill the gap. If approved local credentials are selected, use a maintained salted password-hashing implementation and secure recovery, with explicit justification.

Add sign-in/callback/sign-out and minimal profile/account deletion UI consistent with existing SPECS. Validate issuer/audience/signature/expiry and bind external subject identities safely; use short-lived secure sessions/tokens, safe redirect allowlists and CSRF defenses where cookies apply. Never trust browser role/owner fields. Provide deny-by-default admin and reusable owner checks, secure operator provisioning without public admin self-registration, rate limits and secret redaction. Keep catalog/manual/generation guest access available.

Implement data minimization, deletion/anonymization of personal data within 24 hours, session invalidation and handling of owned builds, shares, alerts, logs/audits and backup retention/restoration so deletion does not get undone by restore. Retain only justified nonpersonal audit information. Test the authorization matrix and deletion with a controllable clock; do not claim a simulated clock is live operational evidence.

Create backend tests/integration/test_accounts.py and tests/security/test_authorization.py plus frontend account tests and tests/e2e/accounts.spec.ts. Run those pytest paths, backend lint/regressions, root npm run lint, npm run typecheck, npm test -- --run, npm run build and npm run test:e2e -- tests/e2e/accounts.spec.ts. Cover forged/expired identities, failed callback rollback, guest access, cross-user denial and revoked/deleted accounts. Keep real-provider verification pending if credentials are unavailable.
```

**Acceptance criteria:** Authenticated roles are server-enforced; provider failure creates no partial account; guest planning remains public; deletion meets tested lifecycle rules; production provider configuration is explicit.

**Tests/commands:** Prompt suites plus secure-cookie/token and redirect assertions; no credential material in logs/client bundles.

**Deliverables:** Identity ADR, auth/account UI/API, reusable authorization policy, deletion policy/workflow and security tests.

### Phase 5 — Component catalog, search and offer presentation

**Objective:** Replace catalog mock reads with normalized, paginated data and transparent prices.

**Requirements/use cases:** FR-01, FR-03, FR-21; NFR-03, NFR-11–NFR-13, NFR-19; PUC-01.

**Prerequisites:** Phases 3–4 storage and access policy; public reads remain unauthenticated.

**Expected components:** Catalog/Offers query services, indexed search adapter, public product/offer endpoints, typed client, existing catalog/picker components and source-date presentation.

**Copy-ready implementation prompt:**

```text
Implement only Phase 5 of PHASED_IMPLEMENTATION_PLAN.md. Inspect existing catalog/picker code, contracts, schema, architecture and local instructions before modifications. Preserve working functionality and SPECS styling. Follow approved layer/adapter boundaries, avoid unnecessary dependencies and implement only this phase. Add/update appropriate tests, run relevant validation and report changed files, tests and remaining limitations.

Implement public /api/v1 catalog/category/product/offer queries with cursor pagination, stable sorting, bounded page sizes and safe typed filters for category, brand/manufacturer, price and relevant technical properties (socket, memory generation/capacity, storage capacity, form factor and documented performance data). Return normalized specifications with explicit units, source references and source dates; expose current offers with currency, observation date, freshness and availability. Unknown prices/specs must remain unknown, not zero/current. Retired products are absent from new selection searches but resolvable for historical builds. Use indexed PostgreSQL search behind a replaceable search port with documented fallback; do not introduce a separate search cluster without evidence.

Incrementally connect the existing catalog and picker to the typed client with loading, empty, failed and stale states. Retain an explicit demo/test fixture mode if useful; do not silently fall back to fake live data. Correct Use in builder so the chosen component is transferred to the correct manual slot through the existing state contract; later phases will add authoritative build mutations. Present dataset dates and price uncertainty anywhere this phase displays totals. Use deterministic curated/synthetic fixtures pending approved retailer sources.

Add backend tests/integration/test_catalog.py, tests/contract/test_catalog.py and frontend tests/e2e/catalog.spec.ts plus component/API tests. Validate pagination continuity, filter combinations, SQL injection attempts, stale/missing offers, retired references, exact decimal pricing and item-to-builder handoff. Run these backend suites and lint; run root lint/typecheck/frontend tests/build and npm run test:e2e -- tests/e2e/catalog.spec.ts. Record query performance baseline without claiming the final 100-user load requirement.
```

**Acceptance criteria:** Existing catalog uses API data with reliable filters/paging; chosen items enter the intended slot; dates/unknowns survive end to end; no live-source claims for fixtures.

**Tests/commands:** Prompt suites; query plans/index use checked on representative data; browser empty/error/stale/filter cases.

**Deliverables:** Catalog/offer read API, typed client, updated catalog/picker, indexed queries and source/freshness tests.

### Phase 6 — Build aggregate, costs and transactional management

**Objective:** Implement authoritative build operations, drafts, ownership, totals and revisions.

**Requirements/use cases:** FR-02, FR-03, FR-13, FR-15, FR-20, FR-21; NFR-06, NFR-15, NFR-19; PUC-02, service foundation for PUC-06.

**Prerequisites:** Phase 5 canonical products/offers and Phase 4 ownership policies.

**Expected components:** Builds domain/application/repositories, commands/read DTOs, money/totals service, revision/idempotency storage and API tests.

**Copy-ready implementation prompt:**

```text
Implement only Phase 6 of PHASED_IMPLEMENTATION_PLAN.md. Inspect current build reducers/logic, schema, API conventions, source documents and local instructions before modifying code. Preserve working functionality, follow the approved architecture, avoid unnecessary dependencies and later-phase work. Add/update appropriate tests, run relevant validation and report changed files, tests and remaining limitations.

Implement the server Build aggregate and create/read/update/add/remove/replace/rename/duplicate/delete application commands. Enforce authenticated ownership on saved builds; guest planning uses a validated stateless draft evaluation contract or an explicitly isolated temporary capability, never an unprotected saved-build ID. Permit incomplete/incompatible drafts while distinguishing completeness and validation status. Validate component category, quantity, identifiers and retired-product selection rules. Support the eight required categories and up-to-15-item test cases through meaningful quantities/multiple storage or memory selections.

Calculate costs on the server using decimal amounts and a documented offer/currency selection policy; missing prices produce incomplete estimates. Return source dates, price uncertainty, selected offer references and revision. Build-item changes and revision/totals updates are atomic. Enforce expected revisions, durable idempotency and conflict errors; do not rely on UI checks. Duplicate creates an independent owned aggregate. Deleting builds must preserve or explicitly revoke snapshots according to the documented ownership/privacy lifecycle.

Define compatibility evaluation integration through a domain port and explicitly return not-yet-evaluated/unknown until Phase 7; never report unimplemented rules as passing. Expose safe build endpoints and typed contracts, but leave complete UI migration for Phase 9/10.

Create tests/integration/test_builds.py and tests/unit/test_totals.py. Test every mutation, cross-user denial, category/quantity errors, missing prices, retired references, duplicate retries, rollback, concurrent updates and independent duplication. Run from backend python -m pytest tests/integration/test_builds.py tests/unit/test_totals.py tests/security/test_authorization.py, plus backend lint and contract regressions. Run frontend baseline checks if contracts change. Do not build sharing/optimizer features yet.
```

**Acceptance criteria:** Authenticated CRUD and guest draft boundary are safe; no lost updates, partial saves or double-applied retries; totals and dates are authoritative; incomplete drafts are represented truthfully.

**Tests/commands:** Prompt suites against isolated PostgreSQL, including parallel conflicting writes and injected transaction failure.

**Deliverables:** Build APIs/domain, transactional repositories, totals/read models, revision/idempotency contracts and integrity evidence.

### Phase 7 — Deterministic compatibility and compatible replacements

**Objective:** Replace illustrative checks with versioned rule evaluation and evidence-backed conflict repair.

**Requirements/use cases:** FR-04–FR-07, FR-13; NFR-01, NFR-04, NFR-13, NFR-15; PUC-02–PUC-03.

**Prerequisites:** Phase 6 build/evaluation port and normalized category facts from Phase 5.

**Expected components:** Compatibility domain, declarative rule definitions/versions, evaluation DTOs, fixture corpus, replacement service and API.

**Copy-ready implementation prompt:**

```text
Implement only Phase 7 of PHASED_IMPLEMENTATION_PLAN.md. Inspect prototype checks and data, existing domain/contracts, architecture, Reqs.txt and local instructions before modifications. Preserve working functionality; follow the approved deterministic domain-service architecture; avoid unnecessary dependencies and implement only this phase. Add/update appropriate tests, run relevant validation, and report changed files, tests and limitations.

Implement versioned, deterministic compatibility rules covering CPU/motherboard sockets, supported motherboard/case form factors, memory generation/support, system power and PSU headroom policy, GPU physical clearance, cooler socket/support/height and case clearance, and storage interfaces/capacity of supported connections. Obtain required facts from validated data, not parsing display text. Document any unsupported real-world conditions as unknown; never invent compatibility guarantees. Rule predicates must use a validated safe declarative model or registered code, never arbitrary eval/executable admin code.

Return structured pass/error/warning/unknown evidence: rule/version, responsible product IDs, expected/observed facts and understandable explanations. Keep completeness distinct from compatibility. Evaluate on every add/remove/replace; persist build revision and evaluation reference coherently. Evaluate preview drafts without saving them. Avoid network/provider calls in the critical rule path and define revalidation after catalog/rule version changes.

Implement conflict-repair candidates by same-category search and reevaluation of the entire resulting build. Label a replacement compatible only when supported checks justify it; distinguish partial repairs and unknown data. Return no-candidate outcomes honestly. Preserve the ability to inspect incompatible drafts without presenting them as valid generated builds.

Create at least 100 independently specified valid/invalid/boundary/unknown fixtures in tests/unit/test_compatibility.py, integration tests/integration/test_compatibility.py and a repeatable tests/performance/test_compatibility.py benchmark. Include removed parts, equality clearances, insufficient PSU, cooler failure, actual interface mismatch and up-to-15-item builds. Run those pytest suites and backend lint, then contract/client regression checks. Require 100% expected-case correctness and p95 <=1 second over at least 100 modifications; report environment, timing boundaries and samples. Do not use the prototype's always-pass cooling check as an oracle.
```

**Acceptance criteria:** All seven rule areas and truthful unknown/incomplete states work; ≥100 cases pass; replacements are reevaluated; measured NFR-01 target passes in the documented environment.

**Tests/commands:** `python -m pytest tests/unit/test_compatibility.py tests/integration/test_compatibility.py tests/performance/test_compatibility.py` from `backend`, plus common checks. Phase 9/14 verify browser-inclusive timing.

**Deliverables:** Engine, safe versioned rules, explanation contract, candidate repair API, fixture corpus and benchmark evidence.

### Phase 8 — Optimization, workload profiles and explainable recommendations

**Objective:** Produce complete configurations satisfying mandatory constraints with deterministic scoring.

**Requirements/use cases:** FR-08–FR-12; NFR-02, NFR-05, NFR-13, NFR-17, NFR-20; PUC-04.

**Prerequisites:** Phase 7 authoritative validator/candidate facts; Phase 6 totals; versioned scoring data.

**Expected components:** Constraint DTOs, optimizer service, workload/scoring profiles, recommendation API, explanation records and benchmark scenarios.

**Copy-ready implementation prompt:**

```text
Implement only Phase 8 of PHASED_IMPLEMENTATION_PLAN.md. Inspect existing mock generation/preferences, validated catalog, rule engine, architecture, requirements and local instructions before changing code. Preserve working functionality. Follow approved separation of deterministic optimization from API and optional AI; avoid unnecessary dependencies; implement only this phase. Add/update appropriate tests, run relevant validation and report files changed, tests and limitations.

Implement structured requirements for budget/currency, gaming/development/content creation/productivity/general workloads, storage minimum, network/Wi-Fi, gaming target where applicable and explicit mandatory versus preferred constraints. Validate unsupported or contradictory requests. Use versioned sourced/curated scoring inputs with documented normalization, workload weights, value/power/upgradeability trade-offs and deterministic tie-breaking. Estimates must not masquerade as measured FPS or guaranteed real-world performance.

Implement bounded constraint-based candidate search with prefiltering and a justified algorithm. Add a solver library only if necessary and record why. Enforce all required component roles, budget and mandatory constraints before returning any generated build; run the same compatibility engine on every result. Missing critical facts cannot qualify as success. Return explicit infeasible, unsupported-data or timeout outcomes without silently relaxing mandatory constraints. Capture catalog/offer/rule/scoring versions and selection reasons, including at least CPU, GPU, motherboard, memory and PSU. The 4 TB case must actually meet >=4 TB, and Wi-Fi/target requests must affect constraints or be explicitly unsupported.

Create tests/unit/test_optimization.py, tests/integration/test_optimization.py and tests/performance/test_optimization.py. Cover >=100 feasible generated-build scenarios across all workloads and boundaries, plus additional infeasible requests. Every successful result must satisfy independent budget/constraint assertions and deterministic compatibility; infeasible cases must return no invalid build. Benchmark >=50 requests at up to 300 components, p95 <=10 seconds; compare equivalent 100- and 300-component datasets for median scaling (increase <=300%, median <10 seconds). Document how the source's increase percentage is calculated and report raw medians. Run those pytest suites, backend lint and contract regression tests. Do not add an LLM or paid provider.
```

**Acceptance criteria:** Feasible results satisfy all mandatory constraints and have explanations; infeasible/timeout results cannot appear successful; NFR-02/05/17/20 evidence is recorded, including sample sizes and data provenance.

**Tests/commands:** Prompt suites and common checks; independently verify every successful scenario rather than testing only solver internals. Coverage gate completed in Phase 14.

**Deliverables:** Optimizer/API, constraint schema, scoring profiles/versioning, reason model, scenario corpus and performance report.

### Phase 9 — Integrate guided and manual frontend workflows

**Objective:** Complete API-backed core GUI behavior while preserving the existing frontend design.

**Requirements/use cases:** FR-01–FR-13, FR-21; NFR-01, NFR-10–NFR-12, NFR-17, NFR-19; PUC-01–PUC-04.

**Prerequisites:** Phases 5–8 APIs, Phase 4 account shell and typed contract checks.

**Expected components:** Existing Preferences/Generating/BuildWorkspace/ManualBuilder/panels, feature hooks, API error handling, accessible state/status and navigation.

**Copy-ready implementation prompt:**

```text
Implement only Phase 9 of PHASED_IMPLEMENTATION_PLAN.md. Inspect all existing screens, reducer transitions, API contracts, styling/design references and local instructions before modifying code. Extend the current SPECS React/Vite application; preserve working functionality, hero/assets and visual direction. Follow approved architecture, avoid unnecessary dependencies, implement only this phase, add/update appropriate tests and run relevant validation. Report files changed, tests performed and remaining limitations.

Connect manual edits, structured brief submission, generated recommendations, compatibility inspection, replacement previews/application and updated-build summaries to the authoritative services. Remove the fixed generation timer from real mode and show actual pending/success/infeasible/timeout states. Preserve explicit demo/test mode if retained; no silent mock fallback. Guest workflows must remain usable without sign-in. Map product IDs and item quantities through typed contracts without assuming local mock dictionaries contain server products.

Cancel/debounce obsolete evaluations or use request sequence/revision checks so old responses cannot overwrite newer edits. Display validation unknown/incomplete/error/warning distinctions and rule explanations/responsible parts, not a generic pass badge. Present selection reasons and honest estimate/source/freshness information, with a dataset date on every total-price view. Keep replacement preview separate from applied state and show server concurrency/authorization/validation failures with safe recovery.

Make dialogs keyboard accessible with focus entry/trap/restore, Escape handling, semantic labels, live status announcements and reduced-motion support. Preserve navigation/resume behavior and add stable URL/deep-link handling where needed without a wholesale routing rewrite. Add tests/e2e/build-workflows.spec.ts, tests/e2e/accessibility.spec.ts and frontend integration tests for failed/slow/out-of-order responses, incomplete drafts and guest use. Run root lint/typecheck/tests/build, npm run test:e2e -- tests/e2e/build-workflows.spec.ts tests/e2e/accessibility.spec.ts, and backend API regressions. Measure edit-to-render compatibility latency over >=100 modifications, up to 15 items, against NFR-01; browser automation must support the necessary test fixtures. Final human usability/browser qualification remains Phase 14.
```

**Acceptance criteria:** Core guided/manual workflows run through APIs; race responses cannot corrupt displayed state; no prototype score/rule is used as authority; all totals dated; dialog keyboard and automated accessibility checks pass.

**Tests/commands:** Prompt commands; smoke at 360/900/1440px and API unavailable/stale-data states. Record browser-inclusive latency separately from engine time.

**Deliverables:** Integrated existing GUI, lifecycle/error handling, accessible panels, URL behavior and end-to-end evidence.

### Phase 10 — Saved builds, comparison and read-only sharing

**Objective:** Complete persistent user workflows and immutable public snapshots.

**Requirements/use cases:** FR-14–FR-16, FR-20, FR-21; NFR-08, NFR-09, NFR-15, NFR-19; PUC-06–PUC-08.

**Prerequisites:** Phase 9 integrated editor, Phase 6 owned/revisioned persistence, Phase 4 accounts.

**Expected components:** SavedBuilds/CompareBuilds extensions, comparison query service, share/snapshot module, public route, local import boundary.

**Copy-ready implementation prompt:**

```text
Implement only Phase 10 of PHASED_IMPLEMENTATION_PLAN.md. Inspect existing saved/compare reducers, localStorage schema, ownership APIs, architecture snapshot requirements and local instructions first. Preserve working functionality and existing local data. Follow approved architecture; avoid unnecessary dependencies and later-phase work. Add/update appropriate tests, run relevant validation and report files changed, tests and limitations.

Connect the existing My Builds screen to owner-authorized save/open/rename/update/duplicate/delete APIs. Replace suffix-only rename with validated editable input. Handle revisions, session expiry and conflicts without silently overwriting edits. Offer explicit authenticated import of validated local prototype builds; never automatically attribute shared-device local data to a signed-in account. Keep guest drafts separate and clear account-specific cached data on sign-out.

Implement comparison of at least two accessible builds for dated cost, estimated workload performance, power and upgradeability using consistent versioned assumptions. Allow the current UI's two-to-three-build limit, document it, and show stale/missing data clearly. Compare price assumptions/currency consistently; do not mix currencies or treat unknown price as free. Display dataset dates on every comparison and result total.

Implement owner-created immutable share snapshots with cryptographically random opaque tokens, visibility/expiry, revocation and rate-limited public resolution. Embed user-visible product/offer/rule/scoring facts for the selected revision, never owner PII or private notes. Public links must remain read-only even if requests are forged. Later owner edits/catalog changes must not mutate snapshots. Define revoked/expired/deleted-account/build behavior and audit revocations. Social previews/SEO indexing are optional and must not block sharing.

Create tests/integration/test_saved_builds.py and test_sharing.py, frontend component tests and tests/e2e/saved-comparison-sharing.spec.ts. Test ownership across two users, local-import consent, concurrent rename/update, independent duplication, complete metric/date display, snapshot immutability after product retirement, token guessing/rate limits, expiry, revocation and privacy. Run these pytest paths, backend lint, root lint/typecheck/tests/build and npm run test:e2e -- tests/e2e/saved-comparison-sharing.spec.ts.
```

**Acceptance criteria:** Saved builds persist across devices/sessions with enforced ownership; comparison meets FR-14; public snapshots are immutable, revocable and PII-free; local data is preserved and imported only intentionally.

**Tests/commands:** Prompt suites, malicious direct API requests and date assertions on every price-result/comparison route.

**Deliverables:** Saved/compare GUI integration, comparison API, share module/public page, local import flow and security tests.

### Phase 11 — Existing-PC upgrade recommendations

**Objective:** Fulfill the Should-priority upgrade requirement using shared domain engines.

**Requirements/use cases:** FR-07, FR-17; NFR-04, NFR-05, NFR-17; PUC-09.

**Prerequisites:** Phases 7–10 validated recommendations, scoring, editor and saved builds.

**Expected components:** Upgrade intake GUI, retained-item constraint model, upgrade recommendation service/API and trade-off view.

**Copy-ready implementation prompt:**

```text
Implement only Phase 11 of PHASED_IMPLEMENTATION_PLAN.md. Inspect existing build entry, compatibility/recommendation services, source FR-17, prior tests and local instructions before modifying code. Preserve working functionality. Follow approved architecture and reuse deterministic domain services, avoid unnecessary dependencies and implement only this phase. Add/update appropriate tests, run relevant validation and report files changed, tests and remaining limitations.

Allow users to enter or load an existing PC, choose components to retain, specify upgrade budget/workload/preferences and request alternatives. Document upgrade-budget semantics (new purchases versus total system value); do not infer resale credits or promise bottleneck measurements unsupported by sourced data. Identify unknown legacy components/facts and explain when a safe recommendation cannot be determined. Do not silently replace locked items.

Reuse the optimizer/candidate filters and entire-build compatibility engine. Each proposed upgrade must account for remaining hardware, power, physical fit, storage/network requirements and documented budget policy. Return before/after price, estimated performance/power/upgradeability and concrete reasons/trade-offs, with source dates. Support no-beneficial-upgrade/infeasible/unknown outcomes. Apply a selected upgrade through existing revisioned editor/save commands with ownership checks; guests can plan without an account.

Create tests/unit/test_upgrades.py, tests/integration/test_upgrades.py and tests/e2e/upgrades.spec.ts. Cover locked parts, incompatible legacy sockets/memory, PSU/case limits, no improvement, insufficient budget, missing specs and successful upgrades across workloads. Independently validate all returned complete configurations. Run these pytest paths, backend lint and compatibility/optimization regressions; run root lint/typecheck/tests/build and npm run test:e2e -- tests/e2e/upgrades.spec.ts. Do not add automatic marketing notifications, resale valuation or an LLM.
```

**Acceptance criteria:** Retained parts stay fixed; upgrades are fully checked or explicitly unknown; budget semantics are clear; existing build is unchanged until the user applies a recommendation.

**Tests/commands:** Prompt suites and full deterministic engine regression corpus.

**Deliverables:** Upgrade UI/API, retained-component constraints, reasons/trade-offs and upgrade scenarios.

### Phase 12 — Retailer pricing, durable workers and ingestion

**Objective:** Add approved-source data refresh without coupling interactive workflows to retailer availability.

**Requirements/use cases:** FR-03, FR-21; NFR-03, NFR-06, NFR-19; PUC-11; architecture Offers, workers and external adapters.

**Prerequisites:** Canonical catalog/offers, source-date UI, idempotent event storage and protected operator identity from earlier phases.

**Expected components:** OfferSourcePort, source registry, source-matching/normalization service, worker/scheduler, event/queue adapter, price history, job health and outbound-link service.

**Copy-ready implementation prompt:**

```text
Implement only Phase 12 of PHASED_IMPLEMENTATION_PLAN.md. Inspect existing catalog/offer data, source freshness contracts, event tables, architecture ingestion workflow and local instructions before modifying code. Preserve working functionality. Follow approved ports/adapters and separate API/worker processes, avoid unnecessary dependencies and implement only this phase. Add/update appropriate tests, run relevant validation and report files changed, tests and limitations.

Implement an approved-source registry and provider-neutral OfferSourcePort, a permitted feed/fixture adapter and normalization pipeline. Real retailer providers, terms, credentials and rate limits are unresolved in the sources; connect a real adapter only when explicitly configured with an approved source and permitted access. Do not scrape or fabricate live prices. Fixture ingestion must be labeled synthetic and leave the real-provider acceptance item pending.

Run imports and scheduled refresh in a separate worker sharing application/domain code. Use a durable queue/event adapter with at-least-once semantics, deduplicated handlers, bounded concurrency, backpressure, retry/backoff, dead-letter state, per-source pause/disable and job metrics. Persist state atomically with an outbox or equivalent reliable event mechanism. Avoid adding multiple brokers; document the chosen minimal durable implementation and its limits.

Match external IDs to canonical products with review for ambiguous/unmatched records; never silently merge similar products. Validate monetary/currency/availability/shipping fields, observation/source dates and safe outbound destinations. Upsert current offers, retain meaningful price history, invalidate derived search/cache and publish refresh events. Preserve last-known values with stale/unknown labels during outages. Ensure builds remain usable without retailer connectivity. Add safe direct retailer links; affiliate attribution is optional, isolated behind ReferralPort and falls back to direct URLs. No checkout/payments.

Create tests/integration/test_ingestion.py, tests/contract/test_offer_sources.py, tests/integration/test_workers.py and tests/e2e/price-freshness.spec.ts. Test duplicate delivery, timeout/429, malformed records, ambiguous matches, out-of-order observations, currency mismatch, worker restart, dead letters, source disable and stale display. Run those pytest suites, backend lint and core regressions; root lint/typecheck/tests/build and npm run test:e2e -- tests/e2e/price-freshness.spec.ts. Document approved-provider smoke steps separately and report unconfigured external dependencies honestly.
```

**Acceptance criteria:** Fixture/approved feed refresh is idempotent and durable; ambiguity is quarantined; stale sources are visible; no source call blocks core build operations; production source readiness requires actual permitted-provider evidence.

**Tests/commands:** Prompt suites with adapter fault injection and process restart; no real retailer requests in ordinary CI.

**Deliverables:** Registry/adapters, worker/queue implementation, normalization/history, source-health data, date/link UI and integration runbook.

### Phase 13 — Administration and account notifications

**Objective:** Deliver privileged maintenance workflows and architecture-supported alert delivery.

**Requirements/use cases:** FR-18–FR-21; NFR-08, NFR-09, NFR-13, NFR-15; PUC-10–PUC-12. Notifications are architecture scope, not a newly invented numbered FR.

**Prerequisites:** Phase 4 RBAC, versioned rules/scoring, Phase 12 worker/import health and events.

**Expected components:** Admin endpoints/React console, audit/review services, rule/scoring administration, source-health controls, alert subscription/evaluation and MessageDeliveryPort.

**Copy-ready implementation prompt:**

```text
Implement only Phase 13 of PHASED_IMPLEMENTATION_PLAN.md. Inspect existing roles, catalog/rule/scoring repositories, worker events, architecture administration/notification workflows and local instructions before editing. Preserve working functionality. Follow approved architecture, avoid unnecessary dependencies and implement only this phase. Add/update appropriate tests, run relevant validation and report files changed, tests and remaining limitations.

Build an accessible admin area within the existing frontend and protected server endpoints for product create/update/deactivate/delete, category facts/source references, rule/scoring profile changes, import review/source health and pause/retry controls. Allow hard deletion only for unreferenced products; retire referenced products and preserve historical builds/snapshots. Use optimistic revisions and atomic audit records with sanitized before/after values, actor/time and effective rule/scoring version. Admin UI visibility is not authorization. Reject unsafe rule predicates and arbitrary code; provide preview against the fixture corpus before activation, feature-flagged rollout/rollback and revalidation of affected editable builds without mutating immutable snapshots.

Add owned, consented price/build alert subscriptions and unsubscribe UI. Evaluate thresholds asynchronously from offer/build events and deliver through MessageDeliveryPort with deduplication, bounded retries/backoff, dead letters and visible delivery state. Verification/recovery messages should use the identity provider's supported flows where applicable. No provider is mandated: use a test sink until an approved email service is configured. Do not send real unsolicited messages or store unnecessary personal data. Optional analytics must be consent-aware, allowlisted and nonblocking.

Create tests/integration/test_admin.py, tests/security/test_admin_access.py, tests/integration/test_notifications.py and tests/e2e/admin-alerts.spec.ts. Test guest/non-admin denial, referenced deletion/retirement, version/audit rollback consistency, malicious predicates, rule preview failures, stale revisions, ambiguous import review, duplicate threshold events, delivery retry/dead letters, unsubscribe and account deletion. Run these pytest paths and the full rule/optimizer regression suites, backend lint, root lint/typecheck/tests/build and npm run test:e2e -- tests/e2e/admin-alerts.spec.ts. If a provider is missing, document that production delivery has not passed external smoke validation.
```

**Acceptance criteria:** Catalog/rule/scoring changes are authorized, validated, versioned and audited; historical records survive; source operators can diagnose/control imports; notifications deduplicate and honor ownership/consent/deletion.

**Tests/commands:** Prompt suites, admin authorization matrix and prior engine fixture regression before activating any rule/scoring change.

**Deliverables:** Admin console/API, import review/source controls, safe rule/scoring lifecycle, audit trail, subscription/delivery workflows and provider readiness notes.

### Phase 14 — System qualification, security, deployment and documentation

**Objective:** Collect release evidence for every unconditional requirement and package repeatable operations.

**Requirements/use cases:** All unconditional FRs; NFR-01–NFR-17, NFR-19–NFR-20; PUC-01–PUC-13. NFR-18/FR-23 remain conditional until Phase 15.

**Prerequisites:** Phases 1–13 pass feature gates; configured providers/infrastructure for environment-dependent checks or explicitly recorded blockers.

**Expected components:** CI quality gates, container/worker deployment definitions, staging configuration, security/load/reliability/browser suites, monitoring, backup/restore and incident runbooks, final traceability evidence.

**Copy-ready implementation prompt:**

```text
Implement only Phase 14 of PHASED_IMPLEMENTATION_PLAN.md. Inspect the complete existing application, source NFR thresholds, ADRs, phase evidence and local instructions before changes. Preserve working functionality and follow approved architecture. Avoid unnecessary dependencies; implement only qualification/operations work and fixes necessary for this phase. Add/update appropriate tests, run relevant validation and report files changed, tests with actual evidence and remaining limitations. Do not invent passing results.

Complete reproducible Docker builds for the existing static Vite client, FastAPI and separate worker; environment-separated PostgreSQL and selected managed services; runtime secrets, TLS/reverse-proxy/CORS/security headers, rate limits, health/readiness, structured redacted logs, metrics/traces, source/job alerts, immutable asset/CDN configuration and documented rollback. Keep public pre-rendering/SEO optional and retain the existing client architecture. Add least-privilege credentials, private object storage policies if used, pinned dependencies, vulnerability/secret scanning, CI formatter/linter/contract/tests and >=80% coverage of backend compatibility/optimization logic. Do not treat test fakes as production providers.

Create repeatable suites under tests/performance, tests/reliability and tests/security in backend, and tests/e2e/release.spec.ts plus browser projects for current stable Chrome, Edge and Firefox at 360-1440px. Configure a root npm run test:security script for documented dependency/secret scanning and a backend script scripts/security_check.py to run the selected Python security checks. Require zero unresolved high/critical vulnerabilities; document any tool/network limitation without marking the gate passed. Generate reproducible reports and commands for all checks.

Verify exact source targets: >=100 compatibility fixtures at 100% expected results; >=100 generation scenarios with every successful result compatible, within budget and all mandatory requirements; every generated build has reasons for CPU/GPU/board/memory/PSU. Benchmark >=100 modifications up to 15 items with p95 <=1s (including browser display timing), >=50 generation requests at up to 300 products with p95 <=10s, 100 concurrent users with non-optimization API p95 <=2s/error <1%, 1000 requests with >=99% success and zero partial/corrupt saves, and 100-to-300 catalog median scaling increase <=300% with median <10s. Report timings, failures, hardware, datasets and method, not only averages.

Verify no orphans/partial transactions under CRUD, failures and concurrent updates; cross-user/admin access denial; HTTPS and credential handling; privacy deletion <=24h; zero critical/serious automated accessibility issues plus all core keyboard flows; dates/uncertainty on 100% of total-price pages. Conduct and document a study with >=10 representative first-time users, >=80% generating a valid build and finding its explanation in <=7 minutes unaided. This study needs real participants, not synthetic browser assertions.

Document and rehearse clean-environment deployment <=15 minutes with health checks and database restore <=30 minutes with RPO <=24h. Include encrypted backups, restore isolation and reapplication of account deletions. Configure once-per-minute availability checks for seven consecutive days with >=99.5% availability excluding announced maintenance. Prepare deployment artifacts and local/staging drills only within authorized environments; do not publish a production release, incur unapproved cloud costs or overwrite live databases. Human participation, provider access or seven-day monitoring cannot be fabricated or skipped: leave specific release gates pending and provide exact follow-up steps if unavailable.

Run root npm run lint, npm run typecheck, npm run format:check, npm test -- --run, npm run build, npm run test:e2e -- tests/e2e/release.spec.ts and npm run test:security. From backend run python -m pytest --cov=app.domain.compatibility --cov=app.domain.optimization --cov-fail-under=80, python -m ruff check ., python -m ruff format --check ., python scripts/security_check.py and the documented performance/reliability/security suites. Adjust coverage module paths only to actual equivalents, preserving the 80% logic gate. Use docker compose config and docker compose build for packaging; conduct deployments/migrations/restores only against explicit disposable or authorized staging targets. Update README, API/domain/admin/user docs, threat/privacy models, operational runbooks, ADRs and requirement-to-test evidence. State go/no-go with every unfulfilled requirement listed.
```

**Acceptance criteria:** Automated checks pass; actual measurements meet all applicable thresholds; real usability, seven-day uptime, clean deployment, restore and provider smoke evidence exists or release is explicitly blocked on the named evidence. A test-ready package with pending external evidence is not a production-ready release.

**Tests/commands:** Full commands in prompt. The backend creates named suites and security runner in this phase; `pytest --cov` requires pytest-cov introduced here if not already present. Availability checks yield ≥10,080 scheduled observations across seven days before exclusions; record outage/exclusion calculation. Run the browser matrix against actual Chrome/Edge channels and stable Firefox, not merely a default Chromium binary.

**Deliverables:** Qualification report, updated traceability, deployment package/CI, threat/privacy review, performance reports, usability/browser/accessibility results, monitor evidence, backup/restore drill and runbooks. Production publication requires separate explicit authorization.

### Phase 15 — Optional natural-language build requests

**Objective:** Add optional language-to-constraints intake without changing deterministic validation authority.

**Requirements/use cases:** FR-22, conditional FR-23, NFR-18; reuse FR-08–FR-12, NFR-05/NFR-17; PUC-14.

**Prerequisites:** Phase 14 core release gates; explicit selection of this stretch feature and an approved provider configuration. Missing provider access permits adapter tests, not a claim of live readiness.

**Expected components:** Language extraction port/adapter, validated constraint DTO, review/correction UI, feature flags, bounded provider calls and conditional security tests.

**Copy-ready implementation prompt:**

```text
Implement only optional Phase 15 of PHASED_IMPLEMENTATION_PLAN.md if this stretch feature has been authorized. Inspect existing structured intake, optimizer, deterministic validator, privacy/security rules, architecture and local instructions before modifying code. Preserve all working functionality and the structured-input path. Follow approved architecture, avoid unnecessary dependencies and implement only this phase. Add/update appropriate tests, run relevant validation and report changed files, tests and remaining limitations.

Implement an LLM adapter that outputs only the existing structured constraint schema. No model/provider is named in the sources: use an approved configured provider behind a port and controlled mocks for tests. Bound input size, provider timeout/cost/retries and logging; redact personal data, protect server credentials and feature-flag the interface. Treat model output as untrusted, validate fields/enums/units/budget and show extracted constraints for correction when ambiguous or incomplete. Unsupported requests must be clarified or rejected, not silently relaxed. Do not allow tool execution or data access based on generated instructions.

Pass approved structured constraints to the same optimizer and deterministic budget/compatibility validation used elsewhere. Never display an AI-produced parts list as an accepted build. Missing data, failed parsing, provider failure, infeasibility or validation failure cannot bypass the gate. Retain normal structured intake when the provider is unavailable. Keep model text from becoming active HTML and protect against prompt injection in requests/provider output.

Create tests/unit/test_language_constraints.py, tests/integration/test_language_pipeline.py and tests/e2e/language-brief.spec.ts. Include >=50 varied natural-language requests covering ambiguity, malformed schemas, adversarial instructions, unsupported components, over-budget demands and provider failure. Every presented successful build must pass identical deterministic compatibility/budget/mandatory-constraint checks; rejected requests must not expose invalid recommendations. Use mocked outputs for repeatable tests and separately document approved live-provider validation. Run these pytest suites plus compatibility/optimization/security regressions, backend lint, root lint/typecheck/tests/build and npm run test:e2e -- tests/e2e/language-brief.spec.ts. Update FR-23/NFR-18 traceability and rerun applicable Phase 14 gates before enabling this feature for release.
```

**Acceptance criteria:** ≥50 language scenarios show no validation bypass; all successful outputs are independently validated; untrusted extraction and provider failure are safe; deterministic structured mode remains usable.

**Tests/commands:** Prompt suites, coverage/security regressions and actual approved-provider smoke evidence before live enablement.

**Deliverables:** Optional adapter/intake UI, extraction contract, adversarial corpus, privacy/cost safeguards and conditional release evidence.

## 6. Requirements traceability

Phase numbers below map the actual IDs in `Reqs.txt`. “Qualify” indicates end-to-end evidence/operational gates in addition to feature implementation. Prototype presence does not satisfy a row.

### 6.1 Functional requirements

| ID | Requirement summary / source priority | Implementation phases | Provisional use cases / verification |
| --- | --- | --- | --- |
| FR-01 | Catalog browse/search/filter/specs — Must | 3, 5, 9; qualify 14 | PUC-01; filters/pagination/details and browser tests |
| FR-02 | Manual eight-category build — Must | 3, 6, 9; qualify 14 | PUC-02; mutation/category/quantity UI/API tests |
| FR-03 | Estimated total — Must | 5, 6, 9, 10, 12; qualify 14 | PUC-02/04/07; money, missing-offer, date tests |
| FR-04 | Reevaluate every mutation — Must | 6, 7, 9; qualify 14 | PUC-02/03; add/remove/replace and race tests |
| FR-05 | All specified compatibility problem areas — Must | 3, 7; qualify 14 | PUC-03; ≥100 independent rule cases |
| FR-06 | Explanations/responsible parts — Must | 7, 9; qualify 14 | PUC-03; evidence contract and accessible rendering |
| FR-07 | Compatible replacements — Should | 7, 9, 11; qualify 14 | PUC-03/09; full-build candidate reevaluation |
| FR-08 | Budget/workload/storage/network/preferences — Must | 8, 9; qualify 14 | PUC-04; validation and constraint scenarios |
| FR-09 | Complete constraint-satisfying configuration — Must | 8, 9; qualify 14 | PUC-04; independent completeness/constraint assertions |
| FR-10 | Budget/compatibility/performance/power/value optimization — Must | 8; qualify 14 | PUC-04; scoring/solver scenarios and benchmarks |
| FR-11 | Five workload profiles — Must | 8, 9; qualify 14 | PUC-04; each profile exercised |
| FR-12 | Major-component selection reasons — Must | 8, 9; qualify 14 | PUC-04; reason coverage and UI assertions |
| FR-13 | Modify generated build and recheck — Must | 6, 7, 9; qualify 14 | PUC-02/03/04; generation→edit→reevaluate |
| FR-14 | Compare at least two builds — Should | 10; qualify 14 | PUC-07; consistent cost/performance/power/upgrade metrics |
| FR-15 | Registered-user save/rename/duplicate/update/delete — Must | 3, 4, 6, 10; qualify 14 | PUC-05/06; ownership/persistence/concurrency |
| FR-16 | Read-only sharing link — Should | 3, 10; qualify 14 | PUC-08; token/immutability/revocation/privacy |
| FR-17 | Existing-PC compatible upgrades — Should | 11; qualify 14 | PUC-09; locked parts, legacy data and validation |
| FR-18 | Admin product create/update/deactivate/delete — Must | 3, 4, 13; qualify 14 | PUC-10; authorized lifecycle, retire referenced records |
| FR-19 | Admin rules/performance data — Must | 3, 7, 8, 13; qualify 14 | PUC-10; safe predicates, versions, audit, preview |
| FR-20 | Protect private builds/admin data — Must | 4, 6, 10, 13; qualify 14 | PUC-05/06/08/10; deny/ownership/security matrix |
| FR-21 | Price/spec source or update dates — Should | 3, 5, 6, 9, 10, 12, 13; qualify 14 | PUC-01/07/11; freshness/date/source assertions |
| FR-22 | Natural-language intake — Could/Stretch | Optional 15 | PUC-14; schema extraction and correction |
| FR-23 | Deterministic validation of language builds — conditional Must | 7, 8 foundations; optional 15; requalify 14 gates | PUC-14; ≥50 requests, no presentation bypass |

### 6.2 Non-functional requirements

| ID | Requirement summary | Implementation phases | Evidence / release phase |
| --- | --- | --- | --- |
| NFR-01 | Compatibility responsiveness | 7, 9 | ≥100 modifications, up to 15 items, p95 ≤1s; browser-inclusive qualification 14 |
| NFR-02 | Optimization responsiveness | 8 | ≥50 generation requests, ≤300 catalog components, p95 ≤10s; qualify 14 |
| NFR-03 | API load | 2, 5, 12 | 100 concurrent users, non-optimization p95 ≤2s, error <1%; qualify 14 |
| NFR-04 | Rule accuracy | 7, 11 | 100% of ≥100 known cases; qualify 14 |
| NFR-05 | Generated-build correctness | 8, 11 | ≥100 scenarios, every successful build meets all mandatory constraints and budget; qualify 14 |
| NFR-06 | Reliability | 2, 3, 6, 12 | 1,000 requests, ≥99% success, zero corrupted/partial saves; qualify 14 |
| NFR-07 | Availability | 2, 12, 14 | Minute health checks over seven days, ≥99.5% excluding announced maintenance; actual evidence 14 |
| NFR-08 | Security | 2, 4, 6, 10, 12, 13, 14 | Credential/session/TLS/access tests, zero unresolved high/critical findings; qualify 14 |
| NFR-09 | Privacy | 3, 4, 10, 13 | Minimal PII and ≤24h deletion/anonymization including recovery policy; qualify 14 |
| NFR-10 | First-time-builder usability | 1, 9, 14 | ≥10 representative users, ≥80% unaided success in ≤7min; real study 14 |
| NFR-11 | Accessibility | 1, 5, 9, 10, 11, 13 | Zero serious/critical automated issues plus keyboard completion; qualify 14 |
| NFR-12 | Browser/responsive behavior | 1, 9, 14 | Stable Chrome/Edge/Firefox, 360–1440px critical workflows; qualify 14 |
| NFR-13 | Maintainability | 1–14 | ≥80% backend compatibility/optimization coverage, formatting/lint/CI; consolidated gate 14 |
| NFR-14 | Repeatable deployability | 1, 2, 3, 14 | Clean setup→deployment ≤15min plus health check; drill 14 |
| NFR-15 | Data integrity | 3, 6, 7, 10, 13 | CRUD/rollback/concurrency with zero orphans/incomplete transactions; qualify 14 |
| NFR-16 | Recovery | 3, 4, 14 | Actual restore ≤30min, data loss ≤24h; drill 14 |
| NFR-17 | Explainability | 8, 9, 11 | Required five major-component reasons in 100% of generated builds; qualify 14 |
| NFR-18 | Conditional AI safeguards | 7, 8 foundations; optional 15 | ≥50 language requests, 100% presented builds deterministically valid; requalify before enablement |
| NFR-19 | Price transparency | 5, 6, 9, 10, 11, 12 | Dataset date on every total-price page plus uncertainty; 100% tested result/comparison views, qualify 14 |
| NFR-20 | Optimization scaling | 8 | 100→300 items, median increase ≤300%, median <10s; qualify 14 |

### 6.3 Provisional use-case coverage

| Derived use case | Main phases | Dependencies/validation |
| --- | --- | --- |
| PUC-01 Discover components | 5, 9 | Schema 3; catalog/browser qualification 14 |
| PUC-02 Create/edit manual build | 6, 7, 9 | Catalog 5; mutation and latency tests |
| PUC-03 Inspect/repair conflict | 7, 9 | Build aggregate 6; rule/candidate corpus |
| PUC-04 Optimize structured brief | 8, 9 | Compatibility 7; scenario/performance/reason tests |
| PUC-05 Identity/account lifecycle | 4 | Schema 3; security/deletion qualification 14 |
| PUC-06 Manage saved builds | 6, 10 | Identity 4; ownership/revision/local-import tests |
| PUC-07 Compare builds | 10 | Common metrics/sources; date/visibility tests |
| PUC-08 Publish/read/revoke share | 10 | Snapshots 3 and owned builds 6; abuse/privacy tests |
| PUC-09 Recommend upgrades | 11 | Catalog/build/rule/optimizer reuse; locked-part tests |
| PUC-10 Administer catalog/rules/scores | 13 | Identity 4, rule/scoring versions 7/8; audited mutations |
| PUC-11 Ingest and operate offers | 12, 13 | Source records 3, Offers 5; worker failure/review tests |
| PUC-12 Subscribe/deliver alerts | 13 | Identity/ownership and worker 12; consent/retry tests |
| PUC-13 Qualify/deploy/recover | 14 | Early health/CI/schema foundations 1–3; real operational evidence |
| PUC-14 Interpret language brief | Optional 15 | Structured optimizer 8; deterministic gate and adversarial tests |

## 7. Coverage gaps, decisions and stretch scope

**Uncovered unconditional numbered requirements:** None in the supplied `Reqs.txt` baseline. All FR-01–FR-21, NFR-01–NFR-17 and NFR-19–NFR-20 have planned implementation and verification. This is planned coverage, not completed compliance. FR-22 is intentionally optional; FR-23/NFR-18 become mandatory if FR-22 is implemented. Formal use-case traceability cannot be completed without the missing Use Case Specification.

The following decisions are necessary at the indicated gates. They are not permission requests to execute anything during this planning task.

| Open issue | Resolve by | Proposed handling |
| --- | --- | --- |
| Missing formal SRS title/document and Use Case Specification | Phase 1, revisit whenever supplied | Treat Reqs.txt as the available requirements baseline; reconcile PUC labels against actual use-case IDs later without inventing them. |
| Identity provider and session strategy | Phase 4 | ADR, provider adapter and isolated tests; real access required before production auth readiness. |
| Precise hardware facts, units, headroom, slot/cardinality and supported rule limits | Phases 3, 7 | Validated structured facts, explicit policy/evidence, unknown state for unsupported data; require cooler support. |
| Performance/value/upgradeability scoring, benchmark sources and gaming-target meaning | Phase 8 | Versioned documented scoring, representative curated data, no invented empirical claims; reject unsupported hard targets. |
| Currency/offer selection and upgrade-budget semantics | Phases 5, 6, 11 | Explicit reproducible policies; no hidden conversions, taxes/shipping promises or resale assumptions. |
| Approved retailer sources, licensing, feed formats, affiliate provider and refresh policy | Phase 12 | Provider-neutral ports plus labeled fixtures; actual integration acceptance remains blocked until approved access is configured and tested. |
| Notification service and alert policy | Phase 13 | Test sink and explicit consent/deduplication; live readiness depends on configured provider. |
| Hosting, managed services, search/cache/queue implementation and costs | Phase 1 ADRs; finalize 12/14 | Minimal adapters with durable semantics and measured justification; production-like staging and explicit release authorization. |
| Privacy retention/deletion across snapshots/audits/backups | Phases 4, 10, 14 | Minimize PII, revoke dependent access as required, preserve necessary nonpersonal history and reapply deletions after restores. |
| Human study, seven-day monitoring and recovery/deploy drills | Phase 14 | Schedule real execution, retain evidence; mark pending if unavailable. Automated checks cannot substitute for them. |

Additional business-plan opportunities are outside the initial numbered requirements: premium subscriptions/payments, historical-price analytics UI, automatic lifecycle marketing/price-drop campaigns beyond consented basic alerts, warranties, resale valuation, detailed bottleneck/thermal modeling, professional workstation extensions, community features and native mobile applications. A price-history storage foundation does not promise a full analytics product. Affiliate monetization and public SEO/social previews remain optional adapters/derived behaviors. Payment processing, retailer checkout, orders and fulfillment require separate scope approval and a new plan; do not add them to these phase prompts.

## 8. Planning-task validation

This plan was prepared through read-only workspace inspection and in-memory DOCX text extraction. No packages were installed, application files changed, database operations run, implementation phases executed, or deployment commands executed. Only `PHASED_IMPLEMENTATION_PLAN.md` was created. Application lint/build/test results are intentionally not claimed because running implementation validation was outside this documentation task. The document should be reviewed against newly supplied source versions before future execution.
