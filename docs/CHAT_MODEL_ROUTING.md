# Tutor model routing

Student chat always uses server-side automatic model selection, including lesson
chats and requests that explicitly name a provider. Admins and instructors retain
their manual provider selection and may also request `provider: "auto"` via the
API. Other features, such as solution evaluation and training, retain their
existing model selection behavior.
Staff requests that omit a provider retain the previous Gemini default.

LangGraph runs a finite `classify → select → answer` workflow. Classification is
an inexpensive rule-based policy over the current question, using the latest
user question for short follow-ups. LangChain's existing model adapters call the
actual provider. Neither framework is an independent answering model.

Configure preferences in the API `.env`:

```dotenv
CHAT_EXPLAIN_PROVIDER=gemini
CHAT_CODE_PROVIDER=claude
CHAT_REASONING_PROVIDER=openai
CHAT_MODEL_TIMEOUT_SECONDS=45
```

These are initial policy defaults, not measured provider quality rankings.
Explanations and quizzes use the explanation preference; fenced code and debug
questions use the code preference; complexity, proof, and comparison questions
use the reasoning preference. Model IDs continue to come from `GEMINI_MODEL`,
`ANTHROPIC_MODEL`, and `OPENAI_MODEL`. No model names are selected by user text.

Only providers with a configured API key and model ID are eligible. The preferred
provider is followed by `DEFAULT_PROVIDER`, then the remaining providers in stable
order. At most two generation attempts run, each bounded by the configured
timeout (including any SDK retries). Fallback handles connectivity, timeouts,
rate limits, and provider configuration/service errors. Application rejections,
invalid results, and cancellations do not trigger another provider.

All attempts execute inside the existing single paid operation. A successful
fallback costs the student one chat charge; total failure refunds that charge.
Idempotent retries replay the answer and routing metadata without generating or
charging again. Routing metadata includes strategy, task, actual provider/model,
and whether a failure fallback was used. Logs record routing without question
text or credentials.

Language access and reference scope are checked independently of model routing:
students have only unexpired subscription languages (a cancelled subscription
retains access until its expiry), admins have the full known catalogue, and
instructor scope is unchanged. Model choice cannot grant another language.

The chat's optional learning-material selector filters references to the current
language. It scopes retrieval to a collection such as Spring MVC; it does not
select a model. Without a collection, the general tutor retrieves within the
current track. No selector is displayed when that language has no collections.

Before treating these defaults as quality-optimized, evaluate representative
explanations, code questions, proofs, follow-ups, and ambiguous questions across
the configured models, recording answer correctness, latency, and provider cost.
Offline tests cover policy, authorization, fallback, timeout, billing, and replay;
they do not establish model answer quality or validate provider credentials.
