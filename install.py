#!/usr/bin/python3

import getpass, os, subprocess

script_dir = os.path.dirname(os.path.realpath(__file__))
os.chdir(script_dir)

username = getpass.getuser()

def shell_cmd(cmd):
    print(cmd)
    print(subprocess.check_output(cmd, shell=True, encoding="utf-8"))

def update_crontab(name, line):
    # Read current 
    completed = subprocess.run(f"crontab -u {username} -l", shell=True, capture_output=True, encoding="utf-8")
    assert(completed.returncode == 0 or "no crontab for" in completed.stderr)
    prev_crontab = completed.stdout.splitlines(keepends=True)
    token = f"AUTOINSTALLED:{name}"
    installme = f"{line} # {token}"
    old_lines = [line for line in prev_crontab if token in line]
    other_lines = [line for line in prev_crontab if token not in line]
    if len(old_lines) == 1 and old_lines[0].strip() == installme:
        print(f"{name}: already up-to-date in {username} crontab: {installme}")
        return
    elif old_lines:
        print(f"{name}: replacing entry in {username} crontab: {installme}")
    else:
        print(f"{name}: adding entry in {username} crontab: {installme}")
    new_crontab_content = ''.join(other_lines) + installme + "\n"
    subprocess.check_output(f"crontab -u {username} -", shell=True, input=new_crontab_content, encoding="utf-8")

python = "/usr/bin/python3"

print("Install python dependencies")
shell_cmd(f"{python} -c 'import wiringpi' 2>/dev/null || sudo {python} -m pip install wiringpi")
print("Turning on i2c")
shell_cmd("sudo raspi-config nonint do_i2c 0")

update_crontab("vizy-power-monitor-standalone", f"@reboot {script_dir}/start")
shell_cmd("./start")



