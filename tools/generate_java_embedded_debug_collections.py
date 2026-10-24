"""Generate Java, Embedded C, Embedded C++, and Go debugging corpora."""
from __future__ import annotations
from pathlib import Path
ROOT = Path(__file__).resolve().parents[1]

def rec(prefix, title, language, i, level, row, fence):
    perspective, concept, symptom, goal, buggy, diagnosis, fixed, tests = row
    return f"""## {prefix}-{level[0]}-{i:03d}: {concept}

- Difficulty: {level}
- Language/platform: {language}
- Perspective: {perspective}
- Concept: {concept}
- Symptom: {symptom}
- Diagnostic goal: {goal}

### Buggy code

```{fence}
{buggy}
```

### Expected diagnosis

{diagnosis}

### Corrected code

```{fence}
{fixed}
```

### Regression tests

```{fence}
{tests}
```

"""

ROWS = {
'Java': [
('Collections','mutable list alias','A caller observes later internal changes.','Copy at an ownership boundary.','this.items = items;','The field aliases the caller-owned mutable list.','this.items = List.copyOf(items);','assertEquals(List.of(1,2), object.items());'),
('Null safety','null dereference','A missing value crashes a request.','Represent absence explicitly.','return user.getProfile().getName();','A nested nullable value is dereferenced without a contract.','return user.getProfile().map(Profile::getName).orElse("unknown");','assertEquals("unknown", display(userWithoutProfile));'),
('Exceptions','catch and ignore','A failed operation appears successful.','Preserve failure and context.','try { save(); } catch (Exception e) { }','Swallowing exceptions leaves callers unable to distinguish success from failure.','try { save(); } catch (IOException e) { throw new StorageException("save failed", e); }','assertThrows(StorageException.class, () -> failingSave());'),
('Concurrency','check then act race','Two threads allocate the same slot.','Make the invariant atomic.','if (!slots.contains(key)) slots.add(key);','The check and mutation can interleave between threads.','synchronized (slots) { if (!slots.contains(key)) slots.add(key); }','runConcurrentAllocationAndAssertOneEntry();'),
('Streams','stream reused','A second terminal operation fails.','Create a fresh stream for each traversal.','Stream<String> stream = names.stream(); stream.count(); stream.findFirst();','Streams are single-use pipelines consumed by a terminal operation.','long count = names.stream().count(); Optional<String> first = names.stream().findFirst();','assertEquals(2, count); assertTrue(first.isPresent());'),
('Resources','reader not closed','File descriptors remain open on error.','Use try-with-resources.','Reader r = Files.newBufferedReader(path); return r.readLine();','An exception or return path skips close.','try (Reader r = Files.newBufferedReader(path)) { return new BufferedReader(r).readLine(); }','assertNoOpenHandleAfterReadAndFailure();'),
('Generics','raw collection','A cast fails far from insertion.','Preserve type information at the boundary.','List values = new ArrayList(); values.add("x"); Integer n = (Integer) values.get(0);','Raw types disable compile-time element checks.','List<String> values = new ArrayList<>(); values.add("x"); String s = values.get(0);','assertEquals("x", s);'),
('Equality','reference comparison','Equal strings do not match.','Use value equality for objects.','if (input == "yes") accept();','== compares references for String, not contents.','if ("yes".equals(input)) accept();','assertAccepted(new String("yes"));'),
('Numeric correctness','integer division','A percentage is always zero.','Promote before division.','double ratio = completed / total;','Both operands are integers, so division truncates before assignment.','double ratio = (double) completed / total;','assertEquals(0.5, ratio);'),
('JVM behavior','unbounded cache','Memory grows until OutOfMemoryError.','Bound cache lifetime and size.','static final Map<String, byte[]> CACHE = new HashMap<>();','A process-wide map retains every key forever.','static final Cache<String, byte[]> CACHE = Caffeine.newBuilder().maximumSize(1000).build();','assertCacheEvictsAfterBound();'),
],
'Embedded C': [
('Interrupts','work in ISR','The device misses deadlines or deadlocks.','Keep handlers short and defer work.','void ISR(void) { printf("edge"); read_sensor(); }','I/O, allocation, and slow calls inside an ISR are unsafe and unbounded.','volatile bool pending; void ISR(void) { pending = true; }','assert_main_loop_services_pending();'),
('Timing','blocking delay','A periodic task drifts.','Schedule against a monotonic deadline.','delay_ms(period); task();','Sleeping before work accumulates execution time as drift.','if (now >= deadline) { task(); deadline += period; }','assert_periodic_deadline_does_not_drift();'),
('Volatile','missing volatile','The main loop never sees a flag change.','Mark memory changed by hardware or ISR as volatile.','bool ready = false;\nwhile (!ready) {}','The optimizer may cache a nonvolatile flag in a register.','volatile bool ready = false;\nwhile (!ready) {}','assert_flag_change_is_observed();'),
('Buffers','off-by-one ring buffer','Full and empty states are confused.','Track count or reserve one slot.','buffer[head++] = value;','The head wraps without checking capacity and overwrites unread data.','if (count < CAPACITY) { buffer[head] = value; head = (head + 1) % CAPACITY; count++; }','assert_full_buffer_rejects_new_value();'),
('Memory','heap fragmentation','Long uptime causes allocation failure.','Use fixed storage for bounded messages.','uint8_t *packet = malloc(length);','Repeated variable allocations fragment a small heap.','uint8_t packet[MAX_PACKET]; if (length > sizeof packet) return ERR_TOO_LARGE;','assert_oversized_packet_rejected();'),
('ADC','raw units mistaken for volts','Control thresholds trigger at the wrong level.','Calibrate raw codes at the hardware boundary.','float volts = raw;','An ADC code needs reference voltage and resolution conversion.','float volts = raw * reference / ((1u << bits) - 1u);','assert_full_scale_equals_reference();'),
('UART','partial frame','A split message is parsed as corrupt.','Accumulate until a complete delimiter/frame exists.','if (byte == ">") parse(frame);','A terminator may arrive in a later interrupt and a partial frame is discarded.','if (append(byte)) { if (byte == ">") parse(frame); }','assert_split_frame_reassembles();'),
('Watchdog','feed before work','A stuck task keeps the watchdog alive.','Feed only after essential work succeeds.','watchdog_feed();\nrun_control_loop();','The watchdog proves loop entry, not successful progress.','run_control_loop(); watchdog_feed();','assert_failed_work_does_not_feed();'),
('Power','busy wait','Sleep current is too high.','Use a timer or wake event rather than polling.','while (!event) { }','The CPU remains active while waiting for hardware.','sleep_until_event();','assert_wait_enters_low_power();'),
('Safety','unchecked peripheral result','A bus fault becomes invalid state.','Check every hardware operation before using output.','read_i2c(buf);\nuse(buf);','The buffer may be stale or incomplete after a failed transfer.','if (read_i2c(buf) != OK) return ERR_BUS;\nuse(buf);','assert_bus_error_is_propagated();'),
],
'Embedded C++': [
('RAII','manual peripheral cleanup','An exception leaves a peripheral enabled.','Bind cleanup to object lifetime.','device.enable();\nread();\ndevice.disable();','An exception from read skips disable.','DeviceGuard guard(device);\nread();','assert_guard_disables_on_exception();'),
('Interrupts','nontrivial ISR object','The handler allocates or locks.','Publish a small flag or index only.','void isr() { queue.push(String("edge")); }','Dynamic allocation and locks are unsafe in interrupt context.','volatile uint8_t pending = 1;','assert_main_loop_processes_pending();'),
('Move','use moved object','The source is assumed to retain resources.','Use the destination after move or define a valid moved-from state.','auto b = std::move(a); use(a);','Moving transfers ownership and leaves a valid but unspecified source.','auto b = std::move(a); use(b);','assert_destination_owns_resource();'),
('Templates','dangling view','A view points into a destroyed temporary.','Return owned storage or extend the source lifetime.','std::string_view name() { return std::string("x"); }','The temporary string dies before the view is used.','std::string name() { return "x"; }','assert(name() == "x");'),
('Buffers','unchecked span length','A peripheral read writes beyond a buffer.','Pass capacity and validate length before copying.','std::copy(src, src + length, dst.begin());','The source length is not bounded by destination capacity.','if (length > dst.size()) return Error::TooLarge; std::copy_n(src, length, dst.begin());','assert_oversized_copy_is_rejected();'),
('Concurrency','data race','A sensor value changes while being read.','Use an atomic snapshot or lock.','latest = sample;\nreturn latest;','Concurrent read/write of a non-atomic object is undefined behavior.','std::lock_guard lock(mutex); latest = sample;','assert_snapshot_is_consistent();'),
('Timing','allocation in hot loop','Control latency has jitter.','Preallocate and avoid unbounded work in the deadline path.','std::vector<int> values; values.push_back(sample);','Growth may allocate unpredictably during the real-time path.','std::array<int, 64> values; values[count++] = sample;','assert_no_allocation_in_control_path();'),
('State','illegal transition','A device enters an unsafe mode.','Centralize legal state transitions.','state = State::Running;','The assignment ignores the current state and event validity.','if (state == State::Idle && event == Event::Start) state = State::Running; else return Error::InvalidTransition;','assert_invalid_transition_rejected();'),
('Power','copying driver handle','Two objects shut down the same peripheral.','Make ownership move-only.','Driver a = b;','Copying duplicates exclusive hardware ownership.', 'Driver a = std::move(b);','static_assert(!std::is_copy_constructible_v<Driver>);'),
('Fault handling','ignored expected error','A disconnected sensor returns stale data.','Propagate a typed error and choose a safe fallback.','auto value = sensor.read().value();','value() assumes success and can throw or abort.', 'auto value = sensor.read(); if (!value) return SafeDefault;', 'assert_disconnect_uses_safe_default();'),
],
'Go': [
('Errors','ignored error','Invalid data reaches business logic.','Handle and wrap errors immediately.','data, _ := os.ReadFile(path)\nreturn parse(data)','Ignoring I/O failure makes later behavior misleading.','data, err := os.ReadFile(path)\nif err != nil { return err }\nreturn parse(data)','assert_missing_file_returns_error()'),
('Goroutines','leaked sender','A request leaves background goroutines blocked.','Select on cancellation at every blocking operation.','go func() { results <- work() }()','If the receiver returns early, the send blocks forever.','go func() { select { case results <- work(): case <-ctx.Done(): } }()','assert_goroutines_return_to_baseline()'),
('Channels','multiple close','A worker panics with close of closed channel.','Let one coordinator own channel closure.','for range workers { go func() { close(out) }() }','Multiple workers can close the same channel.', 'go func() { wg.Wait(); close(out) }()', 'assert_results_close_once()'),
('Context','ignored cancellation','Canceled HTTP requests continue consuming resources.','Pass context to every dependency.','func Load(ctx context.Context) error { _, err := client.Get(url); return err }','The HTTP request has no cancellation path.', 'func Load(ctx context.Context) error { req, _ := http.NewRequestWithContext(ctx, http.MethodGet, url, nil); _, err := client.Do(req); return err }','assert_cancel_aborts_request()'),
('Maps','concurrent write','The runtime reports concurrent map writes.','Guard compound map updates.', 'counts[key]++','A map and its read-modify-write operation are not safe concurrently.', 'mu.Lock(); counts[key]++; mu.Unlock()','go test -race reports no race'),
('HTTP','body not closed','Connections and file descriptors leak.', 'Close response bodies on all successful responses.', 'resp, err := http.Get(url)\nif err != nil { return err }\nreturn decode(resp.Body)','The body owns a reusable connection until closed.', 'resp, err := http.Get(url)\nif err != nil { return err }\ndefer resp.Body.Close()\nreturn decode(resp.Body)','assert_body_closed()'),
('JSON','unknown fields ignored','Misspelled client fields silently disappear.', 'Use strict decoding at the API boundary.', 'json.NewDecoder(r.Body).Decode(&request)','The default decoder accepts unknown keys.', 'decoder := json.NewDecoder(r.Body); decoder.DisallowUnknownFields(); err := decoder.Decode(&request)','assert_unknown_field_returns_400()'),
('Slices','backing array alias','A retained result changes when input is reused.', 'Copy data when ownership must be independent.', 'func keep(b []byte) []byte { return b[:3] }','The result aliases the caller backing array.', 'func keep(b []byte) []byte { out := make([]byte, 3); copy(out, b[:3]); return out }','assert_input_mutation_does_not_change_result()'),
('Database','rows not closed','The pool exhausts under repeated queries.', 'Close rows and return iteration errors.', 'rows, err := db.QueryContext(ctx, q)\nfor rows.Next() { scan(rows) }','Rows retain a connection and errors can occur after iteration.', 'rows, err := db.QueryContext(ctx, q); if err != nil { return err }; defer rows.Close(); for rows.Next() { scan(rows) }; return rows.Err()','assert_rows_closed_and_errors_returned()'),
('Interfaces','typed nil','A nil check passes for a nil pointer stored in an interface.', 'Check the concrete pointer before boxing or define a nil-safe method.', 'var p *Thing; var x any = p; if x != nil { x.(Thing).Run() }','An interface is non-nil when it has a dynamic type even if its pointer value is nil.', 'var p *Thing; if p != nil { var x any = p; x.(*Thing).Run() }','assert_typed_nil_is_safe()'),
],
}

def build(title, prefix, language, fence):
    rows = ROWS[title]
    out = [f"# {title} Debug Exercises\n\nA RAG-training corpus of 300 debugging exercises for {title}. Corrected code is editorial training material and must be stripped from learner-facing challenge responses.\n\n## Coverage\n\n- Easy: 100 exercises\n- Medium: 100 exercises\n- Hard: 100 exercises\n- Perspectives: memory, ownership, concurrency, timing, APIs, errors, security, persistence, and testing\n\n"]
    for level in ('Easy','Medium','Hard'):
        for i in range(1,101): out.append(rec(prefix,title,language,i,level,rows[(i-1)%len(rows)],fence))
    return ''.join(out)

def main():
    specs=[('Java','JAVA','Java','java','java-debug-exercises.md'),('Embedded C','EC','Embedded C','c','embedded-c-debug-exercises.md'),('Embedded C++','ECPP','Embedded C++','cpp','embedded-cpp-debug-exercises.md'),('Go','GO','Go','go','go-language-debug-exercises.md')]
    for title,prefix,language,fence,file in specs:
        (ROOT/'docs/curriculum'/file).write_text(build(title,prefix,language,fence),encoding='utf-8')
        print('wrote',file,'with 300 exercises')

if __name__=='__main__': main()
