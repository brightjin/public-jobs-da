#!/usr/bin/env python3
"""
데이터베이스 기반 채용공고 추천 시스템 테스트
"""

import sys
import os
sys.path.append('.')

# 생성된 추천 함수를 임포트하기 위해 path 추가
sys.path.append('./models')
from log_config import get_logger

# 로깅 설정
logger = get_logger(__name__, 'test_recommendation_system.log')

def test_recommendation_system():
    """추천 시스템 테스트"""
    print("🚀 데이터베이스 기반 추천 시스템 테스트")
    print("=" * 50)
    
    # 샘플 사용자 점수 (구직자 프로필)
    test_cases = [
        {
            "name": "기술직 지향 구직자",
            "scores": {
                '성실성': 4, '개방성': 5, '외향성': 3, '우호성': 3, '정서안정성': 4,
                '기술전문성': 5, '인지문제해결': 5, '대인-영향력': 3, '자기관리': 4,
                '적응력': 4, '학습속도': 5, '대인민첩성': 3, '성과민첩성': 4,
                '자기인식': 4, '자기조절': 4, '공감-사회기술': 3
            }
        },
        {
            "name": "사무직 지향 구직자",
            "scores": {
                '성실성': 5, '개방성': 3, '외향성': 4, '우호성': 4, '정서안정성': 4,
                '기술전문성': 3, '인지문제해결': 4, '대인-영향력': 4, '자기관리': 5,
                '적응력': 4, '학습속도': 3, '대인민첩성': 4, '성과민첩성': 4,
                '자기인식': 4, '자기조절': 5, '공감-사회기술': 4
            }
        },
        {
            "name": "영업/서비스직 지향 구직자",
            "scores": {
                '성실성': 4, '개방성': 4, '외향성': 5, '우호성': 5, '정서안정성': 4,
                '기술전문성': 3, '인지문제해결': 3, '대인-영향력': 5, '자기관리': 4,
                '적응력': 5, '학습속도': 4, '대인민첩성': 5, '성과민첩성': 4,
                '자기인식': 4, '자기조절': 4, '공감-사회기술': 5
            }
        }
    ]
    
    try:
        # 추천 함수 로드
        import pickle
        import numpy as np
        from sklearn.metrics.pairwise import cosine_similarity
        
        # 모델 로딩
        with open('./models/similarity_model.pkl', 'rb') as f:
            model = pickle.load(f)
        
        scaler = model['scaler']
        normalized_scores = model['normalized_scores']
        job_posting_scores = model['job_posting_scores']
        
        score_columns = [
            '성실성', '개방성', '외향성', '우호성', '정서안정성', '기술전문성',
            '인지문제해결', '대인-영향력', '자기관리', '적응력', '학습속도',
            '대인민첩성', '성과민첩성', '자기인식', '자기조절', '공감-사회기술'
        ]
        
        # 각 테스트 케이스에 대해 추천 실행
        for i, test_case in enumerate(test_cases, 1):
            print(f"\n🎯 테스트 케이스 {i}: {test_case['name']}")
            print("-" * 40)
            
            user_scores = test_case['scores']
            
            # 사용자 점수 정규화
            user_score_array = np.array([user_scores.get(col, 3) for col in score_columns])
            user_score_normalized = scaler.transform([user_score_array])
            
            # 유사도 계산
            similarities = cosine_similarity(user_score_normalized, normalized_scores)[0]
            
            # 상위 5개 추천
            top_k = 5
            top_indices = similarities.argsort()[-top_k:][::-1]
            
            print("📊 추천 결과:")
            for rank, idx in enumerate(top_indices, 1):
                posting = job_posting_scores.iloc[idx]
                similarity = similarities[idx]
                
                print(f"  {rank}. 공고번호: {posting['공고일련번호']}")
                print(f"     기관코드: {posting['기관코드']}")
                print(f"     일반전형: {posting['일반전형']}")
                print(f"     유사도: {similarity:.3f}")
                print()
        
        print("✅ 추천 시스템 테스트 완료!")
        
        # 추가 통계 정보
        print(f"\n📈 시스템 통계:")
        print(f"   - 총 채용공고 수: {len(job_posting_scores)}")
        print(f"   - 고유 기관 수: {job_posting_scores['기관코드'].nunique()}")
        print(f"   - 고유 전형 수: {job_posting_scores['일반전형'].nunique()}")
        
        # 전형별 공고 분포
        print(f"\n📋 전형별 공고 분포:")
        form_counts = job_posting_scores['일반전형'].value_counts()
        for form, count in form_counts.head(10).items():
            print(f"   - {form}: {count}개")
        
        return True
        
    except Exception as e:
        print(f"❌ 추천 시스템 테스트 실패: {e}")
        return False

def show_database_data():
    """데이터베이스 데이터 샘플 확인"""
    try:
        print("\n🗄️ 데이터베이스 데이터 샘플 확인")
        print("-" * 40)
        
        from database_manager import DatabaseManager
        
        with DatabaseManager() as db:
            # 샘플 데이터 조회
            query = """
            SELECT 공고일련번호, 기관코드, 일반전형, 성실성, 기술전문성, `대인-영향력`
            FROM 채용공고평가점수 
            ORDER BY 공고일련번호 
            LIMIT 10
            """
            result = db.execute_query(query)
            
            print("📊 채용공고평가점수 테이블 샘플:")
            print("공고번호 | 기관코드 | 일반전형 | 성실성 | 기술전문성 | 대인-영향력")
            print("-" * 60)
            
            for row in result:
                print(f"{row[0]:<8} | {row[1]:<6} | {row[2]:<8} | {row[3]:<4} | {row[4]:<8} | {row[5]:<8}")
        
        return True
        
    except Exception as e:
        print(f"❌ 데이터베이스 확인 실패: {e}")
        return False

if __name__ == "__main__":
    print("🔧 추천 시스템 테스트 시작...")
    
    # 데이터베이스 데이터 확인
    show_database_data()
    
    # 추천 시스템 테스트
    test_recommendation_system()
