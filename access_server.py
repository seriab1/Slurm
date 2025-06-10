import subprocess
import configparser
import os
import shutil

script_dir = os.path.dirname(os.path.abspath(__file__))
os.chdir(script_dir)
# Parameters from the configuration file
config = configparser.ConfigParser()
config.read('_config.ini')
config.read('_secret.ini')

user            = config['SLURM']['user']
password        = config['SSH']['password']
host            = config['SLURM']['host']
port            = config['SLURM']['port']


putty_path = r".\putty\putty.exe"

if os.name == "posix":
    print("Linux o macOS")

    if shutil.which("sshpass") is None:
        print(" sshpass no está instalado.")
        exit(1)

    command = [
        "sshpass", "-p", password,
        "ssh", "-o", "StrictHostKeyChecking=no",
        "-p", port,
        f"{user}@{host}"
    ]
    subprocess.run(command, check=True)


elif os.name == "nt":
    print("Windows")
    commands_file = "log/tmp_commands.txt"
    with open(commands_file, "w") as f:
        f.write("export TERM=xterm\n")
        f.write("/bin/bash\n")

    command = [putty_path, "-ssh", f"{user}@{host}", "-P", port, "-pw", f"{password}", "-m", commands_file, "-t"]
    proc = subprocess.Popen(command, shell=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)


