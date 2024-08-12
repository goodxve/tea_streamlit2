import streamlit as st
import sqlitDate as sql


# 初始化 session_state
def init_login():
    if 'user_info' not in st.session_state:
        st.session_state['user_info'] = None

# 数据库连接和操作函数

# 主函数
def log():
    empty = st.empty()  # 创建一个占位符
    with empty.container():
        if st.session_state['user_info'] is None:
            st.title("用户登录系统")

            menu = ["登录", "注册"]
            choice = st.selectbox("选择功能", menu)

            conn = sql.get_connection()

            if choice == "登录":
                st.subheader("登录")

                with st.form("login_form"):
                    username = st.text_input("用户名")
                    password = st.text_input("密码", type="password")
                    submitted = st.form_submit_button("登录")

                    if submitted:
                        user = sql.login_user(conn, username, password)
                        if user:
                            st.success(f"登录成功，欢迎回来，{user[1]}！")
                            user_info = sql.get_info(user[1], conn)
                            st.session_state['user_info'] = user
                            empty.empty()  # 清空界面
                            return True
                        else:
                            st.error("用户名或密码错误")
                            return False

            elif choice == "注册":
                st.subheader("注册")

                with st.form("register_form"):
                    new_username = st.text_input("用户名")
                    new_password = st.text_input("密码", type="password")
                    confirm_password = st.text_input("确认密码", type="password")
                    perm = st.selectbox("权限", [0, 1, 2])
                    submitted = st.form_submit_button("注册")

                    if submitted:
                        if new_password == confirm_password:
                            if sql.register_user(conn, new_username, new_password, perm):
                                st.success("注册成功！")
                            else:
                                st.error("用户名已存在，请选择其他用户名")
                        else:
                            st.warning("密码不匹配，请重新输入")

            conn.close()

