-- CREATE INTERN TABLE
CREATE TABLE IF NOT EXISTS interns (
    intern_id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    registration_number INTEGER UNIQUE NOT NULL,
    email TEXT,
    start_date TEXT,
    end_date TEXT,
    working_days TEXT,
    working_hours TEXT,
    venue_id INTEGER,
    term TEXT NOT NULL,
    last_update TEXT DEFAULT (strftime('%Y-%m-%d %H:%M:%S', 'now', 'localtime')),
    FOREIGN KEY (venue_id) REFERENCES venues(venue_id)
);

-- CREATE VENUE TABLE
CREATE TABLE IF NOT EXISTS venues (
    venue_id INTEGER PRIMARY KEY AUTOINCREMENT,
    venue_name TEXT NOT NULL,
    address TEXT,
    supervisor_name TEXT,
    email TEXT,
    phone TEXT,
    last_update TEXT DEFAULT (strftime('%Y-%m-%d %H:%M:%S', 'now', 'localtime'))
);

-- CREATE DOCUMENTS TABLE
CREATE TABLE IF NOT EXISTS documents (
    document_id INTEGER PRIMARY KEY AUTOINCREMENT,
    intern_id INTEGER NOT NULL,
    document_name TEXT NOT NULL,
    is_completed INTEGER NOT NULL CHECK (is_completed IN (0, 1)),
    last_update TEXT DEFAULT (strftime('%Y-%m-%d %H:%M:%S', 'now', 'localtime')),
    FOREIGN KEY (intern_id) REFERENCES interns(intern_id)
);

-- CREATE COMMENTS TABLE
CREATE TABLE IF NOT EXISTS comments (
    comment_id INTEGER PRIMARY KEY AUTOINCREMENT,
    intern_id INTEGER NOT NULL,
    comment TEXT NOT NULL,
    last_update TEXT DEFAULT (strftime('%Y-%m-%d %H:%M:%S', 'now', 'localtime')),
    FOREIGN KEY (intern_id) REFERENCES interns(intern_id)
);