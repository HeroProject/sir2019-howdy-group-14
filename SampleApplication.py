from threading import Semaphore
import AbstractApplication as Base
import time
import random

class SampleApplication(Base.AbstractApplication):
    def main(self):
        self.setLanguage('en-US')
        self.sayAnimated("Howdy, partner!, Who are you?")
        time.sleep(3)

        self.setDialogflowKey('howdy-plvfvo-ca953d08832f.json')
        self.setDialogflowAgent('howdy-plvfvo')

        self.name = None
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
            list = [self.name + "My friend, do you want to practice with me or should I take a test"]
            randint = random.randint(0,len(list) -1)
            self.sayAnimated(list[randint])
            time.sleep(5)

        self.practice_test = None
        self.practice_testLock = Semaphore(0)
        self.setAudioContext("awaiting_practice_test")
        self.startListening()
        self.practice_testLock.acquire(timeout=4)
        self.stopListening()
        self.practice_test = "practice"

        if self.practice_test:
            self.sayAnimated("alright, do you want to learn new words, or do you wan to revise some old ones? ")
            time.sleep(5)

        self.old_new = None
        self.old_new_testLock = Semaphore(0)
        self.setAudioContext("awaiting_practice_test")
        self.startListening()
        self.old_new_testLock.acquire(timeout=4)
        self.stopListening()
        self.old_new = "old"

    def onRobotEvent(self, event):
        print(event)


# Run the application
sample = SampleApplication()
sample.main()
sample.stop()
