import psycopg2


class SqlProcessing:
    def __init__(self, database, user, password):
        self.database = database
        self.user = user
        self.password = password
        self.conn = psycopg2.connect(database=self.database, user=self.user, password=self.password)

    def create_table(self):
        with self.conn.cursor() as curs:
            curs.execute("""
                        CREATE TABLE IF NOT EXISTS customer (
                        customer_id serial PRIMARY KEY,
                        first_name varchar(30) NOT NULL,
                        last_name varchar(30) NOT NULL,
                        email varchar(30)
                        );
                        CREATE TABLE IF NOT EXISTS phone_number(
                        phone_number_id serial PRIMARY KEY,
                        customer_id int REFERENCES customer(customer_id),
                        phone varchar(11) NOT NULL
                        );
                        """)
            self.conn.commit()

    def add_new_customer(self):
        print("Команда создаст нового клиента.")
        with self.conn.cursor() as curs:
            curs.execute("""
                        INSERT INTO CUSTOMER (first_name, last_name, email)
                        VALUES (%s, %s, %s) 
                        """, (input("Имя: "), input("Фамилия: "), input("Email: ")))
            self.conn.commit()

    def add_phone_number(self):
        print("Команда добавит телефонный номер клиенту.")
        with self.conn.cursor() as curs:
            curs.execute("""
                        INSERT INTO phone_number (customer_id, phone)
                        VALUES (%s, %s);
                        """, (int(input('Введите id клиента: ')), input("Введете телефонный номер: ")))
            self.conn.commit()

    def change_customer_data(self):
        customer_id = int(input('Введите id клиента: '))
        print('Команда изменит данные клиента, выберете что требуется изменить:\n'
              '1. Имя\n'
              '2. Фамилию\n'
              '3. Email\n')

        user_comand = int(input("Выберите номер команды: "))
        if user_comand == 1:
            with self.conn.cursor() as curs:
                curs.execute("""
                            UPDATE customer
                            SET first_name = %s 
                            WHERE customer_id = %s
                            """, (input("Введите имя: "), customer_id))
                self.conn.commit()

        elif user_comand == 2:
            with self.conn.cursor() as curs:
                curs.execute("""
                              UPDATE customer
                              SET last_name = %s 
                              WHERE customer_id = %s
                              """, (input("Введите Фамилию: "), customer_id))
                self.conn.commit()

        elif user_comand == 3:
            with self.conn.cursor() as curs:
                curs.execute("""
                              UPDATE customer
                              SET email = %s 
                              WHERE customer_id = %s
                              """, (input("Введите email: "), customer_id))
                self.conn.commit()
        else:
            print("Команда не найдена!")

    def del_phone_number(self):
        print("Команда удалит телефонный номер клиента.")
        with self.conn.cursor() as curs:
            curs.execute("""
                        DELETE FROM phone_number
                        WHERE phone = %s;
                        """, (input('Введите номера телефона: '),))
            self.conn.commit()

    def del_customer_data(self):
        print('Команда удалит все данные клиента.')
        client_id = int(input("Введите id клиента: "))
        with self.conn.cursor() as cur:
            cur.execute("""
                        DELETE FROM phone_number
                        WHERE customer_id = %s;
                        DELETE FROM customer
                        WHERE customer_id = %s;
                        """, (client_id, client_id))
            self.conn.commit()

    def find_customer_data(self):
        print("Команда ищет все данные пользователя, выберите тип поиска.\n"
              "1. Поиск по имени, фамилии и email\n"
              "2. Поиск по имени, фамилии\n"
              "3. Поиск по номеру телефона\n")
        user_command = int(input("Выберете номер команды: "))

        if user_command == 1:
            with self.conn.cursor() as curs:
                curs.execute("""
                            SELECT customer_id, first_name, last_name, email, phone FROM customer 
                            LEFT JOIN phone_number USING(customer_id)
                            WHERE first_name = %s AND last_name = %s AND email = %s
                            """, (input("Введите имя: "), input("Введите фамилию: "), input("Введите email: ")))
                record = curs.fetchone()
                print(f'id: {record[0]}\n'
                      f'Имя: {record[1]}\n'
                      f'Фамилия: {record[2]}\n'
                      f'Email: {record[3]}\n'
                      f'Телефонный номер: {record[4]}')

        elif user_command == 2:
            with self.conn.cursor() as curs:
                curs.execute("""
                            SELECT customer_id, first_name, last_name, email, phone FROM customer 
                            LEFT JOIN phone_number USING(customer_id)
                            WHERE first_name = %s AND last_name = %s 
                            """, (input("Введите имя: "), input("Введите фамилию: ")))
                record = curs.fetchall()
                for line in record:
                    print(f'id: {line[0]}, Имя: {line[1]}, Фамлия: {line[2]}, Email: {line[3]}, Тел.номер: {line[4]}')

        elif user_command == 3:
            with self.conn.cursor() as curs:
                curs.execute("""
                            SELECT customer_id, first_name, last_name, email, phone FROM customer 
                            LEFT JOIN phone_number USING(customer_id)
                            WHERE phone = %s 
                            """, (input("Введите номер телефона: "),))
                record = curs.fetchall()
                for line in record:
                    print(f'id: {line[0]}, Имя: {line[1]}, Фамлия: {line[2]}, Email: {line[3]}, Тел.номер: {line[4]}')
        else:
            print('Команда не найдена!')


def select_query():
    print(f"-" * 100)
    print('Список команд:\n'
          '1: Добавить нового клиента\n'
          '2: Добавить телефонный номер клиента\n'
          '3: Изменить данные клиента\n'
          '4: Удалить телефонный номер клиента\n'
          '5: Удалить данные клиента\n'
          '6: Найти данные клиента (по имени, фамилии, email-у или по телефону)\n'
          'q: Выход из программы\n')
    return input('Выберите команду: ')


def main():
    while True:
        try:
            eval(func_data[select_query()])
        except Exception as error:
            print(f"Программа перезагружена в связи с ошибкой: '{error}'")


func_data = {
    "1": "table_manage.add_new_customer()",
    "2": "table_manage.add_phone_number()",
    "3": "table_manage.change_customer_data()",
    "4": "table_manage.del_phone_number()",
    "5": "table_manage.del_customer_data()",
    "6": "table_manage.find_customer_data()",
    "q": "exit(0)",
            }
if __name__ == '__main__':
    print('Для подключения к БД, необходимо внести информацию.')
    table_manage = SqlProcessing(input('Enter database: '), input('Enter user: '), input('Enter password: '))
    table_manage.create_table()
    print('Данная программа позволяет управлять данными клиента, соответствующими командами.\n')
    main()
