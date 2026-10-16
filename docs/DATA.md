# DATA

## `Event` API schema

| Field | Shape | Access pattern | Constraint |
|---|---|---|---|
| `event_id` | Non-empty string | Exact lookup and idempotency | Primary key; max 255 characters in storage |
| `source` | Non-empty string | Stored with the event | Required |
| `event_type` | Fixed string enum | Filter/categorization | Deployment, log, metric, trace, alert, or kubernetes_event |
| `service` | Non-empty string | Future incident grouping and indexed lookup | Required; indexed |
| `timestamp` | Timezone-aware datetime | Future time-window correlation and indexed lookup | Required; indexed |
| `severity` | Fixed string enum | Future prioritization | debug, info, warning, error, or critical |
| `message` | Text | Evidence display and future retrieval | Required |
| `metadata` | JSON object | Source-specific fields | Required object, defaults to `{}` |

## Storage choice

The `events` table is append-oriented for this milestone. `event_id` supports fast idempotency/readback, and `service` plus `timestamp` indexes support the first incident-correlation queries. JSON metadata avoids schema churn for source-specific fields, at the cost of less predictable indexing until query patterns are known.

Expected first scale: thousands to low millions of events in a portfolio deployment, not unbounded production telemetry.
