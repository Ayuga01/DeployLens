# DATA

## `Event` API schema

| Field | Shape | Access pattern | Constraint |
|---|---|---|---|
| `event_id` | Non-empty string | Exact lookup and idempotency | Primary key; max 255 characters in storage |
| `source` | Non-empty string | Stored with the event | Required |
| `event_type` | Fixed string enum | Filter/categorization | Deployment, log, metric, trace, alert, or kubernetes_event |
| `service` | Non-empty string | Incident grouping and indexed lookup | Required; indexed |
| `timestamp` | Timezone-aware datetime | Time-window correlation and indexed lookup | Required; indexed |
| `severity` | Fixed string enum | Future prioritization | debug, info, warning, error, or critical |
| `message` | Text | Evidence display and future retrieval | Required |
| `metadata` | JSON object | Source-specific fields | Required object, defaults to `{}` |

## Storage choice

The `events` table is append-oriented for this milestone. `event_id` supports fast idempotency/readback, and `service` plus `timestamp` indexes support the first incident-correlation queries. JSON metadata avoids schema churn for source-specific fields, at the cost of less predictable indexing until query patterns are known.

Expected first scale: thousands to low millions of events in a portfolio deployment, not unbounded production telemetry.

## `IncidentCorrelation` response

`GET /incidents/correlate` accepts a non-empty `service` and timezone-aware
`start_time`/`end_time` query parameters. The interval is inclusive. The
response contains the original query values, `event_count`, chronologically
ordered `events`, alphabetically keyed `counts_by_type` and
`counts_by_severity`, and `latest_deployment`, which is the final deployment
in the same timestamp/event-ID order or `null` when none match.

The query is deterministic: service and timestamp predicates execute in the
repository, and `event_id` breaks timestamp ties. A valid unknown service or
empty window returns zero, empty maps/lists, and a null latest deployment;
missing timezone information or a reversed window returns HTTP 422.
