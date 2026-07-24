#!/usr/bin/env python3
"""
发送定时提醒脚本
被 cron 每小时调用
"""

import json
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from task_reminder_main import generate_progress_check

def main():
    result = generate_progress_check()
    
    # 输出结果供 openclaw cron 处理
    print(json.dumps(result, ensure_ascii=False))
    
    # 如果所有任务已完成，退出码 1 表示应该删除定时任务
    if result["action"] in ["all_completed_auto"]:
        return 1
    return 0

if __name__ == "__main__":
    exit_code = main()
    sys.exit(exit_code)
