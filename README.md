# KONNECT

KONNECT is a dynamic real-time communication platform that brings users together through seamless messaging, audio, and video calling. 

Whether you're starting a private conversation or managing a group session, KONNECT provides a range of volatile rooms.

## Features

- User registration and verification using an OTP system.
- Real-Time Text Chat 
- Dedicated chat rooms for two and more than two people with live user presence tracking.
- Voice and video calling featured included
- Share images, audio, and videos dynamically within the chat interface.

## Tech Stack

- Python 3 (language)
- Django (framework)
- Daphne (ASGI server)
- Websocket (core tech for real-time communicatio)
- Django Channel, Consumers (websocket handling at backend)
- Redis (message broker for channels) 
- HTML, CSS and JS (frontend logic)
- PostgreSQL (database)
- Brevo (transactional Email)
- Render (deployment)
- WebRTC (audio and video calling)

## Setup Instructions

1. **Clone the repository**

    ```bash
    git clone https://github.com/Apratimmm/konnect.git
    cd konnect
    ```
    
2. **Create and activate a virtual environment**

    ```bash
    python3 -m venv .venv
    source .venv/bin/activate
    ```

3. **Install dependencies**

    ```bash
    pip install -r requirements.txt```
    
4. **Create your .env file**

    Create a `.env` file in the root folder and add your credentials:
    ```bash
    DEBUG=True
    SECRET_KEY=your_django_secret_key
    
    # LiveKit Credentials
    PROJECT_ID=your_project_id
    SIP_URI=your_livekit_sip_uri
    LIVEKIT_URL=your_livekit_wss_url
    LIVEKIT_API_KEY=your_livekit_api_key
    LIVEKIT_API_SECRET=your_livekit_api_secret
    
    # Brevo SMTP Credentials
    EMAIL_USER=your_brevo_email
    EMAIL_PASSWORD=your_brevo_smtp_key
    
    # Production Variables (Optional for Local)
    DB_URL=your_database_url
    REDIS_URL=your_redis_url
    ```

5. **Run database migrations & collect static files**

    ```bash
    python manage.py collectstatic --noinput
    python manage.py migrate
    ```

6. **Run the server**

    Standard `runserver` handles ASGI environments natively in Django 3.0+, but for production-level testing, you may want to use Daphne.
    
    ```bash
    # Standard development server
    python manage.py runserver
    
    # Or via Daphne (ASGI)
    daphne -b 127.0.0.1 -p 8000 main.asgi:application
    ```
