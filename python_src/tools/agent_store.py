from __future__ import annotations

from dataclasses import dataclass, field
from itertools import count
from typing import Any


_AGENT_IDS = count(1)
_TEAM_IDS = count(1)
_MESSAGE_IDS = count(1)
_QUESTION_IDS = count(1)


@dataclass
class AgentRecord:
    id: str
    name: str
    prompt: str
    status: str = "idle"
    messages: list[dict[str, Any]] = field(default_factory=list)

    def to_dict(self) -> dict[str, Any]:
        return {
            "id": self.id,
            "name": self.name,
            "prompt": self.prompt,
            "status": self.status,
            "messages": list(self.messages),
        }


@dataclass
class TeamRecord:
    id: str
    name: str
    agent_ids: list[str] = field(default_factory=list)

    def to_dict(self) -> dict[str, Any]:
        return {"id": self.id, "name": self.name, "agent_ids": list(self.agent_ids)}


@dataclass
class QuestionRecord:
    id: str
    question: str
    choices: list[str] = field(default_factory=list)
    answer: str | None = None

    def to_dict(self) -> dict[str, Any]:
        return {
            "id": self.id,
            "question": self.question,
            "choices": list(self.choices),
            "answer": self.answer,
        }


AGENTS: dict[str, AgentRecord] = {}
TEAMS: dict[str, TeamRecord] = {}
QUESTIONS: dict[str, QuestionRecord] = {}


def create_agent(name: str, prompt: str) -> AgentRecord:
    agent = AgentRecord(id=f"agent_{next(_AGENT_IDS)}", name=name, prompt=prompt)
    AGENTS[agent.id] = agent
    return agent


def get_agent(agent_id: str) -> AgentRecord:
    try:
        return AGENTS[agent_id]
    except KeyError as exc:
        raise KeyError(f"Unknown agent id: {agent_id}") from exc


def create_team(name: str, agent_ids: list[str] | None = None) -> TeamRecord:
    agent_ids = agent_ids or []
    for agent_id in agent_ids:
        get_agent(agent_id)
    team = TeamRecord(id=f"team_{next(_TEAM_IDS)}", name=name, agent_ids=list(agent_ids))
    TEAMS[team.id] = team
    return team


def delete_team(team_id: str) -> TeamRecord:
    try:
        return TEAMS.pop(team_id)
    except KeyError as exc:
        raise KeyError(f"Unknown team id: {team_id}") from exc


def send_message(target_id: str, content: str, *, sender: str = "user") -> dict[str, Any]:
    message = {"id": f"msg_{next(_MESSAGE_IDS)}", "sender": sender, "content": content}
    if target_id in AGENTS:
        AGENTS[target_id].messages.append(message)
    elif target_id in TEAMS:
        for agent_id in TEAMS[target_id].agent_ids:
            AGENTS[agent_id].messages.append(message)
    else:
        raise KeyError(f"Unknown target id: {target_id}")
    return message


def create_question(question: str, choices: list[str] | None = None) -> QuestionRecord:
    record = QuestionRecord(id=f"question_{next(_QUESTION_IDS)}", question=question, choices=choices or [])
    QUESTIONS[record.id] = record
    return record


def answer_question(question_id: str, answer: str) -> QuestionRecord:
    try:
        question = QUESTIONS[question_id]
    except KeyError as exc:
        raise KeyError(f"Unknown question id: {question_id}") from exc
    question.answer = answer
    return question


def clear_agent_state() -> None:
    AGENTS.clear()
    TEAMS.clear()
    QUESTIONS.clear()
