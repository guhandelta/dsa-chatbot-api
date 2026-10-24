# Haskell Debug Exercises

A RAG-training corpus of 300 debugging exercises for Haskell. Corrected code is editorial training material and must be stripped from learner-facing challenge responses.

## Coverage

- Easy: 100 exercises
- Medium: 100 exercises
- Hard: 100 exercises
- Perspectives: language semantics, memory, state, concurrency, errors, collections, APIs, testing, and performance

## HS-E-001: space leak

- Difficulty: Easy
- Language/framework: Haskell / Haskell
- Perspective: Laziness
- Concept: space leak
- Symptom: A long-running fold consumes excessive memory.
- Diagnostic goal: Choose strict accumulation when the result must be evaluated incrementally.

### Buggy code

```haskell
sum = foldl (\a x -> a + x) 0 values
```

### Expected diagnosis

Lazy accumulation builds a chain of thunks instead of forcing each intermediate total.

### Corrected code

```haskell
sum = foldl' (+) 0 values
```

### Regression tests

```haskell
assert (sum [1..100] == 5050)
```

## HS-E-002: unsafe shared state

- Difficulty: Easy
- Language/framework: Haskell / Haskell
- Perspective: Purity
- Concept: unsafe shared state
- Symptom: A helper unexpectedly changes global state.
- Diagnostic goal: Make effects explicit in the type and call boundary.

### Buggy code

```haskell
counter = unsafePerformIO (newIORef 0)
```

### Expected diagnosis

unsafePerformIO hides mutation from the type system and can violate sharing assumptions.

### Corrected code

```haskell
counter :: IO (IORef Int)
counter = newIORef 0
```

### Regression tests

```haskell
-- Test through IO and assert the state transition explicitly.
```

## HS-E-003: partial pattern

- Difficulty: Easy
- Language/framework: Haskell / Haskell
- Perspective: Types
- Concept: partial pattern
- Symptom: An input causes a runtime exception.
- Diagnostic goal: Cover every constructor or make failure explicit.

### Buggy code

```haskell
headName (x:_) = name x
```

### Expected diagnosis

The empty-list pattern is missing, so [] triggers a non-exhaustive match.

### Corrected code

```haskell
headName [] = Nothing
headName (x:_) = Just (name x)
```

### Regression tests

```haskell
assert (headName [] == Nothing)
```

## HS-E-004: unsafe extraction

- Difficulty: Easy
- Language/framework: Haskell / Haskell
- Perspective: Maybe
- Concept: unsafe extraction
- Symptom: Missing configuration crashes startup.
- Diagnostic goal: Use maybe or bind the absence through the computation.

### Buggy code

```haskell
port = read (fromJust (lookup "port" config))
```

### Expected diagnosis

fromJust turns an expected missing-value case into an exception.

### Corrected code

```haskell
port = lookup "port" config >>= readMaybe
```

### Regression tests

```haskell
assert (port [] == Nothing)
```

## HS-E-005: lazy handle

- Difficulty: Easy
- Language/framework: Haskell / Haskell
- Perspective: IO
- Concept: lazy handle
- Symptom: A file is closed before lazy contents are consumed.
- Diagnostic goal: Force contents inside the resource lifetime or stream explicitly.

### Buggy code

```haskell
readLines path = withFile path ReadMode $ \h -> hGetContents h
```

### Expected diagnosis

Lazy hGetContents may defer reads until after withFile closes the handle.

### Corrected code

```haskell
readLines path = withFile path ReadMode $ \h -> hGetContents h >>= \s -> evaluate (length s) >> pure s
```

### Regression tests

```haskell
-- Test reading a complete file after the handle scope.
```

## HS-E-006: wrong bind

- Difficulty: Easy
- Language/framework: Haskell / Haskell
- Perspective: Monads
- Concept: wrong bind
- Symptom: A function receives an IO action instead of its value.
- Diagnostic goal: Use (>>=) or do notation at the effect boundary.

### Buggy code

```haskell
load = fetch >>= pure . parse
```

### Expected diagnosis

This is valid only if parse returns a pure value; mixing nested IO creates the wrong shape.

### Corrected code

```haskell
load = do
  raw <- fetch
  pure (parse raw)
```

### Regression tests

```haskell
assertIO load
```

## HS-E-007: quadratic append

- Difficulty: Easy
- Language/framework: Haskell / Haskell
- Perspective: Lists
- Concept: quadratic append
- Symptom: A list builder becomes slow for large input.
- Diagnostic goal: Prepend and reverse, or use a difference-list structure.

### Buggy code

```haskell
build xs = foldl (\acc x -> acc ++ [f x]) [] xs
```

### Expected diagnosis

Appending to the end copies the accumulated list on every iteration.

### Corrected code

```haskell
build xs = reverse (foldl (\acc x -> f x : acc) [] xs)
```

### Regression tests

```haskell
assert (build [1,2,3] == map f [1,2,3])
```

## HS-E-008: MVar deadlock

- Difficulty: Easy
- Language/framework: Haskell / Haskell
- Perspective: Concurrency
- Concept: MVar deadlock
- Symptom: Two workers wait forever.
- Diagnostic goal: Define lock ownership and always release it on exceptions.

### Buggy code

```haskell
withMVar lock $ \_ -> takeMVar lock
```

### Expected diagnosis

The same thread attempts to take a non-reentrant MVar twice.

### Corrected code

```haskell
withMVar lock $ \_ -> pure ()
```

### Regression tests

```haskell
-- Test completion with a timeout.
```

## HS-E-009: ambiguous instance

- Difficulty: Easy
- Language/framework: Haskell / Haskell
- Perspective: Typeclasses
- Concept: ambiguous instance
- Symptom: Compilation reports overlapping or ambiguous instances.
- Diagnostic goal: Keep instance selection coherent and use newtypes for distinct meanings.

### Buggy code

```haskell
instance Num a => Monoid a where mempty = 0
```

### Expected diagnosis

A broad orphan/overlapping instance conflicts with existing typeclass laws and instances.

### Corrected code

```haskell
newtype Sum a = Sum a
instance Num a => Semigroup (Sum a) where Sum a <> Sum b = Sum (a+b)
```

### Regression tests

```haskell
-- Compile with warnings as errors and test associativity.
```

## HS-E-010: stringly error

- Difficulty: Easy
- Language/framework: Haskell / Haskell
- Perspective: Errors
- Concept: stringly error
- Symptom: Callers cannot distinguish failure cases.
- Diagnostic goal: Use a sum type with stable constructors.

### Buggy code

```haskell
return (Left "not found")
```

### Expected diagnosis

String errors are fragile and force callers to inspect text.

### Corrected code

```haskell
data AppError = NotFound | InvalidInput | StorageError
return (Left NotFound)
```

### Regression tests

```haskell
assert (renderError NotFound == "not found")
```

## HS-E-011: space leak

- Difficulty: Easy
- Language/framework: Haskell / Haskell
- Perspective: Laziness
- Concept: space leak
- Symptom: A long-running fold consumes excessive memory.
- Diagnostic goal: Choose strict accumulation when the result must be evaluated incrementally.

### Buggy code

```haskell
sum = foldl (\a x -> a + x) 0 values
```

### Expected diagnosis

Lazy accumulation builds a chain of thunks instead of forcing each intermediate total.

### Corrected code

```haskell
sum = foldl' (+) 0 values
```

### Regression tests

```haskell
assert (sum [1..100] == 5050)
```

## HS-E-012: unsafe shared state

- Difficulty: Easy
- Language/framework: Haskell / Haskell
- Perspective: Purity
- Concept: unsafe shared state
- Symptom: A helper unexpectedly changes global state.
- Diagnostic goal: Make effects explicit in the type and call boundary.

### Buggy code

```haskell
counter = unsafePerformIO (newIORef 0)
```

### Expected diagnosis

unsafePerformIO hides mutation from the type system and can violate sharing assumptions.

### Corrected code

```haskell
counter :: IO (IORef Int)
counter = newIORef 0
```

### Regression tests

```haskell
-- Test through IO and assert the state transition explicitly.
```

## HS-E-013: partial pattern

- Difficulty: Easy
- Language/framework: Haskell / Haskell
- Perspective: Types
- Concept: partial pattern
- Symptom: An input causes a runtime exception.
- Diagnostic goal: Cover every constructor or make failure explicit.

### Buggy code

```haskell
headName (x:_) = name x
```

### Expected diagnosis

The empty-list pattern is missing, so [] triggers a non-exhaustive match.

### Corrected code

```haskell
headName [] = Nothing
headName (x:_) = Just (name x)
```

### Regression tests

```haskell
assert (headName [] == Nothing)
```

## HS-E-014: unsafe extraction

- Difficulty: Easy
- Language/framework: Haskell / Haskell
- Perspective: Maybe
- Concept: unsafe extraction
- Symptom: Missing configuration crashes startup.
- Diagnostic goal: Use maybe or bind the absence through the computation.

### Buggy code

```haskell
port = read (fromJust (lookup "port" config))
```

### Expected diagnosis

fromJust turns an expected missing-value case into an exception.

### Corrected code

```haskell
port = lookup "port" config >>= readMaybe
```

### Regression tests

```haskell
assert (port [] == Nothing)
```

## HS-E-015: lazy handle

- Difficulty: Easy
- Language/framework: Haskell / Haskell
- Perspective: IO
- Concept: lazy handle
- Symptom: A file is closed before lazy contents are consumed.
- Diagnostic goal: Force contents inside the resource lifetime or stream explicitly.

### Buggy code

```haskell
readLines path = withFile path ReadMode $ \h -> hGetContents h
```

### Expected diagnosis

Lazy hGetContents may defer reads until after withFile closes the handle.

### Corrected code

```haskell
readLines path = withFile path ReadMode $ \h -> hGetContents h >>= \s -> evaluate (length s) >> pure s
```

### Regression tests

```haskell
-- Test reading a complete file after the handle scope.
```

## HS-E-016: wrong bind

- Difficulty: Easy
- Language/framework: Haskell / Haskell
- Perspective: Monads
- Concept: wrong bind
- Symptom: A function receives an IO action instead of its value.
- Diagnostic goal: Use (>>=) or do notation at the effect boundary.

### Buggy code

```haskell
load = fetch >>= pure . parse
```

### Expected diagnosis

This is valid only if parse returns a pure value; mixing nested IO creates the wrong shape.

### Corrected code

```haskell
load = do
  raw <- fetch
  pure (parse raw)
```

### Regression tests

```haskell
assertIO load
```

## HS-E-017: quadratic append

- Difficulty: Easy
- Language/framework: Haskell / Haskell
- Perspective: Lists
- Concept: quadratic append
- Symptom: A list builder becomes slow for large input.
- Diagnostic goal: Prepend and reverse, or use a difference-list structure.

### Buggy code

```haskell
build xs = foldl (\acc x -> acc ++ [f x]) [] xs
```

### Expected diagnosis

Appending to the end copies the accumulated list on every iteration.

### Corrected code

```haskell
build xs = reverse (foldl (\acc x -> f x : acc) [] xs)
```

### Regression tests

```haskell
assert (build [1,2,3] == map f [1,2,3])
```

## HS-E-018: MVar deadlock

- Difficulty: Easy
- Language/framework: Haskell / Haskell
- Perspective: Concurrency
- Concept: MVar deadlock
- Symptom: Two workers wait forever.
- Diagnostic goal: Define lock ownership and always release it on exceptions.

### Buggy code

```haskell
withMVar lock $ \_ -> takeMVar lock
```

### Expected diagnosis

The same thread attempts to take a non-reentrant MVar twice.

### Corrected code

```haskell
withMVar lock $ \_ -> pure ()
```

### Regression tests

```haskell
-- Test completion with a timeout.
```

## HS-E-019: ambiguous instance

- Difficulty: Easy
- Language/framework: Haskell / Haskell
- Perspective: Typeclasses
- Concept: ambiguous instance
- Symptom: Compilation reports overlapping or ambiguous instances.
- Diagnostic goal: Keep instance selection coherent and use newtypes for distinct meanings.

### Buggy code

```haskell
instance Num a => Monoid a where mempty = 0
```

### Expected diagnosis

A broad orphan/overlapping instance conflicts with existing typeclass laws and instances.

### Corrected code

```haskell
newtype Sum a = Sum a
instance Num a => Semigroup (Sum a) where Sum a <> Sum b = Sum (a+b)
```

### Regression tests

```haskell
-- Compile with warnings as errors and test associativity.
```

## HS-E-020: stringly error

- Difficulty: Easy
- Language/framework: Haskell / Haskell
- Perspective: Errors
- Concept: stringly error
- Symptom: Callers cannot distinguish failure cases.
- Diagnostic goal: Use a sum type with stable constructors.

### Buggy code

```haskell
return (Left "not found")
```

### Expected diagnosis

String errors are fragile and force callers to inspect text.

### Corrected code

```haskell
data AppError = NotFound | InvalidInput | StorageError
return (Left NotFound)
```

### Regression tests

```haskell
assert (renderError NotFound == "not found")
```

## HS-E-021: space leak

- Difficulty: Easy
- Language/framework: Haskell / Haskell
- Perspective: Laziness
- Concept: space leak
- Symptom: A long-running fold consumes excessive memory.
- Diagnostic goal: Choose strict accumulation when the result must be evaluated incrementally.

### Buggy code

```haskell
sum = foldl (\a x -> a + x) 0 values
```

### Expected diagnosis

Lazy accumulation builds a chain of thunks instead of forcing each intermediate total.

### Corrected code

```haskell
sum = foldl' (+) 0 values
```

### Regression tests

```haskell
assert (sum [1..100] == 5050)
```

## HS-E-022: unsafe shared state

- Difficulty: Easy
- Language/framework: Haskell / Haskell
- Perspective: Purity
- Concept: unsafe shared state
- Symptom: A helper unexpectedly changes global state.
- Diagnostic goal: Make effects explicit in the type and call boundary.

### Buggy code

```haskell
counter = unsafePerformIO (newIORef 0)
```

### Expected diagnosis

unsafePerformIO hides mutation from the type system and can violate sharing assumptions.

### Corrected code

```haskell
counter :: IO (IORef Int)
counter = newIORef 0
```

### Regression tests

```haskell
-- Test through IO and assert the state transition explicitly.
```

## HS-E-023: partial pattern

- Difficulty: Easy
- Language/framework: Haskell / Haskell
- Perspective: Types
- Concept: partial pattern
- Symptom: An input causes a runtime exception.
- Diagnostic goal: Cover every constructor or make failure explicit.

### Buggy code

```haskell
headName (x:_) = name x
```

### Expected diagnosis

The empty-list pattern is missing, so [] triggers a non-exhaustive match.

### Corrected code

```haskell
headName [] = Nothing
headName (x:_) = Just (name x)
```

### Regression tests

```haskell
assert (headName [] == Nothing)
```

## HS-E-024: unsafe extraction

- Difficulty: Easy
- Language/framework: Haskell / Haskell
- Perspective: Maybe
- Concept: unsafe extraction
- Symptom: Missing configuration crashes startup.
- Diagnostic goal: Use maybe or bind the absence through the computation.

### Buggy code

```haskell
port = read (fromJust (lookup "port" config))
```

### Expected diagnosis

fromJust turns an expected missing-value case into an exception.

### Corrected code

```haskell
port = lookup "port" config >>= readMaybe
```

### Regression tests

```haskell
assert (port [] == Nothing)
```

## HS-E-025: lazy handle

- Difficulty: Easy
- Language/framework: Haskell / Haskell
- Perspective: IO
- Concept: lazy handle
- Symptom: A file is closed before lazy contents are consumed.
- Diagnostic goal: Force contents inside the resource lifetime or stream explicitly.

### Buggy code

```haskell
readLines path = withFile path ReadMode $ \h -> hGetContents h
```

### Expected diagnosis

Lazy hGetContents may defer reads until after withFile closes the handle.

### Corrected code

```haskell
readLines path = withFile path ReadMode $ \h -> hGetContents h >>= \s -> evaluate (length s) >> pure s
```

### Regression tests

```haskell
-- Test reading a complete file after the handle scope.
```

## HS-E-026: wrong bind

- Difficulty: Easy
- Language/framework: Haskell / Haskell
- Perspective: Monads
- Concept: wrong bind
- Symptom: A function receives an IO action instead of its value.
- Diagnostic goal: Use (>>=) or do notation at the effect boundary.

### Buggy code

```haskell
load = fetch >>= pure . parse
```

### Expected diagnosis

This is valid only if parse returns a pure value; mixing nested IO creates the wrong shape.

### Corrected code

```haskell
load = do
  raw <- fetch
  pure (parse raw)
```

### Regression tests

```haskell
assertIO load
```

## HS-E-027: quadratic append

- Difficulty: Easy
- Language/framework: Haskell / Haskell
- Perspective: Lists
- Concept: quadratic append
- Symptom: A list builder becomes slow for large input.
- Diagnostic goal: Prepend and reverse, or use a difference-list structure.

### Buggy code

```haskell
build xs = foldl (\acc x -> acc ++ [f x]) [] xs
```

### Expected diagnosis

Appending to the end copies the accumulated list on every iteration.

### Corrected code

```haskell
build xs = reverse (foldl (\acc x -> f x : acc) [] xs)
```

### Regression tests

```haskell
assert (build [1,2,3] == map f [1,2,3])
```

## HS-E-028: MVar deadlock

- Difficulty: Easy
- Language/framework: Haskell / Haskell
- Perspective: Concurrency
- Concept: MVar deadlock
- Symptom: Two workers wait forever.
- Diagnostic goal: Define lock ownership and always release it on exceptions.

### Buggy code

```haskell
withMVar lock $ \_ -> takeMVar lock
```

### Expected diagnosis

The same thread attempts to take a non-reentrant MVar twice.

### Corrected code

```haskell
withMVar lock $ \_ -> pure ()
```

### Regression tests

```haskell
-- Test completion with a timeout.
```

## HS-E-029: ambiguous instance

- Difficulty: Easy
- Language/framework: Haskell / Haskell
- Perspective: Typeclasses
- Concept: ambiguous instance
- Symptom: Compilation reports overlapping or ambiguous instances.
- Diagnostic goal: Keep instance selection coherent and use newtypes for distinct meanings.

### Buggy code

```haskell
instance Num a => Monoid a where mempty = 0
```

### Expected diagnosis

A broad orphan/overlapping instance conflicts with existing typeclass laws and instances.

### Corrected code

```haskell
newtype Sum a = Sum a
instance Num a => Semigroup (Sum a) where Sum a <> Sum b = Sum (a+b)
```

### Regression tests

```haskell
-- Compile with warnings as errors and test associativity.
```

## HS-E-030: stringly error

- Difficulty: Easy
- Language/framework: Haskell / Haskell
- Perspective: Errors
- Concept: stringly error
- Symptom: Callers cannot distinguish failure cases.
- Diagnostic goal: Use a sum type with stable constructors.

### Buggy code

```haskell
return (Left "not found")
```

### Expected diagnosis

String errors are fragile and force callers to inspect text.

### Corrected code

```haskell
data AppError = NotFound | InvalidInput | StorageError
return (Left NotFound)
```

### Regression tests

```haskell
assert (renderError NotFound == "not found")
```

## HS-E-031: space leak

- Difficulty: Easy
- Language/framework: Haskell / Haskell
- Perspective: Laziness
- Concept: space leak
- Symptom: A long-running fold consumes excessive memory.
- Diagnostic goal: Choose strict accumulation when the result must be evaluated incrementally.

### Buggy code

```haskell
sum = foldl (\a x -> a + x) 0 values
```

### Expected diagnosis

Lazy accumulation builds a chain of thunks instead of forcing each intermediate total.

### Corrected code

```haskell
sum = foldl' (+) 0 values
```

### Regression tests

```haskell
assert (sum [1..100] == 5050)
```

## HS-E-032: unsafe shared state

- Difficulty: Easy
- Language/framework: Haskell / Haskell
- Perspective: Purity
- Concept: unsafe shared state
- Symptom: A helper unexpectedly changes global state.
- Diagnostic goal: Make effects explicit in the type and call boundary.

### Buggy code

```haskell
counter = unsafePerformIO (newIORef 0)
```

### Expected diagnosis

unsafePerformIO hides mutation from the type system and can violate sharing assumptions.

### Corrected code

```haskell
counter :: IO (IORef Int)
counter = newIORef 0
```

### Regression tests

```haskell
-- Test through IO and assert the state transition explicitly.
```

## HS-E-033: partial pattern

- Difficulty: Easy
- Language/framework: Haskell / Haskell
- Perspective: Types
- Concept: partial pattern
- Symptom: An input causes a runtime exception.
- Diagnostic goal: Cover every constructor or make failure explicit.

### Buggy code

```haskell
headName (x:_) = name x
```

### Expected diagnosis

The empty-list pattern is missing, so [] triggers a non-exhaustive match.

### Corrected code

```haskell
headName [] = Nothing
headName (x:_) = Just (name x)
```

### Regression tests

```haskell
assert (headName [] == Nothing)
```

## HS-E-034: unsafe extraction

- Difficulty: Easy
- Language/framework: Haskell / Haskell
- Perspective: Maybe
- Concept: unsafe extraction
- Symptom: Missing configuration crashes startup.
- Diagnostic goal: Use maybe or bind the absence through the computation.

### Buggy code

```haskell
port = read (fromJust (lookup "port" config))
```

### Expected diagnosis

fromJust turns an expected missing-value case into an exception.

### Corrected code

```haskell
port = lookup "port" config >>= readMaybe
```

### Regression tests

```haskell
assert (port [] == Nothing)
```

## HS-E-035: lazy handle

- Difficulty: Easy
- Language/framework: Haskell / Haskell
- Perspective: IO
- Concept: lazy handle
- Symptom: A file is closed before lazy contents are consumed.
- Diagnostic goal: Force contents inside the resource lifetime or stream explicitly.

### Buggy code

```haskell
readLines path = withFile path ReadMode $ \h -> hGetContents h
```

### Expected diagnosis

Lazy hGetContents may defer reads until after withFile closes the handle.

### Corrected code

```haskell
readLines path = withFile path ReadMode $ \h -> hGetContents h >>= \s -> evaluate (length s) >> pure s
```

### Regression tests

```haskell
-- Test reading a complete file after the handle scope.
```

## HS-E-036: wrong bind

- Difficulty: Easy
- Language/framework: Haskell / Haskell
- Perspective: Monads
- Concept: wrong bind
- Symptom: A function receives an IO action instead of its value.
- Diagnostic goal: Use (>>=) or do notation at the effect boundary.

### Buggy code

```haskell
load = fetch >>= pure . parse
```

### Expected diagnosis

This is valid only if parse returns a pure value; mixing nested IO creates the wrong shape.

### Corrected code

```haskell
load = do
  raw <- fetch
  pure (parse raw)
```

### Regression tests

```haskell
assertIO load
```

## HS-E-037: quadratic append

- Difficulty: Easy
- Language/framework: Haskell / Haskell
- Perspective: Lists
- Concept: quadratic append
- Symptom: A list builder becomes slow for large input.
- Diagnostic goal: Prepend and reverse, or use a difference-list structure.

### Buggy code

```haskell
build xs = foldl (\acc x -> acc ++ [f x]) [] xs
```

### Expected diagnosis

Appending to the end copies the accumulated list on every iteration.

### Corrected code

```haskell
build xs = reverse (foldl (\acc x -> f x : acc) [] xs)
```

### Regression tests

```haskell
assert (build [1,2,3] == map f [1,2,3])
```

## HS-E-038: MVar deadlock

- Difficulty: Easy
- Language/framework: Haskell / Haskell
- Perspective: Concurrency
- Concept: MVar deadlock
- Symptom: Two workers wait forever.
- Diagnostic goal: Define lock ownership and always release it on exceptions.

### Buggy code

```haskell
withMVar lock $ \_ -> takeMVar lock
```

### Expected diagnosis

The same thread attempts to take a non-reentrant MVar twice.

### Corrected code

```haskell
withMVar lock $ \_ -> pure ()
```

### Regression tests

```haskell
-- Test completion with a timeout.
```

## HS-E-039: ambiguous instance

- Difficulty: Easy
- Language/framework: Haskell / Haskell
- Perspective: Typeclasses
- Concept: ambiguous instance
- Symptom: Compilation reports overlapping or ambiguous instances.
- Diagnostic goal: Keep instance selection coherent and use newtypes for distinct meanings.

### Buggy code

```haskell
instance Num a => Monoid a where mempty = 0
```

### Expected diagnosis

A broad orphan/overlapping instance conflicts with existing typeclass laws and instances.

### Corrected code

```haskell
newtype Sum a = Sum a
instance Num a => Semigroup (Sum a) where Sum a <> Sum b = Sum (a+b)
```

### Regression tests

```haskell
-- Compile with warnings as errors and test associativity.
```

## HS-E-040: stringly error

- Difficulty: Easy
- Language/framework: Haskell / Haskell
- Perspective: Errors
- Concept: stringly error
- Symptom: Callers cannot distinguish failure cases.
- Diagnostic goal: Use a sum type with stable constructors.

### Buggy code

```haskell
return (Left "not found")
```

### Expected diagnosis

String errors are fragile and force callers to inspect text.

### Corrected code

```haskell
data AppError = NotFound | InvalidInput | StorageError
return (Left NotFound)
```

### Regression tests

```haskell
assert (renderError NotFound == "not found")
```

## HS-E-041: space leak

- Difficulty: Easy
- Language/framework: Haskell / Haskell
- Perspective: Laziness
- Concept: space leak
- Symptom: A long-running fold consumes excessive memory.
- Diagnostic goal: Choose strict accumulation when the result must be evaluated incrementally.

### Buggy code

```haskell
sum = foldl (\a x -> a + x) 0 values
```

### Expected diagnosis

Lazy accumulation builds a chain of thunks instead of forcing each intermediate total.

### Corrected code

```haskell
sum = foldl' (+) 0 values
```

### Regression tests

```haskell
assert (sum [1..100] == 5050)
```

## HS-E-042: unsafe shared state

- Difficulty: Easy
- Language/framework: Haskell / Haskell
- Perspective: Purity
- Concept: unsafe shared state
- Symptom: A helper unexpectedly changes global state.
- Diagnostic goal: Make effects explicit in the type and call boundary.

### Buggy code

```haskell
counter = unsafePerformIO (newIORef 0)
```

### Expected diagnosis

unsafePerformIO hides mutation from the type system and can violate sharing assumptions.

### Corrected code

```haskell
counter :: IO (IORef Int)
counter = newIORef 0
```

### Regression tests

```haskell
-- Test through IO and assert the state transition explicitly.
```

## HS-E-043: partial pattern

- Difficulty: Easy
- Language/framework: Haskell / Haskell
- Perspective: Types
- Concept: partial pattern
- Symptom: An input causes a runtime exception.
- Diagnostic goal: Cover every constructor or make failure explicit.

### Buggy code

```haskell
headName (x:_) = name x
```

### Expected diagnosis

The empty-list pattern is missing, so [] triggers a non-exhaustive match.

### Corrected code

```haskell
headName [] = Nothing
headName (x:_) = Just (name x)
```

### Regression tests

```haskell
assert (headName [] == Nothing)
```

## HS-E-044: unsafe extraction

- Difficulty: Easy
- Language/framework: Haskell / Haskell
- Perspective: Maybe
- Concept: unsafe extraction
- Symptom: Missing configuration crashes startup.
- Diagnostic goal: Use maybe or bind the absence through the computation.

### Buggy code

```haskell
port = read (fromJust (lookup "port" config))
```

### Expected diagnosis

fromJust turns an expected missing-value case into an exception.

### Corrected code

```haskell
port = lookup "port" config >>= readMaybe
```

### Regression tests

```haskell
assert (port [] == Nothing)
```

## HS-E-045: lazy handle

- Difficulty: Easy
- Language/framework: Haskell / Haskell
- Perspective: IO
- Concept: lazy handle
- Symptom: A file is closed before lazy contents are consumed.
- Diagnostic goal: Force contents inside the resource lifetime or stream explicitly.

### Buggy code

```haskell
readLines path = withFile path ReadMode $ \h -> hGetContents h
```

### Expected diagnosis

Lazy hGetContents may defer reads until after withFile closes the handle.

### Corrected code

```haskell
readLines path = withFile path ReadMode $ \h -> hGetContents h >>= \s -> evaluate (length s) >> pure s
```

### Regression tests

```haskell
-- Test reading a complete file after the handle scope.
```

## HS-E-046: wrong bind

- Difficulty: Easy
- Language/framework: Haskell / Haskell
- Perspective: Monads
- Concept: wrong bind
- Symptom: A function receives an IO action instead of its value.
- Diagnostic goal: Use (>>=) or do notation at the effect boundary.

### Buggy code

```haskell
load = fetch >>= pure . parse
```

### Expected diagnosis

This is valid only if parse returns a pure value; mixing nested IO creates the wrong shape.

### Corrected code

```haskell
load = do
  raw <- fetch
  pure (parse raw)
```

### Regression tests

```haskell
assertIO load
```

## HS-E-047: quadratic append

- Difficulty: Easy
- Language/framework: Haskell / Haskell
- Perspective: Lists
- Concept: quadratic append
- Symptom: A list builder becomes slow for large input.
- Diagnostic goal: Prepend and reverse, or use a difference-list structure.

### Buggy code

```haskell
build xs = foldl (\acc x -> acc ++ [f x]) [] xs
```

### Expected diagnosis

Appending to the end copies the accumulated list on every iteration.

### Corrected code

```haskell
build xs = reverse (foldl (\acc x -> f x : acc) [] xs)
```

### Regression tests

```haskell
assert (build [1,2,3] == map f [1,2,3])
```

## HS-E-048: MVar deadlock

- Difficulty: Easy
- Language/framework: Haskell / Haskell
- Perspective: Concurrency
- Concept: MVar deadlock
- Symptom: Two workers wait forever.
- Diagnostic goal: Define lock ownership and always release it on exceptions.

### Buggy code

```haskell
withMVar lock $ \_ -> takeMVar lock
```

### Expected diagnosis

The same thread attempts to take a non-reentrant MVar twice.

### Corrected code

```haskell
withMVar lock $ \_ -> pure ()
```

### Regression tests

```haskell
-- Test completion with a timeout.
```

## HS-E-049: ambiguous instance

- Difficulty: Easy
- Language/framework: Haskell / Haskell
- Perspective: Typeclasses
- Concept: ambiguous instance
- Symptom: Compilation reports overlapping or ambiguous instances.
- Diagnostic goal: Keep instance selection coherent and use newtypes for distinct meanings.

### Buggy code

```haskell
instance Num a => Monoid a where mempty = 0
```

### Expected diagnosis

A broad orphan/overlapping instance conflicts with existing typeclass laws and instances.

### Corrected code

```haskell
newtype Sum a = Sum a
instance Num a => Semigroup (Sum a) where Sum a <> Sum b = Sum (a+b)
```

### Regression tests

```haskell
-- Compile with warnings as errors and test associativity.
```

## HS-E-050: stringly error

- Difficulty: Easy
- Language/framework: Haskell / Haskell
- Perspective: Errors
- Concept: stringly error
- Symptom: Callers cannot distinguish failure cases.
- Diagnostic goal: Use a sum type with stable constructors.

### Buggy code

```haskell
return (Left "not found")
```

### Expected diagnosis

String errors are fragile and force callers to inspect text.

### Corrected code

```haskell
data AppError = NotFound | InvalidInput | StorageError
return (Left NotFound)
```

### Regression tests

```haskell
assert (renderError NotFound == "not found")
```

## HS-E-051: space leak

- Difficulty: Easy
- Language/framework: Haskell / Haskell
- Perspective: Laziness
- Concept: space leak
- Symptom: A long-running fold consumes excessive memory.
- Diagnostic goal: Choose strict accumulation when the result must be evaluated incrementally.

### Buggy code

```haskell
sum = foldl (\a x -> a + x) 0 values
```

### Expected diagnosis

Lazy accumulation builds a chain of thunks instead of forcing each intermediate total.

### Corrected code

```haskell
sum = foldl' (+) 0 values
```

### Regression tests

```haskell
assert (sum [1..100] == 5050)
```

## HS-E-052: unsafe shared state

- Difficulty: Easy
- Language/framework: Haskell / Haskell
- Perspective: Purity
- Concept: unsafe shared state
- Symptom: A helper unexpectedly changes global state.
- Diagnostic goal: Make effects explicit in the type and call boundary.

### Buggy code

```haskell
counter = unsafePerformIO (newIORef 0)
```

### Expected diagnosis

unsafePerformIO hides mutation from the type system and can violate sharing assumptions.

### Corrected code

```haskell
counter :: IO (IORef Int)
counter = newIORef 0
```

### Regression tests

```haskell
-- Test through IO and assert the state transition explicitly.
```

## HS-E-053: partial pattern

- Difficulty: Easy
- Language/framework: Haskell / Haskell
- Perspective: Types
- Concept: partial pattern
- Symptom: An input causes a runtime exception.
- Diagnostic goal: Cover every constructor or make failure explicit.

### Buggy code

```haskell
headName (x:_) = name x
```

### Expected diagnosis

The empty-list pattern is missing, so [] triggers a non-exhaustive match.

### Corrected code

```haskell
headName [] = Nothing
headName (x:_) = Just (name x)
```

### Regression tests

```haskell
assert (headName [] == Nothing)
```

## HS-E-054: unsafe extraction

- Difficulty: Easy
- Language/framework: Haskell / Haskell
- Perspective: Maybe
- Concept: unsafe extraction
- Symptom: Missing configuration crashes startup.
- Diagnostic goal: Use maybe or bind the absence through the computation.

### Buggy code

```haskell
port = read (fromJust (lookup "port" config))
```

### Expected diagnosis

fromJust turns an expected missing-value case into an exception.

### Corrected code

```haskell
port = lookup "port" config >>= readMaybe
```

### Regression tests

```haskell
assert (port [] == Nothing)
```

## HS-E-055: lazy handle

- Difficulty: Easy
- Language/framework: Haskell / Haskell
- Perspective: IO
- Concept: lazy handle
- Symptom: A file is closed before lazy contents are consumed.
- Diagnostic goal: Force contents inside the resource lifetime or stream explicitly.

### Buggy code

```haskell
readLines path = withFile path ReadMode $ \h -> hGetContents h
```

### Expected diagnosis

Lazy hGetContents may defer reads until after withFile closes the handle.

### Corrected code

```haskell
readLines path = withFile path ReadMode $ \h -> hGetContents h >>= \s -> evaluate (length s) >> pure s
```

### Regression tests

```haskell
-- Test reading a complete file after the handle scope.
```

## HS-E-056: wrong bind

- Difficulty: Easy
- Language/framework: Haskell / Haskell
- Perspective: Monads
- Concept: wrong bind
- Symptom: A function receives an IO action instead of its value.
- Diagnostic goal: Use (>>=) or do notation at the effect boundary.

### Buggy code

```haskell
load = fetch >>= pure . parse
```

### Expected diagnosis

This is valid only if parse returns a pure value; mixing nested IO creates the wrong shape.

### Corrected code

```haskell
load = do
  raw <- fetch
  pure (parse raw)
```

### Regression tests

```haskell
assertIO load
```

## HS-E-057: quadratic append

- Difficulty: Easy
- Language/framework: Haskell / Haskell
- Perspective: Lists
- Concept: quadratic append
- Symptom: A list builder becomes slow for large input.
- Diagnostic goal: Prepend and reverse, or use a difference-list structure.

### Buggy code

```haskell
build xs = foldl (\acc x -> acc ++ [f x]) [] xs
```

### Expected diagnosis

Appending to the end copies the accumulated list on every iteration.

### Corrected code

```haskell
build xs = reverse (foldl (\acc x -> f x : acc) [] xs)
```

### Regression tests

```haskell
assert (build [1,2,3] == map f [1,2,3])
```

## HS-E-058: MVar deadlock

- Difficulty: Easy
- Language/framework: Haskell / Haskell
- Perspective: Concurrency
- Concept: MVar deadlock
- Symptom: Two workers wait forever.
- Diagnostic goal: Define lock ownership and always release it on exceptions.

### Buggy code

```haskell
withMVar lock $ \_ -> takeMVar lock
```

### Expected diagnosis

The same thread attempts to take a non-reentrant MVar twice.

### Corrected code

```haskell
withMVar lock $ \_ -> pure ()
```

### Regression tests

```haskell
-- Test completion with a timeout.
```

## HS-E-059: ambiguous instance

- Difficulty: Easy
- Language/framework: Haskell / Haskell
- Perspective: Typeclasses
- Concept: ambiguous instance
- Symptom: Compilation reports overlapping or ambiguous instances.
- Diagnostic goal: Keep instance selection coherent and use newtypes for distinct meanings.

### Buggy code

```haskell
instance Num a => Monoid a where mempty = 0
```

### Expected diagnosis

A broad orphan/overlapping instance conflicts with existing typeclass laws and instances.

### Corrected code

```haskell
newtype Sum a = Sum a
instance Num a => Semigroup (Sum a) where Sum a <> Sum b = Sum (a+b)
```

### Regression tests

```haskell
-- Compile with warnings as errors and test associativity.
```

## HS-E-060: stringly error

- Difficulty: Easy
- Language/framework: Haskell / Haskell
- Perspective: Errors
- Concept: stringly error
- Symptom: Callers cannot distinguish failure cases.
- Diagnostic goal: Use a sum type with stable constructors.

### Buggy code

```haskell
return (Left "not found")
```

### Expected diagnosis

String errors are fragile and force callers to inspect text.

### Corrected code

```haskell
data AppError = NotFound | InvalidInput | StorageError
return (Left NotFound)
```

### Regression tests

```haskell
assert (renderError NotFound == "not found")
```

## HS-E-061: space leak

- Difficulty: Easy
- Language/framework: Haskell / Haskell
- Perspective: Laziness
- Concept: space leak
- Symptom: A long-running fold consumes excessive memory.
- Diagnostic goal: Choose strict accumulation when the result must be evaluated incrementally.

### Buggy code

```haskell
sum = foldl (\a x -> a + x) 0 values
```

### Expected diagnosis

Lazy accumulation builds a chain of thunks instead of forcing each intermediate total.

### Corrected code

```haskell
sum = foldl' (+) 0 values
```

### Regression tests

```haskell
assert (sum [1..100] == 5050)
```

## HS-E-062: unsafe shared state

- Difficulty: Easy
- Language/framework: Haskell / Haskell
- Perspective: Purity
- Concept: unsafe shared state
- Symptom: A helper unexpectedly changes global state.
- Diagnostic goal: Make effects explicit in the type and call boundary.

### Buggy code

```haskell
counter = unsafePerformIO (newIORef 0)
```

### Expected diagnosis

unsafePerformIO hides mutation from the type system and can violate sharing assumptions.

### Corrected code

```haskell
counter :: IO (IORef Int)
counter = newIORef 0
```

### Regression tests

```haskell
-- Test through IO and assert the state transition explicitly.
```

## HS-E-063: partial pattern

- Difficulty: Easy
- Language/framework: Haskell / Haskell
- Perspective: Types
- Concept: partial pattern
- Symptom: An input causes a runtime exception.
- Diagnostic goal: Cover every constructor or make failure explicit.

### Buggy code

```haskell
headName (x:_) = name x
```

### Expected diagnosis

The empty-list pattern is missing, so [] triggers a non-exhaustive match.

### Corrected code

```haskell
headName [] = Nothing
headName (x:_) = Just (name x)
```

### Regression tests

```haskell
assert (headName [] == Nothing)
```

## HS-E-064: unsafe extraction

- Difficulty: Easy
- Language/framework: Haskell / Haskell
- Perspective: Maybe
- Concept: unsafe extraction
- Symptom: Missing configuration crashes startup.
- Diagnostic goal: Use maybe or bind the absence through the computation.

### Buggy code

```haskell
port = read (fromJust (lookup "port" config))
```

### Expected diagnosis

fromJust turns an expected missing-value case into an exception.

### Corrected code

```haskell
port = lookup "port" config >>= readMaybe
```

### Regression tests

```haskell
assert (port [] == Nothing)
```

## HS-E-065: lazy handle

- Difficulty: Easy
- Language/framework: Haskell / Haskell
- Perspective: IO
- Concept: lazy handle
- Symptom: A file is closed before lazy contents are consumed.
- Diagnostic goal: Force contents inside the resource lifetime or stream explicitly.

### Buggy code

```haskell
readLines path = withFile path ReadMode $ \h -> hGetContents h
```

### Expected diagnosis

Lazy hGetContents may defer reads until after withFile closes the handle.

### Corrected code

```haskell
readLines path = withFile path ReadMode $ \h -> hGetContents h >>= \s -> evaluate (length s) >> pure s
```

### Regression tests

```haskell
-- Test reading a complete file after the handle scope.
```

## HS-E-066: wrong bind

- Difficulty: Easy
- Language/framework: Haskell / Haskell
- Perspective: Monads
- Concept: wrong bind
- Symptom: A function receives an IO action instead of its value.
- Diagnostic goal: Use (>>=) or do notation at the effect boundary.

### Buggy code

```haskell
load = fetch >>= pure . parse
```

### Expected diagnosis

This is valid only if parse returns a pure value; mixing nested IO creates the wrong shape.

### Corrected code

```haskell
load = do
  raw <- fetch
  pure (parse raw)
```

### Regression tests

```haskell
assertIO load
```

## HS-E-067: quadratic append

- Difficulty: Easy
- Language/framework: Haskell / Haskell
- Perspective: Lists
- Concept: quadratic append
- Symptom: A list builder becomes slow for large input.
- Diagnostic goal: Prepend and reverse, or use a difference-list structure.

### Buggy code

```haskell
build xs = foldl (\acc x -> acc ++ [f x]) [] xs
```

### Expected diagnosis

Appending to the end copies the accumulated list on every iteration.

### Corrected code

```haskell
build xs = reverse (foldl (\acc x -> f x : acc) [] xs)
```

### Regression tests

```haskell
assert (build [1,2,3] == map f [1,2,3])
```

## HS-E-068: MVar deadlock

- Difficulty: Easy
- Language/framework: Haskell / Haskell
- Perspective: Concurrency
- Concept: MVar deadlock
- Symptom: Two workers wait forever.
- Diagnostic goal: Define lock ownership and always release it on exceptions.

### Buggy code

```haskell
withMVar lock $ \_ -> takeMVar lock
```

### Expected diagnosis

The same thread attempts to take a non-reentrant MVar twice.

### Corrected code

```haskell
withMVar lock $ \_ -> pure ()
```

### Regression tests

```haskell
-- Test completion with a timeout.
```

## HS-E-069: ambiguous instance

- Difficulty: Easy
- Language/framework: Haskell / Haskell
- Perspective: Typeclasses
- Concept: ambiguous instance
- Symptom: Compilation reports overlapping or ambiguous instances.
- Diagnostic goal: Keep instance selection coherent and use newtypes for distinct meanings.

### Buggy code

```haskell
instance Num a => Monoid a where mempty = 0
```

### Expected diagnosis

A broad orphan/overlapping instance conflicts with existing typeclass laws and instances.

### Corrected code

```haskell
newtype Sum a = Sum a
instance Num a => Semigroup (Sum a) where Sum a <> Sum b = Sum (a+b)
```

### Regression tests

```haskell
-- Compile with warnings as errors and test associativity.
```

## HS-E-070: stringly error

- Difficulty: Easy
- Language/framework: Haskell / Haskell
- Perspective: Errors
- Concept: stringly error
- Symptom: Callers cannot distinguish failure cases.
- Diagnostic goal: Use a sum type with stable constructors.

### Buggy code

```haskell
return (Left "not found")
```

### Expected diagnosis

String errors are fragile and force callers to inspect text.

### Corrected code

```haskell
data AppError = NotFound | InvalidInput | StorageError
return (Left NotFound)
```

### Regression tests

```haskell
assert (renderError NotFound == "not found")
```

## HS-E-071: space leak

- Difficulty: Easy
- Language/framework: Haskell / Haskell
- Perspective: Laziness
- Concept: space leak
- Symptom: A long-running fold consumes excessive memory.
- Diagnostic goal: Choose strict accumulation when the result must be evaluated incrementally.

### Buggy code

```haskell
sum = foldl (\a x -> a + x) 0 values
```

### Expected diagnosis

Lazy accumulation builds a chain of thunks instead of forcing each intermediate total.

### Corrected code

```haskell
sum = foldl' (+) 0 values
```

### Regression tests

```haskell
assert (sum [1..100] == 5050)
```

## HS-E-072: unsafe shared state

- Difficulty: Easy
- Language/framework: Haskell / Haskell
- Perspective: Purity
- Concept: unsafe shared state
- Symptom: A helper unexpectedly changes global state.
- Diagnostic goal: Make effects explicit in the type and call boundary.

### Buggy code

```haskell
counter = unsafePerformIO (newIORef 0)
```

### Expected diagnosis

unsafePerformIO hides mutation from the type system and can violate sharing assumptions.

### Corrected code

```haskell
counter :: IO (IORef Int)
counter = newIORef 0
```

### Regression tests

```haskell
-- Test through IO and assert the state transition explicitly.
```

## HS-E-073: partial pattern

- Difficulty: Easy
- Language/framework: Haskell / Haskell
- Perspective: Types
- Concept: partial pattern
- Symptom: An input causes a runtime exception.
- Diagnostic goal: Cover every constructor or make failure explicit.

### Buggy code

```haskell
headName (x:_) = name x
```

### Expected diagnosis

The empty-list pattern is missing, so [] triggers a non-exhaustive match.

### Corrected code

```haskell
headName [] = Nothing
headName (x:_) = Just (name x)
```

### Regression tests

```haskell
assert (headName [] == Nothing)
```

## HS-E-074: unsafe extraction

- Difficulty: Easy
- Language/framework: Haskell / Haskell
- Perspective: Maybe
- Concept: unsafe extraction
- Symptom: Missing configuration crashes startup.
- Diagnostic goal: Use maybe or bind the absence through the computation.

### Buggy code

```haskell
port = read (fromJust (lookup "port" config))
```

### Expected diagnosis

fromJust turns an expected missing-value case into an exception.

### Corrected code

```haskell
port = lookup "port" config >>= readMaybe
```

### Regression tests

```haskell
assert (port [] == Nothing)
```

## HS-E-075: lazy handle

- Difficulty: Easy
- Language/framework: Haskell / Haskell
- Perspective: IO
- Concept: lazy handle
- Symptom: A file is closed before lazy contents are consumed.
- Diagnostic goal: Force contents inside the resource lifetime or stream explicitly.

### Buggy code

```haskell
readLines path = withFile path ReadMode $ \h -> hGetContents h
```

### Expected diagnosis

Lazy hGetContents may defer reads until after withFile closes the handle.

### Corrected code

```haskell
readLines path = withFile path ReadMode $ \h -> hGetContents h >>= \s -> evaluate (length s) >> pure s
```

### Regression tests

```haskell
-- Test reading a complete file after the handle scope.
```

## HS-E-076: wrong bind

- Difficulty: Easy
- Language/framework: Haskell / Haskell
- Perspective: Monads
- Concept: wrong bind
- Symptom: A function receives an IO action instead of its value.
- Diagnostic goal: Use (>>=) or do notation at the effect boundary.

### Buggy code

```haskell
load = fetch >>= pure . parse
```

### Expected diagnosis

This is valid only if parse returns a pure value; mixing nested IO creates the wrong shape.

### Corrected code

```haskell
load = do
  raw <- fetch
  pure (parse raw)
```

### Regression tests

```haskell
assertIO load
```

## HS-E-077: quadratic append

- Difficulty: Easy
- Language/framework: Haskell / Haskell
- Perspective: Lists
- Concept: quadratic append
- Symptom: A list builder becomes slow for large input.
- Diagnostic goal: Prepend and reverse, or use a difference-list structure.

### Buggy code

```haskell
build xs = foldl (\acc x -> acc ++ [f x]) [] xs
```

### Expected diagnosis

Appending to the end copies the accumulated list on every iteration.

### Corrected code

```haskell
build xs = reverse (foldl (\acc x -> f x : acc) [] xs)
```

### Regression tests

```haskell
assert (build [1,2,3] == map f [1,2,3])
```

## HS-E-078: MVar deadlock

- Difficulty: Easy
- Language/framework: Haskell / Haskell
- Perspective: Concurrency
- Concept: MVar deadlock
- Symptom: Two workers wait forever.
- Diagnostic goal: Define lock ownership and always release it on exceptions.

### Buggy code

```haskell
withMVar lock $ \_ -> takeMVar lock
```

### Expected diagnosis

The same thread attempts to take a non-reentrant MVar twice.

### Corrected code

```haskell
withMVar lock $ \_ -> pure ()
```

### Regression tests

```haskell
-- Test completion with a timeout.
```

## HS-E-079: ambiguous instance

- Difficulty: Easy
- Language/framework: Haskell / Haskell
- Perspective: Typeclasses
- Concept: ambiguous instance
- Symptom: Compilation reports overlapping or ambiguous instances.
- Diagnostic goal: Keep instance selection coherent and use newtypes for distinct meanings.

### Buggy code

```haskell
instance Num a => Monoid a where mempty = 0
```

### Expected diagnosis

A broad orphan/overlapping instance conflicts with existing typeclass laws and instances.

### Corrected code

```haskell
newtype Sum a = Sum a
instance Num a => Semigroup (Sum a) where Sum a <> Sum b = Sum (a+b)
```

### Regression tests

```haskell
-- Compile with warnings as errors and test associativity.
```

## HS-E-080: stringly error

- Difficulty: Easy
- Language/framework: Haskell / Haskell
- Perspective: Errors
- Concept: stringly error
- Symptom: Callers cannot distinguish failure cases.
- Diagnostic goal: Use a sum type with stable constructors.

### Buggy code

```haskell
return (Left "not found")
```

### Expected diagnosis

String errors are fragile and force callers to inspect text.

### Corrected code

```haskell
data AppError = NotFound | InvalidInput | StorageError
return (Left NotFound)
```

### Regression tests

```haskell
assert (renderError NotFound == "not found")
```

## HS-E-081: space leak

- Difficulty: Easy
- Language/framework: Haskell / Haskell
- Perspective: Laziness
- Concept: space leak
- Symptom: A long-running fold consumes excessive memory.
- Diagnostic goal: Choose strict accumulation when the result must be evaluated incrementally.

### Buggy code

```haskell
sum = foldl (\a x -> a + x) 0 values
```

### Expected diagnosis

Lazy accumulation builds a chain of thunks instead of forcing each intermediate total.

### Corrected code

```haskell
sum = foldl' (+) 0 values
```

### Regression tests

```haskell
assert (sum [1..100] == 5050)
```

## HS-E-082: unsafe shared state

- Difficulty: Easy
- Language/framework: Haskell / Haskell
- Perspective: Purity
- Concept: unsafe shared state
- Symptom: A helper unexpectedly changes global state.
- Diagnostic goal: Make effects explicit in the type and call boundary.

### Buggy code

```haskell
counter = unsafePerformIO (newIORef 0)
```

### Expected diagnosis

unsafePerformIO hides mutation from the type system and can violate sharing assumptions.

### Corrected code

```haskell
counter :: IO (IORef Int)
counter = newIORef 0
```

### Regression tests

```haskell
-- Test through IO and assert the state transition explicitly.
```

## HS-E-083: partial pattern

- Difficulty: Easy
- Language/framework: Haskell / Haskell
- Perspective: Types
- Concept: partial pattern
- Symptom: An input causes a runtime exception.
- Diagnostic goal: Cover every constructor or make failure explicit.

### Buggy code

```haskell
headName (x:_) = name x
```

### Expected diagnosis

The empty-list pattern is missing, so [] triggers a non-exhaustive match.

### Corrected code

```haskell
headName [] = Nothing
headName (x:_) = Just (name x)
```

### Regression tests

```haskell
assert (headName [] == Nothing)
```

## HS-E-084: unsafe extraction

- Difficulty: Easy
- Language/framework: Haskell / Haskell
- Perspective: Maybe
- Concept: unsafe extraction
- Symptom: Missing configuration crashes startup.
- Diagnostic goal: Use maybe or bind the absence through the computation.

### Buggy code

```haskell
port = read (fromJust (lookup "port" config))
```

### Expected diagnosis

fromJust turns an expected missing-value case into an exception.

### Corrected code

```haskell
port = lookup "port" config >>= readMaybe
```

### Regression tests

```haskell
assert (port [] == Nothing)
```

## HS-E-085: lazy handle

- Difficulty: Easy
- Language/framework: Haskell / Haskell
- Perspective: IO
- Concept: lazy handle
- Symptom: A file is closed before lazy contents are consumed.
- Diagnostic goal: Force contents inside the resource lifetime or stream explicitly.

### Buggy code

```haskell
readLines path = withFile path ReadMode $ \h -> hGetContents h
```

### Expected diagnosis

Lazy hGetContents may defer reads until after withFile closes the handle.

### Corrected code

```haskell
readLines path = withFile path ReadMode $ \h -> hGetContents h >>= \s -> evaluate (length s) >> pure s
```

### Regression tests

```haskell
-- Test reading a complete file after the handle scope.
```

## HS-E-086: wrong bind

- Difficulty: Easy
- Language/framework: Haskell / Haskell
- Perspective: Monads
- Concept: wrong bind
- Symptom: A function receives an IO action instead of its value.
- Diagnostic goal: Use (>>=) or do notation at the effect boundary.

### Buggy code

```haskell
load = fetch >>= pure . parse
```

### Expected diagnosis

This is valid only if parse returns a pure value; mixing nested IO creates the wrong shape.

### Corrected code

```haskell
load = do
  raw <- fetch
  pure (parse raw)
```

### Regression tests

```haskell
assertIO load
```

## HS-E-087: quadratic append

- Difficulty: Easy
- Language/framework: Haskell / Haskell
- Perspective: Lists
- Concept: quadratic append
- Symptom: A list builder becomes slow for large input.
- Diagnostic goal: Prepend and reverse, or use a difference-list structure.

### Buggy code

```haskell
build xs = foldl (\acc x -> acc ++ [f x]) [] xs
```

### Expected diagnosis

Appending to the end copies the accumulated list on every iteration.

### Corrected code

```haskell
build xs = reverse (foldl (\acc x -> f x : acc) [] xs)
```

### Regression tests

```haskell
assert (build [1,2,3] == map f [1,2,3])
```

## HS-E-088: MVar deadlock

- Difficulty: Easy
- Language/framework: Haskell / Haskell
- Perspective: Concurrency
- Concept: MVar deadlock
- Symptom: Two workers wait forever.
- Diagnostic goal: Define lock ownership and always release it on exceptions.

### Buggy code

```haskell
withMVar lock $ \_ -> takeMVar lock
```

### Expected diagnosis

The same thread attempts to take a non-reentrant MVar twice.

### Corrected code

```haskell
withMVar lock $ \_ -> pure ()
```

### Regression tests

```haskell
-- Test completion with a timeout.
```

## HS-E-089: ambiguous instance

- Difficulty: Easy
- Language/framework: Haskell / Haskell
- Perspective: Typeclasses
- Concept: ambiguous instance
- Symptom: Compilation reports overlapping or ambiguous instances.
- Diagnostic goal: Keep instance selection coherent and use newtypes for distinct meanings.

### Buggy code

```haskell
instance Num a => Monoid a where mempty = 0
```

### Expected diagnosis

A broad orphan/overlapping instance conflicts with existing typeclass laws and instances.

### Corrected code

```haskell
newtype Sum a = Sum a
instance Num a => Semigroup (Sum a) where Sum a <> Sum b = Sum (a+b)
```

### Regression tests

```haskell
-- Compile with warnings as errors and test associativity.
```

## HS-E-090: stringly error

- Difficulty: Easy
- Language/framework: Haskell / Haskell
- Perspective: Errors
- Concept: stringly error
- Symptom: Callers cannot distinguish failure cases.
- Diagnostic goal: Use a sum type with stable constructors.

### Buggy code

```haskell
return (Left "not found")
```

### Expected diagnosis

String errors are fragile and force callers to inspect text.

### Corrected code

```haskell
data AppError = NotFound | InvalidInput | StorageError
return (Left NotFound)
```

### Regression tests

```haskell
assert (renderError NotFound == "not found")
```

## HS-E-091: space leak

- Difficulty: Easy
- Language/framework: Haskell / Haskell
- Perspective: Laziness
- Concept: space leak
- Symptom: A long-running fold consumes excessive memory.
- Diagnostic goal: Choose strict accumulation when the result must be evaluated incrementally.

### Buggy code

```haskell
sum = foldl (\a x -> a + x) 0 values
```

### Expected diagnosis

Lazy accumulation builds a chain of thunks instead of forcing each intermediate total.

### Corrected code

```haskell
sum = foldl' (+) 0 values
```

### Regression tests

```haskell
assert (sum [1..100] == 5050)
```

## HS-E-092: unsafe shared state

- Difficulty: Easy
- Language/framework: Haskell / Haskell
- Perspective: Purity
- Concept: unsafe shared state
- Symptom: A helper unexpectedly changes global state.
- Diagnostic goal: Make effects explicit in the type and call boundary.

### Buggy code

```haskell
counter = unsafePerformIO (newIORef 0)
```

### Expected diagnosis

unsafePerformIO hides mutation from the type system and can violate sharing assumptions.

### Corrected code

```haskell
counter :: IO (IORef Int)
counter = newIORef 0
```

### Regression tests

```haskell
-- Test through IO and assert the state transition explicitly.
```

## HS-E-093: partial pattern

- Difficulty: Easy
- Language/framework: Haskell / Haskell
- Perspective: Types
- Concept: partial pattern
- Symptom: An input causes a runtime exception.
- Diagnostic goal: Cover every constructor or make failure explicit.

### Buggy code

```haskell
headName (x:_) = name x
```

### Expected diagnosis

The empty-list pattern is missing, so [] triggers a non-exhaustive match.

### Corrected code

```haskell
headName [] = Nothing
headName (x:_) = Just (name x)
```

### Regression tests

```haskell
assert (headName [] == Nothing)
```

## HS-E-094: unsafe extraction

- Difficulty: Easy
- Language/framework: Haskell / Haskell
- Perspective: Maybe
- Concept: unsafe extraction
- Symptom: Missing configuration crashes startup.
- Diagnostic goal: Use maybe or bind the absence through the computation.

### Buggy code

```haskell
port = read (fromJust (lookup "port" config))
```

### Expected diagnosis

fromJust turns an expected missing-value case into an exception.

### Corrected code

```haskell
port = lookup "port" config >>= readMaybe
```

### Regression tests

```haskell
assert (port [] == Nothing)
```

## HS-E-095: lazy handle

- Difficulty: Easy
- Language/framework: Haskell / Haskell
- Perspective: IO
- Concept: lazy handle
- Symptom: A file is closed before lazy contents are consumed.
- Diagnostic goal: Force contents inside the resource lifetime or stream explicitly.

### Buggy code

```haskell
readLines path = withFile path ReadMode $ \h -> hGetContents h
```

### Expected diagnosis

Lazy hGetContents may defer reads until after withFile closes the handle.

### Corrected code

```haskell
readLines path = withFile path ReadMode $ \h -> hGetContents h >>= \s -> evaluate (length s) >> pure s
```

### Regression tests

```haskell
-- Test reading a complete file after the handle scope.
```

## HS-E-096: wrong bind

- Difficulty: Easy
- Language/framework: Haskell / Haskell
- Perspective: Monads
- Concept: wrong bind
- Symptom: A function receives an IO action instead of its value.
- Diagnostic goal: Use (>>=) or do notation at the effect boundary.

### Buggy code

```haskell
load = fetch >>= pure . parse
```

### Expected diagnosis

This is valid only if parse returns a pure value; mixing nested IO creates the wrong shape.

### Corrected code

```haskell
load = do
  raw <- fetch
  pure (parse raw)
```

### Regression tests

```haskell
assertIO load
```

## HS-E-097: quadratic append

- Difficulty: Easy
- Language/framework: Haskell / Haskell
- Perspective: Lists
- Concept: quadratic append
- Symptom: A list builder becomes slow for large input.
- Diagnostic goal: Prepend and reverse, or use a difference-list structure.

### Buggy code

```haskell
build xs = foldl (\acc x -> acc ++ [f x]) [] xs
```

### Expected diagnosis

Appending to the end copies the accumulated list on every iteration.

### Corrected code

```haskell
build xs = reverse (foldl (\acc x -> f x : acc) [] xs)
```

### Regression tests

```haskell
assert (build [1,2,3] == map f [1,2,3])
```

## HS-E-098: MVar deadlock

- Difficulty: Easy
- Language/framework: Haskell / Haskell
- Perspective: Concurrency
- Concept: MVar deadlock
- Symptom: Two workers wait forever.
- Diagnostic goal: Define lock ownership and always release it on exceptions.

### Buggy code

```haskell
withMVar lock $ \_ -> takeMVar lock
```

### Expected diagnosis

The same thread attempts to take a non-reentrant MVar twice.

### Corrected code

```haskell
withMVar lock $ \_ -> pure ()
```

### Regression tests

```haskell
-- Test completion with a timeout.
```

## HS-E-099: ambiguous instance

- Difficulty: Easy
- Language/framework: Haskell / Haskell
- Perspective: Typeclasses
- Concept: ambiguous instance
- Symptom: Compilation reports overlapping or ambiguous instances.
- Diagnostic goal: Keep instance selection coherent and use newtypes for distinct meanings.

### Buggy code

```haskell
instance Num a => Monoid a where mempty = 0
```

### Expected diagnosis

A broad orphan/overlapping instance conflicts with existing typeclass laws and instances.

### Corrected code

```haskell
newtype Sum a = Sum a
instance Num a => Semigroup (Sum a) where Sum a <> Sum b = Sum (a+b)
```

### Regression tests

```haskell
-- Compile with warnings as errors and test associativity.
```

## HS-E-100: stringly error

- Difficulty: Easy
- Language/framework: Haskell / Haskell
- Perspective: Errors
- Concept: stringly error
- Symptom: Callers cannot distinguish failure cases.
- Diagnostic goal: Use a sum type with stable constructors.

### Buggy code

```haskell
return (Left "not found")
```

### Expected diagnosis

String errors are fragile and force callers to inspect text.

### Corrected code

```haskell
data AppError = NotFound | InvalidInput | StorageError
return (Left NotFound)
```

### Regression tests

```haskell
assert (renderError NotFound == "not found")
```

## HS-M-001: space leak

- Difficulty: Medium
- Language/framework: Haskell / Haskell
- Perspective: Laziness
- Concept: space leak
- Symptom: A long-running fold consumes excessive memory.
- Diagnostic goal: Choose strict accumulation when the result must be evaluated incrementally.

### Buggy code

```haskell
sum = foldl (\a x -> a + x) 0 values
```

### Expected diagnosis

Lazy accumulation builds a chain of thunks instead of forcing each intermediate total.

### Corrected code

```haskell
sum = foldl' (+) 0 values
```

### Regression tests

```haskell
assert (sum [1..100] == 5050)
```

## HS-M-002: unsafe shared state

- Difficulty: Medium
- Language/framework: Haskell / Haskell
- Perspective: Purity
- Concept: unsafe shared state
- Symptom: A helper unexpectedly changes global state.
- Diagnostic goal: Make effects explicit in the type and call boundary.

### Buggy code

```haskell
counter = unsafePerformIO (newIORef 0)
```

### Expected diagnosis

unsafePerformIO hides mutation from the type system and can violate sharing assumptions.

### Corrected code

```haskell
counter :: IO (IORef Int)
counter = newIORef 0
```

### Regression tests

```haskell
-- Test through IO and assert the state transition explicitly.
```

## HS-M-003: partial pattern

- Difficulty: Medium
- Language/framework: Haskell / Haskell
- Perspective: Types
- Concept: partial pattern
- Symptom: An input causes a runtime exception.
- Diagnostic goal: Cover every constructor or make failure explicit.

### Buggy code

```haskell
headName (x:_) = name x
```

### Expected diagnosis

The empty-list pattern is missing, so [] triggers a non-exhaustive match.

### Corrected code

```haskell
headName [] = Nothing
headName (x:_) = Just (name x)
```

### Regression tests

```haskell
assert (headName [] == Nothing)
```

## HS-M-004: unsafe extraction

- Difficulty: Medium
- Language/framework: Haskell / Haskell
- Perspective: Maybe
- Concept: unsafe extraction
- Symptom: Missing configuration crashes startup.
- Diagnostic goal: Use maybe or bind the absence through the computation.

### Buggy code

```haskell
port = read (fromJust (lookup "port" config))
```

### Expected diagnosis

fromJust turns an expected missing-value case into an exception.

### Corrected code

```haskell
port = lookup "port" config >>= readMaybe
```

### Regression tests

```haskell
assert (port [] == Nothing)
```

## HS-M-005: lazy handle

- Difficulty: Medium
- Language/framework: Haskell / Haskell
- Perspective: IO
- Concept: lazy handle
- Symptom: A file is closed before lazy contents are consumed.
- Diagnostic goal: Force contents inside the resource lifetime or stream explicitly.

### Buggy code

```haskell
readLines path = withFile path ReadMode $ \h -> hGetContents h
```

### Expected diagnosis

Lazy hGetContents may defer reads until after withFile closes the handle.

### Corrected code

```haskell
readLines path = withFile path ReadMode $ \h -> hGetContents h >>= \s -> evaluate (length s) >> pure s
```

### Regression tests

```haskell
-- Test reading a complete file after the handle scope.
```

## HS-M-006: wrong bind

- Difficulty: Medium
- Language/framework: Haskell / Haskell
- Perspective: Monads
- Concept: wrong bind
- Symptom: A function receives an IO action instead of its value.
- Diagnostic goal: Use (>>=) or do notation at the effect boundary.

### Buggy code

```haskell
load = fetch >>= pure . parse
```

### Expected diagnosis

This is valid only if parse returns a pure value; mixing nested IO creates the wrong shape.

### Corrected code

```haskell
load = do
  raw <- fetch
  pure (parse raw)
```

### Regression tests

```haskell
assertIO load
```

## HS-M-007: quadratic append

- Difficulty: Medium
- Language/framework: Haskell / Haskell
- Perspective: Lists
- Concept: quadratic append
- Symptom: A list builder becomes slow for large input.
- Diagnostic goal: Prepend and reverse, or use a difference-list structure.

### Buggy code

```haskell
build xs = foldl (\acc x -> acc ++ [f x]) [] xs
```

### Expected diagnosis

Appending to the end copies the accumulated list on every iteration.

### Corrected code

```haskell
build xs = reverse (foldl (\acc x -> f x : acc) [] xs)
```

### Regression tests

```haskell
assert (build [1,2,3] == map f [1,2,3])
```

## HS-M-008: MVar deadlock

- Difficulty: Medium
- Language/framework: Haskell / Haskell
- Perspective: Concurrency
- Concept: MVar deadlock
- Symptom: Two workers wait forever.
- Diagnostic goal: Define lock ownership and always release it on exceptions.

### Buggy code

```haskell
withMVar lock $ \_ -> takeMVar lock
```

### Expected diagnosis

The same thread attempts to take a non-reentrant MVar twice.

### Corrected code

```haskell
withMVar lock $ \_ -> pure ()
```

### Regression tests

```haskell
-- Test completion with a timeout.
```

## HS-M-009: ambiguous instance

- Difficulty: Medium
- Language/framework: Haskell / Haskell
- Perspective: Typeclasses
- Concept: ambiguous instance
- Symptom: Compilation reports overlapping or ambiguous instances.
- Diagnostic goal: Keep instance selection coherent and use newtypes for distinct meanings.

### Buggy code

```haskell
instance Num a => Monoid a where mempty = 0
```

### Expected diagnosis

A broad orphan/overlapping instance conflicts with existing typeclass laws and instances.

### Corrected code

```haskell
newtype Sum a = Sum a
instance Num a => Semigroup (Sum a) where Sum a <> Sum b = Sum (a+b)
```

### Regression tests

```haskell
-- Compile with warnings as errors and test associativity.
```

## HS-M-010: stringly error

- Difficulty: Medium
- Language/framework: Haskell / Haskell
- Perspective: Errors
- Concept: stringly error
- Symptom: Callers cannot distinguish failure cases.
- Diagnostic goal: Use a sum type with stable constructors.

### Buggy code

```haskell
return (Left "not found")
```

### Expected diagnosis

String errors are fragile and force callers to inspect text.

### Corrected code

```haskell
data AppError = NotFound | InvalidInput | StorageError
return (Left NotFound)
```

### Regression tests

```haskell
assert (renderError NotFound == "not found")
```

## HS-M-011: space leak

- Difficulty: Medium
- Language/framework: Haskell / Haskell
- Perspective: Laziness
- Concept: space leak
- Symptom: A long-running fold consumes excessive memory.
- Diagnostic goal: Choose strict accumulation when the result must be evaluated incrementally.

### Buggy code

```haskell
sum = foldl (\a x -> a + x) 0 values
```

### Expected diagnosis

Lazy accumulation builds a chain of thunks instead of forcing each intermediate total.

### Corrected code

```haskell
sum = foldl' (+) 0 values
```

### Regression tests

```haskell
assert (sum [1..100] == 5050)
```

## HS-M-012: unsafe shared state

- Difficulty: Medium
- Language/framework: Haskell / Haskell
- Perspective: Purity
- Concept: unsafe shared state
- Symptom: A helper unexpectedly changes global state.
- Diagnostic goal: Make effects explicit in the type and call boundary.

### Buggy code

```haskell
counter = unsafePerformIO (newIORef 0)
```

### Expected diagnosis

unsafePerformIO hides mutation from the type system and can violate sharing assumptions.

### Corrected code

```haskell
counter :: IO (IORef Int)
counter = newIORef 0
```

### Regression tests

```haskell
-- Test through IO and assert the state transition explicitly.
```

## HS-M-013: partial pattern

- Difficulty: Medium
- Language/framework: Haskell / Haskell
- Perspective: Types
- Concept: partial pattern
- Symptom: An input causes a runtime exception.
- Diagnostic goal: Cover every constructor or make failure explicit.

### Buggy code

```haskell
headName (x:_) = name x
```

### Expected diagnosis

The empty-list pattern is missing, so [] triggers a non-exhaustive match.

### Corrected code

```haskell
headName [] = Nothing
headName (x:_) = Just (name x)
```

### Regression tests

```haskell
assert (headName [] == Nothing)
```

## HS-M-014: unsafe extraction

- Difficulty: Medium
- Language/framework: Haskell / Haskell
- Perspective: Maybe
- Concept: unsafe extraction
- Symptom: Missing configuration crashes startup.
- Diagnostic goal: Use maybe or bind the absence through the computation.

### Buggy code

```haskell
port = read (fromJust (lookup "port" config))
```

### Expected diagnosis

fromJust turns an expected missing-value case into an exception.

### Corrected code

```haskell
port = lookup "port" config >>= readMaybe
```

### Regression tests

```haskell
assert (port [] == Nothing)
```

## HS-M-015: lazy handle

- Difficulty: Medium
- Language/framework: Haskell / Haskell
- Perspective: IO
- Concept: lazy handle
- Symptom: A file is closed before lazy contents are consumed.
- Diagnostic goal: Force contents inside the resource lifetime or stream explicitly.

### Buggy code

```haskell
readLines path = withFile path ReadMode $ \h -> hGetContents h
```

### Expected diagnosis

Lazy hGetContents may defer reads until after withFile closes the handle.

### Corrected code

```haskell
readLines path = withFile path ReadMode $ \h -> hGetContents h >>= \s -> evaluate (length s) >> pure s
```

### Regression tests

```haskell
-- Test reading a complete file after the handle scope.
```

## HS-M-016: wrong bind

- Difficulty: Medium
- Language/framework: Haskell / Haskell
- Perspective: Monads
- Concept: wrong bind
- Symptom: A function receives an IO action instead of its value.
- Diagnostic goal: Use (>>=) or do notation at the effect boundary.

### Buggy code

```haskell
load = fetch >>= pure . parse
```

### Expected diagnosis

This is valid only if parse returns a pure value; mixing nested IO creates the wrong shape.

### Corrected code

```haskell
load = do
  raw <- fetch
  pure (parse raw)
```

### Regression tests

```haskell
assertIO load
```

## HS-M-017: quadratic append

- Difficulty: Medium
- Language/framework: Haskell / Haskell
- Perspective: Lists
- Concept: quadratic append
- Symptom: A list builder becomes slow for large input.
- Diagnostic goal: Prepend and reverse, or use a difference-list structure.

### Buggy code

```haskell
build xs = foldl (\acc x -> acc ++ [f x]) [] xs
```

### Expected diagnosis

Appending to the end copies the accumulated list on every iteration.

### Corrected code

```haskell
build xs = reverse (foldl (\acc x -> f x : acc) [] xs)
```

### Regression tests

```haskell
assert (build [1,2,3] == map f [1,2,3])
```

## HS-M-018: MVar deadlock

- Difficulty: Medium
- Language/framework: Haskell / Haskell
- Perspective: Concurrency
- Concept: MVar deadlock
- Symptom: Two workers wait forever.
- Diagnostic goal: Define lock ownership and always release it on exceptions.

### Buggy code

```haskell
withMVar lock $ \_ -> takeMVar lock
```

### Expected diagnosis

The same thread attempts to take a non-reentrant MVar twice.

### Corrected code

```haskell
withMVar lock $ \_ -> pure ()
```

### Regression tests

```haskell
-- Test completion with a timeout.
```

## HS-M-019: ambiguous instance

- Difficulty: Medium
- Language/framework: Haskell / Haskell
- Perspective: Typeclasses
- Concept: ambiguous instance
- Symptom: Compilation reports overlapping or ambiguous instances.
- Diagnostic goal: Keep instance selection coherent and use newtypes for distinct meanings.

### Buggy code

```haskell
instance Num a => Monoid a where mempty = 0
```

### Expected diagnosis

A broad orphan/overlapping instance conflicts with existing typeclass laws and instances.

### Corrected code

```haskell
newtype Sum a = Sum a
instance Num a => Semigroup (Sum a) where Sum a <> Sum b = Sum (a+b)
```

### Regression tests

```haskell
-- Compile with warnings as errors and test associativity.
```

## HS-M-020: stringly error

- Difficulty: Medium
- Language/framework: Haskell / Haskell
- Perspective: Errors
- Concept: stringly error
- Symptom: Callers cannot distinguish failure cases.
- Diagnostic goal: Use a sum type with stable constructors.

### Buggy code

```haskell
return (Left "not found")
```

### Expected diagnosis

String errors are fragile and force callers to inspect text.

### Corrected code

```haskell
data AppError = NotFound | InvalidInput | StorageError
return (Left NotFound)
```

### Regression tests

```haskell
assert (renderError NotFound == "not found")
```

## HS-M-021: space leak

- Difficulty: Medium
- Language/framework: Haskell / Haskell
- Perspective: Laziness
- Concept: space leak
- Symptom: A long-running fold consumes excessive memory.
- Diagnostic goal: Choose strict accumulation when the result must be evaluated incrementally.

### Buggy code

```haskell
sum = foldl (\a x -> a + x) 0 values
```

### Expected diagnosis

Lazy accumulation builds a chain of thunks instead of forcing each intermediate total.

### Corrected code

```haskell
sum = foldl' (+) 0 values
```

### Regression tests

```haskell
assert (sum [1..100] == 5050)
```

## HS-M-022: unsafe shared state

- Difficulty: Medium
- Language/framework: Haskell / Haskell
- Perspective: Purity
- Concept: unsafe shared state
- Symptom: A helper unexpectedly changes global state.
- Diagnostic goal: Make effects explicit in the type and call boundary.

### Buggy code

```haskell
counter = unsafePerformIO (newIORef 0)
```

### Expected diagnosis

unsafePerformIO hides mutation from the type system and can violate sharing assumptions.

### Corrected code

```haskell
counter :: IO (IORef Int)
counter = newIORef 0
```

### Regression tests

```haskell
-- Test through IO and assert the state transition explicitly.
```

## HS-M-023: partial pattern

- Difficulty: Medium
- Language/framework: Haskell / Haskell
- Perspective: Types
- Concept: partial pattern
- Symptom: An input causes a runtime exception.
- Diagnostic goal: Cover every constructor or make failure explicit.

### Buggy code

```haskell
headName (x:_) = name x
```

### Expected diagnosis

The empty-list pattern is missing, so [] triggers a non-exhaustive match.

### Corrected code

```haskell
headName [] = Nothing
headName (x:_) = Just (name x)
```

### Regression tests

```haskell
assert (headName [] == Nothing)
```

## HS-M-024: unsafe extraction

- Difficulty: Medium
- Language/framework: Haskell / Haskell
- Perspective: Maybe
- Concept: unsafe extraction
- Symptom: Missing configuration crashes startup.
- Diagnostic goal: Use maybe or bind the absence through the computation.

### Buggy code

```haskell
port = read (fromJust (lookup "port" config))
```

### Expected diagnosis

fromJust turns an expected missing-value case into an exception.

### Corrected code

```haskell
port = lookup "port" config >>= readMaybe
```

### Regression tests

```haskell
assert (port [] == Nothing)
```

## HS-M-025: lazy handle

- Difficulty: Medium
- Language/framework: Haskell / Haskell
- Perspective: IO
- Concept: lazy handle
- Symptom: A file is closed before lazy contents are consumed.
- Diagnostic goal: Force contents inside the resource lifetime or stream explicitly.

### Buggy code

```haskell
readLines path = withFile path ReadMode $ \h -> hGetContents h
```

### Expected diagnosis

Lazy hGetContents may defer reads until after withFile closes the handle.

### Corrected code

```haskell
readLines path = withFile path ReadMode $ \h -> hGetContents h >>= \s -> evaluate (length s) >> pure s
```

### Regression tests

```haskell
-- Test reading a complete file after the handle scope.
```

## HS-M-026: wrong bind

- Difficulty: Medium
- Language/framework: Haskell / Haskell
- Perspective: Monads
- Concept: wrong bind
- Symptom: A function receives an IO action instead of its value.
- Diagnostic goal: Use (>>=) or do notation at the effect boundary.

### Buggy code

```haskell
load = fetch >>= pure . parse
```

### Expected diagnosis

This is valid only if parse returns a pure value; mixing nested IO creates the wrong shape.

### Corrected code

```haskell
load = do
  raw <- fetch
  pure (parse raw)
```

### Regression tests

```haskell
assertIO load
```

## HS-M-027: quadratic append

- Difficulty: Medium
- Language/framework: Haskell / Haskell
- Perspective: Lists
- Concept: quadratic append
- Symptom: A list builder becomes slow for large input.
- Diagnostic goal: Prepend and reverse, or use a difference-list structure.

### Buggy code

```haskell
build xs = foldl (\acc x -> acc ++ [f x]) [] xs
```

### Expected diagnosis

Appending to the end copies the accumulated list on every iteration.

### Corrected code

```haskell
build xs = reverse (foldl (\acc x -> f x : acc) [] xs)
```

### Regression tests

```haskell
assert (build [1,2,3] == map f [1,2,3])
```

## HS-M-028: MVar deadlock

- Difficulty: Medium
- Language/framework: Haskell / Haskell
- Perspective: Concurrency
- Concept: MVar deadlock
- Symptom: Two workers wait forever.
- Diagnostic goal: Define lock ownership and always release it on exceptions.

### Buggy code

```haskell
withMVar lock $ \_ -> takeMVar lock
```

### Expected diagnosis

The same thread attempts to take a non-reentrant MVar twice.

### Corrected code

```haskell
withMVar lock $ \_ -> pure ()
```

### Regression tests

```haskell
-- Test completion with a timeout.
```

## HS-M-029: ambiguous instance

- Difficulty: Medium
- Language/framework: Haskell / Haskell
- Perspective: Typeclasses
- Concept: ambiguous instance
- Symptom: Compilation reports overlapping or ambiguous instances.
- Diagnostic goal: Keep instance selection coherent and use newtypes for distinct meanings.

### Buggy code

```haskell
instance Num a => Monoid a where mempty = 0
```

### Expected diagnosis

A broad orphan/overlapping instance conflicts with existing typeclass laws and instances.

### Corrected code

```haskell
newtype Sum a = Sum a
instance Num a => Semigroup (Sum a) where Sum a <> Sum b = Sum (a+b)
```

### Regression tests

```haskell
-- Compile with warnings as errors and test associativity.
```

## HS-M-030: stringly error

- Difficulty: Medium
- Language/framework: Haskell / Haskell
- Perspective: Errors
- Concept: stringly error
- Symptom: Callers cannot distinguish failure cases.
- Diagnostic goal: Use a sum type with stable constructors.

### Buggy code

```haskell
return (Left "not found")
```

### Expected diagnosis

String errors are fragile and force callers to inspect text.

### Corrected code

```haskell
data AppError = NotFound | InvalidInput | StorageError
return (Left NotFound)
```

### Regression tests

```haskell
assert (renderError NotFound == "not found")
```

## HS-M-031: space leak

- Difficulty: Medium
- Language/framework: Haskell / Haskell
- Perspective: Laziness
- Concept: space leak
- Symptom: A long-running fold consumes excessive memory.
- Diagnostic goal: Choose strict accumulation when the result must be evaluated incrementally.

### Buggy code

```haskell
sum = foldl (\a x -> a + x) 0 values
```

### Expected diagnosis

Lazy accumulation builds a chain of thunks instead of forcing each intermediate total.

### Corrected code

```haskell
sum = foldl' (+) 0 values
```

### Regression tests

```haskell
assert (sum [1..100] == 5050)
```

## HS-M-032: unsafe shared state

- Difficulty: Medium
- Language/framework: Haskell / Haskell
- Perspective: Purity
- Concept: unsafe shared state
- Symptom: A helper unexpectedly changes global state.
- Diagnostic goal: Make effects explicit in the type and call boundary.

### Buggy code

```haskell
counter = unsafePerformIO (newIORef 0)
```

### Expected diagnosis

unsafePerformIO hides mutation from the type system and can violate sharing assumptions.

### Corrected code

```haskell
counter :: IO (IORef Int)
counter = newIORef 0
```

### Regression tests

```haskell
-- Test through IO and assert the state transition explicitly.
```

## HS-M-033: partial pattern

- Difficulty: Medium
- Language/framework: Haskell / Haskell
- Perspective: Types
- Concept: partial pattern
- Symptom: An input causes a runtime exception.
- Diagnostic goal: Cover every constructor or make failure explicit.

### Buggy code

```haskell
headName (x:_) = name x
```

### Expected diagnosis

The empty-list pattern is missing, so [] triggers a non-exhaustive match.

### Corrected code

```haskell
headName [] = Nothing
headName (x:_) = Just (name x)
```

### Regression tests

```haskell
assert (headName [] == Nothing)
```

## HS-M-034: unsafe extraction

- Difficulty: Medium
- Language/framework: Haskell / Haskell
- Perspective: Maybe
- Concept: unsafe extraction
- Symptom: Missing configuration crashes startup.
- Diagnostic goal: Use maybe or bind the absence through the computation.

### Buggy code

```haskell
port = read (fromJust (lookup "port" config))
```

### Expected diagnosis

fromJust turns an expected missing-value case into an exception.

### Corrected code

```haskell
port = lookup "port" config >>= readMaybe
```

### Regression tests

```haskell
assert (port [] == Nothing)
```

## HS-M-035: lazy handle

- Difficulty: Medium
- Language/framework: Haskell / Haskell
- Perspective: IO
- Concept: lazy handle
- Symptom: A file is closed before lazy contents are consumed.
- Diagnostic goal: Force contents inside the resource lifetime or stream explicitly.

### Buggy code

```haskell
readLines path = withFile path ReadMode $ \h -> hGetContents h
```

### Expected diagnosis

Lazy hGetContents may defer reads until after withFile closes the handle.

### Corrected code

```haskell
readLines path = withFile path ReadMode $ \h -> hGetContents h >>= \s -> evaluate (length s) >> pure s
```

### Regression tests

```haskell
-- Test reading a complete file after the handle scope.
```

## HS-M-036: wrong bind

- Difficulty: Medium
- Language/framework: Haskell / Haskell
- Perspective: Monads
- Concept: wrong bind
- Symptom: A function receives an IO action instead of its value.
- Diagnostic goal: Use (>>=) or do notation at the effect boundary.

### Buggy code

```haskell
load = fetch >>= pure . parse
```

### Expected diagnosis

This is valid only if parse returns a pure value; mixing nested IO creates the wrong shape.

### Corrected code

```haskell
load = do
  raw <- fetch
  pure (parse raw)
```

### Regression tests

```haskell
assertIO load
```

## HS-M-037: quadratic append

- Difficulty: Medium
- Language/framework: Haskell / Haskell
- Perspective: Lists
- Concept: quadratic append
- Symptom: A list builder becomes slow for large input.
- Diagnostic goal: Prepend and reverse, or use a difference-list structure.

### Buggy code

```haskell
build xs = foldl (\acc x -> acc ++ [f x]) [] xs
```

### Expected diagnosis

Appending to the end copies the accumulated list on every iteration.

### Corrected code

```haskell
build xs = reverse (foldl (\acc x -> f x : acc) [] xs)
```

### Regression tests

```haskell
assert (build [1,2,3] == map f [1,2,3])
```

## HS-M-038: MVar deadlock

- Difficulty: Medium
- Language/framework: Haskell / Haskell
- Perspective: Concurrency
- Concept: MVar deadlock
- Symptom: Two workers wait forever.
- Diagnostic goal: Define lock ownership and always release it on exceptions.

### Buggy code

```haskell
withMVar lock $ \_ -> takeMVar lock
```

### Expected diagnosis

The same thread attempts to take a non-reentrant MVar twice.

### Corrected code

```haskell
withMVar lock $ \_ -> pure ()
```

### Regression tests

```haskell
-- Test completion with a timeout.
```

## HS-M-039: ambiguous instance

- Difficulty: Medium
- Language/framework: Haskell / Haskell
- Perspective: Typeclasses
- Concept: ambiguous instance
- Symptom: Compilation reports overlapping or ambiguous instances.
- Diagnostic goal: Keep instance selection coherent and use newtypes for distinct meanings.

### Buggy code

```haskell
instance Num a => Monoid a where mempty = 0
```

### Expected diagnosis

A broad orphan/overlapping instance conflicts with existing typeclass laws and instances.

### Corrected code

```haskell
newtype Sum a = Sum a
instance Num a => Semigroup (Sum a) where Sum a <> Sum b = Sum (a+b)
```

### Regression tests

```haskell
-- Compile with warnings as errors and test associativity.
```

## HS-M-040: stringly error

- Difficulty: Medium
- Language/framework: Haskell / Haskell
- Perspective: Errors
- Concept: stringly error
- Symptom: Callers cannot distinguish failure cases.
- Diagnostic goal: Use a sum type with stable constructors.

### Buggy code

```haskell
return (Left "not found")
```

### Expected diagnosis

String errors are fragile and force callers to inspect text.

### Corrected code

```haskell
data AppError = NotFound | InvalidInput | StorageError
return (Left NotFound)
```

### Regression tests

```haskell
assert (renderError NotFound == "not found")
```

## HS-M-041: space leak

- Difficulty: Medium
- Language/framework: Haskell / Haskell
- Perspective: Laziness
- Concept: space leak
- Symptom: A long-running fold consumes excessive memory.
- Diagnostic goal: Choose strict accumulation when the result must be evaluated incrementally.

### Buggy code

```haskell
sum = foldl (\a x -> a + x) 0 values
```

### Expected diagnosis

Lazy accumulation builds a chain of thunks instead of forcing each intermediate total.

### Corrected code

```haskell
sum = foldl' (+) 0 values
```

### Regression tests

```haskell
assert (sum [1..100] == 5050)
```

## HS-M-042: unsafe shared state

- Difficulty: Medium
- Language/framework: Haskell / Haskell
- Perspective: Purity
- Concept: unsafe shared state
- Symptom: A helper unexpectedly changes global state.
- Diagnostic goal: Make effects explicit in the type and call boundary.

### Buggy code

```haskell
counter = unsafePerformIO (newIORef 0)
```

### Expected diagnosis

unsafePerformIO hides mutation from the type system and can violate sharing assumptions.

### Corrected code

```haskell
counter :: IO (IORef Int)
counter = newIORef 0
```

### Regression tests

```haskell
-- Test through IO and assert the state transition explicitly.
```

## HS-M-043: partial pattern

- Difficulty: Medium
- Language/framework: Haskell / Haskell
- Perspective: Types
- Concept: partial pattern
- Symptom: An input causes a runtime exception.
- Diagnostic goal: Cover every constructor or make failure explicit.

### Buggy code

```haskell
headName (x:_) = name x
```

### Expected diagnosis

The empty-list pattern is missing, so [] triggers a non-exhaustive match.

### Corrected code

```haskell
headName [] = Nothing
headName (x:_) = Just (name x)
```

### Regression tests

```haskell
assert (headName [] == Nothing)
```

## HS-M-044: unsafe extraction

- Difficulty: Medium
- Language/framework: Haskell / Haskell
- Perspective: Maybe
- Concept: unsafe extraction
- Symptom: Missing configuration crashes startup.
- Diagnostic goal: Use maybe or bind the absence through the computation.

### Buggy code

```haskell
port = read (fromJust (lookup "port" config))
```

### Expected diagnosis

fromJust turns an expected missing-value case into an exception.

### Corrected code

```haskell
port = lookup "port" config >>= readMaybe
```

### Regression tests

```haskell
assert (port [] == Nothing)
```

## HS-M-045: lazy handle

- Difficulty: Medium
- Language/framework: Haskell / Haskell
- Perspective: IO
- Concept: lazy handle
- Symptom: A file is closed before lazy contents are consumed.
- Diagnostic goal: Force contents inside the resource lifetime or stream explicitly.

### Buggy code

```haskell
readLines path = withFile path ReadMode $ \h -> hGetContents h
```

### Expected diagnosis

Lazy hGetContents may defer reads until after withFile closes the handle.

### Corrected code

```haskell
readLines path = withFile path ReadMode $ \h -> hGetContents h >>= \s -> evaluate (length s) >> pure s
```

### Regression tests

```haskell
-- Test reading a complete file after the handle scope.
```

## HS-M-046: wrong bind

- Difficulty: Medium
- Language/framework: Haskell / Haskell
- Perspective: Monads
- Concept: wrong bind
- Symptom: A function receives an IO action instead of its value.
- Diagnostic goal: Use (>>=) or do notation at the effect boundary.

### Buggy code

```haskell
load = fetch >>= pure . parse
```

### Expected diagnosis

This is valid only if parse returns a pure value; mixing nested IO creates the wrong shape.

### Corrected code

```haskell
load = do
  raw <- fetch
  pure (parse raw)
```

### Regression tests

```haskell
assertIO load
```

## HS-M-047: quadratic append

- Difficulty: Medium
- Language/framework: Haskell / Haskell
- Perspective: Lists
- Concept: quadratic append
- Symptom: A list builder becomes slow for large input.
- Diagnostic goal: Prepend and reverse, or use a difference-list structure.

### Buggy code

```haskell
build xs = foldl (\acc x -> acc ++ [f x]) [] xs
```

### Expected diagnosis

Appending to the end copies the accumulated list on every iteration.

### Corrected code

```haskell
build xs = reverse (foldl (\acc x -> f x : acc) [] xs)
```

### Regression tests

```haskell
assert (build [1,2,3] == map f [1,2,3])
```

## HS-M-048: MVar deadlock

- Difficulty: Medium
- Language/framework: Haskell / Haskell
- Perspective: Concurrency
- Concept: MVar deadlock
- Symptom: Two workers wait forever.
- Diagnostic goal: Define lock ownership and always release it on exceptions.

### Buggy code

```haskell
withMVar lock $ \_ -> takeMVar lock
```

### Expected diagnosis

The same thread attempts to take a non-reentrant MVar twice.

### Corrected code

```haskell
withMVar lock $ \_ -> pure ()
```

### Regression tests

```haskell
-- Test completion with a timeout.
```

## HS-M-049: ambiguous instance

- Difficulty: Medium
- Language/framework: Haskell / Haskell
- Perspective: Typeclasses
- Concept: ambiguous instance
- Symptom: Compilation reports overlapping or ambiguous instances.
- Diagnostic goal: Keep instance selection coherent and use newtypes for distinct meanings.

### Buggy code

```haskell
instance Num a => Monoid a where mempty = 0
```

### Expected diagnosis

A broad orphan/overlapping instance conflicts with existing typeclass laws and instances.

### Corrected code

```haskell
newtype Sum a = Sum a
instance Num a => Semigroup (Sum a) where Sum a <> Sum b = Sum (a+b)
```

### Regression tests

```haskell
-- Compile with warnings as errors and test associativity.
```

## HS-M-050: stringly error

- Difficulty: Medium
- Language/framework: Haskell / Haskell
- Perspective: Errors
- Concept: stringly error
- Symptom: Callers cannot distinguish failure cases.
- Diagnostic goal: Use a sum type with stable constructors.

### Buggy code

```haskell
return (Left "not found")
```

### Expected diagnosis

String errors are fragile and force callers to inspect text.

### Corrected code

```haskell
data AppError = NotFound | InvalidInput | StorageError
return (Left NotFound)
```

### Regression tests

```haskell
assert (renderError NotFound == "not found")
```

## HS-M-051: space leak

- Difficulty: Medium
- Language/framework: Haskell / Haskell
- Perspective: Laziness
- Concept: space leak
- Symptom: A long-running fold consumes excessive memory.
- Diagnostic goal: Choose strict accumulation when the result must be evaluated incrementally.

### Buggy code

```haskell
sum = foldl (\a x -> a + x) 0 values
```

### Expected diagnosis

Lazy accumulation builds a chain of thunks instead of forcing each intermediate total.

### Corrected code

```haskell
sum = foldl' (+) 0 values
```

### Regression tests

```haskell
assert (sum [1..100] == 5050)
```

## HS-M-052: unsafe shared state

- Difficulty: Medium
- Language/framework: Haskell / Haskell
- Perspective: Purity
- Concept: unsafe shared state
- Symptom: A helper unexpectedly changes global state.
- Diagnostic goal: Make effects explicit in the type and call boundary.

### Buggy code

```haskell
counter = unsafePerformIO (newIORef 0)
```

### Expected diagnosis

unsafePerformIO hides mutation from the type system and can violate sharing assumptions.

### Corrected code

```haskell
counter :: IO (IORef Int)
counter = newIORef 0
```

### Regression tests

```haskell
-- Test through IO and assert the state transition explicitly.
```

## HS-M-053: partial pattern

- Difficulty: Medium
- Language/framework: Haskell / Haskell
- Perspective: Types
- Concept: partial pattern
- Symptom: An input causes a runtime exception.
- Diagnostic goal: Cover every constructor or make failure explicit.

### Buggy code

```haskell
headName (x:_) = name x
```

### Expected diagnosis

The empty-list pattern is missing, so [] triggers a non-exhaustive match.

### Corrected code

```haskell
headName [] = Nothing
headName (x:_) = Just (name x)
```

### Regression tests

```haskell
assert (headName [] == Nothing)
```

## HS-M-054: unsafe extraction

- Difficulty: Medium
- Language/framework: Haskell / Haskell
- Perspective: Maybe
- Concept: unsafe extraction
- Symptom: Missing configuration crashes startup.
- Diagnostic goal: Use maybe or bind the absence through the computation.

### Buggy code

```haskell
port = read (fromJust (lookup "port" config))
```

### Expected diagnosis

fromJust turns an expected missing-value case into an exception.

### Corrected code

```haskell
port = lookup "port" config >>= readMaybe
```

### Regression tests

```haskell
assert (port [] == Nothing)
```

## HS-M-055: lazy handle

- Difficulty: Medium
- Language/framework: Haskell / Haskell
- Perspective: IO
- Concept: lazy handle
- Symptom: A file is closed before lazy contents are consumed.
- Diagnostic goal: Force contents inside the resource lifetime or stream explicitly.

### Buggy code

```haskell
readLines path = withFile path ReadMode $ \h -> hGetContents h
```

### Expected diagnosis

Lazy hGetContents may defer reads until after withFile closes the handle.

### Corrected code

```haskell
readLines path = withFile path ReadMode $ \h -> hGetContents h >>= \s -> evaluate (length s) >> pure s
```

### Regression tests

```haskell
-- Test reading a complete file after the handle scope.
```

## HS-M-056: wrong bind

- Difficulty: Medium
- Language/framework: Haskell / Haskell
- Perspective: Monads
- Concept: wrong bind
- Symptom: A function receives an IO action instead of its value.
- Diagnostic goal: Use (>>=) or do notation at the effect boundary.

### Buggy code

```haskell
load = fetch >>= pure . parse
```

### Expected diagnosis

This is valid only if parse returns a pure value; mixing nested IO creates the wrong shape.

### Corrected code

```haskell
load = do
  raw <- fetch
  pure (parse raw)
```

### Regression tests

```haskell
assertIO load
```

## HS-M-057: quadratic append

- Difficulty: Medium
- Language/framework: Haskell / Haskell
- Perspective: Lists
- Concept: quadratic append
- Symptom: A list builder becomes slow for large input.
- Diagnostic goal: Prepend and reverse, or use a difference-list structure.

### Buggy code

```haskell
build xs = foldl (\acc x -> acc ++ [f x]) [] xs
```

### Expected diagnosis

Appending to the end copies the accumulated list on every iteration.

### Corrected code

```haskell
build xs = reverse (foldl (\acc x -> f x : acc) [] xs)
```

### Regression tests

```haskell
assert (build [1,2,3] == map f [1,2,3])
```

## HS-M-058: MVar deadlock

- Difficulty: Medium
- Language/framework: Haskell / Haskell
- Perspective: Concurrency
- Concept: MVar deadlock
- Symptom: Two workers wait forever.
- Diagnostic goal: Define lock ownership and always release it on exceptions.

### Buggy code

```haskell
withMVar lock $ \_ -> takeMVar lock
```

### Expected diagnosis

The same thread attempts to take a non-reentrant MVar twice.

### Corrected code

```haskell
withMVar lock $ \_ -> pure ()
```

### Regression tests

```haskell
-- Test completion with a timeout.
```

## HS-M-059: ambiguous instance

- Difficulty: Medium
- Language/framework: Haskell / Haskell
- Perspective: Typeclasses
- Concept: ambiguous instance
- Symptom: Compilation reports overlapping or ambiguous instances.
- Diagnostic goal: Keep instance selection coherent and use newtypes for distinct meanings.

### Buggy code

```haskell
instance Num a => Monoid a where mempty = 0
```

### Expected diagnosis

A broad orphan/overlapping instance conflicts with existing typeclass laws and instances.

### Corrected code

```haskell
newtype Sum a = Sum a
instance Num a => Semigroup (Sum a) where Sum a <> Sum b = Sum (a+b)
```

### Regression tests

```haskell
-- Compile with warnings as errors and test associativity.
```

## HS-M-060: stringly error

- Difficulty: Medium
- Language/framework: Haskell / Haskell
- Perspective: Errors
- Concept: stringly error
- Symptom: Callers cannot distinguish failure cases.
- Diagnostic goal: Use a sum type with stable constructors.

### Buggy code

```haskell
return (Left "not found")
```

### Expected diagnosis

String errors are fragile and force callers to inspect text.

### Corrected code

```haskell
data AppError = NotFound | InvalidInput | StorageError
return (Left NotFound)
```

### Regression tests

```haskell
assert (renderError NotFound == "not found")
```

## HS-M-061: space leak

- Difficulty: Medium
- Language/framework: Haskell / Haskell
- Perspective: Laziness
- Concept: space leak
- Symptom: A long-running fold consumes excessive memory.
- Diagnostic goal: Choose strict accumulation when the result must be evaluated incrementally.

### Buggy code

```haskell
sum = foldl (\a x -> a + x) 0 values
```

### Expected diagnosis

Lazy accumulation builds a chain of thunks instead of forcing each intermediate total.

### Corrected code

```haskell
sum = foldl' (+) 0 values
```

### Regression tests

```haskell
assert (sum [1..100] == 5050)
```

## HS-M-062: unsafe shared state

- Difficulty: Medium
- Language/framework: Haskell / Haskell
- Perspective: Purity
- Concept: unsafe shared state
- Symptom: A helper unexpectedly changes global state.
- Diagnostic goal: Make effects explicit in the type and call boundary.

### Buggy code

```haskell
counter = unsafePerformIO (newIORef 0)
```

### Expected diagnosis

unsafePerformIO hides mutation from the type system and can violate sharing assumptions.

### Corrected code

```haskell
counter :: IO (IORef Int)
counter = newIORef 0
```

### Regression tests

```haskell
-- Test through IO and assert the state transition explicitly.
```

## HS-M-063: partial pattern

- Difficulty: Medium
- Language/framework: Haskell / Haskell
- Perspective: Types
- Concept: partial pattern
- Symptom: An input causes a runtime exception.
- Diagnostic goal: Cover every constructor or make failure explicit.

### Buggy code

```haskell
headName (x:_) = name x
```

### Expected diagnosis

The empty-list pattern is missing, so [] triggers a non-exhaustive match.

### Corrected code

```haskell
headName [] = Nothing
headName (x:_) = Just (name x)
```

### Regression tests

```haskell
assert (headName [] == Nothing)
```

## HS-M-064: unsafe extraction

- Difficulty: Medium
- Language/framework: Haskell / Haskell
- Perspective: Maybe
- Concept: unsafe extraction
- Symptom: Missing configuration crashes startup.
- Diagnostic goal: Use maybe or bind the absence through the computation.

### Buggy code

```haskell
port = read (fromJust (lookup "port" config))
```

### Expected diagnosis

fromJust turns an expected missing-value case into an exception.

### Corrected code

```haskell
port = lookup "port" config >>= readMaybe
```

### Regression tests

```haskell
assert (port [] == Nothing)
```

## HS-M-065: lazy handle

- Difficulty: Medium
- Language/framework: Haskell / Haskell
- Perspective: IO
- Concept: lazy handle
- Symptom: A file is closed before lazy contents are consumed.
- Diagnostic goal: Force contents inside the resource lifetime or stream explicitly.

### Buggy code

```haskell
readLines path = withFile path ReadMode $ \h -> hGetContents h
```

### Expected diagnosis

Lazy hGetContents may defer reads until after withFile closes the handle.

### Corrected code

```haskell
readLines path = withFile path ReadMode $ \h -> hGetContents h >>= \s -> evaluate (length s) >> pure s
```

### Regression tests

```haskell
-- Test reading a complete file after the handle scope.
```

## HS-M-066: wrong bind

- Difficulty: Medium
- Language/framework: Haskell / Haskell
- Perspective: Monads
- Concept: wrong bind
- Symptom: A function receives an IO action instead of its value.
- Diagnostic goal: Use (>>=) or do notation at the effect boundary.

### Buggy code

```haskell
load = fetch >>= pure . parse
```

### Expected diagnosis

This is valid only if parse returns a pure value; mixing nested IO creates the wrong shape.

### Corrected code

```haskell
load = do
  raw <- fetch
  pure (parse raw)
```

### Regression tests

```haskell
assertIO load
```

## HS-M-067: quadratic append

- Difficulty: Medium
- Language/framework: Haskell / Haskell
- Perspective: Lists
- Concept: quadratic append
- Symptom: A list builder becomes slow for large input.
- Diagnostic goal: Prepend and reverse, or use a difference-list structure.

### Buggy code

```haskell
build xs = foldl (\acc x -> acc ++ [f x]) [] xs
```

### Expected diagnosis

Appending to the end copies the accumulated list on every iteration.

### Corrected code

```haskell
build xs = reverse (foldl (\acc x -> f x : acc) [] xs)
```

### Regression tests

```haskell
assert (build [1,2,3] == map f [1,2,3])
```

## HS-M-068: MVar deadlock

- Difficulty: Medium
- Language/framework: Haskell / Haskell
- Perspective: Concurrency
- Concept: MVar deadlock
- Symptom: Two workers wait forever.
- Diagnostic goal: Define lock ownership and always release it on exceptions.

### Buggy code

```haskell
withMVar lock $ \_ -> takeMVar lock
```

### Expected diagnosis

The same thread attempts to take a non-reentrant MVar twice.

### Corrected code

```haskell
withMVar lock $ \_ -> pure ()
```

### Regression tests

```haskell
-- Test completion with a timeout.
```

## HS-M-069: ambiguous instance

- Difficulty: Medium
- Language/framework: Haskell / Haskell
- Perspective: Typeclasses
- Concept: ambiguous instance
- Symptom: Compilation reports overlapping or ambiguous instances.
- Diagnostic goal: Keep instance selection coherent and use newtypes for distinct meanings.

### Buggy code

```haskell
instance Num a => Monoid a where mempty = 0
```

### Expected diagnosis

A broad orphan/overlapping instance conflicts with existing typeclass laws and instances.

### Corrected code

```haskell
newtype Sum a = Sum a
instance Num a => Semigroup (Sum a) where Sum a <> Sum b = Sum (a+b)
```

### Regression tests

```haskell
-- Compile with warnings as errors and test associativity.
```

## HS-M-070: stringly error

- Difficulty: Medium
- Language/framework: Haskell / Haskell
- Perspective: Errors
- Concept: stringly error
- Symptom: Callers cannot distinguish failure cases.
- Diagnostic goal: Use a sum type with stable constructors.

### Buggy code

```haskell
return (Left "not found")
```

### Expected diagnosis

String errors are fragile and force callers to inspect text.

### Corrected code

```haskell
data AppError = NotFound | InvalidInput | StorageError
return (Left NotFound)
```

### Regression tests

```haskell
assert (renderError NotFound == "not found")
```

## HS-M-071: space leak

- Difficulty: Medium
- Language/framework: Haskell / Haskell
- Perspective: Laziness
- Concept: space leak
- Symptom: A long-running fold consumes excessive memory.
- Diagnostic goal: Choose strict accumulation when the result must be evaluated incrementally.

### Buggy code

```haskell
sum = foldl (\a x -> a + x) 0 values
```

### Expected diagnosis

Lazy accumulation builds a chain of thunks instead of forcing each intermediate total.

### Corrected code

```haskell
sum = foldl' (+) 0 values
```

### Regression tests

```haskell
assert (sum [1..100] == 5050)
```

## HS-M-072: unsafe shared state

- Difficulty: Medium
- Language/framework: Haskell / Haskell
- Perspective: Purity
- Concept: unsafe shared state
- Symptom: A helper unexpectedly changes global state.
- Diagnostic goal: Make effects explicit in the type and call boundary.

### Buggy code

```haskell
counter = unsafePerformIO (newIORef 0)
```

### Expected diagnosis

unsafePerformIO hides mutation from the type system and can violate sharing assumptions.

### Corrected code

```haskell
counter :: IO (IORef Int)
counter = newIORef 0
```

### Regression tests

```haskell
-- Test through IO and assert the state transition explicitly.
```

## HS-M-073: partial pattern

- Difficulty: Medium
- Language/framework: Haskell / Haskell
- Perspective: Types
- Concept: partial pattern
- Symptom: An input causes a runtime exception.
- Diagnostic goal: Cover every constructor or make failure explicit.

### Buggy code

```haskell
headName (x:_) = name x
```

### Expected diagnosis

The empty-list pattern is missing, so [] triggers a non-exhaustive match.

### Corrected code

```haskell
headName [] = Nothing
headName (x:_) = Just (name x)
```

### Regression tests

```haskell
assert (headName [] == Nothing)
```

## HS-M-074: unsafe extraction

- Difficulty: Medium
- Language/framework: Haskell / Haskell
- Perspective: Maybe
- Concept: unsafe extraction
- Symptom: Missing configuration crashes startup.
- Diagnostic goal: Use maybe or bind the absence through the computation.

### Buggy code

```haskell
port = read (fromJust (lookup "port" config))
```

### Expected diagnosis

fromJust turns an expected missing-value case into an exception.

### Corrected code

```haskell
port = lookup "port" config >>= readMaybe
```

### Regression tests

```haskell
assert (port [] == Nothing)
```

## HS-M-075: lazy handle

- Difficulty: Medium
- Language/framework: Haskell / Haskell
- Perspective: IO
- Concept: lazy handle
- Symptom: A file is closed before lazy contents are consumed.
- Diagnostic goal: Force contents inside the resource lifetime or stream explicitly.

### Buggy code

```haskell
readLines path = withFile path ReadMode $ \h -> hGetContents h
```

### Expected diagnosis

Lazy hGetContents may defer reads until after withFile closes the handle.

### Corrected code

```haskell
readLines path = withFile path ReadMode $ \h -> hGetContents h >>= \s -> evaluate (length s) >> pure s
```

### Regression tests

```haskell
-- Test reading a complete file after the handle scope.
```

## HS-M-076: wrong bind

- Difficulty: Medium
- Language/framework: Haskell / Haskell
- Perspective: Monads
- Concept: wrong bind
- Symptom: A function receives an IO action instead of its value.
- Diagnostic goal: Use (>>=) or do notation at the effect boundary.

### Buggy code

```haskell
load = fetch >>= pure . parse
```

### Expected diagnosis

This is valid only if parse returns a pure value; mixing nested IO creates the wrong shape.

### Corrected code

```haskell
load = do
  raw <- fetch
  pure (parse raw)
```

### Regression tests

```haskell
assertIO load
```

## HS-M-077: quadratic append

- Difficulty: Medium
- Language/framework: Haskell / Haskell
- Perspective: Lists
- Concept: quadratic append
- Symptom: A list builder becomes slow for large input.
- Diagnostic goal: Prepend and reverse, or use a difference-list structure.

### Buggy code

```haskell
build xs = foldl (\acc x -> acc ++ [f x]) [] xs
```

### Expected diagnosis

Appending to the end copies the accumulated list on every iteration.

### Corrected code

```haskell
build xs = reverse (foldl (\acc x -> f x : acc) [] xs)
```

### Regression tests

```haskell
assert (build [1,2,3] == map f [1,2,3])
```

## HS-M-078: MVar deadlock

- Difficulty: Medium
- Language/framework: Haskell / Haskell
- Perspective: Concurrency
- Concept: MVar deadlock
- Symptom: Two workers wait forever.
- Diagnostic goal: Define lock ownership and always release it on exceptions.

### Buggy code

```haskell
withMVar lock $ \_ -> takeMVar lock
```

### Expected diagnosis

The same thread attempts to take a non-reentrant MVar twice.

### Corrected code

```haskell
withMVar lock $ \_ -> pure ()
```

### Regression tests

```haskell
-- Test completion with a timeout.
```

## HS-M-079: ambiguous instance

- Difficulty: Medium
- Language/framework: Haskell / Haskell
- Perspective: Typeclasses
- Concept: ambiguous instance
- Symptom: Compilation reports overlapping or ambiguous instances.
- Diagnostic goal: Keep instance selection coherent and use newtypes for distinct meanings.

### Buggy code

```haskell
instance Num a => Monoid a where mempty = 0
```

### Expected diagnosis

A broad orphan/overlapping instance conflicts with existing typeclass laws and instances.

### Corrected code

```haskell
newtype Sum a = Sum a
instance Num a => Semigroup (Sum a) where Sum a <> Sum b = Sum (a+b)
```

### Regression tests

```haskell
-- Compile with warnings as errors and test associativity.
```

## HS-M-080: stringly error

- Difficulty: Medium
- Language/framework: Haskell / Haskell
- Perspective: Errors
- Concept: stringly error
- Symptom: Callers cannot distinguish failure cases.
- Diagnostic goal: Use a sum type with stable constructors.

### Buggy code

```haskell
return (Left "not found")
```

### Expected diagnosis

String errors are fragile and force callers to inspect text.

### Corrected code

```haskell
data AppError = NotFound | InvalidInput | StorageError
return (Left NotFound)
```

### Regression tests

```haskell
assert (renderError NotFound == "not found")
```

## HS-M-081: space leak

- Difficulty: Medium
- Language/framework: Haskell / Haskell
- Perspective: Laziness
- Concept: space leak
- Symptom: A long-running fold consumes excessive memory.
- Diagnostic goal: Choose strict accumulation when the result must be evaluated incrementally.

### Buggy code

```haskell
sum = foldl (\a x -> a + x) 0 values
```

### Expected diagnosis

Lazy accumulation builds a chain of thunks instead of forcing each intermediate total.

### Corrected code

```haskell
sum = foldl' (+) 0 values
```

### Regression tests

```haskell
assert (sum [1..100] == 5050)
```

## HS-M-082: unsafe shared state

- Difficulty: Medium
- Language/framework: Haskell / Haskell
- Perspective: Purity
- Concept: unsafe shared state
- Symptom: A helper unexpectedly changes global state.
- Diagnostic goal: Make effects explicit in the type and call boundary.

### Buggy code

```haskell
counter = unsafePerformIO (newIORef 0)
```

### Expected diagnosis

unsafePerformIO hides mutation from the type system and can violate sharing assumptions.

### Corrected code

```haskell
counter :: IO (IORef Int)
counter = newIORef 0
```

### Regression tests

```haskell
-- Test through IO and assert the state transition explicitly.
```

## HS-M-083: partial pattern

- Difficulty: Medium
- Language/framework: Haskell / Haskell
- Perspective: Types
- Concept: partial pattern
- Symptom: An input causes a runtime exception.
- Diagnostic goal: Cover every constructor or make failure explicit.

### Buggy code

```haskell
headName (x:_) = name x
```

### Expected diagnosis

The empty-list pattern is missing, so [] triggers a non-exhaustive match.

### Corrected code

```haskell
headName [] = Nothing
headName (x:_) = Just (name x)
```

### Regression tests

```haskell
assert (headName [] == Nothing)
```

## HS-M-084: unsafe extraction

- Difficulty: Medium
- Language/framework: Haskell / Haskell
- Perspective: Maybe
- Concept: unsafe extraction
- Symptom: Missing configuration crashes startup.
- Diagnostic goal: Use maybe or bind the absence through the computation.

### Buggy code

```haskell
port = read (fromJust (lookup "port" config))
```

### Expected diagnosis

fromJust turns an expected missing-value case into an exception.

### Corrected code

```haskell
port = lookup "port" config >>= readMaybe
```

### Regression tests

```haskell
assert (port [] == Nothing)
```

## HS-M-085: lazy handle

- Difficulty: Medium
- Language/framework: Haskell / Haskell
- Perspective: IO
- Concept: lazy handle
- Symptom: A file is closed before lazy contents are consumed.
- Diagnostic goal: Force contents inside the resource lifetime or stream explicitly.

### Buggy code

```haskell
readLines path = withFile path ReadMode $ \h -> hGetContents h
```

### Expected diagnosis

Lazy hGetContents may defer reads until after withFile closes the handle.

### Corrected code

```haskell
readLines path = withFile path ReadMode $ \h -> hGetContents h >>= \s -> evaluate (length s) >> pure s
```

### Regression tests

```haskell
-- Test reading a complete file after the handle scope.
```

## HS-M-086: wrong bind

- Difficulty: Medium
- Language/framework: Haskell / Haskell
- Perspective: Monads
- Concept: wrong bind
- Symptom: A function receives an IO action instead of its value.
- Diagnostic goal: Use (>>=) or do notation at the effect boundary.

### Buggy code

```haskell
load = fetch >>= pure . parse
```

### Expected diagnosis

This is valid only if parse returns a pure value; mixing nested IO creates the wrong shape.

### Corrected code

```haskell
load = do
  raw <- fetch
  pure (parse raw)
```

### Regression tests

```haskell
assertIO load
```

## HS-M-087: quadratic append

- Difficulty: Medium
- Language/framework: Haskell / Haskell
- Perspective: Lists
- Concept: quadratic append
- Symptom: A list builder becomes slow for large input.
- Diagnostic goal: Prepend and reverse, or use a difference-list structure.

### Buggy code

```haskell
build xs = foldl (\acc x -> acc ++ [f x]) [] xs
```

### Expected diagnosis

Appending to the end copies the accumulated list on every iteration.

### Corrected code

```haskell
build xs = reverse (foldl (\acc x -> f x : acc) [] xs)
```

### Regression tests

```haskell
assert (build [1,2,3] == map f [1,2,3])
```

## HS-M-088: MVar deadlock

- Difficulty: Medium
- Language/framework: Haskell / Haskell
- Perspective: Concurrency
- Concept: MVar deadlock
- Symptom: Two workers wait forever.
- Diagnostic goal: Define lock ownership and always release it on exceptions.

### Buggy code

```haskell
withMVar lock $ \_ -> takeMVar lock
```

### Expected diagnosis

The same thread attempts to take a non-reentrant MVar twice.

### Corrected code

```haskell
withMVar lock $ \_ -> pure ()
```

### Regression tests

```haskell
-- Test completion with a timeout.
```

## HS-M-089: ambiguous instance

- Difficulty: Medium
- Language/framework: Haskell / Haskell
- Perspective: Typeclasses
- Concept: ambiguous instance
- Symptom: Compilation reports overlapping or ambiguous instances.
- Diagnostic goal: Keep instance selection coherent and use newtypes for distinct meanings.

### Buggy code

```haskell
instance Num a => Monoid a where mempty = 0
```

### Expected diagnosis

A broad orphan/overlapping instance conflicts with existing typeclass laws and instances.

### Corrected code

```haskell
newtype Sum a = Sum a
instance Num a => Semigroup (Sum a) where Sum a <> Sum b = Sum (a+b)
```

### Regression tests

```haskell
-- Compile with warnings as errors and test associativity.
```

## HS-M-090: stringly error

- Difficulty: Medium
- Language/framework: Haskell / Haskell
- Perspective: Errors
- Concept: stringly error
- Symptom: Callers cannot distinguish failure cases.
- Diagnostic goal: Use a sum type with stable constructors.

### Buggy code

```haskell
return (Left "not found")
```

### Expected diagnosis

String errors are fragile and force callers to inspect text.

### Corrected code

```haskell
data AppError = NotFound | InvalidInput | StorageError
return (Left NotFound)
```

### Regression tests

```haskell
assert (renderError NotFound == "not found")
```

## HS-M-091: space leak

- Difficulty: Medium
- Language/framework: Haskell / Haskell
- Perspective: Laziness
- Concept: space leak
- Symptom: A long-running fold consumes excessive memory.
- Diagnostic goal: Choose strict accumulation when the result must be evaluated incrementally.

### Buggy code

```haskell
sum = foldl (\a x -> a + x) 0 values
```

### Expected diagnosis

Lazy accumulation builds a chain of thunks instead of forcing each intermediate total.

### Corrected code

```haskell
sum = foldl' (+) 0 values
```

### Regression tests

```haskell
assert (sum [1..100] == 5050)
```

## HS-M-092: unsafe shared state

- Difficulty: Medium
- Language/framework: Haskell / Haskell
- Perspective: Purity
- Concept: unsafe shared state
- Symptom: A helper unexpectedly changes global state.
- Diagnostic goal: Make effects explicit in the type and call boundary.

### Buggy code

```haskell
counter = unsafePerformIO (newIORef 0)
```

### Expected diagnosis

unsafePerformIO hides mutation from the type system and can violate sharing assumptions.

### Corrected code

```haskell
counter :: IO (IORef Int)
counter = newIORef 0
```

### Regression tests

```haskell
-- Test through IO and assert the state transition explicitly.
```

## HS-M-093: partial pattern

- Difficulty: Medium
- Language/framework: Haskell / Haskell
- Perspective: Types
- Concept: partial pattern
- Symptom: An input causes a runtime exception.
- Diagnostic goal: Cover every constructor or make failure explicit.

### Buggy code

```haskell
headName (x:_) = name x
```

### Expected diagnosis

The empty-list pattern is missing, so [] triggers a non-exhaustive match.

### Corrected code

```haskell
headName [] = Nothing
headName (x:_) = Just (name x)
```

### Regression tests

```haskell
assert (headName [] == Nothing)
```

## HS-M-094: unsafe extraction

- Difficulty: Medium
- Language/framework: Haskell / Haskell
- Perspective: Maybe
- Concept: unsafe extraction
- Symptom: Missing configuration crashes startup.
- Diagnostic goal: Use maybe or bind the absence through the computation.

### Buggy code

```haskell
port = read (fromJust (lookup "port" config))
```

### Expected diagnosis

fromJust turns an expected missing-value case into an exception.

### Corrected code

```haskell
port = lookup "port" config >>= readMaybe
```

### Regression tests

```haskell
assert (port [] == Nothing)
```

## HS-M-095: lazy handle

- Difficulty: Medium
- Language/framework: Haskell / Haskell
- Perspective: IO
- Concept: lazy handle
- Symptom: A file is closed before lazy contents are consumed.
- Diagnostic goal: Force contents inside the resource lifetime or stream explicitly.

### Buggy code

```haskell
readLines path = withFile path ReadMode $ \h -> hGetContents h
```

### Expected diagnosis

Lazy hGetContents may defer reads until after withFile closes the handle.

### Corrected code

```haskell
readLines path = withFile path ReadMode $ \h -> hGetContents h >>= \s -> evaluate (length s) >> pure s
```

### Regression tests

```haskell
-- Test reading a complete file after the handle scope.
```

## HS-M-096: wrong bind

- Difficulty: Medium
- Language/framework: Haskell / Haskell
- Perspective: Monads
- Concept: wrong bind
- Symptom: A function receives an IO action instead of its value.
- Diagnostic goal: Use (>>=) or do notation at the effect boundary.

### Buggy code

```haskell
load = fetch >>= pure . parse
```

### Expected diagnosis

This is valid only if parse returns a pure value; mixing nested IO creates the wrong shape.

### Corrected code

```haskell
load = do
  raw <- fetch
  pure (parse raw)
```

### Regression tests

```haskell
assertIO load
```

## HS-M-097: quadratic append

- Difficulty: Medium
- Language/framework: Haskell / Haskell
- Perspective: Lists
- Concept: quadratic append
- Symptom: A list builder becomes slow for large input.
- Diagnostic goal: Prepend and reverse, or use a difference-list structure.

### Buggy code

```haskell
build xs = foldl (\acc x -> acc ++ [f x]) [] xs
```

### Expected diagnosis

Appending to the end copies the accumulated list on every iteration.

### Corrected code

```haskell
build xs = reverse (foldl (\acc x -> f x : acc) [] xs)
```

### Regression tests

```haskell
assert (build [1,2,3] == map f [1,2,3])
```

## HS-M-098: MVar deadlock

- Difficulty: Medium
- Language/framework: Haskell / Haskell
- Perspective: Concurrency
- Concept: MVar deadlock
- Symptom: Two workers wait forever.
- Diagnostic goal: Define lock ownership and always release it on exceptions.

### Buggy code

```haskell
withMVar lock $ \_ -> takeMVar lock
```

### Expected diagnosis

The same thread attempts to take a non-reentrant MVar twice.

### Corrected code

```haskell
withMVar lock $ \_ -> pure ()
```

### Regression tests

```haskell
-- Test completion with a timeout.
```

## HS-M-099: ambiguous instance

- Difficulty: Medium
- Language/framework: Haskell / Haskell
- Perspective: Typeclasses
- Concept: ambiguous instance
- Symptom: Compilation reports overlapping or ambiguous instances.
- Diagnostic goal: Keep instance selection coherent and use newtypes for distinct meanings.

### Buggy code

```haskell
instance Num a => Monoid a where mempty = 0
```

### Expected diagnosis

A broad orphan/overlapping instance conflicts with existing typeclass laws and instances.

### Corrected code

```haskell
newtype Sum a = Sum a
instance Num a => Semigroup (Sum a) where Sum a <> Sum b = Sum (a+b)
```

### Regression tests

```haskell
-- Compile with warnings as errors and test associativity.
```

## HS-M-100: stringly error

- Difficulty: Medium
- Language/framework: Haskell / Haskell
- Perspective: Errors
- Concept: stringly error
- Symptom: Callers cannot distinguish failure cases.
- Diagnostic goal: Use a sum type with stable constructors.

### Buggy code

```haskell
return (Left "not found")
```

### Expected diagnosis

String errors are fragile and force callers to inspect text.

### Corrected code

```haskell
data AppError = NotFound | InvalidInput | StorageError
return (Left NotFound)
```

### Regression tests

```haskell
assert (renderError NotFound == "not found")
```

## HS-H-001: space leak

- Difficulty: Hard
- Language/framework: Haskell / Haskell
- Perspective: Laziness
- Concept: space leak
- Symptom: A long-running fold consumes excessive memory.
- Diagnostic goal: Choose strict accumulation when the result must be evaluated incrementally.

### Buggy code

```haskell
sum = foldl (\a x -> a + x) 0 values
```

### Expected diagnosis

Lazy accumulation builds a chain of thunks instead of forcing each intermediate total.

### Corrected code

```haskell
sum = foldl' (+) 0 values
```

### Regression tests

```haskell
assert (sum [1..100] == 5050)
```

## HS-H-002: unsafe shared state

- Difficulty: Hard
- Language/framework: Haskell / Haskell
- Perspective: Purity
- Concept: unsafe shared state
- Symptom: A helper unexpectedly changes global state.
- Diagnostic goal: Make effects explicit in the type and call boundary.

### Buggy code

```haskell
counter = unsafePerformIO (newIORef 0)
```

### Expected diagnosis

unsafePerformIO hides mutation from the type system and can violate sharing assumptions.

### Corrected code

```haskell
counter :: IO (IORef Int)
counter = newIORef 0
```

### Regression tests

```haskell
-- Test through IO and assert the state transition explicitly.
```

## HS-H-003: partial pattern

- Difficulty: Hard
- Language/framework: Haskell / Haskell
- Perspective: Types
- Concept: partial pattern
- Symptom: An input causes a runtime exception.
- Diagnostic goal: Cover every constructor or make failure explicit.

### Buggy code

```haskell
headName (x:_) = name x
```

### Expected diagnosis

The empty-list pattern is missing, so [] triggers a non-exhaustive match.

### Corrected code

```haskell
headName [] = Nothing
headName (x:_) = Just (name x)
```

### Regression tests

```haskell
assert (headName [] == Nothing)
```

## HS-H-004: unsafe extraction

- Difficulty: Hard
- Language/framework: Haskell / Haskell
- Perspective: Maybe
- Concept: unsafe extraction
- Symptom: Missing configuration crashes startup.
- Diagnostic goal: Use maybe or bind the absence through the computation.

### Buggy code

```haskell
port = read (fromJust (lookup "port" config))
```

### Expected diagnosis

fromJust turns an expected missing-value case into an exception.

### Corrected code

```haskell
port = lookup "port" config >>= readMaybe
```

### Regression tests

```haskell
assert (port [] == Nothing)
```

## HS-H-005: lazy handle

- Difficulty: Hard
- Language/framework: Haskell / Haskell
- Perspective: IO
- Concept: lazy handle
- Symptom: A file is closed before lazy contents are consumed.
- Diagnostic goal: Force contents inside the resource lifetime or stream explicitly.

### Buggy code

```haskell
readLines path = withFile path ReadMode $ \h -> hGetContents h
```

### Expected diagnosis

Lazy hGetContents may defer reads until after withFile closes the handle.

### Corrected code

```haskell
readLines path = withFile path ReadMode $ \h -> hGetContents h >>= \s -> evaluate (length s) >> pure s
```

### Regression tests

```haskell
-- Test reading a complete file after the handle scope.
```

## HS-H-006: wrong bind

- Difficulty: Hard
- Language/framework: Haskell / Haskell
- Perspective: Monads
- Concept: wrong bind
- Symptom: A function receives an IO action instead of its value.
- Diagnostic goal: Use (>>=) or do notation at the effect boundary.

### Buggy code

```haskell
load = fetch >>= pure . parse
```

### Expected diagnosis

This is valid only if parse returns a pure value; mixing nested IO creates the wrong shape.

### Corrected code

```haskell
load = do
  raw <- fetch
  pure (parse raw)
```

### Regression tests

```haskell
assertIO load
```

## HS-H-007: quadratic append

- Difficulty: Hard
- Language/framework: Haskell / Haskell
- Perspective: Lists
- Concept: quadratic append
- Symptom: A list builder becomes slow for large input.
- Diagnostic goal: Prepend and reverse, or use a difference-list structure.

### Buggy code

```haskell
build xs = foldl (\acc x -> acc ++ [f x]) [] xs
```

### Expected diagnosis

Appending to the end copies the accumulated list on every iteration.

### Corrected code

```haskell
build xs = reverse (foldl (\acc x -> f x : acc) [] xs)
```

### Regression tests

```haskell
assert (build [1,2,3] == map f [1,2,3])
```

## HS-H-008: MVar deadlock

- Difficulty: Hard
- Language/framework: Haskell / Haskell
- Perspective: Concurrency
- Concept: MVar deadlock
- Symptom: Two workers wait forever.
- Diagnostic goal: Define lock ownership and always release it on exceptions.

### Buggy code

```haskell
withMVar lock $ \_ -> takeMVar lock
```

### Expected diagnosis

The same thread attempts to take a non-reentrant MVar twice.

### Corrected code

```haskell
withMVar lock $ \_ -> pure ()
```

### Regression tests

```haskell
-- Test completion with a timeout.
```

## HS-H-009: ambiguous instance

- Difficulty: Hard
- Language/framework: Haskell / Haskell
- Perspective: Typeclasses
- Concept: ambiguous instance
- Symptom: Compilation reports overlapping or ambiguous instances.
- Diagnostic goal: Keep instance selection coherent and use newtypes for distinct meanings.

### Buggy code

```haskell
instance Num a => Monoid a where mempty = 0
```

### Expected diagnosis

A broad orphan/overlapping instance conflicts with existing typeclass laws and instances.

### Corrected code

```haskell
newtype Sum a = Sum a
instance Num a => Semigroup (Sum a) where Sum a <> Sum b = Sum (a+b)
```

### Regression tests

```haskell
-- Compile with warnings as errors and test associativity.
```

## HS-H-010: stringly error

- Difficulty: Hard
- Language/framework: Haskell / Haskell
- Perspective: Errors
- Concept: stringly error
- Symptom: Callers cannot distinguish failure cases.
- Diagnostic goal: Use a sum type with stable constructors.

### Buggy code

```haskell
return (Left "not found")
```

### Expected diagnosis

String errors are fragile and force callers to inspect text.

### Corrected code

```haskell
data AppError = NotFound | InvalidInput | StorageError
return (Left NotFound)
```

### Regression tests

```haskell
assert (renderError NotFound == "not found")
```

## HS-H-011: space leak

- Difficulty: Hard
- Language/framework: Haskell / Haskell
- Perspective: Laziness
- Concept: space leak
- Symptom: A long-running fold consumes excessive memory.
- Diagnostic goal: Choose strict accumulation when the result must be evaluated incrementally.

### Buggy code

```haskell
sum = foldl (\a x -> a + x) 0 values
```

### Expected diagnosis

Lazy accumulation builds a chain of thunks instead of forcing each intermediate total.

### Corrected code

```haskell
sum = foldl' (+) 0 values
```

### Regression tests

```haskell
assert (sum [1..100] == 5050)
```

## HS-H-012: unsafe shared state

- Difficulty: Hard
- Language/framework: Haskell / Haskell
- Perspective: Purity
- Concept: unsafe shared state
- Symptom: A helper unexpectedly changes global state.
- Diagnostic goal: Make effects explicit in the type and call boundary.

### Buggy code

```haskell
counter = unsafePerformIO (newIORef 0)
```

### Expected diagnosis

unsafePerformIO hides mutation from the type system and can violate sharing assumptions.

### Corrected code

```haskell
counter :: IO (IORef Int)
counter = newIORef 0
```

### Regression tests

```haskell
-- Test through IO and assert the state transition explicitly.
```

## HS-H-013: partial pattern

- Difficulty: Hard
- Language/framework: Haskell / Haskell
- Perspective: Types
- Concept: partial pattern
- Symptom: An input causes a runtime exception.
- Diagnostic goal: Cover every constructor or make failure explicit.

### Buggy code

```haskell
headName (x:_) = name x
```

### Expected diagnosis

The empty-list pattern is missing, so [] triggers a non-exhaustive match.

### Corrected code

```haskell
headName [] = Nothing
headName (x:_) = Just (name x)
```

### Regression tests

```haskell
assert (headName [] == Nothing)
```

## HS-H-014: unsafe extraction

- Difficulty: Hard
- Language/framework: Haskell / Haskell
- Perspective: Maybe
- Concept: unsafe extraction
- Symptom: Missing configuration crashes startup.
- Diagnostic goal: Use maybe or bind the absence through the computation.

### Buggy code

```haskell
port = read (fromJust (lookup "port" config))
```

### Expected diagnosis

fromJust turns an expected missing-value case into an exception.

### Corrected code

```haskell
port = lookup "port" config >>= readMaybe
```

### Regression tests

```haskell
assert (port [] == Nothing)
```

## HS-H-015: lazy handle

- Difficulty: Hard
- Language/framework: Haskell / Haskell
- Perspective: IO
- Concept: lazy handle
- Symptom: A file is closed before lazy contents are consumed.
- Diagnostic goal: Force contents inside the resource lifetime or stream explicitly.

### Buggy code

```haskell
readLines path = withFile path ReadMode $ \h -> hGetContents h
```

### Expected diagnosis

Lazy hGetContents may defer reads until after withFile closes the handle.

### Corrected code

```haskell
readLines path = withFile path ReadMode $ \h -> hGetContents h >>= \s -> evaluate (length s) >> pure s
```

### Regression tests

```haskell
-- Test reading a complete file after the handle scope.
```

## HS-H-016: wrong bind

- Difficulty: Hard
- Language/framework: Haskell / Haskell
- Perspective: Monads
- Concept: wrong bind
- Symptom: A function receives an IO action instead of its value.
- Diagnostic goal: Use (>>=) or do notation at the effect boundary.

### Buggy code

```haskell
load = fetch >>= pure . parse
```

### Expected diagnosis

This is valid only if parse returns a pure value; mixing nested IO creates the wrong shape.

### Corrected code

```haskell
load = do
  raw <- fetch
  pure (parse raw)
```

### Regression tests

```haskell
assertIO load
```

## HS-H-017: quadratic append

- Difficulty: Hard
- Language/framework: Haskell / Haskell
- Perspective: Lists
- Concept: quadratic append
- Symptom: A list builder becomes slow for large input.
- Diagnostic goal: Prepend and reverse, or use a difference-list structure.

### Buggy code

```haskell
build xs = foldl (\acc x -> acc ++ [f x]) [] xs
```

### Expected diagnosis

Appending to the end copies the accumulated list on every iteration.

### Corrected code

```haskell
build xs = reverse (foldl (\acc x -> f x : acc) [] xs)
```

### Regression tests

```haskell
assert (build [1,2,3] == map f [1,2,3])
```

## HS-H-018: MVar deadlock

- Difficulty: Hard
- Language/framework: Haskell / Haskell
- Perspective: Concurrency
- Concept: MVar deadlock
- Symptom: Two workers wait forever.
- Diagnostic goal: Define lock ownership and always release it on exceptions.

### Buggy code

```haskell
withMVar lock $ \_ -> takeMVar lock
```

### Expected diagnosis

The same thread attempts to take a non-reentrant MVar twice.

### Corrected code

```haskell
withMVar lock $ \_ -> pure ()
```

### Regression tests

```haskell
-- Test completion with a timeout.
```

## HS-H-019: ambiguous instance

- Difficulty: Hard
- Language/framework: Haskell / Haskell
- Perspective: Typeclasses
- Concept: ambiguous instance
- Symptom: Compilation reports overlapping or ambiguous instances.
- Diagnostic goal: Keep instance selection coherent and use newtypes for distinct meanings.

### Buggy code

```haskell
instance Num a => Monoid a where mempty = 0
```

### Expected diagnosis

A broad orphan/overlapping instance conflicts with existing typeclass laws and instances.

### Corrected code

```haskell
newtype Sum a = Sum a
instance Num a => Semigroup (Sum a) where Sum a <> Sum b = Sum (a+b)
```

### Regression tests

```haskell
-- Compile with warnings as errors and test associativity.
```

## HS-H-020: stringly error

- Difficulty: Hard
- Language/framework: Haskell / Haskell
- Perspective: Errors
- Concept: stringly error
- Symptom: Callers cannot distinguish failure cases.
- Diagnostic goal: Use a sum type with stable constructors.

### Buggy code

```haskell
return (Left "not found")
```

### Expected diagnosis

String errors are fragile and force callers to inspect text.

### Corrected code

```haskell
data AppError = NotFound | InvalidInput | StorageError
return (Left NotFound)
```

### Regression tests

```haskell
assert (renderError NotFound == "not found")
```

## HS-H-021: space leak

- Difficulty: Hard
- Language/framework: Haskell / Haskell
- Perspective: Laziness
- Concept: space leak
- Symptom: A long-running fold consumes excessive memory.
- Diagnostic goal: Choose strict accumulation when the result must be evaluated incrementally.

### Buggy code

```haskell
sum = foldl (\a x -> a + x) 0 values
```

### Expected diagnosis

Lazy accumulation builds a chain of thunks instead of forcing each intermediate total.

### Corrected code

```haskell
sum = foldl' (+) 0 values
```

### Regression tests

```haskell
assert (sum [1..100] == 5050)
```

## HS-H-022: unsafe shared state

- Difficulty: Hard
- Language/framework: Haskell / Haskell
- Perspective: Purity
- Concept: unsafe shared state
- Symptom: A helper unexpectedly changes global state.
- Diagnostic goal: Make effects explicit in the type and call boundary.

### Buggy code

```haskell
counter = unsafePerformIO (newIORef 0)
```

### Expected diagnosis

unsafePerformIO hides mutation from the type system and can violate sharing assumptions.

### Corrected code

```haskell
counter :: IO (IORef Int)
counter = newIORef 0
```

### Regression tests

```haskell
-- Test through IO and assert the state transition explicitly.
```

## HS-H-023: partial pattern

- Difficulty: Hard
- Language/framework: Haskell / Haskell
- Perspective: Types
- Concept: partial pattern
- Symptom: An input causes a runtime exception.
- Diagnostic goal: Cover every constructor or make failure explicit.

### Buggy code

```haskell
headName (x:_) = name x
```

### Expected diagnosis

The empty-list pattern is missing, so [] triggers a non-exhaustive match.

### Corrected code

```haskell
headName [] = Nothing
headName (x:_) = Just (name x)
```

### Regression tests

```haskell
assert (headName [] == Nothing)
```

## HS-H-024: unsafe extraction

- Difficulty: Hard
- Language/framework: Haskell / Haskell
- Perspective: Maybe
- Concept: unsafe extraction
- Symptom: Missing configuration crashes startup.
- Diagnostic goal: Use maybe or bind the absence through the computation.

### Buggy code

```haskell
port = read (fromJust (lookup "port" config))
```

### Expected diagnosis

fromJust turns an expected missing-value case into an exception.

### Corrected code

```haskell
port = lookup "port" config >>= readMaybe
```

### Regression tests

```haskell
assert (port [] == Nothing)
```

## HS-H-025: lazy handle

- Difficulty: Hard
- Language/framework: Haskell / Haskell
- Perspective: IO
- Concept: lazy handle
- Symptom: A file is closed before lazy contents are consumed.
- Diagnostic goal: Force contents inside the resource lifetime or stream explicitly.

### Buggy code

```haskell
readLines path = withFile path ReadMode $ \h -> hGetContents h
```

### Expected diagnosis

Lazy hGetContents may defer reads until after withFile closes the handle.

### Corrected code

```haskell
readLines path = withFile path ReadMode $ \h -> hGetContents h >>= \s -> evaluate (length s) >> pure s
```

### Regression tests

```haskell
-- Test reading a complete file after the handle scope.
```

## HS-H-026: wrong bind

- Difficulty: Hard
- Language/framework: Haskell / Haskell
- Perspective: Monads
- Concept: wrong bind
- Symptom: A function receives an IO action instead of its value.
- Diagnostic goal: Use (>>=) or do notation at the effect boundary.

### Buggy code

```haskell
load = fetch >>= pure . parse
```

### Expected diagnosis

This is valid only if parse returns a pure value; mixing nested IO creates the wrong shape.

### Corrected code

```haskell
load = do
  raw <- fetch
  pure (parse raw)
```

### Regression tests

```haskell
assertIO load
```

## HS-H-027: quadratic append

- Difficulty: Hard
- Language/framework: Haskell / Haskell
- Perspective: Lists
- Concept: quadratic append
- Symptom: A list builder becomes slow for large input.
- Diagnostic goal: Prepend and reverse, or use a difference-list structure.

### Buggy code

```haskell
build xs = foldl (\acc x -> acc ++ [f x]) [] xs
```

### Expected diagnosis

Appending to the end copies the accumulated list on every iteration.

### Corrected code

```haskell
build xs = reverse (foldl (\acc x -> f x : acc) [] xs)
```

### Regression tests

```haskell
assert (build [1,2,3] == map f [1,2,3])
```

## HS-H-028: MVar deadlock

- Difficulty: Hard
- Language/framework: Haskell / Haskell
- Perspective: Concurrency
- Concept: MVar deadlock
- Symptom: Two workers wait forever.
- Diagnostic goal: Define lock ownership and always release it on exceptions.

### Buggy code

```haskell
withMVar lock $ \_ -> takeMVar lock
```

### Expected diagnosis

The same thread attempts to take a non-reentrant MVar twice.

### Corrected code

```haskell
withMVar lock $ \_ -> pure ()
```

### Regression tests

```haskell
-- Test completion with a timeout.
```

## HS-H-029: ambiguous instance

- Difficulty: Hard
- Language/framework: Haskell / Haskell
- Perspective: Typeclasses
- Concept: ambiguous instance
- Symptom: Compilation reports overlapping or ambiguous instances.
- Diagnostic goal: Keep instance selection coherent and use newtypes for distinct meanings.

### Buggy code

```haskell
instance Num a => Monoid a where mempty = 0
```

### Expected diagnosis

A broad orphan/overlapping instance conflicts with existing typeclass laws and instances.

### Corrected code

```haskell
newtype Sum a = Sum a
instance Num a => Semigroup (Sum a) where Sum a <> Sum b = Sum (a+b)
```

### Regression tests

```haskell
-- Compile with warnings as errors and test associativity.
```

## HS-H-030: stringly error

- Difficulty: Hard
- Language/framework: Haskell / Haskell
- Perspective: Errors
- Concept: stringly error
- Symptom: Callers cannot distinguish failure cases.
- Diagnostic goal: Use a sum type with stable constructors.

### Buggy code

```haskell
return (Left "not found")
```

### Expected diagnosis

String errors are fragile and force callers to inspect text.

### Corrected code

```haskell
data AppError = NotFound | InvalidInput | StorageError
return (Left NotFound)
```

### Regression tests

```haskell
assert (renderError NotFound == "not found")
```

## HS-H-031: space leak

- Difficulty: Hard
- Language/framework: Haskell / Haskell
- Perspective: Laziness
- Concept: space leak
- Symptom: A long-running fold consumes excessive memory.
- Diagnostic goal: Choose strict accumulation when the result must be evaluated incrementally.

### Buggy code

```haskell
sum = foldl (\a x -> a + x) 0 values
```

### Expected diagnosis

Lazy accumulation builds a chain of thunks instead of forcing each intermediate total.

### Corrected code

```haskell
sum = foldl' (+) 0 values
```

### Regression tests

```haskell
assert (sum [1..100] == 5050)
```

## HS-H-032: unsafe shared state

- Difficulty: Hard
- Language/framework: Haskell / Haskell
- Perspective: Purity
- Concept: unsafe shared state
- Symptom: A helper unexpectedly changes global state.
- Diagnostic goal: Make effects explicit in the type and call boundary.

### Buggy code

```haskell
counter = unsafePerformIO (newIORef 0)
```

### Expected diagnosis

unsafePerformIO hides mutation from the type system and can violate sharing assumptions.

### Corrected code

```haskell
counter :: IO (IORef Int)
counter = newIORef 0
```

### Regression tests

```haskell
-- Test through IO and assert the state transition explicitly.
```

## HS-H-033: partial pattern

- Difficulty: Hard
- Language/framework: Haskell / Haskell
- Perspective: Types
- Concept: partial pattern
- Symptom: An input causes a runtime exception.
- Diagnostic goal: Cover every constructor or make failure explicit.

### Buggy code

```haskell
headName (x:_) = name x
```

### Expected diagnosis

The empty-list pattern is missing, so [] triggers a non-exhaustive match.

### Corrected code

```haskell
headName [] = Nothing
headName (x:_) = Just (name x)
```

### Regression tests

```haskell
assert (headName [] == Nothing)
```

## HS-H-034: unsafe extraction

- Difficulty: Hard
- Language/framework: Haskell / Haskell
- Perspective: Maybe
- Concept: unsafe extraction
- Symptom: Missing configuration crashes startup.
- Diagnostic goal: Use maybe or bind the absence through the computation.

### Buggy code

```haskell
port = read (fromJust (lookup "port" config))
```

### Expected diagnosis

fromJust turns an expected missing-value case into an exception.

### Corrected code

```haskell
port = lookup "port" config >>= readMaybe
```

### Regression tests

```haskell
assert (port [] == Nothing)
```

## HS-H-035: lazy handle

- Difficulty: Hard
- Language/framework: Haskell / Haskell
- Perspective: IO
- Concept: lazy handle
- Symptom: A file is closed before lazy contents are consumed.
- Diagnostic goal: Force contents inside the resource lifetime or stream explicitly.

### Buggy code

```haskell
readLines path = withFile path ReadMode $ \h -> hGetContents h
```

### Expected diagnosis

Lazy hGetContents may defer reads until after withFile closes the handle.

### Corrected code

```haskell
readLines path = withFile path ReadMode $ \h -> hGetContents h >>= \s -> evaluate (length s) >> pure s
```

### Regression tests

```haskell
-- Test reading a complete file after the handle scope.
```

## HS-H-036: wrong bind

- Difficulty: Hard
- Language/framework: Haskell / Haskell
- Perspective: Monads
- Concept: wrong bind
- Symptom: A function receives an IO action instead of its value.
- Diagnostic goal: Use (>>=) or do notation at the effect boundary.

### Buggy code

```haskell
load = fetch >>= pure . parse
```

### Expected diagnosis

This is valid only if parse returns a pure value; mixing nested IO creates the wrong shape.

### Corrected code

```haskell
load = do
  raw <- fetch
  pure (parse raw)
```

### Regression tests

```haskell
assertIO load
```

## HS-H-037: quadratic append

- Difficulty: Hard
- Language/framework: Haskell / Haskell
- Perspective: Lists
- Concept: quadratic append
- Symptom: A list builder becomes slow for large input.
- Diagnostic goal: Prepend and reverse, or use a difference-list structure.

### Buggy code

```haskell
build xs = foldl (\acc x -> acc ++ [f x]) [] xs
```

### Expected diagnosis

Appending to the end copies the accumulated list on every iteration.

### Corrected code

```haskell
build xs = reverse (foldl (\acc x -> f x : acc) [] xs)
```

### Regression tests

```haskell
assert (build [1,2,3] == map f [1,2,3])
```

## HS-H-038: MVar deadlock

- Difficulty: Hard
- Language/framework: Haskell / Haskell
- Perspective: Concurrency
- Concept: MVar deadlock
- Symptom: Two workers wait forever.
- Diagnostic goal: Define lock ownership and always release it on exceptions.

### Buggy code

```haskell
withMVar lock $ \_ -> takeMVar lock
```

### Expected diagnosis

The same thread attempts to take a non-reentrant MVar twice.

### Corrected code

```haskell
withMVar lock $ \_ -> pure ()
```

### Regression tests

```haskell
-- Test completion with a timeout.
```

## HS-H-039: ambiguous instance

- Difficulty: Hard
- Language/framework: Haskell / Haskell
- Perspective: Typeclasses
- Concept: ambiguous instance
- Symptom: Compilation reports overlapping or ambiguous instances.
- Diagnostic goal: Keep instance selection coherent and use newtypes for distinct meanings.

### Buggy code

```haskell
instance Num a => Monoid a where mempty = 0
```

### Expected diagnosis

A broad orphan/overlapping instance conflicts with existing typeclass laws and instances.

### Corrected code

```haskell
newtype Sum a = Sum a
instance Num a => Semigroup (Sum a) where Sum a <> Sum b = Sum (a+b)
```

### Regression tests

```haskell
-- Compile with warnings as errors and test associativity.
```

## HS-H-040: stringly error

- Difficulty: Hard
- Language/framework: Haskell / Haskell
- Perspective: Errors
- Concept: stringly error
- Symptom: Callers cannot distinguish failure cases.
- Diagnostic goal: Use a sum type with stable constructors.

### Buggy code

```haskell
return (Left "not found")
```

### Expected diagnosis

String errors are fragile and force callers to inspect text.

### Corrected code

```haskell
data AppError = NotFound | InvalidInput | StorageError
return (Left NotFound)
```

### Regression tests

```haskell
assert (renderError NotFound == "not found")
```

## HS-H-041: space leak

- Difficulty: Hard
- Language/framework: Haskell / Haskell
- Perspective: Laziness
- Concept: space leak
- Symptom: A long-running fold consumes excessive memory.
- Diagnostic goal: Choose strict accumulation when the result must be evaluated incrementally.

### Buggy code

```haskell
sum = foldl (\a x -> a + x) 0 values
```

### Expected diagnosis

Lazy accumulation builds a chain of thunks instead of forcing each intermediate total.

### Corrected code

```haskell
sum = foldl' (+) 0 values
```

### Regression tests

```haskell
assert (sum [1..100] == 5050)
```

## HS-H-042: unsafe shared state

- Difficulty: Hard
- Language/framework: Haskell / Haskell
- Perspective: Purity
- Concept: unsafe shared state
- Symptom: A helper unexpectedly changes global state.
- Diagnostic goal: Make effects explicit in the type and call boundary.

### Buggy code

```haskell
counter = unsafePerformIO (newIORef 0)
```

### Expected diagnosis

unsafePerformIO hides mutation from the type system and can violate sharing assumptions.

### Corrected code

```haskell
counter :: IO (IORef Int)
counter = newIORef 0
```

### Regression tests

```haskell
-- Test through IO and assert the state transition explicitly.
```

## HS-H-043: partial pattern

- Difficulty: Hard
- Language/framework: Haskell / Haskell
- Perspective: Types
- Concept: partial pattern
- Symptom: An input causes a runtime exception.
- Diagnostic goal: Cover every constructor or make failure explicit.

### Buggy code

```haskell
headName (x:_) = name x
```

### Expected diagnosis

The empty-list pattern is missing, so [] triggers a non-exhaustive match.

### Corrected code

```haskell
headName [] = Nothing
headName (x:_) = Just (name x)
```

### Regression tests

```haskell
assert (headName [] == Nothing)
```

## HS-H-044: unsafe extraction

- Difficulty: Hard
- Language/framework: Haskell / Haskell
- Perspective: Maybe
- Concept: unsafe extraction
- Symptom: Missing configuration crashes startup.
- Diagnostic goal: Use maybe or bind the absence through the computation.

### Buggy code

```haskell
port = read (fromJust (lookup "port" config))
```

### Expected diagnosis

fromJust turns an expected missing-value case into an exception.

### Corrected code

```haskell
port = lookup "port" config >>= readMaybe
```

### Regression tests

```haskell
assert (port [] == Nothing)
```

## HS-H-045: lazy handle

- Difficulty: Hard
- Language/framework: Haskell / Haskell
- Perspective: IO
- Concept: lazy handle
- Symptom: A file is closed before lazy contents are consumed.
- Diagnostic goal: Force contents inside the resource lifetime or stream explicitly.

### Buggy code

```haskell
readLines path = withFile path ReadMode $ \h -> hGetContents h
```

### Expected diagnosis

Lazy hGetContents may defer reads until after withFile closes the handle.

### Corrected code

```haskell
readLines path = withFile path ReadMode $ \h -> hGetContents h >>= \s -> evaluate (length s) >> pure s
```

### Regression tests

```haskell
-- Test reading a complete file after the handle scope.
```

## HS-H-046: wrong bind

- Difficulty: Hard
- Language/framework: Haskell / Haskell
- Perspective: Monads
- Concept: wrong bind
- Symptom: A function receives an IO action instead of its value.
- Diagnostic goal: Use (>>=) or do notation at the effect boundary.

### Buggy code

```haskell
load = fetch >>= pure . parse
```

### Expected diagnosis

This is valid only if parse returns a pure value; mixing nested IO creates the wrong shape.

### Corrected code

```haskell
load = do
  raw <- fetch
  pure (parse raw)
```

### Regression tests

```haskell
assertIO load
```

## HS-H-047: quadratic append

- Difficulty: Hard
- Language/framework: Haskell / Haskell
- Perspective: Lists
- Concept: quadratic append
- Symptom: A list builder becomes slow for large input.
- Diagnostic goal: Prepend and reverse, or use a difference-list structure.

### Buggy code

```haskell
build xs = foldl (\acc x -> acc ++ [f x]) [] xs
```

### Expected diagnosis

Appending to the end copies the accumulated list on every iteration.

### Corrected code

```haskell
build xs = reverse (foldl (\acc x -> f x : acc) [] xs)
```

### Regression tests

```haskell
assert (build [1,2,3] == map f [1,2,3])
```

## HS-H-048: MVar deadlock

- Difficulty: Hard
- Language/framework: Haskell / Haskell
- Perspective: Concurrency
- Concept: MVar deadlock
- Symptom: Two workers wait forever.
- Diagnostic goal: Define lock ownership and always release it on exceptions.

### Buggy code

```haskell
withMVar lock $ \_ -> takeMVar lock
```

### Expected diagnosis

The same thread attempts to take a non-reentrant MVar twice.

### Corrected code

```haskell
withMVar lock $ \_ -> pure ()
```

### Regression tests

```haskell
-- Test completion with a timeout.
```

## HS-H-049: ambiguous instance

- Difficulty: Hard
- Language/framework: Haskell / Haskell
- Perspective: Typeclasses
- Concept: ambiguous instance
- Symptom: Compilation reports overlapping or ambiguous instances.
- Diagnostic goal: Keep instance selection coherent and use newtypes for distinct meanings.

### Buggy code

```haskell
instance Num a => Monoid a where mempty = 0
```

### Expected diagnosis

A broad orphan/overlapping instance conflicts with existing typeclass laws and instances.

### Corrected code

```haskell
newtype Sum a = Sum a
instance Num a => Semigroup (Sum a) where Sum a <> Sum b = Sum (a+b)
```

### Regression tests

```haskell
-- Compile with warnings as errors and test associativity.
```

## HS-H-050: stringly error

- Difficulty: Hard
- Language/framework: Haskell / Haskell
- Perspective: Errors
- Concept: stringly error
- Symptom: Callers cannot distinguish failure cases.
- Diagnostic goal: Use a sum type with stable constructors.

### Buggy code

```haskell
return (Left "not found")
```

### Expected diagnosis

String errors are fragile and force callers to inspect text.

### Corrected code

```haskell
data AppError = NotFound | InvalidInput | StorageError
return (Left NotFound)
```

### Regression tests

```haskell
assert (renderError NotFound == "not found")
```

## HS-H-051: space leak

- Difficulty: Hard
- Language/framework: Haskell / Haskell
- Perspective: Laziness
- Concept: space leak
- Symptom: A long-running fold consumes excessive memory.
- Diagnostic goal: Choose strict accumulation when the result must be evaluated incrementally.

### Buggy code

```haskell
sum = foldl (\a x -> a + x) 0 values
```

### Expected diagnosis

Lazy accumulation builds a chain of thunks instead of forcing each intermediate total.

### Corrected code

```haskell
sum = foldl' (+) 0 values
```

### Regression tests

```haskell
assert (sum [1..100] == 5050)
```

## HS-H-052: unsafe shared state

- Difficulty: Hard
- Language/framework: Haskell / Haskell
- Perspective: Purity
- Concept: unsafe shared state
- Symptom: A helper unexpectedly changes global state.
- Diagnostic goal: Make effects explicit in the type and call boundary.

### Buggy code

```haskell
counter = unsafePerformIO (newIORef 0)
```

### Expected diagnosis

unsafePerformIO hides mutation from the type system and can violate sharing assumptions.

### Corrected code

```haskell
counter :: IO (IORef Int)
counter = newIORef 0
```

### Regression tests

```haskell
-- Test through IO and assert the state transition explicitly.
```

## HS-H-053: partial pattern

- Difficulty: Hard
- Language/framework: Haskell / Haskell
- Perspective: Types
- Concept: partial pattern
- Symptom: An input causes a runtime exception.
- Diagnostic goal: Cover every constructor or make failure explicit.

### Buggy code

```haskell
headName (x:_) = name x
```

### Expected diagnosis

The empty-list pattern is missing, so [] triggers a non-exhaustive match.

### Corrected code

```haskell
headName [] = Nothing
headName (x:_) = Just (name x)
```

### Regression tests

```haskell
assert (headName [] == Nothing)
```

## HS-H-054: unsafe extraction

- Difficulty: Hard
- Language/framework: Haskell / Haskell
- Perspective: Maybe
- Concept: unsafe extraction
- Symptom: Missing configuration crashes startup.
- Diagnostic goal: Use maybe or bind the absence through the computation.

### Buggy code

```haskell
port = read (fromJust (lookup "port" config))
```

### Expected diagnosis

fromJust turns an expected missing-value case into an exception.

### Corrected code

```haskell
port = lookup "port" config >>= readMaybe
```

### Regression tests

```haskell
assert (port [] == Nothing)
```

## HS-H-055: lazy handle

- Difficulty: Hard
- Language/framework: Haskell / Haskell
- Perspective: IO
- Concept: lazy handle
- Symptom: A file is closed before lazy contents are consumed.
- Diagnostic goal: Force contents inside the resource lifetime or stream explicitly.

### Buggy code

```haskell
readLines path = withFile path ReadMode $ \h -> hGetContents h
```

### Expected diagnosis

Lazy hGetContents may defer reads until after withFile closes the handle.

### Corrected code

```haskell
readLines path = withFile path ReadMode $ \h -> hGetContents h >>= \s -> evaluate (length s) >> pure s
```

### Regression tests

```haskell
-- Test reading a complete file after the handle scope.
```

## HS-H-056: wrong bind

- Difficulty: Hard
- Language/framework: Haskell / Haskell
- Perspective: Monads
- Concept: wrong bind
- Symptom: A function receives an IO action instead of its value.
- Diagnostic goal: Use (>>=) or do notation at the effect boundary.

### Buggy code

```haskell
load = fetch >>= pure . parse
```

### Expected diagnosis

This is valid only if parse returns a pure value; mixing nested IO creates the wrong shape.

### Corrected code

```haskell
load = do
  raw <- fetch
  pure (parse raw)
```

### Regression tests

```haskell
assertIO load
```

## HS-H-057: quadratic append

- Difficulty: Hard
- Language/framework: Haskell / Haskell
- Perspective: Lists
- Concept: quadratic append
- Symptom: A list builder becomes slow for large input.
- Diagnostic goal: Prepend and reverse, or use a difference-list structure.

### Buggy code

```haskell
build xs = foldl (\acc x -> acc ++ [f x]) [] xs
```

### Expected diagnosis

Appending to the end copies the accumulated list on every iteration.

### Corrected code

```haskell
build xs = reverse (foldl (\acc x -> f x : acc) [] xs)
```

### Regression tests

```haskell
assert (build [1,2,3] == map f [1,2,3])
```

## HS-H-058: MVar deadlock

- Difficulty: Hard
- Language/framework: Haskell / Haskell
- Perspective: Concurrency
- Concept: MVar deadlock
- Symptom: Two workers wait forever.
- Diagnostic goal: Define lock ownership and always release it on exceptions.

### Buggy code

```haskell
withMVar lock $ \_ -> takeMVar lock
```

### Expected diagnosis

The same thread attempts to take a non-reentrant MVar twice.

### Corrected code

```haskell
withMVar lock $ \_ -> pure ()
```

### Regression tests

```haskell
-- Test completion with a timeout.
```

## HS-H-059: ambiguous instance

- Difficulty: Hard
- Language/framework: Haskell / Haskell
- Perspective: Typeclasses
- Concept: ambiguous instance
- Symptom: Compilation reports overlapping or ambiguous instances.
- Diagnostic goal: Keep instance selection coherent and use newtypes for distinct meanings.

### Buggy code

```haskell
instance Num a => Monoid a where mempty = 0
```

### Expected diagnosis

A broad orphan/overlapping instance conflicts with existing typeclass laws and instances.

### Corrected code

```haskell
newtype Sum a = Sum a
instance Num a => Semigroup (Sum a) where Sum a <> Sum b = Sum (a+b)
```

### Regression tests

```haskell
-- Compile with warnings as errors and test associativity.
```

## HS-H-060: stringly error

- Difficulty: Hard
- Language/framework: Haskell / Haskell
- Perspective: Errors
- Concept: stringly error
- Symptom: Callers cannot distinguish failure cases.
- Diagnostic goal: Use a sum type with stable constructors.

### Buggy code

```haskell
return (Left "not found")
```

### Expected diagnosis

String errors are fragile and force callers to inspect text.

### Corrected code

```haskell
data AppError = NotFound | InvalidInput | StorageError
return (Left NotFound)
```

### Regression tests

```haskell
assert (renderError NotFound == "not found")
```

## HS-H-061: space leak

- Difficulty: Hard
- Language/framework: Haskell / Haskell
- Perspective: Laziness
- Concept: space leak
- Symptom: A long-running fold consumes excessive memory.
- Diagnostic goal: Choose strict accumulation when the result must be evaluated incrementally.

### Buggy code

```haskell
sum = foldl (\a x -> a + x) 0 values
```

### Expected diagnosis

Lazy accumulation builds a chain of thunks instead of forcing each intermediate total.

### Corrected code

```haskell
sum = foldl' (+) 0 values
```

### Regression tests

```haskell
assert (sum [1..100] == 5050)
```

## HS-H-062: unsafe shared state

- Difficulty: Hard
- Language/framework: Haskell / Haskell
- Perspective: Purity
- Concept: unsafe shared state
- Symptom: A helper unexpectedly changes global state.
- Diagnostic goal: Make effects explicit in the type and call boundary.

### Buggy code

```haskell
counter = unsafePerformIO (newIORef 0)
```

### Expected diagnosis

unsafePerformIO hides mutation from the type system and can violate sharing assumptions.

### Corrected code

```haskell
counter :: IO (IORef Int)
counter = newIORef 0
```

### Regression tests

```haskell
-- Test through IO and assert the state transition explicitly.
```

## HS-H-063: partial pattern

- Difficulty: Hard
- Language/framework: Haskell / Haskell
- Perspective: Types
- Concept: partial pattern
- Symptom: An input causes a runtime exception.
- Diagnostic goal: Cover every constructor or make failure explicit.

### Buggy code

```haskell
headName (x:_) = name x
```

### Expected diagnosis

The empty-list pattern is missing, so [] triggers a non-exhaustive match.

### Corrected code

```haskell
headName [] = Nothing
headName (x:_) = Just (name x)
```

### Regression tests

```haskell
assert (headName [] == Nothing)
```

## HS-H-064: unsafe extraction

- Difficulty: Hard
- Language/framework: Haskell / Haskell
- Perspective: Maybe
- Concept: unsafe extraction
- Symptom: Missing configuration crashes startup.
- Diagnostic goal: Use maybe or bind the absence through the computation.

### Buggy code

```haskell
port = read (fromJust (lookup "port" config))
```

### Expected diagnosis

fromJust turns an expected missing-value case into an exception.

### Corrected code

```haskell
port = lookup "port" config >>= readMaybe
```

### Regression tests

```haskell
assert (port [] == Nothing)
```

## HS-H-065: lazy handle

- Difficulty: Hard
- Language/framework: Haskell / Haskell
- Perspective: IO
- Concept: lazy handle
- Symptom: A file is closed before lazy contents are consumed.
- Diagnostic goal: Force contents inside the resource lifetime or stream explicitly.

### Buggy code

```haskell
readLines path = withFile path ReadMode $ \h -> hGetContents h
```

### Expected diagnosis

Lazy hGetContents may defer reads until after withFile closes the handle.

### Corrected code

```haskell
readLines path = withFile path ReadMode $ \h -> hGetContents h >>= \s -> evaluate (length s) >> pure s
```

### Regression tests

```haskell
-- Test reading a complete file after the handle scope.
```

## HS-H-066: wrong bind

- Difficulty: Hard
- Language/framework: Haskell / Haskell
- Perspective: Monads
- Concept: wrong bind
- Symptom: A function receives an IO action instead of its value.
- Diagnostic goal: Use (>>=) or do notation at the effect boundary.

### Buggy code

```haskell
load = fetch >>= pure . parse
```

### Expected diagnosis

This is valid only if parse returns a pure value; mixing nested IO creates the wrong shape.

### Corrected code

```haskell
load = do
  raw <- fetch
  pure (parse raw)
```

### Regression tests

```haskell
assertIO load
```

## HS-H-067: quadratic append

- Difficulty: Hard
- Language/framework: Haskell / Haskell
- Perspective: Lists
- Concept: quadratic append
- Symptom: A list builder becomes slow for large input.
- Diagnostic goal: Prepend and reverse, or use a difference-list structure.

### Buggy code

```haskell
build xs = foldl (\acc x -> acc ++ [f x]) [] xs
```

### Expected diagnosis

Appending to the end copies the accumulated list on every iteration.

### Corrected code

```haskell
build xs = reverse (foldl (\acc x -> f x : acc) [] xs)
```

### Regression tests

```haskell
assert (build [1,2,3] == map f [1,2,3])
```

## HS-H-068: MVar deadlock

- Difficulty: Hard
- Language/framework: Haskell / Haskell
- Perspective: Concurrency
- Concept: MVar deadlock
- Symptom: Two workers wait forever.
- Diagnostic goal: Define lock ownership and always release it on exceptions.

### Buggy code

```haskell
withMVar lock $ \_ -> takeMVar lock
```

### Expected diagnosis

The same thread attempts to take a non-reentrant MVar twice.

### Corrected code

```haskell
withMVar lock $ \_ -> pure ()
```

### Regression tests

```haskell
-- Test completion with a timeout.
```

## HS-H-069: ambiguous instance

- Difficulty: Hard
- Language/framework: Haskell / Haskell
- Perspective: Typeclasses
- Concept: ambiguous instance
- Symptom: Compilation reports overlapping or ambiguous instances.
- Diagnostic goal: Keep instance selection coherent and use newtypes for distinct meanings.

### Buggy code

```haskell
instance Num a => Monoid a where mempty = 0
```

### Expected diagnosis

A broad orphan/overlapping instance conflicts with existing typeclass laws and instances.

### Corrected code

```haskell
newtype Sum a = Sum a
instance Num a => Semigroup (Sum a) where Sum a <> Sum b = Sum (a+b)
```

### Regression tests

```haskell
-- Compile with warnings as errors and test associativity.
```

## HS-H-070: stringly error

- Difficulty: Hard
- Language/framework: Haskell / Haskell
- Perspective: Errors
- Concept: stringly error
- Symptom: Callers cannot distinguish failure cases.
- Diagnostic goal: Use a sum type with stable constructors.

### Buggy code

```haskell
return (Left "not found")
```

### Expected diagnosis

String errors are fragile and force callers to inspect text.

### Corrected code

```haskell
data AppError = NotFound | InvalidInput | StorageError
return (Left NotFound)
```

### Regression tests

```haskell
assert (renderError NotFound == "not found")
```

## HS-H-071: space leak

- Difficulty: Hard
- Language/framework: Haskell / Haskell
- Perspective: Laziness
- Concept: space leak
- Symptom: A long-running fold consumes excessive memory.
- Diagnostic goal: Choose strict accumulation when the result must be evaluated incrementally.

### Buggy code

```haskell
sum = foldl (\a x -> a + x) 0 values
```

### Expected diagnosis

Lazy accumulation builds a chain of thunks instead of forcing each intermediate total.

### Corrected code

```haskell
sum = foldl' (+) 0 values
```

### Regression tests

```haskell
assert (sum [1..100] == 5050)
```

## HS-H-072: unsafe shared state

- Difficulty: Hard
- Language/framework: Haskell / Haskell
- Perspective: Purity
- Concept: unsafe shared state
- Symptom: A helper unexpectedly changes global state.
- Diagnostic goal: Make effects explicit in the type and call boundary.

### Buggy code

```haskell
counter = unsafePerformIO (newIORef 0)
```

### Expected diagnosis

unsafePerformIO hides mutation from the type system and can violate sharing assumptions.

### Corrected code

```haskell
counter :: IO (IORef Int)
counter = newIORef 0
```

### Regression tests

```haskell
-- Test through IO and assert the state transition explicitly.
```

## HS-H-073: partial pattern

- Difficulty: Hard
- Language/framework: Haskell / Haskell
- Perspective: Types
- Concept: partial pattern
- Symptom: An input causes a runtime exception.
- Diagnostic goal: Cover every constructor or make failure explicit.

### Buggy code

```haskell
headName (x:_) = name x
```

### Expected diagnosis

The empty-list pattern is missing, so [] triggers a non-exhaustive match.

### Corrected code

```haskell
headName [] = Nothing
headName (x:_) = Just (name x)
```

### Regression tests

```haskell
assert (headName [] == Nothing)
```

## HS-H-074: unsafe extraction

- Difficulty: Hard
- Language/framework: Haskell / Haskell
- Perspective: Maybe
- Concept: unsafe extraction
- Symptom: Missing configuration crashes startup.
- Diagnostic goal: Use maybe or bind the absence through the computation.

### Buggy code

```haskell
port = read (fromJust (lookup "port" config))
```

### Expected diagnosis

fromJust turns an expected missing-value case into an exception.

### Corrected code

```haskell
port = lookup "port" config >>= readMaybe
```

### Regression tests

```haskell
assert (port [] == Nothing)
```

## HS-H-075: lazy handle

- Difficulty: Hard
- Language/framework: Haskell / Haskell
- Perspective: IO
- Concept: lazy handle
- Symptom: A file is closed before lazy contents are consumed.
- Diagnostic goal: Force contents inside the resource lifetime or stream explicitly.

### Buggy code

```haskell
readLines path = withFile path ReadMode $ \h -> hGetContents h
```

### Expected diagnosis

Lazy hGetContents may defer reads until after withFile closes the handle.

### Corrected code

```haskell
readLines path = withFile path ReadMode $ \h -> hGetContents h >>= \s -> evaluate (length s) >> pure s
```

### Regression tests

```haskell
-- Test reading a complete file after the handle scope.
```

## HS-H-076: wrong bind

- Difficulty: Hard
- Language/framework: Haskell / Haskell
- Perspective: Monads
- Concept: wrong bind
- Symptom: A function receives an IO action instead of its value.
- Diagnostic goal: Use (>>=) or do notation at the effect boundary.

### Buggy code

```haskell
load = fetch >>= pure . parse
```

### Expected diagnosis

This is valid only if parse returns a pure value; mixing nested IO creates the wrong shape.

### Corrected code

```haskell
load = do
  raw <- fetch
  pure (parse raw)
```

### Regression tests

```haskell
assertIO load
```

## HS-H-077: quadratic append

- Difficulty: Hard
- Language/framework: Haskell / Haskell
- Perspective: Lists
- Concept: quadratic append
- Symptom: A list builder becomes slow for large input.
- Diagnostic goal: Prepend and reverse, or use a difference-list structure.

### Buggy code

```haskell
build xs = foldl (\acc x -> acc ++ [f x]) [] xs
```

### Expected diagnosis

Appending to the end copies the accumulated list on every iteration.

### Corrected code

```haskell
build xs = reverse (foldl (\acc x -> f x : acc) [] xs)
```

### Regression tests

```haskell
assert (build [1,2,3] == map f [1,2,3])
```

## HS-H-078: MVar deadlock

- Difficulty: Hard
- Language/framework: Haskell / Haskell
- Perspective: Concurrency
- Concept: MVar deadlock
- Symptom: Two workers wait forever.
- Diagnostic goal: Define lock ownership and always release it on exceptions.

### Buggy code

```haskell
withMVar lock $ \_ -> takeMVar lock
```

### Expected diagnosis

The same thread attempts to take a non-reentrant MVar twice.

### Corrected code

```haskell
withMVar lock $ \_ -> pure ()
```

### Regression tests

```haskell
-- Test completion with a timeout.
```

## HS-H-079: ambiguous instance

- Difficulty: Hard
- Language/framework: Haskell / Haskell
- Perspective: Typeclasses
- Concept: ambiguous instance
- Symptom: Compilation reports overlapping or ambiguous instances.
- Diagnostic goal: Keep instance selection coherent and use newtypes for distinct meanings.

### Buggy code

```haskell
instance Num a => Monoid a where mempty = 0
```

### Expected diagnosis

A broad orphan/overlapping instance conflicts with existing typeclass laws and instances.

### Corrected code

```haskell
newtype Sum a = Sum a
instance Num a => Semigroup (Sum a) where Sum a <> Sum b = Sum (a+b)
```

### Regression tests

```haskell
-- Compile with warnings as errors and test associativity.
```

## HS-H-080: stringly error

- Difficulty: Hard
- Language/framework: Haskell / Haskell
- Perspective: Errors
- Concept: stringly error
- Symptom: Callers cannot distinguish failure cases.
- Diagnostic goal: Use a sum type with stable constructors.

### Buggy code

```haskell
return (Left "not found")
```

### Expected diagnosis

String errors are fragile and force callers to inspect text.

### Corrected code

```haskell
data AppError = NotFound | InvalidInput | StorageError
return (Left NotFound)
```

### Regression tests

```haskell
assert (renderError NotFound == "not found")
```

## HS-H-081: space leak

- Difficulty: Hard
- Language/framework: Haskell / Haskell
- Perspective: Laziness
- Concept: space leak
- Symptom: A long-running fold consumes excessive memory.
- Diagnostic goal: Choose strict accumulation when the result must be evaluated incrementally.

### Buggy code

```haskell
sum = foldl (\a x -> a + x) 0 values
```

### Expected diagnosis

Lazy accumulation builds a chain of thunks instead of forcing each intermediate total.

### Corrected code

```haskell
sum = foldl' (+) 0 values
```

### Regression tests

```haskell
assert (sum [1..100] == 5050)
```

## HS-H-082: unsafe shared state

- Difficulty: Hard
- Language/framework: Haskell / Haskell
- Perspective: Purity
- Concept: unsafe shared state
- Symptom: A helper unexpectedly changes global state.
- Diagnostic goal: Make effects explicit in the type and call boundary.

### Buggy code

```haskell
counter = unsafePerformIO (newIORef 0)
```

### Expected diagnosis

unsafePerformIO hides mutation from the type system and can violate sharing assumptions.

### Corrected code

```haskell
counter :: IO (IORef Int)
counter = newIORef 0
```

### Regression tests

```haskell
-- Test through IO and assert the state transition explicitly.
```

## HS-H-083: partial pattern

- Difficulty: Hard
- Language/framework: Haskell / Haskell
- Perspective: Types
- Concept: partial pattern
- Symptom: An input causes a runtime exception.
- Diagnostic goal: Cover every constructor or make failure explicit.

### Buggy code

```haskell
headName (x:_) = name x
```

### Expected diagnosis

The empty-list pattern is missing, so [] triggers a non-exhaustive match.

### Corrected code

```haskell
headName [] = Nothing
headName (x:_) = Just (name x)
```

### Regression tests

```haskell
assert (headName [] == Nothing)
```

## HS-H-084: unsafe extraction

- Difficulty: Hard
- Language/framework: Haskell / Haskell
- Perspective: Maybe
- Concept: unsafe extraction
- Symptom: Missing configuration crashes startup.
- Diagnostic goal: Use maybe or bind the absence through the computation.

### Buggy code

```haskell
port = read (fromJust (lookup "port" config))
```

### Expected diagnosis

fromJust turns an expected missing-value case into an exception.

### Corrected code

```haskell
port = lookup "port" config >>= readMaybe
```

### Regression tests

```haskell
assert (port [] == Nothing)
```

## HS-H-085: lazy handle

- Difficulty: Hard
- Language/framework: Haskell / Haskell
- Perspective: IO
- Concept: lazy handle
- Symptom: A file is closed before lazy contents are consumed.
- Diagnostic goal: Force contents inside the resource lifetime or stream explicitly.

### Buggy code

```haskell
readLines path = withFile path ReadMode $ \h -> hGetContents h
```

### Expected diagnosis

Lazy hGetContents may defer reads until after withFile closes the handle.

### Corrected code

```haskell
readLines path = withFile path ReadMode $ \h -> hGetContents h >>= \s -> evaluate (length s) >> pure s
```

### Regression tests

```haskell
-- Test reading a complete file after the handle scope.
```

## HS-H-086: wrong bind

- Difficulty: Hard
- Language/framework: Haskell / Haskell
- Perspective: Monads
- Concept: wrong bind
- Symptom: A function receives an IO action instead of its value.
- Diagnostic goal: Use (>>=) or do notation at the effect boundary.

### Buggy code

```haskell
load = fetch >>= pure . parse
```

### Expected diagnosis

This is valid only if parse returns a pure value; mixing nested IO creates the wrong shape.

### Corrected code

```haskell
load = do
  raw <- fetch
  pure (parse raw)
```

### Regression tests

```haskell
assertIO load
```

## HS-H-087: quadratic append

- Difficulty: Hard
- Language/framework: Haskell / Haskell
- Perspective: Lists
- Concept: quadratic append
- Symptom: A list builder becomes slow for large input.
- Diagnostic goal: Prepend and reverse, or use a difference-list structure.

### Buggy code

```haskell
build xs = foldl (\acc x -> acc ++ [f x]) [] xs
```

### Expected diagnosis

Appending to the end copies the accumulated list on every iteration.

### Corrected code

```haskell
build xs = reverse (foldl (\acc x -> f x : acc) [] xs)
```

### Regression tests

```haskell
assert (build [1,2,3] == map f [1,2,3])
```

## HS-H-088: MVar deadlock

- Difficulty: Hard
- Language/framework: Haskell / Haskell
- Perspective: Concurrency
- Concept: MVar deadlock
- Symptom: Two workers wait forever.
- Diagnostic goal: Define lock ownership and always release it on exceptions.

### Buggy code

```haskell
withMVar lock $ \_ -> takeMVar lock
```

### Expected diagnosis

The same thread attempts to take a non-reentrant MVar twice.

### Corrected code

```haskell
withMVar lock $ \_ -> pure ()
```

### Regression tests

```haskell
-- Test completion with a timeout.
```

## HS-H-089: ambiguous instance

- Difficulty: Hard
- Language/framework: Haskell / Haskell
- Perspective: Typeclasses
- Concept: ambiguous instance
- Symptom: Compilation reports overlapping or ambiguous instances.
- Diagnostic goal: Keep instance selection coherent and use newtypes for distinct meanings.

### Buggy code

```haskell
instance Num a => Monoid a where mempty = 0
```

### Expected diagnosis

A broad orphan/overlapping instance conflicts with existing typeclass laws and instances.

### Corrected code

```haskell
newtype Sum a = Sum a
instance Num a => Semigroup (Sum a) where Sum a <> Sum b = Sum (a+b)
```

### Regression tests

```haskell
-- Compile with warnings as errors and test associativity.
```

## HS-H-090: stringly error

- Difficulty: Hard
- Language/framework: Haskell / Haskell
- Perspective: Errors
- Concept: stringly error
- Symptom: Callers cannot distinguish failure cases.
- Diagnostic goal: Use a sum type with stable constructors.

### Buggy code

```haskell
return (Left "not found")
```

### Expected diagnosis

String errors are fragile and force callers to inspect text.

### Corrected code

```haskell
data AppError = NotFound | InvalidInput | StorageError
return (Left NotFound)
```

### Regression tests

```haskell
assert (renderError NotFound == "not found")
```

## HS-H-091: space leak

- Difficulty: Hard
- Language/framework: Haskell / Haskell
- Perspective: Laziness
- Concept: space leak
- Symptom: A long-running fold consumes excessive memory.
- Diagnostic goal: Choose strict accumulation when the result must be evaluated incrementally.

### Buggy code

```haskell
sum = foldl (\a x -> a + x) 0 values
```

### Expected diagnosis

Lazy accumulation builds a chain of thunks instead of forcing each intermediate total.

### Corrected code

```haskell
sum = foldl' (+) 0 values
```

### Regression tests

```haskell
assert (sum [1..100] == 5050)
```

## HS-H-092: unsafe shared state

- Difficulty: Hard
- Language/framework: Haskell / Haskell
- Perspective: Purity
- Concept: unsafe shared state
- Symptom: A helper unexpectedly changes global state.
- Diagnostic goal: Make effects explicit in the type and call boundary.

### Buggy code

```haskell
counter = unsafePerformIO (newIORef 0)
```

### Expected diagnosis

unsafePerformIO hides mutation from the type system and can violate sharing assumptions.

### Corrected code

```haskell
counter :: IO (IORef Int)
counter = newIORef 0
```

### Regression tests

```haskell
-- Test through IO and assert the state transition explicitly.
```

## HS-H-093: partial pattern

- Difficulty: Hard
- Language/framework: Haskell / Haskell
- Perspective: Types
- Concept: partial pattern
- Symptom: An input causes a runtime exception.
- Diagnostic goal: Cover every constructor or make failure explicit.

### Buggy code

```haskell
headName (x:_) = name x
```

### Expected diagnosis

The empty-list pattern is missing, so [] triggers a non-exhaustive match.

### Corrected code

```haskell
headName [] = Nothing
headName (x:_) = Just (name x)
```

### Regression tests

```haskell
assert (headName [] == Nothing)
```

## HS-H-094: unsafe extraction

- Difficulty: Hard
- Language/framework: Haskell / Haskell
- Perspective: Maybe
- Concept: unsafe extraction
- Symptom: Missing configuration crashes startup.
- Diagnostic goal: Use maybe or bind the absence through the computation.

### Buggy code

```haskell
port = read (fromJust (lookup "port" config))
```

### Expected diagnosis

fromJust turns an expected missing-value case into an exception.

### Corrected code

```haskell
port = lookup "port" config >>= readMaybe
```

### Regression tests

```haskell
assert (port [] == Nothing)
```

## HS-H-095: lazy handle

- Difficulty: Hard
- Language/framework: Haskell / Haskell
- Perspective: IO
- Concept: lazy handle
- Symptom: A file is closed before lazy contents are consumed.
- Diagnostic goal: Force contents inside the resource lifetime or stream explicitly.

### Buggy code

```haskell
readLines path = withFile path ReadMode $ \h -> hGetContents h
```

### Expected diagnosis

Lazy hGetContents may defer reads until after withFile closes the handle.

### Corrected code

```haskell
readLines path = withFile path ReadMode $ \h -> hGetContents h >>= \s -> evaluate (length s) >> pure s
```

### Regression tests

```haskell
-- Test reading a complete file after the handle scope.
```

## HS-H-096: wrong bind

- Difficulty: Hard
- Language/framework: Haskell / Haskell
- Perspective: Monads
- Concept: wrong bind
- Symptom: A function receives an IO action instead of its value.
- Diagnostic goal: Use (>>=) or do notation at the effect boundary.

### Buggy code

```haskell
load = fetch >>= pure . parse
```

### Expected diagnosis

This is valid only if parse returns a pure value; mixing nested IO creates the wrong shape.

### Corrected code

```haskell
load = do
  raw <- fetch
  pure (parse raw)
```

### Regression tests

```haskell
assertIO load
```

## HS-H-097: quadratic append

- Difficulty: Hard
- Language/framework: Haskell / Haskell
- Perspective: Lists
- Concept: quadratic append
- Symptom: A list builder becomes slow for large input.
- Diagnostic goal: Prepend and reverse, or use a difference-list structure.

### Buggy code

```haskell
build xs = foldl (\acc x -> acc ++ [f x]) [] xs
```

### Expected diagnosis

Appending to the end copies the accumulated list on every iteration.

### Corrected code

```haskell
build xs = reverse (foldl (\acc x -> f x : acc) [] xs)
```

### Regression tests

```haskell
assert (build [1,2,3] == map f [1,2,3])
```

## HS-H-098: MVar deadlock

- Difficulty: Hard
- Language/framework: Haskell / Haskell
- Perspective: Concurrency
- Concept: MVar deadlock
- Symptom: Two workers wait forever.
- Diagnostic goal: Define lock ownership and always release it on exceptions.

### Buggy code

```haskell
withMVar lock $ \_ -> takeMVar lock
```

### Expected diagnosis

The same thread attempts to take a non-reentrant MVar twice.

### Corrected code

```haskell
withMVar lock $ \_ -> pure ()
```

### Regression tests

```haskell
-- Test completion with a timeout.
```

## HS-H-099: ambiguous instance

- Difficulty: Hard
- Language/framework: Haskell / Haskell
- Perspective: Typeclasses
- Concept: ambiguous instance
- Symptom: Compilation reports overlapping or ambiguous instances.
- Diagnostic goal: Keep instance selection coherent and use newtypes for distinct meanings.

### Buggy code

```haskell
instance Num a => Monoid a where mempty = 0
```

### Expected diagnosis

A broad orphan/overlapping instance conflicts with existing typeclass laws and instances.

### Corrected code

```haskell
newtype Sum a = Sum a
instance Num a => Semigroup (Sum a) where Sum a <> Sum b = Sum (a+b)
```

### Regression tests

```haskell
-- Compile with warnings as errors and test associativity.
```

## HS-H-100: stringly error

- Difficulty: Hard
- Language/framework: Haskell / Haskell
- Perspective: Errors
- Concept: stringly error
- Symptom: Callers cannot distinguish failure cases.
- Diagnostic goal: Use a sum type with stable constructors.

### Buggy code

```haskell
return (Left "not found")
```

### Expected diagnosis

String errors are fragile and force callers to inspect text.

### Corrected code

```haskell
data AppError = NotFound | InvalidInput | StorageError
return (Left NotFound)
```

### Regression tests

```haskell
assert (renderError NotFound == "not found")
```
