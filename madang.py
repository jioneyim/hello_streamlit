import duckdb
import streamlit as st 
import pandas as pd
import time
import duckdb
import os 

conn = duckdb.connect(database='madang.db')
conn.sql("drop table if exists Customer")
conn.sql("drop table if exists Book")
conn.sql("drop table if exists Orders")
conn.sql("create table Customer as select * from 'Customer_madang.csv'")
conn.sql("create table Book as select * from 'Book_madang.csv'")
conn.sql("create table Orders as select * from 'Orders_madang.csv'")
conn.close()

import duckdb
conn = duckdb.connect(database='madang.db')
name = st.text_input("고객명", key='name')
custid = st.text_input("고객번호", key='id')
address = st.text_input("주소", key='add')
phone = st.text_input("전화번호", key='pn')
if st.button('고객 정보 저장', key='insert_btn'):
    if name and custid and address and phone:
            custid = int(custid)
            phone = int(phone)
            
          
            sql_query = f"INSERT INTO Customer (custid, name, address, phone) VALUES ({custid}, '{name}', '{address}', {phone});"
            
            conn.sql(sql_query)
            st.success(f"고객 '{name}' (ID: {custid}) 정보가 성공적으로 추가되었습니다.")
insert_name = st.text_input("고객명", key = 'inserted')
if insert_name is not None:
    sql_query = f"SELECT * FROM Customer WHERE name LIKE '%{insert_name}%'"
    result_df = conn.sql(sql_query).fetchdf()
    if not result_df.empty:
        st.subheader(f"'{insert_name}' 검색 결과")
        st.dataframe(result_df)
    else:
        st.info(f"고객명 '{insert_name}'에 해당하는 고객이 없습니다.")   
