import streamlit as st

def confidence():
    # 添加置信度阈值选项
    confidence_option = st.radio(
        "置信度选项",
        ("滑动条", "选择框")
    )

    if confidence_option == "滑动条":
        confidence = st.slider(
            "请滑动下边滑条选择置信度", 0.1, 1.0, 0.5)
    else:
        confidence = float(st.text_input(
            "请输入置信度： (0.1 - 1.0)", 0.5))
    return confidence





