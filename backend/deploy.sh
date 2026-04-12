#!/bin/bash
# ==========================================================
# Newsume AI — Backend Deployment Script for GCP Compute Engine
# Run this ON the GCP instance after cloning the repo.
# Usage: chmod +x deploy.sh && ./deploy.sh
# ==========================================================

set -e

echo "=== Newsume AI Backend Deployment ==="

# 1. Install system dependencies
echo "[1/6] Installing system packages..."
sudo apt-get update -qq
sudo apt-get install -y -qq python3 python3-pip python3-venv git

# 2. Create virtual environment
echo "[2/6] Setting up Python virtual environment..."
cd ~/Newsume_AI/backend
python3 -m venv .venv
source .venv/bin/activate

# 3. Install Python dependencies
echo "[3/6] Installing Python dependencies..."
pip install --upgrade pip -q
pip install -r requirements.txt -q

# 4. Create .env if it doesn't exist
echo "[4/6] Checking .env file..."
if [ ! -f .env ]; then
    cp .env.example .env
    echo "  ⚠️  Created .env from template. Edit it with your API keys:"
    echo "     nano ~/Newsume_AI/backend/.env"
else
    echo "  ✓ .env already exists"
fi

# 5. Create systemd service
echo "[5/6] Creating systemd service..."
sudo tee /etc/systemd/system/newsume-api.service > /dev/null << 'EOF'
[Unit]
Description=Newsume AI Backend API
After=network.target

[Service]
Type=simple
User=$USER
WorkingDirectory=/home/$USER/Newsume_AI/backend
Environment=PATH=/home/$USER/Newsume_AI/backend/.venv/bin:/usr/bin
ExecStart=/home/$USER/Newsume_AI/backend/.venv/bin/python main.py
Restart=always
RestartSec=5

[Install]
WantedBy=multi-user.target
EOF

# Fix the $USER placeholder in the service file
sudo sed -i "s|\$USER|$USER|g" /etc/systemd/system/newsume-api.service

sudo systemctl daemon-reload
sudo systemctl enable newsume-api
sudo systemctl restart newsume-api

# 6. Open firewall port
echo "[6/6] Opening firewall port 8000..."
sudo ufw allow 8000/tcp 2>/dev/null || true

echo ""
echo "=== Deployment Complete! ==="
echo "  Backend running at: http://$(curl -s ifconfig.me):8000"
echo "  Health check:       http://$(curl -s ifconfig.me):8000/health"
echo "  Check status:       sudo systemctl status newsume-api"
echo "  View logs:          sudo journalctl -u newsume-api -f"
echo ""
echo "  ⚠️  Don't forget to:"
echo "  1. Edit .env with your GROQ_API_KEY: nano ~/Newsume_AI/backend/.env"
echo "  2. Open port 8000 in GCP Firewall Rules (VPC Network → Firewall)"
echo "     gcloud compute firewall-rules create allow-newsume-8000 \\"
echo "       --allow tcp:8000 --source-ranges 0.0.0.0/0 --target-tags http-server"
