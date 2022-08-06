import mysql.connector

server_config = {
    'user': 'root',
    'password': '#coc3303OS',
    'host': 'localhost',
    'database': 'chats',
    'raise_on_warnings': False,
    'buffered': True
}
cnx = mysql.connector.connect(**server_config)
cursor = cnx.cursor()


class ChatsInfo:
    def create_table(self, peer_id):
        cursor.execute(f'''CREATE TABLE IF NOT EXISTS chat_{peer_id} (
                       id int unsigned NOT NULL AUTO_INCREMENT,
                       vk_id varchar(30) NOT NULL,
                       toxic_comments int NOT NULL DEFAULT 0,
                       all_comments int NOT NULL DEFAULT 0,
                       PRIMARY KEY (id))''')
        cnx.commit()

    def rows(self, peer_id):
        cursor.execute(f'SELECT COUNT(*) FROM chat_{peer_id}')
        cnx.commit()
        return int(cursor.fetchone()[0])

    def is_reg(self, peer_id, user_id):
        cursor.execute(f'''SELECT * FROM chat_{peer_id}
                      WHERE vk_id={user_id}''')
        cnx.commit()
        if cursor.fetchone():
            return True
        else:
            return False

    def insert_user(self, peer_id, user_id):
        cursor.execute(f'''INSERT INTO chat_{peer_id} (vk_id)
                      VALUES ({user_id})''')
        cnx.commit()

    def get_toxic_comments(self, peer_id, user_id):
        cursor.execute(f'''SELECT toxic_comments FROM chat_{peer_id}
                      WHERE vk_id={user_id}''')
        cnx.commit()
        return cursor.fetchone()[0]

    def get_all_comments(self, peer_id, user_id):
        cursor.execute(f'''SELECT all_comments FROM chat_{peer_id}
                      WHERE vk_id={user_id}''')
        cnx.commit()
        return cursor.fetchone()[0]

    def update(self, peer_id, user_id, toxic):
        if toxic:
            cursor.execute(f'''UPDATE chat_{peer_id}
                        SET toxic_comments=toxic_comments+1
                        WHERE vk_id={user_id}''')
        cursor.execute(f'''UPDATE chat_{peer_id}
                        SET all_comments=all_comments+1
                        WHERE vk_id={user_id}''')
        cnx.commit()

    def get_top_n(self, peer_id, n):
        cursor.execute(f'''SELECT vk_id, toxic_comments, all_comments, (toxic_comments*toxic_comments+0.0)/all_comments AS rating
                      FROM chat_{peer_id}
                      ORDER BY rating DESC
                      LIMIT {n}''')
        cnx.commit()
        return cursor.fetchall()


class UsersInfo:
    def create_table(self):
        cursor.execute(f'''CREATE TABLE IF NOT EXISTS users (
                       id int unsigned NOT NULL AUTO_INCREMENT,
                       vk_id varchar(30) NOT NULL,
                       toxic_comments int NOT NULL DEFAULT 0,
                       all_comments int NOT NULL DEFAULT 0,
                       PRIMARY KEY (id))''')
        cnx.commit()

    def rows(self):
        cursor.execute(f'SELECT COUNT(*) FROM users')
        cnx.commit()
        return int(cursor.fetchone()[0])

    def is_reg(self, user_id):
        cursor.execute(f'''SELECT * FROM users
                      WHERE vk_id={user_id}''')
        cnx.commit()
        if cursor.fetchone():
            return True
        else:
            return False

    def insert_user(self, user_id):
        cursor.execute(f'''INSERT INTO users (vk_id)
                      VALUES ({user_id})''')
        cnx.commit()

    def get_toxic_comments(self, user_id):
        cursor.execute(f'''SELECT toxic_comments FROM users
                        WHERE vk_id={user_id}''')
        cnx.commit()
        return cursor.fetchone()[0]

    def get_all_comments(self, user_id):
        cursor.execute(f'''SELECT all_comments FROM users
                        WHERE vk_id={user_id}''')
        cnx.commit()
        return cursor.fetchone()[0]

    def update(self, user_id, toxic):
        if toxic:
            cursor.execute(f'''UPDATE users
                          SET toxic_comments=toxic_comments+1
                          WHERE vk_id={user_id}''')
        cursor.execute(f'''UPDATE users
                        SET all_comments=all_comments+1
                        WHERE vk_id={user_id}''')
        cnx.commit()

    def get_top_n(self, n):
        cursor.execute(f'''SELECT vk_id, toxic_comments, all_comments, (toxic_comments*toxic_comments+0.0)/all_comments AS rating
                      FROM users
                      ORDER BY rating DESC
                      LIMIT {n}''')
        cnx.commit()
        return cursor.fetchall()
