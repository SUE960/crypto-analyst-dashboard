"""
분석가 목표가 데이터를 위한 Supabase 클라이언트
암호화폐 분석가들의 목표가, 신뢰도, 예측 정확도 등을 Supabase에 저장하고 관리
"""

import logging
from typing import List, Dict, Any, Optional
from datetime import datetime
from decimal import Decimal
import json

from supabase import create_client, Client
from database.models_analyst_targets import (
    AnalystProfile, AnalystTarget, PredictionAccuracy, 
    AnalystReliabilityHistory, CoinAnalystSummary,
    MarketInsight, SentimentAnalysis, MarketIndex, SectorAnalysis,
    CollectedAnalystData, validate_price_target, validate_analyst_profile,
    calculate_consensus_direction, calculate_price_dispersion
)
from utils.logger import log_error, log_info

logger = logging.getLogger(__name__)

class SupabaseClientAnalystTargets:
    """분석가 목표가 데이터를 위한 Supabase 클라이언트"""
    
    def __init__(self, supabase_url: str, supabase_key: str):
        """
        Supabase 클라이언트 초기화
        
        Args:
            supabase_url: Supabase 프로젝트 URL
            supabase_key: Supabase 서비스 역할 키
        """
        self.client: Client = create_client(supabase_url, supabase_key)
        self.logger = logger
    
    def insert_analyst_profile(self, profile: AnalystProfile) -> Optional[str]:
        """
        분석가 프로필 삽입
        
        Args:
            profile: 분석가 프로필 모델
        
        Returns:
            삽입된 레코드의 ID 또는 None
        """
        try:
            if not validate_analyst_profile(profile):
                log_error(self.logger, None, f"분석가 프로필 유효성 검증 실패: {profile.name}")
                return None
            
            data = profile.dict(exclude={'id'})
            data['created_at'] = datetime.now().isoformat()
            data['updated_at'] = datetime.now().isoformat()
            
            response = self.client.table('analyst_profiles').insert(data).execute()
            
            if response.data:
                profile_id = response.data[0]['id']
                log_info(self.logger, f"분석가 프로필 삽입 성공: {profile.name} (ID: {profile_id})")
                return profile_id
            else:
                log_error(self.logger, None, f"분석가 프로필 삽입 실패: {profile.name}")
                return None
                
        except Exception as e:
            log_error(self.logger, e, f"분석가 프로필 삽입 오류: {profile.name}")
            return None
    
    def upsert_analyst_profile(self, profile: AnalystProfile) -> Optional[str]:
        """
        분석가 프로필 업서트 (중복 제거)
        
        Args:
            profile: 분석가 프로필 모델
        
        Returns:
            레코드의 ID 또는 None
        """
        try:
            # 기존 프로필 확인
            existing = self.client.table('analyst_profiles')\
                .select('id')\
                .eq('source', profile.source)\
                .eq('source_id', profile.source_id)\
                .execute()
            
            if existing.data:
                # 업데이트
                profile_id = existing.data[0]['id']
                data = profile.dict(exclude={'id'})
                data['updated_at'] = datetime.now().isoformat()
                
                self.client.table('analyst_profiles')\
                    .update(data)\
                    .eq('id', profile_id)\
                    .execute()
                
                log_info(self.logger, f"분석가 프로필 업데이트 성공: {profile.name} (ID: {profile_id})")
                return profile_id
            else:
                # 새로 삽입
                return self.insert_analyst_profile(profile)
                
        except Exception as e:
            log_error(self.logger, e, f"분석가 프로필 업서트 오류: {profile.name}")
            return None
    
    def insert_analyst_target(self, target: AnalystTarget) -> Optional[str]:
        """
        분석가 목표가 삽입
        
        Args:
            target: 분석가 목표가 모델
        
        Returns:
            삽입된 레코드의 ID 또는 None
        """
        try:
            if not validate_price_target(target):
                log_error(self.logger, None, f"가격 목표가 유효성 검증 실패: {target.symbol}")
                return None
            
            data = target.dict(exclude={'id'})
            data['created_at'] = datetime.now().isoformat()
            data['updated_at'] = datetime.now().isoformat()
            
            # Decimal을 float로 변환
            if isinstance(data.get('current_price'), Decimal):
                data['current_price'] = float(data['current_price'])
            if isinstance(data.get('target_price'), Decimal):
                data['target_price'] = float(data['target_price'])
            if isinstance(data.get('price_change_percent'), Decimal):
                data['price_change_percent'] = float(data['price_change_percent'])
            
            response = self.client.table('analyst_targets').insert(data).execute()
            
            if response.data:
                target_id = response.data[0]['id']
                log_info(self.logger, f"분석가 목표가 삽입 성공: {target.symbol} (ID: {target_id})")
                return target_id
            else:
                log_error(self.logger, None, f"분석가 목표가 삽입 실패: {target.symbol}")
                return None
                
        except Exception as e:
            log_error(self.logger, e, f"분석가 목표가 삽입 오류: {target.symbol}")
            return None
    
    def insert_prediction_accuracy(self, accuracy: PredictionAccuracy) -> Optional[str]:
        """
        예측 정확도 삽입
        
        Args:
            accuracy: 예측 정확도 모델
        
        Returns:
            삽입된 레코드의 ID 또는 None
        """
        try:
            data = accuracy.dict(exclude={'id'})
            data['created_at'] = datetime.now().isoformat()
            
            # Decimal을 float로 변환
            if isinstance(data.get('predicted_price'), Decimal):
                data['predicted_price'] = float(data['predicted_price'])
            if isinstance(data.get('actual_price'), Decimal):
                data['actual_price'] = float(data['actual_price'])
            if isinstance(data.get('price_accuracy'), Decimal):
                data['price_accuracy'] = float(data['price_accuracy'])
            
            response = self.client.table('prediction_accuracy').insert(data).execute()
            
            if response.data:
                accuracy_id = response.data[0]['id']
                log_info(self.logger, f"예측 정확도 삽입 성공: {accuracy.symbol} (ID: {accuracy_id})")
                return accuracy_id
            else:
                log_error(self.logger, None, f"예측 정확도 삽입 실패: {accuracy.symbol}")
                return None
                
        except Exception as e:
            log_error(self.logger, e, f"예측 정확도 삽입 오류: {accuracy.symbol}")
            return None
    
    def insert_market_insight(self, insight: MarketInsight) -> Optional[str]:
        """
        시장 인사이트 삽입
        
        Args:
            insight: 시장 인사이트 모델
        
        Returns:
            삽입된 레코드의 ID 또는 None
        """
        try:
            data = insight.dict(exclude={'id'})
            data['created_at'] = datetime.now().isoformat()
            
            response = self.client.table('market_insights').insert(data).execute()
            
            if response.data:
                insight_id = response.data[0]['id']
                log_info(self.logger, f"시장 인사이트 삽입 성공: {insight.symbol} (ID: {insight_id})")
                return insight_id
            else:
                log_error(self.logger, None, f"시장 인사이트 삽입 실패: {insight.symbol}")
                return None
                
        except Exception as e:
            log_error(self.logger, e, f"시장 인사이트 삽입 오류: {insight.symbol}")
            return None
    
    def insert_sentiment_analysis(self, sentiment: SentimentAnalysis) -> Optional[str]:
        """
        감성 분석 삽입
        
        Args:
            sentiment: 감성 분석 모델
        
        Returns:
            삽입된 레코드의 ID 또는 None
        """
        try:
            data = sentiment.dict(exclude={'id'})
            data['created_at'] = datetime.now().isoformat()
            
            response = self.client.table('sentiment_analysis').insert(data).execute()
            
            if response.data:
                sentiment_id = response.data[0]['id']
                log_info(self.logger, f"감성 분석 삽입 성공: {sentiment.symbol} (ID: {sentiment_id})")
                return sentiment_id
            else:
                log_error(self.logger, None, f"감성 분석 삽입 실패: {sentiment.symbol}")
                return None
                
        except Exception as e:
            log_error(self.logger, e, f"감성 분석 삽입 오류: {sentiment.symbol}")
            return None
    
    def insert_market_index(self, index: MarketIndex) -> Optional[str]:
        """
        시장 지수 삽입
        
        Args:
            index: 시장 지수 모델
        
        Returns:
            삽입된 레코드의 ID 또는 None
        """
        try:
            data = index.dict(exclude={'id'})
            data['created_at'] = datetime.now().isoformat()
            
            response = self.client.table('market_indices').insert(data).execute()
            
            if response.data:
                index_id = response.data[0]['id']
                log_info(self.logger, f"시장 지수 삽입 성공: {index.name} (ID: {index_id})")
                return index_id
            else:
                log_error(self.logger, None, f"시장 지수 삽입 실패: {index.name}")
                return None
                
        except Exception as e:
            log_error(self.logger, e, f"시장 지수 삽입 오류: {index.name}")
            return None
    
    def insert_sector_analysis(self, sector: SectorAnalysis) -> Optional[str]:
        """
        섹터 분석 삽입
        
        Args:
            sector: 섹터 분석 모델
        
        Returns:
            삽입된 레코드의 ID 또는 None
        """
        try:
            data = sector.dict(exclude={'id'})
            data['created_at'] = datetime.now().isoformat()
            
            response = self.client.table('sector_analysis').insert(data).execute()
            
            if response.data:
                sector_id = response.data[0]['id']
                log_info(self.logger, f"섹터 분석 삽입 성공: {sector.metric} (ID: {sector_id})")
                return sector_id
            else:
                log_error(self.logger, None, f"섹터 분석 삽입 실패: {sector.metric}")
                return None
                
        except Exception as e:
            log_error(self.logger, e, f"섹터 분석 삽입 오류: {sector.metric}")
            return None
    
    def save_collected_data(self, data: CollectedAnalystData) -> Dict[str, int]:
        """
        수집된 데이터 일괄 저장
        
        Args:
            data: 수집된 분석가 데이터
        
        Returns:
            저장 결과 통계
        """
        results = {
            'analyst_profiles': 0,
            'analyst_targets': 0,
            'prediction_accuracy': 0,
            'market_insights': 0,
            'sentiment_analysis': 0,
            'market_indices': 0,
            'sector_analysis': 0,
            'errors': 0
        }
        
        try:
            log_info(self.logger, f"분석가 데이터 일괄 저장 시작: 총 {data.total_records}개 레코드")
            
            # 분석가 프로필 저장
            for profile in data.analyst_profiles:
                profile_id = self.upsert_analyst_profile(profile)
                if profile_id:
                    results['analyst_profiles'] += 1
                else:
                    results['errors'] += 1
            
            # 분석가 목표가 저장
            for target in data.analyst_targets:
                target_id = self.insert_analyst_target(target)
                if target_id:
                    results['analyst_targets'] += 1
                else:
                    results['errors'] += 1
            
            # 예측 정확도 저장
            for accuracy in data.prediction_accuracy:
                accuracy_id = self.insert_prediction_accuracy(accuracy)
                if accuracy_id:
                    results['prediction_accuracy'] += 1
                else:
                    results['errors'] += 1
            
            # 시장 인사이트 저장
            for insight in data.market_insights:
                insight_id = self.insert_market_insight(insight)
                if insight_id:
                    results['market_insights'] += 1
                else:
                    results['errors'] += 1
            
            # 감성 분석 저장
            for sentiment in data.sentiment_analysis:
                sentiment_id = self.insert_sentiment_analysis(sentiment)
                if sentiment_id:
                    results['sentiment_analysis'] += 1
                else:
                    results['errors'] += 1
            
            # 시장 지수 저장
            for index in data.market_indices:
                index_id = self.insert_market_index(index)
                if index_id:
                    results['market_indices'] += 1
                else:
                    results['errors'] += 1
            
            # 섹터 분석 저장
            for sector in data.sector_analysis:
                sector_id = self.insert_sector_analysis(sector)
                if sector_id:
                    results['sector_analysis'] += 1
                else:
                    results['errors'] += 1
            
            total_saved = sum(results[key] for key in results if key != 'errors')
            log_info(self.logger, f"분석가 데이터 저장 완료: {total_saved}개 성공, {results['errors']}개 실패")
            
            return results
            
        except Exception as e:
            log_error(self.logger, e, "분석가 데이터 일괄 저장 오류")
            results['errors'] += 1
            return results
    
    def get_analyst_targets_by_symbol(self, symbol: str, timeframe: Optional[str] = None) -> List[Dict[str, Any]]:
        """
        심볼별 분석가 목표가 조회
        
        Args:
            symbol: 코인 심볼
            timeframe: 시간대 필터 (선택사항)
        
        Returns:
            분석가 목표가 리스트
        """
        try:
            query = self.client.table('analyst_targets')\
                .select('*')\
                .eq('symbol', symbol.upper())\
                .eq('is_active', True)
            
            if timeframe:
                query = query.eq('timeframe', timeframe)
            
            response = query.order('published_at', desc=True).execute()
            
            return response.data if response.data else []
            
        except Exception as e:
            log_error(self.logger, e, f"분석가 목표가 조회 오류: {symbol}")
            return []
    
    def get_coin_analyst_summary(self, symbol: str) -> Optional[Dict[str, Any]]:
        """
        코인별 분석가 목표가 집계 조회
        
        Args:
            symbol: 코인 심볼
        
        Returns:
            코인별 분석가 집계 정보 또는 None
        """
        try:
            response = self.client.table('coin_analyst_summary')\
                .select('*')\
                .eq('symbol', symbol.upper())\
                .execute()
            
            return response.data[0] if response.data else None
            
        except Exception as e:
            log_error(self.logger, e, f"코인별 분석가 집계 조회 오류: {symbol}")
            return None
    
    def get_top_analysts(self, limit: int = 10) -> List[Dict[str, Any]]:
        """
        상위 분석가 조회 (신뢰도 기준)
        
        Args:
            limit: 조회할 분석가 수
        
        Returns:
            상위 분석가 리스트
        """
        try:
            response = self.client.table('analyst_profiles')\
                .select('*')\
                .eq('is_active', True)\
                .order('reliability_score', desc=True)\
                .limit(limit)\
                .execute()
            
            return response.data if response.data else []
            
        except Exception as e:
            log_error(self.logger, e, "상위 분석가 조회 오류")
            return []
    
    def get_recent_targets(self, limit: int = 20) -> List[Dict[str, Any]]:
        """
        최근 분석가 목표가 조회
        
        Args:
            limit: 조회할 목표가 수
        
        Returns:
            최근 목표가 리스트
        """
        try:
            response = self.client.table('analyst_targets')\
                .select('*')\
                .eq('is_active', True)\
                .order('published_at', desc=True)\
                .limit(limit)\
                .execute()
            
            return response.data if response.data else []
            
        except Exception as e:
            log_error(self.logger, e, "최근 목표가 조회 오류")
            return []
    
    def test_connection(self) -> bool:
        """
        Supabase 연결 테스트
        
        Returns:
            연결 성공 여부
        """
        try:
            response = self.client.table('analyst_profiles').select('id').limit(1).execute()
            log_info(self.logger, "Supabase 연결 테스트 성공")
            return True
        except Exception as e:
            log_error(self.logger, e, "Supabase 연결 테스트 실패")
            return False

# 테스트 함수
def test_supabase_client():
    """Supabase 클라이언트 테스트"""
    import os
    from dotenv import load_dotenv
    
    load_dotenv()
    
    supabase_url = os.getenv('SUPABASE_URL')
    supabase_key = os.getenv('SUPABASE_SERVICE_ROLE_KEY')
    
    if not supabase_url or not supabase_key:
        print("❌ Supabase 설정이 .env 파일에 없습니다.")
        return
    
    client = SupabaseClientAnalystTargets(supabase_url, supabase_key)
    
    print("=== Supabase 분석가 목표가 클라이언트 테스트 ===")
    
    # 연결 테스트
    if client.test_connection():
        print("✅ Supabase 연결 성공")
    else:
        print("❌ Supabase 연결 실패")
        return
    
    # 테스트 데이터 생성
    test_profile = AnalystProfile(
        name="Test Analyst",
        source="test",
        source_id="test_001",
        bio="테스트 분석가",
        expertise_areas=["technical", "fundamental"],
        reliability_score=85.0
    )
    
    test_target = AnalystTarget(
        symbol="BTC",
        current_price=Decimal("50000"),
        target_price=Decimal("60000"),
        timeframe="medium_term",
        timeframe_months=6,
        analysis_type="technical",
        confidence_level=8,
        reasoning="테스트 목표가"
    )
    
    # 프로필 저장 테스트
    profile_id = client.insert_analyst_profile(test_profile)
    if profile_id:
        print(f"✅ 분석가 프로필 저장 성공 (ID: {profile_id})")
        test_target.analyst_id = profile_id
    else:
        print("❌ 분석가 프로필 저장 실패")
    
    # 목표가 저장 테스트
    target_id = client.insert_analyst_target(test_target)
    if target_id:
        print(f"✅ 분석가 목표가 저장 성공 (ID: {target_id})")
    else:
        print("❌ 분석가 목표가 저장 실패")
    
    # 조회 테스트
    targets = client.get_analyst_targets_by_symbol("BTC")
    print(f"✅ BTC 목표가 조회: {len(targets)}개")
    
    recent_targets = client.get_recent_targets(5)
    print(f"✅ 최근 목표가 조회: {len(recent_targets)}개")

if __name__ == "__main__":
    test_supabase_client()
