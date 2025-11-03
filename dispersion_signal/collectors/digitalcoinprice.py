"""
DigitalCoinPrice 웹 스크래핑 - 분석가 목표가 데이터 수집
https://digitalcoinprice.com/forecast 에서 분석가 목표가 정보를 수집합니다.
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

class DigitalCoinPriceCollector(BaseCollector):
    """DigitalCoinPrice 웹사이트 스크래핑을 통한 분석가 목표가 데이터 수집기"""
    
    def __init__(self):
        super().__init__(
            api_key=None,  # 웹 스크래핑이므로 API 키 불필요
            base_url='https://digitalcoinprice.com',
            rate_limit=10  # 분당 10회 제한 (웹사이트 부하 고려)
        )
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.5',
            'Accept-Encoding': 'gzip, deflate',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1'
        })
        self.logger = logger
    
    def get_coin_forecast_page(self, symbol: str) -> Optional[str]:
        """
        코인별 예측 페이지 HTML 가져오기
        
        Args:
            symbol: 코인 심볼 (예: 'BTC')
        
        Returns:
            HTML 내용 또는 None
        """
        try:
            # DigitalCoinPrice의 예측 페이지 URL 패턴
            url = f"{self.base_url}/forecast/{symbol.lower()}"
            
            response = requests.get(url, headers=self.session.headers, timeout=15)
            response.raise_for_status()
            
            return response.text
            
        except Exception as e:
            log_error(self.logger, e, f"DigitalCoinPrice {symbol} 예측 페이지 조회 실패")
            return None
    
    def parse_price_targets(self, html_content: str, symbol: str) -> Optional[List[Dict[str, Any]]]:
        """
        HTML에서 가격 목표가 정보 파싱
        
        Args:
            html_content: HTML 내용
            symbol: 코인 심볼
        
        Returns:
            가격 목표가 리스트 또는 None
        """
        try:
            soup = BeautifulSoup(html_content, 'html.parser')
            targets = []
            
            # 현재 가격 추출
            current_price_elem = soup.find('span', class_='price') or soup.find('div', class_='current-price')
            current_price = None
            
            if current_price_elem:
                price_text = current_price_elem.get_text().strip()
                price_match = re.search(r'\$?([\d,]+\.?\d*)', price_text.replace(',', ''))
                if price_match:
                    current_price = float(price_match.group(1))
            
            # 예측 테이블 또는 섹션 찾기
            forecast_sections = soup.find_all(['div', 'section'], class_=re.compile(r'forecast|prediction|target'))
            
            for section in forecast_sections:
                # 시간대별 예측 찾기
                timeframes = ['short', 'medium', 'long', '1 month', '3 month', '6 month', '1 year', '2025', '2026']
                
                for timeframe_text in timeframes:
                    timeframe_elem = section.find(text=re.compile(timeframe_text, re.IGNORECASE))
                    if timeframe_elem:
                        parent = timeframe_elem.parent
                        
                        # 가격 정보 추출
                        price_elem = parent.find_next(['span', 'div', 'td'], class_=re.compile(r'price|target|prediction'))
                        if price_elem:
                            price_text = price_elem.get_text().strip()
                            price_match = re.search(r'\$?([\d,]+\.?\d*)', price_text.replace(',', ''))
                            
                            if price_match:
                                target_price = float(price_match.group(1))
                                
                                # 시간대 분류
                                timeframe = self._classify_timeframe(timeframe_text)
                                
                                targets.append({
                                    'symbol': symbol.upper(),
                                    'current_price': current_price,
                                    'target_price': target_price,
                                    'timeframe': timeframe['type'],
                                    'timeframe_months': timeframe['months'],
                                    'analysis_type': 'mixed',
                                    'confidence_level': 7,  # 기본 신뢰도
                                    'reasoning': f'DigitalCoinPrice {timeframe_text} 예측',
                                    'source': 'digitalcoinprice',
                                    'published_at': datetime.now().isoformat()
                                })
            
            # 추가적인 예측 정보가 있는지 확인
            prediction_cards = soup.find_all(['div', 'card'], class_=re.compile(r'prediction|forecast|target'))
            
            for card in prediction_cards:
                card_text = card.get_text().lower()
                
                # 가격 정보 추출
                price_matches = re.findall(r'\$?([\d,]+\.?\d*)', card_text)
                if len(price_matches) >= 2:  # 현재가와 목표가가 모두 있는 경우
                    try:
                        current = float(price_matches[0].replace(',', ''))
                        target = float(price_matches[1].replace(',', ''))
                        
                        # 시간대 정보 추출
                        timeframe_info = self._extract_timeframe_from_text(card_text)
                        
                        targets.append({
                            'symbol': symbol.upper(),
                            'current_price': current,
                            'target_price': target,
                            'timeframe': timeframe_info['type'],
                            'timeframe_months': timeframe_info['months'],
                            'analysis_type': 'mixed',
                            'confidence_level': 6,
                            'reasoning': f'DigitalCoinPrice 카드 예측',
                            'source': 'digitalcoinprice',
                            'published_at': datetime.now().isoformat()
                        })
                    except ValueError:
                        continue
            
            return targets if targets else None
            
        except Exception as e:
            log_error(self.logger, e, f"DigitalCoinPrice {symbol} 가격 목표가 파싱 실패")
            return None
    
    def _classify_timeframe(self, timeframe_text: str) -> Dict[str, Any]:
        """
        시간대 텍스트를 표준화된 시간대로 분류
        
        Args:
            timeframe_text: 시간대 텍스트
        
        Returns:
            시간대 정보 딕셔너리
        """
        timeframe_text = timeframe_text.lower()
        
        if any(word in timeframe_text for word in ['short', '1 month', '1m']):
            return {'type': 'short_term', 'months': 1}
        elif any(word in timeframe_text for word in ['medium', '3 month', '3m', 'quarter']):
            return {'type': 'short_term', 'months': 3}
        elif any(word in timeframe_text for word in ['6 month', '6m', 'half']):
            return {'type': 'medium_term', 'months': 6}
        elif any(word in timeframe_text for word in ['long', '1 year', '1y', '12 month']):
            return {'type': 'medium_term', 'months': 12}
        elif any(word in timeframe_text for word in ['2025']):
            return {'type': 'long_term', 'months': 18}
        elif any(word in timeframe_text for word in ['2026']):
            return {'type': 'long_term', 'months': 30}
        else:
            return {'type': 'medium_term', 'months': 6}  # 기본값
    
    def _extract_timeframe_from_text(self, text: str) -> Dict[str, Any]:
        """
        텍스트에서 시간대 정보 추출
        
        Args:
            text: 분석할 텍스트
        
        Returns:
            시간대 정보 딕셔너리
        """
        if 'month' in text:
            month_match = re.search(r'(\d+)\s*month', text)
            if month_match:
                months = int(month_match.group(1))
                if months <= 3:
                    return {'type': 'short_term', 'months': months}
                elif months <= 12:
                    return {'type': 'medium_term', 'months': months}
                else:
                    return {'type': 'long_term', 'months': months}
        
        if 'year' in text:
            year_match = re.search(r'(\d+)\s*year', text)
            if year_match:
                years = int(year_match.group(1))
                return {'type': 'long_term', 'months': years * 12}
        
        if '2025' in text:
            return {'type': 'long_term', 'months': 18}
        elif '2026' in text:
            return {'type': 'long_term', 'months': 30}
        
        return {'type': 'medium_term', 'months': 6}  # 기본값
    
    def get_analyst_insights(self, html_content: str, symbol: str) -> Optional[List[Dict[str, Any]]]:
        """
        HTML에서 분석가 인사이트 추출
        
        Args:
            html_content: HTML 내용
            symbol: 코인 심볼
        
        Returns:
            분석가 인사이트 리스트 또는 None
        """
        try:
            soup = BeautifulSoup(html_content, 'html.parser')
            insights = []
            
            # 분석 관련 텍스트 추출
            analysis_sections = soup.find_all(['div', 'section', 'article'], 
                                            class_=re.compile(r'analysis|insight|opinion|outlook'))
            
            for section in analysis_sections:
                text = section.get_text().strip()
                if len(text) > 50:  # 의미있는 길이의 텍스트만
                    insights.append({
                        'symbol': symbol.upper(),
                        'type': 'analysis',
                        'content': text[:500],  # 처음 500자만
                        'source': 'digitalcoinprice',
                        'confidence': 6,
                        'analysis_type': 'mixed',
                        'published_at': datetime.now().isoformat()
                    })
            
            return insights if insights else None
            
        except Exception as e:
            log_error(self.logger, e, f"DigitalCoinPrice {symbol} 인사이트 추출 실패")
            return None
    
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
            # 예측 페이지 가져오기
            html_content = self.get_coin_forecast_page(symbol)
            if not html_content:
                return []
            
            # 가격 목표가 파싱
            targets = self.parse_price_targets(html_content, symbol)
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
                    'source': 'digitalcoinprice'
                })
            
            return result
            
        except Exception as e:
            log_error(self.logger, e, f"DigitalCoinPrice 데이터 수집 실패: {symbol}")
            return []
    
    def collect_analyst_data(self, symbols: List[str]) -> Dict[str, Any]:
        """
        여러 코인에 대한 분석가 데이터 수집
        
        Args:
            symbols: 코인 심볼 리스트
        
        Returns:
            수집된 분석가 데이터 딕셔너리
        """
        collected_data = {
            'analyst_profiles': [],
            'analyst_targets': [],
            'insights': []
        }
        
        # DigitalCoinPrice 분석가 프로필 생성
        analyst_profile = {
            'name': 'DigitalCoinPrice Research Team',
            'source': 'digitalcoinprice',
            'source_id': 'digitalcoinprice_research',
            'profile_url': 'https://digitalcoinprice.com/forecast',
            'bio': 'DigitalCoinPrice 전문 분석팀의 암호화폐 예측',
            'expertise_areas': ['technical', 'fundamental'],
            'reliability_score': 75.0,
            'followers_count': 25000,
            'is_active': True
        }
        collected_data['analyst_profiles'].append(analyst_profile)
        
        for symbol in symbols:
            try:
                log_info(self.logger, f"DigitalCoinPrice {symbol} 분석가 데이터 수집 중...")
                
                # 예측 페이지 가져오기
                html_content = self.get_coin_forecast_page(symbol)
                if not html_content:
                    continue
                
                # 가격 목표가 파싱
                targets = self.parse_price_targets(html_content, symbol)
                if targets:
                    collected_data['analyst_targets'].extend(targets)
                
                # 분석가 인사이트 추출
                insights = self.get_analyst_insights(html_content, symbol)
                if insights:
                    collected_data['insights'].extend(insights)
                
                # Rate limiting
                time.sleep(2)
                
            except Exception as e:
                log_error(self.logger, e, f"DigitalCoinPrice {symbol} 데이터 수집 실패")
                continue
        
        return collected_data

# 테스트 함수
def test_digitalcoinprice_collector():
    """DigitalCoinPrice 수집기 테스트"""
    collector = DigitalCoinPriceCollector()
    
    # 테스트 코인들
    test_symbols = ['BTC', 'ETH', 'SOL']
    
    print("=== DigitalCoinPrice 분석가 데이터 수집 테스트 ===")
    
    for symbol in test_symbols:
        print(f"\n{symbol} 데이터 수집 중...")
        
        # 예측 페이지 가져오기
        html_content = collector.get_coin_forecast_page(symbol)
        if html_content:
            print(f"✅ HTML 페이지 수집 성공 ({len(html_content)} 문자)")
            
            # 가격 목표가 파싱
            targets = collector.parse_price_targets(html_content, symbol)
            if targets:
                print(f"✅ 목표가 {len(targets)}개 수집")
                for target in targets:
                    print(f"   {target['timeframe']}: ${target['target_price']:.2f}")
            else:
                print("❌ 목표가 파싱 실패")
            
            # 인사이트 추출
            insights = collector.get_analyst_insights(html_content, symbol)
            if insights:
                print(f"✅ 인사이트 {len(insights)}개 추출")
            else:
                print("❌ 인사이트 추출 실패")
        else:
            print("❌ HTML 페이지 수집 실패")
        
        time.sleep(3)  # Rate limiting

if __name__ == "__main__":
    test_digitalcoinprice_collector()
