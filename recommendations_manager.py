"""
추천 결과 관리 모듈
recommendations 테이블 관련 CRUD 작업 및 데이터 처리
"""

import json
from datetime import datetime
from typing import List, Dict, Any, Optional
from database_manager import DatabaseManager
from log_config import get_logger

# 로깅 설정
logger = get_logger(__name__, 'recommendations_manager.log')

class RecommendationsManager:
    """추천 결과 관리 클래스"""
    
    def __init__(self, database='dive_recruit'):
        """
        추천 결과 관리자 초기화
        
        Args:
            database: 데이터베이스 이름
        """
        self.db = DatabaseManager(database=database)
    
    def create_recommendations_table(self):
        """추천 결과 저장 테이블 생성"""
        try:
            if not self.db.connect():
                return False
                
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
            
            self.db.execute_query(recommendations_table_sql, fetch=False)
            logger.info("✅ recommendations 테이블 생성 완료")
            return True
            
        except Exception as e:
            logger.error(f"❌ recommendations 테이블 생성 실패: {str(e)}")
            return False
        finally:
            self.db.disconnect()
    
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
            if not self.db.connect():
                return False
                
            sql = """
            INSERT INTO recommendations (
                session_id, user_scores, recommendations, profile_analysis, model_version
            ) VALUES (
                %s, %s, %s, %s, %s
            )
            """
            self.db.execute_query(sql, (
                session_id,
                json.dumps(user_scores, ensure_ascii=False),
                json.dumps(recommendations, ensure_ascii=False),
                json.dumps(profile_analysis, ensure_ascii=False) if profile_analysis else None,
                model_version
            ), fetch=False)
            
            logger.info(f"✅ 추천 결과 저장 완료: 세션 {session_id}")
            return True
            
        except Exception as e:
            logger.error(f"❌ 추천 결과 저장 실패: {str(e)}")
            return False
        finally:
            self.db.disconnect()
    
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
            if not self.db.connect():
                return []
                
            if session_id:
                sql = """
                SELECT * FROM recommendations 
                WHERE session_id = %s 
                ORDER BY created_at DESC 
                LIMIT %s
                """
                results = self.db.execute_query_dict(sql, (session_id, limit))
            else:
                sql = """
                SELECT * FROM recommendations 
                ORDER BY created_at DESC 
                LIMIT %s
                """
                results = self.db.execute_query_dict(sql, (limit,))
            
            # JSON 필드 파싱
            if results:
                for result in results:
                    if result['user_scores']:
                        result['user_scores'] = json.loads(result['user_scores'])
                    if result['recommendations']:
                        result['recommendations'] = json.loads(result['recommendations'])
                    if result['profile_analysis']:
                        result['profile_analysis'] = json.loads(result['profile_analysis'])
            
            logger.info(f"📊 추천 이력 조회 완료: {len(results)}개 레코드")
            return results or []
            
        except Exception as e:
            logger.error(f"❌ 추천 이력 조회 실패: {str(e)}")
            return []
        finally:
            self.db.disconnect()
    
    def get_recommendation_statistics(self) -> Dict[str, Any]:
        """
        추천 통계 정보 조회
        
        Returns:
            통계 정보 딕셔너리
        """
        try:
            if not self.db.connect():
                return {}
                
            # 전체 추천 횟수
            result = self.db.execute_query("SELECT COUNT(*) as total_recommendations FROM recommendations")
            total_count = result[0][0] if result else 0
            
            # 오늘 추천 횟수
            result = self.db.execute_query("""
                SELECT COUNT(*) as today_recommendations 
                FROM recommendations 
                WHERE DATE(created_at) = CURDATE()
            """)
            today_count = result[0][0] if result else 0
            
            # 최다 추천된 전형 TOP 5
            top_forms_result = self.db.execute_query_dict("""
                SELECT 
                    JSON_EXTRACT(recommendations, '$[0].전형명') as 전형명,
                    COUNT(*) as 추천횟수
                FROM recommendations 
                WHERE JSON_EXTRACT(recommendations, '$[0].전형명') IS NOT NULL
                GROUP BY JSON_EXTRACT(recommendations, '$[0].전형명')
                ORDER BY COUNT(*) DESC 
                LIMIT 5
            """)
            
            stats = {
                "전체_추천_횟수": total_count,
                "오늘_추천_횟수": today_count,
                "최다_추천_전형": top_forms_result or [],
                "조회_시각": datetime.now().isoformat()
            }
            
            logger.info("📊 추천 통계 조회 완료")
            return stats
            
        except Exception as e:
            logger.error(f"❌ 추천 통계 조회 실패: {str(e)}")
            return {}
        finally:
            self.db.disconnect()
    
    def get_user_recommendation_history(self, session_id: str) -> List[Dict]:
        """
        특정 사용자의 추천 이력 조회
        
        Args:
            session_id: 세션 ID
            
        Returns:
            해당 사용자의 추천 이력
        """
        return self.get_recommendations_history(session_id=session_id)
    
    def delete_old_recommendations(self, days: int = 30) -> int:
        """
        오래된 추천 결과 삭제
        
        Args:
            days: 보관 기간 (일)
            
        Returns:
            삭제된 레코드 수
        """
        try:
            if not self.db.connect():
                return 0
                
            # 삭제 전 카운트 조회
            count_sql = """
            SELECT COUNT(*) FROM recommendations 
            WHERE created_at < DATE_SUB(NOW(), INTERVAL %s DAY)
            """
            result = self.db.execute_query(count_sql, (days,))
            delete_count = result[0][0] if result else 0
            
            if delete_count > 0:
                # 실제 삭제
                delete_sql = """
                DELETE FROM recommendations 
                WHERE created_at < DATE_SUB(NOW(), INTERVAL %s DAY)
                """
                self.db.execute_query(delete_sql, (days,), fetch=False)
                logger.info(f"🗑️ 오래된 추천 결과 삭제 완료: {delete_count}개 ({days}일 이전)")
            else:
                logger.info(f"🔍 삭제할 오래된 추천 결과 없음 ({days}일 이전)")
            
            return delete_count
            
        except Exception as e:
            logger.error(f"❌ 오래된 추천 결과 삭제 실패: {str(e)}")
            return 0
        finally:
            self.db.disconnect()

def main():
    """추천 관리자 테스트"""
    print("🧪 RecommendationsManager 테스트 시작")
    
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
    
    sample_profile = {
        "강점": ["기술전문성", "학습속도", "인지문제해결"],
        "약점": ["대인민첩성", "외향성"],
        "추천사유": "기술 중심의 역량이 뛰어남"
    }
    
    try:
        rec_mgr = RecommendationsManager(database='sangsang')
        
        # 1. 테이블 생성
        print("📋 테이블 생성...")
        rec_mgr.create_recommendations_table()
        
        # 2. 추천 결과 저장
        print("💾 추천 결과 저장...")
        success = rec_mgr.save_recommendation(
            session_id="test_session_001",
            user_scores=sample_user_scores,
            recommendations=sample_recommendation,
            profile_analysis=sample_profile,
            model_version="v20250819_test"
        )
        print(f"저장 성공: {success}")
        
        # 3. 이력 조회
        print("📊 추천 이력 조회...")
        history = rec_mgr.get_recommendations_history(limit=5)
        print(f"조회된 이력: {len(history)}개")
        
        # 4. 통계 조회
        print("📈 통계 조회...")
        stats = rec_mgr.get_recommendation_statistics()
        print(f"통계: {stats}")
        
    except Exception as e:
        print(f"❌ 테스트 실패: {e}")

if __name__ == "__main__":
    main()
