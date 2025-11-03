"""
Reddit API 클라이언트
"""
import requests
from typing import List, Dict, Any, Optional
import base64
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from collectors.base import BaseCollector
from utils.logger import log_error

class RedditCollector(BaseCollector):
    """Reddit API 클라이언트"""
    
    def __init__(self, client_id: str, client_secret: str, 
                 username: str, password: str, user_agent: str):
        super().__init__(
            api_key=None,  # Reddit은 OAuth 사용
            base_url='https://oauth.reddit.com',
            rate_limit=60  # 분당 60회
        )
        
        self.client_id = client_id
        self.client_secret = client_secret
        self.username = username
        self.password = password
        self.user_agent = user_agent
        self.access_token = None
        
        # OAuth 토큰 획득
        self._get_access_token()
    
    def _get_access_token(self):
        """Reddit OAuth 토큰 획득"""
        try:
            # Basic Auth 헤더 생성
            auth_string = f"{self.client_id}:{self.client_secret}"
            auth_bytes = auth_string.encode('ascii')
            auth_b64 = base64.b64encode(auth_bytes).decode('ascii')
            
            headers = {
                'Authorization': f'Basic {auth_b64}',
                'User-Agent': self.user_agent
            }
            
            data = {
                'grant_type': 'password',
                'username': self.username,
                'password': self.password
            }
            
            response = requests.post(
                'https://www.reddit.com/api/v1/access_token',
                headers=headers,
                data=data
            )
            
            if response.status_code == 200:
                token_data = response.json()
                self.access_token = token_data['access_token']
                
                # 세션 헤더 설정
                self.session.headers.update({
                    'Authorization': f'Bearer {self.access_token}',
                    'User-Agent': self.user_agent
                })
                
                if self.logger:
                    self.logger.info("Reddit OAuth 토큰 획득 성공")
            else:
                raise Exception(f"토큰 획득 실패: {response.status_code} - {response.text}")
                
        except Exception as e:
            if hasattr(self, 'logger') and self.logger:
                log_error(self.logger, e, "Reddit OAuth 토큰 획득 실패")
            else:
                print(f"Reddit OAuth 토큰 획득 실패: {e}")
    
    def get_subreddit_posts(self, subreddit: str, limit: int = 100, 
                           time_filter: str = 'day') -> Optional[Dict[str, Any]]:
        """
        서브레딧 포스트 조회
        
        Args:
            subreddit: 서브레딧 이름 (예: 'cryptocurrency')
            limit: 조회할 포스트 수
            time_filter: 시간 필터 (hour, day, week, month, year, all)
        
        Returns:
            포스트 데이터
        """
        endpoint = f"/r/{subreddit}/hot"
        params = {
            'limit': limit,
            't': time_filter
        }
        return self._make_request(endpoint, params=params)
    
    def search_posts(self, query: str, subreddit: str = None, 
                    limit: int = 100) -> Optional[Dict[str, Any]]:
        """
        포스트 검색
        
        Args:
            query: 검색어
            subreddit: 서브레딧 이름 (선택사항)
            limit: 조회할 포스트 수
        
        Returns:
            검색 결과
        """
        if subreddit:
            endpoint = f"/r/{subreddit}/search"
        else:
            endpoint = "/search"
        
        params = {
            'q': query,
            'limit': limit,
            'sort': 'relevance',
            't': 'week'
        }
        return self._make_request(endpoint, params=params)
    
    def get_crypto_mentions(self, symbols: List[str], 
                           subreddits: List[str] = None) -> Dict[str, Any]:
        """
        암호화폐 언급 분석
        
        Args:
            symbols: 코인 심볼 리스트
            subreddits: 분석할 서브레딧 리스트
        
        Returns:
            코인별 언급 분석 결과
        """
        if subreddits is None:
            subreddits = ['cryptocurrency', 'bitcoin', 'ethereum', 'solana']
        
        crypto_mentions = {}
        
        for symbol in symbols:
            mentions = {
                'total_mentions': 0,
                'positive_mentions': 0,
                'negative_mentions': 0,
                'neutral_mentions': 0,
                'subreddit_breakdown': {}
            }
            
            for subreddit in subreddits:
                try:
                    # 서브레딧에서 코인 검색
                    posts = self.search_posts(symbol, subreddit, limit=50)
                    
                    if posts and 'data' in posts:
                        posts_data = posts['data']['children']
                        
                        subreddit_mentions = len(posts_data)
                        mentions['total_mentions'] += subreddit_mentions
                        mentions['subreddit_breakdown'][subreddit] = subreddit_mentions
                        
                        # 간단한 감성 분석 (업보트/다운보트 기반)
                        for post in posts_data:
                            post_data = post['data']
                            score = post_data.get('score', 0)
                            
                            if score > 10:
                                mentions['positive_mentions'] += 1
                            elif score < -5:
                                mentions['negative_mentions'] += 1
                            else:
                                mentions['neutral_mentions'] += 1
                
                except Exception as e:
                    log_error(self.logger, e, f"Reddit 검색 실패: {symbol} in {subreddit}")
                    continue
            
            crypto_mentions[symbol] = mentions
        
        return crypto_mentions
    
    def get_subreddit_info(self, subreddit: str) -> Optional[Dict[str, Any]]:
        """
        서브레딧 정보 조회
        
        Args:
            subreddit: 서브레딧 이름
        
        Returns:
            서브레딧 정보
        """
        endpoint = f"/r/{subreddit}/about"
        return self._make_request(endpoint)
    
    def get_user_info(self, username: str) -> Optional[Dict[str, Any]]:
        """
        사용자 정보 조회
        
        Args:
            username: 사용자명
        
        Returns:
            사용자 정보
        """
        endpoint = f"/user/{username}/about"
        return self._make_request(endpoint)
    
    def get_trending_subreddits(self) -> Optional[List[Dict[str, Any]]]:
        """
        트렌딩 서브레딧 조회
        
        Returns:
            트렌딩 서브레딧 목록
        """
        endpoint = "/subreddits/popular"
        params = {'limit': 25}
        response = self._make_request(endpoint, params=params)
        
        if response and 'data' in response:
            return response['data']['children']
        return None
    
    def analyze_sentiment_from_posts(self, posts_data: List[Dict[str, Any]]) -> Dict[str, int]:
        """
        포스트 데이터에서 감성 분석
        
        Args:
            posts_data: 포스트 데이터 리스트
        
        Returns:
            감성 분석 결과
        """
        sentiment_counts = {
            'positive': 0,
            'negative': 0,
            'neutral': 0
        }
        
        for post in posts_data:
            post_data = post['data']
            score = post_data.get('score', 0)
            upvote_ratio = post_data.get('upvote_ratio', 0.5)
            
            # 점수와 업보트 비율을 기반으로 감성 판단
            if score > 10 and upvote_ratio > 0.7:
                sentiment_counts['positive'] += 1
            elif score < -5 or upvote_ratio < 0.3:
                sentiment_counts['negative'] += 1
            else:
                sentiment_counts['neutral'] += 1
        
        return sentiment_counts
    
    def calculate_sentiment_score(self, sentiment_counts: Dict[str, int]) -> float:
        """
        감성 점수 계산 (-100 to 100)
        
        Args:
            sentiment_counts: 감성 카운트 딕셔너리
        
        Returns:
            감성 점수
        """
        total = sum(sentiment_counts.values())
        if total == 0:
            return 0.0
        
        positive_ratio = sentiment_counts['positive'] / total
        negative_ratio = sentiment_counts['negative'] / total
        
        # -100 (완전 부정) to 100 (완전 긍정)
        sentiment_score = (positive_ratio - negative_ratio) * 100
        
        return round(sentiment_score, 2)
    
    def collect_data(self, symbols: List[str]) -> Dict[str, Any]:
        """
        BaseCollector 추상 메서드 구현
        
        Args:
            symbols: 코인 심볼 리스트
        
        Returns:
            수집된 데이터
        """
        try:
            data = {}
            crypto_mentions = self.get_crypto_mentions(symbols)
            
            for symbol, mentions in crypto_mentions.items():
                sentiment_counts = {
                    'positive': mentions['positive_mentions'],
                    'negative': mentions['negative_mentions'],
                    'neutral': mentions['neutral_mentions']
                }
                
                sentiment_score = self.calculate_sentiment_score(sentiment_counts)
                community_interest = min(mentions['total_mentions'] * 2, 100)
                
                data[symbol] = {
                    'total_mentions': mentions['total_mentions'],
                    'sentiment_score': sentiment_score,
                    'community_interest': community_interest,
                    'sentiment_counts': sentiment_counts,
                    'subreddit_breakdown': mentions['subreddit_breakdown'],
                    'source': 'reddit',
                    'timestamp': datetime.now(timezone.utc).isoformat()
                }
            
            return data
        except Exception as e:
            log_error(self.logger, e, "Reddit 데이터 수집 실패")
            return {}
