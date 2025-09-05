SET SCHEMA 'vision_data';
CREATE OR REPLACE FUNCTION GET_ADDR_FROM_NODE(_node_id BIGINT)
RETURNS JSONB AS $$
DECLARE
resolved_node_address VARCHAR;
BEGIN
    SET SCHEMA 'vision_data';
    SELECT node_address INTO  resolved_node_address
    FROM nodes
    WHERE node_id = _node_id;
    RETURN jsonb_build_object('node_address', resolved_node_address::text);
END;
$$ LANGUAGE plpgsql;
