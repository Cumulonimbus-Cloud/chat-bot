import csv

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
    fieldnames = ['학년', '교필 총 학점', '교선 총 학점', '전필 총 학점', '전선 총 학점', '일선 총 학점']
    
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

input_file = 'contents_uk.csv'
data = read_csv(input_file)
credits = calculate_credits(data)
save_to_csv(credits, "contents_uk_summary.csv")