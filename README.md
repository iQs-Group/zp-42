# ZP42 Cyber Reasoning System

**ZP42** (Zeroth Protocol 42) is a cyber reasoning system for defensive, active-defense, and sovereign-authorized workflows.

## Project Identity

- **Public Name**: ZP42
- **Expansion**: Zeroth Protocol 42
- **Formal Phrase**: ZP42 Cyber Reasoning System
- **Positioning**: Defensive, active-defense, and sovereign-authorized cyber reasoning

## Architecture

ZP42 is built with strict safety boundaries and governance controls:

```
zp42/
├── core/              # Core reasoning capabilities
│   ├── models/        # Model integration interfaces
│   ├── eval/          # Controlled evaluation framework
│   └── snapshot/      # Manifest and snapshot tooling
├── orchestrator/      # Central control and routing
│   ├── lanes/         # Lane-based authorization
│   ├── roe/           # Rules of engagement engine
│   └── human_gate/    # Human authorization gates
├── verifiers/         # Output verification and validation
├── benchmarks/        # Safe evaluation benchmarks
├── governance/        # Audit logging and compliance
├── compliance/        # Model allowlists and policy enforcement
├── docs/              # Technical documentation
├── tests/             # Test suites
└── scripts/           # Utility scripts
```

## Safety Boundaries

ZP42 enforces strict operational boundaries:

- **Lane A**: Defensive workflows requiring customer/system authorization
- **Lane B**: Active-defense workflows requiring written authorization
- **Lane C**: Sovereign-authorized workflows requiring sovereign authorization + human signoff

All operations are:
- Governed by rules of engagement (ROE)
- Subject to audit logging
- Gated by human authorization where required
- Verified against model allowlists
- Tested against prohibited terms

## Model Policy

ZP42 only references approved models:
- AI2 OLMo 3 32B Base
- AI2 OLMo 3 32B Think
- IBM Granite 4.1 30B Base

No PRC-origin models, outputs, embeddings, labels, checkpoints, synthetic data, or derivatives are permitted.

## Development

**Requirements**: Python 3.11+

**Setup**:
```bash
pip install -e .
```

**Validation**:
```bash
# Compile all Python files
python -m compileall .

# Run tests
python -m pytest -q

# Scan for prohibited terms
python scripts/scan_prohibited_terms.py --root .
```

## License

ZP42 is proprietary software. See `docs/FOUNDATION.md` for licensing details.

## Governance

All ZP42 operations are logged for audit purposes. See `governance/` for audit schema and logging implementation.
