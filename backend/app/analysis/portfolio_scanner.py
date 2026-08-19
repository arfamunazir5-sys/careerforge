import requests
from app.analysis.schemas import PortfolioScanResult

GITHUB_API_BASE = "https://api.github.com"


def scan_portfolio(github_username: str) -> PortfolioScanResult:
    repos_url = f"{GITHUB_API_BASE}/users/{github_username}/repos?per_page=100"
    response = requests.get(repos_url, timeout=10)

    if response.status_code != 200:
        return PortfolioScanResult(
            portfolio_score=0,
            repo_count=0,
            readme_ratio=0.0,
            notes=[f"Could not fetch GitHub data (status {response.status_code}). Check the username."],
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
        notes.append("Many repos are missing descriptions/READMEs.")
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