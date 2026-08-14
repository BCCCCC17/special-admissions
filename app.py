import streamlit as st
import pandas as pd

# Page config
st.set_page_config(
    page_title="特殊選才雙語檢索系統 Special Admissions Search",
    page_icon="🎓",
    layout="wide"
)

st.title("🎓 大學特殊選才——雙語與地點動態檢索系統")
st.caption("Special Admissions Interactive Matching & Search Portal for High School Students")

# Load data
@st.cache_data
def load_data():
    return pd.read_csv("special_admissions_data.csv")

df = load_data()

# Sidebar Filters
st.sidebar.header("🔍 篩選與搜尋條件 Filters")

# 1. Location filter
locations = ["全部 All"] + sorted(list(df['地區'].unique()))
selected_loc = st.sidebar.selectbox("📍 選擇地區 / Select Location", locations)

# 2. Exam method filter
exam_methods = ["全部 All", "審查 Document Review", "口試 Interview", "筆試/實作 Written/Practical"]
selected_exam = st.sidebar.selectbox("📝 考試方式 / Exam Format", exam_methods)

# 3. Keyword Search Input
search_kw = st.sidebar.text_input("💡 關鍵字搜尋 / Search Keywords", value="", placeholder="例如: CS, NTU, 台北, 實驗教育, 化學...")

st.sidebar.markdown("---")
st.sidebar.info("💡 **提示 Hint:** 學生可以直接輸入英文簡稱 (如 CS, EE, NTU, Hsinchu) 或中文關鍵字進行檢索！")

# Filtering Logic
filtered_df = df.copy()

if selected_loc != "全部 All":
    filtered_df = filtered_df[filtered_df['地區'] == selected_loc]

if selected_exam != "全部 All":
    exam_kw = selected_exam.split()[0]
    filtered_df = filtered_df[filtered_df['考試方式簡記'].str.contains(exam_kw, na=False)]

if search_kw.strip():
    kw = search_kw.strip().lower()
    match_mask = (
        filtered_df['學校名稱'].str.lower().str.contains(kw, na=False) |
        filtered_df['系所'].str.lower().str.contains(kw, na=False) |
        filtered_df['Search_Tags'].str.lower().str.contains(kw, na=False) |
        filtered_df['系所招生對象'].str.lower().str.contains(kw, na=False) |
        filtered_df['地區'].str.lower().str.contains(kw, na=False)
    )
    filtered_df = filtered_df[match_mask]

# Results metrics
st.markdown(f"### 📊 找到 **{len(filtered_df)}** 個符合條件的校系 (Found {len(filtered_df)} matching programs)")

if len(filtered_df) == 0:
    st.warning("⚠️ 沒有找到符合條件的校系，請嘗試縮短關鍵字或重設篩選條件。")
else:
    # Display results as nice interactive cards / table
    for idx, row in filtered_df.iterrows():
        with st.expander(f"🏫 **[{row['地區']}] {row['學校名稱']}** —— {row['系所']} (招生名額: {row['招生名額']} 名)"):
            col1, col2 = st.columns([1, 1])
            with col1:
                st.markdown(f"**📌 考試方式 Format:** {row['考試方式簡記']}")
                st.markdown(f"**🏷️ 搜尋標籤 Search Tags:** `{row['Search_Tags']}`")
                st.markdown(f"**🎯 招生對象與條件 Target & Criteria:**")
                st.text(row['系所招生對象'])
            with col2:
                st.markdown(f"**📝 考試項目與比例 Exam Details:**")
                st.text(row['考試項目'])
                st.markdown(f"**📅 日程公告 Schedule:**")
                st.text(row['日程公告'])
                st.markdown(f"**📞 聯絡與簡章連結 Contact & Links:**")
                st.text(f"{row['聯絡資訊']}\n{row['相關連結']}")

# Option to download current filtered results as CSV
csv_data = filtered_df.to_csv(index=False, encoding='utf-8-sig').encode('utf-8-sig')
st.download_button(
    label="📥 下載目前篩選結果 (Download Search Results CSV)",
    data=csv_data,
    file_name="filtered_special_admissions.csv",
    mime="text/csv"
)
