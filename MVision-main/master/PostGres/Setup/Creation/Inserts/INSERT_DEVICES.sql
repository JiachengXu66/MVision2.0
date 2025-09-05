SET SCHEMA 'vision_data';

CREATE OR REPLACE FUNCTION INSERT_DEVICES(_device_names_json JSON, _creation_date DATE)
RETURNS JSONB AS $$
DECLARE
    _device_name VARCHAR;
    resolved_device_id INT;
    result_json JSONB := '[]'::JSONB; 
BEGIN
    SET SCHEMA 'vision_data';
    FOR _device_name IN SELECT value::VARCHAR
                      FROM json_array_elements_text(_device_names_json) AS value
    LOOP
        
        SELECT device_id INTO resolved_device_id FROM devices WHERE device_name = _device_name;

        IF resolved_device_id IS NULL THEN 
            INSERT INTO devices(device_name, creation_date)
            VALUES (_device_name, _creation_date)
            RETURNING device_id INTO resolved_device_id;
        END IF;
        
        result_json := result_json::jsonb || to_jsonb(resolved_device_id);
    END LOOP;

    RETURN result_json;
END;
$$ LANGUAGE plpgsql;

