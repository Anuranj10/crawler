@echo off
echo Deploying Backend with Email Feature to Azure...
echo.
echo This will:
echo 1. Copy updated files to Azure VM
echo 2. Restart the backend service
echo.
pause

echo Connecting to Azure VM...
scp -i eduro-vm_key.pem backend/src/api.py azureuser@eduro.eastasia.cloudapp.azure.com:~/crawler/backend/src/
scp -i eduro-vm_key.pem backend/src/email_service.py azureuser@eduro.eastasia.cloudapp.azure.com:~/crawler/backend/src/

echo.
echo Restarting backend service...
ssh -i eduro-vm_key.pem azureuser@eduro.eastasia.cloudapp.azure.com "cd ~/crawler && docker-compose restart backend"

echo.
echo Deployment complete!
echo Backend is now running with email notifications.
echo.
pause
