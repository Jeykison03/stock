DROP TABLE IF EXISTS stock_prices;
DROP TABLE IF EXISTS stock_analysis;

CREATE TABLE stock_prices (
    id SERIAL PRIMARY KEY,
    symbol VARCHAR(10) NOT NULL,
    date DATE NOT NULL,
    open NUMERIC(10, 4) NOT NULL,
    high NUMERIC(10, 4) NOT NULL,
    low NUMERIC(10, 4) NOT NULL,
    close NUMERIC(10, 4) NOT NULL,
    volume BIGINT NOT NULL  -- BIGINT because volume can be very large (millions)
);

ALTER TABLE stock_prices
ADD CONSTRAINT unique_symbol_date UNIQUE (symbol, date);  -- Ensure no duplicate entries for the same stock and date IF WE RUN THE CODE TWICE 

CREATE INDEX idx_symbol ON stock_prices(symbol);
CREATE INDEX idx_date ON stock_prices(date);


CREATE TABLE stock_analysis (
    id SERIAL PRIMARY KEY,
    symbol VARCHAR(10) NOT NULL,
    date DATE NOT NULL,
    open NUMERIC(10, 4) NOT NULL,
    high NUMERIC(10, 4) NOT NULL,
    low NUMERIC(10, 4) NOT NULL,
    close NUMERIC(10, 4) NOT NULL,
    volume BIGINT NOT NULL,
    sma_5 NUMERIC(10, 4),
    sma_20 NUMERIC(10, 4),
    rsi_14 NUMERIC(10, 4),
    macd NUMERIC(10, 4),
    daily_return NUMERIC(10, 4),
    daily_range NUMERIC(10, 4),
    processed_at TIMESTAMP  DEFAULT NOW()
);

ALTER TABLE stock_analysis
ADD CONSTRAINT unique_stock_analysis_symbol_date UNIQUE (symbol, date);
 
CREATE INDEX idx_stock_analysis_symbol ON stock_analysis(symbol);
CREATE INDEX idx_stock_analysis_date   ON stock_analysis (date);