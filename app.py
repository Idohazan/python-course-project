import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

# הגדרות בסיסיות
st.set_page_config(page_title="דאשבורד נדלן ישראל", page_icon="🏘️", layout="wide")

# הזרקת CSS ליישור לימין (RTL)
st.markdown("""
    <style>
    /* הפיכת כל האפליקציה לימין-לשמאל */
    .stApp {
        direction: rtl;
    }
    /* יישור טקסטים, כותרות ותפריטים לימין */
    div.stMarkdown, div.stText, div.stMetric {
        text-align: right !important;
    }
    .st-bb {
        direction: rtl;
    }
    </style>
    """, unsafe_allow_html=True)

@st.cache_data
def load_data():
    df = pd.read_csv('israel_housing_dashboard_data.csv')
    df['date'] = pd.to_datetime(df['date'])
    return df

df = load_data()

st.sidebar.title("שלבי המצגת 📊")
slide = st.sidebar.radio(
    "נווט בין המסכים:", 
    ["1. רקע ושאלת פתיחה", "2. ניתוח אינטראקטיבי (הדאשבורד)", "3. מסקנות וסיכום"]
)

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
# שקף 2: הדאשבורד המרכזי (עם 3 הגרפים)
# ==========================================
elif slide == "2. ניתוח אינטראקטיבי (הדאשבורד)":
    st.title("חוקרים את הנתונים 🔍")
    
    st.sidebar.markdown("---")
    st.sidebar.subheader("מסננים לגרף 🎛️")
    min_year = df['date'].dt.year.min()
    max_year = df['date'].dt.year.max()
    
    selected_years = st.sidebar.slider(
        "בחר טווח שנים:", 
        min_value=min_year, 
        max_value=max_year, 
        value=(min_year, max_year)
    )
    
    df_filtered = df[(df['date'].dt.year >= selected_years[0]) & (df['date'].dt.year <= selected_years[1])]
    
    # KPI Cards
    col1, col2, col3 = st.columns(3)
    col1.metric("ממוצע ריבית לתקופה", f"{df_filtered['interest_rate'].mean():.2f}%")
    col2.metric("שינוי שנתי מקסימלי (דיור)", f"{df_filtered['percentYear'].max()}%")
    col3.metric("אירועי מאקרו בתקופה", df_filtered['event_name'].count())
    
    st.markdown("---")
    
    # גרף 1: מאקרו - ריבית מול אירועים
    st.subheader("1. סביבת המאקרו: ריבית ואירועים היסטוריים")
    fig1 = px.line(df_filtered, x='date', y='interest_rate', labels={'date': 'תאריך', 'interest_rate': 'ריבית (%)'})
    fig1.update_traces(line_color='#1f77b4', name='ריבית בנק ישראל')
    
    # הוספת האירועים כנקודות על הגרף
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
    
    # גרף 2: השוואת ריבית לשינוי במחירי דיור
    st.subheader("2. פרדוקס הריבית: איך השוק מגיב?")
    fig2 = px.line(
        df_filtered, 
        x='date', 
        y=['percentYear', 'interest_rate'],
        labels={'value': 'אחוז (%)', 'date': 'תאריך', 'variable': 'מדדים'}
    )
    newnames = {'percentYear': 'שינוי שנתי בדיור (%)', 'interest_rate': 'ריבית בנק ישראל'}
    fig2.for_each_trace(lambda t: t.update(name=newnames[t.name]))
    st.plotly_chart(fig2, use_container_width=True)

    # גרף 3: מדד מחירי הדיור לאורך זמן
    st.subheader("3. השורה התחתונה: מדד מחירי הדיור (ערך מוחלט)")
    fig3 = px.line(df_filtered, x='date', y='index_value', labels={'date': 'תאריך', 'index_value': 'נקודות מדד'})
    fig3.update_traces(line_color='#2ca02c')
    st.plotly_chart(fig3, use_container_width=True)

# ==========================================
# שקף 3: מסקנות
# ==========================================
elif slide == "3. מסקנות וסיכום":
    st.title("המסקנות שלנו 💡")
    
    st.error("**1. פרדוקס הריבית:** הריבית עלתה במקביל להשתוללות המחירים. השוק לא התקרר מיידית בעקבות העלאות הריבית.")
    st.warning("**2. חוסן השוק:** השוק הישראלי מפגין קשיחות מרשימה. בזמן אירועי קיצון (קורונה, מלחמות), הירידות מתונות מאוד.")
    st.success("**3. השפעת ממשלה:** תוכניות ממשלתיות ('מחיר למשתכן') גורמות לקיפאון זמני בהמתנה, ולאחריו לרוב מגיע זינוק בגלל חוסר בהיצע.")
    
    st.balloons()
