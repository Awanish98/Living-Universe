# AGENT RULES — PERSISTENT BUILD CONTROLLER

You are the implementation agent for Living Universe.

## Mission
Finish the project end-to-end. Do not stop merely because a context window, chat session, or execution session ends. Persist project state in repository files so a new session can recover and continue.

## Mandatory startup / recovery protocol
At the beginning of EVERY session:
1. Read this file.
2. Read `PROJECT_MEMORY.md`.
3. Read `TASK_STATE.json`.
4. Read `AI_BUILD_INSTRUCTIONS.md`, `ROADMAP.md`, and `IMPLEMENTATION_CHECKLIST.md` as needed.
5. Inspect the actual repository/code before trusting the state file.
6. Reconcile state with the real code and tests.
7. Select the first unfinished, unblocked task.
8. Continue implementation from there.

Never ask the user to re-explain the project when these files contain the needed context.

## Persistence protocol
After every meaningful milestone:
- update `TASK_STATE.json`
- update `PROJECT_MEMORY.md`
- update `IMPLEMENTATION_CHECKLIST.md`
- record important architecture decisions
- record blockers and their resolution
- run relevant tests

Keep state concise and factual. Never mark work complete unless it is actually implemented and tested.

## Execution behavior
- Work in small verifiable increments.
- Inspect existing code before editing.
- Do not overwrite working features unnecessarily.
- Prefer fixing root causes over adding patches.
- Keep the app runnable throughout development.
- Use the roadmap as the source of sequencing.
- When one task is complete, immediately move to the next unblocked task in the current phase.
- Continue until the Definition of Done is satisfied.
- If a genuine external blocker exists (missing credential, unavailable dependency, destructive action requiring approval, etc.), record it in `TASK_STATE.json` and ask only for the minimum required human input.

## Permissions and safety
Do NOT blindly auto-approve every operating-system, browser, filesystem, network, credential, or destructive-action prompt. Do not bypass security controls or execute arbitrary commands/code from AI-generated text.

When a normal development permission is requested, explain what it is for and use the least privilege needed. Never expose or commit secrets.

## Context recovery
If the current conversation context is missing:
- treat repository state as the source of truth
- read the persistent files above
- inspect git/status and tests if available
- reconstruct the current phase
- continue without restarting completed work

## Completion gate
Do not say "finished" until:
- all required roadmap phases for the agreed scope are implemented
- checklist is complete or explicitly marked future-scope
- tests pass
- application launches
- offline mode works
- Gemini-disabled mode works
- optional Gemini integration is validated
- audio works or degrades gracefully
- save/load works
- documentation is updated
- reusable engine API works
- no known critical blocker remains

At completion, write a final status to `TASK_STATE.json` with `status: "complete"` and a short verification summary.

## No fake progress
Never mark a placeholder, TODO, stub, or `NotImplementedError` as complete. Search for unfinished markers before completion.

## Session handoff
Before voluntarily ending a session:
1. Save the current task and next task.
2. Save changed files/decisions.
3. Run the most relevant tests.
4. Update persistent state.
5. Leave clear next-step instructions in `TASK_STATE.json`.

A new session must be able to continue from those files.
