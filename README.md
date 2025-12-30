# AI-Powered Civic Reporting Platform

A full-stack application that allows users to upload photos of civic issues, get AI-generated social media posts, and earn credits for their contributions.

## Features

📸 Upload photos of civic issues
🤖 AI-powered analysis using Gemini Flash 1.5
📱 Generate Instagram/Twitter-ready social media posts
🏆 Credit system (100 points per post)
Simple and minimalist UI

## Tech Stack

### Backend
- Python 3.x
- Flask (REST API)
- SQLAlchemy (Database ORM)
- Google Gemini AI (Image Analysis)
- Cloudinary (Image Storage)

### Frontend
- React 18
- Axios (HTTP Client)
- Modern CSS with gradients

## Setup Instructions

### Backend Setup

1. Install Python dependencies:
```bash
pip install -r "requirements (1).txt"
```

2. Create a `.env` file in the root directory:
```env
GEMINI_API_KEY=your_gemini_api_key_here
CLOUDINARY_CLOUD_NAME=your_cloud_name
CLOUDINARY_API_KEY=your_cloudinary_key
CLOUDINARY_API_SECRET=your_cloudinary_secret
AYRSHARE_API_KEY=your_ayrshare_key
DATABASE_URL=sqlite:///./hackathon.db
```

3. Run the Flask server:
```bash
python app.py
```

The backend will run on `http://localhost:5000`

### Frontend Setup

1. Navigate to the frontend directory:
```bash
cd frontend
```

2. Install dependencies:
```bash
npm install
```

3. Start the development server:
```bash
npm start
```

The frontend will run on `http://localhost:3000`

## API Endpoints

- `POST /api/user/create` - Create a new user
- `GET /api/user/<user_id>` - Get user information
- `POST /api/upload` - Upload image and analyze
- `GET /api/reports/<user_id>` - Get user reports
- `POST /api/report/<report_id>/post` - Mark report as posted

## Project Structure

```
.
├── app.py                 # Flask API server
├── database.py            # Database models and functions
├── ai_helper.py           # Gemini AI integration
├── storage.py             # Cloudinary integration
├── config.py              # Configuration
├── social.py              # Social media posting
├── requirements (1).txt   # Python dependencies
├── frontend/              # React frontend
│   ├── src/
│   │   ├── App.js         # Main React component
│   │   ├── App.css        # Styles
│   │   └── index.js       # Entry point
│   └── package.json       # Node dependencies
└── README.md
```

## Usage

1. Start both backend and frontend servers
2. Open `http://localhost:3000` in your browser
3. Upload a photo of a civic issue
4. Add optional tags
5. Click "Generate Social Media Post"
6. Copy the generated caption and post to social media
7. Mark as posted to earn 100 credits!

## Credits System

- Users earn 100 credits when they mark a report as posted
- Credits are displayed in the header
- Credits are stored in the database and persist across sessions

## Notes

- Make sure to add your Gemini API key to the `.env` file
- The app uses Cloudinary for image storage
- Database is SQLite (can be changed in config)

