import streamlit as st
import duckdb
import pandas as pd
import time

DB_NAME = "madang.db"

# ===========================================================
# 1) DB 초기화 (앱 최초 1번만 실행)
# ===========================================================
if "db_initialized" not in st.session_state:
    conn = duckdb.connect(DB_NAME)

    conn.sql("DROP TABLE IF EXISTS Customer")
    conn.sql("DROP TABLE IF EXISTS Book")
    conn.sql("DROP TABLE IF EXISTS Orders")

    conn.sql("CREATE TABLE Customer AS SELECT * FROM 'Customer_madang.csv'")
    conn.sql("CREATE TABLE Book AS SELECT * FROM 'Book_madang.csv'")
    conn.sql("CREATE TABLE Orders AS SELECT * FROM 'Orders_madang.csv'")


    st.session_state.db_initialized = True


# ===========================================================
# 2) DB 연결 (전역 하나만 유지)
# ===========================================================
conn = duckdb.connect(DB_NAME)


# ===========================================================
# 3) SQL 실행 함수
# ===========================================================
def query(sql, return_type="relation"):
    result = conn.sql(sql)
    if return_type == "df":
        return result.df()
    elif return_type == "scalar":
        return result.fetchone()[0]
    return result


# ===========================================================
# Streamlit UI
# ===========================================================
st.title("📚 마당 DB (DuckDB 버전)")

tab1, tab2, tab3 = st.tabs(["고객조회", "거래 입력", "신규 고객 등록"])


# ===========================================================
# 1) 고객 조회
# ===========================================================
with tab1:
    st.subheader("고객 주문 내역 조회")

    search_name = st.text_input("고객명 입력")

    if search_name:
        sql = f"""
            SELECT c.custid, c.name, b.bookname, o.orderdate, o.saleprice
            FROM Customer c
            LEFT JOIN Orders o ON c.custid = o.custid
            LEFT JOIN Book b ON b.bookid = o.bookid
            WHERE c.name LIKE '%{search_name}%'
        """
        df = query(sql, "df")
        st.dataframe(df)

        if not df.empty:
            st.session_state.selected_custid = int(df.iloc[0]["custid"])
            st.success(f"선택된 고객번호: {st.session_state.selected_custid}")


# ===========================================================
# 2) 거래 입력
# ===========================================================
with tab2:
    st.subheader("고객 거래 입력")

    if "selected_custid" not in st.session_state:
        st.info("먼저 '고객조회' 탭에서 고객을 선택하세요.")
    else:
        custid = st.session_state.selected_custid
        st.write(f"📌 선택된 고객번호: **{custid}**")

        # 책 목록 불러오기
        books_df = query("SELECT bookid, bookname FROM Book", "df")
        book_list = [
            f"{row.bookid}, {row.bookname}" for idx, row in books_df.iterrows()
        ]
        selected_book = st.selectbox("구매 서적 선택", book_list)

        bookid = int(selected_book.split(",")[0])
        price = st.text_input("금액 입력")

        if st.button("거래 입력"):

            # 숫자 체크
            if not price.isdigit():
                st.error("금액은 숫자로 입력하세요.")
            else:
                max_order = query("SELECT COALESCE(MAX(orderid),0) FROM Orders", "scalar")
                new_orderid = max_order + 1
                today = time.strftime("%Y-%m-%d")

                insert_sql = f"""
                    INSERT INTO Orders (orderid, custid, bookid, saleprice, orderdate)
                    VALUES ({new_orderid}, {custid}, {bookid}, {price}, '{today}')
                """

                try:
                    conn.sql(insert_sql)
                    st.success("거래가 성공적으로 입력되었습니다.")
                except Exception as e:
                    st.error(f"오류 발생: {e}")


# ===========================================================
# 3) 신규 고객 등록
# ===========================================================
with tab3:
    st.subheader("신규 고객 등록")

    new_name = st.text_input("이름")
    new_addr = st.text_input("주소")
    new_phone = st.text_input("전화번호 (숫자만)")

    if st.button("고객 등록"):

        # phone 숫자 검증
        if not new_phone.isdigit():
            st.error("전화번호는 숫자만 입력하세요.")
        else:
            max_cust = query("SELECT COALESCE(MAX(custid), 0) FROM Customer", "scalar")
            new_custid = max_cust + 1

            insert_sql = f"""
                INSERT INTO Customer (custid, name, address, phone)
                VALUES ({new_custid}, '{new_name}', '{new_addr}', {new_phone});
            """

            try:
                conn.sql(insert_sql)
                st.success(f"신규 고객 등록 완료! (custid: {new_custid})")
            except Exception as e:
                st.error(f"오류 발생: {e}")    

