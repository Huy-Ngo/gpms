# Group Project Management System

# Deployment

## Requirements

### Python packages

These packages should be installed in a Python virtual environment.

- Quart-Trio
- HyperCorn

### Server requirements

I haven't decided on whether to deploy JSON DB as merely JSON files with IPFS
or using a JSON DBMS like RethinkDB

- NGINX
- IPFS
- RethinkDB

## Steps

### Configure NGINX file

Add following file as `/etc/nginx/sites-available/gpms`

```nginx
server {
	listen 80;
	server_name <IP address or domain name>;
	location / {
		include proxy_params;
		proxy_pass http://unix:/var/www/gpms/gpms.sock;
	}
}
```

Make a symlink to `/etc/nginx/sites-enabled/`

### Configure systemd service

```ini
[Unit]
Description=Instance to serve GPMS
After=network.target

[Service]
User=username
WorkingDirectory=/home/username/gpms
ExecStart=/home/username/gpms/venv/bin/python -m hypercorn -w 5 -k trio gpms:app

[Install]
WantedBy=multi-user.target
```

Start the service:

```bash
systemctl start gpms.service
```