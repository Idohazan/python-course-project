import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

# 1. הגדרות בסיסיות
st.set_page_config(page_title="דאשבורד נדלן ישראל", page_icon="🏘️", layout="wide")

# 2. קוד CSS אגרסיבי ליישור מלא לימין (RTL) של כל רכיבי המערכת
st.markdown("""
    <style>
    /* כיווניות האתר לימין */
    .stApp {
        direction: rtl;
    }
    
    /* יישור כל כותרות הטקסט והפסקאות */
    div[data-testid="stMarkdownContainer"] p,
    div[data-testid="stMarkdownContainer"] h1,
    div[data-testid="stMarkdownContainer"] h2,
    div[data-testid="stMarkdownContainer"] h3,
    div[data-testid="stMarkdownContainer"] h4 {
        text-align: right !important;
        direction: rtl !important;
    }
    
    /* יישור אזור המדדים (KPIs) */
    div[data-testid="stMetricLabel"] *, 
    div[data-testid="stMetricValue"] {
        text-align: right !important;
        direction: rtl !important;
    }
    
    /* יישור תוויות בתפריט הצד (כפתורי רדיו וסליידרים) */
    div[data-testid="stSidebar"] label,
    div.stRadio > label,
    div.stSlider > label {
        text-align: right !important;
        direction: rtl !important;
        display: block;
        width: 100%;
    }
    
    /* יישור טקסט בתוך כפתורי הרדיו עצמם */
    div[role="radiogroup"] label {
        text-align: right !important;
        direction: rtl !important;
    }
    
    /* הפיכת הודעות מערכת (info, warning, success, error) */
    div.stAlert {
        direction: rtl !important;
        text-align: right !important;
    }
    </style>
    """, unsafe_allow_html=True)

# 3. טעינת נתונים
@st.cache_data
def load_data():
    df = pd.read_csv('israel_housing_dashboard_data.csv')
    df['date'] = pd.to_datetime(df['date'])
    return df

df = load_data()

# 4. תפריט הניווט (חלוקה לדפים)
st.sidebar.title("שלבי המצגת 📊")
slide = st.sidebar.radio(
    "נווט בין המסכים:", 
    [
        "1. רקע ושאלת פתיחה", 
        "2. מאקרו: ריבית ואירועים", 
        "3. פרדוקס הריבית (דיור)",
        "4. השורה התחתונה: מדד המחירים",
        "5. מסקנות וסיכום"
    ]
)

# הוספת מסננים רק אם אנחנו באחד מדפי הניתוח
if slide in ["2. מאקרו: ריבית ואירועים", "3. פרדוקס הריבית (דיור)", "4. השורה התחתונה: מדד המחירים"]:
    st.sidebar.markdown("---")
    st.sidebar.subheader("מסננים לגרף 🎛️")
    min_year = int(df['date'].dt.year.min())
    max_year = int(df['date'].dt.year.max())
    
    selected_years = st.sidebar.slider(
        "בחר טווח שנים:", 
        min_value=min_year, 
        max_value=max_year, 
        value=(min_year, max_year)
    )
    
    # סינון הנתונים
    df_filtered = df[(df['date'].dt.year >= selected_years[0]) & (df['date'].dt.year <= selected_years[1])]
    
    # תצוגת נתונים מרכזיים בראש הדף
    col1, col2, col3 = st.columns(3)
    col1.metric("ממוצע ריבית לתקופה", f"{df_filtered['interest_rate'].mean():.2f}%")
    col2.metric("שינוי שנתי מקסימלי (דיור)", f"{df_filtered['percentYear'].max()}%")
    col3.metric("אירועי מאקרו בתקופה", df_filtered['event_name'].count())
    st.markdown("---")


# ==========================================
# שקף 1: רקע
# ==========================================
if slide == "1. רקע ושאלת פתיחה":
    st.title("מחירי הדיור מול הריבית בישראל 🇮🇱")
    st.markdown("### האם הכלכלה באמת פועלת לפי הספר?")
    
    st.info("בכלכלה קלאסית: כשהריבית עולה ⬅️ המשכנתא מתייקרת ⬅️ הביקוש יורד ⬅️ מחירי הדירות יורדים. **אבל מה קורה בישראל?**")
    
    st.markdown("#### שאלות למחשבה לפני שרואים את הנתונים:")
    st.markdown("1. כיצד אירועי קיצון (מלחמות, מגפות) משפיעים על הריבית והמחירים?")
    st.markdown("2. האם תוכניות ממשלתיות ('מחיר למשתכן') באמת מקררות את השוק לטווח ארוך?")
    
    st.success("👈 בואו נעבור לדאשבורד (בתפריט הצד) ונראה מה הנתונים מספרים לנו...")

# ==========================================
# שקף 2: מאקרו - ריבית מול אירועים
# ==========================================
elif slide == "2. מאקרו: ריבית ואירועים":
    st.title("סביבת המאקרו 🌍")
    st.markdown("#### ריבית בנק ישראל לאורך זמן ואירועים היסטוריים")
    
    fig1 = px.line(df_filtered, x='date', y='interest_rate', labels={'date': 'תאריך', 'interest_rate': 'ריבית (%)'})
    fig1.update_traces(line_color='#1f77b4', name='ריבית בנק ישראל')
    
    events_df = df_filtered.dropna(subset=['event_name'])
    if not events_df.empty:
        fig1.add_trace(go.Scatter(
            x=events_df['date'], 
            y=events_df['interest_rate'],
            mode='markers+text',
            marker=dict(color='red', size=12, symbol='star'),
            text=events_df['event_name'],
            textposition='top center',
            name='אירועי מאקרו'
        ))
    st.plotly_chart(fig1, use_container_width=True)

# ==========================================
# שקף 3: השוואת ריבית לשינוי במחירי דיור
# ==========================================
elif slide == "3. פרדוקס הריבית (דיור)":
    st.title("פרדוקס הריבית 📈")
    st.markdown("#### איך שינוי מחירי הדיור (YoY) מגיב להעלאות הריבית?")
    
    fig2 = px.line(
        df_filtered, 
        x='date', 
        y=['percentYear', 'interest_rate'],
        labels={'value': 'אחוז (%)', 'date': 'תאריך', 'variable': 'מדדים'}
    )
    newnames = {'percentYear': 'שינוי שנתי בדיור (%)', 'interest_rate': 'ריבית בנק ישראל'}
    fig2.for_each_trace(lambda t: t.update(name=newnames[t.name]))
    st.plotly_chart(fig2, use_container_width=True)

# ==========================================
# שקף 4: מדד מחירי הדיור (השורה התחתונה)
# ==========================================
elif slide == "4. השורה התחתונה: מדד המחירים":
    st.title("השורה התחתונה 🏠")
    st.markdown("#### מדד מחירי הדיור (ערך מוחלט לאורך זמן)")
    
    fig3 = px.line(df_filtered, x='date', y='index_value', labels={'date': 'תאריך', 'index_value': 'נקודות מדד'})
    fig3.update_traces(line_color='#2ca02c', name='מדד מחירי הדיור')
    st.plotly_chart(fig3, use_container_width=True)

# ==========================================
# שקף 5: מסקנות וסיכום
# ==========================================
elif slide == "5. מסקנות וסיכום":
    st.title("המסקנות שלנו 💡")
    
    st.error("**1. פרדוקס הריבית:** הריבית עלתה במקביל להשתוללות המחירים. השוק לא התקרר מיידית בעקבות העלאות הריבית.")
    st.warning("**2. חוסן השוק:** השוק הישראלי מפגין קשיחות מרשימה. בזמן אירועי קיצון (קורונה, מלחמות), הירידות מתונות מאוד.")
    st.success("**3. השפעת ממשלה:** תוכניות ממשלתיות ('מחיר למשתכן') גורמות לקיפאון זמני בהמתנה, ולאחריו לרוב מגיע זינוק בגלל חוסר בהיצע.")
    
    st.balloons()
