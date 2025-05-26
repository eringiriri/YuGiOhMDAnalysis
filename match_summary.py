import tkinter as tk
from datetime import datetime, timedelta
from menu_functions_utils import read_csv_by_month, window_key

def show_match_summary():
    """戦績の集計結果を表示"""
    if "match_summary" in window_key:
        window_key["match_summary"].lift()
        return

    def update_month_display(change):
        """月を変更し、データを更新"""
        nonlocal selected_month
        new_date = datetime.strptime(selected_month, '%Y/%m')

        if change == 0:  # 現在の月にリセット
            new_date = datetime.today().replace(day=1)
        elif change == 1:  # 次の月
            new_date = (new_date.replace(day=28) + timedelta(days=4)).replace(day=1)
        elif change == -1:  # 前の月
            new_date = (new_date.replace(day=1) - timedelta(days=1)).replace(day=1)

        if new_date > datetime.today().replace(day=1):
            return

        selected_month = new_date.strftime('%Y/%m')
        month_label.config(text=f"現在の月: {selected_month}")
        summarize_data()

        # ボタンの有効/無効状態を更新
        next_month_button.config(state="disabled" if new_date == datetime.today().replace(day=1) else "normal")
        prev_month_button.config(state="normal")

    def summarize_data():
        """指定された月の戦績を要約"""
        data = read_csv_by_month(selected_month)
        if not data:
            result_label.config(text="データなし")
            return

        # 戦績データを集計
        total_matches = len(data)
        win_count = sum(1 for row in data if row["result"] == "勝")
        heads_count = sum(1 for row in data if row["coin"] == "表")
        tails_count = total_matches - heads_count
        first_turn_count = sum(1 for row in data if row["turn"] == "先攻")

        win_rate = (win_count / total_matches) * 100 if total_matches else 0
        heads_rate = (heads_count / total_matches) * 100 if total_matches else 0
        first_turn_rate = (first_turn_count / total_matches) * 100 if total_matches else 0

        heads_win_count = sum(1 for row in data if row["coin"] == "表" and row["result"] == "勝")
        tails_win_count = sum(1 for row in data if row["coin"] == "裏" and row["result"] == "勝")
        heads_win_rate = (heads_win_count / heads_count) * 100 if heads_count else 0
        tails_win_rate = (tails_win_count / tails_count) * 100 if tails_count else 0

        heads_first_turn_count = sum(1 for row in data if row["coin"] == "表" and row["turn"] == "先攻")
        tails_first_turn_count = sum(1 for row in data if row["coin"] == "裏" and row["turn"] == "先攻")
        heads_first_turn_rate = (heads_first_turn_count / heads_count) * 100 if heads_count else 0
        tails_first_turn_rate = (tails_first_turn_count / tails_count) * 100 if tails_count else 0

        # 集計結果を表示用の文字列に変換
        summary = (
            f"月間対戦数: {total_matches}\n"
            f"月間勝率: {win_rate:.2f}%\n"
            f"コイン表率: {heads_rate:.2f}%\n"
            f"先攻率: {first_turn_rate:.2f}%\n"
            f"コイン表時勝率: {heads_win_rate:.2f}%\n"
            f"コイン裏時勝率: {tails_win_rate:.2f}%\n"
            f"コイン表時先攻率: {heads_first_turn_rate:.2f}%\n"
            f"コイン裏時先攻率: {tails_first_turn_rate:.2f}%"
        )
        result_label.config(text=summary)

    # ウィンドウ作成
    window = tk.Toplevel()
    window.title("戦績まとめ")
    window.geometry("400x300")
    window_key["match_summary"] = window

    # 選択された月を管理
    selected_month = datetime.today().strftime('%Y/%m')
    month_label = tk.Label(window, text=f"現在の月: {selected_month}")
    month_label.pack()

    # 結果表示用ラベル
    result_label = tk.Label(window, text="", justify="left", anchor="w")
    result_label.pack(fill="both", expand=True, padx=10, pady=10)

    # 月変更用のボタンを作成
    nav_frame = tk.Frame(window)
    nav_frame.pack(pady=10)

    prev_month_button = tk.Button(nav_frame, text="前の月", command=lambda: update_month_display(-1))
    prev_month_button.pack(side="left", padx=5)

    current_month_button = tk.Button(nav_frame, text="現在の月", command=lambda: update_month_display(0))
    current_month_button.pack(side="left", padx=5)

    next_month_button = tk.Button(nav_frame, text="次の月", command=lambda: update_month_display(1))
    next_month_button.pack(side="left", padx=5)

    # 初期状態で次の月ボタンを無効化
    if selected_month == datetime.today().strftime('%Y/%m'):
        next_month_button.config(state="disabled")

    summarize_data()

    # ウィンドウ終了時の処理
    def on_close():
        del window_key["match_summary"]
        window.destroy()

    window.protocol("WM_DELETE_WINDOW", on_close)