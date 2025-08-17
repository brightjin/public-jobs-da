"""
분석 모델 생성 및 저장 모듈 (API 연동 버전)
채용 데이터를 REST API에서 조회하거나 CSV 파일에서 로딩하여 전형 추천 모델을 생성하고 파일로 저장합니다.
"""

import pandas as pd
import numpy as np
import pickle
import json
import requests
from datetime import datetime
import os
import warnings
warnings.filterwarnings('ignore')

class JobRecommendationModelBuilder:
    """채용 전형 추천 모델 생성 클래스"""
    
    def __init__(self, data_source='api', api_url='http://mysite.com/recruits', csv_path='./data/all_data.csv'):
        """
        모델 빌더 초기화
        
        Args:
            data_source (str): 데이터 소스 타입 ('api' 또는 'csv')
            api_url (str): 채용 데이터 API 엔드포인트 URL
            csv_path (str): CSV 파일 경로 (data_source가 'csv'일 때 사용)
        """
        self.data_source = data_source
        self.api_url = api_url
        self.csv_path = csv_path
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
        
    def load_data_from_api(self):
        """REST API에서 채용 데이터 로딩"""
        try:
            print(f"🌐 API에서 채용 데이터 로딩 중: {self.api_url}")
            
            response = requests.get(self.api_url, timeout=30)
            response.raise_for_status()
            
            data = response.json()
            
            # JSON 데이터를 DataFrame으로 변환
            if isinstance(data, list):
                self.df_raw = pd.DataFrame(data)
            elif isinstance(data, dict) and 'data' in data:
                self.df_raw = pd.DataFrame(data['data'])
            elif isinstance(data, dict) and 'recruits' in data:
                self.df_raw = pd.DataFrame(data['recruits'])
            else:
                self.df_raw = pd.DataFrame([data])
            
            print(f"✅ API 데이터 로딩 완료: {self.df_raw.shape[0]}개 행, {self.df_raw.shape[1]}개 열")
            print(f"📊 컬럼: {list(self.df_raw.columns)}")
            return True
            
        except requests.exceptions.RequestException as e:
            print(f"❌ API 요청 실패: {e}")
            print("📋 CSV 파일로 대체하여 로딩을 시도합니다...")
            return self.load_data_from_csv()
        except Exception as e:
            print(f"❌ API 데이터 처리 실패: {e}")
            print("📋 CSV 파일로 대체하여 로딩을 시도합니다...")
            return self.load_data_from_csv()
    
    def load_data_from_csv(self):
        """CSV 파일에서 채용 데이터 로딩 (백업 방법)"""
        try:
            print(f"📂 CSV 파일에서 데이터 로딩 중: {self.csv_path}")
            self.df_raw = pd.read_csv(self.csv_path, skiprows=1)
            print(f"✅ CSV 데이터 로딩 완료: {self.df_raw.shape[0]}개 행, {self.df_raw.shape[1]}개 열")
            return True
        except Exception as e:
            print(f"❌ CSV 데이터 로딩 실패: {e}")
            return False
    
    def load_data(self):
        """데이터 소스에 따라 데이터 로딩"""
        if self.data_source == 'api':
            return self.load_data_from_api()
        else:
            return self.load_data_from_csv()
    
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
            data_source_info = {
                'source_type': self.data_source,
                'api_url': self.api_url if self.data_source == 'api' else None,
                'csv_path': self.csv_path if self.data_source == 'csv' else None
            }
            
            self.model_info = {
                'version': f'v{timestamp}',
                'created_at': datetime.now().isoformat(),
                'data_source': data_source_info,
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
    import argparse
    
    parser = argparse.ArgumentParser(description='채용 전형 추천 모델 빌더')
    parser.add_argument('--source', choices=['api', 'csv'], default='api', 
                        help='데이터 소스 (api: REST API, csv: CSV 파일)')
    parser.add_argument('--api-url', default='http://mysite.com/recruits',
                        help='채용 데이터 API URL')
    parser.add_argument('--csv-path', default='./data/all_data.csv',
                        help='CSV 파일 경로')
    parser.add_argument('--output-dir', default='./models',
                        help='모델 저장 디렉토리')
    
    args = parser.parse_args()
    
    print("🚀 채용 전형 추천 모델 빌더 시작")
    print("=" * 50)
    print(f"📡 데이터 소스: {args.source.upper()}")
    
    if args.source == 'api':
        print(f"🌐 API URL: {args.api_url}")
        print("📋 백업: CSV 파일 사용 (API 실패 시)")
    else:
        print(f"📂 CSV 파일: {args.csv_path}")
    
    print(f"💾 출력 디렉토리: {args.output_dir}")
    print("=" * 50)
    
    # 모델 빌더 생성
    builder = JobRecommendationModelBuilder(
        data_source=args.source,
        api_url=args.api_url,
        csv_path=args.csv_path
    )
    
    # 모델 빌드 및 저장
    if builder.build_and_save_model(args.output_dir):
        print("\n✅ 모델이 성공적으로 생성되고 저장되었습니다!")
        print("💡 이제 API 서버에서 이 모델을 로딩하여 사용할 수 있습니다.")
        
        if args.source == 'api':
            print("\n🔄 모델 업데이트 방법:")
            print("   1. 새로운 채용 데이터가 API에 추가되면")
            print("   2. python3 model_builder.py --source api")
            print("   3. curl -X POST http://localhost:8080/reload_model")
    else:
        print("\n❌ 모델 생성에 실패했습니다.")
        if args.source == 'api':
            print("💡 API 연결 문제일 수 있습니다. CSV 모드로 시도해보세요:")
            print("   python3 model_builder.py --source csv")

if __name__ == "__main__":
    main()
