"""
CSV 테이블 관리 유틸리티
생성된 테이블의 구조 확인, 데이터 조회, 통계 정보 제공
"""

import os
import sys
import pymysql
import pandas as pd
from datetime import datetime

# 상위 디렉토리의 database_manager 모듈 import
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from database_manager import DatabaseManager

def show_table_structure(db_manager, table_name):
    """테이블 구조 출력"""
    try:
        with db_manager.connection.cursor(pymysql.cursors.DictCursor) as cursor:
            cursor.execute(f"DESCRIBE `{table_name}`")
            columns = cursor.fetchall()
            
            print(f"\n📊 테이블 구조: {table_name}")
            print("-" * 80)
            print(f"{'컬럼명':<25} {'타입':<20} {'NULL':<8} {'키':<8} {'기본값':<15}")
            print("-" * 80)
            
            for col in columns:
                null_str = "YES" if col['Null'] == 'YES' else "NO"
                key_str = col['Key'] if col['Key'] else ""
                default_str = str(col['Default']) if col['Default'] is not None else "NULL"
                
                print(f"{col['Field']:<25} {col['Type']:<20} {null_str:<8} {key_str:<8} {default_str:<15}")
            
            return True
            
    except Exception as e:
        print(f"❌ 테이블 구조 조회 실패: {e}")
        return False

def show_table_data(db_manager, table_name, limit=10):
    """테이블 데이터 샘플 출력"""
    try:
        with db_manager.connection.cursor(pymysql.cursors.DictCursor) as cursor:
            # 전체 레코드 수 조회
            cursor.execute(f"SELECT COUNT(*) as count FROM `{table_name}`")
            total_count = cursor.fetchone()['count']
            
            # 샘플 데이터 조회
            cursor.execute(f"SELECT * FROM `{table_name}` LIMIT {limit}")
            rows = cursor.fetchall()
            
            print(f"\n📋 테이블 데이터: {table_name} (총 {total_count}개 레코드)")
            print("-" * 100)
            
            if rows:
                df = pd.DataFrame(rows)
                # ID, created_at, updated_at 컬럼 제외하고 표시
                display_columns = [col for col in df.columns 
                                 if col not in ['id', 'created_at', 'updated_at']]
                
                if display_columns:
                    print(df[display_columns].to_string(index=False, max_colwidth=20))
                else:
                    print("표시할 데이터 컬럼이 없습니다.")
            else:
                print("데이터가 없습니다.")
            
            return True
            
    except Exception as e:
        print(f"❌ 테이블 데이터 조회 실패: {e}")
        return False

def show_table_statistics(db_manager, table_name):
    """테이블 통계 정보 출력"""
    try:
        with db_manager.connection.cursor(pymysql.cursors.DictCursor) as cursor:
            # 기본 통계
            cursor.execute(f"SELECT COUNT(*) as total_rows FROM `{table_name}`")
            total_rows = cursor.fetchone()['total_rows']
            
            # 테이블 크기
            cursor.execute(f"""
                SELECT 
                    ROUND(((data_length + index_length) / 1024 / 1024), 2) AS size_mb
                FROM information_schema.tables 
                WHERE table_schema = DATABASE() AND table_name = '{table_name}'
            """)
            size_info = cursor.fetchone()
            size_mb = size_info['size_mb'] if size_info else 0
            
            # 컬럼 정보
            cursor.execute(f"DESCRIBE `{table_name}`")
            columns = cursor.fetchall()
            
            print(f"\n📈 테이블 통계: {table_name}")
            print("-" * 50)
            print(f"전체 레코드 수: {total_rows:,}")
            print(f"테이블 크기: {size_mb} MB")
            print(f"컬럼 수: {len(columns)}")
            
            # 최근 업데이트 시간
            if any(col['Field'] == 'updated_at' for col in columns):
                cursor.execute(f"SELECT MAX(updated_at) as last_update FROM `{table_name}`")
                result = cursor.fetchone()
                if result['last_update']:
                    print(f"최근 업데이트: {result['last_update']}")
            
            return True
            
    except Exception as e:
        print(f"❌ 테이블 통계 조회 실패: {e}")
        return False

def list_all_tables(db_manager):
    """모든 테이블 목록 출력"""
    try:
        with db_manager.connection.cursor() as cursor:
            cursor.execute("SHOW TABLES")
            tables = cursor.fetchall()
            
            print(f"\n📚 데이터베이스 테이블 목록")
            print("=" * 60)
            
            if not tables:
                print("테이블이 없습니다.")
                return []
            
            table_info = []
            for i, table in enumerate(tables, 1):
                table_name = table[0]
                
                # 각 테이블의 레코드 수 조회
                cursor.execute(f"SELECT COUNT(*) FROM `{table_name}`")
                count = cursor.fetchone()[0]
                
                table_info.append({'name': table_name, 'count': count})
                print(f"{i:2d}. {table_name:<25} ({count:,}개 레코드)")
            
            return table_info
            
    except Exception as e:
        print(f"❌ 테이블 목록 조회 실패: {e}")
        return []

def export_table_to_csv(db_manager, table_name, output_dir):
    """테이블을 CSV로 내보내기"""
    try:
        with db_manager.connection.cursor(pymysql.cursors.DictCursor) as cursor:
            cursor.execute(f"SELECT * FROM `{table_name}`")
            rows = cursor.fetchall()
            
            if not rows:
                print(f"⚠️ {table_name}: 내보낼 데이터가 없습니다.")
                return False
            
            df = pd.DataFrame(rows)
            output_file = os.path.join(output_dir, f"{table_name}_export.csv")
            df.to_csv(output_file, index=False, encoding='utf-8-sig')
            
            print(f"✅ {table_name} → {output_file} ({len(rows)}개 레코드)")
            return True
            
    except Exception as e:
        print(f"❌ {table_name} CSV 내보내기 실패: {e}")
        return False

def interactive_mode(db_manager):
    """대화형 모드"""
    print(f"\n🔍 대화형 테이블 탐색 모드")
    print("=" * 50)
    
    while True:
        print(f"\n선택하세요:")
        print(f"1. 모든 테이블 목록 보기")
        print(f"2. 테이블 구조 보기")
        print(f"3. 테이블 데이터 보기")
        print(f"4. 테이블 통계 보기")
        print(f"5. 테이블을 CSV로 내보내기")
        print(f"6. 종료")
        
        choice = input(f"\n선택 (1-6): ").strip()
        
        if choice == '1':
            list_all_tables(db_manager)
            
        elif choice in ['2', '3', '4', '5']:
            tables = list_all_tables(db_manager)
            if not tables:
                continue
                
            table_choice = input(f"\n테이블 번호 선택 (1-{len(tables)}): ").strip()
            
            try:
                table_index = int(table_choice) - 1
                if 0 <= table_index < len(tables):
                    table_name = tables[table_index]['name']
                    
                    if choice == '2':
                        show_table_structure(db_manager, table_name)
                    elif choice == '3':
                        limit = input("표시할 레코드 수 (기본 10): ").strip()
                        limit = int(limit) if limit.isdigit() else 10
                        show_table_data(db_manager, table_name, limit)
                    elif choice == '4':
                        show_table_statistics(db_manager, table_name)
                    elif choice == '5':
                        output_dir = input("내보낼 디렉토리 (기본: ./): ").strip() or "./"
                        if not os.path.exists(output_dir):
                            os.makedirs(output_dir)
                        export_table_to_csv(db_manager, table_name, output_dir)
                else:
                    print("❌ 잘못된 테이블 번호입니다.")
            except ValueError:
                print("❌ 올바른 숫자를 입력하세요.")
                
        elif choice == '6':
            print("👋 종료합니다.")
            break
            
        else:
            print("❌ 1-6 사이의 숫자를 입력하세요.")

def main():
    """메인 함수"""
    print("🗄️ CSV 테이블 관리 유틸리티")
    print("=" * 50)
    
    # 환경변수에서 DB 설정 읽기
    db_config = {
        'host': os.getenv('DB_HOST', 'localhost'),
        'port': int(os.getenv('DB_PORT', 3306)),
        'user': os.getenv('DB_USER', 'root'),
        'password': os.getenv('DB_PASSWORD', ''),
        'database': os.getenv('DB_NAME', 'dive_recruit')
    }
    
    print(f"🔗 데이터베이스: {db_config['host']}:{db_config['port']}/{db_config['database']}")
    
    try:
        with DatabaseManager(**db_config) as db_manager:
            print(f"✅ 데이터베이스 연결 성공")
            
            # 명령행 인수 확인
            if len(sys.argv) > 1:
                command = sys.argv[1].lower()
                
                if command == 'list':
                    list_all_tables(db_manager)
                    
                elif command == 'structure' and len(sys.argv) > 2:
                    table_name = sys.argv[2]
                    show_table_structure(db_manager, table_name)
                    
                elif command == 'data' and len(sys.argv) > 2:
                    table_name = sys.argv[2]
                    limit = int(sys.argv[3]) if len(sys.argv) > 3 else 10
                    show_table_data(db_manager, table_name, limit)
                    
                elif command == 'stats' and len(sys.argv) > 2:
                    table_name = sys.argv[2]
                    show_table_statistics(db_manager, table_name)
                    
                elif command == 'export':
                    tables = list_all_tables(db_manager)
                    output_dir = sys.argv[2] if len(sys.argv) > 2 else "./"
                    
                    if not os.path.exists(output_dir):
                        os.makedirs(output_dir)
                    
                    print(f"\n📤 모든 테이블을 CSV로 내보내는 중...")
                    success_count = 0
                    for table_info in tables:
                        if export_table_to_csv(db_manager, table_info['name'], output_dir):
                            success_count += 1
                    
                    print(f"\n✅ 완료: {success_count}/{len(tables)} 테이블 내보내기 성공")
                    
                else:
                    print(f"❌ 알 수 없는 명령어: {command}")
                    print(f"\n💡 사용법:")
                    print(f"  python manage_tables.py list")
                    print(f"  python manage_tables.py structure <테이블명>")
                    print(f"  python manage_tables.py data <테이블명> [레코드수]")
                    print(f"  python manage_tables.py stats <테이블명>")
                    print(f"  python manage_tables.py export [출력디렉토리]")
            else:
                # 대화형 모드
                interactive_mode(db_manager)
                
    except Exception as e:
        print(f"❌ 데이터베이스 연결 실패: {e}")
        print(f"\n💡 해결 방법:")
        print(f"1. MariaDB가 실행 중인지 확인")
        print(f"2. 환경변수 설정 확인 (.env 파일)")
        print(f"3. create_tables_from_csv.py를 먼저 실행")

if __name__ == "__main__":
    main()
