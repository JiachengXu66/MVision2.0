SET SCHEMA 'vision_data';

CREATE OR REPLACE FUNCTION INSERT_DEPLOYMENTS(
    _deployment_name VARCHAR,
    _target_id INT,
    _status_value VARCHAR,
    _model_id INT,
    _creation_date DATE,
    _start_date DATE,
    _expiry_date DATE,
    _node_id INT,
    _device_id INT
)
RETURNS INT AS $$
DECLARE
    new_deployment_id INT;
BEGIN
    SET SCHEMA 'vision_data';
    INSERT INTO deployments(deployment_name, target_id, status_value, model_id, creation_date, start_date, expiry_date, node_id, device_id)
    VALUES (_deployment_name, _target_id, _status_value, _model_id, _creation_date, _start_date, _expiry_date, _node_id, _device_id)
    RETURNING deployment_id INTO new_deployment_id;
    
    RETURN new_deployment_id;
END;
$$ LANGUAGE plpgsql;

