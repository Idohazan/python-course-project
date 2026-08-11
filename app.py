import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
from pathlib import Path


# ============================================================
# PAGE CONFIGURATION
# ============================================================

st.set_page_config(
    page_title="Israel Housing Market",
    page_icon="🏘️",
    layout="wide",
    initial_sidebar_state="expanded",
)


# ============================================================
# CUSTOM CSS (RTL, Multiselect Box Expansion & Clean UI)
# ============================================================

st.markdown(
    """
    <style>

    /* הגדרת כל האפליקציה כמימין לשמאל וישור לימין */
    .stApp {
        direction: rtl;
        text-align: right;
    }

    .block-container {
        padding-top: 1.5rem;
        padding-bottom: 3rem;
        direction: rtl;
        text-align: right;
    }

    [data-testid="stSidebar"] {
        direction: rtl;
        text-align: right;
    }

    /* יישור כל כותרות הטקסט והפסקאות לימין */
    div[data-testid="stMarkdownContainer"] {
        direction: rtl;
        text-align: right;
    }

    /* יישור קוביות מדדים (Metrics) לימין */
    div[data-testid="stMetricLabel"],
    div[data-testid="stMetricValue"] {
        direction: rtl;
        text-align: right;
    }

    /* יישור תוויות של תיבות בחירה ותאריכים לימין */
    label, .stSelectbox label, .stDateInput label {
        direction: rtl;
        text-align: right;
    }

    /* תיקון קריטי לתיבות ה-Multiselect: הגדלת המשבצת אוטומטית וסידור התגיות כך שלא ייחתכו */
    div[data-baseweb="select"] > div:first-child {
        min-height: 55px !important;
        height: auto !important;
        flex-wrap: wrap !important;
        padding: 6px !important;
        direction: rtl !important;
    }

    [data-baseweb="tag"] {
        direction: rtl !important;
        text-align: right !important;
        background-color: #ff4b4b !important;
        border-radius: 6px !important;
        padding: 2px 8px !important;
        margin: 3px !important;
    }
    
    [data-baseweb="tag"] span {
        color: white !important;
        font-size: 12px !important;
    }

    [data-baseweb="tag"] span[role="button"] {
        transform: scale(0.75);
    }

    /* יישור לשוניות (Tabs) לימין */
    .stTabs [data-baseweb="tab-list"] {
        direction: rtl;
    }

    .hero-box {
        padding: 1.5rem;
        border-radius: 18px;
        background: linear-gradient(
            135deg,
            #eef4ff 0%,
            #f8fbff 100%
        );
        border: 1px solid #dbe7f7;
        margin-bottom: 1.5rem;
        direction: rtl;
        text-align: right;
    }

    .metric-box {
        padding: 1rem;
        border-radius: 14px;
        border: 1px solid #e5e7eb;
        background: #ffffff;
        min-height: 120px;
        direction: rtl;
        text-align: right;
    }

    </style>
    """,
    unsafe_allow_html=True,
)


# ============================================================
# DATA FILE
# ============================================================

DATA_FILE = (
    Path(__file__).parent
    / "israel_housing_dashboard_data.csv"
)


# ============================================================
# LOAD DATA
# ============================================================

@st.cache_data
def load_data(path: str) -> pd.DataFrame:

    data = pd.read_csv(path)

    required_columns = [
        "date",
        "percent",
        "percentYear",
        "index_value",
        "interest_rate",
        "event_name",
        "category",
        "impact",
    ]

    missing_columns = [
        column
        for column in required_columns
        if column not in data.columns
    ]

    if missing_columns:
        raise ValueError(
            f"Missing columns in CSV: {missing_columns}"
        )

    # Date conversion
    data["date"] = pd.to_datetime(
        data["date"],
        errors="coerce"
    )

    # Numeric conversion
    numeric_columns = [
        "percent",
        "percentYear",
        "index_value",
        "interest_rate",
        "impact",
    ]

    for column in numeric_columns:

        data[column] = pd.to_numeric(
            data[column],
            errors="coerce"
        )

    # Remove invalid dates
    data = data.dropna(
        subset=["date"]
    )

    # Sort chronologically
    data = (
        data
        .sort_values("date")
        .reset_index(drop=True)
    )

    # ========================================================
    # FEATURE ENGINEERING
    # ========================================================

    data["year"] = data["date"].dt.year

    data["month"] = data["date"].dt.month

    # 12-month change
    data["index_change_12m"] = (
        data["index_value"]
        .pct_change(12)
        * 100
    )

    # Interest rate monthly change
    data["rate_change"] = (
        data["interest_rate"]
        .diff()
    )

    # Event flag
    data["is_event"] = (
        data["event_name"].notna()
    )

    return data


# ============================================================
# LOAD DATASET
# ============================================================

try:

    df = load_data(
        str(DATA_FILE)
    )

except Exception as e:

    st.error(
        f"לא ניתן לטעון את קובץ הנתונים: {e}"
    )

    st.info(
        "ודא שהקובץ "
        "israel_housing_dashboard_data.csv "
        "נמצא באותה תיקייה של app.py."
    )

    st.stop()


# ============================================================
# MAIN HEADER
# ============================================================

st.title(
    "שוק הדיור בישראל תחת לחץ"
)

st.markdown(
    """
    ### כיצד ריבית, אירועים לאומיים ותנאי השוק משפיעים על מחירי הדיור בישראל?
    """
)

st.divider()


# ============================================================
# SIDEBAR
# ============================================================

st.sidebar.title("🎛️ מסננים")

min_date = (
    df["date"]
    .min()
    .date()
)

max_date = (
    df["date"]
    .max()
    .date()
)

date_range = st.sidebar.date_input(
    "טווח תאריכים",
    value=(min_date, max_date),
    min_value=min_date,
    max_value=max_date,
)

if (
    isinstance(date_range, tuple)
    and len(date_range) == 2
):

    start_date = pd.Timestamp(
        date_range[0]
    )

    end_date = pd.Timestamp(
        date_range[1]
    )

else:

    start_date = pd.Timestamp(
        min_date
    )

    end_date = pd.Timestamp(
        max_date
    )


# --- מסנן קטגוריות אירועים ---
categories = sorted(
    df["category"]
    .dropna()
    .unique()
    .tolist()
)

selected_categories = st.sidebar.multiselect(
    "סוגי קטגוריות",
    categories,
    default=categories,
)

# --- מסנן אירועים ספציפיים דינמי ---
df_events_only = df[df["is_event"]].copy()

if selected_categories:
    available_events = sorted(
        df_events_only[
            df_events_only["category"].isin(selected_categories)
        ]["event_name"]
        .dropna()
        .unique()
        .tolist()
    )
else:
    available_events = []

selected_events = st.sidebar.multiselect(
    "בחר אירועים ספציפיים",
    available_events,
    default=available_events,
)


# ============================================================
# FILTER DATA
# ============================================================

filtered = df[
    (df["date"] >= start_date)
    &
    (df["date"] <= end_date)
].copy()


if selected_categories:

    filtered = filtered[
        (~filtered["is_event"])
        |
        (
            filtered["category"].isin(selected_categories)
            &
            filtered["event_name"].isin(selected_events)
        )
    ]
else:
    filtered = filtered[~filtered["is_event"]]


events = filtered[
    filtered["is_event"]
].copy()


# ============================================================
# TABS
# ============================================================

tab_overview, tab_relationship, tab_events, tab_questions, tab_etl = st.tabs(
    [
        "📊 סקירה",
        "🏦 ריבית מול דיור",
        "⚡ אירועים",
        "🎯 שאלות עסקיות",
        "🔧 ETL",
    ]
)


# ============================================================
# TAB 1 - OVERVIEW
# ============================================================

with tab_overview:

    st.header(
        "📊 תמונת מצב"
    )

    latest = (
        filtered
        .dropna(
            subset=["index_value"]
        )
        .sort_values("date")
        .iloc[-1]
    )

    c1, c2, c3, c4 = st.columns(4)

    with c1:

        st.metric(
            "מדד מחירי דיור",
            f"{latest['index_value']:.3f}"
        )

    with c2:

        st.metric(
            "ריבית בנק ישראל",
            f"{latest['interest_rate']:.2f}%"
        )

    with c3:

        st.metric(
            "שינוי שנתי במחירי הדיור",
            f"{latest['percentYear']:.1f}%"
        )

    with c4:

        st.metric(
            "מספר אירועים",
            len(events)
        )

    st.subheader(
        "📈 התפתחות מחירי הדיור לאורך זמן"
    )

    fig = go.Figure()

    fig.add_trace(
        go.Scatter(
            x=filtered["date"],
            y=filtered["index_value"],
            mode="lines",
            name="מדד מחירי הדיור",
            line=dict(width=3),
            hovertemplate=
                "תאריך: %{x|%m/%Y}"
                "<br>מדד: %{y:.3f}"
                "<extra></extra>",
        )
    )

    # Event markers
    for _, row in events.iterrows():

        fig.add_vline(
            x=row["date"],
            line_width=1,
            line_dash="dot",
            opacity=0.35,
        )

        fig.add_annotation(
            x=row["date"],
            y=row["index_value"],
            text=row["event_name"],
            showarrow=True,
            arrowhead=1,
            ax=0,
            ay=-35,
            font=dict(size=10),
        )

    fig.update_layout(
        height=560,
        hovermode="x unified",
        margin=dict(
            l=20,
            r=20,
            t=30,
            b=20
        ),
        xaxis_title="תאריך",
        yaxis_title="מדד מחירי דיור",
        legend=dict(
            orientation="h",
            y=1.08,
            x=1,
            xanchor="right"
        ),
    )

    st.plotly_chart(
        fig,
        use_container_width=True
    )

    st.info(
        "💡 הגרף מאפשר לזהות שינויי מגמה "
        "ולבחון אותם ביחס לאירועים משמעותיים "
        "שהתרחשו באותה תקופה."
    )


# ============================================================
# TAB 2 - INTEREST RATE
# ============================================================

with tab_relationship:

    st.header(
        "🏦 ריבית בנק ישראל מול שוק הדיור"
    )

    st.markdown(
        """
        ### השאלות המרכזיות

        **1.** כיצד השתנו מחירי הדיור בתקופות של עליית ריבית?

        **2.** האם קיימת תגובה בפיגור של שוק הדיור לשינויי ריבית?
        """
    )

    fig = go.Figure()

    fig.add_trace(
        go.Scatter(
            x=filtered["date"],
            y=filtered["index_value"],
            name="מדד מחירי הדיור",
            mode="lines",
            line=dict(width=3),
            yaxis="y1",
        )
    )

    fig.add_trace(
        go.Scatter(
            x=filtered["date"],
            y=filtered["interest_rate"],
            name="ריבית בנק ישראל",
            mode="lines",
            line=dict(
                width=2,
                dash="dash"
            ),
            yaxis="y2",
        )
    )

    fig.update_layout(
        height=560,
        hovermode="x unified",

        yaxis=dict(
            title="מדד מחירי דיור"
        ),

        yaxis2=dict(
            title="ריבית (%)",
            overlaying="y",
            side="right",
        ),

        margin=dict(
            l=20,
            r=80,
            t=30,
            b=20
        ),

        legend=dict(
            orientation="h",
            y=1.08,
            x=1,
            xanchor="right"
        ),
    )

    st.plotly_chart(
        fig,
        use_container_width=True
    )

    # Lag analysis using selectbox (clean and bug-free under RTL)
    st.subheader(
        "⏱️ ניתוח השפעה בפיגור (Lag Analysis)"
    )

    lag_months = st.selectbox(
        "בחר מספר חודשי פיגור:",
        options=[1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12],
        index=5 # ברירת מחדל 6 חודשים
    )

    lag_df = filtered[
        [
            "date",
            "interest_rate",
            "index_value"
        ]
    ].dropna().copy()

    lag_df["rate_lagged"] = (
        lag_df["interest_rate"]
        .shift(lag_months)
    )

    fig_lag = go.Figure()

    fig_lag.add_trace(
        go.Scatter(
            x=lag_df["date"],
            y=lag_df["index_value"],
            name="מדד מחירי הדיור",
            mode="lines",
            line=dict(width=2, color="blue"),
            yaxis="y1",
        )
    )

    fig_lag.add_trace(
        go.Scatter(
            x=lag_df["date"],
            y=lag_df["rate_lagged"],
            name=f"ריבית בפיגור של {lag_months} חודשים",
            mode="lines",
            line=dict(width=2, color="red", dash="dot"),
            yaxis="y2",
        )
    )

    fig_lag.update_layout(
        height=450,
        hovermode="x unified",
        yaxis=dict(title="מדד מחירי דיור"),
        yaxis2=dict(
            title="ריבית בפיגור (%)",
            overlaying="y",
            side="right",
        ),
        margin=dict(l=20, r=80, t=30, b=20),
        legend=dict(orientation="h", y=1.08, x=1, xanchor="right"),
    )

    st.plotly_chart(
        fig_lag,
        use_container_width=True
    )


# ============================================================
# TAB 3 - EVENTS
# ============================================================

with tab_events:

    st.header(
        "⚡ תגובת שוק הדיור לאירועים"
    )

    st.markdown(
        """
        ### האם אירועים משמעותיים משנים את מגמת השוק?

        בחר אירוע ובדוק את התנהגות מדד מחירי הדיור
        לפני ואחרי האירוע.
        """
    )

    if events.empty:

        st.warning(
            "לא נמצאו אירועים בטווח שנבחר."
        )

    else:

        event_options = (
            events["event_name"]
            .tolist()
        )

        selected_event = st.selectbox(
            "בחר אירוע",
            event_options
        )

        event_row = events[
            events["event_name"]
            == selected_event
        ].iloc[0]

        event_date = event_row["date"]

        window = st.selectbox(
            "בחר חלון סביב האירוע (בחודשים):",
            options=[3, 6, 9, 12, 18, 24],
            index=3 # ברירת מחדל 12 חודשים
        )

        st.markdown(
            f"""
            **אירוע:** {selected_event}

            **תאריך:** {event_date.strftime('%m/%Y')}

            **קטגוריה:** {event_row['category']}

            **עוצמת אירוע:** {event_row['impact']:.0f}/5
            """
        )

        event_window = df[
            (
                df["date"]
                >= event_date
                - pd.DateOffset(
                    months=window
                )
            )
            &
            (
                df["date"]
                <= event_date
                + pd.DateOffset(
                    months=window
                )
            )
        ].copy()

        fig = go.Figure()

        fig.add_trace(
            go.Scatter(
                x=event_window["date"],
                y=event_window["index_value"],
                mode="lines",
                name="מדד מחירי הדיור",
                line=dict(width=3),
            )
        )

        fig.add_vline(
            x=event_date,
            line_width=3,
            line_dash="dash",
        )

        fig.add_annotation(
            x=event_date,
            y=event_window[
                "index_value"
            ].max(),
            text="האירוע",
            showarrow=False,
            yshift=15,
        )

        fig.update_layout(
            height=500,
            hovermode="x unified",
            xaxis_title="תאריך",
            yaxis_title="מדד מחירי דיור",
            margin=dict(
                l=20,
                r=20,
                t=30,
                b=20
            ),
        )

        st.plotly_chart(
            fig,
            use_container_width=True
        )

        # Before / After

        before = df[
            (df["date"] < event_date)
            &
            (
                df["date"]
                >= event_date
                - pd.DateOffset(
                    months=window
                )
            )
        ]["index_value"].dropna()

        after = df[
            (df["date"] > event_date)
            &
            (
                df["date"]
                <= event_date
                + pd.DateOffset(
                    months=window
                )
            )
        ]["index_value"].dropna()

        if len(before) and len(after):

            before_change = (
                (
                    before.iloc[-1]
                    /
                    before.iloc[0]
                )
                - 1
            ) * 100

            after_change = (
                (
                    after.iloc[-1]
                    /
                    after.iloc[0]
                )
                - 1
            ) * 100

            difference = (
                after_change
                - before_change
            )

            b1, b2, b3 = st.columns(3)

            with b1:

                st.metric(
                    "שינוי בתקופה שלפני",
                    f"{before_change:.1f}%"
                )

            with b2:

                st.metric(
                    "שינוי בתקופה שאחרי",
                    f"{after_change:.1f}%"
                )

            with b3:

                st.metric(
                    "הפרש בין התקופות",
                    f"{difference:+.1f}%"
                )

        st.subheader(
            "📋 אירועים בטווח הנבחר"
        )

        st.dataframe(
            events[
                [
                    "date",
                    "event_name",
                    "category",
                    "impact"
                ]
            ]
            .sort_values(
                "date",
                ascending=False
            )
            .rename(
                columns={
                    "date": "תאריך",
                    "event_name": "אירוע",
                    "category": "קטגוריה",
                    "impact": "עוצמה",
                }
            ),
            use_container_width=True,
            hide_index=True,
        )


# ============================================================
# TAB 4 - BUSINESS QUESTIONS
# ============================================================

with tab_questions:

    st.header(
        "🎯 השאלות העסקיות"
    )

    st.markdown(
        """
        הפרויקט נבנה סביב מספר שאלות מרכזיות:

        ### 🏠 1. מגמת מחירי הדיור
        כיצד התפתחו מחירי הדיור בישראל לאורך התקופה?

        ### 🏦 2. השפעת הריבית
        האם קיימת התאמה בין ריבית בנק ישראל
        לבין התנהגות מחירי הדיור?

        ### ⏱️ 3. תגובה בפיגור
        האם שינויי ריבית משפיעים על שוק הדיור
        באופן מיידי או בפיגור?

        ### ⚡ 4. אירועים חריגים
        כיצד הגיב שוק הדיור לאירועים לאומיים משמעותיים?

        ### 📉 5. שינוי מגמה
        האם אירוע משמעותי יצר שינוי זמני
        או שינוי מתמשך במגמת השוק?

        ### 🇮🇱 6. חוסן השוק
        עד כמה שוק הדיור הישראלי חוזר למגמה
        לאחר זעזועים?
        """
    )

    st.subheader(
        "📌 הערה מתודולוגית"
    )

    st.warning(
        "הניתוח מתאר קשרים ודפוסים בנתונים "
        "ואינו מהווה הוכחה לקשר סיבתי. "
        "מחירי הדיור מושפעים מגורמים רבים נוספים "
        "כגון היצע, ביקוש, אשראי, תעסוקה, "
        "מדיניות ממשלתית וציפיות הציבור."
    )


# ============================================================
# TAB 5 - ETL
# ============================================================

with tab_etl:

    st.header(
        "🔧 תהליך ETL ו-Data Preparation"
    )

    st.markdown(
        """
        ### שלבי התהליך

        **1. Extract**

        טעינת נתוני מחירי דיור, ריבית ואירועים
        ממקור הנתונים.

        **2. Transform**

        המרת תאריכים, טיפול בסוגי נתונים,
        ניקוי, מיון וסטנדרטיזציה.

        **3. Feature Engineering**

        יצירת מדדים חדשים כגון שינוי שנתי,
        שינויי ריבית, משתני זמן וסימון אירועים.

        **4. Load & Analyze**

        יצירת Dataset אנליטי אחיד המשמש
        את Pandas ואת ה-Dashboard.
        """
    )

    st.subheader(
        "🔍 בדיקות איכות נתונים"
    )

    quality = {

        "מספר רשומות":
            len(df),

        "מספר עמודות":
            len(df.columns),

        "טווח תאריכים":
            (
                f"{df['date'].min().strftime('%m/%Y')}"
                f" – "
                f"{df['date'].max().strftime('%m/%Y')}"
            ),

        "ערכים חסרים":
            int(
                df.isna()
                .sum()
                .sum()
            ),

        "רשומות אירועים":
            int(
                df["is_event"]
                .sum()
            ),

        "כפילויות":
            int(
                df.duplicated()
                .sum()
            ),
    }

    qcols = st.columns(3)

    for index, (
        label,
        value
    ) in enumerate(
        quality.items()
    ):

        with qcols[index % 3]:

            st.metric(
                label,
                value
            )

    st.subheader(
        "📋 Preview של הנתונים"
    )

    st.dataframe(
        filtered.head(20),
        use_container_width=True,
        hide_index=True,
    )


# ============================================================
# FOOTER
# ============================================================

st.divider()

st.caption(
    "Israel Housing Market Dashboard | "
    "Python • Pandas • ETL • Streamlit"
)
