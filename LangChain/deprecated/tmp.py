import requests
from bs4 import BeautifulSoup
import pandas as pd
import csv
from io import StringIO

def get_pandas_as_csv(URL):
    # 공지사항 첫 페이지 URL
    if URL == 2024:
        #2024년도 URL
        base_url = 'https://cse.inha.ac.kr/cse/879/subview.do' 
    elif URL == 2023 :
        #2023년도 URL
        base_url = 'https://cse.inha.ac.kr/cse/879/subview.do?enc=Zm5jdDF8QEB8JTJGZGVwYXJ0bWVudEludHJvJTJGY3NlJTJGMjA2JTJGMjA2JTJGZ3JhZEludHJvLmRvJTNGZmxhZyUzRCUyNnllYXIlM0QyMDIzJTI2' 
    # 헤더 설정
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/73.0.3683.86 Safari/537.36'
    }

    try:
        # 리퀘스트 요청
        response = requests.get(base_url, headers=headers)
        response.raise_for_status()  # 요청 실패 시 예외 발생

        # 수프 생성
        soup = BeautifulSoup(response.text, 'html.parser')

        # 테이블 정보 가져오기
        tables = soup.select('table')

        # 데이터 프레임 리스트 생성
        dfs = []

        # 각 테이블을 데이터프레임으로 변환
        for table in tables:
            dfs.append(pd.read_html(StringIO(str(table)), encoding='utf-8')[0])

        # 데이터프레임 병합
        df = pd.concat(dfs, ignore_index=True)
        # CSV 파일로 저장
        df.to_csv(f'./{URL}년도table_data.csv', index=False, encoding='utf-8-sig')
        

    except requests.exceptions.RequestException as e:
        print(f'Error occurred: {e}')

def get_CSV(URL):

    # CSV 파일 읽기
    with open(f'{URL}년도table_data.csv', 'r', newline='', encoding='utf-8') as csvfile:
        reader = csv.reader(csvfile)
        data = list(reader)
        data[1][0]="졸업요구조건"
        data[1][4]="비고"
        data[2][4]=data[4][1]
        data[3][4]=data[4][1]
        data[4][0]="제2전공 졸업요구조건"
        data[4][1]=data[1][5]
        data[4][2]=data[1][6]
        data[4][3]=data[1][7]
        data[4][4]="비고"
        del data[5][0:4]
        del data[6][0:4]
        del data[7][0:4]
        del data[8][0:4]
        data[5].append(data[6][1])
        data[7].append(data[8][1])
        del data[4][5:]
        del data[8]
        del data[6]
        del data[0]
        del data[0][5:]
        print(data)
        # CSV 파일 쓰기
        
    with open(f'{URL}년도table_data.csv', 'w', newline='', encoding='utf-8-sig') as csvfile:
        writer = csv.writer(csvfile)
        writer.writerows(data)


# CSV 파일 생성 
get_pandas_as_csv(2024)
get_pandas_as_csv(2023)
print('CSV 파일이 생성되었습니다.')
get_CSV(2024)
get_CSV(2023)
print('CSV 파일 편집이 완료되었습니다.')