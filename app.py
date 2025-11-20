import streamlit as st
import duckdb
import time

DB_NAME = "madang.db"

# DB 연결
def connect():
    return duckdb.connect(DB_NAME)


# SQL 실행 함수
def query(sql, return_type="relation"):
    conn = connect()
    result = conn.sql(sql)
    conn.close()

    if return_type == "relation":
        return result
    elif return_type == "df":
        return result.df()
    elif return_type == "scalar":
        return result.fetchone()[0]


# ------------------------------------
# Streamlit UI 시작
# ------------------------------------
st.title("📚 마당 DB (DuckDB 버전)")

tab1, tab2 = st.tabs(["고객조회", "거래 입력"])

# ===========================
# 1) 고객 조회
# ===========================
name = tab1.text_input("고객명")

custid = None

if name:
    sql = f"""
        SELECT c.custid, c.name, b.bookname, o.orderdate, o.saleprice
        FROM Customer c
        JOIN Orders o ON c.custid = o.custid
        JOIN Book b ON b.bookid = o.bookid
        WHERE c.name = '{name}';
    """

    result = query(sql, "df")
    tab1.dataframe(result)

    if not result.empty:
        custid = int(result.iloc[0]["custid"])
        tab2.write(f"📌 고객번호: {custid}")
        tab2.write(f"📌 고객명: {name}")

# ===========================
# 2) 거래 입력
# ===========================
if custid:

    # 책 목록 불러오기
    books_df = query("SELECT bookid, bookname FROM Book", "df")
    books = [f"{row.bookid}, {row.bookname}" for idx, row in books_df.iterrows()]

    select_book = tab2.selectbox("구매 서적", books)

    bookid = int(select_book.split(",")[0]) if select_book else None
    price = tab2.text_input("금액 입력")

    if tab2.button("거래 입력"):

        # 새로운 주문번호 생성
        max_id = query("SELECT MAX(orderid) FROM Orders", "scalar")
        new_orderid = (max_id or 0) + 1

        today = time.strftime("%Y-%m-%d")

        insert_sql = f"""
            INSERT INTO Orders (orderid, custid, bookid, saleprice, orderdate)
            VALUES ({new_orderid}, {custid}, {bookid}, {price}, '{today}');
        """

        try:
            conn = connect()
            conn.sql(insert_sql)
            conn.close()
            tab2.success("거래가 입력되었습니다.")
        except Exception as e:
            tab2.error(f"오류 발생: {e}")
