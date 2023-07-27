# Smart Contract Crawler

## CronJob for Every 1 Hour
```sh
0 * * * * /usr/bin/python3 /path/to/your_python_file.py
```

## Job1: Crawl Addresses

## Job2: Crawl API

## Production Ready
To make a Flask app production-ready with Nginx, we need to configure Nginx as a reverse proxy server that forwards incoming HTTP requests to the Flask app. This setup allows Nginx to handle tasks like static file serving, load balancing, and SSL termination, while the Flask app focuses on processing business logic.

Here are the general steps to achieve this:

1. Set up the Flask app with Gunicorn: Gunicorn is a production-ready WSGI HTTP server that can serve your Flask app. It provides multiple worker processes, ensuring better performance and concurrency.

2. Install and configure Nginx: Nginx will act as a reverse proxy to forward incoming requests to the Gunicorn server.

3. Secure the communication with SSL/TLS: Optionally, you can configure SSL certificates to enable HTTPS for secure communication between the client and server.

Here's a step-by-step guide:

1. Set up the Flask app with Gunicorn:
First, install Gunicorn using pip:

```bash
pip install gunicorn
```

Next, start your Flask app using Gunicorn:

```bash
gunicorn -w 4 -b 127.0.0.1:8000 your_app:app
```

Replace `your_app` with the name of your Flask app instance (usually `app`).

2. Install and configure Nginx:

Install Nginx on your server:

```bash
sudo apt update
sudo apt install nginx
```

Create an Nginx server block (configuration file) for your Flask app:

```bash
sudo nano /etc/nginx/sites-available/your_app
```

Add the following configuration (replace `your_app` with your domain or IP and update paths accordingly):

```
server {
    listen 80;
    server_name your_domain_or_ip;

    location / {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
    }

    # Optional: Enable SSL/TLS (HTTPS) with your SSL certificate
    # listen 443 ssl;
    # ssl_certificate /path/to/your_ssl_certificate.crt;
    # ssl_certificate_key /path/to/your_ssl_certificate_key.key;
}
```

Enable the Nginx server block by creating a symbolic link in the `sites-enabled` directory:

```bash
sudo ln -s /etc/nginx/sites-available/your_app /etc/nginx/sites-enabled/
```

Remove the default Nginx configuration if not required:

```bash
sudo rm /etc/nginx/sites-enabled/default
```

Test Nginx configuration:

```bash
sudo nginx -t
```

Restart Nginx to apply the changes:

```bash
sudo systemctl restart nginx
```

3. Secure the communication with SSL/TLS (optional):

If you want to enable HTTPS, you need to obtain an SSL certificate and key. You can get one from a trusted certificate authority (CA) or use a free option like Let's Encrypt.

```bash
# Install Certbot for Let's Encrypt
sudo apt install certbot python3-certbot-nginx

# Obtain and install SSL certificate
sudo certbot --nginx -d your_domain_or_ip
```

Certbot will automatically configure Nginx to use SSL/TLS and renew the certificate when needed.

With these steps, your Flask app should be production-ready with Nginx acting as a reverse proxy and handling SSL/TLS for secure communication. Note that this guide assumes you are using a Linux-based server (e.g., Ubuntu) and have root or sudo privileges.
