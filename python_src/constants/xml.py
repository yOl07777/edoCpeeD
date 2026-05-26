from __future__ import annotations


BASH_INPUT_TAG = "bash-input"
BASH_STDERR_TAG = "bash-stderr"
BASH_STDOUT_TAG = "bash-stdout"
CHANNEL_MESSAGE_TAG = "channel-message"
CHANNEL_TAG = "channel"
COMMAND_ARGS_TAG = "command-args"
COMMAND_MESSAGE_TAG = "command-message"
COMMAND_NAME_TAG = "command-name"
COMMON_HELP_ARGS = "help"
COMMON_INFO_ARGS = "info"
CROSS_SESSION_MESSAGE_TAG = "cross-session-message"
FORK_BOILERPLATE_TAG = "fork-boilerplate"
FORK_DIRECTIVE_PREFIX = "fork:"
LOCAL_COMMAND_CAVEAT_TAG = "local-command-caveat"
LOCAL_COMMAND_STDERR_TAG = "local-command-stderr"
LOCAL_COMMAND_STDOUT_TAG = "local-command-stdout"
OUTPUT_FILE_TAG = "output-file"
REASON_TAG = "reason"
REMOTE_REVIEW_PROGRESS_TAG = "remote-review-progress"
REMOTE_REVIEW_TAG = "remote-review"
STATUS_TAG = "status"
SUMMARY_TAG = "summary"
TASK_ID_TAG = "task-id"
TASK_NOTIFICATION_TAG = "task-notification"
TASK_TYPE_TAG = "task-type"
TEAMMATE_MESSAGE_TAG = "teammate-message"
TERMINAL_OUTPUT_TAGS = [BASH_INPUT_TAG, BASH_STDOUT_TAG, BASH_STDERR_TAG, LOCAL_COMMAND_STDOUT_TAG, LOCAL_COMMAND_STDERR_TAG]
TICK_TAG = "tick"
TOOL_USE_ID_TAG = "tool-use-id"
ULTRAPLAN_TAG = "ultraplan"
WORKTREE_BRANCH_TAG = "worktree-branch"
WORKTREE_PATH_TAG = "worktree-path"
WORKTREE_TAG = "worktree"


__all__ = [name for name in globals() if name.isupper()]
