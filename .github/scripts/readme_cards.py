"""Refresh the profile cards from public GitHub data using the GitHub CLI."""

import json
import subprocess
from collections import Counter
from html import escape
from pathlib import Path


def api(*args):
    return json.loads(subprocess.check_output(["gh", "api", *args]))


def card(filename, title, rows):
    lines = "\n".join(
        f'<text x="20" y="{59 + i * 23}">{escape(row)}</text>'
        for i, row in enumerate(rows)
    )
    path = Path(__file__).resolve().parents[2] / "profile" / filename
    path.parent.mkdir(exist_ok=True)
    path.write_text(f'''<svg xmlns="http://www.w3.org/2000/svg" width="300" height="170" role="img">
<title>{escape(title)}</title>
<rect width="300" height="170" rx="8" fill="#161b22"/>
<g font-family="system-ui, sans-serif" font-size="15" fill="#f0f6fc">
<text x="20" y="30" fill="#79c0ff" font-size="19">{escape(title)}</text>
{lines}
</g>
</svg>
''', encoding="utf-8", newline="\n")


user = api("users/jasonmoodie")
pages = api("--paginate", "--slurp", "users/jasonmoodie/repos?type=owner&per_page=100")
repos = [r for page in pages for r in page if not r["private"] and not r["fork"]]
languages = Counter(r["language"] for r in repos if r["language"])
card("stats.svg", "GitHub stats", [
    f'Public repositories: {user["public_repos"]}',
    f'Followers: {user["followers"]}',
    f'Stars on non-fork public repos: {sum(r["stargazers_count"] for r in repos)}',
])
card("top-langs.svg", "Top languages by repository", [
    f'{name}: {count} {"repo" if count == 1 else "repos"}'
    for name, count in sorted(languages.items(), key=lambda item: (-item[1], item[0]))[:5]
])
