import psycopg2


class SqlProcessing:
    def __init__(self, database, user, password):
        self.database = database
        self.user = user
        self.password = password
        self.conn = psycopg2.connect(database=self.database, user=self.user, password=self.password)

    def create_table(self):
        with self.conn.cursor() as curs:
            curs.execute(
                """
                CREATE TABLE IF NOT EXISTS customer (
                customer_id serial PRIMARY KEY,
                first_name varchar(30) NOT NULL,
                last_name varchar(30) NOT NULL,
                email varchar(30) NOT NULL UNIQUE
                );
                CREATE TABLE IF NOT EXISTS phone_number(
                phone_number_id serial PRIMARY KEY,
                customer_id int REFERENCES customer(customer_id) ON DELETE CASCADE,
                phone varchar(11) NOT NULL UNIQUE
                );
                """)
            self.conn.commit()

    def find_email(self, email):
        with self.conn.cursor() as curs:
            curs.execute(
                """
                SELECT email FROM customer
                WHERE email = %s
                """, (email,))
            if curs.fetchone():
                return True
            else:
                return False

    def add_new_customer (self, first_name, last_name, email, phone=None):
        with self.conn.cursor() as curs:
            if self.find_email(email):
                return f"Клиент c {email} уже зарегистрирован."
            curs.execute(
                """
                INSERT INTO customer (first_name, last_name, email) 
                VALUES (%s, %s, %s) RETURNING customer_id;
                """,
                (first_name, last_name, email)
            )
            if phone is not None:
                client_id = curs.fetchone()[0]
                ask = self.add_phone_number(client_id, phone)
                if ask == f"Номер {phone} уже есть в Базе Данных.":
                    self.conn.rollback()
                    return f"Клиент не добавлен, номер {phone} уже есть в Базе Данных."
            self.conn.commit()
        return 'Клиент добавлен в БД.'

    def add_phone_number(self, client_id, phone):
        with self.conn.cursor() as curs:
            curs.execute(
                """
                SELECT phone FROM phone_number 
                WHERE phone = %s; 
                """, (phone,)
                )
            if curs.fetchone():
                return f"Номер {phone} уже есть в Базе Данных."
            curs.execute(
                """
                SELECT customer_id from customer
                WHERE customer_id = %s; 
                """,(client_id,)
                )
            if not curs.fetchone():
                return f"Клиента с id {client_id} в Базе Данных нет."

            curs.execute("""
                INSERT INTO phone_number (customer_id, phone) VALUES (%s, %s);
                """, (client_id, phone)
                )
            self.conn.commit()
        return f"Номер телефона:{phone} добавлен клиенту id№{client_id}"

    def change_client(self, client_id, first_name=None, last_name=None, email=None):
        with self.conn.cursor() as curs:
            curs.execute(
                """
                SELECT first_name, last_name, email FROM customer  
                WHERE customer_id = %s; 
                """, (client_id,)
                )
            data = curs.fetchone()
            if not data:
                return f"Пользователь с id={client_id} в БД не найден."
            data = list(data)
            if first_name is not None:
                data[0] = first_name
            if last_name is not None:
                data[1] = last_name
            if email is not None:
                data[2] = email
            curs.execute(
                """
                UPDATE customer
                SET first_name = %s, last_name = %s, email = %s
                WHERE customer_id = %s; 
                """,
                (data[0], data[1], data[2], client_id)
                )
            self.conn.commit()
        return "Пользователь успешно изменен"

    def del_phone_number(self, client_id, phone):
        with self.conn.cursor() as curs:
            curs.execute(
                '''
                SELECT phone FROM phone_number
                WHERE phone = %s and customer_id = %s
                ''', (phone, client_id))
            if not curs.fetchone():
                return f"У клиента с id {client_id} в БД нет телефонного номера {phone}"
            curs.execute("""
                        DELETE FROM phone_number
                        WHERE phone = %s and customer_id = %s;
                        """, (phone, client_id))
            self.conn.commit()
        return f"Удален номер телефона:{phone} клиента c id №{client_id}."

    def del_customer_data(self, client_id):
        with self.conn.cursor() as curs:
            curs.execute("""
                        SELECT customer_id FROM customer
                        WHERE customer_id = %s
                        """, (client_id,))
            if not curs.fetchone():
                return f"Клиент с id {client_id} не найден в БД."
            curs.execute("""
                        DELETE FROM customer
                        WHERE customer_id = %s;
                        """, (client_id,))
            self.conn.commit()
        return f'Удалены все данные клиента с ID {client_id}.'

    def find_client(self, first_name=None, last_name=None, email=None, phone=None):
        with self.conn.cursor() as curs:
            if first_name is None:
                first_name = '%'
            if last_name is None:
                last_name = '%'
            if email is None:
                email = '%'
            if phone is None:
                phone = '%'
            searching_request = f"""
                SELECT  
                    email, first_name, last_name,
                    CASE
                        WHEN ARRAY_AGG(phone) = '{{Null}}' THEN ARRAY[]::TEXT[] 
                        ELSE ARRAY_AGG(phone)
                    END phones
                FROM customer 
                LEFT JOIN phone_number ON customer.customer_id = phone_number.customer_id 
                GROUP BY email, first_name, last_name, phone 
                HAVING first_name LIKE %s AND last_name LIKE %s AND email LIKE %s AND phone LIKE %s 
                """
            curs.execute(searching_request,(first_name, last_name, email, phone))
            return curs.fetchall()


def main():
    print(table_manage.add_new_customer('Иван', 'Петров', 'petrov@mail.com', '8991000999'))
    print(table_manage.add_new_customer('Николай', 'Иванов', 'ivanov@mail.com'))
    print(table_manage.add_new_customer('Петр', 'Николаев', 'nick@mail.com', '3350606'))
    print(table_manage.add_phone_number(1, '8911233322'))
    print(table_manage.add_phone_number(2, '8911244422'))
    print(table_manage.change_client(3, last_name='Николаевич'))
    print(table_manage.change_client(2, first_name='Ник', email='i@mail.com'))
    print(table_manage.del_phone_number(1, '8911233322'))
    print(table_manage.add_new_customer('Temporary', 'client', 'without email'))
    print(table_manage.del_customer_data(4))
    print(table_manage.find_client("Иван"))
    print(table_manage.find_client(last_name='Николаевич'))
    print(table_manage.find_client(phone='8991000999'))
    print(table_manage.find_client(email='i@mail.com'))


if __name__ == '__main__':
    print('Для подключения к БД, необходимо внести информацию.')
    table_manage = SqlProcessing(input('Enter database: '), input('Enter user: '), input('Enter password: '))
    table_manage.create_table()
    print('Данная программа управляет данными клиента.\n')
    main()
