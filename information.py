import subprocess
import configparser
import os
import shutil

script_dir = os.path.dirname(os.path.abspath(__file__))
os.chdir(script_dir)

config = configparser.ConfigParser()
config.read('_config.ini')
config.read('_secret.ini')
user            = config['SLURM']['user']
password        = config['SSH']['password']
host            = config['SLURM']['host']
port            = config['SLURM']['port']
folder_dest     = config['SLURM']['folder_dest']

putty_path = r".\putty\putty.exe"

if os.name == "posix":
    print("Linux o macOS")

    # Verifica si sshpass está instalado
    if shutil.which("sshpass") is None:
        print(" sshpass no está instalado.")
        exit(1)

    commands = f"""
    echo View detailed partition information
    sinfo
    echo View priority of all pending jobs
    sprio
    echo All current jobs
    squeue
    echo Display the job history of the current user
    sacct -u {user}
    exec bash
    """
    command = [
        "sshpass", "-p", password,
        "ssh", "-p", port, "-t", f"{user}@{host}",
        "bash -s"
    ]
    subprocess.run(command, input=commands.encode(), check=True)


elif os.name == "nt":
    print("Windows")
    # view error of the last job
    # Create a command file with the commands to execute
    commands_file = "log/tmp_commands4.txt"
    with open(commands_file, "w") as f:
        f.write("export TERM=xterm\n")
        f.write(f"echo View detailed partition information\n")
        f.write(f"sinfo\n")
        f.write(f"echo View priority of all pending jobs\n")
        f.write(f"sprio\n")
        f.write(f"echo All current jobs\n")
        f.write(f"squeue\n")
        f.write(f"echo Display the job history of the current user\n")
        f.write(f"sacct -u {user}\n")
        f.write("/bin/bash\n")
    command = [putty_path, "-ssh", f"{user}@{host}", "-P", port, "-pw", f"{password}", "-m", commands_file, "-t"]
    proc = subprocess.Popen(command, shell=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

