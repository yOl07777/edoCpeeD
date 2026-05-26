from __future__ import annotations


GITHUB_ACTION_SETUP_DOCS_URL = "https://docs.github.com/actions"
PR_TITLE = "Set up DeepSeek Code automation"
PR_BODY = """## Summary

Configure repository automation for DeepSeek Code.

## Notes

- Review secrets before enabling the workflow.
- Use `DEEPSEEK_API_KEY` or an approved organization secret.
- This migration shim does not create commits, push branches, or open PRs by itself.
"""
WORKFLOW_CONTENT = """name: DeepSeek Code

on:
  workflow_dispatch:
  pull_request:

jobs:
  deepseek-code:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - name: DeepSeek Code placeholder
        run: echo "Configure your DeepSeek Code workflow here"
"""
CODE_REVIEW_PLUGIN_WORKFLOW_CONTENT = WORKFLOW_CONTENT


__all__ = [
    "CODE_REVIEW_PLUGIN_WORKFLOW_CONTENT",
    "GITHUB_ACTION_SETUP_DOCS_URL",
    "PR_BODY",
    "PR_TITLE",
    "WORKFLOW_CONTENT",
]
