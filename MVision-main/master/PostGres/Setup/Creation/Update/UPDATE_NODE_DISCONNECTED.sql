SET SCHEMA 'vision_data';
CREATE OR REPLACE FUNCTION UPDATE_NODE_CONNECTION(_node_address VARCHAR, _status_value VARCHAR)
RETURNS VARCHAR AS $$
BEGIN
    SET SCHEMA 'vision_data';
    UPDATE nodes
    SET status_value = _status_value
    WHERE node_address = _node_address;
    RETURN 'Node disconnected';
END;
$$ LANGUAGE plpgsql;
