SET SCHEMA 'vision_data';
CREATE OR REPLACE FUNCTION INSERT_MODELS(_task_id BIGINT, _location_name VARCHAR)
RETURNS BIGINT AS $$
DECLARE
    new_model_id BIGINT;
BEGIN
    SET SCHEMA 'vision_data';
    INSERT INTO Models (model_name, epochs, num_frames, shuffle_size, batch_size, creation_date, train, test, verification, location_name)
    SELECT model_name, epochs, num_frames, shuffle_size, batch_size, creation_date, train, test, verification, _location_name
    FROM ModelTask WHERE task_id = _task_id
    RETURNING model_id INTO new_model_id; 
    
    INSERT INTO ModelClasses (model_id, class_id)
    SELECT new_model_id, class_id FROM TaskClass WHERE task_id = _task_id;
    
    INSERT INTO ModelSources (model_id, source_id)
    SELECT new_model_id, source_id FROM TaskSources WHERE task_id = _task_id;
    
    RETURN new_model_id;
END;
$$ LANGUAGE plpgsql;
