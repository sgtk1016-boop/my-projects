import json
import subprocess
import sys
from datetime import date
from pathlib import Path

PROJECTS_FILE = Path(__file__).parent / "projects.json"
STATUS_MAP = {"1": "planning", "2": "in_progress", "3": "completed", "4": "paused"}

def generate_id(projects):
    today = date.today().strftime("%Y%m%d")
    existing = [p["id"] for p in projects if p["id"].startswith(today)]
    seq = len(existing) + 1
    return f"{today}-{seq:02d}"

def git_sync(name, date_str, action="add"):
    print("\n=== Git 同期 ===")
    git_cmds = [
        (["git", "add", "projects.json"], "git add"),
        (["git", "commit", "-m", f"{action}: {name} ({date_str})"], "git commit"),
        (["git", "push"], "git push"),
    ]
    for cmd, label in git_cmds:
        try:
            result = subprocess.run(cmd, cwd=PROJECTS_FILE.parent, capture_output=True, text=True)
            if result.returncode == 0:
                print(f"[OK] {label}")
            else:
                print(f"[NG] {label}: {result.stderr.strip()}")
        except Exception as e:
            print(f"[NG] {label}: {e}")

def edit_mode(data, projects):
    if not projects:
        print("登録済みプロジェクトがありません。")
        return

    print("=== プロジェクト一覧 ===")
    for i, p in enumerate(projects, 1):
        print(f"  {i}: [{p['id']}] {p['name']}")

    try:
        idx = int(input("編集する番号: ").strip()) - 1
        if not (0 <= idx < len(projects)):
            print("無効な番号です。")
            return
    except ValueError:
        print("無効な入力です。")
        return

    entry = projects[idx]
    print(f"\n=== 編集: {entry['name']} ===")
    print("(空Enterでスキップ＝変更なし)\n")

    STATUS_REVERSE = {v: k for k, v in STATUS_MAP.items()}

    def ask(label, current):
        val = input(f"{label} [{current}]: ").strip()
        return val if val else None

    name_in = ask("name       ", entry["name"])
    if name_in:
        entry["name"] = name_in

    purpose_in = ask("purpose    ", entry["purpose"])
    if purpose_in:
        entry["purpose"] = purpose_in

    mechanism_in = ask("mechanism  ", entry["mechanism"])
    if mechanism_in:
        entry["mechanism"] = mechanism_in

    integ_in = ask("integrations (カンマ区切り)", ",".join(entry["integrations"]))
    if integ_in:
        entry["integrations"] = [s.strip() for s in integ_in.split(",") if s.strip()]

    print("status: 1=planning  2=in_progress  3=completed  4=paused")
    status_in = ask("status     ", entry["status"])
    if status_in and status_in in STATUS_MAP:
        entry["status"] = STATUS_MAP[status_in]

    tags_in = ask("tags (カンマ区切り)", ",".join(entry["tags"]))
    if tags_in:
        entry["tags"] = [s.strip() for s in tags_in.split(",") if s.strip()]

    usage_in = input(f"usage      [{entry.get('usage', '')}]: ").strip()
    if usage_in:
        entry["usage"] = usage_in

    notes_in = input(f"notes      [{entry.get('notes', '')}]: ").strip()
    if notes_in:
        entry["notes"] = notes_in

    projects[idx] = entry
    data["projects"] = projects

    try:
        PROJECTS_FILE.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")
    except Exception as e:
        print(f"保存に失敗しました: {e}")
        return

    print("\n=== 更新完了 ===")
    print(json.dumps(entry, ensure_ascii=False, indent=2))
    git_sync(entry["name"], entry["date"], action="update")

def register_entry(data, projects, name, purpose, mechanism, integrations, status, tags, usage, notes):
    entry = {
        "id":           generate_id(projects),
        "name":         name,
        "date":         date.today().isoformat(),
        "purpose":      purpose,
        "mechanism":    mechanism,
        "integrations": integrations,
        "status":       status,
        "tags":         tags,
        "usage":        usage,
        "notes":        notes,
    }

    projects.append(entry)
    data["projects"] = projects

    try:
        PROJECTS_FILE.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")
    except Exception as e:
        print(f"保存に失敗しました: {e}")
        sys.exit(1)

    print("\n=== 登録完了 ===")
    print(json.dumps(entry, ensure_ascii=False, indent=2))
    git_sync(entry["name"], entry["date"], action="add")

def main():
    try:
        data = json.loads(PROJECTS_FILE.read_text(encoding="utf-8"))
    except Exception as e:
        print(f"projects.json の読み込みに失敗しました: {e}")
        sys.exit(1)

    projects = data.get("projects", [])

    # 自動モード: --data '{"name":"..."}' が指定された場合
    if "--data" in sys.argv:
        idx = sys.argv.index("--data")
        try:
            payload = json.loads(sys.argv[idx + 1])
        except (IndexError, json.JSONDecodeError) as e:
            print(f"--data のパースに失敗しました: {e}")
            sys.exit(1)
        register_entry(
            data, projects,
            name=payload.get("name", ""),
            purpose=payload.get("purpose", ""),
            mechanism=payload.get("mechanism", ""),
            integrations=payload.get("integrations", []),
            status=payload.get("status", "planning"),
            tags=payload.get("tags", []),
            usage=payload.get("usage", ""),
            notes=payload.get("notes", ""),
        )
        return

    print("1: 新規登録 / 2: 既存編集")
    mode = input("選択: ").strip()
    if mode == "2":
        edit_mode(data, projects)
        return

    print("\n=== プロジェクト登録 ===")
    name         = input("name        : ").strip()
    purpose      = input("purpose     : ").strip()
    mechanism    = input("mechanism   : ").strip()
    integrations = [s.strip() for s in input("integrations (カンマ区切り): ").split(",") if s.strip()]

    print("status: 1=planning  2=in_progress  3=completed  4=paused")
    status_key = input("status      : ").strip()
    status = STATUS_MAP.get(status_key, "planning")

    tags  = [s.strip() for s in input("tags (カンマ区切り): ").split(",") if s.strip()]
    usage = input("usage / 使用方法 (空Enterでスキップ): ").strip()
    notes = input("notes (空Enterでスキップ): ").strip()

    register_entry(data, projects, name, purpose, mechanism, integrations, status, tags, usage, notes)

if __name__ == "__main__":
    main()
