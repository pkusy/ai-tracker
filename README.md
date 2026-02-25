# AI Tracker - GitHub AI 前沿追踪系统

> 每日自动抓取 GitHub 知名 AI 项目，追踪前沿模型和出色应用

## 功能特性

- 🔥 **GitHub Trending** - 每日 AI 领域热门项目
- 🔍 **关键词搜索** - 按 LLM, GPT, diffusion 等关键词发现新项目
- ⭐ **Watchlist 监控** - 跟踪知名 AI 项目动态
- 📊 **结构化存储** - JSON 格式保存，便于分析
- 📝 **Markdown 报告** - 每日自动生成摘要报告

## 快速开始

### 1. 安装依赖

```bash
cd ai-tracker
pip install -r requirements.txt
```

### 2. 配置 GitHub Token（可选，但推荐）

```bash
# 创建 .env 文件
echo "GITHUB_TOKEN=your_github_token_here" > .env
```

获取 Token: https://github.com/settings/tokens

### 3. 运行

```bash
# 手动运行
python main.py

# 指定日期
python main.py --date 2026-02-25

#  verbose 模式
python main.py -v
```

## 输出

运行后会在 `data/` 目录生成：

```
ai-tracker/
├── data/
│   ├── projects.json     # 项目数据（结构化）
│   ├── daily/
│   │   └── 2026-02-25.md  # 每日报告
│   └── history/          # 历史存档
```

## 每日自动运行

### Option 1: Crontab（macOS/Linux）

```bash
# 编辑 crontab
crontab -e

# 每天早上 8 点运行
0 8 * * * /usr/bin/python3 /path/to/ai-tracker/main.py >> /path/to/ai-tracker.log 2>&1
```

### Option 2: GitHub Actions（推荐）

创建 `.github/workflows/daily-tracker.yml`:

```yaml
name: Daily AI Tracker

on:
  schedule:
    - cron: '0 0 * * *'  # 每天 UTC 0 点运行
  workflow_dispatch:  # 手动触发

jobs:
  track:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - name: Set up Python
        uses: actions/setup-python@v5
        with:
          python-version: '3.10'
      - name: Install dependencies
        run: |
          pip install -r requirements.txt
      - name: Run tracker
        env:
          GITHUB_TOKEN: ${{ secrets.GITHUB_TOKEN }}
        run: python main.py
      - name: Commit and push
        run: |
          git config --local user.email "ai-tracker@github.com"
          git config --local user.name "AI Tracker"
          git add data/
          git diff --staged --quiet || git commit -m "Update AI tracker data"
          git push
```

## 配置

编辑 `config.py` 自定义：

- `AI_KEYWORDS` - 搜索关键词列表
- `WATCHLIST` - 监控的项目列表
- `TRENDING_LANGUAGES` - 关注的编程语言
- `CACHE_TTL_SECONDS` - 缓存时间

## 报告预览

生成的 Markdown 报告包含：

- 📊 概览统计
- 🔥 Trending 项目 TOP 15
- 🔍 关键词搜索发现
- ⭐ Watchlist 今日更新
- 🏆 Top 10 热门项目

## 技术栈

- Python 3.9+
- PyGithub - GitHub API
- BeautifulSoup4 - HTML 解析
- Requests - HTTP 请求

---

*由 AI Tracker 自动生成*
