import mysql.connector
import helper

_CONFIG = helper.read_config()

USER = _CONFIG['SQLServerSettings']['user']  # peer_id чата, в который будут приходить сообщения с ошибками
PASSWORD = _CONFIG['SQLServerSettings']['password']
HOST = _CONFIG['SQLServerSettings']['host']

server_config = {
    'user': USER,
    'password': PASSWORD,
    'host': HOST,
    'database': 'chats',
    'raise_on_warnings': False,
    'buffered': True
}
cnx = mysql.connector.connect(**server_config)
cursor = cnx.cursor()


class ChatsInfo:
    def create_table(self, peer_id):
        cursor.execute(f'''CREATE TABLE IF NOT EXISTS chat_{peer_id} (
                               id INT UNSIGNED NOT NULL AUTO_INCREMENT,
                               vk_id VARCHAR(30) NOT NULL,
                               toxic_comments INT NOT NULL DEFAULT 0,
                               all_comments INT NOT NULL DEFAULT 0,
                               PRIMARY KEY (id)
                               )
                        ''')
        cnx.commit()

    def rows(self, peer_id):
        cursor.execute(f'SELECT COUNT(*) FROM chat_{peer_id}')
        cnx.commit()
        return int(cursor.fetchone()[0])

    def is_reg(self, peer_id, user_id):
        cursor.execute(f'''SELECT * FROM chat_{peer_id}
                           WHERE vk_id={user_id}
                        ''')
        cnx.commit()
        if cursor.fetchone():
            return True
        else:
            return False

    def insert_user(self, peer_id, user_id):
        sql = f'''INSERT INTO chat_{peer_id} (vk_id)
                  VALUES (%s)
               '''
        cursor.execute(sql, user_id)
        cnx.commit()

    def get_toxic_comments(self, peer_id, user_id):
        cursor.execute(f'''SELECT toxic_comments FROM chat_{peer_id}
                           WHERE vk_id={user_id}
                        ''')
        cnx.commit()
        return cursor.fetchone()[0]

    def get_all_comments(self, peer_id, user_id):
        cursor.execute(f'''SELECT all_comments FROM chat_{peer_id}
                           WHERE vk_id={user_id}
                        ''')
        cnx.commit()
        return cursor.fetchone()[0]

    def update(self, peer_id, user_id, toxic):
        if toxic:
            cursor.execute(f'''UPDATE chat_{peer_id}
                               SET toxic_comments=toxic_comments+1
                               WHERE vk_id={user_id}
                            ''')
        cursor.execute(f'''UPDATE chat_{peer_id}
                           SET all_comments=all_comments+1
                           WHERE vk_id={user_id}
                        ''')
        cnx.commit()

    def get_top_n(self, peer_id, n):
        cursor.execute(f'''SELECT vk_id, toxic_comments, all_comments, (toxic_comments*toxic_comments+0.0)/all_comments AS rating
                           FROM chat_{peer_id}
                           ORDER BY rating DESC
                           LIMIT {n}
                        ''')
        cnx.commit()
        return cursor.fetchall()


class UsersInfo:
    def create_table(self):
        cursor.execute('''CREATE TABLE IF NOT EXISTS users (
                               id INT UNSIGNED NOT NULL AUTO_INCREMENT,
                               vk_id VARCHAR(30) NOT NULL,
                               name VARCHAR(255) NOT NULL,
                               surname VARCHAR(255) NOT NULL,
                               toxic_comments INT NOT NULL DEFAULT 0,
                               all_comments INT NOT NULL DEFAULT 0,
                               first_login_date VARCHAR(20) NOT NULL,
                               sex TINYINT NOT NULL DEFAULT 0,
                               bdate VARCHAR(20) DEFAULT NULL,
                               country VARCHAR(255) DEFAULT NULL,
                               city VARCHAR(255) DEFAULT NULL,
                               political TINYINT UNSIGNED DEFAULT NULL,
                               religion VARCHAR(255) DEFAULT NULL,
                               relation TINYINT UNSIGNED DEFAULT 0,
                               people_main TINYINT UNSIGNED DEFAULT 0,
                               life_main TINYINT UNSIGNED DEFAULT 0,
                               smoking TINYINT UNSIGNED DEFAULT 0,
                               alcohol TINYINT UNSIGNED DEFAULT 0,
                               PRIMARY KEY (id)
                            )
                       ''')
        cnx.commit()

    def rows(self):
        cursor.execute(f'SELECT COUNT(*) FROM users')
        cnx.commit()
        return int(cursor.fetchone()[0])

    def is_reg(self, user_id):
        cursor.execute(f'''SELECT * FROM users
                           WHERE vk_id={user_id}
                        ''')
        cnx.commit()
        if cursor.fetchone():
            return True
        else:
            return False

    def insert_user(self, user_id, user_name, user_surname, user_first_login_date, user_sex, user_bdate, user_country,
                    user_city, user_political, user_religion, user_relation, user_people_main, user_life_main,
                    user_smoking, user_alcohol):
        sql = '''INSERT INTO users (
                    vk_id, name, surname, first_login_date, sex, bdate,
                    country, city, political, religion, relation,
                    people_main, life_main, smoking, alcohol)
                 VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
              '''
        cursor.execute(sql,
                       (user_id, user_name, user_surname, user_first_login_date, user_sex, user_bdate, user_country,
                        user_city, user_political, user_religion, user_relation, user_people_main, user_life_main,
                        user_smoking, user_alcohol))
        cnx.commit()

    def get_toxic_comments(self, user_id):
        cursor.execute(f'''SELECT toxic_comments FROM users
                           WHERE vk_id={user_id}
                        ''')
        cnx.commit()
        return cursor.fetchone()[0]

    def get_all_comments(self, user_id):
        cursor.execute(f'''SELECT all_comments FROM users
                           WHERE vk_id={user_id}
                        ''')
        cnx.commit()
        return cursor.fetchone()[0]

    def update(self, user_id, toxic):
        if toxic:
            cursor.execute(f'''UPDATE users
                               SET toxic_comments=toxic_comments+1
                               WHERE vk_id={user_id}
                            ''')
        cursor.execute(f'''UPDATE users
                           SET all_comments=all_comments+1
                           WHERE vk_id={user_id}
                        ''')
        cnx.commit()

    def get_top_n(self, n):
        cursor.execute(f'''SELECT vk_id, toxic_comments, all_comments, (toxic_comments*toxic_comments+0.0)/all_comments AS rating
                           FROM users
                           ORDER BY rating DESC
                           LIMIT {n}
                        ''')
        cnx.commit()
        return cursor.fetchall()
