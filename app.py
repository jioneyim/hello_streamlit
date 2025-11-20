import streamlit as st
import duckdb
import pandas as pd
import time

# --- DuckDB 연결 ---
def get_conn():
    return duckdb.connect("madang.duckdb")

def query(sql):
    conn = get_conn()
    result = conn.execute(sql).fetchall()
    conn.close()
    return result

# ---------------------------------------
# 책 목록 불러오기 (너의 코드 방식 그대로)
# ---------------------------------------
books = [None]
result = query("SELECT bookid || ',' || bookname FROM Book")
for res in result:
    books.append(res[0])   # res는 튜플 → 첫 번째 값이 문자열

# ---------------------------------------
# UI
# ---------------------------------------
tab1, tab2 = st.tabs(["고객조회", "거래 입력"])

name = ""
custid = None
result_df = pd.DataFrame()

name = tab1.text_input("고객명")
select_book = ""

if len(name) > 0:
    sql = f"""
        SELECT c.custid, c.name, b.bookname, o.orderdate, o.saleprice
        FROM Customer c, Book b, Orders o
        WHERE c.custid = o.custid 
          AND o.bookid = b.bookid
          AND c.name = '{name}';
    """
    rows = query(sql)
    result_df = pd.DataFrame(rows, columns=["custid", "name", "bookname", "orderdate", "saleprice"])
    tab1.write(result_df)

    if not result_df.empty:
        custid = result_df['custid'][0]
        tab2.write("고객번호: " + str(custid))
        tab2.write("고객명: " + name)

        # ---------------------------------------
        # 책 선택 (네 코드 흐름 그대로)
        # ---------------------------------------
        select_book = tab2.selectbox("구매 서적:", books)

        if select_book is not None:
            bookid = select_book.split(",")[0]

            # 오늘 날짜
            dt = time.strftime('%Y-%m-%d')

            # orderid 자동 증가
            orderid = query("SELECT MAX(orderid) FROM Orders")[0][0]
            orderid = (orderid or 0) + 1

            price = tab2.text_input("금액")

            # INSERT SQL
            insert_sql = f"""
                INSERT INTO Orders (orderid, custid, bookid, saleprice, orderdate)
                VALUES ({orderid}, {custid}, {bookid}, {price}, '{dt}');
            """

            # ---------------------------------------
            # 거래 입력 버튼
            # ---------------------------------------
            if tab2.button("거래 입력"):
                conn = get_conn()
                conn.execute(insert_sql)
                conn.close()
                tab2.success("거래가 입력되었습니다.")
