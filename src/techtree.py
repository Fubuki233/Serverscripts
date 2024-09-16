import os


# 根据输入生成坐标和物品ID相关的字符串
def generate_item_core(item_id, x, y, texture, texture_hovered, recipe, unlockable, recipe_items, required_quantities,
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



def generate_item_command(item_id, recipe, unlockable,unlockable_, recipe_items, required_quantities,level):
    item_key = item_id.lower().split('_')[1]
    if len(required_quantities) > 1:
        quantity_check_condition = ''.join(
        [
        f"\\\\- caonima[console]clear %player_name% {recipe_items[i]} {required_quantities[i]}caonima '\n'        " for i in range(len(required_quantities))])
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
def generate_files(levels, initial_x, initial_y, items_info, unlockables):
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
            for index, (item_id, recipe, recipe_items, required_quantities) in enumerate(items):
                core_content = generate_item_core(
                    item_id=item_id,
                    x=f"{x}+{index * 16}",
                    y=f"{y}+{level * 16}",
                    texture=f"icon/{item_id.lower().split('_')[1]}",
                    texture_hovered=f"icon/{item_id.lower().split('_')[1]}",
                    recipe=recipe,
                    unlockable=unlockables[level],
                    recipe_items=recipe_items,
                    required_quantities=required_quantities
                )
                command_content = generate_item_command(
                    item_id=item_id,
                    recipe=recipe,
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
levels = 4
initial_x = "0.35*方法.取屏幕宽度"
initial_y = "界面变量.滚动值*6+0.25*方法.取屏幕高度"

items_info = [
    [("MINERUSTADDONS_ROCK", "MINERUSTADDONS_PIECESTONE 4", ['MINERUSTADDONS_PIECESTONE'], [4])],
    [("MINERUSTADDONS_BONEKNIFE", "MINERUSTADDONS_RESBONE 4", ['MINERUSTADDONS_RESBONE'], [4]),
     ("MINERUSTADDONS_BONETOOL", "MINERUSTADDONS_RESBONE 4", ['MINERUSTADDONS_RESBONE'], [4]),
     ("MINERUSTADDONS_WOODENSPEAR", "MINERUSTADDONS_PIECEWOOD 4", ['MINERUSTADDONS_PIECEWOOD'], [4]),
     ("MINERUSTADDONS_WOODENSWORD", "MINERUSTADDONS_PLANKITEM 4 MINERUSTADDONS_STICKITEM 1", ['MINERUSTADDONS_PLANKITEM', 'MINERUSTADDONS_STICKITEM'], [4, 1])],
    [("MINERUSTADDONS_STONEPICKAXE", "MINERUSTADDONS_PIECESTONE 4 MINERUSTADDONS_STICKITEM 1", ['minerustaddons_piecestone', 'MINERUSTADDONS_STICKITEM'], [4, 1]),
     ("MINERUSTADDONS_STONEAXE", "MINERUSTADDONS_PIECESTONE 4 MINERUSTADDONS_STICKITEM 1", ['minerustaddons_piecestone', 'MINERUSTADDONS_STICKITEM'], [4, 1]),
     ("MINERUSTADDONS_STONESPEAR", "MINERUSTADDONS_PIECESTONE 1 MINERUSTADDONS_STICKITEM 1", ['minerustaddons_piecestone', 'MINERUSTADDONS_STICKITEM'], [1, 1]),
     ("MINERUSTADDONS_KNIFE", "MINERUSTADDONS_PIECESTONE 4 MINERUSTADDONS_STICKITEM 1", ['minerustaddons_piecestone', 'MINERUSTADDONS_STICKITEM'], [4, 1])],
    [("MINERUSTADDONS_METALPICKAXE",  "MINERUSTADDONS_MHQ 4 MINERUSTADDONS_NAILS 4 MINERUSTADDONS_BOLTS 4 MINERUSTADDONS_METALPICKAXELOWERDETAIL 1",
      ['MINERUSTADDONS_MHQ', 'MINERUSTADDONS_NAILS', 'MINERUSTADDONS_BOLTS', 'MINERUSTADDONS_METALPICKAXELOWERDETAIL'], [4, 4, 4, 1]),
     ("MINERUSTADDONS_METALAXE",  "MINERUSTADDONS_MHQ 4 MINERUSTADDONS_NAILS 4 MINERUSTADDONS_BOLTS 4 MINERUSTADDONS_METALPICKAXELOWERDETAIL 1",
      ['MINERUSTADDONS_MHQ', 'MINERUSTADDONS_NAILS', 'MINERUSTADDONS_BOLTS', 'MINERUSTADDONS_METALPICKAXELOWERDETAIL'], [4, 4, 4, 1]),
     ("MINERUSTADDONS_COMBATKNIFE",  "MINERUSTADDONS_MHQ 4 MINERUSTADDONS_METALPICKAXELOWERDETAIL 1",
      ['MINERUSTADDONS_MHQ', 'MINERUSTADDONS_METALPICKAXELOWERDETAIL'], [4, 1]),
     ("MINERUSTADDONS_METALSWORD",  "MINERUSTADDONS_MHQ 4 MINERUSTADDONS_METALPICKAXELOWERDETAIL 1",
      ['MINERUSTADDONS_MHQ', 'MINERUSTADDONS_METALPICKAXELOWERDETAIL'], [4, 1]),
     ("MINERUSTADDONS_MACE",  "MINERUSTADDONS_MHQ 4 MINERUSTADDONS_NAILS 8 MINERUSTADDONS_METALPICKAXELOWERDETAIL 1",
      ['MINERUSTADDONS_MHQ', 'MINERUSTADDONS_NAILS', 'MINERUSTADDONS_METALPICKAXELOWERDETAIL'], [4, 8, 1]),
     ("MINERUSTADDONS_WARHAMMER",  "MINERUSTADDONS_MHQ 8 MINERUSTADDONS_METALPICKAXELOWERDETAIL 1",
      ['MINERUSTADDONS_MHQ', 'MINERUSTADDONS_METALPICKAXELOWERDETAIL'], [4, 1])]
]

unlockables = ["rock", "bonetools", "stonetools","mentaltools"] #所有层级的权限节点
unlockables_ = ["bonetools", "stonetools","mentaltools","void"] #去除第一位，树冠补void

generate_files(levels, initial_x, initial_y, items_info, unlockables)
print("文件已生成")
