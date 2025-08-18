#!/usr/bin/env python3
"""
채용공고 추천 API 서버
데이터베이스 기반 유사도 추천 시스템을 REST API로 제공
"""

import os
import pickle
import numpy as np
from flask import Flask, request, jsonify
from flask_cors import CORS
from sklearn.metrics.pairwise import cosine_similarity
from database_manager import DatabaseManager
from log_config import get_logger

# 로깅 설정
logger = get_logger(__name__, 'job_recommendation_api.log')

app = Flask(__name__)
CORS(app)

# 글로벌 변수로 모델 저장
similarity_model = None
score_columns = [
    '성실성', '개방성', '외향성', '우호성', '정서안정성', '기술전문성',
    '인지문제해결', '대인영향력', '자기관리', '적응력', '학습속도',
    '대인민첩성', '성과민첩성', '자기인식', '자기조절', '공감사회기술'
]

def load_similarity_model():
    """유사도 모델 로드"""
    global similarity_model
    try:
        model_path = './models/similarity_model.pkl'
        
        if not os.path.exists(model_path):
            logger.error(f"❌ 모델 파일이 존재하지 않습니다: {model_path}")
            return False
        
        with open(model_path, 'rb') as f:
            similarity_model = pickle.load(f)
        
        logger.info("✅ 유사도 모델 로딩 완료")
        logger.info(f"📊 총 공고 수: {len(similarity_model['job_posting_scores'])}")
        return True
        
    except Exception as e:
        logger.error(f"❌ 모델 로딩 실패: {e}")
        return False

@app.route('/health', methods=['GET'])
def health_check():
    """헬스 체크"""
    return jsonify({
        'status': 'healthy',
        'service': 'job_recommendation_api',
        'model_loaded': similarity_model is not None
    })

@app.route('/recommend', methods=['POST'])
def recommend_jobs():
    """
    구직자 점수를 받아 유사한 채용공고 추천
    
    Request Body:
    {
        "user_scores": {
            "성실성": 4,
            "개방성": 3,
            ...
        },
        "top_k": 5  // 선택사항, 기본값 5
    }
    """
    try:
        if similarity_model is None:
            return jsonify({
                'success': False,
                'error': '모델이 로딩되지 않았습니다. 서버를 다시 시작해주세요.'
            }), 500
        
        data = request.get_json()
        
        if not data or 'user_scores' not in data:
            return jsonify({
                'success': False,
                'error': 'user_scores가 필요합니다.'
            }), 400
        
        user_scores = data['user_scores']
        top_k = data.get('top_k', 5)
        
        # 점수 유효성 검사
        missing_scores = [col for col in score_columns if col not in user_scores]
        if missing_scores:
            return jsonify({
                'success': False,
                'error': f'다음 점수가 누락되었습니다: {missing_scores}'
            }), 400
        
        # 점수 범위 검사 (1~5)
        invalid_scores = [col for col in score_columns 
                         if not (1 <= user_scores[col] <= 5)]
        if invalid_scores:
            return jsonify({
                'success': False,
                'error': f'점수는 1~5 범위여야 합니다. 잘못된 점수: {invalid_scores}'
            }), 400
        
        # 추천 수행
        recommendations = get_recommendations(user_scores, top_k)
        
        return jsonify({
            'success': True,
            'user_scores': user_scores,
            'recommendations': recommendations,
            'total_count': len(recommendations)
        })
        
    except Exception as e:
        logger.error(f"❌ 추천 실패: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

def get_recommendations(user_scores, top_k=5):
    """실제 추천 로직"""
    try:
        scaler = similarity_model['scaler']
        normalized_scores = similarity_model['normalized_scores']
        job_posting_scores = similarity_model['job_posting_scores']
        
        # 사용자 점수를 배열로 변환 및 정규화
        user_score_array = np.array([user_scores.get(col, 3) for col in score_columns])
        user_score_normalized = scaler.transform([user_score_array])
        
        # 코사인 유사도 계산
        similarities = cosine_similarity(user_score_normalized, normalized_scores)[0]
        
        # 상위 k개 추천
        top_indices = similarities.argsort()[-top_k:][::-1]
        
        recommendations = []
        for rank, idx in enumerate(top_indices, 1):
            posting = job_posting_scores.iloc[idx]
            similarity = float(similarities[idx])
            
            # 해당 공고의 실제 점수도 포함
            posting_scores = {}
            for col in score_columns:
                posting_scores[col] = int(posting[col])
            
            recommendation = {
                'rank': rank,
                'id': int(posting['id']),  # int64를 int로 변환
                '기관명': posting['기관명'],
                '일반전형': posting['일반전형'],
                '유사도': round(similarity, 3),
                '공고점수': posting_scores
            }
            recommendations.append(recommendation)
        
        return recommendations
        
    except Exception as e:
        logger.error(f"❌ 추천 로직 실패: {e}")
        raise

@app.route('/statistics', methods=['GET'])
def get_statistics():
    """시스템 통계 정보"""
    try:
        if similarity_model is None:
            return jsonify({
                'success': False,
                'error': '모델이 로딩되지 않았습니다.'
            }), 500
        
        job_posting_scores = similarity_model['job_posting_scores']
        
        # 기본 통계
        stats = {
            'total_postings': len(job_posting_scores),
            'unique_agencies': job_posting_scores['기관명'].nunique(),
            'unique_forms': job_posting_scores['일반전형'].nunique()
        }
        
        # 전형별 분포
        form_distribution = job_posting_scores['일반전형'].value_counts().to_dict()
        
        # 기관별 분포
        agency_distribution = job_posting_scores['기관명'].value_counts().to_dict()
        
        return jsonify({
            'success': True,
            'statistics': stats,
            'form_distribution': form_distribution,
            'agency_distribution': agency_distribution
        })
        
    except Exception as e:
        logger.error(f"❌ 통계 조회 실패: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/sample_scores', methods=['GET'])
def get_sample_scores():
    """샘플 점수 제공 (테스트용)"""
    samples = [
        {
            "name": "기술직 지향",
            "scores": {
                '성실성': 4, '개방성': 5, '외향성': 3, '우호성': 3, '정서안정성': 4,
                '기술전문성': 5, '인지문제해결': 5, '대인영향력': 3, '자기관리': 4,
                '적응력': 4, '학습속도': 5, '대인민첩성': 3, '성과민첩성': 4,
                '자기인식': 4, '자기조절': 4, '공감사회기술': 3
            }
        },
        {
            "name": "사무직 지향",
            "scores": {
                '성실성': 5, '개방성': 3, '외향성': 4, '우호성': 4, '정서안정성': 4,
                '기술전문성': 3, '인지문제해결': 4, '대인영향력': 4, '자기관리': 5,
                '적응력': 4, '학습속도': 3, '대인민첩성': 4, '성과민첩성': 4,
                '자기인식': 4, '자기조절': 5, '공감사회기술': 4
            }
        },
        {
            "name": "영업/서비스직 지향",
            "scores": {
                '성실성': 4, '개방성': 4, '외향성': 5, '우호성': 5, '정서안정성': 4,
                '기술전문성': 3, '인지문제해결': 3, '대인영향력': 5, '자기관리': 4,
                '적응력': 5, '학습속도': 4, '대인민첩성': 5, '성과민첩성': 4,
                '자기인식': 4, '자기조절': 4, '공감사회기술': 5
            }
        }
    ]
    
    return jsonify({
        'success': True,
        'samples': samples,
        'score_columns': score_columns
    })

@app.route('/reload_model', methods=['POST'])
def reload_model():
    """모델 다시 로딩"""
    try:
        if load_similarity_model():
            return jsonify({
                'success': True,
                'message': '모델이 성공적으로 다시 로딩되었습니다.'
            })
        else:
            return jsonify({
                'success': False,
                'error': '모델 로딩에 실패했습니다.'
            }), 500
            
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

if __name__ == '__main__':
    print("🚀 채용공고 추천 API 서버 시작")
    print("=" * 50)
    
    # 모델 로딩
    if load_similarity_model():
        print("✅ 모델 로딩 완료")
        
        # 서버 시작
        host = os.getenv('API_HOST', '0.0.0.0')
        port = int(os.getenv('API_PORT', 8080))
        
        print(f"🌐 서버 주소: http://{host}:{port}")
        print("📋 API 엔드포인트:")
        print("   - GET  /health         : 헬스 체크")
        print("   - POST /recommend      : 채용공고 추천")
        print("   - GET  /statistics     : 시스템 통계")
        print("   - GET  /sample_scores  : 샘플 점수")
        print("   - POST /reload_model   : 모델 다시 로딩")
        print("=" * 50)
        
        app.run(host=host, port=port, debug=False)
    else:
        print("❌ 모델 로딩에 실패했습니다. 서버를 시작할 수 없습니다.")
        print("💡 먼저 다음 명령으로 모델을 생성하세요:")
        print("   python3 model_builder.py --source database")
