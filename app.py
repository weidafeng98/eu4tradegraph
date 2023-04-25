# -*- coding: utf-8 -*-

import streamlit as st
import colorsys
from io import BytesIO
from PIL import Image, ImageDraw
import os
import re
import graphviz
import pydot

class Trade_center:
    def __init__(self, name, current, outgoing, local_value):
            self.name = name.title()
            self.current = current
            self.outgoing = outgoing
            self.local_value = local_value

class Trade_transfer:
    def __init__(self, start, final, value):
        self.start = start
        self.final = final
        self.value = value

def generate_plot(save_path, aspect_ratio, line_width_min, line_width_max, node_size_min, node_size_max, font_size_min, font_size_max, h1, s1, v1, h2, s2, v2):
    trade_center_path = "trade_center.txt"

    def cal_width(value, transfer_list):
        min_width = line_width_min
        max_width = line_width_max
        value_list = list()
        for transfer in transfer_list:
            value_list.append(transfer.value)
        return (value - min(value_list)) / (max(value_list) - min(value_list)) * (max_width - min_width) + min_width

    def cal_node_color(value, node_list):
        value_list = list()
        for node in node_list:
            value_list.append(node.local_value)
        min_value = min(value_list)
        max_value = max(value_list)
        norm_value = (value - min_value) / (max_value - min_value)

        return str(norm_value*(h2-h1)+h1)+" "+str(norm_value*(s2-s1)+s1)+" "+str(norm_value*(v2-v1)+v1)

    def cal_node_size(value, node_list):
        min_size = node_size_min
        max_size = node_size_max

        value_list = list()
        for node in node_list:
            value_list.append(node.current)

        return (value - min(value_list)) / (max(value_list) - min(value_list)) * (max_size - min_size) + min_size

    def cal_font_size(value, node_list):
        min_size = font_size_min
        max_size = font_size_max

        value_list = list()
        for node in node_list:
            value_list.append(node.current)

        return (value - min(value_list)) / (max(value_list) - min(value_list)) * (max_size - min_size) + min_size

    Trade_center_info = {}

    with open(trade_center_path, "rt", encoding="GB2312") as txt:
        s = txt.readlines()

    for sub_s in s:
        Trade_center_info[sub_s.split()[0]] = [sub_s.split()[1], sub_s.split()[2]]

    s = save_path

    Trade_center_list = list()
    Trade_transfer_list = list()

    matches = re.compile(r'(node={[\s\S]*?\n\t})').findall(s)

    for match in matches:
        definitions = re.search(r'definitions="(.+?)"', match)
        if definitions:
            definitions = definitions.group(1)
        else:
            definitions = "null"

        current = re.search(r'current=(\d+\.?\d*)', match)
        if current:
            current = eval(current.group(1))
        else:
            current = 0.0 

        outgoing = re.search(r'outgoing=(\d+\.?\d*)', match)
        if outgoing:
            outgoing = eval(outgoing.group(1))
        else:
            outgoing = 0.0 

        local_value = re.search(r'local_value=(\d+\.?\d*)', match)
        if local_value:
            local_value = eval(local_value.group(1))
        else:
            local_value = 0.0 

        Trade_center_list.append(Trade_center(definitions, current, outgoing, local_value))

        transfer_matches = re.compile(r'(incoming={[\s\S]*?\n\t\t})').findall(match)
        
        for transfer_match in transfer_matches:
            value = re.search(r'value=(\d+\.?\d*)', transfer_match)
            if value:
                value = eval(value.group(1))
            else:
                value = 0.0 

            start = re.search(r'from=(\d+\.?\d*)', transfer_match)
            if start:
                start = eval(start.group(1)) - 1
            else:
                start = 0
            
            final = len(Trade_center_list) - 1
            
            Trade_transfer_list.append(Trade_transfer(start, final, value))


    G = pydot.Dot(graph_type="digraph")
    G.set_charset("utf-8")
    G.set("fontname", "Noto Sans CJK JP")
    
    G.set_ratio(str(aspect_ratio))

    for i in range(len(Trade_center_list)):
        if Trade_center_info[Trade_center_list[i].name][1] == "1":
            new_node = pydot.Node(
                Trade_center_info[Trade_center_list[i].name][0],shape = "box", fontname = "bold", style = "filled", fillcolor = cal_node_color(Trade_center_list[i].local_value, Trade_center_list), penwidth = "4", width = str(cal_node_size(Trade_center_list[i].current, Trade_center_list)), height = str(0.618*cal_node_size(Trade_center_list[i].current, Trade_center_list)), fontsize = str(cal_font_size(Trade_center_list[i].current, Trade_center_list))
            )
        else:
            new_node = pydot.Node(
                Trade_center_info[Trade_center_list[i].name][0], fontname = "bold", style = "filled", fillcolor = cal_node_color(Trade_center_list[i].local_value, Trade_center_list), penwidth = "4", width = str(cal_node_size(Trade_center_list[i].current, Trade_center_list)), height = str(0.618*cal_node_size(Trade_center_list[i].current, Trade_center_list)), fontsize = str(cal_font_size(Trade_center_list[i].current, Trade_center_list))
            )
        
        G.add_node(new_node)
    for edge in Trade_transfer_list:
        if edge.value == 0:
            new_edge = pydot.Edge(
                Trade_center_info[Trade_center_list[edge.start].name][0], Trade_center_info[Trade_center_list[edge.final].name][0], style = "dashed", penwidth = str(cal_width(edge.value, Trade_transfer_list))
            )
        else:
            new_edge = pydot.Edge(
                Trade_center_info[Trade_center_list[edge.start].name][0], Trade_center_info[Trade_center_list[edge.final].name][0], penwidth = str(cal_width(edge.value, Trade_transfer_list))
            )
        G.add_edge(new_edge)

    G_graph = graphviz.Source(G.to_string())

    filename="graph"
    format="png"
    # Save the rendered graph as a PNG image file
    G_graph.render(filename=filename, format=format)

    filepath = os.path.join(os.getcwd(), filename + "." + format)
    image = Image.open(filepath)

    return image


def gradient(start_color, end_color, width, height):
    img = Image.new('RGB', (width, height))
    draw = ImageDraw.Draw(img)
    h1, s1, v1 = start_color
    h2, s2, v2 = end_color
    for y in range(height):
        h = h1 + (h2 - h1) * y / (height - 1)
        s = s1 + (s2 - s1) * y / (height - 1)
        v = v1 + (v2 - v1) * y / (height - 1)
        r, g, b = colorsys.hsv_to_rgb(h, s, v)
        draw.line((0, y, width - 1, y), fill=(int(r * 255), int(g * 255), int(b * 255)))
    return img.rotate(90, expand=True)  # 旋转图像


# Streamlit 应用程序的主体部分
def main():
    st.set_option('deprecation.showPyplotGlobalUse', False)
    st.title('欧陆风云4贸易路线图生成器V0.1.1')

    st.text("本应用目前还在测试中，仅对1.34版本无mod的存档进行过测试，不保证应用稳定性。")
    st.text("若发现任何问题或有任何建议，请联系本人：weidafeng98@126.com")

    session_state = st.session_state

    if "data" not in session_state:
        session_state.data = None

    # 默认设定
    aspect_ratio = 2.16
    line_width_min, line_width_max = 4, 20
    node_size_min, node_size_max = 1.0, 6.0
    font_size_min, font_size_max = 24, 72
    h1, s1, v1 = 0.0, 0.5, 1.0
    h2, s2, v2 = 2/3, 0.5, 1.0

    uploaded_file = st.file_uploader("请上传欧陆风云4的非压缩存档文件", type='eu4')

    if uploaded_file is not None:
        try:
            session_state.data = uploaded_file.read().decode("MacRoman")
        except:
            session_state.data = uploaded_file.read().decode("cp1252")
    if st.button("使用示例文件"):
        script_dir = os.path.dirname(os.path.abspath(__file__))
        sample_file_path = os.path.join(script_dir, "original.eu4")
        with open(sample_file_path, 'rt', encoding='cp1252') as file:
            session_state.data = file.read()

    if session_state.data is not None:
        with st.form(key="my_form"):
            aspect_ratio = st.slider("图片长宽比（默认为2.16）", 1.0, 3.0, value = 2.16)
            line_width_min, line_width_max = st.slider("线条宽度范围（表示该线路贸易流量，默认为4 - 20）", min_value=1, max_value=48, value=(4, 20))
            node_size_min, node_size_max = st.slider("节点大小范围（表示从该节点提取的贸易总额，默认为1.00 - 6.00）", min_value=1.0, max_value=12.0, value=(1.0, 6.0))
            font_size_min, font_size_max = st.slider("字体大小范围（默认为24-72）", min_value=12, max_value=144, value=(24, 72))
            h1 = st.slider("节点颜色范围起始值（表示该节点的本地贸易产出），H（色相，默认为0.00）", min_value=0.0, max_value=1.0, value=0.0)
            s1 = st.slider("节点颜色范围起始值（表示该节点的本地贸易产出），H（饱和度，默认为0.50）", min_value=0.0, max_value=1.0, value=0.5)
            v1 = st.slider("节点颜色范围起始值（表示该节点的本地贸易产出），H（明度，默认为1.00）", min_value=0.0, max_value=1.0, value=1.0)
            h2 = st.slider("节点颜色范围终止值（表示该节点的本地贸易产出），H（色相，默认为0.67）", min_value=0.0, max_value=1.0, value=2/3) 
            s2 = st.slider("节点颜色范围终止值（表示该节点的本地贸易产出），H（饱和度，默认为0.50）", min_value=0.0, max_value=1.0, value=0.5) 
            v2 = st.slider("节点颜色范围终止值（表示该节点的本地贸易产出），H（明度，默认为1.00）", min_value=0.0, max_value=1.0, value=1.0)
            submit_button = st.form_submit_button(label="获取图片")
            
        if submit_button:
            start_color = (h1, s1, v1)
            end_color = (h2, s2, v2)
            width = 5
            height = 100
            gradient_img = gradient(start_color, end_color, width, height)

            image = generate_plot(session_state.data, aspect_ratio, line_width_min, line_width_max, node_size_min, node_size_max, font_size_min, font_size_max, h1, s1, v1, h2, s2, v2)
            st.image(image, caption='贸易路线图', use_column_width=True)
            st.image(gradient_img, caption='节点的本地贸易产出图例', use_column_width=True)

            
# 运行 Streamlit 应用程序
if __name__ == '__main__':
    main()

