

from kivy.lang import Builder
from kivy.uix.screenmanager import ScreenManager, Screen
from kivymd.app import MDApp
from kivymd.uix.button import MDRaisedButton
import requests
from kivymd.uix.list import OneLineListItem


DATABASE_URL = "https://test6razryad-default-rtdb.europe-west1.firebasedatabase.app"

val = 0
dat = []
for i in range(500):
    dat.append("")
baza = []
results = {}
c = 0
Builder.load_file("quiz.kv")
Builder.load_file("results.kv")

def get_questions():
    response = requests.get(f"{DATABASE_URL}/questions.json")
    if response.status_code == 200:
        data = response.json()
        if isinstance(data, dict):  # Если пришел словарь, берем values()
            return list(data.values())
        elif isinstance(data, list):  # Если сразу список, возвращаем его
            return data
    return []  # Возвращаем пустой список, если данные некорректны

class QuizScreen(Screen):
    global results
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.dynamic_widgets = {}
    def on_pre_enter(self, *args):
        """Этот метод срабатывает перед тем, как экран становится активным"""
        self.load_questions()
        self.update_question_list()





    def load_questions(self):
        global question2
        self.questions = get_questions()
        self.answered = {}
        self.current_question = 0
        self.answered = {i: False for i in range(len(self.questions))}  # Все вопросы неотвеченные
        #self.update()  # Обновляем список номеров вопросов
        self.show_question()

    def update(self):
        i = str(self.current_question-1)
        j = self.current_question - 1
        color = (0, 0.4, 1, 0.8) if self.answered[j] else (0.5, 0.5, 0.5, 1)
        self.dynamic_widgets[f"btn_{i}"].text_color = color


    def update_question_list(self):
        """Обновляет список вопросов справа, меняя цвета номеров"""
        self.ids.question_list.clear_widgets()
        for i in range(len(self.questions)):
            color = (0, 0.4, 1, 0.8) if self.answered[i] else (0.5, 0.5, 0.5, 1)  # Зеленый или серый
            btn = OneLineListItem(
                text=f"{i+1}",
                id = f"{i+1}",
                theme_text_color="Custom",
                text_color=color,
                on_release=lambda instance, idx=i:self.go_to_question(idx)
            )
            self.ids.question_list.add_widget(btn)
            self.dynamic_widgets[f"btn_{i}"] = btn

    def split_text(self, text, max_chars=20):
        """Разбивает текст на строки, выравнивая влево"""
        words = text.split()  # Разбиваем текст на слова
        lines = []
        current_line = ""
        lines.append(68 * " ")
        for word in words:
            if len(current_line) + len(word) + 1 <= max_chars:

                current_line += (" " if current_line else '') + word  # Добавляем пробел между словами
            else:
                lines.append(current_line)  # Добавляем текущую строку в список
                current_line = word  # Начинаем новую строку с нового слова

        if current_line:
            lines.append(current_line)
            lines.append(68*" ") # Добавляем последнюю строку

        return "\n".join(lines)  # Объединяем строки с переносами

    def show_question(self):
        global c
        question = self.questions[self.current_question]
        if not self.questions:
            return
        c = len(self.questions)

        self.ids.question_label.text = question["text"]
        self.ids.value.text = f"{self.current_question + 1}/{len(self.questions)}"
        self.ids.options.clear_widgets()



    # Логика создания кнопок:
        for i, option in enumerate(question["options"]):
            formatted_text = self.split_text(option, max_chars=30)  # Разбиваем текст


            # Создаем кнопку
            btn = MDRaisedButton(
                text = formatted_text,
                md_bg_color="white",
                text_color="black",
                on_release=lambda _, idx=i: self.check_answer(idx)



            )


            # Добавляем кнопку на экран
            self.ids.options.add_widget(btn)



    def check_answer(self, selected_idx):
        global val, dat, results
        self.answered[self.current_question] = True
        i = self.current_question
        correct = self.questions[self.current_question]["correct_index"]
        if not self.questions[self.current_question] in dat:
            dat[i] = (self.questions[self.current_question])



        question_data = dat[i]

        if isinstance(question_data, dict):
            self.protvet = question_data["options"][selected_idx]

            if selected_idx == correct:
                if question_data["text"] in results:
                    del results[question_data["text"]]
                self.next_question()
            else:
                results[question_data["text"]] = question_data
                self.next_question()
            self.update()

    def next_question(self):
        if self.current_question < len(self.questions) - 1:
            self.current_question += 1
            self.show_question()

    def last_question(self):
        if self.current_question > 0:
            self.current_question -= 1
            self.show_question()

    def go_to_question(self, question_index):
        """Переход к конкретному вопросу при нажатии на номер"""
        self.current_question = question_index
        self.show_question()


class ResultsScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.current_index = 0
        self.errors = []  # Список ошибок


    def on_pre_enter(self, *args):
        """Этот метод срабатывает перед тем, как экран становится активным"""
        self.load_error()
        self.show_error()



    def load_error(self):
        global results
        self.errors = list(results.items())  # Преобразуем словарь в список пар (вопрос, данные)
        self.current_index = 0

    def show_error(self):
        """Отображает текущую ошибку"""
        if not self.errors:

            self.ids.true_text.text = ""
            self.ids.itog.text = "Все правильно! Ошибок нет."
            self.ids.prev_button.disabled = True
            self.ids.next_button.disabled = True
            return

        vopros, otvet = self.errors[self.current_index]

        options = "\n\n".join([f"{i+1}. {option}" for i, option in enumerate(otvet["options"])])
        correct_answer = otvet["options"][otvet["correct_index"]]

        error_text = f"{vopros}\n\n{options}\n"
        true_text = f"Правильный ответ:\n{correct_answer}"

        self.ids.itog.text = error_text
        self.ids.true_text.text = true_text
        self.ids.true_text.color = (0, 0.4, 1, 0.8)

        self.ids.page_label.text = f"{self.current_index + 1} / {len(self.errors)}"

        # Блокируем кнопки, если достигли начала или конца
        self.ids.prev_button.disabled = (self.current_index == 0)
        self.ids.next_button.disabled = (self.current_index == len(self.errors) - 1)

    def next_error(self):
        """Переключается на следующую ошибку"""
        if self.current_index < len(self.errors) - 1:
            self.current_index += 1
            self.show_error()

    def prev_error(self):
        """Переключается на предыдущую ошибку"""
        if self.current_index > 0:
            self.current_index -= 1
            self.show_error()

    def replace(self):
        global results
        results={}





class UceApp(MDApp):
    def build(self):
        sm = ScreenManager()
        sm.add_widget(QuizScreen(name="quiz"))
        sm.add_widget(ResultsScreen(name="results"))
        return sm



if __name__ == "__main__":
    UceApp().run()
