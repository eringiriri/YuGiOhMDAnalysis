import tkinter as tk
from datetime import datetime, timedelta
import matplotlib.pyplot as plt
import matplotlib
import configparser
import os
matplotlib.rc('font', family='Meiryo')
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from menu_functions_utils import read_csv_by_month, window_key  # ユーティリティモジュールを使用

SETTINGS_FILE = "settings.ini"
RANKS = [
    "R1", "B5", "B4", "B3", "B2", "B1",
    "S5", "S4", "S3", "S2", "S1",
    "G5", "G4", "G3", "G2", "G1",
    "P5", "P4", "P3", "P2", "P1",
    "D5", "D4", "D3", "D2", "D1",
    "M5", "M4", "M3", "M2", "M1"
]


def load_graph_type():
    """グラフタイプを設定ファイルから読み込む"""
    if not os.path.exists(SETTINGS_FILE):
        config = configparser.ConfigParser()
        config["Settings"] = {"RateGraphType": "rate"}
        with open(SETTINGS_FILE, "w") as f:
            config.write(f)
        return "rate"
    config = configparser.ConfigParser()
    config.read(SETTINGS_FILE)
    return config["Settings"].get("RateGraphType", "rate")


def save_graph_type(graph_type):
    """グラフタイプを設定ファイルに保存"""
    config = configparser.ConfigParser()
    if os.path.exists(SETTINGS_FILE):
        config.read(SETTINGS_FILE)
    if "Settings" not in config:
        config["Settings"] = {}
    config["Settings"]["RateGraphType"] = graph_type
    with open(SETTINGS_FILE, "w") as f:
        config.write(f)


def show_rate_graph():
    """レート推移・ランク推移の折れ線グラフ表示"""
    if "rate_graph" in window_key:
        window_key["rate_graph"].lift()
        return

    graph_type = load_graph_type()  # 現在のグラフタイプを読み込み

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
        update_graph()

        next_month_button.config(state="disabled" if new_date == datetime.today().replace(day=1) else "normal")
        prev_month_button.config(state="normal")

    def update_graph():
        """指定された月のグラフを更新"""
        data = read_csv_by_month(selected_month)
        figure.clear()
        ax = figure.add_subplot(111)

        if not data:
            # データがない場合の表示
            ax.text(0.5, 0.5, "データなし", fontsize=15, ha='center', va='center')
            ax.set_title(f"{'レート推移' if graph_type_var.get() == 'rate' else 'ランク推移'} ({selected_month})")
        else:
            all_dates = [row["date"] for row in data]  # 日付
            x_indices = list(range(1, len(all_dates) + 1))  # インデックス

            if graph_type_var.get() == "rate":
                rates = [int(row["rate"]) for row in data if row["rate"].isdigit()]
                ax.plot(x_indices, rates, marker="o", label="レート")
                ax.set_ylabel("レート")
            elif graph_type_var.get() == "rank":
                rank_dict = {rank: i for i, rank in enumerate(RANKS)}  # ランクを数値に変換
                ranks = [rank_dict.get(row["rank"], 0) for row in data]
                ax.plot(x_indices, ranks, marker="o", label="ランク")
                ax.set_yticks(range(len(RANKS)))
                ax.set_yticklabels(RANKS, fontsize=8)
                ax.set_ylabel("ランク")

            ax.set_title(f"{'レート推移' if graph_type_var.get() == 'rate' else 'ランク推移'} ({selected_month})")
            ax.set_xlabel("データ登録順")
            ax.set_xticks(x_indices)
            ax.set_xticklabels(all_dates, rotation=45, fontsize=8)
            ax.grid(True)
            ax.legend()

        canvas.draw()

    def toggle_graph_type():
        """グラフタイプを切り替え"""
        current_type = graph_type_var.get()
        new_type = "rank" if current_type == "rate" else "rate"
        graph_type_var.set(new_type)
        save_graph_type(new_type)  # 設定を保存
        update_graph()

    # ウィンドウ作成
    window = tk.Toplevel()
    window.title("レート推移 / ランク推移")
    window.geometry("600x400")
    window_key["rate_graph"] = window

    selected_month = datetime.today().strftime('%Y/%m')
    graph_type_var = tk.StringVar(value=graph_type)  # グラフタイプを保持

    month_label = tk.Label(window, text=f"現在の月: {selected_month}")
    month_label.pack()

    figure = plt.Figure(figsize=(6, 3), dpi=100)
    canvas = FigureCanvasTkAgg(figure, master=window)
    canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)

    # トグルボタンを追加
    toggle_button = tk.Button(window, text="表示切り替え (レート⇔ランク)", command=toggle_graph_type)
    toggle_button.pack(pady=5)

    # 月移動ボタン
    nav_frame = tk.Frame(window)
    nav_frame.pack(pady=10)

    prev_month_button = tk.Button(nav_frame, text="前の月", command=lambda: update_month_display(-1))
    prev_month_button.pack(side="left", padx=5)

    current_month_button = tk.Button(nav_frame, text="現在の月", command=lambda: update_month_display(0))
    current_month_button.pack(side="left", padx=5)

    next_month_button = tk.Button(nav_frame, text="次の月", command=lambda: update_month_display(1))
    next_month_button.pack(side="left", padx=5)

    if selected_month == datetime.today().strftime('%Y/%m'):
        next_month_button.config(state="disabled")

    # グラフを初期化
    update_graph()

    def on_close():
        del window_key["rate_graph"]
        window.destroy()

    window.protocol("WM_DELETE_WINDOW", on_close)