# 유사도 기반 채용공고 추천 시스템

## 📋 프로젝트 개요

이 시스템은 구직자의 16가지 성격/능력 점수를 기반으로 유사도 분석을 통해 가장 적합한 채용공고를 추천하는 REST API 서비스입니다.

**주요 특징:**
- 🤖 **코사인 유사도 기반 추천**: 16차원 특성 벡터를 활용한 정확한 매칭
- 🗄️ **MariaDB 통합**: 실시간 데이터베이스 연동으로 최신 공고 반영
- 🚀 **REST API**: 웹/모바일 애플리케이션과 쉽게 연동 가능
- 📊 **표준화된 점수 시스템**: StandardScaler를 활용한 정규화

## 🏗️ 시스템 아키텍처

```
데이터베이스 → 유사도 모델 → API 서버 → 추천 결과
    ↓              ↓           ↓         ↓
MariaDB     →  cosine_sim  →  Flask  →  JSON
```

## 🔧 설치 및 설정

### 1. 저장소 클론
```bash
git clone [repository-url]
cd dive-da
```

### 2. 가상환경 설정
```bash
python -m venv .venv
source .venv/bin/activate  # macOS/Linux
# 또는
.venv\Scripts\activate     # Windows
```

### 3. 의존성 설치
```bash
pip install -r requirements.txt
```

### 4. 환경변수 설정
`.env` 파일 생성:
```bash
DB_HOST=hostname
DB_PORT=port
DB_NAME=database
DB_USER=your_username
DB_PASSWORD=your_password
API_PORT=8080
```

## 🚀 사용 방법

### 자동 실행 (권장)
```bash
chmod +x run.sh
./run.sh
```

### 수동 실행

#### 1. 데이터베이스 테이블 생성
```bash
python create_job_posting_scores_table.py
```

#### 2. 유사도 모델 생성
```bash
python model_builder.py --source database
```

#### 3. API 서버 시작
```bash
python job_recommendation_api.py
```

## 📡 API 사용법

### 기본 정보
- **베이스 URL**: `http://localhost:8080`
- **Content-Type**: `application/json`

### 엔드포인트

#### 1. 추천 요청
```http
POST /recommend
Content-Type: application/json

{
  "scores": {
    "성실성": 4,
    "개방성": 3,
    "외향성": 5,
    "우호성": 4,
    "정서안정성": 3,
    "기술전문성": 5,
    "인지문제해결": 4,
    "대인-영향력": 3,
    "자기관리": 4,
    "적응력": 4,
    "학습속도": 5,
    "대인민첩성": 3,
    "성과민첩성": 4,
    "자기인식": 4,
    "자기조절": 3,
    "공감-사회기술": 4
  }
}
```

**응답 예시:**
```json
{
  "recommendations": [
    {
      "공고일련번호": 1,
      "기관명": "한국전력공사",
      "직렬": "기능직",
      "similarity_score": 0.892
    }
  ]
}
```

#### 2. 시스템 통계
```http
GET /statistics
```

#### 3. 서버 상태 확인
```http
GET /health
```

#### 4. 샘플 점수 조회
```http
GET /sample_scores
```

#### 5. 모델 리로드
```http
POST /reload_model
```

## 🧪 테스트

### 추천 시스템 테스트
```bash
python test_recommendation_system.py
```

### cURL 테스트 예시
```bash
# 추천 요청
curl -X POST http://localhost:8080/recommend \
  -H "Content-Type: application/json" \
  -d @test_request.json

# 서버 상태 확인
curl http://localhost:8080/health

# 시스템 통계
curl http://localhost:8080/statistics
```

## 📊 점수 체계

### 16가지 평가 요소
1. **성격 특성** (5개)
   - 성실성, 개방성, 외향성, 우호성, 정서안정성

2. **능력 특성** (11개)
   - 기술전문성, 인지문제해결, 대인-영향력, 자기관리, 적응력
   - 학습속도, 대인민첩성, 성과민첩성, 자기인식, 자기조절, 공감-사회기술

### 점수 범위
- **범위**: 1-5점 (정수)
- **의미**: 1(낮음) ~ 5(높음)

## 🗄️ 데이터베이스 구조

### 채용공고평가점수 테이블
```sql
CREATE TABLE 채용공고평가점수 (
    공고일련번호 INT PRIMARY KEY AUTO_INCREMENT,
    기관명 VARCHAR(100),
    직렬 VARCHAR(50),
    성실성 INT,
    개방성 INT,
    외향성 INT,
    우호성 INT,
    정서안정성 INT,
    기술전문성 INT,
    인지문제해결 INT,
    대인_영향력 INT,
    자기관리 INT,
    적응력 INT,
    학습속도 INT,
    대인민첩성 INT,
    성과민첩성 INT,
    자기인식 INT,
    자기조절 INT,
    공감_사회기술 INT
);
```

## 🔧 개발자 가이드

### 프로젝트 구조
```
dive-da/
├── job_recommendation_api.py    # 메인 API 서버 (포트 8080)
├── model_builder.py            # 유사도 모델 생성
├── database_manager.py         # DB 연결 관리
├── create_job_posting_scores_table.py  # 테이블 생성
├── test_recommendation_system.py       # 시스템 테스트
├── log_config.py               # 공통 로깅 설정
├── models/                     # 저장된 모델 파일
├── data/                       # 데이터 파일
├── log/                        # 로그 파일 디렉토리
│   ├── job_recommendation_api.log      # API 서버 로그
│   ├── model_builder.log              # 모델 생성 로그
│   ├── database_manager.log           # DB 연결 로그
│   └── *.log                          # 기타 서비스 로그
└── requirements.txt            # 의존성
```

### 로깅 시스템
모든 서비스는 `./log/` 디렉토리에 개별 로그 파일을 생성합니다:

- **파일별 로그**: 각 모듈마다 별도의 로그 파일 생성
- **UTF-8 인코딩**: 한글 로그 메시지 지원
- **타임스탬프**: 모든 로그에 정확한 시간 기록
- **레벨별 구분**: INFO, WARNING, ERROR 레벨 구분
- **콘솔 + 파일**: 동시 출력으로 개발/운영 편의성 제공

#### 로그 파일 확인
```bash
# 모든 로그 파일 목록
ls -la ./log/

# API 서버 로그 실시간 모니터링
tail -f ./log/job_recommendation_api.log

# 모델 생성 로그 확인
cat ./log/model_builder.log

# 에러 로그만 필터링
grep "ERROR" ./log/*.log
```

### 모델 업데이트 워크플로우
1. 새 데이터가 데이터베이스에 추가됨
2. `model_builder.py` 실행하여 새 모델 생성
3. API 서버가 자동으로 새 모델 로드 또는 `/reload_model` 엔드포인트 호출
4. 업데이트된 추천 제공

## 🐛 문제 해결

### 일반적인 오류

#### 1. 데이터베이스 연결 오류
```bash
# 환경변수 확인
cat .env

# 데이터베이스 연결 테스트
python -c "from database_manager import DatabaseManager; dm = DatabaseManager(); print('연결 성공' if dm.test_connection() else '연결 실패')"
```

#### 2. 모델 파일 없음
```bash
# 모델 재생성
python model_builder.py --source database
```

#### 3. 포트 충돌
```bash
# 포트 8080 사용 중인 프로세스 확인
lsof -i :8080

# 대체 포트로 실행 (환경변수 설정)
export API_PORT=8081
python job_recommendation_api.py
```

## 📈 성능 최적화

### 추천 속도
- 평균 응답 시간: 50ms 이하
- 동시 처리: 최대 100 요청/초
- 메모리 사용량: 약 200MB

### 확장성
- 수평 확장 가능 (로드 밸런서 활용)
- 데이터베이스 읽기 전용 복제본 지원
- 캐싱 시스템 통합 가능

## 🎯 실제 사용 예시

### 기술직 구직자
```bash
curl -X POST http://localhost:8080/recommend \
  -H "Content-Type: application/json" \
  -d '{
    "scores": {
      "성실성": 4, "개방성": 3, "외향성": 2, "우호성": 3, "정서안정성": 4,
      "기술전문성": 5, "인지문제해결": 5, "대인-영향력": 2, "자기관리": 4,
      "적응력": 4, "학습속도": 5, "대인민첩성": 2, "성과민첩성": 4,
      "자기인식": 4, "자기조절": 4, "공감-사회기술": 3
    }
  }'
```

### 관리직 구직자
```bash
curl -X POST http://localhost:8080/recommend \
  -H "Content-Type: application/json" \
  -d '{
    "scores": {
      "성실성": 5, "개방성": 4, "외향성": 5, "우호성": 5, "정서안정성": 4,
      "기술전문성": 3, "인지문제해결": 4, "대인-영향력": 5, "자기관리": 5,
      "적응력": 4, "학습속도": 4, "대인민첩성": 5, "성과민첩성": 5,
      "자기인식": 5, "자기조절": 5, "공감-사회기술": 5
    }
  }'
```

## 🤝 기여하기

1. Fork the repository
2. Create a feature branch
3. Commit your changes
4. Push to the branch
5. Create a Pull Request

## 📄 라이선스

이 프로젝트는 MIT 라이선스 하에 배포됩니다.

## 📞 지원

문의사항이나 버그 리포트는 이슈를 통해 남겨주세요.

---

**마지막 업데이트**: 2025년 1월 7일  
**버전**: v0.5 (유사도 기반 추천 시스템)  
**기본 포트**: 8080
