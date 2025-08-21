# 유사도 기반 채용공고 추천 시스템

## 📋 프로젝트 개요

구직자의 16가지 성격/능력 점수를 기반으로 유사도 분석을 통해 가장 적합한 채용공고를 추천하는 REST API 서비스입니다.

**주요 특징:**
- 🤖 **코사인 유사도 기반 추천**: 16차원 특성 벡터를 활용한 정확한 매칭
- 🗄️ **MariaDB 연동**: 실시간 데이터베이스 반영
- 🚀 **REST API**: 웹/모바일 연동
- 📊 **표준화된 점수 시스템**: StandardScaler 활용
- 🏷️ **일반전형별 일관성**: 같은 전형은 비슷한 점수로 생성

## 🏗️ 시스템 아키텍처

```
MariaDB → 점수 테이블 → 모델 빌더 → API 서버 → 추천 결과
```

## 🔧 설치 및 설정

### 1. 저장소 클론
```bash
git clone [repository-url]
cd public-jobs-da
```

### 2. 가상환경 설정
```bash
python -m venv .venv
source .venv/bin/activate  # macOS/Linux
.venv\Scripts\activate   # Windows
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
API_PORT=8888
```

## 🚀 실행 방법

### 자동 실행 (권장)
```bash
chmod +x run.sh
./run.sh
```

### 수동 실행
1. 점수 테이블 생성
   ```bash
   python create_job_posting_scores_table.py
   ```
2. 유사도 모델 생성
   ```bash
   python model_builder.py --source database
   ```
3. API 서버 시작
   ```bash
   python job_recommendation_api.py
   ```

## 📡 API 사용법

- **Base URL**: `http://localhost:8888`
- **Content-Type**: `application/json`

### 엔드포인트

#### 1. 추천 요청
```http
POST /recommend
Content-Type: application/json
{
  "user_scores": {
    "성실성": 4, "개방성": 3, ... (16개 점수)
  },
  "top_k": 5
}
```

**응답 예시:**
```json
{
  "success": true,
  "user_scores": {...},
  "recommendations": [
    {
      "rank": 1,
      "id": 123,
      "기관명": "부산교통공사",
      "일반전형": "운영직",
      "유사도": 0.581,
      "공고점수": {"성실성": 4, ...}
    }
  ],
  "total_count": 5
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

## 📊 점수 체계

- **16가지 평가 요소**: 성실성, 개방성, 외향성, 우호성, 정서안정성, 기술전문성, 인지문제해결, 대인영향력, 자기관리, 적응력, 학습속도, 대인민첩성, 성과민첩성, 자기인식, 자기조절, 공감사회기술
- **점수 범위**: 1~5 (정수)
- **일반전형별 기준점수 + ±1 변동**: 같은 전형은 비슷한 점수

## 🗄️ 데이터베이스 구조

### TMP_채용공고평가점수 테이블
```sql
CREATE TABLE TMP_채용공고평가점수 (
    id INT PRIMARY KEY AUTO_INCREMENT,
    기관명 VARCHAR(255),
    공고명 TEXT,
    일반전형 VARCHAR(500),
    성실성 INT, 개방성 INT, 외향성 INT, 우호성 INT, 정서안정성 INT,
    기술전문성 INT, 인지문제해결 INT, 대인영향력 INT, 자기관리 INT, 적응력 INT,
    학습속도 INT, 대인민첩성 INT, 성과민첩성 INT, 자기인식 INT, 자기조절 INT, 공감사회기술 INT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

## 🔧 주요 파일 구조
```
public-jobs-da/
├── create_job_posting_scores_table.py  # 점수 테이블 생성
├── model_builder.py                    # 유사도 모델 생성
├── job_recommendation_api.py           # 추천 API 서버
├── scores_manager.py                   # 점수 관리 모듈
├── recommendations_manager.py          # 추천 관리 모듈
├── database_manager.py                 # DB 연결 관리
├── log_config.py                       # 로깅 설정
├── run.sh                              # 자동 실행 스크립트
├── models/                             # 생성된 모델 파일
├── data/                               # 데이터 파일
├── log/                                # 로그 파일
└── requirements.txt                    # 의존성
```

## 🐛 문제 해결

- DB 연결 오류: .env 환경변수 확인, DB 서버 상태 점검
- 모델 파일 없음: model_builder.py 재실행
- 포트 충돌: lsof -i :8080, 환경변수로 포트 변경
- 점수 불일치: create_job_posting_scores_table.py 재실행

## 📈 성능 및 확장성

- 평균 응답 시간: 50ms 이하
- 동시 처리: 최대 100 요청/초
- 수평 확장 가능, 캐싱 시스템 연동 가능

## 🤝 기여 방법

1. Fork → Branch 생성 → Commit → PR 제출

## 📄 라이선스
MIT

## 📞 지원
이슈로 문의 또는 버그 리포트

---
**마지막 업데이트**: 2025년 8월 20일
**버전**: v0.6 (일반전형별 일관성 점수, TMP_채용공고평가점수 기반)
**기본 포트**: 8888
