import subprocess
import configparser
import os
import shutil

script_dir = os.path.dirname(os.path.abspath(__file__))
os.chdir(script_dir)

config = configparser.ConfigParser()
config.read('_secret.ini')
config.read('_config.ini')
user            = config['SLURM']['user']
password        = config['SSH']['password']
host            = config['SLURM']['host']
port            = config['SLURM']['port']

putty_path = r".\putty\putty.exe"

if os.name == "posix":
    print("Linux o macOS")

    if shutil.which("sshpass") is None:
        print("sshpass no está instalado.")
        exit(1)

    commands_file = "log/tmp_commands2.sh"
    with open(commands_file, "w") as f:
        f.write("echo All current jobs\n")
        f.write(f"squeue -u {user} -l\n")
        f.write("echo Cancel all jobs\n")
        f.write(f"scancel -u {user}\n")
        f.write("echo All current jobs\n")
        f.write(f"squeue -u {user} -l\n")
        f.write("exec bash\n")

    command = f"sshpass -p '{password}' ssh -t -o StrictHostKeyChecking=no -p {port} {user}@{host} < {commands_file}"
    subprocess.run(command, shell=True)

elif os.name == "nt":
    print("Windows")
    commands_file = "log/tmp_commands2.txt"
    with open(commands_file, "w") as f:
        f.write("export TERM=xterm\n")
        f.write(f"echo All current jobs\n")
        f.write(f"squeue -u {user} -l\n")
        f.write(f"echo Cancel all jobs\n")
        f.write(f"scancel -u {user}\n")
        f.write(f"echo All current jobs\n")
        f.write(f"squeue -u {user} -l\n")
        f.write("/bin/bash\n")

    command = [putty_path, "-ssh", f"{user}@{host}", "-P", port, "-pw", f"{password}", "-m", commands_file, "-t"]
    proc = subprocess.Popen(command, shell=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

