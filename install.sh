#!/bin/bash

# Function to install the project
install_project() {
  # Step 1: Clone project and install requirements
  echo "Step 1: Cloning project and installing requirements..."
  cd /opt
  git clone https://github.com/Fortify-Access/fortify-config.git fortify
  cd fortify

  # Detect the python version that is installed in server
  python_version=$(python3 -c 'import sys; version=sys.version_info[:2]; print("{0}.{1}".format(*version))')

  if [[ -x "$(command -v apt)" ]]; then
    apt install -y python$python_version-venv
  elif [[ -x "$(command -v yum)" ]]; then
    yum install -y python$python_version-venv
  else
    echo "Unsupported package manager."
    exit 1
  fi

  python3 -m venv venv
  source venv/bin/activate
  pip install -r requirements.txt
  mkdir -p /opt/fortify/media/qr_codes/

  # Step 6: Run migrations and create superuser
  echo "Step 6: Running migrations and creating superuser..."
  python manage.py makemigrations config inbounds
  python manage.py migrate
  python manage.py createsuperuser

  # Step 7: Configure and start Django service
  echo "Step 7: Configuring and starting Django service..."
  cp /opt/fortify/services/fortify.service /etc/systemd/system/
  systemctl enable fortify.service
  systemctl start fortify.service

  # Step 8: Docker installation for
  echo "Step 8: Docker installation..."
  sudo apt-get install -y \
    apt-transport-https \
    ca-certificates \
    curl \
    software-properties-common curl -fsSL https://yum.dockerproject.org/gpg | sudo apt-key add - sudo add-apt-repository \
    "deb https://apt.dockerproject.org/repo/ \
    ubuntu-$(lsb_release -cs) \
    main" sudo apt-get update
  sudo apt-get -y install docker-engine  
  sudo usermod -aG docker $(whoami)
  docker run --name celery_db -p 5080:6379 -d redis

  # Step 9: Configure and start Django celery service
  echo "Step 9: Configuring and starting Django celery service..."
  cp /opt/fortify/services/celery.service /etc/systemd/system/
  cp /opt/fortify/services/celerybeat.service /etc/systemd/system/
  systemctl enable celery.service
  systemctl start celery.service
  systemctl enable celerybeat.service
  systemctl start celerybeat.service
}

# Step 10: Initialize the project
install_project
server_ip=$(curl -s https://api.ipify.org)
echo "Step 10: Initializing the project..."

# Check arguments to determine which function to execute
echo "ALLOWED_HOSTS=$server_ip:8000" > .env
python manage.py initialproject --ip "$server_ip"

echo "Installation completed successfully."
