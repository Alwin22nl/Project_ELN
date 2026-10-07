CREATE TABLE notifications (
    notification_id SERIAL PRIMARY KEY,

    user_id INTEGER NOT NULL
        REFERENCES users(user_id),

    notification_type VARCHAR(50) NOT NULL,

    title VARCHAR(255) NOT NULL,
    message TEXT,

    reference_type VARCHAR(50),
    reference_id INTEGER,

    link VARCHAR(500),

    is_read BOOLEAN NOT NULL DEFAULT FALSE,
    is_active BOOLEAN NOT NULL DEFAULT TRUE,

    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    read_at TIMESTAMP
);

CREATE INDEX idx_notifications_user_active
ON notifications (user_id, is_active);

GRANT USAGE ON SCHEMA public TO eln_app;

GRANT SELECT, INSERT, UPDATE, DELETE
ON ALL TABLES IN SCHEMA public
TO eln_app;

GRANT USAGE, SELECT, UPDATE
ON ALL SEQUENCES IN SCHEMA public
TO eln_app;
