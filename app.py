import streamlit as st
import pandas as pd
import sqlite3
import plotly.express as px

# ۱. تنظیمات ساختاری صفحه و راست‌به‌چپ (RTL)
st.set_page_config(page_title="سامانه مدیریت داده‌های زنجیره تامین اتکا", layout="wide", initial_sidebar_state="expanded")

# اعمال استایل‌های پیشرفته CSS برای راست‌به‌چپ کردن کامل منوها، متون و جاستیفای کردن متن‌های بزرگ
st.markdown("""
    <style>
    /* راست به چپ کردن کل بدنه سایت */
    .stApp { direction: RTL; text-align: right; }
    /* راست به چپ کردن سایدبار و منوها */
    [data-testid="stSidebar"] { direction: RTL; text-align: right; position: fixed; right: 0; }
    [data-testid="stSidebarNav"] { direction: RTL; text-align: right; }
    /* تنظیم تراز متن (Justify) برای متون بزرگ */
    .justified-text { text-align: justify; direction: RTL; text-spacing: normal; }
    /* استایل دکمه‌ها */
    div.stButton > button:first-child { width: 100%; background-color: #1F4E78; color: white; border-radius: 5px; }
    /* راست چین کردن فرم‌ها و برچسب‌ها */
    .stSelectbox, .stTextInput, .stNumberInput, .stForm { direction: RTL; text-align: right; }
    div[data-baseweb="select"] { direction: RTL; text-align: right; }
    </style>
    """, unsafe_allow_html=True)

# ۲. اتصال به پایگاه داده و ساخت جداول
conn = sqlite3.connect("etka_scf_database_v4.db", check_same_thread=False)
cursor = conn.cursor()

cursor.execute("""
CREATE TABLE IF NOT EXISTS actors (
    national_id TEXT PRIMARY KEY, registro_id TEXT, economic_code TEXT, name TEXT, 
    legal_type TEXT, ownership_type TEXT, industry_1 TEXT, industry_2 TEXT, 
    phone TEXT, contact_name TEXT, contact_phone TEXT)
""")
cursor.execute("""
CREATE TABLE IF NOT EXISTS catalog (
    product_code TEXT PRIMARY KEY, product_name TEXT, chain_position TEXT, 
    unit TEXT, order_scale TEXT, eoq REAL)
""")
cursor.execute("""
CREATE TABLE IF NOT EXISTS linkages (
    id INTEGER PRIMARY KEY AUTOINCREMENT, rel_id TEXT, supplier_id TEXT, buyer_id TEXT, 
    product_code TEXT, fin_scale TEXT, time_frame TEXT)
""")
conn.commit()

# ۳. اسکریپت خودکار تزریق داده‌های نمونه (۲۰ شرکت اتکا + ۲۰ شرکت بیرونی + کاتالوگ و روابط)
def inject_sample_data():
    cursor.execute("SELECT COUNT(*) FROM actors")
    if cursor.fetchone()[0] == 0:
        # الف) ۲۰ شرکت تابعه هلدینگ اتکا (مدیریتی/غیرمدیریتی)
        etka_companies = [
            ("10101111101", "4001", "4111", "شرکت صنایع غذایی اتکا", "سهامی خاص", "مالکیت مدیریتی اتکا", "غذایی", "بازرگانی", "02128733", "مهندس علوی", "09121111101"),
            ("10101111102", "4002", "4112", "شرکت کشت و صنعت اسفراین اتکا", "سهامی خاص", "مالکیت مدیریتی اتکا", "کشاورزی و دامپروری", "-", "02128734", "مهندس اکبری", "09121111102"),
            ("10101111103", "4003", "4113", "شرکت قند و شکر اتکا", "سهامی خاص", "مالکیت مدیریتی اتکا", "غذایی", "-", "02128735", "مهندس رضایی", "09121111103"),
            ("10101111104", "4004", "4114", "شرکت روغن‌کشی خرمشهر اتکا", "سهامی خاص", "مالکیت مدیریتی اتکا", "غذایی", "شیمیایی و پتروشیمی", "02128736", "مهندس نوری", "09121111104"),
            ("10101111105", "4005", "4115", "شرکت پخش سراسری اتکا", "سهامی عام", "مالکیت مدیریتی اتکا", "بازرگانی", "خدمات و لجستیک", "02128737", "مهندس حسنی", "09121111105"),
            ("10101111106", "4006", "4116", "شرکت لجستیک زنجیره سرد اتکا", "سهامی خاص", "مالکیت مدیریتی اتکا", "خدمات و لجستیک", "-", "02128738", "مهندس کرمی", "09121111106"),
            ("10101111107", "4007", "4117", "شرکت صنایع شوینده فجر اتکا", "سهامی خاص", "مالکیت مدیریتی اتکا", "شوینده و بهداشتی", "-", "02128739", "###", "09121111107"),
            ("10101111108", "4008", "4118", "شرکت کارتن و بسته‌بندی اتکا", "سهامی خاص", "مالکیت مدیریتی اتکا", "بسته‌بندی و سلولوزی", "-", "02128740", "###", "09121111108"),
            ("10101111109", "4009", "4119", "شرکت مزارع نوین ایرانیان اتکا", "سهامی خاص", "مالکیت مدیریتی اتکا", "کشاورزی و دامپروری", "-", "02128741", "###", "09121111109"),
            ("10101111110", "4010", "4120", "شرکت بازرگانی حامی سرمایه اتکا", "سهامی خاص", "مالکیت مدیریتی اتکا", "بازرگانی", "-", "02128742", "###", "09121111110"),
            ("10101111111", "4011", "4121", "شرکت فرآورده‌های گوشتی اتکا", "سهامی خاص", "مالکیت غیرمدیریتی اتکا", "غذایی", "-", "02128743", "###", "09121111111"),
            ("10101111112", "4012", "4122", "شرکت صنایع لبنی وارنا اتکا", "سهامی خاص", "مالکیت غیرمدیریتی اتکا", "غذایی", "-", "02128744", "###", "09121111112"),
            ("10101111113", "4013", "4123", "شرکت چاپ و صحافی اتکا", "سهامی خاص", "مالکیت مدیریتی اتکا", "بسته‌بندی و سلولوزی", "-", "02128745", "###", "09121111113"),
            ("10101111114", "4014", "4124", "شرکت کشتیرانی امین اتکا", "سهامی خاص", "مالکیت مدیریتی اتکا", "خدمات و لجستیک", "-", "02128746", "###", "09121111114"),
            ("10101111115", "4015", "4125", "شرکت صنایع نساجی فخر اتکا", "سهامی خاص", "مالکیت مدیریتی اتکا", "خدمات و لجستیک", "-", "02128747", "###", "09121111115"),
            ("10101111116", "4016", "4126", "شرکت ساختمانی هما اتکا", "سهامی خاص", "مالکیت غیرمدیریتی اتکا", "خدمات و لجستیک", "-", "02128748", "###", "09121111116"),
            ("10101111117", "4017", "4127", "شرکت صنایع چوب هوشمند اتکا", "سهامی خاص", "مالکیت مدیریتی اتکا", "صنایع چوب", "-", "02128749", "###", "09121111117"),
            ("10101111118", "4018", "4128", "شرکت خدمات بیمه‌ای اتکا", "سهامی خاص", "مالکیت غیرمدیریتی اتکا", "بازرگانی", "-", "02128750", "###", "09121111118"),
            ("10101111119", "4019", "4129", "شرکت تندیس پروتئین اتکا", "سهامی خاص", "مالکیت مدیریتی اتکا", "کشاورزی و دامپروری", "غذایی", "02128751", "###", "09121111119"),
            ("10101111120", "4020", "4130", "شرکت زنجیره فروشگاه‌های اتکا", "سهامی عام", "مالکیت مدیریتی اتکا", "بازرگانی", "غذایی", "02128752", "###", "09121111120")
        ]
        # ب) ۲۰ شرکت بزرگ تأمین‌کننده خارجی خارج از گروه (مالکیت بیرونی)
        external_companies = [
            ("10202222201", "5001", "5111", "هلدینگ پتروشیمی خلیج فارس", "سهامی عام", "مالکیت بیرونی", "شیمیایی و پتروشیمی", "-", "02188221", "مهندس شریفی", "09122222201"),
            ("10202222202", "5002", "5112", "شرکت پتروشیمی تندگویان", "سهامی عام", "مالکیت بیرونی", "شیمیایی و پتروشیمی", "بسته‌بندی و سلولوزی", "02188222", "مهندس عباسی", "09122222202"),
            ("10202222203", "5003", "5113", "شرکت صنایع چوب و کاغذ مازندران", "سهامی عام", "مالکیت بیرونی", "صنایع چوب", "بسته‌بندی و سلولوزی", "02188223", "مهندس مرادی", "09122222203"),
            ("10202222204", "5004", "5114", "گروه صنعتی پاکشو (گلرنگ)", "سهامی عام", "مالکیت بیرونی", "شوینده و بهداشتی", "غذایی", "02188224", "مهندس صالحی", "09122222204"),
            ("10202222205", "5005", "5115", "شرکت توسعه کشت دانه های روغنی", "سهامی خاص", "مالکیت بیرونی", "کشاورزی و دامپروری", "غذایی", "02188225", "###", "09122222205"),
            ("10202222206", "5006", "5116", "شرکت فولاد مبارکه اصفهان", "سهامی عام", "مالکیت بیرونی", "شیمیایی و پتروشیمی", "-", "02188226", "###", "09122222206"),
            ("10202222207", "5007", "5117", "شرکت زرین غله خاورمیانه", "سهامی خاص", "مالکیت بیرونی", "بازرگانی", "کشاورزی و دامپروری", "02188227", "###", "09122222207"),
            ("10202222208", "5008", "5118", "هلدینگ داروپخش", "سهامی عام", "مالکیت بیرونی", "شیمیایی و پتروشیمی", "شوینده و بهداشتی", "02188228", "###", "09122222208"),
            ("10202222209", "5009", "5119", "شرکت کشت و صنعت کارون", "سهامی خاص", "مالکیت بیرونی", "کشاورزی و دامپروری", "غذایی", "02188229", "###", "09122222209"),
            ("10202222210", "5010", "5120", "شرکت کارتن ایران", "سهامی عام", "مالکیت بیرونی", "بسته‌بندی و سلولوزی", "-", "02188230", "###", "09122222210"),
            ("10202222211", "5011", "5121", "پتروشیمی مارون", "سهامی عام", "مالکیت بیرونی", "شیمیایی و پتروشیمی", "-", "02188231", "###", "09122222211"),
            ("10202222212", "5012", "5122", "صنایع چوب آستان قدس", "سهامی خاص", "مالکیت بیرونی", "صنایع چوب", "-", "02188232", "###", "09122222212"),
            ("10202222213", "5013", "5123", "بهپاک بهشهر", "سهامی عام", "مالکیت بیرونی", "غذایی", "کشاورزی و دامپروری", "02188233", "###", "09122222213"),
            ("10202222214", "5014", "5124", "بازرگانی دولتی ایران", "سهامی خاص", "مالکیت بیرونی", "بازرگانی", "-", "02188234", "###", "09122222214"),
            ("10202222215", "5015", "5125", "پتروشیمی شازند", "سهامی عام", "مالکیت بیرونی", "شیمیایی و پتروشیمی", "-", "02188235", "###", "09122222215"),
            ("10202222216", "5016", "5126", "کاغذسازی پارس", "سهامی عام", "مالکیت بیرونی", "بسته‌بندی و سلولوزی", "صنایع چوب", "02188236", "###", "09122222216"),
            ("10202222217", "5017", "5127", "تأمین مواد اولیه فولاد ایران", "سهامی خاص", "مالکیت بیرونی", "بازرگانی", "-", "02188237", "###", "09122222217"),
            ("10202222218", "5018", "5128", "صنایع پلاستیک کوثر", "سهامی خاص", "مالکیت بیرونی", "بسته‌بندی و سلولوزی", "شیمیایی و پتروشیمی", "02188238", "###", "09122222218"),
            ("10202222219", "5019", "5129", "هلدینگ حمل و نقل خلیج فارس", "سهامی عام", "مالکیت بیرونی", "خدمات و لجستیک", "-", "02188239", "###", "09122222219"),
            ("10202222220", "5020", "5130", "نفت جی (تامین قیر و مواد)", "سهامی عام", "مالکیت بیرونی", "شیمیایی و پتروشیمی", "-", "02188240", "###", "09122222220")
        ]
        cursor.executemany("INSERT INTO actors VALUES (?,?,?,?,?,?,?,?,?,?,?)", etka_companies + external_companies)
        
        # ج) کاتالوگ استراتژیک کالا و اقلام صنعتی نمونه
        products = [
            ("MESC-101", "روغن خام آفتابگردان فله", "مواد اولیه (Raw Materials)", "تن", "تانکر ۲۵ تنی", 500.0),
            ("MESC-102", "گرانول پلی‌اتیلن تفتان (PET)", "مواد اولیه (Raw Materials)", "کیلوگرم", "جامبوبگ ۱ تنی", 120.0),
            ("MESC-103", "ورق خمیر کاغذ استاندارد", "مواد اولیه (Raw Materials)", "تن", "پالت ۵ تنی", 200.0),
            ("IRC-201", "کارتن بسته‌بندی ۳ لایه مرغی", "ملزومات مصرفی و بسته‌بندی", "تعداد", "بسته ۵۰۰ تایی", 50000.0),
            ("IRC-202", "اسید چرب پیشرفته شوینده", "محصول میانی (Intermediate Product)", "بشکه", "کانتینر ۲۰ تایی", 150.0),
            ("IRC-301", "روغن مایع آفتابگردان ۸۰۰ گرمی اتکا", "محصول نهایی (Final Product)", "کارتن", "پالت ۱۲۰ کارتنی", 1000.0),
            ("IRC-302", "مایع ظرفشویی ۴ لیتری گام", "محصول نهایی (Final Product)", "کارتن", "پالت ۸۰ کارتنی", 800.0)
        ]
        cursor.executemany("INSERT INTO catalog VALUES (?,?,?,?,?,?)", products)
        
        # د) ماتریس نقشه‌برداری روابط مالی-زمانی زنجیره (توزیع دهک‌های تصادفی جهت تحلیل BI)
        linkages = [
            ("REL-001", "10202222205", "10101111104", "MESC-101", "۵. بسیار کلان (۱۰۰ تا ۳۰۰ میلیارد تومان)", "۴. بلندمدت (۶۰ تا ۹۰ روز)"),
            ("REL-002", "10101111104", "10101111101", "MESC-101", "۴. کلان (۵۰ تا ۱۰۰ میلیارد تومان)", "۳. میان‌مدت (۳۰ تا ۶۰ روز)"),
            ("REL-003", "10202222201", "10101111108", "MESC-102", "۶. فوق‌کلان (بالای ۳۰۰ میلیارد تومان)", "۵. خیلی بلندمدت (۹۰ تا ۱۸۰ روز)"),
            ("REL-004", "10202222203", "10101111108", "MESC-103", "۴. کلان (۵۰ تا ۱۰۰ میلیارد تومان)", "۴. بلندمدت (۶۰ تا ۹۰ روز)"),
            ("REL-005", "10101111108", "10101111101", "IRC-201", "۳. متوسط (۱۰ تا ۵۰ میلیارد تومان)", "۲. کوتاه‌مدت (زیر ۳۰ روز)"),
            ("REL-006", "10202222204", "10101111105", "IRC-302", "۵. بسیار کلان (۱۰۰ تا ۳۰۰ میلیارد تومان)", "۴. بلندمدت (۶۰ تا ۹۰ روز)"),
            ("REL-007", "10101111101", "10101111105", "IRC-301", "۶. فوق‌کلان (بالای ۳۰۰ میلیارد تومان)", "۲. کوتاه‌مدت (زیر ۳۰ روز)"),
            ("REL-008", "10101111105", "10101111120", "IRC-301", "۶. فوق‌کلان (بالای ۳۰۰ میلیارد تومان)", "۱. آنی و نقدی")
        ]
        cursor.executemany("INSERT INTO linkages (rel_id, supplier_id, buyer_id, product_code, fin_scale, time_frame) VALUES (?,?,?,?,?,?)", linkages)
        conn.commit()

inject_sample_data()

# ۴. متغیرهای ثابت مرجع آبشاری
INDUSTRIES = ["غذایی", "شوینده و بهداشتی", "بازرگانی", "بسته‌بندی و سلولوزی", "صنایع چوب", "شیمیایی و پتروشیمی", "کشاورزی و دامپروری", "خدمات و لجستیک"]
FIN_SCALES = ["۱. خرد (زیر ۱ میلیارد تومان)", "۲. کوچک (۱ تا ۱۰ میلیارد تومان)", "۳. متوسط (۱۰ تا ۵۰ میلیارد تومان)", "۴. کلان (۵۰ تا ۱۰۰ میلیارد تومان)", "۵. بسیار کلان (۱۰۰ تا ۳۰۰ میلیارد تومان)", "۶. فوق‌کلان (بالای ۳۰۰ میلیارد تومان)"]
TIME_FRAMES = ["۱. آنی و نقدی", "۲. کوتاه‌مدت (زیر ۳۰ روز)", "۳. میان‌مدت (۳۰ تا ۶۰ روز)", "۴. بلندمدت (۶۰ تا ۹۰ روز)", "۵. خیلی بلندمدت (۹۰ تا ۱۸۰ روز)", "۶. فوق بلندمدت (بالای ۱۸۰ روز)"]
POSITIONS = ["مواد اولیه (Raw Materials)", "محصول میانی (Intermediate Product)", "محصول نهایی (Final Product)", "ملزومات مصرفی و بسته‌بندی", "قطعات، لوازم یدکی و تجهیزات فنی"]

# ۵. سیستم احراز هویت
if 'logged_in' not in st.session_state:
    st.session_state.update({'logged_in': False, 'username': "", 'role': "", 'name': ""})

if not st.session_state['logged_in']:
    st.title("🔑 ورود به سامانه نقشه‌برداری زنجیره تامین اتکا")
    username = st.text_input("نام کاربری (شناسه ملی شرکت یا کلمه admin):")
    password = st.text_input("رمز عبور:", type="password")
    if st.button("ورود به پورتال"):
        if username == "admin" and password == "123":
            st.session_state.update({'logged_in': True, 'username': "admin", 'role': "admin", 'name': "آقای دکتر حسینی (مدیر کلان)"})
            st.rerun()
        else:
            # چک کردن شرکت‌ها در دیتابیس
            user_check = pd.read_sql_query(f"SELECT * FROM actors WHERE national_id='{username}'", conn)
            if not user_check.empty and password == "etka":
                st.session_state.update({'logged_in': True, 'username': username, 'role': "user", 'name': user_check['name'].values[0]})
                st.rerun()
            else:
                st.error("❌ اطلاعات ورود نامعتبر است. (برای شرکت‌ها رمز پیش‌فرض etکا است)")
else:
    st.sidebar.title("📌 منوی اصلی سامانه")
    st.sidebar.info(f"کاربر جاری: {st.session_state['name']}")
    
    menu = ["🔗 ثبت و مدیریت روابط زنجیره", "📦 کاتالوگ استراتژیک محصولات", "🏢 ثبت شناسنامه شرکت"]
    if st.session_state['role'] == "admin":
        menu.insert(0, "📊 داشبورد تحلیل کلان و هوش تجاری (BI)")
        menu.append("🛠️ مدیریت پیشرفته دیتابیس (بک‌ئند)")
        
    if st.sidebar.button("خروج از حساب کاربری"):
        st.session_state.update({'logged_in': False, 'username': "", 'role': "", 'name': ""})
        st.rerun()
        
    choice = st.sidebar.radio("انتخاب بخش:", menu)

    # ----------------------------------------------------
    # ۱. داشبورد هوش تجاری (BI) - مخصوص ادمین
    # ----------------------------------------------------
    if choice == "📊 داشبورد تحلیل کلان و هوش تجاری (BI)":
        st.title("📊 داشبورد هوش تجاری (BI) و پایش دهک‌های مالی زنجیره")
        st.markdown("<p class='justified-text'>این داشبورد به شما اجازه می‌دهد الگوهای رسوب نقدینگی، توزیع فراوانی حجم معاملات درون‌گروهی و برون‌گروهی هلدینگ اتکا و بازیگران کلیدی زنجیره ارزش را بر اساس داده‌های شبیه‌سازی‌شده پتروشیمی، صنایع چوب و سلولوزی تحلیل فرمایید.</p>", unsafe_allow_html=True)
        
        df_links = pd.read_sql_query("SELECT * FROM linkages", conn)
        df_actors = pd.read_sql_query("SELECT * FROM actors", conn)
        
        col_kpi1, col_kpi2, col_kpi3 = st.columns(3)
        col_kpi1.metric("تعداد کل روابط تجاری کشف شده", len(df_links))
        col_kpi2.metric("کل بازیگران شناسایی شده (درون و برون گروه)", len(df_actors))
        col_kpi3.metric("تعداد شرکت‌های تابعه مستقیم اتکا", len(df_actors[df_actors['ownership_type'] != 'مالکیت بیرونی']))
        
        st.write("---")
        c_graph1, c_graph2 = st.columns(2)
        with c_graph1:
            st.subheader("📈 تمرکز سرمایه در دهک‌ها و کلاس‌های مالی روابط")
            fig_fin = px.histogram(df_links, x="fin_scale", color="fin_scale", title="حجم مبادلات ریالی")
            st.plotly_chart(fig_fin, use_container_width=True)
        with c_graph2:
            st.subheader("⏳ تحلیل ساختار زمانی تسویه فاکتورها (ریسک زنجیره)")
            fig_time = px.bar(df_links, x="time_frame", color="time_frame", title="چارچوب‌های زمانی تسویه تجاری")
            st.plotly_chart(fig_time, use_container_width=True)

        st.subheader("📋 کل دیتابیس ماتریس روابط استراتژیک (خروجی تجمیعی)")
        st.dataframe(df_links, use_container_width=True)
        st.download_button("📥 دانلود مستقیم اکسل خروجی (CSV)", data=df_links.to_csv(index=False).encode('utf-8'), file_name="Etka_SCF_Full_Data.csv", mime="text/csv")

    # ----------------------------------------------------
    # ۲. ثبت و مدیریت روابط زنجیره (ایزوله شده برای شرکت‌ها)
    # ----------------------------------------------------
    elif choice == "🔗 ثبت و مدیریت روابط زنجیره":
        st.title("🔗 نقشه‌برداری و ثبت روابط تأمین کالا")
        user_id = st.session_state['username']
        is_admin = st.session_state['role'] == "admin"
        
        actors_df = pd.read_sql_query("SELECT national_id, name FROM actors", conn)
        catalog_df = pd.read_sql_query("SELECT product_code, product_name FROM catalog", conn)
        
        actor_options = dict(zip(actors_df['national_id'], actors_df['name']))
        product_options = dict(zip(catalog_df['product_code'], catalog_df['product_name']))
        
        with st.form("link_form"):
            supplier = st.selectbox("تأمین‌کننده (فروشنده):", options=list(actor_options.keys()), format_func=lambda x: actor_options[x]) if is_admin else user_id
            buyer = st.selectbox("خریدار (مشتری):", options=list(actor_options.keys()), format_func=lambda x: actor_options[x])
            product = st.selectbox("محصول مبادلاتی کاتالوگ:", options=list(product_options.keys()), format_func=lambda x: product_options[x])
            fin_scale = st.selectbox("کلاس ریالی معامله:", options=FIN_SCALES)
            time_frame = st.selectbox("چارچوب زمانی تسویه:", options=TIME_FRAMES)
            
            if st.form_submit_with_visible_submit("ثبت رابطه استراتژیک"):
                rel_id = f"REL-{supplier[:4]}-{buyer[:4]}"
                cursor.execute("INSERT INTO linkages (rel_id, supplier_id, buyer_id, product_code, fin_scale, time_frame) VALUES (?,?,?,?,?,?)",
                               (rel_id, supplier, buyer, product, fin_scale, time_frame))
                conn.commit()
                st.success(f"✔️ رابطه تجاری با کد خودکار {rel_id} با موفقیت افزوده شد.")
                st.rerun()

        st.subheader("📋 دیتابیس روابط اختصاصی قابل مشاهده")
        query = "SELECT * FROM linkages" if is_admin else f"SELECT * FROM linkages WHERE supplier_id='{user_id}' OR buyer_id='{user_id}'"
        st.dataframe(pd.read_sql_query(query, conn), use_container_width=True)

    # ----------------------------------------------------
    # ۳. کاتالوگ استراتژیک کالا و مواد
    # ----------------------------------------------------
    elif choice == "📦 کاتالوگ استراتژیک محصولات":
        st.title("📦 کاتالوگ استراتژیک فرآورده‌ها و تجهیزات زنجیره")
        with st.form("cat_form"):
            p_code = st.text_input("کد یکتای کالا (ایران‌کد / IRC):")
            p_name = st.text_input("نام کالا:")
            p_pos = st.selectbox("جایگاه تولید:", options=POSITIONS)
            p_unit = st.text_input("واحد سنجش:")
            p_scale = st.text_input("مقیاس سفارش:")
            p_eoq = st.number_input("حد بهینه سفارش (EOQ):", min_value=0.0)
            if st.form_submit_with_visible_submit("ثبت کالا"):
                try:
                    cursor.execute("INSERT INTO catalog VALUES (?,?,?,?,?,?)", (p_code, p_name, p_pos, p_unit, p_scale, p_eoq))
                    conn.commit()
                    st.success("✔️ کالا در کاتالوگ مرجع ثبت شد.")
                    st.rerun()
                except sqlite3.IntegrityError:
                    st.error("❌ خطا: این کد کالا تکراری است.")
                    
        st.dataframe(pd.read_sql_query("SELECT * FROM catalog", conn), use_container_width=True)

    # ----------------------------------------------------
    # ۴. شناسنامه شرکت‌ها
    # ----------------------------------------------------
    elif choice == "🏢 ثبت شناسنامه شرکت":
        st.title("🏢 شناسنامه هویت حقوقی بازیگران")
        with st.form("act_form"):
            n_id = st.text_input("شناسه ملی ۱۰ رقمی (کلید اصلی):")
            r_id = st.text_input("شماره ثبت:")
            e_code = st.text_input("کد اقتصادی:")
            name = st.text_input("نام شرکت:")
            legal = st.selectbox("نوع حقوقی:", ["سهامی خاص", "سهامی عام", "مسئولیت محدود"])
            owner = st.selectbox("ارتباط مالکیتی با اتکا:", ["مالکیت مدیریتی اتکا", "مالکیت غیرمدیریتی اتکا", "مالکیت بیرونی"])
            ind1 = st.selectbox("حوزه صنعت اصلی:", INDUSTRIES)
            ind2 = st.selectbox("حوزه صنعت فرعی:", ["-"] + INDUSTRIES)
            phone = st.text_input("تلفن:")
            c_name = st.text_input("رابط سامانه:")
            c_phone = st.text_input("موبایل رابط:")
            if st.form_submit_with_visible_submit("ثبت شرکت"):
                try:
                    cursor.execute("INSERT INTO actors VALUES (?,?,?,?,?,?,?,?,?,?,?)", (n_id, r_id, e_code, name, legal, owner, ind1, ind2, phone, c_name, c_phone))
                    conn.commit()
                    st.success("✔️ شرکت احراز هویت و ثبت شد.")
                    st.rerun()
                except sqlite3.IntegrityError:
                    st.error("❌ خطا: این شناسه ملی قبلاً ثبت شده است.")
                    
        st.dataframe(pd.read_sql_query("SELECT national_id, name, ownership_type, industry_1 FROM actors", conn), use_container_width=True)

    # ----------------------------------------------------
    # ۵. مدیریت پیشرفته دیتابیس (بک‌ئند مستقیم) - مخصوص ادمین
    # ----------------------------------------------------
    elif choice == "🛠️ مدیریت پیشرفته دیتابیس (بک‌ئند)":
        st.title("🛠️ پنل مدیریت مستقیم هسته دیتابیس (Backend Manager)")
        st.markdown("<p class='justified-text'>آقای دکتر، این پنل اختصاصی شماست و کاربران دیگر در فرانت‌ئند به آن دسترسی ندارند. شما می‌توانید داده‌های ورودی شرکت‌ها یا داده‌های نمونه را مستقیماً مدیریت یا حذف نمایید.</p>", unsafe_allow_html=True)
        
        tab1, tab2, tab3 = st.tabs(["🔗 مدیریت روابط", "🏢 مدیریت بازیگران", "📦 مدیریت کاتالوگ کالا"])
        
        with tab1:
            df_l = pd.read_sql_query("SELECT * FROM linkages", conn)
            st.write("حذف ردیف‌های ماتریس روابط:")
            for index, row in df_l.iterrows():
                col1, col2 = st.columns([6, 1])
                col1.write(f"رابطه {row['id']}: تأمین‌کننده {row['supplier_id']} به خریدار {row['buyer_id']} ({row['fin_scale']})")
                if col2.button(f"حذف ردیف {row['id']}", key=f"del_l_{row['id']}"):
                    cursor.execute(f"DELETE FROM linkages WHERE id={row['id']}")
                    conn.commit()
                    st.success("ردیف با موفقیت حذف شد.")
                    st.rerun()
                    
        with tab2:
            df_a = pd.read_sql_query("SELECT national_id, name FROM actors", conn)
            st.write("حذف شرکت‌ها از بانک جامع:")
            for index, row in df_a.iterrows():
                col1, col2 = st.columns([6, 1])
                col1.write(f"شرکت: {row['name']} | شناسه ملی: {row['national_id']}")
                if col2.button(f"حذف شرکت", key=f"del_a_{row['national_id']}"):
                    cursor.execute(f"DELETE FROM actors WHERE national_id='{row['national_id']}'")
                    conn.commit()
                    st.success("شرکت حذف شد.")
                    st.rerun()
                    
        with tab3:
            df_c = pd.read_sql_query("SELECT product_code, product_name FROM catalog", conn)
            st.write("حذف محصولات از کاتالوگ مرجع:")
            for index, row in df_c.iterrows():
                col1, col2 = st.columns([6, 1])
                col1.write(f"کد: {row['product_code']} | نام کالا: {row['product_name']}")
                if col2.button(f"حذف کالا", key=f"del_c_{row['product_code']}"):
                    cursor.execute(f"DELETE FROM catalog WHERE product_code='{row['product_code']}'")
                    conn.commit()
                    st.success("کالا حذف شد.")
                    st.rerun()
