"""
MariaDB 데이터베이스 핵심 연동 모듈
공통 데이터베이스 연결 및 쿼리 실행 기능 제공
"""

import pymysql
import os
from typing import Any, Optional, Dict, List
from log_config import get_logger
from dotenv import load_dotenv

# 환경변수 로드
load_dotenv()

# 로깅 설정
logger = get_logger(__name__, 'database_manager.log')

class DatabaseManager:
    """MariaDB 데이터베이스 관리 클래스 - 핵심 기능만 포함"""
    
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
            self.connection = None
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
        if not self.connection:
            logger.error("❌ 데이터베이스 연결이 없습니다")
            return None
            
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
    
    def execute_query_dict(self, sql: str, params=None, fetch=True):
        """
        SQL 쿼리 실행 (딕셔너리 결과 반환)
        
        Args:
            sql: 실행할 SQL 쿼리
            params: 쿼리 파라미터 (dict 또는 tuple)
            fetch: 결과를 반환할지 여부
            
        Returns:
            fetch=True인 경우 딕셔너리 형태의 쿼리 결과, 그렇지 않으면 None
        """
        if not self.connection:
            logger.error("❌ 데이터베이스 연결이 없습니다")
            return None
            
        try:
            with self.connection.cursor(pymysql.cursors.DictCursor) as cursor:
                cursor.execute(sql, params)
                
                if fetch:
                    return cursor.fetchall()
                else:
                    return None
                    
        except Exception as e:
            logger.error(f"❌ 쿼리 실행 실패: {str(e)}")
            raise
    
    def begin_transaction(self):
        """트랜잭션 시작"""
        if self.connection:
            self.connection.begin()
            logger.debug("🔄 트랜잭션 시작")
    
    def commit(self):
        """트랜잭션 커밋"""
        if self.connection:
            self.connection.commit()
            logger.debug("✅ 트랜잭션 커밋")
    
    def rollback(self):
        """트랜잭션 롤백"""
        if self.connection:
            self.connection.rollback()
            logger.debug("↩️ 트랜잭션 롤백")
    
    def get_table_info(self, table_name: str) -> List[Dict[str, Any]]:
        """
        테이블 정보 조회
        
        Args:
            table_name: 테이블 이름
            
        Returns:
            테이블 구조 정보 리스트
        """
        try:
            sql = f"DESCRIBE {table_name}"
            result = self.execute_query_dict(sql)
            logger.info(f"📋 테이블 '{table_name}' 정보 조회 완료")
            return result or []
        except Exception as e:
            logger.error(f"❌ 테이블 '{table_name}' 정보 조회 실패: {str(e)}")
            return []
    
    def table_exists(self, table_name: str) -> bool:
        """
        테이블 존재 여부 확인
        
        Args:
            table_name: 테이블 이름
            
        Returns:
            테이블 존재 여부
        """
        try:
            sql = """
            SELECT COUNT(*) as count 
            FROM information_schema.tables 
            WHERE table_schema = %s AND table_name = %s
            """
            result = self.execute_query(sql, (self.database, table_name))
            exists = result[0][0] > 0 if result else False
            logger.debug(f"🔍 테이블 '{table_name}' 존재 여부: {exists}")
            return exists
        except Exception as e:
            logger.error(f"❌ 테이블 '{table_name}' 존재 여부 확인 실패: {str(e)}")
            return False
    
    def get_row_count(self, table_name: str, where_clause: str = None) -> int:
        """
        테이블 행 수 조회
        
        Args:
            table_name: 테이블 이름
            where_clause: WHERE 조건 (선택사항)
            
        Returns:
            행 수
        """
        try:
            sql = f"SELECT COUNT(*) FROM {table_name}"
            if where_clause:
                sql += f" WHERE {where_clause}"
            
            result = self.execute_query(sql)
            count = result[0][0] if result else 0
            logger.debug(f"📊 테이블 '{table_name}' 행 수: {count}")
            return count
        except Exception as e:
            logger.error(f"❌ 테이블 '{table_name}' 행 수 조회 실패: {str(e)}")
            return 0

def test_connection():
    """데이터베이스 연결 테스트"""
    print("🔌 데이터베이스 연결 테스트 시작")
    
    try:
        with DatabaseManager(database='sangsang') as db:
            print("✅ 연결 성공")
            
            # 테이블 목록 조회
            result = db.execute_query("SHOW TABLES")
            if result:
                print(f"📋 테이블 목록: {len(result)}개")
                for table in result[:5]:  # 상위 5개만 출력
                    print(f"   - {table[0]}")
            else:
                print("⚠️ 테이블이 없습니다")
                
    except Exception as e:
        print(f"❌ 연결 실패: {e}")

if __name__ == "__main__":
    test_connection()
