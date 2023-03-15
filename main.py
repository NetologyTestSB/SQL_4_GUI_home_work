# домашняя работа «Работа с PostgreSQL из Python» от 15.03.23
import tkinter.messagebox
from tkinter import *
from tkinter import ttk
from tkinter.ttk import Combobox
import psycopg2

class Base():
    ''' операции с базой данных'''
    def __init__(self):
        self.conn = None

    def set_connection(self):
        self.conn = psycopg2.connect(database='netology_db', user='postgres', password='MyBasePass')

    def close_connection(self):
        self.conn.close()

# 1.Функция, создающая структуру БД (таблицы). (часть 1)
    def create_tables(self):
        ''' создание таблиц базы данных'''
        with self.conn.cursor() as cur:
            # сначала удалим эти таблицы
            cur.execute("""
                    DROP TABLE IF EXISTS phone;
                    DROP TABLE IF EXISTS customer;    
                        """)
            # создаем пустые таблицы
            cur.execute("""
                    CREATE TABLE IF NOT EXISTS customer
                        (
                        PRIMARY KEY (customer_id),
                        customer_id SERIAL,
                        name_customer VARCHAR(50) NOT NULL,
                        surname_customer VARCHAR(50) NOT NULL,
                        email VARCHAR(100) NOT NULL                   
                        );
                    CREATE TABLE IF NOT EXISTS phone
                        (
                        PRIMARY KEY (phone_id),
                        phone_id SERIAL,
                        customer_id INTEGER NOT NULL REFERENCES customer(customer_id) ON DELETE CASCADE,
                        phone_number VARCHAR(20) NOT NULL UNIQUE
                        );                            
                        """)
        # инициируем выполнение запросов в бд
        self.conn.commit()

    def initialize_tables(self):
        ''' в таблицы записываем тестовые данные'''
        with self.conn.cursor() as cur:
            cur.execute("""
                    INSERT INTO customer (name_customer, surname_customer, email)
                    VALUES
                        ('Иван', 'Иванов', 'ivanivanov@mail.ru'),
                        ('Петр', 'Петров', 'petrpetrov@mail.ru'),                    
                        ('Сидор', 'Сидоров', 'sidorsidorov@mail.ru'),
                        ('Иван Грозный', 'Романов', 'ivantheterrible@mail.ru'),
                        ('Петр 1', 'Романов', 'peterthegreat@mail.ru'),
                        ('Николай 2 Кровавый', 'Романов', 'nickthebloody@mail.ru')
                    -- RETURNING customer_id;                                                                
                            """)
            cur.execute("""
                    INSERT INTO phone (customer_id, phone_number)
                    VALUES
                        (1, '8-095-123-45-67'),
                        (1, '8-095-333-22-22'),                        
                        (1, '8-095-444-11-11'),
                        (2, '8-095-123-89-07'),                          
                        (2, '8-095-123-55-30'),
                        (6, '8-812-000-00-00')                           
                    -- RETURNING phone_id;                                                                
                            """)

            #print(cur.fetchall())
        self.conn.commit()

# 2.Функция, позволяющая добавить нового клиента. (часть 1)
    def insert_new_customer(self, aname, asurname, amail):
        ''' запись нового клиента'''
        with self.conn.cursor() as cur:
            cur.execute("""
                    INSERT INTO customer (name_customer, surname_customer, email)
                    VALUES (%s, %s, %s);
                    """, (aname, asurname, amail))
        self.conn.commit()

# 6.Функция, позволяющая удалить существующего клиента. (часть 1)
    def delete_customer(self, aid):
        ''' удаление клиента'''
        with self.conn.cursor() as cur:
            cur.execute("""
                    DELETE 
                      FROM customer 
                     WHERE customer_id = %s;
                     """, (aid, ))
        self.conn.commit()

# 4.Функция, позволяющая изменить данные о клиенте. (часть 1)
    def update_customer(self, aid, aname, asurname, amail):
        ''' изменение данных клиента'''
        with self.conn.cursor() as cur:
            cur.execute("""
                    UPDATE customer
                       SET name_customer = %s, surname_customer = %s, email = %s
                     WHERE customer_id = %s;
                     """, (aname, asurname, amail, aid))
        self.conn.commit()

    def create_parameter(self, param) -> str:
        '''формирование параметра для запроса поиска клиента'''
        if param is None or param == '':
            return '%'
        else:
            return '%' + param + '%'

# 7.Функция, позволяющая найти клиента по его данным: имени, фамилии, email или телефону. (часть 1)
    def find_customer(self, aname=None, asurname=None, amail=None, aphone=None) -> list:
        ''' поиск клиента по его данным. поиск ведется по любому из параметров -
        имя, фамилия, почта и телефон как отдельно, так и в произвольной комбинации'''
        aname = self.create_parameter(aname)
        asurname = self.create_parameter(asurname)
        amail = self.create_parameter(amail)
        aphone = self.create_parameter(aphone)
        with self.conn.cursor() as cur:
            if aphone == '%': # если для поиска НЕ задан номер телефона
                cur.execute("""
                         SELECT DISTINCT name_customer, surname_customer, email, phone_number, customer_id
                        -- SELECT name_customer, surname_customer
                          FROM customer
                               LEFT JOIN phone USING (customer_id)
                         WHERE name_customer LIKE %s
                               AND surname_customer LIKE %s
                               AND email LIKE %s
                        """ , (aname, asurname, amail))
            else: # если для поиска задан номер телефона
                cur.execute("""
                         SELECT DISTINCT name_customer, surname_customer, email, phone_number, customer_id
                        -- SELECT name_customer, surname_customer
                          FROM customer
                               LEFT JOIN phone USING (customer_id)
                         WHERE name_customer LIKE %s
                               AND surname_customer LIKE %s
                               AND email LIKE %s
                               AND phone_number LIKE %s
                        """ , (aname, asurname, amail, aphone))
            return cur.fetchall()

    def list_of_customers(self) -> list:
        ''' список клиентов'''
        with self.conn.cursor() as cur:
            cur.execute("""
                    SELECT customer_id, name_customer, surname_customer, email
                      FROM customer
                     ORDER BY customer_id;""")
            return cur.fetchall()

    def list_of_phones(self) -> list:
        ''' список телефонов'''
        with self.conn.cursor() as cur:
            cur.execute("""
                    SELECT phone_id, CONCAT(name_customer,' ', surname_customer) AS fio, phone_number
                      FROM customer
                            JOIN phone USING (customer_id)
                    ORDER BY fio;
                        """)
            return cur.fetchall()

    def select_customer_by_id(self, aid):
        ''' поиск клиента по номеру'''
        with self.conn.cursor() as cur:
            cur.execute(""" 
                    SELECT *
                      FROM customer
                     WHERE customer_id = %s;
                     """, (aid,))
            return cur.fetchone()

    def select_phones_of_customer(self, aid):
        ''' список номеров телефонов заданного клиента (по номеру клиента)'''
        with self.conn.cursor() as cur:
            cur.execute("""
                    SELECT phone_id, phone_number
                      FROM phone
                     WHERE customer_id = %s;
                    """, (aid,))
            return cur.fetchall()

# 5.Функция, позволяющая удалить телефон для существующего клиента. (часть 1)
    def delete_phone(self, aid):
        ''' удаление телефона по его идентификационному номеру'''
        with self.conn.cursor() as cur:
            cur.execute("""
                    DELETE 
                      FROM phone 
                     WHERE phone_id = %s;
                     """, (aid, ))
        self.conn.commit()

# 3.Функция, позволяющая добавить телефон для существующего клиента. (часть 1)
    def insert_new_phone(self, aid, anumber):
        ''' добавление нового телефона для клиента (по номеру клиента)'''
        with self.conn.cursor() as cur:
            cur.execute("""
                    INSERT INTO phone (customer_id, phone_number)
                    VALUES (%s, %s);
                    """, (aid, anumber))
        self.conn.commit()


class Wind():
    ''' класс для создания GUI для управления операциями с базой данных'''
    def __init__(self):
        self.secondform = None
        self.inp_name = None
        self.inp_surname = None
        self.inp_mail = None
        self.inp_phone = None
        self.client_num = None
        self.phone_combo = None
        self.phone_id = None

    def create_tables(self):
        ''' формируем таблицы для вывода данных'''
        columns_cust = ('name', 'surname', 'email')
        self.table1 = ttk.Treeview(self.frame, columns=columns_cust, show="headings", height=10)
        self.table1.pack(anchor=N, fill=BOTH, expand=1, side='top')
        self.table1.heading('name', text='имя', anchor=W)
        self.table1.heading('surname', text='фамилия', anchor=W)
        self.table1.heading('email', text='e-mail', anchor=W)
        self.table1.column("#1", width=3)
        self.table1.column("#2", width=5)
        self.table1.column("#3", width=10)

        columns_phone = ('surname', 'phone')
        self.table2 = ttk.Treeview(self.frame, columns=columns_phone, show="headings")
        self.table2.pack(anchor=N, fill=BOTH, expand=1, side='top', pady=5)
        self.table2.heading('surname', text='владелец', anchor=W)
        self.table2.heading('phone', text='телефон', anchor=W)
        self.table2.column("#1", width=10)
        self.table2.column("#2", width=10)

    def fill_tables(self):
        ''' заполнение таблиц главной формы содержимым таблиц бд'''
        for customer in base.list_of_customers():
            self.table1.insert("", END, values=customer[1:])
        for phone in base.list_of_phones():
            self.table2.insert("", END, values=phone[1:])

    def center_position(self, width, height) -> str:
        '''создаем строку с параметрами для расположения формы по центру экрана'''
        screen_w = self.root.winfo_screenwidth()
        screen_h = self.root.winfo_screenheight()
        # отступы слева-справа и сверху-снизу одинаковы
        left = (screen_w - width) // 2
        top = (screen_h - height) // 2
        return f'{width}x{height}+{left}+{top}'

# 7.Функция, позволяющая найти клиента по его данным: имени, фамилии, email или телефону. (часть 2)
    def find_operation(self):
        '''вывод результата поиска клиента по его данным, если число найденных клиентов превышает 10,
        выводится только количество найденных клиентов
        '''
        lst = base.find_customer(self.inp_name.get(), self.inp_surname.get(),
                                 self.inp_mail.get(), self.inp_phone.get())
        dct = {}
        for el in lst:
            dct.setdefault(el[4], {'name': None, 'surname': None, 'email': None, 'phone': []})
            dct[el[4]]['phone'].append(el[3])
            dct[el[4]]['name'] = el[0]
            dct[el[4]]['surname'] = el[1]
            dct[el[4]]['email'] = el[2]
        info = f'Количество найденных клиентов: {len(dct)}'
        if len(dct) < 11:
            for v in dct.values():
                pstr = ''
                lst = v["phone"]
                for el in v["phone"]:
                    if el:
                        pstr += ' ' + el + '\n\t   '
                if not pstr:
                    pstr = 'нет телефона\n'
                info += f'\n          имя: {v["name"]}' \
                        f'\n фамилия: {v["surname"]}'\
                        f'\n       e-mail: {v["email"]}'\
                        f'\n  телефон: {pstr}'
        tkinter.messagebox.showinfo('Результаты поиска клиента', info)
        self.secondform.destroy()

    def refresh_tables(self):
        ''' обновление содержимого таблиц формы'''
        self.table1.delete(*self.table1.get_children())
        self.table2.delete(*self.table2.get_children())
        self.fill_tables()

    def on_close_second_form(self):
        ''' закрытие дополнительной формы и обновление таблиц формы'''
        self.secondform.destroy()
        self.refresh_tables()

# 2.Функция, позволяющая добавить нового клиента. (часть 2)
    def add_customer(self):
        ''' выполнение запроса на добавление нового пользователя и обновление таблиц формы'''
        base.insert_new_customer(self.inp_name.get(), self.inp_surname.get(), self.inp_mail.get())
        self.on_close_second_form()

# 6.Функция, позволяющая удалить существующего клиента. (часть 2)
    def del_customer(self):
        ''' выполнение запроса на удаление пользователя и обновление таблиц формы'''
        base.delete_customer(self.client_num)
        self.on_close_second_form()

# 4.Функция, позволяющая изменить данные о клиенте. (часть 2)
    def change_customer(self):
        ''' выполнение запроса на изменения данных пользователя и обновление таблиц формы'''
        base.update_customer(self.client_num, self.inp_name.get(), self.inp_surname.get(), self.inp_mail.get())
        self.on_close_second_form()

# 1.Функция, создающая структуру БД (таблицы). (часть 2)
    def back_to_initial_state(self):
        ''' удаляем все таблицы бд, создаем их снова и записываем в них тестовые данные'''
        base.create_tables()
        base.initialize_tables()
        self.refresh_tables()

# 5.Функция, позволяющая удалить телефон для существующего клиента. (часть 2)
    def del_phone(self):
        ''' удаление выбранного телефона у выбранного клиента'''
        self.phone_id = int(self.phone_combo.get()[0])
        base.delete_phone(self.phone_id)
        self.on_close_second_form()

# 3.Функция, позволяющая добавить телефон для существующего клиента. (часть 2)
    def add_phone(self):
        ''' добавление нового телефона выбранному клиенту'''
        if len(self.inp_phone.get()) > 0:
            base.insert_new_phone(self.client_num, self.inp_phone.get())
            self.on_close_second_form()

    def on_item_selection(self, par):
        ''' обработка события выбора клиента в комбобоксе - заполнение полей данных клиента
        par - параметр события выбора строки комбобокса'''
        self.client_num = int(self.combo.get()[0])
        # данные из base.select_customer_by_id -> (2, 'Петр', 'Петров', 'petrpetrov@mail.ru')
        cort = base.select_customer_by_id(self.client_num)
        if not self.inp_name:
            return
        self.inp_name.delete(0, END)
        self.inp_surname.delete(0, END)
        self.inp_mail.delete(0, END)
        self.inp_name.insert(0, cort[1])
        self.inp_surname.insert(0, cort[2])
        self.inp_mail.insert(0, cort[3])

    def on_select_customer(self, par):
        ''' обработка события выбора клиента в комбобоксе - формирование списка телефонов'''
        self.client_num = int(self.combo.get()[0])
        lst = base.select_phones_of_customer(self.client_num)
        lst = [str(el[0]) + ':  ' + el[1] for el in lst]
        self.phone_combo.set('') #прочистка активной строки
        self.phone_combo['values'] = [] #прочистка всего списка
        if lst:
            self.phone_combo['values'] = lst
            self.phone_combo.current(0)

    def create_second_form(self, width, height, title):
        ''' создание дополнительной формы'''
        self.secondform = Toplevel(self.root)
        self.secondform.geometry(self.center_position(width, height))
        self.secondform.title(title)

    def set_client_entries(self, parent):
        ''' размещение на дополнительной форме элементов ввода данных клиента'''
        width_e = 25
        lbl_name = Label(parent, text='имя')
        lbl_surname = Label(parent, text='фамилия')
        lbl_mail = Label(parent, text='e-mail')
        lbl_name.grid(row=0, column=1, padx=10, pady=10, sticky=E)
        lbl_surname.grid(row=1, column=1, padx=10, pady=10, sticky=E)
        lbl_mail.grid(row=2, column=1, padx=10, pady=10, sticky=E)
        self.inp_name = Entry(parent, width=width_e)
        self.inp_name.grid(row=0, column=2, padx=10, pady=10)
        self.inp_surname = Entry(parent, width=width_e)
        self.inp_surname.grid(row=1, column=2, padx=10, pady=10)
        self.inp_mail = Entry(parent, width=width_e)
        self.inp_mail.grid(row=2, column=2, padx=10, pady=10)

# 7.Функция, позволяющая найти клиента по его данным: имени, фамилии, email или телефону. (часть 3)
    def open_find_customer_form(self):
        ''' форма для поиска клиента по его данным'''
        self.create_second_form(250, 250, 'Поиск клиента')
        self.set_client_entries(self.secondform)
        lbl_phone = Label(self.secondform, text='телефон')
        lbl_phone.grid(row=3, column=1, padx=10, pady=10, sticky=E)
        self.inp_phone = Entry(self.secondform, width=20)
        self.inp_phone.grid(row=3, column=2, padx=10, pady=10)
        frm = Frame(self.secondform)
        frm.grid(row=4, column=2, pady=20)
        btn1 = Button(frm, text='Искать', width=12, command=self.find_operation)
        btn1.grid(column=2, row=0)

    def set_combobox_for_select_customer(self, parent, on_select=None):
        ''' размещение на форме комбобокса для выбора клиента'''
        self.combo = Combobox(parent, width=30, state='readonly')
        lst = [str(el[0]) + ':   ' + el[1] + ' ' +el[2] for el in base.list_of_customers()]
        self.combo['values'] = lst
        self.combo.grid(column=0, row=0, padx=10, pady=10)
        self.combo.current(0)
        self.combo.bind("<<ComboboxSelected>>", on_select)

# 4.Функция, позволяющая изменить данные о клиенте. (часть 3)
# 6.Функция, позволяющая удалить существующего клиента. (часть 3)
    def open_del_edit_customer_form(self):
        '''форма для выбора существующего клиента для выполнения операций:
           изменение данных клиента,
           удаление клиента'''
        self.create_second_form(500, 200, 'Редактирование или удаление клиента')
        self.set_combobox_for_select_customer(self.secondform, self.on_item_selection)
        self.set_client_entries(self.secondform)
        frm = Frame(self.secondform)
        frm.grid(row=7, column=2, pady=30)
        btn1 = Button(frm, text='Записать', width=12, command=self.change_customer)
        btn1.grid(column=0, row=0)
        btn2 = Button(frm, text='Удалить', width=12, command=self.del_customer)
        btn2.grid(column=1, row=0)

# 2.Функция, позволяющая добавить нового клиента. (часть 3)
    def open_new_customer_form(self):
        '''форма для добавления нового клиента'''
        self.create_second_form(250, 200, 'Новый клиент')
        self.set_client_entries(self.secondform)
        frm = Frame(self.secondform)
        frm.grid(row=7, column=2, pady=30)
        btn1 = Button(frm, text='Записать', width=12, command=self.add_customer)
        btn1.grid(column=0, row=0)

# 3.Функция, позволяющая добавить телефон для существующего клиента. (часть 3)
# 5.Функция, позволяющая удалить телефон для существующего клиента. (часть 3)
    def open_add_delete_phone_form(self):
        ''' форма для выполнения операций с телефоном:
        - добавить номер телефона существующему клиенту,
        - удалить номер телефона у существующего клиента
        '''
        self.create_second_form(550, 250, 'Операции с телефоном')
        frm1 = Frame(self.secondform)
        frm1.pack(side=TOP)
        self.set_combobox_for_select_customer(frm1, self.on_select_customer)
        lbl_phone = Label(frm1, text='Новый телефон')
        lbl_phone.grid(row=0, column=1, padx=10, pady=10, sticky=E)
        self.inp_phone = Entry(frm1, width=23)
        self.inp_phone.grid(row=0, column=2, padx=10, pady=10)
        lbl_phone_combo = Label(frm1, text='Имеющиеся телефоны')
        lbl_phone_combo.grid(row=1, column=1, padx=10, pady=10, sticky=E)
        self.phone_combo = Combobox(frm1, width=20, state='readonly')
        self.phone_combo.grid(column=2, row=1, padx=10, pady=10)
        frm2 = Frame(self.secondform)
        frm2.pack(side=BOTTOM, pady=20)
        btn1 = Button(frm2, text='Записать', width=12, command=self.add_phone)
        btn1.pack(side=LEFT, padx=10)
        btn2 = Button(frm2, text='Удалить', width=12, command=self.del_phone)
        btn2.pack(side=LEFT)

    def create_main_menu(self):
        '''главное меню программы'''
        mainmenu = Menu(self.root)
        self.root.config(menu=mainmenu)
        opermenu = Menu(mainmenu, tearoff=0)
        opermenu.add_command(label='инициализация таблиц базы данных (возврат к исходным значениям)',
                             command=self.back_to_initial_state)
        opermenu.add_command(label='добавление нового клиента',
                             command=self.open_new_customer_form)
        opermenu.add_command(label='добавление телефона существующего клиента',
                             command=self.open_add_delete_phone_form)
        opermenu.add_command(label='изменение данных существующего клиента',
                             command=self.open_del_edit_customer_form)
        opermenu.add_command(label='удаление телефона существующего клиента',
                             command=self.open_add_delete_phone_form)
        opermenu.add_command(label='удаление клиента',
                             command=self.open_del_edit_customer_form)
        opermenu.add_command(label='поиск клиента по его данным (имени, фио, email или телефону)',
                             command=self.open_find_customer_form)
        mainmenu.add_cascade(label='Операции', menu=opermenu)
        mainmenu.add_command(label='Выход', command=self.root.quit)

    def set_main_form(self):
        self.root = Tk()  # главная форма программы
        self.root.title('Таблицы клиентов и их телефонов')
        self.root.geometry(self.center_position(600, 500))
        self.create_main_menu()
        self.frame = Frame(self.root, padx=5, pady=5)
        self.frame.pack(expand=True, fill=BOTH, side='top')
        self.create_tables()


if __name__ == '__main__':
    base = Base()
    base.set_connection()
    base.create_tables()
    base.initialize_tables()

    app = Wind()
    app.set_main_form()
    app.fill_tables()
    app.root.mainloop()

    base.close_connection()