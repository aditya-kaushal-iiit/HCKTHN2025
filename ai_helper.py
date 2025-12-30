import requests
from PIL import Image
from io import BytesIO
from google import genai
from config import Config

def analyze_image(image_url: str, tags: str = "", context: str = "") -> dict:
    """Analyze image using Gemini AI and return problem, authority, and caption"""
    try:
        get_image = requests.get(image_url)
        data = get_image.content

        image = Image.open(BytesIO(data))

        api_key = Config.GEMINI_API_KEY
        if not api_key:
            raise ValueError("GEMINI_API_KEY not found in environment variables")

        client = genai.Client(api_key=api_key)

        # Build context prompt
        context_prompt = ""
        if tags:
            context_prompt += f"\nUser-provided tags: {tags}"
        if context:
            context_prompt += f"\nAdditional context: {context}"

        # Analyze problem
        problem_prompt = "tell the problem seen in image in 2 words"
        if context_prompt:
            problem_prompt += context_prompt
        
        problem = client.models.generate_content(
            model="gemini-1.5-flash", 
            contents=[image, problem_prompt]
        )

        # Analyze authority
        authority_prompt = "let a person live in india then respective to that in few words provide only the name of two authorities and their contact number to solve this problem."
        if context_prompt:
            authority_prompt += context_prompt
        
        authority = client.models.generate_content(
            model="gemini-1.5-flash", 
            contents=[image, authority_prompt]
        )

        return {
            "problem": problem.text.strip(),
            "authority": authority.text.strip()
        }
    except Exception as e:
        raise Exception(f"Error analyzing image: {str(e)}")

def generate_caption(image_url: str, tags: str = "", context: str = "", problem: str = "") -> str:
    """Generate social media caption for the analyzed image"""
    try:
        get_image = requests.get(image_url)
        data = get_image.content

        image = Image.open(BytesIO(data))

        api_key = Config.GEMINI_API_KEY
        if not api_key:
            raise ValueError("GEMINI_API_KEY not found in environment variables")

        client = genai.Client(api_key=api_key)

        # Build caption prompt with context
        caption_prompt = "only provide the caption with hashtag without giving details so that i can post on social media"
        if tags:
            caption_prompt += f"\nInclude these tags if relevant: {tags}"
        if context:
            caption_prompt += f"\nContext: {context}"
        if problem:
            caption_prompt += f"\nThe issue identified is: {problem}"
        
        caption = client.models.generate_content(
            model="gemini-1.5-flash", 
            contents=[image, caption_prompt]
        )

        return caption.text.strip()
    except Exception as e:
        raise Exception(f"Error generating caption: {str(e)}")



###extract the url of image uploaded from cloudinary and put it in place of image_url

#to check
# a  = analyze_image("url") ##dummy image
# print("problem:\n")
# print(a['problem'])
# print("\n")
# print(a['authority'])
# print("caption\n")
# print(a['caption'])




# No need

# def get_authority_contacts(authority: str) -> dict:
#     """Get contact info for authority"""
#     contacts = {
#         "municipality": {"name": "Municipal Corporation", "phone": "123-456-7890"},
#         "PWD": {"name": "Public Works Department", "phone": "123-456-7891"},
#         "water_board": {"name": "Water Board", "phone": "123-456-7892"}
#     }
#     return contacts.get(authority, {})

# no need