# FLOW

## POST /events

```text
POST /events
  -> FastAPI parses JSON
  -> Event schema validates fields, enums, and timezone-aware timestamp
  -> session dependency opens one SQLAlchemy session
  -> repository reads events.event_id
      -> no row: insert, commit, refresh, return 201
      -> same payload: return stored row, change response to 200
      -> different payload: return 409
  -> response model serializes the persisted event
  -> session closes
```

The unique primary key is the final database guard against concurrent duplicate IDs. If a concurrent insert wins the race, the route re-reads the row and applies the same identical/conflicting-payload rule.

## GET /events/{event_id}

```text
GET /events/{event_id}
  -> open session
  -> repository selects by primary key
      -> row found: convert ORM model to Event and return 200
      -> no row: return 404
  -> session closes
```
