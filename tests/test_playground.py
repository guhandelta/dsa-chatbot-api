"""Web playground: stored projects and sandboxed TypeScript compilation."""
import pytest

from app.core.config import settings
from app.routers.playground import parse_tsc, transpile
from app.services.code_runner import available_languages


async def _learner(client, email="playground@example.com"):
    registered = (await client.post("/auth/register", json={"email": email, "password": "password123"})).json()
    return {"Authorization": "Bearer " + registered["access_token"]}


def _files(*pairs):
    return [{"name": n, "content": c} for n, c in pairs]


async def test_projects_start_from_templates_and_autosave_with_revisions(client):
    headers = await _learner(client)
    listing = (await client.get("/playground", headers=headers)).json()
    assert {t["id"] for t in listing["templates"]} == {"html-css-js", "html-css-ts", "react-tsx", "html-css"}
    fresh = (await client.get("/playground/first", params={"template": "html-css-ts"}, headers=headers)).json()
    assert fresh["revision"] is None and {f["name"] for f in fresh["files"]} == {"index.html", "styles.css", "script.ts"}
    saved = await client.put("/playground/first", headers=headers,
                             json={"template": "html-css-ts", "files": fresh["files"], "revision": None})
    assert saved.status_code == 200 and saved.json()["revision"] == 1
    stale = await client.put("/playground/first", headers=headers,
                             json={"template": "html-css-ts", "files": fresh["files"], "revision": None})
    assert stale.status_code == 409
    reopened = (await client.get("/playground/first", headers=headers)).json()
    assert reopened["revision"] == 1 and reopened["template"] == "html-css-ts"
    assert [p["slug"] for p in (await client.get("/playground", headers=headers)).json()["projects"]] == ["first"]
    other = await _learner(client, "playground-other@example.com")
    assert (await client.get("/playground/first", headers=other)).json()["revision"] is None


async def test_project_names_and_files_are_validated(client):
    headers = await _learner(client)
    assert (await client.get("/playground/Bad_Name", headers=headers)).status_code == 422
    for files in (_files(("styles.css", "")), _files(("index.html", ""), ("../x.js", "")),
                  _files(("index.html", ""), ("app.py", "")), _files(("index.html", "x" * 60_001))):
        response = await client.put("/playground/ok", headers=headers, json={"files": files})
        assert response.status_code == 422, files


async def test_project_capacity_covers_ui_challenge_battery_and_enforces_limit(client, monkeypatch):
    from app.routers import playground

    headers = await _learner(client)
    assert playground.MAX_PROJECTS >= 38
    assert (await client.get("/playground", headers=headers)).json()["limits"]["max_projects"] == 100

    monkeypatch.setattr(playground, "MAX_PROJECTS", 1)
    files = _files(("index.html", "<main>work</main>"))
    assert (await client.put("/playground/first", headers=headers,
                             json={"files": files, "revision": None})).status_code == 200
    limited = await client.put("/playground/second", headers=headers,
                               json={"files": files, "revision": None})
    assert limited.status_code == 409
    assert "up to 1 playground projects" in limited.json()["detail"]


def test_tsc_diagnostics_are_parsed_with_locations():
    out = "script.ts(3,7): error TS2322: Type 'string' is not assignable to type 'number'.\n  continued detail"
    assert parse_tsc(out) == [{"file": "script.ts", "line": 3, "column": 7, "code": "TS2322",
                               "message": "Type 'string' is not assignable to type 'number'. continued detail"}]


def test_typescript_compiles_with_dom_types_and_still_emits_on_type_errors():
    if not available_languages().get("typescript"):
        pytest.skip("TypeScript unavailable")
    ok = transpile(_files(("index.html", ""), ("script.ts", "const b = document.body as HTMLElement;\nlet n: number = 1;\nconsole.log(b, n);\n")))
    assert ok["diagnostics"] == [] and "document.body" in ok["outputs"]["script.ts"]
    bad = transpile(_files(("script.ts", "let n: number = 'one';\nconsole.log(n);\n")))
    assert bad["diagnostics"][0]["line"] == 1 and bad["diagnostics"][0]["code"] == "TS2322"
    assert "console.log(n)" in bad["outputs"]["script.ts"]


async def test_transpile_endpoint_is_rate_limited(client, monkeypatch):
    if not available_languages().get("typescript"):
        pytest.skip("TypeScript unavailable")
    monkeypatch.setattr(settings, "workspace_runs_per_hour", 1)
    headers = await _learner(client)
    body = {"files": _files(("script.ts", "let n: number = 1;\n"))}
    assert (await client.post("/playground/transpile", headers=headers, json=body)).status_code == 200
    assert (await client.post("/playground/transpile", headers=headers, json=body)).status_code == 429


def test_react_tsx_and_jsx_compile_to_create_element_calls():
    if not available_languages().get("typescript"):
        pytest.skip("TypeScript unavailable")
    from app.routers.playground import TEMPLATES
    react = TEMPLATES["react-tsx"]["files"]
    result = transpile([{"name": n, "content": c} for n, c in react])
    assert result["diagnostics"] == [], result["diagnostics"]
    assert "React.createElement(Counter" in result["outputs"]["app.tsx"]
    jsx = transpile(_files(("widget.jsx", "const el = <p className=\"x\">hi</p>;\nReactDOM.createRoot(document.body).render(el);\n")))
    assert 'React.createElement("p"' in jsx["outputs"]["widget.jsx"]
    broken = transpile(_files(("app.tsx", "const n: number = <div />;\n")))
    assert broken["diagnostics"] and broken["diagnostics"][0]["file"] == "app.tsx"
