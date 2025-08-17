# MariaDB 연동 가이드

## 📋 개요
이 문서는 채용 전형 추천 시스템에서 MariaDB와 연동하는 방법을 설명합니다.

## 🗄️ 주요 기능
- **점수 데이터 조회**: MariaDB의 `scores` 테이블에서 전형별 점수 데이터 조회
- **추천 결과 저장**: 사용자의 추천 요청과 결과를 `recommendations` 테이블에 저장
- **통계 정보 제공**: 추천 이력 기반 통계 정보 제공
- **자동 폴백**: DB 연결 실패 시 샘플 데이터 자동 사용

## 📁 파일 구조
```
📦 MariaDB 연동 모듈
├── 📄 database_manager.py      # DB 연결 및 데이터 관리 클래스
├── 📄 mariadb_api_server.py    # MariaDB 기반 API 서버
├── 📄 setup_database.py       # DB 초기화 스크립트
├── 📄 .env                     # 환경변수 설정 파일
└── 📄 README_MariaDB.md        # 이 문서
```

## 🛠️ 설치 및 설정

### 1. MariaDB 설치
```bash
# macOS (Homebrew)
brew install mariadb
brew services start mariadb

# Ubuntu/Debian
sudo apt-get install mariadb-server
sudo systemctl start mariadb

# CentOS/RHEL
sudo yum install mariadb-server
sudo systemctl start mariadb
```

### 2. Python 패키지 설치
```bash
pip install pymysql==1.1.0
```

### 3. 데이터베이스 생성
```sql
CREATE DATABASE dive_recruit CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
CREATE USER 'dive_user'@'localhost' IDENTIFIED BY 'dive_password';
GRANT ALL PRIVILEGES ON dive_recruit.* TO 'dive_user'@'localhost';
FLUSH PRIVILEGES;
```

### 4. 환경변수 설정
```bash
# .env 파일 수정
export DB_HOST=localhost
export DB_PORT=3306
export DB_USER=dive_user
export DB_PASSWORD=dive_password
export DB_NAME=dive_recruit

# 환경변수 로드
source .env
```

## 🚀 시작하기

### 1. 데이터베이스 초기화
```bash
python setup_database.py
```

### 2. API 서버 실행
```bash
python mariadb_api_server.py
```

### 3. 연결 테스트
```bash
curl http://localhost:3001/health
```

## 📊 데이터베이스 스키마

### scores 테이블
```sql
CREATE TABLE scores (
    id INT AUTO_INCREMENT PRIMARY KEY,
    기관명 VARCHAR(100) NOT NULL,
    일반전형 VARCHAR(100) NOT NULL,
    성실성 INT CHECK (성실성 >= 1 AND 성실성 <= 5),
    개방성 INT CHECK (개방성 >= 1 AND 개방성 <= 5),
    외향성 INT CHECK (외향성 >= 1 AND 외향성 <= 5),
    우호성 INT CHECK (우호성 >= 1 AND 우호성 <= 5),
    정서안정성 INT CHECK (정서안정성 >= 1 AND 정서안정성 <= 5),
    기술전문성 INT CHECK (기술전문성 >= 1 AND 기술전문성 <= 5),
    인지문제해결 INT CHECK (인지문제해결 >= 1 AND 인지문제해결 <= 5),
    `대인-영향력` INT CHECK (`대인-영향력` >= 1 AND `대인-영향력` <= 5),
    자기관리 INT CHECK (자기관리 >= 1 AND 자기관리 <= 5),
    적응력 INT CHECK (적응력 >= 1 AND 적응력 <= 5),
    학습속도 INT CHECK (학습속도 >= 1 AND 학습속도 <= 5),
    대인민첩성 INT CHECK (대인민첩성 >= 1 AND 대인민첩성 <= 5),
    성과민첩성 INT CHECK (성과민첩성 >= 1 AND 성과민첩성 <= 5),
    자기인식 INT CHECK (자기인식 >= 1 AND 자기인식 <= 5),
    자기조절 INT CHECK (자기조절 >= 1 AND 자기조절 <= 5),
    `공감-사회기술` INT CHECK (`공감-사회기술` >= 1 AND `공감-사회기술` <= 5),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    UNIQUE KEY unique_form (기관명, 일반전형)
);
```

### recommendations 테이블
```sql
CREATE TABLE recommendations (
    id INT AUTO_INCREMENT PRIMARY KEY,
    session_id VARCHAR(100),
    user_scores JSON NOT NULL,
    recommendations JSON NOT NULL,
    profile_analysis JSON,
    model_version VARCHAR(50),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    INDEX idx_session_id (session_id),
    INDEX idx_created_at (created_at)
);
```

## 🌐 API 엔드포인트

### GET /scores
**점수 데이터 조회**
```bash
curl http://localhost:3001/scores
```

**응답 예시:**
```json
{
  "success": true,
  "total_count": 8,
  "data": [
    {
      "기관명": "부산교통공사",
      "일반전형": "운영직",
      "성실성": 4,
      "개방성": 3,
      ...
    }
  ],
  "message": "데이터베이스에서 점수 데이터 조회 성공"
}
```

### POST /scores
**점수 데이터 추가**
```bash
curl -X POST http://localhost:3001/scores \
  -H "Content-Type: application/json" \
  -d '{
    "기관명": "새로운기관",
    "일반전형": "새전형",
    "성실성": 4,
    "개방성": 3,
    ...
  }'
```

### POST /recommendations
**추천 결과 저장**
```bash
curl -X POST http://localhost:3001/recommendations \
  -H "Content-Type: application/json" \
  -d '{
    "session_id": "unique_session_123",
    "user_scores": {
      "성실성": 4,
      "개방성": 3,
      ...
    },
    "recommendations": [
      {
        "순위": 1,
        "전형명": "기계직",
        "적합도": 89.5
      }
    ]
  }'
```

### GET /recommendations
**추천 이력 조회**
```bash
# 전체 이력 조회
curl "http://localhost:3001/recommendations?limit=10"

# 특정 세션 이력 조회
curl "http://localhost:3001/recommendations?session_id=unique_session_123"
```

### GET /statistics
**통계 정보 조회**
```bash
curl http://localhost:3001/statistics
```

### GET /health
**상태 확인**
```bash
curl http://localhost:3001/health
```

## 🔄 모델 빌더와 연동

### 점수 데이터 API 사용
```bash
# MariaDB 기반 점수 API를 사용하여 모델 생성
python model_builder.py \
  --api-url http://localhost:3002/recruits \
  --scores-api-url http://localhost:3001/scores
```

### 추천 서비스 연동
```python
# app.py에서 추천 결과 자동 저장
import requests

def save_recommendation_to_db(session_id, user_scores, recommendations):
    try:
        response = requests.post('http://localhost:3001/recommendations', json={
            'session_id': session_id,
            'user_scores': user_scores,
            'recommendations': recommendations,
            'model_version': get_current_model_version()
        })
        return response.json()
    except Exception as e:
        logger.error(f"추천 결과 저장 실패: {e}")
        return None
```

## 🛡️ 오류 처리

### 연결 실패 시 자동 폴백
- DB 연결 실패 시 자동으로 샘플 데이터 사용
- API 응답에 `db_available` 필드로 상태 표시

### 로그 확인
```bash
# API 서버 로그 확인
python mariadb_api_server.py

# 데이터베이스 로그 확인
tail -f /var/log/mysql/error.log
```

## 📈 성능 최적화

### 인덱스 추가
```sql
-- 자주 조회되는 컬럼에 인덱스 추가
CREATE INDEX idx_scores_org_form ON scores (기관명, 일반전형);
CREATE INDEX idx_recommendations_session ON recommendations (session_id);
CREATE INDEX idx_recommendations_created ON recommendations (created_at);
```

### 연결 풀 설정
```python
# database_manager.py에서 연결 풀 사용
import pymysql.cursors
from pymysql import pooling

config = {
    'host': 'localhost',
    'user': 'dive_user',
    'password': 'dive_password',
    'database': 'dive_recruit',
    'charset': 'utf8mb4',
    'autocommit': True
}

pool = pooling.ConnectionPool(
    size=5,
    name='dive_pool',
    **config
)
```

## 🔧 트러블슈팅

### 일반적인 문제와 해결책

1. **연결 거부 오류**
   ```
   pymysql.err.OperationalError: (2003, "Can't connect to MySQL server")
   ```
   - MariaDB 서비스가 실행 중인지 확인
   - 방화벽 설정 확인
   - 호스트/포트 정보 확인

2. **인증 실패**
   ```
   pymysql.err.OperationalError: (1045, "Access denied for user")
   ```
   - 사용자명/비밀번호 확인
   - 사용자 권한 확인
   - 환경변수 설정 확인

3. **테이블 없음**
   ```
   pymysql.err.ProgrammingError: (1146, "Table 'dive_recruit.scores' doesn't exist")
   ```
   - `python setup_database.py` 실행
   - 수동으로 테이블 생성

4. **JSON 필드 오류**
   ```
   JSON 데이터 파싱 오류
   ```
   - MariaDB 10.2+ 버전 사용 확인
   - JSON 필드 형식 확인

## 🔒 보안 고려사항

1. **데이터베이스 보안**
   - 강력한 비밀번호 사용
   - 필요한 권한만 부여
   - SSL 연결 사용 권장

2. **API 보안**
   - 인증/인가 시스템 구현
   - 입력 데이터 검증
   - SQL 인젝션 방지

3. **환경변수 관리**
   - `.env` 파일을 git에 커밋하지 않음
   - 프로덕션에서는 시스템 환경변수 사용

## 📚 참고 자료

- [MariaDB 공식 문서](https://mariadb.org/documentation/)
- [PyMySQL 문서](https://pymysql.readthedocs.io/)
- [Flask 공식 문서](https://flask.palletsprojects.com/)
- [JSON 필드 사용법](https://mariadb.com/kb/en/json-data-type/)
