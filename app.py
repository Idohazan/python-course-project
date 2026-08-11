import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

# הגדרות עמוד - Layout רחב ומקצועי
st.set_page_config(page_title="Data Analytics Portfolio", layout="wide")

# CSS מתקדם למראה נקי (כרטיסיות ומרווחים)
st.markdown("""
    <style>
    .stApp { direction: rtl; font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; }
    .css-1544g2n { padding: 2rem; }
    h1, h2, h3 { color: #1e3d59; }
    .card { background-color: #f8f9fa; padding: 20px; border-radius: 10px; border: 1px solid #e9ecef; }
    </style>
    """, unsafe_allow_html=True)

# טעינת נתונים
@st.cache_data
def load_data():
    return pd.read_csv('israel_housing_dashboard_data.csv')

try:
    df = load_data()
except:
    st.error("שגיאה בטעינת הנתונים: ודא שקובץ ה-CSV קיים בנתיב המוגדר.")
    st.stop()

# ניווט צדדי (Side Panel)
with st.sidebar:
    st.title("ניווט במצגת")
    slide = st.radio("בחר שלב:", [
        "פתיח: תמונת מצב", 
        "הדילמה הכלכלית", 
        "Data Engineering Pipeline", 
        "שאלות עסקיות", 
        "ניתוח אנליטי", 
        "מסקנות אסטרטגיות"
    ])
    st.markdown("---")
    st.caption("פרויקט גמר: ניתוח שוק הדיור")

# --- שקופיות ---

if slide == "פתיח: תמונת מצב":
    st.title("בין ריבית לנדל\"ן: ניתוח המערכת הישראלית")
    st.markdown("### פרויקט גמר: התנהגות שוק הדיור תחת זעזועים מאקרו-כלכליים")
    
    col1, col2 = st.columns([2, 1])
    with col1:
        st.image("https://images.unsplash.com/photo-1486406146926-c627a92ad1ab?w=1200", use_container_width=True)
    with col2:
        st.markdown("<div class='card'>", unsafe_allow_html=True)
        st.write("הפרויקט בוחן את הקשר המורכב בין המדיניות המוניטרית של בנק ישראל לבין התנהגות מחירי הדיור. ננסה להבין אם השוק הישראלי פועל לפי התיאוריות הכלכליות הקלאסיות.")
        st.markdown("</div>", unsafe_allow_html=True)

elif slide == "הדילמה הכלכלית":
    st.title("הפרדוקס: שוק עמיד או בועה?")
    st.markdown("---")
    c1, c2, c3 = st.columns(3)
    c1.metric("טלטלות מאקרו", "זיהוי משברים")
    c2.metric("ריבית בנק ישראל", "דינמיקה מוניטרית")
    c3.metric("תגובת השוק", "קשיחות מחירים")
    
    st.subheader("שאלות ליבה למחקר:")
    st.info("איך מדינה רוויית אירועים ביטחוניים ופוליטיים מייצרת שוק נדל\"ן בעל אופי התנהגותי שונה מכלכלות המערב?")
    st.write("האם העלאת ריבית היא אכן 'התרופה' לבלימת מחירי הדיור, או שמא גורמים מבניים (היצע, פסיכולוגיה) דומיננטיים יותר?")

elif slide == "Data Engineering Pipeline":
    st.title("ארכיטקטורת נתונים (Data Pipeline)")
    st.markdown("---")
    
    # תצוגה ויזואלית של ה-Pipeline
    col1, col2, col3 = st.columns(3)
    with col1:
        st.subheader("1. Extract")
        st.write("איסוף נתונים ממקורות הטרוגניים (ממשלתיים, כלכליים ומדדי אירועים).")
    with col2:
        st.subheader("2. Transform")
        st.write("Data Normalization & Standardization: עיבוד נתונים גולמיים לכדי מדדים ברי-השוואה (Standardized Metrics) למניעת עיוותים סטטיסטיים.")
    with col3:
        st.subheader("3. Load")
        st.write("יצירת Golden Table מאוחדת ומוכנה לצריכה אנליטית (High-Availability Database).")
    
    st.code("""
# Feature Engineering Process
df_final = df_housing.merge(df_rates, on='date').merge(df_events, on='date')
df_final['index_value'] = df_final['index_value'] / 100  # Normalization
    """, language="python")

elif slide == "שאלות עסקיות":
    st.title("שאלות עסקיות למחקר")
    st.markdown("""
    * **התאמה למחזוריות:** האם קיים פיגור (Lag) בין העלאת הריבית לבין בלימת עליות המחירים?
    * **שבירת קורלציות:** מהם 'נקודות השבר' שבהן השוק התעלם מהנחיות בנק ישראל?
    * **השוואתיות:** כיצד השפיעו אירועי מאקרו על העדפות הקונים?
    """)

elif slide == "ניתוח אנליטי":
    st.title("ניתוח וממצאים")
    
    # KPIs למעלה
    c1, c2 = st.columns(2)
    c1.metric("ריבית ממוצעת לתקופה", f"{df['interest_rate'].mean():.2f}%")
    c2.metric("סטיית תקן מדדית", f"{df['index_value'].std():.2f}")
    
    fig = px.line(df, x='date', y=['index_value', 'interest_rate'], 
                  title="קורלציה: מדד מחירי הדיור (מנורמל) vs ריבית",
                  labels={'value': 'ערך מדד / אחוזי ריבית', 'date': 'ציר זמן'})
    st.plotly_chart(fig, use_container_width=True)

elif slide == "מסקנות אסטרטגיות":
    st.title("מסקנות וסיכום")
    st.success("השוק הישראלי מפגין 'עמידות מושרשת' - הנתונים מראים שגורמים מבניים (היצע) גוברים על השפעות מוניטריות בטווח הקצר.")
    st.markdown("### סיכום אופרטיבי:")
    st.write("הוכח כי קיים נתק בין התיאוריה הכלכלית הקלאסית למציאות בשטח בישראל. הנתונים מאפשרים לנו בעתיד לבנות מודל חיזוי מדויק יותר.")
    st.balloons()
