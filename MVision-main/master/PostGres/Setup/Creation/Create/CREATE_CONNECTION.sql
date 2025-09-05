SET SCHEMA 'vision_data';
CREATE OR REPLACE FUNCTION CREATE_CONNECTION(_node_key_value UUID, _node_id BIGINT, _node_name VARCHAR, _node_address VARCHAR,_creation_date DATE)
RETURNS JSONB AS $$
DECLARE
    _existing_node_id BIGINT;
    _new_node_id BIGINT;
BEGIN
    SET SCHEMA 'vision_data';
    IF (_node_id IS NOT NULL AND (_node_name IS NOT NULL OR _node_address IS NOT NULL OR _creation_date IS NOT NULL)) OR (_node_id IS NULL AND (_node_name IS NULL OR _node_address IS NULL OR _creation_date IS NULL)) THEN
        RETURN '{"map": "error"}'::JSONB;
    END IF;

    SELECT node_id INTO _existing_node_id FROM nodekeys WHERE key_value = _node_key_value;
    IF FOUND THEN
        IF _existing_node_id IS NULL AND _node_id IS NULL THEN
            _new_node_id := INSERT_NODES(_node_name, _node_address, _creation_date);
            UPDATE nodekeys
            SET node_id = _new_node_id
            WHERE key_value = _node_key_value;
            RETURN jsonb_build_object('map', 'new', 'node_id', _new_node_id::text);
        ELSIF _existing_node_id = _node_id THEN 
            UPDATE nodes
            SET status_value = 'Connected'
            WHERE node_id = _node_id;
            RETURN jsonb_build_object('map', 'existing', 'node_id', _node_id::text);
        ELSE
            RETURN '{"map": "different"}'::JSONB;
        END IF;
    ELSE
        RETURN '{"map": "missing"}'::JSONB;
    END IF;
END;
$$ LANGUAGE plpgsql;
