# PMP Route Guardian Repo Index Routing-Only Decision — 2026-05-13

Status: LOCKED SCOPE

## Decision

Route Guardian Repo Index is a routing truth index, not a deletion or cleanup machine.

## Reason

The repository deletion/remodel work was already handled by earlier repo sweep and remodel extraction work.

Repo Index should not duplicate that work.

## Repo Index job

Repo Index answers:

```text
What changed recently?
What is the current approved route?
Does pmp-current-map.json agree with Route Guardian expected currentInner?
Is there a newer candidate/support file that is not approved as current?
Is the Home Screen current route still pointed at the right stable path?
```

## Repo Index must not do

```text
No deletion decisions.
No archive decisions.
No cleanup decisions.
No auto-promoting newest file.
No rewriting pmp-current-map.json.
No changing Route Guardian expected path.
```

## Current v1 scope

```text
newest-to-oldest recent repo activity
current map proof
Route Guardian expected-path proof
map-vs-Route-Guardian agreement check
file classification for routing relevance
copyable report
```

## Main rule

Newest does not mean correct.

Correct means:

```text
current approved stable path + map agreement + Route Guardian agreement + pass receipts
```

Deletion permission: false
Archive permission: false
Auto-promotion permission: false
