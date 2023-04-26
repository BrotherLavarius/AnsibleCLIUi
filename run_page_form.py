import npyscreen
import os
import subprocess
import threading

class CustomBufferPager(npyscreen.BufferPager):
    def __init__(self, *args, **kwargs):
        max_height = self._find_height(kwargs.get("parent"))
        kwargs["max_height"] = max_height
        super().__init__(*args, **kwargs)

    def _find_height(self, parent):
        if not parent:
            return 50
        return parent.lines  # Reserve 5 lines for buttons and other widgets

    def add_line(self, line):
        self.buffer([line])


class RunPageForm(npyscreen.Form):
    def create(self):

        self.start_button = self.add(npyscreen.ButtonPress, name="Start Ansible",
                                     when_pressed_function=self.start_ansible, rely=1)
        self.stop_button = self.add(npyscreen.ButtonPress, name="Stop Ansible",
                                    when_pressed_function=self.stop_ansible, rely=1, relx=20)
        self.goto_main_button = self.add(npyscreen.ButtonPress, name="Go to MAIN page",
                                         when_pressed_function=self.goto_main_page, rely=1, relx=40)
        self.add(npyscreen.FixedText, value="-" * 40, editable=False)  # Delimiter line


        self.log_output = self.add(CustomBufferPager, name="Log Output:", max_height=None, rely=3)

        self.add(npyscreen.FixedText, value="-" * 40, editable=False)  # Delimiter line
        self.ansible_process = None

    def set_vars(self, env_input, extra_vars, playbooks, vault_password_file, ssh_key_file,inventory_files):
        self.env_input_value = env_input
        self.extra_vars_value = extra_vars
        self.playbooks_value = playbooks
        self.vault_password_file_value = vault_password_file
        self.ssh_key_file = ssh_key_file
        self.inventory_files = inventory_files

    def goto_main_page(self):
        self.parentApp.switchForm("MAIN")

    def start_ansible(self):
        if self.ansible_process is not None and self.ansible_process.poll() is None:
            self.log_output.add_line("Ansible is already running. Please stop it before starting a new one.")
            return

        extra_vars = self.extra_vars_value if self.extra_vars_value else '""'
        env_vars = self.env_input_value.split() if self.env_input_value else []
        playbook = self.playbooks_value
        vault_password_file = self.vault_password_file_value
        ssh_key_file = self.ssh_key_file

        cmd = ["ansible-playbook"] + env_vars + ["-e", extra_vars, playbook]

        # Add inventory files to the command
        for inventory_file in self.inventory_files:
            cmd += ["-i", inventory_file]

        # Include vault password file if it's present
        if vault_password_file:
            cmd += ["--vault-password-file", vault_password_file]

        if ssh_key_file:
            cmd.append(f'--private-key={ssh_key_file}')

        os.environ['ANSIBLE_FORCE_COLOR'] = '1'  # Add this line to force color mode


        self.log_output.add_line(f"Running: {' '.join(cmd)}")

        # Add bufsize=1 parameter to enable line buffering
        self.ansible_process = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True, bufsize=1)

        threading.Thread(target=self.stream_output).start()

    def stop_ansible(self):
        if self.ansible_process is not None and self.ansible_process.poll() is None:
            self.ansible_process.terminate()
            self.log_output.add_line("Ansible process terminated.")
        else:
            self.log_output.add_line("No running Ansible process to stop.")

    def stream_output(self):
        for line in self.ansible_process.stdout:
            self.log_output.add_line(line.rstrip())
            self.log_output.update()  # Force screen to refresh
            self.log_output.display()  # Force the widget to redraw

