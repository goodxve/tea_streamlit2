"""
登录验证
"""
import streamlit as st
from sql_data_base import inquire_mysql
import json


def get_info(username):
    """
    获取用户信息存入session_state的
    :param username: 用户ID
    :return: 返回对应的值
    """
    sql_query = f"SELECT * FROM grades_info.user_info WHERE student_id = '{username}';"
    if username is not '':
        try:
            user_info = json.loads ( inquire_mysql ( sql_query ) ) [ 0 ]
            return user_info
        except:
            st.warning('账号或者密码错误')
    else:
        return None


def init_login():
    """
    初始化session_state
    :return: None
    """
    if 'student_info' not in st.session_state:
        st.session_state [ 'student_info' ] = None



def login_in():
    """
    登录页面 直接用
    :return: 登录结果
    """
    empty = st.empty ()
    with empty:
        if st.session_state [ 'student_info' ] is None:
            with st.form ( "login_form" ):
                st.title ( '登录' )
                username = st.text_input ( "账号" )
                password = st.text_input ( "密码" ,type = "password" )
                submitted = st.form_submit_button ( "login" )

                try:
                    student_info = get_info(username)
                    class_id = student_info['class_id']
                    sql = f"SELECT * FROM grades_info.class_info WHERE class_id = '{class_id}'"
                    class_name = json.loads(inquire_mysql(sql))[0]['class_name']

                    real_password = student_info [ 'password' ]
                    student_info['class_name'] = class_name

                except:
                    pass

                if submitted is True and password == real_password:
                    st.session_state [ 'student_info' ] = student_info
                    empty.empty ()
                    return True
                elif submitted is True and password != real_password:
                    st.error ( "账号或密码错误" )
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



