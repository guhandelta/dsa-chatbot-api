# Embedded C Debug Exercises

A RAG-training corpus of 300 debugging exercises for Embedded C. Corrected code is editorial training material and must be stripped from learner-facing challenge responses.

## Coverage

- Easy: 100 exercises
- Medium: 100 exercises
- Hard: 100 exercises
- Perspectives: memory, ownership, concurrency, timing, APIs, errors, security, persistence, and testing

## EC-E-001: work in ISR

- Difficulty: Easy
- Language/platform: Embedded C
- Perspective: Interrupts
- Concept: work in ISR
- Symptom: The device misses deadlines or deadlocks.
- Diagnostic goal: Keep handlers short and defer work.

### Buggy code

```c
void ISR(void) { printf("edge"); read_sensor(); }
```

### Expected diagnosis

I/O, allocation, and slow calls inside an ISR are unsafe and unbounded.

### Corrected code

```c
volatile bool pending; void ISR(void) { pending = true; }
```

### Regression tests

```c
assert_main_loop_services_pending();
```

## EC-E-002: blocking delay

- Difficulty: Easy
- Language/platform: Embedded C
- Perspective: Timing
- Concept: blocking delay
- Symptom: A periodic task drifts.
- Diagnostic goal: Schedule against a monotonic deadline.

### Buggy code

```c
delay_ms(period); task();
```

### Expected diagnosis

Sleeping before work accumulates execution time as drift.

### Corrected code

```c
if (now >= deadline) { task(); deadline += period; }
```

### Regression tests

```c
assert_periodic_deadline_does_not_drift();
```

## EC-E-003: missing volatile

- Difficulty: Easy
- Language/platform: Embedded C
- Perspective: Volatile
- Concept: missing volatile
- Symptom: The main loop never sees a flag change.
- Diagnostic goal: Mark memory changed by hardware or ISR as volatile.

### Buggy code

```c
bool ready = false;
while (!ready) {}
```

### Expected diagnosis

The optimizer may cache a nonvolatile flag in a register.

### Corrected code

```c
volatile bool ready = false;
while (!ready) {}
```

### Regression tests

```c
assert_flag_change_is_observed();
```

## EC-E-004: off-by-one ring buffer

- Difficulty: Easy
- Language/platform: Embedded C
- Perspective: Buffers
- Concept: off-by-one ring buffer
- Symptom: Full and empty states are confused.
- Diagnostic goal: Track count or reserve one slot.

### Buggy code

```c
buffer[head++] = value;
```

### Expected diagnosis

The head wraps without checking capacity and overwrites unread data.

### Corrected code

```c
if (count < CAPACITY) { buffer[head] = value; head = (head + 1) % CAPACITY; count++; }
```

### Regression tests

```c
assert_full_buffer_rejects_new_value();
```

## EC-E-005: heap fragmentation

- Difficulty: Easy
- Language/platform: Embedded C
- Perspective: Memory
- Concept: heap fragmentation
- Symptom: Long uptime causes allocation failure.
- Diagnostic goal: Use fixed storage for bounded messages.

### Buggy code

```c
uint8_t *packet = malloc(length);
```

### Expected diagnosis

Repeated variable allocations fragment a small heap.

### Corrected code

```c
uint8_t packet[MAX_PACKET]; if (length > sizeof packet) return ERR_TOO_LARGE;
```

### Regression tests

```c
assert_oversized_packet_rejected();
```

## EC-E-006: raw units mistaken for volts

- Difficulty: Easy
- Language/platform: Embedded C
- Perspective: ADC
- Concept: raw units mistaken for volts
- Symptom: Control thresholds trigger at the wrong level.
- Diagnostic goal: Calibrate raw codes at the hardware boundary.

### Buggy code

```c
float volts = raw;
```

### Expected diagnosis

An ADC code needs reference voltage and resolution conversion.

### Corrected code

```c
float volts = raw * reference / ((1u << bits) - 1u);
```

### Regression tests

```c
assert_full_scale_equals_reference();
```

## EC-E-007: partial frame

- Difficulty: Easy
- Language/platform: Embedded C
- Perspective: UART
- Concept: partial frame
- Symptom: A split message is parsed as corrupt.
- Diagnostic goal: Accumulate until a complete delimiter/frame exists.

### Buggy code

```c
if (byte == ">") parse(frame);
```

### Expected diagnosis

A terminator may arrive in a later interrupt and a partial frame is discarded.

### Corrected code

```c
if (append(byte)) { if (byte == ">") parse(frame); }
```

### Regression tests

```c
assert_split_frame_reassembles();
```

## EC-E-008: feed before work

- Difficulty: Easy
- Language/platform: Embedded C
- Perspective: Watchdog
- Concept: feed before work
- Symptom: A stuck task keeps the watchdog alive.
- Diagnostic goal: Feed only after essential work succeeds.

### Buggy code

```c
watchdog_feed();
run_control_loop();
```

### Expected diagnosis

The watchdog proves loop entry, not successful progress.

### Corrected code

```c
run_control_loop(); watchdog_feed();
```

### Regression tests

```c
assert_failed_work_does_not_feed();
```

## EC-E-009: busy wait

- Difficulty: Easy
- Language/platform: Embedded C
- Perspective: Power
- Concept: busy wait
- Symptom: Sleep current is too high.
- Diagnostic goal: Use a timer or wake event rather than polling.

### Buggy code

```c
while (!event) { }
```

### Expected diagnosis

The CPU remains active while waiting for hardware.

### Corrected code

```c
sleep_until_event();
```

### Regression tests

```c
assert_wait_enters_low_power();
```

## EC-E-010: unchecked peripheral result

- Difficulty: Easy
- Language/platform: Embedded C
- Perspective: Safety
- Concept: unchecked peripheral result
- Symptom: A bus fault becomes invalid state.
- Diagnostic goal: Check every hardware operation before using output.

### Buggy code

```c
read_i2c(buf);
use(buf);
```

### Expected diagnosis

The buffer may be stale or incomplete after a failed transfer.

### Corrected code

```c
if (read_i2c(buf) != OK) return ERR_BUS;
use(buf);
```

### Regression tests

```c
assert_bus_error_is_propagated();
```

## EC-E-011: work in ISR

- Difficulty: Easy
- Language/platform: Embedded C
- Perspective: Interrupts
- Concept: work in ISR
- Symptom: The device misses deadlines or deadlocks.
- Diagnostic goal: Keep handlers short and defer work.

### Buggy code

```c
void ISR(void) { printf("edge"); read_sensor(); }
```

### Expected diagnosis

I/O, allocation, and slow calls inside an ISR are unsafe and unbounded.

### Corrected code

```c
volatile bool pending; void ISR(void) { pending = true; }
```

### Regression tests

```c
assert_main_loop_services_pending();
```

## EC-E-012: blocking delay

- Difficulty: Easy
- Language/platform: Embedded C
- Perspective: Timing
- Concept: blocking delay
- Symptom: A periodic task drifts.
- Diagnostic goal: Schedule against a monotonic deadline.

### Buggy code

```c
delay_ms(period); task();
```

### Expected diagnosis

Sleeping before work accumulates execution time as drift.

### Corrected code

```c
if (now >= deadline) { task(); deadline += period; }
```

### Regression tests

```c
assert_periodic_deadline_does_not_drift();
```

## EC-E-013: missing volatile

- Difficulty: Easy
- Language/platform: Embedded C
- Perspective: Volatile
- Concept: missing volatile
- Symptom: The main loop never sees a flag change.
- Diagnostic goal: Mark memory changed by hardware or ISR as volatile.

### Buggy code

```c
bool ready = false;
while (!ready) {}
```

### Expected diagnosis

The optimizer may cache a nonvolatile flag in a register.

### Corrected code

```c
volatile bool ready = false;
while (!ready) {}
```

### Regression tests

```c
assert_flag_change_is_observed();
```

## EC-E-014: off-by-one ring buffer

- Difficulty: Easy
- Language/platform: Embedded C
- Perspective: Buffers
- Concept: off-by-one ring buffer
- Symptom: Full and empty states are confused.
- Diagnostic goal: Track count or reserve one slot.

### Buggy code

```c
buffer[head++] = value;
```

### Expected diagnosis

The head wraps without checking capacity and overwrites unread data.

### Corrected code

```c
if (count < CAPACITY) { buffer[head] = value; head = (head + 1) % CAPACITY; count++; }
```

### Regression tests

```c
assert_full_buffer_rejects_new_value();
```

## EC-E-015: heap fragmentation

- Difficulty: Easy
- Language/platform: Embedded C
- Perspective: Memory
- Concept: heap fragmentation
- Symptom: Long uptime causes allocation failure.
- Diagnostic goal: Use fixed storage for bounded messages.

### Buggy code

```c
uint8_t *packet = malloc(length);
```

### Expected diagnosis

Repeated variable allocations fragment a small heap.

### Corrected code

```c
uint8_t packet[MAX_PACKET]; if (length > sizeof packet) return ERR_TOO_LARGE;
```

### Regression tests

```c
assert_oversized_packet_rejected();
```

## EC-E-016: raw units mistaken for volts

- Difficulty: Easy
- Language/platform: Embedded C
- Perspective: ADC
- Concept: raw units mistaken for volts
- Symptom: Control thresholds trigger at the wrong level.
- Diagnostic goal: Calibrate raw codes at the hardware boundary.

### Buggy code

```c
float volts = raw;
```

### Expected diagnosis

An ADC code needs reference voltage and resolution conversion.

### Corrected code

```c
float volts = raw * reference / ((1u << bits) - 1u);
```

### Regression tests

```c
assert_full_scale_equals_reference();
```

## EC-E-017: partial frame

- Difficulty: Easy
- Language/platform: Embedded C
- Perspective: UART
- Concept: partial frame
- Symptom: A split message is parsed as corrupt.
- Diagnostic goal: Accumulate until a complete delimiter/frame exists.

### Buggy code

```c
if (byte == ">") parse(frame);
```

### Expected diagnosis

A terminator may arrive in a later interrupt and a partial frame is discarded.

### Corrected code

```c
if (append(byte)) { if (byte == ">") parse(frame); }
```

### Regression tests

```c
assert_split_frame_reassembles();
```

## EC-E-018: feed before work

- Difficulty: Easy
- Language/platform: Embedded C
- Perspective: Watchdog
- Concept: feed before work
- Symptom: A stuck task keeps the watchdog alive.
- Diagnostic goal: Feed only after essential work succeeds.

### Buggy code

```c
watchdog_feed();
run_control_loop();
```

### Expected diagnosis

The watchdog proves loop entry, not successful progress.

### Corrected code

```c
run_control_loop(); watchdog_feed();
```

### Regression tests

```c
assert_failed_work_does_not_feed();
```

## EC-E-019: busy wait

- Difficulty: Easy
- Language/platform: Embedded C
- Perspective: Power
- Concept: busy wait
- Symptom: Sleep current is too high.
- Diagnostic goal: Use a timer or wake event rather than polling.

### Buggy code

```c
while (!event) { }
```

### Expected diagnosis

The CPU remains active while waiting for hardware.

### Corrected code

```c
sleep_until_event();
```

### Regression tests

```c
assert_wait_enters_low_power();
```

## EC-E-020: unchecked peripheral result

- Difficulty: Easy
- Language/platform: Embedded C
- Perspective: Safety
- Concept: unchecked peripheral result
- Symptom: A bus fault becomes invalid state.
- Diagnostic goal: Check every hardware operation before using output.

### Buggy code

```c
read_i2c(buf);
use(buf);
```

### Expected diagnosis

The buffer may be stale or incomplete after a failed transfer.

### Corrected code

```c
if (read_i2c(buf) != OK) return ERR_BUS;
use(buf);
```

### Regression tests

```c
assert_bus_error_is_propagated();
```

## EC-E-021: work in ISR

- Difficulty: Easy
- Language/platform: Embedded C
- Perspective: Interrupts
- Concept: work in ISR
- Symptom: The device misses deadlines or deadlocks.
- Diagnostic goal: Keep handlers short and defer work.

### Buggy code

```c
void ISR(void) { printf("edge"); read_sensor(); }
```

### Expected diagnosis

I/O, allocation, and slow calls inside an ISR are unsafe and unbounded.

### Corrected code

```c
volatile bool pending; void ISR(void) { pending = true; }
```

### Regression tests

```c
assert_main_loop_services_pending();
```

## EC-E-022: blocking delay

- Difficulty: Easy
- Language/platform: Embedded C
- Perspective: Timing
- Concept: blocking delay
- Symptom: A periodic task drifts.
- Diagnostic goal: Schedule against a monotonic deadline.

### Buggy code

```c
delay_ms(period); task();
```

### Expected diagnosis

Sleeping before work accumulates execution time as drift.

### Corrected code

```c
if (now >= deadline) { task(); deadline += period; }
```

### Regression tests

```c
assert_periodic_deadline_does_not_drift();
```

## EC-E-023: missing volatile

- Difficulty: Easy
- Language/platform: Embedded C
- Perspective: Volatile
- Concept: missing volatile
- Symptom: The main loop never sees a flag change.
- Diagnostic goal: Mark memory changed by hardware or ISR as volatile.

### Buggy code

```c
bool ready = false;
while (!ready) {}
```

### Expected diagnosis

The optimizer may cache a nonvolatile flag in a register.

### Corrected code

```c
volatile bool ready = false;
while (!ready) {}
```

### Regression tests

```c
assert_flag_change_is_observed();
```

## EC-E-024: off-by-one ring buffer

- Difficulty: Easy
- Language/platform: Embedded C
- Perspective: Buffers
- Concept: off-by-one ring buffer
- Symptom: Full and empty states are confused.
- Diagnostic goal: Track count or reserve one slot.

### Buggy code

```c
buffer[head++] = value;
```

### Expected diagnosis

The head wraps without checking capacity and overwrites unread data.

### Corrected code

```c
if (count < CAPACITY) { buffer[head] = value; head = (head + 1) % CAPACITY; count++; }
```

### Regression tests

```c
assert_full_buffer_rejects_new_value();
```

## EC-E-025: heap fragmentation

- Difficulty: Easy
- Language/platform: Embedded C
- Perspective: Memory
- Concept: heap fragmentation
- Symptom: Long uptime causes allocation failure.
- Diagnostic goal: Use fixed storage for bounded messages.

### Buggy code

```c
uint8_t *packet = malloc(length);
```

### Expected diagnosis

Repeated variable allocations fragment a small heap.

### Corrected code

```c
uint8_t packet[MAX_PACKET]; if (length > sizeof packet) return ERR_TOO_LARGE;
```

### Regression tests

```c
assert_oversized_packet_rejected();
```

## EC-E-026: raw units mistaken for volts

- Difficulty: Easy
- Language/platform: Embedded C
- Perspective: ADC
- Concept: raw units mistaken for volts
- Symptom: Control thresholds trigger at the wrong level.
- Diagnostic goal: Calibrate raw codes at the hardware boundary.

### Buggy code

```c
float volts = raw;
```

### Expected diagnosis

An ADC code needs reference voltage and resolution conversion.

### Corrected code

```c
float volts = raw * reference / ((1u << bits) - 1u);
```

### Regression tests

```c
assert_full_scale_equals_reference();
```

## EC-E-027: partial frame

- Difficulty: Easy
- Language/platform: Embedded C
- Perspective: UART
- Concept: partial frame
- Symptom: A split message is parsed as corrupt.
- Diagnostic goal: Accumulate until a complete delimiter/frame exists.

### Buggy code

```c
if (byte == ">") parse(frame);
```

### Expected diagnosis

A terminator may arrive in a later interrupt and a partial frame is discarded.

### Corrected code

```c
if (append(byte)) { if (byte == ">") parse(frame); }
```

### Regression tests

```c
assert_split_frame_reassembles();
```

## EC-E-028: feed before work

- Difficulty: Easy
- Language/platform: Embedded C
- Perspective: Watchdog
- Concept: feed before work
- Symptom: A stuck task keeps the watchdog alive.
- Diagnostic goal: Feed only after essential work succeeds.

### Buggy code

```c
watchdog_feed();
run_control_loop();
```

### Expected diagnosis

The watchdog proves loop entry, not successful progress.

### Corrected code

```c
run_control_loop(); watchdog_feed();
```

### Regression tests

```c
assert_failed_work_does_not_feed();
```

## EC-E-029: busy wait

- Difficulty: Easy
- Language/platform: Embedded C
- Perspective: Power
- Concept: busy wait
- Symptom: Sleep current is too high.
- Diagnostic goal: Use a timer or wake event rather than polling.

### Buggy code

```c
while (!event) { }
```

### Expected diagnosis

The CPU remains active while waiting for hardware.

### Corrected code

```c
sleep_until_event();
```

### Regression tests

```c
assert_wait_enters_low_power();
```

## EC-E-030: unchecked peripheral result

- Difficulty: Easy
- Language/platform: Embedded C
- Perspective: Safety
- Concept: unchecked peripheral result
- Symptom: A bus fault becomes invalid state.
- Diagnostic goal: Check every hardware operation before using output.

### Buggy code

```c
read_i2c(buf);
use(buf);
```

### Expected diagnosis

The buffer may be stale or incomplete after a failed transfer.

### Corrected code

```c
if (read_i2c(buf) != OK) return ERR_BUS;
use(buf);
```

### Regression tests

```c
assert_bus_error_is_propagated();
```

## EC-E-031: work in ISR

- Difficulty: Easy
- Language/platform: Embedded C
- Perspective: Interrupts
- Concept: work in ISR
- Symptom: The device misses deadlines or deadlocks.
- Diagnostic goal: Keep handlers short and defer work.

### Buggy code

```c
void ISR(void) { printf("edge"); read_sensor(); }
```

### Expected diagnosis

I/O, allocation, and slow calls inside an ISR are unsafe and unbounded.

### Corrected code

```c
volatile bool pending; void ISR(void) { pending = true; }
```

### Regression tests

```c
assert_main_loop_services_pending();
```

## EC-E-032: blocking delay

- Difficulty: Easy
- Language/platform: Embedded C
- Perspective: Timing
- Concept: blocking delay
- Symptom: A periodic task drifts.
- Diagnostic goal: Schedule against a monotonic deadline.

### Buggy code

```c
delay_ms(period); task();
```

### Expected diagnosis

Sleeping before work accumulates execution time as drift.

### Corrected code

```c
if (now >= deadline) { task(); deadline += period; }
```

### Regression tests

```c
assert_periodic_deadline_does_not_drift();
```

## EC-E-033: missing volatile

- Difficulty: Easy
- Language/platform: Embedded C
- Perspective: Volatile
- Concept: missing volatile
- Symptom: The main loop never sees a flag change.
- Diagnostic goal: Mark memory changed by hardware or ISR as volatile.

### Buggy code

```c
bool ready = false;
while (!ready) {}
```

### Expected diagnosis

The optimizer may cache a nonvolatile flag in a register.

### Corrected code

```c
volatile bool ready = false;
while (!ready) {}
```

### Regression tests

```c
assert_flag_change_is_observed();
```

## EC-E-034: off-by-one ring buffer

- Difficulty: Easy
- Language/platform: Embedded C
- Perspective: Buffers
- Concept: off-by-one ring buffer
- Symptom: Full and empty states are confused.
- Diagnostic goal: Track count or reserve one slot.

### Buggy code

```c
buffer[head++] = value;
```

### Expected diagnosis

The head wraps without checking capacity and overwrites unread data.

### Corrected code

```c
if (count < CAPACITY) { buffer[head] = value; head = (head + 1) % CAPACITY; count++; }
```

### Regression tests

```c
assert_full_buffer_rejects_new_value();
```

## EC-E-035: heap fragmentation

- Difficulty: Easy
- Language/platform: Embedded C
- Perspective: Memory
- Concept: heap fragmentation
- Symptom: Long uptime causes allocation failure.
- Diagnostic goal: Use fixed storage for bounded messages.

### Buggy code

```c
uint8_t *packet = malloc(length);
```

### Expected diagnosis

Repeated variable allocations fragment a small heap.

### Corrected code

```c
uint8_t packet[MAX_PACKET]; if (length > sizeof packet) return ERR_TOO_LARGE;
```

### Regression tests

```c
assert_oversized_packet_rejected();
```

## EC-E-036: raw units mistaken for volts

- Difficulty: Easy
- Language/platform: Embedded C
- Perspective: ADC
- Concept: raw units mistaken for volts
- Symptom: Control thresholds trigger at the wrong level.
- Diagnostic goal: Calibrate raw codes at the hardware boundary.

### Buggy code

```c
float volts = raw;
```

### Expected diagnosis

An ADC code needs reference voltage and resolution conversion.

### Corrected code

```c
float volts = raw * reference / ((1u << bits) - 1u);
```

### Regression tests

```c
assert_full_scale_equals_reference();
```

## EC-E-037: partial frame

- Difficulty: Easy
- Language/platform: Embedded C
- Perspective: UART
- Concept: partial frame
- Symptom: A split message is parsed as corrupt.
- Diagnostic goal: Accumulate until a complete delimiter/frame exists.

### Buggy code

```c
if (byte == ">") parse(frame);
```

### Expected diagnosis

A terminator may arrive in a later interrupt and a partial frame is discarded.

### Corrected code

```c
if (append(byte)) { if (byte == ">") parse(frame); }
```

### Regression tests

```c
assert_split_frame_reassembles();
```

## EC-E-038: feed before work

- Difficulty: Easy
- Language/platform: Embedded C
- Perspective: Watchdog
- Concept: feed before work
- Symptom: A stuck task keeps the watchdog alive.
- Diagnostic goal: Feed only after essential work succeeds.

### Buggy code

```c
watchdog_feed();
run_control_loop();
```

### Expected diagnosis

The watchdog proves loop entry, not successful progress.

### Corrected code

```c
run_control_loop(); watchdog_feed();
```

### Regression tests

```c
assert_failed_work_does_not_feed();
```

## EC-E-039: busy wait

- Difficulty: Easy
- Language/platform: Embedded C
- Perspective: Power
- Concept: busy wait
- Symptom: Sleep current is too high.
- Diagnostic goal: Use a timer or wake event rather than polling.

### Buggy code

```c
while (!event) { }
```

### Expected diagnosis

The CPU remains active while waiting for hardware.

### Corrected code

```c
sleep_until_event();
```

### Regression tests

```c
assert_wait_enters_low_power();
```

## EC-E-040: unchecked peripheral result

- Difficulty: Easy
- Language/platform: Embedded C
- Perspective: Safety
- Concept: unchecked peripheral result
- Symptom: A bus fault becomes invalid state.
- Diagnostic goal: Check every hardware operation before using output.

### Buggy code

```c
read_i2c(buf);
use(buf);
```

### Expected diagnosis

The buffer may be stale or incomplete after a failed transfer.

### Corrected code

```c
if (read_i2c(buf) != OK) return ERR_BUS;
use(buf);
```

### Regression tests

```c
assert_bus_error_is_propagated();
```

## EC-E-041: work in ISR

- Difficulty: Easy
- Language/platform: Embedded C
- Perspective: Interrupts
- Concept: work in ISR
- Symptom: The device misses deadlines or deadlocks.
- Diagnostic goal: Keep handlers short and defer work.

### Buggy code

```c
void ISR(void) { printf("edge"); read_sensor(); }
```

### Expected diagnosis

I/O, allocation, and slow calls inside an ISR are unsafe and unbounded.

### Corrected code

```c
volatile bool pending; void ISR(void) { pending = true; }
```

### Regression tests

```c
assert_main_loop_services_pending();
```

## EC-E-042: blocking delay

- Difficulty: Easy
- Language/platform: Embedded C
- Perspective: Timing
- Concept: blocking delay
- Symptom: A periodic task drifts.
- Diagnostic goal: Schedule against a monotonic deadline.

### Buggy code

```c
delay_ms(period); task();
```

### Expected diagnosis

Sleeping before work accumulates execution time as drift.

### Corrected code

```c
if (now >= deadline) { task(); deadline += period; }
```

### Regression tests

```c
assert_periodic_deadline_does_not_drift();
```

## EC-E-043: missing volatile

- Difficulty: Easy
- Language/platform: Embedded C
- Perspective: Volatile
- Concept: missing volatile
- Symptom: The main loop never sees a flag change.
- Diagnostic goal: Mark memory changed by hardware or ISR as volatile.

### Buggy code

```c
bool ready = false;
while (!ready) {}
```

### Expected diagnosis

The optimizer may cache a nonvolatile flag in a register.

### Corrected code

```c
volatile bool ready = false;
while (!ready) {}
```

### Regression tests

```c
assert_flag_change_is_observed();
```

## EC-E-044: off-by-one ring buffer

- Difficulty: Easy
- Language/platform: Embedded C
- Perspective: Buffers
- Concept: off-by-one ring buffer
- Symptom: Full and empty states are confused.
- Diagnostic goal: Track count or reserve one slot.

### Buggy code

```c
buffer[head++] = value;
```

### Expected diagnosis

The head wraps without checking capacity and overwrites unread data.

### Corrected code

```c
if (count < CAPACITY) { buffer[head] = value; head = (head + 1) % CAPACITY; count++; }
```

### Regression tests

```c
assert_full_buffer_rejects_new_value();
```

## EC-E-045: heap fragmentation

- Difficulty: Easy
- Language/platform: Embedded C
- Perspective: Memory
- Concept: heap fragmentation
- Symptom: Long uptime causes allocation failure.
- Diagnostic goal: Use fixed storage for bounded messages.

### Buggy code

```c
uint8_t *packet = malloc(length);
```

### Expected diagnosis

Repeated variable allocations fragment a small heap.

### Corrected code

```c
uint8_t packet[MAX_PACKET]; if (length > sizeof packet) return ERR_TOO_LARGE;
```

### Regression tests

```c
assert_oversized_packet_rejected();
```

## EC-E-046: raw units mistaken for volts

- Difficulty: Easy
- Language/platform: Embedded C
- Perspective: ADC
- Concept: raw units mistaken for volts
- Symptom: Control thresholds trigger at the wrong level.
- Diagnostic goal: Calibrate raw codes at the hardware boundary.

### Buggy code

```c
float volts = raw;
```

### Expected diagnosis

An ADC code needs reference voltage and resolution conversion.

### Corrected code

```c
float volts = raw * reference / ((1u << bits) - 1u);
```

### Regression tests

```c
assert_full_scale_equals_reference();
```

## EC-E-047: partial frame

- Difficulty: Easy
- Language/platform: Embedded C
- Perspective: UART
- Concept: partial frame
- Symptom: A split message is parsed as corrupt.
- Diagnostic goal: Accumulate until a complete delimiter/frame exists.

### Buggy code

```c
if (byte == ">") parse(frame);
```

### Expected diagnosis

A terminator may arrive in a later interrupt and a partial frame is discarded.

### Corrected code

```c
if (append(byte)) { if (byte == ">") parse(frame); }
```

### Regression tests

```c
assert_split_frame_reassembles();
```

## EC-E-048: feed before work

- Difficulty: Easy
- Language/platform: Embedded C
- Perspective: Watchdog
- Concept: feed before work
- Symptom: A stuck task keeps the watchdog alive.
- Diagnostic goal: Feed only after essential work succeeds.

### Buggy code

```c
watchdog_feed();
run_control_loop();
```

### Expected diagnosis

The watchdog proves loop entry, not successful progress.

### Corrected code

```c
run_control_loop(); watchdog_feed();
```

### Regression tests

```c
assert_failed_work_does_not_feed();
```

## EC-E-049: busy wait

- Difficulty: Easy
- Language/platform: Embedded C
- Perspective: Power
- Concept: busy wait
- Symptom: Sleep current is too high.
- Diagnostic goal: Use a timer or wake event rather than polling.

### Buggy code

```c
while (!event) { }
```

### Expected diagnosis

The CPU remains active while waiting for hardware.

### Corrected code

```c
sleep_until_event();
```

### Regression tests

```c
assert_wait_enters_low_power();
```

## EC-E-050: unchecked peripheral result

- Difficulty: Easy
- Language/platform: Embedded C
- Perspective: Safety
- Concept: unchecked peripheral result
- Symptom: A bus fault becomes invalid state.
- Diagnostic goal: Check every hardware operation before using output.

### Buggy code

```c
read_i2c(buf);
use(buf);
```

### Expected diagnosis

The buffer may be stale or incomplete after a failed transfer.

### Corrected code

```c
if (read_i2c(buf) != OK) return ERR_BUS;
use(buf);
```

### Regression tests

```c
assert_bus_error_is_propagated();
```

## EC-E-051: work in ISR

- Difficulty: Easy
- Language/platform: Embedded C
- Perspective: Interrupts
- Concept: work in ISR
- Symptom: The device misses deadlines or deadlocks.
- Diagnostic goal: Keep handlers short and defer work.

### Buggy code

```c
void ISR(void) { printf("edge"); read_sensor(); }
```

### Expected diagnosis

I/O, allocation, and slow calls inside an ISR are unsafe and unbounded.

### Corrected code

```c
volatile bool pending; void ISR(void) { pending = true; }
```

### Regression tests

```c
assert_main_loop_services_pending();
```

## EC-E-052: blocking delay

- Difficulty: Easy
- Language/platform: Embedded C
- Perspective: Timing
- Concept: blocking delay
- Symptom: A periodic task drifts.
- Diagnostic goal: Schedule against a monotonic deadline.

### Buggy code

```c
delay_ms(period); task();
```

### Expected diagnosis

Sleeping before work accumulates execution time as drift.

### Corrected code

```c
if (now >= deadline) { task(); deadline += period; }
```

### Regression tests

```c
assert_periodic_deadline_does_not_drift();
```

## EC-E-053: missing volatile

- Difficulty: Easy
- Language/platform: Embedded C
- Perspective: Volatile
- Concept: missing volatile
- Symptom: The main loop never sees a flag change.
- Diagnostic goal: Mark memory changed by hardware or ISR as volatile.

### Buggy code

```c
bool ready = false;
while (!ready) {}
```

### Expected diagnosis

The optimizer may cache a nonvolatile flag in a register.

### Corrected code

```c
volatile bool ready = false;
while (!ready) {}
```

### Regression tests

```c
assert_flag_change_is_observed();
```

## EC-E-054: off-by-one ring buffer

- Difficulty: Easy
- Language/platform: Embedded C
- Perspective: Buffers
- Concept: off-by-one ring buffer
- Symptom: Full and empty states are confused.
- Diagnostic goal: Track count or reserve one slot.

### Buggy code

```c
buffer[head++] = value;
```

### Expected diagnosis

The head wraps without checking capacity and overwrites unread data.

### Corrected code

```c
if (count < CAPACITY) { buffer[head] = value; head = (head + 1) % CAPACITY; count++; }
```

### Regression tests

```c
assert_full_buffer_rejects_new_value();
```

## EC-E-055: heap fragmentation

- Difficulty: Easy
- Language/platform: Embedded C
- Perspective: Memory
- Concept: heap fragmentation
- Symptom: Long uptime causes allocation failure.
- Diagnostic goal: Use fixed storage for bounded messages.

### Buggy code

```c
uint8_t *packet = malloc(length);
```

### Expected diagnosis

Repeated variable allocations fragment a small heap.

### Corrected code

```c
uint8_t packet[MAX_PACKET]; if (length > sizeof packet) return ERR_TOO_LARGE;
```

### Regression tests

```c
assert_oversized_packet_rejected();
```

## EC-E-056: raw units mistaken for volts

- Difficulty: Easy
- Language/platform: Embedded C
- Perspective: ADC
- Concept: raw units mistaken for volts
- Symptom: Control thresholds trigger at the wrong level.
- Diagnostic goal: Calibrate raw codes at the hardware boundary.

### Buggy code

```c
float volts = raw;
```

### Expected diagnosis

An ADC code needs reference voltage and resolution conversion.

### Corrected code

```c
float volts = raw * reference / ((1u << bits) - 1u);
```

### Regression tests

```c
assert_full_scale_equals_reference();
```

## EC-E-057: partial frame

- Difficulty: Easy
- Language/platform: Embedded C
- Perspective: UART
- Concept: partial frame
- Symptom: A split message is parsed as corrupt.
- Diagnostic goal: Accumulate until a complete delimiter/frame exists.

### Buggy code

```c
if (byte == ">") parse(frame);
```

### Expected diagnosis

A terminator may arrive in a later interrupt and a partial frame is discarded.

### Corrected code

```c
if (append(byte)) { if (byte == ">") parse(frame); }
```

### Regression tests

```c
assert_split_frame_reassembles();
```

## EC-E-058: feed before work

- Difficulty: Easy
- Language/platform: Embedded C
- Perspective: Watchdog
- Concept: feed before work
- Symptom: A stuck task keeps the watchdog alive.
- Diagnostic goal: Feed only after essential work succeeds.

### Buggy code

```c
watchdog_feed();
run_control_loop();
```

### Expected diagnosis

The watchdog proves loop entry, not successful progress.

### Corrected code

```c
run_control_loop(); watchdog_feed();
```

### Regression tests

```c
assert_failed_work_does_not_feed();
```

## EC-E-059: busy wait

- Difficulty: Easy
- Language/platform: Embedded C
- Perspective: Power
- Concept: busy wait
- Symptom: Sleep current is too high.
- Diagnostic goal: Use a timer or wake event rather than polling.

### Buggy code

```c
while (!event) { }
```

### Expected diagnosis

The CPU remains active while waiting for hardware.

### Corrected code

```c
sleep_until_event();
```

### Regression tests

```c
assert_wait_enters_low_power();
```

## EC-E-060: unchecked peripheral result

- Difficulty: Easy
- Language/platform: Embedded C
- Perspective: Safety
- Concept: unchecked peripheral result
- Symptom: A bus fault becomes invalid state.
- Diagnostic goal: Check every hardware operation before using output.

### Buggy code

```c
read_i2c(buf);
use(buf);
```

### Expected diagnosis

The buffer may be stale or incomplete after a failed transfer.

### Corrected code

```c
if (read_i2c(buf) != OK) return ERR_BUS;
use(buf);
```

### Regression tests

```c
assert_bus_error_is_propagated();
```

## EC-E-061: work in ISR

- Difficulty: Easy
- Language/platform: Embedded C
- Perspective: Interrupts
- Concept: work in ISR
- Symptom: The device misses deadlines or deadlocks.
- Diagnostic goal: Keep handlers short and defer work.

### Buggy code

```c
void ISR(void) { printf("edge"); read_sensor(); }
```

### Expected diagnosis

I/O, allocation, and slow calls inside an ISR are unsafe and unbounded.

### Corrected code

```c
volatile bool pending; void ISR(void) { pending = true; }
```

### Regression tests

```c
assert_main_loop_services_pending();
```

## EC-E-062: blocking delay

- Difficulty: Easy
- Language/platform: Embedded C
- Perspective: Timing
- Concept: blocking delay
- Symptom: A periodic task drifts.
- Diagnostic goal: Schedule against a monotonic deadline.

### Buggy code

```c
delay_ms(period); task();
```

### Expected diagnosis

Sleeping before work accumulates execution time as drift.

### Corrected code

```c
if (now >= deadline) { task(); deadline += period; }
```

### Regression tests

```c
assert_periodic_deadline_does_not_drift();
```

## EC-E-063: missing volatile

- Difficulty: Easy
- Language/platform: Embedded C
- Perspective: Volatile
- Concept: missing volatile
- Symptom: The main loop never sees a flag change.
- Diagnostic goal: Mark memory changed by hardware or ISR as volatile.

### Buggy code

```c
bool ready = false;
while (!ready) {}
```

### Expected diagnosis

The optimizer may cache a nonvolatile flag in a register.

### Corrected code

```c
volatile bool ready = false;
while (!ready) {}
```

### Regression tests

```c
assert_flag_change_is_observed();
```

## EC-E-064: off-by-one ring buffer

- Difficulty: Easy
- Language/platform: Embedded C
- Perspective: Buffers
- Concept: off-by-one ring buffer
- Symptom: Full and empty states are confused.
- Diagnostic goal: Track count or reserve one slot.

### Buggy code

```c
buffer[head++] = value;
```

### Expected diagnosis

The head wraps without checking capacity and overwrites unread data.

### Corrected code

```c
if (count < CAPACITY) { buffer[head] = value; head = (head + 1) % CAPACITY; count++; }
```

### Regression tests

```c
assert_full_buffer_rejects_new_value();
```

## EC-E-065: heap fragmentation

- Difficulty: Easy
- Language/platform: Embedded C
- Perspective: Memory
- Concept: heap fragmentation
- Symptom: Long uptime causes allocation failure.
- Diagnostic goal: Use fixed storage for bounded messages.

### Buggy code

```c
uint8_t *packet = malloc(length);
```

### Expected diagnosis

Repeated variable allocations fragment a small heap.

### Corrected code

```c
uint8_t packet[MAX_PACKET]; if (length > sizeof packet) return ERR_TOO_LARGE;
```

### Regression tests

```c
assert_oversized_packet_rejected();
```

## EC-E-066: raw units mistaken for volts

- Difficulty: Easy
- Language/platform: Embedded C
- Perspective: ADC
- Concept: raw units mistaken for volts
- Symptom: Control thresholds trigger at the wrong level.
- Diagnostic goal: Calibrate raw codes at the hardware boundary.

### Buggy code

```c
float volts = raw;
```

### Expected diagnosis

An ADC code needs reference voltage and resolution conversion.

### Corrected code

```c
float volts = raw * reference / ((1u << bits) - 1u);
```

### Regression tests

```c
assert_full_scale_equals_reference();
```

## EC-E-067: partial frame

- Difficulty: Easy
- Language/platform: Embedded C
- Perspective: UART
- Concept: partial frame
- Symptom: A split message is parsed as corrupt.
- Diagnostic goal: Accumulate until a complete delimiter/frame exists.

### Buggy code

```c
if (byte == ">") parse(frame);
```

### Expected diagnosis

A terminator may arrive in a later interrupt and a partial frame is discarded.

### Corrected code

```c
if (append(byte)) { if (byte == ">") parse(frame); }
```

### Regression tests

```c
assert_split_frame_reassembles();
```

## EC-E-068: feed before work

- Difficulty: Easy
- Language/platform: Embedded C
- Perspective: Watchdog
- Concept: feed before work
- Symptom: A stuck task keeps the watchdog alive.
- Diagnostic goal: Feed only after essential work succeeds.

### Buggy code

```c
watchdog_feed();
run_control_loop();
```

### Expected diagnosis

The watchdog proves loop entry, not successful progress.

### Corrected code

```c
run_control_loop(); watchdog_feed();
```

### Regression tests

```c
assert_failed_work_does_not_feed();
```

## EC-E-069: busy wait

- Difficulty: Easy
- Language/platform: Embedded C
- Perspective: Power
- Concept: busy wait
- Symptom: Sleep current is too high.
- Diagnostic goal: Use a timer or wake event rather than polling.

### Buggy code

```c
while (!event) { }
```

### Expected diagnosis

The CPU remains active while waiting for hardware.

### Corrected code

```c
sleep_until_event();
```

### Regression tests

```c
assert_wait_enters_low_power();
```

## EC-E-070: unchecked peripheral result

- Difficulty: Easy
- Language/platform: Embedded C
- Perspective: Safety
- Concept: unchecked peripheral result
- Symptom: A bus fault becomes invalid state.
- Diagnostic goal: Check every hardware operation before using output.

### Buggy code

```c
read_i2c(buf);
use(buf);
```

### Expected diagnosis

The buffer may be stale or incomplete after a failed transfer.

### Corrected code

```c
if (read_i2c(buf) != OK) return ERR_BUS;
use(buf);
```

### Regression tests

```c
assert_bus_error_is_propagated();
```

## EC-E-071: work in ISR

- Difficulty: Easy
- Language/platform: Embedded C
- Perspective: Interrupts
- Concept: work in ISR
- Symptom: The device misses deadlines or deadlocks.
- Diagnostic goal: Keep handlers short and defer work.

### Buggy code

```c
void ISR(void) { printf("edge"); read_sensor(); }
```

### Expected diagnosis

I/O, allocation, and slow calls inside an ISR are unsafe and unbounded.

### Corrected code

```c
volatile bool pending; void ISR(void) { pending = true; }
```

### Regression tests

```c
assert_main_loop_services_pending();
```

## EC-E-072: blocking delay

- Difficulty: Easy
- Language/platform: Embedded C
- Perspective: Timing
- Concept: blocking delay
- Symptom: A periodic task drifts.
- Diagnostic goal: Schedule against a monotonic deadline.

### Buggy code

```c
delay_ms(period); task();
```

### Expected diagnosis

Sleeping before work accumulates execution time as drift.

### Corrected code

```c
if (now >= deadline) { task(); deadline += period; }
```

### Regression tests

```c
assert_periodic_deadline_does_not_drift();
```

## EC-E-073: missing volatile

- Difficulty: Easy
- Language/platform: Embedded C
- Perspective: Volatile
- Concept: missing volatile
- Symptom: The main loop never sees a flag change.
- Diagnostic goal: Mark memory changed by hardware or ISR as volatile.

### Buggy code

```c
bool ready = false;
while (!ready) {}
```

### Expected diagnosis

The optimizer may cache a nonvolatile flag in a register.

### Corrected code

```c
volatile bool ready = false;
while (!ready) {}
```

### Regression tests

```c
assert_flag_change_is_observed();
```

## EC-E-074: off-by-one ring buffer

- Difficulty: Easy
- Language/platform: Embedded C
- Perspective: Buffers
- Concept: off-by-one ring buffer
- Symptom: Full and empty states are confused.
- Diagnostic goal: Track count or reserve one slot.

### Buggy code

```c
buffer[head++] = value;
```

### Expected diagnosis

The head wraps without checking capacity and overwrites unread data.

### Corrected code

```c
if (count < CAPACITY) { buffer[head] = value; head = (head + 1) % CAPACITY; count++; }
```

### Regression tests

```c
assert_full_buffer_rejects_new_value();
```

## EC-E-075: heap fragmentation

- Difficulty: Easy
- Language/platform: Embedded C
- Perspective: Memory
- Concept: heap fragmentation
- Symptom: Long uptime causes allocation failure.
- Diagnostic goal: Use fixed storage for bounded messages.

### Buggy code

```c
uint8_t *packet = malloc(length);
```

### Expected diagnosis

Repeated variable allocations fragment a small heap.

### Corrected code

```c
uint8_t packet[MAX_PACKET]; if (length > sizeof packet) return ERR_TOO_LARGE;
```

### Regression tests

```c
assert_oversized_packet_rejected();
```

## EC-E-076: raw units mistaken for volts

- Difficulty: Easy
- Language/platform: Embedded C
- Perspective: ADC
- Concept: raw units mistaken for volts
- Symptom: Control thresholds trigger at the wrong level.
- Diagnostic goal: Calibrate raw codes at the hardware boundary.

### Buggy code

```c
float volts = raw;
```

### Expected diagnosis

An ADC code needs reference voltage and resolution conversion.

### Corrected code

```c
float volts = raw * reference / ((1u << bits) - 1u);
```

### Regression tests

```c
assert_full_scale_equals_reference();
```

## EC-E-077: partial frame

- Difficulty: Easy
- Language/platform: Embedded C
- Perspective: UART
- Concept: partial frame
- Symptom: A split message is parsed as corrupt.
- Diagnostic goal: Accumulate until a complete delimiter/frame exists.

### Buggy code

```c
if (byte == ">") parse(frame);
```

### Expected diagnosis

A terminator may arrive in a later interrupt and a partial frame is discarded.

### Corrected code

```c
if (append(byte)) { if (byte == ">") parse(frame); }
```

### Regression tests

```c
assert_split_frame_reassembles();
```

## EC-E-078: feed before work

- Difficulty: Easy
- Language/platform: Embedded C
- Perspective: Watchdog
- Concept: feed before work
- Symptom: A stuck task keeps the watchdog alive.
- Diagnostic goal: Feed only after essential work succeeds.

### Buggy code

```c
watchdog_feed();
run_control_loop();
```

### Expected diagnosis

The watchdog proves loop entry, not successful progress.

### Corrected code

```c
run_control_loop(); watchdog_feed();
```

### Regression tests

```c
assert_failed_work_does_not_feed();
```

## EC-E-079: busy wait

- Difficulty: Easy
- Language/platform: Embedded C
- Perspective: Power
- Concept: busy wait
- Symptom: Sleep current is too high.
- Diagnostic goal: Use a timer or wake event rather than polling.

### Buggy code

```c
while (!event) { }
```

### Expected diagnosis

The CPU remains active while waiting for hardware.

### Corrected code

```c
sleep_until_event();
```

### Regression tests

```c
assert_wait_enters_low_power();
```

## EC-E-080: unchecked peripheral result

- Difficulty: Easy
- Language/platform: Embedded C
- Perspective: Safety
- Concept: unchecked peripheral result
- Symptom: A bus fault becomes invalid state.
- Diagnostic goal: Check every hardware operation before using output.

### Buggy code

```c
read_i2c(buf);
use(buf);
```

### Expected diagnosis

The buffer may be stale or incomplete after a failed transfer.

### Corrected code

```c
if (read_i2c(buf) != OK) return ERR_BUS;
use(buf);
```

### Regression tests

```c
assert_bus_error_is_propagated();
```

## EC-E-081: work in ISR

- Difficulty: Easy
- Language/platform: Embedded C
- Perspective: Interrupts
- Concept: work in ISR
- Symptom: The device misses deadlines or deadlocks.
- Diagnostic goal: Keep handlers short and defer work.

### Buggy code

```c
void ISR(void) { printf("edge"); read_sensor(); }
```

### Expected diagnosis

I/O, allocation, and slow calls inside an ISR are unsafe and unbounded.

### Corrected code

```c
volatile bool pending; void ISR(void) { pending = true; }
```

### Regression tests

```c
assert_main_loop_services_pending();
```

## EC-E-082: blocking delay

- Difficulty: Easy
- Language/platform: Embedded C
- Perspective: Timing
- Concept: blocking delay
- Symptom: A periodic task drifts.
- Diagnostic goal: Schedule against a monotonic deadline.

### Buggy code

```c
delay_ms(period); task();
```

### Expected diagnosis

Sleeping before work accumulates execution time as drift.

### Corrected code

```c
if (now >= deadline) { task(); deadline += period; }
```

### Regression tests

```c
assert_periodic_deadline_does_not_drift();
```

## EC-E-083: missing volatile

- Difficulty: Easy
- Language/platform: Embedded C
- Perspective: Volatile
- Concept: missing volatile
- Symptom: The main loop never sees a flag change.
- Diagnostic goal: Mark memory changed by hardware or ISR as volatile.

### Buggy code

```c
bool ready = false;
while (!ready) {}
```

### Expected diagnosis

The optimizer may cache a nonvolatile flag in a register.

### Corrected code

```c
volatile bool ready = false;
while (!ready) {}
```

### Regression tests

```c
assert_flag_change_is_observed();
```

## EC-E-084: off-by-one ring buffer

- Difficulty: Easy
- Language/platform: Embedded C
- Perspective: Buffers
- Concept: off-by-one ring buffer
- Symptom: Full and empty states are confused.
- Diagnostic goal: Track count or reserve one slot.

### Buggy code

```c
buffer[head++] = value;
```

### Expected diagnosis

The head wraps without checking capacity and overwrites unread data.

### Corrected code

```c
if (count < CAPACITY) { buffer[head] = value; head = (head + 1) % CAPACITY; count++; }
```

### Regression tests

```c
assert_full_buffer_rejects_new_value();
```

## EC-E-085: heap fragmentation

- Difficulty: Easy
- Language/platform: Embedded C
- Perspective: Memory
- Concept: heap fragmentation
- Symptom: Long uptime causes allocation failure.
- Diagnostic goal: Use fixed storage for bounded messages.

### Buggy code

```c
uint8_t *packet = malloc(length);
```

### Expected diagnosis

Repeated variable allocations fragment a small heap.

### Corrected code

```c
uint8_t packet[MAX_PACKET]; if (length > sizeof packet) return ERR_TOO_LARGE;
```

### Regression tests

```c
assert_oversized_packet_rejected();
```

## EC-E-086: raw units mistaken for volts

- Difficulty: Easy
- Language/platform: Embedded C
- Perspective: ADC
- Concept: raw units mistaken for volts
- Symptom: Control thresholds trigger at the wrong level.
- Diagnostic goal: Calibrate raw codes at the hardware boundary.

### Buggy code

```c
float volts = raw;
```

### Expected diagnosis

An ADC code needs reference voltage and resolution conversion.

### Corrected code

```c
float volts = raw * reference / ((1u << bits) - 1u);
```

### Regression tests

```c
assert_full_scale_equals_reference();
```

## EC-E-087: partial frame

- Difficulty: Easy
- Language/platform: Embedded C
- Perspective: UART
- Concept: partial frame
- Symptom: A split message is parsed as corrupt.
- Diagnostic goal: Accumulate until a complete delimiter/frame exists.

### Buggy code

```c
if (byte == ">") parse(frame);
```

### Expected diagnosis

A terminator may arrive in a later interrupt and a partial frame is discarded.

### Corrected code

```c
if (append(byte)) { if (byte == ">") parse(frame); }
```

### Regression tests

```c
assert_split_frame_reassembles();
```

## EC-E-088: feed before work

- Difficulty: Easy
- Language/platform: Embedded C
- Perspective: Watchdog
- Concept: feed before work
- Symptom: A stuck task keeps the watchdog alive.
- Diagnostic goal: Feed only after essential work succeeds.

### Buggy code

```c
watchdog_feed();
run_control_loop();
```

### Expected diagnosis

The watchdog proves loop entry, not successful progress.

### Corrected code

```c
run_control_loop(); watchdog_feed();
```

### Regression tests

```c
assert_failed_work_does_not_feed();
```

## EC-E-089: busy wait

- Difficulty: Easy
- Language/platform: Embedded C
- Perspective: Power
- Concept: busy wait
- Symptom: Sleep current is too high.
- Diagnostic goal: Use a timer or wake event rather than polling.

### Buggy code

```c
while (!event) { }
```

### Expected diagnosis

The CPU remains active while waiting for hardware.

### Corrected code

```c
sleep_until_event();
```

### Regression tests

```c
assert_wait_enters_low_power();
```

## EC-E-090: unchecked peripheral result

- Difficulty: Easy
- Language/platform: Embedded C
- Perspective: Safety
- Concept: unchecked peripheral result
- Symptom: A bus fault becomes invalid state.
- Diagnostic goal: Check every hardware operation before using output.

### Buggy code

```c
read_i2c(buf);
use(buf);
```

### Expected diagnosis

The buffer may be stale or incomplete after a failed transfer.

### Corrected code

```c
if (read_i2c(buf) != OK) return ERR_BUS;
use(buf);
```

### Regression tests

```c
assert_bus_error_is_propagated();
```

## EC-E-091: work in ISR

- Difficulty: Easy
- Language/platform: Embedded C
- Perspective: Interrupts
- Concept: work in ISR
- Symptom: The device misses deadlines or deadlocks.
- Diagnostic goal: Keep handlers short and defer work.

### Buggy code

```c
void ISR(void) { printf("edge"); read_sensor(); }
```

### Expected diagnosis

I/O, allocation, and slow calls inside an ISR are unsafe and unbounded.

### Corrected code

```c
volatile bool pending; void ISR(void) { pending = true; }
```

### Regression tests

```c
assert_main_loop_services_pending();
```

## EC-E-092: blocking delay

- Difficulty: Easy
- Language/platform: Embedded C
- Perspective: Timing
- Concept: blocking delay
- Symptom: A periodic task drifts.
- Diagnostic goal: Schedule against a monotonic deadline.

### Buggy code

```c
delay_ms(period); task();
```

### Expected diagnosis

Sleeping before work accumulates execution time as drift.

### Corrected code

```c
if (now >= deadline) { task(); deadline += period; }
```

### Regression tests

```c
assert_periodic_deadline_does_not_drift();
```

## EC-E-093: missing volatile

- Difficulty: Easy
- Language/platform: Embedded C
- Perspective: Volatile
- Concept: missing volatile
- Symptom: The main loop never sees a flag change.
- Diagnostic goal: Mark memory changed by hardware or ISR as volatile.

### Buggy code

```c
bool ready = false;
while (!ready) {}
```

### Expected diagnosis

The optimizer may cache a nonvolatile flag in a register.

### Corrected code

```c
volatile bool ready = false;
while (!ready) {}
```

### Regression tests

```c
assert_flag_change_is_observed();
```

## EC-E-094: off-by-one ring buffer

- Difficulty: Easy
- Language/platform: Embedded C
- Perspective: Buffers
- Concept: off-by-one ring buffer
- Symptom: Full and empty states are confused.
- Diagnostic goal: Track count or reserve one slot.

### Buggy code

```c
buffer[head++] = value;
```

### Expected diagnosis

The head wraps without checking capacity and overwrites unread data.

### Corrected code

```c
if (count < CAPACITY) { buffer[head] = value; head = (head + 1) % CAPACITY; count++; }
```

### Regression tests

```c
assert_full_buffer_rejects_new_value();
```

## EC-E-095: heap fragmentation

- Difficulty: Easy
- Language/platform: Embedded C
- Perspective: Memory
- Concept: heap fragmentation
- Symptom: Long uptime causes allocation failure.
- Diagnostic goal: Use fixed storage for bounded messages.

### Buggy code

```c
uint8_t *packet = malloc(length);
```

### Expected diagnosis

Repeated variable allocations fragment a small heap.

### Corrected code

```c
uint8_t packet[MAX_PACKET]; if (length > sizeof packet) return ERR_TOO_LARGE;
```

### Regression tests

```c
assert_oversized_packet_rejected();
```

## EC-E-096: raw units mistaken for volts

- Difficulty: Easy
- Language/platform: Embedded C
- Perspective: ADC
- Concept: raw units mistaken for volts
- Symptom: Control thresholds trigger at the wrong level.
- Diagnostic goal: Calibrate raw codes at the hardware boundary.

### Buggy code

```c
float volts = raw;
```

### Expected diagnosis

An ADC code needs reference voltage and resolution conversion.

### Corrected code

```c
float volts = raw * reference / ((1u << bits) - 1u);
```

### Regression tests

```c
assert_full_scale_equals_reference();
```

## EC-E-097: partial frame

- Difficulty: Easy
- Language/platform: Embedded C
- Perspective: UART
- Concept: partial frame
- Symptom: A split message is parsed as corrupt.
- Diagnostic goal: Accumulate until a complete delimiter/frame exists.

### Buggy code

```c
if (byte == ">") parse(frame);
```

### Expected diagnosis

A terminator may arrive in a later interrupt and a partial frame is discarded.

### Corrected code

```c
if (append(byte)) { if (byte == ">") parse(frame); }
```

### Regression tests

```c
assert_split_frame_reassembles();
```

## EC-E-098: feed before work

- Difficulty: Easy
- Language/platform: Embedded C
- Perspective: Watchdog
- Concept: feed before work
- Symptom: A stuck task keeps the watchdog alive.
- Diagnostic goal: Feed only after essential work succeeds.

### Buggy code

```c
watchdog_feed();
run_control_loop();
```

### Expected diagnosis

The watchdog proves loop entry, not successful progress.

### Corrected code

```c
run_control_loop(); watchdog_feed();
```

### Regression tests

```c
assert_failed_work_does_not_feed();
```

## EC-E-099: busy wait

- Difficulty: Easy
- Language/platform: Embedded C
- Perspective: Power
- Concept: busy wait
- Symptom: Sleep current is too high.
- Diagnostic goal: Use a timer or wake event rather than polling.

### Buggy code

```c
while (!event) { }
```

### Expected diagnosis

The CPU remains active while waiting for hardware.

### Corrected code

```c
sleep_until_event();
```

### Regression tests

```c
assert_wait_enters_low_power();
```

## EC-E-100: unchecked peripheral result

- Difficulty: Easy
- Language/platform: Embedded C
- Perspective: Safety
- Concept: unchecked peripheral result
- Symptom: A bus fault becomes invalid state.
- Diagnostic goal: Check every hardware operation before using output.

### Buggy code

```c
read_i2c(buf);
use(buf);
```

### Expected diagnosis

The buffer may be stale or incomplete after a failed transfer.

### Corrected code

```c
if (read_i2c(buf) != OK) return ERR_BUS;
use(buf);
```

### Regression tests

```c
assert_bus_error_is_propagated();
```

## EC-M-001: work in ISR

- Difficulty: Medium
- Language/platform: Embedded C
- Perspective: Interrupts
- Concept: work in ISR
- Symptom: The device misses deadlines or deadlocks.
- Diagnostic goal: Keep handlers short and defer work.

### Buggy code

```c
void ISR(void) { printf("edge"); read_sensor(); }
```

### Expected diagnosis

I/O, allocation, and slow calls inside an ISR are unsafe and unbounded.

### Corrected code

```c
volatile bool pending; void ISR(void) { pending = true; }
```

### Regression tests

```c
assert_main_loop_services_pending();
```

## EC-M-002: blocking delay

- Difficulty: Medium
- Language/platform: Embedded C
- Perspective: Timing
- Concept: blocking delay
- Symptom: A periodic task drifts.
- Diagnostic goal: Schedule against a monotonic deadline.

### Buggy code

```c
delay_ms(period); task();
```

### Expected diagnosis

Sleeping before work accumulates execution time as drift.

### Corrected code

```c
if (now >= deadline) { task(); deadline += period; }
```

### Regression tests

```c
assert_periodic_deadline_does_not_drift();
```

## EC-M-003: missing volatile

- Difficulty: Medium
- Language/platform: Embedded C
- Perspective: Volatile
- Concept: missing volatile
- Symptom: The main loop never sees a flag change.
- Diagnostic goal: Mark memory changed by hardware or ISR as volatile.

### Buggy code

```c
bool ready = false;
while (!ready) {}
```

### Expected diagnosis

The optimizer may cache a nonvolatile flag in a register.

### Corrected code

```c
volatile bool ready = false;
while (!ready) {}
```

### Regression tests

```c
assert_flag_change_is_observed();
```

## EC-M-004: off-by-one ring buffer

- Difficulty: Medium
- Language/platform: Embedded C
- Perspective: Buffers
- Concept: off-by-one ring buffer
- Symptom: Full and empty states are confused.
- Diagnostic goal: Track count or reserve one slot.

### Buggy code

```c
buffer[head++] = value;
```

### Expected diagnosis

The head wraps without checking capacity and overwrites unread data.

### Corrected code

```c
if (count < CAPACITY) { buffer[head] = value; head = (head + 1) % CAPACITY; count++; }
```

### Regression tests

```c
assert_full_buffer_rejects_new_value();
```

## EC-M-005: heap fragmentation

- Difficulty: Medium
- Language/platform: Embedded C
- Perspective: Memory
- Concept: heap fragmentation
- Symptom: Long uptime causes allocation failure.
- Diagnostic goal: Use fixed storage for bounded messages.

### Buggy code

```c
uint8_t *packet = malloc(length);
```

### Expected diagnosis

Repeated variable allocations fragment a small heap.

### Corrected code

```c
uint8_t packet[MAX_PACKET]; if (length > sizeof packet) return ERR_TOO_LARGE;
```

### Regression tests

```c
assert_oversized_packet_rejected();
```

## EC-M-006: raw units mistaken for volts

- Difficulty: Medium
- Language/platform: Embedded C
- Perspective: ADC
- Concept: raw units mistaken for volts
- Symptom: Control thresholds trigger at the wrong level.
- Diagnostic goal: Calibrate raw codes at the hardware boundary.

### Buggy code

```c
float volts = raw;
```

### Expected diagnosis

An ADC code needs reference voltage and resolution conversion.

### Corrected code

```c
float volts = raw * reference / ((1u << bits) - 1u);
```

### Regression tests

```c
assert_full_scale_equals_reference();
```

## EC-M-007: partial frame

- Difficulty: Medium
- Language/platform: Embedded C
- Perspective: UART
- Concept: partial frame
- Symptom: A split message is parsed as corrupt.
- Diagnostic goal: Accumulate until a complete delimiter/frame exists.

### Buggy code

```c
if (byte == ">") parse(frame);
```

### Expected diagnosis

A terminator may arrive in a later interrupt and a partial frame is discarded.

### Corrected code

```c
if (append(byte)) { if (byte == ">") parse(frame); }
```

### Regression tests

```c
assert_split_frame_reassembles();
```

## EC-M-008: feed before work

- Difficulty: Medium
- Language/platform: Embedded C
- Perspective: Watchdog
- Concept: feed before work
- Symptom: A stuck task keeps the watchdog alive.
- Diagnostic goal: Feed only after essential work succeeds.

### Buggy code

```c
watchdog_feed();
run_control_loop();
```

### Expected diagnosis

The watchdog proves loop entry, not successful progress.

### Corrected code

```c
run_control_loop(); watchdog_feed();
```

### Regression tests

```c
assert_failed_work_does_not_feed();
```

## EC-M-009: busy wait

- Difficulty: Medium
- Language/platform: Embedded C
- Perspective: Power
- Concept: busy wait
- Symptom: Sleep current is too high.
- Diagnostic goal: Use a timer or wake event rather than polling.

### Buggy code

```c
while (!event) { }
```

### Expected diagnosis

The CPU remains active while waiting for hardware.

### Corrected code

```c
sleep_until_event();
```

### Regression tests

```c
assert_wait_enters_low_power();
```

## EC-M-010: unchecked peripheral result

- Difficulty: Medium
- Language/platform: Embedded C
- Perspective: Safety
- Concept: unchecked peripheral result
- Symptom: A bus fault becomes invalid state.
- Diagnostic goal: Check every hardware operation before using output.

### Buggy code

```c
read_i2c(buf);
use(buf);
```

### Expected diagnosis

The buffer may be stale or incomplete after a failed transfer.

### Corrected code

```c
if (read_i2c(buf) != OK) return ERR_BUS;
use(buf);
```

### Regression tests

```c
assert_bus_error_is_propagated();
```

## EC-M-011: work in ISR

- Difficulty: Medium
- Language/platform: Embedded C
- Perspective: Interrupts
- Concept: work in ISR
- Symptom: The device misses deadlines or deadlocks.
- Diagnostic goal: Keep handlers short and defer work.

### Buggy code

```c
void ISR(void) { printf("edge"); read_sensor(); }
```

### Expected diagnosis

I/O, allocation, and slow calls inside an ISR are unsafe and unbounded.

### Corrected code

```c
volatile bool pending; void ISR(void) { pending = true; }
```

### Regression tests

```c
assert_main_loop_services_pending();
```

## EC-M-012: blocking delay

- Difficulty: Medium
- Language/platform: Embedded C
- Perspective: Timing
- Concept: blocking delay
- Symptom: A periodic task drifts.
- Diagnostic goal: Schedule against a monotonic deadline.

### Buggy code

```c
delay_ms(period); task();
```

### Expected diagnosis

Sleeping before work accumulates execution time as drift.

### Corrected code

```c
if (now >= deadline) { task(); deadline += period; }
```

### Regression tests

```c
assert_periodic_deadline_does_not_drift();
```

## EC-M-013: missing volatile

- Difficulty: Medium
- Language/platform: Embedded C
- Perspective: Volatile
- Concept: missing volatile
- Symptom: The main loop never sees a flag change.
- Diagnostic goal: Mark memory changed by hardware or ISR as volatile.

### Buggy code

```c
bool ready = false;
while (!ready) {}
```

### Expected diagnosis

The optimizer may cache a nonvolatile flag in a register.

### Corrected code

```c
volatile bool ready = false;
while (!ready) {}
```

### Regression tests

```c
assert_flag_change_is_observed();
```

## EC-M-014: off-by-one ring buffer

- Difficulty: Medium
- Language/platform: Embedded C
- Perspective: Buffers
- Concept: off-by-one ring buffer
- Symptom: Full and empty states are confused.
- Diagnostic goal: Track count or reserve one slot.

### Buggy code

```c
buffer[head++] = value;
```

### Expected diagnosis

The head wraps without checking capacity and overwrites unread data.

### Corrected code

```c
if (count < CAPACITY) { buffer[head] = value; head = (head + 1) % CAPACITY; count++; }
```

### Regression tests

```c
assert_full_buffer_rejects_new_value();
```

## EC-M-015: heap fragmentation

- Difficulty: Medium
- Language/platform: Embedded C
- Perspective: Memory
- Concept: heap fragmentation
- Symptom: Long uptime causes allocation failure.
- Diagnostic goal: Use fixed storage for bounded messages.

### Buggy code

```c
uint8_t *packet = malloc(length);
```

### Expected diagnosis

Repeated variable allocations fragment a small heap.

### Corrected code

```c
uint8_t packet[MAX_PACKET]; if (length > sizeof packet) return ERR_TOO_LARGE;
```

### Regression tests

```c
assert_oversized_packet_rejected();
```

## EC-M-016: raw units mistaken for volts

- Difficulty: Medium
- Language/platform: Embedded C
- Perspective: ADC
- Concept: raw units mistaken for volts
- Symptom: Control thresholds trigger at the wrong level.
- Diagnostic goal: Calibrate raw codes at the hardware boundary.

### Buggy code

```c
float volts = raw;
```

### Expected diagnosis

An ADC code needs reference voltage and resolution conversion.

### Corrected code

```c
float volts = raw * reference / ((1u << bits) - 1u);
```

### Regression tests

```c
assert_full_scale_equals_reference();
```

## EC-M-017: partial frame

- Difficulty: Medium
- Language/platform: Embedded C
- Perspective: UART
- Concept: partial frame
- Symptom: A split message is parsed as corrupt.
- Diagnostic goal: Accumulate until a complete delimiter/frame exists.

### Buggy code

```c
if (byte == ">") parse(frame);
```

### Expected diagnosis

A terminator may arrive in a later interrupt and a partial frame is discarded.

### Corrected code

```c
if (append(byte)) { if (byte == ">") parse(frame); }
```

### Regression tests

```c
assert_split_frame_reassembles();
```

## EC-M-018: feed before work

- Difficulty: Medium
- Language/platform: Embedded C
- Perspective: Watchdog
- Concept: feed before work
- Symptom: A stuck task keeps the watchdog alive.
- Diagnostic goal: Feed only after essential work succeeds.

### Buggy code

```c
watchdog_feed();
run_control_loop();
```

### Expected diagnosis

The watchdog proves loop entry, not successful progress.

### Corrected code

```c
run_control_loop(); watchdog_feed();
```

### Regression tests

```c
assert_failed_work_does_not_feed();
```

## EC-M-019: busy wait

- Difficulty: Medium
- Language/platform: Embedded C
- Perspective: Power
- Concept: busy wait
- Symptom: Sleep current is too high.
- Diagnostic goal: Use a timer or wake event rather than polling.

### Buggy code

```c
while (!event) { }
```

### Expected diagnosis

The CPU remains active while waiting for hardware.

### Corrected code

```c
sleep_until_event();
```

### Regression tests

```c
assert_wait_enters_low_power();
```

## EC-M-020: unchecked peripheral result

- Difficulty: Medium
- Language/platform: Embedded C
- Perspective: Safety
- Concept: unchecked peripheral result
- Symptom: A bus fault becomes invalid state.
- Diagnostic goal: Check every hardware operation before using output.

### Buggy code

```c
read_i2c(buf);
use(buf);
```

### Expected diagnosis

The buffer may be stale or incomplete after a failed transfer.

### Corrected code

```c
if (read_i2c(buf) != OK) return ERR_BUS;
use(buf);
```

### Regression tests

```c
assert_bus_error_is_propagated();
```

## EC-M-021: work in ISR

- Difficulty: Medium
- Language/platform: Embedded C
- Perspective: Interrupts
- Concept: work in ISR
- Symptom: The device misses deadlines or deadlocks.
- Diagnostic goal: Keep handlers short and defer work.

### Buggy code

```c
void ISR(void) { printf("edge"); read_sensor(); }
```

### Expected diagnosis

I/O, allocation, and slow calls inside an ISR are unsafe and unbounded.

### Corrected code

```c
volatile bool pending; void ISR(void) { pending = true; }
```

### Regression tests

```c
assert_main_loop_services_pending();
```

## EC-M-022: blocking delay

- Difficulty: Medium
- Language/platform: Embedded C
- Perspective: Timing
- Concept: blocking delay
- Symptom: A periodic task drifts.
- Diagnostic goal: Schedule against a monotonic deadline.

### Buggy code

```c
delay_ms(period); task();
```

### Expected diagnosis

Sleeping before work accumulates execution time as drift.

### Corrected code

```c
if (now >= deadline) { task(); deadline += period; }
```

### Regression tests

```c
assert_periodic_deadline_does_not_drift();
```

## EC-M-023: missing volatile

- Difficulty: Medium
- Language/platform: Embedded C
- Perspective: Volatile
- Concept: missing volatile
- Symptom: The main loop never sees a flag change.
- Diagnostic goal: Mark memory changed by hardware or ISR as volatile.

### Buggy code

```c
bool ready = false;
while (!ready) {}
```

### Expected diagnosis

The optimizer may cache a nonvolatile flag in a register.

### Corrected code

```c
volatile bool ready = false;
while (!ready) {}
```

### Regression tests

```c
assert_flag_change_is_observed();
```

## EC-M-024: off-by-one ring buffer

- Difficulty: Medium
- Language/platform: Embedded C
- Perspective: Buffers
- Concept: off-by-one ring buffer
- Symptom: Full and empty states are confused.
- Diagnostic goal: Track count or reserve one slot.

### Buggy code

```c
buffer[head++] = value;
```

### Expected diagnosis

The head wraps without checking capacity and overwrites unread data.

### Corrected code

```c
if (count < CAPACITY) { buffer[head] = value; head = (head + 1) % CAPACITY; count++; }
```

### Regression tests

```c
assert_full_buffer_rejects_new_value();
```

## EC-M-025: heap fragmentation

- Difficulty: Medium
- Language/platform: Embedded C
- Perspective: Memory
- Concept: heap fragmentation
- Symptom: Long uptime causes allocation failure.
- Diagnostic goal: Use fixed storage for bounded messages.

### Buggy code

```c
uint8_t *packet = malloc(length);
```

### Expected diagnosis

Repeated variable allocations fragment a small heap.

### Corrected code

```c
uint8_t packet[MAX_PACKET]; if (length > sizeof packet) return ERR_TOO_LARGE;
```

### Regression tests

```c
assert_oversized_packet_rejected();
```

## EC-M-026: raw units mistaken for volts

- Difficulty: Medium
- Language/platform: Embedded C
- Perspective: ADC
- Concept: raw units mistaken for volts
- Symptom: Control thresholds trigger at the wrong level.
- Diagnostic goal: Calibrate raw codes at the hardware boundary.

### Buggy code

```c
float volts = raw;
```

### Expected diagnosis

An ADC code needs reference voltage and resolution conversion.

### Corrected code

```c
float volts = raw * reference / ((1u << bits) - 1u);
```

### Regression tests

```c
assert_full_scale_equals_reference();
```

## EC-M-027: partial frame

- Difficulty: Medium
- Language/platform: Embedded C
- Perspective: UART
- Concept: partial frame
- Symptom: A split message is parsed as corrupt.
- Diagnostic goal: Accumulate until a complete delimiter/frame exists.

### Buggy code

```c
if (byte == ">") parse(frame);
```

### Expected diagnosis

A terminator may arrive in a later interrupt and a partial frame is discarded.

### Corrected code

```c
if (append(byte)) { if (byte == ">") parse(frame); }
```

### Regression tests

```c
assert_split_frame_reassembles();
```

## EC-M-028: feed before work

- Difficulty: Medium
- Language/platform: Embedded C
- Perspective: Watchdog
- Concept: feed before work
- Symptom: A stuck task keeps the watchdog alive.
- Diagnostic goal: Feed only after essential work succeeds.

### Buggy code

```c
watchdog_feed();
run_control_loop();
```

### Expected diagnosis

The watchdog proves loop entry, not successful progress.

### Corrected code

```c
run_control_loop(); watchdog_feed();
```

### Regression tests

```c
assert_failed_work_does_not_feed();
```

## EC-M-029: busy wait

- Difficulty: Medium
- Language/platform: Embedded C
- Perspective: Power
- Concept: busy wait
- Symptom: Sleep current is too high.
- Diagnostic goal: Use a timer or wake event rather than polling.

### Buggy code

```c
while (!event) { }
```

### Expected diagnosis

The CPU remains active while waiting for hardware.

### Corrected code

```c
sleep_until_event();
```

### Regression tests

```c
assert_wait_enters_low_power();
```

## EC-M-030: unchecked peripheral result

- Difficulty: Medium
- Language/platform: Embedded C
- Perspective: Safety
- Concept: unchecked peripheral result
- Symptom: A bus fault becomes invalid state.
- Diagnostic goal: Check every hardware operation before using output.

### Buggy code

```c
read_i2c(buf);
use(buf);
```

### Expected diagnosis

The buffer may be stale or incomplete after a failed transfer.

### Corrected code

```c
if (read_i2c(buf) != OK) return ERR_BUS;
use(buf);
```

### Regression tests

```c
assert_bus_error_is_propagated();
```

## EC-M-031: work in ISR

- Difficulty: Medium
- Language/platform: Embedded C
- Perspective: Interrupts
- Concept: work in ISR
- Symptom: The device misses deadlines or deadlocks.
- Diagnostic goal: Keep handlers short and defer work.

### Buggy code

```c
void ISR(void) { printf("edge"); read_sensor(); }
```

### Expected diagnosis

I/O, allocation, and slow calls inside an ISR are unsafe and unbounded.

### Corrected code

```c
volatile bool pending; void ISR(void) { pending = true; }
```

### Regression tests

```c
assert_main_loop_services_pending();
```

## EC-M-032: blocking delay

- Difficulty: Medium
- Language/platform: Embedded C
- Perspective: Timing
- Concept: blocking delay
- Symptom: A periodic task drifts.
- Diagnostic goal: Schedule against a monotonic deadline.

### Buggy code

```c
delay_ms(period); task();
```

### Expected diagnosis

Sleeping before work accumulates execution time as drift.

### Corrected code

```c
if (now >= deadline) { task(); deadline += period; }
```

### Regression tests

```c
assert_periodic_deadline_does_not_drift();
```

## EC-M-033: missing volatile

- Difficulty: Medium
- Language/platform: Embedded C
- Perspective: Volatile
- Concept: missing volatile
- Symptom: The main loop never sees a flag change.
- Diagnostic goal: Mark memory changed by hardware or ISR as volatile.

### Buggy code

```c
bool ready = false;
while (!ready) {}
```

### Expected diagnosis

The optimizer may cache a nonvolatile flag in a register.

### Corrected code

```c
volatile bool ready = false;
while (!ready) {}
```

### Regression tests

```c
assert_flag_change_is_observed();
```

## EC-M-034: off-by-one ring buffer

- Difficulty: Medium
- Language/platform: Embedded C
- Perspective: Buffers
- Concept: off-by-one ring buffer
- Symptom: Full and empty states are confused.
- Diagnostic goal: Track count or reserve one slot.

### Buggy code

```c
buffer[head++] = value;
```

### Expected diagnosis

The head wraps without checking capacity and overwrites unread data.

### Corrected code

```c
if (count < CAPACITY) { buffer[head] = value; head = (head + 1) % CAPACITY; count++; }
```

### Regression tests

```c
assert_full_buffer_rejects_new_value();
```

## EC-M-035: heap fragmentation

- Difficulty: Medium
- Language/platform: Embedded C
- Perspective: Memory
- Concept: heap fragmentation
- Symptom: Long uptime causes allocation failure.
- Diagnostic goal: Use fixed storage for bounded messages.

### Buggy code

```c
uint8_t *packet = malloc(length);
```

### Expected diagnosis

Repeated variable allocations fragment a small heap.

### Corrected code

```c
uint8_t packet[MAX_PACKET]; if (length > sizeof packet) return ERR_TOO_LARGE;
```

### Regression tests

```c
assert_oversized_packet_rejected();
```

## EC-M-036: raw units mistaken for volts

- Difficulty: Medium
- Language/platform: Embedded C
- Perspective: ADC
- Concept: raw units mistaken for volts
- Symptom: Control thresholds trigger at the wrong level.
- Diagnostic goal: Calibrate raw codes at the hardware boundary.

### Buggy code

```c
float volts = raw;
```

### Expected diagnosis

An ADC code needs reference voltage and resolution conversion.

### Corrected code

```c
float volts = raw * reference / ((1u << bits) - 1u);
```

### Regression tests

```c
assert_full_scale_equals_reference();
```

## EC-M-037: partial frame

- Difficulty: Medium
- Language/platform: Embedded C
- Perspective: UART
- Concept: partial frame
- Symptom: A split message is parsed as corrupt.
- Diagnostic goal: Accumulate until a complete delimiter/frame exists.

### Buggy code

```c
if (byte == ">") parse(frame);
```

### Expected diagnosis

A terminator may arrive in a later interrupt and a partial frame is discarded.

### Corrected code

```c
if (append(byte)) { if (byte == ">") parse(frame); }
```

### Regression tests

```c
assert_split_frame_reassembles();
```

## EC-M-038: feed before work

- Difficulty: Medium
- Language/platform: Embedded C
- Perspective: Watchdog
- Concept: feed before work
- Symptom: A stuck task keeps the watchdog alive.
- Diagnostic goal: Feed only after essential work succeeds.

### Buggy code

```c
watchdog_feed();
run_control_loop();
```

### Expected diagnosis

The watchdog proves loop entry, not successful progress.

### Corrected code

```c
run_control_loop(); watchdog_feed();
```

### Regression tests

```c
assert_failed_work_does_not_feed();
```

## EC-M-039: busy wait

- Difficulty: Medium
- Language/platform: Embedded C
- Perspective: Power
- Concept: busy wait
- Symptom: Sleep current is too high.
- Diagnostic goal: Use a timer or wake event rather than polling.

### Buggy code

```c
while (!event) { }
```

### Expected diagnosis

The CPU remains active while waiting for hardware.

### Corrected code

```c
sleep_until_event();
```

### Regression tests

```c
assert_wait_enters_low_power();
```

## EC-M-040: unchecked peripheral result

- Difficulty: Medium
- Language/platform: Embedded C
- Perspective: Safety
- Concept: unchecked peripheral result
- Symptom: A bus fault becomes invalid state.
- Diagnostic goal: Check every hardware operation before using output.

### Buggy code

```c
read_i2c(buf);
use(buf);
```

### Expected diagnosis

The buffer may be stale or incomplete after a failed transfer.

### Corrected code

```c
if (read_i2c(buf) != OK) return ERR_BUS;
use(buf);
```

### Regression tests

```c
assert_bus_error_is_propagated();
```

## EC-M-041: work in ISR

- Difficulty: Medium
- Language/platform: Embedded C
- Perspective: Interrupts
- Concept: work in ISR
- Symptom: The device misses deadlines or deadlocks.
- Diagnostic goal: Keep handlers short and defer work.

### Buggy code

```c
void ISR(void) { printf("edge"); read_sensor(); }
```

### Expected diagnosis

I/O, allocation, and slow calls inside an ISR are unsafe and unbounded.

### Corrected code

```c
volatile bool pending; void ISR(void) { pending = true; }
```

### Regression tests

```c
assert_main_loop_services_pending();
```

## EC-M-042: blocking delay

- Difficulty: Medium
- Language/platform: Embedded C
- Perspective: Timing
- Concept: blocking delay
- Symptom: A periodic task drifts.
- Diagnostic goal: Schedule against a monotonic deadline.

### Buggy code

```c
delay_ms(period); task();
```

### Expected diagnosis

Sleeping before work accumulates execution time as drift.

### Corrected code

```c
if (now >= deadline) { task(); deadline += period; }
```

### Regression tests

```c
assert_periodic_deadline_does_not_drift();
```

## EC-M-043: missing volatile

- Difficulty: Medium
- Language/platform: Embedded C
- Perspective: Volatile
- Concept: missing volatile
- Symptom: The main loop never sees a flag change.
- Diagnostic goal: Mark memory changed by hardware or ISR as volatile.

### Buggy code

```c
bool ready = false;
while (!ready) {}
```

### Expected diagnosis

The optimizer may cache a nonvolatile flag in a register.

### Corrected code

```c
volatile bool ready = false;
while (!ready) {}
```

### Regression tests

```c
assert_flag_change_is_observed();
```

## EC-M-044: off-by-one ring buffer

- Difficulty: Medium
- Language/platform: Embedded C
- Perspective: Buffers
- Concept: off-by-one ring buffer
- Symptom: Full and empty states are confused.
- Diagnostic goal: Track count or reserve one slot.

### Buggy code

```c
buffer[head++] = value;
```

### Expected diagnosis

The head wraps without checking capacity and overwrites unread data.

### Corrected code

```c
if (count < CAPACITY) { buffer[head] = value; head = (head + 1) % CAPACITY; count++; }
```

### Regression tests

```c
assert_full_buffer_rejects_new_value();
```

## EC-M-045: heap fragmentation

- Difficulty: Medium
- Language/platform: Embedded C
- Perspective: Memory
- Concept: heap fragmentation
- Symptom: Long uptime causes allocation failure.
- Diagnostic goal: Use fixed storage for bounded messages.

### Buggy code

```c
uint8_t *packet = malloc(length);
```

### Expected diagnosis

Repeated variable allocations fragment a small heap.

### Corrected code

```c
uint8_t packet[MAX_PACKET]; if (length > sizeof packet) return ERR_TOO_LARGE;
```

### Regression tests

```c
assert_oversized_packet_rejected();
```

## EC-M-046: raw units mistaken for volts

- Difficulty: Medium
- Language/platform: Embedded C
- Perspective: ADC
- Concept: raw units mistaken for volts
- Symptom: Control thresholds trigger at the wrong level.
- Diagnostic goal: Calibrate raw codes at the hardware boundary.

### Buggy code

```c
float volts = raw;
```

### Expected diagnosis

An ADC code needs reference voltage and resolution conversion.

### Corrected code

```c
float volts = raw * reference / ((1u << bits) - 1u);
```

### Regression tests

```c
assert_full_scale_equals_reference();
```

## EC-M-047: partial frame

- Difficulty: Medium
- Language/platform: Embedded C
- Perspective: UART
- Concept: partial frame
- Symptom: A split message is parsed as corrupt.
- Diagnostic goal: Accumulate until a complete delimiter/frame exists.

### Buggy code

```c
if (byte == ">") parse(frame);
```

### Expected diagnosis

A terminator may arrive in a later interrupt and a partial frame is discarded.

### Corrected code

```c
if (append(byte)) { if (byte == ">") parse(frame); }
```

### Regression tests

```c
assert_split_frame_reassembles();
```

## EC-M-048: feed before work

- Difficulty: Medium
- Language/platform: Embedded C
- Perspective: Watchdog
- Concept: feed before work
- Symptom: A stuck task keeps the watchdog alive.
- Diagnostic goal: Feed only after essential work succeeds.

### Buggy code

```c
watchdog_feed();
run_control_loop();
```

### Expected diagnosis

The watchdog proves loop entry, not successful progress.

### Corrected code

```c
run_control_loop(); watchdog_feed();
```

### Regression tests

```c
assert_failed_work_does_not_feed();
```

## EC-M-049: busy wait

- Difficulty: Medium
- Language/platform: Embedded C
- Perspective: Power
- Concept: busy wait
- Symptom: Sleep current is too high.
- Diagnostic goal: Use a timer or wake event rather than polling.

### Buggy code

```c
while (!event) { }
```

### Expected diagnosis

The CPU remains active while waiting for hardware.

### Corrected code

```c
sleep_until_event();
```

### Regression tests

```c
assert_wait_enters_low_power();
```

## EC-M-050: unchecked peripheral result

- Difficulty: Medium
- Language/platform: Embedded C
- Perspective: Safety
- Concept: unchecked peripheral result
- Symptom: A bus fault becomes invalid state.
- Diagnostic goal: Check every hardware operation before using output.

### Buggy code

```c
read_i2c(buf);
use(buf);
```

### Expected diagnosis

The buffer may be stale or incomplete after a failed transfer.

### Corrected code

```c
if (read_i2c(buf) != OK) return ERR_BUS;
use(buf);
```

### Regression tests

```c
assert_bus_error_is_propagated();
```

## EC-M-051: work in ISR

- Difficulty: Medium
- Language/platform: Embedded C
- Perspective: Interrupts
- Concept: work in ISR
- Symptom: The device misses deadlines or deadlocks.
- Diagnostic goal: Keep handlers short and defer work.

### Buggy code

```c
void ISR(void) { printf("edge"); read_sensor(); }
```

### Expected diagnosis

I/O, allocation, and slow calls inside an ISR are unsafe and unbounded.

### Corrected code

```c
volatile bool pending; void ISR(void) { pending = true; }
```

### Regression tests

```c
assert_main_loop_services_pending();
```

## EC-M-052: blocking delay

- Difficulty: Medium
- Language/platform: Embedded C
- Perspective: Timing
- Concept: blocking delay
- Symptom: A periodic task drifts.
- Diagnostic goal: Schedule against a monotonic deadline.

### Buggy code

```c
delay_ms(period); task();
```

### Expected diagnosis

Sleeping before work accumulates execution time as drift.

### Corrected code

```c
if (now >= deadline) { task(); deadline += period; }
```

### Regression tests

```c
assert_periodic_deadline_does_not_drift();
```

## EC-M-053: missing volatile

- Difficulty: Medium
- Language/platform: Embedded C
- Perspective: Volatile
- Concept: missing volatile
- Symptom: The main loop never sees a flag change.
- Diagnostic goal: Mark memory changed by hardware or ISR as volatile.

### Buggy code

```c
bool ready = false;
while (!ready) {}
```

### Expected diagnosis

The optimizer may cache a nonvolatile flag in a register.

### Corrected code

```c
volatile bool ready = false;
while (!ready) {}
```

### Regression tests

```c
assert_flag_change_is_observed();
```

## EC-M-054: off-by-one ring buffer

- Difficulty: Medium
- Language/platform: Embedded C
- Perspective: Buffers
- Concept: off-by-one ring buffer
- Symptom: Full and empty states are confused.
- Diagnostic goal: Track count or reserve one slot.

### Buggy code

```c
buffer[head++] = value;
```

### Expected diagnosis

The head wraps without checking capacity and overwrites unread data.

### Corrected code

```c
if (count < CAPACITY) { buffer[head] = value; head = (head + 1) % CAPACITY; count++; }
```

### Regression tests

```c
assert_full_buffer_rejects_new_value();
```

## EC-M-055: heap fragmentation

- Difficulty: Medium
- Language/platform: Embedded C
- Perspective: Memory
- Concept: heap fragmentation
- Symptom: Long uptime causes allocation failure.
- Diagnostic goal: Use fixed storage for bounded messages.

### Buggy code

```c
uint8_t *packet = malloc(length);
```

### Expected diagnosis

Repeated variable allocations fragment a small heap.

### Corrected code

```c
uint8_t packet[MAX_PACKET]; if (length > sizeof packet) return ERR_TOO_LARGE;
```

### Regression tests

```c
assert_oversized_packet_rejected();
```

## EC-M-056: raw units mistaken for volts

- Difficulty: Medium
- Language/platform: Embedded C
- Perspective: ADC
- Concept: raw units mistaken for volts
- Symptom: Control thresholds trigger at the wrong level.
- Diagnostic goal: Calibrate raw codes at the hardware boundary.

### Buggy code

```c
float volts = raw;
```

### Expected diagnosis

An ADC code needs reference voltage and resolution conversion.

### Corrected code

```c
float volts = raw * reference / ((1u << bits) - 1u);
```

### Regression tests

```c
assert_full_scale_equals_reference();
```

## EC-M-057: partial frame

- Difficulty: Medium
- Language/platform: Embedded C
- Perspective: UART
- Concept: partial frame
- Symptom: A split message is parsed as corrupt.
- Diagnostic goal: Accumulate until a complete delimiter/frame exists.

### Buggy code

```c
if (byte == ">") parse(frame);
```

### Expected diagnosis

A terminator may arrive in a later interrupt and a partial frame is discarded.

### Corrected code

```c
if (append(byte)) { if (byte == ">") parse(frame); }
```

### Regression tests

```c
assert_split_frame_reassembles();
```

## EC-M-058: feed before work

- Difficulty: Medium
- Language/platform: Embedded C
- Perspective: Watchdog
- Concept: feed before work
- Symptom: A stuck task keeps the watchdog alive.
- Diagnostic goal: Feed only after essential work succeeds.

### Buggy code

```c
watchdog_feed();
run_control_loop();
```

### Expected diagnosis

The watchdog proves loop entry, not successful progress.

### Corrected code

```c
run_control_loop(); watchdog_feed();
```

### Regression tests

```c
assert_failed_work_does_not_feed();
```

## EC-M-059: busy wait

- Difficulty: Medium
- Language/platform: Embedded C
- Perspective: Power
- Concept: busy wait
- Symptom: Sleep current is too high.
- Diagnostic goal: Use a timer or wake event rather than polling.

### Buggy code

```c
while (!event) { }
```

### Expected diagnosis

The CPU remains active while waiting for hardware.

### Corrected code

```c
sleep_until_event();
```

### Regression tests

```c
assert_wait_enters_low_power();
```

## EC-M-060: unchecked peripheral result

- Difficulty: Medium
- Language/platform: Embedded C
- Perspective: Safety
- Concept: unchecked peripheral result
- Symptom: A bus fault becomes invalid state.
- Diagnostic goal: Check every hardware operation before using output.

### Buggy code

```c
read_i2c(buf);
use(buf);
```

### Expected diagnosis

The buffer may be stale or incomplete after a failed transfer.

### Corrected code

```c
if (read_i2c(buf) != OK) return ERR_BUS;
use(buf);
```

### Regression tests

```c
assert_bus_error_is_propagated();
```

## EC-M-061: work in ISR

- Difficulty: Medium
- Language/platform: Embedded C
- Perspective: Interrupts
- Concept: work in ISR
- Symptom: The device misses deadlines or deadlocks.
- Diagnostic goal: Keep handlers short and defer work.

### Buggy code

```c
void ISR(void) { printf("edge"); read_sensor(); }
```

### Expected diagnosis

I/O, allocation, and slow calls inside an ISR are unsafe and unbounded.

### Corrected code

```c
volatile bool pending; void ISR(void) { pending = true; }
```

### Regression tests

```c
assert_main_loop_services_pending();
```

## EC-M-062: blocking delay

- Difficulty: Medium
- Language/platform: Embedded C
- Perspective: Timing
- Concept: blocking delay
- Symptom: A periodic task drifts.
- Diagnostic goal: Schedule against a monotonic deadline.

### Buggy code

```c
delay_ms(period); task();
```

### Expected diagnosis

Sleeping before work accumulates execution time as drift.

### Corrected code

```c
if (now >= deadline) { task(); deadline += period; }
```

### Regression tests

```c
assert_periodic_deadline_does_not_drift();
```

## EC-M-063: missing volatile

- Difficulty: Medium
- Language/platform: Embedded C
- Perspective: Volatile
- Concept: missing volatile
- Symptom: The main loop never sees a flag change.
- Diagnostic goal: Mark memory changed by hardware or ISR as volatile.

### Buggy code

```c
bool ready = false;
while (!ready) {}
```

### Expected diagnosis

The optimizer may cache a nonvolatile flag in a register.

### Corrected code

```c
volatile bool ready = false;
while (!ready) {}
```

### Regression tests

```c
assert_flag_change_is_observed();
```

## EC-M-064: off-by-one ring buffer

- Difficulty: Medium
- Language/platform: Embedded C
- Perspective: Buffers
- Concept: off-by-one ring buffer
- Symptom: Full and empty states are confused.
- Diagnostic goal: Track count or reserve one slot.

### Buggy code

```c
buffer[head++] = value;
```

### Expected diagnosis

The head wraps without checking capacity and overwrites unread data.

### Corrected code

```c
if (count < CAPACITY) { buffer[head] = value; head = (head + 1) % CAPACITY; count++; }
```

### Regression tests

```c
assert_full_buffer_rejects_new_value();
```

## EC-M-065: heap fragmentation

- Difficulty: Medium
- Language/platform: Embedded C
- Perspective: Memory
- Concept: heap fragmentation
- Symptom: Long uptime causes allocation failure.
- Diagnostic goal: Use fixed storage for bounded messages.

### Buggy code

```c
uint8_t *packet = malloc(length);
```

### Expected diagnosis

Repeated variable allocations fragment a small heap.

### Corrected code

```c
uint8_t packet[MAX_PACKET]; if (length > sizeof packet) return ERR_TOO_LARGE;
```

### Regression tests

```c
assert_oversized_packet_rejected();
```

## EC-M-066: raw units mistaken for volts

- Difficulty: Medium
- Language/platform: Embedded C
- Perspective: ADC
- Concept: raw units mistaken for volts
- Symptom: Control thresholds trigger at the wrong level.
- Diagnostic goal: Calibrate raw codes at the hardware boundary.

### Buggy code

```c
float volts = raw;
```

### Expected diagnosis

An ADC code needs reference voltage and resolution conversion.

### Corrected code

```c
float volts = raw * reference / ((1u << bits) - 1u);
```

### Regression tests

```c
assert_full_scale_equals_reference();
```

## EC-M-067: partial frame

- Difficulty: Medium
- Language/platform: Embedded C
- Perspective: UART
- Concept: partial frame
- Symptom: A split message is parsed as corrupt.
- Diagnostic goal: Accumulate until a complete delimiter/frame exists.

### Buggy code

```c
if (byte == ">") parse(frame);
```

### Expected diagnosis

A terminator may arrive in a later interrupt and a partial frame is discarded.

### Corrected code

```c
if (append(byte)) { if (byte == ">") parse(frame); }
```

### Regression tests

```c
assert_split_frame_reassembles();
```

## EC-M-068: feed before work

- Difficulty: Medium
- Language/platform: Embedded C
- Perspective: Watchdog
- Concept: feed before work
- Symptom: A stuck task keeps the watchdog alive.
- Diagnostic goal: Feed only after essential work succeeds.

### Buggy code

```c
watchdog_feed();
run_control_loop();
```

### Expected diagnosis

The watchdog proves loop entry, not successful progress.

### Corrected code

```c
run_control_loop(); watchdog_feed();
```

### Regression tests

```c
assert_failed_work_does_not_feed();
```

## EC-M-069: busy wait

- Difficulty: Medium
- Language/platform: Embedded C
- Perspective: Power
- Concept: busy wait
- Symptom: Sleep current is too high.
- Diagnostic goal: Use a timer or wake event rather than polling.

### Buggy code

```c
while (!event) { }
```

### Expected diagnosis

The CPU remains active while waiting for hardware.

### Corrected code

```c
sleep_until_event();
```

### Regression tests

```c
assert_wait_enters_low_power();
```

## EC-M-070: unchecked peripheral result

- Difficulty: Medium
- Language/platform: Embedded C
- Perspective: Safety
- Concept: unchecked peripheral result
- Symptom: A bus fault becomes invalid state.
- Diagnostic goal: Check every hardware operation before using output.

### Buggy code

```c
read_i2c(buf);
use(buf);
```

### Expected diagnosis

The buffer may be stale or incomplete after a failed transfer.

### Corrected code

```c
if (read_i2c(buf) != OK) return ERR_BUS;
use(buf);
```

### Regression tests

```c
assert_bus_error_is_propagated();
```

## EC-M-071: work in ISR

- Difficulty: Medium
- Language/platform: Embedded C
- Perspective: Interrupts
- Concept: work in ISR
- Symptom: The device misses deadlines or deadlocks.
- Diagnostic goal: Keep handlers short and defer work.

### Buggy code

```c
void ISR(void) { printf("edge"); read_sensor(); }
```

### Expected diagnosis

I/O, allocation, and slow calls inside an ISR are unsafe and unbounded.

### Corrected code

```c
volatile bool pending; void ISR(void) { pending = true; }
```

### Regression tests

```c
assert_main_loop_services_pending();
```

## EC-M-072: blocking delay

- Difficulty: Medium
- Language/platform: Embedded C
- Perspective: Timing
- Concept: blocking delay
- Symptom: A periodic task drifts.
- Diagnostic goal: Schedule against a monotonic deadline.

### Buggy code

```c
delay_ms(period); task();
```

### Expected diagnosis

Sleeping before work accumulates execution time as drift.

### Corrected code

```c
if (now >= deadline) { task(); deadline += period; }
```

### Regression tests

```c
assert_periodic_deadline_does_not_drift();
```

## EC-M-073: missing volatile

- Difficulty: Medium
- Language/platform: Embedded C
- Perspective: Volatile
- Concept: missing volatile
- Symptom: The main loop never sees a flag change.
- Diagnostic goal: Mark memory changed by hardware or ISR as volatile.

### Buggy code

```c
bool ready = false;
while (!ready) {}
```

### Expected diagnosis

The optimizer may cache a nonvolatile flag in a register.

### Corrected code

```c
volatile bool ready = false;
while (!ready) {}
```

### Regression tests

```c
assert_flag_change_is_observed();
```

## EC-M-074: off-by-one ring buffer

- Difficulty: Medium
- Language/platform: Embedded C
- Perspective: Buffers
- Concept: off-by-one ring buffer
- Symptom: Full and empty states are confused.
- Diagnostic goal: Track count or reserve one slot.

### Buggy code

```c
buffer[head++] = value;
```

### Expected diagnosis

The head wraps without checking capacity and overwrites unread data.

### Corrected code

```c
if (count < CAPACITY) { buffer[head] = value; head = (head + 1) % CAPACITY; count++; }
```

### Regression tests

```c
assert_full_buffer_rejects_new_value();
```

## EC-M-075: heap fragmentation

- Difficulty: Medium
- Language/platform: Embedded C
- Perspective: Memory
- Concept: heap fragmentation
- Symptom: Long uptime causes allocation failure.
- Diagnostic goal: Use fixed storage for bounded messages.

### Buggy code

```c
uint8_t *packet = malloc(length);
```

### Expected diagnosis

Repeated variable allocations fragment a small heap.

### Corrected code

```c
uint8_t packet[MAX_PACKET]; if (length > sizeof packet) return ERR_TOO_LARGE;
```

### Regression tests

```c
assert_oversized_packet_rejected();
```

## EC-M-076: raw units mistaken for volts

- Difficulty: Medium
- Language/platform: Embedded C
- Perspective: ADC
- Concept: raw units mistaken for volts
- Symptom: Control thresholds trigger at the wrong level.
- Diagnostic goal: Calibrate raw codes at the hardware boundary.

### Buggy code

```c
float volts = raw;
```

### Expected diagnosis

An ADC code needs reference voltage and resolution conversion.

### Corrected code

```c
float volts = raw * reference / ((1u << bits) - 1u);
```

### Regression tests

```c
assert_full_scale_equals_reference();
```

## EC-M-077: partial frame

- Difficulty: Medium
- Language/platform: Embedded C
- Perspective: UART
- Concept: partial frame
- Symptom: A split message is parsed as corrupt.
- Diagnostic goal: Accumulate until a complete delimiter/frame exists.

### Buggy code

```c
if (byte == ">") parse(frame);
```

### Expected diagnosis

A terminator may arrive in a later interrupt and a partial frame is discarded.

### Corrected code

```c
if (append(byte)) { if (byte == ">") parse(frame); }
```

### Regression tests

```c
assert_split_frame_reassembles();
```

## EC-M-078: feed before work

- Difficulty: Medium
- Language/platform: Embedded C
- Perspective: Watchdog
- Concept: feed before work
- Symptom: A stuck task keeps the watchdog alive.
- Diagnostic goal: Feed only after essential work succeeds.

### Buggy code

```c
watchdog_feed();
run_control_loop();
```

### Expected diagnosis

The watchdog proves loop entry, not successful progress.

### Corrected code

```c
run_control_loop(); watchdog_feed();
```

### Regression tests

```c
assert_failed_work_does_not_feed();
```

## EC-M-079: busy wait

- Difficulty: Medium
- Language/platform: Embedded C
- Perspective: Power
- Concept: busy wait
- Symptom: Sleep current is too high.
- Diagnostic goal: Use a timer or wake event rather than polling.

### Buggy code

```c
while (!event) { }
```

### Expected diagnosis

The CPU remains active while waiting for hardware.

### Corrected code

```c
sleep_until_event();
```

### Regression tests

```c
assert_wait_enters_low_power();
```

## EC-M-080: unchecked peripheral result

- Difficulty: Medium
- Language/platform: Embedded C
- Perspective: Safety
- Concept: unchecked peripheral result
- Symptom: A bus fault becomes invalid state.
- Diagnostic goal: Check every hardware operation before using output.

### Buggy code

```c
read_i2c(buf);
use(buf);
```

### Expected diagnosis

The buffer may be stale or incomplete after a failed transfer.

### Corrected code

```c
if (read_i2c(buf) != OK) return ERR_BUS;
use(buf);
```

### Regression tests

```c
assert_bus_error_is_propagated();
```

## EC-M-081: work in ISR

- Difficulty: Medium
- Language/platform: Embedded C
- Perspective: Interrupts
- Concept: work in ISR
- Symptom: The device misses deadlines or deadlocks.
- Diagnostic goal: Keep handlers short and defer work.

### Buggy code

```c
void ISR(void) { printf("edge"); read_sensor(); }
```

### Expected diagnosis

I/O, allocation, and slow calls inside an ISR are unsafe and unbounded.

### Corrected code

```c
volatile bool pending; void ISR(void) { pending = true; }
```

### Regression tests

```c
assert_main_loop_services_pending();
```

## EC-M-082: blocking delay

- Difficulty: Medium
- Language/platform: Embedded C
- Perspective: Timing
- Concept: blocking delay
- Symptom: A periodic task drifts.
- Diagnostic goal: Schedule against a monotonic deadline.

### Buggy code

```c
delay_ms(period); task();
```

### Expected diagnosis

Sleeping before work accumulates execution time as drift.

### Corrected code

```c
if (now >= deadline) { task(); deadline += period; }
```

### Regression tests

```c
assert_periodic_deadline_does_not_drift();
```

## EC-M-083: missing volatile

- Difficulty: Medium
- Language/platform: Embedded C
- Perspective: Volatile
- Concept: missing volatile
- Symptom: The main loop never sees a flag change.
- Diagnostic goal: Mark memory changed by hardware or ISR as volatile.

### Buggy code

```c
bool ready = false;
while (!ready) {}
```

### Expected diagnosis

The optimizer may cache a nonvolatile flag in a register.

### Corrected code

```c
volatile bool ready = false;
while (!ready) {}
```

### Regression tests

```c
assert_flag_change_is_observed();
```

## EC-M-084: off-by-one ring buffer

- Difficulty: Medium
- Language/platform: Embedded C
- Perspective: Buffers
- Concept: off-by-one ring buffer
- Symptom: Full and empty states are confused.
- Diagnostic goal: Track count or reserve one slot.

### Buggy code

```c
buffer[head++] = value;
```

### Expected diagnosis

The head wraps without checking capacity and overwrites unread data.

### Corrected code

```c
if (count < CAPACITY) { buffer[head] = value; head = (head + 1) % CAPACITY; count++; }
```

### Regression tests

```c
assert_full_buffer_rejects_new_value();
```

## EC-M-085: heap fragmentation

- Difficulty: Medium
- Language/platform: Embedded C
- Perspective: Memory
- Concept: heap fragmentation
- Symptom: Long uptime causes allocation failure.
- Diagnostic goal: Use fixed storage for bounded messages.

### Buggy code

```c
uint8_t *packet = malloc(length);
```

### Expected diagnosis

Repeated variable allocations fragment a small heap.

### Corrected code

```c
uint8_t packet[MAX_PACKET]; if (length > sizeof packet) return ERR_TOO_LARGE;
```

### Regression tests

```c
assert_oversized_packet_rejected();
```

## EC-M-086: raw units mistaken for volts

- Difficulty: Medium
- Language/platform: Embedded C
- Perspective: ADC
- Concept: raw units mistaken for volts
- Symptom: Control thresholds trigger at the wrong level.
- Diagnostic goal: Calibrate raw codes at the hardware boundary.

### Buggy code

```c
float volts = raw;
```

### Expected diagnosis

An ADC code needs reference voltage and resolution conversion.

### Corrected code

```c
float volts = raw * reference / ((1u << bits) - 1u);
```

### Regression tests

```c
assert_full_scale_equals_reference();
```

## EC-M-087: partial frame

- Difficulty: Medium
- Language/platform: Embedded C
- Perspective: UART
- Concept: partial frame
- Symptom: A split message is parsed as corrupt.
- Diagnostic goal: Accumulate until a complete delimiter/frame exists.

### Buggy code

```c
if (byte == ">") parse(frame);
```

### Expected diagnosis

A terminator may arrive in a later interrupt and a partial frame is discarded.

### Corrected code

```c
if (append(byte)) { if (byte == ">") parse(frame); }
```

### Regression tests

```c
assert_split_frame_reassembles();
```

## EC-M-088: feed before work

- Difficulty: Medium
- Language/platform: Embedded C
- Perspective: Watchdog
- Concept: feed before work
- Symptom: A stuck task keeps the watchdog alive.
- Diagnostic goal: Feed only after essential work succeeds.

### Buggy code

```c
watchdog_feed();
run_control_loop();
```

### Expected diagnosis

The watchdog proves loop entry, not successful progress.

### Corrected code

```c
run_control_loop(); watchdog_feed();
```

### Regression tests

```c
assert_failed_work_does_not_feed();
```

## EC-M-089: busy wait

- Difficulty: Medium
- Language/platform: Embedded C
- Perspective: Power
- Concept: busy wait
- Symptom: Sleep current is too high.
- Diagnostic goal: Use a timer or wake event rather than polling.

### Buggy code

```c
while (!event) { }
```

### Expected diagnosis

The CPU remains active while waiting for hardware.

### Corrected code

```c
sleep_until_event();
```

### Regression tests

```c
assert_wait_enters_low_power();
```

## EC-M-090: unchecked peripheral result

- Difficulty: Medium
- Language/platform: Embedded C
- Perspective: Safety
- Concept: unchecked peripheral result
- Symptom: A bus fault becomes invalid state.
- Diagnostic goal: Check every hardware operation before using output.

### Buggy code

```c
read_i2c(buf);
use(buf);
```

### Expected diagnosis

The buffer may be stale or incomplete after a failed transfer.

### Corrected code

```c
if (read_i2c(buf) != OK) return ERR_BUS;
use(buf);
```

### Regression tests

```c
assert_bus_error_is_propagated();
```

## EC-M-091: work in ISR

- Difficulty: Medium
- Language/platform: Embedded C
- Perspective: Interrupts
- Concept: work in ISR
- Symptom: The device misses deadlines or deadlocks.
- Diagnostic goal: Keep handlers short and defer work.

### Buggy code

```c
void ISR(void) { printf("edge"); read_sensor(); }
```

### Expected diagnosis

I/O, allocation, and slow calls inside an ISR are unsafe and unbounded.

### Corrected code

```c
volatile bool pending; void ISR(void) { pending = true; }
```

### Regression tests

```c
assert_main_loop_services_pending();
```

## EC-M-092: blocking delay

- Difficulty: Medium
- Language/platform: Embedded C
- Perspective: Timing
- Concept: blocking delay
- Symptom: A periodic task drifts.
- Diagnostic goal: Schedule against a monotonic deadline.

### Buggy code

```c
delay_ms(period); task();
```

### Expected diagnosis

Sleeping before work accumulates execution time as drift.

### Corrected code

```c
if (now >= deadline) { task(); deadline += period; }
```

### Regression tests

```c
assert_periodic_deadline_does_not_drift();
```

## EC-M-093: missing volatile

- Difficulty: Medium
- Language/platform: Embedded C
- Perspective: Volatile
- Concept: missing volatile
- Symptom: The main loop never sees a flag change.
- Diagnostic goal: Mark memory changed by hardware or ISR as volatile.

### Buggy code

```c
bool ready = false;
while (!ready) {}
```

### Expected diagnosis

The optimizer may cache a nonvolatile flag in a register.

### Corrected code

```c
volatile bool ready = false;
while (!ready) {}
```

### Regression tests

```c
assert_flag_change_is_observed();
```

## EC-M-094: off-by-one ring buffer

- Difficulty: Medium
- Language/platform: Embedded C
- Perspective: Buffers
- Concept: off-by-one ring buffer
- Symptom: Full and empty states are confused.
- Diagnostic goal: Track count or reserve one slot.

### Buggy code

```c
buffer[head++] = value;
```

### Expected diagnosis

The head wraps without checking capacity and overwrites unread data.

### Corrected code

```c
if (count < CAPACITY) { buffer[head] = value; head = (head + 1) % CAPACITY; count++; }
```

### Regression tests

```c
assert_full_buffer_rejects_new_value();
```

## EC-M-095: heap fragmentation

- Difficulty: Medium
- Language/platform: Embedded C
- Perspective: Memory
- Concept: heap fragmentation
- Symptom: Long uptime causes allocation failure.
- Diagnostic goal: Use fixed storage for bounded messages.

### Buggy code

```c
uint8_t *packet = malloc(length);
```

### Expected diagnosis

Repeated variable allocations fragment a small heap.

### Corrected code

```c
uint8_t packet[MAX_PACKET]; if (length > sizeof packet) return ERR_TOO_LARGE;
```

### Regression tests

```c
assert_oversized_packet_rejected();
```

## EC-M-096: raw units mistaken for volts

- Difficulty: Medium
- Language/platform: Embedded C
- Perspective: ADC
- Concept: raw units mistaken for volts
- Symptom: Control thresholds trigger at the wrong level.
- Diagnostic goal: Calibrate raw codes at the hardware boundary.

### Buggy code

```c
float volts = raw;
```

### Expected diagnosis

An ADC code needs reference voltage and resolution conversion.

### Corrected code

```c
float volts = raw * reference / ((1u << bits) - 1u);
```

### Regression tests

```c
assert_full_scale_equals_reference();
```

## EC-M-097: partial frame

- Difficulty: Medium
- Language/platform: Embedded C
- Perspective: UART
- Concept: partial frame
- Symptom: A split message is parsed as corrupt.
- Diagnostic goal: Accumulate until a complete delimiter/frame exists.

### Buggy code

```c
if (byte == ">") parse(frame);
```

### Expected diagnosis

A terminator may arrive in a later interrupt and a partial frame is discarded.

### Corrected code

```c
if (append(byte)) { if (byte == ">") parse(frame); }
```

### Regression tests

```c
assert_split_frame_reassembles();
```

## EC-M-098: feed before work

- Difficulty: Medium
- Language/platform: Embedded C
- Perspective: Watchdog
- Concept: feed before work
- Symptom: A stuck task keeps the watchdog alive.
- Diagnostic goal: Feed only after essential work succeeds.

### Buggy code

```c
watchdog_feed();
run_control_loop();
```

### Expected diagnosis

The watchdog proves loop entry, not successful progress.

### Corrected code

```c
run_control_loop(); watchdog_feed();
```

### Regression tests

```c
assert_failed_work_does_not_feed();
```

## EC-M-099: busy wait

- Difficulty: Medium
- Language/platform: Embedded C
- Perspective: Power
- Concept: busy wait
- Symptom: Sleep current is too high.
- Diagnostic goal: Use a timer or wake event rather than polling.

### Buggy code

```c
while (!event) { }
```

### Expected diagnosis

The CPU remains active while waiting for hardware.

### Corrected code

```c
sleep_until_event();
```

### Regression tests

```c
assert_wait_enters_low_power();
```

## EC-M-100: unchecked peripheral result

- Difficulty: Medium
- Language/platform: Embedded C
- Perspective: Safety
- Concept: unchecked peripheral result
- Symptom: A bus fault becomes invalid state.
- Diagnostic goal: Check every hardware operation before using output.

### Buggy code

```c
read_i2c(buf);
use(buf);
```

### Expected diagnosis

The buffer may be stale or incomplete after a failed transfer.

### Corrected code

```c
if (read_i2c(buf) != OK) return ERR_BUS;
use(buf);
```

### Regression tests

```c
assert_bus_error_is_propagated();
```

## EC-H-001: work in ISR

- Difficulty: Hard
- Language/platform: Embedded C
- Perspective: Interrupts
- Concept: work in ISR
- Symptom: The device misses deadlines or deadlocks.
- Diagnostic goal: Keep handlers short and defer work.

### Buggy code

```c
void ISR(void) { printf("edge"); read_sensor(); }
```

### Expected diagnosis

I/O, allocation, and slow calls inside an ISR are unsafe and unbounded.

### Corrected code

```c
volatile bool pending; void ISR(void) { pending = true; }
```

### Regression tests

```c
assert_main_loop_services_pending();
```

## EC-H-002: blocking delay

- Difficulty: Hard
- Language/platform: Embedded C
- Perspective: Timing
- Concept: blocking delay
- Symptom: A periodic task drifts.
- Diagnostic goal: Schedule against a monotonic deadline.

### Buggy code

```c
delay_ms(period); task();
```

### Expected diagnosis

Sleeping before work accumulates execution time as drift.

### Corrected code

```c
if (now >= deadline) { task(); deadline += period; }
```

### Regression tests

```c
assert_periodic_deadline_does_not_drift();
```

## EC-H-003: missing volatile

- Difficulty: Hard
- Language/platform: Embedded C
- Perspective: Volatile
- Concept: missing volatile
- Symptom: The main loop never sees a flag change.
- Diagnostic goal: Mark memory changed by hardware or ISR as volatile.

### Buggy code

```c
bool ready = false;
while (!ready) {}
```

### Expected diagnosis

The optimizer may cache a nonvolatile flag in a register.

### Corrected code

```c
volatile bool ready = false;
while (!ready) {}
```

### Regression tests

```c
assert_flag_change_is_observed();
```

## EC-H-004: off-by-one ring buffer

- Difficulty: Hard
- Language/platform: Embedded C
- Perspective: Buffers
- Concept: off-by-one ring buffer
- Symptom: Full and empty states are confused.
- Diagnostic goal: Track count or reserve one slot.

### Buggy code

```c
buffer[head++] = value;
```

### Expected diagnosis

The head wraps without checking capacity and overwrites unread data.

### Corrected code

```c
if (count < CAPACITY) { buffer[head] = value; head = (head + 1) % CAPACITY; count++; }
```

### Regression tests

```c
assert_full_buffer_rejects_new_value();
```

## EC-H-005: heap fragmentation

- Difficulty: Hard
- Language/platform: Embedded C
- Perspective: Memory
- Concept: heap fragmentation
- Symptom: Long uptime causes allocation failure.
- Diagnostic goal: Use fixed storage for bounded messages.

### Buggy code

```c
uint8_t *packet = malloc(length);
```

### Expected diagnosis

Repeated variable allocations fragment a small heap.

### Corrected code

```c
uint8_t packet[MAX_PACKET]; if (length > sizeof packet) return ERR_TOO_LARGE;
```

### Regression tests

```c
assert_oversized_packet_rejected();
```

## EC-H-006: raw units mistaken for volts

- Difficulty: Hard
- Language/platform: Embedded C
- Perspective: ADC
- Concept: raw units mistaken for volts
- Symptom: Control thresholds trigger at the wrong level.
- Diagnostic goal: Calibrate raw codes at the hardware boundary.

### Buggy code

```c
float volts = raw;
```

### Expected diagnosis

An ADC code needs reference voltage and resolution conversion.

### Corrected code

```c
float volts = raw * reference / ((1u << bits) - 1u);
```

### Regression tests

```c
assert_full_scale_equals_reference();
```

## EC-H-007: partial frame

- Difficulty: Hard
- Language/platform: Embedded C
- Perspective: UART
- Concept: partial frame
- Symptom: A split message is parsed as corrupt.
- Diagnostic goal: Accumulate until a complete delimiter/frame exists.

### Buggy code

```c
if (byte == ">") parse(frame);
```

### Expected diagnosis

A terminator may arrive in a later interrupt and a partial frame is discarded.

### Corrected code

```c
if (append(byte)) { if (byte == ">") parse(frame); }
```

### Regression tests

```c
assert_split_frame_reassembles();
```

## EC-H-008: feed before work

- Difficulty: Hard
- Language/platform: Embedded C
- Perspective: Watchdog
- Concept: feed before work
- Symptom: A stuck task keeps the watchdog alive.
- Diagnostic goal: Feed only after essential work succeeds.

### Buggy code

```c
watchdog_feed();
run_control_loop();
```

### Expected diagnosis

The watchdog proves loop entry, not successful progress.

### Corrected code

```c
run_control_loop(); watchdog_feed();
```

### Regression tests

```c
assert_failed_work_does_not_feed();
```

## EC-H-009: busy wait

- Difficulty: Hard
- Language/platform: Embedded C
- Perspective: Power
- Concept: busy wait
- Symptom: Sleep current is too high.
- Diagnostic goal: Use a timer or wake event rather than polling.

### Buggy code

```c
while (!event) { }
```

### Expected diagnosis

The CPU remains active while waiting for hardware.

### Corrected code

```c
sleep_until_event();
```

### Regression tests

```c
assert_wait_enters_low_power();
```

## EC-H-010: unchecked peripheral result

- Difficulty: Hard
- Language/platform: Embedded C
- Perspective: Safety
- Concept: unchecked peripheral result
- Symptom: A bus fault becomes invalid state.
- Diagnostic goal: Check every hardware operation before using output.

### Buggy code

```c
read_i2c(buf);
use(buf);
```

### Expected diagnosis

The buffer may be stale or incomplete after a failed transfer.

### Corrected code

```c
if (read_i2c(buf) != OK) return ERR_BUS;
use(buf);
```

### Regression tests

```c
assert_bus_error_is_propagated();
```

## EC-H-011: work in ISR

- Difficulty: Hard
- Language/platform: Embedded C
- Perspective: Interrupts
- Concept: work in ISR
- Symptom: The device misses deadlines or deadlocks.
- Diagnostic goal: Keep handlers short and defer work.

### Buggy code

```c
void ISR(void) { printf("edge"); read_sensor(); }
```

### Expected diagnosis

I/O, allocation, and slow calls inside an ISR are unsafe and unbounded.

### Corrected code

```c
volatile bool pending; void ISR(void) { pending = true; }
```

### Regression tests

```c
assert_main_loop_services_pending();
```

## EC-H-012: blocking delay

- Difficulty: Hard
- Language/platform: Embedded C
- Perspective: Timing
- Concept: blocking delay
- Symptom: A periodic task drifts.
- Diagnostic goal: Schedule against a monotonic deadline.

### Buggy code

```c
delay_ms(period); task();
```

### Expected diagnosis

Sleeping before work accumulates execution time as drift.

### Corrected code

```c
if (now >= deadline) { task(); deadline += period; }
```

### Regression tests

```c
assert_periodic_deadline_does_not_drift();
```

## EC-H-013: missing volatile

- Difficulty: Hard
- Language/platform: Embedded C
- Perspective: Volatile
- Concept: missing volatile
- Symptom: The main loop never sees a flag change.
- Diagnostic goal: Mark memory changed by hardware or ISR as volatile.

### Buggy code

```c
bool ready = false;
while (!ready) {}
```

### Expected diagnosis

The optimizer may cache a nonvolatile flag in a register.

### Corrected code

```c
volatile bool ready = false;
while (!ready) {}
```

### Regression tests

```c
assert_flag_change_is_observed();
```

## EC-H-014: off-by-one ring buffer

- Difficulty: Hard
- Language/platform: Embedded C
- Perspective: Buffers
- Concept: off-by-one ring buffer
- Symptom: Full and empty states are confused.
- Diagnostic goal: Track count or reserve one slot.

### Buggy code

```c
buffer[head++] = value;
```

### Expected diagnosis

The head wraps without checking capacity and overwrites unread data.

### Corrected code

```c
if (count < CAPACITY) { buffer[head] = value; head = (head + 1) % CAPACITY; count++; }
```

### Regression tests

```c
assert_full_buffer_rejects_new_value();
```

## EC-H-015: heap fragmentation

- Difficulty: Hard
- Language/platform: Embedded C
- Perspective: Memory
- Concept: heap fragmentation
- Symptom: Long uptime causes allocation failure.
- Diagnostic goal: Use fixed storage for bounded messages.

### Buggy code

```c
uint8_t *packet = malloc(length);
```

### Expected diagnosis

Repeated variable allocations fragment a small heap.

### Corrected code

```c
uint8_t packet[MAX_PACKET]; if (length > sizeof packet) return ERR_TOO_LARGE;
```

### Regression tests

```c
assert_oversized_packet_rejected();
```

## EC-H-016: raw units mistaken for volts

- Difficulty: Hard
- Language/platform: Embedded C
- Perspective: ADC
- Concept: raw units mistaken for volts
- Symptom: Control thresholds trigger at the wrong level.
- Diagnostic goal: Calibrate raw codes at the hardware boundary.

### Buggy code

```c
float volts = raw;
```

### Expected diagnosis

An ADC code needs reference voltage and resolution conversion.

### Corrected code

```c
float volts = raw * reference / ((1u << bits) - 1u);
```

### Regression tests

```c
assert_full_scale_equals_reference();
```

## EC-H-017: partial frame

- Difficulty: Hard
- Language/platform: Embedded C
- Perspective: UART
- Concept: partial frame
- Symptom: A split message is parsed as corrupt.
- Diagnostic goal: Accumulate until a complete delimiter/frame exists.

### Buggy code

```c
if (byte == ">") parse(frame);
```

### Expected diagnosis

A terminator may arrive in a later interrupt and a partial frame is discarded.

### Corrected code

```c
if (append(byte)) { if (byte == ">") parse(frame); }
```

### Regression tests

```c
assert_split_frame_reassembles();
```

## EC-H-018: feed before work

- Difficulty: Hard
- Language/platform: Embedded C
- Perspective: Watchdog
- Concept: feed before work
- Symptom: A stuck task keeps the watchdog alive.
- Diagnostic goal: Feed only after essential work succeeds.

### Buggy code

```c
watchdog_feed();
run_control_loop();
```

### Expected diagnosis

The watchdog proves loop entry, not successful progress.

### Corrected code

```c
run_control_loop(); watchdog_feed();
```

### Regression tests

```c
assert_failed_work_does_not_feed();
```

## EC-H-019: busy wait

- Difficulty: Hard
- Language/platform: Embedded C
- Perspective: Power
- Concept: busy wait
- Symptom: Sleep current is too high.
- Diagnostic goal: Use a timer or wake event rather than polling.

### Buggy code

```c
while (!event) { }
```

### Expected diagnosis

The CPU remains active while waiting for hardware.

### Corrected code

```c
sleep_until_event();
```

### Regression tests

```c
assert_wait_enters_low_power();
```

## EC-H-020: unchecked peripheral result

- Difficulty: Hard
- Language/platform: Embedded C
- Perspective: Safety
- Concept: unchecked peripheral result
- Symptom: A bus fault becomes invalid state.
- Diagnostic goal: Check every hardware operation before using output.

### Buggy code

```c
read_i2c(buf);
use(buf);
```

### Expected diagnosis

The buffer may be stale or incomplete after a failed transfer.

### Corrected code

```c
if (read_i2c(buf) != OK) return ERR_BUS;
use(buf);
```

### Regression tests

```c
assert_bus_error_is_propagated();
```

## EC-H-021: work in ISR

- Difficulty: Hard
- Language/platform: Embedded C
- Perspective: Interrupts
- Concept: work in ISR
- Symptom: The device misses deadlines or deadlocks.
- Diagnostic goal: Keep handlers short and defer work.

### Buggy code

```c
void ISR(void) { printf("edge"); read_sensor(); }
```

### Expected diagnosis

I/O, allocation, and slow calls inside an ISR are unsafe and unbounded.

### Corrected code

```c
volatile bool pending; void ISR(void) { pending = true; }
```

### Regression tests

```c
assert_main_loop_services_pending();
```

## EC-H-022: blocking delay

- Difficulty: Hard
- Language/platform: Embedded C
- Perspective: Timing
- Concept: blocking delay
- Symptom: A periodic task drifts.
- Diagnostic goal: Schedule against a monotonic deadline.

### Buggy code

```c
delay_ms(period); task();
```

### Expected diagnosis

Sleeping before work accumulates execution time as drift.

### Corrected code

```c
if (now >= deadline) { task(); deadline += period; }
```

### Regression tests

```c
assert_periodic_deadline_does_not_drift();
```

## EC-H-023: missing volatile

- Difficulty: Hard
- Language/platform: Embedded C
- Perspective: Volatile
- Concept: missing volatile
- Symptom: The main loop never sees a flag change.
- Diagnostic goal: Mark memory changed by hardware or ISR as volatile.

### Buggy code

```c
bool ready = false;
while (!ready) {}
```

### Expected diagnosis

The optimizer may cache a nonvolatile flag in a register.

### Corrected code

```c
volatile bool ready = false;
while (!ready) {}
```

### Regression tests

```c
assert_flag_change_is_observed();
```

## EC-H-024: off-by-one ring buffer

- Difficulty: Hard
- Language/platform: Embedded C
- Perspective: Buffers
- Concept: off-by-one ring buffer
- Symptom: Full and empty states are confused.
- Diagnostic goal: Track count or reserve one slot.

### Buggy code

```c
buffer[head++] = value;
```

### Expected diagnosis

The head wraps without checking capacity and overwrites unread data.

### Corrected code

```c
if (count < CAPACITY) { buffer[head] = value; head = (head + 1) % CAPACITY; count++; }
```

### Regression tests

```c
assert_full_buffer_rejects_new_value();
```

## EC-H-025: heap fragmentation

- Difficulty: Hard
- Language/platform: Embedded C
- Perspective: Memory
- Concept: heap fragmentation
- Symptom: Long uptime causes allocation failure.
- Diagnostic goal: Use fixed storage for bounded messages.

### Buggy code

```c
uint8_t *packet = malloc(length);
```

### Expected diagnosis

Repeated variable allocations fragment a small heap.

### Corrected code

```c
uint8_t packet[MAX_PACKET]; if (length > sizeof packet) return ERR_TOO_LARGE;
```

### Regression tests

```c
assert_oversized_packet_rejected();
```

## EC-H-026: raw units mistaken for volts

- Difficulty: Hard
- Language/platform: Embedded C
- Perspective: ADC
- Concept: raw units mistaken for volts
- Symptom: Control thresholds trigger at the wrong level.
- Diagnostic goal: Calibrate raw codes at the hardware boundary.

### Buggy code

```c
float volts = raw;
```

### Expected diagnosis

An ADC code needs reference voltage and resolution conversion.

### Corrected code

```c
float volts = raw * reference / ((1u << bits) - 1u);
```

### Regression tests

```c
assert_full_scale_equals_reference();
```

## EC-H-027: partial frame

- Difficulty: Hard
- Language/platform: Embedded C
- Perspective: UART
- Concept: partial frame
- Symptom: A split message is parsed as corrupt.
- Diagnostic goal: Accumulate until a complete delimiter/frame exists.

### Buggy code

```c
if (byte == ">") parse(frame);
```

### Expected diagnosis

A terminator may arrive in a later interrupt and a partial frame is discarded.

### Corrected code

```c
if (append(byte)) { if (byte == ">") parse(frame); }
```

### Regression tests

```c
assert_split_frame_reassembles();
```

## EC-H-028: feed before work

- Difficulty: Hard
- Language/platform: Embedded C
- Perspective: Watchdog
- Concept: feed before work
- Symptom: A stuck task keeps the watchdog alive.
- Diagnostic goal: Feed only after essential work succeeds.

### Buggy code

```c
watchdog_feed();
run_control_loop();
```

### Expected diagnosis

The watchdog proves loop entry, not successful progress.

### Corrected code

```c
run_control_loop(); watchdog_feed();
```

### Regression tests

```c
assert_failed_work_does_not_feed();
```

## EC-H-029: busy wait

- Difficulty: Hard
- Language/platform: Embedded C
- Perspective: Power
- Concept: busy wait
- Symptom: Sleep current is too high.
- Diagnostic goal: Use a timer or wake event rather than polling.

### Buggy code

```c
while (!event) { }
```

### Expected diagnosis

The CPU remains active while waiting for hardware.

### Corrected code

```c
sleep_until_event();
```

### Regression tests

```c
assert_wait_enters_low_power();
```

## EC-H-030: unchecked peripheral result

- Difficulty: Hard
- Language/platform: Embedded C
- Perspective: Safety
- Concept: unchecked peripheral result
- Symptom: A bus fault becomes invalid state.
- Diagnostic goal: Check every hardware operation before using output.

### Buggy code

```c
read_i2c(buf);
use(buf);
```

### Expected diagnosis

The buffer may be stale or incomplete after a failed transfer.

### Corrected code

```c
if (read_i2c(buf) != OK) return ERR_BUS;
use(buf);
```

### Regression tests

```c
assert_bus_error_is_propagated();
```

## EC-H-031: work in ISR

- Difficulty: Hard
- Language/platform: Embedded C
- Perspective: Interrupts
- Concept: work in ISR
- Symptom: The device misses deadlines or deadlocks.
- Diagnostic goal: Keep handlers short and defer work.

### Buggy code

```c
void ISR(void) { printf("edge"); read_sensor(); }
```

### Expected diagnosis

I/O, allocation, and slow calls inside an ISR are unsafe and unbounded.

### Corrected code

```c
volatile bool pending; void ISR(void) { pending = true; }
```

### Regression tests

```c
assert_main_loop_services_pending();
```

## EC-H-032: blocking delay

- Difficulty: Hard
- Language/platform: Embedded C
- Perspective: Timing
- Concept: blocking delay
- Symptom: A periodic task drifts.
- Diagnostic goal: Schedule against a monotonic deadline.

### Buggy code

```c
delay_ms(period); task();
```

### Expected diagnosis

Sleeping before work accumulates execution time as drift.

### Corrected code

```c
if (now >= deadline) { task(); deadline += period; }
```

### Regression tests

```c
assert_periodic_deadline_does_not_drift();
```

## EC-H-033: missing volatile

- Difficulty: Hard
- Language/platform: Embedded C
- Perspective: Volatile
- Concept: missing volatile
- Symptom: The main loop never sees a flag change.
- Diagnostic goal: Mark memory changed by hardware or ISR as volatile.

### Buggy code

```c
bool ready = false;
while (!ready) {}
```

### Expected diagnosis

The optimizer may cache a nonvolatile flag in a register.

### Corrected code

```c
volatile bool ready = false;
while (!ready) {}
```

### Regression tests

```c
assert_flag_change_is_observed();
```

## EC-H-034: off-by-one ring buffer

- Difficulty: Hard
- Language/platform: Embedded C
- Perspective: Buffers
- Concept: off-by-one ring buffer
- Symptom: Full and empty states are confused.
- Diagnostic goal: Track count or reserve one slot.

### Buggy code

```c
buffer[head++] = value;
```

### Expected diagnosis

The head wraps without checking capacity and overwrites unread data.

### Corrected code

```c
if (count < CAPACITY) { buffer[head] = value; head = (head + 1) % CAPACITY; count++; }
```

### Regression tests

```c
assert_full_buffer_rejects_new_value();
```

## EC-H-035: heap fragmentation

- Difficulty: Hard
- Language/platform: Embedded C
- Perspective: Memory
- Concept: heap fragmentation
- Symptom: Long uptime causes allocation failure.
- Diagnostic goal: Use fixed storage for bounded messages.

### Buggy code

```c
uint8_t *packet = malloc(length);
```

### Expected diagnosis

Repeated variable allocations fragment a small heap.

### Corrected code

```c
uint8_t packet[MAX_PACKET]; if (length > sizeof packet) return ERR_TOO_LARGE;
```

### Regression tests

```c
assert_oversized_packet_rejected();
```

## EC-H-036: raw units mistaken for volts

- Difficulty: Hard
- Language/platform: Embedded C
- Perspective: ADC
- Concept: raw units mistaken for volts
- Symptom: Control thresholds trigger at the wrong level.
- Diagnostic goal: Calibrate raw codes at the hardware boundary.

### Buggy code

```c
float volts = raw;
```

### Expected diagnosis

An ADC code needs reference voltage and resolution conversion.

### Corrected code

```c
float volts = raw * reference / ((1u << bits) - 1u);
```

### Regression tests

```c
assert_full_scale_equals_reference();
```

## EC-H-037: partial frame

- Difficulty: Hard
- Language/platform: Embedded C
- Perspective: UART
- Concept: partial frame
- Symptom: A split message is parsed as corrupt.
- Diagnostic goal: Accumulate until a complete delimiter/frame exists.

### Buggy code

```c
if (byte == ">") parse(frame);
```

### Expected diagnosis

A terminator may arrive in a later interrupt and a partial frame is discarded.

### Corrected code

```c
if (append(byte)) { if (byte == ">") parse(frame); }
```

### Regression tests

```c
assert_split_frame_reassembles();
```

## EC-H-038: feed before work

- Difficulty: Hard
- Language/platform: Embedded C
- Perspective: Watchdog
- Concept: feed before work
- Symptom: A stuck task keeps the watchdog alive.
- Diagnostic goal: Feed only after essential work succeeds.

### Buggy code

```c
watchdog_feed();
run_control_loop();
```

### Expected diagnosis

The watchdog proves loop entry, not successful progress.

### Corrected code

```c
run_control_loop(); watchdog_feed();
```

### Regression tests

```c
assert_failed_work_does_not_feed();
```

## EC-H-039: busy wait

- Difficulty: Hard
- Language/platform: Embedded C
- Perspective: Power
- Concept: busy wait
- Symptom: Sleep current is too high.
- Diagnostic goal: Use a timer or wake event rather than polling.

### Buggy code

```c
while (!event) { }
```

### Expected diagnosis

The CPU remains active while waiting for hardware.

### Corrected code

```c
sleep_until_event();
```

### Regression tests

```c
assert_wait_enters_low_power();
```

## EC-H-040: unchecked peripheral result

- Difficulty: Hard
- Language/platform: Embedded C
- Perspective: Safety
- Concept: unchecked peripheral result
- Symptom: A bus fault becomes invalid state.
- Diagnostic goal: Check every hardware operation before using output.

### Buggy code

```c
read_i2c(buf);
use(buf);
```

### Expected diagnosis

The buffer may be stale or incomplete after a failed transfer.

### Corrected code

```c
if (read_i2c(buf) != OK) return ERR_BUS;
use(buf);
```

### Regression tests

```c
assert_bus_error_is_propagated();
```

## EC-H-041: work in ISR

- Difficulty: Hard
- Language/platform: Embedded C
- Perspective: Interrupts
- Concept: work in ISR
- Symptom: The device misses deadlines or deadlocks.
- Diagnostic goal: Keep handlers short and defer work.

### Buggy code

```c
void ISR(void) { printf("edge"); read_sensor(); }
```

### Expected diagnosis

I/O, allocation, and slow calls inside an ISR are unsafe and unbounded.

### Corrected code

```c
volatile bool pending; void ISR(void) { pending = true; }
```

### Regression tests

```c
assert_main_loop_services_pending();
```

## EC-H-042: blocking delay

- Difficulty: Hard
- Language/platform: Embedded C
- Perspective: Timing
- Concept: blocking delay
- Symptom: A periodic task drifts.
- Diagnostic goal: Schedule against a monotonic deadline.

### Buggy code

```c
delay_ms(period); task();
```

### Expected diagnosis

Sleeping before work accumulates execution time as drift.

### Corrected code

```c
if (now >= deadline) { task(); deadline += period; }
```

### Regression tests

```c
assert_periodic_deadline_does_not_drift();
```

## EC-H-043: missing volatile

- Difficulty: Hard
- Language/platform: Embedded C
- Perspective: Volatile
- Concept: missing volatile
- Symptom: The main loop never sees a flag change.
- Diagnostic goal: Mark memory changed by hardware or ISR as volatile.

### Buggy code

```c
bool ready = false;
while (!ready) {}
```

### Expected diagnosis

The optimizer may cache a nonvolatile flag in a register.

### Corrected code

```c
volatile bool ready = false;
while (!ready) {}
```

### Regression tests

```c
assert_flag_change_is_observed();
```

## EC-H-044: off-by-one ring buffer

- Difficulty: Hard
- Language/platform: Embedded C
- Perspective: Buffers
- Concept: off-by-one ring buffer
- Symptom: Full and empty states are confused.
- Diagnostic goal: Track count or reserve one slot.

### Buggy code

```c
buffer[head++] = value;
```

### Expected diagnosis

The head wraps without checking capacity and overwrites unread data.

### Corrected code

```c
if (count < CAPACITY) { buffer[head] = value; head = (head + 1) % CAPACITY; count++; }
```

### Regression tests

```c
assert_full_buffer_rejects_new_value();
```

## EC-H-045: heap fragmentation

- Difficulty: Hard
- Language/platform: Embedded C
- Perspective: Memory
- Concept: heap fragmentation
- Symptom: Long uptime causes allocation failure.
- Diagnostic goal: Use fixed storage for bounded messages.

### Buggy code

```c
uint8_t *packet = malloc(length);
```

### Expected diagnosis

Repeated variable allocations fragment a small heap.

### Corrected code

```c
uint8_t packet[MAX_PACKET]; if (length > sizeof packet) return ERR_TOO_LARGE;
```

### Regression tests

```c
assert_oversized_packet_rejected();
```

## EC-H-046: raw units mistaken for volts

- Difficulty: Hard
- Language/platform: Embedded C
- Perspective: ADC
- Concept: raw units mistaken for volts
- Symptom: Control thresholds trigger at the wrong level.
- Diagnostic goal: Calibrate raw codes at the hardware boundary.

### Buggy code

```c
float volts = raw;
```

### Expected diagnosis

An ADC code needs reference voltage and resolution conversion.

### Corrected code

```c
float volts = raw * reference / ((1u << bits) - 1u);
```

### Regression tests

```c
assert_full_scale_equals_reference();
```

## EC-H-047: partial frame

- Difficulty: Hard
- Language/platform: Embedded C
- Perspective: UART
- Concept: partial frame
- Symptom: A split message is parsed as corrupt.
- Diagnostic goal: Accumulate until a complete delimiter/frame exists.

### Buggy code

```c
if (byte == ">") parse(frame);
```

### Expected diagnosis

A terminator may arrive in a later interrupt and a partial frame is discarded.

### Corrected code

```c
if (append(byte)) { if (byte == ">") parse(frame); }
```

### Regression tests

```c
assert_split_frame_reassembles();
```

## EC-H-048: feed before work

- Difficulty: Hard
- Language/platform: Embedded C
- Perspective: Watchdog
- Concept: feed before work
- Symptom: A stuck task keeps the watchdog alive.
- Diagnostic goal: Feed only after essential work succeeds.

### Buggy code

```c
watchdog_feed();
run_control_loop();
```

### Expected diagnosis

The watchdog proves loop entry, not successful progress.

### Corrected code

```c
run_control_loop(); watchdog_feed();
```

### Regression tests

```c
assert_failed_work_does_not_feed();
```

## EC-H-049: busy wait

- Difficulty: Hard
- Language/platform: Embedded C
- Perspective: Power
- Concept: busy wait
- Symptom: Sleep current is too high.
- Diagnostic goal: Use a timer or wake event rather than polling.

### Buggy code

```c
while (!event) { }
```

### Expected diagnosis

The CPU remains active while waiting for hardware.

### Corrected code

```c
sleep_until_event();
```

### Regression tests

```c
assert_wait_enters_low_power();
```

## EC-H-050: unchecked peripheral result

- Difficulty: Hard
- Language/platform: Embedded C
- Perspective: Safety
- Concept: unchecked peripheral result
- Symptom: A bus fault becomes invalid state.
- Diagnostic goal: Check every hardware operation before using output.

### Buggy code

```c
read_i2c(buf);
use(buf);
```

### Expected diagnosis

The buffer may be stale or incomplete after a failed transfer.

### Corrected code

```c
if (read_i2c(buf) != OK) return ERR_BUS;
use(buf);
```

### Regression tests

```c
assert_bus_error_is_propagated();
```

## EC-H-051: work in ISR

- Difficulty: Hard
- Language/platform: Embedded C
- Perspective: Interrupts
- Concept: work in ISR
- Symptom: The device misses deadlines or deadlocks.
- Diagnostic goal: Keep handlers short and defer work.

### Buggy code

```c
void ISR(void) { printf("edge"); read_sensor(); }
```

### Expected diagnosis

I/O, allocation, and slow calls inside an ISR are unsafe and unbounded.

### Corrected code

```c
volatile bool pending; void ISR(void) { pending = true; }
```

### Regression tests

```c
assert_main_loop_services_pending();
```

## EC-H-052: blocking delay

- Difficulty: Hard
- Language/platform: Embedded C
- Perspective: Timing
- Concept: blocking delay
- Symptom: A periodic task drifts.
- Diagnostic goal: Schedule against a monotonic deadline.

### Buggy code

```c
delay_ms(period); task();
```

### Expected diagnosis

Sleeping before work accumulates execution time as drift.

### Corrected code

```c
if (now >= deadline) { task(); deadline += period; }
```

### Regression tests

```c
assert_periodic_deadline_does_not_drift();
```

## EC-H-053: missing volatile

- Difficulty: Hard
- Language/platform: Embedded C
- Perspective: Volatile
- Concept: missing volatile
- Symptom: The main loop never sees a flag change.
- Diagnostic goal: Mark memory changed by hardware or ISR as volatile.

### Buggy code

```c
bool ready = false;
while (!ready) {}
```

### Expected diagnosis

The optimizer may cache a nonvolatile flag in a register.

### Corrected code

```c
volatile bool ready = false;
while (!ready) {}
```

### Regression tests

```c
assert_flag_change_is_observed();
```

## EC-H-054: off-by-one ring buffer

- Difficulty: Hard
- Language/platform: Embedded C
- Perspective: Buffers
- Concept: off-by-one ring buffer
- Symptom: Full and empty states are confused.
- Diagnostic goal: Track count or reserve one slot.

### Buggy code

```c
buffer[head++] = value;
```

### Expected diagnosis

The head wraps without checking capacity and overwrites unread data.

### Corrected code

```c
if (count < CAPACITY) { buffer[head] = value; head = (head + 1) % CAPACITY; count++; }
```

### Regression tests

```c
assert_full_buffer_rejects_new_value();
```

## EC-H-055: heap fragmentation

- Difficulty: Hard
- Language/platform: Embedded C
- Perspective: Memory
- Concept: heap fragmentation
- Symptom: Long uptime causes allocation failure.
- Diagnostic goal: Use fixed storage for bounded messages.

### Buggy code

```c
uint8_t *packet = malloc(length);
```

### Expected diagnosis

Repeated variable allocations fragment a small heap.

### Corrected code

```c
uint8_t packet[MAX_PACKET]; if (length > sizeof packet) return ERR_TOO_LARGE;
```

### Regression tests

```c
assert_oversized_packet_rejected();
```

## EC-H-056: raw units mistaken for volts

- Difficulty: Hard
- Language/platform: Embedded C
- Perspective: ADC
- Concept: raw units mistaken for volts
- Symptom: Control thresholds trigger at the wrong level.
- Diagnostic goal: Calibrate raw codes at the hardware boundary.

### Buggy code

```c
float volts = raw;
```

### Expected diagnosis

An ADC code needs reference voltage and resolution conversion.

### Corrected code

```c
float volts = raw * reference / ((1u << bits) - 1u);
```

### Regression tests

```c
assert_full_scale_equals_reference();
```

## EC-H-057: partial frame

- Difficulty: Hard
- Language/platform: Embedded C
- Perspective: UART
- Concept: partial frame
- Symptom: A split message is parsed as corrupt.
- Diagnostic goal: Accumulate until a complete delimiter/frame exists.

### Buggy code

```c
if (byte == ">") parse(frame);
```

### Expected diagnosis

A terminator may arrive in a later interrupt and a partial frame is discarded.

### Corrected code

```c
if (append(byte)) { if (byte == ">") parse(frame); }
```

### Regression tests

```c
assert_split_frame_reassembles();
```

## EC-H-058: feed before work

- Difficulty: Hard
- Language/platform: Embedded C
- Perspective: Watchdog
- Concept: feed before work
- Symptom: A stuck task keeps the watchdog alive.
- Diagnostic goal: Feed only after essential work succeeds.

### Buggy code

```c
watchdog_feed();
run_control_loop();
```

### Expected diagnosis

The watchdog proves loop entry, not successful progress.

### Corrected code

```c
run_control_loop(); watchdog_feed();
```

### Regression tests

```c
assert_failed_work_does_not_feed();
```

## EC-H-059: busy wait

- Difficulty: Hard
- Language/platform: Embedded C
- Perspective: Power
- Concept: busy wait
- Symptom: Sleep current is too high.
- Diagnostic goal: Use a timer or wake event rather than polling.

### Buggy code

```c
while (!event) { }
```

### Expected diagnosis

The CPU remains active while waiting for hardware.

### Corrected code

```c
sleep_until_event();
```

### Regression tests

```c
assert_wait_enters_low_power();
```

## EC-H-060: unchecked peripheral result

- Difficulty: Hard
- Language/platform: Embedded C
- Perspective: Safety
- Concept: unchecked peripheral result
- Symptom: A bus fault becomes invalid state.
- Diagnostic goal: Check every hardware operation before using output.

### Buggy code

```c
read_i2c(buf);
use(buf);
```

### Expected diagnosis

The buffer may be stale or incomplete after a failed transfer.

### Corrected code

```c
if (read_i2c(buf) != OK) return ERR_BUS;
use(buf);
```

### Regression tests

```c
assert_bus_error_is_propagated();
```

## EC-H-061: work in ISR

- Difficulty: Hard
- Language/platform: Embedded C
- Perspective: Interrupts
- Concept: work in ISR
- Symptom: The device misses deadlines or deadlocks.
- Diagnostic goal: Keep handlers short and defer work.

### Buggy code

```c
void ISR(void) { printf("edge"); read_sensor(); }
```

### Expected diagnosis

I/O, allocation, and slow calls inside an ISR are unsafe and unbounded.

### Corrected code

```c
volatile bool pending; void ISR(void) { pending = true; }
```

### Regression tests

```c
assert_main_loop_services_pending();
```

## EC-H-062: blocking delay

- Difficulty: Hard
- Language/platform: Embedded C
- Perspective: Timing
- Concept: blocking delay
- Symptom: A periodic task drifts.
- Diagnostic goal: Schedule against a monotonic deadline.

### Buggy code

```c
delay_ms(period); task();
```

### Expected diagnosis

Sleeping before work accumulates execution time as drift.

### Corrected code

```c
if (now >= deadline) { task(); deadline += period; }
```

### Regression tests

```c
assert_periodic_deadline_does_not_drift();
```

## EC-H-063: missing volatile

- Difficulty: Hard
- Language/platform: Embedded C
- Perspective: Volatile
- Concept: missing volatile
- Symptom: The main loop never sees a flag change.
- Diagnostic goal: Mark memory changed by hardware or ISR as volatile.

### Buggy code

```c
bool ready = false;
while (!ready) {}
```

### Expected diagnosis

The optimizer may cache a nonvolatile flag in a register.

### Corrected code

```c
volatile bool ready = false;
while (!ready) {}
```

### Regression tests

```c
assert_flag_change_is_observed();
```

## EC-H-064: off-by-one ring buffer

- Difficulty: Hard
- Language/platform: Embedded C
- Perspective: Buffers
- Concept: off-by-one ring buffer
- Symptom: Full and empty states are confused.
- Diagnostic goal: Track count or reserve one slot.

### Buggy code

```c
buffer[head++] = value;
```

### Expected diagnosis

The head wraps without checking capacity and overwrites unread data.

### Corrected code

```c
if (count < CAPACITY) { buffer[head] = value; head = (head + 1) % CAPACITY; count++; }
```

### Regression tests

```c
assert_full_buffer_rejects_new_value();
```

## EC-H-065: heap fragmentation

- Difficulty: Hard
- Language/platform: Embedded C
- Perspective: Memory
- Concept: heap fragmentation
- Symptom: Long uptime causes allocation failure.
- Diagnostic goal: Use fixed storage for bounded messages.

### Buggy code

```c
uint8_t *packet = malloc(length);
```

### Expected diagnosis

Repeated variable allocations fragment a small heap.

### Corrected code

```c
uint8_t packet[MAX_PACKET]; if (length > sizeof packet) return ERR_TOO_LARGE;
```

### Regression tests

```c
assert_oversized_packet_rejected();
```

## EC-H-066: raw units mistaken for volts

- Difficulty: Hard
- Language/platform: Embedded C
- Perspective: ADC
- Concept: raw units mistaken for volts
- Symptom: Control thresholds trigger at the wrong level.
- Diagnostic goal: Calibrate raw codes at the hardware boundary.

### Buggy code

```c
float volts = raw;
```

### Expected diagnosis

An ADC code needs reference voltage and resolution conversion.

### Corrected code

```c
float volts = raw * reference / ((1u << bits) - 1u);
```

### Regression tests

```c
assert_full_scale_equals_reference();
```

## EC-H-067: partial frame

- Difficulty: Hard
- Language/platform: Embedded C
- Perspective: UART
- Concept: partial frame
- Symptom: A split message is parsed as corrupt.
- Diagnostic goal: Accumulate until a complete delimiter/frame exists.

### Buggy code

```c
if (byte == ">") parse(frame);
```

### Expected diagnosis

A terminator may arrive in a later interrupt and a partial frame is discarded.

### Corrected code

```c
if (append(byte)) { if (byte == ">") parse(frame); }
```

### Regression tests

```c
assert_split_frame_reassembles();
```

## EC-H-068: feed before work

- Difficulty: Hard
- Language/platform: Embedded C
- Perspective: Watchdog
- Concept: feed before work
- Symptom: A stuck task keeps the watchdog alive.
- Diagnostic goal: Feed only after essential work succeeds.

### Buggy code

```c
watchdog_feed();
run_control_loop();
```

### Expected diagnosis

The watchdog proves loop entry, not successful progress.

### Corrected code

```c
run_control_loop(); watchdog_feed();
```

### Regression tests

```c
assert_failed_work_does_not_feed();
```

## EC-H-069: busy wait

- Difficulty: Hard
- Language/platform: Embedded C
- Perspective: Power
- Concept: busy wait
- Symptom: Sleep current is too high.
- Diagnostic goal: Use a timer or wake event rather than polling.

### Buggy code

```c
while (!event) { }
```

### Expected diagnosis

The CPU remains active while waiting for hardware.

### Corrected code

```c
sleep_until_event();
```

### Regression tests

```c
assert_wait_enters_low_power();
```

## EC-H-070: unchecked peripheral result

- Difficulty: Hard
- Language/platform: Embedded C
- Perspective: Safety
- Concept: unchecked peripheral result
- Symptom: A bus fault becomes invalid state.
- Diagnostic goal: Check every hardware operation before using output.

### Buggy code

```c
read_i2c(buf);
use(buf);
```

### Expected diagnosis

The buffer may be stale or incomplete after a failed transfer.

### Corrected code

```c
if (read_i2c(buf) != OK) return ERR_BUS;
use(buf);
```

### Regression tests

```c
assert_bus_error_is_propagated();
```

## EC-H-071: work in ISR

- Difficulty: Hard
- Language/platform: Embedded C
- Perspective: Interrupts
- Concept: work in ISR
- Symptom: The device misses deadlines or deadlocks.
- Diagnostic goal: Keep handlers short and defer work.

### Buggy code

```c
void ISR(void) { printf("edge"); read_sensor(); }
```

### Expected diagnosis

I/O, allocation, and slow calls inside an ISR are unsafe and unbounded.

### Corrected code

```c
volatile bool pending; void ISR(void) { pending = true; }
```

### Regression tests

```c
assert_main_loop_services_pending();
```

## EC-H-072: blocking delay

- Difficulty: Hard
- Language/platform: Embedded C
- Perspective: Timing
- Concept: blocking delay
- Symptom: A periodic task drifts.
- Diagnostic goal: Schedule against a monotonic deadline.

### Buggy code

```c
delay_ms(period); task();
```

### Expected diagnosis

Sleeping before work accumulates execution time as drift.

### Corrected code

```c
if (now >= deadline) { task(); deadline += period; }
```

### Regression tests

```c
assert_periodic_deadline_does_not_drift();
```

## EC-H-073: missing volatile

- Difficulty: Hard
- Language/platform: Embedded C
- Perspective: Volatile
- Concept: missing volatile
- Symptom: The main loop never sees a flag change.
- Diagnostic goal: Mark memory changed by hardware or ISR as volatile.

### Buggy code

```c
bool ready = false;
while (!ready) {}
```

### Expected diagnosis

The optimizer may cache a nonvolatile flag in a register.

### Corrected code

```c
volatile bool ready = false;
while (!ready) {}
```

### Regression tests

```c
assert_flag_change_is_observed();
```

## EC-H-074: off-by-one ring buffer

- Difficulty: Hard
- Language/platform: Embedded C
- Perspective: Buffers
- Concept: off-by-one ring buffer
- Symptom: Full and empty states are confused.
- Diagnostic goal: Track count or reserve one slot.

### Buggy code

```c
buffer[head++] = value;
```

### Expected diagnosis

The head wraps without checking capacity and overwrites unread data.

### Corrected code

```c
if (count < CAPACITY) { buffer[head] = value; head = (head + 1) % CAPACITY; count++; }
```

### Regression tests

```c
assert_full_buffer_rejects_new_value();
```

## EC-H-075: heap fragmentation

- Difficulty: Hard
- Language/platform: Embedded C
- Perspective: Memory
- Concept: heap fragmentation
- Symptom: Long uptime causes allocation failure.
- Diagnostic goal: Use fixed storage for bounded messages.

### Buggy code

```c
uint8_t *packet = malloc(length);
```

### Expected diagnosis

Repeated variable allocations fragment a small heap.

### Corrected code

```c
uint8_t packet[MAX_PACKET]; if (length > sizeof packet) return ERR_TOO_LARGE;
```

### Regression tests

```c
assert_oversized_packet_rejected();
```

## EC-H-076: raw units mistaken for volts

- Difficulty: Hard
- Language/platform: Embedded C
- Perspective: ADC
- Concept: raw units mistaken for volts
- Symptom: Control thresholds trigger at the wrong level.
- Diagnostic goal: Calibrate raw codes at the hardware boundary.

### Buggy code

```c
float volts = raw;
```

### Expected diagnosis

An ADC code needs reference voltage and resolution conversion.

### Corrected code

```c
float volts = raw * reference / ((1u << bits) - 1u);
```

### Regression tests

```c
assert_full_scale_equals_reference();
```

## EC-H-077: partial frame

- Difficulty: Hard
- Language/platform: Embedded C
- Perspective: UART
- Concept: partial frame
- Symptom: A split message is parsed as corrupt.
- Diagnostic goal: Accumulate until a complete delimiter/frame exists.

### Buggy code

```c
if (byte == ">") parse(frame);
```

### Expected diagnosis

A terminator may arrive in a later interrupt and a partial frame is discarded.

### Corrected code

```c
if (append(byte)) { if (byte == ">") parse(frame); }
```

### Regression tests

```c
assert_split_frame_reassembles();
```

## EC-H-078: feed before work

- Difficulty: Hard
- Language/platform: Embedded C
- Perspective: Watchdog
- Concept: feed before work
- Symptom: A stuck task keeps the watchdog alive.
- Diagnostic goal: Feed only after essential work succeeds.

### Buggy code

```c
watchdog_feed();
run_control_loop();
```

### Expected diagnosis

The watchdog proves loop entry, not successful progress.

### Corrected code

```c
run_control_loop(); watchdog_feed();
```

### Regression tests

```c
assert_failed_work_does_not_feed();
```

## EC-H-079: busy wait

- Difficulty: Hard
- Language/platform: Embedded C
- Perspective: Power
- Concept: busy wait
- Symptom: Sleep current is too high.
- Diagnostic goal: Use a timer or wake event rather than polling.

### Buggy code

```c
while (!event) { }
```

### Expected diagnosis

The CPU remains active while waiting for hardware.

### Corrected code

```c
sleep_until_event();
```

### Regression tests

```c
assert_wait_enters_low_power();
```

## EC-H-080: unchecked peripheral result

- Difficulty: Hard
- Language/platform: Embedded C
- Perspective: Safety
- Concept: unchecked peripheral result
- Symptom: A bus fault becomes invalid state.
- Diagnostic goal: Check every hardware operation before using output.

### Buggy code

```c
read_i2c(buf);
use(buf);
```

### Expected diagnosis

The buffer may be stale or incomplete after a failed transfer.

### Corrected code

```c
if (read_i2c(buf) != OK) return ERR_BUS;
use(buf);
```

### Regression tests

```c
assert_bus_error_is_propagated();
```

## EC-H-081: work in ISR

- Difficulty: Hard
- Language/platform: Embedded C
- Perspective: Interrupts
- Concept: work in ISR
- Symptom: The device misses deadlines or deadlocks.
- Diagnostic goal: Keep handlers short and defer work.

### Buggy code

```c
void ISR(void) { printf("edge"); read_sensor(); }
```

### Expected diagnosis

I/O, allocation, and slow calls inside an ISR are unsafe and unbounded.

### Corrected code

```c
volatile bool pending; void ISR(void) { pending = true; }
```

### Regression tests

```c
assert_main_loop_services_pending();
```

## EC-H-082: blocking delay

- Difficulty: Hard
- Language/platform: Embedded C
- Perspective: Timing
- Concept: blocking delay
- Symptom: A periodic task drifts.
- Diagnostic goal: Schedule against a monotonic deadline.

### Buggy code

```c
delay_ms(period); task();
```

### Expected diagnosis

Sleeping before work accumulates execution time as drift.

### Corrected code

```c
if (now >= deadline) { task(); deadline += period; }
```

### Regression tests

```c
assert_periodic_deadline_does_not_drift();
```

## EC-H-083: missing volatile

- Difficulty: Hard
- Language/platform: Embedded C
- Perspective: Volatile
- Concept: missing volatile
- Symptom: The main loop never sees a flag change.
- Diagnostic goal: Mark memory changed by hardware or ISR as volatile.

### Buggy code

```c
bool ready = false;
while (!ready) {}
```

### Expected diagnosis

The optimizer may cache a nonvolatile flag in a register.

### Corrected code

```c
volatile bool ready = false;
while (!ready) {}
```

### Regression tests

```c
assert_flag_change_is_observed();
```

## EC-H-084: off-by-one ring buffer

- Difficulty: Hard
- Language/platform: Embedded C
- Perspective: Buffers
- Concept: off-by-one ring buffer
- Symptom: Full and empty states are confused.
- Diagnostic goal: Track count or reserve one slot.

### Buggy code

```c
buffer[head++] = value;
```

### Expected diagnosis

The head wraps without checking capacity and overwrites unread data.

### Corrected code

```c
if (count < CAPACITY) { buffer[head] = value; head = (head + 1) % CAPACITY; count++; }
```

### Regression tests

```c
assert_full_buffer_rejects_new_value();
```

## EC-H-085: heap fragmentation

- Difficulty: Hard
- Language/platform: Embedded C
- Perspective: Memory
- Concept: heap fragmentation
- Symptom: Long uptime causes allocation failure.
- Diagnostic goal: Use fixed storage for bounded messages.

### Buggy code

```c
uint8_t *packet = malloc(length);
```

### Expected diagnosis

Repeated variable allocations fragment a small heap.

### Corrected code

```c
uint8_t packet[MAX_PACKET]; if (length > sizeof packet) return ERR_TOO_LARGE;
```

### Regression tests

```c
assert_oversized_packet_rejected();
```

## EC-H-086: raw units mistaken for volts

- Difficulty: Hard
- Language/platform: Embedded C
- Perspective: ADC
- Concept: raw units mistaken for volts
- Symptom: Control thresholds trigger at the wrong level.
- Diagnostic goal: Calibrate raw codes at the hardware boundary.

### Buggy code

```c
float volts = raw;
```

### Expected diagnosis

An ADC code needs reference voltage and resolution conversion.

### Corrected code

```c
float volts = raw * reference / ((1u << bits) - 1u);
```

### Regression tests

```c
assert_full_scale_equals_reference();
```

## EC-H-087: partial frame

- Difficulty: Hard
- Language/platform: Embedded C
- Perspective: UART
- Concept: partial frame
- Symptom: A split message is parsed as corrupt.
- Diagnostic goal: Accumulate until a complete delimiter/frame exists.

### Buggy code

```c
if (byte == ">") parse(frame);
```

### Expected diagnosis

A terminator may arrive in a later interrupt and a partial frame is discarded.

### Corrected code

```c
if (append(byte)) { if (byte == ">") parse(frame); }
```

### Regression tests

```c
assert_split_frame_reassembles();
```

## EC-H-088: feed before work

- Difficulty: Hard
- Language/platform: Embedded C
- Perspective: Watchdog
- Concept: feed before work
- Symptom: A stuck task keeps the watchdog alive.
- Diagnostic goal: Feed only after essential work succeeds.

### Buggy code

```c
watchdog_feed();
run_control_loop();
```

### Expected diagnosis

The watchdog proves loop entry, not successful progress.

### Corrected code

```c
run_control_loop(); watchdog_feed();
```

### Regression tests

```c
assert_failed_work_does_not_feed();
```

## EC-H-089: busy wait

- Difficulty: Hard
- Language/platform: Embedded C
- Perspective: Power
- Concept: busy wait
- Symptom: Sleep current is too high.
- Diagnostic goal: Use a timer or wake event rather than polling.

### Buggy code

```c
while (!event) { }
```

### Expected diagnosis

The CPU remains active while waiting for hardware.

### Corrected code

```c
sleep_until_event();
```

### Regression tests

```c
assert_wait_enters_low_power();
```

## EC-H-090: unchecked peripheral result

- Difficulty: Hard
- Language/platform: Embedded C
- Perspective: Safety
- Concept: unchecked peripheral result
- Symptom: A bus fault becomes invalid state.
- Diagnostic goal: Check every hardware operation before using output.

### Buggy code

```c
read_i2c(buf);
use(buf);
```

### Expected diagnosis

The buffer may be stale or incomplete after a failed transfer.

### Corrected code

```c
if (read_i2c(buf) != OK) return ERR_BUS;
use(buf);
```

### Regression tests

```c
assert_bus_error_is_propagated();
```

## EC-H-091: work in ISR

- Difficulty: Hard
- Language/platform: Embedded C
- Perspective: Interrupts
- Concept: work in ISR
- Symptom: The device misses deadlines or deadlocks.
- Diagnostic goal: Keep handlers short and defer work.

### Buggy code

```c
void ISR(void) { printf("edge"); read_sensor(); }
```

### Expected diagnosis

I/O, allocation, and slow calls inside an ISR are unsafe and unbounded.

### Corrected code

```c
volatile bool pending; void ISR(void) { pending = true; }
```

### Regression tests

```c
assert_main_loop_services_pending();
```

## EC-H-092: blocking delay

- Difficulty: Hard
- Language/platform: Embedded C
- Perspective: Timing
- Concept: blocking delay
- Symptom: A periodic task drifts.
- Diagnostic goal: Schedule against a monotonic deadline.

### Buggy code

```c
delay_ms(period); task();
```

### Expected diagnosis

Sleeping before work accumulates execution time as drift.

### Corrected code

```c
if (now >= deadline) { task(); deadline += period; }
```

### Regression tests

```c
assert_periodic_deadline_does_not_drift();
```

## EC-H-093: missing volatile

- Difficulty: Hard
- Language/platform: Embedded C
- Perspective: Volatile
- Concept: missing volatile
- Symptom: The main loop never sees a flag change.
- Diagnostic goal: Mark memory changed by hardware or ISR as volatile.

### Buggy code

```c
bool ready = false;
while (!ready) {}
```

### Expected diagnosis

The optimizer may cache a nonvolatile flag in a register.

### Corrected code

```c
volatile bool ready = false;
while (!ready) {}
```

### Regression tests

```c
assert_flag_change_is_observed();
```

## EC-H-094: off-by-one ring buffer

- Difficulty: Hard
- Language/platform: Embedded C
- Perspective: Buffers
- Concept: off-by-one ring buffer
- Symptom: Full and empty states are confused.
- Diagnostic goal: Track count or reserve one slot.

### Buggy code

```c
buffer[head++] = value;
```

### Expected diagnosis

The head wraps without checking capacity and overwrites unread data.

### Corrected code

```c
if (count < CAPACITY) { buffer[head] = value; head = (head + 1) % CAPACITY; count++; }
```

### Regression tests

```c
assert_full_buffer_rejects_new_value();
```

## EC-H-095: heap fragmentation

- Difficulty: Hard
- Language/platform: Embedded C
- Perspective: Memory
- Concept: heap fragmentation
- Symptom: Long uptime causes allocation failure.
- Diagnostic goal: Use fixed storage for bounded messages.

### Buggy code

```c
uint8_t *packet = malloc(length);
```

### Expected diagnosis

Repeated variable allocations fragment a small heap.

### Corrected code

```c
uint8_t packet[MAX_PACKET]; if (length > sizeof packet) return ERR_TOO_LARGE;
```

### Regression tests

```c
assert_oversized_packet_rejected();
```

## EC-H-096: raw units mistaken for volts

- Difficulty: Hard
- Language/platform: Embedded C
- Perspective: ADC
- Concept: raw units mistaken for volts
- Symptom: Control thresholds trigger at the wrong level.
- Diagnostic goal: Calibrate raw codes at the hardware boundary.

### Buggy code

```c
float volts = raw;
```

### Expected diagnosis

An ADC code needs reference voltage and resolution conversion.

### Corrected code

```c
float volts = raw * reference / ((1u << bits) - 1u);
```

### Regression tests

```c
assert_full_scale_equals_reference();
```

## EC-H-097: partial frame

- Difficulty: Hard
- Language/platform: Embedded C
- Perspective: UART
- Concept: partial frame
- Symptom: A split message is parsed as corrupt.
- Diagnostic goal: Accumulate until a complete delimiter/frame exists.

### Buggy code

```c
if (byte == ">") parse(frame);
```

### Expected diagnosis

A terminator may arrive in a later interrupt and a partial frame is discarded.

### Corrected code

```c
if (append(byte)) { if (byte == ">") parse(frame); }
```

### Regression tests

```c
assert_split_frame_reassembles();
```

## EC-H-098: feed before work

- Difficulty: Hard
- Language/platform: Embedded C
- Perspective: Watchdog
- Concept: feed before work
- Symptom: A stuck task keeps the watchdog alive.
- Diagnostic goal: Feed only after essential work succeeds.

### Buggy code

```c
watchdog_feed();
run_control_loop();
```

### Expected diagnosis

The watchdog proves loop entry, not successful progress.

### Corrected code

```c
run_control_loop(); watchdog_feed();
```

### Regression tests

```c
assert_failed_work_does_not_feed();
```

## EC-H-099: busy wait

- Difficulty: Hard
- Language/platform: Embedded C
- Perspective: Power
- Concept: busy wait
- Symptom: Sleep current is too high.
- Diagnostic goal: Use a timer or wake event rather than polling.

### Buggy code

```c
while (!event) { }
```

### Expected diagnosis

The CPU remains active while waiting for hardware.

### Corrected code

```c
sleep_until_event();
```

### Regression tests

```c
assert_wait_enters_low_power();
```

## EC-H-100: unchecked peripheral result

- Difficulty: Hard
- Language/platform: Embedded C
- Perspective: Safety
- Concept: unchecked peripheral result
- Symptom: A bus fault becomes invalid state.
- Diagnostic goal: Check every hardware operation before using output.

### Buggy code

```c
read_i2c(buf);
use(buf);
```

### Expected diagnosis

The buffer may be stale or incomplete after a failed transfer.

### Corrected code

```c
if (read_i2c(buf) != OK) return ERR_BUS;
use(buf);
```

### Regression tests

```c
assert_bus_error_is_propagated();
```
