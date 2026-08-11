# -*- coding: utf-8 -*-
"""
דאשבורד אנליטי - ריבית בנק ישראל מול מחירי דיור
גרסה משופרת: נרטיב שאלות, אלמנטים אינטראקטיביים, גרפים מגוונים
"""

import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

# ==========================================
# 1. הגדרות בסיסיות
# ==========================================
st.set_page_config(page_title="דאשבורד נדלן ישראל", page_icon="🏘️", layout="wide")

# ==========================================
# 2. CSS - יישור מלא לימין (RTL)
# ==========================================
st.markdown("""
    <style>
    .stApp { direction: rtl; }

    div[data-testid="stMarkdownContainer"] p,
    div[data-testid="stMarkdownContainer"] h1,
    div[data-testid="stMarkdownContainer"] h2,
    div[data-testid="stMarkdownContainer"] h3,
    div[data-testid="stMarkdownContainer"] h4 {
        text-align: right !important;
        direction: rtl !important;
    }

    div[data-testid="stMetricLabel"] *,
    div[data-testid="stMetricValue"],
    div[data-testid="stMetricDelta"] {
        text-align: right !important;
        direction: rtl !important;
    }

    div[data-testid="stSidebar"] label,
    div.stRadio > label,
    div.stSlider > label {
        text-align: right !important;
        direction: rtl !important;
        display: block;
        width: 100%;
    }

    div[role="radiogroup"] label {
        text-align: right !important;
        direction: rtl !important;
    }

    div.stAlert {
        direction: rtl !important;
        text-align: right !important;
    }

    button[data-baseweb="tab"] {
        direction: rtl !important;
    }

    /* אינדיקטור התקדמות בסיידבר */
    .slide-progress {
        text-align: right;
        direction: rtl;
        color: #888;
        font-size: 0.85rem;
        margin-bottom: 0.5rem;
    }
    </style>
    """, unsafe_allow_html=True)

# ==========================================
# 3. טעינת נתונים
# ==========================================
@st.cache_data
def load_data():
    df = pd.read_csv('israel_housing_dashboard_data.csv')
    df['date'] = pd.to_datetime(df['date'])
    df = df.sort_values('date').reset_index(drop=True)
    # ממוצע נע ל-12 חודשים על מדד המחירים - לשקף 4
    df['index_value_ma12'] = df['index_value'].rolling(window=12, min_periods=1).mean()
    return df

try:
    df = load_data()
except FileNotFoundError:
    st.error("לא נמצא הקובץ israel_housing_dashboard_data.csv — ודא שהרצת את שלב ה-ETL ושמרת את df_final לקובץ בשם הזה.")
    st.stop()

# רצועות אירועי משבר (טווחי תאריכים) לצביעת רקע בגרף הריבית.
# אפשר להרחיב/לעדכן לפי טבלת israel_macro_events שלך.
CRISIS_PERIODS = [
    {"label": "משבר 2008", "start": "2008-09-01", "end": "2009-06-01"},
    {"label": "קורונה", "start": "2020-03-01", "end": "2021-06-01"},
    {"label": "מלחמת חרבות ברזל", "start": "2023-10-01", "end": "2024-06-01"},
]

# ==========================================
# 4. תפריט הניווט
# ==========================================
SLIDES = [
    "1. מה קורה כשמעלים ריבית? (על הנייר)",
    "2. אז למה בעצם מעלים ריבית מלכתחילה?",
    "3. רגע... למה המחירים לא ירדו? 🤔",
    "4. כמה זה עלה לנו בפועל?",
    "5. אז מי צדק — התיאוריה או המציאות?",
]

st.sidebar.title("שלבי המצגת 📊")
slide = st.sidebar.radio("נווט בין המסכים:", SLIDES)

slide_num = SLIDES.index(slide) + 1
st.sidebar.markdown(f'<div class="slide-progress">שקף {slide_num} מתוך {len(SLIDES)}</div>', unsafe_allow_html=True)
st.sidebar.progress(slide_num / len(SLIDES))

# מסננים רק בדפי הניתוח
if slide in [SLIDES[1], SLIDES[2], SLIDES[3]]:
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

    df_filtered = df[(df['date'].dt.year >= selected_years[0]) & (df['date'].dt.year <= selected_years[1])]

    # KPI-ים עם delta לעומת המחצית הראשונה של הטווח הנבחר, לתחושת מגמה
    mid_point = df_filtered['date'].median()
    first_half = df_filtered[df_filtered['date'] <= mid_point]
    second_half = df_filtered[df_filtered['date'] > mid_point]

    avg_rate_now = df_filtered['interest_rate'].mean()
    avg_rate_delta = second_half['interest_rate'].mean() - first_half['interest_rate'].mean() if not first_half.empty and not second_half.empty else None

    col1, col2, col3 = st.columns(3)
    col1.metric(
        "ממוצע ריבית לתקופה",
        f"{avg_rate_now:.2f}%",
        delta=f"{avg_rate_delta:+.2f}% (מחצית שנייה לעומת ראשונה)" if avg_rate_delta is not None else None,
        delta_color="inverse"
    )
    col2.metric("שינוי שנתי מקסימלי (דיור)", f"{df_filtered['percentYear'].max():.1f}%")
    col3.metric("אירועי מאקרו בתקופה", int(df_filtered['event_name'].count()))
    st.markdown("---")


def add_crisis_shading(fig, df_range):
    """מוסיף רצועות רקע שקופות לתקופות משבר שנופלות בטווח הנתונים המוצג."""
    x_min, x_max = df_range['date'].min(), df_range['date'].max()
    for period in CRISIS_PERIODS:
        start = pd.to_datetime(period["start"])
        end = pd.to_datetime(period["end"])
        if end < x_min or start > x_max:
            continue
        fig.add_vrect(
            x0=max(start, x_min), x1=min(end, x_max),
            fillcolor="red", opacity=0.08, line_width=0,
            annotation_text=period["label"], annotation_position="top left",
            annotation_font_size=11, annotation_font_color="#a33"
        )
    return fig


# ==========================================
# שקף 1: רקע
# ==========================================
if slide == SLIDES[0]:
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
elif slide == SLIDES[1]:
    st.title("סביבת המאקרו 🌍")
    st.markdown("#### ריבית בנק ישראל לאורך זמן, על רקע תקופות משבר")

    fig1 = px.line(df_filtered, x='date', y='interest_rate', labels={'date': 'תאריך', 'interest_rate': 'ריבית (%)'})
    fig1.update_traces(line_color='#1f77b4', name='ריבית בנק ישראל', line_width=2.5)

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

    fig1 = add_crisis_shading(fig1, df_filtered)
    st.plotly_chart(fig1, use_container_width=True)
    st.caption("הרצועות האדומות מסמנות תקופות משבר — שימו לב לכיוון הריבית מיד אחרי כל תקופה.")

# ==========================================
# שקף 3: פרדוקס הריבית - עם ניחוש קהל + שתי תצוגות
# ==========================================
elif slide == SLIDES[2]:
    st.title("פרדוקס הריבית 📈")

    # --- אלמנט אינטראקטיבי: ניחוש הקהל ---
    if "reveal_paradox" not in st.session_state:
        st.session_state.reveal_paradox = False

    if not st.session_state.reveal_paradox:
        st.markdown("#### לפני שחושפים את הגרף — נחשו יחד:")
        st.markdown("הריבית עלתה מ-0.1% לכ-4.75% תוך כשנתיים. מה קרה למחירי הדיור?")
        guess = st.radio(
            "הניחוש שלכם:",
            ["ירדו משמעותית", "נשארו יציבים בערך", "המשיכו לעלות"],
            index=None,
            key="audience_guess"
        )
        if st.button("חשפו את התשובה 🔍") and guess is not None:
            st.session_state.reveal_paradox = True
            st.rerun()
    else:
        st.markdown("#### התשובה: השינוי השנתי במחירי הדיור מול גובה הריבית בפועל")

        tab_line, tab_scatter = st.tabs(["📈 תצוגת ציר זמן", "🔬 תצוגת קורלציה"])

        with tab_line:
            fig2 = px.line(
                df_filtered,
                x='date',
                y=['percentYear', 'interest_rate'],
                labels={'value': 'אחוז (%)', 'date': 'תאריך', 'variable': 'מדדים'}
            )
            newnames = {'percentYear': 'שינוי שנתי בדיור (%)', 'interest_rate': 'ריבית בנק ישראל'}
            fig2.for_each_trace(lambda t: t.update(name=newnames[t.name]))
            st.plotly_chart(fig2, use_container_width=True)

        with tab_scatter:
            st.markdown("אם הכלכלה הקלאסית הייתה צודקת, היינו מצפים לראות מגמה **יורדת**: ריבית גבוהה יותר ↔ שינוי מחירים נמוך יותר.")
            fig_scatter = px.scatter(
                df_filtered,
                x='interest_rate',
                y='percentYear',
                color=df_filtered['date'].dt.year.astype(str),
                labels={'interest_rate': 'ריבית בנק ישראל (%)', 'percentYear': 'שינוי שנתי בדיור (%)', 'color': 'שנה'},
            )
            st.plotly_chart(fig_scatter, use_container_width=True)
            st.caption("כל נקודה = חודש. אם הייתם מצפים לקו יורד ולא רואים כזה — זה בדיוק הפרדוקס.")

        if st.button("↺ נחשו שוב"):
            st.session_state.reveal_paradox = False
            st.rerun()

# ==========================================
# שקף 4: מדד מחירי הדיור - עם ממוצע נע
# ==========================================
elif slide == SLIDES[3]:
    st.title("השורה התחתונה 🏠")
    st.markdown("#### מדד מחירי הדיור לאורך זמן (עם ממוצע נע ל-12 חודשים)")

    fig3 = go.Figure()
    fig3.add_trace(go.Scatter(
        x=df_filtered['date'], y=df_filtered['index_value'],
        mode='lines', name='מדד מחירי הדיור (חודשי)',
        line=dict(color='#2ca02c', width=1), opacity=0.4
    ))
    fig3.add_trace(go.Scatter(
        x=df_filtered['date'], y=df_filtered['index_value_ma12'],
        mode='lines', name='ממוצע נע 12 חודשים',
        line=dict(color='#1a6e1a', width=3)
    ))
    fig3.update_layout(xaxis_title='תאריך', yaxis_title='נקודות מדד')
    st.plotly_chart(fig3, use_container_width=True)
    st.caption("הקו הבהיר מציג את הנתון הגולמי החודשי; הקו הכהה מחליק את הרעש כדי להראות את המגמה האמיתית.")

# ==========================================
# שקף 5: מסקנות וסיכום
# ==========================================
elif slide == SLIDES[4]:
    st.title("המסקנות שלנו 💡")

    total_change = df['index_value'].iloc[-1] / df['index_value'].iloc[0] * 100 - 100
    rate_start, rate_end = df['interest_rate'].iloc[0], df['interest_rate'].iloc[-1]

    st.metric(
        "התמונה המלאה: מדד המחירים לכל התקופה",
        f"{total_change:+.1f}%",
        delta=f"בזמן שהריבית זזה מ-{rate_start:.2f}% ל-{rate_end:.2f}%"
    )
    st.markdown("---")

    st.error("**1. פרדוקס הריבית:** הריבית עלתה במקביל להשתוללות המחירים. השוק לא התקרר מיידית בעקבות העלאות הריבית.")
    st.warning("**2. חוסן השוק:** השוק הישראלי מפגין קשיחות מרשימה. בזמן אירועי קיצון (קורונה, מלחמות), הירידות מתונות מאוד.")
    st.success("**3. השפעת ממשלה:** תוכניות ממשלתיות ('מחיר למשתכן') גורמות לקיפאון זמני בהמתנה, ולאחריו לרוב מגיע זינוק בגלל חוסר בהיצע.")

    st.markdown("#### שאלות פתוחות לדיון:")
    st.markdown("- אם לא ריבית — מה כן ישפיע על מחירי הדיור בישראל?")
    st.markdown("- האם נפח העסקאות (לא המחיר) הוא בעצם המשתנה שכן מגיב לריבית?")

    st.balloons()
