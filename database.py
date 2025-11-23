from customtkinter import *
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import json
import os
from datetime import datetime
import numpy as np



set_appearance_mode("dark")
set_default_color_theme("blue")

class PatientManagementApp(CTk):
    def __init__(self):
        super().__init__()
        
        self.title("Система управления пациентами")
        self.geometry("1400x800")
        self.patients = []
        self.data_file = "patients_data.json"
        
        # Загрузка данных при запуске
        self.load_data()
        
        self.create_widgets()
        
    def create_widgets(self):
        # Основной фрейм
        main_frame = CTkFrame(self)
        main_frame.pack(fill="both", expand=True, padx=10, pady=10)
        
        # Левая панель - форма ввода
        left_frame = CTkFrame(main_frame)
        left_frame.pack(side="left", fill="y", padx=5, pady=5)
        
        # Правая панель - таблица и графика
        right_frame = CTkScrollableFrame(main_frame)
        right_frame.pack(side="right", fill="both", expand=True, padx=5, pady=5)
        
        # Создание формы ввода
        self.create_input_form(left_frame)
        
        # Создание таблицы пациентов
        self.create_patients_table(right_frame)
        
        # Создание области для графиков
        self.create_charts_area(right_frame)
    
    def create_input_form(self, parent):
        # Заголовок формы
        CTkLabel(parent, text="Добавить/Редактировать пациента", 
                font=("Arial", 16, "bold")).pack(pady=10)
        
        # Поля формы
        form_frame = CTkFrame(parent)
        form_frame.pack(fill="x", padx=10, pady=10)
        
        # ФИО
        CTkLabel(form_frame, text="ФИО:").grid(row=0, column=0, sticky="w", pady=5)
        self.name_entry = CTkEntry(form_frame, width=200)
        self.name_entry.grid(row=0, column=1, pady=5, padx=5)
        
        # Возраст
        CTkLabel(form_frame, text="Возраст:").grid(row=1, column=0, sticky="w", pady=5)
        self.age_entry = CTkEntry(form_frame, width=200)
        self.age_entry.grid(row=1, column=1, pady=5, padx=5)
        
        # Пол
        CTkLabel(form_frame, text="Пол:").grid(row=2, column=0, sticky="w", pady=5)
        self.gender_combo = CTkComboBox(form_frame, values=["Мужской", "Женский"], width=200)
        self.gender_combo.grid(row=2, column=1, pady=5, padx=5)
        
        # Рост
        CTkLabel(form_frame, text="Рост (см):").grid(row=3, column=0, sticky="w", pady=5)
        self.height_entry = CTkEntry(form_frame, width=200)
        self.height_entry.grid(row=3, column=1, pady=5, padx=5)
        
        # Вес
        CTkLabel(form_frame, text="Вес (кг):").grid(row=4, column=0, sticky="w", pady=5)
        self.weight_entry = CTkEntry(form_frame, width=200)
        self.weight_entry.grid(row=4, column=1, pady=5, padx=5)
        
        # Кнопки управления
        button_frame = CTkFrame(parent)
        button_frame.pack(fill="x", padx=10, pady=10)
        
        CTkButton(button_frame, text="Добавить пациента", 
                 command=self.add_patient).pack(side="left", padx=5, pady=5)
        CTkButton(button_frame, text="Обновить пациента", 
                 command=self.update_patient).pack(side="left", padx=5, pady=5)
        CTkButton(button_frame, text="Очистить форму", 
                 command=self.clear_form).pack(side="left", padx=5, pady=5)
        
        # Текущий выбранный пациент
        self.selected_patient_index = None
    
    def create_patients_table(self, parent):
        # Заголовок таблицы
        CTkLabel(parent, text="Список пациентов", 
                font=("Arial", 16, "bold")).pack(pady=10)
        
        # Фрейм для таблицы
        table_frame = CTkFrame(parent)
        table_frame.pack(fill="both", expand=True, padx=10, pady=10)
        
        # Заголовки таблицы
        headers = ["ФИО", "Возраст", "Пол", "Рост", "Вес", "ИМТ", "Действия"]
        for i, header in enumerate(headers):
            CTkLabel(table_frame, text=header, font=("Arial", 12, "bold")).grid(
                row=0, column=i, padx=5, pady=5, sticky="ew")
        
        # Контейнер для данных пациентов
        self.patients_frame = CTkFrame(table_frame)
        self.patients_frame.grid(row=1, column=0, columnspan=7, sticky="nsew")
        
        # Обновление таблицы
        self.update_patients_table()
    
    def create_charts_area(self, parent):
        # Кнопки для отображения графиков
        charts_button_frame = CTkFrame(parent)
        charts_button_frame.pack(fill="x", padx=10, pady=5)
        
        CTkButton(charts_button_frame, text="Статистика по полу", 
                 command=self.show_gender_stats).pack(side="left", padx=5, pady=5)
        CTkButton(charts_button_frame, text="Статистика по возрасту", 
                 command=self.show_age_stats).pack(side="left", padx=5, pady=5)
        CTkButton(charts_button_frame, text="ИМТ по полу", 
                 command=self.show_bmi_by_gender).pack(side="left", padx=5, pady=5)
        CTkButton(charts_button_frame, text="ИМТ по возрасту", 
                 command=self.show_bmi_by_age).pack(side="left", padx=5, pady=5)
        
        # Область для графиков
        self.chart_frame = CTkFrame(parent)
        self.chart_frame.pack(fill="both", expand=True, padx=10, pady=10)
    
    def calculate_bmi(self, height, weight):
        """Расчет индекса массы тела"""
        height_m = height / 100 
        return round(weight / (height_m ** 2), 2)
    
    def add_patient(self):
        """Добавление нового пациента"""
        try:
            name = self.name_entry.get().strip()
            age = int(self.age_entry.get())
            gender = self.gender_combo.get()
            height = float(self.height_entry.get())
            weight = float(self.weight_entry.get())
            
            if not name:
                self.show_message("Ошибка", "Введите ФИО пациента")
                return
            
            bmi = self.calculate_bmi(height, weight)
            
            patient = {
                "name": name,
                "age": age,
                "gender": gender,
                "height": height,
                "weight": weight,
                "bmi": bmi
            }
            
            self.patients.append(patient)
            self.save_data()
            self.update_patients_table()
            self.clear_form()
            self.show_message("Успех", "Пациент добавлен")
            
        except ValueError:
            self.show_message("Ошибка", "Проверьте правильность введенных данных")
    
    def update_patient(self):
        """Обновление информации о пациенте"""
        if self.selected_patient_index is None:
            self.show_message("Ошибка", "Выберите пациента для редактирования")
            return
            
        try:
            name = self.name_entry.get().strip()
            age = int(self.age_entry.get())
            gender = self.gender_combo.get()
            height = float(self.height_entry.get())
            weight = float(self.weight_entry.get())
            
            if not name:
                self.show_message("Ошибка", "Введите ФИО пациента")
                return
            
            bmi = self.calculate_bmi(height, weight)
            
            self.patients[self.selected_patient_index] = {
                "name": name,
                "age": age,
                "gender": gender,
                "height": height,
                "weight": weight,
                "bmi": bmi
            }
            
            self.save_data()
            self.update_patients_table()
            self.clear_form()
            self.show_message("Успех", "Данные пациента обновлены")
            
        except ValueError:
            self.show_message("Ошибка", "Проверьте правильность введенных данных")
    
    def edit_patient(self, index):
        """Заполнение формы для редактирования пациента"""
        patient = self.patients[index]
        self.name_entry.delete(0, "end")
        self.name_entry.insert(0, patient["name"])
        self.age_entry.delete(0, "end")
        self.age_entry.insert(0, str(patient["age"]))
        self.gender_combo.set(patient["gender"])
        self.height_entry.delete(0, "end")
        self.height_entry.insert(0, str(patient["height"]))
        self.weight_entry.delete(0, "end")
        self.weight_entry.insert(0, str(patient["weight"]))
        self.selected_patient_index = index
    
    def delete_patient(self, index):
        """Удаление пациента"""
        del self.patients[index]
        self.save_data()
        self.update_patients_table()
        self.clear_form()
        self.show_message("Успех", "Пациент удален")
    
    def clear_form(self):
        """Очистка формы ввода"""
        self.name_entry.delete(0, "end")
        self.age_entry.delete(0, "end")
        self.gender_combo.set("")
        self.height_entry.delete(0, "end")
        self.weight_entry.delete(0, "end")
        self.selected_patient_index = None
    
    def update_patients_table(self):
        """Обновление таблицы пациентов"""
        # Очистка текущей таблицы
        for widget in self.patients_frame.winfo_children():
            widget.destroy()
        
        # Заполнение данными
        for i, patient in enumerate(self.patients):
            # ФИО
            CTkLabel(self.patients_frame, text=patient["name"]).grid(
                row=i, column=0, padx=5, pady=2, sticky="w")
            
            # Возраст
            CTkLabel(self.patients_frame, text=str(patient["age"])).grid(
                row=i, column=1, padx=5, pady=2)
            
            # Пол
            CTkLabel(self.patients_frame, text=patient["gender"]).grid(
                row=i, column=2, padx=5, pady=2)
            
            # Рост
            CTkLabel(self.patients_frame, text=str(patient["height"])).grid(
                row=i, column=3, padx=5, pady=2)
            
            # Вес
            CTkLabel(self.patients_frame, text=str(patient["weight"])).grid(
                row=i, column=4, padx=5, pady=2)
            
            # ИМТ
            bmi_text = f"{patient['bmi']} ({self.get_bmi_category(patient['bmi'])})"
            CTkLabel(self.patients_frame, text=bmi_text).grid(
                row=i, column=5, padx=5, pady=2)
            
            # Кнопки действий
            action_frame = CTkFrame(self.patients_frame)
            action_frame.grid(row=i, column=6, padx=5, pady=2)
            
            CTkButton(action_frame, text="✏️", width=30,
                     command=lambda idx=i: self.edit_patient(idx)).pack(side="left", padx=2)
            CTkButton(action_frame, text="🗑️", width=30,
                     command=lambda idx=i: self.delete_patient(idx)).pack(side="left", padx=2)
    
    def get_bmi_category(self, bmi):
        """Определение категории ИМТ"""
        if bmi < 18.5:
            return "Недостаток"
        elif 18.5 <= bmi < 25:
            return "Норма"
        elif 25 <= bmi < 30:
            return "Избыток"
        else:
            return "Ожирение"
    
    def show_gender_stats(self):
        """Статистика по полу"""
        if not self.patients:
            self.show_message("Информация", "Нет данных для построения графика")
            return
        
        genders = [p["gender"] for p in self.patients]
        male_count = genders.count("Мужской")
        female_count = genders.count("Женский")
        
        fig, ax = plt.subplots(figsize=(8, 6))
        labels = ['Мужской', 'Женский']
        sizes = [male_count, female_count]
        colors = ['lightblue', 'lightpink']
        
        ax.pie(sizes, labels=labels, colors=colors, autopct='%1.1f%%', startangle=90)
        ax.set_title('Распределение пациентов по полу')
        
        self.display_chart(fig)
    
    def show_age_stats(self):
        """Статистика по возрасту"""
        if not self.patients:
            self.show_message("Информация", "Нет данных для построения графика")
            return
        
        ages = [p["age"] for p in self.patients]
        
        fig, ax = plt.subplots(figsize=(8, 6))
        ax.hist(ages, bins=10, edgecolor='black', alpha=0.7)
        ax.set_xlabel('Возраст')
        ax.set_ylabel('Количество пациентов')
        ax.set_title('Распределение пациентов по возрасту')
        ax.grid(True, alpha=0.3)
        
        self.display_chart(fig)
    
    def show_bmi_by_gender(self):
        """ИМТ по полу"""
        if not self.patients:
            self.show_message("Информация", "Нет данных для построения графика")
            return
        
        male_bmi = [p["bmi"] for p in self.patients if p["gender"] == "Мужской"]
        female_bmi = [p["bmi"] for p in self.patients if p["gender"] == "Женский"]
        
        fig, ax = plt.subplots(figsize=(8, 6))
        
        data = [male_bmi, female_bmi]
        labels = ['Мужской', 'Женский']
        
        ax.boxplot(data, labels=labels)
        ax.set_ylabel('ИМТ')
        ax.set_title('Распределение ИМТ по полу')
        ax.grid(True, alpha=0.3)
        
        self.display_chart(fig)
    
    def show_bmi_by_age(self):
        """Зависимость ИМТ от возраста"""
        if not self.patients:
            self.show_message("Информация", "Нет данных для построения графика")
            return
        
        ages = [p["age"] for p in self.patients]
        bmis = [p["bmi"] for p in self.patients]
        genders = [p["gender"] for p in self.patients]
        
        fig, ax = plt.subplots(figsize=(8, 6))
        
        colors = ['blue' if g == 'Мужской' else 'red' for g in genders]
        
        scatter = ax.scatter(ages, bmis, c=colors, alpha=0.6)
        ax.set_xlabel('Возраст')
        ax.set_ylabel('ИМТ')
        ax.set_title('Зависимость ИМТ от возраста')
        ax.grid(True, alpha=0.3)
        
        # Добавляем легенду
        from matplotlib.lines import Line2D
        legend_elements = [
            Line2D([0], [0], marker='o', color='w', markerfacecolor='blue', markersize=8, label='Мужской'),
            Line2D([0], [0], marker='o', color='w', markerfacecolor='red', markersize=8, label='Женской')
        ]
        ax.legend(handles=legend_elements)
        
        self.display_chart(fig)
    
    def display_chart(self, fig):
        """Отображение графика в интерфейсе"""
        # Очистка предыдущего графика
        for widget in self.chart_frame.winfo_children():
            widget.destroy()
        
        # Создание canvas для matplotlib
        canvas = FigureCanvasTkAgg(fig, self.chart_frame)
        canvas.draw()
        canvas.get_tk_widget().pack(fill="both", expand=True)
    
    def show_message(self, title, message):
        """Показать сообщение"""
        # Простое сообщение через CTk (можно заменить на CTkMessagebox)
        print(f"{title}: {message}")
    
    def save_data(self):
        """Сохранение данных в файл"""
        try:
            with open(self.data_file, 'w', encoding='utf-8') as f:
                json.dump(self.patients, f, ensure_ascii=False, indent=2)
        except Exception as e:
            print(f"Ошибка сохранения: {e}")
    
    def load_data(self):
        """Загрузка данных из файла"""
        try:
            if os.path.exists(self.data_file):
                with open(self.data_file, 'r', encoding='utf-8') as f:
                    self.patients = json.load(f)
        except Exception as e:
            print(f"Ошибка загрузки: {e}")
            self.patients = []
    
    def safe_destroy(self):
        try:
            # Закрываем все дочерние окна
            for child in self.winfo_children():
                try:
                    child.destroy()
                except:
                    pass
            
            # Останавливаем все pending callbacks
            for after_id in self.tk.eval('after info').split():
                self.after_cancel(after_id)
                
        except Exception as e:
            print(f"Ошибка при завершении: {e}")
        
        finally:
            # Всегда вызываем destroy
            self.destroy()
            plt.close('all') 

app = PatientManagementApp()
app.protocol("WM_DELETE_WINDOW", app.safe_destroy) 
app.mainloop()