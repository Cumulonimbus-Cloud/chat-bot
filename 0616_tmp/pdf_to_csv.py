# pip install PyPDF2 pdfplumber

import pdfplumber
import pandas as pd
import csv, re, os

# 참고용 성적표 PDF 파일 경로 설정
pdf_path = '/home/ec2-user/environment/Chatbot/0616_tmp/assets/score_Hwang.pdf'

# 파일 경로에서 마지막 파일 이름만 추출
file_name = os.path.splitext(os.path.basename(pdf_path))[0]


# 페이지를 세로로 나누는 구분선을 정의하는 함수
def get_column_texts(page, num_columns):
    width = page.width
    height = page.height
    column_width = width / num_columns

    columns_texts = []
    for col in range(num_columns):
        # 각 열의 좌표 영역 설정
        left = col * column_width
        right = (col + 1) * column_width
        top = 0
        bottom = height

        # 해당 영역의 텍스트 추출
        crop_box = (left, top, right, bottom)
        cropped_page = page.within_bbox(crop_box)
        column_text = cropped_page.extract_text()
        columns_texts.append(column_text.strip() if column_text else '')

    return columns_texts

# PDF 파일 열기 및 텍스트 추출
all_columns_texts = []
with pdfplumber.open(pdf_path) as pdf:
    for page in pdf.pages:
        num_columns = 2  # 페이지를 세로로 2등분 (pdf에 따라 조정 가능)
        columns_texts = get_column_texts(page, num_columns)
        all_columns_texts.append(columns_texts)

# 텍스트를 필요한 형태로 가공 (위치에 따른 재배치)
ordered_texts = []
num_pages = len(all_columns_texts)  # 전체 페이지 수
num_columns = len(all_columns_texts[0]) if all_columns_texts else 0  # 첫 페이지의 열 개수

# 페이지 순서대로 교차 배치
for page_idx in range(num_pages):
    for col in range(num_columns):
        if col < len(all_columns_texts[page_idx]):
            ordered_texts.append(all_columns_texts[page_idx][col])

# 학기 정보 및 과목 정보 추출을 위한 정규 표현식 패턴
semester_pattern = re.compile(r"\d학년 \d{4}학년도 [^ ]+기")
course_pattern = re.compile(r"([A-Z]{3}[0-9]{4})\s+(.+?)\s+([0-9]+\.[0-9])\s+([-A-Z][0-9]?\+?)\s+([가-힣]+)")
score_pattern_1 = re.compile(r"신청학점\(A\) (\d+)")
score_pattern_2 = re.compile(r"취득학점\(B\) (\d+)")
score_pattern_3 = re.compile(r"평점누계\(C\) ([\d.]+)")
score_pattern_4 = re.compile(r"평점평균\(C/A\) ([\d.]+)")

# 학기 및 과목 정보를 저장할 리스트
semesters = []
courses = []
scores = {
    "신청학점": None,
    "취득학점": None,
    "평점누계": None,
    "평점평균": None
}

# 정렬된 텍스트에서 학기 및 과목 정보 추출
current_semester = None
for text in ordered_texts:
    # 텍스트를 줄 단위로 분리
    lines = text.split('\n')
    for line in lines:
        sem_match = semester_pattern.search(line)
        s1_match = score_pattern_1.search(line)
        s2_match = score_pattern_2.search(line)
        s3_match = score_pattern_3.search(line)
        s4_match = score_pattern_4.search(line)
        
        if s1_match:
            scores["신청학점"] = s1_match.group()
        if s2_match:
            scores["취득학점"] = s2_match.group()
        if s3_match:
            scores["평점누계"] = s3_match.group()
        if s4_match:
            scores["평점평균"] = s4_match.group()    
        
        if sem_match:
            current_semester = sem_match.group()
            semesters.append(current_semester)
        elif "금학기 수강내역" in line:
            current_semester = "금학기 수강내역"
        else:
            course_matches = course_pattern.findall(line)
            if course_matches:
                courses.append((current_semester, course_matches))

# 파일 저장 위치
save_dir_path = "/home/ec2-user/environment/Chatbot/0616_tmp/assets/"

# scores 정보를 csv 파일로 저장

csv_file = save_dir_path + "total_" + file_name + ".csv"
csv_columns = list(scores.keys())

try:
    with open(csv_file, 'w', newline='', encoding='utf-8') as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=csv_columns)
        writer.writeheader()
        writer.writerow(scores)
except IOError:
    print("I/O error")

csv_filename = save_dir_path +'contents_' + file_name + '.csv'

# CSV 파일 저장
with open(csv_filename, 'w', newline='', encoding='utf-8') as csvfile:
    csv_writer = csv.writer(csvfile)

    # CSV 헤더 작성
    csv_writer.writerow(['수강 시기', '과목 코드', '과목명', '학점', '성적', '과목 유형'])

    # 과목 정보를 CSV에 작성
    for semester, course_list in courses:
        for course in course_list:
            csv_writer.writerow([semester] + list(course))


# CSV 파일 불러오기
# df = pd.read_csv('contents_uk.csv')

# 데이터프레임 출력
#display(df)


### csv suumary


# CSV 파일에서 데이터 읽어오기
def read_csv(file_path):
    with open(file_path, mode='r', newline='', encoding='utf-8-sig') as file:
        reader = csv.DictReader(file)
        data = [row for row in reader]
    return data

# 각 학년별 학점 계산
def calculate_credits(data):
    credits = {
        '1학년': {'교필': 0, '교선': 0, '전필': 0, '전선': 0, '일선': 0, '교직': 0},
        '2학년': {'교필': 0, '교선': 0, '전필': 0, '전선': 0, '일선': 0, '교직': 0},
        '3학년': {'교필': 0, '교선': 0, '전필': 0, '전선': 0, '일선': 0, '교직': 0},
        '4학년': {'교필': 0, '교선': 0, '전필': 0, '전선': 0, '일선': 0, '교직': 0},
        '금학기 수강내역': {'교필': 0, '교선': 0, '전필': 0, '전선': 0, '일선': 0, '교직': 0}
    }
    
    for row in data:
        year = row['수강 시기'].split()[0]
        credit_type = row['과목 유형']
        credit = float(row['학점'])
        
        if year in credits:
            credits[year][credit_type] += credit
    
    return credits

# 학점 계산 결과를 CSV 파일로 저장
def save_to_csv(credits, output_file='credits_summary.csv'):
    fieldnames = ['학년', '교필 총 학점', '교선 총 학점', '전필 총 학점', '전선 총 학점', '일선 총 학점', '교직 총 학점']
    
    with open(output_file, mode='w', newline='', encoding='utf-8-sig') as file:
        writer = csv.DictWriter(file, fieldnames=fieldnames)
        writer.writeheader()
        
        for year, credit_dict in credits.items():
            writer.writerow({
                '학년': year,
                '교필 총 학점': credit_dict['교필'],
                '교선 총 학점': credit_dict['교선'],
                '전필 총 학점': credit_dict['전필'],
                '전선 총 학점': credit_dict['전선'],
                '일선 총 학점': credit_dict['일선'],
                '교직 총 학점': credit_dict['교직']
            })

input_file = csv_filename
data = read_csv(input_file)
credits = calculate_credits(data)
summary_filename = save_dir_path +"summary_" + file_name + ".csv"
save_to_csv(credits, summary_filename)

print(f'{csv_filename} 파일이 성공적으로 저장되었습니다.')
print(f'{csv_file} 파일이 성공적으로 저장되었습니다.')
print(f'{summary_filename} 파일이 성공적으로 저장되었습니다.')

