SET SCHEMA 'vision_data';
CREATE OR REPLACE FUNCTION GET_GRAPH_MAP()
RETURNS JSON
LANGUAGE plpgsql
AS $$
DECLARE
    result_json JSON;
BEGIN
    SET SCHEMA 'vision_data';
    SELECT json_object_agg(graph_id::text, json_build_object('graph_type', graph_type, 'value_type', value_type)) 
    INTO result_json
    FROM graphmap;

    RETURN result_json;
END;
$$;
