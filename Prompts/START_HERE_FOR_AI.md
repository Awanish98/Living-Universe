# START HERE

You are receiving this repository as the specification and starter scaffold for Living Universe.

At EVERY session start, first read `AGENT_RULES.md`, `PROJECT_MEMORY.md`, and `TASK_STATE.json`.

Read these in order:
1. AI_BUILD_INSTRUCTIONS.md
2. ROADMAP.md
3. ARCHITECTURE.md
4. PROJECT_STRUCTURE.md
5. IMPLEMENTATION_CHECKLIST.md
6. GEMINI_INTEGRATION.md

Then implement the project end-to-end.

Important:
- Do not stop at the scaffold.
- Replace all `NotImplementedError` placeholders.
- Keep the application runnable after each phase.
- First make the offline simulation fully functional.
- Then add optional Gemini integration.
- Run tests and fix failures.
- Keep dependencies reasonable for an 8 GB laptop.
- Do not require a local LLM.
- Do not hardcode any API key.
- Do not execute arbitrary code from Gemini.
- Deliver a clean, documented, runnable project.

Definition of success: launching the app produces a visible living 2D universe where organisms consume resources, survive, reproduce, mutate, die, and evolve; the UI shows useful statistics; the engine is reusable; Gemini can optionally observe/control the world through validated structured commands.
