import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
from pathlib import Path

# ============================================================
# Israel Housing Market Dashboard
# ============================================================

st.set_page_config(
    page_title="Israel Housing Market",
    page_icon="🇮🇱",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ============================================================
# Styling / RTL
# ============================================================

st.markdown(
    """
    <style>
    .block-container {
        padding-top: 1.5rem;
        padding-bottom: 3rem;
        direction: rtl;
    }

    [data-testid="stSidebar"] {
        direction: rtl;
    }

    .hero {
        padding: 1.5rem 1.8rem;
        border-radius: 18px;
        background: linear-gradient(135deg, #eef4ff 0%, #f8fbff 100%);
        border: 1px solid #dbe7f7;
        margin-bottom: 1rem;
    }

    .hero h1 {
        margin-bottom: 0.3rem;
        font-size: 2.35rem;
    }

    .hero p {
        font-size: 1.08rem;
        color: #4b5563;
        margin-bottom: 0;
    }

    .question {
        padding: 1rem 1.2rem;
        border-radius: 14px;
        border: 1px solid #e5e7eb;
        background: #ffffff;
        min-height: 120px;
    }

    .question h4 {
        margin-top: 0;
        margin-bottom: .45rem;
    }
    </style>
    """,
    unsafe_allow_html=True,
)

# ============================================================
# Data Loading
# ============================================================

DATA_FILE = Path(__file__).parent / "israel_housing_dashboard_data.csv"


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
        column for column in required_columns
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
    data = data.sort_values(
        "date"
    ).reset_index(drop=True)

    # ========================================================
    # Feature Engineering
    # ========================================================

    data["year"] = data["date"].dt.year
    data["month"] = data["date"].dt.month

    # 12-month change in housing index
    data["index_change_12m"] = (
        data["index_value"].pct_change(12) * 100
    )

    # Monthly interest rate change
    data["rate_change"] = (
        data["interest_rate"].diff()
    )

    # Event flag
    data["is_event"] = (
        data["event_name"].notna()
    )

    return data


# ============================================================
# Load Dataset
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
        "ודא שהקובץ israel_housing_dashboard_data.csv "
        "נמצא באותה תיקייה של app.py."
    )

    st.stop()


# ============================================================
# Header
# ============================================================

st.markdown(
    """
    <div class="hero">

        <h1>
            🇮🇱 שוק הדיור בישראל תחת לחץ
        </h1>

        <p>
            ניתוח הקשר בין מחירי הדיור, ריבית בנק ישראל
            ואירועים משמעותיים לאורך זמן —
            באמצעות ETL, Pandas ו-Streamlit.
        </p>

    </div>
    """,
    unsafe_allow_html=True,
)


# ============================================================
# Sidebar
# ============================================================

st.sidebar.title("🎛️ מסננים")

min_date = df["date"].min().date()
max_date = df["date"].max().date()

date_range = st.sidebar.date_input(
    "טווח תאריכים",
    value=(min_date, max_date),
    min_value=min_date,
    max_value=max_date,
)

if isinstance(date_range, tuple) and len(date_range) == 2:

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


categories = sorted(
    df["category"]
    .dropna()
    .unique()
    .tolist()
)

selected_categories = st.sidebar.multiselect(
    "סוגי אירועים",
    categories,
    default=categories,
)


filtered = df[
    (df["date"] >= start_date)
    &
    (df["date"] <= end_date)
].copy()


if selected_categories:

    filtered = filtered[
        (~filtered["is_event"])
        |
        (filtered["category"].isin(selected_categories))
    ]


events = filtered[
    filtered["is_event"]
].copy()


st.sidebar.divider()

st.sidebar.caption(
    "מקור הנתונים: "
    "israel_housing_dashboard_data.csv"
)


# ============================================================
# Tabs
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
# TAB 1 - Overview
# ============================================================

with tab_overview:

    latest = (
        filtered
        .dropna(subset=["index_value"])
        .sort_values("date")
        .iloc[-1]
    )

    first = (
        filtered
        .dropna(subset=["index_value"])
        .sort_values("date")
        .iloc[0]
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
            "אירועים בטווח הנבחר",
            f"{len(events)}"
        )

    st.subheader(
        "📈 התפתחות שוק הדיור לאורך זמן"
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

    # Mark events
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
# TAB 2 - Interest Rate vs Housing
# ============================================================

with tab_relationship:

    st.subheader(
        "🏦 האם הריבית קשורה להתנהגות מחירי הדיור?"
    )

    c1, c2 = st.columns(2)

    with c1:

        st.markdown(
            """
            <div class="question">

                <h4>שאלה</h4>

                כיצד השתנו מחירי הדיור
                בתקופות של עליית ריבית?

            </div>
            """,
            unsafe_allow_html=True,
        )

    with c2:

        st.markdown(
            """
            <div class="question">

                <h4>שאלה נוספת</h4>

                האם קיימת תגובה בפיגור
                של שוק הדיור לשינויי ריבית?

            </div>
            """,
            unsafe_allow_html=True,
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

    # Correlation

    corr_data = filtered[
        [
            "index_value",
            "interest_rate"
        ]
    ].dropna()

    if len(corr_data) > 2:

        corr = corr_data[
            "index_value"
        ].corr(
            corr_data["interest_rate"]
        )

        st.metric(
            "מתאם Pearson בין המדדים",
            f"{corr:.2f}"
        )

        st.caption(
            "⚠️ מתאם אינו מוכיח סיבתיות. "
            "הקשר עשוי להיות מושפע ממגמות משותפות "
            "ומגורמים נוספים."
        )

    # Lag analysis

    st.subheader(
        "⏱️ בדיקת תגובה בפיגור"
    )

    lag_months = st.slider(
        "מספר חודשי פיגור",
        min_value=1,
        max_value=12,
        value=6,
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

    lag_corr = lag_df[
        "rate_lagged"
    ].corr(
        lag_df["index_value"]
    )

    st.metric(
        f"מתאם: ריבית בפיגור של {lag_months} חודשים",
        f"{lag_corr:.2f}"
        if pd.notna(lag_corr)
        else "N/A"
    )


# ============================================================
# TAB 3 - Events
# ============================================================

with tab_events:

    st.subheader(
        "⚡ כיצד שוק הדיור מגיב לאירועים?"
    )

    if events.empty:

        st.warning(
            "לא נמצאו אירועים בטווח ובמסננים שנבחרו."
        )

    else:

        event_options = events[
            "event_name"
        ].tolist()

        selected_event = st.selectbox(
            "בחר אירוע לניתוח",
            event_options
        )

        event_row = events[
            events["event_name"] == selected_event
        ].iloc[0]

        event_date = event_row["date"]

        window = st.slider(
            "חלון סביב האירוע (בחודשים)",
            min_value=3,
            max_value=24,
            value=12,
            step=3,
        )

        event_window = df[
            (df["date"] >=
             event_date - pd.DateOffset(months=window))
            &
            (df["date"] <=
             event_date + pd.DateOffset(months=window))
        ].copy()

        st.markdown(
            f"""
            **{selected_event}**

            תאריך: **{event_date.strftime('%m/%Y')}**

            קטגוריה: **{event_row['category']}**

            עוצמת אירוע: **{event_row['impact']:.0f}/5**
            """
        )

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
                df["date"] >=
                event_date -
                pd.DateOffset(months=window)
            )
        ]["index_value"].dropna()

        after = df[
            (df["date"] > event_date)
            &
            (
                df["date"] <=
                event_date +
                pd.DateOffset(months=window)
            )
        ]["index_value"].dropna()

        if len(before) and len(after):

            b1, b2, b3 = st.columns(3)

            before_change = (
                (before.iloc[-1] /
                 before.iloc[0]) - 1
            ) * 100

            after_change = (
                (after.iloc[-1] /
                 after.iloc[0]) - 1
            ) * 100

            difference = (
                after_change -
                before_change
            )

            b1.metric(
                "שינוי בתקופה שלפני",
                f"{before_change:.1f}%"
            )

            b2.metric(
                "שינוי בתקופה שאחרי",
                f"{after_change:.1f}%"
            )

            b3.metric(
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
# TAB 4 - Business Questions
# ============================================================

with tab_questions:

    st.subheader(
        "🎯 שאלות עסקיות"
    )

    questions = [

        (
            "🏠 מגמת מחירי הדיור",
            "כיצד התפתחו מחירי הדיור בישראל לאורך התקופה?"
        ),

        (
            "🏦 השפעת הריבית",
            "האם קיימת התאמה בין ריבית בנק ישראל לבין התנהגות מחירי הדיור?"
        ),

        (
            "⏱️ תגובה בפיגור",
            "האם שינויי ריבית משפיעים על שוק הדיור באופן מיידי או בפיגור?"
        ),

        (
            "⚡ אירועים חריגים",
            "כיצד הגיב שוק הדיור לאירועים לאומיים משמעותיים?"
        ),

        (
            "📉 שינוי מגמה",
            "האם אירוע משמעותי יצר שינוי זמני או שינוי מתמשך במגמת השוק?"
        ),

        (
            "🇮🇱 חוסן השוק",
            "עד כמה שוק הדיור הישראלי חוזר למגמה לאחר זעזועים?"
        ),

    ]

    for i in range(
        0,
        len(questions),
        2
    ):

        cols = st.columns(2)

        for col, (title, question) in zip(
            cols,
            questions[i:i + 2]
        ):

            with col:

                st.markdown(
                    f"""
                    <div class="question">

                        <h4>
                            {title}
                        </h4>

                        <div>
                            {question}
                        </div>

                    </div>
                    """,
                    unsafe_allow_html=True,
                )

        st.write("")

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

    st.subheader(
        "🔧 תהליך ETL ו-Data Preparation"
    )

    etl_cols = st.columns(4)

    steps = [

        (
            "1",
            "Extract",
            "טעינת נתוני מחירי דיור, ריבית ואירועים ממקור הנתונים."
        ),

        (
            "2",
            "Transform",
            "המרת תאריכים, טיפול בסוגי נתונים, ניקוי, מיון וסטנדרטיזציה."
        ),

        (
            "3",
            "Feature Engineering",
            "יצירת שינוי שנתי, שינויי ריבית, משתני זמן וסימון אירועים."
        ),

        (
            "4",
            "Load & Analyze",
            "יצירת Dataset אנליטי אחיד המשמש את Pandas ואת ה-Dashboard."
        ),

    ]

    for col, (
        num,
        title,
        description
    ) in zip(
        etl_cols,
        steps
    ):

        with col:

            st.markdown(
                f"""
                <div class="question">

                    <h4>
                        {num}. {title}
                    </h4>

                    <div>
                        {description}
                    </div>

                </div>
                """,
                unsafe_allow_html=True,
            )

    st.write("")

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
            int(df.isna().sum().sum()),

        "רשומות אירועים":
            int(df["is_event"].sum()),

        "כפילויות":
            int(df.duplicated().sum()),
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
# Footer
# ============================================================

st.divider()

st.caption(
    "Israel Housing Market Dashboard | "
    "Python • Pandas • ETL • Streamlit"
)
