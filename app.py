import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

# 1. הגדרות עמוד
st.set_page_config(page_title="דאשבורד נדלן", layout="wide")

# 2. CSS ליישור לימין
st.markdown("""
    <style>
    .stApp { direction: rtl; }
    div[data-testid="stMarkdownContainer"] { text-align: right; }
    </style>
    """, unsafe_allow_html=True)

# 3. טעינת נתונים
@st.cache_data
def load_data():
    return pd.read_csv('israel_housing_dashboard_data.csv')

df = load_data()

# 4. תפריט צד
st.sidebar.title("מצגת פרויקט: שוק הדיור")
slide = st.sidebar.radio("נווט:", [
    "1. פתיח",
    "2. ארכיטקטורת ה-ETL (מאחורי הקלעים)",
    "3. ניתוח: מאקרו וריבית",
    "4. תובנות ומסקנות"
])

# --- שקף 1: פתיח ---
if slide == "1. פתיח":
    st.title("מחירי הדיור בישראל: פרדוקסים ונתונים")
    st.write('ברוכים הבאים למצגת שלי. נבחן כיצד הריבית, אירועי המאקרו ומדדי הנדל"ן נפגשים.')
    st.image("https://images.unsplash.com/photo-1560518883-ce09059eeffa?w=800")

# --- שקף 2: ארכיטקטורת ה-ETL ---
elif slide == "2. ארכיטקטורת ה-ETL (מאחורי הקלעים)":
    st.title("תהליך הנתונים (Pipeline)")
    
    col1, col2 = st.columns(2)
    with col1:
        st.subheader("איך זה עובד?")
        st.markdown("""
        1. **Extract:** שליפה אוטומטית מ-API ממשלתי וקבצי CSV.
        2. **Transform:** ניקוי, אגרגציה וחיבור (Merge) של 3 מקורות נתונים.
        3. **Load:** שמירה ל-"Golden Table" מאוחדת ב-GitHub.
        """)
    with col2:
        st.info("💡 **ערך מוסף:** ביצעתי נירמול לערכי המדד (חלוקה ב-100), מה שמאפשר השוואה ויזואלית מדויקת מול עקומת הריבית.")
    
    st.code("df_final = df1.merge(df2).merge(df3)\ndf_final['index_value'] /= 100", language="python")

# --- שקף 3: ניתוח ---
elif slide == "3. ניתוח: מאקרו וריבית":
    st.title("ניתוח נתונים")
    fig = px.line(df, x='date', y=['index_value', 'interest_rate'], title="מדד מחירי הדיור מול הריבית")
    st.plotly_chart(fig, use_container_width=True)

# --- שקף 4: תובנות ---
elif slide == "4. תובנות ומסקנות":
    st.title("שורה תחתונה")
    st.success("השוק הישראלי גילה עמידות גבוהה למרות העלאות ריבית חדות.")
    st.write("הנתונים מראים שגורמים חיצוניים והיצע משפיעים לעיתים יותר מהריבית.")
