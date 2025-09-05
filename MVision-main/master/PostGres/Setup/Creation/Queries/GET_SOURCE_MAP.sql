SET SCHEMA 'vision_data';
CREATE OR REPLACE FUNCTION GET_SOURCE_MAP()
RETURNS JSON
LANGUAGE plpgsql
AS $$
DECLARE
    result_json JSON;
BEGIN
    SET SCHEMA 'vision_data';
    SELECT json_object_agg(source_id::text, source_name)
    INTO result_json
    FROM sources;

    RETURN result_json;
END;
$$;
