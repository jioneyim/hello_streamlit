import streamlit as st
import duckdb
import time

DB_NAME = "madang.db"

def connect():
    return duckdb.connect(DB_NAME, read_only=False)

# CSV → DuckDB 초기화 (앱 켜질 때 자동 실행)
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

# Relation → 리스트(dict 형태) 변환
def relation_to_table(rel):
    cols = rel.columns
    data = rel.to_pylist()
    return cols, data

# SQL 실행 함수
def run_query(sql):
    conn = connect()
    rel = conn.sql(sql)
    conn.close()
    return rel


# --------------------------------------------
# Streamlit App 시작
# --------------------------------------------
st.title("📚 마당 DB (DuckDB Cloud 버전)")

# CSV → DuckDB 자동 초기화
init_db()

tab1, tab2 = st.tabs(["고객 조회", "거래 입력"])

# -------------------------------
# 고객 조회
# -------------------------------
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

    rel = run_query(sql)
    cols, data = relation_to_table(rel)
    tab1.dataframe(data)

    if len(data) > 0:
        customer_id = data[0]["custid"]
        tab2.write(f"📌 고객번호: {customer_id}")
        tab2.write(f"📌 고객명: {name}")

# -------------------------------
# 거래 입력
# -------------------------------
if customer_id:

    rel = run_query("SELECT bookid, bookname FROM Book")
    _, book_data = relation_to_table(rel)

    books_list = [f"{row['bookid']}, {row['bookname']}" for row in book_data]

    selected_book = tab2.selectbox("구매 서적 선택", books_list)
    bookid = int(selected_book.split(",")[0])

    price = tab2.text_input("금액 입력")

    if tab2.button("거래 입력"):

        max_rel = run_query("SELECT MAX(orderid) AS maxid FROM Orders")
        _, max_data = relation_to_table(max_rel)
        max_orderid = max_data[0]["maxid"] or 0

        new_order_id = max_orderid + 1
        today = time.strftime('%Y-%m-%d')

        insert_sql = f"""
            INSERT INTO Orders (orderid, custid, bookid, saleprice, orderdate)
            VALUES ({new_order_id}, {customer_id}, {bookid}, {price}, '{today}');
        """

        conn = connect()
        conn.sql(insert_sql)
        conn.close()

        tab2.success("거래가 입력되었습니다.")
