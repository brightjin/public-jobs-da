import requests
import json

# API 서버 주소
BASE_URL = "http://localhost:8080"

def test_api():
    """API 테스트 함수"""
    
    print("🧪 구직자 적합 전형 추천 API 테스트")
    print("=" * 50)
    
    # 1. 서버 상태 확인
    print("🔍 서버 상태 확인...")
    try:
        response = requests.get(f"{BASE_URL}/health")
        print(f"Status: {response.status_code}")
        print(f"Response: {response.json()}\n")
    except requests.exceptions.ConnectionError:
        print("❌ 서버에 연결할 수 없습니다. 서버가 실행 중인지 확인하세요.\n")
        return
    
    # 2. 홈페이지 확인
    print("🏠 홈페이지 확인...")
    response = requests.get(f"{BASE_URL}/")
    print(f"Response: {response.json()}\n")
    
    # 3. 전형 목록 조회
    print("📋 전형 목록 조회...")
    response = requests.get(f"{BASE_URL}/forms")
    if response.status_code == 200:
        data = response.json()
        print(f"총 전형 수: {data['total_forms']}")
        print(f"첫 5개 전형: {data['forms'][:5]}")
        print(f"기관별 전형 수: {len(data['forms_by_organization'])}\n")
    
    # 4. 능력 카테고리 조회
    print("📊 능력 카테고리 조회...")
    response = requests.get(f"{BASE_URL}/categories")
    if response.status_code == 200:
        data = response.json()
        print(f"능력 항목 ({len(data['categories'])}개): {data['categories'][:5]}...\n")
    
    # 5. 전형 추천 테스트
    print("🎯 전형 추천 테스트...")
    
    # 테스트 구직자 데이터들
    test_cases = [
        {
            "name": "👨‍💻 구직자 A (기술직 성향)",
            "description": "기술전문성, 인지문제해결, 학습속도가 높음",
            "scores": {
                "성실성": 4, "개방성": 3, "외향성": 2, "우호성": 3, "정서안정성": 4,
                "기술전문성": 5, "인지문제해결": 5, "대인-영향력": 2, "자기관리": 4, 
                "적응력": 4, "학습속도": 5, "대인민첩성": 2, "성과민첩성": 3, 
                "자기인식": 3, "자기조절": 4, "공감-사회기술": 3
            }
        },
        {
            "name": "👩‍💼 구직자 B (운영직 성향)",
            "description": "성실성, 대인-영향력, 자기관리, 공감-사회기술이 높음",
            "scores": {
                "성실성": 5, "개방성": 4, "외향성": 4, "우호성": 5, "정서안정성": 4,
                "기술전문성": 2, "인지문제해결": 3, "대인-영향력": 5, "자기관리": 5, 
                "적응력": 4, "학습속도": 3, "대인민첩성": 5, "성과민첩성": 4, 
                "자기인식": 4, "자기조절": 4, "공감-사회기술": 5
            }
        },
        {
            "name": "🚗 구직자 C (운전직 성향)",
            "description": "성실성, 정서안정성, 자기관리, 적응력이 높음",
            "scores": {
                "성실성": 5, "개방성": 3, "외향성": 3, "우호성": 4, "정서안정성": 5,
                "기술전문성": 3, "인지문제해결": 3, "대인-영향력": 3, "자기관리": 5, 
                "적응력": 5, "학습속도": 3, "대인민첩성": 3, "성과민첩성": 4, 
                "자기인식": 4, "자기조절": 5, "공감-사회기술": 3
            }
        }
    ]
    
    for test_case in test_cases:
        print(f"\n{test_case['name']}:")
        print(f"특징: {test_case['description']}")
        
        # 추천 요청
        payload = {
            "scores": test_case["scores"],
            "top_n": 3
        }
        
        response = requests.post(
            f"{BASE_URL}/recommend",
            headers={'Content-Type': 'application/json'},
            data=json.dumps(payload)
        )
        
        if response.status_code == 200:
            data = response.json()
            print("✅ 추천 성공!")
            
            # 프로필 분석 출력
            profile = data['profile_analysis']
            print(f"평균 점수: {profile['평균_점수']}")
            print(f"강점: {', '.join([item['항목'] for item in profile['강점_항목']])}")
            
            # 추천 결과 출력
            print("추천 결과:")
            for rec in data['recommendations']:
                print(f"  {rec['순위']}. {rec['전형명']} - 적합도: {rec['적합도']}%")
        else:
            print(f"❌ 추천 실패: {response.status_code}")
            print(f"Error: {response.text}")
    
    # 6. 잘못된 요청 테스트
    print(f"\n🚨 잘못된 요청 테스트...")
    
    # 점수 범위 초과
    invalid_payload = {
        "scores": {
            "성실성": 6,  # 잘못된 점수 (1-5 범위 초과)
            "개방성": 3
            # 나머지 항목 누락
        }
    }
    
    response = requests.post(
        f"{BASE_URL}/recommend",
        headers={'Content-Type': 'application/json'},
        data=json.dumps(invalid_payload)
    )
    
    if response.status_code == 400:
        print("✅ 잘못된 요청 처리 확인:")
        print(f"Error: {response.json()}")
    else:
        print(f"❌ 예상과 다른 응답: {response.status_code}")

def test_specific_endpoint(endpoint):
    """특정 엔드포인트 테스트"""
    print(f"🔍 {endpoint} 엔드포인트 테스트...")
    
    try:
        if endpoint == "/recommend":
            # 샘플 데이터로 테스트
            payload = {
                "scores": {
                    "성실성": 4, "개방성": 3, "외향성": 2, "우호성": 3, "정서안정성": 4,
                    "기술전문성": 5, "인지문제해결": 5, "대인-영향력": 2, "자기관리": 4, 
                    "적응력": 4, "학습속도": 5, "대인민첩성": 2, "성과민첩성": 3, 
                    "자기인식": 3, "자기조절": 4, "공감-사회기술": 3
                },
                "top_n": 5
            }
            response = requests.post(f"{BASE_URL}{endpoint}", json=payload)
        else:
            response = requests.get(f"{BASE_URL}{endpoint}")
        
        print(f"Status: {response.status_code}")
        print(f"Response: {response.json()}")
        
    except requests.exceptions.ConnectionError:
        print("❌ 서버에 연결할 수 없습니다.")
    except Exception as e:
        print(f"❌ 오류 발생: {e}")

if __name__ == "__main__":
    import sys
    
    if len(sys.argv) > 1:
        # 특정 엔드포인트 테스트
        endpoint = sys.argv[1]
        test_specific_endpoint(endpoint)
    else:
        # 전체 API 테스트
        test_api()
