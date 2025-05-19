import streamlit as st
import pandas as pd
from datetime import datetime

st.title("宿泊予約ステータス表示アプリ")

# CSVファイルのアップロード
uploaded_file = st.file_uploader("予約CSVファイルをアップロードしてください", type=["csv"])

if uploaded_file:
    df = pd.read_csv(uploaded_file)
    st.success("CSVファイルを読み込みました！")

    # チェックイン・チェックアウト列の整形（datetime形式に変換）
    df['チェックイン'] = pd.to_datetime(df['チェックイン'], errors='coerce')
    df['チェックアウト'] = pd.to_datetime(df['チェックアウト'], errors='coerce')

    # フォームで表示したい日付を選択
    selected_date = st.date_input("表示したい日付を選んでください")

    if selected_date:
        results = []

        for _, row in df.iterrows():
            checkin = row['チェックイン']
            checkout = row['チェックアウト']
            if pd.isna(checkin) or pd.isna(checkout):
                continue

            status = ""
            if checkin.date() == selected_date:
                status = "I"  # チェックイン
            elif checkout.date() == selected_date:
                status = "O"  # チェックアウト
            elif checkin.date() < selected_date < checkout.date():
                status = "S"  # ステイ中

            if status:
                # 表示用の「日程」列を生成（例: 18-20）
                date_range = f"{checkin.day}-{checkout.day}"

                results.append({
                    "備考": row["物件名"],
                    "O": "暖簾" if status == "O" else "",
                    "S": "●" if status == "S" else "",
                    "I": "●" if status == "I" else "",
                    "日程": date_range,
                    "人数": row.get("人数", ""),
                    "名前": row.get("ゲスト名", ""),
                    "媒体": row.get("媒体", "")
                })

        result_df = pd.DataFrame(results)

        if not result_df.empty:
            st.markdown("### 🔽 表示結果（コピー＆ペースト可能）")
            st.dataframe(result_df, use_container_width=True)
        else:
            st.warning("指定された日に該当する予約はありません。")
