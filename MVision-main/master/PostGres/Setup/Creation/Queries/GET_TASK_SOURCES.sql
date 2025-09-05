SET SCHEMA 'vision_data';
CREATE OR REPLACE FUNCTION GET_TASK_SOURCES(_task_id INT)
RETURNS JSON
LANGUAGE plpgsql
AS $$
DECLARE
    result_json JSON;
BEGIN
    SET SCHEMA 'vision_data';
    SELECT json_build_object('sources', json_agg(source_id))
    INTO result_json
    FROM tasksources
    WHERE task_id = _task_id;

    RETURN result_json;
END;
$$;
