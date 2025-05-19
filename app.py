import streamlit as st
import pandas as pd
from datetime import datetime

st.title("宿泊予約ステータス表示アプリ")

# ファイルアップロード
uploaded_csv = st.file_uploader("予約CSVファイルをアップロードしてください", type=["csv"])
uploaded_template = st.file_uploader("テンプレートExcelファイル（施設順用）をアップロードしてください", type=["xlsx"])

if uploaded_csv and uploaded_template:
    # CSVとテンプレート読み込み
    df = pd.read_csv(uploaded_csv)
    template_df = pd.read_excel(uploaded_template)

    st.success("CSVファイルとテンプレートを読み込みました！")

    # テンプレートから施設の並び順を取得（1列目、2行目以降）
    facility_order = template_df.iloc[1:, 0].dropna().astype(str).tolist()

    # 表示したい日付を選択
    selected_date = st.date_input("表示したい日付を選んでください")

    if selected_date:
        # チェックイン・チェックアウトを日付型に変換
        df['チェックイン'] = pd.to_datetime(df['チェックイン'], errors='coerce')
        df['チェックアウト'] = pd.to_datetime(df['チェックアウト'], errors='coerce')

        # 結果リスト
        results = []

        for _, row in df.iterrows():
            checkin = row['チェックイン']
            checkout = row['チェックアウト']

            if pd.isna(checkin) or pd.isna(checkout):
                continue

            status = ""
            if checkin.date() == selected_date:
                status = "I"
            elif checkout.date() == selected_date:
                status = "O"
            elif checkin.date() < selected_date < checkout.date():
                status = "S"

            if status:
                date_range = f"{checkin.day}-{checkout.day}"
                results.append({
                    "備考": str(row["物件名"]),
                    "O": "●" if status == "O" else "",
                    "S": "●" if status == "S" else "",
                    "I": "●" if status == "I" else "",
                    "日程": date_range,
                    "人数": row.get("人数", ""),
                    "名前": row.get("ゲスト名", ""),
                    "媒体": row.get("媒体", "")
                })

        result_df = pd.DataFrame(results)

        # 並び順をテンプレートの施設順に合わせる
        result_df["備考"] = pd.Categorical(result_df["備考"], categories=facility_order, ordered=True)
        result_df = result_df.sort_values("備考")

        # 表示
        if not result_df.empty:
            st.markdown("### ✅ 表示結果（コピー＆ペースト可能）")
            st.dataframe(result_df, use_container_width=True)
        else:
            st.warning("指定された日に該当する予約はありません。")
