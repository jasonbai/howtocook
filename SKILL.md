---
name: howtocook
description: 智能菜谱推荐与烹饪指导助手。当用户询问"今天吃什么"、"怎么做某道菜"、"给我推荐个菜谱"、"晚餐做什么"、"有什么简单易做的菜"、"来客人了怎么安排菜单"、"帮我查个菜谱"、"什么菜好吃"等任何与烹饪、菜谱、饮食安排相关的问题时，必须使用此技能。支持基于场景、食材、难度、时间、人数等多维度智能推荐，并提供详细的分步烹饪指导。内置 357+ 精选家常菜谱，涵盖荤菜、素菜、汤品、主食、水产、甜品等 10 大分类。
---

# HowToCook 智能烹饪助手

基于 [HowToCook 项目](https://github.com/Anduin2017/HowToCook) 的智能菜谱推荐与烹饪指导系统，帮助你解决日常烹饪三大难题：

## 🎯 核心功能

1. **吃什么** - 根据场景、时间、难度智能推荐菜谱
2. **怎么做** - 提供详细的分步烹饪指导
3. **怎么安排** - 为多人用餐规划平衡菜单

## 📚 菜谱数据库

- **数据来源**: [HowToCook 项目](https://github.com/Anduin2017/HowToCook)
- **356** 精选家常菜谱（内置在技能目录中）
- **10 大分类**: 荤菜、素菜、汤品、主食、水产、早餐、甜品、饮品、酱料、半成品
- **9 级难度**: 从 ★ (极简单) to ★★★★★★★★ (大师级)
- **时间预估**: 基于难度的智能时间估算

## 🏷️ 分类速查表

| 分类 | 英文标识 | 示例菜谱 |
|------|----------|----------|
| 🥩 荤菜 | `meat_dish` | 红烧肉、宫保鸡丁、糖醋排骨 |
| 🥬 素菜 | `vegetable_dish` | 西红柿炒鸡蛋、酸辣土豆丝、蒜蓉西兰花 |
| 🍲 汤品 | `soup` | 西红柿豆腐汤羹、紫菜蛋花汤 |
| 🍜 主食 | `staple` | 炒米饭、意面、煎饼 |
| 🐟 水产 | `aquatic` | 红烧鱼、清蒸鲈鱼 |
| 🌅 早餐 | `breakfast` | 牛奶面包、煎蛋 |
| 🍮 甜品 | `dessert` | 拔丝土豆、清蒸南瓜 |
| 🥤 饮品 | `drink` | 各类饮品 |
| 🧂 酱料 | `condiment` | 自制酱料 |
| 📦 半成品 | `semi-finished` | 基础食材处理 |

## ⭐ 难度等级参考表

| 星级 | 名称 | 预估时间 | 特征 |
|------|------|----------|------|
| ★ | 极简单 | 5 分钟 | 无需刀工，简单调味 |
| ★★ | 新手友好 | 10 分钟 | 基础刀工，常见调料 |
| ★★★ | 简单 | 20 分钟 | 标准家常菜难度 |
| ★★★★ | 中等 | 35 分钟 | 需要多步骤操作 |
| ★★★★★ | 进阶 | 50 分钟 | 复杂调味或技巧 |
| ★★★★★★ | 困难 | 60 分钟 | 需要熟练技巧 |
| ★★★★★★★ | 较难 | 75 分钟 | 高难度技巧 |
| ★★★★★★★★ | 很难 | 90 分钟 | 专业厨师级别 |
| ★★★★★★★★★ | 大师级 | 120 分钟 | 极具挑战性 |

---

# 🔄 工作流程

## Phase 0: 意图识别

首先判断用户意图类型：

### 模式 A: 菜谱推荐
**触发词示例:**
- "今天吃什么"
- "给我推荐个菜"
- "晚餐做什么"
- "有什么简单易做的菜"
- "新手做什么菜好"

### 模式 B: 菜谱查询
**触发词示例:**
- "怎么做[菜名]"
- "[菜名]怎么做"
- "查一下[菜名]的做法"
- "我想做[菜名]"

### 模式 C: 菜单规划
**触发词示例:**
- "来客人了怎么安排"
- "帮几个人规划菜单"
- "聚餐做什么菜"
- "多人用餐建议"

---

## Phase 1: 信息收集

根据用户意图，使用 `AskUserQuestion` 收集偏好信息：

### 菜谱推荐 - 收集以下信息

```python
AskUserQuestion(
    questions=[
        {
            "question": "什么时候用餐？",
            "header": "用餐时间",
            "options": [
                {"label": "早餐", "description": "简单快捷，唤醒一天"},
                {"label": "午餐", "description": "营养丰富，补充能量"},
                {"label": "晚餐", "description": "丰盛满足，享受美食"},
                {"label": "夜宵", "description": "简单轻食，缓解饥饿"}
            ],
            "multiSelect": False
        },
        {
            "question": "大概有多少时间做饭？",
            "header": "时间限制",
            "options": [
                {"label": "5-10分钟", "description": "快手菜，极简单"},
                {"label": "10-20分钟", "description": "简单家常菜"},
                {"label": "20-40分钟", "description": "标准烹饪时间"},
                {"label": "40分钟以上", "description": "复杂菜式，不急"}
            ],
            "multiSelect": False
        },
        {
            "question": "你的厨艺水平如何？",
            "header": "厨艺水平",
            "options": [
                {"label": "新手", "description": "刚开始学做菜"},
                {"label": "进阶", "description": "会做一些基础菜"},
                {"label": "熟练", "description": "经常做菜，有经验"}
            ],
            "multiSelect": False
        },
        {
            "question": "偏好什么类型的菜品？",
            "header": "菜品偏好",
            "options": [
                {"label": "荤菜", "description": "肉食为主，营养丰富"},
                {"label": "素菜", "description": "清淡健康，绿色蔬菜"},
                {"label": "汤品", "description": "滋补养生，温暖舒适"},
                {"label": "主食", "description": "面食米饭，饱腹感强"},
                {"label": "都可以", "description": "帮我随机推荐"}
            ],
            "multiSelect": True
        }
    ]
)
```

### 菜单规划 - 收集以下信息

```python
AskUserQuestion(
    questions=[
        {
            "question": "一共有多少人吃饭？",
            "header": "人数",
            "options": [
                {"label": "1-2人", "description": "简单家常，2-3道菜"},
                {"label": "3-4人", "description": "标准配置，4-5道菜"},
                {"label": "5-7人", "description": "丰富菜品，6-8道菜"},
                {"label": "8人以上", "description": "宴席级别，9道菜以上"}
            ],
            "multiSelect": False
        },
        {
            "question": "用餐场景是什么？",
            "header": "场景",
            "options": [
                {"label": "日常聚餐", "description": "家常菜，温馨舒适"},
                {"label": "节日宴请", "description": "硬菜为主，丰盛体面"},
                {"label": "儿童用餐", "description": "增加甜味菜，适合小朋友"},
                {"label": "老人用餐", "description": "软烂易嚼，清淡健康"}
            ],
            "multiSelect": False
        },
        {
            "question": "烹饪时间限制？",
            "header": "时间",
            "options": [
                {"label": "30分钟内", "description": "快手菜为主"},
                {"label": "1小时内", "description": "标准烹饪时间"},
                {"label": "不限", "description": "可以慢慢做"}
            ],
            "multiSelect": False
        }
    ]
)
```

### 菜谱查询

直接查询，无需额外收集信息。

---

## Phase 2: 智能筛选

使用 Python 脚本根据用户偏好筛选菜谱：

### 调用方式

```bash
cd ~/.claude/skills/howtocook/scripts
python3 -c "
import sys
sys.path.insert(0, '.')
from recipe_search import RecipeSearcher
from recipe_parser import RecipeParser

searcher = RecipeSearcher()
searcher.build_index()

# 示例: 查询难度<=2的素菜
results = searcher.multi_filter(
    categories=['vegetable_dish'],
    max_difficulty=2,
    max_time=20
)

parser = RecipeParser()
for r in results[:5]:
    print(parser.format_compact(r))
"
```

### 筛选参数映射

| 用户选择 | max_difficulty | max_time | categories |
|----------|----------------|----------|------------|
| 新手 | 2 | - | - |
| 进阶 | 4 | - | - |
| 熟练 | 8 | - | - |
| 5-10分钟 | - | 10 | - |
| 10-20分钟 | - | 20 | - |
| 20-40分钟 | - | 40 | - |
| 荤菜 | - | - | ['meat_dish'] |
| 素菜 | - | - | ['vegetable_dish'] |
| 汤品 | - | - | ['soup'] |
| 主食 | - | - | ['staple'] |

---

## Phase 3: 结果展示

### 菜谱推荐格式 (紧凑)

```
根据你的需求，推荐以下菜谱：

📍 西红柿炒鸡蛋 | 素菜 | 难度:★★ | 约20分钟
📍 酸辣土豆丝 | 素菜 | 难度:★★ | 约20分钟
📍 蒜蓉西兰花 | 素菜 | 难度:★★ | 约20分钟
📍 手撕包菜 | 素菜 | 难度:★★ | 约20分钟
📍 凉拌黄瓜 | 素菜 | 难度:★ | 约10分钟

输入菜名可查看详细做法 👆
```

### 菜谱详情格式 (详细)

```markdown
# 西红柿炒鸡蛋

**难度等级:** ★★
**分类:** 素菜
**预估时间:** 约 20 分钟

**简介:**
西红柿炒蛋是中国家常几乎最常见的一道菜肴...

**食材:**
  - 西红柿
  - 鸡蛋
  - 食用油
  - 盐
  - 糖（可选）
  - 葱花（可选）

**制作步骤:**
  1. 西红柿洗净，去蒂，切成边长不超过 4cm 的小块
  2. 将鸡蛋打入碗中，加入盐，搅匀
  3. 热锅，加入食用油
  4. 油热后，倒入鸡蛋液。翻炒至鸡蛋结为固体且颜色微微发黄
  5. 关火。将鸡蛋盛盘，重新开火
  6. 加入西红柿块，锅铲拍打并翻炒 20 秒
  7. 向锅中加入鸡蛋，翻炒均匀
  8. 加入剩余的盐、糖（可选）、葱花（可选），翻炒均匀
  9. 关火，盛盘

**小贴士:**
  - 可以考虑向鸡蛋中加入 1ml 醋，这可以去除腥味
  - 可以考虑加入 10ml 番茄酱和 50ml 清水，增加汤汁
  - 快速做法：直接在有半熟鸡蛋的锅中加入西红柿块
```

### 菜单规划格式

```markdown
# 🍽️ 推荐菜单

## 🥩 荤菜
- 📍 红烧肉 | 荤菜 | 难度:★★★ | 约35分钟
- 📍 宫保鸡丁 | 荤菜 | 难度:★★★ | 约35分钟
- 📍 糖醋排骨 | 荤菜 | 难度:★★★ | 约35分钟

## 🥬 素菜
- 📍 西红柿炒鸡蛋 | 素菜 | 难度:★★ | 约20分钟
- 📍 酸辣土豆丝 | 素菜 | 难度:★★ | 约20分钟
- 📍 蒜蓉西兰花 | 素菜 | 难度:★★ | 约20分钟

**总计: 6 道菜**

*💡 输入菜名可查看详细做法*
```

---

## Phase 4: 后续行动

展示结果后，提供以下选项：

### 选项 1: 查看详细做法
用户输入菜名 → 展示详细菜谱

### 选项 2: 推荐配菜
```bash
# 基于已选菜谱推荐互补菜品
python3 -c "
from recipe_search import RecipeSearcher
from menu_planner import MenuPlanner

searcher = RecipeSearcher()
planner = MenuPlanner(searcher)

# 获取配菜建议
current = ['西红柿炒鸡蛋']  # 已选菜品
suggestions = planner._suggest_side_dishes(current)
"
```

### 选项 3: 替代方案
提供不同难度或相似菜式的替代选择

### 选项 4: 生成购物清单
提取所有食材，生成购物清单

---

# 🧮 菜单规划算法

来自 `如何选择现在吃什么.md`：

## 基础公式

```
菜的数量 = 人数 + 1
荤菜数 = ceil((人数 + 1) / 2)
素菜数 = floor((人数 + 1) / 2)
```

## 特殊规则

1. **8人以上**: 在荤菜中增加水产类
2. **有儿童**: 增加甜味菜
3. **肉类多样性**: 避免重复使用同一种肉类
4. **肉类优先级**: 猪肉 → 鸡肉 → 牛肉 → 羊肉 → 鸭肉 → 鱼肉

## 示例

| 人数 | 总菜数 | 荤菜 | 素菜 |
|------|--------|------|------|
| 1-2人 | 2-3 | 1-2 | 1 |
| 3-4人 | 4-5 | 2-3 | 2 |
| 5-7人 | 6-8 | 3-4 | 3-4 |
| 8人+ | 9+ | 4-5+ | 4+ |

---

# 🛠️ Python 脚本使用

## recipe_search.py - 菜谱搜索

```python
from recipe_search import RecipeSearcher

searcher = RecipeSearcher()
searcher.build_index()

# 按名称搜索
results = searcher.search_by_name("西红柿")

# 按难度筛选
easy = searcher.filter_by_difficulty(max_difficulty=2)

# 按分类筛选
vegetarian = searcher.filter_by_category("vegetable_dish")

# 多维度筛选
results = searcher.multi_filter(
    categories=['vegetable_dish', 'soup'],
    max_difficulty=2,
    max_time=20
)

# 获取完整菜谱
recipe = searcher.get_recipe(recipe_name="西红柿炒鸡蛋")
```

## recipe_parser.py - 菜谱解析

```python
from recipe_parser import RecipeParser

parser = RecipeParser()

# 解析菜谱文件
recipe = parser.parse("/path/to/recipe.md")

# 格式化输出
compact = parser.format_compact(recipe)
detailed = parser.format_detailed(recipe)
```

## menu_planner.py - 菜单规划

```python
from menu_planner import MenuPlanner
from recipe_search import RecipeSearcher

searcher = RecipeSearcher()
planner = MenuPlanner(searcher)

# 规划菜单
menu = planner.plan_menu(
    people_count=4,
    max_difficulty=3,
    max_time=40,
    preferences={
        'has_children': False,
        'prefer_easy': True
    }
)

# 格式化菜单
print(planner.format_menu(menu))
```

---

# 💡 会话流程示例

## 示例 1: 菜谱推荐

```
用户: 今天晚餐吃什么？

助手: [识别为模式 A: 菜谱推荐]
      [使用 AskUserQuestion 收集偏好]

用户: [选择: 晚餐、10-20分钟、新手、素菜]

助手: [调用 Python 脚本筛选]
      [展示推荐结果]

根据你的需求，推荐以下菜谱：

📍 西红柿炒鸡蛋 | 素菜 | 难度:★★ | 约20分钟
📍 酸辣土豆丝 | 素菜 | 难度:★★ | 约20分钟
📍 凉拌黄瓜 | 素菜 | 难度:★ | 约10分钟

输入菜名可查看详细做法 👆

用户: 怎么做西红柿炒鸡蛋？

助手: [展示详细菜谱]
```

## 示例 2: 菜单规划

```
用户: 明天有4个客人来吃饭，帮我规划一下

助手: [识别为模式 C: 菜单规划]
      [使用 AskUserQuestion 收集信息]

用户: [选择: 日常聚餐、1小时内]

助手: [调用 menu_planner.py]
      [展示平衡菜单]

# 🍽️ 推荐菜单

## 🥩 荤菜
- 📍 红烧肉 | 荤菜 | 难度:★★★ | 约35分钟
- 📍 宫保鸡丁 | 荤菜 | 难度:★★★ | 约35分钟
- 📍 糖醋排骨 | 荤菜 | 难度:★★★ | 约35分钟

## 🥬 素菜
- 📍 西红柿炒鸡蛋 | 素菜 | 难度:★★ | 约20分钟
- 📍 酸辣土豆丝 | 素菜 | 难度:★★ | 约20分钟

**总计: 5 道菜**

*💡 输入菜名可查看详细做法*
```

## 示例 3: 菜谱查询

```
用户: 怎么做可乐鸡翅？

助手: [识别为模式 B: 菜谱查询]
      [直接搜索菜谱]
      [展示详细做法]

# 可乐鸡翅

**难度等级:** ★★★
**分类:** 荷菜
**预估时间:** 约 35 分钟

[详细菜谱内容...]
```

---

# 📊 技巧与最佳实践

## 搜索技巧

1. **模糊搜索**: 支持部分菜名匹配，如"西红柿"可匹配"西红柿炒鸡蛋"
2. **食材搜索**: 使用 `filter_by_ingredient()` 查找含特定食材的菜谱
3. **组合筛选**: 使用 `multi_filter()` 同时应用多个条件

## 交互技巧

1. **分步展示**: 先展示紧凑格式，用户感兴趣再展示详情
2. **合理建议**: 根据用户厨艺水平推荐适当难度的菜谱
3. **多样性**: 推荐时注意菜式多样性，避免重复

## 错误处理

1. **未找到菜谱**: 提供相似菜名建议
2. **筛选结果为空**: 放宽筛选条件重新搜索
3. **解析错误**: 跳过问题文件，继续处理其他菜谱

---

# 🔧 故障排除

## 索引构建失败

```bash
# 手动重建索引
cd ~/.claude/skills/howtocook/scripts
python3 -c "
from recipe_search import RecipeSearcher
searcher = RecipeSearcher()
searcher.build_index(force_rebuild=True)
print('索引重建完成')
"
```

## 菜谱路径错误

```python
# 指定自定义路径（可选，默认使用技能内置数据）
searcher = RecipeSearcher(cookbook_path="/custom/path/to/cookbook")
```

---

# 📝 版本信息

- **技能版本**: 1.0.0
- **菜谱数据库**: HowToCook-master
- **Python 要求**: 3.6+
- **依赖**: 仅标准库

---

# 🎉 开始使用

现在你可以使用 HowToCook 智能烹饪助手了！

试试这些问题：
- "今天晚餐吃什么？"
- "怎么做红烧肉？"
- "帮我规划6个人的聚餐菜单"
- "有什么简单易做的素菜推荐？"
