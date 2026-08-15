from __future__ import annotations

import json
import os
import re
import urllib.request
from datetime import datetime, timezone
from pathlib import Path


USERNAME = os.environ.get("GITHUB_REPOSITORY_OWNER", "cynthia174")
TOKEN = os.environ.get("FOCUS_REPOS_TOKEN", "")
README = Path("README.md")
START = "<!-- CURRENT-FOCUS:START -->"
END = "<!-- CURRENT-FOCUS:END -->"

PROJECTS = {
    "risk-management-new": {
        "title": "Financial Risk Management System",
        "summary": "Risk analytics, delivery insights, and enterprise data integration",
    },
    "-": {
        "title": "Approval Expert Bot",
        "summary": "AI-assisted approval workflows and enterprise automation",
    },
}


def fetch_repositories() -> list[dict]:
    if TOKEN:
        url = (
            "https://api.github.com/user/repos"
            "?per_page=100&sort=pushed&direction=desc&visibility=all&affiliation=owner"
        )
    else:
        url = (
            f"https://api.github.com/users/{USERNAME}/repos"
            "?per_page=100&sort=pushed&direction=desc"
        )

    headers = {
        "Accept": "application/vnd.github+json",
        "User-Agent": f"{USERNAME}-profile-focus",
        "X-GitHub-Api-Version": "2022-11-28",
    }
    if TOKEN:
        headers["Authorization"] = f"Bearer {TOKEN}"

    request = urllib.request.Request(url, headers=headers)
    with urllib.request.urlopen(request, timeout=30) as response:
        return json.load(response)


def focus_block(repositories: list[dict]) -> str:
    by_name = {repo["name"]: repo for repo in repositories}
    ordered_names = sorted(
        PROJECTS,
        key=lambda name: by_name.get(name, {}).get("pushed_at", ""),
        reverse=True,
    )
    first, second = (PROJECTS[name] for name in ordered_names)

    rows: list[tuple[str, str]] = [
        ("🎯 Latest focus", first["title"]),
        ("🚀 Also building", second["title"]),
        ("🧠 Working on", "AI agents, workflow automation, and enterprise integrations"),
        ("⚡ Goal", "Reliable, data-safe automation for finance and approvals"),
    ]
    width = max(len(label) for label, _ in rows)
    lines = [f"{label.ljust(width)}  {value}" for label, value in rows]
    updated = datetime.now(timezone.utc).strftime("%Y-%m-%d UTC")
    lines.append(f"{'🕒 Updated'.ljust(width)}  {updated}")

    return (
        f"{START}\n"
        "## 🎯 Current Focus\n\n"
        "```text\n"
        + "\n".join(lines)
        + "\n```\n"
        f"{END}"
    )


def main() -> None:
    content = README.read_text(encoding="utf-8")
    block = focus_block(fetch_repositories())
    pattern = re.compile(rf"{re.escape(START)}.*?{re.escape(END)}", re.DOTALL)

    if pattern.search(content):
        updated = pattern.sub(block, content)
    else:
        picture = "<picture>"
        position = content.find(picture)
        if position == -1:
            updated = content.rstrip() + "\n\n" + block + "\n"
        else:
            updated = content[:position] + block + "\n\n" + content[position:]

    README.write_text(updated, encoding="utf-8", newline="\n")


if __name__ == "__main__":
    main()
