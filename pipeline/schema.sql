-- This file should contain all code required to create & seed database tables.

DROP TABLE IF EXISTS request_interaction;
DROP TABLE IF EXISTS rating_interaction;
DROP TABLE IF EXISTS request CASCADE;
DROP TABLE IF EXISTS rating CASCADE;
DROP TABLE IF EXISTS exhibition CASCADE;
DROP TABLE IF EXISTS department CASCADE;
DROP TABLE IF EXISTS floor CASCADE;

CREATE TABLE department (
    department_id SMALLINT GENERATED ALWAYS AS IDENTITY,
    department_name VARCHAR(100),
    PRIMARY KEY (department_id)
);

CREATE TABLE floor (
    floor_id SMALLINT GENERATED ALWAYS AS IDENTITY,
    floor_name VARCHAR(100),
    PRIMARY KEY (floor_id)
);

CREATE TABLE request (
    request_id SMALLINT GENERATED ALWAYS AS IDENTITY,
    request_value SMALLINT NOT NULL,
    request_description VARCHAR(100) NOT NULL,
    PRIMARY KEY (request_id)
);

CREATE TABLE rating (
    rating_id SMALLINT GENERATED ALWAYS AS IDENTITY,
    rating_value SMALLINT,
    rating_description VARCHAR(100),
    PRIMARY KEY (rating_id)
);

CREATE TABLE exhibition (
    exhibition_id SMALLINT UNIQUE,
    exhibition_name VARCHAR(100) NOT NULL,
    exhibition_description TEXT NOT NULL,
    department_id SMALLINT NOT NULL,
    floor_id SMALLINT NOT NULL,
    exhibition_start_date DATE NOT NULL,
    public_id TEXT NOT NULL,
    PRIMARY KEY (exhibition_id),
    FOREIGN KEY (department_id) REFERENCES department(department_id),
    FOREIGN KEY (floor_id) REFERENCES floor(floor_id)
);

CREATE TABLE request_interaction (
    request_interaction_id SMALLINT GENERATED ALWAYS AS IDENTITY,
    exhibition_id SMALLINT,
    request_id SMALLINT,
    event_at TIMESTAMPTZ,
    PRIMARY KEY (request_interaction_id),
    FOREIGN KEY (exhibition_id) REFERENCES exhibition(exhibition_id),
    FOREIGN KEY (request_id) REFERENCES request(request_id)
);

CREATE TABLE rating_interaction (
    rating_interaction_id SMALLINT GENERATED ALWAYS AS IDENTITY,
    exhibition_id SMALLINT,
    rating_id SMALLINT,
    event_at TIMESTAMPTZ,
    PRIMARY KEY (rating_interaction_id),
    FOREIGN KEY (exhibition_id) REFERENCES exhibition(exhibition_id),
    FOREIGN KEY (rating_id) REFERENCES rating(rating_id)
);

INSERT INTO department (department_name)
VALUES
('Ecology'),
('Entomology'),
('Geology'),
('Paleontology'),
('Zoology');

INSERT INTO floor (floor_name)
VALUES
('1'),
('2'),
('3'),
('Vault');

INSERT INTO exhibition (exhibition_id, exhibition_name, exhibition_description, department_id, floor_id, exhibition_start_date, public_id)
VALUES 
(0, 'Measureless to Man', 'An immersive 3D experience: delve deep into a previously-inaccessible cave system.', 3, 1, '2021-08-23', 'EXH_00'),
(1, 'Adaptation', 'How insect evolution has kept pace with an industrialised world', 2, 4, '2019-07-01', 'EXH_01'),
(2, 'The Crenshaw Collection', 'An exhibition of 18th Century watercolours, mostly focused on South American wildlife.', 5, 2, '2021-03-03', 'EXH_02'),
(3, 'Cetacean Sensations', 'Whales: from ancient myth to critically endangered.', 5, 1, '2019-07-01', 'EXH_03'),
(4, 'Our Polluted World', 'A hard-hitting exploration of humanity''s impact on the environment.', 1, 3, '2021-05-12', 'EXH_04'),
(5, 'Thunder Lizards', 'How new research is making scientists rethink what dinosaurs really looked like.', 4, 1, '2023-02-01', 'EXH_05');

INSERT INTO request (request_value, request_description) VALUES 
(0, 'Assistance'),
(1, 'Emergency');

INSERT INTO rating (rating_value, rating_description) VALUES
(0, 'Terrible'),
(1, 'Bad'),
(2, 'Neutral'),
(3, 'Good'),
(4, 'Amazing');

