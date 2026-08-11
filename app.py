import streamlit as st
import pandas as pd
import plotly.express as px

# 1. הגדרות בסיסיות (חייב להיות ראשון)
st.set_page_config(page_title="דאשבורד נדלן ישראל", page_icon="🏘️", layout="wide")

# 2. פונקציה לטעינת נתונים
@st.cache_data
def load_data():
    df = pd.read_csv('israel_housing_dashboard_data.csv')
    df['date'] = pd.to_datetime(df['date'])
    return df

df = load_data()

# 3. תפריט הניווט (ה"שקפים" שלנו)
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
    st.markdown("1. מה קרה למחירי הדיור בחודשים הראשונים של מלחמת חרבות ברזל (כשהריבית בשיא)?")
    st.markdown("2. האם תוכניות כמו 'מחיר למשתכן' באמת מקררות את השוק?")
    
    st.success("👈 בואו נעבור לדאשבורד (בתפריט הצד) ונראה מה הנתונים מספרים לנו...")

# ==========================================
# שקף 2: הדאשבורד המרכזי
# ==========================================
elif slide == "2. ניתוח אינטראקטיבי (הדאשבורד)":
    st.title("חוקרים את הנתונים 🔍")
    
    # מסננים שמופיעים בתפריט הצד רק כשאנחנו בשקף הזה
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
    
    # סינון הנתונים לפי הסליידר
    df_filtered = df[(df['date'].dt.year >= selected_years[0]) & (df['date'].dt.year <= selected_years[1])]
    
    # הצגת נתוני KPI
    st.subheader('נתונים מרכזיים לתקופה הנבחרת:')
    col1, col2, col3 = st.columns(3)
    col1.metric("ממוצע ריבית", f"{df_filtered['interest_rate'].mean():.2f}%")
    col2.metric("שינוי שנתי מקסימלי (דיור)", f"{df_filtered['percentYear'].max()}%")
    col3.metric("אירועי מאקרו", df_filtered['event_name'].count())
    
    # הגרף המרכזי
    st.markdown("---")
    fig = px.line(
        df_filtered, 
        x='date', 
        y=['percentYear', 'interest_rate'],
        labels={'value': 'אחוז (%)', 'date': 'תאריך', 'variable': 'מדדים'},
        title="מגמת הריבית מול שינוי מחירי הדיור השנתי"
    )
    
    # שינוי שמות הקווים בגרף שיהיה ברור בעברית
    newnames = {'percentYear': 'שינוי שנתי במחירי הדיור', 'interest_rate': 'ריבית בנק ישראל'}
    fig.for_each_trace(lambda t: t.update(name = newnames[t.name],
                                          legendgroup = newnames[t.name],
                                          hovertemplate = t.hovertemplate.replace(t.name, newnames[t.name])))
    
    st.plotly_chart(fig, use_container_width=True)

# ==========================================
# שקף 3: מסקנות
# ==========================================
elif slide == "3. מסקנות וסיכום":
    st.title("המסקנות שלנו 💡")
    
    st.error("**1. פרדוקס הריבית:** בניגוד לתיאוריה, הריבית עלתה במקביל להשתוללות המחירים. השוק לא התקרר מיידית בעקבות העלאות הריבית.")
    st.warning("**2. חוסן השוק:** השוק הישראלי מפגין קשיחות מרשימה. גם בזמן אירועי קיצון כמו פרוץ מגפת הקורונה או מלחמות, הירידות מתונות מאוד או לא קיימות.")
    st.success("**3. השפעת ממשלה:** תוכניות ממשלתיות (כמו מחיר למשתכן ומחיר מטרה) גורמות לעיתים לקיפאון זמני בהמתנה, ולאחריו לרוב מגיע זינוק מחודש בגלל מחסור בהיצע.")
    
    # חגיגה לסיום
    st.balloons()
