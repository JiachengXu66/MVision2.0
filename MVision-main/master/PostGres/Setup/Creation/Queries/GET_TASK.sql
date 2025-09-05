SET SCHEMA 'vision_data';
CREATE OR REPLACE FUNCTION GET_TASK(_task_id INT)
RETURNS JSONB AS $$
DECLARE
    result_json JSONB;
BEGIN
    SET SCHEMA 'vision_data';
    WITH task_entry AS (
        SELECT *
        FROM modeltask
        WHERE task_id = _task_id
    )
    SELECT jsonb_agg(to_jsonb(task_entry.*))
    INTO result_json
    FROM task_entry;

    RETURN result_json;
END;
$$ LANGUAGE plpgsql;
