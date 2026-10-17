import pytest

from app.state.schemas import StateVector, SkillProgress
from app.agents import networking_agent, portfolio_agent, interview_agent, skill_agent
from app.agents.coordinator import allocate
from app.agents.calibration import need_from_score, momentum_bonus
from app.analysis.skill_graph import get_full_chain, get_next_skill

ROLE = "frontend_dev"
MODULES = [networking_agent, portfolio_agent, interview_agent, skill_agent]


def make_state(skills_done=1, **overrides):
    chain = get_full_chain(ROLE)
    completed = chain[:skills_done]
    base = dict(
        user_id="test",
        target_role=ROLE,
        week_number=1,
        available_hours=15,
        completed_tasks_last_week=8,
        ignored_tasks_last_week=1,
        confidence=6,
        interview_score=61,
        resume_score=60,
        networking_score=43,
        portfolio_score=53,
        streak_count=7,
        skill_progress=SkillProgress(
            completed_skills=list(completed),
            next_skill=get_next_skill(ROLE, completed),
        ),
        skill_task_progress=0,
    )
    base.update(overrides)
    return StateVector(**base)


def bids_of(state):
    return {b.agent: b for b in (m.get_bid(state) for m in MODULES)}


def hours_of(state):
    bids = list(bids_of(state).values())
    alloc = allocate(state, bids)
    return {a.agent: a.hours for a in alloc.allocations}


def test_roadmap_exists_for_role():
    assert len(get_full_chain(ROLE)) >= 2


def test_need_curve_is_bounded_and_monotonic():
    scores = [0, 10, 25, 43, 60, 70, 85, 100]
    needs = [need_from_score(s) for s in scores]
    assert all(0.0 < n <= 1.0 for n in needs)
    assert needs == sorted(needs, reverse=True)
    assert need_from_score(100) == pytest.approx(0.05)


def test_momentum_is_capped_and_zero_without_streak():
    assert momentum_bonus(0) == 0
    assert momentum_bonus(2) < momentum_bonus(4)
    assert momentum_bonus(50) == pytest.approx(0.10)


@pytest.mark.parametrize(
    "field,agent",
    [
        ("networking_score", "networking"),
        ("portfolio_score", "portfolio"),
        ("interview_score", "interview_prep"),
    ],
)
def test_domain_progress_lowers_that_agents_bid_and_hours(field, agent):
    before = make_state()
    after = make_state(**{field: getattr(before, field) + 9})

    b_before, b_after = bids_of(before), bids_of(after)
    assert b_after[agent].bid_score < b_before[agent].bid_score

    for other in b_before:
        if other != agent:
            assert b_after[other].bid_score == b_before[other].bid_score

    h_before, h_after = hours_of(before), hours_of(after)
    assert h_after[agent] <= h_before[agent] - 1
    assert sum(h_after.values()) == after.available_hours


def test_completing_a_skill_lowers_skill_bid():
    one = make_state(skills_done=1)
    two = make_state(skills_done=2)
    assert bids_of(two)["skill_building"].bid_score < bids_of(one)["skill_building"].bid_score
    assert hours_of(two)["skill_building"] <= hours_of(one)["skill_building"]


def test_task_progress_within_a_skill_never_raises_skill_bid():
    start = make_state(skill_task_progress=0)
    mid = make_state(skill_task_progress=2)
    assert bids_of(mid)["skill_building"].bid_score <= bids_of(start)["skill_building"].bid_score


def test_ignoring_tasks_ends_streak_and_removes_skill_momentum():
    streaking = make_state(streak_count=7)
    broken = make_state(streak_count=0, ignored_tasks_last_week=3)
    assert bids_of(broken)["skill_building"].bid_score < bids_of(streaking)["skill_building"].bid_score
    assert hours_of(broken)["skill_building"] <= hours_of(streaking)["skill_building"]


@pytest.mark.parametrize("hours", [5, 10, 15, 21, 40])
def test_hours_always_sum_to_budget(hours):
    assert sum(hours_of(make_state(available_hours=hours)).values()) == hours


@pytest.mark.parametrize(
    "overrides",
    [
        dict(networking_score=100, portfolio_score=100, interview_score=100, resume_score=100, confidence=10, streak_count=0),
        dict(networking_score=0, portfolio_score=0, interview_score=0, resume_score=0, confidence=0, streak_count=20),
    ],
)
def test_extreme_states_still_allocate_the_full_budget(overrides):
    state = make_state(**overrides)
    assert sum(hours_of(state).values()) == state.available_hours