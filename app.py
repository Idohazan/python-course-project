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
    .css-1544g2n { padding: 2rem; }
    </style>
    """, unsafe_allow_html=True)

# טעינת נתונים
@st.cache_data
def load_data():
    return pd.read_csv('israel_housing_dashboard_data.csv')

df = load_data()

# תפריט ניווט
menu = ["הפתיח", "הדילמה הכלכלית", "מתודולוגיית ה-Pipeline", "שאלות מחקר", "תובנות מהשטח", "סיכום"]
slide = st.sidebar.radio("ניווט במצגת", menu)

# --- שקף 1: הפתיח ---
if slide == "הפתיח":
    st.title("בין ריבית לנדל\"ן: ניתוח המערכת הישראלית")
    st.markdown("### פרויקט גמר: ניתוח התנהגות שוק הדיור תחת זעזועים מאקרו-כלכליים")
    st.image("https://images.unsplash.com/photo-1486406146926-c627a92ad1ab?w=1200", use_column_width=True)
    st.write("בחינה כמותית של הגורמים המניעים את שוק הנדל\"ן בישראל.")

# --- שקף 2: הדילמה הכלכלית ---
elif slide == "הדילמה הכלכלית":
    st.title("הפרדוקס הישראלי")
    col1, col2 = st.columns(2)
    with col1:
        st.subheader("שאלות הפתיחה")
        st.markdown("- כיצד שוק הנדל\"ן מגיב לטלטלות ביטחוניות וחברתיות?")
        st.markdown("- האם הריבית היא אכן הכלי האפקטיבי ביותר לריסון מחירי הדיור בישראל?")
        st.markdown("- מהו הקשר בין המדיניות המוניטרית של בנק ישראל לבין התנהגות הקונים?")
    with col2:
        st.info("בניגוד לכלכלות מערביות קלאסיות, השוק הישראלי מפגין עמידות מול תנודות ריבית. הפרויקט בא לפצח למה.")

# --- שקף 3: מתודולוגיית ה-Pipeline ---
elif slide == "האופרציה הטכנית":
    st.title("מתודולוגיית ה-Data Engineering")
    st.write("בניתי תהליך ETL מורכב להפיכת דאטה גולמי לנכס אנליטי:")
    
    steps = {
        "Extract": "שאיבת נתונים ממקורות הטרוגניים (ממשלתיים, כלכליים ואירועי מאקרו).",
        "Transform": "ניקוי נתונים, סנכרון ציר זמן (Alignment) ו-Feature Engineering (נירמול מדדים לצורך השוואה).",
        "Load": "יצירת 'Golden Table' מרוכזת, המהווה את מקור האמת של המערכת."
    }
    for step, desc in steps.items():
        st.markdown(f"**{step}**: {desc}")

# --- שקף 4: שאלות מחקר ---
elif slide == "שאלות מחקר":
    st.title("השאלות שמובילות את הניתוח")
    st.markdown("1. האם קיימת קורלציה ישירה בין עליית הריבית לבין קצב עליית המחירים?")
    st.markdown("2. זיהוי נקודות מפנה (Turning Points) סביב אירועים היסטוריים.")
    st.markdown("3. הערכת עוצמת ההשפעה של מדיניות בנק ישראל אל מול 'כוחות השוק'.")

# --- שקף 5: ניתוח נתונים (גרפים) ---
elif slide == "תובנות מהשטח":
    st.title("ממצאים אנליטיים")
    tab1, tab2 = st.tabs(["מבט מאקרו-משולב", "ניתוח תנודתיות"])
    
    with tab1:
        fig = px.line(df, x='date', y=['index_value', 'interest_rate'], title="מדד הנדל\"ן מול הריבית (מנומל)")
        st.plotly_chart(fig, use_column_width=True)
        
    with tab2:
        st.write("ניתוח זה מראה כיצד אירועים ספציפיים משנים את כיוון המדד.")

# --- שקף 6: סיכום ---
elif slide == "סיכום":
    st.title("מסקנות ומבט לעתיד")
    st.success("הנדל\"ן בישראל מושפע מפרמטרים מורכבים מעבר לריבית בלבד.")
    st.markdown("- **עמידות:** השוק מגיב באיטיות לשינויי ריבית.")
    st.markdown("- **פסיכולוגיה:** אירועי מאקרו יוצרים 'רעש' שמשפיע על היקף העסקאות.")
    st.balloons()
