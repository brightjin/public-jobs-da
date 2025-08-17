# CSV 테이블 생성 스크립트

## 📋 개요
이 디렉토리는 CSV 파일들을 MariaDB 테이블로 자동 변환하는 스크립트들을 포함합니다.

## 📁 파일 구조
```
📦 ./data/
├── 📄 all_data.csv              # 채용 정보 데이터
├── 📄 competition_rate.csv      # 채용 경쟁률 현황
├── 📄 new_recruit.csv           # 신규 채용인원 현황
├── 📄 api_sample.json           # API 샘플 데이터
├── 🔧 analyze_csv.py            # CSV 파일 분석 및 스키마 미리보기
├── 🔧 create_tables_from_csv.py # CSV → MariaDB 테이블 자동 생성
├── 🔧 manage_tables.py          # 생성된 테이블 관리 유틸리티
└── 📄 README.md                 # 이 문서
```

## 🚀 사용 방법

### 1단계: CSV 파일 분석 (선택사항)
```bash
cd ./data
python analyze_csv.py
```
**기능:**
- 각 CSV 파일의 구조 분석
- MySQL 데이터 타입 자동 추론
- CREATE TABLE SQL 미리보기
- 데이터 품질 분석 (NULL 비율, 중복 행 등)

### 2단계: 테이블 생성
```bash
cd ./data
python create_tables_from_csv.py
```
**기능:**
- 모든 CSV 파일을 자동으로 MariaDB 테이블로 변환
- 컬럼명 자동 정리 (MySQL 호환)
- 데이터 타입 자동 추론 및 적용
- 자동 인덱스 생성 (ID, created_at, updated_at)

### 3단계: 테이블 관리
```bash
cd ./data

# 대화형 모드
python manage_tables.py

# 명령행 모드
python manage_tables.py list                    # 테이블 목록
python manage_tables.py structure all_data      # 테이블 구조 확인
python manage_tables.py data all_data 20        # 데이터 조회 (20개)
python manage_tables.py stats all_data          # 통계 정보
python manage_tables.py export ./backup/        # 모든 테이블을 CSV로 내보내기
```

## 📊 생성되는 테이블

### 1. all_data 테이블
**설명:** 채용 정보 데이터
```sql
CREATE TABLE all_data (
    id INT AUTO_INCREMENT PRIMARY KEY,
    기관명 VARCHAR(100) NOT NULL,
    공고명 VARCHAR(255),
    공고시작일 DATE,
    공고마감일 DATE,
    접수시작일 DATE,
    접수마감일 DATE,
    접수방법 VARCHAR(100),
    접수대행 VARCHAR(255),
    일반전형 TEXT,
    채용인원 VARCHAR(100),
    채용방법 VARCHAR(255),
    전형방법 TEXT,
    임용시기 VARCHAR(100),
    임용조건 VARCHAR(255),
    담당부서 VARCHAR(100),
    연락처 VARCHAR(100),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
);
```

### 2. competition_rate 테이블
**설명:** 채용 경쟁률 현황
```sql
CREATE TABLE competition_rate (
    id INT AUTO_INCREMENT PRIMARY KEY,
    기관명 VARCHAR(100) NOT NULL,
    연도 YEAR,
    구분 VARCHAR(255),
    전형 VARCHAR(100),
    직렬_업무분야_ VARCHAR(100),
    선발인원 INT,
    지원인원 INT,
    필기_합격선 DECIMAL(10,2),
    경쟁률 VARCHAR(50),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
);
```

### 3. new_recruit 테이블
**설명:** 신규 채용인원 현황
```sql
CREATE TABLE new_recruit (
    id INT AUTO_INCREMENT PRIMARY KEY,
    기관명 VARCHAR(100) NOT NULL,
    연도 YEAR,
    정규직_일반_ INT,
    정규직_장애_ INT,
    공무직 INT,
    인턴_일반_ INT,
    인턴_장애인_ INT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
);
```

## 🔧 스크립트별 상세 기능

### analyze_csv.py
- **목적:** 테이블 생성 전 미리보기
- **기능:**
  - CSV 파일 구조 분석
  - 데이터 타입 자동 추론
  - NULL 비율 및 데이터 품질 분석
  - CREATE TABLE SQL 미리보기
  - SQL 스크립트 파일 생성

### create_tables_from_csv.py
- **목적:** 실제 테이블 생성 및 데이터 삽입
- **기능:**
  - 자동 컬럼명 정리 (특수문자 → 언더스코어)
  - MySQL 호환 데이터 타입 자동 변환
  - 날짜 데이터 자동 파싱
  - 중복 실행 시 데이터 재삽입
  - 에러 발생 시 개별 행 스킵

### manage_tables.py
- **목적:** 생성된 테이블 관리 및 조회
- **기능:**
  - 테이블 목록 및 구조 확인
  - 데이터 샘플 조회
  - 통계 정보 (레코드 수, 테이블 크기 등)
  - CSV 내보내기
  - 대화형 탐색 모드

## 🛠️ 환경 설정

### 1. 필수 패키지 설치
```bash
pip install pandas pymysql
```

### 2. 환경변수 설정
`.env` 파일에서 데이터베이스 연결 정보 설정:
```bash
export DB_HOST=158.247.213.167
export DB_PORT=3306
export DB_USER=root
export DB_PASSWORD=your_password
export DB_NAME=dive_recruit
```

### 3. 데이터베이스 생성
```sql
CREATE DATABASE dive_recruit CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
```

## 📈 데이터 타입 매핑 규칙

| CSV 데이터 특성 | MySQL 타입 | 예시 |
|----------------|------------|------|
| 정수 (0-255) | TINYINT UNSIGNED | 나이, 점수 |
| 정수 (큰 범위) | INT | ID, 인원수 |
| 소수점 | DECIMAL(10,2) | 점수, 비율 |
| 연도 | YEAR | 2020, 2021 |
| 날짜 | DATE | 2020-01-15 |
| 짧은 문자열 (<50자) | VARCHAR(100) | 기관명, 전형명 |
| 긴 문자열 (>255자) | TEXT | 상세 설명 |

## 🚨 주의사항

1. **데이터 백업:** 기존 테이블이 있으면 데이터가 삭제되고 재삽입됩니다.
2. **컬럼명 변경:** 특수문자가 포함된 컬럼명은 언더스코어로 변경됩니다.
3. **인코딩:** UTF-8, CP949, EUC-KR 순으로 자동 감지 시도합니다.
4. **NULL 처리:** NULL 비율이 10% 미만인 컬럼은 NOT NULL로 설정됩니다.

## 💡 활용 예시

### 채용 데이터 조회
```sql
-- 기관별 채용 정보
SELECT 기관명, COUNT(*) as 공고수, 
       GROUP_CONCAT(DISTINCT 일반전형) as 전형목록
FROM all_data 
GROUP BY 기관명;

-- 연도별 경쟁률 추이
SELECT 연도, AVG(지원인원/선발인원) as 평균경쟁률
FROM competition_rate 
GROUP BY 연도 
ORDER BY 연도;

-- 신규 채용 트렌드
SELECT 연도, SUM(정규직_일반_ + 정규직_장애_) as 정규직합계
FROM new_recruit 
GROUP BY 연도 
ORDER BY 연도;
```

### API 연동 활용
```python
# 생성된 테이블을 API에서 활용
from database_manager import DatabaseManager

with DatabaseManager() as db:
    # 모든 채용 정보 조회
    cursor.execute("SELECT * FROM all_data")
    recruits = cursor.fetchall()
    
    # 경쟁률 정보 조회
    cursor.execute("SELECT * FROM competition_rate WHERE 연도 = 2023")
    rates = cursor.fetchall()
```

## 🔗 관련 파일들

- **`../database_manager.py`**: 데이터베이스 연결 관리
- **`../mariadb_api_server.py`**: MariaDB 기반 API 서버
- **`../.env`**: 환경변수 설정
- **`../README_MariaDB.md`**: MariaDB 연동 가이드

## 📞 문제 해결

### 일반적인 오류와 해결책

1. **"Module not found" 오류**
   ```bash
   pip install pandas pymysql
   ```

2. **"Connection refused" 오류**
   - MariaDB 서비스 상태 확인
   - 환경변수 설정 확인
   - 방화벽 설정 확인

3. **"Access denied" 오류**
   - 데이터베이스 사용자 권한 확인
   - 비밀번호 확인

4. **"Table already exists" 경고**
   - 정상적인 메시지 (기존 테이블 덮어쓰기)

5. **한글 깨짐**
   - UTF-8 인코딩 확인
   - 데이터베이스 charset 확인 (utf8mb4)

### 로그 확인
```bash
# 스크립트 실행 시 상세 로그 확인
python create_tables_from_csv.py 2>&1 | tee table_creation.log
```

---

**작성일:** 2025-08-17  
**버전:** 1.0  
**작성자:** Dive2025 Team
