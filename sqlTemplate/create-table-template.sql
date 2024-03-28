-- Active: 1711137133822@@127.0.0.1@5432@diplom@public
CREATE TABLE CategoryReplacement(  
    id int NOT NULL PRIMARY KEY GENERATED ALWAYS AS IDENTITY,
    word VARCHAR,
    replacement VARCHAR
);


CREATE TABLE ReferenceWord(  
    id int NOT NULL PRIMARY KEY GENERATED ALWAYS AS IDENTITY,
    categoryId INT,
    mfcc BYTEA,
    weight FLOAT,
    FOREIGN KEY (categoryId) REFERENCES CategoryReplacement(id)
);

