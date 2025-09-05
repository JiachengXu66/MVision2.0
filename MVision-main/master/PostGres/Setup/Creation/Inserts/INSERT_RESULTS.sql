SET SCHEMA 'vision_data';

CREATE OR REPLACE FUNCTION INSERT_RESULTS(
    _deployment_id INT,
    _data JSONB,
    _metric VARCHAR DEFAULT NULL
)
RETURNS SETOF INT AS $$
DECLARE
    result_id INT;
    data_element JSONB;
    _class_id INT;
    _creation_date TIMESTAMP;
    _confidence FLOAT;
BEGIN
    SET SCHEMA 'vision_data';
	FOR data_element IN SELECT * FROM jsonb_array_elements(_data)
    LOOP
        _class_id := (SELECT class_id FROM classes WHERE class_name = data_element->>'class');
        _creation_date := (data_element->>'timestamp')::TIMESTAMP;
        _confidence := (data_element->>'confidence')::FLOAT;

        INSERT INTO datatotalentry(deployment_id, class_id, creation_date, confidence, unit)
        VALUES (_deployment_id, _class_id, _creation_date, _confidence, _metric)
        RETURNING entry_num INTO result_id;

        RETURN NEXT result_id;
    END LOOP;
    RETURN;
END;
$$ LANGUAGE plpgsql;