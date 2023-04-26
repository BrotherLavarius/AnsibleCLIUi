import npyscreen
import json
import os

class MainPageForm(npyscreen.Form):
    def create(self):
        self.env_input = self.add(npyscreen.TitleText, name="Environment Variables:")
        self.add(npyscreen.FixedText, value="-" * 40, editable=False)  # Delimiter line

        self.extra_vars = self.add(npyscreen.TitleText, name="Extra Variables (-e):")
        self.add(npyscreen.FixedText, value="-" * 40, editable=False)  # Delimiter line

        self.ssh_key_file = self.add(npyscreen.TitleFilenameCombo, name="Select SSH Key:")
        self.add(npyscreen.FixedText, value="-" * 40, editable=False)  # Delimiter line


        self.playbooks = self.add(npyscreen.TitleFilenameCombo, name="Select a playbook:")
        self.add(npyscreen.FixedText, value="-" * 40, editable=False)  # Delimiter line

        self.vault_password_file = self.add(npyscreen.TitleFilenameCombo, name="Vault Password File:")
        self.add(npyscreen.FixedText, value="-" * 40, editable=False)  # Delimiter line



        self.inventory_file = self.add(npyscreen.TitleFilenameCombo, name="Add Inventory File:")

        self.add_inventory_button = self.add(npyscreen.ButtonPress, name="Add Inventory",
                                             when_pressed_function=self.add_inventory_file)
        self.add(npyscreen.FixedText, value="-" * 40, editable=False)  # Delimiter line

        self.selected_inventory_files = self.add(npyscreen.TitleMultiLine, name="Selected Inventory Files:",
                                                 max_height=4, values=[], scroll_exit=True)
        self.add(npyscreen.FixedText, value="-" * 40, editable=False)  # Delimiter line

        self.save_history = self.add(npyscreen.ButtonPress, name="Save Variables",
                                        when_pressed_function=self.save_history)
        self.goto_run_button = self.add(npyscreen.ButtonPress, name="Go to RUN page",
                                        when_pressed_function=self.goto_run_page)

        self.load_history()

    def add_inventory_file(self):
        if self.inventory_file.value and self.inventory_file.value not in self.selected_inventory_files.values:
            self.selected_inventory_files.values.append(self.inventory_file.value)
            self.selected_inventory_files.display()
            self.inventory_file.value = ''

    def keypress(self, input, key):
        if key == '+':
            self.move_inventory_up()
        elif key == '-':
            self.move_inventory_down()
        else:
            super().keypress(input, key)

    def move_inventory_up(self):
        idx = self.selected_inventory_files.cursor_line
        if idx > 0:
            self.selected_inventory_files.values[idx], self.selected_inventory_files.values[idx - 1] = self.selected_inventory_files.values[idx - 1], self.selected_inventory_files.values[idx]
            self.selected_inventory_files.cursor_line -= 1
            self.selected_inventory_files.display()

    def move_inventory_down(self):
        idx = self.selected_inventory_files.cursor_line
        if idx < len(self.selected_inventory_files.values) - 1:
            self.selected_inventory_files.values[idx], self.selected_inventory_files.values[idx + 1] = self.selected_inventory_files.values[idx + 1], self.selected_inventory_files.values[idx]
            self.selected_inventory_files.cursor_line += 1
            self.selected_inventory_files.display()

    def goto_run_page(self):
        run_page = self.parentApp.getForm("RUN")
        run_page.set_vars(
            env_input=self.env_input.value,
            extra_vars=self.extra_vars.value,
            playbooks=self.playbooks.value,
            vault_password_file=self.vault_password_file.value,
            ssh_key_file=self.ssh_key_file.value,  # Add this line
            inventory_files=self.selected_inventory_files.values   # Pass the selected_inventory_files values to the RunPageForm
        )

        self.parentApp.switchForm("RUN")

    def save_history(self):
        history = {
            "env_input": self.env_input.value,
            "extra_vars": self.extra_vars.value,
            "playbook": self.playbooks.value,
            "vault_password_file": self.vault_password_file.value,  # Save vault password file value
            "ssh_key_file": self.ssh_key_file.value,  # Add this line
            "inventory_files": self.selected_inventory_files.values
        }

        with open(os.path.expanduser("~/.ansible_cli.json"), "w") as f:
            json.dump(history, f)

    def load_history(self):
        try:
            with open(os.path.expanduser("~/.ansible_cli.json"), "r") as f:
                history = json.load(f)

            self.env_input.value = history["env_input"]
            self.extra_vars.value = history["extra_vars"]
            self.playbooks.value = history["playbook"]
            self.vault_password_file.value = history.get("vault_password_file", "") # Use get with a default value
            self.ssh_key_file.value = history.get("ssh_key_file", "") # Use get with a default value
            self.selected_inventory_files.values = history.get("inventory_files", []) # Use get with a default value
        except FileNotFoundError:
            pass  # If the file doesn't exist, we won't load any history.

