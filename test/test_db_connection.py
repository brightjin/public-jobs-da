#!/usr/bin/env python3
"""
데이터베이스 연결 테스트 스크립트
"""

import os
import pymysql
from dotenv import load_dotenv

# 환경변수 로드
load_dotenv()

def test_direct_connection():
    """직접 pymysql 연결 테스트"""
    try:
        print("🔧 직접 연결 테스트...")
        
        # 환경변수에서 읽기
        host = os.getenv('DB_HOST', 'localhost')
        port = int(os.getenv('DB_PORT', 3306))
        user = os.getenv('DB_USER', 'root')
        password = os.getenv('DB_PASSWORD', '')
        database = os.getenv('DB_NAME', 'test')
        
        print(f"📍 연결 정보:")
        print(f"   Host: {host} (type: {type(host)})")
        print(f"   Port: {port} (type: {type(port)})")
        print(f"   User: {user} (type: {type(user)})")
        print(f"   Password: {'*' * len(password) if password else 'None'}")
        print(f"   Database: {database} (type: {type(database)})")
        
        # 연결 시도
        connection = pymysql.connect(
            host=host,
            port=port,
            user=user,
            password=password,
            database=database,
            charset='utf8mb4',
            connect_timeout=10
        )
        
        print("✅ 데이터베이스 연결 성공!")
        
        # 간단한 쿼리 테스트
        with connection.cursor() as cursor:
            cursor.execute("SELECT 1 as test")
            result = cursor.fetchone()
            print(f"✅ 쿼리 테스트 성공: {result}")
        
        # 테이블 목록 확인
        with connection.cursor() as cursor:
            cursor.execute("SHOW TABLES")
            tables = cursor.fetchall()
            print(f"📋 데이터베이스 테이블 목록:")
            for table in tables:
                print(f"   - {table[0]}")
        
        connection.close()
        return True
        
    except Exception as e:
        print(f"❌ 연결 실패: {e}")
        return False

def test_database_manager():
    """DatabaseManager 클래스 테스트"""
    try:
        from database_manager import DatabaseManager
        
        print("\n🔧 DatabaseManager 클래스 테스트...")
        
        db_manager = DatabaseManager()
        if db_manager.connect():
            print("✅ DatabaseManager 연결 성공!")
            
            # TMP_채용공고 테이블 확인
            query = "SHOW TABLES LIKE 'TMP_%'"
            result = db_manager.execute_query(query)
            if result:
                print("📋 TMP 테이블 목록:")
                for table in result:
                    print(f"   - {table[0]}")
            
            db_manager.disconnect()
            return True
        else:
            print("❌ DatabaseManager 연결 실패")
            return False
            
    except Exception as e:
        print(f"❌ DatabaseManager 테스트 실패: {e}")
        return False

if __name__ == "__main__":
    print("🚀 데이터베이스 연결 테스트")
    print("=" * 50)
    
    # 환경변수 확인
    print("📋 환경변수 확인:")
    for key in ['DB_HOST', 'DB_PORT', 'DB_USER', 'DB_PASSWORD', 'DB_NAME']:
        value = os.getenv(key, 'Not Set')
        if 'PASSWORD' in key:
            value = '*' * len(value) if value != 'Not Set' else 'Not Set'
        print(f"   {key}: {value}")
    
    print("\n" + "=" * 50)
    
    # 직접 연결 테스트
    if test_direct_connection():
        print("\n" + "=" * 50)
        # DatabaseManager 테스트
        test_database_manager()
    
    print("\n🏁 테스트 완료")
