# Embedded C++ Debug Exercises

A RAG-training corpus of 300 debugging exercises for Embedded C++. Corrected code is editorial training material and must be stripped from learner-facing challenge responses.

## Coverage

- Easy: 100 exercises
- Medium: 100 exercises
- Hard: 100 exercises
- Perspectives: memory, ownership, concurrency, timing, APIs, errors, security, persistence, and testing

## ECPP-E-001: manual peripheral cleanup

- Difficulty: Easy
- Language/platform: Embedded C++
- Perspective: RAII
- Concept: manual peripheral cleanup
- Symptom: An exception leaves a peripheral enabled.
- Diagnostic goal: Bind cleanup to object lifetime.

### Buggy code

```cpp
device.enable();
read();
device.disable();
```

### Expected diagnosis

An exception from read skips disable.

### Corrected code

```cpp
DeviceGuard guard(device);
read();
```

### Regression tests

```cpp
assert_guard_disables_on_exception();
```

## ECPP-E-002: nontrivial ISR object

- Difficulty: Easy
- Language/platform: Embedded C++
- Perspective: Interrupts
- Concept: nontrivial ISR object
- Symptom: The handler allocates or locks.
- Diagnostic goal: Publish a small flag or index only.

### Buggy code

```cpp
void isr() { queue.push(String("edge")); }
```

### Expected diagnosis

Dynamic allocation and locks are unsafe in interrupt context.

### Corrected code

```cpp
volatile uint8_t pending = 1;
```

### Regression tests

```cpp
assert_main_loop_processes_pending();
```

## ECPP-E-003: use moved object

- Difficulty: Easy
- Language/platform: Embedded C++
- Perspective: Move
- Concept: use moved object
- Symptom: The source is assumed to retain resources.
- Diagnostic goal: Use the destination after move or define a valid moved-from state.

### Buggy code

```cpp
auto b = std::move(a); use(a);
```

### Expected diagnosis

Moving transfers ownership and leaves a valid but unspecified source.

### Corrected code

```cpp
auto b = std::move(a); use(b);
```

### Regression tests

```cpp
assert_destination_owns_resource();
```

## ECPP-E-004: dangling view

- Difficulty: Easy
- Language/platform: Embedded C++
- Perspective: Templates
- Concept: dangling view
- Symptom: A view points into a destroyed temporary.
- Diagnostic goal: Return owned storage or extend the source lifetime.

### Buggy code

```cpp
std::string_view name() { return std::string("x"); }
```

### Expected diagnosis

The temporary string dies before the view is used.

### Corrected code

```cpp
std::string name() { return "x"; }
```

### Regression tests

```cpp
assert(name() == "x");
```

## ECPP-E-005: unchecked span length

- Difficulty: Easy
- Language/platform: Embedded C++
- Perspective: Buffers
- Concept: unchecked span length
- Symptom: A peripheral read writes beyond a buffer.
- Diagnostic goal: Pass capacity and validate length before copying.

### Buggy code

```cpp
std::copy(src, src + length, dst.begin());
```

### Expected diagnosis

The source length is not bounded by destination capacity.

### Corrected code

```cpp
if (length > dst.size()) return Error::TooLarge; std::copy_n(src, length, dst.begin());
```

### Regression tests

```cpp
assert_oversized_copy_is_rejected();
```

## ECPP-E-006: data race

- Difficulty: Easy
- Language/platform: Embedded C++
- Perspective: Concurrency
- Concept: data race
- Symptom: A sensor value changes while being read.
- Diagnostic goal: Use an atomic snapshot or lock.

### Buggy code

```cpp
latest = sample;
return latest;
```

### Expected diagnosis

Concurrent read/write of a non-atomic object is undefined behavior.

### Corrected code

```cpp
std::lock_guard lock(mutex); latest = sample;
```

### Regression tests

```cpp
assert_snapshot_is_consistent();
```

## ECPP-E-007: allocation in hot loop

- Difficulty: Easy
- Language/platform: Embedded C++
- Perspective: Timing
- Concept: allocation in hot loop
- Symptom: Control latency has jitter.
- Diagnostic goal: Preallocate and avoid unbounded work in the deadline path.

### Buggy code

```cpp
std::vector<int> values; values.push_back(sample);
```

### Expected diagnosis

Growth may allocate unpredictably during the real-time path.

### Corrected code

```cpp
std::array<int, 64> values; values[count++] = sample;
```

### Regression tests

```cpp
assert_no_allocation_in_control_path();
```

## ECPP-E-008: illegal transition

- Difficulty: Easy
- Language/platform: Embedded C++
- Perspective: State
- Concept: illegal transition
- Symptom: A device enters an unsafe mode.
- Diagnostic goal: Centralize legal state transitions.

### Buggy code

```cpp
state = State::Running;
```

### Expected diagnosis

The assignment ignores the current state and event validity.

### Corrected code

```cpp
if (state == State::Idle && event == Event::Start) state = State::Running; else return Error::InvalidTransition;
```

### Regression tests

```cpp
assert_invalid_transition_rejected();
```

## ECPP-E-009: copying driver handle

- Difficulty: Easy
- Language/platform: Embedded C++
- Perspective: Power
- Concept: copying driver handle
- Symptom: Two objects shut down the same peripheral.
- Diagnostic goal: Make ownership move-only.

### Buggy code

```cpp
Driver a = b;
```

### Expected diagnosis

Copying duplicates exclusive hardware ownership.

### Corrected code

```cpp
Driver a = std::move(b);
```

### Regression tests

```cpp
static_assert(!std::is_copy_constructible_v<Driver>);
```

## ECPP-E-010: ignored expected error

- Difficulty: Easy
- Language/platform: Embedded C++
- Perspective: Fault handling
- Concept: ignored expected error
- Symptom: A disconnected sensor returns stale data.
- Diagnostic goal: Propagate a typed error and choose a safe fallback.

### Buggy code

```cpp
auto value = sensor.read().value();
```

### Expected diagnosis

value() assumes success and can throw or abort.

### Corrected code

```cpp
auto value = sensor.read(); if (!value) return SafeDefault;
```

### Regression tests

```cpp
assert_disconnect_uses_safe_default();
```

## ECPP-E-011: manual peripheral cleanup

- Difficulty: Easy
- Language/platform: Embedded C++
- Perspective: RAII
- Concept: manual peripheral cleanup
- Symptom: An exception leaves a peripheral enabled.
- Diagnostic goal: Bind cleanup to object lifetime.

### Buggy code

```cpp
device.enable();
read();
device.disable();
```

### Expected diagnosis

An exception from read skips disable.

### Corrected code

```cpp
DeviceGuard guard(device);
read();
```

### Regression tests

```cpp
assert_guard_disables_on_exception();
```

## ECPP-E-012: nontrivial ISR object

- Difficulty: Easy
- Language/platform: Embedded C++
- Perspective: Interrupts
- Concept: nontrivial ISR object
- Symptom: The handler allocates or locks.
- Diagnostic goal: Publish a small flag or index only.

### Buggy code

```cpp
void isr() { queue.push(String("edge")); }
```

### Expected diagnosis

Dynamic allocation and locks are unsafe in interrupt context.

### Corrected code

```cpp
volatile uint8_t pending = 1;
```

### Regression tests

```cpp
assert_main_loop_processes_pending();
```

## ECPP-E-013: use moved object

- Difficulty: Easy
- Language/platform: Embedded C++
- Perspective: Move
- Concept: use moved object
- Symptom: The source is assumed to retain resources.
- Diagnostic goal: Use the destination after move or define a valid moved-from state.

### Buggy code

```cpp
auto b = std::move(a); use(a);
```

### Expected diagnosis

Moving transfers ownership and leaves a valid but unspecified source.

### Corrected code

```cpp
auto b = std::move(a); use(b);
```

### Regression tests

```cpp
assert_destination_owns_resource();
```

## ECPP-E-014: dangling view

- Difficulty: Easy
- Language/platform: Embedded C++
- Perspective: Templates
- Concept: dangling view
- Symptom: A view points into a destroyed temporary.
- Diagnostic goal: Return owned storage or extend the source lifetime.

### Buggy code

```cpp
std::string_view name() { return std::string("x"); }
```

### Expected diagnosis

The temporary string dies before the view is used.

### Corrected code

```cpp
std::string name() { return "x"; }
```

### Regression tests

```cpp
assert(name() == "x");
```

## ECPP-E-015: unchecked span length

- Difficulty: Easy
- Language/platform: Embedded C++
- Perspective: Buffers
- Concept: unchecked span length
- Symptom: A peripheral read writes beyond a buffer.
- Diagnostic goal: Pass capacity and validate length before copying.

### Buggy code

```cpp
std::copy(src, src + length, dst.begin());
```

### Expected diagnosis

The source length is not bounded by destination capacity.

### Corrected code

```cpp
if (length > dst.size()) return Error::TooLarge; std::copy_n(src, length, dst.begin());
```

### Regression tests

```cpp
assert_oversized_copy_is_rejected();
```

## ECPP-E-016: data race

- Difficulty: Easy
- Language/platform: Embedded C++
- Perspective: Concurrency
- Concept: data race
- Symptom: A sensor value changes while being read.
- Diagnostic goal: Use an atomic snapshot or lock.

### Buggy code

```cpp
latest = sample;
return latest;
```

### Expected diagnosis

Concurrent read/write of a non-atomic object is undefined behavior.

### Corrected code

```cpp
std::lock_guard lock(mutex); latest = sample;
```

### Regression tests

```cpp
assert_snapshot_is_consistent();
```

## ECPP-E-017: allocation in hot loop

- Difficulty: Easy
- Language/platform: Embedded C++
- Perspective: Timing
- Concept: allocation in hot loop
- Symptom: Control latency has jitter.
- Diagnostic goal: Preallocate and avoid unbounded work in the deadline path.

### Buggy code

```cpp
std::vector<int> values; values.push_back(sample);
```

### Expected diagnosis

Growth may allocate unpredictably during the real-time path.

### Corrected code

```cpp
std::array<int, 64> values; values[count++] = sample;
```

### Regression tests

```cpp
assert_no_allocation_in_control_path();
```

## ECPP-E-018: illegal transition

- Difficulty: Easy
- Language/platform: Embedded C++
- Perspective: State
- Concept: illegal transition
- Symptom: A device enters an unsafe mode.
- Diagnostic goal: Centralize legal state transitions.

### Buggy code

```cpp
state = State::Running;
```

### Expected diagnosis

The assignment ignores the current state and event validity.

### Corrected code

```cpp
if (state == State::Idle && event == Event::Start) state = State::Running; else return Error::InvalidTransition;
```

### Regression tests

```cpp
assert_invalid_transition_rejected();
```

## ECPP-E-019: copying driver handle

- Difficulty: Easy
- Language/platform: Embedded C++
- Perspective: Power
- Concept: copying driver handle
- Symptom: Two objects shut down the same peripheral.
- Diagnostic goal: Make ownership move-only.

### Buggy code

```cpp
Driver a = b;
```

### Expected diagnosis

Copying duplicates exclusive hardware ownership.

### Corrected code

```cpp
Driver a = std::move(b);
```

### Regression tests

```cpp
static_assert(!std::is_copy_constructible_v<Driver>);
```

## ECPP-E-020: ignored expected error

- Difficulty: Easy
- Language/platform: Embedded C++
- Perspective: Fault handling
- Concept: ignored expected error
- Symptom: A disconnected sensor returns stale data.
- Diagnostic goal: Propagate a typed error and choose a safe fallback.

### Buggy code

```cpp
auto value = sensor.read().value();
```

### Expected diagnosis

value() assumes success and can throw or abort.

### Corrected code

```cpp
auto value = sensor.read(); if (!value) return SafeDefault;
```

### Regression tests

```cpp
assert_disconnect_uses_safe_default();
```

## ECPP-E-021: manual peripheral cleanup

- Difficulty: Easy
- Language/platform: Embedded C++
- Perspective: RAII
- Concept: manual peripheral cleanup
- Symptom: An exception leaves a peripheral enabled.
- Diagnostic goal: Bind cleanup to object lifetime.

### Buggy code

```cpp
device.enable();
read();
device.disable();
```

### Expected diagnosis

An exception from read skips disable.

### Corrected code

```cpp
DeviceGuard guard(device);
read();
```

### Regression tests

```cpp
assert_guard_disables_on_exception();
```

## ECPP-E-022: nontrivial ISR object

- Difficulty: Easy
- Language/platform: Embedded C++
- Perspective: Interrupts
- Concept: nontrivial ISR object
- Symptom: The handler allocates or locks.
- Diagnostic goal: Publish a small flag or index only.

### Buggy code

```cpp
void isr() { queue.push(String("edge")); }
```

### Expected diagnosis

Dynamic allocation and locks are unsafe in interrupt context.

### Corrected code

```cpp
volatile uint8_t pending = 1;
```

### Regression tests

```cpp
assert_main_loop_processes_pending();
```

## ECPP-E-023: use moved object

- Difficulty: Easy
- Language/platform: Embedded C++
- Perspective: Move
- Concept: use moved object
- Symptom: The source is assumed to retain resources.
- Diagnostic goal: Use the destination after move or define a valid moved-from state.

### Buggy code

```cpp
auto b = std::move(a); use(a);
```

### Expected diagnosis

Moving transfers ownership and leaves a valid but unspecified source.

### Corrected code

```cpp
auto b = std::move(a); use(b);
```

### Regression tests

```cpp
assert_destination_owns_resource();
```

## ECPP-E-024: dangling view

- Difficulty: Easy
- Language/platform: Embedded C++
- Perspective: Templates
- Concept: dangling view
- Symptom: A view points into a destroyed temporary.
- Diagnostic goal: Return owned storage or extend the source lifetime.

### Buggy code

```cpp
std::string_view name() { return std::string("x"); }
```

### Expected diagnosis

The temporary string dies before the view is used.

### Corrected code

```cpp
std::string name() { return "x"; }
```

### Regression tests

```cpp
assert(name() == "x");
```

## ECPP-E-025: unchecked span length

- Difficulty: Easy
- Language/platform: Embedded C++
- Perspective: Buffers
- Concept: unchecked span length
- Symptom: A peripheral read writes beyond a buffer.
- Diagnostic goal: Pass capacity and validate length before copying.

### Buggy code

```cpp
std::copy(src, src + length, dst.begin());
```

### Expected diagnosis

The source length is not bounded by destination capacity.

### Corrected code

```cpp
if (length > dst.size()) return Error::TooLarge; std::copy_n(src, length, dst.begin());
```

### Regression tests

```cpp
assert_oversized_copy_is_rejected();
```

## ECPP-E-026: data race

- Difficulty: Easy
- Language/platform: Embedded C++
- Perspective: Concurrency
- Concept: data race
- Symptom: A sensor value changes while being read.
- Diagnostic goal: Use an atomic snapshot or lock.

### Buggy code

```cpp
latest = sample;
return latest;
```

### Expected diagnosis

Concurrent read/write of a non-atomic object is undefined behavior.

### Corrected code

```cpp
std::lock_guard lock(mutex); latest = sample;
```

### Regression tests

```cpp
assert_snapshot_is_consistent();
```

## ECPP-E-027: allocation in hot loop

- Difficulty: Easy
- Language/platform: Embedded C++
- Perspective: Timing
- Concept: allocation in hot loop
- Symptom: Control latency has jitter.
- Diagnostic goal: Preallocate and avoid unbounded work in the deadline path.

### Buggy code

```cpp
std::vector<int> values; values.push_back(sample);
```

### Expected diagnosis

Growth may allocate unpredictably during the real-time path.

### Corrected code

```cpp
std::array<int, 64> values; values[count++] = sample;
```

### Regression tests

```cpp
assert_no_allocation_in_control_path();
```

## ECPP-E-028: illegal transition

- Difficulty: Easy
- Language/platform: Embedded C++
- Perspective: State
- Concept: illegal transition
- Symptom: A device enters an unsafe mode.
- Diagnostic goal: Centralize legal state transitions.

### Buggy code

```cpp
state = State::Running;
```

### Expected diagnosis

The assignment ignores the current state and event validity.

### Corrected code

```cpp
if (state == State::Idle && event == Event::Start) state = State::Running; else return Error::InvalidTransition;
```

### Regression tests

```cpp
assert_invalid_transition_rejected();
```

## ECPP-E-029: copying driver handle

- Difficulty: Easy
- Language/platform: Embedded C++
- Perspective: Power
- Concept: copying driver handle
- Symptom: Two objects shut down the same peripheral.
- Diagnostic goal: Make ownership move-only.

### Buggy code

```cpp
Driver a = b;
```

### Expected diagnosis

Copying duplicates exclusive hardware ownership.

### Corrected code

```cpp
Driver a = std::move(b);
```

### Regression tests

```cpp
static_assert(!std::is_copy_constructible_v<Driver>);
```

## ECPP-E-030: ignored expected error

- Difficulty: Easy
- Language/platform: Embedded C++
- Perspective: Fault handling
- Concept: ignored expected error
- Symptom: A disconnected sensor returns stale data.
- Diagnostic goal: Propagate a typed error and choose a safe fallback.

### Buggy code

```cpp
auto value = sensor.read().value();
```

### Expected diagnosis

value() assumes success and can throw or abort.

### Corrected code

```cpp
auto value = sensor.read(); if (!value) return SafeDefault;
```

### Regression tests

```cpp
assert_disconnect_uses_safe_default();
```

## ECPP-E-031: manual peripheral cleanup

- Difficulty: Easy
- Language/platform: Embedded C++
- Perspective: RAII
- Concept: manual peripheral cleanup
- Symptom: An exception leaves a peripheral enabled.
- Diagnostic goal: Bind cleanup to object lifetime.

### Buggy code

```cpp
device.enable();
read();
device.disable();
```

### Expected diagnosis

An exception from read skips disable.

### Corrected code

```cpp
DeviceGuard guard(device);
read();
```

### Regression tests

```cpp
assert_guard_disables_on_exception();
```

## ECPP-E-032: nontrivial ISR object

- Difficulty: Easy
- Language/platform: Embedded C++
- Perspective: Interrupts
- Concept: nontrivial ISR object
- Symptom: The handler allocates or locks.
- Diagnostic goal: Publish a small flag or index only.

### Buggy code

```cpp
void isr() { queue.push(String("edge")); }
```

### Expected diagnosis

Dynamic allocation and locks are unsafe in interrupt context.

### Corrected code

```cpp
volatile uint8_t pending = 1;
```

### Regression tests

```cpp
assert_main_loop_processes_pending();
```

## ECPP-E-033: use moved object

- Difficulty: Easy
- Language/platform: Embedded C++
- Perspective: Move
- Concept: use moved object
- Symptom: The source is assumed to retain resources.
- Diagnostic goal: Use the destination after move or define a valid moved-from state.

### Buggy code

```cpp
auto b = std::move(a); use(a);
```

### Expected diagnosis

Moving transfers ownership and leaves a valid but unspecified source.

### Corrected code

```cpp
auto b = std::move(a); use(b);
```

### Regression tests

```cpp
assert_destination_owns_resource();
```

## ECPP-E-034: dangling view

- Difficulty: Easy
- Language/platform: Embedded C++
- Perspective: Templates
- Concept: dangling view
- Symptom: A view points into a destroyed temporary.
- Diagnostic goal: Return owned storage or extend the source lifetime.

### Buggy code

```cpp
std::string_view name() { return std::string("x"); }
```

### Expected diagnosis

The temporary string dies before the view is used.

### Corrected code

```cpp
std::string name() { return "x"; }
```

### Regression tests

```cpp
assert(name() == "x");
```

## ECPP-E-035: unchecked span length

- Difficulty: Easy
- Language/platform: Embedded C++
- Perspective: Buffers
- Concept: unchecked span length
- Symptom: A peripheral read writes beyond a buffer.
- Diagnostic goal: Pass capacity and validate length before copying.

### Buggy code

```cpp
std::copy(src, src + length, dst.begin());
```

### Expected diagnosis

The source length is not bounded by destination capacity.

### Corrected code

```cpp
if (length > dst.size()) return Error::TooLarge; std::copy_n(src, length, dst.begin());
```

### Regression tests

```cpp
assert_oversized_copy_is_rejected();
```

## ECPP-E-036: data race

- Difficulty: Easy
- Language/platform: Embedded C++
- Perspective: Concurrency
- Concept: data race
- Symptom: A sensor value changes while being read.
- Diagnostic goal: Use an atomic snapshot or lock.

### Buggy code

```cpp
latest = sample;
return latest;
```

### Expected diagnosis

Concurrent read/write of a non-atomic object is undefined behavior.

### Corrected code

```cpp
std::lock_guard lock(mutex); latest = sample;
```

### Regression tests

```cpp
assert_snapshot_is_consistent();
```

## ECPP-E-037: allocation in hot loop

- Difficulty: Easy
- Language/platform: Embedded C++
- Perspective: Timing
- Concept: allocation in hot loop
- Symptom: Control latency has jitter.
- Diagnostic goal: Preallocate and avoid unbounded work in the deadline path.

### Buggy code

```cpp
std::vector<int> values; values.push_back(sample);
```

### Expected diagnosis

Growth may allocate unpredictably during the real-time path.

### Corrected code

```cpp
std::array<int, 64> values; values[count++] = sample;
```

### Regression tests

```cpp
assert_no_allocation_in_control_path();
```

## ECPP-E-038: illegal transition

- Difficulty: Easy
- Language/platform: Embedded C++
- Perspective: State
- Concept: illegal transition
- Symptom: A device enters an unsafe mode.
- Diagnostic goal: Centralize legal state transitions.

### Buggy code

```cpp
state = State::Running;
```

### Expected diagnosis

The assignment ignores the current state and event validity.

### Corrected code

```cpp
if (state == State::Idle && event == Event::Start) state = State::Running; else return Error::InvalidTransition;
```

### Regression tests

```cpp
assert_invalid_transition_rejected();
```

## ECPP-E-039: copying driver handle

- Difficulty: Easy
- Language/platform: Embedded C++
- Perspective: Power
- Concept: copying driver handle
- Symptom: Two objects shut down the same peripheral.
- Diagnostic goal: Make ownership move-only.

### Buggy code

```cpp
Driver a = b;
```

### Expected diagnosis

Copying duplicates exclusive hardware ownership.

### Corrected code

```cpp
Driver a = std::move(b);
```

### Regression tests

```cpp
static_assert(!std::is_copy_constructible_v<Driver>);
```

## ECPP-E-040: ignored expected error

- Difficulty: Easy
- Language/platform: Embedded C++
- Perspective: Fault handling
- Concept: ignored expected error
- Symptom: A disconnected sensor returns stale data.
- Diagnostic goal: Propagate a typed error and choose a safe fallback.

### Buggy code

```cpp
auto value = sensor.read().value();
```

### Expected diagnosis

value() assumes success and can throw or abort.

### Corrected code

```cpp
auto value = sensor.read(); if (!value) return SafeDefault;
```

### Regression tests

```cpp
assert_disconnect_uses_safe_default();
```

## ECPP-E-041: manual peripheral cleanup

- Difficulty: Easy
- Language/platform: Embedded C++
- Perspective: RAII
- Concept: manual peripheral cleanup
- Symptom: An exception leaves a peripheral enabled.
- Diagnostic goal: Bind cleanup to object lifetime.

### Buggy code

```cpp
device.enable();
read();
device.disable();
```

### Expected diagnosis

An exception from read skips disable.

### Corrected code

```cpp
DeviceGuard guard(device);
read();
```

### Regression tests

```cpp
assert_guard_disables_on_exception();
```

## ECPP-E-042: nontrivial ISR object

- Difficulty: Easy
- Language/platform: Embedded C++
- Perspective: Interrupts
- Concept: nontrivial ISR object
- Symptom: The handler allocates or locks.
- Diagnostic goal: Publish a small flag or index only.

### Buggy code

```cpp
void isr() { queue.push(String("edge")); }
```

### Expected diagnosis

Dynamic allocation and locks are unsafe in interrupt context.

### Corrected code

```cpp
volatile uint8_t pending = 1;
```

### Regression tests

```cpp
assert_main_loop_processes_pending();
```

## ECPP-E-043: use moved object

- Difficulty: Easy
- Language/platform: Embedded C++
- Perspective: Move
- Concept: use moved object
- Symptom: The source is assumed to retain resources.
- Diagnostic goal: Use the destination after move or define a valid moved-from state.

### Buggy code

```cpp
auto b = std::move(a); use(a);
```

### Expected diagnosis

Moving transfers ownership and leaves a valid but unspecified source.

### Corrected code

```cpp
auto b = std::move(a); use(b);
```

### Regression tests

```cpp
assert_destination_owns_resource();
```

## ECPP-E-044: dangling view

- Difficulty: Easy
- Language/platform: Embedded C++
- Perspective: Templates
- Concept: dangling view
- Symptom: A view points into a destroyed temporary.
- Diagnostic goal: Return owned storage or extend the source lifetime.

### Buggy code

```cpp
std::string_view name() { return std::string("x"); }
```

### Expected diagnosis

The temporary string dies before the view is used.

### Corrected code

```cpp
std::string name() { return "x"; }
```

### Regression tests

```cpp
assert(name() == "x");
```

## ECPP-E-045: unchecked span length

- Difficulty: Easy
- Language/platform: Embedded C++
- Perspective: Buffers
- Concept: unchecked span length
- Symptom: A peripheral read writes beyond a buffer.
- Diagnostic goal: Pass capacity and validate length before copying.

### Buggy code

```cpp
std::copy(src, src + length, dst.begin());
```

### Expected diagnosis

The source length is not bounded by destination capacity.

### Corrected code

```cpp
if (length > dst.size()) return Error::TooLarge; std::copy_n(src, length, dst.begin());
```

### Regression tests

```cpp
assert_oversized_copy_is_rejected();
```

## ECPP-E-046: data race

- Difficulty: Easy
- Language/platform: Embedded C++
- Perspective: Concurrency
- Concept: data race
- Symptom: A sensor value changes while being read.
- Diagnostic goal: Use an atomic snapshot or lock.

### Buggy code

```cpp
latest = sample;
return latest;
```

### Expected diagnosis

Concurrent read/write of a non-atomic object is undefined behavior.

### Corrected code

```cpp
std::lock_guard lock(mutex); latest = sample;
```

### Regression tests

```cpp
assert_snapshot_is_consistent();
```

## ECPP-E-047: allocation in hot loop

- Difficulty: Easy
- Language/platform: Embedded C++
- Perspective: Timing
- Concept: allocation in hot loop
- Symptom: Control latency has jitter.
- Diagnostic goal: Preallocate and avoid unbounded work in the deadline path.

### Buggy code

```cpp
std::vector<int> values; values.push_back(sample);
```

### Expected diagnosis

Growth may allocate unpredictably during the real-time path.

### Corrected code

```cpp
std::array<int, 64> values; values[count++] = sample;
```

### Regression tests

```cpp
assert_no_allocation_in_control_path();
```

## ECPP-E-048: illegal transition

- Difficulty: Easy
- Language/platform: Embedded C++
- Perspective: State
- Concept: illegal transition
- Symptom: A device enters an unsafe mode.
- Diagnostic goal: Centralize legal state transitions.

### Buggy code

```cpp
state = State::Running;
```

### Expected diagnosis

The assignment ignores the current state and event validity.

### Corrected code

```cpp
if (state == State::Idle && event == Event::Start) state = State::Running; else return Error::InvalidTransition;
```

### Regression tests

```cpp
assert_invalid_transition_rejected();
```

## ECPP-E-049: copying driver handle

- Difficulty: Easy
- Language/platform: Embedded C++
- Perspective: Power
- Concept: copying driver handle
- Symptom: Two objects shut down the same peripheral.
- Diagnostic goal: Make ownership move-only.

### Buggy code

```cpp
Driver a = b;
```

### Expected diagnosis

Copying duplicates exclusive hardware ownership.

### Corrected code

```cpp
Driver a = std::move(b);
```

### Regression tests

```cpp
static_assert(!std::is_copy_constructible_v<Driver>);
```

## ECPP-E-050: ignored expected error

- Difficulty: Easy
- Language/platform: Embedded C++
- Perspective: Fault handling
- Concept: ignored expected error
- Symptom: A disconnected sensor returns stale data.
- Diagnostic goal: Propagate a typed error and choose a safe fallback.

### Buggy code

```cpp
auto value = sensor.read().value();
```

### Expected diagnosis

value() assumes success and can throw or abort.

### Corrected code

```cpp
auto value = sensor.read(); if (!value) return SafeDefault;
```

### Regression tests

```cpp
assert_disconnect_uses_safe_default();
```

## ECPP-E-051: manual peripheral cleanup

- Difficulty: Easy
- Language/platform: Embedded C++
- Perspective: RAII
- Concept: manual peripheral cleanup
- Symptom: An exception leaves a peripheral enabled.
- Diagnostic goal: Bind cleanup to object lifetime.

### Buggy code

```cpp
device.enable();
read();
device.disable();
```

### Expected diagnosis

An exception from read skips disable.

### Corrected code

```cpp
DeviceGuard guard(device);
read();
```

### Regression tests

```cpp
assert_guard_disables_on_exception();
```

## ECPP-E-052: nontrivial ISR object

- Difficulty: Easy
- Language/platform: Embedded C++
- Perspective: Interrupts
- Concept: nontrivial ISR object
- Symptom: The handler allocates or locks.
- Diagnostic goal: Publish a small flag or index only.

### Buggy code

```cpp
void isr() { queue.push(String("edge")); }
```

### Expected diagnosis

Dynamic allocation and locks are unsafe in interrupt context.

### Corrected code

```cpp
volatile uint8_t pending = 1;
```

### Regression tests

```cpp
assert_main_loop_processes_pending();
```

## ECPP-E-053: use moved object

- Difficulty: Easy
- Language/platform: Embedded C++
- Perspective: Move
- Concept: use moved object
- Symptom: The source is assumed to retain resources.
- Diagnostic goal: Use the destination after move or define a valid moved-from state.

### Buggy code

```cpp
auto b = std::move(a); use(a);
```

### Expected diagnosis

Moving transfers ownership and leaves a valid but unspecified source.

### Corrected code

```cpp
auto b = std::move(a); use(b);
```

### Regression tests

```cpp
assert_destination_owns_resource();
```

## ECPP-E-054: dangling view

- Difficulty: Easy
- Language/platform: Embedded C++
- Perspective: Templates
- Concept: dangling view
- Symptom: A view points into a destroyed temporary.
- Diagnostic goal: Return owned storage or extend the source lifetime.

### Buggy code

```cpp
std::string_view name() { return std::string("x"); }
```

### Expected diagnosis

The temporary string dies before the view is used.

### Corrected code

```cpp
std::string name() { return "x"; }
```

### Regression tests

```cpp
assert(name() == "x");
```

## ECPP-E-055: unchecked span length

- Difficulty: Easy
- Language/platform: Embedded C++
- Perspective: Buffers
- Concept: unchecked span length
- Symptom: A peripheral read writes beyond a buffer.
- Diagnostic goal: Pass capacity and validate length before copying.

### Buggy code

```cpp
std::copy(src, src + length, dst.begin());
```

### Expected diagnosis

The source length is not bounded by destination capacity.

### Corrected code

```cpp
if (length > dst.size()) return Error::TooLarge; std::copy_n(src, length, dst.begin());
```

### Regression tests

```cpp
assert_oversized_copy_is_rejected();
```

## ECPP-E-056: data race

- Difficulty: Easy
- Language/platform: Embedded C++
- Perspective: Concurrency
- Concept: data race
- Symptom: A sensor value changes while being read.
- Diagnostic goal: Use an atomic snapshot or lock.

### Buggy code

```cpp
latest = sample;
return latest;
```

### Expected diagnosis

Concurrent read/write of a non-atomic object is undefined behavior.

### Corrected code

```cpp
std::lock_guard lock(mutex); latest = sample;
```

### Regression tests

```cpp
assert_snapshot_is_consistent();
```

## ECPP-E-057: allocation in hot loop

- Difficulty: Easy
- Language/platform: Embedded C++
- Perspective: Timing
- Concept: allocation in hot loop
- Symptom: Control latency has jitter.
- Diagnostic goal: Preallocate and avoid unbounded work in the deadline path.

### Buggy code

```cpp
std::vector<int> values; values.push_back(sample);
```

### Expected diagnosis

Growth may allocate unpredictably during the real-time path.

### Corrected code

```cpp
std::array<int, 64> values; values[count++] = sample;
```

### Regression tests

```cpp
assert_no_allocation_in_control_path();
```

## ECPP-E-058: illegal transition

- Difficulty: Easy
- Language/platform: Embedded C++
- Perspective: State
- Concept: illegal transition
- Symptom: A device enters an unsafe mode.
- Diagnostic goal: Centralize legal state transitions.

### Buggy code

```cpp
state = State::Running;
```

### Expected diagnosis

The assignment ignores the current state and event validity.

### Corrected code

```cpp
if (state == State::Idle && event == Event::Start) state = State::Running; else return Error::InvalidTransition;
```

### Regression tests

```cpp
assert_invalid_transition_rejected();
```

## ECPP-E-059: copying driver handle

- Difficulty: Easy
- Language/platform: Embedded C++
- Perspective: Power
- Concept: copying driver handle
- Symptom: Two objects shut down the same peripheral.
- Diagnostic goal: Make ownership move-only.

### Buggy code

```cpp
Driver a = b;
```

### Expected diagnosis

Copying duplicates exclusive hardware ownership.

### Corrected code

```cpp
Driver a = std::move(b);
```

### Regression tests

```cpp
static_assert(!std::is_copy_constructible_v<Driver>);
```

## ECPP-E-060: ignored expected error

- Difficulty: Easy
- Language/platform: Embedded C++
- Perspective: Fault handling
- Concept: ignored expected error
- Symptom: A disconnected sensor returns stale data.
- Diagnostic goal: Propagate a typed error and choose a safe fallback.

### Buggy code

```cpp
auto value = sensor.read().value();
```

### Expected diagnosis

value() assumes success and can throw or abort.

### Corrected code

```cpp
auto value = sensor.read(); if (!value) return SafeDefault;
```

### Regression tests

```cpp
assert_disconnect_uses_safe_default();
```

## ECPP-E-061: manual peripheral cleanup

- Difficulty: Easy
- Language/platform: Embedded C++
- Perspective: RAII
- Concept: manual peripheral cleanup
- Symptom: An exception leaves a peripheral enabled.
- Diagnostic goal: Bind cleanup to object lifetime.

### Buggy code

```cpp
device.enable();
read();
device.disable();
```

### Expected diagnosis

An exception from read skips disable.

### Corrected code

```cpp
DeviceGuard guard(device);
read();
```

### Regression tests

```cpp
assert_guard_disables_on_exception();
```

## ECPP-E-062: nontrivial ISR object

- Difficulty: Easy
- Language/platform: Embedded C++
- Perspective: Interrupts
- Concept: nontrivial ISR object
- Symptom: The handler allocates or locks.
- Diagnostic goal: Publish a small flag or index only.

### Buggy code

```cpp
void isr() { queue.push(String("edge")); }
```

### Expected diagnosis

Dynamic allocation and locks are unsafe in interrupt context.

### Corrected code

```cpp
volatile uint8_t pending = 1;
```

### Regression tests

```cpp
assert_main_loop_processes_pending();
```

## ECPP-E-063: use moved object

- Difficulty: Easy
- Language/platform: Embedded C++
- Perspective: Move
- Concept: use moved object
- Symptom: The source is assumed to retain resources.
- Diagnostic goal: Use the destination after move or define a valid moved-from state.

### Buggy code

```cpp
auto b = std::move(a); use(a);
```

### Expected diagnosis

Moving transfers ownership and leaves a valid but unspecified source.

### Corrected code

```cpp
auto b = std::move(a); use(b);
```

### Regression tests

```cpp
assert_destination_owns_resource();
```

## ECPP-E-064: dangling view

- Difficulty: Easy
- Language/platform: Embedded C++
- Perspective: Templates
- Concept: dangling view
- Symptom: A view points into a destroyed temporary.
- Diagnostic goal: Return owned storage or extend the source lifetime.

### Buggy code

```cpp
std::string_view name() { return std::string("x"); }
```

### Expected diagnosis

The temporary string dies before the view is used.

### Corrected code

```cpp
std::string name() { return "x"; }
```

### Regression tests

```cpp
assert(name() == "x");
```

## ECPP-E-065: unchecked span length

- Difficulty: Easy
- Language/platform: Embedded C++
- Perspective: Buffers
- Concept: unchecked span length
- Symptom: A peripheral read writes beyond a buffer.
- Diagnostic goal: Pass capacity and validate length before copying.

### Buggy code

```cpp
std::copy(src, src + length, dst.begin());
```

### Expected diagnosis

The source length is not bounded by destination capacity.

### Corrected code

```cpp
if (length > dst.size()) return Error::TooLarge; std::copy_n(src, length, dst.begin());
```

### Regression tests

```cpp
assert_oversized_copy_is_rejected();
```

## ECPP-E-066: data race

- Difficulty: Easy
- Language/platform: Embedded C++
- Perspective: Concurrency
- Concept: data race
- Symptom: A sensor value changes while being read.
- Diagnostic goal: Use an atomic snapshot or lock.

### Buggy code

```cpp
latest = sample;
return latest;
```

### Expected diagnosis

Concurrent read/write of a non-atomic object is undefined behavior.

### Corrected code

```cpp
std::lock_guard lock(mutex); latest = sample;
```

### Regression tests

```cpp
assert_snapshot_is_consistent();
```

## ECPP-E-067: allocation in hot loop

- Difficulty: Easy
- Language/platform: Embedded C++
- Perspective: Timing
- Concept: allocation in hot loop
- Symptom: Control latency has jitter.
- Diagnostic goal: Preallocate and avoid unbounded work in the deadline path.

### Buggy code

```cpp
std::vector<int> values; values.push_back(sample);
```

### Expected diagnosis

Growth may allocate unpredictably during the real-time path.

### Corrected code

```cpp
std::array<int, 64> values; values[count++] = sample;
```

### Regression tests

```cpp
assert_no_allocation_in_control_path();
```

## ECPP-E-068: illegal transition

- Difficulty: Easy
- Language/platform: Embedded C++
- Perspective: State
- Concept: illegal transition
- Symptom: A device enters an unsafe mode.
- Diagnostic goal: Centralize legal state transitions.

### Buggy code

```cpp
state = State::Running;
```

### Expected diagnosis

The assignment ignores the current state and event validity.

### Corrected code

```cpp
if (state == State::Idle && event == Event::Start) state = State::Running; else return Error::InvalidTransition;
```

### Regression tests

```cpp
assert_invalid_transition_rejected();
```

## ECPP-E-069: copying driver handle

- Difficulty: Easy
- Language/platform: Embedded C++
- Perspective: Power
- Concept: copying driver handle
- Symptom: Two objects shut down the same peripheral.
- Diagnostic goal: Make ownership move-only.

### Buggy code

```cpp
Driver a = b;
```

### Expected diagnosis

Copying duplicates exclusive hardware ownership.

### Corrected code

```cpp
Driver a = std::move(b);
```

### Regression tests

```cpp
static_assert(!std::is_copy_constructible_v<Driver>);
```

## ECPP-E-070: ignored expected error

- Difficulty: Easy
- Language/platform: Embedded C++
- Perspective: Fault handling
- Concept: ignored expected error
- Symptom: A disconnected sensor returns stale data.
- Diagnostic goal: Propagate a typed error and choose a safe fallback.

### Buggy code

```cpp
auto value = sensor.read().value();
```

### Expected diagnosis

value() assumes success and can throw or abort.

### Corrected code

```cpp
auto value = sensor.read(); if (!value) return SafeDefault;
```

### Regression tests

```cpp
assert_disconnect_uses_safe_default();
```

## ECPP-E-071: manual peripheral cleanup

- Difficulty: Easy
- Language/platform: Embedded C++
- Perspective: RAII
- Concept: manual peripheral cleanup
- Symptom: An exception leaves a peripheral enabled.
- Diagnostic goal: Bind cleanup to object lifetime.

### Buggy code

```cpp
device.enable();
read();
device.disable();
```

### Expected diagnosis

An exception from read skips disable.

### Corrected code

```cpp
DeviceGuard guard(device);
read();
```

### Regression tests

```cpp
assert_guard_disables_on_exception();
```

## ECPP-E-072: nontrivial ISR object

- Difficulty: Easy
- Language/platform: Embedded C++
- Perspective: Interrupts
- Concept: nontrivial ISR object
- Symptom: The handler allocates or locks.
- Diagnostic goal: Publish a small flag or index only.

### Buggy code

```cpp
void isr() { queue.push(String("edge")); }
```

### Expected diagnosis

Dynamic allocation and locks are unsafe in interrupt context.

### Corrected code

```cpp
volatile uint8_t pending = 1;
```

### Regression tests

```cpp
assert_main_loop_processes_pending();
```

## ECPP-E-073: use moved object

- Difficulty: Easy
- Language/platform: Embedded C++
- Perspective: Move
- Concept: use moved object
- Symptom: The source is assumed to retain resources.
- Diagnostic goal: Use the destination after move or define a valid moved-from state.

### Buggy code

```cpp
auto b = std::move(a); use(a);
```

### Expected diagnosis

Moving transfers ownership and leaves a valid but unspecified source.

### Corrected code

```cpp
auto b = std::move(a); use(b);
```

### Regression tests

```cpp
assert_destination_owns_resource();
```

## ECPP-E-074: dangling view

- Difficulty: Easy
- Language/platform: Embedded C++
- Perspective: Templates
- Concept: dangling view
- Symptom: A view points into a destroyed temporary.
- Diagnostic goal: Return owned storage or extend the source lifetime.

### Buggy code

```cpp
std::string_view name() { return std::string("x"); }
```

### Expected diagnosis

The temporary string dies before the view is used.

### Corrected code

```cpp
std::string name() { return "x"; }
```

### Regression tests

```cpp
assert(name() == "x");
```

## ECPP-E-075: unchecked span length

- Difficulty: Easy
- Language/platform: Embedded C++
- Perspective: Buffers
- Concept: unchecked span length
- Symptom: A peripheral read writes beyond a buffer.
- Diagnostic goal: Pass capacity and validate length before copying.

### Buggy code

```cpp
std::copy(src, src + length, dst.begin());
```

### Expected diagnosis

The source length is not bounded by destination capacity.

### Corrected code

```cpp
if (length > dst.size()) return Error::TooLarge; std::copy_n(src, length, dst.begin());
```

### Regression tests

```cpp
assert_oversized_copy_is_rejected();
```

## ECPP-E-076: data race

- Difficulty: Easy
- Language/platform: Embedded C++
- Perspective: Concurrency
- Concept: data race
- Symptom: A sensor value changes while being read.
- Diagnostic goal: Use an atomic snapshot or lock.

### Buggy code

```cpp
latest = sample;
return latest;
```

### Expected diagnosis

Concurrent read/write of a non-atomic object is undefined behavior.

### Corrected code

```cpp
std::lock_guard lock(mutex); latest = sample;
```

### Regression tests

```cpp
assert_snapshot_is_consistent();
```

## ECPP-E-077: allocation in hot loop

- Difficulty: Easy
- Language/platform: Embedded C++
- Perspective: Timing
- Concept: allocation in hot loop
- Symptom: Control latency has jitter.
- Diagnostic goal: Preallocate and avoid unbounded work in the deadline path.

### Buggy code

```cpp
std::vector<int> values; values.push_back(sample);
```

### Expected diagnosis

Growth may allocate unpredictably during the real-time path.

### Corrected code

```cpp
std::array<int, 64> values; values[count++] = sample;
```

### Regression tests

```cpp
assert_no_allocation_in_control_path();
```

## ECPP-E-078: illegal transition

- Difficulty: Easy
- Language/platform: Embedded C++
- Perspective: State
- Concept: illegal transition
- Symptom: A device enters an unsafe mode.
- Diagnostic goal: Centralize legal state transitions.

### Buggy code

```cpp
state = State::Running;
```

### Expected diagnosis

The assignment ignores the current state and event validity.

### Corrected code

```cpp
if (state == State::Idle && event == Event::Start) state = State::Running; else return Error::InvalidTransition;
```

### Regression tests

```cpp
assert_invalid_transition_rejected();
```

## ECPP-E-079: copying driver handle

- Difficulty: Easy
- Language/platform: Embedded C++
- Perspective: Power
- Concept: copying driver handle
- Symptom: Two objects shut down the same peripheral.
- Diagnostic goal: Make ownership move-only.

### Buggy code

```cpp
Driver a = b;
```

### Expected diagnosis

Copying duplicates exclusive hardware ownership.

### Corrected code

```cpp
Driver a = std::move(b);
```

### Regression tests

```cpp
static_assert(!std::is_copy_constructible_v<Driver>);
```

## ECPP-E-080: ignored expected error

- Difficulty: Easy
- Language/platform: Embedded C++
- Perspective: Fault handling
- Concept: ignored expected error
- Symptom: A disconnected sensor returns stale data.
- Diagnostic goal: Propagate a typed error and choose a safe fallback.

### Buggy code

```cpp
auto value = sensor.read().value();
```

### Expected diagnosis

value() assumes success and can throw or abort.

### Corrected code

```cpp
auto value = sensor.read(); if (!value) return SafeDefault;
```

### Regression tests

```cpp
assert_disconnect_uses_safe_default();
```

## ECPP-E-081: manual peripheral cleanup

- Difficulty: Easy
- Language/platform: Embedded C++
- Perspective: RAII
- Concept: manual peripheral cleanup
- Symptom: An exception leaves a peripheral enabled.
- Diagnostic goal: Bind cleanup to object lifetime.

### Buggy code

```cpp
device.enable();
read();
device.disable();
```

### Expected diagnosis

An exception from read skips disable.

### Corrected code

```cpp
DeviceGuard guard(device);
read();
```

### Regression tests

```cpp
assert_guard_disables_on_exception();
```

## ECPP-E-082: nontrivial ISR object

- Difficulty: Easy
- Language/platform: Embedded C++
- Perspective: Interrupts
- Concept: nontrivial ISR object
- Symptom: The handler allocates or locks.
- Diagnostic goal: Publish a small flag or index only.

### Buggy code

```cpp
void isr() { queue.push(String("edge")); }
```

### Expected diagnosis

Dynamic allocation and locks are unsafe in interrupt context.

### Corrected code

```cpp
volatile uint8_t pending = 1;
```

### Regression tests

```cpp
assert_main_loop_processes_pending();
```

## ECPP-E-083: use moved object

- Difficulty: Easy
- Language/platform: Embedded C++
- Perspective: Move
- Concept: use moved object
- Symptom: The source is assumed to retain resources.
- Diagnostic goal: Use the destination after move or define a valid moved-from state.

### Buggy code

```cpp
auto b = std::move(a); use(a);
```

### Expected diagnosis

Moving transfers ownership and leaves a valid but unspecified source.

### Corrected code

```cpp
auto b = std::move(a); use(b);
```

### Regression tests

```cpp
assert_destination_owns_resource();
```

## ECPP-E-084: dangling view

- Difficulty: Easy
- Language/platform: Embedded C++
- Perspective: Templates
- Concept: dangling view
- Symptom: A view points into a destroyed temporary.
- Diagnostic goal: Return owned storage or extend the source lifetime.

### Buggy code

```cpp
std::string_view name() { return std::string("x"); }
```

### Expected diagnosis

The temporary string dies before the view is used.

### Corrected code

```cpp
std::string name() { return "x"; }
```

### Regression tests

```cpp
assert(name() == "x");
```

## ECPP-E-085: unchecked span length

- Difficulty: Easy
- Language/platform: Embedded C++
- Perspective: Buffers
- Concept: unchecked span length
- Symptom: A peripheral read writes beyond a buffer.
- Diagnostic goal: Pass capacity and validate length before copying.

### Buggy code

```cpp
std::copy(src, src + length, dst.begin());
```

### Expected diagnosis

The source length is not bounded by destination capacity.

### Corrected code

```cpp
if (length > dst.size()) return Error::TooLarge; std::copy_n(src, length, dst.begin());
```

### Regression tests

```cpp
assert_oversized_copy_is_rejected();
```

## ECPP-E-086: data race

- Difficulty: Easy
- Language/platform: Embedded C++
- Perspective: Concurrency
- Concept: data race
- Symptom: A sensor value changes while being read.
- Diagnostic goal: Use an atomic snapshot or lock.

### Buggy code

```cpp
latest = sample;
return latest;
```

### Expected diagnosis

Concurrent read/write of a non-atomic object is undefined behavior.

### Corrected code

```cpp
std::lock_guard lock(mutex); latest = sample;
```

### Regression tests

```cpp
assert_snapshot_is_consistent();
```

## ECPP-E-087: allocation in hot loop

- Difficulty: Easy
- Language/platform: Embedded C++
- Perspective: Timing
- Concept: allocation in hot loop
- Symptom: Control latency has jitter.
- Diagnostic goal: Preallocate and avoid unbounded work in the deadline path.

### Buggy code

```cpp
std::vector<int> values; values.push_back(sample);
```

### Expected diagnosis

Growth may allocate unpredictably during the real-time path.

### Corrected code

```cpp
std::array<int, 64> values; values[count++] = sample;
```

### Regression tests

```cpp
assert_no_allocation_in_control_path();
```

## ECPP-E-088: illegal transition

- Difficulty: Easy
- Language/platform: Embedded C++
- Perspective: State
- Concept: illegal transition
- Symptom: A device enters an unsafe mode.
- Diagnostic goal: Centralize legal state transitions.

### Buggy code

```cpp
state = State::Running;
```

### Expected diagnosis

The assignment ignores the current state and event validity.

### Corrected code

```cpp
if (state == State::Idle && event == Event::Start) state = State::Running; else return Error::InvalidTransition;
```

### Regression tests

```cpp
assert_invalid_transition_rejected();
```

## ECPP-E-089: copying driver handle

- Difficulty: Easy
- Language/platform: Embedded C++
- Perspective: Power
- Concept: copying driver handle
- Symptom: Two objects shut down the same peripheral.
- Diagnostic goal: Make ownership move-only.

### Buggy code

```cpp
Driver a = b;
```

### Expected diagnosis

Copying duplicates exclusive hardware ownership.

### Corrected code

```cpp
Driver a = std::move(b);
```

### Regression tests

```cpp
static_assert(!std::is_copy_constructible_v<Driver>);
```

## ECPP-E-090: ignored expected error

- Difficulty: Easy
- Language/platform: Embedded C++
- Perspective: Fault handling
- Concept: ignored expected error
- Symptom: A disconnected sensor returns stale data.
- Diagnostic goal: Propagate a typed error and choose a safe fallback.

### Buggy code

```cpp
auto value = sensor.read().value();
```

### Expected diagnosis

value() assumes success and can throw or abort.

### Corrected code

```cpp
auto value = sensor.read(); if (!value) return SafeDefault;
```

### Regression tests

```cpp
assert_disconnect_uses_safe_default();
```

## ECPP-E-091: manual peripheral cleanup

- Difficulty: Easy
- Language/platform: Embedded C++
- Perspective: RAII
- Concept: manual peripheral cleanup
- Symptom: An exception leaves a peripheral enabled.
- Diagnostic goal: Bind cleanup to object lifetime.

### Buggy code

```cpp
device.enable();
read();
device.disable();
```

### Expected diagnosis

An exception from read skips disable.

### Corrected code

```cpp
DeviceGuard guard(device);
read();
```

### Regression tests

```cpp
assert_guard_disables_on_exception();
```

## ECPP-E-092: nontrivial ISR object

- Difficulty: Easy
- Language/platform: Embedded C++
- Perspective: Interrupts
- Concept: nontrivial ISR object
- Symptom: The handler allocates or locks.
- Diagnostic goal: Publish a small flag or index only.

### Buggy code

```cpp
void isr() { queue.push(String("edge")); }
```

### Expected diagnosis

Dynamic allocation and locks are unsafe in interrupt context.

### Corrected code

```cpp
volatile uint8_t pending = 1;
```

### Regression tests

```cpp
assert_main_loop_processes_pending();
```

## ECPP-E-093: use moved object

- Difficulty: Easy
- Language/platform: Embedded C++
- Perspective: Move
- Concept: use moved object
- Symptom: The source is assumed to retain resources.
- Diagnostic goal: Use the destination after move or define a valid moved-from state.

### Buggy code

```cpp
auto b = std::move(a); use(a);
```

### Expected diagnosis

Moving transfers ownership and leaves a valid but unspecified source.

### Corrected code

```cpp
auto b = std::move(a); use(b);
```

### Regression tests

```cpp
assert_destination_owns_resource();
```

## ECPP-E-094: dangling view

- Difficulty: Easy
- Language/platform: Embedded C++
- Perspective: Templates
- Concept: dangling view
- Symptom: A view points into a destroyed temporary.
- Diagnostic goal: Return owned storage or extend the source lifetime.

### Buggy code

```cpp
std::string_view name() { return std::string("x"); }
```

### Expected diagnosis

The temporary string dies before the view is used.

### Corrected code

```cpp
std::string name() { return "x"; }
```

### Regression tests

```cpp
assert(name() == "x");
```

## ECPP-E-095: unchecked span length

- Difficulty: Easy
- Language/platform: Embedded C++
- Perspective: Buffers
- Concept: unchecked span length
- Symptom: A peripheral read writes beyond a buffer.
- Diagnostic goal: Pass capacity and validate length before copying.

### Buggy code

```cpp
std::copy(src, src + length, dst.begin());
```

### Expected diagnosis

The source length is not bounded by destination capacity.

### Corrected code

```cpp
if (length > dst.size()) return Error::TooLarge; std::copy_n(src, length, dst.begin());
```

### Regression tests

```cpp
assert_oversized_copy_is_rejected();
```

## ECPP-E-096: data race

- Difficulty: Easy
- Language/platform: Embedded C++
- Perspective: Concurrency
- Concept: data race
- Symptom: A sensor value changes while being read.
- Diagnostic goal: Use an atomic snapshot or lock.

### Buggy code

```cpp
latest = sample;
return latest;
```

### Expected diagnosis

Concurrent read/write of a non-atomic object is undefined behavior.

### Corrected code

```cpp
std::lock_guard lock(mutex); latest = sample;
```

### Regression tests

```cpp
assert_snapshot_is_consistent();
```

## ECPP-E-097: allocation in hot loop

- Difficulty: Easy
- Language/platform: Embedded C++
- Perspective: Timing
- Concept: allocation in hot loop
- Symptom: Control latency has jitter.
- Diagnostic goal: Preallocate and avoid unbounded work in the deadline path.

### Buggy code

```cpp
std::vector<int> values; values.push_back(sample);
```

### Expected diagnosis

Growth may allocate unpredictably during the real-time path.

### Corrected code

```cpp
std::array<int, 64> values; values[count++] = sample;
```

### Regression tests

```cpp
assert_no_allocation_in_control_path();
```

## ECPP-E-098: illegal transition

- Difficulty: Easy
- Language/platform: Embedded C++
- Perspective: State
- Concept: illegal transition
- Symptom: A device enters an unsafe mode.
- Diagnostic goal: Centralize legal state transitions.

### Buggy code

```cpp
state = State::Running;
```

### Expected diagnosis

The assignment ignores the current state and event validity.

### Corrected code

```cpp
if (state == State::Idle && event == Event::Start) state = State::Running; else return Error::InvalidTransition;
```

### Regression tests

```cpp
assert_invalid_transition_rejected();
```

## ECPP-E-099: copying driver handle

- Difficulty: Easy
- Language/platform: Embedded C++
- Perspective: Power
- Concept: copying driver handle
- Symptom: Two objects shut down the same peripheral.
- Diagnostic goal: Make ownership move-only.

### Buggy code

```cpp
Driver a = b;
```

### Expected diagnosis

Copying duplicates exclusive hardware ownership.

### Corrected code

```cpp
Driver a = std::move(b);
```

### Regression tests

```cpp
static_assert(!std::is_copy_constructible_v<Driver>);
```

## ECPP-E-100: ignored expected error

- Difficulty: Easy
- Language/platform: Embedded C++
- Perspective: Fault handling
- Concept: ignored expected error
- Symptom: A disconnected sensor returns stale data.
- Diagnostic goal: Propagate a typed error and choose a safe fallback.

### Buggy code

```cpp
auto value = sensor.read().value();
```

### Expected diagnosis

value() assumes success and can throw or abort.

### Corrected code

```cpp
auto value = sensor.read(); if (!value) return SafeDefault;
```

### Regression tests

```cpp
assert_disconnect_uses_safe_default();
```

## ECPP-M-001: manual peripheral cleanup

- Difficulty: Medium
- Language/platform: Embedded C++
- Perspective: RAII
- Concept: manual peripheral cleanup
- Symptom: An exception leaves a peripheral enabled.
- Diagnostic goal: Bind cleanup to object lifetime.

### Buggy code

```cpp
device.enable();
read();
device.disable();
```

### Expected diagnosis

An exception from read skips disable.

### Corrected code

```cpp
DeviceGuard guard(device);
read();
```

### Regression tests

```cpp
assert_guard_disables_on_exception();
```

## ECPP-M-002: nontrivial ISR object

- Difficulty: Medium
- Language/platform: Embedded C++
- Perspective: Interrupts
- Concept: nontrivial ISR object
- Symptom: The handler allocates or locks.
- Diagnostic goal: Publish a small flag or index only.

### Buggy code

```cpp
void isr() { queue.push(String("edge")); }
```

### Expected diagnosis

Dynamic allocation and locks are unsafe in interrupt context.

### Corrected code

```cpp
volatile uint8_t pending = 1;
```

### Regression tests

```cpp
assert_main_loop_processes_pending();
```

## ECPP-M-003: use moved object

- Difficulty: Medium
- Language/platform: Embedded C++
- Perspective: Move
- Concept: use moved object
- Symptom: The source is assumed to retain resources.
- Diagnostic goal: Use the destination after move or define a valid moved-from state.

### Buggy code

```cpp
auto b = std::move(a); use(a);
```

### Expected diagnosis

Moving transfers ownership and leaves a valid but unspecified source.

### Corrected code

```cpp
auto b = std::move(a); use(b);
```

### Regression tests

```cpp
assert_destination_owns_resource();
```

## ECPP-M-004: dangling view

- Difficulty: Medium
- Language/platform: Embedded C++
- Perspective: Templates
- Concept: dangling view
- Symptom: A view points into a destroyed temporary.
- Diagnostic goal: Return owned storage or extend the source lifetime.

### Buggy code

```cpp
std::string_view name() { return std::string("x"); }
```

### Expected diagnosis

The temporary string dies before the view is used.

### Corrected code

```cpp
std::string name() { return "x"; }
```

### Regression tests

```cpp
assert(name() == "x");
```

## ECPP-M-005: unchecked span length

- Difficulty: Medium
- Language/platform: Embedded C++
- Perspective: Buffers
- Concept: unchecked span length
- Symptom: A peripheral read writes beyond a buffer.
- Diagnostic goal: Pass capacity and validate length before copying.

### Buggy code

```cpp
std::copy(src, src + length, dst.begin());
```

### Expected diagnosis

The source length is not bounded by destination capacity.

### Corrected code

```cpp
if (length > dst.size()) return Error::TooLarge; std::copy_n(src, length, dst.begin());
```

### Regression tests

```cpp
assert_oversized_copy_is_rejected();
```

## ECPP-M-006: data race

- Difficulty: Medium
- Language/platform: Embedded C++
- Perspective: Concurrency
- Concept: data race
- Symptom: A sensor value changes while being read.
- Diagnostic goal: Use an atomic snapshot or lock.

### Buggy code

```cpp
latest = sample;
return latest;
```

### Expected diagnosis

Concurrent read/write of a non-atomic object is undefined behavior.

### Corrected code

```cpp
std::lock_guard lock(mutex); latest = sample;
```

### Regression tests

```cpp
assert_snapshot_is_consistent();
```

## ECPP-M-007: allocation in hot loop

- Difficulty: Medium
- Language/platform: Embedded C++
- Perspective: Timing
- Concept: allocation in hot loop
- Symptom: Control latency has jitter.
- Diagnostic goal: Preallocate and avoid unbounded work in the deadline path.

### Buggy code

```cpp
std::vector<int> values; values.push_back(sample);
```

### Expected diagnosis

Growth may allocate unpredictably during the real-time path.

### Corrected code

```cpp
std::array<int, 64> values; values[count++] = sample;
```

### Regression tests

```cpp
assert_no_allocation_in_control_path();
```

## ECPP-M-008: illegal transition

- Difficulty: Medium
- Language/platform: Embedded C++
- Perspective: State
- Concept: illegal transition
- Symptom: A device enters an unsafe mode.
- Diagnostic goal: Centralize legal state transitions.

### Buggy code

```cpp
state = State::Running;
```

### Expected diagnosis

The assignment ignores the current state and event validity.

### Corrected code

```cpp
if (state == State::Idle && event == Event::Start) state = State::Running; else return Error::InvalidTransition;
```

### Regression tests

```cpp
assert_invalid_transition_rejected();
```

## ECPP-M-009: copying driver handle

- Difficulty: Medium
- Language/platform: Embedded C++
- Perspective: Power
- Concept: copying driver handle
- Symptom: Two objects shut down the same peripheral.
- Diagnostic goal: Make ownership move-only.

### Buggy code

```cpp
Driver a = b;
```

### Expected diagnosis

Copying duplicates exclusive hardware ownership.

### Corrected code

```cpp
Driver a = std::move(b);
```

### Regression tests

```cpp
static_assert(!std::is_copy_constructible_v<Driver>);
```

## ECPP-M-010: ignored expected error

- Difficulty: Medium
- Language/platform: Embedded C++
- Perspective: Fault handling
- Concept: ignored expected error
- Symptom: A disconnected sensor returns stale data.
- Diagnostic goal: Propagate a typed error and choose a safe fallback.

### Buggy code

```cpp
auto value = sensor.read().value();
```

### Expected diagnosis

value() assumes success and can throw or abort.

### Corrected code

```cpp
auto value = sensor.read(); if (!value) return SafeDefault;
```

### Regression tests

```cpp
assert_disconnect_uses_safe_default();
```

## ECPP-M-011: manual peripheral cleanup

- Difficulty: Medium
- Language/platform: Embedded C++
- Perspective: RAII
- Concept: manual peripheral cleanup
- Symptom: An exception leaves a peripheral enabled.
- Diagnostic goal: Bind cleanup to object lifetime.

### Buggy code

```cpp
device.enable();
read();
device.disable();
```

### Expected diagnosis

An exception from read skips disable.

### Corrected code

```cpp
DeviceGuard guard(device);
read();
```

### Regression tests

```cpp
assert_guard_disables_on_exception();
```

## ECPP-M-012: nontrivial ISR object

- Difficulty: Medium
- Language/platform: Embedded C++
- Perspective: Interrupts
- Concept: nontrivial ISR object
- Symptom: The handler allocates or locks.
- Diagnostic goal: Publish a small flag or index only.

### Buggy code

```cpp
void isr() { queue.push(String("edge")); }
```

### Expected diagnosis

Dynamic allocation and locks are unsafe in interrupt context.

### Corrected code

```cpp
volatile uint8_t pending = 1;
```

### Regression tests

```cpp
assert_main_loop_processes_pending();
```

## ECPP-M-013: use moved object

- Difficulty: Medium
- Language/platform: Embedded C++
- Perspective: Move
- Concept: use moved object
- Symptom: The source is assumed to retain resources.
- Diagnostic goal: Use the destination after move or define a valid moved-from state.

### Buggy code

```cpp
auto b = std::move(a); use(a);
```

### Expected diagnosis

Moving transfers ownership and leaves a valid but unspecified source.

### Corrected code

```cpp
auto b = std::move(a); use(b);
```

### Regression tests

```cpp
assert_destination_owns_resource();
```

## ECPP-M-014: dangling view

- Difficulty: Medium
- Language/platform: Embedded C++
- Perspective: Templates
- Concept: dangling view
- Symptom: A view points into a destroyed temporary.
- Diagnostic goal: Return owned storage or extend the source lifetime.

### Buggy code

```cpp
std::string_view name() { return std::string("x"); }
```

### Expected diagnosis

The temporary string dies before the view is used.

### Corrected code

```cpp
std::string name() { return "x"; }
```

### Regression tests

```cpp
assert(name() == "x");
```

## ECPP-M-015: unchecked span length

- Difficulty: Medium
- Language/platform: Embedded C++
- Perspective: Buffers
- Concept: unchecked span length
- Symptom: A peripheral read writes beyond a buffer.
- Diagnostic goal: Pass capacity and validate length before copying.

### Buggy code

```cpp
std::copy(src, src + length, dst.begin());
```

### Expected diagnosis

The source length is not bounded by destination capacity.

### Corrected code

```cpp
if (length > dst.size()) return Error::TooLarge; std::copy_n(src, length, dst.begin());
```

### Regression tests

```cpp
assert_oversized_copy_is_rejected();
```

## ECPP-M-016: data race

- Difficulty: Medium
- Language/platform: Embedded C++
- Perspective: Concurrency
- Concept: data race
- Symptom: A sensor value changes while being read.
- Diagnostic goal: Use an atomic snapshot or lock.

### Buggy code

```cpp
latest = sample;
return latest;
```

### Expected diagnosis

Concurrent read/write of a non-atomic object is undefined behavior.

### Corrected code

```cpp
std::lock_guard lock(mutex); latest = sample;
```

### Regression tests

```cpp
assert_snapshot_is_consistent();
```

## ECPP-M-017: allocation in hot loop

- Difficulty: Medium
- Language/platform: Embedded C++
- Perspective: Timing
- Concept: allocation in hot loop
- Symptom: Control latency has jitter.
- Diagnostic goal: Preallocate and avoid unbounded work in the deadline path.

### Buggy code

```cpp
std::vector<int> values; values.push_back(sample);
```

### Expected diagnosis

Growth may allocate unpredictably during the real-time path.

### Corrected code

```cpp
std::array<int, 64> values; values[count++] = sample;
```

### Regression tests

```cpp
assert_no_allocation_in_control_path();
```

## ECPP-M-018: illegal transition

- Difficulty: Medium
- Language/platform: Embedded C++
- Perspective: State
- Concept: illegal transition
- Symptom: A device enters an unsafe mode.
- Diagnostic goal: Centralize legal state transitions.

### Buggy code

```cpp
state = State::Running;
```

### Expected diagnosis

The assignment ignores the current state and event validity.

### Corrected code

```cpp
if (state == State::Idle && event == Event::Start) state = State::Running; else return Error::InvalidTransition;
```

### Regression tests

```cpp
assert_invalid_transition_rejected();
```

## ECPP-M-019: copying driver handle

- Difficulty: Medium
- Language/platform: Embedded C++
- Perspective: Power
- Concept: copying driver handle
- Symptom: Two objects shut down the same peripheral.
- Diagnostic goal: Make ownership move-only.

### Buggy code

```cpp
Driver a = b;
```

### Expected diagnosis

Copying duplicates exclusive hardware ownership.

### Corrected code

```cpp
Driver a = std::move(b);
```

### Regression tests

```cpp
static_assert(!std::is_copy_constructible_v<Driver>);
```

## ECPP-M-020: ignored expected error

- Difficulty: Medium
- Language/platform: Embedded C++
- Perspective: Fault handling
- Concept: ignored expected error
- Symptom: A disconnected sensor returns stale data.
- Diagnostic goal: Propagate a typed error and choose a safe fallback.

### Buggy code

```cpp
auto value = sensor.read().value();
```

### Expected diagnosis

value() assumes success and can throw or abort.

### Corrected code

```cpp
auto value = sensor.read(); if (!value) return SafeDefault;
```

### Regression tests

```cpp
assert_disconnect_uses_safe_default();
```

## ECPP-M-021: manual peripheral cleanup

- Difficulty: Medium
- Language/platform: Embedded C++
- Perspective: RAII
- Concept: manual peripheral cleanup
- Symptom: An exception leaves a peripheral enabled.
- Diagnostic goal: Bind cleanup to object lifetime.

### Buggy code

```cpp
device.enable();
read();
device.disable();
```

### Expected diagnosis

An exception from read skips disable.

### Corrected code

```cpp
DeviceGuard guard(device);
read();
```

### Regression tests

```cpp
assert_guard_disables_on_exception();
```

## ECPP-M-022: nontrivial ISR object

- Difficulty: Medium
- Language/platform: Embedded C++
- Perspective: Interrupts
- Concept: nontrivial ISR object
- Symptom: The handler allocates or locks.
- Diagnostic goal: Publish a small flag or index only.

### Buggy code

```cpp
void isr() { queue.push(String("edge")); }
```

### Expected diagnosis

Dynamic allocation and locks are unsafe in interrupt context.

### Corrected code

```cpp
volatile uint8_t pending = 1;
```

### Regression tests

```cpp
assert_main_loop_processes_pending();
```

## ECPP-M-023: use moved object

- Difficulty: Medium
- Language/platform: Embedded C++
- Perspective: Move
- Concept: use moved object
- Symptom: The source is assumed to retain resources.
- Diagnostic goal: Use the destination after move or define a valid moved-from state.

### Buggy code

```cpp
auto b = std::move(a); use(a);
```

### Expected diagnosis

Moving transfers ownership and leaves a valid but unspecified source.

### Corrected code

```cpp
auto b = std::move(a); use(b);
```

### Regression tests

```cpp
assert_destination_owns_resource();
```

## ECPP-M-024: dangling view

- Difficulty: Medium
- Language/platform: Embedded C++
- Perspective: Templates
- Concept: dangling view
- Symptom: A view points into a destroyed temporary.
- Diagnostic goal: Return owned storage or extend the source lifetime.

### Buggy code

```cpp
std::string_view name() { return std::string("x"); }
```

### Expected diagnosis

The temporary string dies before the view is used.

### Corrected code

```cpp
std::string name() { return "x"; }
```

### Regression tests

```cpp
assert(name() == "x");
```

## ECPP-M-025: unchecked span length

- Difficulty: Medium
- Language/platform: Embedded C++
- Perspective: Buffers
- Concept: unchecked span length
- Symptom: A peripheral read writes beyond a buffer.
- Diagnostic goal: Pass capacity and validate length before copying.

### Buggy code

```cpp
std::copy(src, src + length, dst.begin());
```

### Expected diagnosis

The source length is not bounded by destination capacity.

### Corrected code

```cpp
if (length > dst.size()) return Error::TooLarge; std::copy_n(src, length, dst.begin());
```

### Regression tests

```cpp
assert_oversized_copy_is_rejected();
```

## ECPP-M-026: data race

- Difficulty: Medium
- Language/platform: Embedded C++
- Perspective: Concurrency
- Concept: data race
- Symptom: A sensor value changes while being read.
- Diagnostic goal: Use an atomic snapshot or lock.

### Buggy code

```cpp
latest = sample;
return latest;
```

### Expected diagnosis

Concurrent read/write of a non-atomic object is undefined behavior.

### Corrected code

```cpp
std::lock_guard lock(mutex); latest = sample;
```

### Regression tests

```cpp
assert_snapshot_is_consistent();
```

## ECPP-M-027: allocation in hot loop

- Difficulty: Medium
- Language/platform: Embedded C++
- Perspective: Timing
- Concept: allocation in hot loop
- Symptom: Control latency has jitter.
- Diagnostic goal: Preallocate and avoid unbounded work in the deadline path.

### Buggy code

```cpp
std::vector<int> values; values.push_back(sample);
```

### Expected diagnosis

Growth may allocate unpredictably during the real-time path.

### Corrected code

```cpp
std::array<int, 64> values; values[count++] = sample;
```

### Regression tests

```cpp
assert_no_allocation_in_control_path();
```

## ECPP-M-028: illegal transition

- Difficulty: Medium
- Language/platform: Embedded C++
- Perspective: State
- Concept: illegal transition
- Symptom: A device enters an unsafe mode.
- Diagnostic goal: Centralize legal state transitions.

### Buggy code

```cpp
state = State::Running;
```

### Expected diagnosis

The assignment ignores the current state and event validity.

### Corrected code

```cpp
if (state == State::Idle && event == Event::Start) state = State::Running; else return Error::InvalidTransition;
```

### Regression tests

```cpp
assert_invalid_transition_rejected();
```

## ECPP-M-029: copying driver handle

- Difficulty: Medium
- Language/platform: Embedded C++
- Perspective: Power
- Concept: copying driver handle
- Symptom: Two objects shut down the same peripheral.
- Diagnostic goal: Make ownership move-only.

### Buggy code

```cpp
Driver a = b;
```

### Expected diagnosis

Copying duplicates exclusive hardware ownership.

### Corrected code

```cpp
Driver a = std::move(b);
```

### Regression tests

```cpp
static_assert(!std::is_copy_constructible_v<Driver>);
```

## ECPP-M-030: ignored expected error

- Difficulty: Medium
- Language/platform: Embedded C++
- Perspective: Fault handling
- Concept: ignored expected error
- Symptom: A disconnected sensor returns stale data.
- Diagnostic goal: Propagate a typed error and choose a safe fallback.

### Buggy code

```cpp
auto value = sensor.read().value();
```

### Expected diagnosis

value() assumes success and can throw or abort.

### Corrected code

```cpp
auto value = sensor.read(); if (!value) return SafeDefault;
```

### Regression tests

```cpp
assert_disconnect_uses_safe_default();
```

## ECPP-M-031: manual peripheral cleanup

- Difficulty: Medium
- Language/platform: Embedded C++
- Perspective: RAII
- Concept: manual peripheral cleanup
- Symptom: An exception leaves a peripheral enabled.
- Diagnostic goal: Bind cleanup to object lifetime.

### Buggy code

```cpp
device.enable();
read();
device.disable();
```

### Expected diagnosis

An exception from read skips disable.

### Corrected code

```cpp
DeviceGuard guard(device);
read();
```

### Regression tests

```cpp
assert_guard_disables_on_exception();
```

## ECPP-M-032: nontrivial ISR object

- Difficulty: Medium
- Language/platform: Embedded C++
- Perspective: Interrupts
- Concept: nontrivial ISR object
- Symptom: The handler allocates or locks.
- Diagnostic goal: Publish a small flag or index only.

### Buggy code

```cpp
void isr() { queue.push(String("edge")); }
```

### Expected diagnosis

Dynamic allocation and locks are unsafe in interrupt context.

### Corrected code

```cpp
volatile uint8_t pending = 1;
```

### Regression tests

```cpp
assert_main_loop_processes_pending();
```

## ECPP-M-033: use moved object

- Difficulty: Medium
- Language/platform: Embedded C++
- Perspective: Move
- Concept: use moved object
- Symptom: The source is assumed to retain resources.
- Diagnostic goal: Use the destination after move or define a valid moved-from state.

### Buggy code

```cpp
auto b = std::move(a); use(a);
```

### Expected diagnosis

Moving transfers ownership and leaves a valid but unspecified source.

### Corrected code

```cpp
auto b = std::move(a); use(b);
```

### Regression tests

```cpp
assert_destination_owns_resource();
```

## ECPP-M-034: dangling view

- Difficulty: Medium
- Language/platform: Embedded C++
- Perspective: Templates
- Concept: dangling view
- Symptom: A view points into a destroyed temporary.
- Diagnostic goal: Return owned storage or extend the source lifetime.

### Buggy code

```cpp
std::string_view name() { return std::string("x"); }
```

### Expected diagnosis

The temporary string dies before the view is used.

### Corrected code

```cpp
std::string name() { return "x"; }
```

### Regression tests

```cpp
assert(name() == "x");
```

## ECPP-M-035: unchecked span length

- Difficulty: Medium
- Language/platform: Embedded C++
- Perspective: Buffers
- Concept: unchecked span length
- Symptom: A peripheral read writes beyond a buffer.
- Diagnostic goal: Pass capacity and validate length before copying.

### Buggy code

```cpp
std::copy(src, src + length, dst.begin());
```

### Expected diagnosis

The source length is not bounded by destination capacity.

### Corrected code

```cpp
if (length > dst.size()) return Error::TooLarge; std::copy_n(src, length, dst.begin());
```

### Regression tests

```cpp
assert_oversized_copy_is_rejected();
```

## ECPP-M-036: data race

- Difficulty: Medium
- Language/platform: Embedded C++
- Perspective: Concurrency
- Concept: data race
- Symptom: A sensor value changes while being read.
- Diagnostic goal: Use an atomic snapshot or lock.

### Buggy code

```cpp
latest = sample;
return latest;
```

### Expected diagnosis

Concurrent read/write of a non-atomic object is undefined behavior.

### Corrected code

```cpp
std::lock_guard lock(mutex); latest = sample;
```

### Regression tests

```cpp
assert_snapshot_is_consistent();
```

## ECPP-M-037: allocation in hot loop

- Difficulty: Medium
- Language/platform: Embedded C++
- Perspective: Timing
- Concept: allocation in hot loop
- Symptom: Control latency has jitter.
- Diagnostic goal: Preallocate and avoid unbounded work in the deadline path.

### Buggy code

```cpp
std::vector<int> values; values.push_back(sample);
```

### Expected diagnosis

Growth may allocate unpredictably during the real-time path.

### Corrected code

```cpp
std::array<int, 64> values; values[count++] = sample;
```

### Regression tests

```cpp
assert_no_allocation_in_control_path();
```

## ECPP-M-038: illegal transition

- Difficulty: Medium
- Language/platform: Embedded C++
- Perspective: State
- Concept: illegal transition
- Symptom: A device enters an unsafe mode.
- Diagnostic goal: Centralize legal state transitions.

### Buggy code

```cpp
state = State::Running;
```

### Expected diagnosis

The assignment ignores the current state and event validity.

### Corrected code

```cpp
if (state == State::Idle && event == Event::Start) state = State::Running; else return Error::InvalidTransition;
```

### Regression tests

```cpp
assert_invalid_transition_rejected();
```

## ECPP-M-039: copying driver handle

- Difficulty: Medium
- Language/platform: Embedded C++
- Perspective: Power
- Concept: copying driver handle
- Symptom: Two objects shut down the same peripheral.
- Diagnostic goal: Make ownership move-only.

### Buggy code

```cpp
Driver a = b;
```

### Expected diagnosis

Copying duplicates exclusive hardware ownership.

### Corrected code

```cpp
Driver a = std::move(b);
```

### Regression tests

```cpp
static_assert(!std::is_copy_constructible_v<Driver>);
```

## ECPP-M-040: ignored expected error

- Difficulty: Medium
- Language/platform: Embedded C++
- Perspective: Fault handling
- Concept: ignored expected error
- Symptom: A disconnected sensor returns stale data.
- Diagnostic goal: Propagate a typed error and choose a safe fallback.

### Buggy code

```cpp
auto value = sensor.read().value();
```

### Expected diagnosis

value() assumes success and can throw or abort.

### Corrected code

```cpp
auto value = sensor.read(); if (!value) return SafeDefault;
```

### Regression tests

```cpp
assert_disconnect_uses_safe_default();
```

## ECPP-M-041: manual peripheral cleanup

- Difficulty: Medium
- Language/platform: Embedded C++
- Perspective: RAII
- Concept: manual peripheral cleanup
- Symptom: An exception leaves a peripheral enabled.
- Diagnostic goal: Bind cleanup to object lifetime.

### Buggy code

```cpp
device.enable();
read();
device.disable();
```

### Expected diagnosis

An exception from read skips disable.

### Corrected code

```cpp
DeviceGuard guard(device);
read();
```

### Regression tests

```cpp
assert_guard_disables_on_exception();
```

## ECPP-M-042: nontrivial ISR object

- Difficulty: Medium
- Language/platform: Embedded C++
- Perspective: Interrupts
- Concept: nontrivial ISR object
- Symptom: The handler allocates or locks.
- Diagnostic goal: Publish a small flag or index only.

### Buggy code

```cpp
void isr() { queue.push(String("edge")); }
```

### Expected diagnosis

Dynamic allocation and locks are unsafe in interrupt context.

### Corrected code

```cpp
volatile uint8_t pending = 1;
```

### Regression tests

```cpp
assert_main_loop_processes_pending();
```

## ECPP-M-043: use moved object

- Difficulty: Medium
- Language/platform: Embedded C++
- Perspective: Move
- Concept: use moved object
- Symptom: The source is assumed to retain resources.
- Diagnostic goal: Use the destination after move or define a valid moved-from state.

### Buggy code

```cpp
auto b = std::move(a); use(a);
```

### Expected diagnosis

Moving transfers ownership and leaves a valid but unspecified source.

### Corrected code

```cpp
auto b = std::move(a); use(b);
```

### Regression tests

```cpp
assert_destination_owns_resource();
```

## ECPP-M-044: dangling view

- Difficulty: Medium
- Language/platform: Embedded C++
- Perspective: Templates
- Concept: dangling view
- Symptom: A view points into a destroyed temporary.
- Diagnostic goal: Return owned storage or extend the source lifetime.

### Buggy code

```cpp
std::string_view name() { return std::string("x"); }
```

### Expected diagnosis

The temporary string dies before the view is used.

### Corrected code

```cpp
std::string name() { return "x"; }
```

### Regression tests

```cpp
assert(name() == "x");
```

## ECPP-M-045: unchecked span length

- Difficulty: Medium
- Language/platform: Embedded C++
- Perspective: Buffers
- Concept: unchecked span length
- Symptom: A peripheral read writes beyond a buffer.
- Diagnostic goal: Pass capacity and validate length before copying.

### Buggy code

```cpp
std::copy(src, src + length, dst.begin());
```

### Expected diagnosis

The source length is not bounded by destination capacity.

### Corrected code

```cpp
if (length > dst.size()) return Error::TooLarge; std::copy_n(src, length, dst.begin());
```

### Regression tests

```cpp
assert_oversized_copy_is_rejected();
```

## ECPP-M-046: data race

- Difficulty: Medium
- Language/platform: Embedded C++
- Perspective: Concurrency
- Concept: data race
- Symptom: A sensor value changes while being read.
- Diagnostic goal: Use an atomic snapshot or lock.

### Buggy code

```cpp
latest = sample;
return latest;
```

### Expected diagnosis

Concurrent read/write of a non-atomic object is undefined behavior.

### Corrected code

```cpp
std::lock_guard lock(mutex); latest = sample;
```

### Regression tests

```cpp
assert_snapshot_is_consistent();
```

## ECPP-M-047: allocation in hot loop

- Difficulty: Medium
- Language/platform: Embedded C++
- Perspective: Timing
- Concept: allocation in hot loop
- Symptom: Control latency has jitter.
- Diagnostic goal: Preallocate and avoid unbounded work in the deadline path.

### Buggy code

```cpp
std::vector<int> values; values.push_back(sample);
```

### Expected diagnosis

Growth may allocate unpredictably during the real-time path.

### Corrected code

```cpp
std::array<int, 64> values; values[count++] = sample;
```

### Regression tests

```cpp
assert_no_allocation_in_control_path();
```

## ECPP-M-048: illegal transition

- Difficulty: Medium
- Language/platform: Embedded C++
- Perspective: State
- Concept: illegal transition
- Symptom: A device enters an unsafe mode.
- Diagnostic goal: Centralize legal state transitions.

### Buggy code

```cpp
state = State::Running;
```

### Expected diagnosis

The assignment ignores the current state and event validity.

### Corrected code

```cpp
if (state == State::Idle && event == Event::Start) state = State::Running; else return Error::InvalidTransition;
```

### Regression tests

```cpp
assert_invalid_transition_rejected();
```

## ECPP-M-049: copying driver handle

- Difficulty: Medium
- Language/platform: Embedded C++
- Perspective: Power
- Concept: copying driver handle
- Symptom: Two objects shut down the same peripheral.
- Diagnostic goal: Make ownership move-only.

### Buggy code

```cpp
Driver a = b;
```

### Expected diagnosis

Copying duplicates exclusive hardware ownership.

### Corrected code

```cpp
Driver a = std::move(b);
```

### Regression tests

```cpp
static_assert(!std::is_copy_constructible_v<Driver>);
```

## ECPP-M-050: ignored expected error

- Difficulty: Medium
- Language/platform: Embedded C++
- Perspective: Fault handling
- Concept: ignored expected error
- Symptom: A disconnected sensor returns stale data.
- Diagnostic goal: Propagate a typed error and choose a safe fallback.

### Buggy code

```cpp
auto value = sensor.read().value();
```

### Expected diagnosis

value() assumes success and can throw or abort.

### Corrected code

```cpp
auto value = sensor.read(); if (!value) return SafeDefault;
```

### Regression tests

```cpp
assert_disconnect_uses_safe_default();
```

## ECPP-M-051: manual peripheral cleanup

- Difficulty: Medium
- Language/platform: Embedded C++
- Perspective: RAII
- Concept: manual peripheral cleanup
- Symptom: An exception leaves a peripheral enabled.
- Diagnostic goal: Bind cleanup to object lifetime.

### Buggy code

```cpp
device.enable();
read();
device.disable();
```

### Expected diagnosis

An exception from read skips disable.

### Corrected code

```cpp
DeviceGuard guard(device);
read();
```

### Regression tests

```cpp
assert_guard_disables_on_exception();
```

## ECPP-M-052: nontrivial ISR object

- Difficulty: Medium
- Language/platform: Embedded C++
- Perspective: Interrupts
- Concept: nontrivial ISR object
- Symptom: The handler allocates or locks.
- Diagnostic goal: Publish a small flag or index only.

### Buggy code

```cpp
void isr() { queue.push(String("edge")); }
```

### Expected diagnosis

Dynamic allocation and locks are unsafe in interrupt context.

### Corrected code

```cpp
volatile uint8_t pending = 1;
```

### Regression tests

```cpp
assert_main_loop_processes_pending();
```

## ECPP-M-053: use moved object

- Difficulty: Medium
- Language/platform: Embedded C++
- Perspective: Move
- Concept: use moved object
- Symptom: The source is assumed to retain resources.
- Diagnostic goal: Use the destination after move or define a valid moved-from state.

### Buggy code

```cpp
auto b = std::move(a); use(a);
```

### Expected diagnosis

Moving transfers ownership and leaves a valid but unspecified source.

### Corrected code

```cpp
auto b = std::move(a); use(b);
```

### Regression tests

```cpp
assert_destination_owns_resource();
```

## ECPP-M-054: dangling view

- Difficulty: Medium
- Language/platform: Embedded C++
- Perspective: Templates
- Concept: dangling view
- Symptom: A view points into a destroyed temporary.
- Diagnostic goal: Return owned storage or extend the source lifetime.

### Buggy code

```cpp
std::string_view name() { return std::string("x"); }
```

### Expected diagnosis

The temporary string dies before the view is used.

### Corrected code

```cpp
std::string name() { return "x"; }
```

### Regression tests

```cpp
assert(name() == "x");
```

## ECPP-M-055: unchecked span length

- Difficulty: Medium
- Language/platform: Embedded C++
- Perspective: Buffers
- Concept: unchecked span length
- Symptom: A peripheral read writes beyond a buffer.
- Diagnostic goal: Pass capacity and validate length before copying.

### Buggy code

```cpp
std::copy(src, src + length, dst.begin());
```

### Expected diagnosis

The source length is not bounded by destination capacity.

### Corrected code

```cpp
if (length > dst.size()) return Error::TooLarge; std::copy_n(src, length, dst.begin());
```

### Regression tests

```cpp
assert_oversized_copy_is_rejected();
```

## ECPP-M-056: data race

- Difficulty: Medium
- Language/platform: Embedded C++
- Perspective: Concurrency
- Concept: data race
- Symptom: A sensor value changes while being read.
- Diagnostic goal: Use an atomic snapshot or lock.

### Buggy code

```cpp
latest = sample;
return latest;
```

### Expected diagnosis

Concurrent read/write of a non-atomic object is undefined behavior.

### Corrected code

```cpp
std::lock_guard lock(mutex); latest = sample;
```

### Regression tests

```cpp
assert_snapshot_is_consistent();
```

## ECPP-M-057: allocation in hot loop

- Difficulty: Medium
- Language/platform: Embedded C++
- Perspective: Timing
- Concept: allocation in hot loop
- Symptom: Control latency has jitter.
- Diagnostic goal: Preallocate and avoid unbounded work in the deadline path.

### Buggy code

```cpp
std::vector<int> values; values.push_back(sample);
```

### Expected diagnosis

Growth may allocate unpredictably during the real-time path.

### Corrected code

```cpp
std::array<int, 64> values; values[count++] = sample;
```

### Regression tests

```cpp
assert_no_allocation_in_control_path();
```

## ECPP-M-058: illegal transition

- Difficulty: Medium
- Language/platform: Embedded C++
- Perspective: State
- Concept: illegal transition
- Symptom: A device enters an unsafe mode.
- Diagnostic goal: Centralize legal state transitions.

### Buggy code

```cpp
state = State::Running;
```

### Expected diagnosis

The assignment ignores the current state and event validity.

### Corrected code

```cpp
if (state == State::Idle && event == Event::Start) state = State::Running; else return Error::InvalidTransition;
```

### Regression tests

```cpp
assert_invalid_transition_rejected();
```

## ECPP-M-059: copying driver handle

- Difficulty: Medium
- Language/platform: Embedded C++
- Perspective: Power
- Concept: copying driver handle
- Symptom: Two objects shut down the same peripheral.
- Diagnostic goal: Make ownership move-only.

### Buggy code

```cpp
Driver a = b;
```

### Expected diagnosis

Copying duplicates exclusive hardware ownership.

### Corrected code

```cpp
Driver a = std::move(b);
```

### Regression tests

```cpp
static_assert(!std::is_copy_constructible_v<Driver>);
```

## ECPP-M-060: ignored expected error

- Difficulty: Medium
- Language/platform: Embedded C++
- Perspective: Fault handling
- Concept: ignored expected error
- Symptom: A disconnected sensor returns stale data.
- Diagnostic goal: Propagate a typed error and choose a safe fallback.

### Buggy code

```cpp
auto value = sensor.read().value();
```

### Expected diagnosis

value() assumes success and can throw or abort.

### Corrected code

```cpp
auto value = sensor.read(); if (!value) return SafeDefault;
```

### Regression tests

```cpp
assert_disconnect_uses_safe_default();
```

## ECPP-M-061: manual peripheral cleanup

- Difficulty: Medium
- Language/platform: Embedded C++
- Perspective: RAII
- Concept: manual peripheral cleanup
- Symptom: An exception leaves a peripheral enabled.
- Diagnostic goal: Bind cleanup to object lifetime.

### Buggy code

```cpp
device.enable();
read();
device.disable();
```

### Expected diagnosis

An exception from read skips disable.

### Corrected code

```cpp
DeviceGuard guard(device);
read();
```

### Regression tests

```cpp
assert_guard_disables_on_exception();
```

## ECPP-M-062: nontrivial ISR object

- Difficulty: Medium
- Language/platform: Embedded C++
- Perspective: Interrupts
- Concept: nontrivial ISR object
- Symptom: The handler allocates or locks.
- Diagnostic goal: Publish a small flag or index only.

### Buggy code

```cpp
void isr() { queue.push(String("edge")); }
```

### Expected diagnosis

Dynamic allocation and locks are unsafe in interrupt context.

### Corrected code

```cpp
volatile uint8_t pending = 1;
```

### Regression tests

```cpp
assert_main_loop_processes_pending();
```

## ECPP-M-063: use moved object

- Difficulty: Medium
- Language/platform: Embedded C++
- Perspective: Move
- Concept: use moved object
- Symptom: The source is assumed to retain resources.
- Diagnostic goal: Use the destination after move or define a valid moved-from state.

### Buggy code

```cpp
auto b = std::move(a); use(a);
```

### Expected diagnosis

Moving transfers ownership and leaves a valid but unspecified source.

### Corrected code

```cpp
auto b = std::move(a); use(b);
```

### Regression tests

```cpp
assert_destination_owns_resource();
```

## ECPP-M-064: dangling view

- Difficulty: Medium
- Language/platform: Embedded C++
- Perspective: Templates
- Concept: dangling view
- Symptom: A view points into a destroyed temporary.
- Diagnostic goal: Return owned storage or extend the source lifetime.

### Buggy code

```cpp
std::string_view name() { return std::string("x"); }
```

### Expected diagnosis

The temporary string dies before the view is used.

### Corrected code

```cpp
std::string name() { return "x"; }
```

### Regression tests

```cpp
assert(name() == "x");
```

## ECPP-M-065: unchecked span length

- Difficulty: Medium
- Language/platform: Embedded C++
- Perspective: Buffers
- Concept: unchecked span length
- Symptom: A peripheral read writes beyond a buffer.
- Diagnostic goal: Pass capacity and validate length before copying.

### Buggy code

```cpp
std::copy(src, src + length, dst.begin());
```

### Expected diagnosis

The source length is not bounded by destination capacity.

### Corrected code

```cpp
if (length > dst.size()) return Error::TooLarge; std::copy_n(src, length, dst.begin());
```

### Regression tests

```cpp
assert_oversized_copy_is_rejected();
```

## ECPP-M-066: data race

- Difficulty: Medium
- Language/platform: Embedded C++
- Perspective: Concurrency
- Concept: data race
- Symptom: A sensor value changes while being read.
- Diagnostic goal: Use an atomic snapshot or lock.

### Buggy code

```cpp
latest = sample;
return latest;
```

### Expected diagnosis

Concurrent read/write of a non-atomic object is undefined behavior.

### Corrected code

```cpp
std::lock_guard lock(mutex); latest = sample;
```

### Regression tests

```cpp
assert_snapshot_is_consistent();
```

## ECPP-M-067: allocation in hot loop

- Difficulty: Medium
- Language/platform: Embedded C++
- Perspective: Timing
- Concept: allocation in hot loop
- Symptom: Control latency has jitter.
- Diagnostic goal: Preallocate and avoid unbounded work in the deadline path.

### Buggy code

```cpp
std::vector<int> values; values.push_back(sample);
```

### Expected diagnosis

Growth may allocate unpredictably during the real-time path.

### Corrected code

```cpp
std::array<int, 64> values; values[count++] = sample;
```

### Regression tests

```cpp
assert_no_allocation_in_control_path();
```

## ECPP-M-068: illegal transition

- Difficulty: Medium
- Language/platform: Embedded C++
- Perspective: State
- Concept: illegal transition
- Symptom: A device enters an unsafe mode.
- Diagnostic goal: Centralize legal state transitions.

### Buggy code

```cpp
state = State::Running;
```

### Expected diagnosis

The assignment ignores the current state and event validity.

### Corrected code

```cpp
if (state == State::Idle && event == Event::Start) state = State::Running; else return Error::InvalidTransition;
```

### Regression tests

```cpp
assert_invalid_transition_rejected();
```

## ECPP-M-069: copying driver handle

- Difficulty: Medium
- Language/platform: Embedded C++
- Perspective: Power
- Concept: copying driver handle
- Symptom: Two objects shut down the same peripheral.
- Diagnostic goal: Make ownership move-only.

### Buggy code

```cpp
Driver a = b;
```

### Expected diagnosis

Copying duplicates exclusive hardware ownership.

### Corrected code

```cpp
Driver a = std::move(b);
```

### Regression tests

```cpp
static_assert(!std::is_copy_constructible_v<Driver>);
```

## ECPP-M-070: ignored expected error

- Difficulty: Medium
- Language/platform: Embedded C++
- Perspective: Fault handling
- Concept: ignored expected error
- Symptom: A disconnected sensor returns stale data.
- Diagnostic goal: Propagate a typed error and choose a safe fallback.

### Buggy code

```cpp
auto value = sensor.read().value();
```

### Expected diagnosis

value() assumes success and can throw or abort.

### Corrected code

```cpp
auto value = sensor.read(); if (!value) return SafeDefault;
```

### Regression tests

```cpp
assert_disconnect_uses_safe_default();
```

## ECPP-M-071: manual peripheral cleanup

- Difficulty: Medium
- Language/platform: Embedded C++
- Perspective: RAII
- Concept: manual peripheral cleanup
- Symptom: An exception leaves a peripheral enabled.
- Diagnostic goal: Bind cleanup to object lifetime.

### Buggy code

```cpp
device.enable();
read();
device.disable();
```

### Expected diagnosis

An exception from read skips disable.

### Corrected code

```cpp
DeviceGuard guard(device);
read();
```

### Regression tests

```cpp
assert_guard_disables_on_exception();
```

## ECPP-M-072: nontrivial ISR object

- Difficulty: Medium
- Language/platform: Embedded C++
- Perspective: Interrupts
- Concept: nontrivial ISR object
- Symptom: The handler allocates or locks.
- Diagnostic goal: Publish a small flag or index only.

### Buggy code

```cpp
void isr() { queue.push(String("edge")); }
```

### Expected diagnosis

Dynamic allocation and locks are unsafe in interrupt context.

### Corrected code

```cpp
volatile uint8_t pending = 1;
```

### Regression tests

```cpp
assert_main_loop_processes_pending();
```

## ECPP-M-073: use moved object

- Difficulty: Medium
- Language/platform: Embedded C++
- Perspective: Move
- Concept: use moved object
- Symptom: The source is assumed to retain resources.
- Diagnostic goal: Use the destination after move or define a valid moved-from state.

### Buggy code

```cpp
auto b = std::move(a); use(a);
```

### Expected diagnosis

Moving transfers ownership and leaves a valid but unspecified source.

### Corrected code

```cpp
auto b = std::move(a); use(b);
```

### Regression tests

```cpp
assert_destination_owns_resource();
```

## ECPP-M-074: dangling view

- Difficulty: Medium
- Language/platform: Embedded C++
- Perspective: Templates
- Concept: dangling view
- Symptom: A view points into a destroyed temporary.
- Diagnostic goal: Return owned storage or extend the source lifetime.

### Buggy code

```cpp
std::string_view name() { return std::string("x"); }
```

### Expected diagnosis

The temporary string dies before the view is used.

### Corrected code

```cpp
std::string name() { return "x"; }
```

### Regression tests

```cpp
assert(name() == "x");
```

## ECPP-M-075: unchecked span length

- Difficulty: Medium
- Language/platform: Embedded C++
- Perspective: Buffers
- Concept: unchecked span length
- Symptom: A peripheral read writes beyond a buffer.
- Diagnostic goal: Pass capacity and validate length before copying.

### Buggy code

```cpp
std::copy(src, src + length, dst.begin());
```

### Expected diagnosis

The source length is not bounded by destination capacity.

### Corrected code

```cpp
if (length > dst.size()) return Error::TooLarge; std::copy_n(src, length, dst.begin());
```

### Regression tests

```cpp
assert_oversized_copy_is_rejected();
```

## ECPP-M-076: data race

- Difficulty: Medium
- Language/platform: Embedded C++
- Perspective: Concurrency
- Concept: data race
- Symptom: A sensor value changes while being read.
- Diagnostic goal: Use an atomic snapshot or lock.

### Buggy code

```cpp
latest = sample;
return latest;
```

### Expected diagnosis

Concurrent read/write of a non-atomic object is undefined behavior.

### Corrected code

```cpp
std::lock_guard lock(mutex); latest = sample;
```

### Regression tests

```cpp
assert_snapshot_is_consistent();
```

## ECPP-M-077: allocation in hot loop

- Difficulty: Medium
- Language/platform: Embedded C++
- Perspective: Timing
- Concept: allocation in hot loop
- Symptom: Control latency has jitter.
- Diagnostic goal: Preallocate and avoid unbounded work in the deadline path.

### Buggy code

```cpp
std::vector<int> values; values.push_back(sample);
```

### Expected diagnosis

Growth may allocate unpredictably during the real-time path.

### Corrected code

```cpp
std::array<int, 64> values; values[count++] = sample;
```

### Regression tests

```cpp
assert_no_allocation_in_control_path();
```

## ECPP-M-078: illegal transition

- Difficulty: Medium
- Language/platform: Embedded C++
- Perspective: State
- Concept: illegal transition
- Symptom: A device enters an unsafe mode.
- Diagnostic goal: Centralize legal state transitions.

### Buggy code

```cpp
state = State::Running;
```

### Expected diagnosis

The assignment ignores the current state and event validity.

### Corrected code

```cpp
if (state == State::Idle && event == Event::Start) state = State::Running; else return Error::InvalidTransition;
```

### Regression tests

```cpp
assert_invalid_transition_rejected();
```

## ECPP-M-079: copying driver handle

- Difficulty: Medium
- Language/platform: Embedded C++
- Perspective: Power
- Concept: copying driver handle
- Symptom: Two objects shut down the same peripheral.
- Diagnostic goal: Make ownership move-only.

### Buggy code

```cpp
Driver a = b;
```

### Expected diagnosis

Copying duplicates exclusive hardware ownership.

### Corrected code

```cpp
Driver a = std::move(b);
```

### Regression tests

```cpp
static_assert(!std::is_copy_constructible_v<Driver>);
```

## ECPP-M-080: ignored expected error

- Difficulty: Medium
- Language/platform: Embedded C++
- Perspective: Fault handling
- Concept: ignored expected error
- Symptom: A disconnected sensor returns stale data.
- Diagnostic goal: Propagate a typed error and choose a safe fallback.

### Buggy code

```cpp
auto value = sensor.read().value();
```

### Expected diagnosis

value() assumes success and can throw or abort.

### Corrected code

```cpp
auto value = sensor.read(); if (!value) return SafeDefault;
```

### Regression tests

```cpp
assert_disconnect_uses_safe_default();
```

## ECPP-M-081: manual peripheral cleanup

- Difficulty: Medium
- Language/platform: Embedded C++
- Perspective: RAII
- Concept: manual peripheral cleanup
- Symptom: An exception leaves a peripheral enabled.
- Diagnostic goal: Bind cleanup to object lifetime.

### Buggy code

```cpp
device.enable();
read();
device.disable();
```

### Expected diagnosis

An exception from read skips disable.

### Corrected code

```cpp
DeviceGuard guard(device);
read();
```

### Regression tests

```cpp
assert_guard_disables_on_exception();
```

## ECPP-M-082: nontrivial ISR object

- Difficulty: Medium
- Language/platform: Embedded C++
- Perspective: Interrupts
- Concept: nontrivial ISR object
- Symptom: The handler allocates or locks.
- Diagnostic goal: Publish a small flag or index only.

### Buggy code

```cpp
void isr() { queue.push(String("edge")); }
```

### Expected diagnosis

Dynamic allocation and locks are unsafe in interrupt context.

### Corrected code

```cpp
volatile uint8_t pending = 1;
```

### Regression tests

```cpp
assert_main_loop_processes_pending();
```

## ECPP-M-083: use moved object

- Difficulty: Medium
- Language/platform: Embedded C++
- Perspective: Move
- Concept: use moved object
- Symptom: The source is assumed to retain resources.
- Diagnostic goal: Use the destination after move or define a valid moved-from state.

### Buggy code

```cpp
auto b = std::move(a); use(a);
```

### Expected diagnosis

Moving transfers ownership and leaves a valid but unspecified source.

### Corrected code

```cpp
auto b = std::move(a); use(b);
```

### Regression tests

```cpp
assert_destination_owns_resource();
```

## ECPP-M-084: dangling view

- Difficulty: Medium
- Language/platform: Embedded C++
- Perspective: Templates
- Concept: dangling view
- Symptom: A view points into a destroyed temporary.
- Diagnostic goal: Return owned storage or extend the source lifetime.

### Buggy code

```cpp
std::string_view name() { return std::string("x"); }
```

### Expected diagnosis

The temporary string dies before the view is used.

### Corrected code

```cpp
std::string name() { return "x"; }
```

### Regression tests

```cpp
assert(name() == "x");
```

## ECPP-M-085: unchecked span length

- Difficulty: Medium
- Language/platform: Embedded C++
- Perspective: Buffers
- Concept: unchecked span length
- Symptom: A peripheral read writes beyond a buffer.
- Diagnostic goal: Pass capacity and validate length before copying.

### Buggy code

```cpp
std::copy(src, src + length, dst.begin());
```

### Expected diagnosis

The source length is not bounded by destination capacity.

### Corrected code

```cpp
if (length > dst.size()) return Error::TooLarge; std::copy_n(src, length, dst.begin());
```

### Regression tests

```cpp
assert_oversized_copy_is_rejected();
```

## ECPP-M-086: data race

- Difficulty: Medium
- Language/platform: Embedded C++
- Perspective: Concurrency
- Concept: data race
- Symptom: A sensor value changes while being read.
- Diagnostic goal: Use an atomic snapshot or lock.

### Buggy code

```cpp
latest = sample;
return latest;
```

### Expected diagnosis

Concurrent read/write of a non-atomic object is undefined behavior.

### Corrected code

```cpp
std::lock_guard lock(mutex); latest = sample;
```

### Regression tests

```cpp
assert_snapshot_is_consistent();
```

## ECPP-M-087: allocation in hot loop

- Difficulty: Medium
- Language/platform: Embedded C++
- Perspective: Timing
- Concept: allocation in hot loop
- Symptom: Control latency has jitter.
- Diagnostic goal: Preallocate and avoid unbounded work in the deadline path.

### Buggy code

```cpp
std::vector<int> values; values.push_back(sample);
```

### Expected diagnosis

Growth may allocate unpredictably during the real-time path.

### Corrected code

```cpp
std::array<int, 64> values; values[count++] = sample;
```

### Regression tests

```cpp
assert_no_allocation_in_control_path();
```

## ECPP-M-088: illegal transition

- Difficulty: Medium
- Language/platform: Embedded C++
- Perspective: State
- Concept: illegal transition
- Symptom: A device enters an unsafe mode.
- Diagnostic goal: Centralize legal state transitions.

### Buggy code

```cpp
state = State::Running;
```

### Expected diagnosis

The assignment ignores the current state and event validity.

### Corrected code

```cpp
if (state == State::Idle && event == Event::Start) state = State::Running; else return Error::InvalidTransition;
```

### Regression tests

```cpp
assert_invalid_transition_rejected();
```

## ECPP-M-089: copying driver handle

- Difficulty: Medium
- Language/platform: Embedded C++
- Perspective: Power
- Concept: copying driver handle
- Symptom: Two objects shut down the same peripheral.
- Diagnostic goal: Make ownership move-only.

### Buggy code

```cpp
Driver a = b;
```

### Expected diagnosis

Copying duplicates exclusive hardware ownership.

### Corrected code

```cpp
Driver a = std::move(b);
```

### Regression tests

```cpp
static_assert(!std::is_copy_constructible_v<Driver>);
```

## ECPP-M-090: ignored expected error

- Difficulty: Medium
- Language/platform: Embedded C++
- Perspective: Fault handling
- Concept: ignored expected error
- Symptom: A disconnected sensor returns stale data.
- Diagnostic goal: Propagate a typed error and choose a safe fallback.

### Buggy code

```cpp
auto value = sensor.read().value();
```

### Expected diagnosis

value() assumes success and can throw or abort.

### Corrected code

```cpp
auto value = sensor.read(); if (!value) return SafeDefault;
```

### Regression tests

```cpp
assert_disconnect_uses_safe_default();
```

## ECPP-M-091: manual peripheral cleanup

- Difficulty: Medium
- Language/platform: Embedded C++
- Perspective: RAII
- Concept: manual peripheral cleanup
- Symptom: An exception leaves a peripheral enabled.
- Diagnostic goal: Bind cleanup to object lifetime.

### Buggy code

```cpp
device.enable();
read();
device.disable();
```

### Expected diagnosis

An exception from read skips disable.

### Corrected code

```cpp
DeviceGuard guard(device);
read();
```

### Regression tests

```cpp
assert_guard_disables_on_exception();
```

## ECPP-M-092: nontrivial ISR object

- Difficulty: Medium
- Language/platform: Embedded C++
- Perspective: Interrupts
- Concept: nontrivial ISR object
- Symptom: The handler allocates or locks.
- Diagnostic goal: Publish a small flag or index only.

### Buggy code

```cpp
void isr() { queue.push(String("edge")); }
```

### Expected diagnosis

Dynamic allocation and locks are unsafe in interrupt context.

### Corrected code

```cpp
volatile uint8_t pending = 1;
```

### Regression tests

```cpp
assert_main_loop_processes_pending();
```

## ECPP-M-093: use moved object

- Difficulty: Medium
- Language/platform: Embedded C++
- Perspective: Move
- Concept: use moved object
- Symptom: The source is assumed to retain resources.
- Diagnostic goal: Use the destination after move or define a valid moved-from state.

### Buggy code

```cpp
auto b = std::move(a); use(a);
```

### Expected diagnosis

Moving transfers ownership and leaves a valid but unspecified source.

### Corrected code

```cpp
auto b = std::move(a); use(b);
```

### Regression tests

```cpp
assert_destination_owns_resource();
```

## ECPP-M-094: dangling view

- Difficulty: Medium
- Language/platform: Embedded C++
- Perspective: Templates
- Concept: dangling view
- Symptom: A view points into a destroyed temporary.
- Diagnostic goal: Return owned storage or extend the source lifetime.

### Buggy code

```cpp
std::string_view name() { return std::string("x"); }
```

### Expected diagnosis

The temporary string dies before the view is used.

### Corrected code

```cpp
std::string name() { return "x"; }
```

### Regression tests

```cpp
assert(name() == "x");
```

## ECPP-M-095: unchecked span length

- Difficulty: Medium
- Language/platform: Embedded C++
- Perspective: Buffers
- Concept: unchecked span length
- Symptom: A peripheral read writes beyond a buffer.
- Diagnostic goal: Pass capacity and validate length before copying.

### Buggy code

```cpp
std::copy(src, src + length, dst.begin());
```

### Expected diagnosis

The source length is not bounded by destination capacity.

### Corrected code

```cpp
if (length > dst.size()) return Error::TooLarge; std::copy_n(src, length, dst.begin());
```

### Regression tests

```cpp
assert_oversized_copy_is_rejected();
```

## ECPP-M-096: data race

- Difficulty: Medium
- Language/platform: Embedded C++
- Perspective: Concurrency
- Concept: data race
- Symptom: A sensor value changes while being read.
- Diagnostic goal: Use an atomic snapshot or lock.

### Buggy code

```cpp
latest = sample;
return latest;
```

### Expected diagnosis

Concurrent read/write of a non-atomic object is undefined behavior.

### Corrected code

```cpp
std::lock_guard lock(mutex); latest = sample;
```

### Regression tests

```cpp
assert_snapshot_is_consistent();
```

## ECPP-M-097: allocation in hot loop

- Difficulty: Medium
- Language/platform: Embedded C++
- Perspective: Timing
- Concept: allocation in hot loop
- Symptom: Control latency has jitter.
- Diagnostic goal: Preallocate and avoid unbounded work in the deadline path.

### Buggy code

```cpp
std::vector<int> values; values.push_back(sample);
```

### Expected diagnosis

Growth may allocate unpredictably during the real-time path.

### Corrected code

```cpp
std::array<int, 64> values; values[count++] = sample;
```

### Regression tests

```cpp
assert_no_allocation_in_control_path();
```

## ECPP-M-098: illegal transition

- Difficulty: Medium
- Language/platform: Embedded C++
- Perspective: State
- Concept: illegal transition
- Symptom: A device enters an unsafe mode.
- Diagnostic goal: Centralize legal state transitions.

### Buggy code

```cpp
state = State::Running;
```

### Expected diagnosis

The assignment ignores the current state and event validity.

### Corrected code

```cpp
if (state == State::Idle && event == Event::Start) state = State::Running; else return Error::InvalidTransition;
```

### Regression tests

```cpp
assert_invalid_transition_rejected();
```

## ECPP-M-099: copying driver handle

- Difficulty: Medium
- Language/platform: Embedded C++
- Perspective: Power
- Concept: copying driver handle
- Symptom: Two objects shut down the same peripheral.
- Diagnostic goal: Make ownership move-only.

### Buggy code

```cpp
Driver a = b;
```

### Expected diagnosis

Copying duplicates exclusive hardware ownership.

### Corrected code

```cpp
Driver a = std::move(b);
```

### Regression tests

```cpp
static_assert(!std::is_copy_constructible_v<Driver>);
```

## ECPP-M-100: ignored expected error

- Difficulty: Medium
- Language/platform: Embedded C++
- Perspective: Fault handling
- Concept: ignored expected error
- Symptom: A disconnected sensor returns stale data.
- Diagnostic goal: Propagate a typed error and choose a safe fallback.

### Buggy code

```cpp
auto value = sensor.read().value();
```

### Expected diagnosis

value() assumes success and can throw or abort.

### Corrected code

```cpp
auto value = sensor.read(); if (!value) return SafeDefault;
```

### Regression tests

```cpp
assert_disconnect_uses_safe_default();
```

## ECPP-H-001: manual peripheral cleanup

- Difficulty: Hard
- Language/platform: Embedded C++
- Perspective: RAII
- Concept: manual peripheral cleanup
- Symptom: An exception leaves a peripheral enabled.
- Diagnostic goal: Bind cleanup to object lifetime.

### Buggy code

```cpp
device.enable();
read();
device.disable();
```

### Expected diagnosis

An exception from read skips disable.

### Corrected code

```cpp
DeviceGuard guard(device);
read();
```

### Regression tests

```cpp
assert_guard_disables_on_exception();
```

## ECPP-H-002: nontrivial ISR object

- Difficulty: Hard
- Language/platform: Embedded C++
- Perspective: Interrupts
- Concept: nontrivial ISR object
- Symptom: The handler allocates or locks.
- Diagnostic goal: Publish a small flag or index only.

### Buggy code

```cpp
void isr() { queue.push(String("edge")); }
```

### Expected diagnosis

Dynamic allocation and locks are unsafe in interrupt context.

### Corrected code

```cpp
volatile uint8_t pending = 1;
```

### Regression tests

```cpp
assert_main_loop_processes_pending();
```

## ECPP-H-003: use moved object

- Difficulty: Hard
- Language/platform: Embedded C++
- Perspective: Move
- Concept: use moved object
- Symptom: The source is assumed to retain resources.
- Diagnostic goal: Use the destination after move or define a valid moved-from state.

### Buggy code

```cpp
auto b = std::move(a); use(a);
```

### Expected diagnosis

Moving transfers ownership and leaves a valid but unspecified source.

### Corrected code

```cpp
auto b = std::move(a); use(b);
```

### Regression tests

```cpp
assert_destination_owns_resource();
```

## ECPP-H-004: dangling view

- Difficulty: Hard
- Language/platform: Embedded C++
- Perspective: Templates
- Concept: dangling view
- Symptom: A view points into a destroyed temporary.
- Diagnostic goal: Return owned storage or extend the source lifetime.

### Buggy code

```cpp
std::string_view name() { return std::string("x"); }
```

### Expected diagnosis

The temporary string dies before the view is used.

### Corrected code

```cpp
std::string name() { return "x"; }
```

### Regression tests

```cpp
assert(name() == "x");
```

## ECPP-H-005: unchecked span length

- Difficulty: Hard
- Language/platform: Embedded C++
- Perspective: Buffers
- Concept: unchecked span length
- Symptom: A peripheral read writes beyond a buffer.
- Diagnostic goal: Pass capacity and validate length before copying.

### Buggy code

```cpp
std::copy(src, src + length, dst.begin());
```

### Expected diagnosis

The source length is not bounded by destination capacity.

### Corrected code

```cpp
if (length > dst.size()) return Error::TooLarge; std::copy_n(src, length, dst.begin());
```

### Regression tests

```cpp
assert_oversized_copy_is_rejected();
```

## ECPP-H-006: data race

- Difficulty: Hard
- Language/platform: Embedded C++
- Perspective: Concurrency
- Concept: data race
- Symptom: A sensor value changes while being read.
- Diagnostic goal: Use an atomic snapshot or lock.

### Buggy code

```cpp
latest = sample;
return latest;
```

### Expected diagnosis

Concurrent read/write of a non-atomic object is undefined behavior.

### Corrected code

```cpp
std::lock_guard lock(mutex); latest = sample;
```

### Regression tests

```cpp
assert_snapshot_is_consistent();
```

## ECPP-H-007: allocation in hot loop

- Difficulty: Hard
- Language/platform: Embedded C++
- Perspective: Timing
- Concept: allocation in hot loop
- Symptom: Control latency has jitter.
- Diagnostic goal: Preallocate and avoid unbounded work in the deadline path.

### Buggy code

```cpp
std::vector<int> values; values.push_back(sample);
```

### Expected diagnosis

Growth may allocate unpredictably during the real-time path.

### Corrected code

```cpp
std::array<int, 64> values; values[count++] = sample;
```

### Regression tests

```cpp
assert_no_allocation_in_control_path();
```

## ECPP-H-008: illegal transition

- Difficulty: Hard
- Language/platform: Embedded C++
- Perspective: State
- Concept: illegal transition
- Symptom: A device enters an unsafe mode.
- Diagnostic goal: Centralize legal state transitions.

### Buggy code

```cpp
state = State::Running;
```

### Expected diagnosis

The assignment ignores the current state and event validity.

### Corrected code

```cpp
if (state == State::Idle && event == Event::Start) state = State::Running; else return Error::InvalidTransition;
```

### Regression tests

```cpp
assert_invalid_transition_rejected();
```

## ECPP-H-009: copying driver handle

- Difficulty: Hard
- Language/platform: Embedded C++
- Perspective: Power
- Concept: copying driver handle
- Symptom: Two objects shut down the same peripheral.
- Diagnostic goal: Make ownership move-only.

### Buggy code

```cpp
Driver a = b;
```

### Expected diagnosis

Copying duplicates exclusive hardware ownership.

### Corrected code

```cpp
Driver a = std::move(b);
```

### Regression tests

```cpp
static_assert(!std::is_copy_constructible_v<Driver>);
```

## ECPP-H-010: ignored expected error

- Difficulty: Hard
- Language/platform: Embedded C++
- Perspective: Fault handling
- Concept: ignored expected error
- Symptom: A disconnected sensor returns stale data.
- Diagnostic goal: Propagate a typed error and choose a safe fallback.

### Buggy code

```cpp
auto value = sensor.read().value();
```

### Expected diagnosis

value() assumes success and can throw or abort.

### Corrected code

```cpp
auto value = sensor.read(); if (!value) return SafeDefault;
```

### Regression tests

```cpp
assert_disconnect_uses_safe_default();
```

## ECPP-H-011: manual peripheral cleanup

- Difficulty: Hard
- Language/platform: Embedded C++
- Perspective: RAII
- Concept: manual peripheral cleanup
- Symptom: An exception leaves a peripheral enabled.
- Diagnostic goal: Bind cleanup to object lifetime.

### Buggy code

```cpp
device.enable();
read();
device.disable();
```

### Expected diagnosis

An exception from read skips disable.

### Corrected code

```cpp
DeviceGuard guard(device);
read();
```

### Regression tests

```cpp
assert_guard_disables_on_exception();
```

## ECPP-H-012: nontrivial ISR object

- Difficulty: Hard
- Language/platform: Embedded C++
- Perspective: Interrupts
- Concept: nontrivial ISR object
- Symptom: The handler allocates or locks.
- Diagnostic goal: Publish a small flag or index only.

### Buggy code

```cpp
void isr() { queue.push(String("edge")); }
```

### Expected diagnosis

Dynamic allocation and locks are unsafe in interrupt context.

### Corrected code

```cpp
volatile uint8_t pending = 1;
```

### Regression tests

```cpp
assert_main_loop_processes_pending();
```

## ECPP-H-013: use moved object

- Difficulty: Hard
- Language/platform: Embedded C++
- Perspective: Move
- Concept: use moved object
- Symptom: The source is assumed to retain resources.
- Diagnostic goal: Use the destination after move or define a valid moved-from state.

### Buggy code

```cpp
auto b = std::move(a); use(a);
```

### Expected diagnosis

Moving transfers ownership and leaves a valid but unspecified source.

### Corrected code

```cpp
auto b = std::move(a); use(b);
```

### Regression tests

```cpp
assert_destination_owns_resource();
```

## ECPP-H-014: dangling view

- Difficulty: Hard
- Language/platform: Embedded C++
- Perspective: Templates
- Concept: dangling view
- Symptom: A view points into a destroyed temporary.
- Diagnostic goal: Return owned storage or extend the source lifetime.

### Buggy code

```cpp
std::string_view name() { return std::string("x"); }
```

### Expected diagnosis

The temporary string dies before the view is used.

### Corrected code

```cpp
std::string name() { return "x"; }
```

### Regression tests

```cpp
assert(name() == "x");
```

## ECPP-H-015: unchecked span length

- Difficulty: Hard
- Language/platform: Embedded C++
- Perspective: Buffers
- Concept: unchecked span length
- Symptom: A peripheral read writes beyond a buffer.
- Diagnostic goal: Pass capacity and validate length before copying.

### Buggy code

```cpp
std::copy(src, src + length, dst.begin());
```

### Expected diagnosis

The source length is not bounded by destination capacity.

### Corrected code

```cpp
if (length > dst.size()) return Error::TooLarge; std::copy_n(src, length, dst.begin());
```

### Regression tests

```cpp
assert_oversized_copy_is_rejected();
```

## ECPP-H-016: data race

- Difficulty: Hard
- Language/platform: Embedded C++
- Perspective: Concurrency
- Concept: data race
- Symptom: A sensor value changes while being read.
- Diagnostic goal: Use an atomic snapshot or lock.

### Buggy code

```cpp
latest = sample;
return latest;
```

### Expected diagnosis

Concurrent read/write of a non-atomic object is undefined behavior.

### Corrected code

```cpp
std::lock_guard lock(mutex); latest = sample;
```

### Regression tests

```cpp
assert_snapshot_is_consistent();
```

## ECPP-H-017: allocation in hot loop

- Difficulty: Hard
- Language/platform: Embedded C++
- Perspective: Timing
- Concept: allocation in hot loop
- Symptom: Control latency has jitter.
- Diagnostic goal: Preallocate and avoid unbounded work in the deadline path.

### Buggy code

```cpp
std::vector<int> values; values.push_back(sample);
```

### Expected diagnosis

Growth may allocate unpredictably during the real-time path.

### Corrected code

```cpp
std::array<int, 64> values; values[count++] = sample;
```

### Regression tests

```cpp
assert_no_allocation_in_control_path();
```

## ECPP-H-018: illegal transition

- Difficulty: Hard
- Language/platform: Embedded C++
- Perspective: State
- Concept: illegal transition
- Symptom: A device enters an unsafe mode.
- Diagnostic goal: Centralize legal state transitions.

### Buggy code

```cpp
state = State::Running;
```

### Expected diagnosis

The assignment ignores the current state and event validity.

### Corrected code

```cpp
if (state == State::Idle && event == Event::Start) state = State::Running; else return Error::InvalidTransition;
```

### Regression tests

```cpp
assert_invalid_transition_rejected();
```

## ECPP-H-019: copying driver handle

- Difficulty: Hard
- Language/platform: Embedded C++
- Perspective: Power
- Concept: copying driver handle
- Symptom: Two objects shut down the same peripheral.
- Diagnostic goal: Make ownership move-only.

### Buggy code

```cpp
Driver a = b;
```

### Expected diagnosis

Copying duplicates exclusive hardware ownership.

### Corrected code

```cpp
Driver a = std::move(b);
```

### Regression tests

```cpp
static_assert(!std::is_copy_constructible_v<Driver>);
```

## ECPP-H-020: ignored expected error

- Difficulty: Hard
- Language/platform: Embedded C++
- Perspective: Fault handling
- Concept: ignored expected error
- Symptom: A disconnected sensor returns stale data.
- Diagnostic goal: Propagate a typed error and choose a safe fallback.

### Buggy code

```cpp
auto value = sensor.read().value();
```

### Expected diagnosis

value() assumes success and can throw or abort.

### Corrected code

```cpp
auto value = sensor.read(); if (!value) return SafeDefault;
```

### Regression tests

```cpp
assert_disconnect_uses_safe_default();
```

## ECPP-H-021: manual peripheral cleanup

- Difficulty: Hard
- Language/platform: Embedded C++
- Perspective: RAII
- Concept: manual peripheral cleanup
- Symptom: An exception leaves a peripheral enabled.
- Diagnostic goal: Bind cleanup to object lifetime.

### Buggy code

```cpp
device.enable();
read();
device.disable();
```

### Expected diagnosis

An exception from read skips disable.

### Corrected code

```cpp
DeviceGuard guard(device);
read();
```

### Regression tests

```cpp
assert_guard_disables_on_exception();
```

## ECPP-H-022: nontrivial ISR object

- Difficulty: Hard
- Language/platform: Embedded C++
- Perspective: Interrupts
- Concept: nontrivial ISR object
- Symptom: The handler allocates or locks.
- Diagnostic goal: Publish a small flag or index only.

### Buggy code

```cpp
void isr() { queue.push(String("edge")); }
```

### Expected diagnosis

Dynamic allocation and locks are unsafe in interrupt context.

### Corrected code

```cpp
volatile uint8_t pending = 1;
```

### Regression tests

```cpp
assert_main_loop_processes_pending();
```

## ECPP-H-023: use moved object

- Difficulty: Hard
- Language/platform: Embedded C++
- Perspective: Move
- Concept: use moved object
- Symptom: The source is assumed to retain resources.
- Diagnostic goal: Use the destination after move or define a valid moved-from state.

### Buggy code

```cpp
auto b = std::move(a); use(a);
```

### Expected diagnosis

Moving transfers ownership and leaves a valid but unspecified source.

### Corrected code

```cpp
auto b = std::move(a); use(b);
```

### Regression tests

```cpp
assert_destination_owns_resource();
```

## ECPP-H-024: dangling view

- Difficulty: Hard
- Language/platform: Embedded C++
- Perspective: Templates
- Concept: dangling view
- Symptom: A view points into a destroyed temporary.
- Diagnostic goal: Return owned storage or extend the source lifetime.

### Buggy code

```cpp
std::string_view name() { return std::string("x"); }
```

### Expected diagnosis

The temporary string dies before the view is used.

### Corrected code

```cpp
std::string name() { return "x"; }
```

### Regression tests

```cpp
assert(name() == "x");
```

## ECPP-H-025: unchecked span length

- Difficulty: Hard
- Language/platform: Embedded C++
- Perspective: Buffers
- Concept: unchecked span length
- Symptom: A peripheral read writes beyond a buffer.
- Diagnostic goal: Pass capacity and validate length before copying.

### Buggy code

```cpp
std::copy(src, src + length, dst.begin());
```

### Expected diagnosis

The source length is not bounded by destination capacity.

### Corrected code

```cpp
if (length > dst.size()) return Error::TooLarge; std::copy_n(src, length, dst.begin());
```

### Regression tests

```cpp
assert_oversized_copy_is_rejected();
```

## ECPP-H-026: data race

- Difficulty: Hard
- Language/platform: Embedded C++
- Perspective: Concurrency
- Concept: data race
- Symptom: A sensor value changes while being read.
- Diagnostic goal: Use an atomic snapshot or lock.

### Buggy code

```cpp
latest = sample;
return latest;
```

### Expected diagnosis

Concurrent read/write of a non-atomic object is undefined behavior.

### Corrected code

```cpp
std::lock_guard lock(mutex); latest = sample;
```

### Regression tests

```cpp
assert_snapshot_is_consistent();
```

## ECPP-H-027: allocation in hot loop

- Difficulty: Hard
- Language/platform: Embedded C++
- Perspective: Timing
- Concept: allocation in hot loop
- Symptom: Control latency has jitter.
- Diagnostic goal: Preallocate and avoid unbounded work in the deadline path.

### Buggy code

```cpp
std::vector<int> values; values.push_back(sample);
```

### Expected diagnosis

Growth may allocate unpredictably during the real-time path.

### Corrected code

```cpp
std::array<int, 64> values; values[count++] = sample;
```

### Regression tests

```cpp
assert_no_allocation_in_control_path();
```

## ECPP-H-028: illegal transition

- Difficulty: Hard
- Language/platform: Embedded C++
- Perspective: State
- Concept: illegal transition
- Symptom: A device enters an unsafe mode.
- Diagnostic goal: Centralize legal state transitions.

### Buggy code

```cpp
state = State::Running;
```

### Expected diagnosis

The assignment ignores the current state and event validity.

### Corrected code

```cpp
if (state == State::Idle && event == Event::Start) state = State::Running; else return Error::InvalidTransition;
```

### Regression tests

```cpp
assert_invalid_transition_rejected();
```

## ECPP-H-029: copying driver handle

- Difficulty: Hard
- Language/platform: Embedded C++
- Perspective: Power
- Concept: copying driver handle
- Symptom: Two objects shut down the same peripheral.
- Diagnostic goal: Make ownership move-only.

### Buggy code

```cpp
Driver a = b;
```

### Expected diagnosis

Copying duplicates exclusive hardware ownership.

### Corrected code

```cpp
Driver a = std::move(b);
```

### Regression tests

```cpp
static_assert(!std::is_copy_constructible_v<Driver>);
```

## ECPP-H-030: ignored expected error

- Difficulty: Hard
- Language/platform: Embedded C++
- Perspective: Fault handling
- Concept: ignored expected error
- Symptom: A disconnected sensor returns stale data.
- Diagnostic goal: Propagate a typed error and choose a safe fallback.

### Buggy code

```cpp
auto value = sensor.read().value();
```

### Expected diagnosis

value() assumes success and can throw or abort.

### Corrected code

```cpp
auto value = sensor.read(); if (!value) return SafeDefault;
```

### Regression tests

```cpp
assert_disconnect_uses_safe_default();
```

## ECPP-H-031: manual peripheral cleanup

- Difficulty: Hard
- Language/platform: Embedded C++
- Perspective: RAII
- Concept: manual peripheral cleanup
- Symptom: An exception leaves a peripheral enabled.
- Diagnostic goal: Bind cleanup to object lifetime.

### Buggy code

```cpp
device.enable();
read();
device.disable();
```

### Expected diagnosis

An exception from read skips disable.

### Corrected code

```cpp
DeviceGuard guard(device);
read();
```

### Regression tests

```cpp
assert_guard_disables_on_exception();
```

## ECPP-H-032: nontrivial ISR object

- Difficulty: Hard
- Language/platform: Embedded C++
- Perspective: Interrupts
- Concept: nontrivial ISR object
- Symptom: The handler allocates or locks.
- Diagnostic goal: Publish a small flag or index only.

### Buggy code

```cpp
void isr() { queue.push(String("edge")); }
```

### Expected diagnosis

Dynamic allocation and locks are unsafe in interrupt context.

### Corrected code

```cpp
volatile uint8_t pending = 1;
```

### Regression tests

```cpp
assert_main_loop_processes_pending();
```

## ECPP-H-033: use moved object

- Difficulty: Hard
- Language/platform: Embedded C++
- Perspective: Move
- Concept: use moved object
- Symptom: The source is assumed to retain resources.
- Diagnostic goal: Use the destination after move or define a valid moved-from state.

### Buggy code

```cpp
auto b = std::move(a); use(a);
```

### Expected diagnosis

Moving transfers ownership and leaves a valid but unspecified source.

### Corrected code

```cpp
auto b = std::move(a); use(b);
```

### Regression tests

```cpp
assert_destination_owns_resource();
```

## ECPP-H-034: dangling view

- Difficulty: Hard
- Language/platform: Embedded C++
- Perspective: Templates
- Concept: dangling view
- Symptom: A view points into a destroyed temporary.
- Diagnostic goal: Return owned storage or extend the source lifetime.

### Buggy code

```cpp
std::string_view name() { return std::string("x"); }
```

### Expected diagnosis

The temporary string dies before the view is used.

### Corrected code

```cpp
std::string name() { return "x"; }
```

### Regression tests

```cpp
assert(name() == "x");
```

## ECPP-H-035: unchecked span length

- Difficulty: Hard
- Language/platform: Embedded C++
- Perspective: Buffers
- Concept: unchecked span length
- Symptom: A peripheral read writes beyond a buffer.
- Diagnostic goal: Pass capacity and validate length before copying.

### Buggy code

```cpp
std::copy(src, src + length, dst.begin());
```

### Expected diagnosis

The source length is not bounded by destination capacity.

### Corrected code

```cpp
if (length > dst.size()) return Error::TooLarge; std::copy_n(src, length, dst.begin());
```

### Regression tests

```cpp
assert_oversized_copy_is_rejected();
```

## ECPP-H-036: data race

- Difficulty: Hard
- Language/platform: Embedded C++
- Perspective: Concurrency
- Concept: data race
- Symptom: A sensor value changes while being read.
- Diagnostic goal: Use an atomic snapshot or lock.

### Buggy code

```cpp
latest = sample;
return latest;
```

### Expected diagnosis

Concurrent read/write of a non-atomic object is undefined behavior.

### Corrected code

```cpp
std::lock_guard lock(mutex); latest = sample;
```

### Regression tests

```cpp
assert_snapshot_is_consistent();
```

## ECPP-H-037: allocation in hot loop

- Difficulty: Hard
- Language/platform: Embedded C++
- Perspective: Timing
- Concept: allocation in hot loop
- Symptom: Control latency has jitter.
- Diagnostic goal: Preallocate and avoid unbounded work in the deadline path.

### Buggy code

```cpp
std::vector<int> values; values.push_back(sample);
```

### Expected diagnosis

Growth may allocate unpredictably during the real-time path.

### Corrected code

```cpp
std::array<int, 64> values; values[count++] = sample;
```

### Regression tests

```cpp
assert_no_allocation_in_control_path();
```

## ECPP-H-038: illegal transition

- Difficulty: Hard
- Language/platform: Embedded C++
- Perspective: State
- Concept: illegal transition
- Symptom: A device enters an unsafe mode.
- Diagnostic goal: Centralize legal state transitions.

### Buggy code

```cpp
state = State::Running;
```

### Expected diagnosis

The assignment ignores the current state and event validity.

### Corrected code

```cpp
if (state == State::Idle && event == Event::Start) state = State::Running; else return Error::InvalidTransition;
```

### Regression tests

```cpp
assert_invalid_transition_rejected();
```

## ECPP-H-039: copying driver handle

- Difficulty: Hard
- Language/platform: Embedded C++
- Perspective: Power
- Concept: copying driver handle
- Symptom: Two objects shut down the same peripheral.
- Diagnostic goal: Make ownership move-only.

### Buggy code

```cpp
Driver a = b;
```

### Expected diagnosis

Copying duplicates exclusive hardware ownership.

### Corrected code

```cpp
Driver a = std::move(b);
```

### Regression tests

```cpp
static_assert(!std::is_copy_constructible_v<Driver>);
```

## ECPP-H-040: ignored expected error

- Difficulty: Hard
- Language/platform: Embedded C++
- Perspective: Fault handling
- Concept: ignored expected error
- Symptom: A disconnected sensor returns stale data.
- Diagnostic goal: Propagate a typed error and choose a safe fallback.

### Buggy code

```cpp
auto value = sensor.read().value();
```

### Expected diagnosis

value() assumes success and can throw or abort.

### Corrected code

```cpp
auto value = sensor.read(); if (!value) return SafeDefault;
```

### Regression tests

```cpp
assert_disconnect_uses_safe_default();
```

## ECPP-H-041: manual peripheral cleanup

- Difficulty: Hard
- Language/platform: Embedded C++
- Perspective: RAII
- Concept: manual peripheral cleanup
- Symptom: An exception leaves a peripheral enabled.
- Diagnostic goal: Bind cleanup to object lifetime.

### Buggy code

```cpp
device.enable();
read();
device.disable();
```

### Expected diagnosis

An exception from read skips disable.

### Corrected code

```cpp
DeviceGuard guard(device);
read();
```

### Regression tests

```cpp
assert_guard_disables_on_exception();
```

## ECPP-H-042: nontrivial ISR object

- Difficulty: Hard
- Language/platform: Embedded C++
- Perspective: Interrupts
- Concept: nontrivial ISR object
- Symptom: The handler allocates or locks.
- Diagnostic goal: Publish a small flag or index only.

### Buggy code

```cpp
void isr() { queue.push(String("edge")); }
```

### Expected diagnosis

Dynamic allocation and locks are unsafe in interrupt context.

### Corrected code

```cpp
volatile uint8_t pending = 1;
```

### Regression tests

```cpp
assert_main_loop_processes_pending();
```

## ECPP-H-043: use moved object

- Difficulty: Hard
- Language/platform: Embedded C++
- Perspective: Move
- Concept: use moved object
- Symptom: The source is assumed to retain resources.
- Diagnostic goal: Use the destination after move or define a valid moved-from state.

### Buggy code

```cpp
auto b = std::move(a); use(a);
```

### Expected diagnosis

Moving transfers ownership and leaves a valid but unspecified source.

### Corrected code

```cpp
auto b = std::move(a); use(b);
```

### Regression tests

```cpp
assert_destination_owns_resource();
```

## ECPP-H-044: dangling view

- Difficulty: Hard
- Language/platform: Embedded C++
- Perspective: Templates
- Concept: dangling view
- Symptom: A view points into a destroyed temporary.
- Diagnostic goal: Return owned storage or extend the source lifetime.

### Buggy code

```cpp
std::string_view name() { return std::string("x"); }
```

### Expected diagnosis

The temporary string dies before the view is used.

### Corrected code

```cpp
std::string name() { return "x"; }
```

### Regression tests

```cpp
assert(name() == "x");
```

## ECPP-H-045: unchecked span length

- Difficulty: Hard
- Language/platform: Embedded C++
- Perspective: Buffers
- Concept: unchecked span length
- Symptom: A peripheral read writes beyond a buffer.
- Diagnostic goal: Pass capacity and validate length before copying.

### Buggy code

```cpp
std::copy(src, src + length, dst.begin());
```

### Expected diagnosis

The source length is not bounded by destination capacity.

### Corrected code

```cpp
if (length > dst.size()) return Error::TooLarge; std::copy_n(src, length, dst.begin());
```

### Regression tests

```cpp
assert_oversized_copy_is_rejected();
```

## ECPP-H-046: data race

- Difficulty: Hard
- Language/platform: Embedded C++
- Perspective: Concurrency
- Concept: data race
- Symptom: A sensor value changes while being read.
- Diagnostic goal: Use an atomic snapshot or lock.

### Buggy code

```cpp
latest = sample;
return latest;
```

### Expected diagnosis

Concurrent read/write of a non-atomic object is undefined behavior.

### Corrected code

```cpp
std::lock_guard lock(mutex); latest = sample;
```

### Regression tests

```cpp
assert_snapshot_is_consistent();
```

## ECPP-H-047: allocation in hot loop

- Difficulty: Hard
- Language/platform: Embedded C++
- Perspective: Timing
- Concept: allocation in hot loop
- Symptom: Control latency has jitter.
- Diagnostic goal: Preallocate and avoid unbounded work in the deadline path.

### Buggy code

```cpp
std::vector<int> values; values.push_back(sample);
```

### Expected diagnosis

Growth may allocate unpredictably during the real-time path.

### Corrected code

```cpp
std::array<int, 64> values; values[count++] = sample;
```

### Regression tests

```cpp
assert_no_allocation_in_control_path();
```

## ECPP-H-048: illegal transition

- Difficulty: Hard
- Language/platform: Embedded C++
- Perspective: State
- Concept: illegal transition
- Symptom: A device enters an unsafe mode.
- Diagnostic goal: Centralize legal state transitions.

### Buggy code

```cpp
state = State::Running;
```

### Expected diagnosis

The assignment ignores the current state and event validity.

### Corrected code

```cpp
if (state == State::Idle && event == Event::Start) state = State::Running; else return Error::InvalidTransition;
```

### Regression tests

```cpp
assert_invalid_transition_rejected();
```

## ECPP-H-049: copying driver handle

- Difficulty: Hard
- Language/platform: Embedded C++
- Perspective: Power
- Concept: copying driver handle
- Symptom: Two objects shut down the same peripheral.
- Diagnostic goal: Make ownership move-only.

### Buggy code

```cpp
Driver a = b;
```

### Expected diagnosis

Copying duplicates exclusive hardware ownership.

### Corrected code

```cpp
Driver a = std::move(b);
```

### Regression tests

```cpp
static_assert(!std::is_copy_constructible_v<Driver>);
```

## ECPP-H-050: ignored expected error

- Difficulty: Hard
- Language/platform: Embedded C++
- Perspective: Fault handling
- Concept: ignored expected error
- Symptom: A disconnected sensor returns stale data.
- Diagnostic goal: Propagate a typed error and choose a safe fallback.

### Buggy code

```cpp
auto value = sensor.read().value();
```

### Expected diagnosis

value() assumes success and can throw or abort.

### Corrected code

```cpp
auto value = sensor.read(); if (!value) return SafeDefault;
```

### Regression tests

```cpp
assert_disconnect_uses_safe_default();
```

## ECPP-H-051: manual peripheral cleanup

- Difficulty: Hard
- Language/platform: Embedded C++
- Perspective: RAII
- Concept: manual peripheral cleanup
- Symptom: An exception leaves a peripheral enabled.
- Diagnostic goal: Bind cleanup to object lifetime.

### Buggy code

```cpp
device.enable();
read();
device.disable();
```

### Expected diagnosis

An exception from read skips disable.

### Corrected code

```cpp
DeviceGuard guard(device);
read();
```

### Regression tests

```cpp
assert_guard_disables_on_exception();
```

## ECPP-H-052: nontrivial ISR object

- Difficulty: Hard
- Language/platform: Embedded C++
- Perspective: Interrupts
- Concept: nontrivial ISR object
- Symptom: The handler allocates or locks.
- Diagnostic goal: Publish a small flag or index only.

### Buggy code

```cpp
void isr() { queue.push(String("edge")); }
```

### Expected diagnosis

Dynamic allocation and locks are unsafe in interrupt context.

### Corrected code

```cpp
volatile uint8_t pending = 1;
```

### Regression tests

```cpp
assert_main_loop_processes_pending();
```

## ECPP-H-053: use moved object

- Difficulty: Hard
- Language/platform: Embedded C++
- Perspective: Move
- Concept: use moved object
- Symptom: The source is assumed to retain resources.
- Diagnostic goal: Use the destination after move or define a valid moved-from state.

### Buggy code

```cpp
auto b = std::move(a); use(a);
```

### Expected diagnosis

Moving transfers ownership and leaves a valid but unspecified source.

### Corrected code

```cpp
auto b = std::move(a); use(b);
```

### Regression tests

```cpp
assert_destination_owns_resource();
```

## ECPP-H-054: dangling view

- Difficulty: Hard
- Language/platform: Embedded C++
- Perspective: Templates
- Concept: dangling view
- Symptom: A view points into a destroyed temporary.
- Diagnostic goal: Return owned storage or extend the source lifetime.

### Buggy code

```cpp
std::string_view name() { return std::string("x"); }
```

### Expected diagnosis

The temporary string dies before the view is used.

### Corrected code

```cpp
std::string name() { return "x"; }
```

### Regression tests

```cpp
assert(name() == "x");
```

## ECPP-H-055: unchecked span length

- Difficulty: Hard
- Language/platform: Embedded C++
- Perspective: Buffers
- Concept: unchecked span length
- Symptom: A peripheral read writes beyond a buffer.
- Diagnostic goal: Pass capacity and validate length before copying.

### Buggy code

```cpp
std::copy(src, src + length, dst.begin());
```

### Expected diagnosis

The source length is not bounded by destination capacity.

### Corrected code

```cpp
if (length > dst.size()) return Error::TooLarge; std::copy_n(src, length, dst.begin());
```

### Regression tests

```cpp
assert_oversized_copy_is_rejected();
```

## ECPP-H-056: data race

- Difficulty: Hard
- Language/platform: Embedded C++
- Perspective: Concurrency
- Concept: data race
- Symptom: A sensor value changes while being read.
- Diagnostic goal: Use an atomic snapshot or lock.

### Buggy code

```cpp
latest = sample;
return latest;
```

### Expected diagnosis

Concurrent read/write of a non-atomic object is undefined behavior.

### Corrected code

```cpp
std::lock_guard lock(mutex); latest = sample;
```

### Regression tests

```cpp
assert_snapshot_is_consistent();
```

## ECPP-H-057: allocation in hot loop

- Difficulty: Hard
- Language/platform: Embedded C++
- Perspective: Timing
- Concept: allocation in hot loop
- Symptom: Control latency has jitter.
- Diagnostic goal: Preallocate and avoid unbounded work in the deadline path.

### Buggy code

```cpp
std::vector<int> values; values.push_back(sample);
```

### Expected diagnosis

Growth may allocate unpredictably during the real-time path.

### Corrected code

```cpp
std::array<int, 64> values; values[count++] = sample;
```

### Regression tests

```cpp
assert_no_allocation_in_control_path();
```

## ECPP-H-058: illegal transition

- Difficulty: Hard
- Language/platform: Embedded C++
- Perspective: State
- Concept: illegal transition
- Symptom: A device enters an unsafe mode.
- Diagnostic goal: Centralize legal state transitions.

### Buggy code

```cpp
state = State::Running;
```

### Expected diagnosis

The assignment ignores the current state and event validity.

### Corrected code

```cpp
if (state == State::Idle && event == Event::Start) state = State::Running; else return Error::InvalidTransition;
```

### Regression tests

```cpp
assert_invalid_transition_rejected();
```

## ECPP-H-059: copying driver handle

- Difficulty: Hard
- Language/platform: Embedded C++
- Perspective: Power
- Concept: copying driver handle
- Symptom: Two objects shut down the same peripheral.
- Diagnostic goal: Make ownership move-only.

### Buggy code

```cpp
Driver a = b;
```

### Expected diagnosis

Copying duplicates exclusive hardware ownership.

### Corrected code

```cpp
Driver a = std::move(b);
```

### Regression tests

```cpp
static_assert(!std::is_copy_constructible_v<Driver>);
```

## ECPP-H-060: ignored expected error

- Difficulty: Hard
- Language/platform: Embedded C++
- Perspective: Fault handling
- Concept: ignored expected error
- Symptom: A disconnected sensor returns stale data.
- Diagnostic goal: Propagate a typed error and choose a safe fallback.

### Buggy code

```cpp
auto value = sensor.read().value();
```

### Expected diagnosis

value() assumes success and can throw or abort.

### Corrected code

```cpp
auto value = sensor.read(); if (!value) return SafeDefault;
```

### Regression tests

```cpp
assert_disconnect_uses_safe_default();
```

## ECPP-H-061: manual peripheral cleanup

- Difficulty: Hard
- Language/platform: Embedded C++
- Perspective: RAII
- Concept: manual peripheral cleanup
- Symptom: An exception leaves a peripheral enabled.
- Diagnostic goal: Bind cleanup to object lifetime.

### Buggy code

```cpp
device.enable();
read();
device.disable();
```

### Expected diagnosis

An exception from read skips disable.

### Corrected code

```cpp
DeviceGuard guard(device);
read();
```

### Regression tests

```cpp
assert_guard_disables_on_exception();
```

## ECPP-H-062: nontrivial ISR object

- Difficulty: Hard
- Language/platform: Embedded C++
- Perspective: Interrupts
- Concept: nontrivial ISR object
- Symptom: The handler allocates or locks.
- Diagnostic goal: Publish a small flag or index only.

### Buggy code

```cpp
void isr() { queue.push(String("edge")); }
```

### Expected diagnosis

Dynamic allocation and locks are unsafe in interrupt context.

### Corrected code

```cpp
volatile uint8_t pending = 1;
```

### Regression tests

```cpp
assert_main_loop_processes_pending();
```

## ECPP-H-063: use moved object

- Difficulty: Hard
- Language/platform: Embedded C++
- Perspective: Move
- Concept: use moved object
- Symptom: The source is assumed to retain resources.
- Diagnostic goal: Use the destination after move or define a valid moved-from state.

### Buggy code

```cpp
auto b = std::move(a); use(a);
```

### Expected diagnosis

Moving transfers ownership and leaves a valid but unspecified source.

### Corrected code

```cpp
auto b = std::move(a); use(b);
```

### Regression tests

```cpp
assert_destination_owns_resource();
```

## ECPP-H-064: dangling view

- Difficulty: Hard
- Language/platform: Embedded C++
- Perspective: Templates
- Concept: dangling view
- Symptom: A view points into a destroyed temporary.
- Diagnostic goal: Return owned storage or extend the source lifetime.

### Buggy code

```cpp
std::string_view name() { return std::string("x"); }
```

### Expected diagnosis

The temporary string dies before the view is used.

### Corrected code

```cpp
std::string name() { return "x"; }
```

### Regression tests

```cpp
assert(name() == "x");
```

## ECPP-H-065: unchecked span length

- Difficulty: Hard
- Language/platform: Embedded C++
- Perspective: Buffers
- Concept: unchecked span length
- Symptom: A peripheral read writes beyond a buffer.
- Diagnostic goal: Pass capacity and validate length before copying.

### Buggy code

```cpp
std::copy(src, src + length, dst.begin());
```

### Expected diagnosis

The source length is not bounded by destination capacity.

### Corrected code

```cpp
if (length > dst.size()) return Error::TooLarge; std::copy_n(src, length, dst.begin());
```

### Regression tests

```cpp
assert_oversized_copy_is_rejected();
```

## ECPP-H-066: data race

- Difficulty: Hard
- Language/platform: Embedded C++
- Perspective: Concurrency
- Concept: data race
- Symptom: A sensor value changes while being read.
- Diagnostic goal: Use an atomic snapshot or lock.

### Buggy code

```cpp
latest = sample;
return latest;
```

### Expected diagnosis

Concurrent read/write of a non-atomic object is undefined behavior.

### Corrected code

```cpp
std::lock_guard lock(mutex); latest = sample;
```

### Regression tests

```cpp
assert_snapshot_is_consistent();
```

## ECPP-H-067: allocation in hot loop

- Difficulty: Hard
- Language/platform: Embedded C++
- Perspective: Timing
- Concept: allocation in hot loop
- Symptom: Control latency has jitter.
- Diagnostic goal: Preallocate and avoid unbounded work in the deadline path.

### Buggy code

```cpp
std::vector<int> values; values.push_back(sample);
```

### Expected diagnosis

Growth may allocate unpredictably during the real-time path.

### Corrected code

```cpp
std::array<int, 64> values; values[count++] = sample;
```

### Regression tests

```cpp
assert_no_allocation_in_control_path();
```

## ECPP-H-068: illegal transition

- Difficulty: Hard
- Language/platform: Embedded C++
- Perspective: State
- Concept: illegal transition
- Symptom: A device enters an unsafe mode.
- Diagnostic goal: Centralize legal state transitions.

### Buggy code

```cpp
state = State::Running;
```

### Expected diagnosis

The assignment ignores the current state and event validity.

### Corrected code

```cpp
if (state == State::Idle && event == Event::Start) state = State::Running; else return Error::InvalidTransition;
```

### Regression tests

```cpp
assert_invalid_transition_rejected();
```

## ECPP-H-069: copying driver handle

- Difficulty: Hard
- Language/platform: Embedded C++
- Perspective: Power
- Concept: copying driver handle
- Symptom: Two objects shut down the same peripheral.
- Diagnostic goal: Make ownership move-only.

### Buggy code

```cpp
Driver a = b;
```

### Expected diagnosis

Copying duplicates exclusive hardware ownership.

### Corrected code

```cpp
Driver a = std::move(b);
```

### Regression tests

```cpp
static_assert(!std::is_copy_constructible_v<Driver>);
```

## ECPP-H-070: ignored expected error

- Difficulty: Hard
- Language/platform: Embedded C++
- Perspective: Fault handling
- Concept: ignored expected error
- Symptom: A disconnected sensor returns stale data.
- Diagnostic goal: Propagate a typed error and choose a safe fallback.

### Buggy code

```cpp
auto value = sensor.read().value();
```

### Expected diagnosis

value() assumes success and can throw or abort.

### Corrected code

```cpp
auto value = sensor.read(); if (!value) return SafeDefault;
```

### Regression tests

```cpp
assert_disconnect_uses_safe_default();
```

## ECPP-H-071: manual peripheral cleanup

- Difficulty: Hard
- Language/platform: Embedded C++
- Perspective: RAII
- Concept: manual peripheral cleanup
- Symptom: An exception leaves a peripheral enabled.
- Diagnostic goal: Bind cleanup to object lifetime.

### Buggy code

```cpp
device.enable();
read();
device.disable();
```

### Expected diagnosis

An exception from read skips disable.

### Corrected code

```cpp
DeviceGuard guard(device);
read();
```

### Regression tests

```cpp
assert_guard_disables_on_exception();
```

## ECPP-H-072: nontrivial ISR object

- Difficulty: Hard
- Language/platform: Embedded C++
- Perspective: Interrupts
- Concept: nontrivial ISR object
- Symptom: The handler allocates or locks.
- Diagnostic goal: Publish a small flag or index only.

### Buggy code

```cpp
void isr() { queue.push(String("edge")); }
```

### Expected diagnosis

Dynamic allocation and locks are unsafe in interrupt context.

### Corrected code

```cpp
volatile uint8_t pending = 1;
```

### Regression tests

```cpp
assert_main_loop_processes_pending();
```

## ECPP-H-073: use moved object

- Difficulty: Hard
- Language/platform: Embedded C++
- Perspective: Move
- Concept: use moved object
- Symptom: The source is assumed to retain resources.
- Diagnostic goal: Use the destination after move or define a valid moved-from state.

### Buggy code

```cpp
auto b = std::move(a); use(a);
```

### Expected diagnosis

Moving transfers ownership and leaves a valid but unspecified source.

### Corrected code

```cpp
auto b = std::move(a); use(b);
```

### Regression tests

```cpp
assert_destination_owns_resource();
```

## ECPP-H-074: dangling view

- Difficulty: Hard
- Language/platform: Embedded C++
- Perspective: Templates
- Concept: dangling view
- Symptom: A view points into a destroyed temporary.
- Diagnostic goal: Return owned storage or extend the source lifetime.

### Buggy code

```cpp
std::string_view name() { return std::string("x"); }
```

### Expected diagnosis

The temporary string dies before the view is used.

### Corrected code

```cpp
std::string name() { return "x"; }
```

### Regression tests

```cpp
assert(name() == "x");
```

## ECPP-H-075: unchecked span length

- Difficulty: Hard
- Language/platform: Embedded C++
- Perspective: Buffers
- Concept: unchecked span length
- Symptom: A peripheral read writes beyond a buffer.
- Diagnostic goal: Pass capacity and validate length before copying.

### Buggy code

```cpp
std::copy(src, src + length, dst.begin());
```

### Expected diagnosis

The source length is not bounded by destination capacity.

### Corrected code

```cpp
if (length > dst.size()) return Error::TooLarge; std::copy_n(src, length, dst.begin());
```

### Regression tests

```cpp
assert_oversized_copy_is_rejected();
```

## ECPP-H-076: data race

- Difficulty: Hard
- Language/platform: Embedded C++
- Perspective: Concurrency
- Concept: data race
- Symptom: A sensor value changes while being read.
- Diagnostic goal: Use an atomic snapshot or lock.

### Buggy code

```cpp
latest = sample;
return latest;
```

### Expected diagnosis

Concurrent read/write of a non-atomic object is undefined behavior.

### Corrected code

```cpp
std::lock_guard lock(mutex); latest = sample;
```

### Regression tests

```cpp
assert_snapshot_is_consistent();
```

## ECPP-H-077: allocation in hot loop

- Difficulty: Hard
- Language/platform: Embedded C++
- Perspective: Timing
- Concept: allocation in hot loop
- Symptom: Control latency has jitter.
- Diagnostic goal: Preallocate and avoid unbounded work in the deadline path.

### Buggy code

```cpp
std::vector<int> values; values.push_back(sample);
```

### Expected diagnosis

Growth may allocate unpredictably during the real-time path.

### Corrected code

```cpp
std::array<int, 64> values; values[count++] = sample;
```

### Regression tests

```cpp
assert_no_allocation_in_control_path();
```

## ECPP-H-078: illegal transition

- Difficulty: Hard
- Language/platform: Embedded C++
- Perspective: State
- Concept: illegal transition
- Symptom: A device enters an unsafe mode.
- Diagnostic goal: Centralize legal state transitions.

### Buggy code

```cpp
state = State::Running;
```

### Expected diagnosis

The assignment ignores the current state and event validity.

### Corrected code

```cpp
if (state == State::Idle && event == Event::Start) state = State::Running; else return Error::InvalidTransition;
```

### Regression tests

```cpp
assert_invalid_transition_rejected();
```

## ECPP-H-079: copying driver handle

- Difficulty: Hard
- Language/platform: Embedded C++
- Perspective: Power
- Concept: copying driver handle
- Symptom: Two objects shut down the same peripheral.
- Diagnostic goal: Make ownership move-only.

### Buggy code

```cpp
Driver a = b;
```

### Expected diagnosis

Copying duplicates exclusive hardware ownership.

### Corrected code

```cpp
Driver a = std::move(b);
```

### Regression tests

```cpp
static_assert(!std::is_copy_constructible_v<Driver>);
```

## ECPP-H-080: ignored expected error

- Difficulty: Hard
- Language/platform: Embedded C++
- Perspective: Fault handling
- Concept: ignored expected error
- Symptom: A disconnected sensor returns stale data.
- Diagnostic goal: Propagate a typed error and choose a safe fallback.

### Buggy code

```cpp
auto value = sensor.read().value();
```

### Expected diagnosis

value() assumes success and can throw or abort.

### Corrected code

```cpp
auto value = sensor.read(); if (!value) return SafeDefault;
```

### Regression tests

```cpp
assert_disconnect_uses_safe_default();
```

## ECPP-H-081: manual peripheral cleanup

- Difficulty: Hard
- Language/platform: Embedded C++
- Perspective: RAII
- Concept: manual peripheral cleanup
- Symptom: An exception leaves a peripheral enabled.
- Diagnostic goal: Bind cleanup to object lifetime.

### Buggy code

```cpp
device.enable();
read();
device.disable();
```

### Expected diagnosis

An exception from read skips disable.

### Corrected code

```cpp
DeviceGuard guard(device);
read();
```

### Regression tests

```cpp
assert_guard_disables_on_exception();
```

## ECPP-H-082: nontrivial ISR object

- Difficulty: Hard
- Language/platform: Embedded C++
- Perspective: Interrupts
- Concept: nontrivial ISR object
- Symptom: The handler allocates or locks.
- Diagnostic goal: Publish a small flag or index only.

### Buggy code

```cpp
void isr() { queue.push(String("edge")); }
```

### Expected diagnosis

Dynamic allocation and locks are unsafe in interrupt context.

### Corrected code

```cpp
volatile uint8_t pending = 1;
```

### Regression tests

```cpp
assert_main_loop_processes_pending();
```

## ECPP-H-083: use moved object

- Difficulty: Hard
- Language/platform: Embedded C++
- Perspective: Move
- Concept: use moved object
- Symptom: The source is assumed to retain resources.
- Diagnostic goal: Use the destination after move or define a valid moved-from state.

### Buggy code

```cpp
auto b = std::move(a); use(a);
```

### Expected diagnosis

Moving transfers ownership and leaves a valid but unspecified source.

### Corrected code

```cpp
auto b = std::move(a); use(b);
```

### Regression tests

```cpp
assert_destination_owns_resource();
```

## ECPP-H-084: dangling view

- Difficulty: Hard
- Language/platform: Embedded C++
- Perspective: Templates
- Concept: dangling view
- Symptom: A view points into a destroyed temporary.
- Diagnostic goal: Return owned storage or extend the source lifetime.

### Buggy code

```cpp
std::string_view name() { return std::string("x"); }
```

### Expected diagnosis

The temporary string dies before the view is used.

### Corrected code

```cpp
std::string name() { return "x"; }
```

### Regression tests

```cpp
assert(name() == "x");
```

## ECPP-H-085: unchecked span length

- Difficulty: Hard
- Language/platform: Embedded C++
- Perspective: Buffers
- Concept: unchecked span length
- Symptom: A peripheral read writes beyond a buffer.
- Diagnostic goal: Pass capacity and validate length before copying.

### Buggy code

```cpp
std::copy(src, src + length, dst.begin());
```

### Expected diagnosis

The source length is not bounded by destination capacity.

### Corrected code

```cpp
if (length > dst.size()) return Error::TooLarge; std::copy_n(src, length, dst.begin());
```

### Regression tests

```cpp
assert_oversized_copy_is_rejected();
```

## ECPP-H-086: data race

- Difficulty: Hard
- Language/platform: Embedded C++
- Perspective: Concurrency
- Concept: data race
- Symptom: A sensor value changes while being read.
- Diagnostic goal: Use an atomic snapshot or lock.

### Buggy code

```cpp
latest = sample;
return latest;
```

### Expected diagnosis

Concurrent read/write of a non-atomic object is undefined behavior.

### Corrected code

```cpp
std::lock_guard lock(mutex); latest = sample;
```

### Regression tests

```cpp
assert_snapshot_is_consistent();
```

## ECPP-H-087: allocation in hot loop

- Difficulty: Hard
- Language/platform: Embedded C++
- Perspective: Timing
- Concept: allocation in hot loop
- Symptom: Control latency has jitter.
- Diagnostic goal: Preallocate and avoid unbounded work in the deadline path.

### Buggy code

```cpp
std::vector<int> values; values.push_back(sample);
```

### Expected diagnosis

Growth may allocate unpredictably during the real-time path.

### Corrected code

```cpp
std::array<int, 64> values; values[count++] = sample;
```

### Regression tests

```cpp
assert_no_allocation_in_control_path();
```

## ECPP-H-088: illegal transition

- Difficulty: Hard
- Language/platform: Embedded C++
- Perspective: State
- Concept: illegal transition
- Symptom: A device enters an unsafe mode.
- Diagnostic goal: Centralize legal state transitions.

### Buggy code

```cpp
state = State::Running;
```

### Expected diagnosis

The assignment ignores the current state and event validity.

### Corrected code

```cpp
if (state == State::Idle && event == Event::Start) state = State::Running; else return Error::InvalidTransition;
```

### Regression tests

```cpp
assert_invalid_transition_rejected();
```

## ECPP-H-089: copying driver handle

- Difficulty: Hard
- Language/platform: Embedded C++
- Perspective: Power
- Concept: copying driver handle
- Symptom: Two objects shut down the same peripheral.
- Diagnostic goal: Make ownership move-only.

### Buggy code

```cpp
Driver a = b;
```

### Expected diagnosis

Copying duplicates exclusive hardware ownership.

### Corrected code

```cpp
Driver a = std::move(b);
```

### Regression tests

```cpp
static_assert(!std::is_copy_constructible_v<Driver>);
```

## ECPP-H-090: ignored expected error

- Difficulty: Hard
- Language/platform: Embedded C++
- Perspective: Fault handling
- Concept: ignored expected error
- Symptom: A disconnected sensor returns stale data.
- Diagnostic goal: Propagate a typed error and choose a safe fallback.

### Buggy code

```cpp
auto value = sensor.read().value();
```

### Expected diagnosis

value() assumes success and can throw or abort.

### Corrected code

```cpp
auto value = sensor.read(); if (!value) return SafeDefault;
```

### Regression tests

```cpp
assert_disconnect_uses_safe_default();
```

## ECPP-H-091: manual peripheral cleanup

- Difficulty: Hard
- Language/platform: Embedded C++
- Perspective: RAII
- Concept: manual peripheral cleanup
- Symptom: An exception leaves a peripheral enabled.
- Diagnostic goal: Bind cleanup to object lifetime.

### Buggy code

```cpp
device.enable();
read();
device.disable();
```

### Expected diagnosis

An exception from read skips disable.

### Corrected code

```cpp
DeviceGuard guard(device);
read();
```

### Regression tests

```cpp
assert_guard_disables_on_exception();
```

## ECPP-H-092: nontrivial ISR object

- Difficulty: Hard
- Language/platform: Embedded C++
- Perspective: Interrupts
- Concept: nontrivial ISR object
- Symptom: The handler allocates or locks.
- Diagnostic goal: Publish a small flag or index only.

### Buggy code

```cpp
void isr() { queue.push(String("edge")); }
```

### Expected diagnosis

Dynamic allocation and locks are unsafe in interrupt context.

### Corrected code

```cpp
volatile uint8_t pending = 1;
```

### Regression tests

```cpp
assert_main_loop_processes_pending();
```

## ECPP-H-093: use moved object

- Difficulty: Hard
- Language/platform: Embedded C++
- Perspective: Move
- Concept: use moved object
- Symptom: The source is assumed to retain resources.
- Diagnostic goal: Use the destination after move or define a valid moved-from state.

### Buggy code

```cpp
auto b = std::move(a); use(a);
```

### Expected diagnosis

Moving transfers ownership and leaves a valid but unspecified source.

### Corrected code

```cpp
auto b = std::move(a); use(b);
```

### Regression tests

```cpp
assert_destination_owns_resource();
```

## ECPP-H-094: dangling view

- Difficulty: Hard
- Language/platform: Embedded C++
- Perspective: Templates
- Concept: dangling view
- Symptom: A view points into a destroyed temporary.
- Diagnostic goal: Return owned storage or extend the source lifetime.

### Buggy code

```cpp
std::string_view name() { return std::string("x"); }
```

### Expected diagnosis

The temporary string dies before the view is used.

### Corrected code

```cpp
std::string name() { return "x"; }
```

### Regression tests

```cpp
assert(name() == "x");
```

## ECPP-H-095: unchecked span length

- Difficulty: Hard
- Language/platform: Embedded C++
- Perspective: Buffers
- Concept: unchecked span length
- Symptom: A peripheral read writes beyond a buffer.
- Diagnostic goal: Pass capacity and validate length before copying.

### Buggy code

```cpp
std::copy(src, src + length, dst.begin());
```

### Expected diagnosis

The source length is not bounded by destination capacity.

### Corrected code

```cpp
if (length > dst.size()) return Error::TooLarge; std::copy_n(src, length, dst.begin());
```

### Regression tests

```cpp
assert_oversized_copy_is_rejected();
```

## ECPP-H-096: data race

- Difficulty: Hard
- Language/platform: Embedded C++
- Perspective: Concurrency
- Concept: data race
- Symptom: A sensor value changes while being read.
- Diagnostic goal: Use an atomic snapshot or lock.

### Buggy code

```cpp
latest = sample;
return latest;
```

### Expected diagnosis

Concurrent read/write of a non-atomic object is undefined behavior.

### Corrected code

```cpp
std::lock_guard lock(mutex); latest = sample;
```

### Regression tests

```cpp
assert_snapshot_is_consistent();
```

## ECPP-H-097: allocation in hot loop

- Difficulty: Hard
- Language/platform: Embedded C++
- Perspective: Timing
- Concept: allocation in hot loop
- Symptom: Control latency has jitter.
- Diagnostic goal: Preallocate and avoid unbounded work in the deadline path.

### Buggy code

```cpp
std::vector<int> values; values.push_back(sample);
```

### Expected diagnosis

Growth may allocate unpredictably during the real-time path.

### Corrected code

```cpp
std::array<int, 64> values; values[count++] = sample;
```

### Regression tests

```cpp
assert_no_allocation_in_control_path();
```

## ECPP-H-098: illegal transition

- Difficulty: Hard
- Language/platform: Embedded C++
- Perspective: State
- Concept: illegal transition
- Symptom: A device enters an unsafe mode.
- Diagnostic goal: Centralize legal state transitions.

### Buggy code

```cpp
state = State::Running;
```

### Expected diagnosis

The assignment ignores the current state and event validity.

### Corrected code

```cpp
if (state == State::Idle && event == Event::Start) state = State::Running; else return Error::InvalidTransition;
```

### Regression tests

```cpp
assert_invalid_transition_rejected();
```

## ECPP-H-099: copying driver handle

- Difficulty: Hard
- Language/platform: Embedded C++
- Perspective: Power
- Concept: copying driver handle
- Symptom: Two objects shut down the same peripheral.
- Diagnostic goal: Make ownership move-only.

### Buggy code

```cpp
Driver a = b;
```

### Expected diagnosis

Copying duplicates exclusive hardware ownership.

### Corrected code

```cpp
Driver a = std::move(b);
```

### Regression tests

```cpp
static_assert(!std::is_copy_constructible_v<Driver>);
```

## ECPP-H-100: ignored expected error

- Difficulty: Hard
- Language/platform: Embedded C++
- Perspective: Fault handling
- Concept: ignored expected error
- Symptom: A disconnected sensor returns stale data.
- Diagnostic goal: Propagate a typed error and choose a safe fallback.

### Buggy code

```cpp
auto value = sensor.read().value();
```

### Expected diagnosis

value() assumes success and can throw or abort.

### Corrected code

```cpp
auto value = sensor.read(); if (!value) return SafeDefault;
```

### Regression tests

```cpp
assert_disconnect_uses_safe_default();
```
