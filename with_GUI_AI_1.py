import openai
import sys
from PyQt5.QtWidgets import QApplication, QDialog, QMessageBox
from PyQt5 import QtCore, QtGui, QtWidgets
import pickle

from langchain.llms import OpenAI
from langchain import PromptTemplate, LLMChain

class AIAssistantDialog(QDialog):
    def __init__(self):
        super(AIAssistantDialog, self).__init__()
        self.ui = Ui_Dialog()
        self.ui.setupUi(self)
        self.ui.sendButton.clicked.connect(self.send_message)
        self.ui.activateButton.clicked.connect(self.activate_api_key)

        self.previous_conversations = self.load_conversations()
        self.api_key = ''

    def send_message(self):
        user_input = self.ui.userInput.text()
        self.ui.userInput.clear()

        self.save_conversation(user_input)

        prompt = '\n'.join(self.previous_conversations)

        try:
            response = self.communicate_with_gpt3(prompt)
            self.display_response(response)

            self.previous_conversations.append(user_input)
            self.previous_conversations.append(response)

        except Exception as e:
            self.display_error(str(e))

    def save_conversation(self, conversation):
        self.previous_conversations.append(conversation)
        self.save_conversations()

    def load_conversations(self):
        try:
            with open('conversations.pickle', 'rb') as file:
                conversations = pickle.load(file)
        except FileNotFoundError:
            conversations = []
        return conversations

    def save_conversations(self):
        with open('conversations.pickle', 'wb') as file:
            pickle.dump(self.previous_conversations, file)

    def communicate_with_gpt3(self, prompt):
        response = openai.ChatCompletion.create(
            model='gpt-3.5-turbo',
            messages=[
                {"role": "system", "content": "You are a helpful assistant."},
                {"role": "user", "content": prompt}
            ],
            max_tokens=150,
            n=1,
            stop=None,
            temperature=0.5,
        )
        return response.choices[0].message['content'].strip() 


    def display_response(self, response):
        self.ui.aiResponse.append(response)

    def activate_api_key(self):
        self.api_key = self.ui.apiKeyInput.text()
        openai.api_key = self.api_key  # Добавьте эту строку
        self.ui.apiKeyInput.setDisabled(True)
        self.ui.activateButton.setDisabled(True)
        self.ui.sendButton.setEnabled(True)

#        self.api_key = self.ui.apiKeyInput.text()
 #       self.ui.apiKeyInput.setDisabled(True)
  #      self.ui.activateButton.setDisabled(True)
   #     self.ui.sendButton.setEnabled(True)

    def display_error(self, message):
        QMessageBox.critical(self, "Error", message)

class Ui_Dialog(object):
    def setupUi(self, Dialog):
        Dialog.setObjectName("Dialog")
        Dialog.resize(400, 400)
        self.verticalLayout = QtWidgets.QVBoxLayout(Dialog)
        self.verticalLayout.setObjectName("verticalLayout")
        
        self.aiResponse = QtWidgets.QTextBrowser(Dialog)
        self.aiResponse.setObjectName("aiResponse")
        self.verticalLayout.addWidget(self.aiResponse)
        self.userInput = QtWidgets.QLineEdit(Dialog)
        self.userInput.setObjectName("userInput")
        self.verticalLayout.addWidget(self.userInput)
        self.sendButton = QtWidgets.QPushButton(Dialog)
        self.sendButton.setObjectName("sendButton")
        self.verticalLayout.addWidget(self.sendButton)

        self.apiKeyInput = QtWidgets.QLineEdit(Dialog)
        self.apiKeyInput.setObjectName("apiKeyInput")
        self.verticalLayout.addWidget(self.apiKeyInput)

        self.activateButton = QtWidgets.QPushButton(Dialog)
        self.activateButton.setObjectName("activateButton")
        self.verticalLayout.addWidget(self.activateButton)

        self.retranslateUi(Dialog)
        QtCore.QMetaObject.connectSlotsByName(Dialog)

    def retranslateUi(self, Dialog):
        _translate = QtCore.QCoreApplication.translate
        Dialog.setWindowTitle(_translate("Dialog", "AI Assistant"))
        self.sendButton.setText(_translate("Dialog", "Send"))
        self.activateButton.setText(_translate("Dialog", "Activate API Key"))


if __name__ == '__main__':
    app = QApplication(sys.argv)
    dialog = AIAssistantDialog()
    dialog.show()
    sys.exit(app.exec_())
