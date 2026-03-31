@echo off
echo Stopping old container if it exists...
docker stop pm_container
docker rm pm_container

echo Building Docker image...
docker build -t pm-app .

echo Running Docker container...
docker run -d -p 8000:8000 -v pm_data:/app/data --env-file .env --name pm_container pm-app

echo Application started! Validating health...
timeout /t 3 /nobreak >nul
curl http://localhost:8000/api/hello
echo.
