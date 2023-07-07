#!/bin/bash

# Step 1: Clone project and install requirements
echo "Step 1: Cloning project and installing requirements..."
cd /opt
git clone -b admin_redesign https://github.com/Fortify-Access/fortify-config.git fortify
git checkout admin_redesign
cd fortify

# Step 2: Download package based on system architecture
echo "Step 2: Downloading sing-box..."
if [[ "$(uname -m)" == "x86_64" ]]; then
  package_url="https://github.com/SagerNet/sing-box/releases/download/v1.3.0/sing-box-1.3.0-linux-amd64.tar.gz"
elif [[ "$(uname -m)" == "aarch64" ]]; then
  package_url="https://github.com/SagerNet/sing-box/releases/download/v1.3.0/sing-box-1.3.0-linux-arm64.tar.gz"
else
  echo "Unsupported system architecture."
  exit 1
fi

wget "$package_url" -P /opt/fortify
package_file=$(basename "$package_url")

# Step 3: Extract the downloaded package
echo "Step 3: Extracting sing-box..."
tar xf "/opt/fortify/$package_file" -C /opt/fortify/sing-box
rm "/opt/fortify/$package_file"

# Step 4: Install Nginx
echo "Step 4: Installing Nginx..."
if [[ "$(uname)" == "Linux" ]]; then
  if [[ -x "$(command -v apt)" ]]; then
    apt update
    apt install -y nginx
    apt install -y python3.10-venv
  elif [[ -x "$(command -v yum)" ]]; then
    yum install -y epel-release
    yum install -y nginx
    yum install -y python3.10-venv
  else
    echo "Unsupported package manager."
    exit 1
  fi
else
  echo "Unsupported operating system."
  exit 1
fi

# Step 5: Replace Nginx conf file and restart Nginx
echo "Step 5: Configuring Nginx..."
cp /opt/fortify/services/nginx.conf /etc/nginx/nginx.conf
systemctl restart nginx

# Step 6: Run migrations and create superuser
echo "Step 6: Running migrations and creating superuser..."
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
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

# Step 9: Initialize the project
echo "Step 9: Initializing the project..."
python manage.py initialproject $(curl -s https://api.ipify.org)

echo "Installation completed successfully."
