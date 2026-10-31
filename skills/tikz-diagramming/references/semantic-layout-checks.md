# Semantic and layout checks

## Grounding ledger

Before drawing, record every item in two tables kept in scratch context:

```text
node | label | owner/boundary | status | evidence
edge | source | target | direction | label/condition | evidence
```

The final diagram must account for every row. Preserve full detail by default; a smaller semantic view requires explicit user approval.

## Ownership and boundaries

A node belongs inside the boundary that owns its process, state, and lifecycle. An adapter running in the application stays inside; the remote service it calls stays outside. Code existing in a repository does not prove a deployment-opt-in component is active.

Check every boundary twice:

1. node geometry is physically inside or outside as intended;
2. labels and connectors do not visually imply different ownership.

## Status notation

- solid node: current core;
- dashed node: implemented and shipped, but deployment-opt-in;
- proposed node: absent from a current-state plate or isolated in a labeled proposal area.

A dashed connector to an optional node uses the same status treatment. Do not reuse dashed styling for ordinary asynchronous flow on the same plate; label asynchronous semantics in text.

## State and safety semantics

Distinguish acknowledgment, derivation, persistence, and authorization. A user confirmation can acknowledge risk without creating, clearing, or downgrading a server-derived state. Draw security gates before the execution they constrain, and route persistent state through its owning entity.

Use canonical terms from the project glossary. Avoid replacing a monotonic fact with a reversible “mode,” or a server-owned derivation with a client-supplied flag.

## Completion levels

Separate sub-step completion from whole-process terminal states. A tool round, child completion, batch completion, or intermediate commit is not automatically the user-visible outcome. Name terminal states explicitly and show retry/recovery paths only where they actually exist.

## Edge audit

For each connector verify:

- arrowhead direction matches the ledger;
- both endpoints land on intended node borders;
- bidirectional arrows represent two real directions;
- the path does not enter an unrelated node;
- the label describes that exact path;
- the label backplate does not hide an arrowhead;
- parallel paths are separated enough to trace;
- return arcs clear intervening nodes and labels.

## Density audit

At fit-to-window scale, every node title, detail line, CJK label, numbered step, and terminal state must remain identifiable. Resolve crowding in order:

1. widen the canvas;
2. increase gaps and reroute;
3. wrap text deliberately;
4. split into an additional diagram only with user approval.

Do not delete grounded content or reduce text below the visual-system floor merely to make the picture sparse.
