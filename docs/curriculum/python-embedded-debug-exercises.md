# Python for Embedded Systems Debug Exercises

A RAG-training corpus of 300 debugging exercises for MicroPython and CircuitPython. Examples use pure decision functions or small injected interfaces so they can be tested without a board; board APIs and electrical assumptions must be adapted to the target hardware. Corrected code is editorial material and must be stripped from learner-facing challenge responses.

## Coverage

- Easy: 100 exercises
- Medium: 100 exercises
- Hard: 100 exercises
- Perspectives: timing, GPIO, ADC/PWM, UART/I2C, interrupts, memory, debouncing, watchdogs, power, state machines, security boundaries, and testability

## EPY-E-001: blocking delay

- Difficulty: Easy
- Language: Python for Embedded Systems (MicroPython/CircuitPython)
- Perspective: Timing
- Concept: blocking delay
- Symptom: A periodic task misses its interval.
- Diagnostic goal: Use a monotonic clock and account for elapsed work.

### Buggy code

```python
def tick_1(now, last, period):
    if now - last >= period:
        sleep(period)
        return now
    return last
```

### Expected diagnosis

Sleeping for the full period after work accumulates drift and the undefined sleep dependency hides the scheduling contract.

### Corrected code

```python
def tick_1(now, last, period):
    if now - last >= period:
        return now
    return last
```

### Regression tests

```python
assert tick_1(100, 0, 100) == 100
assert tick_1(150, 100, 100) == 100
```

## EPY-E-002: wrong active level

- Difficulty: Easy
- Language: Python for Embedded Systems (MicroPython/CircuitPython)
- Perspective: GPIO boundary
- Concept: wrong active level
- Symptom: An LED or relay behaves inverted.
- Diagnostic goal: Model active-low hardware explicitly.

### Buggy code

```python
def output_2(on):
    return 1 if on else 0
```

### Expected diagnosis

The device is wired active-low, so a logical on state must drive the low electrical level.

### Corrected code

```python
def output_2(on):
    return 0 if on else 1
```

### Regression tests

```python
assert output_2(True) == 0
assert output_2(False) == 1
```

## EPY-E-003: raw value treated as volts

- Difficulty: Easy
- Language: Python for Embedded Systems (MicroPython/CircuitPython)
- Perspective: ADC reasoning
- Concept: raw value treated as volts
- Symptom: The displayed voltage is far too large.
- Diagnostic goal: Separate raw ADC units from calibrated physical units.

### Buggy code

```python
def volts_3(raw):
    return raw
```

### Expected diagnosis

An ADC returns a code, not volts; conversion needs the reference voltage and resolution.

### Corrected code

```python
def volts_3(raw, reference=3.3, maximum=4095):
    return raw * reference / maximum
```

### Regression tests

```python
assert abs(volts_3(4095) - 3.3) < 1e-9
assert volts_3(0) == 0
```

## EPY-E-004: duty-cycle units

- Difficulty: Easy
- Language: Python for Embedded Systems (MicroPython/CircuitPython)
- Perspective: PWM reasoning
- Concept: duty-cycle units
- Symptom: The output is always off or saturated.
- Diagnostic goal: Normalize the public duty-cycle contract before writing hardware units.

### Buggy code

```python
def duty_4(percent):
    return int(percent)
```

### Expected diagnosis

The PWM API expects a different range than the user-facing percentage.

### Corrected code

```python
def duty_4(percent):
    if not 0 <= percent <= 100:
        raise ValueError('percent out of range')
    return round(percent * 65535 / 100)
```

### Regression tests

```python
assert duty_4(0) == 0
assert duty_4(100) == 65535
```

## EPY-E-005: partial frame parsing

- Difficulty: Easy
- Language: Python for Embedded Systems (MicroPython/CircuitPython)
- Perspective: Serial protocol
- Concept: partial frame parsing
- Symptom: A split UART message is decoded incorrectly.
- Diagnostic goal: Buffer bytes until a complete framed message exists.

### Buggy code

```python
def parse_5(buffer):
    start = buffer.find(b'<')
    end = buffer.find(b'>')
    return buffer[start + 1:end], buffer[end + 1:]
```

### Expected diagnosis

A missing terminator produces an incomplete frame and slicing with -1 silently discards data.

### Corrected code

```python
def parse_5(buffer):
    start = buffer.find(b'<')
    if start < 0:
        return None, buffer
    end = buffer.find(b'>', start + 1)
    if end < 0:
        return None, buffer[start:]
    return buffer[start + 1:end], buffer[end + 1:]
```

### Regression tests

```python
assert parse_5(b'<ok>rest') == (b'ok', b'rest')
assert parse_5(b'<ok') == (None, b'<ok')
```

## EPY-E-006: unbounded buffer

- Difficulty: Easy
- Language: Python for Embedded Systems (MicroPython/CircuitPython)
- Perspective: Memory budgeting
- Concept: unbounded buffer
- Symptom: Long-running firmware eventually runs out of RAM.
- Diagnostic goal: Enforce a bounded buffer before appending input.

### Buggy code

```python
def append_6(buffer, chunk):
    buffer += chunk
    return buffer
```

### Expected diagnosis

Accumulating input without a maximum lets noisy or disconnected peers consume all available memory.

### Corrected code

```python
def append_6(buffer, chunk, limit=128):
    buffer += chunk
    if len(buffer) > limit:
        raise ValueError('frame too large')
    return buffer
```

### Regression tests

```python
assert append_6(b'a', b'b') == b'ab'
try: append_6(b'a' * 128, b'b')
except ValueError: pass
else: raise AssertionError
```

## EPY-E-007: level confused with edge

- Difficulty: Easy
- Language: Python for Embedded Systems (MicroPython/CircuitPython)
- Perspective: Debouncing
- Concept: level confused with edge
- Symptom: One button press counts many times.
- Diagnostic goal: Count a transition only after the signal remains stable.

### Buggy code

```python
def pressed_7(level):
    return level
```

### Expected diagnosis

A sampled high level is not a new press; edge detection must compare the current state with the previous stable state.

### Corrected code

```python
def pressed_7(previous, current):
    return not previous and current
```

### Regression tests

```python
assert pressed_7(False, True)
assert not pressed_7(True, True)
```

## EPY-E-008: bytes and text mixed

- Difficulty: Easy
- Language: Python for Embedded Systems (MicroPython/CircuitPython)
- Perspective: Data representation
- Concept: bytes and text mixed
- Symptom: A serial write raises a type error or corrupts data.
- Diagnostic goal: Choose an encoding boundary and keep bytes as bytes on the wire.

### Buggy code

```python
def packet_8(text):
    return b'<' + text + b'>'
```

### Expected diagnosis

Python text strings and byte strings are distinct; concatenating them is invalid.

### Corrected code

```python
def packet_8(text):
    return b'<' + text.encode('ascii') + b'>'
```

### Regression tests

```python
assert packet_8('ok') == b'<ok>'
```

## EPY-E-009: sleep state loses context

- Difficulty: Easy
- Language: Python for Embedded Systems (MicroPython/CircuitPython)
- Perspective: Power state
- Concept: sleep state loses context
- Symptom: The device wakes without knowing why.
- Diagnostic goal: Persist only the minimal wake context in a stable representation.

### Buggy code

```python
def save_9(reason):
    return str(reason)
```

### Expected diagnosis

A string representation is ambiguous and may not survive a reset or schema change.

### Corrected code

```python
def save_9(reason):
    if reason not in ('timer', 'pin'):
        raise ValueError('unknown wake reason')
    return {'reason': reason}
```

### Regression tests

```python
assert save_9('timer') == {'reason': 'timer'}
```

## EPY-E-010: blocking delay

- Difficulty: Easy
- Language: Python for Embedded Systems (MicroPython/CircuitPython)
- Perspective: Timing
- Concept: blocking delay
- Symptom: A periodic task misses its interval.
- Diagnostic goal: Use a monotonic clock and account for elapsed work.

### Buggy code

```python
def tick_10(now, last, period):
    if now - last >= period:
        sleep(period)
        return now
    return last
```

### Expected diagnosis

Sleeping for the full period after work accumulates drift and the undefined sleep dependency hides the scheduling contract.

### Corrected code

```python
def tick_10(now, last, period):
    if now - last >= period:
        return now
    return last
```

### Regression tests

```python
assert tick_10(100, 0, 100) == 100
assert tick_10(150, 100, 100) == 100
```

## EPY-E-011: wrong active level

- Difficulty: Easy
- Language: Python for Embedded Systems (MicroPython/CircuitPython)
- Perspective: GPIO boundary
- Concept: wrong active level
- Symptom: An LED or relay behaves inverted.
- Diagnostic goal: Model active-low hardware explicitly.

### Buggy code

```python
def output_11(on):
    return 1 if on else 0
```

### Expected diagnosis

The device is wired active-low, so a logical on state must drive the low electrical level.

### Corrected code

```python
def output_11(on):
    return 0 if on else 1
```

### Regression tests

```python
assert output_11(True) == 0
assert output_11(False) == 1
```

## EPY-E-012: raw value treated as volts

- Difficulty: Easy
- Language: Python for Embedded Systems (MicroPython/CircuitPython)
- Perspective: ADC reasoning
- Concept: raw value treated as volts
- Symptom: The displayed voltage is far too large.
- Diagnostic goal: Separate raw ADC units from calibrated physical units.

### Buggy code

```python
def volts_12(raw):
    return raw
```

### Expected diagnosis

An ADC returns a code, not volts; conversion needs the reference voltage and resolution.

### Corrected code

```python
def volts_12(raw, reference=3.3, maximum=4095):
    return raw * reference / maximum
```

### Regression tests

```python
assert abs(volts_12(4095) - 3.3) < 1e-9
assert volts_12(0) == 0
```

## EPY-E-013: duty-cycle units

- Difficulty: Easy
- Language: Python for Embedded Systems (MicroPython/CircuitPython)
- Perspective: PWM reasoning
- Concept: duty-cycle units
- Symptom: The output is always off or saturated.
- Diagnostic goal: Normalize the public duty-cycle contract before writing hardware units.

### Buggy code

```python
def duty_13(percent):
    return int(percent)
```

### Expected diagnosis

The PWM API expects a different range than the user-facing percentage.

### Corrected code

```python
def duty_13(percent):
    if not 0 <= percent <= 100:
        raise ValueError('percent out of range')
    return round(percent * 65535 / 100)
```

### Regression tests

```python
assert duty_13(0) == 0
assert duty_13(100) == 65535
```

## EPY-E-014: partial frame parsing

- Difficulty: Easy
- Language: Python for Embedded Systems (MicroPython/CircuitPython)
- Perspective: Serial protocol
- Concept: partial frame parsing
- Symptom: A split UART message is decoded incorrectly.
- Diagnostic goal: Buffer bytes until a complete framed message exists.

### Buggy code

```python
def parse_14(buffer):
    start = buffer.find(b'<')
    end = buffer.find(b'>')
    return buffer[start + 1:end], buffer[end + 1:]
```

### Expected diagnosis

A missing terminator produces an incomplete frame and slicing with -1 silently discards data.

### Corrected code

```python
def parse_14(buffer):
    start = buffer.find(b'<')
    if start < 0:
        return None, buffer
    end = buffer.find(b'>', start + 1)
    if end < 0:
        return None, buffer[start:]
    return buffer[start + 1:end], buffer[end + 1:]
```

### Regression tests

```python
assert parse_14(b'<ok>rest') == (b'ok', b'rest')
assert parse_14(b'<ok') == (None, b'<ok')
```

## EPY-E-015: unbounded buffer

- Difficulty: Easy
- Language: Python for Embedded Systems (MicroPython/CircuitPython)
- Perspective: Memory budgeting
- Concept: unbounded buffer
- Symptom: Long-running firmware eventually runs out of RAM.
- Diagnostic goal: Enforce a bounded buffer before appending input.

### Buggy code

```python
def append_15(buffer, chunk):
    buffer += chunk
    return buffer
```

### Expected diagnosis

Accumulating input without a maximum lets noisy or disconnected peers consume all available memory.

### Corrected code

```python
def append_15(buffer, chunk, limit=128):
    buffer += chunk
    if len(buffer) > limit:
        raise ValueError('frame too large')
    return buffer
```

### Regression tests

```python
assert append_15(b'a', b'b') == b'ab'
try: append_15(b'a' * 128, b'b')
except ValueError: pass
else: raise AssertionError
```

## EPY-E-016: level confused with edge

- Difficulty: Easy
- Language: Python for Embedded Systems (MicroPython/CircuitPython)
- Perspective: Debouncing
- Concept: level confused with edge
- Symptom: One button press counts many times.
- Diagnostic goal: Count a transition only after the signal remains stable.

### Buggy code

```python
def pressed_16(level):
    return level
```

### Expected diagnosis

A sampled high level is not a new press; edge detection must compare the current state with the previous stable state.

### Corrected code

```python
def pressed_16(previous, current):
    return not previous and current
```

### Regression tests

```python
assert pressed_16(False, True)
assert not pressed_16(True, True)
```

## EPY-E-017: bytes and text mixed

- Difficulty: Easy
- Language: Python for Embedded Systems (MicroPython/CircuitPython)
- Perspective: Data representation
- Concept: bytes and text mixed
- Symptom: A serial write raises a type error or corrupts data.
- Diagnostic goal: Choose an encoding boundary and keep bytes as bytes on the wire.

### Buggy code

```python
def packet_17(text):
    return b'<' + text + b'>'
```

### Expected diagnosis

Python text strings and byte strings are distinct; concatenating them is invalid.

### Corrected code

```python
def packet_17(text):
    return b'<' + text.encode('ascii') + b'>'
```

### Regression tests

```python
assert packet_17('ok') == b'<ok>'
```

## EPY-E-018: sleep state loses context

- Difficulty: Easy
- Language: Python for Embedded Systems (MicroPython/CircuitPython)
- Perspective: Power state
- Concept: sleep state loses context
- Symptom: The device wakes without knowing why.
- Diagnostic goal: Persist only the minimal wake context in a stable representation.

### Buggy code

```python
def save_18(reason):
    return str(reason)
```

### Expected diagnosis

A string representation is ambiguous and may not survive a reset or schema change.

### Corrected code

```python
def save_18(reason):
    if reason not in ('timer', 'pin'):
        raise ValueError('unknown wake reason')
    return {'reason': reason}
```

### Regression tests

```python
assert save_18('timer') == {'reason': 'timer'}
```

## EPY-E-019: blocking delay

- Difficulty: Easy
- Language: Python for Embedded Systems (MicroPython/CircuitPython)
- Perspective: Timing
- Concept: blocking delay
- Symptom: A periodic task misses its interval.
- Diagnostic goal: Use a monotonic clock and account for elapsed work.

### Buggy code

```python
def tick_19(now, last, period):
    if now - last >= period:
        sleep(period)
        return now
    return last
```

### Expected diagnosis

Sleeping for the full period after work accumulates drift and the undefined sleep dependency hides the scheduling contract.

### Corrected code

```python
def tick_19(now, last, period):
    if now - last >= period:
        return now
    return last
```

### Regression tests

```python
assert tick_19(100, 0, 100) == 100
assert tick_19(150, 100, 100) == 100
```

## EPY-E-020: wrong active level

- Difficulty: Easy
- Language: Python for Embedded Systems (MicroPython/CircuitPython)
- Perspective: GPIO boundary
- Concept: wrong active level
- Symptom: An LED or relay behaves inverted.
- Diagnostic goal: Model active-low hardware explicitly.

### Buggy code

```python
def output_20(on):
    return 1 if on else 0
```

### Expected diagnosis

The device is wired active-low, so a logical on state must drive the low electrical level.

### Corrected code

```python
def output_20(on):
    return 0 if on else 1
```

### Regression tests

```python
assert output_20(True) == 0
assert output_20(False) == 1
```

## EPY-E-021: raw value treated as volts

- Difficulty: Easy
- Language: Python for Embedded Systems (MicroPython/CircuitPython)
- Perspective: ADC reasoning
- Concept: raw value treated as volts
- Symptom: The displayed voltage is far too large.
- Diagnostic goal: Separate raw ADC units from calibrated physical units.

### Buggy code

```python
def volts_21(raw):
    return raw
```

### Expected diagnosis

An ADC returns a code, not volts; conversion needs the reference voltage and resolution.

### Corrected code

```python
def volts_21(raw, reference=3.3, maximum=4095):
    return raw * reference / maximum
```

### Regression tests

```python
assert abs(volts_21(4095) - 3.3) < 1e-9
assert volts_21(0) == 0
```

## EPY-E-022: duty-cycle units

- Difficulty: Easy
- Language: Python for Embedded Systems (MicroPython/CircuitPython)
- Perspective: PWM reasoning
- Concept: duty-cycle units
- Symptom: The output is always off or saturated.
- Diagnostic goal: Normalize the public duty-cycle contract before writing hardware units.

### Buggy code

```python
def duty_22(percent):
    return int(percent)
```

### Expected diagnosis

The PWM API expects a different range than the user-facing percentage.

### Corrected code

```python
def duty_22(percent):
    if not 0 <= percent <= 100:
        raise ValueError('percent out of range')
    return round(percent * 65535 / 100)
```

### Regression tests

```python
assert duty_22(0) == 0
assert duty_22(100) == 65535
```

## EPY-E-023: partial frame parsing

- Difficulty: Easy
- Language: Python for Embedded Systems (MicroPython/CircuitPython)
- Perspective: Serial protocol
- Concept: partial frame parsing
- Symptom: A split UART message is decoded incorrectly.
- Diagnostic goal: Buffer bytes until a complete framed message exists.

### Buggy code

```python
def parse_23(buffer):
    start = buffer.find(b'<')
    end = buffer.find(b'>')
    return buffer[start + 1:end], buffer[end + 1:]
```

### Expected diagnosis

A missing terminator produces an incomplete frame and slicing with -1 silently discards data.

### Corrected code

```python
def parse_23(buffer):
    start = buffer.find(b'<')
    if start < 0:
        return None, buffer
    end = buffer.find(b'>', start + 1)
    if end < 0:
        return None, buffer[start:]
    return buffer[start + 1:end], buffer[end + 1:]
```

### Regression tests

```python
assert parse_23(b'<ok>rest') == (b'ok', b'rest')
assert parse_23(b'<ok') == (None, b'<ok')
```

## EPY-E-024: unbounded buffer

- Difficulty: Easy
- Language: Python for Embedded Systems (MicroPython/CircuitPython)
- Perspective: Memory budgeting
- Concept: unbounded buffer
- Symptom: Long-running firmware eventually runs out of RAM.
- Diagnostic goal: Enforce a bounded buffer before appending input.

### Buggy code

```python
def append_24(buffer, chunk):
    buffer += chunk
    return buffer
```

### Expected diagnosis

Accumulating input without a maximum lets noisy or disconnected peers consume all available memory.

### Corrected code

```python
def append_24(buffer, chunk, limit=128):
    buffer += chunk
    if len(buffer) > limit:
        raise ValueError('frame too large')
    return buffer
```

### Regression tests

```python
assert append_24(b'a', b'b') == b'ab'
try: append_24(b'a' * 128, b'b')
except ValueError: pass
else: raise AssertionError
```

## EPY-E-025: level confused with edge

- Difficulty: Easy
- Language: Python for Embedded Systems (MicroPython/CircuitPython)
- Perspective: Debouncing
- Concept: level confused with edge
- Symptom: One button press counts many times.
- Diagnostic goal: Count a transition only after the signal remains stable.

### Buggy code

```python
def pressed_25(level):
    return level
```

### Expected diagnosis

A sampled high level is not a new press; edge detection must compare the current state with the previous stable state.

### Corrected code

```python
def pressed_25(previous, current):
    return not previous and current
```

### Regression tests

```python
assert pressed_25(False, True)
assert not pressed_25(True, True)
```

## EPY-E-026: bytes and text mixed

- Difficulty: Easy
- Language: Python for Embedded Systems (MicroPython/CircuitPython)
- Perspective: Data representation
- Concept: bytes and text mixed
- Symptom: A serial write raises a type error or corrupts data.
- Diagnostic goal: Choose an encoding boundary and keep bytes as bytes on the wire.

### Buggy code

```python
def packet_26(text):
    return b'<' + text + b'>'
```

### Expected diagnosis

Python text strings and byte strings are distinct; concatenating them is invalid.

### Corrected code

```python
def packet_26(text):
    return b'<' + text.encode('ascii') + b'>'
```

### Regression tests

```python
assert packet_26('ok') == b'<ok>'
```

## EPY-E-027: sleep state loses context

- Difficulty: Easy
- Language: Python for Embedded Systems (MicroPython/CircuitPython)
- Perspective: Power state
- Concept: sleep state loses context
- Symptom: The device wakes without knowing why.
- Diagnostic goal: Persist only the minimal wake context in a stable representation.

### Buggy code

```python
def save_27(reason):
    return str(reason)
```

### Expected diagnosis

A string representation is ambiguous and may not survive a reset or schema change.

### Corrected code

```python
def save_27(reason):
    if reason not in ('timer', 'pin'):
        raise ValueError('unknown wake reason')
    return {'reason': reason}
```

### Regression tests

```python
assert save_27('timer') == {'reason': 'timer'}
```

## EPY-E-028: blocking delay

- Difficulty: Easy
- Language: Python for Embedded Systems (MicroPython/CircuitPython)
- Perspective: Timing
- Concept: blocking delay
- Symptom: A periodic task misses its interval.
- Diagnostic goal: Use a monotonic clock and account for elapsed work.

### Buggy code

```python
def tick_28(now, last, period):
    if now - last >= period:
        sleep(period)
        return now
    return last
```

### Expected diagnosis

Sleeping for the full period after work accumulates drift and the undefined sleep dependency hides the scheduling contract.

### Corrected code

```python
def tick_28(now, last, period):
    if now - last >= period:
        return now
    return last
```

### Regression tests

```python
assert tick_28(100, 0, 100) == 100
assert tick_28(150, 100, 100) == 100
```

## EPY-E-029: wrong active level

- Difficulty: Easy
- Language: Python for Embedded Systems (MicroPython/CircuitPython)
- Perspective: GPIO boundary
- Concept: wrong active level
- Symptom: An LED or relay behaves inverted.
- Diagnostic goal: Model active-low hardware explicitly.

### Buggy code

```python
def output_29(on):
    return 1 if on else 0
```

### Expected diagnosis

The device is wired active-low, so a logical on state must drive the low electrical level.

### Corrected code

```python
def output_29(on):
    return 0 if on else 1
```

### Regression tests

```python
assert output_29(True) == 0
assert output_29(False) == 1
```

## EPY-E-030: raw value treated as volts

- Difficulty: Easy
- Language: Python for Embedded Systems (MicroPython/CircuitPython)
- Perspective: ADC reasoning
- Concept: raw value treated as volts
- Symptom: The displayed voltage is far too large.
- Diagnostic goal: Separate raw ADC units from calibrated physical units.

### Buggy code

```python
def volts_30(raw):
    return raw
```

### Expected diagnosis

An ADC returns a code, not volts; conversion needs the reference voltage and resolution.

### Corrected code

```python
def volts_30(raw, reference=3.3, maximum=4095):
    return raw * reference / maximum
```

### Regression tests

```python
assert abs(volts_30(4095) - 3.3) < 1e-9
assert volts_30(0) == 0
```

## EPY-E-031: duty-cycle units

- Difficulty: Easy
- Language: Python for Embedded Systems (MicroPython/CircuitPython)
- Perspective: PWM reasoning
- Concept: duty-cycle units
- Symptom: The output is always off or saturated.
- Diagnostic goal: Normalize the public duty-cycle contract before writing hardware units.

### Buggy code

```python
def duty_31(percent):
    return int(percent)
```

### Expected diagnosis

The PWM API expects a different range than the user-facing percentage.

### Corrected code

```python
def duty_31(percent):
    if not 0 <= percent <= 100:
        raise ValueError('percent out of range')
    return round(percent * 65535 / 100)
```

### Regression tests

```python
assert duty_31(0) == 0
assert duty_31(100) == 65535
```

## EPY-E-032: partial frame parsing

- Difficulty: Easy
- Language: Python for Embedded Systems (MicroPython/CircuitPython)
- Perspective: Serial protocol
- Concept: partial frame parsing
- Symptom: A split UART message is decoded incorrectly.
- Diagnostic goal: Buffer bytes until a complete framed message exists.

### Buggy code

```python
def parse_32(buffer):
    start = buffer.find(b'<')
    end = buffer.find(b'>')
    return buffer[start + 1:end], buffer[end + 1:]
```

### Expected diagnosis

A missing terminator produces an incomplete frame and slicing with -1 silently discards data.

### Corrected code

```python
def parse_32(buffer):
    start = buffer.find(b'<')
    if start < 0:
        return None, buffer
    end = buffer.find(b'>', start + 1)
    if end < 0:
        return None, buffer[start:]
    return buffer[start + 1:end], buffer[end + 1:]
```

### Regression tests

```python
assert parse_32(b'<ok>rest') == (b'ok', b'rest')
assert parse_32(b'<ok') == (None, b'<ok')
```

## EPY-E-033: unbounded buffer

- Difficulty: Easy
- Language: Python for Embedded Systems (MicroPython/CircuitPython)
- Perspective: Memory budgeting
- Concept: unbounded buffer
- Symptom: Long-running firmware eventually runs out of RAM.
- Diagnostic goal: Enforce a bounded buffer before appending input.

### Buggy code

```python
def append_33(buffer, chunk):
    buffer += chunk
    return buffer
```

### Expected diagnosis

Accumulating input without a maximum lets noisy or disconnected peers consume all available memory.

### Corrected code

```python
def append_33(buffer, chunk, limit=128):
    buffer += chunk
    if len(buffer) > limit:
        raise ValueError('frame too large')
    return buffer
```

### Regression tests

```python
assert append_33(b'a', b'b') == b'ab'
try: append_33(b'a' * 128, b'b')
except ValueError: pass
else: raise AssertionError
```

## EPY-E-034: level confused with edge

- Difficulty: Easy
- Language: Python for Embedded Systems (MicroPython/CircuitPython)
- Perspective: Debouncing
- Concept: level confused with edge
- Symptom: One button press counts many times.
- Diagnostic goal: Count a transition only after the signal remains stable.

### Buggy code

```python
def pressed_34(level):
    return level
```

### Expected diagnosis

A sampled high level is not a new press; edge detection must compare the current state with the previous stable state.

### Corrected code

```python
def pressed_34(previous, current):
    return not previous and current
```

### Regression tests

```python
assert pressed_34(False, True)
assert not pressed_34(True, True)
```

## EPY-E-035: bytes and text mixed

- Difficulty: Easy
- Language: Python for Embedded Systems (MicroPython/CircuitPython)
- Perspective: Data representation
- Concept: bytes and text mixed
- Symptom: A serial write raises a type error or corrupts data.
- Diagnostic goal: Choose an encoding boundary and keep bytes as bytes on the wire.

### Buggy code

```python
def packet_35(text):
    return b'<' + text + b'>'
```

### Expected diagnosis

Python text strings and byte strings are distinct; concatenating them is invalid.

### Corrected code

```python
def packet_35(text):
    return b'<' + text.encode('ascii') + b'>'
```

### Regression tests

```python
assert packet_35('ok') == b'<ok>'
```

## EPY-E-036: sleep state loses context

- Difficulty: Easy
- Language: Python for Embedded Systems (MicroPython/CircuitPython)
- Perspective: Power state
- Concept: sleep state loses context
- Symptom: The device wakes without knowing why.
- Diagnostic goal: Persist only the minimal wake context in a stable representation.

### Buggy code

```python
def save_36(reason):
    return str(reason)
```

### Expected diagnosis

A string representation is ambiguous and may not survive a reset or schema change.

### Corrected code

```python
def save_36(reason):
    if reason not in ('timer', 'pin'):
        raise ValueError('unknown wake reason')
    return {'reason': reason}
```

### Regression tests

```python
assert save_36('timer') == {'reason': 'timer'}
```

## EPY-E-037: blocking delay

- Difficulty: Easy
- Language: Python for Embedded Systems (MicroPython/CircuitPython)
- Perspective: Timing
- Concept: blocking delay
- Symptom: A periodic task misses its interval.
- Diagnostic goal: Use a monotonic clock and account for elapsed work.

### Buggy code

```python
def tick_37(now, last, period):
    if now - last >= period:
        sleep(period)
        return now
    return last
```

### Expected diagnosis

Sleeping for the full period after work accumulates drift and the undefined sleep dependency hides the scheduling contract.

### Corrected code

```python
def tick_37(now, last, period):
    if now - last >= period:
        return now
    return last
```

### Regression tests

```python
assert tick_37(100, 0, 100) == 100
assert tick_37(150, 100, 100) == 100
```

## EPY-E-038: wrong active level

- Difficulty: Easy
- Language: Python for Embedded Systems (MicroPython/CircuitPython)
- Perspective: GPIO boundary
- Concept: wrong active level
- Symptom: An LED or relay behaves inverted.
- Diagnostic goal: Model active-low hardware explicitly.

### Buggy code

```python
def output_38(on):
    return 1 if on else 0
```

### Expected diagnosis

The device is wired active-low, so a logical on state must drive the low electrical level.

### Corrected code

```python
def output_38(on):
    return 0 if on else 1
```

### Regression tests

```python
assert output_38(True) == 0
assert output_38(False) == 1
```

## EPY-E-039: raw value treated as volts

- Difficulty: Easy
- Language: Python for Embedded Systems (MicroPython/CircuitPython)
- Perspective: ADC reasoning
- Concept: raw value treated as volts
- Symptom: The displayed voltage is far too large.
- Diagnostic goal: Separate raw ADC units from calibrated physical units.

### Buggy code

```python
def volts_39(raw):
    return raw
```

### Expected diagnosis

An ADC returns a code, not volts; conversion needs the reference voltage and resolution.

### Corrected code

```python
def volts_39(raw, reference=3.3, maximum=4095):
    return raw * reference / maximum
```

### Regression tests

```python
assert abs(volts_39(4095) - 3.3) < 1e-9
assert volts_39(0) == 0
```

## EPY-E-040: duty-cycle units

- Difficulty: Easy
- Language: Python for Embedded Systems (MicroPython/CircuitPython)
- Perspective: PWM reasoning
- Concept: duty-cycle units
- Symptom: The output is always off or saturated.
- Diagnostic goal: Normalize the public duty-cycle contract before writing hardware units.

### Buggy code

```python
def duty_40(percent):
    return int(percent)
```

### Expected diagnosis

The PWM API expects a different range than the user-facing percentage.

### Corrected code

```python
def duty_40(percent):
    if not 0 <= percent <= 100:
        raise ValueError('percent out of range')
    return round(percent * 65535 / 100)
```

### Regression tests

```python
assert duty_40(0) == 0
assert duty_40(100) == 65535
```

## EPY-E-041: partial frame parsing

- Difficulty: Easy
- Language: Python for Embedded Systems (MicroPython/CircuitPython)
- Perspective: Serial protocol
- Concept: partial frame parsing
- Symptom: A split UART message is decoded incorrectly.
- Diagnostic goal: Buffer bytes until a complete framed message exists.

### Buggy code

```python
def parse_41(buffer):
    start = buffer.find(b'<')
    end = buffer.find(b'>')
    return buffer[start + 1:end], buffer[end + 1:]
```

### Expected diagnosis

A missing terminator produces an incomplete frame and slicing with -1 silently discards data.

### Corrected code

```python
def parse_41(buffer):
    start = buffer.find(b'<')
    if start < 0:
        return None, buffer
    end = buffer.find(b'>', start + 1)
    if end < 0:
        return None, buffer[start:]
    return buffer[start + 1:end], buffer[end + 1:]
```

### Regression tests

```python
assert parse_41(b'<ok>rest') == (b'ok', b'rest')
assert parse_41(b'<ok') == (None, b'<ok')
```

## EPY-E-042: unbounded buffer

- Difficulty: Easy
- Language: Python for Embedded Systems (MicroPython/CircuitPython)
- Perspective: Memory budgeting
- Concept: unbounded buffer
- Symptom: Long-running firmware eventually runs out of RAM.
- Diagnostic goal: Enforce a bounded buffer before appending input.

### Buggy code

```python
def append_42(buffer, chunk):
    buffer += chunk
    return buffer
```

### Expected diagnosis

Accumulating input without a maximum lets noisy or disconnected peers consume all available memory.

### Corrected code

```python
def append_42(buffer, chunk, limit=128):
    buffer += chunk
    if len(buffer) > limit:
        raise ValueError('frame too large')
    return buffer
```

### Regression tests

```python
assert append_42(b'a', b'b') == b'ab'
try: append_42(b'a' * 128, b'b')
except ValueError: pass
else: raise AssertionError
```

## EPY-E-043: level confused with edge

- Difficulty: Easy
- Language: Python for Embedded Systems (MicroPython/CircuitPython)
- Perspective: Debouncing
- Concept: level confused with edge
- Symptom: One button press counts many times.
- Diagnostic goal: Count a transition only after the signal remains stable.

### Buggy code

```python
def pressed_43(level):
    return level
```

### Expected diagnosis

A sampled high level is not a new press; edge detection must compare the current state with the previous stable state.

### Corrected code

```python
def pressed_43(previous, current):
    return not previous and current
```

### Regression tests

```python
assert pressed_43(False, True)
assert not pressed_43(True, True)
```

## EPY-E-044: bytes and text mixed

- Difficulty: Easy
- Language: Python for Embedded Systems (MicroPython/CircuitPython)
- Perspective: Data representation
- Concept: bytes and text mixed
- Symptom: A serial write raises a type error or corrupts data.
- Diagnostic goal: Choose an encoding boundary and keep bytes as bytes on the wire.

### Buggy code

```python
def packet_44(text):
    return b'<' + text + b'>'
```

### Expected diagnosis

Python text strings and byte strings are distinct; concatenating them is invalid.

### Corrected code

```python
def packet_44(text):
    return b'<' + text.encode('ascii') + b'>'
```

### Regression tests

```python
assert packet_44('ok') == b'<ok>'
```

## EPY-E-045: sleep state loses context

- Difficulty: Easy
- Language: Python for Embedded Systems (MicroPython/CircuitPython)
- Perspective: Power state
- Concept: sleep state loses context
- Symptom: The device wakes without knowing why.
- Diagnostic goal: Persist only the minimal wake context in a stable representation.

### Buggy code

```python
def save_45(reason):
    return str(reason)
```

### Expected diagnosis

A string representation is ambiguous and may not survive a reset or schema change.

### Corrected code

```python
def save_45(reason):
    if reason not in ('timer', 'pin'):
        raise ValueError('unknown wake reason')
    return {'reason': reason}
```

### Regression tests

```python
assert save_45('timer') == {'reason': 'timer'}
```

## EPY-E-046: blocking delay

- Difficulty: Easy
- Language: Python for Embedded Systems (MicroPython/CircuitPython)
- Perspective: Timing
- Concept: blocking delay
- Symptom: A periodic task misses its interval.
- Diagnostic goal: Use a monotonic clock and account for elapsed work.

### Buggy code

```python
def tick_46(now, last, period):
    if now - last >= period:
        sleep(period)
        return now
    return last
```

### Expected diagnosis

Sleeping for the full period after work accumulates drift and the undefined sleep dependency hides the scheduling contract.

### Corrected code

```python
def tick_46(now, last, period):
    if now - last >= period:
        return now
    return last
```

### Regression tests

```python
assert tick_46(100, 0, 100) == 100
assert tick_46(150, 100, 100) == 100
```

## EPY-E-047: wrong active level

- Difficulty: Easy
- Language: Python for Embedded Systems (MicroPython/CircuitPython)
- Perspective: GPIO boundary
- Concept: wrong active level
- Symptom: An LED or relay behaves inverted.
- Diagnostic goal: Model active-low hardware explicitly.

### Buggy code

```python
def output_47(on):
    return 1 if on else 0
```

### Expected diagnosis

The device is wired active-low, so a logical on state must drive the low electrical level.

### Corrected code

```python
def output_47(on):
    return 0 if on else 1
```

### Regression tests

```python
assert output_47(True) == 0
assert output_47(False) == 1
```

## EPY-E-048: raw value treated as volts

- Difficulty: Easy
- Language: Python for Embedded Systems (MicroPython/CircuitPython)
- Perspective: ADC reasoning
- Concept: raw value treated as volts
- Symptom: The displayed voltage is far too large.
- Diagnostic goal: Separate raw ADC units from calibrated physical units.

### Buggy code

```python
def volts_48(raw):
    return raw
```

### Expected diagnosis

An ADC returns a code, not volts; conversion needs the reference voltage and resolution.

### Corrected code

```python
def volts_48(raw, reference=3.3, maximum=4095):
    return raw * reference / maximum
```

### Regression tests

```python
assert abs(volts_48(4095) - 3.3) < 1e-9
assert volts_48(0) == 0
```

## EPY-E-049: duty-cycle units

- Difficulty: Easy
- Language: Python for Embedded Systems (MicroPython/CircuitPython)
- Perspective: PWM reasoning
- Concept: duty-cycle units
- Symptom: The output is always off or saturated.
- Diagnostic goal: Normalize the public duty-cycle contract before writing hardware units.

### Buggy code

```python
def duty_49(percent):
    return int(percent)
```

### Expected diagnosis

The PWM API expects a different range than the user-facing percentage.

### Corrected code

```python
def duty_49(percent):
    if not 0 <= percent <= 100:
        raise ValueError('percent out of range')
    return round(percent * 65535 / 100)
```

### Regression tests

```python
assert duty_49(0) == 0
assert duty_49(100) == 65535
```

## EPY-E-050: partial frame parsing

- Difficulty: Easy
- Language: Python for Embedded Systems (MicroPython/CircuitPython)
- Perspective: Serial protocol
- Concept: partial frame parsing
- Symptom: A split UART message is decoded incorrectly.
- Diagnostic goal: Buffer bytes until a complete framed message exists.

### Buggy code

```python
def parse_50(buffer):
    start = buffer.find(b'<')
    end = buffer.find(b'>')
    return buffer[start + 1:end], buffer[end + 1:]
```

### Expected diagnosis

A missing terminator produces an incomplete frame and slicing with -1 silently discards data.

### Corrected code

```python
def parse_50(buffer):
    start = buffer.find(b'<')
    if start < 0:
        return None, buffer
    end = buffer.find(b'>', start + 1)
    if end < 0:
        return None, buffer[start:]
    return buffer[start + 1:end], buffer[end + 1:]
```

### Regression tests

```python
assert parse_50(b'<ok>rest') == (b'ok', b'rest')
assert parse_50(b'<ok') == (None, b'<ok')
```

## EPY-E-051: unbounded buffer

- Difficulty: Easy
- Language: Python for Embedded Systems (MicroPython/CircuitPython)
- Perspective: Memory budgeting
- Concept: unbounded buffer
- Symptom: Long-running firmware eventually runs out of RAM.
- Diagnostic goal: Enforce a bounded buffer before appending input.

### Buggy code

```python
def append_51(buffer, chunk):
    buffer += chunk
    return buffer
```

### Expected diagnosis

Accumulating input without a maximum lets noisy or disconnected peers consume all available memory.

### Corrected code

```python
def append_51(buffer, chunk, limit=128):
    buffer += chunk
    if len(buffer) > limit:
        raise ValueError('frame too large')
    return buffer
```

### Regression tests

```python
assert append_51(b'a', b'b') == b'ab'
try: append_51(b'a' * 128, b'b')
except ValueError: pass
else: raise AssertionError
```

## EPY-E-052: level confused with edge

- Difficulty: Easy
- Language: Python for Embedded Systems (MicroPython/CircuitPython)
- Perspective: Debouncing
- Concept: level confused with edge
- Symptom: One button press counts many times.
- Diagnostic goal: Count a transition only after the signal remains stable.

### Buggy code

```python
def pressed_52(level):
    return level
```

### Expected diagnosis

A sampled high level is not a new press; edge detection must compare the current state with the previous stable state.

### Corrected code

```python
def pressed_52(previous, current):
    return not previous and current
```

### Regression tests

```python
assert pressed_52(False, True)
assert not pressed_52(True, True)
```

## EPY-E-053: bytes and text mixed

- Difficulty: Easy
- Language: Python for Embedded Systems (MicroPython/CircuitPython)
- Perspective: Data representation
- Concept: bytes and text mixed
- Symptom: A serial write raises a type error or corrupts data.
- Diagnostic goal: Choose an encoding boundary and keep bytes as bytes on the wire.

### Buggy code

```python
def packet_53(text):
    return b'<' + text + b'>'
```

### Expected diagnosis

Python text strings and byte strings are distinct; concatenating them is invalid.

### Corrected code

```python
def packet_53(text):
    return b'<' + text.encode('ascii') + b'>'
```

### Regression tests

```python
assert packet_53('ok') == b'<ok>'
```

## EPY-E-054: sleep state loses context

- Difficulty: Easy
- Language: Python for Embedded Systems (MicroPython/CircuitPython)
- Perspective: Power state
- Concept: sleep state loses context
- Symptom: The device wakes without knowing why.
- Diagnostic goal: Persist only the minimal wake context in a stable representation.

### Buggy code

```python
def save_54(reason):
    return str(reason)
```

### Expected diagnosis

A string representation is ambiguous and may not survive a reset or schema change.

### Corrected code

```python
def save_54(reason):
    if reason not in ('timer', 'pin'):
        raise ValueError('unknown wake reason')
    return {'reason': reason}
```

### Regression tests

```python
assert save_54('timer') == {'reason': 'timer'}
```

## EPY-E-055: blocking delay

- Difficulty: Easy
- Language: Python for Embedded Systems (MicroPython/CircuitPython)
- Perspective: Timing
- Concept: blocking delay
- Symptom: A periodic task misses its interval.
- Diagnostic goal: Use a monotonic clock and account for elapsed work.

### Buggy code

```python
def tick_55(now, last, period):
    if now - last >= period:
        sleep(period)
        return now
    return last
```

### Expected diagnosis

Sleeping for the full period after work accumulates drift and the undefined sleep dependency hides the scheduling contract.

### Corrected code

```python
def tick_55(now, last, period):
    if now - last >= period:
        return now
    return last
```

### Regression tests

```python
assert tick_55(100, 0, 100) == 100
assert tick_55(150, 100, 100) == 100
```

## EPY-E-056: wrong active level

- Difficulty: Easy
- Language: Python for Embedded Systems (MicroPython/CircuitPython)
- Perspective: GPIO boundary
- Concept: wrong active level
- Symptom: An LED or relay behaves inverted.
- Diagnostic goal: Model active-low hardware explicitly.

### Buggy code

```python
def output_56(on):
    return 1 if on else 0
```

### Expected diagnosis

The device is wired active-low, so a logical on state must drive the low electrical level.

### Corrected code

```python
def output_56(on):
    return 0 if on else 1
```

### Regression tests

```python
assert output_56(True) == 0
assert output_56(False) == 1
```

## EPY-E-057: raw value treated as volts

- Difficulty: Easy
- Language: Python for Embedded Systems (MicroPython/CircuitPython)
- Perspective: ADC reasoning
- Concept: raw value treated as volts
- Symptom: The displayed voltage is far too large.
- Diagnostic goal: Separate raw ADC units from calibrated physical units.

### Buggy code

```python
def volts_57(raw):
    return raw
```

### Expected diagnosis

An ADC returns a code, not volts; conversion needs the reference voltage and resolution.

### Corrected code

```python
def volts_57(raw, reference=3.3, maximum=4095):
    return raw * reference / maximum
```

### Regression tests

```python
assert abs(volts_57(4095) - 3.3) < 1e-9
assert volts_57(0) == 0
```

## EPY-E-058: duty-cycle units

- Difficulty: Easy
- Language: Python for Embedded Systems (MicroPython/CircuitPython)
- Perspective: PWM reasoning
- Concept: duty-cycle units
- Symptom: The output is always off or saturated.
- Diagnostic goal: Normalize the public duty-cycle contract before writing hardware units.

### Buggy code

```python
def duty_58(percent):
    return int(percent)
```

### Expected diagnosis

The PWM API expects a different range than the user-facing percentage.

### Corrected code

```python
def duty_58(percent):
    if not 0 <= percent <= 100:
        raise ValueError('percent out of range')
    return round(percent * 65535 / 100)
```

### Regression tests

```python
assert duty_58(0) == 0
assert duty_58(100) == 65535
```

## EPY-E-059: partial frame parsing

- Difficulty: Easy
- Language: Python for Embedded Systems (MicroPython/CircuitPython)
- Perspective: Serial protocol
- Concept: partial frame parsing
- Symptom: A split UART message is decoded incorrectly.
- Diagnostic goal: Buffer bytes until a complete framed message exists.

### Buggy code

```python
def parse_59(buffer):
    start = buffer.find(b'<')
    end = buffer.find(b'>')
    return buffer[start + 1:end], buffer[end + 1:]
```

### Expected diagnosis

A missing terminator produces an incomplete frame and slicing with -1 silently discards data.

### Corrected code

```python
def parse_59(buffer):
    start = buffer.find(b'<')
    if start < 0:
        return None, buffer
    end = buffer.find(b'>', start + 1)
    if end < 0:
        return None, buffer[start:]
    return buffer[start + 1:end], buffer[end + 1:]
```

### Regression tests

```python
assert parse_59(b'<ok>rest') == (b'ok', b'rest')
assert parse_59(b'<ok') == (None, b'<ok')
```

## EPY-E-060: unbounded buffer

- Difficulty: Easy
- Language: Python for Embedded Systems (MicroPython/CircuitPython)
- Perspective: Memory budgeting
- Concept: unbounded buffer
- Symptom: Long-running firmware eventually runs out of RAM.
- Diagnostic goal: Enforce a bounded buffer before appending input.

### Buggy code

```python
def append_60(buffer, chunk):
    buffer += chunk
    return buffer
```

### Expected diagnosis

Accumulating input without a maximum lets noisy or disconnected peers consume all available memory.

### Corrected code

```python
def append_60(buffer, chunk, limit=128):
    buffer += chunk
    if len(buffer) > limit:
        raise ValueError('frame too large')
    return buffer
```

### Regression tests

```python
assert append_60(b'a', b'b') == b'ab'
try: append_60(b'a' * 128, b'b')
except ValueError: pass
else: raise AssertionError
```

## EPY-E-061: level confused with edge

- Difficulty: Easy
- Language: Python for Embedded Systems (MicroPython/CircuitPython)
- Perspective: Debouncing
- Concept: level confused with edge
- Symptom: One button press counts many times.
- Diagnostic goal: Count a transition only after the signal remains stable.

### Buggy code

```python
def pressed_61(level):
    return level
```

### Expected diagnosis

A sampled high level is not a new press; edge detection must compare the current state with the previous stable state.

### Corrected code

```python
def pressed_61(previous, current):
    return not previous and current
```

### Regression tests

```python
assert pressed_61(False, True)
assert not pressed_61(True, True)
```

## EPY-E-062: bytes and text mixed

- Difficulty: Easy
- Language: Python for Embedded Systems (MicroPython/CircuitPython)
- Perspective: Data representation
- Concept: bytes and text mixed
- Symptom: A serial write raises a type error or corrupts data.
- Diagnostic goal: Choose an encoding boundary and keep bytes as bytes on the wire.

### Buggy code

```python
def packet_62(text):
    return b'<' + text + b'>'
```

### Expected diagnosis

Python text strings and byte strings are distinct; concatenating them is invalid.

### Corrected code

```python
def packet_62(text):
    return b'<' + text.encode('ascii') + b'>'
```

### Regression tests

```python
assert packet_62('ok') == b'<ok>'
```

## EPY-E-063: sleep state loses context

- Difficulty: Easy
- Language: Python for Embedded Systems (MicroPython/CircuitPython)
- Perspective: Power state
- Concept: sleep state loses context
- Symptom: The device wakes without knowing why.
- Diagnostic goal: Persist only the minimal wake context in a stable representation.

### Buggy code

```python
def save_63(reason):
    return str(reason)
```

### Expected diagnosis

A string representation is ambiguous and may not survive a reset or schema change.

### Corrected code

```python
def save_63(reason):
    if reason not in ('timer', 'pin'):
        raise ValueError('unknown wake reason')
    return {'reason': reason}
```

### Regression tests

```python
assert save_63('timer') == {'reason': 'timer'}
```

## EPY-E-064: blocking delay

- Difficulty: Easy
- Language: Python for Embedded Systems (MicroPython/CircuitPython)
- Perspective: Timing
- Concept: blocking delay
- Symptom: A periodic task misses its interval.
- Diagnostic goal: Use a monotonic clock and account for elapsed work.

### Buggy code

```python
def tick_64(now, last, period):
    if now - last >= period:
        sleep(period)
        return now
    return last
```

### Expected diagnosis

Sleeping for the full period after work accumulates drift and the undefined sleep dependency hides the scheduling contract.

### Corrected code

```python
def tick_64(now, last, period):
    if now - last >= period:
        return now
    return last
```

### Regression tests

```python
assert tick_64(100, 0, 100) == 100
assert tick_64(150, 100, 100) == 100
```

## EPY-E-065: wrong active level

- Difficulty: Easy
- Language: Python for Embedded Systems (MicroPython/CircuitPython)
- Perspective: GPIO boundary
- Concept: wrong active level
- Symptom: An LED or relay behaves inverted.
- Diagnostic goal: Model active-low hardware explicitly.

### Buggy code

```python
def output_65(on):
    return 1 if on else 0
```

### Expected diagnosis

The device is wired active-low, so a logical on state must drive the low electrical level.

### Corrected code

```python
def output_65(on):
    return 0 if on else 1
```

### Regression tests

```python
assert output_65(True) == 0
assert output_65(False) == 1
```

## EPY-E-066: raw value treated as volts

- Difficulty: Easy
- Language: Python for Embedded Systems (MicroPython/CircuitPython)
- Perspective: ADC reasoning
- Concept: raw value treated as volts
- Symptom: The displayed voltage is far too large.
- Diagnostic goal: Separate raw ADC units from calibrated physical units.

### Buggy code

```python
def volts_66(raw):
    return raw
```

### Expected diagnosis

An ADC returns a code, not volts; conversion needs the reference voltage and resolution.

### Corrected code

```python
def volts_66(raw, reference=3.3, maximum=4095):
    return raw * reference / maximum
```

### Regression tests

```python
assert abs(volts_66(4095) - 3.3) < 1e-9
assert volts_66(0) == 0
```

## EPY-E-067: duty-cycle units

- Difficulty: Easy
- Language: Python for Embedded Systems (MicroPython/CircuitPython)
- Perspective: PWM reasoning
- Concept: duty-cycle units
- Symptom: The output is always off or saturated.
- Diagnostic goal: Normalize the public duty-cycle contract before writing hardware units.

### Buggy code

```python
def duty_67(percent):
    return int(percent)
```

### Expected diagnosis

The PWM API expects a different range than the user-facing percentage.

### Corrected code

```python
def duty_67(percent):
    if not 0 <= percent <= 100:
        raise ValueError('percent out of range')
    return round(percent * 65535 / 100)
```

### Regression tests

```python
assert duty_67(0) == 0
assert duty_67(100) == 65535
```

## EPY-E-068: partial frame parsing

- Difficulty: Easy
- Language: Python for Embedded Systems (MicroPython/CircuitPython)
- Perspective: Serial protocol
- Concept: partial frame parsing
- Symptom: A split UART message is decoded incorrectly.
- Diagnostic goal: Buffer bytes until a complete framed message exists.

### Buggy code

```python
def parse_68(buffer):
    start = buffer.find(b'<')
    end = buffer.find(b'>')
    return buffer[start + 1:end], buffer[end + 1:]
```

### Expected diagnosis

A missing terminator produces an incomplete frame and slicing with -1 silently discards data.

### Corrected code

```python
def parse_68(buffer):
    start = buffer.find(b'<')
    if start < 0:
        return None, buffer
    end = buffer.find(b'>', start + 1)
    if end < 0:
        return None, buffer[start:]
    return buffer[start + 1:end], buffer[end + 1:]
```

### Regression tests

```python
assert parse_68(b'<ok>rest') == (b'ok', b'rest')
assert parse_68(b'<ok') == (None, b'<ok')
```

## EPY-E-069: unbounded buffer

- Difficulty: Easy
- Language: Python for Embedded Systems (MicroPython/CircuitPython)
- Perspective: Memory budgeting
- Concept: unbounded buffer
- Symptom: Long-running firmware eventually runs out of RAM.
- Diagnostic goal: Enforce a bounded buffer before appending input.

### Buggy code

```python
def append_69(buffer, chunk):
    buffer += chunk
    return buffer
```

### Expected diagnosis

Accumulating input without a maximum lets noisy or disconnected peers consume all available memory.

### Corrected code

```python
def append_69(buffer, chunk, limit=128):
    buffer += chunk
    if len(buffer) > limit:
        raise ValueError('frame too large')
    return buffer
```

### Regression tests

```python
assert append_69(b'a', b'b') == b'ab'
try: append_69(b'a' * 128, b'b')
except ValueError: pass
else: raise AssertionError
```

## EPY-E-070: level confused with edge

- Difficulty: Easy
- Language: Python for Embedded Systems (MicroPython/CircuitPython)
- Perspective: Debouncing
- Concept: level confused with edge
- Symptom: One button press counts many times.
- Diagnostic goal: Count a transition only after the signal remains stable.

### Buggy code

```python
def pressed_70(level):
    return level
```

### Expected diagnosis

A sampled high level is not a new press; edge detection must compare the current state with the previous stable state.

### Corrected code

```python
def pressed_70(previous, current):
    return not previous and current
```

### Regression tests

```python
assert pressed_70(False, True)
assert not pressed_70(True, True)
```

## EPY-E-071: bytes and text mixed

- Difficulty: Easy
- Language: Python for Embedded Systems (MicroPython/CircuitPython)
- Perspective: Data representation
- Concept: bytes and text mixed
- Symptom: A serial write raises a type error or corrupts data.
- Diagnostic goal: Choose an encoding boundary and keep bytes as bytes on the wire.

### Buggy code

```python
def packet_71(text):
    return b'<' + text + b'>'
```

### Expected diagnosis

Python text strings and byte strings are distinct; concatenating them is invalid.

### Corrected code

```python
def packet_71(text):
    return b'<' + text.encode('ascii') + b'>'
```

### Regression tests

```python
assert packet_71('ok') == b'<ok>'
```

## EPY-E-072: sleep state loses context

- Difficulty: Easy
- Language: Python for Embedded Systems (MicroPython/CircuitPython)
- Perspective: Power state
- Concept: sleep state loses context
- Symptom: The device wakes without knowing why.
- Diagnostic goal: Persist only the minimal wake context in a stable representation.

### Buggy code

```python
def save_72(reason):
    return str(reason)
```

### Expected diagnosis

A string representation is ambiguous and may not survive a reset or schema change.

### Corrected code

```python
def save_72(reason):
    if reason not in ('timer', 'pin'):
        raise ValueError('unknown wake reason')
    return {'reason': reason}
```

### Regression tests

```python
assert save_72('timer') == {'reason': 'timer'}
```

## EPY-E-073: blocking delay

- Difficulty: Easy
- Language: Python for Embedded Systems (MicroPython/CircuitPython)
- Perspective: Timing
- Concept: blocking delay
- Symptom: A periodic task misses its interval.
- Diagnostic goal: Use a monotonic clock and account for elapsed work.

### Buggy code

```python
def tick_73(now, last, period):
    if now - last >= period:
        sleep(period)
        return now
    return last
```

### Expected diagnosis

Sleeping for the full period after work accumulates drift and the undefined sleep dependency hides the scheduling contract.

### Corrected code

```python
def tick_73(now, last, period):
    if now - last >= period:
        return now
    return last
```

### Regression tests

```python
assert tick_73(100, 0, 100) == 100
assert tick_73(150, 100, 100) == 100
```

## EPY-E-074: wrong active level

- Difficulty: Easy
- Language: Python for Embedded Systems (MicroPython/CircuitPython)
- Perspective: GPIO boundary
- Concept: wrong active level
- Symptom: An LED or relay behaves inverted.
- Diagnostic goal: Model active-low hardware explicitly.

### Buggy code

```python
def output_74(on):
    return 1 if on else 0
```

### Expected diagnosis

The device is wired active-low, so a logical on state must drive the low electrical level.

### Corrected code

```python
def output_74(on):
    return 0 if on else 1
```

### Regression tests

```python
assert output_74(True) == 0
assert output_74(False) == 1
```

## EPY-E-075: raw value treated as volts

- Difficulty: Easy
- Language: Python for Embedded Systems (MicroPython/CircuitPython)
- Perspective: ADC reasoning
- Concept: raw value treated as volts
- Symptom: The displayed voltage is far too large.
- Diagnostic goal: Separate raw ADC units from calibrated physical units.

### Buggy code

```python
def volts_75(raw):
    return raw
```

### Expected diagnosis

An ADC returns a code, not volts; conversion needs the reference voltage and resolution.

### Corrected code

```python
def volts_75(raw, reference=3.3, maximum=4095):
    return raw * reference / maximum
```

### Regression tests

```python
assert abs(volts_75(4095) - 3.3) < 1e-9
assert volts_75(0) == 0
```

## EPY-E-076: duty-cycle units

- Difficulty: Easy
- Language: Python for Embedded Systems (MicroPython/CircuitPython)
- Perspective: PWM reasoning
- Concept: duty-cycle units
- Symptom: The output is always off or saturated.
- Diagnostic goal: Normalize the public duty-cycle contract before writing hardware units.

### Buggy code

```python
def duty_76(percent):
    return int(percent)
```

### Expected diagnosis

The PWM API expects a different range than the user-facing percentage.

### Corrected code

```python
def duty_76(percent):
    if not 0 <= percent <= 100:
        raise ValueError('percent out of range')
    return round(percent * 65535 / 100)
```

### Regression tests

```python
assert duty_76(0) == 0
assert duty_76(100) == 65535
```

## EPY-E-077: partial frame parsing

- Difficulty: Easy
- Language: Python for Embedded Systems (MicroPython/CircuitPython)
- Perspective: Serial protocol
- Concept: partial frame parsing
- Symptom: A split UART message is decoded incorrectly.
- Diagnostic goal: Buffer bytes until a complete framed message exists.

### Buggy code

```python
def parse_77(buffer):
    start = buffer.find(b'<')
    end = buffer.find(b'>')
    return buffer[start + 1:end], buffer[end + 1:]
```

### Expected diagnosis

A missing terminator produces an incomplete frame and slicing with -1 silently discards data.

### Corrected code

```python
def parse_77(buffer):
    start = buffer.find(b'<')
    if start < 0:
        return None, buffer
    end = buffer.find(b'>', start + 1)
    if end < 0:
        return None, buffer[start:]
    return buffer[start + 1:end], buffer[end + 1:]
```

### Regression tests

```python
assert parse_77(b'<ok>rest') == (b'ok', b'rest')
assert parse_77(b'<ok') == (None, b'<ok')
```

## EPY-E-078: unbounded buffer

- Difficulty: Easy
- Language: Python for Embedded Systems (MicroPython/CircuitPython)
- Perspective: Memory budgeting
- Concept: unbounded buffer
- Symptom: Long-running firmware eventually runs out of RAM.
- Diagnostic goal: Enforce a bounded buffer before appending input.

### Buggy code

```python
def append_78(buffer, chunk):
    buffer += chunk
    return buffer
```

### Expected diagnosis

Accumulating input without a maximum lets noisy or disconnected peers consume all available memory.

### Corrected code

```python
def append_78(buffer, chunk, limit=128):
    buffer += chunk
    if len(buffer) > limit:
        raise ValueError('frame too large')
    return buffer
```

### Regression tests

```python
assert append_78(b'a', b'b') == b'ab'
try: append_78(b'a' * 128, b'b')
except ValueError: pass
else: raise AssertionError
```

## EPY-E-079: level confused with edge

- Difficulty: Easy
- Language: Python for Embedded Systems (MicroPython/CircuitPython)
- Perspective: Debouncing
- Concept: level confused with edge
- Symptom: One button press counts many times.
- Diagnostic goal: Count a transition only after the signal remains stable.

### Buggy code

```python
def pressed_79(level):
    return level
```

### Expected diagnosis

A sampled high level is not a new press; edge detection must compare the current state with the previous stable state.

### Corrected code

```python
def pressed_79(previous, current):
    return not previous and current
```

### Regression tests

```python
assert pressed_79(False, True)
assert not pressed_79(True, True)
```

## EPY-E-080: bytes and text mixed

- Difficulty: Easy
- Language: Python for Embedded Systems (MicroPython/CircuitPython)
- Perspective: Data representation
- Concept: bytes and text mixed
- Symptom: A serial write raises a type error or corrupts data.
- Diagnostic goal: Choose an encoding boundary and keep bytes as bytes on the wire.

### Buggy code

```python
def packet_80(text):
    return b'<' + text + b'>'
```

### Expected diagnosis

Python text strings and byte strings are distinct; concatenating them is invalid.

### Corrected code

```python
def packet_80(text):
    return b'<' + text.encode('ascii') + b'>'
```

### Regression tests

```python
assert packet_80('ok') == b'<ok>'
```

## EPY-E-081: sleep state loses context

- Difficulty: Easy
- Language: Python for Embedded Systems (MicroPython/CircuitPython)
- Perspective: Power state
- Concept: sleep state loses context
- Symptom: The device wakes without knowing why.
- Diagnostic goal: Persist only the minimal wake context in a stable representation.

### Buggy code

```python
def save_81(reason):
    return str(reason)
```

### Expected diagnosis

A string representation is ambiguous and may not survive a reset or schema change.

### Corrected code

```python
def save_81(reason):
    if reason not in ('timer', 'pin'):
        raise ValueError('unknown wake reason')
    return {'reason': reason}
```

### Regression tests

```python
assert save_81('timer') == {'reason': 'timer'}
```

## EPY-E-082: blocking delay

- Difficulty: Easy
- Language: Python for Embedded Systems (MicroPython/CircuitPython)
- Perspective: Timing
- Concept: blocking delay
- Symptom: A periodic task misses its interval.
- Diagnostic goal: Use a monotonic clock and account for elapsed work.

### Buggy code

```python
def tick_82(now, last, period):
    if now - last >= period:
        sleep(period)
        return now
    return last
```

### Expected diagnosis

Sleeping for the full period after work accumulates drift and the undefined sleep dependency hides the scheduling contract.

### Corrected code

```python
def tick_82(now, last, period):
    if now - last >= period:
        return now
    return last
```

### Regression tests

```python
assert tick_82(100, 0, 100) == 100
assert tick_82(150, 100, 100) == 100
```

## EPY-E-083: wrong active level

- Difficulty: Easy
- Language: Python for Embedded Systems (MicroPython/CircuitPython)
- Perspective: GPIO boundary
- Concept: wrong active level
- Symptom: An LED or relay behaves inverted.
- Diagnostic goal: Model active-low hardware explicitly.

### Buggy code

```python
def output_83(on):
    return 1 if on else 0
```

### Expected diagnosis

The device is wired active-low, so a logical on state must drive the low electrical level.

### Corrected code

```python
def output_83(on):
    return 0 if on else 1
```

### Regression tests

```python
assert output_83(True) == 0
assert output_83(False) == 1
```

## EPY-E-084: raw value treated as volts

- Difficulty: Easy
- Language: Python for Embedded Systems (MicroPython/CircuitPython)
- Perspective: ADC reasoning
- Concept: raw value treated as volts
- Symptom: The displayed voltage is far too large.
- Diagnostic goal: Separate raw ADC units from calibrated physical units.

### Buggy code

```python
def volts_84(raw):
    return raw
```

### Expected diagnosis

An ADC returns a code, not volts; conversion needs the reference voltage and resolution.

### Corrected code

```python
def volts_84(raw, reference=3.3, maximum=4095):
    return raw * reference / maximum
```

### Regression tests

```python
assert abs(volts_84(4095) - 3.3) < 1e-9
assert volts_84(0) == 0
```

## EPY-E-085: duty-cycle units

- Difficulty: Easy
- Language: Python for Embedded Systems (MicroPython/CircuitPython)
- Perspective: PWM reasoning
- Concept: duty-cycle units
- Symptom: The output is always off or saturated.
- Diagnostic goal: Normalize the public duty-cycle contract before writing hardware units.

### Buggy code

```python
def duty_85(percent):
    return int(percent)
```

### Expected diagnosis

The PWM API expects a different range than the user-facing percentage.

### Corrected code

```python
def duty_85(percent):
    if not 0 <= percent <= 100:
        raise ValueError('percent out of range')
    return round(percent * 65535 / 100)
```

### Regression tests

```python
assert duty_85(0) == 0
assert duty_85(100) == 65535
```

## EPY-E-086: partial frame parsing

- Difficulty: Easy
- Language: Python for Embedded Systems (MicroPython/CircuitPython)
- Perspective: Serial protocol
- Concept: partial frame parsing
- Symptom: A split UART message is decoded incorrectly.
- Diagnostic goal: Buffer bytes until a complete framed message exists.

### Buggy code

```python
def parse_86(buffer):
    start = buffer.find(b'<')
    end = buffer.find(b'>')
    return buffer[start + 1:end], buffer[end + 1:]
```

### Expected diagnosis

A missing terminator produces an incomplete frame and slicing with -1 silently discards data.

### Corrected code

```python
def parse_86(buffer):
    start = buffer.find(b'<')
    if start < 0:
        return None, buffer
    end = buffer.find(b'>', start + 1)
    if end < 0:
        return None, buffer[start:]
    return buffer[start + 1:end], buffer[end + 1:]
```

### Regression tests

```python
assert parse_86(b'<ok>rest') == (b'ok', b'rest')
assert parse_86(b'<ok') == (None, b'<ok')
```

## EPY-E-087: unbounded buffer

- Difficulty: Easy
- Language: Python for Embedded Systems (MicroPython/CircuitPython)
- Perspective: Memory budgeting
- Concept: unbounded buffer
- Symptom: Long-running firmware eventually runs out of RAM.
- Diagnostic goal: Enforce a bounded buffer before appending input.

### Buggy code

```python
def append_87(buffer, chunk):
    buffer += chunk
    return buffer
```

### Expected diagnosis

Accumulating input without a maximum lets noisy or disconnected peers consume all available memory.

### Corrected code

```python
def append_87(buffer, chunk, limit=128):
    buffer += chunk
    if len(buffer) > limit:
        raise ValueError('frame too large')
    return buffer
```

### Regression tests

```python
assert append_87(b'a', b'b') == b'ab'
try: append_87(b'a' * 128, b'b')
except ValueError: pass
else: raise AssertionError
```

## EPY-E-088: level confused with edge

- Difficulty: Easy
- Language: Python for Embedded Systems (MicroPython/CircuitPython)
- Perspective: Debouncing
- Concept: level confused with edge
- Symptom: One button press counts many times.
- Diagnostic goal: Count a transition only after the signal remains stable.

### Buggy code

```python
def pressed_88(level):
    return level
```

### Expected diagnosis

A sampled high level is not a new press; edge detection must compare the current state with the previous stable state.

### Corrected code

```python
def pressed_88(previous, current):
    return not previous and current
```

### Regression tests

```python
assert pressed_88(False, True)
assert not pressed_88(True, True)
```

## EPY-E-089: bytes and text mixed

- Difficulty: Easy
- Language: Python for Embedded Systems (MicroPython/CircuitPython)
- Perspective: Data representation
- Concept: bytes and text mixed
- Symptom: A serial write raises a type error or corrupts data.
- Diagnostic goal: Choose an encoding boundary and keep bytes as bytes on the wire.

### Buggy code

```python
def packet_89(text):
    return b'<' + text + b'>'
```

### Expected diagnosis

Python text strings and byte strings are distinct; concatenating them is invalid.

### Corrected code

```python
def packet_89(text):
    return b'<' + text.encode('ascii') + b'>'
```

### Regression tests

```python
assert packet_89('ok') == b'<ok>'
```

## EPY-E-090: sleep state loses context

- Difficulty: Easy
- Language: Python for Embedded Systems (MicroPython/CircuitPython)
- Perspective: Power state
- Concept: sleep state loses context
- Symptom: The device wakes without knowing why.
- Diagnostic goal: Persist only the minimal wake context in a stable representation.

### Buggy code

```python
def save_90(reason):
    return str(reason)
```

### Expected diagnosis

A string representation is ambiguous and may not survive a reset or schema change.

### Corrected code

```python
def save_90(reason):
    if reason not in ('timer', 'pin'):
        raise ValueError('unknown wake reason')
    return {'reason': reason}
```

### Regression tests

```python
assert save_90('timer') == {'reason': 'timer'}
```

## EPY-E-091: blocking delay

- Difficulty: Easy
- Language: Python for Embedded Systems (MicroPython/CircuitPython)
- Perspective: Timing
- Concept: blocking delay
- Symptom: A periodic task misses its interval.
- Diagnostic goal: Use a monotonic clock and account for elapsed work.

### Buggy code

```python
def tick_91(now, last, period):
    if now - last >= period:
        sleep(period)
        return now
    return last
```

### Expected diagnosis

Sleeping for the full period after work accumulates drift and the undefined sleep dependency hides the scheduling contract.

### Corrected code

```python
def tick_91(now, last, period):
    if now - last >= period:
        return now
    return last
```

### Regression tests

```python
assert tick_91(100, 0, 100) == 100
assert tick_91(150, 100, 100) == 100
```

## EPY-E-092: wrong active level

- Difficulty: Easy
- Language: Python for Embedded Systems (MicroPython/CircuitPython)
- Perspective: GPIO boundary
- Concept: wrong active level
- Symptom: An LED or relay behaves inverted.
- Diagnostic goal: Model active-low hardware explicitly.

### Buggy code

```python
def output_92(on):
    return 1 if on else 0
```

### Expected diagnosis

The device is wired active-low, so a logical on state must drive the low electrical level.

### Corrected code

```python
def output_92(on):
    return 0 if on else 1
```

### Regression tests

```python
assert output_92(True) == 0
assert output_92(False) == 1
```

## EPY-E-093: raw value treated as volts

- Difficulty: Easy
- Language: Python for Embedded Systems (MicroPython/CircuitPython)
- Perspective: ADC reasoning
- Concept: raw value treated as volts
- Symptom: The displayed voltage is far too large.
- Diagnostic goal: Separate raw ADC units from calibrated physical units.

### Buggy code

```python
def volts_93(raw):
    return raw
```

### Expected diagnosis

An ADC returns a code, not volts; conversion needs the reference voltage and resolution.

### Corrected code

```python
def volts_93(raw, reference=3.3, maximum=4095):
    return raw * reference / maximum
```

### Regression tests

```python
assert abs(volts_93(4095) - 3.3) < 1e-9
assert volts_93(0) == 0
```

## EPY-E-094: duty-cycle units

- Difficulty: Easy
- Language: Python for Embedded Systems (MicroPython/CircuitPython)
- Perspective: PWM reasoning
- Concept: duty-cycle units
- Symptom: The output is always off or saturated.
- Diagnostic goal: Normalize the public duty-cycle contract before writing hardware units.

### Buggy code

```python
def duty_94(percent):
    return int(percent)
```

### Expected diagnosis

The PWM API expects a different range than the user-facing percentage.

### Corrected code

```python
def duty_94(percent):
    if not 0 <= percent <= 100:
        raise ValueError('percent out of range')
    return round(percent * 65535 / 100)
```

### Regression tests

```python
assert duty_94(0) == 0
assert duty_94(100) == 65535
```

## EPY-E-095: partial frame parsing

- Difficulty: Easy
- Language: Python for Embedded Systems (MicroPython/CircuitPython)
- Perspective: Serial protocol
- Concept: partial frame parsing
- Symptom: A split UART message is decoded incorrectly.
- Diagnostic goal: Buffer bytes until a complete framed message exists.

### Buggy code

```python
def parse_95(buffer):
    start = buffer.find(b'<')
    end = buffer.find(b'>')
    return buffer[start + 1:end], buffer[end + 1:]
```

### Expected diagnosis

A missing terminator produces an incomplete frame and slicing with -1 silently discards data.

### Corrected code

```python
def parse_95(buffer):
    start = buffer.find(b'<')
    if start < 0:
        return None, buffer
    end = buffer.find(b'>', start + 1)
    if end < 0:
        return None, buffer[start:]
    return buffer[start + 1:end], buffer[end + 1:]
```

### Regression tests

```python
assert parse_95(b'<ok>rest') == (b'ok', b'rest')
assert parse_95(b'<ok') == (None, b'<ok')
```

## EPY-E-096: unbounded buffer

- Difficulty: Easy
- Language: Python for Embedded Systems (MicroPython/CircuitPython)
- Perspective: Memory budgeting
- Concept: unbounded buffer
- Symptom: Long-running firmware eventually runs out of RAM.
- Diagnostic goal: Enforce a bounded buffer before appending input.

### Buggy code

```python
def append_96(buffer, chunk):
    buffer += chunk
    return buffer
```

### Expected diagnosis

Accumulating input without a maximum lets noisy or disconnected peers consume all available memory.

### Corrected code

```python
def append_96(buffer, chunk, limit=128):
    buffer += chunk
    if len(buffer) > limit:
        raise ValueError('frame too large')
    return buffer
```

### Regression tests

```python
assert append_96(b'a', b'b') == b'ab'
try: append_96(b'a' * 128, b'b')
except ValueError: pass
else: raise AssertionError
```

## EPY-E-097: level confused with edge

- Difficulty: Easy
- Language: Python for Embedded Systems (MicroPython/CircuitPython)
- Perspective: Debouncing
- Concept: level confused with edge
- Symptom: One button press counts many times.
- Diagnostic goal: Count a transition only after the signal remains stable.

### Buggy code

```python
def pressed_97(level):
    return level
```

### Expected diagnosis

A sampled high level is not a new press; edge detection must compare the current state with the previous stable state.

### Corrected code

```python
def pressed_97(previous, current):
    return not previous and current
```

### Regression tests

```python
assert pressed_97(False, True)
assert not pressed_97(True, True)
```

## EPY-E-098: bytes and text mixed

- Difficulty: Easy
- Language: Python for Embedded Systems (MicroPython/CircuitPython)
- Perspective: Data representation
- Concept: bytes and text mixed
- Symptom: A serial write raises a type error or corrupts data.
- Diagnostic goal: Choose an encoding boundary and keep bytes as bytes on the wire.

### Buggy code

```python
def packet_98(text):
    return b'<' + text + b'>'
```

### Expected diagnosis

Python text strings and byte strings are distinct; concatenating them is invalid.

### Corrected code

```python
def packet_98(text):
    return b'<' + text.encode('ascii') + b'>'
```

### Regression tests

```python
assert packet_98('ok') == b'<ok>'
```

## EPY-E-099: sleep state loses context

- Difficulty: Easy
- Language: Python for Embedded Systems (MicroPython/CircuitPython)
- Perspective: Power state
- Concept: sleep state loses context
- Symptom: The device wakes without knowing why.
- Diagnostic goal: Persist only the minimal wake context in a stable representation.

### Buggy code

```python
def save_99(reason):
    return str(reason)
```

### Expected diagnosis

A string representation is ambiguous and may not survive a reset or schema change.

### Corrected code

```python
def save_99(reason):
    if reason not in ('timer', 'pin'):
        raise ValueError('unknown wake reason')
    return {'reason': reason}
```

### Regression tests

```python
assert save_99('timer') == {'reason': 'timer'}
```

## EPY-E-100: blocking delay

- Difficulty: Easy
- Language: Python for Embedded Systems (MicroPython/CircuitPython)
- Perspective: Timing
- Concept: blocking delay
- Symptom: A periodic task misses its interval.
- Diagnostic goal: Use a monotonic clock and account for elapsed work.

### Buggy code

```python
def tick_100(now, last, period):
    if now - last >= period:
        sleep(period)
        return now
    return last
```

### Expected diagnosis

Sleeping for the full period after work accumulates drift and the undefined sleep dependency hides the scheduling contract.

### Corrected code

```python
def tick_100(now, last, period):
    if now - last >= period:
        return now
    return last
```

### Regression tests

```python
assert tick_100(100, 0, 100) == 100
assert tick_100(150, 100, 100) == 100
```

## EPY-M-001: work done in ISR

- Difficulty: Medium
- Language: Python for Embedded Systems (MicroPython/CircuitPython)
- Perspective: Interrupt safety
- Concept: work done in ISR
- Symptom: The interrupt handler blocks or corrupts state.
- Diagnostic goal: Keep interrupt handlers short and hand work to the main loop.

### Buggy code

```python
def irq_1(state):
    state['count'] += 1
    read_sensor()
    print(state)
```

### Expected diagnosis

Peripheral access, allocation, and I/O inside an interrupt can be unsafe or unbounded.

### Corrected code

```python
def irq_1(state):
    state['count'] += 1
    state['pending'] = True
```

### Regression tests

```python
state = {'count': 0, 'pending': False}
irq_1(state)
assert state == {'count': 1, 'pending': True}
```

## EPY-M-002: off-by-one capacity

- Difficulty: Medium
- Language: Python for Embedded Systems (MicroPython/CircuitPython)
- Perspective: Ring buffers
- Concept: off-by-one capacity
- Symptom: A full buffer is mistaken for an empty buffer.
- Diagnostic goal: Reserve one slot or track size separately.

### Buggy code

```python
def push_2(items, value, capacity):
    if len(items) == capacity:
        return False
    items.append(value)
    return True
```

### Expected diagnosis

A list model is ambiguous about overwrite policy and gives no explicit distinction between full and empty states.

### Corrected code

```python
def push_2(items, value, capacity):
    if len(items) >= capacity:
        return False
    items.append(value)
    return True
```

### Regression tests

```python
items = []
assert push_2(items, 1, 1)
assert not push_2(items, 2, 1)
```

## EPY-M-003: watchdog fed during a hang

- Difficulty: Medium
- Language: Python for Embedded Systems (MicroPython/CircuitPython)
- Perspective: Watchdog design
- Concept: watchdog fed during a hang
- Symptom: A stuck loop prevents recovery.
- Diagnostic goal: Feed the watchdog only after essential work completes.

### Buggy code

```python
def service_3(work, watchdog):
    watchdog.feed()
    work()
```

### Expected diagnosis

Feeding before the work proves only that the loop started, so a blocked work call can still run forever.

### Corrected code

```python
def service_3(work, watchdog):
    work()
    watchdog.feed()
```

### Regression tests

```python
# Regression: a failed or blocked work call must not reach feed().
```

## EPY-M-004: address and register confused

- Difficulty: Medium
- Language: Python for Embedded Systems (MicroPython/CircuitPython)
- Perspective: I2C transaction
- Concept: address and register confused
- Symptom: Reads return bytes from the wrong device or register.
- Diagnostic goal: Keep bus address, register, and payload as separate fields.

### Buggy code

```python
def read_4(bus, address, register):
    return bus.readfrom_mem(register, address, 1)
```

### Expected diagnosis

The common MicroPython memory-read order is address, register, and length; swapping the first two changes the transaction.

### Corrected code

```python
def read_4(bus, address, register):
    return bus.readfrom_mem(address, register, 1)
```

### Regression tests

```python
# Regression: a fake bus should observe address=64, register=0x01, length=1.
```

## EPY-M-005: forgotten await

- Difficulty: Medium
- Language: Python for Embedded Systems (MicroPython/CircuitPython)
- Perspective: Async scheduling
- Concept: forgotten await
- Symptom: A coroutine object is stored instead of sensor data.
- Diagnostic goal: Trace the await boundary and return the resolved value.

### Buggy code

```python
async def sample_5(sensor):
    value = sensor.read_async()
    return value * 2
```

### Expected diagnosis

Calling an async method creates a coroutine; arithmetic must happen after awaiting it.

### Corrected code

```python
async def sample_5(sensor):
    value = await sensor.read_async()
    return value * 2
```

### Regression tests

```python
# Regression: run with an async fake sensor and assert the numeric result.
```

## EPY-M-006: invalid pin mode accepted

- Difficulty: Medium
- Language: Python for Embedded Systems (MicroPython/CircuitPython)
- Perspective: Configuration
- Concept: invalid pin mode accepted
- Symptom: A board fails later with a confusing hardware error.
- Diagnostic goal: Validate configuration at startup and fail close to the boundary.

### Buggy code

```python
def configure_6(pin, mode):
    pin.init(mode=mode)
    return pin
```

### Expected diagnosis

An arbitrary mode reaches the hardware API without a clear application-level contract.

### Corrected code

```python
def configure_6(pin, mode):
    if mode not in ('in', 'out'):
        raise ValueError('mode must be in or out')
    pin.init(mode=mode)
    return pin
```

### Regression tests

```python
# Regression: invalid modes raise before pin.init is called.
```

## EPY-M-007: integer truncation

- Difficulty: Medium
- Language: Python for Embedded Systems (MicroPython/CircuitPython)
- Perspective: Calibration
- Concept: integer truncation
- Symptom: Small sensor changes disappear.
- Diagnostic goal: Retain precision until formatting for display.

### Buggy code

```python
def calibrate_7(raw, offset):
    return int(raw + offset)
```

### Expected diagnosis

Converting to int during calibration discards fractional information that may matter to control decisions.

### Corrected code

```python
def calibrate_7(raw, offset):
    return raw + offset
```

### Regression tests

```python
assert calibrate_7(10.5, 0.25) == 10.75
```

## EPY-M-008: retry storm

- Difficulty: Medium
- Language: Python for Embedded Systems (MicroPython/CircuitPython)
- Perspective: Fault recovery
- Concept: retry storm
- Symptom: A disconnected peripheral is retried continuously and starves other tasks.
- Diagnostic goal: Bound retries and include a delay or backoff.

### Buggy code

```python
def read_with_retry_8(read, attempts):
    for _ in range(attempts):
        try: return read()
        except OSError: pass
    return None
```

### Expected diagnosis

Repeated immediate retries consume the scheduler and can worsen a bus fault; recovery needs a bounded, observable policy.

### Corrected code

```python
def read_with_retry_8(read, attempts):
    for attempt in range(attempts):
        try: return read()
        except OSError:
            if attempt == attempts - 1: raise
    raise AssertionError('unreachable')
```

### Regression tests

```python
# Regression: a permanent OSError is raised after exactly the configured attempts.
```

## EPY-M-009: schema drift

- Difficulty: Medium
- Language: Python for Embedded Systems (MicroPython/CircuitPython)
- Perspective: Serialization
- Concept: schema drift
- Symptom: Persisted settings cannot be loaded after a firmware update.
- Diagnostic goal: Version the stored schema and migrate known versions.

### Buggy code

```python
def load_9(data):
    return {'threshold': data['threshold']}
```

### Expected diagnosis

Reading fields without a version prevents controlled migration and turns old data into an opaque KeyError.

### Corrected code

```python
def load_9(data):
    version = data.get('version', 1)
    if version == 1:
        return {'threshold': data['threshold']}
    if version == 2:
        return {'threshold': data['limit']}
    raise ValueError('unsupported settings version')
```

### Regression tests

```python
assert load_9({'threshold': 3}) == {'threshold': 3}
assert load_9({'version': 2, 'limit': 4}) == {'threshold': 4}
```

## EPY-M-010: work done in ISR

- Difficulty: Medium
- Language: Python for Embedded Systems (MicroPython/CircuitPython)
- Perspective: Interrupt safety
- Concept: work done in ISR
- Symptom: The interrupt handler blocks or corrupts state.
- Diagnostic goal: Keep interrupt handlers short and hand work to the main loop.

### Buggy code

```python
def irq_10(state):
    state['count'] += 1
    read_sensor()
    print(state)
```

### Expected diagnosis

Peripheral access, allocation, and I/O inside an interrupt can be unsafe or unbounded.

### Corrected code

```python
def irq_10(state):
    state['count'] += 1
    state['pending'] = True
```

### Regression tests

```python
state = {'count': 0, 'pending': False}
irq_10(state)
assert state == {'count': 1, 'pending': True}
```

## EPY-M-011: off-by-one capacity

- Difficulty: Medium
- Language: Python for Embedded Systems (MicroPython/CircuitPython)
- Perspective: Ring buffers
- Concept: off-by-one capacity
- Symptom: A full buffer is mistaken for an empty buffer.
- Diagnostic goal: Reserve one slot or track size separately.

### Buggy code

```python
def push_11(items, value, capacity):
    if len(items) == capacity:
        return False
    items.append(value)
    return True
```

### Expected diagnosis

A list model is ambiguous about overwrite policy and gives no explicit distinction between full and empty states.

### Corrected code

```python
def push_11(items, value, capacity):
    if len(items) >= capacity:
        return False
    items.append(value)
    return True
```

### Regression tests

```python
items = []
assert push_11(items, 1, 1)
assert not push_11(items, 2, 1)
```

## EPY-M-012: watchdog fed during a hang

- Difficulty: Medium
- Language: Python for Embedded Systems (MicroPython/CircuitPython)
- Perspective: Watchdog design
- Concept: watchdog fed during a hang
- Symptom: A stuck loop prevents recovery.
- Diagnostic goal: Feed the watchdog only after essential work completes.

### Buggy code

```python
def service_12(work, watchdog):
    watchdog.feed()
    work()
```

### Expected diagnosis

Feeding before the work proves only that the loop started, so a blocked work call can still run forever.

### Corrected code

```python
def service_12(work, watchdog):
    work()
    watchdog.feed()
```

### Regression tests

```python
# Regression: a failed or blocked work call must not reach feed().
```

## EPY-M-013: address and register confused

- Difficulty: Medium
- Language: Python for Embedded Systems (MicroPython/CircuitPython)
- Perspective: I2C transaction
- Concept: address and register confused
- Symptom: Reads return bytes from the wrong device or register.
- Diagnostic goal: Keep bus address, register, and payload as separate fields.

### Buggy code

```python
def read_13(bus, address, register):
    return bus.readfrom_mem(register, address, 1)
```

### Expected diagnosis

The common MicroPython memory-read order is address, register, and length; swapping the first two changes the transaction.

### Corrected code

```python
def read_13(bus, address, register):
    return bus.readfrom_mem(address, register, 1)
```

### Regression tests

```python
# Regression: a fake bus should observe address=64, register=0x01, length=1.
```

## EPY-M-014: forgotten await

- Difficulty: Medium
- Language: Python for Embedded Systems (MicroPython/CircuitPython)
- Perspective: Async scheduling
- Concept: forgotten await
- Symptom: A coroutine object is stored instead of sensor data.
- Diagnostic goal: Trace the await boundary and return the resolved value.

### Buggy code

```python
async def sample_14(sensor):
    value = sensor.read_async()
    return value * 2
```

### Expected diagnosis

Calling an async method creates a coroutine; arithmetic must happen after awaiting it.

### Corrected code

```python
async def sample_14(sensor):
    value = await sensor.read_async()
    return value * 2
```

### Regression tests

```python
# Regression: run with an async fake sensor and assert the numeric result.
```

## EPY-M-015: invalid pin mode accepted

- Difficulty: Medium
- Language: Python for Embedded Systems (MicroPython/CircuitPython)
- Perspective: Configuration
- Concept: invalid pin mode accepted
- Symptom: A board fails later with a confusing hardware error.
- Diagnostic goal: Validate configuration at startup and fail close to the boundary.

### Buggy code

```python
def configure_15(pin, mode):
    pin.init(mode=mode)
    return pin
```

### Expected diagnosis

An arbitrary mode reaches the hardware API without a clear application-level contract.

### Corrected code

```python
def configure_15(pin, mode):
    if mode not in ('in', 'out'):
        raise ValueError('mode must be in or out')
    pin.init(mode=mode)
    return pin
```

### Regression tests

```python
# Regression: invalid modes raise before pin.init is called.
```

## EPY-M-016: integer truncation

- Difficulty: Medium
- Language: Python for Embedded Systems (MicroPython/CircuitPython)
- Perspective: Calibration
- Concept: integer truncation
- Symptom: Small sensor changes disappear.
- Diagnostic goal: Retain precision until formatting for display.

### Buggy code

```python
def calibrate_16(raw, offset):
    return int(raw + offset)
```

### Expected diagnosis

Converting to int during calibration discards fractional information that may matter to control decisions.

### Corrected code

```python
def calibrate_16(raw, offset):
    return raw + offset
```

### Regression tests

```python
assert calibrate_16(10.5, 0.25) == 10.75
```

## EPY-M-017: retry storm

- Difficulty: Medium
- Language: Python for Embedded Systems (MicroPython/CircuitPython)
- Perspective: Fault recovery
- Concept: retry storm
- Symptom: A disconnected peripheral is retried continuously and starves other tasks.
- Diagnostic goal: Bound retries and include a delay or backoff.

### Buggy code

```python
def read_with_retry_17(read, attempts):
    for _ in range(attempts):
        try: return read()
        except OSError: pass
    return None
```

### Expected diagnosis

Repeated immediate retries consume the scheduler and can worsen a bus fault; recovery needs a bounded, observable policy.

### Corrected code

```python
def read_with_retry_17(read, attempts):
    for attempt in range(attempts):
        try: return read()
        except OSError:
            if attempt == attempts - 1: raise
    raise AssertionError('unreachable')
```

### Regression tests

```python
# Regression: a permanent OSError is raised after exactly the configured attempts.
```

## EPY-M-018: schema drift

- Difficulty: Medium
- Language: Python for Embedded Systems (MicroPython/CircuitPython)
- Perspective: Serialization
- Concept: schema drift
- Symptom: Persisted settings cannot be loaded after a firmware update.
- Diagnostic goal: Version the stored schema and migrate known versions.

### Buggy code

```python
def load_18(data):
    return {'threshold': data['threshold']}
```

### Expected diagnosis

Reading fields without a version prevents controlled migration and turns old data into an opaque KeyError.

### Corrected code

```python
def load_18(data):
    version = data.get('version', 1)
    if version == 1:
        return {'threshold': data['threshold']}
    if version == 2:
        return {'threshold': data['limit']}
    raise ValueError('unsupported settings version')
```

### Regression tests

```python
assert load_18({'threshold': 3}) == {'threshold': 3}
assert load_18({'version': 2, 'limit': 4}) == {'threshold': 4}
```

## EPY-M-019: work done in ISR

- Difficulty: Medium
- Language: Python for Embedded Systems (MicroPython/CircuitPython)
- Perspective: Interrupt safety
- Concept: work done in ISR
- Symptom: The interrupt handler blocks or corrupts state.
- Diagnostic goal: Keep interrupt handlers short and hand work to the main loop.

### Buggy code

```python
def irq_19(state):
    state['count'] += 1
    read_sensor()
    print(state)
```

### Expected diagnosis

Peripheral access, allocation, and I/O inside an interrupt can be unsafe or unbounded.

### Corrected code

```python
def irq_19(state):
    state['count'] += 1
    state['pending'] = True
```

### Regression tests

```python
state = {'count': 0, 'pending': False}
irq_19(state)
assert state == {'count': 1, 'pending': True}
```

## EPY-M-020: off-by-one capacity

- Difficulty: Medium
- Language: Python for Embedded Systems (MicroPython/CircuitPython)
- Perspective: Ring buffers
- Concept: off-by-one capacity
- Symptom: A full buffer is mistaken for an empty buffer.
- Diagnostic goal: Reserve one slot or track size separately.

### Buggy code

```python
def push_20(items, value, capacity):
    if len(items) == capacity:
        return False
    items.append(value)
    return True
```

### Expected diagnosis

A list model is ambiguous about overwrite policy and gives no explicit distinction between full and empty states.

### Corrected code

```python
def push_20(items, value, capacity):
    if len(items) >= capacity:
        return False
    items.append(value)
    return True
```

### Regression tests

```python
items = []
assert push_20(items, 1, 1)
assert not push_20(items, 2, 1)
```

## EPY-M-021: watchdog fed during a hang

- Difficulty: Medium
- Language: Python for Embedded Systems (MicroPython/CircuitPython)
- Perspective: Watchdog design
- Concept: watchdog fed during a hang
- Symptom: A stuck loop prevents recovery.
- Diagnostic goal: Feed the watchdog only after essential work completes.

### Buggy code

```python
def service_21(work, watchdog):
    watchdog.feed()
    work()
```

### Expected diagnosis

Feeding before the work proves only that the loop started, so a blocked work call can still run forever.

### Corrected code

```python
def service_21(work, watchdog):
    work()
    watchdog.feed()
```

### Regression tests

```python
# Regression: a failed or blocked work call must not reach feed().
```

## EPY-M-022: address and register confused

- Difficulty: Medium
- Language: Python for Embedded Systems (MicroPython/CircuitPython)
- Perspective: I2C transaction
- Concept: address and register confused
- Symptom: Reads return bytes from the wrong device or register.
- Diagnostic goal: Keep bus address, register, and payload as separate fields.

### Buggy code

```python
def read_22(bus, address, register):
    return bus.readfrom_mem(register, address, 1)
```

### Expected diagnosis

The common MicroPython memory-read order is address, register, and length; swapping the first two changes the transaction.

### Corrected code

```python
def read_22(bus, address, register):
    return bus.readfrom_mem(address, register, 1)
```

### Regression tests

```python
# Regression: a fake bus should observe address=64, register=0x01, length=1.
```

## EPY-M-023: forgotten await

- Difficulty: Medium
- Language: Python for Embedded Systems (MicroPython/CircuitPython)
- Perspective: Async scheduling
- Concept: forgotten await
- Symptom: A coroutine object is stored instead of sensor data.
- Diagnostic goal: Trace the await boundary and return the resolved value.

### Buggy code

```python
async def sample_23(sensor):
    value = sensor.read_async()
    return value * 2
```

### Expected diagnosis

Calling an async method creates a coroutine; arithmetic must happen after awaiting it.

### Corrected code

```python
async def sample_23(sensor):
    value = await sensor.read_async()
    return value * 2
```

### Regression tests

```python
# Regression: run with an async fake sensor and assert the numeric result.
```

## EPY-M-024: invalid pin mode accepted

- Difficulty: Medium
- Language: Python for Embedded Systems (MicroPython/CircuitPython)
- Perspective: Configuration
- Concept: invalid pin mode accepted
- Symptom: A board fails later with a confusing hardware error.
- Diagnostic goal: Validate configuration at startup and fail close to the boundary.

### Buggy code

```python
def configure_24(pin, mode):
    pin.init(mode=mode)
    return pin
```

### Expected diagnosis

An arbitrary mode reaches the hardware API without a clear application-level contract.

### Corrected code

```python
def configure_24(pin, mode):
    if mode not in ('in', 'out'):
        raise ValueError('mode must be in or out')
    pin.init(mode=mode)
    return pin
```

### Regression tests

```python
# Regression: invalid modes raise before pin.init is called.
```

## EPY-M-025: integer truncation

- Difficulty: Medium
- Language: Python for Embedded Systems (MicroPython/CircuitPython)
- Perspective: Calibration
- Concept: integer truncation
- Symptom: Small sensor changes disappear.
- Diagnostic goal: Retain precision until formatting for display.

### Buggy code

```python
def calibrate_25(raw, offset):
    return int(raw + offset)
```

### Expected diagnosis

Converting to int during calibration discards fractional information that may matter to control decisions.

### Corrected code

```python
def calibrate_25(raw, offset):
    return raw + offset
```

### Regression tests

```python
assert calibrate_25(10.5, 0.25) == 10.75
```

## EPY-M-026: retry storm

- Difficulty: Medium
- Language: Python for Embedded Systems (MicroPython/CircuitPython)
- Perspective: Fault recovery
- Concept: retry storm
- Symptom: A disconnected peripheral is retried continuously and starves other tasks.
- Diagnostic goal: Bound retries and include a delay or backoff.

### Buggy code

```python
def read_with_retry_26(read, attempts):
    for _ in range(attempts):
        try: return read()
        except OSError: pass
    return None
```

### Expected diagnosis

Repeated immediate retries consume the scheduler and can worsen a bus fault; recovery needs a bounded, observable policy.

### Corrected code

```python
def read_with_retry_26(read, attempts):
    for attempt in range(attempts):
        try: return read()
        except OSError:
            if attempt == attempts - 1: raise
    raise AssertionError('unreachable')
```

### Regression tests

```python
# Regression: a permanent OSError is raised after exactly the configured attempts.
```

## EPY-M-027: schema drift

- Difficulty: Medium
- Language: Python for Embedded Systems (MicroPython/CircuitPython)
- Perspective: Serialization
- Concept: schema drift
- Symptom: Persisted settings cannot be loaded after a firmware update.
- Diagnostic goal: Version the stored schema and migrate known versions.

### Buggy code

```python
def load_27(data):
    return {'threshold': data['threshold']}
```

### Expected diagnosis

Reading fields without a version prevents controlled migration and turns old data into an opaque KeyError.

### Corrected code

```python
def load_27(data):
    version = data.get('version', 1)
    if version == 1:
        return {'threshold': data['threshold']}
    if version == 2:
        return {'threshold': data['limit']}
    raise ValueError('unsupported settings version')
```

### Regression tests

```python
assert load_27({'threshold': 3}) == {'threshold': 3}
assert load_27({'version': 2, 'limit': 4}) == {'threshold': 4}
```

## EPY-M-028: work done in ISR

- Difficulty: Medium
- Language: Python for Embedded Systems (MicroPython/CircuitPython)
- Perspective: Interrupt safety
- Concept: work done in ISR
- Symptom: The interrupt handler blocks or corrupts state.
- Diagnostic goal: Keep interrupt handlers short and hand work to the main loop.

### Buggy code

```python
def irq_28(state):
    state['count'] += 1
    read_sensor()
    print(state)
```

### Expected diagnosis

Peripheral access, allocation, and I/O inside an interrupt can be unsafe or unbounded.

### Corrected code

```python
def irq_28(state):
    state['count'] += 1
    state['pending'] = True
```

### Regression tests

```python
state = {'count': 0, 'pending': False}
irq_28(state)
assert state == {'count': 1, 'pending': True}
```

## EPY-M-029: off-by-one capacity

- Difficulty: Medium
- Language: Python for Embedded Systems (MicroPython/CircuitPython)
- Perspective: Ring buffers
- Concept: off-by-one capacity
- Symptom: A full buffer is mistaken for an empty buffer.
- Diagnostic goal: Reserve one slot or track size separately.

### Buggy code

```python
def push_29(items, value, capacity):
    if len(items) == capacity:
        return False
    items.append(value)
    return True
```

### Expected diagnosis

A list model is ambiguous about overwrite policy and gives no explicit distinction between full and empty states.

### Corrected code

```python
def push_29(items, value, capacity):
    if len(items) >= capacity:
        return False
    items.append(value)
    return True
```

### Regression tests

```python
items = []
assert push_29(items, 1, 1)
assert not push_29(items, 2, 1)
```

## EPY-M-030: watchdog fed during a hang

- Difficulty: Medium
- Language: Python for Embedded Systems (MicroPython/CircuitPython)
- Perspective: Watchdog design
- Concept: watchdog fed during a hang
- Symptom: A stuck loop prevents recovery.
- Diagnostic goal: Feed the watchdog only after essential work completes.

### Buggy code

```python
def service_30(work, watchdog):
    watchdog.feed()
    work()
```

### Expected diagnosis

Feeding before the work proves only that the loop started, so a blocked work call can still run forever.

### Corrected code

```python
def service_30(work, watchdog):
    work()
    watchdog.feed()
```

### Regression tests

```python
# Regression: a failed or blocked work call must not reach feed().
```

## EPY-M-031: address and register confused

- Difficulty: Medium
- Language: Python for Embedded Systems (MicroPython/CircuitPython)
- Perspective: I2C transaction
- Concept: address and register confused
- Symptom: Reads return bytes from the wrong device or register.
- Diagnostic goal: Keep bus address, register, and payload as separate fields.

### Buggy code

```python
def read_31(bus, address, register):
    return bus.readfrom_mem(register, address, 1)
```

### Expected diagnosis

The common MicroPython memory-read order is address, register, and length; swapping the first two changes the transaction.

### Corrected code

```python
def read_31(bus, address, register):
    return bus.readfrom_mem(address, register, 1)
```

### Regression tests

```python
# Regression: a fake bus should observe address=64, register=0x01, length=1.
```

## EPY-M-032: forgotten await

- Difficulty: Medium
- Language: Python for Embedded Systems (MicroPython/CircuitPython)
- Perspective: Async scheduling
- Concept: forgotten await
- Symptom: A coroutine object is stored instead of sensor data.
- Diagnostic goal: Trace the await boundary and return the resolved value.

### Buggy code

```python
async def sample_32(sensor):
    value = sensor.read_async()
    return value * 2
```

### Expected diagnosis

Calling an async method creates a coroutine; arithmetic must happen after awaiting it.

### Corrected code

```python
async def sample_32(sensor):
    value = await sensor.read_async()
    return value * 2
```

### Regression tests

```python
# Regression: run with an async fake sensor and assert the numeric result.
```

## EPY-M-033: invalid pin mode accepted

- Difficulty: Medium
- Language: Python for Embedded Systems (MicroPython/CircuitPython)
- Perspective: Configuration
- Concept: invalid pin mode accepted
- Symptom: A board fails later with a confusing hardware error.
- Diagnostic goal: Validate configuration at startup and fail close to the boundary.

### Buggy code

```python
def configure_33(pin, mode):
    pin.init(mode=mode)
    return pin
```

### Expected diagnosis

An arbitrary mode reaches the hardware API without a clear application-level contract.

### Corrected code

```python
def configure_33(pin, mode):
    if mode not in ('in', 'out'):
        raise ValueError('mode must be in or out')
    pin.init(mode=mode)
    return pin
```

### Regression tests

```python
# Regression: invalid modes raise before pin.init is called.
```

## EPY-M-034: integer truncation

- Difficulty: Medium
- Language: Python for Embedded Systems (MicroPython/CircuitPython)
- Perspective: Calibration
- Concept: integer truncation
- Symptom: Small sensor changes disappear.
- Diagnostic goal: Retain precision until formatting for display.

### Buggy code

```python
def calibrate_34(raw, offset):
    return int(raw + offset)
```

### Expected diagnosis

Converting to int during calibration discards fractional information that may matter to control decisions.

### Corrected code

```python
def calibrate_34(raw, offset):
    return raw + offset
```

### Regression tests

```python
assert calibrate_34(10.5, 0.25) == 10.75
```

## EPY-M-035: retry storm

- Difficulty: Medium
- Language: Python for Embedded Systems (MicroPython/CircuitPython)
- Perspective: Fault recovery
- Concept: retry storm
- Symptom: A disconnected peripheral is retried continuously and starves other tasks.
- Diagnostic goal: Bound retries and include a delay or backoff.

### Buggy code

```python
def read_with_retry_35(read, attempts):
    for _ in range(attempts):
        try: return read()
        except OSError: pass
    return None
```

### Expected diagnosis

Repeated immediate retries consume the scheduler and can worsen a bus fault; recovery needs a bounded, observable policy.

### Corrected code

```python
def read_with_retry_35(read, attempts):
    for attempt in range(attempts):
        try: return read()
        except OSError:
            if attempt == attempts - 1: raise
    raise AssertionError('unreachable')
```

### Regression tests

```python
# Regression: a permanent OSError is raised after exactly the configured attempts.
```

## EPY-M-036: schema drift

- Difficulty: Medium
- Language: Python for Embedded Systems (MicroPython/CircuitPython)
- Perspective: Serialization
- Concept: schema drift
- Symptom: Persisted settings cannot be loaded after a firmware update.
- Diagnostic goal: Version the stored schema and migrate known versions.

### Buggy code

```python
def load_36(data):
    return {'threshold': data['threshold']}
```

### Expected diagnosis

Reading fields without a version prevents controlled migration and turns old data into an opaque KeyError.

### Corrected code

```python
def load_36(data):
    version = data.get('version', 1)
    if version == 1:
        return {'threshold': data['threshold']}
    if version == 2:
        return {'threshold': data['limit']}
    raise ValueError('unsupported settings version')
```

### Regression tests

```python
assert load_36({'threshold': 3}) == {'threshold': 3}
assert load_36({'version': 2, 'limit': 4}) == {'threshold': 4}
```

## EPY-M-037: work done in ISR

- Difficulty: Medium
- Language: Python for Embedded Systems (MicroPython/CircuitPython)
- Perspective: Interrupt safety
- Concept: work done in ISR
- Symptom: The interrupt handler blocks or corrupts state.
- Diagnostic goal: Keep interrupt handlers short and hand work to the main loop.

### Buggy code

```python
def irq_37(state):
    state['count'] += 1
    read_sensor()
    print(state)
```

### Expected diagnosis

Peripheral access, allocation, and I/O inside an interrupt can be unsafe or unbounded.

### Corrected code

```python
def irq_37(state):
    state['count'] += 1
    state['pending'] = True
```

### Regression tests

```python
state = {'count': 0, 'pending': False}
irq_37(state)
assert state == {'count': 1, 'pending': True}
```

## EPY-M-038: off-by-one capacity

- Difficulty: Medium
- Language: Python for Embedded Systems (MicroPython/CircuitPython)
- Perspective: Ring buffers
- Concept: off-by-one capacity
- Symptom: A full buffer is mistaken for an empty buffer.
- Diagnostic goal: Reserve one slot or track size separately.

### Buggy code

```python
def push_38(items, value, capacity):
    if len(items) == capacity:
        return False
    items.append(value)
    return True
```

### Expected diagnosis

A list model is ambiguous about overwrite policy and gives no explicit distinction between full and empty states.

### Corrected code

```python
def push_38(items, value, capacity):
    if len(items) >= capacity:
        return False
    items.append(value)
    return True
```

### Regression tests

```python
items = []
assert push_38(items, 1, 1)
assert not push_38(items, 2, 1)
```

## EPY-M-039: watchdog fed during a hang

- Difficulty: Medium
- Language: Python for Embedded Systems (MicroPython/CircuitPython)
- Perspective: Watchdog design
- Concept: watchdog fed during a hang
- Symptom: A stuck loop prevents recovery.
- Diagnostic goal: Feed the watchdog only after essential work completes.

### Buggy code

```python
def service_39(work, watchdog):
    watchdog.feed()
    work()
```

### Expected diagnosis

Feeding before the work proves only that the loop started, so a blocked work call can still run forever.

### Corrected code

```python
def service_39(work, watchdog):
    work()
    watchdog.feed()
```

### Regression tests

```python
# Regression: a failed or blocked work call must not reach feed().
```

## EPY-M-040: address and register confused

- Difficulty: Medium
- Language: Python for Embedded Systems (MicroPython/CircuitPython)
- Perspective: I2C transaction
- Concept: address and register confused
- Symptom: Reads return bytes from the wrong device or register.
- Diagnostic goal: Keep bus address, register, and payload as separate fields.

### Buggy code

```python
def read_40(bus, address, register):
    return bus.readfrom_mem(register, address, 1)
```

### Expected diagnosis

The common MicroPython memory-read order is address, register, and length; swapping the first two changes the transaction.

### Corrected code

```python
def read_40(bus, address, register):
    return bus.readfrom_mem(address, register, 1)
```

### Regression tests

```python
# Regression: a fake bus should observe address=64, register=0x01, length=1.
```

## EPY-M-041: forgotten await

- Difficulty: Medium
- Language: Python for Embedded Systems (MicroPython/CircuitPython)
- Perspective: Async scheduling
- Concept: forgotten await
- Symptom: A coroutine object is stored instead of sensor data.
- Diagnostic goal: Trace the await boundary and return the resolved value.

### Buggy code

```python
async def sample_41(sensor):
    value = sensor.read_async()
    return value * 2
```

### Expected diagnosis

Calling an async method creates a coroutine; arithmetic must happen after awaiting it.

### Corrected code

```python
async def sample_41(sensor):
    value = await sensor.read_async()
    return value * 2
```

### Regression tests

```python
# Regression: run with an async fake sensor and assert the numeric result.
```

## EPY-M-042: invalid pin mode accepted

- Difficulty: Medium
- Language: Python for Embedded Systems (MicroPython/CircuitPython)
- Perspective: Configuration
- Concept: invalid pin mode accepted
- Symptom: A board fails later with a confusing hardware error.
- Diagnostic goal: Validate configuration at startup and fail close to the boundary.

### Buggy code

```python
def configure_42(pin, mode):
    pin.init(mode=mode)
    return pin
```

### Expected diagnosis

An arbitrary mode reaches the hardware API without a clear application-level contract.

### Corrected code

```python
def configure_42(pin, mode):
    if mode not in ('in', 'out'):
        raise ValueError('mode must be in or out')
    pin.init(mode=mode)
    return pin
```

### Regression tests

```python
# Regression: invalid modes raise before pin.init is called.
```

## EPY-M-043: integer truncation

- Difficulty: Medium
- Language: Python for Embedded Systems (MicroPython/CircuitPython)
- Perspective: Calibration
- Concept: integer truncation
- Symptom: Small sensor changes disappear.
- Diagnostic goal: Retain precision until formatting for display.

### Buggy code

```python
def calibrate_43(raw, offset):
    return int(raw + offset)
```

### Expected diagnosis

Converting to int during calibration discards fractional information that may matter to control decisions.

### Corrected code

```python
def calibrate_43(raw, offset):
    return raw + offset
```

### Regression tests

```python
assert calibrate_43(10.5, 0.25) == 10.75
```

## EPY-M-044: retry storm

- Difficulty: Medium
- Language: Python for Embedded Systems (MicroPython/CircuitPython)
- Perspective: Fault recovery
- Concept: retry storm
- Symptom: A disconnected peripheral is retried continuously and starves other tasks.
- Diagnostic goal: Bound retries and include a delay or backoff.

### Buggy code

```python
def read_with_retry_44(read, attempts):
    for _ in range(attempts):
        try: return read()
        except OSError: pass
    return None
```

### Expected diagnosis

Repeated immediate retries consume the scheduler and can worsen a bus fault; recovery needs a bounded, observable policy.

### Corrected code

```python
def read_with_retry_44(read, attempts):
    for attempt in range(attempts):
        try: return read()
        except OSError:
            if attempt == attempts - 1: raise
    raise AssertionError('unreachable')
```

### Regression tests

```python
# Regression: a permanent OSError is raised after exactly the configured attempts.
```

## EPY-M-045: schema drift

- Difficulty: Medium
- Language: Python for Embedded Systems (MicroPython/CircuitPython)
- Perspective: Serialization
- Concept: schema drift
- Symptom: Persisted settings cannot be loaded after a firmware update.
- Diagnostic goal: Version the stored schema and migrate known versions.

### Buggy code

```python
def load_45(data):
    return {'threshold': data['threshold']}
```

### Expected diagnosis

Reading fields without a version prevents controlled migration and turns old data into an opaque KeyError.

### Corrected code

```python
def load_45(data):
    version = data.get('version', 1)
    if version == 1:
        return {'threshold': data['threshold']}
    if version == 2:
        return {'threshold': data['limit']}
    raise ValueError('unsupported settings version')
```

### Regression tests

```python
assert load_45({'threshold': 3}) == {'threshold': 3}
assert load_45({'version': 2, 'limit': 4}) == {'threshold': 4}
```

## EPY-M-046: work done in ISR

- Difficulty: Medium
- Language: Python for Embedded Systems (MicroPython/CircuitPython)
- Perspective: Interrupt safety
- Concept: work done in ISR
- Symptom: The interrupt handler blocks or corrupts state.
- Diagnostic goal: Keep interrupt handlers short and hand work to the main loop.

### Buggy code

```python
def irq_46(state):
    state['count'] += 1
    read_sensor()
    print(state)
```

### Expected diagnosis

Peripheral access, allocation, and I/O inside an interrupt can be unsafe or unbounded.

### Corrected code

```python
def irq_46(state):
    state['count'] += 1
    state['pending'] = True
```

### Regression tests

```python
state = {'count': 0, 'pending': False}
irq_46(state)
assert state == {'count': 1, 'pending': True}
```

## EPY-M-047: off-by-one capacity

- Difficulty: Medium
- Language: Python for Embedded Systems (MicroPython/CircuitPython)
- Perspective: Ring buffers
- Concept: off-by-one capacity
- Symptom: A full buffer is mistaken for an empty buffer.
- Diagnostic goal: Reserve one slot or track size separately.

### Buggy code

```python
def push_47(items, value, capacity):
    if len(items) == capacity:
        return False
    items.append(value)
    return True
```

### Expected diagnosis

A list model is ambiguous about overwrite policy and gives no explicit distinction between full and empty states.

### Corrected code

```python
def push_47(items, value, capacity):
    if len(items) >= capacity:
        return False
    items.append(value)
    return True
```

### Regression tests

```python
items = []
assert push_47(items, 1, 1)
assert not push_47(items, 2, 1)
```

## EPY-M-048: watchdog fed during a hang

- Difficulty: Medium
- Language: Python for Embedded Systems (MicroPython/CircuitPython)
- Perspective: Watchdog design
- Concept: watchdog fed during a hang
- Symptom: A stuck loop prevents recovery.
- Diagnostic goal: Feed the watchdog only after essential work completes.

### Buggy code

```python
def service_48(work, watchdog):
    watchdog.feed()
    work()
```

### Expected diagnosis

Feeding before the work proves only that the loop started, so a blocked work call can still run forever.

### Corrected code

```python
def service_48(work, watchdog):
    work()
    watchdog.feed()
```

### Regression tests

```python
# Regression: a failed or blocked work call must not reach feed().
```

## EPY-M-049: address and register confused

- Difficulty: Medium
- Language: Python for Embedded Systems (MicroPython/CircuitPython)
- Perspective: I2C transaction
- Concept: address and register confused
- Symptom: Reads return bytes from the wrong device or register.
- Diagnostic goal: Keep bus address, register, and payload as separate fields.

### Buggy code

```python
def read_49(bus, address, register):
    return bus.readfrom_mem(register, address, 1)
```

### Expected diagnosis

The common MicroPython memory-read order is address, register, and length; swapping the first two changes the transaction.

### Corrected code

```python
def read_49(bus, address, register):
    return bus.readfrom_mem(address, register, 1)
```

### Regression tests

```python
# Regression: a fake bus should observe address=64, register=0x01, length=1.
```

## EPY-M-050: forgotten await

- Difficulty: Medium
- Language: Python for Embedded Systems (MicroPython/CircuitPython)
- Perspective: Async scheduling
- Concept: forgotten await
- Symptom: A coroutine object is stored instead of sensor data.
- Diagnostic goal: Trace the await boundary and return the resolved value.

### Buggy code

```python
async def sample_50(sensor):
    value = sensor.read_async()
    return value * 2
```

### Expected diagnosis

Calling an async method creates a coroutine; arithmetic must happen after awaiting it.

### Corrected code

```python
async def sample_50(sensor):
    value = await sensor.read_async()
    return value * 2
```

### Regression tests

```python
# Regression: run with an async fake sensor and assert the numeric result.
```

## EPY-M-051: invalid pin mode accepted

- Difficulty: Medium
- Language: Python for Embedded Systems (MicroPython/CircuitPython)
- Perspective: Configuration
- Concept: invalid pin mode accepted
- Symptom: A board fails later with a confusing hardware error.
- Diagnostic goal: Validate configuration at startup and fail close to the boundary.

### Buggy code

```python
def configure_51(pin, mode):
    pin.init(mode=mode)
    return pin
```

### Expected diagnosis

An arbitrary mode reaches the hardware API without a clear application-level contract.

### Corrected code

```python
def configure_51(pin, mode):
    if mode not in ('in', 'out'):
        raise ValueError('mode must be in or out')
    pin.init(mode=mode)
    return pin
```

### Regression tests

```python
# Regression: invalid modes raise before pin.init is called.
```

## EPY-M-052: integer truncation

- Difficulty: Medium
- Language: Python for Embedded Systems (MicroPython/CircuitPython)
- Perspective: Calibration
- Concept: integer truncation
- Symptom: Small sensor changes disappear.
- Diagnostic goal: Retain precision until formatting for display.

### Buggy code

```python
def calibrate_52(raw, offset):
    return int(raw + offset)
```

### Expected diagnosis

Converting to int during calibration discards fractional information that may matter to control decisions.

### Corrected code

```python
def calibrate_52(raw, offset):
    return raw + offset
```

### Regression tests

```python
assert calibrate_52(10.5, 0.25) == 10.75
```

## EPY-M-053: retry storm

- Difficulty: Medium
- Language: Python for Embedded Systems (MicroPython/CircuitPython)
- Perspective: Fault recovery
- Concept: retry storm
- Symptom: A disconnected peripheral is retried continuously and starves other tasks.
- Diagnostic goal: Bound retries and include a delay or backoff.

### Buggy code

```python
def read_with_retry_53(read, attempts):
    for _ in range(attempts):
        try: return read()
        except OSError: pass
    return None
```

### Expected diagnosis

Repeated immediate retries consume the scheduler and can worsen a bus fault; recovery needs a bounded, observable policy.

### Corrected code

```python
def read_with_retry_53(read, attempts):
    for attempt in range(attempts):
        try: return read()
        except OSError:
            if attempt == attempts - 1: raise
    raise AssertionError('unreachable')
```

### Regression tests

```python
# Regression: a permanent OSError is raised after exactly the configured attempts.
```

## EPY-M-054: schema drift

- Difficulty: Medium
- Language: Python for Embedded Systems (MicroPython/CircuitPython)
- Perspective: Serialization
- Concept: schema drift
- Symptom: Persisted settings cannot be loaded after a firmware update.
- Diagnostic goal: Version the stored schema and migrate known versions.

### Buggy code

```python
def load_54(data):
    return {'threshold': data['threshold']}
```

### Expected diagnosis

Reading fields without a version prevents controlled migration and turns old data into an opaque KeyError.

### Corrected code

```python
def load_54(data):
    version = data.get('version', 1)
    if version == 1:
        return {'threshold': data['threshold']}
    if version == 2:
        return {'threshold': data['limit']}
    raise ValueError('unsupported settings version')
```

### Regression tests

```python
assert load_54({'threshold': 3}) == {'threshold': 3}
assert load_54({'version': 2, 'limit': 4}) == {'threshold': 4}
```

## EPY-M-055: work done in ISR

- Difficulty: Medium
- Language: Python for Embedded Systems (MicroPython/CircuitPython)
- Perspective: Interrupt safety
- Concept: work done in ISR
- Symptom: The interrupt handler blocks or corrupts state.
- Diagnostic goal: Keep interrupt handlers short and hand work to the main loop.

### Buggy code

```python
def irq_55(state):
    state['count'] += 1
    read_sensor()
    print(state)
```

### Expected diagnosis

Peripheral access, allocation, and I/O inside an interrupt can be unsafe or unbounded.

### Corrected code

```python
def irq_55(state):
    state['count'] += 1
    state['pending'] = True
```

### Regression tests

```python
state = {'count': 0, 'pending': False}
irq_55(state)
assert state == {'count': 1, 'pending': True}
```

## EPY-M-056: off-by-one capacity

- Difficulty: Medium
- Language: Python for Embedded Systems (MicroPython/CircuitPython)
- Perspective: Ring buffers
- Concept: off-by-one capacity
- Symptom: A full buffer is mistaken for an empty buffer.
- Diagnostic goal: Reserve one slot or track size separately.

### Buggy code

```python
def push_56(items, value, capacity):
    if len(items) == capacity:
        return False
    items.append(value)
    return True
```

### Expected diagnosis

A list model is ambiguous about overwrite policy and gives no explicit distinction between full and empty states.

### Corrected code

```python
def push_56(items, value, capacity):
    if len(items) >= capacity:
        return False
    items.append(value)
    return True
```

### Regression tests

```python
items = []
assert push_56(items, 1, 1)
assert not push_56(items, 2, 1)
```

## EPY-M-057: watchdog fed during a hang

- Difficulty: Medium
- Language: Python for Embedded Systems (MicroPython/CircuitPython)
- Perspective: Watchdog design
- Concept: watchdog fed during a hang
- Symptom: A stuck loop prevents recovery.
- Diagnostic goal: Feed the watchdog only after essential work completes.

### Buggy code

```python
def service_57(work, watchdog):
    watchdog.feed()
    work()
```

### Expected diagnosis

Feeding before the work proves only that the loop started, so a blocked work call can still run forever.

### Corrected code

```python
def service_57(work, watchdog):
    work()
    watchdog.feed()
```

### Regression tests

```python
# Regression: a failed or blocked work call must not reach feed().
```

## EPY-M-058: address and register confused

- Difficulty: Medium
- Language: Python for Embedded Systems (MicroPython/CircuitPython)
- Perspective: I2C transaction
- Concept: address and register confused
- Symptom: Reads return bytes from the wrong device or register.
- Diagnostic goal: Keep bus address, register, and payload as separate fields.

### Buggy code

```python
def read_58(bus, address, register):
    return bus.readfrom_mem(register, address, 1)
```

### Expected diagnosis

The common MicroPython memory-read order is address, register, and length; swapping the first two changes the transaction.

### Corrected code

```python
def read_58(bus, address, register):
    return bus.readfrom_mem(address, register, 1)
```

### Regression tests

```python
# Regression: a fake bus should observe address=64, register=0x01, length=1.
```

## EPY-M-059: forgotten await

- Difficulty: Medium
- Language: Python for Embedded Systems (MicroPython/CircuitPython)
- Perspective: Async scheduling
- Concept: forgotten await
- Symptom: A coroutine object is stored instead of sensor data.
- Diagnostic goal: Trace the await boundary and return the resolved value.

### Buggy code

```python
async def sample_59(sensor):
    value = sensor.read_async()
    return value * 2
```

### Expected diagnosis

Calling an async method creates a coroutine; arithmetic must happen after awaiting it.

### Corrected code

```python
async def sample_59(sensor):
    value = await sensor.read_async()
    return value * 2
```

### Regression tests

```python
# Regression: run with an async fake sensor and assert the numeric result.
```

## EPY-M-060: invalid pin mode accepted

- Difficulty: Medium
- Language: Python for Embedded Systems (MicroPython/CircuitPython)
- Perspective: Configuration
- Concept: invalid pin mode accepted
- Symptom: A board fails later with a confusing hardware error.
- Diagnostic goal: Validate configuration at startup and fail close to the boundary.

### Buggy code

```python
def configure_60(pin, mode):
    pin.init(mode=mode)
    return pin
```

### Expected diagnosis

An arbitrary mode reaches the hardware API without a clear application-level contract.

### Corrected code

```python
def configure_60(pin, mode):
    if mode not in ('in', 'out'):
        raise ValueError('mode must be in or out')
    pin.init(mode=mode)
    return pin
```

### Regression tests

```python
# Regression: invalid modes raise before pin.init is called.
```

## EPY-M-061: integer truncation

- Difficulty: Medium
- Language: Python for Embedded Systems (MicroPython/CircuitPython)
- Perspective: Calibration
- Concept: integer truncation
- Symptom: Small sensor changes disappear.
- Diagnostic goal: Retain precision until formatting for display.

### Buggy code

```python
def calibrate_61(raw, offset):
    return int(raw + offset)
```

### Expected diagnosis

Converting to int during calibration discards fractional information that may matter to control decisions.

### Corrected code

```python
def calibrate_61(raw, offset):
    return raw + offset
```

### Regression tests

```python
assert calibrate_61(10.5, 0.25) == 10.75
```

## EPY-M-062: retry storm

- Difficulty: Medium
- Language: Python for Embedded Systems (MicroPython/CircuitPython)
- Perspective: Fault recovery
- Concept: retry storm
- Symptom: A disconnected peripheral is retried continuously and starves other tasks.
- Diagnostic goal: Bound retries and include a delay or backoff.

### Buggy code

```python
def read_with_retry_62(read, attempts):
    for _ in range(attempts):
        try: return read()
        except OSError: pass
    return None
```

### Expected diagnosis

Repeated immediate retries consume the scheduler and can worsen a bus fault; recovery needs a bounded, observable policy.

### Corrected code

```python
def read_with_retry_62(read, attempts):
    for attempt in range(attempts):
        try: return read()
        except OSError:
            if attempt == attempts - 1: raise
    raise AssertionError('unreachable')
```

### Regression tests

```python
# Regression: a permanent OSError is raised after exactly the configured attempts.
```

## EPY-M-063: schema drift

- Difficulty: Medium
- Language: Python for Embedded Systems (MicroPython/CircuitPython)
- Perspective: Serialization
- Concept: schema drift
- Symptom: Persisted settings cannot be loaded after a firmware update.
- Diagnostic goal: Version the stored schema and migrate known versions.

### Buggy code

```python
def load_63(data):
    return {'threshold': data['threshold']}
```

### Expected diagnosis

Reading fields without a version prevents controlled migration and turns old data into an opaque KeyError.

### Corrected code

```python
def load_63(data):
    version = data.get('version', 1)
    if version == 1:
        return {'threshold': data['threshold']}
    if version == 2:
        return {'threshold': data['limit']}
    raise ValueError('unsupported settings version')
```

### Regression tests

```python
assert load_63({'threshold': 3}) == {'threshold': 3}
assert load_63({'version': 2, 'limit': 4}) == {'threshold': 4}
```

## EPY-M-064: work done in ISR

- Difficulty: Medium
- Language: Python for Embedded Systems (MicroPython/CircuitPython)
- Perspective: Interrupt safety
- Concept: work done in ISR
- Symptom: The interrupt handler blocks or corrupts state.
- Diagnostic goal: Keep interrupt handlers short and hand work to the main loop.

### Buggy code

```python
def irq_64(state):
    state['count'] += 1
    read_sensor()
    print(state)
```

### Expected diagnosis

Peripheral access, allocation, and I/O inside an interrupt can be unsafe or unbounded.

### Corrected code

```python
def irq_64(state):
    state['count'] += 1
    state['pending'] = True
```

### Regression tests

```python
state = {'count': 0, 'pending': False}
irq_64(state)
assert state == {'count': 1, 'pending': True}
```

## EPY-M-065: off-by-one capacity

- Difficulty: Medium
- Language: Python for Embedded Systems (MicroPython/CircuitPython)
- Perspective: Ring buffers
- Concept: off-by-one capacity
- Symptom: A full buffer is mistaken for an empty buffer.
- Diagnostic goal: Reserve one slot or track size separately.

### Buggy code

```python
def push_65(items, value, capacity):
    if len(items) == capacity:
        return False
    items.append(value)
    return True
```

### Expected diagnosis

A list model is ambiguous about overwrite policy and gives no explicit distinction between full and empty states.

### Corrected code

```python
def push_65(items, value, capacity):
    if len(items) >= capacity:
        return False
    items.append(value)
    return True
```

### Regression tests

```python
items = []
assert push_65(items, 1, 1)
assert not push_65(items, 2, 1)
```

## EPY-M-066: watchdog fed during a hang

- Difficulty: Medium
- Language: Python for Embedded Systems (MicroPython/CircuitPython)
- Perspective: Watchdog design
- Concept: watchdog fed during a hang
- Symptom: A stuck loop prevents recovery.
- Diagnostic goal: Feed the watchdog only after essential work completes.

### Buggy code

```python
def service_66(work, watchdog):
    watchdog.feed()
    work()
```

### Expected diagnosis

Feeding before the work proves only that the loop started, so a blocked work call can still run forever.

### Corrected code

```python
def service_66(work, watchdog):
    work()
    watchdog.feed()
```

### Regression tests

```python
# Regression: a failed or blocked work call must not reach feed().
```

## EPY-M-067: address and register confused

- Difficulty: Medium
- Language: Python for Embedded Systems (MicroPython/CircuitPython)
- Perspective: I2C transaction
- Concept: address and register confused
- Symptom: Reads return bytes from the wrong device or register.
- Diagnostic goal: Keep bus address, register, and payload as separate fields.

### Buggy code

```python
def read_67(bus, address, register):
    return bus.readfrom_mem(register, address, 1)
```

### Expected diagnosis

The common MicroPython memory-read order is address, register, and length; swapping the first two changes the transaction.

### Corrected code

```python
def read_67(bus, address, register):
    return bus.readfrom_mem(address, register, 1)
```

### Regression tests

```python
# Regression: a fake bus should observe address=64, register=0x01, length=1.
```

## EPY-M-068: forgotten await

- Difficulty: Medium
- Language: Python for Embedded Systems (MicroPython/CircuitPython)
- Perspective: Async scheduling
- Concept: forgotten await
- Symptom: A coroutine object is stored instead of sensor data.
- Diagnostic goal: Trace the await boundary and return the resolved value.

### Buggy code

```python
async def sample_68(sensor):
    value = sensor.read_async()
    return value * 2
```

### Expected diagnosis

Calling an async method creates a coroutine; arithmetic must happen after awaiting it.

### Corrected code

```python
async def sample_68(sensor):
    value = await sensor.read_async()
    return value * 2
```

### Regression tests

```python
# Regression: run with an async fake sensor and assert the numeric result.
```

## EPY-M-069: invalid pin mode accepted

- Difficulty: Medium
- Language: Python for Embedded Systems (MicroPython/CircuitPython)
- Perspective: Configuration
- Concept: invalid pin mode accepted
- Symptom: A board fails later with a confusing hardware error.
- Diagnostic goal: Validate configuration at startup and fail close to the boundary.

### Buggy code

```python
def configure_69(pin, mode):
    pin.init(mode=mode)
    return pin
```

### Expected diagnosis

An arbitrary mode reaches the hardware API without a clear application-level contract.

### Corrected code

```python
def configure_69(pin, mode):
    if mode not in ('in', 'out'):
        raise ValueError('mode must be in or out')
    pin.init(mode=mode)
    return pin
```

### Regression tests

```python
# Regression: invalid modes raise before pin.init is called.
```

## EPY-M-070: integer truncation

- Difficulty: Medium
- Language: Python for Embedded Systems (MicroPython/CircuitPython)
- Perspective: Calibration
- Concept: integer truncation
- Symptom: Small sensor changes disappear.
- Diagnostic goal: Retain precision until formatting for display.

### Buggy code

```python
def calibrate_70(raw, offset):
    return int(raw + offset)
```

### Expected diagnosis

Converting to int during calibration discards fractional information that may matter to control decisions.

### Corrected code

```python
def calibrate_70(raw, offset):
    return raw + offset
```

### Regression tests

```python
assert calibrate_70(10.5, 0.25) == 10.75
```

## EPY-M-071: retry storm

- Difficulty: Medium
- Language: Python for Embedded Systems (MicroPython/CircuitPython)
- Perspective: Fault recovery
- Concept: retry storm
- Symptom: A disconnected peripheral is retried continuously and starves other tasks.
- Diagnostic goal: Bound retries and include a delay or backoff.

### Buggy code

```python
def read_with_retry_71(read, attempts):
    for _ in range(attempts):
        try: return read()
        except OSError: pass
    return None
```

### Expected diagnosis

Repeated immediate retries consume the scheduler and can worsen a bus fault; recovery needs a bounded, observable policy.

### Corrected code

```python
def read_with_retry_71(read, attempts):
    for attempt in range(attempts):
        try: return read()
        except OSError:
            if attempt == attempts - 1: raise
    raise AssertionError('unreachable')
```

### Regression tests

```python
# Regression: a permanent OSError is raised after exactly the configured attempts.
```

## EPY-M-072: schema drift

- Difficulty: Medium
- Language: Python for Embedded Systems (MicroPython/CircuitPython)
- Perspective: Serialization
- Concept: schema drift
- Symptom: Persisted settings cannot be loaded after a firmware update.
- Diagnostic goal: Version the stored schema and migrate known versions.

### Buggy code

```python
def load_72(data):
    return {'threshold': data['threshold']}
```

### Expected diagnosis

Reading fields without a version prevents controlled migration and turns old data into an opaque KeyError.

### Corrected code

```python
def load_72(data):
    version = data.get('version', 1)
    if version == 1:
        return {'threshold': data['threshold']}
    if version == 2:
        return {'threshold': data['limit']}
    raise ValueError('unsupported settings version')
```

### Regression tests

```python
assert load_72({'threshold': 3}) == {'threshold': 3}
assert load_72({'version': 2, 'limit': 4}) == {'threshold': 4}
```

## EPY-M-073: work done in ISR

- Difficulty: Medium
- Language: Python for Embedded Systems (MicroPython/CircuitPython)
- Perspective: Interrupt safety
- Concept: work done in ISR
- Symptom: The interrupt handler blocks or corrupts state.
- Diagnostic goal: Keep interrupt handlers short and hand work to the main loop.

### Buggy code

```python
def irq_73(state):
    state['count'] += 1
    read_sensor()
    print(state)
```

### Expected diagnosis

Peripheral access, allocation, and I/O inside an interrupt can be unsafe or unbounded.

### Corrected code

```python
def irq_73(state):
    state['count'] += 1
    state['pending'] = True
```

### Regression tests

```python
state = {'count': 0, 'pending': False}
irq_73(state)
assert state == {'count': 1, 'pending': True}
```

## EPY-M-074: off-by-one capacity

- Difficulty: Medium
- Language: Python for Embedded Systems (MicroPython/CircuitPython)
- Perspective: Ring buffers
- Concept: off-by-one capacity
- Symptom: A full buffer is mistaken for an empty buffer.
- Diagnostic goal: Reserve one slot or track size separately.

### Buggy code

```python
def push_74(items, value, capacity):
    if len(items) == capacity:
        return False
    items.append(value)
    return True
```

### Expected diagnosis

A list model is ambiguous about overwrite policy and gives no explicit distinction between full and empty states.

### Corrected code

```python
def push_74(items, value, capacity):
    if len(items) >= capacity:
        return False
    items.append(value)
    return True
```

### Regression tests

```python
items = []
assert push_74(items, 1, 1)
assert not push_74(items, 2, 1)
```

## EPY-M-075: watchdog fed during a hang

- Difficulty: Medium
- Language: Python for Embedded Systems (MicroPython/CircuitPython)
- Perspective: Watchdog design
- Concept: watchdog fed during a hang
- Symptom: A stuck loop prevents recovery.
- Diagnostic goal: Feed the watchdog only after essential work completes.

### Buggy code

```python
def service_75(work, watchdog):
    watchdog.feed()
    work()
```

### Expected diagnosis

Feeding before the work proves only that the loop started, so a blocked work call can still run forever.

### Corrected code

```python
def service_75(work, watchdog):
    work()
    watchdog.feed()
```

### Regression tests

```python
# Regression: a failed or blocked work call must not reach feed().
```

## EPY-M-076: address and register confused

- Difficulty: Medium
- Language: Python for Embedded Systems (MicroPython/CircuitPython)
- Perspective: I2C transaction
- Concept: address and register confused
- Symptom: Reads return bytes from the wrong device or register.
- Diagnostic goal: Keep bus address, register, and payload as separate fields.

### Buggy code

```python
def read_76(bus, address, register):
    return bus.readfrom_mem(register, address, 1)
```

### Expected diagnosis

The common MicroPython memory-read order is address, register, and length; swapping the first two changes the transaction.

### Corrected code

```python
def read_76(bus, address, register):
    return bus.readfrom_mem(address, register, 1)
```

### Regression tests

```python
# Regression: a fake bus should observe address=64, register=0x01, length=1.
```

## EPY-M-077: forgotten await

- Difficulty: Medium
- Language: Python for Embedded Systems (MicroPython/CircuitPython)
- Perspective: Async scheduling
- Concept: forgotten await
- Symptom: A coroutine object is stored instead of sensor data.
- Diagnostic goal: Trace the await boundary and return the resolved value.

### Buggy code

```python
async def sample_77(sensor):
    value = sensor.read_async()
    return value * 2
```

### Expected diagnosis

Calling an async method creates a coroutine; arithmetic must happen after awaiting it.

### Corrected code

```python
async def sample_77(sensor):
    value = await sensor.read_async()
    return value * 2
```

### Regression tests

```python
# Regression: run with an async fake sensor and assert the numeric result.
```

## EPY-M-078: invalid pin mode accepted

- Difficulty: Medium
- Language: Python for Embedded Systems (MicroPython/CircuitPython)
- Perspective: Configuration
- Concept: invalid pin mode accepted
- Symptom: A board fails later with a confusing hardware error.
- Diagnostic goal: Validate configuration at startup and fail close to the boundary.

### Buggy code

```python
def configure_78(pin, mode):
    pin.init(mode=mode)
    return pin
```

### Expected diagnosis

An arbitrary mode reaches the hardware API without a clear application-level contract.

### Corrected code

```python
def configure_78(pin, mode):
    if mode not in ('in', 'out'):
        raise ValueError('mode must be in or out')
    pin.init(mode=mode)
    return pin
```

### Regression tests

```python
# Regression: invalid modes raise before pin.init is called.
```

## EPY-M-079: integer truncation

- Difficulty: Medium
- Language: Python for Embedded Systems (MicroPython/CircuitPython)
- Perspective: Calibration
- Concept: integer truncation
- Symptom: Small sensor changes disappear.
- Diagnostic goal: Retain precision until formatting for display.

### Buggy code

```python
def calibrate_79(raw, offset):
    return int(raw + offset)
```

### Expected diagnosis

Converting to int during calibration discards fractional information that may matter to control decisions.

### Corrected code

```python
def calibrate_79(raw, offset):
    return raw + offset
```

### Regression tests

```python
assert calibrate_79(10.5, 0.25) == 10.75
```

## EPY-M-080: retry storm

- Difficulty: Medium
- Language: Python for Embedded Systems (MicroPython/CircuitPython)
- Perspective: Fault recovery
- Concept: retry storm
- Symptom: A disconnected peripheral is retried continuously and starves other tasks.
- Diagnostic goal: Bound retries and include a delay or backoff.

### Buggy code

```python
def read_with_retry_80(read, attempts):
    for _ in range(attempts):
        try: return read()
        except OSError: pass
    return None
```

### Expected diagnosis

Repeated immediate retries consume the scheduler and can worsen a bus fault; recovery needs a bounded, observable policy.

### Corrected code

```python
def read_with_retry_80(read, attempts):
    for attempt in range(attempts):
        try: return read()
        except OSError:
            if attempt == attempts - 1: raise
    raise AssertionError('unreachable')
```

### Regression tests

```python
# Regression: a permanent OSError is raised after exactly the configured attempts.
```

## EPY-M-081: schema drift

- Difficulty: Medium
- Language: Python for Embedded Systems (MicroPython/CircuitPython)
- Perspective: Serialization
- Concept: schema drift
- Symptom: Persisted settings cannot be loaded after a firmware update.
- Diagnostic goal: Version the stored schema and migrate known versions.

### Buggy code

```python
def load_81(data):
    return {'threshold': data['threshold']}
```

### Expected diagnosis

Reading fields without a version prevents controlled migration and turns old data into an opaque KeyError.

### Corrected code

```python
def load_81(data):
    version = data.get('version', 1)
    if version == 1:
        return {'threshold': data['threshold']}
    if version == 2:
        return {'threshold': data['limit']}
    raise ValueError('unsupported settings version')
```

### Regression tests

```python
assert load_81({'threshold': 3}) == {'threshold': 3}
assert load_81({'version': 2, 'limit': 4}) == {'threshold': 4}
```

## EPY-M-082: work done in ISR

- Difficulty: Medium
- Language: Python for Embedded Systems (MicroPython/CircuitPython)
- Perspective: Interrupt safety
- Concept: work done in ISR
- Symptom: The interrupt handler blocks or corrupts state.
- Diagnostic goal: Keep interrupt handlers short and hand work to the main loop.

### Buggy code

```python
def irq_82(state):
    state['count'] += 1
    read_sensor()
    print(state)
```

### Expected diagnosis

Peripheral access, allocation, and I/O inside an interrupt can be unsafe or unbounded.

### Corrected code

```python
def irq_82(state):
    state['count'] += 1
    state['pending'] = True
```

### Regression tests

```python
state = {'count': 0, 'pending': False}
irq_82(state)
assert state == {'count': 1, 'pending': True}
```

## EPY-M-083: off-by-one capacity

- Difficulty: Medium
- Language: Python for Embedded Systems (MicroPython/CircuitPython)
- Perspective: Ring buffers
- Concept: off-by-one capacity
- Symptom: A full buffer is mistaken for an empty buffer.
- Diagnostic goal: Reserve one slot or track size separately.

### Buggy code

```python
def push_83(items, value, capacity):
    if len(items) == capacity:
        return False
    items.append(value)
    return True
```

### Expected diagnosis

A list model is ambiguous about overwrite policy and gives no explicit distinction between full and empty states.

### Corrected code

```python
def push_83(items, value, capacity):
    if len(items) >= capacity:
        return False
    items.append(value)
    return True
```

### Regression tests

```python
items = []
assert push_83(items, 1, 1)
assert not push_83(items, 2, 1)
```

## EPY-M-084: watchdog fed during a hang

- Difficulty: Medium
- Language: Python for Embedded Systems (MicroPython/CircuitPython)
- Perspective: Watchdog design
- Concept: watchdog fed during a hang
- Symptom: A stuck loop prevents recovery.
- Diagnostic goal: Feed the watchdog only after essential work completes.

### Buggy code

```python
def service_84(work, watchdog):
    watchdog.feed()
    work()
```

### Expected diagnosis

Feeding before the work proves only that the loop started, so a blocked work call can still run forever.

### Corrected code

```python
def service_84(work, watchdog):
    work()
    watchdog.feed()
```

### Regression tests

```python
# Regression: a failed or blocked work call must not reach feed().
```

## EPY-M-085: address and register confused

- Difficulty: Medium
- Language: Python for Embedded Systems (MicroPython/CircuitPython)
- Perspective: I2C transaction
- Concept: address and register confused
- Symptom: Reads return bytes from the wrong device or register.
- Diagnostic goal: Keep bus address, register, and payload as separate fields.

### Buggy code

```python
def read_85(bus, address, register):
    return bus.readfrom_mem(register, address, 1)
```

### Expected diagnosis

The common MicroPython memory-read order is address, register, and length; swapping the first two changes the transaction.

### Corrected code

```python
def read_85(bus, address, register):
    return bus.readfrom_mem(address, register, 1)
```

### Regression tests

```python
# Regression: a fake bus should observe address=64, register=0x01, length=1.
```

## EPY-M-086: forgotten await

- Difficulty: Medium
- Language: Python for Embedded Systems (MicroPython/CircuitPython)
- Perspective: Async scheduling
- Concept: forgotten await
- Symptom: A coroutine object is stored instead of sensor data.
- Diagnostic goal: Trace the await boundary and return the resolved value.

### Buggy code

```python
async def sample_86(sensor):
    value = sensor.read_async()
    return value * 2
```

### Expected diagnosis

Calling an async method creates a coroutine; arithmetic must happen after awaiting it.

### Corrected code

```python
async def sample_86(sensor):
    value = await sensor.read_async()
    return value * 2
```

### Regression tests

```python
# Regression: run with an async fake sensor and assert the numeric result.
```

## EPY-M-087: invalid pin mode accepted

- Difficulty: Medium
- Language: Python for Embedded Systems (MicroPython/CircuitPython)
- Perspective: Configuration
- Concept: invalid pin mode accepted
- Symptom: A board fails later with a confusing hardware error.
- Diagnostic goal: Validate configuration at startup and fail close to the boundary.

### Buggy code

```python
def configure_87(pin, mode):
    pin.init(mode=mode)
    return pin
```

### Expected diagnosis

An arbitrary mode reaches the hardware API without a clear application-level contract.

### Corrected code

```python
def configure_87(pin, mode):
    if mode not in ('in', 'out'):
        raise ValueError('mode must be in or out')
    pin.init(mode=mode)
    return pin
```

### Regression tests

```python
# Regression: invalid modes raise before pin.init is called.
```

## EPY-M-088: integer truncation

- Difficulty: Medium
- Language: Python for Embedded Systems (MicroPython/CircuitPython)
- Perspective: Calibration
- Concept: integer truncation
- Symptom: Small sensor changes disappear.
- Diagnostic goal: Retain precision until formatting for display.

### Buggy code

```python
def calibrate_88(raw, offset):
    return int(raw + offset)
```

### Expected diagnosis

Converting to int during calibration discards fractional information that may matter to control decisions.

### Corrected code

```python
def calibrate_88(raw, offset):
    return raw + offset
```

### Regression tests

```python
assert calibrate_88(10.5, 0.25) == 10.75
```

## EPY-M-089: retry storm

- Difficulty: Medium
- Language: Python for Embedded Systems (MicroPython/CircuitPython)
- Perspective: Fault recovery
- Concept: retry storm
- Symptom: A disconnected peripheral is retried continuously and starves other tasks.
- Diagnostic goal: Bound retries and include a delay or backoff.

### Buggy code

```python
def read_with_retry_89(read, attempts):
    for _ in range(attempts):
        try: return read()
        except OSError: pass
    return None
```

### Expected diagnosis

Repeated immediate retries consume the scheduler and can worsen a bus fault; recovery needs a bounded, observable policy.

### Corrected code

```python
def read_with_retry_89(read, attempts):
    for attempt in range(attempts):
        try: return read()
        except OSError:
            if attempt == attempts - 1: raise
    raise AssertionError('unreachable')
```

### Regression tests

```python
# Regression: a permanent OSError is raised after exactly the configured attempts.
```

## EPY-M-090: schema drift

- Difficulty: Medium
- Language: Python for Embedded Systems (MicroPython/CircuitPython)
- Perspective: Serialization
- Concept: schema drift
- Symptom: Persisted settings cannot be loaded after a firmware update.
- Diagnostic goal: Version the stored schema and migrate known versions.

### Buggy code

```python
def load_90(data):
    return {'threshold': data['threshold']}
```

### Expected diagnosis

Reading fields without a version prevents controlled migration and turns old data into an opaque KeyError.

### Corrected code

```python
def load_90(data):
    version = data.get('version', 1)
    if version == 1:
        return {'threshold': data['threshold']}
    if version == 2:
        return {'threshold': data['limit']}
    raise ValueError('unsupported settings version')
```

### Regression tests

```python
assert load_90({'threshold': 3}) == {'threshold': 3}
assert load_90({'version': 2, 'limit': 4}) == {'threshold': 4}
```

## EPY-M-091: work done in ISR

- Difficulty: Medium
- Language: Python for Embedded Systems (MicroPython/CircuitPython)
- Perspective: Interrupt safety
- Concept: work done in ISR
- Symptom: The interrupt handler blocks or corrupts state.
- Diagnostic goal: Keep interrupt handlers short and hand work to the main loop.

### Buggy code

```python
def irq_91(state):
    state['count'] += 1
    read_sensor()
    print(state)
```

### Expected diagnosis

Peripheral access, allocation, and I/O inside an interrupt can be unsafe or unbounded.

### Corrected code

```python
def irq_91(state):
    state['count'] += 1
    state['pending'] = True
```

### Regression tests

```python
state = {'count': 0, 'pending': False}
irq_91(state)
assert state == {'count': 1, 'pending': True}
```

## EPY-M-092: off-by-one capacity

- Difficulty: Medium
- Language: Python for Embedded Systems (MicroPython/CircuitPython)
- Perspective: Ring buffers
- Concept: off-by-one capacity
- Symptom: A full buffer is mistaken for an empty buffer.
- Diagnostic goal: Reserve one slot or track size separately.

### Buggy code

```python
def push_92(items, value, capacity):
    if len(items) == capacity:
        return False
    items.append(value)
    return True
```

### Expected diagnosis

A list model is ambiguous about overwrite policy and gives no explicit distinction between full and empty states.

### Corrected code

```python
def push_92(items, value, capacity):
    if len(items) >= capacity:
        return False
    items.append(value)
    return True
```

### Regression tests

```python
items = []
assert push_92(items, 1, 1)
assert not push_92(items, 2, 1)
```

## EPY-M-093: watchdog fed during a hang

- Difficulty: Medium
- Language: Python for Embedded Systems (MicroPython/CircuitPython)
- Perspective: Watchdog design
- Concept: watchdog fed during a hang
- Symptom: A stuck loop prevents recovery.
- Diagnostic goal: Feed the watchdog only after essential work completes.

### Buggy code

```python
def service_93(work, watchdog):
    watchdog.feed()
    work()
```

### Expected diagnosis

Feeding before the work proves only that the loop started, so a blocked work call can still run forever.

### Corrected code

```python
def service_93(work, watchdog):
    work()
    watchdog.feed()
```

### Regression tests

```python
# Regression: a failed or blocked work call must not reach feed().
```

## EPY-M-094: address and register confused

- Difficulty: Medium
- Language: Python for Embedded Systems (MicroPython/CircuitPython)
- Perspective: I2C transaction
- Concept: address and register confused
- Symptom: Reads return bytes from the wrong device or register.
- Diagnostic goal: Keep bus address, register, and payload as separate fields.

### Buggy code

```python
def read_94(bus, address, register):
    return bus.readfrom_mem(register, address, 1)
```

### Expected diagnosis

The common MicroPython memory-read order is address, register, and length; swapping the first two changes the transaction.

### Corrected code

```python
def read_94(bus, address, register):
    return bus.readfrom_mem(address, register, 1)
```

### Regression tests

```python
# Regression: a fake bus should observe address=64, register=0x01, length=1.
```

## EPY-M-095: forgotten await

- Difficulty: Medium
- Language: Python for Embedded Systems (MicroPython/CircuitPython)
- Perspective: Async scheduling
- Concept: forgotten await
- Symptom: A coroutine object is stored instead of sensor data.
- Diagnostic goal: Trace the await boundary and return the resolved value.

### Buggy code

```python
async def sample_95(sensor):
    value = sensor.read_async()
    return value * 2
```

### Expected diagnosis

Calling an async method creates a coroutine; arithmetic must happen after awaiting it.

### Corrected code

```python
async def sample_95(sensor):
    value = await sensor.read_async()
    return value * 2
```

### Regression tests

```python
# Regression: run with an async fake sensor and assert the numeric result.
```

## EPY-M-096: invalid pin mode accepted

- Difficulty: Medium
- Language: Python for Embedded Systems (MicroPython/CircuitPython)
- Perspective: Configuration
- Concept: invalid pin mode accepted
- Symptom: A board fails later with a confusing hardware error.
- Diagnostic goal: Validate configuration at startup and fail close to the boundary.

### Buggy code

```python
def configure_96(pin, mode):
    pin.init(mode=mode)
    return pin
```

### Expected diagnosis

An arbitrary mode reaches the hardware API without a clear application-level contract.

### Corrected code

```python
def configure_96(pin, mode):
    if mode not in ('in', 'out'):
        raise ValueError('mode must be in or out')
    pin.init(mode=mode)
    return pin
```

### Regression tests

```python
# Regression: invalid modes raise before pin.init is called.
```

## EPY-M-097: integer truncation

- Difficulty: Medium
- Language: Python for Embedded Systems (MicroPython/CircuitPython)
- Perspective: Calibration
- Concept: integer truncation
- Symptom: Small sensor changes disappear.
- Diagnostic goal: Retain precision until formatting for display.

### Buggy code

```python
def calibrate_97(raw, offset):
    return int(raw + offset)
```

### Expected diagnosis

Converting to int during calibration discards fractional information that may matter to control decisions.

### Corrected code

```python
def calibrate_97(raw, offset):
    return raw + offset
```

### Regression tests

```python
assert calibrate_97(10.5, 0.25) == 10.75
```

## EPY-M-098: retry storm

- Difficulty: Medium
- Language: Python for Embedded Systems (MicroPython/CircuitPython)
- Perspective: Fault recovery
- Concept: retry storm
- Symptom: A disconnected peripheral is retried continuously and starves other tasks.
- Diagnostic goal: Bound retries and include a delay or backoff.

### Buggy code

```python
def read_with_retry_98(read, attempts):
    for _ in range(attempts):
        try: return read()
        except OSError: pass
    return None
```

### Expected diagnosis

Repeated immediate retries consume the scheduler and can worsen a bus fault; recovery needs a bounded, observable policy.

### Corrected code

```python
def read_with_retry_98(read, attempts):
    for attempt in range(attempts):
        try: return read()
        except OSError:
            if attempt == attempts - 1: raise
    raise AssertionError('unreachable')
```

### Regression tests

```python
# Regression: a permanent OSError is raised after exactly the configured attempts.
```

## EPY-M-099: schema drift

- Difficulty: Medium
- Language: Python for Embedded Systems (MicroPython/CircuitPython)
- Perspective: Serialization
- Concept: schema drift
- Symptom: Persisted settings cannot be loaded after a firmware update.
- Diagnostic goal: Version the stored schema and migrate known versions.

### Buggy code

```python
def load_99(data):
    return {'threshold': data['threshold']}
```

### Expected diagnosis

Reading fields without a version prevents controlled migration and turns old data into an opaque KeyError.

### Corrected code

```python
def load_99(data):
    version = data.get('version', 1)
    if version == 1:
        return {'threshold': data['threshold']}
    if version == 2:
        return {'threshold': data['limit']}
    raise ValueError('unsupported settings version')
```

### Regression tests

```python
assert load_99({'threshold': 3}) == {'threshold': 3}
assert load_99({'version': 2, 'limit': 4}) == {'threshold': 4}
```

## EPY-M-100: work done in ISR

- Difficulty: Medium
- Language: Python for Embedded Systems (MicroPython/CircuitPython)
- Perspective: Interrupt safety
- Concept: work done in ISR
- Symptom: The interrupt handler blocks or corrupts state.
- Diagnostic goal: Keep interrupt handlers short and hand work to the main loop.

### Buggy code

```python
def irq_100(state):
    state['count'] += 1
    read_sensor()
    print(state)
```

### Expected diagnosis

Peripheral access, allocation, and I/O inside an interrupt can be unsafe or unbounded.

### Corrected code

```python
def irq_100(state):
    state['count'] += 1
    state['pending'] = True
```

### Regression tests

```python
state = {'count': 0, 'pending': False}
irq_100(state)
assert state == {'count': 1, 'pending': True}
```

## EPY-H-001: jitter from allocation

- Difficulty: Hard
- Language: Python for Embedded Systems (MicroPython/CircuitPython)
- Perspective: Real-time reasoning
- Concept: jitter from allocation
- Symptom: A control loop occasionally misses its deadline.
- Diagnostic goal: Move allocation and unpredictable work out of the hot path.

### Buggy code

```python
def control_1(samples):
    values = [sample * 2 for sample in samples]
    return sum(values) / len(values)
```

### Expected diagnosis

Creating a list in every control iteration adds memory pressure and latency variance on constrained devices.

### Corrected code

```python
def control_1(samples):
    total = 0
    count = 0
    for sample in samples:
        total += sample * 2
        count += 1
    return total / count if count else 0
```

### Regression tests

```python
assert control_1([1, 2, 3]) == 4
assert control_1([]) == 0
```

## EPY-H-002: non-atomic multi-field update

- Difficulty: Hard
- Language: Python for Embedded Systems (MicroPython/CircuitPython)
- Perspective: Interrupt/main-loop race
- Concept: non-atomic multi-field update
- Symptom: A snapshot contains a mixed timestamp and value.
- Diagnostic goal: Publish a complete snapshot with a consistency protocol.

### Buggy code

```python
def snapshot_2(state):
    return state['timestamp'], state['value']
```

### Expected diagnosis

An interrupt can update the two fields between reads, so the pair may never have existed together.

### Corrected code

```python
def snapshot_2(state):
    first = state['sequence']
    if first % 2:
        return None
    result = (state['timestamp'], state['value'])
    if state['sequence'] != first:
        return None
    return result
```

### Regression tests

```python
# Regression: odd or changed sequence numbers cause a retry instead of a mixed snapshot.
```

## EPY-H-003: length field trust

- Difficulty: Hard
- Language: Python for Embedded Systems (MicroPython/CircuitPython)
- Perspective: Protocol security
- Concept: length field trust
- Symptom: A malformed packet causes excessive allocation.
- Diagnostic goal: Validate framing and maximum length before allocating.

### Buggy code

```python
def decode_3(packet):
    size = int.from_bytes(packet[:2], 'big')
    payload = packet[2:2 + size]
    return payload
```

### Expected diagnosis

The declared length is trusted without checking the header, maximum frame size, or truncation.

### Corrected code

```python
def decode_3(packet, maximum=256):
    if len(packet) < 2:
        raise ValueError('short header')
    size = int.from_bytes(packet[:2], 'big')
    if size > maximum or len(packet) != size + 2:
        raise ValueError('invalid frame')
    return packet[2:]
```

### Regression tests

```python
assert decode_3(b'\x00\x02ok') == b'ok'
# Regression: reject short, oversized, and truncated frames.
```

## EPY-H-004: busy wait

- Difficulty: Hard
- Language: Python for Embedded Systems (MicroPython/CircuitPython)
- Perspective: Power budgeting
- Concept: busy wait
- Symptom: Sleep current is much higher than expected.
- Diagnostic goal: Replace polling with a deadline or hardware wake source.

### Buggy code

```python
def wait_4(clock, deadline):
    while clock.now() < deadline:
        pass
```

### Expected diagnosis

A tight polling loop keeps the CPU active and consumes power while waiting for an external event.

### Corrected code

```python
def wait_4(clock, deadline):
    remaining = deadline - clock.now()
    if remaining > 0:
        clock.sleep(remaining)
```

### Regression tests

```python
# Regression: positive remaining time calls sleep once; expired deadlines do not.
```

## EPY-H-005: peripheral left enabled

- Difficulty: Hard
- Language: Python for Embedded Systems (MicroPython/CircuitPython)
- Perspective: Resource lifetime
- Concept: peripheral left enabled
- Symptom: The sensor remains powered after a failed read.
- Diagnostic goal: Use a cleanup boundary even when the operation raises.

### Buggy code

```python
def read_5(sensor):
    sensor.enable()
    value = sensor.read()
    sensor.disable()
    return value
```

### Expected diagnosis

An exception skips disable, leaving the peripheral and possibly the bus in an unsafe state.

### Corrected code

```python
def read_5(sensor):
    sensor.enable()
    try:
        return sensor.read()
    finally:
        sensor.disable()
```

### Regression tests

```python
# Regression: fake sensor records disable after both success and failure.
```

## EPY-H-006: overflow-prone accumulation

- Difficulty: Hard
- Language: Python for Embedded Systems (MicroPython/CircuitPython)
- Perspective: Numeric stability
- Concept: overflow-prone accumulation
- Symptom: A long-running total loses precision or wraps in fixed-width storage.
- Diagnostic goal: Bound or rescale state according to the measurement contract.

### Buggy code

```python
def accumulate_6(total, sample):
    return total + sample
```

### Expected diagnosis

An unbounded accumulator can exceed the representation or lose useful resolution over long uptime.

### Corrected code

```python
def accumulate_6(total, sample, maximum=1000000):
    result = total + sample
    return min(result, maximum)
```

### Regression tests

```python
assert accumulate_6(999, 2, 1000) == 1000
```

## EPY-H-007: illegal transition

- Difficulty: Hard
- Language: Python for Embedded Systems (MicroPython/CircuitPython)
- Perspective: State machine
- Concept: illegal transition
- Symptom: A device enters a state in which commands are unsafe.
- Diagnostic goal: Centralize legal transitions and reject invalid events.

### Buggy code

```python
def transition_7(state, event):
    if event == 'start': return 'running'
    if event == 'stop': return 'idle'
    return state
```

### Expected diagnosis

The transition table ignores the current state, so stop can succeed before start and start can restart a faulted device.

### Corrected code

```python
def transition_7(state, event):
    allowed = {'idle': {'start': 'running'}, 'running': {'stop': 'idle'}}
    if event not in allowed.get(state, {}):
        raise ValueError('illegal transition')
    return allowed[state][event]
```

### Regression tests

```python
assert transition_7('idle', 'start') == 'running'
try: transition_7('idle', 'stop')
except ValueError: pass
else: raise AssertionError
```

## EPY-H-008: non-idempotent restart

- Difficulty: Hard
- Language: Python for Embedded Systems (MicroPython/CircuitPython)
- Perspective: Watchdog recovery
- Concept: non-idempotent restart
- Symptom: Recovery repeats an action and duplicates an external side effect.
- Diagnostic goal: Make recovery steps idempotent and record progress.

### Buggy code

```python
def recover_8(device):
    device.close_valve()
    device.close_valve()
    device.reset()
```

### Expected diagnosis

Repeating a non-idempotent command can damage hardware or produce a different result on the second attempt.

### Corrected code

```python
def recover_8(device):
    if not device.is_closed():
        device.close_valve()
    device.reset()
```

### Regression tests

```python
# Regression: recovery called twice closes the valve once and resets safely.
```

## EPY-H-009: hardware calls in business logic

- Difficulty: Hard
- Language: Python for Embedded Systems (MicroPython/CircuitPython)
- Perspective: Testability
- Concept: hardware calls in business logic
- Symptom: The algorithm cannot be tested without a board.
- Diagnostic goal: Inject a narrow hardware interface and test the pure decision logic separately.

### Buggy code

```python
def alarm_9(reading):
    Pin(2, Pin.OUT).value(1 if reading > 70 else 0)
```

### Expected diagnosis

Constructing and driving hardware inside the decision function couples policy to a specific runtime and pin.

### Corrected code

```python
def alarm_9(reading, output):
    output( reading > 70 )
```

### Regression tests

```python
seen = []
alarm_9(71, seen.append)
assert seen == [True]
alarm_9(70, seen.append)
assert seen == [True, False]
```

## EPY-H-010: single fault aborts startup

- Difficulty: Hard
- Language: Python for Embedded Systems (MicroPython/CircuitPython)
- Perspective: Boot resilience
- Concept: single fault aborts startup
- Symptom: One optional peripheral prevents the core device from booting.
- Diagnostic goal: Isolate optional initialization and expose degraded operation.

### Buggy code

```python
def boot_10(display, sensor):
    display.init()
    sensor.init()
    return 'ready'
```

### Expected diagnosis

A failure in a nonessential component aborts the whole boot path without recording the degraded capability.

### Corrected code

```python
def boot_10(display, sensor):
    display.init()
    try:
        sensor.init()
        return 'ready'
    except OSError:
        return 'display-only'
```

### Regression tests

```python
# Regression: sensor failure returns display-only while display failure still propagates.
```

## EPY-H-011: jitter from allocation

- Difficulty: Hard
- Language: Python for Embedded Systems (MicroPython/CircuitPython)
- Perspective: Real-time reasoning
- Concept: jitter from allocation
- Symptom: A control loop occasionally misses its deadline.
- Diagnostic goal: Move allocation and unpredictable work out of the hot path.

### Buggy code

```python
def control_11(samples):
    values = [sample * 2 for sample in samples]
    return sum(values) / len(values)
```

### Expected diagnosis

Creating a list in every control iteration adds memory pressure and latency variance on constrained devices.

### Corrected code

```python
def control_11(samples):
    total = 0
    count = 0
    for sample in samples:
        total += sample * 2
        count += 1
    return total / count if count else 0
```

### Regression tests

```python
assert control_11([1, 2, 3]) == 4
assert control_11([]) == 0
```

## EPY-H-012: non-atomic multi-field update

- Difficulty: Hard
- Language: Python for Embedded Systems (MicroPython/CircuitPython)
- Perspective: Interrupt/main-loop race
- Concept: non-atomic multi-field update
- Symptom: A snapshot contains a mixed timestamp and value.
- Diagnostic goal: Publish a complete snapshot with a consistency protocol.

### Buggy code

```python
def snapshot_12(state):
    return state['timestamp'], state['value']
```

### Expected diagnosis

An interrupt can update the two fields between reads, so the pair may never have existed together.

### Corrected code

```python
def snapshot_12(state):
    first = state['sequence']
    if first % 2:
        return None
    result = (state['timestamp'], state['value'])
    if state['sequence'] != first:
        return None
    return result
```

### Regression tests

```python
# Regression: odd or changed sequence numbers cause a retry instead of a mixed snapshot.
```

## EPY-H-013: length field trust

- Difficulty: Hard
- Language: Python for Embedded Systems (MicroPython/CircuitPython)
- Perspective: Protocol security
- Concept: length field trust
- Symptom: A malformed packet causes excessive allocation.
- Diagnostic goal: Validate framing and maximum length before allocating.

### Buggy code

```python
def decode_13(packet):
    size = int.from_bytes(packet[:2], 'big')
    payload = packet[2:2 + size]
    return payload
```

### Expected diagnosis

The declared length is trusted without checking the header, maximum frame size, or truncation.

### Corrected code

```python
def decode_13(packet, maximum=256):
    if len(packet) < 2:
        raise ValueError('short header')
    size = int.from_bytes(packet[:2], 'big')
    if size > maximum or len(packet) != size + 2:
        raise ValueError('invalid frame')
    return packet[2:]
```

### Regression tests

```python
assert decode_13(b'\x00\x02ok') == b'ok'
# Regression: reject short, oversized, and truncated frames.
```

## EPY-H-014: busy wait

- Difficulty: Hard
- Language: Python for Embedded Systems (MicroPython/CircuitPython)
- Perspective: Power budgeting
- Concept: busy wait
- Symptom: Sleep current is much higher than expected.
- Diagnostic goal: Replace polling with a deadline or hardware wake source.

### Buggy code

```python
def wait_14(clock, deadline):
    while clock.now() < deadline:
        pass
```

### Expected diagnosis

A tight polling loop keeps the CPU active and consumes power while waiting for an external event.

### Corrected code

```python
def wait_14(clock, deadline):
    remaining = deadline - clock.now()
    if remaining > 0:
        clock.sleep(remaining)
```

### Regression tests

```python
# Regression: positive remaining time calls sleep once; expired deadlines do not.
```

## EPY-H-015: peripheral left enabled

- Difficulty: Hard
- Language: Python for Embedded Systems (MicroPython/CircuitPython)
- Perspective: Resource lifetime
- Concept: peripheral left enabled
- Symptom: The sensor remains powered after a failed read.
- Diagnostic goal: Use a cleanup boundary even when the operation raises.

### Buggy code

```python
def read_15(sensor):
    sensor.enable()
    value = sensor.read()
    sensor.disable()
    return value
```

### Expected diagnosis

An exception skips disable, leaving the peripheral and possibly the bus in an unsafe state.

### Corrected code

```python
def read_15(sensor):
    sensor.enable()
    try:
        return sensor.read()
    finally:
        sensor.disable()
```

### Regression tests

```python
# Regression: fake sensor records disable after both success and failure.
```

## EPY-H-016: overflow-prone accumulation

- Difficulty: Hard
- Language: Python for Embedded Systems (MicroPython/CircuitPython)
- Perspective: Numeric stability
- Concept: overflow-prone accumulation
- Symptom: A long-running total loses precision or wraps in fixed-width storage.
- Diagnostic goal: Bound or rescale state according to the measurement contract.

### Buggy code

```python
def accumulate_16(total, sample):
    return total + sample
```

### Expected diagnosis

An unbounded accumulator can exceed the representation or lose useful resolution over long uptime.

### Corrected code

```python
def accumulate_16(total, sample, maximum=1000000):
    result = total + sample
    return min(result, maximum)
```

### Regression tests

```python
assert accumulate_16(999, 2, 1000) == 1000
```

## EPY-H-017: illegal transition

- Difficulty: Hard
- Language: Python for Embedded Systems (MicroPython/CircuitPython)
- Perspective: State machine
- Concept: illegal transition
- Symptom: A device enters a state in which commands are unsafe.
- Diagnostic goal: Centralize legal transitions and reject invalid events.

### Buggy code

```python
def transition_17(state, event):
    if event == 'start': return 'running'
    if event == 'stop': return 'idle'
    return state
```

### Expected diagnosis

The transition table ignores the current state, so stop can succeed before start and start can restart a faulted device.

### Corrected code

```python
def transition_17(state, event):
    allowed = {'idle': {'start': 'running'}, 'running': {'stop': 'idle'}}
    if event not in allowed.get(state, {}):
        raise ValueError('illegal transition')
    return allowed[state][event]
```

### Regression tests

```python
assert transition_17('idle', 'start') == 'running'
try: transition_17('idle', 'stop')
except ValueError: pass
else: raise AssertionError
```

## EPY-H-018: non-idempotent restart

- Difficulty: Hard
- Language: Python for Embedded Systems (MicroPython/CircuitPython)
- Perspective: Watchdog recovery
- Concept: non-idempotent restart
- Symptom: Recovery repeats an action and duplicates an external side effect.
- Diagnostic goal: Make recovery steps idempotent and record progress.

### Buggy code

```python
def recover_18(device):
    device.close_valve()
    device.close_valve()
    device.reset()
```

### Expected diagnosis

Repeating a non-idempotent command can damage hardware or produce a different result on the second attempt.

### Corrected code

```python
def recover_18(device):
    if not device.is_closed():
        device.close_valve()
    device.reset()
```

### Regression tests

```python
# Regression: recovery called twice closes the valve once and resets safely.
```

## EPY-H-019: hardware calls in business logic

- Difficulty: Hard
- Language: Python for Embedded Systems (MicroPython/CircuitPython)
- Perspective: Testability
- Concept: hardware calls in business logic
- Symptom: The algorithm cannot be tested without a board.
- Diagnostic goal: Inject a narrow hardware interface and test the pure decision logic separately.

### Buggy code

```python
def alarm_19(reading):
    Pin(2, Pin.OUT).value(1 if reading > 70 else 0)
```

### Expected diagnosis

Constructing and driving hardware inside the decision function couples policy to a specific runtime and pin.

### Corrected code

```python
def alarm_19(reading, output):
    output( reading > 70 )
```

### Regression tests

```python
seen = []
alarm_19(71, seen.append)
assert seen == [True]
alarm_19(70, seen.append)
assert seen == [True, False]
```

## EPY-H-020: single fault aborts startup

- Difficulty: Hard
- Language: Python for Embedded Systems (MicroPython/CircuitPython)
- Perspective: Boot resilience
- Concept: single fault aborts startup
- Symptom: One optional peripheral prevents the core device from booting.
- Diagnostic goal: Isolate optional initialization and expose degraded operation.

### Buggy code

```python
def boot_20(display, sensor):
    display.init()
    sensor.init()
    return 'ready'
```

### Expected diagnosis

A failure in a nonessential component aborts the whole boot path without recording the degraded capability.

### Corrected code

```python
def boot_20(display, sensor):
    display.init()
    try:
        sensor.init()
        return 'ready'
    except OSError:
        return 'display-only'
```

### Regression tests

```python
# Regression: sensor failure returns display-only while display failure still propagates.
```

## EPY-H-021: jitter from allocation

- Difficulty: Hard
- Language: Python for Embedded Systems (MicroPython/CircuitPython)
- Perspective: Real-time reasoning
- Concept: jitter from allocation
- Symptom: A control loop occasionally misses its deadline.
- Diagnostic goal: Move allocation and unpredictable work out of the hot path.

### Buggy code

```python
def control_21(samples):
    values = [sample * 2 for sample in samples]
    return sum(values) / len(values)
```

### Expected diagnosis

Creating a list in every control iteration adds memory pressure and latency variance on constrained devices.

### Corrected code

```python
def control_21(samples):
    total = 0
    count = 0
    for sample in samples:
        total += sample * 2
        count += 1
    return total / count if count else 0
```

### Regression tests

```python
assert control_21([1, 2, 3]) == 4
assert control_21([]) == 0
```

## EPY-H-022: non-atomic multi-field update

- Difficulty: Hard
- Language: Python for Embedded Systems (MicroPython/CircuitPython)
- Perspective: Interrupt/main-loop race
- Concept: non-atomic multi-field update
- Symptom: A snapshot contains a mixed timestamp and value.
- Diagnostic goal: Publish a complete snapshot with a consistency protocol.

### Buggy code

```python
def snapshot_22(state):
    return state['timestamp'], state['value']
```

### Expected diagnosis

An interrupt can update the two fields between reads, so the pair may never have existed together.

### Corrected code

```python
def snapshot_22(state):
    first = state['sequence']
    if first % 2:
        return None
    result = (state['timestamp'], state['value'])
    if state['sequence'] != first:
        return None
    return result
```

### Regression tests

```python
# Regression: odd or changed sequence numbers cause a retry instead of a mixed snapshot.
```

## EPY-H-023: length field trust

- Difficulty: Hard
- Language: Python for Embedded Systems (MicroPython/CircuitPython)
- Perspective: Protocol security
- Concept: length field trust
- Symptom: A malformed packet causes excessive allocation.
- Diagnostic goal: Validate framing and maximum length before allocating.

### Buggy code

```python
def decode_23(packet):
    size = int.from_bytes(packet[:2], 'big')
    payload = packet[2:2 + size]
    return payload
```

### Expected diagnosis

The declared length is trusted without checking the header, maximum frame size, or truncation.

### Corrected code

```python
def decode_23(packet, maximum=256):
    if len(packet) < 2:
        raise ValueError('short header')
    size = int.from_bytes(packet[:2], 'big')
    if size > maximum or len(packet) != size + 2:
        raise ValueError('invalid frame')
    return packet[2:]
```

### Regression tests

```python
assert decode_23(b'\x00\x02ok') == b'ok'
# Regression: reject short, oversized, and truncated frames.
```

## EPY-H-024: busy wait

- Difficulty: Hard
- Language: Python for Embedded Systems (MicroPython/CircuitPython)
- Perspective: Power budgeting
- Concept: busy wait
- Symptom: Sleep current is much higher than expected.
- Diagnostic goal: Replace polling with a deadline or hardware wake source.

### Buggy code

```python
def wait_24(clock, deadline):
    while clock.now() < deadline:
        pass
```

### Expected diagnosis

A tight polling loop keeps the CPU active and consumes power while waiting for an external event.

### Corrected code

```python
def wait_24(clock, deadline):
    remaining = deadline - clock.now()
    if remaining > 0:
        clock.sleep(remaining)
```

### Regression tests

```python
# Regression: positive remaining time calls sleep once; expired deadlines do not.
```

## EPY-H-025: peripheral left enabled

- Difficulty: Hard
- Language: Python for Embedded Systems (MicroPython/CircuitPython)
- Perspective: Resource lifetime
- Concept: peripheral left enabled
- Symptom: The sensor remains powered after a failed read.
- Diagnostic goal: Use a cleanup boundary even when the operation raises.

### Buggy code

```python
def read_25(sensor):
    sensor.enable()
    value = sensor.read()
    sensor.disable()
    return value
```

### Expected diagnosis

An exception skips disable, leaving the peripheral and possibly the bus in an unsafe state.

### Corrected code

```python
def read_25(sensor):
    sensor.enable()
    try:
        return sensor.read()
    finally:
        sensor.disable()
```

### Regression tests

```python
# Regression: fake sensor records disable after both success and failure.
```

## EPY-H-026: overflow-prone accumulation

- Difficulty: Hard
- Language: Python for Embedded Systems (MicroPython/CircuitPython)
- Perspective: Numeric stability
- Concept: overflow-prone accumulation
- Symptom: A long-running total loses precision or wraps in fixed-width storage.
- Diagnostic goal: Bound or rescale state according to the measurement contract.

### Buggy code

```python
def accumulate_26(total, sample):
    return total + sample
```

### Expected diagnosis

An unbounded accumulator can exceed the representation or lose useful resolution over long uptime.

### Corrected code

```python
def accumulate_26(total, sample, maximum=1000000):
    result = total + sample
    return min(result, maximum)
```

### Regression tests

```python
assert accumulate_26(999, 2, 1000) == 1000
```

## EPY-H-027: illegal transition

- Difficulty: Hard
- Language: Python for Embedded Systems (MicroPython/CircuitPython)
- Perspective: State machine
- Concept: illegal transition
- Symptom: A device enters a state in which commands are unsafe.
- Diagnostic goal: Centralize legal transitions and reject invalid events.

### Buggy code

```python
def transition_27(state, event):
    if event == 'start': return 'running'
    if event == 'stop': return 'idle'
    return state
```

### Expected diagnosis

The transition table ignores the current state, so stop can succeed before start and start can restart a faulted device.

### Corrected code

```python
def transition_27(state, event):
    allowed = {'idle': {'start': 'running'}, 'running': {'stop': 'idle'}}
    if event not in allowed.get(state, {}):
        raise ValueError('illegal transition')
    return allowed[state][event]
```

### Regression tests

```python
assert transition_27('idle', 'start') == 'running'
try: transition_27('idle', 'stop')
except ValueError: pass
else: raise AssertionError
```

## EPY-H-028: non-idempotent restart

- Difficulty: Hard
- Language: Python for Embedded Systems (MicroPython/CircuitPython)
- Perspective: Watchdog recovery
- Concept: non-idempotent restart
- Symptom: Recovery repeats an action and duplicates an external side effect.
- Diagnostic goal: Make recovery steps idempotent and record progress.

### Buggy code

```python
def recover_28(device):
    device.close_valve()
    device.close_valve()
    device.reset()
```

### Expected diagnosis

Repeating a non-idempotent command can damage hardware or produce a different result on the second attempt.

### Corrected code

```python
def recover_28(device):
    if not device.is_closed():
        device.close_valve()
    device.reset()
```

### Regression tests

```python
# Regression: recovery called twice closes the valve once and resets safely.
```

## EPY-H-029: hardware calls in business logic

- Difficulty: Hard
- Language: Python for Embedded Systems (MicroPython/CircuitPython)
- Perspective: Testability
- Concept: hardware calls in business logic
- Symptom: The algorithm cannot be tested without a board.
- Diagnostic goal: Inject a narrow hardware interface and test the pure decision logic separately.

### Buggy code

```python
def alarm_29(reading):
    Pin(2, Pin.OUT).value(1 if reading > 70 else 0)
```

### Expected diagnosis

Constructing and driving hardware inside the decision function couples policy to a specific runtime and pin.

### Corrected code

```python
def alarm_29(reading, output):
    output( reading > 70 )
```

### Regression tests

```python
seen = []
alarm_29(71, seen.append)
assert seen == [True]
alarm_29(70, seen.append)
assert seen == [True, False]
```

## EPY-H-030: single fault aborts startup

- Difficulty: Hard
- Language: Python for Embedded Systems (MicroPython/CircuitPython)
- Perspective: Boot resilience
- Concept: single fault aborts startup
- Symptom: One optional peripheral prevents the core device from booting.
- Diagnostic goal: Isolate optional initialization and expose degraded operation.

### Buggy code

```python
def boot_30(display, sensor):
    display.init()
    sensor.init()
    return 'ready'
```

### Expected diagnosis

A failure in a nonessential component aborts the whole boot path without recording the degraded capability.

### Corrected code

```python
def boot_30(display, sensor):
    display.init()
    try:
        sensor.init()
        return 'ready'
    except OSError:
        return 'display-only'
```

### Regression tests

```python
# Regression: sensor failure returns display-only while display failure still propagates.
```

## EPY-H-031: jitter from allocation

- Difficulty: Hard
- Language: Python for Embedded Systems (MicroPython/CircuitPython)
- Perspective: Real-time reasoning
- Concept: jitter from allocation
- Symptom: A control loop occasionally misses its deadline.
- Diagnostic goal: Move allocation and unpredictable work out of the hot path.

### Buggy code

```python
def control_31(samples):
    values = [sample * 2 for sample in samples]
    return sum(values) / len(values)
```

### Expected diagnosis

Creating a list in every control iteration adds memory pressure and latency variance on constrained devices.

### Corrected code

```python
def control_31(samples):
    total = 0
    count = 0
    for sample in samples:
        total += sample * 2
        count += 1
    return total / count if count else 0
```

### Regression tests

```python
assert control_31([1, 2, 3]) == 4
assert control_31([]) == 0
```

## EPY-H-032: non-atomic multi-field update

- Difficulty: Hard
- Language: Python for Embedded Systems (MicroPython/CircuitPython)
- Perspective: Interrupt/main-loop race
- Concept: non-atomic multi-field update
- Symptom: A snapshot contains a mixed timestamp and value.
- Diagnostic goal: Publish a complete snapshot with a consistency protocol.

### Buggy code

```python
def snapshot_32(state):
    return state['timestamp'], state['value']
```

### Expected diagnosis

An interrupt can update the two fields between reads, so the pair may never have existed together.

### Corrected code

```python
def snapshot_32(state):
    first = state['sequence']
    if first % 2:
        return None
    result = (state['timestamp'], state['value'])
    if state['sequence'] != first:
        return None
    return result
```

### Regression tests

```python
# Regression: odd or changed sequence numbers cause a retry instead of a mixed snapshot.
```

## EPY-H-033: length field trust

- Difficulty: Hard
- Language: Python for Embedded Systems (MicroPython/CircuitPython)
- Perspective: Protocol security
- Concept: length field trust
- Symptom: A malformed packet causes excessive allocation.
- Diagnostic goal: Validate framing and maximum length before allocating.

### Buggy code

```python
def decode_33(packet):
    size = int.from_bytes(packet[:2], 'big')
    payload = packet[2:2 + size]
    return payload
```

### Expected diagnosis

The declared length is trusted without checking the header, maximum frame size, or truncation.

### Corrected code

```python
def decode_33(packet, maximum=256):
    if len(packet) < 2:
        raise ValueError('short header')
    size = int.from_bytes(packet[:2], 'big')
    if size > maximum or len(packet) != size + 2:
        raise ValueError('invalid frame')
    return packet[2:]
```

### Regression tests

```python
assert decode_33(b'\x00\x02ok') == b'ok'
# Regression: reject short, oversized, and truncated frames.
```

## EPY-H-034: busy wait

- Difficulty: Hard
- Language: Python for Embedded Systems (MicroPython/CircuitPython)
- Perspective: Power budgeting
- Concept: busy wait
- Symptom: Sleep current is much higher than expected.
- Diagnostic goal: Replace polling with a deadline or hardware wake source.

### Buggy code

```python
def wait_34(clock, deadline):
    while clock.now() < deadline:
        pass
```

### Expected diagnosis

A tight polling loop keeps the CPU active and consumes power while waiting for an external event.

### Corrected code

```python
def wait_34(clock, deadline):
    remaining = deadline - clock.now()
    if remaining > 0:
        clock.sleep(remaining)
```

### Regression tests

```python
# Regression: positive remaining time calls sleep once; expired deadlines do not.
```

## EPY-H-035: peripheral left enabled

- Difficulty: Hard
- Language: Python for Embedded Systems (MicroPython/CircuitPython)
- Perspective: Resource lifetime
- Concept: peripheral left enabled
- Symptom: The sensor remains powered after a failed read.
- Diagnostic goal: Use a cleanup boundary even when the operation raises.

### Buggy code

```python
def read_35(sensor):
    sensor.enable()
    value = sensor.read()
    sensor.disable()
    return value
```

### Expected diagnosis

An exception skips disable, leaving the peripheral and possibly the bus in an unsafe state.

### Corrected code

```python
def read_35(sensor):
    sensor.enable()
    try:
        return sensor.read()
    finally:
        sensor.disable()
```

### Regression tests

```python
# Regression: fake sensor records disable after both success and failure.
```

## EPY-H-036: overflow-prone accumulation

- Difficulty: Hard
- Language: Python for Embedded Systems (MicroPython/CircuitPython)
- Perspective: Numeric stability
- Concept: overflow-prone accumulation
- Symptom: A long-running total loses precision or wraps in fixed-width storage.
- Diagnostic goal: Bound or rescale state according to the measurement contract.

### Buggy code

```python
def accumulate_36(total, sample):
    return total + sample
```

### Expected diagnosis

An unbounded accumulator can exceed the representation or lose useful resolution over long uptime.

### Corrected code

```python
def accumulate_36(total, sample, maximum=1000000):
    result = total + sample
    return min(result, maximum)
```

### Regression tests

```python
assert accumulate_36(999, 2, 1000) == 1000
```

## EPY-H-037: illegal transition

- Difficulty: Hard
- Language: Python for Embedded Systems (MicroPython/CircuitPython)
- Perspective: State machine
- Concept: illegal transition
- Symptom: A device enters a state in which commands are unsafe.
- Diagnostic goal: Centralize legal transitions and reject invalid events.

### Buggy code

```python
def transition_37(state, event):
    if event == 'start': return 'running'
    if event == 'stop': return 'idle'
    return state
```

### Expected diagnosis

The transition table ignores the current state, so stop can succeed before start and start can restart a faulted device.

### Corrected code

```python
def transition_37(state, event):
    allowed = {'idle': {'start': 'running'}, 'running': {'stop': 'idle'}}
    if event not in allowed.get(state, {}):
        raise ValueError('illegal transition')
    return allowed[state][event]
```

### Regression tests

```python
assert transition_37('idle', 'start') == 'running'
try: transition_37('idle', 'stop')
except ValueError: pass
else: raise AssertionError
```

## EPY-H-038: non-idempotent restart

- Difficulty: Hard
- Language: Python for Embedded Systems (MicroPython/CircuitPython)
- Perspective: Watchdog recovery
- Concept: non-idempotent restart
- Symptom: Recovery repeats an action and duplicates an external side effect.
- Diagnostic goal: Make recovery steps idempotent and record progress.

### Buggy code

```python
def recover_38(device):
    device.close_valve()
    device.close_valve()
    device.reset()
```

### Expected diagnosis

Repeating a non-idempotent command can damage hardware or produce a different result on the second attempt.

### Corrected code

```python
def recover_38(device):
    if not device.is_closed():
        device.close_valve()
    device.reset()
```

### Regression tests

```python
# Regression: recovery called twice closes the valve once and resets safely.
```

## EPY-H-039: hardware calls in business logic

- Difficulty: Hard
- Language: Python for Embedded Systems (MicroPython/CircuitPython)
- Perspective: Testability
- Concept: hardware calls in business logic
- Symptom: The algorithm cannot be tested without a board.
- Diagnostic goal: Inject a narrow hardware interface and test the pure decision logic separately.

### Buggy code

```python
def alarm_39(reading):
    Pin(2, Pin.OUT).value(1 if reading > 70 else 0)
```

### Expected diagnosis

Constructing and driving hardware inside the decision function couples policy to a specific runtime and pin.

### Corrected code

```python
def alarm_39(reading, output):
    output( reading > 70 )
```

### Regression tests

```python
seen = []
alarm_39(71, seen.append)
assert seen == [True]
alarm_39(70, seen.append)
assert seen == [True, False]
```

## EPY-H-040: single fault aborts startup

- Difficulty: Hard
- Language: Python for Embedded Systems (MicroPython/CircuitPython)
- Perspective: Boot resilience
- Concept: single fault aborts startup
- Symptom: One optional peripheral prevents the core device from booting.
- Diagnostic goal: Isolate optional initialization and expose degraded operation.

### Buggy code

```python
def boot_40(display, sensor):
    display.init()
    sensor.init()
    return 'ready'
```

### Expected diagnosis

A failure in a nonessential component aborts the whole boot path without recording the degraded capability.

### Corrected code

```python
def boot_40(display, sensor):
    display.init()
    try:
        sensor.init()
        return 'ready'
    except OSError:
        return 'display-only'
```

### Regression tests

```python
# Regression: sensor failure returns display-only while display failure still propagates.
```

## EPY-H-041: jitter from allocation

- Difficulty: Hard
- Language: Python for Embedded Systems (MicroPython/CircuitPython)
- Perspective: Real-time reasoning
- Concept: jitter from allocation
- Symptom: A control loop occasionally misses its deadline.
- Diagnostic goal: Move allocation and unpredictable work out of the hot path.

### Buggy code

```python
def control_41(samples):
    values = [sample * 2 for sample in samples]
    return sum(values) / len(values)
```

### Expected diagnosis

Creating a list in every control iteration adds memory pressure and latency variance on constrained devices.

### Corrected code

```python
def control_41(samples):
    total = 0
    count = 0
    for sample in samples:
        total += sample * 2
        count += 1
    return total / count if count else 0
```

### Regression tests

```python
assert control_41([1, 2, 3]) == 4
assert control_41([]) == 0
```

## EPY-H-042: non-atomic multi-field update

- Difficulty: Hard
- Language: Python for Embedded Systems (MicroPython/CircuitPython)
- Perspective: Interrupt/main-loop race
- Concept: non-atomic multi-field update
- Symptom: A snapshot contains a mixed timestamp and value.
- Diagnostic goal: Publish a complete snapshot with a consistency protocol.

### Buggy code

```python
def snapshot_42(state):
    return state['timestamp'], state['value']
```

### Expected diagnosis

An interrupt can update the two fields between reads, so the pair may never have existed together.

### Corrected code

```python
def snapshot_42(state):
    first = state['sequence']
    if first % 2:
        return None
    result = (state['timestamp'], state['value'])
    if state['sequence'] != first:
        return None
    return result
```

### Regression tests

```python
# Regression: odd or changed sequence numbers cause a retry instead of a mixed snapshot.
```

## EPY-H-043: length field trust

- Difficulty: Hard
- Language: Python for Embedded Systems (MicroPython/CircuitPython)
- Perspective: Protocol security
- Concept: length field trust
- Symptom: A malformed packet causes excessive allocation.
- Diagnostic goal: Validate framing and maximum length before allocating.

### Buggy code

```python
def decode_43(packet):
    size = int.from_bytes(packet[:2], 'big')
    payload = packet[2:2 + size]
    return payload
```

### Expected diagnosis

The declared length is trusted without checking the header, maximum frame size, or truncation.

### Corrected code

```python
def decode_43(packet, maximum=256):
    if len(packet) < 2:
        raise ValueError('short header')
    size = int.from_bytes(packet[:2], 'big')
    if size > maximum or len(packet) != size + 2:
        raise ValueError('invalid frame')
    return packet[2:]
```

### Regression tests

```python
assert decode_43(b'\x00\x02ok') == b'ok'
# Regression: reject short, oversized, and truncated frames.
```

## EPY-H-044: busy wait

- Difficulty: Hard
- Language: Python for Embedded Systems (MicroPython/CircuitPython)
- Perspective: Power budgeting
- Concept: busy wait
- Symptom: Sleep current is much higher than expected.
- Diagnostic goal: Replace polling with a deadline or hardware wake source.

### Buggy code

```python
def wait_44(clock, deadline):
    while clock.now() < deadline:
        pass
```

### Expected diagnosis

A tight polling loop keeps the CPU active and consumes power while waiting for an external event.

### Corrected code

```python
def wait_44(clock, deadline):
    remaining = deadline - clock.now()
    if remaining > 0:
        clock.sleep(remaining)
```

### Regression tests

```python
# Regression: positive remaining time calls sleep once; expired deadlines do not.
```

## EPY-H-045: peripheral left enabled

- Difficulty: Hard
- Language: Python for Embedded Systems (MicroPython/CircuitPython)
- Perspective: Resource lifetime
- Concept: peripheral left enabled
- Symptom: The sensor remains powered after a failed read.
- Diagnostic goal: Use a cleanup boundary even when the operation raises.

### Buggy code

```python
def read_45(sensor):
    sensor.enable()
    value = sensor.read()
    sensor.disable()
    return value
```

### Expected diagnosis

An exception skips disable, leaving the peripheral and possibly the bus in an unsafe state.

### Corrected code

```python
def read_45(sensor):
    sensor.enable()
    try:
        return sensor.read()
    finally:
        sensor.disable()
```

### Regression tests

```python
# Regression: fake sensor records disable after both success and failure.
```

## EPY-H-046: overflow-prone accumulation

- Difficulty: Hard
- Language: Python for Embedded Systems (MicroPython/CircuitPython)
- Perspective: Numeric stability
- Concept: overflow-prone accumulation
- Symptom: A long-running total loses precision or wraps in fixed-width storage.
- Diagnostic goal: Bound or rescale state according to the measurement contract.

### Buggy code

```python
def accumulate_46(total, sample):
    return total + sample
```

### Expected diagnosis

An unbounded accumulator can exceed the representation or lose useful resolution over long uptime.

### Corrected code

```python
def accumulate_46(total, sample, maximum=1000000):
    result = total + sample
    return min(result, maximum)
```

### Regression tests

```python
assert accumulate_46(999, 2, 1000) == 1000
```

## EPY-H-047: illegal transition

- Difficulty: Hard
- Language: Python for Embedded Systems (MicroPython/CircuitPython)
- Perspective: State machine
- Concept: illegal transition
- Symptom: A device enters a state in which commands are unsafe.
- Diagnostic goal: Centralize legal transitions and reject invalid events.

### Buggy code

```python
def transition_47(state, event):
    if event == 'start': return 'running'
    if event == 'stop': return 'idle'
    return state
```

### Expected diagnosis

The transition table ignores the current state, so stop can succeed before start and start can restart a faulted device.

### Corrected code

```python
def transition_47(state, event):
    allowed = {'idle': {'start': 'running'}, 'running': {'stop': 'idle'}}
    if event not in allowed.get(state, {}):
        raise ValueError('illegal transition')
    return allowed[state][event]
```

### Regression tests

```python
assert transition_47('idle', 'start') == 'running'
try: transition_47('idle', 'stop')
except ValueError: pass
else: raise AssertionError
```

## EPY-H-048: non-idempotent restart

- Difficulty: Hard
- Language: Python for Embedded Systems (MicroPython/CircuitPython)
- Perspective: Watchdog recovery
- Concept: non-idempotent restart
- Symptom: Recovery repeats an action and duplicates an external side effect.
- Diagnostic goal: Make recovery steps idempotent and record progress.

### Buggy code

```python
def recover_48(device):
    device.close_valve()
    device.close_valve()
    device.reset()
```

### Expected diagnosis

Repeating a non-idempotent command can damage hardware or produce a different result on the second attempt.

### Corrected code

```python
def recover_48(device):
    if not device.is_closed():
        device.close_valve()
    device.reset()
```

### Regression tests

```python
# Regression: recovery called twice closes the valve once and resets safely.
```

## EPY-H-049: hardware calls in business logic

- Difficulty: Hard
- Language: Python for Embedded Systems (MicroPython/CircuitPython)
- Perspective: Testability
- Concept: hardware calls in business logic
- Symptom: The algorithm cannot be tested without a board.
- Diagnostic goal: Inject a narrow hardware interface and test the pure decision logic separately.

### Buggy code

```python
def alarm_49(reading):
    Pin(2, Pin.OUT).value(1 if reading > 70 else 0)
```

### Expected diagnosis

Constructing and driving hardware inside the decision function couples policy to a specific runtime and pin.

### Corrected code

```python
def alarm_49(reading, output):
    output( reading > 70 )
```

### Regression tests

```python
seen = []
alarm_49(71, seen.append)
assert seen == [True]
alarm_49(70, seen.append)
assert seen == [True, False]
```

## EPY-H-050: single fault aborts startup

- Difficulty: Hard
- Language: Python for Embedded Systems (MicroPython/CircuitPython)
- Perspective: Boot resilience
- Concept: single fault aborts startup
- Symptom: One optional peripheral prevents the core device from booting.
- Diagnostic goal: Isolate optional initialization and expose degraded operation.

### Buggy code

```python
def boot_50(display, sensor):
    display.init()
    sensor.init()
    return 'ready'
```

### Expected diagnosis

A failure in a nonessential component aborts the whole boot path without recording the degraded capability.

### Corrected code

```python
def boot_50(display, sensor):
    display.init()
    try:
        sensor.init()
        return 'ready'
    except OSError:
        return 'display-only'
```

### Regression tests

```python
# Regression: sensor failure returns display-only while display failure still propagates.
```

## EPY-H-051: jitter from allocation

- Difficulty: Hard
- Language: Python for Embedded Systems (MicroPython/CircuitPython)
- Perspective: Real-time reasoning
- Concept: jitter from allocation
- Symptom: A control loop occasionally misses its deadline.
- Diagnostic goal: Move allocation and unpredictable work out of the hot path.

### Buggy code

```python
def control_51(samples):
    values = [sample * 2 for sample in samples]
    return sum(values) / len(values)
```

### Expected diagnosis

Creating a list in every control iteration adds memory pressure and latency variance on constrained devices.

### Corrected code

```python
def control_51(samples):
    total = 0
    count = 0
    for sample in samples:
        total += sample * 2
        count += 1
    return total / count if count else 0
```

### Regression tests

```python
assert control_51([1, 2, 3]) == 4
assert control_51([]) == 0
```

## EPY-H-052: non-atomic multi-field update

- Difficulty: Hard
- Language: Python for Embedded Systems (MicroPython/CircuitPython)
- Perspective: Interrupt/main-loop race
- Concept: non-atomic multi-field update
- Symptom: A snapshot contains a mixed timestamp and value.
- Diagnostic goal: Publish a complete snapshot with a consistency protocol.

### Buggy code

```python
def snapshot_52(state):
    return state['timestamp'], state['value']
```

### Expected diagnosis

An interrupt can update the two fields between reads, so the pair may never have existed together.

### Corrected code

```python
def snapshot_52(state):
    first = state['sequence']
    if first % 2:
        return None
    result = (state['timestamp'], state['value'])
    if state['sequence'] != first:
        return None
    return result
```

### Regression tests

```python
# Regression: odd or changed sequence numbers cause a retry instead of a mixed snapshot.
```

## EPY-H-053: length field trust

- Difficulty: Hard
- Language: Python for Embedded Systems (MicroPython/CircuitPython)
- Perspective: Protocol security
- Concept: length field trust
- Symptom: A malformed packet causes excessive allocation.
- Diagnostic goal: Validate framing and maximum length before allocating.

### Buggy code

```python
def decode_53(packet):
    size = int.from_bytes(packet[:2], 'big')
    payload = packet[2:2 + size]
    return payload
```

### Expected diagnosis

The declared length is trusted without checking the header, maximum frame size, or truncation.

### Corrected code

```python
def decode_53(packet, maximum=256):
    if len(packet) < 2:
        raise ValueError('short header')
    size = int.from_bytes(packet[:2], 'big')
    if size > maximum or len(packet) != size + 2:
        raise ValueError('invalid frame')
    return packet[2:]
```

### Regression tests

```python
assert decode_53(b'\x00\x02ok') == b'ok'
# Regression: reject short, oversized, and truncated frames.
```

## EPY-H-054: busy wait

- Difficulty: Hard
- Language: Python for Embedded Systems (MicroPython/CircuitPython)
- Perspective: Power budgeting
- Concept: busy wait
- Symptom: Sleep current is much higher than expected.
- Diagnostic goal: Replace polling with a deadline or hardware wake source.

### Buggy code

```python
def wait_54(clock, deadline):
    while clock.now() < deadline:
        pass
```

### Expected diagnosis

A tight polling loop keeps the CPU active and consumes power while waiting for an external event.

### Corrected code

```python
def wait_54(clock, deadline):
    remaining = deadline - clock.now()
    if remaining > 0:
        clock.sleep(remaining)
```

### Regression tests

```python
# Regression: positive remaining time calls sleep once; expired deadlines do not.
```

## EPY-H-055: peripheral left enabled

- Difficulty: Hard
- Language: Python for Embedded Systems (MicroPython/CircuitPython)
- Perspective: Resource lifetime
- Concept: peripheral left enabled
- Symptom: The sensor remains powered after a failed read.
- Diagnostic goal: Use a cleanup boundary even when the operation raises.

### Buggy code

```python
def read_55(sensor):
    sensor.enable()
    value = sensor.read()
    sensor.disable()
    return value
```

### Expected diagnosis

An exception skips disable, leaving the peripheral and possibly the bus in an unsafe state.

### Corrected code

```python
def read_55(sensor):
    sensor.enable()
    try:
        return sensor.read()
    finally:
        sensor.disable()
```

### Regression tests

```python
# Regression: fake sensor records disable after both success and failure.
```

## EPY-H-056: overflow-prone accumulation

- Difficulty: Hard
- Language: Python for Embedded Systems (MicroPython/CircuitPython)
- Perspective: Numeric stability
- Concept: overflow-prone accumulation
- Symptom: A long-running total loses precision or wraps in fixed-width storage.
- Diagnostic goal: Bound or rescale state according to the measurement contract.

### Buggy code

```python
def accumulate_56(total, sample):
    return total + sample
```

### Expected diagnosis

An unbounded accumulator can exceed the representation or lose useful resolution over long uptime.

### Corrected code

```python
def accumulate_56(total, sample, maximum=1000000):
    result = total + sample
    return min(result, maximum)
```

### Regression tests

```python
assert accumulate_56(999, 2, 1000) == 1000
```

## EPY-H-057: illegal transition

- Difficulty: Hard
- Language: Python for Embedded Systems (MicroPython/CircuitPython)
- Perspective: State machine
- Concept: illegal transition
- Symptom: A device enters a state in which commands are unsafe.
- Diagnostic goal: Centralize legal transitions and reject invalid events.

### Buggy code

```python
def transition_57(state, event):
    if event == 'start': return 'running'
    if event == 'stop': return 'idle'
    return state
```

### Expected diagnosis

The transition table ignores the current state, so stop can succeed before start and start can restart a faulted device.

### Corrected code

```python
def transition_57(state, event):
    allowed = {'idle': {'start': 'running'}, 'running': {'stop': 'idle'}}
    if event not in allowed.get(state, {}):
        raise ValueError('illegal transition')
    return allowed[state][event]
```

### Regression tests

```python
assert transition_57('idle', 'start') == 'running'
try: transition_57('idle', 'stop')
except ValueError: pass
else: raise AssertionError
```

## EPY-H-058: non-idempotent restart

- Difficulty: Hard
- Language: Python for Embedded Systems (MicroPython/CircuitPython)
- Perspective: Watchdog recovery
- Concept: non-idempotent restart
- Symptom: Recovery repeats an action and duplicates an external side effect.
- Diagnostic goal: Make recovery steps idempotent and record progress.

### Buggy code

```python
def recover_58(device):
    device.close_valve()
    device.close_valve()
    device.reset()
```

### Expected diagnosis

Repeating a non-idempotent command can damage hardware or produce a different result on the second attempt.

### Corrected code

```python
def recover_58(device):
    if not device.is_closed():
        device.close_valve()
    device.reset()
```

### Regression tests

```python
# Regression: recovery called twice closes the valve once and resets safely.
```

## EPY-H-059: hardware calls in business logic

- Difficulty: Hard
- Language: Python for Embedded Systems (MicroPython/CircuitPython)
- Perspective: Testability
- Concept: hardware calls in business logic
- Symptom: The algorithm cannot be tested without a board.
- Diagnostic goal: Inject a narrow hardware interface and test the pure decision logic separately.

### Buggy code

```python
def alarm_59(reading):
    Pin(2, Pin.OUT).value(1 if reading > 70 else 0)
```

### Expected diagnosis

Constructing and driving hardware inside the decision function couples policy to a specific runtime and pin.

### Corrected code

```python
def alarm_59(reading, output):
    output( reading > 70 )
```

### Regression tests

```python
seen = []
alarm_59(71, seen.append)
assert seen == [True]
alarm_59(70, seen.append)
assert seen == [True, False]
```

## EPY-H-060: single fault aborts startup

- Difficulty: Hard
- Language: Python for Embedded Systems (MicroPython/CircuitPython)
- Perspective: Boot resilience
- Concept: single fault aborts startup
- Symptom: One optional peripheral prevents the core device from booting.
- Diagnostic goal: Isolate optional initialization and expose degraded operation.

### Buggy code

```python
def boot_60(display, sensor):
    display.init()
    sensor.init()
    return 'ready'
```

### Expected diagnosis

A failure in a nonessential component aborts the whole boot path without recording the degraded capability.

### Corrected code

```python
def boot_60(display, sensor):
    display.init()
    try:
        sensor.init()
        return 'ready'
    except OSError:
        return 'display-only'
```

### Regression tests

```python
# Regression: sensor failure returns display-only while display failure still propagates.
```

## EPY-H-061: jitter from allocation

- Difficulty: Hard
- Language: Python for Embedded Systems (MicroPython/CircuitPython)
- Perspective: Real-time reasoning
- Concept: jitter from allocation
- Symptom: A control loop occasionally misses its deadline.
- Diagnostic goal: Move allocation and unpredictable work out of the hot path.

### Buggy code

```python
def control_61(samples):
    values = [sample * 2 for sample in samples]
    return sum(values) / len(values)
```

### Expected diagnosis

Creating a list in every control iteration adds memory pressure and latency variance on constrained devices.

### Corrected code

```python
def control_61(samples):
    total = 0
    count = 0
    for sample in samples:
        total += sample * 2
        count += 1
    return total / count if count else 0
```

### Regression tests

```python
assert control_61([1, 2, 3]) == 4
assert control_61([]) == 0
```

## EPY-H-062: non-atomic multi-field update

- Difficulty: Hard
- Language: Python for Embedded Systems (MicroPython/CircuitPython)
- Perspective: Interrupt/main-loop race
- Concept: non-atomic multi-field update
- Symptom: A snapshot contains a mixed timestamp and value.
- Diagnostic goal: Publish a complete snapshot with a consistency protocol.

### Buggy code

```python
def snapshot_62(state):
    return state['timestamp'], state['value']
```

### Expected diagnosis

An interrupt can update the two fields between reads, so the pair may never have existed together.

### Corrected code

```python
def snapshot_62(state):
    first = state['sequence']
    if first % 2:
        return None
    result = (state['timestamp'], state['value'])
    if state['sequence'] != first:
        return None
    return result
```

### Regression tests

```python
# Regression: odd or changed sequence numbers cause a retry instead of a mixed snapshot.
```

## EPY-H-063: length field trust

- Difficulty: Hard
- Language: Python for Embedded Systems (MicroPython/CircuitPython)
- Perspective: Protocol security
- Concept: length field trust
- Symptom: A malformed packet causes excessive allocation.
- Diagnostic goal: Validate framing and maximum length before allocating.

### Buggy code

```python
def decode_63(packet):
    size = int.from_bytes(packet[:2], 'big')
    payload = packet[2:2 + size]
    return payload
```

### Expected diagnosis

The declared length is trusted without checking the header, maximum frame size, or truncation.

### Corrected code

```python
def decode_63(packet, maximum=256):
    if len(packet) < 2:
        raise ValueError('short header')
    size = int.from_bytes(packet[:2], 'big')
    if size > maximum or len(packet) != size + 2:
        raise ValueError('invalid frame')
    return packet[2:]
```

### Regression tests

```python
assert decode_63(b'\x00\x02ok') == b'ok'
# Regression: reject short, oversized, and truncated frames.
```

## EPY-H-064: busy wait

- Difficulty: Hard
- Language: Python for Embedded Systems (MicroPython/CircuitPython)
- Perspective: Power budgeting
- Concept: busy wait
- Symptom: Sleep current is much higher than expected.
- Diagnostic goal: Replace polling with a deadline or hardware wake source.

### Buggy code

```python
def wait_64(clock, deadline):
    while clock.now() < deadline:
        pass
```

### Expected diagnosis

A tight polling loop keeps the CPU active and consumes power while waiting for an external event.

### Corrected code

```python
def wait_64(clock, deadline):
    remaining = deadline - clock.now()
    if remaining > 0:
        clock.sleep(remaining)
```

### Regression tests

```python
# Regression: positive remaining time calls sleep once; expired deadlines do not.
```

## EPY-H-065: peripheral left enabled

- Difficulty: Hard
- Language: Python for Embedded Systems (MicroPython/CircuitPython)
- Perspective: Resource lifetime
- Concept: peripheral left enabled
- Symptom: The sensor remains powered after a failed read.
- Diagnostic goal: Use a cleanup boundary even when the operation raises.

### Buggy code

```python
def read_65(sensor):
    sensor.enable()
    value = sensor.read()
    sensor.disable()
    return value
```

### Expected diagnosis

An exception skips disable, leaving the peripheral and possibly the bus in an unsafe state.

### Corrected code

```python
def read_65(sensor):
    sensor.enable()
    try:
        return sensor.read()
    finally:
        sensor.disable()
```

### Regression tests

```python
# Regression: fake sensor records disable after both success and failure.
```

## EPY-H-066: overflow-prone accumulation

- Difficulty: Hard
- Language: Python for Embedded Systems (MicroPython/CircuitPython)
- Perspective: Numeric stability
- Concept: overflow-prone accumulation
- Symptom: A long-running total loses precision or wraps in fixed-width storage.
- Diagnostic goal: Bound or rescale state according to the measurement contract.

### Buggy code

```python
def accumulate_66(total, sample):
    return total + sample
```

### Expected diagnosis

An unbounded accumulator can exceed the representation or lose useful resolution over long uptime.

### Corrected code

```python
def accumulate_66(total, sample, maximum=1000000):
    result = total + sample
    return min(result, maximum)
```

### Regression tests

```python
assert accumulate_66(999, 2, 1000) == 1000
```

## EPY-H-067: illegal transition

- Difficulty: Hard
- Language: Python for Embedded Systems (MicroPython/CircuitPython)
- Perspective: State machine
- Concept: illegal transition
- Symptom: A device enters a state in which commands are unsafe.
- Diagnostic goal: Centralize legal transitions and reject invalid events.

### Buggy code

```python
def transition_67(state, event):
    if event == 'start': return 'running'
    if event == 'stop': return 'idle'
    return state
```

### Expected diagnosis

The transition table ignores the current state, so stop can succeed before start and start can restart a faulted device.

### Corrected code

```python
def transition_67(state, event):
    allowed = {'idle': {'start': 'running'}, 'running': {'stop': 'idle'}}
    if event not in allowed.get(state, {}):
        raise ValueError('illegal transition')
    return allowed[state][event]
```

### Regression tests

```python
assert transition_67('idle', 'start') == 'running'
try: transition_67('idle', 'stop')
except ValueError: pass
else: raise AssertionError
```

## EPY-H-068: non-idempotent restart

- Difficulty: Hard
- Language: Python for Embedded Systems (MicroPython/CircuitPython)
- Perspective: Watchdog recovery
- Concept: non-idempotent restart
- Symptom: Recovery repeats an action and duplicates an external side effect.
- Diagnostic goal: Make recovery steps idempotent and record progress.

### Buggy code

```python
def recover_68(device):
    device.close_valve()
    device.close_valve()
    device.reset()
```

### Expected diagnosis

Repeating a non-idempotent command can damage hardware or produce a different result on the second attempt.

### Corrected code

```python
def recover_68(device):
    if not device.is_closed():
        device.close_valve()
    device.reset()
```

### Regression tests

```python
# Regression: recovery called twice closes the valve once and resets safely.
```

## EPY-H-069: hardware calls in business logic

- Difficulty: Hard
- Language: Python for Embedded Systems (MicroPython/CircuitPython)
- Perspective: Testability
- Concept: hardware calls in business logic
- Symptom: The algorithm cannot be tested without a board.
- Diagnostic goal: Inject a narrow hardware interface and test the pure decision logic separately.

### Buggy code

```python
def alarm_69(reading):
    Pin(2, Pin.OUT).value(1 if reading > 70 else 0)
```

### Expected diagnosis

Constructing and driving hardware inside the decision function couples policy to a specific runtime and pin.

### Corrected code

```python
def alarm_69(reading, output):
    output( reading > 70 )
```

### Regression tests

```python
seen = []
alarm_69(71, seen.append)
assert seen == [True]
alarm_69(70, seen.append)
assert seen == [True, False]
```

## EPY-H-070: single fault aborts startup

- Difficulty: Hard
- Language: Python for Embedded Systems (MicroPython/CircuitPython)
- Perspective: Boot resilience
- Concept: single fault aborts startup
- Symptom: One optional peripheral prevents the core device from booting.
- Diagnostic goal: Isolate optional initialization and expose degraded operation.

### Buggy code

```python
def boot_70(display, sensor):
    display.init()
    sensor.init()
    return 'ready'
```

### Expected diagnosis

A failure in a nonessential component aborts the whole boot path without recording the degraded capability.

### Corrected code

```python
def boot_70(display, sensor):
    display.init()
    try:
        sensor.init()
        return 'ready'
    except OSError:
        return 'display-only'
```

### Regression tests

```python
# Regression: sensor failure returns display-only while display failure still propagates.
```

## EPY-H-071: jitter from allocation

- Difficulty: Hard
- Language: Python for Embedded Systems (MicroPython/CircuitPython)
- Perspective: Real-time reasoning
- Concept: jitter from allocation
- Symptom: A control loop occasionally misses its deadline.
- Diagnostic goal: Move allocation and unpredictable work out of the hot path.

### Buggy code

```python
def control_71(samples):
    values = [sample * 2 for sample in samples]
    return sum(values) / len(values)
```

### Expected diagnosis

Creating a list in every control iteration adds memory pressure and latency variance on constrained devices.

### Corrected code

```python
def control_71(samples):
    total = 0
    count = 0
    for sample in samples:
        total += sample * 2
        count += 1
    return total / count if count else 0
```

### Regression tests

```python
assert control_71([1, 2, 3]) == 4
assert control_71([]) == 0
```

## EPY-H-072: non-atomic multi-field update

- Difficulty: Hard
- Language: Python for Embedded Systems (MicroPython/CircuitPython)
- Perspective: Interrupt/main-loop race
- Concept: non-atomic multi-field update
- Symptom: A snapshot contains a mixed timestamp and value.
- Diagnostic goal: Publish a complete snapshot with a consistency protocol.

### Buggy code

```python
def snapshot_72(state):
    return state['timestamp'], state['value']
```

### Expected diagnosis

An interrupt can update the two fields between reads, so the pair may never have existed together.

### Corrected code

```python
def snapshot_72(state):
    first = state['sequence']
    if first % 2:
        return None
    result = (state['timestamp'], state['value'])
    if state['sequence'] != first:
        return None
    return result
```

### Regression tests

```python
# Regression: odd or changed sequence numbers cause a retry instead of a mixed snapshot.
```

## EPY-H-073: length field trust

- Difficulty: Hard
- Language: Python for Embedded Systems (MicroPython/CircuitPython)
- Perspective: Protocol security
- Concept: length field trust
- Symptom: A malformed packet causes excessive allocation.
- Diagnostic goal: Validate framing and maximum length before allocating.

### Buggy code

```python
def decode_73(packet):
    size = int.from_bytes(packet[:2], 'big')
    payload = packet[2:2 + size]
    return payload
```

### Expected diagnosis

The declared length is trusted without checking the header, maximum frame size, or truncation.

### Corrected code

```python
def decode_73(packet, maximum=256):
    if len(packet) < 2:
        raise ValueError('short header')
    size = int.from_bytes(packet[:2], 'big')
    if size > maximum or len(packet) != size + 2:
        raise ValueError('invalid frame')
    return packet[2:]
```

### Regression tests

```python
assert decode_73(b'\x00\x02ok') == b'ok'
# Regression: reject short, oversized, and truncated frames.
```

## EPY-H-074: busy wait

- Difficulty: Hard
- Language: Python for Embedded Systems (MicroPython/CircuitPython)
- Perspective: Power budgeting
- Concept: busy wait
- Symptom: Sleep current is much higher than expected.
- Diagnostic goal: Replace polling with a deadline or hardware wake source.

### Buggy code

```python
def wait_74(clock, deadline):
    while clock.now() < deadline:
        pass
```

### Expected diagnosis

A tight polling loop keeps the CPU active and consumes power while waiting for an external event.

### Corrected code

```python
def wait_74(clock, deadline):
    remaining = deadline - clock.now()
    if remaining > 0:
        clock.sleep(remaining)
```

### Regression tests

```python
# Regression: positive remaining time calls sleep once; expired deadlines do not.
```

## EPY-H-075: peripheral left enabled

- Difficulty: Hard
- Language: Python for Embedded Systems (MicroPython/CircuitPython)
- Perspective: Resource lifetime
- Concept: peripheral left enabled
- Symptom: The sensor remains powered after a failed read.
- Diagnostic goal: Use a cleanup boundary even when the operation raises.

### Buggy code

```python
def read_75(sensor):
    sensor.enable()
    value = sensor.read()
    sensor.disable()
    return value
```

### Expected diagnosis

An exception skips disable, leaving the peripheral and possibly the bus in an unsafe state.

### Corrected code

```python
def read_75(sensor):
    sensor.enable()
    try:
        return sensor.read()
    finally:
        sensor.disable()
```

### Regression tests

```python
# Regression: fake sensor records disable after both success and failure.
```

## EPY-H-076: overflow-prone accumulation

- Difficulty: Hard
- Language: Python for Embedded Systems (MicroPython/CircuitPython)
- Perspective: Numeric stability
- Concept: overflow-prone accumulation
- Symptom: A long-running total loses precision or wraps in fixed-width storage.
- Diagnostic goal: Bound or rescale state according to the measurement contract.

### Buggy code

```python
def accumulate_76(total, sample):
    return total + sample
```

### Expected diagnosis

An unbounded accumulator can exceed the representation or lose useful resolution over long uptime.

### Corrected code

```python
def accumulate_76(total, sample, maximum=1000000):
    result = total + sample
    return min(result, maximum)
```

### Regression tests

```python
assert accumulate_76(999, 2, 1000) == 1000
```

## EPY-H-077: illegal transition

- Difficulty: Hard
- Language: Python for Embedded Systems (MicroPython/CircuitPython)
- Perspective: State machine
- Concept: illegal transition
- Symptom: A device enters a state in which commands are unsafe.
- Diagnostic goal: Centralize legal transitions and reject invalid events.

### Buggy code

```python
def transition_77(state, event):
    if event == 'start': return 'running'
    if event == 'stop': return 'idle'
    return state
```

### Expected diagnosis

The transition table ignores the current state, so stop can succeed before start and start can restart a faulted device.

### Corrected code

```python
def transition_77(state, event):
    allowed = {'idle': {'start': 'running'}, 'running': {'stop': 'idle'}}
    if event not in allowed.get(state, {}):
        raise ValueError('illegal transition')
    return allowed[state][event]
```

### Regression tests

```python
assert transition_77('idle', 'start') == 'running'
try: transition_77('idle', 'stop')
except ValueError: pass
else: raise AssertionError
```

## EPY-H-078: non-idempotent restart

- Difficulty: Hard
- Language: Python for Embedded Systems (MicroPython/CircuitPython)
- Perspective: Watchdog recovery
- Concept: non-idempotent restart
- Symptom: Recovery repeats an action and duplicates an external side effect.
- Diagnostic goal: Make recovery steps idempotent and record progress.

### Buggy code

```python
def recover_78(device):
    device.close_valve()
    device.close_valve()
    device.reset()
```

### Expected diagnosis

Repeating a non-idempotent command can damage hardware or produce a different result on the second attempt.

### Corrected code

```python
def recover_78(device):
    if not device.is_closed():
        device.close_valve()
    device.reset()
```

### Regression tests

```python
# Regression: recovery called twice closes the valve once and resets safely.
```

## EPY-H-079: hardware calls in business logic

- Difficulty: Hard
- Language: Python for Embedded Systems (MicroPython/CircuitPython)
- Perspective: Testability
- Concept: hardware calls in business logic
- Symptom: The algorithm cannot be tested without a board.
- Diagnostic goal: Inject a narrow hardware interface and test the pure decision logic separately.

### Buggy code

```python
def alarm_79(reading):
    Pin(2, Pin.OUT).value(1 if reading > 70 else 0)
```

### Expected diagnosis

Constructing and driving hardware inside the decision function couples policy to a specific runtime and pin.

### Corrected code

```python
def alarm_79(reading, output):
    output( reading > 70 )
```

### Regression tests

```python
seen = []
alarm_79(71, seen.append)
assert seen == [True]
alarm_79(70, seen.append)
assert seen == [True, False]
```

## EPY-H-080: single fault aborts startup

- Difficulty: Hard
- Language: Python for Embedded Systems (MicroPython/CircuitPython)
- Perspective: Boot resilience
- Concept: single fault aborts startup
- Symptom: One optional peripheral prevents the core device from booting.
- Diagnostic goal: Isolate optional initialization and expose degraded operation.

### Buggy code

```python
def boot_80(display, sensor):
    display.init()
    sensor.init()
    return 'ready'
```

### Expected diagnosis

A failure in a nonessential component aborts the whole boot path without recording the degraded capability.

### Corrected code

```python
def boot_80(display, sensor):
    display.init()
    try:
        sensor.init()
        return 'ready'
    except OSError:
        return 'display-only'
```

### Regression tests

```python
# Regression: sensor failure returns display-only while display failure still propagates.
```

## EPY-H-081: jitter from allocation

- Difficulty: Hard
- Language: Python for Embedded Systems (MicroPython/CircuitPython)
- Perspective: Real-time reasoning
- Concept: jitter from allocation
- Symptom: A control loop occasionally misses its deadline.
- Diagnostic goal: Move allocation and unpredictable work out of the hot path.

### Buggy code

```python
def control_81(samples):
    values = [sample * 2 for sample in samples]
    return sum(values) / len(values)
```

### Expected diagnosis

Creating a list in every control iteration adds memory pressure and latency variance on constrained devices.

### Corrected code

```python
def control_81(samples):
    total = 0
    count = 0
    for sample in samples:
        total += sample * 2
        count += 1
    return total / count if count else 0
```

### Regression tests

```python
assert control_81([1, 2, 3]) == 4
assert control_81([]) == 0
```

## EPY-H-082: non-atomic multi-field update

- Difficulty: Hard
- Language: Python for Embedded Systems (MicroPython/CircuitPython)
- Perspective: Interrupt/main-loop race
- Concept: non-atomic multi-field update
- Symptom: A snapshot contains a mixed timestamp and value.
- Diagnostic goal: Publish a complete snapshot with a consistency protocol.

### Buggy code

```python
def snapshot_82(state):
    return state['timestamp'], state['value']
```

### Expected diagnosis

An interrupt can update the two fields between reads, so the pair may never have existed together.

### Corrected code

```python
def snapshot_82(state):
    first = state['sequence']
    if first % 2:
        return None
    result = (state['timestamp'], state['value'])
    if state['sequence'] != first:
        return None
    return result
```

### Regression tests

```python
# Regression: odd or changed sequence numbers cause a retry instead of a mixed snapshot.
```

## EPY-H-083: length field trust

- Difficulty: Hard
- Language: Python for Embedded Systems (MicroPython/CircuitPython)
- Perspective: Protocol security
- Concept: length field trust
- Symptom: A malformed packet causes excessive allocation.
- Diagnostic goal: Validate framing and maximum length before allocating.

### Buggy code

```python
def decode_83(packet):
    size = int.from_bytes(packet[:2], 'big')
    payload = packet[2:2 + size]
    return payload
```

### Expected diagnosis

The declared length is trusted without checking the header, maximum frame size, or truncation.

### Corrected code

```python
def decode_83(packet, maximum=256):
    if len(packet) < 2:
        raise ValueError('short header')
    size = int.from_bytes(packet[:2], 'big')
    if size > maximum or len(packet) != size + 2:
        raise ValueError('invalid frame')
    return packet[2:]
```

### Regression tests

```python
assert decode_83(b'\x00\x02ok') == b'ok'
# Regression: reject short, oversized, and truncated frames.
```

## EPY-H-084: busy wait

- Difficulty: Hard
- Language: Python for Embedded Systems (MicroPython/CircuitPython)
- Perspective: Power budgeting
- Concept: busy wait
- Symptom: Sleep current is much higher than expected.
- Diagnostic goal: Replace polling with a deadline or hardware wake source.

### Buggy code

```python
def wait_84(clock, deadline):
    while clock.now() < deadline:
        pass
```

### Expected diagnosis

A tight polling loop keeps the CPU active and consumes power while waiting for an external event.

### Corrected code

```python
def wait_84(clock, deadline):
    remaining = deadline - clock.now()
    if remaining > 0:
        clock.sleep(remaining)
```

### Regression tests

```python
# Regression: positive remaining time calls sleep once; expired deadlines do not.
```

## EPY-H-085: peripheral left enabled

- Difficulty: Hard
- Language: Python for Embedded Systems (MicroPython/CircuitPython)
- Perspective: Resource lifetime
- Concept: peripheral left enabled
- Symptom: The sensor remains powered after a failed read.
- Diagnostic goal: Use a cleanup boundary even when the operation raises.

### Buggy code

```python
def read_85(sensor):
    sensor.enable()
    value = sensor.read()
    sensor.disable()
    return value
```

### Expected diagnosis

An exception skips disable, leaving the peripheral and possibly the bus in an unsafe state.

### Corrected code

```python
def read_85(sensor):
    sensor.enable()
    try:
        return sensor.read()
    finally:
        sensor.disable()
```

### Regression tests

```python
# Regression: fake sensor records disable after both success and failure.
```

## EPY-H-086: overflow-prone accumulation

- Difficulty: Hard
- Language: Python for Embedded Systems (MicroPython/CircuitPython)
- Perspective: Numeric stability
- Concept: overflow-prone accumulation
- Symptom: A long-running total loses precision or wraps in fixed-width storage.
- Diagnostic goal: Bound or rescale state according to the measurement contract.

### Buggy code

```python
def accumulate_86(total, sample):
    return total + sample
```

### Expected diagnosis

An unbounded accumulator can exceed the representation or lose useful resolution over long uptime.

### Corrected code

```python
def accumulate_86(total, sample, maximum=1000000):
    result = total + sample
    return min(result, maximum)
```

### Regression tests

```python
assert accumulate_86(999, 2, 1000) == 1000
```

## EPY-H-087: illegal transition

- Difficulty: Hard
- Language: Python for Embedded Systems (MicroPython/CircuitPython)
- Perspective: State machine
- Concept: illegal transition
- Symptom: A device enters a state in which commands are unsafe.
- Diagnostic goal: Centralize legal transitions and reject invalid events.

### Buggy code

```python
def transition_87(state, event):
    if event == 'start': return 'running'
    if event == 'stop': return 'idle'
    return state
```

### Expected diagnosis

The transition table ignores the current state, so stop can succeed before start and start can restart a faulted device.

### Corrected code

```python
def transition_87(state, event):
    allowed = {'idle': {'start': 'running'}, 'running': {'stop': 'idle'}}
    if event not in allowed.get(state, {}):
        raise ValueError('illegal transition')
    return allowed[state][event]
```

### Regression tests

```python
assert transition_87('idle', 'start') == 'running'
try: transition_87('idle', 'stop')
except ValueError: pass
else: raise AssertionError
```

## EPY-H-088: non-idempotent restart

- Difficulty: Hard
- Language: Python for Embedded Systems (MicroPython/CircuitPython)
- Perspective: Watchdog recovery
- Concept: non-idempotent restart
- Symptom: Recovery repeats an action and duplicates an external side effect.
- Diagnostic goal: Make recovery steps idempotent and record progress.

### Buggy code

```python
def recover_88(device):
    device.close_valve()
    device.close_valve()
    device.reset()
```

### Expected diagnosis

Repeating a non-idempotent command can damage hardware or produce a different result on the second attempt.

### Corrected code

```python
def recover_88(device):
    if not device.is_closed():
        device.close_valve()
    device.reset()
```

### Regression tests

```python
# Regression: recovery called twice closes the valve once and resets safely.
```

## EPY-H-089: hardware calls in business logic

- Difficulty: Hard
- Language: Python for Embedded Systems (MicroPython/CircuitPython)
- Perspective: Testability
- Concept: hardware calls in business logic
- Symptom: The algorithm cannot be tested without a board.
- Diagnostic goal: Inject a narrow hardware interface and test the pure decision logic separately.

### Buggy code

```python
def alarm_89(reading):
    Pin(2, Pin.OUT).value(1 if reading > 70 else 0)
```

### Expected diagnosis

Constructing and driving hardware inside the decision function couples policy to a specific runtime and pin.

### Corrected code

```python
def alarm_89(reading, output):
    output( reading > 70 )
```

### Regression tests

```python
seen = []
alarm_89(71, seen.append)
assert seen == [True]
alarm_89(70, seen.append)
assert seen == [True, False]
```

## EPY-H-090: single fault aborts startup

- Difficulty: Hard
- Language: Python for Embedded Systems (MicroPython/CircuitPython)
- Perspective: Boot resilience
- Concept: single fault aborts startup
- Symptom: One optional peripheral prevents the core device from booting.
- Diagnostic goal: Isolate optional initialization and expose degraded operation.

### Buggy code

```python
def boot_90(display, sensor):
    display.init()
    sensor.init()
    return 'ready'
```

### Expected diagnosis

A failure in a nonessential component aborts the whole boot path without recording the degraded capability.

### Corrected code

```python
def boot_90(display, sensor):
    display.init()
    try:
        sensor.init()
        return 'ready'
    except OSError:
        return 'display-only'
```

### Regression tests

```python
# Regression: sensor failure returns display-only while display failure still propagates.
```

## EPY-H-091: jitter from allocation

- Difficulty: Hard
- Language: Python for Embedded Systems (MicroPython/CircuitPython)
- Perspective: Real-time reasoning
- Concept: jitter from allocation
- Symptom: A control loop occasionally misses its deadline.
- Diagnostic goal: Move allocation and unpredictable work out of the hot path.

### Buggy code

```python
def control_91(samples):
    values = [sample * 2 for sample in samples]
    return sum(values) / len(values)
```

### Expected diagnosis

Creating a list in every control iteration adds memory pressure and latency variance on constrained devices.

### Corrected code

```python
def control_91(samples):
    total = 0
    count = 0
    for sample in samples:
        total += sample * 2
        count += 1
    return total / count if count else 0
```

### Regression tests

```python
assert control_91([1, 2, 3]) == 4
assert control_91([]) == 0
```

## EPY-H-092: non-atomic multi-field update

- Difficulty: Hard
- Language: Python for Embedded Systems (MicroPython/CircuitPython)
- Perspective: Interrupt/main-loop race
- Concept: non-atomic multi-field update
- Symptom: A snapshot contains a mixed timestamp and value.
- Diagnostic goal: Publish a complete snapshot with a consistency protocol.

### Buggy code

```python
def snapshot_92(state):
    return state['timestamp'], state['value']
```

### Expected diagnosis

An interrupt can update the two fields between reads, so the pair may never have existed together.

### Corrected code

```python
def snapshot_92(state):
    first = state['sequence']
    if first % 2:
        return None
    result = (state['timestamp'], state['value'])
    if state['sequence'] != first:
        return None
    return result
```

### Regression tests

```python
# Regression: odd or changed sequence numbers cause a retry instead of a mixed snapshot.
```

## EPY-H-093: length field trust

- Difficulty: Hard
- Language: Python for Embedded Systems (MicroPython/CircuitPython)
- Perspective: Protocol security
- Concept: length field trust
- Symptom: A malformed packet causes excessive allocation.
- Diagnostic goal: Validate framing and maximum length before allocating.

### Buggy code

```python
def decode_93(packet):
    size = int.from_bytes(packet[:2], 'big')
    payload = packet[2:2 + size]
    return payload
```

### Expected diagnosis

The declared length is trusted without checking the header, maximum frame size, or truncation.

### Corrected code

```python
def decode_93(packet, maximum=256):
    if len(packet) < 2:
        raise ValueError('short header')
    size = int.from_bytes(packet[:2], 'big')
    if size > maximum or len(packet) != size + 2:
        raise ValueError('invalid frame')
    return packet[2:]
```

### Regression tests

```python
assert decode_93(b'\x00\x02ok') == b'ok'
# Regression: reject short, oversized, and truncated frames.
```

## EPY-H-094: busy wait

- Difficulty: Hard
- Language: Python for Embedded Systems (MicroPython/CircuitPython)
- Perspective: Power budgeting
- Concept: busy wait
- Symptom: Sleep current is much higher than expected.
- Diagnostic goal: Replace polling with a deadline or hardware wake source.

### Buggy code

```python
def wait_94(clock, deadline):
    while clock.now() < deadline:
        pass
```

### Expected diagnosis

A tight polling loop keeps the CPU active and consumes power while waiting for an external event.

### Corrected code

```python
def wait_94(clock, deadline):
    remaining = deadline - clock.now()
    if remaining > 0:
        clock.sleep(remaining)
```

### Regression tests

```python
# Regression: positive remaining time calls sleep once; expired deadlines do not.
```

## EPY-H-095: peripheral left enabled

- Difficulty: Hard
- Language: Python for Embedded Systems (MicroPython/CircuitPython)
- Perspective: Resource lifetime
- Concept: peripheral left enabled
- Symptom: The sensor remains powered after a failed read.
- Diagnostic goal: Use a cleanup boundary even when the operation raises.

### Buggy code

```python
def read_95(sensor):
    sensor.enable()
    value = sensor.read()
    sensor.disable()
    return value
```

### Expected diagnosis

An exception skips disable, leaving the peripheral and possibly the bus in an unsafe state.

### Corrected code

```python
def read_95(sensor):
    sensor.enable()
    try:
        return sensor.read()
    finally:
        sensor.disable()
```

### Regression tests

```python
# Regression: fake sensor records disable after both success and failure.
```

## EPY-H-096: overflow-prone accumulation

- Difficulty: Hard
- Language: Python for Embedded Systems (MicroPython/CircuitPython)
- Perspective: Numeric stability
- Concept: overflow-prone accumulation
- Symptom: A long-running total loses precision or wraps in fixed-width storage.
- Diagnostic goal: Bound or rescale state according to the measurement contract.

### Buggy code

```python
def accumulate_96(total, sample):
    return total + sample
```

### Expected diagnosis

An unbounded accumulator can exceed the representation or lose useful resolution over long uptime.

### Corrected code

```python
def accumulate_96(total, sample, maximum=1000000):
    result = total + sample
    return min(result, maximum)
```

### Regression tests

```python
assert accumulate_96(999, 2, 1000) == 1000
```

## EPY-H-097: illegal transition

- Difficulty: Hard
- Language: Python for Embedded Systems (MicroPython/CircuitPython)
- Perspective: State machine
- Concept: illegal transition
- Symptom: A device enters a state in which commands are unsafe.
- Diagnostic goal: Centralize legal transitions and reject invalid events.

### Buggy code

```python
def transition_97(state, event):
    if event == 'start': return 'running'
    if event == 'stop': return 'idle'
    return state
```

### Expected diagnosis

The transition table ignores the current state, so stop can succeed before start and start can restart a faulted device.

### Corrected code

```python
def transition_97(state, event):
    allowed = {'idle': {'start': 'running'}, 'running': {'stop': 'idle'}}
    if event not in allowed.get(state, {}):
        raise ValueError('illegal transition')
    return allowed[state][event]
```

### Regression tests

```python
assert transition_97('idle', 'start') == 'running'
try: transition_97('idle', 'stop')
except ValueError: pass
else: raise AssertionError
```

## EPY-H-098: non-idempotent restart

- Difficulty: Hard
- Language: Python for Embedded Systems (MicroPython/CircuitPython)
- Perspective: Watchdog recovery
- Concept: non-idempotent restart
- Symptom: Recovery repeats an action and duplicates an external side effect.
- Diagnostic goal: Make recovery steps idempotent and record progress.

### Buggy code

```python
def recover_98(device):
    device.close_valve()
    device.close_valve()
    device.reset()
```

### Expected diagnosis

Repeating a non-idempotent command can damage hardware or produce a different result on the second attempt.

### Corrected code

```python
def recover_98(device):
    if not device.is_closed():
        device.close_valve()
    device.reset()
```

### Regression tests

```python
# Regression: recovery called twice closes the valve once and resets safely.
```

## EPY-H-099: hardware calls in business logic

- Difficulty: Hard
- Language: Python for Embedded Systems (MicroPython/CircuitPython)
- Perspective: Testability
- Concept: hardware calls in business logic
- Symptom: The algorithm cannot be tested without a board.
- Diagnostic goal: Inject a narrow hardware interface and test the pure decision logic separately.

### Buggy code

```python
def alarm_99(reading):
    Pin(2, Pin.OUT).value(1 if reading > 70 else 0)
```

### Expected diagnosis

Constructing and driving hardware inside the decision function couples policy to a specific runtime and pin.

### Corrected code

```python
def alarm_99(reading, output):
    output( reading > 70 )
```

### Regression tests

```python
seen = []
alarm_99(71, seen.append)
assert seen == [True]
alarm_99(70, seen.append)
assert seen == [True, False]
```

## EPY-H-100: single fault aborts startup

- Difficulty: Hard
- Language: Python for Embedded Systems (MicroPython/CircuitPython)
- Perspective: Boot resilience
- Concept: single fault aborts startup
- Symptom: One optional peripheral prevents the core device from booting.
- Diagnostic goal: Isolate optional initialization and expose degraded operation.

### Buggy code

```python
def boot_100(display, sensor):
    display.init()
    sensor.init()
    return 'ready'
```

### Expected diagnosis

A failure in a nonessential component aborts the whole boot path without recording the degraded capability.

### Corrected code

```python
def boot_100(display, sensor):
    display.init()
    try:
        sensor.init()
        return 'ready'
    except OSError:
        return 'display-only'
```

### Regression tests

```python
# Regression: sensor failure returns display-only while display failure still propagates.
```
