---
name: jev-codex
description: Use TypeSafe AI's Jev model as a bounded, structured judgment layer while planning software design or coding work. Use when a task has concrete alternatives to compare, prioritization, risk scoring, or a focused yes/no judgment. Do not use for implementation, free-form explanations, exact calculations, or as a substitute for inspecting project evidence.
---

# Jev-Codex

Use Jev as an optional decision aid inside Codex. Codex remains responsible for understanding the request, inspecting the repository, doing the work, and explaining the result. Jev contributes focused judgments; it does not write plans or code.

## Workflow

1. Inspect the user request and relevant project evidence first. Reduce the decision to small, concrete questions.
2. Use Jev only when its answer could change a design or coding choice. Send only the minimum necessary context; do not send the entire conversation, repository, secrets, or unrelated source files.
3. If `TYPESAFE_API_KEY` is unavailable, Jev returns an API error, or the task is not suited to a typed judgment, continue using normal Codex reasoning and repository evidence. Never invent a Jev result.
4. Submit JSON to `scripts/jev_decide.py` from this skill directory. The request follows TypeSafe's System One API schema: `state`, `questions`, and optionally `model`.
5. Use `choice` for named alternatives, `score` for a rubric, and `noul` for a focused yes/no judgment. Keep questions atomic; combine separate judgments in code or in Codex's own synthesis.
6. Treat the result as evidence, not authority. Consider the selected value and confidence/probabilities. For consequential or low-confidence choices, inspect evidence further or ask the user. Jev must not approve destructive changes, security-sensitive actions, deployments, or external side effects.
7. Explain the decision in ordinary language and distinguish Jev's judgment from facts found in the project. Do not claim certainty from a confidence score.

## Example request

```json
{
  "state": {
    "task": "Choose an integration shape for a reusable Codex decision helper",
    "constraints": ["works across projects", "small initial implementation", "no UI"],
    "alternatives": {
      "skill": "A global Codex skill invokes Jev for bounded decisions",
      "mcp": "A standalone MCP server exposes Jev as a tool"
    }
  },
  "questions": {
    "approach": {
      "type": "choice",
      "instructions": "Which approach best fits the stated constraints?",
      "criteria": {
        "skill": "Simple to install globally with minimal runtime infrastructure",
        "mcp": "Best when an always-available reusable tool interface is required"
      }
    }
  }
}
```

Run from the skill directory:

```powershell
Get-Content request.json -Raw | python scripts/jev_decide.py
```

The helper reads `TYPESAFE_API_KEY` from the environment, calls the official TypeSafe endpoint, and prints the structured response as JSON. Keep the key out of source control and request data.
