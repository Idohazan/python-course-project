import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

# הגדרות עמוד
st.set_page_config(page_title="נדל\"ן ומאקרו - ניתוח נתונים", layout="wide")

# CSS לעיצוב יוקרתי
st.markdown("""
    <style>
    .stApp { direction: rtl; font-family: sans-serif; }
    h1 { color: #1f77b4; }
    </style>
    """, unsafe_allow_html=True)

# טעינת נתונים
@st.cache_data
def load_data():
    return pd.read_csv('israel_housing_dashboard_data.csv')

try:
    df = load_data()
except:
    st.error("לא נמצא קובץ הנתונים. ודא ש-'israel_housing_dashboard_data.csv' נמצא בתיקייה.")
    st.stop()

# תפריט ניווט
menu = ["הפתיח", "הדילמה הכלכלית", "האופרציה הטכנית", "שאלות מחקר", "תובנות מהשטח", "סיכום"]
slide = st.sidebar.radio("ניווט במצגת", menu)

# --- שקף 1: הפתיח ---
if slide == "הפתיח":
    st.title("בין ריבית לנדל\"ן: ניתוח המערכת הישראלית")
    st.markdown("### פרויקט גמר: ניתוח התנהגות שוק הדיור תחת זעזועים מאקרו-כלכליים")
    # תיקון הפרמטר כאן:
    st.image("https://images.unsplash.com/photo-1486406146926-c627a92ad1ab?w=1200", use_container_width=True)
    st.write("בחינה כמותית של הגורמים המניעים את שוק הנדל\"ן בישראל.")

# --- שקף 2: הדילמה הכלכלית ---
elif slide == "הדילמה הכלכלית":
    st.title("הפרדוקס הישראלי")
    col1, col2 = st.columns(2)
    with col1:
        st.subheader("שאלות הפתיחה")
        st.markdown("- כיצד שוק הנדל\"ן מגיב לטלטלות ביטחוניות וחברתיות?")
        st.markdown("- האם הריבית היא אכן הכלי האפקטיבי ביותר לריסון מחירי הדיור?")
    with col2:
        st.info("השוק הישראלי מפגין עמידות יוצאת דופן מול תנודות ריבית. הפרויקט בא לפצח את הקשר הזה.")

# --- שקף 3: מתודולוגיית ה-Pipeline ---
elif slide == "האופרציה הטכנית":
    st.title("מתודולוגיית ה-Data Engineering")
    st.write("תהליך העיבוד (Pipeline) כולל:")
    steps = {
        "Extract": "שאיבת נתונים ממקורות הטרוגניים (ממשלתיים וכלכליים).",
        "Transform": "Data Normalization ו-Feature Engineering לצורך השוואה.",
        "Load": "יצירת 'Golden Table' המהווה את מקור האמת של המערכת."
    }
    for step, desc in steps.items():
        st.markdown(f"**{step}**: {desc}")

# --- שקף 4: שאלות מחקר ---
elif slide == "שאלות מחקר":
    st.title("שאלות מחקר מרכזיות")
    st.markdown("1. קורלציה בין עליית הריבית לקצב עליית המחירים.")
    st.markdown("2. זיהוי נקודות מפנה סביב אירועים היסטוריים.")

# --- שקף 5: ניתוח נתונים ---
elif slide == "תובנות מהשטח":
    st.title("ממצאים אנליטיים")
    fig = px.line(df, x='date', y=['index_value', 'interest_rate'], title="מדד הנדל\"ן מול הריבית")
    st.plotly_chart(fig, use_container_width=True)

# --- שקף 6: סיכום ---
elif slide == "סיכום":
    st.title("מסקנות ומבט לעתיד")
    st.success("השוק הישראלי מושפע מפרמטרים מורכבים מעבר לריבית בלבד.")
    st.balloons()
