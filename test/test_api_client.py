#!/usr/bin/env python3
"""
API 클라이언트 테스트 스크립트
test_request.json 파일을 사용하여 http://localhost:8888/recommend API에 요청을 보내고 결과를 확인합니다.
"""

import json
import requests
import time
from datetime import datetime

def load_test_data(filename="test_request.json"):
    """테스트 요청 데이터를 JSON 파일에서 로드"""
    try:
        with open(filename, 'r', encoding='utf-8') as f:
            return json.load(f)
    except FileNotFoundError:
        print(f"❌ 파일을 찾을 수 없습니다: {filename}")
        return None
    except json.JSONDecodeError as e:
        print(f"❌ JSON 파싱 오류: {e}")
        return None

def test_api_connection(url):
    """API 서버 연결 상태 확인"""
    try:
        response = requests.get(url.replace('/recommend', '/health'), timeout=5)
        return response.status_code == 200
    except:
        return False

def send_recommendation_request(url, data):
    """추천 API에 요청을 보내고 응답을 받음"""
    try:
        print(f"🚀 API 요청 전송: {url}")
        print(f"📤 요청 데이터:")
        print(json.dumps(data, indent=2, ensure_ascii=False))
        print("-" * 50)
        
        # API 요청 전송
        response = requests.post(
            url,
            json=data,
            headers={
                'Content-Type': 'application/json',
                'Accept': 'application/json'
            },
            timeout=30
        )
        
        print(f"📊 응답 상태 코드: {response.status_code}")
        
        if response.status_code == 200:
            result = response.json()
            print("✅ 요청 성공!")
            return True, result
        else:
            print(f"❌ 요청 실패: {response.status_code}")
            try:
                error_data = response.json()
                print(f"오류 내용: {error_data}")
            except:
                print(f"오류 내용: {response.text}")
            return False, None
            
    except requests.exceptions.Timeout:
        print("❌ 요청 시간 초과")
        return False, None
    except requests.exceptions.ConnectionError:
        print("❌ 연결 오류 - API 서버가 실행 중인지 확인해주세요")
        return False, None
    except Exception as e:
        print(f"❌ 예상치 못한 오류: {e}")
        return False, None

def display_recommendations(result):
    """추천 결과를 보기 좋게 출력"""
    print("\n" + "=" * 60)
    print("📋 추천 결과")
    print("=" * 60)
    
    if 'recommendations' in result:
        recommendations = result['recommendations']
        print(f"📊 총 {len(recommendations)}개의 추천 공고")
        print()
        
        for i, rec in enumerate(recommendations, 1):
            print(f"  {i}. 공고번호: {rec.get('id', 'N/A')}")
            print(f"     기관명: {rec.get('기관명', 'N/A')}")
            print(f"     일반전형: {rec.get('일반전형', 'N/A')}")
            print(f"     유사도: {rec.get('유사도', 'N/A'):.3f}")
            print()
    
    if 'statistics' in result:
        stats = result['statistics']
        print("📈 시스템 통계:")
        for key, value in stats.items():
            print(f"   - {key}: {value}")
        print()
    
    if 'request_info' in result:
        req_info = result['request_info']
        print("🔍 요청 정보:")
        print(f"   - 요청 시간: {req_info.get('timestamp', 'N/A')}")
        print(f"   - 요청된 추천 수: {req_info.get('top_k', 'N/A')}")
        print(f"   - 처리 시간: {req_info.get('processing_time', 'N/A')}초")

def main():
    """메인 테스트 함수"""
    print("🔧 API 클라이언트 테스트 시작")
    print(f"⏰ 테스트 시작 시간: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 60)
    
    # 설정
    api_url = "http://localhost:8888/recommend"
    test_file = "test_request.json"
    
    # 1. 테스트 데이터 로드
    print("📁 테스트 데이터 로드 중...")
    test_data = load_test_data(test_file)
    if not test_data:
        return
    
    print("✅ 테스트 데이터 로드 완료")
    
    # 2. API 서버 연결 확인
    print("\n🔍 API 서버 연결 확인 중...")
    if not test_api_connection(api_url):
        print("❌ API 서버에 연결할 수 없습니다.")
        print("💡 다음을 확인해주세요:")
        print("   1. API 서버가 실행 중인지 확인 (./run.sh)")
        print("   2. 포트 8080이 사용 가능한지 확인")
        print("   3. 방화벽 설정 확인")
        return
    
    print("✅ API 서버 연결 확인 완료")
    
    # 3. 추천 요청 전송
    print("\n📤 추천 요청 전송 중...")
    success, result = send_recommendation_request(api_url, test_data)
    
    if success and result:
        # 4. 결과 출력
        display_recommendations(result)
        
        # 5. 성능 정보 출력
        if 'request_info' in result and 'processing_time' in result['request_info']:
            processing_time = result['request_info']['processing_time']
            print(f"\n⚡ 처리 성능: {processing_time:.3f}초")
            
            if processing_time < 1.0:
                print("🚀 우수한 응답 속도!")
            elif processing_time < 3.0:
                print("✅ 양호한 응답 속도")
            else:
                print("⚠️ 응답 속도가 다소 느림")
        
        print("\n✅ 테스트 완료!")
        
    else:
        print("\n❌ 테스트 실패!")
        print("💡 문제 해결 방법:")
        print("   1. API 서버 로그 확인")
        print("   2. test_request.json 파일 형식 확인")
        print("   3. 서버 재시작 시도")

def test_multiple_requests():
    """여러 요청을 연속으로 보내는 부하 테스트"""
    print("\n🔄 다중 요청 테스트 시작...")
    
    api_url = "http://localhost:8080/recommend"
    test_data = load_test_data()
    
    if not test_data:
        return
    
    success_count = 0
    total_time = 0
    num_requests = 5
    
    for i in range(num_requests):
        print(f"\n📤 요청 {i+1}/{num_requests}")
        start_time = time.time()
        success, result = send_recommendation_request(api_url, test_data)
        end_time = time.time()
        
        if success:
            success_count += 1
            request_time = end_time - start_time
            total_time += request_time
            print(f"✅ 성공 (소요시간: {request_time:.3f}초)")
        else:
            print("❌ 실패")
        
        time.sleep(0.5)  # 요청 간 간격
    
    print(f"\n📊 다중 요청 테스트 결과:")
    print(f"   - 성공률: {success_count}/{num_requests} ({success_count/num_requests*100:.1f}%)")
    print(f"   - 평균 응답 시간: {total_time/success_count:.3f}초" if success_count > 0 else "   - 평균 응답 시간: N/A")

if __name__ == "__main__":
    try:
        main()
        
        # 추가 테스트 실행 여부 확인
        print("\n" + "=" * 60)
        user_input = input("🔄 다중 요청 테스트를 실행하시겠습니까? (y/N): ").strip().lower()
        if user_input in ['y', 'yes']:
            test_multiple_requests()
            
    except KeyboardInterrupt:
        print("\n\n⏹️ 사용자에 의해 테스트가 중단되었습니다.")
    except Exception as e:
        print(f"\n❌ 예상치 못한 오류: {e}")
