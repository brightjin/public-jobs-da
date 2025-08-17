"""
CSV 파일별 MariaDB 테이블 생성 스크립트
./data 디렉토리의 모든 CSV 파일을 분석하여 자동으로 테이블 생성 및 데이터 삽입
"""

import os
import sys
import pandas as pd
import pymysql
import numpy as np
from datetime import datetime
import re

# 상위 디렉토리의 database_manager 모듈 import
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from database_manager import DatabaseManager

def clean_column_name(col_name):
    """컬럼명을 MySQL 호환 형식으로 정리"""
    # 공백과 특수문자를 언더스코어로 변경
    cleaned = re.sub(r'[^\w가-힣]', '_', str(col_name).strip())
    # 연속된 언더스코어 제거
    cleaned = re.sub(r'_+', '_', cleaned)
    # 시작/끝 언더스코어 제거
    cleaned = cleaned.strip('_')
    # 빈 문자열이면 기본값 사용
    if not cleaned:
        cleaned = 'column_name'
    # 숫자로 시작하면 접두사 추가
    if cleaned[0].isdigit():
        cleaned = 'col_' + cleaned
    return cleaned

def infer_mysql_type(series, col_name):
    """pandas Series를 분석하여 적절한 MySQL 데이터 타입 추론"""
    # NULL 값 제거
    non_null_series = series.dropna()
    
    if len(non_null_series) == 0:
        return "TEXT"
    
    # 날짜 타입 확인
    if any(keyword in col_name.lower() for keyword in ['날짜', 'date', '시작일', '마감일', '연도']):
        if col_name == '연도':
            return "YEAR"
        return "DATE"
    
    # 숫자 타입 확인
    if pd.api.types.is_numeric_dtype(series):
        if pd.api.types.is_integer_dtype(series):
            max_val = non_null_series.max()
            min_val = non_null_series.min()
            
            if min_val >= 0 and max_val <= 255:
                return "TINYINT UNSIGNED"
            elif min_val >= -128 and max_val <= 127:
                return "TINYINT"
            elif min_val >= 0 and max_val <= 65535:
                return "SMALLINT UNSIGNED"
            elif min_val >= -32768 and max_val <= 32767:
                return "SMALLINT"
            elif min_val >= 0 and max_val <= 4294967295:
                return "INT UNSIGNED"
            elif min_val >= -2147483648 and max_val <= 2147483647:
                return "INT"
            else:
                return "BIGINT"
        else:
            # 부동소수점
            return "DECIMAL(10,2)"
    
    # 문자열 타입
    if pd.api.types.is_object_dtype(series):
        max_length = non_null_series.astype(str).str.len().max()
        
        if max_length <= 50:
            return f"VARCHAR({min(255, max_length * 2)})"
        elif max_length <= 255:
            return "VARCHAR(255)"
        elif max_length <= 65535:
            return "TEXT"
        else:
            return "LONGTEXT"
    
    # 기본값
    return "TEXT"

def create_table_sql(df, table_name):
    """DataFrame을 기반으로 CREATE TABLE SQL 생성"""
    columns = []
    
    # ID 컬럼 추가
    columns.append("id INT AUTO_INCREMENT PRIMARY KEY")
    
    for col in df.columns:
        cleaned_col = clean_column_name(col)
        mysql_type = infer_mysql_type(df[col], col)
        
        # NOT NULL 여부 결정
        null_ratio = df[col].isnull().sum() / len(df)
        not_null = "NOT NULL" if null_ratio < 0.1 else ""
        
        # 기본값 설정
        default_val = ""
        if mysql_type.startswith("VARCHAR") or mysql_type in ["TEXT", "LONGTEXT"]:
            if not_null:
                default_val = "DEFAULT ''"
        elif mysql_type in ["DATE"]:
            default_val = "DEFAULT NULL"
        
        columns.append(f"`{cleaned_col}` {mysql_type} {not_null} {default_val}".strip())
    
    # 생성/수정 시간 컬럼 추가
    columns.append("created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP")
    columns.append("updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP")
    
    separator = ',\n        '
    columns_str = separator.join(columns)
    
    sql = f"""
    CREATE TABLE IF NOT EXISTS `{table_name}` (
        {columns_str}
    ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci
    """
    
    return sql

def clean_data_for_insert(df):
    """데이터 삽입을 위한 DataFrame 정리"""
    df_cleaned = df.copy()
    
    # 컬럼명 정리
    df_cleaned.columns = [clean_column_name(col) for col in df_cleaned.columns]
    
    # 날짜 컬럼 변환
    for col in df_cleaned.columns:
        if any(keyword in col.lower() for keyword in ['날짜', 'date', '시작일', '마감일']):
            df_cleaned[col] = pd.to_datetime(df_cleaned[col], errors='coerce', infer_datetime_format=True)
            df_cleaned[col] = df_cleaned[col].dt.strftime('%Y-%m-%d')
    
    # NaN을 None으로 변경 (MySQL NULL)
    df_cleaned = df_cleaned.where(pd.notnull(df_cleaned), None)
    
    return df_cleaned

def process_csv_file(file_path, db_manager):
    """개별 CSV 파일 처리"""
    try:
        print(f"\n📁 처리 중: {os.path.basename(file_path)}")
        
        # CSV 파일 읽기 (인코딩 자동 감지)
        try:
            df = pd.read_csv(file_path, encoding='utf-8')
        except UnicodeDecodeError:
            try:
                df = pd.read_csv(file_path, encoding='cp949')
            except UnicodeDecodeError:
                df = pd.read_csv(file_path, encoding='euc-kr')
        
        # 빈 행 제거
        df = df.dropna(how='all')
        
        # 헤더가 없는 경우 확인 (첫 번째 행이 데이터인지 확인)
        if df.iloc[0].astype(str).str.contains('채용정보|현황|기관명').any():
            # 첫 번째 행이 타이틀이면 제거하고 두 번째 행을 헤더로 사용
            if len(df) > 1:
                df.columns = df.iloc[1]
                df = df.iloc[2:].reset_index(drop=True)
            else:
                df = df.iloc[1:].reset_index(drop=True)
        
        # 빈 컬럼 제거
        df = df.loc[:, ~df.columns.str.contains('^Unnamed')]
        df = df.dropna(axis=1, how='all')
        
        if df.empty:
            print(f"⚠️ {os.path.basename(file_path)}: 유효한 데이터가 없습니다.")
            return False
        
        print(f"📊 크기: {df.shape[0]}행 x {df.shape[1]}열")
        print(f"📋 컬럼: {list(df.columns)[:5]}..." if len(df.columns) > 5 else f"📋 컬럼: {list(df.columns)}")
        
        # 테이블명 생성 (파일명에서 확장자 제거)
        table_name = os.path.splitext(os.path.basename(file_path))[0]
        
        # 테이블 생성
        create_sql = create_table_sql(df, table_name)
        print(f"🏗️ 테이블 생성 중: {table_name}")
        
        with db_manager.connection.cursor() as cursor:
            cursor.execute(create_sql)
        
        # 데이터 정리 및 삽입
        df_cleaned = clean_data_for_insert(df)
        
        # 기존 데이터 삭제 (재실행 시)
        with db_manager.connection.cursor() as cursor:
            cursor.execute(f"DELETE FROM `{table_name}`")
        
        # 데이터 삽입
        print(f"💾 데이터 삽입 중...")
        
        columns = [f"`{col}`" for col in df_cleaned.columns]
        placeholders = ['%s'] * len(columns)
        
        insert_sql = f"""
            INSERT INTO `{table_name}` ({', '.join(columns)})
            VALUES ({', '.join(placeholders)})
        """
        
        with db_manager.connection.cursor() as cursor:
            for _, row in df_cleaned.iterrows():
                try:
                    cursor.execute(insert_sql, tuple(row))
                except Exception as e:
                    print(f"⚠️ 행 삽입 실패: {e}")
                    continue
        
        print(f"✅ {table_name} 테이블 생성 완료: {len(df_cleaned)}개 레코드")
        return True
        
    except Exception as e:
        print(f"❌ {os.path.basename(file_path)} 처리 실패: {e}")
        return False

def main():
    """메인 함수"""
    print("🗄️ CSV 파일별 MariaDB 테이블 생성 스크립트")
    print("=" * 60)
    
    # 현재 스크립트의 디렉토리 확인
    script_dir = os.path.dirname(os.path.abspath(__file__))
    data_dir = script_dir  # 스크립트가 ./data 디렉토리에 있음
    
    print(f"📁 데이터 디렉토리: {data_dir}")
    
    # CSV 파일 목록 확인
    csv_files = [f for f in os.listdir(data_dir) if f.endswith('.csv')]
    
    if not csv_files:
        print("❌ CSV 파일을 찾을 수 없습니다.")
        return
    
    print(f"📄 발견된 CSV 파일: {len(csv_files)}개")
    for f in csv_files:
        print(f"  - {f}")
    
    # 환경변수에서 DB 설정 읽기
    db_config = {
        'host': os.getenv('DB_HOST', 'localhost'),
        'port': int(os.getenv('DB_PORT', 3306)),
        'user': os.getenv('DB_USER', 'root'),
        'password': os.getenv('DB_PASSWORD', ''),
        'database': os.getenv('DB_NAME', 'dive_recruit')
    }
    
    print(f"\n🔗 데이터베이스 연결 정보:")
    print(f"  호스트: {db_config['host']}:{db_config['port']}")
    print(f"  데이터베이스: {db_config['database']}")
    print(f"  사용자: {db_config['user']}")
    
    # 사용자 확인
    print("\n" + "=" * 60)
    while True:
        choice = input(f"📥 {len(csv_files)}개 CSV 파일로 테이블을 생성하시겠습니까? (y/N): ").strip().lower()
        if choice in ['y', 'yes']:
            break
        elif choice in ['n', 'no', '']:
            print("취소되었습니다.")
            return
        else:
            print("y 또는 n을 입력하세요.")
    
    # 데이터베이스 연결 및 처리
    try:
        with DatabaseManager(**db_config) as db_manager:
            print(f"\n✅ 데이터베이스 연결 성공")
            
            success_count = 0
            total_count = len(csv_files)
            
            for csv_file in csv_files:
                file_path = os.path.join(data_dir, csv_file)
                if process_csv_file(file_path, db_manager):
                    success_count += 1
            
            print(f"\n" + "=" * 60)
            print(f"🎉 처리 완료!")
            print(f"📊 성공: {success_count}/{total_count} 파일")
            
            if success_count > 0:
                print(f"\n💡 생성된 테이블 확인:")
                print(f"  mysql -h {db_config['host']} -u {db_config['user']} -p {db_config['database']}")
                print(f"  SHOW TABLES;")
                
                # 테이블 목록 출력
                with db_manager.connection.cursor() as cursor:
                    cursor.execute("SHOW TABLES")
                    tables = cursor.fetchall()
                    print(f"\n📋 생성된 테이블 목록:")
                    for table in tables:
                        cursor.execute(f"SELECT COUNT(*) FROM `{table[0]}`")
                        count = cursor.fetchone()[0]
                        print(f"  - {table[0]}: {count}개 레코드")
                        
    except Exception as e:
        print(f"❌ 데이터베이스 연결 실패: {e}")
        print(f"\n💡 해결 방법:")
        print(f"1. MariaDB가 실행 중인지 확인")
        print(f"2. 환경변수 설정 확인 (.env 파일)")
        print(f"3. 데이터베이스가 생성되어 있는지 확인")
        print(f"4. 사용자 권한 확인")

if __name__ == "__main__":
    main()
