"""
점수 데이터 관리 모듈
scores 테이블 관련 CRUD 작업 및 데이터 처리
"""

import pandas as pd
import json
from typing import List, Dict, Any
from database_manager import DatabaseManager
from log_config import get_logger

# 로깅 설정
logger = get_logger(__name__, 'scores_manager.log')

class ScoresManager:
    """점수 데이터 관리 클래스"""
    
    def __init__(self, database='dive_recruit'):
        """
        점수 데이터 관리자 초기화
        
        Args:
            database: 데이터베이스 이름
        """
        self.db = DatabaseManager(database=database)
        self.score_columns = [
            '성실성', '개방성', '외향성', '우호성', '정서안정성', '기술전문성',
            '인지문제해결', '대인-영향력', '자기관리', '적응력', '학습속도',
            '대인민첩성', '성과민첩성', '자기인식', '자기조절', '공감-사회기술'
        ]
    
    def create_scores_table(self):
        """점수 데이터 테이블 생성"""
        try:
            if not self.db.connect():
                return False
                
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
            
            self.db.execute_query(scores_table_sql, fetch=False)
            logger.info("✅ scores 테이블 생성 완료")
            return True
            
        except Exception as e:
            logger.error(f"❌ scores 테이블 생성 실패: {str(e)}")
            return False
        finally:
            self.db.disconnect()
    
    def get_scores_data(self) -> List[Dict[str, Any]]:
        """
        점수 데이터를 조회하여 API 형식으로 반환
        
        Returns:
            점수 데이터 리스트
        """
        try:
            if not self.db.connect():
                return []
                
            sql = """
            SELECT 기관명, 일반전형, 성실성, 개방성, 외향성, 우호성, 정서안정성,
                   기술전문성, 인지문제해결, `대인-영향력`, 자기관리, 적응력,
                   학습속도, 대인민첩성, 성과민첩성, 자기인식, 자기조절, `공감-사회기술`
            FROM scores
            ORDER BY 기관명, 일반전형
            """
            results = self.db.execute_query_dict(sql)
            
            logger.info(f"📊 점수 데이터 조회 완료: {len(results)}개 레코드")
            return results or []
            
        except Exception as e:
            logger.error(f"❌ 점수 데이터 조회 실패: {str(e)}")
            return []
        finally:
            self.db.disconnect()
    
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
            if not self.db.connect():
                return False
                
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
            self.db.execute_query(sql, data, fetch=False)
            logger.info(f"✅ 점수 데이터 저장 완료: {data['기관명']} - {data['일반전형']}")
            return True
            
        except Exception as e:
            logger.error(f"❌ 점수 데이터 저장 실패: {str(e)}")
            return False
        finally:
            self.db.disconnect()
    
    def bulk_insert_scores(self, scores_list: List[Dict[str, Any]]) -> int:
        """
        점수 데이터 대량 삽입
        
        Args:
            scores_list: 점수 데이터 리스트
            
        Returns:
            성공한 레코드 수
        """
        success_count = 0
        
        try:
            if not self.db.connect():
                return 0
                
            for score_data in scores_list:
                try:
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
                    self.db.execute_query(sql, score_data, fetch=False)
                    success_count += 1
                except Exception as e:
                    logger.warning(f"⚠️ 개별 점수 데이터 삽입 실패: {score_data.get('기관명', 'Unknown')} - {e}")
            
            logger.info(f"🔄 대량 점수 데이터 저장 완료: {success_count}/{len(scores_list)}개")
            
        except Exception as e:
            logger.error(f"❌ 대량 점수 데이터 저장 실패: {str(e)}")
        finally:
            self.db.disconnect()
            
        return success_count
    
    def get_scores_by_organization(self, 기관명: str) -> List[Dict[str, Any]]:
        """
        특정 기관의 점수 데이터 조회
        
        Args:
            기관명: 조회할 기관명
            
        Returns:
            해당 기관의 점수 데이터 리스트
        """
        try:
            if not self.db.connect():
                return []
                
            sql = """
            SELECT 기관명, 일반전형, 성실성, 개방성, 외향성, 우호성, 정서안정성,
                   기술전문성, 인지문제해결, `대인-영향력`, 자기관리, 적응력,
                   학습속도, 대인민첩성, 성과민첩성, 자기인식, 자기조절, `공감-사회기술`
            FROM scores
            WHERE 기관명 = %s
            ORDER BY 일반전형
            """
            results = self.db.execute_query_dict(sql, (기관명,))
            
            logger.info(f"📊 기관별 점수 데이터 조회 완료: {기관명} - {len(results)}개 레코드")
            return results or []
            
        except Exception as e:
            logger.error(f"❌ 기관별 점수 데이터 조회 실패: {str(e)}")
            return []
        finally:
            self.db.disconnect()

def main():
    """점수 관리자 테스트"""
    print("🧪 ScoresManager 테스트 시작")
    
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
    
    try:
        scores_mgr = ScoresManager(database='sangsang')
        
        # 1. 테이블 생성
        print("📋 테이블 생성...")
        scores_mgr.create_scores_table()
        
        # 2. 샘플 데이터 삽입
        print("💾 샘플 데이터 삽입...")
        success_count = scores_mgr.bulk_insert_scores(sample_scores)
        print(f"삽입 완료: {success_count}개")
        
        # 3. 데이터 조회
        print("📊 데이터 조회...")
        data = scores_mgr.get_scores_data()
        print(f"조회된 데이터: {len(data)}개")
        
        # 4. DataFrame 변환
        print("📊 DataFrame 변환...")
        df = scores_mgr.get_scores_dataframe()
        print(f"DataFrame shape: {df.shape}")
        
    except Exception as e:
        print(f"❌ 테스트 실패: {e}")

if __name__ == "__main__":
    main()
