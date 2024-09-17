import os
import tkinter as tk
from tkinter import ttk
import numpy as np

# 创建主界面
root = tk.Tk()
root.title("Tech Tree Generator")
root.geometry("400x300+100+100")
# 定义输入字段
item_id_var = tk.StringVar()
x_var = tk.StringVar()
y_var = tk.StringVar()
level_var = tk.IntVar()
recipe_var = tk.StringVar()
recipe_items_var = tk.StringVar()
required_quantities_var = tk.StringVar()
permission_nodes = tk.StringVar()
recipe_num_val = []
recipe_num_var = []
nodes = []
nodes_shift = []
intstr_product = []
intstr_recipe = []
intvar_quantities = []
product = []
recipe_separate = []
recipe = []
quantities = []
quantities_separate = []
# 布局
window_width = 500
window_height = 150
root.geometry(f"{window_width}x{window_height}")
tk.Label(root, text="X coordinate:").grid(row=0, column=0)
tk.Entry(root, textvariable=x_var).grid(row=0, column=1)

tk.Label(root, text="Y coordinate:").grid(row=1, column=0)
tk.Entry(root, textvariable=y_var).grid(row=1, column=1)

tk.Label(root, text="Level:").grid(row=2, column=0)
tk.Entry(root, textvariable=level_var).grid(row=2, column=1)

tk.Label(root, text=f"permission nodes(separate with comma, quantities=level):").grid(row=3, column=0)
tk.Entry(root, textvariable=permission_nodes).grid(row=3, column=1)
text_widget = tk.Text(root, width=40, height=10)
# tk.Label(root, text="Item ID:").grid(row=2, column=0)
# tk.Entry(root, textvariable=item_id_var).grid(row=2, column=1)

# tk.Label(root, text="Recipe:").grid(row=3, column=0)
# tk.Entry(root, textvariable=recipe_var).grid(row=3, column=1)

# tk.Label(root, text="Recipe Items (comma-separated):").grid(row=4, column=0)
# tk.Entry(root, textvariable=recipe_items_var).grid(row=4, column=1)

# tk.Label(root, text="Required Quantities (comma-separated):").grid(row=5, column=0)
# tk.Entry(root, textvariable=required_quantities_var).grid(row=5, column=1)
def split_by_comma(input_string):
    # 使用 split() 方法按逗号拆分字符串，并去掉首尾空格
    result_array = [item.strip() for item in input_string.split(",")]
    return result_array


def shift_left(arr):
    if len(arr) > 0:
        # 将数组内容左移一位，并在末尾补上 None
        shifted_array = arr[1:] + [None]
        return shifted_array
    return arr  # 如果数组为空，直接返回


# 处理输入

def prevalue():
    global recipe_num_var,nodes,nodes_shift  # 使用 global 声明全局变量

    # 获取输入的 x, y, level 值
    x = x_var.get()
    y = y_var.get()
    level = level_var.get()
    # 清空之前的全局变量数组，避免累加
    recipe_num_var.clear()

    # 动态创建 IntVar 并生成 Label 和 Entry
    for i in range(level):
        recipe_num_var.append(tk.IntVar())  # 添加到全局数组中
        recipe_num_val.append(int)  # 添加到全局数组中
        tk.Label(root, text=f"Enter the number of recipes in rank {i}:").grid(row=i + 4, column=0)
        tk.Entry(root, textvariable=recipe_num_var[i]).grid(row=i + 4, column=1)
    root.geometry(f"{window_width + level * 100}x{window_height + level * 40}")
    print(window_width + level * 100)
    nodes = split_by_comma(permission_nodes.get())
    nodes_shift = shift_left(nodes)
    print(f"nodes={nodes}")
    print(nodes_shift)
    submit_btn.grid(row=6 + level_var.get(), column=0)
    recipe_btn = ttk.Button(root, text="NEXT", command=recipe_command)
    recipe_btn.grid(row=6 + level_var.get(), column=1)


# 提交按钮

def recipe_command():
    global product, recipe, recipe_separate, recipe_num_var, recipe_num_val, quantities, quantities_separate, intstr_product
    x = x_var.get()
    y = y_var.get()
    prev = 0
    level = level_var.get()
    for i in range(level):
        recipe_num_val[i] = recipe_num_var[i].get()
        print(recipe_num_val[i])
        # 创建 IntVar 并添加到列表中
        # 动态创建 Label 和 Entry
        if recipe_num_val[i] == 0:
            print("不看要求你是脑瘫儿吗")
            prevalue()
            break
    max_val = max(recipe_num_val)
    # 创建二维数组，使用None初始化
    product = [[None for _ in range(max_val)] for _ in range(level)]
    recipe = [[None for _ in range(max_val)] for _ in range(level)]
    quantities = [[None for _ in range(max_val)] for _ in range(level)]
    root.geometry(f"{window_width + max(recipe_num_val) * 300}x{window_height + level * 100}")
    for i in range(level):
        for j in range(recipe_num_val[i]):
            # 显示产品条目
            product_str = tk.StringVar()
            recipe_str = tk.StringVar()
            quantities_int = tk.StringVar()
            product[i][j] = product_str  # 存储字符串变量
            recipe[i][j] = recipe_str  # 存储字符串变量
            quantities[i][j] = quantities_int  # 存储字符串变量

            tk.Label(root, text=f"product:").grid(row=0 + i * 7, column=j + 8)
            tk.Entry(root, textvariable=product_str).grid(row=1 + i * 7, column=j + 8)
            tk.Label(root, text=f"recipes (separate with comma)").grid(row=2 + i * 7, column=j + 8)
            tk.Entry(root, textvariable=recipe_str).grid(row=3 + i * 7, column=j + 8)
            tk.Label(root, text=f"quantities (separate with comma)").grid(row=4 + i * 7, column=j + 8)
            tk.Entry(root, textvariable=quantities_int).grid(row=5 + i * 7, column=j + 8)
            tk.Label(root, text=f"--------------------------------------------------").grid(row=6 + i * 7, column=j + 8)
    print(f"product:{product}")
    submit_btn.grid(row=6 + recipe_num_val[i], column=0)
    recipe_btn = ttk.Button(root, text="generate", command=generate)
    recipe_btn.grid(row=6 + level_var.get(), column=1)


def analysis():
    global product, recipe, quantities
    level = level_var.get()
    items_info = []

    for i in range(level):
        product_row = []
        recipe_row = []
        quantities_row = []

        for j in range(recipe_num_val[i]):
            if product[i][j] is not None and recipe[i][j] is not None and quantities[i][j] is not None:
                product_value = product[i][j].get().strip()
                recipe_value = recipe[i][j].get().strip().split(',')  # 处理为数组
                quantities_value = [int(q) for q in quantities[i][j].get().strip().split(',') if q.isdigit()]  # 处理为整数数组

                product_row.append(product_value)
                recipe_row.append(recipe_value)
                quantities_row.append(quantities_value)

        if product_row and recipe_row and quantities_row:
            items_info.append([
                (product_row[k], recipe_row[k], quantities_row[k])  # 按简化后的格式处理
                for k in range(len(product_row))
            ])

    # 打印输出，用于检查生成的 items_info
    for idx, level_items in enumerate(items_info):
        print(f"Level {idx}:")
        for item in level_items:
            print(f" Item ID: {item[0]}")
            print(f" Recipe Items: {item[1]}")
            print(f" Quantities: {item[2]}")

    print(items_info)
    return items_info



    # 启动界面



# 根据输入生成坐标和物品ID相关的字符串
def generate_item_core(item_id, x, y, texture, texture_hovered, unlockable, recipe_items, required_quantities,
                       width=16, height=16):
    item_key = item_id.lower().split('_')[1]  # 提取下划线后的内容并小写

    # 动态生成局部变量和判断逻辑
    recipe_variables = [f"局部变量.recipe{i + 1} = 0;" for i in range(len(recipe_items))]
    recipe_checks = [
        f"""
        if(方法.取成员(方法.分割(方法.取槽位物品(方法.合并文本('container_' , 局部变量.计数文本 )),'"'), 1) == '{item}'){{
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
    if(方法.取变量('player_has_permission_recipe.{item_key}')!="yes" && 方法.取变量('player_has_permission_recipe.unlockable.{unlockable}')=="yes"){{
      return "{texture}_unlockable.png";
    }};
    return "icon/unknown_recipe.png"
  textureHovered:     
    if(方法.取变量('player_has_permission_recipe.{item_key}')=="yes"){{
      return "{texture_hovered}.png";
    }};
    if(方法.取变量('player_has_permission_recipe.{item_key}')!="yes" && 方法.取变量('player_has_permission_recipe.unlockable.{unlockable}')=="yes"){{
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
      return '{recipe}';
    }};
    if(方法.取变量('player_has_permission_recipe.{item_key}')!="yes" && 方法.取变量('player_has_permission_recipe.unlockable.{unlockable}')=="yes"){{
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
      }} else if(方法.取变量('player_has_permission_recipe.unlockable.{unlockable}')=="yes"){{
        if(方法.取变量('player_level')>=1){{
          方法.执行按键指令('{item_id}_unlock');
        }} else {{
          方法.消息('§b你的科技点不足');
        }}
      }};
    """


def generate_item_var(item_id, unlockable, generated_set):
    item_key = item_id.lower().split('_')[1]
    var = []

    # 检查重复的变量
    if f'player_has_permission_recipe.{item_key}' not in generated_set:
        generated_set.add(f'player_has_permission_recipe.{item_key}')
        var.append(f"方法.更新变量值('player_has_permission_recipe.{item_key}');\n")

    for i in range(len(unlockable)):
        if f'player_has_permission_recipe.unlockable.{unlockable[i]}' not in generated_set:
            generated_set.add(f'player_has_permission_recipe.unlockable.{unlockable[i]}')
            var.append(f"方法.更新变量值('player_has_permission_recipe.unlockable.{unlockable[i]}');\n")

    return ''.join(var)


def generate_item_command(item_id, unlockable, unlockable_, recipe_items, required_quantities, level):
    item_key = item_id.lower().split('_')[1]
    if len(required_quantities) > 1:
        quantity_check_condition = ''.join(
            [
                f"\\\\- caonima[console]clear %player_name% {recipe_items[i]} {required_quantities[i]}caonima '\n'        "
                for i in range(len(required_quantities))])
        quantity_check = f"{quantity_check_condition}"
    else:
        # 单个条件时，正常生成
        quantity_check = f"\\\\- caonima[console]clear %player_name% {recipe_items} {required_quantities[0]}caonima"
    command = [
        f"""
    {item_id}:
        {quantity_check}
        \\\\- "[console]give %player_name% {item_id} 1"
    {item_id}_unlock:
        \\\\- "[console]xp -1L %player_name%"
        \\\\- "[console]manuaddp %player_name% recipe.{item_key}"
        \\\\- "[console]manuaddp %player_name% recipe.unlockable.{unlockable_}"
    """
    ]
    return f"""
    {''.join(command)}
        """


# 生成文件
def generate_files(levels, initial_x, initial_y, items_info, unlockables,unlockables_):
    # 创建文件夹
    os.makedirs('output', exist_ok=True)

    # 存储已经生成的变量，以避免重复
    generated_set = set()

    # 打开文件写入
    with open('output/core.yaml', 'w', encoding='utf-8') as core_file, \
            open('output/command.yaml', 'w', encoding='utf-8') as command_file, \
            open('output/var.yaml', 'w', encoding='utf-8') as var_file:

        x = initial_x
        y = initial_y

        for level, items in enumerate(items_info):
            for index, (item_id, recipe_items, required_quantities) in enumerate(items):
                core_content = generate_item_core(
                    item_id=item_id,
                    x=f"{x}+{index * 16}",
                    y=f"{y}+{level * 16}",
                    texture=f"icon/{item_id.lower().split('_')[1]}",
                    texture_hovered=f"icon/{item_id.lower().split('_')[1]}",
                    unlockable=unlockables[level],
                    recipe_items=recipe_items,
                    required_quantities=required_quantities
                )
                command_content = generate_item_command(
                    item_id=item_id,
                    unlockable=unlockables[level],
                    unlockable_=unlockables_[level],
                    recipe_items=recipe_items,
                    required_quantities=required_quantities,
                    level=level
                )
                var_content = generate_item_var(
                    item_id=item_id,
                    unlockable=unlockables,
                    generated_set=generated_set  # 传入去重的集合
                )
                core_content = core_content.replace('{{', '{').replace('}}', '}')
                var_content = var_content.replace("\n        ", '')
                var_content = var_content.replace("\n    ", '')
                var_content = var_content.replace("方法.", '    方法.')
                command_content = command_content.replace("['", '').replace("']", '')
                command_content = command_content.replace("caonima", '"')
                command_content = command_content.replace("'", '')
                command_content = command_content.replace("    ", '')
                command_content = command_content.replace("\\\\", '    ')
                core_file.write(core_content + "\n")
                var_file.write(var_content)
                command_file.write(command_content)


# 示例输入
def generate():
    levels = level_var.get()
    initial_x = x_var.get()
    initial_y = y_var.get()
    items_info = analysis()
    unlockables = nodes  # 所有层级的权限节点
    unlockables_ = nodes_shift  # 去除第一位，树冠补None
    print(unlockables)
    print(f"Length of unlockables: {len(unlockables)}")
    print(f"Length of unlockables_: {len(unlockables_)}")
    generate_files(levels, initial_x, initial_y, items_info, unlockables,unlockables_)
    print("文件已生成")

submit_btn = ttk.Button(root, text="Submit", command=prevalue)
submit_btn.grid(row=6, column=0)
root.mainloop()