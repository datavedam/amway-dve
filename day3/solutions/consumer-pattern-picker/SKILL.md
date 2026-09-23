---
name: consumer-pattern-picker
description: Pick one of the six certified Camel Kafka consumer patterns for a GI integration and write its properties. Use when designing a Kafka consumer bundle, choosing how a consumer behaves when the target (e.g. OEBS) is down, or asked "which consumer pattern", "serial or concurrent", "circuit breaker", "manual commit". Do NOT use for MFT / Composer flows, producers, or REST-sourced integrations.
---

# Consumer pattern picker

Stage 3 (Design) of the integration lifecycle. Turns three answers into one
certified pattern, its properties, and an ADR paragraph.

## Ask first (one round, recommend an answer for each)
1. **Ordering** — must messages for the same key be processed in order?
2. **Throughput** — roughly how many messages per minute at peak? (OPEN if unknown)
3. **Target down** — when the target (e.g. OEBS) is unavailable, should the
   consumer **stop**, **retry and then stop**, or **park the message and continue**?

## Choose
| Answers | Pattern | Key settings |
|---|---|---|
| Strict order, low volume | Serial | `maxInFlightRequest=1`, `consumersCount=1`, `maxPollRecords=1` |
| No order need, high volume | Concurrent | `maxInFlightRequest>=5`, `consumersCount>=5`, `maxPollRecords>=10` |
| Target down → stop, lose nothing | Circuit breaker (fail-fast) | `allowManualCommit=false`, `autoCommitEnable=true`, `pollOnError=STOP`, `breakOnFirstError=true` |
| Target down → retry, then stop | Circuit breaker (half-open) | `pollOnError=RETRY`, `breakOnFirstError=true`, `retries>=3`, `retryBackoffMs` |
| Bad message → park it, continue | Error handler | `pollOnError=ERROR_HANDLER`, `breakOnFirstError=true`, redelivery policy |
| Commit only after the OEBS write succeeds | Manual commit | `allowManualCommit=true`, `autoCommitEnable=false`, `KafkaOffsetManager` bean |

Source of truth: `camel-integration-author/reference/authoring-rules.md`
(Kafka — consumer management & error handling). If it disagrees with this
table, that file wins.

## Rules
- Manual **or** auto commit — never both.
- `breakOnFirstError=true` is required with `pollOnError` = `ERROR_HANDLER`, `RECONNECT` or `RETRY`.
- `retries` only applies with those same `pollOnError` values.

## Output
1. The properties block for the template instance.
2. Run `python scripts/check_pattern.py <properties-file>` — must PASS.
3. An ADR paragraph: pattern, why, and **what happens to a message when the target is down**.
