#!/bin/bash

# Function to install the project
install_project() {
  # Step 1: Clone project and install requirements
  echo "Step 1: Cloning project and installing requirements..."
  cd /opt
  git clone https://github.com/Fortify-Access/fortify-config.git fortify
  cd fortify

  if [[ "$(uname)" == "Linux" ]]; then
    if [[ -x "$(command -v apt)" ]]; then
      apt install -y python3.10-venv
    elif [[ -x "$(command -v yum)" ]]; then
      yum install -y python3.10-venv
    else
      echo "Unsupported package manager."
      exit 1
    fi
  else
    echo "Unsupported operating system."
    exit 1
  fi

  python3 -m venv env
  source env/bin/activate
  pip install -r requirements.txt

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

}

# Function to install Nginx and configure services
install_nginx() {
  # Step 4: Install Nginx
  echo "Step 4: Installing Nginx..."
  if [[ "$(uname)" == "Linux" ]]; then
    if [[ -x "$(command -v apt)" ]]; then
      apt update
      apt install -y nginx
    elif [[ -x "$(command -v yum)" ]]; then
      yum install -y epel-release
      yum install -y nginx-extras
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

  echo "Nginx installation and service setup completed successfully."
}


# Step 9: Initialize the project
install_project
echo "Step 9: Initializing the project..."

# Check arguments to determine which function to execute
if [[ "$1" == "nginx-enable" ]]; then
  install_nginx
  read -p "Enter your cloudflare zone id: " cz
  read -p "Enter your cloudflare authentication token: " ct
  read -p "Enter your parent domain: " domain
  read -p "Enter your incoming port: " port
  python manage.py initialproject --ip $(curl -s https://api.ipify.org) -cz "$cz" -ct "$ct" --domain "$domain" -p "$port"
else
  python manage.py initialproject --ip $(curl -s https://api.ipify.org)
fi

echo "Installation completed successfully."
