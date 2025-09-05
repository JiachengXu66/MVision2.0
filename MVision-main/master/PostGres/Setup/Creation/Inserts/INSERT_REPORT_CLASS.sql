SET SCHEMA 'vision_data';
CREATE OR REPLACE FUNCTION INSERT_REPORT_CLASS(_report_id INT, _class_ids_json JSON)
RETURNS VOID AS $$
DECLARE
    _class_id BIGINT;
BEGIN
    SET SCHEMA 'vision_data';
        FOR _class_id IN SELECT value::INT
                          FROM json_array_elements_text(_class_ids_json) AS value
        LOOP
            INSERT INTO reportclasses(report_id, class_id)
            VALUES (_report_id, _class_id);
        END LOOP;
END;
$$ LANGUAGE plpgsql;
