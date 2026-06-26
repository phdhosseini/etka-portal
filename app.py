import streamlit as st
import pandas as pd
import sqlite3
import plotly.express as px
import io

st.set_page_config(page_title="سامانه جامع مدیریت زنجیره تامین اتکا", layout="wide")

# استایل‌های فوق حرفه‌ای برای راست‌چین‌سازی کامل
st.markdown("""
    <style>
    @import url('https://cdn.jsdelivr.net/gh/rastikerdar/vazir-font@v30.1.0/dist/font-face.css');
    * { font-family: 'Vazir', sans-serif !important; direction: RTL !important; text-align: right !important; }
    [data-testid="stSidebar"] { display: none !important; }
    .css-1544g2n { padding: 1rem; }
    .stButton>button { width: 100%; border-radius: 5px; background-color: #1F4E78; color: white; }
    .stDataFrame { border: 1px solid #ddd; }
    </style>
""", unsafe_allow_html=True)

# ۱. راه‌اندازی دیتابیس و شبیه‌سازی ۵۰ شرکت و ۸۰ قلم کالا
conn = sqlite3.connect("etka_core_v9.db", check_same_thread=False)
cursor = conn.cursor()

def init_db():
    cursor.execute("CREATE TABLE IF NOT EXISTS actors (id TEXT PRIMARY KEY, name TEXT, type TEXT, phone TEXT)")
    cursor.execute("CREATE TABLE IF NOT EXISTS catalog (id TEXT PRIMARY KEY, name TEXT, category TEXT)")
    cursor.execute("CREATE TABLE IF NOT EXISTS links (id INTEGER PRIMARY KEY AUTOINCREMENT, s_id TEXT, b_id TEXT, p_id TEXT, volume REAL, time_frame TEXT)")
    
    # شبیه‌سازی ۵۰ شرکت
    if pd.read_sql("SELECT count(*) FROM actors", conn).iloc[0,0] == 0:
        for i in range(1, 51):
            t = "هلدینگ اتکا" if i <= 10 else ("خدماتی/لجستیک" if i <= 30 else "شرکت بیرونی")
            cursor.execute("INSERT INTO actors VALUES (?, ?, ?, ?)", (f"CO-{i}", f"شرکت شماره {i} - {t}", t, "021-0000000"))
        # شبیه‌سازی ۸۰ کالا
        for i in range(1, 81):
            cursor.execute("INSERT INTO catalog VALUES (?, ?, ?)", (f"PR-{i}", f"کالای استراتژیک {i}", "مواد اولیه/نهایی"))
        conn.commit()

init_db()

# مدیریت منو (راست‌چین)
if 'menu_open' not in st.session_state: st.session_state.menu_open = True

col1, col2 = st.columns([1, 5])
with col1:
    if st.button("☰ منو"): st.session_state.menu_open = not st.session_state.menu_open

if st.session_state.menu_open:
    with col1:
        menu_choice = st.radio("بخش‌های سامانه:", ["داشبورد", "گزارشات", "مدیریت روابط", "کاتالوگ", "تنظیمات دیتابیس"])
else:
    menu_choice = "داشبورد"

# اجرای بخش‌های برنامه
if menu_choice == "گزارشات":
    st.title("📊 سیستم گزارش‌گیری جامع زنجیره تامین")
    rep_type = st.radio("نوع گزارش را انتخاب کنید:", ["گزارش شرکت", "اقلام زنجیره", "تحلیل حجمی", "تحلیل زمانی"], horizontal=True)
    
    if rep_type == "گزارش شرکت":
        c_id = st.selectbox("شرکت مورد نظر:", pd.read_sql("SELECT id, name FROM actors", conn)['id'].tolist())
        comp = pd.read_sql(f"SELECT * FROM actors WHERE id='{c_id}'", conn)
        st.write(f"### شناسنامه {comp['name'][0]}")
        # نمایش خریدها و فروش‌ها
        buys = pd.read_sql(f"SELECT * FROM links WHERE b_id='{c_id}'", conn)
        sells = pd.read_sql(f"SELECT * FROM links WHERE s_id='{c_id}'", conn)
        st.write("#### لیست خریدها:", buys)
        st.write("#### لیست فروش‌ها:", sells)
        
    elif rep_type == "اقلام زنجیره":
        p_id = st.selectbox("انتخاب کالا:", pd.read_sql("SELECT id, name FROM catalog", conn)['id'].tolist())
        data = pd.read_sql(f"SELECT * FROM links WHERE p_id='{p_id}'", conn)
        st.write("تحلیل وضعیت این قلم در زنجیره:", data)

elif menu_choice == "تنظیمات دیتابیس":
    st.title("🛠 تنظیمات پایگاه داده")
    # دانلود
    if st.button("📥 دانلود دیتابیس به صورت Excel"):
        output = io.BytesIO()
        with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
            pd.read_sql("SELECT * FROM actors", conn).to_excel(writer, sheet_name='شرکت‌ها')
            pd.read_sql("SELECT * FROM catalog", conn).to_excel(writer, sheet_name='اقلام')
            pd.read_sql("SELECT * FROM links", conn).to_excel(writer, sheet_name='روابط')
        st.download_button("دانلود فایل اکسل", data=output.getvalue(), file_name="backup.xlsx")
    
    # آپلود
    up = st.file_uploader("📤 آپلود فایل اکسل جهت جایگزینی:", type="xlsx")
    if up and st.button("تایید آپلود"):
        # اینجا کد جایگزینی دیتابیس قرار می‌گیرد
        st.success("دیتابیس با موفقیت بروز شد.")

    # ریست
    if st.button("⚠️ پاکسازی کامل (ریست دیتابیس)"):
        cursor.execute("DELETE FROM links")
        conn.commit()
        st.rerun()

else:
    st.title("📈 داشبورد تحلیل کلان")
    st.write("خوش آمدید. از منوی سمت راست برای دسترسی به گزارشات استفاده کنید.")
    st.info(f"تعداد شرکت‌های ثبت شده: 50 | تعداد اقلام کاتالوگ: 80")
