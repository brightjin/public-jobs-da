# Dive-DA v1.0 백업

## 백업 정보
- **버전**: v1.0
- **백업 날짜**: 2025-01-17
- **압축 파일**: v1.0_backup.tar.gz (83.8MB)

## 주요 변경사항

### 1. 포트 설정 변경
- 서비스 포트를 5001에서 8080으로 변경
- 관련 파일: `job_recommendation_api.py`, `README.md`

### 2. 통합 로깅 시스템 구현
- 새로운 로깅 모듈 `log_config.py` 생성
- UTF-8 인코딩 지원으로 한글 로그 완벽 지원
- 파일별 개별 로그 파일 생성 (./log/ 디렉토리)
- 콘솔과 파일 동시 출력 설정

### 3. 로깅 적용 파일
- `job_recommendation_api.py`: 메인 API 서버
- `data/create_tables_from_csv.py`: 테이블 생성 스크립트
- `data/manage_tables.py`: 테이블 관리 스크립트
- `data/analyze_csv.py`: CSV 분석 스크립트
- `models/recommendation_function.py`: 추천 함수

### 4. 문서화 업데이트
- `README.md`: 포트 8080 반영, 로깅 시스템 설명 추가
- 로깅 명령어 예시 추가:
  ```bash
  tail -f ./log/job_recommendation_api.log
  tail -f ./log/create_tables_from_csv.log
  tail -f ./log/manage_tables.log
  ```

### 5. Git 환경 설정
- `.gitignore` 파일 생성
- Python 프로젝트에 최적화된 제외 규칙
- log/ 디렉토리 제외 설정

### 6. 코드 오류 수정
- `job_recommendation_api.py`: import 구문 오류 수정
- 모든 Python 파일의 구문 오류 점검 완료

## 사용법

### 백업 복원
```bash
# 압축 해제
tar -xzf v1.0_backup.tar.gz

# 또는 디렉토리 복사
cp -r v1.0/* /target/directory/
```

### 서비스 실행
```bash
# 가상환경 활성화
source .venv/bin/activate

# API 서버 실행 (포트 8080)
python job_recommendation_api.py
```

### 로그 모니터링
```bash
# 실시간 로그 확인
tail -f ./log/job_recommendation_api.log

# 모든 로그 확인
find ./log -name "*.log" -exec tail -f {} +
```

## 기술 스택
- Python 3.9+
- Flask (API 서버)
- MariaDB (데이터베이스)
- scikit-learn (머신러닝)
- 로깅: UTF-8 지원 파일 로깅
- 포트: 8080

## 다음 개발 계획
- API 엔드포인트 확장
- 성능 모니터링 시스템
- 오류 처리 개선
- 단위 테스트 추가
