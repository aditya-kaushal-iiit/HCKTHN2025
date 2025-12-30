import cloudinary
import cloudinary.uploader
from config import Config

cloudinary.config(
    cloud_name=Config.CLOUDINARY_CLOUD_NAME,
    api_key=Config.CLOUDINARY_API_KEY,
    api_secret=Config.CLOUDINARY_API_SECRET
)

def upload_image_to_cloud(image_file , folder = "Civic-Issues"):
    """
    Upload an image file to Cloudinary and return the public URL.
    
    Args:
        image_file: File object or file path
        folder: Cloudinary folder to organize uploads
        
    Returns:
        str: Secure public URL of uploaded image
    """

    try:
        result = cloudinary.uploader.upload(
            image_file,
            folder = folder,
            resource_type = "image"
        )

        return result.get("secure_url")
    except Exception as e:
        raise Exception(f"Failed to upload image :{str(e)}")

def delete_image_from_cloud(image_url):
    """Delete image from cloudinary"""
    try:
        public_id = image_url.split("/")[-1].split(".")[0]
        result = cloudinary.uploader.destroy(public_id)
        return result.get("result") == "OK"

    except Exception as e:
        print(f"Error deleting image: {str(e)}")
        return False