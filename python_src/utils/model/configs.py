from __future__ import annotations


DEEPSEEK_CHAT_CONFIG = {
    "id": "deepseek-chat",
    "key": "deepseek-chat",
    "display_name": "DeepSeek Chat",
    "family": "chat",
    "context_window": 64_000,
    "supports_tools": True,
    "supports_vision": False,
    "supports_streaming": True,
}
DEEPSEEK_CODER_CONFIG = {
    "id": "deepseek-coder",
    "key": "deepseek-coder",
    "display_name": "DeepSeek Coder",
    "family": "coder",
    "context_window": 64_000,
    "supports_tools": True,
    "supports_vision": False,
    "supports_streaming": True,
}
DEEPSEEK_REASONER_CONFIG = {
    "id": "deepseek-reasoner",
    "key": "deepseek-reasoner",
    "display_name": "DeepSeek Reasoner",
    "family": "reasoner",
    "context_window": 64_000,
    "supports_tools": False,
    "supports_vision": False,
    "supports_streaming": True,
}

ALL_MODEL_CONFIGS = {
    "deepseek-chat": DEEPSEEK_CHAT_CONFIG,
    "deepseek-coder": DEEPSEEK_CODER_CONFIG,
    "deepseek-reasoner": DEEPSEEK_REASONER_CONFIG,
}
CANONICAL_MODEL_IDS = list(ALL_MODEL_CONFIGS)
CANONICAL_ID_TO_KEY = {key: key for key in ALL_MODEL_CONFIGS}

# Compatibility names for Claude-oriented imports in the generated tree.
CLAUDE_3_5_HAIKU_CONFIG = DEEPSEEK_CHAT_CONFIG
CLAUDE_3_5_V2_SONNET_CONFIG = DEEPSEEK_CHAT_CONFIG
CLAUDE_3_7_SONNET_CONFIG = DEEPSEEK_CHAT_CONFIG
CLAUDE_HAIKU_4_5_CONFIG = DEEPSEEK_CHAT_CONFIG
CLAUDE_OPUS_4_CONFIG = DEEPSEEK_REASONER_CONFIG
CLAUDE_OPUS_4_1_CONFIG = DEEPSEEK_REASONER_CONFIG
CLAUDE_OPUS_4_5_CONFIG = DEEPSEEK_REASONER_CONFIG
CLAUDE_OPUS_4_6_CONFIG = DEEPSEEK_REASONER_CONFIG
CLAUDE_SONNET_4_CONFIG = DEEPSEEK_CHAT_CONFIG
CLAUDE_SONNET_4_5_CONFIG = DEEPSEEK_CHAT_CONFIG
CLAUDE_SONNET_4_6_CONFIG = DEEPSEEK_CHAT_CONFIG
