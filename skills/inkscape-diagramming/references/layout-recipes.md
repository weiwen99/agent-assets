# Layout recipes

## Architecture plate

**Question answered:** what runs where, which boundary owns control, and which external systems it calls.

1. Place clients or upstream actors at the left or top.
2. Draw the main system boundary as the dominant light-gray panel.
3. Put the synchronous control path on one horizontal spine.
4. Put durable stores below the owning component.
5. Put providers and external capability seams at the right.
6. Put asynchronous feedback, event fan-out, and recovery paths above or below the spine as broad arcs.
7. Put shipped deployment-opt-in elements at the perimeter with dashed borders.

Aim for 4–7 boundaries and 12–20 nodes. Collapse leaf implementations into one node when they share ownership and lifecycle. Keep technology names as secondary labels; the primary label states the role.

A component belongs inside the boundary that owns its lifecycle. An external provider stays outside even when an adapter for it runs inside.

## Business-flow plate

**Question answered:** how an external actor reaches a business-visible outcome and where they can intervene.

1. Put the initiating actor at the left.
2. Put the primary service or decision hub in the center.
3. Put downstream actors/capabilities at the right.
4. Number the happy path in causal order.
5. Draw immediate requests as straight arrows.
6. Draw results and feedback as broad arcs returning above or below the main row.
7. Keep no more than four side branches; each must change an observable outcome or user action.
8. Show terminal states explicitly. Distinguish a sub-step completion from the whole process outcome.

Use verbs on arrows and nouns inside boxes. A label such as `6. 执行工具` belongs on an arrow; `ToolDispatch` belongs in a node. Put constraints beside the gate they constrain, not in a detached legend.

## Logic or data-flow plate

**Question answered:** how inputs become outputs, or how a decision selects a path.

1. Inputs left/top; outputs right/bottom.
2. Transformations are rectangles; durable data is a cylinder.
3. Use a diamond only when two or more outgoing branches have explicit predicates.
4. Label every conditional edge with its predicate.
5. Merge branches at a named transformation or state, not at an unexplained line junction.
6. Use one broad return arc for iteration rather than many crossing backward arrows.

## Routing rules

- Attach to node sides at stable ports: left/right center for horizontal flow, top/bottom center for vertical flow.
- Leave at least 28 px between an arrowhead and neighboring text.
- Keep parallel edges separated by at least 24 px.
- A cubic return arc should clear intervening nodes by at least one node height.
- Use at most three orthogonal bends in one connector.
- When two connectors would cross, first reorder nodes; only then reroute.
- Give edge labels an opaque white backplate with 8–12 px horizontal padding and 5–8 px vertical padding.

## Density and omission

Every diagram needs an omission sentence in its semantic map: what a reader might expect but this viewpoint intentionally excludes. Do not solve crowding by shrinking text. Remove an adjacent abstraction level or split the diagram.

Current-state status is binary in geometry:

- solid: active core;
- dashed: shipped, deployment-opt-in;
- absent: proposed or irrelevant to the viewpoint.

Do not use dashed lines for ordinary asynchronous traffic on the same plate; label that traffic instead. One visual channel must keep one meaning.
