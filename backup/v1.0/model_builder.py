"""
분석 모델 생성 및 저장 모듈 (데이터베이스 연동 버전)
채용공고평가점수 테이블에서 데이터를 조회하여 유사도 기반 추천 모델을 생성하고 파일로 저장합니다.
"""

import pandas as pd
import numpy as np
import pickle
import json
import requests
from datetime import datetime
import os
import warnings
from sklearn.metrics.pairwise import cosine_similarity
from sklearn.preprocessing import StandardScaler
from database_manager import DatabaseManager
from log_config import get_logger
warnings.filterwarnings('ignore')

# 로깅 설정
logger = get_logger(__name__, 'model_builder.log')

class JobRecommendationModelBuilder:
    """채용 공고 유사도 기반 추천 모델 생성 클래스"""
    
    def __init__(self, data_source='database', api_url='http://mysite.com/recruits', scores_api_url='http://mysite.com/scores', csv_path='./data/all_data.csv'):
        """
        모델 빌더 초기화
        
        Args:
            data_source (str): 데이터 소스 타입 ('database', 'api' 또는 'csv')
            api_url (str): 채용 데이터 API 엔드포인트 URL (하위 호환성)
            scores_api_url (str): 점수 데이터 API 엔드포인트 URL (하위 호환성)
            csv_path (str): CSV 파일 경로 (data_source가 'csv'일 때 사용)
        """
        self.data_source = data_source
        self.api_url = api_url
        self.scores_api_url = scores_api_url
        self.csv_path = csv_path
        self.score_columns = [
            '성실성', '개방성', '외향성', '우호성', '정서안정성', '기술전문성', 
            '인지문제해결', '대인-영향력', '자기관리', '적응력', '학습속도', 
            '대인민첩성', '성과민첩성', '자기인식', '자기조절', '공감-사회기술'
        ]
        self.job_posting_scores = None  # 채용공고평가점수 데이터
        self.scaler = StandardScaler()  # 점수 정규화를 위한 스케일러
        self.model_info = {}
        
    def load_data_from_database(self):
        """데이터베이스에서 채용공고평가점수 테이블 로딩"""
        try:
            print("🗄️ 데이터베이스에서 채용공고평가점수 데이터 로딩 중...")
            
            with DatabaseManager() as db:
                # 채용공고평가점수 테이블 조회
                query = """
                SELECT 공고일련번호, 기관코드, 일반전형,
                       성실성, 개방성, 외향성, 우호성, 정서안정성, 기술전문성,
                       인지문제해결, `대인-영향력`, 자기관리, 적응력, 학습속도,
                       대인민첩성, 성과민첩성, 자기인식, 자기조절, `공감-사회기술`
                FROM 채용공고평가점수
                WHERE 성실성 IS NOT NULL 
                AND 개방성 IS NOT NULL 
                AND 외향성 IS NOT NULL
                ORDER BY 공고일련번호
                """
                
                result = db.execute_query(query)
                if not result:
                    print("❌ 채용공고평가점수 테이블에서 데이터를 찾을 수 없습니다.")
                    return False
                
                # DataFrame으로 변환
                columns = [
                    '공고일련번호', '기관코드', '일반전형',
                    '성실성', '개방성', '외향성', '우호성', '정서안정성', '기술전문성',
                    '인지문제해결', '대인-영향력', '자기관리', '적응력', '학습속도',
                    '대인민첩성', '성과민첩성', '자기인식', '자기조절', '공감-사회기술'
                ]
                
                self.job_posting_scores = pd.DataFrame(result, columns=columns)
                
                print(f"✅ 데이터베이스 데이터 로딩 완료: {len(self.job_posting_scores)}개 채용공고")
                print(f"📊 컬럼: {list(self.job_posting_scores.columns)}")
                print(f"📋 고유 기관 수: {self.job_posting_scores['기관코드'].nunique()}")
                print(f"📋 고유 전형 수: {self.job_posting_scores['일반전형'].nunique()}")
                
                return True
                
        except Exception as e:
            print(f"❌ 데이터베이스 데이터 로딩 실패: {e}")
            return False
        
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
        if self.data_source == 'database':
            return self.load_data_from_database()
        elif self.data_source == 'api':
            return self.load_data_from_api()
        else:
            return self.load_data_from_csv()
    
    def prepare_similarity_model(self):
        """유사도 기반 추천을 위한 모델 준비"""
        try:
            print("🔄 유사도 모델 준비 중...")
            
            if self.job_posting_scores is None:
                print("❌ 채용공고평가점수 데이터가 없습니다.")
                return False
            
            # 점수 데이터만 추출하여 정규화
            score_data = self.job_posting_scores[self.score_columns].copy()
            
            # 결측값 처리 (평균값으로 대체)
            score_data = score_data.fillna(score_data.mean())
            
            # 데이터 정규화 (표준화)
            self.normalized_scores = self.scaler.fit_transform(score_data)
            
            print(f"✅ 유사도 모델 준비 완료: {len(self.normalized_scores)}개 공고 데이터")
            return True
            
        except Exception as e:
            print(f"❌ 유사도 모델 준비 실패: {e}")
            return False
    
    def find_similar_job_postings(self, user_scores, top_k=5):
        """
        사용자 점수와 유사한 채용공고 찾기
        
        Args:
            user_scores (dict): 사용자의 16가지 점수 {'성실성': 4, '개방성': 3, ...}
            top_k (int): 추천할 공고 수
            
        Returns:
            list: 추천 공고일련번호 리스트
        """
        try:
            if self.job_posting_scores is None or self.normalized_scores is None:
                print("❌ 모델이 준비되지 않았습니다.")
                return []
            
            # 사용자 점수를 배열로 변환 및 정규화
            user_score_array = np.array([user_scores.get(col, 3) for col in self.score_columns])
            user_score_normalized = self.scaler.transform([user_score_array])
            
            # 코사인 유사도 계산
            similarities = cosine_similarity(user_score_normalized, self.normalized_scores)[0]
            
            # 유사도 순으로 정렬하여 상위 k개 추출
            top_indices = similarities.argsort()[-top_k:][::-1]
            
            # 추천 결과 생성
            recommendations = []
            for idx in top_indices:
                posting_info = {
                    '공고일련번호': self.job_posting_scores.iloc[idx]['공고일련번호'],
                    '기관코드': self.job_posting_scores.iloc[idx]['기관코드'],
                    '일반전형': self.job_posting_scores.iloc[idx]['일반전형'],
                    '유사도': float(similarities[idx])
                }
                recommendations.append(posting_info)
            
            print(f"✅ 유사한 채용공고 {len(recommendations)}개 찾기 완료")
            return recommendations
            
        except Exception as e:
            print(f"❌ 유사 공고 찾기 실패: {e}")
            return []
    
    def preprocess_data(self):
        """데이터 전처리 - 데이터베이스 방식에서는 유사도 모델 준비"""
        if self.data_source == 'database':
            return self.prepare_similarity_model()
        else:
            # 기존 API/CSV 방식
            return self.preprocess_data_legacy()
    
    def preprocess_data_legacy(self):
        """데이터 전처리 - 일반전형 분리 및 확장 (기존 방식)"""
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
    
    def load_scores_from_api(self):
        """REST API에서 점수 데이터 로딩"""
        try:
            print(f"🎯 API에서 점수 데이터 로딩 중: {self.scores_api_url}")
            
            response = requests.get(self.scores_api_url, timeout=30)
            
            # HTTP 상태 코드 확인하되, 500 에러여도 응답 데이터가 있으면 사용
            if response.status_code == 200:
                data = response.json()
            elif response.status_code == 500:
                # 500 에러이지만 JSON 응답이 있는 경우 (샘플 데이터 등)
                try:
                    data = response.json()
                    if 'data' in data and data['data']:
                        print(f"⚠️ API 서버 오류(500)이지만 데이터를 사용합니다: {data.get('message', '')}")
                    else:
                        raise ValueError("응답에 유효한 데이터가 없습니다")
                except (ValueError, KeyError):
                    response.raise_for_status()  # 정상적인 500 에러로 처리
            else:
                response.raise_for_status()
            
            # JSON 데이터를 DataFrame으로 변환
            if isinstance(data, list):
                scores_df = pd.DataFrame(data)
            elif isinstance(data, dict) and 'data' in data:
                scores_df = pd.DataFrame(data['data'])
            elif isinstance(data, dict) and 'scores' in data:
                scores_df = pd.DataFrame(data['scores'])
            else:
                scores_df = pd.DataFrame([data])
            
            # 필수 컬럼 확인
            required_columns = ['기관명', '일반전형'] + self.score_columns
            missing_columns = [col for col in required_columns if col not in scores_df.columns]
            
            if missing_columns:
                print(f"❌ API 점수 데이터에 필수 컬럼이 없습니다: {missing_columns}")
                print("🔄 자동 점수 생성으로 대체합니다...")
                return False
            
            # df_processed와 매칭하여 점수 데이터 생성
            merged_df = self.df_processed.merge(
                scores_df[required_columns], 
                on=['기관명', '일반전형'], 
                how='left'
            )
            
            # 매칭되지 않은 데이터 확인
            missing_scores = merged_df[merged_df[self.score_columns[0]].isna()]
            
            if len(missing_scores) > 0:
                print(f"⚠️ API에서 점수를 찾을 수 없는 전형: {len(missing_scores)}개")
                print("🔄 누락된 전형에 대해 자동 점수 생성을 수행합니다...")
                
                # 누락된 전형에 대해 자동 점수 생성
                for idx in missing_scores.index:
                    form = merged_df.loc[idx, '일반전형']
                    for column in self.score_columns:
                        if pd.isna(merged_df.loc[idx, column]):
                            merged_df.loc[idx, column] = self._generate_score_for_form(form, column)
            
            self.df_scores = merged_df
            print(f"✅ API 점수 데이터 로딩 완료: {len(self.df_scores)}개 전형 프로파일")
            print(f"📊 API에서 로딩된 전형: {len(self.df_scores) - len(missing_scores)}개")
            if len(missing_scores) > 0:
                print(f"🔄 자동 생성된 전형: {len(missing_scores)}개")
            
            return True
            
        except requests.exceptions.RequestException as e:
            print(f"❌ 점수 API 요청 실패: {e}")
            print("🔄 자동 점수 생성으로 대체합니다...")
            return False
        except Exception as e:
            print(f"❌ 점수 API 데이터 처리 실패: {e}")
            print("🔄 자동 점수 생성으로 대체합니다...")
            return False
    
    def _generate_score_for_form(self, form, column):
        """개별 전형-컬럼에 대한 점수 생성"""
        # 기존 generate_scores 로직에서 추출한 점수 생성 규칙
        if '운영' in form or '사무' in form:
            if column in ['성실성', '자기관리', '대인-영향력', '공감-사회기술']:
                return np.random.randint(3, 6)
            else:
                return np.random.randint(2, 5)
        elif any(keyword in form for keyword in ['기술', '전기', '기계', '토목', '건축', '통신', '신호']):
            if column in ['기술전문성', '인지문제해결', '학습속도', '자기관리']:
                return np.random.randint(3, 6)
            else:
                return np.random.randint(2, 5)
        elif '운전' in form:
            if column in ['성실성', '정서안정성', '적응력', '자기관리']:
                return np.random.randint(3, 6)
            else:
                return np.random.randint(2, 5)
        elif '공무' in form:
            if column in ['성실성', '기술전문성', '자기관리']:
                return np.random.randint(3, 6)
            else:
                return np.random.randint(2, 5)
        else:
            return np.random.randint(2, 5)
    
    def generate_scores_from_rules(self):
        """전형별 특성화된 점수 생성 (기존 방식)"""
        try:
            print("🎯 규칙 기반 점수 생성 중...")
            
            self.df_scores = self.df_processed.copy()
            
            # 일반전형별 기준 점수 생성
            np.random.seed(42)  # 재현 가능한 결과
            unique_forms = self.df_processed['일반전형'].unique()
            base_scores = {}
            
            for form in unique_forms:
                base_scores[form] = {}
                for column in self.score_columns:
                    base_scores[form][column] = self._generate_score_for_form(form, column)
            
            # 각 행에 대해 기준 점수에서 약간의 변동을 가진 점수 할당
            for idx, row in self.df_scores.iterrows():
                form = row['일반전형']
                for column in self.score_columns:
                    base_score = base_scores[form][column]
                    # 기준 점수에서 ±1 범위의 변동 (1~5 범위 유지)
                    variation = np.random.randint(-1, 2)
                    final_score = max(1, min(5, base_score + variation))
                    self.df_scores.loc[idx, column] = final_score
            
            print(f"✅ 규칙 기반 점수 생성 완료: {len(self.df_scores)}개 전형 프로파일")
            return True
            
        except Exception as e:
            print(f"❌ 점수 생성 실패: {e}")
            return False
    
    def generate_scores(self):
        """점수 생성 - 데이터베이스 방식에서는 스킵 (이미 점수가 있음)"""
        if self.data_source == 'database':
            print("✅ 데이터베이스 방식: 점수 데이터가 이미 존재합니다.")
            return True
        else:
            # 기존 API/CSV 방식
            if self.data_source == 'api':
                # API 모드일 때 점수 API 시도
                if self.load_scores_from_api():
                    return True
                else:
                    print("📋 점수 API 실패로 규칙 기반 점수 생성을 사용합니다...")
                    return self.generate_scores_from_rules()
            else:
                # CSV 모드일 때는 규칙 기반 생성
                return self.generate_scores_from_rules()
    
    def create_form_profiles(self):
        """전형별 평균 프로파일 생성"""
        if self.data_source == 'database':
            return self.create_database_profiles()
        else:
            return self.create_legacy_profiles()
    
    def create_database_profiles(self):
        """데이터베이스 방식: 기관코드별 전형 프로파일 생성"""
        try:
            print("📊 데이터베이스 기반 프로파일 생성 중...")
            
            if self.job_posting_scores is None:
                print("❌ 채용공고평가점수 데이터가 없습니다.")
                return False
            
            # 기관코드 + 일반전형별 평균 점수 계산
            self.form_profiles = self.job_posting_scores.groupby(['기관코드', '일반전형'])[self.score_columns].mean()
            
            # 전형별 통계 정보도 생성
            self.form_stats = {
                'total_postings': len(self.job_posting_scores),
                'unique_agencies': self.job_posting_scores['기관코드'].nunique(),
                'unique_forms': self.job_posting_scores['일반전형'].nunique(),
                'agency_form_combinations': len(self.form_profiles)
            }
            
            print(f"✅ 데이터베이스 프로파일 생성 완료:")
            print(f"   📋 총 공고 수: {self.form_stats['total_postings']}")
            print(f"   🏢 고유 기관 수: {self.form_stats['unique_agencies']}")
            print(f"   📝 고유 전형 수: {self.form_stats['unique_forms']}")
            print(f"   🔗 기관-전형 조합: {self.form_stats['agency_form_combinations']}")
            
            return True
            
        except Exception as e:
            print(f"❌ 데이터베이스 프로파일 생성 실패: {e}")
            return False
    
    def create_legacy_profiles(self):
        """기존 방식: 전형별 평균 프로파일 생성"""
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
            
            if self.data_source == 'database':
                # 데이터베이스 방식 모델 정보
                self.model_info = {
                    'version': f'v{timestamp}',
                    'created_at': datetime.now().isoformat(),
                    'data_source': {
                        'source_type': 'database',
                        'table_name': '채용공고평가점수'
                    },
                    'total_postings': self.form_stats['total_postings'],
                    'unique_agencies': self.form_stats['unique_agencies'],
                    'unique_forms': self.form_stats['unique_forms'],
                    'agency_form_combinations': self.form_stats['agency_form_combinations'],
                    'score_columns': self.score_columns,
                    'model_type': 'similarity_based_recommendation'
                }
                
                # 1. 유사도 모델 저장 (스케일러 + 정규화된 점수)
                similarity_model = {
                    'scaler': self.scaler,
                    'normalized_scores': self.normalized_scores,
                    'job_posting_scores': self.job_posting_scores
                }
                similarity_path = os.path.join(model_dir, 'similarity_model.pkl')
                with open(similarity_path, 'wb') as f:
                    pickle.dump(similarity_model, f)
                
                # 2. 전형 프로파일 저장 (pickle)
                profile_path = os.path.join(model_dir, 'form_profiles.pkl')
                with open(profile_path, 'wb') as f:
                    pickle.dump(self.form_profiles, f)
                
                print(f"✅ 데이터베이스 모델 저장 완료:")
                print(f"   📁 디렉토리: {model_dir}")
                print(f"   🎯 유사도 모델: {similarity_path}")
                print(f"   📊 전형 프로파일: {profile_path}")
                
            else:
                # 기존 API/CSV 방식
                data_source_info = {
                    'source_type': self.data_source,
                    'api_url': self.api_url if self.data_source == 'api' else None,
                    'scores_api_url': self.scores_api_url if self.data_source == 'api' else None,
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
                    'score_columns': self.score_columns,
                    'model_type': 'legacy_form_based'
                }
                
                # 1. 전형 프로파일 저장 (pickle)
                profile_path = os.path.join(model_dir, 'form_profiles.pkl')
                with open(profile_path, 'wb') as f:
                    pickle.dump(self.form_profiles, f)
                
                # 2. 점수 데이터 저장 (pickle)
                scores_path = os.path.join(model_dir, 'scores_data.pkl')
                with open(scores_path, 'wb') as f:
                    pickle.dump(self.df_scores, f)
                
                print(f"✅ 레거시 모델 저장 완료:")
                print(f"   📁 디렉토리: {model_dir}")
                print(f"   📊 전형 프로파일: {profile_path}")
                print(f"   📈 점수 데이터: {scores_path}")
            
            # 3. 모델 정보 저장 (JSON) - 공통
            info_path = os.path.join(model_dir, 'model_info.json')
            with open(info_path, 'w', encoding='utf-8') as f:
                json.dump(self.model_info, f, ensure_ascii=False, indent=2)
            
            # 4. 추천 함수 저장 (데이터베이스 방식에서만)
            if self.data_source == 'database':
                recommendation_function = """
def recommend_job_postings(user_scores, model_dir='./models', top_k=5):
    \"\"\"
    사용자 점수를 받아 유사한 채용공고 추천
    
    Args:
        user_scores (dict): 사용자의 16가지 점수
        model_dir (str): 모델 디렉토리 경로
        top_k (int): 추천할 공고 수
    
    Returns:
        list: 추천 공고일련번호와 유사도 정보
    \"\"\"
    import pickle
    import numpy as np
    from sklearn.metrics.pairwise import cosine_similarity
    
    # 모델 로딩
    with open(f'{model_dir}/similarity_model.pkl', 'rb') as f:
        model = pickle.load(f)
    
    scaler = model['scaler']
    normalized_scores = model['normalized_scores']
    job_posting_scores = model['job_posting_scores']
    
    score_columns = [
        '성실성', '개방성', '외향성', '우호성', '정서안정성', '기술전문성',
        '인지문제해결', '대인-영향력', '자기관리', '적응력', '학습속도',
        '대인민첩성', '성과민첩성', '자기인식', '자기조절', '공감-사회기술'
    ]
    
    # 사용자 점수 정규화
    user_score_array = np.array([user_scores.get(col, 3) for col in score_columns])
    user_score_normalized = scaler.transform([user_score_array])
    
    # 유사도 계산
    similarities = cosine_similarity(user_score_normalized, normalized_scores)[0]
    
    # 상위 k개 추천
    top_indices = similarities.argsort()[-top_k:][::-1]
    
    recommendations = []
    for idx in top_indices:
        recommendations.append({
            '공고일련번호': job_posting_scores.iloc[idx]['공고일련번호'],
            '기관코드': job_posting_scores.iloc[idx]['기관코드'],
            '일반전형': job_posting_scores.iloc[idx]['일반전형'],
            '유사도': float(similarities[idx])
        })
    
    return recommendations
"""
                func_path = os.path.join(model_dir, 'recommendation_function.py')
                with open(func_path, 'w', encoding='utf-8') as f:
                    f.write(recommendation_function)
                
                print(f"   🎯 추천 함수: {func_path}")
            
            print(f"   ℹ️ 모델 정보: {info_path}")
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
        
        if self.data_source == 'database':
            print(f"   - 총 공고 수: {self.model_info.get('total_postings', 'N/A')}")
            print(f"   - 기관 수: {self.model_info.get('unique_agencies', 'N/A')}")
            print(f"   - 전형 수: {self.model_info.get('unique_forms', 'N/A')}")
        else:
            print(f"   - 전형 수: {self.model_info.get('unique_forms', 'N/A')}")
            print(f"   - 기관 수: {self.model_info.get('unique_organizations', 'N/A')}")
            print(f"   - 데이터 레코드: {self.model_info.get('processed_records', 'N/A')}")
        
        return True

def main():
    """메인 실행 함수"""
    import argparse
    
    parser = argparse.ArgumentParser(description='채용 전형 추천 모델 빌더')
    parser.add_argument('--source', choices=['database', 'api', 'csv'], default='database', 
                        help='데이터 소스 (database: MariaDB 채용공고평가점수 테이블, api: REST API, csv: CSV 파일)')
    parser.add_argument('--api-url', default='http://mysite.com/recruits',
                        help='채용 데이터 API URL (레거시)')
    parser.add_argument('--scores-api-url', default='http://mysite.com/scores',
                        help='점수 데이터 API URL (레거시)')
    parser.add_argument('--csv-path', default='./data/all_data.csv',
                        help='CSV 파일 경로 (레거시)')
    parser.add_argument('--output-dir', default='./models',
                        help='모델 저장 디렉토리')
    
    args = parser.parse_args()
    
    print("🚀 채용 공고 유사도 기반 추천 모델 빌더 시작")
    print("=" * 60)
    print(f"📡 데이터 소스: {args.source.upper()}")
    
    if args.source == 'database':
        print("🗄️ MariaDB 채용공고평가점수 테이블에서 데이터 로딩")
        print("🎯 유사도 기반 추천 시스템 구축")
        print("📊 16가지 점수를 통한 개인화된 공고 추천")
    elif args.source == 'api':
        print(f"🌐 채용 데이터 API: {args.api_url}")
        print(f"🎯 점수 데이터 API: {args.scores_api_url}")
        print("📋 백업: CSV 파일 사용 (API 실패 시)")
    else:
        print(f"📂 CSV 파일: {args.csv_path}")
    
    print(f"💾 출력 디렉토리: {args.output_dir}")
    print("=" * 60)
    
    # 모델 빌더 생성
    builder = JobRecommendationModelBuilder(
        data_source=args.source,
        api_url=args.api_url,
        scores_api_url=args.scores_api_url,
        csv_path=args.csv_path
    )
    
    # 모델 빌드 및 저장
    if builder.build_and_save_model(args.output_dir):
        print("\n✅ 모델이 성공적으로 생성되고 저장되었습니다!")
        
        if args.source == 'database':
            print("\n🎯 데이터베이스 기반 추천 시스템 사용법:")
            print("   1. 사용자의 16가지 점수 입력")
            print("   2. from models.recommendation_function import recommend_job_postings")
            print("   3. recommendations = recommend_job_postings(user_scores)")
            print("\n📋 사용자 점수 형식:")
            print("   user_scores = {")
            print("       '성실성': 4, '개방성': 3, '외향성': 5, ...")
            print("       # 16가지 모든 점수 포함")
            print("   }")
            print(f"\n� 모델 정보:")
            print(f"   - 총 채용공고: {builder.model_info.get('total_postings', 'N/A')}")
            print(f"   - 기관 수: {builder.model_info.get('unique_agencies', 'N/A')}")
            print(f"   - 전형 수: {builder.model_info.get('unique_forms', 'N/A')}")
        else:
            print("�💡 이제 API 서버에서 이 모델을 로딩하여 사용할 수 있습니다.")
            
            if args.source == 'api':
                print("\n🔄 모델 업데이트 방법:")
                print("   1. 새로운 채용 데이터가 API에 추가되면")
                print("   2. python3 model_builder.py --source api")
                print("   3. curl -X POST http://localhost:8080/reload_model")
                print("\n🎯 점수 데이터 API 형식:")
                print("   GET /scores 응답 예시:")
                print('   [{"기관명": "기관명", "일반전형": "전형명", "성실성": 4, "개방성": 3, ...}]')
    else:
        print("\n❌ 모델 생성에 실패했습니다.")
        if args.source == 'database':
            print("💡 데이터베이스 연결 또는 테이블 문제일 수 있습니다.")
            print("   - MariaDB 서버 연결 상태 확인")
            print("   - 채용공고평가점수 테이블 존재 여부 확인")
            print("   - 테이블에 데이터가 있는지 확인")
        elif args.source == 'api':
            print("💡 API 연결 문제일 수 있습니다. CSV 모드로 시도해보세요:")
            print("   python3 model_builder.py --source csv")

if __name__ == "__main__":
    main()
