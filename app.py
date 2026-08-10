import streamlit as st
import pandas as pd
import plotly.express as px

# 1. הגדרות בסיסיות של העמוד
st.set_page_config(page_title="דאשבורד נדלן ישראל", page_icon="🏘️", layout="wide")
st.title('דאשבורד מחירי הדיור בישראל 🇮🇱')

# 2. טעינת הנתונים (הפונקציה שומרת את הנתונים בזיכרון כדי שהאתר ירוץ מהר)
@st.cache_data
def load_data():
    df = pd.read_csv('israel_housing_dashboard_data.csv')
    # מוודאים שוב שהתאריך הוא תאריך
    df['date'] = pd.to_datetime(df['date'])
    return df

df = load_data()

# 3. תפריט צד (Sidebar) - הוספת המסננים שלנו
st.sidebar.header("מסננים 🎛️")

# יצירת סליידר לשנים
min_year = df['date'].dt.year.min()
max_year = df['date'].dt.year.max()
selected_years = st.sidebar.slider(
    "בחר טווח שנים:", 
    min_value=min_year, 
    max_value=max_year, 
    value=(min_year, max_year) # ברירת המחדל היא כל התקופה
)

# סינון הטבלה לפי השנים שהמשתמש בחר בסליידר
df_filtered = df[(df['date'].dt.year >= selected_years[0]) & (df['date'].dt.year <= selected_years[1])]

# 4. הצגת נתוני KPI מרכזיים בחלק העליון
st.subheader('נתונים מרכזיים לתקופה הנבחרת:')
col1, col2, col3 = st.columns(3)
col1.metric("ממוצע ריבית", f"{df_filtered['interest_rate'].mean():.2f}%")
col2.metric("שינוי שנתי מקסימלי (דיור)", f"{df_filtered['percentYear'].max()}%")
col3.metric("אירועי מאקרו בתקופה", df_filtered['event_name'].count())

# 5. הוספת הגרף המרכזי
st.subheader("מגמת הריבית מול שינוי מחירי הדיור השנתי")
fig = px.line(
    df_filtered, 
    x='date', 
    y=['percentYear', 'interest_rate'],
    labels={'value': 'אחוז (%)', 'date': 'תאריך', 'variable': 'מדדים'},
    title="השוואת ריבית מול עליית מחירי הדיור"
)
# פקודה שמציגה את הגרף ב-Streamlit
st.plotly_chart(fig, use_container_width=True)