SET SCHEMA 'vision_data';  
CREATE OR REPLACE FUNCTION GET_DEVICES_DETAILS(_device_ids_json JSON)
RETURNS JSONB AS $$
DECLARE
    device_ids INT[]; 
    result_json JSONB;
BEGIN
    SET SCHEMA 'vision_data';  
    SELECT ARRAY_AGG(value::INT)
    INTO device_ids
    FROM json_array_elements_text(_device_ids_json) AS value;
    
    SELECT jsonb_build_object(
        'devices', jsonb_agg(jsonb_build_object(
            'device_id', device_id,
            'device_name', device_name,
            'creation_date', creation_date
        ))
    )
    INTO result_json
    FROM devices
    WHERE device_id = ANY(device_ids);

    RETURN result_json;
END;
$$ LANGUAGE plpgsql;
