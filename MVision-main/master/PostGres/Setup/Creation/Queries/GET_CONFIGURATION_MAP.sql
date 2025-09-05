SET SCHEMA 'vision_data';
CREATE OR REPLACE FUNCTION GET_CONFIGURATION_MAP()
RETURNS JSON
LANGUAGE plpgsql
AS $$
DECLARE
    result_json JSON;
BEGIN
    SET SCHEMA 'vision_data';
    WITH configurations AS (
        SELECT *
        FROM ModelConfiguration
    )
    SELECT jsonb_agg(to_jsonb(configurations.*))
    INTO result_json
    FROM configurations;

    RETURN result_json;
END;
$$;
