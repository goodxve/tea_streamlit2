import streamlit as st
from streamlit_option_menu import option_menu
# """自己写的函数分割线"""
import log_info
from sqlitDate import login_out
from analysis import photo_show,video_show,camera,dateAnaly,AIcommunicate,manage,encyclopedia,manage_date
import os

os.environ["KMP_DUPLICATE_LIB_OK"]="TRUE"



# 设置页面配置
st.set_page_config(
    page_title="茶叶虫害检测",   # 设置页面标题
    page_icon="function/Date/photo/icon/茶叶.png",  # 设置图标，可以是相对路径或URL
    layout="wide",  # 布局设置：'centered' 或 'wide'
    initial_sidebar_state="auto"  # 初始侧边栏状态：'auto', 'expanded' 或 'collapsed'
)



log_info.init_login()
login_code = log_info.log()

if st.session_state['user_info']:
    if st.session_state['user_info'][3] == 0:
        options = ["病虫害百科", '图片检测', '视频检测', '摄像头实时检测', '数据分析', 'AI助手', '退出登录']
        icons = ['📖', '🖼️', '🎥', '📷', '📊', '🤖', '🚪']
    else:
        options = ["病虫害百科", '图片检测', '视频检测', '摄像头实时检测', '数据分析', 'AI助手', "用户", '数据管理', '退出登录']
        icons = ['📖', '🖼️', '🎥', '📷', '📊', '🤖', '👤', '🗂️', '🚪']

    # 在侧边栏创建一个带有图标的选项菜单
    menu = {name: icon for name, icon in zip(options, icons)}
    selected = st.sidebar.radio(
        f'{st.session_state["user_info"][1]} 你好',
        options=list(menu.keys()),
        format_func=lambda option: f"{menu[option]} {option}"
    )


    if selected == '病虫害百科':
        try:
            encyclopedia()
        except:
            pass
    elif selected == '图片检测':
        try:
            photo_show()
        except:
            pass
    elif selected == '视频检测':
        try:
            video_show()
        except:
            pass

    elif selected == '摄像头实时检测':
        try:
            camera()
        except:
            pass
    elif selected == '数据分析':
        try:
            dateAnaly()
        except:
            pass
    elif selected == 'AI助手':
        try:
            AIcommunicate()
        except:
            pass
    elif selected == '用户':
        try:
            manage()
        except:
            pass
    elif selected == '数据管理':
        try:
            manage_date()
        except:
            pass
    elif selected == '退出登录':
        login_out()
        st.rerun()