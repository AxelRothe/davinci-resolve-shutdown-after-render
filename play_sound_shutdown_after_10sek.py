# coding=utf-8
"""
Resolve Script to shut down the system after a render is complete.
"""
import os
import threading
import time
import subprocess
from inspect import getsourcefile
from os.path import abspath

execlocation = abspath(getsourcefile(lambda: 0))

class AbortSignal(Exception):
    """
    Exception to signal that the render should be aborted.
    """
    signal = False

    def __init__(self, default):
        self.signal = default

    def setstate(self, b):
        self.signal = b


class App:
    """
    The main app
    """
    timeinseconds = 10
    abort = AbortSignal(False)
    shutdownNow = False
    window = None

    def __init__(self, title):
        self.whenever(self.playSound, ('render_complete.mp3',))

        self.loop()

    def whenever(self, target, args=()):
        threading.Thread(target=target, args=args).start()

    def playSound(self, soundfile):
        """
        Play a sound file.
        """
        subprocess.Popen(['afplay', (abspath(execlocation + "/../assets/sounds/" + soundfile))])

    def notify(self, title, message):
        """
        Notify the user of the render completion.
        """
        # os.system("""osascript -e 'display notification "{}" with title "{}"'""".format(message, title))
        result = subprocess.check_output(
            """osascript -e 'display dialog "Render Complete. Shutting Down in 10 Seconds." buttons {"ABORT", "Shutdown"} default button "ABORT"'""", shell=True).format(message, title)
        # check if result contains the word ABORT
        if "ABORT" in result:
            self.abort.setstate(True)
        elif "Shutdown" in result:
            self.shutdownNow = True


    def loop(self):
        delta = 0
        # get current time
        starttime = time.time()
        self.whenever(self.notify, ('Render Complete', 'Shutting Down'))

        while True:
            if self.abort.signal:
                print("Abort signal set, exiting...")
                break

            # calculate delta
            delta = time.time() - starttime
            print(round(self.timeinseconds - delta))

            # if the delta is greater than the time in seconds, shutdown
            if delta > self.timeinseconds or self.shutdownNow:
                print("Shutting Down")
                break

            time.sleep(1)

        # if the abort signal is set, exit the app
        if not self.abort.signal:
            print("Shutdown")
            # show a message box
            # os.system("""osascript -e 'display dialog "Render Complete. Shutting Down in 10 Seconds." buttons {"ABORT", "Shutdown"} default button "ABORT"'""")
            os.system("""osascript -e 'tell application "System Events" to shut down'""")
            # subprocess.Popen(['shutdown', '-h', 'now'])

        exit()


# Press the green button in the gutter to run the script.
if __name__ == '__main__':
    App("Render Complete")
