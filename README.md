# caso03_talma_backend
Backend de desarrollo de sistema de extracción y anonimización de datos a partir de imágenes.

# Comandos para ejecutar el proyecto (cada uno en otro cmd)
1. docker run --name redis-talma -p 6379:6379 -d redis
2. (activate) : celery -A app.core.celery_app worker --loglevel=info --pool=solo
3. uvicorn main:app --reload