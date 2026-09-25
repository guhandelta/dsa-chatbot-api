#!/usr/bin/env bash
#
# Builds a logical commit series for the backend.
#
# These commits reconstruct the project in a sensible build order — they are
# not a replay of real development history. Each commit stages a coherent slice
# so the log reads as a narrative and reviewers can step through it.
#
# Usage (from inside dsa-chatbot-api/):
#     bash git_commits.sh
#
# Works on a fresh repo (runs git init) or on top of an existing one.
set -euo pipefail

BRANCH="${BRANCH:-main}"

# ---------------------------------------------------------------- safety
if [ ! -f "app/main.py" ]; then
  echo "ERROR: run this from inside dsa-chatbot-api/" >&2
  exit 1
fi

if [ ! -d .git ]; then
  echo "→ Initialising a new repository"
  git init -q
  git symbolic-ref HEAD "refs/heads/$BRANCH"
fi

# Never let a real .env reach a commit.
if [ -f .env ] && ! grep -qx '\.env' .gitignore 2>/dev/null; then
  echo "ERROR: .env exists but is not ignored. Fix .gitignore first." >&2
  exit 1
fi
if git ls-files --error-unmatch .env >/dev/null 2>&1; then
  echo "ERROR: .env is tracked by git. Run: git rm --cached .env" >&2
  exit 1
fi

commit () {
  local msg="$1"; shift
  # -A picks up deletions too, so this works when replacing an older checkout
  git add -A -- "$@" 2>/dev/null || true
  if git diff --cached --quiet; then
    echo "   (nothing staged, skipping) $msg"
  else
    git commit -q -m "$msg"
    echo "✓ $msg"
  fi
}

echo
echo "Building commit series on branch '$BRANCH'..."
echo

commit "chore: project scaffolding, gitignore, and pinned dependencies" \
  .gitignore .env.example requirements.txt requirements-dev.txt pytest.ini \
  app/__init__.py app/core/__init__.py app/db/__init__.py \
  app/models/__init__.py app/routers/__init__.py app/services/__init__.py

commit "feat(core): env-driven settings and async SQLAlchemy session management" \
  app/core/config.py app/db/database.py

commit "feat(db): user, transaction, chat history, and submission models" \
  app/db/models.py

commit "feat(auth): JWT issuance, password hashing, and role dependencies" \
  app/core/security.py

commit "feat(api): request/response schemas" \
  app/models/schemas.py

commit "feat(auth): register, login, profile, and language preference endpoints" \
  app/routers/auth.py

commit "feat(peppercorns): append-only ledger with atomic debits and refunds" \
  app/services/peppercorns.py

commit "feat(llm): provider router for OpenAI, Anthropic, and Gemini" \
  app/services/llm_router.py

commit "feat(rag): Chroma knowledge base with incremental upsert" \
  app/services/knowledge_base.py

commit "feat(rag): track-scoped retrieval pipeline with per-track tutor personas" \
  app/services/rag_pipeline.py

commit "feat(chat): paid chat endpoint with persisted history and refund-on-failure" \
  app/routers/chat.py

commit "feat(analyze): structured solution review via constrained LLM output" \
  app/services/solution_analyzer.py app/routers/analyze.py

commit "feat(content): problem catalog and three-track content model" \
  app/services/problem_catalog.py app/services/content_catalog.py

commit "content: 23 Blind 75 problems with solutions in six languages" \
  data/dsa_problems

commit "content: language-fundamentals and algorithm-concept track seeds" \
  data/content

commit "feat(tracks): three learning paths with learn and practice modes" \
  app/routers/tracks.py app/routers/problems.py

commit "feat(admin): user listing and role assignment" \
  app/routers/admin.py

commit "feat(training): sandboxed multi-language code execution harness" \
  app/services/code_runner.py

commit "feat(training): LLM enrichment with correction and test-case generation" \
  app/services/training.py

commit "feat(training): validation pipeline gating auto-publish on execution" \
  app/services/training_pipeline.py app/routers/training.py

commit "feat(app): application entry point with CORS and router registration" \
  app/main.py

commit "test: ledger, auth, roles, chat flow, tracks, and sandbox suites" \
  tests

commit "tools: offline verification and brute-force stress checks" \
  tools

commit "docs: setup, API reference, training workflow, and security notes" \
  README.md git_commits.sh

echo
echo "Done. Review with:  git log --oneline"
echo
echo "Then push:"
echo "  git remote add origin git@github.com:<you>/dsa-chatbot-api.git"
echo "  git push -u origin $BRANCH"
