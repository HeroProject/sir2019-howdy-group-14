from threading import Semaphore
import AbstractApplication as Base
import time
import random


class SampleApplication(Base.AbstractApplication):
    def main(self):
        self.setLanguage("en-US")
        self.sayAnimated("Howdy partner! Who are you?")
        time.sleep(3)

        self.setDialogflowKey("howdy-plvfvo-ca953d08832f.json")
        self.setDialogflowAgent("howdy-plvfvo")
        self.introduction()
        self.name = None
        self.practiceTest = None
        self.level = None

    def introduction(self):
        self.nameLock = Semaphore(0)
        self.setAudioContext("awaiting_name")
        self.startListening()
        self.nameLock.acquire(timeout=4)
        self.stopListening()
        if not self.name:
            self.nameLock.acquire(timeout=1)

        print(self.name)
        self.name = "George"
        if self.name:
            self.pickFromList(self.nameList)
            self.practiceOrTest()

    def practiceOrTest(self):
        self.practiceTestLock = Semaphore(0)
        self.setAudioContext("awaiting_practice_test")
        self.startListening()
        self.practiceTestLock.acquire(timeout=4)
        self.stopListening()
        self.practiceTest = "practice"

        if self.practiceTest:
            self.pickFromList(self.practiceOrTestList)
            self.whichLevel()

    def whichLevel(self):
        self.levelTestLock = Semaphore(0)
        if self.practiceTest == "practice":
            self.setAudioContext("practice-followup")
        elif self.practiceTest == "test":
            self.setAudioContext("test-followup")
        self.startListening()
        self.levelTestLock.acquire(timeout=4)
        self.stopListening()
        self.level = int("1")

        if self.level:
            self.pickFromList(self.levelList)

        if self.practiceTest == "practice":
            self.practice()
        elif self. practiceTest == "test":
            self.test()


    def practice(self):
        wordDict = self.wordDicts[self.level]
        self.sayAnimated("Lets practice!")
        numberWord = 0
        for key, value in wordDict.items():
            self.practiceWord(key, value, numberWord)
            numberWord += 1

        self.sayAnimated("Nice practice session brosky, you're the best in the wild west!")
        self.sayAnimated("Do you want to Test your new skills?")

        self.savePracticeLevel()

    def practiceWord(self, key, value, numberWord):
        self.sayAnimated(key + "means" + value)
        if numberWord < 3:
            self.sayAnimated("repeat please")
        self.sleep(2)
        # May implement a method that recognises the input from user and checks if the pronunciation is correct.


    def test(self):
        wordDict = self.wordDicts[self.level]
        self.sayAnimated("Alright let's test your skills")
        counter = 0
        for key, value in wordDict.items():
            self.testWord(key, value, counter)
            counter += 1

    def testWord(self, key, value, counter):
        self.answer = None
        if counter < 3:
            self.sayAnimated("What does" + key + "mean?")
        else:
            self.sayAnimated(key)
        self.startListening()
        self.answerLock.acquire(timeout=4)
        self.stopListening()
        if self.answer:
            if value == self.answer:
                self.sayAnimated(self.pickFromList(self.complimentList))
            else:
                self.sayAnimated(self.pickFromList((self.wrongAnswerList)))
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
            3 : { "entrepreneur": "ryady", "dedication": "tafan", "citizenship": "almuatina", "citizen": "muatin",
                  "expect": "tuaqie", "learn": "taealam", "wish": "raghba", "effort": "majhud", "offer": "eard",
                  "discuss": "munaqasha", "allow": "alsamah", "areas": "almanatiq", "resume": "sirat dhatia",
                  "employment": "tawzif"}
            ,
            4 : {"catering industry": "sinaeat altaeam", "working hours": "saeat aleamal",
                 "civil servant": "iinaa aistifan", "police officer": "dabit shurta", "fireman": "rajul al'iitfa",
                 "retail": "altajzia", "hospital": "mustashfaa", "full - time": "waqt kamil", "part - time":
                     "dawam jazyaa", "tax": "hamal"}
            ,
            5 : {"drivers license": "rukhsat alssayiq", "apply for" : "altaqadum bitalab lilhusul",
                 "responsibilities": "almaswuwliat", "vacancy": "shaghir", "vocational level": "almustawaa almahniu",
                 "cover letter": "ghita' alrisala", "life insurance": "altaamin ealaa alhaya",
                 "tax advisor": "mustashar aldarayib", "investing": "alaistithmar"}
        }

    def pickFromList(self, list):
        randint = random.randint(0, len(list) - 1)
        self.sayAnimated(list[randint])
        time.sleep(5)

    def listen(self):
        self.startListening()
        self.practice_testLock.acquire(timeout=4)
        self.stopListening()

    def loadLists(self):
        self.nameList = [self.name + "My friend, do you want to practice with me or should I take a test",
                         "Nice to meet you" + self.name +  "my name is Howdy! Would you like to practice or take a test?",
                         "My name is Howdy, saddle up" + self.name + " Would you like to practice or take a test?",
                         "yeeee haww, nice to meet you "+ self.name + ", I'm Howdy! Would you like to practice or take a test?",
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
        print(event)


# Run the application
sample = SampleApplication()
sample.main()
sample.stop()