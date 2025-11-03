"""
CryptoCompare API 클라이언트
"""
from typing import Dict, Any, List, Optional
from datetime import datetime, timezone
import time
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from .base import BaseCollector
from utils.logger import log_error

class CryptoCompareCollector(BaseCollector):
    """CryptoCompare API 데이터 수집기"""
    
    def __init__(self, api_key: str):
        """
        CryptoCompare 수집기 초기화
        
        Args:
            api_key: CryptoCompare API 키
        """
        super().__init__(
            api_key=api_key,
            base_url='https://min-api.cryptocompare.com/data',
            rate_limit=3333  # 월 100,000 요청
        )
        
        # CryptoCompare API 헤더 설정
        self.session.headers['authorization'] = f'Apikey {api_key}'
    
    def get_social_stats(self, coin_id: int) -> Optional[Dict[str, Any]]:
        """
        소셜 통계 조회
        
        Args:
            coin_id: CryptoCompare 코인 ID
        
        Returns:
            소셜 통계 데이터 또는 None
        """
        try:
            endpoint = f"/social/coin/{coin_id}"
            
            response = self._make_request(endpoint)
            
            if not response or 'Data' not in response:
                return None
            
            data = response['Data']
            
            social_stats = {
                'coin_id': coin_id,
                'timestamp': datetime.now(timezone.utc),
                'twitter_followers': data.get('Twitter', {}).get('followers', 0),
                'twitter_following': data.get('Twitter', {}).get('following', 0),
                'twitter_lists': data.get('Twitter', {}).get('lists', 0),
                'twitter_favourites': data.get('Twitter', {}).get('favourites', 0),
                'twitter_statuses': data.get('Twitter', {}).get('statuses', 0),
                'reddit_subscribers': data.get('Reddit', {}).get('subscribers', 0),
                'reddit_active_users': data.get('Reddit', {}).get('active_users', 0),
                'reddit_posts_per_hour': data.get('Reddit', {}).get('posts_per_hour', 0),
                'reddit_comments_per_hour': data.get('Reddit', {}).get('comments_per_hour', 0),
                'community_score': data.get('General', {}).get('community_score', 0),
                'public_interest_score': data.get('General', {}).get('public_interest_score', 0),
                'raw_data': data
            }
            
            return social_stats
            
        except Exception as e:
            import logging
            logger = logging.getLogger(__name__)
            log_error(logger, e, f"소셜 통계 조회 실패: {coin_id}")
            return None
    
    def get_news_list(self, coins: List[str], limit: int = 50) -> List[Dict[str, Any]]:
        """
        뉴스 목록 조회
        
        Args:
            coins: 코인 심볼 리스트
            limit: 조회할 뉴스 수
        
        Returns:
            뉴스 목록
        """
        try:
            endpoint = "/v2/news/"
            params = {
                'lang': 'EN',
                'sortOrder': 'latest',
                'limit': limit
            }
            
            # 특정 코인 필터링이 필요한 경우
            if len(coins) == 1:
                params['categories'] = coins[0].lower()
            
            response = self._make_request(endpoint, params)
            
            if not response or 'Data' not in response:
                return []
            
            news_list = []
            for news_item in response['Data']:
                news = {
                    'id': news_item['id'],
                    'title': news_item['title'],
                    'url': news_item['url'],
                    'source': news_item['source'],
                    'published_on': datetime.fromtimestamp(news_item['published_on'], tz=timezone.utc),
                    'imageurl': news_item.get('imageurl', ''),
                    'body': news_item.get('body', ''),
                    'tags': news_item.get('tags', ''),
                    'categories': news_item.get('categories', ''),
                    'raw_data': news_item
                }
                news_list.append(news)
            
            return news_list
            
        except Exception as e:
            import logging
            logger = logging.getLogger(__name__)
            log_error(logger, e, f"뉴스 목록 조회 실패: {coins}")
            return []
    
    def get_latest_sentiment(self, coins: List[str]) -> List[Dict[str, Any]]:
        """
        최신 감성 분석 데이터 조회
        
        Args:
            coins: 코인 심볼 리스트
        
        Returns:
            감성 분석 데이터 리스트
        """
        try:
            all_sentiment = []
            
            for coin in coins:
                endpoint = f"/sentiment/v2/latest"
                params = {
                    'fsym': coin,
                    'tsym': 'USD'
                }
                
                response = self._make_request(endpoint, params)
                
                if not response or 'Data' not in response:
                    continue
                
                data = response['Data']
                
                sentiment = {
                    'symbol': coin,
                    'timestamp': datetime.now(timezone.utc),
                    'news_count': data.get('news_count', 0),
                    'news_sources': data.get('news_sources', []),
                    'sentiment_score': data.get('sentiment_score', 0),
                    'sentiment_positive': data.get('sentiment_positive', 0),
                    'sentiment_neutral': data.get('sentiment_neutral', 0),
                    'sentiment_negative': data.get('sentiment_negative', 0),
                    'trending_score': data.get('trending_score', 0),
                    'raw_data': data
                }
                
                all_sentiment.append(sentiment)
                
                # Rate limit 고려하여 잠시 대기
                time.sleep(0.1)
            
            return all_sentiment
            
        except Exception as e:
            import logging
            logger = logging.getLogger(__name__)
            log_error(logger, e, f"감성 분석 데이터 조회 실패: {coins}")
            return []
    
    def get_coin_list(self) -> Dict[str, Any]:
        """
        코인 목록 조회 (ID 매핑용)
        
        Returns:
            코인 목록 딕셔너리
        """
        try:
            endpoint = "/all/coinlist"
            
            response = self._make_request(endpoint)
            
            if not response or 'Data' not in response:
                return {}
            
            return response['Data']
            
        except Exception as e:
            import logging
            logger = logging.getLogger(__name__)
            log_error(logger, e, "코인 목록 조회 실패")
            return {}
    
    def collect_social_data(self, symbols: List[str]) -> List[Dict[str, Any]]:
        """
        여러 코인의 소셜 데이터 수집
        
        Args:
            symbols: 코인 심볼 리스트
        
        Returns:
            소셜 데이터 리스트
        """
        try:
            all_data = []
            
            # 코인 목록에서 ID 매핑
            coin_list = self.get_coin_list()
            
            for symbol in symbols:
                # 심볼로 코인 ID 찾기
                coin_id = None
                for coin_id_key, coin_data in coin_list.items():
                    if coin_data.get('Symbol') == symbol:
                        coin_id = int(coin_id_key)
                        break
                
                if not coin_id:
                    continue
                
                # 소셜 통계 조회
                social_stats = self.get_social_stats(coin_id)
                if social_stats:
                    all_data.append(social_stats)
                
                # Rate limit 고려하여 잠시 대기
                time.sleep(0.1)
            
            return all_data
            
        except Exception as e:
            import logging
            logger = logging.getLogger(__name__)
            log_error(logger, e, "소셜 데이터 수집 실패")
            return []
    
    def collect_news_sentiment_data(self, symbols: List[str]) -> List[Dict[str, Any]]:
        """
        여러 코인의 뉴스 감성 데이터 수집
        
        Args:
            symbols: 코인 심볼 리스트
        
        Returns:
            뉴스 감성 데이터 리스트
        """
        try:
            return self.get_latest_sentiment(symbols)
            
        except Exception as e:
            import logging
            logger = logging.getLogger(__name__)
            log_error(logger, e, "뉴스 감성 데이터 수집 실패")
            return []
    
    def collect_data(self, symbol: str, start_date: datetime, end_date: datetime, interval: str = '1d') -> List[Dict[str, Any]]:
        """
        베이스 클래스의 추상 메서드 구현
        
        Args:
            symbol: 코인 심볼
            start_date: 시작 날짜
            end_date: 종료 날짜
            interval: 데이터 간격
        
        Returns:
            수집된 데이터 리스트
        """
        try:
            # CryptoCompare는 실시간 소셜/뉴스 데이터만 제공
            social_data = self.collect_social_data([symbol])
            sentiment_data = self.collect_news_sentiment_data([symbol])
            
            return social_data + sentiment_data
            
        except Exception as e:
            import logging
            logger = logging.getLogger(__name__)
            log_error(logger, e, f"데이터 수집 실패: {symbol}")
            return []
