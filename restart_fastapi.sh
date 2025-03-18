#!/bin/bash

echo "Reloading systemd daemon..."
sudo systemctl daemon-reload

echo "Restarting FastAPI service..."
sudo systemctl restart fastapi.service

echo "Checking FastAPI service status..."
sudo systemctl status fastapi.service
