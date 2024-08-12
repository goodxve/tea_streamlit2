"""
个人信息
"""
import streamlit as st
from sql_data_base import  execute_mysql
from login_config import login_out
from PIL import Image
import os
import time

# 获取当前文件路径
SPATH = os.path.dirname( os.path.abspath( __file__ ) )


def my_info():
    """
    直接大的用户信息函数 没有可拆分
    :return: None
    """
    st.write('---')
    # 获取个人信息
    user_info_session = st.session_state['student_info']
    # 读取图片路径
    image_path = os.path.join( SPATH ,'data' ,user_info_session[ 'student_id' ]+'.jpg' )
    # 个人信息卡
    show_info_card(image_path, user_info_session)

    # 修改密码
    with st.expander("下拉修改密码"):
        new_password_0 = st.text_input(label='输入密码', value=user_info_session['password'], type="password")
        new_password_1 = st.text_input(label='再次确认密码', type="password")
        make_ture = st.button('确定修改')

        if make_ture and new_password_0 == new_password_1:
            student_id = user_info_session['student_id']
            sql_password = f"UPDATE grades_info.user_info SET password = '{new_password_0}' WHERE student_id = '{student_id}';"
            execute_mysql(sql_password)
            st.success('修改成功')
            login_out()
            time.sleep(0.5)
            st.experimental_rerun ()
        elif make_ture and new_password_0 != new_password_1:
            st.error("再次密码不正确")

    st.write ( '---' )
    # 上传照片
    uploaded_file = st.file_uploader ( "上传头像" ,type = [ "jpg"] )
    if uploaded_file is not None:
        student_id = user_info_session [ 'student_id' ]
        # 将上传的文件读取为PIL图像对象
        image = Image.open ( uploaded_file )
        # 重命名图片并保存到本地文件系统
        save_path = os.path.join ( SPATH ,'data')
        image_path = os.path.join ( save_path ,f"{student_id}.jpg" )
        # 保存图像
        image.save ( image_path )
        st.success('上传成功')
    st.write ( '---' )


def show_info_card(image_path, user_info):
    """
    用户信息卡
    :param image_path: 用户照片路径
    :param user_info: 用户信息
    :return: None
    """
    col1, col2 = st.columns([2, 5])
    with col1:
        if os.path.exists(image_path):
            st.image(Image.open(image_path),
                     caption=user_info['name'],
                     width = 160,
                     )
        else:
            st.image( image=Image.open( os.path.join( SPATH ,'data' ,'no_data.jpg' ) ) ,
                      caption=user_info['name'] ,
                      width = 160 ,
                      )
    with col2:
        st.header('ID：' + user_info['student_id'])
        st.subheader("姓名：" + user_info['name'])
        st.subheader("班级：" + user_info['class_name'])
