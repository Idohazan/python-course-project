import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots

# 1. הגדרות בסיסיות
st.set_page_config(page_title="דאשבורד נדלן ישראל - מרכז אנליטי", page_icon="🏘️", layout="wide")

# 2. קוד CSS ליישור מלא לימין (RTL) של כל רכיבי המערכת
st.markdown("""
    <style>
    .stApp {
        direction: rtl;
    }
    div[data-testid="stMarkdownContainer"] p,
    div[data-testid="stMarkdownContainer"] h1,
    div[data-testid="stMarkdownContainer"] h2,
    div[data-testid="stMarkdownContainer"] h3,
    div[data-testid="stMarkdownContainer"] h4 {
        text-align: right !important;
        direction: rtl !important;
    }
    div[data-testid="stMetricLabel"] *, 
    div[data-testid="stMetricValue"] {
        text-align: right !important;
        direction: rtl !important;
    }
    div[data-testid="stSidebar"] label,
    div.stSlider > label {
        text-align: right !important;
        direction: rtl !important;
        display: block;
        width: 100%;
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

# 4. כותרת ראשית ומסננים גלובליים בסיידבר
st.title("מרכז הניתוח האנליטי: שוק הדיור בישראל 🇮🇱")
st.markdown("סקירה רוחבית של כלל המדדים, האירועים והקשרים הכלכליים.")

st.sidebar.subheader("מסננים גלובליים לכל הגרפים 🎛️")
min_year = int(df['date'].dt.year.min())
max_year = int(df['date'].dt.year.max())

selected_years = st.sidebar.slider(
    "בחר טווח שנים למערכת:", 
    min_value=min_year, 
    max_value=max_year, 
    value=(min_year, max_year)
)

# סינון הנתונים
df_filtered = df[(df['date'].dt.year >= selected_years[0]) & (df['date'].dt.year <= selected_years[1])]

# תצוגת מדדים מרכזיים (KPIs)
col1, col2, col3 = st.columns(3)
col1.metric("ממוצע ריבית לתקופה", f"{df_filtered['interest_rate'].mean():.2f}%")
col2.metric("שינוי שנתי מקסימלי (דיור)", f"{df_filtered['percentYear'].max()}%")
col3.metric("אירועי מאקרו בתקופה", df_filtered['event_name'].count())
st.markdown("---")

# 5. יצירת לשוניות (Tabs) כדי להציג את כל האופציות במקביל
tab1, tab2, tab3, tab4 = st.tabs([
    "🌍 1. ריבית ואירועים", 
    "📈 2. פרדוקס הריבית (YoY)", 
    "🏠 3. מדד המחירים המוחלט", 
    "🔗 4. מבט משולב (דואלי)"
])

# לשונית 1: מאקרו ואירועים
with tab1:
    st.subheader("סביבת המאקרו: ריבית בנק ישראל מול אירועים היסטוריים")
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

# לשונית 2: פרדוקס הריבית
with tab2:
    st.subheader("פרדוקס הריבית: השוואת שינוי שנתי במחירי הדיור מול הריבית")
    fig2 = px.line(
        df_filtered, 
        x='date', 
        y=['percentYear', 'interest_rate'],
        labels={'value': 'אחוז (%)', 'date': 'תאריך', 'variable': 'מדדים'}
    )
    newnames = {'percentYear': 'שינוי שנתי בדיור (%)', 'interest_rate': 'ריבית בנק ישראל'}
    fig2.for_each_trace(lambda t: t.update(name=newnames[t.name]))
    st.plotly_chart(fig2, use_container_width=True)

# לשונית 3: מדד מחירי הדיור המוחלט
with tab3:
    st.subheader("השורה התחתונה: ערך מדד מחירי הדיור לאורך זמן")
    fig3 = px.line(df_filtered, x='date', y='index_value', labels={'date': 'תאריך', 'index_value': 'נקודות מדד'})
    fig3.update_traces(line_color='#2ca02c', name='מדד מחירי הדיור')
    st.plotly_chart(fig3, use_container_width=True)

# לשונית 4: מבט משולב (Dual-Axis)
with tab4:
    st.subheader("מבט על משולב: מדד מחירי הדיור (ציר ראשי) מול ריבית (ציר משני)")
    fig4 = make_subplots(specs=[[{"secondary_y": True}]])
    
    fig4.add_trace(
        go.Scatter(x=df_filtered['date'], y=df_filtered['index_value'], name="מדד מחירי הדיור", line=dict(color='#2ca02c', width=2)),
        secondary_y=False,
    )
    fig4.add_trace(
        go.Scatter(x=df_filtered['date'], y=df_filtered['interest_rate'], name="ריבית בנק ישראל (%)", line=dict(color='#1f77b4', width=2, dash='dot')),
        secondary_y=True,
    )
    
    fig4.update_layout(xaxis_title="תאריך", legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1))
    fig4.update_yaxes(title_text="ערך מדד הדיור", secondary_y=False)
    fig4.update_yaxes(title_text="ריבית בנק ישראל (%)", secondary_y=True)
    
    st.plotly_chart(fig4, use_container_width=True)
