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
name_env        = config['SLURM']['name_venv']
folder_dest     = config['SLURM']['folder_dest']

putty_path = r".\putty\putty.exe"

if os.name == "posix":
    print("Linux o macOS")

    if shutil.which("sshpass") is None:
        print("sshpass no está instalado.")
        exit(1)

    commands_file = "log/tmp_commands3.sh"
    with open(commands_file, "w") as f:
        f.write(f"python3.12 -m venv venv/{name_env}\n")
        f.write(f"source venv/{name_env}/bin/activate\n")
        f.write("pip install --upgrade pip\n")
        f.write("pip install pipreqs\n")
        f.write(f"cd {folder_dest}\n")
        f.write("pipreqs ./ --force\n")
        f.write("pip install -r requirements.txt\n")
        f.write("exec bash\n")

    command = f"sshpass -p '{password}' ssh -t -o StrictHostKeyChecking=no -p {port} {user}@{host} < {commands_file}"
    subprocess.run(command, shell=True)

elif os.name == "nt":
    print("Windows")
    commands_file = "log/tmp_commands3.txt"
    with open(commands_file, "w") as f:
        f.write("export TERM=xterm\n")
        f.write(f"python3.12 -m venv venv/{name_env}\n")
        f.write(f"source venv/{name_env}/bin/activate\n")
        f.write("pip install --upgrade pip\n")
        f.write("pip install pipreqs\n")
        f.write(f"cd {folder_dest}\n")
        f.write("pipreqs ./ --force\n")
        f.write("pip install -r requirements.txt\n")
        f.write("/bin/bash\n")
    command = [putty_path, "-ssh", f"{user}@{host}", "-P", port, "-pw", f"{password}", "-m", commands_file, "-t"]
    proc = subprocess.Popen(command, shell=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
