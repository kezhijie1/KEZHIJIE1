# -*- coding: utf-8 -*-
"""MBTI 人格测试 —— 单文件整合版

用法（任选其一）：
    1. 双击「启动MBTI人格测试.bat」
    2. 命令行执行：py MBTI人格测试.py

说明：
- 仅需 Python 3.8+（自带 tkinter 与 sqlite3），无需安装任何第三方库；
- 本文件把原来的 12 个模块整合在一起，按「配置 → 人格数据 → 题库 → 数据库
  → 图表 → 页面 → 主程序」分区，想修改哪块就找对应部分的代码；
- 首次运行会在本文件同目录自动生成数据库文件 mbti_data.db（历史记录、设置、
  自定义题库都保存在里面）；删除该文件即可恢复出厂状态。
"""

# ═══════════════════════════════════════════════════════════════════
# 第 1 部分：全局配置（主题颜色 / 字体 / 常量，想改外观就改这里）
# ═══════════════════════════════════════════════════════════════════

APP_NAME = "MBTI 人格测试"
APP_VERSION = "1.0"

# ---------- 字体（微软雅黑是 Windows 自带字体） ----------
FONT_TITLE = ("微软雅黑", 26, "bold")   # 大标题（首页 / 结果类型）
FONT_H1 = ("微软雅黑", 18, "bold")      # 页面标题
FONT_H2 = ("微软雅黑", 13, "bold")      # 区块标题 / 题目文字
FONT_TEXT = ("微软雅黑", 11)            # 正文
FONT_SMALL = ("微软雅黑", 9)            # 辅助小字

# ---------- 选项 ----------
OPTION_KEYS = ["A", "B", "C", "D"]
# 新增题目时 A/B/C/D 四个选项的默认文字
DEFAULT_OPTIONS = ["非常符合", "比较符合", "不太符合", "非常不符合"]

# ---------- 主题配色 ----------
# 每个主题包含这些键：
#   bg        页面背景        card  卡片背景      card_alt 浅色卡片
#   primary   主色(按钮/强调)  primary_dark 主色深色
#   accent    强调色(图表)     text  正文文字      subtext  次要文字
#   border    边框线          success 成功绿     warn 警告橙    danger 危险红
#   pie       饼图使用的 10 种颜色
THEMES = {
    "海洋蓝": {
        "bg": "#EFF4F9", "card": "#FFFFFF", "card_alt": "#F4F8FC",
        "primary": "#2E6DA4", "primary_dark": "#24547F", "accent": "#5FA8D3",
        "text": "#22313F", "subtext": "#6B7C8C", "border": "#D7E0E8",
        "success": "#2FB56B", "warn": "#E28B3D", "danger": "#D9534F",
        "pie": ["#2E6DA4", "#5FA8D3", "#2FB56B", "#E28B3D", "#D9534F",
                "#8E6BC0", "#3FBFBF", "#C05C8A", "#A0A832", "#7A8B99"],
    },
    "清新绿": {
        "bg": "#F0F7F1", "card": "#FFFFFF", "card_alt": "#F5FAF6",
        "primary": "#3D8B5F", "primary_dark": "#2E6A48", "accent": "#7CC29B",
        "text": "#23352B", "subtext": "#6D7F74", "border": "#D8E7DC",
        "success": "#2FB56B", "warn": "#E28B3D", "danger": "#D9534F",
        "pie": ["#3D8B5F", "#7CC29B", "#2E6DA4", "#E28B3D", "#C05C8A",
                "#3FBFBF", "#A0A832", "#8E6BC0", "#D9534F", "#7A8B99"],
    },
    "暖阳橙": {
        "bg": "#FBF5EE", "card": "#FFFFFF", "card_alt": "#FCF8F2",
        "primary": "#C26E2D", "primary_dark": "#9A5622", "accent": "#E0A05C",
        "text": "#3A2E22", "subtext": "#867763", "border": "#EDE0CF",
        "success": "#2FB56B", "warn": "#D98A3D", "danger": "#C94F44",
        "pie": ["#C26E2D", "#E0A05C", "#2E6DA4", "#2FB56B", "#C05C8A",
                "#8E6BC0", "#A0A832", "#3FBFBF", "#D9534F", "#7A8B99"],
    },
    "暗夜黑": {
        "bg": "#1E242B", "card": "#2A323C", "card_alt": "#232A32",
        "primary": "#4E8FC9", "primary_dark": "#3B6F9E", "accent": "#6FA8D8",
        "text": "#E6EDF3", "subtext": "#9AA8B5", "border": "#3A4652",
        "success": "#4FBF7F", "warn": "#E09A4F", "danger": "#D97066",
        "pie": ["#4E8FC9", "#6FA8D8", "#4FBF7F", "#E09A4F", "#D97066",
                "#9B7FD4", "#55C4C4", "#D47FA4", "#B3BC4E", "#8499A8"],
    },
}

DEFAULT_THEME = "海洋蓝"

# ═══════════════════════════════════════════════════════════════════
# 第 2 部分：MBTI 核心数据与计分（四维度、16 种人格资料、算分逻辑）
# ═══════════════════════════════════════════════════════════════════

# 四个维度，first 是维度第一字母（如 E/S/T/J），second 是第二字母（如 I/N/F/P）
DIMENSIONS = [
    {"key": "EI", "first": "E", "second": "I", "first_name": "外向", "second_name": "内向"},
    {"key": "SN", "first": "S", "second": "N", "first_name": "感觉", "second_name": "直觉"},
    {"key": "TF", "first": "T", "second": "F", "first_name": "思考", "second_name": "情感"},
    {"key": "JP", "first": "J", "second": "P", "first_name": "判断", "second_name": "知觉"},
]

# 图表中 8 个字母的固定展示顺序
TYPE_ORDER = "EISNTFJP"

# 16 种人格类型信息。
# 想修改某种类型的描述、优缺点或职业推荐，直接改这里即可。
TYPE_INFO = {
    "INTJ": {
        "name": "建筑师", "tagline": "独立、理性、深谋远虑的战略家",
        "desc": "独立、理性的战略家。你习惯以长远眼光看待问题，喜欢制定周密的计划，"
                "并坚定地朝着目标前进。你善于洞察复杂事物的本质，追求高效与完美。",
        "strengths": ["战略思维强，善于长远规划", "独立自律，行动力强", "洞察深刻，能看到问题本质"],
        "weaknesses": ["过于理性，显得冷漠疏离", "完美主义，对人对己要求苛刻", "不善于表达情感"],
        "jobs": "科学家、工程师、战略顾问、律师、程序员",
    },
    "INTP": {
        "name": "逻辑学家", "tagline": "好奇心旺盛的抽象思考者",
        "desc": "好奇心旺盛的逻辑学家。你热衷于探索事物的原理与规律，享受在抽象世界中思考。"
                "你重视理性，对感兴趣的问题会钻研到底。",
        "strengths": ["分析能力强，逻辑严密", "思想开放，乐于接受新观点", "求知欲旺盛，学习能力强"],
        "weaknesses": ["容易拖延，行动跟不上想法", "忽视现实细节", "社交场合较为冷淡被动"],
        "jobs": "研究员、程序员、数据分析师、教授、产品设计师",
    },
    "ENTJ": {
        "name": "指挥官", "tagline": "目标明确的天然领导者",
        "desc": "天生的指挥官。你目标明确、行动果断，擅长组织资源、带领团队实现目标。"
                "你相信效率与结果，是天生的领导者。",
        "strengths": ["决断力强，敢于拍板", "善于统筹规划与组织协调", "自信坚定，抗压能力强"],
        "weaknesses": ["过于强势固执", "缺乏耐心，容易催促他人", "有时忽视他人感受"],
        "jobs": "企业家、管理者、律师、项目经理、投资分析师",
    },
    "ENTP": {
        "name": "辩论家", "tagline": "思维敏捷的创意挑战者",
        "desc": "思维敏捷的辩论家。你喜欢挑战常规，从不同角度分析问题，并享受思想碰撞的乐趣。"
                "创意和可能性让你充满动力。",
        "strengths": ["创意十足，点子层出不穷", "反应敏捷，善于即兴发挥", "口才好，善于说服他人"],
        "weaknesses": ["三分钟热度，难以坚持", "喜欢抬杠，容易引发争论", "对执行细节缺乏耐心"],
        "jobs": "创业者、产品经理、律师、营销策划、主持人",
    },
    "INFJ": {
        "name": "提倡者", "tagline": "富有远见的理想主义者",
        "desc": "富有远见的提倡者。你内心坚定，追求意义与价值，善于洞察他人的内心世界。"
                "你希望让世界变得更好，并愿意为之默默付出。",
        "strengths": ["同理心强，善解人意", "信念坚定，有使命感", "洞察深刻，能看透人心"],
        "weaknesses": ["过于敏感，容易受伤", "完美主义，自我要求过高", "过度付出，容易疲惫"],
        "jobs": "心理咨询师、作家、教师、公益工作者、人力资源",
    },
    "INFP": {
        "name": "调停者", "tagline": "温柔坚定的理想主义者",
        "desc": "温柔理想主义的调停者。你重视内心的价值观，追求真实与善良。"
                "你想象力丰富，常沉浸在文学、艺术与理想的世界中。",
        "strengths": ["真诚善良，富有同情心", "想象力丰富，有创造力", "包容开放，尊重差异"],
        "weaknesses": ["过于理想化，容易失望", "行动力弱，难以开始", "情绪敏感，容易内耗"],
        "jobs": "作家、设计师、心理咨询师、翻译、艺术家",
    },
    "ENFJ": {
        "name": "主人公", "tagline": "热情洋溢的引路人",
        "desc": "热情洋溢的主人公。你善于沟通与激励，总能发现他人的闪光点。"
                "你乐于帮助他人成长，是天生的组织者与引路人。",
        "strengths": ["感染力强，善于鼓舞人心", "沟通能力出色", "乐于奉献，责任感强"],
        "weaknesses": ["过于在意他人评价", "爱操心，事必躬亲", "容易忽略自身需求"],
        "jobs": "教师、培训师、公关、人力资源管理、心理咨询师",
    },
    "ENFP": {
        "name": "竞选者", "tagline": "自由热情的可能性探索者",
        "desc": "自由热情的竞选者。你对世界充满好奇，喜欢探索各种可能性。"
                "你热情乐观，能用自己的活力感染身边的人。",
        "strengths": ["热情乐观，感染力强", "创意丰富，联想能力强", "善于社交，人缘好"],
        "weaknesses": ["注意力容易分散", "难以坚持长期计划", "情绪起伏较大"],
        "jobs": "记者、市场营销、创意策划、培训师、创业者",
    },
    "ISTJ": {
        "name": "物流师", "tagline": "严谨可靠的秩序守护者",
        "desc": "严谨可靠的物流师。你重视秩序、责任与传统，做事一丝不苟。"
                "你的可靠与踏实让身边的人都感到安心。",
        "strengths": ["可靠严谨，值得信赖", "执行力强，有始有终", "条理清晰，注重细节"],
        "weaknesses": ["固执保守，不喜变化", "不擅变通，容易死板", "过于严肃，缺少幽默"],
        "jobs": "会计师、审计师、公务员、质检员、运营管理",
    },
    "ISFJ": {
        "name": "守卫者", "tagline": "温暖细心的守护者",
        "desc": "温暖细心的守卫者。你默默关心身边的人，用实际行动守护你在乎的一切。"
                "你温和踏实，是团队中最可靠的支柱。",
        "strengths": ["体贴周到，细心可靠", "踏实勤恳，任劳任怨", "忠诚重情，值得托付"],
        "weaknesses": ["不善于拒绝别人", "习惯压抑自己的情绪", "害怕变化，回避风险"],
        "jobs": "护士、教师、行政人员、客服、社会工作者",
    },
    "ESTJ": {
        "name": "总经理", "tagline": "务实高效的规则执行者",
        "desc": "务实高效的总经理。你崇尚规则与效率，善于组织和管理。"
                "你果断务实，是天生的管理者与执行者。",
        "strengths": ["组织管理能力强", "果断务实，讲究效率", "责任感强，说到做到"],
        "weaknesses": ["固执强势，难以接受异议", "不够灵活，缺少弹性", "对他人要求过高"],
        "jobs": "管理者、军官、财务总监、运营总监、法官",
    },
    "ESFJ": {
        "name": "执政官", "tagline": "热心周到的社交核心",
        "desc": "热心周到的执政官。你重视和谐的人际关系，乐于为他人提供帮助。"
                "你亲和力强，总能把大家凝聚在一起。",
        "strengths": ["亲和力强，人缘极好", "乐于助人，无私奉献", "组织协调能力强"],
        "weaknesses": ["过于在意别人的评价", "缺乏主见，容易随大流", "情绪易受外界影响"],
        "jobs": "教师、销售、护士、人事专员、社区服务",
    },
    "ISTP": {
        "name": "鉴赏家", "tagline": "冷静灵活的实干家",
        "desc": "冷静灵活的鉴赏家。你喜欢动手探索事物的运作原理，遇到问题总能冷静地找到解决办法。"
                "你崇尚自由，活在当下。",
        "strengths": ["动手能力强，善于实操", "冷静理性，临危不乱", "灵活应变，适应力强"],
        "weaknesses": ["沉默寡言，难以接近", "缺乏耐心，容易厌倦", "回避长期规划"],
        "jobs": "工程师、机械师、飞行员、程序员、运动员",
    },
    "ISFP": {
        "name": "探险家", "tagline": "温和随性的生活艺术家",
        "desc": "温和随性的探险家。你对美有敏锐的感知，喜欢用自己的方式体验生活。"
                "你随和包容，享受宁静而真实的生活。",
        "strengths": ["审美出色，有艺术天赋", "随和包容，与世无争", "观察敏锐，感受细腻"],
        "weaknesses": ["缺乏长远规划", "不善于表达自己", "回避冲突，容易逃避"],
        "jobs": "设计师、摄影师、厨师、美容师、音乐人",
    },
    "ESTP": {
        "name": "企业家", "tagline": "精力充沛的行动派",
        "desc": "精力充沛的企业家。你是天生的行动派，善于抓住机会、随机应变。"
                "你热爱挑战，喜欢在实战中证明自己。",
        "strengths": ["应变能力强，行动迅速", "务实果断，不拖泥带水", "社交出色，人脉广"],
        "weaknesses": ["冲动冒险，考虑不周", "缺乏耐心，难以坚持", "忽视规则，喜欢走捷径"],
        "jobs": "销售、创业者、运动员、警察、房地产经纪",
    },
    "ESFP": {
        "name": "表演者", "tagline": "热情开朗的快乐源泉",
        "desc": "热情开朗的表演者。你热爱生活，享受聚光灯下的每一刻。"
                "你的乐观与活力总能给身边的人带来快乐。",
        "strengths": ["热情友好，感染力强", "适应力强，随遇而安", "乐观开朗，善于活跃气氛"],
        "weaknesses": ["缺乏规划，走一步看一步", "容易冲动消费", "回避严肃的话题"],
        "jobs": "演员、主持人、导游、幼教、销售",
    },
}


def compute_result(questions, answers):
    """根据题目与答案计算 MBTI 结果。

    参数：
        questions: 题目列表，每题为 {"id", "dim", "direction", "text", "options"}
        answers:   答案字典 {题目id: "A"/"B"/"C"/"D"}
    返回：
        result 字典，包含 mbti、type_name、tagline、desc、strengths、weaknesses、
        jobs、letters（每维度选出的字母）、scores（8 个字母得分）、percents（每维度第一字母百分比）
    """
    scores = {"E": 0, "I": 0, "S": 0, "N": 0, "T": 0, "F": 0, "J": 0, "P": 0}

    for q in questions:
        ans = answers.get(q["id"])
        if ans not in OPTION_KEYS:
            continue
        idx = OPTION_KEYS.index(ans)
        dim = next(d for d in DIMENSIONS if d["key"] == q["dim"])
        # direction=1: A/B 给第一字母加分, C/D 给第二字母加分
        # direction=0: 反过来
        if q["direction"] == 1:
            points = [2, 1, -1, -2]
        else:
            points = [-2, -1, 1, 2]
        p = points[idx]
        letter = dim["first"] if p > 0 else dim["second"]
        scores[letter] += abs(p)

    letters, percents = {}, {}
    for d in DIMENSIONS:
        a, b = scores[d["first"]], scores[d["second"]]
        letters[d["key"]] = d["first"] if a >= b else d["second"]
        percents[d["key"]] = round(a * 100 / (a + b)) if a + b > 0 else 50

    mbti = "".join(letters[d["key"]] for d in DIMENSIONS)
    info = TYPE_INFO.get(mbti, TYPE_INFO["INTJ"])
    return {
        "mbti": mbti,
        "type_name": info["name"],
        "tagline": info["tagline"],
        "desc": info["desc"],
        "strengths": info["strengths"],
        "weaknesses": info["weaknesses"],
        "jobs": info["jobs"],
        "letters": letters,
        "scores": scores,
        "percents": percents,
    }


def result_from_record(record):
    """把数据库中的一条历史记录还原成结果字典（用于历史详情页）。"""
    info = TYPE_INFO.get(record["mbti"], TYPE_INFO["INTJ"])
    return {
        "mbti": record["mbti"],
        "type_name": info["name"],
        "tagline": info["tagline"],
        "desc": info["desc"],
        "strengths": info["strengths"],
        "weaknesses": info["weaknesses"],
        "jobs": info["jobs"],
        "letters": {"EI": record["ei"], "SN": record["sn"],
                    "TF": record["tf"], "JP": record["jp"]},
        "scores": {"E": record["e"], "I": record["i"], "S": record["s"], "N": record["n"],
                   "T": record["t"], "F": record["f"], "J": record["j"], "P": record["p"]},
        "percents": {"EI": record["ei_pct"], "SN": record["sn_pct"],
                     "TF": record["tf_pct"], "JP": record["jp_pct"]},
    }

# ═══════════════════════════════════════════════════════════════════
# 第 3 部分：默认题库（32 题，每维度 8 题）
# ═══════════════════════════════════════════════════════════════════

DEFAULT_QUESTIONS = [
    # ---------- EI：外向 / 内向 ----------
    {"id": 1, "dim": "EI", "direction": 1, "text": "在聚会中，我更愿意主动认识新朋友。"},
    {"id": 2, "dim": "EI", "direction": 0, "text": "独处时，我能更快恢复精力。"},
    {"id": 3, "dim": "EI", "direction": 1, "text": "我喜欢成为人群中的焦点。"},
    {"id": 4, "dim": "EI", "direction": 0, "text": "我倾向于先想清楚再表达，而不是边说边想。"},
    {"id": 5, "dim": "EI", "direction": 1, "text": "与朋友外出活动比待在家里更让我兴奋。"},
    {"id": 6, "dim": "EI", "direction": 0, "text": "长时间社交后，我需要独处来充电。"},
    {"id": 7, "dim": "EI", "direction": 1, "text": "我通常很快能和陌生人打开话题。"},
    {"id": 8, "dim": "EI", "direction": 0, "text": "比起群体热闹，我更享受一对一的深入交流。"},

    # ---------- SN：感觉 / 直觉 ----------
    {"id": 9, "dim": "SN", "direction": 1, "text": "我更关注事情的细节和具体事实。"},
    {"id": 10, "dim": "SN", "direction": 0, "text": "我经常沉浸在对未来的想象中。"},
    {"id": 11, "dim": "SN", "direction": 1, "text": "比起理论，我更相信亲身实践的经验。"},
    {"id": 12, "dim": "SN", "direction": 0, "text": "我喜欢思考事物的可能性和深层含义。"},
    {"id": 13, "dim": "SN", "direction": 1, "text": "我习惯按部就班地完成事情。"},
    {"id": 14, "dim": "SN", "direction": 0, "text": "我常常有突如其来的灵感和新点子。"},
    {"id": 15, "dim": "SN", "direction": 1, "text": "我更喜欢照着说明书的具体步骤操作，而不是自己摸索。"},
    {"id": 16, "dim": "SN", "direction": 0, "text": "我喜欢用比喻和联想来表达想法。"},

    # ---------- TF：思考 / 情感 ----------
    {"id": 17, "dim": "TF", "direction": 1, "text": "做决定时，我优先考虑逻辑和客观标准。"},
    {"id": 18, "dim": "TF", "direction": 0, "text": "他人的感受会影响我的决定。"},
    {"id": 19, "dim": "TF", "direction": 1, "text": "我认为分清对错比维持和谐更重要。"},
    {"id": 20, "dim": "TF", "direction": 0, "text": "我很容易察觉并照顾他人的情绪。"},
    {"id": 21, "dim": "TF", "direction": 1, "text": "指出问题时，我会直截了当，不太绕弯子。"},
    {"id": 22, "dim": "TF", "direction": 0, "text": "我宁愿委屈自己，也不愿伤害别人的感情。"},
    {"id": 23, "dim": "TF", "direction": 1, "text": "我更欣赏理性、有条理的分析。"},
    {"id": 24, "dim": "TF", "direction": 0, "text": "看到感人的故事，我很容易动情。"},

    # ---------- JP：判断 / 知觉 ----------
    {"id": 25, "dim": "JP", "direction": 1, "text": "我喜欢提前制定计划并严格执行。"},
    {"id": 26, "dim": "JP", "direction": 0, "text": "比起按计划行事，我更享受随机应变。"},
    {"id": 27, "dim": "JP", "direction": 1, "text": "我的书桌和房间通常被收拾得井井有条。"},
    {"id": 28, "dim": "JP", "direction": 0, "text": "截止日期临近时，我才会爆发出最高效率。"},
    {"id": 29, "dim": "JP", "direction": 1, "text": "我喜欢事情有明确的安排和结论。"},
    {"id": 30, "dim": "JP", "direction": 0, "text": "我常常同时进行好几件事，并乐在其中。"},
    {"id": 31, "dim": "JP", "direction": 1, "text": "旅行前，我会做详细的攻略。"},
    {"id": 32, "dim": "JP", "direction": 0, "text": "计划赶不上变化，所以我很少做长远规划。"},
]

# ═══════════════════════════════════════════════════════════════════
# 第 4 部分：SQLite 数据库（设置 / 历史记录 / 题库三张表）
# ═══════════════════════════════════════════════════════════════════

import json
import os
import sqlite3
from datetime import datetime



class Database:
    """所有数据库操作的唯一入口。页面通过 app.db 使用它。"""

    def __init__(self, path=None):
        if path is None:
            path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "mbti_data.db")
        self.path = path
        self.conn = sqlite3.connect(path)
        self.conn.row_factory = sqlite3.Row
        self._create_tables()

    def _create_tables(self):
        cur = self.conn.cursor()
        cur.execute("""CREATE TABLE IF NOT EXISTS settings(
            key TEXT PRIMARY KEY, value TEXT)""")
        cur.execute("""CREATE TABLE IF NOT EXISTS records(
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nickname TEXT, mbti TEXT, type_name TEXT,
            ei TEXT, sn TEXT, tf TEXT, jp TEXT,
            e INT, i INT, s INT, n INT, t INT, f INT, j INT, p INT,
            ei_pct INT, sn_pct INT, tf_pct INT, jp_pct INT,
            answers TEXT, created_at TEXT)""")
        cur.execute("""CREATE TABLE IF NOT EXISTS questions(
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            dim TEXT, direction INTEGER, text TEXT,
            opt_a TEXT, opt_b TEXT, opt_c TEXT, opt_d TEXT)""")
        # 首次运行时题库为空，写入默认题库
        cur.execute("SELECT COUNT(*) AS c FROM questions")
        if cur.fetchone()["c"] == 0:
            self.reset_questions()
        self.conn.commit()

    # ---------- 设置 ----------
    def get_setting(self, key, default=None):
        """读取设置项，不存在时返回 default。"""
        row = self.conn.execute("SELECT value FROM settings WHERE key=?", (key,)).fetchone()
        return row["value"] if row else default

    def set_setting(self, key, value):
        """写入设置项（存在则更新）。"""
        self.conn.execute(
            "INSERT INTO settings(key,value) VALUES(?,?) "
            "ON CONFLICT(key) DO UPDATE SET value=excluded.value", (key, str(value)))
        self.conn.commit()

    # ---------- 历史记录 ----------
    def add_record(self, result, nickname="", answers=None):
        """保存一次测试结果，返回新记录 id。result 为 compute_result() 的返回值。"""
        p, s, l = result["percents"], result["scores"], result["letters"]
        now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        # 列名与值一一对应，占位符数量用 len(values) 自动生成，避免数错
        columns = ("nickname,mbti,type_name,ei,sn,tf,jp,"
                   "e,i,s,n,t,f,j,p,ei_pct,sn_pct,tf_pct,jp_pct,answers,created_at")
        values = (nickname, result["mbti"], result["type_name"],
                  l["EI"], l["SN"], l["TF"], l["JP"],
                  s["E"], s["I"], s["S"], s["N"], s["T"], s["F"], s["J"], s["P"],
                  p["EI"], p["SN"], p["TF"], p["JP"],
                  json.dumps(answers or {}, ensure_ascii=False), now)
        placeholders = ",".join(["?"] * len(values))
        cur = self.conn.execute(
            "INSERT INTO records(%s) VALUES(%s)" % (columns, placeholders), values)
        self.conn.commit()
        return cur.lastrowid

    def get_records(self):
        """返回全部历史记录（新的在前），每条为字典，字段见 records 表结构。"""
        rows = self.conn.execute("SELECT * FROM records ORDER BY id DESC").fetchall()
        return [dict(r) for r in rows]

    def get_record(self, rid):
        """按 id 取一条记录，answers 字段已解析为字典；不存在返回 None。"""
        row = self.conn.execute("SELECT * FROM records WHERE id=?", (rid,)).fetchone()
        if row is None:
            return None
        rec = dict(row)
        rec["answers"] = json.loads(rec["answers"] or "{}")
        return rec

    def delete_record(self, rid):
        self.conn.execute("DELETE FROM records WHERE id=?", (rid,))
        self.conn.commit()

    def clear_records(self):
        self.conn.execute("DELETE FROM records")
        self.conn.commit()

    # ---------- 题库 ----------
    def get_questions(self):
        """返回题库列表，每题为 {"id","dim","direction","text","options":{"A".."D"}}。"""
        rows = self.conn.execute("SELECT * FROM questions ORDER BY id").fetchall()
        questions = []
        for r in rows:
            questions.append({
                "id": r["id"], "dim": r["dim"], "direction": r["direction"],
                "text": r["text"],
                "options": {"A": r["opt_a"], "B": r["opt_b"],
                            "C": r["opt_c"], "D": r["opt_d"]},
            })
        return questions

    def save_question(self, q):
        """保存题目。q 含 id 时更新该题，否则新增；返回题目 id。"""
        o = q["options"]
        vals = (q["dim"], q["direction"], q["text"], o["A"], o["B"], o["C"], o["D"])
        if q.get("id"):
            self.conn.execute(
                "UPDATE questions SET dim=?,direction=?,text=?,opt_a=?,opt_b=?,opt_c=?,opt_d=? "
                "WHERE id=?", vals + (q["id"],))
            self.conn.commit()
            return q["id"]
        cur = self.conn.execute(
            "INSERT INTO questions(dim,direction,text,opt_a,opt_b,opt_c,opt_d) "
            "VALUES(?,?,?,?,?,?,?)", vals)
        self.conn.commit()
        return cur.lastrowid

    def delete_question(self, qid):
        self.conn.execute("DELETE FROM questions WHERE id=?", (qid,))
        self.conn.commit()

    def reset_questions(self):
        """清空题库并恢复为默认 32 题。"""
        self.conn.execute("DELETE FROM questions")
        for q in DEFAULT_QUESTIONS:
            o = dict(zip(OPTION_KEYS, DEFAULT_OPTIONS))
            self.conn.execute(
                "INSERT INTO questions(id,dim,direction,text,opt_a,opt_b,opt_c,opt_d) "
                "VALUES(?,?,?,?,?,?,?,?)",
                (q["id"], q["dim"], q["direction"], q["text"], o["A"], o["B"], o["C"], o["D"]))
        self.conn.commit()

    def close(self):
        self.conn.close()

# ═══════════════════════════════════════════════════════════════════
# 第 5 部分：图表绘制（雷达图 / 饼图 / 柱状图 / 横向条形图 / 折线图）
# ═══════════════════════════════════════════════════════════════════

import math

_CHART_TITLE_FONT = ("微软雅黑", 12, "bold")
_AXIS_FONT = ("微软雅黑", 8)
_LABEL_FONT = ("微软雅黑", 9)


def _text(canvas, x, y, s, theme, anchor="n", fill=None, font=None):
    """画一段文字的小工具。"""
    return canvas.create_text(x, y, text=s, font=font or _LABEL_FONT,
                              anchor=anchor, fill=fill or theme["text"])


def draw_radar(canvas, title, labels, values, theme, w, h):
    """雷达图：labels 与 values 等长（建议 8 个），values 取值 0~100。"""
    canvas.delete("all")
    n = len(labels)
    if n == 0:
        return
    cx, cy = w / 2, h / 2 + (12 if title else 0)
    r = min(w, h) / 2 - 48

    # 背景网格：5 圈同心多边形 + 从圆心发出的轴线
    for level in range(1, 6):
        pts = []
        for i in range(n):
            ang = math.radians(-90 + i * 360 / n)
            pts += [cx + r * level / 5 * math.cos(ang),
                    cy + r * level / 5 * math.sin(ang)]
        canvas.create_polygon(pts, outline=theme["border"], fill="")
    for i in range(n):
        ang = math.radians(-90 + i * 360 / n)
        canvas.create_line(cx, cy, cx + r * math.cos(ang),
                           cy + r * math.sin(ang), fill=theme["border"])

    # 数据多边形（stipple 让填充半透明，能看见网格）
    pts = []
    for i, v in enumerate(values):
        ang = math.radians(-90 + i * 360 / n)
        rr = r * max(0.0, min(100.0, float(v))) / 100
        pts += [cx + rr * math.cos(ang), cy + rr * math.sin(ang)]
    if len(pts) >= 6:
        canvas.create_polygon(pts, fill=theme["accent"], outline=theme["primary"],
                              stipple="gray50", width=2)

    # 顶点标签：字母 + 百分比
    for i, (lab, v) in enumerate(zip(labels, values)):
        ang = math.radians(-90 + i * 360 / n)
        lx, ly = cx + (r + 16) * math.cos(ang), cy + (r + 16) * math.sin(ang)
        anchor = "n" if ly < cy - 4 else ("s" if ly > cy + 4 else "w")
        _text(canvas, lx, ly, "%s %d%%" % (lab, v), theme, anchor=anchor)

    if title:
        _text(canvas, cx, 14, title, theme, font=_CHART_TITLE_FONT)


def draw_pie(canvas, items, theme, w, h, title=""):
    """饼图：items 为 [(标签, 数值), ...]，自动忽略数值 <= 0 的项，右侧画图例。"""
    canvas.delete("all")
    valid = [(l, v) for l, v in items if v and v > 0]
    if not valid:
        _text(canvas, w / 2, h / 2, "暂无数据", theme)
        return
    total = sum(v for _, v in valid)

    # 饼画在左侧，图例画在右侧
    cx, cy, r = w * 0.30, h / 2, min(w * 0.26, h / 2 - 24)
    start = 90
    for idx, (label, v) in enumerate(valid):
        extent = -360.0 * v / total
        color = theme["pie"][idx % len(theme["pie"])]
        canvas.create_arc(cx - r, cy - r, cx + r, cy + r, start=start, extent=extent,
                          fill=color, outline=theme["card"])
        start += extent

    lx = cx + r + 24
    ly = (24 if title else 12) + 4
    for idx, (label, v) in enumerate(valid):
        color = theme["pie"][idx % len(theme["pie"])]
        pct = v / total * 100
        canvas.create_rectangle(lx, ly, lx + 12, ly + 12, fill=color, outline="")
        _text(canvas, lx + 18, ly + 6, "%s  %d次 (%.0f%%)" % (label, v, pct),
              theme, anchor="w")
        ly += 24

    if title:
        _text(canvas, w / 2, 14, title, theme, font=_CHART_TITLE_FONT)


def draw_bars(canvas, title, labels, values, theme, w, h, color=None):
    """竖向柱状图：labels 与 values 等长，柱顶显示数值，底部显示标签。"""
    canvas.delete("all")
    if not labels:
        _text(canvas, w / 2, h / 2, "暂无数据", theme)
        return
    n = len(labels)
    left, right = 46, w - 20
    top, bottom = (30 if title else 16), h - 36
    canvas.create_line(left, bottom, right, bottom, fill=theme["border"])

    vmax = max(max(values), 1) * 1.15
    slot = (right - left) / n
    bw = min(slot * 0.55, 46)
    fill_color = color or theme["primary"]
    for i, (lab, v) in enumerate(zip(labels, values)):
        x = left + slot * i + slot / 2
        bh = (bottom - top) * v / vmax
        canvas.create_rectangle(x - bw / 2, bottom - bh, x + bw / 2, bottom,
                                fill=fill_color, outline="")
        _text(canvas, x, bottom - bh - 8, str(round(v)), theme, anchor="s")
        _text(canvas, x, bottom + 6, str(lab), theme, anchor="n", font=_AXIS_FONT)

    if title:
        _text(canvas, (left + right) / 2, 12, title, theme, font=_CHART_TITLE_FONT)


def draw_hbars(canvas, pairs, theme, w, h):
    """横向条形图：pairs 为 [(标签, 百分比0~100), ...]，适合展示维度占比。"""
    canvas.delete("all")
    if not pairs:
        return
    row_h = min(34, max(10, (h - 8) / len(pairs)))
    y = 4
    for lab, pct in pairs:
        mid_y = y + row_h / 2
        _text(canvas, 8, mid_y, lab, theme, anchor="w")
        tx, tw = 96, w - 96 - 52
        canvas.create_rectangle(tx, mid_y - 6, tx + tw, mid_y + 6,
                                fill=theme["card_alt"], outline=theme["border"])
        fill_w = tw * max(0.0, min(100.0, float(pct))) / 100
        canvas.create_rectangle(tx, mid_y - 6, tx + fill_w, mid_y + 6,
                                fill=theme["accent"], outline="")
        _text(canvas, tx + tw + 8, mid_y, "%d%%" % pct, theme,
              anchor="w", fill=theme["subtext"])
        y += row_h


def draw_line(canvas, title, xlabels, values, theme, w, h):
    """折线图：values 为数值序列（0~100 效果最好），xlabels 为等长的横轴标签。"""
    canvas.delete("all")
    if not values:
        _text(canvas, w / 2, h / 2, "暂无数据", theme)
        return
    left, right = 44, w - 24
    top, bottom = (30 if title else 16), h - 34
    canvas.create_line(left, bottom, right, bottom, fill=theme["border"])

    vmax, vmin = max(max(values), 1), min(min(values), 0)
    span = (vmax - vmin) or 1
    n = len(values)
    xs = [left + (right - left) * i / max(n - 1, 1) for i in range(n)]

    def y_of(v):
        return bottom - (bottom - top) * (v - vmin) / span

    pts = [(xs[i], y_of(v)) for i, v in enumerate(values)]
    if n > 1:
        canvas.create_line(*[c for p in pts for c in p],
                           fill=theme["primary"], width=2, smooth=(n >= 4))
    for i, (x, y) in enumerate(pts):
        canvas.create_oval(x - 3, y - 3, x + 3, y + 3,
                           fill=theme["primary"], outline=theme["card"])
        _text(canvas, x, y - 10, str(round(values[i])), theme, anchor="s", font=_AXIS_FONT)
        _text(canvas, x, bottom + 6, str(xlabels[i]), theme, anchor="n", font=_AXIS_FONT)

    if title:
        _text(canvas, (left + right) / 2, 12, title, theme, font=_CHART_TITLE_FONT)

# ═══════════════════════════════════════════════════════════════════
# 第 6 部分：页面一：首页
# ═══════════════════════════════════════════════════════════════════


class HomePage:
    """应用首页：大标题 + 简介卡 + 上次结果卡 + 底部功能按钮。"""

    def __init__(self, app, parent, **kwargs):
        self.app = app
        self.t = app.theme

        # 页面根容器：所有控件都放进 self.frame
        self.frame = tk.Frame(parent, bg=self.t["bg"])
        self.frame.pack(fill="both", expand=True)

        # ---------- 顶部大标题与副标题 ----------
        self.app.label(self.frame, APP_NAME, font=FONT_TITLE,
                       bg=self.t["bg"], fg=self.t["primary"]).pack(pady=(48, 4))
        self.app.label(self.frame, "了解自己，从这里开始", font=FONT_TEXT,
                       bg=self.t["bg"], fg=self.t["subtext"]).pack(pady=(0, 28))

        # ---------- MBTI 简介卡 ----------
        intro_card = self.app.card(self.frame)
        intro_card.pack(fill="x", padx=40, pady=(0, 20))
        self.app.label(intro_card, "什么是 MBTI？", font=FONT_H2,
                       fg=self.t["text"]).pack(anchor="w", padx=20, pady=(16, 6))
        self.app.label(
            intro_card,
            "MBTI（迈尔斯-布里格斯类型指标）是一套经典的人格分类工具，它从四个维度"
            "描述人的行为偏好，两两组合成 16 种人格类型。\n"
            "通过回答一系列贴近日常的选择题，你可以了解自己的性格倾向、天赋优势以及"
            "适合自己的职业方向。",
            font=FONT_TEXT, bg=self.t["card"], fg=self.t["text"],
            justify="left", wraplength=760).pack(anchor="w", padx=20, pady=(0, 10))
        # 四个维度各一行小字（数据取自 mbti_types.DIMENSIONS）
        for d in DIMENSIONS:
            self.app.label(
                intro_card,
                "%s %s / %s %s" % (d["first_name"], d["first"], d["second_name"], d["second"]),
                font=FONT_SMALL, bg=self.t["card"], fg=self.t["subtext"]
            ).pack(anchor="w", padx=20)
        # 底部留白
        self.app.label(intro_card, "", bg=self.t["card"]).pack(pady=8)

        # ---------- 上次测试结果卡 ----------
        # 优先用 app.last_result（本次会话刚测的结果），否则取数据库最新一条记录
        rec = None
        if self.app.last_result is not None:
            text = "上次测试：%s %s" % (self.app.last_result["mbti"],
                                       self.app.last_result["type_name"])
            records = self.app.db.get_records()
            if records:
                rec = records[0]
                text += "（%s）" % rec["created_at"]
        else:
            records = self.app.db.get_records()
            if records:
                rec = records[0]
                text = "上次测试：%s %s（%s）" % (rec["mbti"], rec["type_name"],
                                                 rec["created_at"])
            else:
                text = "还没有测试记录，快来测一测吧"

        last_card = self.app.card(self.frame)
        last_card.pack(fill="x", padx=40, pady=(0, 24))
        self.app.label(last_card, "上次测试结果", font=FONT_H2,
                       fg=self.t["text"]).pack(anchor="w", padx=20, pady=(16, 4))
        row = tk.Frame(last_card, bg=self.t["card"])
        row.pack(fill="x", padx=20, pady=(0, 16))
        self.app.label(row, text, font=FONT_TEXT,
                       bg=self.t["card"], fg=self.t["text"]).pack(side="left")
        if rec is not None:
            # 查看详情：结果页用 record 还原历史记录，save=False 表示不重复入库
            self.app.button(
                row, "查看详情",
                lambda r=rec: self.app.show_page("result", record=r, save=False),
                kind="ghost").pack(side="right")

        # ---------- 底部操作区 ----------
        # 开始测试：加宽的 primary 大按钮
        self.app.button(self.frame, "开始测试",
                        lambda: self.app.show_page("test"),
                        kind="primary", width=20).pack(pady=(0, 10))
        # 并排三个 ghost 按钮：历史记录 / 统计图表 / 设置
        nav = tk.Frame(self.frame, bg=self.t["bg"])
        nav.pack(pady=(0, 40))
        self.app.button(nav, "历史记录",
                        lambda: self.app.show_page("history"),
                        kind="ghost").pack(side="left", padx=6)
        self.app.button(nav, "统计图表",
                        lambda: self.app.show_page("stats"),
                        kind="ghost").pack(side="left", padx=6)
        self.app.button(nav, "设置",
                        lambda: self.app.show_page("settings"),
                        kind="ghost").pack(side="left", padx=6)

    def destroy(self):
        """销毁页面根容器（供 App.show_page 切换页面时调用）。"""
        self.frame.destroy()

# ═══════════════════════════════════════════════════════════════════
# 第 7 部分：页面二：答题
# ═══════════════════════════════════════════════════════════════════

import random
import tkinter as tk



class TestPage:
    """MBTI 答题页：顶部导航 + 进度条 + 题目卡 + 选项 + 上一题/下一题。"""

    def __init__(self, app, parent, **kwargs):
        self.app = app
        self.t = app.theme

        # 页面根容器
        self.frame = tk.Frame(parent, bg=self.t["bg"])
        self.frame.pack(fill="both", expand=True)

        # 取题库并打乱副本（不影响数据库原始顺序）
        self.questions = list(app.db.get_questions())
        random.shuffle(self.questions)
        self.idx = 0                # 当前题下标
        self.answers = {}           # {题目id: "A"/"B"/"C"/"D"}
        self._progress_ratio = 0.0  # 当前进度比例，供进度条重绘使用

        # ---------- 题库为空：居中提示 + 返回首页 ----------
        if not self.questions:
            self.app.label(self.frame, "题库为空，请到设置中添加题目",
                           font=FONT_TEXT, bg=self.t["bg"],
                           fg=self.t["subtext"]).pack(expand=True)
            back_btn = self.app.button(self.frame, "返回首页",
                                       lambda: self.app.show_page("home"),
                                       kind="ghost")
            back_btn.config(bg=self.t["bg"])
            back_btn.pack(pady=(0, 80))
            return

        # ---------- 顶部导航：标题 + 返回首页 ----------
        nav = tk.Frame(self.frame, bg=self.t["bg"])
        nav.pack(fill="x", padx=40, pady=(24, 14))
        self.app.label(nav, "MBTI 测试", font=FONT_H1,
                       bg=self.t["bg"], fg=self.t["text"]).pack(side="left")
        home_btn = self.app.button(nav, "返回首页", self._quit_test, kind="ghost")
        home_btn.config(bg=self.t["bg"])  # 贴合页面背景色
        home_btn.pack(side="right")

        # ---------- 进度区：文字 + Canvas 进度条 ----------
        progress = tk.Frame(self.frame, bg=self.t["bg"])
        progress.pack(fill="x", padx=40, pady=(0, 12))
        self._progress_label = self.app.label(progress, "", font=FONT_TEXT,
                                              bg=self.t["bg"], fg=self.t["subtext"])
        self._progress_label.pack(anchor="w")
        self._progress_canvas = tk.Canvas(progress, height=8,
                                          bg=self.t["bg"], highlightthickness=0)
        self._progress_canvas.pack(fill="x", pady=(4, 0))
        # 窗口尺寸变化时按当前比例重绘进度条
        self._progress_canvas.bind("<Configure>", self._redraw_progress)

        # ---------- 题目卡 ----------
        card = self.app.card(self.frame)
        card.pack(fill="both", expand=True, padx=40, pady=(0, 14))
        self._dim_label = self.app.label(card, "", font=FONT_SMALL,
                                         fg=self.t["subtext"])
        self._dim_label.pack(anchor="w", padx=20, pady=(14, 4))
        self._question_label = self.app.label(card, "", font=FONT_H2,
                                              fg=self.t["text"],
                                              justify="left", wraplength=700)
        self._question_label.pack(anchor="w", padx=20, pady=(0, 12))

        # 4 个选项按钮：手写选中态（普通态白底黑字，选中态主色底白字）
        self.opt_buttons = []
        for key in OPTION_KEYS:
            btn = tk.Button(card, text="", font=FONT_TEXT,
                            anchor="w", justify="left",
                            relief="flat", cursor="hand2", highlightthickness=0,
                            padx=16, pady=9,
                            bg=self.t["card"], fg=self.t["text"],
                            activebackground=self.t["card_alt"],
                            activeforeground=self.t["text"],
                            command=lambda k=key: self._choose(k))
            btn.pack(fill="x", padx=20, pady=4)
            self.opt_buttons.append(btn)

        # ---------- 底部按钮行 ----------
        bottom = tk.Frame(self.frame, bg=self.t["bg"])
        bottom.pack(fill="x", padx=40, pady=(0, 24))
        self._prev_btn = self.app.button(bottom, "上一题",
                                         self._prev, kind="ghost")
        self._prev_btn.pack(side="left")
        self._next_btn = self.app.button(bottom, "下一题",
                                         self._next, kind="primary")
        self._next_btn.pack(side="right")

        # 渲染第 1 题
        self._refresh()

    # ---------- 交互逻辑 ----------
    def _quit_test(self):
        """返回首页前二次确认，避免误触丢失进度。"""
        if self.app.confirm("退出测试", "退出将丢失本次答题进度，确定退出吗？"):
            self.app.show_page("home")

    def _choose(self, key):
        """选择选项：记录答案并刷新 4 个按钮的选中态（不自动跳题）。"""
        q = self.questions[self.idx]
        self.answers[q["id"]] = key
        self._update_options()

    def _prev(self):
        """上一题。"""
        if self.idx > 0:
            self.idx -= 1
            self._refresh()

    def _next(self):
        """下一题；最后一题时执行交卷。"""
        if self.idx < len(self.questions) - 1:
            self.idx += 1
            self._refresh()
        else:
            self._submit()

    def _submit(self):
        """交卷：检查是否全部作答，通过后计算结果并跳转结果页。"""
        n = sum(1 for q in self.questions if q["id"] not in self.answers)
        if n > 0:
            self.app.info("提示", "还有 %d 题未作答，请完成后再交卷" % n)
            return
        r = compute_result(self.questions, self.answers)
        self.app.last_result = r
        self.app.show_page("result", result=r,
                           answers=dict(self.answers), save=True)

    # ---------- 界面刷新 ----------
    def _refresh(self):
        """切题时统一刷新：进度、题目、选项与按钮状态。"""
        total = len(self.questions)
        q = self.questions[self.idx]

        # 进度文字与进度条比例
        self._progress_label.config(text="第 %d / %d 题" % (self.idx + 1, total))
        self._progress_ratio = (self.idx + 1) / total
        self._redraw_progress()

        # 维度小字与题目文本
        dim = next(d for d in DIMENSIONS if d["key"] == q["dim"])
        self._dim_label.config(
            text="维度：%s %s / %s %s" % (dim["first_name"], dim["first"],
                                         dim["second_name"], dim["second"]))
        self._question_label.config(text=q["text"])

        # 选项文字与选中态
        self._update_options()

        # 上一题禁用态 / 下一题文字（最后一题显示「交卷」）
        self._prev_btn.config(state="normal" if self.idx > 0 else "disabled")
        self._next_btn.config(text="交卷" if self.idx == total - 1 else "下一题")

    def _update_options(self):
        """刷新 4 个选项按钮的文字与选中态样式。"""
        q = self.questions[self.idx]
        chosen = self.answers.get(q["id"])
        for key, btn in zip(OPTION_KEYS, self.opt_buttons):
            btn.config(text="%s. %s" % (key.upper(), q["options"][key]))
            if key == chosen:
                # 选中态：主色底 + 白字
                btn.config(bg=self.t["primary"], fg="#FFFFFF",
                           activebackground=self.t["primary_dark"],
                           activeforeground="#FFFFFF")
            else:
                # 普通态：卡片底 + 正文色
                btn.config(bg=self.t["card"], fg=self.t["text"],
                           activebackground=self.t["card_alt"],
                           activeforeground=self.t["text"])

    def _redraw_progress(self, event=None):
        """按当前比例重绘进度条：先画整条底，再画主色填充。"""
        canvas = self._progress_canvas
        canvas.delete("all")
        w = canvas.winfo_width()
        h = canvas.winfo_height()
        if w <= 1 or h <= 1:
            return
        # 整条底（border 色）
        canvas.create_rectangle(0, 0, w, h, fill=self.t["border"], outline="")
        # 按 (idx+1)/total 比例填充 primary 色
        fw = w * max(0.0, min(1.0, self._progress_ratio))
        if fw > 0:
            canvas.create_rectangle(0, 0, fw, h, fill=self.t["primary"], outline="")

    def destroy(self):
        """销毁页面根容器。"""
        self.frame.destroy()

# ═══════════════════════════════════════════════════════════════════
# 第 8 部分：页面三：测试结果
# ═══════════════════════════════════════════════════════════════════



class ResultPage:
    """结果页：左侧结果卡展示类型信息，右侧图表卡展示雷达图与维度条形图。"""

    def __init__(self, app, parent, result=None, answers=None, save=False, record=None):
        self.app = app
        self.t = app.theme

        # 从历史记录打开时，把记录还原成结果字典（优先于 result 参数）
        if record is not None:
            result = result_from_record(record)
        # 兜底：都没有时使用最近一次测试结果
        if result is None:
            result = app.last_result

        # 页面根框架：全部控件都放进 self.frame
        self.frame = tk.Frame(parent, bg=self.t["bg"])
        self.frame.pack(fill="both", expand=True)

        self._build_nav()

        # 自动保存提示行：显示在顶部导航下方
        if save:
            self.app.label(self.frame, "✔ 已自动保存到历史记录", font=FONT_TEXT,
                           bg=self.t["bg"], fg=self.t["success"]).pack(pady=(0, 4))

        self._build_body(result)
        self._build_buttons()

        # save=True 时在 __init__ 末尾执行一次自动保存（避免重复入库）
        if save:
            self.app.db.add_record(result, nickname=self.app.last_nickname,
                                   answers=answers)

    def destroy(self):
        """销毁页面所有控件。"""
        self.frame.destroy()

    # ---------- 顶部导航 ----------
    def _build_nav(self):
        nav = tk.Frame(self.frame, bg=self.t["bg"])
        nav.pack(fill="x", padx=24, pady=(18, 8))
        self.app.label(nav, "测试结果", font=FONT_H1, bg=self.t["bg"]).pack(side="left")
        # 顶部 ghost 按钮与页面背景同色
        back_btn = self.app.button(nav, "返回首页", lambda: self.app.show_page("home"),
                                   kind="ghost")
        back_btn.configure(bg=self.t["bg"], activebackground=self.t["bg"])
        back_btn.pack(side="right")

    # ---------- 主体：左右两列 ----------
    def _build_body(self, result):
        body = tk.Frame(self.frame, bg=self.t["bg"])
        body.pack(fill="both", expand=True, padx=24, pady=(0, 12))
        # 左侧约 46% 宽（结果卡），右侧剩余宽度（图表卡）
        body.grid_columnconfigure(0, weight=46)
        body.grid_columnconfigure(1, weight=54)
        body.grid_rowconfigure(0, weight=1)

        left = self.app.card(body)
        left.grid(row=0, column=0, sticky="nsew", padx=(0, 12))
        self._build_left_card(left, result)

        right = self.app.card(body)
        right.grid(row=0, column=1, sticky="nsew")
        self._build_right_card(right, result)

    # ---------- 左卡：类型详情 ----------
    def _build_left_card(self, card, result):
        # 类型大字（主色）
        self.app.label(card, result["mbti"], font=FONT_TITLE,
                       fg=self.t["primary"]).pack(pady=(18, 2))
        # 「类型名称 · tagline」
        self.app.label(card, "%s · %s" % (result["type_name"], result["tagline"]),
                       font=FONT_H2, fg=self.t["subtext"]).pack(pady=(0, 12))
        # 性格描述
        self.app.label(card, result["desc"], font=FONT_TEXT, wraplength=400,
                       justify="left").pack(padx=20, pady=(0, 12))
        # 优点 / 缺点
        self._build_bullets(card, "优点", result["strengths"])
        self._build_bullets(card, "缺点", result["weaknesses"])
        # 适合职业
        self.app.label(card, "适合职业", font=FONT_H2).pack(anchor="w", padx=20, pady=(8, 2))
        self.app.label(card, result["jobs"], font=FONT_TEXT, wraplength=400,
                       justify="left").pack(anchor="w", padx=28, pady=(0, 16))

    def _build_bullets(self, card, title, items):
        """标题 + 若干「• 内容」行。"""
        self.app.label(card, title, font=FONT_H2).pack(anchor="w", padx=20, pady=(8, 2))
        for item in items:
            self.app.label(card, "• %s" % item, font=FONT_TEXT).pack(anchor="w", padx=28)

    # ---------- 右卡：图表 ----------
    def _build_right_card(self, card, result):
        labels, values = self._radar_data(result)

        # 八维倾向雷达图：绑定 <Configure>，尺寸变化时用最新宽高重绘
        self.radar_canvas = tk.Canvas(card, height=300, bg=self.t["card"],
                                      highlightthickness=0, bd=0)
        self.radar_canvas.pack(fill="x", padx=12, pady=(12, 0))
        self.radar_canvas.bind("<Configure>",
                               lambda e: draw_radar(e.widget, "八维倾向雷达图", labels,
                                                    values, self.t, e.width, e.height))

        # 四维占比横向条形图：label「中文名 字母 / 中文名 字母」，
        # pct 取该维度第一字母（E/S/T/J）的百分比
        pairs = [("%s %s / %s %s" % (d["first_name"], d["first"],
                                     d["second_name"], d["second"]),
                  result["percents"][d["key"]]) for d in DIMENSIONS]
        self.hbar_canvas = tk.Canvas(card, height=150, bg=self.t["card"],
                                     highlightthickness=0, bd=0)
        self.hbar_canvas.pack(fill="x", padx=12, pady=12)
        self.hbar_canvas.bind("<Configure>",
                              lambda e: draw_hbars(e.widget, pairs, self.t,
                                                   e.width, e.height))

    def _radar_data(self, result):
        """按 TYPE_ORDER 计算 8 个字母在各自维度内的百分比（除零保护 → 50）。"""
        scores = result["scores"]
        # 字母 -> 所属维度
        dim_of = {}
        for d in DIMENSIONS:
            dim_of[d["first"]] = d
            dim_of[d["second"]] = d
        labels, values = [], []
        for letter in TYPE_ORDER:
            d = dim_of[letter]
            total = scores[d["first"]] + scores[d["second"]]
            # 维度总分为 0 时（异常数据）取 50，避免除零
            values.append(round(scores[letter] * 100.0 / total) if total else 50)
            labels.append(letter)
        return labels, values

    # ---------- 底部按钮 ----------
    def _build_buttons(self):
        bar = tk.Frame(self.frame, bg=self.t["bg"])
        bar.pack(fill="x", padx=24, pady=(0, 16))
        self.app.button(bar, "再来一次", lambda: self.app.show_page("test")).pack(side="left")
        # 先 pack 的靠右：返回首页在最右，查看历史在其左侧
        self.app.button(bar, "返回首页", lambda: self.app.show_page("home"),
                        kind="ghost").pack(side="right")
        self.app.button(bar, "查看历史", lambda: self.app.show_page("history"),
                        kind="ghost").pack(side="right", padx=(0, 8))

# ═══════════════════════════════════════════════════════════════════
# 第 9 部分：页面四：历史记录
# ═══════════════════════════════════════════════════════════════════

import csv



class HistoryPage:
    """历史记录页。Treeview 的主题样式由 main.py 统一配置，本页不再修改。"""

    # 表格列：(列 id, 表头, 列宽)
    COLUMNS = (("time", "时间", 150), ("nick", "昵称", 100), ("mbti", "类型", 60),
               ("name", "类型名称", 90), ("ei", "EI", 70), ("sn", "SN", 70),
               ("tf", "TF", 70), ("jp", "JP", 70))

    # CSV 导出表头（维度字母 + 8 个字母得分）
    CSV_HEADER = ("时间", "昵称", "类型", "类型名称", "EI", "SN", "TF", "JP",
                  "外向分", "内向分", "感觉分", "直觉分", "思考分", "情感分", "判断分", "知觉分")

    def __init__(self, app, parent, **kwargs):
        self.app = app
        self.t = app.theme

        # 页面根框架：全部控件都放进 self.frame
        self.frame = tk.Frame(parent, bg=self.t["bg"])
        self.frame.pack(fill="both", expand=True)

        self._build_nav()
        self._build_toolbar()
        self._build_list()
        self._refresh()

    def destroy(self):
        """销毁页面所有控件。"""
        self.frame.destroy()

    # ---------- 顶部导航 ----------
    def _build_nav(self):
        nav = tk.Frame(self.frame, bg=self.t["bg"])
        nav.pack(fill="x", padx=24, pady=(18, 8))
        self.app.label(nav, "历史记录", font=FONT_H1, bg=self.t["bg"]).pack(side="left")
        # 顶部 ghost 按钮与页面背景同色
        back_btn = self.app.button(nav, "返回首页", lambda: self.app.show_page("home"),
                                   kind="ghost")
        back_btn.configure(bg=self.t["bg"], activebackground=self.t["bg"])
        back_btn.pack(side="right")

    # ---------- 工具行 ----------
    def _build_toolbar(self):
        bar = tk.Frame(self.frame, bg=self.t["bg"])
        bar.pack(fill="x", padx=24, pady=(0, 10))
        self.app.button(bar, "查看详情", self._view_detail).pack(side="left")
        # 先 pack 的靠右：导出CSV 最右，清空历史、删除选中依次在左
        self.app.button(bar, "导出CSV", self._export_csv, kind="ghost").pack(side="right")
        self.app.button(bar, "清空历史", self._clear_all, kind="danger").pack(
            side="right", padx=(0, 8))
        self.app.button(bar, "删除选中", self._delete_selected, kind="danger").pack(
            side="right", padx=(0, 8))

    # ---------- 记录列表 ----------
    def _build_list(self):
        # 列表容器：Treeview + 垂直滚动条 + 空态提示
        wrap = tk.Frame(self.frame, bg=self.t["bg"])
        wrap.pack(fill="both", expand=True, padx=24, pady=(0, 16))

        cols = [c[0] for c in self.COLUMNS]
        self.tree = ttk.Treeview(wrap, columns=cols, show="headings")
        for cid, title, width in self.COLUMNS:
            self.tree.heading(cid, text=title)
            self.tree.column(cid, width=width, anchor="center")
        self.tree.column("time", anchor="w")  # 时间列靠左更易读

        sb = ttk.Scrollbar(wrap, orient="vertical", command=self.tree.yview)
        self.tree.configure(yscrollcommand=sb.set)
        self.tree.pack(side="left", fill="both", expand=True)
        sb.pack(side="right", fill="y")

        # 双击行 = 查看详情
        self.tree.bind("<Double-1>", lambda e: self._view_detail())

        # 空态提示：列表为空时居中显示
        self.empty_lbl = self.app.label(wrap, "暂无历史记录，快去完成一次测试吧",
                                        font=FONT_TEXT, fg=self.t["subtext"])

    def _refresh(self):
        """重新读取数据库并刷新列表，同时维护空态提示。"""
        for iid in self.tree.get_children():
            self.tree.delete(iid)
        records = self.app.db.get_records()
        for rec in records:
            # 行 iid 隐藏保存记录 id，选中时直接取出
            self.tree.insert("", "end", iid=str(rec["id"]), values=(
                rec["created_at"], rec["nickname"], rec["mbti"], rec["type_name"],
                "%s %d%%" % (rec["ei"], rec["ei_pct"]),
                "%s %d%%" % (rec["sn"], rec["sn_pct"]),
                "%s %d%%" % (rec["tf"], rec["tf_pct"]),
                "%s %d%%" % (rec["jp"], rec["jp_pct"]),
            ))
        if records:
            self.empty_lbl.place_forget()
        else:
            self.empty_lbl.place(relx=0.5, rely=0.5, anchor="center")

    def _selected_rid(self):
        """返回当前选中记录 id；未选中返回 None。"""
        sel = self.tree.selection()
        return int(sel[0]) if sel else None

    # ---------- 查看详情 ----------
    def _view_detail(self):
        """跳到结果页展示选中记录（record 模式打开，不重复保存）。"""
        rid = self._selected_rid()
        if rid is None:
            self.app.info("提示", "请先在列表中选择一条记录")
            return
        rec = self.app.db.get_record(rid)
        if rec is None:
            self._refresh()
            return
        self.app.show_page("result", record=rec, save=False)

    # ---------- 删除选中 ----------
    def _delete_selected(self):
        rid = self._selected_rid()
        if rid is None:
            self.app.info("提示", "请先在列表中选择一条记录")
            return
        if self.app.confirm("删除记录", "确定删除这条测试记录吗？"):
            self.app.db.delete_record(rid)
            self._refresh()

    # ---------- 清空历史 ----------
    def _clear_all(self):
        if self.app.confirm("清空历史", "确定删除全部测试记录吗？此操作不可恢复！"):
            self.app.db.clear_records()
            self._refresh()

    # ---------- 导出 CSV ----------
    def _export_csv(self):
        """把全部记录导出为 CSV（utf-8-sig 编码，Excel 打开不乱码）。"""
        path = filedialog.asksaveasfilename(
            defaultextension=".csv", filetypes=[("CSV 文件", "*.csv")])
        if not path:
            return  # 用户取消选择
        records = self.app.db.get_records()
        with open(path, "w", encoding="utf-8-sig", newline="") as f:
            writer = csv.writer(f)
            writer.writerow(self.CSV_HEADER)
            for rec in records:
                writer.writerow((
                    rec["created_at"], rec["nickname"], rec["mbti"], rec["type_name"],
                    rec["ei"], rec["sn"], rec["tf"], rec["jp"],
                    rec["e"], rec["i"], rec["s"], rec["n"],
                    rec["t"], rec["f"], rec["j"], rec["p"]))
        self.app.info("导出成功", "已导出到 %s" % path)

# ═══════════════════════════════════════════════════════════════════
# 第 10 部分：页面五：统计图表
# ═══════════════════════════════════════════════════════════════════

import tkinter as tk
from collections import Counter



class StatsPage:
    """统计图表页面。"""

    def __init__(self, app, parent, **kwargs):
        self.app = app
        self.t = app.theme
        t = self.t

        # 页面容器：所有控件都放进 self.frame
        self.frame = tk.Frame(parent, bg=t["bg"])
        self.frame.pack(fill="both", expand=True)

        # 顶部导航
        header = tk.Frame(self.frame, bg=t["bg"])
        header.pack(fill="x", padx=24, pady=(16, 8))
        app.label(header, "统计图表", font=FONT_H1, bg=t["bg"]).pack(side="left")
        app.button(header, "返回首页", lambda: app.show_page("home"),
                   kind="ghost").pack(side="right")

        # 没有历史数据时居中提示后直接返回
        recs = app.db.get_records()
        if not recs:
            app.label(self.frame, "暂无数据，快去完成一次测试吧",
                      font=FONT_TEXT, bg=t["bg"], fg=t["subtext"]).pack(expand=True)
            return

        # ---- 顶部三张统计卡（并排等宽） ----
        counter = Counter(r["mbti"] for r in recs)
        mbti, _ = counter.most_common(1)[0]          # 出现次数最多的类型
        mbti_info = TYPE_INFO.get(mbti)
        mbti_name = mbti_info["name"] if mbti_info else ""

        cards = tk.Frame(self.frame, bg=t["bg"])
        cards.pack(fill="x", padx=24, pady=(0, 12))
        for i in range(3):
            cards.columnconfigure(i, weight=1, uniform="stat")

        # 卡1：累计测试次数
        card1 = app.card(cards)
        card1.grid(row=0, column=0, sticky="nsew", padx=(0, 6))
        app.label(card1, "累计测试", font=FONT_SMALL, fg=t["subtext"]).pack(
            anchor="w", padx=14, pady=(10, 2))
        app.label(card1, "%d 次" % len(recs), font=FONT_H2).pack(
            anchor="w", padx=14, pady=(0, 10))

        # 卡2：最常见类型（类型字母 + 中文名）
        card2 = app.card(cards)
        card2.grid(row=0, column=1, sticky="nsew", padx=6)
        app.label(card2, "最常见类型", font=FONT_SMALL, fg=t["subtext"]).pack(
            anchor="w", padx=14, pady=(10, 2))
        app.label(card2, "%s（%s）" % (mbti, mbti_name), font=FONT_H2).pack(
            anchor="w", padx=14, pady=(0, 10))

        # 卡3：最近一次测试时间（记录已是倒序，第 0 条即最新）
        card3 = app.card(cards)
        card3.grid(row=0, column=2, sticky="nsew", padx=(6, 0))
        app.label(card3, "最近测试", font=FONT_SMALL, fg=t["subtext"]).pack(
            anchor="w", padx=14, pady=(10, 2))
        app.label(card3, recs[0]["created_at"], font=FONT_H2).pack(
            anchor="w", padx=14, pady=(0, 10))

        # ---- 第一行：饼图 + 柱状图（各约一半宽） ----
        # 饼图数据：[(类型, 次数), ...] 按次数降序
        pie_items = sorted(counter.items(), key=lambda kv: kv[1], reverse=True)

        # 柱状图数据：8 个字母，每个字母的值为"所有记录中该字母占比的平均值"。
        # 每对互补字母（E/I、S/N、T/F、J/P）的对应关系来自 DIMENSIONS。
        comp = {}
        for d in DIMENSIONS:
            comp[d["first"]] = d["second"]
            comp[d["second"]] = d["first"]
        letters = ["E", "I", "S", "N", "T", "F", "J", "P"]
        bar_values = []
        for letter in letters:
            total, cnt = 0.0, 0
            key, other = letter.lower(), comp[letter].lower()
            for r in recs:
                a, b = r[key] or 0, r[other] or 0
                if a + b > 0:                          # 除零保护
                    total += a * 100.0 / (a + b)
                    cnt += 1
            bar_values.append(round(total / cnt, 1) if cnt else 0)

        row1 = tk.Frame(self.frame, bg=t["bg"])
        row1.pack(fill="both", expand=True, padx=24, pady=(0, 12))
        row1.columnconfigure(0, weight=1, uniform="chart")
        row1.columnconfigure(1, weight=1, uniform="chart")
        row1.rowconfigure(0, weight=1)

        pie_card = app.card(row1)
        pie_card.grid(row=0, column=0, sticky="nsew", padx=(0, 6))
        pie_canvas = self._chart_canvas(pie_card, 250)
        pie_canvas.bind("<Configure>", lambda e: draw_pie(
            pie_canvas, pie_items, t, e.width, e.height, title="人格类型分布"))

        bar_card = app.card(row1)
        bar_card.grid(row=0, column=1, sticky="nsew", padx=(6, 0))
        bar_canvas = self._chart_canvas(bar_card, 250)
        bar_canvas.bind("<Configure>", lambda e: draw_bars(
            bar_canvas, "各维度倾向平均占比", letters, bar_values,
            t, e.width, e.height))

        # ---- 第二行：折线图（整行宽） ----
        # 记录是倒序的，先反转为时间正序，只取最近 12 条
        latest = list(reversed(recs))[-12:]
        line_xlabels = [r["created_at"][5:10] for r in latest]   # 截取 "MM-DD"
        line_values = [r["ei_pct"] for r in latest]

        line_card = app.card(self.frame)
        line_card.pack(fill="x", padx=24, pady=(0, 16))
        line_canvas = self._chart_canvas(line_card, 200)
        line_canvas.bind("<Configure>", lambda e: draw_line(
            line_canvas, "外向程度(E%)变化趋势", line_xlabels, line_values,
            t, e.width, e.height))

    def _chart_canvas(self, parent, height):
        """在卡片内创建一张铺满可用空间的画布。"""
        canvas = tk.Canvas(parent, bg=self.t["card"],
                           highlightthickness=0, height=height)
        canvas.pack(fill="both", expand=True, padx=10, pady=10)
        return canvas

    def destroy(self):
        """销毁页面。"""
        self.frame.destroy()

# ═══════════════════════════════════════════════════════════════════
# 第 11 部分：页面六：设置（含题库管理对话框）
# ═══════════════════════════════════════════════════════════════════

import tkinter as tk
from tkinter import ttk


# 维度显示名与 key 的映射，由 DIMENSIONS 生成，保证与核心模块一致
DIM_CHOICES = [
    "%s（%s/%s）" % (d["key"], d["first_name"], d["second_name"]) for d in DIMENSIONS
]
DIM_MAP = dict(zip(DIM_CHOICES, (d["key"] for d in DIMENSIONS)))
DIM_KEY_TO_NAME = {v: k for k, v in DIM_MAP.items()}


class SettingsPage:
    """设置页面：昵称、主题、题库与数据管理。"""

    def __init__(self, app, parent, **kwargs):
        self.app = app
        self.t = app.theme
        t = self.t

        # 页面容器：所有控件都放进 self.frame
        self.frame = tk.Frame(parent, bg=t["bg"])
        self.frame.pack(fill="both", expand=True)

        # 顶部导航
        header = tk.Frame(self.frame, bg=t["bg"])
        header.pack(fill="x", padx=24, pady=(16, 8))
        app.label(header, "设置", font=FONT_H1, bg=t["bg"]).pack(side="left")
        app.button(header, "返回首页", lambda: app.show_page("home"),
                   kind="ghost").pack(side="right")

        # ---- 区块1：个人设置 ----
        card = app.card(self.frame)
        card.pack(fill="x", padx=24, pady=(0, 12))
        app.label(card, "个人设置", font=FONT_H2).pack(anchor="w", padx=14, pady=(12, 6))
        row = tk.Frame(card, bg=t["card"])
        row.pack(fill="x", padx=14, pady=(0, 12))
        app.label(row, "默认昵称", bg=t["card"]).pack(side="left")
        self.nick_entry = tk.Entry(row, font=FONT_TEXT, bg=t["card_alt"],
                                   fg=t["text"], insertbackground=t["text"],
                                   relief="flat", highlightthickness=1,
                                   highlightbackground=t["border"])
        self.nick_entry.pack(side="left", fill="x", expand=True, padx=10)
        self.nick_entry.insert(0, app.db.get_setting("nickname", ""))
        app.button(row, "保存昵称", self._save_nickname, kind="primary").pack(side="left")

        # ---- 区块2：外观主题 ----
        card = app.card(self.frame)
        card.pack(fill="x", padx=24, pady=(0, 12))
        app.label(card, "外观主题", font=FONT_H2).pack(anchor="w", padx=14, pady=(12, 2))
        app.label(card, "切换主题后立即生效并自动保存", font=FONT_SMALL,
                  fg=t["subtext"]).pack(anchor="w", padx=14)
        btns = tk.Frame(card, bg=t["card"])
        btns.pack(fill="x", padx=14, pady=(6, 12))
        for name in THEMES:
            # 当前主题用 primary 高亮，其余用 ghost
            kind = "primary" if name == app.theme_name else "ghost"
            app.button(btns, name, lambda n=name: self._switch_theme(n),
                       kind=kind).pack(side="left", padx=(0, 8))

        # ---- 区块3：题库管理 ----
        card = app.card(self.frame)
        card.pack(fill="x", padx=24, pady=(0, 12))
        app.label(card, "题库管理", font=FONT_H2).pack(anchor="w", padx=14, pady=(12, 2))
        app.label(card, "可新增、编辑、删除题目；每道题都能自定义 A/B/C/D 四个选项的文字。",
                  font=FONT_SMALL, fg=t["subtext"]).pack(anchor="w", padx=14)
        body = tk.Frame(card, bg=t["card"])
        body.pack(fill="x", padx=14, pady=(8, 14))
        # 左侧题目列表
        self.listbox = tk.Listbox(body, font=FONT_TEXT, height=8,
                                  bg=t["card_alt"], fg=t["text"],
                                  selectbackground=t["primary"],
                                  selectforeground="#FFFFFF",
                                  relief="flat", highlightthickness=1,
                                  highlightbackground=t["border"],
                                  activestyle="none", exportselection=False)
        self.listbox.pack(side="left", fill="both", expand=True)
        # 右侧操作按钮列
        side = tk.Frame(body, bg=t["card"])
        side.pack(side="left", fill="y", padx=(10, 0))
        app.button(side, "新增题目", lambda: QuestionDialog(app, self),
                   kind="primary").pack(fill="x", pady=(0, 6))
        app.button(side, "编辑选中", self._edit_question,
                   kind="ghost").pack(fill="x", pady=(0, 6))
        app.button(side, "删除选中", self._delete_question,
                   kind="danger").pack(fill="x", pady=(0, 6))
        app.button(side, "恢复默认题库", self._reset_questions,
                   kind="danger").pack(fill="x")
        self.refresh()

        # ---- 区块4：数据管理 ----
        card = app.card(self.frame)
        card.pack(fill="x", padx=24, pady=(0, 16))
        app.label(card, "数据管理", font=FONT_H2).pack(anchor="w", padx=14, pady=(12, 4))
        row = tk.Frame(card, bg=t["card"])
        row.pack(fill="x", padx=14, pady=(0, 12))
        app.button(row, "清空历史记录", self._clear_records,
                   kind="danger").pack(side="left")
        app.label(row, "数据库文件：%s" % app.db.path, font=FONT_SMALL,
                  fg=t["subtext"], bg=t["card"]).pack(side="left", padx=(12, 0))

    # ---------- 各区块的操作回调 ----------
    def _save_nickname(self):
        """保存默认昵称到数据库并同步到 app。"""
        v = self.nick_entry.get().strip()
        self.app.db.set_setting("nickname", v)
        self.app.last_nickname = v
        self.app.info("提示", "昵称已保存")

    def _switch_theme(self, name):
        """切换主题（自动保存）后重建本页面，让新配色立即生效。"""
        self.app.apply_theme(name)
        self.app.show_page("settings")

    def _selected_question(self):
        """返回列表当前选中的题目；未选中时提示并返回 None。"""
        sel = self.listbox.curselection()
        if not sel:
            self.app.info("提示", "请先在左侧列表选中一道题目")
            return None
        return self.questions[sel[0]]

    def _edit_question(self):
        """弹出对话框编辑选中题目。"""
        q = self._selected_question()
        if q is not None:
            QuestionDialog(self.app, self, question=q)

    def _delete_question(self):
        """确认后删除选中题目并刷新列表。"""
        q = self._selected_question()
        if q is None:
            return
        if not self.app.confirm("确认删除", "确定要删除第 %d 题吗？" % q["id"]):
            return
        self.app.db.delete_question(q["id"])
        self.refresh()

    def _reset_questions(self):
        """确认后恢复默认题库并刷新列表。"""
        if not self.app.confirm("确认恢复", "确定要恢复默认题库吗？自定义的题目将被全部覆盖。"):
            return
        self.app.db.reset_questions()
        self.refresh()

    def _clear_records(self):
        """确认后清空全部历史记录。"""
        if not self.app.confirm("确认清空", "确定要清空全部历史记录吗？此操作不可恢复。"):
            return
        self.app.db.clear_records()
        self.app.info("提示", "历史记录已清空")

    def refresh(self):
        """从数据库重新加载题库并刷新左侧列表。"""
        self.questions = self.app.db.get_questions()
        self.listbox.delete(0, "end")
        for q in self.questions:
            self.listbox.insert("end", "%d. [%s] %s" % (q["id"], q["dim"], q["text"]))

    def destroy(self):
        """销毁页面。"""
        self.frame.destroy()


class QuestionDialog:
    """新增 / 编辑题目的模态对话框。question 为 None 表示新增。"""

    def __init__(self, app, parent_page, question=None):
        self.app = app
        self.parent_page = parent_page
        self.question = question
        t = app.theme

        # 模态窗口
        self.win = tk.Toplevel(app.root)
        self.win.title("编辑题目" if question else "新增题目")
        self.win.geometry("520x420")
        self.win.configure(bg=t["card"])
        self.win.resizable(False, False)
        self.win.grab_set()

        # 维度下拉框：编辑时按 question["dim"] 反查显示名
        app.label(self.win, "维度").grid(row=0, column=0, sticky="e",
                                         padx=(16, 8), pady=(16, 6))
        self.dim_var = tk.StringVar()
        self.dim_var.set(DIM_KEY_TO_NAME.get(question["dim"], DIM_CHOICES[0])
                         if question else DIM_CHOICES[0])
        ttk.Combobox(self.win, textvariable=self.dim_var, values=DIM_CHOICES,
                     state="readonly", font=FONT_TEXT).grid(
            row=0, column=1, sticky="w", pady=(16, 6))

        # 方向单选：1 表示 A/B 倾向第一字母，0 表示倾向第二字母
        app.label(self.win, "方向").grid(row=1, column=0, sticky="e",
                                         padx=(16, 8), pady=6)
        self.dir_var = tk.IntVar(value=question["direction"] if question else 1)
        dir_frame = tk.Frame(self.win, bg=t["card"])
        dir_frame.grid(row=1, column=1, sticky="w", pady=6)
        radio_kw = {"bg": t["card"], "fg": t["text"], "selectcolor": t["accent"],
                    "activebackground": t["card"]}
        tk.Radiobutton(dir_frame, text="正向：A/B 倾向第一字母(E/S/T/J)",
                       variable=self.dir_var, value=1, **radio_kw).pack(anchor="w")
        tk.Radiobutton(dir_frame, text="反向：A/B 倾向第二字母(I/N/F/P)",
                       variable=self.dir_var, value=0, **radio_kw).pack(anchor="w")

        # 题目内容多行文本框
        app.label(self.win, "题目内容").grid(row=2, column=0, sticky="ne",
                                             padx=(16, 8), pady=6)
        self.text_widget = tk.Text(self.win, height=4, width=50, font=FONT_TEXT,
                                   bg=t["card_alt"], fg=t["text"],
                                   insertbackground=t["text"], relief="flat",
                                   highlightthickness=1, highlightbackground=t["border"])
        if question:
            self.text_widget.insert("1.0", question["text"])
        self.text_widget.grid(row=2, column=1, sticky="w", pady=6)

        # 选项 A~D：默认用 DEFAULT_OPTIONS，编辑时填原选项文字
        self.opt_vars = {}
        for i, key in enumerate(OPTION_KEYS):
            default = question["options"][key] if question else DEFAULT_OPTIONS[i]
            app.label(self.win, "选项%s" % key).grid(row=3 + i, column=0,
                                                     sticky="e", padx=(16, 8), pady=4)
            var = tk.StringVar(value=default)
            self.opt_vars[key] = var
            tk.Entry(self.win, textvariable=var, width=40, font=FONT_TEXT,
                     bg=t["card_alt"], fg=t["text"], insertbackground=t["text"],
                     relief="flat", highlightthickness=1,
                     highlightbackground=t["border"]).grid(
                row=3 + i, column=1, sticky="w", pady=4)

        # 底部按钮
        btns = tk.Frame(self.win, bg=t["card"])
        btns.grid(row=7, column=0, columnspan=2, pady=(12, 16))
        app.button(btns, "保存", self._save, kind="primary").pack(side="left", padx=(0, 8))
        app.button(btns, "取消", self.destroy, kind="ghost").pack(side="left")

    def _save(self):
        """校验表单后保存题目，刷新列表并关闭对话框。"""
        app = self.app
        text = self.text_widget.get("1.0", "end").strip()
        options = {k: v.get().strip() for k, v in self.opt_vars.items()}
        # 题目内容与四个选项都不能为空
        if not text or any(not v for v in options.values()):
            app.info("提示", "题目内容和 A/B/C/D 四个选项都不能为空")
            return
        q = {
            "id": self.question["id"] if self.question else None,
            "dim": DIM_MAP[self.dim_var.get()],
            "direction": self.dir_var.get(),
            "text": text,
            "options": options,
        }
        app.db.save_question(q)
        self.parent_page.refresh()
        self.destroy()

    def destroy(self):
        """关闭对话框。"""
        self.win.destroy()

# ═══════════════════════════════════════════════════════════════════
# 第 12 部分：主程序：窗口、主题与页面导航
# ═══════════════════════════════════════════════════════════════════

import os
import tkinter as tk
from tkinter import messagebox, ttk



# 页面注册表：导航名 -> 页面类。新增页面时在这里登记即可。
PAGE_CLASSES = {
    "home": HomePage,
    "test": TestPage,
    "result": ResultPage,
    "history": HistoryPage,
    "stats": StatsPage,
    "settings": SettingsPage,
}


class App:
    """应用主体：持有根窗口、数据库与当前主题，提供页面切换和通用控件工厂。"""

    def __init__(self, root):
        self.root = root
        self.db = Database()

        # 读取上次保存的主题与昵称
        self.theme_name = self.db.get_setting("theme", DEFAULT_THEME)
        if self.theme_name not in THEMES:
            self.theme_name = DEFAULT_THEME
        self.theme = THEMES[self.theme_name]
        self.last_nickname = self.db.get_setting("nickname", "")
        self.last_result = None          # 最近一次测试结果（跨页面共享）
        self.page = None                 # 当前页面对象
        self.page_name = None

        root.title("%s v%s" % (APP_NAME, APP_VERSION))
        root.geometry("960x680")
        root.minsize(900, 620)
        root.configure(bg=self.theme["bg"])
        self._apply_ttk_style()
        self.show_page("home")

    # ---------- 主题 ----------
    def apply_theme(self, theme_name):
        """切换主题：更新配色、ttk 样式并持久化。当前页面如需立即换色，调用方自行重建页面。"""
        self.theme_name = theme_name
        self.theme = THEMES[theme_name]
        self.db.set_setting("theme", theme_name)
        self.root.configure(bg=self.theme["bg"])
        self._apply_ttk_style()

    def _apply_ttk_style(self):
        """让 Treeview（表格）等 ttk 控件跟随主题配色。"""
        t = self.theme
        style = ttk.Style()
        style.theme_use("clam")
        style.configure("Treeview", background=t["card"], fieldbackground=t["card"],
                        foreground=t["text"], rowheight=28, borderwidth=0)
        style.configure("Treeview.Heading", background=t["card_alt"],
                        foreground=t["text"], font=FONT_SMALL, relief="flat")
        style.map("Treeview",
                  background=[("selected", t["primary"])],
                  foreground=[("selected", "#FFFFFF")])

    # ---------- 页面导航 ----------
    def show_page(self, name, **kwargs):
        """销毁当前页面并切换到新页面。kwargs 会原样传给页面构造函数。"""
        if self.page is not None:
            self.page.destroy()
        cls = PAGE_CLASSES[name]
        self.page = cls(self, self.root, **kwargs)
        self.page_name = name

    # ---------- 通用控件工厂（页面统一使用，保证风格一致） ----------
    def card(self, parent):
        """带边框的白色卡片容器。"""
        return tk.Frame(parent, bg=self.theme["card"],
                        highlightbackground=self.theme["border"], highlightthickness=1)

    def label(self, parent, text, font=FONT_TEXT, bg=None, fg=None, **kw):
        """文本标签，默认放在卡片底色上。"""
        return tk.Label(parent, text=text, font=font,
                        bg=bg if bg is not None else self.theme["card"],
                        fg=fg if fg is not None else self.theme["text"], **kw)

    def button(self, parent, text, command, kind="primary", width=None):
        """按钮工厂。
        kind:
            primary  主色实心按钮（主要操作）
            ghost    卡片底色 + 主色文字 + 边框（次要操作）
            danger   红色实心按钮（危险操作，如删除）
        """
        t = self.theme
        styles = {
            "primary": {"bg": t["primary"], "fg": "#FFFFFF",
                        "activebackground": t["primary_dark"], "activeforeground": "#FFFFFF"},
            "ghost": {"bg": t["card"], "fg": t["primary"],
                      "activebackground": t["card_alt"], "activeforeground": t["primary_dark"]},
            "danger": {"bg": t["danger"], "fg": "#FFFFFF",
                       "activebackground": "#B7473F", "activeforeground": "#FFFFFF"},
        }
        s = styles[kind]
        kw = {"font": FONT_TEXT, "relief": "flat", "cursor": "hand2",
              "padx": 14, "pady": 7, "highlightthickness": 1,
              "highlightbackground": t["border"] if kind == "ghost" else s["bg"], **s}
        if width:
            kw["width"] = width
        return tk.Button(parent, text=text, command=command, **kw)

    def confirm(self, title, message):
        """弹出是/否确认框。"""
        return messagebox.askyesno(title, message, parent=self.root)

    def info(self, title, message):
        """弹出信息提示框。"""
        return messagebox.showinfo(title, message, parent=self.root)


import streamlit as st

# 1. 初始化状态，用于记录当前是第几题、用户的选择
if 'step' not in st.session_state:
    st.session_state.step = 0
if 'answers' not in st.session_state:
    st.session_state.answers = []

# 定义你的题目和选项（这里只是示例）
questions = [
    {"text": "在聚会中，你更倾向于？", "options": ["主动认识新朋友 (E)", "和熟悉的人待在一起 (I)"]},
    {"text": "做决定时，你更看重？", "options": ["逻辑和事实 (T)", "情感和他人感受 (F)"]}
]

# 2. 根据当前步骤显示内容
if st.session_state.step < len(questions):
    q = questions[st.session_state.step]
    st.subheader(f"问题 {st.session_state.step + 1}")
    st.write(q["text"])

    # 使用表单（form）将选项和提交按钮打包
    with st.form(key=f"form_{st.session_state.step}"):
        choice = st.radio("请选择：", q["options"], key=f"q_{st.session_state.step}")
        submitted = st.form_submit_button("下一题")

        if submitted:
            st.session_state.answers.append(choice)  # 记录答案
            st.session_state.step += 1  # 进入下一题
            st.rerun()  # 立即刷新页面，显示下一题[reference:4]
else:
    # 3. 所有题目答完后，显示结果
    st.success("测试完成！")
    # 这里写你的计分逻辑，比如根据 st.session_state.answers 算出MBTI类型
    # st.write("你的结果是：INTJ")
    if st.button("重新开始"):
        st.session_state.step = 0
        st.session_state.answers = []
        st.rerun()


# ═══════════════════════════════════════════════════════════════════
# 程序入口：直接运行本文件即可启动应用
# ═══════════════════════════════════════════════════════════════════

if __name__ == "__main__":
    root = tk.Tk()
    App(root)
    root.mainloop()
