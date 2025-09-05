SET SCHEMA 'vision_data';
CREATE OR REPLACE FUNCTION GET_GRAPH_ID(_report_id INT)
RETURNS JSONB AS $$
DECLARE
    report_json JSONB; 
    graph_id JSONB; 
BEGIN
    SET SCHEMA 'vision_data';
    SELECT get_report(_report_id) INTO report_json;
    graph_id := report_json->0->'graph_id'; 
    
    RETURN graph_id;
END;
$$ LANGUAGE plpgsql;
