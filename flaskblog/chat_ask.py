import aiml
import os




kernel = aiml.Kernel()

if os.path.isfile("bot_brain.brn"):
    kernel.bootstrap(brainFile = "bot_brain.brn")
else:
    kernel.bootstrap(learnFiles = os.path.abspath("aiml/botdata/std-startup.xml"), commands = "load aiml b")
    kernel.saveBrain("bot_brain.brn")

def replying(message):

    # message = input("Enter your message to the bot: ")
    if message == "quit":
        pass
    elif message == "save":
        kernel.saveBrain("bot_brain.brn")
    else:
        bot_response = kernel.respond(message)
        return bot_response
