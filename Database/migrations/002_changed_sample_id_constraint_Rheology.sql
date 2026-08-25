ALTER TABLE rheology
DROP CONSTRAINT uq_rheology_sample;

ALTER TABLE rheology
ADD CONSTRAINT uq_rheology_sample_afterstorage
UNIQUE (sample_id, afterstorage_id);