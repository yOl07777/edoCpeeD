from deepseek_code.core.prompt_builder import PromptAdapter
from deepseek_code.core.response_adapter import ResponseAdapter, StreamingToolCallAccumulator
from deepseek_code.core.tool_adapter import claude_tool_to_deepseek
from deepseek_code.core.types import InternalMessage


def test_system_is_first_message_and_cache_controls_are_removed():
    messages = PromptAdapter.from_claude(
        system="You are helpful.",
        messages=[
            {
                "role": "user",
                "content": [
                    {"type": "text", "text": "Hello", "cache_control": {"type": "ephemeral"}}
                ],
            }
        ],
    )

    request = PromptAdapter.build_request(messages, model="deepseek-chat")

    assert request["messages"][0] == {"role": "system", "content": "You are helpful."}
    assert request["messages"][1]["content"] == [{"type": "text", "text": "Hello"}]


def test_claude_tool_schema_converts_to_openai_function_tool():
    tool = {
        "name": "read_file",
        "description": "Read a file",
        "input_schema": {"type": "object", "properties": {"path": {"type": "string"}}},
    }

    assert claude_tool_to_deepseek(tool) == {
        "type": "function",
        "function": {
            "name": "read_file",
            "description": "Read a file",
            "parameters": {"type": "object", "properties": {"path": {"type": "string"}}},
        },
    }


def test_completion_response_parses_tool_calls():
    response = ResponseAdapter.from_completion(
        {
            "choices": [
                {
                    "message": {
                        "role": "assistant",
                        "content": None,
                        "tool_calls": [
                            {
                                "id": "call_1",
                                "type": "function",
                                "function": {"name": "read_file", "arguments": "{\"path\":\"a.py\"}"},
                            }
                        ],
                    },
                    "finish_reason": "tool_calls",
                }
            ],
            "usage": {"total_tokens": 10},
        }
    )

    assert response.finish_reason == "tool_calls"
    assert response.message.tool_calls[0].name == "read_file"


def test_streaming_tool_call_arguments_are_accumulated():
    acc = StreamingToolCallAccumulator()
    acc.add_delta(
        [
            {
                "index": 0,
                "id": "call_1",
                "type": "function",
                "function": {"name": "read_file", "arguments": "{\"path\""},
            }
        ]
    )
    acc.add_delta([{"index": 0, "function": {"arguments": ":\"a.py\"}"}}])

    call = acc.complete_calls()[0]
    assert call.id == "call_1"
    assert call.name == "read_file"
    assert call.arguments == {"path": "a.py"}


def test_tool_result_wire_message_uses_role_tool():
    wire = PromptAdapter.message_to_wire(
        InternalMessage(role="tool", content="done", tool_call_id="call_1")
    )

    assert wire == {"role": "tool", "content": "done", "tool_call_id": "call_1"}
