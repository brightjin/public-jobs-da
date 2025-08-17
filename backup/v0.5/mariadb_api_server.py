"""
MariaDB 기반 점수 데이터 API 서버
database_manager.py의 DatabaseManager를 사용하여 실제 DB에서 점수 데이터를 조회
"""

from flask import Flask, jsonify, request
import json
import os
import sys
from datetime import datetime
import uuid

# 현재 디렉토리를 Python 경로에 추가
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

try:
    from database_manager import DatabaseManager
    DB_AVAILABLE = True
except ImportError:
    print("⚠️ database_manager 모듈을 가져올 수 없습니다. 샘플 데이터를 사용합니다.")
    DB_AVAILABLE = False

app = Flask(__name__)

# 데이터베이스 설정 (환경변수 또는 기본값 사용)
DB_CONFIG = {
    'host': os.getenv('DB_HOST', 'localhost'),
    'port': int(os.getenv('DB_PORT', 3306)),
    'user': os.getenv('DB_USER', 'root'),
    'password': os.getenv('DB_PASSWORD', ''),
    'database': os.getenv('DB_NAME', 'dive_recruit')
}

def get_sample_scores():
    """데이터베이스를 사용할 수 없을 때 사용할 샘플 데이터"""
    return [
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
            "기관명": "한국공항공사",
            "일반전형": "항공교통관제직",
            "성실성": 5, "개방성": 4, "외향성": 3, "우호성": 4, "정서안정성": 5,
            "기술전문성": 5, "인지문제해결": 5, "대인-영향력": 4, "자기관리": 5,
            "적응력": 5, "학습속도": 4, "대인민첩성": 4, "성과민첩성": 4,
            "자기인식": 4, "자기조절": 5, "공감-사회기술": 4
        }
    ]

@app.route('/scores', methods=['GET'])
def get_scores():
    """점수 데이터 API - MariaDB에서 점수 정보 조회"""
    try:
        if DB_AVAILABLE:
            # 실제 데이터베이스에서 조회
            with DatabaseManager(**DB_CONFIG) as db:
                scores_data = db.get_scores_data()
                
                if not scores_data:
                    # DB에 데이터가 없으면 샘플 데이터 사용
                    scores_data = get_sample_scores()
                    message = "데이터베이스가 비어있어 샘플 데이터를 반환합니다"
                else:
                    message = "데이터베이스에서 점수 데이터 조회 성공"
        else:
            # 데이터베이스 연결 불가 시 샘플 데이터 사용
            scores_data = get_sample_scores()
            message = "데이터베이스 연결 불가로 샘플 데이터를 사용합니다"
        
        response = {
            "success": True,
            "total_count": len(scores_data),
            "data": scores_data,
            "message": message,
            "db_available": DB_AVAILABLE,
            "timestamp": datetime.now().isoformat()
        }
        
        return jsonify(response)
        
    except Exception as e:
        # 에러 발생 시 샘플 데이터로 폴백
        scores_data = get_sample_scores()
        return jsonify({
            "success": False,
            "total_count": len(scores_data),
            "data": scores_data,
            "error": str(e),
            "message": "데이터베이스 오류로 샘플 데이터를 사용합니다",
            "db_available": False,
            "timestamp": datetime.now().isoformat()
        }), 500

@app.route('/scores', methods=['POST'])
def add_score():
    """점수 데이터 추가 API"""
    try:
        data = request.get_json()
        
        if not data:
            return jsonify({
                "success": False,
                "message": "JSON 데이터가 필요합니다"
            }), 400
        
        # 필수 필드 검증
        required_fields = ['기관명', '일반전형', '성실성', '개방성', '외향성', '우호성', 
                          '정서안정성', '기술전문성', '인지문제해결', '대인-영향력', 
                          '자기관리', '적응력', '학습속도', '대인민첩성', '성과민첩성', 
                          '자기인식', '자기조절', '공감-사회기술']
        
        missing_fields = [field for field in required_fields if field not in data]
        if missing_fields:
            return jsonify({
                "success": False,
                "message": f"필수 필드가 누락되었습니다: {missing_fields}"
            }), 400
        
        if DB_AVAILABLE:
            with DatabaseManager(**DB_CONFIG) as db:
                success = db.insert_score_data(data)
                
                if success:
                    return jsonify({
                        "success": True,
                        "message": "점수 데이터가 성공적으로 저장되었습니다",
                        "data": data
                    })
                else:
                    return jsonify({
                        "success": False,
                        "message": "점수 데이터 저장에 실패했습니다"
                    }), 500
        else:
            return jsonify({
                "success": False,
                "message": "데이터베이스 연결이 불가능합니다"
            }), 503
            
    except Exception as e:
        return jsonify({
            "success": False,
            "error": str(e),
            "message": "점수 데이터 추가 중 오류가 발생했습니다"
        }), 500

@app.route('/recommendations', methods=['POST'])
def save_recommendation():
    """추천 결과 저장 API"""
    try:
        data = request.get_json()
        
        if not data:
            return jsonify({
                "success": False,
                "message": "JSON 데이터가 필요합니다"
            }), 400
        
        # 필수 필드 검증
        if 'user_scores' not in data or 'recommendations' not in data:
            return jsonify({
                "success": False,
                "message": "user_scores와 recommendations 필드가 필요합니다"
            }), 400
        
        session_id = data.get('session_id', str(uuid.uuid4()))
        user_scores = data['user_scores']
        recommendations = data['recommendations']
        profile_analysis = data.get('profile_analysis')
        model_version = data.get('model_version')
        
        if DB_AVAILABLE:
            with DatabaseManager(**DB_CONFIG) as db:
                success = db.save_recommendation(
                    session_id=session_id,
                    user_scores=user_scores,
                    recommendations=recommendations,
                    profile_analysis=profile_analysis,
                    model_version=model_version
                )
                
                if success:
                    return jsonify({
                        "success": True,
                        "message": "추천 결과가 성공적으로 저장되었습니다",
                        "session_id": session_id
                    })
                else:
                    return jsonify({
                        "success": False,
                        "message": "추천 결과 저장에 실패했습니다"
                    }), 500
        else:
            return jsonify({
                "success": False,
                "message": "데이터베이스 연결이 불가능합니다"
            }), 503
            
    except Exception as e:
        return jsonify({
            "success": False,
            "error": str(e),
            "message": "추천 결과 저장 중 오류가 발생했습니다"
        }), 500

@app.route('/recommendations', methods=['GET'])
def get_recommendations():
    """추천 결과 조회 API"""
    try:
        session_id = request.args.get('session_id')
        limit = int(request.args.get('limit', 10))
        
        if DB_AVAILABLE:
            with DatabaseManager(**DB_CONFIG) as db:
                history = db.get_recommendations_history(session_id=session_id, limit=limit)
                
                return jsonify({
                    "success": True,
                    "total_count": len(history),
                    "data": history,
                    "message": "추천 이력 조회 성공"
                })
        else:
            return jsonify({
                "success": False,
                "message": "데이터베이스 연결이 불가능합니다"
            }), 503
            
    except Exception as e:
        return jsonify({
            "success": False,
            "error": str(e),
            "message": "추천 이력 조회 중 오류가 발생했습니다"
        }), 500

@app.route('/statistics', methods=['GET'])
def get_statistics():
    """통계 정보 조회 API"""
    try:
        if DB_AVAILABLE:
            with DatabaseManager(**DB_CONFIG) as db:
                stats = db.get_recommendation_statistics()
                
                return jsonify({
                    "success": True,
                    "data": stats,
                    "message": "통계 정보 조회 성공"
                })
        else:
            return jsonify({
                "success": False,
                "message": "데이터베이스 연결이 불가능합니다"
            }), 503
            
    except Exception as e:
        return jsonify({
            "success": False,
            "error": str(e),
            "message": "통계 정보 조회 중 오류가 발생했습니다"
        }), 500

@app.route('/health', methods=['GET'])
def health_check():
    """API 및 데이터베이스 상태 확인"""
    db_status = "unavailable"
    db_error = None
    
    if DB_AVAILABLE:
        try:
            with DatabaseManager(**DB_CONFIG) as db:
                # 간단한 쿼리로 연결 테스트
                with db.connection.cursor() as cursor:
                    cursor.execute("SELECT 1")
                    result = cursor.fetchone()
                    if result:
                        db_status = "connected"
        except Exception as e:
            db_status = "error"
            db_error = str(e)
    
    return jsonify({
        "status": "healthy",
        "service": "MariaDB 기반 점수 데이터 API",
        "version": "1.0.0",
        "database": {
            "status": db_status,
            "config": {
                "host": DB_CONFIG['host'],
                "port": DB_CONFIG['port'],
                "database": DB_CONFIG['database']
            },
            "error": db_error
        },
        "db_available": DB_AVAILABLE,
        "timestamp": datetime.now().isoformat()
    })

@app.route('/', methods=['GET'])
def home():
    """API 정보"""
    return jsonify({
        "service": "MariaDB 기반 점수 데이터 API 서버",
        "endpoints": {
            "GET /scores": "점수 데이터 조회",
            "POST /scores": "점수 데이터 추가",
            "POST /recommendations": "추천 결과 저장",
            "GET /recommendations": "추천 이력 조회 (session_id, limit 파라미터)",
            "GET /statistics": "추천 통계 정보",
            "GET /health": "서비스 및 DB 상태 확인"
        },
        "description": "MariaDB와 연동하는 점수 데이터 및 추천 결과 관리 API",
        "database": {
            "available": DB_AVAILABLE,
            "fallback": "샘플 데이터 사용 (DB 연결 실패 시)"
        },
        "environment_variables": {
            "DB_HOST": "데이터베이스 호스트 (기본: localhost)",
            "DB_PORT": "데이터베이스 포트 (기본: 3306)",
            "DB_USER": "데이터베이스 사용자 (기본: root)",
            "DB_PASSWORD": "데이터베이스 비밀번호",
            "DB_NAME": "데이터베이스 이름 (기본: dive_recruit)"
        }
    })

if __name__ == '__main__':
    print("🗄️ MariaDB 기반 점수 데이터 API 서버 시작")
    print("=" * 50)
    print(f"📡 URL: http://localhost:3003")
    print(f"🔍 헬스체크: http://localhost:3003/health")
    print(f"📊 점수 데이터: http://localhost:3003/scores")
    print(f"💾 추천 저장: http://localhost:3003/recommendations")
    print(f"📈 통계: http://localhost:3003/statistics")
    print("=" * 50)
    print(f"🗄️ DB 연결 가능: {DB_AVAILABLE}")
    if DB_AVAILABLE:
        print(f"📍 DB 호스트: {DB_CONFIG['host']}:{DB_CONFIG['port']}")
        print(f"📊 DB 이름: {DB_CONFIG['database']}")
    else:
        print("⚠️ 샘플 데이터를 사용합니다 (pymysql 설치 필요)")
    print("=" * 50)
    
    app.run(host='0.0.0.0', port=3003, debug=False)
