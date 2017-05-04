import random
from threading import Timer

class color:
   PURPLE = '\033[95m'
   CYAN = '\033[96m'
   DARKCYAN = '\033[36m'
   BLUE = '\033[94m'
   GREEN = '\033[92m'
   YELLOW = '\033[93m'
   RED = '\033[91m'
   BOLD = '\033[1m'
   UNDERLINE = '\033[4m'
   END = '\033[0m'

score = 0

list = ("Toothpaste", "Seashell", "Binder", "Computer", "Laptop", "Tablet", "Turing", "Python", "Circuit")
list2 = ("Mathematics", "Onomatopoeia", "Obnoxious", "Archiving", "Licencing")

endgame = 0

def printbob():
    print("you lose bro")
    endgame = 1

def boys():
    points = 0
    while(score >= 0):
        timeout = 10
        timer = Timer(timeout, printbob)
        timer.start()
        if(points < 5):
            cs = random.choice(list)
        else:
            cs = random.choice(list2)
        print("Type this sentence:", color.GREEN + cs + color.END)
        user = "You have %d seconds to choose the correct answer...\n" % timeout
        answer = raw_input(user)
        print len(answer)
        timer.cancel()
        if (answer == cs) and (endgame == 0):
            print("Nice")
            points += 1
        else:
            print("Bye")
            exit()
boys()