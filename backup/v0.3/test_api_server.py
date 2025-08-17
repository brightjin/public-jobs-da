"""
테스트용 채용 데이터 API 서버
http://mysite.com/recruits 를 시뮬레이션하는 로컬 서버
"""

from flask import Flask, jsonify
import json
import os

app = Flask(__name__)

@app.route('/recruits', methods=['GET'])
def get_recruits():
    """채용 데이터 API - JSON 형태로 채용 정보 반환"""
    try:
        # CSV 데이터를 JSON으로 변환하여 반환
        sample_path = './data/api_sample.json'
        
        if os.path.exists(sample_path):
            with open(sample_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
        else:
            # 기본 샘플 데이터
            data = [
                {
                    "기관명": "부산교통공사",
                    "공고명": "2025년 부산교통공사 신입사원 공개채용",
                    "공고시작일": "8/1/25",
                    "공고마감일": "8/31/25",
                    "접수시작일": "8/15/25",
                    "접수마감일": "8/31/25",
                    "접수방법": "온라인 접수",
                    "접수대행": "자체",
                    "일반전형": "운영직, 운전직, 기계직, 전기직",
                    "채용인원": "120",
                    "채용방법": "NCS기반 직무능력중심 채용",
                    "전형방법": "1차 필기시험, 2차 면접시험",
                    "임용시기": "2025-10(월중)",
                    "임용조건": "부산·울산·경남 거주",
                    "담당부서": "인사처",
                    "연락처": "051-640-7196"
                }
            ]
        
        response = {
            "success": True,
            "total_count": len(data),
            "data": data,
            "message": "채용 데이터 조회 성공"
        }
        
        return jsonify(response)
        
    except Exception as e:
        return jsonify({
            "success": False,
            "error": str(e),
            "message": "채용 데이터 조회 실패"
        }), 500

@app.route('/health', methods=['GET'])
def health_check():
    """API 상태 확인"""
    return jsonify({
        "status": "healthy",
        "service": "채용 데이터 API",
        "version": "1.0.0"
    })

@app.route('/', methods=['GET'])
def home():
    """API 정보"""
    return jsonify({
        "service": "채용 데이터 API 서버",
        "endpoints": {
            "/recruits": "GET - 채용 데이터 조회",
            "/health": "GET - 서비스 상태 확인"
        },
        "description": "http://mysite.com/recruits 를 시뮬레이션하는 테스트 서버"
    })

if __name__ == '__main__':
    print("🌐 채용 데이터 API 테스트 서버 시작")
    print("📡 URL: http://localhost:3000/recruits")
    print("🔍 헬스체크: http://localhost:3000/health")
    app.run(host='0.0.0.0', port=3000, debug=False)
