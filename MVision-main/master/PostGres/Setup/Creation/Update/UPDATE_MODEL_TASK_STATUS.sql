SET SCHEMA 'vision_data';
CREATE OR REPLACE FUNCTION UPDATE_MODEL_TASK_STATUS(_task_id INT, _status_value VARCHAR)
RETURNS VARCHAR AS $$
BEGIN
    SET SCHEMA 'vision_data';
    UPDATE modeltask
    SET status_value = _status_value
    WHERE task_id = _task_id;

    RETURN 'Task updated';
END;
$$ LANGUAGE plpgsql;
