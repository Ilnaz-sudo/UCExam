import array

from kivy.lang import Builder
from kivy.uix.screenmanager import ScreenManager, Screen
from kivymd.app import MDApp
from kivymd.uix.button import MDRaisedButton
from kivy.uix.label import Label
import os
import numpy as np
from kivy.uix.boxlayout import BoxLayout
import pyrebase

val=0
results=[[]]
dat = [[]]
baza=[]
c=0

# Конфигурация Firebase
firebase_config = {
    "apiKey": "AIzaSyAnkNyaRi7Jn1HCCdTl0i4w3WHWGaVc6_M",
    "authDomain": "test6razryad.firebaseapp.com",
    "databaseURL": "https://test6razryad-default-rtdb.europe-west1.firebasedatabase.app/",
    "storageBucket": "test6razryad.appspot.com"



}

firebase = pyrebase.initialize_app(firebase_config)
db = firebase.database()

Builder.load_file("quiz.kv")
class QuizScreen(Screen):

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.load_questions()  # Загрузка вопросов при создании экрана

    def load_questions(self):
        questions = db.child("questions").get()
        if questions.each():
            self.questions = [q.val() for q in questions.each()]
        else:
            self.questions = []
        self.current_question = 0
        self.show_question()

    def show_question(self):
        global c
        if not self.questions:
            return
        c = len(self.questions)
        question = self.questions[self.current_question]
        self.ids.question_label.text = question["text"]
        self.ids.value.text = (f"{str(int(self.current_question)+1)}/{len(self.questions)}")
        self.ids.options.clear_widgets()
        for i, option in enumerate(question["options"]):
            btn = MDRaisedButton(
                text=option,
                md_bg_color="white",
                text_color = "black",
                on_release=lambda _, idx=i: self.check_answer(idx)
            )
            self.ids.options.add_widget(btn)

    def check_answer(self, selected_idx):
        global results, val, dat
        i = int(self.current_question)
        correct = self.questions[self.current_question]["correct_index"]
        dat=np.append(dat, self.questions[self.current_question])
        val = np.where(np.array(results) == self.questions[self.current_question])
        data = np.array(dat)
        opt = np.array(data[i]["options"])
        protvet = opt[[selected_idx]]

        if selected_idx == correct:
            self.ids.otvet.clear_widgets()
            self.ids.otvet.text = (f"Вы ответили: {protvet[0]}  ")
            try:
                results = np.delete(results,val)
            except:
                pass
            self.next_question()
        else:
            self.ids.otvet.clear_widgets()
            self.ids.otvet.text = (f"Вы ответили: {protvet[0]}  ")
            results = np.delete(results, val)
            results = np.append(results, self.questions[self.current_question])
            if (int(self.current_question)+1)!=len(self.questions):
                self.ids.options.clear_widgets()
            self.next_question()

    def next_question(self):
        if self.current_question < len(self.questions) - 1:
            self.current_question += 1
            self.show_question()

    def last_question(self):
        if self.current_question >0:
            self.current_question -= 1
            self.show_question()

    def end(self):
        self.clear_widgets()
        QuizApp().stop()
        QuizApp().destroy_settings()
        ResultsApp().run()

class ResultsScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.load_error()

    def load_error(self):
        global baza, results
        baza = np.delete(baza, np.s_[0:])
        data_array = np.array(results)
        baza = np.append(baza, f'Правильно {c-len(results)} из {c} вопросов')
        for i in range(len(results)):
            baza = np.append(baza, "")
            baza = np.append(baza, data_array[i]["text"])
            baza = np.append(baza, "")
            baza = np.append(baza, data_array[i]["options"])
            baza = np.append(baza, "")
            inf1 = data_array[i]["options"]
            inf =  data_array[i]['correct_index']
            baza = np.append(baza, "Правильный ответ: ")
            baza = np.append(baza, inf1[int(inf)])
            baza = np.append(baza, 15*"-")

        variant_str = '\n'.join(baza)
        if len(results)>0:
            self.ids.itog.text = str(f'{variant_str}')
        else:
            self.ids.itog.text = str(f'Все правильно!')

    def replace(self):
        self.clear_widgets()
        ResultsApp().stop()
        ResultsApp().destroy_settings()
        QuizApp().run()

    def close_app(self):
        ResultsApp().stop()
        ResultsApp().destroy_settings()

class QuizApp(MDApp):
    def build(self):
        sm = ScreenManager()
        sm.add_widget(QuizScreen(name="quiz"))
        sm.current = "quiz"
        return sm

class ResultsApp(MDApp):
    def build(self):
        sm = ScreenManager()
        sm.add_widget(ResultsScreen(name="results"))
        sm.current = "results"
        return sm

if __name__ == "__main__":
    QuizApp().run()

