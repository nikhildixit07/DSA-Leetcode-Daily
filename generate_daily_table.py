"""
generate_daily_table.py

Scans repository root for LeetCode Daily problem folders named like:
  2263-maximum-running-time-of-n-computers/

Generates a Markdown table with columns:
  Day | Question (hyperlink) | Topic(s) | Level

Outputs:
 - DAILY_PROBLEMS_TABLE.md (always)
 - Optionally inserts the table into README.md between markers:
     <!-- START_PROBLEM_TABLE -->
     <!-- END_PROBLEM_TABLE -->

Usage:
  python generate_daily_table.py            # tries online lookup (if requests + bs4 installed)
  python generate_daily_table.py --offline  # offline heuristics only
  python generate_daily_table.py --insert README.md  # insert into README.md

Recommended workflow step for GitHub Actions:
  python generate_daily_table.py --insert README.md

Dependencies for online mode (optional):
  pip install requests beautifulsoup4
"""

import re
import json
import time
import argparse
from pathlib import Path
from typing import List

# Optional imports for online metadata fetch
try:
    import requests
    from bs4 import BeautifulSoup
    HAS_NETWORK = True
except Exception:
    HAS_NETWORK = False

ROOT = Path('.').resolve()
FOLDER_RE = re.compile(r'^\s*(\d+)[-_](.+)$')
USER_AGENT = "Mozilla/5.0 (compatible; LeetTable/1.0; +https://github.com/)"

# Heuristic keyword -> topic mapping (fallback)
KEYWORD_TOPICS = {
    'linked': 'Linked List',
    'list': 'Linked List',
    'tree': 'Tree',
    'binary-tree': 'Tree',
    'bst': 'BST',
    'binary-search-tree': 'BST',
    'graph': 'Graph',
    'matrix': 'Matrix',
    'array': 'Array',
    'string': 'String',
    'hash': 'Hash / Map',
    'map': 'Hash / Map',
    'set': 'Hash / Set',
    'stack': 'Stack',
    'queue': 'Queue',
    'dp': 'Dynamic Programming',
    'greedy': 'Greedy',
    'two-pointer': 'Two Pointers',
    'sliding-window': 'Sliding Window',
    'bit': 'Bit Manipulation',
    'xor': 'Bit Manipulation',
    'math': 'Math',
    'sort': 'Sorting',
    'search': 'Binary Search',
    'heap': 'Heap / Priority Queue',
    'kth': 'Heap / Selection',
    'palindrome': 'String',
    'gcd': 'GCD / Number Theory',
    'lcm': 'LCM / Number Theory',
}

def slug_to_title(slug: str) -> str:
    parts = [p for p in slug.split('-') if p]
    return ' '.join(part.capitalize() for part in parts)

def infer_slug_from_folder(folder_name: str) -> str:
    m = FOLDER_RE.match(folder_name)
    if m:
        return m.group(2).strip()
    return folder_name.replace(' ', '-')

def gather_problem_folders(root: Path) -> List[dict]:
    items = []
    for child in sorted(root.iterdir()):
        if not child.is_dir():
            continue
        name = child.name
        if name.startswith('.') or name.lower() in ('venv', 'env', '__pycache__'):
            continue
        m = FOLDER_RE.match(name)
        idnum = int(m.group(1)) if m else None
        slug = infer_slug_from_folder(name)
        title = slug_to_title(slug)
        items.append({'folder': name, 'id': idnum, 'slug': slug, 'title': title})
    items.sort(key=lambda x: (x['id'] is None, x['id'] if x['id'] is not None else x['folder']))
    return items

def heuristic_topics(slug: str) -> List[str]:
    s = slug.lower()
    topics = []
    for k, v in KEYWORD_TOPICS.items():
        if k in s and v not in topics:
            topics.append(v)
    return topics or ['Misc']

def fetch_metadata_from_leetcode(slug: str, delay: float = 1.0) -> dict:
    """Best-effort fetch of difficulty and topic tags from LeetCode page JSON (__NEXT_DATA__)."""
    if not HAS_NETWORK:
        raise RuntimeError("requests/bs4 not installed")
    url = f"https://leetcode.com/problems/{slug}/"
    headers = {'User-Agent': USER_AGENT}
    resp = requests.get(url, headers=headers, timeout=10)
    if resp.status_code != 200:
        raise RuntimeError(f"HTTP {resp.status_code} fetching {url}")
    soup = BeautifulSoup(resp.text, 'html.parser')
    script = soup.find('script', id="__NEXT_DATA__")
    if not script:
        raise RuntimeError("Couldn't find __NEXT_DATA__ in page")
    data = json.loads(script.string)
    difficulty = None
    topics = []
    try:
        queries = data.get('props', {}).get('pageProps', {}).get('dehydratedState', {}).get('queries', [])
        for q in queries:
            st = q.get('state', {}).get('data')
            if not st:
                continue
            question = None
            if isinstance(st, dict) and 'question' in st:
                question = st['question']
            elif isinstance(st, dict) and 'difficulty' in st:
                question = st
            if question:
                difficulty = question.get('difficulty') or question.get('difficultyLevel') or question.get('level')
                tgs = question.get('topicTags') or question.get('topics') or []
                for tg in tgs:
                    if isinstance(tg, dict):
                        name = tg.get('name') or tg.get('slug')
                        if name:
                            topics.append(name.capitalize())
                    elif isinstance(tg, str):
                        topics.append(tg.capitalize())
                break
    except Exception:
        pass
    # fallback top-level
    try:
        qtop = data.get('props', {}).get('pageProps', {}).get('question')
        if qtop and isinstance(qtop, dict):
            if not difficulty:
                difficulty = qtop.get('difficulty')
            if not topics:
                tgs = qtop.get('topicTags') or qtop.get('topics') or []
                for tg in tgs:
                    if isinstance(tg, dict):
                        topics.append(tg.get('name', '').capitalize())
                    else:
                        topics.append(str(tg).capitalize())
    except Exception:
        pass
    difficulty = str(difficulty).capitalize() if difficulty else 'Unknown'
    topics = sorted(set([t for t in topics if t])) or []
    time.sleep(delay)
    return {'difficulty': difficulty, 'topics': topics}

def build_rows(folders: List[dict], online=True, delay=1.0) -> List[dict]:
    rows = []
    for idx, it in enumerate(folders, start=1):
        slug = it['slug']
        title = it['title']
        row = {'day': idx, 'title': title, 'slug': slug, 'folder': it['folder']}
        row['topics'] = heuristic_topics(slug)
        row['difficulty'] = 'Unknown'
        if online and HAS_NETWORK:
            try:
                meta = fetch_metadata_from_leetcode(slug, delay=delay)
                if meta.get('topics'):
                    row['topics'] = meta['topics']
                row['difficulty'] = meta.get('difficulty') or 'Unknown'
            except Exception as e:
                print(f"[WARN] fetch failed for {slug}: {e}. Using heuristics.")
        rows.append(row)
    return rows

def render_markdown_table(rows: List[dict]) -> str:
    lines = []
    lines.append("| Day | Question | Topic(s) | Level |")
    lines.append("|---:|---|---|---|")
    for r in rows:
        day = f"Day {r['day']}"
        link = f"https://leetcode.com/problems/{r['slug']}/"
        qmd = f"[{r['title']}]({link})"
        topics = ", ".join(r.get('topics') or ['Misc'])
        level = r.get('difficulty') or 'Unknown'
        lines.append(f"| {day} | {qmd} | {topics} | {level} |")
    return "\n".join(lines)

def insert_into_readme(readme_path: Path, table_md: str):
    start_marker = "<!-- START_PROBLEM_TABLE -->"
    end_marker = "<!-- END_PROBLEM_TABLE -->"
    content = readme_path.read_text(encoding='utf-8') if readme_path.exists() else ""
    if start_marker in content and end_marker in content:
        before, rest = content.split(start_marker, 1)
        _, after = rest.split(end_marker, 1)
        new_content = before + start_marker + "\n\n" + table_md + "\n\n" + end_marker + after
        readme_path.write_text(new_content, encoding='utf-8')
        print(f"Inserted table into {readme_path} between markers.")
    else:
        new_content = content + "\n\n" + start_marker + "\n\n" + table_md + "\n\n" + end_marker + "\n"
        readme_path.write_text(new_content, encoding='utf-8')
        print(f"Appended table to {readme_path} (markers were not found).")

def main():
    parser = argparse.ArgumentParser(description="Generate Day | Question | Topic | Level table")
    parser.add_argument("--offline", action="store_true", help="Don't fetch LeetCode pages; use heuristics.")
    parser.add_argument("--insert", nargs='?', const="README.md", help="Insert into README.md between markers (default README.md).")
    parser.add_argument("--delay", type=float, default=1.0, help="Delay between requests when online")
    args = parser.parse_args()

    folders = gather_problem_folders(ROOT)
    if not folders:
        print("No problem folders found in repo root. Make sure folders are named like '2263-maximum-running-time-of-n-computers'.")
        return

    online = (not args.offline) and HAS_NETWORK
    if (not args.offline) and (not HAS_NETWORK):
        print("[INFO] requests/bs4 not installed — running in offline/heuristic mode.")
        online = False

    rows = build_rows(folders, online=online, delay=args.delay)
    md = render_markdown_table(rows)
    out = ROOT / "DAILY_PROBLEMS_TABLE.md"
    out.write_text(md + "\n", encoding='utf-8')
    print(f"Wrote {out}")
    print(md)

    if args.insert:
        insert_into_readme(Path(args.insert), md)

if __name__ == "__main__":
    main()
