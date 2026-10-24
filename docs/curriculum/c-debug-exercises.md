# C Debug Exercises

A RAG-training corpus of 300 debugging exercises for C. Each record contains a framework-specific failure, diagnosis, corrected implementation, and regression guidance. Corrected code is editorial training material and must be stripped from learner-facing challenge responses.

## Coverage

- Easy: 100 exercises
- Medium: 100 exercises
- Hard: 100 exercises
- Perspectives: memory and ownership, concurrency, API contracts, persistence, validation, security, lifecycle, testing, and deployment

## C-E-001: off-by-one allocation

- Difficulty: Easy
- Language/platform: C
- Perspective: Memory safety
- Concept: off-by-one allocation
- Symptom: The last byte is overwritten.
- Diagnostic goal: Match allocation size to the largest valid index.

### Buggy code

```c
char *copy1(const char *s) {
    size_t n = strlen(s);
    char *out = malloc(n);
    memcpy(out, s, n + 1);
    return out;
}
```

### Expected diagnosis

The terminator requires n + 1 bytes; copying n + 1 bytes into n bytes is a heap overflow.

### Corrected code

```c
char *copy1(const char *s) {
    size_t n = strlen(s);
    char *out = malloc(n + 1);
    if (!out) return NULL;
    memcpy(out, s, n + 1);
    return out;
}
```

### Regression tests

```c
// Assert copy1("abc") is "abc" and allocation failure is handled.
```

## C-E-002: returning address of local

- Difficulty: Easy
- Language/platform: C
- Perspective: Pointer lifetime
- Concept: returning address of local
- Symptom: The caller reads garbage.
- Diagnostic goal: Ensure returned storage outlives the function.

### Buggy code

```c
int *value1(void) { int result = 7; return &result; }
```

### Expected diagnosis

A pointer to an automatic local object becomes invalid when the function returns.

### Corrected code

```c
int value1(void) { return 7; }
```

### Regression tests

```c
assert(value1() == 7);
```

## C-E-003: missing terminator

- Difficulty: Easy
- Language/platform: C
- Perspective: String API
- Concept: missing terminator
- Symptom: Printing reads beyond the buffer.
- Diagnostic goal: Reserve and write the C string terminator.

### Buggy code

```c
char name1[4];
memcpy(name1, "Ada", 3);
printf("%s", name1);
```

### Expected diagnosis

memcpy copies bytes only and does not append a terminator.

### Corrected code

```c
char name1[4];
memcpy(name1, "Ada", 3);
name1[3] = '\0';
```

### Regression tests

```c
assert(strcmp(name1, "Ada") == 0);
```

## C-E-004: signed overflow

- Difficulty: Easy
- Language/platform: C
- Perspective: Integer reasoning
- Concept: signed overflow
- Symptom: A boundary calculation produces undefined behavior.
- Diagnostic goal: Check before arithmetic or use an unsigned/wider representation.

### Buggy code

```c
int total1(int count, int size) { return count * size; }
```

### Expected diagnosis

Signed overflow is undefined in C; validating after the multiplication is too late.

### Corrected code

```c
bool total1(int count, int size, int *out) {
    if (count < 0 || size < 0 || count > INT_MAX / size) return false;
    *out = count * size;
    return true;
}
```

### Regression tests

```c
// Assert overflow returns false and a safe product returns true.
```

## C-E-005: double free

- Difficulty: Easy
- Language/platform: C
- Perspective: Ownership
- Concept: double free
- Symptom: The allocator reports corruption.
- Diagnostic goal: Assign ownership once and clear moved-from pointers.

### Buggy code

```c
void release1(char **p) { free(*p); free(*p); }
```

### Expected diagnosis

Freeing the same allocation twice is undefined behavior.

### Corrected code

```c
void release1(char **p) {
    if (p && *p) { free(*p); *p = NULL; }
}
```

### Regression tests

```c
// Call release1 twice; the second call is harmless.
```

## C-E-006: unchecked fopen

- Difficulty: Easy
- Language/platform: C
- Perspective: I/O contract
- Concept: unchecked fopen
- Symptom: A null FILE pointer is dereferenced.
- Diagnostic goal: Check resource acquisition before use.

### Buggy code

```c
FILE *f = fopen(path, "r");
char line[64];
fgets(line, sizeof line, f);
```

### Expected diagnosis

fopen returns NULL on failure; passing it to fgets is undefined behavior.

### Corrected code

```c
FILE *f = fopen(path, "r");
if (!f) return ERROR_OPEN;
char line[64];
if (!fgets(line, sizeof line, f)) { fclose(f); return ERROR_READ; }
fclose(f);
```

### Regression tests

```c
// Missing paths return an error without dereferencing NULL.
```

## C-E-007: data race

- Difficulty: Easy
- Language/platform: C
- Perspective: Concurrency
- Concept: data race
- Symptom: A counter loses increments under threads.
- Diagnostic goal: Synchronize shared mutable state.

### Buggy code

```c
shared_count1++;
```

### Expected diagnosis

Concurrent unsynchronized read-modify-write accesses form a data race and have undefined behavior.

### Corrected code

```c
pthread_mutex_lock(&count_mutex);
shared_count1++;
pthread_mutex_unlock(&count_mutex);
```

### Regression tests

```c
// Run two workers and assert the final count equals both contributions.
```

## C-E-008: scanf width omission

- Difficulty: Easy
- Language/platform: C
- Perspective: Parsing
- Concept: scanf width omission
- Symptom: Long input corrupts adjacent memory.
- Diagnostic goal: Bound formatted input by the destination capacity.

### Buggy code

```c
char word1[16];
scanf("%s", word1);
```

### Expected diagnosis

The conversion has no width limit, so input longer than 15 characters overflows the array.

### Corrected code

```c
char word1[16];
scanf("%15s", word1);
```

### Regression tests

```c
// A 100-character token must not overwrite memory.
```

## C-E-009: strncpy non-termination

- Difficulty: Easy
- Language/platform: C
- Perspective: API contract
- Concept: strncpy non-termination
- Symptom: The result is not a valid string for exact-length input.
- Diagnostic goal: Terminate explicitly after bounded copying.

### Buggy code

```c
strncpy(dst1, src1, sizeof dst1);
printf("%s", dst1);
```

### Expected diagnosis

strncpy does not append a terminator when the source fills the limit.

### Corrected code

```c
strncpy(dst1, src1, sizeof dst1 - 1);
dst1[sizeof dst1 - 1] = '\0';
```

### Regression tests

```c
// Exact-capacity source remains safely printable.
```

## C-E-010: early return leak

- Difficulty: Easy
- Language/platform: C
- Perspective: Cleanup
- Concept: early return leak
- Symptom: An error path leaks an allocation.
- Diagnostic goal: Centralize cleanup for all exits.

### Buggy code

```c
char *buffer = malloc(1024);
if (!buffer) return 0;
if (!read_data(buffer)) return -1;
free(buffer);
return 0;
```

### Expected diagnosis

The failed read returns before freeing buffer.

### Corrected code

```c
char *buffer = malloc(1024);
if (!buffer) return 0;
int result = read_data(buffer) ? 0 : -1;
free(buffer);
return result;
```

### Regression tests

```c
// Both read success and failure leave no allocation outstanding.
```

## C-E-011: off-by-one allocation

- Difficulty: Easy
- Language/platform: C
- Perspective: Memory safety
- Concept: off-by-one allocation
- Symptom: The last byte is overwritten.
- Diagnostic goal: Match allocation size to the largest valid index.

### Buggy code

```c
char *copy1(const char *s) {
    size_t n = strlen(s);
    char *out = malloc(n);
    memcpy(out, s, n + 1);
    return out;
}
```

### Expected diagnosis

The terminator requires n + 1 bytes; copying n + 1 bytes into n bytes is a heap overflow.

### Corrected code

```c
char *copy1(const char *s) {
    size_t n = strlen(s);
    char *out = malloc(n + 1);
    if (!out) return NULL;
    memcpy(out, s, n + 1);
    return out;
}
```

### Regression tests

```c
// Assert copy1("abc") is "abc" and allocation failure is handled.
```

## C-E-012: returning address of local

- Difficulty: Easy
- Language/platform: C
- Perspective: Pointer lifetime
- Concept: returning address of local
- Symptom: The caller reads garbage.
- Diagnostic goal: Ensure returned storage outlives the function.

### Buggy code

```c
int *value1(void) { int result = 7; return &result; }
```

### Expected diagnosis

A pointer to an automatic local object becomes invalid when the function returns.

### Corrected code

```c
int value1(void) { return 7; }
```

### Regression tests

```c
assert(value1() == 7);
```

## C-E-013: missing terminator

- Difficulty: Easy
- Language/platform: C
- Perspective: String API
- Concept: missing terminator
- Symptom: Printing reads beyond the buffer.
- Diagnostic goal: Reserve and write the C string terminator.

### Buggy code

```c
char name1[4];
memcpy(name1, "Ada", 3);
printf("%s", name1);
```

### Expected diagnosis

memcpy copies bytes only and does not append a terminator.

### Corrected code

```c
char name1[4];
memcpy(name1, "Ada", 3);
name1[3] = '\0';
```

### Regression tests

```c
assert(strcmp(name1, "Ada") == 0);
```

## C-E-014: signed overflow

- Difficulty: Easy
- Language/platform: C
- Perspective: Integer reasoning
- Concept: signed overflow
- Symptom: A boundary calculation produces undefined behavior.
- Diagnostic goal: Check before arithmetic or use an unsigned/wider representation.

### Buggy code

```c
int total1(int count, int size) { return count * size; }
```

### Expected diagnosis

Signed overflow is undefined in C; validating after the multiplication is too late.

### Corrected code

```c
bool total1(int count, int size, int *out) {
    if (count < 0 || size < 0 || count > INT_MAX / size) return false;
    *out = count * size;
    return true;
}
```

### Regression tests

```c
// Assert overflow returns false and a safe product returns true.
```

## C-E-015: double free

- Difficulty: Easy
- Language/platform: C
- Perspective: Ownership
- Concept: double free
- Symptom: The allocator reports corruption.
- Diagnostic goal: Assign ownership once and clear moved-from pointers.

### Buggy code

```c
void release1(char **p) { free(*p); free(*p); }
```

### Expected diagnosis

Freeing the same allocation twice is undefined behavior.

### Corrected code

```c
void release1(char **p) {
    if (p && *p) { free(*p); *p = NULL; }
}
```

### Regression tests

```c
// Call release1 twice; the second call is harmless.
```

## C-E-016: unchecked fopen

- Difficulty: Easy
- Language/platform: C
- Perspective: I/O contract
- Concept: unchecked fopen
- Symptom: A null FILE pointer is dereferenced.
- Diagnostic goal: Check resource acquisition before use.

### Buggy code

```c
FILE *f = fopen(path, "r");
char line[64];
fgets(line, sizeof line, f);
```

### Expected diagnosis

fopen returns NULL on failure; passing it to fgets is undefined behavior.

### Corrected code

```c
FILE *f = fopen(path, "r");
if (!f) return ERROR_OPEN;
char line[64];
if (!fgets(line, sizeof line, f)) { fclose(f); return ERROR_READ; }
fclose(f);
```

### Regression tests

```c
// Missing paths return an error without dereferencing NULL.
```

## C-E-017: data race

- Difficulty: Easy
- Language/platform: C
- Perspective: Concurrency
- Concept: data race
- Symptom: A counter loses increments under threads.
- Diagnostic goal: Synchronize shared mutable state.

### Buggy code

```c
shared_count1++;
```

### Expected diagnosis

Concurrent unsynchronized read-modify-write accesses form a data race and have undefined behavior.

### Corrected code

```c
pthread_mutex_lock(&count_mutex);
shared_count1++;
pthread_mutex_unlock(&count_mutex);
```

### Regression tests

```c
// Run two workers and assert the final count equals both contributions.
```

## C-E-018: scanf width omission

- Difficulty: Easy
- Language/platform: C
- Perspective: Parsing
- Concept: scanf width omission
- Symptom: Long input corrupts adjacent memory.
- Diagnostic goal: Bound formatted input by the destination capacity.

### Buggy code

```c
char word1[16];
scanf("%s", word1);
```

### Expected diagnosis

The conversion has no width limit, so input longer than 15 characters overflows the array.

### Corrected code

```c
char word1[16];
scanf("%15s", word1);
```

### Regression tests

```c
// A 100-character token must not overwrite memory.
```

## C-E-019: strncpy non-termination

- Difficulty: Easy
- Language/platform: C
- Perspective: API contract
- Concept: strncpy non-termination
- Symptom: The result is not a valid string for exact-length input.
- Diagnostic goal: Terminate explicitly after bounded copying.

### Buggy code

```c
strncpy(dst1, src1, sizeof dst1);
printf("%s", dst1);
```

### Expected diagnosis

strncpy does not append a terminator when the source fills the limit.

### Corrected code

```c
strncpy(dst1, src1, sizeof dst1 - 1);
dst1[sizeof dst1 - 1] = '\0';
```

### Regression tests

```c
// Exact-capacity source remains safely printable.
```

## C-E-020: early return leak

- Difficulty: Easy
- Language/platform: C
- Perspective: Cleanup
- Concept: early return leak
- Symptom: An error path leaks an allocation.
- Diagnostic goal: Centralize cleanup for all exits.

### Buggy code

```c
char *buffer = malloc(1024);
if (!buffer) return 0;
if (!read_data(buffer)) return -1;
free(buffer);
return 0;
```

### Expected diagnosis

The failed read returns before freeing buffer.

### Corrected code

```c
char *buffer = malloc(1024);
if (!buffer) return 0;
int result = read_data(buffer) ? 0 : -1;
free(buffer);
return result;
```

### Regression tests

```c
// Both read success and failure leave no allocation outstanding.
```

## C-E-021: off-by-one allocation

- Difficulty: Easy
- Language/platform: C
- Perspective: Memory safety
- Concept: off-by-one allocation
- Symptom: The last byte is overwritten.
- Diagnostic goal: Match allocation size to the largest valid index.

### Buggy code

```c
char *copy1(const char *s) {
    size_t n = strlen(s);
    char *out = malloc(n);
    memcpy(out, s, n + 1);
    return out;
}
```

### Expected diagnosis

The terminator requires n + 1 bytes; copying n + 1 bytes into n bytes is a heap overflow.

### Corrected code

```c
char *copy1(const char *s) {
    size_t n = strlen(s);
    char *out = malloc(n + 1);
    if (!out) return NULL;
    memcpy(out, s, n + 1);
    return out;
}
```

### Regression tests

```c
// Assert copy1("abc") is "abc" and allocation failure is handled.
```

## C-E-022: returning address of local

- Difficulty: Easy
- Language/platform: C
- Perspective: Pointer lifetime
- Concept: returning address of local
- Symptom: The caller reads garbage.
- Diagnostic goal: Ensure returned storage outlives the function.

### Buggy code

```c
int *value1(void) { int result = 7; return &result; }
```

### Expected diagnosis

A pointer to an automatic local object becomes invalid when the function returns.

### Corrected code

```c
int value1(void) { return 7; }
```

### Regression tests

```c
assert(value1() == 7);
```

## C-E-023: missing terminator

- Difficulty: Easy
- Language/platform: C
- Perspective: String API
- Concept: missing terminator
- Symptom: Printing reads beyond the buffer.
- Diagnostic goal: Reserve and write the C string terminator.

### Buggy code

```c
char name1[4];
memcpy(name1, "Ada", 3);
printf("%s", name1);
```

### Expected diagnosis

memcpy copies bytes only and does not append a terminator.

### Corrected code

```c
char name1[4];
memcpy(name1, "Ada", 3);
name1[3] = '\0';
```

### Regression tests

```c
assert(strcmp(name1, "Ada") == 0);
```

## C-E-024: signed overflow

- Difficulty: Easy
- Language/platform: C
- Perspective: Integer reasoning
- Concept: signed overflow
- Symptom: A boundary calculation produces undefined behavior.
- Diagnostic goal: Check before arithmetic or use an unsigned/wider representation.

### Buggy code

```c
int total1(int count, int size) { return count * size; }
```

### Expected diagnosis

Signed overflow is undefined in C; validating after the multiplication is too late.

### Corrected code

```c
bool total1(int count, int size, int *out) {
    if (count < 0 || size < 0 || count > INT_MAX / size) return false;
    *out = count * size;
    return true;
}
```

### Regression tests

```c
// Assert overflow returns false and a safe product returns true.
```

## C-E-025: double free

- Difficulty: Easy
- Language/platform: C
- Perspective: Ownership
- Concept: double free
- Symptom: The allocator reports corruption.
- Diagnostic goal: Assign ownership once and clear moved-from pointers.

### Buggy code

```c
void release1(char **p) { free(*p); free(*p); }
```

### Expected diagnosis

Freeing the same allocation twice is undefined behavior.

### Corrected code

```c
void release1(char **p) {
    if (p && *p) { free(*p); *p = NULL; }
}
```

### Regression tests

```c
// Call release1 twice; the second call is harmless.
```

## C-E-026: unchecked fopen

- Difficulty: Easy
- Language/platform: C
- Perspective: I/O contract
- Concept: unchecked fopen
- Symptom: A null FILE pointer is dereferenced.
- Diagnostic goal: Check resource acquisition before use.

### Buggy code

```c
FILE *f = fopen(path, "r");
char line[64];
fgets(line, sizeof line, f);
```

### Expected diagnosis

fopen returns NULL on failure; passing it to fgets is undefined behavior.

### Corrected code

```c
FILE *f = fopen(path, "r");
if (!f) return ERROR_OPEN;
char line[64];
if (!fgets(line, sizeof line, f)) { fclose(f); return ERROR_READ; }
fclose(f);
```

### Regression tests

```c
// Missing paths return an error without dereferencing NULL.
```

## C-E-027: data race

- Difficulty: Easy
- Language/platform: C
- Perspective: Concurrency
- Concept: data race
- Symptom: A counter loses increments under threads.
- Diagnostic goal: Synchronize shared mutable state.

### Buggy code

```c
shared_count1++;
```

### Expected diagnosis

Concurrent unsynchronized read-modify-write accesses form a data race and have undefined behavior.

### Corrected code

```c
pthread_mutex_lock(&count_mutex);
shared_count1++;
pthread_mutex_unlock(&count_mutex);
```

### Regression tests

```c
// Run two workers and assert the final count equals both contributions.
```

## C-E-028: scanf width omission

- Difficulty: Easy
- Language/platform: C
- Perspective: Parsing
- Concept: scanf width omission
- Symptom: Long input corrupts adjacent memory.
- Diagnostic goal: Bound formatted input by the destination capacity.

### Buggy code

```c
char word1[16];
scanf("%s", word1);
```

### Expected diagnosis

The conversion has no width limit, so input longer than 15 characters overflows the array.

### Corrected code

```c
char word1[16];
scanf("%15s", word1);
```

### Regression tests

```c
// A 100-character token must not overwrite memory.
```

## C-E-029: strncpy non-termination

- Difficulty: Easy
- Language/platform: C
- Perspective: API contract
- Concept: strncpy non-termination
- Symptom: The result is not a valid string for exact-length input.
- Diagnostic goal: Terminate explicitly after bounded copying.

### Buggy code

```c
strncpy(dst1, src1, sizeof dst1);
printf("%s", dst1);
```

### Expected diagnosis

strncpy does not append a terminator when the source fills the limit.

### Corrected code

```c
strncpy(dst1, src1, sizeof dst1 - 1);
dst1[sizeof dst1 - 1] = '\0';
```

### Regression tests

```c
// Exact-capacity source remains safely printable.
```

## C-E-030: early return leak

- Difficulty: Easy
- Language/platform: C
- Perspective: Cleanup
- Concept: early return leak
- Symptom: An error path leaks an allocation.
- Diagnostic goal: Centralize cleanup for all exits.

### Buggy code

```c
char *buffer = malloc(1024);
if (!buffer) return 0;
if (!read_data(buffer)) return -1;
free(buffer);
return 0;
```

### Expected diagnosis

The failed read returns before freeing buffer.

### Corrected code

```c
char *buffer = malloc(1024);
if (!buffer) return 0;
int result = read_data(buffer) ? 0 : -1;
free(buffer);
return result;
```

### Regression tests

```c
// Both read success and failure leave no allocation outstanding.
```

## C-E-031: off-by-one allocation

- Difficulty: Easy
- Language/platform: C
- Perspective: Memory safety
- Concept: off-by-one allocation
- Symptom: The last byte is overwritten.
- Diagnostic goal: Match allocation size to the largest valid index.

### Buggy code

```c
char *copy1(const char *s) {
    size_t n = strlen(s);
    char *out = malloc(n);
    memcpy(out, s, n + 1);
    return out;
}
```

### Expected diagnosis

The terminator requires n + 1 bytes; copying n + 1 bytes into n bytes is a heap overflow.

### Corrected code

```c
char *copy1(const char *s) {
    size_t n = strlen(s);
    char *out = malloc(n + 1);
    if (!out) return NULL;
    memcpy(out, s, n + 1);
    return out;
}
```

### Regression tests

```c
// Assert copy1("abc") is "abc" and allocation failure is handled.
```

## C-E-032: returning address of local

- Difficulty: Easy
- Language/platform: C
- Perspective: Pointer lifetime
- Concept: returning address of local
- Symptom: The caller reads garbage.
- Diagnostic goal: Ensure returned storage outlives the function.

### Buggy code

```c
int *value1(void) { int result = 7; return &result; }
```

### Expected diagnosis

A pointer to an automatic local object becomes invalid when the function returns.

### Corrected code

```c
int value1(void) { return 7; }
```

### Regression tests

```c
assert(value1() == 7);
```

## C-E-033: missing terminator

- Difficulty: Easy
- Language/platform: C
- Perspective: String API
- Concept: missing terminator
- Symptom: Printing reads beyond the buffer.
- Diagnostic goal: Reserve and write the C string terminator.

### Buggy code

```c
char name1[4];
memcpy(name1, "Ada", 3);
printf("%s", name1);
```

### Expected diagnosis

memcpy copies bytes only and does not append a terminator.

### Corrected code

```c
char name1[4];
memcpy(name1, "Ada", 3);
name1[3] = '\0';
```

### Regression tests

```c
assert(strcmp(name1, "Ada") == 0);
```

## C-E-034: signed overflow

- Difficulty: Easy
- Language/platform: C
- Perspective: Integer reasoning
- Concept: signed overflow
- Symptom: A boundary calculation produces undefined behavior.
- Diagnostic goal: Check before arithmetic or use an unsigned/wider representation.

### Buggy code

```c
int total1(int count, int size) { return count * size; }
```

### Expected diagnosis

Signed overflow is undefined in C; validating after the multiplication is too late.

### Corrected code

```c
bool total1(int count, int size, int *out) {
    if (count < 0 || size < 0 || count > INT_MAX / size) return false;
    *out = count * size;
    return true;
}
```

### Regression tests

```c
// Assert overflow returns false and a safe product returns true.
```

## C-E-035: double free

- Difficulty: Easy
- Language/platform: C
- Perspective: Ownership
- Concept: double free
- Symptom: The allocator reports corruption.
- Diagnostic goal: Assign ownership once and clear moved-from pointers.

### Buggy code

```c
void release1(char **p) { free(*p); free(*p); }
```

### Expected diagnosis

Freeing the same allocation twice is undefined behavior.

### Corrected code

```c
void release1(char **p) {
    if (p && *p) { free(*p); *p = NULL; }
}
```

### Regression tests

```c
// Call release1 twice; the second call is harmless.
```

## C-E-036: unchecked fopen

- Difficulty: Easy
- Language/platform: C
- Perspective: I/O contract
- Concept: unchecked fopen
- Symptom: A null FILE pointer is dereferenced.
- Diagnostic goal: Check resource acquisition before use.

### Buggy code

```c
FILE *f = fopen(path, "r");
char line[64];
fgets(line, sizeof line, f);
```

### Expected diagnosis

fopen returns NULL on failure; passing it to fgets is undefined behavior.

### Corrected code

```c
FILE *f = fopen(path, "r");
if (!f) return ERROR_OPEN;
char line[64];
if (!fgets(line, sizeof line, f)) { fclose(f); return ERROR_READ; }
fclose(f);
```

### Regression tests

```c
// Missing paths return an error without dereferencing NULL.
```

## C-E-037: data race

- Difficulty: Easy
- Language/platform: C
- Perspective: Concurrency
- Concept: data race
- Symptom: A counter loses increments under threads.
- Diagnostic goal: Synchronize shared mutable state.

### Buggy code

```c
shared_count1++;
```

### Expected diagnosis

Concurrent unsynchronized read-modify-write accesses form a data race and have undefined behavior.

### Corrected code

```c
pthread_mutex_lock(&count_mutex);
shared_count1++;
pthread_mutex_unlock(&count_mutex);
```

### Regression tests

```c
// Run two workers and assert the final count equals both contributions.
```

## C-E-038: scanf width omission

- Difficulty: Easy
- Language/platform: C
- Perspective: Parsing
- Concept: scanf width omission
- Symptom: Long input corrupts adjacent memory.
- Diagnostic goal: Bound formatted input by the destination capacity.

### Buggy code

```c
char word1[16];
scanf("%s", word1);
```

### Expected diagnosis

The conversion has no width limit, so input longer than 15 characters overflows the array.

### Corrected code

```c
char word1[16];
scanf("%15s", word1);
```

### Regression tests

```c
// A 100-character token must not overwrite memory.
```

## C-E-039: strncpy non-termination

- Difficulty: Easy
- Language/platform: C
- Perspective: API contract
- Concept: strncpy non-termination
- Symptom: The result is not a valid string for exact-length input.
- Diagnostic goal: Terminate explicitly after bounded copying.

### Buggy code

```c
strncpy(dst1, src1, sizeof dst1);
printf("%s", dst1);
```

### Expected diagnosis

strncpy does not append a terminator when the source fills the limit.

### Corrected code

```c
strncpy(dst1, src1, sizeof dst1 - 1);
dst1[sizeof dst1 - 1] = '\0';
```

### Regression tests

```c
// Exact-capacity source remains safely printable.
```

## C-E-040: early return leak

- Difficulty: Easy
- Language/platform: C
- Perspective: Cleanup
- Concept: early return leak
- Symptom: An error path leaks an allocation.
- Diagnostic goal: Centralize cleanup for all exits.

### Buggy code

```c
char *buffer = malloc(1024);
if (!buffer) return 0;
if (!read_data(buffer)) return -1;
free(buffer);
return 0;
```

### Expected diagnosis

The failed read returns before freeing buffer.

### Corrected code

```c
char *buffer = malloc(1024);
if (!buffer) return 0;
int result = read_data(buffer) ? 0 : -1;
free(buffer);
return result;
```

### Regression tests

```c
// Both read success and failure leave no allocation outstanding.
```

## C-E-041: off-by-one allocation

- Difficulty: Easy
- Language/platform: C
- Perspective: Memory safety
- Concept: off-by-one allocation
- Symptom: The last byte is overwritten.
- Diagnostic goal: Match allocation size to the largest valid index.

### Buggy code

```c
char *copy1(const char *s) {
    size_t n = strlen(s);
    char *out = malloc(n);
    memcpy(out, s, n + 1);
    return out;
}
```

### Expected diagnosis

The terminator requires n + 1 bytes; copying n + 1 bytes into n bytes is a heap overflow.

### Corrected code

```c
char *copy1(const char *s) {
    size_t n = strlen(s);
    char *out = malloc(n + 1);
    if (!out) return NULL;
    memcpy(out, s, n + 1);
    return out;
}
```

### Regression tests

```c
// Assert copy1("abc") is "abc" and allocation failure is handled.
```

## C-E-042: returning address of local

- Difficulty: Easy
- Language/platform: C
- Perspective: Pointer lifetime
- Concept: returning address of local
- Symptom: The caller reads garbage.
- Diagnostic goal: Ensure returned storage outlives the function.

### Buggy code

```c
int *value1(void) { int result = 7; return &result; }
```

### Expected diagnosis

A pointer to an automatic local object becomes invalid when the function returns.

### Corrected code

```c
int value1(void) { return 7; }
```

### Regression tests

```c
assert(value1() == 7);
```

## C-E-043: missing terminator

- Difficulty: Easy
- Language/platform: C
- Perspective: String API
- Concept: missing terminator
- Symptom: Printing reads beyond the buffer.
- Diagnostic goal: Reserve and write the C string terminator.

### Buggy code

```c
char name1[4];
memcpy(name1, "Ada", 3);
printf("%s", name1);
```

### Expected diagnosis

memcpy copies bytes only and does not append a terminator.

### Corrected code

```c
char name1[4];
memcpy(name1, "Ada", 3);
name1[3] = '\0';
```

### Regression tests

```c
assert(strcmp(name1, "Ada") == 0);
```

## C-E-044: signed overflow

- Difficulty: Easy
- Language/platform: C
- Perspective: Integer reasoning
- Concept: signed overflow
- Symptom: A boundary calculation produces undefined behavior.
- Diagnostic goal: Check before arithmetic or use an unsigned/wider representation.

### Buggy code

```c
int total1(int count, int size) { return count * size; }
```

### Expected diagnosis

Signed overflow is undefined in C; validating after the multiplication is too late.

### Corrected code

```c
bool total1(int count, int size, int *out) {
    if (count < 0 || size < 0 || count > INT_MAX / size) return false;
    *out = count * size;
    return true;
}
```

### Regression tests

```c
// Assert overflow returns false and a safe product returns true.
```

## C-E-045: double free

- Difficulty: Easy
- Language/platform: C
- Perspective: Ownership
- Concept: double free
- Symptom: The allocator reports corruption.
- Diagnostic goal: Assign ownership once and clear moved-from pointers.

### Buggy code

```c
void release1(char **p) { free(*p); free(*p); }
```

### Expected diagnosis

Freeing the same allocation twice is undefined behavior.

### Corrected code

```c
void release1(char **p) {
    if (p && *p) { free(*p); *p = NULL; }
}
```

### Regression tests

```c
// Call release1 twice; the second call is harmless.
```

## C-E-046: unchecked fopen

- Difficulty: Easy
- Language/platform: C
- Perspective: I/O contract
- Concept: unchecked fopen
- Symptom: A null FILE pointer is dereferenced.
- Diagnostic goal: Check resource acquisition before use.

### Buggy code

```c
FILE *f = fopen(path, "r");
char line[64];
fgets(line, sizeof line, f);
```

### Expected diagnosis

fopen returns NULL on failure; passing it to fgets is undefined behavior.

### Corrected code

```c
FILE *f = fopen(path, "r");
if (!f) return ERROR_OPEN;
char line[64];
if (!fgets(line, sizeof line, f)) { fclose(f); return ERROR_READ; }
fclose(f);
```

### Regression tests

```c
// Missing paths return an error without dereferencing NULL.
```

## C-E-047: data race

- Difficulty: Easy
- Language/platform: C
- Perspective: Concurrency
- Concept: data race
- Symptom: A counter loses increments under threads.
- Diagnostic goal: Synchronize shared mutable state.

### Buggy code

```c
shared_count1++;
```

### Expected diagnosis

Concurrent unsynchronized read-modify-write accesses form a data race and have undefined behavior.

### Corrected code

```c
pthread_mutex_lock(&count_mutex);
shared_count1++;
pthread_mutex_unlock(&count_mutex);
```

### Regression tests

```c
// Run two workers and assert the final count equals both contributions.
```

## C-E-048: scanf width omission

- Difficulty: Easy
- Language/platform: C
- Perspective: Parsing
- Concept: scanf width omission
- Symptom: Long input corrupts adjacent memory.
- Diagnostic goal: Bound formatted input by the destination capacity.

### Buggy code

```c
char word1[16];
scanf("%s", word1);
```

### Expected diagnosis

The conversion has no width limit, so input longer than 15 characters overflows the array.

### Corrected code

```c
char word1[16];
scanf("%15s", word1);
```

### Regression tests

```c
// A 100-character token must not overwrite memory.
```

## C-E-049: strncpy non-termination

- Difficulty: Easy
- Language/platform: C
- Perspective: API contract
- Concept: strncpy non-termination
- Symptom: The result is not a valid string for exact-length input.
- Diagnostic goal: Terminate explicitly after bounded copying.

### Buggy code

```c
strncpy(dst1, src1, sizeof dst1);
printf("%s", dst1);
```

### Expected diagnosis

strncpy does not append a terminator when the source fills the limit.

### Corrected code

```c
strncpy(dst1, src1, sizeof dst1 - 1);
dst1[sizeof dst1 - 1] = '\0';
```

### Regression tests

```c
// Exact-capacity source remains safely printable.
```

## C-E-050: early return leak

- Difficulty: Easy
- Language/platform: C
- Perspective: Cleanup
- Concept: early return leak
- Symptom: An error path leaks an allocation.
- Diagnostic goal: Centralize cleanup for all exits.

### Buggy code

```c
char *buffer = malloc(1024);
if (!buffer) return 0;
if (!read_data(buffer)) return -1;
free(buffer);
return 0;
```

### Expected diagnosis

The failed read returns before freeing buffer.

### Corrected code

```c
char *buffer = malloc(1024);
if (!buffer) return 0;
int result = read_data(buffer) ? 0 : -1;
free(buffer);
return result;
```

### Regression tests

```c
// Both read success and failure leave no allocation outstanding.
```

## C-E-051: off-by-one allocation

- Difficulty: Easy
- Language/platform: C
- Perspective: Memory safety
- Concept: off-by-one allocation
- Symptom: The last byte is overwritten.
- Diagnostic goal: Match allocation size to the largest valid index.

### Buggy code

```c
char *copy1(const char *s) {
    size_t n = strlen(s);
    char *out = malloc(n);
    memcpy(out, s, n + 1);
    return out;
}
```

### Expected diagnosis

The terminator requires n + 1 bytes; copying n + 1 bytes into n bytes is a heap overflow.

### Corrected code

```c
char *copy1(const char *s) {
    size_t n = strlen(s);
    char *out = malloc(n + 1);
    if (!out) return NULL;
    memcpy(out, s, n + 1);
    return out;
}
```

### Regression tests

```c
// Assert copy1("abc") is "abc" and allocation failure is handled.
```

## C-E-052: returning address of local

- Difficulty: Easy
- Language/platform: C
- Perspective: Pointer lifetime
- Concept: returning address of local
- Symptom: The caller reads garbage.
- Diagnostic goal: Ensure returned storage outlives the function.

### Buggy code

```c
int *value1(void) { int result = 7; return &result; }
```

### Expected diagnosis

A pointer to an automatic local object becomes invalid when the function returns.

### Corrected code

```c
int value1(void) { return 7; }
```

### Regression tests

```c
assert(value1() == 7);
```

## C-E-053: missing terminator

- Difficulty: Easy
- Language/platform: C
- Perspective: String API
- Concept: missing terminator
- Symptom: Printing reads beyond the buffer.
- Diagnostic goal: Reserve and write the C string terminator.

### Buggy code

```c
char name1[4];
memcpy(name1, "Ada", 3);
printf("%s", name1);
```

### Expected diagnosis

memcpy copies bytes only and does not append a terminator.

### Corrected code

```c
char name1[4];
memcpy(name1, "Ada", 3);
name1[3] = '\0';
```

### Regression tests

```c
assert(strcmp(name1, "Ada") == 0);
```

## C-E-054: signed overflow

- Difficulty: Easy
- Language/platform: C
- Perspective: Integer reasoning
- Concept: signed overflow
- Symptom: A boundary calculation produces undefined behavior.
- Diagnostic goal: Check before arithmetic or use an unsigned/wider representation.

### Buggy code

```c
int total1(int count, int size) { return count * size; }
```

### Expected diagnosis

Signed overflow is undefined in C; validating after the multiplication is too late.

### Corrected code

```c
bool total1(int count, int size, int *out) {
    if (count < 0 || size < 0 || count > INT_MAX / size) return false;
    *out = count * size;
    return true;
}
```

### Regression tests

```c
// Assert overflow returns false and a safe product returns true.
```

## C-E-055: double free

- Difficulty: Easy
- Language/platform: C
- Perspective: Ownership
- Concept: double free
- Symptom: The allocator reports corruption.
- Diagnostic goal: Assign ownership once and clear moved-from pointers.

### Buggy code

```c
void release1(char **p) { free(*p); free(*p); }
```

### Expected diagnosis

Freeing the same allocation twice is undefined behavior.

### Corrected code

```c
void release1(char **p) {
    if (p && *p) { free(*p); *p = NULL; }
}
```

### Regression tests

```c
// Call release1 twice; the second call is harmless.
```

## C-E-056: unchecked fopen

- Difficulty: Easy
- Language/platform: C
- Perspective: I/O contract
- Concept: unchecked fopen
- Symptom: A null FILE pointer is dereferenced.
- Diagnostic goal: Check resource acquisition before use.

### Buggy code

```c
FILE *f = fopen(path, "r");
char line[64];
fgets(line, sizeof line, f);
```

### Expected diagnosis

fopen returns NULL on failure; passing it to fgets is undefined behavior.

### Corrected code

```c
FILE *f = fopen(path, "r");
if (!f) return ERROR_OPEN;
char line[64];
if (!fgets(line, sizeof line, f)) { fclose(f); return ERROR_READ; }
fclose(f);
```

### Regression tests

```c
// Missing paths return an error without dereferencing NULL.
```

## C-E-057: data race

- Difficulty: Easy
- Language/platform: C
- Perspective: Concurrency
- Concept: data race
- Symptom: A counter loses increments under threads.
- Diagnostic goal: Synchronize shared mutable state.

### Buggy code

```c
shared_count1++;
```

### Expected diagnosis

Concurrent unsynchronized read-modify-write accesses form a data race and have undefined behavior.

### Corrected code

```c
pthread_mutex_lock(&count_mutex);
shared_count1++;
pthread_mutex_unlock(&count_mutex);
```

### Regression tests

```c
// Run two workers and assert the final count equals both contributions.
```

## C-E-058: scanf width omission

- Difficulty: Easy
- Language/platform: C
- Perspective: Parsing
- Concept: scanf width omission
- Symptom: Long input corrupts adjacent memory.
- Diagnostic goal: Bound formatted input by the destination capacity.

### Buggy code

```c
char word1[16];
scanf("%s", word1);
```

### Expected diagnosis

The conversion has no width limit, so input longer than 15 characters overflows the array.

### Corrected code

```c
char word1[16];
scanf("%15s", word1);
```

### Regression tests

```c
// A 100-character token must not overwrite memory.
```

## C-E-059: strncpy non-termination

- Difficulty: Easy
- Language/platform: C
- Perspective: API contract
- Concept: strncpy non-termination
- Symptom: The result is not a valid string for exact-length input.
- Diagnostic goal: Terminate explicitly after bounded copying.

### Buggy code

```c
strncpy(dst1, src1, sizeof dst1);
printf("%s", dst1);
```

### Expected diagnosis

strncpy does not append a terminator when the source fills the limit.

### Corrected code

```c
strncpy(dst1, src1, sizeof dst1 - 1);
dst1[sizeof dst1 - 1] = '\0';
```

### Regression tests

```c
// Exact-capacity source remains safely printable.
```

## C-E-060: early return leak

- Difficulty: Easy
- Language/platform: C
- Perspective: Cleanup
- Concept: early return leak
- Symptom: An error path leaks an allocation.
- Diagnostic goal: Centralize cleanup for all exits.

### Buggy code

```c
char *buffer = malloc(1024);
if (!buffer) return 0;
if (!read_data(buffer)) return -1;
free(buffer);
return 0;
```

### Expected diagnosis

The failed read returns before freeing buffer.

### Corrected code

```c
char *buffer = malloc(1024);
if (!buffer) return 0;
int result = read_data(buffer) ? 0 : -1;
free(buffer);
return result;
```

### Regression tests

```c
// Both read success and failure leave no allocation outstanding.
```

## C-E-061: off-by-one allocation

- Difficulty: Easy
- Language/platform: C
- Perspective: Memory safety
- Concept: off-by-one allocation
- Symptom: The last byte is overwritten.
- Diagnostic goal: Match allocation size to the largest valid index.

### Buggy code

```c
char *copy1(const char *s) {
    size_t n = strlen(s);
    char *out = malloc(n);
    memcpy(out, s, n + 1);
    return out;
}
```

### Expected diagnosis

The terminator requires n + 1 bytes; copying n + 1 bytes into n bytes is a heap overflow.

### Corrected code

```c
char *copy1(const char *s) {
    size_t n = strlen(s);
    char *out = malloc(n + 1);
    if (!out) return NULL;
    memcpy(out, s, n + 1);
    return out;
}
```

### Regression tests

```c
// Assert copy1("abc") is "abc" and allocation failure is handled.
```

## C-E-062: returning address of local

- Difficulty: Easy
- Language/platform: C
- Perspective: Pointer lifetime
- Concept: returning address of local
- Symptom: The caller reads garbage.
- Diagnostic goal: Ensure returned storage outlives the function.

### Buggy code

```c
int *value1(void) { int result = 7; return &result; }
```

### Expected diagnosis

A pointer to an automatic local object becomes invalid when the function returns.

### Corrected code

```c
int value1(void) { return 7; }
```

### Regression tests

```c
assert(value1() == 7);
```

## C-E-063: missing terminator

- Difficulty: Easy
- Language/platform: C
- Perspective: String API
- Concept: missing terminator
- Symptom: Printing reads beyond the buffer.
- Diagnostic goal: Reserve and write the C string terminator.

### Buggy code

```c
char name1[4];
memcpy(name1, "Ada", 3);
printf("%s", name1);
```

### Expected diagnosis

memcpy copies bytes only and does not append a terminator.

### Corrected code

```c
char name1[4];
memcpy(name1, "Ada", 3);
name1[3] = '\0';
```

### Regression tests

```c
assert(strcmp(name1, "Ada") == 0);
```

## C-E-064: signed overflow

- Difficulty: Easy
- Language/platform: C
- Perspective: Integer reasoning
- Concept: signed overflow
- Symptom: A boundary calculation produces undefined behavior.
- Diagnostic goal: Check before arithmetic or use an unsigned/wider representation.

### Buggy code

```c
int total1(int count, int size) { return count * size; }
```

### Expected diagnosis

Signed overflow is undefined in C; validating after the multiplication is too late.

### Corrected code

```c
bool total1(int count, int size, int *out) {
    if (count < 0 || size < 0 || count > INT_MAX / size) return false;
    *out = count * size;
    return true;
}
```

### Regression tests

```c
// Assert overflow returns false and a safe product returns true.
```

## C-E-065: double free

- Difficulty: Easy
- Language/platform: C
- Perspective: Ownership
- Concept: double free
- Symptom: The allocator reports corruption.
- Diagnostic goal: Assign ownership once and clear moved-from pointers.

### Buggy code

```c
void release1(char **p) { free(*p); free(*p); }
```

### Expected diagnosis

Freeing the same allocation twice is undefined behavior.

### Corrected code

```c
void release1(char **p) {
    if (p && *p) { free(*p); *p = NULL; }
}
```

### Regression tests

```c
// Call release1 twice; the second call is harmless.
```

## C-E-066: unchecked fopen

- Difficulty: Easy
- Language/platform: C
- Perspective: I/O contract
- Concept: unchecked fopen
- Symptom: A null FILE pointer is dereferenced.
- Diagnostic goal: Check resource acquisition before use.

### Buggy code

```c
FILE *f = fopen(path, "r");
char line[64];
fgets(line, sizeof line, f);
```

### Expected diagnosis

fopen returns NULL on failure; passing it to fgets is undefined behavior.

### Corrected code

```c
FILE *f = fopen(path, "r");
if (!f) return ERROR_OPEN;
char line[64];
if (!fgets(line, sizeof line, f)) { fclose(f); return ERROR_READ; }
fclose(f);
```

### Regression tests

```c
// Missing paths return an error without dereferencing NULL.
```

## C-E-067: data race

- Difficulty: Easy
- Language/platform: C
- Perspective: Concurrency
- Concept: data race
- Symptom: A counter loses increments under threads.
- Diagnostic goal: Synchronize shared mutable state.

### Buggy code

```c
shared_count1++;
```

### Expected diagnosis

Concurrent unsynchronized read-modify-write accesses form a data race and have undefined behavior.

### Corrected code

```c
pthread_mutex_lock(&count_mutex);
shared_count1++;
pthread_mutex_unlock(&count_mutex);
```

### Regression tests

```c
// Run two workers and assert the final count equals both contributions.
```

## C-E-068: scanf width omission

- Difficulty: Easy
- Language/platform: C
- Perspective: Parsing
- Concept: scanf width omission
- Symptom: Long input corrupts adjacent memory.
- Diagnostic goal: Bound formatted input by the destination capacity.

### Buggy code

```c
char word1[16];
scanf("%s", word1);
```

### Expected diagnosis

The conversion has no width limit, so input longer than 15 characters overflows the array.

### Corrected code

```c
char word1[16];
scanf("%15s", word1);
```

### Regression tests

```c
// A 100-character token must not overwrite memory.
```

## C-E-069: strncpy non-termination

- Difficulty: Easy
- Language/platform: C
- Perspective: API contract
- Concept: strncpy non-termination
- Symptom: The result is not a valid string for exact-length input.
- Diagnostic goal: Terminate explicitly after bounded copying.

### Buggy code

```c
strncpy(dst1, src1, sizeof dst1);
printf("%s", dst1);
```

### Expected diagnosis

strncpy does not append a terminator when the source fills the limit.

### Corrected code

```c
strncpy(dst1, src1, sizeof dst1 - 1);
dst1[sizeof dst1 - 1] = '\0';
```

### Regression tests

```c
// Exact-capacity source remains safely printable.
```

## C-E-070: early return leak

- Difficulty: Easy
- Language/platform: C
- Perspective: Cleanup
- Concept: early return leak
- Symptom: An error path leaks an allocation.
- Diagnostic goal: Centralize cleanup for all exits.

### Buggy code

```c
char *buffer = malloc(1024);
if (!buffer) return 0;
if (!read_data(buffer)) return -1;
free(buffer);
return 0;
```

### Expected diagnosis

The failed read returns before freeing buffer.

### Corrected code

```c
char *buffer = malloc(1024);
if (!buffer) return 0;
int result = read_data(buffer) ? 0 : -1;
free(buffer);
return result;
```

### Regression tests

```c
// Both read success and failure leave no allocation outstanding.
```

## C-E-071: off-by-one allocation

- Difficulty: Easy
- Language/platform: C
- Perspective: Memory safety
- Concept: off-by-one allocation
- Symptom: The last byte is overwritten.
- Diagnostic goal: Match allocation size to the largest valid index.

### Buggy code

```c
char *copy1(const char *s) {
    size_t n = strlen(s);
    char *out = malloc(n);
    memcpy(out, s, n + 1);
    return out;
}
```

### Expected diagnosis

The terminator requires n + 1 bytes; copying n + 1 bytes into n bytes is a heap overflow.

### Corrected code

```c
char *copy1(const char *s) {
    size_t n = strlen(s);
    char *out = malloc(n + 1);
    if (!out) return NULL;
    memcpy(out, s, n + 1);
    return out;
}
```

### Regression tests

```c
// Assert copy1("abc") is "abc" and allocation failure is handled.
```

## C-E-072: returning address of local

- Difficulty: Easy
- Language/platform: C
- Perspective: Pointer lifetime
- Concept: returning address of local
- Symptom: The caller reads garbage.
- Diagnostic goal: Ensure returned storage outlives the function.

### Buggy code

```c
int *value1(void) { int result = 7; return &result; }
```

### Expected diagnosis

A pointer to an automatic local object becomes invalid when the function returns.

### Corrected code

```c
int value1(void) { return 7; }
```

### Regression tests

```c
assert(value1() == 7);
```

## C-E-073: missing terminator

- Difficulty: Easy
- Language/platform: C
- Perspective: String API
- Concept: missing terminator
- Symptom: Printing reads beyond the buffer.
- Diagnostic goal: Reserve and write the C string terminator.

### Buggy code

```c
char name1[4];
memcpy(name1, "Ada", 3);
printf("%s", name1);
```

### Expected diagnosis

memcpy copies bytes only and does not append a terminator.

### Corrected code

```c
char name1[4];
memcpy(name1, "Ada", 3);
name1[3] = '\0';
```

### Regression tests

```c
assert(strcmp(name1, "Ada") == 0);
```

## C-E-074: signed overflow

- Difficulty: Easy
- Language/platform: C
- Perspective: Integer reasoning
- Concept: signed overflow
- Symptom: A boundary calculation produces undefined behavior.
- Diagnostic goal: Check before arithmetic or use an unsigned/wider representation.

### Buggy code

```c
int total1(int count, int size) { return count * size; }
```

### Expected diagnosis

Signed overflow is undefined in C; validating after the multiplication is too late.

### Corrected code

```c
bool total1(int count, int size, int *out) {
    if (count < 0 || size < 0 || count > INT_MAX / size) return false;
    *out = count * size;
    return true;
}
```

### Regression tests

```c
// Assert overflow returns false and a safe product returns true.
```

## C-E-075: double free

- Difficulty: Easy
- Language/platform: C
- Perspective: Ownership
- Concept: double free
- Symptom: The allocator reports corruption.
- Diagnostic goal: Assign ownership once and clear moved-from pointers.

### Buggy code

```c
void release1(char **p) { free(*p); free(*p); }
```

### Expected diagnosis

Freeing the same allocation twice is undefined behavior.

### Corrected code

```c
void release1(char **p) {
    if (p && *p) { free(*p); *p = NULL; }
}
```

### Regression tests

```c
// Call release1 twice; the second call is harmless.
```

## C-E-076: unchecked fopen

- Difficulty: Easy
- Language/platform: C
- Perspective: I/O contract
- Concept: unchecked fopen
- Symptom: A null FILE pointer is dereferenced.
- Diagnostic goal: Check resource acquisition before use.

### Buggy code

```c
FILE *f = fopen(path, "r");
char line[64];
fgets(line, sizeof line, f);
```

### Expected diagnosis

fopen returns NULL on failure; passing it to fgets is undefined behavior.

### Corrected code

```c
FILE *f = fopen(path, "r");
if (!f) return ERROR_OPEN;
char line[64];
if (!fgets(line, sizeof line, f)) { fclose(f); return ERROR_READ; }
fclose(f);
```

### Regression tests

```c
// Missing paths return an error without dereferencing NULL.
```

## C-E-077: data race

- Difficulty: Easy
- Language/platform: C
- Perspective: Concurrency
- Concept: data race
- Symptom: A counter loses increments under threads.
- Diagnostic goal: Synchronize shared mutable state.

### Buggy code

```c
shared_count1++;
```

### Expected diagnosis

Concurrent unsynchronized read-modify-write accesses form a data race and have undefined behavior.

### Corrected code

```c
pthread_mutex_lock(&count_mutex);
shared_count1++;
pthread_mutex_unlock(&count_mutex);
```

### Regression tests

```c
// Run two workers and assert the final count equals both contributions.
```

## C-E-078: scanf width omission

- Difficulty: Easy
- Language/platform: C
- Perspective: Parsing
- Concept: scanf width omission
- Symptom: Long input corrupts adjacent memory.
- Diagnostic goal: Bound formatted input by the destination capacity.

### Buggy code

```c
char word1[16];
scanf("%s", word1);
```

### Expected diagnosis

The conversion has no width limit, so input longer than 15 characters overflows the array.

### Corrected code

```c
char word1[16];
scanf("%15s", word1);
```

### Regression tests

```c
// A 100-character token must not overwrite memory.
```

## C-E-079: strncpy non-termination

- Difficulty: Easy
- Language/platform: C
- Perspective: API contract
- Concept: strncpy non-termination
- Symptom: The result is not a valid string for exact-length input.
- Diagnostic goal: Terminate explicitly after bounded copying.

### Buggy code

```c
strncpy(dst1, src1, sizeof dst1);
printf("%s", dst1);
```

### Expected diagnosis

strncpy does not append a terminator when the source fills the limit.

### Corrected code

```c
strncpy(dst1, src1, sizeof dst1 - 1);
dst1[sizeof dst1 - 1] = '\0';
```

### Regression tests

```c
// Exact-capacity source remains safely printable.
```

## C-E-080: early return leak

- Difficulty: Easy
- Language/platform: C
- Perspective: Cleanup
- Concept: early return leak
- Symptom: An error path leaks an allocation.
- Diagnostic goal: Centralize cleanup for all exits.

### Buggy code

```c
char *buffer = malloc(1024);
if (!buffer) return 0;
if (!read_data(buffer)) return -1;
free(buffer);
return 0;
```

### Expected diagnosis

The failed read returns before freeing buffer.

### Corrected code

```c
char *buffer = malloc(1024);
if (!buffer) return 0;
int result = read_data(buffer) ? 0 : -1;
free(buffer);
return result;
```

### Regression tests

```c
// Both read success and failure leave no allocation outstanding.
```

## C-E-081: off-by-one allocation

- Difficulty: Easy
- Language/platform: C
- Perspective: Memory safety
- Concept: off-by-one allocation
- Symptom: The last byte is overwritten.
- Diagnostic goal: Match allocation size to the largest valid index.

### Buggy code

```c
char *copy1(const char *s) {
    size_t n = strlen(s);
    char *out = malloc(n);
    memcpy(out, s, n + 1);
    return out;
}
```

### Expected diagnosis

The terminator requires n + 1 bytes; copying n + 1 bytes into n bytes is a heap overflow.

### Corrected code

```c
char *copy1(const char *s) {
    size_t n = strlen(s);
    char *out = malloc(n + 1);
    if (!out) return NULL;
    memcpy(out, s, n + 1);
    return out;
}
```

### Regression tests

```c
// Assert copy1("abc") is "abc" and allocation failure is handled.
```

## C-E-082: returning address of local

- Difficulty: Easy
- Language/platform: C
- Perspective: Pointer lifetime
- Concept: returning address of local
- Symptom: The caller reads garbage.
- Diagnostic goal: Ensure returned storage outlives the function.

### Buggy code

```c
int *value1(void) { int result = 7; return &result; }
```

### Expected diagnosis

A pointer to an automatic local object becomes invalid when the function returns.

### Corrected code

```c
int value1(void) { return 7; }
```

### Regression tests

```c
assert(value1() == 7);
```

## C-E-083: missing terminator

- Difficulty: Easy
- Language/platform: C
- Perspective: String API
- Concept: missing terminator
- Symptom: Printing reads beyond the buffer.
- Diagnostic goal: Reserve and write the C string terminator.

### Buggy code

```c
char name1[4];
memcpy(name1, "Ada", 3);
printf("%s", name1);
```

### Expected diagnosis

memcpy copies bytes only and does not append a terminator.

### Corrected code

```c
char name1[4];
memcpy(name1, "Ada", 3);
name1[3] = '\0';
```

### Regression tests

```c
assert(strcmp(name1, "Ada") == 0);
```

## C-E-084: signed overflow

- Difficulty: Easy
- Language/platform: C
- Perspective: Integer reasoning
- Concept: signed overflow
- Symptom: A boundary calculation produces undefined behavior.
- Diagnostic goal: Check before arithmetic or use an unsigned/wider representation.

### Buggy code

```c
int total1(int count, int size) { return count * size; }
```

### Expected diagnosis

Signed overflow is undefined in C; validating after the multiplication is too late.

### Corrected code

```c
bool total1(int count, int size, int *out) {
    if (count < 0 || size < 0 || count > INT_MAX / size) return false;
    *out = count * size;
    return true;
}
```

### Regression tests

```c
// Assert overflow returns false and a safe product returns true.
```

## C-E-085: double free

- Difficulty: Easy
- Language/platform: C
- Perspective: Ownership
- Concept: double free
- Symptom: The allocator reports corruption.
- Diagnostic goal: Assign ownership once and clear moved-from pointers.

### Buggy code

```c
void release1(char **p) { free(*p); free(*p); }
```

### Expected diagnosis

Freeing the same allocation twice is undefined behavior.

### Corrected code

```c
void release1(char **p) {
    if (p && *p) { free(*p); *p = NULL; }
}
```

### Regression tests

```c
// Call release1 twice; the second call is harmless.
```

## C-E-086: unchecked fopen

- Difficulty: Easy
- Language/platform: C
- Perspective: I/O contract
- Concept: unchecked fopen
- Symptom: A null FILE pointer is dereferenced.
- Diagnostic goal: Check resource acquisition before use.

### Buggy code

```c
FILE *f = fopen(path, "r");
char line[64];
fgets(line, sizeof line, f);
```

### Expected diagnosis

fopen returns NULL on failure; passing it to fgets is undefined behavior.

### Corrected code

```c
FILE *f = fopen(path, "r");
if (!f) return ERROR_OPEN;
char line[64];
if (!fgets(line, sizeof line, f)) { fclose(f); return ERROR_READ; }
fclose(f);
```

### Regression tests

```c
// Missing paths return an error without dereferencing NULL.
```

## C-E-087: data race

- Difficulty: Easy
- Language/platform: C
- Perspective: Concurrency
- Concept: data race
- Symptom: A counter loses increments under threads.
- Diagnostic goal: Synchronize shared mutable state.

### Buggy code

```c
shared_count1++;
```

### Expected diagnosis

Concurrent unsynchronized read-modify-write accesses form a data race and have undefined behavior.

### Corrected code

```c
pthread_mutex_lock(&count_mutex);
shared_count1++;
pthread_mutex_unlock(&count_mutex);
```

### Regression tests

```c
// Run two workers and assert the final count equals both contributions.
```

## C-E-088: scanf width omission

- Difficulty: Easy
- Language/platform: C
- Perspective: Parsing
- Concept: scanf width omission
- Symptom: Long input corrupts adjacent memory.
- Diagnostic goal: Bound formatted input by the destination capacity.

### Buggy code

```c
char word1[16];
scanf("%s", word1);
```

### Expected diagnosis

The conversion has no width limit, so input longer than 15 characters overflows the array.

### Corrected code

```c
char word1[16];
scanf("%15s", word1);
```

### Regression tests

```c
// A 100-character token must not overwrite memory.
```

## C-E-089: strncpy non-termination

- Difficulty: Easy
- Language/platform: C
- Perspective: API contract
- Concept: strncpy non-termination
- Symptom: The result is not a valid string for exact-length input.
- Diagnostic goal: Terminate explicitly after bounded copying.

### Buggy code

```c
strncpy(dst1, src1, sizeof dst1);
printf("%s", dst1);
```

### Expected diagnosis

strncpy does not append a terminator when the source fills the limit.

### Corrected code

```c
strncpy(dst1, src1, sizeof dst1 - 1);
dst1[sizeof dst1 - 1] = '\0';
```

### Regression tests

```c
// Exact-capacity source remains safely printable.
```

## C-E-090: early return leak

- Difficulty: Easy
- Language/platform: C
- Perspective: Cleanup
- Concept: early return leak
- Symptom: An error path leaks an allocation.
- Diagnostic goal: Centralize cleanup for all exits.

### Buggy code

```c
char *buffer = malloc(1024);
if (!buffer) return 0;
if (!read_data(buffer)) return -1;
free(buffer);
return 0;
```

### Expected diagnosis

The failed read returns before freeing buffer.

### Corrected code

```c
char *buffer = malloc(1024);
if (!buffer) return 0;
int result = read_data(buffer) ? 0 : -1;
free(buffer);
return result;
```

### Regression tests

```c
// Both read success and failure leave no allocation outstanding.
```

## C-E-091: off-by-one allocation

- Difficulty: Easy
- Language/platform: C
- Perspective: Memory safety
- Concept: off-by-one allocation
- Symptom: The last byte is overwritten.
- Diagnostic goal: Match allocation size to the largest valid index.

### Buggy code

```c
char *copy1(const char *s) {
    size_t n = strlen(s);
    char *out = malloc(n);
    memcpy(out, s, n + 1);
    return out;
}
```

### Expected diagnosis

The terminator requires n + 1 bytes; copying n + 1 bytes into n bytes is a heap overflow.

### Corrected code

```c
char *copy1(const char *s) {
    size_t n = strlen(s);
    char *out = malloc(n + 1);
    if (!out) return NULL;
    memcpy(out, s, n + 1);
    return out;
}
```

### Regression tests

```c
// Assert copy1("abc") is "abc" and allocation failure is handled.
```

## C-E-092: returning address of local

- Difficulty: Easy
- Language/platform: C
- Perspective: Pointer lifetime
- Concept: returning address of local
- Symptom: The caller reads garbage.
- Diagnostic goal: Ensure returned storage outlives the function.

### Buggy code

```c
int *value1(void) { int result = 7; return &result; }
```

### Expected diagnosis

A pointer to an automatic local object becomes invalid when the function returns.

### Corrected code

```c
int value1(void) { return 7; }
```

### Regression tests

```c
assert(value1() == 7);
```

## C-E-093: missing terminator

- Difficulty: Easy
- Language/platform: C
- Perspective: String API
- Concept: missing terminator
- Symptom: Printing reads beyond the buffer.
- Diagnostic goal: Reserve and write the C string terminator.

### Buggy code

```c
char name1[4];
memcpy(name1, "Ada", 3);
printf("%s", name1);
```

### Expected diagnosis

memcpy copies bytes only and does not append a terminator.

### Corrected code

```c
char name1[4];
memcpy(name1, "Ada", 3);
name1[3] = '\0';
```

### Regression tests

```c
assert(strcmp(name1, "Ada") == 0);
```

## C-E-094: signed overflow

- Difficulty: Easy
- Language/platform: C
- Perspective: Integer reasoning
- Concept: signed overflow
- Symptom: A boundary calculation produces undefined behavior.
- Diagnostic goal: Check before arithmetic or use an unsigned/wider representation.

### Buggy code

```c
int total1(int count, int size) { return count * size; }
```

### Expected diagnosis

Signed overflow is undefined in C; validating after the multiplication is too late.

### Corrected code

```c
bool total1(int count, int size, int *out) {
    if (count < 0 || size < 0 || count > INT_MAX / size) return false;
    *out = count * size;
    return true;
}
```

### Regression tests

```c
// Assert overflow returns false and a safe product returns true.
```

## C-E-095: double free

- Difficulty: Easy
- Language/platform: C
- Perspective: Ownership
- Concept: double free
- Symptom: The allocator reports corruption.
- Diagnostic goal: Assign ownership once and clear moved-from pointers.

### Buggy code

```c
void release1(char **p) { free(*p); free(*p); }
```

### Expected diagnosis

Freeing the same allocation twice is undefined behavior.

### Corrected code

```c
void release1(char **p) {
    if (p && *p) { free(*p); *p = NULL; }
}
```

### Regression tests

```c
// Call release1 twice; the second call is harmless.
```

## C-E-096: unchecked fopen

- Difficulty: Easy
- Language/platform: C
- Perspective: I/O contract
- Concept: unchecked fopen
- Symptom: A null FILE pointer is dereferenced.
- Diagnostic goal: Check resource acquisition before use.

### Buggy code

```c
FILE *f = fopen(path, "r");
char line[64];
fgets(line, sizeof line, f);
```

### Expected diagnosis

fopen returns NULL on failure; passing it to fgets is undefined behavior.

### Corrected code

```c
FILE *f = fopen(path, "r");
if (!f) return ERROR_OPEN;
char line[64];
if (!fgets(line, sizeof line, f)) { fclose(f); return ERROR_READ; }
fclose(f);
```

### Regression tests

```c
// Missing paths return an error without dereferencing NULL.
```

## C-E-097: data race

- Difficulty: Easy
- Language/platform: C
- Perspective: Concurrency
- Concept: data race
- Symptom: A counter loses increments under threads.
- Diagnostic goal: Synchronize shared mutable state.

### Buggy code

```c
shared_count1++;
```

### Expected diagnosis

Concurrent unsynchronized read-modify-write accesses form a data race and have undefined behavior.

### Corrected code

```c
pthread_mutex_lock(&count_mutex);
shared_count1++;
pthread_mutex_unlock(&count_mutex);
```

### Regression tests

```c
// Run two workers and assert the final count equals both contributions.
```

## C-E-098: scanf width omission

- Difficulty: Easy
- Language/platform: C
- Perspective: Parsing
- Concept: scanf width omission
- Symptom: Long input corrupts adjacent memory.
- Diagnostic goal: Bound formatted input by the destination capacity.

### Buggy code

```c
char word1[16];
scanf("%s", word1);
```

### Expected diagnosis

The conversion has no width limit, so input longer than 15 characters overflows the array.

### Corrected code

```c
char word1[16];
scanf("%15s", word1);
```

### Regression tests

```c
// A 100-character token must not overwrite memory.
```

## C-E-099: strncpy non-termination

- Difficulty: Easy
- Language/platform: C
- Perspective: API contract
- Concept: strncpy non-termination
- Symptom: The result is not a valid string for exact-length input.
- Diagnostic goal: Terminate explicitly after bounded copying.

### Buggy code

```c
strncpy(dst1, src1, sizeof dst1);
printf("%s", dst1);
```

### Expected diagnosis

strncpy does not append a terminator when the source fills the limit.

### Corrected code

```c
strncpy(dst1, src1, sizeof dst1 - 1);
dst1[sizeof dst1 - 1] = '\0';
```

### Regression tests

```c
// Exact-capacity source remains safely printable.
```

## C-E-100: early return leak

- Difficulty: Easy
- Language/platform: C
- Perspective: Cleanup
- Concept: early return leak
- Symptom: An error path leaks an allocation.
- Diagnostic goal: Centralize cleanup for all exits.

### Buggy code

```c
char *buffer = malloc(1024);
if (!buffer) return 0;
if (!read_data(buffer)) return -1;
free(buffer);
return 0;
```

### Expected diagnosis

The failed read returns before freeing buffer.

### Corrected code

```c
char *buffer = malloc(1024);
if (!buffer) return 0;
int result = read_data(buffer) ? 0 : -1;
free(buffer);
return result;
```

### Regression tests

```c
// Both read success and failure leave no allocation outstanding.
```

## C-M-001: off-by-one allocation

- Difficulty: Medium
- Language/platform: C
- Perspective: Memory safety
- Concept: off-by-one allocation
- Symptom: The last byte is overwritten.
- Diagnostic goal: Match allocation size to the largest valid index.

### Buggy code

```c
char *copy1(const char *s) {
    size_t n = strlen(s);
    char *out = malloc(n);
    memcpy(out, s, n + 1);
    return out;
}
```

### Expected diagnosis

The terminator requires n + 1 bytes; copying n + 1 bytes into n bytes is a heap overflow.

### Corrected code

```c
char *copy1(const char *s) {
    size_t n = strlen(s);
    char *out = malloc(n + 1);
    if (!out) return NULL;
    memcpy(out, s, n + 1);
    return out;
}
```

### Regression tests

```c
// Assert copy1("abc") is "abc" and allocation failure is handled.
```

## C-M-002: returning address of local

- Difficulty: Medium
- Language/platform: C
- Perspective: Pointer lifetime
- Concept: returning address of local
- Symptom: The caller reads garbage.
- Diagnostic goal: Ensure returned storage outlives the function.

### Buggy code

```c
int *value1(void) { int result = 7; return &result; }
```

### Expected diagnosis

A pointer to an automatic local object becomes invalid when the function returns.

### Corrected code

```c
int value1(void) { return 7; }
```

### Regression tests

```c
assert(value1() == 7);
```

## C-M-003: missing terminator

- Difficulty: Medium
- Language/platform: C
- Perspective: String API
- Concept: missing terminator
- Symptom: Printing reads beyond the buffer.
- Diagnostic goal: Reserve and write the C string terminator.

### Buggy code

```c
char name1[4];
memcpy(name1, "Ada", 3);
printf("%s", name1);
```

### Expected diagnosis

memcpy copies bytes only and does not append a terminator.

### Corrected code

```c
char name1[4];
memcpy(name1, "Ada", 3);
name1[3] = '\0';
```

### Regression tests

```c
assert(strcmp(name1, "Ada") == 0);
```

## C-M-004: signed overflow

- Difficulty: Medium
- Language/platform: C
- Perspective: Integer reasoning
- Concept: signed overflow
- Symptom: A boundary calculation produces undefined behavior.
- Diagnostic goal: Check before arithmetic or use an unsigned/wider representation.

### Buggy code

```c
int total1(int count, int size) { return count * size; }
```

### Expected diagnosis

Signed overflow is undefined in C; validating after the multiplication is too late.

### Corrected code

```c
bool total1(int count, int size, int *out) {
    if (count < 0 || size < 0 || count > INT_MAX / size) return false;
    *out = count * size;
    return true;
}
```

### Regression tests

```c
// Assert overflow returns false and a safe product returns true.
```

## C-M-005: double free

- Difficulty: Medium
- Language/platform: C
- Perspective: Ownership
- Concept: double free
- Symptom: The allocator reports corruption.
- Diagnostic goal: Assign ownership once and clear moved-from pointers.

### Buggy code

```c
void release1(char **p) { free(*p); free(*p); }
```

### Expected diagnosis

Freeing the same allocation twice is undefined behavior.

### Corrected code

```c
void release1(char **p) {
    if (p && *p) { free(*p); *p = NULL; }
}
```

### Regression tests

```c
// Call release1 twice; the second call is harmless.
```

## C-M-006: unchecked fopen

- Difficulty: Medium
- Language/platform: C
- Perspective: I/O contract
- Concept: unchecked fopen
- Symptom: A null FILE pointer is dereferenced.
- Diagnostic goal: Check resource acquisition before use.

### Buggy code

```c
FILE *f = fopen(path, "r");
char line[64];
fgets(line, sizeof line, f);
```

### Expected diagnosis

fopen returns NULL on failure; passing it to fgets is undefined behavior.

### Corrected code

```c
FILE *f = fopen(path, "r");
if (!f) return ERROR_OPEN;
char line[64];
if (!fgets(line, sizeof line, f)) { fclose(f); return ERROR_READ; }
fclose(f);
```

### Regression tests

```c
// Missing paths return an error without dereferencing NULL.
```

## C-M-007: data race

- Difficulty: Medium
- Language/platform: C
- Perspective: Concurrency
- Concept: data race
- Symptom: A counter loses increments under threads.
- Diagnostic goal: Synchronize shared mutable state.

### Buggy code

```c
shared_count1++;
```

### Expected diagnosis

Concurrent unsynchronized read-modify-write accesses form a data race and have undefined behavior.

### Corrected code

```c
pthread_mutex_lock(&count_mutex);
shared_count1++;
pthread_mutex_unlock(&count_mutex);
```

### Regression tests

```c
// Run two workers and assert the final count equals both contributions.
```

## C-M-008: scanf width omission

- Difficulty: Medium
- Language/platform: C
- Perspective: Parsing
- Concept: scanf width omission
- Symptom: Long input corrupts adjacent memory.
- Diagnostic goal: Bound formatted input by the destination capacity.

### Buggy code

```c
char word1[16];
scanf("%s", word1);
```

### Expected diagnosis

The conversion has no width limit, so input longer than 15 characters overflows the array.

### Corrected code

```c
char word1[16];
scanf("%15s", word1);
```

### Regression tests

```c
// A 100-character token must not overwrite memory.
```

## C-M-009: strncpy non-termination

- Difficulty: Medium
- Language/platform: C
- Perspective: API contract
- Concept: strncpy non-termination
- Symptom: The result is not a valid string for exact-length input.
- Diagnostic goal: Terminate explicitly after bounded copying.

### Buggy code

```c
strncpy(dst1, src1, sizeof dst1);
printf("%s", dst1);
```

### Expected diagnosis

strncpy does not append a terminator when the source fills the limit.

### Corrected code

```c
strncpy(dst1, src1, sizeof dst1 - 1);
dst1[sizeof dst1 - 1] = '\0';
```

### Regression tests

```c
// Exact-capacity source remains safely printable.
```

## C-M-010: early return leak

- Difficulty: Medium
- Language/platform: C
- Perspective: Cleanup
- Concept: early return leak
- Symptom: An error path leaks an allocation.
- Diagnostic goal: Centralize cleanup for all exits.

### Buggy code

```c
char *buffer = malloc(1024);
if (!buffer) return 0;
if (!read_data(buffer)) return -1;
free(buffer);
return 0;
```

### Expected diagnosis

The failed read returns before freeing buffer.

### Corrected code

```c
char *buffer = malloc(1024);
if (!buffer) return 0;
int result = read_data(buffer) ? 0 : -1;
free(buffer);
return result;
```

### Regression tests

```c
// Both read success and failure leave no allocation outstanding.
```

## C-M-011: off-by-one allocation

- Difficulty: Medium
- Language/platform: C
- Perspective: Memory safety
- Concept: off-by-one allocation
- Symptom: The last byte is overwritten.
- Diagnostic goal: Match allocation size to the largest valid index.

### Buggy code

```c
char *copy1(const char *s) {
    size_t n = strlen(s);
    char *out = malloc(n);
    memcpy(out, s, n + 1);
    return out;
}
```

### Expected diagnosis

The terminator requires n + 1 bytes; copying n + 1 bytes into n bytes is a heap overflow.

### Corrected code

```c
char *copy1(const char *s) {
    size_t n = strlen(s);
    char *out = malloc(n + 1);
    if (!out) return NULL;
    memcpy(out, s, n + 1);
    return out;
}
```

### Regression tests

```c
// Assert copy1("abc") is "abc" and allocation failure is handled.
```

## C-M-012: returning address of local

- Difficulty: Medium
- Language/platform: C
- Perspective: Pointer lifetime
- Concept: returning address of local
- Symptom: The caller reads garbage.
- Diagnostic goal: Ensure returned storage outlives the function.

### Buggy code

```c
int *value1(void) { int result = 7; return &result; }
```

### Expected diagnosis

A pointer to an automatic local object becomes invalid when the function returns.

### Corrected code

```c
int value1(void) { return 7; }
```

### Regression tests

```c
assert(value1() == 7);
```

## C-M-013: missing terminator

- Difficulty: Medium
- Language/platform: C
- Perspective: String API
- Concept: missing terminator
- Symptom: Printing reads beyond the buffer.
- Diagnostic goal: Reserve and write the C string terminator.

### Buggy code

```c
char name1[4];
memcpy(name1, "Ada", 3);
printf("%s", name1);
```

### Expected diagnosis

memcpy copies bytes only and does not append a terminator.

### Corrected code

```c
char name1[4];
memcpy(name1, "Ada", 3);
name1[3] = '\0';
```

### Regression tests

```c
assert(strcmp(name1, "Ada") == 0);
```

## C-M-014: signed overflow

- Difficulty: Medium
- Language/platform: C
- Perspective: Integer reasoning
- Concept: signed overflow
- Symptom: A boundary calculation produces undefined behavior.
- Diagnostic goal: Check before arithmetic or use an unsigned/wider representation.

### Buggy code

```c
int total1(int count, int size) { return count * size; }
```

### Expected diagnosis

Signed overflow is undefined in C; validating after the multiplication is too late.

### Corrected code

```c
bool total1(int count, int size, int *out) {
    if (count < 0 || size < 0 || count > INT_MAX / size) return false;
    *out = count * size;
    return true;
}
```

### Regression tests

```c
// Assert overflow returns false and a safe product returns true.
```

## C-M-015: double free

- Difficulty: Medium
- Language/platform: C
- Perspective: Ownership
- Concept: double free
- Symptom: The allocator reports corruption.
- Diagnostic goal: Assign ownership once and clear moved-from pointers.

### Buggy code

```c
void release1(char **p) { free(*p); free(*p); }
```

### Expected diagnosis

Freeing the same allocation twice is undefined behavior.

### Corrected code

```c
void release1(char **p) {
    if (p && *p) { free(*p); *p = NULL; }
}
```

### Regression tests

```c
// Call release1 twice; the second call is harmless.
```

## C-M-016: unchecked fopen

- Difficulty: Medium
- Language/platform: C
- Perspective: I/O contract
- Concept: unchecked fopen
- Symptom: A null FILE pointer is dereferenced.
- Diagnostic goal: Check resource acquisition before use.

### Buggy code

```c
FILE *f = fopen(path, "r");
char line[64];
fgets(line, sizeof line, f);
```

### Expected diagnosis

fopen returns NULL on failure; passing it to fgets is undefined behavior.

### Corrected code

```c
FILE *f = fopen(path, "r");
if (!f) return ERROR_OPEN;
char line[64];
if (!fgets(line, sizeof line, f)) { fclose(f); return ERROR_READ; }
fclose(f);
```

### Regression tests

```c
// Missing paths return an error without dereferencing NULL.
```

## C-M-017: data race

- Difficulty: Medium
- Language/platform: C
- Perspective: Concurrency
- Concept: data race
- Symptom: A counter loses increments under threads.
- Diagnostic goal: Synchronize shared mutable state.

### Buggy code

```c
shared_count1++;
```

### Expected diagnosis

Concurrent unsynchronized read-modify-write accesses form a data race and have undefined behavior.

### Corrected code

```c
pthread_mutex_lock(&count_mutex);
shared_count1++;
pthread_mutex_unlock(&count_mutex);
```

### Regression tests

```c
// Run two workers and assert the final count equals both contributions.
```

## C-M-018: scanf width omission

- Difficulty: Medium
- Language/platform: C
- Perspective: Parsing
- Concept: scanf width omission
- Symptom: Long input corrupts adjacent memory.
- Diagnostic goal: Bound formatted input by the destination capacity.

### Buggy code

```c
char word1[16];
scanf("%s", word1);
```

### Expected diagnosis

The conversion has no width limit, so input longer than 15 characters overflows the array.

### Corrected code

```c
char word1[16];
scanf("%15s", word1);
```

### Regression tests

```c
// A 100-character token must not overwrite memory.
```

## C-M-019: strncpy non-termination

- Difficulty: Medium
- Language/platform: C
- Perspective: API contract
- Concept: strncpy non-termination
- Symptom: The result is not a valid string for exact-length input.
- Diagnostic goal: Terminate explicitly after bounded copying.

### Buggy code

```c
strncpy(dst1, src1, sizeof dst1);
printf("%s", dst1);
```

### Expected diagnosis

strncpy does not append a terminator when the source fills the limit.

### Corrected code

```c
strncpy(dst1, src1, sizeof dst1 - 1);
dst1[sizeof dst1 - 1] = '\0';
```

### Regression tests

```c
// Exact-capacity source remains safely printable.
```

## C-M-020: early return leak

- Difficulty: Medium
- Language/platform: C
- Perspective: Cleanup
- Concept: early return leak
- Symptom: An error path leaks an allocation.
- Diagnostic goal: Centralize cleanup for all exits.

### Buggy code

```c
char *buffer = malloc(1024);
if (!buffer) return 0;
if (!read_data(buffer)) return -1;
free(buffer);
return 0;
```

### Expected diagnosis

The failed read returns before freeing buffer.

### Corrected code

```c
char *buffer = malloc(1024);
if (!buffer) return 0;
int result = read_data(buffer) ? 0 : -1;
free(buffer);
return result;
```

### Regression tests

```c
// Both read success and failure leave no allocation outstanding.
```

## C-M-021: off-by-one allocation

- Difficulty: Medium
- Language/platform: C
- Perspective: Memory safety
- Concept: off-by-one allocation
- Symptom: The last byte is overwritten.
- Diagnostic goal: Match allocation size to the largest valid index.

### Buggy code

```c
char *copy1(const char *s) {
    size_t n = strlen(s);
    char *out = malloc(n);
    memcpy(out, s, n + 1);
    return out;
}
```

### Expected diagnosis

The terminator requires n + 1 bytes; copying n + 1 bytes into n bytes is a heap overflow.

### Corrected code

```c
char *copy1(const char *s) {
    size_t n = strlen(s);
    char *out = malloc(n + 1);
    if (!out) return NULL;
    memcpy(out, s, n + 1);
    return out;
}
```

### Regression tests

```c
// Assert copy1("abc") is "abc" and allocation failure is handled.
```

## C-M-022: returning address of local

- Difficulty: Medium
- Language/platform: C
- Perspective: Pointer lifetime
- Concept: returning address of local
- Symptom: The caller reads garbage.
- Diagnostic goal: Ensure returned storage outlives the function.

### Buggy code

```c
int *value1(void) { int result = 7; return &result; }
```

### Expected diagnosis

A pointer to an automatic local object becomes invalid when the function returns.

### Corrected code

```c
int value1(void) { return 7; }
```

### Regression tests

```c
assert(value1() == 7);
```

## C-M-023: missing terminator

- Difficulty: Medium
- Language/platform: C
- Perspective: String API
- Concept: missing terminator
- Symptom: Printing reads beyond the buffer.
- Diagnostic goal: Reserve and write the C string terminator.

### Buggy code

```c
char name1[4];
memcpy(name1, "Ada", 3);
printf("%s", name1);
```

### Expected diagnosis

memcpy copies bytes only and does not append a terminator.

### Corrected code

```c
char name1[4];
memcpy(name1, "Ada", 3);
name1[3] = '\0';
```

### Regression tests

```c
assert(strcmp(name1, "Ada") == 0);
```

## C-M-024: signed overflow

- Difficulty: Medium
- Language/platform: C
- Perspective: Integer reasoning
- Concept: signed overflow
- Symptom: A boundary calculation produces undefined behavior.
- Diagnostic goal: Check before arithmetic or use an unsigned/wider representation.

### Buggy code

```c
int total1(int count, int size) { return count * size; }
```

### Expected diagnosis

Signed overflow is undefined in C; validating after the multiplication is too late.

### Corrected code

```c
bool total1(int count, int size, int *out) {
    if (count < 0 || size < 0 || count > INT_MAX / size) return false;
    *out = count * size;
    return true;
}
```

### Regression tests

```c
// Assert overflow returns false and a safe product returns true.
```

## C-M-025: double free

- Difficulty: Medium
- Language/platform: C
- Perspective: Ownership
- Concept: double free
- Symptom: The allocator reports corruption.
- Diagnostic goal: Assign ownership once and clear moved-from pointers.

### Buggy code

```c
void release1(char **p) { free(*p); free(*p); }
```

### Expected diagnosis

Freeing the same allocation twice is undefined behavior.

### Corrected code

```c
void release1(char **p) {
    if (p && *p) { free(*p); *p = NULL; }
}
```

### Regression tests

```c
// Call release1 twice; the second call is harmless.
```

## C-M-026: unchecked fopen

- Difficulty: Medium
- Language/platform: C
- Perspective: I/O contract
- Concept: unchecked fopen
- Symptom: A null FILE pointer is dereferenced.
- Diagnostic goal: Check resource acquisition before use.

### Buggy code

```c
FILE *f = fopen(path, "r");
char line[64];
fgets(line, sizeof line, f);
```

### Expected diagnosis

fopen returns NULL on failure; passing it to fgets is undefined behavior.

### Corrected code

```c
FILE *f = fopen(path, "r");
if (!f) return ERROR_OPEN;
char line[64];
if (!fgets(line, sizeof line, f)) { fclose(f); return ERROR_READ; }
fclose(f);
```

### Regression tests

```c
// Missing paths return an error without dereferencing NULL.
```

## C-M-027: data race

- Difficulty: Medium
- Language/platform: C
- Perspective: Concurrency
- Concept: data race
- Symptom: A counter loses increments under threads.
- Diagnostic goal: Synchronize shared mutable state.

### Buggy code

```c
shared_count1++;
```

### Expected diagnosis

Concurrent unsynchronized read-modify-write accesses form a data race and have undefined behavior.

### Corrected code

```c
pthread_mutex_lock(&count_mutex);
shared_count1++;
pthread_mutex_unlock(&count_mutex);
```

### Regression tests

```c
// Run two workers and assert the final count equals both contributions.
```

## C-M-028: scanf width omission

- Difficulty: Medium
- Language/platform: C
- Perspective: Parsing
- Concept: scanf width omission
- Symptom: Long input corrupts adjacent memory.
- Diagnostic goal: Bound formatted input by the destination capacity.

### Buggy code

```c
char word1[16];
scanf("%s", word1);
```

### Expected diagnosis

The conversion has no width limit, so input longer than 15 characters overflows the array.

### Corrected code

```c
char word1[16];
scanf("%15s", word1);
```

### Regression tests

```c
// A 100-character token must not overwrite memory.
```

## C-M-029: strncpy non-termination

- Difficulty: Medium
- Language/platform: C
- Perspective: API contract
- Concept: strncpy non-termination
- Symptom: The result is not a valid string for exact-length input.
- Diagnostic goal: Terminate explicitly after bounded copying.

### Buggy code

```c
strncpy(dst1, src1, sizeof dst1);
printf("%s", dst1);
```

### Expected diagnosis

strncpy does not append a terminator when the source fills the limit.

### Corrected code

```c
strncpy(dst1, src1, sizeof dst1 - 1);
dst1[sizeof dst1 - 1] = '\0';
```

### Regression tests

```c
// Exact-capacity source remains safely printable.
```

## C-M-030: early return leak

- Difficulty: Medium
- Language/platform: C
- Perspective: Cleanup
- Concept: early return leak
- Symptom: An error path leaks an allocation.
- Diagnostic goal: Centralize cleanup for all exits.

### Buggy code

```c
char *buffer = malloc(1024);
if (!buffer) return 0;
if (!read_data(buffer)) return -1;
free(buffer);
return 0;
```

### Expected diagnosis

The failed read returns before freeing buffer.

### Corrected code

```c
char *buffer = malloc(1024);
if (!buffer) return 0;
int result = read_data(buffer) ? 0 : -1;
free(buffer);
return result;
```

### Regression tests

```c
// Both read success and failure leave no allocation outstanding.
```

## C-M-031: off-by-one allocation

- Difficulty: Medium
- Language/platform: C
- Perspective: Memory safety
- Concept: off-by-one allocation
- Symptom: The last byte is overwritten.
- Diagnostic goal: Match allocation size to the largest valid index.

### Buggy code

```c
char *copy1(const char *s) {
    size_t n = strlen(s);
    char *out = malloc(n);
    memcpy(out, s, n + 1);
    return out;
}
```

### Expected diagnosis

The terminator requires n + 1 bytes; copying n + 1 bytes into n bytes is a heap overflow.

### Corrected code

```c
char *copy1(const char *s) {
    size_t n = strlen(s);
    char *out = malloc(n + 1);
    if (!out) return NULL;
    memcpy(out, s, n + 1);
    return out;
}
```

### Regression tests

```c
// Assert copy1("abc") is "abc" and allocation failure is handled.
```

## C-M-032: returning address of local

- Difficulty: Medium
- Language/platform: C
- Perspective: Pointer lifetime
- Concept: returning address of local
- Symptom: The caller reads garbage.
- Diagnostic goal: Ensure returned storage outlives the function.

### Buggy code

```c
int *value1(void) { int result = 7; return &result; }
```

### Expected diagnosis

A pointer to an automatic local object becomes invalid when the function returns.

### Corrected code

```c
int value1(void) { return 7; }
```

### Regression tests

```c
assert(value1() == 7);
```

## C-M-033: missing terminator

- Difficulty: Medium
- Language/platform: C
- Perspective: String API
- Concept: missing terminator
- Symptom: Printing reads beyond the buffer.
- Diagnostic goal: Reserve and write the C string terminator.

### Buggy code

```c
char name1[4];
memcpy(name1, "Ada", 3);
printf("%s", name1);
```

### Expected diagnosis

memcpy copies bytes only and does not append a terminator.

### Corrected code

```c
char name1[4];
memcpy(name1, "Ada", 3);
name1[3] = '\0';
```

### Regression tests

```c
assert(strcmp(name1, "Ada") == 0);
```

## C-M-034: signed overflow

- Difficulty: Medium
- Language/platform: C
- Perspective: Integer reasoning
- Concept: signed overflow
- Symptom: A boundary calculation produces undefined behavior.
- Diagnostic goal: Check before arithmetic or use an unsigned/wider representation.

### Buggy code

```c
int total1(int count, int size) { return count * size; }
```

### Expected diagnosis

Signed overflow is undefined in C; validating after the multiplication is too late.

### Corrected code

```c
bool total1(int count, int size, int *out) {
    if (count < 0 || size < 0 || count > INT_MAX / size) return false;
    *out = count * size;
    return true;
}
```

### Regression tests

```c
// Assert overflow returns false and a safe product returns true.
```

## C-M-035: double free

- Difficulty: Medium
- Language/platform: C
- Perspective: Ownership
- Concept: double free
- Symptom: The allocator reports corruption.
- Diagnostic goal: Assign ownership once and clear moved-from pointers.

### Buggy code

```c
void release1(char **p) { free(*p); free(*p); }
```

### Expected diagnosis

Freeing the same allocation twice is undefined behavior.

### Corrected code

```c
void release1(char **p) {
    if (p && *p) { free(*p); *p = NULL; }
}
```

### Regression tests

```c
// Call release1 twice; the second call is harmless.
```

## C-M-036: unchecked fopen

- Difficulty: Medium
- Language/platform: C
- Perspective: I/O contract
- Concept: unchecked fopen
- Symptom: A null FILE pointer is dereferenced.
- Diagnostic goal: Check resource acquisition before use.

### Buggy code

```c
FILE *f = fopen(path, "r");
char line[64];
fgets(line, sizeof line, f);
```

### Expected diagnosis

fopen returns NULL on failure; passing it to fgets is undefined behavior.

### Corrected code

```c
FILE *f = fopen(path, "r");
if (!f) return ERROR_OPEN;
char line[64];
if (!fgets(line, sizeof line, f)) { fclose(f); return ERROR_READ; }
fclose(f);
```

### Regression tests

```c
// Missing paths return an error without dereferencing NULL.
```

## C-M-037: data race

- Difficulty: Medium
- Language/platform: C
- Perspective: Concurrency
- Concept: data race
- Symptom: A counter loses increments under threads.
- Diagnostic goal: Synchronize shared mutable state.

### Buggy code

```c
shared_count1++;
```

### Expected diagnosis

Concurrent unsynchronized read-modify-write accesses form a data race and have undefined behavior.

### Corrected code

```c
pthread_mutex_lock(&count_mutex);
shared_count1++;
pthread_mutex_unlock(&count_mutex);
```

### Regression tests

```c
// Run two workers and assert the final count equals both contributions.
```

## C-M-038: scanf width omission

- Difficulty: Medium
- Language/platform: C
- Perspective: Parsing
- Concept: scanf width omission
- Symptom: Long input corrupts adjacent memory.
- Diagnostic goal: Bound formatted input by the destination capacity.

### Buggy code

```c
char word1[16];
scanf("%s", word1);
```

### Expected diagnosis

The conversion has no width limit, so input longer than 15 characters overflows the array.

### Corrected code

```c
char word1[16];
scanf("%15s", word1);
```

### Regression tests

```c
// A 100-character token must not overwrite memory.
```

## C-M-039: strncpy non-termination

- Difficulty: Medium
- Language/platform: C
- Perspective: API contract
- Concept: strncpy non-termination
- Symptom: The result is not a valid string for exact-length input.
- Diagnostic goal: Terminate explicitly after bounded copying.

### Buggy code

```c
strncpy(dst1, src1, sizeof dst1);
printf("%s", dst1);
```

### Expected diagnosis

strncpy does not append a terminator when the source fills the limit.

### Corrected code

```c
strncpy(dst1, src1, sizeof dst1 - 1);
dst1[sizeof dst1 - 1] = '\0';
```

### Regression tests

```c
// Exact-capacity source remains safely printable.
```

## C-M-040: early return leak

- Difficulty: Medium
- Language/platform: C
- Perspective: Cleanup
- Concept: early return leak
- Symptom: An error path leaks an allocation.
- Diagnostic goal: Centralize cleanup for all exits.

### Buggy code

```c
char *buffer = malloc(1024);
if (!buffer) return 0;
if (!read_data(buffer)) return -1;
free(buffer);
return 0;
```

### Expected diagnosis

The failed read returns before freeing buffer.

### Corrected code

```c
char *buffer = malloc(1024);
if (!buffer) return 0;
int result = read_data(buffer) ? 0 : -1;
free(buffer);
return result;
```

### Regression tests

```c
// Both read success and failure leave no allocation outstanding.
```

## C-M-041: off-by-one allocation

- Difficulty: Medium
- Language/platform: C
- Perspective: Memory safety
- Concept: off-by-one allocation
- Symptom: The last byte is overwritten.
- Diagnostic goal: Match allocation size to the largest valid index.

### Buggy code

```c
char *copy1(const char *s) {
    size_t n = strlen(s);
    char *out = malloc(n);
    memcpy(out, s, n + 1);
    return out;
}
```

### Expected diagnosis

The terminator requires n + 1 bytes; copying n + 1 bytes into n bytes is a heap overflow.

### Corrected code

```c
char *copy1(const char *s) {
    size_t n = strlen(s);
    char *out = malloc(n + 1);
    if (!out) return NULL;
    memcpy(out, s, n + 1);
    return out;
}
```

### Regression tests

```c
// Assert copy1("abc") is "abc" and allocation failure is handled.
```

## C-M-042: returning address of local

- Difficulty: Medium
- Language/platform: C
- Perspective: Pointer lifetime
- Concept: returning address of local
- Symptom: The caller reads garbage.
- Diagnostic goal: Ensure returned storage outlives the function.

### Buggy code

```c
int *value1(void) { int result = 7; return &result; }
```

### Expected diagnosis

A pointer to an automatic local object becomes invalid when the function returns.

### Corrected code

```c
int value1(void) { return 7; }
```

### Regression tests

```c
assert(value1() == 7);
```

## C-M-043: missing terminator

- Difficulty: Medium
- Language/platform: C
- Perspective: String API
- Concept: missing terminator
- Symptom: Printing reads beyond the buffer.
- Diagnostic goal: Reserve and write the C string terminator.

### Buggy code

```c
char name1[4];
memcpy(name1, "Ada", 3);
printf("%s", name1);
```

### Expected diagnosis

memcpy copies bytes only and does not append a terminator.

### Corrected code

```c
char name1[4];
memcpy(name1, "Ada", 3);
name1[3] = '\0';
```

### Regression tests

```c
assert(strcmp(name1, "Ada") == 0);
```

## C-M-044: signed overflow

- Difficulty: Medium
- Language/platform: C
- Perspective: Integer reasoning
- Concept: signed overflow
- Symptom: A boundary calculation produces undefined behavior.
- Diagnostic goal: Check before arithmetic or use an unsigned/wider representation.

### Buggy code

```c
int total1(int count, int size) { return count * size; }
```

### Expected diagnosis

Signed overflow is undefined in C; validating after the multiplication is too late.

### Corrected code

```c
bool total1(int count, int size, int *out) {
    if (count < 0 || size < 0 || count > INT_MAX / size) return false;
    *out = count * size;
    return true;
}
```

### Regression tests

```c
// Assert overflow returns false and a safe product returns true.
```

## C-M-045: double free

- Difficulty: Medium
- Language/platform: C
- Perspective: Ownership
- Concept: double free
- Symptom: The allocator reports corruption.
- Diagnostic goal: Assign ownership once and clear moved-from pointers.

### Buggy code

```c
void release1(char **p) { free(*p); free(*p); }
```

### Expected diagnosis

Freeing the same allocation twice is undefined behavior.

### Corrected code

```c
void release1(char **p) {
    if (p && *p) { free(*p); *p = NULL; }
}
```

### Regression tests

```c
// Call release1 twice; the second call is harmless.
```

## C-M-046: unchecked fopen

- Difficulty: Medium
- Language/platform: C
- Perspective: I/O contract
- Concept: unchecked fopen
- Symptom: A null FILE pointer is dereferenced.
- Diagnostic goal: Check resource acquisition before use.

### Buggy code

```c
FILE *f = fopen(path, "r");
char line[64];
fgets(line, sizeof line, f);
```

### Expected diagnosis

fopen returns NULL on failure; passing it to fgets is undefined behavior.

### Corrected code

```c
FILE *f = fopen(path, "r");
if (!f) return ERROR_OPEN;
char line[64];
if (!fgets(line, sizeof line, f)) { fclose(f); return ERROR_READ; }
fclose(f);
```

### Regression tests

```c
// Missing paths return an error without dereferencing NULL.
```

## C-M-047: data race

- Difficulty: Medium
- Language/platform: C
- Perspective: Concurrency
- Concept: data race
- Symptom: A counter loses increments under threads.
- Diagnostic goal: Synchronize shared mutable state.

### Buggy code

```c
shared_count1++;
```

### Expected diagnosis

Concurrent unsynchronized read-modify-write accesses form a data race and have undefined behavior.

### Corrected code

```c
pthread_mutex_lock(&count_mutex);
shared_count1++;
pthread_mutex_unlock(&count_mutex);
```

### Regression tests

```c
// Run two workers and assert the final count equals both contributions.
```

## C-M-048: scanf width omission

- Difficulty: Medium
- Language/platform: C
- Perspective: Parsing
- Concept: scanf width omission
- Symptom: Long input corrupts adjacent memory.
- Diagnostic goal: Bound formatted input by the destination capacity.

### Buggy code

```c
char word1[16];
scanf("%s", word1);
```

### Expected diagnosis

The conversion has no width limit, so input longer than 15 characters overflows the array.

### Corrected code

```c
char word1[16];
scanf("%15s", word1);
```

### Regression tests

```c
// A 100-character token must not overwrite memory.
```

## C-M-049: strncpy non-termination

- Difficulty: Medium
- Language/platform: C
- Perspective: API contract
- Concept: strncpy non-termination
- Symptom: The result is not a valid string for exact-length input.
- Diagnostic goal: Terminate explicitly after bounded copying.

### Buggy code

```c
strncpy(dst1, src1, sizeof dst1);
printf("%s", dst1);
```

### Expected diagnosis

strncpy does not append a terminator when the source fills the limit.

### Corrected code

```c
strncpy(dst1, src1, sizeof dst1 - 1);
dst1[sizeof dst1 - 1] = '\0';
```

### Regression tests

```c
// Exact-capacity source remains safely printable.
```

## C-M-050: early return leak

- Difficulty: Medium
- Language/platform: C
- Perspective: Cleanup
- Concept: early return leak
- Symptom: An error path leaks an allocation.
- Diagnostic goal: Centralize cleanup for all exits.

### Buggy code

```c
char *buffer = malloc(1024);
if (!buffer) return 0;
if (!read_data(buffer)) return -1;
free(buffer);
return 0;
```

### Expected diagnosis

The failed read returns before freeing buffer.

### Corrected code

```c
char *buffer = malloc(1024);
if (!buffer) return 0;
int result = read_data(buffer) ? 0 : -1;
free(buffer);
return result;
```

### Regression tests

```c
// Both read success and failure leave no allocation outstanding.
```

## C-M-051: off-by-one allocation

- Difficulty: Medium
- Language/platform: C
- Perspective: Memory safety
- Concept: off-by-one allocation
- Symptom: The last byte is overwritten.
- Diagnostic goal: Match allocation size to the largest valid index.

### Buggy code

```c
char *copy1(const char *s) {
    size_t n = strlen(s);
    char *out = malloc(n);
    memcpy(out, s, n + 1);
    return out;
}
```

### Expected diagnosis

The terminator requires n + 1 bytes; copying n + 1 bytes into n bytes is a heap overflow.

### Corrected code

```c
char *copy1(const char *s) {
    size_t n = strlen(s);
    char *out = malloc(n + 1);
    if (!out) return NULL;
    memcpy(out, s, n + 1);
    return out;
}
```

### Regression tests

```c
// Assert copy1("abc") is "abc" and allocation failure is handled.
```

## C-M-052: returning address of local

- Difficulty: Medium
- Language/platform: C
- Perspective: Pointer lifetime
- Concept: returning address of local
- Symptom: The caller reads garbage.
- Diagnostic goal: Ensure returned storage outlives the function.

### Buggy code

```c
int *value1(void) { int result = 7; return &result; }
```

### Expected diagnosis

A pointer to an automatic local object becomes invalid when the function returns.

### Corrected code

```c
int value1(void) { return 7; }
```

### Regression tests

```c
assert(value1() == 7);
```

## C-M-053: missing terminator

- Difficulty: Medium
- Language/platform: C
- Perspective: String API
- Concept: missing terminator
- Symptom: Printing reads beyond the buffer.
- Diagnostic goal: Reserve and write the C string terminator.

### Buggy code

```c
char name1[4];
memcpy(name1, "Ada", 3);
printf("%s", name1);
```

### Expected diagnosis

memcpy copies bytes only and does not append a terminator.

### Corrected code

```c
char name1[4];
memcpy(name1, "Ada", 3);
name1[3] = '\0';
```

### Regression tests

```c
assert(strcmp(name1, "Ada") == 0);
```

## C-M-054: signed overflow

- Difficulty: Medium
- Language/platform: C
- Perspective: Integer reasoning
- Concept: signed overflow
- Symptom: A boundary calculation produces undefined behavior.
- Diagnostic goal: Check before arithmetic or use an unsigned/wider representation.

### Buggy code

```c
int total1(int count, int size) { return count * size; }
```

### Expected diagnosis

Signed overflow is undefined in C; validating after the multiplication is too late.

### Corrected code

```c
bool total1(int count, int size, int *out) {
    if (count < 0 || size < 0 || count > INT_MAX / size) return false;
    *out = count * size;
    return true;
}
```

### Regression tests

```c
// Assert overflow returns false and a safe product returns true.
```

## C-M-055: double free

- Difficulty: Medium
- Language/platform: C
- Perspective: Ownership
- Concept: double free
- Symptom: The allocator reports corruption.
- Diagnostic goal: Assign ownership once and clear moved-from pointers.

### Buggy code

```c
void release1(char **p) { free(*p); free(*p); }
```

### Expected diagnosis

Freeing the same allocation twice is undefined behavior.

### Corrected code

```c
void release1(char **p) {
    if (p && *p) { free(*p); *p = NULL; }
}
```

### Regression tests

```c
// Call release1 twice; the second call is harmless.
```

## C-M-056: unchecked fopen

- Difficulty: Medium
- Language/platform: C
- Perspective: I/O contract
- Concept: unchecked fopen
- Symptom: A null FILE pointer is dereferenced.
- Diagnostic goal: Check resource acquisition before use.

### Buggy code

```c
FILE *f = fopen(path, "r");
char line[64];
fgets(line, sizeof line, f);
```

### Expected diagnosis

fopen returns NULL on failure; passing it to fgets is undefined behavior.

### Corrected code

```c
FILE *f = fopen(path, "r");
if (!f) return ERROR_OPEN;
char line[64];
if (!fgets(line, sizeof line, f)) { fclose(f); return ERROR_READ; }
fclose(f);
```

### Regression tests

```c
// Missing paths return an error without dereferencing NULL.
```

## C-M-057: data race

- Difficulty: Medium
- Language/platform: C
- Perspective: Concurrency
- Concept: data race
- Symptom: A counter loses increments under threads.
- Diagnostic goal: Synchronize shared mutable state.

### Buggy code

```c
shared_count1++;
```

### Expected diagnosis

Concurrent unsynchronized read-modify-write accesses form a data race and have undefined behavior.

### Corrected code

```c
pthread_mutex_lock(&count_mutex);
shared_count1++;
pthread_mutex_unlock(&count_mutex);
```

### Regression tests

```c
// Run two workers and assert the final count equals both contributions.
```

## C-M-058: scanf width omission

- Difficulty: Medium
- Language/platform: C
- Perspective: Parsing
- Concept: scanf width omission
- Symptom: Long input corrupts adjacent memory.
- Diagnostic goal: Bound formatted input by the destination capacity.

### Buggy code

```c
char word1[16];
scanf("%s", word1);
```

### Expected diagnosis

The conversion has no width limit, so input longer than 15 characters overflows the array.

### Corrected code

```c
char word1[16];
scanf("%15s", word1);
```

### Regression tests

```c
// A 100-character token must not overwrite memory.
```

## C-M-059: strncpy non-termination

- Difficulty: Medium
- Language/platform: C
- Perspective: API contract
- Concept: strncpy non-termination
- Symptom: The result is not a valid string for exact-length input.
- Diagnostic goal: Terminate explicitly after bounded copying.

### Buggy code

```c
strncpy(dst1, src1, sizeof dst1);
printf("%s", dst1);
```

### Expected diagnosis

strncpy does not append a terminator when the source fills the limit.

### Corrected code

```c
strncpy(dst1, src1, sizeof dst1 - 1);
dst1[sizeof dst1 - 1] = '\0';
```

### Regression tests

```c
// Exact-capacity source remains safely printable.
```

## C-M-060: early return leak

- Difficulty: Medium
- Language/platform: C
- Perspective: Cleanup
- Concept: early return leak
- Symptom: An error path leaks an allocation.
- Diagnostic goal: Centralize cleanup for all exits.

### Buggy code

```c
char *buffer = malloc(1024);
if (!buffer) return 0;
if (!read_data(buffer)) return -1;
free(buffer);
return 0;
```

### Expected diagnosis

The failed read returns before freeing buffer.

### Corrected code

```c
char *buffer = malloc(1024);
if (!buffer) return 0;
int result = read_data(buffer) ? 0 : -1;
free(buffer);
return result;
```

### Regression tests

```c
// Both read success and failure leave no allocation outstanding.
```

## C-M-061: off-by-one allocation

- Difficulty: Medium
- Language/platform: C
- Perspective: Memory safety
- Concept: off-by-one allocation
- Symptom: The last byte is overwritten.
- Diagnostic goal: Match allocation size to the largest valid index.

### Buggy code

```c
char *copy1(const char *s) {
    size_t n = strlen(s);
    char *out = malloc(n);
    memcpy(out, s, n + 1);
    return out;
}
```

### Expected diagnosis

The terminator requires n + 1 bytes; copying n + 1 bytes into n bytes is a heap overflow.

### Corrected code

```c
char *copy1(const char *s) {
    size_t n = strlen(s);
    char *out = malloc(n + 1);
    if (!out) return NULL;
    memcpy(out, s, n + 1);
    return out;
}
```

### Regression tests

```c
// Assert copy1("abc") is "abc" and allocation failure is handled.
```

## C-M-062: returning address of local

- Difficulty: Medium
- Language/platform: C
- Perspective: Pointer lifetime
- Concept: returning address of local
- Symptom: The caller reads garbage.
- Diagnostic goal: Ensure returned storage outlives the function.

### Buggy code

```c
int *value1(void) { int result = 7; return &result; }
```

### Expected diagnosis

A pointer to an automatic local object becomes invalid when the function returns.

### Corrected code

```c
int value1(void) { return 7; }
```

### Regression tests

```c
assert(value1() == 7);
```

## C-M-063: missing terminator

- Difficulty: Medium
- Language/platform: C
- Perspective: String API
- Concept: missing terminator
- Symptom: Printing reads beyond the buffer.
- Diagnostic goal: Reserve and write the C string terminator.

### Buggy code

```c
char name1[4];
memcpy(name1, "Ada", 3);
printf("%s", name1);
```

### Expected diagnosis

memcpy copies bytes only and does not append a terminator.

### Corrected code

```c
char name1[4];
memcpy(name1, "Ada", 3);
name1[3] = '\0';
```

### Regression tests

```c
assert(strcmp(name1, "Ada") == 0);
```

## C-M-064: signed overflow

- Difficulty: Medium
- Language/platform: C
- Perspective: Integer reasoning
- Concept: signed overflow
- Symptom: A boundary calculation produces undefined behavior.
- Diagnostic goal: Check before arithmetic or use an unsigned/wider representation.

### Buggy code

```c
int total1(int count, int size) { return count * size; }
```

### Expected diagnosis

Signed overflow is undefined in C; validating after the multiplication is too late.

### Corrected code

```c
bool total1(int count, int size, int *out) {
    if (count < 0 || size < 0 || count > INT_MAX / size) return false;
    *out = count * size;
    return true;
}
```

### Regression tests

```c
// Assert overflow returns false and a safe product returns true.
```

## C-M-065: double free

- Difficulty: Medium
- Language/platform: C
- Perspective: Ownership
- Concept: double free
- Symptom: The allocator reports corruption.
- Diagnostic goal: Assign ownership once and clear moved-from pointers.

### Buggy code

```c
void release1(char **p) { free(*p); free(*p); }
```

### Expected diagnosis

Freeing the same allocation twice is undefined behavior.

### Corrected code

```c
void release1(char **p) {
    if (p && *p) { free(*p); *p = NULL; }
}
```

### Regression tests

```c
// Call release1 twice; the second call is harmless.
```

## C-M-066: unchecked fopen

- Difficulty: Medium
- Language/platform: C
- Perspective: I/O contract
- Concept: unchecked fopen
- Symptom: A null FILE pointer is dereferenced.
- Diagnostic goal: Check resource acquisition before use.

### Buggy code

```c
FILE *f = fopen(path, "r");
char line[64];
fgets(line, sizeof line, f);
```

### Expected diagnosis

fopen returns NULL on failure; passing it to fgets is undefined behavior.

### Corrected code

```c
FILE *f = fopen(path, "r");
if (!f) return ERROR_OPEN;
char line[64];
if (!fgets(line, sizeof line, f)) { fclose(f); return ERROR_READ; }
fclose(f);
```

### Regression tests

```c
// Missing paths return an error without dereferencing NULL.
```

## C-M-067: data race

- Difficulty: Medium
- Language/platform: C
- Perspective: Concurrency
- Concept: data race
- Symptom: A counter loses increments under threads.
- Diagnostic goal: Synchronize shared mutable state.

### Buggy code

```c
shared_count1++;
```

### Expected diagnosis

Concurrent unsynchronized read-modify-write accesses form a data race and have undefined behavior.

### Corrected code

```c
pthread_mutex_lock(&count_mutex);
shared_count1++;
pthread_mutex_unlock(&count_mutex);
```

### Regression tests

```c
// Run two workers and assert the final count equals both contributions.
```

## C-M-068: scanf width omission

- Difficulty: Medium
- Language/platform: C
- Perspective: Parsing
- Concept: scanf width omission
- Symptom: Long input corrupts adjacent memory.
- Diagnostic goal: Bound formatted input by the destination capacity.

### Buggy code

```c
char word1[16];
scanf("%s", word1);
```

### Expected diagnosis

The conversion has no width limit, so input longer than 15 characters overflows the array.

### Corrected code

```c
char word1[16];
scanf("%15s", word1);
```

### Regression tests

```c
// A 100-character token must not overwrite memory.
```

## C-M-069: strncpy non-termination

- Difficulty: Medium
- Language/platform: C
- Perspective: API contract
- Concept: strncpy non-termination
- Symptom: The result is not a valid string for exact-length input.
- Diagnostic goal: Terminate explicitly after bounded copying.

### Buggy code

```c
strncpy(dst1, src1, sizeof dst1);
printf("%s", dst1);
```

### Expected diagnosis

strncpy does not append a terminator when the source fills the limit.

### Corrected code

```c
strncpy(dst1, src1, sizeof dst1 - 1);
dst1[sizeof dst1 - 1] = '\0';
```

### Regression tests

```c
// Exact-capacity source remains safely printable.
```

## C-M-070: early return leak

- Difficulty: Medium
- Language/platform: C
- Perspective: Cleanup
- Concept: early return leak
- Symptom: An error path leaks an allocation.
- Diagnostic goal: Centralize cleanup for all exits.

### Buggy code

```c
char *buffer = malloc(1024);
if (!buffer) return 0;
if (!read_data(buffer)) return -1;
free(buffer);
return 0;
```

### Expected diagnosis

The failed read returns before freeing buffer.

### Corrected code

```c
char *buffer = malloc(1024);
if (!buffer) return 0;
int result = read_data(buffer) ? 0 : -1;
free(buffer);
return result;
```

### Regression tests

```c
// Both read success and failure leave no allocation outstanding.
```

## C-M-071: off-by-one allocation

- Difficulty: Medium
- Language/platform: C
- Perspective: Memory safety
- Concept: off-by-one allocation
- Symptom: The last byte is overwritten.
- Diagnostic goal: Match allocation size to the largest valid index.

### Buggy code

```c
char *copy1(const char *s) {
    size_t n = strlen(s);
    char *out = malloc(n);
    memcpy(out, s, n + 1);
    return out;
}
```

### Expected diagnosis

The terminator requires n + 1 bytes; copying n + 1 bytes into n bytes is a heap overflow.

### Corrected code

```c
char *copy1(const char *s) {
    size_t n = strlen(s);
    char *out = malloc(n + 1);
    if (!out) return NULL;
    memcpy(out, s, n + 1);
    return out;
}
```

### Regression tests

```c
// Assert copy1("abc") is "abc" and allocation failure is handled.
```

## C-M-072: returning address of local

- Difficulty: Medium
- Language/platform: C
- Perspective: Pointer lifetime
- Concept: returning address of local
- Symptom: The caller reads garbage.
- Diagnostic goal: Ensure returned storage outlives the function.

### Buggy code

```c
int *value1(void) { int result = 7; return &result; }
```

### Expected diagnosis

A pointer to an automatic local object becomes invalid when the function returns.

### Corrected code

```c
int value1(void) { return 7; }
```

### Regression tests

```c
assert(value1() == 7);
```

## C-M-073: missing terminator

- Difficulty: Medium
- Language/platform: C
- Perspective: String API
- Concept: missing terminator
- Symptom: Printing reads beyond the buffer.
- Diagnostic goal: Reserve and write the C string terminator.

### Buggy code

```c
char name1[4];
memcpy(name1, "Ada", 3);
printf("%s", name1);
```

### Expected diagnosis

memcpy copies bytes only and does not append a terminator.

### Corrected code

```c
char name1[4];
memcpy(name1, "Ada", 3);
name1[3] = '\0';
```

### Regression tests

```c
assert(strcmp(name1, "Ada") == 0);
```

## C-M-074: signed overflow

- Difficulty: Medium
- Language/platform: C
- Perspective: Integer reasoning
- Concept: signed overflow
- Symptom: A boundary calculation produces undefined behavior.
- Diagnostic goal: Check before arithmetic or use an unsigned/wider representation.

### Buggy code

```c
int total1(int count, int size) { return count * size; }
```

### Expected diagnosis

Signed overflow is undefined in C; validating after the multiplication is too late.

### Corrected code

```c
bool total1(int count, int size, int *out) {
    if (count < 0 || size < 0 || count > INT_MAX / size) return false;
    *out = count * size;
    return true;
}
```

### Regression tests

```c
// Assert overflow returns false and a safe product returns true.
```

## C-M-075: double free

- Difficulty: Medium
- Language/platform: C
- Perspective: Ownership
- Concept: double free
- Symptom: The allocator reports corruption.
- Diagnostic goal: Assign ownership once and clear moved-from pointers.

### Buggy code

```c
void release1(char **p) { free(*p); free(*p); }
```

### Expected diagnosis

Freeing the same allocation twice is undefined behavior.

### Corrected code

```c
void release1(char **p) {
    if (p && *p) { free(*p); *p = NULL; }
}
```

### Regression tests

```c
// Call release1 twice; the second call is harmless.
```

## C-M-076: unchecked fopen

- Difficulty: Medium
- Language/platform: C
- Perspective: I/O contract
- Concept: unchecked fopen
- Symptom: A null FILE pointer is dereferenced.
- Diagnostic goal: Check resource acquisition before use.

### Buggy code

```c
FILE *f = fopen(path, "r");
char line[64];
fgets(line, sizeof line, f);
```

### Expected diagnosis

fopen returns NULL on failure; passing it to fgets is undefined behavior.

### Corrected code

```c
FILE *f = fopen(path, "r");
if (!f) return ERROR_OPEN;
char line[64];
if (!fgets(line, sizeof line, f)) { fclose(f); return ERROR_READ; }
fclose(f);
```

### Regression tests

```c
// Missing paths return an error without dereferencing NULL.
```

## C-M-077: data race

- Difficulty: Medium
- Language/platform: C
- Perspective: Concurrency
- Concept: data race
- Symptom: A counter loses increments under threads.
- Diagnostic goal: Synchronize shared mutable state.

### Buggy code

```c
shared_count1++;
```

### Expected diagnosis

Concurrent unsynchronized read-modify-write accesses form a data race and have undefined behavior.

### Corrected code

```c
pthread_mutex_lock(&count_mutex);
shared_count1++;
pthread_mutex_unlock(&count_mutex);
```

### Regression tests

```c
// Run two workers and assert the final count equals both contributions.
```

## C-M-078: scanf width omission

- Difficulty: Medium
- Language/platform: C
- Perspective: Parsing
- Concept: scanf width omission
- Symptom: Long input corrupts adjacent memory.
- Diagnostic goal: Bound formatted input by the destination capacity.

### Buggy code

```c
char word1[16];
scanf("%s", word1);
```

### Expected diagnosis

The conversion has no width limit, so input longer than 15 characters overflows the array.

### Corrected code

```c
char word1[16];
scanf("%15s", word1);
```

### Regression tests

```c
// A 100-character token must not overwrite memory.
```

## C-M-079: strncpy non-termination

- Difficulty: Medium
- Language/platform: C
- Perspective: API contract
- Concept: strncpy non-termination
- Symptom: The result is not a valid string for exact-length input.
- Diagnostic goal: Terminate explicitly after bounded copying.

### Buggy code

```c
strncpy(dst1, src1, sizeof dst1);
printf("%s", dst1);
```

### Expected diagnosis

strncpy does not append a terminator when the source fills the limit.

### Corrected code

```c
strncpy(dst1, src1, sizeof dst1 - 1);
dst1[sizeof dst1 - 1] = '\0';
```

### Regression tests

```c
// Exact-capacity source remains safely printable.
```

## C-M-080: early return leak

- Difficulty: Medium
- Language/platform: C
- Perspective: Cleanup
- Concept: early return leak
- Symptom: An error path leaks an allocation.
- Diagnostic goal: Centralize cleanup for all exits.

### Buggy code

```c
char *buffer = malloc(1024);
if (!buffer) return 0;
if (!read_data(buffer)) return -1;
free(buffer);
return 0;
```

### Expected diagnosis

The failed read returns before freeing buffer.

### Corrected code

```c
char *buffer = malloc(1024);
if (!buffer) return 0;
int result = read_data(buffer) ? 0 : -1;
free(buffer);
return result;
```

### Regression tests

```c
// Both read success and failure leave no allocation outstanding.
```

## C-M-081: off-by-one allocation

- Difficulty: Medium
- Language/platform: C
- Perspective: Memory safety
- Concept: off-by-one allocation
- Symptom: The last byte is overwritten.
- Diagnostic goal: Match allocation size to the largest valid index.

### Buggy code

```c
char *copy1(const char *s) {
    size_t n = strlen(s);
    char *out = malloc(n);
    memcpy(out, s, n + 1);
    return out;
}
```

### Expected diagnosis

The terminator requires n + 1 bytes; copying n + 1 bytes into n bytes is a heap overflow.

### Corrected code

```c
char *copy1(const char *s) {
    size_t n = strlen(s);
    char *out = malloc(n + 1);
    if (!out) return NULL;
    memcpy(out, s, n + 1);
    return out;
}
```

### Regression tests

```c
// Assert copy1("abc") is "abc" and allocation failure is handled.
```

## C-M-082: returning address of local

- Difficulty: Medium
- Language/platform: C
- Perspective: Pointer lifetime
- Concept: returning address of local
- Symptom: The caller reads garbage.
- Diagnostic goal: Ensure returned storage outlives the function.

### Buggy code

```c
int *value1(void) { int result = 7; return &result; }
```

### Expected diagnosis

A pointer to an automatic local object becomes invalid when the function returns.

### Corrected code

```c
int value1(void) { return 7; }
```

### Regression tests

```c
assert(value1() == 7);
```

## C-M-083: missing terminator

- Difficulty: Medium
- Language/platform: C
- Perspective: String API
- Concept: missing terminator
- Symptom: Printing reads beyond the buffer.
- Diagnostic goal: Reserve and write the C string terminator.

### Buggy code

```c
char name1[4];
memcpy(name1, "Ada", 3);
printf("%s", name1);
```

### Expected diagnosis

memcpy copies bytes only and does not append a terminator.

### Corrected code

```c
char name1[4];
memcpy(name1, "Ada", 3);
name1[3] = '\0';
```

### Regression tests

```c
assert(strcmp(name1, "Ada") == 0);
```

## C-M-084: signed overflow

- Difficulty: Medium
- Language/platform: C
- Perspective: Integer reasoning
- Concept: signed overflow
- Symptom: A boundary calculation produces undefined behavior.
- Diagnostic goal: Check before arithmetic or use an unsigned/wider representation.

### Buggy code

```c
int total1(int count, int size) { return count * size; }
```

### Expected diagnosis

Signed overflow is undefined in C; validating after the multiplication is too late.

### Corrected code

```c
bool total1(int count, int size, int *out) {
    if (count < 0 || size < 0 || count > INT_MAX / size) return false;
    *out = count * size;
    return true;
}
```

### Regression tests

```c
// Assert overflow returns false and a safe product returns true.
```

## C-M-085: double free

- Difficulty: Medium
- Language/platform: C
- Perspective: Ownership
- Concept: double free
- Symptom: The allocator reports corruption.
- Diagnostic goal: Assign ownership once and clear moved-from pointers.

### Buggy code

```c
void release1(char **p) { free(*p); free(*p); }
```

### Expected diagnosis

Freeing the same allocation twice is undefined behavior.

### Corrected code

```c
void release1(char **p) {
    if (p && *p) { free(*p); *p = NULL; }
}
```

### Regression tests

```c
// Call release1 twice; the second call is harmless.
```

## C-M-086: unchecked fopen

- Difficulty: Medium
- Language/platform: C
- Perspective: I/O contract
- Concept: unchecked fopen
- Symptom: A null FILE pointer is dereferenced.
- Diagnostic goal: Check resource acquisition before use.

### Buggy code

```c
FILE *f = fopen(path, "r");
char line[64];
fgets(line, sizeof line, f);
```

### Expected diagnosis

fopen returns NULL on failure; passing it to fgets is undefined behavior.

### Corrected code

```c
FILE *f = fopen(path, "r");
if (!f) return ERROR_OPEN;
char line[64];
if (!fgets(line, sizeof line, f)) { fclose(f); return ERROR_READ; }
fclose(f);
```

### Regression tests

```c
// Missing paths return an error without dereferencing NULL.
```

## C-M-087: data race

- Difficulty: Medium
- Language/platform: C
- Perspective: Concurrency
- Concept: data race
- Symptom: A counter loses increments under threads.
- Diagnostic goal: Synchronize shared mutable state.

### Buggy code

```c
shared_count1++;
```

### Expected diagnosis

Concurrent unsynchronized read-modify-write accesses form a data race and have undefined behavior.

### Corrected code

```c
pthread_mutex_lock(&count_mutex);
shared_count1++;
pthread_mutex_unlock(&count_mutex);
```

### Regression tests

```c
// Run two workers and assert the final count equals both contributions.
```

## C-M-088: scanf width omission

- Difficulty: Medium
- Language/platform: C
- Perspective: Parsing
- Concept: scanf width omission
- Symptom: Long input corrupts adjacent memory.
- Diagnostic goal: Bound formatted input by the destination capacity.

### Buggy code

```c
char word1[16];
scanf("%s", word1);
```

### Expected diagnosis

The conversion has no width limit, so input longer than 15 characters overflows the array.

### Corrected code

```c
char word1[16];
scanf("%15s", word1);
```

### Regression tests

```c
// A 100-character token must not overwrite memory.
```

## C-M-089: strncpy non-termination

- Difficulty: Medium
- Language/platform: C
- Perspective: API contract
- Concept: strncpy non-termination
- Symptom: The result is not a valid string for exact-length input.
- Diagnostic goal: Terminate explicitly after bounded copying.

### Buggy code

```c
strncpy(dst1, src1, sizeof dst1);
printf("%s", dst1);
```

### Expected diagnosis

strncpy does not append a terminator when the source fills the limit.

### Corrected code

```c
strncpy(dst1, src1, sizeof dst1 - 1);
dst1[sizeof dst1 - 1] = '\0';
```

### Regression tests

```c
// Exact-capacity source remains safely printable.
```

## C-M-090: early return leak

- Difficulty: Medium
- Language/platform: C
- Perspective: Cleanup
- Concept: early return leak
- Symptom: An error path leaks an allocation.
- Diagnostic goal: Centralize cleanup for all exits.

### Buggy code

```c
char *buffer = malloc(1024);
if (!buffer) return 0;
if (!read_data(buffer)) return -1;
free(buffer);
return 0;
```

### Expected diagnosis

The failed read returns before freeing buffer.

### Corrected code

```c
char *buffer = malloc(1024);
if (!buffer) return 0;
int result = read_data(buffer) ? 0 : -1;
free(buffer);
return result;
```

### Regression tests

```c
// Both read success and failure leave no allocation outstanding.
```

## C-M-091: off-by-one allocation

- Difficulty: Medium
- Language/platform: C
- Perspective: Memory safety
- Concept: off-by-one allocation
- Symptom: The last byte is overwritten.
- Diagnostic goal: Match allocation size to the largest valid index.

### Buggy code

```c
char *copy1(const char *s) {
    size_t n = strlen(s);
    char *out = malloc(n);
    memcpy(out, s, n + 1);
    return out;
}
```

### Expected diagnosis

The terminator requires n + 1 bytes; copying n + 1 bytes into n bytes is a heap overflow.

### Corrected code

```c
char *copy1(const char *s) {
    size_t n = strlen(s);
    char *out = malloc(n + 1);
    if (!out) return NULL;
    memcpy(out, s, n + 1);
    return out;
}
```

### Regression tests

```c
// Assert copy1("abc") is "abc" and allocation failure is handled.
```

## C-M-092: returning address of local

- Difficulty: Medium
- Language/platform: C
- Perspective: Pointer lifetime
- Concept: returning address of local
- Symptom: The caller reads garbage.
- Diagnostic goal: Ensure returned storage outlives the function.

### Buggy code

```c
int *value1(void) { int result = 7; return &result; }
```

### Expected diagnosis

A pointer to an automatic local object becomes invalid when the function returns.

### Corrected code

```c
int value1(void) { return 7; }
```

### Regression tests

```c
assert(value1() == 7);
```

## C-M-093: missing terminator

- Difficulty: Medium
- Language/platform: C
- Perspective: String API
- Concept: missing terminator
- Symptom: Printing reads beyond the buffer.
- Diagnostic goal: Reserve and write the C string terminator.

### Buggy code

```c
char name1[4];
memcpy(name1, "Ada", 3);
printf("%s", name1);
```

### Expected diagnosis

memcpy copies bytes only and does not append a terminator.

### Corrected code

```c
char name1[4];
memcpy(name1, "Ada", 3);
name1[3] = '\0';
```

### Regression tests

```c
assert(strcmp(name1, "Ada") == 0);
```

## C-M-094: signed overflow

- Difficulty: Medium
- Language/platform: C
- Perspective: Integer reasoning
- Concept: signed overflow
- Symptom: A boundary calculation produces undefined behavior.
- Diagnostic goal: Check before arithmetic or use an unsigned/wider representation.

### Buggy code

```c
int total1(int count, int size) { return count * size; }
```

### Expected diagnosis

Signed overflow is undefined in C; validating after the multiplication is too late.

### Corrected code

```c
bool total1(int count, int size, int *out) {
    if (count < 0 || size < 0 || count > INT_MAX / size) return false;
    *out = count * size;
    return true;
}
```

### Regression tests

```c
// Assert overflow returns false and a safe product returns true.
```

## C-M-095: double free

- Difficulty: Medium
- Language/platform: C
- Perspective: Ownership
- Concept: double free
- Symptom: The allocator reports corruption.
- Diagnostic goal: Assign ownership once and clear moved-from pointers.

### Buggy code

```c
void release1(char **p) { free(*p); free(*p); }
```

### Expected diagnosis

Freeing the same allocation twice is undefined behavior.

### Corrected code

```c
void release1(char **p) {
    if (p && *p) { free(*p); *p = NULL; }
}
```

### Regression tests

```c
// Call release1 twice; the second call is harmless.
```

## C-M-096: unchecked fopen

- Difficulty: Medium
- Language/platform: C
- Perspective: I/O contract
- Concept: unchecked fopen
- Symptom: A null FILE pointer is dereferenced.
- Diagnostic goal: Check resource acquisition before use.

### Buggy code

```c
FILE *f = fopen(path, "r");
char line[64];
fgets(line, sizeof line, f);
```

### Expected diagnosis

fopen returns NULL on failure; passing it to fgets is undefined behavior.

### Corrected code

```c
FILE *f = fopen(path, "r");
if (!f) return ERROR_OPEN;
char line[64];
if (!fgets(line, sizeof line, f)) { fclose(f); return ERROR_READ; }
fclose(f);
```

### Regression tests

```c
// Missing paths return an error without dereferencing NULL.
```

## C-M-097: data race

- Difficulty: Medium
- Language/platform: C
- Perspective: Concurrency
- Concept: data race
- Symptom: A counter loses increments under threads.
- Diagnostic goal: Synchronize shared mutable state.

### Buggy code

```c
shared_count1++;
```

### Expected diagnosis

Concurrent unsynchronized read-modify-write accesses form a data race and have undefined behavior.

### Corrected code

```c
pthread_mutex_lock(&count_mutex);
shared_count1++;
pthread_mutex_unlock(&count_mutex);
```

### Regression tests

```c
// Run two workers and assert the final count equals both contributions.
```

## C-M-098: scanf width omission

- Difficulty: Medium
- Language/platform: C
- Perspective: Parsing
- Concept: scanf width omission
- Symptom: Long input corrupts adjacent memory.
- Diagnostic goal: Bound formatted input by the destination capacity.

### Buggy code

```c
char word1[16];
scanf("%s", word1);
```

### Expected diagnosis

The conversion has no width limit, so input longer than 15 characters overflows the array.

### Corrected code

```c
char word1[16];
scanf("%15s", word1);
```

### Regression tests

```c
// A 100-character token must not overwrite memory.
```

## C-M-099: strncpy non-termination

- Difficulty: Medium
- Language/platform: C
- Perspective: API contract
- Concept: strncpy non-termination
- Symptom: The result is not a valid string for exact-length input.
- Diagnostic goal: Terminate explicitly after bounded copying.

### Buggy code

```c
strncpy(dst1, src1, sizeof dst1);
printf("%s", dst1);
```

### Expected diagnosis

strncpy does not append a terminator when the source fills the limit.

### Corrected code

```c
strncpy(dst1, src1, sizeof dst1 - 1);
dst1[sizeof dst1 - 1] = '\0';
```

### Regression tests

```c
// Exact-capacity source remains safely printable.
```

## C-M-100: early return leak

- Difficulty: Medium
- Language/platform: C
- Perspective: Cleanup
- Concept: early return leak
- Symptom: An error path leaks an allocation.
- Diagnostic goal: Centralize cleanup for all exits.

### Buggy code

```c
char *buffer = malloc(1024);
if (!buffer) return 0;
if (!read_data(buffer)) return -1;
free(buffer);
return 0;
```

### Expected diagnosis

The failed read returns before freeing buffer.

### Corrected code

```c
char *buffer = malloc(1024);
if (!buffer) return 0;
int result = read_data(buffer) ? 0 : -1;
free(buffer);
return result;
```

### Regression tests

```c
// Both read success and failure leave no allocation outstanding.
```

## C-H-001: off-by-one allocation

- Difficulty: Hard
- Language/platform: C
- Perspective: Memory safety
- Concept: off-by-one allocation
- Symptom: The last byte is overwritten.
- Diagnostic goal: Match allocation size to the largest valid index.

### Buggy code

```c
char *copy1(const char *s) {
    size_t n = strlen(s);
    char *out = malloc(n);
    memcpy(out, s, n + 1);
    return out;
}
```

### Expected diagnosis

The terminator requires n + 1 bytes; copying n + 1 bytes into n bytes is a heap overflow.

### Corrected code

```c
char *copy1(const char *s) {
    size_t n = strlen(s);
    char *out = malloc(n + 1);
    if (!out) return NULL;
    memcpy(out, s, n + 1);
    return out;
}
```

### Regression tests

```c
// Assert copy1("abc") is "abc" and allocation failure is handled.
```

## C-H-002: returning address of local

- Difficulty: Hard
- Language/platform: C
- Perspective: Pointer lifetime
- Concept: returning address of local
- Symptom: The caller reads garbage.
- Diagnostic goal: Ensure returned storage outlives the function.

### Buggy code

```c
int *value1(void) { int result = 7; return &result; }
```

### Expected diagnosis

A pointer to an automatic local object becomes invalid when the function returns.

### Corrected code

```c
int value1(void) { return 7; }
```

### Regression tests

```c
assert(value1() == 7);
```

## C-H-003: missing terminator

- Difficulty: Hard
- Language/platform: C
- Perspective: String API
- Concept: missing terminator
- Symptom: Printing reads beyond the buffer.
- Diagnostic goal: Reserve and write the C string terminator.

### Buggy code

```c
char name1[4];
memcpy(name1, "Ada", 3);
printf("%s", name1);
```

### Expected diagnosis

memcpy copies bytes only and does not append a terminator.

### Corrected code

```c
char name1[4];
memcpy(name1, "Ada", 3);
name1[3] = '\0';
```

### Regression tests

```c
assert(strcmp(name1, "Ada") == 0);
```

## C-H-004: signed overflow

- Difficulty: Hard
- Language/platform: C
- Perspective: Integer reasoning
- Concept: signed overflow
- Symptom: A boundary calculation produces undefined behavior.
- Diagnostic goal: Check before arithmetic or use an unsigned/wider representation.

### Buggy code

```c
int total1(int count, int size) { return count * size; }
```

### Expected diagnosis

Signed overflow is undefined in C; validating after the multiplication is too late.

### Corrected code

```c
bool total1(int count, int size, int *out) {
    if (count < 0 || size < 0 || count > INT_MAX / size) return false;
    *out = count * size;
    return true;
}
```

### Regression tests

```c
// Assert overflow returns false and a safe product returns true.
```

## C-H-005: double free

- Difficulty: Hard
- Language/platform: C
- Perspective: Ownership
- Concept: double free
- Symptom: The allocator reports corruption.
- Diagnostic goal: Assign ownership once and clear moved-from pointers.

### Buggy code

```c
void release1(char **p) { free(*p); free(*p); }
```

### Expected diagnosis

Freeing the same allocation twice is undefined behavior.

### Corrected code

```c
void release1(char **p) {
    if (p && *p) { free(*p); *p = NULL; }
}
```

### Regression tests

```c
// Call release1 twice; the second call is harmless.
```

## C-H-006: unchecked fopen

- Difficulty: Hard
- Language/platform: C
- Perspective: I/O contract
- Concept: unchecked fopen
- Symptom: A null FILE pointer is dereferenced.
- Diagnostic goal: Check resource acquisition before use.

### Buggy code

```c
FILE *f = fopen(path, "r");
char line[64];
fgets(line, sizeof line, f);
```

### Expected diagnosis

fopen returns NULL on failure; passing it to fgets is undefined behavior.

### Corrected code

```c
FILE *f = fopen(path, "r");
if (!f) return ERROR_OPEN;
char line[64];
if (!fgets(line, sizeof line, f)) { fclose(f); return ERROR_READ; }
fclose(f);
```

### Regression tests

```c
// Missing paths return an error without dereferencing NULL.
```

## C-H-007: data race

- Difficulty: Hard
- Language/platform: C
- Perspective: Concurrency
- Concept: data race
- Symptom: A counter loses increments under threads.
- Diagnostic goal: Synchronize shared mutable state.

### Buggy code

```c
shared_count1++;
```

### Expected diagnosis

Concurrent unsynchronized read-modify-write accesses form a data race and have undefined behavior.

### Corrected code

```c
pthread_mutex_lock(&count_mutex);
shared_count1++;
pthread_mutex_unlock(&count_mutex);
```

### Regression tests

```c
// Run two workers and assert the final count equals both contributions.
```

## C-H-008: scanf width omission

- Difficulty: Hard
- Language/platform: C
- Perspective: Parsing
- Concept: scanf width omission
- Symptom: Long input corrupts adjacent memory.
- Diagnostic goal: Bound formatted input by the destination capacity.

### Buggy code

```c
char word1[16];
scanf("%s", word1);
```

### Expected diagnosis

The conversion has no width limit, so input longer than 15 characters overflows the array.

### Corrected code

```c
char word1[16];
scanf("%15s", word1);
```

### Regression tests

```c
// A 100-character token must not overwrite memory.
```

## C-H-009: strncpy non-termination

- Difficulty: Hard
- Language/platform: C
- Perspective: API contract
- Concept: strncpy non-termination
- Symptom: The result is not a valid string for exact-length input.
- Diagnostic goal: Terminate explicitly after bounded copying.

### Buggy code

```c
strncpy(dst1, src1, sizeof dst1);
printf("%s", dst1);
```

### Expected diagnosis

strncpy does not append a terminator when the source fills the limit.

### Corrected code

```c
strncpy(dst1, src1, sizeof dst1 - 1);
dst1[sizeof dst1 - 1] = '\0';
```

### Regression tests

```c
// Exact-capacity source remains safely printable.
```

## C-H-010: early return leak

- Difficulty: Hard
- Language/platform: C
- Perspective: Cleanup
- Concept: early return leak
- Symptom: An error path leaks an allocation.
- Diagnostic goal: Centralize cleanup for all exits.

### Buggy code

```c
char *buffer = malloc(1024);
if (!buffer) return 0;
if (!read_data(buffer)) return -1;
free(buffer);
return 0;
```

### Expected diagnosis

The failed read returns before freeing buffer.

### Corrected code

```c
char *buffer = malloc(1024);
if (!buffer) return 0;
int result = read_data(buffer) ? 0 : -1;
free(buffer);
return result;
```

### Regression tests

```c
// Both read success and failure leave no allocation outstanding.
```

## C-H-011: off-by-one allocation

- Difficulty: Hard
- Language/platform: C
- Perspective: Memory safety
- Concept: off-by-one allocation
- Symptom: The last byte is overwritten.
- Diagnostic goal: Match allocation size to the largest valid index.

### Buggy code

```c
char *copy1(const char *s) {
    size_t n = strlen(s);
    char *out = malloc(n);
    memcpy(out, s, n + 1);
    return out;
}
```

### Expected diagnosis

The terminator requires n + 1 bytes; copying n + 1 bytes into n bytes is a heap overflow.

### Corrected code

```c
char *copy1(const char *s) {
    size_t n = strlen(s);
    char *out = malloc(n + 1);
    if (!out) return NULL;
    memcpy(out, s, n + 1);
    return out;
}
```

### Regression tests

```c
// Assert copy1("abc") is "abc" and allocation failure is handled.
```

## C-H-012: returning address of local

- Difficulty: Hard
- Language/platform: C
- Perspective: Pointer lifetime
- Concept: returning address of local
- Symptom: The caller reads garbage.
- Diagnostic goal: Ensure returned storage outlives the function.

### Buggy code

```c
int *value1(void) { int result = 7; return &result; }
```

### Expected diagnosis

A pointer to an automatic local object becomes invalid when the function returns.

### Corrected code

```c
int value1(void) { return 7; }
```

### Regression tests

```c
assert(value1() == 7);
```

## C-H-013: missing terminator

- Difficulty: Hard
- Language/platform: C
- Perspective: String API
- Concept: missing terminator
- Symptom: Printing reads beyond the buffer.
- Diagnostic goal: Reserve and write the C string terminator.

### Buggy code

```c
char name1[4];
memcpy(name1, "Ada", 3);
printf("%s", name1);
```

### Expected diagnosis

memcpy copies bytes only and does not append a terminator.

### Corrected code

```c
char name1[4];
memcpy(name1, "Ada", 3);
name1[3] = '\0';
```

### Regression tests

```c
assert(strcmp(name1, "Ada") == 0);
```

## C-H-014: signed overflow

- Difficulty: Hard
- Language/platform: C
- Perspective: Integer reasoning
- Concept: signed overflow
- Symptom: A boundary calculation produces undefined behavior.
- Diagnostic goal: Check before arithmetic or use an unsigned/wider representation.

### Buggy code

```c
int total1(int count, int size) { return count * size; }
```

### Expected diagnosis

Signed overflow is undefined in C; validating after the multiplication is too late.

### Corrected code

```c
bool total1(int count, int size, int *out) {
    if (count < 0 || size < 0 || count > INT_MAX / size) return false;
    *out = count * size;
    return true;
}
```

### Regression tests

```c
// Assert overflow returns false and a safe product returns true.
```

## C-H-015: double free

- Difficulty: Hard
- Language/platform: C
- Perspective: Ownership
- Concept: double free
- Symptom: The allocator reports corruption.
- Diagnostic goal: Assign ownership once and clear moved-from pointers.

### Buggy code

```c
void release1(char **p) { free(*p); free(*p); }
```

### Expected diagnosis

Freeing the same allocation twice is undefined behavior.

### Corrected code

```c
void release1(char **p) {
    if (p && *p) { free(*p); *p = NULL; }
}
```

### Regression tests

```c
// Call release1 twice; the second call is harmless.
```

## C-H-016: unchecked fopen

- Difficulty: Hard
- Language/platform: C
- Perspective: I/O contract
- Concept: unchecked fopen
- Symptom: A null FILE pointer is dereferenced.
- Diagnostic goal: Check resource acquisition before use.

### Buggy code

```c
FILE *f = fopen(path, "r");
char line[64];
fgets(line, sizeof line, f);
```

### Expected diagnosis

fopen returns NULL on failure; passing it to fgets is undefined behavior.

### Corrected code

```c
FILE *f = fopen(path, "r");
if (!f) return ERROR_OPEN;
char line[64];
if (!fgets(line, sizeof line, f)) { fclose(f); return ERROR_READ; }
fclose(f);
```

### Regression tests

```c
// Missing paths return an error without dereferencing NULL.
```

## C-H-017: data race

- Difficulty: Hard
- Language/platform: C
- Perspective: Concurrency
- Concept: data race
- Symptom: A counter loses increments under threads.
- Diagnostic goal: Synchronize shared mutable state.

### Buggy code

```c
shared_count1++;
```

### Expected diagnosis

Concurrent unsynchronized read-modify-write accesses form a data race and have undefined behavior.

### Corrected code

```c
pthread_mutex_lock(&count_mutex);
shared_count1++;
pthread_mutex_unlock(&count_mutex);
```

### Regression tests

```c
// Run two workers and assert the final count equals both contributions.
```

## C-H-018: scanf width omission

- Difficulty: Hard
- Language/platform: C
- Perspective: Parsing
- Concept: scanf width omission
- Symptom: Long input corrupts adjacent memory.
- Diagnostic goal: Bound formatted input by the destination capacity.

### Buggy code

```c
char word1[16];
scanf("%s", word1);
```

### Expected diagnosis

The conversion has no width limit, so input longer than 15 characters overflows the array.

### Corrected code

```c
char word1[16];
scanf("%15s", word1);
```

### Regression tests

```c
// A 100-character token must not overwrite memory.
```

## C-H-019: strncpy non-termination

- Difficulty: Hard
- Language/platform: C
- Perspective: API contract
- Concept: strncpy non-termination
- Symptom: The result is not a valid string for exact-length input.
- Diagnostic goal: Terminate explicitly after bounded copying.

### Buggy code

```c
strncpy(dst1, src1, sizeof dst1);
printf("%s", dst1);
```

### Expected diagnosis

strncpy does not append a terminator when the source fills the limit.

### Corrected code

```c
strncpy(dst1, src1, sizeof dst1 - 1);
dst1[sizeof dst1 - 1] = '\0';
```

### Regression tests

```c
// Exact-capacity source remains safely printable.
```

## C-H-020: early return leak

- Difficulty: Hard
- Language/platform: C
- Perspective: Cleanup
- Concept: early return leak
- Symptom: An error path leaks an allocation.
- Diagnostic goal: Centralize cleanup for all exits.

### Buggy code

```c
char *buffer = malloc(1024);
if (!buffer) return 0;
if (!read_data(buffer)) return -1;
free(buffer);
return 0;
```

### Expected diagnosis

The failed read returns before freeing buffer.

### Corrected code

```c
char *buffer = malloc(1024);
if (!buffer) return 0;
int result = read_data(buffer) ? 0 : -1;
free(buffer);
return result;
```

### Regression tests

```c
// Both read success and failure leave no allocation outstanding.
```

## C-H-021: off-by-one allocation

- Difficulty: Hard
- Language/platform: C
- Perspective: Memory safety
- Concept: off-by-one allocation
- Symptom: The last byte is overwritten.
- Diagnostic goal: Match allocation size to the largest valid index.

### Buggy code

```c
char *copy1(const char *s) {
    size_t n = strlen(s);
    char *out = malloc(n);
    memcpy(out, s, n + 1);
    return out;
}
```

### Expected diagnosis

The terminator requires n + 1 bytes; copying n + 1 bytes into n bytes is a heap overflow.

### Corrected code

```c
char *copy1(const char *s) {
    size_t n = strlen(s);
    char *out = malloc(n + 1);
    if (!out) return NULL;
    memcpy(out, s, n + 1);
    return out;
}
```

### Regression tests

```c
// Assert copy1("abc") is "abc" and allocation failure is handled.
```

## C-H-022: returning address of local

- Difficulty: Hard
- Language/platform: C
- Perspective: Pointer lifetime
- Concept: returning address of local
- Symptom: The caller reads garbage.
- Diagnostic goal: Ensure returned storage outlives the function.

### Buggy code

```c
int *value1(void) { int result = 7; return &result; }
```

### Expected diagnosis

A pointer to an automatic local object becomes invalid when the function returns.

### Corrected code

```c
int value1(void) { return 7; }
```

### Regression tests

```c
assert(value1() == 7);
```

## C-H-023: missing terminator

- Difficulty: Hard
- Language/platform: C
- Perspective: String API
- Concept: missing terminator
- Symptom: Printing reads beyond the buffer.
- Diagnostic goal: Reserve and write the C string terminator.

### Buggy code

```c
char name1[4];
memcpy(name1, "Ada", 3);
printf("%s", name1);
```

### Expected diagnosis

memcpy copies bytes only and does not append a terminator.

### Corrected code

```c
char name1[4];
memcpy(name1, "Ada", 3);
name1[3] = '\0';
```

### Regression tests

```c
assert(strcmp(name1, "Ada") == 0);
```

## C-H-024: signed overflow

- Difficulty: Hard
- Language/platform: C
- Perspective: Integer reasoning
- Concept: signed overflow
- Symptom: A boundary calculation produces undefined behavior.
- Diagnostic goal: Check before arithmetic or use an unsigned/wider representation.

### Buggy code

```c
int total1(int count, int size) { return count * size; }
```

### Expected diagnosis

Signed overflow is undefined in C; validating after the multiplication is too late.

### Corrected code

```c
bool total1(int count, int size, int *out) {
    if (count < 0 || size < 0 || count > INT_MAX / size) return false;
    *out = count * size;
    return true;
}
```

### Regression tests

```c
// Assert overflow returns false and a safe product returns true.
```

## C-H-025: double free

- Difficulty: Hard
- Language/platform: C
- Perspective: Ownership
- Concept: double free
- Symptom: The allocator reports corruption.
- Diagnostic goal: Assign ownership once and clear moved-from pointers.

### Buggy code

```c
void release1(char **p) { free(*p); free(*p); }
```

### Expected diagnosis

Freeing the same allocation twice is undefined behavior.

### Corrected code

```c
void release1(char **p) {
    if (p && *p) { free(*p); *p = NULL; }
}
```

### Regression tests

```c
// Call release1 twice; the second call is harmless.
```

## C-H-026: unchecked fopen

- Difficulty: Hard
- Language/platform: C
- Perspective: I/O contract
- Concept: unchecked fopen
- Symptom: A null FILE pointer is dereferenced.
- Diagnostic goal: Check resource acquisition before use.

### Buggy code

```c
FILE *f = fopen(path, "r");
char line[64];
fgets(line, sizeof line, f);
```

### Expected diagnosis

fopen returns NULL on failure; passing it to fgets is undefined behavior.

### Corrected code

```c
FILE *f = fopen(path, "r");
if (!f) return ERROR_OPEN;
char line[64];
if (!fgets(line, sizeof line, f)) { fclose(f); return ERROR_READ; }
fclose(f);
```

### Regression tests

```c
// Missing paths return an error without dereferencing NULL.
```

## C-H-027: data race

- Difficulty: Hard
- Language/platform: C
- Perspective: Concurrency
- Concept: data race
- Symptom: A counter loses increments under threads.
- Diagnostic goal: Synchronize shared mutable state.

### Buggy code

```c
shared_count1++;
```

### Expected diagnosis

Concurrent unsynchronized read-modify-write accesses form a data race and have undefined behavior.

### Corrected code

```c
pthread_mutex_lock(&count_mutex);
shared_count1++;
pthread_mutex_unlock(&count_mutex);
```

### Regression tests

```c
// Run two workers and assert the final count equals both contributions.
```

## C-H-028: scanf width omission

- Difficulty: Hard
- Language/platform: C
- Perspective: Parsing
- Concept: scanf width omission
- Symptom: Long input corrupts adjacent memory.
- Diagnostic goal: Bound formatted input by the destination capacity.

### Buggy code

```c
char word1[16];
scanf("%s", word1);
```

### Expected diagnosis

The conversion has no width limit, so input longer than 15 characters overflows the array.

### Corrected code

```c
char word1[16];
scanf("%15s", word1);
```

### Regression tests

```c
// A 100-character token must not overwrite memory.
```

## C-H-029: strncpy non-termination

- Difficulty: Hard
- Language/platform: C
- Perspective: API contract
- Concept: strncpy non-termination
- Symptom: The result is not a valid string for exact-length input.
- Diagnostic goal: Terminate explicitly after bounded copying.

### Buggy code

```c
strncpy(dst1, src1, sizeof dst1);
printf("%s", dst1);
```

### Expected diagnosis

strncpy does not append a terminator when the source fills the limit.

### Corrected code

```c
strncpy(dst1, src1, sizeof dst1 - 1);
dst1[sizeof dst1 - 1] = '\0';
```

### Regression tests

```c
// Exact-capacity source remains safely printable.
```

## C-H-030: early return leak

- Difficulty: Hard
- Language/platform: C
- Perspective: Cleanup
- Concept: early return leak
- Symptom: An error path leaks an allocation.
- Diagnostic goal: Centralize cleanup for all exits.

### Buggy code

```c
char *buffer = malloc(1024);
if (!buffer) return 0;
if (!read_data(buffer)) return -1;
free(buffer);
return 0;
```

### Expected diagnosis

The failed read returns before freeing buffer.

### Corrected code

```c
char *buffer = malloc(1024);
if (!buffer) return 0;
int result = read_data(buffer) ? 0 : -1;
free(buffer);
return result;
```

### Regression tests

```c
// Both read success and failure leave no allocation outstanding.
```

## C-H-031: off-by-one allocation

- Difficulty: Hard
- Language/platform: C
- Perspective: Memory safety
- Concept: off-by-one allocation
- Symptom: The last byte is overwritten.
- Diagnostic goal: Match allocation size to the largest valid index.

### Buggy code

```c
char *copy1(const char *s) {
    size_t n = strlen(s);
    char *out = malloc(n);
    memcpy(out, s, n + 1);
    return out;
}
```

### Expected diagnosis

The terminator requires n + 1 bytes; copying n + 1 bytes into n bytes is a heap overflow.

### Corrected code

```c
char *copy1(const char *s) {
    size_t n = strlen(s);
    char *out = malloc(n + 1);
    if (!out) return NULL;
    memcpy(out, s, n + 1);
    return out;
}
```

### Regression tests

```c
// Assert copy1("abc") is "abc" and allocation failure is handled.
```

## C-H-032: returning address of local

- Difficulty: Hard
- Language/platform: C
- Perspective: Pointer lifetime
- Concept: returning address of local
- Symptom: The caller reads garbage.
- Diagnostic goal: Ensure returned storage outlives the function.

### Buggy code

```c
int *value1(void) { int result = 7; return &result; }
```

### Expected diagnosis

A pointer to an automatic local object becomes invalid when the function returns.

### Corrected code

```c
int value1(void) { return 7; }
```

### Regression tests

```c
assert(value1() == 7);
```

## C-H-033: missing terminator

- Difficulty: Hard
- Language/platform: C
- Perspective: String API
- Concept: missing terminator
- Symptom: Printing reads beyond the buffer.
- Diagnostic goal: Reserve and write the C string terminator.

### Buggy code

```c
char name1[4];
memcpy(name1, "Ada", 3);
printf("%s", name1);
```

### Expected diagnosis

memcpy copies bytes only and does not append a terminator.

### Corrected code

```c
char name1[4];
memcpy(name1, "Ada", 3);
name1[3] = '\0';
```

### Regression tests

```c
assert(strcmp(name1, "Ada") == 0);
```

## C-H-034: signed overflow

- Difficulty: Hard
- Language/platform: C
- Perspective: Integer reasoning
- Concept: signed overflow
- Symptom: A boundary calculation produces undefined behavior.
- Diagnostic goal: Check before arithmetic or use an unsigned/wider representation.

### Buggy code

```c
int total1(int count, int size) { return count * size; }
```

### Expected diagnosis

Signed overflow is undefined in C; validating after the multiplication is too late.

### Corrected code

```c
bool total1(int count, int size, int *out) {
    if (count < 0 || size < 0 || count > INT_MAX / size) return false;
    *out = count * size;
    return true;
}
```

### Regression tests

```c
// Assert overflow returns false and a safe product returns true.
```

## C-H-035: double free

- Difficulty: Hard
- Language/platform: C
- Perspective: Ownership
- Concept: double free
- Symptom: The allocator reports corruption.
- Diagnostic goal: Assign ownership once and clear moved-from pointers.

### Buggy code

```c
void release1(char **p) { free(*p); free(*p); }
```

### Expected diagnosis

Freeing the same allocation twice is undefined behavior.

### Corrected code

```c
void release1(char **p) {
    if (p && *p) { free(*p); *p = NULL; }
}
```

### Regression tests

```c
// Call release1 twice; the second call is harmless.
```

## C-H-036: unchecked fopen

- Difficulty: Hard
- Language/platform: C
- Perspective: I/O contract
- Concept: unchecked fopen
- Symptom: A null FILE pointer is dereferenced.
- Diagnostic goal: Check resource acquisition before use.

### Buggy code

```c
FILE *f = fopen(path, "r");
char line[64];
fgets(line, sizeof line, f);
```

### Expected diagnosis

fopen returns NULL on failure; passing it to fgets is undefined behavior.

### Corrected code

```c
FILE *f = fopen(path, "r");
if (!f) return ERROR_OPEN;
char line[64];
if (!fgets(line, sizeof line, f)) { fclose(f); return ERROR_READ; }
fclose(f);
```

### Regression tests

```c
// Missing paths return an error without dereferencing NULL.
```

## C-H-037: data race

- Difficulty: Hard
- Language/platform: C
- Perspective: Concurrency
- Concept: data race
- Symptom: A counter loses increments under threads.
- Diagnostic goal: Synchronize shared mutable state.

### Buggy code

```c
shared_count1++;
```

### Expected diagnosis

Concurrent unsynchronized read-modify-write accesses form a data race and have undefined behavior.

### Corrected code

```c
pthread_mutex_lock(&count_mutex);
shared_count1++;
pthread_mutex_unlock(&count_mutex);
```

### Regression tests

```c
// Run two workers and assert the final count equals both contributions.
```

## C-H-038: scanf width omission

- Difficulty: Hard
- Language/platform: C
- Perspective: Parsing
- Concept: scanf width omission
- Symptom: Long input corrupts adjacent memory.
- Diagnostic goal: Bound formatted input by the destination capacity.

### Buggy code

```c
char word1[16];
scanf("%s", word1);
```

### Expected diagnosis

The conversion has no width limit, so input longer than 15 characters overflows the array.

### Corrected code

```c
char word1[16];
scanf("%15s", word1);
```

### Regression tests

```c
// A 100-character token must not overwrite memory.
```

## C-H-039: strncpy non-termination

- Difficulty: Hard
- Language/platform: C
- Perspective: API contract
- Concept: strncpy non-termination
- Symptom: The result is not a valid string for exact-length input.
- Diagnostic goal: Terminate explicitly after bounded copying.

### Buggy code

```c
strncpy(dst1, src1, sizeof dst1);
printf("%s", dst1);
```

### Expected diagnosis

strncpy does not append a terminator when the source fills the limit.

### Corrected code

```c
strncpy(dst1, src1, sizeof dst1 - 1);
dst1[sizeof dst1 - 1] = '\0';
```

### Regression tests

```c
// Exact-capacity source remains safely printable.
```

## C-H-040: early return leak

- Difficulty: Hard
- Language/platform: C
- Perspective: Cleanup
- Concept: early return leak
- Symptom: An error path leaks an allocation.
- Diagnostic goal: Centralize cleanup for all exits.

### Buggy code

```c
char *buffer = malloc(1024);
if (!buffer) return 0;
if (!read_data(buffer)) return -1;
free(buffer);
return 0;
```

### Expected diagnosis

The failed read returns before freeing buffer.

### Corrected code

```c
char *buffer = malloc(1024);
if (!buffer) return 0;
int result = read_data(buffer) ? 0 : -1;
free(buffer);
return result;
```

### Regression tests

```c
// Both read success and failure leave no allocation outstanding.
```

## C-H-041: off-by-one allocation

- Difficulty: Hard
- Language/platform: C
- Perspective: Memory safety
- Concept: off-by-one allocation
- Symptom: The last byte is overwritten.
- Diagnostic goal: Match allocation size to the largest valid index.

### Buggy code

```c
char *copy1(const char *s) {
    size_t n = strlen(s);
    char *out = malloc(n);
    memcpy(out, s, n + 1);
    return out;
}
```

### Expected diagnosis

The terminator requires n + 1 bytes; copying n + 1 bytes into n bytes is a heap overflow.

### Corrected code

```c
char *copy1(const char *s) {
    size_t n = strlen(s);
    char *out = malloc(n + 1);
    if (!out) return NULL;
    memcpy(out, s, n + 1);
    return out;
}
```

### Regression tests

```c
// Assert copy1("abc") is "abc" and allocation failure is handled.
```

## C-H-042: returning address of local

- Difficulty: Hard
- Language/platform: C
- Perspective: Pointer lifetime
- Concept: returning address of local
- Symptom: The caller reads garbage.
- Diagnostic goal: Ensure returned storage outlives the function.

### Buggy code

```c
int *value1(void) { int result = 7; return &result; }
```

### Expected diagnosis

A pointer to an automatic local object becomes invalid when the function returns.

### Corrected code

```c
int value1(void) { return 7; }
```

### Regression tests

```c
assert(value1() == 7);
```

## C-H-043: missing terminator

- Difficulty: Hard
- Language/platform: C
- Perspective: String API
- Concept: missing terminator
- Symptom: Printing reads beyond the buffer.
- Diagnostic goal: Reserve and write the C string terminator.

### Buggy code

```c
char name1[4];
memcpy(name1, "Ada", 3);
printf("%s", name1);
```

### Expected diagnosis

memcpy copies bytes only and does not append a terminator.

### Corrected code

```c
char name1[4];
memcpy(name1, "Ada", 3);
name1[3] = '\0';
```

### Regression tests

```c
assert(strcmp(name1, "Ada") == 0);
```

## C-H-044: signed overflow

- Difficulty: Hard
- Language/platform: C
- Perspective: Integer reasoning
- Concept: signed overflow
- Symptom: A boundary calculation produces undefined behavior.
- Diagnostic goal: Check before arithmetic or use an unsigned/wider representation.

### Buggy code

```c
int total1(int count, int size) { return count * size; }
```

### Expected diagnosis

Signed overflow is undefined in C; validating after the multiplication is too late.

### Corrected code

```c
bool total1(int count, int size, int *out) {
    if (count < 0 || size < 0 || count > INT_MAX / size) return false;
    *out = count * size;
    return true;
}
```

### Regression tests

```c
// Assert overflow returns false and a safe product returns true.
```

## C-H-045: double free

- Difficulty: Hard
- Language/platform: C
- Perspective: Ownership
- Concept: double free
- Symptom: The allocator reports corruption.
- Diagnostic goal: Assign ownership once and clear moved-from pointers.

### Buggy code

```c
void release1(char **p) { free(*p); free(*p); }
```

### Expected diagnosis

Freeing the same allocation twice is undefined behavior.

### Corrected code

```c
void release1(char **p) {
    if (p && *p) { free(*p); *p = NULL; }
}
```

### Regression tests

```c
// Call release1 twice; the second call is harmless.
```

## C-H-046: unchecked fopen

- Difficulty: Hard
- Language/platform: C
- Perspective: I/O contract
- Concept: unchecked fopen
- Symptom: A null FILE pointer is dereferenced.
- Diagnostic goal: Check resource acquisition before use.

### Buggy code

```c
FILE *f = fopen(path, "r");
char line[64];
fgets(line, sizeof line, f);
```

### Expected diagnosis

fopen returns NULL on failure; passing it to fgets is undefined behavior.

### Corrected code

```c
FILE *f = fopen(path, "r");
if (!f) return ERROR_OPEN;
char line[64];
if (!fgets(line, sizeof line, f)) { fclose(f); return ERROR_READ; }
fclose(f);
```

### Regression tests

```c
// Missing paths return an error without dereferencing NULL.
```

## C-H-047: data race

- Difficulty: Hard
- Language/platform: C
- Perspective: Concurrency
- Concept: data race
- Symptom: A counter loses increments under threads.
- Diagnostic goal: Synchronize shared mutable state.

### Buggy code

```c
shared_count1++;
```

### Expected diagnosis

Concurrent unsynchronized read-modify-write accesses form a data race and have undefined behavior.

### Corrected code

```c
pthread_mutex_lock(&count_mutex);
shared_count1++;
pthread_mutex_unlock(&count_mutex);
```

### Regression tests

```c
// Run two workers and assert the final count equals both contributions.
```

## C-H-048: scanf width omission

- Difficulty: Hard
- Language/platform: C
- Perspective: Parsing
- Concept: scanf width omission
- Symptom: Long input corrupts adjacent memory.
- Diagnostic goal: Bound formatted input by the destination capacity.

### Buggy code

```c
char word1[16];
scanf("%s", word1);
```

### Expected diagnosis

The conversion has no width limit, so input longer than 15 characters overflows the array.

### Corrected code

```c
char word1[16];
scanf("%15s", word1);
```

### Regression tests

```c
// A 100-character token must not overwrite memory.
```

## C-H-049: strncpy non-termination

- Difficulty: Hard
- Language/platform: C
- Perspective: API contract
- Concept: strncpy non-termination
- Symptom: The result is not a valid string for exact-length input.
- Diagnostic goal: Terminate explicitly after bounded copying.

### Buggy code

```c
strncpy(dst1, src1, sizeof dst1);
printf("%s", dst1);
```

### Expected diagnosis

strncpy does not append a terminator when the source fills the limit.

### Corrected code

```c
strncpy(dst1, src1, sizeof dst1 - 1);
dst1[sizeof dst1 - 1] = '\0';
```

### Regression tests

```c
// Exact-capacity source remains safely printable.
```

## C-H-050: early return leak

- Difficulty: Hard
- Language/platform: C
- Perspective: Cleanup
- Concept: early return leak
- Symptom: An error path leaks an allocation.
- Diagnostic goal: Centralize cleanup for all exits.

### Buggy code

```c
char *buffer = malloc(1024);
if (!buffer) return 0;
if (!read_data(buffer)) return -1;
free(buffer);
return 0;
```

### Expected diagnosis

The failed read returns before freeing buffer.

### Corrected code

```c
char *buffer = malloc(1024);
if (!buffer) return 0;
int result = read_data(buffer) ? 0 : -1;
free(buffer);
return result;
```

### Regression tests

```c
// Both read success and failure leave no allocation outstanding.
```

## C-H-051: off-by-one allocation

- Difficulty: Hard
- Language/platform: C
- Perspective: Memory safety
- Concept: off-by-one allocation
- Symptom: The last byte is overwritten.
- Diagnostic goal: Match allocation size to the largest valid index.

### Buggy code

```c
char *copy1(const char *s) {
    size_t n = strlen(s);
    char *out = malloc(n);
    memcpy(out, s, n + 1);
    return out;
}
```

### Expected diagnosis

The terminator requires n + 1 bytes; copying n + 1 bytes into n bytes is a heap overflow.

### Corrected code

```c
char *copy1(const char *s) {
    size_t n = strlen(s);
    char *out = malloc(n + 1);
    if (!out) return NULL;
    memcpy(out, s, n + 1);
    return out;
}
```

### Regression tests

```c
// Assert copy1("abc") is "abc" and allocation failure is handled.
```

## C-H-052: returning address of local

- Difficulty: Hard
- Language/platform: C
- Perspective: Pointer lifetime
- Concept: returning address of local
- Symptom: The caller reads garbage.
- Diagnostic goal: Ensure returned storage outlives the function.

### Buggy code

```c
int *value1(void) { int result = 7; return &result; }
```

### Expected diagnosis

A pointer to an automatic local object becomes invalid when the function returns.

### Corrected code

```c
int value1(void) { return 7; }
```

### Regression tests

```c
assert(value1() == 7);
```

## C-H-053: missing terminator

- Difficulty: Hard
- Language/platform: C
- Perspective: String API
- Concept: missing terminator
- Symptom: Printing reads beyond the buffer.
- Diagnostic goal: Reserve and write the C string terminator.

### Buggy code

```c
char name1[4];
memcpy(name1, "Ada", 3);
printf("%s", name1);
```

### Expected diagnosis

memcpy copies bytes only and does not append a terminator.

### Corrected code

```c
char name1[4];
memcpy(name1, "Ada", 3);
name1[3] = '\0';
```

### Regression tests

```c
assert(strcmp(name1, "Ada") == 0);
```

## C-H-054: signed overflow

- Difficulty: Hard
- Language/platform: C
- Perspective: Integer reasoning
- Concept: signed overflow
- Symptom: A boundary calculation produces undefined behavior.
- Diagnostic goal: Check before arithmetic or use an unsigned/wider representation.

### Buggy code

```c
int total1(int count, int size) { return count * size; }
```

### Expected diagnosis

Signed overflow is undefined in C; validating after the multiplication is too late.

### Corrected code

```c
bool total1(int count, int size, int *out) {
    if (count < 0 || size < 0 || count > INT_MAX / size) return false;
    *out = count * size;
    return true;
}
```

### Regression tests

```c
// Assert overflow returns false and a safe product returns true.
```

## C-H-055: double free

- Difficulty: Hard
- Language/platform: C
- Perspective: Ownership
- Concept: double free
- Symptom: The allocator reports corruption.
- Diagnostic goal: Assign ownership once and clear moved-from pointers.

### Buggy code

```c
void release1(char **p) { free(*p); free(*p); }
```

### Expected diagnosis

Freeing the same allocation twice is undefined behavior.

### Corrected code

```c
void release1(char **p) {
    if (p && *p) { free(*p); *p = NULL; }
}
```

### Regression tests

```c
// Call release1 twice; the second call is harmless.
```

## C-H-056: unchecked fopen

- Difficulty: Hard
- Language/platform: C
- Perspective: I/O contract
- Concept: unchecked fopen
- Symptom: A null FILE pointer is dereferenced.
- Diagnostic goal: Check resource acquisition before use.

### Buggy code

```c
FILE *f = fopen(path, "r");
char line[64];
fgets(line, sizeof line, f);
```

### Expected diagnosis

fopen returns NULL on failure; passing it to fgets is undefined behavior.

### Corrected code

```c
FILE *f = fopen(path, "r");
if (!f) return ERROR_OPEN;
char line[64];
if (!fgets(line, sizeof line, f)) { fclose(f); return ERROR_READ; }
fclose(f);
```

### Regression tests

```c
// Missing paths return an error without dereferencing NULL.
```

## C-H-057: data race

- Difficulty: Hard
- Language/platform: C
- Perspective: Concurrency
- Concept: data race
- Symptom: A counter loses increments under threads.
- Diagnostic goal: Synchronize shared mutable state.

### Buggy code

```c
shared_count1++;
```

### Expected diagnosis

Concurrent unsynchronized read-modify-write accesses form a data race and have undefined behavior.

### Corrected code

```c
pthread_mutex_lock(&count_mutex);
shared_count1++;
pthread_mutex_unlock(&count_mutex);
```

### Regression tests

```c
// Run two workers and assert the final count equals both contributions.
```

## C-H-058: scanf width omission

- Difficulty: Hard
- Language/platform: C
- Perspective: Parsing
- Concept: scanf width omission
- Symptom: Long input corrupts adjacent memory.
- Diagnostic goal: Bound formatted input by the destination capacity.

### Buggy code

```c
char word1[16];
scanf("%s", word1);
```

### Expected diagnosis

The conversion has no width limit, so input longer than 15 characters overflows the array.

### Corrected code

```c
char word1[16];
scanf("%15s", word1);
```

### Regression tests

```c
// A 100-character token must not overwrite memory.
```

## C-H-059: strncpy non-termination

- Difficulty: Hard
- Language/platform: C
- Perspective: API contract
- Concept: strncpy non-termination
- Symptom: The result is not a valid string for exact-length input.
- Diagnostic goal: Terminate explicitly after bounded copying.

### Buggy code

```c
strncpy(dst1, src1, sizeof dst1);
printf("%s", dst1);
```

### Expected diagnosis

strncpy does not append a terminator when the source fills the limit.

### Corrected code

```c
strncpy(dst1, src1, sizeof dst1 - 1);
dst1[sizeof dst1 - 1] = '\0';
```

### Regression tests

```c
// Exact-capacity source remains safely printable.
```

## C-H-060: early return leak

- Difficulty: Hard
- Language/platform: C
- Perspective: Cleanup
- Concept: early return leak
- Symptom: An error path leaks an allocation.
- Diagnostic goal: Centralize cleanup for all exits.

### Buggy code

```c
char *buffer = malloc(1024);
if (!buffer) return 0;
if (!read_data(buffer)) return -1;
free(buffer);
return 0;
```

### Expected diagnosis

The failed read returns before freeing buffer.

### Corrected code

```c
char *buffer = malloc(1024);
if (!buffer) return 0;
int result = read_data(buffer) ? 0 : -1;
free(buffer);
return result;
```

### Regression tests

```c
// Both read success and failure leave no allocation outstanding.
```

## C-H-061: off-by-one allocation

- Difficulty: Hard
- Language/platform: C
- Perspective: Memory safety
- Concept: off-by-one allocation
- Symptom: The last byte is overwritten.
- Diagnostic goal: Match allocation size to the largest valid index.

### Buggy code

```c
char *copy1(const char *s) {
    size_t n = strlen(s);
    char *out = malloc(n);
    memcpy(out, s, n + 1);
    return out;
}
```

### Expected diagnosis

The terminator requires n + 1 bytes; copying n + 1 bytes into n bytes is a heap overflow.

### Corrected code

```c
char *copy1(const char *s) {
    size_t n = strlen(s);
    char *out = malloc(n + 1);
    if (!out) return NULL;
    memcpy(out, s, n + 1);
    return out;
}
```

### Regression tests

```c
// Assert copy1("abc") is "abc" and allocation failure is handled.
```

## C-H-062: returning address of local

- Difficulty: Hard
- Language/platform: C
- Perspective: Pointer lifetime
- Concept: returning address of local
- Symptom: The caller reads garbage.
- Diagnostic goal: Ensure returned storage outlives the function.

### Buggy code

```c
int *value1(void) { int result = 7; return &result; }
```

### Expected diagnosis

A pointer to an automatic local object becomes invalid when the function returns.

### Corrected code

```c
int value1(void) { return 7; }
```

### Regression tests

```c
assert(value1() == 7);
```

## C-H-063: missing terminator

- Difficulty: Hard
- Language/platform: C
- Perspective: String API
- Concept: missing terminator
- Symptom: Printing reads beyond the buffer.
- Diagnostic goal: Reserve and write the C string terminator.

### Buggy code

```c
char name1[4];
memcpy(name1, "Ada", 3);
printf("%s", name1);
```

### Expected diagnosis

memcpy copies bytes only and does not append a terminator.

### Corrected code

```c
char name1[4];
memcpy(name1, "Ada", 3);
name1[3] = '\0';
```

### Regression tests

```c
assert(strcmp(name1, "Ada") == 0);
```

## C-H-064: signed overflow

- Difficulty: Hard
- Language/platform: C
- Perspective: Integer reasoning
- Concept: signed overflow
- Symptom: A boundary calculation produces undefined behavior.
- Diagnostic goal: Check before arithmetic or use an unsigned/wider representation.

### Buggy code

```c
int total1(int count, int size) { return count * size; }
```

### Expected diagnosis

Signed overflow is undefined in C; validating after the multiplication is too late.

### Corrected code

```c
bool total1(int count, int size, int *out) {
    if (count < 0 || size < 0 || count > INT_MAX / size) return false;
    *out = count * size;
    return true;
}
```

### Regression tests

```c
// Assert overflow returns false and a safe product returns true.
```

## C-H-065: double free

- Difficulty: Hard
- Language/platform: C
- Perspective: Ownership
- Concept: double free
- Symptom: The allocator reports corruption.
- Diagnostic goal: Assign ownership once and clear moved-from pointers.

### Buggy code

```c
void release1(char **p) { free(*p); free(*p); }
```

### Expected diagnosis

Freeing the same allocation twice is undefined behavior.

### Corrected code

```c
void release1(char **p) {
    if (p && *p) { free(*p); *p = NULL; }
}
```

### Regression tests

```c
// Call release1 twice; the second call is harmless.
```

## C-H-066: unchecked fopen

- Difficulty: Hard
- Language/platform: C
- Perspective: I/O contract
- Concept: unchecked fopen
- Symptom: A null FILE pointer is dereferenced.
- Diagnostic goal: Check resource acquisition before use.

### Buggy code

```c
FILE *f = fopen(path, "r");
char line[64];
fgets(line, sizeof line, f);
```

### Expected diagnosis

fopen returns NULL on failure; passing it to fgets is undefined behavior.

### Corrected code

```c
FILE *f = fopen(path, "r");
if (!f) return ERROR_OPEN;
char line[64];
if (!fgets(line, sizeof line, f)) { fclose(f); return ERROR_READ; }
fclose(f);
```

### Regression tests

```c
// Missing paths return an error without dereferencing NULL.
```

## C-H-067: data race

- Difficulty: Hard
- Language/platform: C
- Perspective: Concurrency
- Concept: data race
- Symptom: A counter loses increments under threads.
- Diagnostic goal: Synchronize shared mutable state.

### Buggy code

```c
shared_count1++;
```

### Expected diagnosis

Concurrent unsynchronized read-modify-write accesses form a data race and have undefined behavior.

### Corrected code

```c
pthread_mutex_lock(&count_mutex);
shared_count1++;
pthread_mutex_unlock(&count_mutex);
```

### Regression tests

```c
// Run two workers and assert the final count equals both contributions.
```

## C-H-068: scanf width omission

- Difficulty: Hard
- Language/platform: C
- Perspective: Parsing
- Concept: scanf width omission
- Symptom: Long input corrupts adjacent memory.
- Diagnostic goal: Bound formatted input by the destination capacity.

### Buggy code

```c
char word1[16];
scanf("%s", word1);
```

### Expected diagnosis

The conversion has no width limit, so input longer than 15 characters overflows the array.

### Corrected code

```c
char word1[16];
scanf("%15s", word1);
```

### Regression tests

```c
// A 100-character token must not overwrite memory.
```

## C-H-069: strncpy non-termination

- Difficulty: Hard
- Language/platform: C
- Perspective: API contract
- Concept: strncpy non-termination
- Symptom: The result is not a valid string for exact-length input.
- Diagnostic goal: Terminate explicitly after bounded copying.

### Buggy code

```c
strncpy(dst1, src1, sizeof dst1);
printf("%s", dst1);
```

### Expected diagnosis

strncpy does not append a terminator when the source fills the limit.

### Corrected code

```c
strncpy(dst1, src1, sizeof dst1 - 1);
dst1[sizeof dst1 - 1] = '\0';
```

### Regression tests

```c
// Exact-capacity source remains safely printable.
```

## C-H-070: early return leak

- Difficulty: Hard
- Language/platform: C
- Perspective: Cleanup
- Concept: early return leak
- Symptom: An error path leaks an allocation.
- Diagnostic goal: Centralize cleanup for all exits.

### Buggy code

```c
char *buffer = malloc(1024);
if (!buffer) return 0;
if (!read_data(buffer)) return -1;
free(buffer);
return 0;
```

### Expected diagnosis

The failed read returns before freeing buffer.

### Corrected code

```c
char *buffer = malloc(1024);
if (!buffer) return 0;
int result = read_data(buffer) ? 0 : -1;
free(buffer);
return result;
```

### Regression tests

```c
// Both read success and failure leave no allocation outstanding.
```

## C-H-071: off-by-one allocation

- Difficulty: Hard
- Language/platform: C
- Perspective: Memory safety
- Concept: off-by-one allocation
- Symptom: The last byte is overwritten.
- Diagnostic goal: Match allocation size to the largest valid index.

### Buggy code

```c
char *copy1(const char *s) {
    size_t n = strlen(s);
    char *out = malloc(n);
    memcpy(out, s, n + 1);
    return out;
}
```

### Expected diagnosis

The terminator requires n + 1 bytes; copying n + 1 bytes into n bytes is a heap overflow.

### Corrected code

```c
char *copy1(const char *s) {
    size_t n = strlen(s);
    char *out = malloc(n + 1);
    if (!out) return NULL;
    memcpy(out, s, n + 1);
    return out;
}
```

### Regression tests

```c
// Assert copy1("abc") is "abc" and allocation failure is handled.
```

## C-H-072: returning address of local

- Difficulty: Hard
- Language/platform: C
- Perspective: Pointer lifetime
- Concept: returning address of local
- Symptom: The caller reads garbage.
- Diagnostic goal: Ensure returned storage outlives the function.

### Buggy code

```c
int *value1(void) { int result = 7; return &result; }
```

### Expected diagnosis

A pointer to an automatic local object becomes invalid when the function returns.

### Corrected code

```c
int value1(void) { return 7; }
```

### Regression tests

```c
assert(value1() == 7);
```

## C-H-073: missing terminator

- Difficulty: Hard
- Language/platform: C
- Perspective: String API
- Concept: missing terminator
- Symptom: Printing reads beyond the buffer.
- Diagnostic goal: Reserve and write the C string terminator.

### Buggy code

```c
char name1[4];
memcpy(name1, "Ada", 3);
printf("%s", name1);
```

### Expected diagnosis

memcpy copies bytes only and does not append a terminator.

### Corrected code

```c
char name1[4];
memcpy(name1, "Ada", 3);
name1[3] = '\0';
```

### Regression tests

```c
assert(strcmp(name1, "Ada") == 0);
```

## C-H-074: signed overflow

- Difficulty: Hard
- Language/platform: C
- Perspective: Integer reasoning
- Concept: signed overflow
- Symptom: A boundary calculation produces undefined behavior.
- Diagnostic goal: Check before arithmetic or use an unsigned/wider representation.

### Buggy code

```c
int total1(int count, int size) { return count * size; }
```

### Expected diagnosis

Signed overflow is undefined in C; validating after the multiplication is too late.

### Corrected code

```c
bool total1(int count, int size, int *out) {
    if (count < 0 || size < 0 || count > INT_MAX / size) return false;
    *out = count * size;
    return true;
}
```

### Regression tests

```c
// Assert overflow returns false and a safe product returns true.
```

## C-H-075: double free

- Difficulty: Hard
- Language/platform: C
- Perspective: Ownership
- Concept: double free
- Symptom: The allocator reports corruption.
- Diagnostic goal: Assign ownership once and clear moved-from pointers.

### Buggy code

```c
void release1(char **p) { free(*p); free(*p); }
```

### Expected diagnosis

Freeing the same allocation twice is undefined behavior.

### Corrected code

```c
void release1(char **p) {
    if (p && *p) { free(*p); *p = NULL; }
}
```

### Regression tests

```c
// Call release1 twice; the second call is harmless.
```

## C-H-076: unchecked fopen

- Difficulty: Hard
- Language/platform: C
- Perspective: I/O contract
- Concept: unchecked fopen
- Symptom: A null FILE pointer is dereferenced.
- Diagnostic goal: Check resource acquisition before use.

### Buggy code

```c
FILE *f = fopen(path, "r");
char line[64];
fgets(line, sizeof line, f);
```

### Expected diagnosis

fopen returns NULL on failure; passing it to fgets is undefined behavior.

### Corrected code

```c
FILE *f = fopen(path, "r");
if (!f) return ERROR_OPEN;
char line[64];
if (!fgets(line, sizeof line, f)) { fclose(f); return ERROR_READ; }
fclose(f);
```

### Regression tests

```c
// Missing paths return an error without dereferencing NULL.
```

## C-H-077: data race

- Difficulty: Hard
- Language/platform: C
- Perspective: Concurrency
- Concept: data race
- Symptom: A counter loses increments under threads.
- Diagnostic goal: Synchronize shared mutable state.

### Buggy code

```c
shared_count1++;
```

### Expected diagnosis

Concurrent unsynchronized read-modify-write accesses form a data race and have undefined behavior.

### Corrected code

```c
pthread_mutex_lock(&count_mutex);
shared_count1++;
pthread_mutex_unlock(&count_mutex);
```

### Regression tests

```c
// Run two workers and assert the final count equals both contributions.
```

## C-H-078: scanf width omission

- Difficulty: Hard
- Language/platform: C
- Perspective: Parsing
- Concept: scanf width omission
- Symptom: Long input corrupts adjacent memory.
- Diagnostic goal: Bound formatted input by the destination capacity.

### Buggy code

```c
char word1[16];
scanf("%s", word1);
```

### Expected diagnosis

The conversion has no width limit, so input longer than 15 characters overflows the array.

### Corrected code

```c
char word1[16];
scanf("%15s", word1);
```

### Regression tests

```c
// A 100-character token must not overwrite memory.
```

## C-H-079: strncpy non-termination

- Difficulty: Hard
- Language/platform: C
- Perspective: API contract
- Concept: strncpy non-termination
- Symptom: The result is not a valid string for exact-length input.
- Diagnostic goal: Terminate explicitly after bounded copying.

### Buggy code

```c
strncpy(dst1, src1, sizeof dst1);
printf("%s", dst1);
```

### Expected diagnosis

strncpy does not append a terminator when the source fills the limit.

### Corrected code

```c
strncpy(dst1, src1, sizeof dst1 - 1);
dst1[sizeof dst1 - 1] = '\0';
```

### Regression tests

```c
// Exact-capacity source remains safely printable.
```

## C-H-080: early return leak

- Difficulty: Hard
- Language/platform: C
- Perspective: Cleanup
- Concept: early return leak
- Symptom: An error path leaks an allocation.
- Diagnostic goal: Centralize cleanup for all exits.

### Buggy code

```c
char *buffer = malloc(1024);
if (!buffer) return 0;
if (!read_data(buffer)) return -1;
free(buffer);
return 0;
```

### Expected diagnosis

The failed read returns before freeing buffer.

### Corrected code

```c
char *buffer = malloc(1024);
if (!buffer) return 0;
int result = read_data(buffer) ? 0 : -1;
free(buffer);
return result;
```

### Regression tests

```c
// Both read success and failure leave no allocation outstanding.
```

## C-H-081: off-by-one allocation

- Difficulty: Hard
- Language/platform: C
- Perspective: Memory safety
- Concept: off-by-one allocation
- Symptom: The last byte is overwritten.
- Diagnostic goal: Match allocation size to the largest valid index.

### Buggy code

```c
char *copy1(const char *s) {
    size_t n = strlen(s);
    char *out = malloc(n);
    memcpy(out, s, n + 1);
    return out;
}
```

### Expected diagnosis

The terminator requires n + 1 bytes; copying n + 1 bytes into n bytes is a heap overflow.

### Corrected code

```c
char *copy1(const char *s) {
    size_t n = strlen(s);
    char *out = malloc(n + 1);
    if (!out) return NULL;
    memcpy(out, s, n + 1);
    return out;
}
```

### Regression tests

```c
// Assert copy1("abc") is "abc" and allocation failure is handled.
```

## C-H-082: returning address of local

- Difficulty: Hard
- Language/platform: C
- Perspective: Pointer lifetime
- Concept: returning address of local
- Symptom: The caller reads garbage.
- Diagnostic goal: Ensure returned storage outlives the function.

### Buggy code

```c
int *value1(void) { int result = 7; return &result; }
```

### Expected diagnosis

A pointer to an automatic local object becomes invalid when the function returns.

### Corrected code

```c
int value1(void) { return 7; }
```

### Regression tests

```c
assert(value1() == 7);
```

## C-H-083: missing terminator

- Difficulty: Hard
- Language/platform: C
- Perspective: String API
- Concept: missing terminator
- Symptom: Printing reads beyond the buffer.
- Diagnostic goal: Reserve and write the C string terminator.

### Buggy code

```c
char name1[4];
memcpy(name1, "Ada", 3);
printf("%s", name1);
```

### Expected diagnosis

memcpy copies bytes only and does not append a terminator.

### Corrected code

```c
char name1[4];
memcpy(name1, "Ada", 3);
name1[3] = '\0';
```

### Regression tests

```c
assert(strcmp(name1, "Ada") == 0);
```

## C-H-084: signed overflow

- Difficulty: Hard
- Language/platform: C
- Perspective: Integer reasoning
- Concept: signed overflow
- Symptom: A boundary calculation produces undefined behavior.
- Diagnostic goal: Check before arithmetic or use an unsigned/wider representation.

### Buggy code

```c
int total1(int count, int size) { return count * size; }
```

### Expected diagnosis

Signed overflow is undefined in C; validating after the multiplication is too late.

### Corrected code

```c
bool total1(int count, int size, int *out) {
    if (count < 0 || size < 0 || count > INT_MAX / size) return false;
    *out = count * size;
    return true;
}
```

### Regression tests

```c
// Assert overflow returns false and a safe product returns true.
```

## C-H-085: double free

- Difficulty: Hard
- Language/platform: C
- Perspective: Ownership
- Concept: double free
- Symptom: The allocator reports corruption.
- Diagnostic goal: Assign ownership once and clear moved-from pointers.

### Buggy code

```c
void release1(char **p) { free(*p); free(*p); }
```

### Expected diagnosis

Freeing the same allocation twice is undefined behavior.

### Corrected code

```c
void release1(char **p) {
    if (p && *p) { free(*p); *p = NULL; }
}
```

### Regression tests

```c
// Call release1 twice; the second call is harmless.
```

## C-H-086: unchecked fopen

- Difficulty: Hard
- Language/platform: C
- Perspective: I/O contract
- Concept: unchecked fopen
- Symptom: A null FILE pointer is dereferenced.
- Diagnostic goal: Check resource acquisition before use.

### Buggy code

```c
FILE *f = fopen(path, "r");
char line[64];
fgets(line, sizeof line, f);
```

### Expected diagnosis

fopen returns NULL on failure; passing it to fgets is undefined behavior.

### Corrected code

```c
FILE *f = fopen(path, "r");
if (!f) return ERROR_OPEN;
char line[64];
if (!fgets(line, sizeof line, f)) { fclose(f); return ERROR_READ; }
fclose(f);
```

### Regression tests

```c
// Missing paths return an error without dereferencing NULL.
```

## C-H-087: data race

- Difficulty: Hard
- Language/platform: C
- Perspective: Concurrency
- Concept: data race
- Symptom: A counter loses increments under threads.
- Diagnostic goal: Synchronize shared mutable state.

### Buggy code

```c
shared_count1++;
```

### Expected diagnosis

Concurrent unsynchronized read-modify-write accesses form a data race and have undefined behavior.

### Corrected code

```c
pthread_mutex_lock(&count_mutex);
shared_count1++;
pthread_mutex_unlock(&count_mutex);
```

### Regression tests

```c
// Run two workers and assert the final count equals both contributions.
```

## C-H-088: scanf width omission

- Difficulty: Hard
- Language/platform: C
- Perspective: Parsing
- Concept: scanf width omission
- Symptom: Long input corrupts adjacent memory.
- Diagnostic goal: Bound formatted input by the destination capacity.

### Buggy code

```c
char word1[16];
scanf("%s", word1);
```

### Expected diagnosis

The conversion has no width limit, so input longer than 15 characters overflows the array.

### Corrected code

```c
char word1[16];
scanf("%15s", word1);
```

### Regression tests

```c
// A 100-character token must not overwrite memory.
```

## C-H-089: strncpy non-termination

- Difficulty: Hard
- Language/platform: C
- Perspective: API contract
- Concept: strncpy non-termination
- Symptom: The result is not a valid string for exact-length input.
- Diagnostic goal: Terminate explicitly after bounded copying.

### Buggy code

```c
strncpy(dst1, src1, sizeof dst1);
printf("%s", dst1);
```

### Expected diagnosis

strncpy does not append a terminator when the source fills the limit.

### Corrected code

```c
strncpy(dst1, src1, sizeof dst1 - 1);
dst1[sizeof dst1 - 1] = '\0';
```

### Regression tests

```c
// Exact-capacity source remains safely printable.
```

## C-H-090: early return leak

- Difficulty: Hard
- Language/platform: C
- Perspective: Cleanup
- Concept: early return leak
- Symptom: An error path leaks an allocation.
- Diagnostic goal: Centralize cleanup for all exits.

### Buggy code

```c
char *buffer = malloc(1024);
if (!buffer) return 0;
if (!read_data(buffer)) return -1;
free(buffer);
return 0;
```

### Expected diagnosis

The failed read returns before freeing buffer.

### Corrected code

```c
char *buffer = malloc(1024);
if (!buffer) return 0;
int result = read_data(buffer) ? 0 : -1;
free(buffer);
return result;
```

### Regression tests

```c
// Both read success and failure leave no allocation outstanding.
```

## C-H-091: off-by-one allocation

- Difficulty: Hard
- Language/platform: C
- Perspective: Memory safety
- Concept: off-by-one allocation
- Symptom: The last byte is overwritten.
- Diagnostic goal: Match allocation size to the largest valid index.

### Buggy code

```c
char *copy1(const char *s) {
    size_t n = strlen(s);
    char *out = malloc(n);
    memcpy(out, s, n + 1);
    return out;
}
```

### Expected diagnosis

The terminator requires n + 1 bytes; copying n + 1 bytes into n bytes is a heap overflow.

### Corrected code

```c
char *copy1(const char *s) {
    size_t n = strlen(s);
    char *out = malloc(n + 1);
    if (!out) return NULL;
    memcpy(out, s, n + 1);
    return out;
}
```

### Regression tests

```c
// Assert copy1("abc") is "abc" and allocation failure is handled.
```

## C-H-092: returning address of local

- Difficulty: Hard
- Language/platform: C
- Perspective: Pointer lifetime
- Concept: returning address of local
- Symptom: The caller reads garbage.
- Diagnostic goal: Ensure returned storage outlives the function.

### Buggy code

```c
int *value1(void) { int result = 7; return &result; }
```

### Expected diagnosis

A pointer to an automatic local object becomes invalid when the function returns.

### Corrected code

```c
int value1(void) { return 7; }
```

### Regression tests

```c
assert(value1() == 7);
```

## C-H-093: missing terminator

- Difficulty: Hard
- Language/platform: C
- Perspective: String API
- Concept: missing terminator
- Symptom: Printing reads beyond the buffer.
- Diagnostic goal: Reserve and write the C string terminator.

### Buggy code

```c
char name1[4];
memcpy(name1, "Ada", 3);
printf("%s", name1);
```

### Expected diagnosis

memcpy copies bytes only and does not append a terminator.

### Corrected code

```c
char name1[4];
memcpy(name1, "Ada", 3);
name1[3] = '\0';
```

### Regression tests

```c
assert(strcmp(name1, "Ada") == 0);
```

## C-H-094: signed overflow

- Difficulty: Hard
- Language/platform: C
- Perspective: Integer reasoning
- Concept: signed overflow
- Symptom: A boundary calculation produces undefined behavior.
- Diagnostic goal: Check before arithmetic or use an unsigned/wider representation.

### Buggy code

```c
int total1(int count, int size) { return count * size; }
```

### Expected diagnosis

Signed overflow is undefined in C; validating after the multiplication is too late.

### Corrected code

```c
bool total1(int count, int size, int *out) {
    if (count < 0 || size < 0 || count > INT_MAX / size) return false;
    *out = count * size;
    return true;
}
```

### Regression tests

```c
// Assert overflow returns false and a safe product returns true.
```

## C-H-095: double free

- Difficulty: Hard
- Language/platform: C
- Perspective: Ownership
- Concept: double free
- Symptom: The allocator reports corruption.
- Diagnostic goal: Assign ownership once and clear moved-from pointers.

### Buggy code

```c
void release1(char **p) { free(*p); free(*p); }
```

### Expected diagnosis

Freeing the same allocation twice is undefined behavior.

### Corrected code

```c
void release1(char **p) {
    if (p && *p) { free(*p); *p = NULL; }
}
```

### Regression tests

```c
// Call release1 twice; the second call is harmless.
```

## C-H-096: unchecked fopen

- Difficulty: Hard
- Language/platform: C
- Perspective: I/O contract
- Concept: unchecked fopen
- Symptom: A null FILE pointer is dereferenced.
- Diagnostic goal: Check resource acquisition before use.

### Buggy code

```c
FILE *f = fopen(path, "r");
char line[64];
fgets(line, sizeof line, f);
```

### Expected diagnosis

fopen returns NULL on failure; passing it to fgets is undefined behavior.

### Corrected code

```c
FILE *f = fopen(path, "r");
if (!f) return ERROR_OPEN;
char line[64];
if (!fgets(line, sizeof line, f)) { fclose(f); return ERROR_READ; }
fclose(f);
```

### Regression tests

```c
// Missing paths return an error without dereferencing NULL.
```

## C-H-097: data race

- Difficulty: Hard
- Language/platform: C
- Perspective: Concurrency
- Concept: data race
- Symptom: A counter loses increments under threads.
- Diagnostic goal: Synchronize shared mutable state.

### Buggy code

```c
shared_count1++;
```

### Expected diagnosis

Concurrent unsynchronized read-modify-write accesses form a data race and have undefined behavior.

### Corrected code

```c
pthread_mutex_lock(&count_mutex);
shared_count1++;
pthread_mutex_unlock(&count_mutex);
```

### Regression tests

```c
// Run two workers and assert the final count equals both contributions.
```

## C-H-098: scanf width omission

- Difficulty: Hard
- Language/platform: C
- Perspective: Parsing
- Concept: scanf width omission
- Symptom: Long input corrupts adjacent memory.
- Diagnostic goal: Bound formatted input by the destination capacity.

### Buggy code

```c
char word1[16];
scanf("%s", word1);
```

### Expected diagnosis

The conversion has no width limit, so input longer than 15 characters overflows the array.

### Corrected code

```c
char word1[16];
scanf("%15s", word1);
```

### Regression tests

```c
// A 100-character token must not overwrite memory.
```

## C-H-099: strncpy non-termination

- Difficulty: Hard
- Language/platform: C
- Perspective: API contract
- Concept: strncpy non-termination
- Symptom: The result is not a valid string for exact-length input.
- Diagnostic goal: Terminate explicitly after bounded copying.

### Buggy code

```c
strncpy(dst1, src1, sizeof dst1);
printf("%s", dst1);
```

### Expected diagnosis

strncpy does not append a terminator when the source fills the limit.

### Corrected code

```c
strncpy(dst1, src1, sizeof dst1 - 1);
dst1[sizeof dst1 - 1] = '\0';
```

### Regression tests

```c
// Exact-capacity source remains safely printable.
```

## C-H-100: early return leak

- Difficulty: Hard
- Language/platform: C
- Perspective: Cleanup
- Concept: early return leak
- Symptom: An error path leaks an allocation.
- Diagnostic goal: Centralize cleanup for all exits.

### Buggy code

```c
char *buffer = malloc(1024);
if (!buffer) return 0;
if (!read_data(buffer)) return -1;
free(buffer);
return 0;
```

### Expected diagnosis

The failed read returns before freeing buffer.

### Corrected code

```c
char *buffer = malloc(1024);
if (!buffer) return 0;
int result = read_data(buffer) ? 0 : -1;
free(buffer);
return result;
```

### Regression tests

```c
// Both read success and failure leave no allocation outstanding.
```
