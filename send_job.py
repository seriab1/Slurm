import subprocess
import configparser
import shutil
import os

script_dir = os.path.dirname(os.path.abspath(__file__))
os.chdir(script_dir)
config = configparser.ConfigParser()
config.read('_config.ini')
config.read('_secret.ini')

user            = config['SLURM']['user']
password        = config['SSH']['password']
host            = config['SLURM']['host']
folder_dest     = config['SLURM']['folder_dest']
task_name       = config['SLURM']['task_name']
exclude_folders = config['SLURM']['exclude_folders'].split(', ')
partition       = config['SLURM']['partition']
nodes           = int(config['SLURM']['nodes'])
ntasks          = int(config['SLURM']['ntasks'])
mail            = config['SLURM']['mail']
mail_type       = config['SLURM']['mail_type']
time            = config['SLURM']['time']
environment     = config['SLURM']['environment']
script          = config['SLURM']['script']
log_debug       = int(config['SLURM']['log_debug'])
source_folder   = config['SLURM']['source_folder']
port = str(config['SLURM']['port'])
application = config['SLURM']['application']
module       = config['SLURM']['module']

# Path to executables
rsync_path = r".\cygwin64\bin\rsync.exe"
ssh_path = r".\cygwin64\bin\ssh.exe"
sshpass_path = r".\cygwin64\bin\sshpass.exe"
putty_path = r".\putty\putty.exe"

# Debug information
# parameter = "-u" if log_debug == 1 else ""
parameter = "-u" if log_debug == 1 and application == "python" else None
source = f"source {environment}" if application == "python" else  "#"
module1 = f"{module}" if module == "" else "#"

# Contents of the file model_python.sh
content = f"""#!/bin/bash
#------- SLURM OPTIONS
#SBATCH -J {task_name}
#SBATCH -p {partition}
#SBATCH -n {nodes}
#SBATCH -c {ntasks}
#SBATCH --mem=0
#SBATCH -o {task_name}_%j.out
#SBATCH -e {task_name}_%j.err
#SBATCH --mail-user={mail}
#SBATCH --mail-type={mail_type}
#SBATCH --time={time}

#------- LOAD ENVIRONMENT
{source}
#------- LOAD MODULES
{module1}
#------- USER COMMANDS

echo "Job start: $(date)"

srun {application} {parameter} {script}

echo "Job end: $(date)"
"""


if os.name == "posix":
    print("Linux o macOS")

    # Verifica si sshpass está instalado
    if shutil.which("sshpass") is None:
        print("sshpass no está instalado.")
        exit(1)

    commands_file = "log/tmp_commands6.sh"
    with open(commands_file, "w") as f:
        f.write(f"""#!/bin/bash
    cd {folder_dest}
    sbatch model_python.sh > jobid.txt
    tmux ls 2>/dev/null | cut -d: -f1 | xargs -n 1 tmux kill-session -t 2>/dev/null || true

    # Extraer job ID
    job_id=$(grep -o '[0-9]\\+' jobid.txt | head -1)
    echo $job_id > id

    # Crear sesión tmux
    tmux new-session -d -s General
    tmux rename-window 'Information'
    tmux split-window -h
    tmux split-window -v
    tmux select-pane -t 0
    tmux split-window -v
    tmux select-pane -t 2
    tmux split-window -v
    tmux select-pane -t 4
    tmux split-window -v

    # Enviar comandos a cada panel
    tmux select-pane -t 0
    tmux send-keys "sleep 2 && id=\\$(cat id) && tail -n +1 -f {task_name}_\\$id.err" C-m

    tmux select-pane -t 1
    tmux send-keys "sleep 2 && id=\\$(cat id) && tail -n +1 -f {task_name}_\\$id.out" C-m

    tmux select-pane -t 2
    tmux send-keys "watch sinfo" C-m

    tmux select-pane -t 3
    tmux send-keys "sacct -u {user}" C-m

    tmux select-pane -t 4
    tmux send-keys "watch squeue" C-m

    tmux select-pane -t 5
    tmux send-keys "du -hs \\$HOME" C-m

    # Conectar a la sesión
    tmux attach-session -t General
    """)

    os.chmod(commands_file, 0o755)
    upload_command = f"sshpass -p '{password}' scp -P {port} {commands_file} {user}@{host}:~/tmp_commands.sh"
    subprocess.run(upload_command, shell=True)

    command = f"sshpass -p '{password}' ssh -tt -o StrictHostKeyChecking=no -p {port} {user}@{host} 'bash ~/tmp_commands.sh'"
    subprocess.run(command, shell=True)


elif os.name == "nt":
    print("Windows")
    # Nombre del archivo
    file_name = "../model_python.sh"
    with open(file_name, "wb") as file:
        content = content.replace('\r\n', '\n')
        file.write(content.encode())

    # Source and destination folders
    destination = f"{user}@{host}:/home/{user}/{folder_dest}"

    # Build the rsync command
    exclude_options = " ".join([f'--exclude="{folder}"' for folder in exclude_folders])

    rsync_command = (
        f'{sshpass_path} -p "{password}" '
        f'{rsync_path} -avz --progress {exclude_options} '
        f'-e "{ssh_path} -o StrictHostKeyChecking=no -p {port}" '
        f'{source_folder} {destination}'
    )

    try:
        process = subprocess.Popen(rsync_command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, shell=True)

        while True:
            output = process.stdout.readline()
            if output == '' and process.poll() is not None:
                break
            if output:
                print(output.strip())
        rc = process.poll()

        if rc == 0:
            print("Folder sent successfully.")
        else:
            print("Error sending the folder.")
            print("Errores:")
            for line in process.stderr:
                print(line.strip())
    except Exception as e:
        print(f"Error executing the rsync command: {e}")


    if rc == 0:
        commands_file = "log/tmp_commands6.txt"
        with open(commands_file, "w") as f:
            f.write(f"cd {folder_dest} \n")
            f.write("sbatch model_python.sh > jobid.txt \n")
            f.write("tmux ls | cut -d: -f1 | xargs -n 1 tmux kill-session -t\n")
            f.write("job_id=$(grep -o '[0-9]\+' jobid.txt | awk '{print $1}' > id) \n")
            f.write(
                rf"tmux new-session -s General \; rename-window 'Information' \; "
                f"split-window -h \; split-window -v \; "  
                f"select-pane -t 0 \; split-window -v \; "  
                f"select-pane -t 2 \; split-window -v \; "  
                f"select-pane -t 4 \; split-window -v \; "  
    
                f"select-pane -t 0 \; send-keys 'sleep 2; id=$(cat id) ;tail -n +1 -f {task_name}_$id.err' C-m \; "  
                f"select-pane -t 1 \; send-keys 'sleep 2;id=$(cat id) ;tail -n +1 -f {task_name}_$id.out' C-m \; "  
                f"select-pane -t 2 \; send-keys 'watch sinfo' C-m \; "  
                f"select-pane -t 3 \; send-keys 'sacct -u {user}' C-m \; "  
                f"select-pane -t 4 \; send-keys 'watch squeue' C-m \; "  
                f"select-pane -t 5 \; send-keys 'du -hs $HOME' C-m\n"
            )

            f.write("tmux kill-server\n")

        command = [putty_path, "-ssh", f"{user}@{host}", "-P", port, "-pw", f"{password}", "-m", commands_file, "-t"]
        proc = subprocess.Popen(command, shell=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)