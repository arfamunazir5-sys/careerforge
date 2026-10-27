import re
import requests
from app.analysis.schemas import PortfolioScanResult

GITHUB_API_BASE = "https://api.github.com"
USERNAME_PATTERN = re.compile(r"^[A-Za-z0-9-]{1,39}$")


class PortfolioScanError(Exception):
    """Raised when GitHub data cannot be fetched. Carries the HTTP status the
    API should answer with, so a failed scan never overwrites a real score."""

    def __init__(self, message: str, status_code: int = 502):
        super().__init__(message)
        self.status_code = status_code


def scan_portfolio(github_username: str) -> PortfolioScanResult:
    username = github_username.strip()
    if not username:
        raise PortfolioScanError("Enter a GitHub username.", 422)
    if not USERNAME_PATTERN.match(username):
        raise PortfolioScanError("That does not look like a valid GitHub username.", 422)

    repos_url = f"{GITHUB_API_BASE}/users/{username}/repos?per_page=100"
    try:
        response = requests.get(repos_url, timeout=10)
    except requests.RequestException:
        raise PortfolioScanError("Could not reach GitHub. Try again in a minute.", 502)

    if response.status_code == 404:
        raise PortfolioScanError(f"GitHub user '{username}' was not found. Check the username.", 404)
    if response.status_code in (403, 429):
        raise PortfolioScanError(
            "GitHub rate limit reached. Your portfolio score was not changed. Try again later.", 502
        )
    if response.status_code != 200:
        raise PortfolioScanError(
            f"GitHub returned status {response.status_code}. Your portfolio score was not changed.", 502
        )

    repos = response.json()
    non_fork_repos = [r for r in repos if not r.get("fork")]
    repo_count = len(non_fork_repos)

    if repo_count == 0:
        return PortfolioScanResult(
            portfolio_score=10,
            repo_count=0,
            readme_ratio=0.0,
            notes=["No original public repositories found."],
        )

    repos_with_description = [r for r in non_fork_repos if r.get("description")]
    readme_ratio = round(len(repos_with_description) / repo_count, 2)

    notes = []
    if repo_count < 3:
        notes.append("Fewer than 3 original projects - consider adding more.")
    if readme_ratio < 0.5:
        notes.append("Many repos are missing descriptions.")
    if not notes:
        notes.append("Portfolio looks reasonably active.")

    repo_count_score = min(1.0, repo_count / 5)
    portfolio_score = round((repo_count_score * 0.6 + readme_ratio * 0.4) * 100)

    return PortfolioScanResult(
        portfolio_score=portfolio_score,
        repo_count=repo_count,
        readme_ratio=readme_ratio,
        notes=notes,
    )