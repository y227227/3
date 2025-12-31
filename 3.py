import streamlit as st
import pandas as pd
import requests

# הגדרות עמוד
st.set_page_config(page_title="ניתוח נדלן חכם", layout="wide")
st.title("📊 מנוע חיפוש עסקאות נדלן - הדגמת SaaS")

st.markdown("""
ברוכים הבאים למערכת ה-SaaS שלך. הקוד הזה מושך נתונים ישירות ממאגר הממשלה (Data.gov.il)
""")

# פונקציה למשיכת נתונים
def get_data(city_name):
    url = "https://data.gov.il/api/3/action/datastore_search"
    # ID של מאגר עסקאות הנדל"ן
    resource_id = "ad53386d-194d-4760-afde-48409b0c0a37"
    
    params = {
        'resource_id': resource_id,
        'q': city_name,
        'limit': 10
    }
    
    try:
        response = requests.get(url, params=params)
        if response.status_code == 200:
            data = response.json()
            records = data['result']['records']
            return pd.DataFrame(records)
        else:
            return pd.DataFrame()
    except Exception as e:
        st.error(f"שגיאת התחברות: {e}")
        return pd.DataFrame()

# ממשק משתמש
city = st.text_input("הזן שם עיר (למשל: תל אביב, חיפה):", "תל אביב - יפו")

if st.button("בצע ניתוח"):
    with st.spinner('מושך נתונים מהשרת...'):
        df = get_data(city)
        
        if not df.empty:
            st.success(f"נמצאו {len(df)} עסקאות אחרונות ב{city}")
            
            # ניקוי והמרת נתונים (הפיכת מחיר למספר)
            if 'DEALAMOUNT' in df.columns:
                df['DEALAMOUNT'] = pd.to_numeric(df['DEALAMOUNT'], errors='coerce')
            
            # הצגת הטבלה - בחרנו עמודות שקיימות ב-API
            cols_to_show = ['GUSH', 'PARCEL', 'DEALAMOUNT', 'DEALDATE', 'FULLADRESS', 'YEARBUILT']
            # מציג רק עמודות שבאמת קיימות בתוצאה
            existing_cols = [c for c in cols_to_show if c in df.columns]
            st.dataframe(df[existing_cols])
            
            # חישוב סטטיסטיקה
            if 'DEALAMOUNT' in df.columns:
                avg_price = df['DEALAMOUNT'].mean()
                st.metric("מחיר ממוצע באזור", f"₪{avg_price:,.0f}")
        else:
            st.error("לא נמצאו נתונים. נסה שם עיר מדויק יותר (למשל 'ירושלים' או 'תל אביב - יפו').")

st.divider()
st.info("הקוד שרץ כאן מוגן בשרת. הלקוח רואה רק את התוצאות האלו.")