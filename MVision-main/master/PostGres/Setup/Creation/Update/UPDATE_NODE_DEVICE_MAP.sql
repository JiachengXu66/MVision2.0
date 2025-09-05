SET SCHEMA 'vision_data';
CREATE OR REPLACE FUNCTION UPDATE_NODE_DEVICE_MAP(_node_id INT, _device_ids_json JSON, _mode TEXT)
RETURNS VOID AS $$
DECLARE
    _device_id BIGINT;
    _exists BOOLEAN;
BEGIN
    SET SCHEMA 'vision_data';
    IF _mode = 'Connected' THEN
        FOR _device_id IN SELECT value::INT
                          FROM json_array_elements_text(_device_ids_json) AS value
        LOOP
            SELECT EXISTS(SELECT 1 FROM nodedevice
                          WHERE node_id = _node_id AND device_id = _device_id)
            INTO _exists;
            
            IF _exists THEN
                UPDATE nodedevice
                SET status_value = 'Connected'
                WHERE node_id = _node_id AND device_id = _device_id AND status_value <> 'Connected';
            ELSE
                INSERT INTO nodedevice(node_id, device_id, status_value)
                VALUES (_node_id, _device_id, 'Connected');
            END IF;
        END LOOP;
    ELSIF _mode = 'Disconnected' THEN
        UPDATE nodedevice
        SET status_value = 'Disconnected'
        WHERE node_id = _node_id
          AND device_id NOT IN (SELECT value::INT FROM json_array_elements_text(_device_ids_json))
          AND status_value <> 'Disconnected';
    END IF;
END;
$$ LANGUAGE plpgsql;
