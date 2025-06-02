-- Création de la table Epidemic
CREATE TABLE Epidemic (
    id INT PRIMARY KEY AUTO_INCREMENT,
    name VARCHAR(255) NOT NULL,
    description TEXT,
    start_date DATE,
    end_date DATE,
    type VARCHAR(100)
);

-- Création de la table Localisation
CREATE TABLE Localisation (
    id INT PRIMARY KEY AUTO_INCREMENT,
    country VARCHAR(100) NOT NULL,
    region VARCHAR(150),
    iso_code VARCHAR(10) UNIQUE
);

-- Création de la table Data_source
CREATE TABLE Data_source (
    id INT PRIMARY KEY AUTO_INCREMENT,
    source_type VARCHAR(100) NOT NULL,
    reference VARCHAR(255),
    url VARCHAR(500) NOT NULL,
    INDEX idx_source_type (source_type)
);

-- Création de la table Daily_stats
CREATE TABLE Daily_stats (
    id INT PRIMARY KEY AUTO_INCREMENT,
    id_epidemic INT NOT NULL,
    id_source INT NOT NULL,
    id_loc INT NOT NULL,
    date DATE NOT NULL,
    cases INT DEFAULT 0,
    active INT DEFAULT 0,
    deaths INT DEFAULT 0,
    recovered INT DEFAULT 0,
    new_cases INT DEFAULT 0,
    new_deaths INT DEFAULT 0,
    new_recovered INT DEFAULT 0,
    FOREIGN KEY (id_epidemic) REFERENCES Epidemic(id) ON DELETE CASCADE,
    FOREIGN KEY (id_source) REFERENCES Data_source(id) ON DELETE CASCADE,
    FOREIGN KEY (id_loc) REFERENCES Localisation(id) ON DELETE CASCADE,
    UNIQUE KEY idx_unique_daily (id_epidemic, id_loc, date),
    INDEX idx_daily_epidemic (id_epidemic),
    INDEX idx_daily_loc (id_loc),
    INDEX idx_daily_date (date)
);

-- Création de la table Overall_stats
CREATE TABLE Overall_stats (
    id INT PRIMARY KEY AUTO_INCREMENT,
    id_epidemic INT NOT NULL,
    total_cases INT DEFAULT 0,
    total_deaths INT DEFAULT 0,
    fatality_ratio FLOAT DEFAULT 0.0,
    FOREIGN KEY (id_epidemic) REFERENCES Epidemic(id) ON DELETE CASCADE,
    INDEX idx_overall_epidemic (id_epidemic)
); 