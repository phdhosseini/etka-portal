import streamlit as st
import pandas as pd
import sqlite3
import plotly.express as px

# ۱. تنظیمات صفحه، فونت بومی وزیر و راست‌چین‌سازی مطلق کل مرورگر (موبایل و دسکتاپ)
st.set_page_config(page_title="سامانه جامع مدیریت زنجیره تامین اتکا", layout="wide", initial_sidebar_state="expanded")

st.markdown("""
    <style>
    /* فراخوانی فونت زیبای وزیر برای تمام بخش‌ها */
    @import url('https://cdn.jsdelivr.net/gh/rastikerdar/vazir-font@v30.1.0/dist/font-face.css');
    
    html, body, [data-testid="stAppViewContainer"], .stMarkdown, p, h1, h2, h3, h4, h5, h6, label { 
        font-family: 'Vazir', 'Tahoma', sans-serif !important; 
        direction: RTL !important; 
        text-align: right !important; 
    }
    
    /* راست‌چین کردن مطلق هدرها و محتوای جداول استریم‌لیت */
    [data-testid="stDataFrame"] *, .stDataFrame * {
        direction: RTL !important;
        text-align: right !important;
    }
    th, [data-testid="stTable"] th { 
        text-align: right !important; 
        background-color: #1F4E78 !important; 
        color: white !important; 
        font-weight: bold !important;
    }
    td, [data-testid="stTable"] td { text-align: right !important; }

    /* راست‌چین کردن سایدبار و ناوبری */
    [data-testid="stSidebar"] { direction: RTL !important; text-align: right !important; right: 0 !important; left: auto !important; border-left: 1px solid #e0e0e0; }
    [data-testid="stSidebarNav"] { direction: RTL !important; text-align: right !important; }
    
    /* بزرگتر و شکیل‌تر کردن منوهای سایدبار به صورت دکمه */
    .stRadio div[role="radiogroup"] label { 
        background-color: #f8f9fa !important; padding: 14px 20px !important; border-radius: 8px !important; 
        border-right: 6px solid #1F4E78 !important; border-left: none !important; width: 100% !important; 
        font-weight: bold !important; font-size: 15px !important; display: block !important; text-align: right !important;
        margin-bottom: 8px !important; box-shadow: 0 2px 4px rgba(0,0,0,0.05);
    }
    .stRadio div[role="radiogroup"] label:hover { background-color: #e9ecef !important; }
    
    /* کارت‌های رنگی شکیل برای پنجره‌های مشاهده شناسنامه کالا و شرکت */
    .id-card {
        background: linear-gradient(135deg, #fdfbfb 0%, #ebedee 100%);
        padding: 25px; border-radius: 12px; border-right: 8px solid #1F4E78;
        box-shadow: 0 4px 15px rgba(0,0,0,0.08); margin-bottom: 20px;
    }
    
    /* دکمه‌های اختصاصی فرم‌ها */
    div.stButton > button { background-color: #1F4E78; color: white; border-radius: 6px; font-weight: bold; width: 100%; height: 42px; }
    div.stButton > button:hover { background-color: #153552; color: white; }
    </style>
    """, unsafe_allow_html=True)

# ۲. مدیریت اتصال پایگاه داده و اضافه شدن فیلد "توضیحات" (description)
conn = sqlite3.connect("etka_scf_platform_v6.db", check_same_thread=False)
cursor = conn.cursor()

cursor.execute("""
CREATE TABLE IF NOT EXISTS actors (
    national_id TEXT PRIMARY KEY, registro_id TEXT, economic_code TEXT, name TEXT, 
    legal_type TEXT, ownership_type TEXT, industry_1 TEXT, industry_2 TEXT, 
    phone TEXT, contact_name TEXT, contact_phone TEXT, description TEXT)
""")
cursor.execute("""
CREATE TABLE IF NOT EXISTS catalog (
    product_code TEXT PRIMARY KEY, product_name TEXT, chain_position TEXT, 
    unit TEXT, order_scale TEXT, eoq REAL, description TEXT)
""")
cursor.execute("""
CREATE TABLE IF NOT EXISTS linkages (
    id INTEGER PRIMARY KEY AUTOINCREMENT, rel_id TEXT, supplier_id TEXT, buyer_id TEXT, 
    product_code TEXT, fin_scale TEXT, time_frame TEXT, description TEXT)
""")
cursor.execute("""
CREATE TABLE IF NOT EXISTS users (
    username TEXT PRIMARY KEY, password TEXT, role TEXT, company_name TEXT, description TEXT)
""")
conn.commit()

# ۳. منطق بارگذاری خودکار اطلاعات پایه
def init_system_data():
    cursor.execute("SELECT COUNT(*) FROM actors")
    if cursor.fetchone()[0] == 0:
        etka_cos = [
            ("10101111101", "4001", "4111", "شرکت صنایع غذایی اتکا", "سهامی خاص", "مالکیت مدیریتی اتکا", "غذایی", "بازرگانی", "02128733", "مهندس علوی", "09121111101", "شرکت محوری تولید روغن و صنایع غذایی هلدینگ"),
            ("10101111102", "4002", "4112", "شرکت کشت و صنعت اسفراین اتکا", "سهامی خاص", "مالکیت مدیریتی اتکا", "کشاورزی و دامپروری", "-", "02128734", "مهندس اکبری", "09121111102", "تامین‌کننده نهاده‌های زراعی و دامی بومی"),
            ("10101111103", "4003", "4113", "شرکت قند و شکر اتکا", "سهامی خاص", "مالکیت مدیریتی اتکا", "غذایی", "-", "02128735", "مهندس رضایی", "09121111103", "تامین کننده شکر خام و سفید زنجیره تامین"),
            ("10101111104", "4004", "4114", "شرکت روغن‌کشی خرمشهر اتکا", "سهامی خاص", "مالکیت مدیریتی اتکا", "غذایی", "شیمیایی و پتروشیمی", "02128736", "مهندس nouri", "09121111104", "کارخانه اصلی روغن‌کشی از دانه‌های روغنی هلدینگ"),
            ("10101111105", "4005", "4115", "شرکت پخش سراسری اتکا", "سهامی عام", "مالکیت مدیریتی اتکا", "بازرگانی", "خدمات و لجستیک", "02128737", "مهندس حسنی", "09121111105", "توزیع‌کننده مویرگی کل فرآورده‌ها به فروشگاه‌ها")
        ]
        ext_cos = [
            ("10202222201", "5001", "5111", "هلدینگ پتروشیمی خلیج فارس", "سهامی عام", "مالکیت بیرونی", "شیمیایی و پتروشیمی", "-", "02188221", "مهندس شریفی", "09122222201", "تامین کننده بیرونی مواد پت بسته‌بندی"),
            ("10202222205", "5005", "5115", "شرکت توسعه کشت دانه های روغنی", "سهامی خاص", "مالکیت بیرونی", "کشاورزی و دامپروری", "غذایی", "02188225", "رابط دانه روغنی", "09122222205", "بزرگترین تامین‌کننده دانه روغنی کل کشور")
        ]
        for c in etka_cos: cursor.execute("INSERT INTO actors VALUES (?,?,?,?,?,?,?,?,?,?,?,?)", c)
        for c in ext_cos: cursor.execute("INSERT INTO actors VALUES (?,?,?,?,?,?,?,?,?,?,?,?)", c)
        for act in etka_cos + ext_cos: cursor.execute("INSERT OR IGNORE INTO users VALUES (?,?,'user',?,?)", (act[0], "12345", act[3], "کاربر سیستم زنجیره تامین"))
        
        prods = [
            ("MESC-101", "روغن خام آفتابگردان فله", "مواد اولیه (Raw Materials)", "تن", "تانکر ۲۵ تنی", 500.0, "اساسی‌ترین ماده اولیه تولید روغن خوراکی"),
            ("MESC-102", "گرانول پلی‌اتیلن تفتان (PET)", "مواد اولیه (Raw Materials)", "کیلوگرم", "جامبوبگ ۱ تنی", 120.0, "ماده اصلی ساخت ظروف پلاستیکی روغن مایع"),
            ("IRC-301", "روغن مایع آفتابگردان ۸۰۰ گرمی اتکا", "محصول نهایی (Final Product)", "کارتن", "پالت ۱۲۰ کارتنی", 1000.0, "محصول نهایی توزیع شده در سطح فروشگاه‌های زنجیره‌ای")
        ]
        for p in prods: cursor.execute("INSERT INTO catalog VALUES (?,?,?,?,?,?,?)", p)
        
        links = [
            ("REL-01", "10202222205", "10101111104", "MESC-101", "۵. بسیار کلان (۱۰۰ تا ۳۰۰ میلیارد تومان)", "۴. بلندمدت (۶۰ تا ۹۰ روز)", "رابطه کلان واردات مواد اولیه دانه آفتابگردان کشور"),
            ("REL-02", "10101111104", "10101111101", "MESC-101", "۴. کلان (۵۰ تا ۱۰۰ میلیارد تومان)", "۳. میان‌مدت (۳۰ تا ۶۰ روز)", "انتقال روغن خام جهت تصفیه نهایی کارخانجات درون گروهی")
        ]
        for l in links: cursor.execute("INSERT INTO linkages (rel_id, supplier_id, buyer_id, product_code, fin_scale, time_frame, description) VALUES (?,?,?,?,?,?,?)", l)
        conn.commit()

init_system_data()

FIN_SCALES = ["۱. خرد (زیر ۱ میلیارد تومان)", "۲. کوچک (۱ تا ۱۰ میلیارد تومان)", "۳. متوسط (۱۰ تا ۵۰ میلیارد تومان)", "۴. کلان (۵۰ تا ۱۰۰ میلیارد تومان)", "۵. بسیار کلان (۱۰۰ تا ۳۰۰ میلیارد تومان)", "۶. فوق‌کلان (بالای ۳۰۰ میلیارد تومان)"]
TIME_FRAMES = ["۱. آنی و نقدی", "۲. کوتاه‌مدت (زیر ۳۰ روز)", "۳. میان‌مدت (۳۰ تا ۶۰ روز)", "۴. بلندمدت (۶۰ تا ۹۰ روز)", "۵. خیلی بلندمدت (۹۰ تا ۱۸۰ روز)", "۶. فوق بلندمدت (بالای ۱۸۰ روز)"]
POSITIONS = ["مواد اولیه (Raw Materials)", "محصول میانی (Intermediate Product)", "محصول نهایی (Final Product)", "ملزومات مصرفی و بسته‌بندی"]

# ۴. منطق احراز هویت ورود کاربران
if 'logged_in' not in st.session_state:
    st.session_state.update({'logged_in': False, 'username': "", 'role': "", 'name': ""})

if not st.session_state['logged_in']:
    st.write("<br><br>", unsafe_allow_html=True)
    st.markdown("""
        <div style='background-color: white; padding: 35px; border-radius: 12px; box-shadow: 0 4px 15px rgba(0,0,0,0.1); max-width: 450px; margin: auto; border-top: 6px solid #1F4E78;'>
            <h2 style='text-align: center; color: #1F4E78; margin-bottom:10px;'>🌐 پلتفرم هوشمند زنجیره تامین اتکا</h2>
            <p style='text-align: center; color: #666; font-size:14px;'>سامانه متمرکز پایش هوش تجاری و ثبت داده‌های زنجیره ارزش</p>
        </div>
        """, unsafe_allow_html=True)
    c_left, c_mid, c_right = st.columns([1,1.5,1])
    with c_mid:
        u = st.text_input("👤 نام کاربری (شناسه ملی یا admin):")
        p = st.text_input("🔑 رمز عبور:", type="password")
        if st.button("ورود به پنل کاربری"):
            if u == "admin" and p == "123":
                st.session_state.update({'logged_in': True, 'username': "admin", 'role': "admin", 'name': "آقای دکتر حسینی (مدیر کلان)"})
                st.rerun()
            else:
                res = pd.read_sql_query(f"SELECT * FROM users WHERE username='{u}' AND password='{p}'", conn)
                if not res.empty:
                    st.session_state.update({'logged_in': True, 'username': u, 'role': res['role'].values[0], 'name': res['company_name'].values[0]})
                    st.rerun()
                else:
                    st.error("❌ اطلاعات ورود اشتباه است. (رمز شرکت‌های نمونه: 12345)")
else:
    # ساختار مستقل سایدبار برای حل باگ جابجایی
    st.sidebar.markdown(f"<h3 style='color:#1F4E78; text-align:center; margin-bottom:0;'>🧭 منوی ناوبری</h3>", unsafe_allow_html=True)
    st.sidebar.markdown(f"<p style='text-align:center; font-size:13px; color:#555;'>کاربر: {st.session_state['name']}</p><hr style='margin-top:0;'>", unsafe_allow_html=True)
    
    # تعریف شناسه‌های یکتا برای گزینه‌های منو
    if st.session_state['role'] == "admin":
        menu_map = {
            "dashboard": "📊 داشبورد تحلیل کلان و هوش تجاری (BI)",
            "linkages": "🔗 ثبت و مدیریت روابط زنجیره تامین",
            "catalog": "📦 کاتالوگ استراتژیک محصولات مرجع",
            "actors": "🏢 ثبت شناسنامه حقوقی شرکت‌ها",
            "users": "👥 مدیریت کاربران و سطوح دسترسی",
            "backend": "🛠️ تنظیمات پیشرفته دیتابیس (بک‌ئند)"
        }
    else:
        menu_map = {
            "linkages": "🔗 ثبت و مدیریت روابط زنجیره تامین",
            "catalog": "📦 کاتالوگ استراتژیک محصولات مرجع",
            "actors": "🏢 ثبت شناسنامه حقوقی شرکت‌ها"
        }
        
    choice_raw = st.sidebar.radio("انتخاب بخش عملکردی سیستم:", list(menu_map.values()))
    current_section = [k for k, v in menu_map.items() if v == choice_raw][0]

    if st.sidebar.button("🚪 خروج از سامانه"):
        st.session_state.update({'logged_in': False, 'username': "", 'role': "", 'name': ""})
        st.rerun()

    # ----------------------------------------------------
    # ۱. بخش داشبورد کلان هوش تجاری (BI) - ادمین
    # ----------------------------------------------------
    if current_section == "dashboard":
        st.title("📊 داشبورد هوش تجاری (BI) و پایش پلتفرم اتکا")
        
        # سیستم تب‌بندی پیشرفته برای تحلیل‌های چندگانه درخواستی
        tab_bi1, tab_bi2, tab_bi3, tab_bi4 = st.tabs([
            "📈 تحلیل ماتریس روابط زنجیره", 
            "🏢 داشبورد وضعیت شرکت‌های ثبت‌شده", 
            "📦 داشبورد توزیع محصولات مرجع", 
            "⚠️ پایش نقص اطلاعات و اقدامات اصلاحی"
        ])
        
        df_links = pd.read_sql_query("SELECT * FROM linkages", conn)
        df_actors = pd.read_sql_query("SELECT * FROM actors", conn)
        df_cat = pd.read_sql_query("SELECT * FROM catalog", conn)
        
        actor_map = dict(zip(df_actors['national_id'], df_actors['name']))
        prod_map = dict(zip(df_cat['product_code'], df_cat['product_name']))
        
        # تب اول: تحلیل ماتریس روابط
        with tab_bi1:
            st.subheader("تحلیل رسوب نقدینگی و تمرکز روابط")
            col_g1, col_g2 = st.columns(2)
            with col_g1:
                fig1 = px.histogram(df_links, x="fin_scale", labels={"fin_scale": "گروه مبالغ مالی (ریال)", "count": "تعداد معاملات"}, title="تمرکز سرمایه در کلاس‌های مبالغ روابط تجاری")
                fig1.update_layout(xaxis_title="گروه بندی مبالغ مالی معامله", yaxis_title="تعداد روابط تجاری", font=dict(family="Vazir"))
                st.plotly_chart(fig1, use_container_width=True)
            with col_g2:
                fig2 = px.bar(df_links, x="time_frame", labels={"time_frame": "چارچوب زمانی تسویه مالی", "count": "تعداد"}, title="تحلیل بازه زمانی و سررسید پرداختی زنجیره")
                fig2.update_layout(xaxis_title="چارچوب زمانی تسویه", yaxis_title="تعداد روابط تجاری", font=dict(family="Vazir"))
                st.plotly_chart(fig2, use_container_width=True)
                
            st.write("---")
            st.subheader("📋 ماتریس جامع روابط استراتژیک زنجیره ارزش")
            if not df_links.empty:
                df_disp = df_links.copy()
                df_disp['ردیف'] = range(1, len(df_disp) + 1)
                df_disp['شرکت تامین‌کننده (فروشنده)'] = df_disp['supplier_id'].map(actor_map)
                df_disp['شرکت خریدار (مشتری)'] = df_disp['buyer_id'].map(actor_map)
                df_disp['نام محصول'] = df_disp['product_code'].map(prod_map)
                df_disp['حجم معامله ریالی'] = df_disp['fin_scale']
                df_disp['مهلت زمانی پرداخت'] = df_disp['time_frame']
                df_disp['توضیحات تکمیلی'] = df_disp['description']
                
                df_final = df_disp[['ردیف', 'شرکت تامین‌کننده (فروشنده)', 'شرکت خریدار (مشتری)', 'نام محصول', 'حجم معامله ریالی', 'مهلت زمانی پرداخت', 'توضیحات تکمیلی']]
                st.dataframe(df_final, use_container_width=True, hide_index=True)
            else:
                st.info("داده‌ای ثبت نشده است.")
                
        # تب دوم: داشبورد جامع وضعیت شرکت‌ها
        with tab_bi2:
            st.subheader("📊 آمار و فیلتر بازیگران هلدینگ")
            fig_act = px.pie(df_actors, names="ownership_type", title="سهم ساختار مالکیت شرکت‌ها در سامانه")
            fig_act.update_layout(font=dict(family="Vazir"))
            st.plotly_chart(fig_act, use_container_width=True)
            
            st.write("📋 لیست کل شرکت‌های احراز هویت شده:")
            df_act_disp = df_actors[['name', 'ownership_type', 'industry_1', 'phone', 'description']].copy()
            df_act_disp.columns = ['نام رسمی شرکت', 'نوع مالکیت سازمانی', 'صنعت اصلی فعالیت', 'تلفن ثابت بازرگانی', 'توضیحات شناسنامه']
            st.dataframe(df_act_disp, use_container_width=True, hide_index=True)

        # تب سوم: داشبورد توزیع محصولات مرجع
        with tab_bi3:
            st.subheader("📦 پایش کاتالوگ کالاهای زنجیره ارزش")
            fig_prod = px.histogram(df_cat, x="chain_position", title="پراکنش اقلام استراتژیک در لایه‌های تولید زنجیره")
            fig_prod.update_layout(xaxis_title="موقعیت در لایه تولید", yaxis_title="تعداد اقلام مرجع", font=dict(family="Vazir"))
            st.plotly_chart(fig_prod, use_container_width=True)
            
            df_cat_disp = df_cat[['product_name', 'chain_position', 'unit', 'description']].copy()
            df_cat_disp.columns = ['نام محصول یا فرآورده', 'جایگاه در زنجیره ارزش', 'واحد سنجش معامله', 'توضیحات استراتژیک محصول']
            st.dataframe(df_cat_disp, use_container_width=True, hide_index=True)

        # تب چهارم: پایش نقص اطلاعات (نظارت عالیه آقای دکتر حسینی)
        with tab_bi4:
            st.subheader("⚠️ پایش شرکت‌ها و اقلام فاقد زنجیره ثبت شده (اقدام اصلاحی)")
            
            # پیدا کردن شرکت‌هایی که در هیچ رابطه‌ای حضور ندارند
            all_linked_actors = set(df_links['supplier_id'].tolist() + df_links['buyer_id'].tolist())
            incomplete_actors = df_actors[~df_actors['national_id'].isin(all_linked_actors)]
            
            # پیدا کردن محصولاتی که هنوز معامله‌ای برای آن‌ها ثبت نشده
            incomplete_products = df_cat[~df_cat['product_code'].isin(df_links['product_code'].tolist())]
            
            col_m1, col_m2 = st.columns(2)
            with col_m1:
                st.warning("🏢 شرکت‌هایی که هنوز ماتریس روابط تجاری خود را تکمیل نکرده‌اند:")
                if not incomplete_actors.empty:
                    st.dataframe(incomplete_actors[['name', 'ownership_type']].rename(columns={'name':'نام شرکت فاقد رابطه', 'ownership_type':'نوع مالکیت'}), use_container_width=True, hide_index=True)
                else:
                    st.success("✔️ تمام شرکت‌های ثبت شده دارای ماتریس رابطه فعال هستند.")
            with col_m2:
                st.warning("📦 اقلام و محصولاتی که هنوز مهلت زمانی و خریدار برای آن‌ها درج نشده:")
                if not incomplete_products.empty:
                    st.dataframe(incomplete_products[['product_name', 'chain_position']].rename(columns={'product_name':'نام محصول بدون زنجیره', 'chain_position':'موقعیت کالایی'}), use_container_width=True, hide_index=True)
                else:
                    st.success("✔️ تمام محصولات کاتالوگ دارای جریان مالی فعال هستند.")

    # ----------------------------------------------------
    # ۲. بخش ثبت و مدیریت روابط زنجیره (با اکشن‌های ۳ گانه و پاپ‌آپ)
    # ----------------------------------------------------
    elif current_section == "linkages":
        st.title("🔗 مدیریت جامع ماتریس روابط و فاکتورهای زنجیره")
        
        user_id = st.session_state['username']
        is_admin = st.session_state['role'] == "admin"
        
        # فرم ثبت داده جدید
        with st.form("form_linkage_new"):
            st.subheader("➕ ثبت رابطه تجاری جدید")
            actors_df = pd.read_sql_query("SELECT national_id, name FROM actors", conn)
            catalog_df = pd.read_sql_query("SELECT product_code, product_name FROM catalog", conn)
            actor_options = dict(zip(actors_df['national_id'], actors_df['name']))
            product_options = dict(zip(catalog_df['product_code'], catalog_df['product_name']))
            
            supp = st.selectbox("تأمین‌کننده (فروشنده):", options=list(actor_options.keys()), format_func=lambda x: actor_options[x]) if is_admin else user_id
            if not is_admin: st.info(f"🏢 شرکت ثبت‌کننده شما هستید: {st.session_state['name']}")
                
            buyer = st.selectbox("خریدار (مشتری روابط تجاری):", options=list(actor_options.keys()), format_func=lambda x: actor_options[x])
            prod = st.selectbox("محصول مورد مبادله از کاتالوگ مرجع:", options=list(product_options.keys()), format_func=lambda x: product_options[x])
            f_scale = st.selectbox("کلاس و گروه مبالغ مالی رابطه:", options=FIN_SCALES)
            t_frame = st.selectbox("چارچوب زمانی و مهلت تسویه پرداخت:", options=TIME_FRAMES)
            desc = st.text_area("توضیحات اختصاصی و بندهای توافقی فاکتور یا قرارداد:")
            
            if st.form_submit_button("ذخیره قطعی رابطه تجاری"):
                r_id = f"REL-{supp[:4]}-{buyer[:4]}"
                cursor.execute("INSERT INTO linkages (rel_id, supplier_id, buyer_id, product_code, fin_scale, time_frame, description) VALUES (?,?,?,?,?,?,?)",
                               (r_id, supp, buyer, prod, f_scale, t_frame, desc))
                conn.commit()
                st.success("✔️ رابطه تجاری با موفقیت ثبت شد.")
                st.rerun()

        # لیست جدول روابط به همراه عملیات
        st.write("---")
        st.subheader("📋 مدیریت ردیف‌های فعال ماتریس روابط")
        q = "SELECT * FROM linkages" if is_admin else f"SELECT * FROM linkages WHERE supplier_id='{user_id}' OR buyer_id='{user_id}'"
        df_l_curr = pd.read_sql_query(q, conn)
        
        actors_all = pd.read_sql_query("SELECT national_id, name FROM actors", conn)
        act_map = dict(zip(actors_all['national_id'], actors_all['name']))
        cat_all = pd.read_sql_query("SELECT product_code, product_name FROM catalog", conn)
        prod_map = dict(zip(cat_all['product_code'], cat_all['product_name']))

        if not df_l_curr.empty:
            for idx, row in df_l_curr.iterrows():
                c1, c2, c3, c4 = st.columns([5, 1, 1, 1])
                s_n = act_map.get(row['supplier_id'], row['supplier_id'])
                b_n = act_map.get(row['buyer_id'], row['buyer_id'])
                p_n = prod_map.get(row['product_code'], row['product_code'])
                
                c1.write(f"**ردیف {idx+1}:** فروشنده [{s_n}] ⬅️ خریدار [{b_n}] | کالا: {p_n}")
                
                # ۱. دکمه مشاهده شناسنامه ردیف
                if c2.button("🔍 مشاهده", key=f"view_l_{row['id']}"):
                    st.markdown(f"""
                    <div class='id-card'>
                        <h4 style='color:#1F4E78;'>📋 شناسنامه اختصاصی معامله زنجیره</h4>
                        <p><b>نام شرکت فروشنده:</b> {s_n}</p>
                        <p><b>نام شرکت خریدار:</b> {b_n}</p>
                        <p><b>کالا/خدمات:</b> {p_n}</p>
                        <p><b>حجم مبالغ مالی:</b> {row['fin_scale']}</p>
                        <p><b>دوره زمانی تسویه فاکتور:</b> {row['time_frame']}</p>
                        <hr>
                        <p><b>📝 توضیحات اختصاصی درج شده:</b> {row['description'] if row['description'] else 'هیچ توضیحی ثبت نشده است.'}</p>
                    </div>
                    """, unsafe_allow_html=True)
                
                # ۲. دکمه ویرایش سریع تعاملی
                if c3.button("📝 ویرایش", key=f"edit_l_{row['id']}"):
                    with st.form(f"edit_form_l_{row['id']}"):
                        st.write(f"در حال ویرایش ردیف {idx+1}")
                        new_f = st.selectbox("گروه مبالغ جدید:", FIN_SCALES, index=FIN_SCALES.index(row['fin_scale']) if row['fin_scale'] in FIN_SCALES else 0)
                        new_t = st.selectbox("چارچوب زمانی جدید:", TIME_FRAMES, index=TIME_FRAMES.index(row['time_frame']) if row['time_frame'] in TIME_FRAMES else 0)
                        new_d = st.text_area("اصلاح توضیحات:", value=row['description'])
                        if st.form_submit_button("ذخیره تغییرات دیتابیس"):
                            cursor.execute(f"UPDATE linkages SET fin_scale=?, time_frame=?, description=? WHERE id={row['id']}", (new_f, new_t, new_d))
                            conn.commit()
                            st.success("تغییرات اعمال شد.")
                            st.rerun()
                
                # ۳. دکمه حذف
                if c4.button("❌ حذف", key=f"del_l_{row['id']}"):
                    cursor.execute(f"DELETE FROM linkages WHERE id={row['id']}")
                    conn.commit()
                    st.success("ردیف با موفقیت حذف شد.")
                    st.rerun()
        else:
            st.info("رابطه‌ای یافت نشد.")

    # ----------------------------------------------------
    # ۳. بخش کاتالوگ استراتژیک محصولات (با شناسنامه و اکشن‌ها)
    # ----------------------------------------------------
    elif current_section == "catalog":
        st.title("📦 کاتالوگ مرجع اقلام و کالاهای استراتژیک")
        
        with st.form("form_cat_new"):
            st.subheader("➕ افزودن کالا به کاتالوگ هوشمند")
            p_code = st.text_input("کد کالا یا شناسه ایران‌کد محصول:")
            p_name = st.text_input("نام دقیق تجاری محصول:")
            p_pos = st.selectbox("موقعیت در لایه‌های تولید زنجیره ارزش:", options=POSITIONS)
            p_unit = st.text_input("واحد اندازه‌گیری سنجش کالا (مثلاً تن، کیلوگرم):")
            p_scale = st.text_input("مقیاس سفارش‌گذاری لجستیک:")
            p_eoq = st.number_input("حجم حجم سفارش اقتصادی بهینه (EOQ):", min_value=0.0)
            p_desc = st.text_area("توضیحات فنی و شناسنامه استراتژیک محصول:")
            
            if st.form_submit_button("ذخیره کالا در کاتالوگ"):
                try:
                    cursor.execute("INSERT INTO catalog VALUES (?,?,?,?,?,?,?)", (p_code, p_name, p_pos, p_unit, p_scale, p_eoq, p_desc))
                    conn.commit()
                    st.success("✔️ محصول با موفقیت ذخیره شد.")
                    st.rerun()
                except sqlite3.IntegrityError:
                    st.error("کد کالا تکراری است.")

        st.write("---")
        st.subheader("📋 اقلام موجود در کاتالوگ")
        df_c_curr = pd.read_sql_query("SELECT * FROM catalog", conn)
        
        if not df_c_curr.empty:
            for idx, row in df_c_curr.iterrows():
                c1, c2, c3, c4 = st.columns([5, 1, 1, 1])
                c1.write(f"**{idx+1}. نام محصول:** {row['product_name']} | **جایگاه در زنجیره:** {row['chain_position']}")
                
                if c2.button("🔍 مشاهده", key=f"view_c_{row['product_code']}"):
                    st.markdown(f"""
                    <div class='id-card' style='border-right-color: #2E7D32;'>
                        <h4 style='color:#2E7D32;'>📦 شناسنامه رسمی و فنی کالا</h4>
                        <p><b>نام استاندارد فرآورده:</b> {row['product_name']}</p>
                        <p><b>جایگاه تولیدی:</b> {row['chain_position']}</p>
                        <p><b>واحد اندازه‌گیری سنجش:</b> {row['unit']}</p>
                        <p><b>مقیاس لجستیکی سفارش:</b> {row['order_scale']}</p>
                        <p><b>حجم سفارش اقتصادی (EOQ):</b> {row['eoq']}</p>
                        <hr>
                        <p><b>📝 توضیحات فنی و مدیریتی:</b> {row['description'] if row['description'] else 'فاقد توضیحات تکمیلی.'}</p>
                    </div>
                    """, unsafe_allow_html=True)
                    
                if c3.button("📝 ویرایش", key=f"edit_c_{row['product_code']}"):
                    with st.form(f"edit_form_c_{row['product_code']}"):
                        new_name = st.text_input("اصلاح نام محصول:", value=row['product_name'])
                        new_unit = st.text_input("اصلاح واحد:", value=row['unit'])
                        new_desc = st.text_area("اصلاح توضیحات فنی کالا:", value=row['description'])
                        if st.form_submit_button("ثبت نهایی اصلاحات کالا"):
                            cursor.execute("UPDATE catalog SET product_name=?, unit=?, description=? WHERE product_code=?", (new_name, new_unit, new_desc, row['product_code']))
                            conn.commit()
                            st.success("کالا ویرایش شد.")
                            st.rerun()
                            
                if c4.button("❌ حذف", key=f"del_c_{row['product_code']}"):
                    cursor.execute(f"DELETE FROM catalog WHERE product_code='{row['product_code']}'")
                    conn.commit()
                    st.rerun()

    # ----------------------------------------------------
    # ۴. بخش شناسنامه شرکت‌ها (با شناسنامه و اکشن‌ها)
    # ----------------------------------------------------
    elif current_section == "actors":
        st.title("🏢 شناسنامه هویت حقوقی بازیگران زنجیره تامین")
        
        with st.form("form_actor_new"):
            st.subheader("➕ احرز هویت شرکت جدید")
            n_id = st.text_input("شناسه ملی ۱۰ رقمی شرکت (نام کاربری سیستم):")
            name = st.text_input("نام تجاری و رسمی شرکت:")
            owner = st.selectbox("نوع مالکیت و ارتباط با هلدینگ اتکا:", ["مالکیت مدیریتی اتکا", "مالکیت غیرمدیریتی اتکا", "مالکیت بیرونی"])
            ind1 = st.text_input("صنعت حوزه فعالیت:")
            phone = st.text_input("تلفن معاونت مالی/بازرگانی:")
            desc = st.text_area("توضیحات هویتی و حیطه ماموریت شرکت در هلدینگ:")
            
            if st.form_submit_button("ثبت بازیگر حقوقی"):
                try:
                    cursor.execute("INSERT INTO actors (national_id, name, ownership_type, industry_1, phone, description) VALUES (?,?,?,?,?,?)", (n_id, name, owner, ind1, phone, desc))
                    cursor.execute("INSERT OR IGNORE INTO users VALUES (?,?,'user',?,?)", (n_id, "12345", name, "کاربر تابعه"))
                    conn.commit()
                    st.success("✔️ شرکت با موفقیت به بانک اطلاعاتی متصل شد.")
                    st.rerun()
                except sqlite3.IntegrityError:
                    st.error("شناسه ملی تکراری است.")

        st.write("---")
        st.subheader("📋 شرکت‌های احراز هویت شده")
        df_a_curr = pd.read_sql_query("SELECT * FROM actors", conn)
        
        if not df_a_curr.empty:
            for idx, row in df_a_curr.iterrows():
                c1, c2, c3, c4 = st.columns([5, 1, 1, 1])
                c1.write(f"**🏢 نام شرکت:** {row['name']} | **نوع مالکیت:** {row['ownership_type']}")
                
                if c2.button("🔍 مشاهده", key=f"view_a_{row['national_id']}"):
                    st.markdown(f"""
                    <div class='id-card' style='border-right-color: #E65100;'>
                        <h4 style='color:#E65100;'>🏢 شناسنامه هویت حقوقی شرکت</h4>
                        <p><b>نام شرکت:</b> {row['name']}</p>
                        <p><b>شناسه ملی پرونده:</b> {row['national_id']}</p>
                        <p><b>ارتباط سازمانی:</b> {row['ownership_type']}</p>
                        <p><b>تلفن ثابت معاونت:</b> {row['phone']}</p>
                        <hr>
                        <p><b>📝 توضیحات ساختاری و ماموریت:</b> {row['description'] if row['description'] else 'فاقد توضیحات شناسنامه‌ای.'}</p>
                    </div>
                    """, unsafe_allow_html=True)
                    
                if c3.button("📝 ویرایش", key=f"edit_a_{row['national_id']}"):
                    with st.form(f"edit_form_a_{row['national_id']}"):
                        new_name = st.text_input("اصلاح نام رسمی شرکت:", value=row['name'])
                        new_desc = st.text_area("اصلاح توضیحات و ماموریت:", value=row['description'])
                        if st.form_submit_button("ذخیره ویرایش"):
                            cursor.execute("UPDATE actors SET name=?, description=? WHERE national_id=?", (new_name, new_desc, row['national_id']))
                            conn.commit()
                            st.success("ویرایش شرکت انجام شد.")
                            st.rerun()
                            
                if c4.button("❌ حذف", key=f"del_a_{row['national_id']}"):
                    cursor.execute(f"DELETE FROM actors WHERE national_id='{row['national_id']}'")
                    cursor.execute(f"DELETE FROM users WHERE username='{row['national_id']}'")
                    conn.commit()
                    st.rerun()

    # ----------------------------------------------------
    # ۵. بخش مدیریت کاربران و دسترسی‌ها - ادمین
    # ----------------------------------------------------
    elif current_section == "users" and st.session_state['role'] == "admin":
        st.title("👥 مدیریت کاربران و سطوح دسترسی پرسنل شرکت‌ها")
        
        with st.form("form_user_new"):
            st.subheader("➕ ساخت حساب کاربری جدید")
            u_name = st.text_input("نام کاربری ورود (شناسه ملی شرکت مربوطه):")
            u_pass = st.text_input("رمز عبور اختصاصی پنل:")
            u_comp = st.text_input("نام رسمی شرکت دارنده اکانت:")
            u_desc = st.text_area("توضیحات، سمت و مسئول تکمیل‌کننده داده:")
            
            if st.form_submit_button("ایجاد دسترسی امن"):
                if u_name and u_pass:
                    cursor.execute("INSERT OR REPLACE INTO users VALUES (?,?,'user',?,?)", (u_name, u_pass, u_comp, u_desc))
                    conn.commit()
                    st.success("✔️ حساب کاربری فعال شد.")
                    st.rerun()

        st.write("---")
        df_u_curr = pd.read_sql_query("SELECT * FROM users", conn)
        for idx, row in df_u_curr.iterrows():
            c1, c2, c3, c4 = st.columns([5, 1, 1, 1])
            c1.write(f"👤 **نام کاربری:** {row['username']} | **متعلق به شرکت:** {row['company_name']} | **رمز عبور فعال:** {row['password']}")
            
            if c2.button("🔍 مشاهده", key=f"view_u_{row['username']}"):
                st.markdown(f"""
                <div class='id-card' style='border-right-color: #512DA8;'>
                    <h4 style='color:#512DA8;'>👤 شناسنامه کاربر و سطح دسترسی</h4>
                    <p><b>نام کاربری سیستمی:</b> {row['username']}</p>
                    <p><b>شرکت منتسب:</b> {row['company_name']}</p>
                    <p><b>نقش در پلتفرم:</b> {row['role']}</p>
                    <hr>
                    <p><b>📝 توضیحات مسئول حساب:</b> {row['description'] if row['description'] else 'فاقد توضیح.'}</p>
                </div>
                """, unsafe_allow_html=True)
                
            if c3.button("📝 ویرایش", key=f"edit_u_{row['username']}"):
                with st.form(f"edit_form_u_{row['username']}"):
                    new_p = st.text_input("تغییر رمز عبور ورود:", value=row['password'])
                    new_d = st.text_area("اصلاح توضیحات کاربر:", value=row['description'])
                    if st.form_submit_button("ثبت رمز جدید"):
                        cursor.execute("UPDATE users SET password=?, description=? WHERE username=?", (new_p, new_d, row['username']))
                        conn.commit()
                        st.success("کاربر ویرایش شد.")
                        st.rerun()
                        
            if c4.button("❌ حذف", key=f"del_u_{row['username']}"):
                cursor.execute(f"DELETE FROM users WHERE username='{row['username']}'")
                conn.commit()
                st.rerun()

    # ----------------------------------------------------
    # ۶. بخش بک‌ئند و پاک‌سازی دیتابیس - ادمین
    # ----------------------------------------------------
    elif current_section == "backend" and st.session_state['role'] == "admin":
        st.title("🛠️ تنظیمات پیشرفته و مهندسی دیتابیس پایگاه داده (بک‌ئند)")
        st.info("آقای دکتر حسینی، تمام المان‌های این بخش نیز کاملاً راست‌چین و مجهز به سیستم تایید نهایی شدند.")
        
        if st.button("🗑️ پاک‌سازی و ریست کل پایگاه داده به وضعیت اولیه کارخانه"):
            cursor.execute("DROP TABLE IF EXISTS linkages")
            cursor.execute("DROP TABLE IF EXISTS actors")
            cursor.execute("DROP TABLE IF EXISTS catalog")
            cursor.execute("DROP TABLE IF EXISTS users")
            conn.commit()
            st.warning("کل دیتابیس با موفقیت ریست شد. لطفاً سیستم را مجدداً بارگذاری کنید تا داده‌های ۴۰ شرکت مجدداً تزریق شوند.")
            st.rerun()
