# Currency Converter - AWS EC2 Deployment Guide

This guide walks you through deploying the Currency Converter Flask application on an AWS EC2 instance with Nginx reverse proxy and Let's Encrypt SSL.

## Prerequisites

- AWS EC2 instance (Ubuntu 20.04/22.04 recommended)
- EC2 security group allowing ports: 22 (SSH), 80 (HTTP), 443 (HTTPS)
- Domain name configured (e.g., `currencyconverter.krishnagarg.online`)
- SSH key pair for EC2 access

## Architecture

```
Internet → DNS → Nginx (Port 80/443) → Gunicorn (Port 5000) → Flask App
```

---

## Step 1: Connect to EC2 Instance

SSH into your EC2 instance using your key pair:

```bash
ssh -i <your-key>.pem ubuntu@<EC2_PUBLIC_IP>
```

Replace `<your-key>.pem` with your actual key file and `<EC2_PUBLIC_IP>` with your instance's public IP.

---

## Step 2: Update System & Install Dependencies

Update package lists and install required packages:

```bash
sudo apt update -y
sudo apt install -y python3 python3-venv python3-pip git nginx
```

Verify installations:

```bash
python3 --version
git --version
nginx -v
```

---

## Step 3: Clone Repository & Setup Python Environment

Clone the repository to `/opt`:

```bash
cd /opt
sudo git clone <YOUR_GIT_REPO_URL> currencyconverter
sudo chown -R ubuntu:ubuntu /opt/currencyconverter
```

Create and activate virtual environment:

```bash
cd /opt/currencyconverter
python3 -m venv venv
source venv/bin/activate
```

Install Python dependencies:

```bash
pip install --upgrade pip
pip install -r requirements.txt
pip install gunicorn
```

---

## Step 4: Test Gunicorn

Before creating the service, verify Gunicorn works with your app:

```bash
gunicorn --bind 0.0.0.0:5000 --workers 2 currency_converter_web:app
```

**Note:** Replace `currency_converter_web:app` with your actual entrypoint:
- If your file is `app.py` with `app = Flask(__name__)`, use: `app:app`
- If your file is `main.py` with `application = Flask(__name__)`, use: `main:application`
- If your file is `currency_converter_web.py` with `app = Flask(__name__)`, use: `currency_converter_web:app`

Press `Ctrl+C` to stop the test server.

---

## Step 5: Create Systemd Service

Create a systemd service file for automatic startup:

```bash
sudo tee /etc/systemd/system/currencyconverter.service > /dev/null <<'EOF'
[Unit]
Description=Currency Converter Python App (Gunicorn)
After=network.target

[Service]
User=ubuntu
Group=www-data
WorkingDirectory=/opt/currencyconverter
Environment="PATH=/opt/currencyconverter/venv/bin"
ExecStart=/opt/currencyconverter/venv/bin/gunicorn --workers 2 --bind 127.0.0.1:5000 currency_converter_web:app
Restart=always
RestartSec=3

[Install]
WantedBy=multi-user.target
EOF
```

**Important:** Update `currency_converter_web:app` in the `ExecStart` line to match your actual entrypoint.

Enable and start the service:

```bash
sudo systemctl daemon-reload
sudo systemctl enable currencyconverter
sudo systemctl start currencyconverter
```

Check service status:

```bash
sudo systemctl status currencyconverter --no-pager
```

View logs (useful for debugging):

```bash
journalctl -u currencyconverter -f
```

---

## Step 6: Configure Nginx Reverse Proxy

Create Nginx configuration:

```bash
sudo tee /etc/nginx/sites-available/currencyconverter > /dev/null <<'EOF'
server {
    listen 80;
    server_name currencyconverter.krishnagarg.online;

    location / {
        proxy_pass http://127.0.0.1:5000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
EOF
```

**Important:** Replace `currencyconverter.krishnagarg.online` with your actual domain.

Enable the site and reload Nginx:

```bash
sudo ln -s /etc/nginx/sites-available/currencyconverter /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl reload nginx
```

---

## Step 7: Configure DNS

In your DNS provider (Route53, Cloudflare, etc.), create an A record:

- **Type:** A
- **Name:** currencyconverter
- **Value:** `<EC2_PUBLIC_IP>`
- **TTL:** 60 seconds (for testing)

Wait 1-2 minutes for DNS propagation, then verify:

```bash
dig +short currencyconverter.krishnagarg.online
```

Test HTTP access:

```bash
curl -I http://currencyconverter.krishnagarg.online
```

---

## Step 8: Setup SSL with Let's Encrypt

Install Certbot:

```bash
sudo apt install -y certbot python3-certbot-nginx
```

Obtain and install SSL certificate:

```bash
sudo certbot --nginx -d currencyconverter.krishnagarg.online
```

Follow the prompts:
- Enter your email address
- Agree to terms of service
- Choose whether to redirect HTTP to HTTPS (recommended: Yes)

Test automatic renewal:

```bash
sudo certbot renew --dry-run
```

Verify HTTPS is working:

```bash
curl -I https://currencyconverter.krishnagarg.online
```

---

## Maintenance Commands

### View application logs
```bash
journalctl -u currencyconverter -f
```

### Restart the application
```bash
sudo systemctl restart currencyconverter
```

### Stop the application
```bash
sudo systemctl stop currencyconverter
```

### Update application code
```bash
cd /opt/currencyconverter
git pull origin main
source venv/bin/activate
pip install -r requirements.txt
sudo systemctl restart currencyconverter
```

### Check Nginx status
```bash
sudo systemctl status nginx
```

### Check Nginx error logs
```bash
sudo tail -f /var/log/nginx/error.log
```

---

## Troubleshooting

### Application won't start
1. Check logs: `journalctl -u currencyconverter -n 50`
2. Verify the entrypoint in the service file matches your app
3. Ensure all dependencies are installed: `pip list`
4. Test manually: `cd /opt/currencyconverter && source venv/bin/activate && gunicorn --bind 0.0.0.0:5000 currency_converter_web:app`

### 502 Bad Gateway
- Check if Gunicorn is running: `sudo systemctl status currencyconverter`
- Check if the app is listening on port 5000: `sudo netstat -tlnp | grep 5000`
- Review Nginx error logs: `sudo tail -f /var/log/nginx/error.log`

### SSL certificate issues
- Ensure port 443 is open in EC2 security group
- Verify DNS is pointing to correct IP: `dig +short currencyconverter.krishnagarg.online`
- Check Certbot logs: `sudo certbot certificates`

### Can't access via domain
- Verify EC2 security group allows ports 80 and 443
- Check DNS propagation: `dig +short currencyconverter.krishnagarg.online`
- Ensure Nginx is running: `sudo systemctl status nginx`

---