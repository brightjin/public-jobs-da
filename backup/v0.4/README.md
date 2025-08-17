# 구직자 적합 전형 추천 API 시스템 (v0.2)

## 📋 프로젝트 개요

이 프로젝트는 구직자의 16가지 능력 점수를 기반으로 가장 적합한 채용 전형을 추천해주는 REST API 시스템입니다.

**v0.2의 주요 개선사항:**
- 🔄 **모듈화 아키텍처**: 모델 빌드와 API 서비스 완전 분리
- 🚀 **동적 모델 업데이트**: 서비스 중단 없이 모델 리로드 가능
- 💾 **모델 영속성**: 훈련된 모델을 파일로 저장하여 재사용
- 🎯 **성능 최적화**: 모델 로딩 시간 단축 및 안정성 향상

## 🏗️ 시스템 아키텍### 👨‍💼 **채용담당자 워크플로우**

1. **새로운 채용 데이터 추가**
   ```bash
   # 방법 1: API 업데이트 (권장)
   # 1. http://mysite.com/recruits API에 새 전형 정보 추가
   # 2. 모델 재빌드 (API에서 최신 데이터 자동 조회)
   python3 model_builder.py --source api
   
   # 방법 2: CSV 업데이트
   # 1. data/all_data.csv에 새 전형 정보 추가
   # 2. 모델 재빌드
   python3 model_builder.py --source csv
   ```

2. **실시간 모델 업데이트**
   ```bash
   # 서비스 중단 없이 새 모델 적용
   curl -X POST http://localhost:8080/reload_model
   ```

3. **API 데이터 형식 예시**
   ```json
   [
     {
       "기관명": "부산교통공사",
       "공고명": "2025년 신입사원 채용",
       "일반전형": "운영직, 운전직, 기계직, 전기직",
       "채용인원": "120",
       "임용조건": "부산·울산·경남 거주",
       "기타_필드": "선택사항..."
     }
   ]
   ```───────────┐    ┌─────────────────┐    ┌─────────────────┐
│  REST API 데이터 │───▶│ model_builder.py │───▶│   저장된 모델   │
│ (채용정보 JSON)  │    │  (모델 생성)    │    │   (/models/)   │
└─────────────────┘    └─────────────────┘    └─────────────────┘
         │                       ▲                       │
         │                       │                       ▼
         │              ┌─────────────────┐    ┌─────────────────┐
         │              │   CSV 데이터    │    │ model_loader.py │
         │              │   (백업 소스)   │    │  (모델 로딩)   │
         │              └─────────────────┘    └─────────────────┘
         │                                              ▲
         ▼                                              │
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   구직자 요청   │───▶│     app.py      │◄───┘
│   (REST API)    │    │  (API 서버)     │
└─────────────────┘    └─────────────────┘

🔄 데이터 소스 우선순위: API → CSV (백업)
🌐 API URL: http://mysite.com/recruits (JSON 형태)
📁 백업: ./data/all_data.csv (CSV 형태)
```

## 🚀 주요 기능

### 🎯 **핵심 기능**
- **전형 추천**: 16가지 능력 점수 기반 맞춤형 전형 추천
- **프로필 분석**: 구직자 강점/약점 분석 및 개선점 제시
- **실시간 점수 검증**: 입력 데이터 유효성 검사

### 📊 **관리 기능**
- **동적 모델 업데이트**: `/reload_model` API로 실시간 모델 갱신
- **전형 목록 관리**: 전체 채용 전형 및 기관별 분류 조회
- **시스템 모니터링**: 헬스체크 및 모델 상태 확인

### 🔧 **개발자 도구**
- **모델 버전 관리**: 타임스탬프 기반 모델 버저닝
- **상세 로깅**: 모델 로딩 및 추천 과정 추적
- **에러 핸들링**: 상세한 오류 메시지 및 복구 가이드

## 📊 평가 항목 (16가지)

### 🧠 **인지 역량**
1. **성실성** - 책임감과 신뢰성
2. **개방성** - 새로운 경험에 대한 개방성  
3. **외향성** - 사교성과 활동성
4. **우호성** - 협조성과 친화성
5. **정서안정성** - 스트레스 관리와 감정 조절

### 💼 **업무 역량**
6. **기술전문성** - 전문 기술 역량
7. **인지문제해결** - 논리적 사고와 문제 해결
8. **대인-영향력** - 타인에게 영향을 미치는 능력
9. **자기관리** - 시간과 업무 관리
10. **적응력** - 변화에 대한 적응

### ⚡ **민첩성 역량**
11. **학습속도** - 새로운 지식 습득 속도
12. **대인민첩성** - 대인관계에서의 민첩성
13. **성과민첩성** - 성과 달성을 위한 민첩성

### 🎭 **감정지능**
14. **자기인식** - 자신에 대한 이해
15. **자기조절** - 자기 통제 능력
16. **공감-사회기술** - 타인 이해와 사회적 기술

**점수 범위**: 각 항목 1~5점 (1: 매우 낮음, 5: 매우 높음)

## 🛠 설치 및 실행

### 1. 환경 설정
```bash
# 가상환경 생성 (권장)
python3 -m venv .venv
source .venv/bin/activate  # macOS/Linux
# .venv\Scripts\activate     # Windows

# 의존성 설치
pip install flask flask-cors pandas numpy scikit-learn scipy requests
```

### 2. 모델 생성

#### 🌐 **API 모드 (권장)**
```bash
# 기본 API URL 사용
python3 model_builder.py --source api

# 커스텀 API URL 사용
python3 model_builder.py --source api --api-url http://your-api.com/recruits
```

#### 📂 **CSV 모드 (백업)**
```bash
# CSV 파일 사용
python3 model_builder.py --source csv

# 커스텀 CSV 파일 사용
python3 model_builder.py --source csv --csv-path ./data/custom_data.csv
```

**API 요구사항:**
- **엔드포인트**: `GET /recruits`
- **응답 형식**: JSON 배열 또는 `{"data": [...]}` 형태
- **필수 필드**: `기관명`, `일반전형` (기타 필드는 선택사항)

### 3. API 서버 실행
```bash
python3 app.py
```

서버는 `http://localhost:8080`에서 실행됩니다.

### 4. API 테스트
```bash
# 헬스체크
curl http://localhost:8080/health

# 전형 추천 테스트
curl -X POST http://localhost:8080/recommend \
  -H "Content-Type: application/json" \
  -d '{"scores": {"성실성": 4, "개방성": 3, ...}, "top_n": 3}'

# 모델 동적 리로드 (새 채용 데이터 반영)
curl -X POST http://localhost:8080/reload_model
```

## 📡 API 엔드포인트

### 🏠 **기본 정보**
- **GET /** - API 홈페이지 및 전체 상태 확인
- **GET /health** - 시스템 및 모델 상태 확인

### 🎯 **추천 서비스**
- **POST /recommend** - 구직자 전형 추천 (핵심 기능)

**요청 예시:**
```json
{
  "scores": {
    "성실성": 4,
    "개방성": 3,
    "외향성": 2,
    "우호성": 3,
    "정서안정성": 4,
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
  "top_n": 5
}
```

**응답 예시:**
```json
{
  "success": true,
  "recommendations": [
    {
      "순위": 1,
      "전형명": "공무직(UIS)",
      "적합도": 67.4,
      "코사인유사도": 0.974,
      "거리기반유사도": 0.224
    }
  ],
  "profile_analysis": {
    "강점_항목": [
      {"항목": "기술전문성", "점수": 5},
      {"항목": "인지문제해결", "점수": 5},
      {"항목": "학습속도", "점수": 5}
    ],
    "개선_항목": [
      {"항목": "외향성", "점수": 2},
      {"항목": "대인-영향력", "점수": 2},
      {"항목": "대인민첩성", "점수": 2}
    ],
    "평균_점수": 3.5
  },
  "request_info": {
    "model_version": "v20250816_013610",
    "top_n": 5,
    "total_forms": 127
  }
}
```

### 📋 **데이터 조회**
- **GET /forms** - 전체 채용 전형 목록 조회
- **GET /categories** - 16가지 평가 항목 및 설명 조회

### 🔄 **관리 기능**
- **POST /reload_model** - 모델 동적 리로드 (데이터 업데이트 후 사용)

## 🧪 테스트 예시

### curl을 사용한 API 호출
```bash
# 전형 추천
curl -X POST http://localhost:8080/recommend \
  -H "Content-Type: application/json" \
  -d '{
    "scores": {
      "성실성": 4,
      "개방성": 3,
      "외향성": 2,
      "우호성": 3,
      "정서안정성": 4,
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
    "top_n": 3
  }'

# 서비스 상태 확인
curl http://localhost:8080/health

# 전형 목록 조회
curl http://localhost:8080/forms

# 모델 리로드
curl -X POST http://localhost:8080/reload_model
```

## 🔍 분석 모델

### 🧮 **추천 알고리즘**
- **코사인 유사도** (60%): 구직자와 전형 간의 패턴 유사성 측정
- **유클리드 거리 기반 유사도** (40%): 절대적 점수 차이 기반 유사성 측정
- **종합 적합도**: 두 지표를 가중평균하여 0-100점으로 정규화

### 📈 **전형별 특성화**
- **운영직/사무직**: 성실성, 자기관리, 대인-영향력, 공감-사회기술 중시
- **기술직**: 기술전문성, 인지문제해결, 학습속도, 자기관리 중시  
- **운전직**: 성실성, 정서안정성, 적응력, 자기관리 중시
- **공무직**: 성실성, 기술전문성, 자기관리 중시
- **경비직**: 성실성, 정서안정성, 우호성, 자기관리 중시

### 🎯 **모델 성능**
- **현재 버전**: v20250816_013610
- **전형 수**: 127개
- **기관 수**: 5개
- **데이터 레코드**: 141개

## 📁 파일 구조

```
dive-da/
├── 🚀 주요 파일
│   ├── model_builder.py    # 모델 생성 및 저장 (API/CSV 연동)
│   ├── model_loader.py     # 모델 로딩 및 추천 서비스
│   ├── app.py              # Flask REST API 서버
│   ├── test_api_server.py  # 테스트용 채용 데이터 API 서버
│   └── dive.py             # 원본 분석 스크립트 (참고용)
│
├── 📊 데이터
│   ├── data/
│   │   ├── all_data.csv    # 원본 채용 데이터 (CSV 백업)
│   │   └── api_sample.json # API 응답 샘플 데이터
│   └── models/             # 저장된 모델 파일들
│       ├── form_profiles.pkl    # 전형별 프로파일
│       ├── scores_data.pkl      # 점수 데이터  
│       ├── model_info.json      # 모델 메타데이터 (API/CSV 출처 포함)
│       └── forms_data.json      # 전형 목록
│
├── 📋 문서
│   └── README.md           # 프로젝트 설명서
│
└── 🗂️ 백업
    └── backup/
        ├── v0.1/           # 이전 버전 백업
        └── v0.2/           # 현재 버전 백업
```

## ⚡ 사용 시나리오

### �‍💼 **채용담당자 워크플로우**

1. **새로운 채용 데이터 추가**
   ```bash
   # 1. data/all_data.csv에 새 전형 정보 추가
   # 2. 모델 재빌드
   python3 model_builder.py
   ```

2. **실시간 모델 업데이트**
   ```bash
   # 서비스 중단 없이 새 모델 적용
   curl -X POST http://localhost:8080/reload_model
   ```

### 👨‍💻 **개발자 워크플로우**

1. **개발 환경 설정**
   ```bash
   git clone [repo]
   cd dive-da
   python3 -m venv .venv
   source .venv/bin/activate
   pip install flask flask-cors pandas numpy scikit-learn scipy requests
   ```

2. **모델 생성 (데이터 소스 선택)**
   ```bash
   # API 모드 (권장)
   python3 model_builder.py --source api --api-url http://mysite.com/recruits
   
   # CSV 모드 (백업)
   python3 model_builder.py --source csv
   ```

3. **API 서버 실행**
   ```bash
   python3 app.py
   ```

4. **로컬 테스트 API 서버** (개발용)
   ```bash
   # 테스트용 API 서버 실행 (포트 3000)
   python3 test_api_server.py
   
   # 테스트 API로 모델 빌드
   python3 model_builder.py --source api --api-url http://localhost:3000/recruits
   ```

### 🔍 **API 사용자 워크플로우**

1. **구직자 능력 평가** → 16가지 항목 점수 수집
2. **API 호출** → `/recommend` 엔드포인트로 점수 전송  
3. **결과 활용** → 추천 전형 및 프로필 분석 결과 활용

### 🌐 **API 연동 개발자 가이드**

1. **채용 데이터 API 구현**
   ```python
   # 예시: Flask 기반 채용 데이터 API
   @app.route('/recruits', methods=['GET'])
   def get_recruits():
       return jsonify([
           {
               "기관명": "기관명",
               "일반전형": "전형1, 전형2, 전형3",
               "기타필드": "선택사항..."
           }
       ])
   ```

2. **API 응답 형식 요구사항**
   - **Content-Type**: `application/json`
   - **구조**: JSON 배열 또는 `{"data": [...]}` 형태
   - **필수 필드**: `기관명`, `일반전형`
   - **일반전형**: 쉼표(,)로 구분된 전형명 목록

3. **API 오류 처리**
   - API 호출 실패 시 자동으로 CSV 백업 사용
   - 타임아웃: 30초
   - 재시도 로직: CSV 파일로 대체

## 🚀 프로덕션 배포

### 🔧 **Gunicorn 사용 (권장)**
```bash
pip install gunicorn
gunicorn -w 4 -b 0.0.0.0:8080 --timeout 60 app:app
```

### � **Docker 배포**
```dockerfile
FROM python:3.9-slim

WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt

COPY . .
RUN python3 model_builder.py

EXPOSE 8080
CMD ["gunicorn", "-w", "4", "-b", "0.0.0.0:8080", "app:app"]
```

### ☁️ **클라우드 배포 고려사항**
- **모델 파일 크기**: `models/` 디렉토리 포함 필수
- **메모리 요구사항**: 최소 512MB 권장
- **스토리지**: 모델 업데이트를 위한 persistent volume 필요

## 🔧 개발 및 확장

### 📈 **성능 모니터링**
```bash
# API 응답시간 확인
curl -w "%{time_total}\n" -o /dev/null -s http://localhost:8080/health

# 모델 메모리 사용량 확인
python3 -c "import model_loader; print('모델 로딩 완료')"
```

### 🎯 **커스터마이징 가이드**

1. **새로운 평가 항목 추가**: `model_builder.py`의 `score_columns` 수정
2. **추천 알고리즘 조정**: `model_loader.py`의 가중치 변경
3. **API 엔드포인트 추가**: `app.py`에 새로운 라우트 정의

### 🧪 **테스트 및 검증**
```bash
# 모델 정확도 테스트
python3 -c "
import model_loader
loader = model_loader.JobRecommendationModelLoader()
loader.load_model()
# 테스트 케이스 실행...
"
```

## 📞 문의 및 지원

- **버그 리포트**: GitHub Issues
- **기능 요청**: Feature Request
- **기술 문의**: 개발팀 연락처

## 📜 버전 히스토리

### v0.2.1 (2025-08-16) - API 연동 업데이트
- ✅ **REST API 연동**: http://mysite.com/recruits 에서 JSON 형태 채용 데이터 조회
- ✅ **자동 백업**: API 실패 시 CSV 파일로 자동 대체
- ✅ **유연한 데이터 소스**: --source 옵션으로 API/CSV 선택 가능
- ✅ **테스트 도구**: 로컬 테스트 API 서버 (test_api_server.py) 제공
- ✅ **개선된 모델 메타데이터**: 데이터 출처 정보 추가

### v0.2 (2025-08-16)
- ✅ 모듈화 아키텍처 도입
- ✅ 동적 모델 리로드 기능
- ✅ 모델 영속성 및 버전 관리
- ✅ 개선된 에러 핸들링
- ✅ 상세한 API 문서화

### v0.1 (Initial Release)
- ✅ 기본 추천 알고리즘
- ✅ REST API 구현
- ✅ 16가지 평가 항목 정의
- ✅ 코사인 유사도 + 유클리드 거리 알고리즘

---

**🎯 이 시스템은 구직자와 채용 전형 간의 최적 매칭을 통해 채용 효율성을 극대화합니다.**
**🌐 v0.2.1부터 REST API 연동으로 실시간 채용 데이터 업데이트를 지원합니다.**
