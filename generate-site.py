#!/usr/bin/env python3
"""
年糕宝宝早教活动生成器
从活动数据生成网页并准备部署
"""

import json
import os
from datetime import datetime, date
from pathlib import Path

# 宝宝出生日期
BIRTH_DATE = date(2026, 1, 9)

# 站点目录
SITE_DIR = Path("/home/ub/clawd/parenting-site")
DATA_FILE = SITE_DIR / "data" / "activities.json"
HTML_FILE = SITE_DIR / "index.html"

def calculate_age(current_date):
    """计算宝宝年龄"""
    days = (current_date - BIRTH_DATE).days
    weeks = days // 7
    week_days = days % 7
    months = days // 30
    month_days = days % 30
    return {
        "days": days,
        "weeks": weeks,
        "weekDays": week_days,
        "months": months,
        "monthDays": month_days
    }

def load_activities():
    """加载活动数据"""
    if DATA_FILE.exists():
        with open(DATA_FILE, 'r', encoding='utf-8') as f:
            return json.load(f)
    return None

def update_html(activities_data):
    """更新 HTML 文件中的活动数据"""
    if not HTML_FILE.exists():
        print("❌ HTML 文件不存在")
        return False

    # 读取 HTML
    with open(HTML_FILE, 'r', encoding='utf-8') as f:
        html_content = f.read()

    # 更新年龄信息
    age = activities_data['babyAge']
    html_content = html_content.replace(
        'id="daysOld">47天',
        f'id="daysOld">{age["days"]}天'
    )
    html_content = html_content.replace(
        'id="weeksOld">6周5天',
        f'id="weeksOld">{age["weeks"]}周{age["weekDays"]}天'
    )
    html_content = html_content.replace(
        'id="monthsOld">1个月16天',
        f'id="monthsOld">{age["months"]}个月{age["monthDays"]}天'
    )

    # 更新 activities 数组
    activities_json = json.dumps(activities_data['activities'], ensure_ascii=False, indent=12)
    
    # 找到 activities 数组并替换
    import re
    pattern = r'const activities = \[.*?\];'
    replacement = f'const activities = {activities_json};'
    html_content = re.sub(pattern, replacement, html_content, flags=re.DOTALL)

    # 写回文件
    with open(HTML_FILE, 'w', encoding='utf-8') as f:
        f.write(html_content)

    print("✅ HTML 已更新")
    return True

def main():
    """主函数"""
    print("🍼 年糕宝宝早教网页生成器")
    print("=" * 50)

    # 加载活动数据
    activities_data = load_activities()
    if not activities_data:
        print("❌ 没有找到活动数据")
        return False

    print(f"📅 日期: {activities_data['date']}")
    print(f"📊 年龄: {activities_data['babyAge']['days']}天")

    # 更新 HTML
    if update_html(activities_data):
        print("✅ 网页生成完成！")
        return True

    return False

if __name__ == "__main__":
    main()
