SET SCHEMA 'vision_data';

BEGIN;

CREATE TYPE FREQUENCY_UNIT AS ENUM ('second','minute','hour','day','week','month','year');

CREATE TABLE Nodes(
    node_id BIGSERIAL PRIMARY KEY,
    node_name VARCHAR NOT NULL,
    node_address VARCHAR NOT NULL,
    status_value VARCHAR NOT NULL,
    creation_date DATE NOT NULL
);

CREATE TABLE Devices(
    device_id BIGSERIAL PRIMARY KEY,
    device_name VARCHAR NOT NULL,
    creation_date DATE NOT NULL
);

CREATE TABLE NodeDevice(
    node_device_id BIGSERIAL PRIMARY KEY,
    node_id INT REFERENCES Nodes(node_id) NOT NULL,
    device_id INT REFERENCES Devices(device_id) NOT NULL,
    status_value VARCHAR NOT NULL,
    UNIQUE(node_id, device_id)
);

CREATE TABLE NodeKeys(
    key_value UUID PRIMARY KEY DEFAULT public.uuid_generate_v4(),
    node_id INT REFERENCES Nodes(node_id),
    creation_date DATE NOT NULL
);

CREATE TABLE Targets(
    target_id BIGSERIAL PRIMARY KEY,
    target_name VARCHAR NOT NULL,
    alt_name VARCHAR,
    creation_date DATE NOT NULL,
    status_value VARCHAR NOT NULL,
    access VARCHAR,
    dob DATE, 
    role VARCHAR
);

CREATE TABLE Sources(
    source_id BIGSERIAL PRIMARY KEY,
    source_name VARCHAR,
    company_name VARCHAR,
    vers VARCHAR,
    install_date DATE,
    licensing VARCHAR, 
    license_expiry_date DATE
);

CREATE TABLE Classes(
    class_id BIGSERIAL PRIMARY KEY,
    class_name VARCHAR NOT NULL,
    data_count INT NOT NULL
);

CREATE TABLE ClassSources(
    class_source_id BIGSERIAL PRIMARY KEY,
    class_id INT REFERENCES Classes(class_id) NOT NULL,
    source_id INT REFERENCES Sources(source_id) NOT NULL
);

CREATE TABLE ModelTask(
    task_id BIGSERIAL PRIMARY KEY,
    model_name VARCHAR NOT NULL,
    epochs INT NOT NULL,
    num_frames INT NOT NULL,
    shuffle_size INT NOT NULL,
    batch_size INT NOT NULL,
    creation_date DATE NOT NULL,
    status_value VARCHAR NOT NULL,
    train INT NOT NULL,
    test INT NOT NULL,
    verification INT NOT NULL
);

CREATE TABLE TaskClass(
    task_class_id BIGSERIAL PRIMARY KEY,
    class_id INT REFERENCES Classes(class_id) NOT NULL,
    task_id INT REFERENCES ModelTask(task_id) NOT NULL
);

CREATE TABLE TaskSources(
    task_sources_id BIGSERIAL PRIMARY KEY,
    source_id INT REFERENCES Sources(source_id) NOT NULL,
    task_id INT REFERENCES ModelTask(task_id) NOT NULL
);

CREATE TABLE Categories(
    category_id BIGSERIAL PRIMARY KEY,
    category_name VARCHAR
);

CREATE TABLE ClassCategories(
    class_category_id BIGSERIAL PRIMARY KEY,
    class_id INT REFERENCES Classes(class_id),
    category_id INT REFERENCES Categories(category_id)
);

CREATE TABLE ModelConfiguration(
    config_id BIGSERIAL PRIMARY KEY,
    config_name VARCHAR NOT NULL,
    epochs INT NOT NULL,
    num_frames INT NOT NULL,
    shuffle_size INT NOT NULL,
    batch_size INT NOT NULL,
    train INT NOT NULL,
    test INT NOT NULL,
    verification INT NOT NULL
);

CREATE TABLE Models(
    model_id BIGSERIAL PRIMARY KEY,
    model_name VARCHAR NOT NULL,
    epochs INT NOT NULL,
    num_frames INT NOT NULL,
    shuffle_size INT NOT NULL,
    batch_size INT NOT NULL,
    creation_date DATE NOT NULL,
    train INT NOT NULL,
    test INT NOT NULL,
    verification INT NOT NULL,
    location_name VARCHAR NOT NULL
);

CREATE TABLE ModelClasses(
    model_class_id BIGSERIAL PRIMARY KEY,
    model_id INT REFERENCES Models(model_id),
    class_id INT REFERENCES Classes(class_id)
);

CREATE TABLE ModelSources(
    model_sources_id BIGSERIAL PRIMARY KEY,
    source_id INT REFERENCES Sources(source_id) NOT NULL,
    model_id INT REFERENCES Models(model_id) NOT NULL
);

CREATE TABLE Deployments(
    deployment_id BIGSERIAL PRIMARY KEY,
    deployment_name VARCHAR NOT NULL,
    target_id INT REFERENCES Targets(target_id) NOT NULL,
    status_value VARCHAR NOT NULL,
    model_id INT REFERENCES Models(model_id) NOT NULL,
    creation_date DATE NOT NULL,
    start_date DATE NOT NULL,
    expiry_date DATE NOT NULL,
    node_id INT REFERENCES Nodes(node_id) NOT NULL,
    device_id INT REFERENCES Devices(device_id) NOT NULL
);

CREATE TABLE GraphMap(
    graph_id BIGSERIAL PRIMARY KEY,
    graph_type VARCHAR NOT NULL,
    value_type VARCHAR NOT NULL
);

CREATE TABLE Reports(
    report_id BIGSERIAL PRIMARY KEY,
    report_name VARCHAR NOT NULL,
    report_type VARCHAR NOT NULL,
    deployment_id INT REFERENCES Deployments(deployment_id)  NOT NULL,
    frequency_value INT NOT NULL,
    frequency_unit FREQUENCY_UNIT NOT NULL,
    creation_date DATE NOT NULL,
    range_value INT NOT NULL,
    range_unit FREQUENCY_UNIT NOT NULL,
    graph_id INT REFERENCES GraphMap(graph_id) NOT NULL,
    threshold INT NOT NULL
);

CREATE TABLE ReportClasses(
    report_class_id BIGSERIAL PRIMARY KEY,
    class_id INT REFERENCES Classes(class_id),
    report_id INT REFERENCES Reports(report_id)
);

CREATE TABLE DataTotalEntry(
    entry_num BIGSERIAL NOT NULL,
    deployment_id INT NOT NULL REFERENCES Deployments(deployment_id),
    class_id INT NOT NULL REFERENCES Classes(class_id), 
    creation_date TIMESTAMP NOT NULL,
    confidence INT NOT NULL,
    unit VARCHAR
)
PARTITION BY RANGE (creation_date);

END;