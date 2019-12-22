from threading import Semaphore
import AbstractApplication as Base
import time
import random

"""
Class that implements the main functionality of the integration robot Howdy.
    """


class SampleApplication(Base.AbstractApplication):
    def _init_(self):
        # Initiate variables that will be used globally.
        self.answerAfterPracticeLock = Semaphore(0)
        self.gestureLock = Semaphore(0)
        self.levelLock = Semaphore(0)
        self.langLock = Semaphore(0)
        self.practiceTestLock = Semaphore(0)
        self.nameLock = Semaphore(0)
        self.speechLock = Semaphore(0)
        self.learnTime = Semaphore(0)
        self.answerLock = Semaphore(0)
        self.answer = ""
        self.answerAfterPractice = ""
        self.name = ""
        self.practiceTest = ""
        self.level = ""
        self.nameList = []
        self.practiceList = []
        self.levelList = []
        self.complimentList = []
        self.wrongAnswerList = []

        # Load lists with possible text-responses and load dictionaries with practice words
        self.loadLists()
        self.loadDicts()

        # Initialise Abstract Application
        Base.AbstractApplication._init_(self)

    def main(self):
        # Record the audio that the user inputs for later analysis and debugging.
        self.setRecordAudio(True)

        # Set the language to American English
        self.setLanguage('en-US')
        self.langLock.release()

        # Connect to Dialogflow.
        self.setDialogflowKey("howdy-plvfvo-ca953d08832f.json")
        self.setDialogflowAgent("howdy-plvfvo")

        # Nao says hey, and asks for name.
        self.speechLock = Semaphore(0)
        self.say("Howdy partner! What is your name")
        self.speechLock.acquire()

        # Start introduction sequence.
        self.introduction()

    def introduction(self):
        # Listen for name of the user.
        self.setAudioContext("answer_name")
        self.setEyeColour("blue")
        self.startListening()
        self.nameLock.acquire(timeout=4)
        self.stopListening()
        self.setEyeColour("white")
        if self.name == "":
            self.nameLock.acquire(timeout=1)

        # If no name was recorded keep asking for name until it is acquired:
        while self.name == "":
            self.say("Sorry I didn't catch your name, could you repeat it?")
            self.speechLock.acquire()
            self.setAudioContext("answer_name")
            self.setEyeColour("blue")
            self.startListening()
            self.nameLock.acquire(timeout=4)
            self.stopListening()
            self.nameLock.acquire(timeout=1)
            self.setEyeColour("white")

        # If a name was recorded, pick one of the answers and start next function
        self.pickFromList(self.nameList, self.name)
        self.practiceOrTest()

    def practiceOrTest(self):
        # Listen for whether to test or to practice
        self.setAudioContext("answer_practice_test")
        self.setAudioHints("Practice", "test")
        self.setEyeColour("blue")
        self.startListening()
        self.practiceTestLock.acquire(timeout=4)
        self.stopListening()
        self.setEyeColour("white")
        if self.practiceTest == "":
            print("No practice found")
            self.practiceTestLock.acquire(timeout=1)

        # If no name was recorded keep asking for name until it is acquired:
        while self.practiceTest == "":
            self.say("Sorry I didn't catch that")
            self.speechLock.acquire()
            self.setAudioContext("answer_practice_test")
            self.setEyeColour("blue")
            self.startListening()
            self.practiceTestLock.acquire(timeout=4)
            self.stopListening()
            self.setEyeColour("white")

        # If the user chose to practice, give appropriate response
        if self.practiceTest == "Practice":
            self.pickFromList(self.practiceList, "")
            self.whichLevel()

        # If user chose to test, give appropriate response
        elif self.practiceTest == "Test":
            self.pickFromList(self.testList, "")
            self.whichLevel()

    def whichLevel(self):
        # Set the right audio context in Dialogflow, depending on whether user chose to test or practice
        self.listenToLevel()

        # If answer was recorded give response and start practice or test sequence
        if self.level:
            self.pickFromList(self.levelList, "")
        if self.practiceTest == "Practice":
            self.practice()
        elif self.practiceTest == "Test":
            self.test()

    def listenToLevel(self):
        # Listen for what level the user wants to test or practice
        self.setAudioContext("answer_level")
        self.setEyeColour("blue")
        self.startListening()
        self.levelLock.acquire(timeout=3)
        self.stopListening()
        self.setEyeColour("white")

        # Keep prompting user for answer while no answer has been recognised
        while self.level == "":
            self.say("Sorry I didn't catch that")
            self.setAudioContext("answer_level")
            self.speechLock.acquire()
            self.setEyeColour("blue")
            self.startListening()
            self.levelLock.acquire(timeout=4)
            self.stopListening()
            self.setEyeColour("white")

    def practice(self):
        # Load the word dictionary that corresponds to the level that was chosen
        wordDict = self.wordDicts[self.level]

        # Tell the user how the practice session will work
        self.sayAnimated("Lets practice!, I will first say a word in english and then repeat it in Syrian, "
                         "then I'll give you a couple seconds to repeat the word")
        self.speechLock.acquire()

        # For every word pair in the dictionary run the practiceWord function
        numberWord = 0
        for key, value in wordDict.items():
            self.practiceWord(key, value, numberWord)
            numberWord += 1
            print(numberWord)

        # When the session is over, give a compliment and ask if the user want to test their new skills
        self.sayAnimated("Nice practice session {}, you're the best in the wild west!".format(self.name))
        self.sayAnimated("What do you want to do? Do you want to Quit, Practice again or Test your new skills?")
        self.aftermath()

    def practiceWord(self, key, value, numberWord):
        # Reset the language to English and say the key word
        for i in range(2):
            self.say(key)
            self.speechLock.acquire(timeout=1)
            self.sayAnimated("means")
            self.speechLock.acquire(timeout=2)
            self.say(value)
            self.speechLock.acquire(timeout=2)

        # On the first three couple words tell the user to repeat the word, then just wait for the user to repeat
        if numberWord < 3:
            self.sayAnimated("repeat please")
        self.learnTime.acquire(timeout=5)

    def test(self):
        """
        Here the robots starts to test the user by looping through all the words to test. But first, Howdy retrieves the
        levels that the user has practised and gives to oppurtunity to choose the level to test.
            """

        levels = self.retrievePracticeLevel()
        if len(levels) == 0:
            self.sayAnimated(self.name + ", you need to practice levels first!")
            self.practice()
        else:
            self.sayAnimated("Would you like to test level")
            firstLoop = True
            for level in levels:
                if not firstLoop:
                    self.sayAnimated(" or ")
                self.sayAnimated(str(level))
                firstLoop = False
            self.listenToLevel()

        wordDict = self.wordDicts[self.level]
        self.sayAnimated("Alright let's test your skills")
        counter = 0
        wrongWords = []
        # Go through every word in the given level word dict and test these words with the user.
        for key, value in wordDict.items():
            self.testWord(key, value, counter, wrongWords)
            counter += 1

        # Here the word that the user got wrong are tested. It removes te word from the list of tuples if the user
        # has it right. It will continue to ask the wrong words (by using the while loop) until there are no more
        # words in the list.
        while len(wrongWords) > 0:
            # we are using a copy to loop through, otherwise it loops through the list while items are being
            # removed. This makes the code skip some elements of the list.
            for key, value in wrongWords[:]:
                self.testWord(key, value, counter, wrongWords)

        self.sayAnimated("What do you want to do? Do you want to Quit, Practice again or Test your new skills?")
        self.aftermath()

    def testWord(self, key, value, counter, wrongWords):
        """Tests a single word by giving the word the user is supposed to translate, and to listen to the input of
        user, checking if the given word corresponds to the answer """
        self.setLanguage("en-US")
        self.langLock.acquire()
        if counter < 3:
            # After pronouncing three words, exclude the "What does... mean from the speech of the robot. "
            self.sayAnimated("What does" + key + "mean?")
        else:
            self.sayAnimated(key)

        # Listen for answer
        # self.setLanguage("nl-NL")
        # self.langLock.acquire()
        self.setAudioContext("answer_answerLevelOne")
        self.setEyeColour("blue")
        self.startListening()
        self.answerLock.acquire(timeout=4)
        self.stopListening()
        self.setEyeColour("white")

        if self.answer:
            if value == self.answer:
                # If the given value by the user is right, say it is right and remove it to the wrongWords list.
                self.sayAnimated(self.pickFromList(self.complimentList, ""))
                if value in [v for k, v in wrongWords]:
                    wrongWords.remove((key, value))
            else:
                # If the given value by the user is wrong, say it is wrong and append it to the wrongWords list.
                self.sayAnimated(self.pickFromList((self.wrongAnswerList, "")))
                wrongWords.append((key, value))

    def aftermath(self):
        self.setAudioContext("answer_after_practice")
        self.setAudioHints("Practice", "Test", "Quit")
        self.setEyeColour("blue")
        self.startListening()
        self.answerAfterPracticeLock.acquire(timeout=3)
        self.stopListening()
        self.setEyeColour("white")
        if self.answerAfterPractice == "":
            self.answerAfterPracticeLock.acquire(timeout=1)


        while self.answerAfterPractice == "":
            self.say("Sorry I didn't catch that, what do you want to do now?")
            self.speechLock.acquire()
            self.setAudioContext("answer_after_practice")
            self.setEyeColour("blue")
            self.startListening()
            self.answerAfterPractice.acquire(timeout=4)
            self.stopListening()
            self.setEyeColour("white")

        if self.answerAfterPractice == "Practice" or self.answerAfterPractice == "practice":
            self.practice()

        elif self.answerAfterPractice == "Test" or self.answerAfterPractice == "test":
            self.test()

        elif self.answerAfterPractice == "Quit" or self.answerAfterPractice == "quit":
            self.sayAnimated("Good bye!")
            quit()


    def loadDicts(self):
        """
        Loads dictionaries of translated word pairs into another dictionary that can be used globally
            """

        self.wordDicts = {
            1: {"goodbye": "wadaeaan", "colleague": "zamil", "company": "sharika"}
            ,
            2: {"business": "aemal", "wholesale": "bialjumla", "sales": "mabieat", "achieve": "altawasul",
                "venture": "almaghamir", "brand": "ealamat tijaria", "delegation": "wafda", "meet": "yajtamie",
                "talk": "hadith", "busy": "mashghul", "delivery": "tawsil", "order": "talab", "know": "aerf",
                "join": "aindama"}
            ,
            3: {"entrepreneur": "ryady", "dedication": "tafan", "citizenship": "almuatina", "citizen": "muatin",
                "expect": "tuaqie", "learn": "taealam", "wish": "raghba", "effort": "majhud", "offer": "eard",
                "discuss": "munaqasha", "allow": "alsamah", "areas": "almanatiq", "resume": "sirat dhatia",
                "employment": "tawzif"}
            ,
            4: {"catering industry": "sinaeat altaeam", "working hours": "saeat aleamal",
                "civil servant": "iinaa aistifan", "police officer": "dabit shurta", "fireman": "rajul al'iitfa",
                "retail": "altajzia", "hospital": "mustashfaa", "full - time": "waqt kamil", "part - time":
                    "dawam jazyaa", "tax": "hamal"}
            ,
            5: {"drivers license": "rukhsat alssayiq", "apply for": "altaqadum bitalab lilhusul",
                "responsibilities": "almaswuwliat", "vacancy": "shaghir", "vocational level": "almustawaa almahniu",
                "cover letter": "ghita' alrisala", "life insurance": "altaamin ealaa alhaya",
                "tax advisor": "mustashar aldarayib", "investing": "alaistithmar"}
        }

    def pickFromList(self, list, var):
        randint = random.randint(0, len(list) - 1)
        self.speechLock = Semaphore(0)
        print(list[randint])
        self.sayAnimated(list[randint].format(var))
        self.speechLock.acquire()

    def Gesture(self, id):
        self.doGesture(id)
        self.gestureLock.release()

    def listen(self):
        self.setEyeColour("blue")
        self.startListening()
        self.practice_testLock.acquire(timeout=4)
        self.stopListening()
        self.setEyeColour("white")

    def loadLists(self):
        self.nameList = ["{} My friend, do you want to practice with me or should I take a test",
                         "Nice to meet you {} my name is Howdy! Would you like to practice or take a test?",
                         "My name is Howdy, saddle up {} Would you like to practice or take a test?",
                         "yee haw, nice to meet you {} , I'm Howdy! Would you like to practice or take a test?",
                         "Hey {}, Good to see you. Do you want to practice or take a test?"]

        self.practiceList = ["Okay! Which level do you want to practice? There are 5 levels.",
                             "Alright! Lets do that, There are 5 Levels, which level do you want to practice?",
                             "There are 5 Levels, which level should we practice?",
                             "Choose a level, you can choose from 1 to 5.",
                             "You can choose which level you want to practice, Which level should we practice?"]

        self.levelList = ["Sweet, let's do it!", "Alright, get ready!"]

        self.complimentList = ["Nice!", "Good", "Correct", "Ding Ding Ding", "Nice going", "That's right!"]

        self.wrongAnswerList = ["Sorry!", "Nope!", "Too bad"]

        self.testList = ["Okay!, what level do you want to test?"]

    def savePracticeLevel(self, level):
        file = open("levelDB.txt", "a+")
        file.write(self.name + " " + str(level) + "\n")

    def retrievePracticeLevel(self):
        file = open("levelDB.txt", "r")
        levels = []
        for line in file.readlines():
            if line.split()[0] == self.name:
                levels.append(line.split()[1])
        return list(set(levels))

    def onRobotEvent(self, event):
        print(event)
        if event == 'LanguageChanged':
            self.langLock.release()
        elif event == 'TextDone':
            self.speechLock.release()
        elif event == 'GestureDone':
            self.gestureLock.release()

    def onAudioIntent(self, *args, intentName):
        print("INTENT NAME = " + intentName)
        if intentName == "answer_name" and len(args) > 0:
            print(args[0])
            self.name = args[0]
            self.nameLock.release()

        if intentName == "answer_practice_test" and len(args) > 0:
            print(args[0])
            self.practiceTest = args[0]
            self.practiceTestLock.release()

        if intentName == "answer_level" and len(args) > 0:
            print(args[0])
            self.level = args[0]
            self.levelLock.release()

        if intentName == "answer_answerLevelOne" and len(args) > 0:
            print(args[0])
            self.answer = args[0]
            self.answerLock.release()

        if intentName == "answer_after_practice" and len(args) > 0:
            print(args[0])
            self.answerAfterPractice = args[0]
            self.answerLock.release()


# Run the application
sample = SampleApplication()
sample.main()
sample.stop()
