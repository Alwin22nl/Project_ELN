BEGIN;

CREATE TABLE limits (
    limit_id SERIAL PRIMARY KEY,
    product_id INTEGER NOT NULL
        REFERENCES products(product_id),
    test_key VARCHAR(100) NOT NULL,
    field_name VARCHAR(100) NOT NULL,
    test_stage VARCHAR(30) NOT NULL
        DEFAULT 'initial',
    min_value NUMERIC,
    max_value NUMERIC,
    is_active BOOLEAN NOT NULL
        DEFAULT TRUE,
    created_by INTEGER
        REFERENCES users(user_id),
    created_at TIMESTAMP NOT NULL
        DEFAULT CURRENT_TIMESTAMP,
    
    CONSTRAINT limits_value_required
        CHECK (
            min_value IS NOT NULL
            OR max_value IS NOT NULL
        ),

    CONSTRAINT limits_valid_range
        CHECK (
            min_value IS NULL
            OR max_value IS NULL
            OR min_value <= max_value
        ),

    CONSTRAINT limits_valid_stage
        CHECK (
            test_stage IN (
                'initial',
                'after_storage'
            )
        )
);

CREATE UNIQUE INDEX uq_active_limits
ON limits (
    product_id,
    test_key,
    field_name,
    test_stage
)
WHERE is_active = TRUE;

CREATE INDEX idx_limits_product
ON limits(product_id);

COMMIT;

GRANT SELECT, INSERT, UPDATE
ON limits
TO eln_app;

GRANT USAGE, SELECT
ON SEQUENCE limits_limit_id_seq
TO eln_app;