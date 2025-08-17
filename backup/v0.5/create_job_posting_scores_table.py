#!/usr/bin/env python3
"""
채용공고평가점수 테이블 생성 스크립트
데이터베이스에 새로운 추천 시스템을 위한 테이블을 생성합니다.
"""

from database_manager import DatabaseManager
import random

def create_job_posting_scores_table():
    """채용공고평가점수 테이블 생성"""
    try:
        print("🗄️ 채용공고평가점수 테이블 생성 중...")
        
        with DatabaseManager() as db:
            # 테이블 생성 SQL
            create_table_sql = """
            CREATE TABLE IF NOT EXISTS 채용공고평가점수 (
                공고일련번호 VARCHAR(50) PRIMARY KEY,
                기관코드 VARCHAR(20) NOT NULL,
                일반전형 VARCHAR(100) NOT NULL,
                성실성 INT NOT NULL CHECK (성실성 BETWEEN 1 AND 5),
                개방성 INT NOT NULL CHECK (개방성 BETWEEN 1 AND 5),
                외향성 INT NOT NULL CHECK (외향성 BETWEEN 1 AND 5),
                우호성 INT NOT NULL CHECK (우호성 BETWEEN 1 AND 5),
                정서안정성 INT NOT NULL CHECK (정서안정성 BETWEEN 1 AND 5),
                기술전문성 INT NOT NULL CHECK (기술전문성 BETWEEN 1 AND 5),
                인지문제해결 INT NOT NULL CHECK (인지문제해결 BETWEEN 1 AND 5),
                `대인-영향력` INT NOT NULL CHECK (`대인-영향력` BETWEEN 1 AND 5),
                자기관리 INT NOT NULL CHECK (자기관리 BETWEEN 1 AND 5),
                적응력 INT NOT NULL CHECK (적응력 BETWEEN 1 AND 5),
                학습속도 INT NOT NULL CHECK (학습속도 BETWEEN 1 AND 5),
                대인민첩성 INT NOT NULL CHECK (대인민첩성 BETWEEN 1 AND 5),
                성과민첩성 INT NOT NULL CHECK (성과민첩성 BETWEEN 1 AND 5),
                자기인식 INT NOT NULL CHECK (자기인식 BETWEEN 1 AND 5),
                자기조절 INT NOT NULL CHECK (자기조절 BETWEEN 1 AND 5),
                `공감-사회기술` INT NOT NULL CHECK (`공감-사회기술` BETWEEN 1 AND 5),
                생성일시 TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                수정일시 TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
                INDEX idx_agency_form (기관코드, 일반전형),
                INDEX idx_agency (기관코드),
                INDEX idx_form (일반전형)
            ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci
            """
            
            db.execute_query(create_table_sql, fetch=False)
            print("✅ 채용공고평가점수 테이블 생성 완료")
            
            # 테이블 존재 확인
            check_sql = "SHOW TABLES LIKE '채용공고평가점수'"
            result = db.execute_query(check_sql)
            
            if result:
                print("✅ 테이블 생성 확인됨")
                return True
            else:
                print("❌ 테이블 생성 실패")
                return False
                
    except Exception as e:
        print(f"❌ 테이블 생성 실패: {e}")
        return False

def insert_sample_data():
    """샘플 데이터 삽입"""
    try:
        print("🎯 샘플 데이터 생성 중...")
        
        # 샘플 기관 및 전형 정보
        sample_agencies = [
            "A001", "A002", "A003", "A004", "A005",
            "B001", "B002", "B003", "B004", "B005",
            "C001", "C002", "C003", "C004", "C005"
        ]
        
        sample_forms = [
            "일반사무", "기술직", "운전직", "공무직", "연구직",
            "사서직", "의료직", "교육직", "보건직", "전문직",
            "기능직", "서비스직", "관리직", "영업직", "생산직"
        ]
        
        sample_data = []
        posting_id = 1
        
        # 각 기관별로 여러 전형의 공고 생성
        for agency in sample_agencies:
            # 기관당 3-7개의 다른 전형 공고 생성
            num_forms = random.randint(3, 7)
            selected_forms = random.sample(sample_forms, num_forms)
            
            for form in selected_forms:
                # 각 전형당 1-3개의 공고 생성
                num_postings = random.randint(1, 3)
                
                for i in range(num_postings):
                    posting_number = f"JOB{posting_id:04d}"
                    
                    # 전형별 특성화된 점수 생성
                    scores = generate_scores_for_form(form)
                    
                    sample_data.append({
                        '공고일련번호': posting_number,
                        '기관코드': agency,
                        '일반전형': form,
                        **scores
                    })
                    
                    posting_id += 1
        
        print(f"📊 생성된 샘플 데이터: {len(sample_data)}개 공고")
        
        # 데이터베이스에 삽입
        with DatabaseManager() as db:
            insert_sql = """
            INSERT INTO 채용공고평가점수 
            (공고일련번호, 기관코드, 일반전형, 성실성, 개방성, 외향성, 우호성, 정서안정성, 
             기술전문성, 인지문제해결, `대인-영향력`, 자기관리, 적응력, 학습속도, 
             대인민첩성, 성과민첩성, 자기인식, 자기조절, `공감-사회기술`)
            VALUES (%(공고일련번호)s, %(기관코드)s, %(일반전형)s, %(성실성)s, %(개방성)s, %(외향성)s, 
                    %(우호성)s, %(정서안정성)s, %(기술전문성)s, %(인지문제해결)s, %(대인-영향력)s, 
                    %(자기관리)s, %(적응력)s, %(학습속도)s, %(대인민첩성)s, %(성과민첩성)s, 
                    %(자기인식)s, %(자기조절)s, %(공감-사회기술)s)
            """
            
            success_count = 0
            for data in sample_data:
                try:
                    db.execute_query(insert_sql, data, fetch=False)
                    success_count += 1
                except Exception as e:
                    print(f"⚠️ 데이터 삽입 실패: {data['공고일련번호']} - {e}")
            
            print(f"✅ 샘플 데이터 삽입 완료: {success_count}/{len(sample_data)}개")
            return True
            
    except Exception as e:
        print(f"❌ 샘플 데이터 삽입 실패: {e}")
        return False

def generate_scores_for_form(form):
    """전형별 특성화된 점수 생성"""
    score_columns = [
        '성실성', '개방성', '외향성', '우호성', '정서안정성', '기술전문성',
        '인지문제해결', '대인-영향력', '자기관리', '적응력', '학습속도',
        '대인민첩성', '성과민첩성', '자기인식', '자기조절', '공감-사회기술'
    ]
    
    scores = {}
    
    # 전형별 특성화된 점수 생성 규칙
    if '사무' in form or '관리' in form:
        # 사무/관리직: 성실성, 자기관리, 대인-영향력, 공감-사회기술 높음
        for col in score_columns:
            if col in ['성실성', '자기관리', '대인-영향력', '공감-사회기술']:
                scores[col] = random.randint(3, 5)
            else:
                scores[col] = random.randint(2, 4)
                
    elif '기술' in form or '연구' in form or '전문' in form:
        # 기술/연구/전문직: 기술전문성, 인지문제해결, 학습속도, 자기관리 높음
        for col in score_columns:
            if col in ['기술전문성', '인지문제해결', '학습속도', '자기관리']:
                scores[col] = random.randint(3, 5)
            else:
                scores[col] = random.randint(2, 4)
                
    elif '운전' in form or '기능' in form:
        # 운전/기능직: 성실성, 정서안정성, 적응력, 자기관리 높음
        for col in score_columns:
            if col in ['성실성', '정서안정성', '적응력', '자기관리']:
                scores[col] = random.randint(3, 5)
            else:
                scores[col] = random.randint(2, 4)
                
    elif '의료' in form or '보건' in form:
        # 의료/보건직: 성실성, 우호성, 공감-사회기술, 자기조절 높음
        for col in score_columns:
            if col in ['성실성', '우호성', '공감-사회기술', '자기조절']:
                scores[col] = random.randint(3, 5)
            else:
                scores[col] = random.randint(2, 4)
                
    elif '교육' in form or '사서' in form:
        # 교육/사서직: 개방성, 대인-영향력, 공감-사회기술, 학습속도 높음
        for col in score_columns:
            if col in ['개방성', '대인-영향력', '공감-사회기술', '학습속도']:
                scores[col] = random.randint(3, 5)
            else:
                scores[col] = random.randint(2, 4)
                
    elif '영업' in form or '서비스' in form:
        # 영업/서비스직: 외향성, 대인-영향력, 공감-사회기술, 대인민첩성 높음
        for col in score_columns:
            if col in ['외향성', '대인-영향력', '공감-사회기술', '대인민첩성']:
                scores[col] = random.randint(3, 5)
            else:
                scores[col] = random.randint(2, 4)
                
    else:
        # 기타: 균등한 점수 분포
        for col in score_columns:
            scores[col] = random.randint(2, 4)
    
    # 약간의 변동성 추가
    for col in score_columns:
        variation = random.randint(-1, 1)
        scores[col] = max(1, min(5, scores[col] + variation))
    
    return scores

def check_table_status():
    """테이블 상태 확인"""
    try:
        print("📊 채용공고평가점수 테이블 상태 확인 중...")
        
        with DatabaseManager() as db:
            # 테이블 존재 확인
            check_sql = "SHOW TABLES LIKE '채용공고평가점수'"
            result = db.execute_query(check_sql)
            
            if not result:
                print("❌ 채용공고평가점수 테이블이 존재하지 않습니다.")
                return False
            
            # 레코드 수 확인
            count_sql = "SELECT COUNT(*) as count FROM 채용공고평가점수"
            count_result = db.execute_query(count_sql)
            
            if count_result:
                record_count = count_result[0][0]
                print(f"✅ 테이블 존재 확인: {record_count}개 레코드")
                
                # 기관별 통계
                stats_sql = """
                SELECT 
                    COUNT(DISTINCT 기관코드) as agencies,
                    COUNT(DISTINCT 일반전형) as forms,
                    COUNT(*) as total_postings
                FROM 채용공고평가점수
                """
                stats_result = db.execute_query(stats_sql)
                
                if stats_result:
                    agencies, forms, total = stats_result[0]
                    print(f"📋 통계: 기관 {agencies}개, 전형 {forms}개, 총 공고 {total}개")
                
                return True
            else:
                print("❌ 테이블 상태 확인 실패")
                return False
                
    except Exception as e:
        print(f"❌ 테이블 상태 확인 실패: {e}")
        return False

def main():
    """메인 실행 함수"""
    print("🚀 채용공고평가점수 테이블 설정 시작")
    print("=" * 50)
    
    # 1. 테이블 상태 확인
    if check_table_status():
        print("\n⚠️ 테이블이 이미 존재합니다.")
        response = input("새로운 샘플 데이터를 추가하시겠습니까? (y/n): ")
        if response.lower() != 'y':
            print("작업을 취소합니다.")
            return
    else:
        # 2. 테이블 생성
        if not create_job_posting_scores_table():
            print("테이블 생성에 실패했습니다.")
            return
    
    # 3. 샘플 데이터 삽입
    if insert_sample_data():
        print("\n✅ 채용공고평가점수 테이블 설정 완료!")
        
        # 4. 최종 상태 확인
        print("\n" + "=" * 50)
        check_table_status()
        
        print("\n🎯 이제 다음 명령으로 추천 모델을 생성할 수 있습니다:")
        print("   python3 model_builder.py --source database")
    else:
        print("❌ 샘플 데이터 삽입에 실패했습니다.")

if __name__ == "__main__":
    main()
