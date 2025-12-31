
import streamlit as st
import pandas as pd
import requests
# IMMEDIATE health check response (runs in <100ms)
st.set_page_config(page_title="נדלן חכם", layout="wide")
# Health check - responds instantly
if len(st.secrets.get("dummy", "")) > 0 or st.query_params.get("health"):
st.success("🟢 אפליקציה פעילה")
st.stop()
st.sidebar.header("🔍 מסננים")
city = st.sidebar.text_input("שם עיר:", "תל אביב")
min_price = st.sidebar.number_input("מחיר מינימלי (₪):", min_value=0, value=1000000)
max_price = st.sidebar.number_input("מחיר מקסימלי (₪):", min_value=0, value=10000000)
min_year = st.sidebar.slider("שנת בנייה מינימלית:", 1950, 2025, 2000)
@st.cache_data(ttl=3600)
def get_data(city_name, p_min, p_max, year_min):
url = "https://data.gov.il/api/3/action/datastore_search_sql"
resource_id = "ad53386d-194d-4760-afde-48409b0c0a37"

sql = f"""
SELECT "GUSH","PARCEL","DEALAMOUNT","DEALDATE","FULLADRESS","CITY","YEARBUILT","ROOMS"
FROM "{resource_id}"
WHERE "CITY" LIKE '%{city_name}%'
AND CAST("DEALAMOUNT" AS NUMERIC) >= {p_min}
AND CAST("DEALAMOUNT" AS NUMERIC) <= {p_max}
AND CAST("YEARBUILT" AS NUMERIC) >= {year_min}
ORDER BY "DEALDATE" DESC LIMIT 200
"""

try:
resp = requests.get(url, params={'sql': sql}, timeout=10)
if resp.status_code == 200:
data = resp.json()
if data.get('success'):
return pd.DataFrame(data['result']['records'])
return pd.DataFrame()
except:
return pd.DataFrame()
st.title("📊 נדלן חכם - חיפוש מתקדם")
if st.sidebar.button("🔍 חפש עסקאות", use_container_width=True):
with st.spinner("טוען נתונים..."):
df = get_data(city, min_price, max_price, min_year)

if not df.empty:
df['DEALAMOUNT'] = pd.to_numeric(df['DEALAMOUNT'], errors='coerce')

col1, col2, col3 = st.columns(3)
col1.metric("עסקאות", len(df))
col2.metric("ממוצע", f"₪{df['DEALAMOUNT'].mean():,.0f}")
col3.metric("חציון", f"₪{df['DEALAMOUNT'].median():,.0f}")

st.dataframe(df[['FULLADRESS', 'DEALAMOUNT', 'DEALDATE', 'ROOMS', 'YEARBUILT']], use_container_width=True)
else:
st.warning("לא נמצאו תוצאות. הרחב טווחים.")
st.info("💡 לחץ 'חפש עסקאות' להפעלת החיפוש")
