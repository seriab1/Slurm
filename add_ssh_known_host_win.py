import subprocess
import configparser
import os

script_dir = os.path.dirname(os.path.abspath(__file__))
os.chdir(script_dir)

if os.name == "posix":
    print("Linux o macOS")
    config = configparser.ConfigParser()
    config.read('_config.ini')
    host = config['SLURM']['host']

    subprocess.run(f"mkdir -p ~/.ssh && ssh-keyscan -H {host} >> ~/.ssh/known_hosts", shell=True)
elif os.name == "nt":
    print("Windows")
    # Parameters from the configuration file
    config = configparser.ConfigParser()
    config.read('_config.ini')
    host= config['SLURM']['host']

    path = r".\cygwin64\Cygwin.bat"
    process = subprocess.Popen(path, shell=True, stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, encoding='utf8')
    process.stdin.write('mkdir -p ~/.ssh\n')
    process.stdin.write(f'ssh-keyscan -H {host} >> ~/.ssh/known_hosts\n')
    process.stdin.flush()
    stdout, stderr = process.communicate()

    print(stdout)
    print(stderr)