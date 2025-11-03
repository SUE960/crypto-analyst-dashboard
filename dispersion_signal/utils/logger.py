"""
로깅 설정 및 유틸리티
"""
import logging
import os
from datetime import datetime
from pathlib import Path

def setup_logger(name: str = 'dispersion_signal', log_file: str = 'logs/collector.log', level: str = 'INFO'):
    """
    로거 설정
    
    Args:
        name: 로거 이름
        log_file: 로그 파일 경로
        level: 로그 레벨
    
    Returns:
        logging.Logger: 설정된 로거
    """
    # 로그 디렉토리 생성
    log_path = Path(log_file)
    log_path.parent.mkdir(parents=True, exist_ok=True)
    
    # 로거 생성
    logger = logging.getLogger(name)
    logger.setLevel(getattr(logging, level.upper()))
    
    # 기존 핸들러 제거 (중복 방지)
    for handler in logger.handlers[:]:
        logger.removeHandler(handler)
    
    # 포맷터 설정
    formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    
    # 파일 핸들러
    file_handler = logging.FileHandler(log_file, encoding='utf-8')
    file_handler.setLevel(getattr(logging, level.upper()))
    file_handler.setFormatter(formatter)
    logger.addHandler(file_handler)
    
    # 콘솔 핸들러
    console_handler = logging.StreamHandler()
    console_handler.setLevel(getattr(logging, level.upper()))
    console_handler.setFormatter(formatter)
    logger.addHandler(console_handler)
    
    return logger

def log_api_call(logger: logging.Logger, endpoint: str, status_code: int, response_time: float):
    """
    API 호출 로깅
    
    Args:
        logger: 로거 인스턴스
        endpoint: API 엔드포인트
        status_code: HTTP 상태 코드
        response_time: 응답 시간 (초)
    """
    if status_code == 200:
        logger.info(f"API 호출 성공: {endpoint} - {status_code} ({response_time:.2f}s)")
    else:
        logger.warning(f"API 호출 실패: {endpoint} - {status_code} ({response_time:.2f}s)")

def log_data_collection(logger: logging.Logger, symbol: str, records_count: int, duration: float):
    """
    데이터 수집 로깅
    
    Args:
        logger: 로거 인스턴스
        symbol: 코인 심볼
        records_count: 수집된 레코드 수
        duration: 수집 시간 (초)
    """
    logger.info(f"데이터 수집 완료: {symbol} - {records_count}개 레코드 ({duration:.2f}s)")

def log_info(logger: logging.Logger, message: str):
    """
    정보 로깅
    
    Args:
        logger: 로거 인스턴스
        message: 로그 메시지
    """
    logger.info(message)

def log_error(logger: logging.Logger, error: Exception, context: str = ""):
    """
    에러 로깅
    
    Args:
        logger: 로거 인스턴스
        error: 발생한 예외
        context: 에러 발생 컨텍스트
    """
    context_msg = f" ({context})" if context else ""
    logger.error(f"에러 발생{context_msg}: {type(error).__name__}: {str(error)}", exc_info=True)
