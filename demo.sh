#!/bin/bash
# Task Reminder Skill 演示脚本
# 演示整个创建和使用流程

echo "========================================"
echo "Task Reminder Skill 演示"
echo "========================================"
echo ""

echo "1. 检查 Skill 文件结构"
echo "----------------------------------------"
sleep 2
ls -lh /root/OpenClawWorkspace/skills/task_reminder/
sleep 3
echo ""

echo "2. 查看任务列表"
echo "----------------------------------------"
sleep 2
cat /root/OpenClawWorkspace/skills/task_reminder/tasks.json
sleep 3
echo ""

echo "3. 运行任务管理器测试"
echo "----------------------------------------"
sleep 2
python3 /root/OpenClawWorkspace/skills/task_reminder/task_manager.py
sleep 3
echo ""

echo "4. 查看主处理逻辑"
echo "----------------------------------------"
sleep 2
head -30 /root/OpenClawWorkspace/skills/task_reminder/task_reminder_main.py
sleep 3
echo ""

echo "5. 查看使用文档"
echo "----------------------------------------"
sleep 2
cat /root/OpenClawWorkspace/skills/task_reminder/SKILL.md
sleep 3
echo ""

echo "6. 查看流程图"
echo "----------------------------------------"
sleep 2
cat /root/OpenClawWorkspace/skills/task_reminder/FLOWCHART.md
sleep 3
echo ""

echo "7. 查看会话记录"
echo "----------------------------------------"
sleep 2
head -50 /root/OpenClawWorkspace/skills/task_reminder/SESSION_LOG.md
sleep 3
echo ""

echo "========================================"
echo "演示完成！"
echo "========================================"
sleep 2
