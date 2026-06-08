# AI Tarot Divination System

一个基于 Flask 和 Minimax API 的 AI 塔罗占卜网站，支持自动抽牌、手动盲抽、每日一牌、AI 解读和本地占卜记录。

## Local Development

```bash
pip install -r requirements.txt
python app.py
```

Open `http://127.0.0.1:5000`.

## Environment Variables

Copy `.env.example` to `.env` and set:

```env
DEEPSEEK_API_KEY=your_deepseek_api_key_here
DEEPSEEK_BASE_URL=https://api.deepseek.com
DEEPSEEK_MODEL=deepseek-v4-flash
DEEPSEEK_THINKING=disabled
SECRET_KEY=change-me
FLASK_DEBUG=false
```

## Render

This repo includes `render.yaml`. Create a Render Web Service from the GitHub repo and set `DEEPSEEK_API_KEY` in Render environment variables.

If you configure the service manually, use:

```bash
gunicorn app:app --bind 0.0.0.0:${PORT:-10000} --timeout 120
```
