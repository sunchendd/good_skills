---
name: super-fitness
description: 三个月科学减脂计划每日推送。使用时机：当用户说"今天健身"、"运动计划"、"减脂建议"、"每日健身打卡"、"fitness plan"。177cm/90kg→70kg，每日 AI 生成个性化运动+饮食方案，邮件+Bark 推送。
---

# 💪 Super 健身

AI 驱动的三个月减脂计划，每日推送个性化运动和饮食方案。

## 用户档案

- 177cm / 90kg → 目标 70kg（减 20kg / 3个月）
- 轻度脂肪肝：低脂低糖，禁酒
- 偏好：跑步、骑行、有氧

## 工作流程

```
三个月计划(缓存) → 计算今日进度 → DeepSeek 生成每日任务 → 邮件+Bark
```

## 每周训练编排

| 周一 | 周二 | 周三 | 周四 | 周五 | 周六 | 周日 |
|------|------|------|------|------|------|------|
| 🏃跑步 | 🚴骑行 | 🏃跑步 | 💪力量 | 🚴骑行 | 🏃跑步 | 😴恢复 |

## 环境变量

| 变量 | 必需 |
|------|------|
| `DEEPSEEK_API_KEY` | ✅ |
| `QQ_EMAIL_PASSWORD` | 发邮件 |

## 用法

```bash
python run_fitness.py              # 今日任务+推送
python run_fitness.py --plan       # 查看/重生三个月计划
python run_fitness.py --no-send    # 只生成不推送
```

## 文件结构

```
super-fitness/
├── SKILL.md
├── run_fitness.py        # 入口
├── fitness_plan.py       # 计划生成+每日任务
├── plan.json             # 缓存的三个月计划
├── bark_client.py
└── daily_tasks/          # 每日任务输出
```
