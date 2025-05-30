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

    # 整形
    df.columns = df.columns.str.strip()
    df["物件名"] = df["物件名"].astype(str).str.strip()
    df['チェックイン'] = pd.to_datetime(df['チェックイン'], errors='coerce')
    df['チェックアウト'] = pd.to_datetime(df['チェックアウト'], errors='coerce')

    # テンプレートから施設順を取得
    facility_order = template_df.iloc[1:, 0].dropna().astype(str).tolist()

    selected_date = st.date_input("表示したい日付を選んでください")

    if selected_date:
        output_rows = []

        for facility in facility_order:
            facility_clean = facility.replace(" ", "").strip()
            df["比較用物件名"] = df["物件名"].str.replace(" ", "").str.strip()
            rows = df[df["比較用物件名"] == facility_clean]

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

            # Oのみ or 完全該当なし → 将来予約を探す
            if not (i_flag or s_flag):
                future_rows = rows[rows["チェックイン"].dt.date > selected_date]
                if not future_rows.empty:
                    info_row = future_rows.sort_values("チェックイン").iloc[0]
                elif o_flag:
                    # Oのみで将来予約もなし → 予約なし
                    output_rows.append({
                        "備考": facility,
                        "O": "●",
                        "S": "",
                        "I": "",
                        "日程": "",
                        "人数": "",
                        "名前": "予約なし",
                        "媒体": ""
                    })
                    continue
                else:
                    # 完全に予約なしの施設
                    output_rows.append({
                        "備考": facility,
                        "O": "",
                        "S": "",
                        "I": "",
                        "日程": "",
                        "人数": "",
                        "名前": "予約なし",
                        "媒体": ""
                    })
                    continue

            # 通常の出力
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

        st.markdown("### ✅ 表示結果（コピー＆ペースト可能）")
        st.dataframe(result_df, use_container_width=True)
