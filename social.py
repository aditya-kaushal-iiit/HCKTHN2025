from config import Config
from storage import upload_image_to_cloud
from ai_helper import analyze_image

url = upload_image_to_cloud("waste.png")

# get the url of uploaded image in cloudinary and use it in analyze image("url")


# remove comment only for testing purpose
a = analyze_image(url)
b = a['caption']

import requests

def post_to_social_media(caption: str, image_url: str, platforms: list = None):
    """
    Post to social media platforms using Ayrshare API
    
    Args:
        caption: The post caption/text
        image_url: URL of the image to post
        platforms: List of platforms to post to (default: all supported)
        
    Returns:
        dict: Response with status and post_id if successful
    """
    if platforms is None:
        platforms = get_supported_platforms()
    
    if not platforms:
        return {"status": "error", "message": "No platforms specified"}
    
    api_url = "https://api.ayrshare.com/api/post"
    headers = {
        "Authorization": f"Bearer {Config.AYRSHARE_API_KEY}",
        "Content-Type": "application/json"
    }
    
    data = {
        "post": caption,
        "platforms": platforms,
        "mediaUrls": [image_url]
    }
    
    try:
        response = requests.post(api_url, json=data, headers=headers)
        response.raise_for_status()
        result = response.json()
        
        if result.get("status") == "success":
            return {
                "status": "success",
                "post_id": result.get("id"),
                "message": f"Successfully posted to {', '.join(platforms)}"
            }
        else:
            return {
                "status": "error",
                "message": result.get("message", "Failed to post to social media")
            }
    except requests.exceptions.RequestException as e:
        return {
            "status": "error",
            "message": f"API request failed: {str(e)}"
        }
    except Exception as e:
        return {
            "status": "error",
            "message": f"Unexpected error: {str(e)}"
        }

def get_post_status(post_id: str):
    """
    Get the status of a social media post
    
    Args:
        post_id: The ID of the post to check
        
    Returns:
        dict: Post status information
    """
    api_url = f"https://api.ayrshare.com/api/post/{post_id}"
    headers = {
        "Authorization": f"Bearer {Config.AYRSHARE_API_KEY}",
        "Content-Type": "application/json"
    }
    data = {
    "post": b,
    "platforms": get_supported_platforms(),
    "mediaUrls": [url]
    }

    response = requests.post(api_url, json=data, headers=headers)
    print(response.json())

    return {"status": "posted",
            "credit": "awarded"}

def get_supported_platforms():
    return ["instagram"]
