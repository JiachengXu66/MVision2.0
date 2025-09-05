SET SCHEMA 'vision_data';

CREATE OR REPLACE FUNCTION INSERT_NODES(_node_name VARCHAR,_node_address VARCHAR,_creation_date DATE)
RETURNS INT AS $$
DECLARE
    new_node_id BIGINT;
BEGIN
    SET SCHEMA 'vision_data';

    INSERT INTO nodes(node_name, node_address, status_value, creation_date)
    VALUES (_node_name, _node_address,'Connected',_creation_date)
    RETURNING node_id into new_node_id;
    
    RETURN new_node_id;
END;
$$ LANGUAGE plpgsql;
