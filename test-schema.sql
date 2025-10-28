-- 간단한 테스트용 테이블 생성
CREATE TABLE IF NOT EXISTS test_table (
    id SERIAL PRIMARY KEY,
    name VARCHAR(50),
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- 테스트 데이터 삽입
INSERT INTO test_table (name) VALUES ('test') ON CONFLICT DO NOTHING;

-- 테이블 확인
SELECT * FROM test_table;
