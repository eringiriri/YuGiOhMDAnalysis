import tkinter as tk
from datetime import datetime, timedelta
import matplotlib.pyplot as plt
from collections import Counter
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from menu_functions_utils import read_csv_by_month, window_key
import configparser
import os

SETTINGS_FILE = "settings.ini"


# 設定ファイルからグラフタイプ取得
def load_graph_type():
    if not os.path.exists(SETTINGS_FILE):
        config = configparser.ConfigParser()
        config["Settings"] = {"GraphType": "pie"}
        with open(SETTINGS_FILE, "w") as f:
            config.write(f)
        return "pie"
    config = configparser.ConfigParser()
    config.read(SETTINGS_FILE)
    return config["Settings"].get("GraphType", "pie")


# 設定ファイルにグラフタイプ保存
def save_graph_type(graph_type):
    config = configparser.ConfigParser()
    config["Settings"] = {"GraphType": graph_type}
    with open(SETTINGS_FILE, "w") as f:
        config.write(f)


def show_environment_distribution():
    """環境分布の円グラフを表示"""
    if "environment_distribution" in window_key:
        window_key["environment_distribution"].lift()
        return

    # 設定読み込み
    graph_type = load_graph_type()

    def update_month_display(change):
        nonlocal selected_month
        new_date = datetime.strptime(selected_month, '%Y/%m')
        if change == 0:
            new_date = datetime.today().replace(day=1)
        elif change == 1:
            new_date = (new_date.replace(day=28) + timedelta(days=4)).replace(day=1)
        elif change == -1:
            new_date = (new_date.replace(day=1) - timedelta(days=1)).replace(day=1)
        if new_date > datetime.today().replace(day=1):
            return
        selected_month = new_date.strftime('%Y/%m')
        month_label.config(text=f"現在の月: {selected_month}")
        update_graph()
        next_month_button.config(state="disabled" if new_date == datetime.today().replace(day=1) else "normal")
        prev_month_button.config(state="normal")

    def update_graph():
        data = read_csv_by_month(selected_month)
        figure.clear()
        ax = figure.add_subplot(111)
        if not data:
            ax.text(0.5, 0.5, "データなし", fontsize=15, ha='center', va='center')
            ax.set_title(f"環境分布 ({selected_month})")
        else:
            deck_counts = Counter(row["opponent_deck"] for row in data)
            labels = list(deck_counts.keys())
            sizes = list(deck_counts.values())

            if graph_type_var.get() == "pie":
                ax.pie(sizes, labels=labels, autopct="%1.1f%%", startangle=90)
            elif graph_type_var.get() == "bar":
                ax.bar(labels, sizes)
                ax.set_xticks(range(len(labels)))  # X軸の位置を設定
                ax.set_xticklabels(labels, rotation=45, fontsize=8)
                ax.set_ylabel("使用デッキ数")

            ax.set_title(f"環境分布 ({selected_month})")
        canvas.draw()

    def toggle_graph_type():
        """円グラフと棒グラフを切り替える"""
        current_type = graph_type_var.get()
        new_type = "bar" if current_type == "pie" else "pie"
        graph_type_var.set(new_type)
        save_graph_type(new_type)
        update_graph()

    # 新しいウィンドウ作成
    window = tk.Toplevel()
    window.title("環境分布")
    window.geometry("500x400")
    window_key["environment_distribution"] = window

    # 現在のグラフタイプを保持
    graph_type_var = tk.StringVar(value=graph_type)

    selected_month = datetime.today().strftime('%Y/%m')
    month_label = tk.Label(window, text=f"現在の月: {selected_month}")
    month_label.pack()

    figure = plt.Figure(figsize=(5, 3), dpi=100)
    canvas = FigureCanvasTkAgg(figure, master=window)
    canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)

    # トグルボタン
    toggle_button = tk.Button(window, text="表示切り替え (円⇔棒)", command=toggle_graph_type)
    toggle_button.pack(pady=5)

    # ナビゲーションフレーム
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

    update_graph()

    def on_close():
        del window_key["environment_distribution"]
        window.destroy()

    window.protocol("WM_DELETE_WINDOW", on_close)