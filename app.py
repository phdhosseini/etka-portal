import streamlit as st
import pandas as pd
import sqlite3
import plotly.express as px
from datetime import datetime
import io

# ۱. تنظیمات صفحه و تزریق استایل‌های راست‌چین مطلق و بومی‌سازی شده
st.set_page_config(page_title="سامانه مدیریت زنجیره تامین", layout="wide", initial_sidebar_state="expanded")

st.markdown("""
    <style>
    @import url('https://cdn.jsdelivr.net/gh/rastikerdar/vazir-font@v30.1.0/dist/font-face.css');
    
    html, body, [data-testid="stAppViewContainer"], .stMarkdown, p, h1, h2, h3, h4, h5, h6, label, span { 
        font-family: 'Vazir', 'Tahoma', sans-serif !important; 
        direction: RTL !important; 
        text-align: right !important; 
    }
    
    /* فورس کردن جداول به راست‌چین بودن مطلق و چینش ستون‌ها از راست به چپ */
    [data-testid="stDataFrame"] *, .stDataFrame *, [data-testid="stTable"] * {
        direction: RTL !important;
        text-align: right !important;
    }
    th { 
        text-align: right !important; 
        background-color: #1F4E78 !important; 
        color: white !important; 
    }
    td { text-align: right !important; direction: rtl !important; }

    /* استایل اختصاصی پاپ‌آپ وسط‌چین و عریض */
    .center-card {
        background-color: #ffffff;
        padding: 25px; border-radius: 12px; border: 2px solid #1F4E78;
        box-shadow: 0 4px 20px rgba(0,0,0,0.15); margin: 20px auto;
        max-width: 90%; text-align: right; direction: RTL;
    }
    
    /* استایل دکمه‌های منوی سفارشی بدون دایره‌های رادیویی حبابی زشت */
    .menu-btn {
        display: block; width: 100%; padding: 12px; margin-bottom: 8px;
        background-color: #f8f9fa; border-right: 5px solid #1F4E78;
        border-left: none; border-top: none; border-bottom: none;
        text-align: right; font-weight: bold; cursor: pointer;
    }
    .menu-btn:hover { background-color: #1F4E78; color: white; }
    </style>
    """, unsafe_allow_html=True)

# ۲. مدیریت پایگاه داده و کنترل وضعیت حافظه پورتال
DB_NAME = "etka_scf_platform_v8.db"
conn = sqlite3.connect(DB_NAME, check_same_thread=False)
cursor = conn.cursor()

for table_query in [
    "CREATE TABLE IF NOT EXISTS actors (national_id TEXT PRIMARY KEY, name TEXT, ownership_type TEXT, industry_1 TEXT, phone TEXT, description TEXT)",
    "CREATE TABLE IF NOT EXISTS catalog (product_code TEXT PRIMARY KEY, product_name TEXT, chain_position TEXT, unit TEXT, order_scale TEXT, eoq REAL, description TEXT)",
    "CREATE TABLE IF NOT EXISTS linkages (id INTEGER PRIMARY KEY AUTOINCREMENT, rel_id TEXT, supplier_id TEXT, buyer_id TEXT, product_code TEXT, fin_scale TEXT, time_frame TEXT, description TEXT)",
    "CREATE TABLE IF NOT EXISTS users (username TEXT PRIMARY KEY, password TEXT, role TEXT, company_name TEXT, user_phone TEXT, user_email TEXT, description TEXT)"
]:
    cursor.execute(table_query)
conn.commit()

# سیستم مدیریت بکاپ و بازگشت به عقب (Rollback) در وضعیت نشست
if 'db_history' not in st.session_state:
    st.session_state['db_history'] = []
if 'show_menu' not in st.session_state:
    st.session_state['show_menu'] = True
if 'current_section' not in st.session_state:
    st.session_state['current_section'] = "bi"

def save_rollback_point(label):
    tables = ['actors', 'catalog', 'linkages', 'users']
    backup = {}
    for t in tables:
        backup[t] = pd.read_sql_query(f"SELECT * FROM {t}", conn)
    st.session_state['db_history'].append({
        'time': datetime.now().strftime("%H:%M:%S"),
        'label': label,
        'data': backup
    })

# بارگذاری اولیه داده‌های پیش‌فرض در صورت خالی بودن دیتابیس
cursor.execute("SELECT COUNT(*) FROM actors")
if cursor.fetchone()[0] == 0:
    cursor.execute("INSERT INTO actors VALUES ('10101111101', 'شرکت صنایع غذایی اتکا', 'مالکیت مدیریتی اتکا', 'غذایی', '02128733', 'تولید فرآورده‌های روغنی هلدینگ')")
    cursor.execute("INSERT INTO actors VALUES ('10101111102', 'شرکت کشت و صنعت اسفراین', 'مالکیت مدیریتی اتکا', 'کشاورزی', '02128734', 'تامین نهاده‌های زراعی')")
    cursor.execute("INSERT INTO actors VALUES ('10202222205', 'شرکت توسعه کشت دانه های روغنی', 'مالکیت بیرونی', 'کشاورزی', '02188225', 'تامین دانه روغنی مرجع')")
    cursor.execute("INSERT INTO catalog VALUES ('MESC-101', 'روغن خام آفتابگردان فله', 'مواد اولیه (Raw Materials)', 'تن', 'تانکر ۲۵ تنی', 500.0, 'ماده پایه فرآوری روغن خوراکی')")
    cursor.execute("INSERT INTO linkages (rel_id, supplier_id, buyer_id, product_code, fin_scale, time_frame, description) VALUES ('REL-01', '10202222205', '10101111101', 'MESC-101', '۴. کلان (۵۰ تا ۱۰۰ میلیارد تومان)', '۳. میان‌مدت (۳۰ تا ۶۰ روز)', 'تامین دانه‌های فله ساختاری')")
    cursor.execute("INSERT INTO users VALUES ('admin', '123', 'admin', 'مدیریت ارشد کلان', '09120000000', 'admin@etka.ir', 'مدیریت ارشد سیستم')")
    conn.commit()

# ۳. پیاده‌سازی دکمه کلید مخفی‌کننده منوی سمت راست برای موبایل و دسکتاپ
col_menu_toggle, _ = st.columns([1, 10])
with col_menu_toggle:
    if st.button("☰ منو"):
        st.session_state['show_menu'] = not st.session_state['show_menu']

# چیدمان ستون‌ها بر اساس وضعیت منو
if st.session_state['show_menu']:
    col_main, col_nav = st.columns([4, 1])
    with col_nav:
        st.markdown("<h4 style='text-align:center; color:#1F4E78;'>🧭 منوی کاربری</h4>", unsafe_allow_html=True)
        if st.button("📊 داشبورد تحلیل کلان", use_container_width=True): st.session_state['current_section'] = "bi"
        if st.button("📊 گزارشات و پاوِت تیبل", use_container_width=True): st.session_state['current_section'] = "reports"
        if st.button("🔗 مدیریت روابط زنجیره", use_container_width=True): st.session_state['current_section'] = "links"
        if st.button("📦 کاتالوگ اقلام مرجع", use_container_width=True): st.session_state['current_section'] = "cat"
        if st.button("🏢 شناسنامه شرکت‌ها", use_container_width=True): st.session_state['current_section'] = "act"
        if st.button("👥 کاربران و دسترسی‌ها", use_container_width=True): st.session_state['current_section'] = "usr"
        if st.button("🛠️ تنظیمات دیتابیس (بکند)", use_container_width=True): st.session_state['current_section'] = "db"
else:
    col_main = st.container()

with col_main:
    df_links = pd.read_sql_query("SELECT * FROM linkages", conn)
    df_actors = pd.read_sql_query("SELECT * FROM actors", conn)
    df_cat = pd.read_sql_query("SELECT * FROM catalog", conn)
    actor_map = dict(zip(df_actors['national_id'], df_actors['name']))
    prod_map = dict(zip(df_cat['product_code'], df_cat['product_name']))

    # ----------------------------------------------------
    # ۱. داشبورد هوش تجاری (BI)
    # ----------------------------------------------------
    if st.session_state['current_section'] == "bi":
        st.title("📊 داشبورد تحلیل کلان و هوش تجاری")
        
        t1, t2, t3 = st.tabs(["📈 تحلیل ماتریس روابط و حجم مالی", "🏢 وضعیت هویتی شرکت‌ها", "⚠️ پایش پلتفرم"])
        
        with t1:
            cg1, cg2 = st.columns(2)
            with cg1:
                f1 = px.histogram(df_links, x="fin_scale", title="پراکنش حجم مالی روابط تجاری")
                f1.update_layout(font=dict(family="Vazir"), title_x=1)
                st.plotly_chart(f1, use_container_width=True)
            with cg2:
                f2 = px.bar(df_links, x="time_frame", title="ساختار چارچوب زمانی تسویه")
                f2.update_layout(font=dict(family="Vazir"), title_x=1)
                st.plotly_chart(f2, use_container_width=True)

        with t2:
            st.subheader("📋 لیست شرکت‌های احراز هویت شده")
            df_act_sub = df_actors[['name', 'ownership_type', 'industry_1', 'phone']].head(7).copy()
            df_act_sub.insert(0, 'ردیف', range(1, len(df_act_sub) + 1))
            df_act_sub.columns = ['ردیف', 'نام رسمی شرکت', 'نوع مالکیت سازمانی', 'صنعت اصلی', 'تلفن ثابت بازرگانی']
            st.dataframe(df_act_sub, use_container_width=True, hide_index=True)
            
            if st.button("🔍 مشاهده لیست کامل تمامی شرکت‌های احراز هویت شده"):
                df_act_all = df_actors[['name', 'ownership_type', 'industry_1', 'phone', 'description']].copy()
                df_act_all.insert(0, 'ردیف', range(1, len(df_act_all) + 1))
                df_act_all.columns = ['ردیف', 'نام رسمی شرکت', 'نوع مالکیت سازمانی', 'صنعت اصلی', 'تلفن ثابت بازرگانی', 'شرح ماموریت']
                st.dataframe(df_act_all, use_container_width=True, hide_index=True)

        with t3:
            st.info("اقدامات اصلاحی پایگاه داده فعال است. تمام جداول این بخش نیز راست‌چین هستند.")

    # ----------------------------------------------------
    # ۲. بخش جدید گزارشات پیشرفته (Pivot Table)
    # ----------------------------------------------------
    elif st.session_state['current_section'] == "reports":
        st.title("📊 سیستم گزارش‌گیری جامع و پاوِت تیبل")
        
        sel_actor = st.selectbox("انتخاب شرکت جهت بررسی زنجیره تامین تخصصی:", ["همه شرکت‌ها"] + list(actor_map.values()))
        
        df_rep = df_links.copy()
        df_rep['تأمین‌کننده'] = df_rep['supplier_id'].map(actor_map)
        df_rep['خریدار'] = df_rep['buyer_id'].map(actor_map)
        df_rep['نام محصول'] = df_rep['product_code'].map(prod_map)
        
        if sel_actor != "همه شرکت‌ها":
            df_rep = df_rep[(df_rep['تأمین‌کننده'] == sel_actor) | (df_rep['خریدار'] == sel_actor)]
            
        df_rep.insert(0, 'ردیف', range(1, len(df_rep) + 1))
        st.dataframe(df_rep[['ردیف', 'تأمین‌کننده', 'خریدار', 'نام محصول', 'fin_scale', 'time_frame']], use_container_width=True, hide_index=True)

    # ----------------------------------------------------
    # ۳. مدیریت روابط تجاری زنجیره (کاملاً راست‌چین و مینیاتوری)
    # ----------------------------------------------------
    elif st.session_state['current_section'] == "links":
        st.title("🔗 مدیریت روابط تجاری زنجیره تامین")
        
        with st.form("add_link"):
            supp = st.selectbox("تأمین‌کننده (فروشنده):", options=list(actor_map.keys()), format_func=lambda x: actor_map[x])
            buyer = st.selectbox("خریدار (مشتری):", options=list(actor_map.keys()), format_func=lambda x: actor_map[x])
            prod = st.selectbox("نام استاندارد محصول مرجع:", options=list(prod_map.keys()), format_func=lambda x: prod_map[x])
            f_scale = st.selectbox("حجم مالی معامله:", options=FIN_SCALES)
            t_frame = st.selectbox("چارچوب زمانی پرداخت:", options=TIME_FRAMES)
            desc = st.text_area("توضیحات:")
            if st.form_submit_button("ذخیره رابطه جدید"):
                save_rollback_point("قبل از افزودن رابطه")
                cursor.execute("INSERT INTO linkages (supplier_id, buyer_id, product_code, fin_scale, time_frame, description) VALUES (?,?,?,?,?,?)", (supp, buyer, prod, f_scale, t_frame, desc))
                conn.commit()
                st.rerun()

        st.write("---")
        if not df_links.empty:
            for idx, row in df_links.iterrows():
                c1, c2 = st.columns([5, 1])
                s_n = actor_map.get(row['supplier_id'], row['supplier_id'])
                b_n = actor_map.get(row['buyer_id'], row['buyer_id'])
                p_n = prod_map.get(row['product_code'], row['product_code'])
                
                c1.write(f"**{idx+1}. ردیف از راست:** تامین‌کننده: {s_n} | خریدار: {b_n} | محصول: {p_n}")
                with c2:
                    sc1, sc2 = st.columns(2)
                    if sc1.button("🔍", key=f"v_l_{row['id']}", help="مشاهده"):
                        st.markdown(f"""
                        <div class='center-card'>
                            <h4>🔍 شناسنامه معامله و شرح توصیفی</h4>
                            <p><b>حجم معامله مالی:</b> {row['fin_scale']}</p>
                            <p><b>دوره زمانی پرداخت:</b> {row['time_frame']}</p>
                            <p><b>توضیحات اختصاصی:</b> {row['description'] if row['description'] else 'بدون شرح.'}</p>
                        </div>
                        """, unsafe_allow_html=True)
                    if sc2.button("❌", key=f"d_l_{row['id']}", help="حذف"):
                        save_rollback_point("قبل از حذف رابطه")
                        cursor.execute(f"DELETE FROM linkages WHERE id={row['id']}")
                        conn.commit()
                        st.rerun()

    # ----------------------------------------------------
    # ۴. کاتالوگ استراتژیک اقلام مرجع
    # ----------------------------------------------------
    elif st.session_state['current_section'] == "cat":
        st.title("📦 کاتالوگ استراتژیک اقلام مرجع")
        if not df_cat.empty:
            for idx, row in df_cat.iterrows():
                c1, c2 = st.columns([5, 1])
                c1.write(f"**{idx+1}. ردیف:** نام کالا: {row['product_name']} | لایه زنجیره: {row['chain_position']} | واحد: {row['unit']}")
                with c2:
                    if st.button("🔍 ", key=f"v_c_{row['product_code']}"):
                        st.markdown(f"<div class='center-card'><h4>📦 مشخصات کالا</h4><p><b>توضیحات تکمیلی:</b> {row['description']}</p></div>", unsafe_allow_html=True)

    # ----------------------------------------------------
    # ۵. شناسنامه شرکت‌ها و زنجیره تامین اختصاصی آن‌ها
    # ----------------------------------------------------
    elif st.session_state['current_section'] == "act":
        st.title("🏢 شناسنامه هویت حقوقی شرکت‌ها")
        if not df_actors.empty:
            for idx, row in df_actors.iterrows():
                c1, c2 = st.columns([5, 1])
                c1.write(f"**{idx+1}. ردیف:** نام شرکت: {row['name']} | صنعت: {row['industry_1']} | تلفن: {row['phone']}")
                with c2:
                    if st.button("🔍 ", key=f"v_a_{row['national_id']}"):
                        # استخراج خودکار لیست اقلامی که این شرکت می‌فروشد یا می‌خرد
                        sells = df_links[df_links['supplier_id'] == row['national_id']]['product_code'].map(prod_map).tolist()
                        buys = df_links[df_links['buyer_id'] == row['national_id']]['product_code'].map(prod_map).tolist()
                        
                        st.markdown(f"""
                        <div class='center-card'>
                            <h4>🏢 شناسنامه هویت حقوقی و زنجیره اختصاصی شرکت</h4>
                            <p><b>نوع مالکیت:</b> {row['ownership_type']}</p>
                            <p><b>شرح توصیفی:</b> {row['description']}</p>
                            <hr>
                            <h5>📦 اقلامی که این شرکت تامین می‌کند (فروشنده):</h5>
                            <p>{', '.join(sells) if sells else 'هیچ کالایی تامین نمی‌کند.'}</p>
                            <h5>🛒 اقلامی که این شرکت خریداری می‌کند (مشتری):</h5>
                            <p>{', '.join(buys) if buys else 'هیچ کالایی خریداری نمی‌کند.'}</p>
                        </div>
                        """, unsafe_allow_html=True)

    # ----------------------------------------------------
    # ۶. مدیریت کاربران (تلفن و ایمیل)
    # ----------------------------------------------------
    elif st.session_state['current_section'] == "usr":
        st.title("👥 مدیریت کاربران و دسترسی‌ها")
        with st.form("add_usr"):
            u_name = st.text_input("نام کاربری:")
            u_pass = st.text_input("رمز عبور:")
            u_comp = st.text_input("نام شرکت:")
            u_phone = st.text_input("شماره تلفن رابط:")
            u_email = st.text_input("ایمیل صاحب حساب:")
            u_desc = st.text_area("توضیحات سمت:")
            if st.form_submit_button("ایجاد دسترسی"):
                cursor.execute("INSERT OR REPLACE INTO users VALUES (?,?,'user',?,?,?,?)", (u_name, u_pass, u_comp, u_phone, u_email, u_desc))
                conn.commit()
                st.rerun()

    # ----------------------------------------------------
    # ۷. تنظیمات پیشرفته پایگاه داده (بکند - فاقد هرگونه راهنمای نوشتاری)
    # ----------------------------------------------------
    elif st.session_state['current_section'] == "db":
        st.title("🛠️ تنظیمات پایگاه داده")
        
        # دکمه ۱: دانلود به صورت فایل اکسل چند شیته XLSX
        if st.button("📥 دانلود دیتابیس (فایل اکسل چند شیته XLSX)"):
            output = io.BytesIO()
            with pd.ExcelWriter(output, engine='openpyxl') as writer:
                df_actors.to_excel(writer, sheet_name='شناسنامه شرکت‌ها', index=False)
                df_cat.to_excel(writer, sheet_name='کاتالوگ محصولات', index=False)
                df_links.to_excel(writer, sheet_name='روابط تجاری', index=False)
                pd.read_sql_query("SELECT * FROM users", conn).to_excel(writer, sheet_name='کاربران', index=False)
            st.download_button(label="📥 دریافت مستقیم فایل Excel", data=output.getvalue(), file_name="ETKA_Database_Backup.xlsx", mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")
            
        # دکمه ۲: آپلود و جایگزینی فایل اکسل چند شیته
        uploaded_file = st.file_saver = st.file_input = st.file_uploader("📤 آپلود فایل اکسل جهت جایگزینی کامل پایگاه داده:", type=["xlsx"])
        if uploaded_file is not None:
            if st.button("🔄 تایید نهایی و بارگذاری داده‌های فایل اکسل"):
                save_rollback_point("قبل از آپلود اکسل جدید")
                excel_file = pd.ExcelFile(uploaded_file)
                if 'شناسنامه شرکت‌ها' in excel_file.sheet_names:
                    pd.read_excel(uploaded_file, sheet_name='شناسنامه شرکت‌ها').to_sql('actors', conn, if_exists='replace', index=False)
                if 'کاتالوگ محصولات' in excel_file.sheet_names:
                    pd.read_excel(uploaded_file, sheet_name='کاتالوگ محصولات').to_sql('catalog', conn, if_exists='replace', index=False)
                if 'روابط تجاری' in excel_file.sheet_names:
                    pd.read_excel(uploaded_file, sheet_name='روابط تجاری').to_sql('linkages', conn, if_exists='replace', index=False)
                st.success("پایگاه داده با موفقیت از روی فایل اکسل بازنویسی شد.")
                st.rerun()

        # دکمه ۳: پاکسازی و ریست کامل پایگاه داده
        if st.button("🗑️ پاک‌سازی و ریست کامل پایگاه داده"):
            save_rollback_point("قبل از ریست دیتابیس")
            cursor.execute("DROP TABLE IF EXISTS linkages")
            cursor.execute("DROP TABLE IF EXISTS actors")
            cursor.execute("DROP TABLE IF EXISTS catalog")
            cursor.execute("DROP TABLE IF EXISTS users")
            conn.commit()
            st.rerun()
            
        # دکمه ۴: سیستم هوشمند بازگشت به عقب (Rollback)
        if st.session_state['db_history']:
            st.write("---")
            st.write("🔄 نقاط بازگشت و پشتیبان‌های زمانی موجود:")
            for h_idx, history in enumerate(st.session_state['db_history']):
                if st.button(f"⏪ بازگشت به زمان {history['time']} ({history['label']})", key=f"roll_{h_idx}"):
                    for t_name, t_df in history['data'].items():
                        t_df.to_sql(t_name, conn, if_exists='replace', index=False)
                    conn.commit()
                    st.success("پایگاه داده با موفقیت به نقطه زمانی مورد نظر بازگشت.")
                    st.rerun()
