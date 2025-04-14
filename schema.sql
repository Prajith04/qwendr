-- schema.sql

CREATE TABLE IF NOT EXISTS disease (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT UNIQUE NOT NULL
);

CREATE TABLE IF NOT EXISTS symptom (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT UNIQUE NOT NULL
);

CREATE TABLE IF NOT EXISTS disease_symptom (
    disease_id INTEGER,
    symptom_id INTEGER,
    PRIMARY KEY (disease_id, symptom_id),
    FOREIGN KEY (disease_id) REFERENCES disease(id),
    FOREIGN KEY (symptom_id) REFERENCES symptom(id)
);
