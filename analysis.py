import streamlit as st

import detection_module as dm

import pandas as pd
import altair as alt
from openai import OpenAI

import cv2
import onnxtest as onnxtest
import numpy as np
import sqlitDate as sql

import tempfile

import os
import base64

from datetime import datetime


model_path = "best.onnx"
iou_thres = 0.5

def photo_show():

    conn = sql.get_connection()
    sql.create_idresult_table(conn)

    st.title("茶叶病虫害图片检测")
    col1, col2 = st.columns(2)
    with col1:
        conf = dm.confidence()

    # 模型设置

    confidence_thres = conf


    with col2:
        uploaded_file = st.file_uploader("选择一张照片", type=["jpg", "jpeg", "png"])

    if uploaded_file is not None:
        file_bytes = np.asarray(bytearray(uploaded_file.read()), dtype=np.uint8)
        img = cv2.imdecode(file_bytes, 1)
        with col1:
            st.image(img, caption="Uploaded Image", use_column_width=True)
            st.write("Running object detection...")

        # Initialize model
        yolo = onnxtest.YOLOv8(model_path, confidence_thres, iou_thres)

        if uploaded_file:
            if st.button("执行"):
                with st.spinner("运行中..."):

                    # Run detection
                    output_image,detected_classes ,class_counts = yolo.run_inference(img)
                    with col2:
                        # Display result
                        st.image(output_image, caption="Detected Objects", use_column_width=True)
                        st.write("检测到的目标类别：")
                        st.write(detected_classes)
                        st.write("不同目标类别的数量：")
                        st.write(class_counts)
                        for labe, count in class_counts.items():
                            sql.add_idresult(conn, labe, count)



def video_show():
    st.title("茶叶病虫害视频检测")

    conn = sql.get_connection()
    sql.create_idresult_table(conn)

    col1, col2 = st.columns(2)
    with col1:
        conf = dm.confidence()

    confidence_thres = conf
    # Initialize model
    yolo = onnxtest.YOLOv8(model_path, confidence_thres, iou_thres)

    with col2:
        source_video = st.file_uploader(
            label="选择一个视频...",
            type=("mp4", "avi", "mov", 'mkv', 'webm')
        )
    if source_video is not None:
        with col1:
            st.text("未检测视频")
            st.video(source_video)
            st.write("Running object detection...")

        if source_video:
            if st.button("执行"):
                with st.spinner("运行中..."):
                    with col2:
                        try:
                            tfile = tempfile.NamedTemporaryFile()
                            tfile.write(source_video.read())
                            vid_cap = cv2.VideoCapture(
                                tfile.name)

                            st_frame = st.empty()


                            while (vid_cap.isOpened()):
                                success, img = vid_cap.read()
                                if success:
                                    output_image, detected_classes, class_counts = yolo.run_inference(img)
                                    st_frame.image(output_image,
                                                   caption='检测后视频',
                                                   channels="BGR",
                                                   use_column_width=True
                                                   )
                                else:
                                    vid_cap.release()
                                    break
                        except Exception as e:
                            st.error(f"加载视频时出错: {e}")

                        # Display result


def camera():
    st.title("茶叶病虫害摄像头实时检测")
    conn = sql.get_connection()
    sql.create_idresult_table(conn)

    if 'running' not in st.session_state:
        st.session_state.running = None
    if 'screenshot' not in st.session_state:
        st.session_state.screenshot = None




    col1, col2, col3 = st.columns(3)
    with col1:
        conf = dm.confidence()
        confidence_thres = conf

    yolo = onnxtest.YOLOv8(model_path, confidence_thres, iou_thres)
    with col2:
        if st.button('开始运行'):
            st.session_state.running = True

        if st.button('停止运行'):
            st.session_state.running = False
        st.write()
    with col3:
        if st.button('截图并检测'):
            st.session_state.screenshot = True

    running = st.session_state.running

    try:
        if running:
            vid_cap = cv2.VideoCapture(0)  # 本地摄像头
            with col1:
                st_frame = st.empty()

            while running:
                success, img = vid_cap.read()
                if success:

                    with col1:
                        output_image, detected_classes, class_counts = yolo.run_inference(img)
                        st_frame.image(output_image,
                                     caption='检测后视频',
                                     channels="BGR",
                                     use_column_width=True
                                   )

                    # 仅在截图按钮被点击时执行一次截图和检测
                    if st.session_state.screenshot:
                        with col2:
                            st.image(img, caption='截图图像', channels="BGR", use_column_width=True)
                        output_image, detected_classes, class_counts = yolo.run_inference(img)
                        with col3:
                            st.image(output_image, caption='截图后的检测结果', channels="BGR", use_column_width=True)
                            st.write("检测到的目标类别：")
                            st.write(detected_classes)
                            st.write("不同目标类别的数量：")
                            st.write(class_counts)
                            for labe, count in class_counts.items():
                                sql.add_idresult(conn, labe, count)
                            st.session_state.screenshot = False  # 只截图一次

                else:
                    vid_cap.release()
                    break
    except Exception as e:
        st.error(f"加载视频出错: {str(e)}")




def dateAnaly():
   conn = sql.get_connection()
   # 将数据加载到DataFrame
   df = pd.read_sql_query("SELECT * FROM idresult", conn)

   # 关闭数据库连接
   conn.close()

   # 获取数据中所有的日期
   available_dates = df['ruqi'].unique()

   # Streamlit应用
   st.title("按日期统计并可视化数据")

   # 日期选择
   selected_date = st.date_input("选择日期", pd.to_datetime(available_dates[0]),
                                 min_value=pd.to_datetime(min(available_dates)),
                                 max_value=pd.to_datetime(max(available_dates)))

   # 将选中的日期转换为字符串格式
   selected_date_str = selected_date.strftime('%Y-%m-%d')

   # 检查选定日期是否有数据
   if selected_date_str in available_dates:
       # 根据选择的日期过滤数据
       filtered_data = df[df['ruqi'] == selected_date_str]

       # 按类别汇总num
       aggregated_data = filtered_data.groupby('labe')['num'].sum().reset_index()

       # 绘制柱状图
       chart = alt.Chart(aggregated_data).mark_bar().encode(
           x=alt.X('labe', sort=None, axis=alt.Axis(title='病虫害类型',labelAngle=0, labelFontSize= 24)),  # 这里设置标签角度为0度，即水平显示
           y=alt.Y('num', axis=alt.Axis(title='总数',labelAngle=0, labelFontSize= 20)),
           color='labe',
           tooltip=['labe', 'num']
       ).properties(
           title=f'{selected_date_str} 各类别num总数'
       )

       st.altair_chart(chart, use_container_width=True)
   else:
       st.write("所选日期没有数据，请选择其他日期。")


def AIcommunicate():

    st.title("💬 Chatbot")
    st.caption("🚀 A Streamlit chatbot powered by OpenAI")

    api_key = 'sk-fe78c4e1094f4814a75fcd974dd0ffca'
    if api_key is None:
        st.error("API key for OpenAI is not set. Please set the api_key environment variable.")
    else:
        # 创建 OpenAI 客户端
        client = OpenAI(api_key=api_key, base_url="https://api.deepseek.com")

        # 聊天记录初始化
        if 'messages' not in st.session_state:
            st.session_state['messages'] = [{"role": "assistant", "content": "怎么样才能帮到你"}]

        for msg in st.session_state['messages']:
            st.chat_message(msg["role"]).write(msg["content"])

        if user_input := st.chat_input("请输入内容"):
            with st.spinner("Generating response..."):
                try:
                    st.session_state['messages'].append({"role": "user", "content": user_input})
                    st.chat_message("user").write(user_input)
                    response = client.chat.completions.create(
                        model="deepseek-chat",
                        messages=[
                            {"role": "system", "content": "You are a helpful assistant that replies in Chinese"},
                            {"role": "user", "content": user_input},
                        ],
                        stream=False
                    )
                    answer = response.choices[0].message.content
                    # 更新聊天记录
                    st.session_state['messages'].append({"role": "assistant", "content": answer})
                    st.chat_message("assistant").write(answer)
                    st.rerun()  # 重新运行以清空输入框并更新聊天记录
                except Exception as e:
                    st.error(f"Error: {str(e)}")

def communicate():
    messages = st.container(border=None)
    if prompt := st.chat_input("输入内容"):
        messages.chat_message("你").write(prompt)
        messages.chat_message("user").write(f"Echo: {prompt}")



def manage():
    st.title("管理员用户管理系统")

    conn = sql.get_connection()
    sql.create_user_table(conn)  # 确保用户表存在

    st.header("所有注册用户")
    users = sql.get_all_users(conn)

    col1, col2 = st.columns(2)

    if users:
        # 显示所有用户信息
        for user in users:
            with col1:
                user_id, name, password, perm = user
                st.write(f"用户ID:  {user_id},  用户名:  {name},  权限: {perm}")

            with col2:
                # 删除用户的按钮
                if st.button(f"删除 {name}", key=user_id):
                    sql.delete_user(conn, user_id)
                    st.success(f"用户 {name} 已被删除")
                    st.experimental_rerun()

    else:
        st.write("没有找到用户信息")

    conn.close()

def list_html_files(folder_path):
    """列出文件夹中的所有HTML文件"""
    html_files = [f for f in os.listdir(folder_path) if f.endswith('.html')]
    return html_files


def read_html_file(file_path):
    """读取HTML文件内容"""
    with open(file_path, 'r', encoding='utf-8') as file:
        return file.read()


def embed_images_in_html(html_content, folder_path):
    """将图片嵌入HTML内容中"""
    import re
    # 查找HTML中的所有图片路径
    img_tags = re.findall(r'<img\s+[^>]*src="([^"]*)"', html_content)
    for img_tag in img_tags:
        img_path = os.path.join(folder_path, img_tag)
        if os.path.exists(img_path):
            # 读取图片文件并将其转换为Base64编码
            with open(img_path, 'rb') as img_file:
                img_base64 = base64.b64encode(img_file.read()).decode('utf-8')
                # 将Base64编码的图片插入HTML中
                html_content = html_content.replace(img_tag, f'data:image/png;base64,{img_base64}')
    return html_content

def encyclopedia():
    st.title('病虫害百科')

    # 用户输入文件夹路径
    folder_path = 'Date/html'

    if folder_path:
        if os.path.exists(folder_path):
            html_files = list_html_files(folder_path)
            if html_files:

                selected_file = st.selectbox('文件', html_files)

                if selected_file:
                    file_path = os.path.join(folder_path, selected_file)
                    html_content = read_html_file(file_path)
                    html_content = embed_images_in_html(html_content, folder_path)

                    # 使用st.components.v1.html显示HTML内容，并设置scrollbar
                    st.components.v1.html(html_content, height=800, scrolling=True)
            else:
                st.write('该文件夹中没有HTML文件。')
        else:
            st.write('文件夹路径无效。')







def manage_date():
    st.title("数据表操作")
    conn = sql.get_connection()
    sql.create_user_table(conn)

    # 状态管理
    if 'confirm_clear_all' not in st.session_state:
        st.session_state.confirm_clear_all = False
    if 'confirm_delete' not in st.session_state:
        st.session_state.confirm_delete = False

    # 清空所有数据按钮和警告
    if st.button("清空所有数据"):
        if not st.session_state.confirm_clear_all:
            st.session_state.confirm_clear_all = True
            st.warning("警告: 此操作将清空表idresult中的所有数据。请点击下面的确认按钮以继续。")
        else:
            sql.clear_all_data(conn)
            st.session_state.confirm_clear_all = False

    # 日期选择和数据显示
    selected_date = st.date_input("选择日期", min_value=datetime(2000, 1, 1), max_value=datetime.now())
    if st.button("显示选择日期的数据"):
        df = sql.get_data_2(selected_date.strftime('%Y-%m-%d'), conn)
        if df.empty:
            st.write("该日期没有数据。")
        else:
            st.write(df)

    # 删除选择日期的数据
    if st.button("删除选择日期的数据"):
        if not st.session_state.confirm_delete:
            st.session_state.confirm_delete = True
            st.warning("警告: 此操作将清除选择日期的数据。请点击下面的确认按钮以继续。")
        else:
            sql.delete_data(selected_date.strftime('%Y-%m-%d'), conn)
            st.session_state.confirm_delete = False
