SET SCHEMA 'vision_data';
CREATE OR REPLACE FUNCTION GET_NODE_FROM_ADDR(_address VARCHAR)
RETURNS JSONB AS $$
DECLARE
resolved_node_id BIGINT;
BEGIN
    SET SCHEMA 'vision_data';
    SELECT node_id INTO  resolved_node_id
    FROM nodes
    WHERE node_address = _address;
    RETURN jsonb_build_object('node_id', resolved_node_id::text);
END;
$$ LANGUAGE plpgsql;
