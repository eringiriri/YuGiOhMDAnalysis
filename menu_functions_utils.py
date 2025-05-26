import csv

# CSVファイル名
CSV_FILE = "master_duel_records.csv"

# グローバル変数でウィンドウ管理
# 他のモジュールで複数のウィンドウを開いた際に、ここで管理するための辞書
window_key = {}

def read_csv_by_month(month):
    """
    指定された月のCSVデータを読み込む。
    :param month: 文字列形式（例：'2023-10'）
    :return: リスト形式のデータ
    """
    data = []
    try:
        with open(CSV_FILE, "r", encoding="mbcs") as f:
            reader = csv.DictReader(f)
            for row in reader:
                if row["date"].startswith(month):  # 日付が指定された月で始まる場合
                    data.append(row)
    except FileNotFoundError:
        # ファイルが存在しない場合は空リストを返す
        pass
    return data