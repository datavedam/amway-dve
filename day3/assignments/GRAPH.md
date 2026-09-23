# Day 3 — Hands-on: Graph (map what exists before you build)

Stage 1 (Intake) and stage 8 (Change) both start with the same question:
**what already exists, and what is connected to what?** Today that answer lives
in people's heads, Confluence pages and diagrams. A knowledge graph puts it in
one place the agent can query — with every link labelled as found in the
source (EXTRACTED) or guessed (INFERRED), so you can tell fact from inference.

## Step 1 — Build a graph of today's material
Inside Claude, in `day3/`:
```
/graphify lab
```
**Observe:** read `graphify-out/GRAPH_REPORT.md`. Which nodes are the most
connected? Is `valuechain_{env}_000_unshippedqty_pub_v1` one of them?

## Step 2 — Add your own material
Point it at something real from your team — your `gi-ai-skills` folder, one
bundle repo, or an exported Confluence space:
```
/graphify <path-to-your-folder> --update
```
**Observe:** how many nodes are EXTRACTED vs INFERRED? Pick one INFERRED edge
and check it by hand. Was the guess right?

## Step 3 — Ask the intake question
```
/graphify query "What reads from or writes to the valuechain unshipped quantity topic, and which service account has access?"
```
**Observe:** does the answer cite where each fact came from? Anything it
couldn't find should come back as unknown — not invented.

## Step 4 — Ask the impact question (stage 8)
```
/graphify path "Manhattan" "Oracle E-Business Suite"
```
**Observe:** the path is the integration chain. Now imagine the protobuf
schema on the topic changes — which nodes on that path are affected?

## Step 5 — Make it a habit
Ask Claude:
> Add a line to CLAUDE.md telling you to query graphify-out/ before answering
> any question about which systems, topics or bundles are connected.

**Observe:** start a new session and ask a connection question. Does it go to
the graph first?

**Discuss:** who keeps this graph current? (Hint: `--update` only re-reads
changed files — it can run on every merge.)
