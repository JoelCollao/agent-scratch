from types import SimpleNamespace

from agent.domain.models import AgentReply, Intent
from agent.infrastructure.llm.foundry_chat_model import FoundryChatModel, partial_reply


def test_partial_reply_includes_the_text_still_being_written():
    assert partial_reply('{"intent": "greeting", "answer": "Ho') == {"intent": "greeting", "answer": "Ho"}
    assert partial_reply('{"intent": "salu') == {"intent": "salu"}
    assert partial_reply("") == {}


def test_parsed_completion_logs_the_last_user_message():
    model = FoundryChatModel.__new__(FoundryChatModel)
    reply = AgentReply(intent=Intent.PRODUCT_QUESTION, answer="El plazo es 60 días.", sources=[1])
    completion = SimpleNamespace(
        choices=[SimpleNamespace(message=SimpleNamespace(parsed=reply, refusal=None))],
        usage=SimpleNamespace(prompt_tokens=10, completion_tokens=5),
        model="mock",
    )

    parsed, usage = model._parsed_and_usage(
        completion,
        0,
        AgentReply,
        [{"role": "user", "content": "¿Cuál es el plazo?"}],
    )

    assert parsed == reply
    assert usage.prompt_tokens == 10
    assert usage.completion_tokens == 5