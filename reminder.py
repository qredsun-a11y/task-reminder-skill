import json
from pathlib import Path
from task_manager import TaskManager
from datetime import datetime
import time

class TaskReminder:
    def __init__(self, tasks_file="tasks.json"):
        self.manager = TaskManager(tasks_file)

    def check_progress(self):
        pending_tasks = self.manager.get_pending_tasks()
        if not pending_tasks:
            print("所有任务已完成！")
            return

        print("以下任务需要确认进度：")
        for i, task in enumerate(pending_tasks):
            print(f"{i + 1}. {task['description']} - {task['status']}")

    def run_hourly_reminder(self):
        while True:
            print(f"\n{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}: 检查任务进度...")
            self.check_progress()
            time.sleep(3600)  # 每小时检查一次

if __name__ == "__main__":
    reminder = TaskReminder()
    print("启动任务提醒系统...")
    reminder.run_hourly_reminder()