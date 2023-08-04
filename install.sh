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
  python manage.py makemigrations
  python manage.py migrate
  python manage.py createsuperuser

  # Step 7: Configure and start Django service
  echo "Step 7: Configuring and starting Django service..."
  cp /opt/fortify/services/fortify.service /etc/systemd/system/
  systemctl enable fortify.service
  systemctl start fortify.service

  # Step 8: Configure and start sing-box service
  echo "Step 8: Configuring and starting sing-box service..."
  cp /opt/fortify/services/singbox.service /etc/systemd/system/
  systemctl enable singbox.service
  systemctl start singbox.service

  # Step 9: Downlaod and extract sing-box binary
  echo "Step 4: Downloading sing-box..."
  if [[ "$(uname -m)" == "x86_64" ]]; then
      package_url="https://github.com/SagerNet/sing-box/releases/download/v1.3.0/sing-box-1.3.0-linux-amd64.tar.gz"
      package_name="sing-box-1.3.0-linux-amd64"
  elif [[ "$(uname -m)" == "aarch64" ]]; then
      package_url="https://github.com/SagerNet/sing-box/releases/download/v1.3.0/sing-box-1.3.0-linux-arm64.tar.gz"
      package_name="sing-box-1.3.0-linux-arm64"
  else
      echo "Unsupported system architecture."
      exit 1
  fi

  # Step 7: Prepare package names
  echo "Step 7: Prepare package names..."
  # Download the latest release package (.tar.gz) from GitHub
  curl -sLo "/opt/fortify-config/${package_name}.tar.gz" $package_url
  # Extract the package and move the binary to /root
  tar -xzf "/opt/fortify-config/${package_name}.tar.gz" -C /opt/fortify-config
  # Change the singbox long directory name
  mv "/opt/fortify-config/${package_name}" "/opt/fortify-config/sing-box"
  # Cleanup the package
  rm -r "/opt/fortify-config/${package_name}.tar.gz"
  # Copy the default sing-box configuration file
  cp /opt/fortify-config/services/default_config.json /opt/fortify-server/sing-box/config.json
}

# Step 9: Initialize the project
install_project
server_ip=$(curl -s https://api.ipify.org)
echo "Step 9: Initializing the project..."

# Check arguments to determine which function to execute
echo "ALLOWED_HOSTS=$server_ip:8000" > .env
python manage.py initialproject --ip "$server_ip"

echo "Installation completed successfully."
