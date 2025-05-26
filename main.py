import tkinter as tk
from tkinter import messagebox
from datetime import datetime
import csv
import os
from data_editor import open_data_editor
from settings_window import open_settings_window, load_settings
from rate_graph import show_rate_graph
from environment_distribution import show_environment_distribution
from match_summary import show_match_summary


# CSVファイル名
CSV_FILE = "master_duel_records.csv"
RANKS = [
    "R1", "B5", "B4", "B3", "B2", "B1",
    "S5", "S4", "S3", "S2", "S1",
    "G5", "G4", "G3", "G2", "G1",
    "P5", "P4", "P3", "P2", "P1",
    "D5", "D4", "D3", "D2", "D1",
    "M5", "M4", "M3", "M2", "M1"
]

settings = load_settings()
# 起動時に開くウィンドウの処理


# メニューバーの作成
def create_menu(root):
    menubar = tk.Menu(root)

    # データタブ
    data_menu = tk.Menu(menubar, tearoff=0)
    data_menu.add_command(label="データ編集", command=open_data_editor)  # データ編集ウィンドウを開く
    menubar.add_cascade(label="データ", menu=data_menu)

    # "分析"メニューを追加
    analysis_menu = tk.Menu(menubar, tearoff=0)
    analysis_menu.add_command(label="レート/ランク推移を表示", command=show_rate_graph)
    analysis_menu.add_command(label="環境分布を見る", command=show_environment_distribution)
    analysis_menu.add_command(label="戦績をまとめる", command=show_match_summary)
    menubar.add_cascade(label="分析", menu=analysis_menu)
    root.config(menu=menubar)
    # 設定メニューの追加
    settings_menu = tk.Menu(menubar, tearoff=0)
    settings_menu.add_command(label="設定", command=open_settings_window)
    menubar.add_cascade(label="設定", menu=settings_menu)

    # メニューバーに追加

# 最後の記録をロードする関数
def load_last_record():
    if os.path.exists(CSV_FILE):
        with open(CSV_FILE, "r", encoding="mbcs") as f:
            reader = csv.DictReader(f)
            records = list(reader)
            if records:
                return records[-1]
    return None

# 新しい記録をCSVに保存する関数
def save_record():
    # 必須フィールドのチェック
    if not date_entry.get().strip():
        messagebox.showerror("入力エラー", "日付を入力してください。")
        return

    if not deck_entry.get().strip():
        messagebox.showerror("入力エラー", "使用デッキを入力してください。")
        return

    if not coin_var.get().strip():
        messagebox.showerror("入力エラー", "コインの表裏を選択してください。")
        return

    if not turn_var.get().strip():
        messagebox.showerror("入力エラー", "先攻/後攻を選択してください。")
        return

    if not result_var.get().strip():
        messagebox.showerror("入力エラー", "戦績を選択してください。")
        return

    # 空欄時のデフォルト値セット
    opponent_deck = opponent_entry.get().strip() or "不明"
    # レートの処理（未入力の場合はデフォルトで 0）
    rate = rate_var.get().strip()
    rate = int(rate) if rate.isdigit() else 0  # 未入力または不正入力なら 0 に設定

    # レコード作成
    record = {
        "date": date_entry.get(),
        "deck": deck_entry.get(),
        "coin": coin_var.get(),
        "turn": turn_var.get(),
        "opponent_deck": opponent_deck,
        "result": result_var.get(),
        "rank": rank_var.get(),
        "rate": rate,
        "memo": memo_entry.get("1.0", "end-1c"),
    }

    # データをCSVに保存
    try:
        file_exists = os.path.exists(CSV_FILE)
        with open(CSV_FILE, "a", encoding="mbcs", newline="") as f:
            writer = csv.DictWriter(f, fieldnames=record.keys())
            if not file_exists:
                writer.writeheader()
            writer.writerow(record)

        # 保存後のリセット操作
        opponent_entry.delete(0, tk.END)  # 相手デッキフィールドを空にする
        result_var.set("")  # 勝敗の選択をリセット
        result_button_win.config(bg="SystemButtonFace", relief="raised")  # 勝ちボタンをリセット
        result_button_lose.config(bg="SystemButtonFace", relief="raised")  # 負けボタンをリセット

    except Exception as e:
        messagebox.showerror("エラー", f"エラーが発生しました: {e}")

# ランク変更
def change_rank(value):
    try:
        current_index = RANKS.index(rank_var.get())
        new_index = max(0, min(current_index + value, len(RANKS) - 1))
        rank_var.set(RANKS[new_index])
    except ValueError:
        rank_var.set(RANKS[0])

#全角数字の半角変換
def convert_to_half_width(text):
    return ''.join(chr(ord(char) - 0xFEE0) if '０' <= char <= '９' else char for char in text)

# レート調整
def update_rate_entry(value):
    try:
        # 全角数字を半角数字に変換
        current_rate = convert_to_half_width(rate_var.get())
        current_rate = int(current_rate) if current_rate.isdigit() else 0
        rate_var.set(current_rate + value)
    except ValueError:
        rate_var.set("0")

# トグルボタン
def toggle_button(selected_var, value, button1, button2):
    selected_var.set(value)
    if selected_var.get() == value:
        button1.config(bg="lightblue", relief="sunken")
        button2.config(bg="SystemButtonFace", relief="raised")
    else:
        button1.config(bg="SystemButtonFace", relief="raised")
        button2.config(bg="lightblue", relief="sunken")

# 安全な終了処理を追加
def on_close():
    """アプリケーション終了処理"""
    try:
        # 必要なリソースの解放（例: ウィンドウやファイルのクローズ）
        print("アプリケーションを終了します...")
        root.destroy()  # メインウィンドウを正常に閉じる
    except Exception as e:
        print(f"エラーが発生しました: {e}")

# GUI作成
root = tk.Tk()
root.title("遊戯王マスターデュエル 戦績記録")
root.geometry("360x524")

root.resizable(False, False)

create_menu(root)

# メインウィンドウの終了イベントを設定
root.protocol("WM_DELETE_WINDOW", on_close)

# 起動時に開くウィンドウの処理
startup_windows = settings["Settings"].get("StartupWindow", "").split(",")

if "RateGraph" in startup_windows:
    show_rate_graph()
if "EnvironmentDistribution" in startup_windows:
    show_environment_distribution()
if "MatchSummary" in startup_windows:
    show_match_summary()

# グリッドのリサイズ設定
for i in range(10):  # 縦10行
    root.rowconfigure(i, weight=1, minsize=40)
for i in range(6):  # 横6列
    root.columnconfigure(i, weight=1, minsize=60)

# グリッドの各要素を配置
last_record = load_last_record()

# 日付
tk.Label(root, text="日付:", anchor="w").grid(row=0, column=0, sticky="nsew", pady=5, padx=(10, 0), columnspan=2)  # 左に10ピクセルの空白
date_var = tk.StringVar(value=datetime.today().strftime('%Y/%m/%d'))
date_entry = tk.Entry(root, textvariable=date_var)
date_entry.grid(row=0, column=2, columnspan=4, sticky="nsew", pady=5, padx=(0, 10))  # 右に10ピクセルの空白

# 使用デッキ
tk.Label(root, text="使用デッキ:", anchor="w").grid(row=1, column=0, sticky="nsew", pady=5, padx=(10, 0), columnspan=2)
deck_var = tk.StringVar(value=last_record["deck"] if last_record else "")
deck_entry = tk.Entry(root, textvariable=deck_var)
deck_entry.grid(row=1, column=2, columnspan=4, sticky="nsew", pady=5, padx=(0, 10))

# コインの表裏
tk.Label(root, text="コインの表裏:", anchor="w").grid(row=2, column=0, sticky="nsew", pady=5, padx=(10, 0), columnspan=2)
coin_var = tk.StringVar(value="")
coin_button_head = tk.Button(root, text="表", command=lambda: toggle_button(coin_var, "表", coin_button_head, coin_button_tail))
coin_button_tail = tk.Button(root, text="裏", command=lambda: toggle_button(coin_var, "裏", coin_button_tail, coin_button_head))
coin_button_head.grid(row=2, column=2, columnspan=2, sticky="nsew", pady=5, padx=(0, 10))
coin_button_tail.grid(row=2, column=4, columnspan=2, sticky="nsew", pady=5, padx=(0, 10))

# 先攻/後攻
tk.Label(root, text="先攻/後攻:", anchor="w").grid(row=3, column=0, sticky="nsew", pady=5, padx=(10, 0), columnspan=2)
turn_var = tk.StringVar(value="")
turn_button_first = tk.Button(root, text="先攻", command=lambda: toggle_button(turn_var, "先攻", turn_button_first, turn_button_second))
turn_button_second = tk.Button(root, text="後攻", command=lambda: toggle_button(turn_var, "後攻", turn_button_second, turn_button_first))
turn_button_first.grid(row=3, column=2, columnspan=2, sticky="nsew", pady=5, padx=(0, 10))
turn_button_second.grid(row=3, column=4, columnspan=2, sticky="nsew", pady=5, padx=(0, 10))

# 相手デッキ
tk.Label(root, text="相手デッキ:", anchor="w").grid(row=4, column=0, sticky="nsew", pady=5, padx=(10, 0), columnspan=2)
opponent_entry = tk.Entry(root)
opponent_entry.grid(row=4, column=2, columnspan=4, sticky="nsew", pady=5, padx=(0, 10))

# 戦績
tk.Label(root, text="戦績:", anchor="w").grid(row=5, column=0, sticky="nsew", pady=5, padx=(10, 0), columnspan=2)
result_var = tk.StringVar(value="")
result_button_win = tk.Button(root, text="勝", command=lambda: toggle_button(result_var, "勝", result_button_win, result_button_lose))
result_button_lose = tk.Button(root, text="敗", command=lambda: toggle_button(result_var, "敗", result_button_lose, result_button_win))
result_button_win.grid(row=5, column=2, columnspan=2, sticky="nsew", pady=5, padx=(0, 10))
result_button_lose.grid(row=5, column=4, columnspan=2, sticky="nsew", pady=5, padx=(0, 10))

# ランク
tk.Label(root, text="ランク:", anchor="w").grid(row=6, column=0, sticky="nsew", pady=5, padx=(10, 0), columnspan=2)
rank_var = tk.StringVar(value=last_record["rank"] if last_record and "rank" in last_record else RANKS[0])
tk.Label(root, textvariable=rank_var, anchor="w").grid(row=6, column=2, sticky="nsew", pady=5, padx=(0, 10))
tk.Button(root, text="-", command=lambda: change_rank(-1)).grid(row=6, column=4, sticky="nsew", pady=5, padx=(0, 10))
tk.Button(root, text="+", command=lambda: change_rank(1)).grid(row=6, column=5, sticky="nsew", pady=5, padx=(0, 10))

# レート
tk.Label(root, text="レート:", anchor="w").grid(row=7, column=0, sticky="nsew", pady=5, padx=(10, 0), columnspan=2)
rate_var = tk.StringVar(value=str(last_record["rate"]) if last_record and "rate" in last_record else "")
rate_entry = tk.Entry(root, textvariable=rate_var)
rate_entry.grid(row=7, column=2, sticky="nsew", pady=5, padx=(0, 10))
tk.Button(root, text="-", command=lambda: update_rate_entry(-1)).grid(row=7, column=4, sticky="nsew", pady=5, padx=(0, 10))
tk.Button(root, text="+", command=lambda: update_rate_entry(1)).grid(row=7, column=5, sticky="nsew", pady=5, padx=(0, 10))

# 備考
tk.Label(root, text="備考:", anchor="w").grid(row=8, column=0, sticky="nsew", pady=5, padx=(10, 0), columnspan=2)
memo_entry = tk.Text(root, height=5)
memo_entry.grid(row=8, column=2, columnspan=4, sticky="nsew", pady=5, padx=(0, 10))

# 保存ボタン
save_button = tk.Button(root, text="保存", command=save_record)
save_button.grid(row=9, column=0, columnspan=6, sticky="nsew", pady=5, padx=(10, 10))  # 左右のスペースを追加

try:
    # メインループの実行
    root.mainloop()
except KeyboardInterrupt:
    # 手動で終了（Ctrl+Cなど）が実行された場合でも問題なく終了
    print("アプリケーションが中断されました（KeyboardInterrupt）。")
    try:
        root.destroy()
    except Exception:
        pass