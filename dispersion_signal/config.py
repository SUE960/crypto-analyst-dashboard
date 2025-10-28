"""
Dispersion Signal 프로젝트 설정 관리
"""
import os
from dotenv import load_dotenv

# .env 파일 로드
load_dotenv()

class Config:
    """애플리케이션 설정"""
    
    # Supabase 설정
    SUPABASE_URL = os.getenv('SUPABASE_URL', 'https://goeqmhurrhgwmazaxfpm.supabase.co')
    SUPABASE_SERVICE_ROLE_KEY = os.getenv('SUPABASE_SERVICE_ROLE_KEY')
    
    # Binance API 설정 (무료)
    BINANCE_BASE_URL = 'https://api.binance.com'
    BINANCE_RATE_LIMIT = 1200  # 분당 1200 요청 (매우 관대함)
    
    # CryptoQuant API 설정 (향후 확장용)
    CRYPTOQUANT_API_KEY = os.getenv('CRYPTOQUANT_API_KEY')
    CRYPTOQUANT_BASE_URL = 'https://api.cryptoquant.com/v1'
    
    # CoinMarketCap API 설정
    COINMARKETCAP_API_KEY = os.getenv('COINMARKETCAP_API_KEY')
    COINMARKETCAP_BASE_URL = 'https://pro-api.coinmarketcap.com/v1'
    COINMARKETCAP_RATE_LIMIT = 333  # 월 10,000 요청 ≈ 분당 333회 (30일 기준)
    
    # CryptoCompare API 설정
    CRYPTOCOMPARE_API_KEY = os.getenv('CRYPTOCOMPARE_API_KEY')
    CRYPTOCOMPARE_BASE_URL = 'https://min-api.cryptocompare.com/data'
    CRYPTOCOMPARE_RATE_LIMIT = 3333  # 월 100,000 요청 ≈ 분당 3333회
    
    # Messari API 설정
    MESSARI_API_KEY = os.getenv('MESSARI_API_KEY')
    MESSARI_BASE_URL = 'https://data.messari.io/api/v1'
    MESSARI_RATE_LIMIT = 20  # 분당 20회 제한
    
    # API 제한 설정
    RATE_LIMIT_REQUESTS_PER_MINUTE = 1200  # Binance 기본값
    MAX_RETRIES = 3
    RETRY_DELAY = 5  # 초
    
    # 데이터 수집 설정
    DEFAULT_DAYS = 365  # 1년치 히스토리컬 데이터
    DEFAULT_INTERVAL = '1d'  # 일일 데이터
    BATCH_SIZE = 100
    TOP_COINS_COUNT = 20  # 상위 20개 코인
    HISTORICAL_DAYS = 365  # 히스토리컬 데이터 일수
    
    # Phase 2 데이터 수집 설정
    MARKETCAP_COINS_COUNT = 20
    SOCIAL_DATA_ENABLED = True
    NEWS_SENTIMENT_ENABLED = True
    
    # Reddit API 설정
    REDDIT_CLIENT_ID = os.getenv('REDDIT_CLIENT_ID')
    REDDIT_CLIENT_SECRET = os.getenv('REDDIT_CLIENT_SECRET')
    REDDIT_USERNAME = os.getenv('REDDIT_USERNAME')
    REDDIT_PASSWORD = os.getenv('REDDIT_PASSWORD')
    REDDIT_REDIRECT_URI = os.getenv('REDDIT_REDIRECT_URI', 'http://localhost:8080/callback')
    REDDIT_USER_AGENT = os.getenv('REDDIT_USER_AGENT', 'coin_by_emotion/1.0')
    REDDIT_RATE_LIMIT = 60  # 분당 60회
    
    # Phase 4 API 설정
    COINCAP_BASE_URL = 'https://api.coincap.io/v2'
    COINPAPRIKA_BASE_URL = 'https://api.coinpaprika.com/v1'
    COINGECKO_BASE_URL = 'https://api.coingecko.com/api/v3'
    COINGECKO_RATE_LIMIT = 30  # 분당 30회
    
    # 로깅 설정
    LOG_LEVEL = 'INFO'
    LOG_FILE = 'logs/collector.log'
    
    @classmethod
    def validate(cls):
        """필수 환경변수 검증"""
        required_vars = [
            'SUPABASE_SERVICE_ROLE_KEY'
        ]
        
        missing_vars = []
        for var in required_vars:
            if not getattr(cls, var):
                missing_vars.append(var)
        
        if missing_vars:
            raise ValueError(f"Missing required environment variables: {', '.join(missing_vars)}")
        
        return True
    
    @classmethod
    def validate_binance(cls):
        """Binance API 설정 검증 (API 키 불필요)"""
        if not cls.SUPABASE_URL or not cls.SUPABASE_SERVICE_ROLE_KEY:
            raise ValueError("Supabase 설정이 필요합니다")
        return True
    
    @classmethod
    def validate_phase2(cls):
        """Phase 2 API 설정 검증"""
        if not cls.COINMARKETCAP_API_KEY:
            raise ValueError("CoinMarketCap API 키가 필요합니다")
        if not cls.CRYPTOCOMPARE_API_KEY:
            raise ValueError("CryptoCompare API 키가 필요합니다")
        return True
    
    @classmethod
    def validate_reddit(cls):
        """Reddit API 설정 검증"""
        required = ['REDDIT_CLIENT_ID', 'REDDIT_CLIENT_SECRET', 'REDDIT_USERNAME', 'REDDIT_PASSWORD']
        missing = [k for k in required if not getattr(cls, k)]
        if missing:
            raise ValueError(f"Reddit API 설정 필요: {', '.join(missing)}")
        return True
