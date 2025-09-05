SET SCHEMA 'vision_data';
CREATE OR REPLACE FUNCTION GET_CLASS_MAP()
RETURNS JSON
LANGUAGE plpgsql
AS $$
DECLARE
    result_json JSON;
BEGIN
    SET SCHEMA 'vision_data';
    SELECT json_object_agg(class_id::text, class_name)
    INTO result_json
    FROM classes;

    RETURN result_json;
END;
$$;
