"""
테스트용 점수 데이터 API 서버
http://mysite.com/scores 를 시뮬레이션하는 로컬 서버
"""

from flask import Flask, jsonify
import json
import os
import numpy as np

app = Flask(__name__)

@app.route('/scores', methods=['GET'])
def get_scores():
    """점수 데이터 API - JSON 형태로 전형별 점수 정보 반환"""
    try:
        # 샘플 점수 데이터 생성
        sample_scores = [
            {
                "기관명": "부산교통공사",
                "일반전형": "운영직",
                "성실성": 4,
                "개방성": 3,
                "외향성": 4,
                "우호성": 4,
                "정서안정성": 3,
                "기술전문성": 3,
                "인지문제해결": 3,
                "대인-영향력": 4,
                "자기관리": 5,
                "적응력": 4,
                "학습속도": 3,
                "대인민첩성": 4,
                "성과민첩성": 4,
                "자기인식": 3,
                "자기조절": 4,
                "공감-사회기술": 5
            },
            {
                "기관명": "부산교통공사",
                "일반전형": "운전직",
                "성실성": 5,
                "개방성": 3,
                "외향성": 3,
                "우호성": 4,
                "정서안정성": 5,
                "기술전문성": 3,
                "인지문제해결": 3,
                "대인-영향력": 3,
                "자기관리": 5,
                "적응력": 5,
                "학습속도": 3,
                "대인민첩성": 3,
                "성과민첩성": 4,
                "자기인식": 4,
                "자기조절": 5,
                "공감-사회기술": 4
            },
            {
                "기관명": "부산교통공사",
                "일반전형": "기계직",
                "성실성": 4,
                "개방성": 4,
                "외향성": 2,
                "우호성": 3,
                "정서안정성": 3,
                "기술전문성": 5,
                "인지문제해결": 5,
                "대인-영향력": 2,
                "자기관리": 4,
                "적응력": 4,
                "학습속도": 5,
                "대인민첩성": 2,
                "성과민첩성": 3,
                "자기인식": 3,
                "자기조절": 4,
                "공감-사회기술": 3
            },
            {
                "기관명": "부산교통공사",
                "일반전형": "전기직",
                "성실성": 4,
                "개방성": 4,
                "외향성": 2,
                "우호성": 3,
                "정서안정성": 4,
                "기술전문성": 5,
                "인지문제해결": 5,
                "대인-영향력": 3,
                "자기관리": 5,
                "적응력": 4,
                "학습속도": 5,
                "대인민첩성": 2,
                "성과민첩성": 4,
                "자기인식": 4,
                "자기조절": 4,
                "공감-사회기술": 3
            },
            {
                "기관명": "한국공항공사",
                "일반전형": "항공교통관제직",
                "성실성": 5,
                "개방성": 4,
                "외향성": 3,
                "우호성": 4,
                "정서안정성": 5,
                "기술전문성": 5,
                "인지문제해결": 5,
                "대인-영향력": 4,
                "자기관리": 5,
                "적응력": 5,
                "학습속도": 4,
                "대인민첩성": 4,
                "성과민첩성": 4,
                "자기인식": 4,
                "자기조절": 5,
                "공감-사회기술": 4
            }
        ]
        
        response = {
            "success": True,
            "total_count": len(sample_scores),
            "data": sample_scores,
            "message": "점수 데이터 조회 성공"
        }
        
        return jsonify(response)
        
    except Exception as e:
        return jsonify({
            "success": False,
            "error": str(e),
            "message": "점수 데이터 조회 실패"
        }), 500

@app.route('/health', methods=['GET'])
def health_check():
    """API 상태 확인"""
    return jsonify({
        "status": "healthy",
        "service": "점수 데이터 API",
        "version": "1.0.0"
    })

@app.route('/', methods=['GET'])
def home():
    """API 정보"""
    return jsonify({
        "service": "점수 데이터 API 서버",
        "endpoints": {
            "/scores": "GET - 전형별 점수 데이터 조회",
            "/health": "GET - 서비스 상태 확인"
        },
        "description": "http://mysite.com/scores 를 시뮬레이션하는 테스트 서버",
        "score_format": {
            "기관명": "기관명",
            "일반전형": "전형명",
            "성실성": "1-5점",
            "기타_16가지_항목": "1-5점"
        }
    })

if __name__ == '__main__':
    print("🎯 점수 데이터 API 테스트 서버 시작")
    print("📡 URL: http://localhost:3001/scores")
    print("🔍 헬스체크: http://localhost:3001/health")
    app.run(host='0.0.0.0', port=3001, debug=False)
