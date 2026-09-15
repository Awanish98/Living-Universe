# Living Universe Versioning System

The owner controls when the project moves to a new major stage.

## Release stages

Use:

```text
ALPHA → BETA → GAMMA → RELEASE
```

Within a stage, use incremental versions:

```text
Alpha 1.0
Alpha 1.1
Alpha 1.2
Alpha 1.3

Beta 2.0
Beta 2.1
Beta 2.2

Gamma 3.0
Gamma 3.1

Release 4.0
Release 4.1
```

The exact numbering is project-controlled. Do not automatically advance to the next stage.

## Owner-controlled promotion

The AI MUST NOT move Alpha → Beta or Beta → Gamma on its own.

Only move stages when the owner explicitly says something equivalent to:
- "Move to Beta"
- "Start Beta"
- "Move to Gamma"
- "Release 1.0"

If the owner says "continue Alpha", remain in Alpha and increment the patch/minor version as appropriate.

## Version meanings

### Alpha
Experimental development.

Allowed:
- architectural changes
- incomplete UI
- experiments
- breaking internal changes
- performance experiments

Requirement:
- core functionality should run, but polish is not required.

### Beta
Feature-complete stabilization.

Allowed:
- bug fixes
- performance work
- UI refinement
- compatibility fixes
- controlled feature additions

Requirement:
- primary feature set is implemented and reasonably tested.

### Gamma
Release-candidate / hardening.

Focus:
- stability
- performance
- persistence reliability
- provider reliability
- security
- UX
- regression testing

Avoid large architectural rewrites unless necessary.

### Release
Stable version.

Focus:
- bug fixes
- security
- compatibility
- documentation
- maintenance

## Version state file

Keep current version in:

`VERSION_STATE.json`

Example:

```json
{
  "stage": "alpha",
  "version": "1.2",
  "owner_promotion_required": true,
  "last_change": "Added multi-provider AI architecture",
  "next_version": "1.3"
}
```

## Every version

For each version:
1. Update `VERSION_STATE.json`.
2. Update `CHANGELOG.md`.
3. Update `TASK_STATE.json`.
4. Run relevant tests.
5. Record migration/breaking changes.
6. Keep a short release note.

## Version boundaries

A big architectural or feature milestone should normally start at `.0` of the next stage:

```text
Alpha 1.x
      ↓ owner says Move to Beta
Beta 2.0
      ↓
Beta 2.1
Beta 2.2
      ↓ owner says Move to Gamma
Gamma 3.0
```

Never infer the owner's promotion decision.
