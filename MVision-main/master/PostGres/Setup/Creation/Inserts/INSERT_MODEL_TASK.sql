SET SCHEMA 'vision_data';
CREATE OR REPLACE FUNCTION INSERT_MODEL_TASK(
    _model_name VARCHAR,
    _epochs INT,
    _num_frames INT,
    _shuffle_size INT,
    _batch_size INT,
    _creation_date DATE,
    _status_value VARCHAR,
    _train INT,
    _test INT,
    _verification INT,
    _classes JSON, 
    _sources JSON  
)
RETURNS INT AS $$
DECLARE
    new_task_id INT;
    class INT;
    source INT;
    exists_flag INT;
BEGIN
    BEGIN
        SET SCHEMA 'vision_data';
        FOR class IN SELECT value::int FROM json_array_elements_text(_classes) AS value
        LOOP
            SELECT COUNT(*) INTO exists_flag FROM classes WHERE class_id = class; 
            IF exists_flag = 0 THEN
                RAISE EXCEPTION 'Class element % does not exist.', class;
            END IF;
        END LOOP;

        FOR source IN SELECT value::int FROM json_array_elements_text(_sources) AS value
        LOOP
            SELECT COUNT(*) INTO exists_flag FROM sources WHERE source_id = source; 
            IF exists_flag = 0 THEN
                RAISE EXCEPTION 'Source element % does not exist.', source;
            END IF;
        END LOOP;

        INSERT INTO modeltask(model_name, epochs, num_frames, shuffle_size, batch_size, creation_date, status_value, train, test, verification)
        VALUES (_model_name, _epochs, _num_frames, _shuffle_size, _batch_size, _creation_date, _status_value, _train, _test, _verification)
        RETURNING task_id INTO new_task_id;

        FOR class IN SELECT value::int FROM json_array_elements_text(_classes) AS value
        LOOP
            INSERT INTO TaskClass(class_id, task_id)
            VALUES (class, new_task_id);
        END LOOP;

        FOR source IN SELECT value::int FROM json_array_elements_text(_sources) AS value
        LOOP
            INSERT INTO TaskSources(source_id, task_id)
            VALUES (source, new_task_id);
        END LOOP;

        RETURN new_task_id;

    EXCEPTION WHEN OTHERS THEN
        RAISE;
    END;
END;
$$ LANGUAGE plpgsql;
