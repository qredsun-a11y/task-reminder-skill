import json
from pathlib import Path
from datetime import datetime
import re

class TaskManager:
    def __init__(self, tasks_file="tasks.json"):
        self.tasks_file = Path(tasks_file)
        self.tasks = self._load_tasks()

    def _load_tasks(self):
        """从文件加载任务列表"""
        if self.tasks_file.exists():
            with open(self.tasks_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        return []

    def _save_tasks(self):
        """保存任务列表到文件"""
        with open(self.tasks_file, 'w', encoding='utf-8') as f:
            json.dump(self.tasks, f, ensure_ascii=False, indent=2)

    def parse_tasks_from_text(self, text):
        """从用户文本中解析任务列表"""
        # 匹配模式：1.任务 2.任务 或 1、任务 2、任务
        task_pattern = r'(?:任务[:：]?)?\s*(?:(?:\d+)[\.、\s]+([^\n\r]+))'
        matches = re.findall(task_pattern, text)
        
        if not matches:
            # 尝试另一种模式：用数字序号开头
            lines = text.split('\n')
            for line in lines:
                match = re.match(r'^\s*(?:\d+)[\.、\s]+(.+)$', line.strip())
                if match:
                    matches.append(match.group(1).strip())
        
        # 清理任务描述
        tasks = []
        for desc in matches:
            desc = desc.strip().rstrip('，,。.;；')
            if desc and len(desc) > 2:
                tasks.append(desc)
        
        return tasks

    def add_tasks(self, descriptions):
        """批量添加任务"""
        for desc in descriptions:
            self.tasks.append({
                "description": desc,
                "status": "未开始",
                "delayed": False,
                "created_at": datetime.now().isoformat(),
                "completed_at": None
            })
        self._save_tasks()
        return len(descriptions)

    def clear_and_add_tasks(self, descriptions):
        """清空并添加新任务（新的一天）"""
        self.tasks = []
        return self.add_tasks(descriptions)

    def mark_completed(self, keyword):
        """根据关键词标记任务完成"""
        keyword = keyword.strip()
        matched = False
        
        for i, task in enumerate(self.tasks):
            if keyword in task["description"] and task["status"] != "已完成":
                self.tasks[i]["status"] = "已完成"
                self.tasks[i]["completed_at"] = datetime.now().isoformat()
                matched = True
                break
        
        if matched:
            self._save_tasks()
        return matched

    def mark_delayed(self, keyword):
        """根据关键词标记任务延期"""
        keyword = keyword.strip()
        matched = False
        
        for i, task in enumerate(self.tasks):
            if keyword in task["description"] and task["status"] != "已完成":
                self.tasks[i]["status"] = "延期"
                self.tasks[i]["delayed"] = True
                matched = True
                break
        
        if matched:
            self._save_tasks()
        return matched

    def get_pending_tasks(self):
        """获取未完成任务"""
        return [task for task in self.tasks if task["status"] in ["未开始", "进行中"]]

    def get_completed_tasks(self):
        """获取已完成任务"""
        return [task for task in self.tasks if task["status"] == "已完成"]

    def get_delayed_tasks(self):
        """获取延期任务"""
        return [task for task in self.tasks if task["delayed"]]

    def get_all_tasks_info(self):
        """获取所有任务信息摘要"""
        total = len(self.tasks)
        completed = len(self.get_completed_tasks())
        pending = len(self.get_pending_tasks())
        delayed = len(self.get_delayed_tasks())
        return {
            "total": total,
            "completed": completed,
            "pending": pending,
            "delayed": delayed
        }

    def get_delayed_task_descriptions(self):
        """获取延期任务描述列表（用于第二天续接）"""
        return [task["description"] for task in self.tasks if task["delayed"]]

    def all_completed(self):
        """检查所有任务是否完成"""
        if not self.tasks:
            return False
        return all(task["status"] == "已完成" for task in self.tasks)

    def has_pending(self):
        """检查是否有未完成任务"""
        return len(self.get_pending_tasks()) > 0

    def clear_tasks(self):
        """清空所有任务"""
        self.tasks = []
        self._save_tasks()

    def load_delayed_from_previous_day(self, descriptions):
        """从之前的一天加载延期任务"""
        for desc in descriptions:
            self.tasks.append({
                "description": desc,
                "status": "未开始",
                "delayed": False,
                "created_at": datetime.now().isoformat(),
                "completed_at": None,
                "continued": True
            })
        self._save_tasks()
