import os
import tkinter as tk
from tkinter import ttk
from PIL import Image, ImageTk
import os
import time


class DraggableRectangle:
    def __init__(self, canvas, x1, y1, x2, y2, itemid, recipes, quantities_new, icon_path, lower_id=None):
        global recipe_spilt, selected_id
        item_id = itemid
        self.x = x1
        self.y = y1
        self.x_axis = f"{x1 / 1920}*方法.取屏幕宽度"
        self.y_axis = f"{y1 / 1080}*方法.取屏幕高度+界面变量.滚动值*12"
        self.lower_id = ["None"]
        self.lower_id_id = ["None"]
        self.quantities = []
        self.recipe_spilt = []
        self.recipe_nospilt = recipes
        self.itemname = itemname.get()
        self.iteminfo = iteminfo.get()
        self.lines = []  # 存储与此节点相关的连接线
        self.itemid = itemid
        self.nodeid = self
        self.canvas = canvas
        selected_id = self
        self.icon_path = icon_path
        ##print(self.quantities)
        # 处理 itemid 获取下划线后的部分，并设置图标路径
        self.icon_path = os.path.join(icon_path, itemid.split(":")[-1] + ".png") if itemid else None
        ##print(f"icon_path={self.icon_path}")
        self.recipe_spilt = split_by_comma(recipes)
        self.quantities = split_by_comma(quantities_new)
        self.quantities_nospilt = quantities_new
        ##print(f"recipe_spilt={self.recipe_spilt}")
        ##print(f"quantities={self.quantities}")
        # 创建组件背景
        self.image_tk = None
        if self.icon_path and os.path.exists(self.icon_path):
            self.image = Image.open(self.icon_path)
            self.image = self.image.resize((int(x2 - x1), int(y2 - y1)))  # 调整图标大小适应组件大小
            self.image_tk = ImageTk.PhotoImage(self.image)
            # 用图片作为背景
            self.image_item = canvas.create_image(x1, y1, image=self.image_tk, anchor="nw")

        # 创建一个透明矩形用于绑定事件
        self.rect = canvas.create_rectangle(x1, y1, x2, y2, outline="", fill="", tags="draggable")

        self.text = canvas.create_text((x1 + x2) // 2, (y1 + y2) // 2, text="")
        self.tag = canvas.create_text(x1 - 20, (y1 + y2) // 2, text="", anchor="e")

        # 创建按钮
        self.button = tk.Button(canvas, text="连接节点", width=6, height=1, command=self.select_node)
        self.button_window = canvas.create_window((x1 + x2) // 2, y1 - 8, window=self.button)

        # 绑定拖动事件到透明的矩形
        self.canvas.tag_bind(self.rect, "<ButtonPress-1>", self.on_press)
        self.canvas.tag_bind(self.rect, "<B1-Motion>", self.on_drag)
        self.canvas.tag_bind(self.text, "<ButtonPress-1>", self.on_press)
        self.canvas.tag_bind(self.text, "<B1-Motion>", self.on_drag)
        self.canvas.tag_bind(self.rect, "<ButtonPress-1>", self.on_press)
        self.canvas.tag_bind(self.text, "<ButtonPress-1>", self.on_press)
        self.canvas.tag_bind(self.rect, "<Double-Button-1>", self.show_parameters)
        self.canvas.tag_bind(self.text, "<Double-Button-1>", self.show_parameters)
        self.selected = False

    def on_press(self, event):
        self.x = self.x
        self.y = self.y

    def on_drag(self, event):
        global selected_id, selected_coord, border
        prex = self.x
        prey = self.y
        for i in range(0, 1920, 64):
            if abs(event.x - i) < 32 and i % 64 == 0:
                self.x = i
                break
        for i in range(0, 1920, 64):
            if abs(event.y - i) < 32 and i % 64 == 0:
                self.y = i
                break
        # 移动背景图片
        dx = prex - self.x
        dy = prey - self.y
        if self.image_tk:
            self.canvas.coords(self.image_item, self.x, self.y)
        # 移动透明矩形和其他组件
        self.canvas.coords(self.rect, self.x, self.y, self.x+64, self.y+64)
        self.canvas.coords(self.text, self.x, self.y)
        self.canvas.coords(self.button_window, self.x, self.y)
        self.canvas.coords(self.tag, self.x, self.y)
        self.selected = True
        # 更新连接线位置
        if self.selected:
            for line in self.lines:
                line.update_position()
        if selected_coord != selected_id.canvas.coords(selected_id.rect):
            canvas.delete(border)
            border = canvas.create_rectangle(self.canvas.coords(self.rect)[0] - 2, self.canvas.coords(self.rect)[1] - 2,
                                             self.canvas.coords(self.rect)[0] + 64,
                                             self.canvas.coords(self.rect)[1] + 64, outline="red", width=2)
            selected_coord = self.canvas.coords(self.rect)

    def select_node(self):
        global selected_nodes, connect_info, connect_num
        if len(selected_nodes) < 2:
            selected_nodes.append(self)

            connect_info[connect_num][0] = selected_nodes[0]
            if len(selected_nodes) == 2 and selected_nodes[0] != selected_nodes[1]:
                connect_info[connect_num][1] = selected_nodes[1]
                # print(f"connect_num={connect_num}")
                # print(f"selected_nodes={selected_nodes}")
                # print(f"cinfo0={connect_info[connect_num][0]}")
                # print(f"cinfo1={connect_info[connect_num][1]}")
                self.set_lower_id()
                # print(f"lower:{self.lower_id}")
                create_line()
            if len(selected_nodes) == 2 and selected_nodes[0] == selected_nodes[1]:
                selected_nodes = []

    def set_position(self, new_x, new_y):
        dx = new_x - self.x
        dy = new_y - self.y
        if self.image_tk:
            self.canvas.move(self.image_item, dx, dy)
        self.canvas.move(self.rect, dx, dy)
        self.canvas.move(self.text, dx, dy)
        self.canvas.move(self.button_window, dx, dy)
        self.canvas.move(self.tag, dx, dy)
        self.x = new_x
        self.y = new_y

    def move_node_to_new_position(self):
        global selected_nodes, connect_info, connect_num
        selected_nodes[1].set_position(100, 100)  # 修改节点的位置

    def set_lower_id(self):  # store lower permission only
        global selected_nodes
        if selected_nodes[0].lower_id[0] == "None":
            del selected_nodes[0].lower_id[0]
            del selected_nodes[0].lower_id_id[0]
        selected_nodes[0].lower_id.append(selected_nodes[1].itemid)
        selected_nodes[0].lower_id_id.append(selected_nodes[1])
        # print(f"{selected_nodes[0].itemid}'s lower itemid={selected_nodes[0].lower_id}")
        # selected_nodes[1].move_node_to_new_position()

    def show_parameters(self, event=None):
        """在输入框中显示当前节点的参数"""
        global selected_id, border, selected_coord
        selected_id = self
        Item_ID_var.set(selected_id.itemid)
        recipe_new.set(",".join(selected_id.recipe_spilt))
        quantities_var.set(",".join(selected_id.quantities))
        itemname.set("".join(selected_id.itemname))
        iteminfo.set("".join(selected_id.iteminfo))
        canvas.delete(border)
        border = canvas.create_rectangle(self.canvas.coords(self.rect)[0] - 2, self.canvas.coords(self.rect)[1] - 2,
                                         self.canvas.coords(self.rect)[0] + 64, self.canvas.coords(self.rect)[1] + 64,
                                         outline="red", width=2)
        selected_coord = self.canvas.coords(self.rect)
        info_text = (f"-----调试信息-----\n"
                     f"node id    = {self}\n"
                     f"x              = {self.x_axis}\n"
                     f"x_ori              = {self.x}\n"
                     f"y              = {self.y_axis}\n"
                     f"y_ori              = {self.y}\n"
                     f"itemid       = {self.itemid}\n"
                     f"recipes     = {self.recipe_spilt}\n"
                     f"quantities = {self.quantities}\n"
                     f"lower_id   = {self.lower_id}\n"
                     f"itemname   = {self.itemname}\n"
                     f"iteminfo   = {self.iteminfo}\n")
        info_label.config(text=info_text)

    def update_parameters(self):
        """更新节点参数"""
        self.itemid = Item_ID_var.get().strip()
        self.recipe_spilt = split_by_comma(recipe_new.get().strip())
        self.quantities = split_by_comma(quantities_var.get().strip())
        # 更新画布上的显示
        self.canvas.itemconfig(self.tag, text=self.itemid)
        self.canvas.itemconfig(self.text, text="")

    def delete_node(self):
        """删除节点并解绑连接线"""
        global lines
        # 解绑所有与该节点相关的连接线
        for line in self.lines[:]:
            line.delete_line()  # 删除连接线对象
        # 从全局线列表中移除这些线
        lines = [line for line in lines if line not in self.lines]
        # 清空与此节点相关的线
        self.lines.clear()
        # 删除节点和相关的图形对象
        self.canvas.delete(self.rect)
        self.canvas.delete(self.text)
        self.canvas.delete(self.button_window)
        self.canvas.delete(self.tag)
        if self.image_tk:
            self.canvas.delete(self.image_item)
        # 从全局节点列表中移除
        canvas.delete(border)


class ConnectionLine:
    def __init__(self, canvas, rect1, rect2):
        self.canvas = canvas
        self.rect1 = rect1
        self.rect2 = rect2
        self.line = canvas.create_line(self.get_center(self.rect1), self.get_center(self.rect2), fill="white", width=3)

        # 将连接线对象添加到相关节点的线列表中
        rect1.lines.append(self)
        rect2.lines.append(self)

    def get_center(self, rect):
        # 检查节点是否存在，以避免删除后报错
        if self.canvas.coords(rect.rect):
            x1, y1, x2, y2 = self.canvas.coords(rect.rect)
            return (x1 + x2) // 2, (y1 + y2) // 2
        return None, None  # 如果节点不存在，返回空值

    def update_position(self):
        pos1 = self.get_center(self.rect1)
        pos2 = self.get_center(self.rect2)
        if pos1 and pos2:  # 确保节点存在
            self.canvas.coords(self.line, pos1, pos2)

    def delete_line(self):
        """删除连接线"""
        self.canvas.delete(self.line)
        # 从两个节点的 lines 列表中移除此连接线
        if self in self.rect1.lines:
            self.rect1.lines.remove(self)
        if self in self.rect2.lines:
            self.rect2.lines.remove(self)


def create_line():
    global selected_nodes, connect_num
    if len(selected_nodes) == 2:
        line = ConnectionLine(canvas, selected_nodes[0], selected_nodes[1])
        lines.append(line)
        selected_nodes = []  # 重置选择
        connect_num = 1 + connect_num


# 创建主界面
root = tk.Tk()
root.title("树形图设计者")
id = 0
# 定义输入字段
Item_ID_var = tk.StringVar()
tag = tk.StringVar()
quantities_var = tk.StringVar()
bgp = tk.StringVar(value=r'F:\0美术素材\craftscection.png')
icons = tk.StringVar(value=r"F:\0客户端\.minecraft\resourcepacks\DragonCore\icon")
y_var = tk.StringVar()
level_var = tk.IntVar()
recipe_var = tk.StringVar()
recipe_items_var = tk.StringVar()
required_quantities_var = tk.StringVar()
permission_nodes = tk.StringVar()
itemname = tk.StringVar(value="暂无")
iteminfo = tk.StringVar(value="暂无")
recipe_new = tk.StringVar()
recipe_num_val = []
recipe_num_var = []
nodes_list = []
node_total = 0
nodes = []
nodes_shift = []
intstr_product = []
intstr_recipe = []
intvar_quantities = []
product = []
recipe = []
recipe_spilt = []
quantities = []
quantities_separate = []
node_rect = [i for i in range(100)]
node_text = [i for i in range(100)]
selected_nodes = []
connect_info = [[None for _ in range(2)] for _ in range(100)]
lines = []
alias_dict = {}
connect_num = 0
selected_id = ""
border = None  # 用于存储红框的引用
selected_coord = None
node_num = 0
item_id_import = []
x_import = []
y_import = []
unlockable_import = []
recipe_items_import = []
required_quantities_import = []
recipe_variables = [""]
node_total_import = 0
node_file = tk.StringVar(value="")
# 布局
window_width = 1920
window_height = 1080
canvas = tk.Canvas(root, width=window_width, height=window_height)
canvas.grid(row=0, column=0, rowspan=50, columnspan=50)  # 覆盖整个窗口
root.geometry(f"{window_width}x{window_height}")
tk.Label(root, text="物品 ID:").grid(row=0, column=0)
tk.Entry(root, textvariable=Item_ID_var).grid(row=0, column=1)

tk.Label(root, text="配方(多个配方用 , 分割):").grid(row=1, column=0)
tk.Entry(root, textvariable=recipe_new).grid(row=1, column=1)

tk.Label(root, text="物品中文名").grid(row=3, column=0)
tk.Entry(root, textvariable=itemname).grid(row=3, column=1)

tk.Label(root, text="物品描述").grid(row=4, column=0)
tk.Entry(root, textvariable=iteminfo).grid(row=4, column=1)

tk.Label(root, text="数量(多个数量用 , 分割，必须与配方数相符)").grid(row=2, column=0)
tk.Entry(root, textvariable=quantities_var).grid(row=2, column=1)

tk.Label(root, text="背景图路径:").grid(row=5, column=0)
tk.Entry(root, textvariable=bgp).grid(row=5, column=1)

tk.Label(root, text="物品图标路径:").grid(row=6, column=0)
tk.Entry(root, textvariable=icons).grid(row=6, column=1)


def process_node_data():
    # 定义全局变量
    global node_total_import, item_id_import, x_import, y_import, unlockable_import, recipe_items_import, required_quantities_import, node_total

    # 初始化变量
    item_id_import = []
    x_import = []
    y_import = []
    unlockable_import = []
    recipe_items_import = []
    required_quantities_import = []
    if os.path.exists(node_file.get().strip().replace("\"", "")):
        with open(node_file.get().strip().replace("\"", ""), 'r', encoding='utf-8') as file:
            lines1 = file.readlines()
            node_total_import = len(lines1)  # 总节点数
            print(node_total_import)
            for line in lines1:
                # 跳过空行
                if not line.strip():
                    continue
                if node_total != 0:
                    print("编辑器内存在节点，请清除之后再导入节点")
                    print(node_total)
                    break
                # 解析每个节点的字段
                # print(line)
                start = line.find("item_id=") + len("item_id=")
                end = line.find(";", start)
                # 提取 item_id= 和 ; 之间的内容
                item_id_import.append(line[start:end])
                start = line.find("x=") + len("x=")
                end = line.find(";", start)
                # 提取 item_id= 和 ; 之间的内容
                x_import.append(line[start:end])
                start = line.find("y=") + len("y=")
                end = line.find(";", start)
                # 提取 item_id= 和 ; 之间的内容
                y_import.append(line[start:end])
                start = line.find("unlockable=[") + len("unlockable=[")
                end = line.find("]", start)
                # 提取 item_id= 和 ; 之间的内容
                unlockable_import.append(line[start:end])
                start = line.find("recipe_items=") + len("recipe_items=")
                end = line.find(";", start)
                # 提取 item_id= 和 ; 之间的内容
                recipe_items_import.append(line[start:end])
                start = line.find("required_quantities=[") + len("required_quantities=[")
                end = line.find("]", start)
                # 提取 item_id= 和 ; 之间的内容
                required_quantities_import.append(line[start:end])
            for i in range(node_total_import):
                node = DraggableRectangle(canvas, float(x_import[i]), float(y_import[i]),
                                          float(x_import[i]) + 64, float(y_import[i]) + 64,
                                          item_id_import[i], recipe_items_import[i],
                                          required_quantities_import[i],
                                          icons.get().strip().replace("\"", ""))
                nodes_list.append(node)  # 将节点和别名存储在字典中

            node_total = node_total_import
        print(node_total)
        print(item_id_import)
        print(x_import)
        print(y_import)
        print(unlockable_import)
        print(recipe_items_import)
        print(required_quantities_import)


# 示例调用函数

delete_btn = ttk.Button(root, text="读取节点数据", command=process_node_data)
delete_btn.grid(row=11, column=0)
tk.Label(root, text="节点文件:").grid(row=7, column=0)
tk.Entry(root, textvariable=node_file).grid(row=7, column=1)


def split_by_comma(input_string):
    result_array = [item.strip() for item in input_string.split(",")]
    return result_array


def shift_left(arr):
    if len(arr) > 0:
        shifted_array = arr[1:] + [None]
        return shifted_array
    return arr


def node_paramater(alias, new_x, new_y):
    if alias in alias_dict:
        print("found alias")
        node = alias_dict[alias]  # 根据别名获取节点
        # node.set_position(new_x, new_y)  # 修改节点的位置
    else:
        print(f"No node found with alias '{alias}'")


def parachange():
    itemid = Item_ID_var.get().strip().replace("\"", "")
    new_x = 100
    new_y = 200
    node_paramater(itemid, new_x, new_y)


# 创建节点
def create_node():
    global node_total, node_total_import
    x = 200
    y = 600
    flag = 0
    node = DraggableRectangle(canvas, x, y, x + 64, y + 64, Item_ID_var.get().strip().replace("\"", ""),
                              recipe_new.get().strip().replace("\"", ""),
                              quantities_var.get().strip().replace("\"", ""),
                              icons.get().strip().replace("\"", ""))
    if node_total_import != 0 and flag == 0:
        flag = 1

        nodes_list.append(node)  # 将节点和别名存储在字典中
        node_total += 1
        print(nodes_list)
    if node_total_import == 0:
        nodes_list.append(node)
        node_total += 1
        print(nodes_list)
    # print(f"nodes_list={nodes_list[0]}")
    # print(f"node_total={node_total}")


def bgp_():
    global bgpimg

    # 加载并显示图片
    # print("11")
    try:
        # print("112")
        # 打开并调整图片大小
        bgpimg = Image.open(bgp.get().strip().replace("\"", "").replace("\"", ""))
        # 将图片转换为 Tkinter 兼容格式
        bgpimg = ImageTk.PhotoImage(bgpimg)

        # 将图片放在 Canvas 上作为背景
        canvas.create_image(474, 0, anchor="nw", image=bgpimg)

    except Exception as e:
        print(f"Error loading image: {e}")


def update_node():
    """删除选中的节点"""
    global selected_id, node_total, nodes_list
    print(node_total)
    print(nodes_list)
    for i in range(node_total):
        if nodes_list[i].nodeid == selected_id:
            nodes_list[i].itemid = Item_ID_var.get().strip().replace("\"", "")
            nodes_list[i].recipe_nospilt = recipe_new.get().strip().replace("\"", "")
            nodes_list[i].recipe_spilt = split_by_comma(recipe_new.get().strip().replace("\"", ""))
            nodes_list[i].quantities = split_by_comma(quantities_var.get().strip().replace("\"", ""))
            nodes_list[i].quantities_nospilt = quantities_var.get().strip().replace("\"", "")
            nodes_list[i].itemname = itemname.get()
            nodes_list[i].iteminfo = iteminfo.get()
            break


delete_btn = ttk.Button(root, text="更新节点", command=update_node)
delete_btn.grid(row=11, column=1)


def delete_node():
    """删除选中的节点"""
    global selected_id, node_total, nodes_list
    print(node_total)
    print(nodes_list)
    for i in range(node_total):
        if nodes_list[i].nodeid == selected_id:
            nodes_list[i].delete_node()
            del nodes_list[i]
            node_total = node_total - 1
            print(node_total)
            # print(nodes_list)
            break


# 增加修改和删除按钮到界面
delete_btn = ttk.Button(root, text="删除节点", command=delete_node)
delete_btn.grid(row=9, column=1)

# 提交按钮
submit_btn = ttk.Button(root, text="创建节点", command=create_node)
submit_btn.grid(row=9, column=0)
submit_btn = ttk.Button(root, text="设置背景", command=bgp_)
submit_btn.grid(row=10, column=0)
# 在创建主界面部分添加
info_label = tk.Label(root, text="双击节点后信息在这里显示", justify="left", anchor="w", padx=10)
info_label.place(x=0, y=800)


def generate_item_core(item_id, x, y, texture, texture_hovered, unlockable, recipe_items, required_quantities,
                       itemname, iteminfo, nodes_list, lower_id, width=16, height=16):
    global recipe_variables
    print(f"itemid={item_id}")
    item_key = item_id.lower().split(":")[1]  # 提取下划线后的内容并小写
    print(f"lowerid={lower_id}")
    # 动态生成局部变量和判断逻辑
    if lower_id[0] != "None":
        recipe_variables = [
            f"""
{item_id}_ori_texture:
  type: texture
  width: "1"
  height: "(方法.abs({y}+16-{lower_id[0].y_axis}))/1.5"
  x: "{x}+8"
  y: "{y}+16+界面变量.滚动值*13"
  limitX: 0
  limitY: 方法.取屏幕高度*0.15
  limitWidth: 9999
  limitHeight: 9999
  texture: 'icon/pixel.png'  
        """]
    if lower_id[0] != "None":
        recipe_variables += [
            f"""  
{item_id}_ori1_texture:
  type: texture
  width: "方法.abs({lower_id[0].x_axis}-{lower_id[len(lower_id) - 1].x_axis})"
  height: "1"
  x: "{lower_id[0].x_axis}+8"
  y: "{y}+16+(方法.abs({y}+16-{lower_id[0].y_axis}))/1.5+界面变量.滚动值*13"
  limitX: 0
  limitY: 方法.取屏幕高度*0.15
  limitWidth: 9999
  limitHeight: 9999
  texture: 'icon/pixel.png'  
"""]
    if lower_id[0] != "None":
        recipe_variables += [
            f"""
{item_id}_{i}_texture:
  type: texture
  width: "1"
  height: "方法.abs({lower_id[i].y_axis}-({y}+16+(方法.abs({y}+16-{lower_id[i].y_axis}))/1.5))"
  x: "{lower_id[i].x_axis}+8"
  y: "{y}+16+(方法.abs({y}+16-{lower_id[i].y_axis}))/1.5+界面变量.滚动值*13"
  limitX: 0
  limitY: 方法.取屏幕高度*0.15
  limitWidth: 9999
  limitHeight: 9999
  texture: 'icon/pixel.png'  
""" for i in range(len(lower_id))]
    recipe_checks = [
        f"""
          if(方法.取成员(方法.分割(方法.取槽位物品(方法.合并文本('container_' , 局部变量.计数文本 )),'"'), 1) == '{item.lower().replace('_', ':')}'){{
            局部变量.recipe{i + 1} = 局部变量.recipe{i + 1} + 方法.取物品数(方法.取槽位物品(方法.合并文本('container_' , 局部变量.计数文本 )));
        }};
        """ for i, item in enumerate(recipe_items)
    ]

    # 动态生成数量检查逻辑
    if len(required_quantities) > 1:
        # 多个条件时，生成使用 '||' 连接的检查逻辑
        quantity_check_condition = ' || '.join(
            [f"局部变量.recipe{i + 1} < {required_quantities[i]}" for i in range(len(required_quantities))])
        quantity_check = f"if({quantity_check_condition}){{"
    else:
        # 单个条件时，正常生成
        quantity_check = f"if(局部变量.recipe1 < {required_quantities[0]}){{"

    # 最终的内容生成
    return f"""  
{''.join([f'{recipe_variables[i]}' for i in range(len(recipe_variables))]).replace("+界面变量.滚动值*12", "").replace("+界面变量.滚动值*6", "").replace("+界面变量.滚动值*13", "+界面变量.滚动值*12")}   
{item_id.replace(":", "_")}_texture:
  x: "{x}"
  y: "{y}"
  texture: 'icon/{item_key}.png'
  width: 16
  height: 16
  limitX: 0
  limitY: 方法.取屏幕高度*0.15
  limitWidth: 9999
  limitHeight: 9999
  actions:
    click: |-
      界面变量.itemid = '{item_id.replace(":", "_")}';
      界面变量.itemid_ = '{item_id.replace(":", "_").split("_")[1]}';
      界面变量.itemname = '{itemname}';
      界面变量.iteminfo = '{iteminfo}';
      界面变量.unlockable='player_has_permission_recipe.unlockable.'&界面变量.itemid;
      界面变量.hasper='player_has_permission_recipe.'&界面变量.itemid;
      界面变量.unlockcmd=界面变量.itemid&'_unlock';
      
{item_id.replace(":", "_")}_locked_texture:
  x: "{x}"
  y: "{y}"
  texture: "icon/lock_icon.png"
  width: |-
    if(方法.取变量('player_has_permission_recipe.{item_id.replace(":", "_")}')=="yes"){{
      return '0' ;
    }};
    return '16';
  height: |-
    if(方法.取变量('player_has_permission_recipe.{item_id.replace(":", "_")}')=="yes"){{
      return '0' ;
    }};
    return '16';
  limitX: 0
  limitY: 方法.取屏幕高度*0.2
  limitWidth: 9999
  limitHeight: 200
  actions:
    click: |-
      界面变量.itemid = '{item_id.replace(":", "_")}';
      界面变量.itemid_ = '{item_id.replace(":", "_").split("_")[1]}';
      界面变量.itemname = '{itemname}';
      界面变量.iteminfo = '{iteminfo}';
      界面变量.unlockable='player_has_permission_recipe.unlockable.'&界面变量.itemid;
      界面变量.hasper='player_has_permission_recipe.'&界面变量.itemid;
      界面变量.unlockcmd=界面变量.itemid&'_unlock';

"""


def generate_item_var(nodes_list):
    var = []
    unlockable_list = ""
    # print(node_total)
    # 检查重复的变量
    for i in range(node_total):
        # print(nodes_list)
        unlockable_list += f"方法.更新变量值('player_has_permission_recipe.unlockable.{nodes_list[i].itemid.replace(":", "_")}');\n"
        unlockable_list += f"方法.更新变量值('player_has_permission_recipe.{nodes_list[i].itemid.replace(":", "_")}');\n"
    return unlockable_list


def generate_item_command(item_id, unlockable, unlockable_, recipe_items, required_quantities):
    item_key = item_id.lower().split(":")[1]
    unlockable_list = ""
    if len(unlockable_) > 1:
        for i in range(len(unlockable_)):
            if unlockable_[i] == "None":
                unlockable_list += "\n"
            else:
                unlockable_list += f"\\\\- \"[console]manuaddp %player_name% recipe.unlockable.{unlockable_[i].replace(":", "_")}\"\n"
    else:
        if unlockable_[0] == "None":
            unlockable_list = "\n"
        else:
            unlockable_list = f"\\\\- \"[console]manuaddp %player_name% recipe.unlockable.{unlockable_[0].replace(":", "_")}\"\n"
    if len(required_quantities) > 1:
        quantity_check_condition = ''.join(
            [
                f"\\\\- \"[console]clear %player_name% {recipe_items[i].replace(":", "_")} {required_quantities[i].replace(":", "_")}\" '\n'        "
                for i in range(len(required_quantities))])
        quantity_check = f"{quantity_check_condition}"
    else:
        # 单个条件时，正常生成
        quantity_check = f"\\\\- \"[console]clear %player_name% {recipe_items[0].replace(":", "_")} {required_quantities[0].replace(":", "_")}\""
    command = [
        f"""
    {item_id.replace(":", "_")}:
        {quantity_check}
        \\\\- "[console]give %player_name% {item_id.replace(":", "_")} 1"
    {item_id.replace(":", "_")}_unlock:
        \\\\- "[console]xp -1L %player_name%"
        \\\\- "[console]manuaddp %player_name% recipe.{item_id.replace(":", "_")}"
        {unlockable_list}
    """
    ]
    return f"""
    {''.join(command)}
        """


def generate_node_list(nodes_list):
    global node_num
    item_id = nodes_list.itemid
    x = nodes_list.x
    y = nodes_list.y
    unlockable = nodes_list.lower_id
    recipe_items = nodes_list.recipe_nospilt
    required_quantities = nodes_list.quantities
    node_para = f"nodenum={node_num}; item_id={item_id}; x={x}; y={y}; unlockable={unlockable}; recipe_items={recipe_items}; required_quantities={required_quantities}\n"
    return node_para


core_content = ""
command_content = ""
var_content = ""
node_content = ""


# 生成文件
def generate_files(nodes_list):
    global core_content, command_content, var_content, node_content, node_total, node_num

    # 创建文件夹
    os.makedirs('output', exist_ok=True)

    # 存储已经生成的变量，以避免重复

    # 打开文件写入
    with    open('output/core.yaml', 'w', encoding='utf-8') as core_file, open('output/command.yaml', 'w',
                                                                               encoding='utf-8') as command_file, open(
        'output/var.yaml', 'w', encoding='utf-8') as var_file, open(
        f'output/node_file_{time.strftime('%Y-%m-%d %H-%M-%S', time.localtime())}.yaml', 'w',
        encoding='utf-8') as node_store:

        core_content = ""
        command_content = ""
        var_content = ""
        node_content = ""
        for i in range(node_total):
            node_num = i
            core_content += generate_item_core(
                item_id=nodes_list[i].itemid,
                x=nodes_list[i].x_axis,
                y=nodes_list[i].y_axis,
                texture=os.path.join("icon/", nodes_list[i].itemid.split(":")[-1]) if nodes_list[i].itemid else None,
                texture_hovered=os.path.join("icon/", nodes_list[i].itemid.split(":")[-1]) if nodes_list[
                    i].itemid else None,
                unlockable=nodes_list[i].lower_id,
                recipe_items=nodes_list[i].recipe_spilt,
                required_quantities=nodes_list[i].quantities,
                itemname=nodes_list[i].itemname,
                iteminfo=nodes_list[i].iteminfo,
                nodes_list=nodes_list,
                lower_id=nodes_list[i].lower_id_id
            )

            command_content += generate_item_command(
                item_id=nodes_list[i].itemid,
                unlockable=nodes_list[i].lower_id,
                unlockable_=nodes_list[i].lower_id,
                recipe_items=nodes_list[i].recipe_spilt,
                required_quantities=nodes_list[i].quantities
            )

            var_content = generate_item_var(
                nodes_list=nodes_list
            )
            node_content += generate_node_list(
                nodes_list=nodes_list[i]
            )
        if core_content is not None:
            core_content = core_content.replace('{{', '{').replace('}}', '}')
        if var_content is not None:
            var_content = var_content.replace("方法.", '    方法.')
        if node_content is not None:
            node_content = node_content.replace("'", '')
        if command_content is not None:
            command_content = command_content.replace("['", '').replace("']", '')
            command_content = command_content.replace("\"", '"')
            command_content = command_content.replace("'", '')
            command_content = command_content.replace("    ", '')
            command_content = command_content.replace("\\", '  ')
        core_file.write(core_content + "\n")
        var_file.write(var_content)
        command_file.write(command_content)
        node_store.write(node_content)


# 示例输入
def generate():
    generate_files(nodes_list)
    print("文件已生成")


submit_btn = ttk.Button(root, text="生成文件", command=generate)
submit_btn.grid(row=10, column=1)
root.mainloop()
