
import curses

import npyscreen
from main_page_form import MainPageForm
from run_page_form import RunPageForm

class AnsibleApp(npyscreen.NPSAppManaged):
    def onStart(self):
        # Enable mouse support
        curses.mousemask(curses.ALL_MOUSE_EVENTS | curses.REPORT_MOUSE_POSITION)

        self.addForm("MAIN", MainPageForm, name="Ansible Console GUI - Main Page")
        self.addForm("RUN", RunPageForm, name="Ansible Console GUI - Run Page")


    def onCleanExit(self):
        npyscreen.notify_wait("Goodbye!")

if __name__ == "__main__":
    app = AnsibleApp()
    app.run()

