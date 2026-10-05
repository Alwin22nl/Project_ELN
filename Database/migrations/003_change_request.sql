CREATE TABLE change_requests (
    change_request_id SERIAL PRIMARY KEY,
    requested_by INTEGER NOT NULL REFERENCES users(user_id),
    table_name VARCHAR(100) NOT NULL,
    record_id INTEGER NOT NULL,
    field_name VARCHAR(100) NOT NULL,

    old_value TEXT,
    new_value TEXT,

    reason TEXT NOT NULL,
    status VARCHAR(20) NOT NULL DEFAULT 'pending',
    requested_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    reviewed_by INTEGER REFERENCES users(user_id),
    reviewed_at TIMESTAMP,
    review_comment TEXT
);

ALTER TABLE change_requests
ADD CONSTRAINT change_requests_status_check
CHECK (status IN ('pending', 'approved', 'rejected'));