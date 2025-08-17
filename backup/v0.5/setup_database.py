"""
MariaDB 초기화 및 설정 스크립트
데이터베이스 생성, 테이블 생성, 샘플 데이터 삽입
"""

import os
import sys
from database_manager import DatabaseManager

def setup_database():
    """데이터베이스 초기 설정"""
    
    print("🗄️ MariaDB 데이터베이스 초기화 시작")
    print("=" * 50)
    
    # 환경변수에서 DB 설정 읽기
    db_config = {
        'host': os.getenv('DB_HOST', 'localhost'),
        'port': int(os.getenv('DB_PORT', 3306)),
        'user': os.getenv('DB_USER', 'root'),
        'password': os.getenv('DB_PASSWORD', ''),
        'database': os.getenv('DB_NAME', 'dive_recruit')
    }
    
    print(f"📍 DB 호스트: {db_config['host']}:{db_config['port']}")
    print(f"👤 DB 사용자: {db_config['user']}")
    print(f"📊 DB 이름: {db_config['database']}")
    print()
    
    try:
        # 1. 데이터베이스 연결 및 테이블 생성
        print("1️⃣ 데이터베이스 연결 및 테이블 생성...")
        with DatabaseManager(**db_config) as db:
            db.create_tables()
            print("✅ 테이블 생성 완료")
        
        # 2. 샘플 점수 데이터 삽입
        print("\n2️⃣ 샘플 점수 데이터 삽입...")
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
                "일반전형": "운전직",
                "성실성": 5, "개방성": 3, "외향성": 3, "우호성": 4, "정서안정성": 5,
                "기술전문성": 3, "인지문제해결": 3, "대인-영향력": 3, "자기관리": 5,
                "적응력": 5, "학습속도": 3, "대인민첩성": 3, "성과민첩성": 4,
                "자기인식": 4, "자기조절": 5, "공감-사회기술": 4
            },
            {
                "기관명": "부산교통공사",
                "일반전형": "기계직",
                "성실성": 4, "개방성": 4, "외향성": 2, "우호성": 3, "정서안정성": 3,
                "기술전문성": 5, "인지문제해결": 5, "대인-영향력": 2, "자기관리": 4,
                "적응력": 4, "학습속도": 5, "대인민첩성": 2, "성과민첩성": 3,
                "자기인식": 3, "자기조절": 4, "공감-사회기술": 3
            },
            {
                "기관명": "부산교통공사",
                "일반전형": "전기직",
                "성실성": 4, "개방성": 4, "외향성": 2, "우호성": 3, "정서안정성": 4,
                "기술전문성": 5, "인지문제해결": 5, "대인-영향력": 3, "자기관리": 5,
                "적응력": 4, "학습속도": 5, "대인민첩성": 2, "성과민첩성": 4,
                "자기인식": 4, "자기조절": 4, "공감-사회기술": 3
            },
            {
                "기관명": "한국공항공사",
                "일반전형": "항공교통관제직",
                "성실성": 5, "개방성": 4, "외향성": 3, "우호성": 4, "정서안정성": 5,
                "기술전문성": 5, "인지문제해결": 5, "대인-영향력": 4, "자기관리": 5,
                "적응력": 5, "학습속도": 4, "대인민첩성": 4, "성과민첩성": 4,
                "자기인식": 4, "자기조절": 5, "공감-사회기술": 4
            },
            {
                "기관명": "한국공항공사",
                "일반전형": "시설관리직",
                "성실성": 4, "개방성": 3, "외향성": 3, "우호성": 4, "정서안정성": 4,
                "기술전문성": 4, "인지문제해결": 4, "대인-영향력": 3, "자기관리": 4,
                "적응력": 4, "학습속도": 3, "대인민첩성": 3, "성과민첩성": 3,
                "자기인식": 3, "자기조절": 4, "공감-사회기술": 4
            },
            {
                "기관명": "한국철도공사",
                "일반전형": "운전직",
                "성실성": 5, "개방성": 3, "외향성": 3, "우호성": 4, "정서안정성": 5,
                "기술전문성": 4, "인지문제해결": 4, "대인-영향력": 3, "자기관리": 5,
                "적응력": 5, "학습속도": 3, "대인민첩성": 3, "성과민첩성": 4,
                "자기인식": 4, "자기조절": 5, "공감-사회기술": 3
            },
            {
                "기관명": "한국철도공사",
                "일반전형": "차량정비직",
                "성실성": 4, "개방성": 4, "외향성": 2, "우호성": 3, "정서안정성": 3,
                "기술전문성": 5, "인지문제해결": 5, "대인-영향력": 2, "자기관리": 4,
                "적응력": 4, "학습속도": 5, "대인민첩성": 2, "성과민첩성": 3,
                "자기인식": 3, "자기조절": 4, "공감-사회기술": 2
            }
        ]
        
        with DatabaseManager(**db_config) as db:
            inserted_count = db.bulk_insert_scores(sample_scores)
            print(f"✅ 샘플 데이터 삽입 완료: {inserted_count}개")
        
        # 3. 샘플 추천 결과 저장
        print("\n3️⃣ 샘플 추천 결과 저장...")
        sample_recommendations = [
            {
                "session_id": "sample_session_001",
                "user_scores": {
                    "성실성": 4, "개방성": 3, "외향성": 2, "우호성": 3,
                    "정서안정성": 4, "기술전문성": 5, "인지문제해결": 5,
                    "대인-영향력": 2, "자기관리": 4, "적응력": 4,
                    "학습속도": 5, "대인민첩성": 2, "성과민첩성": 3,
                    "자기인식": 3, "자기조절": 4, "공감-사회기술": 3
                },
                "recommendations": [
                    {"순위": 1, "전형명": "기계직", "적합도": 89.5, "코사인유사도": 0.952},
                    {"순위": 2, "전형명": "전기직", "적합도": 87.2, "코사인유사도": 0.931}
                ],
                "profile_analysis": {
                    "강점_항목": ["기술전문성", "인지문제해결", "학습속도"],
                    "개선_항목": ["외향성", "대인-영향력", "대인민첩성"],
                    "평균_점수": 3.6
                },
                "model_version": "v20250816_sample"
            }
        ]
        
        with DatabaseManager(**db_config) as db:
            for rec in sample_recommendations:
                success = db.save_recommendation(
                    session_id=rec["session_id"],
                    user_scores=rec["user_scores"],
                    recommendations=rec["recommendations"],
                    profile_analysis=rec["profile_analysis"],
                    model_version=rec["model_version"]
                )
                if success:
                    print(f"✅ 샘플 추천 결과 저장: {rec['session_id']}")
        
        # 4. 데이터 확인
        print("\n4️⃣ 데이터 확인...")
        with DatabaseManager(**db_config) as db:
            scores_data = db.get_scores_data()
            recommendations_data = db.get_recommendations_history(limit=5)
            stats = db.get_recommendation_statistics()
            
            print(f"📊 점수 데이터: {len(scores_data)}개")
            print(f"💾 추천 결과: {len(recommendations_data)}개")
            print(f"📈 통계 정보: {stats}")
        
        print("\n" + "=" * 50)
        print("🎉 MariaDB 데이터베이스 초기화 완료!")
        print("=" * 50)
        print("\n💡 다음 단계:")
        print("1. MariaDB API 서버 실행: python mariadb_api_server.py")
        print("2. 점수 데이터 조회: curl http://localhost:3001/scores")
        print("3. 상태 확인: curl http://localhost:3001/health")
        
    except Exception as e:
        print(f"\n❌ 데이터베이스 초기화 실패: {str(e)}")
        print("\n💡 해결 방법:")
        print("1. MariaDB가 설치되어 있고 실행 중인지 확인")
        print("2. 데이터베이스 연결 정보가 올바른지 확인")
        print("3. pymysql 패키지가 설치되어 있는지 확인: pip install pymysql")
        print("4. 환경변수 설정:")
        print("   export DB_HOST=localhost")
        print("   export DB_USER=root")
        print("   export DB_PASSWORD=your_password")
        print("   export DB_NAME=dive_recruit")
        
        return False
    
    return True

def print_database_info():
    """데이터베이스 설정 정보 출력"""
    print("\n📋 데이터베이스 설정 정보")
    print("-" * 30)
    print(f"호스트: {os.getenv('DB_HOST', 'localhost')}")
    print(f"포트: {os.getenv('DB_PORT', '3306')}")
    print(f"사용자: {os.getenv('DB_USER', 'root')}")
    print(f"데이터베이스: {os.getenv('DB_NAME', 'dive_recruit')}")
    print(f"비밀번호: {'설정됨' if os.getenv('DB_PASSWORD') else '미설정'}")

def main():
    """메인 실행 함수"""
    print("🗄️ MariaDB 초기화 스크립트")
    print_database_info()
    print()
    
    # 사용자 확인
    while True:
        choice = input("데이터베이스를 초기화하시겠습니까? (y/N): ").strip().lower()
        if choice in ['y', 'yes']:
            break
        elif choice in ['n', 'no', '']:
            print("초기화를 취소했습니다.")
            return
        else:
            print("y 또는 n을 입력하세요.")
    
    # 데이터베이스 초기화 실행
    success = setup_database()
    
    if success:
        print("\n🚀 다음 명령어로 API 서버를 시작할 수 있습니다:")
        print("python mariadb_api_server.py")
    else:
        sys.exit(1)

if __name__ == "__main__":
    main()
