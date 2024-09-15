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
        quantity_check_condition = ' || '.join([f"局部变量.recipe{i + 1} < {required_quantities[i]}" for i in range(len(required_quantities))])
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
    return "icon/unknownrecipe.png"
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

# 生成文件
def generate_files(levels, initial_x, initial_y, items_info, unlockables):
    # 创建文件夹
    os.makedirs('output', exist_ok=True)

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
                core_content = core_content.replace('{{', '{').replace('}}', '}')
                core_file.write(core_content + "\n")

# 示例输入
levels = 3
initial_x = "0.69*方法.取屏幕宽度+80"
initial_y = "界面变量.techtree滚动值*6+0.32*方法.取屏幕高度"

items_info = [
    [("MINERUSTADDONS_HAYWALL", "MINERUSTADDONS_CLOTH 8", ['minerustaddons:cloth'], [8]),
     ("MINERUSTADDONS_HAYCEILING", "MINERUSTADDONS_CLOTH 4", ['minerustaddons:cloth'], [4])],
    [("MINERUSTADDONS_WOODWALL", "MINERUSTADDONS_PLANKITEM 8", ['minerustaddons:plankitem'], [8]),
     ("MINERUSTADDONS_WOODCEILING", "MINERUSTADDONS_PLANKITEM 4", ['minerustaddons:plankitem'], [4])],
    [("MINERUSTADDONS_STONEWALL", "MINERUSTADDONS_PIECESTONE 4 MINERUSTADDONS_NAILS 4",
      ['minerustaddons:piecestone', 'minerustaddons:nails'], [4, 4]),
     ("MINERUSTADDONS_STONECEILING", "MINERUSTADDONS_PIECESTONE 2 MINERUSTADDONS_NAILS 2",
      ['minerustaddons:piecestone', 'minerustaddons:nails'], [2, 2])]
]

unlockables = ["haybuild", "woodbuild", "stonebuild"]

generate_files(levels, initial_x, initial_y, items_info, unlockables)
print("文件已生成")
