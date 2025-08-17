import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

# venv
# source /Users/brightjin/Workspace/Dive2025/playground/dive-da/.venv/bin/activate

# all_data.csv 파일을 데이터프레임으로 읽기
try:
    df = pd.read_csv('./data/all_data.csv', skiprows=1)  # 첫 번째 행(채용정보 헤더) 스킵
    print(f"데이터프레임 생성 완료: {df.shape[0]}개 행, {df.shape[1]}개 열")
    print("\n컬럼명:")
    print(df.columns.tolist())
    print("\n첫 5행 데이터:")
    print(df.head())
    
    # '일반전형' 컬럼을 ','로 분리하여 새로운 데이터프레임 생성
    df_new = df[['기관명', '일반전형']].copy()
    
    # '일반전형'이 NaN이 아닌 행만 필터링
    df_new = df_new[df_new['일반전형'].notna()]
    
    # '일반전형' 컬럼을 ','로 분리하고 각 항목을 새로운 행으로 만들기
    df_expanded = []
    for idx, row in df_new.iterrows():
        기관명 = row['기관명']
        일반전형_text = str(row['일반전형'])
        
        # 먼저 줄바꿈으로 분리하고, 다시 쉼표로 분리
        일반전형_lines = 일반전형_text.split('\n')
        
        for line in 일반전형_lines:
            전형_list = line.split(',')
            for 전형 in 전형_list:
                전형 = 전형.strip()  # 공백 제거
                if 전형:  # 빈 문자열이 아닌 경우만
                    df_expanded.append({
                        '기관명': 기관명,
                        '일반전형': 전형
                    })
    
    # 새로운 데이터프레임 생성
    df_new = pd.DataFrame(df_expanded)
    
    # 중복제거
    df_new = df_new.drop_duplicates(subset=['기관명', '일반전형'])

    print(f"\n새로운 데이터프레임 df_new 생성 완료: {df_new.shape[0]}개 행, {df_new.shape[1]}개 열")
    print("\ndf_new 첫 10행:")
    print(df_new.head(10))
    print(f"\n고유한 기관명 수: {df_new['기관명'].nunique()}")
    print(f"고유한 일반전형 수: {df_new['일반전형'].nunique()}")
    
    # df_new_score 데이터프레임 생성
    import numpy as np
    
    # 점수 항목들 정의
    score_columns = [
        '성실성', '개방성', '외향성', '우호성', '정서안정성', '기술전문성', 
        '인지문제해결', '대인-영향력', '자기관리', '적응력', '학습속도', 
        '대인민첩성', '성과민첩성', '자기인식', '자기조절', '공감-사회기술'
    ]
    
    # df_new를 복사하여 df_new_score 생성
    df_new_score = df_new.copy()
    
    # 일반전형별 기준 점수 딕셔너리 생성
    np.random.seed(42)  # 재현 가능한 결과를 위한 시드 설정
    unique_forms = df_new['일반전형'].unique()
    
    # 각 일반전형에 대한 기준 점수 생성
    base_scores = {}
    for form in unique_forms:
        base_scores[form] = {}
        for column in score_columns:
            # 전형 종류에 따라 특성을 다르게 설정
            if '운영' in form or '사무' in form:
                # 운영직/사무직: 자기관리, 성실성, 대인관계 능력 높음
                if column in ['성실성', '자기관리', '대인-영향력', '공감-사회기술']:
                    base_scores[form][column] = np.random.randint(3, 6)
                else:
                    base_scores[form][column] = np.random.randint(2, 5)
            elif '기술' in form or '전기' in form or '기계' in form or '토목' in form or '건축' in form or '통신' in form or '신호' in form:
                # 기술직: 기술전문성, 인지문제해결, 학습속도 높음
                if column in ['기술전문성', '인지문제해결', '학습속도', '자기관리']:
                    base_scores[form][column] = np.random.randint(3, 6)
                else:
                    base_scores[form][column] = np.random.randint(2, 5)
            elif '운전' in form:
                # 운전직: 성실성, 정서안정성, 적응력 높음
                if column in ['성실성', '정서안정성', '적응력', '자기관리']:
                    base_scores[form][column] = np.random.randint(3, 6)
                else:
                    base_scores[form][column] = np.random.randint(2, 5)
            elif '공무' in form:
                # 공무직: 성실성, 기술전문성 높음
                if column in ['성실성', '기술전문성', '자기관리']:
                    base_scores[form][column] = np.random.randint(3, 6)
                else:
                    base_scores[form][column] = np.random.randint(2, 5)
            else:
                # 기타: 균등한 분포
                base_scores[form][column] = np.random.randint(2, 5)
    
    # 각 행에 대해 기준 점수에서 약간의 변동을 가진 점수 할당
    for idx, row in df_new_score.iterrows():
        form = row['일반전형']
        for column in score_columns:
            base_score = base_scores[form][column]
            # 기준 점수에서 ±1 범위의 변동 (1~5 범위 유지)
            variation = np.random.randint(-1, 2)
            final_score = max(1, min(5, base_score + variation))
            df_new_score.loc[idx, column] = final_score
    
    print(f"\n새로운 데이터프레임 df_new_score 생성 완료: {df_new_score.shape[0]}개 행, {df_new_score.shape[1]}개 열")
    print("\ndf_new_score 첫 5행:")
    print(df_new_score.head())
    print(f"\n컬럼명: {df_new_score.columns.tolist()}")
    
    # 유사한 전형끼리 점수 비교 확인
    print("\n=== 전형별 점수 비교 ===")
    
    # 운영직 관련 전형들의 평균 점수
    운영직_data = df_new_score[df_new_score['일반전형'].str.contains('운영', na=False)]
    if not 운영직_data.empty:
        print(f"\n📊 운영직 관련 전형들 ({len(운영직_data)}개):")
        print("주요 강점 항목 평균 점수:")
        강점항목 = ['성실성', '자기관리', '대인-영향력', '공감-사회기술']
        for 항목 in 강점항목:
            평균점수 = 운영직_data[항목].mean()
            print(f"  - {항목}: {평균점수:.1f}점")
    
    # 기술직 관련 전형들의 평균 점수
    기술직_keywords = ['기술', '전기', '기계', '토목', '건축', '통신', '신호']
    기술직_data = df_new_score[df_new_score['일반전형'].str.contains('|'.join(기술직_keywords), na=False)]
    if not 기술직_data.empty:
        print(f"\n🔧 기술직 관련 전형들 ({len(기술직_data)}개):")
        print("주요 강점 항목 평균 점수:")
        강점항목 = ['기술전문성', '인지문제해결', '학습속도', '자기관리']
        for 항목 in 강점항목:
            평균점수 = 기술직_data[항목].mean()
            print(f"  - {항목}: {평균점수:.1f}점")
    
    # 운전직 관련 전형들의 평균 점수
    운전직_data = df_new_score[df_new_score['일반전형'].str.contains('운전', na=False)]
    if not 운전직_data.empty:
        print(f"\n🚗 운전직 관련 전형들 ({len(운전직_data)}개):")
        print("주요 강점 항목 평균 점수:")
        강점항목 = ['성실성', '정서안정성', '적응력', '자기관리']
        for 항목 in 강점항목:
            평균점수 = 운전직_data[항목].mean()
            print(f"  - {항목}: {평균점수:.1f}점")
    
    print("\n" + "="*50)
    print("🎯 구직자 적합 전형 추천 시스템")
    print("="*50)
    
    # 분석 모델 구축
    from sklearn.metrics.pairwise import cosine_similarity
    from sklearn.preprocessing import StandardScaler
    import warnings
    warnings.filterwarnings('ignore')
    
    # 전형별 평균 점수 계산 (기준 프로파일)
    전형_프로파일 = df_new_score.groupby('일반전형')[score_columns].mean()
    print(f"\n📊 전형별 기준 프로파일 생성 완료: {len(전형_프로파일)}개 전형")
    
    def 적합전형_추천(구직자_점수_dict, top_n=5):
        """
        구직자의 16가지 능력 점수를 받아 가장 적합한 전형을 추천하는 함수
        
        Parameters:
        구직자_점수_dict: 16개 항목의 점수 딕셔너리 (예: {'성실성': 4, '개방성': 3, ...})
        top_n: 추천할 전형 개수
        
        Returns:
        추천 결과 리스트
        """
        # 구직자 점수를 배열로 변환
        구직자_점수 = [구직자_점수_dict.get(col, 3) for col in score_columns]
        구직자_점수 = np.array(구직자_점수).reshape(1, -1)
        
        # 코사인 유사도 계산
        유사도_점수 = cosine_similarity(구직자_점수, 전형_프로파일.values)[0]
        
        # 유클리드 거리 계산 (거리가 작을수록 유사)
        from scipy.spatial.distance import euclidean
        거리_점수 = []
        for idx, 전형_점수 in enumerate(전형_프로파일.values):
            거리 = euclidean(구직자_점수[0], 전형_점수)
            거리_점수.append(1 / (1 + 거리))  # 거리를 유사도로 변환
        
        # 두 지표를 결합한 종합 점수 (가중평균)
        종합_점수 = 0.6 * 유사도_점수 + 0.4 * np.array(거리_점수)
        
        # 상위 N개 전형 선택
        추천_인덱스 = np.argsort(종합_점수)[::-1][:top_n]
        
        추천_결과 = []
        for i, idx in enumerate(추천_인덱스):
            전형명 = 전형_프로파일.index[idx]
            적합도 = 종합_점수[idx] * 100
            추천_결과.append({
                '순위': i + 1,
                '전형명': 전형명,
                '적합도': f"{적합도:.1f}%",
                '코사인유사도': f"{유사도_점수[idx]:.3f}",
                '거리기반유사도': f"{거리_점수[idx]:.3f}"
            })
        
        return 추천_결과
    
    # 예시 구직자 데이터로 테스트
    print("\n🧪 모델 테스트 - 예시 구직자들")
    
    # 예시 1: 기술직 성향 구직자
    기술직_구직자 = {
        '성실성': 4, '개방성': 3, '외향성': 2, '우호성': 3, '정서안정성': 4,
        '기술전문성': 5, '인지문제해결': 5, '대인-영향력': 2, '자기관리': 4, '적응력': 4,
        '학습속도': 5, '대인민첩성': 2, '성과민첩성': 3, '자기인식': 3, '자기조절': 4, '공감-사회기술': 3
    }
    
    print("\n👨‍💻 구직자 A (기술직 성향):")
    print("강점: 기술전문성(5점), 인지문제해결(5점), 학습속도(5점)")
    추천결과 = 적합전형_추천(기술직_구직자, top_n=3)
    for 결과 in 추천결과:
        print(f"  {결과['순위']}. {결과['전형명']} - 적합도: {결과['적합도']}")
    
    # 예시 2: 운영직 성향 구직자
    운영직_구직자 = {
        '성실성': 5, '개방성': 4, '외향성': 4, '우호성': 5, '정서안정성': 4,
        '기술전문성': 2, '인지문제해결': 3, '대인-영향력': 5, '자기관리': 5, '적응력': 4,
        '학습속도': 3, '대인민첩성': 5, '성과민첩성': 4, '자기인식': 4, '자기조절': 4, '공감-사회기술': 5
    }
    
    print("\n👩‍💼 구직자 B (운영직 성향):")
    print("강점: 성실성(5점), 대인-영향력(5점), 자기관리(5점), 공감-사회기술(5점)")
    추천결과 = 적합전형_추천(운영직_구직자, top_n=3)
    for 결과 in 추천결과:
        print(f"  {결과['순위']}. {결과['전형명']} - 적합도: {결과['적합도']}")
    
    # 예시 3: 운전직 성향 구직자
    운전직_구직자 = {
        '성실성': 5, '개방성': 3, '외향성': 3, '우호성': 4, '정서안정성': 5,
        '기술전문성': 3, '인지문제해결': 3, '대인-영향력': 3, '자기관리': 5, '적응력': 5,
        '학습속도': 3, '대인민첩성': 3, '성과민첩성': 4, '자기인식': 4, '자기조절': 5, '공감-사회기술': 3
    }
    
    print("\n🚗 구직자 C (운전직 성향):")
    print("강점: 성실성(5점), 정서안정성(5점), 자기관리(5점), 적응력(5점)")
    추천결과 = 적합전형_추천(운전직_구직자, top_n=3)
    for 결과 in 추천결과:
        print(f"  {결과['순위']}. {결과['전형명']} - 적합도: {결과['적합도']}")
    
    # 함수를 전역에서 사용할 수 있도록 저장
    globals()['추천_함수'] = 적합전형_추천
    globals()['전형_프로파일_데이터'] = 전형_프로파일
    
    print("\n✅ 추천 모델이 성공적으로 구축되었습니다!")
    print("📝 사용법: 적합전형_추천(구직자_점수_딕셔너리, top_n=5)")
    
except FileNotFoundError:
    print("./data/all_data.csv 파일을 찾을 수 없습니다.")
except Exception as e:
    print(f"파일 읽기 중 오류 발생: {e}")