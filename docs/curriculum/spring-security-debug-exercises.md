# Spring Security Debug Exercises

A RAG-training corpus of 300 debugging exercises for Spring Security. Each record contains framework-specific metadata, a failure example, an editorial diagnosis, corrected Java/Spring code, and regression guidance. Corrected code is training material and must be stripped from learner-facing challenge responses.

## Coverage

- Easy: 100 exercises
- Medium: 100 exercises
- Hard: 100 exercises
- Perspectives: configuration, lifecycle, proxies, persistence, HTTP contracts, security, testing, transactions, observability, and deployment

## SEC-E-001: permitAll on protected path

- Difficulty: Easy
- Framework: Spring Security
- Language: Java
- Perspective: Filter chain
- Concept: permitAll on protected path
- Symptom: Unauthenticated users access an admin endpoint.
- Diagnostic goal: Order matchers from specific protected paths to general rules.

### Buggy code

```java
authorize.requestMatchers("/**").permitAll()
       .requestMatchers("/admin/**").hasRole("ADMIN")
```

### Expected diagnosis

The catch-all matcher matches first, so the admin rule is unreachable.

### Corrected code

```java
authorize.requestMatchers("/admin/**").hasRole("ADMIN")
       .anyRequest().authenticated()
```

### Regression tests

```java
// Anonymous admin access is 401/403; authenticated users follow role rules.
```

## SEC-E-002: CSRF disabled for browser session

- Difficulty: Easy
- Framework: Spring Security
- Language: Java
- Perspective: CSRF
- Concept: CSRF disabled for browser session
- Symptom: State-changing browser requests lack forgery protection.
- Diagnostic goal: Keep CSRF for cookie-authenticated browser flows.

### Buggy code

```java
http.csrf(csrf -> csrf.disable());
```

### Expected diagnosis

Disabling CSRF globally is unsafe when authentication is carried by cookies.

### Corrected code

```java
http.csrf(Customizer.withDefaults());
```

### Regression tests

```java
// A missing token is rejected for a session-authenticated POST.
```

## SEC-E-003: plain text password

- Difficulty: Easy
- Framework: Spring Security
- Language: Java
- Perspective: Password storage
- Concept: plain text password
- Symptom: A database leak exposes credentials immediately.
- Diagnostic goal: Store adaptive password hashes and compare through the encoder.

### Buggy code

```java
user.setPassword(rawPassword);
```

### Expected diagnosis

Raw passwords are reversible by anyone who obtains the database.

### Corrected code

```java
user.setPassword(passwordEncoder.encode(rawPassword));
```

### Regression tests

```java
// Login matches through passwordEncoder.matches and never compares raw storage.
```

## SEC-E-004: annotation ignored

- Difficulty: Easy
- Framework: Spring Security
- Language: Java
- Perspective: Method security
- Concept: annotation ignored
- Symptom: A role annotation has no effect.
- Diagnostic goal: Enable method security and use the correct authority prefix.

### Buggy code

```java
@PreAuthorize("hasRole("ADMIN")")
public void delete() {}
```

### Expected diagnosis

Method annotations are inactive unless method security is enabled.

### Corrected code

```java
@EnableMethodSecurity
@Configuration
class SecurityConfig {}
```

### Regression tests

```java
// Nonadmins are denied when invoking the method directly through the proxy.
```

## SEC-E-005: signature not checked

- Difficulty: Easy
- Framework: Spring Security
- Language: Java
- Perspective: JWT validation
- Concept: signature not checked
- Symptom: Forged claims authorize a request.
- Diagnostic goal: Verify signature, issuer, audience, and expiry.

### Buggy code

```java
JwtClaims claims = parser.parseUnsecured(token);
```

### Expected diagnosis

Reading claims without verification is equivalent to trusting user input.

### Corrected code

```java
JwtClaims claims = parser.verify(token, key).requireIssuer(issuer).requireAudience(audience).parse();
```

### Regression tests

```java
// Forged, expired, wrong-issuer tokens are rejected.
```

## SEC-E-006: authentication mistaken for authorization

- Difficulty: Easy
- Framework: Spring Security
- Language: Java
- Perspective: Authorization
- Concept: authentication mistaken for authorization
- Symptom: Every signed-in user can perform an admin action.
- Diagnostic goal: Require a permission or role for the operation.

### Buggy code

```java
.anyRequest().authenticated()
```

### Expected diagnosis

Authenticated only proves identity; it does not grant the admin capability.

### Corrected code

```java
.requestMatchers("/admin/**").hasAuthority("admin:write")
```

### Regression tests

```java
// A user without admin:write receives 403.
```

## SEC-E-007: session fixation risk

- Difficulty: Easy
- Framework: Spring Security
- Language: Java
- Perspective: Session policy
- Concept: session fixation risk
- Symptom: The session identifier remains attacker-controlled after login.
- Diagnostic goal: Apply a session fixation protection policy.

### Buggy code

```java
http.sessionManagement(s -> s.sessionFixation(f -> f.none()));
```

### Expected diagnosis

Keeping the pre-login session identifier permits fixation attacks.

### Corrected code

```java
http.sessionManagement(s -> s.sessionFixation(f -> f.changeSessionId()));
```

### Regression tests

```java
// Successful login changes or invalidates the pre-authentication id.
```

## SEC-E-008: security CORS differs from MVC CORS

- Difficulty: Easy
- Framework: Spring Security
- Language: Java
- Perspective: CORS
- Concept: security CORS differs from MVC CORS
- Symptom: Preflight requests are rejected before the controller.
- Diagnostic goal: Configure CORS in the security filter chain with the application policy.

### Buggy code

```java
http.cors(c -> c.disable());
```

### Expected diagnosis

The security chain can reject preflight before MVC configuration is reached.

### Corrected code

```java
http.cors(Customizer.withDefaults());
```

### Regression tests

```java
// OPTIONS preflight receives the configured allow origin and methods.
```

## SEC-E-009: logout endpoint accepts GET

- Difficulty: Easy
- Framework: Spring Security
- Language: Java
- Perspective: Logout
- Concept: logout endpoint accepts GET
- Symptom: A cross-site link can log users out unexpectedly.
- Diagnostic goal: Use POST and CSRF protection for browser logout.

### Buggy code

```java
http.logout(l -> l.logoutRequestMatcher(new AntPathRequestMatcher("/logout", "GET")));
```

### Expected diagnosis

GET should be safe and cannot carry a CSRF-protected state change reliably.

### Corrected code

```java
http.logout(l -> l.logoutUrl("/logout"));
```

### Regression tests

```java
// GET does not log out; CSRF-protected POST does.
```

## SEC-E-010: test user missing authority

- Difficulty: Easy
- Framework: Spring Security
- Language: Java
- Perspective: Testing security
- Concept: test user missing authority
- Symptom: A controller test fails before the business assertion.
- Diagnostic goal: Make the test authentication match the endpoint contract.

### Buggy code

```java
@WebMvcTest
void deletes() { mockMvc.perform(delete("/items/1")); }
```

### Expected diagnosis

The request is anonymous and security correctly denies it.

### Corrected code

```java
@WithMockUser(roles = "ADMIN")
void deletes() { mockMvc.perform(delete("/items/1").with(csrf())); }
```

### Regression tests

```java
// The test supplies both role and CSRF token.
```

## SEC-E-011: permitAll on protected path

- Difficulty: Easy
- Framework: Spring Security
- Language: Java
- Perspective: Filter chain
- Concept: permitAll on protected path
- Symptom: Unauthenticated users access an admin endpoint.
- Diagnostic goal: Order matchers from specific protected paths to general rules.

### Buggy code

```java
authorize.requestMatchers("/**").permitAll()
       .requestMatchers("/admin/**").hasRole("ADMIN")
```

### Expected diagnosis

The catch-all matcher matches first, so the admin rule is unreachable.

### Corrected code

```java
authorize.requestMatchers("/admin/**").hasRole("ADMIN")
       .anyRequest().authenticated()
```

### Regression tests

```java
// Anonymous admin access is 401/403; authenticated users follow role rules.
```

## SEC-E-012: CSRF disabled for browser session

- Difficulty: Easy
- Framework: Spring Security
- Language: Java
- Perspective: CSRF
- Concept: CSRF disabled for browser session
- Symptom: State-changing browser requests lack forgery protection.
- Diagnostic goal: Keep CSRF for cookie-authenticated browser flows.

### Buggy code

```java
http.csrf(csrf -> csrf.disable());
```

### Expected diagnosis

Disabling CSRF globally is unsafe when authentication is carried by cookies.

### Corrected code

```java
http.csrf(Customizer.withDefaults());
```

### Regression tests

```java
// A missing token is rejected for a session-authenticated POST.
```

## SEC-E-013: plain text password

- Difficulty: Easy
- Framework: Spring Security
- Language: Java
- Perspective: Password storage
- Concept: plain text password
- Symptom: A database leak exposes credentials immediately.
- Diagnostic goal: Store adaptive password hashes and compare through the encoder.

### Buggy code

```java
user.setPassword(rawPassword);
```

### Expected diagnosis

Raw passwords are reversible by anyone who obtains the database.

### Corrected code

```java
user.setPassword(passwordEncoder.encode(rawPassword));
```

### Regression tests

```java
// Login matches through passwordEncoder.matches and never compares raw storage.
```

## SEC-E-014: annotation ignored

- Difficulty: Easy
- Framework: Spring Security
- Language: Java
- Perspective: Method security
- Concept: annotation ignored
- Symptom: A role annotation has no effect.
- Diagnostic goal: Enable method security and use the correct authority prefix.

### Buggy code

```java
@PreAuthorize("hasRole("ADMIN")")
public void delete() {}
```

### Expected diagnosis

Method annotations are inactive unless method security is enabled.

### Corrected code

```java
@EnableMethodSecurity
@Configuration
class SecurityConfig {}
```

### Regression tests

```java
// Nonadmins are denied when invoking the method directly through the proxy.
```

## SEC-E-015: signature not checked

- Difficulty: Easy
- Framework: Spring Security
- Language: Java
- Perspective: JWT validation
- Concept: signature not checked
- Symptom: Forged claims authorize a request.
- Diagnostic goal: Verify signature, issuer, audience, and expiry.

### Buggy code

```java
JwtClaims claims = parser.parseUnsecured(token);
```

### Expected diagnosis

Reading claims without verification is equivalent to trusting user input.

### Corrected code

```java
JwtClaims claims = parser.verify(token, key).requireIssuer(issuer).requireAudience(audience).parse();
```

### Regression tests

```java
// Forged, expired, wrong-issuer tokens are rejected.
```

## SEC-E-016: authentication mistaken for authorization

- Difficulty: Easy
- Framework: Spring Security
- Language: Java
- Perspective: Authorization
- Concept: authentication mistaken for authorization
- Symptom: Every signed-in user can perform an admin action.
- Diagnostic goal: Require a permission or role for the operation.

### Buggy code

```java
.anyRequest().authenticated()
```

### Expected diagnosis

Authenticated only proves identity; it does not grant the admin capability.

### Corrected code

```java
.requestMatchers("/admin/**").hasAuthority("admin:write")
```

### Regression tests

```java
// A user without admin:write receives 403.
```

## SEC-E-017: session fixation risk

- Difficulty: Easy
- Framework: Spring Security
- Language: Java
- Perspective: Session policy
- Concept: session fixation risk
- Symptom: The session identifier remains attacker-controlled after login.
- Diagnostic goal: Apply a session fixation protection policy.

### Buggy code

```java
http.sessionManagement(s -> s.sessionFixation(f -> f.none()));
```

### Expected diagnosis

Keeping the pre-login session identifier permits fixation attacks.

### Corrected code

```java
http.sessionManagement(s -> s.sessionFixation(f -> f.changeSessionId()));
```

### Regression tests

```java
// Successful login changes or invalidates the pre-authentication id.
```

## SEC-E-018: security CORS differs from MVC CORS

- Difficulty: Easy
- Framework: Spring Security
- Language: Java
- Perspective: CORS
- Concept: security CORS differs from MVC CORS
- Symptom: Preflight requests are rejected before the controller.
- Diagnostic goal: Configure CORS in the security filter chain with the application policy.

### Buggy code

```java
http.cors(c -> c.disable());
```

### Expected diagnosis

The security chain can reject preflight before MVC configuration is reached.

### Corrected code

```java
http.cors(Customizer.withDefaults());
```

### Regression tests

```java
// OPTIONS preflight receives the configured allow origin and methods.
```

## SEC-E-019: logout endpoint accepts GET

- Difficulty: Easy
- Framework: Spring Security
- Language: Java
- Perspective: Logout
- Concept: logout endpoint accepts GET
- Symptom: A cross-site link can log users out unexpectedly.
- Diagnostic goal: Use POST and CSRF protection for browser logout.

### Buggy code

```java
http.logout(l -> l.logoutRequestMatcher(new AntPathRequestMatcher("/logout", "GET")));
```

### Expected diagnosis

GET should be safe and cannot carry a CSRF-protected state change reliably.

### Corrected code

```java
http.logout(l -> l.logoutUrl("/logout"));
```

### Regression tests

```java
// GET does not log out; CSRF-protected POST does.
```

## SEC-E-020: test user missing authority

- Difficulty: Easy
- Framework: Spring Security
- Language: Java
- Perspective: Testing security
- Concept: test user missing authority
- Symptom: A controller test fails before the business assertion.
- Diagnostic goal: Make the test authentication match the endpoint contract.

### Buggy code

```java
@WebMvcTest
void deletes() { mockMvc.perform(delete("/items/1")); }
```

### Expected diagnosis

The request is anonymous and security correctly denies it.

### Corrected code

```java
@WithMockUser(roles = "ADMIN")
void deletes() { mockMvc.perform(delete("/items/1").with(csrf())); }
```

### Regression tests

```java
// The test supplies both role and CSRF token.
```

## SEC-E-021: permitAll on protected path

- Difficulty: Easy
- Framework: Spring Security
- Language: Java
- Perspective: Filter chain
- Concept: permitAll on protected path
- Symptom: Unauthenticated users access an admin endpoint.
- Diagnostic goal: Order matchers from specific protected paths to general rules.

### Buggy code

```java
authorize.requestMatchers("/**").permitAll()
       .requestMatchers("/admin/**").hasRole("ADMIN")
```

### Expected diagnosis

The catch-all matcher matches first, so the admin rule is unreachable.

### Corrected code

```java
authorize.requestMatchers("/admin/**").hasRole("ADMIN")
       .anyRequest().authenticated()
```

### Regression tests

```java
// Anonymous admin access is 401/403; authenticated users follow role rules.
```

## SEC-E-022: CSRF disabled for browser session

- Difficulty: Easy
- Framework: Spring Security
- Language: Java
- Perspective: CSRF
- Concept: CSRF disabled for browser session
- Symptom: State-changing browser requests lack forgery protection.
- Diagnostic goal: Keep CSRF for cookie-authenticated browser flows.

### Buggy code

```java
http.csrf(csrf -> csrf.disable());
```

### Expected diagnosis

Disabling CSRF globally is unsafe when authentication is carried by cookies.

### Corrected code

```java
http.csrf(Customizer.withDefaults());
```

### Regression tests

```java
// A missing token is rejected for a session-authenticated POST.
```

## SEC-E-023: plain text password

- Difficulty: Easy
- Framework: Spring Security
- Language: Java
- Perspective: Password storage
- Concept: plain text password
- Symptom: A database leak exposes credentials immediately.
- Diagnostic goal: Store adaptive password hashes and compare through the encoder.

### Buggy code

```java
user.setPassword(rawPassword);
```

### Expected diagnosis

Raw passwords are reversible by anyone who obtains the database.

### Corrected code

```java
user.setPassword(passwordEncoder.encode(rawPassword));
```

### Regression tests

```java
// Login matches through passwordEncoder.matches and never compares raw storage.
```

## SEC-E-024: annotation ignored

- Difficulty: Easy
- Framework: Spring Security
- Language: Java
- Perspective: Method security
- Concept: annotation ignored
- Symptom: A role annotation has no effect.
- Diagnostic goal: Enable method security and use the correct authority prefix.

### Buggy code

```java
@PreAuthorize("hasRole("ADMIN")")
public void delete() {}
```

### Expected diagnosis

Method annotations are inactive unless method security is enabled.

### Corrected code

```java
@EnableMethodSecurity
@Configuration
class SecurityConfig {}
```

### Regression tests

```java
// Nonadmins are denied when invoking the method directly through the proxy.
```

## SEC-E-025: signature not checked

- Difficulty: Easy
- Framework: Spring Security
- Language: Java
- Perspective: JWT validation
- Concept: signature not checked
- Symptom: Forged claims authorize a request.
- Diagnostic goal: Verify signature, issuer, audience, and expiry.

### Buggy code

```java
JwtClaims claims = parser.parseUnsecured(token);
```

### Expected diagnosis

Reading claims without verification is equivalent to trusting user input.

### Corrected code

```java
JwtClaims claims = parser.verify(token, key).requireIssuer(issuer).requireAudience(audience).parse();
```

### Regression tests

```java
// Forged, expired, wrong-issuer tokens are rejected.
```

## SEC-E-026: authentication mistaken for authorization

- Difficulty: Easy
- Framework: Spring Security
- Language: Java
- Perspective: Authorization
- Concept: authentication mistaken for authorization
- Symptom: Every signed-in user can perform an admin action.
- Diagnostic goal: Require a permission or role for the operation.

### Buggy code

```java
.anyRequest().authenticated()
```

### Expected diagnosis

Authenticated only proves identity; it does not grant the admin capability.

### Corrected code

```java
.requestMatchers("/admin/**").hasAuthority("admin:write")
```

### Regression tests

```java
// A user without admin:write receives 403.
```

## SEC-E-027: session fixation risk

- Difficulty: Easy
- Framework: Spring Security
- Language: Java
- Perspective: Session policy
- Concept: session fixation risk
- Symptom: The session identifier remains attacker-controlled after login.
- Diagnostic goal: Apply a session fixation protection policy.

### Buggy code

```java
http.sessionManagement(s -> s.sessionFixation(f -> f.none()));
```

### Expected diagnosis

Keeping the pre-login session identifier permits fixation attacks.

### Corrected code

```java
http.sessionManagement(s -> s.sessionFixation(f -> f.changeSessionId()));
```

### Regression tests

```java
// Successful login changes or invalidates the pre-authentication id.
```

## SEC-E-028: security CORS differs from MVC CORS

- Difficulty: Easy
- Framework: Spring Security
- Language: Java
- Perspective: CORS
- Concept: security CORS differs from MVC CORS
- Symptom: Preflight requests are rejected before the controller.
- Diagnostic goal: Configure CORS in the security filter chain with the application policy.

### Buggy code

```java
http.cors(c -> c.disable());
```

### Expected diagnosis

The security chain can reject preflight before MVC configuration is reached.

### Corrected code

```java
http.cors(Customizer.withDefaults());
```

### Regression tests

```java
// OPTIONS preflight receives the configured allow origin and methods.
```

## SEC-E-029: logout endpoint accepts GET

- Difficulty: Easy
- Framework: Spring Security
- Language: Java
- Perspective: Logout
- Concept: logout endpoint accepts GET
- Symptom: A cross-site link can log users out unexpectedly.
- Diagnostic goal: Use POST and CSRF protection for browser logout.

### Buggy code

```java
http.logout(l -> l.logoutRequestMatcher(new AntPathRequestMatcher("/logout", "GET")));
```

### Expected diagnosis

GET should be safe and cannot carry a CSRF-protected state change reliably.

### Corrected code

```java
http.logout(l -> l.logoutUrl("/logout"));
```

### Regression tests

```java
// GET does not log out; CSRF-protected POST does.
```

## SEC-E-030: test user missing authority

- Difficulty: Easy
- Framework: Spring Security
- Language: Java
- Perspective: Testing security
- Concept: test user missing authority
- Symptom: A controller test fails before the business assertion.
- Diagnostic goal: Make the test authentication match the endpoint contract.

### Buggy code

```java
@WebMvcTest
void deletes() { mockMvc.perform(delete("/items/1")); }
```

### Expected diagnosis

The request is anonymous and security correctly denies it.

### Corrected code

```java
@WithMockUser(roles = "ADMIN")
void deletes() { mockMvc.perform(delete("/items/1").with(csrf())); }
```

### Regression tests

```java
// The test supplies both role and CSRF token.
```

## SEC-E-031: permitAll on protected path

- Difficulty: Easy
- Framework: Spring Security
- Language: Java
- Perspective: Filter chain
- Concept: permitAll on protected path
- Symptom: Unauthenticated users access an admin endpoint.
- Diagnostic goal: Order matchers from specific protected paths to general rules.

### Buggy code

```java
authorize.requestMatchers("/**").permitAll()
       .requestMatchers("/admin/**").hasRole("ADMIN")
```

### Expected diagnosis

The catch-all matcher matches first, so the admin rule is unreachable.

### Corrected code

```java
authorize.requestMatchers("/admin/**").hasRole("ADMIN")
       .anyRequest().authenticated()
```

### Regression tests

```java
// Anonymous admin access is 401/403; authenticated users follow role rules.
```

## SEC-E-032: CSRF disabled for browser session

- Difficulty: Easy
- Framework: Spring Security
- Language: Java
- Perspective: CSRF
- Concept: CSRF disabled for browser session
- Symptom: State-changing browser requests lack forgery protection.
- Diagnostic goal: Keep CSRF for cookie-authenticated browser flows.

### Buggy code

```java
http.csrf(csrf -> csrf.disable());
```

### Expected diagnosis

Disabling CSRF globally is unsafe when authentication is carried by cookies.

### Corrected code

```java
http.csrf(Customizer.withDefaults());
```

### Regression tests

```java
// A missing token is rejected for a session-authenticated POST.
```

## SEC-E-033: plain text password

- Difficulty: Easy
- Framework: Spring Security
- Language: Java
- Perspective: Password storage
- Concept: plain text password
- Symptom: A database leak exposes credentials immediately.
- Diagnostic goal: Store adaptive password hashes and compare through the encoder.

### Buggy code

```java
user.setPassword(rawPassword);
```

### Expected diagnosis

Raw passwords are reversible by anyone who obtains the database.

### Corrected code

```java
user.setPassword(passwordEncoder.encode(rawPassword));
```

### Regression tests

```java
// Login matches through passwordEncoder.matches and never compares raw storage.
```

## SEC-E-034: annotation ignored

- Difficulty: Easy
- Framework: Spring Security
- Language: Java
- Perspective: Method security
- Concept: annotation ignored
- Symptom: A role annotation has no effect.
- Diagnostic goal: Enable method security and use the correct authority prefix.

### Buggy code

```java
@PreAuthorize("hasRole("ADMIN")")
public void delete() {}
```

### Expected diagnosis

Method annotations are inactive unless method security is enabled.

### Corrected code

```java
@EnableMethodSecurity
@Configuration
class SecurityConfig {}
```

### Regression tests

```java
// Nonadmins are denied when invoking the method directly through the proxy.
```

## SEC-E-035: signature not checked

- Difficulty: Easy
- Framework: Spring Security
- Language: Java
- Perspective: JWT validation
- Concept: signature not checked
- Symptom: Forged claims authorize a request.
- Diagnostic goal: Verify signature, issuer, audience, and expiry.

### Buggy code

```java
JwtClaims claims = parser.parseUnsecured(token);
```

### Expected diagnosis

Reading claims without verification is equivalent to trusting user input.

### Corrected code

```java
JwtClaims claims = parser.verify(token, key).requireIssuer(issuer).requireAudience(audience).parse();
```

### Regression tests

```java
// Forged, expired, wrong-issuer tokens are rejected.
```

## SEC-E-036: authentication mistaken for authorization

- Difficulty: Easy
- Framework: Spring Security
- Language: Java
- Perspective: Authorization
- Concept: authentication mistaken for authorization
- Symptom: Every signed-in user can perform an admin action.
- Diagnostic goal: Require a permission or role for the operation.

### Buggy code

```java
.anyRequest().authenticated()
```

### Expected diagnosis

Authenticated only proves identity; it does not grant the admin capability.

### Corrected code

```java
.requestMatchers("/admin/**").hasAuthority("admin:write")
```

### Regression tests

```java
// A user without admin:write receives 403.
```

## SEC-E-037: session fixation risk

- Difficulty: Easy
- Framework: Spring Security
- Language: Java
- Perspective: Session policy
- Concept: session fixation risk
- Symptom: The session identifier remains attacker-controlled after login.
- Diagnostic goal: Apply a session fixation protection policy.

### Buggy code

```java
http.sessionManagement(s -> s.sessionFixation(f -> f.none()));
```

### Expected diagnosis

Keeping the pre-login session identifier permits fixation attacks.

### Corrected code

```java
http.sessionManagement(s -> s.sessionFixation(f -> f.changeSessionId()));
```

### Regression tests

```java
// Successful login changes or invalidates the pre-authentication id.
```

## SEC-E-038: security CORS differs from MVC CORS

- Difficulty: Easy
- Framework: Spring Security
- Language: Java
- Perspective: CORS
- Concept: security CORS differs from MVC CORS
- Symptom: Preflight requests are rejected before the controller.
- Diagnostic goal: Configure CORS in the security filter chain with the application policy.

### Buggy code

```java
http.cors(c -> c.disable());
```

### Expected diagnosis

The security chain can reject preflight before MVC configuration is reached.

### Corrected code

```java
http.cors(Customizer.withDefaults());
```

### Regression tests

```java
// OPTIONS preflight receives the configured allow origin and methods.
```

## SEC-E-039: logout endpoint accepts GET

- Difficulty: Easy
- Framework: Spring Security
- Language: Java
- Perspective: Logout
- Concept: logout endpoint accepts GET
- Symptom: A cross-site link can log users out unexpectedly.
- Diagnostic goal: Use POST and CSRF protection for browser logout.

### Buggy code

```java
http.logout(l -> l.logoutRequestMatcher(new AntPathRequestMatcher("/logout", "GET")));
```

### Expected diagnosis

GET should be safe and cannot carry a CSRF-protected state change reliably.

### Corrected code

```java
http.logout(l -> l.logoutUrl("/logout"));
```

### Regression tests

```java
// GET does not log out; CSRF-protected POST does.
```

## SEC-E-040: test user missing authority

- Difficulty: Easy
- Framework: Spring Security
- Language: Java
- Perspective: Testing security
- Concept: test user missing authority
- Symptom: A controller test fails before the business assertion.
- Diagnostic goal: Make the test authentication match the endpoint contract.

### Buggy code

```java
@WebMvcTest
void deletes() { mockMvc.perform(delete("/items/1")); }
```

### Expected diagnosis

The request is anonymous and security correctly denies it.

### Corrected code

```java
@WithMockUser(roles = "ADMIN")
void deletes() { mockMvc.perform(delete("/items/1").with(csrf())); }
```

### Regression tests

```java
// The test supplies both role and CSRF token.
```

## SEC-E-041: permitAll on protected path

- Difficulty: Easy
- Framework: Spring Security
- Language: Java
- Perspective: Filter chain
- Concept: permitAll on protected path
- Symptom: Unauthenticated users access an admin endpoint.
- Diagnostic goal: Order matchers from specific protected paths to general rules.

### Buggy code

```java
authorize.requestMatchers("/**").permitAll()
       .requestMatchers("/admin/**").hasRole("ADMIN")
```

### Expected diagnosis

The catch-all matcher matches first, so the admin rule is unreachable.

### Corrected code

```java
authorize.requestMatchers("/admin/**").hasRole("ADMIN")
       .anyRequest().authenticated()
```

### Regression tests

```java
// Anonymous admin access is 401/403; authenticated users follow role rules.
```

## SEC-E-042: CSRF disabled for browser session

- Difficulty: Easy
- Framework: Spring Security
- Language: Java
- Perspective: CSRF
- Concept: CSRF disabled for browser session
- Symptom: State-changing browser requests lack forgery protection.
- Diagnostic goal: Keep CSRF for cookie-authenticated browser flows.

### Buggy code

```java
http.csrf(csrf -> csrf.disable());
```

### Expected diagnosis

Disabling CSRF globally is unsafe when authentication is carried by cookies.

### Corrected code

```java
http.csrf(Customizer.withDefaults());
```

### Regression tests

```java
// A missing token is rejected for a session-authenticated POST.
```

## SEC-E-043: plain text password

- Difficulty: Easy
- Framework: Spring Security
- Language: Java
- Perspective: Password storage
- Concept: plain text password
- Symptom: A database leak exposes credentials immediately.
- Diagnostic goal: Store adaptive password hashes and compare through the encoder.

### Buggy code

```java
user.setPassword(rawPassword);
```

### Expected diagnosis

Raw passwords are reversible by anyone who obtains the database.

### Corrected code

```java
user.setPassword(passwordEncoder.encode(rawPassword));
```

### Regression tests

```java
// Login matches through passwordEncoder.matches and never compares raw storage.
```

## SEC-E-044: annotation ignored

- Difficulty: Easy
- Framework: Spring Security
- Language: Java
- Perspective: Method security
- Concept: annotation ignored
- Symptom: A role annotation has no effect.
- Diagnostic goal: Enable method security and use the correct authority prefix.

### Buggy code

```java
@PreAuthorize("hasRole("ADMIN")")
public void delete() {}
```

### Expected diagnosis

Method annotations are inactive unless method security is enabled.

### Corrected code

```java
@EnableMethodSecurity
@Configuration
class SecurityConfig {}
```

### Regression tests

```java
// Nonadmins are denied when invoking the method directly through the proxy.
```

## SEC-E-045: signature not checked

- Difficulty: Easy
- Framework: Spring Security
- Language: Java
- Perspective: JWT validation
- Concept: signature not checked
- Symptom: Forged claims authorize a request.
- Diagnostic goal: Verify signature, issuer, audience, and expiry.

### Buggy code

```java
JwtClaims claims = parser.parseUnsecured(token);
```

### Expected diagnosis

Reading claims without verification is equivalent to trusting user input.

### Corrected code

```java
JwtClaims claims = parser.verify(token, key).requireIssuer(issuer).requireAudience(audience).parse();
```

### Regression tests

```java
// Forged, expired, wrong-issuer tokens are rejected.
```

## SEC-E-046: authentication mistaken for authorization

- Difficulty: Easy
- Framework: Spring Security
- Language: Java
- Perspective: Authorization
- Concept: authentication mistaken for authorization
- Symptom: Every signed-in user can perform an admin action.
- Diagnostic goal: Require a permission or role for the operation.

### Buggy code

```java
.anyRequest().authenticated()
```

### Expected diagnosis

Authenticated only proves identity; it does not grant the admin capability.

### Corrected code

```java
.requestMatchers("/admin/**").hasAuthority("admin:write")
```

### Regression tests

```java
// A user without admin:write receives 403.
```

## SEC-E-047: session fixation risk

- Difficulty: Easy
- Framework: Spring Security
- Language: Java
- Perspective: Session policy
- Concept: session fixation risk
- Symptom: The session identifier remains attacker-controlled after login.
- Diagnostic goal: Apply a session fixation protection policy.

### Buggy code

```java
http.sessionManagement(s -> s.sessionFixation(f -> f.none()));
```

### Expected diagnosis

Keeping the pre-login session identifier permits fixation attacks.

### Corrected code

```java
http.sessionManagement(s -> s.sessionFixation(f -> f.changeSessionId()));
```

### Regression tests

```java
// Successful login changes or invalidates the pre-authentication id.
```

## SEC-E-048: security CORS differs from MVC CORS

- Difficulty: Easy
- Framework: Spring Security
- Language: Java
- Perspective: CORS
- Concept: security CORS differs from MVC CORS
- Symptom: Preflight requests are rejected before the controller.
- Diagnostic goal: Configure CORS in the security filter chain with the application policy.

### Buggy code

```java
http.cors(c -> c.disable());
```

### Expected diagnosis

The security chain can reject preflight before MVC configuration is reached.

### Corrected code

```java
http.cors(Customizer.withDefaults());
```

### Regression tests

```java
// OPTIONS preflight receives the configured allow origin and methods.
```

## SEC-E-049: logout endpoint accepts GET

- Difficulty: Easy
- Framework: Spring Security
- Language: Java
- Perspective: Logout
- Concept: logout endpoint accepts GET
- Symptom: A cross-site link can log users out unexpectedly.
- Diagnostic goal: Use POST and CSRF protection for browser logout.

### Buggy code

```java
http.logout(l -> l.logoutRequestMatcher(new AntPathRequestMatcher("/logout", "GET")));
```

### Expected diagnosis

GET should be safe and cannot carry a CSRF-protected state change reliably.

### Corrected code

```java
http.logout(l -> l.logoutUrl("/logout"));
```

### Regression tests

```java
// GET does not log out; CSRF-protected POST does.
```

## SEC-E-050: test user missing authority

- Difficulty: Easy
- Framework: Spring Security
- Language: Java
- Perspective: Testing security
- Concept: test user missing authority
- Symptom: A controller test fails before the business assertion.
- Diagnostic goal: Make the test authentication match the endpoint contract.

### Buggy code

```java
@WebMvcTest
void deletes() { mockMvc.perform(delete("/items/1")); }
```

### Expected diagnosis

The request is anonymous and security correctly denies it.

### Corrected code

```java
@WithMockUser(roles = "ADMIN")
void deletes() { mockMvc.perform(delete("/items/1").with(csrf())); }
```

### Regression tests

```java
// The test supplies both role and CSRF token.
```

## SEC-E-051: permitAll on protected path

- Difficulty: Easy
- Framework: Spring Security
- Language: Java
- Perspective: Filter chain
- Concept: permitAll on protected path
- Symptom: Unauthenticated users access an admin endpoint.
- Diagnostic goal: Order matchers from specific protected paths to general rules.

### Buggy code

```java
authorize.requestMatchers("/**").permitAll()
       .requestMatchers("/admin/**").hasRole("ADMIN")
```

### Expected diagnosis

The catch-all matcher matches first, so the admin rule is unreachable.

### Corrected code

```java
authorize.requestMatchers("/admin/**").hasRole("ADMIN")
       .anyRequest().authenticated()
```

### Regression tests

```java
// Anonymous admin access is 401/403; authenticated users follow role rules.
```

## SEC-E-052: CSRF disabled for browser session

- Difficulty: Easy
- Framework: Spring Security
- Language: Java
- Perspective: CSRF
- Concept: CSRF disabled for browser session
- Symptom: State-changing browser requests lack forgery protection.
- Diagnostic goal: Keep CSRF for cookie-authenticated browser flows.

### Buggy code

```java
http.csrf(csrf -> csrf.disable());
```

### Expected diagnosis

Disabling CSRF globally is unsafe when authentication is carried by cookies.

### Corrected code

```java
http.csrf(Customizer.withDefaults());
```

### Regression tests

```java
// A missing token is rejected for a session-authenticated POST.
```

## SEC-E-053: plain text password

- Difficulty: Easy
- Framework: Spring Security
- Language: Java
- Perspective: Password storage
- Concept: plain text password
- Symptom: A database leak exposes credentials immediately.
- Diagnostic goal: Store adaptive password hashes and compare through the encoder.

### Buggy code

```java
user.setPassword(rawPassword);
```

### Expected diagnosis

Raw passwords are reversible by anyone who obtains the database.

### Corrected code

```java
user.setPassword(passwordEncoder.encode(rawPassword));
```

### Regression tests

```java
// Login matches through passwordEncoder.matches and never compares raw storage.
```

## SEC-E-054: annotation ignored

- Difficulty: Easy
- Framework: Spring Security
- Language: Java
- Perspective: Method security
- Concept: annotation ignored
- Symptom: A role annotation has no effect.
- Diagnostic goal: Enable method security and use the correct authority prefix.

### Buggy code

```java
@PreAuthorize("hasRole("ADMIN")")
public void delete() {}
```

### Expected diagnosis

Method annotations are inactive unless method security is enabled.

### Corrected code

```java
@EnableMethodSecurity
@Configuration
class SecurityConfig {}
```

### Regression tests

```java
// Nonadmins are denied when invoking the method directly through the proxy.
```

## SEC-E-055: signature not checked

- Difficulty: Easy
- Framework: Spring Security
- Language: Java
- Perspective: JWT validation
- Concept: signature not checked
- Symptom: Forged claims authorize a request.
- Diagnostic goal: Verify signature, issuer, audience, and expiry.

### Buggy code

```java
JwtClaims claims = parser.parseUnsecured(token);
```

### Expected diagnosis

Reading claims without verification is equivalent to trusting user input.

### Corrected code

```java
JwtClaims claims = parser.verify(token, key).requireIssuer(issuer).requireAudience(audience).parse();
```

### Regression tests

```java
// Forged, expired, wrong-issuer tokens are rejected.
```

## SEC-E-056: authentication mistaken for authorization

- Difficulty: Easy
- Framework: Spring Security
- Language: Java
- Perspective: Authorization
- Concept: authentication mistaken for authorization
- Symptom: Every signed-in user can perform an admin action.
- Diagnostic goal: Require a permission or role for the operation.

### Buggy code

```java
.anyRequest().authenticated()
```

### Expected diagnosis

Authenticated only proves identity; it does not grant the admin capability.

### Corrected code

```java
.requestMatchers("/admin/**").hasAuthority("admin:write")
```

### Regression tests

```java
// A user without admin:write receives 403.
```

## SEC-E-057: session fixation risk

- Difficulty: Easy
- Framework: Spring Security
- Language: Java
- Perspective: Session policy
- Concept: session fixation risk
- Symptom: The session identifier remains attacker-controlled after login.
- Diagnostic goal: Apply a session fixation protection policy.

### Buggy code

```java
http.sessionManagement(s -> s.sessionFixation(f -> f.none()));
```

### Expected diagnosis

Keeping the pre-login session identifier permits fixation attacks.

### Corrected code

```java
http.sessionManagement(s -> s.sessionFixation(f -> f.changeSessionId()));
```

### Regression tests

```java
// Successful login changes or invalidates the pre-authentication id.
```

## SEC-E-058: security CORS differs from MVC CORS

- Difficulty: Easy
- Framework: Spring Security
- Language: Java
- Perspective: CORS
- Concept: security CORS differs from MVC CORS
- Symptom: Preflight requests are rejected before the controller.
- Diagnostic goal: Configure CORS in the security filter chain with the application policy.

### Buggy code

```java
http.cors(c -> c.disable());
```

### Expected diagnosis

The security chain can reject preflight before MVC configuration is reached.

### Corrected code

```java
http.cors(Customizer.withDefaults());
```

### Regression tests

```java
// OPTIONS preflight receives the configured allow origin and methods.
```

## SEC-E-059: logout endpoint accepts GET

- Difficulty: Easy
- Framework: Spring Security
- Language: Java
- Perspective: Logout
- Concept: logout endpoint accepts GET
- Symptom: A cross-site link can log users out unexpectedly.
- Diagnostic goal: Use POST and CSRF protection for browser logout.

### Buggy code

```java
http.logout(l -> l.logoutRequestMatcher(new AntPathRequestMatcher("/logout", "GET")));
```

### Expected diagnosis

GET should be safe and cannot carry a CSRF-protected state change reliably.

### Corrected code

```java
http.logout(l -> l.logoutUrl("/logout"));
```

### Regression tests

```java
// GET does not log out; CSRF-protected POST does.
```

## SEC-E-060: test user missing authority

- Difficulty: Easy
- Framework: Spring Security
- Language: Java
- Perspective: Testing security
- Concept: test user missing authority
- Symptom: A controller test fails before the business assertion.
- Diagnostic goal: Make the test authentication match the endpoint contract.

### Buggy code

```java
@WebMvcTest
void deletes() { mockMvc.perform(delete("/items/1")); }
```

### Expected diagnosis

The request is anonymous and security correctly denies it.

### Corrected code

```java
@WithMockUser(roles = "ADMIN")
void deletes() { mockMvc.perform(delete("/items/1").with(csrf())); }
```

### Regression tests

```java
// The test supplies both role and CSRF token.
```

## SEC-E-061: permitAll on protected path

- Difficulty: Easy
- Framework: Spring Security
- Language: Java
- Perspective: Filter chain
- Concept: permitAll on protected path
- Symptom: Unauthenticated users access an admin endpoint.
- Diagnostic goal: Order matchers from specific protected paths to general rules.

### Buggy code

```java
authorize.requestMatchers("/**").permitAll()
       .requestMatchers("/admin/**").hasRole("ADMIN")
```

### Expected diagnosis

The catch-all matcher matches first, so the admin rule is unreachable.

### Corrected code

```java
authorize.requestMatchers("/admin/**").hasRole("ADMIN")
       .anyRequest().authenticated()
```

### Regression tests

```java
// Anonymous admin access is 401/403; authenticated users follow role rules.
```

## SEC-E-062: CSRF disabled for browser session

- Difficulty: Easy
- Framework: Spring Security
- Language: Java
- Perspective: CSRF
- Concept: CSRF disabled for browser session
- Symptom: State-changing browser requests lack forgery protection.
- Diagnostic goal: Keep CSRF for cookie-authenticated browser flows.

### Buggy code

```java
http.csrf(csrf -> csrf.disable());
```

### Expected diagnosis

Disabling CSRF globally is unsafe when authentication is carried by cookies.

### Corrected code

```java
http.csrf(Customizer.withDefaults());
```

### Regression tests

```java
// A missing token is rejected for a session-authenticated POST.
```

## SEC-E-063: plain text password

- Difficulty: Easy
- Framework: Spring Security
- Language: Java
- Perspective: Password storage
- Concept: plain text password
- Symptom: A database leak exposes credentials immediately.
- Diagnostic goal: Store adaptive password hashes and compare through the encoder.

### Buggy code

```java
user.setPassword(rawPassword);
```

### Expected diagnosis

Raw passwords are reversible by anyone who obtains the database.

### Corrected code

```java
user.setPassword(passwordEncoder.encode(rawPassword));
```

### Regression tests

```java
// Login matches through passwordEncoder.matches and never compares raw storage.
```

## SEC-E-064: annotation ignored

- Difficulty: Easy
- Framework: Spring Security
- Language: Java
- Perspective: Method security
- Concept: annotation ignored
- Symptom: A role annotation has no effect.
- Diagnostic goal: Enable method security and use the correct authority prefix.

### Buggy code

```java
@PreAuthorize("hasRole("ADMIN")")
public void delete() {}
```

### Expected diagnosis

Method annotations are inactive unless method security is enabled.

### Corrected code

```java
@EnableMethodSecurity
@Configuration
class SecurityConfig {}
```

### Regression tests

```java
// Nonadmins are denied when invoking the method directly through the proxy.
```

## SEC-E-065: signature not checked

- Difficulty: Easy
- Framework: Spring Security
- Language: Java
- Perspective: JWT validation
- Concept: signature not checked
- Symptom: Forged claims authorize a request.
- Diagnostic goal: Verify signature, issuer, audience, and expiry.

### Buggy code

```java
JwtClaims claims = parser.parseUnsecured(token);
```

### Expected diagnosis

Reading claims without verification is equivalent to trusting user input.

### Corrected code

```java
JwtClaims claims = parser.verify(token, key).requireIssuer(issuer).requireAudience(audience).parse();
```

### Regression tests

```java
// Forged, expired, wrong-issuer tokens are rejected.
```

## SEC-E-066: authentication mistaken for authorization

- Difficulty: Easy
- Framework: Spring Security
- Language: Java
- Perspective: Authorization
- Concept: authentication mistaken for authorization
- Symptom: Every signed-in user can perform an admin action.
- Diagnostic goal: Require a permission or role for the operation.

### Buggy code

```java
.anyRequest().authenticated()
```

### Expected diagnosis

Authenticated only proves identity; it does not grant the admin capability.

### Corrected code

```java
.requestMatchers("/admin/**").hasAuthority("admin:write")
```

### Regression tests

```java
// A user without admin:write receives 403.
```

## SEC-E-067: session fixation risk

- Difficulty: Easy
- Framework: Spring Security
- Language: Java
- Perspective: Session policy
- Concept: session fixation risk
- Symptom: The session identifier remains attacker-controlled after login.
- Diagnostic goal: Apply a session fixation protection policy.

### Buggy code

```java
http.sessionManagement(s -> s.sessionFixation(f -> f.none()));
```

### Expected diagnosis

Keeping the pre-login session identifier permits fixation attacks.

### Corrected code

```java
http.sessionManagement(s -> s.sessionFixation(f -> f.changeSessionId()));
```

### Regression tests

```java
// Successful login changes or invalidates the pre-authentication id.
```

## SEC-E-068: security CORS differs from MVC CORS

- Difficulty: Easy
- Framework: Spring Security
- Language: Java
- Perspective: CORS
- Concept: security CORS differs from MVC CORS
- Symptom: Preflight requests are rejected before the controller.
- Diagnostic goal: Configure CORS in the security filter chain with the application policy.

### Buggy code

```java
http.cors(c -> c.disable());
```

### Expected diagnosis

The security chain can reject preflight before MVC configuration is reached.

### Corrected code

```java
http.cors(Customizer.withDefaults());
```

### Regression tests

```java
// OPTIONS preflight receives the configured allow origin and methods.
```

## SEC-E-069: logout endpoint accepts GET

- Difficulty: Easy
- Framework: Spring Security
- Language: Java
- Perspective: Logout
- Concept: logout endpoint accepts GET
- Symptom: A cross-site link can log users out unexpectedly.
- Diagnostic goal: Use POST and CSRF protection for browser logout.

### Buggy code

```java
http.logout(l -> l.logoutRequestMatcher(new AntPathRequestMatcher("/logout", "GET")));
```

### Expected diagnosis

GET should be safe and cannot carry a CSRF-protected state change reliably.

### Corrected code

```java
http.logout(l -> l.logoutUrl("/logout"));
```

### Regression tests

```java
// GET does not log out; CSRF-protected POST does.
```

## SEC-E-070: test user missing authority

- Difficulty: Easy
- Framework: Spring Security
- Language: Java
- Perspective: Testing security
- Concept: test user missing authority
- Symptom: A controller test fails before the business assertion.
- Diagnostic goal: Make the test authentication match the endpoint contract.

### Buggy code

```java
@WebMvcTest
void deletes() { mockMvc.perform(delete("/items/1")); }
```

### Expected diagnosis

The request is anonymous and security correctly denies it.

### Corrected code

```java
@WithMockUser(roles = "ADMIN")
void deletes() { mockMvc.perform(delete("/items/1").with(csrf())); }
```

### Regression tests

```java
// The test supplies both role and CSRF token.
```

## SEC-E-071: permitAll on protected path

- Difficulty: Easy
- Framework: Spring Security
- Language: Java
- Perspective: Filter chain
- Concept: permitAll on protected path
- Symptom: Unauthenticated users access an admin endpoint.
- Diagnostic goal: Order matchers from specific protected paths to general rules.

### Buggy code

```java
authorize.requestMatchers("/**").permitAll()
       .requestMatchers("/admin/**").hasRole("ADMIN")
```

### Expected diagnosis

The catch-all matcher matches first, so the admin rule is unreachable.

### Corrected code

```java
authorize.requestMatchers("/admin/**").hasRole("ADMIN")
       .anyRequest().authenticated()
```

### Regression tests

```java
// Anonymous admin access is 401/403; authenticated users follow role rules.
```

## SEC-E-072: CSRF disabled for browser session

- Difficulty: Easy
- Framework: Spring Security
- Language: Java
- Perspective: CSRF
- Concept: CSRF disabled for browser session
- Symptom: State-changing browser requests lack forgery protection.
- Diagnostic goal: Keep CSRF for cookie-authenticated browser flows.

### Buggy code

```java
http.csrf(csrf -> csrf.disable());
```

### Expected diagnosis

Disabling CSRF globally is unsafe when authentication is carried by cookies.

### Corrected code

```java
http.csrf(Customizer.withDefaults());
```

### Regression tests

```java
// A missing token is rejected for a session-authenticated POST.
```

## SEC-E-073: plain text password

- Difficulty: Easy
- Framework: Spring Security
- Language: Java
- Perspective: Password storage
- Concept: plain text password
- Symptom: A database leak exposes credentials immediately.
- Diagnostic goal: Store adaptive password hashes and compare through the encoder.

### Buggy code

```java
user.setPassword(rawPassword);
```

### Expected diagnosis

Raw passwords are reversible by anyone who obtains the database.

### Corrected code

```java
user.setPassword(passwordEncoder.encode(rawPassword));
```

### Regression tests

```java
// Login matches through passwordEncoder.matches and never compares raw storage.
```

## SEC-E-074: annotation ignored

- Difficulty: Easy
- Framework: Spring Security
- Language: Java
- Perspective: Method security
- Concept: annotation ignored
- Symptom: A role annotation has no effect.
- Diagnostic goal: Enable method security and use the correct authority prefix.

### Buggy code

```java
@PreAuthorize("hasRole("ADMIN")")
public void delete() {}
```

### Expected diagnosis

Method annotations are inactive unless method security is enabled.

### Corrected code

```java
@EnableMethodSecurity
@Configuration
class SecurityConfig {}
```

### Regression tests

```java
// Nonadmins are denied when invoking the method directly through the proxy.
```

## SEC-E-075: signature not checked

- Difficulty: Easy
- Framework: Spring Security
- Language: Java
- Perspective: JWT validation
- Concept: signature not checked
- Symptom: Forged claims authorize a request.
- Diagnostic goal: Verify signature, issuer, audience, and expiry.

### Buggy code

```java
JwtClaims claims = parser.parseUnsecured(token);
```

### Expected diagnosis

Reading claims without verification is equivalent to trusting user input.

### Corrected code

```java
JwtClaims claims = parser.verify(token, key).requireIssuer(issuer).requireAudience(audience).parse();
```

### Regression tests

```java
// Forged, expired, wrong-issuer tokens are rejected.
```

## SEC-E-076: authentication mistaken for authorization

- Difficulty: Easy
- Framework: Spring Security
- Language: Java
- Perspective: Authorization
- Concept: authentication mistaken for authorization
- Symptom: Every signed-in user can perform an admin action.
- Diagnostic goal: Require a permission or role for the operation.

### Buggy code

```java
.anyRequest().authenticated()
```

### Expected diagnosis

Authenticated only proves identity; it does not grant the admin capability.

### Corrected code

```java
.requestMatchers("/admin/**").hasAuthority("admin:write")
```

### Regression tests

```java
// A user without admin:write receives 403.
```

## SEC-E-077: session fixation risk

- Difficulty: Easy
- Framework: Spring Security
- Language: Java
- Perspective: Session policy
- Concept: session fixation risk
- Symptom: The session identifier remains attacker-controlled after login.
- Diagnostic goal: Apply a session fixation protection policy.

### Buggy code

```java
http.sessionManagement(s -> s.sessionFixation(f -> f.none()));
```

### Expected diagnosis

Keeping the pre-login session identifier permits fixation attacks.

### Corrected code

```java
http.sessionManagement(s -> s.sessionFixation(f -> f.changeSessionId()));
```

### Regression tests

```java
// Successful login changes or invalidates the pre-authentication id.
```

## SEC-E-078: security CORS differs from MVC CORS

- Difficulty: Easy
- Framework: Spring Security
- Language: Java
- Perspective: CORS
- Concept: security CORS differs from MVC CORS
- Symptom: Preflight requests are rejected before the controller.
- Diagnostic goal: Configure CORS in the security filter chain with the application policy.

### Buggy code

```java
http.cors(c -> c.disable());
```

### Expected diagnosis

The security chain can reject preflight before MVC configuration is reached.

### Corrected code

```java
http.cors(Customizer.withDefaults());
```

### Regression tests

```java
// OPTIONS preflight receives the configured allow origin and methods.
```

## SEC-E-079: logout endpoint accepts GET

- Difficulty: Easy
- Framework: Spring Security
- Language: Java
- Perspective: Logout
- Concept: logout endpoint accepts GET
- Symptom: A cross-site link can log users out unexpectedly.
- Diagnostic goal: Use POST and CSRF protection for browser logout.

### Buggy code

```java
http.logout(l -> l.logoutRequestMatcher(new AntPathRequestMatcher("/logout", "GET")));
```

### Expected diagnosis

GET should be safe and cannot carry a CSRF-protected state change reliably.

### Corrected code

```java
http.logout(l -> l.logoutUrl("/logout"));
```

### Regression tests

```java
// GET does not log out; CSRF-protected POST does.
```

## SEC-E-080: test user missing authority

- Difficulty: Easy
- Framework: Spring Security
- Language: Java
- Perspective: Testing security
- Concept: test user missing authority
- Symptom: A controller test fails before the business assertion.
- Diagnostic goal: Make the test authentication match the endpoint contract.

### Buggy code

```java
@WebMvcTest
void deletes() { mockMvc.perform(delete("/items/1")); }
```

### Expected diagnosis

The request is anonymous and security correctly denies it.

### Corrected code

```java
@WithMockUser(roles = "ADMIN")
void deletes() { mockMvc.perform(delete("/items/1").with(csrf())); }
```

### Regression tests

```java
// The test supplies both role and CSRF token.
```

## SEC-E-081: permitAll on protected path

- Difficulty: Easy
- Framework: Spring Security
- Language: Java
- Perspective: Filter chain
- Concept: permitAll on protected path
- Symptom: Unauthenticated users access an admin endpoint.
- Diagnostic goal: Order matchers from specific protected paths to general rules.

### Buggy code

```java
authorize.requestMatchers("/**").permitAll()
       .requestMatchers("/admin/**").hasRole("ADMIN")
```

### Expected diagnosis

The catch-all matcher matches first, so the admin rule is unreachable.

### Corrected code

```java
authorize.requestMatchers("/admin/**").hasRole("ADMIN")
       .anyRequest().authenticated()
```

### Regression tests

```java
// Anonymous admin access is 401/403; authenticated users follow role rules.
```

## SEC-E-082: CSRF disabled for browser session

- Difficulty: Easy
- Framework: Spring Security
- Language: Java
- Perspective: CSRF
- Concept: CSRF disabled for browser session
- Symptom: State-changing browser requests lack forgery protection.
- Diagnostic goal: Keep CSRF for cookie-authenticated browser flows.

### Buggy code

```java
http.csrf(csrf -> csrf.disable());
```

### Expected diagnosis

Disabling CSRF globally is unsafe when authentication is carried by cookies.

### Corrected code

```java
http.csrf(Customizer.withDefaults());
```

### Regression tests

```java
// A missing token is rejected for a session-authenticated POST.
```

## SEC-E-083: plain text password

- Difficulty: Easy
- Framework: Spring Security
- Language: Java
- Perspective: Password storage
- Concept: plain text password
- Symptom: A database leak exposes credentials immediately.
- Diagnostic goal: Store adaptive password hashes and compare through the encoder.

### Buggy code

```java
user.setPassword(rawPassword);
```

### Expected diagnosis

Raw passwords are reversible by anyone who obtains the database.

### Corrected code

```java
user.setPassword(passwordEncoder.encode(rawPassword));
```

### Regression tests

```java
// Login matches through passwordEncoder.matches and never compares raw storage.
```

## SEC-E-084: annotation ignored

- Difficulty: Easy
- Framework: Spring Security
- Language: Java
- Perspective: Method security
- Concept: annotation ignored
- Symptom: A role annotation has no effect.
- Diagnostic goal: Enable method security and use the correct authority prefix.

### Buggy code

```java
@PreAuthorize("hasRole("ADMIN")")
public void delete() {}
```

### Expected diagnosis

Method annotations are inactive unless method security is enabled.

### Corrected code

```java
@EnableMethodSecurity
@Configuration
class SecurityConfig {}
```

### Regression tests

```java
// Nonadmins are denied when invoking the method directly through the proxy.
```

## SEC-E-085: signature not checked

- Difficulty: Easy
- Framework: Spring Security
- Language: Java
- Perspective: JWT validation
- Concept: signature not checked
- Symptom: Forged claims authorize a request.
- Diagnostic goal: Verify signature, issuer, audience, and expiry.

### Buggy code

```java
JwtClaims claims = parser.parseUnsecured(token);
```

### Expected diagnosis

Reading claims without verification is equivalent to trusting user input.

### Corrected code

```java
JwtClaims claims = parser.verify(token, key).requireIssuer(issuer).requireAudience(audience).parse();
```

### Regression tests

```java
// Forged, expired, wrong-issuer tokens are rejected.
```

## SEC-E-086: authentication mistaken for authorization

- Difficulty: Easy
- Framework: Spring Security
- Language: Java
- Perspective: Authorization
- Concept: authentication mistaken for authorization
- Symptom: Every signed-in user can perform an admin action.
- Diagnostic goal: Require a permission or role for the operation.

### Buggy code

```java
.anyRequest().authenticated()
```

### Expected diagnosis

Authenticated only proves identity; it does not grant the admin capability.

### Corrected code

```java
.requestMatchers("/admin/**").hasAuthority("admin:write")
```

### Regression tests

```java
// A user without admin:write receives 403.
```

## SEC-E-087: session fixation risk

- Difficulty: Easy
- Framework: Spring Security
- Language: Java
- Perspective: Session policy
- Concept: session fixation risk
- Symptom: The session identifier remains attacker-controlled after login.
- Diagnostic goal: Apply a session fixation protection policy.

### Buggy code

```java
http.sessionManagement(s -> s.sessionFixation(f -> f.none()));
```

### Expected diagnosis

Keeping the pre-login session identifier permits fixation attacks.

### Corrected code

```java
http.sessionManagement(s -> s.sessionFixation(f -> f.changeSessionId()));
```

### Regression tests

```java
// Successful login changes or invalidates the pre-authentication id.
```

## SEC-E-088: security CORS differs from MVC CORS

- Difficulty: Easy
- Framework: Spring Security
- Language: Java
- Perspective: CORS
- Concept: security CORS differs from MVC CORS
- Symptom: Preflight requests are rejected before the controller.
- Diagnostic goal: Configure CORS in the security filter chain with the application policy.

### Buggy code

```java
http.cors(c -> c.disable());
```

### Expected diagnosis

The security chain can reject preflight before MVC configuration is reached.

### Corrected code

```java
http.cors(Customizer.withDefaults());
```

### Regression tests

```java
// OPTIONS preflight receives the configured allow origin and methods.
```

## SEC-E-089: logout endpoint accepts GET

- Difficulty: Easy
- Framework: Spring Security
- Language: Java
- Perspective: Logout
- Concept: logout endpoint accepts GET
- Symptom: A cross-site link can log users out unexpectedly.
- Diagnostic goal: Use POST and CSRF protection for browser logout.

### Buggy code

```java
http.logout(l -> l.logoutRequestMatcher(new AntPathRequestMatcher("/logout", "GET")));
```

### Expected diagnosis

GET should be safe and cannot carry a CSRF-protected state change reliably.

### Corrected code

```java
http.logout(l -> l.logoutUrl("/logout"));
```

### Regression tests

```java
// GET does not log out; CSRF-protected POST does.
```

## SEC-E-090: test user missing authority

- Difficulty: Easy
- Framework: Spring Security
- Language: Java
- Perspective: Testing security
- Concept: test user missing authority
- Symptom: A controller test fails before the business assertion.
- Diagnostic goal: Make the test authentication match the endpoint contract.

### Buggy code

```java
@WebMvcTest
void deletes() { mockMvc.perform(delete("/items/1")); }
```

### Expected diagnosis

The request is anonymous and security correctly denies it.

### Corrected code

```java
@WithMockUser(roles = "ADMIN")
void deletes() { mockMvc.perform(delete("/items/1").with(csrf())); }
```

### Regression tests

```java
// The test supplies both role and CSRF token.
```

## SEC-E-091: permitAll on protected path

- Difficulty: Easy
- Framework: Spring Security
- Language: Java
- Perspective: Filter chain
- Concept: permitAll on protected path
- Symptom: Unauthenticated users access an admin endpoint.
- Diagnostic goal: Order matchers from specific protected paths to general rules.

### Buggy code

```java
authorize.requestMatchers("/**").permitAll()
       .requestMatchers("/admin/**").hasRole("ADMIN")
```

### Expected diagnosis

The catch-all matcher matches first, so the admin rule is unreachable.

### Corrected code

```java
authorize.requestMatchers("/admin/**").hasRole("ADMIN")
       .anyRequest().authenticated()
```

### Regression tests

```java
// Anonymous admin access is 401/403; authenticated users follow role rules.
```

## SEC-E-092: CSRF disabled for browser session

- Difficulty: Easy
- Framework: Spring Security
- Language: Java
- Perspective: CSRF
- Concept: CSRF disabled for browser session
- Symptom: State-changing browser requests lack forgery protection.
- Diagnostic goal: Keep CSRF for cookie-authenticated browser flows.

### Buggy code

```java
http.csrf(csrf -> csrf.disable());
```

### Expected diagnosis

Disabling CSRF globally is unsafe when authentication is carried by cookies.

### Corrected code

```java
http.csrf(Customizer.withDefaults());
```

### Regression tests

```java
// A missing token is rejected for a session-authenticated POST.
```

## SEC-E-093: plain text password

- Difficulty: Easy
- Framework: Spring Security
- Language: Java
- Perspective: Password storage
- Concept: plain text password
- Symptom: A database leak exposes credentials immediately.
- Diagnostic goal: Store adaptive password hashes and compare through the encoder.

### Buggy code

```java
user.setPassword(rawPassword);
```

### Expected diagnosis

Raw passwords are reversible by anyone who obtains the database.

### Corrected code

```java
user.setPassword(passwordEncoder.encode(rawPassword));
```

### Regression tests

```java
// Login matches through passwordEncoder.matches and never compares raw storage.
```

## SEC-E-094: annotation ignored

- Difficulty: Easy
- Framework: Spring Security
- Language: Java
- Perspective: Method security
- Concept: annotation ignored
- Symptom: A role annotation has no effect.
- Diagnostic goal: Enable method security and use the correct authority prefix.

### Buggy code

```java
@PreAuthorize("hasRole("ADMIN")")
public void delete() {}
```

### Expected diagnosis

Method annotations are inactive unless method security is enabled.

### Corrected code

```java
@EnableMethodSecurity
@Configuration
class SecurityConfig {}
```

### Regression tests

```java
// Nonadmins are denied when invoking the method directly through the proxy.
```

## SEC-E-095: signature not checked

- Difficulty: Easy
- Framework: Spring Security
- Language: Java
- Perspective: JWT validation
- Concept: signature not checked
- Symptom: Forged claims authorize a request.
- Diagnostic goal: Verify signature, issuer, audience, and expiry.

### Buggy code

```java
JwtClaims claims = parser.parseUnsecured(token);
```

### Expected diagnosis

Reading claims without verification is equivalent to trusting user input.

### Corrected code

```java
JwtClaims claims = parser.verify(token, key).requireIssuer(issuer).requireAudience(audience).parse();
```

### Regression tests

```java
// Forged, expired, wrong-issuer tokens are rejected.
```

## SEC-E-096: authentication mistaken for authorization

- Difficulty: Easy
- Framework: Spring Security
- Language: Java
- Perspective: Authorization
- Concept: authentication mistaken for authorization
- Symptom: Every signed-in user can perform an admin action.
- Diagnostic goal: Require a permission or role for the operation.

### Buggy code

```java
.anyRequest().authenticated()
```

### Expected diagnosis

Authenticated only proves identity; it does not grant the admin capability.

### Corrected code

```java
.requestMatchers("/admin/**").hasAuthority("admin:write")
```

### Regression tests

```java
// A user without admin:write receives 403.
```

## SEC-E-097: session fixation risk

- Difficulty: Easy
- Framework: Spring Security
- Language: Java
- Perspective: Session policy
- Concept: session fixation risk
- Symptom: The session identifier remains attacker-controlled after login.
- Diagnostic goal: Apply a session fixation protection policy.

### Buggy code

```java
http.sessionManagement(s -> s.sessionFixation(f -> f.none()));
```

### Expected diagnosis

Keeping the pre-login session identifier permits fixation attacks.

### Corrected code

```java
http.sessionManagement(s -> s.sessionFixation(f -> f.changeSessionId()));
```

### Regression tests

```java
// Successful login changes or invalidates the pre-authentication id.
```

## SEC-E-098: security CORS differs from MVC CORS

- Difficulty: Easy
- Framework: Spring Security
- Language: Java
- Perspective: CORS
- Concept: security CORS differs from MVC CORS
- Symptom: Preflight requests are rejected before the controller.
- Diagnostic goal: Configure CORS in the security filter chain with the application policy.

### Buggy code

```java
http.cors(c -> c.disable());
```

### Expected diagnosis

The security chain can reject preflight before MVC configuration is reached.

### Corrected code

```java
http.cors(Customizer.withDefaults());
```

### Regression tests

```java
// OPTIONS preflight receives the configured allow origin and methods.
```

## SEC-E-099: logout endpoint accepts GET

- Difficulty: Easy
- Framework: Spring Security
- Language: Java
- Perspective: Logout
- Concept: logout endpoint accepts GET
- Symptom: A cross-site link can log users out unexpectedly.
- Diagnostic goal: Use POST and CSRF protection for browser logout.

### Buggy code

```java
http.logout(l -> l.logoutRequestMatcher(new AntPathRequestMatcher("/logout", "GET")));
```

### Expected diagnosis

GET should be safe and cannot carry a CSRF-protected state change reliably.

### Corrected code

```java
http.logout(l -> l.logoutUrl("/logout"));
```

### Regression tests

```java
// GET does not log out; CSRF-protected POST does.
```

## SEC-E-100: test user missing authority

- Difficulty: Easy
- Framework: Spring Security
- Language: Java
- Perspective: Testing security
- Concept: test user missing authority
- Symptom: A controller test fails before the business assertion.
- Diagnostic goal: Make the test authentication match the endpoint contract.

### Buggy code

```java
@WebMvcTest
void deletes() { mockMvc.perform(delete("/items/1")); }
```

### Expected diagnosis

The request is anonymous and security correctly denies it.

### Corrected code

```java
@WithMockUser(roles = "ADMIN")
void deletes() { mockMvc.perform(delete("/items/1").with(csrf())); }
```

### Regression tests

```java
// The test supplies both role and CSRF token.
```

## SEC-M-001: permitAll on protected path

- Difficulty: Medium
- Framework: Spring Security
- Language: Java
- Perspective: Filter chain
- Concept: permitAll on protected path
- Symptom: Unauthenticated users access an admin endpoint.
- Diagnostic goal: Order matchers from specific protected paths to general rules.

### Buggy code

```java
authorize.requestMatchers("/**").permitAll()
       .requestMatchers("/admin/**").hasRole("ADMIN")
```

### Expected diagnosis

The catch-all matcher matches first, so the admin rule is unreachable.

### Corrected code

```java
authorize.requestMatchers("/admin/**").hasRole("ADMIN")
       .anyRequest().authenticated()
```

### Regression tests

```java
// Anonymous admin access is 401/403; authenticated users follow role rules.
```

## SEC-M-002: CSRF disabled for browser session

- Difficulty: Medium
- Framework: Spring Security
- Language: Java
- Perspective: CSRF
- Concept: CSRF disabled for browser session
- Symptom: State-changing browser requests lack forgery protection.
- Diagnostic goal: Keep CSRF for cookie-authenticated browser flows.

### Buggy code

```java
http.csrf(csrf -> csrf.disable());
```

### Expected diagnosis

Disabling CSRF globally is unsafe when authentication is carried by cookies.

### Corrected code

```java
http.csrf(Customizer.withDefaults());
```

### Regression tests

```java
// A missing token is rejected for a session-authenticated POST.
```

## SEC-M-003: plain text password

- Difficulty: Medium
- Framework: Spring Security
- Language: Java
- Perspective: Password storage
- Concept: plain text password
- Symptom: A database leak exposes credentials immediately.
- Diagnostic goal: Store adaptive password hashes and compare through the encoder.

### Buggy code

```java
user.setPassword(rawPassword);
```

### Expected diagnosis

Raw passwords are reversible by anyone who obtains the database.

### Corrected code

```java
user.setPassword(passwordEncoder.encode(rawPassword));
```

### Regression tests

```java
// Login matches through passwordEncoder.matches and never compares raw storage.
```

## SEC-M-004: annotation ignored

- Difficulty: Medium
- Framework: Spring Security
- Language: Java
- Perspective: Method security
- Concept: annotation ignored
- Symptom: A role annotation has no effect.
- Diagnostic goal: Enable method security and use the correct authority prefix.

### Buggy code

```java
@PreAuthorize("hasRole("ADMIN")")
public void delete() {}
```

### Expected diagnosis

Method annotations are inactive unless method security is enabled.

### Corrected code

```java
@EnableMethodSecurity
@Configuration
class SecurityConfig {}
```

### Regression tests

```java
// Nonadmins are denied when invoking the method directly through the proxy.
```

## SEC-M-005: signature not checked

- Difficulty: Medium
- Framework: Spring Security
- Language: Java
- Perspective: JWT validation
- Concept: signature not checked
- Symptom: Forged claims authorize a request.
- Diagnostic goal: Verify signature, issuer, audience, and expiry.

### Buggy code

```java
JwtClaims claims = parser.parseUnsecured(token);
```

### Expected diagnosis

Reading claims without verification is equivalent to trusting user input.

### Corrected code

```java
JwtClaims claims = parser.verify(token, key).requireIssuer(issuer).requireAudience(audience).parse();
```

### Regression tests

```java
// Forged, expired, wrong-issuer tokens are rejected.
```

## SEC-M-006: authentication mistaken for authorization

- Difficulty: Medium
- Framework: Spring Security
- Language: Java
- Perspective: Authorization
- Concept: authentication mistaken for authorization
- Symptom: Every signed-in user can perform an admin action.
- Diagnostic goal: Require a permission or role for the operation.

### Buggy code

```java
.anyRequest().authenticated()
```

### Expected diagnosis

Authenticated only proves identity; it does not grant the admin capability.

### Corrected code

```java
.requestMatchers("/admin/**").hasAuthority("admin:write")
```

### Regression tests

```java
// A user without admin:write receives 403.
```

## SEC-M-007: session fixation risk

- Difficulty: Medium
- Framework: Spring Security
- Language: Java
- Perspective: Session policy
- Concept: session fixation risk
- Symptom: The session identifier remains attacker-controlled after login.
- Diagnostic goal: Apply a session fixation protection policy.

### Buggy code

```java
http.sessionManagement(s -> s.sessionFixation(f -> f.none()));
```

### Expected diagnosis

Keeping the pre-login session identifier permits fixation attacks.

### Corrected code

```java
http.sessionManagement(s -> s.sessionFixation(f -> f.changeSessionId()));
```

### Regression tests

```java
// Successful login changes or invalidates the pre-authentication id.
```

## SEC-M-008: security CORS differs from MVC CORS

- Difficulty: Medium
- Framework: Spring Security
- Language: Java
- Perspective: CORS
- Concept: security CORS differs from MVC CORS
- Symptom: Preflight requests are rejected before the controller.
- Diagnostic goal: Configure CORS in the security filter chain with the application policy.

### Buggy code

```java
http.cors(c -> c.disable());
```

### Expected diagnosis

The security chain can reject preflight before MVC configuration is reached.

### Corrected code

```java
http.cors(Customizer.withDefaults());
```

### Regression tests

```java
// OPTIONS preflight receives the configured allow origin and methods.
```

## SEC-M-009: logout endpoint accepts GET

- Difficulty: Medium
- Framework: Spring Security
- Language: Java
- Perspective: Logout
- Concept: logout endpoint accepts GET
- Symptom: A cross-site link can log users out unexpectedly.
- Diagnostic goal: Use POST and CSRF protection for browser logout.

### Buggy code

```java
http.logout(l -> l.logoutRequestMatcher(new AntPathRequestMatcher("/logout", "GET")));
```

### Expected diagnosis

GET should be safe and cannot carry a CSRF-protected state change reliably.

### Corrected code

```java
http.logout(l -> l.logoutUrl("/logout"));
```

### Regression tests

```java
// GET does not log out; CSRF-protected POST does.
```

## SEC-M-010: test user missing authority

- Difficulty: Medium
- Framework: Spring Security
- Language: Java
- Perspective: Testing security
- Concept: test user missing authority
- Symptom: A controller test fails before the business assertion.
- Diagnostic goal: Make the test authentication match the endpoint contract.

### Buggy code

```java
@WebMvcTest
void deletes() { mockMvc.perform(delete("/items/1")); }
```

### Expected diagnosis

The request is anonymous and security correctly denies it.

### Corrected code

```java
@WithMockUser(roles = "ADMIN")
void deletes() { mockMvc.perform(delete("/items/1").with(csrf())); }
```

### Regression tests

```java
// The test supplies both role and CSRF token.
```

## SEC-M-011: permitAll on protected path

- Difficulty: Medium
- Framework: Spring Security
- Language: Java
- Perspective: Filter chain
- Concept: permitAll on protected path
- Symptom: Unauthenticated users access an admin endpoint.
- Diagnostic goal: Order matchers from specific protected paths to general rules.

### Buggy code

```java
authorize.requestMatchers("/**").permitAll()
       .requestMatchers("/admin/**").hasRole("ADMIN")
```

### Expected diagnosis

The catch-all matcher matches first, so the admin rule is unreachable.

### Corrected code

```java
authorize.requestMatchers("/admin/**").hasRole("ADMIN")
       .anyRequest().authenticated()
```

### Regression tests

```java
// Anonymous admin access is 401/403; authenticated users follow role rules.
```

## SEC-M-012: CSRF disabled for browser session

- Difficulty: Medium
- Framework: Spring Security
- Language: Java
- Perspective: CSRF
- Concept: CSRF disabled for browser session
- Symptom: State-changing browser requests lack forgery protection.
- Diagnostic goal: Keep CSRF for cookie-authenticated browser flows.

### Buggy code

```java
http.csrf(csrf -> csrf.disable());
```

### Expected diagnosis

Disabling CSRF globally is unsafe when authentication is carried by cookies.

### Corrected code

```java
http.csrf(Customizer.withDefaults());
```

### Regression tests

```java
// A missing token is rejected for a session-authenticated POST.
```

## SEC-M-013: plain text password

- Difficulty: Medium
- Framework: Spring Security
- Language: Java
- Perspective: Password storage
- Concept: plain text password
- Symptom: A database leak exposes credentials immediately.
- Diagnostic goal: Store adaptive password hashes and compare through the encoder.

### Buggy code

```java
user.setPassword(rawPassword);
```

### Expected diagnosis

Raw passwords are reversible by anyone who obtains the database.

### Corrected code

```java
user.setPassword(passwordEncoder.encode(rawPassword));
```

### Regression tests

```java
// Login matches through passwordEncoder.matches and never compares raw storage.
```

## SEC-M-014: annotation ignored

- Difficulty: Medium
- Framework: Spring Security
- Language: Java
- Perspective: Method security
- Concept: annotation ignored
- Symptom: A role annotation has no effect.
- Diagnostic goal: Enable method security and use the correct authority prefix.

### Buggy code

```java
@PreAuthorize("hasRole("ADMIN")")
public void delete() {}
```

### Expected diagnosis

Method annotations are inactive unless method security is enabled.

### Corrected code

```java
@EnableMethodSecurity
@Configuration
class SecurityConfig {}
```

### Regression tests

```java
// Nonadmins are denied when invoking the method directly through the proxy.
```

## SEC-M-015: signature not checked

- Difficulty: Medium
- Framework: Spring Security
- Language: Java
- Perspective: JWT validation
- Concept: signature not checked
- Symptom: Forged claims authorize a request.
- Diagnostic goal: Verify signature, issuer, audience, and expiry.

### Buggy code

```java
JwtClaims claims = parser.parseUnsecured(token);
```

### Expected diagnosis

Reading claims without verification is equivalent to trusting user input.

### Corrected code

```java
JwtClaims claims = parser.verify(token, key).requireIssuer(issuer).requireAudience(audience).parse();
```

### Regression tests

```java
// Forged, expired, wrong-issuer tokens are rejected.
```

## SEC-M-016: authentication mistaken for authorization

- Difficulty: Medium
- Framework: Spring Security
- Language: Java
- Perspective: Authorization
- Concept: authentication mistaken for authorization
- Symptom: Every signed-in user can perform an admin action.
- Diagnostic goal: Require a permission or role for the operation.

### Buggy code

```java
.anyRequest().authenticated()
```

### Expected diagnosis

Authenticated only proves identity; it does not grant the admin capability.

### Corrected code

```java
.requestMatchers("/admin/**").hasAuthority("admin:write")
```

### Regression tests

```java
// A user without admin:write receives 403.
```

## SEC-M-017: session fixation risk

- Difficulty: Medium
- Framework: Spring Security
- Language: Java
- Perspective: Session policy
- Concept: session fixation risk
- Symptom: The session identifier remains attacker-controlled after login.
- Diagnostic goal: Apply a session fixation protection policy.

### Buggy code

```java
http.sessionManagement(s -> s.sessionFixation(f -> f.none()));
```

### Expected diagnosis

Keeping the pre-login session identifier permits fixation attacks.

### Corrected code

```java
http.sessionManagement(s -> s.sessionFixation(f -> f.changeSessionId()));
```

### Regression tests

```java
// Successful login changes or invalidates the pre-authentication id.
```

## SEC-M-018: security CORS differs from MVC CORS

- Difficulty: Medium
- Framework: Spring Security
- Language: Java
- Perspective: CORS
- Concept: security CORS differs from MVC CORS
- Symptom: Preflight requests are rejected before the controller.
- Diagnostic goal: Configure CORS in the security filter chain with the application policy.

### Buggy code

```java
http.cors(c -> c.disable());
```

### Expected diagnosis

The security chain can reject preflight before MVC configuration is reached.

### Corrected code

```java
http.cors(Customizer.withDefaults());
```

### Regression tests

```java
// OPTIONS preflight receives the configured allow origin and methods.
```

## SEC-M-019: logout endpoint accepts GET

- Difficulty: Medium
- Framework: Spring Security
- Language: Java
- Perspective: Logout
- Concept: logout endpoint accepts GET
- Symptom: A cross-site link can log users out unexpectedly.
- Diagnostic goal: Use POST and CSRF protection for browser logout.

### Buggy code

```java
http.logout(l -> l.logoutRequestMatcher(new AntPathRequestMatcher("/logout", "GET")));
```

### Expected diagnosis

GET should be safe and cannot carry a CSRF-protected state change reliably.

### Corrected code

```java
http.logout(l -> l.logoutUrl("/logout"));
```

### Regression tests

```java
// GET does not log out; CSRF-protected POST does.
```

## SEC-M-020: test user missing authority

- Difficulty: Medium
- Framework: Spring Security
- Language: Java
- Perspective: Testing security
- Concept: test user missing authority
- Symptom: A controller test fails before the business assertion.
- Diagnostic goal: Make the test authentication match the endpoint contract.

### Buggy code

```java
@WebMvcTest
void deletes() { mockMvc.perform(delete("/items/1")); }
```

### Expected diagnosis

The request is anonymous and security correctly denies it.

### Corrected code

```java
@WithMockUser(roles = "ADMIN")
void deletes() { mockMvc.perform(delete("/items/1").with(csrf())); }
```

### Regression tests

```java
// The test supplies both role and CSRF token.
```

## SEC-M-021: permitAll on protected path

- Difficulty: Medium
- Framework: Spring Security
- Language: Java
- Perspective: Filter chain
- Concept: permitAll on protected path
- Symptom: Unauthenticated users access an admin endpoint.
- Diagnostic goal: Order matchers from specific protected paths to general rules.

### Buggy code

```java
authorize.requestMatchers("/**").permitAll()
       .requestMatchers("/admin/**").hasRole("ADMIN")
```

### Expected diagnosis

The catch-all matcher matches first, so the admin rule is unreachable.

### Corrected code

```java
authorize.requestMatchers("/admin/**").hasRole("ADMIN")
       .anyRequest().authenticated()
```

### Regression tests

```java
// Anonymous admin access is 401/403; authenticated users follow role rules.
```

## SEC-M-022: CSRF disabled for browser session

- Difficulty: Medium
- Framework: Spring Security
- Language: Java
- Perspective: CSRF
- Concept: CSRF disabled for browser session
- Symptom: State-changing browser requests lack forgery protection.
- Diagnostic goal: Keep CSRF for cookie-authenticated browser flows.

### Buggy code

```java
http.csrf(csrf -> csrf.disable());
```

### Expected diagnosis

Disabling CSRF globally is unsafe when authentication is carried by cookies.

### Corrected code

```java
http.csrf(Customizer.withDefaults());
```

### Regression tests

```java
// A missing token is rejected for a session-authenticated POST.
```

## SEC-M-023: plain text password

- Difficulty: Medium
- Framework: Spring Security
- Language: Java
- Perspective: Password storage
- Concept: plain text password
- Symptom: A database leak exposes credentials immediately.
- Diagnostic goal: Store adaptive password hashes and compare through the encoder.

### Buggy code

```java
user.setPassword(rawPassword);
```

### Expected diagnosis

Raw passwords are reversible by anyone who obtains the database.

### Corrected code

```java
user.setPassword(passwordEncoder.encode(rawPassword));
```

### Regression tests

```java
// Login matches through passwordEncoder.matches and never compares raw storage.
```

## SEC-M-024: annotation ignored

- Difficulty: Medium
- Framework: Spring Security
- Language: Java
- Perspective: Method security
- Concept: annotation ignored
- Symptom: A role annotation has no effect.
- Diagnostic goal: Enable method security and use the correct authority prefix.

### Buggy code

```java
@PreAuthorize("hasRole("ADMIN")")
public void delete() {}
```

### Expected diagnosis

Method annotations are inactive unless method security is enabled.

### Corrected code

```java
@EnableMethodSecurity
@Configuration
class SecurityConfig {}
```

### Regression tests

```java
// Nonadmins are denied when invoking the method directly through the proxy.
```

## SEC-M-025: signature not checked

- Difficulty: Medium
- Framework: Spring Security
- Language: Java
- Perspective: JWT validation
- Concept: signature not checked
- Symptom: Forged claims authorize a request.
- Diagnostic goal: Verify signature, issuer, audience, and expiry.

### Buggy code

```java
JwtClaims claims = parser.parseUnsecured(token);
```

### Expected diagnosis

Reading claims without verification is equivalent to trusting user input.

### Corrected code

```java
JwtClaims claims = parser.verify(token, key).requireIssuer(issuer).requireAudience(audience).parse();
```

### Regression tests

```java
// Forged, expired, wrong-issuer tokens are rejected.
```

## SEC-M-026: authentication mistaken for authorization

- Difficulty: Medium
- Framework: Spring Security
- Language: Java
- Perspective: Authorization
- Concept: authentication mistaken for authorization
- Symptom: Every signed-in user can perform an admin action.
- Diagnostic goal: Require a permission or role for the operation.

### Buggy code

```java
.anyRequest().authenticated()
```

### Expected diagnosis

Authenticated only proves identity; it does not grant the admin capability.

### Corrected code

```java
.requestMatchers("/admin/**").hasAuthority("admin:write")
```

### Regression tests

```java
// A user without admin:write receives 403.
```

## SEC-M-027: session fixation risk

- Difficulty: Medium
- Framework: Spring Security
- Language: Java
- Perspective: Session policy
- Concept: session fixation risk
- Symptom: The session identifier remains attacker-controlled after login.
- Diagnostic goal: Apply a session fixation protection policy.

### Buggy code

```java
http.sessionManagement(s -> s.sessionFixation(f -> f.none()));
```

### Expected diagnosis

Keeping the pre-login session identifier permits fixation attacks.

### Corrected code

```java
http.sessionManagement(s -> s.sessionFixation(f -> f.changeSessionId()));
```

### Regression tests

```java
// Successful login changes or invalidates the pre-authentication id.
```

## SEC-M-028: security CORS differs from MVC CORS

- Difficulty: Medium
- Framework: Spring Security
- Language: Java
- Perspective: CORS
- Concept: security CORS differs from MVC CORS
- Symptom: Preflight requests are rejected before the controller.
- Diagnostic goal: Configure CORS in the security filter chain with the application policy.

### Buggy code

```java
http.cors(c -> c.disable());
```

### Expected diagnosis

The security chain can reject preflight before MVC configuration is reached.

### Corrected code

```java
http.cors(Customizer.withDefaults());
```

### Regression tests

```java
// OPTIONS preflight receives the configured allow origin and methods.
```

## SEC-M-029: logout endpoint accepts GET

- Difficulty: Medium
- Framework: Spring Security
- Language: Java
- Perspective: Logout
- Concept: logout endpoint accepts GET
- Symptom: A cross-site link can log users out unexpectedly.
- Diagnostic goal: Use POST and CSRF protection for browser logout.

### Buggy code

```java
http.logout(l -> l.logoutRequestMatcher(new AntPathRequestMatcher("/logout", "GET")));
```

### Expected diagnosis

GET should be safe and cannot carry a CSRF-protected state change reliably.

### Corrected code

```java
http.logout(l -> l.logoutUrl("/logout"));
```

### Regression tests

```java
// GET does not log out; CSRF-protected POST does.
```

## SEC-M-030: test user missing authority

- Difficulty: Medium
- Framework: Spring Security
- Language: Java
- Perspective: Testing security
- Concept: test user missing authority
- Symptom: A controller test fails before the business assertion.
- Diagnostic goal: Make the test authentication match the endpoint contract.

### Buggy code

```java
@WebMvcTest
void deletes() { mockMvc.perform(delete("/items/1")); }
```

### Expected diagnosis

The request is anonymous and security correctly denies it.

### Corrected code

```java
@WithMockUser(roles = "ADMIN")
void deletes() { mockMvc.perform(delete("/items/1").with(csrf())); }
```

### Regression tests

```java
// The test supplies both role and CSRF token.
```

## SEC-M-031: permitAll on protected path

- Difficulty: Medium
- Framework: Spring Security
- Language: Java
- Perspective: Filter chain
- Concept: permitAll on protected path
- Symptom: Unauthenticated users access an admin endpoint.
- Diagnostic goal: Order matchers from specific protected paths to general rules.

### Buggy code

```java
authorize.requestMatchers("/**").permitAll()
       .requestMatchers("/admin/**").hasRole("ADMIN")
```

### Expected diagnosis

The catch-all matcher matches first, so the admin rule is unreachable.

### Corrected code

```java
authorize.requestMatchers("/admin/**").hasRole("ADMIN")
       .anyRequest().authenticated()
```

### Regression tests

```java
// Anonymous admin access is 401/403; authenticated users follow role rules.
```

## SEC-M-032: CSRF disabled for browser session

- Difficulty: Medium
- Framework: Spring Security
- Language: Java
- Perspective: CSRF
- Concept: CSRF disabled for browser session
- Symptom: State-changing browser requests lack forgery protection.
- Diagnostic goal: Keep CSRF for cookie-authenticated browser flows.

### Buggy code

```java
http.csrf(csrf -> csrf.disable());
```

### Expected diagnosis

Disabling CSRF globally is unsafe when authentication is carried by cookies.

### Corrected code

```java
http.csrf(Customizer.withDefaults());
```

### Regression tests

```java
// A missing token is rejected for a session-authenticated POST.
```

## SEC-M-033: plain text password

- Difficulty: Medium
- Framework: Spring Security
- Language: Java
- Perspective: Password storage
- Concept: plain text password
- Symptom: A database leak exposes credentials immediately.
- Diagnostic goal: Store adaptive password hashes and compare through the encoder.

### Buggy code

```java
user.setPassword(rawPassword);
```

### Expected diagnosis

Raw passwords are reversible by anyone who obtains the database.

### Corrected code

```java
user.setPassword(passwordEncoder.encode(rawPassword));
```

### Regression tests

```java
// Login matches through passwordEncoder.matches and never compares raw storage.
```

## SEC-M-034: annotation ignored

- Difficulty: Medium
- Framework: Spring Security
- Language: Java
- Perspective: Method security
- Concept: annotation ignored
- Symptom: A role annotation has no effect.
- Diagnostic goal: Enable method security and use the correct authority prefix.

### Buggy code

```java
@PreAuthorize("hasRole("ADMIN")")
public void delete() {}
```

### Expected diagnosis

Method annotations are inactive unless method security is enabled.

### Corrected code

```java
@EnableMethodSecurity
@Configuration
class SecurityConfig {}
```

### Regression tests

```java
// Nonadmins are denied when invoking the method directly through the proxy.
```

## SEC-M-035: signature not checked

- Difficulty: Medium
- Framework: Spring Security
- Language: Java
- Perspective: JWT validation
- Concept: signature not checked
- Symptom: Forged claims authorize a request.
- Diagnostic goal: Verify signature, issuer, audience, and expiry.

### Buggy code

```java
JwtClaims claims = parser.parseUnsecured(token);
```

### Expected diagnosis

Reading claims without verification is equivalent to trusting user input.

### Corrected code

```java
JwtClaims claims = parser.verify(token, key).requireIssuer(issuer).requireAudience(audience).parse();
```

### Regression tests

```java
// Forged, expired, wrong-issuer tokens are rejected.
```

## SEC-M-036: authentication mistaken for authorization

- Difficulty: Medium
- Framework: Spring Security
- Language: Java
- Perspective: Authorization
- Concept: authentication mistaken for authorization
- Symptom: Every signed-in user can perform an admin action.
- Diagnostic goal: Require a permission or role for the operation.

### Buggy code

```java
.anyRequest().authenticated()
```

### Expected diagnosis

Authenticated only proves identity; it does not grant the admin capability.

### Corrected code

```java
.requestMatchers("/admin/**").hasAuthority("admin:write")
```

### Regression tests

```java
// A user without admin:write receives 403.
```

## SEC-M-037: session fixation risk

- Difficulty: Medium
- Framework: Spring Security
- Language: Java
- Perspective: Session policy
- Concept: session fixation risk
- Symptom: The session identifier remains attacker-controlled after login.
- Diagnostic goal: Apply a session fixation protection policy.

### Buggy code

```java
http.sessionManagement(s -> s.sessionFixation(f -> f.none()));
```

### Expected diagnosis

Keeping the pre-login session identifier permits fixation attacks.

### Corrected code

```java
http.sessionManagement(s -> s.sessionFixation(f -> f.changeSessionId()));
```

### Regression tests

```java
// Successful login changes or invalidates the pre-authentication id.
```

## SEC-M-038: security CORS differs from MVC CORS

- Difficulty: Medium
- Framework: Spring Security
- Language: Java
- Perspective: CORS
- Concept: security CORS differs from MVC CORS
- Symptom: Preflight requests are rejected before the controller.
- Diagnostic goal: Configure CORS in the security filter chain with the application policy.

### Buggy code

```java
http.cors(c -> c.disable());
```

### Expected diagnosis

The security chain can reject preflight before MVC configuration is reached.

### Corrected code

```java
http.cors(Customizer.withDefaults());
```

### Regression tests

```java
// OPTIONS preflight receives the configured allow origin and methods.
```

## SEC-M-039: logout endpoint accepts GET

- Difficulty: Medium
- Framework: Spring Security
- Language: Java
- Perspective: Logout
- Concept: logout endpoint accepts GET
- Symptom: A cross-site link can log users out unexpectedly.
- Diagnostic goal: Use POST and CSRF protection for browser logout.

### Buggy code

```java
http.logout(l -> l.logoutRequestMatcher(new AntPathRequestMatcher("/logout", "GET")));
```

### Expected diagnosis

GET should be safe and cannot carry a CSRF-protected state change reliably.

### Corrected code

```java
http.logout(l -> l.logoutUrl("/logout"));
```

### Regression tests

```java
// GET does not log out; CSRF-protected POST does.
```

## SEC-M-040: test user missing authority

- Difficulty: Medium
- Framework: Spring Security
- Language: Java
- Perspective: Testing security
- Concept: test user missing authority
- Symptom: A controller test fails before the business assertion.
- Diagnostic goal: Make the test authentication match the endpoint contract.

### Buggy code

```java
@WebMvcTest
void deletes() { mockMvc.perform(delete("/items/1")); }
```

### Expected diagnosis

The request is anonymous and security correctly denies it.

### Corrected code

```java
@WithMockUser(roles = "ADMIN")
void deletes() { mockMvc.perform(delete("/items/1").with(csrf())); }
```

### Regression tests

```java
// The test supplies both role and CSRF token.
```

## SEC-M-041: permitAll on protected path

- Difficulty: Medium
- Framework: Spring Security
- Language: Java
- Perspective: Filter chain
- Concept: permitAll on protected path
- Symptom: Unauthenticated users access an admin endpoint.
- Diagnostic goal: Order matchers from specific protected paths to general rules.

### Buggy code

```java
authorize.requestMatchers("/**").permitAll()
       .requestMatchers("/admin/**").hasRole("ADMIN")
```

### Expected diagnosis

The catch-all matcher matches first, so the admin rule is unreachable.

### Corrected code

```java
authorize.requestMatchers("/admin/**").hasRole("ADMIN")
       .anyRequest().authenticated()
```

### Regression tests

```java
// Anonymous admin access is 401/403; authenticated users follow role rules.
```

## SEC-M-042: CSRF disabled for browser session

- Difficulty: Medium
- Framework: Spring Security
- Language: Java
- Perspective: CSRF
- Concept: CSRF disabled for browser session
- Symptom: State-changing browser requests lack forgery protection.
- Diagnostic goal: Keep CSRF for cookie-authenticated browser flows.

### Buggy code

```java
http.csrf(csrf -> csrf.disable());
```

### Expected diagnosis

Disabling CSRF globally is unsafe when authentication is carried by cookies.

### Corrected code

```java
http.csrf(Customizer.withDefaults());
```

### Regression tests

```java
// A missing token is rejected for a session-authenticated POST.
```

## SEC-M-043: plain text password

- Difficulty: Medium
- Framework: Spring Security
- Language: Java
- Perspective: Password storage
- Concept: plain text password
- Symptom: A database leak exposes credentials immediately.
- Diagnostic goal: Store adaptive password hashes and compare through the encoder.

### Buggy code

```java
user.setPassword(rawPassword);
```

### Expected diagnosis

Raw passwords are reversible by anyone who obtains the database.

### Corrected code

```java
user.setPassword(passwordEncoder.encode(rawPassword));
```

### Regression tests

```java
// Login matches through passwordEncoder.matches and never compares raw storage.
```

## SEC-M-044: annotation ignored

- Difficulty: Medium
- Framework: Spring Security
- Language: Java
- Perspective: Method security
- Concept: annotation ignored
- Symptom: A role annotation has no effect.
- Diagnostic goal: Enable method security and use the correct authority prefix.

### Buggy code

```java
@PreAuthorize("hasRole("ADMIN")")
public void delete() {}
```

### Expected diagnosis

Method annotations are inactive unless method security is enabled.

### Corrected code

```java
@EnableMethodSecurity
@Configuration
class SecurityConfig {}
```

### Regression tests

```java
// Nonadmins are denied when invoking the method directly through the proxy.
```

## SEC-M-045: signature not checked

- Difficulty: Medium
- Framework: Spring Security
- Language: Java
- Perspective: JWT validation
- Concept: signature not checked
- Symptom: Forged claims authorize a request.
- Diagnostic goal: Verify signature, issuer, audience, and expiry.

### Buggy code

```java
JwtClaims claims = parser.parseUnsecured(token);
```

### Expected diagnosis

Reading claims without verification is equivalent to trusting user input.

### Corrected code

```java
JwtClaims claims = parser.verify(token, key).requireIssuer(issuer).requireAudience(audience).parse();
```

### Regression tests

```java
// Forged, expired, wrong-issuer tokens are rejected.
```

## SEC-M-046: authentication mistaken for authorization

- Difficulty: Medium
- Framework: Spring Security
- Language: Java
- Perspective: Authorization
- Concept: authentication mistaken for authorization
- Symptom: Every signed-in user can perform an admin action.
- Diagnostic goal: Require a permission or role for the operation.

### Buggy code

```java
.anyRequest().authenticated()
```

### Expected diagnosis

Authenticated only proves identity; it does not grant the admin capability.

### Corrected code

```java
.requestMatchers("/admin/**").hasAuthority("admin:write")
```

### Regression tests

```java
// A user without admin:write receives 403.
```

## SEC-M-047: session fixation risk

- Difficulty: Medium
- Framework: Spring Security
- Language: Java
- Perspective: Session policy
- Concept: session fixation risk
- Symptom: The session identifier remains attacker-controlled after login.
- Diagnostic goal: Apply a session fixation protection policy.

### Buggy code

```java
http.sessionManagement(s -> s.sessionFixation(f -> f.none()));
```

### Expected diagnosis

Keeping the pre-login session identifier permits fixation attacks.

### Corrected code

```java
http.sessionManagement(s -> s.sessionFixation(f -> f.changeSessionId()));
```

### Regression tests

```java
// Successful login changes or invalidates the pre-authentication id.
```

## SEC-M-048: security CORS differs from MVC CORS

- Difficulty: Medium
- Framework: Spring Security
- Language: Java
- Perspective: CORS
- Concept: security CORS differs from MVC CORS
- Symptom: Preflight requests are rejected before the controller.
- Diagnostic goal: Configure CORS in the security filter chain with the application policy.

### Buggy code

```java
http.cors(c -> c.disable());
```

### Expected diagnosis

The security chain can reject preflight before MVC configuration is reached.

### Corrected code

```java
http.cors(Customizer.withDefaults());
```

### Regression tests

```java
// OPTIONS preflight receives the configured allow origin and methods.
```

## SEC-M-049: logout endpoint accepts GET

- Difficulty: Medium
- Framework: Spring Security
- Language: Java
- Perspective: Logout
- Concept: logout endpoint accepts GET
- Symptom: A cross-site link can log users out unexpectedly.
- Diagnostic goal: Use POST and CSRF protection for browser logout.

### Buggy code

```java
http.logout(l -> l.logoutRequestMatcher(new AntPathRequestMatcher("/logout", "GET")));
```

### Expected diagnosis

GET should be safe and cannot carry a CSRF-protected state change reliably.

### Corrected code

```java
http.logout(l -> l.logoutUrl("/logout"));
```

### Regression tests

```java
// GET does not log out; CSRF-protected POST does.
```

## SEC-M-050: test user missing authority

- Difficulty: Medium
- Framework: Spring Security
- Language: Java
- Perspective: Testing security
- Concept: test user missing authority
- Symptom: A controller test fails before the business assertion.
- Diagnostic goal: Make the test authentication match the endpoint contract.

### Buggy code

```java
@WebMvcTest
void deletes() { mockMvc.perform(delete("/items/1")); }
```

### Expected diagnosis

The request is anonymous and security correctly denies it.

### Corrected code

```java
@WithMockUser(roles = "ADMIN")
void deletes() { mockMvc.perform(delete("/items/1").with(csrf())); }
```

### Regression tests

```java
// The test supplies both role and CSRF token.
```

## SEC-M-051: permitAll on protected path

- Difficulty: Medium
- Framework: Spring Security
- Language: Java
- Perspective: Filter chain
- Concept: permitAll on protected path
- Symptom: Unauthenticated users access an admin endpoint.
- Diagnostic goal: Order matchers from specific protected paths to general rules.

### Buggy code

```java
authorize.requestMatchers("/**").permitAll()
       .requestMatchers("/admin/**").hasRole("ADMIN")
```

### Expected diagnosis

The catch-all matcher matches first, so the admin rule is unreachable.

### Corrected code

```java
authorize.requestMatchers("/admin/**").hasRole("ADMIN")
       .anyRequest().authenticated()
```

### Regression tests

```java
// Anonymous admin access is 401/403; authenticated users follow role rules.
```

## SEC-M-052: CSRF disabled for browser session

- Difficulty: Medium
- Framework: Spring Security
- Language: Java
- Perspective: CSRF
- Concept: CSRF disabled for browser session
- Symptom: State-changing browser requests lack forgery protection.
- Diagnostic goal: Keep CSRF for cookie-authenticated browser flows.

### Buggy code

```java
http.csrf(csrf -> csrf.disable());
```

### Expected diagnosis

Disabling CSRF globally is unsafe when authentication is carried by cookies.

### Corrected code

```java
http.csrf(Customizer.withDefaults());
```

### Regression tests

```java
// A missing token is rejected for a session-authenticated POST.
```

## SEC-M-053: plain text password

- Difficulty: Medium
- Framework: Spring Security
- Language: Java
- Perspective: Password storage
- Concept: plain text password
- Symptom: A database leak exposes credentials immediately.
- Diagnostic goal: Store adaptive password hashes and compare through the encoder.

### Buggy code

```java
user.setPassword(rawPassword);
```

### Expected diagnosis

Raw passwords are reversible by anyone who obtains the database.

### Corrected code

```java
user.setPassword(passwordEncoder.encode(rawPassword));
```

### Regression tests

```java
// Login matches through passwordEncoder.matches and never compares raw storage.
```

## SEC-M-054: annotation ignored

- Difficulty: Medium
- Framework: Spring Security
- Language: Java
- Perspective: Method security
- Concept: annotation ignored
- Symptom: A role annotation has no effect.
- Diagnostic goal: Enable method security and use the correct authority prefix.

### Buggy code

```java
@PreAuthorize("hasRole("ADMIN")")
public void delete() {}
```

### Expected diagnosis

Method annotations are inactive unless method security is enabled.

### Corrected code

```java
@EnableMethodSecurity
@Configuration
class SecurityConfig {}
```

### Regression tests

```java
// Nonadmins are denied when invoking the method directly through the proxy.
```

## SEC-M-055: signature not checked

- Difficulty: Medium
- Framework: Spring Security
- Language: Java
- Perspective: JWT validation
- Concept: signature not checked
- Symptom: Forged claims authorize a request.
- Diagnostic goal: Verify signature, issuer, audience, and expiry.

### Buggy code

```java
JwtClaims claims = parser.parseUnsecured(token);
```

### Expected diagnosis

Reading claims without verification is equivalent to trusting user input.

### Corrected code

```java
JwtClaims claims = parser.verify(token, key).requireIssuer(issuer).requireAudience(audience).parse();
```

### Regression tests

```java
// Forged, expired, wrong-issuer tokens are rejected.
```

## SEC-M-056: authentication mistaken for authorization

- Difficulty: Medium
- Framework: Spring Security
- Language: Java
- Perspective: Authorization
- Concept: authentication mistaken for authorization
- Symptom: Every signed-in user can perform an admin action.
- Diagnostic goal: Require a permission or role for the operation.

### Buggy code

```java
.anyRequest().authenticated()
```

### Expected diagnosis

Authenticated only proves identity; it does not grant the admin capability.

### Corrected code

```java
.requestMatchers("/admin/**").hasAuthority("admin:write")
```

### Regression tests

```java
// A user without admin:write receives 403.
```

## SEC-M-057: session fixation risk

- Difficulty: Medium
- Framework: Spring Security
- Language: Java
- Perspective: Session policy
- Concept: session fixation risk
- Symptom: The session identifier remains attacker-controlled after login.
- Diagnostic goal: Apply a session fixation protection policy.

### Buggy code

```java
http.sessionManagement(s -> s.sessionFixation(f -> f.none()));
```

### Expected diagnosis

Keeping the pre-login session identifier permits fixation attacks.

### Corrected code

```java
http.sessionManagement(s -> s.sessionFixation(f -> f.changeSessionId()));
```

### Regression tests

```java
// Successful login changes or invalidates the pre-authentication id.
```

## SEC-M-058: security CORS differs from MVC CORS

- Difficulty: Medium
- Framework: Spring Security
- Language: Java
- Perspective: CORS
- Concept: security CORS differs from MVC CORS
- Symptom: Preflight requests are rejected before the controller.
- Diagnostic goal: Configure CORS in the security filter chain with the application policy.

### Buggy code

```java
http.cors(c -> c.disable());
```

### Expected diagnosis

The security chain can reject preflight before MVC configuration is reached.

### Corrected code

```java
http.cors(Customizer.withDefaults());
```

### Regression tests

```java
// OPTIONS preflight receives the configured allow origin and methods.
```

## SEC-M-059: logout endpoint accepts GET

- Difficulty: Medium
- Framework: Spring Security
- Language: Java
- Perspective: Logout
- Concept: logout endpoint accepts GET
- Symptom: A cross-site link can log users out unexpectedly.
- Diagnostic goal: Use POST and CSRF protection for browser logout.

### Buggy code

```java
http.logout(l -> l.logoutRequestMatcher(new AntPathRequestMatcher("/logout", "GET")));
```

### Expected diagnosis

GET should be safe and cannot carry a CSRF-protected state change reliably.

### Corrected code

```java
http.logout(l -> l.logoutUrl("/logout"));
```

### Regression tests

```java
// GET does not log out; CSRF-protected POST does.
```

## SEC-M-060: test user missing authority

- Difficulty: Medium
- Framework: Spring Security
- Language: Java
- Perspective: Testing security
- Concept: test user missing authority
- Symptom: A controller test fails before the business assertion.
- Diagnostic goal: Make the test authentication match the endpoint contract.

### Buggy code

```java
@WebMvcTest
void deletes() { mockMvc.perform(delete("/items/1")); }
```

### Expected diagnosis

The request is anonymous and security correctly denies it.

### Corrected code

```java
@WithMockUser(roles = "ADMIN")
void deletes() { mockMvc.perform(delete("/items/1").with(csrf())); }
```

### Regression tests

```java
// The test supplies both role and CSRF token.
```

## SEC-M-061: permitAll on protected path

- Difficulty: Medium
- Framework: Spring Security
- Language: Java
- Perspective: Filter chain
- Concept: permitAll on protected path
- Symptom: Unauthenticated users access an admin endpoint.
- Diagnostic goal: Order matchers from specific protected paths to general rules.

### Buggy code

```java
authorize.requestMatchers("/**").permitAll()
       .requestMatchers("/admin/**").hasRole("ADMIN")
```

### Expected diagnosis

The catch-all matcher matches first, so the admin rule is unreachable.

### Corrected code

```java
authorize.requestMatchers("/admin/**").hasRole("ADMIN")
       .anyRequest().authenticated()
```

### Regression tests

```java
// Anonymous admin access is 401/403; authenticated users follow role rules.
```

## SEC-M-062: CSRF disabled for browser session

- Difficulty: Medium
- Framework: Spring Security
- Language: Java
- Perspective: CSRF
- Concept: CSRF disabled for browser session
- Symptom: State-changing browser requests lack forgery protection.
- Diagnostic goal: Keep CSRF for cookie-authenticated browser flows.

### Buggy code

```java
http.csrf(csrf -> csrf.disable());
```

### Expected diagnosis

Disabling CSRF globally is unsafe when authentication is carried by cookies.

### Corrected code

```java
http.csrf(Customizer.withDefaults());
```

### Regression tests

```java
// A missing token is rejected for a session-authenticated POST.
```

## SEC-M-063: plain text password

- Difficulty: Medium
- Framework: Spring Security
- Language: Java
- Perspective: Password storage
- Concept: plain text password
- Symptom: A database leak exposes credentials immediately.
- Diagnostic goal: Store adaptive password hashes and compare through the encoder.

### Buggy code

```java
user.setPassword(rawPassword);
```

### Expected diagnosis

Raw passwords are reversible by anyone who obtains the database.

### Corrected code

```java
user.setPassword(passwordEncoder.encode(rawPassword));
```

### Regression tests

```java
// Login matches through passwordEncoder.matches and never compares raw storage.
```

## SEC-M-064: annotation ignored

- Difficulty: Medium
- Framework: Spring Security
- Language: Java
- Perspective: Method security
- Concept: annotation ignored
- Symptom: A role annotation has no effect.
- Diagnostic goal: Enable method security and use the correct authority prefix.

### Buggy code

```java
@PreAuthorize("hasRole("ADMIN")")
public void delete() {}
```

### Expected diagnosis

Method annotations are inactive unless method security is enabled.

### Corrected code

```java
@EnableMethodSecurity
@Configuration
class SecurityConfig {}
```

### Regression tests

```java
// Nonadmins are denied when invoking the method directly through the proxy.
```

## SEC-M-065: signature not checked

- Difficulty: Medium
- Framework: Spring Security
- Language: Java
- Perspective: JWT validation
- Concept: signature not checked
- Symptom: Forged claims authorize a request.
- Diagnostic goal: Verify signature, issuer, audience, and expiry.

### Buggy code

```java
JwtClaims claims = parser.parseUnsecured(token);
```

### Expected diagnosis

Reading claims without verification is equivalent to trusting user input.

### Corrected code

```java
JwtClaims claims = parser.verify(token, key).requireIssuer(issuer).requireAudience(audience).parse();
```

### Regression tests

```java
// Forged, expired, wrong-issuer tokens are rejected.
```

## SEC-M-066: authentication mistaken for authorization

- Difficulty: Medium
- Framework: Spring Security
- Language: Java
- Perspective: Authorization
- Concept: authentication mistaken for authorization
- Symptom: Every signed-in user can perform an admin action.
- Diagnostic goal: Require a permission or role for the operation.

### Buggy code

```java
.anyRequest().authenticated()
```

### Expected diagnosis

Authenticated only proves identity; it does not grant the admin capability.

### Corrected code

```java
.requestMatchers("/admin/**").hasAuthority("admin:write")
```

### Regression tests

```java
// A user without admin:write receives 403.
```

## SEC-M-067: session fixation risk

- Difficulty: Medium
- Framework: Spring Security
- Language: Java
- Perspective: Session policy
- Concept: session fixation risk
- Symptom: The session identifier remains attacker-controlled after login.
- Diagnostic goal: Apply a session fixation protection policy.

### Buggy code

```java
http.sessionManagement(s -> s.sessionFixation(f -> f.none()));
```

### Expected diagnosis

Keeping the pre-login session identifier permits fixation attacks.

### Corrected code

```java
http.sessionManagement(s -> s.sessionFixation(f -> f.changeSessionId()));
```

### Regression tests

```java
// Successful login changes or invalidates the pre-authentication id.
```

## SEC-M-068: security CORS differs from MVC CORS

- Difficulty: Medium
- Framework: Spring Security
- Language: Java
- Perspective: CORS
- Concept: security CORS differs from MVC CORS
- Symptom: Preflight requests are rejected before the controller.
- Diagnostic goal: Configure CORS in the security filter chain with the application policy.

### Buggy code

```java
http.cors(c -> c.disable());
```

### Expected diagnosis

The security chain can reject preflight before MVC configuration is reached.

### Corrected code

```java
http.cors(Customizer.withDefaults());
```

### Regression tests

```java
// OPTIONS preflight receives the configured allow origin and methods.
```

## SEC-M-069: logout endpoint accepts GET

- Difficulty: Medium
- Framework: Spring Security
- Language: Java
- Perspective: Logout
- Concept: logout endpoint accepts GET
- Symptom: A cross-site link can log users out unexpectedly.
- Diagnostic goal: Use POST and CSRF protection for browser logout.

### Buggy code

```java
http.logout(l -> l.logoutRequestMatcher(new AntPathRequestMatcher("/logout", "GET")));
```

### Expected diagnosis

GET should be safe and cannot carry a CSRF-protected state change reliably.

### Corrected code

```java
http.logout(l -> l.logoutUrl("/logout"));
```

### Regression tests

```java
// GET does not log out; CSRF-protected POST does.
```

## SEC-M-070: test user missing authority

- Difficulty: Medium
- Framework: Spring Security
- Language: Java
- Perspective: Testing security
- Concept: test user missing authority
- Symptom: A controller test fails before the business assertion.
- Diagnostic goal: Make the test authentication match the endpoint contract.

### Buggy code

```java
@WebMvcTest
void deletes() { mockMvc.perform(delete("/items/1")); }
```

### Expected diagnosis

The request is anonymous and security correctly denies it.

### Corrected code

```java
@WithMockUser(roles = "ADMIN")
void deletes() { mockMvc.perform(delete("/items/1").with(csrf())); }
```

### Regression tests

```java
// The test supplies both role and CSRF token.
```

## SEC-M-071: permitAll on protected path

- Difficulty: Medium
- Framework: Spring Security
- Language: Java
- Perspective: Filter chain
- Concept: permitAll on protected path
- Symptom: Unauthenticated users access an admin endpoint.
- Diagnostic goal: Order matchers from specific protected paths to general rules.

### Buggy code

```java
authorize.requestMatchers("/**").permitAll()
       .requestMatchers("/admin/**").hasRole("ADMIN")
```

### Expected diagnosis

The catch-all matcher matches first, so the admin rule is unreachable.

### Corrected code

```java
authorize.requestMatchers("/admin/**").hasRole("ADMIN")
       .anyRequest().authenticated()
```

### Regression tests

```java
// Anonymous admin access is 401/403; authenticated users follow role rules.
```

## SEC-M-072: CSRF disabled for browser session

- Difficulty: Medium
- Framework: Spring Security
- Language: Java
- Perspective: CSRF
- Concept: CSRF disabled for browser session
- Symptom: State-changing browser requests lack forgery protection.
- Diagnostic goal: Keep CSRF for cookie-authenticated browser flows.

### Buggy code

```java
http.csrf(csrf -> csrf.disable());
```

### Expected diagnosis

Disabling CSRF globally is unsafe when authentication is carried by cookies.

### Corrected code

```java
http.csrf(Customizer.withDefaults());
```

### Regression tests

```java
// A missing token is rejected for a session-authenticated POST.
```

## SEC-M-073: plain text password

- Difficulty: Medium
- Framework: Spring Security
- Language: Java
- Perspective: Password storage
- Concept: plain text password
- Symptom: A database leak exposes credentials immediately.
- Diagnostic goal: Store adaptive password hashes and compare through the encoder.

### Buggy code

```java
user.setPassword(rawPassword);
```

### Expected diagnosis

Raw passwords are reversible by anyone who obtains the database.

### Corrected code

```java
user.setPassword(passwordEncoder.encode(rawPassword));
```

### Regression tests

```java
// Login matches through passwordEncoder.matches and never compares raw storage.
```

## SEC-M-074: annotation ignored

- Difficulty: Medium
- Framework: Spring Security
- Language: Java
- Perspective: Method security
- Concept: annotation ignored
- Symptom: A role annotation has no effect.
- Diagnostic goal: Enable method security and use the correct authority prefix.

### Buggy code

```java
@PreAuthorize("hasRole("ADMIN")")
public void delete() {}
```

### Expected diagnosis

Method annotations are inactive unless method security is enabled.

### Corrected code

```java
@EnableMethodSecurity
@Configuration
class SecurityConfig {}
```

### Regression tests

```java
// Nonadmins are denied when invoking the method directly through the proxy.
```

## SEC-M-075: signature not checked

- Difficulty: Medium
- Framework: Spring Security
- Language: Java
- Perspective: JWT validation
- Concept: signature not checked
- Symptom: Forged claims authorize a request.
- Diagnostic goal: Verify signature, issuer, audience, and expiry.

### Buggy code

```java
JwtClaims claims = parser.parseUnsecured(token);
```

### Expected diagnosis

Reading claims without verification is equivalent to trusting user input.

### Corrected code

```java
JwtClaims claims = parser.verify(token, key).requireIssuer(issuer).requireAudience(audience).parse();
```

### Regression tests

```java
// Forged, expired, wrong-issuer tokens are rejected.
```

## SEC-M-076: authentication mistaken for authorization

- Difficulty: Medium
- Framework: Spring Security
- Language: Java
- Perspective: Authorization
- Concept: authentication mistaken for authorization
- Symptom: Every signed-in user can perform an admin action.
- Diagnostic goal: Require a permission or role for the operation.

### Buggy code

```java
.anyRequest().authenticated()
```

### Expected diagnosis

Authenticated only proves identity; it does not grant the admin capability.

### Corrected code

```java
.requestMatchers("/admin/**").hasAuthority("admin:write")
```

### Regression tests

```java
// A user without admin:write receives 403.
```

## SEC-M-077: session fixation risk

- Difficulty: Medium
- Framework: Spring Security
- Language: Java
- Perspective: Session policy
- Concept: session fixation risk
- Symptom: The session identifier remains attacker-controlled after login.
- Diagnostic goal: Apply a session fixation protection policy.

### Buggy code

```java
http.sessionManagement(s -> s.sessionFixation(f -> f.none()));
```

### Expected diagnosis

Keeping the pre-login session identifier permits fixation attacks.

### Corrected code

```java
http.sessionManagement(s -> s.sessionFixation(f -> f.changeSessionId()));
```

### Regression tests

```java
// Successful login changes or invalidates the pre-authentication id.
```

## SEC-M-078: security CORS differs from MVC CORS

- Difficulty: Medium
- Framework: Spring Security
- Language: Java
- Perspective: CORS
- Concept: security CORS differs from MVC CORS
- Symptom: Preflight requests are rejected before the controller.
- Diagnostic goal: Configure CORS in the security filter chain with the application policy.

### Buggy code

```java
http.cors(c -> c.disable());
```

### Expected diagnosis

The security chain can reject preflight before MVC configuration is reached.

### Corrected code

```java
http.cors(Customizer.withDefaults());
```

### Regression tests

```java
// OPTIONS preflight receives the configured allow origin and methods.
```

## SEC-M-079: logout endpoint accepts GET

- Difficulty: Medium
- Framework: Spring Security
- Language: Java
- Perspective: Logout
- Concept: logout endpoint accepts GET
- Symptom: A cross-site link can log users out unexpectedly.
- Diagnostic goal: Use POST and CSRF protection for browser logout.

### Buggy code

```java
http.logout(l -> l.logoutRequestMatcher(new AntPathRequestMatcher("/logout", "GET")));
```

### Expected diagnosis

GET should be safe and cannot carry a CSRF-protected state change reliably.

### Corrected code

```java
http.logout(l -> l.logoutUrl("/logout"));
```

### Regression tests

```java
// GET does not log out; CSRF-protected POST does.
```

## SEC-M-080: test user missing authority

- Difficulty: Medium
- Framework: Spring Security
- Language: Java
- Perspective: Testing security
- Concept: test user missing authority
- Symptom: A controller test fails before the business assertion.
- Diagnostic goal: Make the test authentication match the endpoint contract.

### Buggy code

```java
@WebMvcTest
void deletes() { mockMvc.perform(delete("/items/1")); }
```

### Expected diagnosis

The request is anonymous and security correctly denies it.

### Corrected code

```java
@WithMockUser(roles = "ADMIN")
void deletes() { mockMvc.perform(delete("/items/1").with(csrf())); }
```

### Regression tests

```java
// The test supplies both role and CSRF token.
```

## SEC-M-081: permitAll on protected path

- Difficulty: Medium
- Framework: Spring Security
- Language: Java
- Perspective: Filter chain
- Concept: permitAll on protected path
- Symptom: Unauthenticated users access an admin endpoint.
- Diagnostic goal: Order matchers from specific protected paths to general rules.

### Buggy code

```java
authorize.requestMatchers("/**").permitAll()
       .requestMatchers("/admin/**").hasRole("ADMIN")
```

### Expected diagnosis

The catch-all matcher matches first, so the admin rule is unreachable.

### Corrected code

```java
authorize.requestMatchers("/admin/**").hasRole("ADMIN")
       .anyRequest().authenticated()
```

### Regression tests

```java
// Anonymous admin access is 401/403; authenticated users follow role rules.
```

## SEC-M-082: CSRF disabled for browser session

- Difficulty: Medium
- Framework: Spring Security
- Language: Java
- Perspective: CSRF
- Concept: CSRF disabled for browser session
- Symptom: State-changing browser requests lack forgery protection.
- Diagnostic goal: Keep CSRF for cookie-authenticated browser flows.

### Buggy code

```java
http.csrf(csrf -> csrf.disable());
```

### Expected diagnosis

Disabling CSRF globally is unsafe when authentication is carried by cookies.

### Corrected code

```java
http.csrf(Customizer.withDefaults());
```

### Regression tests

```java
// A missing token is rejected for a session-authenticated POST.
```

## SEC-M-083: plain text password

- Difficulty: Medium
- Framework: Spring Security
- Language: Java
- Perspective: Password storage
- Concept: plain text password
- Symptom: A database leak exposes credentials immediately.
- Diagnostic goal: Store adaptive password hashes and compare through the encoder.

### Buggy code

```java
user.setPassword(rawPassword);
```

### Expected diagnosis

Raw passwords are reversible by anyone who obtains the database.

### Corrected code

```java
user.setPassword(passwordEncoder.encode(rawPassword));
```

### Regression tests

```java
// Login matches through passwordEncoder.matches and never compares raw storage.
```

## SEC-M-084: annotation ignored

- Difficulty: Medium
- Framework: Spring Security
- Language: Java
- Perspective: Method security
- Concept: annotation ignored
- Symptom: A role annotation has no effect.
- Diagnostic goal: Enable method security and use the correct authority prefix.

### Buggy code

```java
@PreAuthorize("hasRole("ADMIN")")
public void delete() {}
```

### Expected diagnosis

Method annotations are inactive unless method security is enabled.

### Corrected code

```java
@EnableMethodSecurity
@Configuration
class SecurityConfig {}
```

### Regression tests

```java
// Nonadmins are denied when invoking the method directly through the proxy.
```

## SEC-M-085: signature not checked

- Difficulty: Medium
- Framework: Spring Security
- Language: Java
- Perspective: JWT validation
- Concept: signature not checked
- Symptom: Forged claims authorize a request.
- Diagnostic goal: Verify signature, issuer, audience, and expiry.

### Buggy code

```java
JwtClaims claims = parser.parseUnsecured(token);
```

### Expected diagnosis

Reading claims without verification is equivalent to trusting user input.

### Corrected code

```java
JwtClaims claims = parser.verify(token, key).requireIssuer(issuer).requireAudience(audience).parse();
```

### Regression tests

```java
// Forged, expired, wrong-issuer tokens are rejected.
```

## SEC-M-086: authentication mistaken for authorization

- Difficulty: Medium
- Framework: Spring Security
- Language: Java
- Perspective: Authorization
- Concept: authentication mistaken for authorization
- Symptom: Every signed-in user can perform an admin action.
- Diagnostic goal: Require a permission or role for the operation.

### Buggy code

```java
.anyRequest().authenticated()
```

### Expected diagnosis

Authenticated only proves identity; it does not grant the admin capability.

### Corrected code

```java
.requestMatchers("/admin/**").hasAuthority("admin:write")
```

### Regression tests

```java
// A user without admin:write receives 403.
```

## SEC-M-087: session fixation risk

- Difficulty: Medium
- Framework: Spring Security
- Language: Java
- Perspective: Session policy
- Concept: session fixation risk
- Symptom: The session identifier remains attacker-controlled after login.
- Diagnostic goal: Apply a session fixation protection policy.

### Buggy code

```java
http.sessionManagement(s -> s.sessionFixation(f -> f.none()));
```

### Expected diagnosis

Keeping the pre-login session identifier permits fixation attacks.

### Corrected code

```java
http.sessionManagement(s -> s.sessionFixation(f -> f.changeSessionId()));
```

### Regression tests

```java
// Successful login changes or invalidates the pre-authentication id.
```

## SEC-M-088: security CORS differs from MVC CORS

- Difficulty: Medium
- Framework: Spring Security
- Language: Java
- Perspective: CORS
- Concept: security CORS differs from MVC CORS
- Symptom: Preflight requests are rejected before the controller.
- Diagnostic goal: Configure CORS in the security filter chain with the application policy.

### Buggy code

```java
http.cors(c -> c.disable());
```

### Expected diagnosis

The security chain can reject preflight before MVC configuration is reached.

### Corrected code

```java
http.cors(Customizer.withDefaults());
```

### Regression tests

```java
// OPTIONS preflight receives the configured allow origin and methods.
```

## SEC-M-089: logout endpoint accepts GET

- Difficulty: Medium
- Framework: Spring Security
- Language: Java
- Perspective: Logout
- Concept: logout endpoint accepts GET
- Symptom: A cross-site link can log users out unexpectedly.
- Diagnostic goal: Use POST and CSRF protection for browser logout.

### Buggy code

```java
http.logout(l -> l.logoutRequestMatcher(new AntPathRequestMatcher("/logout", "GET")));
```

### Expected diagnosis

GET should be safe and cannot carry a CSRF-protected state change reliably.

### Corrected code

```java
http.logout(l -> l.logoutUrl("/logout"));
```

### Regression tests

```java
// GET does not log out; CSRF-protected POST does.
```

## SEC-M-090: test user missing authority

- Difficulty: Medium
- Framework: Spring Security
- Language: Java
- Perspective: Testing security
- Concept: test user missing authority
- Symptom: A controller test fails before the business assertion.
- Diagnostic goal: Make the test authentication match the endpoint contract.

### Buggy code

```java
@WebMvcTest
void deletes() { mockMvc.perform(delete("/items/1")); }
```

### Expected diagnosis

The request is anonymous and security correctly denies it.

### Corrected code

```java
@WithMockUser(roles = "ADMIN")
void deletes() { mockMvc.perform(delete("/items/1").with(csrf())); }
```

### Regression tests

```java
// The test supplies both role and CSRF token.
```

## SEC-M-091: permitAll on protected path

- Difficulty: Medium
- Framework: Spring Security
- Language: Java
- Perspective: Filter chain
- Concept: permitAll on protected path
- Symptom: Unauthenticated users access an admin endpoint.
- Diagnostic goal: Order matchers from specific protected paths to general rules.

### Buggy code

```java
authorize.requestMatchers("/**").permitAll()
       .requestMatchers("/admin/**").hasRole("ADMIN")
```

### Expected diagnosis

The catch-all matcher matches first, so the admin rule is unreachable.

### Corrected code

```java
authorize.requestMatchers("/admin/**").hasRole("ADMIN")
       .anyRequest().authenticated()
```

### Regression tests

```java
// Anonymous admin access is 401/403; authenticated users follow role rules.
```

## SEC-M-092: CSRF disabled for browser session

- Difficulty: Medium
- Framework: Spring Security
- Language: Java
- Perspective: CSRF
- Concept: CSRF disabled for browser session
- Symptom: State-changing browser requests lack forgery protection.
- Diagnostic goal: Keep CSRF for cookie-authenticated browser flows.

### Buggy code

```java
http.csrf(csrf -> csrf.disable());
```

### Expected diagnosis

Disabling CSRF globally is unsafe when authentication is carried by cookies.

### Corrected code

```java
http.csrf(Customizer.withDefaults());
```

### Regression tests

```java
// A missing token is rejected for a session-authenticated POST.
```

## SEC-M-093: plain text password

- Difficulty: Medium
- Framework: Spring Security
- Language: Java
- Perspective: Password storage
- Concept: plain text password
- Symptom: A database leak exposes credentials immediately.
- Diagnostic goal: Store adaptive password hashes and compare through the encoder.

### Buggy code

```java
user.setPassword(rawPassword);
```

### Expected diagnosis

Raw passwords are reversible by anyone who obtains the database.

### Corrected code

```java
user.setPassword(passwordEncoder.encode(rawPassword));
```

### Regression tests

```java
// Login matches through passwordEncoder.matches and never compares raw storage.
```

## SEC-M-094: annotation ignored

- Difficulty: Medium
- Framework: Spring Security
- Language: Java
- Perspective: Method security
- Concept: annotation ignored
- Symptom: A role annotation has no effect.
- Diagnostic goal: Enable method security and use the correct authority prefix.

### Buggy code

```java
@PreAuthorize("hasRole("ADMIN")")
public void delete() {}
```

### Expected diagnosis

Method annotations are inactive unless method security is enabled.

### Corrected code

```java
@EnableMethodSecurity
@Configuration
class SecurityConfig {}
```

### Regression tests

```java
// Nonadmins are denied when invoking the method directly through the proxy.
```

## SEC-M-095: signature not checked

- Difficulty: Medium
- Framework: Spring Security
- Language: Java
- Perspective: JWT validation
- Concept: signature not checked
- Symptom: Forged claims authorize a request.
- Diagnostic goal: Verify signature, issuer, audience, and expiry.

### Buggy code

```java
JwtClaims claims = parser.parseUnsecured(token);
```

### Expected diagnosis

Reading claims without verification is equivalent to trusting user input.

### Corrected code

```java
JwtClaims claims = parser.verify(token, key).requireIssuer(issuer).requireAudience(audience).parse();
```

### Regression tests

```java
// Forged, expired, wrong-issuer tokens are rejected.
```

## SEC-M-096: authentication mistaken for authorization

- Difficulty: Medium
- Framework: Spring Security
- Language: Java
- Perspective: Authorization
- Concept: authentication mistaken for authorization
- Symptom: Every signed-in user can perform an admin action.
- Diagnostic goal: Require a permission or role for the operation.

### Buggy code

```java
.anyRequest().authenticated()
```

### Expected diagnosis

Authenticated only proves identity; it does not grant the admin capability.

### Corrected code

```java
.requestMatchers("/admin/**").hasAuthority("admin:write")
```

### Regression tests

```java
// A user without admin:write receives 403.
```

## SEC-M-097: session fixation risk

- Difficulty: Medium
- Framework: Spring Security
- Language: Java
- Perspective: Session policy
- Concept: session fixation risk
- Symptom: The session identifier remains attacker-controlled after login.
- Diagnostic goal: Apply a session fixation protection policy.

### Buggy code

```java
http.sessionManagement(s -> s.sessionFixation(f -> f.none()));
```

### Expected diagnosis

Keeping the pre-login session identifier permits fixation attacks.

### Corrected code

```java
http.sessionManagement(s -> s.sessionFixation(f -> f.changeSessionId()));
```

### Regression tests

```java
// Successful login changes or invalidates the pre-authentication id.
```

## SEC-M-098: security CORS differs from MVC CORS

- Difficulty: Medium
- Framework: Spring Security
- Language: Java
- Perspective: CORS
- Concept: security CORS differs from MVC CORS
- Symptom: Preflight requests are rejected before the controller.
- Diagnostic goal: Configure CORS in the security filter chain with the application policy.

### Buggy code

```java
http.cors(c -> c.disable());
```

### Expected diagnosis

The security chain can reject preflight before MVC configuration is reached.

### Corrected code

```java
http.cors(Customizer.withDefaults());
```

### Regression tests

```java
// OPTIONS preflight receives the configured allow origin and methods.
```

## SEC-M-099: logout endpoint accepts GET

- Difficulty: Medium
- Framework: Spring Security
- Language: Java
- Perspective: Logout
- Concept: logout endpoint accepts GET
- Symptom: A cross-site link can log users out unexpectedly.
- Diagnostic goal: Use POST and CSRF protection for browser logout.

### Buggy code

```java
http.logout(l -> l.logoutRequestMatcher(new AntPathRequestMatcher("/logout", "GET")));
```

### Expected diagnosis

GET should be safe and cannot carry a CSRF-protected state change reliably.

### Corrected code

```java
http.logout(l -> l.logoutUrl("/logout"));
```

### Regression tests

```java
// GET does not log out; CSRF-protected POST does.
```

## SEC-M-100: test user missing authority

- Difficulty: Medium
- Framework: Spring Security
- Language: Java
- Perspective: Testing security
- Concept: test user missing authority
- Symptom: A controller test fails before the business assertion.
- Diagnostic goal: Make the test authentication match the endpoint contract.

### Buggy code

```java
@WebMvcTest
void deletes() { mockMvc.perform(delete("/items/1")); }
```

### Expected diagnosis

The request is anonymous and security correctly denies it.

### Corrected code

```java
@WithMockUser(roles = "ADMIN")
void deletes() { mockMvc.perform(delete("/items/1").with(csrf())); }
```

### Regression tests

```java
// The test supplies both role and CSRF token.
```

## SEC-H-001: permitAll on protected path

- Difficulty: Hard
- Framework: Spring Security
- Language: Java
- Perspective: Filter chain
- Concept: permitAll on protected path
- Symptom: Unauthenticated users access an admin endpoint.
- Diagnostic goal: Order matchers from specific protected paths to general rules.

### Buggy code

```java
authorize.requestMatchers("/**").permitAll()
       .requestMatchers("/admin/**").hasRole("ADMIN")
```

### Expected diagnosis

The catch-all matcher matches first, so the admin rule is unreachable.

### Corrected code

```java
authorize.requestMatchers("/admin/**").hasRole("ADMIN")
       .anyRequest().authenticated()
```

### Regression tests

```java
// Anonymous admin access is 401/403; authenticated users follow role rules.
```

## SEC-H-002: CSRF disabled for browser session

- Difficulty: Hard
- Framework: Spring Security
- Language: Java
- Perspective: CSRF
- Concept: CSRF disabled for browser session
- Symptom: State-changing browser requests lack forgery protection.
- Diagnostic goal: Keep CSRF for cookie-authenticated browser flows.

### Buggy code

```java
http.csrf(csrf -> csrf.disable());
```

### Expected diagnosis

Disabling CSRF globally is unsafe when authentication is carried by cookies.

### Corrected code

```java
http.csrf(Customizer.withDefaults());
```

### Regression tests

```java
// A missing token is rejected for a session-authenticated POST.
```

## SEC-H-003: plain text password

- Difficulty: Hard
- Framework: Spring Security
- Language: Java
- Perspective: Password storage
- Concept: plain text password
- Symptom: A database leak exposes credentials immediately.
- Diagnostic goal: Store adaptive password hashes and compare through the encoder.

### Buggy code

```java
user.setPassword(rawPassword);
```

### Expected diagnosis

Raw passwords are reversible by anyone who obtains the database.

### Corrected code

```java
user.setPassword(passwordEncoder.encode(rawPassword));
```

### Regression tests

```java
// Login matches through passwordEncoder.matches and never compares raw storage.
```

## SEC-H-004: annotation ignored

- Difficulty: Hard
- Framework: Spring Security
- Language: Java
- Perspective: Method security
- Concept: annotation ignored
- Symptom: A role annotation has no effect.
- Diagnostic goal: Enable method security and use the correct authority prefix.

### Buggy code

```java
@PreAuthorize("hasRole("ADMIN")")
public void delete() {}
```

### Expected diagnosis

Method annotations are inactive unless method security is enabled.

### Corrected code

```java
@EnableMethodSecurity
@Configuration
class SecurityConfig {}
```

### Regression tests

```java
// Nonadmins are denied when invoking the method directly through the proxy.
```

## SEC-H-005: signature not checked

- Difficulty: Hard
- Framework: Spring Security
- Language: Java
- Perspective: JWT validation
- Concept: signature not checked
- Symptom: Forged claims authorize a request.
- Diagnostic goal: Verify signature, issuer, audience, and expiry.

### Buggy code

```java
JwtClaims claims = parser.parseUnsecured(token);
```

### Expected diagnosis

Reading claims without verification is equivalent to trusting user input.

### Corrected code

```java
JwtClaims claims = parser.verify(token, key).requireIssuer(issuer).requireAudience(audience).parse();
```

### Regression tests

```java
// Forged, expired, wrong-issuer tokens are rejected.
```

## SEC-H-006: authentication mistaken for authorization

- Difficulty: Hard
- Framework: Spring Security
- Language: Java
- Perspective: Authorization
- Concept: authentication mistaken for authorization
- Symptom: Every signed-in user can perform an admin action.
- Diagnostic goal: Require a permission or role for the operation.

### Buggy code

```java
.anyRequest().authenticated()
```

### Expected diagnosis

Authenticated only proves identity; it does not grant the admin capability.

### Corrected code

```java
.requestMatchers("/admin/**").hasAuthority("admin:write")
```

### Regression tests

```java
// A user without admin:write receives 403.
```

## SEC-H-007: session fixation risk

- Difficulty: Hard
- Framework: Spring Security
- Language: Java
- Perspective: Session policy
- Concept: session fixation risk
- Symptom: The session identifier remains attacker-controlled after login.
- Diagnostic goal: Apply a session fixation protection policy.

### Buggy code

```java
http.sessionManagement(s -> s.sessionFixation(f -> f.none()));
```

### Expected diagnosis

Keeping the pre-login session identifier permits fixation attacks.

### Corrected code

```java
http.sessionManagement(s -> s.sessionFixation(f -> f.changeSessionId()));
```

### Regression tests

```java
// Successful login changes or invalidates the pre-authentication id.
```

## SEC-H-008: security CORS differs from MVC CORS

- Difficulty: Hard
- Framework: Spring Security
- Language: Java
- Perspective: CORS
- Concept: security CORS differs from MVC CORS
- Symptom: Preflight requests are rejected before the controller.
- Diagnostic goal: Configure CORS in the security filter chain with the application policy.

### Buggy code

```java
http.cors(c -> c.disable());
```

### Expected diagnosis

The security chain can reject preflight before MVC configuration is reached.

### Corrected code

```java
http.cors(Customizer.withDefaults());
```

### Regression tests

```java
// OPTIONS preflight receives the configured allow origin and methods.
```

## SEC-H-009: logout endpoint accepts GET

- Difficulty: Hard
- Framework: Spring Security
- Language: Java
- Perspective: Logout
- Concept: logout endpoint accepts GET
- Symptom: A cross-site link can log users out unexpectedly.
- Diagnostic goal: Use POST and CSRF protection for browser logout.

### Buggy code

```java
http.logout(l -> l.logoutRequestMatcher(new AntPathRequestMatcher("/logout", "GET")));
```

### Expected diagnosis

GET should be safe and cannot carry a CSRF-protected state change reliably.

### Corrected code

```java
http.logout(l -> l.logoutUrl("/logout"));
```

### Regression tests

```java
// GET does not log out; CSRF-protected POST does.
```

## SEC-H-010: test user missing authority

- Difficulty: Hard
- Framework: Spring Security
- Language: Java
- Perspective: Testing security
- Concept: test user missing authority
- Symptom: A controller test fails before the business assertion.
- Diagnostic goal: Make the test authentication match the endpoint contract.

### Buggy code

```java
@WebMvcTest
void deletes() { mockMvc.perform(delete("/items/1")); }
```

### Expected diagnosis

The request is anonymous and security correctly denies it.

### Corrected code

```java
@WithMockUser(roles = "ADMIN")
void deletes() { mockMvc.perform(delete("/items/1").with(csrf())); }
```

### Regression tests

```java
// The test supplies both role and CSRF token.
```

## SEC-H-011: permitAll on protected path

- Difficulty: Hard
- Framework: Spring Security
- Language: Java
- Perspective: Filter chain
- Concept: permitAll on protected path
- Symptom: Unauthenticated users access an admin endpoint.
- Diagnostic goal: Order matchers from specific protected paths to general rules.

### Buggy code

```java
authorize.requestMatchers("/**").permitAll()
       .requestMatchers("/admin/**").hasRole("ADMIN")
```

### Expected diagnosis

The catch-all matcher matches first, so the admin rule is unreachable.

### Corrected code

```java
authorize.requestMatchers("/admin/**").hasRole("ADMIN")
       .anyRequest().authenticated()
```

### Regression tests

```java
// Anonymous admin access is 401/403; authenticated users follow role rules.
```

## SEC-H-012: CSRF disabled for browser session

- Difficulty: Hard
- Framework: Spring Security
- Language: Java
- Perspective: CSRF
- Concept: CSRF disabled for browser session
- Symptom: State-changing browser requests lack forgery protection.
- Diagnostic goal: Keep CSRF for cookie-authenticated browser flows.

### Buggy code

```java
http.csrf(csrf -> csrf.disable());
```

### Expected diagnosis

Disabling CSRF globally is unsafe when authentication is carried by cookies.

### Corrected code

```java
http.csrf(Customizer.withDefaults());
```

### Regression tests

```java
// A missing token is rejected for a session-authenticated POST.
```

## SEC-H-013: plain text password

- Difficulty: Hard
- Framework: Spring Security
- Language: Java
- Perspective: Password storage
- Concept: plain text password
- Symptom: A database leak exposes credentials immediately.
- Diagnostic goal: Store adaptive password hashes and compare through the encoder.

### Buggy code

```java
user.setPassword(rawPassword);
```

### Expected diagnosis

Raw passwords are reversible by anyone who obtains the database.

### Corrected code

```java
user.setPassword(passwordEncoder.encode(rawPassword));
```

### Regression tests

```java
// Login matches through passwordEncoder.matches and never compares raw storage.
```

## SEC-H-014: annotation ignored

- Difficulty: Hard
- Framework: Spring Security
- Language: Java
- Perspective: Method security
- Concept: annotation ignored
- Symptom: A role annotation has no effect.
- Diagnostic goal: Enable method security and use the correct authority prefix.

### Buggy code

```java
@PreAuthorize("hasRole("ADMIN")")
public void delete() {}
```

### Expected diagnosis

Method annotations are inactive unless method security is enabled.

### Corrected code

```java
@EnableMethodSecurity
@Configuration
class SecurityConfig {}
```

### Regression tests

```java
// Nonadmins are denied when invoking the method directly through the proxy.
```

## SEC-H-015: signature not checked

- Difficulty: Hard
- Framework: Spring Security
- Language: Java
- Perspective: JWT validation
- Concept: signature not checked
- Symptom: Forged claims authorize a request.
- Diagnostic goal: Verify signature, issuer, audience, and expiry.

### Buggy code

```java
JwtClaims claims = parser.parseUnsecured(token);
```

### Expected diagnosis

Reading claims without verification is equivalent to trusting user input.

### Corrected code

```java
JwtClaims claims = parser.verify(token, key).requireIssuer(issuer).requireAudience(audience).parse();
```

### Regression tests

```java
// Forged, expired, wrong-issuer tokens are rejected.
```

## SEC-H-016: authentication mistaken for authorization

- Difficulty: Hard
- Framework: Spring Security
- Language: Java
- Perspective: Authorization
- Concept: authentication mistaken for authorization
- Symptom: Every signed-in user can perform an admin action.
- Diagnostic goal: Require a permission or role for the operation.

### Buggy code

```java
.anyRequest().authenticated()
```

### Expected diagnosis

Authenticated only proves identity; it does not grant the admin capability.

### Corrected code

```java
.requestMatchers("/admin/**").hasAuthority("admin:write")
```

### Regression tests

```java
// A user without admin:write receives 403.
```

## SEC-H-017: session fixation risk

- Difficulty: Hard
- Framework: Spring Security
- Language: Java
- Perspective: Session policy
- Concept: session fixation risk
- Symptom: The session identifier remains attacker-controlled after login.
- Diagnostic goal: Apply a session fixation protection policy.

### Buggy code

```java
http.sessionManagement(s -> s.sessionFixation(f -> f.none()));
```

### Expected diagnosis

Keeping the pre-login session identifier permits fixation attacks.

### Corrected code

```java
http.sessionManagement(s -> s.sessionFixation(f -> f.changeSessionId()));
```

### Regression tests

```java
// Successful login changes or invalidates the pre-authentication id.
```

## SEC-H-018: security CORS differs from MVC CORS

- Difficulty: Hard
- Framework: Spring Security
- Language: Java
- Perspective: CORS
- Concept: security CORS differs from MVC CORS
- Symptom: Preflight requests are rejected before the controller.
- Diagnostic goal: Configure CORS in the security filter chain with the application policy.

### Buggy code

```java
http.cors(c -> c.disable());
```

### Expected diagnosis

The security chain can reject preflight before MVC configuration is reached.

### Corrected code

```java
http.cors(Customizer.withDefaults());
```

### Regression tests

```java
// OPTIONS preflight receives the configured allow origin and methods.
```

## SEC-H-019: logout endpoint accepts GET

- Difficulty: Hard
- Framework: Spring Security
- Language: Java
- Perspective: Logout
- Concept: logout endpoint accepts GET
- Symptom: A cross-site link can log users out unexpectedly.
- Diagnostic goal: Use POST and CSRF protection for browser logout.

### Buggy code

```java
http.logout(l -> l.logoutRequestMatcher(new AntPathRequestMatcher("/logout", "GET")));
```

### Expected diagnosis

GET should be safe and cannot carry a CSRF-protected state change reliably.

### Corrected code

```java
http.logout(l -> l.logoutUrl("/logout"));
```

### Regression tests

```java
// GET does not log out; CSRF-protected POST does.
```

## SEC-H-020: test user missing authority

- Difficulty: Hard
- Framework: Spring Security
- Language: Java
- Perspective: Testing security
- Concept: test user missing authority
- Symptom: A controller test fails before the business assertion.
- Diagnostic goal: Make the test authentication match the endpoint contract.

### Buggy code

```java
@WebMvcTest
void deletes() { mockMvc.perform(delete("/items/1")); }
```

### Expected diagnosis

The request is anonymous and security correctly denies it.

### Corrected code

```java
@WithMockUser(roles = "ADMIN")
void deletes() { mockMvc.perform(delete("/items/1").with(csrf())); }
```

### Regression tests

```java
// The test supplies both role and CSRF token.
```

## SEC-H-021: permitAll on protected path

- Difficulty: Hard
- Framework: Spring Security
- Language: Java
- Perspective: Filter chain
- Concept: permitAll on protected path
- Symptom: Unauthenticated users access an admin endpoint.
- Diagnostic goal: Order matchers from specific protected paths to general rules.

### Buggy code

```java
authorize.requestMatchers("/**").permitAll()
       .requestMatchers("/admin/**").hasRole("ADMIN")
```

### Expected diagnosis

The catch-all matcher matches first, so the admin rule is unreachable.

### Corrected code

```java
authorize.requestMatchers("/admin/**").hasRole("ADMIN")
       .anyRequest().authenticated()
```

### Regression tests

```java
// Anonymous admin access is 401/403; authenticated users follow role rules.
```

## SEC-H-022: CSRF disabled for browser session

- Difficulty: Hard
- Framework: Spring Security
- Language: Java
- Perspective: CSRF
- Concept: CSRF disabled for browser session
- Symptom: State-changing browser requests lack forgery protection.
- Diagnostic goal: Keep CSRF for cookie-authenticated browser flows.

### Buggy code

```java
http.csrf(csrf -> csrf.disable());
```

### Expected diagnosis

Disabling CSRF globally is unsafe when authentication is carried by cookies.

### Corrected code

```java
http.csrf(Customizer.withDefaults());
```

### Regression tests

```java
// A missing token is rejected for a session-authenticated POST.
```

## SEC-H-023: plain text password

- Difficulty: Hard
- Framework: Spring Security
- Language: Java
- Perspective: Password storage
- Concept: plain text password
- Symptom: A database leak exposes credentials immediately.
- Diagnostic goal: Store adaptive password hashes and compare through the encoder.

### Buggy code

```java
user.setPassword(rawPassword);
```

### Expected diagnosis

Raw passwords are reversible by anyone who obtains the database.

### Corrected code

```java
user.setPassword(passwordEncoder.encode(rawPassword));
```

### Regression tests

```java
// Login matches through passwordEncoder.matches and never compares raw storage.
```

## SEC-H-024: annotation ignored

- Difficulty: Hard
- Framework: Spring Security
- Language: Java
- Perspective: Method security
- Concept: annotation ignored
- Symptom: A role annotation has no effect.
- Diagnostic goal: Enable method security and use the correct authority prefix.

### Buggy code

```java
@PreAuthorize("hasRole("ADMIN")")
public void delete() {}
```

### Expected diagnosis

Method annotations are inactive unless method security is enabled.

### Corrected code

```java
@EnableMethodSecurity
@Configuration
class SecurityConfig {}
```

### Regression tests

```java
// Nonadmins are denied when invoking the method directly through the proxy.
```

## SEC-H-025: signature not checked

- Difficulty: Hard
- Framework: Spring Security
- Language: Java
- Perspective: JWT validation
- Concept: signature not checked
- Symptom: Forged claims authorize a request.
- Diagnostic goal: Verify signature, issuer, audience, and expiry.

### Buggy code

```java
JwtClaims claims = parser.parseUnsecured(token);
```

### Expected diagnosis

Reading claims without verification is equivalent to trusting user input.

### Corrected code

```java
JwtClaims claims = parser.verify(token, key).requireIssuer(issuer).requireAudience(audience).parse();
```

### Regression tests

```java
// Forged, expired, wrong-issuer tokens are rejected.
```

## SEC-H-026: authentication mistaken for authorization

- Difficulty: Hard
- Framework: Spring Security
- Language: Java
- Perspective: Authorization
- Concept: authentication mistaken for authorization
- Symptom: Every signed-in user can perform an admin action.
- Diagnostic goal: Require a permission or role for the operation.

### Buggy code

```java
.anyRequest().authenticated()
```

### Expected diagnosis

Authenticated only proves identity; it does not grant the admin capability.

### Corrected code

```java
.requestMatchers("/admin/**").hasAuthority("admin:write")
```

### Regression tests

```java
// A user without admin:write receives 403.
```

## SEC-H-027: session fixation risk

- Difficulty: Hard
- Framework: Spring Security
- Language: Java
- Perspective: Session policy
- Concept: session fixation risk
- Symptom: The session identifier remains attacker-controlled after login.
- Diagnostic goal: Apply a session fixation protection policy.

### Buggy code

```java
http.sessionManagement(s -> s.sessionFixation(f -> f.none()));
```

### Expected diagnosis

Keeping the pre-login session identifier permits fixation attacks.

### Corrected code

```java
http.sessionManagement(s -> s.sessionFixation(f -> f.changeSessionId()));
```

### Regression tests

```java
// Successful login changes or invalidates the pre-authentication id.
```

## SEC-H-028: security CORS differs from MVC CORS

- Difficulty: Hard
- Framework: Spring Security
- Language: Java
- Perspective: CORS
- Concept: security CORS differs from MVC CORS
- Symptom: Preflight requests are rejected before the controller.
- Diagnostic goal: Configure CORS in the security filter chain with the application policy.

### Buggy code

```java
http.cors(c -> c.disable());
```

### Expected diagnosis

The security chain can reject preflight before MVC configuration is reached.

### Corrected code

```java
http.cors(Customizer.withDefaults());
```

### Regression tests

```java
// OPTIONS preflight receives the configured allow origin and methods.
```

## SEC-H-029: logout endpoint accepts GET

- Difficulty: Hard
- Framework: Spring Security
- Language: Java
- Perspective: Logout
- Concept: logout endpoint accepts GET
- Symptom: A cross-site link can log users out unexpectedly.
- Diagnostic goal: Use POST and CSRF protection for browser logout.

### Buggy code

```java
http.logout(l -> l.logoutRequestMatcher(new AntPathRequestMatcher("/logout", "GET")));
```

### Expected diagnosis

GET should be safe and cannot carry a CSRF-protected state change reliably.

### Corrected code

```java
http.logout(l -> l.logoutUrl("/logout"));
```

### Regression tests

```java
// GET does not log out; CSRF-protected POST does.
```

## SEC-H-030: test user missing authority

- Difficulty: Hard
- Framework: Spring Security
- Language: Java
- Perspective: Testing security
- Concept: test user missing authority
- Symptom: A controller test fails before the business assertion.
- Diagnostic goal: Make the test authentication match the endpoint contract.

### Buggy code

```java
@WebMvcTest
void deletes() { mockMvc.perform(delete("/items/1")); }
```

### Expected diagnosis

The request is anonymous and security correctly denies it.

### Corrected code

```java
@WithMockUser(roles = "ADMIN")
void deletes() { mockMvc.perform(delete("/items/1").with(csrf())); }
```

### Regression tests

```java
// The test supplies both role and CSRF token.
```

## SEC-H-031: permitAll on protected path

- Difficulty: Hard
- Framework: Spring Security
- Language: Java
- Perspective: Filter chain
- Concept: permitAll on protected path
- Symptom: Unauthenticated users access an admin endpoint.
- Diagnostic goal: Order matchers from specific protected paths to general rules.

### Buggy code

```java
authorize.requestMatchers("/**").permitAll()
       .requestMatchers("/admin/**").hasRole("ADMIN")
```

### Expected diagnosis

The catch-all matcher matches first, so the admin rule is unreachable.

### Corrected code

```java
authorize.requestMatchers("/admin/**").hasRole("ADMIN")
       .anyRequest().authenticated()
```

### Regression tests

```java
// Anonymous admin access is 401/403; authenticated users follow role rules.
```

## SEC-H-032: CSRF disabled for browser session

- Difficulty: Hard
- Framework: Spring Security
- Language: Java
- Perspective: CSRF
- Concept: CSRF disabled for browser session
- Symptom: State-changing browser requests lack forgery protection.
- Diagnostic goal: Keep CSRF for cookie-authenticated browser flows.

### Buggy code

```java
http.csrf(csrf -> csrf.disable());
```

### Expected diagnosis

Disabling CSRF globally is unsafe when authentication is carried by cookies.

### Corrected code

```java
http.csrf(Customizer.withDefaults());
```

### Regression tests

```java
// A missing token is rejected for a session-authenticated POST.
```

## SEC-H-033: plain text password

- Difficulty: Hard
- Framework: Spring Security
- Language: Java
- Perspective: Password storage
- Concept: plain text password
- Symptom: A database leak exposes credentials immediately.
- Diagnostic goal: Store adaptive password hashes and compare through the encoder.

### Buggy code

```java
user.setPassword(rawPassword);
```

### Expected diagnosis

Raw passwords are reversible by anyone who obtains the database.

### Corrected code

```java
user.setPassword(passwordEncoder.encode(rawPassword));
```

### Regression tests

```java
// Login matches through passwordEncoder.matches and never compares raw storage.
```

## SEC-H-034: annotation ignored

- Difficulty: Hard
- Framework: Spring Security
- Language: Java
- Perspective: Method security
- Concept: annotation ignored
- Symptom: A role annotation has no effect.
- Diagnostic goal: Enable method security and use the correct authority prefix.

### Buggy code

```java
@PreAuthorize("hasRole("ADMIN")")
public void delete() {}
```

### Expected diagnosis

Method annotations are inactive unless method security is enabled.

### Corrected code

```java
@EnableMethodSecurity
@Configuration
class SecurityConfig {}
```

### Regression tests

```java
// Nonadmins are denied when invoking the method directly through the proxy.
```

## SEC-H-035: signature not checked

- Difficulty: Hard
- Framework: Spring Security
- Language: Java
- Perspective: JWT validation
- Concept: signature not checked
- Symptom: Forged claims authorize a request.
- Diagnostic goal: Verify signature, issuer, audience, and expiry.

### Buggy code

```java
JwtClaims claims = parser.parseUnsecured(token);
```

### Expected diagnosis

Reading claims without verification is equivalent to trusting user input.

### Corrected code

```java
JwtClaims claims = parser.verify(token, key).requireIssuer(issuer).requireAudience(audience).parse();
```

### Regression tests

```java
// Forged, expired, wrong-issuer tokens are rejected.
```

## SEC-H-036: authentication mistaken for authorization

- Difficulty: Hard
- Framework: Spring Security
- Language: Java
- Perspective: Authorization
- Concept: authentication mistaken for authorization
- Symptom: Every signed-in user can perform an admin action.
- Diagnostic goal: Require a permission or role for the operation.

### Buggy code

```java
.anyRequest().authenticated()
```

### Expected diagnosis

Authenticated only proves identity; it does not grant the admin capability.

### Corrected code

```java
.requestMatchers("/admin/**").hasAuthority("admin:write")
```

### Regression tests

```java
// A user without admin:write receives 403.
```

## SEC-H-037: session fixation risk

- Difficulty: Hard
- Framework: Spring Security
- Language: Java
- Perspective: Session policy
- Concept: session fixation risk
- Symptom: The session identifier remains attacker-controlled after login.
- Diagnostic goal: Apply a session fixation protection policy.

### Buggy code

```java
http.sessionManagement(s -> s.sessionFixation(f -> f.none()));
```

### Expected diagnosis

Keeping the pre-login session identifier permits fixation attacks.

### Corrected code

```java
http.sessionManagement(s -> s.sessionFixation(f -> f.changeSessionId()));
```

### Regression tests

```java
// Successful login changes or invalidates the pre-authentication id.
```

## SEC-H-038: security CORS differs from MVC CORS

- Difficulty: Hard
- Framework: Spring Security
- Language: Java
- Perspective: CORS
- Concept: security CORS differs from MVC CORS
- Symptom: Preflight requests are rejected before the controller.
- Diagnostic goal: Configure CORS in the security filter chain with the application policy.

### Buggy code

```java
http.cors(c -> c.disable());
```

### Expected diagnosis

The security chain can reject preflight before MVC configuration is reached.

### Corrected code

```java
http.cors(Customizer.withDefaults());
```

### Regression tests

```java
// OPTIONS preflight receives the configured allow origin and methods.
```

## SEC-H-039: logout endpoint accepts GET

- Difficulty: Hard
- Framework: Spring Security
- Language: Java
- Perspective: Logout
- Concept: logout endpoint accepts GET
- Symptom: A cross-site link can log users out unexpectedly.
- Diagnostic goal: Use POST and CSRF protection for browser logout.

### Buggy code

```java
http.logout(l -> l.logoutRequestMatcher(new AntPathRequestMatcher("/logout", "GET")));
```

### Expected diagnosis

GET should be safe and cannot carry a CSRF-protected state change reliably.

### Corrected code

```java
http.logout(l -> l.logoutUrl("/logout"));
```

### Regression tests

```java
// GET does not log out; CSRF-protected POST does.
```

## SEC-H-040: test user missing authority

- Difficulty: Hard
- Framework: Spring Security
- Language: Java
- Perspective: Testing security
- Concept: test user missing authority
- Symptom: A controller test fails before the business assertion.
- Diagnostic goal: Make the test authentication match the endpoint contract.

### Buggy code

```java
@WebMvcTest
void deletes() { mockMvc.perform(delete("/items/1")); }
```

### Expected diagnosis

The request is anonymous and security correctly denies it.

### Corrected code

```java
@WithMockUser(roles = "ADMIN")
void deletes() { mockMvc.perform(delete("/items/1").with(csrf())); }
```

### Regression tests

```java
// The test supplies both role and CSRF token.
```

## SEC-H-041: permitAll on protected path

- Difficulty: Hard
- Framework: Spring Security
- Language: Java
- Perspective: Filter chain
- Concept: permitAll on protected path
- Symptom: Unauthenticated users access an admin endpoint.
- Diagnostic goal: Order matchers from specific protected paths to general rules.

### Buggy code

```java
authorize.requestMatchers("/**").permitAll()
       .requestMatchers("/admin/**").hasRole("ADMIN")
```

### Expected diagnosis

The catch-all matcher matches first, so the admin rule is unreachable.

### Corrected code

```java
authorize.requestMatchers("/admin/**").hasRole("ADMIN")
       .anyRequest().authenticated()
```

### Regression tests

```java
// Anonymous admin access is 401/403; authenticated users follow role rules.
```

## SEC-H-042: CSRF disabled for browser session

- Difficulty: Hard
- Framework: Spring Security
- Language: Java
- Perspective: CSRF
- Concept: CSRF disabled for browser session
- Symptom: State-changing browser requests lack forgery protection.
- Diagnostic goal: Keep CSRF for cookie-authenticated browser flows.

### Buggy code

```java
http.csrf(csrf -> csrf.disable());
```

### Expected diagnosis

Disabling CSRF globally is unsafe when authentication is carried by cookies.

### Corrected code

```java
http.csrf(Customizer.withDefaults());
```

### Regression tests

```java
// A missing token is rejected for a session-authenticated POST.
```

## SEC-H-043: plain text password

- Difficulty: Hard
- Framework: Spring Security
- Language: Java
- Perspective: Password storage
- Concept: plain text password
- Symptom: A database leak exposes credentials immediately.
- Diagnostic goal: Store adaptive password hashes and compare through the encoder.

### Buggy code

```java
user.setPassword(rawPassword);
```

### Expected diagnosis

Raw passwords are reversible by anyone who obtains the database.

### Corrected code

```java
user.setPassword(passwordEncoder.encode(rawPassword));
```

### Regression tests

```java
// Login matches through passwordEncoder.matches and never compares raw storage.
```

## SEC-H-044: annotation ignored

- Difficulty: Hard
- Framework: Spring Security
- Language: Java
- Perspective: Method security
- Concept: annotation ignored
- Symptom: A role annotation has no effect.
- Diagnostic goal: Enable method security and use the correct authority prefix.

### Buggy code

```java
@PreAuthorize("hasRole("ADMIN")")
public void delete() {}
```

### Expected diagnosis

Method annotations are inactive unless method security is enabled.

### Corrected code

```java
@EnableMethodSecurity
@Configuration
class SecurityConfig {}
```

### Regression tests

```java
// Nonadmins are denied when invoking the method directly through the proxy.
```

## SEC-H-045: signature not checked

- Difficulty: Hard
- Framework: Spring Security
- Language: Java
- Perspective: JWT validation
- Concept: signature not checked
- Symptom: Forged claims authorize a request.
- Diagnostic goal: Verify signature, issuer, audience, and expiry.

### Buggy code

```java
JwtClaims claims = parser.parseUnsecured(token);
```

### Expected diagnosis

Reading claims without verification is equivalent to trusting user input.

### Corrected code

```java
JwtClaims claims = parser.verify(token, key).requireIssuer(issuer).requireAudience(audience).parse();
```

### Regression tests

```java
// Forged, expired, wrong-issuer tokens are rejected.
```

## SEC-H-046: authentication mistaken for authorization

- Difficulty: Hard
- Framework: Spring Security
- Language: Java
- Perspective: Authorization
- Concept: authentication mistaken for authorization
- Symptom: Every signed-in user can perform an admin action.
- Diagnostic goal: Require a permission or role for the operation.

### Buggy code

```java
.anyRequest().authenticated()
```

### Expected diagnosis

Authenticated only proves identity; it does not grant the admin capability.

### Corrected code

```java
.requestMatchers("/admin/**").hasAuthority("admin:write")
```

### Regression tests

```java
// A user without admin:write receives 403.
```

## SEC-H-047: session fixation risk

- Difficulty: Hard
- Framework: Spring Security
- Language: Java
- Perspective: Session policy
- Concept: session fixation risk
- Symptom: The session identifier remains attacker-controlled after login.
- Diagnostic goal: Apply a session fixation protection policy.

### Buggy code

```java
http.sessionManagement(s -> s.sessionFixation(f -> f.none()));
```

### Expected diagnosis

Keeping the pre-login session identifier permits fixation attacks.

### Corrected code

```java
http.sessionManagement(s -> s.sessionFixation(f -> f.changeSessionId()));
```

### Regression tests

```java
// Successful login changes or invalidates the pre-authentication id.
```

## SEC-H-048: security CORS differs from MVC CORS

- Difficulty: Hard
- Framework: Spring Security
- Language: Java
- Perspective: CORS
- Concept: security CORS differs from MVC CORS
- Symptom: Preflight requests are rejected before the controller.
- Diagnostic goal: Configure CORS in the security filter chain with the application policy.

### Buggy code

```java
http.cors(c -> c.disable());
```

### Expected diagnosis

The security chain can reject preflight before MVC configuration is reached.

### Corrected code

```java
http.cors(Customizer.withDefaults());
```

### Regression tests

```java
// OPTIONS preflight receives the configured allow origin and methods.
```

## SEC-H-049: logout endpoint accepts GET

- Difficulty: Hard
- Framework: Spring Security
- Language: Java
- Perspective: Logout
- Concept: logout endpoint accepts GET
- Symptom: A cross-site link can log users out unexpectedly.
- Diagnostic goal: Use POST and CSRF protection for browser logout.

### Buggy code

```java
http.logout(l -> l.logoutRequestMatcher(new AntPathRequestMatcher("/logout", "GET")));
```

### Expected diagnosis

GET should be safe and cannot carry a CSRF-protected state change reliably.

### Corrected code

```java
http.logout(l -> l.logoutUrl("/logout"));
```

### Regression tests

```java
// GET does not log out; CSRF-protected POST does.
```

## SEC-H-050: test user missing authority

- Difficulty: Hard
- Framework: Spring Security
- Language: Java
- Perspective: Testing security
- Concept: test user missing authority
- Symptom: A controller test fails before the business assertion.
- Diagnostic goal: Make the test authentication match the endpoint contract.

### Buggy code

```java
@WebMvcTest
void deletes() { mockMvc.perform(delete("/items/1")); }
```

### Expected diagnosis

The request is anonymous and security correctly denies it.

### Corrected code

```java
@WithMockUser(roles = "ADMIN")
void deletes() { mockMvc.perform(delete("/items/1").with(csrf())); }
```

### Regression tests

```java
// The test supplies both role and CSRF token.
```

## SEC-H-051: permitAll on protected path

- Difficulty: Hard
- Framework: Spring Security
- Language: Java
- Perspective: Filter chain
- Concept: permitAll on protected path
- Symptom: Unauthenticated users access an admin endpoint.
- Diagnostic goal: Order matchers from specific protected paths to general rules.

### Buggy code

```java
authorize.requestMatchers("/**").permitAll()
       .requestMatchers("/admin/**").hasRole("ADMIN")
```

### Expected diagnosis

The catch-all matcher matches first, so the admin rule is unreachable.

### Corrected code

```java
authorize.requestMatchers("/admin/**").hasRole("ADMIN")
       .anyRequest().authenticated()
```

### Regression tests

```java
// Anonymous admin access is 401/403; authenticated users follow role rules.
```

## SEC-H-052: CSRF disabled for browser session

- Difficulty: Hard
- Framework: Spring Security
- Language: Java
- Perspective: CSRF
- Concept: CSRF disabled for browser session
- Symptom: State-changing browser requests lack forgery protection.
- Diagnostic goal: Keep CSRF for cookie-authenticated browser flows.

### Buggy code

```java
http.csrf(csrf -> csrf.disable());
```

### Expected diagnosis

Disabling CSRF globally is unsafe when authentication is carried by cookies.

### Corrected code

```java
http.csrf(Customizer.withDefaults());
```

### Regression tests

```java
// A missing token is rejected for a session-authenticated POST.
```

## SEC-H-053: plain text password

- Difficulty: Hard
- Framework: Spring Security
- Language: Java
- Perspective: Password storage
- Concept: plain text password
- Symptom: A database leak exposes credentials immediately.
- Diagnostic goal: Store adaptive password hashes and compare through the encoder.

### Buggy code

```java
user.setPassword(rawPassword);
```

### Expected diagnosis

Raw passwords are reversible by anyone who obtains the database.

### Corrected code

```java
user.setPassword(passwordEncoder.encode(rawPassword));
```

### Regression tests

```java
// Login matches through passwordEncoder.matches and never compares raw storage.
```

## SEC-H-054: annotation ignored

- Difficulty: Hard
- Framework: Spring Security
- Language: Java
- Perspective: Method security
- Concept: annotation ignored
- Symptom: A role annotation has no effect.
- Diagnostic goal: Enable method security and use the correct authority prefix.

### Buggy code

```java
@PreAuthorize("hasRole("ADMIN")")
public void delete() {}
```

### Expected diagnosis

Method annotations are inactive unless method security is enabled.

### Corrected code

```java
@EnableMethodSecurity
@Configuration
class SecurityConfig {}
```

### Regression tests

```java
// Nonadmins are denied when invoking the method directly through the proxy.
```

## SEC-H-055: signature not checked

- Difficulty: Hard
- Framework: Spring Security
- Language: Java
- Perspective: JWT validation
- Concept: signature not checked
- Symptom: Forged claims authorize a request.
- Diagnostic goal: Verify signature, issuer, audience, and expiry.

### Buggy code

```java
JwtClaims claims = parser.parseUnsecured(token);
```

### Expected diagnosis

Reading claims without verification is equivalent to trusting user input.

### Corrected code

```java
JwtClaims claims = parser.verify(token, key).requireIssuer(issuer).requireAudience(audience).parse();
```

### Regression tests

```java
// Forged, expired, wrong-issuer tokens are rejected.
```

## SEC-H-056: authentication mistaken for authorization

- Difficulty: Hard
- Framework: Spring Security
- Language: Java
- Perspective: Authorization
- Concept: authentication mistaken for authorization
- Symptom: Every signed-in user can perform an admin action.
- Diagnostic goal: Require a permission or role for the operation.

### Buggy code

```java
.anyRequest().authenticated()
```

### Expected diagnosis

Authenticated only proves identity; it does not grant the admin capability.

### Corrected code

```java
.requestMatchers("/admin/**").hasAuthority("admin:write")
```

### Regression tests

```java
// A user without admin:write receives 403.
```

## SEC-H-057: session fixation risk

- Difficulty: Hard
- Framework: Spring Security
- Language: Java
- Perspective: Session policy
- Concept: session fixation risk
- Symptom: The session identifier remains attacker-controlled after login.
- Diagnostic goal: Apply a session fixation protection policy.

### Buggy code

```java
http.sessionManagement(s -> s.sessionFixation(f -> f.none()));
```

### Expected diagnosis

Keeping the pre-login session identifier permits fixation attacks.

### Corrected code

```java
http.sessionManagement(s -> s.sessionFixation(f -> f.changeSessionId()));
```

### Regression tests

```java
// Successful login changes or invalidates the pre-authentication id.
```

## SEC-H-058: security CORS differs from MVC CORS

- Difficulty: Hard
- Framework: Spring Security
- Language: Java
- Perspective: CORS
- Concept: security CORS differs from MVC CORS
- Symptom: Preflight requests are rejected before the controller.
- Diagnostic goal: Configure CORS in the security filter chain with the application policy.

### Buggy code

```java
http.cors(c -> c.disable());
```

### Expected diagnosis

The security chain can reject preflight before MVC configuration is reached.

### Corrected code

```java
http.cors(Customizer.withDefaults());
```

### Regression tests

```java
// OPTIONS preflight receives the configured allow origin and methods.
```

## SEC-H-059: logout endpoint accepts GET

- Difficulty: Hard
- Framework: Spring Security
- Language: Java
- Perspective: Logout
- Concept: logout endpoint accepts GET
- Symptom: A cross-site link can log users out unexpectedly.
- Diagnostic goal: Use POST and CSRF protection for browser logout.

### Buggy code

```java
http.logout(l -> l.logoutRequestMatcher(new AntPathRequestMatcher("/logout", "GET")));
```

### Expected diagnosis

GET should be safe and cannot carry a CSRF-protected state change reliably.

### Corrected code

```java
http.logout(l -> l.logoutUrl("/logout"));
```

### Regression tests

```java
// GET does not log out; CSRF-protected POST does.
```

## SEC-H-060: test user missing authority

- Difficulty: Hard
- Framework: Spring Security
- Language: Java
- Perspective: Testing security
- Concept: test user missing authority
- Symptom: A controller test fails before the business assertion.
- Diagnostic goal: Make the test authentication match the endpoint contract.

### Buggy code

```java
@WebMvcTest
void deletes() { mockMvc.perform(delete("/items/1")); }
```

### Expected diagnosis

The request is anonymous and security correctly denies it.

### Corrected code

```java
@WithMockUser(roles = "ADMIN")
void deletes() { mockMvc.perform(delete("/items/1").with(csrf())); }
```

### Regression tests

```java
// The test supplies both role and CSRF token.
```

## SEC-H-061: permitAll on protected path

- Difficulty: Hard
- Framework: Spring Security
- Language: Java
- Perspective: Filter chain
- Concept: permitAll on protected path
- Symptom: Unauthenticated users access an admin endpoint.
- Diagnostic goal: Order matchers from specific protected paths to general rules.

### Buggy code

```java
authorize.requestMatchers("/**").permitAll()
       .requestMatchers("/admin/**").hasRole("ADMIN")
```

### Expected diagnosis

The catch-all matcher matches first, so the admin rule is unreachable.

### Corrected code

```java
authorize.requestMatchers("/admin/**").hasRole("ADMIN")
       .anyRequest().authenticated()
```

### Regression tests

```java
// Anonymous admin access is 401/403; authenticated users follow role rules.
```

## SEC-H-062: CSRF disabled for browser session

- Difficulty: Hard
- Framework: Spring Security
- Language: Java
- Perspective: CSRF
- Concept: CSRF disabled for browser session
- Symptom: State-changing browser requests lack forgery protection.
- Diagnostic goal: Keep CSRF for cookie-authenticated browser flows.

### Buggy code

```java
http.csrf(csrf -> csrf.disable());
```

### Expected diagnosis

Disabling CSRF globally is unsafe when authentication is carried by cookies.

### Corrected code

```java
http.csrf(Customizer.withDefaults());
```

### Regression tests

```java
// A missing token is rejected for a session-authenticated POST.
```

## SEC-H-063: plain text password

- Difficulty: Hard
- Framework: Spring Security
- Language: Java
- Perspective: Password storage
- Concept: plain text password
- Symptom: A database leak exposes credentials immediately.
- Diagnostic goal: Store adaptive password hashes and compare through the encoder.

### Buggy code

```java
user.setPassword(rawPassword);
```

### Expected diagnosis

Raw passwords are reversible by anyone who obtains the database.

### Corrected code

```java
user.setPassword(passwordEncoder.encode(rawPassword));
```

### Regression tests

```java
// Login matches through passwordEncoder.matches and never compares raw storage.
```

## SEC-H-064: annotation ignored

- Difficulty: Hard
- Framework: Spring Security
- Language: Java
- Perspective: Method security
- Concept: annotation ignored
- Symptom: A role annotation has no effect.
- Diagnostic goal: Enable method security and use the correct authority prefix.

### Buggy code

```java
@PreAuthorize("hasRole("ADMIN")")
public void delete() {}
```

### Expected diagnosis

Method annotations are inactive unless method security is enabled.

### Corrected code

```java
@EnableMethodSecurity
@Configuration
class SecurityConfig {}
```

### Regression tests

```java
// Nonadmins are denied when invoking the method directly through the proxy.
```

## SEC-H-065: signature not checked

- Difficulty: Hard
- Framework: Spring Security
- Language: Java
- Perspective: JWT validation
- Concept: signature not checked
- Symptom: Forged claims authorize a request.
- Diagnostic goal: Verify signature, issuer, audience, and expiry.

### Buggy code

```java
JwtClaims claims = parser.parseUnsecured(token);
```

### Expected diagnosis

Reading claims without verification is equivalent to trusting user input.

### Corrected code

```java
JwtClaims claims = parser.verify(token, key).requireIssuer(issuer).requireAudience(audience).parse();
```

### Regression tests

```java
// Forged, expired, wrong-issuer tokens are rejected.
```

## SEC-H-066: authentication mistaken for authorization

- Difficulty: Hard
- Framework: Spring Security
- Language: Java
- Perspective: Authorization
- Concept: authentication mistaken for authorization
- Symptom: Every signed-in user can perform an admin action.
- Diagnostic goal: Require a permission or role for the operation.

### Buggy code

```java
.anyRequest().authenticated()
```

### Expected diagnosis

Authenticated only proves identity; it does not grant the admin capability.

### Corrected code

```java
.requestMatchers("/admin/**").hasAuthority("admin:write")
```

### Regression tests

```java
// A user without admin:write receives 403.
```

## SEC-H-067: session fixation risk

- Difficulty: Hard
- Framework: Spring Security
- Language: Java
- Perspective: Session policy
- Concept: session fixation risk
- Symptom: The session identifier remains attacker-controlled after login.
- Diagnostic goal: Apply a session fixation protection policy.

### Buggy code

```java
http.sessionManagement(s -> s.sessionFixation(f -> f.none()));
```

### Expected diagnosis

Keeping the pre-login session identifier permits fixation attacks.

### Corrected code

```java
http.sessionManagement(s -> s.sessionFixation(f -> f.changeSessionId()));
```

### Regression tests

```java
// Successful login changes or invalidates the pre-authentication id.
```

## SEC-H-068: security CORS differs from MVC CORS

- Difficulty: Hard
- Framework: Spring Security
- Language: Java
- Perspective: CORS
- Concept: security CORS differs from MVC CORS
- Symptom: Preflight requests are rejected before the controller.
- Diagnostic goal: Configure CORS in the security filter chain with the application policy.

### Buggy code

```java
http.cors(c -> c.disable());
```

### Expected diagnosis

The security chain can reject preflight before MVC configuration is reached.

### Corrected code

```java
http.cors(Customizer.withDefaults());
```

### Regression tests

```java
// OPTIONS preflight receives the configured allow origin and methods.
```

## SEC-H-069: logout endpoint accepts GET

- Difficulty: Hard
- Framework: Spring Security
- Language: Java
- Perspective: Logout
- Concept: logout endpoint accepts GET
- Symptom: A cross-site link can log users out unexpectedly.
- Diagnostic goal: Use POST and CSRF protection for browser logout.

### Buggy code

```java
http.logout(l -> l.logoutRequestMatcher(new AntPathRequestMatcher("/logout", "GET")));
```

### Expected diagnosis

GET should be safe and cannot carry a CSRF-protected state change reliably.

### Corrected code

```java
http.logout(l -> l.logoutUrl("/logout"));
```

### Regression tests

```java
// GET does not log out; CSRF-protected POST does.
```

## SEC-H-070: test user missing authority

- Difficulty: Hard
- Framework: Spring Security
- Language: Java
- Perspective: Testing security
- Concept: test user missing authority
- Symptom: A controller test fails before the business assertion.
- Diagnostic goal: Make the test authentication match the endpoint contract.

### Buggy code

```java
@WebMvcTest
void deletes() { mockMvc.perform(delete("/items/1")); }
```

### Expected diagnosis

The request is anonymous and security correctly denies it.

### Corrected code

```java
@WithMockUser(roles = "ADMIN")
void deletes() { mockMvc.perform(delete("/items/1").with(csrf())); }
```

### Regression tests

```java
// The test supplies both role and CSRF token.
```

## SEC-H-071: permitAll on protected path

- Difficulty: Hard
- Framework: Spring Security
- Language: Java
- Perspective: Filter chain
- Concept: permitAll on protected path
- Symptom: Unauthenticated users access an admin endpoint.
- Diagnostic goal: Order matchers from specific protected paths to general rules.

### Buggy code

```java
authorize.requestMatchers("/**").permitAll()
       .requestMatchers("/admin/**").hasRole("ADMIN")
```

### Expected diagnosis

The catch-all matcher matches first, so the admin rule is unreachable.

### Corrected code

```java
authorize.requestMatchers("/admin/**").hasRole("ADMIN")
       .anyRequest().authenticated()
```

### Regression tests

```java
// Anonymous admin access is 401/403; authenticated users follow role rules.
```

## SEC-H-072: CSRF disabled for browser session

- Difficulty: Hard
- Framework: Spring Security
- Language: Java
- Perspective: CSRF
- Concept: CSRF disabled for browser session
- Symptom: State-changing browser requests lack forgery protection.
- Diagnostic goal: Keep CSRF for cookie-authenticated browser flows.

### Buggy code

```java
http.csrf(csrf -> csrf.disable());
```

### Expected diagnosis

Disabling CSRF globally is unsafe when authentication is carried by cookies.

### Corrected code

```java
http.csrf(Customizer.withDefaults());
```

### Regression tests

```java
// A missing token is rejected for a session-authenticated POST.
```

## SEC-H-073: plain text password

- Difficulty: Hard
- Framework: Spring Security
- Language: Java
- Perspective: Password storage
- Concept: plain text password
- Symptom: A database leak exposes credentials immediately.
- Diagnostic goal: Store adaptive password hashes and compare through the encoder.

### Buggy code

```java
user.setPassword(rawPassword);
```

### Expected diagnosis

Raw passwords are reversible by anyone who obtains the database.

### Corrected code

```java
user.setPassword(passwordEncoder.encode(rawPassword));
```

### Regression tests

```java
// Login matches through passwordEncoder.matches and never compares raw storage.
```

## SEC-H-074: annotation ignored

- Difficulty: Hard
- Framework: Spring Security
- Language: Java
- Perspective: Method security
- Concept: annotation ignored
- Symptom: A role annotation has no effect.
- Diagnostic goal: Enable method security and use the correct authority prefix.

### Buggy code

```java
@PreAuthorize("hasRole("ADMIN")")
public void delete() {}
```

### Expected diagnosis

Method annotations are inactive unless method security is enabled.

### Corrected code

```java
@EnableMethodSecurity
@Configuration
class SecurityConfig {}
```

### Regression tests

```java
// Nonadmins are denied when invoking the method directly through the proxy.
```

## SEC-H-075: signature not checked

- Difficulty: Hard
- Framework: Spring Security
- Language: Java
- Perspective: JWT validation
- Concept: signature not checked
- Symptom: Forged claims authorize a request.
- Diagnostic goal: Verify signature, issuer, audience, and expiry.

### Buggy code

```java
JwtClaims claims = parser.parseUnsecured(token);
```

### Expected diagnosis

Reading claims without verification is equivalent to trusting user input.

### Corrected code

```java
JwtClaims claims = parser.verify(token, key).requireIssuer(issuer).requireAudience(audience).parse();
```

### Regression tests

```java
// Forged, expired, wrong-issuer tokens are rejected.
```

## SEC-H-076: authentication mistaken for authorization

- Difficulty: Hard
- Framework: Spring Security
- Language: Java
- Perspective: Authorization
- Concept: authentication mistaken for authorization
- Symptom: Every signed-in user can perform an admin action.
- Diagnostic goal: Require a permission or role for the operation.

### Buggy code

```java
.anyRequest().authenticated()
```

### Expected diagnosis

Authenticated only proves identity; it does not grant the admin capability.

### Corrected code

```java
.requestMatchers("/admin/**").hasAuthority("admin:write")
```

### Regression tests

```java
// A user without admin:write receives 403.
```

## SEC-H-077: session fixation risk

- Difficulty: Hard
- Framework: Spring Security
- Language: Java
- Perspective: Session policy
- Concept: session fixation risk
- Symptom: The session identifier remains attacker-controlled after login.
- Diagnostic goal: Apply a session fixation protection policy.

### Buggy code

```java
http.sessionManagement(s -> s.sessionFixation(f -> f.none()));
```

### Expected diagnosis

Keeping the pre-login session identifier permits fixation attacks.

### Corrected code

```java
http.sessionManagement(s -> s.sessionFixation(f -> f.changeSessionId()));
```

### Regression tests

```java
// Successful login changes or invalidates the pre-authentication id.
```

## SEC-H-078: security CORS differs from MVC CORS

- Difficulty: Hard
- Framework: Spring Security
- Language: Java
- Perspective: CORS
- Concept: security CORS differs from MVC CORS
- Symptom: Preflight requests are rejected before the controller.
- Diagnostic goal: Configure CORS in the security filter chain with the application policy.

### Buggy code

```java
http.cors(c -> c.disable());
```

### Expected diagnosis

The security chain can reject preflight before MVC configuration is reached.

### Corrected code

```java
http.cors(Customizer.withDefaults());
```

### Regression tests

```java
// OPTIONS preflight receives the configured allow origin and methods.
```

## SEC-H-079: logout endpoint accepts GET

- Difficulty: Hard
- Framework: Spring Security
- Language: Java
- Perspective: Logout
- Concept: logout endpoint accepts GET
- Symptom: A cross-site link can log users out unexpectedly.
- Diagnostic goal: Use POST and CSRF protection for browser logout.

### Buggy code

```java
http.logout(l -> l.logoutRequestMatcher(new AntPathRequestMatcher("/logout", "GET")));
```

### Expected diagnosis

GET should be safe and cannot carry a CSRF-protected state change reliably.

### Corrected code

```java
http.logout(l -> l.logoutUrl("/logout"));
```

### Regression tests

```java
// GET does not log out; CSRF-protected POST does.
```

## SEC-H-080: test user missing authority

- Difficulty: Hard
- Framework: Spring Security
- Language: Java
- Perspective: Testing security
- Concept: test user missing authority
- Symptom: A controller test fails before the business assertion.
- Diagnostic goal: Make the test authentication match the endpoint contract.

### Buggy code

```java
@WebMvcTest
void deletes() { mockMvc.perform(delete("/items/1")); }
```

### Expected diagnosis

The request is anonymous and security correctly denies it.

### Corrected code

```java
@WithMockUser(roles = "ADMIN")
void deletes() { mockMvc.perform(delete("/items/1").with(csrf())); }
```

### Regression tests

```java
// The test supplies both role and CSRF token.
```

## SEC-H-081: permitAll on protected path

- Difficulty: Hard
- Framework: Spring Security
- Language: Java
- Perspective: Filter chain
- Concept: permitAll on protected path
- Symptom: Unauthenticated users access an admin endpoint.
- Diagnostic goal: Order matchers from specific protected paths to general rules.

### Buggy code

```java
authorize.requestMatchers("/**").permitAll()
       .requestMatchers("/admin/**").hasRole("ADMIN")
```

### Expected diagnosis

The catch-all matcher matches first, so the admin rule is unreachable.

### Corrected code

```java
authorize.requestMatchers("/admin/**").hasRole("ADMIN")
       .anyRequest().authenticated()
```

### Regression tests

```java
// Anonymous admin access is 401/403; authenticated users follow role rules.
```

## SEC-H-082: CSRF disabled for browser session

- Difficulty: Hard
- Framework: Spring Security
- Language: Java
- Perspective: CSRF
- Concept: CSRF disabled for browser session
- Symptom: State-changing browser requests lack forgery protection.
- Diagnostic goal: Keep CSRF for cookie-authenticated browser flows.

### Buggy code

```java
http.csrf(csrf -> csrf.disable());
```

### Expected diagnosis

Disabling CSRF globally is unsafe when authentication is carried by cookies.

### Corrected code

```java
http.csrf(Customizer.withDefaults());
```

### Regression tests

```java
// A missing token is rejected for a session-authenticated POST.
```

## SEC-H-083: plain text password

- Difficulty: Hard
- Framework: Spring Security
- Language: Java
- Perspective: Password storage
- Concept: plain text password
- Symptom: A database leak exposes credentials immediately.
- Diagnostic goal: Store adaptive password hashes and compare through the encoder.

### Buggy code

```java
user.setPassword(rawPassword);
```

### Expected diagnosis

Raw passwords are reversible by anyone who obtains the database.

### Corrected code

```java
user.setPassword(passwordEncoder.encode(rawPassword));
```

### Regression tests

```java
// Login matches through passwordEncoder.matches and never compares raw storage.
```

## SEC-H-084: annotation ignored

- Difficulty: Hard
- Framework: Spring Security
- Language: Java
- Perspective: Method security
- Concept: annotation ignored
- Symptom: A role annotation has no effect.
- Diagnostic goal: Enable method security and use the correct authority prefix.

### Buggy code

```java
@PreAuthorize("hasRole("ADMIN")")
public void delete() {}
```

### Expected diagnosis

Method annotations are inactive unless method security is enabled.

### Corrected code

```java
@EnableMethodSecurity
@Configuration
class SecurityConfig {}
```

### Regression tests

```java
// Nonadmins are denied when invoking the method directly through the proxy.
```

## SEC-H-085: signature not checked

- Difficulty: Hard
- Framework: Spring Security
- Language: Java
- Perspective: JWT validation
- Concept: signature not checked
- Symptom: Forged claims authorize a request.
- Diagnostic goal: Verify signature, issuer, audience, and expiry.

### Buggy code

```java
JwtClaims claims = parser.parseUnsecured(token);
```

### Expected diagnosis

Reading claims without verification is equivalent to trusting user input.

### Corrected code

```java
JwtClaims claims = parser.verify(token, key).requireIssuer(issuer).requireAudience(audience).parse();
```

### Regression tests

```java
// Forged, expired, wrong-issuer tokens are rejected.
```

## SEC-H-086: authentication mistaken for authorization

- Difficulty: Hard
- Framework: Spring Security
- Language: Java
- Perspective: Authorization
- Concept: authentication mistaken for authorization
- Symptom: Every signed-in user can perform an admin action.
- Diagnostic goal: Require a permission or role for the operation.

### Buggy code

```java
.anyRequest().authenticated()
```

### Expected diagnosis

Authenticated only proves identity; it does not grant the admin capability.

### Corrected code

```java
.requestMatchers("/admin/**").hasAuthority("admin:write")
```

### Regression tests

```java
// A user without admin:write receives 403.
```

## SEC-H-087: session fixation risk

- Difficulty: Hard
- Framework: Spring Security
- Language: Java
- Perspective: Session policy
- Concept: session fixation risk
- Symptom: The session identifier remains attacker-controlled after login.
- Diagnostic goal: Apply a session fixation protection policy.

### Buggy code

```java
http.sessionManagement(s -> s.sessionFixation(f -> f.none()));
```

### Expected diagnosis

Keeping the pre-login session identifier permits fixation attacks.

### Corrected code

```java
http.sessionManagement(s -> s.sessionFixation(f -> f.changeSessionId()));
```

### Regression tests

```java
// Successful login changes or invalidates the pre-authentication id.
```

## SEC-H-088: security CORS differs from MVC CORS

- Difficulty: Hard
- Framework: Spring Security
- Language: Java
- Perspective: CORS
- Concept: security CORS differs from MVC CORS
- Symptom: Preflight requests are rejected before the controller.
- Diagnostic goal: Configure CORS in the security filter chain with the application policy.

### Buggy code

```java
http.cors(c -> c.disable());
```

### Expected diagnosis

The security chain can reject preflight before MVC configuration is reached.

### Corrected code

```java
http.cors(Customizer.withDefaults());
```

### Regression tests

```java
// OPTIONS preflight receives the configured allow origin and methods.
```

## SEC-H-089: logout endpoint accepts GET

- Difficulty: Hard
- Framework: Spring Security
- Language: Java
- Perspective: Logout
- Concept: logout endpoint accepts GET
- Symptom: A cross-site link can log users out unexpectedly.
- Diagnostic goal: Use POST and CSRF protection for browser logout.

### Buggy code

```java
http.logout(l -> l.logoutRequestMatcher(new AntPathRequestMatcher("/logout", "GET")));
```

### Expected diagnosis

GET should be safe and cannot carry a CSRF-protected state change reliably.

### Corrected code

```java
http.logout(l -> l.logoutUrl("/logout"));
```

### Regression tests

```java
// GET does not log out; CSRF-protected POST does.
```

## SEC-H-090: test user missing authority

- Difficulty: Hard
- Framework: Spring Security
- Language: Java
- Perspective: Testing security
- Concept: test user missing authority
- Symptom: A controller test fails before the business assertion.
- Diagnostic goal: Make the test authentication match the endpoint contract.

### Buggy code

```java
@WebMvcTest
void deletes() { mockMvc.perform(delete("/items/1")); }
```

### Expected diagnosis

The request is anonymous and security correctly denies it.

### Corrected code

```java
@WithMockUser(roles = "ADMIN")
void deletes() { mockMvc.perform(delete("/items/1").with(csrf())); }
```

### Regression tests

```java
// The test supplies both role and CSRF token.
```

## SEC-H-091: permitAll on protected path

- Difficulty: Hard
- Framework: Spring Security
- Language: Java
- Perspective: Filter chain
- Concept: permitAll on protected path
- Symptom: Unauthenticated users access an admin endpoint.
- Diagnostic goal: Order matchers from specific protected paths to general rules.

### Buggy code

```java
authorize.requestMatchers("/**").permitAll()
       .requestMatchers("/admin/**").hasRole("ADMIN")
```

### Expected diagnosis

The catch-all matcher matches first, so the admin rule is unreachable.

### Corrected code

```java
authorize.requestMatchers("/admin/**").hasRole("ADMIN")
       .anyRequest().authenticated()
```

### Regression tests

```java
// Anonymous admin access is 401/403; authenticated users follow role rules.
```

## SEC-H-092: CSRF disabled for browser session

- Difficulty: Hard
- Framework: Spring Security
- Language: Java
- Perspective: CSRF
- Concept: CSRF disabled for browser session
- Symptom: State-changing browser requests lack forgery protection.
- Diagnostic goal: Keep CSRF for cookie-authenticated browser flows.

### Buggy code

```java
http.csrf(csrf -> csrf.disable());
```

### Expected diagnosis

Disabling CSRF globally is unsafe when authentication is carried by cookies.

### Corrected code

```java
http.csrf(Customizer.withDefaults());
```

### Regression tests

```java
// A missing token is rejected for a session-authenticated POST.
```

## SEC-H-093: plain text password

- Difficulty: Hard
- Framework: Spring Security
- Language: Java
- Perspective: Password storage
- Concept: plain text password
- Symptom: A database leak exposes credentials immediately.
- Diagnostic goal: Store adaptive password hashes and compare through the encoder.

### Buggy code

```java
user.setPassword(rawPassword);
```

### Expected diagnosis

Raw passwords are reversible by anyone who obtains the database.

### Corrected code

```java
user.setPassword(passwordEncoder.encode(rawPassword));
```

### Regression tests

```java
// Login matches through passwordEncoder.matches and never compares raw storage.
```

## SEC-H-094: annotation ignored

- Difficulty: Hard
- Framework: Spring Security
- Language: Java
- Perspective: Method security
- Concept: annotation ignored
- Symptom: A role annotation has no effect.
- Diagnostic goal: Enable method security and use the correct authority prefix.

### Buggy code

```java
@PreAuthorize("hasRole("ADMIN")")
public void delete() {}
```

### Expected diagnosis

Method annotations are inactive unless method security is enabled.

### Corrected code

```java
@EnableMethodSecurity
@Configuration
class SecurityConfig {}
```

### Regression tests

```java
// Nonadmins are denied when invoking the method directly through the proxy.
```

## SEC-H-095: signature not checked

- Difficulty: Hard
- Framework: Spring Security
- Language: Java
- Perspective: JWT validation
- Concept: signature not checked
- Symptom: Forged claims authorize a request.
- Diagnostic goal: Verify signature, issuer, audience, and expiry.

### Buggy code

```java
JwtClaims claims = parser.parseUnsecured(token);
```

### Expected diagnosis

Reading claims without verification is equivalent to trusting user input.

### Corrected code

```java
JwtClaims claims = parser.verify(token, key).requireIssuer(issuer).requireAudience(audience).parse();
```

### Regression tests

```java
// Forged, expired, wrong-issuer tokens are rejected.
```

## SEC-H-096: authentication mistaken for authorization

- Difficulty: Hard
- Framework: Spring Security
- Language: Java
- Perspective: Authorization
- Concept: authentication mistaken for authorization
- Symptom: Every signed-in user can perform an admin action.
- Diagnostic goal: Require a permission or role for the operation.

### Buggy code

```java
.anyRequest().authenticated()
```

### Expected diagnosis

Authenticated only proves identity; it does not grant the admin capability.

### Corrected code

```java
.requestMatchers("/admin/**").hasAuthority("admin:write")
```

### Regression tests

```java
// A user without admin:write receives 403.
```

## SEC-H-097: session fixation risk

- Difficulty: Hard
- Framework: Spring Security
- Language: Java
- Perspective: Session policy
- Concept: session fixation risk
- Symptom: The session identifier remains attacker-controlled after login.
- Diagnostic goal: Apply a session fixation protection policy.

### Buggy code

```java
http.sessionManagement(s -> s.sessionFixation(f -> f.none()));
```

### Expected diagnosis

Keeping the pre-login session identifier permits fixation attacks.

### Corrected code

```java
http.sessionManagement(s -> s.sessionFixation(f -> f.changeSessionId()));
```

### Regression tests

```java
// Successful login changes or invalidates the pre-authentication id.
```

## SEC-H-098: security CORS differs from MVC CORS

- Difficulty: Hard
- Framework: Spring Security
- Language: Java
- Perspective: CORS
- Concept: security CORS differs from MVC CORS
- Symptom: Preflight requests are rejected before the controller.
- Diagnostic goal: Configure CORS in the security filter chain with the application policy.

### Buggy code

```java
http.cors(c -> c.disable());
```

### Expected diagnosis

The security chain can reject preflight before MVC configuration is reached.

### Corrected code

```java
http.cors(Customizer.withDefaults());
```

### Regression tests

```java
// OPTIONS preflight receives the configured allow origin and methods.
```

## SEC-H-099: logout endpoint accepts GET

- Difficulty: Hard
- Framework: Spring Security
- Language: Java
- Perspective: Logout
- Concept: logout endpoint accepts GET
- Symptom: A cross-site link can log users out unexpectedly.
- Diagnostic goal: Use POST and CSRF protection for browser logout.

### Buggy code

```java
http.logout(l -> l.logoutRequestMatcher(new AntPathRequestMatcher("/logout", "GET")));
```

### Expected diagnosis

GET should be safe and cannot carry a CSRF-protected state change reliably.

### Corrected code

```java
http.logout(l -> l.logoutUrl("/logout"));
```

### Regression tests

```java
// GET does not log out; CSRF-protected POST does.
```

## SEC-H-100: test user missing authority

- Difficulty: Hard
- Framework: Spring Security
- Language: Java
- Perspective: Testing security
- Concept: test user missing authority
- Symptom: A controller test fails before the business assertion.
- Diagnostic goal: Make the test authentication match the endpoint contract.

### Buggy code

```java
@WebMvcTest
void deletes() { mockMvc.perform(delete("/items/1")); }
```

### Expected diagnosis

The request is anonymous and security correctly denies it.

### Corrected code

```java
@WithMockUser(roles = "ADMIN")
void deletes() { mockMvc.perform(delete("/items/1").with(csrf())); }
```

### Regression tests

```java
// The test supplies both role and CSRF token.
```
