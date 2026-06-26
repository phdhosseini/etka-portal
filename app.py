import streamlit as st
import pandas as pd
import sqlite3
import plotly.express as px

# ۱. تنظیمات ساختاری صفحه و راست‌به‌چپ (RTL) و سازگاری با موبایل
st.set_page_config(page_title="سامانه مدیریت داده‌های زنجیره تامین اتکا", layout="wide", initial_sidebar_state="expanded")

# اعمال استایل‌های پیشرفته CSS برای دگرگونی UI/UX، فونت، تراز متن و منوهای شیک
st.markdown("""
    <style>
    /* تنظیم فونت استاندارد و راست‌چین کردن کل سامانه */
    html, body, [data-testid="stAppViewContainer"] { direction: RTL; text-align: right; font-family: 'Tahoma', 'Segoe UI', sans-serif; }
    
    /* راست به چپ کردن کامل سایدبار (منو) */
    [data-testid="stSidebar"] { direction: RTL; text-align: right; right: 0; left: auto; border-left: 1px solid #e0e0e0; border-right: none; }
    [data-testid="stSidebarNav"] { direction: RTL; text-align: right; }
    
    /* زیباسازی و بزرگتر کردن دکمه‌های منوی سایدبار */
    .stRadio > div { gap: 10px; padding: 5px; }
    .stRadio div[role="radiogroup"] label { 
        background-color: #f8f9fa; padding: 12px 20px; border-radius: 8px; 
        border-right: 5px solid #1F4E78; border-left: none; width: 100%; 
        font-weight: bold; font-size: 15px; cursor: pointer; display: block; text-align: right;
    }
    .stRadio div[role="radiogroup"] label:hover { background-color: #e9ecef; }
    
    /* تراز کردن (Justified) متن‌های بزرگ توضیحی */
    .justified-text { text-align: justify; direction: RTL; text-justify: inter-word; font-size: 14px; line-height: 1.8; color: #333333; }
    
    /* استایل کارت ورود (Login Card) زیبا وسط صفحه */
    .login-container { 
        background-color: #ffffff; padding: 40px; border-radius: 12px; 
        box-shadow: 0 4px 15px rgba(0,0,0,0.1); max-width: 500px; margin: auto; border-top: 6px solid #1F4E78;
    }
    
    /* اصلاح نمایش جدول‌ها و فرم‌ها در حالت موبایل */
    .stDataFrame, .stTable { direction: RTL; text-align: right; width: 100%; }
    th { background-color: #1F4E78 !important; color: white !important; text-align: right !important; }
    td { text-align: right !important; }
    
    /* استایل دکمه‌های فرم‌ها */
    div.stButton > button { background-color: #1F4E78; color: white; border-radius: 6px; font-weight: bold; width: 100%; height: 45px; }
    div.stButton > button:hover { background-color: #153552; color: white; }
    </style>
    """, unsafe_allow_html=True)

# ۲. اتصال به پایگاه داده و ساخت ساختار جداول (شامل جدول کاربران)
conn = sqlite3.connect("etka_scf_platform_v5.db", check_same_thread=False)
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
cursor.execute("""
CREATE TABLE IF NOT EXISTS users (
    username TEXT PRIMARY KEY, password TEXT, role TEXT, company_name TEXT)
""")
conn.commit()

# ۳. تابع خودکار تزریق ۴۰ داده نمونه و ساخت اکانت‌ها در اولین اجرا
def init_system_data():
    cursor.execute("SELECT COUNT(*) FROM actors")
    if cursor.fetchone()[0] == 0:
        # الف) ۲۰ شرکت تابعه اتکا
        etka_cos = [
            ("10101111101", "4001", "4111", "شرکت صنایع غذایی اتکا", "سهامی خاص", "مالکیت مدیریتی اتکا", "غذایی", "بازرگانی", "02128733", "مهندس علوی", "09121111101"),
            ("10101111102", "4002", "4112", "شرکت کشت و صنعت اسفراین اتکا", "سهامی خاص", "مالکیت مدیریتی اتکا", "کشاورزی و دامپروری", "-", "02128734", "مهندس اکبری", "09121111102"),
            ("10101111103", "4003", "4113", "شرکت قند و شکر اتکا", "سهامی خاص", "مالکیت مدیریتی اتکا", "غذایی", "-", "02128735", "مهندس رضایی", "09121111103"),
            ("10101111104", "4004", "4114", "شرکت روغن‌کشی خرمشهر اتکا", "سهامی خاص", "مالکیت مدیریتی اتکا", "غذایی", "شیمیایی و پتروشیمی", "02128736", "مهندس نوری", "09121111104"),
            ("10101111105", "4005", "4115", "شرکت پخش سراسری اتکا", "سهامی عام", "مالکیت مدیریتی اتکا", "بازرگانی", "خدمات و لجستیک", "02128737", "مهندس حسنی", "09121111105"),
            ("10101111106", "4006", "4116", "شرکت لجستیک زنجیره سرد اتکا", "سهامی خاص", "مالکیت مدیریتی اتکا", "خدمات و لجستیک", "-", "02128738", "مهندس کرمی", "09121111106"),
            ("10101111107", "4007", "4117", "شرکت صنایع شوینده فجر اتکا", "سهامی خاص", "مالکیت مدیریتی اتکا", "شوینده و بهداشتی", "-", "02128739", "رابط شوینده", "09121111107"),
            ("10101111108", "4008", "4118", "شرکت کارتن و بسته‌بندی اتکا", "سهامی خاص", "مالکیت مدیریتی اتکا", "بسته‌بندی و سلولوزی", "-", "02128740", "رابط کارتن", "09121111108"),
            ("10101111109", "4009", "4119", "شرکت مزارع نوین ایرانیان اتکا", "سهامی خاص", "مالکیت مدیریتی اتکا", "کشاورزی و دامپروری", "-", "02128741", "رابط مزارع", "09121111109"),
            ("10101111110", "4010", "4120", "شرکت بازرگانی حامی سرمایه اتکا", "سهامی خاص", "مالکیت مدیریتی اتکا", "بازرگانی", "-", "02128742", "رابط بازرگانی", "09121111110"),
            ("10101111111", "4011", "4121", "شرکت فرآورده‌های گوشتی اتکا", "سهامی خاص", "مالکیت غیرمدیریتی اتکا", "غذایی", "-", "02128743", "رابط گوشتی", "09121111111"),
            ("10101111112", "4012", "4122", "شرکت صنایع لبنی وارنا اتکا", "سهامی خاص", "مالکیت غیرمدیریتی اتکا", "غذایی", "-", "02128744", "رابط لبنی", "09121111112"),
            ("10101111113", "4013", "4123", "شرکت چاپ و صحافی اتکا", "سهامی خاص", "مالکیت مدیریتی اتکا", "بسته‌بندی و سلولوزی", "-", "02128745", "رابط چاپ", "09121111113"),
            ("10101111114", "4014", "4124", "شرکت کشتیرانی امین اتکا", "سهامی خاص", "مالکیت مدیریتی اتکا", "خدمات و لجستیک", "-", "02128746", "رابط کشتیرانی", "09121111114"),
            ("10101111115", "4015", "4125", "شرکت صنایع نساجی فخر اتکا", "سهامی خاص", "مالکیت مدیریتی اتکا", "خدمات و لجستیک", "-", "02128747", "رابط نساجی", "09121111115"),
            ("10101111116", "4016", "4126", "شرکت ساختمانی هما اتکا", "سهامی خاص", "مالکیت غیرمدیریتی اتکا", "خدمات و لجستیک", "-", "02128748", "رابط ساختمانی", "09121111116"),
            ("10101111117", "4017", "4127", "شرکت صنایع چوب هوشمند اتکا", "سهامی خاص", "مالکیت مدیریتی اتکا", "صنایع چوب", "-", "02128749", "رابط چوب", "09121111117"),
            ("10101111118", "4018", "4128", "شرکت خدمات بیمه‌ای اتکا", "سهامی خاص", "مالکیت غیرمدیریتی اتکا", "بازرگانی", "-", "02128750", "رابط بیمه", "09121111118"),
            ("10101111119", "4019", "4129", "شرکت تندیس پروتئین اتکا", "سهامی خاص", "مالکیت مدیریتی اتکا", "کشاورزی و دامپروری", "غذایی", "02128751", "رابط پروتئین", "09121111119"),
            ("10101111120", "4020", "4130", "شرکت زنجیره فروشگاه‌های اتکا", "سهامی عام", "مالکیت مدیریتی اتکا", "بازرگانی", "غذایی", "02128752", "رابط فروشگاه", "09121111120")
        ]
        # ب) ۲۰ شرکت تأمین‌کننده بزرگ بیرونی
        ext_cos = [
            ("10202222201", "5001", "5111", "هلدینگ پتروشیمی خلیج فارس", "سهامی عام", "مالکیت بیرونی", "شیمیایی و پتروشیمی", "-", "02188221", "مهندس شریفی", "09122222201"),
            ("10202222202", "5002", "5112", "شرکت پتروشیمی تندگویان", "سهامی عام", "مالکیت بیرونی", "شیمیایی و پتروشیمی", "بسته‌بندی و سلولوزی", "02188222", "مهندس عباسی", "09122222202"),
            ("10202222203", "5003", "5113", "شرکت صنایع چوب و کاغذ مازندران", "سهامی عام", "مالکیت بیرونی", "صنایع چوب", "بسته‌بندی و سلولوزی", "02188223", "مهندس مرادی", "09122222203"),
            ("10202222204", "5004", "5114", "گروه صنعتی پاکشو (گلرنگ)", "سهامی عام", "مالکیت بیرونی", "شوینده و بهداشتی", "غذایی", "02188224", "مهندس صالحی", "09122222204"),
            ("10202222205", "5005", "5115", "شرکت توسعه کشت دانه های روغنی", "سهامی خاص", "مالکیت بیرونی", "کشاورزی و دامپروری", "غذایی", "02188225", "رابط دانه روغنی", "09122222205"),
            ("10202222206", "5006", "5116", "شرکت فولاد مبارکه اصفهان", "سهامی عام", "مالکیت بیرونی", "شیمیایی و پتروشیمی", "-", "02188226", "رابط فولاد", "09122222206"),
            ("10202222207", "5007", "5117", "شرکت زرین غله خاورمیانه", "سهامی خاص", "مالکیت بیرونی", "بازرگانی", "کشاورزی و دامپروری", "02188227", "رابط غله", "09122222207"),
            ("10202222208", "5008", "5118", "هلدینگ داروپخش", "سهامی عام", "مالکیت بیرونی", "شیمیایی و پتروشیمی", "شوینده و بهداشتی", "02188228", "رابط دارو", "09122222208"),
            ("10202222209", "5009", "5119", "شرکت کشت و صنعت کارون", "سهامی خاص", "مالکیت بیرونی", "کشاورزی و دامپروری", "غذایی", "02188229", "رابط کارون", "09122222209"),
            ("10202222210", "5010", "5120", "شرکت کارتن ایران", "سهامی عام", "مالکیت بیرونی", "بسته‌بندی و سلولوزی", "-", "02188230", "رابط کارتن ایران", "09122222210"),
            ("10202222211", "5011", "5121", "پتروشیمی مارون", "سهامی عام", "مالکیت بیرونی", "شیمیایی و پتروشیمی", "-", "02188231", "رابط مارون", "09122222211"),
            ("10202222212", "5012", "5122", "صنایع چوب آستان قدس", "سهامی خاص", "مالکیت بیرونی", "صنایع چوب", "-", "02188232", "رابط چوب قدس", "09122222212"),
            ("10202222213", "5013", "5123", "بهپاک بهشهر", "سهامی عام", "مالکیت بیرونی", "غذایی", "کشاورزی و دامپروری", "02188233", "رابط بهپاک", "09122222213"),
            ("10202222214", "5014", "5124", "بازرگانی دولتی ایران", "سهامی خاص", "مالکیت بیرونی", "بازرگانی", "-", "02188234", "رابط دولتی", "09122222214"),
            ("10202222215", "5015", "5125", "پتروشیمی شازند", "سهامی عام", "مالکیت بیرونی", "شیمیایی و پتروشیمی", "-", "02188235", "رابط شازند", "09122222215"),
            ("10202222216", "5016", "5126", "کاغذسازی پارس", "سهامی عام", "مالکیت بیرونی", "بسته‌بندی و سلولوزی", "صنایع چوب", "02188236", "رابط کاغذ پارس", "09122222216"),
            ("10202222217", "5017", "5127", "تأمین مواد اولیه فولاد ایران", "سهامی خاص", "مالکیت بیرونی", "بازرگانی", "-", "02188237", "رابط مواد فولاد", "09122222217"),
            ("10202222218", "5018", "5128", "صنایع پلاستیک کوثر", "سهامی خاص", "مالکیت بیرونی", "بسته‌بندی و سلولوزی", "شیمیایی و پتروشیمی", "02188238", "رابط پلاستیک", "09122222218"),
            ("10202222219", "5019", "5129", "هلدینگ حمل و نقل خلیج فارس", "سهامی عام", "مالکیت بیرونی", "خدمات و لجستیک", "-", "02188239", "رابط لجستیک فارس", "09122222219"),
            ("10202222220", "5020", "5130", "نفت جی (تامین قیر و مواد)", "سهامی عام", "مالکیت بیرونی", "شیمیایی و پتروشیمی", "-", "02188240", "رابط نفت جی", "0912222220")
        ]
        cursor.executemany("INSERT INTO actors VALUES (?,?,?,?,?,?,?,?,?,?,?)", etka_cos + ext_cos)
        
        # ساخت اکانت‌های پیش‌فرض ورود برای تمام ۴۰ شرکت (پسورد پیش‌فرض همگی: 12345)
        for act in etka_cos + ext_cos:
            cursor.execute("INSERT OR IGNORE INTO users VALUES (?,?,?,?)", (act[0], "12345", "user", act[3]))
            
        # ج) محصولات کاتالوگ
        prods = [
            ("MESC-101", "روغن خام آفتابگردان فله", "مواد اولیه (Raw Materials)", "تن", "تانکر ۲۵ تنی", 500.0),
            ("MESC-102", "گرانول پلی‌اتیلن تفتان (PET)", "مواد اولیه (Raw Materials)", "کیلوگرم", "جامبوبگ ۱ تنی", 120.0),
            ("MESC-103", "ورق خمیر کاغذ استاندارد", "مواد اولیه (Raw Materials)", "تن", "پالت ۵ تنی", 200.0),
            ("IRC-201", "کارتن بسته‌بندی ۳ لایه مرغی", "ملزومات مصرفی و بسته‌بندی", "تعداد", "بسته ۵۰۰ تایی", 50000.0),
            ("IRC-202", "اسید چرب پیشرفته شوینده", "محصول میانی (Intermediate Product)", "بشکه", "کانتینر ۲۰ تایی", 150.0),
            ("IRC-301", "روغن مایع آفتابگردان ۸۰۰ گرمی اتکا", "محصول نهایی (Final Product)", "کارتن", "پالت ۱۲۰ کارتنی", 1000.0),
            ("IRC-302", "مایع ظرفشویی ۴ لیتری گام", "محصول نهایی (Final Product)", "کارتن", "پالت ۸۰ کارتنی", 800.0)
        ]
        cursor.executemany("INSERT INTO catalog VALUES (?,?,?,?,?,?)", prods)
        
        # د) روابط ماتریسی نمونه
        links = [
            ("REL-01", "10202222205", "10101111104", "MESC-101", "۵. بسیار کلان (۱۰۰ تا ۳۰۰ میلیارد تومان)", "۴. بلندمدت (۶۰ تا ۹۰ روز)"),
            ("REL-02", "10101111104", "10101111101", "MESC-101", "۴. کلان (۵۰ تا ۱۰۰ میلیارد تومان)", "۳. میان‌مدت (۳۰ تا ۶۰ روز)"),
            ("REL-03", "10202222201", "10101111108", "MESC-102", "۶. فوق‌کلان (بالای ۳۰۰ میلیارد تومان)", "۵. خیلی بلندمدت (۹۰ تا ۱۸۰ روز)"),
            ("REL-04", "10202222203", "10101111108", "MESC-103", "۴. کلان (۵۰ تا ۱۰۰ میلیارد تومان)", "۴. بلندمدت (۶۰ تا ۹۰ روز)"),
            ("REL-05", "10101111108", "10101111101", "IRC-201", "۳. متوسط (۱۰ تا ۵۰ میلیارد تومان)", "۲. کوتاه‌مدت (زیر ۳۰ روز)"),
            ("REL-06", "10202222204", "10101111105", "IRC-302", "۵. بسیار کلان (۱۰۰ تا ۳۰۰ میلیارد تومان)", "۴. بلندمدت (۶۰ تا ۹۰ روز)"),
            ("REL-07", "10101111101", "10101111105", "IRC-301", "۶. فوق‌کلان (بالای ۳۰۰ میلیارد تومان)", "۲. کوتاه‌مدت (زیر ۳۰ روز)"),
            ("REL-08", "10101111105", "10101111120", "IRC-301", "۶. فوق‌کلان (بالای ۳۰۰ میلیارد تومان)", "۱. آنی و نقدی")
        ]
        cursor.executemany("INSERT INTO linkages (rel_id, supplier_id, buyer_id, product_code, fin_scale, time_frame) VALUES (?,?,?,?,?,?)", links)
        conn.commit()

init_system_data()

# لیست‌های آبشاری ثابت فارسی
INDUSTRIES = ["غذایی", "شوینده و بهداشتی", "بازرگانی", "بسته‌بندی و سلولوزی", "صنایع چوب", "شیمیایی و پتروشیمی", "کشاورزی و دامپروری", "خدمات و لجستیک"]
FIN_SCALES = ["۱. خرد (زیر ۱ میلیارد تومان)", "۲. کوچک (۱ تا ۱۰ میلیارد تومان)", "۳. متوسط (۱۰ تا ۵۰ میلیارد تومان)", "۴. کلان (۵۰ تا ۱۰۰ میلیارد تومان)", "۵. بسیار کلان (۱۰۰ تا ۳۰۰ میلیارد تومان)", "۶. فوق‌کلان (بالای ۳۰۰ میلیارد تومان)"]
TIME_FRAMES = ["۱. آنی و نقدی", "۲. کوتاه‌مدت (زیر ۳۰ روز)", "۳. میان‌مدت (۳۰ تا ۶۰ روز)", "۴. بلندمدت (۶۰ تا ۹۰ روز)", "۵. خیلی بلندمدت (۹۰ تا ۱۸۰ روز)", "۶. فوق بلندمدت (بالای ۱۸۰ روز)"]
POSITIONS = ["مواد اولیه (Raw Materials)", "محصول میانی (Intermediate Product)", "محصول نهایی (Final Product)", "ملزومات مصرفی و بسته‌بندی", "قطعات، لوازم یدکی و تجهیزات فنی"]

# ۴. هسته منطق احراز هویت کاربران
if 'logged_in' not in st.session_state:
    st.session_state.update({'logged_in': False, 'username': "", 'role': "", 'name': ""})

if not st.session_state['logged_in']:
    st.write("<br><br>", unsafe_allow_html=True)
    st.markdown("""
        <div class='login-container'>
            <h2 style='text-align: center; color: #1F4E78;'>🌐 سامانه هوشمند زنجیره تامین اتکا</h2>
            <p style='text-align: center; color: #666;'>لطفاً اطلاعات امنیتی ورود خود را وارد فرمایید.</p>
        </div>
        """, unsafe_allow_html=True)
    
    with st.container():
        c_left, c_mid, c_right = st.columns([1,2,1])
        with c_mid:
            username = st.text_input("👤 نام کاربری (شناسه ملی شرکت / admin):", key="login_user")
            password = st.text_input("🔑 رمز عبور:", type="password", key="login_pass")
            if st.button("ورود به پورتال هوشمند"):
                if username == "admin" and password == "123":
                    st.session_state.update({'logged_in': True, 'username': "admin", 'role': "admin", 'name': "آقای دکتر حسینی (مدیر کلان)"})
                    st.rerun()
                else:
                    db_u = pd.read_sql_query(f"SELECT * FROM users WHERE username='{username}' AND password='{password}'", conn)
                    if not db_u.empty:
                        st.session_state.update({'logged_in': True, 'username': username, 'role': db_u['role'].values[0], 'name': db_u['company_name'].values[0]})
                        st.rerun()
                    else:
                        st.error("❌ نام کاربری یا رمز عبور اشتباه است. (رمز پیش‌فرض شرکت‌های نمونه 12345 است)")
else:
    # منوی پیشرفته سایدبار با آیکون‌های جذاب و متن‌های بزرگ
    st.sidebar.markdown(f"<h3 style='color:#1F4E78; text-align:center;'>🧭 میز کار هوشمند</h3>", unsafe_allow_html=True)
    st.sidebar.markdown(f"<p style='text-align:center; font-weight:bold;'>👤 {st.session_state['name']}</p>", unsafe_allow_html=True)
    
    menu = ["🔗 📊 ثبت و مدیریت روابط زنجیره", "📦 🗂️ کاتالوگ استراتژیک محصولات", "🏢 📑 ثبت شناسنامه شرکت"]
    if st.session_state['role'] == "admin":
        menu.insert(0, "📊 🚀 داشبورد تحلیل کلان و هوش تجاری (BI)")
        menu.append("👥 🔒 مدیریت کاربران و دسترسی‌ها")
        menu.append("🛠️ ⚙️ مدیریت پیشرفته دیتابیس (بک‌ئند)")
        
    if st.sidebar.button("🚪 خروج امن از حساب کاربری"):
        st.session_state.update({'logged_in': False, 'username': "", 'role': "", 'name': ""})
        st.rerun()
        
    choice = st.sidebar.radio("انتخاب بخش عملکردی سامانه:", menu)

    # ----------------------------------------------------
    # ۱. داشبورد هوش تجاری (BI) - مخصوص ادمین (راست‌چین شده و فارسی کامل)
    # ----------------------------------------------------
    if "داشبرد تحلیل کلان" in choice or "📊" in choice and st.session_state['role'] == "admin":
        st.title("📊 داشبورد هوش تجاری (BI) و پایش دهک‌های مالی زنجیره")
        st.markdown("<p class='justified-text'>به پلتفرم بومی تحلیل کلان خوش آمدید. داده‌های زیر از ماتریس تأمین روابط بین ۲۰ شرکت تابعه هلدینگ اتکا و ۲۰ شرکت بزرگ بیرونی استخراج شده و دهک‌های رسوب سرمایه و ساختار پرداختی زنجیره را نمایش می‌دهد.</p>", unsafe_allow_html=True)
        
        df_links = pd.read_sql_query("SELECT * FROM linkages", conn)
        df_actors = pd.read_sql_query("SELECT * FROM actors", conn)
        
        # کارت‌های شاخص کلان (KPIs)
        kpi1, kpi2, kpi3 = st.columns(3)
        kpi1.metric("تعداد کل روابط تجاری کشف شده", len(df_links))
        kpi2.metric("کل بازیگران زنجیره تامین اتکا", len(df_actors))
        kpi3.metric("شرکت‌های درون‌گروه تابعه", len(df_actors[df_actors['ownership_type'] != 'مالکیت بیرونی']))
        
        st.write("---")
        chart_col1, chart_col2 = st.columns(2)
        
        with chart_col1:
            st.subheader("📈 تمرکز سرمایه در گروه بندی‌های مالی")
            # راست‌چین و فارسی‌سازی کامل محورهای نمودار هیستوگرام
            fig_fin = px.histogram(
                df_links, x="fin_scale", color="fin_scale",
                labels={"fin_scale": "گروه بندی مبالغ مالی معامله", "count": "تعداد روابط تجاری"},
                title="توزیع روابط در کلاس‌های ریالی"
            )
            fig_fin.update_layout(xaxis_title="گروه بندی مبالغ مالی معامله", yaxis_title="تعداد روابط تجاری", showlegend=False, font=dict(family="Tahoma"))
            st.plotly_chart(fig_fin, use_container_width=True)
            
        with chart_col2:
            st.subheader("⏳ تحلیل ساختار زمانی تسویه فاکتورها (دهک‌های ریسوب)")
            # راست‌چین و فارسی‌سازی کامل محورهای نمودار میله‌ای
            fig_time = px.bar(
                df_links, x="time_frame", color="time_frame",
                labels={"time_frame": "چارچوب زمانی تسویه", "count": "تعداد روابط تجاری"},
                title="توزیع ساختار مهلت پرداخت"
            )
            fig_time.update_layout(xaxis_title="چارچوب زمانی تسویه", yaxis_title="تعداد روابط تجاری", showlegend=False, font=dict(family="Tahoma"))
            st.plotly_chart(fig_time, use_container_width=True)

        st.write("---")
        st.subheader("📋 ماتریس جامع روابط استراتژیک زنجیره ارزش اتکا")
        
        if not df_links.empty and not df_actors.empty:
            # تبدیل آیدی دیتابیس به نام فارسی و مدیریتی قابل فهم برای ادمین
            actor_map = dict(zip(df_actors['national_id'], df_actors['name']))
            df_cat = pd.read_sql_query("SELECT product_code, product_name FROM catalog", conn)
            prod_map = dict(zip(df_cat['product_code'], df_cat['product_name']))
            
            df_display = df_links.copy()
            df_display['نام شرکت تامین کننده (فروشنده)'] = df_display['supplier_id'].map(actor_map)
            df_display['نام شرکت خریدار (مشتری)'] = df_display['buyer_id'].map(actor_map)
            df_display['نام محصول مورد مبادله'] = df_display['product_code'].map(prod_map)
            df_display['گروه بندی مالی معامله'] = df_display['fin_scale']
            df_display['چارچوب زمانی پرداخت'] = df_display['time_frame']
            
            # فیلتر کردن و انتخاب ستون‌های درخواستی کاربر به ترتیب راست به چپ
            df_clean = df_display[['نام شرکت تامین کننده (فروشنده)', 'نام شرکت خریدار (مشتری)', 'نام محصول مورد مبادله', 'گروه بندی مالی معامله', 'چارچوب زمانی پرداخت']]
            df_clean.insert(0, 'ردیف', range(1, len(df_clean) + 1))
            
            st.dataframe(df_clean, use_container_width=True, hide_index=True)
            
            # دکمه دانلود پیشرفته اکسل کلان
            st.download_button("📥 دانلود مستقیم اکسل خروجی ماتریس نهایی روابط (CSV)", data=df_links.to_csv(index=False).encode('utf-8'), file_name="Etka_SCF_Matrix_Output.csv", mime="text/csv")
        else:
            st.info("اطلاعاتی برای نمایش وجود ندارد.")

    # ----------------------------------------------------
    # ۲. ثبت و مدیریت روابط زنجیره (با رفع باگ دکمه ثبت)
    # ----------------------------------------------------
    elif "ثبت و مدیریت روابط" in choice:
        st.title("🔗 نقشه‌برداری و ثبت روابط تأمین کالا")
        user_id = st.session_state['username']
        is_admin = st.session_state['role'] == "admin"
        
        actors_df = pd.read_sql_query("SELECT national_id, name FROM actors", conn)
        catalog_df = pd.read_sql_query("SELECT product_code, product_name FROM catalog", conn)
        
        actor_options = dict(zip(actors_df['national_id'], actors_df['name']))
        product_options = dict(zip(catalog_df['product_code'], catalog_df['product_name']))
        
        with st.form("link_submission_form"):
            st.subheader("➕ ثبت رابطه تجاری جدید در زنجیره")
            supplier = st.selectbox("تأمین‌کننده (فروشنده):", options=list(actor_options.keys()), format_func=lambda x: actor_options[x]) if is_admin else user_id
            if not is_admin:
                st.info(f"🏢 شرکت ثبت‌کننده شما هستید: {st.session_state['name']}", icon="ℹ️")
                
            buyer = st.selectbox("خریدار (مشتری روابط تجاری):", options=list(actor_options.keys()), format_func=lambda x: actor_options[x])
            product = st.selectbox("محصول مورد مبادله از کاتالوگ مرجع:", options=list(product_options.keys()), format_func=lambda x: product_options[x])
            fin_scale = st.selectbox("کلاس و گروه مبالغ مالی رابطه:", options=FIN_SCALES)
            time_frame = st.selectbox("چارچوب زمانی و مهلت تسویه پرداخت:", options=TIME_FRAMES)
            
            # استفاده از متد استاندارد برای رفع خطای دکمه ثبت
            submit_btn = st.form_submit_button("ثبت قطعی و امن رابطه تجاری")
            if submit_btn:
                rel_id = f"REL-{supplier[:4]}-{buyer[:4]}"
                cursor.execute("INSERT INTO linkages (rel_id, supplier_id, buyer_id, product_code, fin_scale, time_frame) VALUES (?,?,?,?,?,?)",
                               (rel_id, supplier, buyer, product, fin_scale, time_frame))
                conn.commit()
                st.success(f"✔️ رابطه با موفقیت ثبت شد و در داشبورد کلان BI مدیر ارشد قرار گرفت.")
                st.rerun()

        st.subheader("📋 روابط اختصاصی ثبت شده تحت مدیریت شما")
        query = "SELECT * FROM linkages" if is_admin else f"SELECT * FROM linkages WHERE supplier_id='{user_id}' OR buyer_id='{user_id}'"
        st.dataframe(pd.read_sql_query(query, conn), use_container_width=True)

    # ----------------------------------------------------
    # ۳. کاتالوگ استراتژیک محصولات (با رفع باگ فرم)
    # ----------------------------------------------------
    elif "کاتالوگ استراتژیک" in choice:
        st.title("📦 کاتالوگ مرجع اقلام و کالاهای استراتژیک")
        
        with st.form("product_catalog_form"):
            p_code = st.text_input("کد یکتای محصول (ایران‌کد / IRC / کد سامانه):")
            p_name = st.text_input("نام دقیق محصول یا فرآورده:")
            p_pos = st.selectbox("موقعیت در لایه‌های تولید زنجیره ارزش:", options=POSITIONS)
            p_unit = st.text_input("واحد سنجش معامله (کیلوگرم، تن، کارتن):")
            p_scale = st.text_input("مقیاس سفارش‌گذاری لجستیکی (مثلاً پالت):")
            p_eoq = st.number_input("مقدار بهینه حجم سفارش اقتصادی (EOQ):", min_value=0.0)
            
            submit_prod = st.form_submit_button("افزودن و ذخیره محصول در کاتالوگ مرجع")
            if submit_prod:
                try:
                    cursor.execute("INSERT INTO catalog VALUES (?,?,?,?,?,?)", (p_code, p_name, p_pos, p_unit, p_scale, p_eoq))
                    conn.commit()
                    st.success("✔️ محصول جدید با موفقیت به کاتالوگ مرجع اضافه شد.")
                    st.rerun()
                except sqlite3.IntegrityError:
                    st.error("❌ خطا: این کد کالا تکراری است.")
                    
        st.dataframe(pd.read_sql_query("SELECT * FROM catalog", conn), use_container_width=True)

    # ----------------------------------------------------
    # ۴. ثبت شناسنامه شرکت (با رفع باگ فرم)
    # ----------------------------------------------------
    elif "ثبت شناسنامه شرکت" in choice:
        st.title("🏢 شناسنامه هویت حقوقی بازیگران زنجیره تامین")
        
        with st.form("company_actor_form"):
            n_id = st.text_input("شناسه ملی ۱۰ رقمی شرکت (نام کاربری ورود):")
            r_id = st.text_input("شماره ثبت رسمی:")
            e_code = st.text_input("کد اقتصادی حقوقی:")
            name = st.text_input("نام رسمی و تجاری شرکت:")
            legal = st.selectbox("نوع قالب حقوقی:", ["سهامی خاص", "سهامی عام", "مسئولیت محدود"])
            owner = st.selectbox("نوع مالکیت و ارتباط با هلدینگ اتکا:", ["مالکیت مدیریتی اتکا", "مالکیت غیرمدیریتی اتکا", "مالکیت بیرونی"])
            ind1 = st.selectbox("حوزه صنعت مرجع فعالیت:", INDUSTRIES)
            ind2 = st.selectbox("حوزه صنعت ثانویه (اختیاری):", ["-"] + INDUSTRIES)
            phone = st.text_input("تلفن ثابت بازرگانی:")
            c_name = st.text_input("نام و نام خانوادگی نماینده ارشد شرکت:")
            c_phone = st.text_input("شماره موبایل مستقیم رابط:")
            
            submit_actor = st.form_submit_button("احراز هویت و ثبت شرکت در بانک مرجع")
            if submit_actor:
                try:
                    cursor.execute("INSERT INTO actors VALUES (?,?,?,?,?,?,?,?,?,?,?)", (n_id, r_id, e_code, name, legal, owner, ind1, ind2, phone, c_name, c_phone))
                    cursor.execute("INSERT OR IGNORE INTO users VALUES (?,?,?,?)", (n_id, "12345", "user", name))
                    conn.commit()
                    st.success("✔️ شرکت با موفقیت احراز هویت شد و پنل اختصاصی آن فعال گردید.")
                    st.rerun()
                except sqlite3.IntegrityError:
                    st.error("❌ خطا: این شناسه ملی قبلاً در سامانه ثبت شده است.")
                    
        st.dataframe(pd.read_sql_query("SELECT national_id, name, ownership_type, industry_1 FROM actors", conn), use_container_width=True)

    # ----------------------------------------------------
    # ۵. مدیریت کاربران و دسترسی‌ها - جدید و مخصوص ادمین
    # ----------------------------------------------------
    elif "مدیریت کاربران" in choice and st.session_state['role'] == "admin":
        st.title("👥 پنل مدیریت کاربران و رمزهای عبور شرکت‌ها")
        st.markdown("<p class='justified-text'>آقای دکتر حسینی، در این بخش شما بر تمام ده‌ها کاربری که قرار است وارد فرانت سامانه شوند مدیریت کامل دارید. می‌توانید رمزهای آن‌ها را تغییر دهید یا کاربر جدید تعریف بفرمایید.</p>", unsafe_allow_html=True)
        
        with st.form("new_user_form"):
            st.subheader("➕ ایجاد حساب کاربری جدید برای شرکت‌ها")
            u_name = st.text_input("نام کاربری (شناسه ملی شرکت مربوطه):")
            u_pass = st.text_input("رمز عبور ورود اختصاصی:")
            u_comp = st.text_input("نام دقیق و رسمی شرکت جهت نمایش در فرانت:")
            
            if st.form_submit_button("تایید و ساخت حساب کاربری"):
                if u_name and u_pass and u_comp:
                    cursor.execute("INSERT OR REPLACE INTO users VALUES (?,?,'user',?)", (u_name, u_pass, u_comp))
                    conn.commit()
                    st.success(f"✔️ حساب کاربری برای شرکت '{u_comp}' فعال شد.")
                    st.rerun()
                else:
                    st.warning("لطفاً تمام فیلدها را تکمیل بفرمایید.")
                    
        st.write("---")
        st.subheader("📋 لیست کل کاربران فعال در سیستم")
        st.dataframe(pd.read_sql_query("SELECT username as 'نام کاربری (شناسه ملی)', password as 'رمز عبور فعال', company_name as 'نام شرکت تابعه/شریک' FROM users", conn), use_container_width=True)

    # ----------------------------------------------------
    # ۶. مدیریت پیشرفته دیتابیس (بک‌ئند) - مخصوص ادمین (کاملاً فارسی و راست‌چین)
    # ----------------------------------------------------
    elif "مدیریت پیشرفته" in choice and st.session_state['role'] == "admin":
        st.title("🛠️ پنل مدیریت مستقیم دیتابیس و پاک‌سازی داده‌ها (بک‌ئند)")
        
        tab1, tab2, tab3 = st.tabs(["🔗 مدیریت حذف روابط فاکتورها", "🏢 مدیریت حذف شرکت‌ها", "📦 مدیریت کاتالوگ اقلام"])
        
        with tab1:
            df_l = pd.read_sql_query("SELECT * FROM linkages", conn)
            df_a = pd.read_sql_query("SELECT national_id, name FROM actors", conn)
            act_map = dict(zip(df_a['national_id'], df_a['name']))
            
            st.write("ردیف‌های موجود در ماتریس روابط:")
            for idx, row in df_l.iterrows():
                s_name = act_map.get(row['supplier_id'], row['supplier_id'])
                b_name = act_map.get(row['buyer_id'], row['buyer_id'])
                
                col1, col2 = st.columns([6, 1])
                col1.write(f"رابطه {row['id']}: از تأمین‌کننده [{s_name}] به خریدار [{b_name}] - گروه مالی: {row['fin_scale']}")
                if col2.button("حذف ردیف", key=f"del_link_{row['id']}"):
                    cursor.execute(f"DELETE FROM linkages WHERE id={row['id']}")
                    conn.commit()
                    st.success("ردیف با موفقیت حذف شد.")
                    st.rerun()
                    
        with tab2:
            df_actors_all = pd.read_sql_query("SELECT national_id, name FROM actors", conn)
            for idx, row in df_actors_all.iterrows():
                col1, col2 = st.columns([6, 1])
                col1.write(f"🏢 شرکت: {row['name']} | شناسه ملی: {row['national_id']}")
                if col2.button("حذف بازیگر", key=f"del_act_{row['national_id']}"):
                    cursor.execute(f"DELETE FROM actors WHERE national_id='{row['national_id']}'")
                    cursor.execute(f"DELETE FROM users WHERE username='{row['national_id']}'")
                    conn.commit()
                    st.success("شرکت و اکانت کاربری آن حذف شد.")
                    st.rerun()
                    
        with tab3:
            df_cat_all = pd.read_sql_query("SELECT product_code, product_name FROM catalog", conn)
            for idx, row in df_cat_all.iterrows():
                col1, col2 = st.columns([6, 1])
                col1.write(f"📦 کد محصول: {row['product_code']} | نام کالا: {row['product_name']}")
                if col2.button("حذف کالا", key=f"del_cat_{row['product_code']}"):
                    cursor.execute(f"DELETE FROM catalog WHERE product_code='{row['product_code']}'")
                    conn.commit()
                    st.success("کالا از کاتالوگ حذف شد.")
                    st.rerun()
