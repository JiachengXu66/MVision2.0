CREATE OR REPLACE FUNCTION GET_REPORT_DATA(
    _start_date TIMESTAMP, 
    _end_date TIMESTAMP, 
    _class_id INT, 
    _deployment_id INT,
    _threshold INT,
    _metric_value VARCHAR DEFAULT NULL 
)
RETURNS JSON
LANGUAGE plpgsql
AS $$
DECLARE
    result_json JSON;
BEGIN
    SET SCHEMA 'vision_data';
    SELECT json_agg(json_build_object(
        'classid', class_id,
        'creation_dates', creation_dates,
        'values', confidence,
        'metric', _metric_value 
    )) INTO result_json
    FROM (
        SELECT 
            class_id,
            array_agg(creation_date ORDER BY creation_date) AS creation_dates,
            array_agg(confidence ORDER BY creation_date) AS confidence
        FROM vision_data.datatotalentry
        WHERE deployment_id = _deployment_id
        AND creation_date BETWEEN _start_date AND _end_date
        AND class_id = _class_id 
        AND confidence > _threshold
        GROUP BY class_id
    ) AS subquery;

    RETURN result_json;
END;
$$;

