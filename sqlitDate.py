import streamlit as st
import sqlite3
from datetime import datetime
import pandas as pd

def get_connection():
    return sqlite3.connect('Date/test.db')

def create_user_table(conn):
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS users
                 (id INTEGER PRIMARY KEY, name TEXT, password TEXT, perm INTEGER)''')
    conn.commit()

def create_idresult_table(conn):
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS idresult
                 (id INTEGER PRIMARY KEY, ruqi date NOT NULL, labe TEXT NOT NULL, num INTEGER)''')
    conn.commit()

def get_data(date):
    conn = sqlite3.connect('Date/test.db')
    query = f"SELECT * FROM idresult WHERE ruqi = '{date}'"
    df = pd.read_sql_query(query, conn)
    conn.close()
    return df

def add_user(conn, name, password, perm):
    c = conn.cursor()
    c.execute("INSERT INTO users (name, password, perm) VALUES (?, ?, ?)", (name, password, perm))
    conn.commit()

def add_idresult(conn, labe, count):
    c = conn.cursor()
    date = datetime.now().strftime('%Y-%m-%d')
    c.execute('''
            INSERT INTO idresult (ruqi, labe, num) VALUES (?, ?, ?)
        ''', (date, labe, count))
    conn.commit()

def login_user(conn, name, password):
    c = conn.cursor()
    c.execute("SELECT * FROM users WHERE name=? AND password=?", (name, password))
    return c.fetchone()

def register_user(conn, name, password, perm):
    c = conn.cursor()
    c.execute("SELECT * FROM users WHERE name=?", (name,))
    if c.fetchone() is None:
        add_user(conn, name, password, perm)
        return True
    else:
        return False

def login_out():
    """
    修改 authenticator.logout ('注销',location = 'sidebar') 退出登录选项
    :return: True表示成功退出，否则返回错误消息
    """
    try:
        # 重置 session 状态
        st.session_state [ 'user_info' ] = None
        # # 刷新页面
        # st.experimental_rerun ()

        return True

    except KeyError as e:
        return f"缺少配置: {e}"
    except Exception as e:
        return f"退出登录时出错: {e}"

def get_info(name, conn):
    c = conn.cursor()
    user_info = c.execute("SELECT * FROM users WHERE name=? ", (name,))
    return user_info

def get_all_users(conn):
    c = conn.cursor()
    c.execute("SELECT * FROM users")
    users = c.fetchall()
    return users

def delete_user(conn, user_id):
    c = conn.cursor()
    c.execute("DELETE FROM users WHERE id=?", (user_id,))
    conn.commit()




# 清空idresult表中的所有数据
def clear_all_data(conn):
    c = conn.cursor()
    c.execute("DELETE FROM idresult")
    conn.commit()
    conn.close()
    st.success("所有数据已被清空。")

# 获取指定日期的数据
def get_data_2(date,conn):

    query = "SELECT * FROM idresult WHERE ruqi = ?"
    df = pd.read_sql_query(query, conn, params=(date,))
    conn.close()
    return df

# 删除指定日期的数据
def delete_data(date,conn):

    c = conn.cursor()
    c.execute("DELETE FROM idresult WHERE ruqi = ?", (date,))
    conn.commit()
    conn.close()
    st.success(f"日期 {date} 的数据已被清除。")