"""
Knowledge base gia lap cho VinTech Support Agent (RAG demo).
Moi document la mot chunk doc lap, co ID rieng de tinh Hit Rate / MRR.
"""

DOCUMENTS = [
    {
        "id": "doc_001",
        "title": "Doi mat khau",
        "text": (
            "Doi mat khau: De doi mat khau, vao Settings > Security > Change Password. "
            "Mat khau moi phai co it nhat 8 ky tu, bao gom chu hoa, chu thuong va so. "
            "Lien ket doi mat khau qua email se het han sau 15 phut. "
            "Nguoi dung khong the dung lai 5 mat khau gan nhat."
        ),
    },
    {
        "id": "doc_002",
        "title": "Chinh sach hoan tien",
        "text": (
            "Chinh sach hoan tien: Khach hang co the yeu cau hoan tien trong vong 30 ngay "
            "ke tu ngay mua hang, voi dieu kien san pham chua duoc su dung qua 10% dung luong "
            "hoac thoi gian dung thu. Hoan tien duoc xu ly trong 5-7 ngay lam viec qua phuong "
            "thuc thanh toan ban dau. Cac goi subscription theo nam khong duoc hoan tien sau 14 ngay."
        ),
    },
    {
        "id": "doc_003",
        "title": "Chinh sach van chuyen",
        "text": (
            "Van chuyen: Don hang noi thanh giao trong 1-2 ngay, ngoai thanh 3-5 ngay lam viec. "
            "Phi van chuyen mien phi cho don hang tren 500.000 VND. "
            "Khach hang co the theo doi don hang qua ma tracking gui trong email xac nhan."
        ),
    },
    {
        "id": "doc_004",
        "title": "Bao mat tai khoan",
        "text": (
            "Bao mat tai khoan: Khuyen nghi nguoi dung kich hoat xac thuc 2 yeu to (2FA) qua "
            "Google Authenticator hoac SMS. Neu phat hien dang nhap bat thuong, he thong se tu "
            "dong khoa tai khoan va gui email canh bao. Nguoi dung tuyet doi khong chia se OTP "
            "cho bat ky ai, ke ca nhan vien ho tro."
        ),
    },
    {
        "id": "doc_005",
        "title": "Goi subscription",
        "text": (
            "Goi dich vu: Co 3 goi - Basic (mien phi, gioi han 10 request/ngay), Pro (199k/thang, "
            "khong gioi han request, ho tro uu tien), va Enterprise (lien he sales, SLA 99.9%). "
            "Nguoi dung co the nang cap hoac ha cap goi bat ky luc nao, phan chenh lech duoc tinh "
            "theo ty le ngay con lai trong ky."
        ),
    },
    {
        "id": "doc_006",
        "title": "Ho tro ky thuat",
        "text": (
            "Ho tro ky thuat: Kenh ho tro hoat dong 24/7 qua chat va email trong gio hanh chinh "
            "(8h-18h, T2-T6). Thoi gian phan hoi trung binh la 2 gio cho goi Pro va 24 gio cho "
            "goi Basic. Cac van de khan cap (mat du lieu, bao mat) duoc uu tien xu ly trong 30 phut."
        ),
    },
    {
        "id": "doc_007",
        "title": "Xoa tai khoan",
        "text": (
            "Xoa tai khoan: Nguoi dung co the yeu cau xoa vinh vien tai khoan qua Settings > "
            "Account > Delete Account. Du lieu se duoc giu trong 30 ngay truoc khi xoa hoan toan "
            "(grace period) de phong truong hop nguoi dung doi y. Sau 30 ngay, du lieu khong the "
            "khoi phuc duoc."
        ),
    },
    {
        "id": "doc_008",
        "title": "Dieu khoan su dung API",
        "text": (
            "API Rate Limit: Goi Basic gioi han 10 request/ngay, Pro khong gioi han nhung ap dung "
            "rate limit 60 request/phut de chong abuse. Vuot rate limit se nhan ma loi HTTP 429. "
            "API key phai duoc giu bi mat, khong duoc nhung (hardcode) vao code phia client."
        ),
    },
]


def get_document_by_id(doc_id: str):
    for doc in DOCUMENTS:
        if doc["id"] == doc_id:
            return doc
    return None
