import streamlit as st
import duckdb

# DB 연결
con = duckdb.connect("madang.duckdb")

st.title("📚 마당DB Streamlit 조회 시스템")

tab1, tab2, tab3 = st.tabs(["고객 조회", "책 조회", "주문 조회"])

# -------------------------
# 1) 고객 조회
# -------------------------
with tab1:
    st.header("고객 검색")
    name = st.text_input("고객명 입력")

    if name:
        sql = f"""
        SELECT c.custid, c.name, b.bookname, o.orderdate, o.saleprice
        FROM Customer c
        JOIN Orders o ON c.custid = o.custid
        JOIN Book b ON b.bookid = o.bookid
        WHERE c.name LIKE '%{name}%'
        ORDER BY o.orderdate DESC
        """
        df = con.execute(sql).df()
        st.dataframe(df)

# -------------------------
# 2) 책 조회
# -------------------------
with tab2:
    st.header("책 목록")
    df = con.execute("SELECT * FROM Book").df()
    st.dataframe(df)

# -------------------------
# 3) 주문 조회
# -------------------------
with tab3:
    st.header("주문 목록")
    df = con.execute("""
        SELECT o.orderid, c.name, b.bookname, o.orderdate, o.saleprice
        FROM Orders o
        JOIN Customer c ON c.custid = o.custid
        JOIN Book b ON b.bookid = o.bookid
        ORDER BY o.orderdate DESC
    """).df()
    st.dataframe(df)
