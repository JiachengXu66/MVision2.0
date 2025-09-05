SET SCHEMA 'vision_data';
CREATE OR REPLACE FUNCTION GET_REPORT_CLASSES(_report_id INT)
RETURNS JSON
LANGUAGE plpgsql
AS $$
DECLARE
    result_json JSON;
BEGIN
    SET SCHEMA 'vision_data';
    SELECT json_build_object('classes', json_agg(class_id))
    INTO result_json
    FROM ReportClasses
    WHERE report_id = _report_id;

    RETURN result_json;
END;
$$;