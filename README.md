# IRPCS Quiz Generator

A web application for generating and managing IRPCS (International Regulations for Preventing Collisions at Sea) quizzes.

## Features

- Generate quizzes with customizable:
  - Number of questions (up to 500)
  - Difficulty levels (Easy, Medium, Hard, Extreme, Mixed)
  - Question types (Multiple Choice, Fill in the Gap, Written Answer)
- Edit questions in real-time
- Save quizzes for later use
- Download student and teacher versions
- Interactive scoring for written answers
- Visual feedback for answer correctness

## Setup

1. Clone the repository:
```bash
git clone <repository-url>
cd irpcs-quiz-generator
```

2. Create a virtual environment and activate it:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. Run the application:
```bash
python app.py
```

5. Open your browser and navigate to `http://localhost:5000`

## Project Structure

```
irpcs-quiz-generator/
├── app.py                 # Main Flask application
├── quiz_generator.py      # Quiz generation logic
├── requirements.txt       # Python dependencies
├── static/               # Static files (CSS, JS)
├── templates/           # HTML templates
│   └── index.html      # Main application template
├── quizzes/            # Directory for saved quizzes
└── README.md          # This file
```

## Deployment

### Local Deployment
1. Follow the setup instructions above
2. Run `python app.py`
3. Access the application at `http://localhost:5000`

### Production Deployment
1. Set up a production server (e.g., Ubuntu)
2. Install Python and required system packages
3. Clone the repository
4. Set up a virtual environment and install dependencies
5. Configure a production-grade WSGI server (e.g., Gunicorn)
6. Set up a reverse proxy (e.g., Nginx)
7. Configure SSL certificates
8. Set up environment variables for production

Example Gunicorn command:
```bash
gunicorn -w 4 -b 0.0.0.0:8000 app:app
```

Example Nginx configuration:
```nginx
server {
    listen 80;
    server_name your-domain.com;

    location / {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }
}
```

## Contributing

1. Fork the repository
2. Create a feature branch
3. Commit your changes
4. Push to the branch
5. Create a Pull Request

## License

This project is licensed under the MIT License - see the LICENSE file for details. 