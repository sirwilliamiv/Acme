# shunt — a POC of the "Portal cut my token usage by 90%" trick

A working proof of concept of the idea behind
[*Portal by Spotify cut my Claude Code token usage by 90%*](https://engineering.atspotify.com/2026/9/portal-by-spotify-cut-my-claude-code-token-usage-by-90):

> Don't pay frontier-model prices to shovel bytes.

Reading a file is not a reasoning task. But when Claude Code calls `Read`, the
entire file lands in the context of whatever model you're driving — and stays
there, resent on every subsequent turn. `shunt` intercepts those reads, has a
cheap model digest the file, and hands the expensive model the digest instead.

```
                    WITHOUT shunt                          WITH shunt
                    ─────────────                          ──────────
  Claude Code       Read(pipeline.py)                      Read(pipeline.py)
       │                    │                                     │
       │                    │                            ┌────────▼────────┐
       │                    │                            │ PreToolUse hook │
       │                    │                            └────────┬────────┘
       │                    │                                     │ 7,515 tok
       │                    │                            ┌────────▼────────┐
       │                    │                            │  Haiku 4.5      │  $1/MTok
       │                    │                            │  "bulk-reader"  │
       │                    │                            └────────┬────────┘
       │                    │                                     │ 697 tok digest
       ▼                    ▼                                     ▼
   Opus 5 context    7,515 tokens  ·  $0.0376          697 tokens  ·  $0.0035
                                                              ↑ 91% less
```

> **Provenance note.** The Spotify domain is blocked from this sandbox, so this
> POC was reconstructed from search summaries of the article plus Claude Code's
> documented hook API. The mechanism (`PreToolUse` hooks + cheap-model
> delegation + declarative "modes") matches what those summaries describe; the
> specific code here is mine, not Spotify's.

---

## Run it in 15 seconds

No API key, no dependencies, no network:

```bash
python3 demo/run_demo.py
```

That drives the real hook with the exact JSON Claude Code would send, across
six scenarios, then prints the savings ledger. Then run the tests:

```bash
pip install pytest && python3 -m pytest tests/ -q     # 27 tests
```

To use the real cheap model instead of the offline stub:

```bash
pip install anthropic
export ANTHROPIC_API_KEY=sk-ant-...
SHUNT_PROVIDER=anthropic python3 demo/run_demo.py
```

To actually run it inside Claude Code: `.claude/settings.json` is already
wired. Open this repo in Claude Code and ask it to read a large file.

---

## 1. The mechanism: how a `PreToolUse` hook hijacks a tool call

This is the part worth internalizing, because it generalizes far beyond token
saving.

Claude Code fires hooks at lifecycle points. `PreToolUse` fires *after* the
model has decided to call a tool but *before* the tool runs. Your hook is just
a process. Claude Code writes JSON to its stdin:

```json
{
  "session_id": "abc123",
  "hook_event_name": "PreToolUse",
  "tool_name": "Read",
  "tool_input": { "file_path": "/repo/pipeline.py" }
}
```

Your hook writes JSON back on stdout:

```json
{
  "hookSpecificOutput": {
    "hookEventName": "PreToolUse",
    "permissionDecision": "deny",
    "permissionDecisionReason": "…"
  }
}
```

**Here is the trick.** `permissionDecision: "deny"` cancels the tool call, and
`permissionDecisionReason` is text that gets shown *to the model*. It's meant
for "you may not read that file." But it is an arbitrary string, delivered to
the model, in place of the tool result.

So: deny the read, and put the digest in the reason. The model asked for a
file, and got a summary of that file. It never sees the bytes, and never pays
for them. `shunt/hook.py:47` is those nine lines.

Print nothing and exit 0, and the tool runs normally. That's the "allow" path —
and it's what every failure mode falls back to.

---

## 2. The parts

| File | Job |
|---|---|
| `shunt/hook.py` | The hook process. stdin → decision → stdout. |
| `shunt/policy.py` | **Should this read be intercepted?** The important file. |
| `shunt/modes.py` + `shunt/modes/*.json` | Declarative agents: prompt + model + params, as data. |
| `shunt/providers.py` | Executes a mode against Haiku 4.5, or an offline stub. |
| `shunt/cache.py` | Content-addressed digest cache. |
| `shunt/ledger.py` | Records every shunt so savings are measured, not assumed. |
| `.claude/settings.json` | Wires the hook to the `Read` matcher. |

### Modes: the actual Portal idea

The article's core abstraction is the **mode** — a declarative agent, defined
as configuration rather than code. `shunt/modes/bulk-reader.json`:

```json
{
  "name": "bulk-reader",
  "model": "claude-haiku-4-5",
  "max_tokens": 1500,
  "temperature": 0,
  "system": "You are a bulk reader. …",
  "user_template": "File: {path}\n\n<file>\n{content}\n</file>\n\n{question}"
}
```

Nothing in `hook.py` knows which model runs. Moving this workload from Haiku to
Sonnet, or sharpening the digest prompt, is a one-line edit to a JSON file.
That reframing — *model routing as configuration, not systems engineering* — is
what the article is really selling. The plumbing is 200 lines; the leverage is
that you can retune it without touching the plumbing.

`code-writer.json` is a second mode (generate boilerplate to spec) included to
show the registry is general. It is **not** hooked up to `Write`/`Edit` by
default, deliberately — see the honesty section.

---

## 3. The policy is the whole engineering problem

Anyone can write the interception. The interesting question is *when not to*.
Every rule in `shunt/policy.py` exists because a wrong answer is expensive:

| Rule | Why |
|---|---|
| Only files ≳2,000 tokens | Below that, the round trip costs more than it saves. |
| Never when `offset`/`limit` is set | A targeted read means the model already knows what it wants. Summarizing it answers a question nobody asked. |
| Never for `.json`, `.lock`, `.env`, `.csv`, `.sql`, `.pem`, lockfiles | An *approximate* version pin is worse than useless. Some files need exact bytes. |
| Never binary, never `node_modules/`, never `.git/` | Obvious, but must be explicit. |
| **Never the same file twice in one session** | The escape hatch. |

That last one is the most important line in the project.

A lossy view of the codebase is a trap the agent can't see. If the digest omits
what it needs, it re-reads the file — and if you shunt it *again*, it loops
forever on a summary that will never contain the answer. So the second read of
any file always passes through verbatim, and the digest **tells the model this**:

> If you need the exact contents, read it again — the second read of a file in
> a session is always passed through verbatim. For a specific region, use Read
> with offset/limit, which is never intercepted.

Two escape routes, both advertised. A context optimizer without an escape hatch
isn't an optimization, it's a lobotomy.

The same reflex governs failure: `hook.py` catches everything and exits 0. If
the cheap model 429s, if the network is down, if the SDK isn't installed —
the file gets read normally. Verified in
`test_hook_never_blocks_on_malformed_input`. **A token optimizer must never be
able to break the editor.**

---

## 4. Where the 90% actually comes from

Run the demo and the ledger reports 91%. Three separate effects stack, and it's
worth knowing which is which, because only two of them are about model routing:

**(a) Compression — the digest is smaller than the file.**
7,515 tokens → 697. That alone is 91% of the *ingest*.

**(b) The loop multiplier — this is the big one.**
Agent context is cumulative. A file read on turn 3 of a 20-turn session is
resent on turns 4 through 20. Removing 7,000 tokens from context doesn't save
7,000 tokens; it saves 7,000 × (remaining turns). This is why a headline number
can be large even when per-read compression is modest — and why the ledger's
table, which counts each file once, is the *conservative* view.

**(c) The price delta — Haiku 4.5 at $1/MTok vs Opus 5 at $5/MTok.**
5× on the input side. Real, but the smallest of the three.

Note what (a) and (b) have in common: they're about **not putting bytes in
context**, and they'd work even if the digester were the same model. The
cheapest token is the one you never send. Model routing is the third-largest
lever here, which is the opposite of how the headline reads.

**Honest caveats on that 91%:**

- The demo fixture is synthetic and repetitive, so it digests unusually well.
  Your real files will compress less.
- Token counts use a `len/4` heuristic (`config.estimate_tokens`). For
  billing-grade numbers use `client.messages.count_tokens`; I used the
  heuristic because it runs on every single `Read` and has to cost nothing.
- **It ignores prompt caching entirely.** With a warm cache, re-sent context
  bills at a fraction of the input rate — which shrinks lever (b) substantially.
  If you're not already using prompt caching, do that *first*: it's free and it
  costs no accuracy. `shunt` trades a little fidelity for cost; caching doesn't.
- The comparison is per-read, not per-completed-task. If the digest is bad
  enough that the agent needs three extra turns to recover, you lost money.
  **Measure cost per finished task, not per request.**

---

## 5. What's POC and what would need real work

Being straight about the gap:

| Works | Not production |
|---|---|
| Full hook contract, verified against the documented API | The real `anthropic` path is **untested** — this sandbox has no API key. The stub path is covered by 27 tests. |
| Policy, escape hatch, cache, ledger, chunking | No concurrency control on the cache or ledger files |
| Graceful degradation on every failure | Cache never evicts; `.shunt/` grows forever |
| Offline demo + tests | No eval measuring digest *quality* — the thing that actually decides if this is a good idea |

That last row is the real gap. This POC measures tokens saved. It does not
measure whether the agent still does correct work — and that's the number that
determines whether the whole idea pays off. Before running something like this
on real work, build an eval: a set of tasks, run with and without the hook,
scored on task completion. If completion drops 5% to save 40% of tokens,
whether that's a good trade is a judgment call you can only make with the
number in hand.

Hooking `Write`/`Edit` to a `code-writer` mode (the article's second mode) is
left off for the same reason. Delegating *reads* costs you fidelity. Delegating
*writes* costs you correctness, silently, in code that looks fine.

---

## 6. Things to try

1. `SHUNT_MIN_TOKENS=500 python3 demo/run_demo.py` — watch the threshold move.
2. Edit `bulk-reader.json` to `"model": "claude-sonnet-5"`. Note that no Python
   changed. That's the point of modes.
3. Delete the "already shunted this session" check in `policy.py`, then ask
   Claude Code to find an exact constant in a large file. Watch it loop.
4. Add a `Grep`/`Glob` matcher to `.claude/settings.json` and digest large
   search results — often a bigger win than file reads.
5. Build the eval from §5. It's the most valuable thing left undone here.

---

## References

- [Portal by Spotify cut my Claude Code token usage by 90%](https://engineering.atspotify.com/2026/9/portal-by-spotify-cut-my-claude-code-token-usage-by-90) — the source article
- [Hacker News discussion](https://news.ycombinator.com/item?id=49571465)
- [Claude Code hooks reference](https://code.claude.com/docs/en/hooks)
- [MCP in Portal](https://backstage.spotify.com/docs/portal/core-features-and-plugins/mcp/overview)
