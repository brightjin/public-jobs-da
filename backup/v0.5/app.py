from flask import Flask, request, jsonify
from flask_cors import CORS
from model_loader import JobRecommendationModelLoader
import warnings
warnings.filterwarnings('ignore')

app = Flask(__name__)
CORS(app)  # CORS 설정으로 프론트엔드에서 접근 가능

# 전역 모델 로더
model_loader = None

from flask import Flask, request, jsonify
from flask_cors import CORS
from model_loader import JobRecommendationModelLoader
import warnings
warnings.filterwarnings('ignore')

app = Flask(__name__)
CORS(app)  # CORS 설정으로 프론트엔드에서 접근 가능

# 전역 모델 로더
model_loader = None

def initialize_model():
    """모델 초기화 함수"""
    global model_loader
    
    try:
        print("📂 저장된 모델 로딩 중...")
        model_loader = JobRecommendationModelLoader()
        
        if model_loader.load_model():
            print("✅ 모델 로딩 성공!")
            return True
        else:
            print("❌ 모델 로딩 실패")
            return False
            
    except Exception as e:
        print(f"❌ 모델 초기화 오류: {e}")
        return False

# API 엔드포인트들

@app.route('/', methods=['GET'])
def home():
    """API 상태 확인"""
    model_info = model_loader.get_model_info() if model_loader and model_loader.is_loaded else None
    
    return jsonify({
        'message': '구직자 적합 전형 추천 API (모델 분리 버전)',
        'status': 'running',
        'version': '2.0.0',
        'model_version': model_info['version'] if model_info else 'N/A',
        'model_loaded': model_loader.is_loaded if model_loader else False,
        'endpoints': {
            'POST /recommend': '전형 추천',
            'GET /forms': '전체 전형 목록',
            'GET /categories': '능력 카테고리 목록',
            'GET /health': '서비스 상태 확인',
            'POST /reload_model': '모델 다시 로딩'
        }
    })

@app.route('/recommend', methods=['POST'])
def recommend():
    """전형 추천 API"""
    try:
        if not model_loader or not model_loader.is_loaded:
            return jsonify({'error': '모델이 로딩되지 않았습니다.'}), 500
        
        data = request.get_json()
        
        if not data:
            return jsonify({'error': '요청 데이터가 없습니다.'}), 400
        
        # 구직자 점수 가져오기
        구직자_점수 = data.get('scores', {})
        
        if not 구직자_점수:
            return jsonify({'error': '점수 데이터가 없습니다.'}), 400
        
        # 점수 유효성 검사
        is_valid, validation_message = model_loader.validate_scores(구직자_점수)
        if not is_valid:
            return jsonify({'error': validation_message}), 400
        
        # 추천 개수 설정
        top_n = data.get('top_n', 5)
        if not isinstance(top_n, int) or top_n < 1 or top_n > 20:
            top_n = 5
        
        # 전형 추천 실행
        추천_결과 = model_loader.recommend_forms(구직자_점수, top_n)
        
        # 구직자 프로필 분석
        프로필_분석 = model_loader.analyze_profile(구직자_점수)
        
        # 모델 정보
        model_info = model_loader.get_model_info()
        
        return jsonify({
            'success': True,
            'recommendations': 추천_결과,
            'profile_analysis': 프로필_분석,
            'request_info': {
                'top_n': top_n,
                'total_forms': model_info['unique_forms'],
                'model_version': model_info['version']
            }
        })
        
    except Exception as e:
        return jsonify({'error': f'추천 처리 중 오류 발생: {str(e)}'}), 500

@app.route('/forms', methods=['GET'])
def get_forms():
    """전체 전형 목록 API"""
    try:
        if not model_loader or not model_loader.is_loaded:
            return jsonify({'error': '모델이 로딩되지 않았습니다.'}), 500
        
        forms_data = model_loader.get_forms_list()
        model_info = model_loader.get_model_info()
        
        return jsonify({
            'success': True,
            'total_forms': len(forms_data['forms_list']),
            'forms': forms_data['forms_list'],
            'forms_by_organization': forms_data['forms_by_organization'],
            'model_version': model_info['version']
        })
        
    except Exception as e:
        return jsonify({'error': f'전형 목록 조회 중 오류 발생: {str(e)}'}), 500

@app.route('/categories', methods=['GET'])
def get_categories():
    """능력 카테고리 목록 API"""
    if not model_loader or not model_loader.is_loaded:
        return jsonify({'error': '모델이 로딩되지 않았습니다.'}), 500
    
    model_info = model_loader.get_model_info()
    score_columns = model_info['score_columns']
    
    return jsonify({
        'success': True,
        'categories': score_columns,
        'description': {
            '성실성': '책임감과 신뢰성',
            '개방성': '새로운 경험에 대한 개방성',
            '외향성': '사교성과 활동성',
            '우호성': '협조성과 친화성',
            '정서안정성': '스트레스 관리와 감정 조절',
            '기술전문성': '전문 기술 역량',
            '인지문제해결': '논리적 사고와 문제 해결',
            '대인-영향력': '타인에게 영향을 미치는 능력',
            '자기관리': '시간과 업무 관리',
            '적응력': '변화에 대한 적응',
            '학습속도': '새로운 지식 습득 속도',
            '대인민첩성': '대인관계에서의 민첩성',
            '성과민첩성': '성과 달성을 위한 민첩성',
            '자기인식': '자신에 대한 이해',
            '자기조절': '자기 통제 능력',
            '공감-사회기술': '타인 이해와 사회적 기술'
        },
        'model_version': model_info['version']
    })

@app.route('/health', methods=['GET'])
def health_check():
    """서비스 상태 확인 API"""
    try:
        model_status = model_loader and model_loader.is_loaded
        model_info = model_loader.get_model_info() if model_status else None
        
        return jsonify({
            'status': 'healthy' if model_status else 'unhealthy',
            'model_loaded': model_status,
            'model_info': {
                'version': model_info['version'] if model_info else 'N/A',
                'created_at': model_info['created_at'] if model_info else 'N/A',
                'total_forms': model_info['unique_forms'] if model_info else 0,
                'total_organizations': model_info['unique_organizations'] if model_info else 0
            } if model_info else None
        })
    except Exception as e:
        return jsonify({
            'status': 'error',
            'error': str(e)
        }), 500

@app.route('/reload_model', methods=['POST'])
def reload_model():
    """모델 다시 로딩 API"""
    try:
        print("🔄 모델 다시 로딩 요청 받음...")
        
        if initialize_model():
            model_info = model_loader.get_model_info()
            return jsonify({
                'success': True,
                'message': '모델이 성공적으로 다시 로딩되었습니다.',
                'model_info': {
                    'version': model_info['version'],
                    'created_at': model_info['created_at'],
                    'total_forms': model_info['unique_forms'],
                    'total_organizations': model_info['unique_organizations']
                }
            })
        else:
            return jsonify({
                'success': False,
                'error': '모델 로딩에 실패했습니다.'
            }), 500
            
    except Exception as e:
        return jsonify({
            'success': False,
            'error': f'모델 로딩 중 오류 발생: {str(e)}'
        }), 500

# 서버 시작 시 모델 초기화
if __name__ == '__main__':
    print("🚀 구직자 적합 전형 추천 API 서버 시작 (모델 분리 버전)")
    print("� 저장된 모델을 로딩합니다...")
    
    if initialize_model():
        model_info = model_loader.get_model_info()
        print("✅ 모델 로딩 완료")
        print(f"📋 모델 버전: {model_info['version']}")
        print(f"📊 총 {model_info['unique_forms']}개 전형 데이터 로드됨")
        print("🌐 서버 실행 중... (http://localhost:8080)")
        app.run(debug=False, host='0.0.0.0', port=8080)
    else:
        print("❌ 모델 초기화 실패")
        print("💡 먼저 model_builder.py를 실행하여 모델을 생성하세요.")
        print("   python model_builder.py")
