---
name: trader-trainer-replay-correctness
description: Use for replay time, seek, bars, timeframe synchronization, indicator inputs, playback speed, execution snapshots, and recovery. It is for correctness work, not UI polish or new trading features.
---

# Replay Correctness

## Required invariants

- One canonical simulation time and one ordered event cursor.
- No future tick, bar, indicator value, or cached projection may survive a backward seek.
- Sequential playback to time T, deterministic seek/rebuild to T, and restart recovery at T must produce equivalent market state.
- Bar aggregation uses timestamp buckets, not tick-count grouping.
- Active timeframe labels must correspond to actual bar duration.
- Incomplete-bar behavior is explicit.
- Indicator warm-up and confirmation rules are explicit.
- Speed changes affect playback scheduling without dropping market events.
- Trading consumes only accepted post-tick execution snapshots.

## Required test matrix

- dense ticks;
- sparse ticks and gaps;
- duplicate timestamps with deterministic source ordering;
- minute, hour, day, and week boundaries;
- backward and forward seek;
- replay finish;
- restart recovery;
- Training, Exam, and Review restrictions;
- long fixture and performance fixture.

## Review checklist

- no string-only timestamp ordering when parsed time is required;
- no linear full-dataset seek in the final indexed implementation;
- no UI-owned bar or indicator calculations;
- no synthetic market events that were not present in the normalized data;
- no acceptance claim based only on projection text.