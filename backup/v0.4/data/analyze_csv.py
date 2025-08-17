"""
CSV 파일 분석 및 테이블 스키마 미리보기
실제 테이블 생성 전에 어떤 구조로 생성될지 미리 확인
"""

import os
import pandas as pd
import re
from datetime import datetime

def clean_column_name(col_name):
    """컬럼명을 MySQL 호환 형식으로 정리"""
    cleaned = re.sub(r'[^\w가-힣]', '_', str(col_name).strip())
    cleaned = re.sub(r'_+', '_', cleaned)
    cleaned = cleaned.strip('_')
    if not cleaned:
        cleaned = 'column_name'
    if cleaned[0].isdigit():
        cleaned = 'col_' + cleaned
    return cleaned

def infer_mysql_type(series, col_name):
    """pandas Series를 분석하여 적절한 MySQL 데이터 타입 추론"""
    non_null_series = series.dropna()
    
    if len(non_null_series) == 0:
        return "TEXT", "모든 값이 NULL"
    
    # 날짜 타입 확인
    if any(keyword in col_name.lower() for keyword in ['날짜', 'date', '시작일', '마감일', '연도']):
        if col_name == '연도':
            return "YEAR", "연도 필드"
        return "DATE", "날짜 필드"
    
    # 숫자 타입 확인
    if pd.api.types.is_numeric_dtype(series):
        if pd.api.types.is_integer_dtype(series):
            max_val = non_null_series.max()
            min_val = non_null_series.min()
            
            if min_val >= 0 and max_val <= 255:
                return "TINYINT UNSIGNED", f"범위: {min_val}-{max_val}"
            elif min_val >= -128 and max_val <= 127:
                return "TINYINT", f"범위: {min_val}-{max_val}"
            elif min_val >= 0 and max_val <= 65535:
                return "SMALLINT UNSIGNED", f"범위: {min_val}-{max_val}"
            elif min_val >= -32768 and max_val <= 32767:
                return "SMALLINT", f"범위: {min_val}-{max_val}"
            elif min_val >= 0 and max_val <= 4294967295:
                return "INT UNSIGNED", f"범위: {min_val}-{max_val}"
            elif min_val >= -2147483648 and max_val <= 2147483647:
                return "INT", f"범위: {min_val}-{max_val}"
            else:
                return "BIGINT", f"범위: {min_val}-{max_val}"
        else:
            return "DECIMAL(10,2)", f"부동소수점 범위: {non_null_series.min():.2f}-{non_null_series.max():.2f}"
    
    # 문자열 타입
    if pd.api.types.is_object_dtype(series):
        max_length = non_null_series.astype(str).str.len().max()
        avg_length = non_null_series.astype(str).str.len().mean()
        
        if max_length <= 50:
            return f"VARCHAR({min(255, max_length * 2)})", f"평균 길이: {avg_length:.1f}, 최대: {max_length}"
        elif max_length <= 255:
            return "VARCHAR(255)", f"평균 길이: {avg_length:.1f}, 최대: {max_length}"
        elif max_length <= 65535:
            return "TEXT", f"평균 길이: {avg_length:.1f}, 최대: {max_length}"
        else:
            return "LONGTEXT", f"평균 길이: {avg_length:.1f}, 최대: {max_length}"
    
    return "TEXT", "기본 텍스트 타입"

def analyze_csv_file(file_path):
    """CSV 파일 분석"""
    try:
        print(f"\n📁 파일 분석: {os.path.basename(file_path)}")
        print("=" * 80)
        
        # CSV 파일 읽기 (인코딩 자동 감지)
        try:
            df = pd.read_csv(file_path, encoding='utf-8')
        except UnicodeDecodeError:
            try:
                df = pd.read_csv(file_path, encoding='cp949')
            except UnicodeDecodeError:
                df = pd.read_csv(file_path, encoding='euc-kr')
        
        print(f"📊 원본 크기: {df.shape[0]}행 x {df.shape[1]}열")
        
        # 빈 행 제거
        df = df.dropna(how='all')
        
        # 헤더가 없는 경우 확인 (첫 번째 행이 데이터인지 확인)
        if df.iloc[0].astype(str).str.contains('채용정보|현황|기관명').any():
            if len(df) > 1:
                print("🔧 첫 번째 행을 제목으로, 두 번째 행을 헤더로 처리")
                df.columns = df.iloc[1]
                df = df.iloc[2:].reset_index(drop=True)
            else:
                df = df.iloc[1:].reset_index(drop=True)
        
        # 빈 컬럼 제거
        df = df.loc[:, ~df.columns.str.contains('^Unnamed')]
        df = df.dropna(axis=1, how='all')
        
        if df.empty:
            print("⚠️ 유효한 데이터가 없습니다.")
            return None
        
        print(f"📊 정리된 크기: {df.shape[0]}행 x {df.shape[1]}열")
        
        # 테이블명 생성
        table_name = os.path.splitext(os.path.basename(file_path))[0]
        
        print(f"\n🏗️ 생성될 테이블명: {table_name}")
        print(f"\n📋 컬럼 분석:")
        print("-" * 120)
        print(f"{'원본 컬럼명':<25} {'정리된 컬럼명':<25} {'MySQL 타입':<20} {'NULL비율':<10} {'상세정보':<30}")
        print("-" * 120)
        
        schema_info = []
        
        for col in df.columns:
            cleaned_col = clean_column_name(col)
            mysql_type, detail = infer_mysql_type(df[col], col)
            null_ratio = df[col].isnull().sum() / len(df) * 100
            
            schema_info.append({
                'original': col,
                'cleaned': cleaned_col,
                'type': mysql_type,
                'null_ratio': null_ratio,
                'detail': detail
            })
            
            print(f"{col:<25} {cleaned_col:<25} {mysql_type:<20} {null_ratio:>6.1f}% {detail:<30}")
        
        # 샘플 데이터 표시
        print(f"\n📄 샘플 데이터 (상위 5행):")
        print("-" * 120)
        sample_df = df.head(5)
        print(sample_df.to_string(index=False, max_colwidth=15))
        
        # 데이터 품질 분석
        print(f"\n📈 데이터 품질 분석:")
        print("-" * 50)
        
        # 전체 NULL 비율
        total_nulls = df.isnull().sum().sum()
        total_cells = df.shape[0] * df.shape[1]
        null_percentage = total_nulls / total_cells * 100
        
        print(f"전체 NULL 비율: {null_percentage:.1f}%")
        print(f"중복 행 수: {df.duplicated().sum()}")
        
        # 각 컬럼별 고유값 수
        print(f"\n컬럼별 고유값 수:")
        for col in df.columns[:10]:  # 상위 10개 컬럼만
            unique_count = df[col].nunique()
            print(f"  {col}: {unique_count}개")
        
        # CREATE TABLE SQL 미리보기
        print(f"\n🛠️ 생성될 CREATE TABLE SQL:")
        print("-" * 80)
        
        columns = ["id INT AUTO_INCREMENT PRIMARY KEY"]
        
        for info in schema_info:
            null_clause = "NOT NULL" if info['null_ratio'] < 10 else ""
            default_clause = ""
            
            if info['type'].startswith("VARCHAR") or info['type'] in ["TEXT", "LONGTEXT"]:
                if null_clause:
                    default_clause = "DEFAULT ''"
            elif info['type'] == "DATE":
                default_clause = "DEFAULT NULL"
            
            column_def = f"`{info['cleaned']}` {info['type']} {null_clause} {default_clause}".strip()
            columns.append(column_def)
        
        columns.extend([
            "created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP",
            "updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP"
        ])
        
        sql = f"CREATE TABLE IF NOT EXISTS `{table_name}` (\n"
        sql += ",\n".join(f"    {col}" for col in columns)
        sql += f"\n) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;"
        
        print(sql)
        
        return {
            'table_name': table_name,
            'original_shape': df.shape,
            'schema_info': schema_info,
            'null_percentage': null_percentage,
            'duplicate_rows': df.duplicated().sum(),
            'sql': sql
        }
        
    except Exception as e:
        print(f"❌ 파일 분석 실패: {e}")
        return None

def main():
    """메인 함수"""
    print("🔍 CSV 파일 분석 및 테이블 스키마 미리보기")
    print("=" * 80)
    
    # 현재 스크립트의 디렉토리 확인
    script_dir = os.path.dirname(os.path.abspath(__file__))
    
    # CSV 파일 목록 확인
    csv_files = [f for f in os.listdir(script_dir) if f.endswith('.csv')]
    
    if not csv_files:
        print("❌ CSV 파일을 찾을 수 없습니다.")
        return
    
    print(f"📄 발견된 CSV 파일: {len(csv_files)}개")
    for i, f in enumerate(csv_files, 1):
        print(f"  {i}. {f}")
    
    # 분석 결과 저장
    analysis_results = []
    
    for csv_file in csv_files:
        file_path = os.path.join(script_dir, csv_file)
        result = analyze_csv_file(file_path)
        if result:
            analysis_results.append(result)
    
    # 전체 요약
    if analysis_results:
        print(f"\n📊 전체 분석 요약")
        print("=" * 80)
        
        total_tables = len(analysis_results)
        total_rows = sum(r['original_shape'][0] for r in analysis_results)
        total_columns = sum(r['original_shape'][1] for r in analysis_results)
        avg_null_percentage = sum(r['null_percentage'] for r in analysis_results) / total_tables
        
        print(f"생성될 테이블 수: {total_tables}개")
        print(f"총 데이터 행 수: {total_rows:,}개")
        print(f"총 컬럼 수: {total_columns}개")
        print(f"평균 NULL 비율: {avg_null_percentage:.1f}%")
        
        print(f"\n🏗️ 생성될 테이블 목록:")
        for i, result in enumerate(analysis_results, 1):
            rows, cols = result['original_shape']
            print(f"  {i:2d}. {result['table_name']:<20} ({rows:,}행 x {cols}열)")
        
        # SQL 스크립트 파일 생성 옵션
        print(f"\n💾 SQL 스크립트 파일 생성 옵션:")
        choice = input("모든 CREATE TABLE SQL을 파일로 저장하시겠습니까? (y/N): ").strip().lower()
        
        if choice in ['y', 'yes']:
            sql_file = os.path.join(script_dir, 'create_all_tables.sql')
            
            with open(sql_file, 'w', encoding='utf-8') as f:
                f.write("-- CSV 파일 기반 테이블 생성 스크립트\n")
                f.write(f"-- 생성 시각: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
                f.write(f"-- 총 {total_tables}개 테이블\n\n")
                
                f.write("USE dive_recruit;\n\n")
                
                for result in analysis_results:
                    f.write(f"-- 테이블: {result['table_name']}\n")
                    f.write(f"-- 원본 크기: {result['original_shape'][0]}행 x {result['original_shape'][1]}열\n")
                    f.write(f"{result['sql']}\n\n")
            
            print(f"✅ SQL 스크립트가 저장되었습니다: {sql_file}")
    
    print(f"\n💡 다음 단계:")
    print(f"1. 분석 결과를 확인한 후 create_tables_from_csv.py 실행")
    print(f"2. 테이블 생성 후 manage_tables.py로 데이터 확인")

if __name__ == "__main__":
    main()
