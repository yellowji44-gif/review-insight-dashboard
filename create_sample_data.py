# create_sample_data.py
import pandas as pd
import numpy as np

# 1. teachers.csv
teachers_df = pd.DataFrame({
    'Teacher': ['김민수', '이지영', '박도현', '정수연', '한지민'],
    'Category': ['국어', '영어', '수학', '과학', '사회']
})
teachers_df.to_csv('teachers.csv', index=False, encoding='utf-8-sig')

# 2. courses.csv
courses_df = pd.DataFrame({
    'Course_ID': [101, 102, 103, 104, 105],
    'Course_Name': ['수능 국어 마스터', '영어 회화 핵심 패턴', '고등 수학 (상)', '물리학 개론', '한국사 정복'],
    'Teacher': ['김민수', '이지영', '박도현', '정수연', '한지민'],
    'Category': ['국어', '영어', '수학', '과학', '사회']
})
courses_df.to_csv('courses.csv', index=False, encoding='utf-8-sig')

# 3. students.csv
students_df = pd.DataFrame({
    'Student_ID': range(1, 51),
    'Grade': ['고1', '고2', '고3'] * 16 + ['고1', '고2']
})
students_df.to_csv('students.csv', index=False, encoding='utf-8-sig')

# 4. course_reviews.csv
np.random.seed(42)
n_reviews = 300
reviews_df = pd.DataFrame({
    'Review_ID': range(1000, 1000 + n_reviews),
    'Course_ID': np.random.choice([101, 102, 103, 104, 105], n_reviews),
    'Student_ID': np.random.randint(1, 51, n_reviews),
    'Rating': np.random.choice([1, 2, 3, 4, 5], n_reviews, p=[0.05, 0.1, 0.15, 0.4, 0.3]),
    'Review_Text': np.random.choice([
        "배속 조절 원활 및 편의성이 정말 좋습니다! 최고예요.",
        "동영상 화질 및 오디오 고품질이라 몰입감이 높습니다.",
        "모바일 기기 재생 최적화가 잘 되어 있어서 지하철에서 보기 편해요.",
        "내신/시험 성적 향상 직결되는 핵심만 짚어줍니다.",
        "온라인 집중도 및 상세한 설명 훌륭합니다.",
        "미디어 플레이어 볼륨 작동 에러가 가끔 발생합니다.",
        "과도한 숙제 및 과제량 부담이 조금 있네요.",
        "설명 속도가 너무 빠르고 어려워서 따라가기 벅찹니다.",
        "커리큘럼 구성의 체계성 부족이 느껴집니다.",
        "하위권/기초 학생 배려 부족 아쉽습니다."
    ], n_reviews)
})
reviews_df.to_csv('course_reviews.csv', index=False, encoding='utf-8-sig')

# 5. monthly_rating_trends.csv
trends_df = pd.DataFrame({
    'Month': ['2026-01', '2026-02', '2026-03', '2026-04', '2026-05', '2026-06'],
    'Average_Rating': [3.6, 3.65, 3.72, 3.8, 3.75, 3.85]
})
trends_df.to_csv('monthly_rating_trends.csv', index=False, encoding='utf-8-sig')

print("[SUCCESS] 5종의 샘플 CSV 데이터 파일이 성공적으로 생성되었습니다!")
