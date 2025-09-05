SET SCHEMA 'vision_data';
CREATE OR REPLACE FUNCTION UPDATE_DISCONNECT_ALL_DEVICES(_node_id INT)
RETURNS VOID AS $$
BEGIN
    SET SCHEMA 'vision_data';
    UPDATE nodedevice
    SET status_value = 'Disconnected'
    WHERE node_id = _node_id;
END;
$$ LANGUAGE plpgsql;

