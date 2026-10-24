# Spring Data & Repositories Debug Exercises

A RAG-training corpus of 300 debugging exercises for Spring Data & Repositories. Each record contains framework-specific metadata, a failure example, an editorial diagnosis, corrected Java/Spring code, and regression guidance. Corrected code is training material and must be stripped from learner-facing challenge responses.

## Coverage

- Easy: 100 exercises
- Medium: 100 exercises
- Hard: 100 exercises
- Perspectives: configuration, lifecycle, proxies, persistence, HTTP contracts, security, testing, transactions, observability, and deployment

## DATA-E-001: read-modify-write race

- Difficulty: Easy
- Framework: Spring Data & Repositories
- Language: Java
- Perspective: Transactions
- Concept: read-modify-write race
- Symptom: Concurrent updates lose changes.
- Diagnostic goal: Use a transaction and a locking or atomic update strategy.

### Buggy code

```java
entity.setCount(entity.getCount() + 1); repository.save(entity);
```

### Expected diagnosis

Separate requests can read the same old count and overwrite one another.

### Corrected code

```java
@Transactional
@Modifying
@Query("update Item i set i.count = i.count + 1 where i.id = :id")
void increment(long id);
```

### Regression tests

```java
// Concurrent increments equal the number of successful calls.
```

## DATA-E-002: lazy relation in loop

- Difficulty: Easy
- Framework: Spring Data & Repositories
- Language: Java
- Perspective: N+1 queries
- Concept: lazy relation in loop
- Symptom: A page triggers one query per row.
- Diagnostic goal: Fetch the relation with an explicit query plan.

### Buggy code

```java
orders.findAll().forEach(o -> o.getCustomer().getName());
```

### Expected diagnosis

Lazy access in a loop produces N additional selects.

### Corrected code

```java
@EntityGraph(attributePaths = "customer")
List<Order> findAll();
```

### Regression tests

```java
// SQL logging shows one query for the page and relation.
```

## DATA-E-003: session closed before serialization

- Difficulty: Easy
- Framework: Spring Data & Repositories
- Language: Java
- Perspective: Lazy loading
- Concept: session closed before serialization
- Symptom: JSON serialization throws LazyInitializationException.
- Diagnostic goal: Map entities to DTOs inside the transaction.

### Buggy code

```java
return repository.findById(id).orElseThrow();
```

### Expected diagnosis

The web serializer touches a lazy association after the persistence context is closed.

### Corrected code

```java
@Transactional
public OrderDto get(long id) { Order o = repository.findById(id).orElseThrow(); return OrderDto.from(o); }
```

### Regression tests

```java
// DTO serialization never triggers lazy loading.
```

## DATA-E-004: derived name means wrong predicate

- Difficulty: Easy
- Framework: Spring Data & Repositories
- Language: Java
- Perspective: Query methods
- Concept: derived name means wrong predicate
- Symptom: The repository returns unexpected rows.
- Diagnostic goal: Read the derived query name as a precise predicate.

### Buggy code

```java
List<User> findByNameOrEmailAndActive(String name, String email, boolean active);
```

### Expected diagnosis

Operator precedence may be parsed as name OR (email AND active), not (name OR email) AND active.

### Corrected code

```java
@Query("select u from User u where (u.name = :name or u.email = :email) and u.active = :active")
List<User> findActive(...);
```

### Regression tests

```java
// Inactive matches are never returned through either field.
```

## DATA-E-005: unbounded findAll

- Difficulty: Easy
- Framework: Spring Data & Repositories
- Language: Java
- Perspective: Pagination
- Concept: unbounded findAll
- Symptom: Memory and response time grow with table size.
- Diagnostic goal: Expose bounded page or slice queries.

### Buggy code

```java
List<Order> findByStatus(Status status);
```

### Expected diagnosis

Returning every matching entity has no upper bound.

### Corrected code

```java
Page<Order> findByStatus(Status status, Pageable pageable);
```

### Regression tests

```java
// A request with page size 50 never loads more than one page.
```

## DATA-E-006: stale persistence context

- Difficulty: Easy
- Framework: Spring Data & Repositories
- Language: Java
- Perspective: Bulk updates
- Concept: stale persistence context
- Symptom: A later read returns pre-update values.
- Diagnostic goal: Clear or refresh the persistence context after bulk DML.

### Buggy code

```java
@Modifying
@Query("update User u set u.active=false")
void deactivateAll();
```

### Expected diagnosis

Bulk JPQL bypasses managed entity state already held in the context.

### Corrected code

```java
@Modifying(clearAutomatically = true, flushAutomatically = true)
@Query("update User u set u.active=false")
void deactivateAll();
```

### Regression tests

```java
// The next repository read reflects the bulk update.
```

## DATA-E-007: equals null in JPQL

- Difficulty: Easy
- Framework: Spring Data & Repositories
- Language: Java
- Perspective: Null semantics
- Concept: equals null in JPQL
- Symptom: Rows with null values are not found.
- Diagnostic goal: Use IS NULL semantics or derived methods.

### Buggy code

```java
@Query("select x from Item x where x.note = null")
List<Item> missingNote();
```

### Expected diagnosis

SQL null is not equal to null; the predicate is never true.

### Corrected code

```java
@Query("select x from Item x where x.note is null")
List<Item> missingNote();
```

### Regression tests

```java
// Rows with a null note are returned.
```

## DATA-E-008: auditor not populated

- Difficulty: Easy
- Framework: Spring Data & Repositories
- Language: Java
- Perspective: Auditing
- Concept: auditor not populated
- Symptom: CreatedBy fields remain null.
- Diagnostic goal: Enable auditing and provide an authenticated auditor supplier.

### Buggy code

```java
class AuditConfig {}
```

### Expected diagnosis

The entity annotations alone do not activate Spring Data auditing.

### Corrected code

```java
@EnableJpaAuditing
@Configuration
class AuditConfig { @Bean AuditorAware<String> auditor() { return () -> Optional.of("system"); } }
```

### Regression tests

```java
// Save asserts createdBy is populated.
```

## DATA-E-009: lost update not detected

- Difficulty: Easy
- Framework: Spring Data & Repositories
- Language: Java
- Perspective: Optimistic locking
- Concept: lost update not detected
- Symptom: Last writer silently wins.
- Diagnostic goal: Add a version column and handle optimistic lock failures.

### Buggy code

```java
@Entity class Inventory { Long id; int quantity; }
```

### Expected diagnosis

Without @Version, stale writes are accepted.

### Corrected code

```java
@Version
private long version;
```

### Regression tests

```java
// Two updates from the same version cause one OptimisticLockException.
```

## DATA-E-010: repository test uses production schema

- Difficulty: Easy
- Framework: Spring Data & Repositories
- Language: Java
- Perspective: Test data
- Concept: repository test uses production schema
- Symptom: Tests are slow or modify shared data.
- Diagnostic goal: Use an isolated test database and rollback policy.

### Buggy code

```java
@SpringBootTest
class ItemRepositoryTest {}
```

### Expected diagnosis

A full context may load production datasource settings.

### Corrected code

```java
@DataJpaTest
@ActiveProfiles("test")
class ItemRepositoryTest {}
```

### Regression tests

```java
// The test uses an isolated database and rolls back each test.
```

## DATA-E-011: read-modify-write race

- Difficulty: Easy
- Framework: Spring Data & Repositories
- Language: Java
- Perspective: Transactions
- Concept: read-modify-write race
- Symptom: Concurrent updates lose changes.
- Diagnostic goal: Use a transaction and a locking or atomic update strategy.

### Buggy code

```java
entity.setCount(entity.getCount() + 1); repository.save(entity);
```

### Expected diagnosis

Separate requests can read the same old count and overwrite one another.

### Corrected code

```java
@Transactional
@Modifying
@Query("update Item i set i.count = i.count + 1 where i.id = :id")
void increment(long id);
```

### Regression tests

```java
// Concurrent increments equal the number of successful calls.
```

## DATA-E-012: lazy relation in loop

- Difficulty: Easy
- Framework: Spring Data & Repositories
- Language: Java
- Perspective: N+1 queries
- Concept: lazy relation in loop
- Symptom: A page triggers one query per row.
- Diagnostic goal: Fetch the relation with an explicit query plan.

### Buggy code

```java
orders.findAll().forEach(o -> o.getCustomer().getName());
```

### Expected diagnosis

Lazy access in a loop produces N additional selects.

### Corrected code

```java
@EntityGraph(attributePaths = "customer")
List<Order> findAll();
```

### Regression tests

```java
// SQL logging shows one query for the page and relation.
```

## DATA-E-013: session closed before serialization

- Difficulty: Easy
- Framework: Spring Data & Repositories
- Language: Java
- Perspective: Lazy loading
- Concept: session closed before serialization
- Symptom: JSON serialization throws LazyInitializationException.
- Diagnostic goal: Map entities to DTOs inside the transaction.

### Buggy code

```java
return repository.findById(id).orElseThrow();
```

### Expected diagnosis

The web serializer touches a lazy association after the persistence context is closed.

### Corrected code

```java
@Transactional
public OrderDto get(long id) { Order o = repository.findById(id).orElseThrow(); return OrderDto.from(o); }
```

### Regression tests

```java
// DTO serialization never triggers lazy loading.
```

## DATA-E-014: derived name means wrong predicate

- Difficulty: Easy
- Framework: Spring Data & Repositories
- Language: Java
- Perspective: Query methods
- Concept: derived name means wrong predicate
- Symptom: The repository returns unexpected rows.
- Diagnostic goal: Read the derived query name as a precise predicate.

### Buggy code

```java
List<User> findByNameOrEmailAndActive(String name, String email, boolean active);
```

### Expected diagnosis

Operator precedence may be parsed as name OR (email AND active), not (name OR email) AND active.

### Corrected code

```java
@Query("select u from User u where (u.name = :name or u.email = :email) and u.active = :active")
List<User> findActive(...);
```

### Regression tests

```java
// Inactive matches are never returned through either field.
```

## DATA-E-015: unbounded findAll

- Difficulty: Easy
- Framework: Spring Data & Repositories
- Language: Java
- Perspective: Pagination
- Concept: unbounded findAll
- Symptom: Memory and response time grow with table size.
- Diagnostic goal: Expose bounded page or slice queries.

### Buggy code

```java
List<Order> findByStatus(Status status);
```

### Expected diagnosis

Returning every matching entity has no upper bound.

### Corrected code

```java
Page<Order> findByStatus(Status status, Pageable pageable);
```

### Regression tests

```java
// A request with page size 50 never loads more than one page.
```

## DATA-E-016: stale persistence context

- Difficulty: Easy
- Framework: Spring Data & Repositories
- Language: Java
- Perspective: Bulk updates
- Concept: stale persistence context
- Symptom: A later read returns pre-update values.
- Diagnostic goal: Clear or refresh the persistence context after bulk DML.

### Buggy code

```java
@Modifying
@Query("update User u set u.active=false")
void deactivateAll();
```

### Expected diagnosis

Bulk JPQL bypasses managed entity state already held in the context.

### Corrected code

```java
@Modifying(clearAutomatically = true, flushAutomatically = true)
@Query("update User u set u.active=false")
void deactivateAll();
```

### Regression tests

```java
// The next repository read reflects the bulk update.
```

## DATA-E-017: equals null in JPQL

- Difficulty: Easy
- Framework: Spring Data & Repositories
- Language: Java
- Perspective: Null semantics
- Concept: equals null in JPQL
- Symptom: Rows with null values are not found.
- Diagnostic goal: Use IS NULL semantics or derived methods.

### Buggy code

```java
@Query("select x from Item x where x.note = null")
List<Item> missingNote();
```

### Expected diagnosis

SQL null is not equal to null; the predicate is never true.

### Corrected code

```java
@Query("select x from Item x where x.note is null")
List<Item> missingNote();
```

### Regression tests

```java
// Rows with a null note are returned.
```

## DATA-E-018: auditor not populated

- Difficulty: Easy
- Framework: Spring Data & Repositories
- Language: Java
- Perspective: Auditing
- Concept: auditor not populated
- Symptom: CreatedBy fields remain null.
- Diagnostic goal: Enable auditing and provide an authenticated auditor supplier.

### Buggy code

```java
class AuditConfig {}
```

### Expected diagnosis

The entity annotations alone do not activate Spring Data auditing.

### Corrected code

```java
@EnableJpaAuditing
@Configuration
class AuditConfig { @Bean AuditorAware<String> auditor() { return () -> Optional.of("system"); } }
```

### Regression tests

```java
// Save asserts createdBy is populated.
```

## DATA-E-019: lost update not detected

- Difficulty: Easy
- Framework: Spring Data & Repositories
- Language: Java
- Perspective: Optimistic locking
- Concept: lost update not detected
- Symptom: Last writer silently wins.
- Diagnostic goal: Add a version column and handle optimistic lock failures.

### Buggy code

```java
@Entity class Inventory { Long id; int quantity; }
```

### Expected diagnosis

Without @Version, stale writes are accepted.

### Corrected code

```java
@Version
private long version;
```

### Regression tests

```java
// Two updates from the same version cause one OptimisticLockException.
```

## DATA-E-020: repository test uses production schema

- Difficulty: Easy
- Framework: Spring Data & Repositories
- Language: Java
- Perspective: Test data
- Concept: repository test uses production schema
- Symptom: Tests are slow or modify shared data.
- Diagnostic goal: Use an isolated test database and rollback policy.

### Buggy code

```java
@SpringBootTest
class ItemRepositoryTest {}
```

### Expected diagnosis

A full context may load production datasource settings.

### Corrected code

```java
@DataJpaTest
@ActiveProfiles("test")
class ItemRepositoryTest {}
```

### Regression tests

```java
// The test uses an isolated database and rolls back each test.
```

## DATA-E-021: read-modify-write race

- Difficulty: Easy
- Framework: Spring Data & Repositories
- Language: Java
- Perspective: Transactions
- Concept: read-modify-write race
- Symptom: Concurrent updates lose changes.
- Diagnostic goal: Use a transaction and a locking or atomic update strategy.

### Buggy code

```java
entity.setCount(entity.getCount() + 1); repository.save(entity);
```

### Expected diagnosis

Separate requests can read the same old count and overwrite one another.

### Corrected code

```java
@Transactional
@Modifying
@Query("update Item i set i.count = i.count + 1 where i.id = :id")
void increment(long id);
```

### Regression tests

```java
// Concurrent increments equal the number of successful calls.
```

## DATA-E-022: lazy relation in loop

- Difficulty: Easy
- Framework: Spring Data & Repositories
- Language: Java
- Perspective: N+1 queries
- Concept: lazy relation in loop
- Symptom: A page triggers one query per row.
- Diagnostic goal: Fetch the relation with an explicit query plan.

### Buggy code

```java
orders.findAll().forEach(o -> o.getCustomer().getName());
```

### Expected diagnosis

Lazy access in a loop produces N additional selects.

### Corrected code

```java
@EntityGraph(attributePaths = "customer")
List<Order> findAll();
```

### Regression tests

```java
// SQL logging shows one query for the page and relation.
```

## DATA-E-023: session closed before serialization

- Difficulty: Easy
- Framework: Spring Data & Repositories
- Language: Java
- Perspective: Lazy loading
- Concept: session closed before serialization
- Symptom: JSON serialization throws LazyInitializationException.
- Diagnostic goal: Map entities to DTOs inside the transaction.

### Buggy code

```java
return repository.findById(id).orElseThrow();
```

### Expected diagnosis

The web serializer touches a lazy association after the persistence context is closed.

### Corrected code

```java
@Transactional
public OrderDto get(long id) { Order o = repository.findById(id).orElseThrow(); return OrderDto.from(o); }
```

### Regression tests

```java
// DTO serialization never triggers lazy loading.
```

## DATA-E-024: derived name means wrong predicate

- Difficulty: Easy
- Framework: Spring Data & Repositories
- Language: Java
- Perspective: Query methods
- Concept: derived name means wrong predicate
- Symptom: The repository returns unexpected rows.
- Diagnostic goal: Read the derived query name as a precise predicate.

### Buggy code

```java
List<User> findByNameOrEmailAndActive(String name, String email, boolean active);
```

### Expected diagnosis

Operator precedence may be parsed as name OR (email AND active), not (name OR email) AND active.

### Corrected code

```java
@Query("select u from User u where (u.name = :name or u.email = :email) and u.active = :active")
List<User> findActive(...);
```

### Regression tests

```java
// Inactive matches are never returned through either field.
```

## DATA-E-025: unbounded findAll

- Difficulty: Easy
- Framework: Spring Data & Repositories
- Language: Java
- Perspective: Pagination
- Concept: unbounded findAll
- Symptom: Memory and response time grow with table size.
- Diagnostic goal: Expose bounded page or slice queries.

### Buggy code

```java
List<Order> findByStatus(Status status);
```

### Expected diagnosis

Returning every matching entity has no upper bound.

### Corrected code

```java
Page<Order> findByStatus(Status status, Pageable pageable);
```

### Regression tests

```java
// A request with page size 50 never loads more than one page.
```

## DATA-E-026: stale persistence context

- Difficulty: Easy
- Framework: Spring Data & Repositories
- Language: Java
- Perspective: Bulk updates
- Concept: stale persistence context
- Symptom: A later read returns pre-update values.
- Diagnostic goal: Clear or refresh the persistence context after bulk DML.

### Buggy code

```java
@Modifying
@Query("update User u set u.active=false")
void deactivateAll();
```

### Expected diagnosis

Bulk JPQL bypasses managed entity state already held in the context.

### Corrected code

```java
@Modifying(clearAutomatically = true, flushAutomatically = true)
@Query("update User u set u.active=false")
void deactivateAll();
```

### Regression tests

```java
// The next repository read reflects the bulk update.
```

## DATA-E-027: equals null in JPQL

- Difficulty: Easy
- Framework: Spring Data & Repositories
- Language: Java
- Perspective: Null semantics
- Concept: equals null in JPQL
- Symptom: Rows with null values are not found.
- Diagnostic goal: Use IS NULL semantics or derived methods.

### Buggy code

```java
@Query("select x from Item x where x.note = null")
List<Item> missingNote();
```

### Expected diagnosis

SQL null is not equal to null; the predicate is never true.

### Corrected code

```java
@Query("select x from Item x where x.note is null")
List<Item> missingNote();
```

### Regression tests

```java
// Rows with a null note are returned.
```

## DATA-E-028: auditor not populated

- Difficulty: Easy
- Framework: Spring Data & Repositories
- Language: Java
- Perspective: Auditing
- Concept: auditor not populated
- Symptom: CreatedBy fields remain null.
- Diagnostic goal: Enable auditing and provide an authenticated auditor supplier.

### Buggy code

```java
class AuditConfig {}
```

### Expected diagnosis

The entity annotations alone do not activate Spring Data auditing.

### Corrected code

```java
@EnableJpaAuditing
@Configuration
class AuditConfig { @Bean AuditorAware<String> auditor() { return () -> Optional.of("system"); } }
```

### Regression tests

```java
// Save asserts createdBy is populated.
```

## DATA-E-029: lost update not detected

- Difficulty: Easy
- Framework: Spring Data & Repositories
- Language: Java
- Perspective: Optimistic locking
- Concept: lost update not detected
- Symptom: Last writer silently wins.
- Diagnostic goal: Add a version column and handle optimistic lock failures.

### Buggy code

```java
@Entity class Inventory { Long id; int quantity; }
```

### Expected diagnosis

Without @Version, stale writes are accepted.

### Corrected code

```java
@Version
private long version;
```

### Regression tests

```java
// Two updates from the same version cause one OptimisticLockException.
```

## DATA-E-030: repository test uses production schema

- Difficulty: Easy
- Framework: Spring Data & Repositories
- Language: Java
- Perspective: Test data
- Concept: repository test uses production schema
- Symptom: Tests are slow or modify shared data.
- Diagnostic goal: Use an isolated test database and rollback policy.

### Buggy code

```java
@SpringBootTest
class ItemRepositoryTest {}
```

### Expected diagnosis

A full context may load production datasource settings.

### Corrected code

```java
@DataJpaTest
@ActiveProfiles("test")
class ItemRepositoryTest {}
```

### Regression tests

```java
// The test uses an isolated database and rolls back each test.
```

## DATA-E-031: read-modify-write race

- Difficulty: Easy
- Framework: Spring Data & Repositories
- Language: Java
- Perspective: Transactions
- Concept: read-modify-write race
- Symptom: Concurrent updates lose changes.
- Diagnostic goal: Use a transaction and a locking or atomic update strategy.

### Buggy code

```java
entity.setCount(entity.getCount() + 1); repository.save(entity);
```

### Expected diagnosis

Separate requests can read the same old count and overwrite one another.

### Corrected code

```java
@Transactional
@Modifying
@Query("update Item i set i.count = i.count + 1 where i.id = :id")
void increment(long id);
```

### Regression tests

```java
// Concurrent increments equal the number of successful calls.
```

## DATA-E-032: lazy relation in loop

- Difficulty: Easy
- Framework: Spring Data & Repositories
- Language: Java
- Perspective: N+1 queries
- Concept: lazy relation in loop
- Symptom: A page triggers one query per row.
- Diagnostic goal: Fetch the relation with an explicit query plan.

### Buggy code

```java
orders.findAll().forEach(o -> o.getCustomer().getName());
```

### Expected diagnosis

Lazy access in a loop produces N additional selects.

### Corrected code

```java
@EntityGraph(attributePaths = "customer")
List<Order> findAll();
```

### Regression tests

```java
// SQL logging shows one query for the page and relation.
```

## DATA-E-033: session closed before serialization

- Difficulty: Easy
- Framework: Spring Data & Repositories
- Language: Java
- Perspective: Lazy loading
- Concept: session closed before serialization
- Symptom: JSON serialization throws LazyInitializationException.
- Diagnostic goal: Map entities to DTOs inside the transaction.

### Buggy code

```java
return repository.findById(id).orElseThrow();
```

### Expected diagnosis

The web serializer touches a lazy association after the persistence context is closed.

### Corrected code

```java
@Transactional
public OrderDto get(long id) { Order o = repository.findById(id).orElseThrow(); return OrderDto.from(o); }
```

### Regression tests

```java
// DTO serialization never triggers lazy loading.
```

## DATA-E-034: derived name means wrong predicate

- Difficulty: Easy
- Framework: Spring Data & Repositories
- Language: Java
- Perspective: Query methods
- Concept: derived name means wrong predicate
- Symptom: The repository returns unexpected rows.
- Diagnostic goal: Read the derived query name as a precise predicate.

### Buggy code

```java
List<User> findByNameOrEmailAndActive(String name, String email, boolean active);
```

### Expected diagnosis

Operator precedence may be parsed as name OR (email AND active), not (name OR email) AND active.

### Corrected code

```java
@Query("select u from User u where (u.name = :name or u.email = :email) and u.active = :active")
List<User> findActive(...);
```

### Regression tests

```java
// Inactive matches are never returned through either field.
```

## DATA-E-035: unbounded findAll

- Difficulty: Easy
- Framework: Spring Data & Repositories
- Language: Java
- Perspective: Pagination
- Concept: unbounded findAll
- Symptom: Memory and response time grow with table size.
- Diagnostic goal: Expose bounded page or slice queries.

### Buggy code

```java
List<Order> findByStatus(Status status);
```

### Expected diagnosis

Returning every matching entity has no upper bound.

### Corrected code

```java
Page<Order> findByStatus(Status status, Pageable pageable);
```

### Regression tests

```java
// A request with page size 50 never loads more than one page.
```

## DATA-E-036: stale persistence context

- Difficulty: Easy
- Framework: Spring Data & Repositories
- Language: Java
- Perspective: Bulk updates
- Concept: stale persistence context
- Symptom: A later read returns pre-update values.
- Diagnostic goal: Clear or refresh the persistence context after bulk DML.

### Buggy code

```java
@Modifying
@Query("update User u set u.active=false")
void deactivateAll();
```

### Expected diagnosis

Bulk JPQL bypasses managed entity state already held in the context.

### Corrected code

```java
@Modifying(clearAutomatically = true, flushAutomatically = true)
@Query("update User u set u.active=false")
void deactivateAll();
```

### Regression tests

```java
// The next repository read reflects the bulk update.
```

## DATA-E-037: equals null in JPQL

- Difficulty: Easy
- Framework: Spring Data & Repositories
- Language: Java
- Perspective: Null semantics
- Concept: equals null in JPQL
- Symptom: Rows with null values are not found.
- Diagnostic goal: Use IS NULL semantics or derived methods.

### Buggy code

```java
@Query("select x from Item x where x.note = null")
List<Item> missingNote();
```

### Expected diagnosis

SQL null is not equal to null; the predicate is never true.

### Corrected code

```java
@Query("select x from Item x where x.note is null")
List<Item> missingNote();
```

### Regression tests

```java
// Rows with a null note are returned.
```

## DATA-E-038: auditor not populated

- Difficulty: Easy
- Framework: Spring Data & Repositories
- Language: Java
- Perspective: Auditing
- Concept: auditor not populated
- Symptom: CreatedBy fields remain null.
- Diagnostic goal: Enable auditing and provide an authenticated auditor supplier.

### Buggy code

```java
class AuditConfig {}
```

### Expected diagnosis

The entity annotations alone do not activate Spring Data auditing.

### Corrected code

```java
@EnableJpaAuditing
@Configuration
class AuditConfig { @Bean AuditorAware<String> auditor() { return () -> Optional.of("system"); } }
```

### Regression tests

```java
// Save asserts createdBy is populated.
```

## DATA-E-039: lost update not detected

- Difficulty: Easy
- Framework: Spring Data & Repositories
- Language: Java
- Perspective: Optimistic locking
- Concept: lost update not detected
- Symptom: Last writer silently wins.
- Diagnostic goal: Add a version column and handle optimistic lock failures.

### Buggy code

```java
@Entity class Inventory { Long id; int quantity; }
```

### Expected diagnosis

Without @Version, stale writes are accepted.

### Corrected code

```java
@Version
private long version;
```

### Regression tests

```java
// Two updates from the same version cause one OptimisticLockException.
```

## DATA-E-040: repository test uses production schema

- Difficulty: Easy
- Framework: Spring Data & Repositories
- Language: Java
- Perspective: Test data
- Concept: repository test uses production schema
- Symptom: Tests are slow or modify shared data.
- Diagnostic goal: Use an isolated test database and rollback policy.

### Buggy code

```java
@SpringBootTest
class ItemRepositoryTest {}
```

### Expected diagnosis

A full context may load production datasource settings.

### Corrected code

```java
@DataJpaTest
@ActiveProfiles("test")
class ItemRepositoryTest {}
```

### Regression tests

```java
// The test uses an isolated database and rolls back each test.
```

## DATA-E-041: read-modify-write race

- Difficulty: Easy
- Framework: Spring Data & Repositories
- Language: Java
- Perspective: Transactions
- Concept: read-modify-write race
- Symptom: Concurrent updates lose changes.
- Diagnostic goal: Use a transaction and a locking or atomic update strategy.

### Buggy code

```java
entity.setCount(entity.getCount() + 1); repository.save(entity);
```

### Expected diagnosis

Separate requests can read the same old count and overwrite one another.

### Corrected code

```java
@Transactional
@Modifying
@Query("update Item i set i.count = i.count + 1 where i.id = :id")
void increment(long id);
```

### Regression tests

```java
// Concurrent increments equal the number of successful calls.
```

## DATA-E-042: lazy relation in loop

- Difficulty: Easy
- Framework: Spring Data & Repositories
- Language: Java
- Perspective: N+1 queries
- Concept: lazy relation in loop
- Symptom: A page triggers one query per row.
- Diagnostic goal: Fetch the relation with an explicit query plan.

### Buggy code

```java
orders.findAll().forEach(o -> o.getCustomer().getName());
```

### Expected diagnosis

Lazy access in a loop produces N additional selects.

### Corrected code

```java
@EntityGraph(attributePaths = "customer")
List<Order> findAll();
```

### Regression tests

```java
// SQL logging shows one query for the page and relation.
```

## DATA-E-043: session closed before serialization

- Difficulty: Easy
- Framework: Spring Data & Repositories
- Language: Java
- Perspective: Lazy loading
- Concept: session closed before serialization
- Symptom: JSON serialization throws LazyInitializationException.
- Diagnostic goal: Map entities to DTOs inside the transaction.

### Buggy code

```java
return repository.findById(id).orElseThrow();
```

### Expected diagnosis

The web serializer touches a lazy association after the persistence context is closed.

### Corrected code

```java
@Transactional
public OrderDto get(long id) { Order o = repository.findById(id).orElseThrow(); return OrderDto.from(o); }
```

### Regression tests

```java
// DTO serialization never triggers lazy loading.
```

## DATA-E-044: derived name means wrong predicate

- Difficulty: Easy
- Framework: Spring Data & Repositories
- Language: Java
- Perspective: Query methods
- Concept: derived name means wrong predicate
- Symptom: The repository returns unexpected rows.
- Diagnostic goal: Read the derived query name as a precise predicate.

### Buggy code

```java
List<User> findByNameOrEmailAndActive(String name, String email, boolean active);
```

### Expected diagnosis

Operator precedence may be parsed as name OR (email AND active), not (name OR email) AND active.

### Corrected code

```java
@Query("select u from User u where (u.name = :name or u.email = :email) and u.active = :active")
List<User> findActive(...);
```

### Regression tests

```java
// Inactive matches are never returned through either field.
```

## DATA-E-045: unbounded findAll

- Difficulty: Easy
- Framework: Spring Data & Repositories
- Language: Java
- Perspective: Pagination
- Concept: unbounded findAll
- Symptom: Memory and response time grow with table size.
- Diagnostic goal: Expose bounded page or slice queries.

### Buggy code

```java
List<Order> findByStatus(Status status);
```

### Expected diagnosis

Returning every matching entity has no upper bound.

### Corrected code

```java
Page<Order> findByStatus(Status status, Pageable pageable);
```

### Regression tests

```java
// A request with page size 50 never loads more than one page.
```

## DATA-E-046: stale persistence context

- Difficulty: Easy
- Framework: Spring Data & Repositories
- Language: Java
- Perspective: Bulk updates
- Concept: stale persistence context
- Symptom: A later read returns pre-update values.
- Diagnostic goal: Clear or refresh the persistence context after bulk DML.

### Buggy code

```java
@Modifying
@Query("update User u set u.active=false")
void deactivateAll();
```

### Expected diagnosis

Bulk JPQL bypasses managed entity state already held in the context.

### Corrected code

```java
@Modifying(clearAutomatically = true, flushAutomatically = true)
@Query("update User u set u.active=false")
void deactivateAll();
```

### Regression tests

```java
// The next repository read reflects the bulk update.
```

## DATA-E-047: equals null in JPQL

- Difficulty: Easy
- Framework: Spring Data & Repositories
- Language: Java
- Perspective: Null semantics
- Concept: equals null in JPQL
- Symptom: Rows with null values are not found.
- Diagnostic goal: Use IS NULL semantics or derived methods.

### Buggy code

```java
@Query("select x from Item x where x.note = null")
List<Item> missingNote();
```

### Expected diagnosis

SQL null is not equal to null; the predicate is never true.

### Corrected code

```java
@Query("select x from Item x where x.note is null")
List<Item> missingNote();
```

### Regression tests

```java
// Rows with a null note are returned.
```

## DATA-E-048: auditor not populated

- Difficulty: Easy
- Framework: Spring Data & Repositories
- Language: Java
- Perspective: Auditing
- Concept: auditor not populated
- Symptom: CreatedBy fields remain null.
- Diagnostic goal: Enable auditing and provide an authenticated auditor supplier.

### Buggy code

```java
class AuditConfig {}
```

### Expected diagnosis

The entity annotations alone do not activate Spring Data auditing.

### Corrected code

```java
@EnableJpaAuditing
@Configuration
class AuditConfig { @Bean AuditorAware<String> auditor() { return () -> Optional.of("system"); } }
```

### Regression tests

```java
// Save asserts createdBy is populated.
```

## DATA-E-049: lost update not detected

- Difficulty: Easy
- Framework: Spring Data & Repositories
- Language: Java
- Perspective: Optimistic locking
- Concept: lost update not detected
- Symptom: Last writer silently wins.
- Diagnostic goal: Add a version column and handle optimistic lock failures.

### Buggy code

```java
@Entity class Inventory { Long id; int quantity; }
```

### Expected diagnosis

Without @Version, stale writes are accepted.

### Corrected code

```java
@Version
private long version;
```

### Regression tests

```java
// Two updates from the same version cause one OptimisticLockException.
```

## DATA-E-050: repository test uses production schema

- Difficulty: Easy
- Framework: Spring Data & Repositories
- Language: Java
- Perspective: Test data
- Concept: repository test uses production schema
- Symptom: Tests are slow or modify shared data.
- Diagnostic goal: Use an isolated test database and rollback policy.

### Buggy code

```java
@SpringBootTest
class ItemRepositoryTest {}
```

### Expected diagnosis

A full context may load production datasource settings.

### Corrected code

```java
@DataJpaTest
@ActiveProfiles("test")
class ItemRepositoryTest {}
```

### Regression tests

```java
// The test uses an isolated database and rolls back each test.
```

## DATA-E-051: read-modify-write race

- Difficulty: Easy
- Framework: Spring Data & Repositories
- Language: Java
- Perspective: Transactions
- Concept: read-modify-write race
- Symptom: Concurrent updates lose changes.
- Diagnostic goal: Use a transaction and a locking or atomic update strategy.

### Buggy code

```java
entity.setCount(entity.getCount() + 1); repository.save(entity);
```

### Expected diagnosis

Separate requests can read the same old count and overwrite one another.

### Corrected code

```java
@Transactional
@Modifying
@Query("update Item i set i.count = i.count + 1 where i.id = :id")
void increment(long id);
```

### Regression tests

```java
// Concurrent increments equal the number of successful calls.
```

## DATA-E-052: lazy relation in loop

- Difficulty: Easy
- Framework: Spring Data & Repositories
- Language: Java
- Perspective: N+1 queries
- Concept: lazy relation in loop
- Symptom: A page triggers one query per row.
- Diagnostic goal: Fetch the relation with an explicit query plan.

### Buggy code

```java
orders.findAll().forEach(o -> o.getCustomer().getName());
```

### Expected diagnosis

Lazy access in a loop produces N additional selects.

### Corrected code

```java
@EntityGraph(attributePaths = "customer")
List<Order> findAll();
```

### Regression tests

```java
// SQL logging shows one query for the page and relation.
```

## DATA-E-053: session closed before serialization

- Difficulty: Easy
- Framework: Spring Data & Repositories
- Language: Java
- Perspective: Lazy loading
- Concept: session closed before serialization
- Symptom: JSON serialization throws LazyInitializationException.
- Diagnostic goal: Map entities to DTOs inside the transaction.

### Buggy code

```java
return repository.findById(id).orElseThrow();
```

### Expected diagnosis

The web serializer touches a lazy association after the persistence context is closed.

### Corrected code

```java
@Transactional
public OrderDto get(long id) { Order o = repository.findById(id).orElseThrow(); return OrderDto.from(o); }
```

### Regression tests

```java
// DTO serialization never triggers lazy loading.
```

## DATA-E-054: derived name means wrong predicate

- Difficulty: Easy
- Framework: Spring Data & Repositories
- Language: Java
- Perspective: Query methods
- Concept: derived name means wrong predicate
- Symptom: The repository returns unexpected rows.
- Diagnostic goal: Read the derived query name as a precise predicate.

### Buggy code

```java
List<User> findByNameOrEmailAndActive(String name, String email, boolean active);
```

### Expected diagnosis

Operator precedence may be parsed as name OR (email AND active), not (name OR email) AND active.

### Corrected code

```java
@Query("select u from User u where (u.name = :name or u.email = :email) and u.active = :active")
List<User> findActive(...);
```

### Regression tests

```java
// Inactive matches are never returned through either field.
```

## DATA-E-055: unbounded findAll

- Difficulty: Easy
- Framework: Spring Data & Repositories
- Language: Java
- Perspective: Pagination
- Concept: unbounded findAll
- Symptom: Memory and response time grow with table size.
- Diagnostic goal: Expose bounded page or slice queries.

### Buggy code

```java
List<Order> findByStatus(Status status);
```

### Expected diagnosis

Returning every matching entity has no upper bound.

### Corrected code

```java
Page<Order> findByStatus(Status status, Pageable pageable);
```

### Regression tests

```java
// A request with page size 50 never loads more than one page.
```

## DATA-E-056: stale persistence context

- Difficulty: Easy
- Framework: Spring Data & Repositories
- Language: Java
- Perspective: Bulk updates
- Concept: stale persistence context
- Symptom: A later read returns pre-update values.
- Diagnostic goal: Clear or refresh the persistence context after bulk DML.

### Buggy code

```java
@Modifying
@Query("update User u set u.active=false")
void deactivateAll();
```

### Expected diagnosis

Bulk JPQL bypasses managed entity state already held in the context.

### Corrected code

```java
@Modifying(clearAutomatically = true, flushAutomatically = true)
@Query("update User u set u.active=false")
void deactivateAll();
```

### Regression tests

```java
// The next repository read reflects the bulk update.
```

## DATA-E-057: equals null in JPQL

- Difficulty: Easy
- Framework: Spring Data & Repositories
- Language: Java
- Perspective: Null semantics
- Concept: equals null in JPQL
- Symptom: Rows with null values are not found.
- Diagnostic goal: Use IS NULL semantics or derived methods.

### Buggy code

```java
@Query("select x from Item x where x.note = null")
List<Item> missingNote();
```

### Expected diagnosis

SQL null is not equal to null; the predicate is never true.

### Corrected code

```java
@Query("select x from Item x where x.note is null")
List<Item> missingNote();
```

### Regression tests

```java
// Rows with a null note are returned.
```

## DATA-E-058: auditor not populated

- Difficulty: Easy
- Framework: Spring Data & Repositories
- Language: Java
- Perspective: Auditing
- Concept: auditor not populated
- Symptom: CreatedBy fields remain null.
- Diagnostic goal: Enable auditing and provide an authenticated auditor supplier.

### Buggy code

```java
class AuditConfig {}
```

### Expected diagnosis

The entity annotations alone do not activate Spring Data auditing.

### Corrected code

```java
@EnableJpaAuditing
@Configuration
class AuditConfig { @Bean AuditorAware<String> auditor() { return () -> Optional.of("system"); } }
```

### Regression tests

```java
// Save asserts createdBy is populated.
```

## DATA-E-059: lost update not detected

- Difficulty: Easy
- Framework: Spring Data & Repositories
- Language: Java
- Perspective: Optimistic locking
- Concept: lost update not detected
- Symptom: Last writer silently wins.
- Diagnostic goal: Add a version column and handle optimistic lock failures.

### Buggy code

```java
@Entity class Inventory { Long id; int quantity; }
```

### Expected diagnosis

Without @Version, stale writes are accepted.

### Corrected code

```java
@Version
private long version;
```

### Regression tests

```java
// Two updates from the same version cause one OptimisticLockException.
```

## DATA-E-060: repository test uses production schema

- Difficulty: Easy
- Framework: Spring Data & Repositories
- Language: Java
- Perspective: Test data
- Concept: repository test uses production schema
- Symptom: Tests are slow or modify shared data.
- Diagnostic goal: Use an isolated test database and rollback policy.

### Buggy code

```java
@SpringBootTest
class ItemRepositoryTest {}
```

### Expected diagnosis

A full context may load production datasource settings.

### Corrected code

```java
@DataJpaTest
@ActiveProfiles("test")
class ItemRepositoryTest {}
```

### Regression tests

```java
// The test uses an isolated database and rolls back each test.
```

## DATA-E-061: read-modify-write race

- Difficulty: Easy
- Framework: Spring Data & Repositories
- Language: Java
- Perspective: Transactions
- Concept: read-modify-write race
- Symptom: Concurrent updates lose changes.
- Diagnostic goal: Use a transaction and a locking or atomic update strategy.

### Buggy code

```java
entity.setCount(entity.getCount() + 1); repository.save(entity);
```

### Expected diagnosis

Separate requests can read the same old count and overwrite one another.

### Corrected code

```java
@Transactional
@Modifying
@Query("update Item i set i.count = i.count + 1 where i.id = :id")
void increment(long id);
```

### Regression tests

```java
// Concurrent increments equal the number of successful calls.
```

## DATA-E-062: lazy relation in loop

- Difficulty: Easy
- Framework: Spring Data & Repositories
- Language: Java
- Perspective: N+1 queries
- Concept: lazy relation in loop
- Symptom: A page triggers one query per row.
- Diagnostic goal: Fetch the relation with an explicit query plan.

### Buggy code

```java
orders.findAll().forEach(o -> o.getCustomer().getName());
```

### Expected diagnosis

Lazy access in a loop produces N additional selects.

### Corrected code

```java
@EntityGraph(attributePaths = "customer")
List<Order> findAll();
```

### Regression tests

```java
// SQL logging shows one query for the page and relation.
```

## DATA-E-063: session closed before serialization

- Difficulty: Easy
- Framework: Spring Data & Repositories
- Language: Java
- Perspective: Lazy loading
- Concept: session closed before serialization
- Symptom: JSON serialization throws LazyInitializationException.
- Diagnostic goal: Map entities to DTOs inside the transaction.

### Buggy code

```java
return repository.findById(id).orElseThrow();
```

### Expected diagnosis

The web serializer touches a lazy association after the persistence context is closed.

### Corrected code

```java
@Transactional
public OrderDto get(long id) { Order o = repository.findById(id).orElseThrow(); return OrderDto.from(o); }
```

### Regression tests

```java
// DTO serialization never triggers lazy loading.
```

## DATA-E-064: derived name means wrong predicate

- Difficulty: Easy
- Framework: Spring Data & Repositories
- Language: Java
- Perspective: Query methods
- Concept: derived name means wrong predicate
- Symptom: The repository returns unexpected rows.
- Diagnostic goal: Read the derived query name as a precise predicate.

### Buggy code

```java
List<User> findByNameOrEmailAndActive(String name, String email, boolean active);
```

### Expected diagnosis

Operator precedence may be parsed as name OR (email AND active), not (name OR email) AND active.

### Corrected code

```java
@Query("select u from User u where (u.name = :name or u.email = :email) and u.active = :active")
List<User> findActive(...);
```

### Regression tests

```java
// Inactive matches are never returned through either field.
```

## DATA-E-065: unbounded findAll

- Difficulty: Easy
- Framework: Spring Data & Repositories
- Language: Java
- Perspective: Pagination
- Concept: unbounded findAll
- Symptom: Memory and response time grow with table size.
- Diagnostic goal: Expose bounded page or slice queries.

### Buggy code

```java
List<Order> findByStatus(Status status);
```

### Expected diagnosis

Returning every matching entity has no upper bound.

### Corrected code

```java
Page<Order> findByStatus(Status status, Pageable pageable);
```

### Regression tests

```java
// A request with page size 50 never loads more than one page.
```

## DATA-E-066: stale persistence context

- Difficulty: Easy
- Framework: Spring Data & Repositories
- Language: Java
- Perspective: Bulk updates
- Concept: stale persistence context
- Symptom: A later read returns pre-update values.
- Diagnostic goal: Clear or refresh the persistence context after bulk DML.

### Buggy code

```java
@Modifying
@Query("update User u set u.active=false")
void deactivateAll();
```

### Expected diagnosis

Bulk JPQL bypasses managed entity state already held in the context.

### Corrected code

```java
@Modifying(clearAutomatically = true, flushAutomatically = true)
@Query("update User u set u.active=false")
void deactivateAll();
```

### Regression tests

```java
// The next repository read reflects the bulk update.
```

## DATA-E-067: equals null in JPQL

- Difficulty: Easy
- Framework: Spring Data & Repositories
- Language: Java
- Perspective: Null semantics
- Concept: equals null in JPQL
- Symptom: Rows with null values are not found.
- Diagnostic goal: Use IS NULL semantics or derived methods.

### Buggy code

```java
@Query("select x from Item x where x.note = null")
List<Item> missingNote();
```

### Expected diagnosis

SQL null is not equal to null; the predicate is never true.

### Corrected code

```java
@Query("select x from Item x where x.note is null")
List<Item> missingNote();
```

### Regression tests

```java
// Rows with a null note are returned.
```

## DATA-E-068: auditor not populated

- Difficulty: Easy
- Framework: Spring Data & Repositories
- Language: Java
- Perspective: Auditing
- Concept: auditor not populated
- Symptom: CreatedBy fields remain null.
- Diagnostic goal: Enable auditing and provide an authenticated auditor supplier.

### Buggy code

```java
class AuditConfig {}
```

### Expected diagnosis

The entity annotations alone do not activate Spring Data auditing.

### Corrected code

```java
@EnableJpaAuditing
@Configuration
class AuditConfig { @Bean AuditorAware<String> auditor() { return () -> Optional.of("system"); } }
```

### Regression tests

```java
// Save asserts createdBy is populated.
```

## DATA-E-069: lost update not detected

- Difficulty: Easy
- Framework: Spring Data & Repositories
- Language: Java
- Perspective: Optimistic locking
- Concept: lost update not detected
- Symptom: Last writer silently wins.
- Diagnostic goal: Add a version column and handle optimistic lock failures.

### Buggy code

```java
@Entity class Inventory { Long id; int quantity; }
```

### Expected diagnosis

Without @Version, stale writes are accepted.

### Corrected code

```java
@Version
private long version;
```

### Regression tests

```java
// Two updates from the same version cause one OptimisticLockException.
```

## DATA-E-070: repository test uses production schema

- Difficulty: Easy
- Framework: Spring Data & Repositories
- Language: Java
- Perspective: Test data
- Concept: repository test uses production schema
- Symptom: Tests are slow or modify shared data.
- Diagnostic goal: Use an isolated test database and rollback policy.

### Buggy code

```java
@SpringBootTest
class ItemRepositoryTest {}
```

### Expected diagnosis

A full context may load production datasource settings.

### Corrected code

```java
@DataJpaTest
@ActiveProfiles("test")
class ItemRepositoryTest {}
```

### Regression tests

```java
// The test uses an isolated database and rolls back each test.
```

## DATA-E-071: read-modify-write race

- Difficulty: Easy
- Framework: Spring Data & Repositories
- Language: Java
- Perspective: Transactions
- Concept: read-modify-write race
- Symptom: Concurrent updates lose changes.
- Diagnostic goal: Use a transaction and a locking or atomic update strategy.

### Buggy code

```java
entity.setCount(entity.getCount() + 1); repository.save(entity);
```

### Expected diagnosis

Separate requests can read the same old count and overwrite one another.

### Corrected code

```java
@Transactional
@Modifying
@Query("update Item i set i.count = i.count + 1 where i.id = :id")
void increment(long id);
```

### Regression tests

```java
// Concurrent increments equal the number of successful calls.
```

## DATA-E-072: lazy relation in loop

- Difficulty: Easy
- Framework: Spring Data & Repositories
- Language: Java
- Perspective: N+1 queries
- Concept: lazy relation in loop
- Symptom: A page triggers one query per row.
- Diagnostic goal: Fetch the relation with an explicit query plan.

### Buggy code

```java
orders.findAll().forEach(o -> o.getCustomer().getName());
```

### Expected diagnosis

Lazy access in a loop produces N additional selects.

### Corrected code

```java
@EntityGraph(attributePaths = "customer")
List<Order> findAll();
```

### Regression tests

```java
// SQL logging shows one query for the page and relation.
```

## DATA-E-073: session closed before serialization

- Difficulty: Easy
- Framework: Spring Data & Repositories
- Language: Java
- Perspective: Lazy loading
- Concept: session closed before serialization
- Symptom: JSON serialization throws LazyInitializationException.
- Diagnostic goal: Map entities to DTOs inside the transaction.

### Buggy code

```java
return repository.findById(id).orElseThrow();
```

### Expected diagnosis

The web serializer touches a lazy association after the persistence context is closed.

### Corrected code

```java
@Transactional
public OrderDto get(long id) { Order o = repository.findById(id).orElseThrow(); return OrderDto.from(o); }
```

### Regression tests

```java
// DTO serialization never triggers lazy loading.
```

## DATA-E-074: derived name means wrong predicate

- Difficulty: Easy
- Framework: Spring Data & Repositories
- Language: Java
- Perspective: Query methods
- Concept: derived name means wrong predicate
- Symptom: The repository returns unexpected rows.
- Diagnostic goal: Read the derived query name as a precise predicate.

### Buggy code

```java
List<User> findByNameOrEmailAndActive(String name, String email, boolean active);
```

### Expected diagnosis

Operator precedence may be parsed as name OR (email AND active), not (name OR email) AND active.

### Corrected code

```java
@Query("select u from User u where (u.name = :name or u.email = :email) and u.active = :active")
List<User> findActive(...);
```

### Regression tests

```java
// Inactive matches are never returned through either field.
```

## DATA-E-075: unbounded findAll

- Difficulty: Easy
- Framework: Spring Data & Repositories
- Language: Java
- Perspective: Pagination
- Concept: unbounded findAll
- Symptom: Memory and response time grow with table size.
- Diagnostic goal: Expose bounded page or slice queries.

### Buggy code

```java
List<Order> findByStatus(Status status);
```

### Expected diagnosis

Returning every matching entity has no upper bound.

### Corrected code

```java
Page<Order> findByStatus(Status status, Pageable pageable);
```

### Regression tests

```java
// A request with page size 50 never loads more than one page.
```

## DATA-E-076: stale persistence context

- Difficulty: Easy
- Framework: Spring Data & Repositories
- Language: Java
- Perspective: Bulk updates
- Concept: stale persistence context
- Symptom: A later read returns pre-update values.
- Diagnostic goal: Clear or refresh the persistence context after bulk DML.

### Buggy code

```java
@Modifying
@Query("update User u set u.active=false")
void deactivateAll();
```

### Expected diagnosis

Bulk JPQL bypasses managed entity state already held in the context.

### Corrected code

```java
@Modifying(clearAutomatically = true, flushAutomatically = true)
@Query("update User u set u.active=false")
void deactivateAll();
```

### Regression tests

```java
// The next repository read reflects the bulk update.
```

## DATA-E-077: equals null in JPQL

- Difficulty: Easy
- Framework: Spring Data & Repositories
- Language: Java
- Perspective: Null semantics
- Concept: equals null in JPQL
- Symptom: Rows with null values are not found.
- Diagnostic goal: Use IS NULL semantics or derived methods.

### Buggy code

```java
@Query("select x from Item x where x.note = null")
List<Item> missingNote();
```

### Expected diagnosis

SQL null is not equal to null; the predicate is never true.

### Corrected code

```java
@Query("select x from Item x where x.note is null")
List<Item> missingNote();
```

### Regression tests

```java
// Rows with a null note are returned.
```

## DATA-E-078: auditor not populated

- Difficulty: Easy
- Framework: Spring Data & Repositories
- Language: Java
- Perspective: Auditing
- Concept: auditor not populated
- Symptom: CreatedBy fields remain null.
- Diagnostic goal: Enable auditing and provide an authenticated auditor supplier.

### Buggy code

```java
class AuditConfig {}
```

### Expected diagnosis

The entity annotations alone do not activate Spring Data auditing.

### Corrected code

```java
@EnableJpaAuditing
@Configuration
class AuditConfig { @Bean AuditorAware<String> auditor() { return () -> Optional.of("system"); } }
```

### Regression tests

```java
// Save asserts createdBy is populated.
```

## DATA-E-079: lost update not detected

- Difficulty: Easy
- Framework: Spring Data & Repositories
- Language: Java
- Perspective: Optimistic locking
- Concept: lost update not detected
- Symptom: Last writer silently wins.
- Diagnostic goal: Add a version column and handle optimistic lock failures.

### Buggy code

```java
@Entity class Inventory { Long id; int quantity; }
```

### Expected diagnosis

Without @Version, stale writes are accepted.

### Corrected code

```java
@Version
private long version;
```

### Regression tests

```java
// Two updates from the same version cause one OptimisticLockException.
```

## DATA-E-080: repository test uses production schema

- Difficulty: Easy
- Framework: Spring Data & Repositories
- Language: Java
- Perspective: Test data
- Concept: repository test uses production schema
- Symptom: Tests are slow or modify shared data.
- Diagnostic goal: Use an isolated test database and rollback policy.

### Buggy code

```java
@SpringBootTest
class ItemRepositoryTest {}
```

### Expected diagnosis

A full context may load production datasource settings.

### Corrected code

```java
@DataJpaTest
@ActiveProfiles("test")
class ItemRepositoryTest {}
```

### Regression tests

```java
// The test uses an isolated database and rolls back each test.
```

## DATA-E-081: read-modify-write race

- Difficulty: Easy
- Framework: Spring Data & Repositories
- Language: Java
- Perspective: Transactions
- Concept: read-modify-write race
- Symptom: Concurrent updates lose changes.
- Diagnostic goal: Use a transaction and a locking or atomic update strategy.

### Buggy code

```java
entity.setCount(entity.getCount() + 1); repository.save(entity);
```

### Expected diagnosis

Separate requests can read the same old count and overwrite one another.

### Corrected code

```java
@Transactional
@Modifying
@Query("update Item i set i.count = i.count + 1 where i.id = :id")
void increment(long id);
```

### Regression tests

```java
// Concurrent increments equal the number of successful calls.
```

## DATA-E-082: lazy relation in loop

- Difficulty: Easy
- Framework: Spring Data & Repositories
- Language: Java
- Perspective: N+1 queries
- Concept: lazy relation in loop
- Symptom: A page triggers one query per row.
- Diagnostic goal: Fetch the relation with an explicit query plan.

### Buggy code

```java
orders.findAll().forEach(o -> o.getCustomer().getName());
```

### Expected diagnosis

Lazy access in a loop produces N additional selects.

### Corrected code

```java
@EntityGraph(attributePaths = "customer")
List<Order> findAll();
```

### Regression tests

```java
// SQL logging shows one query for the page and relation.
```

## DATA-E-083: session closed before serialization

- Difficulty: Easy
- Framework: Spring Data & Repositories
- Language: Java
- Perspective: Lazy loading
- Concept: session closed before serialization
- Symptom: JSON serialization throws LazyInitializationException.
- Diagnostic goal: Map entities to DTOs inside the transaction.

### Buggy code

```java
return repository.findById(id).orElseThrow();
```

### Expected diagnosis

The web serializer touches a lazy association after the persistence context is closed.

### Corrected code

```java
@Transactional
public OrderDto get(long id) { Order o = repository.findById(id).orElseThrow(); return OrderDto.from(o); }
```

### Regression tests

```java
// DTO serialization never triggers lazy loading.
```

## DATA-E-084: derived name means wrong predicate

- Difficulty: Easy
- Framework: Spring Data & Repositories
- Language: Java
- Perspective: Query methods
- Concept: derived name means wrong predicate
- Symptom: The repository returns unexpected rows.
- Diagnostic goal: Read the derived query name as a precise predicate.

### Buggy code

```java
List<User> findByNameOrEmailAndActive(String name, String email, boolean active);
```

### Expected diagnosis

Operator precedence may be parsed as name OR (email AND active), not (name OR email) AND active.

### Corrected code

```java
@Query("select u from User u where (u.name = :name or u.email = :email) and u.active = :active")
List<User> findActive(...);
```

### Regression tests

```java
// Inactive matches are never returned through either field.
```

## DATA-E-085: unbounded findAll

- Difficulty: Easy
- Framework: Spring Data & Repositories
- Language: Java
- Perspective: Pagination
- Concept: unbounded findAll
- Symptom: Memory and response time grow with table size.
- Diagnostic goal: Expose bounded page or slice queries.

### Buggy code

```java
List<Order> findByStatus(Status status);
```

### Expected diagnosis

Returning every matching entity has no upper bound.

### Corrected code

```java
Page<Order> findByStatus(Status status, Pageable pageable);
```

### Regression tests

```java
// A request with page size 50 never loads more than one page.
```

## DATA-E-086: stale persistence context

- Difficulty: Easy
- Framework: Spring Data & Repositories
- Language: Java
- Perspective: Bulk updates
- Concept: stale persistence context
- Symptom: A later read returns pre-update values.
- Diagnostic goal: Clear or refresh the persistence context after bulk DML.

### Buggy code

```java
@Modifying
@Query("update User u set u.active=false")
void deactivateAll();
```

### Expected diagnosis

Bulk JPQL bypasses managed entity state already held in the context.

### Corrected code

```java
@Modifying(clearAutomatically = true, flushAutomatically = true)
@Query("update User u set u.active=false")
void deactivateAll();
```

### Regression tests

```java
// The next repository read reflects the bulk update.
```

## DATA-E-087: equals null in JPQL

- Difficulty: Easy
- Framework: Spring Data & Repositories
- Language: Java
- Perspective: Null semantics
- Concept: equals null in JPQL
- Symptom: Rows with null values are not found.
- Diagnostic goal: Use IS NULL semantics or derived methods.

### Buggy code

```java
@Query("select x from Item x where x.note = null")
List<Item> missingNote();
```

### Expected diagnosis

SQL null is not equal to null; the predicate is never true.

### Corrected code

```java
@Query("select x from Item x where x.note is null")
List<Item> missingNote();
```

### Regression tests

```java
// Rows with a null note are returned.
```

## DATA-E-088: auditor not populated

- Difficulty: Easy
- Framework: Spring Data & Repositories
- Language: Java
- Perspective: Auditing
- Concept: auditor not populated
- Symptom: CreatedBy fields remain null.
- Diagnostic goal: Enable auditing and provide an authenticated auditor supplier.

### Buggy code

```java
class AuditConfig {}
```

### Expected diagnosis

The entity annotations alone do not activate Spring Data auditing.

### Corrected code

```java
@EnableJpaAuditing
@Configuration
class AuditConfig { @Bean AuditorAware<String> auditor() { return () -> Optional.of("system"); } }
```

### Regression tests

```java
// Save asserts createdBy is populated.
```

## DATA-E-089: lost update not detected

- Difficulty: Easy
- Framework: Spring Data & Repositories
- Language: Java
- Perspective: Optimistic locking
- Concept: lost update not detected
- Symptom: Last writer silently wins.
- Diagnostic goal: Add a version column and handle optimistic lock failures.

### Buggy code

```java
@Entity class Inventory { Long id; int quantity; }
```

### Expected diagnosis

Without @Version, stale writes are accepted.

### Corrected code

```java
@Version
private long version;
```

### Regression tests

```java
// Two updates from the same version cause one OptimisticLockException.
```

## DATA-E-090: repository test uses production schema

- Difficulty: Easy
- Framework: Spring Data & Repositories
- Language: Java
- Perspective: Test data
- Concept: repository test uses production schema
- Symptom: Tests are slow or modify shared data.
- Diagnostic goal: Use an isolated test database and rollback policy.

### Buggy code

```java
@SpringBootTest
class ItemRepositoryTest {}
```

### Expected diagnosis

A full context may load production datasource settings.

### Corrected code

```java
@DataJpaTest
@ActiveProfiles("test")
class ItemRepositoryTest {}
```

### Regression tests

```java
// The test uses an isolated database and rolls back each test.
```

## DATA-E-091: read-modify-write race

- Difficulty: Easy
- Framework: Spring Data & Repositories
- Language: Java
- Perspective: Transactions
- Concept: read-modify-write race
- Symptom: Concurrent updates lose changes.
- Diagnostic goal: Use a transaction and a locking or atomic update strategy.

### Buggy code

```java
entity.setCount(entity.getCount() + 1); repository.save(entity);
```

### Expected diagnosis

Separate requests can read the same old count and overwrite one another.

### Corrected code

```java
@Transactional
@Modifying
@Query("update Item i set i.count = i.count + 1 where i.id = :id")
void increment(long id);
```

### Regression tests

```java
// Concurrent increments equal the number of successful calls.
```

## DATA-E-092: lazy relation in loop

- Difficulty: Easy
- Framework: Spring Data & Repositories
- Language: Java
- Perspective: N+1 queries
- Concept: lazy relation in loop
- Symptom: A page triggers one query per row.
- Diagnostic goal: Fetch the relation with an explicit query plan.

### Buggy code

```java
orders.findAll().forEach(o -> o.getCustomer().getName());
```

### Expected diagnosis

Lazy access in a loop produces N additional selects.

### Corrected code

```java
@EntityGraph(attributePaths = "customer")
List<Order> findAll();
```

### Regression tests

```java
// SQL logging shows one query for the page and relation.
```

## DATA-E-093: session closed before serialization

- Difficulty: Easy
- Framework: Spring Data & Repositories
- Language: Java
- Perspective: Lazy loading
- Concept: session closed before serialization
- Symptom: JSON serialization throws LazyInitializationException.
- Diagnostic goal: Map entities to DTOs inside the transaction.

### Buggy code

```java
return repository.findById(id).orElseThrow();
```

### Expected diagnosis

The web serializer touches a lazy association after the persistence context is closed.

### Corrected code

```java
@Transactional
public OrderDto get(long id) { Order o = repository.findById(id).orElseThrow(); return OrderDto.from(o); }
```

### Regression tests

```java
// DTO serialization never triggers lazy loading.
```

## DATA-E-094: derived name means wrong predicate

- Difficulty: Easy
- Framework: Spring Data & Repositories
- Language: Java
- Perspective: Query methods
- Concept: derived name means wrong predicate
- Symptom: The repository returns unexpected rows.
- Diagnostic goal: Read the derived query name as a precise predicate.

### Buggy code

```java
List<User> findByNameOrEmailAndActive(String name, String email, boolean active);
```

### Expected diagnosis

Operator precedence may be parsed as name OR (email AND active), not (name OR email) AND active.

### Corrected code

```java
@Query("select u from User u where (u.name = :name or u.email = :email) and u.active = :active")
List<User> findActive(...);
```

### Regression tests

```java
// Inactive matches are never returned through either field.
```

## DATA-E-095: unbounded findAll

- Difficulty: Easy
- Framework: Spring Data & Repositories
- Language: Java
- Perspective: Pagination
- Concept: unbounded findAll
- Symptom: Memory and response time grow with table size.
- Diagnostic goal: Expose bounded page or slice queries.

### Buggy code

```java
List<Order> findByStatus(Status status);
```

### Expected diagnosis

Returning every matching entity has no upper bound.

### Corrected code

```java
Page<Order> findByStatus(Status status, Pageable pageable);
```

### Regression tests

```java
// A request with page size 50 never loads more than one page.
```

## DATA-E-096: stale persistence context

- Difficulty: Easy
- Framework: Spring Data & Repositories
- Language: Java
- Perspective: Bulk updates
- Concept: stale persistence context
- Symptom: A later read returns pre-update values.
- Diagnostic goal: Clear or refresh the persistence context after bulk DML.

### Buggy code

```java
@Modifying
@Query("update User u set u.active=false")
void deactivateAll();
```

### Expected diagnosis

Bulk JPQL bypasses managed entity state already held in the context.

### Corrected code

```java
@Modifying(clearAutomatically = true, flushAutomatically = true)
@Query("update User u set u.active=false")
void deactivateAll();
```

### Regression tests

```java
// The next repository read reflects the bulk update.
```

## DATA-E-097: equals null in JPQL

- Difficulty: Easy
- Framework: Spring Data & Repositories
- Language: Java
- Perspective: Null semantics
- Concept: equals null in JPQL
- Symptom: Rows with null values are not found.
- Diagnostic goal: Use IS NULL semantics or derived methods.

### Buggy code

```java
@Query("select x from Item x where x.note = null")
List<Item> missingNote();
```

### Expected diagnosis

SQL null is not equal to null; the predicate is never true.

### Corrected code

```java
@Query("select x from Item x where x.note is null")
List<Item> missingNote();
```

### Regression tests

```java
// Rows with a null note are returned.
```

## DATA-E-098: auditor not populated

- Difficulty: Easy
- Framework: Spring Data & Repositories
- Language: Java
- Perspective: Auditing
- Concept: auditor not populated
- Symptom: CreatedBy fields remain null.
- Diagnostic goal: Enable auditing and provide an authenticated auditor supplier.

### Buggy code

```java
class AuditConfig {}
```

### Expected diagnosis

The entity annotations alone do not activate Spring Data auditing.

### Corrected code

```java
@EnableJpaAuditing
@Configuration
class AuditConfig { @Bean AuditorAware<String> auditor() { return () -> Optional.of("system"); } }
```

### Regression tests

```java
// Save asserts createdBy is populated.
```

## DATA-E-099: lost update not detected

- Difficulty: Easy
- Framework: Spring Data & Repositories
- Language: Java
- Perspective: Optimistic locking
- Concept: lost update not detected
- Symptom: Last writer silently wins.
- Diagnostic goal: Add a version column and handle optimistic lock failures.

### Buggy code

```java
@Entity class Inventory { Long id; int quantity; }
```

### Expected diagnosis

Without @Version, stale writes are accepted.

### Corrected code

```java
@Version
private long version;
```

### Regression tests

```java
// Two updates from the same version cause one OptimisticLockException.
```

## DATA-E-100: repository test uses production schema

- Difficulty: Easy
- Framework: Spring Data & Repositories
- Language: Java
- Perspective: Test data
- Concept: repository test uses production schema
- Symptom: Tests are slow or modify shared data.
- Diagnostic goal: Use an isolated test database and rollback policy.

### Buggy code

```java
@SpringBootTest
class ItemRepositoryTest {}
```

### Expected diagnosis

A full context may load production datasource settings.

### Corrected code

```java
@DataJpaTest
@ActiveProfiles("test")
class ItemRepositoryTest {}
```

### Regression tests

```java
// The test uses an isolated database and rolls back each test.
```

## DATA-M-001: read-modify-write race

- Difficulty: Medium
- Framework: Spring Data & Repositories
- Language: Java
- Perspective: Transactions
- Concept: read-modify-write race
- Symptom: Concurrent updates lose changes.
- Diagnostic goal: Use a transaction and a locking or atomic update strategy.

### Buggy code

```java
entity.setCount(entity.getCount() + 1); repository.save(entity);
```

### Expected diagnosis

Separate requests can read the same old count and overwrite one another.

### Corrected code

```java
@Transactional
@Modifying
@Query("update Item i set i.count = i.count + 1 where i.id = :id")
void increment(long id);
```

### Regression tests

```java
// Concurrent increments equal the number of successful calls.
```

## DATA-M-002: lazy relation in loop

- Difficulty: Medium
- Framework: Spring Data & Repositories
- Language: Java
- Perspective: N+1 queries
- Concept: lazy relation in loop
- Symptom: A page triggers one query per row.
- Diagnostic goal: Fetch the relation with an explicit query plan.

### Buggy code

```java
orders.findAll().forEach(o -> o.getCustomer().getName());
```

### Expected diagnosis

Lazy access in a loop produces N additional selects.

### Corrected code

```java
@EntityGraph(attributePaths = "customer")
List<Order> findAll();
```

### Regression tests

```java
// SQL logging shows one query for the page and relation.
```

## DATA-M-003: session closed before serialization

- Difficulty: Medium
- Framework: Spring Data & Repositories
- Language: Java
- Perspective: Lazy loading
- Concept: session closed before serialization
- Symptom: JSON serialization throws LazyInitializationException.
- Diagnostic goal: Map entities to DTOs inside the transaction.

### Buggy code

```java
return repository.findById(id).orElseThrow();
```

### Expected diagnosis

The web serializer touches a lazy association after the persistence context is closed.

### Corrected code

```java
@Transactional
public OrderDto get(long id) { Order o = repository.findById(id).orElseThrow(); return OrderDto.from(o); }
```

### Regression tests

```java
// DTO serialization never triggers lazy loading.
```

## DATA-M-004: derived name means wrong predicate

- Difficulty: Medium
- Framework: Spring Data & Repositories
- Language: Java
- Perspective: Query methods
- Concept: derived name means wrong predicate
- Symptom: The repository returns unexpected rows.
- Diagnostic goal: Read the derived query name as a precise predicate.

### Buggy code

```java
List<User> findByNameOrEmailAndActive(String name, String email, boolean active);
```

### Expected diagnosis

Operator precedence may be parsed as name OR (email AND active), not (name OR email) AND active.

### Corrected code

```java
@Query("select u from User u where (u.name = :name or u.email = :email) and u.active = :active")
List<User> findActive(...);
```

### Regression tests

```java
// Inactive matches are never returned through either field.
```

## DATA-M-005: unbounded findAll

- Difficulty: Medium
- Framework: Spring Data & Repositories
- Language: Java
- Perspective: Pagination
- Concept: unbounded findAll
- Symptom: Memory and response time grow with table size.
- Diagnostic goal: Expose bounded page or slice queries.

### Buggy code

```java
List<Order> findByStatus(Status status);
```

### Expected diagnosis

Returning every matching entity has no upper bound.

### Corrected code

```java
Page<Order> findByStatus(Status status, Pageable pageable);
```

### Regression tests

```java
// A request with page size 50 never loads more than one page.
```

## DATA-M-006: stale persistence context

- Difficulty: Medium
- Framework: Spring Data & Repositories
- Language: Java
- Perspective: Bulk updates
- Concept: stale persistence context
- Symptom: A later read returns pre-update values.
- Diagnostic goal: Clear or refresh the persistence context after bulk DML.

### Buggy code

```java
@Modifying
@Query("update User u set u.active=false")
void deactivateAll();
```

### Expected diagnosis

Bulk JPQL bypasses managed entity state already held in the context.

### Corrected code

```java
@Modifying(clearAutomatically = true, flushAutomatically = true)
@Query("update User u set u.active=false")
void deactivateAll();
```

### Regression tests

```java
// The next repository read reflects the bulk update.
```

## DATA-M-007: equals null in JPQL

- Difficulty: Medium
- Framework: Spring Data & Repositories
- Language: Java
- Perspective: Null semantics
- Concept: equals null in JPQL
- Symptom: Rows with null values are not found.
- Diagnostic goal: Use IS NULL semantics or derived methods.

### Buggy code

```java
@Query("select x from Item x where x.note = null")
List<Item> missingNote();
```

### Expected diagnosis

SQL null is not equal to null; the predicate is never true.

### Corrected code

```java
@Query("select x from Item x where x.note is null")
List<Item> missingNote();
```

### Regression tests

```java
// Rows with a null note are returned.
```

## DATA-M-008: auditor not populated

- Difficulty: Medium
- Framework: Spring Data & Repositories
- Language: Java
- Perspective: Auditing
- Concept: auditor not populated
- Symptom: CreatedBy fields remain null.
- Diagnostic goal: Enable auditing and provide an authenticated auditor supplier.

### Buggy code

```java
class AuditConfig {}
```

### Expected diagnosis

The entity annotations alone do not activate Spring Data auditing.

### Corrected code

```java
@EnableJpaAuditing
@Configuration
class AuditConfig { @Bean AuditorAware<String> auditor() { return () -> Optional.of("system"); } }
```

### Regression tests

```java
// Save asserts createdBy is populated.
```

## DATA-M-009: lost update not detected

- Difficulty: Medium
- Framework: Spring Data & Repositories
- Language: Java
- Perspective: Optimistic locking
- Concept: lost update not detected
- Symptom: Last writer silently wins.
- Diagnostic goal: Add a version column and handle optimistic lock failures.

### Buggy code

```java
@Entity class Inventory { Long id; int quantity; }
```

### Expected diagnosis

Without @Version, stale writes are accepted.

### Corrected code

```java
@Version
private long version;
```

### Regression tests

```java
// Two updates from the same version cause one OptimisticLockException.
```

## DATA-M-010: repository test uses production schema

- Difficulty: Medium
- Framework: Spring Data & Repositories
- Language: Java
- Perspective: Test data
- Concept: repository test uses production schema
- Symptom: Tests are slow or modify shared data.
- Diagnostic goal: Use an isolated test database and rollback policy.

### Buggy code

```java
@SpringBootTest
class ItemRepositoryTest {}
```

### Expected diagnosis

A full context may load production datasource settings.

### Corrected code

```java
@DataJpaTest
@ActiveProfiles("test")
class ItemRepositoryTest {}
```

### Regression tests

```java
// The test uses an isolated database and rolls back each test.
```

## DATA-M-011: read-modify-write race

- Difficulty: Medium
- Framework: Spring Data & Repositories
- Language: Java
- Perspective: Transactions
- Concept: read-modify-write race
- Symptom: Concurrent updates lose changes.
- Diagnostic goal: Use a transaction and a locking or atomic update strategy.

### Buggy code

```java
entity.setCount(entity.getCount() + 1); repository.save(entity);
```

### Expected diagnosis

Separate requests can read the same old count and overwrite one another.

### Corrected code

```java
@Transactional
@Modifying
@Query("update Item i set i.count = i.count + 1 where i.id = :id")
void increment(long id);
```

### Regression tests

```java
// Concurrent increments equal the number of successful calls.
```

## DATA-M-012: lazy relation in loop

- Difficulty: Medium
- Framework: Spring Data & Repositories
- Language: Java
- Perspective: N+1 queries
- Concept: lazy relation in loop
- Symptom: A page triggers one query per row.
- Diagnostic goal: Fetch the relation with an explicit query plan.

### Buggy code

```java
orders.findAll().forEach(o -> o.getCustomer().getName());
```

### Expected diagnosis

Lazy access in a loop produces N additional selects.

### Corrected code

```java
@EntityGraph(attributePaths = "customer")
List<Order> findAll();
```

### Regression tests

```java
// SQL logging shows one query for the page and relation.
```

## DATA-M-013: session closed before serialization

- Difficulty: Medium
- Framework: Spring Data & Repositories
- Language: Java
- Perspective: Lazy loading
- Concept: session closed before serialization
- Symptom: JSON serialization throws LazyInitializationException.
- Diagnostic goal: Map entities to DTOs inside the transaction.

### Buggy code

```java
return repository.findById(id).orElseThrow();
```

### Expected diagnosis

The web serializer touches a lazy association after the persistence context is closed.

### Corrected code

```java
@Transactional
public OrderDto get(long id) { Order o = repository.findById(id).orElseThrow(); return OrderDto.from(o); }
```

### Regression tests

```java
// DTO serialization never triggers lazy loading.
```

## DATA-M-014: derived name means wrong predicate

- Difficulty: Medium
- Framework: Spring Data & Repositories
- Language: Java
- Perspective: Query methods
- Concept: derived name means wrong predicate
- Symptom: The repository returns unexpected rows.
- Diagnostic goal: Read the derived query name as a precise predicate.

### Buggy code

```java
List<User> findByNameOrEmailAndActive(String name, String email, boolean active);
```

### Expected diagnosis

Operator precedence may be parsed as name OR (email AND active), not (name OR email) AND active.

### Corrected code

```java
@Query("select u from User u where (u.name = :name or u.email = :email) and u.active = :active")
List<User> findActive(...);
```

### Regression tests

```java
// Inactive matches are never returned through either field.
```

## DATA-M-015: unbounded findAll

- Difficulty: Medium
- Framework: Spring Data & Repositories
- Language: Java
- Perspective: Pagination
- Concept: unbounded findAll
- Symptom: Memory and response time grow with table size.
- Diagnostic goal: Expose bounded page or slice queries.

### Buggy code

```java
List<Order> findByStatus(Status status);
```

### Expected diagnosis

Returning every matching entity has no upper bound.

### Corrected code

```java
Page<Order> findByStatus(Status status, Pageable pageable);
```

### Regression tests

```java
// A request with page size 50 never loads more than one page.
```

## DATA-M-016: stale persistence context

- Difficulty: Medium
- Framework: Spring Data & Repositories
- Language: Java
- Perspective: Bulk updates
- Concept: stale persistence context
- Symptom: A later read returns pre-update values.
- Diagnostic goal: Clear or refresh the persistence context after bulk DML.

### Buggy code

```java
@Modifying
@Query("update User u set u.active=false")
void deactivateAll();
```

### Expected diagnosis

Bulk JPQL bypasses managed entity state already held in the context.

### Corrected code

```java
@Modifying(clearAutomatically = true, flushAutomatically = true)
@Query("update User u set u.active=false")
void deactivateAll();
```

### Regression tests

```java
// The next repository read reflects the bulk update.
```

## DATA-M-017: equals null in JPQL

- Difficulty: Medium
- Framework: Spring Data & Repositories
- Language: Java
- Perspective: Null semantics
- Concept: equals null in JPQL
- Symptom: Rows with null values are not found.
- Diagnostic goal: Use IS NULL semantics or derived methods.

### Buggy code

```java
@Query("select x from Item x where x.note = null")
List<Item> missingNote();
```

### Expected diagnosis

SQL null is not equal to null; the predicate is never true.

### Corrected code

```java
@Query("select x from Item x where x.note is null")
List<Item> missingNote();
```

### Regression tests

```java
// Rows with a null note are returned.
```

## DATA-M-018: auditor not populated

- Difficulty: Medium
- Framework: Spring Data & Repositories
- Language: Java
- Perspective: Auditing
- Concept: auditor not populated
- Symptom: CreatedBy fields remain null.
- Diagnostic goal: Enable auditing and provide an authenticated auditor supplier.

### Buggy code

```java
class AuditConfig {}
```

### Expected diagnosis

The entity annotations alone do not activate Spring Data auditing.

### Corrected code

```java
@EnableJpaAuditing
@Configuration
class AuditConfig { @Bean AuditorAware<String> auditor() { return () -> Optional.of("system"); } }
```

### Regression tests

```java
// Save asserts createdBy is populated.
```

## DATA-M-019: lost update not detected

- Difficulty: Medium
- Framework: Spring Data & Repositories
- Language: Java
- Perspective: Optimistic locking
- Concept: lost update not detected
- Symptom: Last writer silently wins.
- Diagnostic goal: Add a version column and handle optimistic lock failures.

### Buggy code

```java
@Entity class Inventory { Long id; int quantity; }
```

### Expected diagnosis

Without @Version, stale writes are accepted.

### Corrected code

```java
@Version
private long version;
```

### Regression tests

```java
// Two updates from the same version cause one OptimisticLockException.
```

## DATA-M-020: repository test uses production schema

- Difficulty: Medium
- Framework: Spring Data & Repositories
- Language: Java
- Perspective: Test data
- Concept: repository test uses production schema
- Symptom: Tests are slow or modify shared data.
- Diagnostic goal: Use an isolated test database and rollback policy.

### Buggy code

```java
@SpringBootTest
class ItemRepositoryTest {}
```

### Expected diagnosis

A full context may load production datasource settings.

### Corrected code

```java
@DataJpaTest
@ActiveProfiles("test")
class ItemRepositoryTest {}
```

### Regression tests

```java
// The test uses an isolated database and rolls back each test.
```

## DATA-M-021: read-modify-write race

- Difficulty: Medium
- Framework: Spring Data & Repositories
- Language: Java
- Perspective: Transactions
- Concept: read-modify-write race
- Symptom: Concurrent updates lose changes.
- Diagnostic goal: Use a transaction and a locking or atomic update strategy.

### Buggy code

```java
entity.setCount(entity.getCount() + 1); repository.save(entity);
```

### Expected diagnosis

Separate requests can read the same old count and overwrite one another.

### Corrected code

```java
@Transactional
@Modifying
@Query("update Item i set i.count = i.count + 1 where i.id = :id")
void increment(long id);
```

### Regression tests

```java
// Concurrent increments equal the number of successful calls.
```

## DATA-M-022: lazy relation in loop

- Difficulty: Medium
- Framework: Spring Data & Repositories
- Language: Java
- Perspective: N+1 queries
- Concept: lazy relation in loop
- Symptom: A page triggers one query per row.
- Diagnostic goal: Fetch the relation with an explicit query plan.

### Buggy code

```java
orders.findAll().forEach(o -> o.getCustomer().getName());
```

### Expected diagnosis

Lazy access in a loop produces N additional selects.

### Corrected code

```java
@EntityGraph(attributePaths = "customer")
List<Order> findAll();
```

### Regression tests

```java
// SQL logging shows one query for the page and relation.
```

## DATA-M-023: session closed before serialization

- Difficulty: Medium
- Framework: Spring Data & Repositories
- Language: Java
- Perspective: Lazy loading
- Concept: session closed before serialization
- Symptom: JSON serialization throws LazyInitializationException.
- Diagnostic goal: Map entities to DTOs inside the transaction.

### Buggy code

```java
return repository.findById(id).orElseThrow();
```

### Expected diagnosis

The web serializer touches a lazy association after the persistence context is closed.

### Corrected code

```java
@Transactional
public OrderDto get(long id) { Order o = repository.findById(id).orElseThrow(); return OrderDto.from(o); }
```

### Regression tests

```java
// DTO serialization never triggers lazy loading.
```

## DATA-M-024: derived name means wrong predicate

- Difficulty: Medium
- Framework: Spring Data & Repositories
- Language: Java
- Perspective: Query methods
- Concept: derived name means wrong predicate
- Symptom: The repository returns unexpected rows.
- Diagnostic goal: Read the derived query name as a precise predicate.

### Buggy code

```java
List<User> findByNameOrEmailAndActive(String name, String email, boolean active);
```

### Expected diagnosis

Operator precedence may be parsed as name OR (email AND active), not (name OR email) AND active.

### Corrected code

```java
@Query("select u from User u where (u.name = :name or u.email = :email) and u.active = :active")
List<User> findActive(...);
```

### Regression tests

```java
// Inactive matches are never returned through either field.
```

## DATA-M-025: unbounded findAll

- Difficulty: Medium
- Framework: Spring Data & Repositories
- Language: Java
- Perspective: Pagination
- Concept: unbounded findAll
- Symptom: Memory and response time grow with table size.
- Diagnostic goal: Expose bounded page or slice queries.

### Buggy code

```java
List<Order> findByStatus(Status status);
```

### Expected diagnosis

Returning every matching entity has no upper bound.

### Corrected code

```java
Page<Order> findByStatus(Status status, Pageable pageable);
```

### Regression tests

```java
// A request with page size 50 never loads more than one page.
```

## DATA-M-026: stale persistence context

- Difficulty: Medium
- Framework: Spring Data & Repositories
- Language: Java
- Perspective: Bulk updates
- Concept: stale persistence context
- Symptom: A later read returns pre-update values.
- Diagnostic goal: Clear or refresh the persistence context after bulk DML.

### Buggy code

```java
@Modifying
@Query("update User u set u.active=false")
void deactivateAll();
```

### Expected diagnosis

Bulk JPQL bypasses managed entity state already held in the context.

### Corrected code

```java
@Modifying(clearAutomatically = true, flushAutomatically = true)
@Query("update User u set u.active=false")
void deactivateAll();
```

### Regression tests

```java
// The next repository read reflects the bulk update.
```

## DATA-M-027: equals null in JPQL

- Difficulty: Medium
- Framework: Spring Data & Repositories
- Language: Java
- Perspective: Null semantics
- Concept: equals null in JPQL
- Symptom: Rows with null values are not found.
- Diagnostic goal: Use IS NULL semantics or derived methods.

### Buggy code

```java
@Query("select x from Item x where x.note = null")
List<Item> missingNote();
```

### Expected diagnosis

SQL null is not equal to null; the predicate is never true.

### Corrected code

```java
@Query("select x from Item x where x.note is null")
List<Item> missingNote();
```

### Regression tests

```java
// Rows with a null note are returned.
```

## DATA-M-028: auditor not populated

- Difficulty: Medium
- Framework: Spring Data & Repositories
- Language: Java
- Perspective: Auditing
- Concept: auditor not populated
- Symptom: CreatedBy fields remain null.
- Diagnostic goal: Enable auditing and provide an authenticated auditor supplier.

### Buggy code

```java
class AuditConfig {}
```

### Expected diagnosis

The entity annotations alone do not activate Spring Data auditing.

### Corrected code

```java
@EnableJpaAuditing
@Configuration
class AuditConfig { @Bean AuditorAware<String> auditor() { return () -> Optional.of("system"); } }
```

### Regression tests

```java
// Save asserts createdBy is populated.
```

## DATA-M-029: lost update not detected

- Difficulty: Medium
- Framework: Spring Data & Repositories
- Language: Java
- Perspective: Optimistic locking
- Concept: lost update not detected
- Symptom: Last writer silently wins.
- Diagnostic goal: Add a version column and handle optimistic lock failures.

### Buggy code

```java
@Entity class Inventory { Long id; int quantity; }
```

### Expected diagnosis

Without @Version, stale writes are accepted.

### Corrected code

```java
@Version
private long version;
```

### Regression tests

```java
// Two updates from the same version cause one OptimisticLockException.
```

## DATA-M-030: repository test uses production schema

- Difficulty: Medium
- Framework: Spring Data & Repositories
- Language: Java
- Perspective: Test data
- Concept: repository test uses production schema
- Symptom: Tests are slow or modify shared data.
- Diagnostic goal: Use an isolated test database and rollback policy.

### Buggy code

```java
@SpringBootTest
class ItemRepositoryTest {}
```

### Expected diagnosis

A full context may load production datasource settings.

### Corrected code

```java
@DataJpaTest
@ActiveProfiles("test")
class ItemRepositoryTest {}
```

### Regression tests

```java
// The test uses an isolated database and rolls back each test.
```

## DATA-M-031: read-modify-write race

- Difficulty: Medium
- Framework: Spring Data & Repositories
- Language: Java
- Perspective: Transactions
- Concept: read-modify-write race
- Symptom: Concurrent updates lose changes.
- Diagnostic goal: Use a transaction and a locking or atomic update strategy.

### Buggy code

```java
entity.setCount(entity.getCount() + 1); repository.save(entity);
```

### Expected diagnosis

Separate requests can read the same old count and overwrite one another.

### Corrected code

```java
@Transactional
@Modifying
@Query("update Item i set i.count = i.count + 1 where i.id = :id")
void increment(long id);
```

### Regression tests

```java
// Concurrent increments equal the number of successful calls.
```

## DATA-M-032: lazy relation in loop

- Difficulty: Medium
- Framework: Spring Data & Repositories
- Language: Java
- Perspective: N+1 queries
- Concept: lazy relation in loop
- Symptom: A page triggers one query per row.
- Diagnostic goal: Fetch the relation with an explicit query plan.

### Buggy code

```java
orders.findAll().forEach(o -> o.getCustomer().getName());
```

### Expected diagnosis

Lazy access in a loop produces N additional selects.

### Corrected code

```java
@EntityGraph(attributePaths = "customer")
List<Order> findAll();
```

### Regression tests

```java
// SQL logging shows one query for the page and relation.
```

## DATA-M-033: session closed before serialization

- Difficulty: Medium
- Framework: Spring Data & Repositories
- Language: Java
- Perspective: Lazy loading
- Concept: session closed before serialization
- Symptom: JSON serialization throws LazyInitializationException.
- Diagnostic goal: Map entities to DTOs inside the transaction.

### Buggy code

```java
return repository.findById(id).orElseThrow();
```

### Expected diagnosis

The web serializer touches a lazy association after the persistence context is closed.

### Corrected code

```java
@Transactional
public OrderDto get(long id) { Order o = repository.findById(id).orElseThrow(); return OrderDto.from(o); }
```

### Regression tests

```java
// DTO serialization never triggers lazy loading.
```

## DATA-M-034: derived name means wrong predicate

- Difficulty: Medium
- Framework: Spring Data & Repositories
- Language: Java
- Perspective: Query methods
- Concept: derived name means wrong predicate
- Symptom: The repository returns unexpected rows.
- Diagnostic goal: Read the derived query name as a precise predicate.

### Buggy code

```java
List<User> findByNameOrEmailAndActive(String name, String email, boolean active);
```

### Expected diagnosis

Operator precedence may be parsed as name OR (email AND active), not (name OR email) AND active.

### Corrected code

```java
@Query("select u from User u where (u.name = :name or u.email = :email) and u.active = :active")
List<User> findActive(...);
```

### Regression tests

```java
// Inactive matches are never returned through either field.
```

## DATA-M-035: unbounded findAll

- Difficulty: Medium
- Framework: Spring Data & Repositories
- Language: Java
- Perspective: Pagination
- Concept: unbounded findAll
- Symptom: Memory and response time grow with table size.
- Diagnostic goal: Expose bounded page or slice queries.

### Buggy code

```java
List<Order> findByStatus(Status status);
```

### Expected diagnosis

Returning every matching entity has no upper bound.

### Corrected code

```java
Page<Order> findByStatus(Status status, Pageable pageable);
```

### Regression tests

```java
// A request with page size 50 never loads more than one page.
```

## DATA-M-036: stale persistence context

- Difficulty: Medium
- Framework: Spring Data & Repositories
- Language: Java
- Perspective: Bulk updates
- Concept: stale persistence context
- Symptom: A later read returns pre-update values.
- Diagnostic goal: Clear or refresh the persistence context after bulk DML.

### Buggy code

```java
@Modifying
@Query("update User u set u.active=false")
void deactivateAll();
```

### Expected diagnosis

Bulk JPQL bypasses managed entity state already held in the context.

### Corrected code

```java
@Modifying(clearAutomatically = true, flushAutomatically = true)
@Query("update User u set u.active=false")
void deactivateAll();
```

### Regression tests

```java
// The next repository read reflects the bulk update.
```

## DATA-M-037: equals null in JPQL

- Difficulty: Medium
- Framework: Spring Data & Repositories
- Language: Java
- Perspective: Null semantics
- Concept: equals null in JPQL
- Symptom: Rows with null values are not found.
- Diagnostic goal: Use IS NULL semantics or derived methods.

### Buggy code

```java
@Query("select x from Item x where x.note = null")
List<Item> missingNote();
```

### Expected diagnosis

SQL null is not equal to null; the predicate is never true.

### Corrected code

```java
@Query("select x from Item x where x.note is null")
List<Item> missingNote();
```

### Regression tests

```java
// Rows with a null note are returned.
```

## DATA-M-038: auditor not populated

- Difficulty: Medium
- Framework: Spring Data & Repositories
- Language: Java
- Perspective: Auditing
- Concept: auditor not populated
- Symptom: CreatedBy fields remain null.
- Diagnostic goal: Enable auditing and provide an authenticated auditor supplier.

### Buggy code

```java
class AuditConfig {}
```

### Expected diagnosis

The entity annotations alone do not activate Spring Data auditing.

### Corrected code

```java
@EnableJpaAuditing
@Configuration
class AuditConfig { @Bean AuditorAware<String> auditor() { return () -> Optional.of("system"); } }
```

### Regression tests

```java
// Save asserts createdBy is populated.
```

## DATA-M-039: lost update not detected

- Difficulty: Medium
- Framework: Spring Data & Repositories
- Language: Java
- Perspective: Optimistic locking
- Concept: lost update not detected
- Symptom: Last writer silently wins.
- Diagnostic goal: Add a version column and handle optimistic lock failures.

### Buggy code

```java
@Entity class Inventory { Long id; int quantity; }
```

### Expected diagnosis

Without @Version, stale writes are accepted.

### Corrected code

```java
@Version
private long version;
```

### Regression tests

```java
// Two updates from the same version cause one OptimisticLockException.
```

## DATA-M-040: repository test uses production schema

- Difficulty: Medium
- Framework: Spring Data & Repositories
- Language: Java
- Perspective: Test data
- Concept: repository test uses production schema
- Symptom: Tests are slow or modify shared data.
- Diagnostic goal: Use an isolated test database and rollback policy.

### Buggy code

```java
@SpringBootTest
class ItemRepositoryTest {}
```

### Expected diagnosis

A full context may load production datasource settings.

### Corrected code

```java
@DataJpaTest
@ActiveProfiles("test")
class ItemRepositoryTest {}
```

### Regression tests

```java
// The test uses an isolated database and rolls back each test.
```

## DATA-M-041: read-modify-write race

- Difficulty: Medium
- Framework: Spring Data & Repositories
- Language: Java
- Perspective: Transactions
- Concept: read-modify-write race
- Symptom: Concurrent updates lose changes.
- Diagnostic goal: Use a transaction and a locking or atomic update strategy.

### Buggy code

```java
entity.setCount(entity.getCount() + 1); repository.save(entity);
```

### Expected diagnosis

Separate requests can read the same old count and overwrite one another.

### Corrected code

```java
@Transactional
@Modifying
@Query("update Item i set i.count = i.count + 1 where i.id = :id")
void increment(long id);
```

### Regression tests

```java
// Concurrent increments equal the number of successful calls.
```

## DATA-M-042: lazy relation in loop

- Difficulty: Medium
- Framework: Spring Data & Repositories
- Language: Java
- Perspective: N+1 queries
- Concept: lazy relation in loop
- Symptom: A page triggers one query per row.
- Diagnostic goal: Fetch the relation with an explicit query plan.

### Buggy code

```java
orders.findAll().forEach(o -> o.getCustomer().getName());
```

### Expected diagnosis

Lazy access in a loop produces N additional selects.

### Corrected code

```java
@EntityGraph(attributePaths = "customer")
List<Order> findAll();
```

### Regression tests

```java
// SQL logging shows one query for the page and relation.
```

## DATA-M-043: session closed before serialization

- Difficulty: Medium
- Framework: Spring Data & Repositories
- Language: Java
- Perspective: Lazy loading
- Concept: session closed before serialization
- Symptom: JSON serialization throws LazyInitializationException.
- Diagnostic goal: Map entities to DTOs inside the transaction.

### Buggy code

```java
return repository.findById(id).orElseThrow();
```

### Expected diagnosis

The web serializer touches a lazy association after the persistence context is closed.

### Corrected code

```java
@Transactional
public OrderDto get(long id) { Order o = repository.findById(id).orElseThrow(); return OrderDto.from(o); }
```

### Regression tests

```java
// DTO serialization never triggers lazy loading.
```

## DATA-M-044: derived name means wrong predicate

- Difficulty: Medium
- Framework: Spring Data & Repositories
- Language: Java
- Perspective: Query methods
- Concept: derived name means wrong predicate
- Symptom: The repository returns unexpected rows.
- Diagnostic goal: Read the derived query name as a precise predicate.

### Buggy code

```java
List<User> findByNameOrEmailAndActive(String name, String email, boolean active);
```

### Expected diagnosis

Operator precedence may be parsed as name OR (email AND active), not (name OR email) AND active.

### Corrected code

```java
@Query("select u from User u where (u.name = :name or u.email = :email) and u.active = :active")
List<User> findActive(...);
```

### Regression tests

```java
// Inactive matches are never returned through either field.
```

## DATA-M-045: unbounded findAll

- Difficulty: Medium
- Framework: Spring Data & Repositories
- Language: Java
- Perspective: Pagination
- Concept: unbounded findAll
- Symptom: Memory and response time grow with table size.
- Diagnostic goal: Expose bounded page or slice queries.

### Buggy code

```java
List<Order> findByStatus(Status status);
```

### Expected diagnosis

Returning every matching entity has no upper bound.

### Corrected code

```java
Page<Order> findByStatus(Status status, Pageable pageable);
```

### Regression tests

```java
// A request with page size 50 never loads more than one page.
```

## DATA-M-046: stale persistence context

- Difficulty: Medium
- Framework: Spring Data & Repositories
- Language: Java
- Perspective: Bulk updates
- Concept: stale persistence context
- Symptom: A later read returns pre-update values.
- Diagnostic goal: Clear or refresh the persistence context after bulk DML.

### Buggy code

```java
@Modifying
@Query("update User u set u.active=false")
void deactivateAll();
```

### Expected diagnosis

Bulk JPQL bypasses managed entity state already held in the context.

### Corrected code

```java
@Modifying(clearAutomatically = true, flushAutomatically = true)
@Query("update User u set u.active=false")
void deactivateAll();
```

### Regression tests

```java
// The next repository read reflects the bulk update.
```

## DATA-M-047: equals null in JPQL

- Difficulty: Medium
- Framework: Spring Data & Repositories
- Language: Java
- Perspective: Null semantics
- Concept: equals null in JPQL
- Symptom: Rows with null values are not found.
- Diagnostic goal: Use IS NULL semantics or derived methods.

### Buggy code

```java
@Query("select x from Item x where x.note = null")
List<Item> missingNote();
```

### Expected diagnosis

SQL null is not equal to null; the predicate is never true.

### Corrected code

```java
@Query("select x from Item x where x.note is null")
List<Item> missingNote();
```

### Regression tests

```java
// Rows with a null note are returned.
```

## DATA-M-048: auditor not populated

- Difficulty: Medium
- Framework: Spring Data & Repositories
- Language: Java
- Perspective: Auditing
- Concept: auditor not populated
- Symptom: CreatedBy fields remain null.
- Diagnostic goal: Enable auditing and provide an authenticated auditor supplier.

### Buggy code

```java
class AuditConfig {}
```

### Expected diagnosis

The entity annotations alone do not activate Spring Data auditing.

### Corrected code

```java
@EnableJpaAuditing
@Configuration
class AuditConfig { @Bean AuditorAware<String> auditor() { return () -> Optional.of("system"); } }
```

### Regression tests

```java
// Save asserts createdBy is populated.
```

## DATA-M-049: lost update not detected

- Difficulty: Medium
- Framework: Spring Data & Repositories
- Language: Java
- Perspective: Optimistic locking
- Concept: lost update not detected
- Symptom: Last writer silently wins.
- Diagnostic goal: Add a version column and handle optimistic lock failures.

### Buggy code

```java
@Entity class Inventory { Long id; int quantity; }
```

### Expected diagnosis

Without @Version, stale writes are accepted.

### Corrected code

```java
@Version
private long version;
```

### Regression tests

```java
// Two updates from the same version cause one OptimisticLockException.
```

## DATA-M-050: repository test uses production schema

- Difficulty: Medium
- Framework: Spring Data & Repositories
- Language: Java
- Perspective: Test data
- Concept: repository test uses production schema
- Symptom: Tests are slow or modify shared data.
- Diagnostic goal: Use an isolated test database and rollback policy.

### Buggy code

```java
@SpringBootTest
class ItemRepositoryTest {}
```

### Expected diagnosis

A full context may load production datasource settings.

### Corrected code

```java
@DataJpaTest
@ActiveProfiles("test")
class ItemRepositoryTest {}
```

### Regression tests

```java
// The test uses an isolated database and rolls back each test.
```

## DATA-M-051: read-modify-write race

- Difficulty: Medium
- Framework: Spring Data & Repositories
- Language: Java
- Perspective: Transactions
- Concept: read-modify-write race
- Symptom: Concurrent updates lose changes.
- Diagnostic goal: Use a transaction and a locking or atomic update strategy.

### Buggy code

```java
entity.setCount(entity.getCount() + 1); repository.save(entity);
```

### Expected diagnosis

Separate requests can read the same old count and overwrite one another.

### Corrected code

```java
@Transactional
@Modifying
@Query("update Item i set i.count = i.count + 1 where i.id = :id")
void increment(long id);
```

### Regression tests

```java
// Concurrent increments equal the number of successful calls.
```

## DATA-M-052: lazy relation in loop

- Difficulty: Medium
- Framework: Spring Data & Repositories
- Language: Java
- Perspective: N+1 queries
- Concept: lazy relation in loop
- Symptom: A page triggers one query per row.
- Diagnostic goal: Fetch the relation with an explicit query plan.

### Buggy code

```java
orders.findAll().forEach(o -> o.getCustomer().getName());
```

### Expected diagnosis

Lazy access in a loop produces N additional selects.

### Corrected code

```java
@EntityGraph(attributePaths = "customer")
List<Order> findAll();
```

### Regression tests

```java
// SQL logging shows one query for the page and relation.
```

## DATA-M-053: session closed before serialization

- Difficulty: Medium
- Framework: Spring Data & Repositories
- Language: Java
- Perspective: Lazy loading
- Concept: session closed before serialization
- Symptom: JSON serialization throws LazyInitializationException.
- Diagnostic goal: Map entities to DTOs inside the transaction.

### Buggy code

```java
return repository.findById(id).orElseThrow();
```

### Expected diagnosis

The web serializer touches a lazy association after the persistence context is closed.

### Corrected code

```java
@Transactional
public OrderDto get(long id) { Order o = repository.findById(id).orElseThrow(); return OrderDto.from(o); }
```

### Regression tests

```java
// DTO serialization never triggers lazy loading.
```

## DATA-M-054: derived name means wrong predicate

- Difficulty: Medium
- Framework: Spring Data & Repositories
- Language: Java
- Perspective: Query methods
- Concept: derived name means wrong predicate
- Symptom: The repository returns unexpected rows.
- Diagnostic goal: Read the derived query name as a precise predicate.

### Buggy code

```java
List<User> findByNameOrEmailAndActive(String name, String email, boolean active);
```

### Expected diagnosis

Operator precedence may be parsed as name OR (email AND active), not (name OR email) AND active.

### Corrected code

```java
@Query("select u from User u where (u.name = :name or u.email = :email) and u.active = :active")
List<User> findActive(...);
```

### Regression tests

```java
// Inactive matches are never returned through either field.
```

## DATA-M-055: unbounded findAll

- Difficulty: Medium
- Framework: Spring Data & Repositories
- Language: Java
- Perspective: Pagination
- Concept: unbounded findAll
- Symptom: Memory and response time grow with table size.
- Diagnostic goal: Expose bounded page or slice queries.

### Buggy code

```java
List<Order> findByStatus(Status status);
```

### Expected diagnosis

Returning every matching entity has no upper bound.

### Corrected code

```java
Page<Order> findByStatus(Status status, Pageable pageable);
```

### Regression tests

```java
// A request with page size 50 never loads more than one page.
```

## DATA-M-056: stale persistence context

- Difficulty: Medium
- Framework: Spring Data & Repositories
- Language: Java
- Perspective: Bulk updates
- Concept: stale persistence context
- Symptom: A later read returns pre-update values.
- Diagnostic goal: Clear or refresh the persistence context after bulk DML.

### Buggy code

```java
@Modifying
@Query("update User u set u.active=false")
void deactivateAll();
```

### Expected diagnosis

Bulk JPQL bypasses managed entity state already held in the context.

### Corrected code

```java
@Modifying(clearAutomatically = true, flushAutomatically = true)
@Query("update User u set u.active=false")
void deactivateAll();
```

### Regression tests

```java
// The next repository read reflects the bulk update.
```

## DATA-M-057: equals null in JPQL

- Difficulty: Medium
- Framework: Spring Data & Repositories
- Language: Java
- Perspective: Null semantics
- Concept: equals null in JPQL
- Symptom: Rows with null values are not found.
- Diagnostic goal: Use IS NULL semantics or derived methods.

### Buggy code

```java
@Query("select x from Item x where x.note = null")
List<Item> missingNote();
```

### Expected diagnosis

SQL null is not equal to null; the predicate is never true.

### Corrected code

```java
@Query("select x from Item x where x.note is null")
List<Item> missingNote();
```

### Regression tests

```java
// Rows with a null note are returned.
```

## DATA-M-058: auditor not populated

- Difficulty: Medium
- Framework: Spring Data & Repositories
- Language: Java
- Perspective: Auditing
- Concept: auditor not populated
- Symptom: CreatedBy fields remain null.
- Diagnostic goal: Enable auditing and provide an authenticated auditor supplier.

### Buggy code

```java
class AuditConfig {}
```

### Expected diagnosis

The entity annotations alone do not activate Spring Data auditing.

### Corrected code

```java
@EnableJpaAuditing
@Configuration
class AuditConfig { @Bean AuditorAware<String> auditor() { return () -> Optional.of("system"); } }
```

### Regression tests

```java
// Save asserts createdBy is populated.
```

## DATA-M-059: lost update not detected

- Difficulty: Medium
- Framework: Spring Data & Repositories
- Language: Java
- Perspective: Optimistic locking
- Concept: lost update not detected
- Symptom: Last writer silently wins.
- Diagnostic goal: Add a version column and handle optimistic lock failures.

### Buggy code

```java
@Entity class Inventory { Long id; int quantity; }
```

### Expected diagnosis

Without @Version, stale writes are accepted.

### Corrected code

```java
@Version
private long version;
```

### Regression tests

```java
// Two updates from the same version cause one OptimisticLockException.
```

## DATA-M-060: repository test uses production schema

- Difficulty: Medium
- Framework: Spring Data & Repositories
- Language: Java
- Perspective: Test data
- Concept: repository test uses production schema
- Symptom: Tests are slow or modify shared data.
- Diagnostic goal: Use an isolated test database and rollback policy.

### Buggy code

```java
@SpringBootTest
class ItemRepositoryTest {}
```

### Expected diagnosis

A full context may load production datasource settings.

### Corrected code

```java
@DataJpaTest
@ActiveProfiles("test")
class ItemRepositoryTest {}
```

### Regression tests

```java
// The test uses an isolated database and rolls back each test.
```

## DATA-M-061: read-modify-write race

- Difficulty: Medium
- Framework: Spring Data & Repositories
- Language: Java
- Perspective: Transactions
- Concept: read-modify-write race
- Symptom: Concurrent updates lose changes.
- Diagnostic goal: Use a transaction and a locking or atomic update strategy.

### Buggy code

```java
entity.setCount(entity.getCount() + 1); repository.save(entity);
```

### Expected diagnosis

Separate requests can read the same old count and overwrite one another.

### Corrected code

```java
@Transactional
@Modifying
@Query("update Item i set i.count = i.count + 1 where i.id = :id")
void increment(long id);
```

### Regression tests

```java
// Concurrent increments equal the number of successful calls.
```

## DATA-M-062: lazy relation in loop

- Difficulty: Medium
- Framework: Spring Data & Repositories
- Language: Java
- Perspective: N+1 queries
- Concept: lazy relation in loop
- Symptom: A page triggers one query per row.
- Diagnostic goal: Fetch the relation with an explicit query plan.

### Buggy code

```java
orders.findAll().forEach(o -> o.getCustomer().getName());
```

### Expected diagnosis

Lazy access in a loop produces N additional selects.

### Corrected code

```java
@EntityGraph(attributePaths = "customer")
List<Order> findAll();
```

### Regression tests

```java
// SQL logging shows one query for the page and relation.
```

## DATA-M-063: session closed before serialization

- Difficulty: Medium
- Framework: Spring Data & Repositories
- Language: Java
- Perspective: Lazy loading
- Concept: session closed before serialization
- Symptom: JSON serialization throws LazyInitializationException.
- Diagnostic goal: Map entities to DTOs inside the transaction.

### Buggy code

```java
return repository.findById(id).orElseThrow();
```

### Expected diagnosis

The web serializer touches a lazy association after the persistence context is closed.

### Corrected code

```java
@Transactional
public OrderDto get(long id) { Order o = repository.findById(id).orElseThrow(); return OrderDto.from(o); }
```

### Regression tests

```java
// DTO serialization never triggers lazy loading.
```

## DATA-M-064: derived name means wrong predicate

- Difficulty: Medium
- Framework: Spring Data & Repositories
- Language: Java
- Perspective: Query methods
- Concept: derived name means wrong predicate
- Symptom: The repository returns unexpected rows.
- Diagnostic goal: Read the derived query name as a precise predicate.

### Buggy code

```java
List<User> findByNameOrEmailAndActive(String name, String email, boolean active);
```

### Expected diagnosis

Operator precedence may be parsed as name OR (email AND active), not (name OR email) AND active.

### Corrected code

```java
@Query("select u from User u where (u.name = :name or u.email = :email) and u.active = :active")
List<User> findActive(...);
```

### Regression tests

```java
// Inactive matches are never returned through either field.
```

## DATA-M-065: unbounded findAll

- Difficulty: Medium
- Framework: Spring Data & Repositories
- Language: Java
- Perspective: Pagination
- Concept: unbounded findAll
- Symptom: Memory and response time grow with table size.
- Diagnostic goal: Expose bounded page or slice queries.

### Buggy code

```java
List<Order> findByStatus(Status status);
```

### Expected diagnosis

Returning every matching entity has no upper bound.

### Corrected code

```java
Page<Order> findByStatus(Status status, Pageable pageable);
```

### Regression tests

```java
// A request with page size 50 never loads more than one page.
```

## DATA-M-066: stale persistence context

- Difficulty: Medium
- Framework: Spring Data & Repositories
- Language: Java
- Perspective: Bulk updates
- Concept: stale persistence context
- Symptom: A later read returns pre-update values.
- Diagnostic goal: Clear or refresh the persistence context after bulk DML.

### Buggy code

```java
@Modifying
@Query("update User u set u.active=false")
void deactivateAll();
```

### Expected diagnosis

Bulk JPQL bypasses managed entity state already held in the context.

### Corrected code

```java
@Modifying(clearAutomatically = true, flushAutomatically = true)
@Query("update User u set u.active=false")
void deactivateAll();
```

### Regression tests

```java
// The next repository read reflects the bulk update.
```

## DATA-M-067: equals null in JPQL

- Difficulty: Medium
- Framework: Spring Data & Repositories
- Language: Java
- Perspective: Null semantics
- Concept: equals null in JPQL
- Symptom: Rows with null values are not found.
- Diagnostic goal: Use IS NULL semantics or derived methods.

### Buggy code

```java
@Query("select x from Item x where x.note = null")
List<Item> missingNote();
```

### Expected diagnosis

SQL null is not equal to null; the predicate is never true.

### Corrected code

```java
@Query("select x from Item x where x.note is null")
List<Item> missingNote();
```

### Regression tests

```java
// Rows with a null note are returned.
```

## DATA-M-068: auditor not populated

- Difficulty: Medium
- Framework: Spring Data & Repositories
- Language: Java
- Perspective: Auditing
- Concept: auditor not populated
- Symptom: CreatedBy fields remain null.
- Diagnostic goal: Enable auditing and provide an authenticated auditor supplier.

### Buggy code

```java
class AuditConfig {}
```

### Expected diagnosis

The entity annotations alone do not activate Spring Data auditing.

### Corrected code

```java
@EnableJpaAuditing
@Configuration
class AuditConfig { @Bean AuditorAware<String> auditor() { return () -> Optional.of("system"); } }
```

### Regression tests

```java
// Save asserts createdBy is populated.
```

## DATA-M-069: lost update not detected

- Difficulty: Medium
- Framework: Spring Data & Repositories
- Language: Java
- Perspective: Optimistic locking
- Concept: lost update not detected
- Symptom: Last writer silently wins.
- Diagnostic goal: Add a version column and handle optimistic lock failures.

### Buggy code

```java
@Entity class Inventory { Long id; int quantity; }
```

### Expected diagnosis

Without @Version, stale writes are accepted.

### Corrected code

```java
@Version
private long version;
```

### Regression tests

```java
// Two updates from the same version cause one OptimisticLockException.
```

## DATA-M-070: repository test uses production schema

- Difficulty: Medium
- Framework: Spring Data & Repositories
- Language: Java
- Perspective: Test data
- Concept: repository test uses production schema
- Symptom: Tests are slow or modify shared data.
- Diagnostic goal: Use an isolated test database and rollback policy.

### Buggy code

```java
@SpringBootTest
class ItemRepositoryTest {}
```

### Expected diagnosis

A full context may load production datasource settings.

### Corrected code

```java
@DataJpaTest
@ActiveProfiles("test")
class ItemRepositoryTest {}
```

### Regression tests

```java
// The test uses an isolated database and rolls back each test.
```

## DATA-M-071: read-modify-write race

- Difficulty: Medium
- Framework: Spring Data & Repositories
- Language: Java
- Perspective: Transactions
- Concept: read-modify-write race
- Symptom: Concurrent updates lose changes.
- Diagnostic goal: Use a transaction and a locking or atomic update strategy.

### Buggy code

```java
entity.setCount(entity.getCount() + 1); repository.save(entity);
```

### Expected diagnosis

Separate requests can read the same old count and overwrite one another.

### Corrected code

```java
@Transactional
@Modifying
@Query("update Item i set i.count = i.count + 1 where i.id = :id")
void increment(long id);
```

### Regression tests

```java
// Concurrent increments equal the number of successful calls.
```

## DATA-M-072: lazy relation in loop

- Difficulty: Medium
- Framework: Spring Data & Repositories
- Language: Java
- Perspective: N+1 queries
- Concept: lazy relation in loop
- Symptom: A page triggers one query per row.
- Diagnostic goal: Fetch the relation with an explicit query plan.

### Buggy code

```java
orders.findAll().forEach(o -> o.getCustomer().getName());
```

### Expected diagnosis

Lazy access in a loop produces N additional selects.

### Corrected code

```java
@EntityGraph(attributePaths = "customer")
List<Order> findAll();
```

### Regression tests

```java
// SQL logging shows one query for the page and relation.
```

## DATA-M-073: session closed before serialization

- Difficulty: Medium
- Framework: Spring Data & Repositories
- Language: Java
- Perspective: Lazy loading
- Concept: session closed before serialization
- Symptom: JSON serialization throws LazyInitializationException.
- Diagnostic goal: Map entities to DTOs inside the transaction.

### Buggy code

```java
return repository.findById(id).orElseThrow();
```

### Expected diagnosis

The web serializer touches a lazy association after the persistence context is closed.

### Corrected code

```java
@Transactional
public OrderDto get(long id) { Order o = repository.findById(id).orElseThrow(); return OrderDto.from(o); }
```

### Regression tests

```java
// DTO serialization never triggers lazy loading.
```

## DATA-M-074: derived name means wrong predicate

- Difficulty: Medium
- Framework: Spring Data & Repositories
- Language: Java
- Perspective: Query methods
- Concept: derived name means wrong predicate
- Symptom: The repository returns unexpected rows.
- Diagnostic goal: Read the derived query name as a precise predicate.

### Buggy code

```java
List<User> findByNameOrEmailAndActive(String name, String email, boolean active);
```

### Expected diagnosis

Operator precedence may be parsed as name OR (email AND active), not (name OR email) AND active.

### Corrected code

```java
@Query("select u from User u where (u.name = :name or u.email = :email) and u.active = :active")
List<User> findActive(...);
```

### Regression tests

```java
// Inactive matches are never returned through either field.
```

## DATA-M-075: unbounded findAll

- Difficulty: Medium
- Framework: Spring Data & Repositories
- Language: Java
- Perspective: Pagination
- Concept: unbounded findAll
- Symptom: Memory and response time grow with table size.
- Diagnostic goal: Expose bounded page or slice queries.

### Buggy code

```java
List<Order> findByStatus(Status status);
```

### Expected diagnosis

Returning every matching entity has no upper bound.

### Corrected code

```java
Page<Order> findByStatus(Status status, Pageable pageable);
```

### Regression tests

```java
// A request with page size 50 never loads more than one page.
```

## DATA-M-076: stale persistence context

- Difficulty: Medium
- Framework: Spring Data & Repositories
- Language: Java
- Perspective: Bulk updates
- Concept: stale persistence context
- Symptom: A later read returns pre-update values.
- Diagnostic goal: Clear or refresh the persistence context after bulk DML.

### Buggy code

```java
@Modifying
@Query("update User u set u.active=false")
void deactivateAll();
```

### Expected diagnosis

Bulk JPQL bypasses managed entity state already held in the context.

### Corrected code

```java
@Modifying(clearAutomatically = true, flushAutomatically = true)
@Query("update User u set u.active=false")
void deactivateAll();
```

### Regression tests

```java
// The next repository read reflects the bulk update.
```

## DATA-M-077: equals null in JPQL

- Difficulty: Medium
- Framework: Spring Data & Repositories
- Language: Java
- Perspective: Null semantics
- Concept: equals null in JPQL
- Symptom: Rows with null values are not found.
- Diagnostic goal: Use IS NULL semantics or derived methods.

### Buggy code

```java
@Query("select x from Item x where x.note = null")
List<Item> missingNote();
```

### Expected diagnosis

SQL null is not equal to null; the predicate is never true.

### Corrected code

```java
@Query("select x from Item x where x.note is null")
List<Item> missingNote();
```

### Regression tests

```java
// Rows with a null note are returned.
```

## DATA-M-078: auditor not populated

- Difficulty: Medium
- Framework: Spring Data & Repositories
- Language: Java
- Perspective: Auditing
- Concept: auditor not populated
- Symptom: CreatedBy fields remain null.
- Diagnostic goal: Enable auditing and provide an authenticated auditor supplier.

### Buggy code

```java
class AuditConfig {}
```

### Expected diagnosis

The entity annotations alone do not activate Spring Data auditing.

### Corrected code

```java
@EnableJpaAuditing
@Configuration
class AuditConfig { @Bean AuditorAware<String> auditor() { return () -> Optional.of("system"); } }
```

### Regression tests

```java
// Save asserts createdBy is populated.
```

## DATA-M-079: lost update not detected

- Difficulty: Medium
- Framework: Spring Data & Repositories
- Language: Java
- Perspective: Optimistic locking
- Concept: lost update not detected
- Symptom: Last writer silently wins.
- Diagnostic goal: Add a version column and handle optimistic lock failures.

### Buggy code

```java
@Entity class Inventory { Long id; int quantity; }
```

### Expected diagnosis

Without @Version, stale writes are accepted.

### Corrected code

```java
@Version
private long version;
```

### Regression tests

```java
// Two updates from the same version cause one OptimisticLockException.
```

## DATA-M-080: repository test uses production schema

- Difficulty: Medium
- Framework: Spring Data & Repositories
- Language: Java
- Perspective: Test data
- Concept: repository test uses production schema
- Symptom: Tests are slow or modify shared data.
- Diagnostic goal: Use an isolated test database and rollback policy.

### Buggy code

```java
@SpringBootTest
class ItemRepositoryTest {}
```

### Expected diagnosis

A full context may load production datasource settings.

### Corrected code

```java
@DataJpaTest
@ActiveProfiles("test")
class ItemRepositoryTest {}
```

### Regression tests

```java
// The test uses an isolated database and rolls back each test.
```

## DATA-M-081: read-modify-write race

- Difficulty: Medium
- Framework: Spring Data & Repositories
- Language: Java
- Perspective: Transactions
- Concept: read-modify-write race
- Symptom: Concurrent updates lose changes.
- Diagnostic goal: Use a transaction and a locking or atomic update strategy.

### Buggy code

```java
entity.setCount(entity.getCount() + 1); repository.save(entity);
```

### Expected diagnosis

Separate requests can read the same old count and overwrite one another.

### Corrected code

```java
@Transactional
@Modifying
@Query("update Item i set i.count = i.count + 1 where i.id = :id")
void increment(long id);
```

### Regression tests

```java
// Concurrent increments equal the number of successful calls.
```

## DATA-M-082: lazy relation in loop

- Difficulty: Medium
- Framework: Spring Data & Repositories
- Language: Java
- Perspective: N+1 queries
- Concept: lazy relation in loop
- Symptom: A page triggers one query per row.
- Diagnostic goal: Fetch the relation with an explicit query plan.

### Buggy code

```java
orders.findAll().forEach(o -> o.getCustomer().getName());
```

### Expected diagnosis

Lazy access in a loop produces N additional selects.

### Corrected code

```java
@EntityGraph(attributePaths = "customer")
List<Order> findAll();
```

### Regression tests

```java
// SQL logging shows one query for the page and relation.
```

## DATA-M-083: session closed before serialization

- Difficulty: Medium
- Framework: Spring Data & Repositories
- Language: Java
- Perspective: Lazy loading
- Concept: session closed before serialization
- Symptom: JSON serialization throws LazyInitializationException.
- Diagnostic goal: Map entities to DTOs inside the transaction.

### Buggy code

```java
return repository.findById(id).orElseThrow();
```

### Expected diagnosis

The web serializer touches a lazy association after the persistence context is closed.

### Corrected code

```java
@Transactional
public OrderDto get(long id) { Order o = repository.findById(id).orElseThrow(); return OrderDto.from(o); }
```

### Regression tests

```java
// DTO serialization never triggers lazy loading.
```

## DATA-M-084: derived name means wrong predicate

- Difficulty: Medium
- Framework: Spring Data & Repositories
- Language: Java
- Perspective: Query methods
- Concept: derived name means wrong predicate
- Symptom: The repository returns unexpected rows.
- Diagnostic goal: Read the derived query name as a precise predicate.

### Buggy code

```java
List<User> findByNameOrEmailAndActive(String name, String email, boolean active);
```

### Expected diagnosis

Operator precedence may be parsed as name OR (email AND active), not (name OR email) AND active.

### Corrected code

```java
@Query("select u from User u where (u.name = :name or u.email = :email) and u.active = :active")
List<User> findActive(...);
```

### Regression tests

```java
// Inactive matches are never returned through either field.
```

## DATA-M-085: unbounded findAll

- Difficulty: Medium
- Framework: Spring Data & Repositories
- Language: Java
- Perspective: Pagination
- Concept: unbounded findAll
- Symptom: Memory and response time grow with table size.
- Diagnostic goal: Expose bounded page or slice queries.

### Buggy code

```java
List<Order> findByStatus(Status status);
```

### Expected diagnosis

Returning every matching entity has no upper bound.

### Corrected code

```java
Page<Order> findByStatus(Status status, Pageable pageable);
```

### Regression tests

```java
// A request with page size 50 never loads more than one page.
```

## DATA-M-086: stale persistence context

- Difficulty: Medium
- Framework: Spring Data & Repositories
- Language: Java
- Perspective: Bulk updates
- Concept: stale persistence context
- Symptom: A later read returns pre-update values.
- Diagnostic goal: Clear or refresh the persistence context after bulk DML.

### Buggy code

```java
@Modifying
@Query("update User u set u.active=false")
void deactivateAll();
```

### Expected diagnosis

Bulk JPQL bypasses managed entity state already held in the context.

### Corrected code

```java
@Modifying(clearAutomatically = true, flushAutomatically = true)
@Query("update User u set u.active=false")
void deactivateAll();
```

### Regression tests

```java
// The next repository read reflects the bulk update.
```

## DATA-M-087: equals null in JPQL

- Difficulty: Medium
- Framework: Spring Data & Repositories
- Language: Java
- Perspective: Null semantics
- Concept: equals null in JPQL
- Symptom: Rows with null values are not found.
- Diagnostic goal: Use IS NULL semantics or derived methods.

### Buggy code

```java
@Query("select x from Item x where x.note = null")
List<Item> missingNote();
```

### Expected diagnosis

SQL null is not equal to null; the predicate is never true.

### Corrected code

```java
@Query("select x from Item x where x.note is null")
List<Item> missingNote();
```

### Regression tests

```java
// Rows with a null note are returned.
```

## DATA-M-088: auditor not populated

- Difficulty: Medium
- Framework: Spring Data & Repositories
- Language: Java
- Perspective: Auditing
- Concept: auditor not populated
- Symptom: CreatedBy fields remain null.
- Diagnostic goal: Enable auditing and provide an authenticated auditor supplier.

### Buggy code

```java
class AuditConfig {}
```

### Expected diagnosis

The entity annotations alone do not activate Spring Data auditing.

### Corrected code

```java
@EnableJpaAuditing
@Configuration
class AuditConfig { @Bean AuditorAware<String> auditor() { return () -> Optional.of("system"); } }
```

### Regression tests

```java
// Save asserts createdBy is populated.
```

## DATA-M-089: lost update not detected

- Difficulty: Medium
- Framework: Spring Data & Repositories
- Language: Java
- Perspective: Optimistic locking
- Concept: lost update not detected
- Symptom: Last writer silently wins.
- Diagnostic goal: Add a version column and handle optimistic lock failures.

### Buggy code

```java
@Entity class Inventory { Long id; int quantity; }
```

### Expected diagnosis

Without @Version, stale writes are accepted.

### Corrected code

```java
@Version
private long version;
```

### Regression tests

```java
// Two updates from the same version cause one OptimisticLockException.
```

## DATA-M-090: repository test uses production schema

- Difficulty: Medium
- Framework: Spring Data & Repositories
- Language: Java
- Perspective: Test data
- Concept: repository test uses production schema
- Symptom: Tests are slow or modify shared data.
- Diagnostic goal: Use an isolated test database and rollback policy.

### Buggy code

```java
@SpringBootTest
class ItemRepositoryTest {}
```

### Expected diagnosis

A full context may load production datasource settings.

### Corrected code

```java
@DataJpaTest
@ActiveProfiles("test")
class ItemRepositoryTest {}
```

### Regression tests

```java
// The test uses an isolated database and rolls back each test.
```

## DATA-M-091: read-modify-write race

- Difficulty: Medium
- Framework: Spring Data & Repositories
- Language: Java
- Perspective: Transactions
- Concept: read-modify-write race
- Symptom: Concurrent updates lose changes.
- Diagnostic goal: Use a transaction and a locking or atomic update strategy.

### Buggy code

```java
entity.setCount(entity.getCount() + 1); repository.save(entity);
```

### Expected diagnosis

Separate requests can read the same old count and overwrite one another.

### Corrected code

```java
@Transactional
@Modifying
@Query("update Item i set i.count = i.count + 1 where i.id = :id")
void increment(long id);
```

### Regression tests

```java
// Concurrent increments equal the number of successful calls.
```

## DATA-M-092: lazy relation in loop

- Difficulty: Medium
- Framework: Spring Data & Repositories
- Language: Java
- Perspective: N+1 queries
- Concept: lazy relation in loop
- Symptom: A page triggers one query per row.
- Diagnostic goal: Fetch the relation with an explicit query plan.

### Buggy code

```java
orders.findAll().forEach(o -> o.getCustomer().getName());
```

### Expected diagnosis

Lazy access in a loop produces N additional selects.

### Corrected code

```java
@EntityGraph(attributePaths = "customer")
List<Order> findAll();
```

### Regression tests

```java
// SQL logging shows one query for the page and relation.
```

## DATA-M-093: session closed before serialization

- Difficulty: Medium
- Framework: Spring Data & Repositories
- Language: Java
- Perspective: Lazy loading
- Concept: session closed before serialization
- Symptom: JSON serialization throws LazyInitializationException.
- Diagnostic goal: Map entities to DTOs inside the transaction.

### Buggy code

```java
return repository.findById(id).orElseThrow();
```

### Expected diagnosis

The web serializer touches a lazy association after the persistence context is closed.

### Corrected code

```java
@Transactional
public OrderDto get(long id) { Order o = repository.findById(id).orElseThrow(); return OrderDto.from(o); }
```

### Regression tests

```java
// DTO serialization never triggers lazy loading.
```

## DATA-M-094: derived name means wrong predicate

- Difficulty: Medium
- Framework: Spring Data & Repositories
- Language: Java
- Perspective: Query methods
- Concept: derived name means wrong predicate
- Symptom: The repository returns unexpected rows.
- Diagnostic goal: Read the derived query name as a precise predicate.

### Buggy code

```java
List<User> findByNameOrEmailAndActive(String name, String email, boolean active);
```

### Expected diagnosis

Operator precedence may be parsed as name OR (email AND active), not (name OR email) AND active.

### Corrected code

```java
@Query("select u from User u where (u.name = :name or u.email = :email) and u.active = :active")
List<User> findActive(...);
```

### Regression tests

```java
// Inactive matches are never returned through either field.
```

## DATA-M-095: unbounded findAll

- Difficulty: Medium
- Framework: Spring Data & Repositories
- Language: Java
- Perspective: Pagination
- Concept: unbounded findAll
- Symptom: Memory and response time grow with table size.
- Diagnostic goal: Expose bounded page or slice queries.

### Buggy code

```java
List<Order> findByStatus(Status status);
```

### Expected diagnosis

Returning every matching entity has no upper bound.

### Corrected code

```java
Page<Order> findByStatus(Status status, Pageable pageable);
```

### Regression tests

```java
// A request with page size 50 never loads more than one page.
```

## DATA-M-096: stale persistence context

- Difficulty: Medium
- Framework: Spring Data & Repositories
- Language: Java
- Perspective: Bulk updates
- Concept: stale persistence context
- Symptom: A later read returns pre-update values.
- Diagnostic goal: Clear or refresh the persistence context after bulk DML.

### Buggy code

```java
@Modifying
@Query("update User u set u.active=false")
void deactivateAll();
```

### Expected diagnosis

Bulk JPQL bypasses managed entity state already held in the context.

### Corrected code

```java
@Modifying(clearAutomatically = true, flushAutomatically = true)
@Query("update User u set u.active=false")
void deactivateAll();
```

### Regression tests

```java
// The next repository read reflects the bulk update.
```

## DATA-M-097: equals null in JPQL

- Difficulty: Medium
- Framework: Spring Data & Repositories
- Language: Java
- Perspective: Null semantics
- Concept: equals null in JPQL
- Symptom: Rows with null values are not found.
- Diagnostic goal: Use IS NULL semantics or derived methods.

### Buggy code

```java
@Query("select x from Item x where x.note = null")
List<Item> missingNote();
```

### Expected diagnosis

SQL null is not equal to null; the predicate is never true.

### Corrected code

```java
@Query("select x from Item x where x.note is null")
List<Item> missingNote();
```

### Regression tests

```java
// Rows with a null note are returned.
```

## DATA-M-098: auditor not populated

- Difficulty: Medium
- Framework: Spring Data & Repositories
- Language: Java
- Perspective: Auditing
- Concept: auditor not populated
- Symptom: CreatedBy fields remain null.
- Diagnostic goal: Enable auditing and provide an authenticated auditor supplier.

### Buggy code

```java
class AuditConfig {}
```

### Expected diagnosis

The entity annotations alone do not activate Spring Data auditing.

### Corrected code

```java
@EnableJpaAuditing
@Configuration
class AuditConfig { @Bean AuditorAware<String> auditor() { return () -> Optional.of("system"); } }
```

### Regression tests

```java
// Save asserts createdBy is populated.
```

## DATA-M-099: lost update not detected

- Difficulty: Medium
- Framework: Spring Data & Repositories
- Language: Java
- Perspective: Optimistic locking
- Concept: lost update not detected
- Symptom: Last writer silently wins.
- Diagnostic goal: Add a version column and handle optimistic lock failures.

### Buggy code

```java
@Entity class Inventory { Long id; int quantity; }
```

### Expected diagnosis

Without @Version, stale writes are accepted.

### Corrected code

```java
@Version
private long version;
```

### Regression tests

```java
// Two updates from the same version cause one OptimisticLockException.
```

## DATA-M-100: repository test uses production schema

- Difficulty: Medium
- Framework: Spring Data & Repositories
- Language: Java
- Perspective: Test data
- Concept: repository test uses production schema
- Symptom: Tests are slow or modify shared data.
- Diagnostic goal: Use an isolated test database and rollback policy.

### Buggy code

```java
@SpringBootTest
class ItemRepositoryTest {}
```

### Expected diagnosis

A full context may load production datasource settings.

### Corrected code

```java
@DataJpaTest
@ActiveProfiles("test")
class ItemRepositoryTest {}
```

### Regression tests

```java
// The test uses an isolated database and rolls back each test.
```

## DATA-H-001: read-modify-write race

- Difficulty: Hard
- Framework: Spring Data & Repositories
- Language: Java
- Perspective: Transactions
- Concept: read-modify-write race
- Symptom: Concurrent updates lose changes.
- Diagnostic goal: Use a transaction and a locking or atomic update strategy.

### Buggy code

```java
entity.setCount(entity.getCount() + 1); repository.save(entity);
```

### Expected diagnosis

Separate requests can read the same old count and overwrite one another.

### Corrected code

```java
@Transactional
@Modifying
@Query("update Item i set i.count = i.count + 1 where i.id = :id")
void increment(long id);
```

### Regression tests

```java
// Concurrent increments equal the number of successful calls.
```

## DATA-H-002: lazy relation in loop

- Difficulty: Hard
- Framework: Spring Data & Repositories
- Language: Java
- Perspective: N+1 queries
- Concept: lazy relation in loop
- Symptom: A page triggers one query per row.
- Diagnostic goal: Fetch the relation with an explicit query plan.

### Buggy code

```java
orders.findAll().forEach(o -> o.getCustomer().getName());
```

### Expected diagnosis

Lazy access in a loop produces N additional selects.

### Corrected code

```java
@EntityGraph(attributePaths = "customer")
List<Order> findAll();
```

### Regression tests

```java
// SQL logging shows one query for the page and relation.
```

## DATA-H-003: session closed before serialization

- Difficulty: Hard
- Framework: Spring Data & Repositories
- Language: Java
- Perspective: Lazy loading
- Concept: session closed before serialization
- Symptom: JSON serialization throws LazyInitializationException.
- Diagnostic goal: Map entities to DTOs inside the transaction.

### Buggy code

```java
return repository.findById(id).orElseThrow();
```

### Expected diagnosis

The web serializer touches a lazy association after the persistence context is closed.

### Corrected code

```java
@Transactional
public OrderDto get(long id) { Order o = repository.findById(id).orElseThrow(); return OrderDto.from(o); }
```

### Regression tests

```java
// DTO serialization never triggers lazy loading.
```

## DATA-H-004: derived name means wrong predicate

- Difficulty: Hard
- Framework: Spring Data & Repositories
- Language: Java
- Perspective: Query methods
- Concept: derived name means wrong predicate
- Symptom: The repository returns unexpected rows.
- Diagnostic goal: Read the derived query name as a precise predicate.

### Buggy code

```java
List<User> findByNameOrEmailAndActive(String name, String email, boolean active);
```

### Expected diagnosis

Operator precedence may be parsed as name OR (email AND active), not (name OR email) AND active.

### Corrected code

```java
@Query("select u from User u where (u.name = :name or u.email = :email) and u.active = :active")
List<User> findActive(...);
```

### Regression tests

```java
// Inactive matches are never returned through either field.
```

## DATA-H-005: unbounded findAll

- Difficulty: Hard
- Framework: Spring Data & Repositories
- Language: Java
- Perspective: Pagination
- Concept: unbounded findAll
- Symptom: Memory and response time grow with table size.
- Diagnostic goal: Expose bounded page or slice queries.

### Buggy code

```java
List<Order> findByStatus(Status status);
```

### Expected diagnosis

Returning every matching entity has no upper bound.

### Corrected code

```java
Page<Order> findByStatus(Status status, Pageable pageable);
```

### Regression tests

```java
// A request with page size 50 never loads more than one page.
```

## DATA-H-006: stale persistence context

- Difficulty: Hard
- Framework: Spring Data & Repositories
- Language: Java
- Perspective: Bulk updates
- Concept: stale persistence context
- Symptom: A later read returns pre-update values.
- Diagnostic goal: Clear or refresh the persistence context after bulk DML.

### Buggy code

```java
@Modifying
@Query("update User u set u.active=false")
void deactivateAll();
```

### Expected diagnosis

Bulk JPQL bypasses managed entity state already held in the context.

### Corrected code

```java
@Modifying(clearAutomatically = true, flushAutomatically = true)
@Query("update User u set u.active=false")
void deactivateAll();
```

### Regression tests

```java
// The next repository read reflects the bulk update.
```

## DATA-H-007: equals null in JPQL

- Difficulty: Hard
- Framework: Spring Data & Repositories
- Language: Java
- Perspective: Null semantics
- Concept: equals null in JPQL
- Symptom: Rows with null values are not found.
- Diagnostic goal: Use IS NULL semantics or derived methods.

### Buggy code

```java
@Query("select x from Item x where x.note = null")
List<Item> missingNote();
```

### Expected diagnosis

SQL null is not equal to null; the predicate is never true.

### Corrected code

```java
@Query("select x from Item x where x.note is null")
List<Item> missingNote();
```

### Regression tests

```java
// Rows with a null note are returned.
```

## DATA-H-008: auditor not populated

- Difficulty: Hard
- Framework: Spring Data & Repositories
- Language: Java
- Perspective: Auditing
- Concept: auditor not populated
- Symptom: CreatedBy fields remain null.
- Diagnostic goal: Enable auditing and provide an authenticated auditor supplier.

### Buggy code

```java
class AuditConfig {}
```

### Expected diagnosis

The entity annotations alone do not activate Spring Data auditing.

### Corrected code

```java
@EnableJpaAuditing
@Configuration
class AuditConfig { @Bean AuditorAware<String> auditor() { return () -> Optional.of("system"); } }
```

### Regression tests

```java
// Save asserts createdBy is populated.
```

## DATA-H-009: lost update not detected

- Difficulty: Hard
- Framework: Spring Data & Repositories
- Language: Java
- Perspective: Optimistic locking
- Concept: lost update not detected
- Symptom: Last writer silently wins.
- Diagnostic goal: Add a version column and handle optimistic lock failures.

### Buggy code

```java
@Entity class Inventory { Long id; int quantity; }
```

### Expected diagnosis

Without @Version, stale writes are accepted.

### Corrected code

```java
@Version
private long version;
```

### Regression tests

```java
// Two updates from the same version cause one OptimisticLockException.
```

## DATA-H-010: repository test uses production schema

- Difficulty: Hard
- Framework: Spring Data & Repositories
- Language: Java
- Perspective: Test data
- Concept: repository test uses production schema
- Symptom: Tests are slow or modify shared data.
- Diagnostic goal: Use an isolated test database and rollback policy.

### Buggy code

```java
@SpringBootTest
class ItemRepositoryTest {}
```

### Expected diagnosis

A full context may load production datasource settings.

### Corrected code

```java
@DataJpaTest
@ActiveProfiles("test")
class ItemRepositoryTest {}
```

### Regression tests

```java
// The test uses an isolated database and rolls back each test.
```

## DATA-H-011: read-modify-write race

- Difficulty: Hard
- Framework: Spring Data & Repositories
- Language: Java
- Perspective: Transactions
- Concept: read-modify-write race
- Symptom: Concurrent updates lose changes.
- Diagnostic goal: Use a transaction and a locking or atomic update strategy.

### Buggy code

```java
entity.setCount(entity.getCount() + 1); repository.save(entity);
```

### Expected diagnosis

Separate requests can read the same old count and overwrite one another.

### Corrected code

```java
@Transactional
@Modifying
@Query("update Item i set i.count = i.count + 1 where i.id = :id")
void increment(long id);
```

### Regression tests

```java
// Concurrent increments equal the number of successful calls.
```

## DATA-H-012: lazy relation in loop

- Difficulty: Hard
- Framework: Spring Data & Repositories
- Language: Java
- Perspective: N+1 queries
- Concept: lazy relation in loop
- Symptom: A page triggers one query per row.
- Diagnostic goal: Fetch the relation with an explicit query plan.

### Buggy code

```java
orders.findAll().forEach(o -> o.getCustomer().getName());
```

### Expected diagnosis

Lazy access in a loop produces N additional selects.

### Corrected code

```java
@EntityGraph(attributePaths = "customer")
List<Order> findAll();
```

### Regression tests

```java
// SQL logging shows one query for the page and relation.
```

## DATA-H-013: session closed before serialization

- Difficulty: Hard
- Framework: Spring Data & Repositories
- Language: Java
- Perspective: Lazy loading
- Concept: session closed before serialization
- Symptom: JSON serialization throws LazyInitializationException.
- Diagnostic goal: Map entities to DTOs inside the transaction.

### Buggy code

```java
return repository.findById(id).orElseThrow();
```

### Expected diagnosis

The web serializer touches a lazy association after the persistence context is closed.

### Corrected code

```java
@Transactional
public OrderDto get(long id) { Order o = repository.findById(id).orElseThrow(); return OrderDto.from(o); }
```

### Regression tests

```java
// DTO serialization never triggers lazy loading.
```

## DATA-H-014: derived name means wrong predicate

- Difficulty: Hard
- Framework: Spring Data & Repositories
- Language: Java
- Perspective: Query methods
- Concept: derived name means wrong predicate
- Symptom: The repository returns unexpected rows.
- Diagnostic goal: Read the derived query name as a precise predicate.

### Buggy code

```java
List<User> findByNameOrEmailAndActive(String name, String email, boolean active);
```

### Expected diagnosis

Operator precedence may be parsed as name OR (email AND active), not (name OR email) AND active.

### Corrected code

```java
@Query("select u from User u where (u.name = :name or u.email = :email) and u.active = :active")
List<User> findActive(...);
```

### Regression tests

```java
// Inactive matches are never returned through either field.
```

## DATA-H-015: unbounded findAll

- Difficulty: Hard
- Framework: Spring Data & Repositories
- Language: Java
- Perspective: Pagination
- Concept: unbounded findAll
- Symptom: Memory and response time grow with table size.
- Diagnostic goal: Expose bounded page or slice queries.

### Buggy code

```java
List<Order> findByStatus(Status status);
```

### Expected diagnosis

Returning every matching entity has no upper bound.

### Corrected code

```java
Page<Order> findByStatus(Status status, Pageable pageable);
```

### Regression tests

```java
// A request with page size 50 never loads more than one page.
```

## DATA-H-016: stale persistence context

- Difficulty: Hard
- Framework: Spring Data & Repositories
- Language: Java
- Perspective: Bulk updates
- Concept: stale persistence context
- Symptom: A later read returns pre-update values.
- Diagnostic goal: Clear or refresh the persistence context after bulk DML.

### Buggy code

```java
@Modifying
@Query("update User u set u.active=false")
void deactivateAll();
```

### Expected diagnosis

Bulk JPQL bypasses managed entity state already held in the context.

### Corrected code

```java
@Modifying(clearAutomatically = true, flushAutomatically = true)
@Query("update User u set u.active=false")
void deactivateAll();
```

### Regression tests

```java
// The next repository read reflects the bulk update.
```

## DATA-H-017: equals null in JPQL

- Difficulty: Hard
- Framework: Spring Data & Repositories
- Language: Java
- Perspective: Null semantics
- Concept: equals null in JPQL
- Symptom: Rows with null values are not found.
- Diagnostic goal: Use IS NULL semantics or derived methods.

### Buggy code

```java
@Query("select x from Item x where x.note = null")
List<Item> missingNote();
```

### Expected diagnosis

SQL null is not equal to null; the predicate is never true.

### Corrected code

```java
@Query("select x from Item x where x.note is null")
List<Item> missingNote();
```

### Regression tests

```java
// Rows with a null note are returned.
```

## DATA-H-018: auditor not populated

- Difficulty: Hard
- Framework: Spring Data & Repositories
- Language: Java
- Perspective: Auditing
- Concept: auditor not populated
- Symptom: CreatedBy fields remain null.
- Diagnostic goal: Enable auditing and provide an authenticated auditor supplier.

### Buggy code

```java
class AuditConfig {}
```

### Expected diagnosis

The entity annotations alone do not activate Spring Data auditing.

### Corrected code

```java
@EnableJpaAuditing
@Configuration
class AuditConfig { @Bean AuditorAware<String> auditor() { return () -> Optional.of("system"); } }
```

### Regression tests

```java
// Save asserts createdBy is populated.
```

## DATA-H-019: lost update not detected

- Difficulty: Hard
- Framework: Spring Data & Repositories
- Language: Java
- Perspective: Optimistic locking
- Concept: lost update not detected
- Symptom: Last writer silently wins.
- Diagnostic goal: Add a version column and handle optimistic lock failures.

### Buggy code

```java
@Entity class Inventory { Long id; int quantity; }
```

### Expected diagnosis

Without @Version, stale writes are accepted.

### Corrected code

```java
@Version
private long version;
```

### Regression tests

```java
// Two updates from the same version cause one OptimisticLockException.
```

## DATA-H-020: repository test uses production schema

- Difficulty: Hard
- Framework: Spring Data & Repositories
- Language: Java
- Perspective: Test data
- Concept: repository test uses production schema
- Symptom: Tests are slow or modify shared data.
- Diagnostic goal: Use an isolated test database and rollback policy.

### Buggy code

```java
@SpringBootTest
class ItemRepositoryTest {}
```

### Expected diagnosis

A full context may load production datasource settings.

### Corrected code

```java
@DataJpaTest
@ActiveProfiles("test")
class ItemRepositoryTest {}
```

### Regression tests

```java
// The test uses an isolated database and rolls back each test.
```

## DATA-H-021: read-modify-write race

- Difficulty: Hard
- Framework: Spring Data & Repositories
- Language: Java
- Perspective: Transactions
- Concept: read-modify-write race
- Symptom: Concurrent updates lose changes.
- Diagnostic goal: Use a transaction and a locking or atomic update strategy.

### Buggy code

```java
entity.setCount(entity.getCount() + 1); repository.save(entity);
```

### Expected diagnosis

Separate requests can read the same old count and overwrite one another.

### Corrected code

```java
@Transactional
@Modifying
@Query("update Item i set i.count = i.count + 1 where i.id = :id")
void increment(long id);
```

### Regression tests

```java
// Concurrent increments equal the number of successful calls.
```

## DATA-H-022: lazy relation in loop

- Difficulty: Hard
- Framework: Spring Data & Repositories
- Language: Java
- Perspective: N+1 queries
- Concept: lazy relation in loop
- Symptom: A page triggers one query per row.
- Diagnostic goal: Fetch the relation with an explicit query plan.

### Buggy code

```java
orders.findAll().forEach(o -> o.getCustomer().getName());
```

### Expected diagnosis

Lazy access in a loop produces N additional selects.

### Corrected code

```java
@EntityGraph(attributePaths = "customer")
List<Order> findAll();
```

### Regression tests

```java
// SQL logging shows one query for the page and relation.
```

## DATA-H-023: session closed before serialization

- Difficulty: Hard
- Framework: Spring Data & Repositories
- Language: Java
- Perspective: Lazy loading
- Concept: session closed before serialization
- Symptom: JSON serialization throws LazyInitializationException.
- Diagnostic goal: Map entities to DTOs inside the transaction.

### Buggy code

```java
return repository.findById(id).orElseThrow();
```

### Expected diagnosis

The web serializer touches a lazy association after the persistence context is closed.

### Corrected code

```java
@Transactional
public OrderDto get(long id) { Order o = repository.findById(id).orElseThrow(); return OrderDto.from(o); }
```

### Regression tests

```java
// DTO serialization never triggers lazy loading.
```

## DATA-H-024: derived name means wrong predicate

- Difficulty: Hard
- Framework: Spring Data & Repositories
- Language: Java
- Perspective: Query methods
- Concept: derived name means wrong predicate
- Symptom: The repository returns unexpected rows.
- Diagnostic goal: Read the derived query name as a precise predicate.

### Buggy code

```java
List<User> findByNameOrEmailAndActive(String name, String email, boolean active);
```

### Expected diagnosis

Operator precedence may be parsed as name OR (email AND active), not (name OR email) AND active.

### Corrected code

```java
@Query("select u from User u where (u.name = :name or u.email = :email) and u.active = :active")
List<User> findActive(...);
```

### Regression tests

```java
// Inactive matches are never returned through either field.
```

## DATA-H-025: unbounded findAll

- Difficulty: Hard
- Framework: Spring Data & Repositories
- Language: Java
- Perspective: Pagination
- Concept: unbounded findAll
- Symptom: Memory and response time grow with table size.
- Diagnostic goal: Expose bounded page or slice queries.

### Buggy code

```java
List<Order> findByStatus(Status status);
```

### Expected diagnosis

Returning every matching entity has no upper bound.

### Corrected code

```java
Page<Order> findByStatus(Status status, Pageable pageable);
```

### Regression tests

```java
// A request with page size 50 never loads more than one page.
```

## DATA-H-026: stale persistence context

- Difficulty: Hard
- Framework: Spring Data & Repositories
- Language: Java
- Perspective: Bulk updates
- Concept: stale persistence context
- Symptom: A later read returns pre-update values.
- Diagnostic goal: Clear or refresh the persistence context after bulk DML.

### Buggy code

```java
@Modifying
@Query("update User u set u.active=false")
void deactivateAll();
```

### Expected diagnosis

Bulk JPQL bypasses managed entity state already held in the context.

### Corrected code

```java
@Modifying(clearAutomatically = true, flushAutomatically = true)
@Query("update User u set u.active=false")
void deactivateAll();
```

### Regression tests

```java
// The next repository read reflects the bulk update.
```

## DATA-H-027: equals null in JPQL

- Difficulty: Hard
- Framework: Spring Data & Repositories
- Language: Java
- Perspective: Null semantics
- Concept: equals null in JPQL
- Symptom: Rows with null values are not found.
- Diagnostic goal: Use IS NULL semantics or derived methods.

### Buggy code

```java
@Query("select x from Item x where x.note = null")
List<Item> missingNote();
```

### Expected diagnosis

SQL null is not equal to null; the predicate is never true.

### Corrected code

```java
@Query("select x from Item x where x.note is null")
List<Item> missingNote();
```

### Regression tests

```java
// Rows with a null note are returned.
```

## DATA-H-028: auditor not populated

- Difficulty: Hard
- Framework: Spring Data & Repositories
- Language: Java
- Perspective: Auditing
- Concept: auditor not populated
- Symptom: CreatedBy fields remain null.
- Diagnostic goal: Enable auditing and provide an authenticated auditor supplier.

### Buggy code

```java
class AuditConfig {}
```

### Expected diagnosis

The entity annotations alone do not activate Spring Data auditing.

### Corrected code

```java
@EnableJpaAuditing
@Configuration
class AuditConfig { @Bean AuditorAware<String> auditor() { return () -> Optional.of("system"); } }
```

### Regression tests

```java
// Save asserts createdBy is populated.
```

## DATA-H-029: lost update not detected

- Difficulty: Hard
- Framework: Spring Data & Repositories
- Language: Java
- Perspective: Optimistic locking
- Concept: lost update not detected
- Symptom: Last writer silently wins.
- Diagnostic goal: Add a version column and handle optimistic lock failures.

### Buggy code

```java
@Entity class Inventory { Long id; int quantity; }
```

### Expected diagnosis

Without @Version, stale writes are accepted.

### Corrected code

```java
@Version
private long version;
```

### Regression tests

```java
// Two updates from the same version cause one OptimisticLockException.
```

## DATA-H-030: repository test uses production schema

- Difficulty: Hard
- Framework: Spring Data & Repositories
- Language: Java
- Perspective: Test data
- Concept: repository test uses production schema
- Symptom: Tests are slow or modify shared data.
- Diagnostic goal: Use an isolated test database and rollback policy.

### Buggy code

```java
@SpringBootTest
class ItemRepositoryTest {}
```

### Expected diagnosis

A full context may load production datasource settings.

### Corrected code

```java
@DataJpaTest
@ActiveProfiles("test")
class ItemRepositoryTest {}
```

### Regression tests

```java
// The test uses an isolated database and rolls back each test.
```

## DATA-H-031: read-modify-write race

- Difficulty: Hard
- Framework: Spring Data & Repositories
- Language: Java
- Perspective: Transactions
- Concept: read-modify-write race
- Symptom: Concurrent updates lose changes.
- Diagnostic goal: Use a transaction and a locking or atomic update strategy.

### Buggy code

```java
entity.setCount(entity.getCount() + 1); repository.save(entity);
```

### Expected diagnosis

Separate requests can read the same old count and overwrite one another.

### Corrected code

```java
@Transactional
@Modifying
@Query("update Item i set i.count = i.count + 1 where i.id = :id")
void increment(long id);
```

### Regression tests

```java
// Concurrent increments equal the number of successful calls.
```

## DATA-H-032: lazy relation in loop

- Difficulty: Hard
- Framework: Spring Data & Repositories
- Language: Java
- Perspective: N+1 queries
- Concept: lazy relation in loop
- Symptom: A page triggers one query per row.
- Diagnostic goal: Fetch the relation with an explicit query plan.

### Buggy code

```java
orders.findAll().forEach(o -> o.getCustomer().getName());
```

### Expected diagnosis

Lazy access in a loop produces N additional selects.

### Corrected code

```java
@EntityGraph(attributePaths = "customer")
List<Order> findAll();
```

### Regression tests

```java
// SQL logging shows one query for the page and relation.
```

## DATA-H-033: session closed before serialization

- Difficulty: Hard
- Framework: Spring Data & Repositories
- Language: Java
- Perspective: Lazy loading
- Concept: session closed before serialization
- Symptom: JSON serialization throws LazyInitializationException.
- Diagnostic goal: Map entities to DTOs inside the transaction.

### Buggy code

```java
return repository.findById(id).orElseThrow();
```

### Expected diagnosis

The web serializer touches a lazy association after the persistence context is closed.

### Corrected code

```java
@Transactional
public OrderDto get(long id) { Order o = repository.findById(id).orElseThrow(); return OrderDto.from(o); }
```

### Regression tests

```java
// DTO serialization never triggers lazy loading.
```

## DATA-H-034: derived name means wrong predicate

- Difficulty: Hard
- Framework: Spring Data & Repositories
- Language: Java
- Perspective: Query methods
- Concept: derived name means wrong predicate
- Symptom: The repository returns unexpected rows.
- Diagnostic goal: Read the derived query name as a precise predicate.

### Buggy code

```java
List<User> findByNameOrEmailAndActive(String name, String email, boolean active);
```

### Expected diagnosis

Operator precedence may be parsed as name OR (email AND active), not (name OR email) AND active.

### Corrected code

```java
@Query("select u from User u where (u.name = :name or u.email = :email) and u.active = :active")
List<User> findActive(...);
```

### Regression tests

```java
// Inactive matches are never returned through either field.
```

## DATA-H-035: unbounded findAll

- Difficulty: Hard
- Framework: Spring Data & Repositories
- Language: Java
- Perspective: Pagination
- Concept: unbounded findAll
- Symptom: Memory and response time grow with table size.
- Diagnostic goal: Expose bounded page or slice queries.

### Buggy code

```java
List<Order> findByStatus(Status status);
```

### Expected diagnosis

Returning every matching entity has no upper bound.

### Corrected code

```java
Page<Order> findByStatus(Status status, Pageable pageable);
```

### Regression tests

```java
// A request with page size 50 never loads more than one page.
```

## DATA-H-036: stale persistence context

- Difficulty: Hard
- Framework: Spring Data & Repositories
- Language: Java
- Perspective: Bulk updates
- Concept: stale persistence context
- Symptom: A later read returns pre-update values.
- Diagnostic goal: Clear or refresh the persistence context after bulk DML.

### Buggy code

```java
@Modifying
@Query("update User u set u.active=false")
void deactivateAll();
```

### Expected diagnosis

Bulk JPQL bypasses managed entity state already held in the context.

### Corrected code

```java
@Modifying(clearAutomatically = true, flushAutomatically = true)
@Query("update User u set u.active=false")
void deactivateAll();
```

### Regression tests

```java
// The next repository read reflects the bulk update.
```

## DATA-H-037: equals null in JPQL

- Difficulty: Hard
- Framework: Spring Data & Repositories
- Language: Java
- Perspective: Null semantics
- Concept: equals null in JPQL
- Symptom: Rows with null values are not found.
- Diagnostic goal: Use IS NULL semantics or derived methods.

### Buggy code

```java
@Query("select x from Item x where x.note = null")
List<Item> missingNote();
```

### Expected diagnosis

SQL null is not equal to null; the predicate is never true.

### Corrected code

```java
@Query("select x from Item x where x.note is null")
List<Item> missingNote();
```

### Regression tests

```java
// Rows with a null note are returned.
```

## DATA-H-038: auditor not populated

- Difficulty: Hard
- Framework: Spring Data & Repositories
- Language: Java
- Perspective: Auditing
- Concept: auditor not populated
- Symptom: CreatedBy fields remain null.
- Diagnostic goal: Enable auditing and provide an authenticated auditor supplier.

### Buggy code

```java
class AuditConfig {}
```

### Expected diagnosis

The entity annotations alone do not activate Spring Data auditing.

### Corrected code

```java
@EnableJpaAuditing
@Configuration
class AuditConfig { @Bean AuditorAware<String> auditor() { return () -> Optional.of("system"); } }
```

### Regression tests

```java
// Save asserts createdBy is populated.
```

## DATA-H-039: lost update not detected

- Difficulty: Hard
- Framework: Spring Data & Repositories
- Language: Java
- Perspective: Optimistic locking
- Concept: lost update not detected
- Symptom: Last writer silently wins.
- Diagnostic goal: Add a version column and handle optimistic lock failures.

### Buggy code

```java
@Entity class Inventory { Long id; int quantity; }
```

### Expected diagnosis

Without @Version, stale writes are accepted.

### Corrected code

```java
@Version
private long version;
```

### Regression tests

```java
// Two updates from the same version cause one OptimisticLockException.
```

## DATA-H-040: repository test uses production schema

- Difficulty: Hard
- Framework: Spring Data & Repositories
- Language: Java
- Perspective: Test data
- Concept: repository test uses production schema
- Symptom: Tests are slow or modify shared data.
- Diagnostic goal: Use an isolated test database and rollback policy.

### Buggy code

```java
@SpringBootTest
class ItemRepositoryTest {}
```

### Expected diagnosis

A full context may load production datasource settings.

### Corrected code

```java
@DataJpaTest
@ActiveProfiles("test")
class ItemRepositoryTest {}
```

### Regression tests

```java
// The test uses an isolated database and rolls back each test.
```

## DATA-H-041: read-modify-write race

- Difficulty: Hard
- Framework: Spring Data & Repositories
- Language: Java
- Perspective: Transactions
- Concept: read-modify-write race
- Symptom: Concurrent updates lose changes.
- Diagnostic goal: Use a transaction and a locking or atomic update strategy.

### Buggy code

```java
entity.setCount(entity.getCount() + 1); repository.save(entity);
```

### Expected diagnosis

Separate requests can read the same old count and overwrite one another.

### Corrected code

```java
@Transactional
@Modifying
@Query("update Item i set i.count = i.count + 1 where i.id = :id")
void increment(long id);
```

### Regression tests

```java
// Concurrent increments equal the number of successful calls.
```

## DATA-H-042: lazy relation in loop

- Difficulty: Hard
- Framework: Spring Data & Repositories
- Language: Java
- Perspective: N+1 queries
- Concept: lazy relation in loop
- Symptom: A page triggers one query per row.
- Diagnostic goal: Fetch the relation with an explicit query plan.

### Buggy code

```java
orders.findAll().forEach(o -> o.getCustomer().getName());
```

### Expected diagnosis

Lazy access in a loop produces N additional selects.

### Corrected code

```java
@EntityGraph(attributePaths = "customer")
List<Order> findAll();
```

### Regression tests

```java
// SQL logging shows one query for the page and relation.
```

## DATA-H-043: session closed before serialization

- Difficulty: Hard
- Framework: Spring Data & Repositories
- Language: Java
- Perspective: Lazy loading
- Concept: session closed before serialization
- Symptom: JSON serialization throws LazyInitializationException.
- Diagnostic goal: Map entities to DTOs inside the transaction.

### Buggy code

```java
return repository.findById(id).orElseThrow();
```

### Expected diagnosis

The web serializer touches a lazy association after the persistence context is closed.

### Corrected code

```java
@Transactional
public OrderDto get(long id) { Order o = repository.findById(id).orElseThrow(); return OrderDto.from(o); }
```

### Regression tests

```java
// DTO serialization never triggers lazy loading.
```

## DATA-H-044: derived name means wrong predicate

- Difficulty: Hard
- Framework: Spring Data & Repositories
- Language: Java
- Perspective: Query methods
- Concept: derived name means wrong predicate
- Symptom: The repository returns unexpected rows.
- Diagnostic goal: Read the derived query name as a precise predicate.

### Buggy code

```java
List<User> findByNameOrEmailAndActive(String name, String email, boolean active);
```

### Expected diagnosis

Operator precedence may be parsed as name OR (email AND active), not (name OR email) AND active.

### Corrected code

```java
@Query("select u from User u where (u.name = :name or u.email = :email) and u.active = :active")
List<User> findActive(...);
```

### Regression tests

```java
// Inactive matches are never returned through either field.
```

## DATA-H-045: unbounded findAll

- Difficulty: Hard
- Framework: Spring Data & Repositories
- Language: Java
- Perspective: Pagination
- Concept: unbounded findAll
- Symptom: Memory and response time grow with table size.
- Diagnostic goal: Expose bounded page or slice queries.

### Buggy code

```java
List<Order> findByStatus(Status status);
```

### Expected diagnosis

Returning every matching entity has no upper bound.

### Corrected code

```java
Page<Order> findByStatus(Status status, Pageable pageable);
```

### Regression tests

```java
// A request with page size 50 never loads more than one page.
```

## DATA-H-046: stale persistence context

- Difficulty: Hard
- Framework: Spring Data & Repositories
- Language: Java
- Perspective: Bulk updates
- Concept: stale persistence context
- Symptom: A later read returns pre-update values.
- Diagnostic goal: Clear or refresh the persistence context after bulk DML.

### Buggy code

```java
@Modifying
@Query("update User u set u.active=false")
void deactivateAll();
```

### Expected diagnosis

Bulk JPQL bypasses managed entity state already held in the context.

### Corrected code

```java
@Modifying(clearAutomatically = true, flushAutomatically = true)
@Query("update User u set u.active=false")
void deactivateAll();
```

### Regression tests

```java
// The next repository read reflects the bulk update.
```

## DATA-H-047: equals null in JPQL

- Difficulty: Hard
- Framework: Spring Data & Repositories
- Language: Java
- Perspective: Null semantics
- Concept: equals null in JPQL
- Symptom: Rows with null values are not found.
- Diagnostic goal: Use IS NULL semantics or derived methods.

### Buggy code

```java
@Query("select x from Item x where x.note = null")
List<Item> missingNote();
```

### Expected diagnosis

SQL null is not equal to null; the predicate is never true.

### Corrected code

```java
@Query("select x from Item x where x.note is null")
List<Item> missingNote();
```

### Regression tests

```java
// Rows with a null note are returned.
```

## DATA-H-048: auditor not populated

- Difficulty: Hard
- Framework: Spring Data & Repositories
- Language: Java
- Perspective: Auditing
- Concept: auditor not populated
- Symptom: CreatedBy fields remain null.
- Diagnostic goal: Enable auditing and provide an authenticated auditor supplier.

### Buggy code

```java
class AuditConfig {}
```

### Expected diagnosis

The entity annotations alone do not activate Spring Data auditing.

### Corrected code

```java
@EnableJpaAuditing
@Configuration
class AuditConfig { @Bean AuditorAware<String> auditor() { return () -> Optional.of("system"); } }
```

### Regression tests

```java
// Save asserts createdBy is populated.
```

## DATA-H-049: lost update not detected

- Difficulty: Hard
- Framework: Spring Data & Repositories
- Language: Java
- Perspective: Optimistic locking
- Concept: lost update not detected
- Symptom: Last writer silently wins.
- Diagnostic goal: Add a version column and handle optimistic lock failures.

### Buggy code

```java
@Entity class Inventory { Long id; int quantity; }
```

### Expected diagnosis

Without @Version, stale writes are accepted.

### Corrected code

```java
@Version
private long version;
```

### Regression tests

```java
// Two updates from the same version cause one OptimisticLockException.
```

## DATA-H-050: repository test uses production schema

- Difficulty: Hard
- Framework: Spring Data & Repositories
- Language: Java
- Perspective: Test data
- Concept: repository test uses production schema
- Symptom: Tests are slow or modify shared data.
- Diagnostic goal: Use an isolated test database and rollback policy.

### Buggy code

```java
@SpringBootTest
class ItemRepositoryTest {}
```

### Expected diagnosis

A full context may load production datasource settings.

### Corrected code

```java
@DataJpaTest
@ActiveProfiles("test")
class ItemRepositoryTest {}
```

### Regression tests

```java
// The test uses an isolated database and rolls back each test.
```

## DATA-H-051: read-modify-write race

- Difficulty: Hard
- Framework: Spring Data & Repositories
- Language: Java
- Perspective: Transactions
- Concept: read-modify-write race
- Symptom: Concurrent updates lose changes.
- Diagnostic goal: Use a transaction and a locking or atomic update strategy.

### Buggy code

```java
entity.setCount(entity.getCount() + 1); repository.save(entity);
```

### Expected diagnosis

Separate requests can read the same old count and overwrite one another.

### Corrected code

```java
@Transactional
@Modifying
@Query("update Item i set i.count = i.count + 1 where i.id = :id")
void increment(long id);
```

### Regression tests

```java
// Concurrent increments equal the number of successful calls.
```

## DATA-H-052: lazy relation in loop

- Difficulty: Hard
- Framework: Spring Data & Repositories
- Language: Java
- Perspective: N+1 queries
- Concept: lazy relation in loop
- Symptom: A page triggers one query per row.
- Diagnostic goal: Fetch the relation with an explicit query plan.

### Buggy code

```java
orders.findAll().forEach(o -> o.getCustomer().getName());
```

### Expected diagnosis

Lazy access in a loop produces N additional selects.

### Corrected code

```java
@EntityGraph(attributePaths = "customer")
List<Order> findAll();
```

### Regression tests

```java
// SQL logging shows one query for the page and relation.
```

## DATA-H-053: session closed before serialization

- Difficulty: Hard
- Framework: Spring Data & Repositories
- Language: Java
- Perspective: Lazy loading
- Concept: session closed before serialization
- Symptom: JSON serialization throws LazyInitializationException.
- Diagnostic goal: Map entities to DTOs inside the transaction.

### Buggy code

```java
return repository.findById(id).orElseThrow();
```

### Expected diagnosis

The web serializer touches a lazy association after the persistence context is closed.

### Corrected code

```java
@Transactional
public OrderDto get(long id) { Order o = repository.findById(id).orElseThrow(); return OrderDto.from(o); }
```

### Regression tests

```java
// DTO serialization never triggers lazy loading.
```

## DATA-H-054: derived name means wrong predicate

- Difficulty: Hard
- Framework: Spring Data & Repositories
- Language: Java
- Perspective: Query methods
- Concept: derived name means wrong predicate
- Symptom: The repository returns unexpected rows.
- Diagnostic goal: Read the derived query name as a precise predicate.

### Buggy code

```java
List<User> findByNameOrEmailAndActive(String name, String email, boolean active);
```

### Expected diagnosis

Operator precedence may be parsed as name OR (email AND active), not (name OR email) AND active.

### Corrected code

```java
@Query("select u from User u where (u.name = :name or u.email = :email) and u.active = :active")
List<User> findActive(...);
```

### Regression tests

```java
// Inactive matches are never returned through either field.
```

## DATA-H-055: unbounded findAll

- Difficulty: Hard
- Framework: Spring Data & Repositories
- Language: Java
- Perspective: Pagination
- Concept: unbounded findAll
- Symptom: Memory and response time grow with table size.
- Diagnostic goal: Expose bounded page or slice queries.

### Buggy code

```java
List<Order> findByStatus(Status status);
```

### Expected diagnosis

Returning every matching entity has no upper bound.

### Corrected code

```java
Page<Order> findByStatus(Status status, Pageable pageable);
```

### Regression tests

```java
// A request with page size 50 never loads more than one page.
```

## DATA-H-056: stale persistence context

- Difficulty: Hard
- Framework: Spring Data & Repositories
- Language: Java
- Perspective: Bulk updates
- Concept: stale persistence context
- Symptom: A later read returns pre-update values.
- Diagnostic goal: Clear or refresh the persistence context after bulk DML.

### Buggy code

```java
@Modifying
@Query("update User u set u.active=false")
void deactivateAll();
```

### Expected diagnosis

Bulk JPQL bypasses managed entity state already held in the context.

### Corrected code

```java
@Modifying(clearAutomatically = true, flushAutomatically = true)
@Query("update User u set u.active=false")
void deactivateAll();
```

### Regression tests

```java
// The next repository read reflects the bulk update.
```

## DATA-H-057: equals null in JPQL

- Difficulty: Hard
- Framework: Spring Data & Repositories
- Language: Java
- Perspective: Null semantics
- Concept: equals null in JPQL
- Symptom: Rows with null values are not found.
- Diagnostic goal: Use IS NULL semantics or derived methods.

### Buggy code

```java
@Query("select x from Item x where x.note = null")
List<Item> missingNote();
```

### Expected diagnosis

SQL null is not equal to null; the predicate is never true.

### Corrected code

```java
@Query("select x from Item x where x.note is null")
List<Item> missingNote();
```

### Regression tests

```java
// Rows with a null note are returned.
```

## DATA-H-058: auditor not populated

- Difficulty: Hard
- Framework: Spring Data & Repositories
- Language: Java
- Perspective: Auditing
- Concept: auditor not populated
- Symptom: CreatedBy fields remain null.
- Diagnostic goal: Enable auditing and provide an authenticated auditor supplier.

### Buggy code

```java
class AuditConfig {}
```

### Expected diagnosis

The entity annotations alone do not activate Spring Data auditing.

### Corrected code

```java
@EnableJpaAuditing
@Configuration
class AuditConfig { @Bean AuditorAware<String> auditor() { return () -> Optional.of("system"); } }
```

### Regression tests

```java
// Save asserts createdBy is populated.
```

## DATA-H-059: lost update not detected

- Difficulty: Hard
- Framework: Spring Data & Repositories
- Language: Java
- Perspective: Optimistic locking
- Concept: lost update not detected
- Symptom: Last writer silently wins.
- Diagnostic goal: Add a version column and handle optimistic lock failures.

### Buggy code

```java
@Entity class Inventory { Long id; int quantity; }
```

### Expected diagnosis

Without @Version, stale writes are accepted.

### Corrected code

```java
@Version
private long version;
```

### Regression tests

```java
// Two updates from the same version cause one OptimisticLockException.
```

## DATA-H-060: repository test uses production schema

- Difficulty: Hard
- Framework: Spring Data & Repositories
- Language: Java
- Perspective: Test data
- Concept: repository test uses production schema
- Symptom: Tests are slow or modify shared data.
- Diagnostic goal: Use an isolated test database and rollback policy.

### Buggy code

```java
@SpringBootTest
class ItemRepositoryTest {}
```

### Expected diagnosis

A full context may load production datasource settings.

### Corrected code

```java
@DataJpaTest
@ActiveProfiles("test")
class ItemRepositoryTest {}
```

### Regression tests

```java
// The test uses an isolated database and rolls back each test.
```

## DATA-H-061: read-modify-write race

- Difficulty: Hard
- Framework: Spring Data & Repositories
- Language: Java
- Perspective: Transactions
- Concept: read-modify-write race
- Symptom: Concurrent updates lose changes.
- Diagnostic goal: Use a transaction and a locking or atomic update strategy.

### Buggy code

```java
entity.setCount(entity.getCount() + 1); repository.save(entity);
```

### Expected diagnosis

Separate requests can read the same old count and overwrite one another.

### Corrected code

```java
@Transactional
@Modifying
@Query("update Item i set i.count = i.count + 1 where i.id = :id")
void increment(long id);
```

### Regression tests

```java
// Concurrent increments equal the number of successful calls.
```

## DATA-H-062: lazy relation in loop

- Difficulty: Hard
- Framework: Spring Data & Repositories
- Language: Java
- Perspective: N+1 queries
- Concept: lazy relation in loop
- Symptom: A page triggers one query per row.
- Diagnostic goal: Fetch the relation with an explicit query plan.

### Buggy code

```java
orders.findAll().forEach(o -> o.getCustomer().getName());
```

### Expected diagnosis

Lazy access in a loop produces N additional selects.

### Corrected code

```java
@EntityGraph(attributePaths = "customer")
List<Order> findAll();
```

### Regression tests

```java
// SQL logging shows one query for the page and relation.
```

## DATA-H-063: session closed before serialization

- Difficulty: Hard
- Framework: Spring Data & Repositories
- Language: Java
- Perspective: Lazy loading
- Concept: session closed before serialization
- Symptom: JSON serialization throws LazyInitializationException.
- Diagnostic goal: Map entities to DTOs inside the transaction.

### Buggy code

```java
return repository.findById(id).orElseThrow();
```

### Expected diagnosis

The web serializer touches a lazy association after the persistence context is closed.

### Corrected code

```java
@Transactional
public OrderDto get(long id) { Order o = repository.findById(id).orElseThrow(); return OrderDto.from(o); }
```

### Regression tests

```java
// DTO serialization never triggers lazy loading.
```

## DATA-H-064: derived name means wrong predicate

- Difficulty: Hard
- Framework: Spring Data & Repositories
- Language: Java
- Perspective: Query methods
- Concept: derived name means wrong predicate
- Symptom: The repository returns unexpected rows.
- Diagnostic goal: Read the derived query name as a precise predicate.

### Buggy code

```java
List<User> findByNameOrEmailAndActive(String name, String email, boolean active);
```

### Expected diagnosis

Operator precedence may be parsed as name OR (email AND active), not (name OR email) AND active.

### Corrected code

```java
@Query("select u from User u where (u.name = :name or u.email = :email) and u.active = :active")
List<User> findActive(...);
```

### Regression tests

```java
// Inactive matches are never returned through either field.
```

## DATA-H-065: unbounded findAll

- Difficulty: Hard
- Framework: Spring Data & Repositories
- Language: Java
- Perspective: Pagination
- Concept: unbounded findAll
- Symptom: Memory and response time grow with table size.
- Diagnostic goal: Expose bounded page or slice queries.

### Buggy code

```java
List<Order> findByStatus(Status status);
```

### Expected diagnosis

Returning every matching entity has no upper bound.

### Corrected code

```java
Page<Order> findByStatus(Status status, Pageable pageable);
```

### Regression tests

```java
// A request with page size 50 never loads more than one page.
```

## DATA-H-066: stale persistence context

- Difficulty: Hard
- Framework: Spring Data & Repositories
- Language: Java
- Perspective: Bulk updates
- Concept: stale persistence context
- Symptom: A later read returns pre-update values.
- Diagnostic goal: Clear or refresh the persistence context after bulk DML.

### Buggy code

```java
@Modifying
@Query("update User u set u.active=false")
void deactivateAll();
```

### Expected diagnosis

Bulk JPQL bypasses managed entity state already held in the context.

### Corrected code

```java
@Modifying(clearAutomatically = true, flushAutomatically = true)
@Query("update User u set u.active=false")
void deactivateAll();
```

### Regression tests

```java
// The next repository read reflects the bulk update.
```

## DATA-H-067: equals null in JPQL

- Difficulty: Hard
- Framework: Spring Data & Repositories
- Language: Java
- Perspective: Null semantics
- Concept: equals null in JPQL
- Symptom: Rows with null values are not found.
- Diagnostic goal: Use IS NULL semantics or derived methods.

### Buggy code

```java
@Query("select x from Item x where x.note = null")
List<Item> missingNote();
```

### Expected diagnosis

SQL null is not equal to null; the predicate is never true.

### Corrected code

```java
@Query("select x from Item x where x.note is null")
List<Item> missingNote();
```

### Regression tests

```java
// Rows with a null note are returned.
```

## DATA-H-068: auditor not populated

- Difficulty: Hard
- Framework: Spring Data & Repositories
- Language: Java
- Perspective: Auditing
- Concept: auditor not populated
- Symptom: CreatedBy fields remain null.
- Diagnostic goal: Enable auditing and provide an authenticated auditor supplier.

### Buggy code

```java
class AuditConfig {}
```

### Expected diagnosis

The entity annotations alone do not activate Spring Data auditing.

### Corrected code

```java
@EnableJpaAuditing
@Configuration
class AuditConfig { @Bean AuditorAware<String> auditor() { return () -> Optional.of("system"); } }
```

### Regression tests

```java
// Save asserts createdBy is populated.
```

## DATA-H-069: lost update not detected

- Difficulty: Hard
- Framework: Spring Data & Repositories
- Language: Java
- Perspective: Optimistic locking
- Concept: lost update not detected
- Symptom: Last writer silently wins.
- Diagnostic goal: Add a version column and handle optimistic lock failures.

### Buggy code

```java
@Entity class Inventory { Long id; int quantity; }
```

### Expected diagnosis

Without @Version, stale writes are accepted.

### Corrected code

```java
@Version
private long version;
```

### Regression tests

```java
// Two updates from the same version cause one OptimisticLockException.
```

## DATA-H-070: repository test uses production schema

- Difficulty: Hard
- Framework: Spring Data & Repositories
- Language: Java
- Perspective: Test data
- Concept: repository test uses production schema
- Symptom: Tests are slow or modify shared data.
- Diagnostic goal: Use an isolated test database and rollback policy.

### Buggy code

```java
@SpringBootTest
class ItemRepositoryTest {}
```

### Expected diagnosis

A full context may load production datasource settings.

### Corrected code

```java
@DataJpaTest
@ActiveProfiles("test")
class ItemRepositoryTest {}
```

### Regression tests

```java
// The test uses an isolated database and rolls back each test.
```

## DATA-H-071: read-modify-write race

- Difficulty: Hard
- Framework: Spring Data & Repositories
- Language: Java
- Perspective: Transactions
- Concept: read-modify-write race
- Symptom: Concurrent updates lose changes.
- Diagnostic goal: Use a transaction and a locking or atomic update strategy.

### Buggy code

```java
entity.setCount(entity.getCount() + 1); repository.save(entity);
```

### Expected diagnosis

Separate requests can read the same old count and overwrite one another.

### Corrected code

```java
@Transactional
@Modifying
@Query("update Item i set i.count = i.count + 1 where i.id = :id")
void increment(long id);
```

### Regression tests

```java
// Concurrent increments equal the number of successful calls.
```

## DATA-H-072: lazy relation in loop

- Difficulty: Hard
- Framework: Spring Data & Repositories
- Language: Java
- Perspective: N+1 queries
- Concept: lazy relation in loop
- Symptom: A page triggers one query per row.
- Diagnostic goal: Fetch the relation with an explicit query plan.

### Buggy code

```java
orders.findAll().forEach(o -> o.getCustomer().getName());
```

### Expected diagnosis

Lazy access in a loop produces N additional selects.

### Corrected code

```java
@EntityGraph(attributePaths = "customer")
List<Order> findAll();
```

### Regression tests

```java
// SQL logging shows one query for the page and relation.
```

## DATA-H-073: session closed before serialization

- Difficulty: Hard
- Framework: Spring Data & Repositories
- Language: Java
- Perspective: Lazy loading
- Concept: session closed before serialization
- Symptom: JSON serialization throws LazyInitializationException.
- Diagnostic goal: Map entities to DTOs inside the transaction.

### Buggy code

```java
return repository.findById(id).orElseThrow();
```

### Expected diagnosis

The web serializer touches a lazy association after the persistence context is closed.

### Corrected code

```java
@Transactional
public OrderDto get(long id) { Order o = repository.findById(id).orElseThrow(); return OrderDto.from(o); }
```

### Regression tests

```java
// DTO serialization never triggers lazy loading.
```

## DATA-H-074: derived name means wrong predicate

- Difficulty: Hard
- Framework: Spring Data & Repositories
- Language: Java
- Perspective: Query methods
- Concept: derived name means wrong predicate
- Symptom: The repository returns unexpected rows.
- Diagnostic goal: Read the derived query name as a precise predicate.

### Buggy code

```java
List<User> findByNameOrEmailAndActive(String name, String email, boolean active);
```

### Expected diagnosis

Operator precedence may be parsed as name OR (email AND active), not (name OR email) AND active.

### Corrected code

```java
@Query("select u from User u where (u.name = :name or u.email = :email) and u.active = :active")
List<User> findActive(...);
```

### Regression tests

```java
// Inactive matches are never returned through either field.
```

## DATA-H-075: unbounded findAll

- Difficulty: Hard
- Framework: Spring Data & Repositories
- Language: Java
- Perspective: Pagination
- Concept: unbounded findAll
- Symptom: Memory and response time grow with table size.
- Diagnostic goal: Expose bounded page or slice queries.

### Buggy code

```java
List<Order> findByStatus(Status status);
```

### Expected diagnosis

Returning every matching entity has no upper bound.

### Corrected code

```java
Page<Order> findByStatus(Status status, Pageable pageable);
```

### Regression tests

```java
// A request with page size 50 never loads more than one page.
```

## DATA-H-076: stale persistence context

- Difficulty: Hard
- Framework: Spring Data & Repositories
- Language: Java
- Perspective: Bulk updates
- Concept: stale persistence context
- Symptom: A later read returns pre-update values.
- Diagnostic goal: Clear or refresh the persistence context after bulk DML.

### Buggy code

```java
@Modifying
@Query("update User u set u.active=false")
void deactivateAll();
```

### Expected diagnosis

Bulk JPQL bypasses managed entity state already held in the context.

### Corrected code

```java
@Modifying(clearAutomatically = true, flushAutomatically = true)
@Query("update User u set u.active=false")
void deactivateAll();
```

### Regression tests

```java
// The next repository read reflects the bulk update.
```

## DATA-H-077: equals null in JPQL

- Difficulty: Hard
- Framework: Spring Data & Repositories
- Language: Java
- Perspective: Null semantics
- Concept: equals null in JPQL
- Symptom: Rows with null values are not found.
- Diagnostic goal: Use IS NULL semantics or derived methods.

### Buggy code

```java
@Query("select x from Item x where x.note = null")
List<Item> missingNote();
```

### Expected diagnosis

SQL null is not equal to null; the predicate is never true.

### Corrected code

```java
@Query("select x from Item x where x.note is null")
List<Item> missingNote();
```

### Regression tests

```java
// Rows with a null note are returned.
```

## DATA-H-078: auditor not populated

- Difficulty: Hard
- Framework: Spring Data & Repositories
- Language: Java
- Perspective: Auditing
- Concept: auditor not populated
- Symptom: CreatedBy fields remain null.
- Diagnostic goal: Enable auditing and provide an authenticated auditor supplier.

### Buggy code

```java
class AuditConfig {}
```

### Expected diagnosis

The entity annotations alone do not activate Spring Data auditing.

### Corrected code

```java
@EnableJpaAuditing
@Configuration
class AuditConfig { @Bean AuditorAware<String> auditor() { return () -> Optional.of("system"); } }
```

### Regression tests

```java
// Save asserts createdBy is populated.
```

## DATA-H-079: lost update not detected

- Difficulty: Hard
- Framework: Spring Data & Repositories
- Language: Java
- Perspective: Optimistic locking
- Concept: lost update not detected
- Symptom: Last writer silently wins.
- Diagnostic goal: Add a version column and handle optimistic lock failures.

### Buggy code

```java
@Entity class Inventory { Long id; int quantity; }
```

### Expected diagnosis

Without @Version, stale writes are accepted.

### Corrected code

```java
@Version
private long version;
```

### Regression tests

```java
// Two updates from the same version cause one OptimisticLockException.
```

## DATA-H-080: repository test uses production schema

- Difficulty: Hard
- Framework: Spring Data & Repositories
- Language: Java
- Perspective: Test data
- Concept: repository test uses production schema
- Symptom: Tests are slow or modify shared data.
- Diagnostic goal: Use an isolated test database and rollback policy.

### Buggy code

```java
@SpringBootTest
class ItemRepositoryTest {}
```

### Expected diagnosis

A full context may load production datasource settings.

### Corrected code

```java
@DataJpaTest
@ActiveProfiles("test")
class ItemRepositoryTest {}
```

### Regression tests

```java
// The test uses an isolated database and rolls back each test.
```

## DATA-H-081: read-modify-write race

- Difficulty: Hard
- Framework: Spring Data & Repositories
- Language: Java
- Perspective: Transactions
- Concept: read-modify-write race
- Symptom: Concurrent updates lose changes.
- Diagnostic goal: Use a transaction and a locking or atomic update strategy.

### Buggy code

```java
entity.setCount(entity.getCount() + 1); repository.save(entity);
```

### Expected diagnosis

Separate requests can read the same old count and overwrite one another.

### Corrected code

```java
@Transactional
@Modifying
@Query("update Item i set i.count = i.count + 1 where i.id = :id")
void increment(long id);
```

### Regression tests

```java
// Concurrent increments equal the number of successful calls.
```

## DATA-H-082: lazy relation in loop

- Difficulty: Hard
- Framework: Spring Data & Repositories
- Language: Java
- Perspective: N+1 queries
- Concept: lazy relation in loop
- Symptom: A page triggers one query per row.
- Diagnostic goal: Fetch the relation with an explicit query plan.

### Buggy code

```java
orders.findAll().forEach(o -> o.getCustomer().getName());
```

### Expected diagnosis

Lazy access in a loop produces N additional selects.

### Corrected code

```java
@EntityGraph(attributePaths = "customer")
List<Order> findAll();
```

### Regression tests

```java
// SQL logging shows one query for the page and relation.
```

## DATA-H-083: session closed before serialization

- Difficulty: Hard
- Framework: Spring Data & Repositories
- Language: Java
- Perspective: Lazy loading
- Concept: session closed before serialization
- Symptom: JSON serialization throws LazyInitializationException.
- Diagnostic goal: Map entities to DTOs inside the transaction.

### Buggy code

```java
return repository.findById(id).orElseThrow();
```

### Expected diagnosis

The web serializer touches a lazy association after the persistence context is closed.

### Corrected code

```java
@Transactional
public OrderDto get(long id) { Order o = repository.findById(id).orElseThrow(); return OrderDto.from(o); }
```

### Regression tests

```java
// DTO serialization never triggers lazy loading.
```

## DATA-H-084: derived name means wrong predicate

- Difficulty: Hard
- Framework: Spring Data & Repositories
- Language: Java
- Perspective: Query methods
- Concept: derived name means wrong predicate
- Symptom: The repository returns unexpected rows.
- Diagnostic goal: Read the derived query name as a precise predicate.

### Buggy code

```java
List<User> findByNameOrEmailAndActive(String name, String email, boolean active);
```

### Expected diagnosis

Operator precedence may be parsed as name OR (email AND active), not (name OR email) AND active.

### Corrected code

```java
@Query("select u from User u where (u.name = :name or u.email = :email) and u.active = :active")
List<User> findActive(...);
```

### Regression tests

```java
// Inactive matches are never returned through either field.
```

## DATA-H-085: unbounded findAll

- Difficulty: Hard
- Framework: Spring Data & Repositories
- Language: Java
- Perspective: Pagination
- Concept: unbounded findAll
- Symptom: Memory and response time grow with table size.
- Diagnostic goal: Expose bounded page or slice queries.

### Buggy code

```java
List<Order> findByStatus(Status status);
```

### Expected diagnosis

Returning every matching entity has no upper bound.

### Corrected code

```java
Page<Order> findByStatus(Status status, Pageable pageable);
```

### Regression tests

```java
// A request with page size 50 never loads more than one page.
```

## DATA-H-086: stale persistence context

- Difficulty: Hard
- Framework: Spring Data & Repositories
- Language: Java
- Perspective: Bulk updates
- Concept: stale persistence context
- Symptom: A later read returns pre-update values.
- Diagnostic goal: Clear or refresh the persistence context after bulk DML.

### Buggy code

```java
@Modifying
@Query("update User u set u.active=false")
void deactivateAll();
```

### Expected diagnosis

Bulk JPQL bypasses managed entity state already held in the context.

### Corrected code

```java
@Modifying(clearAutomatically = true, flushAutomatically = true)
@Query("update User u set u.active=false")
void deactivateAll();
```

### Regression tests

```java
// The next repository read reflects the bulk update.
```

## DATA-H-087: equals null in JPQL

- Difficulty: Hard
- Framework: Spring Data & Repositories
- Language: Java
- Perspective: Null semantics
- Concept: equals null in JPQL
- Symptom: Rows with null values are not found.
- Diagnostic goal: Use IS NULL semantics or derived methods.

### Buggy code

```java
@Query("select x from Item x where x.note = null")
List<Item> missingNote();
```

### Expected diagnosis

SQL null is not equal to null; the predicate is never true.

### Corrected code

```java
@Query("select x from Item x where x.note is null")
List<Item> missingNote();
```

### Regression tests

```java
// Rows with a null note are returned.
```

## DATA-H-088: auditor not populated

- Difficulty: Hard
- Framework: Spring Data & Repositories
- Language: Java
- Perspective: Auditing
- Concept: auditor not populated
- Symptom: CreatedBy fields remain null.
- Diagnostic goal: Enable auditing and provide an authenticated auditor supplier.

### Buggy code

```java
class AuditConfig {}
```

### Expected diagnosis

The entity annotations alone do not activate Spring Data auditing.

### Corrected code

```java
@EnableJpaAuditing
@Configuration
class AuditConfig { @Bean AuditorAware<String> auditor() { return () -> Optional.of("system"); } }
```

### Regression tests

```java
// Save asserts createdBy is populated.
```

## DATA-H-089: lost update not detected

- Difficulty: Hard
- Framework: Spring Data & Repositories
- Language: Java
- Perspective: Optimistic locking
- Concept: lost update not detected
- Symptom: Last writer silently wins.
- Diagnostic goal: Add a version column and handle optimistic lock failures.

### Buggy code

```java
@Entity class Inventory { Long id; int quantity; }
```

### Expected diagnosis

Without @Version, stale writes are accepted.

### Corrected code

```java
@Version
private long version;
```

### Regression tests

```java
// Two updates from the same version cause one OptimisticLockException.
```

## DATA-H-090: repository test uses production schema

- Difficulty: Hard
- Framework: Spring Data & Repositories
- Language: Java
- Perspective: Test data
- Concept: repository test uses production schema
- Symptom: Tests are slow or modify shared data.
- Diagnostic goal: Use an isolated test database and rollback policy.

### Buggy code

```java
@SpringBootTest
class ItemRepositoryTest {}
```

### Expected diagnosis

A full context may load production datasource settings.

### Corrected code

```java
@DataJpaTest
@ActiveProfiles("test")
class ItemRepositoryTest {}
```

### Regression tests

```java
// The test uses an isolated database and rolls back each test.
```

## DATA-H-091: read-modify-write race

- Difficulty: Hard
- Framework: Spring Data & Repositories
- Language: Java
- Perspective: Transactions
- Concept: read-modify-write race
- Symptom: Concurrent updates lose changes.
- Diagnostic goal: Use a transaction and a locking or atomic update strategy.

### Buggy code

```java
entity.setCount(entity.getCount() + 1); repository.save(entity);
```

### Expected diagnosis

Separate requests can read the same old count and overwrite one another.

### Corrected code

```java
@Transactional
@Modifying
@Query("update Item i set i.count = i.count + 1 where i.id = :id")
void increment(long id);
```

### Regression tests

```java
// Concurrent increments equal the number of successful calls.
```

## DATA-H-092: lazy relation in loop

- Difficulty: Hard
- Framework: Spring Data & Repositories
- Language: Java
- Perspective: N+1 queries
- Concept: lazy relation in loop
- Symptom: A page triggers one query per row.
- Diagnostic goal: Fetch the relation with an explicit query plan.

### Buggy code

```java
orders.findAll().forEach(o -> o.getCustomer().getName());
```

### Expected diagnosis

Lazy access in a loop produces N additional selects.

### Corrected code

```java
@EntityGraph(attributePaths = "customer")
List<Order> findAll();
```

### Regression tests

```java
// SQL logging shows one query for the page and relation.
```

## DATA-H-093: session closed before serialization

- Difficulty: Hard
- Framework: Spring Data & Repositories
- Language: Java
- Perspective: Lazy loading
- Concept: session closed before serialization
- Symptom: JSON serialization throws LazyInitializationException.
- Diagnostic goal: Map entities to DTOs inside the transaction.

### Buggy code

```java
return repository.findById(id).orElseThrow();
```

### Expected diagnosis

The web serializer touches a lazy association after the persistence context is closed.

### Corrected code

```java
@Transactional
public OrderDto get(long id) { Order o = repository.findById(id).orElseThrow(); return OrderDto.from(o); }
```

### Regression tests

```java
// DTO serialization never triggers lazy loading.
```

## DATA-H-094: derived name means wrong predicate

- Difficulty: Hard
- Framework: Spring Data & Repositories
- Language: Java
- Perspective: Query methods
- Concept: derived name means wrong predicate
- Symptom: The repository returns unexpected rows.
- Diagnostic goal: Read the derived query name as a precise predicate.

### Buggy code

```java
List<User> findByNameOrEmailAndActive(String name, String email, boolean active);
```

### Expected diagnosis

Operator precedence may be parsed as name OR (email AND active), not (name OR email) AND active.

### Corrected code

```java
@Query("select u from User u where (u.name = :name or u.email = :email) and u.active = :active")
List<User> findActive(...);
```

### Regression tests

```java
// Inactive matches are never returned through either field.
```

## DATA-H-095: unbounded findAll

- Difficulty: Hard
- Framework: Spring Data & Repositories
- Language: Java
- Perspective: Pagination
- Concept: unbounded findAll
- Symptom: Memory and response time grow with table size.
- Diagnostic goal: Expose bounded page or slice queries.

### Buggy code

```java
List<Order> findByStatus(Status status);
```

### Expected diagnosis

Returning every matching entity has no upper bound.

### Corrected code

```java
Page<Order> findByStatus(Status status, Pageable pageable);
```

### Regression tests

```java
// A request with page size 50 never loads more than one page.
```

## DATA-H-096: stale persistence context

- Difficulty: Hard
- Framework: Spring Data & Repositories
- Language: Java
- Perspective: Bulk updates
- Concept: stale persistence context
- Symptom: A later read returns pre-update values.
- Diagnostic goal: Clear or refresh the persistence context after bulk DML.

### Buggy code

```java
@Modifying
@Query("update User u set u.active=false")
void deactivateAll();
```

### Expected diagnosis

Bulk JPQL bypasses managed entity state already held in the context.

### Corrected code

```java
@Modifying(clearAutomatically = true, flushAutomatically = true)
@Query("update User u set u.active=false")
void deactivateAll();
```

### Regression tests

```java
// The next repository read reflects the bulk update.
```

## DATA-H-097: equals null in JPQL

- Difficulty: Hard
- Framework: Spring Data & Repositories
- Language: Java
- Perspective: Null semantics
- Concept: equals null in JPQL
- Symptom: Rows with null values are not found.
- Diagnostic goal: Use IS NULL semantics or derived methods.

### Buggy code

```java
@Query("select x from Item x where x.note = null")
List<Item> missingNote();
```

### Expected diagnosis

SQL null is not equal to null; the predicate is never true.

### Corrected code

```java
@Query("select x from Item x where x.note is null")
List<Item> missingNote();
```

### Regression tests

```java
// Rows with a null note are returned.
```

## DATA-H-098: auditor not populated

- Difficulty: Hard
- Framework: Spring Data & Repositories
- Language: Java
- Perspective: Auditing
- Concept: auditor not populated
- Symptom: CreatedBy fields remain null.
- Diagnostic goal: Enable auditing and provide an authenticated auditor supplier.

### Buggy code

```java
class AuditConfig {}
```

### Expected diagnosis

The entity annotations alone do not activate Spring Data auditing.

### Corrected code

```java
@EnableJpaAuditing
@Configuration
class AuditConfig { @Bean AuditorAware<String> auditor() { return () -> Optional.of("system"); } }
```

### Regression tests

```java
// Save asserts createdBy is populated.
```

## DATA-H-099: lost update not detected

- Difficulty: Hard
- Framework: Spring Data & Repositories
- Language: Java
- Perspective: Optimistic locking
- Concept: lost update not detected
- Symptom: Last writer silently wins.
- Diagnostic goal: Add a version column and handle optimistic lock failures.

### Buggy code

```java
@Entity class Inventory { Long id; int quantity; }
```

### Expected diagnosis

Without @Version, stale writes are accepted.

### Corrected code

```java
@Version
private long version;
```

### Regression tests

```java
// Two updates from the same version cause one OptimisticLockException.
```

## DATA-H-100: repository test uses production schema

- Difficulty: Hard
- Framework: Spring Data & Repositories
- Language: Java
- Perspective: Test data
- Concept: repository test uses production schema
- Symptom: Tests are slow or modify shared data.
- Diagnostic goal: Use an isolated test database and rollback policy.

### Buggy code

```java
@SpringBootTest
class ItemRepositoryTest {}
```

### Expected diagnosis

A full context may load production datasource settings.

### Corrected code

```java
@DataJpaTest
@ActiveProfiles("test")
class ItemRepositoryTest {}
```

### Regression tests

```java
// The test uses an isolated database and rolls back each test.
```
