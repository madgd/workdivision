-- if db not exist run cmd:
-- sqlite3 workdivision.db < sql/creation.sql
CREATE table staff(
   id INTEGER PRIMARY KEY AUTOINCREMENT,
   name CHAR(255) UNIQUE,
   backup CHAR(255),
   state CHAR(100),
   team CHAR(1000),
   customize CHAR
);
CREATE INDEX index_staff_name on staff (name);

CREATE table client(
   id INTEGER PRIMARY KEY AUTOINCREMENT,
   name CHAR(255) UNIQUE,
   staff_id INT,
   staff_name CHAR(255),
   group_id INT,
   group_name CHAR(255),
   type CHAR(100),
   customize CHAR,
   -- customized keys
   industry CHAR(1000),
   level CHAR(16),
   trade_time INT,
   full_name CHAR(255)
);
CREATE INDEX index_client_name on client (name);
CREATE INDEX index_client_staff_name on client (staff_name);
CREATE INDEX index_client_group_name on client (group_name);

CREATE table client_group(
   id INTEGER PRIMARY KEY AUTOINCREMENT,
   name CHAR(255) UNIQUE,
   staff_id INT,
   staff_name CHAR(255),
   type CHAR(100),
   customize CHAR
);
CREATE INDEX index_group_name on client_group (name);
CREATE INDEX index_group_staff_name on client_group (staff_name);

CREATE table contacts(
   id INTEGER PRIMARY KEY AUTOINCREMENT,
   name CHAR(255),
   type CHAR(100),
   related_id INT,
   position CHAR(255),
   prime INT,
   phone CHAR(20),
   tele CHAR(20),
   email CHAR(255),
   wechat CHAR(255),
   customize CHAR
);
CREATE INDEX index_contacts_name on contacts (name);
CREATE INDEX index_contacts_related_id on contacts (related_id);
CREATE INDEX index_contacts_prime on contacts (prime);
