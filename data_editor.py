import tkinter as tk
from tkinter import ttk, messagebox
import csv

CSV_FILE = "master_duel_records.csv"

# グローバル辞書でウィンドウ管理（すべてのウィンドウを統一管理する）
open_windows = {}

def open_data_editor():
    # ウィンドウキー
    window_key = "data_editor"

    # すでに開かれている場合はフォーカスを移す
    if window_key in open_windows:
        open_windows[window_key].lift()
        return

    unsaved_changes = [False]  # 変更状態を追跡する変数（リストでmutableにする）

    def load_csv_data():
        """CSVからデータを読み込んでTreeviewに表示する"""
        tree.delete(*tree.get_children())
        try:
            with open(CSV_FILE, mode="r", encoding="mbcs") as f:
                reader = csv.DictReader(f)
                for row in reader:
                    tree.insert("", "end", values=list(row.values()))
                return reader.fieldnames
        except FileNotFoundError:
            messagebox.showerror("エラー", "CSVファイルが見つかりません。")
        except Exception as e:
            messagebox.showerror("エラー", f"エラー: {e}")
        return []

    def save_csv_data():
        """Treeviewの内容をCSVに保存"""
        try:
            with open(CSV_FILE, mode="w", encoding="mbcs", newline="") as f:
                writer = csv.writer(f)
                writer.writerow(headers)
                for child in tree.get_children():
                    writer.writerow(tree.item(child)["values"])
            unsaved_changes[0] = False  # 保存が成功したので変更フラグをリセット
            messagebox.showinfo("保存完了", "データを保存しました！")
        except Exception as e:
            messagebox.showerror("エラー", f"保存中にエラーが発生しました: {e}")

    def add_row():
        """新しい行を追加"""
        empty_row = [""] * len(headers)
        tree.insert("", "end", values=empty_row)
        unsaved_changes[0] = True  # データに変更があったことを示す

    def delete_row():
        """選択した行を削除"""
        selected_item = tree.selection()
        if not selected_item:
            messagebox.showwarning("警告", "削除する行を選択してください。")
            return
        for item in selected_item:
            tree.delete(item)
        unsaved_changes[0] = True  # データに変更があったことを示す

    def edit_row():
        """選択した行を編集"""
        selected_item = tree.selection()
        if not selected_item:
            messagebox.showwarning("警告", "編集する行を選択してください。")
            return

        selected_item = selected_item[0]
        for i, entry in enumerate(edit_entries):
            tree.set(selected_item, column=headers[i], value=entry.get())
        unsaved_changes[0] = True  # データに変更があったことを示す

    def on_row_select(event):
        """行を選択したときにエントリフィールドに値を設定"""
        selected_item = tree.selection()
        if not selected_item:
            return

        selected_item = selected_item[0]
        selected_data = tree.item(selected_item)["values"]

        # 各エントリフィールドにデータを入力
        for i, entry in enumerate(edit_entries):
            entry.delete(0, tk.END)  # 既存の値を消去
            entry.insert(0, selected_data[i])  # 新しい値を設定

    def on_close():
        """保存状況を確認して閉じる処理"""
        if unsaved_changes[0]:
            # カスタムポップアップを表示
            popup = tk.Toplevel(window)
            popup.title("確認")
            popup.geometry("300x150")
            tk.Label(popup, text="保存されていませんが、閉じてもよいですか？", wraplength=280, justify="center").pack(pady=10)

            def save_and_close():
                """保存して閉じる処理"""
                save_csv_data()
                popup.destroy()
                window.destroy()
                del open_windows[window_key]  # 辞書からエントリを削除

            def discard_and_close():
                """保存せずに閉じる処理"""
                popup.destroy()
                window.destroy()
                del open_windows[window_key]  # 辞書からエントリを削除

            def cancel_close():
                """キャンセル処理"""
                popup.destroy()

            # ボタンを並べる
            button_frame = tk.Frame(popup)
            button_frame.pack(pady=10)
            tk.Button(button_frame, text="保存して閉じる", command=save_and_close).pack(side="left", padx=5)
            tk.Button(button_frame, text="破棄して閉じる", command=discard_and_close).pack(side="left", padx=5)
            tk.Button(button_frame, text="キャンセル", command=cancel_close).pack(side="left", padx=5)

        else:
            window.destroy()
            del open_windows[window_key]  # 辞書からエントリを削除

    # 新しいウィンドウを作成
    window = tk.Toplevel()
    window.title("データ編集")
    window.geometry("800x600")

    # 辞書に記録
    open_windows[window_key] = window

    # TreeviewでCSVデータを表示
    tree = ttk.Treeview(window, columns=[], show="headings", selectmode="browse")
    tree.pack(fill="both", expand=True)

    # CSV読み込み
    headers = load_csv_data()
    if headers:
        tree["columns"] = headers
        for header in headers:
            tree.heading(header, text=header)
            tree.column(header, width=100)

    # 行選択イベントを設定
    tree.bind("<<TreeviewSelect>>", on_row_select)

    # 編集用エントリフィールドのフレーム (2行にレイアウト)
    edit_frame1 = tk.Frame(window)
    edit_frame1.pack(fill="x", padx=5, pady=5)
    edit_frame2 = tk.Frame(window)
    edit_frame2.pack(fill="x", padx=5, pady=5)

    edit_entries = []
    half = len(headers) // 2  # ヘッダーの半分の長さ

    # 1行目のエディタ
    for header in headers[:half]:  # 前半のヘッダー
        field_frame = tk.Frame(edit_frame1)
        field_frame.pack(side="left", padx=5)
        tk.Label(field_frame, text=header).pack()
        entry = tk.Entry(field_frame, width=15)
        entry.pack()
        edit_entries.append(entry)

    # 2行目のエディタ
    for header in headers[half:]:  # 後半のヘッダー
        field_frame = tk.Frame(edit_frame2)
        field_frame.pack(side="left", padx=5)
        tk.Label(field_frame, text=header).pack()
        entry = tk.Entry(field_frame, width=15)
        entry.pack()
        edit_entries.append(entry)

    # ボタンフレーム
    button_frame = tk.Frame(window)
    button_frame.pack(fill="x", pady=10)
    tk.Button(button_frame, text="行を追加", command=add_row).pack(side="left", padx=5)
    tk.Button(button_frame, text="行を削除", command=delete_row).pack(side="left", padx=5)
    tk.Button(button_frame, text="行を編集", command=edit_row).pack(side="left", padx=5)
    tk.Button(button_frame, text="保存", command=save_csv_data).pack(side="left", padx=5)

    # 閉じるボタン処理をウィンドウに登録
    window.protocol("WM_DELETE_WINDOW", on_close)