# Dictionary of hardcoded service data for common queries
HARDCODED_SERVICES = {
    "food_bradford": {
        "nearby_services": [
            {
                "id": 1,
                "name": "Bradford Metropolitan Food Bank",
                "category": "Food Bank",
                "address": "Unit 13, Clifton Business Centre, Clifton Road, Bradford, BD8 7BB",
                "phone": "01274 292256",
                "website": "https://bradfordfoodbank.com",
                "hours": "Mon-Fri: 9am-4pm",
                "distance": "Nearby"
            },
            {
                "id": 2,
                "name": "Bradford Central Foodbank",
                "category": "Food Bank",
                "address": "St. Mary's Church, Barkerend Road, Bradford, BD3 9DF",
                "phone": "01274 734314",
                "website": "https://bradford.foodbank.org.uk",
                "hours": "Mon, Wed, Fri: 10am-2pm",
                "distance": "Nearby"
            },
            {
                "id": 3,
                "name": "Bradford North Foodbank",
                "category": "Food Bank",
                "address": "Greenfield Community Centre, Greenfield Lane, Bradford, BD10 9LD",
                "phone": "01274 292256",
                "website": "https://bradfordfoodbank.com/locations",
                "hours": "Tue, Thu: 11am-1pm",
                "distance": "Nearby"
            }
        ],
        "useful_links": [
            {"name": "Bradford Council Emergency Food Support", "url": "https://www.bradford.gov.uk/benefits/emergency-support/emergency-food-support/"},
            {"name": "Trussell Trust Food Bank Finder", "url": "https://www.trusselltrust.org/get-help/find-a-foodbank/"}
        ],
        "contact_info": [
            {"name": "Bradford Council Helpline", "phone": "01274 431000"},
            {"name": "Citizens Advice Bradford", "phone": "0344 245 1282"}
        ]
    },
    "shelter_bradford": {
        "nearby_services": [
            {
                "id": 4,
                "name": "Bradford Cyrenians",
                "category": "Shelter",
                "address": "24 Mornington Villas, Bradford, BD8 7HB",
                "phone": "01274 481039",
                "website": "https://www.bradfordcyrenians.org.uk",
                "hours": "24/7 Emergency Accommodation",
                "distance": "Nearby"
            },
            {
                "id": 5,
                "name": "Horton Housing Association",
                "category": "Housing Support",
                "address": "Chartford House, 54 Little Horton Lane, Bradford, BD5 0BS",
                "phone": "01274 370689",
                "website": "https://www.hortonhousing.co.uk",
                "hours": "Mon-Fri: 9am-5pm",
                "distance": "Nearby"
            }
        ],
        "useful_links": [
            {"name": "Bradford Housing Options", "url": "https://www.bradford.gov.uk/housing/help-with-housing-and-homelessness/help-with-homelessness/"},
            {"name": "Shelter England", "url": "https://england.shelter.org.uk/"}
        ],
        "contact_info": [
            {"name": "Bradford Housing Options", "phone": "01274 435999"},
            {"name": "National Shelter Helpline", "phone": "0808 800 4444"}
        ]
    }
}

def get_hardcoded_response(message):
    """Check if we have hardcoded service data for this message"""
    message_lower = message.lower()

    # Check for food banks in Bradford
    if ("food" in message_lower or "hungry" in message_lower or "food bank" in message_lower) and "bradford" in message_lower:
        return HARDCODED_SERVICES["food_bradford"]

    # Check for shelters in Bradford
    if ("shelter" in message_lower or "housing" in message_lower or "homeless" in message_lower) and "bradford" in message_lower:
        return HARDCODED_SERVICES["shelter_bradford"]

    # No hardcoded data found
    return None