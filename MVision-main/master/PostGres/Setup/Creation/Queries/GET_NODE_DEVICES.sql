SET SCHEMA 'vision_data';
CREATE OR REPLACE FUNCTION GET_NODE_DEVICES(_node_id BIGINT, _item_limit INT, _current_page INT)
RETURNS JSONB AS $$
DECLARE
    offset_value INT;
    result_json JSONB;
BEGIN
    SET SCHEMA 'vision_data';
    offset_value := (_current_page - 1) * _item_limit;
    
    SELECT json_build_object(
        'devices', json_agg(device_id)
    )
    INTO result_json
    FROM (
        SELECT device_id
        FROM nodedevice
        WHERE node_id = _node_id AND status_value = 'Connected'
        ORDER BY device_id
        LIMIT _item_limit OFFSET offset_value
    ) AS paginated_devices;

    RETURN result_json;
END;
$$ LANGUAGE plpgsql;
