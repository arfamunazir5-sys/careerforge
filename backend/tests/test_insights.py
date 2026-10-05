from app.state.state_builder import get_current_state
from app.agents import skill_agent, networking_agent, portfolio_agent, interview_agent
from app.agents.coordinator import allocate
from app.insights.career_health import compute_career_health
from app.insights.explainability import generate_explanations
from app.insights.career_health import compute_biggest_opportunity


def _get_bids(state):
    return [
        skill_agent.get_bid(state),
        networking_agent.get_bid(state),
        portfolio_agent.get_bid(state),
        interview_agent.get_bid(state),
    ]


def test_career_health_score_is_valid():
    state = get_current_state()
    result = compute_career_health(state)

    assert 0 <= result.overall_score <= 100
    assert len(result.modules) == 4
    for module in result.modules:
        assert 0 <= module.score <= 100
    print(f"overall_score={result.overall_score}")


def test_explanations_cover_all_agents():
    state = get_current_state()
    bids = _get_bids(state)
    allocation = allocate(state, bids)
    result = generate_explanations(state, bids, allocation)

    assert len(result.items) == 4
    for item in result.items:
        assert item.explanation != ""
        assert "%" in item.explanation  # role weight percentage now mentioned
        print(f"{item.agent}: {item.explanation}")

def test_biggest_opportunity_picks_lowest_score():
    state = get_current_state()
    result = compute_biggest_opportunity(state)

    scores = {
        "Resume": state.resume_score,
        "Portfolio": state.portfolio_score,
        "Networking": state.networking_score,
        "Interview": state.interview_score,
    }
    assert result.score == min(scores.values())
    assert result.module in scores
    assert result.note != ""
    print(f"biggest_opportunity={result.module} ({result.score}): {result.note}")