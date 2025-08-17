"""
MariaDB 데이터베이스 연동 모듈
- 점수 데이터 조회 (scores 테이블)
- 추천 결과 저장 (recommendations 테이블)
- 채용공고평가점수 테이블 지원
"""

import pymysql
import pandas as pd
import json
import os
from datetime import datetime
from typing import List, Dict, Any, Optional
import logging

# 로깅 설정
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class DatabaseManager:
    """MariaDB 데이터베이스 관리 클래스"""
    
    def __init__(self, host=None, port=None, user=None, password=None, database=None):
        """
        데이터베이스 연결 초기화
        
        Args:
            host: MariaDB 호스트 주소 (환경변수 DB_HOST 우선)
            port: MariaDB 포트 번호 (환경변수 DB_PORT 우선)
            user: 데이터베이스 사용자명 (환경변수 DB_USER 우선)
            password: 데이터베이스 비밀번호 (환경변수 DB_PASSWORD 우선)
            database: 데이터베이스 이름 (환경변수 DB_NAME 우선)
        """
        self.host = host or os.getenv('DB_HOST', 'localhost')
        self.port = int(port or os.getenv('DB_PORT', 3306))
        self.user = user or os.getenv('DB_USER', 'root')
        self.password = password or os.getenv('DB_PASSWORD', '')
        self.database = database or os.getenv('DB_NAME', 'dive_recruit')
        self.connection = None
    
    def connect(self):
        """데이터베이스 연결"""
        try:
            self.connection = pymysql.connect(
                host=self.host,
                port=self.port,
                user=self.user,
                password=self.password,
                database=self.database,
                charset='utf8mb4',
                autocommit=True
            )
            logger.info(f"✅ 데이터베이스 연결 성공: {self.database}")
            return True
        except Exception as e:
            logger.error(f"❌ 데이터베이스 연결 실패: {str(e)}")
            return False
    
    def disconnect(self):
        """데이터베이스 연결 종료"""
        if self.connection:
            self.connection.close()
            logger.info("🔌 데이터베이스 연결 종료")
    
    def __enter__(self):
        """컨텍스트 매니저 진입"""
        self.connect()
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """컨텍스트 매니저 종료"""
        self.disconnect()
    
    def execute_query(self, sql: str, params=None, fetch=True):
        """
        SQL 쿼리 실행
        
        Args:
            sql: 실행할 SQL 쿼리
            params: 쿼리 파라미터 (dict 또는 tuple)
            fetch: 결과를 반환할지 여부
            
        Returns:
            fetch=True인 경우 쿼리 결과, 그렇지 않으면 None
        """
        try:
            with self.connection.cursor() as cursor:
                cursor.execute(sql, params)
                
                if fetch:
                    return cursor.fetchall()
                else:
                    return None
                    
        except Exception as e:
            logger.error(f"❌ 쿼리 실행 실패: {str(e)}")
            raise
    
    def create_tables(self):
        """필요한 테이블 생성"""
        try:
            with self.connection.cursor() as cursor:
                # 점수 데이터 테이블
                scores_table_sql = """
                CREATE TABLE IF NOT EXISTS scores (
                    id INT AUTO_INCREMENT PRIMARY KEY,
                    기관명 VARCHAR(100) NOT NULL,
                    일반전형 VARCHAR(100) NOT NULL,
                    성실성 INT CHECK (성실성 >= 1 AND 성실성 <= 5),
                    개방성 INT CHECK (개방성 >= 1 AND 개방성 <= 5),
                    외향성 INT CHECK (외향성 >= 1 AND 외향성 <= 5),
                    우호성 INT CHECK (우호성 >= 1 AND 우호성 <= 5),
                    정서안정성 INT CHECK (정서안정성 >= 1 AND 정서안정성 <= 5),
                    기술전문성 INT CHECK (기술전문성 >= 1 AND 기술전문성 <= 5),
                    인지문제해결 INT CHECK (인지문제해결 >= 1 AND 인지문제해결 <= 5),
                    `대인-영향력` INT CHECK (`대인-영향력` >= 1 AND `대인-영향력` <= 5),
                    자기관리 INT CHECK (자기관리 >= 1 AND 자기관리 <= 5),
                    적응력 INT CHECK (적응력 >= 1 AND 적응력 <= 5),
                    학습속도 INT CHECK (학습속도 >= 1 AND 학습속도 <= 5),
                    대인민첩성 INT CHECK (대인민첩성 >= 1 AND 대인민첩성 <= 5),
                    성과민첩성 INT CHECK (성과민첩성 >= 1 AND 성과민첩성 <= 5),
                    자기인식 INT CHECK (자기인식 >= 1 AND 자기인식 <= 5),
                    자기조절 INT CHECK (자기조절 >= 1 AND 자기조절 <= 5),
                    `공감-사회기술` INT CHECK (`공감-사회기술` >= 1 AND `공감-사회기술` <= 5),
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
                    UNIQUE KEY unique_form (기관명, 일반전형)
                ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci
                """
                
                # 추천 결과 저장 테이블
                recommendations_table_sql = """
                CREATE TABLE IF NOT EXISTS recommendations (
                    id INT AUTO_INCREMENT PRIMARY KEY,
                    session_id VARCHAR(100),
                    user_scores JSON NOT NULL,
                    recommendations JSON NOT NULL,
                    profile_analysis JSON,
                    model_version VARCHAR(50),
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    INDEX idx_session_id (session_id),
                    INDEX idx_created_at (created_at)
                ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci
                """
                
                cursor.execute(scores_table_sql)
                cursor.execute(recommendations_table_sql)
                logger.info("✅ 테이블 생성 완료")
                
        except Exception as e:
            logger.error(f"❌ 테이블 생성 실패: {str(e)}")
            raise
    
    def get_scores_data(self) -> List[Dict[str, Any]]:
        """
        점수 데이터를 조회하여 API 형식으로 반환
        
        Returns:
            점수 데이터 리스트
        """
        try:
            with self.connection.cursor(pymysql.cursors.DictCursor) as cursor:
                sql = """
                SELECT 기관명, 일반전형, 성실성, 개방성, 외향성, 우호성, 정서안정성,
                       기술전문성, 인지문제해결, `대인-영향력`, 자기관리, 적응력,
                       학습속도, 대인민첩성, 성과민첩성, 자기인식, 자기조절, `공감-사회기술`
                FROM scores
                ORDER BY 기관명, 일반전형
                """
                cursor.execute(sql)
                results = cursor.fetchall()
                
                logger.info(f"📊 점수 데이터 조회 완료: {len(results)}개 레코드")
                return results
                
        except Exception as e:
            logger.error(f"❌ 점수 데이터 조회 실패: {str(e)}")
            raise
    
    def get_scores_dataframe(self) -> pd.DataFrame:
        """
        점수 데이터를 DataFrame으로 반환
        
        Returns:
            점수 데이터 DataFrame
        """
        try:
            scores_data = self.get_scores_data()
            df = pd.DataFrame(scores_data)
            logger.info(f"📊 점수 DataFrame 생성 완료: {df.shape}")
            return df
            
        except Exception as e:
            logger.error(f"❌ 점수 DataFrame 생성 실패: {str(e)}")
            return pd.DataFrame()
    
    def insert_score_data(self, data: Dict[str, Any]) -> bool:
        """
        점수 데이터 삽입
        
        Args:
            data: 점수 데이터 딕셔너리
            
        Returns:
            성공 여부
        """
        try:
            with self.connection.cursor() as cursor:
                sql = """
                INSERT INTO scores (
                    기관명, 일반전형, 성실성, 개방성, 외향성, 우호성, 정서안정성,
                    기술전문성, 인지문제해결, `대인-영향력`, 자기관리, 적응력,
                    학습속도, 대인민첩성, 성과민첩성, 자기인식, 자기조절, `공감-사회기술`
                ) VALUES (
                    %(기관명)s, %(일반전형)s, %(성실성)s, %(개방성)s, %(외향성)s, %(우호성)s, %(정서안정성)s,
                    %(기술전문성)s, %(인지문제해결)s, %(대인-영향력)s, %(자기관리)s, %(적응력)s,
                    %(학습속도)s, %(대인민첩성)s, %(성과민첩성)s, %(자기인식)s, %(자기조절)s, %(공감-사회기술)s
                ) ON DUPLICATE KEY UPDATE
                    성실성=VALUES(성실성), 개방성=VALUES(개방성), 외향성=VALUES(외향성),
                    우호성=VALUES(우호성), 정서안정성=VALUES(정서안정성), 기술전문성=VALUES(기술전문성),
                    인지문제해결=VALUES(인지문제해결), `대인-영향력`=VALUES(`대인-영향력`), 자기관리=VALUES(자기관리),
                    적응력=VALUES(적응력), 학습속도=VALUES(학습속도), 대인민첩성=VALUES(대인민첩성),
                    성과민첩성=VALUES(성과민첩성), 자기인식=VALUES(자기인식), 자기조절=VALUES(자기조절),
                    `공감-사회기술`=VALUES(`공감-사회기술`), updated_at=CURRENT_TIMESTAMP
                """
                cursor.execute(sql, data)
                logger.info(f"✅ 점수 데이터 저장 완료: {data['기관명']} - {data['일반전형']}")
                return True
                
        except Exception as e:
            logger.error(f"❌ 점수 데이터 저장 실패: {str(e)}")
            return False
    
    def bulk_insert_scores(self, scores_list: List[Dict[str, Any]]) -> int:
        """
        점수 데이터 대량 삽입
        
        Args:
            scores_list: 점수 데이터 리스트
            
        Returns:
            성공한 레코드 수
        """
        success_count = 0
        for score_data in scores_list:
            if self.insert_score_data(score_data):
                success_count += 1
        
        logger.info(f"🔄 대량 점수 데이터 저장 완료: {success_count}/{len(scores_list)}개")
        return success_count
    
    def save_recommendation(self, session_id: str, user_scores: Dict[str, int], 
                          recommendations: List[Dict], profile_analysis: Dict = None,
                          model_version: str = None) -> bool:
        """
        추천 결과 저장
        
        Args:
            session_id: 세션 ID
            user_scores: 사용자 입력 점수
            recommendations: 추천 결과 리스트
            profile_analysis: 프로파일 분석 결과
            model_version: 모델 버전
            
        Returns:
            성공 여부
        """
        try:
            with self.connection.cursor() as cursor:
                sql = """
                INSERT INTO recommendations (
                    session_id, user_scores, recommendations, profile_analysis, model_version
                ) VALUES (
                    %s, %s, %s, %s, %s
                )
                """
                cursor.execute(sql, (
                    session_id,
                    json.dumps(user_scores, ensure_ascii=False),
                    json.dumps(recommendations, ensure_ascii=False),
                    json.dumps(profile_analysis, ensure_ascii=False) if profile_analysis else None,
                    model_version
                ))
                
                logger.info(f"✅ 추천 결과 저장 완료: 세션 {session_id}")
                return True
                
        except Exception as e:
            logger.error(f"❌ 추천 결과 저장 실패: {str(e)}")
            return False
    
    def get_recommendations_history(self, session_id: str = None, limit: int = 100) -> List[Dict]:
        """
        추천 결과 이력 조회
        
        Args:
            session_id: 특정 세션 ID (None이면 전체 조회)
            limit: 조회 개수 제한
            
        Returns:
            추천 결과 이력 리스트
        """
        try:
            with self.connection.cursor(pymysql.cursors.DictCursor) as cursor:
                if session_id:
                    sql = """
                    SELECT * FROM recommendations 
                    WHERE session_id = %s 
                    ORDER BY created_at DESC 
                    LIMIT %s
                    """
                    cursor.execute(sql, (session_id, limit))
                else:
                    sql = """
                    SELECT * FROM recommendations 
                    ORDER BY created_at DESC 
                    LIMIT %s
                    """
                    cursor.execute(sql, (limit,))
                
                results = cursor.fetchall()
                
                # JSON 필드 파싱
                for result in results:
                    if result['user_scores']:
                        result['user_scores'] = json.loads(result['user_scores'])
                    if result['recommendations']:
                        result['recommendations'] = json.loads(result['recommendations'])
                    if result['profile_analysis']:
                        result['profile_analysis'] = json.loads(result['profile_analysis'])
                
                logger.info(f"📊 추천 이력 조회 완료: {len(results)}개 레코드")
                return results
                
        except Exception as e:
            logger.error(f"❌ 추천 이력 조회 실패: {str(e)}")
            return []
    
    def get_recommendation_statistics(self) -> Dict[str, Any]:
        """
        추천 통계 정보 조회
        
        Returns:
            통계 정보 딕셔너리
        """
        try:
            with self.connection.cursor(pymysql.cursors.DictCursor) as cursor:
                # 전체 추천 횟수
                cursor.execute("SELECT COUNT(*) as total_recommendations FROM recommendations")
                total_count = cursor.fetchone()['total_recommendations']
                
                # 오늘 추천 횟수
                cursor.execute("""
                    SELECT COUNT(*) as today_recommendations 
                    FROM recommendations 
                    WHERE DATE(created_at) = CURDATE()
                """)
                today_count = cursor.fetchone()['today_recommendations']
                
                # 최다 추천된 전형 TOP 5
                cursor.execute("""
                    SELECT 
                        JSON_EXTRACT(recommendations, '$[0].전형명') as 전형명,
                        COUNT(*) as 추천횟수
                    FROM recommendations 
                    WHERE JSON_EXTRACT(recommendations, '$[0].전형명') IS NOT NULL
                    GROUP BY JSON_EXTRACT(recommendations, '$[0].전형명')
                    ORDER BY COUNT(*) DESC 
                    LIMIT 5
                """)
                top_forms = cursor.fetchall()
                
                stats = {
                    "전체_추천_횟수": total_count,
                    "오늘_추천_횟수": today_count,
                    "최다_추천_전형": top_forms,
                    "조회_시각": datetime.now().isoformat()
                }
                
                logger.info("📊 추천 통계 조회 완료")
                return stats
                
        except Exception as e:
            logger.error(f"❌ 추천 통계 조회 실패: {str(e)}")
            return {}


def main():
    """테스트 및 예제 실행"""
    
    # 샘플 점수 데이터
    sample_scores = [
        {
            "기관명": "부산교통공사",
            "일반전형": "운영직",
            "성실성": 4, "개방성": 3, "외향성": 4, "우호성": 4, "정서안정성": 3,
            "기술전문성": 3, "인지문제해결": 3, "대인-영향력": 4, "자기관리": 5,
            "적응력": 4, "학습속도": 3, "대인민첩성": 4, "성과민첩성": 4,
            "자기인식": 3, "자기조절": 4, "공감-사회기술": 5
        },
        {
            "기관명": "부산교통공사",
            "일반전형": "기계직",
            "성실성": 4, "개방성": 4, "외향성": 2, "우호성": 3, "정서안정성": 3,
            "기술전문성": 5, "인지문제해결": 5, "대인-영향력": 2, "자기관리": 4,
            "적응력": 4, "학습속도": 5, "대인민첩성": 2, "성과민첩성": 3,
            "자기인식": 3, "자기조절": 4, "공감-사회기술": 3
        }
    ]
    
    # 샘플 추천 결과
    sample_recommendation = [
        {"순위": 1, "전형명": "기계직", "적합도": 89.5, "코사인유사도": 0.952},
        {"순위": 2, "전형명": "운영직", "적합도": 75.2, "코사인유사도": 0.823}
    ]
    
    sample_user_scores = {
        "성실성": 4, "개방성": 3, "외향성": 2, "우호성": 3,
        "정서안정성": 4, "기술전문성": 5, "인지문제해결": 5,
        "대인-영향력": 2, "자기관리": 4, "적응력": 4,
        "학습속도": 5, "대인민첩성": 2, "성과민첩성": 3,
        "자기인식": 3, "자기조절": 4, "공감-사회기술": 3
    }
    
    # 데이터베이스 연결 및 테스트
    print("🚀 MariaDB 연동 모듈 테스트 시작")
    print("=" * 50)
    
    try:
        with DatabaseManager(
            host='localhost',
            user='root',
            password='your_password',  # 실제 비밀번호로 변경
            database='dive_recruit'
        ) as db:
            
            # 1. 테이블 생성
            print("📋 테이블 생성 중...")
            db.create_tables()
            
            # 2. 샘플 점수 데이터 삽입
            print("💾 샘플 점수 데이터 삽입 중...")
            db.bulk_insert_scores(sample_scores)
            
            # 3. 점수 데이터 조회
            print("📊 점수 데이터 조회 중...")
            scores_data = db.get_scores_data()
            print(f"조회된 점수 데이터: {len(scores_data)}개")
            
            # 4. 추천 결과 저장
            print("💾 추천 결과 저장 중...")
            db.save_recommendation(
                session_id="test_session_001",
                user_scores=sample_user_scores,
                recommendations=sample_recommendation,
                model_version="v20250816_test"
            )
            
            # 5. 추천 이력 조회
            print("📊 추천 이력 조회 중...")
            history = db.get_recommendations_history(limit=5)
            print(f"추천 이력: {len(history)}개")
            
            # 6. 통계 정보 조회
            print("📈 통계 정보 조회 중...")
            stats = db.get_recommendation_statistics()
            print(f"통계 정보: {stats}")
            
    except Exception as e:
        print(f"❌ 테스트 실패: {str(e)}")
        print("💡 MariaDB가 설치되어 있고 실행 중인지 확인하세요.")
        print("💡 데이터베이스 연결 정보가 올바른지 확인하세요.")
    
    print("=" * 50)
    print("✅ MariaDB 연동 모듈 테스트 완료")


if __name__ == "__main__":
    main()
