BEGIN TRANSACTION;
CREATE TABLE IF NOT EXISTS books (
	id INTEGER NOT NULL, 
	title VARCHAR NOT NULL, 
	author VARCHAR NOT NULL, 
	isbn VARCHAR, 
	total_copies INTEGER NOT NULL, 
	available_copies INTEGER NOT NULL, 
	PRIMARY KEY (id)
);
CREATE TABLE IF NOT EXISTS borrows (
	id INTEGER NOT NULL, 
	user_id INTEGER NOT NULL, 
	book_id INTEGER NOT NULL, 
	issued_at DATETIME NOT NULL, 
	due_at DATETIME NOT NULL, 
	returned_at DATETIME, 
	renewed_count INTEGER NOT NULL, 
	fine_cents INTEGER NOT NULL, 
	PRIMARY KEY (id), 
	FOREIGN KEY(user_id) REFERENCES users (id), 
	FOREIGN KEY(book_id) REFERENCES books (id)
);
CREATE TABLE IF NOT EXISTS feedbacks (
	id INTEGER NOT NULL, 
	user_id INTEGER NOT NULL, 
	message VARCHAR NOT NULL, 
	created_at DATETIME NOT NULL, 
	PRIMARY KEY (id), 
	FOREIGN KEY(user_id) REFERENCES users (id)
);
CREATE TABLE IF NOT EXISTS payments (
	id INTEGER NOT NULL, 
	user_id INTEGER NOT NULL, 
	amount_cents INTEGER NOT NULL, 
	reason VARCHAR NOT NULL, 
	created_at DATETIME NOT NULL, 
	PRIMARY KEY (id), 
	FOREIGN KEY(user_id) REFERENCES users (id)
);
CREATE TABLE IF NOT EXISTS reservations (
	id INTEGER NOT NULL, 
	user_id INTEGER NOT NULL, 
	book_id INTEGER NOT NULL, 
	status VARCHAR NOT NULL, 
	created_at DATETIME NOT NULL, 
	PRIMARY KEY (id), 
	FOREIGN KEY(user_id) REFERENCES users (id), 
	FOREIGN KEY(book_id) REFERENCES books (id)
);
CREATE TABLE IF NOT EXISTS users (
	id INTEGER NOT NULL, 
	full_name VARCHAR NOT NULL, 
	email VARCHAR NOT NULL, 
	hashed_password VARCHAR NOT NULL, 
	role VARCHAR NOT NULL, 
	library_card_id VARCHAR, 
	is_active BOOLEAN NOT NULL, 
	PRIMARY KEY (id), 
	UNIQUE (library_card_id)
);
INSERT INTO "books" ("id","title","author","isbn","total_copies","available_copies") VALUES (1,'Sach Tieng Viet','Viet','123',1,1);
INSERT INTO "books" ("id","title","author","isbn","total_copies","available_copies") VALUES (2,'Sach Tieng Anh','Anh','1234',1,1);
INSERT INTO "books" ("id","title","author","isbn","total_copies","available_copies") VALUES (3,'Sach Tieng Han','Han','12345',1,1);
INSERT INTO "books" ("id","title","author","isbn","total_copies","available_copies") VALUES (4,'Sach Tieng Trung','Trung','123456',2,1);
INSERT INTO "books" ("id","title","author","isbn","total_copies","available_copies") VALUES (5,'Sach Tieng Nhat','Nhat','1234567',2,2);
INSERT INTO "books" ("id","title","author","isbn","total_copies","available_copies") VALUES (6,'Sach Tieng Phap','Phap','12345678',5,5);
INSERT INTO "books" ("id","title","author","isbn","total_copies","available_copies") VALUES (7,'Sach Tieng Nga','Nga','123456789',3,2);
INSERT INTO "borrows" ("id","user_id","book_id","issued_at","due_at","returned_at","renewed_count","fine_cents") VALUES (1,4,4,'2026-01-17 06:51:40.387646','2026-01-31 06:51:40.379556',NULL,0,0);
INSERT INTO "borrows" ("id","user_id","book_id","issued_at","due_at","returned_at","renewed_count","fine_cents") VALUES (2,4,7,'2026-01-17 06:54:45.975220','2026-01-31 06:54:45.967742',NULL,0,0);
INSERT INTO "borrows" ("id","user_id","book_id","issued_at","due_at","returned_at","renewed_count","fine_cents") VALUES (3,5,7,'2026-01-17 06:56:58.698155','2026-02-07 06:56:58.696458','2026-01-17 07:06:37.155008',1,0);
INSERT INTO "feedbacks" ("id","user_id","message","created_at") VALUES (1,5,'sách hay','2026-01-17 07:07:23.841602');
INSERT INTO "reservations" ("id","user_id","book_id","status","created_at") VALUES (1,4,4,'fulfilled','2026-01-17 06:49:40.907709');
INSERT INTO "users" ("id","full_name","email","hashed_password","role","library_card_id","is_active") VALUES (1,'Demo Librarian','librarian@demo.com','$2b$12$ULkNoGSPN33tBz75NX6PGO03ovWvBzmLo517dGnaUxLDDdlKvVY8e','librarian','LC-27BB8253',1);
INSERT INTO "users" ("id","full_name","email","hashed_password","role","library_card_id","is_active") VALUES (2,'pham le ngoc ngan','ngocngan@gmail.com','$2b$12$qtpVly.U63YCD1KO1b9JLuAoqbnsvTMpI4Tyk8ac1dUndZmWpmsFu','member','LC-DBD39D6D',1);
INSERT INTO "users" ("id","full_name","email","hashed_password","role","library_card_id","is_active") VALUES (3,'ho nguyen quoc vinh','quocvinh@gmail.com','$2b$12$JoBE.EGV3C0lq2VgkoR5Du6FtTXvEUAEOf3vqfC7nr34gOEnlSbD6','member','LC-E7937869',1);
INSERT INTO "users" ("id","full_name","email","hashed_password","role","library_card_id","is_active") VALUES (4,'nguyen lam ngoc ngan','ngocngan1808@gmail.com','$2b$12$boP5dpcP7UQhD.iACGYCIuyDrmOo./z.jfPwcFChKoW7gVmR3TeAq','member','LC-9D1F99A1',1);
INSERT INTO "users" ("id","full_name","email","hashed_password","role","library_card_id","is_active") VALUES (5,'to nguyen hoang phuc','phucto@gmail.com','$2b$12$CFtrltISxUenXODyG6oD/Os4qJt88D4vRw4/VHCdN.wK4PVt3PPE.','member','LC-B1BC3D5B',1);
INSERT INTO "users" ("id","full_name","email","hashed_password","role","library_card_id","is_active") VALUES (6,'le hong tho','hongtho@gmail.com','$2b$12$9NRjwWarZLwUbyEHw6etoOAr229MGuoYz.UjNHmrp8eRAMiJNNaui','member','LC-B15BE7F8',1);
CREATE INDEX ix_books_author ON books (author);
CREATE INDEX ix_books_id ON books (id);
CREATE UNIQUE INDEX ix_books_isbn ON books (isbn);
CREATE INDEX ix_books_title ON books (title);
CREATE INDEX ix_borrows_id ON borrows (id);
CREATE INDEX ix_feedbacks_id ON feedbacks (id);
CREATE INDEX ix_payments_id ON payments (id);
CREATE INDEX ix_reservations_id ON reservations (id);
CREATE UNIQUE INDEX ix_users_email ON users (email);
CREATE INDEX ix_users_id ON users (id);
COMMIT;
