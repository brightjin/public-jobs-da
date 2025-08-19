#!/usr/bin/env python3
"""
TMP_채용공고 테이블에서 일반전형 컬럼을 ','로 분리하여 행으로 확장하는 스크립트
"""

import os
import sys
import uuid
from datetime import datetime
from database_manager import DatabaseManager
from dotenv import load_dotenv

# 환경변수 로드
load_dotenv()

def connect_to_database():
    """데이터베이스 연결"""
    try:
        print(f"📍 DB 연결 정보:")
        print(f"   - 호스트: {os.getenv('DB_HOST')}:{os.getenv('DB_PORT')}")
        print(f"   - 사용자: {os.getenv('DB_USER')}")
        print(f"   - 데이터베이스: {os.getenv('DB_NAME')}")
        
        db_manager = DatabaseManager()
        if db_manager.connect():
            print("✅ 데이터베이스 연결 성공")
            return db_manager
        else:
            print("❌ 데이터베이스 연결 실패")
            return None
            
    except Exception as e:
        print(f"❌ 데이터베이스 연결 오류: {e}")
        return None

def get_table_structure(db_manager, table_name):
    """테이블 구조 확인"""
    query = f"DESCRIBE {table_name}"
    result = db_manager.execute_query(query)
    
    if result:
        print(f"\n📋 {table_name} 테이블 구조:")
        print("-" * 50)
        for row in result:
            print(f"   {row[0]} | {row[1]} | {row[2]} | {row[3]} | {row[4]} | {row[5]}")
        return [row[0] for row in result]  # 컬럼명 리스트 반환
    else:
        print(f"❌ {table_name} 테이블 구조를 가져올 수 없습니다.")
        return None

def get_sample_data(db_manager, table_name, limit=5):
    """샘플 데이터 확인"""
    query = f"SELECT * FROM {table_name} LIMIT {limit}"
    result = db_manager.execute_query(query)
    
    if result:
        print(f"\n📊 {table_name} 샘플 데이터 (상위 {limit}개):")
        print("-" * 80)
        for i, row in enumerate(result, 1):
            print(f"  {i}. {row}")
    else:
        print(f"❌ {table_name} 샘플 데이터를 가져올 수 없습니다.")

def check_job_types_column(db_manager, table_name):
    """일반전형 컬럼의 데이터 분포 확인"""
    query = f"SELECT 일반전형, COUNT(*) as 개수 FROM {table_name} GROUP BY 일반전형 ORDER BY 개수 DESC LIMIT 10"
    result = db_manager.execute_query(query)
    
    if result:
        print(f"\n📈 일반전형 컬럼 데이터 분포 (상위 10개):")
        print("-" * 60)
        for row in result:
            job_types = row[0] if row[0] else 'NULL'
            count = row[1]
            # 콤마가 포함된 경우 분리될 개수 표시
            split_count = len(job_types.split(',')) if ',' in job_types else 1
            print(f"   '{job_types}' -> {count}개 행 (분리 후: {split_count}개씩)")
    else:
        print("❌ 일반전형 컬럼 데이터를 가져올 수 없습니다.")

def create_expanded_table(db_manager, source_table, target_table, columns):
    """확장된 테이블 생성"""
    # 기존 테이블이 있으면 삭제
    drop_query = f"DROP TABLE IF EXISTS {target_table}"
    if db_manager.execute_query(drop_query) is not None:
        print(f"✅ 기존 {target_table} 테이블 삭제 완료")
    
    # 컬럼 정의 생성 (그룹ID 컬럼 추가, id 컬럼 제외)
    column_defs = []
    for col in columns:
        if col.lower() == 'id':  # id 컬럼은 제외 (자동 생성할 예정)
            continue
        elif col == '일반전형':
            column_defs.append(f"`{col}` VARCHAR(100)")
        elif 'ID' in col.upper() or col in ['공고번호', '기관코드']:
            column_defs.append(f"`{col}` VARCHAR(50)")
        elif '날짜' in col or 'DATE' in col.upper() or col.endswith('일'):
            column_defs.append(f"`{col}` DATE")
        elif '시간' in col or 'TIME' in col.upper() or 'created_at' in col or 'updated_at' in col:
            column_defs.append(f"`{col}` TIMESTAMP")
        elif col in ['접수대행']:
            column_defs.append(f"`{col}` TEXT")
        elif '수' in col or '인원' in col or '급여' in col:
            column_defs.append(f"`{col}` VARCHAR(20)")
        elif col == '기관명':
            column_defs.append(f"`{col}` VARCHAR(50)")
        elif col == '공고명':
            column_defs.append(f"`{col}` VARCHAR(255)")
        elif col in ['접수방법', '채용방법', '전형방법', '임용시기', '담당부서', '연락처']:
            column_defs.append(f"`{col}` VARCHAR(100)")
        elif col in ['임용조건']:
            column_defs.append(f"`{col}` TEXT")
        else:
            column_defs.append(f"`{col}` TEXT")
    
    # 그룹ID 컬럼 추가
    column_defs.append("`그룹ID` VARCHAR(36)")
    
    create_query = f"""
    CREATE TABLE {target_table} (
        `id` INT AUTO_INCREMENT PRIMARY KEY,
        {', '.join(column_defs)},
        INDEX idx_group_id (`그룹ID`),
        INDEX idx_job_type (`일반전형`)
    ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci
    """
    
    if db_manager.execute_query(create_query) is not None:
        print(f"✅ {target_table} 테이블 생성 완료")
        return True
    else:
        print(f"❌ {target_table} 테이블 생성 실패")
        return False

def split_and_insert_data(db_manager, source_table, target_table, columns):
    """데이터를 분리하여 새 테이블에 삽입"""
    # id 컬럼 제외한 컬럼들만 선택
    select_columns_list = [col for col in columns if col.lower() != 'id']
    select_columns = ', '.join([f"`{col}`" for col in select_columns_list])
    query = f"SELECT {select_columns} FROM {source_table}"
    
    print(f"\n📥 {source_table}에서 데이터 로딩 중...")
    source_data = db_manager.execute_query(query)
    
    if not source_data:
        print("❌ 소스 데이터를 가져올 수 없습니다.")
        return False
    
    print(f"✅ 총 {len(source_data)}개 행 로딩 완료")
    
    # 데이터 분리 및 삽입
    total_inserted = 0
    failed_count = 0
    
    # 삽입용 컬럼 (그룹ID 포함, id 제외)
    insert_columns = select_columns_list + ['그룹ID']
    placeholders = ', '.join(['%s'] * len(insert_columns))
    insert_query = f"INSERT INTO {target_table} ({', '.join([f'`{col}`' for col in insert_columns])}) VALUES ({placeholders})"
    
    print(f"\n🔄 데이터 분리 및 삽입 중...")
    
    for row_idx, row in enumerate(source_data, 1):
        try:
            # 그룹ID 생성 (동일한 원본 행에서 분리된 것들은 같은 ID)
            group_id = str(uuid.uuid4())
            
            # 일반전형 컬럼 찾기
            job_types_idx = select_columns_list.index('일반전형')
            job_types_value = row[job_types_idx] if row[job_types_idx] else ''
            
            # 콤마로 분리
            if ',' in job_types_value:
                job_type_list = [jt.strip() for jt in job_types_value.split(',') if jt.strip()]
            else:
                job_type_list = [job_types_value.strip()] if job_types_value.strip() else ['']
            
            # 각 일반전형에 대해 행 생성
            for job_type in job_type_list:
                try:
                    new_row = list(row)
                    new_row[job_types_idx] = job_type  # 분리된 일반전형으로 교체
                    new_row.append(group_id)  # 그룹ID 추가
                    
                    # 개별 삽입
                    db_manager.execute_query(insert_query, new_row, fetch=False)
                    total_inserted += 1
                    
                except Exception as insert_error:
                    print(f"   ❌ 개별 삽입 실패 (행 {row_idx}, 전형: {job_type}): {insert_error}")
                    failed_count += 1
            
            if row_idx % 50 == 0:
                print(f"   🔄 {row_idx}/{len(source_data)} 행 처리 완료... (분리된 행: {total_inserted})")
                
        except Exception as e:
            print(f"   ❌ 행 {row_idx} 처리 오류: {e}")
            failed_count += 1
            continue
    
    print(f"\n📊 데이터 분리 및 삽입 완료:")
    print(f"   - 원본 행 수: {len(source_data)}")
    print(f"   - 분리된 행 수: {total_inserted}")
    print(f"   - 실패 수: {failed_count}")
    print(f"   - 확장 비율: {total_inserted / len(source_data):.1f}배")
    
    return total_inserted > 0

def verify_result(db_manager, target_table):
    """결과 검증"""
    print(f"\n🔍 {target_table} 결과 검증:")
    
    # 총 행 수
    count_query = f"SELECT COUNT(*) FROM {target_table}"
    result = db_manager.execute_query(count_query)
    if result:
        total_rows = result[0][0]
        print(f"   📊 총 행 수: {total_rows:,}")
    
    # 그룹별 행 수 분포
    group_query = f"SELECT 그룹ID, COUNT(*) as 행수 FROM {target_table} GROUP BY 그룹ID ORDER BY 행수 DESC LIMIT 10"
    result = db_manager.execute_query(group_query)
    if result:
        print(f"   📈 그룹별 분리 현황 (상위 10개):")
        for row in result:
            print(f"      그룹 {row[0][:8]}... : {row[1]}개 행")
    
    # 일반전형별 분포
    job_type_query = f"SELECT 일반전형, COUNT(*) as 개수 FROM {target_table} GROUP BY 일반전형 ORDER BY 개수 DESC LIMIT 10"
    result = db_manager.execute_query(job_type_query)
    if result:
        print(f"   📋 일반전형별 분포 (상위 10개):")
        for row in result:
            print(f"      {row[0]}: {row[1]:,}개")
    
    # 샘플 데이터
    sample_query = f"SELECT * FROM {target_table} LIMIT 5"
    result = db_manager.execute_query(sample_query)
    if result:
        print(f"   📝 샘플 데이터:")
        for i, row in enumerate(result, 1):
            print(f"      {i}. 그룹ID: {str(row[-2])[:8]}..., 일반전형: '{row[2] if len(row) > 2 else 'N/A'}'")

def main():
    """메인 함수"""
    print("🚀 TMP_채용공고 테이블 일반전형 컬럼 분리 스크립트")
    print("=" * 60)
    print(f"⏰ 시작 시간: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    # 데이터베이스 연결
    db_manager = connect_to_database()
    if not db_manager:
        return
    
    source_table = 'TMP_채용공고'
    target_table = 'TMP_채용공고_분리'
    
    try:
        # 1. 소스 테이블 구조 확인
        print(f"\n📋 1단계: {source_table} 테이블 분석")
        columns = get_table_structure(db_manager, source_table)
        if not columns:
            print(f"❌ {source_table} 테이블이 존재하지 않거나 접근할 수 없습니다.")
            return
        
        # 일반전형 컬럼 존재 확인
        if '일반전형' not in columns:
            print("❌ '일반전형' 컬럼이 존재하지 않습니다.")
            return
        
        # 2. 샘플 데이터 및 분포 확인
        get_sample_data(db_manager, source_table)
        check_job_types_column(db_manager, source_table)
        
        # 3. 사용자 확인
        print(f"\n❓ {source_table} 테이블의 데이터를 일반전형 컬럼 기준으로 분리하여")
        print(f"   {target_table} 테이블에 저장하시겠습니까?")
        
        user_input = input("   계속하려면 'y' 또는 'yes'를 입력하세요: ").strip().lower()
        if user_input not in ['y', 'yes']:
            print("⏹️ 작업이 취소되었습니다.")
            return
        
        # 4. 타겟 테이블 생성
        print(f"\n🔧 2단계: {target_table} 테이블 생성")
        if not create_expanded_table(db_manager, source_table, target_table, columns):
            return
        
        # 5. 데이터 분리 및 삽입
        print(f"\n📤 3단계: 데이터 분리 및 삽입")
        if not split_and_insert_data(db_manager, source_table, target_table, columns):
            return
        
        # 6. 결과 검증
        print(f"\n✅ 4단계: 결과 검증")
        verify_result(db_manager, target_table)
        
        print(f"\n🎉 작업 완료!")
        print(f"⏰ 완료 시간: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"📋 결과 테이블: {target_table}")
        
    except Exception as e:
        print(f"\n❌ 예상치 못한 오류: {e}")
        import traceback
        traceback.print_exc()
    
    finally:
        # 데이터베이스 연결 종료
        if db_manager:
            db_manager.disconnect()
            print("🔌 데이터베이스 연결 종료")

if __name__ == "__main__":
    main()
