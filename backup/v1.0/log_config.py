#!/usr/bin/env python3
"""
공통 로깅 설정 모듈
모든 서비스에서 일관된 로깅 설정을 사용하기 위한 유틸리티
"""

import os
import logging
from datetime import datetime

def setup_logger(name, log_file=None, level=logging.INFO):
    """
    로거 설정
    
    Args:
        name: 로거 이름 (보통 __name__ 사용)
        log_file: 로그 파일 이름 (없으면 모듈명.log 사용)
        level: 로그 레벨
    
    Returns:
        configured logger
    """
    # 로그 디렉토리 생성
    log_dir = './log'
    os.makedirs(log_dir, exist_ok=True)
    
    # 로그 파일명 결정
    if log_file is None:
        # 모듈명에서 로그 파일명 생성
        module_name = name.split('.')[-1] if '.' in name else name
        if module_name == '__main__':
            # 실행 파일명에서 추출
            import sys
            module_name = os.path.splitext(os.path.basename(sys.argv[0]))[0]
        log_file = f"{module_name}.log"
    
    log_path = os.path.join(log_dir, log_file)
    
    # 로거 생성
    logger = logging.getLogger(name)
    
    # 이미 핸들러가 있으면 제거 (중복 방지)
    if logger.handlers:
        logger.handlers.clear()
    
    logger.setLevel(level)
    
    # 포맷터 설정
    formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    
    # 파일 핸들러 (UTF-8 인코딩)
    file_handler = logging.FileHandler(log_path, encoding='utf-8')
    file_handler.setLevel(level)
    file_handler.setFormatter(formatter)
    logger.addHandler(file_handler)
    
    # 콘솔 핸들러 (선택적)
    console_handler = logging.StreamHandler()
    console_handler.setLevel(level)
    console_formatter = logging.Formatter(
        '%(levelname)s - %(message)s'
    )
    console_handler.setFormatter(console_formatter)
    logger.addHandler(console_handler)
    
    return logger

def get_logger(name, log_file=None):
    """
    간편한 로거 생성 함수
    """
    return setup_logger(name, log_file)

# 기본 로거 설정 (하위 호환성)
def init_logging():
    """
    기본 로깅 초기화 (기존 코드 호환용)
    """
    return setup_logger(__name__, 'app.log')
