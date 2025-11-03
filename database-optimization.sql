-- ============================================
-- 데이터베이스 성능 최적화 스크립트
-- 인덱스 추가 및 쿼리 최적화
-- ============================================

-- ============================================
-- 1. 기존 테이블 인덱스 최적화
-- ============================================

-- cryptocurrencies 테이블 인덱스
CREATE INDEX IF NOT EXISTS idx_cryptocurrencies_symbol_active 
ON cryptocurrencies(symbol, is_active) 
WHERE is_active = true;

CREATE INDEX IF NOT EXISTS idx_cryptocurrencies_market_cap_rank 
ON cryptocurrencies(market_cap_rank) 
WHERE market_cap_rank IS NOT NULL;

-- market_data_daily 테이블 인덱스
CREATE INDEX IF NOT EXISTS idx_market_data_daily_crypto_timestamp 
ON market_data_daily(crypto_id, timestamp DESC);

CREATE INDEX IF NOT EXISTS idx_market_data_daily_timestamp_price 
ON market_data_daily(timestamp DESC, current_price) 
WHERE current_price IS NOT NULL;

CREATE INDEX IF NOT EXISTS idx_market_data_daily_volume_24h 
ON market_data_daily(volume_24h DESC) 
WHERE volume_24h IS NOT NULL;

-- price_history 테이블 인덱스
CREATE INDEX IF NOT EXISTS idx_price_history_crypto_timestamp_source 
ON price_history(crypto_id, timestamp DESC, data_source);

CREATE INDEX IF NOT EXISTS idx_price_history_timestamp_price 
ON price_history(timestamp DESC, price) 
WHERE price IS NOT NULL;

-- market_cap_data 테이블 인덱스
CREATE INDEX IF NOT EXISTS idx_market_cap_data_crypto_timestamp 
ON market_cap_data(crypto_id, timestamp DESC);

CREATE INDEX IF NOT EXISTS idx_market_cap_data_market_cap_rank 
ON market_cap_data(market_cap_rank) 
WHERE market_cap_rank IS NOT NULL;

CREATE INDEX IF NOT EXISTS idx_market_cap_data_timestamp_source 
ON market_cap_data(timestamp DESC, data_source);

-- social_data 테이블 인덱스
CREATE INDEX IF NOT EXISTS idx_social_data_crypto_timestamp 
ON social_data(crypto_id, timestamp DESC);

CREATE INDEX IF NOT EXISTS idx_social_data_timestamp_source 
ON social_data(timestamp DESC, data_source);

-- news_sentiment 테이블 인덱스
CREATE INDEX IF NOT EXISTS idx_news_sentiment_crypto_timestamp 
ON news_sentiment(crypto_id, timestamp DESC);

CREATE INDEX IF NOT EXISTS idx_news_sentiment_sentiment_score 
ON news_sentiment(sentiment_score) 
WHERE sentiment_score IS NOT NULL;

-- global_metrics 테이블 인덱스
CREATE INDEX IF NOT EXISTS idx_global_metrics_timestamp_source 
ON global_metrics(timestamp DESC, data_source);

CREATE INDEX IF NOT EXISTS idx_global_metrics_btc_dominance 
ON global_metrics(btc_dominance) 
WHERE btc_dominance IS NOT NULL;

-- dispersion_signals 테이블 인덱스
CREATE INDEX IF NOT EXISTS idx_dispersion_signals_crypto_timestamp 
ON dispersion_signals(crypto_id, timestamp DESC);

CREATE INDEX IF NOT EXISTS idx_dispersion_signals_signal_level_type 
ON dispersion_signals(signal_level, signal_type);

CREATE INDEX IF NOT EXISTS idx_dispersion_signals_timestamp_level 
ON dispersion_signals(timestamp DESC, signal_level);

-- dispersion_summary_daily 테이블 인덱스
CREATE INDEX IF NOT EXISTS idx_dispersion_summary_daily_date 
ON dispersion_summary_daily(summary_date DESC);

CREATE INDEX IF NOT EXISTS idx_dispersion_summary_daily_avg_dispersion 
ON dispersion_summary_daily(average_dispersion) 
WHERE average_dispersion IS NOT NULL;

-- multi_source_prices 테이블 인덱스
CREATE INDEX IF NOT EXISTS idx_multi_source_prices_crypto_timestamp 
ON multi_source_prices(crypto_id, timestamp DESC);

CREATE INDEX IF NOT EXISTS idx_multi_source_prices_price_dispersion 
ON multi_source_prices(price_dispersion) 
WHERE price_dispersion IS NOT NULL;

CREATE INDEX IF NOT EXISTS idx_multi_source_prices_sources_count 
ON multi_source_prices(price_sources_count);

-- reddit_sentiment 테이블 인덱스
CREATE INDEX IF NOT EXISTS idx_reddit_sentiment_crypto_timestamp 
ON reddit_sentiment(crypto_id, timestamp DESC);

CREATE INDEX IF NOT EXISTS idx_reddit_sentiment_sentiment_score 
ON reddit_sentiment(sentiment_score) 
WHERE sentiment_score IS NOT NULL;

CREATE INDEX IF NOT EXISTS idx_reddit_sentiment_total_mentions 
ON reddit_sentiment(total_mentions) 
WHERE total_mentions IS NOT NULL;

-- enhanced_dispersion_signals 테이블 인덱스
CREATE INDEX IF NOT EXISTS idx_enhanced_dispersion_signals_crypto_timestamp 
ON enhanced_dispersion_signals(crypto_id, timestamp DESC);

CREATE INDEX IF NOT EXISTS idx_enhanced_dispersion_signals_signal_level_type 
ON enhanced_dispersion_signals(signal_level, signal_type);

CREATE INDEX IF NOT EXISTS idx_enhanced_dispersion_signals_confidence_score 
ON enhanced_dispersion_signals(confidence_score) 
WHERE confidence_score IS NOT NULL;

-- ============================================
-- 2. 복합 인덱스 (자주 함께 사용되는 컬럼들)
-- ============================================

-- 가격 데이터 조회용 복합 인덱스
CREATE INDEX IF NOT EXISTS idx_price_data_composite 
ON market_data_daily(crypto_id, timestamp DESC, current_price, volume_24h) 
WHERE current_price IS NOT NULL AND volume_24h IS NOT NULL;

-- 분산도 신호 조회용 복합 인덱스
CREATE INDEX IF NOT EXISTS idx_dispersion_signals_composite 
ON dispersion_signals(crypto_id, timestamp DESC, signal_level, signal_type, price_dispersion);

-- 감성 분석 조회용 복합 인덱스
CREATE INDEX IF NOT EXISTS idx_sentiment_composite 
ON reddit_sentiment(crypto_id, timestamp DESC, sentiment_score, total_mentions) 
WHERE sentiment_score IS NOT NULL;

-- ============================================
-- 3. 부분 인덱스 (특정 조건의 데이터만 인덱싱)
-- ============================================

-- 활성 코인만 인덱싱
CREATE INDEX IF NOT EXISTS idx_active_cryptocurrencies_symbol 
ON cryptocurrencies(symbol) 
WHERE is_active = true;

-- 최근 데이터만 인덱싱 (30일)
CREATE INDEX IF NOT EXISTS idx_recent_market_data 
ON market_data_daily(crypto_id, current_price) 
WHERE timestamp >= NOW() - INTERVAL '30 days';

-- 높은 신호 레벨만 인덱싱
CREATE INDEX IF NOT EXISTS idx_high_dispersion_signals 
ON dispersion_signals(crypto_id, timestamp DESC) 
WHERE signal_level >= 4;

-- 긍정적 감성만 인덱싱
CREATE INDEX IF NOT EXISTS idx_positive_sentiment 
ON reddit_sentiment(crypto_id, timestamp DESC) 
WHERE sentiment_score > 50;

-- ============================================
-- 4. 함수 기반 인덱스
-- ============================================

-- 날짜별 그룹화를 위한 함수 인덱스
CREATE INDEX IF NOT EXISTS idx_market_data_date_trunc 
ON market_data_daily(DATE_TRUNC('day', timestamp), crypto_id);

-- 가격 변화율 계산을 위한 함수 인덱스
CREATE INDEX IF NOT EXISTS idx_price_change_percentage 
ON market_data_daily(crypto_id, timestamp DESC) 
WHERE price_change_percentage_24h IS NOT NULL;

-- ============================================
-- 5. 통계 정보 업데이트
-- ============================================

-- 테이블 통계 정보 업데이트 (쿼리 플래너 최적화)
ANALYZE cryptocurrencies;
ANALYZE market_data_daily;
ANALYZE price_history;
ANALYZE market_cap_data;
ANALYZE social_data;
ANALYZE news_sentiment;
ANALYZE global_metrics;
ANALYZE dispersion_signals;
ANALYZE dispersion_summary_daily;
ANALYZE multi_source_prices;
ANALYZE reddit_sentiment;
ANALYZE enhanced_dispersion_signals;

-- ============================================
-- 6. 쿼리 성능 모니터링 뷰
-- ============================================

-- 인덱스 사용률 모니터링 뷰
CREATE OR REPLACE VIEW index_usage_stats AS
SELECT 
    schemaname,
    tablename,
    indexname,
    idx_tup_read,
    idx_tup_fetch,
    CASE 
        WHEN idx_tup_read > 0 
        THEN ROUND((idx_tup_fetch::numeric / idx_tup_read::numeric) * 100, 2)
        ELSE 0 
    END as hit_ratio_percent
FROM pg_stat_user_indexes
WHERE schemaname = 'public'
ORDER BY idx_tup_read DESC;

-- 테이블 크기 모니터링 뷰
CREATE OR REPLACE VIEW table_size_stats AS
SELECT 
    schemaname,
    tablename,
    pg_size_pretty(pg_total_relation_size(schemaname||'.'||tablename)) as total_size,
    pg_size_pretty(pg_relation_size(schemaname||'.'||tablename)) as table_size,
    pg_size_pretty(pg_total_relation_size(schemaname||'.'||tablename) - pg_relation_size(schemaname||'.'||tablename)) as index_size,
    n_tup_ins as inserts,
    n_tup_upd as updates,
    n_tup_del as deletes
FROM pg_stat_user_tables
WHERE schemaname = 'public'
ORDER BY pg_total_relation_size(schemaname||'.'||tablename) DESC;

-- ============================================
-- 7. 성능 최적화 설정
-- ============================================

-- 메모리 설정 최적화 (세션 레벨)
-- SET work_mem = '256MB';  -- 정렬 및 해시 조인용 메모리
-- SET shared_buffers = '256MB';  -- 공유 버퍼 크기
-- SET effective_cache_size = '1GB';  -- OS 캐시 크기 추정

-- ============================================
-- 8. 정리 및 유지보수 함수
-- ============================================

-- 오래된 데이터 정리 함수
CREATE OR REPLACE FUNCTION cleanup_old_data(retention_days INTEGER DEFAULT 365)
RETURNS INTEGER AS $$
DECLARE
    deleted_count INTEGER := 0;
BEGIN
    -- 오래된 가격 히스토리 정리
    DELETE FROM price_history 
    WHERE timestamp < NOW() - INTERVAL '1 day' * retention_days;
    
    GET DIAGNOSTICS deleted_count = ROW_COUNT;
    
    -- 통계 정보 업데이트
    ANALYZE price_history;
    
    RETURN deleted_count;
END;
$$ LANGUAGE plpgsql;

-- 인덱스 재구성 함수
CREATE OR REPLACE FUNCTION rebuild_indexes()
RETURNS TEXT AS $$
DECLARE
    index_record RECORD;
    result_text TEXT := '';
BEGIN
    FOR index_record IN 
        SELECT indexname 
        FROM pg_indexes 
        WHERE schemaname = 'public'
    LOOP
        EXECUTE 'REINDEX INDEX ' || index_record.indexname;
        result_text := result_text || 'Rebuilt: ' || index_record.indexname || E'\n';
    END LOOP;
    
    RETURN result_text;
END;
$$ LANGUAGE plpgsql;

-- ============================================
-- 완료 메시지
-- ============================================

DO $$
BEGIN
    RAISE NOTICE '데이터베이스 성능 최적화 완료!';
    RAISE NOTICE '인덱스 생성, 통계 업데이트, 모니터링 뷰 생성 완료';
    RAISE NOTICE '정기적인 ANALYZE 실행을 권장합니다: ANALYZE;';
END $$;
