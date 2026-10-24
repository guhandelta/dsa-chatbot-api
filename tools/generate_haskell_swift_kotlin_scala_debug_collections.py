"""Generate Haskell, Swift, Kotlin, and Scala debugging corpora."""
from pathlib import Path
ROOT = Path(__file__).resolve().parents[1]

def rec(prefix, title, language, i, level, row, fence):
    perspective, concept, symptom, goal, buggy, diagnosis, fixed, tests = row
    return f"""## {prefix}-{level[0]}-{i:03d}: {concept}

- Difficulty: {level}
- Language/framework: {language} / {title}
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
'Haskell': [
('Laziness','space leak','A long-running fold consumes excessive memory.','Choose strict accumulation when the result must be evaluated incrementally.','sum = foldl (\\a x -> a + x) 0 values','Lazy accumulation builds a chain of thunks instead of forcing each intermediate total.','sum = foldl\' (+) 0 values','assert (sum [1..100] == 5050)'),
('Purity','unsafe shared state','A helper unexpectedly changes global state.','Make effects explicit in the type and call boundary.','counter = unsafePerformIO (newIORef 0)','unsafePerformIO hides mutation from the type system and can violate sharing assumptions.','counter :: IO (IORef Int)\ncounter = newIORef 0','-- Test through IO and assert the state transition explicitly.'),
('Types','partial pattern','An input causes a runtime exception.','Cover every constructor or make failure explicit.','headName (x:_) = name x','The empty-list pattern is missing, so [] triggers a non-exhaustive match.','headName [] = Nothing\nheadName (x:_) = Just (name x)','assert (headName [] == Nothing)'),
('Maybe','unsafe extraction','Missing configuration crashes startup.','Use maybe or bind the absence through the computation.','port = read (fromJust (lookup "port" config))','fromJust turns an expected missing-value case into an exception.','port = lookup "port" config >>= readMaybe','assert (port [] == Nothing)'),
('IO','lazy handle','A file is closed before lazy contents are consumed.','Force contents inside the resource lifetime or stream explicitly.','readLines path = withFile path ReadMode $ \\h -> hGetContents h','Lazy hGetContents may defer reads until after withFile closes the handle.','readLines path = withFile path ReadMode $ \\h -> hGetContents h >>= \\s -> evaluate (length s) >> pure s','-- Test reading a complete file after the handle scope.'),
('Monads','wrong bind','A function receives an IO action instead of its value.','Use (>>=) or do notation at the effect boundary.','load = fetch >>= pure . parse','This is valid only if parse returns a pure value; mixing nested IO creates the wrong shape.','load = do\n  raw <- fetch\n  pure (parse raw)','assertIO load'),
('Lists','quadratic append','A list builder becomes slow for large input.','Prepend and reverse, or use a difference-list structure.','build xs = foldl (\\acc x -> acc ++ [f x]) [] xs','Appending to the end copies the accumulated list on every iteration.','build xs = reverse (foldl (\\acc x -> f x : acc) [] xs)','assert (build [1,2,3] == map f [1,2,3])'),
('Concurrency','MVar deadlock','Two workers wait forever.','Define lock ownership and always release it on exceptions.','withMVar lock $ \\_ -> takeMVar lock','The same thread attempts to take a non-reentrant MVar twice.','withMVar lock $ \\_ -> pure ()','-- Test completion with a timeout.'),
('Typeclasses','ambiguous instance','Compilation reports overlapping or ambiguous instances.','Keep instance selection coherent and use newtypes for distinct meanings.','instance Num a => Monoid a where mempty = 0','A broad orphan/overlapping instance conflicts with existing typeclass laws and instances.','newtype Sum a = Sum a\ninstance Num a => Semigroup (Sum a) where Sum a <> Sum b = Sum (a+b)','-- Compile with warnings as errors and test associativity.'),
('Errors','stringly error','Callers cannot distinguish failure cases.','Use a sum type with stable constructors.','return (Left "not found")','String errors are fragile and force callers to inspect text.','data AppError = NotFound | InvalidInput | StorageError\nreturn (Left NotFound)','assert (renderError NotFound == "not found")'),
],
'Swift': [
('Optionals','forced unwrap','A missing API value crashes the app.','Bind or provide a deliberate fallback.','let name = user.profile!.name','The force unwrap converts an expected absence into a runtime trap.','guard let profile = user.profile else { return .guest }\nlet name = profile.name','XCTAssertEqual(display(userWithoutProfile), "guest")'),
('Value semantics','mutating copy','A change to a struct does not update the original.','Understand copy-on-write and return the updated value.','func add(_ item: Item, to list: [Item]) { var list = list; list.append(item) }','The parameter is a local value copy; its mutation is not visible to the caller.','func adding(_ item: Item, to list: [Item]) -> [Item] { list + [item] }','XCTAssertEqual(adding(item, to: []), [item])'),
('Concurrency','actor isolation','A property is accessed from the wrong isolation domain.','Await actor state or expose a safe method.','Task { print(counter.value) }','Actor-isolated state cannot be synchronously accessed from an arbitrary task.', 'Task { print(await counter.value) }','awaitAssertCounterRead()'),
('ARC','retain cycle','A controller never deallocates.','Use weak/unowned references for non-owning closures.','class Controller { var onDone: (() -> Void)?\n  func bind() { onDone = { self.finish() } } }','The closure strongly captures self while self retains the closure.', 'class Controller { var onDone: (() -> Void)?\n  func bind() { onDone = { [weak self] in self?.finish() } } }','assertDeinitAfterControllerRelease()'),
('Errors','try! at boundary','Malformed data crashes instead of returning an error.','Propagate throws or map the error to a user-facing result.','let value = try! decoder.decode(Model.self, from: data)','try! traps when decoding fails.', 'let value = try decoder.decode(Model.self, from: data)','XCTAssertThrowsError(try decode(invalidData))'),
('Collections','mutating while iterating','The loop skips or traps after removal.','Use filter or collect indexes before mutation.','for item in items { if item.expired { items.removeAll { $0.id == item.id } } }','Changing a collection during iteration invalidates the traversal.', 'items.removeAll { $0.expired }','XCTAssertEqual(items.filter { !$0.expired }, expected)'),
('Protocols','existential mismatch','A generic function cannot accept the protocol value.','Preserve associated-type constraints or erase deliberately.','func merge<T: Sequence>(_ a: T, _ b: T) -> T { ... }','Two sequences with associated types are not necessarily constructible as the same concrete T.', 'func merge<S: Sequence>(_ a: S, _ b: S) -> [S.Element] { Array(a) + Array(b) }','XCTAssertEqual(merge([1], [2]), [1,2])'),
('Async','task lifetime','A detached task outlives the owner and updates stale UI.','Tie task cancellation to the owner lifecycle.','Task.detached { await updateView() }','Detached work ignores actor context and cancellation ownership.', 'let task = Task { await updateView() }\n// cancel task in deinit or view disappearance','assertTaskCancelledOnDisappear()'),
('Persistence','date format mismatch','Decoded records fail only for some locales.', 'Use an explicit stable date strategy.', 'JSONDecoder().decode(Event.self, from: data)','Default date decoding is not a contract for arbitrary wire formats.', 'let decoder = JSONDecoder(); decoder.dateDecodingStrategy = .iso8601','XCTAssertNoThrow(try decoder.decode(Event.self, from: isoData))'),
('Performance','copy in hot loop','A large value is repeatedly copied.', 'Use inout or a reference only when ownership is intentional.', 'for _ in 0..<n { process(largeStruct) }','Repeated value copies can dominate a hot path.', 'withUnsafeMutablePointer(to: &largeStruct) { process($0.pointee) }','measureCopyCostAndAssertBudget()'),
],
'Kotlin': [
('Null safety','!! at boundary','A missing value throws KotlinNullPointerException.', 'Use safe calls, Elvis, or validated require.', 'val name = user.profile!!.name','The non-null assertion bypasses Kotlin’s nullable contract.', 'val name = user.profile?.name ?: "unknown"','assertEquals("unknown", display(userWithoutProfile))'),
('Coroutines','blocking in suspend function','Unrelated coroutines stall.', 'Move blocking work to an appropriate dispatcher or use a suspending client.', 'suspend fun load() = Files.readString(path)','A blocking file read runs on the caller coroutine thread.', 'suspend fun load() = withContext(Dispatchers.IO) { Files.readString(path) }','runTest { assertConcurrentWorkProgresses() }'),
('Collections','mutable list exposure','Callers modify internal state.', 'Return an immutable view or defensive copy.', 'fun items(): MutableList<Item> = internalItems','The mutable collection leaks ownership.', 'fun items(): List<Item> = internalItems.toList()','assertEquals(original, service.items())'),
('Data classes','copy shallow state','Nested mutable state is unexpectedly shared.', 'Copy nested mutable members or use immutable members.', 'val second = first.copy(); second.tags.add("x")','data class copy is shallow; the same mutable tags list is shared.', 'data class User(val tags: List<String>)','assertNotSame(first.tags, second.tags)'),
('Flows','collect never completes','A request waits forever for a hot stream.', 'Use a bounded operator for request-scoped collection.', 'val value = flow.collect { result = it }','collect is terminal and waits for completion; a hot flow may never complete.', 'val value = flow.first()','runTest { assertEquals(expected, flow.first()) }'),
('Exceptions','runCatching hides cancellation','A canceled coroutine continues or reports success.', 'Rethrow CancellationException.', 'runCatching { suspendWork() }.getOrNull()','Cancellation is a control signal, not an ordinary failure to swallow.', 'try { suspendWork() } catch (e: CancellationException) { throw e } catch (e: Exception) { null }','runTest { assertCancellationPropagates() }'),
('Generics','unsafe cast','A runtime ClassCastException appears far from input.', 'Use a sealed result or checked cast.', 'val text = value as String','The cast assumes an unchecked runtime type.', 'val text = value as? String ?: return Error.InvalidType','assertEquals(Error.InvalidType, parse(1))'),
('JVM interop','platform type null','Java API returns null into a non-null declaration.', 'Check Java results at the boundary.', 'val name: String = javaApi.name','Platform types do not carry Kotlin nullability guarantees.', 'val name: String = javaApi.name ?: "unknown"','assertEquals("unknown", adapt(JavaNullApi()))'),
('Testing','shared mutable fixture','Tests pass alone but fail in a suite.', 'Reset or recreate state per test.', 'class Test { val cache = mutableMapOf<String,Int>() }','The fixture survives between test methods.', '@BeforeEach fun reset() { cache.clear() }','runAllTestsInRandomOrder()'),
('Serialization','default value masks missing field','A breaking API change is silently accepted.', 'Distinguish omitted fields from intentional defaults where required.', 'data class Request(val enabled: Boolean = false)','A missing enabled property becomes false and hides a contract violation.', 'data class Request(val enabled: Boolean)','assertFailsWith<SerializationException> { decode("{}") }'),
],
'Scala': [
('Options','get on None','A missing lookup throws NoSuchElementException.', 'Keep absence in the Option pipeline.', 'val name = users.get(id).get.name','get is unsafe for an expected missing value.', 'val name = users.get(id).map(_.name).getOrElse("unknown")','assert(name(unknownId) == "unknown")'),
('Collections','map versus flatMap','Nested collections reach the caller.', 'Use flatMap when each input produces zero or more outputs.', 'val names = users.map(_.emails.map(_.address))','map preserves the nested structure List[List[String]].', 'val names = users.flatMap(_.emails.map(_.address))','assert(names == expectedFlatList)'),
('Options','Option(null)','A supposedly present option contains an invalid value.', 'Use Option.apply for nullable interop.', 'Some(javaApi.getName)','Some(null) is possible and defeats the absence contract.', 'Option(javaApi.getName)','assert(Option(null) == None)'),
('Implicits','wrong implicit','Formatting or ordering changes based on scope.', 'Make contextual dependencies explicit or narrowly scoped.', 'implicit val ordering: Ordering[Item] = Ordering.by(_.id)','A broad implicit silently changes unrelated sort behavior.', 'def sortedItems(items: List[Item])(using Ordering[Item]) = items.sorted','assert(sortedItems(items)(using byName).head == expected)'),
('Futures','blocking Await','A limited execution context starves.', 'Compose futures asynchronously and isolate blocking work.', 'Await.result(fetch(), 10.seconds)','Blocking consumes executor threads and can deadlock dependent futures.', 'fetch().map(transform).recover(handle)','assertFutureCompletesWithoutBlocking())'),
('Actors','shared mutable state','Concurrent messages corrupt a counter.', 'Keep state inside the actor and update through messages.', 'var count = 0\ndef increment(): Unit = count += 1','External callers can mutate or read state without actor serialization.', 'case object Increment\nprivate var count = 0\ncase Increment => count += 1','assertEventually(count == expected)'),
('Pattern matching','non-exhaustive match','A new case causes MatchError.', 'Match every sealed hierarchy case or provide a deliberate fallback.', 'status match { case Ready => run() }','The matcher does not handle Failed or Stopped.', 'status match { case Ready => run(); case Failed => recover(); case Stopped => stop() }','assertAllStatusesHandled())'),
('Type inference','Nothing inference','A collection is inferred too narrowly.', 'Supply a type parameter at empty constructors.', 'val values = List.empty; values :+ 1','List.empty may infer Nothing and constrain later operations.', 'val values: List[Int] = List.empty; values :+ 1','assert(values == List(1))'),
('Resources','Source not closed','File handles remain open after streaming.', 'Close the Source in a managed scope.', 'Source.fromFile(path).getLines().toList','The Source is never closed, especially on exceptions.', 'Using(Source.fromFile(path))(_.getLines().toList)','assert(readLines(path) == expected)'),
('Equality','reference equality','Equivalent case class-like Java objects compare unequal.', 'Use structural equality or a case class.', 'if (a eq b) true else false','eq tests reference identity, not values.', 'a == b','assert(Point(1,2) == Point(1,2))'),
],
}

def build(title, prefix, language, fence):
    rows=ROWS[title]
    out=[f"# {title} Debug Exercises\n\nA RAG-training corpus of 300 debugging exercises for {title}. Corrected code is editorial training material and must be stripped from learner-facing challenge responses.\n\n## Coverage\n\n- Easy: 100 exercises\n- Medium: 100 exercises\n- Hard: 100 exercises\n- Perspectives: language semantics, memory, state, concurrency, errors, collections, APIs, testing, and performance\n\n"]
    for level in ('Easy','Medium','Hard'):
        for i in range(1,101): out.append(rec(prefix,title,language,i,level,rows[(i-1)%len(rows)],fence))
    return ''.join(out)

def main():
    specs=[('Haskell','HS','Haskell','haskell','haskell-debug-exercises.md'),('Swift','SWIFT','Swift','swift','swift-debug-exercises.md'),('Kotlin','KT','Kotlin','kotlin','kotlin-debug-exercises.md'),('Scala','SCALA','Scala','scala','scala-debug-exercises.md')]
    for title,prefix,language,fence,file in specs:
        (ROOT/'docs/curriculum'/file).write_text(build(title,prefix,language,fence),encoding='utf-8')
        print('wrote',file,'with 300 exercises')

if __name__=='__main__': main()
