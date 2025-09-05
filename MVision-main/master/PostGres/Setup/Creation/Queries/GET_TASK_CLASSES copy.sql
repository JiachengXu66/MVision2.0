SET SCHEMA 'vision_data';
CREATE OR REPLACE FUNCTION GET_TASK_CLASSES(_task_id INT)
RETURNS JSON
LANGUAGE plpgsql
AS $$
DECLARE
    result_json JSON;
BEGIN
    SET SCHEMA 'vision_data';
    SELECT json_build_object('classes', json_agg(class_id))
    INTO result_json
    FROM taskclass
    WHERE task_id = _task_id;

    RETURN result_json;
END;
$$;
