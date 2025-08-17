from flask import Flask, request, jsonify
from flask_cors import CORS
import pandas as pd
import numpy as np
from sklearn.metrics.pairwise import cosine_similarity
from scipy.spatial.distance import euclidean
import warnings
warnings.filterwarnings('ignore')

app = Flask(__name__)
CORS(app)  # CORS 설정으로 프론트엔드에서 접근 가능

# 전역 변수 초기화
df_new_score = None
전형_프로파일 = None
score_columns = [
    '성실성', '개방성', '외향성', '우호성', '정서안정성', '기술전문성', 
    '인지문제해결', '대인-영향력', '자기관리', '적응력', '학습속도', 
    '대인민첩성', '성과민첩성', '자기인식', '자기조절', '공감-사회기술'
]

def initialize_model():
    """모델 초기화 함수"""
    global df_new_score, 전형_프로파일
    
    try:
        # 기존 dive.py의 데이터 처리 로직 실행
        df = pd.read_csv('./data/all_data.csv', skiprows=1)
        
        # '일반전형' 컬럼을 ','로 분리하여 새로운 데이터프레임 생성
        df_new = df[['기관명', '일반전형']].copy()
        df_new = df_new[df_new['일반전형'].notna()]
        
        # 전형 데이터 확장
        df_expanded = []
        for idx, row in df_new.iterrows():
            기관명 = row['기관명']
            일반전형_text = str(row['일반전형'])
            
            일반전형_lines = 일반전형_text.split('\n')
            
            for line in 일반전형_lines:
                전형_list = line.split(',')
                for 전형 in 전형_list:
                    전형 = 전형.strip()
                    if 전형:
                        df_expanded.append({
                            '기관명': 기관명,
                            '일반전형': 전형
                        })
        
        df_new = pd.DataFrame(df_expanded)
        df_new = df_new.drop_duplicates(subset=['기관명', '일반전형'])
        
        # 점수 데이터 생성
        df_new_score = df_new.copy()
        
        # 일반전형별 기준 점수 생성
        np.random.seed(42)
        unique_forms = df_new['일반전형'].unique()
        base_scores = {}
        
        for form in unique_forms:
            base_scores[form] = {}
            for column in score_columns:
                if '운영' in form or '사무' in form:
                    if column in ['성실성', '자기관리', '대인-영향력', '공감-사회기술']:
                        base_scores[form][column] = np.random.randint(3, 6)
                    else:
                        base_scores[form][column] = np.random.randint(2, 5)
                elif '기술' in form or '전기' in form or '기계' in form or '토목' in form or '건축' in form or '통신' in form or '신호' in form:
                    if column in ['기술전문성', '인지문제해결', '학습속도', '자기관리']:
                        base_scores[form][column] = np.random.randint(3, 6)
                    else:
                        base_scores[form][column] = np.random.randint(2, 5)
                elif '운전' in form:
                    if column in ['성실성', '정서안정성', '적응력', '자기관리']:
                        base_scores[form][column] = np.random.randint(3, 6)
                    else:
                        base_scores[form][column] = np.random.randint(2, 5)
                elif '공무' in form:
                    if column in ['성실성', '기술전문성', '자기관리']:
                        base_scores[form][column] = np.random.randint(3, 6)
                    else:
                        base_scores[form][column] = np.random.randint(2, 5)
                else:
                    base_scores[form][column] = np.random.randint(2, 5)
        
        # 점수 할당
        for idx, row in df_new_score.iterrows():
            form = row['일반전형']
            for column in score_columns:
                base_score = base_scores[form][column]
                variation = np.random.randint(-1, 2)
                final_score = max(1, min(5, base_score + variation))
                df_new_score.loc[idx, column] = final_score
        
        # 전형별 평균 점수 계산
        전형_프로파일 = df_new_score.groupby('일반전형')[score_columns].mean()
        
        return True
        
    except Exception as e:
        print(f"모델 초기화 오류: {e}")
        return False

def 적합전형_추천(구직자_점수_dict, top_n=5):
    """전형 추천 함수"""
    # 구직자 점수를 배열로 변환
    구직자_점수 = [구직자_점수_dict.get(col, 3) for col in score_columns]
    구직자_점수 = np.array(구직자_점수).reshape(1, -1)
    
    # 코사인 유사도 계산
    유사도_점수 = cosine_similarity(구직자_점수, 전형_프로파일.values)[0]
    
    # 유클리드 거리 계산
    거리_점수 = []
    for idx, 전형_점수 in enumerate(전형_프로파일.values):
        거리 = euclidean(구직자_점수[0], 전형_점수)
        거리_점수.append(1 / (1 + 거리))
    
    # 종합 점수 계산
    종합_점수 = 0.6 * 유사도_점수 + 0.4 * np.array(거리_점수)
    
    # 상위 N개 전형 선택
    추천_인덱스 = np.argsort(종합_점수)[::-1][:top_n]
    
    추천_결과 = []
    for i, idx in enumerate(추천_인덱스):
        전형명 = 전형_프로파일.index[idx]
        적합도 = 종합_점수[idx] * 100
        추천_결과.append({
            '순위': i + 1,
            '전형명': 전형명,
            '적합도': round(적합도, 1),
            '코사인유사도': round(유사도_점수[idx], 3),
            '거리기반유사도': round(거리_점수[idx], 3)
        })
    
    return 추천_결과

# API 엔드포인트들

@app.route('/', methods=['GET'])
def home():
    """API 상태 확인"""
    return jsonify({
        'message': '구직자 적합 전형 추천 API',
        'status': 'running',
        'version': '1.0.0',
        'endpoints': {
            'POST /recommend': '전형 추천',
            'GET /forms': '전체 전형 목록',
            'GET /categories': '능력 카테고리 목록',
            'GET /health': '서비스 상태 확인'
        }
    })

@app.route('/recommend', methods=['POST'])
def recommend():
    """전형 추천 API"""
    try:
        data = request.get_json()
        
        if not data:
            return jsonify({'error': '요청 데이터가 없습니다.'}), 400
        
        # 구직자 점수 유효성 검사
        구직자_점수 = data.get('scores', {})
        
        if not 구직자_점수:
            return jsonify({'error': '점수 데이터가 없습니다.'}), 400
        
        # 필수 항목 확인
        missing_items = [col for col in score_columns if col not in 구직자_점수]
        if missing_items:
            return jsonify({
                'error': '필수 항목이 누락되었습니다.',
                'missing_items': missing_items
            }), 400
        
        # 점수 범위 확인 (1-5)
        invalid_scores = []
        for key, value in 구직자_점수.items():
            if not isinstance(value, (int, float)) or value < 1 or value > 5:
                invalid_scores.append(key)
        
        if invalid_scores:
            return jsonify({
                'error': '점수는 1-5 범위의 숫자여야 합니다.',
                'invalid_items': invalid_scores
            }), 400
        
        # 추천 개수 설정
        top_n = data.get('top_n', 5)
        if not isinstance(top_n, int) or top_n < 1 or top_n > 20:
            top_n = 5
        
        # 전형 추천 실행
        추천_결과 = 적합전형_추천(구직자_점수, top_n)
        
        # 구직자 프로필 분석
        높은_점수_항목 = sorted(구직자_점수.items(), key=lambda x: x[1], reverse=True)[:3]
        낮은_점수_항목 = sorted(구직자_점수.items(), key=lambda x: x[1])[:3]
        
        return jsonify({
            'success': True,
            'recommendations': 추천_결과,
            'profile_analysis': {
                '강점_항목': [{'항목': item[0], '점수': item[1]} for item in 높은_점수_항목],
                '개선_항목': [{'항목': item[0], '점수': item[1]} for item in 낮은_점수_항목],
                '평균_점수': round(sum(구직자_점수.values()) / len(구직자_점수), 1)
            },
            'request_info': {
                'top_n': top_n,
                'total_forms': len(전형_프로파일)
            }
        })
        
    except Exception as e:
        return jsonify({'error': f'추천 처리 중 오류 발생: {str(e)}'}), 500

@app.route('/forms', methods=['GET'])
def get_forms():
    """전체 전형 목록 API"""
    try:
        forms_list = 전형_프로파일.index.tolist()
        
        # 기관별 그룹핑
        기관별_전형 = {}
        for idx, row in df_new_score.iterrows():
            기관명 = row['기관명']
            전형명 = row['일반전형']
            
            if 기관명 not in 기관별_전형:
                기관별_전형[기관명] = []
            
            if 전형명 not in 기관별_전형[기관명]:
                기관별_전형[기관명].append(전형명)
        
        return jsonify({
            'success': True,
            'total_forms': len(forms_list),
            'forms': forms_list,
            'forms_by_organization': 기관별_전형
        })
        
    except Exception as e:
        return jsonify({'error': f'전형 목록 조회 중 오류 발생: {str(e)}'}), 500

@app.route('/categories', methods=['GET'])
def get_categories():
    """능력 카테고리 목록 API"""
    return jsonify({
        'success': True,
        'categories': score_columns,
        'description': {
            '성실성': '책임감과 신뢰성',
            '개방성': '새로운 경험에 대한 개방성',
            '외향성': '사교성과 활동성',
            '우호성': '협조성과 친화성',
            '정서안정성': '스트레스 관리와 감정 조절',
            '기술전문성': '전문 기술 역량',
            '인지문제해결': '논리적 사고와 문제 해결',
            '대인-영향력': '타인에게 영향을 미치는 능력',
            '자기관리': '시간과 업무 관리',
            '적응력': '변화에 대한 적응',
            '학습속도': '새로운 지식 습득 속도',
            '대인민첩성': '대인관계에서의 민첩성',
            '성과민첩성': '성과 달성을 위한 민첩성',
            '자기인식': '자신에 대한 이해',
            '자기조절': '자기 통제 능력',
            '공감-사회기술': '타인 이해와 사회적 기술'
        }
    })

@app.route('/health', methods=['GET'])
def health_check():
    """서비스 상태 확인 API"""
    try:
        model_status = 전형_프로파일 is not None and df_new_score is not None
        return jsonify({
            'status': 'healthy' if model_status else 'unhealthy',
            'model_loaded': model_status,
            'total_forms': len(전형_프로파일) if 전형_프로파일 is not None else 0,
            'total_records': len(df_new_score) if df_new_score is not None else 0
        })
    except Exception as e:
        return jsonify({
            'status': 'error',
            'error': str(e)
        }), 500

# 서버 시작 시 모델 초기화
if __name__ == '__main__':
    print("🚀 구직자 적합 전형 추천 API 서버 시작")
    print("📊 모델 초기화 중...")
    
    if initialize_model():
        print("✅ 모델 초기화 완료")
        print(f"📋 총 {len(전형_프로파일)}개 전형 데이터 로드됨")
        print("🌐 서버 실행 중... (http://localhost:8080)")
        app.run(debug=True, host='0.0.0.0', port=8080)
    else:
        print("❌ 모델 초기화 실패")
