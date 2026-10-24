# Spring Testing Slices Debug Exercises

A RAG-training corpus of 300 debugging exercises for Spring Testing Slices. Each record contains framework-specific metadata, a failure example, an editorial diagnosis, corrected Java/Spring code, and regression guidance. Corrected code is training material and must be stripped from learner-facing challenge responses.

## Coverage

- Easy: 100 exercises
- Medium: 100 exercises
- Hard: 100 exercises
- Perspectives: configuration, lifecycle, proxies, persistence, HTTP contracts, security, testing, transactions, observability, and deployment

## TEST-E-001: repository missing in @WebMvcTest

- Difficulty: Easy
- Framework: Spring Testing Slices
- Language: Java
- Perspective: Web slice
- Concept: repository missing in @WebMvcTest
- Symptom: The controller test context cannot start.
- Diagnostic goal: Mock only collaborators outside the selected slice.

### Buggy code

```java
@WebMvcTest(ItemController.class)
class ItemTest { @Autowired ItemRepository repository; }
```

### Expected diagnosis

@WebMvcTest excludes repositories and services by design.

### Corrected code

```java
@WebMvcTest(ItemController.class)
class ItemTest { @MockBean ItemService service; }
```

### Regression tests

```java
// The MVC slice starts and the controller uses the mocked service.
```

## TEST-E-002: security filter breaks repository test

- Difficulty: Easy
- Framework: Spring Testing Slices
- Language: Java
- Perspective: Data slice
- Concept: security filter breaks repository test
- Symptom: A @DataJpaTest request unexpectedly requires authentication.
- Diagnostic goal: Keep slice scope clear and import only needed configuration.

### Buggy code

```java
@DataJpaTest
class ItemRepositoryTest {}
```

### Expected diagnosis

Importing the full application security configuration changes a focused persistence test.

### Corrected code

```java
@DataJpaTest
@Import(TestDatabaseConfig.class)
class ItemRepositoryTest {}
```

### Regression tests

```java
// The test uses the slice database without loading web security.
```

## TEST-E-003: missing csrf token

- Difficulty: Easy
- Framework: Spring Testing Slices
- Language: Java
- Perspective: MockMvc
- Concept: missing csrf token
- Symptom: A POST test receives 403 unexpectedly.
- Diagnostic goal: Include the security test request post processor.

### Buggy code

```java
mockMvc.perform(post("/items").content(json));
```

### Expected diagnosis

CSRF protection correctly rejects a state-changing request without a token.

### Corrected code

```java
mockMvc.perform(post("/items").with(csrf()).contentType(APPLICATION_JSON).content(json));
```

### Regression tests

```java
// The valid authenticated request passes CSRF and reaches the controller.
```

## TEST-E-004: wrong test configuration

- Difficulty: Easy
- Framework: Spring Testing Slices
- Language: Java
- Perspective: Context bootstrap
- Concept: wrong test configuration
- Symptom: The test starts the wrong application context.
- Diagnostic goal: Load the test configuration that supplies its collaborators.

### Buggy code

```java
@ContextConfiguration(classes = ProductionConfig.class)
class Test {}
```

### Expected diagnosis

A focused test should load the test configuration that supplies its collaborators.

### Corrected code

```java
@ContextConfiguration(classes = TestConfig.class)
class Test {}
```

### Regression tests

```java
// The context contains test doubles and no production connections.
```

## TEST-E-005: mock returns null default

- Difficulty: Easy
- Framework: Spring Testing Slices
- Language: Java
- Perspective: Mocking
- Concept: mock returns null default
- Symptom: The controller throws while the test expects a response.
- Diagnostic goal: Stub the collaborator path that the handler actually uses.

### Buggy code

```java
when(service.find(1L)).thenReturn(null);
```

### Expected diagnosis

Mockito returns null unless the test configures the expected value, so DTO mapping fails.

### Corrected code

```java
when(service.find(1L)).thenReturn(Optional.of(item));
```

### Regression tests

```java
// The success path receives the expected domain object.
```

## TEST-E-006: test rollback assumption

- Difficulty: Easy
- Framework: Spring Testing Slices
- Language: Java
- Perspective: Transactions
- Concept: test rollback assumption
- Symptom: Data leaks between tests.
- Diagnostic goal: Use transactional rollback or clean the database explicitly.

### Buggy code

```java
@SpringBootTest
class ItemTest { @Test void creates() { repository.save(item); } }
```

### Expected diagnosis

A full integration test does not automatically roll back unless a transaction is active for the test.

### Corrected code

```java
@SpringBootTest
@Transactional
class ItemTest { ... }
```

### Regression tests

```java
// Each test starts with a clean database state.
```

## TEST-E-007: container not ready

- Difficulty: Easy
- Framework: Spring Testing Slices
- Language: Java
- Perspective: Test containers
- Concept: container not ready
- Symptom: Integration tests race database startup.
- Diagnostic goal: Use the container lifecycle and dynamic property registration.

### Buggy code

```java
static PostgreSQLContainer<?> db = new PostgreSQLContainer<>("postgres:16");
```

### Expected diagnosis

Creating a container is insufficient if it is not started and its properties are not bound.

### Corrected code

```java
@Container static PostgreSQLContainer<?> db = new PostgreSQLContainer<>("postgres:16");
@DynamicPropertySource static void props(DynamicPropertyRegistry r) { r.add("spring.datasource.url", db::getJdbcUrl); }
```

### Regression tests

```java
// The application datasource points at the running container.
```

## TEST-E-008: only status asserted

- Difficulty: Easy
- Framework: Spring Testing Slices
- Language: Java
- Perspective: Assertions
- Concept: only status asserted
- Symptom: A regression changes the response body unnoticed.
- Diagnostic goal: Assert status, headers, and meaningful payload fields.

### Buggy code

```java
mockMvc.perform(get("/items/1")).andExpect(status().isOk());
```

### Expected diagnosis

A 200 response can still contain the wrong representation.

### Corrected code

```java
mockMvc.perform(get("/items/1")).andExpect(status().isOk()).andExpect(jsonPath("$.id").value(1));
```

### Regression tests

```java
// The contract test fails when the id or JSON shape changes.
```

## TEST-E-009: async result asserted too early

- Difficulty: Easy
- Framework: Spring Testing Slices
- Language: Java
- Perspective: Async tests
- Concept: async result asserted too early
- Symptom: The test is flaky or sees an empty response.
- Diagnostic goal: Wait for the async dispatch before asserting the final result.

### Buggy code

```java
mockMvc.perform(get("/report")).andExpect(status().isOk());
```

### Expected diagnosis

A controller returning a CompletableFuture requires async dispatch handling.

### Corrected code

```java
MvcResult result = mockMvc.perform(get("/report")).andReturn();
mockMvc.perform(asyncDispatch(result)).andExpect(status().isOk());
```

### Regression tests

```java
// The test waits for completion deterministically.
```

## TEST-E-010: test bean overridden by production bean

- Difficulty: Easy
- Framework: Spring Testing Slices
- Language: Java
- Perspective: Profiles
- Concept: test bean overridden by production bean
- Symptom: A test double is ignored.
- Diagnostic goal: Use profile or primary/qualifier rules deliberately.

### Buggy code

```java
@ActiveProfiles("test")
class ServiceTest {}
```

### Expected diagnosis

The test profile alone does not replace a production bean with the same role.

### Corrected code

```java
@TestConfiguration
static class Doubles { @Bean @Primary PaymentGateway gateway() { return new FakeGateway(); } }
```

### Regression tests

```java
// The test resolves the fake gateway and production behavior is isolated.
```

## TEST-E-011: repository missing in @WebMvcTest

- Difficulty: Easy
- Framework: Spring Testing Slices
- Language: Java
- Perspective: Web slice
- Concept: repository missing in @WebMvcTest
- Symptom: The controller test context cannot start.
- Diagnostic goal: Mock only collaborators outside the selected slice.

### Buggy code

```java
@WebMvcTest(ItemController.class)
class ItemTest { @Autowired ItemRepository repository; }
```

### Expected diagnosis

@WebMvcTest excludes repositories and services by design.

### Corrected code

```java
@WebMvcTest(ItemController.class)
class ItemTest { @MockBean ItemService service; }
```

### Regression tests

```java
// The MVC slice starts and the controller uses the mocked service.
```

## TEST-E-012: security filter breaks repository test

- Difficulty: Easy
- Framework: Spring Testing Slices
- Language: Java
- Perspective: Data slice
- Concept: security filter breaks repository test
- Symptom: A @DataJpaTest request unexpectedly requires authentication.
- Diagnostic goal: Keep slice scope clear and import only needed configuration.

### Buggy code

```java
@DataJpaTest
class ItemRepositoryTest {}
```

### Expected diagnosis

Importing the full application security configuration changes a focused persistence test.

### Corrected code

```java
@DataJpaTest
@Import(TestDatabaseConfig.class)
class ItemRepositoryTest {}
```

### Regression tests

```java
// The test uses the slice database without loading web security.
```

## TEST-E-013: missing csrf token

- Difficulty: Easy
- Framework: Spring Testing Slices
- Language: Java
- Perspective: MockMvc
- Concept: missing csrf token
- Symptom: A POST test receives 403 unexpectedly.
- Diagnostic goal: Include the security test request post processor.

### Buggy code

```java
mockMvc.perform(post("/items").content(json));
```

### Expected diagnosis

CSRF protection correctly rejects a state-changing request without a token.

### Corrected code

```java
mockMvc.perform(post("/items").with(csrf()).contentType(APPLICATION_JSON).content(json));
```

### Regression tests

```java
// The valid authenticated request passes CSRF and reaches the controller.
```

## TEST-E-014: wrong test configuration

- Difficulty: Easy
- Framework: Spring Testing Slices
- Language: Java
- Perspective: Context bootstrap
- Concept: wrong test configuration
- Symptom: The test starts the wrong application context.
- Diagnostic goal: Load the test configuration that supplies its collaborators.

### Buggy code

```java
@ContextConfiguration(classes = ProductionConfig.class)
class Test {}
```

### Expected diagnosis

A focused test should load the test configuration that supplies its collaborators.

### Corrected code

```java
@ContextConfiguration(classes = TestConfig.class)
class Test {}
```

### Regression tests

```java
// The context contains test doubles and no production connections.
```

## TEST-E-015: mock returns null default

- Difficulty: Easy
- Framework: Spring Testing Slices
- Language: Java
- Perspective: Mocking
- Concept: mock returns null default
- Symptom: The controller throws while the test expects a response.
- Diagnostic goal: Stub the collaborator path that the handler actually uses.

### Buggy code

```java
when(service.find(1L)).thenReturn(null);
```

### Expected diagnosis

Mockito returns null unless the test configures the expected value, so DTO mapping fails.

### Corrected code

```java
when(service.find(1L)).thenReturn(Optional.of(item));
```

### Regression tests

```java
// The success path receives the expected domain object.
```

## TEST-E-016: test rollback assumption

- Difficulty: Easy
- Framework: Spring Testing Slices
- Language: Java
- Perspective: Transactions
- Concept: test rollback assumption
- Symptom: Data leaks between tests.
- Diagnostic goal: Use transactional rollback or clean the database explicitly.

### Buggy code

```java
@SpringBootTest
class ItemTest { @Test void creates() { repository.save(item); } }
```

### Expected diagnosis

A full integration test does not automatically roll back unless a transaction is active for the test.

### Corrected code

```java
@SpringBootTest
@Transactional
class ItemTest { ... }
```

### Regression tests

```java
// Each test starts with a clean database state.
```

## TEST-E-017: container not ready

- Difficulty: Easy
- Framework: Spring Testing Slices
- Language: Java
- Perspective: Test containers
- Concept: container not ready
- Symptom: Integration tests race database startup.
- Diagnostic goal: Use the container lifecycle and dynamic property registration.

### Buggy code

```java
static PostgreSQLContainer<?> db = new PostgreSQLContainer<>("postgres:16");
```

### Expected diagnosis

Creating a container is insufficient if it is not started and its properties are not bound.

### Corrected code

```java
@Container static PostgreSQLContainer<?> db = new PostgreSQLContainer<>("postgres:16");
@DynamicPropertySource static void props(DynamicPropertyRegistry r) { r.add("spring.datasource.url", db::getJdbcUrl); }
```

### Regression tests

```java
// The application datasource points at the running container.
```

## TEST-E-018: only status asserted

- Difficulty: Easy
- Framework: Spring Testing Slices
- Language: Java
- Perspective: Assertions
- Concept: only status asserted
- Symptom: A regression changes the response body unnoticed.
- Diagnostic goal: Assert status, headers, and meaningful payload fields.

### Buggy code

```java
mockMvc.perform(get("/items/1")).andExpect(status().isOk());
```

### Expected diagnosis

A 200 response can still contain the wrong representation.

### Corrected code

```java
mockMvc.perform(get("/items/1")).andExpect(status().isOk()).andExpect(jsonPath("$.id").value(1));
```

### Regression tests

```java
// The contract test fails when the id or JSON shape changes.
```

## TEST-E-019: async result asserted too early

- Difficulty: Easy
- Framework: Spring Testing Slices
- Language: Java
- Perspective: Async tests
- Concept: async result asserted too early
- Symptom: The test is flaky or sees an empty response.
- Diagnostic goal: Wait for the async dispatch before asserting the final result.

### Buggy code

```java
mockMvc.perform(get("/report")).andExpect(status().isOk());
```

### Expected diagnosis

A controller returning a CompletableFuture requires async dispatch handling.

### Corrected code

```java
MvcResult result = mockMvc.perform(get("/report")).andReturn();
mockMvc.perform(asyncDispatch(result)).andExpect(status().isOk());
```

### Regression tests

```java
// The test waits for completion deterministically.
```

## TEST-E-020: test bean overridden by production bean

- Difficulty: Easy
- Framework: Spring Testing Slices
- Language: Java
- Perspective: Profiles
- Concept: test bean overridden by production bean
- Symptom: A test double is ignored.
- Diagnostic goal: Use profile or primary/qualifier rules deliberately.

### Buggy code

```java
@ActiveProfiles("test")
class ServiceTest {}
```

### Expected diagnosis

The test profile alone does not replace a production bean with the same role.

### Corrected code

```java
@TestConfiguration
static class Doubles { @Bean @Primary PaymentGateway gateway() { return new FakeGateway(); } }
```

### Regression tests

```java
// The test resolves the fake gateway and production behavior is isolated.
```

## TEST-E-021: repository missing in @WebMvcTest

- Difficulty: Easy
- Framework: Spring Testing Slices
- Language: Java
- Perspective: Web slice
- Concept: repository missing in @WebMvcTest
- Symptom: The controller test context cannot start.
- Diagnostic goal: Mock only collaborators outside the selected slice.

### Buggy code

```java
@WebMvcTest(ItemController.class)
class ItemTest { @Autowired ItemRepository repository; }
```

### Expected diagnosis

@WebMvcTest excludes repositories and services by design.

### Corrected code

```java
@WebMvcTest(ItemController.class)
class ItemTest { @MockBean ItemService service; }
```

### Regression tests

```java
// The MVC slice starts and the controller uses the mocked service.
```

## TEST-E-022: security filter breaks repository test

- Difficulty: Easy
- Framework: Spring Testing Slices
- Language: Java
- Perspective: Data slice
- Concept: security filter breaks repository test
- Symptom: A @DataJpaTest request unexpectedly requires authentication.
- Diagnostic goal: Keep slice scope clear and import only needed configuration.

### Buggy code

```java
@DataJpaTest
class ItemRepositoryTest {}
```

### Expected diagnosis

Importing the full application security configuration changes a focused persistence test.

### Corrected code

```java
@DataJpaTest
@Import(TestDatabaseConfig.class)
class ItemRepositoryTest {}
```

### Regression tests

```java
// The test uses the slice database without loading web security.
```

## TEST-E-023: missing csrf token

- Difficulty: Easy
- Framework: Spring Testing Slices
- Language: Java
- Perspective: MockMvc
- Concept: missing csrf token
- Symptom: A POST test receives 403 unexpectedly.
- Diagnostic goal: Include the security test request post processor.

### Buggy code

```java
mockMvc.perform(post("/items").content(json));
```

### Expected diagnosis

CSRF protection correctly rejects a state-changing request without a token.

### Corrected code

```java
mockMvc.perform(post("/items").with(csrf()).contentType(APPLICATION_JSON).content(json));
```

### Regression tests

```java
// The valid authenticated request passes CSRF and reaches the controller.
```

## TEST-E-024: wrong test configuration

- Difficulty: Easy
- Framework: Spring Testing Slices
- Language: Java
- Perspective: Context bootstrap
- Concept: wrong test configuration
- Symptom: The test starts the wrong application context.
- Diagnostic goal: Load the test configuration that supplies its collaborators.

### Buggy code

```java
@ContextConfiguration(classes = ProductionConfig.class)
class Test {}
```

### Expected diagnosis

A focused test should load the test configuration that supplies its collaborators.

### Corrected code

```java
@ContextConfiguration(classes = TestConfig.class)
class Test {}
```

### Regression tests

```java
// The context contains test doubles and no production connections.
```

## TEST-E-025: mock returns null default

- Difficulty: Easy
- Framework: Spring Testing Slices
- Language: Java
- Perspective: Mocking
- Concept: mock returns null default
- Symptom: The controller throws while the test expects a response.
- Diagnostic goal: Stub the collaborator path that the handler actually uses.

### Buggy code

```java
when(service.find(1L)).thenReturn(null);
```

### Expected diagnosis

Mockito returns null unless the test configures the expected value, so DTO mapping fails.

### Corrected code

```java
when(service.find(1L)).thenReturn(Optional.of(item));
```

### Regression tests

```java
// The success path receives the expected domain object.
```

## TEST-E-026: test rollback assumption

- Difficulty: Easy
- Framework: Spring Testing Slices
- Language: Java
- Perspective: Transactions
- Concept: test rollback assumption
- Symptom: Data leaks between tests.
- Diagnostic goal: Use transactional rollback or clean the database explicitly.

### Buggy code

```java
@SpringBootTest
class ItemTest { @Test void creates() { repository.save(item); } }
```

### Expected diagnosis

A full integration test does not automatically roll back unless a transaction is active for the test.

### Corrected code

```java
@SpringBootTest
@Transactional
class ItemTest { ... }
```

### Regression tests

```java
// Each test starts with a clean database state.
```

## TEST-E-027: container not ready

- Difficulty: Easy
- Framework: Spring Testing Slices
- Language: Java
- Perspective: Test containers
- Concept: container not ready
- Symptom: Integration tests race database startup.
- Diagnostic goal: Use the container lifecycle and dynamic property registration.

### Buggy code

```java
static PostgreSQLContainer<?> db = new PostgreSQLContainer<>("postgres:16");
```

### Expected diagnosis

Creating a container is insufficient if it is not started and its properties are not bound.

### Corrected code

```java
@Container static PostgreSQLContainer<?> db = new PostgreSQLContainer<>("postgres:16");
@DynamicPropertySource static void props(DynamicPropertyRegistry r) { r.add("spring.datasource.url", db::getJdbcUrl); }
```

### Regression tests

```java
// The application datasource points at the running container.
```

## TEST-E-028: only status asserted

- Difficulty: Easy
- Framework: Spring Testing Slices
- Language: Java
- Perspective: Assertions
- Concept: only status asserted
- Symptom: A regression changes the response body unnoticed.
- Diagnostic goal: Assert status, headers, and meaningful payload fields.

### Buggy code

```java
mockMvc.perform(get("/items/1")).andExpect(status().isOk());
```

### Expected diagnosis

A 200 response can still contain the wrong representation.

### Corrected code

```java
mockMvc.perform(get("/items/1")).andExpect(status().isOk()).andExpect(jsonPath("$.id").value(1));
```

### Regression tests

```java
// The contract test fails when the id or JSON shape changes.
```

## TEST-E-029: async result asserted too early

- Difficulty: Easy
- Framework: Spring Testing Slices
- Language: Java
- Perspective: Async tests
- Concept: async result asserted too early
- Symptom: The test is flaky or sees an empty response.
- Diagnostic goal: Wait for the async dispatch before asserting the final result.

### Buggy code

```java
mockMvc.perform(get("/report")).andExpect(status().isOk());
```

### Expected diagnosis

A controller returning a CompletableFuture requires async dispatch handling.

### Corrected code

```java
MvcResult result = mockMvc.perform(get("/report")).andReturn();
mockMvc.perform(asyncDispatch(result)).andExpect(status().isOk());
```

### Regression tests

```java
// The test waits for completion deterministically.
```

## TEST-E-030: test bean overridden by production bean

- Difficulty: Easy
- Framework: Spring Testing Slices
- Language: Java
- Perspective: Profiles
- Concept: test bean overridden by production bean
- Symptom: A test double is ignored.
- Diagnostic goal: Use profile or primary/qualifier rules deliberately.

### Buggy code

```java
@ActiveProfiles("test")
class ServiceTest {}
```

### Expected diagnosis

The test profile alone does not replace a production bean with the same role.

### Corrected code

```java
@TestConfiguration
static class Doubles { @Bean @Primary PaymentGateway gateway() { return new FakeGateway(); } }
```

### Regression tests

```java
// The test resolves the fake gateway and production behavior is isolated.
```

## TEST-E-031: repository missing in @WebMvcTest

- Difficulty: Easy
- Framework: Spring Testing Slices
- Language: Java
- Perspective: Web slice
- Concept: repository missing in @WebMvcTest
- Symptom: The controller test context cannot start.
- Diagnostic goal: Mock only collaborators outside the selected slice.

### Buggy code

```java
@WebMvcTest(ItemController.class)
class ItemTest { @Autowired ItemRepository repository; }
```

### Expected diagnosis

@WebMvcTest excludes repositories and services by design.

### Corrected code

```java
@WebMvcTest(ItemController.class)
class ItemTest { @MockBean ItemService service; }
```

### Regression tests

```java
// The MVC slice starts and the controller uses the mocked service.
```

## TEST-E-032: security filter breaks repository test

- Difficulty: Easy
- Framework: Spring Testing Slices
- Language: Java
- Perspective: Data slice
- Concept: security filter breaks repository test
- Symptom: A @DataJpaTest request unexpectedly requires authentication.
- Diagnostic goal: Keep slice scope clear and import only needed configuration.

### Buggy code

```java
@DataJpaTest
class ItemRepositoryTest {}
```

### Expected diagnosis

Importing the full application security configuration changes a focused persistence test.

### Corrected code

```java
@DataJpaTest
@Import(TestDatabaseConfig.class)
class ItemRepositoryTest {}
```

### Regression tests

```java
// The test uses the slice database without loading web security.
```

## TEST-E-033: missing csrf token

- Difficulty: Easy
- Framework: Spring Testing Slices
- Language: Java
- Perspective: MockMvc
- Concept: missing csrf token
- Symptom: A POST test receives 403 unexpectedly.
- Diagnostic goal: Include the security test request post processor.

### Buggy code

```java
mockMvc.perform(post("/items").content(json));
```

### Expected diagnosis

CSRF protection correctly rejects a state-changing request without a token.

### Corrected code

```java
mockMvc.perform(post("/items").with(csrf()).contentType(APPLICATION_JSON).content(json));
```

### Regression tests

```java
// The valid authenticated request passes CSRF and reaches the controller.
```

## TEST-E-034: wrong test configuration

- Difficulty: Easy
- Framework: Spring Testing Slices
- Language: Java
- Perspective: Context bootstrap
- Concept: wrong test configuration
- Symptom: The test starts the wrong application context.
- Diagnostic goal: Load the test configuration that supplies its collaborators.

### Buggy code

```java
@ContextConfiguration(classes = ProductionConfig.class)
class Test {}
```

### Expected diagnosis

A focused test should load the test configuration that supplies its collaborators.

### Corrected code

```java
@ContextConfiguration(classes = TestConfig.class)
class Test {}
```

### Regression tests

```java
// The context contains test doubles and no production connections.
```

## TEST-E-035: mock returns null default

- Difficulty: Easy
- Framework: Spring Testing Slices
- Language: Java
- Perspective: Mocking
- Concept: mock returns null default
- Symptom: The controller throws while the test expects a response.
- Diagnostic goal: Stub the collaborator path that the handler actually uses.

### Buggy code

```java
when(service.find(1L)).thenReturn(null);
```

### Expected diagnosis

Mockito returns null unless the test configures the expected value, so DTO mapping fails.

### Corrected code

```java
when(service.find(1L)).thenReturn(Optional.of(item));
```

### Regression tests

```java
// The success path receives the expected domain object.
```

## TEST-E-036: test rollback assumption

- Difficulty: Easy
- Framework: Spring Testing Slices
- Language: Java
- Perspective: Transactions
- Concept: test rollback assumption
- Symptom: Data leaks between tests.
- Diagnostic goal: Use transactional rollback or clean the database explicitly.

### Buggy code

```java
@SpringBootTest
class ItemTest { @Test void creates() { repository.save(item); } }
```

### Expected diagnosis

A full integration test does not automatically roll back unless a transaction is active for the test.

### Corrected code

```java
@SpringBootTest
@Transactional
class ItemTest { ... }
```

### Regression tests

```java
// Each test starts with a clean database state.
```

## TEST-E-037: container not ready

- Difficulty: Easy
- Framework: Spring Testing Slices
- Language: Java
- Perspective: Test containers
- Concept: container not ready
- Symptom: Integration tests race database startup.
- Diagnostic goal: Use the container lifecycle and dynamic property registration.

### Buggy code

```java
static PostgreSQLContainer<?> db = new PostgreSQLContainer<>("postgres:16");
```

### Expected diagnosis

Creating a container is insufficient if it is not started and its properties are not bound.

### Corrected code

```java
@Container static PostgreSQLContainer<?> db = new PostgreSQLContainer<>("postgres:16");
@DynamicPropertySource static void props(DynamicPropertyRegistry r) { r.add("spring.datasource.url", db::getJdbcUrl); }
```

### Regression tests

```java
// The application datasource points at the running container.
```

## TEST-E-038: only status asserted

- Difficulty: Easy
- Framework: Spring Testing Slices
- Language: Java
- Perspective: Assertions
- Concept: only status asserted
- Symptom: A regression changes the response body unnoticed.
- Diagnostic goal: Assert status, headers, and meaningful payload fields.

### Buggy code

```java
mockMvc.perform(get("/items/1")).andExpect(status().isOk());
```

### Expected diagnosis

A 200 response can still contain the wrong representation.

### Corrected code

```java
mockMvc.perform(get("/items/1")).andExpect(status().isOk()).andExpect(jsonPath("$.id").value(1));
```

### Regression tests

```java
// The contract test fails when the id or JSON shape changes.
```

## TEST-E-039: async result asserted too early

- Difficulty: Easy
- Framework: Spring Testing Slices
- Language: Java
- Perspective: Async tests
- Concept: async result asserted too early
- Symptom: The test is flaky or sees an empty response.
- Diagnostic goal: Wait for the async dispatch before asserting the final result.

### Buggy code

```java
mockMvc.perform(get("/report")).andExpect(status().isOk());
```

### Expected diagnosis

A controller returning a CompletableFuture requires async dispatch handling.

### Corrected code

```java
MvcResult result = mockMvc.perform(get("/report")).andReturn();
mockMvc.perform(asyncDispatch(result)).andExpect(status().isOk());
```

### Regression tests

```java
// The test waits for completion deterministically.
```

## TEST-E-040: test bean overridden by production bean

- Difficulty: Easy
- Framework: Spring Testing Slices
- Language: Java
- Perspective: Profiles
- Concept: test bean overridden by production bean
- Symptom: A test double is ignored.
- Diagnostic goal: Use profile or primary/qualifier rules deliberately.

### Buggy code

```java
@ActiveProfiles("test")
class ServiceTest {}
```

### Expected diagnosis

The test profile alone does not replace a production bean with the same role.

### Corrected code

```java
@TestConfiguration
static class Doubles { @Bean @Primary PaymentGateway gateway() { return new FakeGateway(); } }
```

### Regression tests

```java
// The test resolves the fake gateway and production behavior is isolated.
```

## TEST-E-041: repository missing in @WebMvcTest

- Difficulty: Easy
- Framework: Spring Testing Slices
- Language: Java
- Perspective: Web slice
- Concept: repository missing in @WebMvcTest
- Symptom: The controller test context cannot start.
- Diagnostic goal: Mock only collaborators outside the selected slice.

### Buggy code

```java
@WebMvcTest(ItemController.class)
class ItemTest { @Autowired ItemRepository repository; }
```

### Expected diagnosis

@WebMvcTest excludes repositories and services by design.

### Corrected code

```java
@WebMvcTest(ItemController.class)
class ItemTest { @MockBean ItemService service; }
```

### Regression tests

```java
// The MVC slice starts and the controller uses the mocked service.
```

## TEST-E-042: security filter breaks repository test

- Difficulty: Easy
- Framework: Spring Testing Slices
- Language: Java
- Perspective: Data slice
- Concept: security filter breaks repository test
- Symptom: A @DataJpaTest request unexpectedly requires authentication.
- Diagnostic goal: Keep slice scope clear and import only needed configuration.

### Buggy code

```java
@DataJpaTest
class ItemRepositoryTest {}
```

### Expected diagnosis

Importing the full application security configuration changes a focused persistence test.

### Corrected code

```java
@DataJpaTest
@Import(TestDatabaseConfig.class)
class ItemRepositoryTest {}
```

### Regression tests

```java
// The test uses the slice database without loading web security.
```

## TEST-E-043: missing csrf token

- Difficulty: Easy
- Framework: Spring Testing Slices
- Language: Java
- Perspective: MockMvc
- Concept: missing csrf token
- Symptom: A POST test receives 403 unexpectedly.
- Diagnostic goal: Include the security test request post processor.

### Buggy code

```java
mockMvc.perform(post("/items").content(json));
```

### Expected diagnosis

CSRF protection correctly rejects a state-changing request without a token.

### Corrected code

```java
mockMvc.perform(post("/items").with(csrf()).contentType(APPLICATION_JSON).content(json));
```

### Regression tests

```java
// The valid authenticated request passes CSRF and reaches the controller.
```

## TEST-E-044: wrong test configuration

- Difficulty: Easy
- Framework: Spring Testing Slices
- Language: Java
- Perspective: Context bootstrap
- Concept: wrong test configuration
- Symptom: The test starts the wrong application context.
- Diagnostic goal: Load the test configuration that supplies its collaborators.

### Buggy code

```java
@ContextConfiguration(classes = ProductionConfig.class)
class Test {}
```

### Expected diagnosis

A focused test should load the test configuration that supplies its collaborators.

### Corrected code

```java
@ContextConfiguration(classes = TestConfig.class)
class Test {}
```

### Regression tests

```java
// The context contains test doubles and no production connections.
```

## TEST-E-045: mock returns null default

- Difficulty: Easy
- Framework: Spring Testing Slices
- Language: Java
- Perspective: Mocking
- Concept: mock returns null default
- Symptom: The controller throws while the test expects a response.
- Diagnostic goal: Stub the collaborator path that the handler actually uses.

### Buggy code

```java
when(service.find(1L)).thenReturn(null);
```

### Expected diagnosis

Mockito returns null unless the test configures the expected value, so DTO mapping fails.

### Corrected code

```java
when(service.find(1L)).thenReturn(Optional.of(item));
```

### Regression tests

```java
// The success path receives the expected domain object.
```

## TEST-E-046: test rollback assumption

- Difficulty: Easy
- Framework: Spring Testing Slices
- Language: Java
- Perspective: Transactions
- Concept: test rollback assumption
- Symptom: Data leaks between tests.
- Diagnostic goal: Use transactional rollback or clean the database explicitly.

### Buggy code

```java
@SpringBootTest
class ItemTest { @Test void creates() { repository.save(item); } }
```

### Expected diagnosis

A full integration test does not automatically roll back unless a transaction is active for the test.

### Corrected code

```java
@SpringBootTest
@Transactional
class ItemTest { ... }
```

### Regression tests

```java
// Each test starts with a clean database state.
```

## TEST-E-047: container not ready

- Difficulty: Easy
- Framework: Spring Testing Slices
- Language: Java
- Perspective: Test containers
- Concept: container not ready
- Symptom: Integration tests race database startup.
- Diagnostic goal: Use the container lifecycle and dynamic property registration.

### Buggy code

```java
static PostgreSQLContainer<?> db = new PostgreSQLContainer<>("postgres:16");
```

### Expected diagnosis

Creating a container is insufficient if it is not started and its properties are not bound.

### Corrected code

```java
@Container static PostgreSQLContainer<?> db = new PostgreSQLContainer<>("postgres:16");
@DynamicPropertySource static void props(DynamicPropertyRegistry r) { r.add("spring.datasource.url", db::getJdbcUrl); }
```

### Regression tests

```java
// The application datasource points at the running container.
```

## TEST-E-048: only status asserted

- Difficulty: Easy
- Framework: Spring Testing Slices
- Language: Java
- Perspective: Assertions
- Concept: only status asserted
- Symptom: A regression changes the response body unnoticed.
- Diagnostic goal: Assert status, headers, and meaningful payload fields.

### Buggy code

```java
mockMvc.perform(get("/items/1")).andExpect(status().isOk());
```

### Expected diagnosis

A 200 response can still contain the wrong representation.

### Corrected code

```java
mockMvc.perform(get("/items/1")).andExpect(status().isOk()).andExpect(jsonPath("$.id").value(1));
```

### Regression tests

```java
// The contract test fails when the id or JSON shape changes.
```

## TEST-E-049: async result asserted too early

- Difficulty: Easy
- Framework: Spring Testing Slices
- Language: Java
- Perspective: Async tests
- Concept: async result asserted too early
- Symptom: The test is flaky or sees an empty response.
- Diagnostic goal: Wait for the async dispatch before asserting the final result.

### Buggy code

```java
mockMvc.perform(get("/report")).andExpect(status().isOk());
```

### Expected diagnosis

A controller returning a CompletableFuture requires async dispatch handling.

### Corrected code

```java
MvcResult result = mockMvc.perform(get("/report")).andReturn();
mockMvc.perform(asyncDispatch(result)).andExpect(status().isOk());
```

### Regression tests

```java
// The test waits for completion deterministically.
```

## TEST-E-050: test bean overridden by production bean

- Difficulty: Easy
- Framework: Spring Testing Slices
- Language: Java
- Perspective: Profiles
- Concept: test bean overridden by production bean
- Symptom: A test double is ignored.
- Diagnostic goal: Use profile or primary/qualifier rules deliberately.

### Buggy code

```java
@ActiveProfiles("test")
class ServiceTest {}
```

### Expected diagnosis

The test profile alone does not replace a production bean with the same role.

### Corrected code

```java
@TestConfiguration
static class Doubles { @Bean @Primary PaymentGateway gateway() { return new FakeGateway(); } }
```

### Regression tests

```java
// The test resolves the fake gateway and production behavior is isolated.
```

## TEST-E-051: repository missing in @WebMvcTest

- Difficulty: Easy
- Framework: Spring Testing Slices
- Language: Java
- Perspective: Web slice
- Concept: repository missing in @WebMvcTest
- Symptom: The controller test context cannot start.
- Diagnostic goal: Mock only collaborators outside the selected slice.

### Buggy code

```java
@WebMvcTest(ItemController.class)
class ItemTest { @Autowired ItemRepository repository; }
```

### Expected diagnosis

@WebMvcTest excludes repositories and services by design.

### Corrected code

```java
@WebMvcTest(ItemController.class)
class ItemTest { @MockBean ItemService service; }
```

### Regression tests

```java
// The MVC slice starts and the controller uses the mocked service.
```

## TEST-E-052: security filter breaks repository test

- Difficulty: Easy
- Framework: Spring Testing Slices
- Language: Java
- Perspective: Data slice
- Concept: security filter breaks repository test
- Symptom: A @DataJpaTest request unexpectedly requires authentication.
- Diagnostic goal: Keep slice scope clear and import only needed configuration.

### Buggy code

```java
@DataJpaTest
class ItemRepositoryTest {}
```

### Expected diagnosis

Importing the full application security configuration changes a focused persistence test.

### Corrected code

```java
@DataJpaTest
@Import(TestDatabaseConfig.class)
class ItemRepositoryTest {}
```

### Regression tests

```java
// The test uses the slice database without loading web security.
```

## TEST-E-053: missing csrf token

- Difficulty: Easy
- Framework: Spring Testing Slices
- Language: Java
- Perspective: MockMvc
- Concept: missing csrf token
- Symptom: A POST test receives 403 unexpectedly.
- Diagnostic goal: Include the security test request post processor.

### Buggy code

```java
mockMvc.perform(post("/items").content(json));
```

### Expected diagnosis

CSRF protection correctly rejects a state-changing request without a token.

### Corrected code

```java
mockMvc.perform(post("/items").with(csrf()).contentType(APPLICATION_JSON).content(json));
```

### Regression tests

```java
// The valid authenticated request passes CSRF and reaches the controller.
```

## TEST-E-054: wrong test configuration

- Difficulty: Easy
- Framework: Spring Testing Slices
- Language: Java
- Perspective: Context bootstrap
- Concept: wrong test configuration
- Symptom: The test starts the wrong application context.
- Diagnostic goal: Load the test configuration that supplies its collaborators.

### Buggy code

```java
@ContextConfiguration(classes = ProductionConfig.class)
class Test {}
```

### Expected diagnosis

A focused test should load the test configuration that supplies its collaborators.

### Corrected code

```java
@ContextConfiguration(classes = TestConfig.class)
class Test {}
```

### Regression tests

```java
// The context contains test doubles and no production connections.
```

## TEST-E-055: mock returns null default

- Difficulty: Easy
- Framework: Spring Testing Slices
- Language: Java
- Perspective: Mocking
- Concept: mock returns null default
- Symptom: The controller throws while the test expects a response.
- Diagnostic goal: Stub the collaborator path that the handler actually uses.

### Buggy code

```java
when(service.find(1L)).thenReturn(null);
```

### Expected diagnosis

Mockito returns null unless the test configures the expected value, so DTO mapping fails.

### Corrected code

```java
when(service.find(1L)).thenReturn(Optional.of(item));
```

### Regression tests

```java
// The success path receives the expected domain object.
```

## TEST-E-056: test rollback assumption

- Difficulty: Easy
- Framework: Spring Testing Slices
- Language: Java
- Perspective: Transactions
- Concept: test rollback assumption
- Symptom: Data leaks between tests.
- Diagnostic goal: Use transactional rollback or clean the database explicitly.

### Buggy code

```java
@SpringBootTest
class ItemTest { @Test void creates() { repository.save(item); } }
```

### Expected diagnosis

A full integration test does not automatically roll back unless a transaction is active for the test.

### Corrected code

```java
@SpringBootTest
@Transactional
class ItemTest { ... }
```

### Regression tests

```java
// Each test starts with a clean database state.
```

## TEST-E-057: container not ready

- Difficulty: Easy
- Framework: Spring Testing Slices
- Language: Java
- Perspective: Test containers
- Concept: container not ready
- Symptom: Integration tests race database startup.
- Diagnostic goal: Use the container lifecycle and dynamic property registration.

### Buggy code

```java
static PostgreSQLContainer<?> db = new PostgreSQLContainer<>("postgres:16");
```

### Expected diagnosis

Creating a container is insufficient if it is not started and its properties are not bound.

### Corrected code

```java
@Container static PostgreSQLContainer<?> db = new PostgreSQLContainer<>("postgres:16");
@DynamicPropertySource static void props(DynamicPropertyRegistry r) { r.add("spring.datasource.url", db::getJdbcUrl); }
```

### Regression tests

```java
// The application datasource points at the running container.
```

## TEST-E-058: only status asserted

- Difficulty: Easy
- Framework: Spring Testing Slices
- Language: Java
- Perspective: Assertions
- Concept: only status asserted
- Symptom: A regression changes the response body unnoticed.
- Diagnostic goal: Assert status, headers, and meaningful payload fields.

### Buggy code

```java
mockMvc.perform(get("/items/1")).andExpect(status().isOk());
```

### Expected diagnosis

A 200 response can still contain the wrong representation.

### Corrected code

```java
mockMvc.perform(get("/items/1")).andExpect(status().isOk()).andExpect(jsonPath("$.id").value(1));
```

### Regression tests

```java
// The contract test fails when the id or JSON shape changes.
```

## TEST-E-059: async result asserted too early

- Difficulty: Easy
- Framework: Spring Testing Slices
- Language: Java
- Perspective: Async tests
- Concept: async result asserted too early
- Symptom: The test is flaky or sees an empty response.
- Diagnostic goal: Wait for the async dispatch before asserting the final result.

### Buggy code

```java
mockMvc.perform(get("/report")).andExpect(status().isOk());
```

### Expected diagnosis

A controller returning a CompletableFuture requires async dispatch handling.

### Corrected code

```java
MvcResult result = mockMvc.perform(get("/report")).andReturn();
mockMvc.perform(asyncDispatch(result)).andExpect(status().isOk());
```

### Regression tests

```java
// The test waits for completion deterministically.
```

## TEST-E-060: test bean overridden by production bean

- Difficulty: Easy
- Framework: Spring Testing Slices
- Language: Java
- Perspective: Profiles
- Concept: test bean overridden by production bean
- Symptom: A test double is ignored.
- Diagnostic goal: Use profile or primary/qualifier rules deliberately.

### Buggy code

```java
@ActiveProfiles("test")
class ServiceTest {}
```

### Expected diagnosis

The test profile alone does not replace a production bean with the same role.

### Corrected code

```java
@TestConfiguration
static class Doubles { @Bean @Primary PaymentGateway gateway() { return new FakeGateway(); } }
```

### Regression tests

```java
// The test resolves the fake gateway and production behavior is isolated.
```

## TEST-E-061: repository missing in @WebMvcTest

- Difficulty: Easy
- Framework: Spring Testing Slices
- Language: Java
- Perspective: Web slice
- Concept: repository missing in @WebMvcTest
- Symptom: The controller test context cannot start.
- Diagnostic goal: Mock only collaborators outside the selected slice.

### Buggy code

```java
@WebMvcTest(ItemController.class)
class ItemTest { @Autowired ItemRepository repository; }
```

### Expected diagnosis

@WebMvcTest excludes repositories and services by design.

### Corrected code

```java
@WebMvcTest(ItemController.class)
class ItemTest { @MockBean ItemService service; }
```

### Regression tests

```java
// The MVC slice starts and the controller uses the mocked service.
```

## TEST-E-062: security filter breaks repository test

- Difficulty: Easy
- Framework: Spring Testing Slices
- Language: Java
- Perspective: Data slice
- Concept: security filter breaks repository test
- Symptom: A @DataJpaTest request unexpectedly requires authentication.
- Diagnostic goal: Keep slice scope clear and import only needed configuration.

### Buggy code

```java
@DataJpaTest
class ItemRepositoryTest {}
```

### Expected diagnosis

Importing the full application security configuration changes a focused persistence test.

### Corrected code

```java
@DataJpaTest
@Import(TestDatabaseConfig.class)
class ItemRepositoryTest {}
```

### Regression tests

```java
// The test uses the slice database without loading web security.
```

## TEST-E-063: missing csrf token

- Difficulty: Easy
- Framework: Spring Testing Slices
- Language: Java
- Perspective: MockMvc
- Concept: missing csrf token
- Symptom: A POST test receives 403 unexpectedly.
- Diagnostic goal: Include the security test request post processor.

### Buggy code

```java
mockMvc.perform(post("/items").content(json));
```

### Expected diagnosis

CSRF protection correctly rejects a state-changing request without a token.

### Corrected code

```java
mockMvc.perform(post("/items").with(csrf()).contentType(APPLICATION_JSON).content(json));
```

### Regression tests

```java
// The valid authenticated request passes CSRF and reaches the controller.
```

## TEST-E-064: wrong test configuration

- Difficulty: Easy
- Framework: Spring Testing Slices
- Language: Java
- Perspective: Context bootstrap
- Concept: wrong test configuration
- Symptom: The test starts the wrong application context.
- Diagnostic goal: Load the test configuration that supplies its collaborators.

### Buggy code

```java
@ContextConfiguration(classes = ProductionConfig.class)
class Test {}
```

### Expected diagnosis

A focused test should load the test configuration that supplies its collaborators.

### Corrected code

```java
@ContextConfiguration(classes = TestConfig.class)
class Test {}
```

### Regression tests

```java
// The context contains test doubles and no production connections.
```

## TEST-E-065: mock returns null default

- Difficulty: Easy
- Framework: Spring Testing Slices
- Language: Java
- Perspective: Mocking
- Concept: mock returns null default
- Symptom: The controller throws while the test expects a response.
- Diagnostic goal: Stub the collaborator path that the handler actually uses.

### Buggy code

```java
when(service.find(1L)).thenReturn(null);
```

### Expected diagnosis

Mockito returns null unless the test configures the expected value, so DTO mapping fails.

### Corrected code

```java
when(service.find(1L)).thenReturn(Optional.of(item));
```

### Regression tests

```java
// The success path receives the expected domain object.
```

## TEST-E-066: test rollback assumption

- Difficulty: Easy
- Framework: Spring Testing Slices
- Language: Java
- Perspective: Transactions
- Concept: test rollback assumption
- Symptom: Data leaks between tests.
- Diagnostic goal: Use transactional rollback or clean the database explicitly.

### Buggy code

```java
@SpringBootTest
class ItemTest { @Test void creates() { repository.save(item); } }
```

### Expected diagnosis

A full integration test does not automatically roll back unless a transaction is active for the test.

### Corrected code

```java
@SpringBootTest
@Transactional
class ItemTest { ... }
```

### Regression tests

```java
// Each test starts with a clean database state.
```

## TEST-E-067: container not ready

- Difficulty: Easy
- Framework: Spring Testing Slices
- Language: Java
- Perspective: Test containers
- Concept: container not ready
- Symptom: Integration tests race database startup.
- Diagnostic goal: Use the container lifecycle and dynamic property registration.

### Buggy code

```java
static PostgreSQLContainer<?> db = new PostgreSQLContainer<>("postgres:16");
```

### Expected diagnosis

Creating a container is insufficient if it is not started and its properties are not bound.

### Corrected code

```java
@Container static PostgreSQLContainer<?> db = new PostgreSQLContainer<>("postgres:16");
@DynamicPropertySource static void props(DynamicPropertyRegistry r) { r.add("spring.datasource.url", db::getJdbcUrl); }
```

### Regression tests

```java
// The application datasource points at the running container.
```

## TEST-E-068: only status asserted

- Difficulty: Easy
- Framework: Spring Testing Slices
- Language: Java
- Perspective: Assertions
- Concept: only status asserted
- Symptom: A regression changes the response body unnoticed.
- Diagnostic goal: Assert status, headers, and meaningful payload fields.

### Buggy code

```java
mockMvc.perform(get("/items/1")).andExpect(status().isOk());
```

### Expected diagnosis

A 200 response can still contain the wrong representation.

### Corrected code

```java
mockMvc.perform(get("/items/1")).andExpect(status().isOk()).andExpect(jsonPath("$.id").value(1));
```

### Regression tests

```java
// The contract test fails when the id or JSON shape changes.
```

## TEST-E-069: async result asserted too early

- Difficulty: Easy
- Framework: Spring Testing Slices
- Language: Java
- Perspective: Async tests
- Concept: async result asserted too early
- Symptom: The test is flaky or sees an empty response.
- Diagnostic goal: Wait for the async dispatch before asserting the final result.

### Buggy code

```java
mockMvc.perform(get("/report")).andExpect(status().isOk());
```

### Expected diagnosis

A controller returning a CompletableFuture requires async dispatch handling.

### Corrected code

```java
MvcResult result = mockMvc.perform(get("/report")).andReturn();
mockMvc.perform(asyncDispatch(result)).andExpect(status().isOk());
```

### Regression tests

```java
// The test waits for completion deterministically.
```

## TEST-E-070: test bean overridden by production bean

- Difficulty: Easy
- Framework: Spring Testing Slices
- Language: Java
- Perspective: Profiles
- Concept: test bean overridden by production bean
- Symptom: A test double is ignored.
- Diagnostic goal: Use profile or primary/qualifier rules deliberately.

### Buggy code

```java
@ActiveProfiles("test")
class ServiceTest {}
```

### Expected diagnosis

The test profile alone does not replace a production bean with the same role.

### Corrected code

```java
@TestConfiguration
static class Doubles { @Bean @Primary PaymentGateway gateway() { return new FakeGateway(); } }
```

### Regression tests

```java
// The test resolves the fake gateway and production behavior is isolated.
```

## TEST-E-071: repository missing in @WebMvcTest

- Difficulty: Easy
- Framework: Spring Testing Slices
- Language: Java
- Perspective: Web slice
- Concept: repository missing in @WebMvcTest
- Symptom: The controller test context cannot start.
- Diagnostic goal: Mock only collaborators outside the selected slice.

### Buggy code

```java
@WebMvcTest(ItemController.class)
class ItemTest { @Autowired ItemRepository repository; }
```

### Expected diagnosis

@WebMvcTest excludes repositories and services by design.

### Corrected code

```java
@WebMvcTest(ItemController.class)
class ItemTest { @MockBean ItemService service; }
```

### Regression tests

```java
// The MVC slice starts and the controller uses the mocked service.
```

## TEST-E-072: security filter breaks repository test

- Difficulty: Easy
- Framework: Spring Testing Slices
- Language: Java
- Perspective: Data slice
- Concept: security filter breaks repository test
- Symptom: A @DataJpaTest request unexpectedly requires authentication.
- Diagnostic goal: Keep slice scope clear and import only needed configuration.

### Buggy code

```java
@DataJpaTest
class ItemRepositoryTest {}
```

### Expected diagnosis

Importing the full application security configuration changes a focused persistence test.

### Corrected code

```java
@DataJpaTest
@Import(TestDatabaseConfig.class)
class ItemRepositoryTest {}
```

### Regression tests

```java
// The test uses the slice database without loading web security.
```

## TEST-E-073: missing csrf token

- Difficulty: Easy
- Framework: Spring Testing Slices
- Language: Java
- Perspective: MockMvc
- Concept: missing csrf token
- Symptom: A POST test receives 403 unexpectedly.
- Diagnostic goal: Include the security test request post processor.

### Buggy code

```java
mockMvc.perform(post("/items").content(json));
```

### Expected diagnosis

CSRF protection correctly rejects a state-changing request without a token.

### Corrected code

```java
mockMvc.perform(post("/items").with(csrf()).contentType(APPLICATION_JSON).content(json));
```

### Regression tests

```java
// The valid authenticated request passes CSRF and reaches the controller.
```

## TEST-E-074: wrong test configuration

- Difficulty: Easy
- Framework: Spring Testing Slices
- Language: Java
- Perspective: Context bootstrap
- Concept: wrong test configuration
- Symptom: The test starts the wrong application context.
- Diagnostic goal: Load the test configuration that supplies its collaborators.

### Buggy code

```java
@ContextConfiguration(classes = ProductionConfig.class)
class Test {}
```

### Expected diagnosis

A focused test should load the test configuration that supplies its collaborators.

### Corrected code

```java
@ContextConfiguration(classes = TestConfig.class)
class Test {}
```

### Regression tests

```java
// The context contains test doubles and no production connections.
```

## TEST-E-075: mock returns null default

- Difficulty: Easy
- Framework: Spring Testing Slices
- Language: Java
- Perspective: Mocking
- Concept: mock returns null default
- Symptom: The controller throws while the test expects a response.
- Diagnostic goal: Stub the collaborator path that the handler actually uses.

### Buggy code

```java
when(service.find(1L)).thenReturn(null);
```

### Expected diagnosis

Mockito returns null unless the test configures the expected value, so DTO mapping fails.

### Corrected code

```java
when(service.find(1L)).thenReturn(Optional.of(item));
```

### Regression tests

```java
// The success path receives the expected domain object.
```

## TEST-E-076: test rollback assumption

- Difficulty: Easy
- Framework: Spring Testing Slices
- Language: Java
- Perspective: Transactions
- Concept: test rollback assumption
- Symptom: Data leaks between tests.
- Diagnostic goal: Use transactional rollback or clean the database explicitly.

### Buggy code

```java
@SpringBootTest
class ItemTest { @Test void creates() { repository.save(item); } }
```

### Expected diagnosis

A full integration test does not automatically roll back unless a transaction is active for the test.

### Corrected code

```java
@SpringBootTest
@Transactional
class ItemTest { ... }
```

### Regression tests

```java
// Each test starts with a clean database state.
```

## TEST-E-077: container not ready

- Difficulty: Easy
- Framework: Spring Testing Slices
- Language: Java
- Perspective: Test containers
- Concept: container not ready
- Symptom: Integration tests race database startup.
- Diagnostic goal: Use the container lifecycle and dynamic property registration.

### Buggy code

```java
static PostgreSQLContainer<?> db = new PostgreSQLContainer<>("postgres:16");
```

### Expected diagnosis

Creating a container is insufficient if it is not started and its properties are not bound.

### Corrected code

```java
@Container static PostgreSQLContainer<?> db = new PostgreSQLContainer<>("postgres:16");
@DynamicPropertySource static void props(DynamicPropertyRegistry r) { r.add("spring.datasource.url", db::getJdbcUrl); }
```

### Regression tests

```java
// The application datasource points at the running container.
```

## TEST-E-078: only status asserted

- Difficulty: Easy
- Framework: Spring Testing Slices
- Language: Java
- Perspective: Assertions
- Concept: only status asserted
- Symptom: A regression changes the response body unnoticed.
- Diagnostic goal: Assert status, headers, and meaningful payload fields.

### Buggy code

```java
mockMvc.perform(get("/items/1")).andExpect(status().isOk());
```

### Expected diagnosis

A 200 response can still contain the wrong representation.

### Corrected code

```java
mockMvc.perform(get("/items/1")).andExpect(status().isOk()).andExpect(jsonPath("$.id").value(1));
```

### Regression tests

```java
// The contract test fails when the id or JSON shape changes.
```

## TEST-E-079: async result asserted too early

- Difficulty: Easy
- Framework: Spring Testing Slices
- Language: Java
- Perspective: Async tests
- Concept: async result asserted too early
- Symptom: The test is flaky or sees an empty response.
- Diagnostic goal: Wait for the async dispatch before asserting the final result.

### Buggy code

```java
mockMvc.perform(get("/report")).andExpect(status().isOk());
```

### Expected diagnosis

A controller returning a CompletableFuture requires async dispatch handling.

### Corrected code

```java
MvcResult result = mockMvc.perform(get("/report")).andReturn();
mockMvc.perform(asyncDispatch(result)).andExpect(status().isOk());
```

### Regression tests

```java
// The test waits for completion deterministically.
```

## TEST-E-080: test bean overridden by production bean

- Difficulty: Easy
- Framework: Spring Testing Slices
- Language: Java
- Perspective: Profiles
- Concept: test bean overridden by production bean
- Symptom: A test double is ignored.
- Diagnostic goal: Use profile or primary/qualifier rules deliberately.

### Buggy code

```java
@ActiveProfiles("test")
class ServiceTest {}
```

### Expected diagnosis

The test profile alone does not replace a production bean with the same role.

### Corrected code

```java
@TestConfiguration
static class Doubles { @Bean @Primary PaymentGateway gateway() { return new FakeGateway(); } }
```

### Regression tests

```java
// The test resolves the fake gateway and production behavior is isolated.
```

## TEST-E-081: repository missing in @WebMvcTest

- Difficulty: Easy
- Framework: Spring Testing Slices
- Language: Java
- Perspective: Web slice
- Concept: repository missing in @WebMvcTest
- Symptom: The controller test context cannot start.
- Diagnostic goal: Mock only collaborators outside the selected slice.

### Buggy code

```java
@WebMvcTest(ItemController.class)
class ItemTest { @Autowired ItemRepository repository; }
```

### Expected diagnosis

@WebMvcTest excludes repositories and services by design.

### Corrected code

```java
@WebMvcTest(ItemController.class)
class ItemTest { @MockBean ItemService service; }
```

### Regression tests

```java
// The MVC slice starts and the controller uses the mocked service.
```

## TEST-E-082: security filter breaks repository test

- Difficulty: Easy
- Framework: Spring Testing Slices
- Language: Java
- Perspective: Data slice
- Concept: security filter breaks repository test
- Symptom: A @DataJpaTest request unexpectedly requires authentication.
- Diagnostic goal: Keep slice scope clear and import only needed configuration.

### Buggy code

```java
@DataJpaTest
class ItemRepositoryTest {}
```

### Expected diagnosis

Importing the full application security configuration changes a focused persistence test.

### Corrected code

```java
@DataJpaTest
@Import(TestDatabaseConfig.class)
class ItemRepositoryTest {}
```

### Regression tests

```java
// The test uses the slice database without loading web security.
```

## TEST-E-083: missing csrf token

- Difficulty: Easy
- Framework: Spring Testing Slices
- Language: Java
- Perspective: MockMvc
- Concept: missing csrf token
- Symptom: A POST test receives 403 unexpectedly.
- Diagnostic goal: Include the security test request post processor.

### Buggy code

```java
mockMvc.perform(post("/items").content(json));
```

### Expected diagnosis

CSRF protection correctly rejects a state-changing request without a token.

### Corrected code

```java
mockMvc.perform(post("/items").with(csrf()).contentType(APPLICATION_JSON).content(json));
```

### Regression tests

```java
// The valid authenticated request passes CSRF and reaches the controller.
```

## TEST-E-084: wrong test configuration

- Difficulty: Easy
- Framework: Spring Testing Slices
- Language: Java
- Perspective: Context bootstrap
- Concept: wrong test configuration
- Symptom: The test starts the wrong application context.
- Diagnostic goal: Load the test configuration that supplies its collaborators.

### Buggy code

```java
@ContextConfiguration(classes = ProductionConfig.class)
class Test {}
```

### Expected diagnosis

A focused test should load the test configuration that supplies its collaborators.

### Corrected code

```java
@ContextConfiguration(classes = TestConfig.class)
class Test {}
```

### Regression tests

```java
// The context contains test doubles and no production connections.
```

## TEST-E-085: mock returns null default

- Difficulty: Easy
- Framework: Spring Testing Slices
- Language: Java
- Perspective: Mocking
- Concept: mock returns null default
- Symptom: The controller throws while the test expects a response.
- Diagnostic goal: Stub the collaborator path that the handler actually uses.

### Buggy code

```java
when(service.find(1L)).thenReturn(null);
```

### Expected diagnosis

Mockito returns null unless the test configures the expected value, so DTO mapping fails.

### Corrected code

```java
when(service.find(1L)).thenReturn(Optional.of(item));
```

### Regression tests

```java
// The success path receives the expected domain object.
```

## TEST-E-086: test rollback assumption

- Difficulty: Easy
- Framework: Spring Testing Slices
- Language: Java
- Perspective: Transactions
- Concept: test rollback assumption
- Symptom: Data leaks between tests.
- Diagnostic goal: Use transactional rollback or clean the database explicitly.

### Buggy code

```java
@SpringBootTest
class ItemTest { @Test void creates() { repository.save(item); } }
```

### Expected diagnosis

A full integration test does not automatically roll back unless a transaction is active for the test.

### Corrected code

```java
@SpringBootTest
@Transactional
class ItemTest { ... }
```

### Regression tests

```java
// Each test starts with a clean database state.
```

## TEST-E-087: container not ready

- Difficulty: Easy
- Framework: Spring Testing Slices
- Language: Java
- Perspective: Test containers
- Concept: container not ready
- Symptom: Integration tests race database startup.
- Diagnostic goal: Use the container lifecycle and dynamic property registration.

### Buggy code

```java
static PostgreSQLContainer<?> db = new PostgreSQLContainer<>("postgres:16");
```

### Expected diagnosis

Creating a container is insufficient if it is not started and its properties are not bound.

### Corrected code

```java
@Container static PostgreSQLContainer<?> db = new PostgreSQLContainer<>("postgres:16");
@DynamicPropertySource static void props(DynamicPropertyRegistry r) { r.add("spring.datasource.url", db::getJdbcUrl); }
```

### Regression tests

```java
// The application datasource points at the running container.
```

## TEST-E-088: only status asserted

- Difficulty: Easy
- Framework: Spring Testing Slices
- Language: Java
- Perspective: Assertions
- Concept: only status asserted
- Symptom: A regression changes the response body unnoticed.
- Diagnostic goal: Assert status, headers, and meaningful payload fields.

### Buggy code

```java
mockMvc.perform(get("/items/1")).andExpect(status().isOk());
```

### Expected diagnosis

A 200 response can still contain the wrong representation.

### Corrected code

```java
mockMvc.perform(get("/items/1")).andExpect(status().isOk()).andExpect(jsonPath("$.id").value(1));
```

### Regression tests

```java
// The contract test fails when the id or JSON shape changes.
```

## TEST-E-089: async result asserted too early

- Difficulty: Easy
- Framework: Spring Testing Slices
- Language: Java
- Perspective: Async tests
- Concept: async result asserted too early
- Symptom: The test is flaky or sees an empty response.
- Diagnostic goal: Wait for the async dispatch before asserting the final result.

### Buggy code

```java
mockMvc.perform(get("/report")).andExpect(status().isOk());
```

### Expected diagnosis

A controller returning a CompletableFuture requires async dispatch handling.

### Corrected code

```java
MvcResult result = mockMvc.perform(get("/report")).andReturn();
mockMvc.perform(asyncDispatch(result)).andExpect(status().isOk());
```

### Regression tests

```java
// The test waits for completion deterministically.
```

## TEST-E-090: test bean overridden by production bean

- Difficulty: Easy
- Framework: Spring Testing Slices
- Language: Java
- Perspective: Profiles
- Concept: test bean overridden by production bean
- Symptom: A test double is ignored.
- Diagnostic goal: Use profile or primary/qualifier rules deliberately.

### Buggy code

```java
@ActiveProfiles("test")
class ServiceTest {}
```

### Expected diagnosis

The test profile alone does not replace a production bean with the same role.

### Corrected code

```java
@TestConfiguration
static class Doubles { @Bean @Primary PaymentGateway gateway() { return new FakeGateway(); } }
```

### Regression tests

```java
// The test resolves the fake gateway and production behavior is isolated.
```

## TEST-E-091: repository missing in @WebMvcTest

- Difficulty: Easy
- Framework: Spring Testing Slices
- Language: Java
- Perspective: Web slice
- Concept: repository missing in @WebMvcTest
- Symptom: The controller test context cannot start.
- Diagnostic goal: Mock only collaborators outside the selected slice.

### Buggy code

```java
@WebMvcTest(ItemController.class)
class ItemTest { @Autowired ItemRepository repository; }
```

### Expected diagnosis

@WebMvcTest excludes repositories and services by design.

### Corrected code

```java
@WebMvcTest(ItemController.class)
class ItemTest { @MockBean ItemService service; }
```

### Regression tests

```java
// The MVC slice starts and the controller uses the mocked service.
```

## TEST-E-092: security filter breaks repository test

- Difficulty: Easy
- Framework: Spring Testing Slices
- Language: Java
- Perspective: Data slice
- Concept: security filter breaks repository test
- Symptom: A @DataJpaTest request unexpectedly requires authentication.
- Diagnostic goal: Keep slice scope clear and import only needed configuration.

### Buggy code

```java
@DataJpaTest
class ItemRepositoryTest {}
```

### Expected diagnosis

Importing the full application security configuration changes a focused persistence test.

### Corrected code

```java
@DataJpaTest
@Import(TestDatabaseConfig.class)
class ItemRepositoryTest {}
```

### Regression tests

```java
// The test uses the slice database without loading web security.
```

## TEST-E-093: missing csrf token

- Difficulty: Easy
- Framework: Spring Testing Slices
- Language: Java
- Perspective: MockMvc
- Concept: missing csrf token
- Symptom: A POST test receives 403 unexpectedly.
- Diagnostic goal: Include the security test request post processor.

### Buggy code

```java
mockMvc.perform(post("/items").content(json));
```

### Expected diagnosis

CSRF protection correctly rejects a state-changing request without a token.

### Corrected code

```java
mockMvc.perform(post("/items").with(csrf()).contentType(APPLICATION_JSON).content(json));
```

### Regression tests

```java
// The valid authenticated request passes CSRF and reaches the controller.
```

## TEST-E-094: wrong test configuration

- Difficulty: Easy
- Framework: Spring Testing Slices
- Language: Java
- Perspective: Context bootstrap
- Concept: wrong test configuration
- Symptom: The test starts the wrong application context.
- Diagnostic goal: Load the test configuration that supplies its collaborators.

### Buggy code

```java
@ContextConfiguration(classes = ProductionConfig.class)
class Test {}
```

### Expected diagnosis

A focused test should load the test configuration that supplies its collaborators.

### Corrected code

```java
@ContextConfiguration(classes = TestConfig.class)
class Test {}
```

### Regression tests

```java
// The context contains test doubles and no production connections.
```

## TEST-E-095: mock returns null default

- Difficulty: Easy
- Framework: Spring Testing Slices
- Language: Java
- Perspective: Mocking
- Concept: mock returns null default
- Symptom: The controller throws while the test expects a response.
- Diagnostic goal: Stub the collaborator path that the handler actually uses.

### Buggy code

```java
when(service.find(1L)).thenReturn(null);
```

### Expected diagnosis

Mockito returns null unless the test configures the expected value, so DTO mapping fails.

### Corrected code

```java
when(service.find(1L)).thenReturn(Optional.of(item));
```

### Regression tests

```java
// The success path receives the expected domain object.
```

## TEST-E-096: test rollback assumption

- Difficulty: Easy
- Framework: Spring Testing Slices
- Language: Java
- Perspective: Transactions
- Concept: test rollback assumption
- Symptom: Data leaks between tests.
- Diagnostic goal: Use transactional rollback or clean the database explicitly.

### Buggy code

```java
@SpringBootTest
class ItemTest { @Test void creates() { repository.save(item); } }
```

### Expected diagnosis

A full integration test does not automatically roll back unless a transaction is active for the test.

### Corrected code

```java
@SpringBootTest
@Transactional
class ItemTest { ... }
```

### Regression tests

```java
// Each test starts with a clean database state.
```

## TEST-E-097: container not ready

- Difficulty: Easy
- Framework: Spring Testing Slices
- Language: Java
- Perspective: Test containers
- Concept: container not ready
- Symptom: Integration tests race database startup.
- Diagnostic goal: Use the container lifecycle and dynamic property registration.

### Buggy code

```java
static PostgreSQLContainer<?> db = new PostgreSQLContainer<>("postgres:16");
```

### Expected diagnosis

Creating a container is insufficient if it is not started and its properties are not bound.

### Corrected code

```java
@Container static PostgreSQLContainer<?> db = new PostgreSQLContainer<>("postgres:16");
@DynamicPropertySource static void props(DynamicPropertyRegistry r) { r.add("spring.datasource.url", db::getJdbcUrl); }
```

### Regression tests

```java
// The application datasource points at the running container.
```

## TEST-E-098: only status asserted

- Difficulty: Easy
- Framework: Spring Testing Slices
- Language: Java
- Perspective: Assertions
- Concept: only status asserted
- Symptom: A regression changes the response body unnoticed.
- Diagnostic goal: Assert status, headers, and meaningful payload fields.

### Buggy code

```java
mockMvc.perform(get("/items/1")).andExpect(status().isOk());
```

### Expected diagnosis

A 200 response can still contain the wrong representation.

### Corrected code

```java
mockMvc.perform(get("/items/1")).andExpect(status().isOk()).andExpect(jsonPath("$.id").value(1));
```

### Regression tests

```java
// The contract test fails when the id or JSON shape changes.
```

## TEST-E-099: async result asserted too early

- Difficulty: Easy
- Framework: Spring Testing Slices
- Language: Java
- Perspective: Async tests
- Concept: async result asserted too early
- Symptom: The test is flaky or sees an empty response.
- Diagnostic goal: Wait for the async dispatch before asserting the final result.

### Buggy code

```java
mockMvc.perform(get("/report")).andExpect(status().isOk());
```

### Expected diagnosis

A controller returning a CompletableFuture requires async dispatch handling.

### Corrected code

```java
MvcResult result = mockMvc.perform(get("/report")).andReturn();
mockMvc.perform(asyncDispatch(result)).andExpect(status().isOk());
```

### Regression tests

```java
// The test waits for completion deterministically.
```

## TEST-E-100: test bean overridden by production bean

- Difficulty: Easy
- Framework: Spring Testing Slices
- Language: Java
- Perspective: Profiles
- Concept: test bean overridden by production bean
- Symptom: A test double is ignored.
- Diagnostic goal: Use profile or primary/qualifier rules deliberately.

### Buggy code

```java
@ActiveProfiles("test")
class ServiceTest {}
```

### Expected diagnosis

The test profile alone does not replace a production bean with the same role.

### Corrected code

```java
@TestConfiguration
static class Doubles { @Bean @Primary PaymentGateway gateway() { return new FakeGateway(); } }
```

### Regression tests

```java
// The test resolves the fake gateway and production behavior is isolated.
```

## TEST-M-001: repository missing in @WebMvcTest

- Difficulty: Medium
- Framework: Spring Testing Slices
- Language: Java
- Perspective: Web slice
- Concept: repository missing in @WebMvcTest
- Symptom: The controller test context cannot start.
- Diagnostic goal: Mock only collaborators outside the selected slice.

### Buggy code

```java
@WebMvcTest(ItemController.class)
class ItemTest { @Autowired ItemRepository repository; }
```

### Expected diagnosis

@WebMvcTest excludes repositories and services by design.

### Corrected code

```java
@WebMvcTest(ItemController.class)
class ItemTest { @MockBean ItemService service; }
```

### Regression tests

```java
// The MVC slice starts and the controller uses the mocked service.
```

## TEST-M-002: security filter breaks repository test

- Difficulty: Medium
- Framework: Spring Testing Slices
- Language: Java
- Perspective: Data slice
- Concept: security filter breaks repository test
- Symptom: A @DataJpaTest request unexpectedly requires authentication.
- Diagnostic goal: Keep slice scope clear and import only needed configuration.

### Buggy code

```java
@DataJpaTest
class ItemRepositoryTest {}
```

### Expected diagnosis

Importing the full application security configuration changes a focused persistence test.

### Corrected code

```java
@DataJpaTest
@Import(TestDatabaseConfig.class)
class ItemRepositoryTest {}
```

### Regression tests

```java
// The test uses the slice database without loading web security.
```

## TEST-M-003: missing csrf token

- Difficulty: Medium
- Framework: Spring Testing Slices
- Language: Java
- Perspective: MockMvc
- Concept: missing csrf token
- Symptom: A POST test receives 403 unexpectedly.
- Diagnostic goal: Include the security test request post processor.

### Buggy code

```java
mockMvc.perform(post("/items").content(json));
```

### Expected diagnosis

CSRF protection correctly rejects a state-changing request without a token.

### Corrected code

```java
mockMvc.perform(post("/items").with(csrf()).contentType(APPLICATION_JSON).content(json));
```

### Regression tests

```java
// The valid authenticated request passes CSRF and reaches the controller.
```

## TEST-M-004: wrong test configuration

- Difficulty: Medium
- Framework: Spring Testing Slices
- Language: Java
- Perspective: Context bootstrap
- Concept: wrong test configuration
- Symptom: The test starts the wrong application context.
- Diagnostic goal: Load the test configuration that supplies its collaborators.

### Buggy code

```java
@ContextConfiguration(classes = ProductionConfig.class)
class Test {}
```

### Expected diagnosis

A focused test should load the test configuration that supplies its collaborators.

### Corrected code

```java
@ContextConfiguration(classes = TestConfig.class)
class Test {}
```

### Regression tests

```java
// The context contains test doubles and no production connections.
```

## TEST-M-005: mock returns null default

- Difficulty: Medium
- Framework: Spring Testing Slices
- Language: Java
- Perspective: Mocking
- Concept: mock returns null default
- Symptom: The controller throws while the test expects a response.
- Diagnostic goal: Stub the collaborator path that the handler actually uses.

### Buggy code

```java
when(service.find(1L)).thenReturn(null);
```

### Expected diagnosis

Mockito returns null unless the test configures the expected value, so DTO mapping fails.

### Corrected code

```java
when(service.find(1L)).thenReturn(Optional.of(item));
```

### Regression tests

```java
// The success path receives the expected domain object.
```

## TEST-M-006: test rollback assumption

- Difficulty: Medium
- Framework: Spring Testing Slices
- Language: Java
- Perspective: Transactions
- Concept: test rollback assumption
- Symptom: Data leaks between tests.
- Diagnostic goal: Use transactional rollback or clean the database explicitly.

### Buggy code

```java
@SpringBootTest
class ItemTest { @Test void creates() { repository.save(item); } }
```

### Expected diagnosis

A full integration test does not automatically roll back unless a transaction is active for the test.

### Corrected code

```java
@SpringBootTest
@Transactional
class ItemTest { ... }
```

### Regression tests

```java
// Each test starts with a clean database state.
```

## TEST-M-007: container not ready

- Difficulty: Medium
- Framework: Spring Testing Slices
- Language: Java
- Perspective: Test containers
- Concept: container not ready
- Symptom: Integration tests race database startup.
- Diagnostic goal: Use the container lifecycle and dynamic property registration.

### Buggy code

```java
static PostgreSQLContainer<?> db = new PostgreSQLContainer<>("postgres:16");
```

### Expected diagnosis

Creating a container is insufficient if it is not started and its properties are not bound.

### Corrected code

```java
@Container static PostgreSQLContainer<?> db = new PostgreSQLContainer<>("postgres:16");
@DynamicPropertySource static void props(DynamicPropertyRegistry r) { r.add("spring.datasource.url", db::getJdbcUrl); }
```

### Regression tests

```java
// The application datasource points at the running container.
```

## TEST-M-008: only status asserted

- Difficulty: Medium
- Framework: Spring Testing Slices
- Language: Java
- Perspective: Assertions
- Concept: only status asserted
- Symptom: A regression changes the response body unnoticed.
- Diagnostic goal: Assert status, headers, and meaningful payload fields.

### Buggy code

```java
mockMvc.perform(get("/items/1")).andExpect(status().isOk());
```

### Expected diagnosis

A 200 response can still contain the wrong representation.

### Corrected code

```java
mockMvc.perform(get("/items/1")).andExpect(status().isOk()).andExpect(jsonPath("$.id").value(1));
```

### Regression tests

```java
// The contract test fails when the id or JSON shape changes.
```

## TEST-M-009: async result asserted too early

- Difficulty: Medium
- Framework: Spring Testing Slices
- Language: Java
- Perspective: Async tests
- Concept: async result asserted too early
- Symptom: The test is flaky or sees an empty response.
- Diagnostic goal: Wait for the async dispatch before asserting the final result.

### Buggy code

```java
mockMvc.perform(get("/report")).andExpect(status().isOk());
```

### Expected diagnosis

A controller returning a CompletableFuture requires async dispatch handling.

### Corrected code

```java
MvcResult result = mockMvc.perform(get("/report")).andReturn();
mockMvc.perform(asyncDispatch(result)).andExpect(status().isOk());
```

### Regression tests

```java
// The test waits for completion deterministically.
```

## TEST-M-010: test bean overridden by production bean

- Difficulty: Medium
- Framework: Spring Testing Slices
- Language: Java
- Perspective: Profiles
- Concept: test bean overridden by production bean
- Symptom: A test double is ignored.
- Diagnostic goal: Use profile or primary/qualifier rules deliberately.

### Buggy code

```java
@ActiveProfiles("test")
class ServiceTest {}
```

### Expected diagnosis

The test profile alone does not replace a production bean with the same role.

### Corrected code

```java
@TestConfiguration
static class Doubles { @Bean @Primary PaymentGateway gateway() { return new FakeGateway(); } }
```

### Regression tests

```java
// The test resolves the fake gateway and production behavior is isolated.
```

## TEST-M-011: repository missing in @WebMvcTest

- Difficulty: Medium
- Framework: Spring Testing Slices
- Language: Java
- Perspective: Web slice
- Concept: repository missing in @WebMvcTest
- Symptom: The controller test context cannot start.
- Diagnostic goal: Mock only collaborators outside the selected slice.

### Buggy code

```java
@WebMvcTest(ItemController.class)
class ItemTest { @Autowired ItemRepository repository; }
```

### Expected diagnosis

@WebMvcTest excludes repositories and services by design.

### Corrected code

```java
@WebMvcTest(ItemController.class)
class ItemTest { @MockBean ItemService service; }
```

### Regression tests

```java
// The MVC slice starts and the controller uses the mocked service.
```

## TEST-M-012: security filter breaks repository test

- Difficulty: Medium
- Framework: Spring Testing Slices
- Language: Java
- Perspective: Data slice
- Concept: security filter breaks repository test
- Symptom: A @DataJpaTest request unexpectedly requires authentication.
- Diagnostic goal: Keep slice scope clear and import only needed configuration.

### Buggy code

```java
@DataJpaTest
class ItemRepositoryTest {}
```

### Expected diagnosis

Importing the full application security configuration changes a focused persistence test.

### Corrected code

```java
@DataJpaTest
@Import(TestDatabaseConfig.class)
class ItemRepositoryTest {}
```

### Regression tests

```java
// The test uses the slice database without loading web security.
```

## TEST-M-013: missing csrf token

- Difficulty: Medium
- Framework: Spring Testing Slices
- Language: Java
- Perspective: MockMvc
- Concept: missing csrf token
- Symptom: A POST test receives 403 unexpectedly.
- Diagnostic goal: Include the security test request post processor.

### Buggy code

```java
mockMvc.perform(post("/items").content(json));
```

### Expected diagnosis

CSRF protection correctly rejects a state-changing request without a token.

### Corrected code

```java
mockMvc.perform(post("/items").with(csrf()).contentType(APPLICATION_JSON).content(json));
```

### Regression tests

```java
// The valid authenticated request passes CSRF and reaches the controller.
```

## TEST-M-014: wrong test configuration

- Difficulty: Medium
- Framework: Spring Testing Slices
- Language: Java
- Perspective: Context bootstrap
- Concept: wrong test configuration
- Symptom: The test starts the wrong application context.
- Diagnostic goal: Load the test configuration that supplies its collaborators.

### Buggy code

```java
@ContextConfiguration(classes = ProductionConfig.class)
class Test {}
```

### Expected diagnosis

A focused test should load the test configuration that supplies its collaborators.

### Corrected code

```java
@ContextConfiguration(classes = TestConfig.class)
class Test {}
```

### Regression tests

```java
// The context contains test doubles and no production connections.
```

## TEST-M-015: mock returns null default

- Difficulty: Medium
- Framework: Spring Testing Slices
- Language: Java
- Perspective: Mocking
- Concept: mock returns null default
- Symptom: The controller throws while the test expects a response.
- Diagnostic goal: Stub the collaborator path that the handler actually uses.

### Buggy code

```java
when(service.find(1L)).thenReturn(null);
```

### Expected diagnosis

Mockito returns null unless the test configures the expected value, so DTO mapping fails.

### Corrected code

```java
when(service.find(1L)).thenReturn(Optional.of(item));
```

### Regression tests

```java
// The success path receives the expected domain object.
```

## TEST-M-016: test rollback assumption

- Difficulty: Medium
- Framework: Spring Testing Slices
- Language: Java
- Perspective: Transactions
- Concept: test rollback assumption
- Symptom: Data leaks between tests.
- Diagnostic goal: Use transactional rollback or clean the database explicitly.

### Buggy code

```java
@SpringBootTest
class ItemTest { @Test void creates() { repository.save(item); } }
```

### Expected diagnosis

A full integration test does not automatically roll back unless a transaction is active for the test.

### Corrected code

```java
@SpringBootTest
@Transactional
class ItemTest { ... }
```

### Regression tests

```java
// Each test starts with a clean database state.
```

## TEST-M-017: container not ready

- Difficulty: Medium
- Framework: Spring Testing Slices
- Language: Java
- Perspective: Test containers
- Concept: container not ready
- Symptom: Integration tests race database startup.
- Diagnostic goal: Use the container lifecycle and dynamic property registration.

### Buggy code

```java
static PostgreSQLContainer<?> db = new PostgreSQLContainer<>("postgres:16");
```

### Expected diagnosis

Creating a container is insufficient if it is not started and its properties are not bound.

### Corrected code

```java
@Container static PostgreSQLContainer<?> db = new PostgreSQLContainer<>("postgres:16");
@DynamicPropertySource static void props(DynamicPropertyRegistry r) { r.add("spring.datasource.url", db::getJdbcUrl); }
```

### Regression tests

```java
// The application datasource points at the running container.
```

## TEST-M-018: only status asserted

- Difficulty: Medium
- Framework: Spring Testing Slices
- Language: Java
- Perspective: Assertions
- Concept: only status asserted
- Symptom: A regression changes the response body unnoticed.
- Diagnostic goal: Assert status, headers, and meaningful payload fields.

### Buggy code

```java
mockMvc.perform(get("/items/1")).andExpect(status().isOk());
```

### Expected diagnosis

A 200 response can still contain the wrong representation.

### Corrected code

```java
mockMvc.perform(get("/items/1")).andExpect(status().isOk()).andExpect(jsonPath("$.id").value(1));
```

### Regression tests

```java
// The contract test fails when the id or JSON shape changes.
```

## TEST-M-019: async result asserted too early

- Difficulty: Medium
- Framework: Spring Testing Slices
- Language: Java
- Perspective: Async tests
- Concept: async result asserted too early
- Symptom: The test is flaky or sees an empty response.
- Diagnostic goal: Wait for the async dispatch before asserting the final result.

### Buggy code

```java
mockMvc.perform(get("/report")).andExpect(status().isOk());
```

### Expected diagnosis

A controller returning a CompletableFuture requires async dispatch handling.

### Corrected code

```java
MvcResult result = mockMvc.perform(get("/report")).andReturn();
mockMvc.perform(asyncDispatch(result)).andExpect(status().isOk());
```

### Regression tests

```java
// The test waits for completion deterministically.
```

## TEST-M-020: test bean overridden by production bean

- Difficulty: Medium
- Framework: Spring Testing Slices
- Language: Java
- Perspective: Profiles
- Concept: test bean overridden by production bean
- Symptom: A test double is ignored.
- Diagnostic goal: Use profile or primary/qualifier rules deliberately.

### Buggy code

```java
@ActiveProfiles("test")
class ServiceTest {}
```

### Expected diagnosis

The test profile alone does not replace a production bean with the same role.

### Corrected code

```java
@TestConfiguration
static class Doubles { @Bean @Primary PaymentGateway gateway() { return new FakeGateway(); } }
```

### Regression tests

```java
// The test resolves the fake gateway and production behavior is isolated.
```

## TEST-M-021: repository missing in @WebMvcTest

- Difficulty: Medium
- Framework: Spring Testing Slices
- Language: Java
- Perspective: Web slice
- Concept: repository missing in @WebMvcTest
- Symptom: The controller test context cannot start.
- Diagnostic goal: Mock only collaborators outside the selected slice.

### Buggy code

```java
@WebMvcTest(ItemController.class)
class ItemTest { @Autowired ItemRepository repository; }
```

### Expected diagnosis

@WebMvcTest excludes repositories and services by design.

### Corrected code

```java
@WebMvcTest(ItemController.class)
class ItemTest { @MockBean ItemService service; }
```

### Regression tests

```java
// The MVC slice starts and the controller uses the mocked service.
```

## TEST-M-022: security filter breaks repository test

- Difficulty: Medium
- Framework: Spring Testing Slices
- Language: Java
- Perspective: Data slice
- Concept: security filter breaks repository test
- Symptom: A @DataJpaTest request unexpectedly requires authentication.
- Diagnostic goal: Keep slice scope clear and import only needed configuration.

### Buggy code

```java
@DataJpaTest
class ItemRepositoryTest {}
```

### Expected diagnosis

Importing the full application security configuration changes a focused persistence test.

### Corrected code

```java
@DataJpaTest
@Import(TestDatabaseConfig.class)
class ItemRepositoryTest {}
```

### Regression tests

```java
// The test uses the slice database without loading web security.
```

## TEST-M-023: missing csrf token

- Difficulty: Medium
- Framework: Spring Testing Slices
- Language: Java
- Perspective: MockMvc
- Concept: missing csrf token
- Symptom: A POST test receives 403 unexpectedly.
- Diagnostic goal: Include the security test request post processor.

### Buggy code

```java
mockMvc.perform(post("/items").content(json));
```

### Expected diagnosis

CSRF protection correctly rejects a state-changing request without a token.

### Corrected code

```java
mockMvc.perform(post("/items").with(csrf()).contentType(APPLICATION_JSON).content(json));
```

### Regression tests

```java
// The valid authenticated request passes CSRF and reaches the controller.
```

## TEST-M-024: wrong test configuration

- Difficulty: Medium
- Framework: Spring Testing Slices
- Language: Java
- Perspective: Context bootstrap
- Concept: wrong test configuration
- Symptom: The test starts the wrong application context.
- Diagnostic goal: Load the test configuration that supplies its collaborators.

### Buggy code

```java
@ContextConfiguration(classes = ProductionConfig.class)
class Test {}
```

### Expected diagnosis

A focused test should load the test configuration that supplies its collaborators.

### Corrected code

```java
@ContextConfiguration(classes = TestConfig.class)
class Test {}
```

### Regression tests

```java
// The context contains test doubles and no production connections.
```

## TEST-M-025: mock returns null default

- Difficulty: Medium
- Framework: Spring Testing Slices
- Language: Java
- Perspective: Mocking
- Concept: mock returns null default
- Symptom: The controller throws while the test expects a response.
- Diagnostic goal: Stub the collaborator path that the handler actually uses.

### Buggy code

```java
when(service.find(1L)).thenReturn(null);
```

### Expected diagnosis

Mockito returns null unless the test configures the expected value, so DTO mapping fails.

### Corrected code

```java
when(service.find(1L)).thenReturn(Optional.of(item));
```

### Regression tests

```java
// The success path receives the expected domain object.
```

## TEST-M-026: test rollback assumption

- Difficulty: Medium
- Framework: Spring Testing Slices
- Language: Java
- Perspective: Transactions
- Concept: test rollback assumption
- Symptom: Data leaks between tests.
- Diagnostic goal: Use transactional rollback or clean the database explicitly.

### Buggy code

```java
@SpringBootTest
class ItemTest { @Test void creates() { repository.save(item); } }
```

### Expected diagnosis

A full integration test does not automatically roll back unless a transaction is active for the test.

### Corrected code

```java
@SpringBootTest
@Transactional
class ItemTest { ... }
```

### Regression tests

```java
// Each test starts with a clean database state.
```

## TEST-M-027: container not ready

- Difficulty: Medium
- Framework: Spring Testing Slices
- Language: Java
- Perspective: Test containers
- Concept: container not ready
- Symptom: Integration tests race database startup.
- Diagnostic goal: Use the container lifecycle and dynamic property registration.

### Buggy code

```java
static PostgreSQLContainer<?> db = new PostgreSQLContainer<>("postgres:16");
```

### Expected diagnosis

Creating a container is insufficient if it is not started and its properties are not bound.

### Corrected code

```java
@Container static PostgreSQLContainer<?> db = new PostgreSQLContainer<>("postgres:16");
@DynamicPropertySource static void props(DynamicPropertyRegistry r) { r.add("spring.datasource.url", db::getJdbcUrl); }
```

### Regression tests

```java
// The application datasource points at the running container.
```

## TEST-M-028: only status asserted

- Difficulty: Medium
- Framework: Spring Testing Slices
- Language: Java
- Perspective: Assertions
- Concept: only status asserted
- Symptom: A regression changes the response body unnoticed.
- Diagnostic goal: Assert status, headers, and meaningful payload fields.

### Buggy code

```java
mockMvc.perform(get("/items/1")).andExpect(status().isOk());
```

### Expected diagnosis

A 200 response can still contain the wrong representation.

### Corrected code

```java
mockMvc.perform(get("/items/1")).andExpect(status().isOk()).andExpect(jsonPath("$.id").value(1));
```

### Regression tests

```java
// The contract test fails when the id or JSON shape changes.
```

## TEST-M-029: async result asserted too early

- Difficulty: Medium
- Framework: Spring Testing Slices
- Language: Java
- Perspective: Async tests
- Concept: async result asserted too early
- Symptom: The test is flaky or sees an empty response.
- Diagnostic goal: Wait for the async dispatch before asserting the final result.

### Buggy code

```java
mockMvc.perform(get("/report")).andExpect(status().isOk());
```

### Expected diagnosis

A controller returning a CompletableFuture requires async dispatch handling.

### Corrected code

```java
MvcResult result = mockMvc.perform(get("/report")).andReturn();
mockMvc.perform(asyncDispatch(result)).andExpect(status().isOk());
```

### Regression tests

```java
// The test waits for completion deterministically.
```

## TEST-M-030: test bean overridden by production bean

- Difficulty: Medium
- Framework: Spring Testing Slices
- Language: Java
- Perspective: Profiles
- Concept: test bean overridden by production bean
- Symptom: A test double is ignored.
- Diagnostic goal: Use profile or primary/qualifier rules deliberately.

### Buggy code

```java
@ActiveProfiles("test")
class ServiceTest {}
```

### Expected diagnosis

The test profile alone does not replace a production bean with the same role.

### Corrected code

```java
@TestConfiguration
static class Doubles { @Bean @Primary PaymentGateway gateway() { return new FakeGateway(); } }
```

### Regression tests

```java
// The test resolves the fake gateway and production behavior is isolated.
```

## TEST-M-031: repository missing in @WebMvcTest

- Difficulty: Medium
- Framework: Spring Testing Slices
- Language: Java
- Perspective: Web slice
- Concept: repository missing in @WebMvcTest
- Symptom: The controller test context cannot start.
- Diagnostic goal: Mock only collaborators outside the selected slice.

### Buggy code

```java
@WebMvcTest(ItemController.class)
class ItemTest { @Autowired ItemRepository repository; }
```

### Expected diagnosis

@WebMvcTest excludes repositories and services by design.

### Corrected code

```java
@WebMvcTest(ItemController.class)
class ItemTest { @MockBean ItemService service; }
```

### Regression tests

```java
// The MVC slice starts and the controller uses the mocked service.
```

## TEST-M-032: security filter breaks repository test

- Difficulty: Medium
- Framework: Spring Testing Slices
- Language: Java
- Perspective: Data slice
- Concept: security filter breaks repository test
- Symptom: A @DataJpaTest request unexpectedly requires authentication.
- Diagnostic goal: Keep slice scope clear and import only needed configuration.

### Buggy code

```java
@DataJpaTest
class ItemRepositoryTest {}
```

### Expected diagnosis

Importing the full application security configuration changes a focused persistence test.

### Corrected code

```java
@DataJpaTest
@Import(TestDatabaseConfig.class)
class ItemRepositoryTest {}
```

### Regression tests

```java
// The test uses the slice database without loading web security.
```

## TEST-M-033: missing csrf token

- Difficulty: Medium
- Framework: Spring Testing Slices
- Language: Java
- Perspective: MockMvc
- Concept: missing csrf token
- Symptom: A POST test receives 403 unexpectedly.
- Diagnostic goal: Include the security test request post processor.

### Buggy code

```java
mockMvc.perform(post("/items").content(json));
```

### Expected diagnosis

CSRF protection correctly rejects a state-changing request without a token.

### Corrected code

```java
mockMvc.perform(post("/items").with(csrf()).contentType(APPLICATION_JSON).content(json));
```

### Regression tests

```java
// The valid authenticated request passes CSRF and reaches the controller.
```

## TEST-M-034: wrong test configuration

- Difficulty: Medium
- Framework: Spring Testing Slices
- Language: Java
- Perspective: Context bootstrap
- Concept: wrong test configuration
- Symptom: The test starts the wrong application context.
- Diagnostic goal: Load the test configuration that supplies its collaborators.

### Buggy code

```java
@ContextConfiguration(classes = ProductionConfig.class)
class Test {}
```

### Expected diagnosis

A focused test should load the test configuration that supplies its collaborators.

### Corrected code

```java
@ContextConfiguration(classes = TestConfig.class)
class Test {}
```

### Regression tests

```java
// The context contains test doubles and no production connections.
```

## TEST-M-035: mock returns null default

- Difficulty: Medium
- Framework: Spring Testing Slices
- Language: Java
- Perspective: Mocking
- Concept: mock returns null default
- Symptom: The controller throws while the test expects a response.
- Diagnostic goal: Stub the collaborator path that the handler actually uses.

### Buggy code

```java
when(service.find(1L)).thenReturn(null);
```

### Expected diagnosis

Mockito returns null unless the test configures the expected value, so DTO mapping fails.

### Corrected code

```java
when(service.find(1L)).thenReturn(Optional.of(item));
```

### Regression tests

```java
// The success path receives the expected domain object.
```

## TEST-M-036: test rollback assumption

- Difficulty: Medium
- Framework: Spring Testing Slices
- Language: Java
- Perspective: Transactions
- Concept: test rollback assumption
- Symptom: Data leaks between tests.
- Diagnostic goal: Use transactional rollback or clean the database explicitly.

### Buggy code

```java
@SpringBootTest
class ItemTest { @Test void creates() { repository.save(item); } }
```

### Expected diagnosis

A full integration test does not automatically roll back unless a transaction is active for the test.

### Corrected code

```java
@SpringBootTest
@Transactional
class ItemTest { ... }
```

### Regression tests

```java
// Each test starts with a clean database state.
```

## TEST-M-037: container not ready

- Difficulty: Medium
- Framework: Spring Testing Slices
- Language: Java
- Perspective: Test containers
- Concept: container not ready
- Symptom: Integration tests race database startup.
- Diagnostic goal: Use the container lifecycle and dynamic property registration.

### Buggy code

```java
static PostgreSQLContainer<?> db = new PostgreSQLContainer<>("postgres:16");
```

### Expected diagnosis

Creating a container is insufficient if it is not started and its properties are not bound.

### Corrected code

```java
@Container static PostgreSQLContainer<?> db = new PostgreSQLContainer<>("postgres:16");
@DynamicPropertySource static void props(DynamicPropertyRegistry r) { r.add("spring.datasource.url", db::getJdbcUrl); }
```

### Regression tests

```java
// The application datasource points at the running container.
```

## TEST-M-038: only status asserted

- Difficulty: Medium
- Framework: Spring Testing Slices
- Language: Java
- Perspective: Assertions
- Concept: only status asserted
- Symptom: A regression changes the response body unnoticed.
- Diagnostic goal: Assert status, headers, and meaningful payload fields.

### Buggy code

```java
mockMvc.perform(get("/items/1")).andExpect(status().isOk());
```

### Expected diagnosis

A 200 response can still contain the wrong representation.

### Corrected code

```java
mockMvc.perform(get("/items/1")).andExpect(status().isOk()).andExpect(jsonPath("$.id").value(1));
```

### Regression tests

```java
// The contract test fails when the id or JSON shape changes.
```

## TEST-M-039: async result asserted too early

- Difficulty: Medium
- Framework: Spring Testing Slices
- Language: Java
- Perspective: Async tests
- Concept: async result asserted too early
- Symptom: The test is flaky or sees an empty response.
- Diagnostic goal: Wait for the async dispatch before asserting the final result.

### Buggy code

```java
mockMvc.perform(get("/report")).andExpect(status().isOk());
```

### Expected diagnosis

A controller returning a CompletableFuture requires async dispatch handling.

### Corrected code

```java
MvcResult result = mockMvc.perform(get("/report")).andReturn();
mockMvc.perform(asyncDispatch(result)).andExpect(status().isOk());
```

### Regression tests

```java
// The test waits for completion deterministically.
```

## TEST-M-040: test bean overridden by production bean

- Difficulty: Medium
- Framework: Spring Testing Slices
- Language: Java
- Perspective: Profiles
- Concept: test bean overridden by production bean
- Symptom: A test double is ignored.
- Diagnostic goal: Use profile or primary/qualifier rules deliberately.

### Buggy code

```java
@ActiveProfiles("test")
class ServiceTest {}
```

### Expected diagnosis

The test profile alone does not replace a production bean with the same role.

### Corrected code

```java
@TestConfiguration
static class Doubles { @Bean @Primary PaymentGateway gateway() { return new FakeGateway(); } }
```

### Regression tests

```java
// The test resolves the fake gateway and production behavior is isolated.
```

## TEST-M-041: repository missing in @WebMvcTest

- Difficulty: Medium
- Framework: Spring Testing Slices
- Language: Java
- Perspective: Web slice
- Concept: repository missing in @WebMvcTest
- Symptom: The controller test context cannot start.
- Diagnostic goal: Mock only collaborators outside the selected slice.

### Buggy code

```java
@WebMvcTest(ItemController.class)
class ItemTest { @Autowired ItemRepository repository; }
```

### Expected diagnosis

@WebMvcTest excludes repositories and services by design.

### Corrected code

```java
@WebMvcTest(ItemController.class)
class ItemTest { @MockBean ItemService service; }
```

### Regression tests

```java
// The MVC slice starts and the controller uses the mocked service.
```

## TEST-M-042: security filter breaks repository test

- Difficulty: Medium
- Framework: Spring Testing Slices
- Language: Java
- Perspective: Data slice
- Concept: security filter breaks repository test
- Symptom: A @DataJpaTest request unexpectedly requires authentication.
- Diagnostic goal: Keep slice scope clear and import only needed configuration.

### Buggy code

```java
@DataJpaTest
class ItemRepositoryTest {}
```

### Expected diagnosis

Importing the full application security configuration changes a focused persistence test.

### Corrected code

```java
@DataJpaTest
@Import(TestDatabaseConfig.class)
class ItemRepositoryTest {}
```

### Regression tests

```java
// The test uses the slice database without loading web security.
```

## TEST-M-043: missing csrf token

- Difficulty: Medium
- Framework: Spring Testing Slices
- Language: Java
- Perspective: MockMvc
- Concept: missing csrf token
- Symptom: A POST test receives 403 unexpectedly.
- Diagnostic goal: Include the security test request post processor.

### Buggy code

```java
mockMvc.perform(post("/items").content(json));
```

### Expected diagnosis

CSRF protection correctly rejects a state-changing request without a token.

### Corrected code

```java
mockMvc.perform(post("/items").with(csrf()).contentType(APPLICATION_JSON).content(json));
```

### Regression tests

```java
// The valid authenticated request passes CSRF and reaches the controller.
```

## TEST-M-044: wrong test configuration

- Difficulty: Medium
- Framework: Spring Testing Slices
- Language: Java
- Perspective: Context bootstrap
- Concept: wrong test configuration
- Symptom: The test starts the wrong application context.
- Diagnostic goal: Load the test configuration that supplies its collaborators.

### Buggy code

```java
@ContextConfiguration(classes = ProductionConfig.class)
class Test {}
```

### Expected diagnosis

A focused test should load the test configuration that supplies its collaborators.

### Corrected code

```java
@ContextConfiguration(classes = TestConfig.class)
class Test {}
```

### Regression tests

```java
// The context contains test doubles and no production connections.
```

## TEST-M-045: mock returns null default

- Difficulty: Medium
- Framework: Spring Testing Slices
- Language: Java
- Perspective: Mocking
- Concept: mock returns null default
- Symptom: The controller throws while the test expects a response.
- Diagnostic goal: Stub the collaborator path that the handler actually uses.

### Buggy code

```java
when(service.find(1L)).thenReturn(null);
```

### Expected diagnosis

Mockito returns null unless the test configures the expected value, so DTO mapping fails.

### Corrected code

```java
when(service.find(1L)).thenReturn(Optional.of(item));
```

### Regression tests

```java
// The success path receives the expected domain object.
```

## TEST-M-046: test rollback assumption

- Difficulty: Medium
- Framework: Spring Testing Slices
- Language: Java
- Perspective: Transactions
- Concept: test rollback assumption
- Symptom: Data leaks between tests.
- Diagnostic goal: Use transactional rollback or clean the database explicitly.

### Buggy code

```java
@SpringBootTest
class ItemTest { @Test void creates() { repository.save(item); } }
```

### Expected diagnosis

A full integration test does not automatically roll back unless a transaction is active for the test.

### Corrected code

```java
@SpringBootTest
@Transactional
class ItemTest { ... }
```

### Regression tests

```java
// Each test starts with a clean database state.
```

## TEST-M-047: container not ready

- Difficulty: Medium
- Framework: Spring Testing Slices
- Language: Java
- Perspective: Test containers
- Concept: container not ready
- Symptom: Integration tests race database startup.
- Diagnostic goal: Use the container lifecycle and dynamic property registration.

### Buggy code

```java
static PostgreSQLContainer<?> db = new PostgreSQLContainer<>("postgres:16");
```

### Expected diagnosis

Creating a container is insufficient if it is not started and its properties are not bound.

### Corrected code

```java
@Container static PostgreSQLContainer<?> db = new PostgreSQLContainer<>("postgres:16");
@DynamicPropertySource static void props(DynamicPropertyRegistry r) { r.add("spring.datasource.url", db::getJdbcUrl); }
```

### Regression tests

```java
// The application datasource points at the running container.
```

## TEST-M-048: only status asserted

- Difficulty: Medium
- Framework: Spring Testing Slices
- Language: Java
- Perspective: Assertions
- Concept: only status asserted
- Symptom: A regression changes the response body unnoticed.
- Diagnostic goal: Assert status, headers, and meaningful payload fields.

### Buggy code

```java
mockMvc.perform(get("/items/1")).andExpect(status().isOk());
```

### Expected diagnosis

A 200 response can still contain the wrong representation.

### Corrected code

```java
mockMvc.perform(get("/items/1")).andExpect(status().isOk()).andExpect(jsonPath("$.id").value(1));
```

### Regression tests

```java
// The contract test fails when the id or JSON shape changes.
```

## TEST-M-049: async result asserted too early

- Difficulty: Medium
- Framework: Spring Testing Slices
- Language: Java
- Perspective: Async tests
- Concept: async result asserted too early
- Symptom: The test is flaky or sees an empty response.
- Diagnostic goal: Wait for the async dispatch before asserting the final result.

### Buggy code

```java
mockMvc.perform(get("/report")).andExpect(status().isOk());
```

### Expected diagnosis

A controller returning a CompletableFuture requires async dispatch handling.

### Corrected code

```java
MvcResult result = mockMvc.perform(get("/report")).andReturn();
mockMvc.perform(asyncDispatch(result)).andExpect(status().isOk());
```

### Regression tests

```java
// The test waits for completion deterministically.
```

## TEST-M-050: test bean overridden by production bean

- Difficulty: Medium
- Framework: Spring Testing Slices
- Language: Java
- Perspective: Profiles
- Concept: test bean overridden by production bean
- Symptom: A test double is ignored.
- Diagnostic goal: Use profile or primary/qualifier rules deliberately.

### Buggy code

```java
@ActiveProfiles("test")
class ServiceTest {}
```

### Expected diagnosis

The test profile alone does not replace a production bean with the same role.

### Corrected code

```java
@TestConfiguration
static class Doubles { @Bean @Primary PaymentGateway gateway() { return new FakeGateway(); } }
```

### Regression tests

```java
// The test resolves the fake gateway and production behavior is isolated.
```

## TEST-M-051: repository missing in @WebMvcTest

- Difficulty: Medium
- Framework: Spring Testing Slices
- Language: Java
- Perspective: Web slice
- Concept: repository missing in @WebMvcTest
- Symptom: The controller test context cannot start.
- Diagnostic goal: Mock only collaborators outside the selected slice.

### Buggy code

```java
@WebMvcTest(ItemController.class)
class ItemTest { @Autowired ItemRepository repository; }
```

### Expected diagnosis

@WebMvcTest excludes repositories and services by design.

### Corrected code

```java
@WebMvcTest(ItemController.class)
class ItemTest { @MockBean ItemService service; }
```

### Regression tests

```java
// The MVC slice starts and the controller uses the mocked service.
```

## TEST-M-052: security filter breaks repository test

- Difficulty: Medium
- Framework: Spring Testing Slices
- Language: Java
- Perspective: Data slice
- Concept: security filter breaks repository test
- Symptom: A @DataJpaTest request unexpectedly requires authentication.
- Diagnostic goal: Keep slice scope clear and import only needed configuration.

### Buggy code

```java
@DataJpaTest
class ItemRepositoryTest {}
```

### Expected diagnosis

Importing the full application security configuration changes a focused persistence test.

### Corrected code

```java
@DataJpaTest
@Import(TestDatabaseConfig.class)
class ItemRepositoryTest {}
```

### Regression tests

```java
// The test uses the slice database without loading web security.
```

## TEST-M-053: missing csrf token

- Difficulty: Medium
- Framework: Spring Testing Slices
- Language: Java
- Perspective: MockMvc
- Concept: missing csrf token
- Symptom: A POST test receives 403 unexpectedly.
- Diagnostic goal: Include the security test request post processor.

### Buggy code

```java
mockMvc.perform(post("/items").content(json));
```

### Expected diagnosis

CSRF protection correctly rejects a state-changing request without a token.

### Corrected code

```java
mockMvc.perform(post("/items").with(csrf()).contentType(APPLICATION_JSON).content(json));
```

### Regression tests

```java
// The valid authenticated request passes CSRF and reaches the controller.
```

## TEST-M-054: wrong test configuration

- Difficulty: Medium
- Framework: Spring Testing Slices
- Language: Java
- Perspective: Context bootstrap
- Concept: wrong test configuration
- Symptom: The test starts the wrong application context.
- Diagnostic goal: Load the test configuration that supplies its collaborators.

### Buggy code

```java
@ContextConfiguration(classes = ProductionConfig.class)
class Test {}
```

### Expected diagnosis

A focused test should load the test configuration that supplies its collaborators.

### Corrected code

```java
@ContextConfiguration(classes = TestConfig.class)
class Test {}
```

### Regression tests

```java
// The context contains test doubles and no production connections.
```

## TEST-M-055: mock returns null default

- Difficulty: Medium
- Framework: Spring Testing Slices
- Language: Java
- Perspective: Mocking
- Concept: mock returns null default
- Symptom: The controller throws while the test expects a response.
- Diagnostic goal: Stub the collaborator path that the handler actually uses.

### Buggy code

```java
when(service.find(1L)).thenReturn(null);
```

### Expected diagnosis

Mockito returns null unless the test configures the expected value, so DTO mapping fails.

### Corrected code

```java
when(service.find(1L)).thenReturn(Optional.of(item));
```

### Regression tests

```java
// The success path receives the expected domain object.
```

## TEST-M-056: test rollback assumption

- Difficulty: Medium
- Framework: Spring Testing Slices
- Language: Java
- Perspective: Transactions
- Concept: test rollback assumption
- Symptom: Data leaks between tests.
- Diagnostic goal: Use transactional rollback or clean the database explicitly.

### Buggy code

```java
@SpringBootTest
class ItemTest { @Test void creates() { repository.save(item); } }
```

### Expected diagnosis

A full integration test does not automatically roll back unless a transaction is active for the test.

### Corrected code

```java
@SpringBootTest
@Transactional
class ItemTest { ... }
```

### Regression tests

```java
// Each test starts with a clean database state.
```

## TEST-M-057: container not ready

- Difficulty: Medium
- Framework: Spring Testing Slices
- Language: Java
- Perspective: Test containers
- Concept: container not ready
- Symptom: Integration tests race database startup.
- Diagnostic goal: Use the container lifecycle and dynamic property registration.

### Buggy code

```java
static PostgreSQLContainer<?> db = new PostgreSQLContainer<>("postgres:16");
```

### Expected diagnosis

Creating a container is insufficient if it is not started and its properties are not bound.

### Corrected code

```java
@Container static PostgreSQLContainer<?> db = new PostgreSQLContainer<>("postgres:16");
@DynamicPropertySource static void props(DynamicPropertyRegistry r) { r.add("spring.datasource.url", db::getJdbcUrl); }
```

### Regression tests

```java
// The application datasource points at the running container.
```

## TEST-M-058: only status asserted

- Difficulty: Medium
- Framework: Spring Testing Slices
- Language: Java
- Perspective: Assertions
- Concept: only status asserted
- Symptom: A regression changes the response body unnoticed.
- Diagnostic goal: Assert status, headers, and meaningful payload fields.

### Buggy code

```java
mockMvc.perform(get("/items/1")).andExpect(status().isOk());
```

### Expected diagnosis

A 200 response can still contain the wrong representation.

### Corrected code

```java
mockMvc.perform(get("/items/1")).andExpect(status().isOk()).andExpect(jsonPath("$.id").value(1));
```

### Regression tests

```java
// The contract test fails when the id or JSON shape changes.
```

## TEST-M-059: async result asserted too early

- Difficulty: Medium
- Framework: Spring Testing Slices
- Language: Java
- Perspective: Async tests
- Concept: async result asserted too early
- Symptom: The test is flaky or sees an empty response.
- Diagnostic goal: Wait for the async dispatch before asserting the final result.

### Buggy code

```java
mockMvc.perform(get("/report")).andExpect(status().isOk());
```

### Expected diagnosis

A controller returning a CompletableFuture requires async dispatch handling.

### Corrected code

```java
MvcResult result = mockMvc.perform(get("/report")).andReturn();
mockMvc.perform(asyncDispatch(result)).andExpect(status().isOk());
```

### Regression tests

```java
// The test waits for completion deterministically.
```

## TEST-M-060: test bean overridden by production bean

- Difficulty: Medium
- Framework: Spring Testing Slices
- Language: Java
- Perspective: Profiles
- Concept: test bean overridden by production bean
- Symptom: A test double is ignored.
- Diagnostic goal: Use profile or primary/qualifier rules deliberately.

### Buggy code

```java
@ActiveProfiles("test")
class ServiceTest {}
```

### Expected diagnosis

The test profile alone does not replace a production bean with the same role.

### Corrected code

```java
@TestConfiguration
static class Doubles { @Bean @Primary PaymentGateway gateway() { return new FakeGateway(); } }
```

### Regression tests

```java
// The test resolves the fake gateway and production behavior is isolated.
```

## TEST-M-061: repository missing in @WebMvcTest

- Difficulty: Medium
- Framework: Spring Testing Slices
- Language: Java
- Perspective: Web slice
- Concept: repository missing in @WebMvcTest
- Symptom: The controller test context cannot start.
- Diagnostic goal: Mock only collaborators outside the selected slice.

### Buggy code

```java
@WebMvcTest(ItemController.class)
class ItemTest { @Autowired ItemRepository repository; }
```

### Expected diagnosis

@WebMvcTest excludes repositories and services by design.

### Corrected code

```java
@WebMvcTest(ItemController.class)
class ItemTest { @MockBean ItemService service; }
```

### Regression tests

```java
// The MVC slice starts and the controller uses the mocked service.
```

## TEST-M-062: security filter breaks repository test

- Difficulty: Medium
- Framework: Spring Testing Slices
- Language: Java
- Perspective: Data slice
- Concept: security filter breaks repository test
- Symptom: A @DataJpaTest request unexpectedly requires authentication.
- Diagnostic goal: Keep slice scope clear and import only needed configuration.

### Buggy code

```java
@DataJpaTest
class ItemRepositoryTest {}
```

### Expected diagnosis

Importing the full application security configuration changes a focused persistence test.

### Corrected code

```java
@DataJpaTest
@Import(TestDatabaseConfig.class)
class ItemRepositoryTest {}
```

### Regression tests

```java
// The test uses the slice database without loading web security.
```

## TEST-M-063: missing csrf token

- Difficulty: Medium
- Framework: Spring Testing Slices
- Language: Java
- Perspective: MockMvc
- Concept: missing csrf token
- Symptom: A POST test receives 403 unexpectedly.
- Diagnostic goal: Include the security test request post processor.

### Buggy code

```java
mockMvc.perform(post("/items").content(json));
```

### Expected diagnosis

CSRF protection correctly rejects a state-changing request without a token.

### Corrected code

```java
mockMvc.perform(post("/items").with(csrf()).contentType(APPLICATION_JSON).content(json));
```

### Regression tests

```java
// The valid authenticated request passes CSRF and reaches the controller.
```

## TEST-M-064: wrong test configuration

- Difficulty: Medium
- Framework: Spring Testing Slices
- Language: Java
- Perspective: Context bootstrap
- Concept: wrong test configuration
- Symptom: The test starts the wrong application context.
- Diagnostic goal: Load the test configuration that supplies its collaborators.

### Buggy code

```java
@ContextConfiguration(classes = ProductionConfig.class)
class Test {}
```

### Expected diagnosis

A focused test should load the test configuration that supplies its collaborators.

### Corrected code

```java
@ContextConfiguration(classes = TestConfig.class)
class Test {}
```

### Regression tests

```java
// The context contains test doubles and no production connections.
```

## TEST-M-065: mock returns null default

- Difficulty: Medium
- Framework: Spring Testing Slices
- Language: Java
- Perspective: Mocking
- Concept: mock returns null default
- Symptom: The controller throws while the test expects a response.
- Diagnostic goal: Stub the collaborator path that the handler actually uses.

### Buggy code

```java
when(service.find(1L)).thenReturn(null);
```

### Expected diagnosis

Mockito returns null unless the test configures the expected value, so DTO mapping fails.

### Corrected code

```java
when(service.find(1L)).thenReturn(Optional.of(item));
```

### Regression tests

```java
// The success path receives the expected domain object.
```

## TEST-M-066: test rollback assumption

- Difficulty: Medium
- Framework: Spring Testing Slices
- Language: Java
- Perspective: Transactions
- Concept: test rollback assumption
- Symptom: Data leaks between tests.
- Diagnostic goal: Use transactional rollback or clean the database explicitly.

### Buggy code

```java
@SpringBootTest
class ItemTest { @Test void creates() { repository.save(item); } }
```

### Expected diagnosis

A full integration test does not automatically roll back unless a transaction is active for the test.

### Corrected code

```java
@SpringBootTest
@Transactional
class ItemTest { ... }
```

### Regression tests

```java
// Each test starts with a clean database state.
```

## TEST-M-067: container not ready

- Difficulty: Medium
- Framework: Spring Testing Slices
- Language: Java
- Perspective: Test containers
- Concept: container not ready
- Symptom: Integration tests race database startup.
- Diagnostic goal: Use the container lifecycle and dynamic property registration.

### Buggy code

```java
static PostgreSQLContainer<?> db = new PostgreSQLContainer<>("postgres:16");
```

### Expected diagnosis

Creating a container is insufficient if it is not started and its properties are not bound.

### Corrected code

```java
@Container static PostgreSQLContainer<?> db = new PostgreSQLContainer<>("postgres:16");
@DynamicPropertySource static void props(DynamicPropertyRegistry r) { r.add("spring.datasource.url", db::getJdbcUrl); }
```

### Regression tests

```java
// The application datasource points at the running container.
```

## TEST-M-068: only status asserted

- Difficulty: Medium
- Framework: Spring Testing Slices
- Language: Java
- Perspective: Assertions
- Concept: only status asserted
- Symptom: A regression changes the response body unnoticed.
- Diagnostic goal: Assert status, headers, and meaningful payload fields.

### Buggy code

```java
mockMvc.perform(get("/items/1")).andExpect(status().isOk());
```

### Expected diagnosis

A 200 response can still contain the wrong representation.

### Corrected code

```java
mockMvc.perform(get("/items/1")).andExpect(status().isOk()).andExpect(jsonPath("$.id").value(1));
```

### Regression tests

```java
// The contract test fails when the id or JSON shape changes.
```

## TEST-M-069: async result asserted too early

- Difficulty: Medium
- Framework: Spring Testing Slices
- Language: Java
- Perspective: Async tests
- Concept: async result asserted too early
- Symptom: The test is flaky or sees an empty response.
- Diagnostic goal: Wait for the async dispatch before asserting the final result.

### Buggy code

```java
mockMvc.perform(get("/report")).andExpect(status().isOk());
```

### Expected diagnosis

A controller returning a CompletableFuture requires async dispatch handling.

### Corrected code

```java
MvcResult result = mockMvc.perform(get("/report")).andReturn();
mockMvc.perform(asyncDispatch(result)).andExpect(status().isOk());
```

### Regression tests

```java
// The test waits for completion deterministically.
```

## TEST-M-070: test bean overridden by production bean

- Difficulty: Medium
- Framework: Spring Testing Slices
- Language: Java
- Perspective: Profiles
- Concept: test bean overridden by production bean
- Symptom: A test double is ignored.
- Diagnostic goal: Use profile or primary/qualifier rules deliberately.

### Buggy code

```java
@ActiveProfiles("test")
class ServiceTest {}
```

### Expected diagnosis

The test profile alone does not replace a production bean with the same role.

### Corrected code

```java
@TestConfiguration
static class Doubles { @Bean @Primary PaymentGateway gateway() { return new FakeGateway(); } }
```

### Regression tests

```java
// The test resolves the fake gateway and production behavior is isolated.
```

## TEST-M-071: repository missing in @WebMvcTest

- Difficulty: Medium
- Framework: Spring Testing Slices
- Language: Java
- Perspective: Web slice
- Concept: repository missing in @WebMvcTest
- Symptom: The controller test context cannot start.
- Diagnostic goal: Mock only collaborators outside the selected slice.

### Buggy code

```java
@WebMvcTest(ItemController.class)
class ItemTest { @Autowired ItemRepository repository; }
```

### Expected diagnosis

@WebMvcTest excludes repositories and services by design.

### Corrected code

```java
@WebMvcTest(ItemController.class)
class ItemTest { @MockBean ItemService service; }
```

### Regression tests

```java
// The MVC slice starts and the controller uses the mocked service.
```

## TEST-M-072: security filter breaks repository test

- Difficulty: Medium
- Framework: Spring Testing Slices
- Language: Java
- Perspective: Data slice
- Concept: security filter breaks repository test
- Symptom: A @DataJpaTest request unexpectedly requires authentication.
- Diagnostic goal: Keep slice scope clear and import only needed configuration.

### Buggy code

```java
@DataJpaTest
class ItemRepositoryTest {}
```

### Expected diagnosis

Importing the full application security configuration changes a focused persistence test.

### Corrected code

```java
@DataJpaTest
@Import(TestDatabaseConfig.class)
class ItemRepositoryTest {}
```

### Regression tests

```java
// The test uses the slice database without loading web security.
```

## TEST-M-073: missing csrf token

- Difficulty: Medium
- Framework: Spring Testing Slices
- Language: Java
- Perspective: MockMvc
- Concept: missing csrf token
- Symptom: A POST test receives 403 unexpectedly.
- Diagnostic goal: Include the security test request post processor.

### Buggy code

```java
mockMvc.perform(post("/items").content(json));
```

### Expected diagnosis

CSRF protection correctly rejects a state-changing request without a token.

### Corrected code

```java
mockMvc.perform(post("/items").with(csrf()).contentType(APPLICATION_JSON).content(json));
```

### Regression tests

```java
// The valid authenticated request passes CSRF and reaches the controller.
```

## TEST-M-074: wrong test configuration

- Difficulty: Medium
- Framework: Spring Testing Slices
- Language: Java
- Perspective: Context bootstrap
- Concept: wrong test configuration
- Symptom: The test starts the wrong application context.
- Diagnostic goal: Load the test configuration that supplies its collaborators.

### Buggy code

```java
@ContextConfiguration(classes = ProductionConfig.class)
class Test {}
```

### Expected diagnosis

A focused test should load the test configuration that supplies its collaborators.

### Corrected code

```java
@ContextConfiguration(classes = TestConfig.class)
class Test {}
```

### Regression tests

```java
// The context contains test doubles and no production connections.
```

## TEST-M-075: mock returns null default

- Difficulty: Medium
- Framework: Spring Testing Slices
- Language: Java
- Perspective: Mocking
- Concept: mock returns null default
- Symptom: The controller throws while the test expects a response.
- Diagnostic goal: Stub the collaborator path that the handler actually uses.

### Buggy code

```java
when(service.find(1L)).thenReturn(null);
```

### Expected diagnosis

Mockito returns null unless the test configures the expected value, so DTO mapping fails.

### Corrected code

```java
when(service.find(1L)).thenReturn(Optional.of(item));
```

### Regression tests

```java
// The success path receives the expected domain object.
```

## TEST-M-076: test rollback assumption

- Difficulty: Medium
- Framework: Spring Testing Slices
- Language: Java
- Perspective: Transactions
- Concept: test rollback assumption
- Symptom: Data leaks between tests.
- Diagnostic goal: Use transactional rollback or clean the database explicitly.

### Buggy code

```java
@SpringBootTest
class ItemTest { @Test void creates() { repository.save(item); } }
```

### Expected diagnosis

A full integration test does not automatically roll back unless a transaction is active for the test.

### Corrected code

```java
@SpringBootTest
@Transactional
class ItemTest { ... }
```

### Regression tests

```java
// Each test starts with a clean database state.
```

## TEST-M-077: container not ready

- Difficulty: Medium
- Framework: Spring Testing Slices
- Language: Java
- Perspective: Test containers
- Concept: container not ready
- Symptom: Integration tests race database startup.
- Diagnostic goal: Use the container lifecycle and dynamic property registration.

### Buggy code

```java
static PostgreSQLContainer<?> db = new PostgreSQLContainer<>("postgres:16");
```

### Expected diagnosis

Creating a container is insufficient if it is not started and its properties are not bound.

### Corrected code

```java
@Container static PostgreSQLContainer<?> db = new PostgreSQLContainer<>("postgres:16");
@DynamicPropertySource static void props(DynamicPropertyRegistry r) { r.add("spring.datasource.url", db::getJdbcUrl); }
```

### Regression tests

```java
// The application datasource points at the running container.
```

## TEST-M-078: only status asserted

- Difficulty: Medium
- Framework: Spring Testing Slices
- Language: Java
- Perspective: Assertions
- Concept: only status asserted
- Symptom: A regression changes the response body unnoticed.
- Diagnostic goal: Assert status, headers, and meaningful payload fields.

### Buggy code

```java
mockMvc.perform(get("/items/1")).andExpect(status().isOk());
```

### Expected diagnosis

A 200 response can still contain the wrong representation.

### Corrected code

```java
mockMvc.perform(get("/items/1")).andExpect(status().isOk()).andExpect(jsonPath("$.id").value(1));
```

### Regression tests

```java
// The contract test fails when the id or JSON shape changes.
```

## TEST-M-079: async result asserted too early

- Difficulty: Medium
- Framework: Spring Testing Slices
- Language: Java
- Perspective: Async tests
- Concept: async result asserted too early
- Symptom: The test is flaky or sees an empty response.
- Diagnostic goal: Wait for the async dispatch before asserting the final result.

### Buggy code

```java
mockMvc.perform(get("/report")).andExpect(status().isOk());
```

### Expected diagnosis

A controller returning a CompletableFuture requires async dispatch handling.

### Corrected code

```java
MvcResult result = mockMvc.perform(get("/report")).andReturn();
mockMvc.perform(asyncDispatch(result)).andExpect(status().isOk());
```

### Regression tests

```java
// The test waits for completion deterministically.
```

## TEST-M-080: test bean overridden by production bean

- Difficulty: Medium
- Framework: Spring Testing Slices
- Language: Java
- Perspective: Profiles
- Concept: test bean overridden by production bean
- Symptom: A test double is ignored.
- Diagnostic goal: Use profile or primary/qualifier rules deliberately.

### Buggy code

```java
@ActiveProfiles("test")
class ServiceTest {}
```

### Expected diagnosis

The test profile alone does not replace a production bean with the same role.

### Corrected code

```java
@TestConfiguration
static class Doubles { @Bean @Primary PaymentGateway gateway() { return new FakeGateway(); } }
```

### Regression tests

```java
// The test resolves the fake gateway and production behavior is isolated.
```

## TEST-M-081: repository missing in @WebMvcTest

- Difficulty: Medium
- Framework: Spring Testing Slices
- Language: Java
- Perspective: Web slice
- Concept: repository missing in @WebMvcTest
- Symptom: The controller test context cannot start.
- Diagnostic goal: Mock only collaborators outside the selected slice.

### Buggy code

```java
@WebMvcTest(ItemController.class)
class ItemTest { @Autowired ItemRepository repository; }
```

### Expected diagnosis

@WebMvcTest excludes repositories and services by design.

### Corrected code

```java
@WebMvcTest(ItemController.class)
class ItemTest { @MockBean ItemService service; }
```

### Regression tests

```java
// The MVC slice starts and the controller uses the mocked service.
```

## TEST-M-082: security filter breaks repository test

- Difficulty: Medium
- Framework: Spring Testing Slices
- Language: Java
- Perspective: Data slice
- Concept: security filter breaks repository test
- Symptom: A @DataJpaTest request unexpectedly requires authentication.
- Diagnostic goal: Keep slice scope clear and import only needed configuration.

### Buggy code

```java
@DataJpaTest
class ItemRepositoryTest {}
```

### Expected diagnosis

Importing the full application security configuration changes a focused persistence test.

### Corrected code

```java
@DataJpaTest
@Import(TestDatabaseConfig.class)
class ItemRepositoryTest {}
```

### Regression tests

```java
// The test uses the slice database without loading web security.
```

## TEST-M-083: missing csrf token

- Difficulty: Medium
- Framework: Spring Testing Slices
- Language: Java
- Perspective: MockMvc
- Concept: missing csrf token
- Symptom: A POST test receives 403 unexpectedly.
- Diagnostic goal: Include the security test request post processor.

### Buggy code

```java
mockMvc.perform(post("/items").content(json));
```

### Expected diagnosis

CSRF protection correctly rejects a state-changing request without a token.

### Corrected code

```java
mockMvc.perform(post("/items").with(csrf()).contentType(APPLICATION_JSON).content(json));
```

### Regression tests

```java
// The valid authenticated request passes CSRF and reaches the controller.
```

## TEST-M-084: wrong test configuration

- Difficulty: Medium
- Framework: Spring Testing Slices
- Language: Java
- Perspective: Context bootstrap
- Concept: wrong test configuration
- Symptom: The test starts the wrong application context.
- Diagnostic goal: Load the test configuration that supplies its collaborators.

### Buggy code

```java
@ContextConfiguration(classes = ProductionConfig.class)
class Test {}
```

### Expected diagnosis

A focused test should load the test configuration that supplies its collaborators.

### Corrected code

```java
@ContextConfiguration(classes = TestConfig.class)
class Test {}
```

### Regression tests

```java
// The context contains test doubles and no production connections.
```

## TEST-M-085: mock returns null default

- Difficulty: Medium
- Framework: Spring Testing Slices
- Language: Java
- Perspective: Mocking
- Concept: mock returns null default
- Symptom: The controller throws while the test expects a response.
- Diagnostic goal: Stub the collaborator path that the handler actually uses.

### Buggy code

```java
when(service.find(1L)).thenReturn(null);
```

### Expected diagnosis

Mockito returns null unless the test configures the expected value, so DTO mapping fails.

### Corrected code

```java
when(service.find(1L)).thenReturn(Optional.of(item));
```

### Regression tests

```java
// The success path receives the expected domain object.
```

## TEST-M-086: test rollback assumption

- Difficulty: Medium
- Framework: Spring Testing Slices
- Language: Java
- Perspective: Transactions
- Concept: test rollback assumption
- Symptom: Data leaks between tests.
- Diagnostic goal: Use transactional rollback or clean the database explicitly.

### Buggy code

```java
@SpringBootTest
class ItemTest { @Test void creates() { repository.save(item); } }
```

### Expected diagnosis

A full integration test does not automatically roll back unless a transaction is active for the test.

### Corrected code

```java
@SpringBootTest
@Transactional
class ItemTest { ... }
```

### Regression tests

```java
// Each test starts with a clean database state.
```

## TEST-M-087: container not ready

- Difficulty: Medium
- Framework: Spring Testing Slices
- Language: Java
- Perspective: Test containers
- Concept: container not ready
- Symptom: Integration tests race database startup.
- Diagnostic goal: Use the container lifecycle and dynamic property registration.

### Buggy code

```java
static PostgreSQLContainer<?> db = new PostgreSQLContainer<>("postgres:16");
```

### Expected diagnosis

Creating a container is insufficient if it is not started and its properties are not bound.

### Corrected code

```java
@Container static PostgreSQLContainer<?> db = new PostgreSQLContainer<>("postgres:16");
@DynamicPropertySource static void props(DynamicPropertyRegistry r) { r.add("spring.datasource.url", db::getJdbcUrl); }
```

### Regression tests

```java
// The application datasource points at the running container.
```

## TEST-M-088: only status asserted

- Difficulty: Medium
- Framework: Spring Testing Slices
- Language: Java
- Perspective: Assertions
- Concept: only status asserted
- Symptom: A regression changes the response body unnoticed.
- Diagnostic goal: Assert status, headers, and meaningful payload fields.

### Buggy code

```java
mockMvc.perform(get("/items/1")).andExpect(status().isOk());
```

### Expected diagnosis

A 200 response can still contain the wrong representation.

### Corrected code

```java
mockMvc.perform(get("/items/1")).andExpect(status().isOk()).andExpect(jsonPath("$.id").value(1));
```

### Regression tests

```java
// The contract test fails when the id or JSON shape changes.
```

## TEST-M-089: async result asserted too early

- Difficulty: Medium
- Framework: Spring Testing Slices
- Language: Java
- Perspective: Async tests
- Concept: async result asserted too early
- Symptom: The test is flaky or sees an empty response.
- Diagnostic goal: Wait for the async dispatch before asserting the final result.

### Buggy code

```java
mockMvc.perform(get("/report")).andExpect(status().isOk());
```

### Expected diagnosis

A controller returning a CompletableFuture requires async dispatch handling.

### Corrected code

```java
MvcResult result = mockMvc.perform(get("/report")).andReturn();
mockMvc.perform(asyncDispatch(result)).andExpect(status().isOk());
```

### Regression tests

```java
// The test waits for completion deterministically.
```

## TEST-M-090: test bean overridden by production bean

- Difficulty: Medium
- Framework: Spring Testing Slices
- Language: Java
- Perspective: Profiles
- Concept: test bean overridden by production bean
- Symptom: A test double is ignored.
- Diagnostic goal: Use profile or primary/qualifier rules deliberately.

### Buggy code

```java
@ActiveProfiles("test")
class ServiceTest {}
```

### Expected diagnosis

The test profile alone does not replace a production bean with the same role.

### Corrected code

```java
@TestConfiguration
static class Doubles { @Bean @Primary PaymentGateway gateway() { return new FakeGateway(); } }
```

### Regression tests

```java
// The test resolves the fake gateway and production behavior is isolated.
```

## TEST-M-091: repository missing in @WebMvcTest

- Difficulty: Medium
- Framework: Spring Testing Slices
- Language: Java
- Perspective: Web slice
- Concept: repository missing in @WebMvcTest
- Symptom: The controller test context cannot start.
- Diagnostic goal: Mock only collaborators outside the selected slice.

### Buggy code

```java
@WebMvcTest(ItemController.class)
class ItemTest { @Autowired ItemRepository repository; }
```

### Expected diagnosis

@WebMvcTest excludes repositories and services by design.

### Corrected code

```java
@WebMvcTest(ItemController.class)
class ItemTest { @MockBean ItemService service; }
```

### Regression tests

```java
// The MVC slice starts and the controller uses the mocked service.
```

## TEST-M-092: security filter breaks repository test

- Difficulty: Medium
- Framework: Spring Testing Slices
- Language: Java
- Perspective: Data slice
- Concept: security filter breaks repository test
- Symptom: A @DataJpaTest request unexpectedly requires authentication.
- Diagnostic goal: Keep slice scope clear and import only needed configuration.

### Buggy code

```java
@DataJpaTest
class ItemRepositoryTest {}
```

### Expected diagnosis

Importing the full application security configuration changes a focused persistence test.

### Corrected code

```java
@DataJpaTest
@Import(TestDatabaseConfig.class)
class ItemRepositoryTest {}
```

### Regression tests

```java
// The test uses the slice database without loading web security.
```

## TEST-M-093: missing csrf token

- Difficulty: Medium
- Framework: Spring Testing Slices
- Language: Java
- Perspective: MockMvc
- Concept: missing csrf token
- Symptom: A POST test receives 403 unexpectedly.
- Diagnostic goal: Include the security test request post processor.

### Buggy code

```java
mockMvc.perform(post("/items").content(json));
```

### Expected diagnosis

CSRF protection correctly rejects a state-changing request without a token.

### Corrected code

```java
mockMvc.perform(post("/items").with(csrf()).contentType(APPLICATION_JSON).content(json));
```

### Regression tests

```java
// The valid authenticated request passes CSRF and reaches the controller.
```

## TEST-M-094: wrong test configuration

- Difficulty: Medium
- Framework: Spring Testing Slices
- Language: Java
- Perspective: Context bootstrap
- Concept: wrong test configuration
- Symptom: The test starts the wrong application context.
- Diagnostic goal: Load the test configuration that supplies its collaborators.

### Buggy code

```java
@ContextConfiguration(classes = ProductionConfig.class)
class Test {}
```

### Expected diagnosis

A focused test should load the test configuration that supplies its collaborators.

### Corrected code

```java
@ContextConfiguration(classes = TestConfig.class)
class Test {}
```

### Regression tests

```java
// The context contains test doubles and no production connections.
```

## TEST-M-095: mock returns null default

- Difficulty: Medium
- Framework: Spring Testing Slices
- Language: Java
- Perspective: Mocking
- Concept: mock returns null default
- Symptom: The controller throws while the test expects a response.
- Diagnostic goal: Stub the collaborator path that the handler actually uses.

### Buggy code

```java
when(service.find(1L)).thenReturn(null);
```

### Expected diagnosis

Mockito returns null unless the test configures the expected value, so DTO mapping fails.

### Corrected code

```java
when(service.find(1L)).thenReturn(Optional.of(item));
```

### Regression tests

```java
// The success path receives the expected domain object.
```

## TEST-M-096: test rollback assumption

- Difficulty: Medium
- Framework: Spring Testing Slices
- Language: Java
- Perspective: Transactions
- Concept: test rollback assumption
- Symptom: Data leaks between tests.
- Diagnostic goal: Use transactional rollback or clean the database explicitly.

### Buggy code

```java
@SpringBootTest
class ItemTest { @Test void creates() { repository.save(item); } }
```

### Expected diagnosis

A full integration test does not automatically roll back unless a transaction is active for the test.

### Corrected code

```java
@SpringBootTest
@Transactional
class ItemTest { ... }
```

### Regression tests

```java
// Each test starts with a clean database state.
```

## TEST-M-097: container not ready

- Difficulty: Medium
- Framework: Spring Testing Slices
- Language: Java
- Perspective: Test containers
- Concept: container not ready
- Symptom: Integration tests race database startup.
- Diagnostic goal: Use the container lifecycle and dynamic property registration.

### Buggy code

```java
static PostgreSQLContainer<?> db = new PostgreSQLContainer<>("postgres:16");
```

### Expected diagnosis

Creating a container is insufficient if it is not started and its properties are not bound.

### Corrected code

```java
@Container static PostgreSQLContainer<?> db = new PostgreSQLContainer<>("postgres:16");
@DynamicPropertySource static void props(DynamicPropertyRegistry r) { r.add("spring.datasource.url", db::getJdbcUrl); }
```

### Regression tests

```java
// The application datasource points at the running container.
```

## TEST-M-098: only status asserted

- Difficulty: Medium
- Framework: Spring Testing Slices
- Language: Java
- Perspective: Assertions
- Concept: only status asserted
- Symptom: A regression changes the response body unnoticed.
- Diagnostic goal: Assert status, headers, and meaningful payload fields.

### Buggy code

```java
mockMvc.perform(get("/items/1")).andExpect(status().isOk());
```

### Expected diagnosis

A 200 response can still contain the wrong representation.

### Corrected code

```java
mockMvc.perform(get("/items/1")).andExpect(status().isOk()).andExpect(jsonPath("$.id").value(1));
```

### Regression tests

```java
// The contract test fails when the id or JSON shape changes.
```

## TEST-M-099: async result asserted too early

- Difficulty: Medium
- Framework: Spring Testing Slices
- Language: Java
- Perspective: Async tests
- Concept: async result asserted too early
- Symptom: The test is flaky or sees an empty response.
- Diagnostic goal: Wait for the async dispatch before asserting the final result.

### Buggy code

```java
mockMvc.perform(get("/report")).andExpect(status().isOk());
```

### Expected diagnosis

A controller returning a CompletableFuture requires async dispatch handling.

### Corrected code

```java
MvcResult result = mockMvc.perform(get("/report")).andReturn();
mockMvc.perform(asyncDispatch(result)).andExpect(status().isOk());
```

### Regression tests

```java
// The test waits for completion deterministically.
```

## TEST-M-100: test bean overridden by production bean

- Difficulty: Medium
- Framework: Spring Testing Slices
- Language: Java
- Perspective: Profiles
- Concept: test bean overridden by production bean
- Symptom: A test double is ignored.
- Diagnostic goal: Use profile or primary/qualifier rules deliberately.

### Buggy code

```java
@ActiveProfiles("test")
class ServiceTest {}
```

### Expected diagnosis

The test profile alone does not replace a production bean with the same role.

### Corrected code

```java
@TestConfiguration
static class Doubles { @Bean @Primary PaymentGateway gateway() { return new FakeGateway(); } }
```

### Regression tests

```java
// The test resolves the fake gateway and production behavior is isolated.
```

## TEST-H-001: repository missing in @WebMvcTest

- Difficulty: Hard
- Framework: Spring Testing Slices
- Language: Java
- Perspective: Web slice
- Concept: repository missing in @WebMvcTest
- Symptom: The controller test context cannot start.
- Diagnostic goal: Mock only collaborators outside the selected slice.

### Buggy code

```java
@WebMvcTest(ItemController.class)
class ItemTest { @Autowired ItemRepository repository; }
```

### Expected diagnosis

@WebMvcTest excludes repositories and services by design.

### Corrected code

```java
@WebMvcTest(ItemController.class)
class ItemTest { @MockBean ItemService service; }
```

### Regression tests

```java
// The MVC slice starts and the controller uses the mocked service.
```

## TEST-H-002: security filter breaks repository test

- Difficulty: Hard
- Framework: Spring Testing Slices
- Language: Java
- Perspective: Data slice
- Concept: security filter breaks repository test
- Symptom: A @DataJpaTest request unexpectedly requires authentication.
- Diagnostic goal: Keep slice scope clear and import only needed configuration.

### Buggy code

```java
@DataJpaTest
class ItemRepositoryTest {}
```

### Expected diagnosis

Importing the full application security configuration changes a focused persistence test.

### Corrected code

```java
@DataJpaTest
@Import(TestDatabaseConfig.class)
class ItemRepositoryTest {}
```

### Regression tests

```java
// The test uses the slice database without loading web security.
```

## TEST-H-003: missing csrf token

- Difficulty: Hard
- Framework: Spring Testing Slices
- Language: Java
- Perspective: MockMvc
- Concept: missing csrf token
- Symptom: A POST test receives 403 unexpectedly.
- Diagnostic goal: Include the security test request post processor.

### Buggy code

```java
mockMvc.perform(post("/items").content(json));
```

### Expected diagnosis

CSRF protection correctly rejects a state-changing request without a token.

### Corrected code

```java
mockMvc.perform(post("/items").with(csrf()).contentType(APPLICATION_JSON).content(json));
```

### Regression tests

```java
// The valid authenticated request passes CSRF and reaches the controller.
```

## TEST-H-004: wrong test configuration

- Difficulty: Hard
- Framework: Spring Testing Slices
- Language: Java
- Perspective: Context bootstrap
- Concept: wrong test configuration
- Symptom: The test starts the wrong application context.
- Diagnostic goal: Load the test configuration that supplies its collaborators.

### Buggy code

```java
@ContextConfiguration(classes = ProductionConfig.class)
class Test {}
```

### Expected diagnosis

A focused test should load the test configuration that supplies its collaborators.

### Corrected code

```java
@ContextConfiguration(classes = TestConfig.class)
class Test {}
```

### Regression tests

```java
// The context contains test doubles and no production connections.
```

## TEST-H-005: mock returns null default

- Difficulty: Hard
- Framework: Spring Testing Slices
- Language: Java
- Perspective: Mocking
- Concept: mock returns null default
- Symptom: The controller throws while the test expects a response.
- Diagnostic goal: Stub the collaborator path that the handler actually uses.

### Buggy code

```java
when(service.find(1L)).thenReturn(null);
```

### Expected diagnosis

Mockito returns null unless the test configures the expected value, so DTO mapping fails.

### Corrected code

```java
when(service.find(1L)).thenReturn(Optional.of(item));
```

### Regression tests

```java
// The success path receives the expected domain object.
```

## TEST-H-006: test rollback assumption

- Difficulty: Hard
- Framework: Spring Testing Slices
- Language: Java
- Perspective: Transactions
- Concept: test rollback assumption
- Symptom: Data leaks between tests.
- Diagnostic goal: Use transactional rollback or clean the database explicitly.

### Buggy code

```java
@SpringBootTest
class ItemTest { @Test void creates() { repository.save(item); } }
```

### Expected diagnosis

A full integration test does not automatically roll back unless a transaction is active for the test.

### Corrected code

```java
@SpringBootTest
@Transactional
class ItemTest { ... }
```

### Regression tests

```java
// Each test starts with a clean database state.
```

## TEST-H-007: container not ready

- Difficulty: Hard
- Framework: Spring Testing Slices
- Language: Java
- Perspective: Test containers
- Concept: container not ready
- Symptom: Integration tests race database startup.
- Diagnostic goal: Use the container lifecycle and dynamic property registration.

### Buggy code

```java
static PostgreSQLContainer<?> db = new PostgreSQLContainer<>("postgres:16");
```

### Expected diagnosis

Creating a container is insufficient if it is not started and its properties are not bound.

### Corrected code

```java
@Container static PostgreSQLContainer<?> db = new PostgreSQLContainer<>("postgres:16");
@DynamicPropertySource static void props(DynamicPropertyRegistry r) { r.add("spring.datasource.url", db::getJdbcUrl); }
```

### Regression tests

```java
// The application datasource points at the running container.
```

## TEST-H-008: only status asserted

- Difficulty: Hard
- Framework: Spring Testing Slices
- Language: Java
- Perspective: Assertions
- Concept: only status asserted
- Symptom: A regression changes the response body unnoticed.
- Diagnostic goal: Assert status, headers, and meaningful payload fields.

### Buggy code

```java
mockMvc.perform(get("/items/1")).andExpect(status().isOk());
```

### Expected diagnosis

A 200 response can still contain the wrong representation.

### Corrected code

```java
mockMvc.perform(get("/items/1")).andExpect(status().isOk()).andExpect(jsonPath("$.id").value(1));
```

### Regression tests

```java
// The contract test fails when the id or JSON shape changes.
```

## TEST-H-009: async result asserted too early

- Difficulty: Hard
- Framework: Spring Testing Slices
- Language: Java
- Perspective: Async tests
- Concept: async result asserted too early
- Symptom: The test is flaky or sees an empty response.
- Diagnostic goal: Wait for the async dispatch before asserting the final result.

### Buggy code

```java
mockMvc.perform(get("/report")).andExpect(status().isOk());
```

### Expected diagnosis

A controller returning a CompletableFuture requires async dispatch handling.

### Corrected code

```java
MvcResult result = mockMvc.perform(get("/report")).andReturn();
mockMvc.perform(asyncDispatch(result)).andExpect(status().isOk());
```

### Regression tests

```java
// The test waits for completion deterministically.
```

## TEST-H-010: test bean overridden by production bean

- Difficulty: Hard
- Framework: Spring Testing Slices
- Language: Java
- Perspective: Profiles
- Concept: test bean overridden by production bean
- Symptom: A test double is ignored.
- Diagnostic goal: Use profile or primary/qualifier rules deliberately.

### Buggy code

```java
@ActiveProfiles("test")
class ServiceTest {}
```

### Expected diagnosis

The test profile alone does not replace a production bean with the same role.

### Corrected code

```java
@TestConfiguration
static class Doubles { @Bean @Primary PaymentGateway gateway() { return new FakeGateway(); } }
```

### Regression tests

```java
// The test resolves the fake gateway and production behavior is isolated.
```

## TEST-H-011: repository missing in @WebMvcTest

- Difficulty: Hard
- Framework: Spring Testing Slices
- Language: Java
- Perspective: Web slice
- Concept: repository missing in @WebMvcTest
- Symptom: The controller test context cannot start.
- Diagnostic goal: Mock only collaborators outside the selected slice.

### Buggy code

```java
@WebMvcTest(ItemController.class)
class ItemTest { @Autowired ItemRepository repository; }
```

### Expected diagnosis

@WebMvcTest excludes repositories and services by design.

### Corrected code

```java
@WebMvcTest(ItemController.class)
class ItemTest { @MockBean ItemService service; }
```

### Regression tests

```java
// The MVC slice starts and the controller uses the mocked service.
```

## TEST-H-012: security filter breaks repository test

- Difficulty: Hard
- Framework: Spring Testing Slices
- Language: Java
- Perspective: Data slice
- Concept: security filter breaks repository test
- Symptom: A @DataJpaTest request unexpectedly requires authentication.
- Diagnostic goal: Keep slice scope clear and import only needed configuration.

### Buggy code

```java
@DataJpaTest
class ItemRepositoryTest {}
```

### Expected diagnosis

Importing the full application security configuration changes a focused persistence test.

### Corrected code

```java
@DataJpaTest
@Import(TestDatabaseConfig.class)
class ItemRepositoryTest {}
```

### Regression tests

```java
// The test uses the slice database without loading web security.
```

## TEST-H-013: missing csrf token

- Difficulty: Hard
- Framework: Spring Testing Slices
- Language: Java
- Perspective: MockMvc
- Concept: missing csrf token
- Symptom: A POST test receives 403 unexpectedly.
- Diagnostic goal: Include the security test request post processor.

### Buggy code

```java
mockMvc.perform(post("/items").content(json));
```

### Expected diagnosis

CSRF protection correctly rejects a state-changing request without a token.

### Corrected code

```java
mockMvc.perform(post("/items").with(csrf()).contentType(APPLICATION_JSON).content(json));
```

### Regression tests

```java
// The valid authenticated request passes CSRF and reaches the controller.
```

## TEST-H-014: wrong test configuration

- Difficulty: Hard
- Framework: Spring Testing Slices
- Language: Java
- Perspective: Context bootstrap
- Concept: wrong test configuration
- Symptom: The test starts the wrong application context.
- Diagnostic goal: Load the test configuration that supplies its collaborators.

### Buggy code

```java
@ContextConfiguration(classes = ProductionConfig.class)
class Test {}
```

### Expected diagnosis

A focused test should load the test configuration that supplies its collaborators.

### Corrected code

```java
@ContextConfiguration(classes = TestConfig.class)
class Test {}
```

### Regression tests

```java
// The context contains test doubles and no production connections.
```

## TEST-H-015: mock returns null default

- Difficulty: Hard
- Framework: Spring Testing Slices
- Language: Java
- Perspective: Mocking
- Concept: mock returns null default
- Symptom: The controller throws while the test expects a response.
- Diagnostic goal: Stub the collaborator path that the handler actually uses.

### Buggy code

```java
when(service.find(1L)).thenReturn(null);
```

### Expected diagnosis

Mockito returns null unless the test configures the expected value, so DTO mapping fails.

### Corrected code

```java
when(service.find(1L)).thenReturn(Optional.of(item));
```

### Regression tests

```java
// The success path receives the expected domain object.
```

## TEST-H-016: test rollback assumption

- Difficulty: Hard
- Framework: Spring Testing Slices
- Language: Java
- Perspective: Transactions
- Concept: test rollback assumption
- Symptom: Data leaks between tests.
- Diagnostic goal: Use transactional rollback or clean the database explicitly.

### Buggy code

```java
@SpringBootTest
class ItemTest { @Test void creates() { repository.save(item); } }
```

### Expected diagnosis

A full integration test does not automatically roll back unless a transaction is active for the test.

### Corrected code

```java
@SpringBootTest
@Transactional
class ItemTest { ... }
```

### Regression tests

```java
// Each test starts with a clean database state.
```

## TEST-H-017: container not ready

- Difficulty: Hard
- Framework: Spring Testing Slices
- Language: Java
- Perspective: Test containers
- Concept: container not ready
- Symptom: Integration tests race database startup.
- Diagnostic goal: Use the container lifecycle and dynamic property registration.

### Buggy code

```java
static PostgreSQLContainer<?> db = new PostgreSQLContainer<>("postgres:16");
```

### Expected diagnosis

Creating a container is insufficient if it is not started and its properties are not bound.

### Corrected code

```java
@Container static PostgreSQLContainer<?> db = new PostgreSQLContainer<>("postgres:16");
@DynamicPropertySource static void props(DynamicPropertyRegistry r) { r.add("spring.datasource.url", db::getJdbcUrl); }
```

### Regression tests

```java
// The application datasource points at the running container.
```

## TEST-H-018: only status asserted

- Difficulty: Hard
- Framework: Spring Testing Slices
- Language: Java
- Perspective: Assertions
- Concept: only status asserted
- Symptom: A regression changes the response body unnoticed.
- Diagnostic goal: Assert status, headers, and meaningful payload fields.

### Buggy code

```java
mockMvc.perform(get("/items/1")).andExpect(status().isOk());
```

### Expected diagnosis

A 200 response can still contain the wrong representation.

### Corrected code

```java
mockMvc.perform(get("/items/1")).andExpect(status().isOk()).andExpect(jsonPath("$.id").value(1));
```

### Regression tests

```java
// The contract test fails when the id or JSON shape changes.
```

## TEST-H-019: async result asserted too early

- Difficulty: Hard
- Framework: Spring Testing Slices
- Language: Java
- Perspective: Async tests
- Concept: async result asserted too early
- Symptom: The test is flaky or sees an empty response.
- Diagnostic goal: Wait for the async dispatch before asserting the final result.

### Buggy code

```java
mockMvc.perform(get("/report")).andExpect(status().isOk());
```

### Expected diagnosis

A controller returning a CompletableFuture requires async dispatch handling.

### Corrected code

```java
MvcResult result = mockMvc.perform(get("/report")).andReturn();
mockMvc.perform(asyncDispatch(result)).andExpect(status().isOk());
```

### Regression tests

```java
// The test waits for completion deterministically.
```

## TEST-H-020: test bean overridden by production bean

- Difficulty: Hard
- Framework: Spring Testing Slices
- Language: Java
- Perspective: Profiles
- Concept: test bean overridden by production bean
- Symptom: A test double is ignored.
- Diagnostic goal: Use profile or primary/qualifier rules deliberately.

### Buggy code

```java
@ActiveProfiles("test")
class ServiceTest {}
```

### Expected diagnosis

The test profile alone does not replace a production bean with the same role.

### Corrected code

```java
@TestConfiguration
static class Doubles { @Bean @Primary PaymentGateway gateway() { return new FakeGateway(); } }
```

### Regression tests

```java
// The test resolves the fake gateway and production behavior is isolated.
```

## TEST-H-021: repository missing in @WebMvcTest

- Difficulty: Hard
- Framework: Spring Testing Slices
- Language: Java
- Perspective: Web slice
- Concept: repository missing in @WebMvcTest
- Symptom: The controller test context cannot start.
- Diagnostic goal: Mock only collaborators outside the selected slice.

### Buggy code

```java
@WebMvcTest(ItemController.class)
class ItemTest { @Autowired ItemRepository repository; }
```

### Expected diagnosis

@WebMvcTest excludes repositories and services by design.

### Corrected code

```java
@WebMvcTest(ItemController.class)
class ItemTest { @MockBean ItemService service; }
```

### Regression tests

```java
// The MVC slice starts and the controller uses the mocked service.
```

## TEST-H-022: security filter breaks repository test

- Difficulty: Hard
- Framework: Spring Testing Slices
- Language: Java
- Perspective: Data slice
- Concept: security filter breaks repository test
- Symptom: A @DataJpaTest request unexpectedly requires authentication.
- Diagnostic goal: Keep slice scope clear and import only needed configuration.

### Buggy code

```java
@DataJpaTest
class ItemRepositoryTest {}
```

### Expected diagnosis

Importing the full application security configuration changes a focused persistence test.

### Corrected code

```java
@DataJpaTest
@Import(TestDatabaseConfig.class)
class ItemRepositoryTest {}
```

### Regression tests

```java
// The test uses the slice database without loading web security.
```

## TEST-H-023: missing csrf token

- Difficulty: Hard
- Framework: Spring Testing Slices
- Language: Java
- Perspective: MockMvc
- Concept: missing csrf token
- Symptom: A POST test receives 403 unexpectedly.
- Diagnostic goal: Include the security test request post processor.

### Buggy code

```java
mockMvc.perform(post("/items").content(json));
```

### Expected diagnosis

CSRF protection correctly rejects a state-changing request without a token.

### Corrected code

```java
mockMvc.perform(post("/items").with(csrf()).contentType(APPLICATION_JSON).content(json));
```

### Regression tests

```java
// The valid authenticated request passes CSRF and reaches the controller.
```

## TEST-H-024: wrong test configuration

- Difficulty: Hard
- Framework: Spring Testing Slices
- Language: Java
- Perspective: Context bootstrap
- Concept: wrong test configuration
- Symptom: The test starts the wrong application context.
- Diagnostic goal: Load the test configuration that supplies its collaborators.

### Buggy code

```java
@ContextConfiguration(classes = ProductionConfig.class)
class Test {}
```

### Expected diagnosis

A focused test should load the test configuration that supplies its collaborators.

### Corrected code

```java
@ContextConfiguration(classes = TestConfig.class)
class Test {}
```

### Regression tests

```java
// The context contains test doubles and no production connections.
```

## TEST-H-025: mock returns null default

- Difficulty: Hard
- Framework: Spring Testing Slices
- Language: Java
- Perspective: Mocking
- Concept: mock returns null default
- Symptom: The controller throws while the test expects a response.
- Diagnostic goal: Stub the collaborator path that the handler actually uses.

### Buggy code

```java
when(service.find(1L)).thenReturn(null);
```

### Expected diagnosis

Mockito returns null unless the test configures the expected value, so DTO mapping fails.

### Corrected code

```java
when(service.find(1L)).thenReturn(Optional.of(item));
```

### Regression tests

```java
// The success path receives the expected domain object.
```

## TEST-H-026: test rollback assumption

- Difficulty: Hard
- Framework: Spring Testing Slices
- Language: Java
- Perspective: Transactions
- Concept: test rollback assumption
- Symptom: Data leaks between tests.
- Diagnostic goal: Use transactional rollback or clean the database explicitly.

### Buggy code

```java
@SpringBootTest
class ItemTest { @Test void creates() { repository.save(item); } }
```

### Expected diagnosis

A full integration test does not automatically roll back unless a transaction is active for the test.

### Corrected code

```java
@SpringBootTest
@Transactional
class ItemTest { ... }
```

### Regression tests

```java
// Each test starts with a clean database state.
```

## TEST-H-027: container not ready

- Difficulty: Hard
- Framework: Spring Testing Slices
- Language: Java
- Perspective: Test containers
- Concept: container not ready
- Symptom: Integration tests race database startup.
- Diagnostic goal: Use the container lifecycle and dynamic property registration.

### Buggy code

```java
static PostgreSQLContainer<?> db = new PostgreSQLContainer<>("postgres:16");
```

### Expected diagnosis

Creating a container is insufficient if it is not started and its properties are not bound.

### Corrected code

```java
@Container static PostgreSQLContainer<?> db = new PostgreSQLContainer<>("postgres:16");
@DynamicPropertySource static void props(DynamicPropertyRegistry r) { r.add("spring.datasource.url", db::getJdbcUrl); }
```

### Regression tests

```java
// The application datasource points at the running container.
```

## TEST-H-028: only status asserted

- Difficulty: Hard
- Framework: Spring Testing Slices
- Language: Java
- Perspective: Assertions
- Concept: only status asserted
- Symptom: A regression changes the response body unnoticed.
- Diagnostic goal: Assert status, headers, and meaningful payload fields.

### Buggy code

```java
mockMvc.perform(get("/items/1")).andExpect(status().isOk());
```

### Expected diagnosis

A 200 response can still contain the wrong representation.

### Corrected code

```java
mockMvc.perform(get("/items/1")).andExpect(status().isOk()).andExpect(jsonPath("$.id").value(1));
```

### Regression tests

```java
// The contract test fails when the id or JSON shape changes.
```

## TEST-H-029: async result asserted too early

- Difficulty: Hard
- Framework: Spring Testing Slices
- Language: Java
- Perspective: Async tests
- Concept: async result asserted too early
- Symptom: The test is flaky or sees an empty response.
- Diagnostic goal: Wait for the async dispatch before asserting the final result.

### Buggy code

```java
mockMvc.perform(get("/report")).andExpect(status().isOk());
```

### Expected diagnosis

A controller returning a CompletableFuture requires async dispatch handling.

### Corrected code

```java
MvcResult result = mockMvc.perform(get("/report")).andReturn();
mockMvc.perform(asyncDispatch(result)).andExpect(status().isOk());
```

### Regression tests

```java
// The test waits for completion deterministically.
```

## TEST-H-030: test bean overridden by production bean

- Difficulty: Hard
- Framework: Spring Testing Slices
- Language: Java
- Perspective: Profiles
- Concept: test bean overridden by production bean
- Symptom: A test double is ignored.
- Diagnostic goal: Use profile or primary/qualifier rules deliberately.

### Buggy code

```java
@ActiveProfiles("test")
class ServiceTest {}
```

### Expected diagnosis

The test profile alone does not replace a production bean with the same role.

### Corrected code

```java
@TestConfiguration
static class Doubles { @Bean @Primary PaymentGateway gateway() { return new FakeGateway(); } }
```

### Regression tests

```java
// The test resolves the fake gateway and production behavior is isolated.
```

## TEST-H-031: repository missing in @WebMvcTest

- Difficulty: Hard
- Framework: Spring Testing Slices
- Language: Java
- Perspective: Web slice
- Concept: repository missing in @WebMvcTest
- Symptom: The controller test context cannot start.
- Diagnostic goal: Mock only collaborators outside the selected slice.

### Buggy code

```java
@WebMvcTest(ItemController.class)
class ItemTest { @Autowired ItemRepository repository; }
```

### Expected diagnosis

@WebMvcTest excludes repositories and services by design.

### Corrected code

```java
@WebMvcTest(ItemController.class)
class ItemTest { @MockBean ItemService service; }
```

### Regression tests

```java
// The MVC slice starts and the controller uses the mocked service.
```

## TEST-H-032: security filter breaks repository test

- Difficulty: Hard
- Framework: Spring Testing Slices
- Language: Java
- Perspective: Data slice
- Concept: security filter breaks repository test
- Symptom: A @DataJpaTest request unexpectedly requires authentication.
- Diagnostic goal: Keep slice scope clear and import only needed configuration.

### Buggy code

```java
@DataJpaTest
class ItemRepositoryTest {}
```

### Expected diagnosis

Importing the full application security configuration changes a focused persistence test.

### Corrected code

```java
@DataJpaTest
@Import(TestDatabaseConfig.class)
class ItemRepositoryTest {}
```

### Regression tests

```java
// The test uses the slice database without loading web security.
```

## TEST-H-033: missing csrf token

- Difficulty: Hard
- Framework: Spring Testing Slices
- Language: Java
- Perspective: MockMvc
- Concept: missing csrf token
- Symptom: A POST test receives 403 unexpectedly.
- Diagnostic goal: Include the security test request post processor.

### Buggy code

```java
mockMvc.perform(post("/items").content(json));
```

### Expected diagnosis

CSRF protection correctly rejects a state-changing request without a token.

### Corrected code

```java
mockMvc.perform(post("/items").with(csrf()).contentType(APPLICATION_JSON).content(json));
```

### Regression tests

```java
// The valid authenticated request passes CSRF and reaches the controller.
```

## TEST-H-034: wrong test configuration

- Difficulty: Hard
- Framework: Spring Testing Slices
- Language: Java
- Perspective: Context bootstrap
- Concept: wrong test configuration
- Symptom: The test starts the wrong application context.
- Diagnostic goal: Load the test configuration that supplies its collaborators.

### Buggy code

```java
@ContextConfiguration(classes = ProductionConfig.class)
class Test {}
```

### Expected diagnosis

A focused test should load the test configuration that supplies its collaborators.

### Corrected code

```java
@ContextConfiguration(classes = TestConfig.class)
class Test {}
```

### Regression tests

```java
// The context contains test doubles and no production connections.
```

## TEST-H-035: mock returns null default

- Difficulty: Hard
- Framework: Spring Testing Slices
- Language: Java
- Perspective: Mocking
- Concept: mock returns null default
- Symptom: The controller throws while the test expects a response.
- Diagnostic goal: Stub the collaborator path that the handler actually uses.

### Buggy code

```java
when(service.find(1L)).thenReturn(null);
```

### Expected diagnosis

Mockito returns null unless the test configures the expected value, so DTO mapping fails.

### Corrected code

```java
when(service.find(1L)).thenReturn(Optional.of(item));
```

### Regression tests

```java
// The success path receives the expected domain object.
```

## TEST-H-036: test rollback assumption

- Difficulty: Hard
- Framework: Spring Testing Slices
- Language: Java
- Perspective: Transactions
- Concept: test rollback assumption
- Symptom: Data leaks between tests.
- Diagnostic goal: Use transactional rollback or clean the database explicitly.

### Buggy code

```java
@SpringBootTest
class ItemTest { @Test void creates() { repository.save(item); } }
```

### Expected diagnosis

A full integration test does not automatically roll back unless a transaction is active for the test.

### Corrected code

```java
@SpringBootTest
@Transactional
class ItemTest { ... }
```

### Regression tests

```java
// Each test starts with a clean database state.
```

## TEST-H-037: container not ready

- Difficulty: Hard
- Framework: Spring Testing Slices
- Language: Java
- Perspective: Test containers
- Concept: container not ready
- Symptom: Integration tests race database startup.
- Diagnostic goal: Use the container lifecycle and dynamic property registration.

### Buggy code

```java
static PostgreSQLContainer<?> db = new PostgreSQLContainer<>("postgres:16");
```

### Expected diagnosis

Creating a container is insufficient if it is not started and its properties are not bound.

### Corrected code

```java
@Container static PostgreSQLContainer<?> db = new PostgreSQLContainer<>("postgres:16");
@DynamicPropertySource static void props(DynamicPropertyRegistry r) { r.add("spring.datasource.url", db::getJdbcUrl); }
```

### Regression tests

```java
// The application datasource points at the running container.
```

## TEST-H-038: only status asserted

- Difficulty: Hard
- Framework: Spring Testing Slices
- Language: Java
- Perspective: Assertions
- Concept: only status asserted
- Symptom: A regression changes the response body unnoticed.
- Diagnostic goal: Assert status, headers, and meaningful payload fields.

### Buggy code

```java
mockMvc.perform(get("/items/1")).andExpect(status().isOk());
```

### Expected diagnosis

A 200 response can still contain the wrong representation.

### Corrected code

```java
mockMvc.perform(get("/items/1")).andExpect(status().isOk()).andExpect(jsonPath("$.id").value(1));
```

### Regression tests

```java
// The contract test fails when the id or JSON shape changes.
```

## TEST-H-039: async result asserted too early

- Difficulty: Hard
- Framework: Spring Testing Slices
- Language: Java
- Perspective: Async tests
- Concept: async result asserted too early
- Symptom: The test is flaky or sees an empty response.
- Diagnostic goal: Wait for the async dispatch before asserting the final result.

### Buggy code

```java
mockMvc.perform(get("/report")).andExpect(status().isOk());
```

### Expected diagnosis

A controller returning a CompletableFuture requires async dispatch handling.

### Corrected code

```java
MvcResult result = mockMvc.perform(get("/report")).andReturn();
mockMvc.perform(asyncDispatch(result)).andExpect(status().isOk());
```

### Regression tests

```java
// The test waits for completion deterministically.
```

## TEST-H-040: test bean overridden by production bean

- Difficulty: Hard
- Framework: Spring Testing Slices
- Language: Java
- Perspective: Profiles
- Concept: test bean overridden by production bean
- Symptom: A test double is ignored.
- Diagnostic goal: Use profile or primary/qualifier rules deliberately.

### Buggy code

```java
@ActiveProfiles("test")
class ServiceTest {}
```

### Expected diagnosis

The test profile alone does not replace a production bean with the same role.

### Corrected code

```java
@TestConfiguration
static class Doubles { @Bean @Primary PaymentGateway gateway() { return new FakeGateway(); } }
```

### Regression tests

```java
// The test resolves the fake gateway and production behavior is isolated.
```

## TEST-H-041: repository missing in @WebMvcTest

- Difficulty: Hard
- Framework: Spring Testing Slices
- Language: Java
- Perspective: Web slice
- Concept: repository missing in @WebMvcTest
- Symptom: The controller test context cannot start.
- Diagnostic goal: Mock only collaborators outside the selected slice.

### Buggy code

```java
@WebMvcTest(ItemController.class)
class ItemTest { @Autowired ItemRepository repository; }
```

### Expected diagnosis

@WebMvcTest excludes repositories and services by design.

### Corrected code

```java
@WebMvcTest(ItemController.class)
class ItemTest { @MockBean ItemService service; }
```

### Regression tests

```java
// The MVC slice starts and the controller uses the mocked service.
```

## TEST-H-042: security filter breaks repository test

- Difficulty: Hard
- Framework: Spring Testing Slices
- Language: Java
- Perspective: Data slice
- Concept: security filter breaks repository test
- Symptom: A @DataJpaTest request unexpectedly requires authentication.
- Diagnostic goal: Keep slice scope clear and import only needed configuration.

### Buggy code

```java
@DataJpaTest
class ItemRepositoryTest {}
```

### Expected diagnosis

Importing the full application security configuration changes a focused persistence test.

### Corrected code

```java
@DataJpaTest
@Import(TestDatabaseConfig.class)
class ItemRepositoryTest {}
```

### Regression tests

```java
// The test uses the slice database without loading web security.
```

## TEST-H-043: missing csrf token

- Difficulty: Hard
- Framework: Spring Testing Slices
- Language: Java
- Perspective: MockMvc
- Concept: missing csrf token
- Symptom: A POST test receives 403 unexpectedly.
- Diagnostic goal: Include the security test request post processor.

### Buggy code

```java
mockMvc.perform(post("/items").content(json));
```

### Expected diagnosis

CSRF protection correctly rejects a state-changing request without a token.

### Corrected code

```java
mockMvc.perform(post("/items").with(csrf()).contentType(APPLICATION_JSON).content(json));
```

### Regression tests

```java
// The valid authenticated request passes CSRF and reaches the controller.
```

## TEST-H-044: wrong test configuration

- Difficulty: Hard
- Framework: Spring Testing Slices
- Language: Java
- Perspective: Context bootstrap
- Concept: wrong test configuration
- Symptom: The test starts the wrong application context.
- Diagnostic goal: Load the test configuration that supplies its collaborators.

### Buggy code

```java
@ContextConfiguration(classes = ProductionConfig.class)
class Test {}
```

### Expected diagnosis

A focused test should load the test configuration that supplies its collaborators.

### Corrected code

```java
@ContextConfiguration(classes = TestConfig.class)
class Test {}
```

### Regression tests

```java
// The context contains test doubles and no production connections.
```

## TEST-H-045: mock returns null default

- Difficulty: Hard
- Framework: Spring Testing Slices
- Language: Java
- Perspective: Mocking
- Concept: mock returns null default
- Symptom: The controller throws while the test expects a response.
- Diagnostic goal: Stub the collaborator path that the handler actually uses.

### Buggy code

```java
when(service.find(1L)).thenReturn(null);
```

### Expected diagnosis

Mockito returns null unless the test configures the expected value, so DTO mapping fails.

### Corrected code

```java
when(service.find(1L)).thenReturn(Optional.of(item));
```

### Regression tests

```java
// The success path receives the expected domain object.
```

## TEST-H-046: test rollback assumption

- Difficulty: Hard
- Framework: Spring Testing Slices
- Language: Java
- Perspective: Transactions
- Concept: test rollback assumption
- Symptom: Data leaks between tests.
- Diagnostic goal: Use transactional rollback or clean the database explicitly.

### Buggy code

```java
@SpringBootTest
class ItemTest { @Test void creates() { repository.save(item); } }
```

### Expected diagnosis

A full integration test does not automatically roll back unless a transaction is active for the test.

### Corrected code

```java
@SpringBootTest
@Transactional
class ItemTest { ... }
```

### Regression tests

```java
// Each test starts with a clean database state.
```

## TEST-H-047: container not ready

- Difficulty: Hard
- Framework: Spring Testing Slices
- Language: Java
- Perspective: Test containers
- Concept: container not ready
- Symptom: Integration tests race database startup.
- Diagnostic goal: Use the container lifecycle and dynamic property registration.

### Buggy code

```java
static PostgreSQLContainer<?> db = new PostgreSQLContainer<>("postgres:16");
```

### Expected diagnosis

Creating a container is insufficient if it is not started and its properties are not bound.

### Corrected code

```java
@Container static PostgreSQLContainer<?> db = new PostgreSQLContainer<>("postgres:16");
@DynamicPropertySource static void props(DynamicPropertyRegistry r) { r.add("spring.datasource.url", db::getJdbcUrl); }
```

### Regression tests

```java
// The application datasource points at the running container.
```

## TEST-H-048: only status asserted

- Difficulty: Hard
- Framework: Spring Testing Slices
- Language: Java
- Perspective: Assertions
- Concept: only status asserted
- Symptom: A regression changes the response body unnoticed.
- Diagnostic goal: Assert status, headers, and meaningful payload fields.

### Buggy code

```java
mockMvc.perform(get("/items/1")).andExpect(status().isOk());
```

### Expected diagnosis

A 200 response can still contain the wrong representation.

### Corrected code

```java
mockMvc.perform(get("/items/1")).andExpect(status().isOk()).andExpect(jsonPath("$.id").value(1));
```

### Regression tests

```java
// The contract test fails when the id or JSON shape changes.
```

## TEST-H-049: async result asserted too early

- Difficulty: Hard
- Framework: Spring Testing Slices
- Language: Java
- Perspective: Async tests
- Concept: async result asserted too early
- Symptom: The test is flaky or sees an empty response.
- Diagnostic goal: Wait for the async dispatch before asserting the final result.

### Buggy code

```java
mockMvc.perform(get("/report")).andExpect(status().isOk());
```

### Expected diagnosis

A controller returning a CompletableFuture requires async dispatch handling.

### Corrected code

```java
MvcResult result = mockMvc.perform(get("/report")).andReturn();
mockMvc.perform(asyncDispatch(result)).andExpect(status().isOk());
```

### Regression tests

```java
// The test waits for completion deterministically.
```

## TEST-H-050: test bean overridden by production bean

- Difficulty: Hard
- Framework: Spring Testing Slices
- Language: Java
- Perspective: Profiles
- Concept: test bean overridden by production bean
- Symptom: A test double is ignored.
- Diagnostic goal: Use profile or primary/qualifier rules deliberately.

### Buggy code

```java
@ActiveProfiles("test")
class ServiceTest {}
```

### Expected diagnosis

The test profile alone does not replace a production bean with the same role.

### Corrected code

```java
@TestConfiguration
static class Doubles { @Bean @Primary PaymentGateway gateway() { return new FakeGateway(); } }
```

### Regression tests

```java
// The test resolves the fake gateway and production behavior is isolated.
```

## TEST-H-051: repository missing in @WebMvcTest

- Difficulty: Hard
- Framework: Spring Testing Slices
- Language: Java
- Perspective: Web slice
- Concept: repository missing in @WebMvcTest
- Symptom: The controller test context cannot start.
- Diagnostic goal: Mock only collaborators outside the selected slice.

### Buggy code

```java
@WebMvcTest(ItemController.class)
class ItemTest { @Autowired ItemRepository repository; }
```

### Expected diagnosis

@WebMvcTest excludes repositories and services by design.

### Corrected code

```java
@WebMvcTest(ItemController.class)
class ItemTest { @MockBean ItemService service; }
```

### Regression tests

```java
// The MVC slice starts and the controller uses the mocked service.
```

## TEST-H-052: security filter breaks repository test

- Difficulty: Hard
- Framework: Spring Testing Slices
- Language: Java
- Perspective: Data slice
- Concept: security filter breaks repository test
- Symptom: A @DataJpaTest request unexpectedly requires authentication.
- Diagnostic goal: Keep slice scope clear and import only needed configuration.

### Buggy code

```java
@DataJpaTest
class ItemRepositoryTest {}
```

### Expected diagnosis

Importing the full application security configuration changes a focused persistence test.

### Corrected code

```java
@DataJpaTest
@Import(TestDatabaseConfig.class)
class ItemRepositoryTest {}
```

### Regression tests

```java
// The test uses the slice database without loading web security.
```

## TEST-H-053: missing csrf token

- Difficulty: Hard
- Framework: Spring Testing Slices
- Language: Java
- Perspective: MockMvc
- Concept: missing csrf token
- Symptom: A POST test receives 403 unexpectedly.
- Diagnostic goal: Include the security test request post processor.

### Buggy code

```java
mockMvc.perform(post("/items").content(json));
```

### Expected diagnosis

CSRF protection correctly rejects a state-changing request without a token.

### Corrected code

```java
mockMvc.perform(post("/items").with(csrf()).contentType(APPLICATION_JSON).content(json));
```

### Regression tests

```java
// The valid authenticated request passes CSRF and reaches the controller.
```

## TEST-H-054: wrong test configuration

- Difficulty: Hard
- Framework: Spring Testing Slices
- Language: Java
- Perspective: Context bootstrap
- Concept: wrong test configuration
- Symptom: The test starts the wrong application context.
- Diagnostic goal: Load the test configuration that supplies its collaborators.

### Buggy code

```java
@ContextConfiguration(classes = ProductionConfig.class)
class Test {}
```

### Expected diagnosis

A focused test should load the test configuration that supplies its collaborators.

### Corrected code

```java
@ContextConfiguration(classes = TestConfig.class)
class Test {}
```

### Regression tests

```java
// The context contains test doubles and no production connections.
```

## TEST-H-055: mock returns null default

- Difficulty: Hard
- Framework: Spring Testing Slices
- Language: Java
- Perspective: Mocking
- Concept: mock returns null default
- Symptom: The controller throws while the test expects a response.
- Diagnostic goal: Stub the collaborator path that the handler actually uses.

### Buggy code

```java
when(service.find(1L)).thenReturn(null);
```

### Expected diagnosis

Mockito returns null unless the test configures the expected value, so DTO mapping fails.

### Corrected code

```java
when(service.find(1L)).thenReturn(Optional.of(item));
```

### Regression tests

```java
// The success path receives the expected domain object.
```

## TEST-H-056: test rollback assumption

- Difficulty: Hard
- Framework: Spring Testing Slices
- Language: Java
- Perspective: Transactions
- Concept: test rollback assumption
- Symptom: Data leaks between tests.
- Diagnostic goal: Use transactional rollback or clean the database explicitly.

### Buggy code

```java
@SpringBootTest
class ItemTest { @Test void creates() { repository.save(item); } }
```

### Expected diagnosis

A full integration test does not automatically roll back unless a transaction is active for the test.

### Corrected code

```java
@SpringBootTest
@Transactional
class ItemTest { ... }
```

### Regression tests

```java
// Each test starts with a clean database state.
```

## TEST-H-057: container not ready

- Difficulty: Hard
- Framework: Spring Testing Slices
- Language: Java
- Perspective: Test containers
- Concept: container not ready
- Symptom: Integration tests race database startup.
- Diagnostic goal: Use the container lifecycle and dynamic property registration.

### Buggy code

```java
static PostgreSQLContainer<?> db = new PostgreSQLContainer<>("postgres:16");
```

### Expected diagnosis

Creating a container is insufficient if it is not started and its properties are not bound.

### Corrected code

```java
@Container static PostgreSQLContainer<?> db = new PostgreSQLContainer<>("postgres:16");
@DynamicPropertySource static void props(DynamicPropertyRegistry r) { r.add("spring.datasource.url", db::getJdbcUrl); }
```

### Regression tests

```java
// The application datasource points at the running container.
```

## TEST-H-058: only status asserted

- Difficulty: Hard
- Framework: Spring Testing Slices
- Language: Java
- Perspective: Assertions
- Concept: only status asserted
- Symptom: A regression changes the response body unnoticed.
- Diagnostic goal: Assert status, headers, and meaningful payload fields.

### Buggy code

```java
mockMvc.perform(get("/items/1")).andExpect(status().isOk());
```

### Expected diagnosis

A 200 response can still contain the wrong representation.

### Corrected code

```java
mockMvc.perform(get("/items/1")).andExpect(status().isOk()).andExpect(jsonPath("$.id").value(1));
```

### Regression tests

```java
// The contract test fails when the id or JSON shape changes.
```

## TEST-H-059: async result asserted too early

- Difficulty: Hard
- Framework: Spring Testing Slices
- Language: Java
- Perspective: Async tests
- Concept: async result asserted too early
- Symptom: The test is flaky or sees an empty response.
- Diagnostic goal: Wait for the async dispatch before asserting the final result.

### Buggy code

```java
mockMvc.perform(get("/report")).andExpect(status().isOk());
```

### Expected diagnosis

A controller returning a CompletableFuture requires async dispatch handling.

### Corrected code

```java
MvcResult result = mockMvc.perform(get("/report")).andReturn();
mockMvc.perform(asyncDispatch(result)).andExpect(status().isOk());
```

### Regression tests

```java
// The test waits for completion deterministically.
```

## TEST-H-060: test bean overridden by production bean

- Difficulty: Hard
- Framework: Spring Testing Slices
- Language: Java
- Perspective: Profiles
- Concept: test bean overridden by production bean
- Symptom: A test double is ignored.
- Diagnostic goal: Use profile or primary/qualifier rules deliberately.

### Buggy code

```java
@ActiveProfiles("test")
class ServiceTest {}
```

### Expected diagnosis

The test profile alone does not replace a production bean with the same role.

### Corrected code

```java
@TestConfiguration
static class Doubles { @Bean @Primary PaymentGateway gateway() { return new FakeGateway(); } }
```

### Regression tests

```java
// The test resolves the fake gateway and production behavior is isolated.
```

## TEST-H-061: repository missing in @WebMvcTest

- Difficulty: Hard
- Framework: Spring Testing Slices
- Language: Java
- Perspective: Web slice
- Concept: repository missing in @WebMvcTest
- Symptom: The controller test context cannot start.
- Diagnostic goal: Mock only collaborators outside the selected slice.

### Buggy code

```java
@WebMvcTest(ItemController.class)
class ItemTest { @Autowired ItemRepository repository; }
```

### Expected diagnosis

@WebMvcTest excludes repositories and services by design.

### Corrected code

```java
@WebMvcTest(ItemController.class)
class ItemTest { @MockBean ItemService service; }
```

### Regression tests

```java
// The MVC slice starts and the controller uses the mocked service.
```

## TEST-H-062: security filter breaks repository test

- Difficulty: Hard
- Framework: Spring Testing Slices
- Language: Java
- Perspective: Data slice
- Concept: security filter breaks repository test
- Symptom: A @DataJpaTest request unexpectedly requires authentication.
- Diagnostic goal: Keep slice scope clear and import only needed configuration.

### Buggy code

```java
@DataJpaTest
class ItemRepositoryTest {}
```

### Expected diagnosis

Importing the full application security configuration changes a focused persistence test.

### Corrected code

```java
@DataJpaTest
@Import(TestDatabaseConfig.class)
class ItemRepositoryTest {}
```

### Regression tests

```java
// The test uses the slice database without loading web security.
```

## TEST-H-063: missing csrf token

- Difficulty: Hard
- Framework: Spring Testing Slices
- Language: Java
- Perspective: MockMvc
- Concept: missing csrf token
- Symptom: A POST test receives 403 unexpectedly.
- Diagnostic goal: Include the security test request post processor.

### Buggy code

```java
mockMvc.perform(post("/items").content(json));
```

### Expected diagnosis

CSRF protection correctly rejects a state-changing request without a token.

### Corrected code

```java
mockMvc.perform(post("/items").with(csrf()).contentType(APPLICATION_JSON).content(json));
```

### Regression tests

```java
// The valid authenticated request passes CSRF and reaches the controller.
```

## TEST-H-064: wrong test configuration

- Difficulty: Hard
- Framework: Spring Testing Slices
- Language: Java
- Perspective: Context bootstrap
- Concept: wrong test configuration
- Symptom: The test starts the wrong application context.
- Diagnostic goal: Load the test configuration that supplies its collaborators.

### Buggy code

```java
@ContextConfiguration(classes = ProductionConfig.class)
class Test {}
```

### Expected diagnosis

A focused test should load the test configuration that supplies its collaborators.

### Corrected code

```java
@ContextConfiguration(classes = TestConfig.class)
class Test {}
```

### Regression tests

```java
// The context contains test doubles and no production connections.
```

## TEST-H-065: mock returns null default

- Difficulty: Hard
- Framework: Spring Testing Slices
- Language: Java
- Perspective: Mocking
- Concept: mock returns null default
- Symptom: The controller throws while the test expects a response.
- Diagnostic goal: Stub the collaborator path that the handler actually uses.

### Buggy code

```java
when(service.find(1L)).thenReturn(null);
```

### Expected diagnosis

Mockito returns null unless the test configures the expected value, so DTO mapping fails.

### Corrected code

```java
when(service.find(1L)).thenReturn(Optional.of(item));
```

### Regression tests

```java
// The success path receives the expected domain object.
```

## TEST-H-066: test rollback assumption

- Difficulty: Hard
- Framework: Spring Testing Slices
- Language: Java
- Perspective: Transactions
- Concept: test rollback assumption
- Symptom: Data leaks between tests.
- Diagnostic goal: Use transactional rollback or clean the database explicitly.

### Buggy code

```java
@SpringBootTest
class ItemTest { @Test void creates() { repository.save(item); } }
```

### Expected diagnosis

A full integration test does not automatically roll back unless a transaction is active for the test.

### Corrected code

```java
@SpringBootTest
@Transactional
class ItemTest { ... }
```

### Regression tests

```java
// Each test starts with a clean database state.
```

## TEST-H-067: container not ready

- Difficulty: Hard
- Framework: Spring Testing Slices
- Language: Java
- Perspective: Test containers
- Concept: container not ready
- Symptom: Integration tests race database startup.
- Diagnostic goal: Use the container lifecycle and dynamic property registration.

### Buggy code

```java
static PostgreSQLContainer<?> db = new PostgreSQLContainer<>("postgres:16");
```

### Expected diagnosis

Creating a container is insufficient if it is not started and its properties are not bound.

### Corrected code

```java
@Container static PostgreSQLContainer<?> db = new PostgreSQLContainer<>("postgres:16");
@DynamicPropertySource static void props(DynamicPropertyRegistry r) { r.add("spring.datasource.url", db::getJdbcUrl); }
```

### Regression tests

```java
// The application datasource points at the running container.
```

## TEST-H-068: only status asserted

- Difficulty: Hard
- Framework: Spring Testing Slices
- Language: Java
- Perspective: Assertions
- Concept: only status asserted
- Symptom: A regression changes the response body unnoticed.
- Diagnostic goal: Assert status, headers, and meaningful payload fields.

### Buggy code

```java
mockMvc.perform(get("/items/1")).andExpect(status().isOk());
```

### Expected diagnosis

A 200 response can still contain the wrong representation.

### Corrected code

```java
mockMvc.perform(get("/items/1")).andExpect(status().isOk()).andExpect(jsonPath("$.id").value(1));
```

### Regression tests

```java
// The contract test fails when the id or JSON shape changes.
```

## TEST-H-069: async result asserted too early

- Difficulty: Hard
- Framework: Spring Testing Slices
- Language: Java
- Perspective: Async tests
- Concept: async result asserted too early
- Symptom: The test is flaky or sees an empty response.
- Diagnostic goal: Wait for the async dispatch before asserting the final result.

### Buggy code

```java
mockMvc.perform(get("/report")).andExpect(status().isOk());
```

### Expected diagnosis

A controller returning a CompletableFuture requires async dispatch handling.

### Corrected code

```java
MvcResult result = mockMvc.perform(get("/report")).andReturn();
mockMvc.perform(asyncDispatch(result)).andExpect(status().isOk());
```

### Regression tests

```java
// The test waits for completion deterministically.
```

## TEST-H-070: test bean overridden by production bean

- Difficulty: Hard
- Framework: Spring Testing Slices
- Language: Java
- Perspective: Profiles
- Concept: test bean overridden by production bean
- Symptom: A test double is ignored.
- Diagnostic goal: Use profile or primary/qualifier rules deliberately.

### Buggy code

```java
@ActiveProfiles("test")
class ServiceTest {}
```

### Expected diagnosis

The test profile alone does not replace a production bean with the same role.

### Corrected code

```java
@TestConfiguration
static class Doubles { @Bean @Primary PaymentGateway gateway() { return new FakeGateway(); } }
```

### Regression tests

```java
// The test resolves the fake gateway and production behavior is isolated.
```

## TEST-H-071: repository missing in @WebMvcTest

- Difficulty: Hard
- Framework: Spring Testing Slices
- Language: Java
- Perspective: Web slice
- Concept: repository missing in @WebMvcTest
- Symptom: The controller test context cannot start.
- Diagnostic goal: Mock only collaborators outside the selected slice.

### Buggy code

```java
@WebMvcTest(ItemController.class)
class ItemTest { @Autowired ItemRepository repository; }
```

### Expected diagnosis

@WebMvcTest excludes repositories and services by design.

### Corrected code

```java
@WebMvcTest(ItemController.class)
class ItemTest { @MockBean ItemService service; }
```

### Regression tests

```java
// The MVC slice starts and the controller uses the mocked service.
```

## TEST-H-072: security filter breaks repository test

- Difficulty: Hard
- Framework: Spring Testing Slices
- Language: Java
- Perspective: Data slice
- Concept: security filter breaks repository test
- Symptom: A @DataJpaTest request unexpectedly requires authentication.
- Diagnostic goal: Keep slice scope clear and import only needed configuration.

### Buggy code

```java
@DataJpaTest
class ItemRepositoryTest {}
```

### Expected diagnosis

Importing the full application security configuration changes a focused persistence test.

### Corrected code

```java
@DataJpaTest
@Import(TestDatabaseConfig.class)
class ItemRepositoryTest {}
```

### Regression tests

```java
// The test uses the slice database without loading web security.
```

## TEST-H-073: missing csrf token

- Difficulty: Hard
- Framework: Spring Testing Slices
- Language: Java
- Perspective: MockMvc
- Concept: missing csrf token
- Symptom: A POST test receives 403 unexpectedly.
- Diagnostic goal: Include the security test request post processor.

### Buggy code

```java
mockMvc.perform(post("/items").content(json));
```

### Expected diagnosis

CSRF protection correctly rejects a state-changing request without a token.

### Corrected code

```java
mockMvc.perform(post("/items").with(csrf()).contentType(APPLICATION_JSON).content(json));
```

### Regression tests

```java
// The valid authenticated request passes CSRF and reaches the controller.
```

## TEST-H-074: wrong test configuration

- Difficulty: Hard
- Framework: Spring Testing Slices
- Language: Java
- Perspective: Context bootstrap
- Concept: wrong test configuration
- Symptom: The test starts the wrong application context.
- Diagnostic goal: Load the test configuration that supplies its collaborators.

### Buggy code

```java
@ContextConfiguration(classes = ProductionConfig.class)
class Test {}
```

### Expected diagnosis

A focused test should load the test configuration that supplies its collaborators.

### Corrected code

```java
@ContextConfiguration(classes = TestConfig.class)
class Test {}
```

### Regression tests

```java
// The context contains test doubles and no production connections.
```

## TEST-H-075: mock returns null default

- Difficulty: Hard
- Framework: Spring Testing Slices
- Language: Java
- Perspective: Mocking
- Concept: mock returns null default
- Symptom: The controller throws while the test expects a response.
- Diagnostic goal: Stub the collaborator path that the handler actually uses.

### Buggy code

```java
when(service.find(1L)).thenReturn(null);
```

### Expected diagnosis

Mockito returns null unless the test configures the expected value, so DTO mapping fails.

### Corrected code

```java
when(service.find(1L)).thenReturn(Optional.of(item));
```

### Regression tests

```java
// The success path receives the expected domain object.
```

## TEST-H-076: test rollback assumption

- Difficulty: Hard
- Framework: Spring Testing Slices
- Language: Java
- Perspective: Transactions
- Concept: test rollback assumption
- Symptom: Data leaks between tests.
- Diagnostic goal: Use transactional rollback or clean the database explicitly.

### Buggy code

```java
@SpringBootTest
class ItemTest { @Test void creates() { repository.save(item); } }
```

### Expected diagnosis

A full integration test does not automatically roll back unless a transaction is active for the test.

### Corrected code

```java
@SpringBootTest
@Transactional
class ItemTest { ... }
```

### Regression tests

```java
// Each test starts with a clean database state.
```

## TEST-H-077: container not ready

- Difficulty: Hard
- Framework: Spring Testing Slices
- Language: Java
- Perspective: Test containers
- Concept: container not ready
- Symptom: Integration tests race database startup.
- Diagnostic goal: Use the container lifecycle and dynamic property registration.

### Buggy code

```java
static PostgreSQLContainer<?> db = new PostgreSQLContainer<>("postgres:16");
```

### Expected diagnosis

Creating a container is insufficient if it is not started and its properties are not bound.

### Corrected code

```java
@Container static PostgreSQLContainer<?> db = new PostgreSQLContainer<>("postgres:16");
@DynamicPropertySource static void props(DynamicPropertyRegistry r) { r.add("spring.datasource.url", db::getJdbcUrl); }
```

### Regression tests

```java
// The application datasource points at the running container.
```

## TEST-H-078: only status asserted

- Difficulty: Hard
- Framework: Spring Testing Slices
- Language: Java
- Perspective: Assertions
- Concept: only status asserted
- Symptom: A regression changes the response body unnoticed.
- Diagnostic goal: Assert status, headers, and meaningful payload fields.

### Buggy code

```java
mockMvc.perform(get("/items/1")).andExpect(status().isOk());
```

### Expected diagnosis

A 200 response can still contain the wrong representation.

### Corrected code

```java
mockMvc.perform(get("/items/1")).andExpect(status().isOk()).andExpect(jsonPath("$.id").value(1));
```

### Regression tests

```java
// The contract test fails when the id or JSON shape changes.
```

## TEST-H-079: async result asserted too early

- Difficulty: Hard
- Framework: Spring Testing Slices
- Language: Java
- Perspective: Async tests
- Concept: async result asserted too early
- Symptom: The test is flaky or sees an empty response.
- Diagnostic goal: Wait for the async dispatch before asserting the final result.

### Buggy code

```java
mockMvc.perform(get("/report")).andExpect(status().isOk());
```

### Expected diagnosis

A controller returning a CompletableFuture requires async dispatch handling.

### Corrected code

```java
MvcResult result = mockMvc.perform(get("/report")).andReturn();
mockMvc.perform(asyncDispatch(result)).andExpect(status().isOk());
```

### Regression tests

```java
// The test waits for completion deterministically.
```

## TEST-H-080: test bean overridden by production bean

- Difficulty: Hard
- Framework: Spring Testing Slices
- Language: Java
- Perspective: Profiles
- Concept: test bean overridden by production bean
- Symptom: A test double is ignored.
- Diagnostic goal: Use profile or primary/qualifier rules deliberately.

### Buggy code

```java
@ActiveProfiles("test")
class ServiceTest {}
```

### Expected diagnosis

The test profile alone does not replace a production bean with the same role.

### Corrected code

```java
@TestConfiguration
static class Doubles { @Bean @Primary PaymentGateway gateway() { return new FakeGateway(); } }
```

### Regression tests

```java
// The test resolves the fake gateway and production behavior is isolated.
```

## TEST-H-081: repository missing in @WebMvcTest

- Difficulty: Hard
- Framework: Spring Testing Slices
- Language: Java
- Perspective: Web slice
- Concept: repository missing in @WebMvcTest
- Symptom: The controller test context cannot start.
- Diagnostic goal: Mock only collaborators outside the selected slice.

### Buggy code

```java
@WebMvcTest(ItemController.class)
class ItemTest { @Autowired ItemRepository repository; }
```

### Expected diagnosis

@WebMvcTest excludes repositories and services by design.

### Corrected code

```java
@WebMvcTest(ItemController.class)
class ItemTest { @MockBean ItemService service; }
```

### Regression tests

```java
// The MVC slice starts and the controller uses the mocked service.
```

## TEST-H-082: security filter breaks repository test

- Difficulty: Hard
- Framework: Spring Testing Slices
- Language: Java
- Perspective: Data slice
- Concept: security filter breaks repository test
- Symptom: A @DataJpaTest request unexpectedly requires authentication.
- Diagnostic goal: Keep slice scope clear and import only needed configuration.

### Buggy code

```java
@DataJpaTest
class ItemRepositoryTest {}
```

### Expected diagnosis

Importing the full application security configuration changes a focused persistence test.

### Corrected code

```java
@DataJpaTest
@Import(TestDatabaseConfig.class)
class ItemRepositoryTest {}
```

### Regression tests

```java
// The test uses the slice database without loading web security.
```

## TEST-H-083: missing csrf token

- Difficulty: Hard
- Framework: Spring Testing Slices
- Language: Java
- Perspective: MockMvc
- Concept: missing csrf token
- Symptom: A POST test receives 403 unexpectedly.
- Diagnostic goal: Include the security test request post processor.

### Buggy code

```java
mockMvc.perform(post("/items").content(json));
```

### Expected diagnosis

CSRF protection correctly rejects a state-changing request without a token.

### Corrected code

```java
mockMvc.perform(post("/items").with(csrf()).contentType(APPLICATION_JSON).content(json));
```

### Regression tests

```java
// The valid authenticated request passes CSRF and reaches the controller.
```

## TEST-H-084: wrong test configuration

- Difficulty: Hard
- Framework: Spring Testing Slices
- Language: Java
- Perspective: Context bootstrap
- Concept: wrong test configuration
- Symptom: The test starts the wrong application context.
- Diagnostic goal: Load the test configuration that supplies its collaborators.

### Buggy code

```java
@ContextConfiguration(classes = ProductionConfig.class)
class Test {}
```

### Expected diagnosis

A focused test should load the test configuration that supplies its collaborators.

### Corrected code

```java
@ContextConfiguration(classes = TestConfig.class)
class Test {}
```

### Regression tests

```java
// The context contains test doubles and no production connections.
```

## TEST-H-085: mock returns null default

- Difficulty: Hard
- Framework: Spring Testing Slices
- Language: Java
- Perspective: Mocking
- Concept: mock returns null default
- Symptom: The controller throws while the test expects a response.
- Diagnostic goal: Stub the collaborator path that the handler actually uses.

### Buggy code

```java
when(service.find(1L)).thenReturn(null);
```

### Expected diagnosis

Mockito returns null unless the test configures the expected value, so DTO mapping fails.

### Corrected code

```java
when(service.find(1L)).thenReturn(Optional.of(item));
```

### Regression tests

```java
// The success path receives the expected domain object.
```

## TEST-H-086: test rollback assumption

- Difficulty: Hard
- Framework: Spring Testing Slices
- Language: Java
- Perspective: Transactions
- Concept: test rollback assumption
- Symptom: Data leaks between tests.
- Diagnostic goal: Use transactional rollback or clean the database explicitly.

### Buggy code

```java
@SpringBootTest
class ItemTest { @Test void creates() { repository.save(item); } }
```

### Expected diagnosis

A full integration test does not automatically roll back unless a transaction is active for the test.

### Corrected code

```java
@SpringBootTest
@Transactional
class ItemTest { ... }
```

### Regression tests

```java
// Each test starts with a clean database state.
```

## TEST-H-087: container not ready

- Difficulty: Hard
- Framework: Spring Testing Slices
- Language: Java
- Perspective: Test containers
- Concept: container not ready
- Symptom: Integration tests race database startup.
- Diagnostic goal: Use the container lifecycle and dynamic property registration.

### Buggy code

```java
static PostgreSQLContainer<?> db = new PostgreSQLContainer<>("postgres:16");
```

### Expected diagnosis

Creating a container is insufficient if it is not started and its properties are not bound.

### Corrected code

```java
@Container static PostgreSQLContainer<?> db = new PostgreSQLContainer<>("postgres:16");
@DynamicPropertySource static void props(DynamicPropertyRegistry r) { r.add("spring.datasource.url", db::getJdbcUrl); }
```

### Regression tests

```java
// The application datasource points at the running container.
```

## TEST-H-088: only status asserted

- Difficulty: Hard
- Framework: Spring Testing Slices
- Language: Java
- Perspective: Assertions
- Concept: only status asserted
- Symptom: A regression changes the response body unnoticed.
- Diagnostic goal: Assert status, headers, and meaningful payload fields.

### Buggy code

```java
mockMvc.perform(get("/items/1")).andExpect(status().isOk());
```

### Expected diagnosis

A 200 response can still contain the wrong representation.

### Corrected code

```java
mockMvc.perform(get("/items/1")).andExpect(status().isOk()).andExpect(jsonPath("$.id").value(1));
```

### Regression tests

```java
// The contract test fails when the id or JSON shape changes.
```

## TEST-H-089: async result asserted too early

- Difficulty: Hard
- Framework: Spring Testing Slices
- Language: Java
- Perspective: Async tests
- Concept: async result asserted too early
- Symptom: The test is flaky or sees an empty response.
- Diagnostic goal: Wait for the async dispatch before asserting the final result.

### Buggy code

```java
mockMvc.perform(get("/report")).andExpect(status().isOk());
```

### Expected diagnosis

A controller returning a CompletableFuture requires async dispatch handling.

### Corrected code

```java
MvcResult result = mockMvc.perform(get("/report")).andReturn();
mockMvc.perform(asyncDispatch(result)).andExpect(status().isOk());
```

### Regression tests

```java
// The test waits for completion deterministically.
```

## TEST-H-090: test bean overridden by production bean

- Difficulty: Hard
- Framework: Spring Testing Slices
- Language: Java
- Perspective: Profiles
- Concept: test bean overridden by production bean
- Symptom: A test double is ignored.
- Diagnostic goal: Use profile or primary/qualifier rules deliberately.

### Buggy code

```java
@ActiveProfiles("test")
class ServiceTest {}
```

### Expected diagnosis

The test profile alone does not replace a production bean with the same role.

### Corrected code

```java
@TestConfiguration
static class Doubles { @Bean @Primary PaymentGateway gateway() { return new FakeGateway(); } }
```

### Regression tests

```java
// The test resolves the fake gateway and production behavior is isolated.
```

## TEST-H-091: repository missing in @WebMvcTest

- Difficulty: Hard
- Framework: Spring Testing Slices
- Language: Java
- Perspective: Web slice
- Concept: repository missing in @WebMvcTest
- Symptom: The controller test context cannot start.
- Diagnostic goal: Mock only collaborators outside the selected slice.

### Buggy code

```java
@WebMvcTest(ItemController.class)
class ItemTest { @Autowired ItemRepository repository; }
```

### Expected diagnosis

@WebMvcTest excludes repositories and services by design.

### Corrected code

```java
@WebMvcTest(ItemController.class)
class ItemTest { @MockBean ItemService service; }
```

### Regression tests

```java
// The MVC slice starts and the controller uses the mocked service.
```

## TEST-H-092: security filter breaks repository test

- Difficulty: Hard
- Framework: Spring Testing Slices
- Language: Java
- Perspective: Data slice
- Concept: security filter breaks repository test
- Symptom: A @DataJpaTest request unexpectedly requires authentication.
- Diagnostic goal: Keep slice scope clear and import only needed configuration.

### Buggy code

```java
@DataJpaTest
class ItemRepositoryTest {}
```

### Expected diagnosis

Importing the full application security configuration changes a focused persistence test.

### Corrected code

```java
@DataJpaTest
@Import(TestDatabaseConfig.class)
class ItemRepositoryTest {}
```

### Regression tests

```java
// The test uses the slice database without loading web security.
```

## TEST-H-093: missing csrf token

- Difficulty: Hard
- Framework: Spring Testing Slices
- Language: Java
- Perspective: MockMvc
- Concept: missing csrf token
- Symptom: A POST test receives 403 unexpectedly.
- Diagnostic goal: Include the security test request post processor.

### Buggy code

```java
mockMvc.perform(post("/items").content(json));
```

### Expected diagnosis

CSRF protection correctly rejects a state-changing request without a token.

### Corrected code

```java
mockMvc.perform(post("/items").with(csrf()).contentType(APPLICATION_JSON).content(json));
```

### Regression tests

```java
// The valid authenticated request passes CSRF and reaches the controller.
```

## TEST-H-094: wrong test configuration

- Difficulty: Hard
- Framework: Spring Testing Slices
- Language: Java
- Perspective: Context bootstrap
- Concept: wrong test configuration
- Symptom: The test starts the wrong application context.
- Diagnostic goal: Load the test configuration that supplies its collaborators.

### Buggy code

```java
@ContextConfiguration(classes = ProductionConfig.class)
class Test {}
```

### Expected diagnosis

A focused test should load the test configuration that supplies its collaborators.

### Corrected code

```java
@ContextConfiguration(classes = TestConfig.class)
class Test {}
```

### Regression tests

```java
// The context contains test doubles and no production connections.
```

## TEST-H-095: mock returns null default

- Difficulty: Hard
- Framework: Spring Testing Slices
- Language: Java
- Perspective: Mocking
- Concept: mock returns null default
- Symptom: The controller throws while the test expects a response.
- Diagnostic goal: Stub the collaborator path that the handler actually uses.

### Buggy code

```java
when(service.find(1L)).thenReturn(null);
```

### Expected diagnosis

Mockito returns null unless the test configures the expected value, so DTO mapping fails.

### Corrected code

```java
when(service.find(1L)).thenReturn(Optional.of(item));
```

### Regression tests

```java
// The success path receives the expected domain object.
```

## TEST-H-096: test rollback assumption

- Difficulty: Hard
- Framework: Spring Testing Slices
- Language: Java
- Perspective: Transactions
- Concept: test rollback assumption
- Symptom: Data leaks between tests.
- Diagnostic goal: Use transactional rollback or clean the database explicitly.

### Buggy code

```java
@SpringBootTest
class ItemTest { @Test void creates() { repository.save(item); } }
```

### Expected diagnosis

A full integration test does not automatically roll back unless a transaction is active for the test.

### Corrected code

```java
@SpringBootTest
@Transactional
class ItemTest { ... }
```

### Regression tests

```java
// Each test starts with a clean database state.
```

## TEST-H-097: container not ready

- Difficulty: Hard
- Framework: Spring Testing Slices
- Language: Java
- Perspective: Test containers
- Concept: container not ready
- Symptom: Integration tests race database startup.
- Diagnostic goal: Use the container lifecycle and dynamic property registration.

### Buggy code

```java
static PostgreSQLContainer<?> db = new PostgreSQLContainer<>("postgres:16");
```

### Expected diagnosis

Creating a container is insufficient if it is not started and its properties are not bound.

### Corrected code

```java
@Container static PostgreSQLContainer<?> db = new PostgreSQLContainer<>("postgres:16");
@DynamicPropertySource static void props(DynamicPropertyRegistry r) { r.add("spring.datasource.url", db::getJdbcUrl); }
```

### Regression tests

```java
// The application datasource points at the running container.
```

## TEST-H-098: only status asserted

- Difficulty: Hard
- Framework: Spring Testing Slices
- Language: Java
- Perspective: Assertions
- Concept: only status asserted
- Symptom: A regression changes the response body unnoticed.
- Diagnostic goal: Assert status, headers, and meaningful payload fields.

### Buggy code

```java
mockMvc.perform(get("/items/1")).andExpect(status().isOk());
```

### Expected diagnosis

A 200 response can still contain the wrong representation.

### Corrected code

```java
mockMvc.perform(get("/items/1")).andExpect(status().isOk()).andExpect(jsonPath("$.id").value(1));
```

### Regression tests

```java
// The contract test fails when the id or JSON shape changes.
```

## TEST-H-099: async result asserted too early

- Difficulty: Hard
- Framework: Spring Testing Slices
- Language: Java
- Perspective: Async tests
- Concept: async result asserted too early
- Symptom: The test is flaky or sees an empty response.
- Diagnostic goal: Wait for the async dispatch before asserting the final result.

### Buggy code

```java
mockMvc.perform(get("/report")).andExpect(status().isOk());
```

### Expected diagnosis

A controller returning a CompletableFuture requires async dispatch handling.

### Corrected code

```java
MvcResult result = mockMvc.perform(get("/report")).andReturn();
mockMvc.perform(asyncDispatch(result)).andExpect(status().isOk());
```

### Regression tests

```java
// The test waits for completion deterministically.
```

## TEST-H-100: test bean overridden by production bean

- Difficulty: Hard
- Framework: Spring Testing Slices
- Language: Java
- Perspective: Profiles
- Concept: test bean overridden by production bean
- Symptom: A test double is ignored.
- Diagnostic goal: Use profile or primary/qualifier rules deliberately.

### Buggy code

```java
@ActiveProfiles("test")
class ServiceTest {}
```

### Expected diagnosis

The test profile alone does not replace a production bean with the same role.

### Corrected code

```java
@TestConfiguration
static class Doubles { @Bean @Primary PaymentGateway gateway() { return new FakeGateway(); } }
```

### Regression tests

```java
// The test resolves the fake gateway and production behavior is isolated.
```
