@echo off
echo ===================================================
echo   FoodRescue - Celery Beat Scheduler (Requires Redis)
echo ===================================================
set PYTHONPATH=backend
backend\venv\Scripts\celery.exe -A app.tasks.celery_app.celery_app beat --loglevel=info
pause
