SET SCHEMA 'vision_data';
CREATE OR REPLACE FUNCTION GET_COUNT_MAP()
RETURNS json AS
$$
DECLARE
    targets_count bigint;
    reports_count bigint;
    deployments_count bigint;
    model_count bigint;
    nodes_count bigint;
    result_json json;
BEGIN
    SET SCHEMA 'vision_data';
    SELECT COUNT(*) INTO targets_count FROM targets;
    SELECT COUNT(*) INTO reports_count FROM reports;
    SELECT COUNT(*) INTO deployments_count FROM deployments;
    SELECT COUNT(*) INTO model_count FROM models;
    SELECT COUNT(*) INTO nodes_count FROM nodes;

    SELECT json_build_object(
        'deployment_count', deployments_count,
        'target_count', targets_count,
        'report_count', reports_count,
        'model_count', model_count,
        'nodes_count', nodes_count
    ) INTO result_json;

    RETURN result_json;
END;
$$
LANGUAGE plpgsql;
