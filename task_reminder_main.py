#!/usr/bin/env python3
"""
任务提醒主处理逻辑
处理用户消息，管理定时提醒
"""

import json
import os
import re
import sys
from pathlib import Path
from datetime import datetime

# 添加当前目录到路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from task_manager import TaskManager

TASKS_FILE = Path(__file__).parent / "tasks.json"
STATE_FILE = Path(__file__).parent / "state.json"

# 触发关键词
TRIGGER_KEYWORDS = [
    "今晚有几个任务", "今天有几个任务", "待完成任务",
    "今晚任务", "今天任务", "任务列表", "有几个任务"
]

# 完成关键词
COMPLETE_KEYWORDS = ["完成", "搞定了", "做完了", "结束", "ok了", "好了"]

# 延期关键词
DELAY_KEYWORDS = ["明天继续", "后天继续", "延期", "改天", "以后", "明天再做"]

# 结束工作关键词  
END_WORK_KEYWORDS = ["结束", "下班", "休息", "不做了", "今天到此为止"]

# 继续工作关键词
CONTINUE_KEYWORDS = ["继续", "还没结束", "接着干", "继续工作"]


def load_state():
    """加载状态"""
    if STATE_FILE.exists():
        with open(STATE_FILE, 'r', encoding='utf-8') as f:
            return json.load(f)
    return {
        "reminder_active": False,
        "waiting_response": False,
        "last_reminder_time": None,
        "job_id": None
    }


def save_state(state):
    """保存状态"""
    with open(STATE_FILE, 'w', encoding='utf-8') as f:
        json.dump(state, f, ensure_ascii=False, indent=2)


def is_trigger_message(text):
    """检查是否是触发任务收集的消息"""
    text_lower = text.lower()
    for keyword in TRIGGER_KEYWORDS:
        if keyword in text:
            return True
    return False


def is_completion_message(text):
    """检查是否是任务完成消息"""
    text_lower = text.lower()
    for keyword in COMPLETE_KEYWORDS:
        if keyword in text:
            return True
    return False


def is_delay_message(text):
    """检查是否是任务延期消息"""
    text_lower = text.lower()
    for keyword in DELAY_KEYWORDS:
        if keyword in text:
            return True
    return False


def is_end_work_message(text):
    """检查是否是结束工作消息"""
    text_lower = text.lower()
    for keyword in END_WORK_KEYWORDS:
        if keyword in text:
            return True
    return False


def is_continue_message(text):
    """检查是否是继续工作消息"""
    text_lower = text.lower()
    for keyword in CONTINUE_KEYWORDS:
        if keyword in text:
            return True
    return False


def extract_task_keyword(text):
    """从完成/延期消息中提取任务关键词"""
    # 尝试匹配"xxx完成"或"xxx明天继续"的模式
    # 去掉完成/延期关键词，剩余部分作为任务关键词
    all_keywords = COMPLETE_KEYWORDS + DELAY_KEYWORDS
    keyword_part = text
    
    for kw in all_keywords:
        keyword_part = keyword_part.replace(kw, "").strip()
    
    # 去掉标点符号
    keyword_part = re.sub(r'[，,。.;；！!？?]', '', keyword_part).strip()
    
    return keyword_part if len(keyword_part) >= 2 else None


def format_pending_tasks(manager):
    """格式化未完成任务列表"""
    pending = manager.get_pending_tasks()
    if not pending:
        return "✅ 所有任务已完成！"
    
    result = "📋 当前未完成任务：\n"
    for i, task in enumerate(pending):
        result += f"{i + 1}. {task['description']}\n"
    
    return result


def format_progress_report(manager):
    """格式化进度报告"""
    info = manager.get_all_tasks_info()
    pending = manager.get_pending_tasks()
    completed = manager.get_completed_tasks()
    
    result = f"📊 任务进度：{info['completed']}/{info['total']} 完成\n\n"
    
    if completed:
        result += "✅ 已完成：\n"
        for task in completed:
            result += f"  ✓ {task['description']}\n"
        result += "\n"
    
    if pending:
        result += "⏳ 未完成：\n"
        for task in pending:
            result += f"  • {task['description']}\n"
    else:
        result += "\n🎉 太棒了！所有任务都已完成！"
    
    return result


def handle_trigger(text):
    """处理任务收集触发消息"""
    manager = TaskManager(TASKS_FILE)
    
    # 解析任务
    tasks = manager.parse_tasks_from_text(text)
    
    if not tasks:
        return {
            "action": "ask_clarification",
            "message": "我没有找到明确的任务列表。请用序号列出任务，例如：\n1. 任务A\n2. 任务B"
        }
    
    # 检查是否有前一天延期的任务
    delayed_descriptions = manager.get_delayed_task_descriptions()
    
    # 清空并添加新任务
    manager.clear_and_add_tasks(tasks)
    
    # 如果有延期任务，自动续接
    if delayed_descriptions:
        manager.load_delayed_from_previous_day(delayed_descriptions)
        tasks.extend(delayed_descriptions)
    
    # 保存状态
    state = load_state()
    state["reminder_active"] = True
    state["waiting_response"] = False
    save_state(state)
    
    # 创建定时任务
    job_id = setup_hourly_reminder()
    state["job_id"] = job_id
    save_state(state)
    
    message = f"📋 收到 {len(tasks)} 个任务，我将每小时确认进度。\n\n"
    for i, task in enumerate(tasks):
        marker = "🔄" if task in delayed_descriptions else "•"
        message += f"{i + 1}. {marker} {task}\n"
    
    if delayed_descriptions:
        message += "\n🔄 标注的任务是昨天延期过来的。"
    
    return {
        "action": "acknowledge",
        "message": message,
        "job_id": job_id
    }


def handle_completion(text):
    """处理任务完成消息"""
    manager = TaskManager(TASKS_FILE)
    keyword = extract_task_keyword(text)
    
    if not keyword:
        return {
            "action": "ask_clarification",
            "message": "请告诉我具体完成了哪个任务？例如：'git_repo 搭建完成'"
        }
    
    if manager.mark_completed(keyword):
        remaining = len(manager.get_pending_tasks())
        
        if remaining == 0:
            # 所有任务完成
            state = load_state()
            state["reminder_active"] = False
            save_state(state)
            
            return {
                "action": "all_completed",
                "message": f"✅ 已标记完成！\n\n{format_progress_report(manager)}\n\n今天工作辛苦了，先休息吧！所有任务都已完成。🎉"
            }
        else:
            return {
                "action": "mark_completed",
                "message": f"✅ 已标记完成！还剩 {remaining} 个任务。\n\n{format_pending_tasks(manager)}"
            }
    else:
        return {
            "action": "not_found",
            "message": f"我没有找到包含'{keyword}'的任务。\n\n{format_pending_tasks(manager)}"
        }


def handle_delay(text):
    """处理任务延期消息"""
    manager = TaskManager(TASKS_FILE)
    keyword = extract_task_keyword(text)
    
    if not keyword:
        return {
            "action": "ask_clarification",
            "message": "请告诉我具体要延期哪个任务？例如：'整理简历明天继续'"
        }
    
    if manager.mark_delayed(keyword):
        return {
            "action": "mark_delayed",
            "message": f"⏸️ 已标记延期。\n\n{format_pending_tasks(manager)}\n\n今天工作是否结束？"
        }
    else:
        return {
            "action": "not_found",
            "message": f"我没有找到包含'{keyword}'的任务。\n\n{format_pending_tasks(manager)}"
        }


def handle_end_work():
    """处理结束工作"""
    state = load_state()
    state["reminder_active"] = False
    state["waiting_response"] = False
    save_state(state)
    
    manager = TaskManager(TASKS_FILE)
    delayed = manager.get_delayed_tasks()
    
    message = "今天工作辛苦了，先休息吧"
    if delayed:
        message += "\n\n明天继续的任务："
        for task in delayed:
            message += f"\n• {task['description']}"
    message += "💤"
    
    return {
        "action": "end_day",
        "message": message
    }


def handle_continue_work():
    """处理继续工作"""
    state = load_state()
    state["waiting_response"] = False
    save_state(state)
    
    manager = TaskManager(TASKS_FILE)
    return {
        "action": "continue",
        "message": f"好的，继续加油！\n\n{format_pending_tasks(manager)}"
    }


def generate_progress_check():
    """生成进度检查消息（定时任务调用）"""
    manager = TaskManager(TASKS_FILE)
    
    if not manager.has_pending():
        state = load_state()
        state["reminder_active"] = False
        save_state(state)
        
        return {
            "action": "all_completed_auto",
            "message": "🎉 所有任务已完成！今天工作辛苦了，先休息吧！"
        }
    
    return {
        "action": "progress_check",
        "message": f"⏰ 任务进度确认时间到！\n\n{format_progress_report(manager)}\n\n请告诉我哪些任务已完成？"
    }


def setup_hourly_reminder():
    """设置每小时提醒的 cron 任务"""
    import subprocess
    
    # 使用 openclaw 的 cron 工具
    # 这里返回一个 job_id 标识
    job_id = f"task_reminder_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
    return job_id


def process_user_message(text):
    """
    处理用户消息的主入口
    
    返回字典：
    {
        "action": "acknowledge|mark_completed|mark_delayed|progress_check|...",
        "message": "回复消息",
        "job_id": "定时任务ID" (可选)
    }
    """
    text_lower = text.lower().strip()
    state = load_state()
    
    # 1. 检查是否是触发消息
    if is_trigger_message(text):
        return handle_trigger(text)
    
    # 2. 检查是否在等待 结束/继续 的回复
    if state.get("waiting_response", False):
        if is_end_work_message(text):
            return handle_end_work()
        elif is_continue_message(text):
            return handle_continue_work()
    
    # 3. 检查是否是任务完成消息
    if is_completion_message(text):
        return handle_completion(text)
    
    # 4. 检查是否是任务延期消息
    if is_delay_message(text):
        return handle_delay(text)
    
    # 5. 检查是否是结束工作消息
    if is_end_work_message(text) and state.get("reminder_active", False):
        return handle_end_work()
    
    # 6. 默认：返回当前任务状态
    manager = TaskManager(TASKS_FILE)
    if manager.tasks:
        return {
            "action": "show_status",
            "message": format_progress_report(manager)
        }
    
    return {
        "action": "idle",
        "message": ""
    }


if __name__ == "__main__":
    # 测试用
    import sys
    
    if len(sys.argv) > 1:
        message = sys.argv[1]
        result = process_user_message(message)
        print(json.dumps(result, ensure_ascii=False, indent=2))
    else:
        # 运行定时检查
        result = generate_progress_check()
        print(json.dumps(result, ensure_ascii=False, indent=2))
