import openai
import pandas as pd
import yaml
from fpdf import FPDF
from openai import OpenAI
import subprocess
import shutil
import os
import yaml

# Path to the local CSV file
file_path_csv = '/home/hello/Documents/form.csv'

# Initialize result_string with a default value
result_string = "No data available."

results_list = []
try:
    # Try different encodings
    for encoding in ['utf-8']:
        try:
            df = pd.read_csv(file_path_csv, encoding=encoding)
            print(f"Successfully read with encoding: {encoding}")
            break
        except UnicodeDecodeError:
            print(f"Failed with encoding: {encoding}")

    # Check if there is at least one row
    if len(df) > 0:
        # Get the first and last row values
        first_row_values = df.iloc[0].astype(str)
        last_row_values = df.iloc[-1].astype(str)

        # Create a formatted string with paired values
        results_list = [f'"{first}": "{last}"' for first, last in zip(first_row_values, last_row_values)]
    else:
        results_list = ["CSV file is empty."]

except Exception as e:
    print("Error reading CSV file:")
    print(e)
    result_string = f"Error occurred while reading CSV file: {e}"

#print(results_list)

#organize data:

firstpage_summary = "Your character is an elder Based on the questionnaire provided by student Eva Zhao (surrounded by 3 quotation marks), rewrite a story-like summary, no more than 500 words. Please keep the style consistent with the examples below Hello classmates, in this test, I saw a person. . . You are a wise and knowledgeable researcher. You have inexhaustible curiosity, strong logic, and insights that are different from ordinary people. Your thirst for knowledge drives you to stand on the front line of exploring the unknown. Rational, you focus on logical analysis, are good at abstract thinking, and are always ready to find the truth. please fill in the answer from questionnaire (together with question) inside"

major_prompt_one = "You are a top study abroad consultant with many years of education experience. You are especially good at understanding the characteristics of students and making recommendations based on basic data. Next, your task is to help me recommend the most suitable major for this high school student based on a high school student’s questionnaire. You need to give detailed reasons and use the reasons in each case to the detailed information in the questionnaire. You At the same time, sufficient reasoning process needs to be given. In the questionnaire, students will judge the weight of each question or factor. Different weights represent the importance of this factor in major selection (0 means not important at all, 5 means very important). Please combine these weight numbers. Give final recommendation. Your specific task is divided into two steps. The first step is to recommend 10 majors that are most suitable for this student based on the information marked as original information and give reasons. The second step is to select 3 majors from the 10 most suitable majors recommended by this student based on the information marked as supplementary information and give reasons and how these majors match him. As a final result, I hope to have a document containing 10 recommended majors and reasons, 3 most suitable majors and reasons, and each reason should not be less than 300 words."
major_prompt_two = "Please make the first step recommendation of the 10 majors based on the following questionnaire information. During the recommendation process, please pay attention to the weight given by students to each factor. Each recommendation reason cannot be less than 300 words. “please fill in questionnaire information here"
major_prompt_three = "Please continue to the second step of screening the 3 most matching majors based on the following supplementary information. Please give more detailed reasons. Each reason needs enough details, evidence and reasoning process. Each reason should be no less than 300 words. Please also provide the professional matching degree (0 is the least match, 100 is the best match) “please fill in questionnaire information here (rest of part 2)”"

potential_major = "1. Learning difficulty: Some majors may involve high learning difficulty, such as requiring an in-depth understanding of complex theories and concepts or mastering a series of complex technologies and skills. 2. Practical opportunities: Some majors may not have enough practical opportunities, causing students to lack the connection between theory and practical application. 3. Career prospects: Some majors may lack clear or broad career prospects, making it difficult for students to find relevant jobs after graduation. 4. Competitive pressure: Some majors may have highly competitive pressure. For example, some popular majors may have a large number of students competing for limited employment opportunities. 5. Major requirements: Some majors may have strict course requirements or credit requirements, which may result in students not having enough time and opportunities to explore their interests and potential while meeting these requirements. 6. Work stress: Some professions can lead to high-stress jobs, such as those in fields such as medicine, law, or finance that often require working under high pressure and long hours. 7. Dependence on the economic environment or policies: Some majors may be affected by changes in the economic environment or policies, which may affect the job market and salary levels of this major. For example, finance or energy-related majors may be affected by global economic or energy policies. 8. Rapidly changing industry environment: Some majors may face a rapidly changing industry environment, such as technology or media-related majors, and students need to be able to continuously learn and update their knowledge and skills. What you are imitating now is the advisor in the university. Please give the shortcomings of the following three majors based on the above eight dimensions Exercise Science, Biological Science and Physical Therapy. Each dimension of each major needs to be listed. If there are no obvious shortcomings in this dimension, please state it directly. Please be as detailed and detailed as possible and give sufficient evidence and examples. Each point should be no less than 3 sentences. Try to add personal feelings to the description and write about the shortcomings in a more emotional style. Please add detailed examples after each point and make the reasons longer and more detailed."

# Using OpenAI GPT
with open("config.yaml") as f:
    config_yaml = yaml.load(f, Loader=yaml.FullLoader)
openai.api_key = config_yaml['api_key']



try:
    #summary
    gpt_input = f"{firstpage_summary}"
    chat_completion = openai.chat.completions.create(
        model="gpt-3.5-turbo-0125",
        messages=[{"role": "user", "content": gpt_input}]
    )
    generated_summary= chat_completion.choices[0].message.content
    print("done1")
    # generate top major
    gpt_input = f"{major_prompt_one} + {major_prompt_two} + {results_list}"
    chat_completion = openai.chat.completions.create(
        model="gpt-3.5-turbo-0125",
        messages=[{"role": "user", "content": gpt_input}]
    )
    generated_major_prompt_two = chat_completion.choices[0].message.content
    print("done2")

    gpt_input = f"{generated_major_prompt_two}+name the topic three major in a string with no explantions. i.e Computer Science, Math, Areospace Engineering"
    chat_completion = openai.chat.completions.create(
        model="gpt-3.5-turbo-0125",
        messages=[{"role": "user", "content": gpt_input}]
    )
    major_list = chat_completion.choices[0].message.content
    print("done3")

    gpt_input = f"{major_prompt_one} + {major_prompt_three} + {results_list}"
    chat_completion = openai.chat.completions.create(
        model="gpt-3.5-turbo-0125",
        messages=[{"role": "user", "content": gpt_input}]
    )
    generated_major_prompt_three = chat_completion.choices[0].message.content
    print("done4")

    #potential major
    gpt_input = f"{potential_major}"
    chat_completion = openai.chat.completions.create(
        model="gpt-3.5-turbo-0125",
        messages=[{"role": "user", "content": gpt_input}]
    )
    generated_potential_major = chat_completion.choices[0].message.content
    print("done5")

    #more prompt

    Correspondence_college_recommendations = "This user hopes to study for undergraduate studies in the "+ results_list[66] + "in the future. He may major in + major_list + Please recommend to him that these three majors are the most representative in these countries. Two universities of the same gender and give detailed recommendation reasons. Each recommendation reason should be no less than 300 words."

    Correspondence_Courses = "Assume that the three most suitable majors you recommend to Eva are" + major_list + "Please list the 7 basic courses and 3 advanced courses for this major at the undergraduate level. Please display the above course name in this format: major name; course name"

    Major_development_history = "Please list the five most important turning points and their timing and impact in the past 50 years of the following three majors:" + major_list + "A description of each turning point and its impact must be no less than 200 words."

    Cutting_edge_field = "Please list the 3 most cutting-edge fields in academia and industry for each of the following three majors:" + major_list + "Please describe each area in detail. The description of each area should be no less than 200 words."

    Visualization_p1 = "1. Knowledge Mastery: This dimension can measure students’ understanding of the core concepts and skills of the subject through tests or assessments. This may include a student's class performance, assignments, projects, tests and exam results. 2. Interest Level: This dimension can measure students’ interest in the subject through surveys or questionnaires. This may include how often students choose to study the subject, how much time they devote to the subject, and how self-motivated they are in the subject. 3. Practical Application: This dimension can assess students’ practical application ability of the subject. This may include how students performed in experiments, projects, or internships, and how they applied what they learned to real-world problems. 4. Innovative Capability: This dimension can be measured by observing students’ innovative performance in the subject. This might include whether they can come up with new ideas, new ways of solving problems, or create new work. 5. Future Commitment: This dimension can be measured by asking students about their willingness to invest more time and energy in the subject. This may include their plans for future work or further study in this area. Please rate the student's 'Engineering Subject', 'Science Subject', 'Social Science Subject', and 'Social Humanities Subject' in the corresponding five dimensions based on the results of the following questionnaire (0-5 points) fill in the part 3 of questionnaire information here"

    Visualization_p2 = "Please refer to the format and content of the paragraphs in parentheses below and the questionnaire information in below for Albert's recommended majors Business Management, Economics and Finance and their corresponding five dimensions of 'knowledge mastery' and 'passion level'. 'Practical ability', 'Innovative ability', 'Willingness to invest in the future', write an analysis. (sports medicine: - Knowledge mastery: Eva has a high interest and advantage in biological sciences in high school, which will help her master relevant biological knowledge in the field of sports medicine. In addition, her strong subject within the natural science subject range is biology, which means that she may already have a certain knowledge base in biology. Therefore, Eva may have a high level of knowledge in the field of sports medicine, with a score of 4. - Level of passion: Eva clearly stated in her future career preferences that she will engage in fields related to sports medicine, which shows that she has a high degree of passion for this profession. In addition, volleyball is among her favorite extracurricular activities, which also aligns with the relevance of sports medicine. Therefore, Eva's passion for sports medicine may be high, with a score of 5. - Practical application ability: Sports medicine emphasizes the practical application of sports injuries and rehabilitation. Eva stated in her future career preferences that she hopes to engage in work related to sports rehabilitation, which shows that she has a high demand and willingness for practical application ability. In addition, she may have developed some athletic rehabilitation practices in activities such as volleyball, drama, and basketball. Therefore, Eva's practical application ability in the field of sports medicine may be high, with a score of 4. - Innovation ability: The field of sports medicine requires constant exploration of new treatment methods and rehabilitation techniques, and Eva's literary hobby in high school may help cultivate her innovation ability. Although the ability to innovate is not the most important characteristic in sports medicine, she may show some potential for innovation in research and practice. Therefore, Eva's innovation ability in the field of sports medicine may be high, with a score of 3. - Willingness to invest in the future: Eva clearly expressed her interest in fields related to sports medicine and sports rehabilitation in her future career preferences, which shows that she has a high willingness to invest in this field. Her family also provides financial support, which may provide her with certain resources and opportunities in study and practice. Therefore, Eva's willingness to invest in the future in the field of sports medicine may be relatively high, with a score of 4. Comprehensive consideration, based on Eva's interests in different disciplines and the assessment of the five major dimensions, the recommended majors include sports medicine, rehabilitation science and biological science. In these areas, Eva shows a high degree of interest and matching. She has a good knowledge and passion for biology, and she also shows a high demand and willingness for practical application ability and future investment willingness. Regarding innovation ability, Eva may need further training and training in these disciplines. It is recommended that Eva comprehensively consider her own interests and comprehensive abilities when choosing a major and have a clear understanding of future career plans to make the decision that best suits her.) “please fill in part 1 and part 2 of questionnaire information”"

    Highschool_activities = "Your current role is that of a senior college counselor. Your assignment is to plan college application activities for a high school student based on the following framework. Her target majors are: exercise science, biological science, and physical therapy. The activity planning framework is: activities within a week (visits, lectures), activities within a month (summer school, reading, small research, Coursera courses), activities within a year (scientific research, internships, volunteers), and background improvement planning (focusing on scientific research and open-ended project-based learning, real free resources and paid resources) Ultimately what I want to see is a complete plan for each major. Please provide creative and unique event planning. Each activity description must be no less than 300 words."

    # Correspondence_college_recommendations
    gpt_input = f"{Correspondence_college_recommendations}"
    chat_completion = openai.chat.completions.create(
        model="gpt-3.5-turbo-0125",
        messages=[{"role": "user", "content": gpt_input}]
    )
    generated_Correspondence_college_recommendations = chat_completion.choices[0].message.content

    # Correspondence_Courses
    gpt_input = f"{Correspondence_Courses}"
    chat_completion = openai.chat.completions.create(
        model="gpt-3.5-turbo-0125",
        messages=[{"role": "user", "content": gpt_input}]
    )
    generated_Correspondence_Courses = chat_completion.choices[0].message.content
    print("done6")

    # Major_development_history
    gpt_input = f"{Major_development_history}"
    chat_completion = openai.chat.completions.create(
        model="gpt-3.5-turbo-0125",
        messages=[{"role": "user", "content": gpt_input}]
    )
    generated_Major_development_history = chat_completion.choices[0].message.content
    print("done7")

    # Cutting_edge_field
    gpt_input = f"{Cutting_edge_field}"
    chat_completion = openai.chat.completions.create(
        model="gpt-3.5-turbo-0125",
        messages=[{"role": "user", "content": gpt_input}]
    )
    generated_Cutting_edge_field = chat_completion.choices[0].message.content
    print("done8")

    # Visualization_p1
    gpt_input = f"{Visualization_p1}"
    chat_completion = openai.chat.completions.create(
        model="gpt-3.5-turbo-0125",
        messages=[{"role": "user", "content": gpt_input}]
    )
    generated_Visualization_p1 = chat_completion.choices[0].message.content
    print("done9")

    # Visualization_p2
    gpt_input = f"{Visualization_p2}"
    chat_completion = openai.chat.completions.create(
        model="gpt-3.5-turbo-0125",
        messages=[{"role": "user", "content": gpt_input}]
    )
    generated_Visualization_p2 = chat_completion.choices[0].message.content
    print("done10")

    # Highschool_activities
    gpt_input = f"{Highschool_activities}"
    chat_completion = openai.chat.completions.create(
        model="gpt-3.5-turbo-0125",
        messages=[{"role": "user", "content": gpt_input}]
    )
    generated_Highschool_activities = chat_completion.choices[0].message.content
    print("done11")

    # Initialize FPDF object
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", size=12)

    # Assuming you have these response variables from previous parts of your code
    # generated_summary, generated_major_prompt_two, etc.

except Exception as e:
    print(f"An overall error occurred: {e}")

file_path = '/home/hello/Desktop/gpt_formal_response.text'

def read_and_modify_text(file_path, replacements):
    # Read the original .tex file
    with open(file_path, 'r', encoding='utf-8') as file:
        content = file.read()

    # Replacing multiple placeholders
    # 'replacements' is a dictionary where the keys are placeholders and the values are their replacements
    for placeholder, replacement in replacements.items():
        content = content.replace(placeholder, replacement)

    # Save the modified content to a new .tex file
    modified_file_path = 'modified_' + file_path
    with open(modified_file_path, 'w', encoding='utf-8') as file:
        file.write(content)

    return modified_file_path

def compile_text_to_pdf(text_file_path):
    # Absolute path to the pdflatex executable
    pdflatex_path = '/Library/Text/textbin/pdflatex'
    # Use the absolute path in the subprocess call
    subprocess.run([pdflatex_path, text_file_path], check=True)
    # The name of the PDF will match the name of the .tex file but with .pdf extension
    pdf_file_name = text_file_path.replace('.text', '.pdf')

    # Define the target directory where you want to save the PDF
    target_directory = '/home/hello/Desktop/gpt_standford'

    # Ensure the target directory exists
    os.makedirs(target_directory, exist_ok=True)

    # Construct the target path for the PDF file
    target_pdf_path = os.path.join(target_directory, os.path.basename(pdf_file_name))

    # Move the PDF file to the target directory
    shutil.move(pdf_file_name, target_pdf_path)
    print(f"PDF file has been saved to: {target_pdf_path}")

if __name__ == '__main__':
    original_text_path = 'gpt_formal_response.text'  # Path to your original .tex file
    # Dictionary of placeholders and their replacements
    replacements = {
        '%%introductive_paragraph%%': generated_summary,
        '%%person_name%%': 'replacement for placeholder 2',
        '%%major_one%%': major_prompt_three,
        '%%three_major_universities%%': generated_Correspondence_college_recommendations,
        '%%new_major_tech%%': generated_Major_development_history,
        '%%major_top_contribution%%': generated_Cutting_edge_field,
        '%%major_reason_rating%%': generated_Visualization_p1+generated_Visualization_p2,
        '%%activities_week_year%%': generated_Highschool_activities,
        '%%rest_seven_major%%': major_prompt_three
    }
    modified_text_path = read_and_modify_text(original_text_path, replacements)
    compile_text_to_pdf(modified_text_path)