import tkinter as tk
from tkinter import messagebox, filedialog
import os
import configparser
import subprocess

SETTINGS_FILE = "settings.ini"


# 設定を読み込み
def load_settings():
    if not os.path.exists(SETTINGS_FILE):
        config = configparser.ConfigParser()
        config["Settings"] = {
            "SaveLocation": os.getcwd(),
            "StartupWindow": "None"
        }
        with open(SETTINGS_FILE, "w") as f:
            config.write(f)
    config = configparser.ConfigParser()
    config.read(SETTINGS_FILE)
    return config


# 設定を保存
def save_settings(save_location, startup_window):
    config = configparser.ConfigParser()
    config["Settings"] = {
        "SaveLocation": save_location,
        "StartupWindow": startup_window
    }
    with open(SETTINGS_FILE, "w") as f:
        config.write(f)


def open_settings_window():
    """設定ウィンドウを表示"""
    settings = load_settings()

    # キーが存在しない場合のデフォルト設定
    save_location = settings["Settings"].get("SaveLocation", os.getcwd())
    startup_windows = settings["Settings"].get("StartupWindow", "").split(",")  # 複数選択対応

    def reset_data():
        """データリセット"""
        if not os.path.exists(save_location):
            messagebox.showinfo("情報", "データファイルが見つかりません。")
            return
        confirm = messagebox.askyesno("確認", "データを完全に削除します。よろしいですか？")
        if confirm:
            try:
                os.remove(os.path.join(save_location, "master_duel_records.csv"))
                messagebox.showinfo("成功", "データをリセットしました。")
            except Exception as e:
                messagebox.showerror("エラー", f"データ削除中にエラーが発生しました: {e}")

    def open_save_location():
        """保存場所を開く"""
        try:
            subprocess.Popen(f'explorer "{save_location}"')
        except Exception as e:
            messagebox.showerror("エラー", f"保存場所を開けませんでした: {e}")

    def choose_save_location():
        """保存場所を選択"""
        nonlocal save_location
        selected_folder = filedialog.askdirectory()
        if selected_folder:
            # パス形式をWindows用（\ に統一）へ変換
            save_location = os.path.normpath(selected_folder)
            save_location_label.config(text=save_location)

    def save_changes():
        """変更を保存し、設定ウィンドウを閉じる"""
        # 保存場所のパスを正規化
        normalized_save_location = os.path.normpath(save_location)
        # 選択されたウィンドウを取得
        selected_windows = [
            window_var.get() for window_var in startup_window_vars if window_var.get()
        ]
        # 設定を保存
        save_settings(normalized_save_location, ",".join(selected_windows))
        # 設定ウィンドウを閉じる
        window.destroy()

    # 設定ウィンドウ作成
    window = tk.Toplevel()
    window.title("設定")
    window.geometry("400x350")

    # データリセット
    tk.Label(window, text="データリセット:").pack(anchor="w", pady=(10, 0), padx=10)
    reset_button = tk.Button(window, text="データをリセット", command=reset_data, bg="red", fg="white")
    reset_button.pack(pady=5)

    # データ保存場所
    tk.Label(window, text="データ保存場所:").pack(anchor="w", padx=10)
    save_location_label = tk.Label(window, text=save_location, wraplength=350, justify="left")
    save_location_label.pack(anchor="w", padx=10)
    choose_save_location_button = tk.Button(window, text="保存場所を選択", command=choose_save_location)
    choose_save_location_button.pack(pady=5)
    open_folder_button = tk.Button(window, text="保存フォルダを開く", command=open_save_location)
    open_folder_button.pack(pady=5)

    # 起動時に開くウィンドウ
    tk.Label(window, text="起動時に開くウィンドウ:").pack(anchor="w", pady=(10, 0), padx=10)

    # 現在選択されているウィンドウと関連付け
    startup_window_vars = [tk.StringVar(value=(option if option in startup_windows else "")) for option in
                           ["RateGraph", "EnvironmentDistribution", "MatchSummary"]]

    # 各ウィンドウのチェックボックスを作成
    tk.Checkbutton(window, text="レート推移", variable=startup_window_vars[0], onvalue="RateGraph", offvalue="").pack(
        anchor="w", padx=20)
    tk.Checkbutton(window, text="環境分布", variable=startup_window_vars[1], onvalue="EnvironmentDistribution",
                   offvalue="").pack(anchor="w", padx=20)
    tk.Checkbutton(window, text="戦績まとめ", variable=startup_window_vars[2], onvalue="MatchSummary",
                   offvalue="").pack(anchor="w", padx=20)

    # 保存ボタン
    save_button = tk.Button(window, text="変更を保存", command=save_changes)
    save_button.pack(pady=10)