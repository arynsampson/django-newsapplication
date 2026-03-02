# Django News Application Project

## About
This is a Django-based news application with role-based functionality where users can create articles, newsletters, and subscribe to journalists or publishers. Articles are created by Journalists.
Journalists and Editors can create newsletters and manage articles and newsletters, while Readers can browse articles and newsletters and subscribe to Journalists and Publishers to get email notifications about newly published articles.  

The application is run using docker. 

The project uses Django ORM, Django forms, built-in authentication and more.

This project also contains a minimal REST API that use token based authentication with JWT to get data related to articles and newsletters, creating new stores and getting subsriber articles.


**Technologies:** Python 3, Django, Django Templates, Django Rest Framework, MariaDB, HTML/CSS, Docker, Sphinx documentation

---
## Features
- Django Authentication System
- BasicAuthentication (DRF)
- Custom role-based permissions:
- Reader
- Journalist
- Editor
- Publisher
- Custom decorators (e.g. publisher_required)
- Object-level permission checks
- Unit tests for the core application as well as the API
---

## Setup Instructions  

### Prerequisites
- Python 3.10+  
- Django 
- MariaDB installed and setup
- Docker installed and setup

### Steps
1. Clone the repository:
git clone https://github.com/arynsampson/django-newsapplication

2. cd into django-newsapplication directory

3. Create a .env file in the project root directory (See .env.example): 
``` 
    SECRET_KEY=secret_key  (generate a key using the django shell)
    DB_ENGINE=db_engine  (django.db.backends.mysql)
    DB_NAME=dbname  
    DB_USER=user  
    DB_PASSWORD=password  
    DB_HOST=host  (localhost)
    DB_PORT=port  (3306)
    EMAIL_HOST_USER=gmail_app_address (Create a GMAIL APP (mail application for GMAIL) - REQUIRED FOR EMAIL NOTIFICATIONS)  
    EMAIL_HOST_PASSWORD=gmail_app_password  
    DEFAULT_FROM_EMAIL=your_gmail_app_email_address (USED FOR EMAIL SENDING FROM SIGNAL)
```

4. Run docker-compose up --build  

5. Go to http://127.0.0.1:8000/ in your browser

---

## Tests
To run the tests from inside the container, go to the project root:  
1. Run docker ps and get the name of the container for the project
2. Run docker exec -it <container_name> bash
3. Tests can be run with:  
python manage.py test  
or  
python manage.py test <app_name> (individual app tests)

---

## API Endpoints
Uses JWT tokens for authentication
Uses must first get an access token and then add it in the authorization tab under Bearer token in Postman
| Endpoint | Method | Description | Access | Data |
| --- | --- | --- | --- | --- |
| /api/articles/ | GET | List of all published articles | Authenticated user | None |
| /api/articles/subscribed/ | GET | List of articles from subscriptions | Authenticated Reader | body - reader.id |
| /api/article/:id/ | GET | Retrieve a single article | Authenticated user | param - article.id |
| /api/article/create/ | POST | Create a new article | Authenticated Journalist | body - {"title": "", "content": "", author: Journalist.id} |
| /api/article/:id/delete/ | DELETE | Delete an article | Authenticated Journalist or Editor | param - article.id |
| /api/article/:id/update | PUT | Update an existing article | Authenticated Journalist or Editor | param - article.id and response body data |
| /api/token/ | POST | Get an access token | Public | body - {"username": "", "password": ""} |

  
### Email Notifications

The following API actions send email notifications if EMAIL_HOST_USER is configured:  
- Store creation  
- Product added to store  

If email configuration is missing:  
- The system logs a warning  
- The API request still succeeds

---

  
## Sphinx documentation  
Go to docs/build/html/ and open te index.html file in the browser to access the document for the project
