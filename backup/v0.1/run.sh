#!/bin/bash

echo "🚀 구직자 적합 전형 추천 API 시스템"
echo "================================="

# 가상환경 활성화 확인
if [[ "$VIRTUAL_ENV" == "" ]]; then
    echo "📦 가상환경 활성화 중..."
    source .venv/bin/activate
fi

# 필요한 패키지 설치 확인
echo "🔍 의존성 패키지 확인 중..."
pip install -q -r requirements.txt

echo "✅ 준비 완료!"
echo ""

# 메뉴 선택
echo "실행할 작업을 선택하세요:"
echo "1) API 서버 실행"
echo "2) API 테스트"
echo "3) 서버 상태 확인"
echo "4) 종료"
echo ""

read -p "선택 (1-4): " choice

case $choice in
    1)
        echo "🌐 API 서버를 시작합니다..."
        echo "서버 주소: http://localhost:8080"
        echo "종료하려면 Ctrl+C를 누르세요."
        echo ""
        python app.py
        ;;
    2)
        echo "🧪 API 테스트를 실행합니다..."
        python test_api.py
        ;;
    3)
        echo "🔍 서버 상태를 확인합니다..."
        curl -s http://localhost:8080/health | python -m json.tool 2>/dev/null || echo "❌ 서버가 실행되지 않았거나 응답하지 않습니다."
        ;;
    4)
        echo "👋 종료합니다."
        exit 0
        ;;
    *)
        echo "❌ 잘못된 선택입니다."
        exit 1
        ;;
esac
