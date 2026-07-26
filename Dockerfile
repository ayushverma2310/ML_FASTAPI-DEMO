#use base Python 3.11 base-image 
FROM python:3.11-slim

#Set working directory 

WORKDIR /app

#copy the requiremens and install dependencies


COPY requirements.txt

RUN pip install --no-cache-dir -r requiremens.txt

COPY . .


#expose the application port

EXPOSE 8000
    
#command to start the fastapi application
CMD ["uvicorn","app:app","--host","0.0.0.0","--port","8000"]