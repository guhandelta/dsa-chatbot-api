# Product & Engineering Specification: Study Room Dynamic Quiz Engine

**Status:** Draft / Proposed Specification  
**Author:** Engineering & Curriculum Team  
**Last Updated:** 2026-10-26  
**Target Components:** `Study Room`, `TopicQuestionsSection`, `studyApi`, `dsa-chatbot-api (quiz service)`

---

## 1. Executive Summary & Problem Analysis

### 1.1 The Problem
When learners enter the Quiz / Reflection section of the Study Room, the header and questions can be out of step with their active stage or selected learning path. The header now shows the selected node's title; a fallback to a default stage (e.g., *"Topic Questions: Values and arithmetic"*) has been reported and is still to be verified. 

Specifically:
- **Disconnect from Active Context:** When node focus is not set, the page may fall back to a default node instead of the learner's current milestone or selected topic. The header already shows the selected node's title (`TopicQuestionsSection.tsx`); the fallback path has not been verified and is the first thing to check.
- **Conflation of Reflection vs. Assessment:** Open-ended conversational reflection prompts (`"Think it through"`) are mixed with structured, graded quizzes (`"Quiz me"` / checks), causing learner confusion.
- **Limited Interaction Diversity:** Current questions are predominantly static text reflections, lacking code-completion challenges and interactive multi-tier verification.
- **Absence of On-Demand Synthesis:** Questions are largely pulled from rigid static lists rather than generated dynamically from curated curriculum knowledge with deterministic accuracy checks.

### 1.2 The Vision
Transform the Study Room Quiz Generator into an **adaptive, on-demand, multi-format assessment engine** that:
1. Automatically resolves to the user's active stage, subtopic, and selected programming language.
2. Delivers sessions of **unique, randomized questions** (length is an open product decision, see 2.3) blending Multiple-Choice Questions (MCQs) and interactive **Code-Fill ("Fill-in-the-Blank")** challenges.
3. Implements a **multi-pass validation pipeline** to guarantee syntactical correctness, zero cross-language syntax leakage, and unambiguous answer keys before learners ever see a question.

---

## 2. Core Functional Requirements

### 2.1 Dynamic Context Resolution
- The quiz engine must detect the active node context (`language:stage-XX:topic-YY` or active curriculum node slug).
- If the learner clicks a specific topic in the learning pathway sidebar (e.g., *Conditions*, *Pointers & Memory*, *Hash Tables*), the quiz generator immediately aligns to that active selection.
- If no node is explicitly selected, it defaults to the learner's **next uncompleted milestone** according to their learning path progression record, never a hardcoded fallback.

### 2.2 Question Formats & Interaction Types
Each quiz session must present a mixed combination of formats:

| Format | Share | Description | Example Interaction |
| :--- | :--- | :--- | :--- |
| **Conceptual MCQ** | ~35% | Evaluates mental models, edge cases, time/space complexity, or memory semantics. | Standard radio choice with 4 distinct, plausible distractors. |
| **Code Tracing MCQ** | ~35% | Presents an idiomatic snippet and asks for exact output, return value, or state evolution. | Monospace code block with choices reflecting typical off-by-one or evaluation order pitfalls. |
| **Code Fill-in-the-Blank (`code_gap`)** | ~30% | Presents a code snippet with one or two targeted missing tokens/blocks marked by placeholders (`___BLANK___`). | Inline input or code editor field requiring the learner to write the missing keyword, slice syntax, method call, or operator. |

### 2.3 Session Assembly & Difficulty Progression
- **Session Length (open decision):** The current API accepts 1–8 questions and defaults to 4 (`routers/study.py`). The draft's 10–20 target conflicts with that. Proposed: a setting whose default matches the code today, with a longer stage-assessment length once the pool can supply it. Product to decide.
- **Difficulty Curve (Adaptive Spiral), on the learning path's levels:** The path uses five levels, L0–L4 (`learning_path.LEVEL_LABELS`), not L1–L3. The shares below are proposals, and how L0 and L4 items are mixed in is not yet defined.
  - **L1 Core constructs (proposed 30%):** Core syntax, idioms, basic arithmetic/control flow.
  - **L2 Data modelling (proposed 50%):** Boundary conditions, data structure manipulation, scoping rules.
  - **L3 Recursion, complexity and depth (proposed 20%):** Performance implications, memory models (e.g., value vs. reference), edge cases, anti-patterns.
- **Deduplication:** A learner must not see duplicate questions within the same attempt or across recent sessions on the same topic until the pool has been exhausted.

---

## 3. On-Demand Generation & Multi-Pass Quality Assurance Pipeline

To check AI-generated questions before a learner sees them (no process can guarantee perfection), and to keep them strictly confined to the chosen language, generation follows a **four-stage pipeline**. Questions that fail a check go to a review queue, never to learners:

```
[Curriculum Topic + Language + Level]
                 │
                 ▼
 ┌───────────────────────────────┐
 │ Stage 1: LLM Generator Engine │  ──> Structured Generation (Strict JSON Schema)
 └───────────────────────────────┘
                 │
                 ▼
 ┌───────────────────────────────┐
 │ Stage 2: AST & Language Linter│  ──> Validates code snippets compile/parse in target lang
 └───────────────────────────────┘      Rejects cross-language contamination (e.g., no 'console.log' in Python)
                 │
                 ▼
 ┌───────────────────────────────┐
 │ Stage 3: Deterministic Verifier│ ──> Tests correct answer uniqueness, distractor plausibility,
 └───────────────────────────────┘      and verifies code-gap substitutions execute cleanly
                 │
                 ▼
 ┌───────────────────────────────┐
 │ Stage 4: Verified Pool Buffer │  ──> Serves an instant session of the configured length to the client
 └───────────────────────────────┘
```

### 3.1 Stage 1: Schema-Bound Generation
The generator prompt uses strict system instructions, enforced JSON schemas, and language isolation guardrails:
- Injected context: Target language version (e.g., Python 3.12, C++20, ES2024), topic curriculum summary, and disallowed language crossover tokens.
- Output: Strict JSON matching the `QuizItem` specification.

### 3.2 Stage 2: Syntax & Language Contamination Check
- **Contamination Filter:** Automated regex and lexical scan checking for foreign keywords (e.g., ensuring no `nil` or `let` in Python; no `self.` in Java; no `std::` in Go).
- **AST / Parser Validation:** All code snippets (`code` and `codeSnippet`) must parse cleanly through the target language grammar. For code-fill questions, substituting the expected answer into `___BLANK___` must yield valid, executable code.

### 3.3 Stage 3: Verifier & Critic Agent
- Checks that the `expected` answer key unambiguously solves the prompt.
- Checks that distractors are genuinely incorrect, educational, and not viable alternative interpretations.
- Validates that explanations provide clear rationale for both the correct answer and common learner misconceptions.

### 3.4 Stage 4: Fallback & Caching Strategy
- To prevent latency spikes during live user sessions, pre-validated candidate questions are maintained in a verified topic pool buffer (`status: 'verified_ready'`).
- If on-demand generation fails any validation step, the engine immediately fulfills the session from the verified buffer and enqueues asynchronous pool replenishment.

---

## 4. Data Contracts & Architecture

### 4.1 Frontend Data Contract (`QuizItem` Extension)

```typescript
export type QuizType = 
  | 'mcq'              // Conceptual multiple choice
  | 'mcq_code'         // Multiple choice with code snippet
  | 'code_gap'         // Missing block fill-in-the-blank
  | 'short_answer'     // Exact keyword/short string answer
  | 'fix_bug'          // Bug isolation
  | 'write_snippet'    // Micro-code implementation

export interface QuizItem {
  id: string
  type: QuizType
  prompt: string
  concept: string
  language: string               // e.g., 'python', 'javascript', 'cpp', 'rust'
  difficulty: 'L0' | 'L1' | 'L2' | 'L3' | 'L4'   // the learning path's levels (LEVEL_LABELS)
  code?: string                  // Provided code block (with ___BLANK___ if code_gap)
  choices?: string[]             // For MCQ formats (4 choices)
  blank_placeholder?: string     // Default: '___BLANK___'
  starter?: string               // Optional starter text for inputs
  // expected (the answer key) is SERVER-ONLY. It is never in this type or any
  // response before the learner answers. See 4.3.
  explanation: string            // Deep pedagogical explanation
  misconception_hints?: Record<string, string> // Custom feedback per wrong choice
  validation_status: 'verified'
}

export interface QuizSessionRequest {
  language: string
  node_id: string                // e.g., 'python:stage-02'
  count: number                  // 10 to 20
  difficulty_preference?: 'balanced' | 'reinforce' | 'challenge'
}

export interface QuizSessionResponse {
  quiz_id: string
  node_id: string
  node_title: string
  language: string
  items: QuizItem[]
  total: number
  generated_at: string
}
```

### 4.2 Interactive Code Gap Specification
For `type: 'code_gap'`:
- The snippet contains a token `___BLANK___`.
- The user is rendered an inline monospace input field or an editor slot.
- Evaluation supports whitespace trimming, formatting tolerance, and multi-alias acceptance (e.g., `range(len(arr))` vs `range(0, len(arr))`).
- Multi-alias acceptance is its own rule with its own tests. Exact matching rejects correct answers; loose matching accepts wrong ones. Neither is acceptable by default.

### 4.3 Answer-Key Handling (required)

- The answer key (`expected`) and any test inputs stay on the server. The client receives a question (`id`, `type`, `prompt`, `concept`, `level`, `code`, `choices`, `starter`) and nothing else.
- `explanation` and `misconception_hints` are returned only after the learner answers that item. The current API already works this way (`quiz.public` and `quiz.grade`).
- A new `code_gap` item is graded on the server, the same way code items are graded today.
- The test suite must assert that no response before an answer contains `expected`, `answer`, or a test case's expected value.

---

## 5. UI/UX Specifications for Study Room

1. **Clear Header Indicator:**
   - Replace *"Topic Questions: Values and arithmetic"* with:
     ```
     [Stage 2 · Section 3: Branching & Control Flow]
     Active Quiz: Python Conditions (Question 3 of 15)
     ```
2. **Distinct Modes:**
   - **"Think It Through" (Reflection):** Ungraded, conversational coach prompts (no score, no penalty).
   - **"Active Quiz" (Assessment):** Graded, interactive questions (instant feedback, mastery progression, streak rewards).
3. **Question Carousel & Progress Bar:**
   - Shows difficulty indicators (🟢 Easy, 🟡 Medium, 🟣 Advanced).
   - Visual progress tracker (`[ ✓ ][ ✓ ][ ✗ ][ • ][ • ] ...`).
4. **Immediate Misconception Feedback:**
   - When a wrong choice is selected, display an explanation of *why* that choice was a common pitfall rather than just stating it is incorrect.

---

## 6. Implementation Milestones

- [ ] **Milestone 1: Dynamic Node Binding**
  - Decouple `TopicQuestionsSection` from default stage fallback; link directly to active study node from route search params / store.
- [ ] **Milestone 2: Code-Gap UI Component**
  - Implement interactive `CodeGapRenderer` in `src/components/study/` supporting syntax highlighting and inline blank inputs.
- [ ] **Milestone 3: Backend Multi-Pass Generation Service**
  - Implement `QuizGeneratorService` in API with JSON schema enforcement, target language AST validation, and contamination filters.
- [ ] **Milestone 4: Verified Pool & Session Manager**
  - Add pool caching, session randomization at the configured length, and difficulty distribution curves. Build on `quiz.draw` and `learning_strikes.pick` (see the review).
- [ ] **Milestone 5: End-to-End Vitest & Cypress Test Suite**
  - Automated test coverage verifying node switching, MCQ answering, code-gap evaluation, and zero language crossover.
