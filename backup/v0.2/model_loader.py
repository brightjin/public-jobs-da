"""
분석 모델 로더 모듈
저장된 채용 전형 추천 모델을 로딩하고 추천 서비스를 제공합니다.
"""

import pandas as pd
import numpy as np
import pickle
import json
import os
from datetime import datetime
from sklearn.metrics.pairwise import cosine_similarity
from scipy.spatial.distance import euclidean
import warnings
warnings.filterwarnings('ignore')

class JobRecommendationModelLoader:
    """채용 전형 추천 모델 로더 클래스"""
    
    def __init__(self, model_dir='./models'):
        self.model_dir = model_dir
        self.form_profiles = None
        self.scores_data = None
        self.model_info = None
        self.forms_data = None
        self.score_columns = None
        self.is_loaded = False
        
    def load_model(self):
        """저장된 모델 로딩"""
        try:
            print("📂 모델 로딩 중...")
            
            # 모델 디렉토리 확인
            if not os.path.exists(self.model_dir):
                print(f"❌ 모델 디렉토리가 존재하지 않습니다: {self.model_dir}")
                return False
            
            # 1. 모델 정보 로딩
            info_path = os.path.join(self.model_dir, 'model_info.json')
            if not os.path.exists(info_path):
                print(f"❌ 모델 정보 파일이 없습니다: {info_path}")
                return False
                
            with open(info_path, 'r', encoding='utf-8') as f:
                self.model_info = json.load(f)
            
            self.score_columns = self.model_info['score_columns']
            
            # 2. 전형 프로파일 로딩
            profile_path = os.path.join(self.model_dir, 'form_profiles.pkl')
            if not os.path.exists(profile_path):
                print(f"❌ 전형 프로파일 파일이 없습니다: {profile_path}")
                return False
                
            with open(profile_path, 'rb') as f:
                self.form_profiles = pickle.load(f)
            
            # 3. 점수 데이터 로딩
            scores_path = os.path.join(self.model_dir, 'scores_data.pkl')
            if not os.path.exists(scores_path):
                print(f"❌ 점수 데이터 파일이 없습니다: {scores_path}")
                return False
                
            with open(scores_path, 'rb') as f:
                self.scores_data = pickle.load(f)
            
            # 4. 전형 목록 로딩
            forms_path = os.path.join(self.model_dir, 'forms_data.json')
            if not os.path.exists(forms_path):
                print(f"❌ 전형 목록 파일이 없습니다: {forms_path}")
                return False
                
            with open(forms_path, 'r', encoding='utf-8') as f:
                self.forms_data = json.load(f)
            
            self.is_loaded = True
            
            print("✅ 모델 로딩 완료!")
            print(f"   📊 모델 버전: {self.model_info['version']}")
            print(f"   📅 생성일시: {self.model_info['created_at']}")
            print(f"   📋 전형 수: {self.model_info['unique_forms']}")
            print(f"   🏢 기관 수: {self.model_info['unique_organizations']}")
            
            return True
            
        except Exception as e:
            print(f"❌ 모델 로딩 실패: {e}")
            return False
    
    def get_model_info(self):
        """모델 정보 반환"""
        if not self.is_loaded:
            return None
        return self.model_info
    
    def get_forms_list(self):
        """전형 목록 반환"""
        if not self.is_loaded:
            return None
        return self.forms_data
    
    def recommend_forms(self, applicant_scores, top_n=5):
        """전형 추천"""
        if not self.is_loaded:
            raise Exception("모델이 로딩되지 않았습니다. load_model()을 먼저 호출하세요.")
        
        try:
            # 구직자 점수를 배열로 변환
            applicant_array = [applicant_scores.get(col, 3) for col in self.score_columns]
            applicant_array = np.array(applicant_array).reshape(1, -1)
            
            # 코사인 유사도 계산
            cosine_similarities = cosine_similarity(applicant_array, self.form_profiles.values)[0]
            
            # 유클리드 거리 계산
            distance_similarities = []
            for idx, form_scores in enumerate(self.form_profiles.values):
                distance = euclidean(applicant_array[0], form_scores)
                distance_similarities.append(1 / (1 + distance))
            
            # 종합 점수 계산 (코사인 유사도 60% + 거리 기반 유사도 40%)
            combined_scores = 0.6 * cosine_similarities + 0.4 * np.array(distance_similarities)
            
            # 상위 N개 전형 선택
            top_indices = np.argsort(combined_scores)[::-1][:top_n]
            
            recommendations = []
            for i, idx in enumerate(top_indices):
                form_name = self.form_profiles.index[idx]
                fitness_score = combined_scores[idx] * 100
                
                recommendations.append({
                    '순위': i + 1,
                    '전형명': form_name,
                    '적합도': round(fitness_score, 1),
                    '코사인유사도': round(cosine_similarities[idx], 3),
                    '거리기반유사도': round(distance_similarities[idx], 3)
                })
            
            return recommendations
            
        except Exception as e:
            raise Exception(f"추천 처리 중 오류 발생: {str(e)}")
    
    def analyze_profile(self, applicant_scores):
        """구직자 프로필 분석"""
        if not self.is_loaded:
            raise Exception("모델이 로딩되지 않았습니다.")
        
        try:
            # 강점과 약점 분석
            sorted_scores = sorted(applicant_scores.items(), key=lambda x: x[1], reverse=True)
            strengths = sorted_scores[:3]
            improvements = sorted_scores[-3:]
            
            # 평균 점수 계산
            avg_score = sum(applicant_scores.values()) / len(applicant_scores)
            
            analysis = {
                '강점_항목': [{'항목': item[0], '점수': item[1]} for item in strengths],
                '개선_항목': [{'항목': item[0], '점수': item[1]} for item in improvements],
                '평균_점수': round(avg_score, 1)
            }
            
            return analysis
            
        except Exception as e:
            raise Exception(f"프로필 분석 중 오류 발생: {str(e)}")
    
    def validate_scores(self, scores):
        """점수 유효성 검사"""
        if not self.is_loaded:
            return False, "모델이 로딩되지 않았습니다."
        
        # 필수 항목 확인
        missing_items = [col for col in self.score_columns if col not in scores]
        if missing_items:
            return False, f"필수 항목이 누락되었습니다: {missing_items}"
        
        # 점수 범위 확인 (1-5)
        invalid_scores = []
        for key, value in scores.items():
            if not isinstance(value, (int, float)) or value < 1 or value > 5:
                invalid_scores.append(key)
        
        if invalid_scores:
            return False, f"점수는 1-5 범위의 숫자여야 합니다: {invalid_scores}"
        
        return True, "유효한 점수입니다."

def test_model_loader():
    """모델 로더 테스트"""
    print("🧪 모델 로더 테스트 시작")
    print("=" * 40)
    
    # 모델 로더 생성 및 로딩
    loader = JobRecommendationModelLoader()
    
    if not loader.load_model():
        print("❌ 모델 로딩 실패")
        return
    
    # 모델 정보 출력
    model_info = loader.get_model_info()
    print(f"\n📊 로딩된 모델 정보:")
    print(f"   버전: {model_info['version']}")
    print(f"   전형 수: {model_info['unique_forms']}")
    
    # 테스트용 구직자 데이터
    test_scores = {
        "성실성": 4, "개방성": 3, "외향성": 2, "우호성": 3, "정서안정성": 4,
        "기술전문성": 5, "인지문제해결": 5, "대인-영향력": 2, "자기관리": 4, 
        "적응력": 4, "학습속도": 5, "대인민첩성": 2, "성과민첩성": 3, 
        "자기인식": 3, "자기조절": 4, "공감-사회기술": 3
    }
    
    # 점수 유효성 검사
    is_valid, message = loader.validate_scores(test_scores)
    print(f"\n✅ 점수 유효성: {message}")
    
    if is_valid:
        # 추천 테스트
        recommendations = loader.recommend_forms(test_scores, top_n=3)
        print(f"\n🎯 추천 결과:")
        for rec in recommendations:
            print(f"   {rec['순위']}. {rec['전형명']} - 적합도: {rec['적합도']}%")
        
        # 프로필 분석 테스트
        analysis = loader.analyze_profile(test_scores)
        print(f"\n📈 프로필 분석:")
        print(f"   평균 점수: {analysis['평균_점수']}")
        print(f"   강점: {', '.join([item['항목'] for item in analysis['강점_항목']])}")

if __name__ == "__main__":
    test_model_loader()
