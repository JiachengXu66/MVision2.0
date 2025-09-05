SET SCHEMA 'vision_data';
CREATE OR REPLACE FUNCTION UPDATE_DEPLOYMENT_STATUS(_deployment_id INT, _status_value VARCHAR)
RETURNS VARCHAR AS $$
BEGIN
    SET SCHEMA 'vision_data';
    UPDATE deployments
    SET status_value = _status_value
    WHERE deployment_id = _deployment_id;

    RETURN 'Task updated';
END;
$$ LANGUAGE plpgsql;
