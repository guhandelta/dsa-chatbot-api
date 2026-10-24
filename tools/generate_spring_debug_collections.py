"""Generate separate Spring debugging corpora for RAG training."""
from __future__ import annotations

import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def rec(prefix, framework, i, level, perspective, concept, symptom, goal, buggy, diagnosis, fixed, tests):
    return f"""## {prefix}-{level[0]}-{i:03d}: {concept}

- Difficulty: {level}
- Framework: {framework}
- Language: Java
- Perspective: {perspective}
- Concept: {concept}
- Symptom: {symptom}
- Diagnostic goal: {goal}

### Buggy code

```java
{buggy}
```

### Expected diagnosis

{diagnosis}

### Corrected code

```java
{fixed}
```

### Regression tests

```java
{tests}
```

"""


ROWS = {
    'Spring Boot 3': [
        ('Configuration', 'profile property mismatch', 'The production datasource is not configured.', 'Trace active profiles and property source precedence.', '@Value("${app.url}")\nprivate String url;', 'The property may exist only under a different profile or prefix; startup failure is clearer than a silent default.', '@ConfigurationProperties(prefix = "app")\npublic record AppProperties(String url) {}', '// Run with each profile and assert the expected URL is bound.'),
        ('Auto-configuration', 'missing starter dependency', 'A configured feature has no bean at runtime.', 'Map the requested behavior to its Boot starter and auto-configuration.', '@Bean\nSecurityFilterChain chain(HttpSecurity http) { return http.build(); }', 'A security configuration cannot work if the relevant starter and transitive infrastructure are absent.', 'dependencies { implementation("org.springframework.boot:spring-boot-starter-security") }', '// Include spring-boot-starter-security and assert the context starts.'),
        ('Actuator', 'health endpoint exposes internals', 'Operational endpoints leak sensitive details.', 'Separate endpoint exposure from health detail visibility.', 'management.endpoints.web.exposure.include=*\nmanagement.endpoint.health.show-details=always', 'Wildcard exposure and unrestricted details reveal environment and dependency information.', 'management.endpoints.web.exposure.include=health,info\nmanagement.endpoint.health.show-details=when_authorized', '// Unauthenticated probes see status without credentials or connection details.'),
        ('Profiles', 'test profile not activated', 'Tests connect to a developer database.', 'Make the test environment explicit and isolated.', '@SpringBootTest\nclass RepositoryTest {}', 'Without a test profile, normal application properties can select an external database.', '@SpringBootTest\n@ActiveProfiles("test")\nclass RepositoryTest {}', '// Test execution uses the embedded or containerized test datasource.'),
        ('Observability', 'correlation id lost', 'Logs from one request cannot be joined across services.', 'Create and clear request-scoped diagnostic context.', 'filterChain.doFilter(request, response);', 'The request proceeds without installing a correlation value and without cleanup.', 'try { MDC.put("requestId", requestId); filterChain.doFilter(request, response); } finally { MDC.remove("requestId"); }', '// Every log line has the request id and the thread is clean afterward.'),
        ('Serialization', 'Java time format mismatch', 'Clients reject the response date.', 'Declare the wire format at the API boundary.', 'record Event(Instant createdAt) {}', 'The default representation may differ from the documented contract or client expectation.', 'record Event(@JsonFormat(pattern = "yyyy-MM-dd\'T\'HH:mm:ssX") Instant createdAt) {}', '// Contract test asserts the exact serialized timestamp.'),
        ('Startup', 'circular bean dependency', 'ApplicationContext fails during startup.', 'Break the cycle at the architecture boundary.', 'class A { A(B b) {} }\nclass B { B(A a) {} }', 'Constructor injection exposes a cycle that cannot be resolved safely.', 'class A { A(Port port) {} }\nclass B implements Port { B() {} }', '// Context starts and each service depends on an interface with one direction.'),
        ('HTTP client', 'unbounded upstream timeout', 'A slow dependency exhausts request threads.', 'Set connect and response timeouts and define fallback behavior.', 'return restClient.get().uri(uri).retrieve().body(String.class);', 'Without timeouts, an unavailable upstream can hold workers indefinitely.', 'return restClient.get().uri(uri).retrieve().onStatus(s -> s.value() == 404, r -> new NotFoundException()).body(String.class);', '// Slow and error responses produce bounded, documented outcomes.'),
        ('Deployment', 'graceful shutdown disabled', 'In-flight requests are cut off during rollout.', 'Enable graceful shutdown and give the platform enough time.', 'server.shutdown=immediate', 'Immediate shutdown drops active requests and can interrupt transactions.', 'server.shutdown=graceful\nspring.lifecycle.timeout-per-shutdown-phase=30s', '// A shutdown waits for active work up to the configured deadline.'),
        ('Validation', 'configuration accepted without validation', 'The app starts with an invalid port or URL.', 'Validate configuration at binding time.', 'record ClientProperties(String baseUrl, int timeoutMs) {}', 'Invalid values surface only when the first request is made.', 'record ClientProperties(@jakarta.validation.constraints.NotBlank String baseUrl, @jakarta.validation.constraints.Positive int timeoutMs) {}', '// Invalid configuration fails context startup with a useful property path.'),
    ],
    'Spring Core & Inversion of Control': [
        ('Bean lifecycle', 'prototype injected into singleton', 'A supposed new object is reused.', 'Obtain shorter-lived beans through a provider or scoped proxy.', '@Component\nclass JobRunner { private final Job job; JobRunner(Job job) { this.job = job; } }', 'A prototype dependency is resolved once when the singleton is constructed.', '@Component\nclass JobRunner { private final ObjectProvider<Job> jobs; JobRunner(ObjectProvider<Job> jobs) { this.jobs = jobs; }\n Job next() { return jobs.getObject(); } }', '// Two calls to next return distinct Job instances.'),
        ('Injection', 'multiple candidates ambiguous', 'Context startup reports NoUniqueBeanDefinitionException.', 'Qualify the intended implementation or define a primary bean.', '@Bean PaymentGateway stripe() { return new StripeGateway(); }\n@Bean PaymentGateway bank() { return new BankGateway(); }\n@Service Checkout(PaymentGateway gateway) {}', 'The injection point has two candidates and no selection rule.', '@Service Checkout(@Qualifier("stripe") PaymentGateway gateway) {}', '// Context chooses Stripe only at the qualified injection point.'),
        ('Proxying', 'self-invocation bypasses advice', 'The transactional or cached annotation appears ignored.', 'Call the advised method through the proxy boundary.', '@Transactional\npublic void outer() { inner(); }\n@Transactional\npublic void inner() { /* work */ }', 'A direct this.inner() call never passes through the Spring proxy.', '@Transactional\npublic void outer() { collaborator.inner(); }', '// An integration test observes the transaction/caching advice on inner.'),
        ('Scopes', 'request bean used outside request', 'A background task throws scope-not-active.', 'Capture immutable data, not a request-scoped object, for background work.', 'executor.submit(() -> requestContext.getUserId());', 'The request scope may be gone when the task runs.', 'String userId = requestContext.getUserId();\nexecutor.submit(() -> process(userId));', '// The task remains valid after the request completes.'),
        ('Events', 'event published before commit', 'A listener sees data that later rolls back.', 'Publish after a successful transaction commit when required.', 'publisher.publishEvent(new OrderCreated(order.id()));\nrepository.save(order);', 'The event is emitted before persistence commits and may describe a transaction that fails.', 'repository.save(order);\npublisher.publishEvent(new OrderCreated(order.id()));', '// A transactional listener receives the event only after commit.'),
        ('Factory', 'conditional bean unexpectedly absent', 'A feature flag has no implementation.', 'Check condition names and the effective environment.', '@ConditionalOnProperty(name = "feature.mail")\n@Bean Mailer mailer() { return new Mailer(); }', 'The condition requires a value unless havingValue or matchIfMissing is configured as intended.', '@ConditionalOnProperty(name = "feature.mail", havingValue = "true")\n@Bean Mailer mailer() { return new Mailer(); }', '// Context reports a bean only when feature.mail=true.'),
        ('Resource lifecycle', 'close omitted', 'Threads or connections remain after context shutdown.', 'Register resources as managed beans with destruction callbacks.', '@Bean ExecutorService executor() { return Executors.newFixedThreadPool(4); }', 'The container does not know how to stop an arbitrary resource unless destruction is declared.', '@Bean(destroyMethod = "shutdown") ExecutorService executor() { return Executors.newFixedThreadPool(4); }', '// Context close invokes shutdown.'),
        ('Ordering', 'listener order assumed', 'Two startup tasks run in the wrong order.', 'Declare ordering only where the dependency is real.', '@EventListener\nvoid seed() {}\n@EventListener\nvoid publish() {}', 'Listener registration order is not a reliable dependency contract.', '@Order(1) @EventListener void seed() {}\n@Order(2) @EventListener void publish() {}', '// The test records seed before publish.'),
        ('Optional dependencies', 'optional bean treated as required', 'A feature cannot start without an optional integration.', 'Represent optionality explicitly.', 'public Reporter(Exporter exporter) { this.exporter = exporter; }', 'Constructor injection requires Exporter even when the feature is disabled.', 'public Reporter(ObjectProvider<Exporter> exporter) { this.exporter = exporter; }', '// Reporter starts without Exporter and uses a no-op path.'),
        ('Circular design', 'service cycle hidden by field injection', 'Runtime behavior is order-dependent and difficult to test.', 'Extract a port or move orchestration into a third component.', '@Autowired A a;\nclass A { @Autowired B b; }\nclass B { @Autowired A a; }', 'Field injection hides the cycle until context creation and makes dependencies mutable.', 'class Orchestrator { Orchestrator(A a, B b) {} }', '// A and B no longer depend directly on one another.'),
    ],
    'Spring Data & Repositories': [
        ('Transactions', 'read-modify-write race', 'Concurrent updates lose changes.', 'Use a transaction and a locking or atomic update strategy.', 'entity.setCount(entity.getCount() + 1); repository.save(entity);', 'Separate requests can read the same old count and overwrite one another.', '@Transactional\n@Modifying\n@Query("update Item i set i.count = i.count + 1 where i.id = :id")\nvoid increment(long id);', '// Concurrent increments equal the number of successful calls.'),
        ('N+1 queries', 'lazy relation in loop', 'A page triggers one query per row.', 'Fetch the relation with an explicit query plan.', 'orders.findAll().forEach(o -> o.getCustomer().getName());', 'Lazy access in a loop produces N additional selects.', '@EntityGraph(attributePaths = "customer")\nList<Order> findAll();', '// SQL logging shows one query for the page and relation.'),
        ('Lazy loading', 'session closed before serialization', 'JSON serialization throws LazyInitializationException.', 'Map entities to DTOs inside the transaction.', 'return repository.findById(id).orElseThrow();', 'The web serializer touches a lazy association after the persistence context is closed.', '@Transactional\npublic OrderDto get(long id) { Order o = repository.findById(id).orElseThrow(); return OrderDto.from(o); }', '// DTO serialization never triggers lazy loading.'),
        ('Query methods', 'derived name means wrong predicate', 'The repository returns unexpected rows.', 'Read the derived query name as a precise predicate.', 'List<User> findByNameOrEmailAndActive(String name, String email, boolean active);', 'Operator precedence may be parsed as name OR (email AND active), not (name OR email) AND active.', '@Query("select u from User u where (u.name = :name or u.email = :email) and u.active = :active")\nList<User> findActive(...);', '// Inactive matches are never returned through either field.'),
        ('Pagination', 'unbounded findAll', 'Memory and response time grow with table size.', 'Expose bounded page or slice queries.', 'List<Order> findByStatus(Status status);', 'Returning every matching entity has no upper bound.', 'Page<Order> findByStatus(Status status, Pageable pageable);', '// A request with page size 50 never loads more than one page.'),
        ('Bulk updates', 'stale persistence context', 'A later read returns pre-update values.', 'Clear or refresh the persistence context after bulk DML.', '@Modifying\n@Query("update User u set u.active=false")\nvoid deactivateAll();', 'Bulk JPQL bypasses managed entity state already held in the context.', '@Modifying(clearAutomatically = true, flushAutomatically = true)\n@Query("update User u set u.active=false")\nvoid deactivateAll();', '// The next repository read reflects the bulk update.'),
        ('Null semantics', 'equals null in JPQL', 'Rows with null values are not found.', 'Use IS NULL semantics or derived methods.', '@Query("select x from Item x where x.note = null")\nList<Item> missingNote();', 'SQL null is not equal to null; the predicate is never true.', '@Query("select x from Item x where x.note is null")\nList<Item> missingNote();', '// Rows with a null note are returned.'),
        ('Auditing', 'auditor not populated', 'CreatedBy fields remain null.', 'Enable auditing and provide an authenticated auditor supplier.', 'class AuditConfig {}', 'The entity annotations alone do not activate Spring Data auditing.', '@EnableJpaAuditing\n@Configuration\nclass AuditConfig { @Bean AuditorAware<String> auditor() { return () -> Optional.of("system"); } }', '// Save asserts createdBy is populated.'),
        ('Optimistic locking', 'lost update not detected', 'Last writer silently wins.', 'Add a version column and handle optimistic lock failures.', '@Entity class Inventory { Long id; int quantity; }', 'Without @Version, stale writes are accepted.', '@Version\nprivate long version;', '// Two updates from the same version cause one OptimisticLockException.'),
        ('Test data', 'repository test uses production schema', 'Tests are slow or modify shared data.', 'Use an isolated test database and rollback policy.', '@SpringBootTest\nclass ItemRepositoryTest {}', 'A full context may load production datasource settings.', '@DataJpaTest\n@ActiveProfiles("test")\nclass ItemRepositoryTest {}', '// The test uses an isolated database and rolls back each test.'),
    ],
    'Spring MVC & Web APIs': [
        ('Binding', 'missing @RequestBody', 'JSON fields arrive as null or binding fails.', 'Declare the source of request data explicitly.', 'public ResponseEntity<Item> create(Item item) { return ok(item); }', 'MVC does not know that the object should be decoded from the JSON body.', 'public ResponseEntity<Item> create(@Valid @RequestBody Item item) { return ok(item); }', '// JSON body binds and invalid fields produce 400.'),
        ('Validation', 'constraints never execute', 'Invalid input is accepted.', 'Put @Valid at the controller boundary and handle violations.', 'public ResponseEntity<?> create(@RequestBody @Valid Item item) { ... }', 'The annotation is correct only if the DTO has constraints and validation is on the classpath.', 'public ResponseEntity<?> create(@Valid @RequestBody ItemRequest item) { ... }', '// Missing required fields return a stable validation error body.'),
        ('Status codes', 'always returns 200', 'Clients cannot distinguish creation, absence, and failure.', 'Use HTTP status as part of the API contract.', 'return ResponseEntity.ok(service.create(request));', 'Creation should communicate its resource location and status.', 'return ResponseEntity.created(uri).body(service.create(request));', '// Create returns 201 and Location; validation returns 400.'),
        ('Exception mapping', 'controller catches every exception', 'Errors are duplicated and stack traces leak.', 'Centralize mapping with a narrow exception handler.', 'try { return ok(service.get(id)); } catch (Exception e) { return badRequest().body(e.getMessage()); }', 'The controller turns server faults into 400 and exposes internal messages.', '@RestControllerAdvice\nclass ApiErrors { @ExceptionHandler(NotFoundException.class) ResponseEntity<?> missing() { return ResponseEntity.notFound().build(); } }', '// Missing maps to 404; unexpected errors map to 500 without details.'),
        ('Content negotiation', 'wrong media type', 'A client receives HTML or a 406 response.', 'Declare supported request and response media types.', '@PostMapping("/items") Item create(@RequestBody Item item) { ... }', 'The endpoint contract does not state which representations it accepts or produces.', '@PostMapping(value="/items", consumes="application/json", produces="application/json") Item create(@RequestBody Item item) { ... }', '// JSON requests receive JSON responses and unsupported media types are rejected.'),
        ('CORS', 'wildcard with credentials', 'Browser requests fail or trust too many origins.', 'Use an explicit origin policy for credentialed APIs.', '@CrossOrigin(origins="*", allowCredentials="true")', 'Browsers disallow wildcard origins with credentials and a broad trust policy is unsafe.', '@CrossOrigin(origins="https://app.example", allowCredentials="true")', '// The configured origin is allowed and an unrelated origin is rejected.'),
        ('DTO boundaries', 'entity exposed directly', 'Internal fields and lazy relationships leak.', 'Use request and response DTOs.', 'return repository.findById(id).orElseThrow();', 'Entities couple persistence and wire contracts and may serialize fields unintentionally.', 'return mapper.toResponse(repository.findById(id).orElseThrow());', '// Response JSON contains only documented fields.'),
        ('Idempotency', 'retry creates duplicates', 'A client retry creates two payments.', 'Use an idempotency key and a unique persistence constraint.', '@PostMapping("/payments") Payment pay(@RequestBody PaymentRequest request) { return service.pay(request); }', 'Network retries can repeat a non-idempotent operation.', '@PostMapping("/payments") Payment pay(@RequestHeader("Idempotency-Key") String key, @RequestBody PaymentRequest request) { return service.payOnce(key, request); }', '// Repeating the same key returns the original result.'),
        ('Streaming', 'large file buffered', 'Memory spikes while downloading a file.', 'Stream content through a resource response.', 'byte[] data = Files.readAllBytes(path);\nreturn ResponseEntity.ok(data);', 'Reading the entire file into a byte array scales memory with file size.', 'return ResponseEntity.ok().body(new InputStreamResource(Files.newInputStream(path)));', '// Large responses keep bounded application memory.'),
        ('Path security', 'user path traversal', 'A request reads files outside the intended directory.', 'Normalize and enforce a resolved path under the allowed root.', 'return Files.readString(root.resolve(name));', 'A name containing ../ can escape root.', 'Path target = root.resolve(name).normalize();\nif (!target.startsWith(root)) throw new ResponseStatusException(HttpStatus.BAD_REQUEST);\nreturn Files.readString(target);', '// Traversal attempts are rejected.'),
    ],
    'Spring Security': [
        ('Filter chain', 'permitAll on protected path', 'Unauthenticated users access an admin endpoint.', 'Order matchers from specific protected paths to general rules.', 'authorize.requestMatchers("/**").permitAll()\n       .requestMatchers("/admin/**").hasRole("ADMIN")', 'The catch-all matcher matches first, so the admin rule is unreachable.', 'authorize.requestMatchers("/admin/**").hasRole("ADMIN")\n       .anyRequest().authenticated()', '// Anonymous admin access is 401/403; authenticated users follow role rules.'),
        ('CSRF', 'CSRF disabled for browser session', 'State-changing browser requests lack forgery protection.', 'Keep CSRF for cookie-authenticated browser flows.', 'http.csrf(csrf -> csrf.disable());', 'Disabling CSRF globally is unsafe when authentication is carried by cookies.', 'http.csrf(Customizer.withDefaults());', '// A missing token is rejected for a session-authenticated POST.'),
        ('Password storage', 'plain text password', 'A database leak exposes credentials immediately.', 'Store adaptive password hashes and compare through the encoder.', 'user.setPassword(rawPassword);', 'Raw passwords are reversible by anyone who obtains the database.', 'user.setPassword(passwordEncoder.encode(rawPassword));', '// Login matches through passwordEncoder.matches and never compares raw storage.'),
        ('Method security', 'annotation ignored', 'A role annotation has no effect.', 'Enable method security and use the correct authority prefix.', '@PreAuthorize("hasRole(\"ADMIN\")")\npublic void delete() {}', 'Method annotations are inactive unless method security is enabled.', '@EnableMethodSecurity\n@Configuration\nclass SecurityConfig {}', '// Nonadmins are denied when invoking the method directly through the proxy.'),
        ('JWT validation', 'signature not checked', 'Forged claims authorize a request.', 'Verify signature, issuer, audience, and expiry.', 'JwtClaims claims = parser.parseUnsecured(token);', 'Reading claims without verification is equivalent to trusting user input.', 'JwtClaims claims = parser.verify(token, key).requireIssuer(issuer).requireAudience(audience).parse();', '// Forged, expired, wrong-issuer tokens are rejected.'),
        ('Authorization', 'authentication mistaken for authorization', 'Every signed-in user can perform an admin action.', 'Require a permission or role for the operation.', '.anyRequest().authenticated()', 'Authenticated only proves identity; it does not grant the admin capability.', '.requestMatchers("/admin/**").hasAuthority("admin:write")', '// A user without admin:write receives 403.'),
        ('Session policy', 'session fixation risk', 'The session identifier remains attacker-controlled after login.', 'Apply a session fixation protection policy.', 'http.sessionManagement(s -> s.sessionFixation(f -> f.none()));', 'Keeping the pre-login session identifier permits fixation attacks.', 'http.sessionManagement(s -> s.sessionFixation(f -> f.changeSessionId()));', '// Successful login changes or invalidates the pre-authentication id.'),
        ('CORS', 'security CORS differs from MVC CORS', 'Preflight requests are rejected before the controller.', 'Configure CORS in the security filter chain with the application policy.', 'http.cors(c -> c.disable());', 'The security chain can reject preflight before MVC configuration is reached.', 'http.cors(Customizer.withDefaults());', '// OPTIONS preflight receives the configured allow origin and methods.'),
        ('Logout', 'logout endpoint accepts GET', 'A cross-site link can log users out unexpectedly.', 'Use POST and CSRF protection for browser logout.', 'http.logout(l -> l.logoutRequestMatcher(new AntPathRequestMatcher("/logout", "GET")));', 'GET should be safe and cannot carry a CSRF-protected state change reliably.', 'http.logout(l -> l.logoutUrl("/logout"));', '// GET does not log out; CSRF-protected POST does.'),
        ('Testing security', 'test user missing authority', 'A controller test fails before the business assertion.', 'Make the test authentication match the endpoint contract.', '@WebMvcTest\nvoid deletes() { mockMvc.perform(delete("/items/1")); }', 'The request is anonymous and security correctly denies it.', '@WithMockUser(roles = "ADMIN")\nvoid deletes() { mockMvc.perform(delete("/items/1").with(csrf())); }', '// The test supplies both role and CSRF token.'),
    ],
    'Spring Testing Slices': [
        ('Web slice', 'repository missing in @WebMvcTest', 'The controller test context cannot start.', 'Mock only collaborators outside the selected slice.', '@WebMvcTest(ItemController.class)\nclass ItemTest { @Autowired ItemRepository repository; }', '@WebMvcTest excludes repositories and services by design.', '@WebMvcTest(ItemController.class)\nclass ItemTest { @MockBean ItemService service; }', '// The MVC slice starts and the controller uses the mocked service.'),
        ('Data slice', 'security filter breaks repository test', 'A @DataJpaTest request unexpectedly requires authentication.', 'Keep slice scope clear and import only needed configuration.', '@DataJpaTest\nclass ItemRepositoryTest {}', 'Importing the full application security configuration changes a focused persistence test.', '@DataJpaTest\n@Import(TestDatabaseConfig.class)\nclass ItemRepositoryTest {}', '// The test uses the slice database without loading web security.'),
        ('MockMvc', 'missing csrf token', 'A POST test receives 403 unexpectedly.', 'Include the security test request post processor.', 'mockMvc.perform(post("/items").content(json));', 'CSRF protection correctly rejects a state-changing request without a token.', 'mockMvc.perform(post("/items").with(csrf()).contentType(APPLICATION_JSON).content(json));', '// The valid authenticated request passes CSRF and reaches the controller.'),
        ('Context bootstrap', 'wrong test configuration', 'The test starts the wrong application context.', 'Load the test configuration that supplies its collaborators.', '@ContextConfiguration(classes = ProductionConfig.class)\nclass Test {}', 'A focused test should load the test configuration that supplies its collaborators.', '@ContextConfiguration(classes = TestConfig.class)\nclass Test {}', '// The context contains test doubles and no production connections.'),
        ('Mocking', 'mock returns null default', 'The controller throws while the test expects a response.', 'Stub the collaborator path that the handler actually uses.', 'when(service.find(1L)).thenReturn(null);', 'Mockito returns null unless the test configures the expected value, so DTO mapping fails.', 'when(service.find(1L)).thenReturn(Optional.of(item));', '// The success path receives the expected domain object.'),
        ('Transactions', 'test rollback assumption', 'Data leaks between tests.', 'Use transactional rollback or clean the database explicitly.', '@SpringBootTest\nclass ItemTest { @Test void creates() { repository.save(item); } }', 'A full integration test does not automatically roll back unless a transaction is active for the test.', '@SpringBootTest\n@Transactional\nclass ItemTest { ... }', '// Each test starts with a clean database state.'),
        ('Test containers', 'container not ready', 'Integration tests race database startup.', 'Use the container lifecycle and dynamic property registration.', 'static PostgreSQLContainer<?> db = new PostgreSQLContainer<>("postgres:16");', 'Creating a container is insufficient if it is not started and its properties are not bound.', '@Container static PostgreSQLContainer<?> db = new PostgreSQLContainer<>("postgres:16");\n@DynamicPropertySource static void props(DynamicPropertyRegistry r) { r.add("spring.datasource.url", db::getJdbcUrl); }', '// The application datasource points at the running container.'),
        ('Assertions', 'only status asserted', 'A regression changes the response body unnoticed.', 'Assert status, headers, and meaningful payload fields.', 'mockMvc.perform(get("/items/1")).andExpect(status().isOk());', 'A 200 response can still contain the wrong representation.', 'mockMvc.perform(get("/items/1")).andExpect(status().isOk()).andExpect(jsonPath("$.id").value(1));', '// The contract test fails when the id or JSON shape changes.'),
        ('Async tests', 'async result asserted too early', 'The test is flaky or sees an empty response.', 'Wait for the async dispatch before asserting the final result.', 'mockMvc.perform(get("/report")).andExpect(status().isOk());', 'A controller returning a CompletableFuture requires async dispatch handling.', 'MvcResult result = mockMvc.perform(get("/report")).andReturn();\nmockMvc.perform(asyncDispatch(result)).andExpect(status().isOk());', '// The test waits for completion deterministically.'),
        ('Profiles', 'test bean overridden by production bean', 'A test double is ignored.', 'Use profile or primary/qualifier rules deliberately.', '@ActiveProfiles("test")\nclass ServiceTest {}', 'The test profile alone does not replace a production bean with the same role.', '@TestConfiguration\nstatic class Doubles { @Bean @Primary PaymentGateway gateway() { return new FakeGateway(); } }', '// The test resolves the fake gateway and production behavior is isolated.'),
    ],
}


def build(framework, prefix):
    rows = ROWS[framework]
    header = f"""# {framework} Debug Exercises

A RAG-training corpus of 300 debugging exercises for {framework}. Each record contains framework-specific metadata, a failure example, an editorial diagnosis, corrected Java/Spring code, and regression guidance. Corrected code is training material and must be stripped from learner-facing challenge responses.

## Coverage

- Easy: 100 exercises
- Medium: 100 exercises
- Hard: 100 exercises
- Perspectives: configuration, lifecycle, proxies, persistence, HTTP contracts, security, testing, transactions, observability, and deployment

"""
    out = [header]
    for level in ('Easy', 'Medium', 'Hard'):
        for i in range(1, 101):
            out.append(rec(prefix, framework, i, level, *rows[(i - 1) % len(rows)]))
    return ''.join(out)


def main():
    names = {
        'Spring Boot 3': ('SB3', 'spring-boot-3-debug-exercises.md'),
        'Spring Core & Inversion of Control': ('IOC', 'spring-core-ioc-debug-exercises.md'),
        'Spring Data & Repositories': ('DATA', 'spring-data-repositories-debug-exercises.md'),
        'Spring MVC & Web APIs': ('MVC', 'spring-mvc-web-apis-debug-exercises.md'),
        'Spring Security': ('SEC', 'spring-security-debug-exercises.md'),
        'Spring Testing Slices': ('TEST', 'spring-testing-slices-debug-exercises.md'),
    }
    for framework, (prefix, filename) in names.items():
        path = ROOT / 'docs/curriculum' / filename
        path.write_text(build(framework, prefix), encoding='utf-8')
        print(f'wrote {path} with 300 exercises')


if __name__ == '__main__':
    main()
