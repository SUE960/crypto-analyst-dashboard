"""
Coinness 뉴스 데이터 수집 - 분석가 목표가 및 시장 분석 데이터 수집
https://coinness.com/news 에서 암호화폐 관련 뉴스와 분석가 의견을 수집합니다.
"""

import requests
from bs4 import BeautifulSoup
import time
import re
from typing import Dict, List, Optional, Any
from datetime import datetime, timedelta
import logging
from decimal import Decimal
import json

from collectors.base import BaseCollector
from utils.logger import log_error, log_info

logger = logging.getLogger(__name__)

class CoinnessNewsCollector(BaseCollector):
    """Coinness 뉴스 사이트 스크래핑을 통한 분석가 의견 및 시장 분석 데이터 수집기"""
    
    def __init__(self):
        super().__init__(
            api_key=None,  # 웹 스크래핑이므로 API 키 불필요
            base_url='https://coinness.com',
            rate_limit=8  # 분당 8회 제한 (웹사이트 부하 고려)
        )
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'ko-KR,ko;q=0.9,en-US;q=0.8,en;q=0.7',
            'Accept-Encoding': 'gzip, deflate',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1'
        })
        self.logger = logger
    
    def get_news_page(self, page: int = 1) -> Optional[str]:
        """
        뉴스 페이지 HTML 가져오기
        
        Args:
            page: 페이지 번호 (기본값: 1)
        
        Returns:
            HTML 내용 또는 None
        """
        try:
            url = f"{self.base_url}/news"
            if page > 1:
                url += f"?page={page}"
            
            response = requests.get(url, headers=self.session.headers, timeout=15)
            response.raise_for_status()
            
            return response.text
            
        except Exception as e:
            log_error(self.logger, e, f"Coinness 뉴스 페이지 {page} 조회 실패")
            return None
    
    def get_coin_specific_news(self, symbol: str) -> Optional[str]:
        """
        특정 코인 관련 뉴스 페이지 HTML 가져오기
        
        Args:
            symbol: 코인 심볼 (예: 'BTC')
        
        Returns:
            HTML 내용 또는 None
        """
        try:
            # Coinness의 코인별 뉴스 URL 패턴 (실제 구조에 따라 조정 필요)
            url = f"{self.base_url}/news/search?q={symbol}"
            
            response = requests.get(url, headers=self.session.headers, timeout=15)
            response.raise_for_status()
            
            return response.text
            
        except Exception as e:
            log_error(self.logger, e, f"Coinness {symbol} 뉴스 페이지 조회 실패")
            return None
    
    def parse_news_articles(self, html_content: str) -> Optional[List[Dict[str, Any]]]:
        """
        HTML에서 뉴스 기사 정보 파싱
        
        Args:
            html_content: HTML 내용
        
        Returns:
            뉴스 기사 리스트 또는 None
        """
        try:
            soup = BeautifulSoup(html_content, 'html.parser')
            articles = []
            
            # 뉴스 기사 요소 찾기 (실제 구조에 따라 조정 필요)
            article_elements = soup.find_all(['article', 'div'], class_=re.compile(r'article|news|post|item'))
            
            for element in article_elements:
                try:
                    # 제목 추출
                    title_elem = element.find(['h1', 'h2', 'h3', 'a'], class_=re.compile(r'title|headline'))
                    title = title_elem.get_text().strip() if title_elem else None
                    
                    # 링크 추출
                    link_elem = element.find('a', href=True)
                    link = link_elem['href'] if link_elem else None
                    if link and not link.startswith('http'):
                        link = f"{self.base_url}{link}"
                    
                    # 요약/내용 추출
                    content_elem = element.find(['p', 'div'], class_=re.compile(r'content|summary|excerpt'))
                    content = content_elem.get_text().strip() if content_elem else None
                    
                    # 날짜 추출
                    date_elem = element.find(['time', 'span'], class_=re.compile(r'date|time'))
                    date_text = date_elem.get_text().strip() if date_elem else None
                    
                    # 코인 심볼 추출
                    symbols = self._extract_symbols_from_text(title + ' ' + (content or ''))
                    
                    if title and len(title) > 10:  # 의미있는 제목만
                        articles.append({
                            'title': title,
                            'content': content,
                            'link': link,
                            'date_text': date_text,
                            'symbols': symbols,
                            'source': 'coinness',
                            'published_at': datetime.now().isoformat()
                        })
                
                except Exception as e:
                    continue
            
            return articles if articles else None
            
        except Exception as e:
            log_error(self.logger, e, "Coinness 뉴스 기사 파싱 실패")
            return None
    
    def _extract_symbols_from_text(self, text: str) -> List[str]:
        """
        텍스트에서 암호화폐 심볼 추출
        
        Args:
            text: 분석할 텍스트
        
        Returns:
            추출된 심볼 리스트
        """
        if not text:
            return []
        
        # 주요 암호화폐 심볼 패턴
        symbol_patterns = [
            r'\b(BTC|Bitcoin)\b',
            r'\b(ETH|Ethereum)\b',
            r'\b(SOL|Solana)\b',
            r'\b(XRP|Ripple)\b',
            r'\b(BNB|Binance)\b',
            r'\b(DOGE|Dogecoin)\b',
            r'\b(TRX|Tron)\b',
            r'\b(SUI|Sui)\b',
            r'\b(AVAX|Avalanche)\b',
            r'\b(TAO|Bittensor)\b',
            r'\b(USDC|USD Coin)\b',
            r'\b(USDT|Tether)\b',
            r'\b(ADA|Cardano)\b',
            r'\b(MATIC|Polygon)\b',
            r'\b(DOT|Polkadot)\b',
            r'\b(LINK|Chainlink)\b',
            r'\b(UNI|Uniswap)\b',
            r'\b(LTC|Litecoin)\b',
            r'\b(BCH|Bitcoin Cash)\b',
            r'\b(ATOM|Cosmos)\b'
        ]
        
        symbols = []
        for pattern in symbol_patterns:
            matches = re.findall(pattern, text, re.IGNORECASE)
            for match in matches:
                symbol = match.upper() if isinstance(match, str) else match[0].upper()
                if symbol not in symbols:
                    symbols.append(symbol)
        
        return symbols
    
    def extract_price_targets_from_news(self, articles: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        뉴스 기사에서 가격 목표가 정보 추출
        
        Args:
            articles: 뉴스 기사 리스트
        
        Returns:
            가격 목표가 리스트
        """
        targets = []
        
        for article in articles:
            text = (article.get('title', '') + ' ' + article.get('content', '')).lower()
            
            # 가격 목표가 패턴 찾기
            price_patterns = [
                r'(\$[\d,]+\.?\d*)\s*(?:목표|target|예상|예측|전망)',
                r'(?:목표|target|예상|예측|전망).*?(\$[\d,]+\.?\d*)',
                r'(\d+,\d+)\s*(?:달러|dollar|usd)',
                r'(\d+\.\d+)\s*(?:만원|만 달러)',
                r'(\d+)\s*(?:달러|dollar|usd).*?(?:목표|target|예상)'
            ]
            
            for pattern in price_patterns:
                matches = re.finditer(pattern, text, re.IGNORECASE)
                
                for match in matches:
                    try:
                        price_str = match.group(1).replace(',', '').replace('$', '')
                        target_price = float(price_str)
                        
                        # 시간대 정보 추출
                        timeframe_info = self._extract_timeframe_from_text(text)
                        
                        # 현재 가격 추정 (뉴스에서 직접 추출하기 어려우므로 기본값 사용)
                        current_price = target_price * 0.8  # 임시 추정값
                        
                        for symbol in article.get('symbols', []):
                            targets.append({
                                'symbol': symbol,
                                'current_price': current_price,
                                'target_price': target_price,
                                'timeframe': timeframe_info['type'],
                                'timeframe_months': timeframe_info['months'],
                                'analysis_type': 'sentiment',
                                'confidence_level': 5,  # 뉴스 기반이므로 낮은 신뢰도
                                'reasoning': f"Coinness 뉴스 기반 예측: {article.get('title', '')[:100]}",
                                'source': 'coinness',
                                'source_url': article.get('link'),
                                'published_at': article.get('published_at')
                            })
                    
                    except ValueError:
                        continue
        
        return targets
    
    def _extract_timeframe_from_text(self, text: str) -> Dict[str, Any]:
        """
        텍스트에서 시간대 정보 추출
        
        Args:
            text: 분석할 텍스트
        
        Returns:
            시간대 정보 딕셔너리
        """
        text = text.lower()
        
        if any(word in text for word in ['단기', 'short', '1개월', '1 month', '1m']):
            return {'type': 'short_term', 'months': 1}
        elif any(word in text for word in ['중기', 'medium', '3개월', '3 month', '3m', '분기']):
            return {'type': 'short_term', 'months': 3}
        elif any(word in text for word in ['6개월', '6 month', '6m', '반년']):
            return {'type': 'medium_term', 'months': 6}
        elif any(word in text for word in ['장기', 'long', '1년', '1 year', '1y', '12개월']):
            return {'type': 'medium_term', 'months': 12}
        elif any(word in text for word in ['2년', '2 year', '2y', '2025']):
            return {'type': 'long_term', 'months': 24}
        elif any(word in text for word in ['3년', '3 year', '3y', '2026']):
            return {'type': 'long_term', 'months': 36}
        else:
            return {'type': 'medium_term', 'months': 6}  # 기본값
    
    def analyze_sentiment(self, articles: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        뉴스 기사들의 감성 분석
        
        Args:
            articles: 뉴스 기사 리스트
        
        Returns:
            감성 분석 결과 딕셔너리
        """
        sentiment_keywords = {
            'positive': ['상승', '급등', '호재', '긍정', 'optimistic', 'bullish', 'rise', 'surge', 'positive'],
            'negative': ['하락', '급락', '악재', '부정', 'pessimistic', 'bearish', 'fall', 'crash', 'negative'],
            'neutral': ['보합', '횡보', '중립', 'neutral', 'sideways', 'stable']
        }
        
        sentiment_scores = {}
        
        for article in articles:
            text = (article.get('title', '') + ' ' + article.get('content', '')).lower()
            
            for symbol in article.get('symbols', []):
                if symbol not in sentiment_scores:
                    sentiment_scores[symbol] = {'positive': 0, 'negative': 0, 'neutral': 0, 'total': 0}
                
                for sentiment, keywords in sentiment_keywords.items():
                    for keyword in keywords:
                        if keyword in text:
                            sentiment_scores[symbol][sentiment] += 1
                
                sentiment_scores[symbol]['total'] += 1
        
        # 감성 점수 계산
        for symbol in sentiment_scores:
            scores = sentiment_scores[symbol]
            if scores['total'] > 0:
                scores['sentiment_score'] = (scores['positive'] - scores['negative']) / scores['total']
                scores['confidence'] = scores['total'] / 10  # 기사 수 기반 신뢰도
        
        return sentiment_scores
    
    def collect_data(self, symbol: str, start_date: datetime, end_date: datetime, interval: str = '1hour') -> List[Dict[str, Any]]:
        """
        데이터 수집 (BaseCollector 추상 메서드 구현)
        
        Args:
            symbol: 코인 심볼
            start_date: 시작 날짜
            end_date: 종료 날짜
            interval: 데이터 간격
        
        Returns:
            수집된 데이터 리스트
        """
        try:
            # 코인별 뉴스 수집
            html_content = self.get_coin_specific_news(symbol)
            if not html_content:
                return []
            
            # 뉴스 기사 파싱
            articles = self.parse_news_articles(html_content)
            if not articles:
                return []
            
            # 가격 목표가 추출
            targets = self.extract_price_targets_from_news(articles)
            if not targets:
                return []
            
            # BaseCollector 형식에 맞게 변환
            result = []
            for target in targets:
                result.append({
                    'symbol': target['symbol'],
                    'timestamp': datetime.now().isoformat(),
                    'price': float(target['target_price']),
                    'volume': 0,
                    'market_cap': 0,
                    'source': 'coinness'
                })
            
            return result
            
        except Exception as e:
            log_error(self.logger, e, f"Coinness 데이터 수집 실패: {symbol}")
            return []
    
    def collect_analyst_data(self, symbols: List[str], max_pages: int = 3) -> Dict[str, Any]:
        """
        여러 코인에 대한 분석가 데이터 수집
        
        Args:
            symbols: 코인 심볼 리스트
            max_pages: 최대 수집할 페이지 수
        
        Returns:
            수집된 분석가 데이터 딕셔너리
        """
        collected_data = {
            'analyst_profiles': [],
            'analyst_targets': [],
            'insights': [],
            'sentiment_analysis': []
        }
        
        # Coinness 분석가 프로필 생성
        analyst_profile = {
            'name': 'Coinness News Team',
            'source': 'coinness',
            'source_id': 'coinness_news',
            'profile_url': 'https://coinness.com/news',
            'bio': 'Coinness 뉴스팀의 암호화폐 시장 분석 및 뉴스',
            'expertise_areas': ['sentiment', 'news'],
            'reliability_score': 70.0,
            'followers_count': 15000,
            'is_active': True
        }
        collected_data['analyst_profiles'].append(analyst_profile)
        
        all_articles = []
        
        # 일반 뉴스 수집
        for page in range(1, max_pages + 1):
            try:
                log_info(self.logger, f"Coinness 뉴스 페이지 {page} 수집 중...")
                
                html_content = self.get_news_page(page)
                if not html_content:
                    continue
                
                articles = self.parse_news_articles(html_content)
                if articles:
                    all_articles.extend(articles)
                
                time.sleep(2)  # Rate limiting
                
            except Exception as e:
                log_error(self.logger, e, f"Coinness 뉴스 페이지 {page} 수집 실패")
                continue
        
        # 코인별 뉴스 수집
        for symbol in symbols:
            try:
                log_info(self.logger, f"Coinness {symbol} 뉴스 수집 중...")
                
                html_content = self.get_coin_specific_news(symbol)
                if html_content:
                    articles = self.parse_news_articles(html_content)
                    if articles:
                        all_articles.extend(articles)
                
                time.sleep(2)  # Rate limiting
                
            except Exception as e:
                log_error(self.logger, e, f"Coinness {symbol} 뉴스 수집 실패")
                continue
        
        # 중복 제거
        unique_articles = []
        seen_titles = set()
        
        for article in all_articles:
            title = article.get('title', '')
            if title and title not in seen_titles:
                unique_articles.append(article)
                seen_titles.add(title)
        
        # 가격 목표가 추출
        targets = self.extract_price_targets_from_news(unique_articles)
        collected_data['analyst_targets'].extend(targets)
        
        # 감성 분석
        sentiment_analysis = self.analyze_sentiment(unique_articles)
        collected_data['sentiment_analysis'].extend([
            {
                'symbol': symbol,
                'sentiment_score': data['sentiment_score'],
                'confidence': data['confidence'],
                'positive_count': data['positive'],
                'negative_count': data['negative'],
                'neutral_count': data['neutral'],
                'total_articles': data['total'],
                'source': 'coinness',
                'published_at': datetime.now().isoformat()
            }
            for symbol, data in sentiment_analysis.items()
        ])
        
        # 인사이트 생성
        for article in unique_articles[:20]:  # 최대 20개 기사만
            collected_data['insights'].append({
                'symbol': article.get('symbols', ['GENERAL'])[0],
                'type': 'news_analysis',
                'content': article.get('title', '') + ': ' + (article.get('content', '') or ''),
                'source': 'coinness',
                'confidence': 6,
                'analysis_type': 'sentiment',
                'published_at': article.get('published_at')
            })
        
        return collected_data

# 테스트 함수
def test_coinness_collector():
    """Coinness 수집기 테스트"""
    collector = CoinnessNewsCollector()
    
    # 테스트 코인들
    test_symbols = ['BTC', 'ETH', 'SOL']
    
    print("=== Coinness 뉴스 데이터 수집 테스트 ===")
    
    # 뉴스 페이지 테스트
    print("\n뉴스 페이지 수집 테스트...")
    html_content = collector.get_news_page(1)
    if html_content:
        print(f"✅ 뉴스 페이지 수집 성공 ({len(html_content)} 문자)")
        
        articles = collector.parse_news_articles(html_content)
        if articles:
            print(f"✅ 뉴스 기사 {len(articles)}개 파싱")
            for i, article in enumerate(articles[:3]):
                print(f"   {i+1}. {article.get('title', 'N/A')[:50]}...")
        else:
            print("❌ 뉴스 기사 파싱 실패")
    else:
        print("❌ 뉴스 페이지 수집 실패")
    
    # 코인별 뉴스 테스트
    for symbol in test_symbols:
        print(f"\n{symbol} 뉴스 수집 테스트...")
        
        html_content = collector.get_coin_specific_news(symbol)
        if html_content:
            print(f"✅ {symbol} 뉴스 페이지 수집 성공")
            
            articles = collector.parse_news_articles(html_content)
            if articles:
                print(f"✅ {symbol} 뉴스 기사 {len(articles)}개 파싱")
            else:
                print(f"❌ {symbol} 뉴스 기사 파싱 실패")
        else:
            print(f"❌ {symbol} 뉴스 페이지 수집 실패")
        
        time.sleep(2)  # Rate limiting

if __name__ == "__main__":
    test_coinness_collector()
