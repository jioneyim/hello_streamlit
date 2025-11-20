import streamlit as st
import duckdb
import time

DB_NAME = "madang.db"


def connect():
    return duckdb.connect(DB_NAME)


# CSV → DuckDB 초기화 (앱 시작 시 자동 실행됨)
def init_db():
    conn = connect()

    conn.sql("""
        CREATE OR REPLACE TABLE Customer AS
        SELECT * FROM read_csv_auto('Customer_madang.csv');
    """)

    conn.sql("""
        CREATE OR REPLACE TABLE Book AS
        SELECT * FROM read_csv_auto('Book_madang.csv');
    """)

    conn.sql("""
        CREATE OR REPLACE TABLE Orders AS
        SELECT * FROM read_csv_auto('Orders_madang.csv');
    """)

    conn.close()


# SQL 실행 함수
def run_query(sql, return_type="df"):
    conn = connect()
    result = conn.sql(sql)
    conn.close()

    if return_type == "df":
        return result.df()
    if return_type == "scalar":
        return result.fetchone()[0]
    return result


# ------------------------------------------------------
# Streamlit App
# ------------------------------------------------------
st.title("📚 마당 DB (DuckDB 버전)")

# ★★★ 앱 시작 시 DuckDB 초기화 ★★★
init_db()


tab1, tab2 = st.tabs(["고객 조회", "거래 입력"])


# --------------------------
# 고객 조회
# --------------------------
name = tab1.text_input("고객명 입력")
customer_id = None

if name:
    sql = f"""
        SELECT c.custid, c.name, b.bookname, o.orderdate, o.saleprice
        FROM Customer c
        JOIN Orders o ON c.custid = o.custid
        JOIN Book b ON b.bookid = o.bookid
        WHERE c.name = '{name}';
    """

    result_df = run_query(sql, "df")
    tab1.dataframe(result_df)

    if not result_df.empty:
        customer_id = int(result_df.iloc[0]["custid"])
        tab2.write(f"📌 고객번호: {customer_id}")
        tab2.write(f"📌 고객명: {name}")


# --------------------------
# 거래 입력
# --------------------------
if customer_id:

    books_df = run_query("SELECT bookid, bookname FROM Book", "df")
    books_list = [f"{row.bookid}, {row.bookname}" for _, row in books_df.iterrows()]

    selected_book = tab2.selectbox("구매 서적 선택", books_list)
    bookid = int(selected_book.split(",")[0])

    price = tab2.text_input("금액 입력")

    if tab2.button("거래 입력"):

        try:
            max_order_id = run_query("SELECT MAX(orderid) FROM Orders", "scalar")
            new_order_id = (max_order_id or 0) + 1

            today = time.strftime('%Y-%m-%d')

            insert_sql = f"""
                INSERT INTO Orders (orderid, custid, bookid, saleprice, orderdate)
                VALUES ({new_order_id}, {customer_id}, {bookid}, {price}, '{today}');
            """

            conn = connect()
            conn.sql(insert_sql)
            conn.close()

            tab2.success("거래가 입력되었습니다.")

        except Exception as e:
            tab2.error(f"오류: {e}")
