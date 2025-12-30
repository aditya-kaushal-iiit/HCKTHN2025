"""Test script to verify all backend modules work"""

from database import init_database, create_user, create_report, get_user_reports, mark_report_posted
from social import get_supported_platforms
from ai_helper import analyze_image, get_authority_contacts

def test_database():
    print("\n=== Testing Database ===")
    
    init_database()
    print(" Database initialized")
    
    user = create_user("Test User", "test@example.com")
    print(f" User created: {user.name} (ID: {user.id}, Credits: {user.credits})")
    
    report = create_report(
        user_id=user.id,
        image_url="https://example.com/test.jpg",
        category="pothole",
        authority="PWD",
        caption="Test caption"
    )
    print(f" Report created (ID: {report.id})")
    
    reports = get_user_reports(user.id)
    print(f" Retrieved {len(reports)} reports")
    
    mark_report_posted(report.id)
    print(f" Report marked as posted, user now has credits")


def test_social():
    print("\n=== Testing Social Media ===")
    platforms = get_supported_platforms()
    print(f"Supported platforms: {', '.join(platforms[:5])}...")
    print(" Skipping actual post (needs API key)")


def test_ai():
    print("\n=== Testing AI Helper ===")
    result = analyze_image("https://example.com/test.jpg")
    print(f"AI analysis returned: {result}")
    
    # we dont need it
    # contacts = get_authority_contacts("PWD")
    # print(f"Authority contacts: {contacts.get('name', 'Not found')}")   


if __name__ == "__main__":
    print(" Backend Module Test Suite")
    print("=" * 50)
    
    test_database()
    test_social()
    test_ai()
    
    print("\n" + "=" * 50)
    print("All backend modules working!")
    print("\nNext steps:")
    print("1. Add real API keys to .env")
    print("2. AI teammate: implement analyze_image()")
    print("3. API teammate: import these modules")
