# ZP42 — Documentation

The complete documentation set for **ZP42 (Zeroth Protocol 42)**, an open, MIT-licensed, governance-first cyber-reasoning system for defensive, active-defence, and sovereign-authorised workflows. Invented and authored by Naquib Hatami; published by SADI AI Inc. / iQs Group Inc.

The project is a **Foundation-phase scaffold**: the governance components exist as independent modules — `lane_policy`, `audit_logger`, `scan_prohibited_terms`, and `capture_manifest` have dedicated unit-test suites, while `roe_engine` and `human_gate` are implemented but not yet unit-tested — and the end-to-end orchestrator, output verifier, signed audit log, and enforced compliance are specified for later phases.

The project charter, lane definitions, model policy, and safety boundaries live in [`FOUNDATION.md`](FOUNDATION.md), which sits alongside these documents and is the authoritative normative source.

## Vision and foundations

- [`00-vision.md`](00-vision.md) — Why ZP42 exists, the "capability must follow authorisation" principle, and the lane model at a glance.
- [`01-whitepaper.md`](01-whitepaper.md) — Technical whitepaper: the governance-first thesis and trust as an engineering target.
- [`02-srs.md`](02-srs.md) — Software Requirements Specification: testable requirements for every governance module.

## Architecture and design

- [`03-architecture.md`](03-architecture.md) — High-level design: components, trust boundaries, and the specified pipeline.
- [`04-detailed-design.md`](04-detailed-design.md) — Detailed module design, data structures, and the implemented-vs-specified map.

## Governance controls

- [`05-lane-model.md`](05-lane-model.md) — The lane authorisation model (A, B, C, UNKNOWN) and fail-closed assignment.
- [`06-roe-engine.md`](06-roe-engine.md) — The rules-of-engagement engine, capability sets, and global prohibitions.
- [`07-human-gate.md`](07-human-gate.md) — The human-in-the-loop approval gate and its lifecycle.
- [`08-governance-audit.md`](08-governance-audit.md) — The append-only audit logger, schema, and evidence model.
- [`09-compliance-allowlists.md`](09-compliance-allowlists.md) — Model allowlist, licence manifest, and PRC-origin exclusion policy.

## Safety, threats, and assurance

- [`10-threat-model.md`](10-threat-model.md) — Threats, trust boundaries, mitigations, and fail-closed behaviour.
- [`11-safety-boundaries.md`](11-safety-boundaries.md) — Prohibited capabilities and the boundaries beneath every lane.
- [`12-test-strategy.md`](12-test-strategy.md) — Test plan, what is covered today, and the gaps still to close.
- [`13-conformance.md`](13-conformance.md) — Conformance statements that make governance obligations testable.

## Integration and operations

- [`14-integration.md`](14-integration.md) — How the components compose toward the specified pipeline, and the integration gap.
- [`15-operations-runbook.md`](15-operations-runbook.md) — Day-2 operating procedures and validation steps.
- [`16-deployment.md`](16-deployment.md) — Deployment topology, environments, and promotion gates.

## Guides

- [`17-adoption-guide.md`](17-adoption-guide.md) — How to adopt ZP42's controls in your own process.
- [`18-developer-guide.md`](18-developer-guide.md) — Developer manual for working inside the repository.
- [`19-user-guide.md`](19-user-guide.md) — User-facing guide to running the governance controls.

## Reference

- [`20-related-work.md`](20-related-work.md) — Prior art (zero-trust PDP/PEP, OPA, HITL) and an honest gap analysis.
- [`21-authorization-model.md`](21-authorization-model.md) — The authorisation model, references, and check ordering in depth.
- [`22-glossary.md`](22-glossary.md) — Definitions of every term, each tagged by implementation status.
- [`23-faq.md`](23-faq.md) — Frequently asked questions, with an authoritative status table.
- [`24-roadmap-adr.md`](24-roadmap-adr.md) — Phase roadmap and architecture decision records.

## Repository root

- [`../README.md`](../README.md) — Project overview and repository layout.
- [`../LICENSE`](../LICENSE) — MIT License (Naquib Hatami).
