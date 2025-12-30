from flask import Flask, request, jsonify
from flask_cors import CORS
from werkzeug.utils import secure_filename
import os
from database import init_database, create_user, get_user, create_report, get_user_reports, update_report_ai_data, update_user_credits, mark_report_posted
from storage import upload_image_to_cloud
from ai_helper import analyze_image, generate_caption
from social import post_to_social_media, get_supported_platforms
import uuid

app = Flask(__name__)
CORS(app)

# Initialize database
init_database()

# Configuration
UPLOAD_FOLDER = 'uploads'
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif', 'webp'}
MAX_FILE_SIZE = 16 * 1024 * 1024  # 16MB

os.makedirs(UPLOAD_FOLDER, exist_ok=True)

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route('/api/health', methods=['GET'])
def health():
    return jsonify({"status": "ok"})

@app.route('/api/user/create', methods=['POST'])
def create_user_endpoint():
    """Create a new user"""
    try:
        data = request.json
        name = data.get('name', 'Anonymous User')
        email = data.get('email', f'user_{uuid.uuid4().hex[:8]}@civic.app')
        
        user = create_user(name, email)
        return jsonify({
            "success": True,
            "user": {
                "id": user.id,
                "name": user.name,
                "email": user.email,
                "credits": user.credits
            }
        }), 201
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 400

@app.route('/api/user/<int:user_id>', methods=['GET'])
def get_user_endpoint(user_id):
    """Get user information"""
    try:
        user = get_user(user_id)
        if not user:
            return jsonify({"success": False, "error": "User not found"}), 404
        
        return jsonify({
            "success": True,
            "user": {
                "id": user.id,
                "name": user.name,
                "email": user.email,
                "credits": user.credits
            }
        })
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 400

@app.route('/api/upload', methods=['POST'])
def upload_image():
    """Upload image to cloud storage"""
    try:
        if 'image' not in request.files:
            return jsonify({"success": False, "error": "No image file provided"}), 400
        
        file = request.files['image']
        user_id = request.form.get('user_id', type=int)
        
        if file.filename == '':
            return jsonify({"success": False, "error": "No file selected"}), 400
        
        if not allowed_file(file.filename):
            return jsonify({"success": False, "error": "Invalid file type"}), 400
        
        if not user_id:
            return jsonify({"success": False, "error": "User ID required"}), 400
        
        # Save file temporarily
        filename = secure_filename(file.filename)
        filepath = os.path.join(UPLOAD_FOLDER, filename)
        file.save(filepath)
        
        try:
            # Upload to Cloudinary
            image_url = upload_image_to_cloud(filepath)
            
            # Create report in database (without AI data yet)
            report = create_report(
                user_id=user_id,
                image_url=image_url,
                category=None,
                authority=None,
                caption=None
            )
            
            return jsonify({
                "success": True,
                "report": {
                    "id": report.id,
                    "image_url": image_url
                }
            }), 201
            
        finally:
            # Clean up temporary file
            if os.path.exists(filepath):
                os.remove(filepath)
                
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500

@app.route('/api/analyze', methods=['POST'])
def analyze_report():
    """Analyze an uploaded image with tags and context"""
    try:
        data = request.json
        report_id = data.get('report_id')
        image_url = data.get('image_url')
        tags = data.get('tags', '')
        context = data.get('context', '')
        
        if not image_url:
            return jsonify({"success": False, "error": "Image URL required"}), 400
        
        # Analyze image with AI (including tags and context)
        ai_result = analyze_image(image_url, tags=tags, context=context)
        
        # Update report with analysis results
        update_report_ai_data(
            report_id,
            ai_result.get('problem', ''),
            ai_result.get('authority', ''),
            None  # Caption will be generated separately
        )
        
        return jsonify({
            "success": True,
            "analysis": {
                "problem": ai_result.get('problem', ''),
                "authority": ai_result.get('authority', '')
            }
        }), 200
                
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500

@app.route('/api/generate-caption', methods=['POST'])
def generate_caption_endpoint():
    """Generate social media caption for analyzed report"""
    try:
        data = request.json
        report_id = data.get('report_id')
        image_url = data.get('image_url')
        tags = data.get('tags', '')
        context = data.get('context', '')
        problem = data.get('problem', '')
        
        if not image_url:
            return jsonify({"success": False, "error": "Image URL required"}), 400
        
        # Generate caption
        caption = generate_caption(image_url, tags=tags, context=context, problem=problem)
        
        # Update report with caption
        from database import get_db_session, Report
        db = get_db_session()
        try:
            report = db.query(Report).filter(Report.id == report_id).first()
            if report:
                report.caption = caption
                db.commit()
            else:
                return jsonify({"success": False, "error": "Report not found"}), 404
        finally:
            db.close()
        
        return jsonify({
            "success": True,
            "caption": caption
        }), 200
                
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500

@app.route('/api/reports/<int:user_id>', methods=['GET'])
def get_reports(user_id):
    """Get all reports for a user"""
    try:
        reports = get_user_reports(user_id)
        return jsonify({
            "success": True,
            "reports": [
                {
                    "id": r.id,
                    "image_url": r.image_url,
                    "category": r.category,
                    "authority": r.authority,
                    "caption": r.caption,
                    "posted": r.posted,
                    "created_at": r.created_at.isoformat() if r.created_at else None
                }
                for r in reports
            ]
        })
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 400

@app.route('/api/report/<int:report_id>/post', methods=['POST'])
def mark_posted(report_id):
    """Mark report as posted and award credits"""
    try:
        mark_report_posted(report_id)
        
        # Get report to find user_id
        from database import get_db_session, Report
        db = get_db_session()
        try:
            report = db.query(Report).filter(Report.id == report_id).first()
            if report:
                user = get_user(report.user_id)
                return jsonify({
                    "success": True,
                    "user_credits": user.credits if user else 0
                })
            else:
                return jsonify({"success": False, "error": "Report not found"}), 404
        finally:
            db.close()
            
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 400

@app.route('/api/social/platforms', methods=['GET'])
def get_platforms():
    """Get list of supported social media platforms"""
    try:
        platforms = get_supported_platforms()
        return jsonify({
            "success": True,
            "platforms": platforms
        })
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 400

@app.route('/api/report/<int:report_id>/post-to-social', methods=['POST'])
def post_to_social(report_id):
    """Post report to social media platforms"""
    try:
        data = request.json
        platforms = data.get('platforms', get_supported_platforms())
        
        # Get report details
        from database import get_db_session, Report
        db = get_db_session()
        try:
            report = db.query(Report).filter(Report.id == report_id).first()
            if not report:
                return jsonify({"success": False, "error": "Report not found"}), 404
            
            # Post to social media
            result = post_to_social_media(
                caption=report.caption or "",
                image_url=report.image_url,
                platforms=platforms
            )
            
            if result.get("status") == "success":
                # Mark as posted and award credits
                mark_report_posted(report_id)
                
                # Get updated user
                user = get_user(report.user_id)
                
                return jsonify({
                    "success": True,
                    "message": result.get("message", "Posted successfully"),
                    "post_id": result.get("post_id"),
                    "user_credits": user.credits if user else 0
                })
            else:
                return jsonify({
                    "success": False,
                    "error": result.get("message", "Failed to post to social media")
                }), 400
                
        finally:
            db.close()
            
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True, port=5000)

