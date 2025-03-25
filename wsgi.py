from app import app

# For Vercel serverless deployment
app.debug = False  # Disable debug mode in production

if __name__ == "__main__":
    app.run() 