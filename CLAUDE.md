# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Context

Windows 11 home directory. Active projects live as subdirectories.

## Environment

- OS: Windows 11, Git Bash (use Unix shell syntax; PS scripts use Windows paths)
- Run PS scripts: `powershell -File <script.ps1>`
- Python 3.13 installed

## Projects

### dark-tokyo-generator (`~/dark-tokyo-generator`)
Automates DARK TOKYO YouTube content: Claude API generates Suno music prompts, Playwright drives browser automation for Suno/Midjourney, YouTube API analyzes channel performance.

- **Run**: `python app.py`
- **Install**: `pip install -r requirements.txt` then `playwright install chromium`
- **Config**: `config.yaml` (params, series prompts); secrets in `.env`
- `browser_profiles/` stores persistent Playwright sessions (Discord/Suno logins)

### dark-tokyo-suno (`~/dark-tokyo-suno`)
Next.js + TypeScript frontend.

- **Dev**: `npm run dev` → http://localhost:3000
- **Build/Lint**: `npm run build` / `npm run lint`

### youtube-comment-bot (`~/youtube-comment-bot`)
Split architecture: GitHub Actions (daily cron) fetches comments → Groq AI generates replies → Gmail sends approval email. Railway Express server handles JWT approval and posts to YouTube API.

- **Build**: `npm run build`
- **Dev**: `npm run dev:collect` (Actions flow) / `npm run dev:serve` (Express server)
- **Config**: `.env`; GitHub Secrets for Actions; Railway env vars for server

### Desktop scripts (`~/`)
`organize2.ps1` / `organize_desktop.ps1` — sort desktop shortcuts into folders (仕事, コミュニケーション, エンタメ, ツール, ファイル)

## User Context

- YouTube channel: DARK TOKYO (@DARKTOKYO1016) — BGM/Vlog
- Works in medical facility DX
- Prefers concise responses in Japanese or English as appropriate

---

## プロジェクト登録

「登録して」と言われたら以下を実行する。

1. この会話の内容から各フィールドを判断してJSONを組み立てる
   - name: 作ったものの名前
   - purpose: 何のために作ったか（1〜2文）
   - mechanism: 技術的な仕組み（使用言語・処理の流れ）
   - integrations: 連携したサービス・API・ツール名（配列）
   - status: 完成→"completed" / 動作確認中→"in_progress" / 未着手→"planning" / 停止中→"paused"
   - tags: 該当するもの（業務DX / YouTube / 自動化 / GAS / Python / Google Sheets など）
   - usage: 実際の使い方・起動手順（①②③形式で簡潔に。会話中に手順・コマンド・操作方法があれば必ず抽出する）
   - prompt: ユーザーがClaudeに最初に伝えた指示の要約（「〇〇を作って」という依頼内容。会話の冒頭や目的から読み取る）
   - notes: 次のステップや未解決の問題・制約事項。なければ空文字

2. register.py を --data オプションで実行する
   python register.py --data '{"name":"...","purpose":"...","mechanism":"...","integrations":["..."],"status":"...","tags":["..."],"usage":"...","prompt":"...","notes":"..."}'

3. 登録内容をそのまま表示して完了を伝える
