#!/bin/bash

echo "🚀 유사도 기반 채용공고 추천 시스템"
echo "================================="

# 가상환경 활성화 확인
if [[ "$VIRTUAL_ENV" == "" ]]; then
    echo "📦 가상환경 활성화 중..."
    source .venv/bin/activate
fi

# 환경변수 로드
if [ -f .env ]; then
    echo "🔧 환경변수 로드 중..."
    source .env
fi

# 필요한 패키지 설치 확인
echo "🔍 의존성 패키지 확인 중..."
pip install -q -r requirements.txt

echo "✅ 준비 완료!"
echo ""

# 메뉴 선택
echo "실행할 작업을 선택하세요:"
echo "1) 추천 API 서버 실행"
echo "2) 모델 생성/업데이트"
echo "3) 데이터베이스 테이블 생성"
echo "4) 추천 시스템 테스트"
echo "5) API 서버 상태 확인"
echo "6) 종료"
echo ""

read -p "선택 (1-6): " choice

case $choice in
    1)
        echo "🌐 추천 API 서버를 시작합니다..."
        echo "서버 주소: http://localhost:8080"
        echo "종료하려면 Ctrl+C를 누르세요."
        echo ""
        python job_recommendation_api.py
        ;;
    2)
        echo "🤖 유사도 모델을 생성/업데이트합니다..."
        python model_builder.py --source database
        ;;
    3)
        echo "🗄️ 데이터베이스 테이블을 생성합니다..."
        python create_job_posting_scores_table.py
        ;;
    4)
        echo "🧪 추천 시스템 테스트를 실행합니다..."
        python test_recommendation_system.py
        ;;
    5)
        echo "🔍 API 서버 상태를 확인합니다..."
        curl -s http://localhost:8080/health | python -m json.tool 2>/dev/null || echo "❌ 서버가 실행되지 않았거나 응답하지 않습니다."
        ;;
    6)
        echo "👋 종료합니다."
        exit 0
        ;;
    *)
        echo "❌ 잘못된 선택입니다."
        exit 1
        ;;
esac
