# -*- coding: utf-8 -*-
import os
import re
from datetime import datetime
from collections import Counter
import pandas as pd
import numpy as np
from jinja2 import Template

def run_analysis_pipeline():
    print("[INFO] 데이터 분석 파이프라인을 시작합니다...")

    # 1. 데이터 적재 (CSV 파일 로드)
    try:
        reviews = pd.read_csv('course_reviews.csv')
        courses = pd.read_csv('courses.csv')
        students = pd.read_csv('students.csv')
        teachers = pd.read_csv('teachers.csv')
        trends = pd.read_csv('monthly_rating_trends.csv')
    except Exception as e:
        print(f"[ERROR] 데이터 파일 로드 실패: {e}")
        print("동일한 디렉토리에 5개의 CSV 파일이 존재하는지 확인하세요.")
        return

    # 2. 데이터 병합 및 기초 탐색
    reviews_merged = reviews.merge(courses, on='Course_ID', how='left')
    
    total_reviews = len(reviews_merged)
    avg_rating = round(reviews_merged['Rating'].mean(), 2)
    
    # 3. 감성 분류 (Rating 기준: 4~5점 긍정, 3점 중립, 1~2점 부정)
    reviews_merged['Sentiment'] = np.where(
        reviews_merged['Rating'] >= 4, 'Positive', 
        np.where(reviews_merged['Rating'] == 3, 'Neutral', 'Negative')
    )
    
    sentiment_counts = reviews_merged['Sentiment'].value_counts()
    pos_ratio = round((sentiment_counts.get('Positive', 0) / total_reviews) * 100, 1)
    neu_ratio = round((sentiment_counts.get('Neutral', 0) / total_reviews) * 100, 1)
    neg_ratio = round((sentiment_counts.get('Negative', 0) / total_reviews) * 100, 1)

    # 4. 리뷰 텍스트 기반 핵심 키워드/구절 추출 함수
    def get_top_phrases(text_series, top_n=5):
        phrases = []
        for text in text_series.dropna().astype(str):
            parts = [p.strip() for p in text.replace('!', '.').replace('?', '.').split('.') if p.strip()]
            phrases.extend(parts)
        return Counter(phrases).most_common(top_n)

    pos_keywords = get_top_phrases(reviews_merged[reviews_merged['Sentiment'] == 'Positive']['Review_Text'])
    neg_keywords = get_top_phrases(reviews_merged[reviews_merged['Sentiment'] == 'Negative']['Review_Text'])

    # 5. 카테고리별 세부 분석
    cat_stats = reviews_merged.groupby('Category')['Rating'].mean().sort_values(ascending=False).to_dict()
    category_labels = list(cat_stats.keys())
    category_ratings = [round(v, 2) for v in cat_stats.values()]

    # 6. 강사진별 성과 스코어보드 생성
    teacher_groupby = reviews_merged.groupby(['Teacher', 'Category']).agg(
        review_count=('Review_ID', 'count'),
        avg_rating=('Rating', 'mean')
    ).reset_index().sort_values(by='avg_rating', ascending=False)
    
    teacher_list = []
    for _, row in teacher_groupby.iterrows():
        rating = round(row['avg_rating'], 2)
        if rating >= 3.7:
            status, status_class = "최우수 콘텐츠", "badge-pos"
        elif rating <= 3.45:
            status, status_class = "모니터링 대상", "badge-neg"
        else:
            status, status_class = "안정", "badge-pos"
            
        teacher_list.append({
            'name': row['Teacher'], 
            'category': row['Category'], 
            'count': row['review_count'],
            'rating': rating, 
            'status': status, 
            'status_class': status_class
        })

    updated_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

    # 7. HTML 대시보드 템플릿 정의 (모바일 우선 반응형 + 키워드 카드 세로 배치 고정 아키텍처)
    html_template = """<!DOCTYPE html>
    <html lang="ko">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0, maximum-scale=1.0, user-scalable=no">
        <title>EduPlatform 데이터 인사이트 대시보드</title>
        <link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;600;700&family=Noto+Sans+KR:wght@400;700&display=swap" rel="stylesheet">
        <script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
        <style>
            :root { --bg-main: #f8fafc; --bg-card: #ffffff; --text-primary: #1e293b; --text-secondary: #64748b; --primary: #4f46e5; --success: #10b981; --warning: #f59e0b; --danger: #ef4444; --border: #e2e8f0; }
            * { box-sizing: border-box; margin: 0; padding: 0; font-family: 'Inter', 'Noto Sans KR', sans-serif; }
            
            body { background-color: var(--bg-main); color: var(--text-primary); padding: 16px; min-width: 320px; overflow-x: hidden; }
            .container { max-width: 1400px; margin: 0 auto; width: 100%; }
            
            header { display: flex; flex-direction: column; align-items: flex-start; margin-bottom: 24px; border-bottom: 2px solid var(--border); padding-bottom: 16px; gap: 12px; }
            header h1 { font-size: 20px; font-weight: 700; color: var(--primary); word-break: keep-all; }
            .update-badge { background-color: var(--border); padding: 6px 12px; border-radius: 20px; font-size: 12px; color: var(--text-secondary); font-weight: 600; }
            
            /* KPI 대시보드 상단 그리드 */
            .kpi-grid { display: grid; grid-template-columns: repeat(2, 1fr); gap: 12px; margin-bottom: 24px; width: 100%; }
            @media screen and (max-width: 480px) { .kpi-grid { grid-template-columns: 1fr; } }
            .kpi-card { background: var(--bg-card); border: 1px solid var(--border); border-radius: 12px; padding: 16px; box-shadow: 0 1px 3px rgba(0,0,0,0.05); min-width: 0; }
            .kpi-card h3 { font-size: 12px; color: var(--text-secondary); margin-bottom: 6px; }
            .kpi-card .value { font-size: 22px; font-weight: 700; word-break: break-all; }
            
            /* 차트 레이아웃 */
            .dashboard-grid { display: flex; flex-direction: column; gap: 16px; margin-bottom: 24px; width: 100%; }
            .chart-main-card, .chart-sub-card { width: 100%; min-width: 0; }
            
            /* 키워드 카드 영역: 모바일에서 무조건 '긍정 카드 위, 부정 카드 아래' 수직 배치 고정 */
            .keyword-grid { display: block !important; width: 100% !important; margin-bottom: 24px; }
            .keyword-grid .card { display: block !important; width: 100% !important; margin-bottom: 16px !important; }
            .keyword-grid .card:last-child { margin-bottom: 0 !important; }
            
            /* 공통 카드 사양 */
            .card { background: var(--bg-card); border: 1px solid var(--border); border-radius: 12px; padding: 20px; box-shadow: 0 1px 3px rgba(0,0,0,0.05); min-width: 0; width: 100%; overflow: hidden; }
            .card-title { font-size: 16px; font-weight: 600; margin-bottom: 16px; word-break: keep-all; }
            .chart-container { height: 260px; width: 100%; max-width: 100%; position: relative; overflow: hidden; }
            
            /* 리스트 스타일 */
            .kw-list { list-style: none; }
            .kw-item { display: flex; justify-content: space-between; align-items: center; padding: 10px 0; border-bottom: 1px solid var(--border); gap: 8px; }
            .kw-item span { font-size: 13px; line-height: 1.4; word-break: break-all; }
            .badge-pos { background: #ecfdf5; color: var(--success); padding: 4px 6px; border-radius: 6px; font-weight: 600; font-size: 12px; white-space: nowrap; }
            .badge-neg { background: #fef2f2; color: var(--danger); padding: 4px 6px; border-radius: 6px; font-weight: 600; font-size: 12px; white-space: nowrap; }
            
            /* 테이블 반응형 래퍼 */
            .table-responsive { width: 100%; overflow-x: auto; -webkit-overflow-scrolling: touch; margin-top: 10px; border-radius: 8px; border: 1px solid var(--border); }
            table { width: 100%; border-collapse: collapse; min-width: 550px; background: var(--bg-card); }
            th, td { padding: 12px 10px; text-align: left; border-bottom: 1px solid var(--border); font-size: 13px; }
            th { color: var(--text-secondary); font-weight: 600; background: #fafafa; }
            
            .marketing-section { background: linear-gradient(135deg, #6366f1 0%, #4f46e5 100%); color: white; border-radius: 12px; padding: 24px; margin-bottom: 24px; width: 100%; }
            .marketing-grid { display: flex; flex-direction: column; gap: 12px; margin-top: 16px; }
            .copy-card { background: rgba(255, 255, 255, 0.1); border: 1px solid rgba(255, 255, 255, 0.2); border-radius: 8px; padding: 16px; min-width: 0; }
            .copy-btn { background: white; color: var(--primary); border: none; padding: 6px 12px; border-radius: 6px; font-weight: 600; cursor: pointer; margin-top: 10px; font-size: 13px; }

            /* 데스크톱 PC 전용 환경 (폭 768px 이상에서 가로 정렬 확장) */
            @media screen and (min-width: 768px) {
                body { padding: 24px; }
                header { flex-direction: row; justify-content: space-between; align-items: center; margin-bottom: 32px; }
                header h1 { font-size: 26px; }
                .update-badge { font-size: 13px; }
                
                .kpi-grid { grid-template-columns: repeat(4, 1fr); gap: 20px; margin-bottom: 32px; }
                .kpi-card { padding: 24px; }
                .kpi-card h3 { font-size: 14px; }
                .kpi-card .value { font-size: 28px; }
                
                .dashboard-grid { flex-direction: row; gap: 24px; margin-bottom: 32px; }
                .chart-main-card { flex: 2; }
                .chart-sub-card { flex: 1; }
                
                /* PC 화면에서는 키워드 카드를 좌우 가로 배치로 확장 */
                .keyword-grid { display: flex !important; flex-direction: row !important; gap: 24px !important; margin-bottom: 32px; }
                .keyword-grid .card { flex: 1 !important; width: auto !important; margin-bottom: 0 !important; }
                
                .card { padding: 24px; }
                .card-title { font-size: 18px; margin-bottom: 20px; }
                .chart-container { height: 300px; }
                
                .kw-item span { font-size: 14px; }
                .badge-pos, .badge-neg { font-size: 13px; padding: 4px 8px; }
                th, td { padding: 14px; font-size: 14px; }
                
                .marketing-section { padding: 32px; margin-bottom: 32px; }
                .marketing-grid { display: grid; grid-template-columns: repeat(2, 1fr); gap: 20px; }
                .copy-card { padding: 20px; }
                .copy-btn { padding: 8px 16px; margin-top: 12px; font-size: 14px; }
            }
        </style>
    </head>
    <body>
    <div class="container">
        <header>
            <div>
                <h1>EduPlatform AI 리뷰 인사이트 대시보드</h1>
                <p style="color: var(--text-secondary); margin-top: 4px;">자동화 데이터 파이프라인 빌드 완료</p>
            </div>
            <div class="update-badge">최종 데이터 갱신: {{ updated_time }}</div>
        </header>

        <div class="kpi-grid">
            <div class="kpi-card"><h3>분석된 총 수강평 수</h3><div class="value">{{ total_reviews }}</div></div>
            <div class="kpi-card"><h3>전체 평균 평점</h3><div class="value" style="color: var(--primary);">{{ avg_rating }} <span style="font-size: 14px; color:var(--text-secondary);">/ 5.0</span></div></div>
            <div class="kpi-card"><h3>긍정 여론 비중</h3><div class="value" style="color: var(--success);">{{ pos_ratio }}%</div></div>
            <div class="kpi-card"><h3>부정 여론 비중</h3><div class="value" style="color: var(--danger);">{{ neg_ratio }}%</div></div>
        </div>

        <div class="dashboard-grid">
            <div class="card chart-main-card">
                <div class="card-title">Category 별 평균 평점 지표</div>
                <div class="chart-container"><canvas id="categoryChart"></canvas></div>
            </div>
            <div class="card chart-sub-card">
                <div class="card-title">전체 감성 분포 비중</div>
                <div class="chart-container"><canvas id="sentimentChart"></canvas></div>
            </div>
        </div>

        <!-- 키워드 카드 영역 (모바일 위아래 세로 배치 / PC 가로 배치 자동 전환) -->
        <div class="keyword-grid">
            <div class="card">
                <div class="card-title">👍 수강생 열광 포인트 키워드 TOP 5</div>
                <ul class="kw-list">
                    {% for kw, count in pos_keywords %}
                    <li class="kw-item"><span>{{ loop.index }}. {{ kw }}</span> <span class="badge-pos">{{ count }}회 언급</span></li>
                    {% endfor %}
                </ul>
            </div>
            <div class="card">
                <div class="card-title">👎 수강생 진짜 불만 키워드 TOP 5</div>
                <ul class="kw-list">
                    {% for kw, count in neg_keywords %}
                    <li class="kw-item"><span>{{ loop.index }}. {{ kw }}</span> <span class="badge-neg">{{ count }}회 언급</span></li>
                    {% endfor %}
                </ul>
            </div>
        </div>

        <div class="card" style="margin-bottom: 32px;">
            <div class="card-title">강사진별 수강평 성과 스코어보드</div>
            <div class="table-responsive">
                <table>
                    <thead>
                        <tr><th>강사명</th><th>담당 카테고리</th><th>누적 리뷰 수</th><th>평균 평점</th><th>상태 지표</th></tr>
                    </thead>
                    <tbody>
                        {% for t in teacher_list %}
                        <tr>
                            <td><strong>{{ t.name }}</strong></td><td>{{ t.category }}</td><td>{{ t.count }}</td>
                            <td>{{ t.rating }} / 5.0</td><td><span class="{{ t.status_class }}">{{ t.status }}</span></td>
                        </tr>
                        {% endfor %}
                    </tbody>
                </table>
            </div>
        </div>

        <div class="marketing-section">
            <h2>🎯 실시간 데이터 기반 즉시 카피라이팅 추천</h2>
            <div class="marketing-grid">
                <div class="copy-card">
                    <p id="copy1">"끊김 없는 몰입, 내 맘대로 조절하는 초고화질 쾌적 학습 인터페이스 보장!"</p>
                    <button class="copy-btn" onclick="copyText('copy1')">문구 복사</button>
                </div>
                <div class="copy-card">
                    <p id="copy2">"실전 맞춤형 핵심 예제 훈련으로 증명하는 수강생들의 성적 수직 상승 효과!"</p>
                    <button class="copy-btn" onclick="copyText('copy2')">문구 복사</button>
                </div>
            </div>
        </div>
    </div>

    <script>
        new Chart(document.getElementById('sentimentChart').getContext('2d'), {
            type: 'doughnut',
            data: {
                labels: ['긍정', '중립', '부정'],
                datasets: [{ data: [{{ pos_ratio }}, {{ neu_ratio }}, {{ neg_ratio }}], backgroundColor: ['#10b981', '#f59e0b', '#ef4444'], borderWidth: 0 }]
            },
            options: { responsive: true, maintainAspectRatio: false, plugins: { legend: { position: 'bottom' } } }
        });

        new Chart(document.getElementById('categoryChart').getContext('2d'), {
            type: 'bar',
            data: {
                labels: {{ category_labels | tojson }},
                datasets: [{ 
                    label: '평균 평점', 
                    data: {{ category_ratings | tojson }}, 
                    backgroundColor: '#6366f1', 
                    borderRadius: 6,
                    barPercentage: 0.35,
                    categoryPercentage: 0.5
                }]
            },
            options: { responsive: true, maintainAspectRatio: false, scales: { y: { min: 3.0, max: 4.0 } } }
        });

        function copyText(id) {
            navigator.clipboard.writeText(document.getElementById(id).innerText).then(() => alert('클립보드에 복사되었습니다!'));
        }
    </script>
    </body>
    </html>"""

    # 8. 템플릿 렌더링 및 index.html 정적 파일 생성 (오버라이트)
    template = Template(html_template)
    rendered_html = template.render(
        total_reviews=total_reviews, 
        avg_rating=avg_rating,
        pos_ratio=pos_ratio, 
        neu_ratio=neu_ratio, 
        neg_ratio=neg_ratio,
        pos_keywords=pos_keywords, 
        neg_keywords=neg_keywords,
        category_labels=category_labels, 
        category_ratings=category_ratings,
        teacher_list=teacher_list, 
        updated_time=updated_time
    )

    with open('index.html', 'w', encoding='utf-8') as f:
        f.write(rendered_html)
        
    print(f"[SUCCESS] {updated_time} 기준 index.html 정적 대시보드 파일이 성공적으로 생성되었습니다.")

if __name__ == '__main__':
    run_analysis_pipeline()
