"""
CoinPriceForecast 웹 스크래핑 - 분석가 목표가 데이터 수집
https://coinpriceforecast.com/ 에서 분석가 목표가 정보를 수집합니다.
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

class CoinPriceForecastCollector(BaseCollector):
    """CoinPriceForecast 웹사이트 스크래핑을 통한 분석가 목표가 데이터 수집기"""
    
    def __init__(self):
        super().__init__(
            api_key=None,  # 웹 스크래핑이므로 API 키 불필요
            base_url='https://coinpriceforecast.com',
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
    
    def get_coin_prediction_page(self, symbol: str) -> Optional[str]:
        """
        코인별 예측 페이지 HTML 가져오기
        
        Args:
            symbol: 코인 심볼 (예: 'BTC')
        
        Returns:
            HTML 내용 또는 None
        """
        try:
            # CoinPriceForecast의 예측 페이지 URL 패턴
            url = f"{self.base_url}/{symbol.lower()}-price-prediction"
            
            response = requests.get(url, headers=self.session.headers, timeout=15)
            response.raise_for_status()
            
            return response.text
            
        except Exception as e:
            log_error(self.logger, e, f"CoinPriceForecast {symbol} 예측 페이지 조회 실패")
            return None
    
    def parse_price_predictions(self, html_content: str, symbol: str) -> Optional[List[Dict[str, Any]]]:
        """
        HTML에서 가격 예측 정보 파싱
        
        Args:
            html_content: HTML 내용
            symbol: 코인 심볼
        
        Returns:
            가격 예측 리스트 또는 None
        """
        try:
            soup = BeautifulSoup(html_content, 'html.parser')
            predictions = []
            
            # 현재 가격 추출
            current_price_elem = soup.find(['span', 'div'], class_=re.compile(r'price|current'))
            current_price = None
            
            if current_price_elem:
                price_text = current_price_elem.get_text().strip()
                price_match = re.search(r'\$?([\d,]+\.?\d*)', price_text.replace(',', ''))
                if price_match:
                    current_price = float(price_match.group(1))
            
            # 예측 테이블 찾기
            prediction_tables = soup.find_all(['table', 'div'], class_=re.compile(r'prediction|forecast|target|table'))
            
            for table in prediction_tables:
                rows = table.find_all(['tr', 'div'], class_=re.compile(r'row|item'))
                
                for row in rows:
                    row_text = row.get_text().lower()
                    
                    # 시간대 정보 추출
                    timeframe_info = self._extract_timeframe_from_row(row_text)
                    
                    # 가격 정보 추출
                    price_matches = re.findall(r'\$?([\d,]+\.?\d*)', row.get_text())
                    
                    if len(price_matches) >= 1:
                        try:
                            target_price = float(price_matches[0].replace(',', ''))
                            
                            predictions.append({
                                'symbol': symbol.upper(),
                                'current_price': current_price,
                                'target_price': target_price,
                                'timeframe': timeframe_info['type'],
                                'timeframe_months': timeframe_info['months'],
                                'analysis_type': 'mixed',
                                'confidence_level': 7,
                                'reasoning': f'CoinPriceForecast {timeframe_info["text"]} 예측',
                                'source': 'coinpriceforecast',
                                'published_at': datetime.now().isoformat()
                            })
                        except ValueError:
                            continue
            
            # 추가적인 예측 섹션 찾기
            prediction_sections = soup.find_all(['div', 'section'], class_=re.compile(r'prediction|forecast|outlook'))
            
            for section in prediction_sections:
                section_text = section.get_text()
                
                # 연도별 예측 추출 (2025, 2026 등)
                year_matches = re.findall(r'(202[5-9])\s*[:\-]?\s*\$?([\d,]+\.?\d*)', section_text)
                
                for year, price_str in year_matches:
                    try:
                        target_price = float(price_str.replace(',', ''))
                        year_int = int(year)
                        months = (year_int - datetime.now().year) * 12
                        
                        predictions.append({
                            'symbol': symbol.upper(),
                            'current_price': current_price,
                            'target_price': target_price,
                            'timeframe': 'long_term',
                            'timeframe_months': months,
                            'analysis_type': 'fundamental',
                            'confidence_level': 6,
                            'reasoning': f'CoinPriceForecast {year}년 예측',
                            'source': 'coinpriceforecast',
                            'published_at': datetime.now().isoformat()
                        })
                    except ValueError:
                        continue
            
            # 단기/중기/장기 예측 추출
            timeframe_patterns = [
                (r'short\s*term|1\s*month|1m', 'short_term', 1),
                (r'medium\s*term|3\s*month|3m|quarter', 'short_term', 3),
                (r'6\s*month|6m|half\s*year', 'medium_term', 6),
                (r'long\s*term|1\s*year|1y|12\s*month', 'medium_term', 12),
                (r'2\s*year|2y|24\s*month', 'long_term', 24),
                (r'3\s*year|3y|36\s*month', 'long_term', 36)
            ]
            
            for pattern, timeframe_type, months in timeframe_patterns:
                matches = re.finditer(pattern, section_text, re.IGNORECASE)
                
                for match in matches:
                    # 해당 패턴 주변에서 가격 정보 찾기
                    start = max(0, match.start() - 100)
                    end = min(len(section_text), match.end() + 100)
                    context = section_text[start:end]
                    
                    price_match = re.search(r'\$?([\d,]+\.?\d*)', context)
                    if price_match:
                        try:
                            target_price = float(price_match.group(1).replace(',', ''))
                            
                            predictions.append({
                                'symbol': symbol.upper(),
                                'current_price': current_price,
                                'target_price': target_price,
                                'timeframe': timeframe_type,
                                'timeframe_months': months,
                                'analysis_type': 'mixed',
                                'confidence_level': 7,
                                'reasoning': f'CoinPriceForecast {pattern} 예측',
                                'source': 'coinpriceforecast',
                                'published_at': datetime.now().isoformat()
                            })
                        except ValueError:
                            continue
            
            return predictions if predictions else None
            
        except Exception as e:
            log_error(self.logger, e, f"CoinPriceForecast {symbol} 가격 예측 파싱 실패")
            return None
    
    def _extract_timeframe_from_row(self, row_text: str) -> Dict[str, Any]:
        """
        행 텍스트에서 시간대 정보 추출
        
        Args:
            row_text: 행 텍스트
        
        Returns:
            시간대 정보 딕셔너리
        """
        row_text = row_text.lower()
        
        if 'month' in row_text:
            month_match = re.search(r'(\d+)\s*month', row_text)
            if month_match:
                months = int(month_match.group(1))
                if months <= 3:
                    return {'type': 'short_term', 'months': months, 'text': f'{months}개월'}
                elif months <= 12:
                    return {'type': 'medium_term', 'months': months, 'text': f'{months}개월'}
                else:
                    return {'type': 'long_term', 'months': months, 'text': f'{months}개월'}
        
        if 'year' in row_text:
            year_match = re.search(r'(\d+)\s*year', row_text)
            if year_match:
                years = int(year_match.group(1))
                months = years * 12
                return {'type': 'long_term', 'months': months, 'text': f'{years}년'}
        
        if '2025' in row_text:
            return {'type': 'long_term', 'months': 18, 'text': '2025년'}
        elif '2026' in row_text:
            return {'type': 'long_term', 'months': 30, 'text': '2026년'}
        elif '2027' in row_text:
            return {'type': 'long_term', 'months': 42, 'text': '2027년'}
        
        return {'type': 'medium_term', 'months': 6, 'text': '6개월'}  # 기본값
    
    def get_technical_analysis(self, html_content: str, symbol: str) -> Optional[List[Dict[str, Any]]]:
        """
        HTML에서 기술적 분석 정보 추출
        
        Args:
            html_content: HTML 내용
            symbol: 코인 심볼
        
        Returns:
            기술적 분석 정보 리스트 또는 None
        """
        try:
            soup = BeautifulSoup(html_content, 'html.parser')
            analysis = []
            
            # 기술적 분석 관련 섹션 찾기
            tech_sections = soup.find_all(['div', 'section'], 
                                       class_=re.compile(r'technical|analysis|chart|indicator'))
            
            for section in tech_sections:
                text = section.get_text().strip()
                if len(text) > 100:  # 의미있는 길이의 텍스트만
                    analysis.append({
                        'symbol': symbol.upper(),
                        'type': 'technical_analysis',
                        'content': text[:800],  # 처음 800자만
                        'source': 'coinpriceforecast',
                        'confidence': 7,
                        'analysis_type': 'technical',
                        'published_at': datetime.now().isoformat()
                    })
            
            return analysis if analysis else None
            
        except Exception as e:
            log_error(self.logger, e, f"CoinPriceForecast {symbol} 기술적 분석 추출 실패")
            return None
    
    def get_fundamental_analysis(self, html_content: str, symbol: str) -> Optional[List[Dict[str, Any]]]:
        """
        HTML에서 펀더멘털 분석 정보 추출
        
        Args:
            html_content: HTML 내용
            symbol: 코인 심볼
        
        Returns:
            펀더멘털 분석 정보 리스트 또는 None
        """
        try:
            soup = BeautifulSoup(html_content, 'html.parser')
            analysis = []
            
            # 펀더멘털 분석 관련 섹션 찾기
            fund_sections = soup.find_all(['div', 'section'], 
                                        class_=re.compile(r'fundamental|outlook|future|adoption'))
            
            for section in fund_sections:
                text = section.get_text().strip()
                if len(text) > 100:  # 의미있는 길이의 텍스트만
                    analysis.append({
                        'symbol': symbol.upper(),
                        'type': 'fundamental_analysis',
                        'content': text[:800],  # 처음 800자만
                        'source': 'coinpriceforecast',
                        'confidence': 7,
                        'analysis_type': 'fundamental',
                        'published_at': datetime.now().isoformat()
                    })
            
            return analysis if analysis else None
            
        except Exception as e:
            log_error(self.logger, e, f"CoinPriceForecast {symbol} 펀더멘털 분석 추출 실패")
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
            html_content = self.get_coin_prediction_page(symbol)
            if not html_content:
                return []
            
            # 가격 예측 파싱
            predictions = self.parse_price_predictions(html_content, symbol)
            if not predictions:
                return []
            
            # BaseCollector 형식에 맞게 변환
            result = []
            for prediction in predictions:
                result.append({
                    'symbol': prediction['symbol'],
                    'timestamp': datetime.now().isoformat(),
                    'price': float(prediction['target_price']),
                    'volume': 0,
                    'market_cap': 0,
                    'source': 'coinpriceforecast'
                })
            
            return result
            
        except Exception as e:
            log_error(self.logger, e, f"CoinPriceForecast 데이터 수집 실패: {symbol}")
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
        
        # CoinPriceForecast 분석가 프로필 생성
        analyst_profile = {
            'name': 'CoinPriceForecast Research Team',
            'source': 'coinpriceforecast',
            'source_id': 'coinpriceforecast_research',
            'profile_url': 'https://coinpriceforecast.com/',
            'bio': 'CoinPriceForecast 전문 분석팀의 암호화폐 예측 및 분석',
            'expertise_areas': ['technical', 'fundamental'],
            'reliability_score': 80.0,
            'followers_count': 30000,
            'is_active': True
        }
        collected_data['analyst_profiles'].append(analyst_profile)
        
        for symbol in symbols:
            try:
                log_info(self.logger, f"CoinPriceForecast {symbol} 분석가 데이터 수집 중...")
                
                # 예측 페이지 가져오기
                html_content = self.get_coin_prediction_page(symbol)
                if not html_content:
                    continue
                
                # 가격 예측 파싱
                predictions = self.parse_price_predictions(html_content, symbol)
                if predictions:
                    collected_data['analyst_targets'].extend(predictions)
                
                # 기술적 분석 추출
                tech_analysis = self.get_technical_analysis(html_content, symbol)
                if tech_analysis:
                    collected_data['insights'].extend(tech_analysis)
                
                # 펀더멘털 분석 추출
                fund_analysis = self.get_fundamental_analysis(html_content, symbol)
                if fund_analysis:
                    collected_data['insights'].extend(fund_analysis)
                
                # Rate limiting
                time.sleep(2)
                
            except Exception as e:
                log_error(self.logger, e, f"CoinPriceForecast {symbol} 데이터 수집 실패")
                continue
        
        return collected_data

# 테스트 함수
def test_coinpriceforecast_collector():
    """CoinPriceForecast 수집기 테스트"""
    collector = CoinPriceForecastCollector()
    
    # 테스트 코인들
    test_symbols = ['BTC', 'ETH', 'SOL']
    
    print("=== CoinPriceForecast 분석가 데이터 수집 테스트 ===")
    
    for symbol in test_symbols:
        print(f"\n{symbol} 데이터 수집 중...")
        
        # 예측 페이지 가져오기
        html_content = collector.get_coin_prediction_page(symbol)
        if html_content:
            print(f"✅ HTML 페이지 수집 성공 ({len(html_content)} 문자)")
            
            # 가격 예측 파싱
            predictions = collector.parse_price_predictions(html_content, symbol)
            if predictions:
                print(f"✅ 예측 {len(predictions)}개 수집")
                for prediction in predictions:
                    print(f"   {prediction['timeframe']}: ${prediction['target_price']:.2f}")
            else:
                print("❌ 예측 파싱 실패")
            
            # 기술적 분석 추출
            tech_analysis = collector.get_technical_analysis(html_content, symbol)
            if tech_analysis:
                print(f"✅ 기술적 분석 {len(tech_analysis)}개 추출")
            else:
                print("❌ 기술적 분석 추출 실패")
            
            # 펀더멘털 분석 추출
            fund_analysis = collector.get_fundamental_analysis(html_content, symbol)
            if fund_analysis:
                print(f"✅ 펀더멘털 분석 {len(fund_analysis)}개 추출")
            else:
                print("❌ 펀더멘털 분석 추출 실패")
        else:
            print("❌ HTML 페이지 수집 실패")
        
        time.sleep(3)  # Rate limiting

if __name__ == "__main__":
    test_coinpriceforecast_collector()
