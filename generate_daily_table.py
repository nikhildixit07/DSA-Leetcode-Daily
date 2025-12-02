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

This version uses LeetCode's GraphQL endpoint to reliably fetch difficulty and topic tags.
If network or GraphQL fails, it falls back to heuristics.
"""

import re
import json
import time
import argparse
from pathlib import Path
from typing import List

# Optional imports for network fetch
try:
    import requests
    HAS_REQUESTS = True
except Exception:
    HAS_REQUESTS = False

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
    # Attempt to keep capitalized acronyms intact (e.g., 'n' -> 'N')
    def cap(w):
        if len(w) == 1:
            return w.upper()
        return w.capitalize()
    return ' '.join(cap(part) for part in parts)

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

def fetch_metadata_graphql(slug: str, delay: float = 0.6) -> dict:
    """
    Fetch question metadata from LeetCode GraphQL endpoint.
    Returns: {'difficulty': 'Easy'|'Medium'|'Hard'|..., 'topics': [list of topic names]}
    Raises RuntimeError on fatal network issues.
    """
    if not HAS_REQUESTS:
        raise RuntimeError("requests is not available")

    url = "https://leetcode.com/graphql"
    # Query: get basic question fields (titleSlug -> question)
    query = """
    query getQuestionDetail($titleSlug: String!) {
      question(titleSlug: $titleSlug) {
        questionId
        title
        titleSlug
        difficulty
        topicTags {
          name
          slug
        }
      }
    }
    """
    payload = {
        "operationName": "getQuestionDetail",
        "query": query,
        "variables": {"titleSlug": slug}
    }
    headers = {
        "User-Agent": USER_AGENT,
        "Content-Type": "application/json",
        "Referer": f"https://leetcode.com/problems/{slug}/"
    }
    try:
        resp = requests.post(url, json=payload, headers=headers, timeout=10)
    except Exception as e:
        raise RuntimeError(f"Network error: {e}")

    if resp.status_code != 200:
        raise RuntimeError(f"HTTP {resp.status_code}")

    try:
        data = resp.json()
    except Exception as e:
        raise RuntimeError(f"Invalid JSON response: {e}")

    # Navigate the response
    q = data.get('data', {}).get('question')
    if not q:
        raise RuntimeError("GraphQL returned no question data")

    difficulty = q.get('difficulty') or 'Unknown'
    tgs = q.get('topicTags') or []
    topics = []
    for tg in tgs:
        name = tg.get('name') if isinstance(tg, dict) else str(tg)
        if name:
            topics.append(name)
    time.sleep(delay)
    return {'difficulty': str(difficulty).capitalize(), 'topics': topics}

def build_rows(folders: List[dict], online=True, delay=0.6) -> List[dict]:
    rows = []
    for idx, it in enumerate(folders, start=1):
        slug = it['slug']
        title = it['title']
        row = {'day': idx, 'title': title, 'slug': slug, 'folder': it['folder']}
        row['topics'] = heuristic_topics(slug)
        row['difficulty'] = 'Unknown'
        if online and HAS_REQUESTS:
            try:
                meta = fetch_metadata_graphql(slug, delay=delay)
                if meta.get('topics'):
                    row['topics'] = meta['topics']
                row['difficulty'] = meta.get('difficulty') or 'Unknown'
            except Exception as e:
                print(f"[WARN] GraphQL fetch failed for {slug}: {e} — using heuristics.")
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
        # If markers do not exist, append and add markers (explicit behavior)
        new_content = content + "\n\n" + start_marker + "\n\n" + table_md + "\n\n" + end_marker + "\n"
        readme_path.write_text(new_content, encoding='utf-8')
        print(f"Appended table to {readme_path} (markers were not found).")

def main():
    parser = argparse.ArgumentParser(description="Generate Day | Question | Topic | Level table")
    parser.add_argument("--offline", action="store_true", help="Don't fetch LeetCode GraphQL; use heuristics.")
    parser.add_argument("--insert", nargs='?', const="README.md", help="Insert into README.md between markers (default README.md).")
    parser.add_argument("--delay", type=float, default=0.6, help="Delay between requests when online (seconds)")
    args = parser.parse_args()

    folders = gather_problem_folders(ROOT)
    if not folders:
        print("No problem folders found in repo root. Make sure folders are named like '2263-maximum-running-time-of-n-computers'.")
        return

    online = (not args.offline) and HAS_REQUESTS
    if (not args.offline) and (not HAS_REQUESTS):
        print("[INFO] requests not installed — running in offline/heuristic mode.")
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
