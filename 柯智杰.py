# -*- coding: utf-8 -*-
"""
MBTI 人格测试 · 无界面核心版（已删除全部 tkinter 代码）
=========================================================
由原桌面增强版 v3.0 重构而来，功能全部保留在逻辑层，仅移除 tkinter 界面层：
  - 72 题题库（四个维度各 18 题，正反向各 9 题），五级李克特计分；
  - 16 型人格完整报告数据（画像 / 优势 / 短板 / 职业 / 生活分工 / 学习分工）；
  - SQLite 持久化：题库 / 历史记录 / 设置；
  - 数据导出：CSV（原「历史记录→导出 CSV」）、JSON 完整备份与恢复；
  - selftest()：无界面自检，验证计分与题库完整性。
仅依赖标准库（sqlite3 + json 等），可作为模块被任意前端复用
（tkinter / PyQt / 网页 / 命令行均可）。
"""

import json
import os
import sqlite3
import datetime

APP_TITLE = "MBTI 人格测试 · 增强版"
APP_VERSION = "3.1"

# ---------------------------------------------------------------- 路径


def app_dir():
    return os.path.dirname(os.path.abspath(__file__))


def db_path():
    """数据库路径；可用环境变量 MBTI_DB_PATH 覆盖（便于测试与云端挂载）。"""
    env = os.environ.get("MBTI_DB_PATH")
    if env:
        return env
    return os.path.join(app_dir(), "mbti_data.db")


# ---------------------------------------------------------------- 主题

THEMES = {
    "暖阳橙": dict(
        bg="#FFF7EF", bg2="#FFE6D0", card="#FFFFFF", card2="#FFFBF6",
        primary="#E8710A", primary2="#FFB25E", primary_soft="#FDE7D2",
        text="#3B2C1F", sub="#8C7A69", line="#F0DDC8",
        ok="#2FB56B", danger="#D9534F", shadow="#F2E2D0",
    ),
    "海洋蓝": dict(
        bg="#F3F8FD", bg2="#D9E9F8", card="#FFFFFF", card2="#F8FBFF",
        primary="#2E6DA4", primary2="#5FA8D3", primary_soft="#DCEBF9",
        text="#1E2A36", sub="#6B7C8C", line="#D7E0E8",
        ok="#2FB56B", danger="#D9534F", shadow="#E3ECF4",
    ),
    "清新绿": dict(
        bg="#F5FAF6", bg2="#DBEDE1", card="#FFFFFF", card2="#F8FCF9",
        primary="#2E8B57", primary2="#7CC29B", primary_soft="#DDF0E4",
        text="#22312A", sub="#6D7F74", line="#D8E7DC",
        ok="#2FB56B", danger="#D9534F", shadow="#E1EDE5",
    ),
    "暗夜黑": dict(
        bg="#161B22", bg2="#10151B", card="#232A32", card2="#1E242B",
        primary="#4E8FC9", primary2="#7FB4E0", primary_soft="#20303F",
        text="#E6EDF3", sub="#9AA8B5", line="#2F3841",
        ok="#3FBF7F", danger="#D9534F", shadow="#1B2027",
    ),
}
THEME_NAMES = list(THEMES.keys())

# ---------------------------------------------------------------- 16 型

TYPE_ORDER = ["INTJ", "INTP", "ENTJ", "ENTP", "INFJ", "INFP", "ENFJ", "ENFP",
              "ISTJ", "ISFJ", "ESTJ", "ESFJ", "ISTP", "ISFP", "ESTP", "ESFP"]

# 各类型展示用主色（原版使用 16personalities 卡通图片，属第三方版权素材，
# 网页版改为自绘彩色字母徽章，功能不受影响）
TYPE_COLORS = {
    "INTJ": "#3F4E8C", "INTP": "#6A6FA8", "ENTJ": "#B23A48", "ENTP": "#D65C8A",
    "INFJ": "#4E7A54", "INFP": "#7E9E6B", "ENFJ": "#C77D3F", "ENFP": "#D9A04E",
    "ISTJ": "#35566E", "ISFJ": "#5B8A8A", "ESTJ": "#7B5B8C", "ESFJ": "#9B6FA8",
    "ISTP": "#5A6B52", "ISFP": "#8A7B5C", "ESTP": "#C25B3F", "ESFP": "#E08A4B",
}

# ---------------------------------------------------------------- 人格数据

PERSONALITY = {
    "INTJ": dict(
        name="建筑师", tag="独立、理性、深谋远虑的战略家",
        desc="你习惯以长远眼光看待问题，喜欢制定周密的计划，并坚定地朝着目标前进。"
             "你善于洞察复杂事物的本质，追求高效与完美。",
        strengths=["战略思维强，善于长远规划", "分析能力强，逻辑严密",
                   "独立自律，行动力强", "洞察深刻，能看到问题本质", "思想开放，乐于接受新观点"],
        weaknesses=["过于理性，显得冷漠疏离", "完美主义，对人对己要求苛刻",
                    "固执，难以接受他人异议", "社交场合较为冷淡被动"],
        jobs=["战略顾问", "科研人员", "系统架构师", "投资分析师", "产品规划师"],
        life=["长期规划的制定者：储蓄、职业路线、五年计划，都在你心里排好了序。",
              "遇事最冷静的那一个：先分析再行动，很少情绪化表态。"],
        study=["课题的架构设计者：负责框架、方法论与逻辑链条。",
               "小组里的质量守门人：挑出论证漏洞与不严谨之处。"]),
    "INTP": dict(
        name="逻辑学家", tag="好奇心旺盛的抽象思考者",
        desc="你热衷于探索事物的原理与规律，享受在抽象世界中思考。"
             "你重视理性，对感兴趣的问题会钻研到底。",
        strengths=["分析能力强，逻辑严密", "求知欲旺盛，学习能力强",
                   "创意丰富，联想能力强", "思想开放，尊重差异", "独立，不易被外界左右"],
        weaknesses=["对执行细节缺乏耐心", "容易拖延，行动跟不上想法",
                    "忽视现实细节", "社交场合较为冷淡被动"],
        jobs=["研究员", "程序员", "数据分析师", "算法工程师", "大学教授"],
        life=["家里“为什么”的解答者：任何设备与原理都要研究明白。",
              "不喜欢被安排，但一旦入迷可以整夜钻研一件事。"],
        study=["理论与原理部分的攻坚者：负责搞懂最难的那一章。",
               "小组里的校验器：指出逻辑矛盾与数据错误。"]),
    "ENTJ": dict(
        name="指挥官", tag="目标明确的天然领导者",
        desc="你目标明确、行动果断，擅长组织资源、带领团队实现目标。"
             "你相信效率与结果，是天生的领导者。",
        strengths=["战略思维强，善于长远规划", "决断力强，敢于拍板",
                   "自信坚定，抗压能力强", "组织管理能力强", "执行力强，有始有终"],
        weaknesses=["过于强势固执", "缺乏耐心，容易催促他人",
                    "过于理性，显得冷漠疏离", "容易忽略他人感受"],
        jobs=["企业管理者", "项目经理", "投资合伙人", "律师", "创业者"],
        life=["家庭重大决策的推动者：买房、升学、旅行，都由你拍板。",
              "朋友圈里的项目发起人：说做就做，还能把大家组织起来。"],
        study=["小组的项目负责人：定目标、排期、分工、验收。",
               "竞赛或创业项目的操盘手：负责战略与资源整合。"]),
    "ENTP": dict(
        name="辩论家", tag="思维敏捷的创意挑战者",
        desc="你喜欢挑战常规，从不同角度分析问题，并享受思想碰撞的乐趣。"
             "创意和可能性让你充满动力。",
        strengths=["创意丰富，联想能力强", "口才好，善于说服他人",
                   "应变能力强，行动迅速", "求知欲旺盛", "思维敏捷，善于即兴发挥"],
        weaknesses=["喜欢抬杠，容易引发争论", "缺乏耐心，难以坚持",
                    "忽视规则，喜欢走捷径", "注意力容易分散"],
        jobs=["创业者", "产品经理", "营销策划", "咨询顾问", "媒体主理人"],
        life=["话题制造者：一顿饭能被你聊成一场辩论赛。",
              "疑难问题的拆解师：别人卡住的思路，你换个角度就通了。"],
        study=["开题与立论环节的主力：负责提出新颖的观点和框架。",
               "答辩时的辩手：应对提问、临场反驳、补足逻辑漏洞。"]),
    "INFJ": dict(
        name="提倡者", tag="富有远见的理想主义者",
        desc="你内心坚定，追求意义与价值，善于洞察他人的内心世界。"
             "你希望让世界变得更好，并愿意为之默默付出。",
        strengths=["洞察深刻，能看透人心", "信念坚定，有使命感",
                   "同理心强，善解人意", "思想开放，乐于接受新观点", "文字表达细腻"],
        weaknesses=["完美主义，自我要求过高", "情绪敏感，容易内耗",
                    "过度付出，容易疲惫", "习惯压抑自己的情绪"],
        jobs=["心理咨询师", "作家", "教师", "公益项目负责人", "人力资源"],
        life=["亲友的倾听者与顾问：别人愿意把心事说给你听。",
              "小圈子的定盘星：不常说话，但一句话能安定人心。"],
        study=["小组的方向把关者：梳理意义、提炼主题与价值表达。",
               "长文与深度报告的主笔：把零散材料写成有洞见的文字。"]),
    "INFP": dict(
        name="调停者", tag="温柔坚定的理想主义者",
        desc="你重视内心的价值观，追求真实与善良。你想象力丰富，"
             "常沉浸在文学、艺术与理想的世界中。",
        strengths=["真诚善良，富有同情心", "想象力丰富，有创造力",
                   "洞察深刻，能看透人心", "包容开放，尊重差异", "对热爱的事格外坚持"],
        weaknesses=["过于理想化，容易失望", "行动力弱，难以开始",
                    "过于敏感，容易受伤", "不善于表达自己"],
        jobs=["作家", "心理咨询师", "插画师", "翻译", "公益工作者"],
        life=["朋友情绪的安抚者：不评判、只陪伴。",
              "生活里的小小理想主义者：为一件喜欢的事默默坚持很久。"],
        study=["文字与创意部分的主笔：文案、剧本、设计说明。",
               "小组作品的价值把关：让成果多一点真诚与温度。"]),
    "ENFJ": dict(
        name="主人公", tag="热情洋溢的引路人",
        desc="你善于沟通与激励，总能发现他人的闪光点。"
             "你乐于帮助他人成长，是天生的组织者与引路人。",
        strengths=["感染力强，善于鼓舞人心", "沟通能力出色",
                   "洞察深刻，能看透人心", "乐于奉献，责任感强", "组织协调能力强"],
        weaknesses=["过度付出，容易疲惫", "过于理想化，容易失望",
                    "爱操心，事必躬亲", "有时忽视自身需求"],
        jobs=["教师", "培训师", "公关", "人力资源", "团队负责人"],
        life=["家人朋友的心灵树洞：谁有情绪，第一个想到找你。",
              "集体活动的发起人：组织聚会、张罗礼物、凝聚人心。"],
        study=["小组的凝聚核心：分工协调、激励同伴、把控方向。",
               "汇报主讲：把小组的想法讲得动人、讲得清楚。"]),
    "ENFP": dict(
        name="竞选者", tag="自由热情的可能性探索者",
        desc="你对世界充满好奇，喜欢探索各种可能性。"
             "你热情乐观，能用自己的活力感染身边的人。",
        strengths=["热情友好，感染力强", "创意十足，点子层出不穷",
                   "善于社交，人缘好", "乐观开朗，善于活跃气氛", "适应力强，不怕变化"],
        weaknesses=["注意力容易分散", "难以坚持长期计划",
                    "缺乏耐心，容易厌倦", "情绪易受外界影响"],
        jobs=["记者", "市场营销", "创意策划", "培训师", "新媒体主理人"],
        life=["朋友圈的点子王：总能带来新鲜玩法和新认识的人。",
              "情绪充电站：擅长把低迷的气氛重新点燃。"],
        study=["选题与创意策划：头脑风暴时贡献最多可能性。",
               "跨组联络与外联：找资源、找人、找合作。"]),
    "ISTJ": dict(
        name="物流师", tag="严谨可靠的秩序守护者",
        desc="你重视秩序、责任与传统，做事一丝不苟。"
             "你的可靠与踏实让身边的人都感到安心。",
        strengths=["条理清晰，注重细节", "可靠严谨，值得信赖",
                   "责任感强，说到做到", "执行力强，有始有终", "踏实勤恳，任劳任怨"],
        weaknesses=["固执保守，不喜变化", "不擅变通，容易死板",
                    "过于严肃，缺少幽默", "不善于表达情感"],
        jobs=["会计师", "审计师", "公务员", "质检员", "运营管理"],
        life=["家庭秩序的守护者：账单、证件、行程，样样有据可查。",
              "答应的事一定做到，是亲友眼中最靠谱的那个。"],
        study=["小组的进度与规范负责人：检查格式、核对引用、按时提交。",
               "需要长期坚持的任务：复习计划、实验记录、数据整理。"]),
    "ISFJ": dict(
        name="守卫者", tag="温暖细心的守护者",
        desc="你默默关心身边的人，用实际行动守护你在乎的一切。"
             "你温和踏实，是团队中最可靠的支柱。",
        strengths=["体贴周到，细心可靠", "忠诚重情，值得托付",
                   "责任感强，乐于助人", "踏实勤恳", "亲和力强"],
        weaknesses=["不善于拒绝别人", "习惯压抑自己的情绪",
                    "害怕变化，回避风险", "不够灵活，缺少弹性"],
        jobs=["护士", "教师", "行政主管", "客服管理", "社会工作者"],
        life=["家人身边最稳定的存在：记得每个人的习惯和忌口。",
              "默默把琐事做好的人：缴费、备药、收拾，从不声张。"],
        study=["小组的资料与后勤：整理笔记、核对格式、按时提醒。",
               "需要耐心与细致的任务：校对、录入、复盘记录。"]),
    "ESTJ": dict(
        name="总经理", tag="务实高效的规则执行者",
        desc="你崇尚规则与效率，善于组织和管理。"
             "你果断务实，是天生的管理者与执行者。",
        strengths=["组织管理能力强", "决断力强，敢于拍板",
                   "执行力强，有始有终", "责任感强，说到做到", "务实高效，讲究效率"],
        weaknesses=["过于严肃，缺少幽默", "固执强势，难以接受异议",
                    "不够灵活，缺少弹性", "有时忽视他人感受"],
        jobs=["企业管理者", "军官", "财务总监", "运营总监", "法官"],
        life=["家庭与团队的总调度：日程、账目、家务分工的把关与落地。",
              "亲友聚会的组织者：定时间、定地点、定流程，最后负责收尾。"],
        study=["课程小组的组长：拆解任务、分配角色、设定截止时间并催进度。",
               "实验与实践课的记录审核者：核对数据、格式与提交细节。"]),
    "ESFJ": dict(
        name="执政官", tag="热心周到的社交核心",
        desc="你重视和谐的人际关系，乐于为他人提供帮助。"
             "你亲和力强，总能把大家凝聚在一起。",
        strengths=["组织协调能力强", "亲和力强，人缘极好",
                   "体贴周到，细心可靠", "乐于助人，无私奉献", "善于沟通与倾听"],
        weaknesses=["过于在意他人评价", "爱操心，事必躬亲",
                    "不善于拒绝别人", "情绪易受外界影响"],
        jobs=["教师", "销售", "护士", "人事专员", "社区服务"],
        life=["家庭氛围的维护者：记生日、张罗聚餐、关心每个人的近况。",
              "朋友圈的联络中枢：谁和谁需要搭话，你总能想到。"],
        study=["小组里的协调者：负责沟通、汇总与成员情绪照顾。",
               "资料整理与美化：把大家零散的成果统成一份体面的作业。"]),
    "ISTP": dict(
        name="鉴赏家", tag="冷静灵活的实干家",
        desc="你喜欢动手探索事物的运作原理，遇到问题总能冷静地找到解决办法。"
             "你崇尚自由，活在当下。",
        strengths=["动手能力强，善于实操", "冷静理性，临危不乱",
                   "灵活应变，适应力强", "务实果断，不拖泥带水", "独立，自给自足"],
        weaknesses=["沉默寡言，难以接近", "回避严肃的话题",
                    "缺乏长远规划", "不善于表达情感"],
        jobs=["工程师", "机械师", "飞行员", "程序员", "专业运动员"],
        life=["动手解决麻烦的人：修电器、装家具、路上换胎。",
              "危机时刻最镇定的那个：不慌，先看问题出在哪。"],
        study=["实验与工程实践的主力：设备调试、代码调试、现场操作。",
               "小组里的技术顾问：别人搞不定的工具与流程找你。"]),
    "ISFP": dict(
        name="探险家", tag="温和随性的生活艺术家",
        desc="你对美有敏锐的感知，喜欢用自己的方式体验生活。"
             "你随和包容，享受宁静而真实的生活。",
        strengths=["审美出色，有艺术天赋", "观察敏锐，感受细腻",
                   "随和包容，与世无争", "动手能力强，善于实操", "真诚，不虚伪"],
        weaknesses=["回避冲突，容易逃避", "缺乏长远规划",
                    "不善于表达自己", "难以坚持长期计划"],
        jobs=["设计师", "摄影师", "厨师", "美容师", "音乐人"],
        life=["生活美学的实践者：把房间、穿搭、饭菜都过得有质感。",
              "朋友身边的安静陪伴者：不抢话，但在场。"],
        study=["视觉与手工部分：排版、绘图、模型、拍摄。",
               "实操课上的手感型选手：动手比讲理论更快进入状态。"]),
    "ESTP": dict(
        name="企业家", tag="精力充沛的行动派",
        desc="你是天生的行动派，善于抓住机会、随机应变。"
             "你热爱挑战，喜欢在实战中证明自己。",
        strengths=["应变能力强，行动迅速", "口才好，善于说服他人",
                   "自信坚定，抗压能力强", "务实果断，不拖泥带水", "精力充沛，敢于冒险"],
        weaknesses=["冲动冒险，考虑不周", "忽视规则，喜欢走捷径",
                    "缺乏长远规划", "对执行细节缺乏耐心"],
        jobs=["销售", "创业者", "体育教练", "警务人员", "房地产经纪"],
        life=["朋友圈里的行动派：说走就走的行程由你拍板，临时状况由你摆平。",
              "需要现场解决问题的角色：搬家、修东西、砍价，你上手就行。"],
        study=["实操型任务的主力：实验、调研、路演现场的执行与应变。",
               "小组汇报的控场者：负责开场、应答提问与临场救场。"]),
    "ESFP": dict(
        name="表演者", tag="热情开朗的快乐源泉",
        desc="你热爱生活，享受聚光灯下的每一刻。"
             "你的乐观与活力总能给身边的人带来快乐。",
        strengths=["乐观开朗，善于活跃气氛", "感染力强，善于鼓舞人心",
                   "反应敏捷，善于即兴发挥", "适应力强，随遇而安", "真诚热情，人缘好"],
        weaknesses=["缺乏规划，走一步看一步", "注意力容易分散",
                    "情绪起伏较大", "容易冲动消费"],
        jobs=["演员", "主持人", "导游", "幼教", "品牌活动策划"],
        life=["气氛担当：聚会里第一个开口、第一个带动大家玩起来的人。",
              "生活的体验官：发现好吃好玩的地方，带朋友去打卡。"],
        study=["展示环节的主角：PPT 汇报、情景演绎、口语展示。",
               "小组活动的组织者：负责把枯燥的任务变得有趣。"]),
}

# ---------------------------------------------------------------- 题库（72 题）
# dim: EI / SN / TF / JP    d=+1 表示「越同意越偏第一个字母」
QUESTION_BANK = [
    # ---- E / I ----
    ("EI", +1, "在热闹的聚会里，我待得越久越有精神。"),
    ("EI", -1, "忙碌一天后，我最想做的就是安静地独处一会儿。"),
    ("EI", +1, "我喜欢主动打破沉默，和陌生人开启话题。"),
    ("EI", -1, "在小组讨论中，我更愿意先听别人说，想好了再发言。"),
    ("EI", +1, "周末和一群朋友出去玩，比独自在家更让我兴奋。"),
    ("EI", -1, "长时间与人打交道后，我会感到被“掏空”，需要独处充电。"),
    ("EI", +1, "我的朋友圈很广，认识不同圈子的人让我开心。"),
    ("EI", -1, "我更习惯用文字而不是当面表达自己的想法。"),
    ("EI", +1, "遇到开心的事，我第一反应是说给别人听。"),
    ("EI", -1, "我更喜欢一对一的深聊，而不是一大群人热闹。"),
    ("EI", +1, "排队或乘车时，我常会顺口和旁边的人聊几句。"),
    ("EI", -1, "别人眼里热闹的场合，我常常盼着早点回家。"),
    ("EI", +1, "我说话时思路越聊越开阔，边说边想更有效率。"),
    ("EI", -1, "我需要较长的时间才能和新朋友熟络起来。"),
    ("EI", +1, "我喜欢成为团队活动的组织者和气氛担当。"),
    ("EI", -1, "安静的环境能让我保持长时间的专注和高效。"),
    ("EI", +1, "一群人聚在一起时，我常常感到能量满满。"),
    ("EI", -1, "参加大型活动前，我会提前给自己留出“独处储备”。"),
    # ---- S / N ----
    ("SN", +1, "我更关注眼前具体的事实，而不是遥远的可能性。"),
    ("SN", -1, "我常常沉浸在白日梦和对未来的畅想中。"),
    ("SN", +1, "学新东西时，我喜欢从具体步骤和实例入手。"),
    ("SN", -1, "我喜欢琢磨事物背后的象征意义和深层含义。"),
    ("SN", +1, "我相信自己亲身实践过的经验，胜过抽象理论。"),
    ("SN", -1, "我经常能冒出天马行空的新点子和联想。"),
    ("SN", +1, "我描述事情时习惯按顺序讲清细节。"),
    ("SN", -1, "我说话喜欢用比喻，觉得形象比精确更重要。"),
    ("SN", +1, "我做事讲究脚踏实地，一步一个脚印。"),
    ("SN", -1, "我对“未来会怎样”的想象比“现在怎么样”更感兴趣。"),
    ("SN", +1, "我记路、记面孔、记细节的能力比较强。"),
    ("SN", -1, "读文章时，我更容易被字里行间的言外之意吸引。"),
    ("SN", +1, "我喜欢内容明确、看得见摸得着的工作。"),
    ("SN", -1, "重复做同一件事时，我会自己琢磨新玩法来保持新鲜感。"),
    ("SN", +1, "我倾向于选择经过验证的成熟方法。"),
    ("SN", -1, "我常常注意到别人没留意的规律和关联。"),
    ("SN", +1, "我更喜欢照着说明书一步步操作，而不是自己摸索。"),
    ("SN", -1, "我常想“如果换个角度，这事还能怎么做”。"),
    # ---- T / F ----
    ("TF", +1, "做决定时，我优先考虑逻辑和客观标准。"),
    ("TF", -1, "他人的感受会明显影响我的决定。"),
    ("TF", +1, "指出问题时我会直截了当，不太绕弯子。"),
    ("TF", -1, "我宁愿委屈自己，也不愿伤害别人的感情。"),
    ("TF", +1, "我认为分清对错比维持表面和谐更重要。"),
    ("TF", -1, "看到感人的故事或电影，我很容易动感情。"),
    ("TF", +1, "辩论时我更在乎论证是否严密，而不是谁赢谁输。"),
    ("TF", -1, "朋友难过时，我会先安慰情绪，再讨论解决办法。"),
    ("TF", +1, "我能比较冷静地做出别人觉得“不近人情”的决定。"),
    ("TF", -1, "我会下意识地去照顾团队里每个人的情绪。"),
    ("TF", +1, "评价一件事，我先看它合不合理，再看它讨不讨人喜欢。"),
    ("TF", -1, "我很难拒绝别人的请求，即使这让我很为难。"),
    ("TF", +1, "我觉得“讲道理”比“讲人情”更能解决问题。"),
    ("TF", -1, "我很容易感知到气氛的微妙变化并去调和。"),
    ("TF", +1, "对事不对人，批评时我不会特意软化措辞。"),
    ("TF", -1, "别人的肯定和感谢对我很重要。"),
    ("TF", +1, "我更欣赏理性、有条理的分析方式。"),
    ("TF", -1, "我做选择时常常凭“感觉对不对”，而不只是利弊。"),
    # ---- J / P ----
    ("JP", +1, "我喜欢提前制定计划并严格执行。"),
    ("JP", -1, "我喜欢事情保持开放，随时可以灵活调整。"),
    ("JP", +1, "我的书桌和房间通常收拾得井井有条。"),
    ("JP", -1, "截止日期临近时，我才会爆发出最高效率。"),
    ("JP", +1, "旅行前，我会做一份详细的攻略。"),
    ("JP", -1, "计划赶不上变化，所以我很少做长远规划。"),
    ("JP", +1, "事情悬而未决会让我不舒服，我总想尽快敲定。"),
    ("JP", -1, "我常常同时开着好几件事，想到哪件做哪件。"),
    ("JP", +1, "待办清单上的事项我会一项项划掉，很有成就感。"),
    ("JP", -1, "我更喜欢随机应变，说走就走的旅行才有意思。"),
    ("JP", +1, "我习惯把东西放在固定位置，用完归位。"),
    ("JP", -1, "我容易拖延，总觉得“还有时间”。"),
    ("JP", +1, "我喜欢提前把事情安排妥当，避免最后一刻手忙脚乱。"),
    ("JP", -1, "我享受多条任务并行的忙碌和刺激感。"),
    ("JP", +1, "做重要决定前，我会收集足够信息反复比较。"),
    ("JP", -1, "我做决定比较快，边做边调整。"),
    ("JP", +1, "完成一件事后我才会安心开始下一件。"),
    ("JP", -1, "我讨厌一成不变的日程，喜欢每天有点不一样。"),
]

OPTION_LABELS = ["非常不符合", "不太符合", "说不清", "比较符合", "非常符合"]
OPTION_KEYS = ["A", "B", "C", "D", "E"]
OPTION_WEIGHT = {"A": -2, "B": -1, "C": 0, "D": 1, "E": 2}

DIM_META = {
    "EI": ("外向 E", "内向 I"),
    "SN": ("实感 S", "直觉 N"),
    "TF": ("思考 T", "情感 F"),
    "JP": ("判断 J", "知觉 P"),
}
DIM_ORDER = ["EI", "SN", "TF", "JP"]

# ---------------------------------------------------------------- 数据库


class Database:
    """所有数据库操作的唯一入口：题库 / 历史记录 / 设置 / 备份。"""

    def __init__(self, path=None):
        self.path = path or db_path()
        self.conn = sqlite3.connect(self.path, check_same_thread=False)
        self.conn.row_factory = sqlite3.Row
        self._init_schema()
        self.seed_if_empty()

    # ---- 建表与迁移
    def _init_schema(self):
        c = self.conn
        c.execute("""CREATE TABLE IF NOT EXISTS questions(
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            dim TEXT, direction INTEGER, text TEXT,
            opt_a TEXT, opt_b TEXT, opt_c TEXT, opt_d TEXT)""")
        c.execute("""CREATE TABLE IF NOT EXISTS records(
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nickname TEXT, mbti TEXT, type_name TEXT,
            ei TEXT, sn TEXT, tf TEXT, jp TEXT,
            e INT, i INT, s INT, n INT, t INT, f INT, j INT, p INT,
            ei_pct INT, sn_pct INT, tf_pct INT, jp_pct INT,
            answers TEXT, created_at TEXT)""")
        c.execute("""CREATE TABLE IF NOT EXISTS settings(
            key TEXT PRIMARY KEY, value TEXT)""")
        # 兼容旧库：补充第五个选项列
        try:
            cols = [r[1] for r in c.execute("PRAGMA table_info(questions)")]
            if "opt_e" not in cols:
                c.execute("ALTER TABLE questions ADD COLUMN opt_e TEXT")
        except sqlite3.Error:
            pass
        c.commit()

    def seed_if_empty(self):
        if self.count_questions() == 0:
            self.reset_questions()

    def reset_questions(self):
        c = self.conn
        c.execute("DELETE FROM questions")
        for dim, d, text in QUESTION_BANK:
            c.execute("""INSERT INTO questions(dim,direction,text,opt_a,opt_b,opt_c,opt_d,opt_e)
                         VALUES(?,?,?,?,?,?,?,?)""",
                      (dim, d, text, *OPTION_LABELS))
        c.commit()

    # ---- 题库
    def count_questions(self):
        return self.conn.execute("SELECT COUNT(*) FROM questions").fetchone()[0]

    def list_questions(self):
        rows = self.conn.execute("SELECT * FROM questions ORDER BY id").fetchall()
        out = []
        for r in rows:
            d = dict(r)
            opts = {}
            for i, k in enumerate(OPTION_KEYS):
                v = d.get("opt_" + k.lower())
                opts[k] = v if v else OPTION_LABELS[i]
            d["options"] = opts
            out.append(d)
        return out

    def save_question(self, q):
        c = self.conn
        vals = (q["dim"], q["direction"], q["text"],
                q["options"]["A"], q["options"]["B"], q["options"]["C"],
                q["options"]["D"], q["options"]["E"])
        if q.get("id"):
            c.execute("""UPDATE questions SET dim=?,direction=?,text=?,
                         opt_a=?,opt_b=?,opt_c=?,opt_d=?,opt_e=? WHERE id=?""",
                      vals + (q["id"],))
            qid = q["id"]
        else:
            cur = c.execute("""INSERT INTO questions(dim,direction,text,
                               opt_a,opt_b,opt_c,opt_d,opt_e)
                               VALUES(?,?,?,?,?,?,?,?)""", vals)
            qid = cur.lastrowid
        c.commit()
        self.backup_to_file()
        return qid

    def delete_question(self, qid):
        self.conn.execute("DELETE FROM questions WHERE id=?", (qid,))
        self.conn.commit()
        self.backup_to_file()

    # ---- 记录
    def save_record(self, nickname, result):
        r = result
        cur = self.conn.execute(
            """INSERT INTO records(nickname,mbti,type_name,ei,sn,tf,jp,
            e,i,s,n,t,f,j,p,ei_pct,sn_pct,tf_pct,jp_pct,answers,created_at)
            VALUES(?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)""",
            (nickname, r["mbti"], r["type_name"],
             r["letters"]["EI"], r["letters"]["SN"], r["letters"]["TF"], r["letters"]["JP"],
             r["scores"]["E"], r["scores"]["I"], r["scores"]["S"], r["scores"]["N"],
             r["scores"]["T"], r["scores"]["F"], r["scores"]["J"], r["scores"]["P"],
             r["percents"]["EI"], r["percents"]["SN"], r["percents"]["TF"], r["percents"]["JP"],
             json.dumps(r["answers"], ensure_ascii=False),
             datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")))
        self.conn.commit()
        self.backup_to_file()
        return cur.lastrowid

    def list_records(self):
        rows = self.conn.execute("SELECT * FROM records ORDER BY id DESC").fetchall()
        return [dict(r) for r in rows]

    def get_record(self, rid):
        row = self.conn.execute("SELECT * FROM records WHERE id=?", (rid,)).fetchone()
        if not row:
            return None
        d = dict(row)
        try:
            d["answers"] = json.loads(d.get("answers") or "{}")
        except ValueError:
            d["answers"] = {}
        return d

    def delete_record(self, rid):
        self.conn.execute("DELETE FROM records WHERE id=?", (rid,))
        self.conn.commit()
        self.backup_to_file()

    def clear_records(self):
        self.conn.execute("DELETE FROM records")
        self.conn.commit()
        self.backup_to_file()

    # ---- 设置
    def get_setting(self, key, default=None):
        row = self.conn.execute("SELECT value FROM settings WHERE key=?", (key,)).fetchone()
        return row[0] if row else default

    def set_setting(self, key, value):
        self.conn.execute("""INSERT INTO settings(key,value) VALUES(?,?)
                             ON CONFLICT(key) DO UPDATE SET value=excluded.value""",
                          (key, value))
        self.conn.commit()

    # ---- 备份 / 恢复（Streamlit 云端文件系统易失，重要数据可下载保存）
    def export_json(self):
        return json.dumps({
            "app": "mbti",
            "version": APP_VERSION,
            "exported_at": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "records": self.list_records(),
        }, ensure_ascii=False, indent=1)

    def import_json(self, text, replace=True):
        data = json.loads(text)
        rows = data.get("records", [])
        cols = ["nickname", "mbti", "type_name", "ei", "sn", "tf", "jp",
                "e", "i", "s", "n", "t", "f", "j", "p",
                "ei_pct", "sn_pct", "tf_pct", "jp_pct", "answers", "created_at"]
        c = self.conn
        if replace:
            c.execute("DELETE FROM records")
        for r in rows:
            c.execute("INSERT INTO records(%s) VALUES(%s)"
                      % (",".join(cols), ",".join("?" * len(cols))),
                      tuple(r.get(k) for k in cols))
        c.commit()
        self.backup_to_file()
        return len(rows)

    def backup_path(self):
        return self.path + ".backup.json"

    def backup_to_file(self):
        try:
            with open(self.backup_path(), "w", encoding="utf-8") as f:
                f.write(self.export_json())
        except OSError:
            pass

    # ---- 导出 CSV（原桌面版「历史记录 → 导出 CSV」的界面无关实现）
    def export_csv(self):
        import csv
        import io
        keys = ["id", "nickname", "mbti", "type_name", "ei", "sn", "tf", "jp",
                "ei_pct", "sn_pct", "tf_pct", "jp_pct", "created_at"]
        buf = io.StringIO()
        wr = csv.writer(buf)
        wr.writerow(keys)
        for r in self.list_records():
            wr.writerow([r.get(k, "") for k in keys])
        return buf.getvalue()


# ---------------------------------------------------------------- 计分

def compute_result(questions, answers):
    """根据题目与答案计算 MBTI 结果。

    每题五级量表（A..E → -2..+2），按 direction 累加到对应维度两端，
    取占比高者为该维度字母，并给出倾向清晰度。
    """
    scores = {k: 0 for k in "EISNTFJP"}
    for q in questions:
        key = str(q["id"])
        ans = answers.get(key) or answers.get(q["id"])
        if not ans:
            continue
        w = OPTION_WEIGHT.get(str(ans).upper(), 0) * q["direction"]
        first, second = {"EI": ("E", "I"), "SN": ("S", "N"),
                         "TF": ("T", "F"), "JP": ("J", "P")}[q["dim"]]
        if w >= 0:
            scores[first] += w
        else:
            scores[second] += -w

    letters, percents, margins = {}, {}, {}
    for dim in DIM_ORDER:
        a, b = {"EI": ("E", "I"), "SN": ("S", "N"),
                "TF": ("T", "F"), "JP": ("J", "P")}[dim]
        total = scores[a] + scores[b]
        pct = 50 if total == 0 else round(scores[a] * 100.0 / total)
        letters[dim] = a if pct >= 50 else b
        percents[dim] = pct
        margins[dim] = abs(pct - 50)

    mbti = "".join(letters[d] for d in DIM_ORDER)
    info = PERSONALITY.get(mbti, {})
    return dict(
        mbti=mbti,
        type_name=info.get("name", mbti),
        tagline=info.get("tag", ""),
        desc=info.get("desc", ""),
        strengths=info.get("strengths", []),
        weaknesses=info.get("weaknesses", []),
        jobs=info.get("jobs", []),
        life=info.get("life", []),
        study=info.get("study", []),
        letters=letters, percents=percents, margins=margins,
        scores=scores, answers=dict(answers),
        clarity="clear" if min(margins.values()) >= 12 else "mixed",
    )


def estimate_minutes(n):
    return max(2, int(round(n * 9 / 60.0)))


# ---------------------------------------------------------------- 自检

def selftest():
    """无界面自检：验证计分逻辑、题库完整性与备份恢复。"""
    db = Database(os.path.join(os.path.dirname(os.path.abspath(__file__)),
                               "mbti_selftest.db"))
    qs = db.list_questions()
    print("题库总数:", len(qs))
    per_dim = {}
    for q in qs:
        per_dim.setdefault(q["dim"], []).append(q)
    for dim, lst in per_dim.items():
        pos = sum(1 for q in lst if q["direction"] > 0)
        print(f"  {dim}: {len(lst)} 题（正向 {pos} / 反向 {len(lst)-pos}）")

    cases = [
        ("全 A", {q["id"]: "A" for q in qs}),
        ("全 E", {q["id"]: "E" for q in qs}),
        ("全 C", {q["id"]: "C" for q in qs}),
    ]
    for label, ans in cases:
        r = compute_result(qs, ans)
        print(f"{label} → {r['mbti']} {r['type_name']} {r['percents']}")

    r = compute_result(qs, {q["id"]: ("E" if q["direction"] > 0 else "A") for q in qs})
    print("方向一致作答 →", r["mbti"], r["percents"])

    # 备份 / 恢复往返 + CSV 导出
    db.save_record("自检", r)
    backup = db.export_json()
    csv_text = db.export_csv()
    print("CSV 行数:", csv_text.count(chr(10)), "| CSV 表头:", csv_text.splitlines()[0][:40])
    db.clear_records()
    n = db.import_json(backup)
    print("备份恢复记录数:", n, "| 恢复后记录:", len(db.list_records()))

    db.conn.close()
    try:
        os.remove(db.path)
        if os.path.exists(db.backup_path()):
            os.remove(db.backup_path())
    except OSError:
        pass
    print("自检完成")


if __name__ == "__main__":
    selftest()
