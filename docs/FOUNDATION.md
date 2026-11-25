# ZP42 Foundation Documentation

This document consolidates project identity, charter status, model selection policy, safety boundaries, and licensing information for the ZP42 Cyber Reasoning System.

---

## Project Identity

**Public Name**: ZP42

**Expansion**: Zeroth Protocol 42

**Formal Phrase**: ZP42 Cyber Reasoning System

**Public Positioning**: ZP42 is a cyber reasoning system for defensive, active-defense, and sovereign-authorized workflows.

**Prohibited Public Terminology**:
- Do not use internal project codenames in public-facing materials
- Do not use "50/50 offensive" in public descriptions
- Do not use "hack-back", "retaliation", "punishment", or "private offensive action"
- Do not reference unauthorized capabilities

**Approved Public Language**:
- "Defensive cyber reasoning"
- "Active-defense workflows"
- "Sovereign-authorized operations"
- "Governed cyber reasoning system"

---

## Charter Status

**Current Phase**: Foundation (PR #1)

**Foundation Objectives**:
1. Establish safe repository scaffold
2. Define governance and audit framework
3. Implement lane-based authorization policy
4. Create rules of engagement engine
5. Establish human authorization gates
6. Define model allowlist and PRC-origin exclusion policy
7. Create controlled evaluation framework skeleton
8. Implement prohibited-term scanning

**Out of Scope for Foundation PR #1**:
- Model training
- Model weight downloads
- Inference execution
- Cloud resource provisioning
- Telemetry implementation
- Offensive code implementation
- Exploit code implementation
- Live targeting of third-party systems
- Autonomous retaliation or hack-back capabilities

**Next Phases** (Future PRs):
- Phase 2: Model evaluation infrastructure
- Phase 3: Defensive reasoning capabilities
- Phase 4: Active-defense workflows (with appropriate authorization)
- Phase 5: Sovereign-authorized workflows (with human gates)

---

## Model Selection Policy

### Approved Models

ZP42 may reference the following approved models:

1. **AI2 OLMo 3 32B Base**
   - Organization: Allen Institute for AI
   - License: Apache 2.0
   - Use case: General reasoning, defensive analysis

2. **AI2 OLMo 3 32B Think**
   - Organization: Allen Institute for AI
   - License: Apache 2.0
   - Use case: Chain-of-thought reasoning, complex analysis

3. **IBM Granite 4.1 30B Base**
   - Organization: IBM
   - License: Apache 2.0
   - Use case: Enterprise reasoning, code analysis

### Prohibited Model Origins

**PRC-Origin Exclusion Policy**: ZP42 shall not use models, outputs, embeddings, labels, checkpoints, synthetic data, or derivatives originating from organizations or research institutions based in or primarily funded by the People's Republic of China.

**Specifically Prohibited Models**:
- Llama (Meta - excluded by policy decision)
- Qwen (Alibaba Cloud)
- DeepSeek (DeepSeek AI)
- Kimi (Moonshot AI)
- GLM (Zhipu AI / Tsinghua)
- MiniMax (MiniMax)
- Any models trained on PRC-origin datasets
- Any models fine-tuned from PRC-origin base models
- Any embeddings derived from PRC-origin models

### Model Dependency Management

**For Foundation PR #1**:
- No model weights shall be downloaded
- No model inference shall be executed
- No model training shall be performed
- Model references are documentation-only

**For Future PRs**:
- Model downloads must be explicitly authorized
- Model usage must be logged in audit trail
- Model outputs must be verified against safety policies
- Model deployment must follow lane authorization

---

## Safety Boundaries

### Operational Lanes

ZP42 enforces strict lane-based authorization:

#### Lane A: Defensive
**Authorization Required**: Customer authorization or system-level authorization reference

**Permitted Activities**:
- Vulnerability assessment (customer-owned systems)
- Defensive posture analysis
- Security configuration review
- Compliance checking
- Threat modeling

**Prohibited Activities**:
- Live exploitation
- Unauthorized system access
- Data exfiltration
- Persistence mechanisms
- Credential theft

#### Lane B: Active-Defense
**Authorization Required**: Written authorization document reference

**Permitted Activities**:
- Deception technology deployment (customer systems)
- Honeypot/honeytoken management
- Threat hunting (authorized scope)
- Controlled engagement of adversary behavior
- Attribution support (evidence collection only)

**Prohibited Activities**:
- Hack-back operations
- Offensive retaliation
- Unauthorized third-party system access
- Destructive actions
- Autonomous offensive operations

#### Lane C: Sovereign-Authorized
**Authorization Required**: Sovereign authorization reference AND human signoff

**Permitted Activities**:
- Operations explicitly authorized by sovereign authority
- Activities within written rules of engagement
- Actions approved by human command authority
- Operations with explicit legal coverage

**Prohibited Activities**:
- Autonomous decision-making for lethal or destructive actions
- Operations exceeding written authorization scope
- Activities without human-in-the-loop approval
- Unauthorized escalation

### Fail-Closed Policy

**Unknown Lane**: If lane cannot be determined, fail closed and require explicit authorization.

**Invalid Authorization**: If authorization reference is malformed or unverifiable, fail closed.

**Escalation Attempt**: If workflow attempts to escalate lanes without proper authorization, fail closed and log attempt.

### Human Gate Requirements

**Lane A**: No human gate required for routine defensive operations

**Lane B**: Human review required for any active-defense deployment

**Lane C**: Human approval required for every operation

### Prohibited Capabilities (All Lanes)

The following capabilities shall not be implemented in any lane:

1. **Malware creation or deployment**
2. **Credential theft or harvesting**
3. **DDoS attack generation**
4. **Data exfiltration from unauthorized systems**
5. **Persistence mechanism installation**
6. **Evasion technique implementation**
7. **Destructive payload creation**
8. **Autonomous retaliation logic**
9. **Hack-back operations**
10. **Live targeting of third-party systems without explicit authorization**

---

## Audit and Compliance

### Audit Logging

**All Operations**: Every ZP42 operation must be logged with:
- Timestamp (ISO 8601 UTC)
- Operation type
- Lane assignment
- Authorization reference
- Actor identifier
- Operation result
- Any escalation attempts

**Log Format**: Append-only JSONL (JSON Lines)

**Log Location**: `governance/logs/` (gitignored, local dev only)

**Log Retention**: Production log retention policy to be defined in future PR

### Compliance Verification

**Pre-Commit Hook**: Prohibited-term scanner runs on every commit

**CI/CD Integration** (future): Automated compliance checks on every PR

**Manual Review**: All PRs require manual review for compliance with safety boundaries

---

## Round 2 Closure Notes

The ZP42 project was initiated following completion of Parallax Round 2 development. Key architectural decisions carried forward:

1. **Lane-Based Authorization**: Inspired by Parallax's zone-based controls
2. **Fail-Closed Design**: All uncertain states fail to safe mode
3. **Human Gates**: Critical operations require human approval
4. **Audit Logging**: Append-only, immutable audit trail
5. **Model Allowlisting**: Explicit approval required for all models

Lessons learned from Parallax Round 2:
- Governance must be built-in from day one (not bolted on)
- Authorization must be explicit and verifiable
- Autonomous escalation is prohibited
- Human oversight is non-negotiable for sensitive operations

---

## License Notice

**ZP42 is open-source software, released under the MIT License by Naquib Hatami.**

**Open Source License**: This project is licensed under the [MIT License](../LICENSE). You may use, copy, modify, merge, publish, distribute, sublicense, and sell copies, subject to preserving the copyright and permission notice.

**Use**: ZP42 is offered openly for defensive, active-defence, and sovereign-authorised research and deployment. Operators remain responsible for operating it only within authorised scope.

**Distribution**: Redistribution is permitted under the terms of the MIT License.

**Contributions**: Contributions are accepted under the MIT License (see `CONTRIBUTING` where present); contributors retain their copyright and license their contributions under MIT.

---

## Contact and Governance

**Project Owner**: iQs Group Inc.

**Governance Questions**: Contact authorized iQs Group leadership

**Security Concerns**: Report via designated secure channels (to be defined)

**Compliance Issues**: Escalate immediately to project governance team

---

*Document Version: Foundation PR #1*
*Last Updated: 2026-05-18*
