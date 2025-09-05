SET SCHEMA 'vision_data';

CREATE OR REPLACE FUNCTION INSERT_REPORTS(
    _report_name VARCHAR,
    _report_type VARCHAR,
    _deployment_id INT,
    _frequency_value INT,
    _frequency_unit FREQUENCY_UNIT,
    _creation_date DATE,
    _range_value INT,
    _range_unit FREQUENCY_UNIT,
    _graph_id INT,
    _threshold INT
)
RETURNS INT AS $$
DECLARE
    new_report_id INT;
BEGIN
    SET SCHEMA 'vision_data';
    INSERT INTO reports(report_name, report_type, deployment_id, frequency_value, frequency_unit, creation_date, range_value, range_unit, graph_id, threshold)
    VALUES (_report_name, _report_type, _deployment_id, _frequency_value, _frequency_unit, _creation_date, _range_value, _range_unit, _graph_id, _threshold)
    RETURNING report_id INTO new_report_id;
    
    RETURN new_report_id;
END;
$$ LANGUAGE plpgsql;

