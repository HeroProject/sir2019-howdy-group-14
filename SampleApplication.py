from threading import Semaphore
import AbstractApplication as Base
import time
import random

"""
Class that implements the main functionality of the integration robot Howdy.
    """


class SampleApplication(Base.AbstractApplication):
    def __init__(self):
        # Initiate variables that will be used globally.
        self.answer = None
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
        Base.AbstractApplication.__init__(self)

    def main(self):
        # Record the audio that the user inputs for later analysis and debugging.
        self.setRecordAudio(True)

        # Set the language to American English
        self.langLock = Semaphore(0)
        self.setLanguage('en-US')
        self.langLock.release()

        # Connect to Dialogflow.
        self.setDialogflowKey("howdy-plvfvo-ca953d08832f.json")
        self.setDialogflowAgent("howdy-plvfvo")

        # Nao says hey, and asks for name.
        self.speechLock = Semaphore(0)
        self.sayAnimated("Howdy partner! What is your name")
        self.speechLock.acquire()

        # Start introduction sequence.
        self.introduction()

    def introduction(self):
        # Listen for name of the user.
        self.nameLock = Semaphore(0)
        self.setAudioContext("answer_name")
        self.startListening()
        self.nameLock.acquire(timeout=4)
        self.stopListening()

        # If no name was recorded keep asking for name until it is acquired:
        if self.name == "":
            while self.name == "":
                self.speechLock = Semaphore(0)
                self.say("Sorry I didn't catch your name, could you repeat it?")
                self.speechLock.acquire()
                self.startListening()
                self.nameLock.acquire(timeout=4)
                self.stopListening()

        # If a name was recorded, pick one of the answers and start next function
        else:
            print(self.name)
            self.pickFromList(self.nameList)
            self.practiceOrTest()

    def practiceOrTest(self):
        # Listen for whether to test or to practice
        self.practiceTestLock = Semaphore(0)
        self.setAudioContext("awaiting_practice_test")
        self.startListening()
        self.practiceTestLock.acquire(timeout=4)
        self.stopListening()

        # If no name was recorded keep asking for name until it is acquired:
        if self.practiceTest == "":
            while self.practiceTest == "":
                self.speechLock = Semaphore(0)
                self.say("Sorry I didn't catch that")
                self.speechLock.acquire()
                self.startListening()
                self.practiceTestLock.acquire(timeout=4)
                self.stopListening()

        if self.practiceTest == "practice":
            self.pickFromList(self.practiceList)
            self.whichLevel()

        elif self.practiceTest == "test":
            self.pickFromList(self.testList)
            self.whichLevel()

    def whichLevel(self):
        self.levelTestLock = Semaphore(0)
        if self.practiceTest == "practice":
            self.setAudioContext("practice-followup")
        elif self.practiceTest == "test":
            self.setAudioContext("test-followup")
        self.startListening()
        self.levelTestLock.acquire(timeout=3)
        self.stopListening()
        self.level = int("1")

        if self.level:
            self.pickFromList(self.levelList)

        if self.practiceTest == "practice":
            self.practice()
        elif self.practiceTest == "test":
            self.test()

    def practice(self):
        wordDict = self.wordDicts[self.level]
        self.sayAnimated(
            "Lets practice!, I will first say a word in english and then repeat it in Syrian, then I'll give you a couple seconds to repeat the word")
        time.sleep(6)
        numberWord = 0
        for key, value in wordDict.items():
            self.practiceWord(key, value, numberWord)
            numberWord += 1

        self.sayAnimated("Nice practice session brosky, you're the best in the wild west!")
        self.sayAnimated("Do you want to Test your new skills?")

        self.savePracticeLevel(self.level)

    def practiceWord(self, key, value, numberWord):
        self.learnTime = Semaphore(0)
        self.learnTime.acquire(timeout=1)
        self.setLanguage("en-US")
        self.say(key)
        self.learnTime.acquire(timeout=1)
        self.setLanguage("nl-NL")
        self.say("means")
        self.learnTime.acquire(timeout=0.5)
        self.say(value)
        self.learnTime.acquire(timeout=1)
        if numberWord < 3:
            self.sayAnimated("repeat please")
        self.learnTime.acquire(timeout=5)
        # May implement a method that recognises the input from user and checks if the pronunciation is correct.

    def test(self):
        """
        Here the robots starts to test the user by looping through all the words to test.
            """

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
            # we are using a copy to loop through, otherwises it loops through the list while items are being
            # removed. This makes the code skip some elements of the list.
            for key, value in wrongWords[:]:
                self.testWord(key, value, counter, wrongWords)

    def testWord(self, key, value, counter, wrongWords):
        """Tests a single word by giving the word the user is supposed to translate, and to listen to the input of
        user, checking if the given word corresponds to the answer """
        if counter < 3:
            # After pronouncing three words, exclude the "What does... mean from the speech of the robot. "
            self.sayAnimated("What does" + key + "mean?")
        else:
            self.sayAnimated(key)
        self.startListening()
        self.answerLock.acquire(timeout=4)
        self.stopListening()
        if self.answer:
            if value == self.answer:
                # If the given value by the user is right, say it is right and remove it to the wrongWords list.
                self.sayAnimated(self.pickFromList(self.complimentList))
                if value in [v for k, v in wrongWords]:
                    wrongWords.remove((key, value))


            else:
                # If the given value by the user is wrong, say it is wrong and append it to the wrongWords list.
                self.sayAnimated(self.pickFromList((self.wrongAnswerList)))
                wrongWords.append((key, value))
        else:
            self.sayAnimated("speak up you shy bitch")

    def loadDicts(self):
        self.wordDicts = {
            1: {"hello": "marhabaan", "goodbye": "wadaeaan", "job": "wazifa", "wages": "ujur", "salary": "ratib",
                "work": "eamal", "goal": "hadaf", "colleague": "zamil", "skills": "maharat", "manager": "mudir",
                "manage": "tadbir", "company": "sharika", "task": "muhima", "interview": "muqabala"}
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

    def pickFromList(self, list):
        randint = random.randint(0, len(list) - 1)
        self.speechLock = Semaphore(0)
        self.sayAnimated(list[randint])
        self.speechLock.acquire()


    def listen(self):
        self.startListening()
        self.practice_testLock.acquire(timeout=4)
        self.stopListening()

    def loadLists(self):
        self.nameList = [self.name + "My friend, do you want to practice with me or should I take a test",
                         "Nice to meet you" + self.name + "my name is Howdy! Would you like to practice or take a test?",
                         "My name is Howdy, saddle up" + self.name + " Would you like to practice or take a test?",
                         "yeeee haww, nice to meet you " + self.name + ", I'm Howdy! Would you like to practice or take a test?",
                         "Hey " + self.name + ", Good to see you. Do you want to practice or take a test?"]

        self.practiceList = ["Okay! Which level do you want to practice? There are 5 levels.",
                             "Alright! Lets do that, There are 5 Levels, which level do you want to practice?",
                             "There are 5 Levels, which level should we practice?",
                             "Choose a level, you can choose from 1 to 5.",
                             "You can choose which level you want to practice, Which level should we practice?"]

        self.levelList = ["Sweet, let's do it!", "Alright, get ready!"]

        self.complimentList = ["Nice!", "Good", "Correct", "Ding Ding Ding", "Nice going", "That's right!"]

        self.wrongAnswerList = ["Sorry!", "Nope!", "Too bad"]

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
        if event == 'LanguageChanged':
            self.langLock.release()
        elif event == 'TextDone':
            self.speechLock.release()
        elif event == 'GestureDone':
            self.gestureLock.release()

    def onAudioIntent(self, *args, intentName):
        if intentName == "answer_name" and len(args) > 0:
            print("hey")
            self.name = args[0]
            self.nameLock.release()

        if intentName == "awaiting_practice_test" and len(args) > 0:
            self.practiceTest = args[0]
            self.practiceTestLock.release()


# Run the application
sample = SampleApplication()
sample.main()
sample.stop()
