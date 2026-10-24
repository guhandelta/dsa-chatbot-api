# Spring Boot 3 Debug Exercises

A RAG-training corpus of 300 debugging exercises for Spring Boot 3. Each record contains framework-specific metadata, a failure example, an editorial diagnosis, corrected Java/Spring code, and regression guidance. Corrected code is training material and must be stripped from learner-facing challenge responses.

## Coverage

- Easy: 100 exercises
- Medium: 100 exercises
- Hard: 100 exercises
- Perspectives: configuration, lifecycle, proxies, persistence, HTTP contracts, security, testing, transactions, observability, and deployment

## SB3-E-001: profile property mismatch

- Difficulty: Easy
- Framework: Spring Boot 3
- Language: Java
- Perspective: Configuration
- Concept: profile property mismatch
- Symptom: The production datasource is not configured.
- Diagnostic goal: Trace active profiles and property source precedence.

### Buggy code

```java
@Value("${app.url}")
private String url;
```

### Expected diagnosis

The property may exist only under a different profile or prefix; startup failure is clearer than a silent default.

### Corrected code

```java
@ConfigurationProperties(prefix = "app")
public record AppProperties(String url) {}
```

### Regression tests

```java
// Run with each profile and assert the expected URL is bound.
```

## SB3-E-002: missing starter dependency

- Difficulty: Easy
- Framework: Spring Boot 3
- Language: Java
- Perspective: Auto-configuration
- Concept: missing starter dependency
- Symptom: A configured feature has no bean at runtime.
- Diagnostic goal: Map the requested behavior to its Boot starter and auto-configuration.

### Buggy code

```java
@Bean
SecurityFilterChain chain(HttpSecurity http) { return http.build(); }
```

### Expected diagnosis

A security configuration cannot work if the relevant starter and transitive infrastructure are absent.

### Corrected code

```java
dependencies { implementation("org.springframework.boot:spring-boot-starter-security") }
```

### Regression tests

```java
// Include spring-boot-starter-security and assert the context starts.
```

## SB3-E-003: health endpoint exposes internals

- Difficulty: Easy
- Framework: Spring Boot 3
- Language: Java
- Perspective: Actuator
- Concept: health endpoint exposes internals
- Symptom: Operational endpoints leak sensitive details.
- Diagnostic goal: Separate endpoint exposure from health detail visibility.

### Buggy code

```java
management.endpoints.web.exposure.include=*
management.endpoint.health.show-details=always
```

### Expected diagnosis

Wildcard exposure and unrestricted details reveal environment and dependency information.

### Corrected code

```java
management.endpoints.web.exposure.include=health,info
management.endpoint.health.show-details=when_authorized
```

### Regression tests

```java
// Unauthenticated probes see status without credentials or connection details.
```

## SB3-E-004: test profile not activated

- Difficulty: Easy
- Framework: Spring Boot 3
- Language: Java
- Perspective: Profiles
- Concept: test profile not activated
- Symptom: Tests connect to a developer database.
- Diagnostic goal: Make the test environment explicit and isolated.

### Buggy code

```java
@SpringBootTest
class RepositoryTest {}
```

### Expected diagnosis

Without a test profile, normal application properties can select an external database.

### Corrected code

```java
@SpringBootTest
@ActiveProfiles("test")
class RepositoryTest {}
```

### Regression tests

```java
// Test execution uses the embedded or containerized test datasource.
```

## SB3-E-005: correlation id lost

- Difficulty: Easy
- Framework: Spring Boot 3
- Language: Java
- Perspective: Observability
- Concept: correlation id lost
- Symptom: Logs from one request cannot be joined across services.
- Diagnostic goal: Create and clear request-scoped diagnostic context.

### Buggy code

```java
filterChain.doFilter(request, response);
```

### Expected diagnosis

The request proceeds without installing a correlation value and without cleanup.

### Corrected code

```java
try { MDC.put("requestId", requestId); filterChain.doFilter(request, response); } finally { MDC.remove("requestId"); }
```

### Regression tests

```java
// Every log line has the request id and the thread is clean afterward.
```

## SB3-E-006: Java time format mismatch

- Difficulty: Easy
- Framework: Spring Boot 3
- Language: Java
- Perspective: Serialization
- Concept: Java time format mismatch
- Symptom: Clients reject the response date.
- Diagnostic goal: Declare the wire format at the API boundary.

### Buggy code

```java
record Event(Instant createdAt) {}
```

### Expected diagnosis

The default representation may differ from the documented contract or client expectation.

### Corrected code

```java
record Event(@JsonFormat(pattern = "yyyy-MM-dd'T'HH:mm:ssX") Instant createdAt) {}
```

### Regression tests

```java
// Contract test asserts the exact serialized timestamp.
```

## SB3-E-007: circular bean dependency

- Difficulty: Easy
- Framework: Spring Boot 3
- Language: Java
- Perspective: Startup
- Concept: circular bean dependency
- Symptom: ApplicationContext fails during startup.
- Diagnostic goal: Break the cycle at the architecture boundary.

### Buggy code

```java
class A { A(B b) {} }
class B { B(A a) {} }
```

### Expected diagnosis

Constructor injection exposes a cycle that cannot be resolved safely.

### Corrected code

```java
class A { A(Port port) {} }
class B implements Port { B() {} }
```

### Regression tests

```java
// Context starts and each service depends on an interface with one direction.
```

## SB3-E-008: unbounded upstream timeout

- Difficulty: Easy
- Framework: Spring Boot 3
- Language: Java
- Perspective: HTTP client
- Concept: unbounded upstream timeout
- Symptom: A slow dependency exhausts request threads.
- Diagnostic goal: Set connect and response timeouts and define fallback behavior.

### Buggy code

```java
return restClient.get().uri(uri).retrieve().body(String.class);
```

### Expected diagnosis

Without timeouts, an unavailable upstream can hold workers indefinitely.

### Corrected code

```java
return restClient.get().uri(uri).retrieve().onStatus(s -> s.value() == 404, r -> new NotFoundException()).body(String.class);
```

### Regression tests

```java
// Slow and error responses produce bounded, documented outcomes.
```

## SB3-E-009: graceful shutdown disabled

- Difficulty: Easy
- Framework: Spring Boot 3
- Language: Java
- Perspective: Deployment
- Concept: graceful shutdown disabled
- Symptom: In-flight requests are cut off during rollout.
- Diagnostic goal: Enable graceful shutdown and give the platform enough time.

### Buggy code

```java
server.shutdown=immediate
```

### Expected diagnosis

Immediate shutdown drops active requests and can interrupt transactions.

### Corrected code

```java
server.shutdown=graceful
spring.lifecycle.timeout-per-shutdown-phase=30s
```

### Regression tests

```java
// A shutdown waits for active work up to the configured deadline.
```

## SB3-E-010: configuration accepted without validation

- Difficulty: Easy
- Framework: Spring Boot 3
- Language: Java
- Perspective: Validation
- Concept: configuration accepted without validation
- Symptom: The app starts with an invalid port or URL.
- Diagnostic goal: Validate configuration at binding time.

### Buggy code

```java
record ClientProperties(String baseUrl, int timeoutMs) {}
```

### Expected diagnosis

Invalid values surface only when the first request is made.

### Corrected code

```java
record ClientProperties(@jakarta.validation.constraints.NotBlank String baseUrl, @jakarta.validation.constraints.Positive int timeoutMs) {}
```

### Regression tests

```java
// Invalid configuration fails context startup with a useful property path.
```

## SB3-E-011: profile property mismatch

- Difficulty: Easy
- Framework: Spring Boot 3
- Language: Java
- Perspective: Configuration
- Concept: profile property mismatch
- Symptom: The production datasource is not configured.
- Diagnostic goal: Trace active profiles and property source precedence.

### Buggy code

```java
@Value("${app.url}")
private String url;
```

### Expected diagnosis

The property may exist only under a different profile or prefix; startup failure is clearer than a silent default.

### Corrected code

```java
@ConfigurationProperties(prefix = "app")
public record AppProperties(String url) {}
```

### Regression tests

```java
// Run with each profile and assert the expected URL is bound.
```

## SB3-E-012: missing starter dependency

- Difficulty: Easy
- Framework: Spring Boot 3
- Language: Java
- Perspective: Auto-configuration
- Concept: missing starter dependency
- Symptom: A configured feature has no bean at runtime.
- Diagnostic goal: Map the requested behavior to its Boot starter and auto-configuration.

### Buggy code

```java
@Bean
SecurityFilterChain chain(HttpSecurity http) { return http.build(); }
```

### Expected diagnosis

A security configuration cannot work if the relevant starter and transitive infrastructure are absent.

### Corrected code

```java
dependencies { implementation("org.springframework.boot:spring-boot-starter-security") }
```

### Regression tests

```java
// Include spring-boot-starter-security and assert the context starts.
```

## SB3-E-013: health endpoint exposes internals

- Difficulty: Easy
- Framework: Spring Boot 3
- Language: Java
- Perspective: Actuator
- Concept: health endpoint exposes internals
- Symptom: Operational endpoints leak sensitive details.
- Diagnostic goal: Separate endpoint exposure from health detail visibility.

### Buggy code

```java
management.endpoints.web.exposure.include=*
management.endpoint.health.show-details=always
```

### Expected diagnosis

Wildcard exposure and unrestricted details reveal environment and dependency information.

### Corrected code

```java
management.endpoints.web.exposure.include=health,info
management.endpoint.health.show-details=when_authorized
```

### Regression tests

```java
// Unauthenticated probes see status without credentials or connection details.
```

## SB3-E-014: test profile not activated

- Difficulty: Easy
- Framework: Spring Boot 3
- Language: Java
- Perspective: Profiles
- Concept: test profile not activated
- Symptom: Tests connect to a developer database.
- Diagnostic goal: Make the test environment explicit and isolated.

### Buggy code

```java
@SpringBootTest
class RepositoryTest {}
```

### Expected diagnosis

Without a test profile, normal application properties can select an external database.

### Corrected code

```java
@SpringBootTest
@ActiveProfiles("test")
class RepositoryTest {}
```

### Regression tests

```java
// Test execution uses the embedded or containerized test datasource.
```

## SB3-E-015: correlation id lost

- Difficulty: Easy
- Framework: Spring Boot 3
- Language: Java
- Perspective: Observability
- Concept: correlation id lost
- Symptom: Logs from one request cannot be joined across services.
- Diagnostic goal: Create and clear request-scoped diagnostic context.

### Buggy code

```java
filterChain.doFilter(request, response);
```

### Expected diagnosis

The request proceeds without installing a correlation value and without cleanup.

### Corrected code

```java
try { MDC.put("requestId", requestId); filterChain.doFilter(request, response); } finally { MDC.remove("requestId"); }
```

### Regression tests

```java
// Every log line has the request id and the thread is clean afterward.
```

## SB3-E-016: Java time format mismatch

- Difficulty: Easy
- Framework: Spring Boot 3
- Language: Java
- Perspective: Serialization
- Concept: Java time format mismatch
- Symptom: Clients reject the response date.
- Diagnostic goal: Declare the wire format at the API boundary.

### Buggy code

```java
record Event(Instant createdAt) {}
```

### Expected diagnosis

The default representation may differ from the documented contract or client expectation.

### Corrected code

```java
record Event(@JsonFormat(pattern = "yyyy-MM-dd'T'HH:mm:ssX") Instant createdAt) {}
```

### Regression tests

```java
// Contract test asserts the exact serialized timestamp.
```

## SB3-E-017: circular bean dependency

- Difficulty: Easy
- Framework: Spring Boot 3
- Language: Java
- Perspective: Startup
- Concept: circular bean dependency
- Symptom: ApplicationContext fails during startup.
- Diagnostic goal: Break the cycle at the architecture boundary.

### Buggy code

```java
class A { A(B b) {} }
class B { B(A a) {} }
```

### Expected diagnosis

Constructor injection exposes a cycle that cannot be resolved safely.

### Corrected code

```java
class A { A(Port port) {} }
class B implements Port { B() {} }
```

### Regression tests

```java
// Context starts and each service depends on an interface with one direction.
```

## SB3-E-018: unbounded upstream timeout

- Difficulty: Easy
- Framework: Spring Boot 3
- Language: Java
- Perspective: HTTP client
- Concept: unbounded upstream timeout
- Symptom: A slow dependency exhausts request threads.
- Diagnostic goal: Set connect and response timeouts and define fallback behavior.

### Buggy code

```java
return restClient.get().uri(uri).retrieve().body(String.class);
```

### Expected diagnosis

Without timeouts, an unavailable upstream can hold workers indefinitely.

### Corrected code

```java
return restClient.get().uri(uri).retrieve().onStatus(s -> s.value() == 404, r -> new NotFoundException()).body(String.class);
```

### Regression tests

```java
// Slow and error responses produce bounded, documented outcomes.
```

## SB3-E-019: graceful shutdown disabled

- Difficulty: Easy
- Framework: Spring Boot 3
- Language: Java
- Perspective: Deployment
- Concept: graceful shutdown disabled
- Symptom: In-flight requests are cut off during rollout.
- Diagnostic goal: Enable graceful shutdown and give the platform enough time.

### Buggy code

```java
server.shutdown=immediate
```

### Expected diagnosis

Immediate shutdown drops active requests and can interrupt transactions.

### Corrected code

```java
server.shutdown=graceful
spring.lifecycle.timeout-per-shutdown-phase=30s
```

### Regression tests

```java
// A shutdown waits for active work up to the configured deadline.
```

## SB3-E-020: configuration accepted without validation

- Difficulty: Easy
- Framework: Spring Boot 3
- Language: Java
- Perspective: Validation
- Concept: configuration accepted without validation
- Symptom: The app starts with an invalid port or URL.
- Diagnostic goal: Validate configuration at binding time.

### Buggy code

```java
record ClientProperties(String baseUrl, int timeoutMs) {}
```

### Expected diagnosis

Invalid values surface only when the first request is made.

### Corrected code

```java
record ClientProperties(@jakarta.validation.constraints.NotBlank String baseUrl, @jakarta.validation.constraints.Positive int timeoutMs) {}
```

### Regression tests

```java
// Invalid configuration fails context startup with a useful property path.
```

## SB3-E-021: profile property mismatch

- Difficulty: Easy
- Framework: Spring Boot 3
- Language: Java
- Perspective: Configuration
- Concept: profile property mismatch
- Symptom: The production datasource is not configured.
- Diagnostic goal: Trace active profiles and property source precedence.

### Buggy code

```java
@Value("${app.url}")
private String url;
```

### Expected diagnosis

The property may exist only under a different profile or prefix; startup failure is clearer than a silent default.

### Corrected code

```java
@ConfigurationProperties(prefix = "app")
public record AppProperties(String url) {}
```

### Regression tests

```java
// Run with each profile and assert the expected URL is bound.
```

## SB3-E-022: missing starter dependency

- Difficulty: Easy
- Framework: Spring Boot 3
- Language: Java
- Perspective: Auto-configuration
- Concept: missing starter dependency
- Symptom: A configured feature has no bean at runtime.
- Diagnostic goal: Map the requested behavior to its Boot starter and auto-configuration.

### Buggy code

```java
@Bean
SecurityFilterChain chain(HttpSecurity http) { return http.build(); }
```

### Expected diagnosis

A security configuration cannot work if the relevant starter and transitive infrastructure are absent.

### Corrected code

```java
dependencies { implementation("org.springframework.boot:spring-boot-starter-security") }
```

### Regression tests

```java
// Include spring-boot-starter-security and assert the context starts.
```

## SB3-E-023: health endpoint exposes internals

- Difficulty: Easy
- Framework: Spring Boot 3
- Language: Java
- Perspective: Actuator
- Concept: health endpoint exposes internals
- Symptom: Operational endpoints leak sensitive details.
- Diagnostic goal: Separate endpoint exposure from health detail visibility.

### Buggy code

```java
management.endpoints.web.exposure.include=*
management.endpoint.health.show-details=always
```

### Expected diagnosis

Wildcard exposure and unrestricted details reveal environment and dependency information.

### Corrected code

```java
management.endpoints.web.exposure.include=health,info
management.endpoint.health.show-details=when_authorized
```

### Regression tests

```java
// Unauthenticated probes see status without credentials or connection details.
```

## SB3-E-024: test profile not activated

- Difficulty: Easy
- Framework: Spring Boot 3
- Language: Java
- Perspective: Profiles
- Concept: test profile not activated
- Symptom: Tests connect to a developer database.
- Diagnostic goal: Make the test environment explicit and isolated.

### Buggy code

```java
@SpringBootTest
class RepositoryTest {}
```

### Expected diagnosis

Without a test profile, normal application properties can select an external database.

### Corrected code

```java
@SpringBootTest
@ActiveProfiles("test")
class RepositoryTest {}
```

### Regression tests

```java
// Test execution uses the embedded or containerized test datasource.
```

## SB3-E-025: correlation id lost

- Difficulty: Easy
- Framework: Spring Boot 3
- Language: Java
- Perspective: Observability
- Concept: correlation id lost
- Symptom: Logs from one request cannot be joined across services.
- Diagnostic goal: Create and clear request-scoped diagnostic context.

### Buggy code

```java
filterChain.doFilter(request, response);
```

### Expected diagnosis

The request proceeds without installing a correlation value and without cleanup.

### Corrected code

```java
try { MDC.put("requestId", requestId); filterChain.doFilter(request, response); } finally { MDC.remove("requestId"); }
```

### Regression tests

```java
// Every log line has the request id and the thread is clean afterward.
```

## SB3-E-026: Java time format mismatch

- Difficulty: Easy
- Framework: Spring Boot 3
- Language: Java
- Perspective: Serialization
- Concept: Java time format mismatch
- Symptom: Clients reject the response date.
- Diagnostic goal: Declare the wire format at the API boundary.

### Buggy code

```java
record Event(Instant createdAt) {}
```

### Expected diagnosis

The default representation may differ from the documented contract or client expectation.

### Corrected code

```java
record Event(@JsonFormat(pattern = "yyyy-MM-dd'T'HH:mm:ssX") Instant createdAt) {}
```

### Regression tests

```java
// Contract test asserts the exact serialized timestamp.
```

## SB3-E-027: circular bean dependency

- Difficulty: Easy
- Framework: Spring Boot 3
- Language: Java
- Perspective: Startup
- Concept: circular bean dependency
- Symptom: ApplicationContext fails during startup.
- Diagnostic goal: Break the cycle at the architecture boundary.

### Buggy code

```java
class A { A(B b) {} }
class B { B(A a) {} }
```

### Expected diagnosis

Constructor injection exposes a cycle that cannot be resolved safely.

### Corrected code

```java
class A { A(Port port) {} }
class B implements Port { B() {} }
```

### Regression tests

```java
// Context starts and each service depends on an interface with one direction.
```

## SB3-E-028: unbounded upstream timeout

- Difficulty: Easy
- Framework: Spring Boot 3
- Language: Java
- Perspective: HTTP client
- Concept: unbounded upstream timeout
- Symptom: A slow dependency exhausts request threads.
- Diagnostic goal: Set connect and response timeouts and define fallback behavior.

### Buggy code

```java
return restClient.get().uri(uri).retrieve().body(String.class);
```

### Expected diagnosis

Without timeouts, an unavailable upstream can hold workers indefinitely.

### Corrected code

```java
return restClient.get().uri(uri).retrieve().onStatus(s -> s.value() == 404, r -> new NotFoundException()).body(String.class);
```

### Regression tests

```java
// Slow and error responses produce bounded, documented outcomes.
```

## SB3-E-029: graceful shutdown disabled

- Difficulty: Easy
- Framework: Spring Boot 3
- Language: Java
- Perspective: Deployment
- Concept: graceful shutdown disabled
- Symptom: In-flight requests are cut off during rollout.
- Diagnostic goal: Enable graceful shutdown and give the platform enough time.

### Buggy code

```java
server.shutdown=immediate
```

### Expected diagnosis

Immediate shutdown drops active requests and can interrupt transactions.

### Corrected code

```java
server.shutdown=graceful
spring.lifecycle.timeout-per-shutdown-phase=30s
```

### Regression tests

```java
// A shutdown waits for active work up to the configured deadline.
```

## SB3-E-030: configuration accepted without validation

- Difficulty: Easy
- Framework: Spring Boot 3
- Language: Java
- Perspective: Validation
- Concept: configuration accepted without validation
- Symptom: The app starts with an invalid port or URL.
- Diagnostic goal: Validate configuration at binding time.

### Buggy code

```java
record ClientProperties(String baseUrl, int timeoutMs) {}
```

### Expected diagnosis

Invalid values surface only when the first request is made.

### Corrected code

```java
record ClientProperties(@jakarta.validation.constraints.NotBlank String baseUrl, @jakarta.validation.constraints.Positive int timeoutMs) {}
```

### Regression tests

```java
// Invalid configuration fails context startup with a useful property path.
```

## SB3-E-031: profile property mismatch

- Difficulty: Easy
- Framework: Spring Boot 3
- Language: Java
- Perspective: Configuration
- Concept: profile property mismatch
- Symptom: The production datasource is not configured.
- Diagnostic goal: Trace active profiles and property source precedence.

### Buggy code

```java
@Value("${app.url}")
private String url;
```

### Expected diagnosis

The property may exist only under a different profile or prefix; startup failure is clearer than a silent default.

### Corrected code

```java
@ConfigurationProperties(prefix = "app")
public record AppProperties(String url) {}
```

### Regression tests

```java
// Run with each profile and assert the expected URL is bound.
```

## SB3-E-032: missing starter dependency

- Difficulty: Easy
- Framework: Spring Boot 3
- Language: Java
- Perspective: Auto-configuration
- Concept: missing starter dependency
- Symptom: A configured feature has no bean at runtime.
- Diagnostic goal: Map the requested behavior to its Boot starter and auto-configuration.

### Buggy code

```java
@Bean
SecurityFilterChain chain(HttpSecurity http) { return http.build(); }
```

### Expected diagnosis

A security configuration cannot work if the relevant starter and transitive infrastructure are absent.

### Corrected code

```java
dependencies { implementation("org.springframework.boot:spring-boot-starter-security") }
```

### Regression tests

```java
// Include spring-boot-starter-security and assert the context starts.
```

## SB3-E-033: health endpoint exposes internals

- Difficulty: Easy
- Framework: Spring Boot 3
- Language: Java
- Perspective: Actuator
- Concept: health endpoint exposes internals
- Symptom: Operational endpoints leak sensitive details.
- Diagnostic goal: Separate endpoint exposure from health detail visibility.

### Buggy code

```java
management.endpoints.web.exposure.include=*
management.endpoint.health.show-details=always
```

### Expected diagnosis

Wildcard exposure and unrestricted details reveal environment and dependency information.

### Corrected code

```java
management.endpoints.web.exposure.include=health,info
management.endpoint.health.show-details=when_authorized
```

### Regression tests

```java
// Unauthenticated probes see status without credentials or connection details.
```

## SB3-E-034: test profile not activated

- Difficulty: Easy
- Framework: Spring Boot 3
- Language: Java
- Perspective: Profiles
- Concept: test profile not activated
- Symptom: Tests connect to a developer database.
- Diagnostic goal: Make the test environment explicit and isolated.

### Buggy code

```java
@SpringBootTest
class RepositoryTest {}
```

### Expected diagnosis

Without a test profile, normal application properties can select an external database.

### Corrected code

```java
@SpringBootTest
@ActiveProfiles("test")
class RepositoryTest {}
```

### Regression tests

```java
// Test execution uses the embedded or containerized test datasource.
```

## SB3-E-035: correlation id lost

- Difficulty: Easy
- Framework: Spring Boot 3
- Language: Java
- Perspective: Observability
- Concept: correlation id lost
- Symptom: Logs from one request cannot be joined across services.
- Diagnostic goal: Create and clear request-scoped diagnostic context.

### Buggy code

```java
filterChain.doFilter(request, response);
```

### Expected diagnosis

The request proceeds without installing a correlation value and without cleanup.

### Corrected code

```java
try { MDC.put("requestId", requestId); filterChain.doFilter(request, response); } finally { MDC.remove("requestId"); }
```

### Regression tests

```java
// Every log line has the request id and the thread is clean afterward.
```

## SB3-E-036: Java time format mismatch

- Difficulty: Easy
- Framework: Spring Boot 3
- Language: Java
- Perspective: Serialization
- Concept: Java time format mismatch
- Symptom: Clients reject the response date.
- Diagnostic goal: Declare the wire format at the API boundary.

### Buggy code

```java
record Event(Instant createdAt) {}
```

### Expected diagnosis

The default representation may differ from the documented contract or client expectation.

### Corrected code

```java
record Event(@JsonFormat(pattern = "yyyy-MM-dd'T'HH:mm:ssX") Instant createdAt) {}
```

### Regression tests

```java
// Contract test asserts the exact serialized timestamp.
```

## SB3-E-037: circular bean dependency

- Difficulty: Easy
- Framework: Spring Boot 3
- Language: Java
- Perspective: Startup
- Concept: circular bean dependency
- Symptom: ApplicationContext fails during startup.
- Diagnostic goal: Break the cycle at the architecture boundary.

### Buggy code

```java
class A { A(B b) {} }
class B { B(A a) {} }
```

### Expected diagnosis

Constructor injection exposes a cycle that cannot be resolved safely.

### Corrected code

```java
class A { A(Port port) {} }
class B implements Port { B() {} }
```

### Regression tests

```java
// Context starts and each service depends on an interface with one direction.
```

## SB3-E-038: unbounded upstream timeout

- Difficulty: Easy
- Framework: Spring Boot 3
- Language: Java
- Perspective: HTTP client
- Concept: unbounded upstream timeout
- Symptom: A slow dependency exhausts request threads.
- Diagnostic goal: Set connect and response timeouts and define fallback behavior.

### Buggy code

```java
return restClient.get().uri(uri).retrieve().body(String.class);
```

### Expected diagnosis

Without timeouts, an unavailable upstream can hold workers indefinitely.

### Corrected code

```java
return restClient.get().uri(uri).retrieve().onStatus(s -> s.value() == 404, r -> new NotFoundException()).body(String.class);
```

### Regression tests

```java
// Slow and error responses produce bounded, documented outcomes.
```

## SB3-E-039: graceful shutdown disabled

- Difficulty: Easy
- Framework: Spring Boot 3
- Language: Java
- Perspective: Deployment
- Concept: graceful shutdown disabled
- Symptom: In-flight requests are cut off during rollout.
- Diagnostic goal: Enable graceful shutdown and give the platform enough time.

### Buggy code

```java
server.shutdown=immediate
```

### Expected diagnosis

Immediate shutdown drops active requests and can interrupt transactions.

### Corrected code

```java
server.shutdown=graceful
spring.lifecycle.timeout-per-shutdown-phase=30s
```

### Regression tests

```java
// A shutdown waits for active work up to the configured deadline.
```

## SB3-E-040: configuration accepted without validation

- Difficulty: Easy
- Framework: Spring Boot 3
- Language: Java
- Perspective: Validation
- Concept: configuration accepted without validation
- Symptom: The app starts with an invalid port or URL.
- Diagnostic goal: Validate configuration at binding time.

### Buggy code

```java
record ClientProperties(String baseUrl, int timeoutMs) {}
```

### Expected diagnosis

Invalid values surface only when the first request is made.

### Corrected code

```java
record ClientProperties(@jakarta.validation.constraints.NotBlank String baseUrl, @jakarta.validation.constraints.Positive int timeoutMs) {}
```

### Regression tests

```java
// Invalid configuration fails context startup with a useful property path.
```

## SB3-E-041: profile property mismatch

- Difficulty: Easy
- Framework: Spring Boot 3
- Language: Java
- Perspective: Configuration
- Concept: profile property mismatch
- Symptom: The production datasource is not configured.
- Diagnostic goal: Trace active profiles and property source precedence.

### Buggy code

```java
@Value("${app.url}")
private String url;
```

### Expected diagnosis

The property may exist only under a different profile or prefix; startup failure is clearer than a silent default.

### Corrected code

```java
@ConfigurationProperties(prefix = "app")
public record AppProperties(String url) {}
```

### Regression tests

```java
// Run with each profile and assert the expected URL is bound.
```

## SB3-E-042: missing starter dependency

- Difficulty: Easy
- Framework: Spring Boot 3
- Language: Java
- Perspective: Auto-configuration
- Concept: missing starter dependency
- Symptom: A configured feature has no bean at runtime.
- Diagnostic goal: Map the requested behavior to its Boot starter and auto-configuration.

### Buggy code

```java
@Bean
SecurityFilterChain chain(HttpSecurity http) { return http.build(); }
```

### Expected diagnosis

A security configuration cannot work if the relevant starter and transitive infrastructure are absent.

### Corrected code

```java
dependencies { implementation("org.springframework.boot:spring-boot-starter-security") }
```

### Regression tests

```java
// Include spring-boot-starter-security and assert the context starts.
```

## SB3-E-043: health endpoint exposes internals

- Difficulty: Easy
- Framework: Spring Boot 3
- Language: Java
- Perspective: Actuator
- Concept: health endpoint exposes internals
- Symptom: Operational endpoints leak sensitive details.
- Diagnostic goal: Separate endpoint exposure from health detail visibility.

### Buggy code

```java
management.endpoints.web.exposure.include=*
management.endpoint.health.show-details=always
```

### Expected diagnosis

Wildcard exposure and unrestricted details reveal environment and dependency information.

### Corrected code

```java
management.endpoints.web.exposure.include=health,info
management.endpoint.health.show-details=when_authorized
```

### Regression tests

```java
// Unauthenticated probes see status without credentials or connection details.
```

## SB3-E-044: test profile not activated

- Difficulty: Easy
- Framework: Spring Boot 3
- Language: Java
- Perspective: Profiles
- Concept: test profile not activated
- Symptom: Tests connect to a developer database.
- Diagnostic goal: Make the test environment explicit and isolated.

### Buggy code

```java
@SpringBootTest
class RepositoryTest {}
```

### Expected diagnosis

Without a test profile, normal application properties can select an external database.

### Corrected code

```java
@SpringBootTest
@ActiveProfiles("test")
class RepositoryTest {}
```

### Regression tests

```java
// Test execution uses the embedded or containerized test datasource.
```

## SB3-E-045: correlation id lost

- Difficulty: Easy
- Framework: Spring Boot 3
- Language: Java
- Perspective: Observability
- Concept: correlation id lost
- Symptom: Logs from one request cannot be joined across services.
- Diagnostic goal: Create and clear request-scoped diagnostic context.

### Buggy code

```java
filterChain.doFilter(request, response);
```

### Expected diagnosis

The request proceeds without installing a correlation value and without cleanup.

### Corrected code

```java
try { MDC.put("requestId", requestId); filterChain.doFilter(request, response); } finally { MDC.remove("requestId"); }
```

### Regression tests

```java
// Every log line has the request id and the thread is clean afterward.
```

## SB3-E-046: Java time format mismatch

- Difficulty: Easy
- Framework: Spring Boot 3
- Language: Java
- Perspective: Serialization
- Concept: Java time format mismatch
- Symptom: Clients reject the response date.
- Diagnostic goal: Declare the wire format at the API boundary.

### Buggy code

```java
record Event(Instant createdAt) {}
```

### Expected diagnosis

The default representation may differ from the documented contract or client expectation.

### Corrected code

```java
record Event(@JsonFormat(pattern = "yyyy-MM-dd'T'HH:mm:ssX") Instant createdAt) {}
```

### Regression tests

```java
// Contract test asserts the exact serialized timestamp.
```

## SB3-E-047: circular bean dependency

- Difficulty: Easy
- Framework: Spring Boot 3
- Language: Java
- Perspective: Startup
- Concept: circular bean dependency
- Symptom: ApplicationContext fails during startup.
- Diagnostic goal: Break the cycle at the architecture boundary.

### Buggy code

```java
class A { A(B b) {} }
class B { B(A a) {} }
```

### Expected diagnosis

Constructor injection exposes a cycle that cannot be resolved safely.

### Corrected code

```java
class A { A(Port port) {} }
class B implements Port { B() {} }
```

### Regression tests

```java
// Context starts and each service depends on an interface with one direction.
```

## SB3-E-048: unbounded upstream timeout

- Difficulty: Easy
- Framework: Spring Boot 3
- Language: Java
- Perspective: HTTP client
- Concept: unbounded upstream timeout
- Symptom: A slow dependency exhausts request threads.
- Diagnostic goal: Set connect and response timeouts and define fallback behavior.

### Buggy code

```java
return restClient.get().uri(uri).retrieve().body(String.class);
```

### Expected diagnosis

Without timeouts, an unavailable upstream can hold workers indefinitely.

### Corrected code

```java
return restClient.get().uri(uri).retrieve().onStatus(s -> s.value() == 404, r -> new NotFoundException()).body(String.class);
```

### Regression tests

```java
// Slow and error responses produce bounded, documented outcomes.
```

## SB3-E-049: graceful shutdown disabled

- Difficulty: Easy
- Framework: Spring Boot 3
- Language: Java
- Perspective: Deployment
- Concept: graceful shutdown disabled
- Symptom: In-flight requests are cut off during rollout.
- Diagnostic goal: Enable graceful shutdown and give the platform enough time.

### Buggy code

```java
server.shutdown=immediate
```

### Expected diagnosis

Immediate shutdown drops active requests and can interrupt transactions.

### Corrected code

```java
server.shutdown=graceful
spring.lifecycle.timeout-per-shutdown-phase=30s
```

### Regression tests

```java
// A shutdown waits for active work up to the configured deadline.
```

## SB3-E-050: configuration accepted without validation

- Difficulty: Easy
- Framework: Spring Boot 3
- Language: Java
- Perspective: Validation
- Concept: configuration accepted without validation
- Symptom: The app starts with an invalid port or URL.
- Diagnostic goal: Validate configuration at binding time.

### Buggy code

```java
record ClientProperties(String baseUrl, int timeoutMs) {}
```

### Expected diagnosis

Invalid values surface only when the first request is made.

### Corrected code

```java
record ClientProperties(@jakarta.validation.constraints.NotBlank String baseUrl, @jakarta.validation.constraints.Positive int timeoutMs) {}
```

### Regression tests

```java
// Invalid configuration fails context startup with a useful property path.
```

## SB3-E-051: profile property mismatch

- Difficulty: Easy
- Framework: Spring Boot 3
- Language: Java
- Perspective: Configuration
- Concept: profile property mismatch
- Symptom: The production datasource is not configured.
- Diagnostic goal: Trace active profiles and property source precedence.

### Buggy code

```java
@Value("${app.url}")
private String url;
```

### Expected diagnosis

The property may exist only under a different profile or prefix; startup failure is clearer than a silent default.

### Corrected code

```java
@ConfigurationProperties(prefix = "app")
public record AppProperties(String url) {}
```

### Regression tests

```java
// Run with each profile and assert the expected URL is bound.
```

## SB3-E-052: missing starter dependency

- Difficulty: Easy
- Framework: Spring Boot 3
- Language: Java
- Perspective: Auto-configuration
- Concept: missing starter dependency
- Symptom: A configured feature has no bean at runtime.
- Diagnostic goal: Map the requested behavior to its Boot starter and auto-configuration.

### Buggy code

```java
@Bean
SecurityFilterChain chain(HttpSecurity http) { return http.build(); }
```

### Expected diagnosis

A security configuration cannot work if the relevant starter and transitive infrastructure are absent.

### Corrected code

```java
dependencies { implementation("org.springframework.boot:spring-boot-starter-security") }
```

### Regression tests

```java
// Include spring-boot-starter-security and assert the context starts.
```

## SB3-E-053: health endpoint exposes internals

- Difficulty: Easy
- Framework: Spring Boot 3
- Language: Java
- Perspective: Actuator
- Concept: health endpoint exposes internals
- Symptom: Operational endpoints leak sensitive details.
- Diagnostic goal: Separate endpoint exposure from health detail visibility.

### Buggy code

```java
management.endpoints.web.exposure.include=*
management.endpoint.health.show-details=always
```

### Expected diagnosis

Wildcard exposure and unrestricted details reveal environment and dependency information.

### Corrected code

```java
management.endpoints.web.exposure.include=health,info
management.endpoint.health.show-details=when_authorized
```

### Regression tests

```java
// Unauthenticated probes see status without credentials or connection details.
```

## SB3-E-054: test profile not activated

- Difficulty: Easy
- Framework: Spring Boot 3
- Language: Java
- Perspective: Profiles
- Concept: test profile not activated
- Symptom: Tests connect to a developer database.
- Diagnostic goal: Make the test environment explicit and isolated.

### Buggy code

```java
@SpringBootTest
class RepositoryTest {}
```

### Expected diagnosis

Without a test profile, normal application properties can select an external database.

### Corrected code

```java
@SpringBootTest
@ActiveProfiles("test")
class RepositoryTest {}
```

### Regression tests

```java
// Test execution uses the embedded or containerized test datasource.
```

## SB3-E-055: correlation id lost

- Difficulty: Easy
- Framework: Spring Boot 3
- Language: Java
- Perspective: Observability
- Concept: correlation id lost
- Symptom: Logs from one request cannot be joined across services.
- Diagnostic goal: Create and clear request-scoped diagnostic context.

### Buggy code

```java
filterChain.doFilter(request, response);
```

### Expected diagnosis

The request proceeds without installing a correlation value and without cleanup.

### Corrected code

```java
try { MDC.put("requestId", requestId); filterChain.doFilter(request, response); } finally { MDC.remove("requestId"); }
```

### Regression tests

```java
// Every log line has the request id and the thread is clean afterward.
```

## SB3-E-056: Java time format mismatch

- Difficulty: Easy
- Framework: Spring Boot 3
- Language: Java
- Perspective: Serialization
- Concept: Java time format mismatch
- Symptom: Clients reject the response date.
- Diagnostic goal: Declare the wire format at the API boundary.

### Buggy code

```java
record Event(Instant createdAt) {}
```

### Expected diagnosis

The default representation may differ from the documented contract or client expectation.

### Corrected code

```java
record Event(@JsonFormat(pattern = "yyyy-MM-dd'T'HH:mm:ssX") Instant createdAt) {}
```

### Regression tests

```java
// Contract test asserts the exact serialized timestamp.
```

## SB3-E-057: circular bean dependency

- Difficulty: Easy
- Framework: Spring Boot 3
- Language: Java
- Perspective: Startup
- Concept: circular bean dependency
- Symptom: ApplicationContext fails during startup.
- Diagnostic goal: Break the cycle at the architecture boundary.

### Buggy code

```java
class A { A(B b) {} }
class B { B(A a) {} }
```

### Expected diagnosis

Constructor injection exposes a cycle that cannot be resolved safely.

### Corrected code

```java
class A { A(Port port) {} }
class B implements Port { B() {} }
```

### Regression tests

```java
// Context starts and each service depends on an interface with one direction.
```

## SB3-E-058: unbounded upstream timeout

- Difficulty: Easy
- Framework: Spring Boot 3
- Language: Java
- Perspective: HTTP client
- Concept: unbounded upstream timeout
- Symptom: A slow dependency exhausts request threads.
- Diagnostic goal: Set connect and response timeouts and define fallback behavior.

### Buggy code

```java
return restClient.get().uri(uri).retrieve().body(String.class);
```

### Expected diagnosis

Without timeouts, an unavailable upstream can hold workers indefinitely.

### Corrected code

```java
return restClient.get().uri(uri).retrieve().onStatus(s -> s.value() == 404, r -> new NotFoundException()).body(String.class);
```

### Regression tests

```java
// Slow and error responses produce bounded, documented outcomes.
```

## SB3-E-059: graceful shutdown disabled

- Difficulty: Easy
- Framework: Spring Boot 3
- Language: Java
- Perspective: Deployment
- Concept: graceful shutdown disabled
- Symptom: In-flight requests are cut off during rollout.
- Diagnostic goal: Enable graceful shutdown and give the platform enough time.

### Buggy code

```java
server.shutdown=immediate
```

### Expected diagnosis

Immediate shutdown drops active requests and can interrupt transactions.

### Corrected code

```java
server.shutdown=graceful
spring.lifecycle.timeout-per-shutdown-phase=30s
```

### Regression tests

```java
// A shutdown waits for active work up to the configured deadline.
```

## SB3-E-060: configuration accepted without validation

- Difficulty: Easy
- Framework: Spring Boot 3
- Language: Java
- Perspective: Validation
- Concept: configuration accepted without validation
- Symptom: The app starts with an invalid port or URL.
- Diagnostic goal: Validate configuration at binding time.

### Buggy code

```java
record ClientProperties(String baseUrl, int timeoutMs) {}
```

### Expected diagnosis

Invalid values surface only when the first request is made.

### Corrected code

```java
record ClientProperties(@jakarta.validation.constraints.NotBlank String baseUrl, @jakarta.validation.constraints.Positive int timeoutMs) {}
```

### Regression tests

```java
// Invalid configuration fails context startup with a useful property path.
```

## SB3-E-061: profile property mismatch

- Difficulty: Easy
- Framework: Spring Boot 3
- Language: Java
- Perspective: Configuration
- Concept: profile property mismatch
- Symptom: The production datasource is not configured.
- Diagnostic goal: Trace active profiles and property source precedence.

### Buggy code

```java
@Value("${app.url}")
private String url;
```

### Expected diagnosis

The property may exist only under a different profile or prefix; startup failure is clearer than a silent default.

### Corrected code

```java
@ConfigurationProperties(prefix = "app")
public record AppProperties(String url) {}
```

### Regression tests

```java
// Run with each profile and assert the expected URL is bound.
```

## SB3-E-062: missing starter dependency

- Difficulty: Easy
- Framework: Spring Boot 3
- Language: Java
- Perspective: Auto-configuration
- Concept: missing starter dependency
- Symptom: A configured feature has no bean at runtime.
- Diagnostic goal: Map the requested behavior to its Boot starter and auto-configuration.

### Buggy code

```java
@Bean
SecurityFilterChain chain(HttpSecurity http) { return http.build(); }
```

### Expected diagnosis

A security configuration cannot work if the relevant starter and transitive infrastructure are absent.

### Corrected code

```java
dependencies { implementation("org.springframework.boot:spring-boot-starter-security") }
```

### Regression tests

```java
// Include spring-boot-starter-security and assert the context starts.
```

## SB3-E-063: health endpoint exposes internals

- Difficulty: Easy
- Framework: Spring Boot 3
- Language: Java
- Perspective: Actuator
- Concept: health endpoint exposes internals
- Symptom: Operational endpoints leak sensitive details.
- Diagnostic goal: Separate endpoint exposure from health detail visibility.

### Buggy code

```java
management.endpoints.web.exposure.include=*
management.endpoint.health.show-details=always
```

### Expected diagnosis

Wildcard exposure and unrestricted details reveal environment and dependency information.

### Corrected code

```java
management.endpoints.web.exposure.include=health,info
management.endpoint.health.show-details=when_authorized
```

### Regression tests

```java
// Unauthenticated probes see status without credentials or connection details.
```

## SB3-E-064: test profile not activated

- Difficulty: Easy
- Framework: Spring Boot 3
- Language: Java
- Perspective: Profiles
- Concept: test profile not activated
- Symptom: Tests connect to a developer database.
- Diagnostic goal: Make the test environment explicit and isolated.

### Buggy code

```java
@SpringBootTest
class RepositoryTest {}
```

### Expected diagnosis

Without a test profile, normal application properties can select an external database.

### Corrected code

```java
@SpringBootTest
@ActiveProfiles("test")
class RepositoryTest {}
```

### Regression tests

```java
// Test execution uses the embedded or containerized test datasource.
```

## SB3-E-065: correlation id lost

- Difficulty: Easy
- Framework: Spring Boot 3
- Language: Java
- Perspective: Observability
- Concept: correlation id lost
- Symptom: Logs from one request cannot be joined across services.
- Diagnostic goal: Create and clear request-scoped diagnostic context.

### Buggy code

```java
filterChain.doFilter(request, response);
```

### Expected diagnosis

The request proceeds without installing a correlation value and without cleanup.

### Corrected code

```java
try { MDC.put("requestId", requestId); filterChain.doFilter(request, response); } finally { MDC.remove("requestId"); }
```

### Regression tests

```java
// Every log line has the request id and the thread is clean afterward.
```

## SB3-E-066: Java time format mismatch

- Difficulty: Easy
- Framework: Spring Boot 3
- Language: Java
- Perspective: Serialization
- Concept: Java time format mismatch
- Symptom: Clients reject the response date.
- Diagnostic goal: Declare the wire format at the API boundary.

### Buggy code

```java
record Event(Instant createdAt) {}
```

### Expected diagnosis

The default representation may differ from the documented contract or client expectation.

### Corrected code

```java
record Event(@JsonFormat(pattern = "yyyy-MM-dd'T'HH:mm:ssX") Instant createdAt) {}
```

### Regression tests

```java
// Contract test asserts the exact serialized timestamp.
```

## SB3-E-067: circular bean dependency

- Difficulty: Easy
- Framework: Spring Boot 3
- Language: Java
- Perspective: Startup
- Concept: circular bean dependency
- Symptom: ApplicationContext fails during startup.
- Diagnostic goal: Break the cycle at the architecture boundary.

### Buggy code

```java
class A { A(B b) {} }
class B { B(A a) {} }
```

### Expected diagnosis

Constructor injection exposes a cycle that cannot be resolved safely.

### Corrected code

```java
class A { A(Port port) {} }
class B implements Port { B() {} }
```

### Regression tests

```java
// Context starts and each service depends on an interface with one direction.
```

## SB3-E-068: unbounded upstream timeout

- Difficulty: Easy
- Framework: Spring Boot 3
- Language: Java
- Perspective: HTTP client
- Concept: unbounded upstream timeout
- Symptom: A slow dependency exhausts request threads.
- Diagnostic goal: Set connect and response timeouts and define fallback behavior.

### Buggy code

```java
return restClient.get().uri(uri).retrieve().body(String.class);
```

### Expected diagnosis

Without timeouts, an unavailable upstream can hold workers indefinitely.

### Corrected code

```java
return restClient.get().uri(uri).retrieve().onStatus(s -> s.value() == 404, r -> new NotFoundException()).body(String.class);
```

### Regression tests

```java
// Slow and error responses produce bounded, documented outcomes.
```

## SB3-E-069: graceful shutdown disabled

- Difficulty: Easy
- Framework: Spring Boot 3
- Language: Java
- Perspective: Deployment
- Concept: graceful shutdown disabled
- Symptom: In-flight requests are cut off during rollout.
- Diagnostic goal: Enable graceful shutdown and give the platform enough time.

### Buggy code

```java
server.shutdown=immediate
```

### Expected diagnosis

Immediate shutdown drops active requests and can interrupt transactions.

### Corrected code

```java
server.shutdown=graceful
spring.lifecycle.timeout-per-shutdown-phase=30s
```

### Regression tests

```java
// A shutdown waits for active work up to the configured deadline.
```

## SB3-E-070: configuration accepted without validation

- Difficulty: Easy
- Framework: Spring Boot 3
- Language: Java
- Perspective: Validation
- Concept: configuration accepted without validation
- Symptom: The app starts with an invalid port or URL.
- Diagnostic goal: Validate configuration at binding time.

### Buggy code

```java
record ClientProperties(String baseUrl, int timeoutMs) {}
```

### Expected diagnosis

Invalid values surface only when the first request is made.

### Corrected code

```java
record ClientProperties(@jakarta.validation.constraints.NotBlank String baseUrl, @jakarta.validation.constraints.Positive int timeoutMs) {}
```

### Regression tests

```java
// Invalid configuration fails context startup with a useful property path.
```

## SB3-E-071: profile property mismatch

- Difficulty: Easy
- Framework: Spring Boot 3
- Language: Java
- Perspective: Configuration
- Concept: profile property mismatch
- Symptom: The production datasource is not configured.
- Diagnostic goal: Trace active profiles and property source precedence.

### Buggy code

```java
@Value("${app.url}")
private String url;
```

### Expected diagnosis

The property may exist only under a different profile or prefix; startup failure is clearer than a silent default.

### Corrected code

```java
@ConfigurationProperties(prefix = "app")
public record AppProperties(String url) {}
```

### Regression tests

```java
// Run with each profile and assert the expected URL is bound.
```

## SB3-E-072: missing starter dependency

- Difficulty: Easy
- Framework: Spring Boot 3
- Language: Java
- Perspective: Auto-configuration
- Concept: missing starter dependency
- Symptom: A configured feature has no bean at runtime.
- Diagnostic goal: Map the requested behavior to its Boot starter and auto-configuration.

### Buggy code

```java
@Bean
SecurityFilterChain chain(HttpSecurity http) { return http.build(); }
```

### Expected diagnosis

A security configuration cannot work if the relevant starter and transitive infrastructure are absent.

### Corrected code

```java
dependencies { implementation("org.springframework.boot:spring-boot-starter-security") }
```

### Regression tests

```java
// Include spring-boot-starter-security and assert the context starts.
```

## SB3-E-073: health endpoint exposes internals

- Difficulty: Easy
- Framework: Spring Boot 3
- Language: Java
- Perspective: Actuator
- Concept: health endpoint exposes internals
- Symptom: Operational endpoints leak sensitive details.
- Diagnostic goal: Separate endpoint exposure from health detail visibility.

### Buggy code

```java
management.endpoints.web.exposure.include=*
management.endpoint.health.show-details=always
```

### Expected diagnosis

Wildcard exposure and unrestricted details reveal environment and dependency information.

### Corrected code

```java
management.endpoints.web.exposure.include=health,info
management.endpoint.health.show-details=when_authorized
```

### Regression tests

```java
// Unauthenticated probes see status without credentials or connection details.
```

## SB3-E-074: test profile not activated

- Difficulty: Easy
- Framework: Spring Boot 3
- Language: Java
- Perspective: Profiles
- Concept: test profile not activated
- Symptom: Tests connect to a developer database.
- Diagnostic goal: Make the test environment explicit and isolated.

### Buggy code

```java
@SpringBootTest
class RepositoryTest {}
```

### Expected diagnosis

Without a test profile, normal application properties can select an external database.

### Corrected code

```java
@SpringBootTest
@ActiveProfiles("test")
class RepositoryTest {}
```

### Regression tests

```java
// Test execution uses the embedded or containerized test datasource.
```

## SB3-E-075: correlation id lost

- Difficulty: Easy
- Framework: Spring Boot 3
- Language: Java
- Perspective: Observability
- Concept: correlation id lost
- Symptom: Logs from one request cannot be joined across services.
- Diagnostic goal: Create and clear request-scoped diagnostic context.

### Buggy code

```java
filterChain.doFilter(request, response);
```

### Expected diagnosis

The request proceeds without installing a correlation value and without cleanup.

### Corrected code

```java
try { MDC.put("requestId", requestId); filterChain.doFilter(request, response); } finally { MDC.remove("requestId"); }
```

### Regression tests

```java
// Every log line has the request id and the thread is clean afterward.
```

## SB3-E-076: Java time format mismatch

- Difficulty: Easy
- Framework: Spring Boot 3
- Language: Java
- Perspective: Serialization
- Concept: Java time format mismatch
- Symptom: Clients reject the response date.
- Diagnostic goal: Declare the wire format at the API boundary.

### Buggy code

```java
record Event(Instant createdAt) {}
```

### Expected diagnosis

The default representation may differ from the documented contract or client expectation.

### Corrected code

```java
record Event(@JsonFormat(pattern = "yyyy-MM-dd'T'HH:mm:ssX") Instant createdAt) {}
```

### Regression tests

```java
// Contract test asserts the exact serialized timestamp.
```

## SB3-E-077: circular bean dependency

- Difficulty: Easy
- Framework: Spring Boot 3
- Language: Java
- Perspective: Startup
- Concept: circular bean dependency
- Symptom: ApplicationContext fails during startup.
- Diagnostic goal: Break the cycle at the architecture boundary.

### Buggy code

```java
class A { A(B b) {} }
class B { B(A a) {} }
```

### Expected diagnosis

Constructor injection exposes a cycle that cannot be resolved safely.

### Corrected code

```java
class A { A(Port port) {} }
class B implements Port { B() {} }
```

### Regression tests

```java
// Context starts and each service depends on an interface with one direction.
```

## SB3-E-078: unbounded upstream timeout

- Difficulty: Easy
- Framework: Spring Boot 3
- Language: Java
- Perspective: HTTP client
- Concept: unbounded upstream timeout
- Symptom: A slow dependency exhausts request threads.
- Diagnostic goal: Set connect and response timeouts and define fallback behavior.

### Buggy code

```java
return restClient.get().uri(uri).retrieve().body(String.class);
```

### Expected diagnosis

Without timeouts, an unavailable upstream can hold workers indefinitely.

### Corrected code

```java
return restClient.get().uri(uri).retrieve().onStatus(s -> s.value() == 404, r -> new NotFoundException()).body(String.class);
```

### Regression tests

```java
// Slow and error responses produce bounded, documented outcomes.
```

## SB3-E-079: graceful shutdown disabled

- Difficulty: Easy
- Framework: Spring Boot 3
- Language: Java
- Perspective: Deployment
- Concept: graceful shutdown disabled
- Symptom: In-flight requests are cut off during rollout.
- Diagnostic goal: Enable graceful shutdown and give the platform enough time.

### Buggy code

```java
server.shutdown=immediate
```

### Expected diagnosis

Immediate shutdown drops active requests and can interrupt transactions.

### Corrected code

```java
server.shutdown=graceful
spring.lifecycle.timeout-per-shutdown-phase=30s
```

### Regression tests

```java
// A shutdown waits for active work up to the configured deadline.
```

## SB3-E-080: configuration accepted without validation

- Difficulty: Easy
- Framework: Spring Boot 3
- Language: Java
- Perspective: Validation
- Concept: configuration accepted without validation
- Symptom: The app starts with an invalid port or URL.
- Diagnostic goal: Validate configuration at binding time.

### Buggy code

```java
record ClientProperties(String baseUrl, int timeoutMs) {}
```

### Expected diagnosis

Invalid values surface only when the first request is made.

### Corrected code

```java
record ClientProperties(@jakarta.validation.constraints.NotBlank String baseUrl, @jakarta.validation.constraints.Positive int timeoutMs) {}
```

### Regression tests

```java
// Invalid configuration fails context startup with a useful property path.
```

## SB3-E-081: profile property mismatch

- Difficulty: Easy
- Framework: Spring Boot 3
- Language: Java
- Perspective: Configuration
- Concept: profile property mismatch
- Symptom: The production datasource is not configured.
- Diagnostic goal: Trace active profiles and property source precedence.

### Buggy code

```java
@Value("${app.url}")
private String url;
```

### Expected diagnosis

The property may exist only under a different profile or prefix; startup failure is clearer than a silent default.

### Corrected code

```java
@ConfigurationProperties(prefix = "app")
public record AppProperties(String url) {}
```

### Regression tests

```java
// Run with each profile and assert the expected URL is bound.
```

## SB3-E-082: missing starter dependency

- Difficulty: Easy
- Framework: Spring Boot 3
- Language: Java
- Perspective: Auto-configuration
- Concept: missing starter dependency
- Symptom: A configured feature has no bean at runtime.
- Diagnostic goal: Map the requested behavior to its Boot starter and auto-configuration.

### Buggy code

```java
@Bean
SecurityFilterChain chain(HttpSecurity http) { return http.build(); }
```

### Expected diagnosis

A security configuration cannot work if the relevant starter and transitive infrastructure are absent.

### Corrected code

```java
dependencies { implementation("org.springframework.boot:spring-boot-starter-security") }
```

### Regression tests

```java
// Include spring-boot-starter-security and assert the context starts.
```

## SB3-E-083: health endpoint exposes internals

- Difficulty: Easy
- Framework: Spring Boot 3
- Language: Java
- Perspective: Actuator
- Concept: health endpoint exposes internals
- Symptom: Operational endpoints leak sensitive details.
- Diagnostic goal: Separate endpoint exposure from health detail visibility.

### Buggy code

```java
management.endpoints.web.exposure.include=*
management.endpoint.health.show-details=always
```

### Expected diagnosis

Wildcard exposure and unrestricted details reveal environment and dependency information.

### Corrected code

```java
management.endpoints.web.exposure.include=health,info
management.endpoint.health.show-details=when_authorized
```

### Regression tests

```java
// Unauthenticated probes see status without credentials or connection details.
```

## SB3-E-084: test profile not activated

- Difficulty: Easy
- Framework: Spring Boot 3
- Language: Java
- Perspective: Profiles
- Concept: test profile not activated
- Symptom: Tests connect to a developer database.
- Diagnostic goal: Make the test environment explicit and isolated.

### Buggy code

```java
@SpringBootTest
class RepositoryTest {}
```

### Expected diagnosis

Without a test profile, normal application properties can select an external database.

### Corrected code

```java
@SpringBootTest
@ActiveProfiles("test")
class RepositoryTest {}
```

### Regression tests

```java
// Test execution uses the embedded or containerized test datasource.
```

## SB3-E-085: correlation id lost

- Difficulty: Easy
- Framework: Spring Boot 3
- Language: Java
- Perspective: Observability
- Concept: correlation id lost
- Symptom: Logs from one request cannot be joined across services.
- Diagnostic goal: Create and clear request-scoped diagnostic context.

### Buggy code

```java
filterChain.doFilter(request, response);
```

### Expected diagnosis

The request proceeds without installing a correlation value and without cleanup.

### Corrected code

```java
try { MDC.put("requestId", requestId); filterChain.doFilter(request, response); } finally { MDC.remove("requestId"); }
```

### Regression tests

```java
// Every log line has the request id and the thread is clean afterward.
```

## SB3-E-086: Java time format mismatch

- Difficulty: Easy
- Framework: Spring Boot 3
- Language: Java
- Perspective: Serialization
- Concept: Java time format mismatch
- Symptom: Clients reject the response date.
- Diagnostic goal: Declare the wire format at the API boundary.

### Buggy code

```java
record Event(Instant createdAt) {}
```

### Expected diagnosis

The default representation may differ from the documented contract or client expectation.

### Corrected code

```java
record Event(@JsonFormat(pattern = "yyyy-MM-dd'T'HH:mm:ssX") Instant createdAt) {}
```

### Regression tests

```java
// Contract test asserts the exact serialized timestamp.
```

## SB3-E-087: circular bean dependency

- Difficulty: Easy
- Framework: Spring Boot 3
- Language: Java
- Perspective: Startup
- Concept: circular bean dependency
- Symptom: ApplicationContext fails during startup.
- Diagnostic goal: Break the cycle at the architecture boundary.

### Buggy code

```java
class A { A(B b) {} }
class B { B(A a) {} }
```

### Expected diagnosis

Constructor injection exposes a cycle that cannot be resolved safely.

### Corrected code

```java
class A { A(Port port) {} }
class B implements Port { B() {} }
```

### Regression tests

```java
// Context starts and each service depends on an interface with one direction.
```

## SB3-E-088: unbounded upstream timeout

- Difficulty: Easy
- Framework: Spring Boot 3
- Language: Java
- Perspective: HTTP client
- Concept: unbounded upstream timeout
- Symptom: A slow dependency exhausts request threads.
- Diagnostic goal: Set connect and response timeouts and define fallback behavior.

### Buggy code

```java
return restClient.get().uri(uri).retrieve().body(String.class);
```

### Expected diagnosis

Without timeouts, an unavailable upstream can hold workers indefinitely.

### Corrected code

```java
return restClient.get().uri(uri).retrieve().onStatus(s -> s.value() == 404, r -> new NotFoundException()).body(String.class);
```

### Regression tests

```java
// Slow and error responses produce bounded, documented outcomes.
```

## SB3-E-089: graceful shutdown disabled

- Difficulty: Easy
- Framework: Spring Boot 3
- Language: Java
- Perspective: Deployment
- Concept: graceful shutdown disabled
- Symptom: In-flight requests are cut off during rollout.
- Diagnostic goal: Enable graceful shutdown and give the platform enough time.

### Buggy code

```java
server.shutdown=immediate
```

### Expected diagnosis

Immediate shutdown drops active requests and can interrupt transactions.

### Corrected code

```java
server.shutdown=graceful
spring.lifecycle.timeout-per-shutdown-phase=30s
```

### Regression tests

```java
// A shutdown waits for active work up to the configured deadline.
```

## SB3-E-090: configuration accepted without validation

- Difficulty: Easy
- Framework: Spring Boot 3
- Language: Java
- Perspective: Validation
- Concept: configuration accepted without validation
- Symptom: The app starts with an invalid port or URL.
- Diagnostic goal: Validate configuration at binding time.

### Buggy code

```java
record ClientProperties(String baseUrl, int timeoutMs) {}
```

### Expected diagnosis

Invalid values surface only when the first request is made.

### Corrected code

```java
record ClientProperties(@jakarta.validation.constraints.NotBlank String baseUrl, @jakarta.validation.constraints.Positive int timeoutMs) {}
```

### Regression tests

```java
// Invalid configuration fails context startup with a useful property path.
```

## SB3-E-091: profile property mismatch

- Difficulty: Easy
- Framework: Spring Boot 3
- Language: Java
- Perspective: Configuration
- Concept: profile property mismatch
- Symptom: The production datasource is not configured.
- Diagnostic goal: Trace active profiles and property source precedence.

### Buggy code

```java
@Value("${app.url}")
private String url;
```

### Expected diagnosis

The property may exist only under a different profile or prefix; startup failure is clearer than a silent default.

### Corrected code

```java
@ConfigurationProperties(prefix = "app")
public record AppProperties(String url) {}
```

### Regression tests

```java
// Run with each profile and assert the expected URL is bound.
```

## SB3-E-092: missing starter dependency

- Difficulty: Easy
- Framework: Spring Boot 3
- Language: Java
- Perspective: Auto-configuration
- Concept: missing starter dependency
- Symptom: A configured feature has no bean at runtime.
- Diagnostic goal: Map the requested behavior to its Boot starter and auto-configuration.

### Buggy code

```java
@Bean
SecurityFilterChain chain(HttpSecurity http) { return http.build(); }
```

### Expected diagnosis

A security configuration cannot work if the relevant starter and transitive infrastructure are absent.

### Corrected code

```java
dependencies { implementation("org.springframework.boot:spring-boot-starter-security") }
```

### Regression tests

```java
// Include spring-boot-starter-security and assert the context starts.
```

## SB3-E-093: health endpoint exposes internals

- Difficulty: Easy
- Framework: Spring Boot 3
- Language: Java
- Perspective: Actuator
- Concept: health endpoint exposes internals
- Symptom: Operational endpoints leak sensitive details.
- Diagnostic goal: Separate endpoint exposure from health detail visibility.

### Buggy code

```java
management.endpoints.web.exposure.include=*
management.endpoint.health.show-details=always
```

### Expected diagnosis

Wildcard exposure and unrestricted details reveal environment and dependency information.

### Corrected code

```java
management.endpoints.web.exposure.include=health,info
management.endpoint.health.show-details=when_authorized
```

### Regression tests

```java
// Unauthenticated probes see status without credentials or connection details.
```

## SB3-E-094: test profile not activated

- Difficulty: Easy
- Framework: Spring Boot 3
- Language: Java
- Perspective: Profiles
- Concept: test profile not activated
- Symptom: Tests connect to a developer database.
- Diagnostic goal: Make the test environment explicit and isolated.

### Buggy code

```java
@SpringBootTest
class RepositoryTest {}
```

### Expected diagnosis

Without a test profile, normal application properties can select an external database.

### Corrected code

```java
@SpringBootTest
@ActiveProfiles("test")
class RepositoryTest {}
```

### Regression tests

```java
// Test execution uses the embedded or containerized test datasource.
```

## SB3-E-095: correlation id lost

- Difficulty: Easy
- Framework: Spring Boot 3
- Language: Java
- Perspective: Observability
- Concept: correlation id lost
- Symptom: Logs from one request cannot be joined across services.
- Diagnostic goal: Create and clear request-scoped diagnostic context.

### Buggy code

```java
filterChain.doFilter(request, response);
```

### Expected diagnosis

The request proceeds without installing a correlation value and without cleanup.

### Corrected code

```java
try { MDC.put("requestId", requestId); filterChain.doFilter(request, response); } finally { MDC.remove("requestId"); }
```

### Regression tests

```java
// Every log line has the request id and the thread is clean afterward.
```

## SB3-E-096: Java time format mismatch

- Difficulty: Easy
- Framework: Spring Boot 3
- Language: Java
- Perspective: Serialization
- Concept: Java time format mismatch
- Symptom: Clients reject the response date.
- Diagnostic goal: Declare the wire format at the API boundary.

### Buggy code

```java
record Event(Instant createdAt) {}
```

### Expected diagnosis

The default representation may differ from the documented contract or client expectation.

### Corrected code

```java
record Event(@JsonFormat(pattern = "yyyy-MM-dd'T'HH:mm:ssX") Instant createdAt) {}
```

### Regression tests

```java
// Contract test asserts the exact serialized timestamp.
```

## SB3-E-097: circular bean dependency

- Difficulty: Easy
- Framework: Spring Boot 3
- Language: Java
- Perspective: Startup
- Concept: circular bean dependency
- Symptom: ApplicationContext fails during startup.
- Diagnostic goal: Break the cycle at the architecture boundary.

### Buggy code

```java
class A { A(B b) {} }
class B { B(A a) {} }
```

### Expected diagnosis

Constructor injection exposes a cycle that cannot be resolved safely.

### Corrected code

```java
class A { A(Port port) {} }
class B implements Port { B() {} }
```

### Regression tests

```java
// Context starts and each service depends on an interface with one direction.
```

## SB3-E-098: unbounded upstream timeout

- Difficulty: Easy
- Framework: Spring Boot 3
- Language: Java
- Perspective: HTTP client
- Concept: unbounded upstream timeout
- Symptom: A slow dependency exhausts request threads.
- Diagnostic goal: Set connect and response timeouts and define fallback behavior.

### Buggy code

```java
return restClient.get().uri(uri).retrieve().body(String.class);
```

### Expected diagnosis

Without timeouts, an unavailable upstream can hold workers indefinitely.

### Corrected code

```java
return restClient.get().uri(uri).retrieve().onStatus(s -> s.value() == 404, r -> new NotFoundException()).body(String.class);
```

### Regression tests

```java
// Slow and error responses produce bounded, documented outcomes.
```

## SB3-E-099: graceful shutdown disabled

- Difficulty: Easy
- Framework: Spring Boot 3
- Language: Java
- Perspective: Deployment
- Concept: graceful shutdown disabled
- Symptom: In-flight requests are cut off during rollout.
- Diagnostic goal: Enable graceful shutdown and give the platform enough time.

### Buggy code

```java
server.shutdown=immediate
```

### Expected diagnosis

Immediate shutdown drops active requests and can interrupt transactions.

### Corrected code

```java
server.shutdown=graceful
spring.lifecycle.timeout-per-shutdown-phase=30s
```

### Regression tests

```java
// A shutdown waits for active work up to the configured deadline.
```

## SB3-E-100: configuration accepted without validation

- Difficulty: Easy
- Framework: Spring Boot 3
- Language: Java
- Perspective: Validation
- Concept: configuration accepted without validation
- Symptom: The app starts with an invalid port or URL.
- Diagnostic goal: Validate configuration at binding time.

### Buggy code

```java
record ClientProperties(String baseUrl, int timeoutMs) {}
```

### Expected diagnosis

Invalid values surface only when the first request is made.

### Corrected code

```java
record ClientProperties(@jakarta.validation.constraints.NotBlank String baseUrl, @jakarta.validation.constraints.Positive int timeoutMs) {}
```

### Regression tests

```java
// Invalid configuration fails context startup with a useful property path.
```

## SB3-M-001: profile property mismatch

- Difficulty: Medium
- Framework: Spring Boot 3
- Language: Java
- Perspective: Configuration
- Concept: profile property mismatch
- Symptom: The production datasource is not configured.
- Diagnostic goal: Trace active profiles and property source precedence.

### Buggy code

```java
@Value("${app.url}")
private String url;
```

### Expected diagnosis

The property may exist only under a different profile or prefix; startup failure is clearer than a silent default.

### Corrected code

```java
@ConfigurationProperties(prefix = "app")
public record AppProperties(String url) {}
```

### Regression tests

```java
// Run with each profile and assert the expected URL is bound.
```

## SB3-M-002: missing starter dependency

- Difficulty: Medium
- Framework: Spring Boot 3
- Language: Java
- Perspective: Auto-configuration
- Concept: missing starter dependency
- Symptom: A configured feature has no bean at runtime.
- Diagnostic goal: Map the requested behavior to its Boot starter and auto-configuration.

### Buggy code

```java
@Bean
SecurityFilterChain chain(HttpSecurity http) { return http.build(); }
```

### Expected diagnosis

A security configuration cannot work if the relevant starter and transitive infrastructure are absent.

### Corrected code

```java
dependencies { implementation("org.springframework.boot:spring-boot-starter-security") }
```

### Regression tests

```java
// Include spring-boot-starter-security and assert the context starts.
```

## SB3-M-003: health endpoint exposes internals

- Difficulty: Medium
- Framework: Spring Boot 3
- Language: Java
- Perspective: Actuator
- Concept: health endpoint exposes internals
- Symptom: Operational endpoints leak sensitive details.
- Diagnostic goal: Separate endpoint exposure from health detail visibility.

### Buggy code

```java
management.endpoints.web.exposure.include=*
management.endpoint.health.show-details=always
```

### Expected diagnosis

Wildcard exposure and unrestricted details reveal environment and dependency information.

### Corrected code

```java
management.endpoints.web.exposure.include=health,info
management.endpoint.health.show-details=when_authorized
```

### Regression tests

```java
// Unauthenticated probes see status without credentials or connection details.
```

## SB3-M-004: test profile not activated

- Difficulty: Medium
- Framework: Spring Boot 3
- Language: Java
- Perspective: Profiles
- Concept: test profile not activated
- Symptom: Tests connect to a developer database.
- Diagnostic goal: Make the test environment explicit and isolated.

### Buggy code

```java
@SpringBootTest
class RepositoryTest {}
```

### Expected diagnosis

Without a test profile, normal application properties can select an external database.

### Corrected code

```java
@SpringBootTest
@ActiveProfiles("test")
class RepositoryTest {}
```

### Regression tests

```java
// Test execution uses the embedded or containerized test datasource.
```

## SB3-M-005: correlation id lost

- Difficulty: Medium
- Framework: Spring Boot 3
- Language: Java
- Perspective: Observability
- Concept: correlation id lost
- Symptom: Logs from one request cannot be joined across services.
- Diagnostic goal: Create and clear request-scoped diagnostic context.

### Buggy code

```java
filterChain.doFilter(request, response);
```

### Expected diagnosis

The request proceeds without installing a correlation value and without cleanup.

### Corrected code

```java
try { MDC.put("requestId", requestId); filterChain.doFilter(request, response); } finally { MDC.remove("requestId"); }
```

### Regression tests

```java
// Every log line has the request id and the thread is clean afterward.
```

## SB3-M-006: Java time format mismatch

- Difficulty: Medium
- Framework: Spring Boot 3
- Language: Java
- Perspective: Serialization
- Concept: Java time format mismatch
- Symptom: Clients reject the response date.
- Diagnostic goal: Declare the wire format at the API boundary.

### Buggy code

```java
record Event(Instant createdAt) {}
```

### Expected diagnosis

The default representation may differ from the documented contract or client expectation.

### Corrected code

```java
record Event(@JsonFormat(pattern = "yyyy-MM-dd'T'HH:mm:ssX") Instant createdAt) {}
```

### Regression tests

```java
// Contract test asserts the exact serialized timestamp.
```

## SB3-M-007: circular bean dependency

- Difficulty: Medium
- Framework: Spring Boot 3
- Language: Java
- Perspective: Startup
- Concept: circular bean dependency
- Symptom: ApplicationContext fails during startup.
- Diagnostic goal: Break the cycle at the architecture boundary.

### Buggy code

```java
class A { A(B b) {} }
class B { B(A a) {} }
```

### Expected diagnosis

Constructor injection exposes a cycle that cannot be resolved safely.

### Corrected code

```java
class A { A(Port port) {} }
class B implements Port { B() {} }
```

### Regression tests

```java
// Context starts and each service depends on an interface with one direction.
```

## SB3-M-008: unbounded upstream timeout

- Difficulty: Medium
- Framework: Spring Boot 3
- Language: Java
- Perspective: HTTP client
- Concept: unbounded upstream timeout
- Symptom: A slow dependency exhausts request threads.
- Diagnostic goal: Set connect and response timeouts and define fallback behavior.

### Buggy code

```java
return restClient.get().uri(uri).retrieve().body(String.class);
```

### Expected diagnosis

Without timeouts, an unavailable upstream can hold workers indefinitely.

### Corrected code

```java
return restClient.get().uri(uri).retrieve().onStatus(s -> s.value() == 404, r -> new NotFoundException()).body(String.class);
```

### Regression tests

```java
// Slow and error responses produce bounded, documented outcomes.
```

## SB3-M-009: graceful shutdown disabled

- Difficulty: Medium
- Framework: Spring Boot 3
- Language: Java
- Perspective: Deployment
- Concept: graceful shutdown disabled
- Symptom: In-flight requests are cut off during rollout.
- Diagnostic goal: Enable graceful shutdown and give the platform enough time.

### Buggy code

```java
server.shutdown=immediate
```

### Expected diagnosis

Immediate shutdown drops active requests and can interrupt transactions.

### Corrected code

```java
server.shutdown=graceful
spring.lifecycle.timeout-per-shutdown-phase=30s
```

### Regression tests

```java
// A shutdown waits for active work up to the configured deadline.
```

## SB3-M-010: configuration accepted without validation

- Difficulty: Medium
- Framework: Spring Boot 3
- Language: Java
- Perspective: Validation
- Concept: configuration accepted without validation
- Symptom: The app starts with an invalid port or URL.
- Diagnostic goal: Validate configuration at binding time.

### Buggy code

```java
record ClientProperties(String baseUrl, int timeoutMs) {}
```

### Expected diagnosis

Invalid values surface only when the first request is made.

### Corrected code

```java
record ClientProperties(@jakarta.validation.constraints.NotBlank String baseUrl, @jakarta.validation.constraints.Positive int timeoutMs) {}
```

### Regression tests

```java
// Invalid configuration fails context startup with a useful property path.
```

## SB3-M-011: profile property mismatch

- Difficulty: Medium
- Framework: Spring Boot 3
- Language: Java
- Perspective: Configuration
- Concept: profile property mismatch
- Symptom: The production datasource is not configured.
- Diagnostic goal: Trace active profiles and property source precedence.

### Buggy code

```java
@Value("${app.url}")
private String url;
```

### Expected diagnosis

The property may exist only under a different profile or prefix; startup failure is clearer than a silent default.

### Corrected code

```java
@ConfigurationProperties(prefix = "app")
public record AppProperties(String url) {}
```

### Regression tests

```java
// Run with each profile and assert the expected URL is bound.
```

## SB3-M-012: missing starter dependency

- Difficulty: Medium
- Framework: Spring Boot 3
- Language: Java
- Perspective: Auto-configuration
- Concept: missing starter dependency
- Symptom: A configured feature has no bean at runtime.
- Diagnostic goal: Map the requested behavior to its Boot starter and auto-configuration.

### Buggy code

```java
@Bean
SecurityFilterChain chain(HttpSecurity http) { return http.build(); }
```

### Expected diagnosis

A security configuration cannot work if the relevant starter and transitive infrastructure are absent.

### Corrected code

```java
dependencies { implementation("org.springframework.boot:spring-boot-starter-security") }
```

### Regression tests

```java
// Include spring-boot-starter-security and assert the context starts.
```

## SB3-M-013: health endpoint exposes internals

- Difficulty: Medium
- Framework: Spring Boot 3
- Language: Java
- Perspective: Actuator
- Concept: health endpoint exposes internals
- Symptom: Operational endpoints leak sensitive details.
- Diagnostic goal: Separate endpoint exposure from health detail visibility.

### Buggy code

```java
management.endpoints.web.exposure.include=*
management.endpoint.health.show-details=always
```

### Expected diagnosis

Wildcard exposure and unrestricted details reveal environment and dependency information.

### Corrected code

```java
management.endpoints.web.exposure.include=health,info
management.endpoint.health.show-details=when_authorized
```

### Regression tests

```java
// Unauthenticated probes see status without credentials or connection details.
```

## SB3-M-014: test profile not activated

- Difficulty: Medium
- Framework: Spring Boot 3
- Language: Java
- Perspective: Profiles
- Concept: test profile not activated
- Symptom: Tests connect to a developer database.
- Diagnostic goal: Make the test environment explicit and isolated.

### Buggy code

```java
@SpringBootTest
class RepositoryTest {}
```

### Expected diagnosis

Without a test profile, normal application properties can select an external database.

### Corrected code

```java
@SpringBootTest
@ActiveProfiles("test")
class RepositoryTest {}
```

### Regression tests

```java
// Test execution uses the embedded or containerized test datasource.
```

## SB3-M-015: correlation id lost

- Difficulty: Medium
- Framework: Spring Boot 3
- Language: Java
- Perspective: Observability
- Concept: correlation id lost
- Symptom: Logs from one request cannot be joined across services.
- Diagnostic goal: Create and clear request-scoped diagnostic context.

### Buggy code

```java
filterChain.doFilter(request, response);
```

### Expected diagnosis

The request proceeds without installing a correlation value and without cleanup.

### Corrected code

```java
try { MDC.put("requestId", requestId); filterChain.doFilter(request, response); } finally { MDC.remove("requestId"); }
```

### Regression tests

```java
// Every log line has the request id and the thread is clean afterward.
```

## SB3-M-016: Java time format mismatch

- Difficulty: Medium
- Framework: Spring Boot 3
- Language: Java
- Perspective: Serialization
- Concept: Java time format mismatch
- Symptom: Clients reject the response date.
- Diagnostic goal: Declare the wire format at the API boundary.

### Buggy code

```java
record Event(Instant createdAt) {}
```

### Expected diagnosis

The default representation may differ from the documented contract or client expectation.

### Corrected code

```java
record Event(@JsonFormat(pattern = "yyyy-MM-dd'T'HH:mm:ssX") Instant createdAt) {}
```

### Regression tests

```java
// Contract test asserts the exact serialized timestamp.
```

## SB3-M-017: circular bean dependency

- Difficulty: Medium
- Framework: Spring Boot 3
- Language: Java
- Perspective: Startup
- Concept: circular bean dependency
- Symptom: ApplicationContext fails during startup.
- Diagnostic goal: Break the cycle at the architecture boundary.

### Buggy code

```java
class A { A(B b) {} }
class B { B(A a) {} }
```

### Expected diagnosis

Constructor injection exposes a cycle that cannot be resolved safely.

### Corrected code

```java
class A { A(Port port) {} }
class B implements Port { B() {} }
```

### Regression tests

```java
// Context starts and each service depends on an interface with one direction.
```

## SB3-M-018: unbounded upstream timeout

- Difficulty: Medium
- Framework: Spring Boot 3
- Language: Java
- Perspective: HTTP client
- Concept: unbounded upstream timeout
- Symptom: A slow dependency exhausts request threads.
- Diagnostic goal: Set connect and response timeouts and define fallback behavior.

### Buggy code

```java
return restClient.get().uri(uri).retrieve().body(String.class);
```

### Expected diagnosis

Without timeouts, an unavailable upstream can hold workers indefinitely.

### Corrected code

```java
return restClient.get().uri(uri).retrieve().onStatus(s -> s.value() == 404, r -> new NotFoundException()).body(String.class);
```

### Regression tests

```java
// Slow and error responses produce bounded, documented outcomes.
```

## SB3-M-019: graceful shutdown disabled

- Difficulty: Medium
- Framework: Spring Boot 3
- Language: Java
- Perspective: Deployment
- Concept: graceful shutdown disabled
- Symptom: In-flight requests are cut off during rollout.
- Diagnostic goal: Enable graceful shutdown and give the platform enough time.

### Buggy code

```java
server.shutdown=immediate
```

### Expected diagnosis

Immediate shutdown drops active requests and can interrupt transactions.

### Corrected code

```java
server.shutdown=graceful
spring.lifecycle.timeout-per-shutdown-phase=30s
```

### Regression tests

```java
// A shutdown waits for active work up to the configured deadline.
```

## SB3-M-020: configuration accepted without validation

- Difficulty: Medium
- Framework: Spring Boot 3
- Language: Java
- Perspective: Validation
- Concept: configuration accepted without validation
- Symptom: The app starts with an invalid port or URL.
- Diagnostic goal: Validate configuration at binding time.

### Buggy code

```java
record ClientProperties(String baseUrl, int timeoutMs) {}
```

### Expected diagnosis

Invalid values surface only when the first request is made.

### Corrected code

```java
record ClientProperties(@jakarta.validation.constraints.NotBlank String baseUrl, @jakarta.validation.constraints.Positive int timeoutMs) {}
```

### Regression tests

```java
// Invalid configuration fails context startup with a useful property path.
```

## SB3-M-021: profile property mismatch

- Difficulty: Medium
- Framework: Spring Boot 3
- Language: Java
- Perspective: Configuration
- Concept: profile property mismatch
- Symptom: The production datasource is not configured.
- Diagnostic goal: Trace active profiles and property source precedence.

### Buggy code

```java
@Value("${app.url}")
private String url;
```

### Expected diagnosis

The property may exist only under a different profile or prefix; startup failure is clearer than a silent default.

### Corrected code

```java
@ConfigurationProperties(prefix = "app")
public record AppProperties(String url) {}
```

### Regression tests

```java
// Run with each profile and assert the expected URL is bound.
```

## SB3-M-022: missing starter dependency

- Difficulty: Medium
- Framework: Spring Boot 3
- Language: Java
- Perspective: Auto-configuration
- Concept: missing starter dependency
- Symptom: A configured feature has no bean at runtime.
- Diagnostic goal: Map the requested behavior to its Boot starter and auto-configuration.

### Buggy code

```java
@Bean
SecurityFilterChain chain(HttpSecurity http) { return http.build(); }
```

### Expected diagnosis

A security configuration cannot work if the relevant starter and transitive infrastructure are absent.

### Corrected code

```java
dependencies { implementation("org.springframework.boot:spring-boot-starter-security") }
```

### Regression tests

```java
// Include spring-boot-starter-security and assert the context starts.
```

## SB3-M-023: health endpoint exposes internals

- Difficulty: Medium
- Framework: Spring Boot 3
- Language: Java
- Perspective: Actuator
- Concept: health endpoint exposes internals
- Symptom: Operational endpoints leak sensitive details.
- Diagnostic goal: Separate endpoint exposure from health detail visibility.

### Buggy code

```java
management.endpoints.web.exposure.include=*
management.endpoint.health.show-details=always
```

### Expected diagnosis

Wildcard exposure and unrestricted details reveal environment and dependency information.

### Corrected code

```java
management.endpoints.web.exposure.include=health,info
management.endpoint.health.show-details=when_authorized
```

### Regression tests

```java
// Unauthenticated probes see status without credentials or connection details.
```

## SB3-M-024: test profile not activated

- Difficulty: Medium
- Framework: Spring Boot 3
- Language: Java
- Perspective: Profiles
- Concept: test profile not activated
- Symptom: Tests connect to a developer database.
- Diagnostic goal: Make the test environment explicit and isolated.

### Buggy code

```java
@SpringBootTest
class RepositoryTest {}
```

### Expected diagnosis

Without a test profile, normal application properties can select an external database.

### Corrected code

```java
@SpringBootTest
@ActiveProfiles("test")
class RepositoryTest {}
```

### Regression tests

```java
// Test execution uses the embedded or containerized test datasource.
```

## SB3-M-025: correlation id lost

- Difficulty: Medium
- Framework: Spring Boot 3
- Language: Java
- Perspective: Observability
- Concept: correlation id lost
- Symptom: Logs from one request cannot be joined across services.
- Diagnostic goal: Create and clear request-scoped diagnostic context.

### Buggy code

```java
filterChain.doFilter(request, response);
```

### Expected diagnosis

The request proceeds without installing a correlation value and without cleanup.

### Corrected code

```java
try { MDC.put("requestId", requestId); filterChain.doFilter(request, response); } finally { MDC.remove("requestId"); }
```

### Regression tests

```java
// Every log line has the request id and the thread is clean afterward.
```

## SB3-M-026: Java time format mismatch

- Difficulty: Medium
- Framework: Spring Boot 3
- Language: Java
- Perspective: Serialization
- Concept: Java time format mismatch
- Symptom: Clients reject the response date.
- Diagnostic goal: Declare the wire format at the API boundary.

### Buggy code

```java
record Event(Instant createdAt) {}
```

### Expected diagnosis

The default representation may differ from the documented contract or client expectation.

### Corrected code

```java
record Event(@JsonFormat(pattern = "yyyy-MM-dd'T'HH:mm:ssX") Instant createdAt) {}
```

### Regression tests

```java
// Contract test asserts the exact serialized timestamp.
```

## SB3-M-027: circular bean dependency

- Difficulty: Medium
- Framework: Spring Boot 3
- Language: Java
- Perspective: Startup
- Concept: circular bean dependency
- Symptom: ApplicationContext fails during startup.
- Diagnostic goal: Break the cycle at the architecture boundary.

### Buggy code

```java
class A { A(B b) {} }
class B { B(A a) {} }
```

### Expected diagnosis

Constructor injection exposes a cycle that cannot be resolved safely.

### Corrected code

```java
class A { A(Port port) {} }
class B implements Port { B() {} }
```

### Regression tests

```java
// Context starts and each service depends on an interface with one direction.
```

## SB3-M-028: unbounded upstream timeout

- Difficulty: Medium
- Framework: Spring Boot 3
- Language: Java
- Perspective: HTTP client
- Concept: unbounded upstream timeout
- Symptom: A slow dependency exhausts request threads.
- Diagnostic goal: Set connect and response timeouts and define fallback behavior.

### Buggy code

```java
return restClient.get().uri(uri).retrieve().body(String.class);
```

### Expected diagnosis

Without timeouts, an unavailable upstream can hold workers indefinitely.

### Corrected code

```java
return restClient.get().uri(uri).retrieve().onStatus(s -> s.value() == 404, r -> new NotFoundException()).body(String.class);
```

### Regression tests

```java
// Slow and error responses produce bounded, documented outcomes.
```

## SB3-M-029: graceful shutdown disabled

- Difficulty: Medium
- Framework: Spring Boot 3
- Language: Java
- Perspective: Deployment
- Concept: graceful shutdown disabled
- Symptom: In-flight requests are cut off during rollout.
- Diagnostic goal: Enable graceful shutdown and give the platform enough time.

### Buggy code

```java
server.shutdown=immediate
```

### Expected diagnosis

Immediate shutdown drops active requests and can interrupt transactions.

### Corrected code

```java
server.shutdown=graceful
spring.lifecycle.timeout-per-shutdown-phase=30s
```

### Regression tests

```java
// A shutdown waits for active work up to the configured deadline.
```

## SB3-M-030: configuration accepted without validation

- Difficulty: Medium
- Framework: Spring Boot 3
- Language: Java
- Perspective: Validation
- Concept: configuration accepted without validation
- Symptom: The app starts with an invalid port or URL.
- Diagnostic goal: Validate configuration at binding time.

### Buggy code

```java
record ClientProperties(String baseUrl, int timeoutMs) {}
```

### Expected diagnosis

Invalid values surface only when the first request is made.

### Corrected code

```java
record ClientProperties(@jakarta.validation.constraints.NotBlank String baseUrl, @jakarta.validation.constraints.Positive int timeoutMs) {}
```

### Regression tests

```java
// Invalid configuration fails context startup with a useful property path.
```

## SB3-M-031: profile property mismatch

- Difficulty: Medium
- Framework: Spring Boot 3
- Language: Java
- Perspective: Configuration
- Concept: profile property mismatch
- Symptom: The production datasource is not configured.
- Diagnostic goal: Trace active profiles and property source precedence.

### Buggy code

```java
@Value("${app.url}")
private String url;
```

### Expected diagnosis

The property may exist only under a different profile or prefix; startup failure is clearer than a silent default.

### Corrected code

```java
@ConfigurationProperties(prefix = "app")
public record AppProperties(String url) {}
```

### Regression tests

```java
// Run with each profile and assert the expected URL is bound.
```

## SB3-M-032: missing starter dependency

- Difficulty: Medium
- Framework: Spring Boot 3
- Language: Java
- Perspective: Auto-configuration
- Concept: missing starter dependency
- Symptom: A configured feature has no bean at runtime.
- Diagnostic goal: Map the requested behavior to its Boot starter and auto-configuration.

### Buggy code

```java
@Bean
SecurityFilterChain chain(HttpSecurity http) { return http.build(); }
```

### Expected diagnosis

A security configuration cannot work if the relevant starter and transitive infrastructure are absent.

### Corrected code

```java
dependencies { implementation("org.springframework.boot:spring-boot-starter-security") }
```

### Regression tests

```java
// Include spring-boot-starter-security and assert the context starts.
```

## SB3-M-033: health endpoint exposes internals

- Difficulty: Medium
- Framework: Spring Boot 3
- Language: Java
- Perspective: Actuator
- Concept: health endpoint exposes internals
- Symptom: Operational endpoints leak sensitive details.
- Diagnostic goal: Separate endpoint exposure from health detail visibility.

### Buggy code

```java
management.endpoints.web.exposure.include=*
management.endpoint.health.show-details=always
```

### Expected diagnosis

Wildcard exposure and unrestricted details reveal environment and dependency information.

### Corrected code

```java
management.endpoints.web.exposure.include=health,info
management.endpoint.health.show-details=when_authorized
```

### Regression tests

```java
// Unauthenticated probes see status without credentials or connection details.
```

## SB3-M-034: test profile not activated

- Difficulty: Medium
- Framework: Spring Boot 3
- Language: Java
- Perspective: Profiles
- Concept: test profile not activated
- Symptom: Tests connect to a developer database.
- Diagnostic goal: Make the test environment explicit and isolated.

### Buggy code

```java
@SpringBootTest
class RepositoryTest {}
```

### Expected diagnosis

Without a test profile, normal application properties can select an external database.

### Corrected code

```java
@SpringBootTest
@ActiveProfiles("test")
class RepositoryTest {}
```

### Regression tests

```java
// Test execution uses the embedded or containerized test datasource.
```

## SB3-M-035: correlation id lost

- Difficulty: Medium
- Framework: Spring Boot 3
- Language: Java
- Perspective: Observability
- Concept: correlation id lost
- Symptom: Logs from one request cannot be joined across services.
- Diagnostic goal: Create and clear request-scoped diagnostic context.

### Buggy code

```java
filterChain.doFilter(request, response);
```

### Expected diagnosis

The request proceeds without installing a correlation value and without cleanup.

### Corrected code

```java
try { MDC.put("requestId", requestId); filterChain.doFilter(request, response); } finally { MDC.remove("requestId"); }
```

### Regression tests

```java
// Every log line has the request id and the thread is clean afterward.
```

## SB3-M-036: Java time format mismatch

- Difficulty: Medium
- Framework: Spring Boot 3
- Language: Java
- Perspective: Serialization
- Concept: Java time format mismatch
- Symptom: Clients reject the response date.
- Diagnostic goal: Declare the wire format at the API boundary.

### Buggy code

```java
record Event(Instant createdAt) {}
```

### Expected diagnosis

The default representation may differ from the documented contract or client expectation.

### Corrected code

```java
record Event(@JsonFormat(pattern = "yyyy-MM-dd'T'HH:mm:ssX") Instant createdAt) {}
```

### Regression tests

```java
// Contract test asserts the exact serialized timestamp.
```

## SB3-M-037: circular bean dependency

- Difficulty: Medium
- Framework: Spring Boot 3
- Language: Java
- Perspective: Startup
- Concept: circular bean dependency
- Symptom: ApplicationContext fails during startup.
- Diagnostic goal: Break the cycle at the architecture boundary.

### Buggy code

```java
class A { A(B b) {} }
class B { B(A a) {} }
```

### Expected diagnosis

Constructor injection exposes a cycle that cannot be resolved safely.

### Corrected code

```java
class A { A(Port port) {} }
class B implements Port { B() {} }
```

### Regression tests

```java
// Context starts and each service depends on an interface with one direction.
```

## SB3-M-038: unbounded upstream timeout

- Difficulty: Medium
- Framework: Spring Boot 3
- Language: Java
- Perspective: HTTP client
- Concept: unbounded upstream timeout
- Symptom: A slow dependency exhausts request threads.
- Diagnostic goal: Set connect and response timeouts and define fallback behavior.

### Buggy code

```java
return restClient.get().uri(uri).retrieve().body(String.class);
```

### Expected diagnosis

Without timeouts, an unavailable upstream can hold workers indefinitely.

### Corrected code

```java
return restClient.get().uri(uri).retrieve().onStatus(s -> s.value() == 404, r -> new NotFoundException()).body(String.class);
```

### Regression tests

```java
// Slow and error responses produce bounded, documented outcomes.
```

## SB3-M-039: graceful shutdown disabled

- Difficulty: Medium
- Framework: Spring Boot 3
- Language: Java
- Perspective: Deployment
- Concept: graceful shutdown disabled
- Symptom: In-flight requests are cut off during rollout.
- Diagnostic goal: Enable graceful shutdown and give the platform enough time.

### Buggy code

```java
server.shutdown=immediate
```

### Expected diagnosis

Immediate shutdown drops active requests and can interrupt transactions.

### Corrected code

```java
server.shutdown=graceful
spring.lifecycle.timeout-per-shutdown-phase=30s
```

### Regression tests

```java
// A shutdown waits for active work up to the configured deadline.
```

## SB3-M-040: configuration accepted without validation

- Difficulty: Medium
- Framework: Spring Boot 3
- Language: Java
- Perspective: Validation
- Concept: configuration accepted without validation
- Symptom: The app starts with an invalid port or URL.
- Diagnostic goal: Validate configuration at binding time.

### Buggy code

```java
record ClientProperties(String baseUrl, int timeoutMs) {}
```

### Expected diagnosis

Invalid values surface only when the first request is made.

### Corrected code

```java
record ClientProperties(@jakarta.validation.constraints.NotBlank String baseUrl, @jakarta.validation.constraints.Positive int timeoutMs) {}
```

### Regression tests

```java
// Invalid configuration fails context startup with a useful property path.
```

## SB3-M-041: profile property mismatch

- Difficulty: Medium
- Framework: Spring Boot 3
- Language: Java
- Perspective: Configuration
- Concept: profile property mismatch
- Symptom: The production datasource is not configured.
- Diagnostic goal: Trace active profiles and property source precedence.

### Buggy code

```java
@Value("${app.url}")
private String url;
```

### Expected diagnosis

The property may exist only under a different profile or prefix; startup failure is clearer than a silent default.

### Corrected code

```java
@ConfigurationProperties(prefix = "app")
public record AppProperties(String url) {}
```

### Regression tests

```java
// Run with each profile and assert the expected URL is bound.
```

## SB3-M-042: missing starter dependency

- Difficulty: Medium
- Framework: Spring Boot 3
- Language: Java
- Perspective: Auto-configuration
- Concept: missing starter dependency
- Symptom: A configured feature has no bean at runtime.
- Diagnostic goal: Map the requested behavior to its Boot starter and auto-configuration.

### Buggy code

```java
@Bean
SecurityFilterChain chain(HttpSecurity http) { return http.build(); }
```

### Expected diagnosis

A security configuration cannot work if the relevant starter and transitive infrastructure are absent.

### Corrected code

```java
dependencies { implementation("org.springframework.boot:spring-boot-starter-security") }
```

### Regression tests

```java
// Include spring-boot-starter-security and assert the context starts.
```

## SB3-M-043: health endpoint exposes internals

- Difficulty: Medium
- Framework: Spring Boot 3
- Language: Java
- Perspective: Actuator
- Concept: health endpoint exposes internals
- Symptom: Operational endpoints leak sensitive details.
- Diagnostic goal: Separate endpoint exposure from health detail visibility.

### Buggy code

```java
management.endpoints.web.exposure.include=*
management.endpoint.health.show-details=always
```

### Expected diagnosis

Wildcard exposure and unrestricted details reveal environment and dependency information.

### Corrected code

```java
management.endpoints.web.exposure.include=health,info
management.endpoint.health.show-details=when_authorized
```

### Regression tests

```java
// Unauthenticated probes see status without credentials or connection details.
```

## SB3-M-044: test profile not activated

- Difficulty: Medium
- Framework: Spring Boot 3
- Language: Java
- Perspective: Profiles
- Concept: test profile not activated
- Symptom: Tests connect to a developer database.
- Diagnostic goal: Make the test environment explicit and isolated.

### Buggy code

```java
@SpringBootTest
class RepositoryTest {}
```

### Expected diagnosis

Without a test profile, normal application properties can select an external database.

### Corrected code

```java
@SpringBootTest
@ActiveProfiles("test")
class RepositoryTest {}
```

### Regression tests

```java
// Test execution uses the embedded or containerized test datasource.
```

## SB3-M-045: correlation id lost

- Difficulty: Medium
- Framework: Spring Boot 3
- Language: Java
- Perspective: Observability
- Concept: correlation id lost
- Symptom: Logs from one request cannot be joined across services.
- Diagnostic goal: Create and clear request-scoped diagnostic context.

### Buggy code

```java
filterChain.doFilter(request, response);
```

### Expected diagnosis

The request proceeds without installing a correlation value and without cleanup.

### Corrected code

```java
try { MDC.put("requestId", requestId); filterChain.doFilter(request, response); } finally { MDC.remove("requestId"); }
```

### Regression tests

```java
// Every log line has the request id and the thread is clean afterward.
```

## SB3-M-046: Java time format mismatch

- Difficulty: Medium
- Framework: Spring Boot 3
- Language: Java
- Perspective: Serialization
- Concept: Java time format mismatch
- Symptom: Clients reject the response date.
- Diagnostic goal: Declare the wire format at the API boundary.

### Buggy code

```java
record Event(Instant createdAt) {}
```

### Expected diagnosis

The default representation may differ from the documented contract or client expectation.

### Corrected code

```java
record Event(@JsonFormat(pattern = "yyyy-MM-dd'T'HH:mm:ssX") Instant createdAt) {}
```

### Regression tests

```java
// Contract test asserts the exact serialized timestamp.
```

## SB3-M-047: circular bean dependency

- Difficulty: Medium
- Framework: Spring Boot 3
- Language: Java
- Perspective: Startup
- Concept: circular bean dependency
- Symptom: ApplicationContext fails during startup.
- Diagnostic goal: Break the cycle at the architecture boundary.

### Buggy code

```java
class A { A(B b) {} }
class B { B(A a) {} }
```

### Expected diagnosis

Constructor injection exposes a cycle that cannot be resolved safely.

### Corrected code

```java
class A { A(Port port) {} }
class B implements Port { B() {} }
```

### Regression tests

```java
// Context starts and each service depends on an interface with one direction.
```

## SB3-M-048: unbounded upstream timeout

- Difficulty: Medium
- Framework: Spring Boot 3
- Language: Java
- Perspective: HTTP client
- Concept: unbounded upstream timeout
- Symptom: A slow dependency exhausts request threads.
- Diagnostic goal: Set connect and response timeouts and define fallback behavior.

### Buggy code

```java
return restClient.get().uri(uri).retrieve().body(String.class);
```

### Expected diagnosis

Without timeouts, an unavailable upstream can hold workers indefinitely.

### Corrected code

```java
return restClient.get().uri(uri).retrieve().onStatus(s -> s.value() == 404, r -> new NotFoundException()).body(String.class);
```

### Regression tests

```java
// Slow and error responses produce bounded, documented outcomes.
```

## SB3-M-049: graceful shutdown disabled

- Difficulty: Medium
- Framework: Spring Boot 3
- Language: Java
- Perspective: Deployment
- Concept: graceful shutdown disabled
- Symptom: In-flight requests are cut off during rollout.
- Diagnostic goal: Enable graceful shutdown and give the platform enough time.

### Buggy code

```java
server.shutdown=immediate
```

### Expected diagnosis

Immediate shutdown drops active requests and can interrupt transactions.

### Corrected code

```java
server.shutdown=graceful
spring.lifecycle.timeout-per-shutdown-phase=30s
```

### Regression tests

```java
// A shutdown waits for active work up to the configured deadline.
```

## SB3-M-050: configuration accepted without validation

- Difficulty: Medium
- Framework: Spring Boot 3
- Language: Java
- Perspective: Validation
- Concept: configuration accepted without validation
- Symptom: The app starts with an invalid port or URL.
- Diagnostic goal: Validate configuration at binding time.

### Buggy code

```java
record ClientProperties(String baseUrl, int timeoutMs) {}
```

### Expected diagnosis

Invalid values surface only when the first request is made.

### Corrected code

```java
record ClientProperties(@jakarta.validation.constraints.NotBlank String baseUrl, @jakarta.validation.constraints.Positive int timeoutMs) {}
```

### Regression tests

```java
// Invalid configuration fails context startup with a useful property path.
```

## SB3-M-051: profile property mismatch

- Difficulty: Medium
- Framework: Spring Boot 3
- Language: Java
- Perspective: Configuration
- Concept: profile property mismatch
- Symptom: The production datasource is not configured.
- Diagnostic goal: Trace active profiles and property source precedence.

### Buggy code

```java
@Value("${app.url}")
private String url;
```

### Expected diagnosis

The property may exist only under a different profile or prefix; startup failure is clearer than a silent default.

### Corrected code

```java
@ConfigurationProperties(prefix = "app")
public record AppProperties(String url) {}
```

### Regression tests

```java
// Run with each profile and assert the expected URL is bound.
```

## SB3-M-052: missing starter dependency

- Difficulty: Medium
- Framework: Spring Boot 3
- Language: Java
- Perspective: Auto-configuration
- Concept: missing starter dependency
- Symptom: A configured feature has no bean at runtime.
- Diagnostic goal: Map the requested behavior to its Boot starter and auto-configuration.

### Buggy code

```java
@Bean
SecurityFilterChain chain(HttpSecurity http) { return http.build(); }
```

### Expected diagnosis

A security configuration cannot work if the relevant starter and transitive infrastructure are absent.

### Corrected code

```java
dependencies { implementation("org.springframework.boot:spring-boot-starter-security") }
```

### Regression tests

```java
// Include spring-boot-starter-security and assert the context starts.
```

## SB3-M-053: health endpoint exposes internals

- Difficulty: Medium
- Framework: Spring Boot 3
- Language: Java
- Perspective: Actuator
- Concept: health endpoint exposes internals
- Symptom: Operational endpoints leak sensitive details.
- Diagnostic goal: Separate endpoint exposure from health detail visibility.

### Buggy code

```java
management.endpoints.web.exposure.include=*
management.endpoint.health.show-details=always
```

### Expected diagnosis

Wildcard exposure and unrestricted details reveal environment and dependency information.

### Corrected code

```java
management.endpoints.web.exposure.include=health,info
management.endpoint.health.show-details=when_authorized
```

### Regression tests

```java
// Unauthenticated probes see status without credentials or connection details.
```

## SB3-M-054: test profile not activated

- Difficulty: Medium
- Framework: Spring Boot 3
- Language: Java
- Perspective: Profiles
- Concept: test profile not activated
- Symptom: Tests connect to a developer database.
- Diagnostic goal: Make the test environment explicit and isolated.

### Buggy code

```java
@SpringBootTest
class RepositoryTest {}
```

### Expected diagnosis

Without a test profile, normal application properties can select an external database.

### Corrected code

```java
@SpringBootTest
@ActiveProfiles("test")
class RepositoryTest {}
```

### Regression tests

```java
// Test execution uses the embedded or containerized test datasource.
```

## SB3-M-055: correlation id lost

- Difficulty: Medium
- Framework: Spring Boot 3
- Language: Java
- Perspective: Observability
- Concept: correlation id lost
- Symptom: Logs from one request cannot be joined across services.
- Diagnostic goal: Create and clear request-scoped diagnostic context.

### Buggy code

```java
filterChain.doFilter(request, response);
```

### Expected diagnosis

The request proceeds without installing a correlation value and without cleanup.

### Corrected code

```java
try { MDC.put("requestId", requestId); filterChain.doFilter(request, response); } finally { MDC.remove("requestId"); }
```

### Regression tests

```java
// Every log line has the request id and the thread is clean afterward.
```

## SB3-M-056: Java time format mismatch

- Difficulty: Medium
- Framework: Spring Boot 3
- Language: Java
- Perspective: Serialization
- Concept: Java time format mismatch
- Symptom: Clients reject the response date.
- Diagnostic goal: Declare the wire format at the API boundary.

### Buggy code

```java
record Event(Instant createdAt) {}
```

### Expected diagnosis

The default representation may differ from the documented contract or client expectation.

### Corrected code

```java
record Event(@JsonFormat(pattern = "yyyy-MM-dd'T'HH:mm:ssX") Instant createdAt) {}
```

### Regression tests

```java
// Contract test asserts the exact serialized timestamp.
```

## SB3-M-057: circular bean dependency

- Difficulty: Medium
- Framework: Spring Boot 3
- Language: Java
- Perspective: Startup
- Concept: circular bean dependency
- Symptom: ApplicationContext fails during startup.
- Diagnostic goal: Break the cycle at the architecture boundary.

### Buggy code

```java
class A { A(B b) {} }
class B { B(A a) {} }
```

### Expected diagnosis

Constructor injection exposes a cycle that cannot be resolved safely.

### Corrected code

```java
class A { A(Port port) {} }
class B implements Port { B() {} }
```

### Regression tests

```java
// Context starts and each service depends on an interface with one direction.
```

## SB3-M-058: unbounded upstream timeout

- Difficulty: Medium
- Framework: Spring Boot 3
- Language: Java
- Perspective: HTTP client
- Concept: unbounded upstream timeout
- Symptom: A slow dependency exhausts request threads.
- Diagnostic goal: Set connect and response timeouts and define fallback behavior.

### Buggy code

```java
return restClient.get().uri(uri).retrieve().body(String.class);
```

### Expected diagnosis

Without timeouts, an unavailable upstream can hold workers indefinitely.

### Corrected code

```java
return restClient.get().uri(uri).retrieve().onStatus(s -> s.value() == 404, r -> new NotFoundException()).body(String.class);
```

### Regression tests

```java
// Slow and error responses produce bounded, documented outcomes.
```

## SB3-M-059: graceful shutdown disabled

- Difficulty: Medium
- Framework: Spring Boot 3
- Language: Java
- Perspective: Deployment
- Concept: graceful shutdown disabled
- Symptom: In-flight requests are cut off during rollout.
- Diagnostic goal: Enable graceful shutdown and give the platform enough time.

### Buggy code

```java
server.shutdown=immediate
```

### Expected diagnosis

Immediate shutdown drops active requests and can interrupt transactions.

### Corrected code

```java
server.shutdown=graceful
spring.lifecycle.timeout-per-shutdown-phase=30s
```

### Regression tests

```java
// A shutdown waits for active work up to the configured deadline.
```

## SB3-M-060: configuration accepted without validation

- Difficulty: Medium
- Framework: Spring Boot 3
- Language: Java
- Perspective: Validation
- Concept: configuration accepted without validation
- Symptom: The app starts with an invalid port or URL.
- Diagnostic goal: Validate configuration at binding time.

### Buggy code

```java
record ClientProperties(String baseUrl, int timeoutMs) {}
```

### Expected diagnosis

Invalid values surface only when the first request is made.

### Corrected code

```java
record ClientProperties(@jakarta.validation.constraints.NotBlank String baseUrl, @jakarta.validation.constraints.Positive int timeoutMs) {}
```

### Regression tests

```java
// Invalid configuration fails context startup with a useful property path.
```

## SB3-M-061: profile property mismatch

- Difficulty: Medium
- Framework: Spring Boot 3
- Language: Java
- Perspective: Configuration
- Concept: profile property mismatch
- Symptom: The production datasource is not configured.
- Diagnostic goal: Trace active profiles and property source precedence.

### Buggy code

```java
@Value("${app.url}")
private String url;
```

### Expected diagnosis

The property may exist only under a different profile or prefix; startup failure is clearer than a silent default.

### Corrected code

```java
@ConfigurationProperties(prefix = "app")
public record AppProperties(String url) {}
```

### Regression tests

```java
// Run with each profile and assert the expected URL is bound.
```

## SB3-M-062: missing starter dependency

- Difficulty: Medium
- Framework: Spring Boot 3
- Language: Java
- Perspective: Auto-configuration
- Concept: missing starter dependency
- Symptom: A configured feature has no bean at runtime.
- Diagnostic goal: Map the requested behavior to its Boot starter and auto-configuration.

### Buggy code

```java
@Bean
SecurityFilterChain chain(HttpSecurity http) { return http.build(); }
```

### Expected diagnosis

A security configuration cannot work if the relevant starter and transitive infrastructure are absent.

### Corrected code

```java
dependencies { implementation("org.springframework.boot:spring-boot-starter-security") }
```

### Regression tests

```java
// Include spring-boot-starter-security and assert the context starts.
```

## SB3-M-063: health endpoint exposes internals

- Difficulty: Medium
- Framework: Spring Boot 3
- Language: Java
- Perspective: Actuator
- Concept: health endpoint exposes internals
- Symptom: Operational endpoints leak sensitive details.
- Diagnostic goal: Separate endpoint exposure from health detail visibility.

### Buggy code

```java
management.endpoints.web.exposure.include=*
management.endpoint.health.show-details=always
```

### Expected diagnosis

Wildcard exposure and unrestricted details reveal environment and dependency information.

### Corrected code

```java
management.endpoints.web.exposure.include=health,info
management.endpoint.health.show-details=when_authorized
```

### Regression tests

```java
// Unauthenticated probes see status without credentials or connection details.
```

## SB3-M-064: test profile not activated

- Difficulty: Medium
- Framework: Spring Boot 3
- Language: Java
- Perspective: Profiles
- Concept: test profile not activated
- Symptom: Tests connect to a developer database.
- Diagnostic goal: Make the test environment explicit and isolated.

### Buggy code

```java
@SpringBootTest
class RepositoryTest {}
```

### Expected diagnosis

Without a test profile, normal application properties can select an external database.

### Corrected code

```java
@SpringBootTest
@ActiveProfiles("test")
class RepositoryTest {}
```

### Regression tests

```java
// Test execution uses the embedded or containerized test datasource.
```

## SB3-M-065: correlation id lost

- Difficulty: Medium
- Framework: Spring Boot 3
- Language: Java
- Perspective: Observability
- Concept: correlation id lost
- Symptom: Logs from one request cannot be joined across services.
- Diagnostic goal: Create and clear request-scoped diagnostic context.

### Buggy code

```java
filterChain.doFilter(request, response);
```

### Expected diagnosis

The request proceeds without installing a correlation value and without cleanup.

### Corrected code

```java
try { MDC.put("requestId", requestId); filterChain.doFilter(request, response); } finally { MDC.remove("requestId"); }
```

### Regression tests

```java
// Every log line has the request id and the thread is clean afterward.
```

## SB3-M-066: Java time format mismatch

- Difficulty: Medium
- Framework: Spring Boot 3
- Language: Java
- Perspective: Serialization
- Concept: Java time format mismatch
- Symptom: Clients reject the response date.
- Diagnostic goal: Declare the wire format at the API boundary.

### Buggy code

```java
record Event(Instant createdAt) {}
```

### Expected diagnosis

The default representation may differ from the documented contract or client expectation.

### Corrected code

```java
record Event(@JsonFormat(pattern = "yyyy-MM-dd'T'HH:mm:ssX") Instant createdAt) {}
```

### Regression tests

```java
// Contract test asserts the exact serialized timestamp.
```

## SB3-M-067: circular bean dependency

- Difficulty: Medium
- Framework: Spring Boot 3
- Language: Java
- Perspective: Startup
- Concept: circular bean dependency
- Symptom: ApplicationContext fails during startup.
- Diagnostic goal: Break the cycle at the architecture boundary.

### Buggy code

```java
class A { A(B b) {} }
class B { B(A a) {} }
```

### Expected diagnosis

Constructor injection exposes a cycle that cannot be resolved safely.

### Corrected code

```java
class A { A(Port port) {} }
class B implements Port { B() {} }
```

### Regression tests

```java
// Context starts and each service depends on an interface with one direction.
```

## SB3-M-068: unbounded upstream timeout

- Difficulty: Medium
- Framework: Spring Boot 3
- Language: Java
- Perspective: HTTP client
- Concept: unbounded upstream timeout
- Symptom: A slow dependency exhausts request threads.
- Diagnostic goal: Set connect and response timeouts and define fallback behavior.

### Buggy code

```java
return restClient.get().uri(uri).retrieve().body(String.class);
```

### Expected diagnosis

Without timeouts, an unavailable upstream can hold workers indefinitely.

### Corrected code

```java
return restClient.get().uri(uri).retrieve().onStatus(s -> s.value() == 404, r -> new NotFoundException()).body(String.class);
```

### Regression tests

```java
// Slow and error responses produce bounded, documented outcomes.
```

## SB3-M-069: graceful shutdown disabled

- Difficulty: Medium
- Framework: Spring Boot 3
- Language: Java
- Perspective: Deployment
- Concept: graceful shutdown disabled
- Symptom: In-flight requests are cut off during rollout.
- Diagnostic goal: Enable graceful shutdown and give the platform enough time.

### Buggy code

```java
server.shutdown=immediate
```

### Expected diagnosis

Immediate shutdown drops active requests and can interrupt transactions.

### Corrected code

```java
server.shutdown=graceful
spring.lifecycle.timeout-per-shutdown-phase=30s
```

### Regression tests

```java
// A shutdown waits for active work up to the configured deadline.
```

## SB3-M-070: configuration accepted without validation

- Difficulty: Medium
- Framework: Spring Boot 3
- Language: Java
- Perspective: Validation
- Concept: configuration accepted without validation
- Symptom: The app starts with an invalid port or URL.
- Diagnostic goal: Validate configuration at binding time.

### Buggy code

```java
record ClientProperties(String baseUrl, int timeoutMs) {}
```

### Expected diagnosis

Invalid values surface only when the first request is made.

### Corrected code

```java
record ClientProperties(@jakarta.validation.constraints.NotBlank String baseUrl, @jakarta.validation.constraints.Positive int timeoutMs) {}
```

### Regression tests

```java
// Invalid configuration fails context startup with a useful property path.
```

## SB3-M-071: profile property mismatch

- Difficulty: Medium
- Framework: Spring Boot 3
- Language: Java
- Perspective: Configuration
- Concept: profile property mismatch
- Symptom: The production datasource is not configured.
- Diagnostic goal: Trace active profiles and property source precedence.

### Buggy code

```java
@Value("${app.url}")
private String url;
```

### Expected diagnosis

The property may exist only under a different profile or prefix; startup failure is clearer than a silent default.

### Corrected code

```java
@ConfigurationProperties(prefix = "app")
public record AppProperties(String url) {}
```

### Regression tests

```java
// Run with each profile and assert the expected URL is bound.
```

## SB3-M-072: missing starter dependency

- Difficulty: Medium
- Framework: Spring Boot 3
- Language: Java
- Perspective: Auto-configuration
- Concept: missing starter dependency
- Symptom: A configured feature has no bean at runtime.
- Diagnostic goal: Map the requested behavior to its Boot starter and auto-configuration.

### Buggy code

```java
@Bean
SecurityFilterChain chain(HttpSecurity http) { return http.build(); }
```

### Expected diagnosis

A security configuration cannot work if the relevant starter and transitive infrastructure are absent.

### Corrected code

```java
dependencies { implementation("org.springframework.boot:spring-boot-starter-security") }
```

### Regression tests

```java
// Include spring-boot-starter-security and assert the context starts.
```

## SB3-M-073: health endpoint exposes internals

- Difficulty: Medium
- Framework: Spring Boot 3
- Language: Java
- Perspective: Actuator
- Concept: health endpoint exposes internals
- Symptom: Operational endpoints leak sensitive details.
- Diagnostic goal: Separate endpoint exposure from health detail visibility.

### Buggy code

```java
management.endpoints.web.exposure.include=*
management.endpoint.health.show-details=always
```

### Expected diagnosis

Wildcard exposure and unrestricted details reveal environment and dependency information.

### Corrected code

```java
management.endpoints.web.exposure.include=health,info
management.endpoint.health.show-details=when_authorized
```

### Regression tests

```java
// Unauthenticated probes see status without credentials or connection details.
```

## SB3-M-074: test profile not activated

- Difficulty: Medium
- Framework: Spring Boot 3
- Language: Java
- Perspective: Profiles
- Concept: test profile not activated
- Symptom: Tests connect to a developer database.
- Diagnostic goal: Make the test environment explicit and isolated.

### Buggy code

```java
@SpringBootTest
class RepositoryTest {}
```

### Expected diagnosis

Without a test profile, normal application properties can select an external database.

### Corrected code

```java
@SpringBootTest
@ActiveProfiles("test")
class RepositoryTest {}
```

### Regression tests

```java
// Test execution uses the embedded or containerized test datasource.
```

## SB3-M-075: correlation id lost

- Difficulty: Medium
- Framework: Spring Boot 3
- Language: Java
- Perspective: Observability
- Concept: correlation id lost
- Symptom: Logs from one request cannot be joined across services.
- Diagnostic goal: Create and clear request-scoped diagnostic context.

### Buggy code

```java
filterChain.doFilter(request, response);
```

### Expected diagnosis

The request proceeds without installing a correlation value and without cleanup.

### Corrected code

```java
try { MDC.put("requestId", requestId); filterChain.doFilter(request, response); } finally { MDC.remove("requestId"); }
```

### Regression tests

```java
// Every log line has the request id and the thread is clean afterward.
```

## SB3-M-076: Java time format mismatch

- Difficulty: Medium
- Framework: Spring Boot 3
- Language: Java
- Perspective: Serialization
- Concept: Java time format mismatch
- Symptom: Clients reject the response date.
- Diagnostic goal: Declare the wire format at the API boundary.

### Buggy code

```java
record Event(Instant createdAt) {}
```

### Expected diagnosis

The default representation may differ from the documented contract or client expectation.

### Corrected code

```java
record Event(@JsonFormat(pattern = "yyyy-MM-dd'T'HH:mm:ssX") Instant createdAt) {}
```

### Regression tests

```java
// Contract test asserts the exact serialized timestamp.
```

## SB3-M-077: circular bean dependency

- Difficulty: Medium
- Framework: Spring Boot 3
- Language: Java
- Perspective: Startup
- Concept: circular bean dependency
- Symptom: ApplicationContext fails during startup.
- Diagnostic goal: Break the cycle at the architecture boundary.

### Buggy code

```java
class A { A(B b) {} }
class B { B(A a) {} }
```

### Expected diagnosis

Constructor injection exposes a cycle that cannot be resolved safely.

### Corrected code

```java
class A { A(Port port) {} }
class B implements Port { B() {} }
```

### Regression tests

```java
// Context starts and each service depends on an interface with one direction.
```

## SB3-M-078: unbounded upstream timeout

- Difficulty: Medium
- Framework: Spring Boot 3
- Language: Java
- Perspective: HTTP client
- Concept: unbounded upstream timeout
- Symptom: A slow dependency exhausts request threads.
- Diagnostic goal: Set connect and response timeouts and define fallback behavior.

### Buggy code

```java
return restClient.get().uri(uri).retrieve().body(String.class);
```

### Expected diagnosis

Without timeouts, an unavailable upstream can hold workers indefinitely.

### Corrected code

```java
return restClient.get().uri(uri).retrieve().onStatus(s -> s.value() == 404, r -> new NotFoundException()).body(String.class);
```

### Regression tests

```java
// Slow and error responses produce bounded, documented outcomes.
```

## SB3-M-079: graceful shutdown disabled

- Difficulty: Medium
- Framework: Spring Boot 3
- Language: Java
- Perspective: Deployment
- Concept: graceful shutdown disabled
- Symptom: In-flight requests are cut off during rollout.
- Diagnostic goal: Enable graceful shutdown and give the platform enough time.

### Buggy code

```java
server.shutdown=immediate
```

### Expected diagnosis

Immediate shutdown drops active requests and can interrupt transactions.

### Corrected code

```java
server.shutdown=graceful
spring.lifecycle.timeout-per-shutdown-phase=30s
```

### Regression tests

```java
// A shutdown waits for active work up to the configured deadline.
```

## SB3-M-080: configuration accepted without validation

- Difficulty: Medium
- Framework: Spring Boot 3
- Language: Java
- Perspective: Validation
- Concept: configuration accepted without validation
- Symptom: The app starts with an invalid port or URL.
- Diagnostic goal: Validate configuration at binding time.

### Buggy code

```java
record ClientProperties(String baseUrl, int timeoutMs) {}
```

### Expected diagnosis

Invalid values surface only when the first request is made.

### Corrected code

```java
record ClientProperties(@jakarta.validation.constraints.NotBlank String baseUrl, @jakarta.validation.constraints.Positive int timeoutMs) {}
```

### Regression tests

```java
// Invalid configuration fails context startup with a useful property path.
```

## SB3-M-081: profile property mismatch

- Difficulty: Medium
- Framework: Spring Boot 3
- Language: Java
- Perspective: Configuration
- Concept: profile property mismatch
- Symptom: The production datasource is not configured.
- Diagnostic goal: Trace active profiles and property source precedence.

### Buggy code

```java
@Value("${app.url}")
private String url;
```

### Expected diagnosis

The property may exist only under a different profile or prefix; startup failure is clearer than a silent default.

### Corrected code

```java
@ConfigurationProperties(prefix = "app")
public record AppProperties(String url) {}
```

### Regression tests

```java
// Run with each profile and assert the expected URL is bound.
```

## SB3-M-082: missing starter dependency

- Difficulty: Medium
- Framework: Spring Boot 3
- Language: Java
- Perspective: Auto-configuration
- Concept: missing starter dependency
- Symptom: A configured feature has no bean at runtime.
- Diagnostic goal: Map the requested behavior to its Boot starter and auto-configuration.

### Buggy code

```java
@Bean
SecurityFilterChain chain(HttpSecurity http) { return http.build(); }
```

### Expected diagnosis

A security configuration cannot work if the relevant starter and transitive infrastructure are absent.

### Corrected code

```java
dependencies { implementation("org.springframework.boot:spring-boot-starter-security") }
```

### Regression tests

```java
// Include spring-boot-starter-security and assert the context starts.
```

## SB3-M-083: health endpoint exposes internals

- Difficulty: Medium
- Framework: Spring Boot 3
- Language: Java
- Perspective: Actuator
- Concept: health endpoint exposes internals
- Symptom: Operational endpoints leak sensitive details.
- Diagnostic goal: Separate endpoint exposure from health detail visibility.

### Buggy code

```java
management.endpoints.web.exposure.include=*
management.endpoint.health.show-details=always
```

### Expected diagnosis

Wildcard exposure and unrestricted details reveal environment and dependency information.

### Corrected code

```java
management.endpoints.web.exposure.include=health,info
management.endpoint.health.show-details=when_authorized
```

### Regression tests

```java
// Unauthenticated probes see status without credentials or connection details.
```

## SB3-M-084: test profile not activated

- Difficulty: Medium
- Framework: Spring Boot 3
- Language: Java
- Perspective: Profiles
- Concept: test profile not activated
- Symptom: Tests connect to a developer database.
- Diagnostic goal: Make the test environment explicit and isolated.

### Buggy code

```java
@SpringBootTest
class RepositoryTest {}
```

### Expected diagnosis

Without a test profile, normal application properties can select an external database.

### Corrected code

```java
@SpringBootTest
@ActiveProfiles("test")
class RepositoryTest {}
```

### Regression tests

```java
// Test execution uses the embedded or containerized test datasource.
```

## SB3-M-085: correlation id lost

- Difficulty: Medium
- Framework: Spring Boot 3
- Language: Java
- Perspective: Observability
- Concept: correlation id lost
- Symptom: Logs from one request cannot be joined across services.
- Diagnostic goal: Create and clear request-scoped diagnostic context.

### Buggy code

```java
filterChain.doFilter(request, response);
```

### Expected diagnosis

The request proceeds without installing a correlation value and without cleanup.

### Corrected code

```java
try { MDC.put("requestId", requestId); filterChain.doFilter(request, response); } finally { MDC.remove("requestId"); }
```

### Regression tests

```java
// Every log line has the request id and the thread is clean afterward.
```

## SB3-M-086: Java time format mismatch

- Difficulty: Medium
- Framework: Spring Boot 3
- Language: Java
- Perspective: Serialization
- Concept: Java time format mismatch
- Symptom: Clients reject the response date.
- Diagnostic goal: Declare the wire format at the API boundary.

### Buggy code

```java
record Event(Instant createdAt) {}
```

### Expected diagnosis

The default representation may differ from the documented contract or client expectation.

### Corrected code

```java
record Event(@JsonFormat(pattern = "yyyy-MM-dd'T'HH:mm:ssX") Instant createdAt) {}
```

### Regression tests

```java
// Contract test asserts the exact serialized timestamp.
```

## SB3-M-087: circular bean dependency

- Difficulty: Medium
- Framework: Spring Boot 3
- Language: Java
- Perspective: Startup
- Concept: circular bean dependency
- Symptom: ApplicationContext fails during startup.
- Diagnostic goal: Break the cycle at the architecture boundary.

### Buggy code

```java
class A { A(B b) {} }
class B { B(A a) {} }
```

### Expected diagnosis

Constructor injection exposes a cycle that cannot be resolved safely.

### Corrected code

```java
class A { A(Port port) {} }
class B implements Port { B() {} }
```

### Regression tests

```java
// Context starts and each service depends on an interface with one direction.
```

## SB3-M-088: unbounded upstream timeout

- Difficulty: Medium
- Framework: Spring Boot 3
- Language: Java
- Perspective: HTTP client
- Concept: unbounded upstream timeout
- Symptom: A slow dependency exhausts request threads.
- Diagnostic goal: Set connect and response timeouts and define fallback behavior.

### Buggy code

```java
return restClient.get().uri(uri).retrieve().body(String.class);
```

### Expected diagnosis

Without timeouts, an unavailable upstream can hold workers indefinitely.

### Corrected code

```java
return restClient.get().uri(uri).retrieve().onStatus(s -> s.value() == 404, r -> new NotFoundException()).body(String.class);
```

### Regression tests

```java
// Slow and error responses produce bounded, documented outcomes.
```

## SB3-M-089: graceful shutdown disabled

- Difficulty: Medium
- Framework: Spring Boot 3
- Language: Java
- Perspective: Deployment
- Concept: graceful shutdown disabled
- Symptom: In-flight requests are cut off during rollout.
- Diagnostic goal: Enable graceful shutdown and give the platform enough time.

### Buggy code

```java
server.shutdown=immediate
```

### Expected diagnosis

Immediate shutdown drops active requests and can interrupt transactions.

### Corrected code

```java
server.shutdown=graceful
spring.lifecycle.timeout-per-shutdown-phase=30s
```

### Regression tests

```java
// A shutdown waits for active work up to the configured deadline.
```

## SB3-M-090: configuration accepted without validation

- Difficulty: Medium
- Framework: Spring Boot 3
- Language: Java
- Perspective: Validation
- Concept: configuration accepted without validation
- Symptom: The app starts with an invalid port or URL.
- Diagnostic goal: Validate configuration at binding time.

### Buggy code

```java
record ClientProperties(String baseUrl, int timeoutMs) {}
```

### Expected diagnosis

Invalid values surface only when the first request is made.

### Corrected code

```java
record ClientProperties(@jakarta.validation.constraints.NotBlank String baseUrl, @jakarta.validation.constraints.Positive int timeoutMs) {}
```

### Regression tests

```java
// Invalid configuration fails context startup with a useful property path.
```

## SB3-M-091: profile property mismatch

- Difficulty: Medium
- Framework: Spring Boot 3
- Language: Java
- Perspective: Configuration
- Concept: profile property mismatch
- Symptom: The production datasource is not configured.
- Diagnostic goal: Trace active profiles and property source precedence.

### Buggy code

```java
@Value("${app.url}")
private String url;
```

### Expected diagnosis

The property may exist only under a different profile or prefix; startup failure is clearer than a silent default.

### Corrected code

```java
@ConfigurationProperties(prefix = "app")
public record AppProperties(String url) {}
```

### Regression tests

```java
// Run with each profile and assert the expected URL is bound.
```

## SB3-M-092: missing starter dependency

- Difficulty: Medium
- Framework: Spring Boot 3
- Language: Java
- Perspective: Auto-configuration
- Concept: missing starter dependency
- Symptom: A configured feature has no bean at runtime.
- Diagnostic goal: Map the requested behavior to its Boot starter and auto-configuration.

### Buggy code

```java
@Bean
SecurityFilterChain chain(HttpSecurity http) { return http.build(); }
```

### Expected diagnosis

A security configuration cannot work if the relevant starter and transitive infrastructure are absent.

### Corrected code

```java
dependencies { implementation("org.springframework.boot:spring-boot-starter-security") }
```

### Regression tests

```java
// Include spring-boot-starter-security and assert the context starts.
```

## SB3-M-093: health endpoint exposes internals

- Difficulty: Medium
- Framework: Spring Boot 3
- Language: Java
- Perspective: Actuator
- Concept: health endpoint exposes internals
- Symptom: Operational endpoints leak sensitive details.
- Diagnostic goal: Separate endpoint exposure from health detail visibility.

### Buggy code

```java
management.endpoints.web.exposure.include=*
management.endpoint.health.show-details=always
```

### Expected diagnosis

Wildcard exposure and unrestricted details reveal environment and dependency information.

### Corrected code

```java
management.endpoints.web.exposure.include=health,info
management.endpoint.health.show-details=when_authorized
```

### Regression tests

```java
// Unauthenticated probes see status without credentials or connection details.
```

## SB3-M-094: test profile not activated

- Difficulty: Medium
- Framework: Spring Boot 3
- Language: Java
- Perspective: Profiles
- Concept: test profile not activated
- Symptom: Tests connect to a developer database.
- Diagnostic goal: Make the test environment explicit and isolated.

### Buggy code

```java
@SpringBootTest
class RepositoryTest {}
```

### Expected diagnosis

Without a test profile, normal application properties can select an external database.

### Corrected code

```java
@SpringBootTest
@ActiveProfiles("test")
class RepositoryTest {}
```

### Regression tests

```java
// Test execution uses the embedded or containerized test datasource.
```

## SB3-M-095: correlation id lost

- Difficulty: Medium
- Framework: Spring Boot 3
- Language: Java
- Perspective: Observability
- Concept: correlation id lost
- Symptom: Logs from one request cannot be joined across services.
- Diagnostic goal: Create and clear request-scoped diagnostic context.

### Buggy code

```java
filterChain.doFilter(request, response);
```

### Expected diagnosis

The request proceeds without installing a correlation value and without cleanup.

### Corrected code

```java
try { MDC.put("requestId", requestId); filterChain.doFilter(request, response); } finally { MDC.remove("requestId"); }
```

### Regression tests

```java
// Every log line has the request id and the thread is clean afterward.
```

## SB3-M-096: Java time format mismatch

- Difficulty: Medium
- Framework: Spring Boot 3
- Language: Java
- Perspective: Serialization
- Concept: Java time format mismatch
- Symptom: Clients reject the response date.
- Diagnostic goal: Declare the wire format at the API boundary.

### Buggy code

```java
record Event(Instant createdAt) {}
```

### Expected diagnosis

The default representation may differ from the documented contract or client expectation.

### Corrected code

```java
record Event(@JsonFormat(pattern = "yyyy-MM-dd'T'HH:mm:ssX") Instant createdAt) {}
```

### Regression tests

```java
// Contract test asserts the exact serialized timestamp.
```

## SB3-M-097: circular bean dependency

- Difficulty: Medium
- Framework: Spring Boot 3
- Language: Java
- Perspective: Startup
- Concept: circular bean dependency
- Symptom: ApplicationContext fails during startup.
- Diagnostic goal: Break the cycle at the architecture boundary.

### Buggy code

```java
class A { A(B b) {} }
class B { B(A a) {} }
```

### Expected diagnosis

Constructor injection exposes a cycle that cannot be resolved safely.

### Corrected code

```java
class A { A(Port port) {} }
class B implements Port { B() {} }
```

### Regression tests

```java
// Context starts and each service depends on an interface with one direction.
```

## SB3-M-098: unbounded upstream timeout

- Difficulty: Medium
- Framework: Spring Boot 3
- Language: Java
- Perspective: HTTP client
- Concept: unbounded upstream timeout
- Symptom: A slow dependency exhausts request threads.
- Diagnostic goal: Set connect and response timeouts and define fallback behavior.

### Buggy code

```java
return restClient.get().uri(uri).retrieve().body(String.class);
```

### Expected diagnosis

Without timeouts, an unavailable upstream can hold workers indefinitely.

### Corrected code

```java
return restClient.get().uri(uri).retrieve().onStatus(s -> s.value() == 404, r -> new NotFoundException()).body(String.class);
```

### Regression tests

```java
// Slow and error responses produce bounded, documented outcomes.
```

## SB3-M-099: graceful shutdown disabled

- Difficulty: Medium
- Framework: Spring Boot 3
- Language: Java
- Perspective: Deployment
- Concept: graceful shutdown disabled
- Symptom: In-flight requests are cut off during rollout.
- Diagnostic goal: Enable graceful shutdown and give the platform enough time.

### Buggy code

```java
server.shutdown=immediate
```

### Expected diagnosis

Immediate shutdown drops active requests and can interrupt transactions.

### Corrected code

```java
server.shutdown=graceful
spring.lifecycle.timeout-per-shutdown-phase=30s
```

### Regression tests

```java
// A shutdown waits for active work up to the configured deadline.
```

## SB3-M-100: configuration accepted without validation

- Difficulty: Medium
- Framework: Spring Boot 3
- Language: Java
- Perspective: Validation
- Concept: configuration accepted without validation
- Symptom: The app starts with an invalid port or URL.
- Diagnostic goal: Validate configuration at binding time.

### Buggy code

```java
record ClientProperties(String baseUrl, int timeoutMs) {}
```

### Expected diagnosis

Invalid values surface only when the first request is made.

### Corrected code

```java
record ClientProperties(@jakarta.validation.constraints.NotBlank String baseUrl, @jakarta.validation.constraints.Positive int timeoutMs) {}
```

### Regression tests

```java
// Invalid configuration fails context startup with a useful property path.
```

## SB3-H-001: profile property mismatch

- Difficulty: Hard
- Framework: Spring Boot 3
- Language: Java
- Perspective: Configuration
- Concept: profile property mismatch
- Symptom: The production datasource is not configured.
- Diagnostic goal: Trace active profiles and property source precedence.

### Buggy code

```java
@Value("${app.url}")
private String url;
```

### Expected diagnosis

The property may exist only under a different profile or prefix; startup failure is clearer than a silent default.

### Corrected code

```java
@ConfigurationProperties(prefix = "app")
public record AppProperties(String url) {}
```

### Regression tests

```java
// Run with each profile and assert the expected URL is bound.
```

## SB3-H-002: missing starter dependency

- Difficulty: Hard
- Framework: Spring Boot 3
- Language: Java
- Perspective: Auto-configuration
- Concept: missing starter dependency
- Symptom: A configured feature has no bean at runtime.
- Diagnostic goal: Map the requested behavior to its Boot starter and auto-configuration.

### Buggy code

```java
@Bean
SecurityFilterChain chain(HttpSecurity http) { return http.build(); }
```

### Expected diagnosis

A security configuration cannot work if the relevant starter and transitive infrastructure are absent.

### Corrected code

```java
dependencies { implementation("org.springframework.boot:spring-boot-starter-security") }
```

### Regression tests

```java
// Include spring-boot-starter-security and assert the context starts.
```

## SB3-H-003: health endpoint exposes internals

- Difficulty: Hard
- Framework: Spring Boot 3
- Language: Java
- Perspective: Actuator
- Concept: health endpoint exposes internals
- Symptom: Operational endpoints leak sensitive details.
- Diagnostic goal: Separate endpoint exposure from health detail visibility.

### Buggy code

```java
management.endpoints.web.exposure.include=*
management.endpoint.health.show-details=always
```

### Expected diagnosis

Wildcard exposure and unrestricted details reveal environment and dependency information.

### Corrected code

```java
management.endpoints.web.exposure.include=health,info
management.endpoint.health.show-details=when_authorized
```

### Regression tests

```java
// Unauthenticated probes see status without credentials or connection details.
```

## SB3-H-004: test profile not activated

- Difficulty: Hard
- Framework: Spring Boot 3
- Language: Java
- Perspective: Profiles
- Concept: test profile not activated
- Symptom: Tests connect to a developer database.
- Diagnostic goal: Make the test environment explicit and isolated.

### Buggy code

```java
@SpringBootTest
class RepositoryTest {}
```

### Expected diagnosis

Without a test profile, normal application properties can select an external database.

### Corrected code

```java
@SpringBootTest
@ActiveProfiles("test")
class RepositoryTest {}
```

### Regression tests

```java
// Test execution uses the embedded or containerized test datasource.
```

## SB3-H-005: correlation id lost

- Difficulty: Hard
- Framework: Spring Boot 3
- Language: Java
- Perspective: Observability
- Concept: correlation id lost
- Symptom: Logs from one request cannot be joined across services.
- Diagnostic goal: Create and clear request-scoped diagnostic context.

### Buggy code

```java
filterChain.doFilter(request, response);
```

### Expected diagnosis

The request proceeds without installing a correlation value and without cleanup.

### Corrected code

```java
try { MDC.put("requestId", requestId); filterChain.doFilter(request, response); } finally { MDC.remove("requestId"); }
```

### Regression tests

```java
// Every log line has the request id and the thread is clean afterward.
```

## SB3-H-006: Java time format mismatch

- Difficulty: Hard
- Framework: Spring Boot 3
- Language: Java
- Perspective: Serialization
- Concept: Java time format mismatch
- Symptom: Clients reject the response date.
- Diagnostic goal: Declare the wire format at the API boundary.

### Buggy code

```java
record Event(Instant createdAt) {}
```

### Expected diagnosis

The default representation may differ from the documented contract or client expectation.

### Corrected code

```java
record Event(@JsonFormat(pattern = "yyyy-MM-dd'T'HH:mm:ssX") Instant createdAt) {}
```

### Regression tests

```java
// Contract test asserts the exact serialized timestamp.
```

## SB3-H-007: circular bean dependency

- Difficulty: Hard
- Framework: Spring Boot 3
- Language: Java
- Perspective: Startup
- Concept: circular bean dependency
- Symptom: ApplicationContext fails during startup.
- Diagnostic goal: Break the cycle at the architecture boundary.

### Buggy code

```java
class A { A(B b) {} }
class B { B(A a) {} }
```

### Expected diagnosis

Constructor injection exposes a cycle that cannot be resolved safely.

### Corrected code

```java
class A { A(Port port) {} }
class B implements Port { B() {} }
```

### Regression tests

```java
// Context starts and each service depends on an interface with one direction.
```

## SB3-H-008: unbounded upstream timeout

- Difficulty: Hard
- Framework: Spring Boot 3
- Language: Java
- Perspective: HTTP client
- Concept: unbounded upstream timeout
- Symptom: A slow dependency exhausts request threads.
- Diagnostic goal: Set connect and response timeouts and define fallback behavior.

### Buggy code

```java
return restClient.get().uri(uri).retrieve().body(String.class);
```

### Expected diagnosis

Without timeouts, an unavailable upstream can hold workers indefinitely.

### Corrected code

```java
return restClient.get().uri(uri).retrieve().onStatus(s -> s.value() == 404, r -> new NotFoundException()).body(String.class);
```

### Regression tests

```java
// Slow and error responses produce bounded, documented outcomes.
```

## SB3-H-009: graceful shutdown disabled

- Difficulty: Hard
- Framework: Spring Boot 3
- Language: Java
- Perspective: Deployment
- Concept: graceful shutdown disabled
- Symptom: In-flight requests are cut off during rollout.
- Diagnostic goal: Enable graceful shutdown and give the platform enough time.

### Buggy code

```java
server.shutdown=immediate
```

### Expected diagnosis

Immediate shutdown drops active requests and can interrupt transactions.

### Corrected code

```java
server.shutdown=graceful
spring.lifecycle.timeout-per-shutdown-phase=30s
```

### Regression tests

```java
// A shutdown waits for active work up to the configured deadline.
```

## SB3-H-010: configuration accepted without validation

- Difficulty: Hard
- Framework: Spring Boot 3
- Language: Java
- Perspective: Validation
- Concept: configuration accepted without validation
- Symptom: The app starts with an invalid port or URL.
- Diagnostic goal: Validate configuration at binding time.

### Buggy code

```java
record ClientProperties(String baseUrl, int timeoutMs) {}
```

### Expected diagnosis

Invalid values surface only when the first request is made.

### Corrected code

```java
record ClientProperties(@jakarta.validation.constraints.NotBlank String baseUrl, @jakarta.validation.constraints.Positive int timeoutMs) {}
```

### Regression tests

```java
// Invalid configuration fails context startup with a useful property path.
```

## SB3-H-011: profile property mismatch

- Difficulty: Hard
- Framework: Spring Boot 3
- Language: Java
- Perspective: Configuration
- Concept: profile property mismatch
- Symptom: The production datasource is not configured.
- Diagnostic goal: Trace active profiles and property source precedence.

### Buggy code

```java
@Value("${app.url}")
private String url;
```

### Expected diagnosis

The property may exist only under a different profile or prefix; startup failure is clearer than a silent default.

### Corrected code

```java
@ConfigurationProperties(prefix = "app")
public record AppProperties(String url) {}
```

### Regression tests

```java
// Run with each profile and assert the expected URL is bound.
```

## SB3-H-012: missing starter dependency

- Difficulty: Hard
- Framework: Spring Boot 3
- Language: Java
- Perspective: Auto-configuration
- Concept: missing starter dependency
- Symptom: A configured feature has no bean at runtime.
- Diagnostic goal: Map the requested behavior to its Boot starter and auto-configuration.

### Buggy code

```java
@Bean
SecurityFilterChain chain(HttpSecurity http) { return http.build(); }
```

### Expected diagnosis

A security configuration cannot work if the relevant starter and transitive infrastructure are absent.

### Corrected code

```java
dependencies { implementation("org.springframework.boot:spring-boot-starter-security") }
```

### Regression tests

```java
// Include spring-boot-starter-security and assert the context starts.
```

## SB3-H-013: health endpoint exposes internals

- Difficulty: Hard
- Framework: Spring Boot 3
- Language: Java
- Perspective: Actuator
- Concept: health endpoint exposes internals
- Symptom: Operational endpoints leak sensitive details.
- Diagnostic goal: Separate endpoint exposure from health detail visibility.

### Buggy code

```java
management.endpoints.web.exposure.include=*
management.endpoint.health.show-details=always
```

### Expected diagnosis

Wildcard exposure and unrestricted details reveal environment and dependency information.

### Corrected code

```java
management.endpoints.web.exposure.include=health,info
management.endpoint.health.show-details=when_authorized
```

### Regression tests

```java
// Unauthenticated probes see status without credentials or connection details.
```

## SB3-H-014: test profile not activated

- Difficulty: Hard
- Framework: Spring Boot 3
- Language: Java
- Perspective: Profiles
- Concept: test profile not activated
- Symptom: Tests connect to a developer database.
- Diagnostic goal: Make the test environment explicit and isolated.

### Buggy code

```java
@SpringBootTest
class RepositoryTest {}
```

### Expected diagnosis

Without a test profile, normal application properties can select an external database.

### Corrected code

```java
@SpringBootTest
@ActiveProfiles("test")
class RepositoryTest {}
```

### Regression tests

```java
// Test execution uses the embedded or containerized test datasource.
```

## SB3-H-015: correlation id lost

- Difficulty: Hard
- Framework: Spring Boot 3
- Language: Java
- Perspective: Observability
- Concept: correlation id lost
- Symptom: Logs from one request cannot be joined across services.
- Diagnostic goal: Create and clear request-scoped diagnostic context.

### Buggy code

```java
filterChain.doFilter(request, response);
```

### Expected diagnosis

The request proceeds without installing a correlation value and without cleanup.

### Corrected code

```java
try { MDC.put("requestId", requestId); filterChain.doFilter(request, response); } finally { MDC.remove("requestId"); }
```

### Regression tests

```java
// Every log line has the request id and the thread is clean afterward.
```

## SB3-H-016: Java time format mismatch

- Difficulty: Hard
- Framework: Spring Boot 3
- Language: Java
- Perspective: Serialization
- Concept: Java time format mismatch
- Symptom: Clients reject the response date.
- Diagnostic goal: Declare the wire format at the API boundary.

### Buggy code

```java
record Event(Instant createdAt) {}
```

### Expected diagnosis

The default representation may differ from the documented contract or client expectation.

### Corrected code

```java
record Event(@JsonFormat(pattern = "yyyy-MM-dd'T'HH:mm:ssX") Instant createdAt) {}
```

### Regression tests

```java
// Contract test asserts the exact serialized timestamp.
```

## SB3-H-017: circular bean dependency

- Difficulty: Hard
- Framework: Spring Boot 3
- Language: Java
- Perspective: Startup
- Concept: circular bean dependency
- Symptom: ApplicationContext fails during startup.
- Diagnostic goal: Break the cycle at the architecture boundary.

### Buggy code

```java
class A { A(B b) {} }
class B { B(A a) {} }
```

### Expected diagnosis

Constructor injection exposes a cycle that cannot be resolved safely.

### Corrected code

```java
class A { A(Port port) {} }
class B implements Port { B() {} }
```

### Regression tests

```java
// Context starts and each service depends on an interface with one direction.
```

## SB3-H-018: unbounded upstream timeout

- Difficulty: Hard
- Framework: Spring Boot 3
- Language: Java
- Perspective: HTTP client
- Concept: unbounded upstream timeout
- Symptom: A slow dependency exhausts request threads.
- Diagnostic goal: Set connect and response timeouts and define fallback behavior.

### Buggy code

```java
return restClient.get().uri(uri).retrieve().body(String.class);
```

### Expected diagnosis

Without timeouts, an unavailable upstream can hold workers indefinitely.

### Corrected code

```java
return restClient.get().uri(uri).retrieve().onStatus(s -> s.value() == 404, r -> new NotFoundException()).body(String.class);
```

### Regression tests

```java
// Slow and error responses produce bounded, documented outcomes.
```

## SB3-H-019: graceful shutdown disabled

- Difficulty: Hard
- Framework: Spring Boot 3
- Language: Java
- Perspective: Deployment
- Concept: graceful shutdown disabled
- Symptom: In-flight requests are cut off during rollout.
- Diagnostic goal: Enable graceful shutdown and give the platform enough time.

### Buggy code

```java
server.shutdown=immediate
```

### Expected diagnosis

Immediate shutdown drops active requests and can interrupt transactions.

### Corrected code

```java
server.shutdown=graceful
spring.lifecycle.timeout-per-shutdown-phase=30s
```

### Regression tests

```java
// A shutdown waits for active work up to the configured deadline.
```

## SB3-H-020: configuration accepted without validation

- Difficulty: Hard
- Framework: Spring Boot 3
- Language: Java
- Perspective: Validation
- Concept: configuration accepted without validation
- Symptom: The app starts with an invalid port or URL.
- Diagnostic goal: Validate configuration at binding time.

### Buggy code

```java
record ClientProperties(String baseUrl, int timeoutMs) {}
```

### Expected diagnosis

Invalid values surface only when the first request is made.

### Corrected code

```java
record ClientProperties(@jakarta.validation.constraints.NotBlank String baseUrl, @jakarta.validation.constraints.Positive int timeoutMs) {}
```

### Regression tests

```java
// Invalid configuration fails context startup with a useful property path.
```

## SB3-H-021: profile property mismatch

- Difficulty: Hard
- Framework: Spring Boot 3
- Language: Java
- Perspective: Configuration
- Concept: profile property mismatch
- Symptom: The production datasource is not configured.
- Diagnostic goal: Trace active profiles and property source precedence.

### Buggy code

```java
@Value("${app.url}")
private String url;
```

### Expected diagnosis

The property may exist only under a different profile or prefix; startup failure is clearer than a silent default.

### Corrected code

```java
@ConfigurationProperties(prefix = "app")
public record AppProperties(String url) {}
```

### Regression tests

```java
// Run with each profile and assert the expected URL is bound.
```

## SB3-H-022: missing starter dependency

- Difficulty: Hard
- Framework: Spring Boot 3
- Language: Java
- Perspective: Auto-configuration
- Concept: missing starter dependency
- Symptom: A configured feature has no bean at runtime.
- Diagnostic goal: Map the requested behavior to its Boot starter and auto-configuration.

### Buggy code

```java
@Bean
SecurityFilterChain chain(HttpSecurity http) { return http.build(); }
```

### Expected diagnosis

A security configuration cannot work if the relevant starter and transitive infrastructure are absent.

### Corrected code

```java
dependencies { implementation("org.springframework.boot:spring-boot-starter-security") }
```

### Regression tests

```java
// Include spring-boot-starter-security and assert the context starts.
```

## SB3-H-023: health endpoint exposes internals

- Difficulty: Hard
- Framework: Spring Boot 3
- Language: Java
- Perspective: Actuator
- Concept: health endpoint exposes internals
- Symptom: Operational endpoints leak sensitive details.
- Diagnostic goal: Separate endpoint exposure from health detail visibility.

### Buggy code

```java
management.endpoints.web.exposure.include=*
management.endpoint.health.show-details=always
```

### Expected diagnosis

Wildcard exposure and unrestricted details reveal environment and dependency information.

### Corrected code

```java
management.endpoints.web.exposure.include=health,info
management.endpoint.health.show-details=when_authorized
```

### Regression tests

```java
// Unauthenticated probes see status without credentials or connection details.
```

## SB3-H-024: test profile not activated

- Difficulty: Hard
- Framework: Spring Boot 3
- Language: Java
- Perspective: Profiles
- Concept: test profile not activated
- Symptom: Tests connect to a developer database.
- Diagnostic goal: Make the test environment explicit and isolated.

### Buggy code

```java
@SpringBootTest
class RepositoryTest {}
```

### Expected diagnosis

Without a test profile, normal application properties can select an external database.

### Corrected code

```java
@SpringBootTest
@ActiveProfiles("test")
class RepositoryTest {}
```

### Regression tests

```java
// Test execution uses the embedded or containerized test datasource.
```

## SB3-H-025: correlation id lost

- Difficulty: Hard
- Framework: Spring Boot 3
- Language: Java
- Perspective: Observability
- Concept: correlation id lost
- Symptom: Logs from one request cannot be joined across services.
- Diagnostic goal: Create and clear request-scoped diagnostic context.

### Buggy code

```java
filterChain.doFilter(request, response);
```

### Expected diagnosis

The request proceeds without installing a correlation value and without cleanup.

### Corrected code

```java
try { MDC.put("requestId", requestId); filterChain.doFilter(request, response); } finally { MDC.remove("requestId"); }
```

### Regression tests

```java
// Every log line has the request id and the thread is clean afterward.
```

## SB3-H-026: Java time format mismatch

- Difficulty: Hard
- Framework: Spring Boot 3
- Language: Java
- Perspective: Serialization
- Concept: Java time format mismatch
- Symptom: Clients reject the response date.
- Diagnostic goal: Declare the wire format at the API boundary.

### Buggy code

```java
record Event(Instant createdAt) {}
```

### Expected diagnosis

The default representation may differ from the documented contract or client expectation.

### Corrected code

```java
record Event(@JsonFormat(pattern = "yyyy-MM-dd'T'HH:mm:ssX") Instant createdAt) {}
```

### Regression tests

```java
// Contract test asserts the exact serialized timestamp.
```

## SB3-H-027: circular bean dependency

- Difficulty: Hard
- Framework: Spring Boot 3
- Language: Java
- Perspective: Startup
- Concept: circular bean dependency
- Symptom: ApplicationContext fails during startup.
- Diagnostic goal: Break the cycle at the architecture boundary.

### Buggy code

```java
class A { A(B b) {} }
class B { B(A a) {} }
```

### Expected diagnosis

Constructor injection exposes a cycle that cannot be resolved safely.

### Corrected code

```java
class A { A(Port port) {} }
class B implements Port { B() {} }
```

### Regression tests

```java
// Context starts and each service depends on an interface with one direction.
```

## SB3-H-028: unbounded upstream timeout

- Difficulty: Hard
- Framework: Spring Boot 3
- Language: Java
- Perspective: HTTP client
- Concept: unbounded upstream timeout
- Symptom: A slow dependency exhausts request threads.
- Diagnostic goal: Set connect and response timeouts and define fallback behavior.

### Buggy code

```java
return restClient.get().uri(uri).retrieve().body(String.class);
```

### Expected diagnosis

Without timeouts, an unavailable upstream can hold workers indefinitely.

### Corrected code

```java
return restClient.get().uri(uri).retrieve().onStatus(s -> s.value() == 404, r -> new NotFoundException()).body(String.class);
```

### Regression tests

```java
// Slow and error responses produce bounded, documented outcomes.
```

## SB3-H-029: graceful shutdown disabled

- Difficulty: Hard
- Framework: Spring Boot 3
- Language: Java
- Perspective: Deployment
- Concept: graceful shutdown disabled
- Symptom: In-flight requests are cut off during rollout.
- Diagnostic goal: Enable graceful shutdown and give the platform enough time.

### Buggy code

```java
server.shutdown=immediate
```

### Expected diagnosis

Immediate shutdown drops active requests and can interrupt transactions.

### Corrected code

```java
server.shutdown=graceful
spring.lifecycle.timeout-per-shutdown-phase=30s
```

### Regression tests

```java
// A shutdown waits for active work up to the configured deadline.
```

## SB3-H-030: configuration accepted without validation

- Difficulty: Hard
- Framework: Spring Boot 3
- Language: Java
- Perspective: Validation
- Concept: configuration accepted without validation
- Symptom: The app starts with an invalid port or URL.
- Diagnostic goal: Validate configuration at binding time.

### Buggy code

```java
record ClientProperties(String baseUrl, int timeoutMs) {}
```

### Expected diagnosis

Invalid values surface only when the first request is made.

### Corrected code

```java
record ClientProperties(@jakarta.validation.constraints.NotBlank String baseUrl, @jakarta.validation.constraints.Positive int timeoutMs) {}
```

### Regression tests

```java
// Invalid configuration fails context startup with a useful property path.
```

## SB3-H-031: profile property mismatch

- Difficulty: Hard
- Framework: Spring Boot 3
- Language: Java
- Perspective: Configuration
- Concept: profile property mismatch
- Symptom: The production datasource is not configured.
- Diagnostic goal: Trace active profiles and property source precedence.

### Buggy code

```java
@Value("${app.url}")
private String url;
```

### Expected diagnosis

The property may exist only under a different profile or prefix; startup failure is clearer than a silent default.

### Corrected code

```java
@ConfigurationProperties(prefix = "app")
public record AppProperties(String url) {}
```

### Regression tests

```java
// Run with each profile and assert the expected URL is bound.
```

## SB3-H-032: missing starter dependency

- Difficulty: Hard
- Framework: Spring Boot 3
- Language: Java
- Perspective: Auto-configuration
- Concept: missing starter dependency
- Symptom: A configured feature has no bean at runtime.
- Diagnostic goal: Map the requested behavior to its Boot starter and auto-configuration.

### Buggy code

```java
@Bean
SecurityFilterChain chain(HttpSecurity http) { return http.build(); }
```

### Expected diagnosis

A security configuration cannot work if the relevant starter and transitive infrastructure are absent.

### Corrected code

```java
dependencies { implementation("org.springframework.boot:spring-boot-starter-security") }
```

### Regression tests

```java
// Include spring-boot-starter-security and assert the context starts.
```

## SB3-H-033: health endpoint exposes internals

- Difficulty: Hard
- Framework: Spring Boot 3
- Language: Java
- Perspective: Actuator
- Concept: health endpoint exposes internals
- Symptom: Operational endpoints leak sensitive details.
- Diagnostic goal: Separate endpoint exposure from health detail visibility.

### Buggy code

```java
management.endpoints.web.exposure.include=*
management.endpoint.health.show-details=always
```

### Expected diagnosis

Wildcard exposure and unrestricted details reveal environment and dependency information.

### Corrected code

```java
management.endpoints.web.exposure.include=health,info
management.endpoint.health.show-details=when_authorized
```

### Regression tests

```java
// Unauthenticated probes see status without credentials or connection details.
```

## SB3-H-034: test profile not activated

- Difficulty: Hard
- Framework: Spring Boot 3
- Language: Java
- Perspective: Profiles
- Concept: test profile not activated
- Symptom: Tests connect to a developer database.
- Diagnostic goal: Make the test environment explicit and isolated.

### Buggy code

```java
@SpringBootTest
class RepositoryTest {}
```

### Expected diagnosis

Without a test profile, normal application properties can select an external database.

### Corrected code

```java
@SpringBootTest
@ActiveProfiles("test")
class RepositoryTest {}
```

### Regression tests

```java
// Test execution uses the embedded or containerized test datasource.
```

## SB3-H-035: correlation id lost

- Difficulty: Hard
- Framework: Spring Boot 3
- Language: Java
- Perspective: Observability
- Concept: correlation id lost
- Symptom: Logs from one request cannot be joined across services.
- Diagnostic goal: Create and clear request-scoped diagnostic context.

### Buggy code

```java
filterChain.doFilter(request, response);
```

### Expected diagnosis

The request proceeds without installing a correlation value and without cleanup.

### Corrected code

```java
try { MDC.put("requestId", requestId); filterChain.doFilter(request, response); } finally { MDC.remove("requestId"); }
```

### Regression tests

```java
// Every log line has the request id and the thread is clean afterward.
```

## SB3-H-036: Java time format mismatch

- Difficulty: Hard
- Framework: Spring Boot 3
- Language: Java
- Perspective: Serialization
- Concept: Java time format mismatch
- Symptom: Clients reject the response date.
- Diagnostic goal: Declare the wire format at the API boundary.

### Buggy code

```java
record Event(Instant createdAt) {}
```

### Expected diagnosis

The default representation may differ from the documented contract or client expectation.

### Corrected code

```java
record Event(@JsonFormat(pattern = "yyyy-MM-dd'T'HH:mm:ssX") Instant createdAt) {}
```

### Regression tests

```java
// Contract test asserts the exact serialized timestamp.
```

## SB3-H-037: circular bean dependency

- Difficulty: Hard
- Framework: Spring Boot 3
- Language: Java
- Perspective: Startup
- Concept: circular bean dependency
- Symptom: ApplicationContext fails during startup.
- Diagnostic goal: Break the cycle at the architecture boundary.

### Buggy code

```java
class A { A(B b) {} }
class B { B(A a) {} }
```

### Expected diagnosis

Constructor injection exposes a cycle that cannot be resolved safely.

### Corrected code

```java
class A { A(Port port) {} }
class B implements Port { B() {} }
```

### Regression tests

```java
// Context starts and each service depends on an interface with one direction.
```

## SB3-H-038: unbounded upstream timeout

- Difficulty: Hard
- Framework: Spring Boot 3
- Language: Java
- Perspective: HTTP client
- Concept: unbounded upstream timeout
- Symptom: A slow dependency exhausts request threads.
- Diagnostic goal: Set connect and response timeouts and define fallback behavior.

### Buggy code

```java
return restClient.get().uri(uri).retrieve().body(String.class);
```

### Expected diagnosis

Without timeouts, an unavailable upstream can hold workers indefinitely.

### Corrected code

```java
return restClient.get().uri(uri).retrieve().onStatus(s -> s.value() == 404, r -> new NotFoundException()).body(String.class);
```

### Regression tests

```java
// Slow and error responses produce bounded, documented outcomes.
```

## SB3-H-039: graceful shutdown disabled

- Difficulty: Hard
- Framework: Spring Boot 3
- Language: Java
- Perspective: Deployment
- Concept: graceful shutdown disabled
- Symptom: In-flight requests are cut off during rollout.
- Diagnostic goal: Enable graceful shutdown and give the platform enough time.

### Buggy code

```java
server.shutdown=immediate
```

### Expected diagnosis

Immediate shutdown drops active requests and can interrupt transactions.

### Corrected code

```java
server.shutdown=graceful
spring.lifecycle.timeout-per-shutdown-phase=30s
```

### Regression tests

```java
// A shutdown waits for active work up to the configured deadline.
```

## SB3-H-040: configuration accepted without validation

- Difficulty: Hard
- Framework: Spring Boot 3
- Language: Java
- Perspective: Validation
- Concept: configuration accepted without validation
- Symptom: The app starts with an invalid port or URL.
- Diagnostic goal: Validate configuration at binding time.

### Buggy code

```java
record ClientProperties(String baseUrl, int timeoutMs) {}
```

### Expected diagnosis

Invalid values surface only when the first request is made.

### Corrected code

```java
record ClientProperties(@jakarta.validation.constraints.NotBlank String baseUrl, @jakarta.validation.constraints.Positive int timeoutMs) {}
```

### Regression tests

```java
// Invalid configuration fails context startup with a useful property path.
```

## SB3-H-041: profile property mismatch

- Difficulty: Hard
- Framework: Spring Boot 3
- Language: Java
- Perspective: Configuration
- Concept: profile property mismatch
- Symptom: The production datasource is not configured.
- Diagnostic goal: Trace active profiles and property source precedence.

### Buggy code

```java
@Value("${app.url}")
private String url;
```

### Expected diagnosis

The property may exist only under a different profile or prefix; startup failure is clearer than a silent default.

### Corrected code

```java
@ConfigurationProperties(prefix = "app")
public record AppProperties(String url) {}
```

### Regression tests

```java
// Run with each profile and assert the expected URL is bound.
```

## SB3-H-042: missing starter dependency

- Difficulty: Hard
- Framework: Spring Boot 3
- Language: Java
- Perspective: Auto-configuration
- Concept: missing starter dependency
- Symptom: A configured feature has no bean at runtime.
- Diagnostic goal: Map the requested behavior to its Boot starter and auto-configuration.

### Buggy code

```java
@Bean
SecurityFilterChain chain(HttpSecurity http) { return http.build(); }
```

### Expected diagnosis

A security configuration cannot work if the relevant starter and transitive infrastructure are absent.

### Corrected code

```java
dependencies { implementation("org.springframework.boot:spring-boot-starter-security") }
```

### Regression tests

```java
// Include spring-boot-starter-security and assert the context starts.
```

## SB3-H-043: health endpoint exposes internals

- Difficulty: Hard
- Framework: Spring Boot 3
- Language: Java
- Perspective: Actuator
- Concept: health endpoint exposes internals
- Symptom: Operational endpoints leak sensitive details.
- Diagnostic goal: Separate endpoint exposure from health detail visibility.

### Buggy code

```java
management.endpoints.web.exposure.include=*
management.endpoint.health.show-details=always
```

### Expected diagnosis

Wildcard exposure and unrestricted details reveal environment and dependency information.

### Corrected code

```java
management.endpoints.web.exposure.include=health,info
management.endpoint.health.show-details=when_authorized
```

### Regression tests

```java
// Unauthenticated probes see status without credentials or connection details.
```

## SB3-H-044: test profile not activated

- Difficulty: Hard
- Framework: Spring Boot 3
- Language: Java
- Perspective: Profiles
- Concept: test profile not activated
- Symptom: Tests connect to a developer database.
- Diagnostic goal: Make the test environment explicit and isolated.

### Buggy code

```java
@SpringBootTest
class RepositoryTest {}
```

### Expected diagnosis

Without a test profile, normal application properties can select an external database.

### Corrected code

```java
@SpringBootTest
@ActiveProfiles("test")
class RepositoryTest {}
```

### Regression tests

```java
// Test execution uses the embedded or containerized test datasource.
```

## SB3-H-045: correlation id lost

- Difficulty: Hard
- Framework: Spring Boot 3
- Language: Java
- Perspective: Observability
- Concept: correlation id lost
- Symptom: Logs from one request cannot be joined across services.
- Diagnostic goal: Create and clear request-scoped diagnostic context.

### Buggy code

```java
filterChain.doFilter(request, response);
```

### Expected diagnosis

The request proceeds without installing a correlation value and without cleanup.

### Corrected code

```java
try { MDC.put("requestId", requestId); filterChain.doFilter(request, response); } finally { MDC.remove("requestId"); }
```

### Regression tests

```java
// Every log line has the request id and the thread is clean afterward.
```

## SB3-H-046: Java time format mismatch

- Difficulty: Hard
- Framework: Spring Boot 3
- Language: Java
- Perspective: Serialization
- Concept: Java time format mismatch
- Symptom: Clients reject the response date.
- Diagnostic goal: Declare the wire format at the API boundary.

### Buggy code

```java
record Event(Instant createdAt) {}
```

### Expected diagnosis

The default representation may differ from the documented contract or client expectation.

### Corrected code

```java
record Event(@JsonFormat(pattern = "yyyy-MM-dd'T'HH:mm:ssX") Instant createdAt) {}
```

### Regression tests

```java
// Contract test asserts the exact serialized timestamp.
```

## SB3-H-047: circular bean dependency

- Difficulty: Hard
- Framework: Spring Boot 3
- Language: Java
- Perspective: Startup
- Concept: circular bean dependency
- Symptom: ApplicationContext fails during startup.
- Diagnostic goal: Break the cycle at the architecture boundary.

### Buggy code

```java
class A { A(B b) {} }
class B { B(A a) {} }
```

### Expected diagnosis

Constructor injection exposes a cycle that cannot be resolved safely.

### Corrected code

```java
class A { A(Port port) {} }
class B implements Port { B() {} }
```

### Regression tests

```java
// Context starts and each service depends on an interface with one direction.
```

## SB3-H-048: unbounded upstream timeout

- Difficulty: Hard
- Framework: Spring Boot 3
- Language: Java
- Perspective: HTTP client
- Concept: unbounded upstream timeout
- Symptom: A slow dependency exhausts request threads.
- Diagnostic goal: Set connect and response timeouts and define fallback behavior.

### Buggy code

```java
return restClient.get().uri(uri).retrieve().body(String.class);
```

### Expected diagnosis

Without timeouts, an unavailable upstream can hold workers indefinitely.

### Corrected code

```java
return restClient.get().uri(uri).retrieve().onStatus(s -> s.value() == 404, r -> new NotFoundException()).body(String.class);
```

### Regression tests

```java
// Slow and error responses produce bounded, documented outcomes.
```

## SB3-H-049: graceful shutdown disabled

- Difficulty: Hard
- Framework: Spring Boot 3
- Language: Java
- Perspective: Deployment
- Concept: graceful shutdown disabled
- Symptom: In-flight requests are cut off during rollout.
- Diagnostic goal: Enable graceful shutdown and give the platform enough time.

### Buggy code

```java
server.shutdown=immediate
```

### Expected diagnosis

Immediate shutdown drops active requests and can interrupt transactions.

### Corrected code

```java
server.shutdown=graceful
spring.lifecycle.timeout-per-shutdown-phase=30s
```

### Regression tests

```java
// A shutdown waits for active work up to the configured deadline.
```

## SB3-H-050: configuration accepted without validation

- Difficulty: Hard
- Framework: Spring Boot 3
- Language: Java
- Perspective: Validation
- Concept: configuration accepted without validation
- Symptom: The app starts with an invalid port or URL.
- Diagnostic goal: Validate configuration at binding time.

### Buggy code

```java
record ClientProperties(String baseUrl, int timeoutMs) {}
```

### Expected diagnosis

Invalid values surface only when the first request is made.

### Corrected code

```java
record ClientProperties(@jakarta.validation.constraints.NotBlank String baseUrl, @jakarta.validation.constraints.Positive int timeoutMs) {}
```

### Regression tests

```java
// Invalid configuration fails context startup with a useful property path.
```

## SB3-H-051: profile property mismatch

- Difficulty: Hard
- Framework: Spring Boot 3
- Language: Java
- Perspective: Configuration
- Concept: profile property mismatch
- Symptom: The production datasource is not configured.
- Diagnostic goal: Trace active profiles and property source precedence.

### Buggy code

```java
@Value("${app.url}")
private String url;
```

### Expected diagnosis

The property may exist only under a different profile or prefix; startup failure is clearer than a silent default.

### Corrected code

```java
@ConfigurationProperties(prefix = "app")
public record AppProperties(String url) {}
```

### Regression tests

```java
// Run with each profile and assert the expected URL is bound.
```

## SB3-H-052: missing starter dependency

- Difficulty: Hard
- Framework: Spring Boot 3
- Language: Java
- Perspective: Auto-configuration
- Concept: missing starter dependency
- Symptom: A configured feature has no bean at runtime.
- Diagnostic goal: Map the requested behavior to its Boot starter and auto-configuration.

### Buggy code

```java
@Bean
SecurityFilterChain chain(HttpSecurity http) { return http.build(); }
```

### Expected diagnosis

A security configuration cannot work if the relevant starter and transitive infrastructure are absent.

### Corrected code

```java
dependencies { implementation("org.springframework.boot:spring-boot-starter-security") }
```

### Regression tests

```java
// Include spring-boot-starter-security and assert the context starts.
```

## SB3-H-053: health endpoint exposes internals

- Difficulty: Hard
- Framework: Spring Boot 3
- Language: Java
- Perspective: Actuator
- Concept: health endpoint exposes internals
- Symptom: Operational endpoints leak sensitive details.
- Diagnostic goal: Separate endpoint exposure from health detail visibility.

### Buggy code

```java
management.endpoints.web.exposure.include=*
management.endpoint.health.show-details=always
```

### Expected diagnosis

Wildcard exposure and unrestricted details reveal environment and dependency information.

### Corrected code

```java
management.endpoints.web.exposure.include=health,info
management.endpoint.health.show-details=when_authorized
```

### Regression tests

```java
// Unauthenticated probes see status without credentials or connection details.
```

## SB3-H-054: test profile not activated

- Difficulty: Hard
- Framework: Spring Boot 3
- Language: Java
- Perspective: Profiles
- Concept: test profile not activated
- Symptom: Tests connect to a developer database.
- Diagnostic goal: Make the test environment explicit and isolated.

### Buggy code

```java
@SpringBootTest
class RepositoryTest {}
```

### Expected diagnosis

Without a test profile, normal application properties can select an external database.

### Corrected code

```java
@SpringBootTest
@ActiveProfiles("test")
class RepositoryTest {}
```

### Regression tests

```java
// Test execution uses the embedded or containerized test datasource.
```

## SB3-H-055: correlation id lost

- Difficulty: Hard
- Framework: Spring Boot 3
- Language: Java
- Perspective: Observability
- Concept: correlation id lost
- Symptom: Logs from one request cannot be joined across services.
- Diagnostic goal: Create and clear request-scoped diagnostic context.

### Buggy code

```java
filterChain.doFilter(request, response);
```

### Expected diagnosis

The request proceeds without installing a correlation value and without cleanup.

### Corrected code

```java
try { MDC.put("requestId", requestId); filterChain.doFilter(request, response); } finally { MDC.remove("requestId"); }
```

### Regression tests

```java
// Every log line has the request id and the thread is clean afterward.
```

## SB3-H-056: Java time format mismatch

- Difficulty: Hard
- Framework: Spring Boot 3
- Language: Java
- Perspective: Serialization
- Concept: Java time format mismatch
- Symptom: Clients reject the response date.
- Diagnostic goal: Declare the wire format at the API boundary.

### Buggy code

```java
record Event(Instant createdAt) {}
```

### Expected diagnosis

The default representation may differ from the documented contract or client expectation.

### Corrected code

```java
record Event(@JsonFormat(pattern = "yyyy-MM-dd'T'HH:mm:ssX") Instant createdAt) {}
```

### Regression tests

```java
// Contract test asserts the exact serialized timestamp.
```

## SB3-H-057: circular bean dependency

- Difficulty: Hard
- Framework: Spring Boot 3
- Language: Java
- Perspective: Startup
- Concept: circular bean dependency
- Symptom: ApplicationContext fails during startup.
- Diagnostic goal: Break the cycle at the architecture boundary.

### Buggy code

```java
class A { A(B b) {} }
class B { B(A a) {} }
```

### Expected diagnosis

Constructor injection exposes a cycle that cannot be resolved safely.

### Corrected code

```java
class A { A(Port port) {} }
class B implements Port { B() {} }
```

### Regression tests

```java
// Context starts and each service depends on an interface with one direction.
```

## SB3-H-058: unbounded upstream timeout

- Difficulty: Hard
- Framework: Spring Boot 3
- Language: Java
- Perspective: HTTP client
- Concept: unbounded upstream timeout
- Symptom: A slow dependency exhausts request threads.
- Diagnostic goal: Set connect and response timeouts and define fallback behavior.

### Buggy code

```java
return restClient.get().uri(uri).retrieve().body(String.class);
```

### Expected diagnosis

Without timeouts, an unavailable upstream can hold workers indefinitely.

### Corrected code

```java
return restClient.get().uri(uri).retrieve().onStatus(s -> s.value() == 404, r -> new NotFoundException()).body(String.class);
```

### Regression tests

```java
// Slow and error responses produce bounded, documented outcomes.
```

## SB3-H-059: graceful shutdown disabled

- Difficulty: Hard
- Framework: Spring Boot 3
- Language: Java
- Perspective: Deployment
- Concept: graceful shutdown disabled
- Symptom: In-flight requests are cut off during rollout.
- Diagnostic goal: Enable graceful shutdown and give the platform enough time.

### Buggy code

```java
server.shutdown=immediate
```

### Expected diagnosis

Immediate shutdown drops active requests and can interrupt transactions.

### Corrected code

```java
server.shutdown=graceful
spring.lifecycle.timeout-per-shutdown-phase=30s
```

### Regression tests

```java
// A shutdown waits for active work up to the configured deadline.
```

## SB3-H-060: configuration accepted without validation

- Difficulty: Hard
- Framework: Spring Boot 3
- Language: Java
- Perspective: Validation
- Concept: configuration accepted without validation
- Symptom: The app starts with an invalid port or URL.
- Diagnostic goal: Validate configuration at binding time.

### Buggy code

```java
record ClientProperties(String baseUrl, int timeoutMs) {}
```

### Expected diagnosis

Invalid values surface only when the first request is made.

### Corrected code

```java
record ClientProperties(@jakarta.validation.constraints.NotBlank String baseUrl, @jakarta.validation.constraints.Positive int timeoutMs) {}
```

### Regression tests

```java
// Invalid configuration fails context startup with a useful property path.
```

## SB3-H-061: profile property mismatch

- Difficulty: Hard
- Framework: Spring Boot 3
- Language: Java
- Perspective: Configuration
- Concept: profile property mismatch
- Symptom: The production datasource is not configured.
- Diagnostic goal: Trace active profiles and property source precedence.

### Buggy code

```java
@Value("${app.url}")
private String url;
```

### Expected diagnosis

The property may exist only under a different profile or prefix; startup failure is clearer than a silent default.

### Corrected code

```java
@ConfigurationProperties(prefix = "app")
public record AppProperties(String url) {}
```

### Regression tests

```java
// Run with each profile and assert the expected URL is bound.
```

## SB3-H-062: missing starter dependency

- Difficulty: Hard
- Framework: Spring Boot 3
- Language: Java
- Perspective: Auto-configuration
- Concept: missing starter dependency
- Symptom: A configured feature has no bean at runtime.
- Diagnostic goal: Map the requested behavior to its Boot starter and auto-configuration.

### Buggy code

```java
@Bean
SecurityFilterChain chain(HttpSecurity http) { return http.build(); }
```

### Expected diagnosis

A security configuration cannot work if the relevant starter and transitive infrastructure are absent.

### Corrected code

```java
dependencies { implementation("org.springframework.boot:spring-boot-starter-security") }
```

### Regression tests

```java
// Include spring-boot-starter-security and assert the context starts.
```

## SB3-H-063: health endpoint exposes internals

- Difficulty: Hard
- Framework: Spring Boot 3
- Language: Java
- Perspective: Actuator
- Concept: health endpoint exposes internals
- Symptom: Operational endpoints leak sensitive details.
- Diagnostic goal: Separate endpoint exposure from health detail visibility.

### Buggy code

```java
management.endpoints.web.exposure.include=*
management.endpoint.health.show-details=always
```

### Expected diagnosis

Wildcard exposure and unrestricted details reveal environment and dependency information.

### Corrected code

```java
management.endpoints.web.exposure.include=health,info
management.endpoint.health.show-details=when_authorized
```

### Regression tests

```java
// Unauthenticated probes see status without credentials or connection details.
```

## SB3-H-064: test profile not activated

- Difficulty: Hard
- Framework: Spring Boot 3
- Language: Java
- Perspective: Profiles
- Concept: test profile not activated
- Symptom: Tests connect to a developer database.
- Diagnostic goal: Make the test environment explicit and isolated.

### Buggy code

```java
@SpringBootTest
class RepositoryTest {}
```

### Expected diagnosis

Without a test profile, normal application properties can select an external database.

### Corrected code

```java
@SpringBootTest
@ActiveProfiles("test")
class RepositoryTest {}
```

### Regression tests

```java
// Test execution uses the embedded or containerized test datasource.
```

## SB3-H-065: correlation id lost

- Difficulty: Hard
- Framework: Spring Boot 3
- Language: Java
- Perspective: Observability
- Concept: correlation id lost
- Symptom: Logs from one request cannot be joined across services.
- Diagnostic goal: Create and clear request-scoped diagnostic context.

### Buggy code

```java
filterChain.doFilter(request, response);
```

### Expected diagnosis

The request proceeds without installing a correlation value and without cleanup.

### Corrected code

```java
try { MDC.put("requestId", requestId); filterChain.doFilter(request, response); } finally { MDC.remove("requestId"); }
```

### Regression tests

```java
// Every log line has the request id and the thread is clean afterward.
```

## SB3-H-066: Java time format mismatch

- Difficulty: Hard
- Framework: Spring Boot 3
- Language: Java
- Perspective: Serialization
- Concept: Java time format mismatch
- Symptom: Clients reject the response date.
- Diagnostic goal: Declare the wire format at the API boundary.

### Buggy code

```java
record Event(Instant createdAt) {}
```

### Expected diagnosis

The default representation may differ from the documented contract or client expectation.

### Corrected code

```java
record Event(@JsonFormat(pattern = "yyyy-MM-dd'T'HH:mm:ssX") Instant createdAt) {}
```

### Regression tests

```java
// Contract test asserts the exact serialized timestamp.
```

## SB3-H-067: circular bean dependency

- Difficulty: Hard
- Framework: Spring Boot 3
- Language: Java
- Perspective: Startup
- Concept: circular bean dependency
- Symptom: ApplicationContext fails during startup.
- Diagnostic goal: Break the cycle at the architecture boundary.

### Buggy code

```java
class A { A(B b) {} }
class B { B(A a) {} }
```

### Expected diagnosis

Constructor injection exposes a cycle that cannot be resolved safely.

### Corrected code

```java
class A { A(Port port) {} }
class B implements Port { B() {} }
```

### Regression tests

```java
// Context starts and each service depends on an interface with one direction.
```

## SB3-H-068: unbounded upstream timeout

- Difficulty: Hard
- Framework: Spring Boot 3
- Language: Java
- Perspective: HTTP client
- Concept: unbounded upstream timeout
- Symptom: A slow dependency exhausts request threads.
- Diagnostic goal: Set connect and response timeouts and define fallback behavior.

### Buggy code

```java
return restClient.get().uri(uri).retrieve().body(String.class);
```

### Expected diagnosis

Without timeouts, an unavailable upstream can hold workers indefinitely.

### Corrected code

```java
return restClient.get().uri(uri).retrieve().onStatus(s -> s.value() == 404, r -> new NotFoundException()).body(String.class);
```

### Regression tests

```java
// Slow and error responses produce bounded, documented outcomes.
```

## SB3-H-069: graceful shutdown disabled

- Difficulty: Hard
- Framework: Spring Boot 3
- Language: Java
- Perspective: Deployment
- Concept: graceful shutdown disabled
- Symptom: In-flight requests are cut off during rollout.
- Diagnostic goal: Enable graceful shutdown and give the platform enough time.

### Buggy code

```java
server.shutdown=immediate
```

### Expected diagnosis

Immediate shutdown drops active requests and can interrupt transactions.

### Corrected code

```java
server.shutdown=graceful
spring.lifecycle.timeout-per-shutdown-phase=30s
```

### Regression tests

```java
// A shutdown waits for active work up to the configured deadline.
```

## SB3-H-070: configuration accepted without validation

- Difficulty: Hard
- Framework: Spring Boot 3
- Language: Java
- Perspective: Validation
- Concept: configuration accepted without validation
- Symptom: The app starts with an invalid port or URL.
- Diagnostic goal: Validate configuration at binding time.

### Buggy code

```java
record ClientProperties(String baseUrl, int timeoutMs) {}
```

### Expected diagnosis

Invalid values surface only when the first request is made.

### Corrected code

```java
record ClientProperties(@jakarta.validation.constraints.NotBlank String baseUrl, @jakarta.validation.constraints.Positive int timeoutMs) {}
```

### Regression tests

```java
// Invalid configuration fails context startup with a useful property path.
```

## SB3-H-071: profile property mismatch

- Difficulty: Hard
- Framework: Spring Boot 3
- Language: Java
- Perspective: Configuration
- Concept: profile property mismatch
- Symptom: The production datasource is not configured.
- Diagnostic goal: Trace active profiles and property source precedence.

### Buggy code

```java
@Value("${app.url}")
private String url;
```

### Expected diagnosis

The property may exist only under a different profile or prefix; startup failure is clearer than a silent default.

### Corrected code

```java
@ConfigurationProperties(prefix = "app")
public record AppProperties(String url) {}
```

### Regression tests

```java
// Run with each profile and assert the expected URL is bound.
```

## SB3-H-072: missing starter dependency

- Difficulty: Hard
- Framework: Spring Boot 3
- Language: Java
- Perspective: Auto-configuration
- Concept: missing starter dependency
- Symptom: A configured feature has no bean at runtime.
- Diagnostic goal: Map the requested behavior to its Boot starter and auto-configuration.

### Buggy code

```java
@Bean
SecurityFilterChain chain(HttpSecurity http) { return http.build(); }
```

### Expected diagnosis

A security configuration cannot work if the relevant starter and transitive infrastructure are absent.

### Corrected code

```java
dependencies { implementation("org.springframework.boot:spring-boot-starter-security") }
```

### Regression tests

```java
// Include spring-boot-starter-security and assert the context starts.
```

## SB3-H-073: health endpoint exposes internals

- Difficulty: Hard
- Framework: Spring Boot 3
- Language: Java
- Perspective: Actuator
- Concept: health endpoint exposes internals
- Symptom: Operational endpoints leak sensitive details.
- Diagnostic goal: Separate endpoint exposure from health detail visibility.

### Buggy code

```java
management.endpoints.web.exposure.include=*
management.endpoint.health.show-details=always
```

### Expected diagnosis

Wildcard exposure and unrestricted details reveal environment and dependency information.

### Corrected code

```java
management.endpoints.web.exposure.include=health,info
management.endpoint.health.show-details=when_authorized
```

### Regression tests

```java
// Unauthenticated probes see status without credentials or connection details.
```

## SB3-H-074: test profile not activated

- Difficulty: Hard
- Framework: Spring Boot 3
- Language: Java
- Perspective: Profiles
- Concept: test profile not activated
- Symptom: Tests connect to a developer database.
- Diagnostic goal: Make the test environment explicit and isolated.

### Buggy code

```java
@SpringBootTest
class RepositoryTest {}
```

### Expected diagnosis

Without a test profile, normal application properties can select an external database.

### Corrected code

```java
@SpringBootTest
@ActiveProfiles("test")
class RepositoryTest {}
```

### Regression tests

```java
// Test execution uses the embedded or containerized test datasource.
```

## SB3-H-075: correlation id lost

- Difficulty: Hard
- Framework: Spring Boot 3
- Language: Java
- Perspective: Observability
- Concept: correlation id lost
- Symptom: Logs from one request cannot be joined across services.
- Diagnostic goal: Create and clear request-scoped diagnostic context.

### Buggy code

```java
filterChain.doFilter(request, response);
```

### Expected diagnosis

The request proceeds without installing a correlation value and without cleanup.

### Corrected code

```java
try { MDC.put("requestId", requestId); filterChain.doFilter(request, response); } finally { MDC.remove("requestId"); }
```

### Regression tests

```java
// Every log line has the request id and the thread is clean afterward.
```

## SB3-H-076: Java time format mismatch

- Difficulty: Hard
- Framework: Spring Boot 3
- Language: Java
- Perspective: Serialization
- Concept: Java time format mismatch
- Symptom: Clients reject the response date.
- Diagnostic goal: Declare the wire format at the API boundary.

### Buggy code

```java
record Event(Instant createdAt) {}
```

### Expected diagnosis

The default representation may differ from the documented contract or client expectation.

### Corrected code

```java
record Event(@JsonFormat(pattern = "yyyy-MM-dd'T'HH:mm:ssX") Instant createdAt) {}
```

### Regression tests

```java
// Contract test asserts the exact serialized timestamp.
```

## SB3-H-077: circular bean dependency

- Difficulty: Hard
- Framework: Spring Boot 3
- Language: Java
- Perspective: Startup
- Concept: circular bean dependency
- Symptom: ApplicationContext fails during startup.
- Diagnostic goal: Break the cycle at the architecture boundary.

### Buggy code

```java
class A { A(B b) {} }
class B { B(A a) {} }
```

### Expected diagnosis

Constructor injection exposes a cycle that cannot be resolved safely.

### Corrected code

```java
class A { A(Port port) {} }
class B implements Port { B() {} }
```

### Regression tests

```java
// Context starts and each service depends on an interface with one direction.
```

## SB3-H-078: unbounded upstream timeout

- Difficulty: Hard
- Framework: Spring Boot 3
- Language: Java
- Perspective: HTTP client
- Concept: unbounded upstream timeout
- Symptom: A slow dependency exhausts request threads.
- Diagnostic goal: Set connect and response timeouts and define fallback behavior.

### Buggy code

```java
return restClient.get().uri(uri).retrieve().body(String.class);
```

### Expected diagnosis

Without timeouts, an unavailable upstream can hold workers indefinitely.

### Corrected code

```java
return restClient.get().uri(uri).retrieve().onStatus(s -> s.value() == 404, r -> new NotFoundException()).body(String.class);
```

### Regression tests

```java
// Slow and error responses produce bounded, documented outcomes.
```

## SB3-H-079: graceful shutdown disabled

- Difficulty: Hard
- Framework: Spring Boot 3
- Language: Java
- Perspective: Deployment
- Concept: graceful shutdown disabled
- Symptom: In-flight requests are cut off during rollout.
- Diagnostic goal: Enable graceful shutdown and give the platform enough time.

### Buggy code

```java
server.shutdown=immediate
```

### Expected diagnosis

Immediate shutdown drops active requests and can interrupt transactions.

### Corrected code

```java
server.shutdown=graceful
spring.lifecycle.timeout-per-shutdown-phase=30s
```

### Regression tests

```java
// A shutdown waits for active work up to the configured deadline.
```

## SB3-H-080: configuration accepted without validation

- Difficulty: Hard
- Framework: Spring Boot 3
- Language: Java
- Perspective: Validation
- Concept: configuration accepted without validation
- Symptom: The app starts with an invalid port or URL.
- Diagnostic goal: Validate configuration at binding time.

### Buggy code

```java
record ClientProperties(String baseUrl, int timeoutMs) {}
```

### Expected diagnosis

Invalid values surface only when the first request is made.

### Corrected code

```java
record ClientProperties(@jakarta.validation.constraints.NotBlank String baseUrl, @jakarta.validation.constraints.Positive int timeoutMs) {}
```

### Regression tests

```java
// Invalid configuration fails context startup with a useful property path.
```

## SB3-H-081: profile property mismatch

- Difficulty: Hard
- Framework: Spring Boot 3
- Language: Java
- Perspective: Configuration
- Concept: profile property mismatch
- Symptom: The production datasource is not configured.
- Diagnostic goal: Trace active profiles and property source precedence.

### Buggy code

```java
@Value("${app.url}")
private String url;
```

### Expected diagnosis

The property may exist only under a different profile or prefix; startup failure is clearer than a silent default.

### Corrected code

```java
@ConfigurationProperties(prefix = "app")
public record AppProperties(String url) {}
```

### Regression tests

```java
// Run with each profile and assert the expected URL is bound.
```

## SB3-H-082: missing starter dependency

- Difficulty: Hard
- Framework: Spring Boot 3
- Language: Java
- Perspective: Auto-configuration
- Concept: missing starter dependency
- Symptom: A configured feature has no bean at runtime.
- Diagnostic goal: Map the requested behavior to its Boot starter and auto-configuration.

### Buggy code

```java
@Bean
SecurityFilterChain chain(HttpSecurity http) { return http.build(); }
```

### Expected diagnosis

A security configuration cannot work if the relevant starter and transitive infrastructure are absent.

### Corrected code

```java
dependencies { implementation("org.springframework.boot:spring-boot-starter-security") }
```

### Regression tests

```java
// Include spring-boot-starter-security and assert the context starts.
```

## SB3-H-083: health endpoint exposes internals

- Difficulty: Hard
- Framework: Spring Boot 3
- Language: Java
- Perspective: Actuator
- Concept: health endpoint exposes internals
- Symptom: Operational endpoints leak sensitive details.
- Diagnostic goal: Separate endpoint exposure from health detail visibility.

### Buggy code

```java
management.endpoints.web.exposure.include=*
management.endpoint.health.show-details=always
```

### Expected diagnosis

Wildcard exposure and unrestricted details reveal environment and dependency information.

### Corrected code

```java
management.endpoints.web.exposure.include=health,info
management.endpoint.health.show-details=when_authorized
```

### Regression tests

```java
// Unauthenticated probes see status without credentials or connection details.
```

## SB3-H-084: test profile not activated

- Difficulty: Hard
- Framework: Spring Boot 3
- Language: Java
- Perspective: Profiles
- Concept: test profile not activated
- Symptom: Tests connect to a developer database.
- Diagnostic goal: Make the test environment explicit and isolated.

### Buggy code

```java
@SpringBootTest
class RepositoryTest {}
```

### Expected diagnosis

Without a test profile, normal application properties can select an external database.

### Corrected code

```java
@SpringBootTest
@ActiveProfiles("test")
class RepositoryTest {}
```

### Regression tests

```java
// Test execution uses the embedded or containerized test datasource.
```

## SB3-H-085: correlation id lost

- Difficulty: Hard
- Framework: Spring Boot 3
- Language: Java
- Perspective: Observability
- Concept: correlation id lost
- Symptom: Logs from one request cannot be joined across services.
- Diagnostic goal: Create and clear request-scoped diagnostic context.

### Buggy code

```java
filterChain.doFilter(request, response);
```

### Expected diagnosis

The request proceeds without installing a correlation value and without cleanup.

### Corrected code

```java
try { MDC.put("requestId", requestId); filterChain.doFilter(request, response); } finally { MDC.remove("requestId"); }
```

### Regression tests

```java
// Every log line has the request id and the thread is clean afterward.
```

## SB3-H-086: Java time format mismatch

- Difficulty: Hard
- Framework: Spring Boot 3
- Language: Java
- Perspective: Serialization
- Concept: Java time format mismatch
- Symptom: Clients reject the response date.
- Diagnostic goal: Declare the wire format at the API boundary.

### Buggy code

```java
record Event(Instant createdAt) {}
```

### Expected diagnosis

The default representation may differ from the documented contract or client expectation.

### Corrected code

```java
record Event(@JsonFormat(pattern = "yyyy-MM-dd'T'HH:mm:ssX") Instant createdAt) {}
```

### Regression tests

```java
// Contract test asserts the exact serialized timestamp.
```

## SB3-H-087: circular bean dependency

- Difficulty: Hard
- Framework: Spring Boot 3
- Language: Java
- Perspective: Startup
- Concept: circular bean dependency
- Symptom: ApplicationContext fails during startup.
- Diagnostic goal: Break the cycle at the architecture boundary.

### Buggy code

```java
class A { A(B b) {} }
class B { B(A a) {} }
```

### Expected diagnosis

Constructor injection exposes a cycle that cannot be resolved safely.

### Corrected code

```java
class A { A(Port port) {} }
class B implements Port { B() {} }
```

### Regression tests

```java
// Context starts and each service depends on an interface with one direction.
```

## SB3-H-088: unbounded upstream timeout

- Difficulty: Hard
- Framework: Spring Boot 3
- Language: Java
- Perspective: HTTP client
- Concept: unbounded upstream timeout
- Symptom: A slow dependency exhausts request threads.
- Diagnostic goal: Set connect and response timeouts and define fallback behavior.

### Buggy code

```java
return restClient.get().uri(uri).retrieve().body(String.class);
```

### Expected diagnosis

Without timeouts, an unavailable upstream can hold workers indefinitely.

### Corrected code

```java
return restClient.get().uri(uri).retrieve().onStatus(s -> s.value() == 404, r -> new NotFoundException()).body(String.class);
```

### Regression tests

```java
// Slow and error responses produce bounded, documented outcomes.
```

## SB3-H-089: graceful shutdown disabled

- Difficulty: Hard
- Framework: Spring Boot 3
- Language: Java
- Perspective: Deployment
- Concept: graceful shutdown disabled
- Symptom: In-flight requests are cut off during rollout.
- Diagnostic goal: Enable graceful shutdown and give the platform enough time.

### Buggy code

```java
server.shutdown=immediate
```

### Expected diagnosis

Immediate shutdown drops active requests and can interrupt transactions.

### Corrected code

```java
server.shutdown=graceful
spring.lifecycle.timeout-per-shutdown-phase=30s
```

### Regression tests

```java
// A shutdown waits for active work up to the configured deadline.
```

## SB3-H-090: configuration accepted without validation

- Difficulty: Hard
- Framework: Spring Boot 3
- Language: Java
- Perspective: Validation
- Concept: configuration accepted without validation
- Symptom: The app starts with an invalid port or URL.
- Diagnostic goal: Validate configuration at binding time.

### Buggy code

```java
record ClientProperties(String baseUrl, int timeoutMs) {}
```

### Expected diagnosis

Invalid values surface only when the first request is made.

### Corrected code

```java
record ClientProperties(@jakarta.validation.constraints.NotBlank String baseUrl, @jakarta.validation.constraints.Positive int timeoutMs) {}
```

### Regression tests

```java
// Invalid configuration fails context startup with a useful property path.
```

## SB3-H-091: profile property mismatch

- Difficulty: Hard
- Framework: Spring Boot 3
- Language: Java
- Perspective: Configuration
- Concept: profile property mismatch
- Symptom: The production datasource is not configured.
- Diagnostic goal: Trace active profiles and property source precedence.

### Buggy code

```java
@Value("${app.url}")
private String url;
```

### Expected diagnosis

The property may exist only under a different profile or prefix; startup failure is clearer than a silent default.

### Corrected code

```java
@ConfigurationProperties(prefix = "app")
public record AppProperties(String url) {}
```

### Regression tests

```java
// Run with each profile and assert the expected URL is bound.
```

## SB3-H-092: missing starter dependency

- Difficulty: Hard
- Framework: Spring Boot 3
- Language: Java
- Perspective: Auto-configuration
- Concept: missing starter dependency
- Symptom: A configured feature has no bean at runtime.
- Diagnostic goal: Map the requested behavior to its Boot starter and auto-configuration.

### Buggy code

```java
@Bean
SecurityFilterChain chain(HttpSecurity http) { return http.build(); }
```

### Expected diagnosis

A security configuration cannot work if the relevant starter and transitive infrastructure are absent.

### Corrected code

```java
dependencies { implementation("org.springframework.boot:spring-boot-starter-security") }
```

### Regression tests

```java
// Include spring-boot-starter-security and assert the context starts.
```

## SB3-H-093: health endpoint exposes internals

- Difficulty: Hard
- Framework: Spring Boot 3
- Language: Java
- Perspective: Actuator
- Concept: health endpoint exposes internals
- Symptom: Operational endpoints leak sensitive details.
- Diagnostic goal: Separate endpoint exposure from health detail visibility.

### Buggy code

```java
management.endpoints.web.exposure.include=*
management.endpoint.health.show-details=always
```

### Expected diagnosis

Wildcard exposure and unrestricted details reveal environment and dependency information.

### Corrected code

```java
management.endpoints.web.exposure.include=health,info
management.endpoint.health.show-details=when_authorized
```

### Regression tests

```java
// Unauthenticated probes see status without credentials or connection details.
```

## SB3-H-094: test profile not activated

- Difficulty: Hard
- Framework: Spring Boot 3
- Language: Java
- Perspective: Profiles
- Concept: test profile not activated
- Symptom: Tests connect to a developer database.
- Diagnostic goal: Make the test environment explicit and isolated.

### Buggy code

```java
@SpringBootTest
class RepositoryTest {}
```

### Expected diagnosis

Without a test profile, normal application properties can select an external database.

### Corrected code

```java
@SpringBootTest
@ActiveProfiles("test")
class RepositoryTest {}
```

### Regression tests

```java
// Test execution uses the embedded or containerized test datasource.
```

## SB3-H-095: correlation id lost

- Difficulty: Hard
- Framework: Spring Boot 3
- Language: Java
- Perspective: Observability
- Concept: correlation id lost
- Symptom: Logs from one request cannot be joined across services.
- Diagnostic goal: Create and clear request-scoped diagnostic context.

### Buggy code

```java
filterChain.doFilter(request, response);
```

### Expected diagnosis

The request proceeds without installing a correlation value and without cleanup.

### Corrected code

```java
try { MDC.put("requestId", requestId); filterChain.doFilter(request, response); } finally { MDC.remove("requestId"); }
```

### Regression tests

```java
// Every log line has the request id and the thread is clean afterward.
```

## SB3-H-096: Java time format mismatch

- Difficulty: Hard
- Framework: Spring Boot 3
- Language: Java
- Perspective: Serialization
- Concept: Java time format mismatch
- Symptom: Clients reject the response date.
- Diagnostic goal: Declare the wire format at the API boundary.

### Buggy code

```java
record Event(Instant createdAt) {}
```

### Expected diagnosis

The default representation may differ from the documented contract or client expectation.

### Corrected code

```java
record Event(@JsonFormat(pattern = "yyyy-MM-dd'T'HH:mm:ssX") Instant createdAt) {}
```

### Regression tests

```java
// Contract test asserts the exact serialized timestamp.
```

## SB3-H-097: circular bean dependency

- Difficulty: Hard
- Framework: Spring Boot 3
- Language: Java
- Perspective: Startup
- Concept: circular bean dependency
- Symptom: ApplicationContext fails during startup.
- Diagnostic goal: Break the cycle at the architecture boundary.

### Buggy code

```java
class A { A(B b) {} }
class B { B(A a) {} }
```

### Expected diagnosis

Constructor injection exposes a cycle that cannot be resolved safely.

### Corrected code

```java
class A { A(Port port) {} }
class B implements Port { B() {} }
```

### Regression tests

```java
// Context starts and each service depends on an interface with one direction.
```

## SB3-H-098: unbounded upstream timeout

- Difficulty: Hard
- Framework: Spring Boot 3
- Language: Java
- Perspective: HTTP client
- Concept: unbounded upstream timeout
- Symptom: A slow dependency exhausts request threads.
- Diagnostic goal: Set connect and response timeouts and define fallback behavior.

### Buggy code

```java
return restClient.get().uri(uri).retrieve().body(String.class);
```

### Expected diagnosis

Without timeouts, an unavailable upstream can hold workers indefinitely.

### Corrected code

```java
return restClient.get().uri(uri).retrieve().onStatus(s -> s.value() == 404, r -> new NotFoundException()).body(String.class);
```

### Regression tests

```java
// Slow and error responses produce bounded, documented outcomes.
```

## SB3-H-099: graceful shutdown disabled

- Difficulty: Hard
- Framework: Spring Boot 3
- Language: Java
- Perspective: Deployment
- Concept: graceful shutdown disabled
- Symptom: In-flight requests are cut off during rollout.
- Diagnostic goal: Enable graceful shutdown and give the platform enough time.

### Buggy code

```java
server.shutdown=immediate
```

### Expected diagnosis

Immediate shutdown drops active requests and can interrupt transactions.

### Corrected code

```java
server.shutdown=graceful
spring.lifecycle.timeout-per-shutdown-phase=30s
```

### Regression tests

```java
// A shutdown waits for active work up to the configured deadline.
```

## SB3-H-100: configuration accepted without validation

- Difficulty: Hard
- Framework: Spring Boot 3
- Language: Java
- Perspective: Validation
- Concept: configuration accepted without validation
- Symptom: The app starts with an invalid port or URL.
- Diagnostic goal: Validate configuration at binding time.

### Buggy code

```java
record ClientProperties(String baseUrl, int timeoutMs) {}
```

### Expected diagnosis

Invalid values surface only when the first request is made.

### Corrected code

```java
record ClientProperties(@jakarta.validation.constraints.NotBlank String baseUrl, @jakarta.validation.constraints.Positive int timeoutMs) {}
```

### Regression tests

```java
// Invalid configuration fails context startup with a useful property path.
```
