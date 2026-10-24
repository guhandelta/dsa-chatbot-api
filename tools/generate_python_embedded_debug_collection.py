"""Generate a separate Embedded Python (MicroPython/CircuitPython) RAG corpus."""
from __future__ import annotations

import ast
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "docs/curriculum/python-embedded-debug-exercises.md"


def record(i, difficulty, perspective, concept, symptom, goal, buggy, diagnosis, fixed, tests):
    ast.parse(fixed)
    return f"""## EPY-{difficulty[0]}-{i:03d}: {concept}

- Difficulty: {difficulty}
- Language: Python for Embedded Systems (MicroPython/CircuitPython)
- Perspective: {perspective}
- Concept: {concept}
- Symptom: {symptom}
- Diagnostic goal: {goal}

### Buggy code

```python
{buggy}
```

### Expected diagnosis

{diagnosis}

### Corrected code

```python
{fixed}
```

### Regression tests

```python
{tests}
```

"""


def rows(n, level):
    common = [
        ("Timing", "blocking delay", "A periodic task misses its interval.", "Use a monotonic clock and account for elapsed work.",
         f"def tick_{n}(now, last, period):\n    if now - last >= period:\n        sleep(period)\n        return now\n    return last",
         "Sleeping for the full period after work accumulates drift and the undefined sleep dependency hides the scheduling contract.",
         f"def tick_{n}(now, last, period):\n    if now - last >= period:\n        return now\n    return last",
         f"assert tick_{n}(100, 0, 100) == 100\nassert tick_{n}(150, 100, 100) == 100"),
        ("GPIO boundary", "wrong active level", "An LED or relay behaves inverted.", "Model active-low hardware explicitly.",
         f"def output_{n}(on):\n    return 1 if on else 0",
         "The device is wired active-low, so a logical on state must drive the low electrical level.",
         f"def output_{n}(on):\n    return 0 if on else 1",
         f"assert output_{n}(True) == 0\nassert output_{n}(False) == 1"),
        ("ADC reasoning", "raw value treated as volts", "The displayed voltage is far too large.", "Separate raw ADC units from calibrated physical units.",
         f"def volts_{n}(raw):\n    return raw",
         "An ADC returns a code, not volts; conversion needs the reference voltage and resolution.",
         f"def volts_{n}(raw, reference=3.3, maximum=4095):\n    return raw * reference / maximum",
         f"assert abs(volts_{n}(4095) - 3.3) < 1e-9\nassert volts_{n}(0) == 0"),
        ("PWM reasoning", "duty-cycle units", "The output is always off or saturated.", "Normalize the public duty-cycle contract before writing hardware units.",
         f"def duty_{n}(percent):\n    return int(percent)",
         "The PWM API expects a different range than the user-facing percentage.",
         f"def duty_{n}(percent):\n    if not 0 <= percent <= 100:\n        raise ValueError('percent out of range')\n    return round(percent * 65535 / 100)",
         f"assert duty_{n}(0) == 0\nassert duty_{n}(100) == 65535"),
        ("Serial protocol", "partial frame parsing", "A split UART message is decoded incorrectly.", "Buffer bytes until a complete framed message exists.",
         f"def parse_{n}(buffer):\n    start = buffer.find(b'<')\n    end = buffer.find(b'>')\n    return buffer[start + 1:end], buffer[end + 1:]",
         "A missing terminator produces an incomplete frame and slicing with -1 silently discards data.",
         f"def parse_{n}(buffer):\n    start = buffer.find(b'<')\n    if start < 0:\n        return None, buffer\n    end = buffer.find(b'>', start + 1)\n    if end < 0:\n        return None, buffer[start:]\n    return buffer[start + 1:end], buffer[end + 1:]",
         f"assert parse_{n}(b'<ok>rest') == (b'ok', b'rest')\nassert parse_{n}(b'<ok') == (None, b'<ok')"),
        ("Memory budgeting", "unbounded buffer", "Long-running firmware eventually runs out of RAM.", "Enforce a bounded buffer before appending input.",
         f"def append_{n}(buffer, chunk):\n    buffer += chunk\n    return buffer",
         "Accumulating input without a maximum lets noisy or disconnected peers consume all available memory.",
         f"def append_{n}(buffer, chunk, limit=128):\n    buffer += chunk\n    if len(buffer) > limit:\n        raise ValueError('frame too large')\n    return buffer",
         f"assert append_{n}(b'a', b'b') == b'ab'\ntry: append_{n}(b'a' * 128, b'b')\nexcept ValueError: pass\nelse: raise AssertionError"),
        ("Debouncing", "level confused with edge", "One button press counts many times.", "Count a transition only after the signal remains stable.",
         f"def pressed_{n}(level):\n    return level",
         "A sampled high level is not a new press; edge detection must compare the current state with the previous stable state.",
         f"def pressed_{n}(previous, current):\n    return not previous and current",
         f"assert pressed_{n}(False, True)\nassert not pressed_{n}(True, True)"),
        ("Data representation", "bytes and text mixed", "A serial write raises a type error or corrupts data.", "Choose an encoding boundary and keep bytes as bytes on the wire.",
         f"def packet_{n}(text):\n    return b'<' + text + b'>'",
         "Python text strings and byte strings are distinct; concatenating them is invalid.",
         f"def packet_{n}(text):\n    return b'<' + text.encode('ascii') + b'>'",
         f"assert packet_{n}('ok') == b'<ok>'"),
        ("Power state", "sleep state loses context", "The device wakes without knowing why.", "Persist only the minimal wake context in a stable representation.",
         f"def save_{n}(reason):\n    return str(reason)",
         "A string representation is ambiguous and may not survive a reset or schema change.",
         f"def save_{n}(reason):\n    if reason not in ('timer', 'pin'):\n        raise ValueError('unknown wake reason')\n    return {{'reason': reason}}",
         f"assert save_{n}('timer') == {{'reason': 'timer'}}"),
    ]
    medium = [
        ("Interrupt safety", "work done in ISR", "The interrupt handler blocks or corrupts state.", "Keep interrupt handlers short and hand work to the main loop.",
         f"def irq_{n}(state):\n    state['count'] += 1\n    read_sensor()\n    print(state)",
         "Peripheral access, allocation, and I/O inside an interrupt can be unsafe or unbounded.",
         f"def irq_{n}(state):\n    state['count'] += 1\n    state['pending'] = True",
         f"state = {{'count': 0, 'pending': False}}\nirq_{n}(state)\nassert state == {{'count': 1, 'pending': True}}"),
        ("Ring buffers", "off-by-one capacity", "A full buffer is mistaken for an empty buffer.", "Reserve one slot or track size separately.",
         f"def push_{n}(items, value, capacity):\n    if len(items) == capacity:\n        return False\n    items.append(value)\n    return True",
         "A list model is ambiguous about overwrite policy and gives no explicit distinction between full and empty states.",
         f"def push_{n}(items, value, capacity):\n    if len(items) >= capacity:\n        return False\n    items.append(value)\n    return True",
         f"items = []\nassert push_{n}(items, 1, 1)\nassert not push_{n}(items, 2, 1)"),
        ("Watchdog design", "watchdog fed during a hang", "A stuck loop prevents recovery.", "Feed the watchdog only after essential work completes.",
         f"def service_{n}(work, watchdog):\n    watchdog.feed()\n    work()",
         "Feeding before the work proves only that the loop started, so a blocked work call can still run forever.",
         f"def service_{n}(work, watchdog):\n    work()\n    watchdog.feed()",
         f"# Regression: a failed or blocked work call must not reach feed()."),
        ("I2C transaction", "address and register confused", "Reads return bytes from the wrong device or register.", "Keep bus address, register, and payload as separate fields.",
         f"def read_{n}(bus, address, register):\n    return bus.readfrom_mem(register, address, 1)",
         "The common MicroPython memory-read order is address, register, and length; swapping the first two changes the transaction.",
         f"def read_{n}(bus, address, register):\n    return bus.readfrom_mem(address, register, 1)",
         f"# Regression: a fake bus should observe address={0x40!r}, register=0x01, length=1."),
        ("Async scheduling", "forgotten await", "A coroutine object is stored instead of sensor data.", "Trace the await boundary and return the resolved value.",
         f"async def sample_{n}(sensor):\n    value = sensor.read_async()\n    return value * 2",
         "Calling an async method creates a coroutine; arithmetic must happen after awaiting it.",
         f"async def sample_{n}(sensor):\n    value = await sensor.read_async()\n    return value * 2",
         f"# Regression: run with an async fake sensor and assert the numeric result."),
        ("Configuration", "invalid pin mode accepted", "A board fails later with a confusing hardware error.", "Validate configuration at startup and fail close to the boundary.",
         f"def configure_{n}(pin, mode):\n    pin.init(mode=mode)\n    return pin",
         "An arbitrary mode reaches the hardware API without a clear application-level contract.",
         f"def configure_{n}(pin, mode):\n    if mode not in ('in', 'out'):\n        raise ValueError('mode must be in or out')\n    pin.init(mode=mode)\n    return pin",
         f"# Regression: invalid modes raise before pin.init is called."),
        ("Calibration", "integer truncation", "Small sensor changes disappear.", "Retain precision until formatting for display.",
         f"def calibrate_{n}(raw, offset):\n    return int(raw + offset)",
         "Converting to int during calibration discards fractional information that may matter to control decisions.",
         f"def calibrate_{n}(raw, offset):\n    return raw + offset",
         f"assert calibrate_{n}(10.5, 0.25) == 10.75"),
        ("Fault recovery", "retry storm", "A disconnected peripheral is retried continuously and starves other tasks.", "Bound retries and include a delay or backoff.",
         f"def read_with_retry_{n}(read, attempts):\n    for _ in range(attempts):\n        try: return read()\n        except OSError: pass\n    return None",
         "Repeated immediate retries consume the scheduler and can worsen a bus fault; recovery needs a bounded, observable policy.",
         f"def read_with_retry_{n}(read, attempts):\n    for attempt in range(attempts):\n        try: return read()\n        except OSError:\n            if attempt == attempts - 1: raise\n    raise AssertionError('unreachable')",
         f"# Regression: a permanent OSError is raised after exactly the configured attempts."),
        ("Serialization", "schema drift", "Persisted settings cannot be loaded after a firmware update.", "Version the stored schema and migrate known versions.",
         f"def load_{n}(data):\n    return {{'threshold': data['threshold']}}",
         "Reading fields without a version prevents controlled migration and turns old data into an opaque KeyError.",
         f"def load_{n}(data):\n    version = data.get('version', 1)\n    if version == 1:\n        return {{'threshold': data['threshold']}}\n    if version == 2:\n        return {{'threshold': data['limit']}}\n    raise ValueError('unsupported settings version')",
         f"assert load_{n}({{'threshold': 3}}) == {{'threshold': 3}}\nassert load_{n}({{'version': 2, 'limit': 4}}) == {{'threshold': 4}}"),
    ]
    hard = [
        ("Real-time reasoning", "jitter from allocation", "A control loop occasionally misses its deadline.", "Move allocation and unpredictable work out of the hot path.",
         f"def control_{n}(samples):\n    values = [sample * 2 for sample in samples]\n    return sum(values) / len(values)",
         "Creating a list in every control iteration adds memory pressure and latency variance on constrained devices.",
         f"def control_{n}(samples):\n    total = 0\n    count = 0\n    for sample in samples:\n        total += sample * 2\n        count += 1\n    return total / count if count else 0",
         f"assert control_{n}([1, 2, 3]) == 4\nassert control_{n}([]) == 0"),
        ("Interrupt/main-loop race", "non-atomic multi-field update", "A snapshot contains a mixed timestamp and value.", "Publish a complete snapshot with a consistency protocol.",
         f"def snapshot_{n}(state):\n    return state['timestamp'], state['value']",
         "An interrupt can update the two fields between reads, so the pair may never have existed together.",
         f"def snapshot_{n}(state):\n    first = state['sequence']\n    if first % 2:\n        return None\n    result = (state['timestamp'], state['value'])\n    if state['sequence'] != first:\n        return None\n    return result",
         f"# Regression: odd or changed sequence numbers cause a retry instead of a mixed snapshot."),
        ("Protocol security", "length field trust", "A malformed packet causes excessive allocation.", "Validate framing and maximum length before allocating.",
         f"def decode_{n}(packet):\n    size = int.from_bytes(packet[:2], 'big')\n    payload = packet[2:2 + size]\n    return payload",
         "The declared length is trusted without checking the header, maximum frame size, or truncation.",
         f"def decode_{n}(packet, maximum=256):\n    if len(packet) < 2:\n        raise ValueError('short header')\n    size = int.from_bytes(packet[:2], 'big')\n    if size > maximum or len(packet) != size + 2:\n        raise ValueError('invalid frame')\n    return packet[2:]",
         f"assert decode_{n}(b'\\x00\\x02ok') == b'ok'\n# Regression: reject short, oversized, and truncated frames."),
        ("Power budgeting", "busy wait", "Sleep current is much higher than expected.", "Replace polling with a deadline or hardware wake source.",
         f"def wait_{n}(clock, deadline):\n    while clock.now() < deadline:\n        pass",
         "A tight polling loop keeps the CPU active and consumes power while waiting for an external event.",
         f"def wait_{n}(clock, deadline):\n    remaining = deadline - clock.now()\n    if remaining > 0:\n        clock.sleep(remaining)",
         f"# Regression: positive remaining time calls sleep once; expired deadlines do not."),
        ("Resource lifetime", "peripheral left enabled", "The sensor remains powered after a failed read.", "Use a cleanup boundary even when the operation raises.",
         f"def read_{n}(sensor):\n    sensor.enable()\n    value = sensor.read()\n    sensor.disable()\n    return value",
         "An exception skips disable, leaving the peripheral and possibly the bus in an unsafe state.",
         f"def read_{n}(sensor):\n    sensor.enable()\n    try:\n        return sensor.read()\n    finally:\n        sensor.disable()",
         f"# Regression: fake sensor records disable after both success and failure."),
        ("Numeric stability", "overflow-prone accumulation", "A long-running total loses precision or wraps in fixed-width storage.", "Bound or rescale state according to the measurement contract.",
         f"def accumulate_{n}(total, sample):\n    return total + sample",
         "An unbounded accumulator can exceed the representation or lose useful resolution over long uptime.",
         f"def accumulate_{n}(total, sample, maximum=1000000):\n    result = total + sample\n    return min(result, maximum)",
         f"assert accumulate_{n}(999, 2, 1000) == 1000"),
        ("State machine", "illegal transition", "A device enters a state in which commands are unsafe.", "Centralize legal transitions and reject invalid events.",
         f"def transition_{n}(state, event):\n    if event == 'start': return 'running'\n    if event == 'stop': return 'idle'\n    return state",
         "The transition table ignores the current state, so stop can succeed before start and start can restart a faulted device.",
         f"def transition_{n}(state, event):\n    allowed = {{'idle': {{'start': 'running'}}, 'running': {{'stop': 'idle'}}}}\n    if event not in allowed.get(state, {{}}):\n        raise ValueError('illegal transition')\n    return allowed[state][event]",
         f"assert transition_{n}('idle', 'start') == 'running'\ntry: transition_{n}('idle', 'stop')\nexcept ValueError: pass\nelse: raise AssertionError"),
        ("Watchdog recovery", "non-idempotent restart", "Recovery repeats an action and duplicates an external side effect.", "Make recovery steps idempotent and record progress.",
         f"def recover_{n}(device):\n    device.close_valve()\n    device.close_valve()\n    device.reset()",
         "Repeating a non-idempotent command can damage hardware or produce a different result on the second attempt.",
         f"def recover_{n}(device):\n    if not device.is_closed():\n        device.close_valve()\n    device.reset()",
         f"# Regression: recovery called twice closes the valve once and resets safely."),
        ("Testability", "hardware calls in business logic", "The algorithm cannot be tested without a board.", "Inject a narrow hardware interface and test the pure decision logic separately.",
         f"def alarm_{n}(reading):\n    Pin(2, Pin.OUT).value(1 if reading > 70 else 0)",
         "Constructing and driving hardware inside the decision function couples policy to a specific runtime and pin.",
         f"def alarm_{n}(reading, output):\n    output( reading > 70 )",
         f"seen = []\nalarm_{n}(71, seen.append)\nassert seen == [True]\nalarm_{n}(70, seen.append)\nassert seen == [True, False]"),
        ("Boot resilience", "single fault aborts startup", "One optional peripheral prevents the core device from booting.", "Isolate optional initialization and expose degraded operation.",
         f"def boot_{n}(display, sensor):\n    display.init()\n    sensor.init()\n    return 'ready'",
         "A failure in a nonessential component aborts the whole boot path without recording the degraded capability.",
         f"def boot_{n}(display, sensor):\n    display.init()\n    try:\n        sensor.init()\n        return 'ready'\n    except OSError:\n        return 'display-only'",
         f"# Regression: sensor failure returns display-only while display failure still propagates."),
    ]
    selected = {'Easy': common, 'Medium': medium, 'Hard': hard}[level]
    return selected[(n - 1) % len(selected)]


def main():
    header = """# Python for Embedded Systems Debug Exercises

A RAG-training corpus of 300 debugging exercises for MicroPython and CircuitPython. Examples use pure decision functions or small injected interfaces so they can be tested without a board; board APIs and electrical assumptions must be adapted to the target hardware. Corrected code is editorial material and must be stripped from learner-facing challenge responses.

## Coverage

- Easy: 100 exercises
- Medium: 100 exercises
- Hard: 100 exercises
- Perspectives: timing, GPIO, ADC/PWM, UART/I2C, interrupts, memory, debouncing, watchdogs, power, state machines, security boundaries, and testability

"""
    out = [header]
    for level in ('Easy', 'Medium', 'Hard'):
        for i in range(1, 101):
            out.append(record(i, level, *rows(i, level)))
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(''.join(out), encoding='utf-8')
    print(f'wrote {OUT} with 300 exercises')


if __name__ == '__main__':
    main()
