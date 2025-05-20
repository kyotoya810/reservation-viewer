import streamlit as st
import pandas as pd
from datetime import datetime

st.title("宿泊予約ステータス表示アプリ")

uploaded_csv = st.file_uploader("予約CSVファイルをアップロードしてください", type=["csv"])
uploaded_template = st.file_uploader("テンプレートExcelファイル（施設順用）をアップロードしてください", type=["xlsx"])

if uploaded_csv and uploaded_template:
    df = pd.read_csv(uploaded_csv)
    template_df = pd.read_excel(uploaded_template)

    st.success("CSVファイルとテンプレートを読み込みました！")

    # 列名を正規化（空白削除など）
    df.columns = df.columns.str.strip()

    # テンプレートから施設順を取得（2行目以降の1列目）
    facility_order = template_df.iloc[1:, 0].dropna().astype(str).tolist()

    selected_date = st.date_input("表示したい日付を選んでください")

    if selected_date:
        df['チェックイン'] = pd.to_datetime(df['チェックイン'], errors='coerce')
        df['チェックアウト'] = pd.to_datetime(df['チェックアウト'], errors='coerce')

        output_rows = []

        for facility in facility_order:
            facility_clean = facility.strip()
            rows = df[df["物件名"].astype(str).str.strip() == facility_clean]

            o_flag = s_flag = i_flag = False
            info_row = None

            for _, row in rows.iterrows():
                checkin = row['チェックイン']
                checkout = row['チェックアウト']
                if pd.isna(checkin) or pd.isna(checkout):
                    continue

                if checkin.date() == selected_date:
                    i_flag = True
                    info_row = row
                elif checkin.date() < selected_date < checkout.date():
                    s_flag = True
                    if not i_flag:
                        info_row = row
                elif checkout.date() == selected_date:
                    o_flag = True

            # Oのみ → 次の予約
            if o_flag and not (i_flag or s_flag):
                future_rows = rows[rows["チェックイン"].dt.date > selected_date]
                if not future_rows.empty:
                    info_row = future_rows.sort_values("チェックイン").iloc[0]

            if o_flag or s_flag or i_flag:
                output_rows.append({
                    "備考": facility,
                    "O": "●" if o_flag else "",
                    "S": "●" if s_flag else "",
                    "I": "●" if i_flag else "",
                    "日程": f"{info_row['チェックイン'].day}-{info_row['チェックアウト'].day}" if info_row is not None else "",
                    "人数": info_row["ゲスト数"] if info_row is not None and "ゲスト数" in info_row else "",
                    "名前": info_row["ゲスト名"] if info_row is not None and "ゲスト名" in info_row else "",
                    "媒体": info_row["予約サイト"] if info_row is not None and "予約サイト" in info_row else ""
                })

        result_df = pd.DataFrame(output_rows)

        if not result_df.empty:
            st.markdown("### ✅ 表示結果（コピー＆ペースト可能）")
            st.dataframe(result_df, use_container_width=True)
        else:
            st.warning("指定された日に該当する予約はありません。")
