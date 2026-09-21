@echo off
echo ===================================================
echo   FoodRescue - Celery Worker (Requires Redis)
echo ===================================================
set PYTHONPATH=backend
backend\venv\Scripts\celery.exe -A app.tasks.celery_app.celery_app worker --loglevel=info -P solo
pause
