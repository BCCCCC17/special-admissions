import streamlit as st
import pandas as pd

st.set_page_config(page_title="1對1 特殊選才專屬選校系統 (Bilingual)", page_icon="🎓", layout="wide")

st.title("🎓 1對1 特殊選才雙語精準選校系統")
st.caption("Special Admissions Interactive Matching & Search Portal")

@st.cache_data
def load_data():
    return pd.read_csv("special_admissions_data.csv")

df = load_data()

# Sidebar: Student Strategy Center
st.sidebar.header("🎯 學生專屬條件配置 / Settings")

# 1. Location
locations = ["不限 (全區) All"] + sorted(list(df['地區'].unique()))
selected_loc = st.sidebar.selectbox("📍 偏好地區 / Location", locations)

# 2. Written / Practical Test Option
test_option = st.sidebar.radio("✍️ 是否接受「筆試 / 實作」？ Written Test?", ["不限 All", "不需要 (僅備審/口試) No Test", "需要筆試/實作 Need Test"])

# 3. Interview Weight
interview_pref = st.sidebar.selectbox(
    "🗣️ 口試/面試 偏好 Interview",
    ["不限 All", "免面試 (0%) No Interview", "面試佔比低 (≦ 50%) <= 50%", "面試決勝負 (> 50%) > 50%"]
)

# 4. Document Review Weight
doc_pref = st.sidebar.selectbox(
    "📄 書面審查 偏好 Portfolio",
    ["不限 All", "備審比重大 (≧ 50%) >= 50%", "備審比重低 (< 50%) < 50%"]
)

# 5. Fast Advantage Filter
st.sidebar.markdown("---")
st.sidebar.subheader("🌟 個人優勢籌碼 / Advantages")
kw_exp = st.sidebar.checkbox("實驗教育 / 自學 Homeschooling")
kw_cs = st.sidebar.checkbox("資工 / APCS / CS & Coding")
kw_lang = st.sidebar.checkbox("外語 / 雙語 English & Languages")

search_kw = st.sidebar.text_input("🔍 關鍵字 Keywords (CS, NTU, 清華, 化學):", "")

# Filter Logic
filtered_df = df.copy()

if selected_loc != "不限 (全區) All":
    filtered_df = filtered_df[filtered_df['地區'] == selected_loc]

if test_option == "不需要 (僅備審/口試) No Test":
    filtered_df = filtered_df[filtered_df['需筆試實作'] == False]
elif test_option == "需要筆試/實作 Need Test":
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

if kw_exp:
    filtered_df = filtered_df[filtered_df['系所招生對象'].str.contains('實驗教育|自學', na=False)]
if kw_cs:
    filtered_df = filtered_df[filtered_df['Search_Tags'].str.contains('CS|Computer Science', na=False)]
if kw_lang:
    filtered_df = filtered_df[filtered_df['Search_Tags'].str.contains('English|Languages|Bilingual', na=False)]

if search_kw.strip():
    kw = search_kw.strip().lower()
    filtered_df = filtered_df[
        filtered_df['學校名稱簡稱'].str.lower().str.contains(kw, na=False) |
        filtered_df['系所名稱中英'].str.lower().str.contains(kw, na=False) |
        filtered_df['Search_Tags'].str.lower().str.contains(kw, na=False) |
        filtered_df['系所招生對象'].str.lower().str.contains(kw, na=False)
    ]

# Display
st.markdown(f"### 🎯 匹配結果：共 **{len(filtered_df)}** 個目標系所 (Found {len(filtered_df)} programs)")

if len(filtered_df) == 0:
    st.info("💡 條件設定較為嚴格，建議稍微放寬限制！ Please relax search criteria.")
else:
    for idx, row in filtered_df.iterrows():
        doc_p = row['審查比例']
        int_p = row['口試比例']
        test_flag = "✍️ 需筆試/實作 Test" if row['需筆試實作'] else "✅ 免筆試 No Test"
        
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
