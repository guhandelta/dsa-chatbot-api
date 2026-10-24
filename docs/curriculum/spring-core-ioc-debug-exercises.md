# Spring Core & Inversion of Control Debug Exercises

A RAG-training corpus of 300 debugging exercises for Spring Core & Inversion of Control. Each record contains framework-specific metadata, a failure example, an editorial diagnosis, corrected Java/Spring code, and regression guidance. Corrected code is training material and must be stripped from learner-facing challenge responses.

## Coverage

- Easy: 100 exercises
- Medium: 100 exercises
- Hard: 100 exercises
- Perspectives: configuration, lifecycle, proxies, persistence, HTTP contracts, security, testing, transactions, observability, and deployment

## IOC-E-001: prototype injected into singleton

- Difficulty: Easy
- Framework: Spring Core & Inversion of Control
- Language: Java
- Perspective: Bean lifecycle
- Concept: prototype injected into singleton
- Symptom: A supposed new object is reused.
- Diagnostic goal: Obtain shorter-lived beans through a provider or scoped proxy.

### Buggy code

```java
@Component
class JobRunner { private final Job job; JobRunner(Job job) { this.job = job; } }
```

### Expected diagnosis

A prototype dependency is resolved once when the singleton is constructed.

### Corrected code

```java
@Component
class JobRunner { private final ObjectProvider<Job> jobs; JobRunner(ObjectProvider<Job> jobs) { this.jobs = jobs; }
 Job next() { return jobs.getObject(); } }
```

### Regression tests

```java
// Two calls to next return distinct Job instances.
```

## IOC-E-002: multiple candidates ambiguous

- Difficulty: Easy
- Framework: Spring Core & Inversion of Control
- Language: Java
- Perspective: Injection
- Concept: multiple candidates ambiguous
- Symptom: Context startup reports NoUniqueBeanDefinitionException.
- Diagnostic goal: Qualify the intended implementation or define a primary bean.

### Buggy code

```java
@Bean PaymentGateway stripe() { return new StripeGateway(); }
@Bean PaymentGateway bank() { return new BankGateway(); }
@Service Checkout(PaymentGateway gateway) {}
```

### Expected diagnosis

The injection point has two candidates and no selection rule.

### Corrected code

```java
@Service Checkout(@Qualifier("stripe") PaymentGateway gateway) {}
```

### Regression tests

```java
// Context chooses Stripe only at the qualified injection point.
```

## IOC-E-003: self-invocation bypasses advice

- Difficulty: Easy
- Framework: Spring Core & Inversion of Control
- Language: Java
- Perspective: Proxying
- Concept: self-invocation bypasses advice
- Symptom: The transactional or cached annotation appears ignored.
- Diagnostic goal: Call the advised method through the proxy boundary.

### Buggy code

```java
@Transactional
public void outer() { inner(); }
@Transactional
public void inner() { /* work */ }
```

### Expected diagnosis

A direct this.inner() call never passes through the Spring proxy.

### Corrected code

```java
@Transactional
public void outer() { collaborator.inner(); }
```

### Regression tests

```java
// An integration test observes the transaction/caching advice on inner.
```

## IOC-E-004: request bean used outside request

- Difficulty: Easy
- Framework: Spring Core & Inversion of Control
- Language: Java
- Perspective: Scopes
- Concept: request bean used outside request
- Symptom: A background task throws scope-not-active.
- Diagnostic goal: Capture immutable data, not a request-scoped object, for background work.

### Buggy code

```java
executor.submit(() -> requestContext.getUserId());
```

### Expected diagnosis

The request scope may be gone when the task runs.

### Corrected code

```java
String userId = requestContext.getUserId();
executor.submit(() -> process(userId));
```

### Regression tests

```java
// The task remains valid after the request completes.
```

## IOC-E-005: event published before commit

- Difficulty: Easy
- Framework: Spring Core & Inversion of Control
- Language: Java
- Perspective: Events
- Concept: event published before commit
- Symptom: A listener sees data that later rolls back.
- Diagnostic goal: Publish after a successful transaction commit when required.

### Buggy code

```java
publisher.publishEvent(new OrderCreated(order.id()));
repository.save(order);
```

### Expected diagnosis

The event is emitted before persistence commits and may describe a transaction that fails.

### Corrected code

```java
repository.save(order);
publisher.publishEvent(new OrderCreated(order.id()));
```

### Regression tests

```java
// A transactional listener receives the event only after commit.
```

## IOC-E-006: conditional bean unexpectedly absent

- Difficulty: Easy
- Framework: Spring Core & Inversion of Control
- Language: Java
- Perspective: Factory
- Concept: conditional bean unexpectedly absent
- Symptom: A feature flag has no implementation.
- Diagnostic goal: Check condition names and the effective environment.

### Buggy code

```java
@ConditionalOnProperty(name = "feature.mail")
@Bean Mailer mailer() { return new Mailer(); }
```

### Expected diagnosis

The condition requires a value unless havingValue or matchIfMissing is configured as intended.

### Corrected code

```java
@ConditionalOnProperty(name = "feature.mail", havingValue = "true")
@Bean Mailer mailer() { return new Mailer(); }
```

### Regression tests

```java
// Context reports a bean only when feature.mail=true.
```

## IOC-E-007: close omitted

- Difficulty: Easy
- Framework: Spring Core & Inversion of Control
- Language: Java
- Perspective: Resource lifecycle
- Concept: close omitted
- Symptom: Threads or connections remain after context shutdown.
- Diagnostic goal: Register resources as managed beans with destruction callbacks.

### Buggy code

```java
@Bean ExecutorService executor() { return Executors.newFixedThreadPool(4); }
```

### Expected diagnosis

The container does not know how to stop an arbitrary resource unless destruction is declared.

### Corrected code

```java
@Bean(destroyMethod = "shutdown") ExecutorService executor() { return Executors.newFixedThreadPool(4); }
```

### Regression tests

```java
// Context close invokes shutdown.
```

## IOC-E-008: listener order assumed

- Difficulty: Easy
- Framework: Spring Core & Inversion of Control
- Language: Java
- Perspective: Ordering
- Concept: listener order assumed
- Symptom: Two startup tasks run in the wrong order.
- Diagnostic goal: Declare ordering only where the dependency is real.

### Buggy code

```java
@EventListener
void seed() {}
@EventListener
void publish() {}
```

### Expected diagnosis

Listener registration order is not a reliable dependency contract.

### Corrected code

```java
@Order(1) @EventListener void seed() {}
@Order(2) @EventListener void publish() {}
```

### Regression tests

```java
// The test records seed before publish.
```

## IOC-E-009: optional bean treated as required

- Difficulty: Easy
- Framework: Spring Core & Inversion of Control
- Language: Java
- Perspective: Optional dependencies
- Concept: optional bean treated as required
- Symptom: A feature cannot start without an optional integration.
- Diagnostic goal: Represent optionality explicitly.

### Buggy code

```java
public Reporter(Exporter exporter) { this.exporter = exporter; }
```

### Expected diagnosis

Constructor injection requires Exporter even when the feature is disabled.

### Corrected code

```java
public Reporter(ObjectProvider<Exporter> exporter) { this.exporter = exporter; }
```

### Regression tests

```java
// Reporter starts without Exporter and uses a no-op path.
```

## IOC-E-010: service cycle hidden by field injection

- Difficulty: Easy
- Framework: Spring Core & Inversion of Control
- Language: Java
- Perspective: Circular design
- Concept: service cycle hidden by field injection
- Symptom: Runtime behavior is order-dependent and difficult to test.
- Diagnostic goal: Extract a port or move orchestration into a third component.

### Buggy code

```java
@Autowired A a;
class A { @Autowired B b; }
class B { @Autowired A a; }
```

### Expected diagnosis

Field injection hides the cycle until context creation and makes dependencies mutable.

### Corrected code

```java
class Orchestrator { Orchestrator(A a, B b) {} }
```

### Regression tests

```java
// A and B no longer depend directly on one another.
```

## IOC-E-011: prototype injected into singleton

- Difficulty: Easy
- Framework: Spring Core & Inversion of Control
- Language: Java
- Perspective: Bean lifecycle
- Concept: prototype injected into singleton
- Symptom: A supposed new object is reused.
- Diagnostic goal: Obtain shorter-lived beans through a provider or scoped proxy.

### Buggy code

```java
@Component
class JobRunner { private final Job job; JobRunner(Job job) { this.job = job; } }
```

### Expected diagnosis

A prototype dependency is resolved once when the singleton is constructed.

### Corrected code

```java
@Component
class JobRunner { private final ObjectProvider<Job> jobs; JobRunner(ObjectProvider<Job> jobs) { this.jobs = jobs; }
 Job next() { return jobs.getObject(); } }
```

### Regression tests

```java
// Two calls to next return distinct Job instances.
```

## IOC-E-012: multiple candidates ambiguous

- Difficulty: Easy
- Framework: Spring Core & Inversion of Control
- Language: Java
- Perspective: Injection
- Concept: multiple candidates ambiguous
- Symptom: Context startup reports NoUniqueBeanDefinitionException.
- Diagnostic goal: Qualify the intended implementation or define a primary bean.

### Buggy code

```java
@Bean PaymentGateway stripe() { return new StripeGateway(); }
@Bean PaymentGateway bank() { return new BankGateway(); }
@Service Checkout(PaymentGateway gateway) {}
```

### Expected diagnosis

The injection point has two candidates and no selection rule.

### Corrected code

```java
@Service Checkout(@Qualifier("stripe") PaymentGateway gateway) {}
```

### Regression tests

```java
// Context chooses Stripe only at the qualified injection point.
```

## IOC-E-013: self-invocation bypasses advice

- Difficulty: Easy
- Framework: Spring Core & Inversion of Control
- Language: Java
- Perspective: Proxying
- Concept: self-invocation bypasses advice
- Symptom: The transactional or cached annotation appears ignored.
- Diagnostic goal: Call the advised method through the proxy boundary.

### Buggy code

```java
@Transactional
public void outer() { inner(); }
@Transactional
public void inner() { /* work */ }
```

### Expected diagnosis

A direct this.inner() call never passes through the Spring proxy.

### Corrected code

```java
@Transactional
public void outer() { collaborator.inner(); }
```

### Regression tests

```java
// An integration test observes the transaction/caching advice on inner.
```

## IOC-E-014: request bean used outside request

- Difficulty: Easy
- Framework: Spring Core & Inversion of Control
- Language: Java
- Perspective: Scopes
- Concept: request bean used outside request
- Symptom: A background task throws scope-not-active.
- Diagnostic goal: Capture immutable data, not a request-scoped object, for background work.

### Buggy code

```java
executor.submit(() -> requestContext.getUserId());
```

### Expected diagnosis

The request scope may be gone when the task runs.

### Corrected code

```java
String userId = requestContext.getUserId();
executor.submit(() -> process(userId));
```

### Regression tests

```java
// The task remains valid after the request completes.
```

## IOC-E-015: event published before commit

- Difficulty: Easy
- Framework: Spring Core & Inversion of Control
- Language: Java
- Perspective: Events
- Concept: event published before commit
- Symptom: A listener sees data that later rolls back.
- Diagnostic goal: Publish after a successful transaction commit when required.

### Buggy code

```java
publisher.publishEvent(new OrderCreated(order.id()));
repository.save(order);
```

### Expected diagnosis

The event is emitted before persistence commits and may describe a transaction that fails.

### Corrected code

```java
repository.save(order);
publisher.publishEvent(new OrderCreated(order.id()));
```

### Regression tests

```java
// A transactional listener receives the event only after commit.
```

## IOC-E-016: conditional bean unexpectedly absent

- Difficulty: Easy
- Framework: Spring Core & Inversion of Control
- Language: Java
- Perspective: Factory
- Concept: conditional bean unexpectedly absent
- Symptom: A feature flag has no implementation.
- Diagnostic goal: Check condition names and the effective environment.

### Buggy code

```java
@ConditionalOnProperty(name = "feature.mail")
@Bean Mailer mailer() { return new Mailer(); }
```

### Expected diagnosis

The condition requires a value unless havingValue or matchIfMissing is configured as intended.

### Corrected code

```java
@ConditionalOnProperty(name = "feature.mail", havingValue = "true")
@Bean Mailer mailer() { return new Mailer(); }
```

### Regression tests

```java
// Context reports a bean only when feature.mail=true.
```

## IOC-E-017: close omitted

- Difficulty: Easy
- Framework: Spring Core & Inversion of Control
- Language: Java
- Perspective: Resource lifecycle
- Concept: close omitted
- Symptom: Threads or connections remain after context shutdown.
- Diagnostic goal: Register resources as managed beans with destruction callbacks.

### Buggy code

```java
@Bean ExecutorService executor() { return Executors.newFixedThreadPool(4); }
```

### Expected diagnosis

The container does not know how to stop an arbitrary resource unless destruction is declared.

### Corrected code

```java
@Bean(destroyMethod = "shutdown") ExecutorService executor() { return Executors.newFixedThreadPool(4); }
```

### Regression tests

```java
// Context close invokes shutdown.
```

## IOC-E-018: listener order assumed

- Difficulty: Easy
- Framework: Spring Core & Inversion of Control
- Language: Java
- Perspective: Ordering
- Concept: listener order assumed
- Symptom: Two startup tasks run in the wrong order.
- Diagnostic goal: Declare ordering only where the dependency is real.

### Buggy code

```java
@EventListener
void seed() {}
@EventListener
void publish() {}
```

### Expected diagnosis

Listener registration order is not a reliable dependency contract.

### Corrected code

```java
@Order(1) @EventListener void seed() {}
@Order(2) @EventListener void publish() {}
```

### Regression tests

```java
// The test records seed before publish.
```

## IOC-E-019: optional bean treated as required

- Difficulty: Easy
- Framework: Spring Core & Inversion of Control
- Language: Java
- Perspective: Optional dependencies
- Concept: optional bean treated as required
- Symptom: A feature cannot start without an optional integration.
- Diagnostic goal: Represent optionality explicitly.

### Buggy code

```java
public Reporter(Exporter exporter) { this.exporter = exporter; }
```

### Expected diagnosis

Constructor injection requires Exporter even when the feature is disabled.

### Corrected code

```java
public Reporter(ObjectProvider<Exporter> exporter) { this.exporter = exporter; }
```

### Regression tests

```java
// Reporter starts without Exporter and uses a no-op path.
```

## IOC-E-020: service cycle hidden by field injection

- Difficulty: Easy
- Framework: Spring Core & Inversion of Control
- Language: Java
- Perspective: Circular design
- Concept: service cycle hidden by field injection
- Symptom: Runtime behavior is order-dependent and difficult to test.
- Diagnostic goal: Extract a port or move orchestration into a third component.

### Buggy code

```java
@Autowired A a;
class A { @Autowired B b; }
class B { @Autowired A a; }
```

### Expected diagnosis

Field injection hides the cycle until context creation and makes dependencies mutable.

### Corrected code

```java
class Orchestrator { Orchestrator(A a, B b) {} }
```

### Regression tests

```java
// A and B no longer depend directly on one another.
```

## IOC-E-021: prototype injected into singleton

- Difficulty: Easy
- Framework: Spring Core & Inversion of Control
- Language: Java
- Perspective: Bean lifecycle
- Concept: prototype injected into singleton
- Symptom: A supposed new object is reused.
- Diagnostic goal: Obtain shorter-lived beans through a provider or scoped proxy.

### Buggy code

```java
@Component
class JobRunner { private final Job job; JobRunner(Job job) { this.job = job; } }
```

### Expected diagnosis

A prototype dependency is resolved once when the singleton is constructed.

### Corrected code

```java
@Component
class JobRunner { private final ObjectProvider<Job> jobs; JobRunner(ObjectProvider<Job> jobs) { this.jobs = jobs; }
 Job next() { return jobs.getObject(); } }
```

### Regression tests

```java
// Two calls to next return distinct Job instances.
```

## IOC-E-022: multiple candidates ambiguous

- Difficulty: Easy
- Framework: Spring Core & Inversion of Control
- Language: Java
- Perspective: Injection
- Concept: multiple candidates ambiguous
- Symptom: Context startup reports NoUniqueBeanDefinitionException.
- Diagnostic goal: Qualify the intended implementation or define a primary bean.

### Buggy code

```java
@Bean PaymentGateway stripe() { return new StripeGateway(); }
@Bean PaymentGateway bank() { return new BankGateway(); }
@Service Checkout(PaymentGateway gateway) {}
```

### Expected diagnosis

The injection point has two candidates and no selection rule.

### Corrected code

```java
@Service Checkout(@Qualifier("stripe") PaymentGateway gateway) {}
```

### Regression tests

```java
// Context chooses Stripe only at the qualified injection point.
```

## IOC-E-023: self-invocation bypasses advice

- Difficulty: Easy
- Framework: Spring Core & Inversion of Control
- Language: Java
- Perspective: Proxying
- Concept: self-invocation bypasses advice
- Symptom: The transactional or cached annotation appears ignored.
- Diagnostic goal: Call the advised method through the proxy boundary.

### Buggy code

```java
@Transactional
public void outer() { inner(); }
@Transactional
public void inner() { /* work */ }
```

### Expected diagnosis

A direct this.inner() call never passes through the Spring proxy.

### Corrected code

```java
@Transactional
public void outer() { collaborator.inner(); }
```

### Regression tests

```java
// An integration test observes the transaction/caching advice on inner.
```

## IOC-E-024: request bean used outside request

- Difficulty: Easy
- Framework: Spring Core & Inversion of Control
- Language: Java
- Perspective: Scopes
- Concept: request bean used outside request
- Symptom: A background task throws scope-not-active.
- Diagnostic goal: Capture immutable data, not a request-scoped object, for background work.

### Buggy code

```java
executor.submit(() -> requestContext.getUserId());
```

### Expected diagnosis

The request scope may be gone when the task runs.

### Corrected code

```java
String userId = requestContext.getUserId();
executor.submit(() -> process(userId));
```

### Regression tests

```java
// The task remains valid after the request completes.
```

## IOC-E-025: event published before commit

- Difficulty: Easy
- Framework: Spring Core & Inversion of Control
- Language: Java
- Perspective: Events
- Concept: event published before commit
- Symptom: A listener sees data that later rolls back.
- Diagnostic goal: Publish after a successful transaction commit when required.

### Buggy code

```java
publisher.publishEvent(new OrderCreated(order.id()));
repository.save(order);
```

### Expected diagnosis

The event is emitted before persistence commits and may describe a transaction that fails.

### Corrected code

```java
repository.save(order);
publisher.publishEvent(new OrderCreated(order.id()));
```

### Regression tests

```java
// A transactional listener receives the event only after commit.
```

## IOC-E-026: conditional bean unexpectedly absent

- Difficulty: Easy
- Framework: Spring Core & Inversion of Control
- Language: Java
- Perspective: Factory
- Concept: conditional bean unexpectedly absent
- Symptom: A feature flag has no implementation.
- Diagnostic goal: Check condition names and the effective environment.

### Buggy code

```java
@ConditionalOnProperty(name = "feature.mail")
@Bean Mailer mailer() { return new Mailer(); }
```

### Expected diagnosis

The condition requires a value unless havingValue or matchIfMissing is configured as intended.

### Corrected code

```java
@ConditionalOnProperty(name = "feature.mail", havingValue = "true")
@Bean Mailer mailer() { return new Mailer(); }
```

### Regression tests

```java
// Context reports a bean only when feature.mail=true.
```

## IOC-E-027: close omitted

- Difficulty: Easy
- Framework: Spring Core & Inversion of Control
- Language: Java
- Perspective: Resource lifecycle
- Concept: close omitted
- Symptom: Threads or connections remain after context shutdown.
- Diagnostic goal: Register resources as managed beans with destruction callbacks.

### Buggy code

```java
@Bean ExecutorService executor() { return Executors.newFixedThreadPool(4); }
```

### Expected diagnosis

The container does not know how to stop an arbitrary resource unless destruction is declared.

### Corrected code

```java
@Bean(destroyMethod = "shutdown") ExecutorService executor() { return Executors.newFixedThreadPool(4); }
```

### Regression tests

```java
// Context close invokes shutdown.
```

## IOC-E-028: listener order assumed

- Difficulty: Easy
- Framework: Spring Core & Inversion of Control
- Language: Java
- Perspective: Ordering
- Concept: listener order assumed
- Symptom: Two startup tasks run in the wrong order.
- Diagnostic goal: Declare ordering only where the dependency is real.

### Buggy code

```java
@EventListener
void seed() {}
@EventListener
void publish() {}
```

### Expected diagnosis

Listener registration order is not a reliable dependency contract.

### Corrected code

```java
@Order(1) @EventListener void seed() {}
@Order(2) @EventListener void publish() {}
```

### Regression tests

```java
// The test records seed before publish.
```

## IOC-E-029: optional bean treated as required

- Difficulty: Easy
- Framework: Spring Core & Inversion of Control
- Language: Java
- Perspective: Optional dependencies
- Concept: optional bean treated as required
- Symptom: A feature cannot start without an optional integration.
- Diagnostic goal: Represent optionality explicitly.

### Buggy code

```java
public Reporter(Exporter exporter) { this.exporter = exporter; }
```

### Expected diagnosis

Constructor injection requires Exporter even when the feature is disabled.

### Corrected code

```java
public Reporter(ObjectProvider<Exporter> exporter) { this.exporter = exporter; }
```

### Regression tests

```java
// Reporter starts without Exporter and uses a no-op path.
```

## IOC-E-030: service cycle hidden by field injection

- Difficulty: Easy
- Framework: Spring Core & Inversion of Control
- Language: Java
- Perspective: Circular design
- Concept: service cycle hidden by field injection
- Symptom: Runtime behavior is order-dependent and difficult to test.
- Diagnostic goal: Extract a port or move orchestration into a third component.

### Buggy code

```java
@Autowired A a;
class A { @Autowired B b; }
class B { @Autowired A a; }
```

### Expected diagnosis

Field injection hides the cycle until context creation and makes dependencies mutable.

### Corrected code

```java
class Orchestrator { Orchestrator(A a, B b) {} }
```

### Regression tests

```java
// A and B no longer depend directly on one another.
```

## IOC-E-031: prototype injected into singleton

- Difficulty: Easy
- Framework: Spring Core & Inversion of Control
- Language: Java
- Perspective: Bean lifecycle
- Concept: prototype injected into singleton
- Symptom: A supposed new object is reused.
- Diagnostic goal: Obtain shorter-lived beans through a provider or scoped proxy.

### Buggy code

```java
@Component
class JobRunner { private final Job job; JobRunner(Job job) { this.job = job; } }
```

### Expected diagnosis

A prototype dependency is resolved once when the singleton is constructed.

### Corrected code

```java
@Component
class JobRunner { private final ObjectProvider<Job> jobs; JobRunner(ObjectProvider<Job> jobs) { this.jobs = jobs; }
 Job next() { return jobs.getObject(); } }
```

### Regression tests

```java
// Two calls to next return distinct Job instances.
```

## IOC-E-032: multiple candidates ambiguous

- Difficulty: Easy
- Framework: Spring Core & Inversion of Control
- Language: Java
- Perspective: Injection
- Concept: multiple candidates ambiguous
- Symptom: Context startup reports NoUniqueBeanDefinitionException.
- Diagnostic goal: Qualify the intended implementation or define a primary bean.

### Buggy code

```java
@Bean PaymentGateway stripe() { return new StripeGateway(); }
@Bean PaymentGateway bank() { return new BankGateway(); }
@Service Checkout(PaymentGateway gateway) {}
```

### Expected diagnosis

The injection point has two candidates and no selection rule.

### Corrected code

```java
@Service Checkout(@Qualifier("stripe") PaymentGateway gateway) {}
```

### Regression tests

```java
// Context chooses Stripe only at the qualified injection point.
```

## IOC-E-033: self-invocation bypasses advice

- Difficulty: Easy
- Framework: Spring Core & Inversion of Control
- Language: Java
- Perspective: Proxying
- Concept: self-invocation bypasses advice
- Symptom: The transactional or cached annotation appears ignored.
- Diagnostic goal: Call the advised method through the proxy boundary.

### Buggy code

```java
@Transactional
public void outer() { inner(); }
@Transactional
public void inner() { /* work */ }
```

### Expected diagnosis

A direct this.inner() call never passes through the Spring proxy.

### Corrected code

```java
@Transactional
public void outer() { collaborator.inner(); }
```

### Regression tests

```java
// An integration test observes the transaction/caching advice on inner.
```

## IOC-E-034: request bean used outside request

- Difficulty: Easy
- Framework: Spring Core & Inversion of Control
- Language: Java
- Perspective: Scopes
- Concept: request bean used outside request
- Symptom: A background task throws scope-not-active.
- Diagnostic goal: Capture immutable data, not a request-scoped object, for background work.

### Buggy code

```java
executor.submit(() -> requestContext.getUserId());
```

### Expected diagnosis

The request scope may be gone when the task runs.

### Corrected code

```java
String userId = requestContext.getUserId();
executor.submit(() -> process(userId));
```

### Regression tests

```java
// The task remains valid after the request completes.
```

## IOC-E-035: event published before commit

- Difficulty: Easy
- Framework: Spring Core & Inversion of Control
- Language: Java
- Perspective: Events
- Concept: event published before commit
- Symptom: A listener sees data that later rolls back.
- Diagnostic goal: Publish after a successful transaction commit when required.

### Buggy code

```java
publisher.publishEvent(new OrderCreated(order.id()));
repository.save(order);
```

### Expected diagnosis

The event is emitted before persistence commits and may describe a transaction that fails.

### Corrected code

```java
repository.save(order);
publisher.publishEvent(new OrderCreated(order.id()));
```

### Regression tests

```java
// A transactional listener receives the event only after commit.
```

## IOC-E-036: conditional bean unexpectedly absent

- Difficulty: Easy
- Framework: Spring Core & Inversion of Control
- Language: Java
- Perspective: Factory
- Concept: conditional bean unexpectedly absent
- Symptom: A feature flag has no implementation.
- Diagnostic goal: Check condition names and the effective environment.

### Buggy code

```java
@ConditionalOnProperty(name = "feature.mail")
@Bean Mailer mailer() { return new Mailer(); }
```

### Expected diagnosis

The condition requires a value unless havingValue or matchIfMissing is configured as intended.

### Corrected code

```java
@ConditionalOnProperty(name = "feature.mail", havingValue = "true")
@Bean Mailer mailer() { return new Mailer(); }
```

### Regression tests

```java
// Context reports a bean only when feature.mail=true.
```

## IOC-E-037: close omitted

- Difficulty: Easy
- Framework: Spring Core & Inversion of Control
- Language: Java
- Perspective: Resource lifecycle
- Concept: close omitted
- Symptom: Threads or connections remain after context shutdown.
- Diagnostic goal: Register resources as managed beans with destruction callbacks.

### Buggy code

```java
@Bean ExecutorService executor() { return Executors.newFixedThreadPool(4); }
```

### Expected diagnosis

The container does not know how to stop an arbitrary resource unless destruction is declared.

### Corrected code

```java
@Bean(destroyMethod = "shutdown") ExecutorService executor() { return Executors.newFixedThreadPool(4); }
```

### Regression tests

```java
// Context close invokes shutdown.
```

## IOC-E-038: listener order assumed

- Difficulty: Easy
- Framework: Spring Core & Inversion of Control
- Language: Java
- Perspective: Ordering
- Concept: listener order assumed
- Symptom: Two startup tasks run in the wrong order.
- Diagnostic goal: Declare ordering only where the dependency is real.

### Buggy code

```java
@EventListener
void seed() {}
@EventListener
void publish() {}
```

### Expected diagnosis

Listener registration order is not a reliable dependency contract.

### Corrected code

```java
@Order(1) @EventListener void seed() {}
@Order(2) @EventListener void publish() {}
```

### Regression tests

```java
// The test records seed before publish.
```

## IOC-E-039: optional bean treated as required

- Difficulty: Easy
- Framework: Spring Core & Inversion of Control
- Language: Java
- Perspective: Optional dependencies
- Concept: optional bean treated as required
- Symptom: A feature cannot start without an optional integration.
- Diagnostic goal: Represent optionality explicitly.

### Buggy code

```java
public Reporter(Exporter exporter) { this.exporter = exporter; }
```

### Expected diagnosis

Constructor injection requires Exporter even when the feature is disabled.

### Corrected code

```java
public Reporter(ObjectProvider<Exporter> exporter) { this.exporter = exporter; }
```

### Regression tests

```java
// Reporter starts without Exporter and uses a no-op path.
```

## IOC-E-040: service cycle hidden by field injection

- Difficulty: Easy
- Framework: Spring Core & Inversion of Control
- Language: Java
- Perspective: Circular design
- Concept: service cycle hidden by field injection
- Symptom: Runtime behavior is order-dependent and difficult to test.
- Diagnostic goal: Extract a port or move orchestration into a third component.

### Buggy code

```java
@Autowired A a;
class A { @Autowired B b; }
class B { @Autowired A a; }
```

### Expected diagnosis

Field injection hides the cycle until context creation and makes dependencies mutable.

### Corrected code

```java
class Orchestrator { Orchestrator(A a, B b) {} }
```

### Regression tests

```java
// A and B no longer depend directly on one another.
```

## IOC-E-041: prototype injected into singleton

- Difficulty: Easy
- Framework: Spring Core & Inversion of Control
- Language: Java
- Perspective: Bean lifecycle
- Concept: prototype injected into singleton
- Symptom: A supposed new object is reused.
- Diagnostic goal: Obtain shorter-lived beans through a provider or scoped proxy.

### Buggy code

```java
@Component
class JobRunner { private final Job job; JobRunner(Job job) { this.job = job; } }
```

### Expected diagnosis

A prototype dependency is resolved once when the singleton is constructed.

### Corrected code

```java
@Component
class JobRunner { private final ObjectProvider<Job> jobs; JobRunner(ObjectProvider<Job> jobs) { this.jobs = jobs; }
 Job next() { return jobs.getObject(); } }
```

### Regression tests

```java
// Two calls to next return distinct Job instances.
```

## IOC-E-042: multiple candidates ambiguous

- Difficulty: Easy
- Framework: Spring Core & Inversion of Control
- Language: Java
- Perspective: Injection
- Concept: multiple candidates ambiguous
- Symptom: Context startup reports NoUniqueBeanDefinitionException.
- Diagnostic goal: Qualify the intended implementation or define a primary bean.

### Buggy code

```java
@Bean PaymentGateway stripe() { return new StripeGateway(); }
@Bean PaymentGateway bank() { return new BankGateway(); }
@Service Checkout(PaymentGateway gateway) {}
```

### Expected diagnosis

The injection point has two candidates and no selection rule.

### Corrected code

```java
@Service Checkout(@Qualifier("stripe") PaymentGateway gateway) {}
```

### Regression tests

```java
// Context chooses Stripe only at the qualified injection point.
```

## IOC-E-043: self-invocation bypasses advice

- Difficulty: Easy
- Framework: Spring Core & Inversion of Control
- Language: Java
- Perspective: Proxying
- Concept: self-invocation bypasses advice
- Symptom: The transactional or cached annotation appears ignored.
- Diagnostic goal: Call the advised method through the proxy boundary.

### Buggy code

```java
@Transactional
public void outer() { inner(); }
@Transactional
public void inner() { /* work */ }
```

### Expected diagnosis

A direct this.inner() call never passes through the Spring proxy.

### Corrected code

```java
@Transactional
public void outer() { collaborator.inner(); }
```

### Regression tests

```java
// An integration test observes the transaction/caching advice on inner.
```

## IOC-E-044: request bean used outside request

- Difficulty: Easy
- Framework: Spring Core & Inversion of Control
- Language: Java
- Perspective: Scopes
- Concept: request bean used outside request
- Symptom: A background task throws scope-not-active.
- Diagnostic goal: Capture immutable data, not a request-scoped object, for background work.

### Buggy code

```java
executor.submit(() -> requestContext.getUserId());
```

### Expected diagnosis

The request scope may be gone when the task runs.

### Corrected code

```java
String userId = requestContext.getUserId();
executor.submit(() -> process(userId));
```

### Regression tests

```java
// The task remains valid after the request completes.
```

## IOC-E-045: event published before commit

- Difficulty: Easy
- Framework: Spring Core & Inversion of Control
- Language: Java
- Perspective: Events
- Concept: event published before commit
- Symptom: A listener sees data that later rolls back.
- Diagnostic goal: Publish after a successful transaction commit when required.

### Buggy code

```java
publisher.publishEvent(new OrderCreated(order.id()));
repository.save(order);
```

### Expected diagnosis

The event is emitted before persistence commits and may describe a transaction that fails.

### Corrected code

```java
repository.save(order);
publisher.publishEvent(new OrderCreated(order.id()));
```

### Regression tests

```java
// A transactional listener receives the event only after commit.
```

## IOC-E-046: conditional bean unexpectedly absent

- Difficulty: Easy
- Framework: Spring Core & Inversion of Control
- Language: Java
- Perspective: Factory
- Concept: conditional bean unexpectedly absent
- Symptom: A feature flag has no implementation.
- Diagnostic goal: Check condition names and the effective environment.

### Buggy code

```java
@ConditionalOnProperty(name = "feature.mail")
@Bean Mailer mailer() { return new Mailer(); }
```

### Expected diagnosis

The condition requires a value unless havingValue or matchIfMissing is configured as intended.

### Corrected code

```java
@ConditionalOnProperty(name = "feature.mail", havingValue = "true")
@Bean Mailer mailer() { return new Mailer(); }
```

### Regression tests

```java
// Context reports a bean only when feature.mail=true.
```

## IOC-E-047: close omitted

- Difficulty: Easy
- Framework: Spring Core & Inversion of Control
- Language: Java
- Perspective: Resource lifecycle
- Concept: close omitted
- Symptom: Threads or connections remain after context shutdown.
- Diagnostic goal: Register resources as managed beans with destruction callbacks.

### Buggy code

```java
@Bean ExecutorService executor() { return Executors.newFixedThreadPool(4); }
```

### Expected diagnosis

The container does not know how to stop an arbitrary resource unless destruction is declared.

### Corrected code

```java
@Bean(destroyMethod = "shutdown") ExecutorService executor() { return Executors.newFixedThreadPool(4); }
```

### Regression tests

```java
// Context close invokes shutdown.
```

## IOC-E-048: listener order assumed

- Difficulty: Easy
- Framework: Spring Core & Inversion of Control
- Language: Java
- Perspective: Ordering
- Concept: listener order assumed
- Symptom: Two startup tasks run in the wrong order.
- Diagnostic goal: Declare ordering only where the dependency is real.

### Buggy code

```java
@EventListener
void seed() {}
@EventListener
void publish() {}
```

### Expected diagnosis

Listener registration order is not a reliable dependency contract.

### Corrected code

```java
@Order(1) @EventListener void seed() {}
@Order(2) @EventListener void publish() {}
```

### Regression tests

```java
// The test records seed before publish.
```

## IOC-E-049: optional bean treated as required

- Difficulty: Easy
- Framework: Spring Core & Inversion of Control
- Language: Java
- Perspective: Optional dependencies
- Concept: optional bean treated as required
- Symptom: A feature cannot start without an optional integration.
- Diagnostic goal: Represent optionality explicitly.

### Buggy code

```java
public Reporter(Exporter exporter) { this.exporter = exporter; }
```

### Expected diagnosis

Constructor injection requires Exporter even when the feature is disabled.

### Corrected code

```java
public Reporter(ObjectProvider<Exporter> exporter) { this.exporter = exporter; }
```

### Regression tests

```java
// Reporter starts without Exporter and uses a no-op path.
```

## IOC-E-050: service cycle hidden by field injection

- Difficulty: Easy
- Framework: Spring Core & Inversion of Control
- Language: Java
- Perspective: Circular design
- Concept: service cycle hidden by field injection
- Symptom: Runtime behavior is order-dependent and difficult to test.
- Diagnostic goal: Extract a port or move orchestration into a third component.

### Buggy code

```java
@Autowired A a;
class A { @Autowired B b; }
class B { @Autowired A a; }
```

### Expected diagnosis

Field injection hides the cycle until context creation and makes dependencies mutable.

### Corrected code

```java
class Orchestrator { Orchestrator(A a, B b) {} }
```

### Regression tests

```java
// A and B no longer depend directly on one another.
```

## IOC-E-051: prototype injected into singleton

- Difficulty: Easy
- Framework: Spring Core & Inversion of Control
- Language: Java
- Perspective: Bean lifecycle
- Concept: prototype injected into singleton
- Symptom: A supposed new object is reused.
- Diagnostic goal: Obtain shorter-lived beans through a provider or scoped proxy.

### Buggy code

```java
@Component
class JobRunner { private final Job job; JobRunner(Job job) { this.job = job; } }
```

### Expected diagnosis

A prototype dependency is resolved once when the singleton is constructed.

### Corrected code

```java
@Component
class JobRunner { private final ObjectProvider<Job> jobs; JobRunner(ObjectProvider<Job> jobs) { this.jobs = jobs; }
 Job next() { return jobs.getObject(); } }
```

### Regression tests

```java
// Two calls to next return distinct Job instances.
```

## IOC-E-052: multiple candidates ambiguous

- Difficulty: Easy
- Framework: Spring Core & Inversion of Control
- Language: Java
- Perspective: Injection
- Concept: multiple candidates ambiguous
- Symptom: Context startup reports NoUniqueBeanDefinitionException.
- Diagnostic goal: Qualify the intended implementation or define a primary bean.

### Buggy code

```java
@Bean PaymentGateway stripe() { return new StripeGateway(); }
@Bean PaymentGateway bank() { return new BankGateway(); }
@Service Checkout(PaymentGateway gateway) {}
```

### Expected diagnosis

The injection point has two candidates and no selection rule.

### Corrected code

```java
@Service Checkout(@Qualifier("stripe") PaymentGateway gateway) {}
```

### Regression tests

```java
// Context chooses Stripe only at the qualified injection point.
```

## IOC-E-053: self-invocation bypasses advice

- Difficulty: Easy
- Framework: Spring Core & Inversion of Control
- Language: Java
- Perspective: Proxying
- Concept: self-invocation bypasses advice
- Symptom: The transactional or cached annotation appears ignored.
- Diagnostic goal: Call the advised method through the proxy boundary.

### Buggy code

```java
@Transactional
public void outer() { inner(); }
@Transactional
public void inner() { /* work */ }
```

### Expected diagnosis

A direct this.inner() call never passes through the Spring proxy.

### Corrected code

```java
@Transactional
public void outer() { collaborator.inner(); }
```

### Regression tests

```java
// An integration test observes the transaction/caching advice on inner.
```

## IOC-E-054: request bean used outside request

- Difficulty: Easy
- Framework: Spring Core & Inversion of Control
- Language: Java
- Perspective: Scopes
- Concept: request bean used outside request
- Symptom: A background task throws scope-not-active.
- Diagnostic goal: Capture immutable data, not a request-scoped object, for background work.

### Buggy code

```java
executor.submit(() -> requestContext.getUserId());
```

### Expected diagnosis

The request scope may be gone when the task runs.

### Corrected code

```java
String userId = requestContext.getUserId();
executor.submit(() -> process(userId));
```

### Regression tests

```java
// The task remains valid after the request completes.
```

## IOC-E-055: event published before commit

- Difficulty: Easy
- Framework: Spring Core & Inversion of Control
- Language: Java
- Perspective: Events
- Concept: event published before commit
- Symptom: A listener sees data that later rolls back.
- Diagnostic goal: Publish after a successful transaction commit when required.

### Buggy code

```java
publisher.publishEvent(new OrderCreated(order.id()));
repository.save(order);
```

### Expected diagnosis

The event is emitted before persistence commits and may describe a transaction that fails.

### Corrected code

```java
repository.save(order);
publisher.publishEvent(new OrderCreated(order.id()));
```

### Regression tests

```java
// A transactional listener receives the event only after commit.
```

## IOC-E-056: conditional bean unexpectedly absent

- Difficulty: Easy
- Framework: Spring Core & Inversion of Control
- Language: Java
- Perspective: Factory
- Concept: conditional bean unexpectedly absent
- Symptom: A feature flag has no implementation.
- Diagnostic goal: Check condition names and the effective environment.

### Buggy code

```java
@ConditionalOnProperty(name = "feature.mail")
@Bean Mailer mailer() { return new Mailer(); }
```

### Expected diagnosis

The condition requires a value unless havingValue or matchIfMissing is configured as intended.

### Corrected code

```java
@ConditionalOnProperty(name = "feature.mail", havingValue = "true")
@Bean Mailer mailer() { return new Mailer(); }
```

### Regression tests

```java
// Context reports a bean only when feature.mail=true.
```

## IOC-E-057: close omitted

- Difficulty: Easy
- Framework: Spring Core & Inversion of Control
- Language: Java
- Perspective: Resource lifecycle
- Concept: close omitted
- Symptom: Threads or connections remain after context shutdown.
- Diagnostic goal: Register resources as managed beans with destruction callbacks.

### Buggy code

```java
@Bean ExecutorService executor() { return Executors.newFixedThreadPool(4); }
```

### Expected diagnosis

The container does not know how to stop an arbitrary resource unless destruction is declared.

### Corrected code

```java
@Bean(destroyMethod = "shutdown") ExecutorService executor() { return Executors.newFixedThreadPool(4); }
```

### Regression tests

```java
// Context close invokes shutdown.
```

## IOC-E-058: listener order assumed

- Difficulty: Easy
- Framework: Spring Core & Inversion of Control
- Language: Java
- Perspective: Ordering
- Concept: listener order assumed
- Symptom: Two startup tasks run in the wrong order.
- Diagnostic goal: Declare ordering only where the dependency is real.

### Buggy code

```java
@EventListener
void seed() {}
@EventListener
void publish() {}
```

### Expected diagnosis

Listener registration order is not a reliable dependency contract.

### Corrected code

```java
@Order(1) @EventListener void seed() {}
@Order(2) @EventListener void publish() {}
```

### Regression tests

```java
// The test records seed before publish.
```

## IOC-E-059: optional bean treated as required

- Difficulty: Easy
- Framework: Spring Core & Inversion of Control
- Language: Java
- Perspective: Optional dependencies
- Concept: optional bean treated as required
- Symptom: A feature cannot start without an optional integration.
- Diagnostic goal: Represent optionality explicitly.

### Buggy code

```java
public Reporter(Exporter exporter) { this.exporter = exporter; }
```

### Expected diagnosis

Constructor injection requires Exporter even when the feature is disabled.

### Corrected code

```java
public Reporter(ObjectProvider<Exporter> exporter) { this.exporter = exporter; }
```

### Regression tests

```java
// Reporter starts without Exporter and uses a no-op path.
```

## IOC-E-060: service cycle hidden by field injection

- Difficulty: Easy
- Framework: Spring Core & Inversion of Control
- Language: Java
- Perspective: Circular design
- Concept: service cycle hidden by field injection
- Symptom: Runtime behavior is order-dependent and difficult to test.
- Diagnostic goal: Extract a port or move orchestration into a third component.

### Buggy code

```java
@Autowired A a;
class A { @Autowired B b; }
class B { @Autowired A a; }
```

### Expected diagnosis

Field injection hides the cycle until context creation and makes dependencies mutable.

### Corrected code

```java
class Orchestrator { Orchestrator(A a, B b) {} }
```

### Regression tests

```java
// A and B no longer depend directly on one another.
```

## IOC-E-061: prototype injected into singleton

- Difficulty: Easy
- Framework: Spring Core & Inversion of Control
- Language: Java
- Perspective: Bean lifecycle
- Concept: prototype injected into singleton
- Symptom: A supposed new object is reused.
- Diagnostic goal: Obtain shorter-lived beans through a provider or scoped proxy.

### Buggy code

```java
@Component
class JobRunner { private final Job job; JobRunner(Job job) { this.job = job; } }
```

### Expected diagnosis

A prototype dependency is resolved once when the singleton is constructed.

### Corrected code

```java
@Component
class JobRunner { private final ObjectProvider<Job> jobs; JobRunner(ObjectProvider<Job> jobs) { this.jobs = jobs; }
 Job next() { return jobs.getObject(); } }
```

### Regression tests

```java
// Two calls to next return distinct Job instances.
```

## IOC-E-062: multiple candidates ambiguous

- Difficulty: Easy
- Framework: Spring Core & Inversion of Control
- Language: Java
- Perspective: Injection
- Concept: multiple candidates ambiguous
- Symptom: Context startup reports NoUniqueBeanDefinitionException.
- Diagnostic goal: Qualify the intended implementation or define a primary bean.

### Buggy code

```java
@Bean PaymentGateway stripe() { return new StripeGateway(); }
@Bean PaymentGateway bank() { return new BankGateway(); }
@Service Checkout(PaymentGateway gateway) {}
```

### Expected diagnosis

The injection point has two candidates and no selection rule.

### Corrected code

```java
@Service Checkout(@Qualifier("stripe") PaymentGateway gateway) {}
```

### Regression tests

```java
// Context chooses Stripe only at the qualified injection point.
```

## IOC-E-063: self-invocation bypasses advice

- Difficulty: Easy
- Framework: Spring Core & Inversion of Control
- Language: Java
- Perspective: Proxying
- Concept: self-invocation bypasses advice
- Symptom: The transactional or cached annotation appears ignored.
- Diagnostic goal: Call the advised method through the proxy boundary.

### Buggy code

```java
@Transactional
public void outer() { inner(); }
@Transactional
public void inner() { /* work */ }
```

### Expected diagnosis

A direct this.inner() call never passes through the Spring proxy.

### Corrected code

```java
@Transactional
public void outer() { collaborator.inner(); }
```

### Regression tests

```java
// An integration test observes the transaction/caching advice on inner.
```

## IOC-E-064: request bean used outside request

- Difficulty: Easy
- Framework: Spring Core & Inversion of Control
- Language: Java
- Perspective: Scopes
- Concept: request bean used outside request
- Symptom: A background task throws scope-not-active.
- Diagnostic goal: Capture immutable data, not a request-scoped object, for background work.

### Buggy code

```java
executor.submit(() -> requestContext.getUserId());
```

### Expected diagnosis

The request scope may be gone when the task runs.

### Corrected code

```java
String userId = requestContext.getUserId();
executor.submit(() -> process(userId));
```

### Regression tests

```java
// The task remains valid after the request completes.
```

## IOC-E-065: event published before commit

- Difficulty: Easy
- Framework: Spring Core & Inversion of Control
- Language: Java
- Perspective: Events
- Concept: event published before commit
- Symptom: A listener sees data that later rolls back.
- Diagnostic goal: Publish after a successful transaction commit when required.

### Buggy code

```java
publisher.publishEvent(new OrderCreated(order.id()));
repository.save(order);
```

### Expected diagnosis

The event is emitted before persistence commits and may describe a transaction that fails.

### Corrected code

```java
repository.save(order);
publisher.publishEvent(new OrderCreated(order.id()));
```

### Regression tests

```java
// A transactional listener receives the event only after commit.
```

## IOC-E-066: conditional bean unexpectedly absent

- Difficulty: Easy
- Framework: Spring Core & Inversion of Control
- Language: Java
- Perspective: Factory
- Concept: conditional bean unexpectedly absent
- Symptom: A feature flag has no implementation.
- Diagnostic goal: Check condition names and the effective environment.

### Buggy code

```java
@ConditionalOnProperty(name = "feature.mail")
@Bean Mailer mailer() { return new Mailer(); }
```

### Expected diagnosis

The condition requires a value unless havingValue or matchIfMissing is configured as intended.

### Corrected code

```java
@ConditionalOnProperty(name = "feature.mail", havingValue = "true")
@Bean Mailer mailer() { return new Mailer(); }
```

### Regression tests

```java
// Context reports a bean only when feature.mail=true.
```

## IOC-E-067: close omitted

- Difficulty: Easy
- Framework: Spring Core & Inversion of Control
- Language: Java
- Perspective: Resource lifecycle
- Concept: close omitted
- Symptom: Threads or connections remain after context shutdown.
- Diagnostic goal: Register resources as managed beans with destruction callbacks.

### Buggy code

```java
@Bean ExecutorService executor() { return Executors.newFixedThreadPool(4); }
```

### Expected diagnosis

The container does not know how to stop an arbitrary resource unless destruction is declared.

### Corrected code

```java
@Bean(destroyMethod = "shutdown") ExecutorService executor() { return Executors.newFixedThreadPool(4); }
```

### Regression tests

```java
// Context close invokes shutdown.
```

## IOC-E-068: listener order assumed

- Difficulty: Easy
- Framework: Spring Core & Inversion of Control
- Language: Java
- Perspective: Ordering
- Concept: listener order assumed
- Symptom: Two startup tasks run in the wrong order.
- Diagnostic goal: Declare ordering only where the dependency is real.

### Buggy code

```java
@EventListener
void seed() {}
@EventListener
void publish() {}
```

### Expected diagnosis

Listener registration order is not a reliable dependency contract.

### Corrected code

```java
@Order(1) @EventListener void seed() {}
@Order(2) @EventListener void publish() {}
```

### Regression tests

```java
// The test records seed before publish.
```

## IOC-E-069: optional bean treated as required

- Difficulty: Easy
- Framework: Spring Core & Inversion of Control
- Language: Java
- Perspective: Optional dependencies
- Concept: optional bean treated as required
- Symptom: A feature cannot start without an optional integration.
- Diagnostic goal: Represent optionality explicitly.

### Buggy code

```java
public Reporter(Exporter exporter) { this.exporter = exporter; }
```

### Expected diagnosis

Constructor injection requires Exporter even when the feature is disabled.

### Corrected code

```java
public Reporter(ObjectProvider<Exporter> exporter) { this.exporter = exporter; }
```

### Regression tests

```java
// Reporter starts without Exporter and uses a no-op path.
```

## IOC-E-070: service cycle hidden by field injection

- Difficulty: Easy
- Framework: Spring Core & Inversion of Control
- Language: Java
- Perspective: Circular design
- Concept: service cycle hidden by field injection
- Symptom: Runtime behavior is order-dependent and difficult to test.
- Diagnostic goal: Extract a port or move orchestration into a third component.

### Buggy code

```java
@Autowired A a;
class A { @Autowired B b; }
class B { @Autowired A a; }
```

### Expected diagnosis

Field injection hides the cycle until context creation and makes dependencies mutable.

### Corrected code

```java
class Orchestrator { Orchestrator(A a, B b) {} }
```

### Regression tests

```java
// A and B no longer depend directly on one another.
```

## IOC-E-071: prototype injected into singleton

- Difficulty: Easy
- Framework: Spring Core & Inversion of Control
- Language: Java
- Perspective: Bean lifecycle
- Concept: prototype injected into singleton
- Symptom: A supposed new object is reused.
- Diagnostic goal: Obtain shorter-lived beans through a provider or scoped proxy.

### Buggy code

```java
@Component
class JobRunner { private final Job job; JobRunner(Job job) { this.job = job; } }
```

### Expected diagnosis

A prototype dependency is resolved once when the singleton is constructed.

### Corrected code

```java
@Component
class JobRunner { private final ObjectProvider<Job> jobs; JobRunner(ObjectProvider<Job> jobs) { this.jobs = jobs; }
 Job next() { return jobs.getObject(); } }
```

### Regression tests

```java
// Two calls to next return distinct Job instances.
```

## IOC-E-072: multiple candidates ambiguous

- Difficulty: Easy
- Framework: Spring Core & Inversion of Control
- Language: Java
- Perspective: Injection
- Concept: multiple candidates ambiguous
- Symptom: Context startup reports NoUniqueBeanDefinitionException.
- Diagnostic goal: Qualify the intended implementation or define a primary bean.

### Buggy code

```java
@Bean PaymentGateway stripe() { return new StripeGateway(); }
@Bean PaymentGateway bank() { return new BankGateway(); }
@Service Checkout(PaymentGateway gateway) {}
```

### Expected diagnosis

The injection point has two candidates and no selection rule.

### Corrected code

```java
@Service Checkout(@Qualifier("stripe") PaymentGateway gateway) {}
```

### Regression tests

```java
// Context chooses Stripe only at the qualified injection point.
```

## IOC-E-073: self-invocation bypasses advice

- Difficulty: Easy
- Framework: Spring Core & Inversion of Control
- Language: Java
- Perspective: Proxying
- Concept: self-invocation bypasses advice
- Symptom: The transactional or cached annotation appears ignored.
- Diagnostic goal: Call the advised method through the proxy boundary.

### Buggy code

```java
@Transactional
public void outer() { inner(); }
@Transactional
public void inner() { /* work */ }
```

### Expected diagnosis

A direct this.inner() call never passes through the Spring proxy.

### Corrected code

```java
@Transactional
public void outer() { collaborator.inner(); }
```

### Regression tests

```java
// An integration test observes the transaction/caching advice on inner.
```

## IOC-E-074: request bean used outside request

- Difficulty: Easy
- Framework: Spring Core & Inversion of Control
- Language: Java
- Perspective: Scopes
- Concept: request bean used outside request
- Symptom: A background task throws scope-not-active.
- Diagnostic goal: Capture immutable data, not a request-scoped object, for background work.

### Buggy code

```java
executor.submit(() -> requestContext.getUserId());
```

### Expected diagnosis

The request scope may be gone when the task runs.

### Corrected code

```java
String userId = requestContext.getUserId();
executor.submit(() -> process(userId));
```

### Regression tests

```java
// The task remains valid after the request completes.
```

## IOC-E-075: event published before commit

- Difficulty: Easy
- Framework: Spring Core & Inversion of Control
- Language: Java
- Perspective: Events
- Concept: event published before commit
- Symptom: A listener sees data that later rolls back.
- Diagnostic goal: Publish after a successful transaction commit when required.

### Buggy code

```java
publisher.publishEvent(new OrderCreated(order.id()));
repository.save(order);
```

### Expected diagnosis

The event is emitted before persistence commits and may describe a transaction that fails.

### Corrected code

```java
repository.save(order);
publisher.publishEvent(new OrderCreated(order.id()));
```

### Regression tests

```java
// A transactional listener receives the event only after commit.
```

## IOC-E-076: conditional bean unexpectedly absent

- Difficulty: Easy
- Framework: Spring Core & Inversion of Control
- Language: Java
- Perspective: Factory
- Concept: conditional bean unexpectedly absent
- Symptom: A feature flag has no implementation.
- Diagnostic goal: Check condition names and the effective environment.

### Buggy code

```java
@ConditionalOnProperty(name = "feature.mail")
@Bean Mailer mailer() { return new Mailer(); }
```

### Expected diagnosis

The condition requires a value unless havingValue or matchIfMissing is configured as intended.

### Corrected code

```java
@ConditionalOnProperty(name = "feature.mail", havingValue = "true")
@Bean Mailer mailer() { return new Mailer(); }
```

### Regression tests

```java
// Context reports a bean only when feature.mail=true.
```

## IOC-E-077: close omitted

- Difficulty: Easy
- Framework: Spring Core & Inversion of Control
- Language: Java
- Perspective: Resource lifecycle
- Concept: close omitted
- Symptom: Threads or connections remain after context shutdown.
- Diagnostic goal: Register resources as managed beans with destruction callbacks.

### Buggy code

```java
@Bean ExecutorService executor() { return Executors.newFixedThreadPool(4); }
```

### Expected diagnosis

The container does not know how to stop an arbitrary resource unless destruction is declared.

### Corrected code

```java
@Bean(destroyMethod = "shutdown") ExecutorService executor() { return Executors.newFixedThreadPool(4); }
```

### Regression tests

```java
// Context close invokes shutdown.
```

## IOC-E-078: listener order assumed

- Difficulty: Easy
- Framework: Spring Core & Inversion of Control
- Language: Java
- Perspective: Ordering
- Concept: listener order assumed
- Symptom: Two startup tasks run in the wrong order.
- Diagnostic goal: Declare ordering only where the dependency is real.

### Buggy code

```java
@EventListener
void seed() {}
@EventListener
void publish() {}
```

### Expected diagnosis

Listener registration order is not a reliable dependency contract.

### Corrected code

```java
@Order(1) @EventListener void seed() {}
@Order(2) @EventListener void publish() {}
```

### Regression tests

```java
// The test records seed before publish.
```

## IOC-E-079: optional bean treated as required

- Difficulty: Easy
- Framework: Spring Core & Inversion of Control
- Language: Java
- Perspective: Optional dependencies
- Concept: optional bean treated as required
- Symptom: A feature cannot start without an optional integration.
- Diagnostic goal: Represent optionality explicitly.

### Buggy code

```java
public Reporter(Exporter exporter) { this.exporter = exporter; }
```

### Expected diagnosis

Constructor injection requires Exporter even when the feature is disabled.

### Corrected code

```java
public Reporter(ObjectProvider<Exporter> exporter) { this.exporter = exporter; }
```

### Regression tests

```java
// Reporter starts without Exporter and uses a no-op path.
```

## IOC-E-080: service cycle hidden by field injection

- Difficulty: Easy
- Framework: Spring Core & Inversion of Control
- Language: Java
- Perspective: Circular design
- Concept: service cycle hidden by field injection
- Symptom: Runtime behavior is order-dependent and difficult to test.
- Diagnostic goal: Extract a port or move orchestration into a third component.

### Buggy code

```java
@Autowired A a;
class A { @Autowired B b; }
class B { @Autowired A a; }
```

### Expected diagnosis

Field injection hides the cycle until context creation and makes dependencies mutable.

### Corrected code

```java
class Orchestrator { Orchestrator(A a, B b) {} }
```

### Regression tests

```java
// A and B no longer depend directly on one another.
```

## IOC-E-081: prototype injected into singleton

- Difficulty: Easy
- Framework: Spring Core & Inversion of Control
- Language: Java
- Perspective: Bean lifecycle
- Concept: prototype injected into singleton
- Symptom: A supposed new object is reused.
- Diagnostic goal: Obtain shorter-lived beans through a provider or scoped proxy.

### Buggy code

```java
@Component
class JobRunner { private final Job job; JobRunner(Job job) { this.job = job; } }
```

### Expected diagnosis

A prototype dependency is resolved once when the singleton is constructed.

### Corrected code

```java
@Component
class JobRunner { private final ObjectProvider<Job> jobs; JobRunner(ObjectProvider<Job> jobs) { this.jobs = jobs; }
 Job next() { return jobs.getObject(); } }
```

### Regression tests

```java
// Two calls to next return distinct Job instances.
```

## IOC-E-082: multiple candidates ambiguous

- Difficulty: Easy
- Framework: Spring Core & Inversion of Control
- Language: Java
- Perspective: Injection
- Concept: multiple candidates ambiguous
- Symptom: Context startup reports NoUniqueBeanDefinitionException.
- Diagnostic goal: Qualify the intended implementation or define a primary bean.

### Buggy code

```java
@Bean PaymentGateway stripe() { return new StripeGateway(); }
@Bean PaymentGateway bank() { return new BankGateway(); }
@Service Checkout(PaymentGateway gateway) {}
```

### Expected diagnosis

The injection point has two candidates and no selection rule.

### Corrected code

```java
@Service Checkout(@Qualifier("stripe") PaymentGateway gateway) {}
```

### Regression tests

```java
// Context chooses Stripe only at the qualified injection point.
```

## IOC-E-083: self-invocation bypasses advice

- Difficulty: Easy
- Framework: Spring Core & Inversion of Control
- Language: Java
- Perspective: Proxying
- Concept: self-invocation bypasses advice
- Symptom: The transactional or cached annotation appears ignored.
- Diagnostic goal: Call the advised method through the proxy boundary.

### Buggy code

```java
@Transactional
public void outer() { inner(); }
@Transactional
public void inner() { /* work */ }
```

### Expected diagnosis

A direct this.inner() call never passes through the Spring proxy.

### Corrected code

```java
@Transactional
public void outer() { collaborator.inner(); }
```

### Regression tests

```java
// An integration test observes the transaction/caching advice on inner.
```

## IOC-E-084: request bean used outside request

- Difficulty: Easy
- Framework: Spring Core & Inversion of Control
- Language: Java
- Perspective: Scopes
- Concept: request bean used outside request
- Symptom: A background task throws scope-not-active.
- Diagnostic goal: Capture immutable data, not a request-scoped object, for background work.

### Buggy code

```java
executor.submit(() -> requestContext.getUserId());
```

### Expected diagnosis

The request scope may be gone when the task runs.

### Corrected code

```java
String userId = requestContext.getUserId();
executor.submit(() -> process(userId));
```

### Regression tests

```java
// The task remains valid after the request completes.
```

## IOC-E-085: event published before commit

- Difficulty: Easy
- Framework: Spring Core & Inversion of Control
- Language: Java
- Perspective: Events
- Concept: event published before commit
- Symptom: A listener sees data that later rolls back.
- Diagnostic goal: Publish after a successful transaction commit when required.

### Buggy code

```java
publisher.publishEvent(new OrderCreated(order.id()));
repository.save(order);
```

### Expected diagnosis

The event is emitted before persistence commits and may describe a transaction that fails.

### Corrected code

```java
repository.save(order);
publisher.publishEvent(new OrderCreated(order.id()));
```

### Regression tests

```java
// A transactional listener receives the event only after commit.
```

## IOC-E-086: conditional bean unexpectedly absent

- Difficulty: Easy
- Framework: Spring Core & Inversion of Control
- Language: Java
- Perspective: Factory
- Concept: conditional bean unexpectedly absent
- Symptom: A feature flag has no implementation.
- Diagnostic goal: Check condition names and the effective environment.

### Buggy code

```java
@ConditionalOnProperty(name = "feature.mail")
@Bean Mailer mailer() { return new Mailer(); }
```

### Expected diagnosis

The condition requires a value unless havingValue or matchIfMissing is configured as intended.

### Corrected code

```java
@ConditionalOnProperty(name = "feature.mail", havingValue = "true")
@Bean Mailer mailer() { return new Mailer(); }
```

### Regression tests

```java
// Context reports a bean only when feature.mail=true.
```

## IOC-E-087: close omitted

- Difficulty: Easy
- Framework: Spring Core & Inversion of Control
- Language: Java
- Perspective: Resource lifecycle
- Concept: close omitted
- Symptom: Threads or connections remain after context shutdown.
- Diagnostic goal: Register resources as managed beans with destruction callbacks.

### Buggy code

```java
@Bean ExecutorService executor() { return Executors.newFixedThreadPool(4); }
```

### Expected diagnosis

The container does not know how to stop an arbitrary resource unless destruction is declared.

### Corrected code

```java
@Bean(destroyMethod = "shutdown") ExecutorService executor() { return Executors.newFixedThreadPool(4); }
```

### Regression tests

```java
// Context close invokes shutdown.
```

## IOC-E-088: listener order assumed

- Difficulty: Easy
- Framework: Spring Core & Inversion of Control
- Language: Java
- Perspective: Ordering
- Concept: listener order assumed
- Symptom: Two startup tasks run in the wrong order.
- Diagnostic goal: Declare ordering only where the dependency is real.

### Buggy code

```java
@EventListener
void seed() {}
@EventListener
void publish() {}
```

### Expected diagnosis

Listener registration order is not a reliable dependency contract.

### Corrected code

```java
@Order(1) @EventListener void seed() {}
@Order(2) @EventListener void publish() {}
```

### Regression tests

```java
// The test records seed before publish.
```

## IOC-E-089: optional bean treated as required

- Difficulty: Easy
- Framework: Spring Core & Inversion of Control
- Language: Java
- Perspective: Optional dependencies
- Concept: optional bean treated as required
- Symptom: A feature cannot start without an optional integration.
- Diagnostic goal: Represent optionality explicitly.

### Buggy code

```java
public Reporter(Exporter exporter) { this.exporter = exporter; }
```

### Expected diagnosis

Constructor injection requires Exporter even when the feature is disabled.

### Corrected code

```java
public Reporter(ObjectProvider<Exporter> exporter) { this.exporter = exporter; }
```

### Regression tests

```java
// Reporter starts without Exporter and uses a no-op path.
```

## IOC-E-090: service cycle hidden by field injection

- Difficulty: Easy
- Framework: Spring Core & Inversion of Control
- Language: Java
- Perspective: Circular design
- Concept: service cycle hidden by field injection
- Symptom: Runtime behavior is order-dependent and difficult to test.
- Diagnostic goal: Extract a port or move orchestration into a third component.

### Buggy code

```java
@Autowired A a;
class A { @Autowired B b; }
class B { @Autowired A a; }
```

### Expected diagnosis

Field injection hides the cycle until context creation and makes dependencies mutable.

### Corrected code

```java
class Orchestrator { Orchestrator(A a, B b) {} }
```

### Regression tests

```java
// A and B no longer depend directly on one another.
```

## IOC-E-091: prototype injected into singleton

- Difficulty: Easy
- Framework: Spring Core & Inversion of Control
- Language: Java
- Perspective: Bean lifecycle
- Concept: prototype injected into singleton
- Symptom: A supposed new object is reused.
- Diagnostic goal: Obtain shorter-lived beans through a provider or scoped proxy.

### Buggy code

```java
@Component
class JobRunner { private final Job job; JobRunner(Job job) { this.job = job; } }
```

### Expected diagnosis

A prototype dependency is resolved once when the singleton is constructed.

### Corrected code

```java
@Component
class JobRunner { private final ObjectProvider<Job> jobs; JobRunner(ObjectProvider<Job> jobs) { this.jobs = jobs; }
 Job next() { return jobs.getObject(); } }
```

### Regression tests

```java
// Two calls to next return distinct Job instances.
```

## IOC-E-092: multiple candidates ambiguous

- Difficulty: Easy
- Framework: Spring Core & Inversion of Control
- Language: Java
- Perspective: Injection
- Concept: multiple candidates ambiguous
- Symptom: Context startup reports NoUniqueBeanDefinitionException.
- Diagnostic goal: Qualify the intended implementation or define a primary bean.

### Buggy code

```java
@Bean PaymentGateway stripe() { return new StripeGateway(); }
@Bean PaymentGateway bank() { return new BankGateway(); }
@Service Checkout(PaymentGateway gateway) {}
```

### Expected diagnosis

The injection point has two candidates and no selection rule.

### Corrected code

```java
@Service Checkout(@Qualifier("stripe") PaymentGateway gateway) {}
```

### Regression tests

```java
// Context chooses Stripe only at the qualified injection point.
```

## IOC-E-093: self-invocation bypasses advice

- Difficulty: Easy
- Framework: Spring Core & Inversion of Control
- Language: Java
- Perspective: Proxying
- Concept: self-invocation bypasses advice
- Symptom: The transactional or cached annotation appears ignored.
- Diagnostic goal: Call the advised method through the proxy boundary.

### Buggy code

```java
@Transactional
public void outer() { inner(); }
@Transactional
public void inner() { /* work */ }
```

### Expected diagnosis

A direct this.inner() call never passes through the Spring proxy.

### Corrected code

```java
@Transactional
public void outer() { collaborator.inner(); }
```

### Regression tests

```java
// An integration test observes the transaction/caching advice on inner.
```

## IOC-E-094: request bean used outside request

- Difficulty: Easy
- Framework: Spring Core & Inversion of Control
- Language: Java
- Perspective: Scopes
- Concept: request bean used outside request
- Symptom: A background task throws scope-not-active.
- Diagnostic goal: Capture immutable data, not a request-scoped object, for background work.

### Buggy code

```java
executor.submit(() -> requestContext.getUserId());
```

### Expected diagnosis

The request scope may be gone when the task runs.

### Corrected code

```java
String userId = requestContext.getUserId();
executor.submit(() -> process(userId));
```

### Regression tests

```java
// The task remains valid after the request completes.
```

## IOC-E-095: event published before commit

- Difficulty: Easy
- Framework: Spring Core & Inversion of Control
- Language: Java
- Perspective: Events
- Concept: event published before commit
- Symptom: A listener sees data that later rolls back.
- Diagnostic goal: Publish after a successful transaction commit when required.

### Buggy code

```java
publisher.publishEvent(new OrderCreated(order.id()));
repository.save(order);
```

### Expected diagnosis

The event is emitted before persistence commits and may describe a transaction that fails.

### Corrected code

```java
repository.save(order);
publisher.publishEvent(new OrderCreated(order.id()));
```

### Regression tests

```java
// A transactional listener receives the event only after commit.
```

## IOC-E-096: conditional bean unexpectedly absent

- Difficulty: Easy
- Framework: Spring Core & Inversion of Control
- Language: Java
- Perspective: Factory
- Concept: conditional bean unexpectedly absent
- Symptom: A feature flag has no implementation.
- Diagnostic goal: Check condition names and the effective environment.

### Buggy code

```java
@ConditionalOnProperty(name = "feature.mail")
@Bean Mailer mailer() { return new Mailer(); }
```

### Expected diagnosis

The condition requires a value unless havingValue or matchIfMissing is configured as intended.

### Corrected code

```java
@ConditionalOnProperty(name = "feature.mail", havingValue = "true")
@Bean Mailer mailer() { return new Mailer(); }
```

### Regression tests

```java
// Context reports a bean only when feature.mail=true.
```

## IOC-E-097: close omitted

- Difficulty: Easy
- Framework: Spring Core & Inversion of Control
- Language: Java
- Perspective: Resource lifecycle
- Concept: close omitted
- Symptom: Threads or connections remain after context shutdown.
- Diagnostic goal: Register resources as managed beans with destruction callbacks.

### Buggy code

```java
@Bean ExecutorService executor() { return Executors.newFixedThreadPool(4); }
```

### Expected diagnosis

The container does not know how to stop an arbitrary resource unless destruction is declared.

### Corrected code

```java
@Bean(destroyMethod = "shutdown") ExecutorService executor() { return Executors.newFixedThreadPool(4); }
```

### Regression tests

```java
// Context close invokes shutdown.
```

## IOC-E-098: listener order assumed

- Difficulty: Easy
- Framework: Spring Core & Inversion of Control
- Language: Java
- Perspective: Ordering
- Concept: listener order assumed
- Symptom: Two startup tasks run in the wrong order.
- Diagnostic goal: Declare ordering only where the dependency is real.

### Buggy code

```java
@EventListener
void seed() {}
@EventListener
void publish() {}
```

### Expected diagnosis

Listener registration order is not a reliable dependency contract.

### Corrected code

```java
@Order(1) @EventListener void seed() {}
@Order(2) @EventListener void publish() {}
```

### Regression tests

```java
// The test records seed before publish.
```

## IOC-E-099: optional bean treated as required

- Difficulty: Easy
- Framework: Spring Core & Inversion of Control
- Language: Java
- Perspective: Optional dependencies
- Concept: optional bean treated as required
- Symptom: A feature cannot start without an optional integration.
- Diagnostic goal: Represent optionality explicitly.

### Buggy code

```java
public Reporter(Exporter exporter) { this.exporter = exporter; }
```

### Expected diagnosis

Constructor injection requires Exporter even when the feature is disabled.

### Corrected code

```java
public Reporter(ObjectProvider<Exporter> exporter) { this.exporter = exporter; }
```

### Regression tests

```java
// Reporter starts without Exporter and uses a no-op path.
```

## IOC-E-100: service cycle hidden by field injection

- Difficulty: Easy
- Framework: Spring Core & Inversion of Control
- Language: Java
- Perspective: Circular design
- Concept: service cycle hidden by field injection
- Symptom: Runtime behavior is order-dependent and difficult to test.
- Diagnostic goal: Extract a port or move orchestration into a third component.

### Buggy code

```java
@Autowired A a;
class A { @Autowired B b; }
class B { @Autowired A a; }
```

### Expected diagnosis

Field injection hides the cycle until context creation and makes dependencies mutable.

### Corrected code

```java
class Orchestrator { Orchestrator(A a, B b) {} }
```

### Regression tests

```java
// A and B no longer depend directly on one another.
```

## IOC-M-001: prototype injected into singleton

- Difficulty: Medium
- Framework: Spring Core & Inversion of Control
- Language: Java
- Perspective: Bean lifecycle
- Concept: prototype injected into singleton
- Symptom: A supposed new object is reused.
- Diagnostic goal: Obtain shorter-lived beans through a provider or scoped proxy.

### Buggy code

```java
@Component
class JobRunner { private final Job job; JobRunner(Job job) { this.job = job; } }
```

### Expected diagnosis

A prototype dependency is resolved once when the singleton is constructed.

### Corrected code

```java
@Component
class JobRunner { private final ObjectProvider<Job> jobs; JobRunner(ObjectProvider<Job> jobs) { this.jobs = jobs; }
 Job next() { return jobs.getObject(); } }
```

### Regression tests

```java
// Two calls to next return distinct Job instances.
```

## IOC-M-002: multiple candidates ambiguous

- Difficulty: Medium
- Framework: Spring Core & Inversion of Control
- Language: Java
- Perspective: Injection
- Concept: multiple candidates ambiguous
- Symptom: Context startup reports NoUniqueBeanDefinitionException.
- Diagnostic goal: Qualify the intended implementation or define a primary bean.

### Buggy code

```java
@Bean PaymentGateway stripe() { return new StripeGateway(); }
@Bean PaymentGateway bank() { return new BankGateway(); }
@Service Checkout(PaymentGateway gateway) {}
```

### Expected diagnosis

The injection point has two candidates and no selection rule.

### Corrected code

```java
@Service Checkout(@Qualifier("stripe") PaymentGateway gateway) {}
```

### Regression tests

```java
// Context chooses Stripe only at the qualified injection point.
```

## IOC-M-003: self-invocation bypasses advice

- Difficulty: Medium
- Framework: Spring Core & Inversion of Control
- Language: Java
- Perspective: Proxying
- Concept: self-invocation bypasses advice
- Symptom: The transactional or cached annotation appears ignored.
- Diagnostic goal: Call the advised method through the proxy boundary.

### Buggy code

```java
@Transactional
public void outer() { inner(); }
@Transactional
public void inner() { /* work */ }
```

### Expected diagnosis

A direct this.inner() call never passes through the Spring proxy.

### Corrected code

```java
@Transactional
public void outer() { collaborator.inner(); }
```

### Regression tests

```java
// An integration test observes the transaction/caching advice on inner.
```

## IOC-M-004: request bean used outside request

- Difficulty: Medium
- Framework: Spring Core & Inversion of Control
- Language: Java
- Perspective: Scopes
- Concept: request bean used outside request
- Symptom: A background task throws scope-not-active.
- Diagnostic goal: Capture immutable data, not a request-scoped object, for background work.

### Buggy code

```java
executor.submit(() -> requestContext.getUserId());
```

### Expected diagnosis

The request scope may be gone when the task runs.

### Corrected code

```java
String userId = requestContext.getUserId();
executor.submit(() -> process(userId));
```

### Regression tests

```java
// The task remains valid after the request completes.
```

## IOC-M-005: event published before commit

- Difficulty: Medium
- Framework: Spring Core & Inversion of Control
- Language: Java
- Perspective: Events
- Concept: event published before commit
- Symptom: A listener sees data that later rolls back.
- Diagnostic goal: Publish after a successful transaction commit when required.

### Buggy code

```java
publisher.publishEvent(new OrderCreated(order.id()));
repository.save(order);
```

### Expected diagnosis

The event is emitted before persistence commits and may describe a transaction that fails.

### Corrected code

```java
repository.save(order);
publisher.publishEvent(new OrderCreated(order.id()));
```

### Regression tests

```java
// A transactional listener receives the event only after commit.
```

## IOC-M-006: conditional bean unexpectedly absent

- Difficulty: Medium
- Framework: Spring Core & Inversion of Control
- Language: Java
- Perspective: Factory
- Concept: conditional bean unexpectedly absent
- Symptom: A feature flag has no implementation.
- Diagnostic goal: Check condition names and the effective environment.

### Buggy code

```java
@ConditionalOnProperty(name = "feature.mail")
@Bean Mailer mailer() { return new Mailer(); }
```

### Expected diagnosis

The condition requires a value unless havingValue or matchIfMissing is configured as intended.

### Corrected code

```java
@ConditionalOnProperty(name = "feature.mail", havingValue = "true")
@Bean Mailer mailer() { return new Mailer(); }
```

### Regression tests

```java
// Context reports a bean only when feature.mail=true.
```

## IOC-M-007: close omitted

- Difficulty: Medium
- Framework: Spring Core & Inversion of Control
- Language: Java
- Perspective: Resource lifecycle
- Concept: close omitted
- Symptom: Threads or connections remain after context shutdown.
- Diagnostic goal: Register resources as managed beans with destruction callbacks.

### Buggy code

```java
@Bean ExecutorService executor() { return Executors.newFixedThreadPool(4); }
```

### Expected diagnosis

The container does not know how to stop an arbitrary resource unless destruction is declared.

### Corrected code

```java
@Bean(destroyMethod = "shutdown") ExecutorService executor() { return Executors.newFixedThreadPool(4); }
```

### Regression tests

```java
// Context close invokes shutdown.
```

## IOC-M-008: listener order assumed

- Difficulty: Medium
- Framework: Spring Core & Inversion of Control
- Language: Java
- Perspective: Ordering
- Concept: listener order assumed
- Symptom: Two startup tasks run in the wrong order.
- Diagnostic goal: Declare ordering only where the dependency is real.

### Buggy code

```java
@EventListener
void seed() {}
@EventListener
void publish() {}
```

### Expected diagnosis

Listener registration order is not a reliable dependency contract.

### Corrected code

```java
@Order(1) @EventListener void seed() {}
@Order(2) @EventListener void publish() {}
```

### Regression tests

```java
// The test records seed before publish.
```

## IOC-M-009: optional bean treated as required

- Difficulty: Medium
- Framework: Spring Core & Inversion of Control
- Language: Java
- Perspective: Optional dependencies
- Concept: optional bean treated as required
- Symptom: A feature cannot start without an optional integration.
- Diagnostic goal: Represent optionality explicitly.

### Buggy code

```java
public Reporter(Exporter exporter) { this.exporter = exporter; }
```

### Expected diagnosis

Constructor injection requires Exporter even when the feature is disabled.

### Corrected code

```java
public Reporter(ObjectProvider<Exporter> exporter) { this.exporter = exporter; }
```

### Regression tests

```java
// Reporter starts without Exporter and uses a no-op path.
```

## IOC-M-010: service cycle hidden by field injection

- Difficulty: Medium
- Framework: Spring Core & Inversion of Control
- Language: Java
- Perspective: Circular design
- Concept: service cycle hidden by field injection
- Symptom: Runtime behavior is order-dependent and difficult to test.
- Diagnostic goal: Extract a port or move orchestration into a third component.

### Buggy code

```java
@Autowired A a;
class A { @Autowired B b; }
class B { @Autowired A a; }
```

### Expected diagnosis

Field injection hides the cycle until context creation and makes dependencies mutable.

### Corrected code

```java
class Orchestrator { Orchestrator(A a, B b) {} }
```

### Regression tests

```java
// A and B no longer depend directly on one another.
```

## IOC-M-011: prototype injected into singleton

- Difficulty: Medium
- Framework: Spring Core & Inversion of Control
- Language: Java
- Perspective: Bean lifecycle
- Concept: prototype injected into singleton
- Symptom: A supposed new object is reused.
- Diagnostic goal: Obtain shorter-lived beans through a provider or scoped proxy.

### Buggy code

```java
@Component
class JobRunner { private final Job job; JobRunner(Job job) { this.job = job; } }
```

### Expected diagnosis

A prototype dependency is resolved once when the singleton is constructed.

### Corrected code

```java
@Component
class JobRunner { private final ObjectProvider<Job> jobs; JobRunner(ObjectProvider<Job> jobs) { this.jobs = jobs; }
 Job next() { return jobs.getObject(); } }
```

### Regression tests

```java
// Two calls to next return distinct Job instances.
```

## IOC-M-012: multiple candidates ambiguous

- Difficulty: Medium
- Framework: Spring Core & Inversion of Control
- Language: Java
- Perspective: Injection
- Concept: multiple candidates ambiguous
- Symptom: Context startup reports NoUniqueBeanDefinitionException.
- Diagnostic goal: Qualify the intended implementation or define a primary bean.

### Buggy code

```java
@Bean PaymentGateway stripe() { return new StripeGateway(); }
@Bean PaymentGateway bank() { return new BankGateway(); }
@Service Checkout(PaymentGateway gateway) {}
```

### Expected diagnosis

The injection point has two candidates and no selection rule.

### Corrected code

```java
@Service Checkout(@Qualifier("stripe") PaymentGateway gateway) {}
```

### Regression tests

```java
// Context chooses Stripe only at the qualified injection point.
```

## IOC-M-013: self-invocation bypasses advice

- Difficulty: Medium
- Framework: Spring Core & Inversion of Control
- Language: Java
- Perspective: Proxying
- Concept: self-invocation bypasses advice
- Symptom: The transactional or cached annotation appears ignored.
- Diagnostic goal: Call the advised method through the proxy boundary.

### Buggy code

```java
@Transactional
public void outer() { inner(); }
@Transactional
public void inner() { /* work */ }
```

### Expected diagnosis

A direct this.inner() call never passes through the Spring proxy.

### Corrected code

```java
@Transactional
public void outer() { collaborator.inner(); }
```

### Regression tests

```java
// An integration test observes the transaction/caching advice on inner.
```

## IOC-M-014: request bean used outside request

- Difficulty: Medium
- Framework: Spring Core & Inversion of Control
- Language: Java
- Perspective: Scopes
- Concept: request bean used outside request
- Symptom: A background task throws scope-not-active.
- Diagnostic goal: Capture immutable data, not a request-scoped object, for background work.

### Buggy code

```java
executor.submit(() -> requestContext.getUserId());
```

### Expected diagnosis

The request scope may be gone when the task runs.

### Corrected code

```java
String userId = requestContext.getUserId();
executor.submit(() -> process(userId));
```

### Regression tests

```java
// The task remains valid after the request completes.
```

## IOC-M-015: event published before commit

- Difficulty: Medium
- Framework: Spring Core & Inversion of Control
- Language: Java
- Perspective: Events
- Concept: event published before commit
- Symptom: A listener sees data that later rolls back.
- Diagnostic goal: Publish after a successful transaction commit when required.

### Buggy code

```java
publisher.publishEvent(new OrderCreated(order.id()));
repository.save(order);
```

### Expected diagnosis

The event is emitted before persistence commits and may describe a transaction that fails.

### Corrected code

```java
repository.save(order);
publisher.publishEvent(new OrderCreated(order.id()));
```

### Regression tests

```java
// A transactional listener receives the event only after commit.
```

## IOC-M-016: conditional bean unexpectedly absent

- Difficulty: Medium
- Framework: Spring Core & Inversion of Control
- Language: Java
- Perspective: Factory
- Concept: conditional bean unexpectedly absent
- Symptom: A feature flag has no implementation.
- Diagnostic goal: Check condition names and the effective environment.

### Buggy code

```java
@ConditionalOnProperty(name = "feature.mail")
@Bean Mailer mailer() { return new Mailer(); }
```

### Expected diagnosis

The condition requires a value unless havingValue or matchIfMissing is configured as intended.

### Corrected code

```java
@ConditionalOnProperty(name = "feature.mail", havingValue = "true")
@Bean Mailer mailer() { return new Mailer(); }
```

### Regression tests

```java
// Context reports a bean only when feature.mail=true.
```

## IOC-M-017: close omitted

- Difficulty: Medium
- Framework: Spring Core & Inversion of Control
- Language: Java
- Perspective: Resource lifecycle
- Concept: close omitted
- Symptom: Threads or connections remain after context shutdown.
- Diagnostic goal: Register resources as managed beans with destruction callbacks.

### Buggy code

```java
@Bean ExecutorService executor() { return Executors.newFixedThreadPool(4); }
```

### Expected diagnosis

The container does not know how to stop an arbitrary resource unless destruction is declared.

### Corrected code

```java
@Bean(destroyMethod = "shutdown") ExecutorService executor() { return Executors.newFixedThreadPool(4); }
```

### Regression tests

```java
// Context close invokes shutdown.
```

## IOC-M-018: listener order assumed

- Difficulty: Medium
- Framework: Spring Core & Inversion of Control
- Language: Java
- Perspective: Ordering
- Concept: listener order assumed
- Symptom: Two startup tasks run in the wrong order.
- Diagnostic goal: Declare ordering only where the dependency is real.

### Buggy code

```java
@EventListener
void seed() {}
@EventListener
void publish() {}
```

### Expected diagnosis

Listener registration order is not a reliable dependency contract.

### Corrected code

```java
@Order(1) @EventListener void seed() {}
@Order(2) @EventListener void publish() {}
```

### Regression tests

```java
// The test records seed before publish.
```

## IOC-M-019: optional bean treated as required

- Difficulty: Medium
- Framework: Spring Core & Inversion of Control
- Language: Java
- Perspective: Optional dependencies
- Concept: optional bean treated as required
- Symptom: A feature cannot start without an optional integration.
- Diagnostic goal: Represent optionality explicitly.

### Buggy code

```java
public Reporter(Exporter exporter) { this.exporter = exporter; }
```

### Expected diagnosis

Constructor injection requires Exporter even when the feature is disabled.

### Corrected code

```java
public Reporter(ObjectProvider<Exporter> exporter) { this.exporter = exporter; }
```

### Regression tests

```java
// Reporter starts without Exporter and uses a no-op path.
```

## IOC-M-020: service cycle hidden by field injection

- Difficulty: Medium
- Framework: Spring Core & Inversion of Control
- Language: Java
- Perspective: Circular design
- Concept: service cycle hidden by field injection
- Symptom: Runtime behavior is order-dependent and difficult to test.
- Diagnostic goal: Extract a port or move orchestration into a third component.

### Buggy code

```java
@Autowired A a;
class A { @Autowired B b; }
class B { @Autowired A a; }
```

### Expected diagnosis

Field injection hides the cycle until context creation and makes dependencies mutable.

### Corrected code

```java
class Orchestrator { Orchestrator(A a, B b) {} }
```

### Regression tests

```java
// A and B no longer depend directly on one another.
```

## IOC-M-021: prototype injected into singleton

- Difficulty: Medium
- Framework: Spring Core & Inversion of Control
- Language: Java
- Perspective: Bean lifecycle
- Concept: prototype injected into singleton
- Symptom: A supposed new object is reused.
- Diagnostic goal: Obtain shorter-lived beans through a provider or scoped proxy.

### Buggy code

```java
@Component
class JobRunner { private final Job job; JobRunner(Job job) { this.job = job; } }
```

### Expected diagnosis

A prototype dependency is resolved once when the singleton is constructed.

### Corrected code

```java
@Component
class JobRunner { private final ObjectProvider<Job> jobs; JobRunner(ObjectProvider<Job> jobs) { this.jobs = jobs; }
 Job next() { return jobs.getObject(); } }
```

### Regression tests

```java
// Two calls to next return distinct Job instances.
```

## IOC-M-022: multiple candidates ambiguous

- Difficulty: Medium
- Framework: Spring Core & Inversion of Control
- Language: Java
- Perspective: Injection
- Concept: multiple candidates ambiguous
- Symptom: Context startup reports NoUniqueBeanDefinitionException.
- Diagnostic goal: Qualify the intended implementation or define a primary bean.

### Buggy code

```java
@Bean PaymentGateway stripe() { return new StripeGateway(); }
@Bean PaymentGateway bank() { return new BankGateway(); }
@Service Checkout(PaymentGateway gateway) {}
```

### Expected diagnosis

The injection point has two candidates and no selection rule.

### Corrected code

```java
@Service Checkout(@Qualifier("stripe") PaymentGateway gateway) {}
```

### Regression tests

```java
// Context chooses Stripe only at the qualified injection point.
```

## IOC-M-023: self-invocation bypasses advice

- Difficulty: Medium
- Framework: Spring Core & Inversion of Control
- Language: Java
- Perspective: Proxying
- Concept: self-invocation bypasses advice
- Symptom: The transactional or cached annotation appears ignored.
- Diagnostic goal: Call the advised method through the proxy boundary.

### Buggy code

```java
@Transactional
public void outer() { inner(); }
@Transactional
public void inner() { /* work */ }
```

### Expected diagnosis

A direct this.inner() call never passes through the Spring proxy.

### Corrected code

```java
@Transactional
public void outer() { collaborator.inner(); }
```

### Regression tests

```java
// An integration test observes the transaction/caching advice on inner.
```

## IOC-M-024: request bean used outside request

- Difficulty: Medium
- Framework: Spring Core & Inversion of Control
- Language: Java
- Perspective: Scopes
- Concept: request bean used outside request
- Symptom: A background task throws scope-not-active.
- Diagnostic goal: Capture immutable data, not a request-scoped object, for background work.

### Buggy code

```java
executor.submit(() -> requestContext.getUserId());
```

### Expected diagnosis

The request scope may be gone when the task runs.

### Corrected code

```java
String userId = requestContext.getUserId();
executor.submit(() -> process(userId));
```

### Regression tests

```java
// The task remains valid after the request completes.
```

## IOC-M-025: event published before commit

- Difficulty: Medium
- Framework: Spring Core & Inversion of Control
- Language: Java
- Perspective: Events
- Concept: event published before commit
- Symptom: A listener sees data that later rolls back.
- Diagnostic goal: Publish after a successful transaction commit when required.

### Buggy code

```java
publisher.publishEvent(new OrderCreated(order.id()));
repository.save(order);
```

### Expected diagnosis

The event is emitted before persistence commits and may describe a transaction that fails.

### Corrected code

```java
repository.save(order);
publisher.publishEvent(new OrderCreated(order.id()));
```

### Regression tests

```java
// A transactional listener receives the event only after commit.
```

## IOC-M-026: conditional bean unexpectedly absent

- Difficulty: Medium
- Framework: Spring Core & Inversion of Control
- Language: Java
- Perspective: Factory
- Concept: conditional bean unexpectedly absent
- Symptom: A feature flag has no implementation.
- Diagnostic goal: Check condition names and the effective environment.

### Buggy code

```java
@ConditionalOnProperty(name = "feature.mail")
@Bean Mailer mailer() { return new Mailer(); }
```

### Expected diagnosis

The condition requires a value unless havingValue or matchIfMissing is configured as intended.

### Corrected code

```java
@ConditionalOnProperty(name = "feature.mail", havingValue = "true")
@Bean Mailer mailer() { return new Mailer(); }
```

### Regression tests

```java
// Context reports a bean only when feature.mail=true.
```

## IOC-M-027: close omitted

- Difficulty: Medium
- Framework: Spring Core & Inversion of Control
- Language: Java
- Perspective: Resource lifecycle
- Concept: close omitted
- Symptom: Threads or connections remain after context shutdown.
- Diagnostic goal: Register resources as managed beans with destruction callbacks.

### Buggy code

```java
@Bean ExecutorService executor() { return Executors.newFixedThreadPool(4); }
```

### Expected diagnosis

The container does not know how to stop an arbitrary resource unless destruction is declared.

### Corrected code

```java
@Bean(destroyMethod = "shutdown") ExecutorService executor() { return Executors.newFixedThreadPool(4); }
```

### Regression tests

```java
// Context close invokes shutdown.
```

## IOC-M-028: listener order assumed

- Difficulty: Medium
- Framework: Spring Core & Inversion of Control
- Language: Java
- Perspective: Ordering
- Concept: listener order assumed
- Symptom: Two startup tasks run in the wrong order.
- Diagnostic goal: Declare ordering only where the dependency is real.

### Buggy code

```java
@EventListener
void seed() {}
@EventListener
void publish() {}
```

### Expected diagnosis

Listener registration order is not a reliable dependency contract.

### Corrected code

```java
@Order(1) @EventListener void seed() {}
@Order(2) @EventListener void publish() {}
```

### Regression tests

```java
// The test records seed before publish.
```

## IOC-M-029: optional bean treated as required

- Difficulty: Medium
- Framework: Spring Core & Inversion of Control
- Language: Java
- Perspective: Optional dependencies
- Concept: optional bean treated as required
- Symptom: A feature cannot start without an optional integration.
- Diagnostic goal: Represent optionality explicitly.

### Buggy code

```java
public Reporter(Exporter exporter) { this.exporter = exporter; }
```

### Expected diagnosis

Constructor injection requires Exporter even when the feature is disabled.

### Corrected code

```java
public Reporter(ObjectProvider<Exporter> exporter) { this.exporter = exporter; }
```

### Regression tests

```java
// Reporter starts without Exporter and uses a no-op path.
```

## IOC-M-030: service cycle hidden by field injection

- Difficulty: Medium
- Framework: Spring Core & Inversion of Control
- Language: Java
- Perspective: Circular design
- Concept: service cycle hidden by field injection
- Symptom: Runtime behavior is order-dependent and difficult to test.
- Diagnostic goal: Extract a port or move orchestration into a third component.

### Buggy code

```java
@Autowired A a;
class A { @Autowired B b; }
class B { @Autowired A a; }
```

### Expected diagnosis

Field injection hides the cycle until context creation and makes dependencies mutable.

### Corrected code

```java
class Orchestrator { Orchestrator(A a, B b) {} }
```

### Regression tests

```java
// A and B no longer depend directly on one another.
```

## IOC-M-031: prototype injected into singleton

- Difficulty: Medium
- Framework: Spring Core & Inversion of Control
- Language: Java
- Perspective: Bean lifecycle
- Concept: prototype injected into singleton
- Symptom: A supposed new object is reused.
- Diagnostic goal: Obtain shorter-lived beans through a provider or scoped proxy.

### Buggy code

```java
@Component
class JobRunner { private final Job job; JobRunner(Job job) { this.job = job; } }
```

### Expected diagnosis

A prototype dependency is resolved once when the singleton is constructed.

### Corrected code

```java
@Component
class JobRunner { private final ObjectProvider<Job> jobs; JobRunner(ObjectProvider<Job> jobs) { this.jobs = jobs; }
 Job next() { return jobs.getObject(); } }
```

### Regression tests

```java
// Two calls to next return distinct Job instances.
```

## IOC-M-032: multiple candidates ambiguous

- Difficulty: Medium
- Framework: Spring Core & Inversion of Control
- Language: Java
- Perspective: Injection
- Concept: multiple candidates ambiguous
- Symptom: Context startup reports NoUniqueBeanDefinitionException.
- Diagnostic goal: Qualify the intended implementation or define a primary bean.

### Buggy code

```java
@Bean PaymentGateway stripe() { return new StripeGateway(); }
@Bean PaymentGateway bank() { return new BankGateway(); }
@Service Checkout(PaymentGateway gateway) {}
```

### Expected diagnosis

The injection point has two candidates and no selection rule.

### Corrected code

```java
@Service Checkout(@Qualifier("stripe") PaymentGateway gateway) {}
```

### Regression tests

```java
// Context chooses Stripe only at the qualified injection point.
```

## IOC-M-033: self-invocation bypasses advice

- Difficulty: Medium
- Framework: Spring Core & Inversion of Control
- Language: Java
- Perspective: Proxying
- Concept: self-invocation bypasses advice
- Symptom: The transactional or cached annotation appears ignored.
- Diagnostic goal: Call the advised method through the proxy boundary.

### Buggy code

```java
@Transactional
public void outer() { inner(); }
@Transactional
public void inner() { /* work */ }
```

### Expected diagnosis

A direct this.inner() call never passes through the Spring proxy.

### Corrected code

```java
@Transactional
public void outer() { collaborator.inner(); }
```

### Regression tests

```java
// An integration test observes the transaction/caching advice on inner.
```

## IOC-M-034: request bean used outside request

- Difficulty: Medium
- Framework: Spring Core & Inversion of Control
- Language: Java
- Perspective: Scopes
- Concept: request bean used outside request
- Symptom: A background task throws scope-not-active.
- Diagnostic goal: Capture immutable data, not a request-scoped object, for background work.

### Buggy code

```java
executor.submit(() -> requestContext.getUserId());
```

### Expected diagnosis

The request scope may be gone when the task runs.

### Corrected code

```java
String userId = requestContext.getUserId();
executor.submit(() -> process(userId));
```

### Regression tests

```java
// The task remains valid after the request completes.
```

## IOC-M-035: event published before commit

- Difficulty: Medium
- Framework: Spring Core & Inversion of Control
- Language: Java
- Perspective: Events
- Concept: event published before commit
- Symptom: A listener sees data that later rolls back.
- Diagnostic goal: Publish after a successful transaction commit when required.

### Buggy code

```java
publisher.publishEvent(new OrderCreated(order.id()));
repository.save(order);
```

### Expected diagnosis

The event is emitted before persistence commits and may describe a transaction that fails.

### Corrected code

```java
repository.save(order);
publisher.publishEvent(new OrderCreated(order.id()));
```

### Regression tests

```java
// A transactional listener receives the event only after commit.
```

## IOC-M-036: conditional bean unexpectedly absent

- Difficulty: Medium
- Framework: Spring Core & Inversion of Control
- Language: Java
- Perspective: Factory
- Concept: conditional bean unexpectedly absent
- Symptom: A feature flag has no implementation.
- Diagnostic goal: Check condition names and the effective environment.

### Buggy code

```java
@ConditionalOnProperty(name = "feature.mail")
@Bean Mailer mailer() { return new Mailer(); }
```

### Expected diagnosis

The condition requires a value unless havingValue or matchIfMissing is configured as intended.

### Corrected code

```java
@ConditionalOnProperty(name = "feature.mail", havingValue = "true")
@Bean Mailer mailer() { return new Mailer(); }
```

### Regression tests

```java
// Context reports a bean only when feature.mail=true.
```

## IOC-M-037: close omitted

- Difficulty: Medium
- Framework: Spring Core & Inversion of Control
- Language: Java
- Perspective: Resource lifecycle
- Concept: close omitted
- Symptom: Threads or connections remain after context shutdown.
- Diagnostic goal: Register resources as managed beans with destruction callbacks.

### Buggy code

```java
@Bean ExecutorService executor() { return Executors.newFixedThreadPool(4); }
```

### Expected diagnosis

The container does not know how to stop an arbitrary resource unless destruction is declared.

### Corrected code

```java
@Bean(destroyMethod = "shutdown") ExecutorService executor() { return Executors.newFixedThreadPool(4); }
```

### Regression tests

```java
// Context close invokes shutdown.
```

## IOC-M-038: listener order assumed

- Difficulty: Medium
- Framework: Spring Core & Inversion of Control
- Language: Java
- Perspective: Ordering
- Concept: listener order assumed
- Symptom: Two startup tasks run in the wrong order.
- Diagnostic goal: Declare ordering only where the dependency is real.

### Buggy code

```java
@EventListener
void seed() {}
@EventListener
void publish() {}
```

### Expected diagnosis

Listener registration order is not a reliable dependency contract.

### Corrected code

```java
@Order(1) @EventListener void seed() {}
@Order(2) @EventListener void publish() {}
```

### Regression tests

```java
// The test records seed before publish.
```

## IOC-M-039: optional bean treated as required

- Difficulty: Medium
- Framework: Spring Core & Inversion of Control
- Language: Java
- Perspective: Optional dependencies
- Concept: optional bean treated as required
- Symptom: A feature cannot start without an optional integration.
- Diagnostic goal: Represent optionality explicitly.

### Buggy code

```java
public Reporter(Exporter exporter) { this.exporter = exporter; }
```

### Expected diagnosis

Constructor injection requires Exporter even when the feature is disabled.

### Corrected code

```java
public Reporter(ObjectProvider<Exporter> exporter) { this.exporter = exporter; }
```

### Regression tests

```java
// Reporter starts without Exporter and uses a no-op path.
```

## IOC-M-040: service cycle hidden by field injection

- Difficulty: Medium
- Framework: Spring Core & Inversion of Control
- Language: Java
- Perspective: Circular design
- Concept: service cycle hidden by field injection
- Symptom: Runtime behavior is order-dependent and difficult to test.
- Diagnostic goal: Extract a port or move orchestration into a third component.

### Buggy code

```java
@Autowired A a;
class A { @Autowired B b; }
class B { @Autowired A a; }
```

### Expected diagnosis

Field injection hides the cycle until context creation and makes dependencies mutable.

### Corrected code

```java
class Orchestrator { Orchestrator(A a, B b) {} }
```

### Regression tests

```java
// A and B no longer depend directly on one another.
```

## IOC-M-041: prototype injected into singleton

- Difficulty: Medium
- Framework: Spring Core & Inversion of Control
- Language: Java
- Perspective: Bean lifecycle
- Concept: prototype injected into singleton
- Symptom: A supposed new object is reused.
- Diagnostic goal: Obtain shorter-lived beans through a provider or scoped proxy.

### Buggy code

```java
@Component
class JobRunner { private final Job job; JobRunner(Job job) { this.job = job; } }
```

### Expected diagnosis

A prototype dependency is resolved once when the singleton is constructed.

### Corrected code

```java
@Component
class JobRunner { private final ObjectProvider<Job> jobs; JobRunner(ObjectProvider<Job> jobs) { this.jobs = jobs; }
 Job next() { return jobs.getObject(); } }
```

### Regression tests

```java
// Two calls to next return distinct Job instances.
```

## IOC-M-042: multiple candidates ambiguous

- Difficulty: Medium
- Framework: Spring Core & Inversion of Control
- Language: Java
- Perspective: Injection
- Concept: multiple candidates ambiguous
- Symptom: Context startup reports NoUniqueBeanDefinitionException.
- Diagnostic goal: Qualify the intended implementation or define a primary bean.

### Buggy code

```java
@Bean PaymentGateway stripe() { return new StripeGateway(); }
@Bean PaymentGateway bank() { return new BankGateway(); }
@Service Checkout(PaymentGateway gateway) {}
```

### Expected diagnosis

The injection point has two candidates and no selection rule.

### Corrected code

```java
@Service Checkout(@Qualifier("stripe") PaymentGateway gateway) {}
```

### Regression tests

```java
// Context chooses Stripe only at the qualified injection point.
```

## IOC-M-043: self-invocation bypasses advice

- Difficulty: Medium
- Framework: Spring Core & Inversion of Control
- Language: Java
- Perspective: Proxying
- Concept: self-invocation bypasses advice
- Symptom: The transactional or cached annotation appears ignored.
- Diagnostic goal: Call the advised method through the proxy boundary.

### Buggy code

```java
@Transactional
public void outer() { inner(); }
@Transactional
public void inner() { /* work */ }
```

### Expected diagnosis

A direct this.inner() call never passes through the Spring proxy.

### Corrected code

```java
@Transactional
public void outer() { collaborator.inner(); }
```

### Regression tests

```java
// An integration test observes the transaction/caching advice on inner.
```

## IOC-M-044: request bean used outside request

- Difficulty: Medium
- Framework: Spring Core & Inversion of Control
- Language: Java
- Perspective: Scopes
- Concept: request bean used outside request
- Symptom: A background task throws scope-not-active.
- Diagnostic goal: Capture immutable data, not a request-scoped object, for background work.

### Buggy code

```java
executor.submit(() -> requestContext.getUserId());
```

### Expected diagnosis

The request scope may be gone when the task runs.

### Corrected code

```java
String userId = requestContext.getUserId();
executor.submit(() -> process(userId));
```

### Regression tests

```java
// The task remains valid after the request completes.
```

## IOC-M-045: event published before commit

- Difficulty: Medium
- Framework: Spring Core & Inversion of Control
- Language: Java
- Perspective: Events
- Concept: event published before commit
- Symptom: A listener sees data that later rolls back.
- Diagnostic goal: Publish after a successful transaction commit when required.

### Buggy code

```java
publisher.publishEvent(new OrderCreated(order.id()));
repository.save(order);
```

### Expected diagnosis

The event is emitted before persistence commits and may describe a transaction that fails.

### Corrected code

```java
repository.save(order);
publisher.publishEvent(new OrderCreated(order.id()));
```

### Regression tests

```java
// A transactional listener receives the event only after commit.
```

## IOC-M-046: conditional bean unexpectedly absent

- Difficulty: Medium
- Framework: Spring Core & Inversion of Control
- Language: Java
- Perspective: Factory
- Concept: conditional bean unexpectedly absent
- Symptom: A feature flag has no implementation.
- Diagnostic goal: Check condition names and the effective environment.

### Buggy code

```java
@ConditionalOnProperty(name = "feature.mail")
@Bean Mailer mailer() { return new Mailer(); }
```

### Expected diagnosis

The condition requires a value unless havingValue or matchIfMissing is configured as intended.

### Corrected code

```java
@ConditionalOnProperty(name = "feature.mail", havingValue = "true")
@Bean Mailer mailer() { return new Mailer(); }
```

### Regression tests

```java
// Context reports a bean only when feature.mail=true.
```

## IOC-M-047: close omitted

- Difficulty: Medium
- Framework: Spring Core & Inversion of Control
- Language: Java
- Perspective: Resource lifecycle
- Concept: close omitted
- Symptom: Threads or connections remain after context shutdown.
- Diagnostic goal: Register resources as managed beans with destruction callbacks.

### Buggy code

```java
@Bean ExecutorService executor() { return Executors.newFixedThreadPool(4); }
```

### Expected diagnosis

The container does not know how to stop an arbitrary resource unless destruction is declared.

### Corrected code

```java
@Bean(destroyMethod = "shutdown") ExecutorService executor() { return Executors.newFixedThreadPool(4); }
```

### Regression tests

```java
// Context close invokes shutdown.
```

## IOC-M-048: listener order assumed

- Difficulty: Medium
- Framework: Spring Core & Inversion of Control
- Language: Java
- Perspective: Ordering
- Concept: listener order assumed
- Symptom: Two startup tasks run in the wrong order.
- Diagnostic goal: Declare ordering only where the dependency is real.

### Buggy code

```java
@EventListener
void seed() {}
@EventListener
void publish() {}
```

### Expected diagnosis

Listener registration order is not a reliable dependency contract.

### Corrected code

```java
@Order(1) @EventListener void seed() {}
@Order(2) @EventListener void publish() {}
```

### Regression tests

```java
// The test records seed before publish.
```

## IOC-M-049: optional bean treated as required

- Difficulty: Medium
- Framework: Spring Core & Inversion of Control
- Language: Java
- Perspective: Optional dependencies
- Concept: optional bean treated as required
- Symptom: A feature cannot start without an optional integration.
- Diagnostic goal: Represent optionality explicitly.

### Buggy code

```java
public Reporter(Exporter exporter) { this.exporter = exporter; }
```

### Expected diagnosis

Constructor injection requires Exporter even when the feature is disabled.

### Corrected code

```java
public Reporter(ObjectProvider<Exporter> exporter) { this.exporter = exporter; }
```

### Regression tests

```java
// Reporter starts without Exporter and uses a no-op path.
```

## IOC-M-050: service cycle hidden by field injection

- Difficulty: Medium
- Framework: Spring Core & Inversion of Control
- Language: Java
- Perspective: Circular design
- Concept: service cycle hidden by field injection
- Symptom: Runtime behavior is order-dependent and difficult to test.
- Diagnostic goal: Extract a port or move orchestration into a third component.

### Buggy code

```java
@Autowired A a;
class A { @Autowired B b; }
class B { @Autowired A a; }
```

### Expected diagnosis

Field injection hides the cycle until context creation and makes dependencies mutable.

### Corrected code

```java
class Orchestrator { Orchestrator(A a, B b) {} }
```

### Regression tests

```java
// A and B no longer depend directly on one another.
```

## IOC-M-051: prototype injected into singleton

- Difficulty: Medium
- Framework: Spring Core & Inversion of Control
- Language: Java
- Perspective: Bean lifecycle
- Concept: prototype injected into singleton
- Symptom: A supposed new object is reused.
- Diagnostic goal: Obtain shorter-lived beans through a provider or scoped proxy.

### Buggy code

```java
@Component
class JobRunner { private final Job job; JobRunner(Job job) { this.job = job; } }
```

### Expected diagnosis

A prototype dependency is resolved once when the singleton is constructed.

### Corrected code

```java
@Component
class JobRunner { private final ObjectProvider<Job> jobs; JobRunner(ObjectProvider<Job> jobs) { this.jobs = jobs; }
 Job next() { return jobs.getObject(); } }
```

### Regression tests

```java
// Two calls to next return distinct Job instances.
```

## IOC-M-052: multiple candidates ambiguous

- Difficulty: Medium
- Framework: Spring Core & Inversion of Control
- Language: Java
- Perspective: Injection
- Concept: multiple candidates ambiguous
- Symptom: Context startup reports NoUniqueBeanDefinitionException.
- Diagnostic goal: Qualify the intended implementation or define a primary bean.

### Buggy code

```java
@Bean PaymentGateway stripe() { return new StripeGateway(); }
@Bean PaymentGateway bank() { return new BankGateway(); }
@Service Checkout(PaymentGateway gateway) {}
```

### Expected diagnosis

The injection point has two candidates and no selection rule.

### Corrected code

```java
@Service Checkout(@Qualifier("stripe") PaymentGateway gateway) {}
```

### Regression tests

```java
// Context chooses Stripe only at the qualified injection point.
```

## IOC-M-053: self-invocation bypasses advice

- Difficulty: Medium
- Framework: Spring Core & Inversion of Control
- Language: Java
- Perspective: Proxying
- Concept: self-invocation bypasses advice
- Symptom: The transactional or cached annotation appears ignored.
- Diagnostic goal: Call the advised method through the proxy boundary.

### Buggy code

```java
@Transactional
public void outer() { inner(); }
@Transactional
public void inner() { /* work */ }
```

### Expected diagnosis

A direct this.inner() call never passes through the Spring proxy.

### Corrected code

```java
@Transactional
public void outer() { collaborator.inner(); }
```

### Regression tests

```java
// An integration test observes the transaction/caching advice on inner.
```

## IOC-M-054: request bean used outside request

- Difficulty: Medium
- Framework: Spring Core & Inversion of Control
- Language: Java
- Perspective: Scopes
- Concept: request bean used outside request
- Symptom: A background task throws scope-not-active.
- Diagnostic goal: Capture immutable data, not a request-scoped object, for background work.

### Buggy code

```java
executor.submit(() -> requestContext.getUserId());
```

### Expected diagnosis

The request scope may be gone when the task runs.

### Corrected code

```java
String userId = requestContext.getUserId();
executor.submit(() -> process(userId));
```

### Regression tests

```java
// The task remains valid after the request completes.
```

## IOC-M-055: event published before commit

- Difficulty: Medium
- Framework: Spring Core & Inversion of Control
- Language: Java
- Perspective: Events
- Concept: event published before commit
- Symptom: A listener sees data that later rolls back.
- Diagnostic goal: Publish after a successful transaction commit when required.

### Buggy code

```java
publisher.publishEvent(new OrderCreated(order.id()));
repository.save(order);
```

### Expected diagnosis

The event is emitted before persistence commits and may describe a transaction that fails.

### Corrected code

```java
repository.save(order);
publisher.publishEvent(new OrderCreated(order.id()));
```

### Regression tests

```java
// A transactional listener receives the event only after commit.
```

## IOC-M-056: conditional bean unexpectedly absent

- Difficulty: Medium
- Framework: Spring Core & Inversion of Control
- Language: Java
- Perspective: Factory
- Concept: conditional bean unexpectedly absent
- Symptom: A feature flag has no implementation.
- Diagnostic goal: Check condition names and the effective environment.

### Buggy code

```java
@ConditionalOnProperty(name = "feature.mail")
@Bean Mailer mailer() { return new Mailer(); }
```

### Expected diagnosis

The condition requires a value unless havingValue or matchIfMissing is configured as intended.

### Corrected code

```java
@ConditionalOnProperty(name = "feature.mail", havingValue = "true")
@Bean Mailer mailer() { return new Mailer(); }
```

### Regression tests

```java
// Context reports a bean only when feature.mail=true.
```

## IOC-M-057: close omitted

- Difficulty: Medium
- Framework: Spring Core & Inversion of Control
- Language: Java
- Perspective: Resource lifecycle
- Concept: close omitted
- Symptom: Threads or connections remain after context shutdown.
- Diagnostic goal: Register resources as managed beans with destruction callbacks.

### Buggy code

```java
@Bean ExecutorService executor() { return Executors.newFixedThreadPool(4); }
```

### Expected diagnosis

The container does not know how to stop an arbitrary resource unless destruction is declared.

### Corrected code

```java
@Bean(destroyMethod = "shutdown") ExecutorService executor() { return Executors.newFixedThreadPool(4); }
```

### Regression tests

```java
// Context close invokes shutdown.
```

## IOC-M-058: listener order assumed

- Difficulty: Medium
- Framework: Spring Core & Inversion of Control
- Language: Java
- Perspective: Ordering
- Concept: listener order assumed
- Symptom: Two startup tasks run in the wrong order.
- Diagnostic goal: Declare ordering only where the dependency is real.

### Buggy code

```java
@EventListener
void seed() {}
@EventListener
void publish() {}
```

### Expected diagnosis

Listener registration order is not a reliable dependency contract.

### Corrected code

```java
@Order(1) @EventListener void seed() {}
@Order(2) @EventListener void publish() {}
```

### Regression tests

```java
// The test records seed before publish.
```

## IOC-M-059: optional bean treated as required

- Difficulty: Medium
- Framework: Spring Core & Inversion of Control
- Language: Java
- Perspective: Optional dependencies
- Concept: optional bean treated as required
- Symptom: A feature cannot start without an optional integration.
- Diagnostic goal: Represent optionality explicitly.

### Buggy code

```java
public Reporter(Exporter exporter) { this.exporter = exporter; }
```

### Expected diagnosis

Constructor injection requires Exporter even when the feature is disabled.

### Corrected code

```java
public Reporter(ObjectProvider<Exporter> exporter) { this.exporter = exporter; }
```

### Regression tests

```java
// Reporter starts without Exporter and uses a no-op path.
```

## IOC-M-060: service cycle hidden by field injection

- Difficulty: Medium
- Framework: Spring Core & Inversion of Control
- Language: Java
- Perspective: Circular design
- Concept: service cycle hidden by field injection
- Symptom: Runtime behavior is order-dependent and difficult to test.
- Diagnostic goal: Extract a port or move orchestration into a third component.

### Buggy code

```java
@Autowired A a;
class A { @Autowired B b; }
class B { @Autowired A a; }
```

### Expected diagnosis

Field injection hides the cycle until context creation and makes dependencies mutable.

### Corrected code

```java
class Orchestrator { Orchestrator(A a, B b) {} }
```

### Regression tests

```java
// A and B no longer depend directly on one another.
```

## IOC-M-061: prototype injected into singleton

- Difficulty: Medium
- Framework: Spring Core & Inversion of Control
- Language: Java
- Perspective: Bean lifecycle
- Concept: prototype injected into singleton
- Symptom: A supposed new object is reused.
- Diagnostic goal: Obtain shorter-lived beans through a provider or scoped proxy.

### Buggy code

```java
@Component
class JobRunner { private final Job job; JobRunner(Job job) { this.job = job; } }
```

### Expected diagnosis

A prototype dependency is resolved once when the singleton is constructed.

### Corrected code

```java
@Component
class JobRunner { private final ObjectProvider<Job> jobs; JobRunner(ObjectProvider<Job> jobs) { this.jobs = jobs; }
 Job next() { return jobs.getObject(); } }
```

### Regression tests

```java
// Two calls to next return distinct Job instances.
```

## IOC-M-062: multiple candidates ambiguous

- Difficulty: Medium
- Framework: Spring Core & Inversion of Control
- Language: Java
- Perspective: Injection
- Concept: multiple candidates ambiguous
- Symptom: Context startup reports NoUniqueBeanDefinitionException.
- Diagnostic goal: Qualify the intended implementation or define a primary bean.

### Buggy code

```java
@Bean PaymentGateway stripe() { return new StripeGateway(); }
@Bean PaymentGateway bank() { return new BankGateway(); }
@Service Checkout(PaymentGateway gateway) {}
```

### Expected diagnosis

The injection point has two candidates and no selection rule.

### Corrected code

```java
@Service Checkout(@Qualifier("stripe") PaymentGateway gateway) {}
```

### Regression tests

```java
// Context chooses Stripe only at the qualified injection point.
```

## IOC-M-063: self-invocation bypasses advice

- Difficulty: Medium
- Framework: Spring Core & Inversion of Control
- Language: Java
- Perspective: Proxying
- Concept: self-invocation bypasses advice
- Symptom: The transactional or cached annotation appears ignored.
- Diagnostic goal: Call the advised method through the proxy boundary.

### Buggy code

```java
@Transactional
public void outer() { inner(); }
@Transactional
public void inner() { /* work */ }
```

### Expected diagnosis

A direct this.inner() call never passes through the Spring proxy.

### Corrected code

```java
@Transactional
public void outer() { collaborator.inner(); }
```

### Regression tests

```java
// An integration test observes the transaction/caching advice on inner.
```

## IOC-M-064: request bean used outside request

- Difficulty: Medium
- Framework: Spring Core & Inversion of Control
- Language: Java
- Perspective: Scopes
- Concept: request bean used outside request
- Symptom: A background task throws scope-not-active.
- Diagnostic goal: Capture immutable data, not a request-scoped object, for background work.

### Buggy code

```java
executor.submit(() -> requestContext.getUserId());
```

### Expected diagnosis

The request scope may be gone when the task runs.

### Corrected code

```java
String userId = requestContext.getUserId();
executor.submit(() -> process(userId));
```

### Regression tests

```java
// The task remains valid after the request completes.
```

## IOC-M-065: event published before commit

- Difficulty: Medium
- Framework: Spring Core & Inversion of Control
- Language: Java
- Perspective: Events
- Concept: event published before commit
- Symptom: A listener sees data that later rolls back.
- Diagnostic goal: Publish after a successful transaction commit when required.

### Buggy code

```java
publisher.publishEvent(new OrderCreated(order.id()));
repository.save(order);
```

### Expected diagnosis

The event is emitted before persistence commits and may describe a transaction that fails.

### Corrected code

```java
repository.save(order);
publisher.publishEvent(new OrderCreated(order.id()));
```

### Regression tests

```java
// A transactional listener receives the event only after commit.
```

## IOC-M-066: conditional bean unexpectedly absent

- Difficulty: Medium
- Framework: Spring Core & Inversion of Control
- Language: Java
- Perspective: Factory
- Concept: conditional bean unexpectedly absent
- Symptom: A feature flag has no implementation.
- Diagnostic goal: Check condition names and the effective environment.

### Buggy code

```java
@ConditionalOnProperty(name = "feature.mail")
@Bean Mailer mailer() { return new Mailer(); }
```

### Expected diagnosis

The condition requires a value unless havingValue or matchIfMissing is configured as intended.

### Corrected code

```java
@ConditionalOnProperty(name = "feature.mail", havingValue = "true")
@Bean Mailer mailer() { return new Mailer(); }
```

### Regression tests

```java
// Context reports a bean only when feature.mail=true.
```

## IOC-M-067: close omitted

- Difficulty: Medium
- Framework: Spring Core & Inversion of Control
- Language: Java
- Perspective: Resource lifecycle
- Concept: close omitted
- Symptom: Threads or connections remain after context shutdown.
- Diagnostic goal: Register resources as managed beans with destruction callbacks.

### Buggy code

```java
@Bean ExecutorService executor() { return Executors.newFixedThreadPool(4); }
```

### Expected diagnosis

The container does not know how to stop an arbitrary resource unless destruction is declared.

### Corrected code

```java
@Bean(destroyMethod = "shutdown") ExecutorService executor() { return Executors.newFixedThreadPool(4); }
```

### Regression tests

```java
// Context close invokes shutdown.
```

## IOC-M-068: listener order assumed

- Difficulty: Medium
- Framework: Spring Core & Inversion of Control
- Language: Java
- Perspective: Ordering
- Concept: listener order assumed
- Symptom: Two startup tasks run in the wrong order.
- Diagnostic goal: Declare ordering only where the dependency is real.

### Buggy code

```java
@EventListener
void seed() {}
@EventListener
void publish() {}
```

### Expected diagnosis

Listener registration order is not a reliable dependency contract.

### Corrected code

```java
@Order(1) @EventListener void seed() {}
@Order(2) @EventListener void publish() {}
```

### Regression tests

```java
// The test records seed before publish.
```

## IOC-M-069: optional bean treated as required

- Difficulty: Medium
- Framework: Spring Core & Inversion of Control
- Language: Java
- Perspective: Optional dependencies
- Concept: optional bean treated as required
- Symptom: A feature cannot start without an optional integration.
- Diagnostic goal: Represent optionality explicitly.

### Buggy code

```java
public Reporter(Exporter exporter) { this.exporter = exporter; }
```

### Expected diagnosis

Constructor injection requires Exporter even when the feature is disabled.

### Corrected code

```java
public Reporter(ObjectProvider<Exporter> exporter) { this.exporter = exporter; }
```

### Regression tests

```java
// Reporter starts without Exporter and uses a no-op path.
```

## IOC-M-070: service cycle hidden by field injection

- Difficulty: Medium
- Framework: Spring Core & Inversion of Control
- Language: Java
- Perspective: Circular design
- Concept: service cycle hidden by field injection
- Symptom: Runtime behavior is order-dependent and difficult to test.
- Diagnostic goal: Extract a port or move orchestration into a third component.

### Buggy code

```java
@Autowired A a;
class A { @Autowired B b; }
class B { @Autowired A a; }
```

### Expected diagnosis

Field injection hides the cycle until context creation and makes dependencies mutable.

### Corrected code

```java
class Orchestrator { Orchestrator(A a, B b) {} }
```

### Regression tests

```java
// A and B no longer depend directly on one another.
```

## IOC-M-071: prototype injected into singleton

- Difficulty: Medium
- Framework: Spring Core & Inversion of Control
- Language: Java
- Perspective: Bean lifecycle
- Concept: prototype injected into singleton
- Symptom: A supposed new object is reused.
- Diagnostic goal: Obtain shorter-lived beans through a provider or scoped proxy.

### Buggy code

```java
@Component
class JobRunner { private final Job job; JobRunner(Job job) { this.job = job; } }
```

### Expected diagnosis

A prototype dependency is resolved once when the singleton is constructed.

### Corrected code

```java
@Component
class JobRunner { private final ObjectProvider<Job> jobs; JobRunner(ObjectProvider<Job> jobs) { this.jobs = jobs; }
 Job next() { return jobs.getObject(); } }
```

### Regression tests

```java
// Two calls to next return distinct Job instances.
```

## IOC-M-072: multiple candidates ambiguous

- Difficulty: Medium
- Framework: Spring Core & Inversion of Control
- Language: Java
- Perspective: Injection
- Concept: multiple candidates ambiguous
- Symptom: Context startup reports NoUniqueBeanDefinitionException.
- Diagnostic goal: Qualify the intended implementation or define a primary bean.

### Buggy code

```java
@Bean PaymentGateway stripe() { return new StripeGateway(); }
@Bean PaymentGateway bank() { return new BankGateway(); }
@Service Checkout(PaymentGateway gateway) {}
```

### Expected diagnosis

The injection point has two candidates and no selection rule.

### Corrected code

```java
@Service Checkout(@Qualifier("stripe") PaymentGateway gateway) {}
```

### Regression tests

```java
// Context chooses Stripe only at the qualified injection point.
```

## IOC-M-073: self-invocation bypasses advice

- Difficulty: Medium
- Framework: Spring Core & Inversion of Control
- Language: Java
- Perspective: Proxying
- Concept: self-invocation bypasses advice
- Symptom: The transactional or cached annotation appears ignored.
- Diagnostic goal: Call the advised method through the proxy boundary.

### Buggy code

```java
@Transactional
public void outer() { inner(); }
@Transactional
public void inner() { /* work */ }
```

### Expected diagnosis

A direct this.inner() call never passes through the Spring proxy.

### Corrected code

```java
@Transactional
public void outer() { collaborator.inner(); }
```

### Regression tests

```java
// An integration test observes the transaction/caching advice on inner.
```

## IOC-M-074: request bean used outside request

- Difficulty: Medium
- Framework: Spring Core & Inversion of Control
- Language: Java
- Perspective: Scopes
- Concept: request bean used outside request
- Symptom: A background task throws scope-not-active.
- Diagnostic goal: Capture immutable data, not a request-scoped object, for background work.

### Buggy code

```java
executor.submit(() -> requestContext.getUserId());
```

### Expected diagnosis

The request scope may be gone when the task runs.

### Corrected code

```java
String userId = requestContext.getUserId();
executor.submit(() -> process(userId));
```

### Regression tests

```java
// The task remains valid after the request completes.
```

## IOC-M-075: event published before commit

- Difficulty: Medium
- Framework: Spring Core & Inversion of Control
- Language: Java
- Perspective: Events
- Concept: event published before commit
- Symptom: A listener sees data that later rolls back.
- Diagnostic goal: Publish after a successful transaction commit when required.

### Buggy code

```java
publisher.publishEvent(new OrderCreated(order.id()));
repository.save(order);
```

### Expected diagnosis

The event is emitted before persistence commits and may describe a transaction that fails.

### Corrected code

```java
repository.save(order);
publisher.publishEvent(new OrderCreated(order.id()));
```

### Regression tests

```java
// A transactional listener receives the event only after commit.
```

## IOC-M-076: conditional bean unexpectedly absent

- Difficulty: Medium
- Framework: Spring Core & Inversion of Control
- Language: Java
- Perspective: Factory
- Concept: conditional bean unexpectedly absent
- Symptom: A feature flag has no implementation.
- Diagnostic goal: Check condition names and the effective environment.

### Buggy code

```java
@ConditionalOnProperty(name = "feature.mail")
@Bean Mailer mailer() { return new Mailer(); }
```

### Expected diagnosis

The condition requires a value unless havingValue or matchIfMissing is configured as intended.

### Corrected code

```java
@ConditionalOnProperty(name = "feature.mail", havingValue = "true")
@Bean Mailer mailer() { return new Mailer(); }
```

### Regression tests

```java
// Context reports a bean only when feature.mail=true.
```

## IOC-M-077: close omitted

- Difficulty: Medium
- Framework: Spring Core & Inversion of Control
- Language: Java
- Perspective: Resource lifecycle
- Concept: close omitted
- Symptom: Threads or connections remain after context shutdown.
- Diagnostic goal: Register resources as managed beans with destruction callbacks.

### Buggy code

```java
@Bean ExecutorService executor() { return Executors.newFixedThreadPool(4); }
```

### Expected diagnosis

The container does not know how to stop an arbitrary resource unless destruction is declared.

### Corrected code

```java
@Bean(destroyMethod = "shutdown") ExecutorService executor() { return Executors.newFixedThreadPool(4); }
```

### Regression tests

```java
// Context close invokes shutdown.
```

## IOC-M-078: listener order assumed

- Difficulty: Medium
- Framework: Spring Core & Inversion of Control
- Language: Java
- Perspective: Ordering
- Concept: listener order assumed
- Symptom: Two startup tasks run in the wrong order.
- Diagnostic goal: Declare ordering only where the dependency is real.

### Buggy code

```java
@EventListener
void seed() {}
@EventListener
void publish() {}
```

### Expected diagnosis

Listener registration order is not a reliable dependency contract.

### Corrected code

```java
@Order(1) @EventListener void seed() {}
@Order(2) @EventListener void publish() {}
```

### Regression tests

```java
// The test records seed before publish.
```

## IOC-M-079: optional bean treated as required

- Difficulty: Medium
- Framework: Spring Core & Inversion of Control
- Language: Java
- Perspective: Optional dependencies
- Concept: optional bean treated as required
- Symptom: A feature cannot start without an optional integration.
- Diagnostic goal: Represent optionality explicitly.

### Buggy code

```java
public Reporter(Exporter exporter) { this.exporter = exporter; }
```

### Expected diagnosis

Constructor injection requires Exporter even when the feature is disabled.

### Corrected code

```java
public Reporter(ObjectProvider<Exporter> exporter) { this.exporter = exporter; }
```

### Regression tests

```java
// Reporter starts without Exporter and uses a no-op path.
```

## IOC-M-080: service cycle hidden by field injection

- Difficulty: Medium
- Framework: Spring Core & Inversion of Control
- Language: Java
- Perspective: Circular design
- Concept: service cycle hidden by field injection
- Symptom: Runtime behavior is order-dependent and difficult to test.
- Diagnostic goal: Extract a port or move orchestration into a third component.

### Buggy code

```java
@Autowired A a;
class A { @Autowired B b; }
class B { @Autowired A a; }
```

### Expected diagnosis

Field injection hides the cycle until context creation and makes dependencies mutable.

### Corrected code

```java
class Orchestrator { Orchestrator(A a, B b) {} }
```

### Regression tests

```java
// A and B no longer depend directly on one another.
```

## IOC-M-081: prototype injected into singleton

- Difficulty: Medium
- Framework: Spring Core & Inversion of Control
- Language: Java
- Perspective: Bean lifecycle
- Concept: prototype injected into singleton
- Symptom: A supposed new object is reused.
- Diagnostic goal: Obtain shorter-lived beans through a provider or scoped proxy.

### Buggy code

```java
@Component
class JobRunner { private final Job job; JobRunner(Job job) { this.job = job; } }
```

### Expected diagnosis

A prototype dependency is resolved once when the singleton is constructed.

### Corrected code

```java
@Component
class JobRunner { private final ObjectProvider<Job> jobs; JobRunner(ObjectProvider<Job> jobs) { this.jobs = jobs; }
 Job next() { return jobs.getObject(); } }
```

### Regression tests

```java
// Two calls to next return distinct Job instances.
```

## IOC-M-082: multiple candidates ambiguous

- Difficulty: Medium
- Framework: Spring Core & Inversion of Control
- Language: Java
- Perspective: Injection
- Concept: multiple candidates ambiguous
- Symptom: Context startup reports NoUniqueBeanDefinitionException.
- Diagnostic goal: Qualify the intended implementation or define a primary bean.

### Buggy code

```java
@Bean PaymentGateway stripe() { return new StripeGateway(); }
@Bean PaymentGateway bank() { return new BankGateway(); }
@Service Checkout(PaymentGateway gateway) {}
```

### Expected diagnosis

The injection point has two candidates and no selection rule.

### Corrected code

```java
@Service Checkout(@Qualifier("stripe") PaymentGateway gateway) {}
```

### Regression tests

```java
// Context chooses Stripe only at the qualified injection point.
```

## IOC-M-083: self-invocation bypasses advice

- Difficulty: Medium
- Framework: Spring Core & Inversion of Control
- Language: Java
- Perspective: Proxying
- Concept: self-invocation bypasses advice
- Symptom: The transactional or cached annotation appears ignored.
- Diagnostic goal: Call the advised method through the proxy boundary.

### Buggy code

```java
@Transactional
public void outer() { inner(); }
@Transactional
public void inner() { /* work */ }
```

### Expected diagnosis

A direct this.inner() call never passes through the Spring proxy.

### Corrected code

```java
@Transactional
public void outer() { collaborator.inner(); }
```

### Regression tests

```java
// An integration test observes the transaction/caching advice on inner.
```

## IOC-M-084: request bean used outside request

- Difficulty: Medium
- Framework: Spring Core & Inversion of Control
- Language: Java
- Perspective: Scopes
- Concept: request bean used outside request
- Symptom: A background task throws scope-not-active.
- Diagnostic goal: Capture immutable data, not a request-scoped object, for background work.

### Buggy code

```java
executor.submit(() -> requestContext.getUserId());
```

### Expected diagnosis

The request scope may be gone when the task runs.

### Corrected code

```java
String userId = requestContext.getUserId();
executor.submit(() -> process(userId));
```

### Regression tests

```java
// The task remains valid after the request completes.
```

## IOC-M-085: event published before commit

- Difficulty: Medium
- Framework: Spring Core & Inversion of Control
- Language: Java
- Perspective: Events
- Concept: event published before commit
- Symptom: A listener sees data that later rolls back.
- Diagnostic goal: Publish after a successful transaction commit when required.

### Buggy code

```java
publisher.publishEvent(new OrderCreated(order.id()));
repository.save(order);
```

### Expected diagnosis

The event is emitted before persistence commits and may describe a transaction that fails.

### Corrected code

```java
repository.save(order);
publisher.publishEvent(new OrderCreated(order.id()));
```

### Regression tests

```java
// A transactional listener receives the event only after commit.
```

## IOC-M-086: conditional bean unexpectedly absent

- Difficulty: Medium
- Framework: Spring Core & Inversion of Control
- Language: Java
- Perspective: Factory
- Concept: conditional bean unexpectedly absent
- Symptom: A feature flag has no implementation.
- Diagnostic goal: Check condition names and the effective environment.

### Buggy code

```java
@ConditionalOnProperty(name = "feature.mail")
@Bean Mailer mailer() { return new Mailer(); }
```

### Expected diagnosis

The condition requires a value unless havingValue or matchIfMissing is configured as intended.

### Corrected code

```java
@ConditionalOnProperty(name = "feature.mail", havingValue = "true")
@Bean Mailer mailer() { return new Mailer(); }
```

### Regression tests

```java
// Context reports a bean only when feature.mail=true.
```

## IOC-M-087: close omitted

- Difficulty: Medium
- Framework: Spring Core & Inversion of Control
- Language: Java
- Perspective: Resource lifecycle
- Concept: close omitted
- Symptom: Threads or connections remain after context shutdown.
- Diagnostic goal: Register resources as managed beans with destruction callbacks.

### Buggy code

```java
@Bean ExecutorService executor() { return Executors.newFixedThreadPool(4); }
```

### Expected diagnosis

The container does not know how to stop an arbitrary resource unless destruction is declared.

### Corrected code

```java
@Bean(destroyMethod = "shutdown") ExecutorService executor() { return Executors.newFixedThreadPool(4); }
```

### Regression tests

```java
// Context close invokes shutdown.
```

## IOC-M-088: listener order assumed

- Difficulty: Medium
- Framework: Spring Core & Inversion of Control
- Language: Java
- Perspective: Ordering
- Concept: listener order assumed
- Symptom: Two startup tasks run in the wrong order.
- Diagnostic goal: Declare ordering only where the dependency is real.

### Buggy code

```java
@EventListener
void seed() {}
@EventListener
void publish() {}
```

### Expected diagnosis

Listener registration order is not a reliable dependency contract.

### Corrected code

```java
@Order(1) @EventListener void seed() {}
@Order(2) @EventListener void publish() {}
```

### Regression tests

```java
// The test records seed before publish.
```

## IOC-M-089: optional bean treated as required

- Difficulty: Medium
- Framework: Spring Core & Inversion of Control
- Language: Java
- Perspective: Optional dependencies
- Concept: optional bean treated as required
- Symptom: A feature cannot start without an optional integration.
- Diagnostic goal: Represent optionality explicitly.

### Buggy code

```java
public Reporter(Exporter exporter) { this.exporter = exporter; }
```

### Expected diagnosis

Constructor injection requires Exporter even when the feature is disabled.

### Corrected code

```java
public Reporter(ObjectProvider<Exporter> exporter) { this.exporter = exporter; }
```

### Regression tests

```java
// Reporter starts without Exporter and uses a no-op path.
```

## IOC-M-090: service cycle hidden by field injection

- Difficulty: Medium
- Framework: Spring Core & Inversion of Control
- Language: Java
- Perspective: Circular design
- Concept: service cycle hidden by field injection
- Symptom: Runtime behavior is order-dependent and difficult to test.
- Diagnostic goal: Extract a port or move orchestration into a third component.

### Buggy code

```java
@Autowired A a;
class A { @Autowired B b; }
class B { @Autowired A a; }
```

### Expected diagnosis

Field injection hides the cycle until context creation and makes dependencies mutable.

### Corrected code

```java
class Orchestrator { Orchestrator(A a, B b) {} }
```

### Regression tests

```java
// A and B no longer depend directly on one another.
```

## IOC-M-091: prototype injected into singleton

- Difficulty: Medium
- Framework: Spring Core & Inversion of Control
- Language: Java
- Perspective: Bean lifecycle
- Concept: prototype injected into singleton
- Symptom: A supposed new object is reused.
- Diagnostic goal: Obtain shorter-lived beans through a provider or scoped proxy.

### Buggy code

```java
@Component
class JobRunner { private final Job job; JobRunner(Job job) { this.job = job; } }
```

### Expected diagnosis

A prototype dependency is resolved once when the singleton is constructed.

### Corrected code

```java
@Component
class JobRunner { private final ObjectProvider<Job> jobs; JobRunner(ObjectProvider<Job> jobs) { this.jobs = jobs; }
 Job next() { return jobs.getObject(); } }
```

### Regression tests

```java
// Two calls to next return distinct Job instances.
```

## IOC-M-092: multiple candidates ambiguous

- Difficulty: Medium
- Framework: Spring Core & Inversion of Control
- Language: Java
- Perspective: Injection
- Concept: multiple candidates ambiguous
- Symptom: Context startup reports NoUniqueBeanDefinitionException.
- Diagnostic goal: Qualify the intended implementation or define a primary bean.

### Buggy code

```java
@Bean PaymentGateway stripe() { return new StripeGateway(); }
@Bean PaymentGateway bank() { return new BankGateway(); }
@Service Checkout(PaymentGateway gateway) {}
```

### Expected diagnosis

The injection point has two candidates and no selection rule.

### Corrected code

```java
@Service Checkout(@Qualifier("stripe") PaymentGateway gateway) {}
```

### Regression tests

```java
// Context chooses Stripe only at the qualified injection point.
```

## IOC-M-093: self-invocation bypasses advice

- Difficulty: Medium
- Framework: Spring Core & Inversion of Control
- Language: Java
- Perspective: Proxying
- Concept: self-invocation bypasses advice
- Symptom: The transactional or cached annotation appears ignored.
- Diagnostic goal: Call the advised method through the proxy boundary.

### Buggy code

```java
@Transactional
public void outer() { inner(); }
@Transactional
public void inner() { /* work */ }
```

### Expected diagnosis

A direct this.inner() call never passes through the Spring proxy.

### Corrected code

```java
@Transactional
public void outer() { collaborator.inner(); }
```

### Regression tests

```java
// An integration test observes the transaction/caching advice on inner.
```

## IOC-M-094: request bean used outside request

- Difficulty: Medium
- Framework: Spring Core & Inversion of Control
- Language: Java
- Perspective: Scopes
- Concept: request bean used outside request
- Symptom: A background task throws scope-not-active.
- Diagnostic goal: Capture immutable data, not a request-scoped object, for background work.

### Buggy code

```java
executor.submit(() -> requestContext.getUserId());
```

### Expected diagnosis

The request scope may be gone when the task runs.

### Corrected code

```java
String userId = requestContext.getUserId();
executor.submit(() -> process(userId));
```

### Regression tests

```java
// The task remains valid after the request completes.
```

## IOC-M-095: event published before commit

- Difficulty: Medium
- Framework: Spring Core & Inversion of Control
- Language: Java
- Perspective: Events
- Concept: event published before commit
- Symptom: A listener sees data that later rolls back.
- Diagnostic goal: Publish after a successful transaction commit when required.

### Buggy code

```java
publisher.publishEvent(new OrderCreated(order.id()));
repository.save(order);
```

### Expected diagnosis

The event is emitted before persistence commits and may describe a transaction that fails.

### Corrected code

```java
repository.save(order);
publisher.publishEvent(new OrderCreated(order.id()));
```

### Regression tests

```java
// A transactional listener receives the event only after commit.
```

## IOC-M-096: conditional bean unexpectedly absent

- Difficulty: Medium
- Framework: Spring Core & Inversion of Control
- Language: Java
- Perspective: Factory
- Concept: conditional bean unexpectedly absent
- Symptom: A feature flag has no implementation.
- Diagnostic goal: Check condition names and the effective environment.

### Buggy code

```java
@ConditionalOnProperty(name = "feature.mail")
@Bean Mailer mailer() { return new Mailer(); }
```

### Expected diagnosis

The condition requires a value unless havingValue or matchIfMissing is configured as intended.

### Corrected code

```java
@ConditionalOnProperty(name = "feature.mail", havingValue = "true")
@Bean Mailer mailer() { return new Mailer(); }
```

### Regression tests

```java
// Context reports a bean only when feature.mail=true.
```

## IOC-M-097: close omitted

- Difficulty: Medium
- Framework: Spring Core & Inversion of Control
- Language: Java
- Perspective: Resource lifecycle
- Concept: close omitted
- Symptom: Threads or connections remain after context shutdown.
- Diagnostic goal: Register resources as managed beans with destruction callbacks.

### Buggy code

```java
@Bean ExecutorService executor() { return Executors.newFixedThreadPool(4); }
```

### Expected diagnosis

The container does not know how to stop an arbitrary resource unless destruction is declared.

### Corrected code

```java
@Bean(destroyMethod = "shutdown") ExecutorService executor() { return Executors.newFixedThreadPool(4); }
```

### Regression tests

```java
// Context close invokes shutdown.
```

## IOC-M-098: listener order assumed

- Difficulty: Medium
- Framework: Spring Core & Inversion of Control
- Language: Java
- Perspective: Ordering
- Concept: listener order assumed
- Symptom: Two startup tasks run in the wrong order.
- Diagnostic goal: Declare ordering only where the dependency is real.

### Buggy code

```java
@EventListener
void seed() {}
@EventListener
void publish() {}
```

### Expected diagnosis

Listener registration order is not a reliable dependency contract.

### Corrected code

```java
@Order(1) @EventListener void seed() {}
@Order(2) @EventListener void publish() {}
```

### Regression tests

```java
// The test records seed before publish.
```

## IOC-M-099: optional bean treated as required

- Difficulty: Medium
- Framework: Spring Core & Inversion of Control
- Language: Java
- Perspective: Optional dependencies
- Concept: optional bean treated as required
- Symptom: A feature cannot start without an optional integration.
- Diagnostic goal: Represent optionality explicitly.

### Buggy code

```java
public Reporter(Exporter exporter) { this.exporter = exporter; }
```

### Expected diagnosis

Constructor injection requires Exporter even when the feature is disabled.

### Corrected code

```java
public Reporter(ObjectProvider<Exporter> exporter) { this.exporter = exporter; }
```

### Regression tests

```java
// Reporter starts without Exporter and uses a no-op path.
```

## IOC-M-100: service cycle hidden by field injection

- Difficulty: Medium
- Framework: Spring Core & Inversion of Control
- Language: Java
- Perspective: Circular design
- Concept: service cycle hidden by field injection
- Symptom: Runtime behavior is order-dependent and difficult to test.
- Diagnostic goal: Extract a port or move orchestration into a third component.

### Buggy code

```java
@Autowired A a;
class A { @Autowired B b; }
class B { @Autowired A a; }
```

### Expected diagnosis

Field injection hides the cycle until context creation and makes dependencies mutable.

### Corrected code

```java
class Orchestrator { Orchestrator(A a, B b) {} }
```

### Regression tests

```java
// A and B no longer depend directly on one another.
```

## IOC-H-001: prototype injected into singleton

- Difficulty: Hard
- Framework: Spring Core & Inversion of Control
- Language: Java
- Perspective: Bean lifecycle
- Concept: prototype injected into singleton
- Symptom: A supposed new object is reused.
- Diagnostic goal: Obtain shorter-lived beans through a provider or scoped proxy.

### Buggy code

```java
@Component
class JobRunner { private final Job job; JobRunner(Job job) { this.job = job; } }
```

### Expected diagnosis

A prototype dependency is resolved once when the singleton is constructed.

### Corrected code

```java
@Component
class JobRunner { private final ObjectProvider<Job> jobs; JobRunner(ObjectProvider<Job> jobs) { this.jobs = jobs; }
 Job next() { return jobs.getObject(); } }
```

### Regression tests

```java
// Two calls to next return distinct Job instances.
```

## IOC-H-002: multiple candidates ambiguous

- Difficulty: Hard
- Framework: Spring Core & Inversion of Control
- Language: Java
- Perspective: Injection
- Concept: multiple candidates ambiguous
- Symptom: Context startup reports NoUniqueBeanDefinitionException.
- Diagnostic goal: Qualify the intended implementation or define a primary bean.

### Buggy code

```java
@Bean PaymentGateway stripe() { return new StripeGateway(); }
@Bean PaymentGateway bank() { return new BankGateway(); }
@Service Checkout(PaymentGateway gateway) {}
```

### Expected diagnosis

The injection point has two candidates and no selection rule.

### Corrected code

```java
@Service Checkout(@Qualifier("stripe") PaymentGateway gateway) {}
```

### Regression tests

```java
// Context chooses Stripe only at the qualified injection point.
```

## IOC-H-003: self-invocation bypasses advice

- Difficulty: Hard
- Framework: Spring Core & Inversion of Control
- Language: Java
- Perspective: Proxying
- Concept: self-invocation bypasses advice
- Symptom: The transactional or cached annotation appears ignored.
- Diagnostic goal: Call the advised method through the proxy boundary.

### Buggy code

```java
@Transactional
public void outer() { inner(); }
@Transactional
public void inner() { /* work */ }
```

### Expected diagnosis

A direct this.inner() call never passes through the Spring proxy.

### Corrected code

```java
@Transactional
public void outer() { collaborator.inner(); }
```

### Regression tests

```java
// An integration test observes the transaction/caching advice on inner.
```

## IOC-H-004: request bean used outside request

- Difficulty: Hard
- Framework: Spring Core & Inversion of Control
- Language: Java
- Perspective: Scopes
- Concept: request bean used outside request
- Symptom: A background task throws scope-not-active.
- Diagnostic goal: Capture immutable data, not a request-scoped object, for background work.

### Buggy code

```java
executor.submit(() -> requestContext.getUserId());
```

### Expected diagnosis

The request scope may be gone when the task runs.

### Corrected code

```java
String userId = requestContext.getUserId();
executor.submit(() -> process(userId));
```

### Regression tests

```java
// The task remains valid after the request completes.
```

## IOC-H-005: event published before commit

- Difficulty: Hard
- Framework: Spring Core & Inversion of Control
- Language: Java
- Perspective: Events
- Concept: event published before commit
- Symptom: A listener sees data that later rolls back.
- Diagnostic goal: Publish after a successful transaction commit when required.

### Buggy code

```java
publisher.publishEvent(new OrderCreated(order.id()));
repository.save(order);
```

### Expected diagnosis

The event is emitted before persistence commits and may describe a transaction that fails.

### Corrected code

```java
repository.save(order);
publisher.publishEvent(new OrderCreated(order.id()));
```

### Regression tests

```java
// A transactional listener receives the event only after commit.
```

## IOC-H-006: conditional bean unexpectedly absent

- Difficulty: Hard
- Framework: Spring Core & Inversion of Control
- Language: Java
- Perspective: Factory
- Concept: conditional bean unexpectedly absent
- Symptom: A feature flag has no implementation.
- Diagnostic goal: Check condition names and the effective environment.

### Buggy code

```java
@ConditionalOnProperty(name = "feature.mail")
@Bean Mailer mailer() { return new Mailer(); }
```

### Expected diagnosis

The condition requires a value unless havingValue or matchIfMissing is configured as intended.

### Corrected code

```java
@ConditionalOnProperty(name = "feature.mail", havingValue = "true")
@Bean Mailer mailer() { return new Mailer(); }
```

### Regression tests

```java
// Context reports a bean only when feature.mail=true.
```

## IOC-H-007: close omitted

- Difficulty: Hard
- Framework: Spring Core & Inversion of Control
- Language: Java
- Perspective: Resource lifecycle
- Concept: close omitted
- Symptom: Threads or connections remain after context shutdown.
- Diagnostic goal: Register resources as managed beans with destruction callbacks.

### Buggy code

```java
@Bean ExecutorService executor() { return Executors.newFixedThreadPool(4); }
```

### Expected diagnosis

The container does not know how to stop an arbitrary resource unless destruction is declared.

### Corrected code

```java
@Bean(destroyMethod = "shutdown") ExecutorService executor() { return Executors.newFixedThreadPool(4); }
```

### Regression tests

```java
// Context close invokes shutdown.
```

## IOC-H-008: listener order assumed

- Difficulty: Hard
- Framework: Spring Core & Inversion of Control
- Language: Java
- Perspective: Ordering
- Concept: listener order assumed
- Symptom: Two startup tasks run in the wrong order.
- Diagnostic goal: Declare ordering only where the dependency is real.

### Buggy code

```java
@EventListener
void seed() {}
@EventListener
void publish() {}
```

### Expected diagnosis

Listener registration order is not a reliable dependency contract.

### Corrected code

```java
@Order(1) @EventListener void seed() {}
@Order(2) @EventListener void publish() {}
```

### Regression tests

```java
// The test records seed before publish.
```

## IOC-H-009: optional bean treated as required

- Difficulty: Hard
- Framework: Spring Core & Inversion of Control
- Language: Java
- Perspective: Optional dependencies
- Concept: optional bean treated as required
- Symptom: A feature cannot start without an optional integration.
- Diagnostic goal: Represent optionality explicitly.

### Buggy code

```java
public Reporter(Exporter exporter) { this.exporter = exporter; }
```

### Expected diagnosis

Constructor injection requires Exporter even when the feature is disabled.

### Corrected code

```java
public Reporter(ObjectProvider<Exporter> exporter) { this.exporter = exporter; }
```

### Regression tests

```java
// Reporter starts without Exporter and uses a no-op path.
```

## IOC-H-010: service cycle hidden by field injection

- Difficulty: Hard
- Framework: Spring Core & Inversion of Control
- Language: Java
- Perspective: Circular design
- Concept: service cycle hidden by field injection
- Symptom: Runtime behavior is order-dependent and difficult to test.
- Diagnostic goal: Extract a port or move orchestration into a third component.

### Buggy code

```java
@Autowired A a;
class A { @Autowired B b; }
class B { @Autowired A a; }
```

### Expected diagnosis

Field injection hides the cycle until context creation and makes dependencies mutable.

### Corrected code

```java
class Orchestrator { Orchestrator(A a, B b) {} }
```

### Regression tests

```java
// A and B no longer depend directly on one another.
```

## IOC-H-011: prototype injected into singleton

- Difficulty: Hard
- Framework: Spring Core & Inversion of Control
- Language: Java
- Perspective: Bean lifecycle
- Concept: prototype injected into singleton
- Symptom: A supposed new object is reused.
- Diagnostic goal: Obtain shorter-lived beans through a provider or scoped proxy.

### Buggy code

```java
@Component
class JobRunner { private final Job job; JobRunner(Job job) { this.job = job; } }
```

### Expected diagnosis

A prototype dependency is resolved once when the singleton is constructed.

### Corrected code

```java
@Component
class JobRunner { private final ObjectProvider<Job> jobs; JobRunner(ObjectProvider<Job> jobs) { this.jobs = jobs; }
 Job next() { return jobs.getObject(); } }
```

### Regression tests

```java
// Two calls to next return distinct Job instances.
```

## IOC-H-012: multiple candidates ambiguous

- Difficulty: Hard
- Framework: Spring Core & Inversion of Control
- Language: Java
- Perspective: Injection
- Concept: multiple candidates ambiguous
- Symptom: Context startup reports NoUniqueBeanDefinitionException.
- Diagnostic goal: Qualify the intended implementation or define a primary bean.

### Buggy code

```java
@Bean PaymentGateway stripe() { return new StripeGateway(); }
@Bean PaymentGateway bank() { return new BankGateway(); }
@Service Checkout(PaymentGateway gateway) {}
```

### Expected diagnosis

The injection point has two candidates and no selection rule.

### Corrected code

```java
@Service Checkout(@Qualifier("stripe") PaymentGateway gateway) {}
```

### Regression tests

```java
// Context chooses Stripe only at the qualified injection point.
```

## IOC-H-013: self-invocation bypasses advice

- Difficulty: Hard
- Framework: Spring Core & Inversion of Control
- Language: Java
- Perspective: Proxying
- Concept: self-invocation bypasses advice
- Symptom: The transactional or cached annotation appears ignored.
- Diagnostic goal: Call the advised method through the proxy boundary.

### Buggy code

```java
@Transactional
public void outer() { inner(); }
@Transactional
public void inner() { /* work */ }
```

### Expected diagnosis

A direct this.inner() call never passes through the Spring proxy.

### Corrected code

```java
@Transactional
public void outer() { collaborator.inner(); }
```

### Regression tests

```java
// An integration test observes the transaction/caching advice on inner.
```

## IOC-H-014: request bean used outside request

- Difficulty: Hard
- Framework: Spring Core & Inversion of Control
- Language: Java
- Perspective: Scopes
- Concept: request bean used outside request
- Symptom: A background task throws scope-not-active.
- Diagnostic goal: Capture immutable data, not a request-scoped object, for background work.

### Buggy code

```java
executor.submit(() -> requestContext.getUserId());
```

### Expected diagnosis

The request scope may be gone when the task runs.

### Corrected code

```java
String userId = requestContext.getUserId();
executor.submit(() -> process(userId));
```

### Regression tests

```java
// The task remains valid after the request completes.
```

## IOC-H-015: event published before commit

- Difficulty: Hard
- Framework: Spring Core & Inversion of Control
- Language: Java
- Perspective: Events
- Concept: event published before commit
- Symptom: A listener sees data that later rolls back.
- Diagnostic goal: Publish after a successful transaction commit when required.

### Buggy code

```java
publisher.publishEvent(new OrderCreated(order.id()));
repository.save(order);
```

### Expected diagnosis

The event is emitted before persistence commits and may describe a transaction that fails.

### Corrected code

```java
repository.save(order);
publisher.publishEvent(new OrderCreated(order.id()));
```

### Regression tests

```java
// A transactional listener receives the event only after commit.
```

## IOC-H-016: conditional bean unexpectedly absent

- Difficulty: Hard
- Framework: Spring Core & Inversion of Control
- Language: Java
- Perspective: Factory
- Concept: conditional bean unexpectedly absent
- Symptom: A feature flag has no implementation.
- Diagnostic goal: Check condition names and the effective environment.

### Buggy code

```java
@ConditionalOnProperty(name = "feature.mail")
@Bean Mailer mailer() { return new Mailer(); }
```

### Expected diagnosis

The condition requires a value unless havingValue or matchIfMissing is configured as intended.

### Corrected code

```java
@ConditionalOnProperty(name = "feature.mail", havingValue = "true")
@Bean Mailer mailer() { return new Mailer(); }
```

### Regression tests

```java
// Context reports a bean only when feature.mail=true.
```

## IOC-H-017: close omitted

- Difficulty: Hard
- Framework: Spring Core & Inversion of Control
- Language: Java
- Perspective: Resource lifecycle
- Concept: close omitted
- Symptom: Threads or connections remain after context shutdown.
- Diagnostic goal: Register resources as managed beans with destruction callbacks.

### Buggy code

```java
@Bean ExecutorService executor() { return Executors.newFixedThreadPool(4); }
```

### Expected diagnosis

The container does not know how to stop an arbitrary resource unless destruction is declared.

### Corrected code

```java
@Bean(destroyMethod = "shutdown") ExecutorService executor() { return Executors.newFixedThreadPool(4); }
```

### Regression tests

```java
// Context close invokes shutdown.
```

## IOC-H-018: listener order assumed

- Difficulty: Hard
- Framework: Spring Core & Inversion of Control
- Language: Java
- Perspective: Ordering
- Concept: listener order assumed
- Symptom: Two startup tasks run in the wrong order.
- Diagnostic goal: Declare ordering only where the dependency is real.

### Buggy code

```java
@EventListener
void seed() {}
@EventListener
void publish() {}
```

### Expected diagnosis

Listener registration order is not a reliable dependency contract.

### Corrected code

```java
@Order(1) @EventListener void seed() {}
@Order(2) @EventListener void publish() {}
```

### Regression tests

```java
// The test records seed before publish.
```

## IOC-H-019: optional bean treated as required

- Difficulty: Hard
- Framework: Spring Core & Inversion of Control
- Language: Java
- Perspective: Optional dependencies
- Concept: optional bean treated as required
- Symptom: A feature cannot start without an optional integration.
- Diagnostic goal: Represent optionality explicitly.

### Buggy code

```java
public Reporter(Exporter exporter) { this.exporter = exporter; }
```

### Expected diagnosis

Constructor injection requires Exporter even when the feature is disabled.

### Corrected code

```java
public Reporter(ObjectProvider<Exporter> exporter) { this.exporter = exporter; }
```

### Regression tests

```java
// Reporter starts without Exporter and uses a no-op path.
```

## IOC-H-020: service cycle hidden by field injection

- Difficulty: Hard
- Framework: Spring Core & Inversion of Control
- Language: Java
- Perspective: Circular design
- Concept: service cycle hidden by field injection
- Symptom: Runtime behavior is order-dependent and difficult to test.
- Diagnostic goal: Extract a port or move orchestration into a third component.

### Buggy code

```java
@Autowired A a;
class A { @Autowired B b; }
class B { @Autowired A a; }
```

### Expected diagnosis

Field injection hides the cycle until context creation and makes dependencies mutable.

### Corrected code

```java
class Orchestrator { Orchestrator(A a, B b) {} }
```

### Regression tests

```java
// A and B no longer depend directly on one another.
```

## IOC-H-021: prototype injected into singleton

- Difficulty: Hard
- Framework: Spring Core & Inversion of Control
- Language: Java
- Perspective: Bean lifecycle
- Concept: prototype injected into singleton
- Symptom: A supposed new object is reused.
- Diagnostic goal: Obtain shorter-lived beans through a provider or scoped proxy.

### Buggy code

```java
@Component
class JobRunner { private final Job job; JobRunner(Job job) { this.job = job; } }
```

### Expected diagnosis

A prototype dependency is resolved once when the singleton is constructed.

### Corrected code

```java
@Component
class JobRunner { private final ObjectProvider<Job> jobs; JobRunner(ObjectProvider<Job> jobs) { this.jobs = jobs; }
 Job next() { return jobs.getObject(); } }
```

### Regression tests

```java
// Two calls to next return distinct Job instances.
```

## IOC-H-022: multiple candidates ambiguous

- Difficulty: Hard
- Framework: Spring Core & Inversion of Control
- Language: Java
- Perspective: Injection
- Concept: multiple candidates ambiguous
- Symptom: Context startup reports NoUniqueBeanDefinitionException.
- Diagnostic goal: Qualify the intended implementation or define a primary bean.

### Buggy code

```java
@Bean PaymentGateway stripe() { return new StripeGateway(); }
@Bean PaymentGateway bank() { return new BankGateway(); }
@Service Checkout(PaymentGateway gateway) {}
```

### Expected diagnosis

The injection point has two candidates and no selection rule.

### Corrected code

```java
@Service Checkout(@Qualifier("stripe") PaymentGateway gateway) {}
```

### Regression tests

```java
// Context chooses Stripe only at the qualified injection point.
```

## IOC-H-023: self-invocation bypasses advice

- Difficulty: Hard
- Framework: Spring Core & Inversion of Control
- Language: Java
- Perspective: Proxying
- Concept: self-invocation bypasses advice
- Symptom: The transactional or cached annotation appears ignored.
- Diagnostic goal: Call the advised method through the proxy boundary.

### Buggy code

```java
@Transactional
public void outer() { inner(); }
@Transactional
public void inner() { /* work */ }
```

### Expected diagnosis

A direct this.inner() call never passes through the Spring proxy.

### Corrected code

```java
@Transactional
public void outer() { collaborator.inner(); }
```

### Regression tests

```java
// An integration test observes the transaction/caching advice on inner.
```

## IOC-H-024: request bean used outside request

- Difficulty: Hard
- Framework: Spring Core & Inversion of Control
- Language: Java
- Perspective: Scopes
- Concept: request bean used outside request
- Symptom: A background task throws scope-not-active.
- Diagnostic goal: Capture immutable data, not a request-scoped object, for background work.

### Buggy code

```java
executor.submit(() -> requestContext.getUserId());
```

### Expected diagnosis

The request scope may be gone when the task runs.

### Corrected code

```java
String userId = requestContext.getUserId();
executor.submit(() -> process(userId));
```

### Regression tests

```java
// The task remains valid after the request completes.
```

## IOC-H-025: event published before commit

- Difficulty: Hard
- Framework: Spring Core & Inversion of Control
- Language: Java
- Perspective: Events
- Concept: event published before commit
- Symptom: A listener sees data that later rolls back.
- Diagnostic goal: Publish after a successful transaction commit when required.

### Buggy code

```java
publisher.publishEvent(new OrderCreated(order.id()));
repository.save(order);
```

### Expected diagnosis

The event is emitted before persistence commits and may describe a transaction that fails.

### Corrected code

```java
repository.save(order);
publisher.publishEvent(new OrderCreated(order.id()));
```

### Regression tests

```java
// A transactional listener receives the event only after commit.
```

## IOC-H-026: conditional bean unexpectedly absent

- Difficulty: Hard
- Framework: Spring Core & Inversion of Control
- Language: Java
- Perspective: Factory
- Concept: conditional bean unexpectedly absent
- Symptom: A feature flag has no implementation.
- Diagnostic goal: Check condition names and the effective environment.

### Buggy code

```java
@ConditionalOnProperty(name = "feature.mail")
@Bean Mailer mailer() { return new Mailer(); }
```

### Expected diagnosis

The condition requires a value unless havingValue or matchIfMissing is configured as intended.

### Corrected code

```java
@ConditionalOnProperty(name = "feature.mail", havingValue = "true")
@Bean Mailer mailer() { return new Mailer(); }
```

### Regression tests

```java
// Context reports a bean only when feature.mail=true.
```

## IOC-H-027: close omitted

- Difficulty: Hard
- Framework: Spring Core & Inversion of Control
- Language: Java
- Perspective: Resource lifecycle
- Concept: close omitted
- Symptom: Threads or connections remain after context shutdown.
- Diagnostic goal: Register resources as managed beans with destruction callbacks.

### Buggy code

```java
@Bean ExecutorService executor() { return Executors.newFixedThreadPool(4); }
```

### Expected diagnosis

The container does not know how to stop an arbitrary resource unless destruction is declared.

### Corrected code

```java
@Bean(destroyMethod = "shutdown") ExecutorService executor() { return Executors.newFixedThreadPool(4); }
```

### Regression tests

```java
// Context close invokes shutdown.
```

## IOC-H-028: listener order assumed

- Difficulty: Hard
- Framework: Spring Core & Inversion of Control
- Language: Java
- Perspective: Ordering
- Concept: listener order assumed
- Symptom: Two startup tasks run in the wrong order.
- Diagnostic goal: Declare ordering only where the dependency is real.

### Buggy code

```java
@EventListener
void seed() {}
@EventListener
void publish() {}
```

### Expected diagnosis

Listener registration order is not a reliable dependency contract.

### Corrected code

```java
@Order(1) @EventListener void seed() {}
@Order(2) @EventListener void publish() {}
```

### Regression tests

```java
// The test records seed before publish.
```

## IOC-H-029: optional bean treated as required

- Difficulty: Hard
- Framework: Spring Core & Inversion of Control
- Language: Java
- Perspective: Optional dependencies
- Concept: optional bean treated as required
- Symptom: A feature cannot start without an optional integration.
- Diagnostic goal: Represent optionality explicitly.

### Buggy code

```java
public Reporter(Exporter exporter) { this.exporter = exporter; }
```

### Expected diagnosis

Constructor injection requires Exporter even when the feature is disabled.

### Corrected code

```java
public Reporter(ObjectProvider<Exporter> exporter) { this.exporter = exporter; }
```

### Regression tests

```java
// Reporter starts without Exporter and uses a no-op path.
```

## IOC-H-030: service cycle hidden by field injection

- Difficulty: Hard
- Framework: Spring Core & Inversion of Control
- Language: Java
- Perspective: Circular design
- Concept: service cycle hidden by field injection
- Symptom: Runtime behavior is order-dependent and difficult to test.
- Diagnostic goal: Extract a port or move orchestration into a third component.

### Buggy code

```java
@Autowired A a;
class A { @Autowired B b; }
class B { @Autowired A a; }
```

### Expected diagnosis

Field injection hides the cycle until context creation and makes dependencies mutable.

### Corrected code

```java
class Orchestrator { Orchestrator(A a, B b) {} }
```

### Regression tests

```java
// A and B no longer depend directly on one another.
```

## IOC-H-031: prototype injected into singleton

- Difficulty: Hard
- Framework: Spring Core & Inversion of Control
- Language: Java
- Perspective: Bean lifecycle
- Concept: prototype injected into singleton
- Symptom: A supposed new object is reused.
- Diagnostic goal: Obtain shorter-lived beans through a provider or scoped proxy.

### Buggy code

```java
@Component
class JobRunner { private final Job job; JobRunner(Job job) { this.job = job; } }
```

### Expected diagnosis

A prototype dependency is resolved once when the singleton is constructed.

### Corrected code

```java
@Component
class JobRunner { private final ObjectProvider<Job> jobs; JobRunner(ObjectProvider<Job> jobs) { this.jobs = jobs; }
 Job next() { return jobs.getObject(); } }
```

### Regression tests

```java
// Two calls to next return distinct Job instances.
```

## IOC-H-032: multiple candidates ambiguous

- Difficulty: Hard
- Framework: Spring Core & Inversion of Control
- Language: Java
- Perspective: Injection
- Concept: multiple candidates ambiguous
- Symptom: Context startup reports NoUniqueBeanDefinitionException.
- Diagnostic goal: Qualify the intended implementation or define a primary bean.

### Buggy code

```java
@Bean PaymentGateway stripe() { return new StripeGateway(); }
@Bean PaymentGateway bank() { return new BankGateway(); }
@Service Checkout(PaymentGateway gateway) {}
```

### Expected diagnosis

The injection point has two candidates and no selection rule.

### Corrected code

```java
@Service Checkout(@Qualifier("stripe") PaymentGateway gateway) {}
```

### Regression tests

```java
// Context chooses Stripe only at the qualified injection point.
```

## IOC-H-033: self-invocation bypasses advice

- Difficulty: Hard
- Framework: Spring Core & Inversion of Control
- Language: Java
- Perspective: Proxying
- Concept: self-invocation bypasses advice
- Symptom: The transactional or cached annotation appears ignored.
- Diagnostic goal: Call the advised method through the proxy boundary.

### Buggy code

```java
@Transactional
public void outer() { inner(); }
@Transactional
public void inner() { /* work */ }
```

### Expected diagnosis

A direct this.inner() call never passes through the Spring proxy.

### Corrected code

```java
@Transactional
public void outer() { collaborator.inner(); }
```

### Regression tests

```java
// An integration test observes the transaction/caching advice on inner.
```

## IOC-H-034: request bean used outside request

- Difficulty: Hard
- Framework: Spring Core & Inversion of Control
- Language: Java
- Perspective: Scopes
- Concept: request bean used outside request
- Symptom: A background task throws scope-not-active.
- Diagnostic goal: Capture immutable data, not a request-scoped object, for background work.

### Buggy code

```java
executor.submit(() -> requestContext.getUserId());
```

### Expected diagnosis

The request scope may be gone when the task runs.

### Corrected code

```java
String userId = requestContext.getUserId();
executor.submit(() -> process(userId));
```

### Regression tests

```java
// The task remains valid after the request completes.
```

## IOC-H-035: event published before commit

- Difficulty: Hard
- Framework: Spring Core & Inversion of Control
- Language: Java
- Perspective: Events
- Concept: event published before commit
- Symptom: A listener sees data that later rolls back.
- Diagnostic goal: Publish after a successful transaction commit when required.

### Buggy code

```java
publisher.publishEvent(new OrderCreated(order.id()));
repository.save(order);
```

### Expected diagnosis

The event is emitted before persistence commits and may describe a transaction that fails.

### Corrected code

```java
repository.save(order);
publisher.publishEvent(new OrderCreated(order.id()));
```

### Regression tests

```java
// A transactional listener receives the event only after commit.
```

## IOC-H-036: conditional bean unexpectedly absent

- Difficulty: Hard
- Framework: Spring Core & Inversion of Control
- Language: Java
- Perspective: Factory
- Concept: conditional bean unexpectedly absent
- Symptom: A feature flag has no implementation.
- Diagnostic goal: Check condition names and the effective environment.

### Buggy code

```java
@ConditionalOnProperty(name = "feature.mail")
@Bean Mailer mailer() { return new Mailer(); }
```

### Expected diagnosis

The condition requires a value unless havingValue or matchIfMissing is configured as intended.

### Corrected code

```java
@ConditionalOnProperty(name = "feature.mail", havingValue = "true")
@Bean Mailer mailer() { return new Mailer(); }
```

### Regression tests

```java
// Context reports a bean only when feature.mail=true.
```

## IOC-H-037: close omitted

- Difficulty: Hard
- Framework: Spring Core & Inversion of Control
- Language: Java
- Perspective: Resource lifecycle
- Concept: close omitted
- Symptom: Threads or connections remain after context shutdown.
- Diagnostic goal: Register resources as managed beans with destruction callbacks.

### Buggy code

```java
@Bean ExecutorService executor() { return Executors.newFixedThreadPool(4); }
```

### Expected diagnosis

The container does not know how to stop an arbitrary resource unless destruction is declared.

### Corrected code

```java
@Bean(destroyMethod = "shutdown") ExecutorService executor() { return Executors.newFixedThreadPool(4); }
```

### Regression tests

```java
// Context close invokes shutdown.
```

## IOC-H-038: listener order assumed

- Difficulty: Hard
- Framework: Spring Core & Inversion of Control
- Language: Java
- Perspective: Ordering
- Concept: listener order assumed
- Symptom: Two startup tasks run in the wrong order.
- Diagnostic goal: Declare ordering only where the dependency is real.

### Buggy code

```java
@EventListener
void seed() {}
@EventListener
void publish() {}
```

### Expected diagnosis

Listener registration order is not a reliable dependency contract.

### Corrected code

```java
@Order(1) @EventListener void seed() {}
@Order(2) @EventListener void publish() {}
```

### Regression tests

```java
// The test records seed before publish.
```

## IOC-H-039: optional bean treated as required

- Difficulty: Hard
- Framework: Spring Core & Inversion of Control
- Language: Java
- Perspective: Optional dependencies
- Concept: optional bean treated as required
- Symptom: A feature cannot start without an optional integration.
- Diagnostic goal: Represent optionality explicitly.

### Buggy code

```java
public Reporter(Exporter exporter) { this.exporter = exporter; }
```

### Expected diagnosis

Constructor injection requires Exporter even when the feature is disabled.

### Corrected code

```java
public Reporter(ObjectProvider<Exporter> exporter) { this.exporter = exporter; }
```

### Regression tests

```java
// Reporter starts without Exporter and uses a no-op path.
```

## IOC-H-040: service cycle hidden by field injection

- Difficulty: Hard
- Framework: Spring Core & Inversion of Control
- Language: Java
- Perspective: Circular design
- Concept: service cycle hidden by field injection
- Symptom: Runtime behavior is order-dependent and difficult to test.
- Diagnostic goal: Extract a port or move orchestration into a third component.

### Buggy code

```java
@Autowired A a;
class A { @Autowired B b; }
class B { @Autowired A a; }
```

### Expected diagnosis

Field injection hides the cycle until context creation and makes dependencies mutable.

### Corrected code

```java
class Orchestrator { Orchestrator(A a, B b) {} }
```

### Regression tests

```java
// A and B no longer depend directly on one another.
```

## IOC-H-041: prototype injected into singleton

- Difficulty: Hard
- Framework: Spring Core & Inversion of Control
- Language: Java
- Perspective: Bean lifecycle
- Concept: prototype injected into singleton
- Symptom: A supposed new object is reused.
- Diagnostic goal: Obtain shorter-lived beans through a provider or scoped proxy.

### Buggy code

```java
@Component
class JobRunner { private final Job job; JobRunner(Job job) { this.job = job; } }
```

### Expected diagnosis

A prototype dependency is resolved once when the singleton is constructed.

### Corrected code

```java
@Component
class JobRunner { private final ObjectProvider<Job> jobs; JobRunner(ObjectProvider<Job> jobs) { this.jobs = jobs; }
 Job next() { return jobs.getObject(); } }
```

### Regression tests

```java
// Two calls to next return distinct Job instances.
```

## IOC-H-042: multiple candidates ambiguous

- Difficulty: Hard
- Framework: Spring Core & Inversion of Control
- Language: Java
- Perspective: Injection
- Concept: multiple candidates ambiguous
- Symptom: Context startup reports NoUniqueBeanDefinitionException.
- Diagnostic goal: Qualify the intended implementation or define a primary bean.

### Buggy code

```java
@Bean PaymentGateway stripe() { return new StripeGateway(); }
@Bean PaymentGateway bank() { return new BankGateway(); }
@Service Checkout(PaymentGateway gateway) {}
```

### Expected diagnosis

The injection point has two candidates and no selection rule.

### Corrected code

```java
@Service Checkout(@Qualifier("stripe") PaymentGateway gateway) {}
```

### Regression tests

```java
// Context chooses Stripe only at the qualified injection point.
```

## IOC-H-043: self-invocation bypasses advice

- Difficulty: Hard
- Framework: Spring Core & Inversion of Control
- Language: Java
- Perspective: Proxying
- Concept: self-invocation bypasses advice
- Symptom: The transactional or cached annotation appears ignored.
- Diagnostic goal: Call the advised method through the proxy boundary.

### Buggy code

```java
@Transactional
public void outer() { inner(); }
@Transactional
public void inner() { /* work */ }
```

### Expected diagnosis

A direct this.inner() call never passes through the Spring proxy.

### Corrected code

```java
@Transactional
public void outer() { collaborator.inner(); }
```

### Regression tests

```java
// An integration test observes the transaction/caching advice on inner.
```

## IOC-H-044: request bean used outside request

- Difficulty: Hard
- Framework: Spring Core & Inversion of Control
- Language: Java
- Perspective: Scopes
- Concept: request bean used outside request
- Symptom: A background task throws scope-not-active.
- Diagnostic goal: Capture immutable data, not a request-scoped object, for background work.

### Buggy code

```java
executor.submit(() -> requestContext.getUserId());
```

### Expected diagnosis

The request scope may be gone when the task runs.

### Corrected code

```java
String userId = requestContext.getUserId();
executor.submit(() -> process(userId));
```

### Regression tests

```java
// The task remains valid after the request completes.
```

## IOC-H-045: event published before commit

- Difficulty: Hard
- Framework: Spring Core & Inversion of Control
- Language: Java
- Perspective: Events
- Concept: event published before commit
- Symptom: A listener sees data that later rolls back.
- Diagnostic goal: Publish after a successful transaction commit when required.

### Buggy code

```java
publisher.publishEvent(new OrderCreated(order.id()));
repository.save(order);
```

### Expected diagnosis

The event is emitted before persistence commits and may describe a transaction that fails.

### Corrected code

```java
repository.save(order);
publisher.publishEvent(new OrderCreated(order.id()));
```

### Regression tests

```java
// A transactional listener receives the event only after commit.
```

## IOC-H-046: conditional bean unexpectedly absent

- Difficulty: Hard
- Framework: Spring Core & Inversion of Control
- Language: Java
- Perspective: Factory
- Concept: conditional bean unexpectedly absent
- Symptom: A feature flag has no implementation.
- Diagnostic goal: Check condition names and the effective environment.

### Buggy code

```java
@ConditionalOnProperty(name = "feature.mail")
@Bean Mailer mailer() { return new Mailer(); }
```

### Expected diagnosis

The condition requires a value unless havingValue or matchIfMissing is configured as intended.

### Corrected code

```java
@ConditionalOnProperty(name = "feature.mail", havingValue = "true")
@Bean Mailer mailer() { return new Mailer(); }
```

### Regression tests

```java
// Context reports a bean only when feature.mail=true.
```

## IOC-H-047: close omitted

- Difficulty: Hard
- Framework: Spring Core & Inversion of Control
- Language: Java
- Perspective: Resource lifecycle
- Concept: close omitted
- Symptom: Threads or connections remain after context shutdown.
- Diagnostic goal: Register resources as managed beans with destruction callbacks.

### Buggy code

```java
@Bean ExecutorService executor() { return Executors.newFixedThreadPool(4); }
```

### Expected diagnosis

The container does not know how to stop an arbitrary resource unless destruction is declared.

### Corrected code

```java
@Bean(destroyMethod = "shutdown") ExecutorService executor() { return Executors.newFixedThreadPool(4); }
```

### Regression tests

```java
// Context close invokes shutdown.
```

## IOC-H-048: listener order assumed

- Difficulty: Hard
- Framework: Spring Core & Inversion of Control
- Language: Java
- Perspective: Ordering
- Concept: listener order assumed
- Symptom: Two startup tasks run in the wrong order.
- Diagnostic goal: Declare ordering only where the dependency is real.

### Buggy code

```java
@EventListener
void seed() {}
@EventListener
void publish() {}
```

### Expected diagnosis

Listener registration order is not a reliable dependency contract.

### Corrected code

```java
@Order(1) @EventListener void seed() {}
@Order(2) @EventListener void publish() {}
```

### Regression tests

```java
// The test records seed before publish.
```

## IOC-H-049: optional bean treated as required

- Difficulty: Hard
- Framework: Spring Core & Inversion of Control
- Language: Java
- Perspective: Optional dependencies
- Concept: optional bean treated as required
- Symptom: A feature cannot start without an optional integration.
- Diagnostic goal: Represent optionality explicitly.

### Buggy code

```java
public Reporter(Exporter exporter) { this.exporter = exporter; }
```

### Expected diagnosis

Constructor injection requires Exporter even when the feature is disabled.

### Corrected code

```java
public Reporter(ObjectProvider<Exporter> exporter) { this.exporter = exporter; }
```

### Regression tests

```java
// Reporter starts without Exporter and uses a no-op path.
```

## IOC-H-050: service cycle hidden by field injection

- Difficulty: Hard
- Framework: Spring Core & Inversion of Control
- Language: Java
- Perspective: Circular design
- Concept: service cycle hidden by field injection
- Symptom: Runtime behavior is order-dependent and difficult to test.
- Diagnostic goal: Extract a port or move orchestration into a third component.

### Buggy code

```java
@Autowired A a;
class A { @Autowired B b; }
class B { @Autowired A a; }
```

### Expected diagnosis

Field injection hides the cycle until context creation and makes dependencies mutable.

### Corrected code

```java
class Orchestrator { Orchestrator(A a, B b) {} }
```

### Regression tests

```java
// A and B no longer depend directly on one another.
```

## IOC-H-051: prototype injected into singleton

- Difficulty: Hard
- Framework: Spring Core & Inversion of Control
- Language: Java
- Perspective: Bean lifecycle
- Concept: prototype injected into singleton
- Symptom: A supposed new object is reused.
- Diagnostic goal: Obtain shorter-lived beans through a provider or scoped proxy.

### Buggy code

```java
@Component
class JobRunner { private final Job job; JobRunner(Job job) { this.job = job; } }
```

### Expected diagnosis

A prototype dependency is resolved once when the singleton is constructed.

### Corrected code

```java
@Component
class JobRunner { private final ObjectProvider<Job> jobs; JobRunner(ObjectProvider<Job> jobs) { this.jobs = jobs; }
 Job next() { return jobs.getObject(); } }
```

### Regression tests

```java
// Two calls to next return distinct Job instances.
```

## IOC-H-052: multiple candidates ambiguous

- Difficulty: Hard
- Framework: Spring Core & Inversion of Control
- Language: Java
- Perspective: Injection
- Concept: multiple candidates ambiguous
- Symptom: Context startup reports NoUniqueBeanDefinitionException.
- Diagnostic goal: Qualify the intended implementation or define a primary bean.

### Buggy code

```java
@Bean PaymentGateway stripe() { return new StripeGateway(); }
@Bean PaymentGateway bank() { return new BankGateway(); }
@Service Checkout(PaymentGateway gateway) {}
```

### Expected diagnosis

The injection point has two candidates and no selection rule.

### Corrected code

```java
@Service Checkout(@Qualifier("stripe") PaymentGateway gateway) {}
```

### Regression tests

```java
// Context chooses Stripe only at the qualified injection point.
```

## IOC-H-053: self-invocation bypasses advice

- Difficulty: Hard
- Framework: Spring Core & Inversion of Control
- Language: Java
- Perspective: Proxying
- Concept: self-invocation bypasses advice
- Symptom: The transactional or cached annotation appears ignored.
- Diagnostic goal: Call the advised method through the proxy boundary.

### Buggy code

```java
@Transactional
public void outer() { inner(); }
@Transactional
public void inner() { /* work */ }
```

### Expected diagnosis

A direct this.inner() call never passes through the Spring proxy.

### Corrected code

```java
@Transactional
public void outer() { collaborator.inner(); }
```

### Regression tests

```java
// An integration test observes the transaction/caching advice on inner.
```

## IOC-H-054: request bean used outside request

- Difficulty: Hard
- Framework: Spring Core & Inversion of Control
- Language: Java
- Perspective: Scopes
- Concept: request bean used outside request
- Symptom: A background task throws scope-not-active.
- Diagnostic goal: Capture immutable data, not a request-scoped object, for background work.

### Buggy code

```java
executor.submit(() -> requestContext.getUserId());
```

### Expected diagnosis

The request scope may be gone when the task runs.

### Corrected code

```java
String userId = requestContext.getUserId();
executor.submit(() -> process(userId));
```

### Regression tests

```java
// The task remains valid after the request completes.
```

## IOC-H-055: event published before commit

- Difficulty: Hard
- Framework: Spring Core & Inversion of Control
- Language: Java
- Perspective: Events
- Concept: event published before commit
- Symptom: A listener sees data that later rolls back.
- Diagnostic goal: Publish after a successful transaction commit when required.

### Buggy code

```java
publisher.publishEvent(new OrderCreated(order.id()));
repository.save(order);
```

### Expected diagnosis

The event is emitted before persistence commits and may describe a transaction that fails.

### Corrected code

```java
repository.save(order);
publisher.publishEvent(new OrderCreated(order.id()));
```

### Regression tests

```java
// A transactional listener receives the event only after commit.
```

## IOC-H-056: conditional bean unexpectedly absent

- Difficulty: Hard
- Framework: Spring Core & Inversion of Control
- Language: Java
- Perspective: Factory
- Concept: conditional bean unexpectedly absent
- Symptom: A feature flag has no implementation.
- Diagnostic goal: Check condition names and the effective environment.

### Buggy code

```java
@ConditionalOnProperty(name = "feature.mail")
@Bean Mailer mailer() { return new Mailer(); }
```

### Expected diagnosis

The condition requires a value unless havingValue or matchIfMissing is configured as intended.

### Corrected code

```java
@ConditionalOnProperty(name = "feature.mail", havingValue = "true")
@Bean Mailer mailer() { return new Mailer(); }
```

### Regression tests

```java
// Context reports a bean only when feature.mail=true.
```

## IOC-H-057: close omitted

- Difficulty: Hard
- Framework: Spring Core & Inversion of Control
- Language: Java
- Perspective: Resource lifecycle
- Concept: close omitted
- Symptom: Threads or connections remain after context shutdown.
- Diagnostic goal: Register resources as managed beans with destruction callbacks.

### Buggy code

```java
@Bean ExecutorService executor() { return Executors.newFixedThreadPool(4); }
```

### Expected diagnosis

The container does not know how to stop an arbitrary resource unless destruction is declared.

### Corrected code

```java
@Bean(destroyMethod = "shutdown") ExecutorService executor() { return Executors.newFixedThreadPool(4); }
```

### Regression tests

```java
// Context close invokes shutdown.
```

## IOC-H-058: listener order assumed

- Difficulty: Hard
- Framework: Spring Core & Inversion of Control
- Language: Java
- Perspective: Ordering
- Concept: listener order assumed
- Symptom: Two startup tasks run in the wrong order.
- Diagnostic goal: Declare ordering only where the dependency is real.

### Buggy code

```java
@EventListener
void seed() {}
@EventListener
void publish() {}
```

### Expected diagnosis

Listener registration order is not a reliable dependency contract.

### Corrected code

```java
@Order(1) @EventListener void seed() {}
@Order(2) @EventListener void publish() {}
```

### Regression tests

```java
// The test records seed before publish.
```

## IOC-H-059: optional bean treated as required

- Difficulty: Hard
- Framework: Spring Core & Inversion of Control
- Language: Java
- Perspective: Optional dependencies
- Concept: optional bean treated as required
- Symptom: A feature cannot start without an optional integration.
- Diagnostic goal: Represent optionality explicitly.

### Buggy code

```java
public Reporter(Exporter exporter) { this.exporter = exporter; }
```

### Expected diagnosis

Constructor injection requires Exporter even when the feature is disabled.

### Corrected code

```java
public Reporter(ObjectProvider<Exporter> exporter) { this.exporter = exporter; }
```

### Regression tests

```java
// Reporter starts without Exporter and uses a no-op path.
```

## IOC-H-060: service cycle hidden by field injection

- Difficulty: Hard
- Framework: Spring Core & Inversion of Control
- Language: Java
- Perspective: Circular design
- Concept: service cycle hidden by field injection
- Symptom: Runtime behavior is order-dependent and difficult to test.
- Diagnostic goal: Extract a port or move orchestration into a third component.

### Buggy code

```java
@Autowired A a;
class A { @Autowired B b; }
class B { @Autowired A a; }
```

### Expected diagnosis

Field injection hides the cycle until context creation and makes dependencies mutable.

### Corrected code

```java
class Orchestrator { Orchestrator(A a, B b) {} }
```

### Regression tests

```java
// A and B no longer depend directly on one another.
```

## IOC-H-061: prototype injected into singleton

- Difficulty: Hard
- Framework: Spring Core & Inversion of Control
- Language: Java
- Perspective: Bean lifecycle
- Concept: prototype injected into singleton
- Symptom: A supposed new object is reused.
- Diagnostic goal: Obtain shorter-lived beans through a provider or scoped proxy.

### Buggy code

```java
@Component
class JobRunner { private final Job job; JobRunner(Job job) { this.job = job; } }
```

### Expected diagnosis

A prototype dependency is resolved once when the singleton is constructed.

### Corrected code

```java
@Component
class JobRunner { private final ObjectProvider<Job> jobs; JobRunner(ObjectProvider<Job> jobs) { this.jobs = jobs; }
 Job next() { return jobs.getObject(); } }
```

### Regression tests

```java
// Two calls to next return distinct Job instances.
```

## IOC-H-062: multiple candidates ambiguous

- Difficulty: Hard
- Framework: Spring Core & Inversion of Control
- Language: Java
- Perspective: Injection
- Concept: multiple candidates ambiguous
- Symptom: Context startup reports NoUniqueBeanDefinitionException.
- Diagnostic goal: Qualify the intended implementation or define a primary bean.

### Buggy code

```java
@Bean PaymentGateway stripe() { return new StripeGateway(); }
@Bean PaymentGateway bank() { return new BankGateway(); }
@Service Checkout(PaymentGateway gateway) {}
```

### Expected diagnosis

The injection point has two candidates and no selection rule.

### Corrected code

```java
@Service Checkout(@Qualifier("stripe") PaymentGateway gateway) {}
```

### Regression tests

```java
// Context chooses Stripe only at the qualified injection point.
```

## IOC-H-063: self-invocation bypasses advice

- Difficulty: Hard
- Framework: Spring Core & Inversion of Control
- Language: Java
- Perspective: Proxying
- Concept: self-invocation bypasses advice
- Symptom: The transactional or cached annotation appears ignored.
- Diagnostic goal: Call the advised method through the proxy boundary.

### Buggy code

```java
@Transactional
public void outer() { inner(); }
@Transactional
public void inner() { /* work */ }
```

### Expected diagnosis

A direct this.inner() call never passes through the Spring proxy.

### Corrected code

```java
@Transactional
public void outer() { collaborator.inner(); }
```

### Regression tests

```java
// An integration test observes the transaction/caching advice on inner.
```

## IOC-H-064: request bean used outside request

- Difficulty: Hard
- Framework: Spring Core & Inversion of Control
- Language: Java
- Perspective: Scopes
- Concept: request bean used outside request
- Symptom: A background task throws scope-not-active.
- Diagnostic goal: Capture immutable data, not a request-scoped object, for background work.

### Buggy code

```java
executor.submit(() -> requestContext.getUserId());
```

### Expected diagnosis

The request scope may be gone when the task runs.

### Corrected code

```java
String userId = requestContext.getUserId();
executor.submit(() -> process(userId));
```

### Regression tests

```java
// The task remains valid after the request completes.
```

## IOC-H-065: event published before commit

- Difficulty: Hard
- Framework: Spring Core & Inversion of Control
- Language: Java
- Perspective: Events
- Concept: event published before commit
- Symptom: A listener sees data that later rolls back.
- Diagnostic goal: Publish after a successful transaction commit when required.

### Buggy code

```java
publisher.publishEvent(new OrderCreated(order.id()));
repository.save(order);
```

### Expected diagnosis

The event is emitted before persistence commits and may describe a transaction that fails.

### Corrected code

```java
repository.save(order);
publisher.publishEvent(new OrderCreated(order.id()));
```

### Regression tests

```java
// A transactional listener receives the event only after commit.
```

## IOC-H-066: conditional bean unexpectedly absent

- Difficulty: Hard
- Framework: Spring Core & Inversion of Control
- Language: Java
- Perspective: Factory
- Concept: conditional bean unexpectedly absent
- Symptom: A feature flag has no implementation.
- Diagnostic goal: Check condition names and the effective environment.

### Buggy code

```java
@ConditionalOnProperty(name = "feature.mail")
@Bean Mailer mailer() { return new Mailer(); }
```

### Expected diagnosis

The condition requires a value unless havingValue or matchIfMissing is configured as intended.

### Corrected code

```java
@ConditionalOnProperty(name = "feature.mail", havingValue = "true")
@Bean Mailer mailer() { return new Mailer(); }
```

### Regression tests

```java
// Context reports a bean only when feature.mail=true.
```

## IOC-H-067: close omitted

- Difficulty: Hard
- Framework: Spring Core & Inversion of Control
- Language: Java
- Perspective: Resource lifecycle
- Concept: close omitted
- Symptom: Threads or connections remain after context shutdown.
- Diagnostic goal: Register resources as managed beans with destruction callbacks.

### Buggy code

```java
@Bean ExecutorService executor() { return Executors.newFixedThreadPool(4); }
```

### Expected diagnosis

The container does not know how to stop an arbitrary resource unless destruction is declared.

### Corrected code

```java
@Bean(destroyMethod = "shutdown") ExecutorService executor() { return Executors.newFixedThreadPool(4); }
```

### Regression tests

```java
// Context close invokes shutdown.
```

## IOC-H-068: listener order assumed

- Difficulty: Hard
- Framework: Spring Core & Inversion of Control
- Language: Java
- Perspective: Ordering
- Concept: listener order assumed
- Symptom: Two startup tasks run in the wrong order.
- Diagnostic goal: Declare ordering only where the dependency is real.

### Buggy code

```java
@EventListener
void seed() {}
@EventListener
void publish() {}
```

### Expected diagnosis

Listener registration order is not a reliable dependency contract.

### Corrected code

```java
@Order(1) @EventListener void seed() {}
@Order(2) @EventListener void publish() {}
```

### Regression tests

```java
// The test records seed before publish.
```

## IOC-H-069: optional bean treated as required

- Difficulty: Hard
- Framework: Spring Core & Inversion of Control
- Language: Java
- Perspective: Optional dependencies
- Concept: optional bean treated as required
- Symptom: A feature cannot start without an optional integration.
- Diagnostic goal: Represent optionality explicitly.

### Buggy code

```java
public Reporter(Exporter exporter) { this.exporter = exporter; }
```

### Expected diagnosis

Constructor injection requires Exporter even when the feature is disabled.

### Corrected code

```java
public Reporter(ObjectProvider<Exporter> exporter) { this.exporter = exporter; }
```

### Regression tests

```java
// Reporter starts without Exporter and uses a no-op path.
```

## IOC-H-070: service cycle hidden by field injection

- Difficulty: Hard
- Framework: Spring Core & Inversion of Control
- Language: Java
- Perspective: Circular design
- Concept: service cycle hidden by field injection
- Symptom: Runtime behavior is order-dependent and difficult to test.
- Diagnostic goal: Extract a port or move orchestration into a third component.

### Buggy code

```java
@Autowired A a;
class A { @Autowired B b; }
class B { @Autowired A a; }
```

### Expected diagnosis

Field injection hides the cycle until context creation and makes dependencies mutable.

### Corrected code

```java
class Orchestrator { Orchestrator(A a, B b) {} }
```

### Regression tests

```java
// A and B no longer depend directly on one another.
```

## IOC-H-071: prototype injected into singleton

- Difficulty: Hard
- Framework: Spring Core & Inversion of Control
- Language: Java
- Perspective: Bean lifecycle
- Concept: prototype injected into singleton
- Symptom: A supposed new object is reused.
- Diagnostic goal: Obtain shorter-lived beans through a provider or scoped proxy.

### Buggy code

```java
@Component
class JobRunner { private final Job job; JobRunner(Job job) { this.job = job; } }
```

### Expected diagnosis

A prototype dependency is resolved once when the singleton is constructed.

### Corrected code

```java
@Component
class JobRunner { private final ObjectProvider<Job> jobs; JobRunner(ObjectProvider<Job> jobs) { this.jobs = jobs; }
 Job next() { return jobs.getObject(); } }
```

### Regression tests

```java
// Two calls to next return distinct Job instances.
```

## IOC-H-072: multiple candidates ambiguous

- Difficulty: Hard
- Framework: Spring Core & Inversion of Control
- Language: Java
- Perspective: Injection
- Concept: multiple candidates ambiguous
- Symptom: Context startup reports NoUniqueBeanDefinitionException.
- Diagnostic goal: Qualify the intended implementation or define a primary bean.

### Buggy code

```java
@Bean PaymentGateway stripe() { return new StripeGateway(); }
@Bean PaymentGateway bank() { return new BankGateway(); }
@Service Checkout(PaymentGateway gateway) {}
```

### Expected diagnosis

The injection point has two candidates and no selection rule.

### Corrected code

```java
@Service Checkout(@Qualifier("stripe") PaymentGateway gateway) {}
```

### Regression tests

```java
// Context chooses Stripe only at the qualified injection point.
```

## IOC-H-073: self-invocation bypasses advice

- Difficulty: Hard
- Framework: Spring Core & Inversion of Control
- Language: Java
- Perspective: Proxying
- Concept: self-invocation bypasses advice
- Symptom: The transactional or cached annotation appears ignored.
- Diagnostic goal: Call the advised method through the proxy boundary.

### Buggy code

```java
@Transactional
public void outer() { inner(); }
@Transactional
public void inner() { /* work */ }
```

### Expected diagnosis

A direct this.inner() call never passes through the Spring proxy.

### Corrected code

```java
@Transactional
public void outer() { collaborator.inner(); }
```

### Regression tests

```java
// An integration test observes the transaction/caching advice on inner.
```

## IOC-H-074: request bean used outside request

- Difficulty: Hard
- Framework: Spring Core & Inversion of Control
- Language: Java
- Perspective: Scopes
- Concept: request bean used outside request
- Symptom: A background task throws scope-not-active.
- Diagnostic goal: Capture immutable data, not a request-scoped object, for background work.

### Buggy code

```java
executor.submit(() -> requestContext.getUserId());
```

### Expected diagnosis

The request scope may be gone when the task runs.

### Corrected code

```java
String userId = requestContext.getUserId();
executor.submit(() -> process(userId));
```

### Regression tests

```java
// The task remains valid after the request completes.
```

## IOC-H-075: event published before commit

- Difficulty: Hard
- Framework: Spring Core & Inversion of Control
- Language: Java
- Perspective: Events
- Concept: event published before commit
- Symptom: A listener sees data that later rolls back.
- Diagnostic goal: Publish after a successful transaction commit when required.

### Buggy code

```java
publisher.publishEvent(new OrderCreated(order.id()));
repository.save(order);
```

### Expected diagnosis

The event is emitted before persistence commits and may describe a transaction that fails.

### Corrected code

```java
repository.save(order);
publisher.publishEvent(new OrderCreated(order.id()));
```

### Regression tests

```java
// A transactional listener receives the event only after commit.
```

## IOC-H-076: conditional bean unexpectedly absent

- Difficulty: Hard
- Framework: Spring Core & Inversion of Control
- Language: Java
- Perspective: Factory
- Concept: conditional bean unexpectedly absent
- Symptom: A feature flag has no implementation.
- Diagnostic goal: Check condition names and the effective environment.

### Buggy code

```java
@ConditionalOnProperty(name = "feature.mail")
@Bean Mailer mailer() { return new Mailer(); }
```

### Expected diagnosis

The condition requires a value unless havingValue or matchIfMissing is configured as intended.

### Corrected code

```java
@ConditionalOnProperty(name = "feature.mail", havingValue = "true")
@Bean Mailer mailer() { return new Mailer(); }
```

### Regression tests

```java
// Context reports a bean only when feature.mail=true.
```

## IOC-H-077: close omitted

- Difficulty: Hard
- Framework: Spring Core & Inversion of Control
- Language: Java
- Perspective: Resource lifecycle
- Concept: close omitted
- Symptom: Threads or connections remain after context shutdown.
- Diagnostic goal: Register resources as managed beans with destruction callbacks.

### Buggy code

```java
@Bean ExecutorService executor() { return Executors.newFixedThreadPool(4); }
```

### Expected diagnosis

The container does not know how to stop an arbitrary resource unless destruction is declared.

### Corrected code

```java
@Bean(destroyMethod = "shutdown") ExecutorService executor() { return Executors.newFixedThreadPool(4); }
```

### Regression tests

```java
// Context close invokes shutdown.
```

## IOC-H-078: listener order assumed

- Difficulty: Hard
- Framework: Spring Core & Inversion of Control
- Language: Java
- Perspective: Ordering
- Concept: listener order assumed
- Symptom: Two startup tasks run in the wrong order.
- Diagnostic goal: Declare ordering only where the dependency is real.

### Buggy code

```java
@EventListener
void seed() {}
@EventListener
void publish() {}
```

### Expected diagnosis

Listener registration order is not a reliable dependency contract.

### Corrected code

```java
@Order(1) @EventListener void seed() {}
@Order(2) @EventListener void publish() {}
```

### Regression tests

```java
// The test records seed before publish.
```

## IOC-H-079: optional bean treated as required

- Difficulty: Hard
- Framework: Spring Core & Inversion of Control
- Language: Java
- Perspective: Optional dependencies
- Concept: optional bean treated as required
- Symptom: A feature cannot start without an optional integration.
- Diagnostic goal: Represent optionality explicitly.

### Buggy code

```java
public Reporter(Exporter exporter) { this.exporter = exporter; }
```

### Expected diagnosis

Constructor injection requires Exporter even when the feature is disabled.

### Corrected code

```java
public Reporter(ObjectProvider<Exporter> exporter) { this.exporter = exporter; }
```

### Regression tests

```java
// Reporter starts without Exporter and uses a no-op path.
```

## IOC-H-080: service cycle hidden by field injection

- Difficulty: Hard
- Framework: Spring Core & Inversion of Control
- Language: Java
- Perspective: Circular design
- Concept: service cycle hidden by field injection
- Symptom: Runtime behavior is order-dependent and difficult to test.
- Diagnostic goal: Extract a port or move orchestration into a third component.

### Buggy code

```java
@Autowired A a;
class A { @Autowired B b; }
class B { @Autowired A a; }
```

### Expected diagnosis

Field injection hides the cycle until context creation and makes dependencies mutable.

### Corrected code

```java
class Orchestrator { Orchestrator(A a, B b) {} }
```

### Regression tests

```java
// A and B no longer depend directly on one another.
```

## IOC-H-081: prototype injected into singleton

- Difficulty: Hard
- Framework: Spring Core & Inversion of Control
- Language: Java
- Perspective: Bean lifecycle
- Concept: prototype injected into singleton
- Symptom: A supposed new object is reused.
- Diagnostic goal: Obtain shorter-lived beans through a provider or scoped proxy.

### Buggy code

```java
@Component
class JobRunner { private final Job job; JobRunner(Job job) { this.job = job; } }
```

### Expected diagnosis

A prototype dependency is resolved once when the singleton is constructed.

### Corrected code

```java
@Component
class JobRunner { private final ObjectProvider<Job> jobs; JobRunner(ObjectProvider<Job> jobs) { this.jobs = jobs; }
 Job next() { return jobs.getObject(); } }
```

### Regression tests

```java
// Two calls to next return distinct Job instances.
```

## IOC-H-082: multiple candidates ambiguous

- Difficulty: Hard
- Framework: Spring Core & Inversion of Control
- Language: Java
- Perspective: Injection
- Concept: multiple candidates ambiguous
- Symptom: Context startup reports NoUniqueBeanDefinitionException.
- Diagnostic goal: Qualify the intended implementation or define a primary bean.

### Buggy code

```java
@Bean PaymentGateway stripe() { return new StripeGateway(); }
@Bean PaymentGateway bank() { return new BankGateway(); }
@Service Checkout(PaymentGateway gateway) {}
```

### Expected diagnosis

The injection point has two candidates and no selection rule.

### Corrected code

```java
@Service Checkout(@Qualifier("stripe") PaymentGateway gateway) {}
```

### Regression tests

```java
// Context chooses Stripe only at the qualified injection point.
```

## IOC-H-083: self-invocation bypasses advice

- Difficulty: Hard
- Framework: Spring Core & Inversion of Control
- Language: Java
- Perspective: Proxying
- Concept: self-invocation bypasses advice
- Symptom: The transactional or cached annotation appears ignored.
- Diagnostic goal: Call the advised method through the proxy boundary.

### Buggy code

```java
@Transactional
public void outer() { inner(); }
@Transactional
public void inner() { /* work */ }
```

### Expected diagnosis

A direct this.inner() call never passes through the Spring proxy.

### Corrected code

```java
@Transactional
public void outer() { collaborator.inner(); }
```

### Regression tests

```java
// An integration test observes the transaction/caching advice on inner.
```

## IOC-H-084: request bean used outside request

- Difficulty: Hard
- Framework: Spring Core & Inversion of Control
- Language: Java
- Perspective: Scopes
- Concept: request bean used outside request
- Symptom: A background task throws scope-not-active.
- Diagnostic goal: Capture immutable data, not a request-scoped object, for background work.

### Buggy code

```java
executor.submit(() -> requestContext.getUserId());
```

### Expected diagnosis

The request scope may be gone when the task runs.

### Corrected code

```java
String userId = requestContext.getUserId();
executor.submit(() -> process(userId));
```

### Regression tests

```java
// The task remains valid after the request completes.
```

## IOC-H-085: event published before commit

- Difficulty: Hard
- Framework: Spring Core & Inversion of Control
- Language: Java
- Perspective: Events
- Concept: event published before commit
- Symptom: A listener sees data that later rolls back.
- Diagnostic goal: Publish after a successful transaction commit when required.

### Buggy code

```java
publisher.publishEvent(new OrderCreated(order.id()));
repository.save(order);
```

### Expected diagnosis

The event is emitted before persistence commits and may describe a transaction that fails.

### Corrected code

```java
repository.save(order);
publisher.publishEvent(new OrderCreated(order.id()));
```

### Regression tests

```java
// A transactional listener receives the event only after commit.
```

## IOC-H-086: conditional bean unexpectedly absent

- Difficulty: Hard
- Framework: Spring Core & Inversion of Control
- Language: Java
- Perspective: Factory
- Concept: conditional bean unexpectedly absent
- Symptom: A feature flag has no implementation.
- Diagnostic goal: Check condition names and the effective environment.

### Buggy code

```java
@ConditionalOnProperty(name = "feature.mail")
@Bean Mailer mailer() { return new Mailer(); }
```

### Expected diagnosis

The condition requires a value unless havingValue or matchIfMissing is configured as intended.

### Corrected code

```java
@ConditionalOnProperty(name = "feature.mail", havingValue = "true")
@Bean Mailer mailer() { return new Mailer(); }
```

### Regression tests

```java
// Context reports a bean only when feature.mail=true.
```

## IOC-H-087: close omitted

- Difficulty: Hard
- Framework: Spring Core & Inversion of Control
- Language: Java
- Perspective: Resource lifecycle
- Concept: close omitted
- Symptom: Threads or connections remain after context shutdown.
- Diagnostic goal: Register resources as managed beans with destruction callbacks.

### Buggy code

```java
@Bean ExecutorService executor() { return Executors.newFixedThreadPool(4); }
```

### Expected diagnosis

The container does not know how to stop an arbitrary resource unless destruction is declared.

### Corrected code

```java
@Bean(destroyMethod = "shutdown") ExecutorService executor() { return Executors.newFixedThreadPool(4); }
```

### Regression tests

```java
// Context close invokes shutdown.
```

## IOC-H-088: listener order assumed

- Difficulty: Hard
- Framework: Spring Core & Inversion of Control
- Language: Java
- Perspective: Ordering
- Concept: listener order assumed
- Symptom: Two startup tasks run in the wrong order.
- Diagnostic goal: Declare ordering only where the dependency is real.

### Buggy code

```java
@EventListener
void seed() {}
@EventListener
void publish() {}
```

### Expected diagnosis

Listener registration order is not a reliable dependency contract.

### Corrected code

```java
@Order(1) @EventListener void seed() {}
@Order(2) @EventListener void publish() {}
```

### Regression tests

```java
// The test records seed before publish.
```

## IOC-H-089: optional bean treated as required

- Difficulty: Hard
- Framework: Spring Core & Inversion of Control
- Language: Java
- Perspective: Optional dependencies
- Concept: optional bean treated as required
- Symptom: A feature cannot start without an optional integration.
- Diagnostic goal: Represent optionality explicitly.

### Buggy code

```java
public Reporter(Exporter exporter) { this.exporter = exporter; }
```

### Expected diagnosis

Constructor injection requires Exporter even when the feature is disabled.

### Corrected code

```java
public Reporter(ObjectProvider<Exporter> exporter) { this.exporter = exporter; }
```

### Regression tests

```java
// Reporter starts without Exporter and uses a no-op path.
```

## IOC-H-090: service cycle hidden by field injection

- Difficulty: Hard
- Framework: Spring Core & Inversion of Control
- Language: Java
- Perspective: Circular design
- Concept: service cycle hidden by field injection
- Symptom: Runtime behavior is order-dependent and difficult to test.
- Diagnostic goal: Extract a port or move orchestration into a third component.

### Buggy code

```java
@Autowired A a;
class A { @Autowired B b; }
class B { @Autowired A a; }
```

### Expected diagnosis

Field injection hides the cycle until context creation and makes dependencies mutable.

### Corrected code

```java
class Orchestrator { Orchestrator(A a, B b) {} }
```

### Regression tests

```java
// A and B no longer depend directly on one another.
```

## IOC-H-091: prototype injected into singleton

- Difficulty: Hard
- Framework: Spring Core & Inversion of Control
- Language: Java
- Perspective: Bean lifecycle
- Concept: prototype injected into singleton
- Symptom: A supposed new object is reused.
- Diagnostic goal: Obtain shorter-lived beans through a provider or scoped proxy.

### Buggy code

```java
@Component
class JobRunner { private final Job job; JobRunner(Job job) { this.job = job; } }
```

### Expected diagnosis

A prototype dependency is resolved once when the singleton is constructed.

### Corrected code

```java
@Component
class JobRunner { private final ObjectProvider<Job> jobs; JobRunner(ObjectProvider<Job> jobs) { this.jobs = jobs; }
 Job next() { return jobs.getObject(); } }
```

### Regression tests

```java
// Two calls to next return distinct Job instances.
```

## IOC-H-092: multiple candidates ambiguous

- Difficulty: Hard
- Framework: Spring Core & Inversion of Control
- Language: Java
- Perspective: Injection
- Concept: multiple candidates ambiguous
- Symptom: Context startup reports NoUniqueBeanDefinitionException.
- Diagnostic goal: Qualify the intended implementation or define a primary bean.

### Buggy code

```java
@Bean PaymentGateway stripe() { return new StripeGateway(); }
@Bean PaymentGateway bank() { return new BankGateway(); }
@Service Checkout(PaymentGateway gateway) {}
```

### Expected diagnosis

The injection point has two candidates and no selection rule.

### Corrected code

```java
@Service Checkout(@Qualifier("stripe") PaymentGateway gateway) {}
```

### Regression tests

```java
// Context chooses Stripe only at the qualified injection point.
```

## IOC-H-093: self-invocation bypasses advice

- Difficulty: Hard
- Framework: Spring Core & Inversion of Control
- Language: Java
- Perspective: Proxying
- Concept: self-invocation bypasses advice
- Symptom: The transactional or cached annotation appears ignored.
- Diagnostic goal: Call the advised method through the proxy boundary.

### Buggy code

```java
@Transactional
public void outer() { inner(); }
@Transactional
public void inner() { /* work */ }
```

### Expected diagnosis

A direct this.inner() call never passes through the Spring proxy.

### Corrected code

```java
@Transactional
public void outer() { collaborator.inner(); }
```

### Regression tests

```java
// An integration test observes the transaction/caching advice on inner.
```

## IOC-H-094: request bean used outside request

- Difficulty: Hard
- Framework: Spring Core & Inversion of Control
- Language: Java
- Perspective: Scopes
- Concept: request bean used outside request
- Symptom: A background task throws scope-not-active.
- Diagnostic goal: Capture immutable data, not a request-scoped object, for background work.

### Buggy code

```java
executor.submit(() -> requestContext.getUserId());
```

### Expected diagnosis

The request scope may be gone when the task runs.

### Corrected code

```java
String userId = requestContext.getUserId();
executor.submit(() -> process(userId));
```

### Regression tests

```java
// The task remains valid after the request completes.
```

## IOC-H-095: event published before commit

- Difficulty: Hard
- Framework: Spring Core & Inversion of Control
- Language: Java
- Perspective: Events
- Concept: event published before commit
- Symptom: A listener sees data that later rolls back.
- Diagnostic goal: Publish after a successful transaction commit when required.

### Buggy code

```java
publisher.publishEvent(new OrderCreated(order.id()));
repository.save(order);
```

### Expected diagnosis

The event is emitted before persistence commits and may describe a transaction that fails.

### Corrected code

```java
repository.save(order);
publisher.publishEvent(new OrderCreated(order.id()));
```

### Regression tests

```java
// A transactional listener receives the event only after commit.
```

## IOC-H-096: conditional bean unexpectedly absent

- Difficulty: Hard
- Framework: Spring Core & Inversion of Control
- Language: Java
- Perspective: Factory
- Concept: conditional bean unexpectedly absent
- Symptom: A feature flag has no implementation.
- Diagnostic goal: Check condition names and the effective environment.

### Buggy code

```java
@ConditionalOnProperty(name = "feature.mail")
@Bean Mailer mailer() { return new Mailer(); }
```

### Expected diagnosis

The condition requires a value unless havingValue or matchIfMissing is configured as intended.

### Corrected code

```java
@ConditionalOnProperty(name = "feature.mail", havingValue = "true")
@Bean Mailer mailer() { return new Mailer(); }
```

### Regression tests

```java
// Context reports a bean only when feature.mail=true.
```

## IOC-H-097: close omitted

- Difficulty: Hard
- Framework: Spring Core & Inversion of Control
- Language: Java
- Perspective: Resource lifecycle
- Concept: close omitted
- Symptom: Threads or connections remain after context shutdown.
- Diagnostic goal: Register resources as managed beans with destruction callbacks.

### Buggy code

```java
@Bean ExecutorService executor() { return Executors.newFixedThreadPool(4); }
```

### Expected diagnosis

The container does not know how to stop an arbitrary resource unless destruction is declared.

### Corrected code

```java
@Bean(destroyMethod = "shutdown") ExecutorService executor() { return Executors.newFixedThreadPool(4); }
```

### Regression tests

```java
// Context close invokes shutdown.
```

## IOC-H-098: listener order assumed

- Difficulty: Hard
- Framework: Spring Core & Inversion of Control
- Language: Java
- Perspective: Ordering
- Concept: listener order assumed
- Symptom: Two startup tasks run in the wrong order.
- Diagnostic goal: Declare ordering only where the dependency is real.

### Buggy code

```java
@EventListener
void seed() {}
@EventListener
void publish() {}
```

### Expected diagnosis

Listener registration order is not a reliable dependency contract.

### Corrected code

```java
@Order(1) @EventListener void seed() {}
@Order(2) @EventListener void publish() {}
```

### Regression tests

```java
// The test records seed before publish.
```

## IOC-H-099: optional bean treated as required

- Difficulty: Hard
- Framework: Spring Core & Inversion of Control
- Language: Java
- Perspective: Optional dependencies
- Concept: optional bean treated as required
- Symptom: A feature cannot start without an optional integration.
- Diagnostic goal: Represent optionality explicitly.

### Buggy code

```java
public Reporter(Exporter exporter) { this.exporter = exporter; }
```

### Expected diagnosis

Constructor injection requires Exporter even when the feature is disabled.

### Corrected code

```java
public Reporter(ObjectProvider<Exporter> exporter) { this.exporter = exporter; }
```

### Regression tests

```java
// Reporter starts without Exporter and uses a no-op path.
```

## IOC-H-100: service cycle hidden by field injection

- Difficulty: Hard
- Framework: Spring Core & Inversion of Control
- Language: Java
- Perspective: Circular design
- Concept: service cycle hidden by field injection
- Symptom: Runtime behavior is order-dependent and difficult to test.
- Diagnostic goal: Extract a port or move orchestration into a third component.

### Buggy code

```java
@Autowired A a;
class A { @Autowired B b; }
class B { @Autowired A a; }
```

### Expected diagnosis

Field injection hides the cycle until context creation and makes dependencies mutable.

### Corrected code

```java
class Orchestrator { Orchestrator(A a, B b) {} }
```

### Regression tests

```java
// A and B no longer depend directly on one another.
```
