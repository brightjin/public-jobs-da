#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
채용공고 평가점수 테이블 생성 스크립트
TMP_채용공고_분리 테이블의 기관명, 공고명, 일반전형 컬럼을 분석하여
16개 평가점수를 생성하고 TMP_채용공고평가점수 테이블을 신규 생성
"""

import pandas as pd
import numpy as np
import re
import logging
from datetime import datetime
from database_manager import DatabaseManager
from log_config import setup_logger

# 로거 설정
logger = setup_logger('job_score_generator', 'create_job_posting_scores.log')

class JobPostingScoreGenerator:
    """채용공고 평가점수 생성기"""
    
    def __init__(self):
        self.db = DatabaseManager(database='sangsang')
        self.db.connect()  # 데이터베이스 연결
        self.score_columns = [
            '성실성', '개방성', '외향성', '우호성', '정서안정성', '기술전문성',
            '인지문제해결', '대인영향력', '자기관리', '적응력', '학습속도', 
            '대인민첩성', '성과민첩성', '자기인식', '자기조절', '공감사회기술'
        ]
        
    def create_table(self):
        """TMP_채용공고평가점수 테이블 생성"""
        try:
            logger.info("TMP_채용공고평가점수 테이블 생성 시작")
            
            # 기존 테이블 삭제
            drop_query = "DROP TABLE IF EXISTS TMP_채용공고평가점수"
            self.db.execute_query(drop_query, fetch=False)
            logger.info("기존 TMP_채용공고평가점수 테이블 삭제 완료")
            
            # 새 테이블 생성
            create_query = """
            CREATE TABLE TMP_채용공고평가점수 (
                id INT AUTO_INCREMENT PRIMARY KEY,
                기관명 VARCHAR(255) NOT NULL,
                공고명 TEXT,
                일반전형 VARCHAR(500),
                성실성 INT DEFAULT 0 CHECK (성실성 BETWEEN 1 AND 5),
                개방성 INT DEFAULT 0 CHECK (개방성 BETWEEN 1 AND 5),
                외향성 INT DEFAULT 0 CHECK (외향성 BETWEEN 1 AND 5),
                우호성 INT DEFAULT 0 CHECK (우호성 BETWEEN 1 AND 5),
                정서안정성 INT DEFAULT 0 CHECK (정서안정성 BETWEEN 1 AND 5),
                기술전문성 INT DEFAULT 0 CHECK (기술전문성 BETWEEN 1 AND 5),
                인지문제해결 INT DEFAULT 0 CHECK (인지문제해결 BETWEEN 1 AND 5),
                대인영향력 INT DEFAULT 0 CHECK (대인영향력 BETWEEN 1 AND 5),
                자기관리 INT DEFAULT 0 CHECK (자기관리 BETWEEN 1 AND 5),
                적응력 INT DEFAULT 0 CHECK (적응력 BETWEEN 1 AND 5),
                학습속도 INT DEFAULT 0 CHECK (학습속도 BETWEEN 1 AND 5),
                대인민첩성 INT DEFAULT 0 CHECK (대인민첩성 BETWEEN 1 AND 5),
                성과민첩성 INT DEFAULT 0 CHECK (성과민첩성 BETWEEN 1 AND 5),
                자기인식 INT DEFAULT 0 CHECK (자기인식 BETWEEN 1 AND 5),
                자기조절 INT DEFAULT 0 CHECK (자기조절 BETWEEN 1 AND 5),
                공감사회기술 INT DEFAULT 0 CHECK (공감사회기술 BETWEEN 1 AND 5),
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                INDEX idx_기관명 (기관명),
                INDEX idx_일반전형 (일반전형(100))
            ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci
            """
            
            self.db.execute_query(create_query, fetch=False)
            logger.info("TMP_채용공고평가점수 테이블 생성 완료")
            print("✅ TMP_채용공고평가점수 테이블 생성 완료")
            return True
            
        except Exception as e:
            logger.error(f"테이블 생성 실패: {e}")
            print(f"❌ 테이블 생성 실패: {e}")
            return False
    
    def load_source_data(self):
        """소스 데이터 로드"""
        try:
            logger.info("소스 데이터 로드 시작")
            
            query = """
            SELECT id, 기관명, 공고명, 일반전형
            FROM TMP_채용공고_분리
            ORDER BY id
            """
            
            result = self.db.execute_query(query)
            if not result:
                logger.error("소스 데이터가 없습니다")
                return None
                
            df = pd.DataFrame(result, columns=['id', '기관명', '공고명', '일반전형'])
            logger.info(f"소스 데이터 로드 완료: {len(df)}개 레코드")
            print(f"📊 소스 데이터 로드 완료: {len(df)}개 레코드")
            return df
            
        except Exception as e:
            logger.error(f"소스 데이터 로드 실패: {e}")
            print(f"❌ 소스 데이터 로드 실패: {e}")
            return None
    
    def analyze_job_characteristics(self, 기관명, 공고명, 일반전형):
        """채용공고 특성 분석 및 가중치 계산"""
        weights = {col: 1.0 for col in self.score_columns}
        
        # 텍스트 결합 및 전처리
        combined_text = f"{기관명} {공고명} {일반전형}".lower()
        
        # 1. 기술/전문직 가중치
        tech_keywords = ['기술', '연구', '개발', 'it', '정보', '시스템', '프로그램', '엔지니어', '전산', '소프트웨어']
        if any(keyword in combined_text for keyword in tech_keywords):
            weights['기술전문성'] *= 1.5
            weights['인지문제해결'] *= 1.4
            weights['학습속도'] *= 1.3
            weights['자기관리'] *= 1.2
        
        # 2. 행정/사무직 가중치
        admin_keywords = ['사무', '행정', '관리', '총무', '기획', '회계', '인사']
        if any(keyword in combined_text for keyword in admin_keywords):
            weights['성실성'] *= 1.4
            weights['자기관리'] *= 1.3
            weights['공감사회기술'] *= 1.2
            weights['대인영향력'] *= 1.2
        
        # 3. 대인서비스 가중치
        service_keywords = ['고객', '상담', '민원', '안내', '서비스', '접수']
        if any(keyword in combined_text for keyword in service_keywords):
            weights['외향성'] *= 1.4
            weights['우호성'] *= 1.3
            weights['공감사회기술'] *= 1.3
            weights['대인민첩성'] *= 1.2
        
        # 4. 경력/신입 구분
        if '신입' in combined_text or '경력무관' in combined_text:
            weights['학습속도'] *= 1.3
            weights['적응력'] *= 1.2
            weights['개방성'] *= 1.2
        elif '경력' in combined_text:
            weights['성실성'] *= 1.2
            weights['자기관리'] *= 1.2
            weights['성과민첩성'] *= 1.2
        
        # 5. 관리직 가중치
        manager_keywords = ['팀장', '과장', '부장', '관리자', '책임자', '리더']
        if any(keyword in combined_text for keyword in manager_keywords):
            weights['대인영향력'] *= 1.4
            weights['자기조절'] *= 1.3
            weights['성과민첩성'] *= 1.3
            weights['자기인식'] *= 1.2
        
        return weights
    
    def generate_score_with_weights(self, weights):
        """가중치를 적용한 점수 생성"""
        scores = {}
        
        for col in self.score_columns:
            # 기본 점수: 평균 3.0, 표준편차 0.8의 정규분포
            base_score = np.random.normal(3.0, 0.8)
            
            # 가중치 적용
            weighted_score = base_score * weights[col]
            
            # 점수 범위 제한 (1 ~ 5)
            final_score = max(1, min(5, weighted_score))
            
            # 정수로 반올림
            scores[col] = int(round(final_score))
        
        return scores
    
    def generate_all_scores(self, df):
        """모든 레코드의 점수 생성"""
        try:
            logger.info("점수 생성 시작")
            all_scores = []
            
            for idx, row in df.iterrows():
                # 특성 분석 및 가중치 계산
                weights = self.analyze_job_characteristics(
                    row['기관명'], row['공고명'], row['일반전형']
                )
                
                # 가중치 적용 점수 생성
                scores = self.generate_score_with_weights(weights)
                
                # 기본 정보 추가
                score_data = {
                    '기관명': row['기관명'],
                    '공고명': row['공고명'],
                    '일반전형': row['일반전형']
                }
                score_data.update(scores)
                all_scores.append(score_data)
                
                if (idx + 1) % 50 == 0:
                    print(f"  📈 진행률: {idx + 1}/{len(df)} ({(idx + 1)/len(df)*100:.1f}%)")
            
            logger.info(f"점수 생성 완료: {len(all_scores)}개")
            print(f"✅ 점수 생성 완료: {len(all_scores)}개")
            return all_scores
            
        except Exception as e:
            logger.error(f"점수 생성 실패: {e}")
            print(f"❌ 점수 생성 실패: {e}")
            return None
    
    def insert_scores(self, scores_data):
        """점수 데이터 삽입"""
        try:
            logger.info("점수 데이터 삽입 시작")
            
            insert_query = f"""
            INSERT INTO TMP_채용공고평가점수 
            (기관명, 공고명, 일반전형, {', '.join(self.score_columns)})
            VALUES (%(기관명)s, %(공고명)s, %(일반전형)s, {', '.join([f'%({col})s' for col in self.score_columns])})
            """
            
            success_count = 0
            batch_size = 50
            
            for i in range(0, len(scores_data), batch_size):
                batch = scores_data[i:i + batch_size]
                
                for data in batch:
                    try:
                        self.db.execute_query(insert_query, data, fetch=False)
                        success_count += 1
                    except Exception as e:
                        logger.warning(f"데이터 삽입 실패: {data['기관명']} - {e}")
                
                print(f"  📥 삽입 진행률: {min(i + batch_size, len(scores_data))}/{len(scores_data)} ({min(i + batch_size, len(scores_data))/len(scores_data)*100:.1f}%)")
            
            logger.info(f"점수 데이터 삽입 완료: {success_count}/{len(scores_data)}개")
            print(f"✅ 점수 데이터 삽입 완료: {success_count}/{len(scores_data)}개")
            return success_count > 0
            
        except Exception as e:
            logger.error(f"점수 데이터 삽입 실패: {e}")
            print(f"❌ 점수 데이터 삽입 실패: {e}")
            return False
    
    def verify_results(self):
        """결과 검증"""
        try:
            logger.info("결과 검증 시작")
            
            # 전체 레코드 수 확인
            count_query = "SELECT COUNT(*) FROM TMP_채용공고평가점수"
            result = self.db.execute_query(count_query)
            total_count = result[0][0] if result else 0
            
            print(f"\n📊 검증 결과:")
            print(f"   총 레코드 수: {total_count}개")
            
            # 점수 통계
            stats_query = f"""
            SELECT 
                AVG(`성실성`) as avg_성실성,
                AVG(`기술전문성`) as avg_기술전문성,
                AVG(`인지문제해결`) as avg_인지문제해결,
                AVG(`대인영향력`) as avg_대인영향력,
                MIN(`성실성`) as min_score,
                MAX(`성실성`) as max_score
            FROM TMP_채용공고평가점수
            """
            
            result = self.db.execute_query(stats_query)
            if result:
                stats = result[0]
                print(f"   평균 성실성: {stats[0]:.2f}")
                print(f"   평균 기술전문성: {stats[1]:.2f}")
                print(f"   평균 인지문제해결: {stats[2]:.2f}")
                print(f"   평균 대인영향력: {stats[3]:.2f}")
                print(f"   점수 범위: {stats[4]:.1f} ~ {stats[5]:.1f}")
            
            # 샘플 데이터
            sample_query = """
            SELECT 기관명, 일반전형, 성실성, 기술전문성, 인지문제해결, 대인영향력
            FROM TMP_채용공고평가점수
            ORDER BY id
            LIMIT 3
            """
            
            result = self.db.execute_query(sample_query)
            if result:
                print(f"\n📝 샘플 데이터:")
                for row in result:
                    print(f"   {row[0]} | {row[1]} | 성실성:{row[2]} | 기술:{row[3]} | 인지:{row[4]} | 대인:{row[5]}")
            
            logger.info("결과 검증 완료")
            return True
            
        except Exception as e:
            logger.error(f"결과 검증 실패: {e}")
            print(f"❌ 결과 검증 실패: {e}")
            return False
    
    def run(self):
        """전체 프로세스 실행"""
        print("=" * 60)
        print("🚀 TMP_채용공고평가점수 테이블 생성 시작")
        print(f"⏰ 시작 시간: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print("=" * 60)
        
        steps = [
            ("테이블 생성", self.create_table),
            ("소스 데이터 로드", lambda: self.load_source_data()),
            ("점수 생성 및 삽입", self.process_scores),
            ("결과 검증", self.verify_results)
        ]
        
        self.source_df = None
        
        for step_name, step_func in steps:
            print(f"\n📋 {step_name}...")
            
            if step_name == "소스 데이터 로드":
                self.source_df = step_func()
                if self.source_df is None:
                    print(f"❌ {step_name} 실패")
                    return False
            elif step_name == "점수 생성 및 삽입":
                if not step_func():
                    print(f"❌ {step_name} 실패")
                    return False
            else:
                if not step_func():
                    print(f"❌ {step_name} 실패")
                    return False
        
        print("\n" + "=" * 60)
        print("🎉 TMP_채용공고평가점수 테이블 생성 완료!")
        print(f"⏰ 완료 시간: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print("📊 이제 이 테이블을 사용하여 유사도 기반 추천 모델을 구축할 수 있습니다.")
        print("=" * 60)
        return True
    
    def process_scores(self):
        """점수 생성 및 삽입 프로세스"""
        if self.source_df is None:
            print("❌ 소스 데이터가 없습니다")
            return False
        
        # 점수 생성
        scores_data = self.generate_all_scores(self.source_df)
        if scores_data is None:
            return False
        
        # 점수 삽입
        return self.insert_scores(scores_data)

def main():
    """메인 함수"""
    generator = JobPostingScoreGenerator()
    
    if generator.run():
        print("\n✅ 모든 작업이 성공적으로 완료되었습니다!")
        print("\n💡 다음 단계:")
        print("   1. python model_builder.py --source database")
        print("   2. 유사도 기반 추천 모델 구축")
        print("   3. API 서버에서 추천 시스템 사용")
    else:
        print("\n❌ 작업 중 오류가 발생했습니다.")
        print("💡 로그 파일을 확인하여 상세 오류를 파악하세요.")

if __name__ == "__main__":
    main()
