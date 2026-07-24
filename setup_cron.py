#!/usr/bin/env python3
"""
设置或更新定时提醒的 cron 任务

使用方式：
  作为 OpenClaw skill 的一部分使用时，
  直接调用 cron(action="add", job={...}) 工具，
  不依赖 subprocess openclaw CLI（CLI 需要 gateway scope 审批）。

  示例 job 配置：
    {
      "name": "task_reminder_hourly",
      "schedule": {"kind": "every", "everyMs": 3600000},
      "payload": {"kind": "agentTurn", "message": "⏰ 任务进度确认..."},
      "sessionTarget": "current",
      "enabled": True,
    }

  CLI 方式（需要 gateway 审批，可能失败）：
    openclaw cron add --name task_reminder_hourly --every 1h \
      --system-event "⏰ 任务进度确认时间！"

命令行模式（直接调 python3 setup_cron.py）：
  使用 cron 工具 API 进行管理（推荐）。
"""

import json as json_module
import sys
import os

# 添加当前目录到路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))


def get_cron_job_config(task_count):
    """生成 cron job 配置（供 cron 工具使用）"""
    return {
        "name": "task_reminder_hourly",
        "schedule": {"kind": "every", "everyMs": 3600000},
        "payload": {
            "kind": "agentTurn",
            "message": (
                "⏰ 任务进度确认时间！\n\n"
                f"当前有 {task_count} 个任务进行中。\n\n"
                "请运行以下命令检查任务进度：\n"
                "python3 /root/OpenClawWorkspace/skills/task_reminder/send_reminder.py\n\n"
                "然后根据返回结果，在当前会话中回复用户当前任务状态和未完成任务列表。"
            ),
        },
        "sessionTarget": "current",
        "enabled": True,
        "description": "每小时提醒用户确认任务完成进度",
    }


def main():
    """命令行入口（调试用）"""
    tasks_file = os.path.join(os.path.dirname(os.path.abspath(__file__)), "tasks.json")
    task_count = 0
    try:
        with open(tasks_file, 'r', encoding='utf-8') as f:
            tasks = json_module.load(f)
            task_count = len(tasks)
    except Exception as e:
        print(f"Warning: Could not read tasks file: {e}")

    config = get_cron_job_config(task_count)
    print(json_module.dumps(config, ensure_ascii=False, indent=2))
    print()
    print("请在 OpenClaw agent 会话中使用 cron(action='add', job={...}) 添加此任务。")


if __name__ == "__main__":
    main()