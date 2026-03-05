Here’s the exact debug payload contract and exact wiring requirements your API must implement for x-cie-debug: 1, so your harness + deterministic grader become ironclad without touching your DB run store yet.

Everything below is aligned to how the Agents SDK actually works:
	•	Runner.run() returns a RunResult with finalOutput, output (model items), newItems (agent-associated items), state (serializable), lastResponseId, etc.  ￼
	•	Tracing is wrapped around each run()/Runner.run() by default, and you can set workflowName, traceId, and groupId in RunConfig.  ￼
	•	Function/tool names must match a-z A-Z 0-9 _ - and max length 64.  ￼

⸻

1) Debug mode gate (security + determinism)

Required gating rule

Only include debug if BOTH are true:
	1.	Header x-cie-debug: 1 present
	2.	Server env CIE_DEBUG_AGENTIC=1 (or equivalent) enabled

Optional (recommended):
	•	additionally require NODE_ENV !== "production" OR allowlist IPs

Why: debug includes sensitive tool and model execution metadata; you don’t want it escaping.

⸻

2) Exact API response contract (non-stream /chat)

When debug is OFF:

{
  "ok": true,
  "run_id": "…",
  "trace_id": "trace_…",
  "workflow_name": "CIE.SLB.manager_v2.L2.…",
  "report": { /* ReportSchema */ }
}

When debug is ON (x-cie-debug: 1):

{
  "ok": true,

  "run_id": "mix_cyclone_sea_level_001__t3__1700000000000",
  "trace_id": "trace_abcdef0123456789abcdef0123456789",
  "group_id": "thread_1234", 
  "workflow_name": "CIE.SLB.manager_v2.L2.mix_cyclone_sea_level_001",

  "report": { /* ReportSchema exact */ },

  "debug": {
    "version": "slb_debug_v1",

    "sdk": {
      "agents_sdk_version": "0.4.11",
      "agents_core_version": "0.4.11",
      "mode": "manager_v2"
    },

    "run": {
      "started_at_iso": "2026-02-20T12:34:56.000Z",
      "ended_at_iso": "2026-02-20T12:34:58.500Z",
      "max_turns": 10,
      "turns_used": 4,

      "last_response_id": "resp_…",
      "last_agent_name": "CIE_SLB_Orchestrator_v2"
    },

    "tools": {
      "tool_ledger": [
        {
          "tool_name": "slb_data_geo_admin_lookup",
          "args_hash": "1f2e3d…",
          "attempts": 1,
          "executed": 1,
          "disposition": "executed",
          "first_attempt_iso": "2026-02-20T12:34:56.200Z",
          "last_attempt_iso": "2026-02-20T12:34:56.500Z",
          "receipt_id": "rcpt_8f3a…"
        },
        {
          "tool_name": "slb_data_exposure_population_within_buffer",
          "args_hash": "aa11bb…",
          "attempts": 2,
          "executed": 1,
          "disposition": "executed",
          "first_attempt_iso": "2026-02-20T12:34:56.700Z",
          "last_attempt_iso": "2026-02-20T12:34:57.200Z",
          "receipt_id": "rcpt_09ab…"
        },
        {
          "tool_name": "slb_data_geo_admin_lookup",
          "args_hash": "1f2e3d…",
          "attempts": 2,
          "executed": 1,
          "disposition": "blocked_duplicate",
          "first_attempt_iso": "2026-02-20T12:34:56.200Z",
          "last_attempt_iso": "2026-02-20T12:34:57.400Z",
          "receipt_id": "rcpt_8f3a…"
        }
      ],
      "counters": {
        "tool_exec_count": 9,
        "tool_blocked_count": 1,
        "tool_error_count": 0,
        "signatures_attempted": 10,
        "signatures_executed": 9
      }
    },

    "run_items": [
      // FILTERED model output items (NOT RunItem wrappers)
      // Use result.output and filter to tool events:
      // type: "function_call" | "function_call_result"
      { "type": "function_call", "callId": "call_1", "name": "slb_data_geo_admin_lookup", "arguments": "{...}" },
      { "type": "function_call_result", "callId": "call_1", "output": "..." }
    ],

    "artifacts": {
      "bundle_path": "reports/agentic_runs/mix_cyclone_sea_level_001__t3__1700000000000.bundle.json"
    }
  }
}

Why run_items must be result.output, not result.newItems
	•	RunResult.output is “model data” (messages/tool calls/results) and is what you’d feed into the next run.
	•	RunResult.newItems are RunItem wrappers that include agent association but are harder to serialize and don’t always surface raw function_call / function_call_result shapes cleanly.  ￼

Your harness+grader (the ones you’re implementing) can parse function_call / function_call_result deterministically from result.output.

⸻

3) Streaming route /chat/stream contract

For streaming, do NOT spam debug every event. Only include debug once, in the final event:

Final event: run_finished

Payload includes the same as non-stream response:

{
  "event": "run_finished",
  "ok": true,
  "run_id": "...",
  "trace_id": "...",
  "workflow_name": "...",
  "report": { /* ReportSchema */ },
  "debug": { /* slb_debug_v1 */ }
}

This keeps streaming stable and prevents huge payloads mid-stream.

⸻

4) Exactly how to populate each debug field (source mapping)

4.1 Trace fields (must be deterministic)

Use Agents SDK RunConfig:
	•	workflowName → workflow_name in response  ￼
	•	traceId → trace_id in response (must match trace_<32_alphanumeric> format)  ￼
	•	groupId → group_id in response  ￼

4.2 RunResult fields

From RunResult:
	•	finalOutput → your report (already parsed if outputType is Zod)  ￼
	•	output → debug.run_items (filter tool events)  ￼
	•	lastResponseId → debug.run.last_response_id  ￼
	•	lastAgent.name → debug.run.last_agent_name  ￼
	•	state → DO NOT return by default (too big/sensitive) but DO persist to disk inside the bundle; it’s serializable and useful for recovery.  ￼

4.3 Tool ledger fields

From your shared Context:
	•	context.toolLedger Map → debug.tools.tool_ledger[]
	•	context.tool_exec_count, tool_blocked_count, tool_error_count → counters

Non-negotiable: the ledger must be updated inside tool guardrails/tools so it represents attempts vs executions. This is how you stop arguing about what “tool loop” really means.

⸻

5) The on-disk bundle (this is what makes everything reproducible)

When x-cie-debug: 1 is set, you also write:

reports/agentic_runs/<run_id>.bundle.json

Bundle must include:

{
  "version": "slb_run_bundle_v1",
  "run_id": "...",
  "trace_id": "...",
  "group_id": "...",
  "workflow_name": "...",
  "created_at_iso": "...",

  "report": { /* ReportSchema */ },

  "tool_ledger": [ /* same as debug.tools.tool_ledger */ ],
  "run_items": [ /* same as debug.run_items (filtered result.output) */ ],

  // Optional but gold:
  "run_state": { /* result.state (serializable) */ },
  "raw_responses_count": 5
}

Why:
	•	The grader can operate off the bundle alone.
	•	You can rerun grading without rerunning models.
	•	You can diff “before/after” fixes with real artifacts.

⸻

6) Two crucial correctness checks your agents must implement now

Check A — traceId format contract

Your trace id must be trace_<32_alphanumeric>.  ￼
If you generate a hex hash of length 32 you’re fine.

Check B — tool name contract

Every tool name must match allowed characters and max length 64.  ￼
Your tool registry/sanitizer is mandatory.

⸻

7) Implementation instructions (exactly what to build)

Tell your agents:

Implement debugEnabled
	•	In API handler:
	•	debugEnabled = req.headers["x-cie-debug"] === "1" && process.env.CIE_DEBUG_AGENTIC === "1"

Ensure runSlbChatTurn (or equivalent) returns:
	•	report (ReportSchema)
	•	result (RunResult) or at least: lastResponseId, lastAgent.name, output
	•	context snapshot: ledger + counters
	•	trace_id, workflow_name, group_id

Construct debug object exactly as slb_debug_v1
	•	run_items = filtered result.output for tool events:
	•	keep only type === "function_call" and type === "function_call_result"
	•	tool_ledger = Array from context ledger
	•	bundle_path = where you wrote bundle json

⸻

8) Why this instantly unblocks you

Once this is in place:
	•	your harness stops relying on “DB evidence” or “OpenAI dashboard vibe”
	•	your grader gets deterministic input:
	•	tool signatures attempted/executed
	•	duplicates blocked vs duplicates executed
	•	report evidence referential integrity
	•	trace IDs always present

That’s how you stop chasing rabbits.

⸻

If you want, next I’ll give you:
	•	a Zod schema for slb_debug_v1 (so debug payload itself is validated),
	•	and a one-file “bundle writer” helper that both API and scripts can call, so you never re-implement artifact logic twice.