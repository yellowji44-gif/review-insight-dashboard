# 📊 EduPlatform AI 수강평 데이터 자동화 및 반응형 대시보드 시스템

마케팅팀의 수강평 데이터 분석 업무를 완전 자동화하고, 매일 밤 최신 데이터가 반영되는 정적 웹 대시보드(HTML/CSS/Chart.js)를 구축한 End-to-End 자동화 프로젝트입니다.

## 🚀 Key Features (주요 기능)
1. **데이터 파이프라인 자동화**: Pandas를 활용해 5종의 이기종 CSV 데이터 적재 및 결합 정형화
2. **AI & 텍스트 마이닝**: 감성 분석(긍정/중립/부정) 및 빈출 텍스트 키워드 TOP 5 자동 추출
3. **정적 사이트 제너레이션 (SSG)**: Jinja2 엔진을 통해 분석 통계를 HTML에 동적 주입 후 `index.html` 자동 덮어쓰기
4. **모바일 우선 반응형 UI**: 스마트폰 화면에서는 긍정/부정 키워드 카드가 위아래(Stack)로 배치되고, PC 대화면에서는 좌우 가로로 유연하게 확장되는 크로스 브라우징 설계
5. **OS 스케줄러 연동**: Windows 작업 스케줄러(Task Scheduler)를 활용해 매일 자정 무중단 자동 갱신 체계 구축

## 🛠️ Tech Stack
- **Language**: Python (Pandas, NumPy, Jinja2)
- **Frontend**: HTML5, CSS3 (Mobile-First Layout), JavaScript, Chart.js
- **Automation**: Windows Task Scheduler / Batch (`.bat`)

## ⚙️ How to Run
1. 저장소 클론 후 아래 5종의 CSV 데이터 준비 (`create_sample_data.py` 실행 시 자동 생성 가능)
   - `course_reviews.csv`, `courses.csv`, `students.csv`, `teachers.csv`, `monthly_rating_trends.csv`
2. 파이프라인 실행:
   ```bash
   python pipeline.py
