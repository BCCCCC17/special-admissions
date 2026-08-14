import streamlit as st
import pandas as pd
import re

st.set_page_config(
    page_title="1對1 體育與商管專屬選校系統 (Sports & Business Special Admissions)",
    page_icon="🏅",
    layout="wide"
)

st.title("🏅 1對1 特殊選才專屬選校系統（體育運動與商管專長）")
st.caption("Custom Special Admissions Portal Tailored for Sports, Athletics & Business Majors")

@st.cache_data
def load_data():
    df_loaded = pd.read_csv("special_admissions_data.csv")
    
    # 🛡️ 容錯補齊
    if '審查比例' not in df_loaded.columns or '口試比例' not in df_loaded.columns or '需筆試實作' not in df_loaded.columns:
        def parse_percentages_fast(text):
            s = str(text)
            doc_p = 0
            int_p = 0
            test_p = 0
            m_doc = re.search(r'(?:審查|書面|備審)[^0-9%]*[:：]?\s*(\d+)%', s)
            m_int = re.search(r'(?:口試|面試)[^0-9%]*[:：]?\s*(\d+)%', s)
            m_tst = re.search(r'(?:筆試|實作)[^0-9%]*[:：]?\s*(\d+)%', s)
            if m_doc: doc_p = int(m_doc.group(1))
            if m_int: int_p = int(m_int.group(1))
            if m_tst: test_p = int(m_tst.group(1))
            has_tst = (test_p > 0) or ('筆試' in s) or ('實作' in s)
            return doc_p, int_p, test_p, has_tst

        parsed_res = df_loaded['考試項目'].apply(lambda x: pd.Series(parse_percentages_fast(x)))
        df_loaded['審查比例'] = parsed_res[0]
        df_loaded['口試比例'] = parsed_res[1]
        df_loaded['筆試比例'] = parsed_res[2]
        df_loaded['需筆試實作'] = parsed_res[3]

    if '學校名稱簡稱' not in df_loaded.columns:
        df_loaded['學校名稱簡稱'] = df_loaded['學校名稱']
    if '系所名稱中英' not in df_loaded.columns:
        df_loaded['系所名稱中英'] = df_loaded['系所']
    if '地區' not in df_loaded.columns:
        df_loaded['地區'] = "全區"

    return df_loaded

df = load_data()

# Sidebar: Student Strategy Center
st.sidebar.header("🎯 學生專屬條件配置 / Settings")

# 1. Target Field (Directly Sports / Business / Interdisciplinary)
st.sidebar.subheader("🌟 專長領域篩選 / Target Major")
field_filter = st.sidebar.radio(
    "選擇學生主要目標領域：",
    ["全部 All", "🏅 運動與體育類 (Sports & Athletics)", "💼 商管、經濟與金融 (Business, Management, Finance)", "🌐 跨領域與創新學院 (Interdisciplinary)"]
)

# 2. Location
locations = ["不限 (全區) All"] + sorted(list(df['地區'].astype(str).unique()))
selected_loc = st.sidebar.selectbox("📍 偏好地區 / Location", locations)

# 3. Written / Practical Test Option
test_option = st.sidebar.radio("✍️ 是否接受「筆試 / 實作」？ Written Test?", ["不限 All", "不需要 (僅備審/口試) No Test", "需要筆試/術科實作 Need Test"])

# 4. Interview Weight
interview_pref = st.sidebar.selectbox(
    "🗣️ 口試/面試 偏好 Interview",
    ["不限 All", "免面試 (0%) No Interview", "面試佔比低 (≦ 50%) <= 50%", "面試決勝負 (> 50%) > 50%"]
)

# 5. Document Review Weight
doc_pref = st.sidebar.selectbox(
    "📄 書面審查 偏好 Portfolio",
    ["不限 All", "備審比重大 (≧ 50%) >= 50%", "備審比重低 (< 50%) < 50%"]
)

search_kw = st.sidebar.text_input("🔍 自由關鍵字搜尋 (如: 體育, 國體大, 適應, 企管, 行銷, NTU):", "")

# Filter Logic
filtered_df = df.copy()

# Field filter logic
if field_filter == "🏅 運動與體育類 (Sports & Athletics)":
    filtered_df = filtered_df[filtered_df['Search_Tags'].astype(str).str.contains('Sports|Athletics|體育運動', na=False)]
elif field_filter == "💼 商管、經濟與金融 (Business, Management, Finance)":
    filtered_df = filtered_df[filtered_df['Search_Tags'].astype(str).str.contains('Business|Management|Finance|商管專業', na=False)]
elif field_filter == "🌐 跨領域與創新學院 (Interdisciplinary)":
    filtered_df = filtered_df[filtered_df['Search_Tags'].astype(str).str.contains('Interdisciplinary|跨領域學程', na=False)]

if selected_loc != "不限 (全區) All":
    filtered_df = filtered_df[filtered_df['地區'] == selected_loc]

if test_option == "不需要 (僅備審/口試) No Test":
    filtered_df = filtered_df[filtered_df['需筆試實作'] == False]
elif test_option == "需要筆試/術科實作 Need Test":
    filtered_df = filtered_df[filtered_df['需筆試實作'] == True]

if interview_pref == "免面試 (0%) No Interview":
    filtered_df = filtered_df[filtered_df['口試比例'] == 0]
elif interview_pref == "面試佔比低 (≦ 50%) <= 50%":
    filtered_df = filtered_df[(filtered_df['口試比例'] > 0) & (filtered_df['口試比例'] <= 50)]
elif interview_pref == "面試決勝負 (> 50%) > 50%":
    filtered_df = filtered_df[filtered_df['口試比例'] > 50]

if doc_pref == "備審比重大 (≧ 50%) >= 50%":
    filtered_df = filtered_df[filtered_df['審查比例'] >= 50]
elif doc_pref == "備審比重低 (< 50%) < 50%":
    filtered_df = filtered_df[filtered_df['審查比例'] < 50]

if search_kw.strip():
    kw = search_kw.strip().lower()
    filtered_df = filtered_df[
        filtered_df['學校名稱簡稱'].astype(str).str.lower().str.contains(kw, na=False) |
        filtered_df['系所名稱中英'].astype(str).str.lower().str.contains(kw, na=False) |
        filtered_df['Search_Tags'].astype(str).str.lower().str.contains(kw, na=False) |
        filtered_df['系所招生對象'].astype(str).str.lower().str.contains(kw, na=False)
    ]

# Display
st.markdown(f"### 🎯 匹配結果：共 **{len(filtered_df)}** 個目標系所 (Found {len(filtered_df)} programs)")

if len(filtered_df) == 0:
    st.info("💡 條件設定較為嚴格，建議稍微放寬限制！ Please relax search criteria.")
else:
    for idx, row in filtered_df.iterrows():
        doc_p = row['審查比例']
        int_p = row['口試比例']
        test_flag = "✍️ 需筆試/術科實作 Test" if row['需筆試實作'] else "✅ 免筆試 No Test"
        
        with st.expander(f"🏫 **[{row['地區']}] {row['學校名稱簡稱']}** —— {row['系所名稱中英']} ｜📄審查 Portfolio:{doc_p}% 🗣️口試 Interview:{int_p}% ｜ {test_flag}"):
            col1, col2 = st.columns([1, 1])
            with col1:
                st.markdown(f"**🎯 招生對象與門檻 Target & Criteria：**")
                st.text(row['系所招生對象'])
                st.markdown(f"**🏷️ 搜尋標籤 Search Tags：** `{row['Search_Tags']}`")
            with col2:
                st.markdown(f"**📝 採計比例 Exam Details：**")
                st.text(row['考試項目'])
                st.markdown(f"**📅 日程與簡章連結 Schedule & Links：**")
                st.text(f"{row['日程公告']}\n{row['相關連結']}")
