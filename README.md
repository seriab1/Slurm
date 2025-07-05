# Slurm Auto-Deploy HPC

A comprehensive toolkit for automatically deploying and managing High Performance Computing (HPC) jobs on Slurm clusters. This tool provides cross-platform support (Linux and Windows) for seamless interaction with remote HPC systems.

## Features

- **Cross-platform support**: Works on Linux and Windows
- **Automated job deployment**: Transfer files and submit jobs with a single command
- **Environment management**: Create and manage Python virtual environments on remote systems
- **Real-time monitoring**: Live job status monitoring with tmux sessions
- **Job management**: Cancel jobs, view logs, and check system information
- **Secure authentication**: SSH-based secure connections with password authentication

## Prerequisites

### Linux
- `sshpass` (for password authentication)
- `rsync` (for file synchronization)
- `ssh` client

### Windows
- Cygwin64 (included in the project structure)
- PuTTY (included in the project structure)

## Installation

1. Clone the repository:
```bash
git clone <repository-url>
cd slurm-auto-deploy
```

2. Configure your connection and job parameters:
   - Edit `_config.ini` with your HPC cluster details
   - Edit `_secret.ini` with your SSH password

3. For Linux, install required packages:
```bash
# Ubuntu/Debian
sudo apt-get install sshpass rsync openssh-client

# CentOS/RHEL
sudo yum install sshpass rsync openssh-clients
```

## Configuration

### _config.ini
Configure your HPC cluster connection and job parameters:

```ini
[SLURM]
user = your_username
host = your.hpc.cluster.com
port = 22
folder_dest = project_name
task_name = your_job_name
exclude_folders = Slurm, .git, .idea
source_folder = "../"
partition = compute
nodes = 1
ntasks = 4
mail = your.email@domain.com
mail_type = END,FAIL
time = 0-06:00:00
name_venv = project_venv
environment = ../venv/project_venv/bin/activate
application = python
script = main.py
log_debug = 1
module = ""
```

### _secret.ini
Store your SSH password securely:

```ini
[SSH]
password = your_ssh_password
```

## Usage

### Core Scripts

#### 1. Deploy and Submit Job
```bash
python send_job.py
```
- Transfers your project files to the HPC cluster
- Creates a Slurm job script
- Submits the job to the queue
- Sets up real-time monitoring with tmux

#### 2. Access Server
```bash
python access_server.py
```
- Opens an SSH connection to the HPC cluster
- Provides interactive shell access

#### 3. Create Python Environment
```bash
python create_environment.py
```
- Creates a Python virtual environment on the remote system
- Installs required packages from your project
- Automatically generates requirements.txt using pipreqs

#### 4. Monitor Jobs and System
```bash
python information.py
```
- Displays partition information
- Shows job queue status
- Lists job history
- Provides system overview

#### 5. View Job Logs
```bash
python last_job_log.py
```
- Displays output and error logs from the most recent job
- Provides commands for manual log inspection

#### 6. Cancel All Jobs
```bash
python cancel_all_job.py
```
- Cancels all running jobs for your user
- Shows job status before and after cancellation

### Setup Scripts

#### Add SSH Known Host
```bash
python add_ssh_known_host_win.py
```
- Adds the HPC cluster to your SSH known hosts
- Prevents SSH connection warnings

## Slurm Job Template

The system automatically generates Slurm job scripts with the following structure:

```bash
#!/bin/bash
#SBATCH -J job_name
#SBATCH -p partition_name
#SBATCH -n nodes
#SBATCH -c ntasks
#SBATCH --mem=0
#SBATCH -o job_name_%j.out
#SBATCH -e job_name_%j.err
#SBATCH --mail-user=email@domain.com
#SBATCH --mail-type=END,FAIL
#SBATCH --time=0-06:00:00

# Load environment
source ../venv/project/bin/activate

# Execute application
srun python -u script.py
```

## Real-time Monitoring

When you submit a job, the system automatically creates a tmux session with multiple panels:

- **Panel 0**: Real-time error log (`tail -f job_name_id.err`)
- **Panel 1**: Real-time output log (`tail -f job_name_id.out`)
- **Panel 2**: System information (`watch sinfo`)
- **Panel 3**: Job accounting (`sacct -u username`)
- **Panel 4**: Job queue (`watch squeue`)
- **Panel 5**: Disk usage (`du -hs $HOME`)

## File Structure

```
slurm-auto-deploy/
├── _config.ini                 # Configuration file
├── _secret.ini                 # SSH credentials
├── README.md                   # This file
├── access_server.py            # SSH connection script
├── add_ssh_known_host_win.py   # SSH host setup
├── cancel_all_job.py           # Cancel all jobs
├── create_environment.py       # Environment setup
├── information.py              # System information
├── last_job_log.py            # View job logs
├── send_job.py                # Main deployment script
├── log/                       # Temporary files directory
├── cygwin64/                  # Windows SSH tools
└── putty/                     # Windows PuTTY tools
```

## Security Considerations

- Keep `_secret.ini` secure and never commit it to version control
- Consider using SSH keys instead of passwords for production environments
- Regularly update your SSH client and tools
- Use strong passwords and enable two-factor authentication when available

## Troubleshooting

### Common Issues

1. **SSH Connection Failed**: Check host, port, and credentials in config files
2. **Permission Denied**: Verify SSH key permissions and user access
3. **Job Submission Failed**: Check Slurm partition availability and resource limits
4. **File Transfer Issues**: Verify rsync/scp availability and network connectivity

### Debug Mode

Enable debug logging by setting `log_debug = 1` in `_config.ini`. This will:
- Add `-u` flag to Python execution for unbuffered output
- Show detailed transfer progress
- Display verbose SSH connection information

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Test on your target platforms
5. Submit a pull request



## Support

For issues and questions:
- Create an issue in the repository
- Check the troubleshooting section
- Review Slurm documentation for cluster-specific configurations

## Disclaimer

This project includes and uses third-party software:

- **PuTTY**: A free SSH and telnet client. PuTTY is copyright © 1997-2022 Simon Tatham. All rights reserved. For more information, visit [https://www.putty.org/](https://www.putty.org/)

- **Cygwin64**: A large collection of GNU and Open Source tools which provide functionality similar to a Linux distribution on Windows. Cygwin is maintained by Red Hat, Inc. and other contributors. For more information, visit [https://www.cygwin.com/](https://www.cygwin.com/)

These tools are included for convenience and functionality on Windows systems. All credit and rights belong to their respective authors and maintainers. Users should comply with the licenses and terms of use of these third-party components.

---

**Note**: This tool is designed for educational and research purposes. Always follow your institution's HPC usage policies and security guidelines.
