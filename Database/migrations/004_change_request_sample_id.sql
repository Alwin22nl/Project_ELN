ALTER TABLE change_requests
ADD COLUMN sample_id INTEGER REFERENCES samples(sample_id);