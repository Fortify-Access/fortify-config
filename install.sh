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

  python3 -m venv venv
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

  # Step 9: Downlaod and extract sing-box binary
  echo "Step 9: Downloading sing-box..."
  if [[ "$(uname -m)" == "x86_64" ]]; then
      package_url="https://github.com/SagerNet/sing-box/releases/download/v1.3.0/sing-box-1.3.0-linux-amd64.tar.gz"
  elif [[ "$(uname -m)" == "aarch64" ]]; then
      package_url="https://github.com/SagerNet/sing-box/releases/download/v1.3.0/sing-box-1.3.0-linux-arm64.tar.gz"
  else
      echo "Unsupported system architecture."
      exit 1
  fi

  # Fetch the latest (including pre-releases) release version number from GitHub API
  latest_version=$(curl -s "https://api.github.com/repos/SagerNet/sing-box/releases" | jq -r '.[0].name')
  
  # Detect server architecture
  arch=$(uname -m)
  
  # Map architecture names
  case ${arch} in
      x86_64)
          arch="amd64"
          ;;
      aarch64)
          arch="arm64"
          ;;
      armv7l)
          arch="armv7"
          ;;
  esac
  
  # Prepare package names
  package_name="sing-box-${latest_version}-linux-${arch}"
  # Download the latest release package (.tar.gz) from GitHub
  curl -sLo "/opt/fortify/${package_name}.tar.gz" "https://github.com/SagerNet/sing-box/releases/download/v${latest_version}/${package_name}.tar.gz"
  # Extract the package and move the binary to /root
  tar -xzf "/opt/fortify/${package_name}.tar.gz" -C /opt/fortify/
  # Cleanup the package
  rm -r "/opt/fortify/${package_name}.tar.gz"
}

check_cloudflare_details_validation() {
  response=$(curl -X GET "https://api.cloudflare.com/client/v4/user/tokens/verify" \
     -H "Authorization: Bearer $1" \
     -H "Content-Type:application/json")
  # Check if the status key is true
  status=$(echo "$response" | jq -r '.status')
  if [[ "$status" == "true" ]]; then
    return "true"
  else
    return "false"
  fi
}

# Function to install Nginx and configure services
install_nginx() {
  # Step 4: Install Nginx
  echo "Step 4: Installing Nginx..."
  if [[ "$(uname)" == "Linux" ]]; then
    if [[ -x "$(command -v apt)" ]]; then
      apt update
      apt install -y nginx
      apt install -y jq
    elif [[ -x "$(command -v yum)" ]]; then
      yum install -y epel-release
      yum install -y nginx
      yum install -y jq
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
  while true
    do
      read -p "Enter your cloudflare zone id: " cz
      read -p "Enter your cloudflare authentication token: " ct
      read -p "Enter your parent domain: " domain
      token_validation=$(check_cloudflare_details_validation "$ct")
      if [[ "$token_validation" == "true" ]]; then
        break
      fi
    done
  python manage.py initialproject --ip $(curl -s https://api.ipify.org) -cz "$cz" -ct "$ct" --domain "$domain"
else
  python manage.py initialproject --ip $(curl -s https://api.ipify.org)
fi

echo "Installation completed successfully."
