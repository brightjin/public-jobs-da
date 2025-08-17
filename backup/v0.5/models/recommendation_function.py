
def recommend_job_postings(user_scores, model_dir='./models', top_k=5):
    """
    사용자 점수를 받아 유사한 채용공고 추천
    
    Args:
        user_scores (dict): 사용자의 16가지 점수
        model_dir (str): 모델 디렉토리 경로
        top_k (int): 추천할 공고 수
    
    Returns:
        list: 추천 공고일련번호와 유사도 정보
    """
    import pickle
    import numpy as np
    from sklearn.metrics.pairwise import cosine_similarity
    
    # 모델 로딩
    with open(f'{model_dir}/similarity_model.pkl', 'rb') as f:
        model = pickle.load(f)
    
    scaler = model['scaler']
    normalized_scores = model['normalized_scores']
    job_posting_scores = model['job_posting_scores']
    
    score_columns = [
        '성실성', '개방성', '외향성', '우호성', '정서안정성', '기술전문성',
        '인지문제해결', '대인-영향력', '자기관리', '적응력', '학습속도',
        '대인민첩성', '성과민첩성', '자기인식', '자기조절', '공감-사회기술'
    ]
    
    # 사용자 점수 정규화
    user_score_array = np.array([user_scores.get(col, 3) for col in score_columns])
    user_score_normalized = scaler.transform([user_score_array])
    
    # 유사도 계산
    similarities = cosine_similarity(user_score_normalized, normalized_scores)[0]
    
    # 상위 k개 추천
    top_indices = similarities.argsort()[-top_k:][::-1]
    
    recommendations = []
    for idx in top_indices:
        recommendations.append({
            '공고일련번호': job_posting_scores.iloc[idx]['공고일련번호'],
            '기관코드': job_posting_scores.iloc[idx]['기관코드'],
            '일반전형': job_posting_scores.iloc[idx]['일반전형'],
            '유사도': float(similarities[idx])
        })
    
    return recommendations
