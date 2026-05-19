#!/usr/bin/env python3
"""
Super 健身 - 三个月减脂计划 + 每日任务生成
用户档案：177cm / 180斤(90kg) → 目标140斤(70kg) / 男 / 轻度脂肪肝
喜好：跑步、骑行、有氧运动
"""

import os, json, datetime, logging
from openai import OpenAI
from pathlib import Path

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# ── 用户档案 ──────────────────────────────────────────────────────────────────
USER_PROFILE = {
    "gender": "男",
    "height_cm": 177,
    "weight_current_kg": 90,   # 180斤
    "weight_target_kg": 70,    # 140斤
    "weight_loss_kg": 20,
    "duration_months": 3,
    "condition": "轻度脂肪肝",
    "prefer_exercise": ["跑步", "骑行", "有氧运动"],
    "start_date": "2026-03-01",
    "bmi_current": round(90 / (1.77 ** 2), 1),
}

# ── 三个月整体计划（静态，生成一次） ─────────────────────────────────────────
THREE_MONTH_PLAN = None

def get_three_month_plan(client) -> str:
    """生成三个月完整计划（如果 plan.json 不存在就生成并缓存）"""
    plan_file = Path(__file__).parent / "plan.json"
    if plan_file.exists():
        return json.loads(plan_file.read_text())["plan"]

    logger.info("📋 生成三个月整体计划...")
    p = USER_PROFILE
    prompt = f"""你是专业健身教练和营养师。请为以下用户制定科学的三个月减脂计划。

## 用户档案
- 性别：{p['gender']} | 身高：{p['height_cm']}cm | 当前体重：{p['weight_current_kg']}kg（{p['weight_current_kg']*2}斤）
- 目标体重：{p['weight_target_kg']}kg（{p['weight_target_kg']*2}斤）| 目标减重：{p['weight_loss_kg']}kg
- 健康状况：{p['condition']}（需注意：避免高脂饮食，适量有氧为主）
- 运动偏好：{', '.join(p['prefer_exercise'])}
- 计划周期：{p['duration_months']} 个月（从 {p['start_date']} 开始）
- 当前 BMI：{p['bmi_current']}（超重）

## 要求
1. 考虑轻度脂肪肝：饮食以低脂低糖为主，禁酒
2. 每周减重 1.2-1.5kg 左右（总减 20kg / 3个月）
3. 运动以跑步、骑行有氧为主，配合适量力量训练
4. 分三个阶段（第1月/第2月/第3月），每阶段说明运动强度升级策略

请输出完整的 Markdown 格式计划，包含：
### 第一个月（适应期）
- 运动计划（每周几天/每次多长/强度）
- 饮食原则和三餐示例
- 注意事项

### 第二个月（强化期）
（同上）

### 第三个月（冲刺期）
（同上）

### 每周训练结构模板
（每天安排：跑步日/骑行日/休息日）

### 饮食总原则（适合脂肪肝患者）
（5条核心原则）

### 重要提醒
（脂肪肝注意事项、何时需要就医等）"""

    resp = client.chat.completions.create(
        model="deepseek-chat",
        messages=[{"role": "user", "content": prompt}],
        timeout=120,
    )
    plan = resp.choices[0].message.content
    plan_file.write_text(json.dumps({"plan": plan, "generated_at": str(datetime.datetime.now())}))
    logger.info("✅ 三个月计划已生成并缓存")
    return plan


def get_day_number(start_date_str="2026-03-01") -> tuple[int, int]:
    """计算今天是第几天、第几周"""
    start = datetime.datetime.strptime(start_date_str, "%Y-%m-%d").date()
    today = datetime.date.today()
    delta = (today - start).days
    day_num = max(1, delta + 1)
    week_num = (day_num - 1) // 7 + 1
    return day_num, week_num


def generate_daily_task(client, day_num: int, week_num: int, three_month_plan: str) -> str:
    """生成今日具体任务"""
    today = datetime.datetime.now().strftime("%Y年%m月%d日 %A")
    month_num = (day_num - 1) // 30 + 1
    day_in_week = ((day_num - 1) % 7) + 1

    # 周期规律：1跑步、2骑行、3跑步、4力量+核心、5骑行、6跑步、7休息
    exercise_rotation = {
        1: ("🏃 跑步日", "有氧跑步"),
        2: ("🚴 骑行日", "有氧骑行"),
        3: ("🏃 跑步日", "有氧跑步"),
        4: ("💪 力量+核心日", "力量训练与核心"),
        5: ("🚴 骑行日", "有氧骑行"),
        6: ("🏃 跑步日", "有氧跑步"),
        7: ("😴 主动恢复日", "低强度拉伸"),
    }
    day_type, exercise_type = exercise_rotation[day_in_week]

    prompt = f"""你是专业健身教练，请根据三个月计划为用户生成今日具体任务。

## 当前进度
- 今日：{today}
- 计划第 {day_num} 天（第 {week_num} 周 / 第 {month_num} 月）
- 今日类型：{day_type}

## 三个月整体计划（参考）
{three_month_plan[:1500]}...

## 请生成今日任务（Markdown格式）：

### {day_type} · 第{day_num}天

**今日目标：** （一句话，明确本次训练目的）

#### 🏋️ 运动计划
（具体安排：热身 + 主训练 + 拉伸放松，注明时间/距离/配速/强度）

#### 🥗 今日饮食建议
- **早餐**：（具体食物，约XXXkcal）
- **午餐**：（具体食物，约XXXkcal）
- **晚餐**：（具体食物，约XXXkcal）
- **加餐/饮水**：
- **今日总热量**：约 XXXX kcal（脂肪肝友好版）

#### 💊 今日补剂/注意
（维生素/电解质/水分/脂肪肝注意事项）

#### 📊 进度提示
不要声称和计算已减重多少公斤，真实减重数据只有用户本人知道。
只说"今天加油"、"本周重点"、"当前属于第几阶段"的鼓励语即可。语气积极友好，不要太长。

语气积极友好，有激励感，不要太长。"""

    resp = client.chat.completions.create(
        model="deepseek-chat",
        messages=[{"role": "user", "content": prompt}],
        timeout=60,
    )
    return resp.choices[0].message.content


def format_newsletter(daily_task: str, day_num: int, week_num: int) -> str:
    today = datetime.datetime.now().strftime("%Y年%m月%d日")
    now = datetime.datetime.now().strftime("%H:%M")
    p = USER_PROFILE
    progress_pct = min(100, round(day_num / 90 * 100))

    lines = [
        f"# 💪 Super 健身 · 今日任务",
        f"**{today}** | 第 {day_num} 天 / 第 {week_num} 周 | 进度 {progress_pct}%",
        f"目标：{p['weight_current_kg']}kg → {p['weight_target_kg']}kg（还需减 {p['weight_loss_kg']}kg）",
        "",
        "---",
        "",
        daily_task,
        "",
        "---",
        f"*Super 健身助手 · {today} {now} | 坚持就是胜利！💪*",
    ]
    return "\n".join(lines)


if __name__ == "__main__":
    client = OpenAI(api_key=os.environ["DEEPSEEK_API_KEY"], base_url="https://api.deepseek.com")
    plan = get_three_month_plan(client)
    day_num, week_num = get_day_number()
    daily = generate_daily_task(client, day_num, week_num, plan)
    content = format_newsletter(daily, day_num, week_num)
    print(content)
    out_dir = Path(__file__).parent / "daily_tasks"
    out_dir.mkdir(exist_ok=True)
    fname = out_dir / f"fitness_{datetime.datetime.now().strftime('%Y%m%d')}.md"
    fname.write_text(content, encoding='utf-8')
    logger.info(f"💾 已保存: {fname}")
