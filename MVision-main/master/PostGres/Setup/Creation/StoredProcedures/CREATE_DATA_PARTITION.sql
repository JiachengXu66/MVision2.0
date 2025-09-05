SET SCHEMA 'vision_data';
CREATE OR REPLACE PROCEDURE CREATE_DATA_PARTITION()
LANGUAGE plpgsql
AS $$
DECLARE
    next_partition_start DATE;
    next_partition_end DATE;
    partition_name TEXT;
BEGIN   
    next_partition_start := (DATE_TRUNC('month', CURRENT_DATE) + INTERVAL '1 month')::DATE;
    next_partition_end := (DATE_TRUNC('month', next_partition_start) + INTERVAL '1 month')::DATE;
    partition_name := 'data_totalentry_' || TO_CHAR(next_partition_start, 'MMYYYY');
    
    IF NOT EXISTS(SELECT FROM pg_class WHERE relname = partition_name) THEN
        EXECUTE FORMAT('CREATE TABLE %I PARTITION OF DataTotalEntry FOR VALUES FROM (%L) TO (%L)', partition_name, next_partition_start, next_partition_end);
        EXECUTE FORMAT('ALTER TABLE %I ADD PRIMARY KEY (entry_num, creation_date)', partition_name);
        EXECUTE FORMAT('ALTER TABLE %I ADD CONSTRAINT deployment_key FOREIGN KEY (deployment_id) REFERENCES Deployments(deployment_id)', partition_name);
    END IF;
END;
$$;
DO $$
DECLARE
BEGIN
    CALL create_data_partition();
END;
 $$;
DO $$
DECLARE
    job_name TEXT='partition total data';
BEGIN
    PERFORM cron.schedule(job_name, '0 0 2,20 * *', 'create_data_partitions');
END;
 $$;