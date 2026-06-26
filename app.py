import streamlit as st
import pandas as pd
import sqlite3
import plotly.express as px

# ۱. تنظیمات ساختاری صفحه و استایل‌های فوق پیشرفته راست‌چین ۱۰۰٪ و بهینه‌سازی موبایل
st.set_page_config(page_title="سامانه مدیریت زنجیره تامین", layout="wide", initial_sidebar_state="expanded")

st.markdown("""
    <style>
    /* فراخوانی و اعمال فونت بومی و استاندارد وزیر */
    @import url('https://cdn.jsdelivr.net/gh/rastikerdar/vazir-font@v30.1.0/dist/font-face.css');
    
    html, body, [data-testid="stAppViewContainer"], .stMarkdown, p, h1, h2, h3, h4, h5, h6, label, span { 
        font-family: 'Vazir', 'Tahoma', sans-serif !important; 
        direction: RTL !important; 
        text-align: right !important; 
    }
    
    /* اصلاح کامل جداول استریم‌لیت، راست‌چین کردن هدرها و سلول‌ها */
    [data-testid="stDataFrame"] *, .stDataFrame *, [data-testid="stTable"] * {
        direction: RTL !important;
        text-align: right !important;
    }
    th { 
        text-align: right !important; 
        background-color: #1F4E78 !important; 
        color: white !important; 
        font-weight: bold !important;
    }
    
    /* فیکس کردن نمایش اعداد و شماره تلفن‌ها بدون نیاز به دبل کلیک */
    td { text-align: right !important; white-space: nowrap !important; direction: ltr !important; }

    /* مهندسی مجدد سایدبار موبایل و دسکتاپ - حذف دکمه‌های رادیویی حبابی */
    [data-testid="stSidebar"] { direction: RTL !important; text-align: right !important; right: 0 !important; left: auto !important; border-left: 1px solid #e0e0e0; }
    [data-testid="stSidebarNav"] { direction: RTL !important; text-align: right !important; }
    
    /* زیباسازی دکمه‌های منو و حذف دایره‌های رادیو باتن پیش‌فرض */
    .stRadio div[role="radiogroup"] { display: block !important; }
    .stRadio div[role="radiogroup"] > label {
        display: flex !important;
        align-items: center !important;
        background-color: #ffffff !important; 
        padding: 12px 15px !important; 
        border-radius: 6px !important; 
        border-right: 5px solid #1F4E78 !important; 
        border-left: none !important;
        font-weight: bold !important; 
        font-size: 14px !important; 
        margin-bottom: 8px !important; 
        box-shadow: 0 1px 3px rgba(0,0,0,0.05);
        cursor: pointer !important;
        transition: all 0.2s ease-in-out !important;
    }
    /* حذف دایره کوچک رادیویی */
    .stRadio div[role="radiogroup"] > label div[data-testid="stMarker"] { display: none !important; }
    
    /* افکت تغییر رنگ بسیار شکیل منو هنگام قرارگیری موس */
    .stRadio div[role="radiogroup"] > label:hover { 
        background-color: #1F4E78 !important; 
        color: #ffffff !important;
    }
    
    /* استایل پنجره‌های پاپ‌آپ و کارت‌های شناسنامه کالا و شرکت */
    .id-card {
        background-color: #f9f9f9;
        padding: 20px; border-radius: 10px; border-right: 6px solid #1F4E78;
        box-shadow: 0 2px 10px rgba(0,0,0,0.05); margin-bottom: 15px;
    }
    
    /* کوچک‌سازی و چیدمان خطی دکمه‌های مینیاتوری عملیات در یک ستون */
    .mini-btn {
        display: inline-block; padding: 2px 6px; font-size: 12px; 
        cursor: pointer; border-radius: 4px; border: 1px solid #ccc; background-color: #fff;
    }
    
    /* پنهان‌سازی بخش‌های مدیریت پیشرفته دیتابیس در لایه کاربری */
    .stTabs [data-baseweb="tab"] { font-weight: bold !important; font-size: 14px !important; }
    </style>
    """, unsafe_allow_html=True)

# ۲. اتصال پایگاه داده نسخه ۷ و اعمال فیلدهای جدید اطلاعاتی کاربران (تلفن و ایمیل)
conn = sqlite3.connect("etka_scf_platform_v7.db", check_same_thread=False)
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
    username TEXT PRIMARY KEY, password TEXT, role TEXT, company_name TEXT, 
    user_phone TEXT, user_email TEXT, description TEXT)
""")
conn.commit()

# ۳. متد تزریق خودکار و شبیه‌سازی داده‌های پایه
def init_system_data():
    cursor.execute("SELECT COUNT(*) FROM actors")
    if cursor.fetchone()[0] == 0:
        etka_cos = [
            ("10101111101", "4001", "4111", "شرکت صنایع غذایی اتکا", "سهامی خاص", "مالکیت مدیریتی اتکا", "غذایی", "بازرگانی", "02128733", "مدیریت علوی", "09121111101", "هسته محوری تولید روغن هلدینگ"),
            ("10101111102", "4002", "4112", "شرکت کشت و صنعت اسفراین اتکا", "سهامی خاص", "مالکیت مدیریتی اتکا", "کشاورزی و دامپروری", "-", "02128734", "مدیریت اکبری", "09121111102", "تامین‌کننده زراعی بومی"),
            ("10101111103", "4003", "4113", "شرکت قند و شکر اتکا", "سهامی خاص", "مالکیت مدیریتی اتکا", "غذایی", "-", "02128735", "مدیریت رضایی", "09121111103", "تامین‌کننده شکر زنجیره ارزش"),
            ("10101111104", "4004", "4114", "شرکت روغن‌کشی خرمشهر اتکا", "سهامی خاص", "مالکیت مدیریتی اتکا", "غذایی", "شیمیایی و پتروشیمی", "02128736", "مدیریت نوری", "09121111104", "کارخانه استحصال روغن خام"),
            ("10101111105", "4005", "4115", "شرکت پخش سراسری اتکا", "سهامی عام", "مالکیت مدیریتی اتکا", "بازرگانی", "خدمات و لجستیک", "02128737", "مدیریت حسنی", "09121111105", "لجستیک مویرگی توزیع فرآورده‌ها"),
            ("10101111106", "4006", "4116", "شرکت لجستیک زنجیره سرد اتکا", "سهامی خاص", "مالکیت مدیریتی اتکا", "خدمات و لجستیک", "-", "02128738", "مدیریت کرمی", "09121111106", "توزیع سرد اقلام پروتئینی"),
            ("10101111107", "4007", "4117", "شرکت صنایع شوینده فجر اتکا", "سهامی خاص", "مالکیت مدیریتی اتکا", "شوینده و بهداشتی", "-", "02128739", "مدیریت شوینده", "09121111107", "تولید فرآورده‌های بهداشتی زنجیره"),
            ("10101111108", "4008", "4118", "شرکت کارتن و بسته‌بندی اتکا", "سهامی خاص", "مالکیت مدیریتی اتکا", "بسته‌بندی و سلولوزی", "-", "02128740", "مدیریت بسته‌بندی", "09121111108", "تولید ملزومات سلولوزی زنجیره")
        ]
        ext_cos = [
            ("10202222201", "5001", "5111", "هلدینگ پتروشیمی خلیج فارس", "سهامی عام", "مالکیت بیرونی", "شیمیایی و پتروشیمی", "-", "02188221", "مدیریت شریفی", "09122222201", "تامین‌کننده مواد پت پلاستیکی"),
            ("10202222205", "5005", "5115", "شرکت توسعه کشت دانه های روغنی", "سهامی خاص", "مالکیت بیرونی", "کشاورزی و دامپروری", "غذایی", "02188225", "مدیریت تامین دانه", "09122222205", "تامین مواد اولیه کشاورزی دانه‌های روغنی")
        ]
        for c in etka_cos: cursor.execute("INSERT INTO actors VALUES (?,?,?,?,?,?,?,?,?,?,?,?)", c)
        for c in ext_cos: cursor.execute("INSERT INTO actors VALUES (?,?,?,?,?,?,?,?,?,?,?,?)", c)
        for act in etka_cos + ext_cos: 
            cursor.execute("INSERT OR IGNORE INTO users VALUES (?,?,'user',?,?,?,?)", (act[0], "12345", act[3], "02188888", "info@company.ir", "اکانت رسمی بازیگر زنجیره"))
        
        prods = [
            ("MESC-101", "روغن خام آفتابگردان فله", "مواد اولیه (Raw Materials)", "تن", "تانکر ۲۵ تنی", 500.0, "اساسی‌ترین ماده اولیه فرآوری روغن"),
            ("MESC-102", "گرانول پلی‌اتیلن تفتان (PET)", "مواد اولیه (Raw Materials)", "کیلوگرم", "جامبوبگ ۱ تنی", 120.0, "ساخت پت و گالن‌های روغن مایع"),
            ("IRC-301", "روغن مایع آفتابگردان ۸۰۰ گرمی اتکا", "محصول نهایی (Final Product)", "کارتن", "پالت ۱۲۰ کارتنی", 1000.0, "توزیع نهایی فروشگاهی")
        ]
        for p in prods: cursor.execute("INSERT INTO catalog VALUES (?,?,?,?,?,?,?)", p)
        
        links = [
            ("REL-01", "10202222205", "10101111104", "MESC-101", "۵. بسیار کلان (100 تا 300 میلیارد)", "۴. بلندمدت (60 تا 90 روز)", "تامین دانه روغنی استراتژیک کشوری"),
            ("REL-02", "10101111104", "10101111101", "MESC-101", "۴. کلان (50 تا 100 میلیارد)", "۳. میان‌مدت (30 تا 60 روز)", "جریان تصفیه درون‌گروهی هلدینگ")
        ]
        for l in links: cursor.execute("INSERT INTO linkages (rel_id, supplier_id, buyer_id, product_code, fin_scale, time_frame, description) VALUES (?,?,?,?,?,?,?)", l)
        conn.commit()

init_system_data()

FIN_SCALES = ["۱. خرد (زیر ۱ میلیارد تومان)", "۲. کوچک (۱ تا ۱۰ میلیارد تومان)", "۳. متوسط (۱۰ تا ۵۰ میلیارد تومان)", "۴. کلان (۵۰ تا ۱۰۰ میلیارد تومان)", "۵. بسیار کلان (۱۰۰ تا ۳۰۰ میلیارد تومان)", "۶. فوق‌کلان (بالای ۳۰۰ میلیارد تومان)"]
TIME_FRAMES = ["۱. آنی و نقدی", "۲. کوتاه‌مدت (زیر ۳۰ روز)", "۳. میان‌مدت (۳۰ تا ۶۰ روز)", "۴. بلندمدت (۶۰ تا ۹۰ روز)", "۵. خیلی بلندمدت (۹۰ تا ۱۸۰ روز)", "۶. فوق بلندمدت (بالای ۱۸۰ روز)"]
POSITIONS = ["مواد اولیه (Raw Materials)", "محصول میانی (Intermediate Product)", "محصول نهایی (Final Product)", "ملزومات مصرفی و بسته‌بندی"]

if 'logged_in' not in st.session_state:
    st.session_state.update({'logged_in': False, 'username': "", 'role': "", 'name': ""})

# فرم احراز هویت ورود ادمین و شرکت‌ها
if not st.session_state['logged_in']:
    st.write("<br><br>", unsafe_allow_html=True)
    st.markdown("""
        <div style='background-color: white; padding: 30px; border-radius: 10px; box-shadow: 0 4px 15px rgba(0,0,0,0.08); max-width: 450px; margin: auto; border-top: 5px solid #1F4E78;'>
            <h3 style='text-align: center; color: #1F4E78; margin-bottom:5px;'>🌐 سامانه مدیریت داده‌های زنجیره تامین</h3>
            <p style='text-align: center; color: #555; font-size:13px;'>پورتال پایش هوش تجاری و ثبت ماتریس روابط استراتژیک</p>
        </div>
        """, unsafe_allow_html=True)
    c_l, c_m, c_r = st.columns([1, 1.4, 1])
    with c_m:
        u = st.text_input("👤 نام کاربری سیستمی:")
        p = st.text_input("🔑 رمز عبور پنل:", type="password")
        if st.button("ورود به پورتال مدیریت"):
            if u == "admin" and p == "123":
                st.session_state.update({'logged_in': True, 'username': "admin", 'role': "admin", 'name': "مدیریت ارشد کلان"})
                st.rerun()
            else:
                res = pd.read_sql_query(f"SELECT * FROM users WHERE username='{u}' AND password='{p}'", conn)
                if not res.empty:
                    st.session_state.update({'logged_in': True, 'username': u, 'role': res['role'].values[0], 'name': res['company_name'].values[0]})
                    st.rerun()
                else:
                    st.error("❌ اطلاعات ورود اشتباه است.")
else:
    # نقشه منوی سیستم کاربری بدون المان رادیویی حبابی زشت
    if st.session_state['role'] == "admin":
        menu_map = {
            "bi": "📊 داشبورد تحلیل کلان هوش تجاری",
            "links": "🔗 مدیریت روابط تجاری زنجیره",
            "cat": "📦 کاتالوگ استراتژیک اقلام مرجع",
            "act": "🏢 شناسنامه هویت حقوقی شرکت‌ها",
            "usr": "👥 مدیریت کاربران و دسترسی‌ها",
            "db": "🛠️ تنظیمات پایگاه داده (بک‌ئند)"
        }
    else:
        menu_map = {
            "links": "🔗 مدیریت روابط تجاری زنجیره",
            "cat": "📦 کاتالوگ استراتژیک اقلام مرجع",
            "act": "🏢 شناسنامه هویت حقوقی شرکت‌ها"
        }
        
    choice_txt = st.sidebar.radio("منوی ناوبری سیستم:", list(menu_map.values()))
    section = [k for k, v in menu_map.items() if v == choice_txt][0]

    if st.sidebar.button("🚪 خروج امن از سیستم"):
        st.session_state.update({'logged_in': False, 'username': "", 'role': "", 'name': ""})
        st.rerun()

    # بانک‌های اطلاعاتی پایه جهت استفاده در بخش‌های مختلف
    df_links = pd.read_sql_query("SELECT * FROM linkages", conn)
    df_actors = pd.read_sql_query("SELECT * FROM actors", conn)
    df_cat = pd.read_sql_query("SELECT * FROM catalog", conn)
    
    actor_map = dict(zip(df_actors['national_id'], df_actors['name']))
    prod_map = dict(zip(df_cat['product_code'], df_cat['product_name']))

    # ----------------------------------------------------
    # ۱. داشبورد تحلیل کلان هوش تجاری (BI)
    # ----------------------------------------------------
    if section == "bi":
        st.title("📊 داشبورد تحلیل کلان هوش تجاری (BI)")
        
        t1, t2, t3, t4 = st.tabs([
            "📈 ماتریس روابط زنجیره تامین", 
            "🏢 وضعیت هویتی شرکت‌ها", 
            "📦 توزیع محصولات مرجع", 
            "⚠️ پایش هوشمند نقص اطلاعات"
        ])
        
        with t1:
            st.subheader("تمرکز سرمایه و بازه‌های تسویه مالی")
            c_g1, c_g2 = st.columns(2)
            with c_g1:
                # اصلاح راست‌چین سازی ۱۰۰٪ نمودارها از طریق تنظیمات پلوتلی
                f1 = px.histogram(df_links, x="fin_scale", labels={"fin_scale": "گروه مبالغ مالی معامله", "count": "تعداد روابط"}, title="حجم تمرکز روابط تجاری بر اساس کلاس‌های ریالی")
                f1.update_layout(xaxis_title="گروه بندی مبالغ مالی معامله", yaxis_title="تعداد روابط تجاری", font=dict(family="Vazir"), title_x=1)
                st.plotly_chart(f1, use_container_width=True)
            with c_g2:
                f2 = px.bar(df_links, x="time_frame", labels={"time_frame": "چارچوب زمانی تسویه مالی", "count": "تعداد"}, title="تحلیل ساختار زمانی رسوب سرمایه و سررسید پرداخت")
                f2.update_layout(xaxis_title="چارچوب زمانی تسویه", yaxis_title="تعداد روابط تجاری", font=dict(family="Vazir"), title_x=1)
                st.plotly_chart(f2, use_container_width=True)
                
            st.write("---")
            st.subheader("📋 ماتریس جامع روابط استراتژیک زنجیره ارزش")
            if not df_links.empty:
                df_disp = df_links.copy()
                df_disp['ردیف'] = range(1, len(df_disp) + 1)
                df_disp['تأمین‌کننده (فروشنده)'] = df_disp['supplier_id'].map(actor_map)
                df_disp['خریدار (مشتری)'] = df_disp['buyer_id'].map(actor_map)
                df_disp['نام استاندارد محصول'] = df_disp['product_code'].map(prod_map)
                df_disp['حجم مالی معامله'] = df_disp['fin_scale']
                df_disp['مهلت تسویه پرداخت'] = df_disp['time_frame']
                df_disp['توضیحات قرارداد'] = df_disp['description']
                
                st.dataframe(df_disp[['ردیف', 'تأمین‌کننده (فروشنده)', 'خریدار (مشتری)', 'نام استاندارد محصول', 'حجم مالی معامله', 'مهلت تسویه پرداخت', 'توضیحات قرارداد']], use_container_width=True, hide_index=True)
                st.download_button("📥 خروجی مستقیم اکسل ماتریس روابط (CSV)", data=df_links.to_csv(index=False).encode('utf-8'), file_name="SCF_Matrix.csv", mime="text/csv")

        with t2:
            st.subheader("تحلیل وضعیت هویت شرکت‌های ثبت شده")
            f_act = px.pie(df_actors, names="ownership_type", title="سهم دسته‌بندی مالکیت شرکت‌ها در پلتفرم")
            f_act.update_layout(font=dict(family="Vazir"), title_x=1)
            st.plotly_chart(f_act, use_container_width=True)
            
            st.write("📋 لیست شرکت‌های احراز هویت شده (۷ ردیف اول جهت بهینه‌سازی صفحه):")
            df_act_sub = df_actors[['name', 'ownership_type', 'industry_1', 'phone']].head(7).copy()
            df_act_sub.columns = ['نام رسمی شرکت', 'نوع مالکیت سازمانی', 'صنعت مرجع فعالیت', 'تلفن ثابت بازرگانی']
            st.dataframe(df_act_sub, use_container_width=True, hide_index=True)
            
            # کلید پاپ‌آپ پیشرفته مشاهده لیست کامل کل شرکت‌ها طبق درخواست شما
            if st.button("🔍 مشاهده لیست کامل تمامی شرکت‌های احراز هویت شده"):
                st.write("📋 لیست کل جداول بازیگران دیتابیس:")
                df_act_all = df_actors[['name', 'ownership_type', 'industry_1', 'phone', 'description']].copy()
                df_act_all.columns = ['نام رسمی شرکت', 'نوع مالکیت سازمانی', 'صنعت مرجع فعالیت', 'تلفن ثابت بازرگانی', 'شرح ماموریت شناسنامه']
                st.dataframe(df_act_all, use_container_width=True, hide_index=True)

        with t3:
            st.subheader("پایش کاتالوگ کالاهای استراتژیک مرجع")
            f_cat = px.histogram(df_cat, x="chain_position", title="پراکنش اقلام در لایه‌های تولید زنجیره تامین")
            f_cat.update_layout(xaxis_title="جایگاه در زنجیره ارزش", yaxis_title="تعداد اقلام مرجع", font=dict(family="Vazir"), title_x=1)
            st.plotly_chart(f_cat, use_container_width=True)
            
            df_cat_disp = df_cat[['product_name', 'chain_position', 'unit', 'description']].copy()
            df_cat_disp.columns = ['نام محصول یا فرآورده', 'جایگاه در زنجیره ارزش', 'واحد سنجش معامله', 'شرح استراتژیک محصول']
            st.dataframe(df_cat_disp, use_container_width=True, hide_index=True)

        with t4:
            st.subheader("⚠️ پایش پلتفرم و اقدامات اصلاحی داده‌ها")
            all_linked = set(df_links['supplier_id'].tolist() + df_links['buyer_id'].tolist())
            inc_actors = df_actors[~df_actors['national_id'].isin(all_linked)]
            inc_prods = df_cat[~df_cat['product_code'].isin(df_links['product_code'].tolist())]
            
            c_m1, c_m2 = st.columns(2)
            with c_m1:
                st.warning("🏢 شرکت‌های ثبت‌شده بدون ماتریس روابط تجاری فعال:")
                if not inc_actors.empty:
                    st.dataframe(inc_actors[['name', 'ownership_type']].rename(columns={'name':'نام شرکت', 'ownership_type':'نوع مالکیت'}), use_container_width=True, hide_index=True)
                else:
                    st.success("کیفیت داده عالی: تمام شرکت‌ها ماتریس رابطه دارند.")
            with c_m2:
                st.warning("📦 کالاهای کاتالوگ بدون جریان معامله و سررسید پرداختی:")
                if not inc_prods.empty:
                    st.dataframe(inc_prods[['product_name', 'chain_position']].rename(columns={'product_name':'نام محصول', 'chain_position':'لایه‌ زنجیره'}), use_container_width=True, hide_index=True)
                else:
                    st.success("کیفیت داده عالی: تمام اقلام جریان فعال دارند.")

    # ----------------------------------------------------
    # ۲. مدیریت روابط تجاری زنجیره (با ستون آیکون‌های عملیاتی مینیاتوری)
    # ----------------------------------------------------
    elif section == "links":
        st.title("🔗 مدیریت روابط تجاری و فاکتورهای زنجیره")
        user_id = st.session_state['username']
        is_admin = st.session_state['role'] == "admin"
        
        with st.form("form_link_add"):
            st.subheader("➕ ثبت جریان مالی و رابطه کالا جدید")
            supp = st.selectbox("تأمین‌کننده (فروشنده):", options=list(actor_map.keys()), format_func=lambda x: actor_map[x]) if is_admin else user_id
            buyer = st.selectbox("خریدار (مشتری روابط تجاری):", options=list(actor_map.keys()), format_func=lambda x: actor_map[x])
            prod = st.selectbox("محصول مورد مبادله از کاتالوگ مرجع:", options=list(prod_map.keys()), format_func=lambda x: prod_map[x])
            f_scale = st.selectbox("کلاس و گروه مبالغ مالی رابطه:", options=FIN_SCALES)
            t_frame = st.selectbox("چارچوب زمانی و مهلت تسویه پرداخت:", options=TIME_FRAMES)
            desc = st.text_area("توضیحات بندهای قراردادی و فاکتور:")
            
            if st.form_submit_button("ذخیره قطعی ردیف معامله"):
                r_id = f"REL-{supp[:4]}-{buyer[:4]}"
                cursor.execute("INSERT INTO linkages (rel_id, supplier_id, buyer_id, product_code, fin_scale, time_frame, description) VALUES (?,?,?,?,?,?,?)",
                               (r_id, supp, buyer, prod, f_scale, t_frame, desc))
                conn.connect().commit()
                st.success("رابطه تجاری ثبت شد.")
                st.rerun()

        st.write("---")
        st.subheader("📋 ردیف‌های فعال ماتریس روابط تجاری تحت نظارت")
        q = "SELECT * FROM linkages" if is_admin else f"SELECT * FROM linkages WHERE supplier_id='{user_id}' OR buyer_id='{user_id}'"
        df_l_curr = pd.read_sql_query(q, conn)
        
        if not df_l_curr.empty:
            for idx, row in df_l_curr.iterrows():
                c1, c2 = st.columns([5, 1.2])
                s_n = actor_map.get(row['supplier_id'], row['supplier_id'])
                b_n = actor_map.get(row['buyer_id'], row['buyer_id'])
                p_n = prod_map.get(row['product_code'], row['product_code'])
                
                c1.write(f"**{idx+1}.** فروشنده: [{s_n}] ⬅️ خریدار: [{b_n}] | محصول: {p_n}")
                
                # قرارگیری آیکون‌های عملیاتی مینیاتوری در کنار هم در یک ردیف کانتینری کوچیک
                with c2:
                    sub_c1, sub_c2, sub_c3 = st.columns(3)
                    if sub_c1.button("🔍", key=f"v_l_{row['id']}", help="مشاهده شناسنامه و توضیحات"):
                        st.markdown(f"""
                        <div class='id-card'>
                            <h5>🔍 شناسنامه شرح رابطه معامله</h5>
                            <p><b>مبالغ مالی:</b> {row['fin_scale']}</p>
                            <p><b>مهلت تسویه پرداخت:</b> {row['time_frame']}</p>
                            <p><b>📝 توضیحات اختصاصی ثبت شده:</b> {row['description'] if row['description'] else 'فاقد شرح توضیحات.'}</p>
                        </div>
                        """, unsafe_allow_html=True)
                        
                    if sub_c2.button("📝", key=f"e_l_{row['id']}", help="ویرایش سریع داده"):
                        with st.form(f"ef_l_{row['id']}"):
                            n_f = st.selectbox("اصلاح گروه مبالغ:", FIN_SCALES, index=FIN_SCALES.index(row['fin_scale']) if row['fin_scale'] in FIN_SCALES else 0)
                            n_t = st.selectbox("اصلاح مهلت پرداخت:", TIME_FRAMES, index=TIME_FRAMES.index(row['time_frame']) if row['time_frame'] in TIME_FRAMES else 0)
                            n_d = st.text_area("اصلاح شرح توضیحات:", value=row['description'])
                            if st.form_submit_button("بروزرسانی دیتابیس"):
                                cursor.execute("UPDATE linkages SET fin_scale=?, time_frame=?, description=? WHERE id=?", (n_f, n_t, n_d, row['id']))
                                conn.commit()
                                st.rerun()
                                
                    if sub_c3.button("❌", key=f"d_l_{row['id']}", help="حذف قطعی ردیف"):
                        cursor.execute(f"DELETE FROM linkages WHERE id={row['id']}")
                        conn.commit()
                        st.rerun()

    # ----------------------------------------------------
    # ۳. کاتالوگ استراتژیک اقلام مرجع (با ستون آیکون‌های عملیاتی مینیاتوری)
    # ----------------------------------------------------
    elif section == "cat":
        st.title("📦 کاتالوگ استراتژیک اقلام مرجع")
        
        with st.form("form_cat_add"):
            st.subheader("➕ افزودن کالا به کاتالوگ")
            p_code = st.text_input("کد یکتای کالا یا شناسه ایران‌کد:")
            p_name = st.text_input("نام دقیق فرآورده یا کالا:")
            p_pos = st.selectbox("موقعیت در زنجیره ارزش:", options=POSITIONS)
            p_unit = st.text_input("واحد اندازه‌گیری (تن، کیلوگرم، بشکه):")
            p_scale = st.text_input("مقیاس سفارش‌گذاری لجستیکی:")
            p_eoq = st.number_input("مقدار اقتصادی بهینه سفارش (EOQ):", min_value=0.0)
            p_desc = st.text_area("توضیحات و مشخصات استراتژیک کالا:")
            
            if st.form_submit_button("ذخیره کالا در کاتالوگ مرجع"):
                try:
                    cursor.execute("INSERT INTO catalog VALUES (?,?,?,?,?,?,?)", (p_code, p_name, p_pos, p_unit, p_scale, p_eoq, p_desc))
                    conn.commit()
                    st.success("کالا اضافه شد.")
                    st.rerun()
                except sqlite3.IntegrityError:
                    st.error("کد کالا تکراری است.")

        st.write("---")
        st.subheader("📋 مدیریت اقلام موجود در کاتالوگ")
        
        if not df_cat.empty:
            for idx, row in df_cat.iterrows():
                c1, c2 = st.columns([5, 1.2])
                c1.write(f"**{idx+1}. نام محصول:** {row['product_name']} | واحد: {row['unit']} | جایگاه: {row['chain_position']}")
                
                with c2:
                    sub_c1, sub_c2, sub_c3 = st.columns(3)
                    if sub_c1.button("🔍", key=f"v_c_{row['product_code']}", help="مشاهده شناسنامه فنی کالا"):
                        st.markdown(f"""
                        <div class='id-card' style='border-right-color:#2E7D32;'>
                            <h5>📦 شناسنامه رسمی و فنی کالا</h5>
                            <p><b>مقیاس لجستیکی:</b> {row['order_scale']}</p>
                            <p><b>حجم حجم سفارش اقتصادی:</b> {row['eoq']}</p>
                            <p><b>📝 شرح توضیحات فنی کالا:</b> {row['description'] if row['description'] else 'فاقد شرح توضیحات.'}</p>
                        </div>
                        """, unsafe_allow_html=True)
                        
                    if sub_c2.button("📝", key=f"e_c_{row['product_code']}", help="ویرایش اطلاعات کالا"):
                        with st.form(f"ef_c_{row['product_code']}"):
                            n_n = st.text_input("اصلاح نام کالا:", value=row['product_name'])
                            n_u = st.text_input("اصلاح واحد اندازه‌گیری:", value=row['unit'])
                            n_d = st.text_area("اصلاح مشخصات و توضیحات:", value=row['description'])
                            if st.form_submit_button("ثبت اصلاحات"):
                                cursor.execute("UPDATE catalog SET product_name=?, unit=?, description=? WHERE product_code=?", (n_n, n_u, n_d, row['product_code']))
                                conn.commit()
                                st.rerun()
                                
                    if sub_c3.button("❌", key=f"d_c_{row['product_code']}", help="حذف کالا از کاتالوگ"):
                        cursor.execute(f"DELETE FROM catalog WHERE product_code='{row['product_code']}'")
                        conn.commit()
                        st.rerun()

    # ----------------------------------------------------
    # ۴. شناسنامه هویت حقوقی شرکت‌ها (با ستون آیکون‌های عملیاتی مینیاتوری)
    # ----------------------------------------------------
    elif section == "act":
        st.title("🏢 شناسنامه هویت حقوقی شرکت‌ها")
        
        with st.form("form_act_add"):
            st.subheader("➕ ثبت و احراز هویت شرکت جدید")
            n_id = st.text_input("شناسه ملی ۱۰ رقمی (نام کاربری ورود):")
            name = st.text_input("نام تجاری و رسمی شرکت:")
            owner = st.selectbox("نوع مالکیت و ارتباط سازمانی:", ["مالکیت مدیریتی اتکا", "مالکیت غیرمدیریتی اتکا", "مالکیت بیرونی"])
            ind1 = st.text_input("صنعت حوزه فعالیت اصلی:")
            phone = st.text_input("تلفن معاونت بازرگانی/مالی:")
            desc = st.text_area("توضیحات شناسنامه‌ای و حیطه ماموریت شرکت:")
            
            if st.form_submit_button("احراز هویت و ذخیره"):
                try:
                    cursor.execute("INSERT INTO actors (national_id, name, ownership_type, industry_1, phone, description) VALUES (?,?,?,?,?,?)", (n_id, name, owner, ind1, phone, desc))
                    cursor.execute("INSERT OR IGNORE INTO users VALUES (?,?,'user',?,'','',?)", (n_id, "12345", name, desc))
                    conn.commit()
                    st.success("شرکت احراز هویت شد.")
                    st.rerun()
                except sqlite3.IntegrityError:
                    st.error("شناسه ملی تکراری است.")

        st.write("---")
        st.subheader("📋 مدیریت شناسنامه شرکت‌های فعال")
        
        if not df_actors.empty:
            for idx, row in df_actors.iterrows():
                c1, c2 = st.columns([5, 1.2])
                c1.write(f"**🏢 شرکت:** {row['name']} | شناسه ملی: {row['national_id']} | تلفن بازرگانی: {row['phone']}")
                
                with c2:
                    sub_c1, sub_c2, sub_c3 = st.columns(3)
                    if sub_c1.button("🔍", key=f"v_a_{row['national_id']}", help="مشاهده شناسنامه شرکت"):
                        st.markdown(f"""
                        <div class='id-card' style='border-right-color:#E65100;'>
                            <h5>🏢 شناسنامه هویت حقوقی بازیگر زنجیره</h5>
                            <p><b>ارتباط سازمانی:</b> {row['ownership_type']}</p>
                            <p><b>صنعت مرجع:</b> {row['industry_1']}</p>
                            <p><b>تلفن ثابت:</b> {row['phone']}</p>
                            <p><b>📝 شرح ماموریت و توضیحات:</b> {row['description'] if row['description'] else 'فاقد شرح توضیحات.'}</p>
                        </div>
                        """, unsafe_allow_html=True)
                        
                    if sub_c2.button("📝", key=f"e_a_{row['national_id']}", help="ویرایش شناسنامه شرکت"):
                        with st.form(f"ef_a_{row['national_id']}"):
                            n_n = st.text_input("اصلاح نام رسمی:", value=row['name'])
                            n_p = st.text_input("اصلاح تلفن ثابت:", value=row['phone'])
                            n_d = st.text_area("اصلاح ماموریت و توضیحات:", value=row['description'])
                            if st.form_submit_button("ثبت اصلاحات شناسنامه"):
                                cursor.execute("UPDATE actors SET name=?, phone=?, description=? WHERE national_id=?", (n_n, n_p, n_d, row['national_id']))
                                conn.commit()
                                st.rerun()
                                
                    if sub_c3.button("❌", key=f"d_a_{row['national_id']}", help="حذف کامل از دیتابیس"):
                        cursor.execute(f"DELETE FROM actors WHERE national_id='{row['national_id']}'")
                        cursor.execute(f"DELETE FROM users WHERE username='{row['national_id']}'")
                        conn.commit()
                        st.rerun()

    # ----------------------------------------------------
    # ۵. مدیریت کاربران و دسترسی‌ها (با فیلدهای ایمیل و تلفن اختصاصی صاحب کاربری)
    # ----------------------------------------------------
    elif section == "usr" and st.session_state['role'] == "admin":
        st.title("👥 مدیریت کاربران و سطوح دسترسی پرسنل")
        
        with st.form("form_user_create"):
            st.subheader("➕ ساخت حساب کاربری جدید برای رابطین شرکت‌ها")
            u_name = st.text_input("نام کاربری اختصاصی پنل:")
            u_pass = st.text_input("رمز عبور اختصاصی پنل:")
            u_comp = st.text_input("نام رسمی شرکت دارنده اکانت:")
            u_phone = st.text_input("📞 شماره تلفن مستقیم صاحب حساب کاربری:")
            u_email = st.text_input("📧 آدرس ایمیل رسمی صاحب حساب کاربری:")
            u_desc = st.text_area("توضیحات سمت و مسئول تکمیل‌کننده داده:")
            
            if st.form_submit_button("ایجاد دسترسی امن پنل"):
                if u_name and u_pass:
                    cursor.execute("INSERT OR REPLACE INTO users VALUES (?,?,'user',?,?,?,?)", (u_name, u_pass, u_comp, u_phone, u_email, u_desc))
                    conn.commit()
                    st.success("حساب کاربری با موفقیت فعال گردید.")
                    st.rerun()

        st.write("---")
        st.subheader("📋 مدیریت اکانت‌های فعال سیستم")
        df_u_curr = pd.read_sql_query("SELECT * FROM users", conn)
        
        if not df_u_curr.empty:
            for idx, row in df_u_curr.iterrows():
                c1, c2 = st.columns([5, 1.2])
                # عدم نمایش مستقیم رمز عبور در کادر متنی عمومی جهت امنیت بالاتر لایه ادمین
                c1.write(f"👤 **نام کاربری:** {row['username']} | **شرکت منتسب:** {row['company_name']} | تلفن رابط: {row['user_phone']}")
                
                with c2:
                    sub_c1, sub_c2, sub_c3 = st.columns(3)
                    if sub_c1.button("🔍", key=f"v_u_{row['username']}", help="مشاهده پروفایل و توضیحات کاربر"):
                        st.markdown(f"""
                        <div class='id-card' style='border-right-color:#512DA8;'>
                            <h5>👤 اطلاعات تماس و دسترسی صاحب کاربری</h5>
                            <p><b>نام کاربری:</b> {row['username']}</p>
                            <p><b>رمز عبور فعال:</b> {row['password']}</p>
                            <p><b>شماره همراه صاحب اکانت:</b> {row['user_phone']}</p>
                            <p><b>ایمیل رسمی صاحب اکانت:</b> {row['user_email']}</p>
                            <hr>
                            <p><b>📝 شرح سمت و مسئولیت:</b> {row['description'] if row['description'] else 'فاقد شرح توضیحات.'}</p>
                        </div>
                        """, unsafe_allow_html=True)
                        
                    if sub_c2.button("📝", key=f"e_u_{row['username']}", help="ویرایش و تغییر رمز"):
                        with st.form(f"ef_u_{row['username']}"):
                            n_p = st.text_input("تغییر رمز عبور ورود:", value=row['password'])
                            n_ph = st.text_input("اصلاح شماره همراه رابط:", value=row['user_phone'])
                            n_em = st.text_input("اصلاح ایمیل رابط:", value=row['user_email'])
                            n_d = st.text_area("اصلاح شرح مسئولیت:", value=row['description'])
                            if st.form_submit_button("بروزرسانی حساب"):
                                cursor.execute("UPDATE users SET password=?, user_phone=?, user_email=?, description=? WHERE username=?", (n_p, n_ph, n_em, n_d, row['username']))
                                conn.commit()
                                st.rerun()
                                
                    if sub_c3.button("❌", key=f"d_u_{row['username']}", help="حذف دسترسی کاربر"):
                        if row['username'] != 'admin':
                            cursor.execute(f"DELETE FROM users WHERE username='{row['username']}'")
                            conn.commit()
                            st.rerun()

    # ----------------------------------------------------
    # ۶. تنظیمات پایگاه داده (بک‌ئند) - فاقد هرگونه متن و شرح راهنما
    # ----------------------------------------------------
    elif section == "db" and st.session_state['role'] == "admin":
        if st.button("🗑️ پاک‌سازی و ریست کامل پایگاه داده"):
            cursor.execute("DROP TABLE IF EXISTS linkages")
            cursor.execute("DROP TABLE IF EXISTS actors")
            cursor.execute("DROP TABLE IF EXISTS catalog")
            cursor.execute("DROP TABLE IF EXISTS users")
            conn.commit()
            st.rerun()
