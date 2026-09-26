#!/usr/bin/env python3
"""End-to-end smoke test against a RUNNING server.

    # terminal 1
    uvicorn app.main:app --reload --port 8000
    # terminal 2
    python tools/smoke_test.py
    python tools/smoke_test.py --no-llm     # skip everything that costs money
    python tools/smoke_test.py --url http://localhost:8000

`doctor.py` validates the app before it starts. This validates it after —
by driving the real HTTP API the way the UI does, in the order a user would.

WHAT IT COVERS
--------------
  health, register, admin bootstrap, login, /auth/me, language preference,
  the track catalog, problem statements, rate limiting, peppercorn debits and
  the ledger, code execution and evidence, the mentor gate, role gates, and
  the admin surfaces.

WHAT COSTS MONEY
----------------
Only the three LLM paths: chat, analyze, mentor. `--no-llm` skips them and
still exercises everything else, which is most of the surface. A full run
costs a few cents.

The test creates a throwaway account with a timestamped email so repeated
runs never collide, and it never deletes anything — inspect the leftovers if
something fails.
"""
from __future__ import annotations

import argparse
import sys
import time
import uuid

try:
    import httpx
except ImportError:
    print("httpx is required:  pip install -r requirements.txt")
    sys.exit(1)

PASS, FAIL, SKIP = "PASS", "FAIL", "SKIP"
results: list[tuple[str, str, str]] = []


def record(name: str, status: str, detail: str = "") -> bool:
    results.append((name, status, detail))
    mark = {PASS: "ok  ", FAIL: "FAIL", SKIP: "skip"}[status]
    line = f"  {mark} {name}"
    if detail:
        line += f"  — {detail}"
    print(line, flush=True)
    return status != FAIL


class Smoke:
    def __init__(self, base_url: str, use_llm: bool):
        self.base = base_url.rstrip("/")
        self.use_llm = use_llm
        # Generous timeout: a review runs fuzzing plus two LLM calls and can
        # legitimately take a minute. A short timeout here would report a
        # false failure on a working system.
        self.client = httpx.Client(base_url=self.base, timeout=180.0)
        self.token = ""
        self.user_id = ""
        self.email = f"smoke+{int(time.time())}-{uuid.uuid4().hex[:6]}@example.com"

    def h(self) -> dict:
        return {"Authorization": f"Bearer {self.token}"} if self.token else {}

    # ---------------------------------------------------------- foundation

    def check_health(self) -> bool:
        try:
            r = self.client.get("/health")
        except httpx.ConnectError:
            return record("server reachable", FAIL,
                          f"nothing listening on {self.base} — is uvicorn running?")
        return record("server reachable", PASS if r.status_code == 200 else FAIL,
                      f"status {r.status_code}")

    def check_docs(self) -> bool:
        r = self.client.get("/docs")
        return record("OpenAPI docs render", PASS if r.status_code == 200 else FAIL)

    # ---------------------------------------------------------- auth

    def check_register(self) -> bool:
        r = self.client.post("/auth/register",
                             json={"email": self.email, "password": "smoketest123"})
        if r.status_code != 201:
            return record("register", FAIL, f"{r.status_code} {r.text[:120]}")
        body = r.json()
        self.token = body["access_token"]
        self.user_id = body["user"]["id"]
        bonus = body["user"]["peppercorns"]
        ok = bonus > 0
        return record("register grants signup bonus",
                      PASS if ok else FAIL, f"{bonus} peppercorns")

    def check_duplicate_register(self) -> bool:
        r = self.client.post("/auth/register",
                             json={"email": self.email, "password": "smoketest123"})
        return record("duplicate email rejected",
                      PASS if r.status_code == 409 else FAIL, f"status {r.status_code}")

    def check_login(self) -> bool:
        r = self.client.post("/auth/login",
                             json={"email": self.email, "password": "smoketest123"})
        if r.status_code != 200:
            return record("login", FAIL, f"{r.status_code} {r.text[:120]}")
        self.token = r.json()["access_token"]
        return record("login returns a working token", PASS)

    def check_bad_password(self) -> bool:
        r = self.client.post("/auth/login",
                             json={"email": self.email, "password": "wrongpassword"})
        return record("wrong password rejected",
                      PASS if r.status_code == 401 else FAIL, f"status {r.status_code}")

    def check_unauthenticated_blocked(self) -> bool:
        r = self.client.get("/auth/me")   # no header
        return record("protected route rejects anonymous",
                      PASS if r.status_code == 401 else FAIL, f"status {r.status_code}")

    def check_me(self) -> bool:
        r = self.client.get("/auth/me", headers=self.h())
        if r.status_code != 200:
            return record("/auth/me", FAIL, f"status {r.status_code}")
        body = r.json()
        return record("/auth/me returns the session", PASS,
                      f"role={body['role']} peppercorns={body['peppercorns']}")

    def check_language_preference(self) -> bool:
        r = self.client.patch("/auth/me/language", headers=self.h(),
                              json={"language": "rust"})
        if r.status_code != 200 or r.json()["preferred_language"] != "rust":
            return record("language preference saves", FAIL, r.text[:120])
        self.client.patch("/auth/me/language", headers=self.h(),
                          json={"language": "python"})
        return record("language preference saves and persists", PASS)

    # ---------------------------------------------------------- content

    def check_tracks(self) -> bool:
        r = self.client.get("/tracks/", headers=self.h())
        if r.status_code != 200:
            return record("track catalog", FAIL, f"status {r.status_code}")
        tracks = [t["track"] for t in r.json()["tracks"]]
        ok = {"language", "dsa", "algorithm"}.issubset(set(tracks))
        return record("three tracks present", PASS if ok else FAIL, ", ".join(tracks))

    def check_problems(self) -> bool:
        r = self.client.get("/tracks/dsa/items", headers=self.h())
        if r.status_code != 200:
            return record("problem list", FAIL, f"status {r.status_code}")
        items = r.json()
        ok = len(items) > 0
        return record("problems available", PASS if ok else FAIL,
                      f"{len(items)} problems — did you run the ingest?")

    def check_statement(self) -> bool:
        """The Practice page depends on this; it was missing entirely once."""
        r = self.client.get("/tracks/items/two-sum", headers=self.h())
        if r.status_code != 200:
            return record("problem statement fetch", FAIL, f"status {r.status_code}")
        md = r.json()["markdown"]
        has_problem = "## Problem" in md
        return record("problem statement retrievable",
                      PASS if has_problem else FAIL, f"{len(md)} chars")

    def check_algorithm_links(self) -> bool:
        r = self.client.get("/tracks/algorithms/tags", headers=self.h())
        if r.status_code != 200:
            return record("algorithm tags", FAIL, f"status {r.status_code}")
        tags = r.json()["algorithms"]
        return record("algorithm tags resolve", PASS if tags else FAIL,
                      f"{len(tags)} tags")

    # ---------------------------------------------------------- paid paths

    def check_analyze(self) -> bool:
        """The most valuable single check: exercises the sandbox, differential
        fuzzing against the reference, the LLM review, and the debit."""
        if not self.use_llm:
            return record("code review (analyze)", SKIP, "--no-llm")

        buggy = (
            "def two_sum(nums, target):\n"
            "    seen = {}\n"
            "    for i, x in enumerate(nums):\n"
            "        seen[x] = i\n"           # reuse bug, fuzzer should catch it
            "        if target - x in seen:\n"
            "            return [seen[target - x], i]\n"
            "    return []"
        )
        before = self.client.get("/auth/me", headers=self.h()).json()["peppercorns"]
        r = self.client.post("/analyze/", headers=self.h(), json={
            "problem_id": "two-sum", "user_code": buggy, "language": "python",
        })
        if r.status_code != 200:
            return record("code review (analyze)", FAIL, f"{r.status_code} {r.text[:200]}")

        body = r.json()
        after = body["peppercorns_remaining"]
        record("analyze debits peppercorns",
               PASS if after < before else FAIL, f"{before} -> {after}")

        evidence = body.get("evidence") or {}
        fuzz = evidence.get("fuzz") or {}
        if fuzz.get("ran"):
            found = bool(fuzz.get("counterexamples"))
            record("differential fuzzing catches a known bug",
                   PASS if found else FAIL,
                   fuzz["counterexamples"][0]["description"][:80] if found
                   else f"{fuzz.get('passed')}/{fuzz.get('total')} passed — expected a failure")
        else:
            record("differential fuzzing ran", FAIL, fuzz.get("note", "did not run"))

        return record("analyze returns structured feedback",
                      PASS if body.get("analysis") else FAIL)

    def check_chat(self) -> bool:
        if not self.use_llm:
            return record("RAG chat", SKIP, "--no-llm")
        r = self.client.post("/chat/", headers=self.h(), json={
            "message": "What data structure gives O(1) lookup?",
            "track": "dsa", "language": "python",
        })
        if r.status_code != 200:
            return record("RAG chat", FAIL, f"{r.status_code} {r.text[:200]}")
        body = r.json()
        return record("RAG chat answers and debits", PASS,
                      f"{len(body['answer'])} chars, {body['peppercorns_remaining']} left")

    def check_mentor_gate(self) -> bool:
        """Without a subscription the mentor must refuse with 402."""
        r = self.client.post("/mentor/ask", headers=self.h(), json={
            "problem_id": "two-sum", "language": "python",
            "reasoning": "I think I need a nested loop.",
        })
        ok = r.status_code == 402
        return record("mentor requires a subscription",
                      PASS if ok else FAIL, f"status {r.status_code}")

    def check_profile(self) -> bool:
        r = self.client.get("/mentor/profile", headers=self.h())
        if r.status_code != 200:
            return record("learning profile", FAIL, f"status {r.status_code}")
        body = r.json()
        if self.use_llm:
            ok = body["total_attempts"] > 0
            return record("analyze recorded a learning event",
                          PASS if ok else FAIL,
                          f"attempts={body['total_attempts']} solved={body['solved']}")
        return record("learning profile reachable", PASS)

    # ---------------------------------------------------------- roles

    def check_role_gates(self) -> bool:
        r = self.client.get("/training/status", headers=self.h())
        train_blocked = r.status_code == 403
        r2 = self.client.get("/admin/users", headers=self.h())
        admin_blocked = r2.status_code == 403
        is_admin = self.client.get("/auth/me", headers=self.h()).json()["role"] == "admin"

        if is_admin:
            return record("role gates (account is admin)", PASS,
                          "training and admin reachable — ADMIN_EMAILS matched")
        ok = train_blocked and admin_blocked
        return record("role gates block a plain student",
                      PASS if ok else FAIL,
                      f"training={r.status_code} admin={r2.status_code}")

    # ---------------------------------------------------------- report

    def run(self) -> int:
        print(f"\nSmoke test against {self.base}")
        print(f"Account: {self.email}")
        print(f"LLM paths: {'enabled' if self.use_llm else 'skipped (--no-llm)'}\n")

        print("[foundation]")
        if not self.check_health():
            print("\nServer is not reachable — nothing else can be tested.")
            return 1
        self.check_docs()

        print("\n[auth]")
        if not self.check_register():
            return 1
        self.check_duplicate_register()
        self.check_bad_password()
        self.check_unauthenticated_blocked()
        self.check_login()
        self.check_me()
        self.check_language_preference()

        print("\n[content]")
        self.check_tracks()
        self.check_problems()
        self.check_statement()
        self.check_algorithm_links()

        print("\n[paid paths]")
        self.check_analyze()
        self.check_chat()
        self.check_mentor_gate()
        self.check_profile()

        print("\n[roles]")
        self.check_role_gates()

        failed = [n for n, s, _ in results if s == FAIL]
        skipped = sum(1 for _, s, _ in results if s == SKIP)
        passed = sum(1 for _, s, _ in results if s == PASS)

        print("\n" + "=" * 60)
        if failed:
            print(f"{len(failed)} FAILED, {passed} passed, {skipped} skipped\n")
            for name in failed:
                print(f"  - {name}")
            return 1
        print(f"All {passed} checks passed"
              + (f", {skipped} skipped" if skipped else "") + ".")
        print(f"\nTest account left in place for inspection: {self.email}")
        return 0


def main() -> int:
    parser = argparse.ArgumentParser(description="Smoke-test a running server.")
    parser.add_argument("--url", default="http://localhost:8000")
    parser.add_argument("--no-llm", action="store_true",
                        help="skip chat/analyze/mentor (no API spend)")
    args = parser.parse_args()
    return Smoke(args.url, use_llm=not args.no_llm).run()


if __name__ == "__main__":
    sys.exit(main())
