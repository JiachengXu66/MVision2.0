SET SCHEMA 'vision_data';
CREATE OR REPLACE FUNCTION GET_DEVICE_FROM_NAME(_device_name VARCHAR)
RETURNS JSONB AS $$
DECLARE
resolved_device_id BIGINT;
BEGIN
    SET SCHEMA 'vision_data';
    SELECT device_id INTO resolved_device_id
    FROM devices
    WHERE device_name = _device_name;

    RETURN jsonb_build_object('device_id', resolved_device_id::text);
END;
$$ LANGUAGE plpgsql;
