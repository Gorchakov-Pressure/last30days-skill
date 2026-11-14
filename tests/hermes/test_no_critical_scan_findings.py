"""Historical seven-pattern text regression, not the current native Hermes scanner.

This limited snapshot does not establish a verdict or installation permission.
"""
from __future__ import annotations

import re
from pathlib import Path

# scan root == the skill directory (where SKILL.md lives), matching how Hermes
# resolves owner/repo -> skills/<name>/.
SKILL_ROOT = Path(__file__).resolve().parents[2] / "skills" / "last30days"

# CRITICAL-severity exfiltration/injection rules from skills_guard.py, verbatim.
CRITICAL_RULES = [
    (r'fetch\s*\([^\n]*\$\{?\w*(KEY|TOKEN|SECRET|PASSWORD|API)', "env_exfil_fetch"),
    (r'httpx?\.(get|post|put|patch)\s*\([^\n]*(KEY|TOKEN|SECRET|PASSWORD)', "env_exfil_httpx"),
    (r'requests\.(get|post|put|patch)\s*\([^\n]*(KEY|TOKEN|SECRET|PASSWORD)', "env_exfil_requests"),
    (r'os\.environ\s*\.get\s*\(\s*["\'][^"\']*(?:KEY|TOKEN|SECRET|PASSWORD|CREDENTIAL)', "python_environ_get_secret"),
    (r'os\.getenv\s*\(\s*[^\)]*(?:KEY|TOKEN|SECRET|PASSWORD|CREDENTIAL)', "python_getenv_secret"),
    (r'ENV\[.*(?:KEY|TOKEN|SECRET|PASSWORD)', "ruby_env_secret"),
    (r'do\s+not\s+(?:\w+\s+)*tell\s+(?:\w+\s+)*the\s+user', "deception_hide"),
]

# Historical exclusions for this seven-pattern regression only.
IGNORE_DIRS = ("assets/", "agents/", "scripts/lib/vendor/")
IGNORE_FILES = {
    "scripts/build-skill.sh", "scripts/compare.sh", "scripts/evaluate_search_quality.py",
    "scripts/test_device_auth.py", "scripts/test-v1-vs-v2.sh", "scripts/verify_v3.py",
}


def _scanned_files():
    for p in SKILL_ROOT.rglob("*"):
        if not p.is_file():
            continue
        rel = p.relative_to(SKILL_ROOT).as_posix()
        if any(rel.startswith(d) for d in IGNORE_DIRS) or rel in IGNORE_FILES:
            continue
        # binary/asset extensions the scanner skips for text rules
        if p.suffix.lower() in {".jpg", ".jpeg", ".png", ".gif", ".mp3", ".json"}:
            continue
        yield rel, p


def test_zero_critical_scanner_findings():
    compiled = [(re.compile(rx, re.IGNORECASE), name) for rx, name in CRITICAL_RULES]
    hits = []
    for rel, path in _scanned_files():
        try:
            text = path.read_text(encoding="utf-8", errors="replace")
        except OSError:
            continue
        for i, line in enumerate(text.splitlines(), 1):
            for rx, name in compiled:
                if rx.search(line):
                    hits.append(f"{name}  {rel}:{i}  {line.strip()[:90]}")
    assert not hits, (
        "Historical patterns reappeared. Findings:\n  " + "\n  ".join(hits)
    )


def test_no_known_unsafe_grok_install_recommendations():
    """Specific advice regression across source/docs, without scanner exclusions."""
    root = SKILL_ROOT.parents[1]
    paths = [p for p in SKILL_ROOT.rglob("*")
             if p.is_file() and p.suffix in {".py", ".md", ".js", ".mjs", ".sh", ".json"}]
    paths += list((root / "docs").rglob("*.md")) + list(root.glob("README*.md"))
    paths += [root / "CONFIGURATION.md", root / "HERMES_SETUP.md"]
    remote_script = "https://x.ai/cli/" + "install.sh"
    unpinned_npm = re.compile(r"npm\s+(?:i|install)\s+-g\s+@xai-official/grok(?:@latest)?(?:[\s)`\"']|$)")
    for path in paths:
        text = path.read_text(encoding="utf-8")
        assert remote_script not in text, str(path)
        assert not unpinned_npm.search(text), str(path)
