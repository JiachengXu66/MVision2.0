SET SCHEMA 'vision_data';
CREATE OR REPLACE FUNCTION INSERT_GRAPH_MAPS(
    _graph_type VARCHAR
)
RETURNS INT AS $$
DECLARE
    new_graph_id INT;
BEGIN
    SET SCHEMA 'vision_data';
    INSERT INTO graphmap(graph_type)
    VALUES (_graph_type)
    RETURNING graph_id INTO new_graph_id;
    
    RETURN new_graph_id;
END;
$$ LANGUAGE plpgsql;