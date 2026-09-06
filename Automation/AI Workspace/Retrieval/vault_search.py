from pathlib import Path
import re

VAULT = Path(r"D:\OBSIDIAN VAULT\halal-trading-os")

EXCLUDED = {
    ".git",
    ".obsidian",
    "Assets",
    "Attachments",
    "Archive",
}

def search_vault(query, max_results=10):
    query = query.lower().strip()
    terms = re.findall(r"\w+", query)

    results = []

    for path in VAULT.rglob("*.md"):
        if any(part in EXCLUDED for part in path.parts):
            continue

        try:
            text = path.read_text(encoding="utf-8")
        except Exception:
            continue

        lower = text.lower()

        score = 0
        for term in terms:
            score += lower.count(term)

        if score > 0:
            results.append((score, path, text))

    results.sort(key=lambda x: x[0], reverse=True)

    output = []

    for score, path, text in results[:max_results]:
        lines = text.splitlines()

        matching_lines = []
        for i, line in enumerate(lines):
            if any(term in line.lower() for term in terms):
                start = max(0, i - 2)
                end = min(len(lines), i + 3)
                matching_lines.extend(lines[start:end])

        output.append({
            "score": score,
            "file": str(path.relative_to(VAULT)),
            "content": "\n".join(dict.fromkeys(matching_lines))
        })

    return output


if __name__ == "__main__":
    query = input("Search vault: ")

    results = search_vault(query)

    if not results:
        print("\nNo results found.")
    else:
        print(f"\nFound {len(results)} result(s):\n")

        for i, result in enumerate(results, 1):
            print("=" * 80)
            print(f"RESULT {i}")
            print(f"Score: {result['score']}")
            print(f"File: {result['file']}")
            print("-" * 80)
            print(result["content"])
            print()