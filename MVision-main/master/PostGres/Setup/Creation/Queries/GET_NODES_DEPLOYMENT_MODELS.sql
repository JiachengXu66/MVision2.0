SET SCHEMA 'vision_data';
CREATE OR REPLACE FUNCTION GET_NODES_DEPLOYMENT_MODELS(_node_id BIGINT, _device_id BIGINT, _current_date DATE)
RETURNS JSONB AS $$
DECLARE
    result_json JSONB;
BEGIN
    SET SCHEMA 'vision_data';
    SELECT JSONB_BUILD_OBJECT('deployments', JSONB_AGG(JSONB_BUILD_OBJECT('deployment_id', deployment_id, 'model_id', model_id)))
    INTO result_json
    FROM deployments
    WHERE _current_date BETWEEN start_date AND expiry_date
    AND node_id = _node_id
    AND device_id = _device_id
    AND status_value != 'Disabled';

    IF result_json IS NULL THEN
        result_json := '{"deployments": []}';
    END IF;

    RETURN result_json;
END;
$$ LANGUAGE plpgsql;
