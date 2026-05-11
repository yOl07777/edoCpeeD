# DeepSeek Code

这是 Claude Code 模型交互层的 Python 实现，底层已适配 DeepSeek 的 OpenAI 兼容 Chat Completions API。

## 适配内容

- Claude 的顶层 `system` 请求参数会转换为第一条 `role="system"` 消息。
- Claude 工具定义中的 `input_schema` 会转换为 OpenAI/DeepSeek 的 `tools[].function.parameters`。
- Claude 的 `tool_use` / `tool_result` 流程已替换为 `message.tool_calls` 和 `role="tool"` 结果消息。
- 流式输出会读取 SSE 中的 `choices[0].delta.content`，并增量拼接 `choices[0].delta.tool_calls`。
- Bash/PowerShell 工具已补充本地只读校验、危险命令提示、路径约束和权限模式判断，减少 DeepSeek 调用外部命令时的误操作风险。
- 权限系统已提供 Python 版规则解析、规则持久化、权限模式、文件系统安全检查和 tool permission hook，可用于 DeepSeek 工具调用前的统一授权判断。
- Git 相关辅助模块已提供 Python 版 config 解析、`.git` 目录/HEAD/ref/remote 读取、gitignore 匹配、`/diff` 命令和本地 review prompt 生成。
- GitHub/分支命令已提供 Python 版 `gh auth status`、issue 列表/查看、PR 评论读取和分支名派生/读取；在未安装或未登录 `gh` 时会返回结构化不可用状态。
- Settings/config/model/status 已提供 Python 版设置文件解析与合并、配置读写、模型选择和运行状态摘要，默认读取 DeepSeek 环境变量与项目设置文件。
- 模型工具层已完成 DeepSeek 化，提供模型别名、能力表、显示名、agent 默认模型、模型校验和 Claude 旧名称到 DeepSeek 模型的兼容映射。
- 已移除 Claude 专属的 prompt cache 控制、Anthropic beta headers、Bedrock/Vertex/Foundry 路径，以及 `api.anthropic.com` 依赖。

## 安装

```bash
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
```

## 配置

创建 `.env` 文件，或直接导出环境变量。DeepSeek 当前的 OpenAI 兼容 base URL 是 `https://api.deepseek.com`；如果你使用代理或兼容网关，也可以通过配置继续使用 `/v1` 端点。

```bash
DEEPSEEK_API_KEYS=key1,key2,key3
DEEPSEEK_MODELS=deepseek-chat,deepseek-coder
DEEPSEEK_ENDPOINTS=https://api.deepseek.com
DEFAULT_MODEL=deepseek-chat
```

## 运行

```bash
python -m deepseek_code.cli "write a python fibonacci function"
python -m deepseek_code.cli --stream --model deepseek-chat "explain this repository"
python -m deepseek_code.cli --enable-tools "read README.md and summarize it"
```

`--enable-tools` 会启用已迁移的本地工具，目前包括：

- `read_file`
- `write_file`
- `edit_file`
- `glob_files`
- `grep_files`
- `run_shell`
- `run_powershell`
- `config`
- `notebook_edit`
- `list_mcp_resources`
- `read_mcp_resource`
- `skill`
- `enter_plan_mode`
- `exit_plan_mode`
- `lsp_symbol_search`
- `memory`
- `session`
- `cost`
- `clear_conversation`
- `agent`
- `sleep`
- `cron_create`
- `cron_list`
- `cron_delete`
- `monitor`
- `remote_trigger`
- `plugin`
- `reload_plugins`
- `output_style`
- `workflow`
- `team_create`
- `team_delete`
- `send_message`
- `ask_user_question`
- `todo_write`
- `task_create`
- `task_get`
- `task_list`
- `task_update`
- `task_stop`
- `task_output`
- `web_fetch`
- `web_search`

## 说明

实现遵循 DeepSeek 的 OpenAI 兼容 Chat Completions 结构：Chat Completion endpoint、Bearer 鉴权、`messages`、`tools`、`tool_calls`，以及 SSE 流式响应中的 `choices[].delta`。
