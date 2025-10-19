# GitHub Repo Fetcher

A small command-line utility to search GitHub users, list their public repositories, show repository details (stars, forks, primary language, open issues, license) and optionally export the results to a JSON file.

> **Note:** This tool can use an authenticated GitHub token (recommended) to raise the rate limit (5,000 requests/hr). **Do not** hardcode your token in source files. Use an environment variable or secure secret manager.

---

## Features

* Search GitHub users by username or name (returns top results).
* Choose a user interactively from search results.
* Fetch all public repositories for the chosen user (handles pagination).
* Retrieve languages used in each repository.
* Display repository metadata (description, stars, forks, last updated, URL, issues, license).
* Export repository list and metadata to a JSON file.
* Simple, interactive CLI workflow.

---

## Requirements

* Python 3.8+
* `requests` library

Install dependencies:

```bash
pip install requests
```

---

## Installation

1. Clone or copy the script into a file, for example `github_repo_fetcher.py`.
2. Make the script executable (optional):

```bash
chmod +x github_repo_fetcher.py
```

3. Install dependencies:

```bash
pip install requests
```

---

## Usage

### Configure GitHub token (recommended)

Create a Personal Access Token (PAT) on GitHub with `public_repo` permissions or `repo` scope if you need additional access. Never commit this token to source control.

Set the token in an environment variable:

**Linux / macOS**

```bash
export GITHUB_TOKEN="ghp_xxx..."
```

**Windows (PowerShell)**

```powershell
$env:GITHUB_TOKEN="ghp_xxx..."
```

> The script supports passing a token to the constructor. If you keep using the script directly, update it to read from `os.environ['GITHUB_TOKEN']` rather than hardcoding.

### Run

```bash
python github_repo_fetcher.py
```

Follow the interactive prompts:

* Choose `1` to search for a GitHub user.
* Enter a search string (username or real name).
* Select one of the returned users by number.
* The program fetches and displays repository details and optionally exports to JSON.

---

## Exported JSON format

When you export repositories to a JSON file, the structure is:

```json
{
  "username": "octocat",
  "fetched_at": "2025-06-01 12:34:56",
  "total_repositories": 12,
  "repositories": [
    {
      "name": "hello-world",
      "description": "My example repo",
      "url": "https://github.com/octocat/hello-world",
      "stars": 42,
      "forks": 4,
      "updated_at": "2025-06-01T08:25:00Z",
      "primary_language": "Python",
      "languages": ["Python", "HTML", "CSS"],
      "has_issues": true,
      "open_issues": 0,
      "license": "MIT License"
    },
    ...
  ]
}
```

---

## Security & Best Practices

* **Never** hardcode tokens in source code (the sample script contains a token placeholder; remove it).
* Prefer storing tokens in environment variables or secure vaults.
* Rotate tokens regularly.
* Limit token scopes: grant only the permissions you need.
* If you accidentally commit a token, revoke it immediately via GitHub settings.

---

## Configuration Tips / Improvements

If you want to make the script more robust or reusable:

* Read the GitHub token from the `GITHUB_TOKEN` environment variable:

  ```python
  import os
  token = os.getenv("GITHUB_TOKEN")
  fetcher = GitHubRepoFetcher(token=token)
  ```
* Add command-line flags (using `argparse`) to run non-interactively (e.g., `--user username --export filename.json`).
* Rate-limit handling: implement exponential backoff and respect `X-RateLimit-Remaining` and `X-RateLimit-Reset` headers.
* Use caching for repeated language lookups to reduce API calls.
* Add retry logic for transient network failures.
* Add unit tests for parsing and export functions.

---

## Troubleshooting

* **403 Forbidden / Rate limited** — You are likely hitting the GitHub API rate limit. Use an authenticated token or wait until rate limit resets.
* **Network errors** — Ensure your machine has network access and GitHub is reachable.
* **Empty search results** — Try broader search, or search using exact username.

---

## Example: Non-interactive usage (suggested pattern)

Below is a suggested small wrapper to quickly fetch and export repositories for a single user without interactivity:

```python
import os
from github_repo_fetcher import GitHubRepoFetcher

token = os.getenv("GITHUB_TOKEN")
fetcher = GitHubRepoFetcher(token=token)

username = "octocat"
repos = fetcher.get_user_repos(username)
fetcher.export_to_json(repos, username, filename=f"{username}_repos.json")
```

---

## License

This project is provided under the MIT License. Use, modify and distribute freely. (Add a `LICENSE` file if publishing.)

---

## Contributing

* Fix bugs, improve error handling, or add features (CLI flags, caching).
* Open a pull request with a clear description of changes.

---

## Contact

If you need help adapting this utility for automation, batching multiple users, or integrating into a larger pipeline, open an issue or contact the maintainer.

