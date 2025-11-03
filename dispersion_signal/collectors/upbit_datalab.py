"""
Upbit DataLab 데이터 수집 - 분석가 목표가 및 시장 분석 데이터 수집
https://datalab.upbit.com 에서 업비트의 디지털 자산 분석 데이터를 수집합니다.
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

class UpbitDataLabCollector(BaseCollector):
    """Upbit DataLab 웹사이트 스크래핑을 통한 분석가 목표가 및 시장 분석 데이터 수집기"""
    
    def __init__(self):
        super().__init__(
            api_key=None,  # 웹 스크래핑이므로 API 키 불필요
            base_url='https://datalab.upbit.com',
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
    
    def get_main_page(self) -> Optional[str]:
        """
        메인 페이지 HTML 가져오기
        
        Returns:
            HTML 내용 또는 None
        """
        try:
            response = requests.get(self.base_url, headers=self.session.headers, timeout=15)
            response.raise_for_status()
            
            return response.text
            
        except Exception as e:
            log_error(self.logger, e, "Upbit DataLab 메인 페이지 조회 실패")
            return None
    
    def get_insights_page(self) -> Optional[str]:
        """
        인사이트 페이지 HTML 가져오기
        
        Returns:
            HTML 내용 또는 None
        """
        try:
            url = f"{self.base_url}/insights"
            response = requests.get(url, headers=self.session.headers, timeout=15)
            response.raise_for_status()
            
            return response.text
            
        except Exception as e:
            log_error(self.logger, e, "Upbit DataLab 인사이트 페이지 조회 실패")
            return None
    
    def get_sector_analysis_page(self) -> Optional[str]:
        """
        섹터 분석 페이지 HTML 가져오기
        
        Returns:
            HTML 내용 또는 None
        """
        try:
            url = f"{self.base_url}/sector"
            response = requests.get(url, headers=self.session.headers, timeout=15)
            response.raise_for_status()
            
            return response.text
            
        except Exception as e:
            log_error(self.logger, e, "Upbit DataLab 섹터 분석 페이지 조회 실패")
            return None
    
    def parse_market_indices(self, html_content: str) -> Optional[List[Dict[str, Any]]]:
        """
        HTML에서 시장 지수 정보 파싱
        
        Args:
            html_content: HTML 내용
        
        Returns:
            시장 지수 리스트 또는 None
        """
        try:
            soup = BeautifulSoup(html_content, 'html.parser')
            indices = []
            
            # 시장 지수 요소 찾기
            index_elements = soup.find_all(['div', 'span'], class_=re.compile(r'index|indices|market'))
            
            for element in index_elements:
                try:
                    text = element.get_text().strip()
                    
                    # 지수 이름과 값 추출
                    if '업비트' in text and ('지수' in text or 'Index' in text):
                        # 숫자 추출
                        numbers = re.findall(r'[\d,]+\.?\d*', text)
                        if len(numbers) >= 2:
                            try:
                                index_name = text.split()[0] if text.split() else 'Unknown'
                                index_value = float(numbers[0].replace(',', ''))
                                change_value = float(numbers[1].replace(',', ''))
                                
                                indices.append({
                                    'name': index_name,
                                    'value': index_value,
                                    'change': change_value,
                                    'source': 'upbit_datalab',
                                    'published_at': datetime.now().isoformat()
                                })
                            except ValueError:
                                continue
                
                except Exception as e:
                    continue
            
            return indices if indices else None
            
        except Exception as e:
            log_error(self.logger, e, "Upbit DataLab 시장 지수 파싱 실패")
            return None
    
    def parse_sector_analysis(self, html_content: str) -> Optional[List[Dict[str, Any]]]:
        """
        HTML에서 섹터 분석 정보 파싱
        
        Args:
            html_content: HTML 내용
        
        Returns:
            섹터 분석 리스트 또는 None
        """
        try:
            soup = BeautifulSoup(html_content, 'html.parser')
            sectors = []
            
            # 섹터 분석 요소 찾기
            sector_elements = soup.find_all(['div', 'section'], class_=re.compile(r'sector|analysis|chart'))
            
            for element in sector_elements:
                try:
                    text = element.get_text().strip()
                    
                    # 섹터 이름과 데이터 추출
                    if any(keyword in text for keyword in ['거래대금', '시가총액', '섹터', 'Sector']):
                        # 섹터별 데이터 추출
                        lines = text.split('\n')
                        
                        for line in lines:
                            if '거래대금' in line or '시가총액' in line:
                                # 숫자와 퍼센트 추출
                                numbers = re.findall(r'[\d,]+\.?\d*', line)
                                percentages = re.findall(r'[\d,]+\.?\d*%', line)
                                
                                if numbers and percentages:
                                    try:
                                        sector_data = {
                                            'metric': '거래대금' if '거래대금' in line else '시가총액',
                                            'value': float(numbers[0].replace(',', '')),
                                            'percentage': float(percentages[0].replace('%', '')),
                                            'source': 'upbit_datalab',
                                            'published_at': datetime.now().isoformat()
                                        }
                                        sectors.append(sector_data)
                                    except ValueError:
                                        continue
                
                except Exception as e:
                    continue
            
            return sectors if sectors else None
            
        except Exception as e:
            log_error(self.logger, e, "Upbit DataLab 섹터 분석 파싱 실패")
            return None
    
    def parse_insights(self, html_content: str) -> Optional[List[Dict[str, Any]]]:
        """
        HTML에서 인사이트 정보 파싱
        
        Args:
            html_content: HTML 내용
        
        Returns:
            인사이트 리스트 또는 None
        """
        try:
            soup = BeautifulSoup(html_content, 'html.parser')
            insights = []
            
            # 인사이트 요소 찾기
            insight_elements = soup.find_all(['div', 'article', 'section'], 
                                          class_=re.compile(r'insight|analysis|report|article'))
            
            for element in insight_elements:
                try:
                    # 제목 추출
                    title_elem = element.find(['h1', 'h2', 'h3', 'h4'], class_=re.compile(r'title|headline'))
                    title = title_elem.get_text().strip() if title_elem else None
                    
                    # 내용 추출
                    content_elem = element.find(['p', 'div'], class_=re.compile(r'content|description|summary'))
                    content = content_elem.get_text().strip() if content_elem else None
                    
                    # 링크 추출
                    link_elem = element.find('a', href=True)
                    link = link_elem['href'] if link_elem else None
                    if link and not link.startswith('http'):
                        link = f"{self.base_url}{link}"
                    
                    if title and len(title) > 10:  # 의미있는 제목만
                        # 코인 심볼 추출
                        symbols = self._extract_symbols_from_text(title + ' ' + (content or ''))
                        
                        insights.append({
                            'title': title,
                            'content': content,
                            'link': link,
                            'symbols': symbols,
                            'source': 'upbit_datalab',
                            'published_at': datetime.now().isoformat()
                        })
                
                except Exception as e:
                    continue
            
            return insights if insights else None
            
        except Exception as e:
            log_error(self.logger, e, "Upbit DataLab 인사이트 파싱 실패")
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
        
        # 주요 암호화폐 심볼 패턴 (한국어 포함)
        symbol_patterns = [
            r'\b(BTC|비트코인|Bitcoin)\b',
            r'\b(ETH|이더리움|Ethereum)\b',
            r'\b(SOL|솔라나|Solana)\b',
            r'\b(XRP|리플|Ripple)\b',
            r'\b(BNB|바이낸스|Binance)\b',
            r'\b(DOGE|도지코인|Dogecoin)\b',
            r'\b(TRX|트론|Tron)\b',
            r'\b(SUI|수이|Sui)\b',
            r'\b(AVAX|아발란체|Avalanche)\b',
            r'\b(TAO|비텐서|Bittensor)\b',
            r'\b(USDC|USD Coin)\b',
            r'\b(USDT|테더|Tether)\b',
            r'\b(ADA|카르다노|Cardano)\b',
            r'\b(MATIC|폴리곤|Polygon)\b',
            r'\b(DOT|폴카닷|Polkadot)\b',
            r'\b(LINK|체인링크|Chainlink)\b',
            r'\b(UNI|유니스왑|Uniswap)\b',
            r'\b(LTC|라이트코인|Litecoin)\b',
            r'\b(BCH|비트코인캐시|Bitcoin Cash)\b',
            r'\b(ATOM|코스모스|Cosmos)\b'
        ]
        
        symbols = []
        for pattern in symbol_patterns:
            matches = re.findall(pattern, text, re.IGNORECASE)
            for match in matches:
                symbol = match.upper() if isinstance(match, str) else match[0].upper()
                if symbol not in symbols:
                    symbols.append(symbol)
        
        return symbols
    
    def extract_price_targets_from_insights(self, insights: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        인사이트에서 가격 목표가 정보 추출
        
        Args:
            insights: 인사이트 리스트
        
        Returns:
            가격 목표가 리스트
        """
        targets = []
        
        for insight in insights:
            text = (insight.get('title', '') + ' ' + insight.get('content', '')).lower()
            
            # 가격 목표가 패턴 찾기 (한국어 포함)
            price_patterns = [
                r'(\d+,\d+)\s*(?:원|won|krw)',
                r'(\d+\.\d+)\s*(?:만원|만 달러)',
                r'(\$[\d,]+\.?\d*)\s*(?:목표|target|예상|예측|전망)',
                r'(?:목표|target|예상|예측|전망).*?(\$[\d,]+\.?\d*)',
                r'(\d+)\s*(?:달러|dollar|usd).*?(?:목표|target|예상)',
                r'(\d+,\d+)\s*(?:달러|dollar|usd)'
            ]
            
            for pattern in price_patterns:
                matches = re.finditer(pattern, text, re.IGNORECASE)
                
                for match in matches:
                    try:
                        price_str = match.group(1).replace(',', '').replace('$', '')
                        target_price = float(price_str)
                        
                        # 시간대 정보 추출
                        timeframe_info = self._extract_timeframe_from_text(text)
                        
                        # 현재 가격 추정
                        current_price = target_price * 0.85  # 임시 추정값
                        
                        for symbol in insight.get('symbols', []):
                            targets.append({
                                'symbol': symbol,
                                'current_price': current_price,
                                'target_price': target_price,
                                'timeframe': timeframe_info['type'],
                                'timeframe_months': timeframe_info['months'],
                                'analysis_type': 'fundamental',
                                'confidence_level': 8,  # 업비트 데이터랩은 높은 신뢰도
                                'reasoning': f"Upbit DataLab 인사이트 기반 예측: {insight.get('title', '')[:100]}",
                                'source': 'upbit_datalab',
                                'source_url': insight.get('link'),
                                'published_at': insight.get('published_at')
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
            # 인사이트 페이지 수집
            html_content = self.get_insights_page()
            if not html_content:
                return []
            
            # 인사이트 파싱
            insights = self.parse_insights(html_content)
            if not insights:
                return []
            
            # 가격 목표가 추출
            targets = self.extract_price_targets_from_insights(insights)
            if not targets:
                return []
            
            # BaseCollector 형식에 맞게 변환
            result = []
            for target in targets:
                if target['symbol'] == symbol:  # 특정 심볼만 필터링
                    result.append({
                        'symbol': target['symbol'],
                        'timestamp': datetime.now().isoformat(),
                        'price': float(target['target_price']),
                        'volume': 0,
                        'market_cap': 0,
                        'source': 'upbit_datalab'
                    })
            
            return result
            
        except Exception as e:
            log_error(self.logger, e, f"Upbit DataLab 데이터 수집 실패: {symbol}")
            return []
    
    def collect_analyst_data(self) -> Dict[str, Any]:
        """
        Upbit DataLab에서 분석가 데이터 수집
        
        Returns:
            수집된 분석가 데이터 딕셔너리
        """
        collected_data = {
            'analyst_profiles': [],
            'analyst_targets': [],
            'insights': [],
            'market_indices': [],
            'sector_analysis': []
        }
        
        # Upbit DataLab 분석가 프로필 생성
        analyst_profile = {
            'name': 'Upbit DataLab Research Team',
            'source': 'upbit_datalab',
            'source_id': 'upbit_datalab_research',
            'profile_url': 'https://datalab.upbit.com',
            'bio': '업비트 데이터랩 전문 분석팀의 디지털 자산 시장 분석',
            'expertise_areas': ['technical', 'fundamental', 'market'],
            'reliability_score': 90.0,  # 업비트는 높은 신뢰도
            'followers_count': 100000,
            'is_active': True
        }
        collected_data['analyst_profiles'].append(analyst_profile)
        
        try:
            log_info(self.logger, "Upbit DataLab 메인 페이지 수집 중...")
            
            # 메인 페이지 수집
            main_html = self.get_main_page()
            if main_html:
                # 시장 지수 파싱
                indices = self.parse_market_indices(main_html)
                if indices:
                    collected_data['market_indices'].extend(indices)
            
            time.sleep(2)  # Rate limiting
            
            log_info(self.logger, "Upbit DataLab 인사이트 페이지 수집 중...")
            
            # 인사이트 페이지 수집
            insights_html = self.get_insights_page()
            if insights_html:
                insights = self.parse_insights(insights_html)
                if insights:
                    collected_data['insights'].extend(insights)
                    
                    # 가격 목표가 추출
                    targets = self.extract_price_targets_from_insights(insights)
                    collected_data['analyst_targets'].extend(targets)
            
            time.sleep(2)  # Rate limiting
            
            log_info(self.logger, "Upbit DataLab 섹터 분석 페이지 수집 중...")
            
            # 섹터 분석 페이지 수집
            sector_html = self.get_sector_analysis_page()
            if sector_html:
                sectors = self.parse_sector_analysis(sector_html)
                if sectors:
                    collected_data['sector_analysis'].extend(sectors)
            
        except Exception as e:
            log_error(self.logger, e, "Upbit DataLab 데이터 수집 실패")
        
        return collected_data

# 테스트 함수
def test_upbit_datalab_collector():
    """Upbit DataLab 수집기 테스트"""
    collector = UpbitDataLabCollector()
    
    print("=== Upbit DataLab 분석가 데이터 수집 테스트 ===")
    
    # 메인 페이지 테스트
    print("\n메인 페이지 수집 테스트...")
    html_content = collector.get_main_page()
    if html_content:
        print(f"✅ 메인 페이지 수집 성공 ({len(html_content)} 문자)")
        
        indices = collector.parse_market_indices(html_content)
        if indices:
            print(f"✅ 시장 지수 {len(indices)}개 파싱")
            for index in indices[:3]:
                print(f"   {index['name']}: {index['value']}")
        else:
            print("❌ 시장 지수 파싱 실패")
    else:
        print("❌ 메인 페이지 수집 실패")
    
    # 인사이트 페이지 테스트
    print("\n인사이트 페이지 수집 테스트...")
    html_content = collector.get_insights_page()
    if html_content:
        print(f"✅ 인사이트 페이지 수집 성공")
        
        insights = collector.parse_insights(html_content)
        if insights:
            print(f"✅ 인사이트 {len(insights)}개 파싱")
            for i, insight in enumerate(insights[:3]):
                print(f"   {i+1}. {insight.get('title', 'N/A')[:50]}...")
        else:
            print("❌ 인사이트 파싱 실패")
    else:
        print("❌ 인사이트 페이지 수집 실패")
    
    # 섹터 분석 페이지 테스트
    print("\n섹터 분석 페이지 수집 테스트...")
    html_content = collector.get_sector_analysis_page()
    if html_content:
        print(f"✅ 섹터 분석 페이지 수집 성공")
        
        sectors = collector.parse_sector_analysis(html_content)
        if sectors:
            print(f"✅ 섹터 분석 {len(sectors)}개 파싱")
            for sector in sectors[:3]:
                print(f"   {sector['metric']}: {sector['value']} ({sector['percentage']}%)")
        else:
            print("❌ 섹터 분석 파싱 실패")
    else:
        print("❌ 섹터 분석 페이지 수집 실패")

if __name__ == "__main__":
    test_upbit_datalab_collector()
