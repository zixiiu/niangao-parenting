#!/bin/bash
# 这个脚本由 cron 任务调用，用于更新早教活动数据并触发部署

set -e

# 站点目录
SITE_DIR="/home/ub/clawd/parenting-site"
DATA_FILE="$SITE_DIR/data/activities.json"

# 确保数据目录存在
mkdir -p "$SITE_DIR/data"

# 从 cron 任务接收 JSON 数据
if [ -n "$1" ]; then
    echo "$1" > "$DATA_FILE"
    echo "数据已更新: $DATA_FILE"
fi

# 进入站点目录
cd "$SITE_DIR"

# 提交更改
git add -A
git commit -m "自动更新: $(date '+%Y-%m-%d %H:%M:%S')" || echo "没有需要提交的更改"

# 推送到 GitHub（这会触发 GitHub Actions 部署）
git push origin master

echo "已推送到 GitHub，等待 Actions 自动部署..."
