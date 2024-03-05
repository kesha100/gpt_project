import openai
import pandas as pd
import yaml
import os
from fastapi import FastAPI, HTTPException
from fastapi.responses import FileResponse
from fpdf import FPDF
from reportlab.lib.pagesizes import letter,A4
from reportlab.lib.units import inch,cm
from reportlab.lib import colors
from reportlab.pdfgen import canvas
from datetime import datetime
import subprocess
import re

app = FastAPI(title='gpt-4',)

# Load OpenAI API key from config file
def load_api_key():
    with open("config.yaml") as f:
        config_yaml = yaml.safe_load(f)
    return config_yaml['api_key']

openai.api_key=load_api_key()



def process_csv_and_generate_content(file_path_xlxs, name):
    try:
        df = pd.read_excel(file_path_xlxs)
        name_column = '学生拼音/英文姓名（例：Eric Zhang 或者 Runxin Zhang）Student Name (First Name + Last Name)'
        data = df[df[name_column] == name].astype(str)

        if data.empty:
            return None, "person not found", None, None, None, None, None

        basic_info = data.iloc[:, 6:10].astype(str)
        major_preferences = data.iloc[:, 14:37].astype(str)
        college_preferences = data.iloc[:, 37:49].astype(str)
        potential_major_exploration = data.iloc[:, 49:82].astype(str)
        column_AU = data.iloc[:, 46].astype(str)

        return data, name, basic_info, major_preferences, college_preferences, potential_major_exploration, column_AU
    except ValueError as e:
        print(f"Error reading the Excel file: {e}")
        return None, None, None, None, None, None, None

def generate_gpt(data,name,basic_info,major_preferences,college_preferences,potential_major_exploration,column_AU):
    firstpage_summary = f""" 你的角色是一位长者。根据学生 提供的问卷，重新书写出一段故事性的总结，不要超过500字。请与以下例子中的风格保持一致。“同学你好，在本次测试中，我看到了一位...；你是智慧博学的研究员，你有着永不枯竭的好奇心，强大的逻辑和异于常人的洞察力，求知欲更是驱使你站到了探索未知的第一线。理性的你注重逻辑分析，擅长抽象思考，时刻准备找出真理.use this information and generate on chinese language: '''{name},{basic_info}, {major_preferences}, {college_preferences}''' """
    major_prompt_one = f""" 你是一位拥有多年教育经验的顶级留学咨询师，你尤其擅长了解学生的特点并进行基于基础数据的推荐。接下来你的任务是帮助我根据一份高中生的问卷为这位高中生推荐出最适合他的专业，你需要给出详细的理由并在每个中用理由到问卷里的细节信息，你同时需要给出足够的推理过程。在问卷中，学生会对每一个问题或因素进行权重的判断，不同的权重代表了这个因素在专业选择中得重要性(0表示一点都不重要，5表示非常重要)，请结合这些权重的数字给出最终推荐。你的具体任务分为两步。第一步是根据标为原始信息的信息为这位学生推荐10个最适合他的专业并给出理由。第二步是根据标为补充信息的信息从未这位学生推荐的10个最适合他的专业中筛选出3个专业并给出理由和这些专业与他的匹配度。最终结果我希望拥有一个含有10个推荐专业和理由，3个最适合专业和理由文档，每个理由都不能少于300字。当你准备好了，我就把这位学生的信息发给你。generate on the chinese language"""
    major_prompt_two = f""" 请根据以下问卷信息为用户 进行第一步10个专业的推荐，在推荐的过程中请注重学生给出对于每个因素的权重。每个推荐理由不能少于300字.use this information and generate on chinese language: '''{name},{basic_info},{major_preferences}''' """
    major_prompt_three = f""" 请根据以下补充信息（被3个引号括起）继续从上述10个专业中进行第二步的3个最匹配专业的筛选。请给出更详细的理由，每个理由都需要要足够多的细节，证据和推理过程。每个理由都不能少于300字。请同时给出专业匹配度（0为最不匹配，100为最匹配）represent only main 3 majors, without explanation and description :'''{college_preferences}''' """
    

    # gpt_input = f"{firstpage_summary}"
    # chat_completion = openai.chat.completions.create(
    # model="gpt-4",
    #     messages=[{"role": "user", "content": gpt_input}],
    #     temperature=0.7,
    #     top_p=1.0,
    #     frequency_penalty=0.3,
    #     presence_penalty=0.0
    # )
    # generated_summary=chat_completion.choices[0].message.content
    # print("done1")

    # gpt_input = f"{major_prompt_one},{major_prompt_two},{data}"
    # # print(gpt_input)
    # chat_completion = openai.chat.completions.create(
    #     model="gpt-3.5-turbo",
    #     messages=[{"role": "user", "content": gpt_input}],
    #     temperature=0.5,
    #     top_p=1.0,
    #     frequency_penalty=0.3,
    #     presence_penalty=0.0
    # )
    # generated_major_prompt_two = chat_completion.choices[0].message.content
    # print("done2")

    gpt_input = f"{major_prompt_three}"
    chat_completion = openai.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=[{"role": "user", "content": gpt_input}],
        temperature=0.5,
        top_p=1.0,
        frequency_penalty=0.3,
        presence_penalty=0.0
    )
    major_list = chat_completion.choices[0].message.content
    print("done3")
    
#     potential_major = f"""1. 學習困難。 有些專業可能涉及較高的學習複雜性，例如需要深入理解複雜的理論和概念或掌握一系列複雜的技術和技能。
#         2. 實踐機會。 有些專業可能沒有足夠的實務機會，導致學生缺乏理論與實際應用的連結。
#         3.職業前景：有些專業可能缺乏明確或廣闊的職業前景，導致學生畢業後很難找到適合的工作。
#         4.競爭壓力：有些專業可能競爭壓力較大，例如一些熱門專業可能會有大量學生競爭有限的就業機會。
#         5、基本要求。 一些專業可能有嚴格的課程或學分要求，這可能會讓學生在滿足這些要求的同時沒有足夠的時間和機會來探索自己的興趣和潛力。
#         6.工作壓力。 有些職業可能會導致高壓力工作，例如醫學、法律或金融等領域，這些領域通常需要高壓工作和長時間工作。
#         7. 對經濟環境或政策的依賴：某些職業可能會受到經濟環境或政策變化的影響，這些變化可能會影響該職業的勞動市場和薪資水準。 例如，全球經濟或能源政策可能會影響涉及金融或能源的大公司。
#         8.產業環境快速變化。 有些專業可能面臨快速變化的行業環境，例如技術或媒體專業，學生必須有機會不斷學習和更新自己的知識和技能。
#         你現在正在模仿大學輔導員。
#         請從顧問的角度，依照以上八個參數，指出以下三個專業的缺點：'''{major_list}'''_。 必須列出每個主要方向的每個維度。 如果此測量沒有明顯缺陷，請明確說明。
#         有必要詳細、詳細地描述，並提供充分的證據和例子。 每個段落必須至少由 3 個句子組成。 描述中需要加入個人經歷，用更感性的風格寫出缺點。 在每點後面加入詳細的例子，並使理由更長、更詳細。 建立文字時，請遵循諮詢性質。请与以下例子中的风格保持一致。“你的 等等 " 生成中文"""
    # gpt_input = f"{major_prompt_one},{major_prompt_three},{data}"
    # chat_completion = openai.chat.completions.create(
    #     model="gpt-3.5-turbo",
    #     messages=[{"role": "user", "content": gpt_input}],
    #     temperature=0.5,
    #     top_p=1.0,
    #     frequency_penalty=0.3,
    #     presence_penalty=0.0
    # )
    # generated_major_prompt_three = chat_completion.choices[0].message.content
    # print("done4")

#     # potential major
#     gpt_input = f"{potential_major}"
#     chat_completion = openai.chat.completions.create(
#         model="gpt-4",
#         messages=[{"role": "user", "content": gpt_input}],
#         temperature=0.5,
#         top_p=1.0,
#         frequency_penalty=0.3,
#         presence_penalty=0.0,

#     )
#     generated_potential_major = chat_completion.choices[0].message.content
#     print("done5")

#     Correspondence_college_recommendations = f"""想象你正在规划你的未来学术之旅，目标是在'''{column_AU}'''国家中深造，专注于"'''{major_list}'''"这几个潜在的专业。针对这些专业，我将为你推荐每个国家中最具代表性的三所大学，并详细解释推荐理由。每所大学的推荐理由将不少于300字，旨在帮助你更好地了解这些大学在你感兴趣的专业领域中的地位和优势。我们的目标是为你提供足够的信息，以便你能够做出明智的选择，规划你的未来教育和职业路径。"""

#     Correspondence_Courses = f"""想象我们正在为你量身定制一个学习计划，专注于你最感兴趣的三个专业'''{major_list}'''。对于每个专业，我将为你精选出7门基础课程和3门进阶课程，这些课程将帮助你在本科阶段打下坚实的基础，并进一步深化你的专业知识。每门课程都将以中英文双语的形式呈现，格式为：专业名'''{name}'''；课程名(class name)。通过这样的方式，我们希望能够帮助你更清晰地规划你的学术之旅，让你对未来的学习和职业发展充满信心。"""

#     Major_development_history = f"""想象我们正在一起回顾'{major_list}'这些专业在过去50年中的发展历程，并挑选出其中5个关键的转折点。对于每个转折点，我们将深入探讨它发生的时间、背后的原因、以及它对专业领域带来的深远影响。每个转折点的描述将不少于200字，通过这样详细的分析，我们希望能帮助你更好地理解这些领域如何演变成今天的模样。"""

#     Cutting_edge_field = f"""想象一下，我们一起深入探索'{major_list}'这几个专业，并且聚焦于它们在学术界和工业界最前沿的三个领域。对于每个专业，我会帮你揭示这些领域的创新和进展，并为每个领域提供不少于200字的详细描述。这将不仅仅是一个简单的列表，而是一次发现之旅，带你了解这些专业领域的最新研究成果和行业趋势。通过这个过程，希望能激发你对未来学习和职业路径的思考和规划。"""

#     Visualization_p1 = f"""想象我们正共同在一间充满未来可能性的房间里，面前铺开的地图指向'工程学科', '理科学科', '社会科学学科', 和 '社会人文学科'这四个潜在的专业方向。我们要通过五个关键维度来探索和评估你在这些领域的潜力和热情：1. 知识掌握程度 - 探讨你对这些学科核心理念和技能的理解深度。2. 热爱程度 - 衡量你对这些学科的兴趣程度。3. 实践应用能力 - 评价你如何将理论知识运用到实际问题解决中。4. 创新能力 - 考察你在这些学科中提出新观点和解决方案的能力。5. 对未来的投入意愿 - 询问你愿意为实现未来职业或学术目标在这些学科中投入多少时间和精力。

# 我们将基于你的问卷结果，对这些学科的每一个维度给出0到5分的评分，深入挖掘你的兴趣所在，并辅助你做出最适合自己的专业选择'''{potential_major_exploration}''' """
    
#     Visualization_p2 = f"""想象我们正坐在一间安静的图书馆里，面前摊开的是你的未来规划。我们将一起探索 '{major_list}' 这些你感兴趣的专业，并针对每个专业深入分析‘知识掌握程度’、‘热爱程度’、‘实践实用能力’、‘创新能力’和‘对未来的投入意愿’这五大关键维度。通过综合考量你的问卷信息、个人偏好以及未来职业目标，我们不仅将发现哪个专业最适合你，还将揭示你在这些领域中的独特潜力和热情。

#     比如在运动医学领域，我们会基于你对生物科学的兴趣和在相关课外活动中的表现，来评估你的‘知识掌握程度’和‘热爱程度’。进一步地，我们还会探讨你在实践中的应用能力，以及你对创新和未来投入的意愿。

#     通过这个过程，我们将为你提供一个量身定制的分析报告，帮助你做出最适合你的专业选择，确保它符合你的个人兴趣和职业规划。{basic_info}、{major_preferences}、{college_preferences}将是我们分析的基础。"""


#     Highschool_activities = f"""1. 运动科学(Kinesiology)：
# 一周以内：在一周之内，你可以组织一次校内运动科学小型研讨会。邀请校内的体育爱 好者、健身教练和相关专业的学生参加。你可以邀请一位运动科学领域的教授或专家进 行讲座，探讨热门话题如运动与健康的关系，新兴的运动训练方法等。通过这个独特的 活动，你将展示自己的组织能力、领导力，并为同学们带来有价值的学习机会。
# 一个月以内：在一个月内，你可以参与一个在线社交平台上的科学普及活动。你可以制 作短视频或撰写博文，介绍一些有趣的科学实验或运动原理。这样的活动将帮助你将运 动科学知识传播给更广大的受众，同时锻炼你的科学沟通能力。你还可以邀请其他研究 生或教授合作，共同打造一个有趣而有深度的科普系列。
# 一年以内：在一年内，你可以组织一个大型的运动科学实验活动。你可以合作建立一个 临时的体能测试中心，邀请学生和社区居民参与。你可以设计各种测试项目，如心肺功 能测试、肌肉力量测试等，为参与者提供个性化的健康建议。通过这个活动，你将锻炼 项目管理、团队协作和数据分析的能力，同时服务社区，传播健康理念。 
# 背景提升规划：除了参与学术和实践活动外，你还可以考虑策划一个创新性的"运动科学 展览"。你可以利用虚拟现实技术，打造一个沉浸式的展览环境，让参观者可以亲身体验 不同类型的运动和其对身体的影响。你可以合作设计师、程序员和医学专家，共同创造 一个有趣而富有教育价值的展览，以展示运动科学的魅力。 
# 2. 生物科学(Biology)： 
# 一周以内：在一周之内，你可以发起一个校内的生态探索活动。邀请同学们一起前往附 近的自然保护区或野外地区，进行一次生物多样性调查。你可以带领大家观察不同种类 的植物和动物，记录它们的分布和行为。通过这个活动，你将培养同学们的野外观察技 能，提升他们对生态系统的认识。 
# 一个月以内：在一个月内，你可以启动一个“生物故事收集计划”。邀请周围的人们，包 括老人、农民、渔民等，分享他们与自然界的互动经历和传统知识。你可以采访他们， 记录这些有趣的生物观察和传说，然后将它们整理成书籍、博客或短片。通过这个计 划，你将传承当地的生物文化，弘扬生物科学的价值。 
# 一年以内：在一年内，你可以发起一个“城市生态恢复计划”。与同学们合作，选择校园 或社区中的一个受损生态环境，如荒地或污染区，然后设计并实施一个生态恢复方案。 你可以种植适应性植物、引入天敌，同时监测环境变化。通过这个项目，你将锻炼项目 管理和环境保护技能，同时为城市生态的改善做出贡献。 
# 背景提升规划：除了学术和实践活动外，你可以考虑参与一个“生物文化交流计划”。你 可以申请前往其他国家或地区，与当地的生物学家、民间艺术家和社区领袖合作，了解 他们的生物文化传统。你可以学习当地的野外观察方法、草药医学、传统故事等，以拓 展你的生物科学视野。将这些经验与你的专业知识相结合，创造出独特的研究或项目。 
# 3. 物理治療(Physical Therapy)：
# 一週以內：在一週之內，你可以組織一個「復健運動體驗日」。邀請社區參與者，特別是有運動損的家庭有氧運動。透過這個活動，你將幫助參與者體驗到物理治療的積極影響，同時提升他們的健康意識。
# 《》本有趣的繪本，介紹復健治療的基本原理和方法。你可以選擇一些常見的復健案例，將科學知識用豐富創意的故事和插畫表現出來。本繪本可以用於兒童醫院、復健中心等地，幫助患者和家庭了解復健治療。
# 一年以內：在一年內，你可以合作開發一個「虛擬復健實驗室」。利用虛擬實境技術，創造一個虛擬環境，模擬各種復健訓練場景。使用者可以透過VR頭盔體驗不同類型的運動、平衡這個計畫將結合技術和復健實踐，為患者提供創新的復健體驗。
# ""關於我們首頁同時提升您的復健諮詢與溝通技巧
# 請根據以上的論文風格內容格式，為該高中生規劃大學申請的活動。他的目標專業分別為：'''{major_list}'''。活動規劃課程程），一年內的活動（科研，實習，志工），以及背景提升的規劃（主打科研和基於開放式專案的學習，現實免費資源和付費資源）
# 請提供更多創意和獨特性的活動規劃。每個活動的細節和資訊不能少300字。请与以下例子中的风格保持一致。“你的 等等 " 生成中文  """

#     Correspondence_college_recommendations
#     gpt_input = f"{Correspondence_college_recommendations}"
#     chat_completion = openai.chat.completions.create(
#         model="gpt-4",
#         messages=[{"role": "user", "content": gpt_input}],
#         temperature=0.8,
#         top_p=1.0,
#         frequency_penalty=0.3,
#         presence_penalty=0.0,
#     )
#     generated_Correspondence_college_recommendations = chat_completion.choices[0].message.content

#     # Correspondence_Courses
#     gpt_input = f"{Correspondence_Courses}"
#     chat_completion = openai.chat.completions.create(
#         model="gpt-4",
#         messages=[{"role": "user", "content": gpt_input}],
#         temperature=0.8,
#         top_p=1.0,
#         frequency_penalty=0.3,
#         presence_penalty=0.0,
#     )
#     generated_Correspondence_Courses = chat_completion.choices[0].message.content
#     print("done6")

#     # Major_development_history
#     gpt_input = f"{Major_development_history}"
#     chat_completion = openai.chat.completions.create(
#         model="gpt-4",
#         messages=[{"role": "user", "content": gpt_input}],
#         temperature=0.8,
#         top_p=1.0,
#         frequency_penalty=0.3,
#         presence_penalty=0.0,
#     )
#     generated_Major_development_history = chat_completion.choices[0].message.content
#     print("done7")

#     # Cutting_edge_field
#     gpt_input = f"{Cutting_edge_field}"
#     chat_completion = openai.chat.completions.create(
#         model="gpt-4",
#         messages=[{"role": "user", "content": gpt_input}],
#         temperature=0.8,
#         top_p=1.0,
#         frequency_penalty=0.3,
#         presence_penalty=0.0,
#     )
#     generated_Cutting_edge_field = chat_completion.choices[0].message.content
#     print("done8")

#     # Visualization_p1
#     gpt_input = f"{Visualization_p1}"
#     chat_completion = openai.chat.completions.create(
#         model="gpt-4",
#         messages=[{"role": "user", "content": gpt_input}],
#         temperature=0.8,
#         top_p=1.0,
#         frequency_penalty=0.3,
#         presence_penalty=0.0,
#     )
#     generated_Visualization_p1 = chat_completion.choices[0].message.content
#     print("done9")

#     # Visualization_p2
#     gpt_input = f"{Visualization_p2}"
#     chat_completion = openai.chat.completions.create(
#         model="gpt-4",
#         messages=[{"role": "user", "content": gpt_input}],
#         temperature=0.8,
#         top_p=1.0,
#         frequency_penalty=0.3,
#         presence_penalty=0.0,
#     )
#     generated_Visualization_p2 = chat_completion.choices[0].message.content
#     print("done10")

#     # Highschool_activities
#     gpt_input = f"{Highschool_activities}"
#     chat_completion = openai.chat.completions.create(
#         model="gpt-4",
#         messages=[{"role": "user", "content": gpt_input}],
#         temperature=0.8,
#         top_p=1.0,
#         frequency_penalty=0.3,
#         presence_penalty=0.0,
#     )
#     generated_Highschool_activities = chat_completion.choices[0].message.content
#     print("done11")

    generated_content = [
    #     generated_summary,
    #     generated_major_prompt_two,
        major_list,
        # generated_major_prompt_three,
    #     # generated_potential_major,
    #     # generated_Correspondence_college_recommendations,
    #     # generated_Correspondence_Courses,
    #     # generated_Major_development_history,
    #     # generated_Cutting_edge_field,
    #     # generated_Visualization_p1,
    #     # generated_Visualization_p2,
    #     # generated_Highschool_activities,
    ]
    return generated_content


class PDF(FPDF):
    def header(self):
        self.set_font('Arial', 'B', 14)
        self.cell(0, 10, 'Generated Report',border=False,ln=1,align='C')
        self.ln(10)

    def footer(self):
        self.set_y(-15)
        self.set_font('helvetica', 'I', 10)
        self.cell(0, 10, f'Page {self.page_no()}/{{nb}}',align='C')

def generate_pdf(generated_content):
    try:
        pdf = PDF(orientation='P', unit='mm', format='A4')
        pdf.add_font('NotoSansCJK', '', '/home/hello/VScode/NotoSansSC-VariableFont_wght.ttf')
        pdf.set_font('NotoSansCJK', '', 14)
        pdf.set_left_margin(15)
        pdf.set_right_margin(15)
        pdf.set_auto_page_break(auto=True, margin=15)

        pdf.add_page()

        for item in generated_content:
            if isinstance(item, str):
                pdf.set_font('NotoSansCJK', '', 14)
                pdf.multi_cell(0, 10, item)
            elif isinstance(item, dict):
                pdf.set_font('NotoSansCJK', '', 14)
                pdf.cell(0, 10, item['title'], ln=True, align='C')
                pdf.set_font('NotoSansCJK', '', 14)
                pdf.set_fill_color(0, 0, 0)
                pdf.multi_cell(60, 10, item['content'], align='C')
            pdf.ln(10)

        pdf_file_name = f'gpt_report_{datetime.now().strftime("%Y%m%d_%H%M%S")}.pdf'
        pdf_file_path = f'/home/hello/Desktop/{pdf_file_name}'
        pdf.set_title('Report')
        pdf.set_author('Sigma')
        pdf.output(pdf_file_path)
        return pdf_file_path

    except Exception as e:
        return f"Error generating PDF: {e}"



@app.get("/generate_pdf")
def main():
    file_path_xlsx = '/home/hello/Desktop/form.xlsx'
    name = 'Jake Li'

    data,name,basic_info,major_preferences,college_preferences,potential_major_exploration,column_AU = process_csv_and_generate_content(file_path_xlsx,name)
    # generated_summary,generated_major_prompt_two,major_list,generated_major_prompt_three,generated_potential_major,generated_Correspondence_college_recommendations,generated_Correspondence_Courses,generated_Major_development_history,generated_Cutting_edge_field,generated_Visualization_p1,generated_Visualization_p2,generated_Highschool_activities=generate_gpt(data,name,basic_info,major_preferences,college_preferences,potential_major_exploration,column_AU) 
    generated_content=generate_gpt(data,name,basic_info,major_preferences,college_preferences,potential_major_exploration,column_AU) 
    pdf_file_path = generate_pdf(generated_content) 
    print(f"PDF generated at {pdf_file_path}")
       return {"message": "PDF generated successfully."}

    
@app.on_event("startup")
async def startup_event():
    main()
