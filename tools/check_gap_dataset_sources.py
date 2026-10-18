"""Check public provenance URLs; never downloads whole referenced documents."""
import concurrent.futures
import json
import re
import ssl
from datetime import datetime, timezone
from pathlib import Path
from urllib.error import HTTPError
from urllib.parse import urlparse
from urllib.request import Request, urlopen

ROOT = Path(__file__).resolve().parents[2]
PACKAGE = ROOT / 'Training Data/generated/knowledge-gap-fill-v1'
if (Path(__file__).resolve().parents[1] / 'manifest.json').exists():
    PACKAGE = Path(__file__).resolve().parents[1]


def check(url):
    try:
        request = Request(url, headers={'User-Agent': 'KnowledgeDatasetSourceCheck/1.0', 'Range': 'bytes=0-8191'})
        with urlopen(request, timeout=18, context=ssl.create_default_context()) as response:
            sample = response.read(8192).decode('utf-8', errors='ignore')
            title = re.search(r'<title[^>]*>(.*?)</title>', sample, re.S | re.I)
            title = re.sub(r'\s+', ' ', title.group(1)).strip() if title else ''
            return {'url': url, 'status': response.status, 'final_url': response.geturl(), 'title': title,
                    'result': 'reachable', 'anchor_verified': False, 'claims_verified': False}
    except HTTPError as exc:
        return {'url': url, 'status': exc.code, 'result': 'http_error', 'error': str(exc)}
    except Exception as exc:
        return {'url': url, 'result': 'not_confirmed', 'error': str(exc)[:200]}


if __name__ == '__main__':
    urls = sorted({url for line in (PACKAGE / 'all_records.jsonl').open() for url in json.loads(line)['provenance']})
    if any(urlparse(u).scheme != 'https' or not urlparse(u).hostname for u in urls):
        raise SystemExit('Non-HTTPS/invalid provenance URL')
    output = PACKAGE / 'evaluation/source-link-check.json'
    today = datetime.now(timezone.utc).date().isoformat()
    previous = json.loads(output.read_text()) if output.exists() else {}
    cached = {r['url']: r for r in previous.get('results', []) if r['result'] == 'reachable'} if previous.get('checked_on') == today else {}
    remaining = [u for u in urls if u not in cached]
    with concurrent.futures.ThreadPoolExecutor(max_workers=8) as pool:
        fresh = {r['url']: r for r in pool.map(check, remaining)}
    results = [cached[u] if u in cached else fresh[u] for u in urls]
    report = {'checked_on': today, 'urls': len(urls), 'reachable': sum(r['result'] == 'reachable' for r in results),
              'limitations': ['HTTP reachability does not certify claims or fragment anchors.', 'No third-party document text is included in the dataset.'],
              'results': results}
    (PACKAGE / 'evaluation').mkdir(exist_ok=True)
    (PACKAGE / 'evaluation/source-link-check.json').write_text(json.dumps(report, indent=2) + '\n')
    print(json.dumps({'urls': len(urls), 'reachable': report['reachable'],
                      'unconfirmed': [r for r in results if r['result'] != 'reachable']}, indent=2))
