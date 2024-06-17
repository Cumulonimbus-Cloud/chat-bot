import pdfplumber
import pandas as pd
import csv
import re

# PDF 파일을 읽고 CSV 파일로 변환하는 함수
def pdf_to_csv(pdf_path, csv_path):
    def get_column_texts(page, num_columns):
        width = page.width
        height = page.height
        column_width = width / num_columns

        columns_texts = []
        for col in range(num_columns):
            left = col * column_width
            right = (col + 1) * column_width
            top = 0
            bottom = height

            crop_box = (left, top, right, bottom)
            cropped_page = page.within_bbox(crop_box)
            column_text = cropped_page.extract_text()
            columns_texts.append(column_text.strip() if column_text else '')

        return columns_texts

    all_columns_texts = []
    with pdfplumber.open(pdf_path) as pdf:
        for page in pdf.pages:
            num_columns = 2
            columns_texts = get_column_texts(page, num_columns)
            all_columns_texts.append(columns_texts)

    ordered_texts = []
    num_pages = len(all_columns_texts)
    num_columns = len(all_columns_texts[0]) if all_columns_texts else 0

    for page_idx in range(num_pages):
        for col in range(num_columns):
            if col < len(all_columns_texts[page_idx]):
                ordered_texts.append(all_columns_texts[page_idx][col])

    semester_pattern = re.compile(r"\d학년 \d{4}학년도 [^ ]+기")
    course_pattern = re.compile(r"([A-Z]{3}[0-9]{4})\s+(.+?)\s+([0-9]+\.[0-9])\s+([-A-Z][0-9]?\+?)\s+([가-힣]+)")

    semesters = []
    courses = []

    current_semester = None
    for text in ordered_texts:
        lines = text.split('\n')
        for line in lines:
            sem_match = semester_pattern.search(line)
            if sem_match:
                current_semester = sem_match.group()
                semesters.append(current_semester)
            elif "금학기 수강내역" in line:
                current_semester = "금학기 수강내역"
            else:
                course_matches = course_pattern.findall(line)
                if course_matches:
                    courses.append((current_semester, course_matches))

    with open(csv_path, 'w', newline='', encoding='utf-8') as csvfile:
        csv_writer = csv.writer(csvfile)
        csv_writer.writerow(['수강 시기', '과목 코드', '과목명', '학점', '성적', '과목 유형'])

        for semester, course_list in courses:
            for course in course_list:
                csv_writer.writerow([semester] + list(course))