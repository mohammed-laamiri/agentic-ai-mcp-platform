"""
Unit tests for PlannerAgent.

Covers SINGLE_AGENT vs MULTI_AGENT selection and _assign_agents.
"""

from app.services.planner_agent import PlannerAgent
from app.schemas.agent import AgentRead
from app.schemas.task import TaskCreate
from app.schemas.execution_strategy import ExecutionStrategy


def test_plan_simple_task_returns_single_agent():
    """Simple task description yields SINGLE_AGENT plan."""
    planner = PlannerAgent()
    agent = AgentRead(id="a1", name="Agent1")
    task = TaskCreate(name="Task", description="Do something simple")
    plan = planner.plan_sync(agent=agent, task=task)
    assert plan.strategy == ExecutionStrategy.SINGLE_AGENT
    assert plan.steps is None


def test_plan_complex_task_returns_multi_agent():
    """Description with complex keywords yields MULTI_AGENT plan."""
    planner = PlannerAgent()
    agent = AgentRead(id="a1", name="Agent1")
    task = TaskCreate(name="Task", description="Analyze the market and compare results")
    plan = planner.plan_sync(agent=agent, task=task)
    assert plan.strategy == ExecutionStrategy.MULTI_AGENT
    assert plan.steps is not None
    assert len(plan.steps) >= 2


def test_plan_research_keyword_triggers_multi_agent():
    """Keyword 'research' triggers MULTI_AGENT."""
    planner = PlannerAgent()
    agent = AgentRead(id="a1", name="A1")
    task = TaskCreate(name="T", description="Research the topic")
    plan = planner.plan_sync(agent=agent, task=task)
    assert plan.strategy == ExecutionStrategy.MULTI_AGENT


def test_assign_agents_returns_lead_agent_twice():
    """_assign_agents returns [lead_agent, lead_agent] as placeholder."""
    planner = PlannerAgent()
    agent = AgentRead(id="lead", name="Lead")
    task = TaskCreate(name="T", description="Complex task")
    steps = planner._assign_agents(task=task, lead_agent=agent)
    assert len(steps) == 2
    assert steps[0].id == steps[1].id == "lead"


def test_assign_tools_returns_empty_list():
    """_assign_tools is a hook that returns empty list."""
    planner = PlannerAgent()
    agent = AgentRead(id="a1", name="A1")
    task = TaskCreate(name="T", description="Task")
    tools = planner._assign_tools(task=task, agent=agent)
    assert tools == []
