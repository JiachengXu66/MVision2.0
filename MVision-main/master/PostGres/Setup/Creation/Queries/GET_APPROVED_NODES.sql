SET SCHEMA 'vision_data';
CREATE OR REPLACE FUNCTION GET_APPROVED_NODES()
RETURNS JSON
LANGUAGE plpgsql
AS $$
DECLARE
    result_json JSON;
BEGIN
    SET SCHEMA 'vision_data';
    SELECT COALESCE(json_agg(node_address), '[]'::JSON) INTO result_json
    FROM nodes
    WHERE status_value = 'Connected';
    RETURN result_json;
END;
$$;