import os
import tkinter as tk
from tkinter import ttk
from PIL import Image, ImageTk
import os


class DraggableRectangle:
    def __init__(self, canvas, x1, y1, x2, y2, itemid, recipes, quantities_new, icon_path, lower_id=None):
        global recipe_spilt,selected_id
        item_id = itemid
        self.x1 = x1
        self.y1 = y1
        self.x_axis = f"{(x1 + 623) / 1920}*方法.取屏幕宽度"
        self.y_axis = f"{y1 / 1080}*方法.取屏幕高度"
        self.lower_id = ["None"]
        self.quantities = []
        self.recipe_spilt = []
        self.lines = []  # 存储与此节点相关的连接线
        self.itemid = itemid
        self.nodeid = self
        self.canvas = canvas
        selected_id = self
        self.icon_path = icon_path
        print(self.quantities)
        # 处理 itemid 获取下划线后的部分，并设置图标路径
        self.icon_path = os.path.join(icon_path, itemid.split("_")[-1] + ".png") if itemid else None
        print(f"icon_path={self.icon_path}")
        self.recipe_spilt = split_by_comma(recipes)
        self.quantities = split_by_comma(quantities_new)
        print(f"recipe_spilt={self.recipe_spilt}")
        print(f"quantities={self.quantities}")
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

        self.text = canvas.create_text((x1 + x2) // 2, (y1 + y2) // 2, text="Node")
        self.tag = canvas.create_text(x1 - 20, (y1 + y2) // 2, text=item_id, anchor="e")

        # 创建按钮
        self.button = tk.Button(canvas, text="Connect", width=1, height=1, command=self.select_node)
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

        self.x = 0
        self.y = 0
        self.selected = False

    def on_press(self, event):
        self.x = event.x
        self.y = event.y

    def on_drag(self, event):
        dx = event.x - self.x
        dy = event.y - self.y
        # 移动背景图片
        if self.image_tk:
            self.canvas.move(self.image_item, dx, dy)
        # 移动透明矩形和其他组件
        self.canvas.move(self.rect, dx, dy)
        self.canvas.move(self.text, dx, dy)
        self.canvas.move(self.button_window, dx, dy)
        self.canvas.move(self.tag, dx, dy)
        self.x = event.x
        self.y = event.y
        self.x_axis = f"{self.x / 1920}*方法.取屏幕宽度"
        self.y_axis = f"{self.y / 1080}*方法.取屏幕高度"
        self.selected = True
        # 更新连接线位置
        if self.selected:
            for line in self.lines:
                line.update_position()

    def select_node(self):
        global selected_nodes, connect_info, connect_num
        if len(selected_nodes) < 2:
            selected_nodes.append(self)
            print(f"connect_num={connect_num}")
            connect_info[connect_num][0] = selected_nodes[0]
            if len(selected_nodes) == 2:
                connect_info[connect_num][1] = selected_nodes[1]
                print(f"selected_nodes={selected_nodes}")
                print(f"cinfo0={connect_info[connect_num][0]}")
                print(f"cinfo1={connect_info[connect_num][1]}")
                self.set_lower_id()
                print(f"lower:{self.lower_id}")
                create_line()

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
        selected_nodes[0].lower_id.append(selected_nodes[1].itemid)
        print(f"{selected_nodes[0].itemid}'s lower itemid={selected_nodes[0].lower_id}")
        # selected_nodes[1].move_node_to_new_position()

    def show_parameters(self, event=None):
        """在输入框中显示当前节点的参数"""
        global selected_id,border
        selected_id=self
        Item_ID_var.set(selected_id.itemid)
        recipe_new.set(",".join(selected_id.recipe_spilt))
        quantities_var.set(",".join(selected_id.quantities))
        print(selected_id)
        canvas.delete(border)
        border = canvas.create_rectangle(self.canvas.coords(self.rect)[0] - 2, self.canvas.coords(self.rect)[1] - 2, self.canvas.coords(self.rect)[0] + 64, self.canvas.coords(self.rect)[1] + 64, outline="red", width=2)
        print(self.canvas.coords(self.rect))
    def update_parameters(self):
        """更新节点参数"""
        self.itemid = Item_ID_var.get()
        self.recipe_spilt = split_by_comma(recipe_new.get())
        self.quantities = split_by_comma(quantities_var.get())
        # 更新画布上的显示
        self.canvas.itemconfig(self.tag, text=self.itemid)
        self.canvas.itemconfig(self.text, text="Node")


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
        nodes_list.remove(self)
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
root.title("Tech Tree Generator")
id = 0
# 定义输入字段
Item_ID_var = tk.StringVar()
tag = tk.StringVar()
quantities_var = tk.StringVar()
bgp = tk.StringVar()
icons = tk.StringVar()
y_var = tk.StringVar()
level_var = tk.IntVar()
recipe_var = tk.StringVar()
recipe_items_var = tk.StringVar()
required_quantities_var = tk.StringVar()
permission_nodes = tk.StringVar()
recipe_new = tk.StringVar()
recipe_num_val = []
recipe_num_var = []
nodes_list = [i for i in range(100)]
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
# 布局
window_width = 1920
window_height = 1080
canvas = tk.Canvas(root, width=window_width, height=window_height)
canvas.grid(row=0, column=0, rowspan=50, columnspan=50)  # 覆盖整个窗口
root.geometry(f"{window_width}x{window_height}")
tk.Label(root, text="Item ID:").grid(row=0, column=0)
tk.Entry(root, textvariable=Item_ID_var).grid(row=0, column=1)

tk.Label(root, text="recipes(comma seperated):").grid(row=1, column=0)
tk.Entry(root, textvariable=recipe_new).grid(row=1, column=1)

tk.Label(root, text="quantities(comma seperated)").grid(row=2, column=0)
tk.Entry(root, textvariable=quantities_var).grid(row=2, column=1)

tk.Label(root, text="bgp path:").grid(row=3, column=0)
tk.Entry(root, textvariable=bgp).grid(row=3, column=1)

tk.Label(root, text="icons path:").grid(row=4, column=0)
tk.Entry(root, textvariable=icons).grid(row=4, column=1)


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
    itemid = Item_ID_var.get()
    new_x = 100
    new_y = 200
    node_paramater(itemid, new_x, new_y)


# 创建节点
def create_node():
    global node_total
    x = 800
    y = 200
    node = DraggableRectangle(canvas, x, y, x + 64, y + 64, Item_ID_var.get(), recipe_new.get(), quantities_var.get(),
                              icons.get())
    nodes_list[node_total] = node  # 将节点和别名存储在字典中
    node_total += 1
    print(f"nodes_list={nodes_list[0]}")
    print(f"node_total={node_total}")


def test_nodes():
    for i in range(node_total):
        # itemid, recipes, quantities_new, icon_path, lower_id = None
        print("-------------------------------------------")
        print(f"x={nodes_list[i].x_axis}")
        print(f"y={nodes_list[i].y_axis}")
        print(f"itemid={nodes_list[i].itemid}")
        print(f"recipes={nodes_list[i].recipe}")
        print(f"uantities={nodes_list[i].quantities}")
        print(f"lower_id={nodes_list[i].lower_id}")


def bgp_():
    global bgpimg

    # 加载并显示图片
    print("11")
    try:
        print("112")
        # 打开并调整图片大小
        bgpimg = Image.open(bgp.get())
        # 将图片转换为 Tkinter 兼容格式
        bgpimg = ImageTk.PhotoImage(bgpimg)

        # 将图片放在 Canvas 上作为背景
        canvas.create_image(623, 0, anchor="nw", image=bgpimg)

    except Exception as e:
        print(f"Error loading image: {e}")
def modify_node():
    """修改节点参数"""
    itemid = Item_ID_var.get()
    for node in nodes_list:
        if node.itemid == itemid:
            node.update_parameters()
            break

def delete_node():
    """删除选中的节点"""
    global selected_id
    for node in nodes_list:
        if node.nodeid == selected_id:
            node.delete_node()
            break

# 增加修改和删除按钮到界面
modify_btn = ttk.Button(root, text="Modify Node", command=modify_node)
modify_btn.grid(row=7, column=0)
delete_btn = ttk.Button(root, text="Delete Node", command=delete_node)
delete_btn.grid(row=8, column=0)

# 提交按钮
submit_btn = ttk.Button(root, text="Create Node", command=create_node)
submit_btn.grid(row=5, column=0)
submit_btn = ttk.Button(root, text="Set bgp", command=bgp_)
submit_btn.grid(row=6, column=0)


def generate_item_core(item_id, x, y, texture, texture_hovered, unlockable, recipe_items, required_quantities,
                       width=16, height=16):
    item_key = item_id.lower().split('_')[1]  # 提取下划线后的内容并小写
    # 动态生成局部变量和判断逻辑
    recipe_variables = [f"局部变量.recipe{i + 1} = 0;" for i in range(len(recipe_items))]
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
    
{item_id}_texture:
  x: "{x}"
  y: "{y}"
  texture: |-
    if(方法.取变量('player_has_permission_recipe.{item_key}')=="yes"){{
      return "{texture}.png";
    }};
    if(方法.取变量('player_has_permission_recipe.{item_key}')!="yes" && 方法.取变量('player_has_permission_recipe.unlockable.{item_id}')=="yes"){{
      return "{texture}_unlockable.png";
    }};
    return "icon/unknown_recipe.png"
  textureHovered:     
    if(方法.取变量('player_has_permission_recipe.{item_key}')=="yes"){{
      return "{texture_hovered}.png";
    }};
    if(方法.取变量('player_has_permission_recipe.{item_key}')!="yes" && 方法.取变量('player_has_permission_recipe.unlockable.{item_id}')=="yes"){{
      return "{texture_hovered}_unlockable.png";
    }};
    return "icon/unknown_recipe.png";
  width: {width}
  height: {height}
  limitX: 0
  limitY: 方法.取屏幕高度*0.2
  limitWidth: 9999
  limitHeight: 200
  tip: |-
    if(方法.取变量('player_has_permission_recipe.{item_key}')=="yes"){{
      return '可以合成';
    }};
    if(方法.取变量('player_has_permission_recipe.{item_key}')!="yes" && 方法.取变量('player_has_permission_recipe.unlockable.{item_id}')=="yes"){{
      return '单击消耗 1科技点 来解锁配方';
    }};
    return '未知的配方'; 
  actions:
    click: |-
      if(方法.取变量('player_has_permission_recipe.{item_key}')=="yes"){{
        {''.join(recipe_variables)}
        局部变量.计数 = 0;
        loop(88, {{
          局部变量.计数文本 = 方法.到整数(局部变量.计数);
          {''.join(recipe_checks)}
          局部变量.计数 = 局部变量.计数 + 1;
        }});
        {quantity_check}
          方法.消息('§b你的背包中没有足够的材料');
          方法.actionbar('文本');
          方法.界面变量.{item_key}_craftable=false;
        }} else {{
          方法.执行按键指令('{item_id}');
          方法.界面变量.{item_key}_craftable=true;
        }};
      }} else if(方法.取变量('player_has_permission_recipe.unlockable.{item_id}')=="yes"){{
        if(方法.取变量('player_level')>=1){{
          方法.执行按键指令('{item_id}_unlock');
        }} else {{
          方法.消息('§b你的科技点不足');
        }}
      }};
    """


def generate_item_var(nodes_list):
    var = []
    unlockable_list = ""
    # 检查重复的变量
    for i in range(node_total):
        unlockable_list += f"方法.更新变量值('player_has_permission_recipe.unlockable.{nodes_list[i].itemid}');\n"
        unlockable_list += f"方法.更新变量值('player_has_permission_recipe.{nodes_list[i].itemid}');\n"
    return unlockable_list


def generate_item_command(item_id, unlockable, unlockable_, recipe_items, required_quantities):
    item_key = item_id.lower().split('_')[1]
    unlockable_list = ""
    if len(unlockable_) > 1:
        for i in range(len(unlockable_)):
            if unlockable_[i] == "None":
                unlockable_list += "\n"
            else:
                unlockable_list += f"\\\\- \"[console]manuaddp %player_name% recipe.unlockable.{unlockable_[i]}\"\n"
    else:
        if unlockable_[0] == "None":
            unlockable_list = "\n"
        else:
            unlockable_list = f"\\\\- \"[console]manuaddp %player_name% recipe.unlockable.{unlockable_[0]}\"\n"
    if len(required_quantities) > 1:
        quantity_check_condition = ''.join(
            [
                f"\\\\- \"[console]clear %player_name% {recipe_items[i]} {required_quantities[i]}\" '\n'        "
                for i in range(len(required_quantities))])
        quantity_check = f"{quantity_check_condition}"
    else:
        # 单个条件时，正常生成
        quantity_check = f"\\\\- \"[console]clear %player_name% {recipe_items} {required_quantities[0]}\""
    command = [
        f"""
    {item_id}:
        {quantity_check}
        \\\\- "[console]give %player_name% {item_id} 1"
    {item_id}_unlock:
        \\\\- "[console]xp -1L %player_name%"
        \\\\- "[console]manuaddp %player_name% recipe.{item_key}"
        {unlockable_list}
    """
    ]
    return f"""
    {''.join(command)}
        """


core_content = ""
command_content = ""
var_content = ""


# 生成文件
def generate_files(nodes_list):
    global core_content, command_content, var_content
    # 创建文件夹
    os.makedirs('output', exist_ok=True)

    # 存储已经生成的变量，以避免重复

    # 打开文件写入
    with    open('output/core.yaml', 'w', encoding='utf-8') as core_file, open('output/command.yaml', 'w',
                                                                               encoding='utf-8') as command_file, open(
        'output/var.yaml', 'w', encoding='utf-8') as var_file:
        for i in range(node_total):
            core_content += generate_item_core(
                item_id=nodes_list[i].itemid,
                x=nodes_list[i].x_axis,
                y=nodes_list[i].y_axis,
                texture=os.path.join("icon/", nodes_list[i].itemid.split("_")[-1]) if nodes_list[i].itemid else None,
                texture_hovered=os.path.join("icon/", nodes_list[i].itemid.split("_")[-1]) if nodes_list[
                    i].itemid else None,
                unlockable=nodes_list[i].lower_id,
                recipe_items=nodes_list[i].recipe_spilt,
                required_quantities=nodes_list[i].quantities
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
        if core_content is not None:
            core_content = core_content.replace('{{', '{').replace('}}', '}')
        if var_content is not None:
            var_content = var_content.replace("方法.", '    方法.')
        if command_content is not None:
            command_content = command_content.replace("['", '').replace("']", '')
            command_content = command_content.replace("\"", '"')
            command_content = command_content.replace("'", '')
            command_content = command_content.replace("    ", '')
            command_content = command_content.replace("\\", '  ')
        core_file.write(core_content + "\n")
        var_file.write(var_content)
        command_file.write(command_content)


# 示例输入
def generate():
    generate_files(nodes_list)
    print("文件已生成")


submit_btn = ttk.Button(root, text="Submit", command=generate)
submit_btn.grid(row=7, column=0)
root.mainloop()
