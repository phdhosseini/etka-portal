import streamlit as st
import pandas as pd
import sqlite3
import io

st.set_page_config(page_title="سامانه جامع اتکا", layout="wide")

# استایل CSS برای راست‌چین کردن کل رابط کاربری
st.markdown("""
    <style>
    * { font-family: 'Tahoma', sans-serif !important; direction: RTL !important; }
    .stApp { text-align: right !important; }
    th { text-align: right !important; background-color: #f0f2f6 !important; }
    </style>
""", unsafe_allow_html=True)

conn = sqlite3.connect("etka_core_v7_fixed.db", check_same_thread=False)
cursor = conn.cursor()

# ایجاد جداول و شبیه‌سازی داده‌های حجیم (۵۰ شرکت و ۸۰ کالا)
def setup_db():
    cursor.execute("CREATE TABLE IF NOT EXISTS actors (id TEXT PRIMARY KEY, name TEXT, type TEXT)")
    cursor.execute("CREATE TABLE IF NOT EXISTS catalog (id TEXT PRIMARY KEY, name TEXT)")
    cursor.execute("CREATE TABLE IF NOT EXISTS links (s_id TEXT, b_id TEXT, p_id TEXT, vol REAL, time_frame TEXT)")
    
    if pd.read_sql("SELECT count(*) FROM actors", conn).iloc[0,0] == 0:
        for i in range(1, 51):
            cursor.execute("INSERT INTO actors VALUES (?, ?, ?)", (f"C{i}", f"شرکت {i}", "هلدینگ/خدماتی" if i <= 30 else "بیرونی"))
        for i in range(1, 81):
            cursor.execute("INSERT INTO catalog VALUES (?, ?)", (f"P{i}", f"کالا {i}"))
        conn.commit()

setup_db()

# مدیریت منو از سمت راست
if 'show_menu' not in st.session_state: st.session_state.show_menu = True

col_menu, col_main = st.columns([1, 4]) if st.session_state.show_menu else (st.columns([1, 10])[0], None)

with col_menu:
    if st.button("☰ منو"): st.session_state.show_menu = not st.session_state.show_menu
    if st.session_state.show_menu:
        section = st.radio("بخش‌ها:", ["داشبورد", "گزارشات", "مدیریت روابط", "تنظیمات دیتابیس"])
    else:
        section = "داشبورد"

with (col_main if st.session_state.show_menu else st.container()):
    if section == "گزارشات":
        st.title("📊 سیستم گزارش‌گیری جامع")
        r1, r2, r3, r4 = st.columns(4)
        
        # ۱. گزارش شرکت
        with r1:
            if st.button("گزارش شرکت"): st.session_state.rep = "comp"
        # ۲. گزارش اقلام زنجیره
        with r2:
            if st.button("اقلام زنجیره"): st.session_state.rep = "items"
        # ۳. گزارش حجمی
        with r3:
            if st.button("گزارش حجمی"): st.session_state.rep = "vol"
        # ۴. گزارش زمانی
        with r4:
            if st.button("گزارش زمانی"): st.session_state.rep = "time"
            
        # نمایش منطق گزارش‌ها
        if 'rep' in st.session_state:
            if st.session_state.rep == "comp":
                c_id = st.selectbox("انتخاب شرکت:", pd.read_sql("SELECT id, name FROM actors", conn)['name'])
                st.write("اطلاعات هویتی و لیست خریدهای شرکت...")
            elif st.session_state.rep == "items":
                p_id = st.selectbox("انتخاب کالا:", pd.read_sql("SELECT name FROM catalog", conn)['name'])
                st.write("تحلیل فروشندگان و خریداران این کالا...")

    elif section == "تنظیمات دیتابیس":
        st.title("🛠 تنظیمات دیتابیس")
        if st.button("📥 دانلود فایل اکسل"):
            st.write("در حال آماده‌سازی فایل برای دانلود...")
        if st.button("🔄 آپلود داده جدید"):
            st.file_uploader("فایل اکسل خود را انتخاب کنید")
        if st.button("⚠️ ریست کامل"):
            cursor.execute("DELETE FROM links")
            conn.commit()

    else:
        st.title("داشبورد مدیریتی")
        st.write("مدیریت ۵۰ شرکت و ۸۰ قلم کالا فعال است.")
