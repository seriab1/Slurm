import subprocess
import configparser
import os
import shutil

script_dir = os.path.dirname(os.path.abspath(__file__))
os.chdir(script_dir)

config = configparser.ConfigParser()
config.read('_config.ini')
config.read('_secret.ini')
user = config['SLURM']['user']
password = config['SSH']['password']
host = config['SLURM']['host']
folder_dest = config['SLURM']['folder_dest']
task_name = config['SLURM']['task_name']
port = config['SLURM']['port']

if os.name == "posix":
    print("Linux o macOS")

    if shutil.which("sshpass") is None:
        print(" sshpass no está instalado.")
        exit(1)

    commands_file = "log/tmp_commands5.sh"
    with open(commands_file, "w") as f:
        f.write(f"cd {folder_dest}\n")
        f.write(f"id=$(cat id) ;less {task_name}_$id.err\n")
        f.write(f"echo 'To view the output, manually execute: id=$(cat id) ;less {task_name}_$id.err'\n")
        f.write(f"cat {task_name}_$id.err\n")
        f.write(f"echo 'To view the output, manually execute: id=$(cat id) ;cat {task_name}_$id.out'\n")
        f.write(f"cat {task_name}_$id.out\n")
        f.write("exec bash\n")

    command = f"sshpass -p '{password}' ssh -t -o StrictHostKeyChecking=no -p {port} {user}@{host} < {commands_file}"
    subprocess.run(command, shell=True)


elif os.name == "nt":
    print("Windows")

    putty_path = r".\putty\putty.exe"
    commands_file = "log/tmp_commands.txt"
    with open(commands_file, "w") as f:
        f.write("export TERM=xterm\n")
        f.write(f"cd {folder_dest} \n")
        f.write(f"id=$(cat id) ;less {task_name}_$id.err\n")
        f.write(f"echo 'To view the output, manually execute: id=$(cat id) ;cat {task_name}_$id.err'\n")
        f.write("/bin/bash\n")
    command = [putty_path, "-ssh", f"{user}@{host}", "-P", port, "-pw", f"{password}", "-m", commands_file, "-t"]
    proc = subprocess.Popen(command, shell=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

    commands_file = "log/tmp_commands5.txt"
    with open(commands_file, "w") as f:
        f.write("export TERM=xterm\n")
        f.write(f"cd {folder_dest} \n")
        f.write(f"id=$(cat id) ;less {task_name}_$id.out\n")
        f.write(f"echo 'To view the output, manually execute: id=$(cat id) ;less {task_name}_$id.out'\n")
        f.write("/bin/bash\n")

    command = [putty_path, "-ssh", f"{user}@{host}", "-P", port, "-pw", f"{password}", "-m", commands_file, "-t"]
    proc = subprocess.Popen(command, shell=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
