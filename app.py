import streamlit as st
import pandas as pd
from datetime import datetime, date
import math
import mysql.connector
from mysql.connector import Error

# ==========================================
# CẤU HÌNH BẢO MẬT ADMIN & KẾT NỐI DATABASE AIVEN
# ==========================================
ADMIN_PASSWORD = "admin123"

DB_HOST = "mysql-1cc70107-anhthutran21092005-5a1e.h.aivencloud.com"
DB_PORT = 12023
DB_USER = "avnadmin"
DB_PASSWORD = "AVNS_KO5XwLUd22vzEvBne42"
DB_NAME = "defaultdb"  # Tên database mặc định trên Aiven MySQL

# Hàm khởi tạo kết nối Database
def get_db_connection():
    try:
        connection = mysql.connector.connect(
            host=DB_HOST,
            port=DB_PORT,
            user=DB_USER,
            password=DB_PASSWORD,
            database=DB_NAME,
            ssl_disabled=False # Aiven yêu cầu kết nối SSL/TLS mặc định
        )
        return connection
    except Error as e:
        st.error(f"❌ Lỗi kết nối cơ sở dữ liệu Aiven MySQL: {e}")
        return None

# ==========================================
# KHỞI TẠO CÁC BẢNG TRONG DATABASE VÀ DỮ LIỆU MAU
# ==========================================
def init_db():
    conn = get_db_connection()
    if conn is None:
        return
    cursor = conn.cursor()

    # 1. Bảng Khách sạn (hotels)
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS hotels (
        ma_hs VARCHAR(20) PRIMARY KEY,
        ten_khach_san VARCHAR(255),
        dia_diem VARCHAR(100),
        hang VARCHAR(50),
        loai_phong VARCHAR(50),
        gia_phong_dem DOUBLE
    ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;
    """)

    # 2. Bảng Đơn đặt tour (bookings)
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS bookings (
        ma_don VARCHAR(20) PRIMARY KEY,
        ten_khach VARCHAR(255),
        sdt VARCHAR(20),
        diem_den VARCHAR(100),
        so_khach VARCHAR(100),
        thoi_gian_di VARCHAR(100),
        ngay_dem VARCHAR(50),
        khach_san VARCHAR(255),
        bay VARCHAR(100),
        tong_tien DOUBLE,
        trang_thai VARCHAR(100),
        ngay_dat DATE
    ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;
    """)

    # 3. Bảng Tour (tours)
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS tours (
        id VARCHAR(20) PRIMARY KEY,
        ten_tour VARCHAR(255),
        loai VARCHAR(50),
        khoi_hanh DATE,
        trang_thai VARCHAR(100),
        so_cho INT,
        da_dat INT,
        doanh_thu DOUBLE,
        chi_phi DOUBLE
    ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;
    """)

    # 4. Bảng Nhân sự / Hướng dẫn viên (staff)
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS staff (
        ma_nv VARCHAR(20) PRIMARY KEY,
        ho_ten VARCHAR(255),
        ngay_sinh VARCHAR(50),
        cccd VARCHAR(20),
        chuc_danh VARCHAR(100),
        sdt VARCHAR(20),
        loai_the VARCHAR(50),
        ma_so_the_hdv VARCHAR(50),
        ngon_ngu VARCHAR(255),
        tuyen_duong_chinh VARCHAR(255),
        kinh_nghiem VARCHAR(100),
        trang_thai VARCHAR(100),
        lich_truc VARCHAR(255)
    ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;
    """)
    conn.commit()

    # Thêm dữ liệu mẫu vào Khách sạn nếu bảng đang trống
    cursor.execute("SELECT COUNT(*) FROM hotels")
    if cursor.fetchone()[0] == 0:
        hotels_data = [
            ("H001", "Vinpearl Resort & Spa", "Phú Quốc", "5 Sao", "Standard", 2500000),
            ("H002", "Vinpearl Discovery VIP", "Phú Quốc", "5 Sao", "VIP / Suite", 4800000),
            ("H003", "JW Marriott Phu Quoc Emerald Bay", "Phú Quốc", "5 Sao", "VIP / Suite", 8500000),
            ("H004", "Novotel Phu Quoc Resort", "Phú Quốc", "4 Sao", "Standard", 1800000),
            ("H005", "Sunset Sanato Resort", "Phú Quốc", "3 Sao", "Standard", 950000),
            ("H006", "Sun World Hotel", "Đà Nẵng", "4 Sao", "Standard", 1200000),
            ("H007", "Novotel Han River VIP", "Đà Nẵng", "5 Sao", "VIP / Suite", 3800000),
            ("H008", "InterContinental Danang Sun Peninsula", "Đà Nẵng", "5 Sao", "VIP / Suite", 9200000),
            ("H011", "Hôtel de la Coupole MGallery", "Sapa", "5 Sao", "VIP / Suite", 4900000),
            ("H012", "Silk Path Grand Resort Sapa", "Sapa", "5 Sao", "Standard", 2800000),
            ("H013", "Sapa Horizon Hotel", "Sapa", "3 Sao", "Standard", 850000),
            ("H015", "Vinpearl Resort Nha Trang", "Nha Trang", "5 Sao", "Standard", 2600000),
            ("H016", "Amiana Resort Nha Trang", "Nha Trang", "5 Sao", "VIP / Suite", 5200000),
            ("H019", "Dalat Palace Heritage Hotel", "Đà Lạt", "5 Sao", "VIP / Suite", 4200000),
            ("H021", "Terracotta Hotel & Resort", "Đà Lạt", "4 Sao", "Standard", 1500000),
            ("H024", "Vinpearl Resort & Spa Hạ Long", "Hạ Long", "5 Sao", "VIP / Suite", 4500000),
            ("H025", "FLC Grand Hotel Hạ Long", "Hạ Long", "5 Sao", "Standard", 2200000),
            ("H028", "InterContinental Westlake", "Hà Nội", "5 Sao", "VIP / Suite", 5500000),
            ("H031", "Anantara Quy Nhon Villas", "Quy Nhơn", "5 Sao", "VIP / Suite", 9800000),
            ("H034", "The Reverie Saigon", "TP. Hồ Chí Minh", "5 Sao", "VIP / Suite", 7500000)
        ]
        cursor.executemany("INSERT INTO hotels VALUES (%s, %s, %s, %s, %s, %s)", hotels_data)
        conn.commit()

    # Thêm dữ liệu mẫu vào Bookings nếu đang trống
    cursor.execute("SELECT COUNT(*) FROM bookings")
    if cursor.fetchone()[0] == 0:
        bookings_data = [
            ("BK-1001", "Anh Minh", "0901234567", "Phú Quốc", "2 NL, 1 TE(5-12t)", "Tháng 6/2026 (Cao điểm)", "4N3Đ", "Vinpearl Discovery VIP (5 Sao VIP)", "Vietnam Airlines (Phổ thông)", 48500000, "Chờ Giám đốc duyệt", "2026-09-28"),
            ("BK-1002", "Chị Hoa (Tập đoàn FPT)", "0912345678", "Sapa", "10 NL, 2 TE(<5t)", "Tháng 10/2026 (Thấp điểm)", "3N2Đ", "Hôtel de la Coupole (5 Sao VIP)", "Không vé bay", 118000000, "Đã chốt & Cọc", "2026-09-27")
        ]
        cursor.executemany("INSERT INTO bookings VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)", bookings_data)
        conn.commit()

    # Thêm dữ liệu mẫu vào Tours nếu đang trống
    cursor.execute("SELECT COUNT(*) FROM tours")
    if cursor.fetchone()[0] == 0:
        tours_data = [
            ("T001", "Hà Nội - Sapa - Fansipan 3N2Đ", "Nội địa", "2026-10-05", "Đã đủ chỗ", 25, 25, 105000000, 78000000),
            ("T002", "Đà Nẵng - Hội An - Bà Nà 4N3Đ", "Nội địa", "2026-10-10", "Mở bán", 30, 18, 104400000, 72000000)
        ]
        cursor.executemany("INSERT INTO tours VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)", tours_data)
        conn.commit()

    # Thêm dữ liệu mẫu vào Staff nếu đang trống
    cursor.execute("SELECT COUNT(*) FROM staff")
    if cursor.fetchone()[0] == 0:
        staff_data = [
            ("HDV-01", "Nguyễn Văn Tuấn", "15/08/1990", "001090012345", "HDV Quốc tế", "0908112233", "Quốc tế", "101180234", "Tiếng Anh, Tiếng Trung", "Sapa, Hà Nội, Hạ Long", "8 năm", "Sẵn sàng nhận tour", "Trực văn phòng (T2-T4)"),
            ("HDV-02", "Lê Thị Mai", "20/03/1994", "048194005678", "HDV Nội địa", "0918334455", "Nội địa", "201190567", "Tiếng Anh", "Đà Nẵng, Hội An, Huế", "5 năm", "Đang đi tour (T001)", "Đi tour Sapa (05/10 - 08/10)"),
            ("HDV-03", "Trần Hoàng Nam", "10/11/1988", "079188009988", "HDV Quốc tế", "0938556677", "Quốc tế", "101150889", "Tiếng Anh, Tiếng Hàn", "Phú Quốc, Nha Trang, Đà Lạt", "10 năm", "Sẵn sàng nhận tour", "Trực hotline hỗ trợ khách"),
            ("HDV-04", "Phạm Thị Hương", "05/02/1992", "001192003344", "HDV Quốc tế", "0971223344", "Quốc tế", "101170112", "Tiếng Nhật, Tiếng Anh", "Hà Nội, Ninh Bình, Hạ Long", "6 năm", "Sẵn sàng nhận tour", "Trực tại Cảng Quảng Ninh"),
            ("HDV-05", "Đặng Quốc Anh", "18/09/1995", "036195007711", "HDV Nội địa", "0982334455", "Nội địa", "201200334", "Tiếng Anh", "Quy Nhơn, Phú Yên, Tây Nguyên", "4 năm", "Sẵn sàng nhận tour", "Off nghỉ bù"),
            ("HDV-06", "Nguyễn Thùy Linh", "12/12/1996", "001196008822", "HDV Quốc tế", "0945667788", "Quốc tế", "101210445", "Tiếng Pháp, Tiếng Anh", "TP.HCM, Cần Thơ, Miền Tây", "3 năm", "Đang đi tour", "Đi tour Miền Tây (28/09 - 01/10)"),
            ("HDV-07", "Vũ Minh Đức", "22/07/1987", "031187004455", "HDV Quốc tế", "0912998877", "Quốc tế", "101140998", "Tiếng Đức, Tiếng Anh", "Hà Nội, Sapa, Hà Giang", "11 năm", "Sẵn sàng nhận tour", "Trực văn phòng (T5-T7)"),
            ("HDV-08", "Bùi Tuyết Mai", "30/04/1993", "040193006611", "HDV Nội địa", "0903445566", "Nội địa", "201180223", "Tiếng Anh", "Phú Quốc, Kiên Giang", "6 năm", "Đang đi tour", "Đón đoàn BK-1001 Phú Quốc"),
            ("HDV-09", "Hoàng Văn Thái", "14/06/1991", "025191002233", "HDV Quốc tế", "0934112233", "Quốc tế", "101160778", "Tiếng Nga, Tiếng Anh", "Nha Trang, Phan Thiết", "7 năm", "Sẵn sàng nhận tour", "Trực sân bay Cam Ranh"),
            ("HDV-10", "Đỗ Quang Vinh", "08/01/1989", "001189005544", "HDV Quốc tế", "0967889900", "Quốc tế", "101130556", "Tiếng Tây Ban Nha, Tiếng Anh", "Huế, Đà Nẵng, Hội An", "9 năm", "Nghỉ phép", "Nghỉ phép đến 03/10"),
            ("HDV-11", "Trịnh Thị Ngọc", "19/10/1997", "038197001122", "HDV Nội địa", "0989001122", "Nội địa", "201220119", "Tiếng Anh", "Đà Lạt, Tây Nguyên", "2 năm", "Sẵn sàng nhận tour", "Trực Fanpage hỗ trợ"),
            ("HDV-12", "Lý Văn Hùng", "03/03/1985", "020185009911", "HDV Quốc tế", "0909332211", "Quốc tế", "101110332", "Tiếng Thái, Tiếng Anh", "Đà Nẵng, Hà Nội, TP.HCM", "12 năm", "Sẵn sàng nhận tour", "Trực tổng đài điều hành"),
            ("HDV-13", "Ngô Phương Anh", "25/05/1995", "001195004488", "HDV Quốc tế", "0915667700", "Quốc tế", "101190667", "Tiếng Ý, Tiếng Anh", "Hà Nội, Hạ Long, Ninh Bình", "4 năm", "Sẵn sàng nhận tour", "Trực văn phòng (T2-T6)"),
            ("DH-01", "Phạm Quốc Bảo", "11/04/1991", "001191008899", "Chuyên viên Điều hành Tour", "0977889900", "Không", "Không", "Tiếng Anh", "Toàn quốc", "7 năm", "Đang làm việc", "Điều hành trung tâm")
        ]
        cursor.executemany("INSERT INTO staff VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)", staff_data)
        conn.commit()

    cursor.close()
    conn.close()

# Chạy tạo bảng dữ liệu khi ứng dụng mở
init_db()

# ==========================================
# CÁC HÀM THAO TÁC DATABASE (QUERY/INSERT/UPDATE)
# ==========================================
def load_hotels():
    conn = get_db_connection()
    df = pd.read_sql_query("SELECT ma_hs as 'Mã HS', ten_khach_san as 'Tên Khách Sạn', dia_diem as 'Địa điểm', hang as 'Hạng', loai_phong as 'Loại phòng', gia_phong_dem as 'Giá/Phòng/Đêm' FROM hotels", conn)
    conn.close()
    return df

def load_bookings():
    conn = get_db_connection()
    df = pd.read_sql_query("SELECT ma_don as 'Mã Đơn', ten_khach as 'Tên Khách', sdt as 'SĐT', diem_den as 'Điểm đến', so_khach as 'Số Khách', thoi_gian_di as 'Thời gian đi', ngay_dem as 'Ngày/Đêm', khach_san as 'Khách sạn', bay as 'Bay', tong_tien as 'Tổng Tiền', trang_thai as 'Trạng thái', ngay_dat as 'Ngày đặt' FROM bookings", conn)
    conn.close()
    return df

def load_tours():
    conn = get_db_connection()
    df = pd.read_sql_query("SELECT id as 'ID', ten_tour as 'Tên Tour', loai as 'Loại', khoi_hanh as 'Khởi hành', trang_thai as 'Trạng thái', so_cho as 'Số chỗ', da_dat as 'Đã đặt', doanh_thu as 'Doanh thu', chi_phi as 'Chi phí' FROM tours", conn)
    conn.close()
    return df

def load_staff():
    conn = get_db_connection()
    df = pd.read_sql_query("SELECT ma_nv as 'Mã NV', ho_ten as 'Họ và Tên', ngay_sinh as 'Ngày sinh', cccd as 'CCCD', chuc_danh as 'Chức danh', sdt as 'SĐT', loai_the as 'Loại thẻ', ma_so_the_hdv as 'Mã số thẻ HDV', ngon_ngu as 'Ngôn ngữ', tuyen_duong_chinh as 'Tuyến đường chính', kinh_nghiem as 'Kinh nghiệm', trang_thai as 'Trạng thái', lich_truc as 'Lịch trực / Phân công' FROM staff", conn)
    conn.close()
    return df

def add_booking(b):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("""
        INSERT INTO bookings (ma_don, ten_khach, sdt, diem_den, so_khach, thoi_gian_di, ngay_dem, khach_san, bay, tong_tien, trang_thai, ngay_dat)
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
    """, (b["Mã Đơn"], b["Tên Khách"], b["SĐT"], b["Điểm đến"], b["Số Khách"], b["Thời gian đi"], b["Ngày/Đêm"], b["Khách sạn"], b["Bay"], b["Tổng Tiền"], b["Trạng thái"], b["Ngày đặt"]))
    conn.commit()
    cursor.close()
    conn.close()

def update_booking_status(ma_don, status):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("UPDATE bookings SET trang_thai = %s WHERE ma_don = %s", (status, ma_don))
    conn.commit()
    cursor.close()
    conn.close()

def add_staff_db(s):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("""
        INSERT INTO staff (ma_nv, ho_ten, ngay_sinh, cccd, chuc_danh, sdt, loai_the, ma_so_the_hdv, ngon_ngu, tuyen_duong_chinh, kinh_nghiem, trang_thai, lich_truc)
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
    """, (s["Mã NV"], s["Họ và Tên"], s["Ngày sinh"], s["CCCD"], s["Chức danh"], s["SĐT"], s["Loại thẻ"], s["Mã số thẻ HDV"], s["Ngôn ngữ"], s["Tuyến đường chính"], s["Kinh nghiệm"], s["Trạng thái"], s["Lịch trực / Phân công"]))
    conn.commit()
    cursor.close()
    conn.close()

# ==========================================
# KHỞI TẠO SESSION STATE DÀNH CHO ADMIN
# ==========================================
if 'admin_authenticated' not in st.session_state:
    st.session_state.admin_authenticated = False

# ==========================================
# 1. CẤU HÌNH TRANG & GIAO DIỆN HỆ THỐNG
# ==========================================
st.set_page_config(
    page_title="Viet Travel Enterprise - Platform Điều Hành & Đặt Tour",
    page_icon="✈️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS cho giao diện
st.markdown("""
<style>
    .main-title {
        font-size: 26px;
        font-weight: bold;
        color: #1E3A8A;
        padding-bottom: 10px;
        border-bottom: 2px solid #E5E7EB;
        margin-bottom: 20px;
    }
    .booking-card {
        background-color: #F0FDF4;
        border: 2px solid #16A34A;
        padding: 20px;
        border-radius: 12px;
        text-align: center;
        box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1);
    }
    .policy-box {
        background-color: #EFF6FF;
        border-left: 4px solid #3B82F6;
        padding: 12px 15px;
        border-radius: 4px;
        margin-top: 15px;
        font-size: 14px;
    }
    .login-box {
        max-width: 450px;
        margin: 50px auto;
        padding: 30px;
        background-color: #FFFFFF;
        border: 1px solid #E5E7EB;
        border-radius: 12px;
        box-shadow: 0 10px 15px -3px rgba(0, 0, 0, 0.1);
    }
</style>
""", unsafe_allow_html=True)

# ==========================================
# 2. DỮ LIỆU THAM CHIẾU HỆ THỐNG
# ==========================================
FLIGHT_RATES = {
    "Vietjet Air": {"Phổ thông": 1800000, "Thương gia": 4500000},
    "Vietnam Airlines": {"Phổ thông": 2800000, "Thương gia": 6500000},
    "Bamboo Airways": {"Phổ thông": 2200000, "Thương gia": 5200000}
}

ITINERARY_DATABASE = {
    "sapa": """
🗓️ **Lịch trình gợi ý Sapa (3 Ngày 2 Đêm):**
- **Ngày 1:** Đến Sapa -> Check-in khách sạn -> Tham quan Bản Cát Cát, tìm hiểu văn hóa H'Mông -> Tối dạo Chợ đêm, thưởng thức đồ nướng.
- **Ngày 2:** Chinh phục Đỉnh Fansipan bằng cáp treo -> Chiều check-in Moana Sapa / Cầu kính Rồng Mây -> Tối tắm lá thuốc người Dao đỏ.
- **Ngày 3:** Thăm Thung lũng Mường Hoa / Đèo Ô Quy Hồ -> Mua đặc sản (thịt trâu gác bếp, hạt dổi) -> Khởi hành về.
    """,
    "phú quốc": """
🗓️ **Lịch trình gợi ý Phú Quốc (4 Ngày 3 Đêm):**
- **Ngày 1:** Đón sân bay -> Check-in resort -> Chiều ngắm hoàng hôn tại Sunset Sanato / Grand World -> Tối khám phá Chợ đêm Phú Quốc.
- **Ngày 2:** Tour 4 Đảo (Hòn Mây Rút, Hòn Móng Tay...) -> Lặn ngắm san hô -> Trải nghiệm Cáp treo Hòn Thơm dài nhất thế giới.
- **Ngày 3:** Khám phá VinWonders & Vinpearl Safari -> Tối xem show diễn triệu đô Grand World (Sắc Màu Venices).
- **Ngày 4:** Mua sắm đặc sản (Hạt tiêu, Rượu sim, Nước mắm) -> Tự do tắm biển -> Ra sân bay.
    """,
    "đà nẵng": """
🗓️ **Lịch trình gợi ý Đà Nẵng - Hội An (3 Ngày 2 Đêm):**
- **Ngày 1:** Đón khách Đà Nẵng -> Bán đảo Sơn Trà (Chùa Linh Ứng) -> Chiều di chuyển Phố cổ Hội An, thả hoa đăng -> Tối về Đà Nẵng.
- **Ngày 2:** Vui chơi trọn ngày tại Sun World Bà Nà Hills (Check-in Cầu Vàng, Làng Pháp) -> Tối ngắm Cầu Rồng phun lửa/nước.
- **Ngày 3:** Tham quan Danh thắng Ngũ Hành Sơn -> Mua sắm Chợ Hàn -> Tiễn sân bay.
    """,
    "đà lạt": """
🗓️ **Lịch trình gợi ý Đà Lạt (3 Ngày 2 Đêm):**
- **Ngày 1:** Check-in Quảng trường Lâm Viên, Hồ Xuân Hương -> Tham quan Dinh I / Dinh III -> Tối dạo Chợ Âm Phủ thưởng thức bánh tráng nướng.
- **Ngày 2:** Săn mây đồi Cầu Đất -> Tham quan Chùa Ve Chai (Linh Phước) -> Chiều check-in Thung lũng Tình Yêu / Mongo Land -> Tối nghe nhạc acoustic.
- **Ngày 3:** Langbiang -> Thác Datanla (chơi xe trượt) -> Mua mứt đặc sản Đà Lạt -> Về lại.
    """,
    "hạ long": """
🗓️ **Lịch trình gợi ý Hạ Long (2 Ngày 1 Đêm):**
- **Ngày 1:** Lên du thuyền thăm Vịnh Hạ Long (Động Thiên Cung, Hang Đầu Gỗ, Hòn Gà Chọi) -> Ăn trưa hải sản trên tàu -> Check-in khách sạn -> Tối quẩy tại Sun World Park.
- **Ngày 2:** Tắm biển Bãi Cháy -> Mua chả mực Hạ Long -> Trả phòng về.
    """,
    "nha trang": """
🗓️ **Lịch trình gợi ý Nha Trang (3 Ngày 2 Đêm):**
- **Ngày 1:** Đón khách -> Tháp Bà Ponagar -> Chùa Long Sơn -> Chiều tắm biển Trần Phú -> Tối ăn hải sản.
- **Ngày 2:** Vui chơi trọn gói tại VinWonders Hòn Tre (Cáp treo vượt biển, công viên nước, show Tata) -> Tối dạo chợ đêm.
- **Ngày 3:** Tour lặn biển Hòn Mun / Đảo Yến -> Mua yến sào, nem nướng -> Tiễn khách.
    """
}

TRANSPORT_RATES = {
    "Phú Quốc": 1200000, "Đà Nẵng": 1000000, "Hà Nội": 900000, "Sapa": 1500000,
    "Nha Trang": 1100000, "Đà Lạt": 1300000, "Hạ Long": 1200000, "Quy Nhơn": 1200000, "TP. Hồ Chí Minh": 1000000
}
GUIDE_RATE = 800000
MEAL_RATES = {"3 Sao": 150000, "4 Sao": 250000, "5 Sao": 450000}

if "chat_history" not in st.session_state:
    st.session_state.chat_history = [
        {"role": "assistant", "content": "Xin chào! Tôi là Trợ lý ảo tư vấn tour Viet Travel 🤖.\n\nBạn muốn tìm hiểu lịch trình du lịch ở đâu (Sapa, Phú Quốc, Đà Nẵng, Đà Lạt, Hạ Long, Nha Trang...) hoặc có thắc mắc gì về dịch vụ không ạ?"}
    ]

# Tải dữ liệu từ Database
df_hotels = load_hotels()
df_bookings = load_bookings()
df_tours = load_tours()
df_staff = load_staff()

# ==========================================
# 3. THANH ĐIỀU HƯỚNG CHÍNH (SIDEBAR)
# ==========================================
with st.sidebar:
    st.image("https://cdn-icons-png.flaticon.com/512/201/201623.png", width=65)
    st.title("VIET TRAVEL ENTERPRISE")
    app_mode = st.radio(
        "🔀 CHỌN CHẾ ĐỘ SỬ DỤNG:",
        ["🌟 CỔNG ĐẶT TOUR (Dành cho Khách)", "💬 CHATBOT TƯ VẤN LỊCH TRÌNH", "👔 HỆ THỐNG QUẢN TRỊ (Dành cho CEO)"],
        index=0
    )
    st.divider()
    
    if "CEO" in app_mode:
        if st.session_state.admin_authenticated:
            st.success("🔓 BẠN ĐÃ ĐĂNG NHẬP ADMIN")
            ceo_menu = st.selectbox(
                "DANH MỤC QUẢN TRỊ:",
                [
                    "📊 Dashboard Điều hành CEO",
                    "📥 Tiếp nhận & Duyệt Đơn đặt",
                    "👨‍💼 Quản lý Nhân sự & HDV",
                    "🏨 Quản lý Khách sạn Partner",
                    "🗺️ Quản lý Tour & Vận hành",
                    "💰 Báo cáo Tài chính"
                ]
            )
            if st.button("🔒 Đăng xuất Quản trị"):
                st.session_state.admin_authenticated = False
                st.rerun()

# ==========================================
# 4. KHU VỰC HIỂN THỊ NỘI DUNG CHÍNH
# ==========================================

# ------------------------------------------
# CHẾ ĐỘ 1: CỔNG ĐẶT TOUR
# ------------------------------------------
if "CỔNG ĐẶT TOUR" in app_mode:
    st.markdown('<div class="main-title">🏖️ ĐẶT TOUR DU LỊCH THIẾT KẾ THEO YÊU CẦU CỦA BẠN</div>', unsafe_allow_html=True)
    st.caption("Hãy tự do thiết kế chuyến đi hoàn hảo của bạn. Hệ thống sẽ tự động tính toán chi phí minh bạch tức thì!")
    c_left, c_right = st.columns([1.2, 1])
    with c_left:
        st.subheader("1. Thời gian & Mùa vụ du lịch")
        col_t1, col_t2 = st.columns(2)
        with col_t1:
            travel_month = st.selectbox(
                "📅 Chọn tháng khởi hành",
                [f"Tháng {m}" for m in range(1, 13)],
                index=5
            )
        with col_t2:
            month_num = int(travel_month.split(" ")[1])
            is_peak = month_num in [6, 7, 8, 12, 1]
            season_label = "🔥 Mùa Cao Điểm (+20% phí)" if is_peak else "🍃 Mùa Thấp Điểm (Giá chuẩn)"
            st.text_input("Trạng thái mùa vụ", value=season_label, disabled=True)
        
        st.subheader("2. Thông tin Chuyến đi & Cơ cấu Khách")
        available_locations = sorted(list(df_hotels["Địa điểm"].unique()))
        col_a, col_b = st.columns(2)
        with col_a:
            destination = st.selectbox("📍 Điểm đến bạn muốn đi", available_locations)
            pax_adult = st.number_input("👨‍🦰 Người lớn (≥ 12 tuổi) [100% giá]", min_value=1, value=2, step=1)
            pax_child_5_12 = st.number_input("🧒 Trẻ em (5 - 12 tuổi) [50% giá]", min_value=0, value=1, step=1)
            pax_child_under_5 = st.number_input("👶 Trẻ em (< 5 tuổi) [Miễn phí 0%]", min_value=0, value=0, step=1)
        with col_b:
            days = st.number_input("☀️ Số ngày đi", min_value=1, value=3, step=1)
            nights = st.number_input("🌙 Số đêm ở", min_value=0, value=2, step=1)
            star_rating = st.selectbox("⭐ Hạng Khách sạn mong muốn", ["5 Sao", "4 Sao", "3 Sao"])
            room_type = st.selectbox("🛏️ Loại phòng", ["Standard", "VIP / Suite"])
            matched_hotels = df_hotels[
                (df_hotels["Địa điểm"] == destination) & 
                (df_hotels["Hạng"] == star_rating) & 
                (df_hotels["Loại phòng"] == room_type)
            ]
            if not matched_hotels.empty:
                selected_hotel_name = st.selectbox("🏨 Khách sạn gợi ý phù hợp nhất", matched_hotels["Tên Khách Sạn"].unique())
                hotel_price_per_night = matched_hotels[matched_hotels["Tên Khách Sạn"] == selected_hotel_name]["Giá/Phòng/Đêm"].values[0]
            else:
                selected_hotel_name = f"Khách sạn Tiêu chuẩn {star_rating} (Tham chiếu)"
                hotel_price_per_night = 4500000 if star_rating == "5 Sao" else (2000000 if star_rating == "4 Sao" else 900000)
                st.info(f"💡 Chưa có Partner cụ thể cho tùy chọn này. Sử dụng đơn giá tham chiếu {star_rating}.")
        
        st.subheader("3. Phương tiện & Dịch vụ đi kèm")
        col_f1, col_f2 = st.columns(2)
        with col_f1:
            inc_flight = st.checkbox("Đặt thêm Vé máy bay khứ hồi", value=False)
            airline_choice = "Không đặt"
            flight_class = "Không đặt"
            if inc_flight:
                airline_choice = st.selectbox("Hãng hàng không", list(FLIGHT_RATES.keys()))
                flight_class = st.selectbox("Hạng ghế", ["Phổ thông", "Thương gia"])
        with col_f2:
            inc_car = st.checkbox("Xe riêng đưa đón suốt tuyến", value=True)
            inc_guide = st.checkbox("Hướng dẫn viên chuyên nghiệp", value=True)
            inc_meal = st.checkbox("Bao gồm ăn uống (3 bữa/ngày)", value=True)
        
        st.markdown("""
        <div class="policy-box">
            <b>📌 LƯU Ý TRONG CHƯƠNG TRÌNH TOUR:</b><br>
            • <b>Độ tuổi tính phí:</b> Trẻ em < 5 tuổi miễn phí dịch vụ tour; Từ 5 đến dưới 12 tuổi tính 50% giá tour; Từ 12 tuổi trở lên tính giá như người lớn.<br>
            • <b>Mùa vụ:</b> Mùa cao điểm (Tháng 6, 7, 8 và Tháng 12, 1) áp dụng phụ thu 20% do chênh lệch chi phí dịch vụ, phòng nghỉ và vé tham quan.<br>
            • <b>Vé máy bay:</b> Giá vé trẻ em tuân thủ theo quy định riêng của từng hãng hàng không.
        </div>
        """, unsafe_allow_html=True)
    
    with c_right:
        st.subheader("4. Báo Giá Chuyến Đi Chi Tiết")
        effective_pax_services = pax_adult + (pax_child_5_12 * 0.5)
        total_people_count = pax_adult + pax_child_5_12 + pax_child_under_5
        rooms_needed = math.ceil((pax_adult + (pax_child_5_12 * 0.5)) / 2)
        seasonal_multiplier = 1.20 if is_peak else 1.0
        cost_hotel = rooms_needed * hotel_price_per_night * nights * seasonal_multiplier
        cost_car = (TRANSPORT_RATES.get(destination, 1100000) * days * seasonal_multiplier) if inc_car else 0
        cost_guide = (GUIDE_RATE * days * seasonal_multiplier) if inc_guide else 0
        cost_meal = (effective_pax_services * MEAL_RATES.get(star_rating, 200000) * 2 * days * seasonal_multiplier) if inc_meal else 0
        flight_cost_per_person = FLIGHT_RATES.get(airline_choice, {}).get(flight_class, 0) if inc_flight else 0
        cost_flight_total = flight_cost_per_person * (pax_adult + pax_child_5_12)
        total_cost_net = cost_hotel + cost_car + cost_guide + cost_meal + cost_flight_total
        selling_price = total_cost_net / 0.8
        st.markdown(f"""
        <div class="booking-card">
            <h3 style="color: #15803D; margin:0;">TỔNG CHI PHÍ TRỌN GÓI</h3>
            <h1 style="color: #16A34A; margin: 10px 0;">{selling_price:,.0f} VNĐ</h1>
            <p style="font-size: 15px; color: #1E3A8A; margin:0;"><b>Khởi hành:</b> {travel_month} ({'Cao điểm' if is_peak else 'Thấp điểm'})</p>
            <p style="font-size: 14px; color: #4B5563; margin-top:5px;"><b>Cơ cấu:</b> {pax_adult} Người lớn | {pax_child_5_12} Trẻ em (5-12t) | {pax_child_under_5} Trẻ em (<5t)</p>
        </div>
        """, unsafe_allow_html=True)
        st.write("")
        st.markdown("**Bóc tách hạng mục chi phí đã bao gồm:**")
        st.write(f"- 🛏️ **Khách sạn:** {rooms_needed} phòng {room_type} ({selected_hotel_name}) x {nights} đêm.")
        if inc_flight:
            st.write(f"- ✈️ **Vé máy bay:** {airline_choice} - Hạng {flight_class}.")
        st.write(f"- 🚗 **Di chuyển:** Xe đưa đón riêng tại {destination} ({days} ngày).")
        st.write(f"- 👨‍💼 **Phục vụ:** Hướng dẫn viên suốt tuyến ({days} ngày).")
        st.write(f"- 🍽️ **Ẩm thực:** {days*2} bữa ăn chính theo tiêu chuẩn {star_rating}.")
        st.divider()
        st.subheader("📝 Xác Nhận Đặt Tour")
        with st.form("customer_booking_form"):
            cust_name = st.text_input("Họ và Tên người đặt*", placeholder="Nhập họ tên...")
            cust_phone = st.text_input("Số điện thoại liên hệ*", placeholder="Nhập SĐT...")
            cust_note = st.text_area("Ghi chú thêm (Nếu có)", placeholder="Ví dụ: Yêu cầu phòng tầng cao, có xe đẩy trẻ em...")
            btn_submit = st.form_submit_button("🚀 ĐẶT TOUR NGAY")
            if btn_submit:
                if not cust_name or not cust_phone:
                    st.error("Vui lòng nhập đầy đủ Họ tên và Số điện thoại!")
                else:
                    pax_str = f"{pax_adult} NL"
                    if pax_child_5_12 > 0: pax_str += f", {pax_child_5_12} TE(5-12t)"
                    if pax_child_under_5 > 0: pax_str += f", {pax_child_under_5} TE(<5t)"
                    flight_str = f"{airline_choice} ({flight_class})" if inc_flight else "Không vé bay"
                    new_booking = {
                        "Mã Đơn": f"BK-{1001 + len(df_bookings)}",
                        "Tên Khách": cust_name,
                        "SĐT": cust_phone,
                        "Điểm đến": destination,
                        "Số Khách": pax_str,
                        "Thời gian đi": f"{travel_month} ({'Cao điểm' if is_peak else 'Thấp điểm'})",
                        "Ngày/Đêm": f"{days}N{nights}Đ",
                        "Khách sạn": f"{selected_hotel_name} ({star_rating} {room_type})",
                        "Bay": flight_str,
                        "Tổng Tiền": selling_price,
                        "Trạng thái": "Chờ Giám đốc duyệt",
                        "Ngày đặt": str(date.today())
                    }
                    add_booking(new_booking)
                    st.balloons()
                    st.success("🎉 Đặt tour thành công! Đã lưu vào CSDL Aiven. Đội ngũ Điều hành sẽ liên hệ xác nhận trong vòng 15 phút.")

# ------------------------------------------
# CHẾ ĐỘ 2: CHATBOT TƯ VẤN LỊCH TRÌNH
# ------------------------------------------
elif "CHATBOT" in app_mode:
    st.markdown('<div class="main-title">💬 CHATBOT HỎI ĐÁP & TƯ VẤN LỊCH TRÌNH DU LỊCH</div>', unsafe_allow_html=True)
    st.caption("Trợ lý AI sẵn sàng giải đáp thắc mắc về địa điểm, lịch trình chi tiết và chi phí dự kiến 24/7.")
    st.write("💡 **Gợi ý câu hỏi nhanh:**")
    quick_cols = st.columns(4)
    quick_q = None
    if quick_cols[0].button("📍 Lịch trình Sapa"):
        quick_q = "Gợi ý lịch trình tour Sapa"
    if quick_cols[1].button("🏖️ Lịch trình Phú Quốc"):
        quick_q = "Cho tôi lịch trình đi Phú Quốc"
    if quick_cols[2].button("🌉 Lịch trình Đà Nẵng"):
        quick_q = "Tư vấn tour Đà Nẵng"
    if quick_cols[3].button("🌲 Lịch trình Đà Lạt"):
        quick_q = "Lịch trình đi Đà Lạt thế nào?"
    st.divider()
    for message in st.session_state.chat_history:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])
    user_input = st.chat_input("Nhập thắc mắc của bạn về lịch trình tour tại đây...")
    prompt = user_input or quick_q
    if prompt:
        st.session_state.chat_history.append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.markdown(prompt)
        prompt_lower = prompt.lower()
        response = ""
        found_destination = False
        for loc_key, itinerary in ITINERARY_DATABASE.items():
            if loc_key in prompt_lower:
                response = f"Dưới đây là gợi ý lịch trình chi tiết cho chuyến đi **{loc_key.upper()}** của bạn:\n" + itinerary
                response += "\n\n👉 Bạn có thể chuyển sang tab **'CỔNG ĐẶT TOUR'** ở thanh bên trái để chọn tháng đi, độ tuổi trẻ em, hãng máy bay và nhận báo giá trọn gói tự động nhé!"
                found_destination = True
                break
        if not found_destination:
            if "trẻ em" in prompt_lower or "tuổi" in prompt_lower or "giá trẻ em" in prompt_lower:
                response = """
👶 **Chính sách giá tour theo độ tuổi tại Viet Travel:**
- **Dưới 5 tuổi:** Miễn phí 100% giá dịch vụ tour.
- **Từ 5 đến dưới 12 tuổi:** Tính 50% giá dịch vụ tour.
- **Từ 12 tuổi trở lên:** Tính như người lớn (100% giá).
                """
            elif "mùa" in prompt_lower or "cao điểm" in prompt_lower or "tháng" in prompt_lower:
                response = """
📅 **Chính sách Mùa vụ Du lịch:**
- **Mùa cao điểm (Tháng 6, 7, 8 và Tháng 12, 1):** Phụ thu 20% do dịch vụ vé tham quan, phòng ở và di chuyển tăng cao.
- **Mùa thấp điểm (Các tháng còn lại):** Áp dụng nguyên giá chuẩn, nhiều ưu đãi đi kèm.
                """
            elif "giá" in prompt_lower or "chi phí" in prompt_lower or "tiền" in prompt_lower:
                response = """
💰 **Thông tin chi phí Tour:**
- Giá tour được tự động tính toán dựa trên: **Tháng đi (Mùa vụ)**, **Cơ cấu độ tuổi (Người lớn/Trẻ em)**, **Loại vé máy bay/hãng bay** và **Hạng khách sạn (3-5 sao)**.
- Bạn vui lòng vào tab **'CỔNG ĐẶT TOUR'** chọn các tùy chọn để xem bảng giá chính xác nhất!
                """
            elif "khách sạn" in prompt_lower or "phòng" in prompt_lower:
                response = "🏨 Viet Travel hợp tác với hơn 30+ hệ thống khách sạn/resort hàng đầu Việt Nam như Vinpearl, InterContinental, Novotel, Silk Path, FLC... từ 3 sao đến 5 sao VIP."
            elif "xin chào" in prompt_lower or "chào" in prompt_lower or "hi" in prompt_lower:
                response = "Xin chào bạn! Tôi có thể giúp gì cho chuyến du lịch sắp tới của bạn? Bạn muốn tham khảo lịch trình Sapa, Phú Quốc, Đà Nẵng, Đà Lạt hay địa điểm nào khác?"
            else:
                response = f"""
Cảm ơn bạn đã đặt câu hỏi: *"{prompt}"*.
Dưới đây là một số địa điểm nổi tiếng Viet Travel có sẵn lịch trình chi tiết:
- 🏔️ **Sapa** (3N2Đ - Cáp treo Fansipan, Bản Cát Cát)
- 🏖️ **Phú Quốc** (4N3Đ - Tour 4 Đảo, VinWonders, Safari)
- 🌉 **Đà Nẵng** (3N2Đ - Bà Nà Hills, Hội An)
- 🌲 **Đà Lạt** (3N2Đ - Quảng trường Lâm Viên, Langbiang)
- 🚢 **Hạ Long** (2N1Đ - Du thuyền Vịnh Hạ Long)
- 🏖️ **Nha Trang** (3N2Đ - VinWonders, Tour Đảo)
Bạn hãy nhập tên địa điểm muốn đi để tôi gửi lịch trình gợi ý nhé!
                """
        with st.chat_message("assistant"):
            st.markdown(response)
        st.session_state.chat_history.append({"role": "assistant", "content": response})

# ------------------------------------------
# CHẾ ĐỘ 3: QUẢN TRỊ CEO (CÓ XÁC THỰC MẬT KHẨU)
# ------------------------------------------
else:
    if not st.session_state.admin_authenticated:
        st.markdown('<div class="main-title">🔒 DÀNH CHO QUẢN TRỊ VIÊN (CEO / MANAGEMENT)</div>', unsafe_allow_html=True)
        c_p1, c_p2, c_p3 = st.columns([1, 2, 1])
        with c_p2:
            st.info("👋 Bạn đang truy cập vào khu vực bảo mật. Vui lòng nhập mật khẩu Quản trị để tiếp tục.")
            with st.form("admin_login_form"):
                input_pass = st.text_input("🔑 Mật khẩu Admin", type="password", placeholder="Nhập mật khẩu quản trị...")
                btn_login = st.form_submit_button("🔓 Đăng nhập Hệ thống")
                if btn_login:
                    if input_pass == ADMIN_PASSWORD:
                        st.session_state.admin_authenticated = True
                        st.success("✅ Đăng nhập thành công! Đang tải dữ liệu...")
                        st.rerun()
                    else:
                        st.error("❌ Mật khẩu không chính xác! Vui lòng thử lại.")
    else:
        if ceo_menu == "📊 Dashboard Điều hành CEO":
            st.markdown('<div class="main-title">👔 EXECUTIVE DASHBOARD - BÁO CÁO BÀN GIÁO QUẢN TRỊ</div>', unsafe_allow_html=True)
            total_custom_rev = df_bookings[df_bookings["Trạng thái"] != "Hủy đơn"]["Tổng Tiền"].sum()
            total_tour_rev = df_tours["Doanh thu"].sum()
            grand_total_rev = total_custom_rev + total_tour_rev
            pending_orders = len(df_bookings[df_bookings["Trạng thái"] == "Chờ Giám đốc duyệt"])
            k1, k2, k3, k4 = st.columns(4)
            k1.metric("TỔNG DOANH THU TOÀN CÔNG TY", f"{grand_total_rev:,.0f} VNĐ", delta="+22.4% Tăng trưởng")
            k2.metric("Doanh thu Tour Khách Tự Thiết Kế", f"{total_custom_rev:,.0f} VNĐ", delta=f"{len(df_bookings)} Đơn hàng")
            k3.metric("Doanh thu Tour Ghép Định Kỳ", f"{total_tour_rev:,.0f} VNĐ", delta=f"{len(df_tours)} Tour đang chạy")
            k4.metric("ĐƠN ĐẶT TOUR CHỜ DUYỆT", f"{pending_orders} Đơn", delta="Cần xử lý ngay" if pending_orders > 0 else "Đã xong", delta_color="inverse")
            st.divider()
            c1, c2 = st.columns(2)
            with c1:
                st.subheader("📈 Doanh thu theo Điểm đến (Tour Thiết Kế)")
                chart_data_dest = df_bookings.groupby("Điểm đến")["Tổng Tiền"].sum()
                st.bar_chart(chart_data_dest)
            with c2:
                st.subheader("📊 So sánh Doanh thu vs Chi phí các Tour")
                chart_data_tour = df_tours.set_index("ID")[["Doanh thu", "Chi phí"]]
                st.bar_chart(chart_data_tour)

        elif ceo_menu == "📥 Tiếp nhận & Duyệt Đơn đặt":
            st.markdown('<div class="main-title">📥 QUẢN LÝ & DUYỆT YÊU CẦU ĐẶT TOUR TỪ KHÁCH HÀNG</div>', unsafe_allow_html=True)
            for idx, row in df_bookings.iterrows():
                with st.expander(f"📌 Mã đơn: **{row['Mã Đơn']}** | Khách: **{row['Tên Khách']}** ({row['SĐT']}) - **{row['Điểm đến']}** - **{row['Trạng thái']}**"):
                    col1, col2 = st.columns(2)
                    with col1:
                        st.write(f"- **Điểm đến:** {row['Điểm đến']}")
                        st.write(f"- **Thời gian khởi hành:** {row.get('Thời gian đi', 'N/A')}")
                        st.write(f"- **Số lượng khách:** {row['Số Khách']}")
                        st.write(f"- **Lịch trình:** {row['Ngày/Đêm']}")
                        st.write(f"- **Khách sạn yêu cầu:** {row['Khách sạn']}")
                        st.write(f"- **Chuyến bay:** {row.get('Bay', 'Không vé bay')}")
                    with col2:
                        st.write(f"- **Tổng giá trị đơn:** {row['Tổng Tiền']:,.0f} VNĐ")
                        st.write(f"- **Ngày đặt:** {row['Ngày đặt']}")
                        status_list = ["Chờ Giám đốc duyệt", "Đã chốt & Cọc", "Đã hoàn thành", "Hủy đơn"]
                        current_idx = status_list.index(row["Trạng thái"]) if row["Trạng thái"] in status_list else 0
                        new_status = st.selectbox(
                            "Cập nhật Trạng thái đơn:",
                            status_list,
                            key=f"status_{idx}",
                            index=current_idx
                        )
                        if new_status != row["Trạng thái"]:
                            update_booking_status(row['Mã Đơn'], new_status)
                            st.success(f"Đã cập nhật trạng thái đơn {row['Mã Đơn']} thành '{new_status}' trong database!")
                            st.rerun()

        elif ceo_menu == "👨‍💼 Quản lý Nhân sự & HDV":
            st.markdown('<div class="main-title">👨‍💼 QUẢN LÝ DANH SÁCH NHÂN SỰ & HƯỚNG DẪN VIÊN</div>', unsafe_allow_html=True)
            c_hdv1, c_hdv2, c_hdv3, c_hdv4 = st.columns(4)
            c_hdv1.metric("TỔNG NHÂN SỰ / HDV", f"{len(df_staff)} Người")
            c_hdv2.metric("HDV Quốc tế", f"{len(df_staff[df_staff['Chức danh'] == 'HDV Quốc tế'])} HDV")
            c_hdv3.metric("HDV Sẵn Sàng Đi Tour", f"{len(df_staff[df_staff['Trạng thái'] == 'Sẵn sàng nhận tour'])} HDV")
            c_hdv4.metric("HDV Đang Bận / Đi Tour", f"{len(df_staff[df_staff['Trạng thái'].str.contains('Đang đi tour')])} HDV")
            st.divider()
            
            flt_col1, flt_col2, flt_col3 = st.columns(3)
            with flt_col1:
                role_filter = st.multiselect("Lọc theo Chức danh", options=df_staff["Chức danh"].unique(), default=df_staff["Chức danh"].unique())
            with flt_col2:
                status_filter = st.multiselect("Lọc theo Trạng thái", options=df_staff["Trạng thái"].unique(), default=df_staff["Trạng thái"].unique())
            with flt_col3:
                lang_search = st.text_input("🔍 Tìm theo Ngôn ngữ (VD: Anh, Trung, Nhật...)", value="")
            filtered_staff = df_staff[
                (df_staff["Chức danh"].isin(role_filter)) & 
                (df_staff["Trạng thái"].isin(status_filter))
            ]
            if lang_search:
                filtered_staff = filtered_staff[filtered_staff["Ngôn ngữ"].str.contains(lang_search, case=False, na=False)]
            st.subheader("📋 Bảng Danh Sách & Lịch Trực Hướng Dẫn Viên")
            st.dataframe(
                filtered_staff[[
                    "Mã NV", "Họ và Tên", "Mã số thẻ HDV", "Loại thẻ", "Ngôn ngữ", 
                    "Chức danh", "SĐT", "Trạng thái", "Lịch trực / Phân công", "Tuyến đường chính", "Kinh nghiệm"
                ]], 
                use_container_width=True, 
                hide_index=True
            )
            st.divider()
            st.subheader("➕ Thêm Nhân Sự / Hướng Dẫn Viên Mới")
            with st.form("add_staff_form"):
                s1, s2, s3 = st.columns(3)
                with s1:
                    st_name = st.text_input("Họ và Tên*")
                    st_dob = st.text_input("Ngày sinh (DD/MM/YYYY)", placeholder="15/08/1995")
                    st_cccd = st.text_input("Số CCCD/CMND", placeholder="001095XXXXXX")
                    st_phone = st.text_input("Số điện thoại*")
                with s2:
                    st_role = st.selectbox("Chức danh*", ["HDV Quốc tế", "HDV Nội địa", "Chuyên viên Điều hành Tour", "NV Kinh doanh"])
                    st_card_type = st.selectbox("Loại thẻ HDV", ["Quốc tế", "Nội địa", "Không"])
                    st_card_no = st.text_input("Mã số thẻ HDV", placeholder="Ví dụ: 101180234")
                    st_lang = st.text_input("Ngôn ngữ thành thạo*", value="Tiếng Anh")
                with s3:
                    st_routes = st.text_input("Tuyến đường chính / Khu vực", placeholder="Ví dụ: Phú Quốc, Nha Trang")
                    st_exp = st.text_input("Kinh nghiệm", placeholder="Ví dụ: 5 năm")
                    st_status = st.selectbox("Trạng thái", ["Sẵn sàng nhận tour", "Đang đi tour", "Đang làm việc", "Nghỉ phép"])
                    st_schedule = st.text_input("Lịch trực / Phân công", placeholder="Ví dụ: Trực văn phòng T2-T4")
                btn_add_staff = st.form_submit_button("💾 Lưu Nhân Sự Mới")
                if btn_add_staff:
                    if not st_name or not st_phone:
                        st.error("Vui lòng điền đầy đủ Họ tên và Số điện thoại!")
                    else:
                        new_id_num = len(df_staff) + 1
                        new_staff = {
                            "Mã NV": f"HDV-{new_id_num:02d}" if "HDV" in st_role else f"NV-{new_id_num:02d}",
                            "Họ và Tên": st_name,
                            "Ngày sinh": st_dob if st_dob else "N/A",
                            "CCCD": st_cccd if st_cccd else "N/A",
                            "Chức danh": st_role,
                            "SĐT": st_phone,
                            "Loại thẻ": st_card_type,
                            "Mã số thẻ HDV": st_card_no if st_card_no else "Không",
                            "Ngôn ngữ": st_lang,
                            "Tuyến đường chính": st_routes if st_routes else "Chưa phân công",
                            "Kinh nghiệm": st_exp if st_exp else "Dưới 1 năm",
                            "Trạng thái": st_status,
                            "Lịch trực / Phân công": st_schedule if st_schedule else "Chưa xếp lịch"
                        }
                        add_staff_db(new_staff)
                        st.success(f"🎉 Đã thêm thành công HDV/Nhân viên **{st_name}** vào Database!")
                        st.rerun()

        elif ceo_menu == "🏨 Quản lý Khách sạn Partner":
            st.markdown('<div class="main-title">🏨 QUẢN LÝ DANH SÁCH KHÁCH SẠN ĐỐI TÁC</div>', unsafe_allow_html=True)
            st.dataframe(df_hotels, use_container_width=True, hide_index=True)

        elif ceo_menu == "🗺️ Quản lý Tour & Vận hành":
            st.markdown('<div class="main-title">🗺️ QUẢN LÝ TOUR ĐỊNH KỲ & VẬN HÀNH</div>', unsafe_allow_html=True)
            st.dataframe(df_tours, use_container_width=True, hide_index=True)

        elif ceo_menu == "💰 Báo cáo Tài chính":
            st.markdown('<div class="main-title">💰 BÁO CÁO TÀI CHÍNH & TỔNG QUAN DOANH THU</div>', unsafe_allow_html=True)
            st.write("### 1. Chi tiết doanh thu đặt tour tự thiết kế")
            st.dataframe(df_bookings[["Mã Đơn", "Tên Khách", "Điểm đến", "Tổng Tiền", "Trạng thái", "Ngày đặt"]], use_container_width=True, hide_index=True)
            st.write("### 2. Chi tiết doanh thu & chi phí tour ghép")
            st.dataframe(df_tours[["ID", "Tên Tour", "Số chỗ", "Đã đặt", "Doanh thu", "Chi phí"]], use_container_width=True, hide_index=True)
