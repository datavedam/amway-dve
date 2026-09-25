---
name: kafka-topic-contract
description: Check the Kafka contract for an integration before any route is built — topic names against the team naming rule, and producer serializer settings (auto.register.schemas must be false, a subject-name strategy must be set). Use when the user says "check the topic name", "name a new topic", "review the Kafka contract", "is this producer config right", or proposes a new *_pub_v1 topic. Do NOT use for registering schemas, creating or deleting topics, reviewing .proto field changes (use a schema-review skill), or writing routes (use camel-integration-author).
---

# Kafka topic contract

Stage 2 of the integration lifecycle. A topic name and its producer settings are a contract with
every consumer. Check them before design, not after deploy.

## Rules
- Topic names are written with `{env}` as a placeholder, e.g. `valuechain_{env}_000_unshippedqty_pub_v1`.
- The naming pattern lives in `reference/naming.yaml`. **It is a DRAFT built from two known
  examples — confirm it with the team.** If a real Amway topic fails the check, the pattern is
  wrong, not the topic: raise it, do not "fix" the topic name.
- Producers: `auto.register.schemas` must be `false`. The agent never registers a schema.
- Producers must set a value subject-name strategy. The GI standard is
  `com.amway.kafka.custom.serializers.subject.AmwaySubjectNameStrategy`.
- Kafka endpoints are never hand-written in a route. They are route-template instances
  (`eda-proto-producer`, `eda-proto-consumer`, `eda-avro-consumer`) set in properties.

## Workflow
1. Collect every topic the flow reads or writes (from the intake brief or diagram).
2. Check names:
   ```
   python scripts/check_topic.py valuechain_{env}_000_unshippedqty_pub_v1
   ```
   Quote the name in shells that expand braces.
3. If a producer is involved, check its properties file:
   ```
   python scripts/check_props.py .support/application.properties
   ```
4. Report PASS/FAIL per topic and per setting. For a FAIL, say which rule and propose the fix;
   the principal and the producer team approve contract changes.

## Evidence
Both script outputs, pasted into the review.

## Self-test
```
python scripts/check_topic.py selftest
python scripts/check_props.py selftest
```
