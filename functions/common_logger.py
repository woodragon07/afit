# functions/common_logger.py - 공통 로깅 설정
import logging
import os

# 로깅 관련 기본 설정
def setup_logger():
    """공통 로거 설정 함수"""
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    
    # 로그 레벨 환경 변수에서 가져오기
    log_level = os.getenv('LOG_LEVEL', 'INFO').upper()
    valid_levels = {
        'DEBUG': logging.DEBUG,
        'INFO': logging.INFO,
        'WARNING': logging.WARNING,
        'ERROR': logging.ERROR,
        'CRITICAL': logging.CRITICAL
    }
    
    # 유효한 로그 레벨이면 설정
    if log_level in valid_levels:
        logging.getLogger().setLevel(valid_levels[log_level])

# 애플리케이션 시작 시 로거 설정 호출
setup_logger()

def get_logger(name):
    """모듈별 로거를 가져오는 함수"""
    return logging.getLogger(name)