"""
분석 모델 생성 및 저장 모듈
채용 데이터를 기반으로 전형 추천 모델을 생성하고 파일로 저장합니다.
"""

import pandas as pd
import numpy as np
import pickle
import json
from datetime import datetime
import os
import warnings
warnings.filterwarnings('ignore')

class JobRecommendationModelBuilder:
    """채용 전형 추천 모델 생성 클래스"""
    
    def __init__(self, data_path='./data/all_data.csv'):
        self.data_path = data_path
        self.score_columns = [
            '성실성', '개방성', '외향성', '우호성', '정서안정성', '기술전문성', 
            '인지문제해결', '대인-영향력', '자기관리', '적응력', '학습속도', 
            '대인민첩성', '성과민첩성', '자기인식', '자기조절', '공감-사회기술'
        ]
        self.df_raw = None
        self.df_processed = None
        self.df_scores = None
        self.form_profiles = None
        self.model_info = {}
        
    def load_data(self):
        """원본 데이터 로딩"""
        try:
            print("📊 원본 데이터 로딩 중...")
            self.df_raw = pd.read_csv(self.data_path, skiprows=1)
            print(f"✅ 원본 데이터 로딩 완료: {self.df_raw.shape[0]}개 행, {self.df_raw.shape[1]}개 열")
            return True
        except Exception as e:
            print(f"❌ 데이터 로딩 실패: {e}")
            return False
    
    def preprocess_data(self):
        """데이터 전처리 - 일반전형 분리 및 확장"""
        try:
            print("🔄 데이터 전처리 중...")
            
            # '일반전형' 컬럼을 ','로 분리하여 새로운 데이터프레임 생성
            df_new = self.df_raw[['기관명', '일반전형']].copy()
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
            
            self.df_processed = pd.DataFrame(df_expanded)
            self.df_processed = self.df_processed.drop_duplicates(subset=['기관명', '일반전형'])
            
            print(f"✅ 데이터 전처리 완료: {len(self.df_processed)}개 기관-전형 조합")
            print(f"📋 고유 기관 수: {self.df_processed['기관명'].nunique()}")
            print(f"📋 고유 전형 수: {self.df_processed['일반전형'].nunique()}")
            
            return True
            
        except Exception as e:
            print(f"❌ 데이터 전처리 실패: {e}")
            return False
    
    def generate_scores(self):
        """전형별 특성화된 점수 생성"""
        try:
            print("🎯 전형별 점수 생성 중...")
            
            self.df_scores = self.df_processed.copy()
            
            # 일반전형별 기준 점수 생성
            np.random.seed(42)  # 재현 가능한 결과
            unique_forms = self.df_processed['일반전형'].unique()
            base_scores = {}
            
            for form in unique_forms:
                base_scores[form] = {}
                for column in self.score_columns:
                    # 전형 종류에 따라 특성을 다르게 설정
                    if '운영' in form or '사무' in form:
                        # 운영직/사무직: 자기관리, 성실성, 대인관계 능력 높음
                        if column in ['성실성', '자기관리', '대인-영향력', '공감-사회기술']:
                            base_scores[form][column] = np.random.randint(3, 6)
                        else:
                            base_scores[form][column] = np.random.randint(2, 5)
                    elif any(keyword in form for keyword in ['기술', '전기', '기계', '토목', '건축', '통신', '신호']):
                        # 기술직: 기술전문성, 인지문제해결, 학습속도 높음
                        if column in ['기술전문성', '인지문제해결', '학습속도', '자기관리']:
                            base_scores[form][column] = np.random.randint(3, 6)
                        else:
                            base_scores[form][column] = np.random.randint(2, 5)
                    elif '운전' in form:
                        # 운전직: 성실성, 정서안정성, 적응력 높음
                        if column in ['성실성', '정서안정성', '적응력', '자기관리']:
                            base_scores[form][column] = np.random.randint(3, 6)
                        else:
                            base_scores[form][column] = np.random.randint(2, 5)
                    elif '공무' in form:
                        # 공무직: 성실성, 기술전문성 높음
                        if column in ['성실성', '기술전문성', '자기관리']:
                            base_scores[form][column] = np.random.randint(3, 6)
                        else:
                            base_scores[form][column] = np.random.randint(2, 5)
                    else:
                        # 기타: 균등한 분포
                        base_scores[form][column] = np.random.randint(2, 5)
            
            # 각 행에 대해 기준 점수에서 약간의 변동을 가진 점수 할당
            for idx, row in self.df_scores.iterrows():
                form = row['일반전형']
                for column in self.score_columns:
                    base_score = base_scores[form][column]
                    # 기준 점수에서 ±1 범위의 변동 (1~5 범위 유지)
                    variation = np.random.randint(-1, 2)
                    final_score = max(1, min(5, base_score + variation))
                    self.df_scores.loc[idx, column] = final_score
            
            print(f"✅ 점수 생성 완료: {len(self.df_scores)}개 전형 프로파일")
            return True
            
        except Exception as e:
            print(f"❌ 점수 생성 실패: {e}")
            return False
    
    def create_form_profiles(self):
        """전형별 평균 프로파일 생성"""
        try:
            print("📊 전형별 프로파일 생성 중...")
            
            # 전형별 평균 점수 계산
            self.form_profiles = self.df_scores.groupby('일반전형')[self.score_columns].mean()
            
            print(f"✅ 전형 프로파일 생성 완료: {len(self.form_profiles)}개 전형")
            return True
            
        except Exception as e:
            print(f"❌ 전형 프로파일 생성 실패: {e}")
            return False
    
    def save_model(self, model_dir='./models'):
        """모델 저장"""
        try:
            print("💾 모델 저장 중...")
            
            # 모델 디렉토리 생성
            os.makedirs(model_dir, exist_ok=True)
            
            # 현재 시간으로 버전 정보 생성
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            
            # 모델 정보 설정
            self.model_info = {
                'version': f'v{timestamp}',
                'created_at': datetime.now().isoformat(),
                'data_path': self.data_path,
                'total_records': len(self.df_raw),
                'processed_records': len(self.df_processed),
                'unique_forms': len(self.form_profiles),
                'unique_organizations': self.df_processed['기관명'].nunique(),
                'score_columns': self.score_columns
            }
            
            # 1. 전형 프로파일 저장 (pickle)
            profile_path = os.path.join(model_dir, 'form_profiles.pkl')
            with open(profile_path, 'wb') as f:
                pickle.dump(self.form_profiles, f)
            
            # 2. 점수 데이터 저장 (pickle)
            scores_path = os.path.join(model_dir, 'scores_data.pkl')
            with open(scores_path, 'wb') as f:
                pickle.dump(self.df_scores, f)
            
            # 3. 모델 정보 저장 (JSON)
            info_path = os.path.join(model_dir, 'model_info.json')
            with open(info_path, 'w', encoding='utf-8') as f:
                json.dump(self.model_info, f, ensure_ascii=False, indent=2)
            
            # 4. 전형 목록 저장 (JSON)
            forms_data = {
                'forms_list': self.form_profiles.index.tolist(),
                'forms_by_organization': {}
            }
            
            for idx, row in self.df_scores.iterrows():
                org = row['기관명']
                form = row['일반전형']
                if org not in forms_data['forms_by_organization']:
                    forms_data['forms_by_organization'][org] = []
                if form not in forms_data['forms_by_organization'][org]:
                    forms_data['forms_by_organization'][org].append(form)
            
            forms_path = os.path.join(model_dir, 'forms_data.json')
            with open(forms_path, 'w', encoding='utf-8') as f:
                json.dump(forms_data, f, ensure_ascii=False, indent=2)
            
            print(f"✅ 모델 저장 완료:")
            print(f"   📁 디렉토리: {model_dir}")
            print(f"   📊 전형 프로파일: {profile_path}")
            print(f"   📈 점수 데이터: {scores_path}")
            print(f"   ℹ️ 모델 정보: {info_path}")
            print(f"   📋 전형 목록: {forms_path}")
            print(f"   🏷️ 버전: {self.model_info['version']}")
            
            return True
            
        except Exception as e:
            print(f"❌ 모델 저장 실패: {e}")
            return False
    
    def build_and_save_model(self, model_dir='./models'):
        """전체 모델 빌드 및 저장 프로세스"""
        print("🚀 채용 전형 추천 모델 빌드 시작")
        print("=" * 50)
        
        steps = [
            ("데이터 로딩", self.load_data),
            ("데이터 전처리", self.preprocess_data),
            ("점수 생성", self.generate_scores),
            ("프로파일 생성", self.create_form_profiles),
            ("모델 저장", lambda: self.save_model(model_dir))
        ]
        
        for step_name, step_func in steps:
            if not step_func():
                print(f"❌ {step_name} 단계에서 실패했습니다.")
                return False
        
        print("\n" + "=" * 50)
        print("🎉 모델 빌드 및 저장 완료!")
        print(f"📊 모델 정보:")
        print(f"   - 버전: {self.model_info['version']}")
        print(f"   - 전형 수: {self.model_info['unique_forms']}")
        print(f"   - 기관 수: {self.model_info['unique_organizations']}")
        print(f"   - 데이터 레코드: {self.model_info['processed_records']}")
        
        return True

def main():
    """메인 실행 함수"""
    # 모델 빌더 생성
    builder = JobRecommendationModelBuilder()
    
    # 모델 빌드 및 저장
    if builder.build_and_save_model():
        print("\n✅ 모델이 성공적으로 생성되고 저장되었습니다!")
        print("💡 이제 API 서버에서 이 모델을 로딩하여 사용할 수 있습니다.")
    else:
        print("\n❌ 모델 생성에 실패했습니다.")

if __name__ == "__main__":
    main()
