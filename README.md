# DeepSeek Code

## 最新补充：SDK schema 与控制入口增强

- `python_src/entrypoints/sdk/coreSchemas.py` 已补齐 DeepSeek/OpenAI 兼容的消息、tool call、usage、prompt request/response、output format 和 result schema。
- 新增 SDK helper：`validate_prompt_request`、`normalize_output_format`、`sdk_message`、`prompt_response`。
- `python_src/entrypoints/sdk/controlSchemas.py` 已补齐 control request/response 结构，并提供 `parse_control_request`、`control_success`、`control_error`。
- `python_src/entrypoints/agentSdkTypes.py` 的 `query()` 已复用 prompt request 校验和 DeepSeek prompt response payload，保持本地 dry-run。

# 最新补充：Ink 顶层渲染/运行时 shim

- 已继续补齐 `python_src/ink` 顶层渲染底座：measure/wrap/widest-line/tabstop/colorize、screen/selection/search highlight、render-to-screen、render-node-to-output 和 squash-text-nodes。
- 已清理 Ink 顶层 runtime shell 占位：dom/focus/hit-test/reconciler/root/renderer/instances/node-cache/optimizer/output/styles/parse-keypress/terminal helpers 等均改为可测试的本地 Python shim。
- `python_src/ink/*.py` 当前已无真实 `NotImplementedError` 残留；实现保持本地结构化输出，不引入 React/Ink 运行时、不触发外部终端副作用。

这是一个将 Claude Code TypeScript 项目逐步迁移到 Python 的实验性实现。原始 `src` 目录保持不变，Python 迁移代码放在 `python_src` 与 `deepseek_code` 中；模型交互层已经改为 DeepSeek/OpenAI 兼容的 Chat Completions API。

## 已适配内容

- Claude 顶层 `system` 参数会转换为 `messages[0].role = "system"`。
- Claude `input_schema` 工具定义会转换为 DeepSeek/OpenAI `tools[].function.parameters`。
- Claude `tool_use` / `tool_result` 流程已替换为 `message.tool_calls` 与 `role="tool"` 消息。
- 流式输出解析 DeepSeek SSE 的 `choices[0].delta.content`，并支持增量拼接 `delta.tool_calls`。
- 移除 Anthropic 专属 API 路径、beta headers、prompt cache 控制、Bedrock/Vertex/Foundry 调用路径。
- 默认工具池导出 43 个 DeepSeek/OpenAI 兼容函数工具，覆盖文件读写、搜索、Shell/PowerShell、配置、Notebook、MCP 资源、技能、计划模式、LSP、记忆、会话、成本、Agent/Team、任务、调度、监控、插件、工作流、网页抓取和网页搜索。
- 已补齐多层本地运行时：权限系统、Git/GitHub 辅助、settings/config/model/status、compact/context、Session Memory、Prompt Suggestion、工具执行流、MCP 基础服务、analytics 本地 sink、API 错误/重试/usage 辅助、token/rate-limit、voice/MCP approval、LSP 服务和顶层 bootstrap/task/history/command/context 状态层。
- 已补齐一批 REPL/编辑基础能力：Vim state/motion/text object/operator/transition、小型 XDG/XML/YAML/workload/worktree/zod schema 工具函数。
- 已补齐文件与数据基础工具：Node-like `fsOperations`、文件读取缓存、编码/换行检测、路径展开/规范化、JSON/JSONC/JSONL 解析、hash、uuid、sleep/timeout。
- 已补齐 buddy/companion 展示辅助层：确定性 companion roll、稀有度/属性常量、intro attachment、ASCII sprite/face 渲染、终端预留列、浮动气泡文本和 `/buddy` 通知触发检测。
- 已补齐桥接基础层：session history 分页、bridge 配置/开关、状态展示、debug 脱敏、JWT 解析、session ID 兼容转换、work secret 解码、SDK URL 构造和 bridge pointer 持久化。
- 已补齐桥接协议层：bridge API client、错误分类、故障注入、入站消息/附件规范化、控制请求响应、UUID 去重、poll interval 配置和 capacity wake 基础结构。
- 已补齐桥接会话层：code session 创建、remote credentials 获取、bridge session 创建/读取/归档/标题更新、trusted device token 本地存储、REPL bridge handle 指针、permission response 校验、env-less bridge 配置和轻量 session runner。
- 已补齐桥接运行层：`FlushGate` 初始 flush 队列状态机、bridge logger、v1/v2 REPL transport 适配、env-less bridge core、REPL bridge handle 初始化、bridge 主循环参数解析和连接/服务端错误分类。
- 已补齐 CLI 结构化 IO 基础层：退出 helper、NDJSON 安全序列化、StructuredIO 控制请求/响应、RemoteIO transport shim、SSE frame 解析，以及 WebSocket/Hybrid/SSE transport 选择。
- 已补齐 CLI headless/CCR 运行层：`cli/print.py` 的 prompt 合并、批处理判断、权限 prompt、MCP set_servers/reconcile、orphaned permission response 和轻量 headless 返回；`cli/update.py` 的 DeepSeek Code 本地更新检查；`SerialBatchEventUploader`、`WorkerStateUploader`、`CCRClient` 的批量上传、状态合并、delivery/state/metadata 和 stream_event 文本增量合并。
- 已补齐一批基础 slash commands：`add-dir` 路径校验/工作目录更新、`color` 会话颜色状态、`copy` 最近 assistant 文本/代码块导出、`effort` 推理强度状态和 `exit` 退出结果。
- 已补齐更多 slash commands：`agents` 复用 agent 配置扫描，`remote-control` 接入本地 bridge headless 会话，`btw` 提供 DeepSeek 安全的旁路提问参数，`clear/reset/new` 清理会话与运行时缓存。
- 已补齐本地配置类 commands：`version` 输出运行版本，`brief` 切换简短输出模式，`advisor` 配置 DeepSeek advisor 模型，并补齐 `utils/advisor.py` 的本地 feature gate、advisor block 判断和 usage 提取。
- 已补齐更多运行态 commands：`fast` 及 `utils/fastMode.py` 的 DeepSeek 快速模式状态、冷却和模型切换，`files` 的上下文文件列表，以及 `cost` 的会话成本摘要入口。
- 已补齐导出/反馈/诊断命令：`export` 的会话纯文本渲染与文件导出，`feedback` 的本地组件数据 shim，`heapdump` 的 Python 运行时诊断文件输出，以及 `debug-tool-call` 的禁用 stub；同时补齐 `exportRenderer`、`heapDumpService` 和 `slowOperations`。
- 已补齐帮助与偏好类命令：`help` 的命令列表视图数据、`keybindings` 的配置文件创建/加载/模板、`release-notes` 的 changelog 缓存解析，以及 `theme` 的主题选择 shim。
- 已补齐 keybindings 深层辅助模块：`parser`、`match`、`resolver`、`reservedShortcuts` 和 `validate`，支持快捷键解析、组合键匹配、chord 状态解析、保留快捷键检查、重复配置检测和 warning 格式化。
- 已补齐 keybindings 交互层 shim：默认绑定表、schema 常量、快捷键显示 fallback、Python context 容器、hook 注册包装、provider setup 和 chord interceptor 处理逻辑。
- 已补齐 output styles 配置链路：frontmatter 解析、markdown 配置目录扫描、`.deepseek/.claude/output-styles` 加载、内置 Explanatory/Learning 风格、settings 选择和插件强制风格 shim。
- 已补齐登录/退出/计划/通行证相关运行层：DeepSeek 本地 API key 登录/退出、本地全局/项目配置、plan 文件持久化、`/plan` 模式 shim 和 `/passes` 首次访问状态。
- 已补齐成本追踪与 DeepSeek 价格估算层：`cost_tracker` 会累加 token、cache、web search、模型用量和 session cost，并支持保存/恢复到项目配置；`utils/modelCost.py` 按 DeepSeek/OpenAI usage 结构估算费用，且支持环境变量覆盖单价。
- 已补齐 Git/Review prompt 命令层：`commit`、`commit-push-pr`、`review`、`security-review` 和 `statusline` 现在会生成 DeepSeek 可消费的文本 prompt 与 allowed tools metadata，不直接执行提交、推送或 PR 创建。
- 已补齐轻量设置/环境命令层：`privacy-settings`、`remote-env`、`rate-limit-options`、`sandbox`、`tag` 和 `terminal-setup` 提供本地 Python shim，覆盖隐私开关、安全环境摘要、限流选项、沙箱排除规则、会话标签和终端按键设置状态。
- 已补齐初始化/计划命令层：`init`、`init-verifiers`、`bridge-kick` 和 `ultraplan` 从占位实现迁移为 Python shim；其中初始化和 verifier 命令生成 DeepSeek 原生指导 prompt，`bridge-kick` 支持桥接故障注入入口，`ultraplan` 提供本地高级计划 prompt 与状态管理。
- 已补齐桌面/浏览器/额外用量命令层：`desktop`、`chrome` 和 `extra-usage` 不再依赖 React/Claude 订阅 UI，改为 DeepSeek 品牌化的本地状态、配置写入和安全提示结果。
- 已补齐状态型本地命令包装层：`memory`、`session`、`usage`、`vim`、`voice`、`tasks` 和 `skills` 的 index/命令实现已接到 Python store/config，覆盖记忆、会话、用量、编辑模式、语音开关、后台任务和技能列表。
- 已补齐会话辅助命令层：`rename`、`resume`、`rewind`、`summary`、`share` 和 `stats` 现在基于 Python 本地会话/历史/task store 工作，支持会话命名、恢复列表、回退、摘要 prompt、本地分享 payload 和统计摘要。
- 已补齐一批 CLI handlers：DeepSeek 本地 auth login/status/logout/token 安装、agents 列表、auto-mode 默认/配置/规则评估，以及 doctor/setup/install 轻量处理。
- 已补齐 MCP/plugin CLI handlers：MCP server 本地增删查列、Desktop 配置导入、choices 重置、plugin/marketplace 本地安装列表启停更新卸载和 manifest 校验。
- 已补齐顶层启动/交互 shim：`costHook`、`interactiveHelpers`、`dialogLaunchers`、`main`、`replLauncher`、`ink`、`setup`、`QueryEngine` 和 `query` 不再抛占位异常，改为 DeepSeek 结构化结果或 `CodeProcessor` 兼容包装。
- 已补齐权限组件 shim：`components/permissions` 的通用 permission UI、文件写入/编辑/Notebook diff、Shell/PowerShell/WebFetch/Skill/Plan/ComputerUse 请求、AskUserQuestion 预览状态和权限规则管理组件都已替换为 DeepSeek/Python 结构化结果。
- 已补齐 StructuredDiff/Spinner 展示 shim：结构化 diff fallback、word diff、彩色 diff 摘要、Spinner glyph/row、shimmer/stalled 状态和 teammate 选择提示均可在 Python 侧稳定导入与测试。
- 已补齐 Agent 组件 shim：agent markdown 读写路径、生成 fallback、校验、列表/详情/编辑器、模型/工具/颜色选择器和新建 agent 向导 steps 已迁为 DeepSeek/Python 结构化结果。
- 已补齐 CustomSelect 交互基础 shim：单选、多选、option map、输入键位解析和导航状态都已替换为 Python 可测试状态机。
- 已补齐 design-system 基础组件 shim：主题、文本/容器、Dialog、Tabs、ProgressBar、FuzzyPicker、StatusIcon 等通用 UI 构件已迁为结构化终端数据。
- 已补齐 diff 展示组件 shim：DiffFileList、DiffDetailView 和 DiffDialog 现在基于 unified diff/StructuredDiff 返回文件摘要、增删行统计和操作状态。
- 已补齐 FeedbackSurvey/HelpV2 组件 shim：反馈评分、transcript share 本地记录、memory/compact survey 状态和 DeepSeek 帮助页/命令列表均已可测试。
- 已补齐 hooks 与零散展示组件 shim：hooks 配置菜单、事件/模式选择、hook prompt dialog、插件提示、桌面提示、代码高亮 fallback 和 Grove/隐私弹窗均已迁为本地结构化结果。
- 已补齐 LSP 推荐与 managed settings 安全组件 shim：LSP server 推荐菜单、敏感设置提取、危险设置变更检测和安全确认弹窗均已迁为本地结构化结果。
- 已补齐 MCP UI 组件 shim：MCP server 列表/菜单、tool 列表/详情、capabilities、settings、parsing warnings、elicitation dialog 和 reconnect helpers 均已迁为只读结构化状态。
- 已补齐 memory 与用户工具结果消息 shim：memory 文件选择、更新通知、工具成功/错误/拒绝/取消/计划拒绝消息和 tool-use 查找工具均已迁为 DeepSeek/Python 结构化结果。
- 已补齐通用 messages 展示 shim：assistant/user/system 文本、thinking、tool use、附件、compact 边界、rate-limit、shutdown、plan approval、任务分配、团队记忆和用户命令/图片/资源消息均已迁为结构化输出。
- 已补齐 PromptInput 输入组件 shim：输入模式识别、paste 截断、history search、footer/suggestions/help、placeholder、sandbox hint、voice indicator 和 queued/stash 状态均已迁为 Python 状态机。
- 已补齐 sandbox 与 Settings 组件 shim：沙箱配置/依赖/doctor/override 视图、设置 config/status/usage 视图和敏感配置脱敏均已迁为本地结构化结果。
- 已补齐 shell、TrustDialog、wizard 与 ui 底座 shim：shell 输出/JSON/URL/耗时展示、信任来源摘要、wizard 步骤状态和 ordered/tree UI 选择均已迁为 DeepSeek/Python 结构化结果。
- 已补齐 tasks/teams/skills/Passes 组件 shim：后台任务、远程会话、shell progress、工具活动、团队状态、技能菜单和 passes 视图均已迁为本地结构化结果。
- 已补齐 LogoV2 欢迎展示组件 shim：启动 logo、动画标记、feed/notice、欢迎页、guest pass 与 overage credit 提示均已迁为 DeepSeek 品牌化结构化结果。
- 已补齐一批根级状态/对话组件 shim：App、进度行、API key 审批、auto mode、更新提示、bridge、上下文、快捷键、桌面 handoff 等均已迁为本地结构化结果。
- 已补齐第二批根级开发/文件/搜索组件 shim：DevBar、诊断、推理 effort、退出/导出、工具错误/拒绝、反馈脱敏、文件 diff、全屏布局、全局搜索、代码高亮和历史搜索均已迁为可测试结构。
- 已补齐 IDE/Markdown/MCP 根级组件 shim：IDE 自动连接/引导/状态、无效配置提示、语言/日志选择、Markdown/表格解析、MCP server 审批/导入/复制/多选和 memory usage 指示器均已迁为本地结构化结果。
- 已补齐消息/模型/选择器根级组件 shim：Message、MessageRow、Messages、MessageSelector、messageActions、模型选择、onboarding、输出风格和 PR badge 均已迁为 DeepSeek 消息语义。
- 已补齐远程/滚动/状态根级组件 shim：QuickOpen、Remote、ResumeTask、SandboxViolation、ScrollKeybinding、SearchBox、Session、Spinner、Stats、StatusLine 和 StatusNotices 均已迁为本地状态机结果。
- 已补齐末批根级结构/输入/Teleport 组件 shim：StructuredDiff/列表、TagTabs、TaskListV2、TeammateViewHeader、Teleport 错误/进度/恢复/stash、TextInput/VimTextInput、主题/思考开关/token warning、工具加载、校验错误、虚拟消息列表、工作流多选和 worktree 退出确认均已迁为本地结构化结果。
- 已补齐 constants 基础常量层：API/media/tool limits、DeepSeek product/oauth/prompt/system 文案、文件二进制判断、spinner/turn verbs、XML tag、GitHub workflow 模板和工具权限常量均已去 Claude 草稿化。
- 已补齐安装/限流重置/hooks 命令 shim：`install` 生成本地安装计划，`reset-limits` 返回 DeepSeek mock/rate-limit 状态路径，`hooks/hooks.py` 复用本地 hooks 配置视图，均不执行外部安装或删除操作。
- 已补齐 context 状态容器 shim：fps metrics、mailbox、modal/overlay、prompt overlay、notifications、queued messages、stats 和 voice context 均已迁为进程内 DeepSeek/Python 轻量 store。
- 已补齐 coordinator 与 entrypoints SDK 层：coordinator mode prompt/context、agent SDK session dry-run、CLI/init/MCP 入口、sandbox schema、SDK core/control schema 常量均已迁为 DeepSeek/Python 本地接口。
- 已补齐第一批基础 hooks：文件路径建议、统一建议、placeholder 渲染、首渲染状态、API key 检查、箭头历史、assistant history、away summary、后台任务导航、blink、取消请求和工具可用性判断均已迁为本地 shim。
- 已补齐第二批基础 hooks：Chrome/DeepSeek 提示、剪贴板图片提示、命令 keybinding/队列、选择复制、deferred hook messages、diff 数据/IDE diff dry-run、direct connect、double press、dynamic config、elapsed time、Ctrl+C 退出和文件历史快照均已迁为本地 shim。
- 已补齐第三批基础 hooks：全局快捷键、历史搜索、IDE mention/连接/集成/日志/选择、inbox poller、input buffer、issue banner、日志过滤、LSP 推荐、mailbox bridge、主循环模型、插件管理、memory usage 和 clients/commands/tools 合并均已迁为本地 shim。

## 安装

```bash
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
```

## 配置

创建 `.env` 文件，或直接设置环境变量：

```bash
DEEPSEEK_API_KEYS=key1,key2,key3
DEEPSEEK_MODELS=deepseek-chat,deepseek-coder
DEEPSEEK_ENDPOINTS=https://api.deepseek.com
DEEPSEEK_BALANCE_STRATEGY=round_robin
DEFAULT_MODEL=deepseek-chat
```

如果使用代理或兼容网关，可以把 `DEEPSEEK_ENDPOINTS` 改为自己的 OpenAI 兼容 `/v1` 端点。

## 运行

```bash
python -m deepseek_code.cli "write a python fibonacci function"
python -m deepseek_code.cli --model deepseek-chat "explain this repository"
python -m deepseek_code.cli --enable-tools "read README.md and summarize it"
```

默认会流式打印模型输出；需要一次性输出时使用 `--no-stream`。`--enable-tools` 会启用已经迁移的本地工具，并把工具 schema 以 DeepSeek/OpenAI 兼容格式传给模型，流式模式下仍会执行工具调用后继续输出最终回答。

## 验证

```bash
python -m compileall deepseek_code python_src tools
$env:PYTEST_DISABLE_PLUGIN_AUTOLOAD='1'; python -m pytest tests
python -c "from python_src.tools import get_deepseek_tools; print(len(get_deepseek_tools()))"
```

当前测试覆盖 DeepSeek 消息/工具适配、负载均衡、本地工具运行时、权限/Git/设置/模型辅助、compact/context、Session Memory、MCP/analytics/API/token/rate-limit 服务、voice/MCP approval、LSP 服务、顶层运行态、任务输出、命令 registry、历史记录、context facade、Vim/小型工具函数、文件/路径/JSON 基础工具、buddy/companion 展示辅助、桥接基础层/协议层/会话层/运行层、CLI 结构化 IO/transport 基础层、CLI headless/CCR 运行层、多批 slash commands、多组 CLI handlers、keybindings 解析/匹配/校验/交互辅助层、output styles/frontmatter/markdown 配置加载链路、auth/config/plan/passes 本地运行链路、DeepSeek 成本追踪/价格估算链路、Git/Review prompt 命令层、轻量设置/环境命令层、初始化/计划命令层、桌面/浏览器/额外用量命令层、状态型本地命令包装层、会话辅助命令层、顶层启动/交互 shim、权限组件 shim、StructuredDiff/Spinner 展示 shim、Agent 组件 shim、CustomSelect 交互基础 shim、design-system 基础组件 shim、diff 展示组件 shim、FeedbackSurvey/HelpV2 组件 shim、hooks/零散展示组件 shim、LSP/managed settings 安全组件 shim、MCP UI 组件 shim、memory/用户工具结果消息 shim、通用 messages 展示 shim、PromptInput 输入组件 shim、sandbox/Settings 组件 shim、shell/TrustDialog/wizard/ui 底座 shim、tasks/teams/skills/Passes 组件 shim、LogoV2 欢迎展示组件 shim、多批根级状态/对话/文件/搜索/IDE/Markdown/MCP/消息/远程滚动状态/Teleport/输入/工作流组件 shim、constants 与安装/限流/hooks 命令 shim、context 状态容器 shim、coordinator/entrypoints SDK shim，以及三批基础 hooks shim。

## 迁移原则

- 不修改原始 `src` TypeScript 源码。
- 迁移文件保留原模块边界，优先补齐可测试的业务行为。
- 所有模型请求都应经由 `deepseek_code` 的 DeepSeek/OpenAI 兼容适配层。
- 不硬编码 API Key，不保留直接调用 `api.anthropic.com` 的路径。
# 最新迁移进度

- 继续补齐 MCP 命令层：`mcp`、`mcp/addCommand` 和 `mcp/xaaIdpCommand` 已替换占位实现，接入本地 `mcp_servers.json`，支持 list/status/enable/disable/reconnect 和 XAA 元数据 shim。
- MCP 迁移只修改本地 DeepSeek 配置摘要，不启动 MCP server、不打开浏览器、不执行 OAuth/XAA 远程登录。
- 继续补齐 IDE/hooks/Think Back 命令 shim：`ide`、`hooks`、`ant-trace`、`think-back` 和 `thinkback-play` 已替换占位实现。
- 这些命令提供本地 IDE 配置检测、hooks 设置摘要、DeepSeek 诊断 trace prompt、年终回顾 prompt 和动画资产检查，不安装 IDE 插件、不启动外部播放器、不触发远程 marketplace。
- 继续补齐本地入口/状态命令 shim：`mobile`、`oauth-refresh`、`onboarding`、`reload-plugins`、`stickers`、`teleport`、`upgrade` 和 `mock-limits` 已替换占位实现。
- 这些命令将 Claude/浏览器/React 依赖改为 DeepSeek 本地结构化结果或文本 prompt，不自动打开浏览器、不执行远程安装、不写入破坏性状态。
- 继续补齐隐藏 prompt/local 命令 shim：`autofix-pr`、`bughunter`、`ctx-viz`、`break-cache`、`backfill-sessions`、`good-claude` 兼容入口和 `perf-issue` 已替换占位实现。
- 这些命令均使用 DeepSeek Code/OpenAI 兼容文本块或本地结构化结果，不直接执行提交、推送、PR、缓存或远程操作。
# 独立终端入口

现在可以用类似 Claude Code 的常驻终端方式启动：

```powershell
python -m deepseek_code.cli
```

也可以使用单独入口：

```powershell
python -m deepseek_terminal
```

常用命令：

```text
/help
/login
/status
/model deepseek-chat
/pwd
/cd D:\DeepCode
/ls
/read README.md
/write hello.py print("hello")
/write notes.md
/append notes.md done
/clear
/exit
```

也支持更接近 Claude Code 的输入习惯：

```text
@README.md 总结这个文件
!git status
/paste
/compact
```

当 `/write <path>` 没有跟随正文时，会进入多行输入模式，使用单独一行 `.end` 结束写入。终端默认启用本地文件工具，模型可以按你的自然语言要求读取、创建和编辑当前工作区文件；工具执行后会显示简短的 `[read_file]`、`[write_file]` 或 `[edit_file]` 摘要，便于确认实际落盘动作。需要禁用时使用：

```powershell
python -m deepseek_code.cli --no-tools
```

如果还没有配置 API Key，终端会先进入离线模式，本地 slash commands 仍可用。配置后再对话：

```powershell
$env:DEEPSEEK_API_KEYS="sk-..."
python -m deepseek_code.cli
```

# 最新迁移进度：remote-setup 与 insights

- 已补齐 `commands/remote-setup` 命令层 shim：`api.py`、`remote-setup.py` 和 `index.py` 现在提供 DeepSeek 品牌化的本地 web-setup 状态检查、GitHub CLI 前置条件提示和安全 token wrapper。
- `remote-setup` 不再调用 Claude CCR 后端、不上传 GitHub token、不创建 Claude hosted environment；DeepSeek 迁移版只返回本地结构化结果和网页连接指引。
- 已补齐 `commands/insights.py` 的轻量报告实现：扫描本地 `.jsonl` 会话、去重 session 分支、统计消息与工具调用、生成本地 HTML 报告，并导出 OpenAI/DeepSeek 可消费的 prompt 文本块。
- `insights` 不再调用 Claude/Anthropic 模型做 facet extraction；当前为确定性本地摘要，后续可按需接入 DeepSeek chat completions 做高阶洞察。

# 最新迁移进度：安装集成命令

- 已补齐 `install-slack-app`：返回 DeepSeek Slack 集成安装提示和本地计数，不主动打开浏览器，不跳转 Claude Slack marketplace。
- 已补齐 `install-github-app`：所有 Step、主命令和 `setupGitHubActions` 已从占位替换为 dry-run planner，生成 DeepSeek GitHub Actions workflow/secret 手动设置计划。
- 安装集成迁移版不创建分支、不写 workflow、不设置 GitHub secret、不打开 PR、不调用 Claude OAuth；只做 GitHub CLI 前置检查、repo 归一化和安全提示。

# 最新补充：hooks 顶层占位清理

- 已继续清理 `python_src/hooks` 顶层剩余占位：补齐最小展示时间、超时通知、官方 marketplace 提示、粘贴处理、插件推荐、Chrome prompt、prompt suggestion、PR 状态、队列处理、远程/REPL/SSH 会话、计划任务、搜索输入、设置变更、技能变更、swarm 初始化与权限 callback 轮询。
- 已补齐终端体验相关 hooks：任务列表 watcher、TasksV2 折叠状态、teammate 自动退出、Teleport resume dry-run、终端尺寸、文本输入、timeout、turn diff、typeahead、更新提示、Vim 输入、虚拟滚动、voice enabled/voice integration。
- 这一批全部保持 DeepSeek/Python 本地结构化 payload，不触发浏览器、语音录制、远程 Teleport、SSH 连接、插件安装或 git/gh 写操作；`python_src/hooks` 顶层文件已无 `NotImplementedError` 占位。

# 最新补充：终端会话驾驶优化

- 独立终端新增 `/context`、`/undo`、`/retry`、`/stream on|off`，`/tools` 会显示工具摘要，输错 slash command 时会提示相近命令。
- 长上下文会自动提示 `/compact 16`；流式请求失败时仍会自动降级为非流式请求重试一次。
- 继续补齐常用终端命令：`/last` 查看最近助手回答，`/find <text>` 搜索当前会话，`/save [path]` 导出 transcript，`/open <path>` 读取文件，`/tree [path]` 快速查看浅层目录结构。
- 终端现在会在 prompt、`/status` 和 `/doctor` 中展示 git 分支与 dirty 状态；新增 `/branch` 查看当前分支，`/diff [--full]` 查看 git diff 摘要或完整 diff，`/tree` 支持 `--depth N`。

# 最新补充：通知 hooks shim

- 已补齐 `python_src/hooks/notifs` 顶层通知 hooks：auto mode、订阅切换、弃用提醒、fast mode、IDE/LSP/MCP 状态、安装消息、模型迁移、npm 弃用、插件更新/安装、rate limit、settings error、startup 和 teammate lifecycle。
- 这些通知均返回 DeepSeek/Python 本地结构化 payload，不依赖 React/Ink，不触发网络、订阅切换、插件安装或外部进程副作用。

# 最新补充：Ink 终端底座 shim

- 已补齐 `python_src/ink/components` 的基础组件、上下文组件和 `App.handleMouseEvent`：Text/Box/Link/ScrollBox/Button/RawAnsi/AlternateScreen 等现在返回 DeepSeek/Python 可消费的结构化节点。
- 已补齐 `python_src/ink/termio` 的 DEC/OSC/SGR/tokenizer/types/ESC 解析能力，支持常用 ANSI 序列、OSC hyperlink/title/clipboard/tab status、SGR 样式状态和流式 escape sequence 分词。
- 已补齐 `python_src/ink/hooks` 的剩余占位：app/input/stdin/selection/search highlight/animation/interval/declared cursor/tab status/focus/title/viewport 都改为本地状态 shim，不依赖 React/Ink 运行时。
