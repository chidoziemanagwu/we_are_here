import openai
import json
import requests
import re
from django.conf import settings
from bs4 import BeautifulSoup
from urllib.parse import quote_plus

class AIAssistant:
    def __init__(self):
        self.client = openai.OpenAI(api_key=settings.OPENAI_API_KEY)
        self.history = []
        self.emergency_keywords = [
            "suicide", "kill myself", "want to die", "end my life",
            "domestic violence", "being beaten", "attacked", "emergency",
            "heart attack", "can't breathe", "bleeding badly"
        ]

    def is_emergency(self, message):
        """Check if message contains emergency keywords"""
        message_lower = message.lower()
        for keyword in self.emergency_keywords:
            if keyword in message_lower:
                return True
        return False

    def get_response(self, user_message, user_location=None):
        # Check for emergency first
        if self.is_emergency(user_message):
            return {
                "response": "I notice this may be an emergency situation. Would you like me to connect you with immediate help?",
                "is_emergency": True,
                "emergency_type": self._classify_emergency(user_message)
            }

        # Add to conversation history
        self.history.append({"role": "user", "content": user_message})

        # Check if the user is explicitly asking for a list
        is_list_request = any(term in user_message.lower() for term in
                            ["list", "show me", "give me a list", "show a list"])

        # First, perform a web search to get relevant information
        search_results = self._perform_WebSearch(user_message, user_location)

        # Prepare messages for ChatGPT
        messages = [
            {"role": "system", "content": self._create_system_prompt(user_location, search_results, is_list_request)}
        ]

        # Add conversation history (last 5 messages)
        if len(self.history) > 0:
            for entry in self.history[-5:]:
                messages.append({"role": entry["role"], "content": entry["content"]})

        try:
            # Get ChatGPT response
            response = self.client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=messages,
                temperature=0.7
            )

            # Get the response text
            response_text = response.choices[0].message.content

            # Extract services, links, and contact info from the search results
            nearby_services = self._extract_services_from_search(search_results)
            useful_links = self._extract_links_from_search(search_results)
            contact_info = self._extract_contact_info_from_search(search_results)

            # Format response with better bullet points if this is a list request
            if is_list_request and nearby_services:
                # Create a cleaner introduction
                intro = "<p>Here are some services that might help you:</p>\n"

                # Format list with proper bullet points
                formatted_list = "<ul class='list-disc pl-5 space-y-2 mt-2'>\n"
                for service in nearby_services:
                    formatted_list += f"<li><strong>{service['name']}</strong>"

                    # Create a nested list for details instead of separate paragraphs
                    details = []
                    if service.get('address'):
                        details.append(f"Address: {service['address']}")
                    if service.get('phone'):
                        details.append(f"Phone: {service['phone']}")
                    if service.get('website'):
                        details.append(f"Website: <a href='{service['website']}' class='text-blue-600 hover:underline' target='_blank'>{service['name']}</a>")

                    if details:
                        formatted_list += "\n<ul class='list-none pl-4 mt-1 text-sm text-gray-600'>\n"
                        for detail in details:
                            formatted_list += f"<li>{detail}</li>\n"
                        formatted_list += "</ul>\n"

                    formatted_list += "</li>\n"
                formatted_list += "</ul>"

                # Add a concise outro
                outro = "<p>Feel free to ask about any of these services.</p>"
                response_text = intro + formatted_list + outro

            # Add to history
            self.history.append({"role": "assistant", "content": response_text})

            # Create a structured response
            structured_response = {
                "response": response_text,
                "identified_needs": self._extract_needs(response_text, user_message),
                "suggested_service_types": self._extract_service_types(response_text)
            }

            # Add the extracted information if available
            if nearby_services:
                structured_response["nearby_services"] = nearby_services
            if useful_links:
                structured_response["useful_links"] = useful_links
            if contact_info:
                structured_response["contact_info"] = contact_info

            return structured_response

        except Exception as e:
            print(f"Error getting response: {e}")
            fallback_response = {
                "response": f"I understand you're asking about: {user_message}. How can I help you find services?",
                "identified_needs": ["assistance"],
                "suggested_service_types": ["General Support"]
            }
            return fallback_response



    def _perform_WebSearch(self, query, location=None):
        """Perform a web search to find relevant information"""
        try:
            # Add location context if available
            if location:
                # Check if location is coordinates or text
                if isinstance(location, tuple) and len(location) == 2:
                    # It's coordinates (lat, lng)
                    lat, lng = location
                    search_query = f"{query} near {lat},{lng}"
                else:
                    # It's a text location
                    search_query = f"{query} near {location}"
            else:
                search_query = query

            # Add service-specific terms to improve results
            if "therapist" in query.lower() or "therapy" in query.lower() or "counseling" in query.lower():
                search_query += " therapist contact information address phone"
            elif "shelter" in query.lower() or "housing" in query.lower():
                search_query += " shelter housing services contact address"
            elif "food" in query.lower() or "hungry" in query.lower():
                search_query += " food bank meal service contact address"
            elif "job" in query.lower() or "employment" in query.lower() or "work" in query.lower():
                search_query += " job center employment services contact address"

            # Use a search API or scrape search results
            # For demonstration, we'll use a simple requests approach
            # In production, you should use a proper search API
            encoded_query = quote_plus(search_query)
            url = f"https://www.google.com/search?q={encoded_query}"

            headers = {
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
            }

            response = requests.get(url, headers=headers)

            if response.status_code == 200:
                # Parse the HTML content
                soup = BeautifulSoup(response.text, 'html.parser')

                # Extract search results
                results = []

                # Get all search result divs
                search_divs = soup.find_all('div', class_='g')

                for div in search_divs[:5]:  # Limit to first 5 results
                    title_elem = div.find('h3')
                    link_elem = div.find('a')
                    snippet_elem = div.find('div', class_='VwiC3b')

                    if title_elem and link_elem and snippet_elem:
                        title = title_elem.text
                        link = link_elem.get('href')
                        if link.startswith('/url?q='):
                            link = link.split('/url?q=')[1].split('&')[0]
                        snippet = snippet_elem.text

                        results.append({
                            "title": title,
                            "link": link,
                            "snippet": snippet
                        })

                return results

            return []

        except Exception as e:
            print(f"Error performing web search: {e}")
            return []


    def _extract_potential_list_items(self, text):
        """Extract potential list items from text for better formatting"""
        items = []

        # Look for patterns that might indicate service listings
        lines = text.split('\n')
        current_item = None

        for line in lines:
            line = line.strip()
            if not line:
                continue

            # Check for service name patterns (capitalized words, followed by details)
            if re.match(r'^[A-Z][A-Za-z\s\-]+', line) and not line.endswith(':'):
                if current_item:
                    items.append(current_item)
                current_item = {'name': line}

            # Check for address patterns
            elif current_item and ('address' in line.lower() or 'located at' in line.lower()):
                address_match = re.search(r'(?:address|located at)[:\s]+(.*)', line.lower())
                if address_match:
                    current_item['address'] = address_match.group(1).strip()

            # Check for phone patterns
            elif current_item and ('phone' in line.lower() or 'call' in line.lower() or 'contact' in line.lower()):
                phone_match = re.search(r'(?:phone|call|contact)[:\s]+([\d\s\(\)\-\+]+)', line.lower())
                if phone_match:
                    current_item['phone'] = phone_match.group(1).strip()

            # Check for website patterns
            elif current_item and ('website' in line.lower() or 'visit' in line.lower() or 'www' in line.lower() or 'http' in line.lower()):
                website_match = re.search(r'(?:website|visit)[:\s]+((?:https?://)?[\w\.-]+\.[a-z]{2,}(?:/\S*)?)', line.lower())
                if website_match:
                    current_item['website'] = website_match.group(1).strip()

        # Add the last item if it exists
        if current_item:
            items.append(current_item)

        return items

    def _extract_services_from_search(self, search_results):
        """Extract service information from search results with improved formatting"""
        services = []

        for i, result in enumerate(search_results):
            # Try to extract address, phone, and other details from the snippet
            snippet = result.get("snippet", "")
            title = result.get("title", "")
            link = result.get("link", "")

            # Simple heuristic to identify service listings
            if any(term in snippet.lower() for term in ["address", "location", "street", "avenue", "road", "phone", "contact"]):
                # Extract phone number (simple pattern)
                phone = None
                phone_patterns = [
                    r'\(?\d{3}\)?[-.\s]?\d{3}[-.\s]?\d{4}',  # (123) 456-7890 or 123-456-7890
                    r'\d{5}\s\d{6}',  # UK format: 01234 567890
                    r'\+\d{1,3}\s\d{3,}',  # International: +1 123456789
                ]

                for pattern in phone_patterns:
                    phone_match = re.search(pattern, snippet)
                    if phone_match:
                        phone = phone_match.group(0)
                        break

                # Extract address (simplified approach)
                address = None
                address_indicators = ["located at", "address:", "address is", "find us at"]
                for indicator in address_indicators:
                    if indicator in snippet.lower():
                        address_start = snippet.lower().find(indicator) + len(indicator)
                        address_end = min(
                            [snippet.find(". ", address_start) if snippet.find(". ", address_start) != -1 else len(snippet),
                            snippet.find("\n", address_start) if snippet.find("\n", address_start) != -1 else len(snippet)]
                        )
                        address = snippet[address_start:address_end].strip()
                        break

                # Clean up the address format
                if address:
                    # Remove common prefixes
                    for prefix in ["located at", "address:", "address is", "find us at"]:
                        if address.lower().startswith(prefix):
                            address = address[len(prefix):].strip()

                    # Capitalize first letter of each word in address
                    address = ' '.join(word.capitalize() for word in address.split())

                # Clean up phone number format
                if phone:
                    # Ensure consistent phone format
                    phone = re.sub(r'[^\d\+\-\(\)\s]', '', phone)

                services.append({
                    'id': i + 1,
                    'name': title,
                    'category': self._categorize_service(title, snippet),
                    'address': address or "Contact for address",
                    'phone': phone,
                    'website': link,
                    'hours': self._extract_hours(snippet),
                    'distance': "Nearby"
                })

        return services


    def _extract_links_from_search(self, search_results):
        """Extract useful links from search results"""
        links = []

        for result in search_results:
            title = result.get("title", "")
            link = result.get("link", "")

            if link and title:
                links.append({
                    "name": title,
                    "url": link
                })

        return links[:3]  # Limit to 3 links

    def _extract_contact_info_from_search(self, search_results):
        """Extract contact information from search results"""
        contacts = []

        for i, result in enumerate(search_results):
            snippet = result.get("snippet", "")
            title = result.get("title", "")

            # Simple heuristic to identify contact information
            if any(term in snippet.lower() for term in ["contact", "phone", "call", "helpline"]):
                # Extract phone number (simple pattern)
                phone = None
                phone_match = re.search(r'\(?\d{3}\)?[-.\s]?\d{3}[-.\s]?\d{4}', snippet)
                if phone_match:
                    phone = phone_match.group(0)

                if phone:
                    contacts.append({
                        "name": title,
                        "phone": phone
                    })

        return contacts

    def _categorize_service(self, title, snippet):
        """Categorize the service based on title and snippet"""
        title_and_snippet = (title + " " + snippet).lower()

        categories = {
            "Therapy": ["therapist", "therapy", "counseling", "mental health", "psychologist"],
            "Shelter": ["shelter", "housing", "homeless", "accommodation"],
            "Food Bank": ["food bank", "food pantry", "meal", "hungry"],
            "Medical": ["medical", "health center", "clinic", "hospital", "doctor"],
            "Legal Aid": ["legal", "lawyer", "attorney", "law firm"],
            "Crisis Support": ["crisis", "hotline", "helpline", "suicide prevention"],
            "Employment": ["job", "employment", "career", "work"]
        }

        for category, keywords in categories.items():
            if any(keyword in title_and_snippet for keyword in keywords):
                return category

        return "Support Service"

    def _extract_hours(self, snippet):
        """Extract operating hours from snippet"""
        hours_indicators = ["hours:", "open", "available", "operating hours"]
        for indicator in hours_indicators:
            if indicator in snippet.lower():
                # Simple extraction - get the sentence containing hours
                start_idx = snippet.lower().find(indicator)
                end_idx = snippet.find(".", start_idx)
                if end_idx == -1:
                    end_idx = len(snippet)

                hours_text = snippet[start_idx:end_idx + 1].strip()
                return hours_text

        return None

    def _create_system_prompt(self, user_location, search_results, is_list_request=False):
        # Create detailed prompt for ChatGPT
        location_info = ""
        if user_location:
            if isinstance(user_location, tuple) and len(user_location) == 2:
                location_info = f"The user's current location coordinates are: {user_location}"
            else:
                location_info = f"The user is looking for services near: {user_location}"
        else:
            location_info = "The user has not shared their location."
        # Add search results to the prompt
        search_info = "I found the following information that might be helpful:\n\n"
        for i, result in enumerate(search_results):
            search_info += f"{i+1}. {result.get('title', 'No title')}\n"
            search_info += f"   {result.get('snippet', 'No description')}\n"
            search_info += f"   Link: {result.get('link', 'No link')}\n\n"

        # Add formatting instructions based on request type
        formatting_instructions = ""
        if is_list_request:
            formatting_instructions = """
            The user is asking for a list. Format your response as a numbered list with clear headings and structured information.
            For each service or resource mentioned:
            1. Start with a numbered item and the name in bold (e.g., "1. **Service Name**")
            2. Include address, phone, and website on separate lines with clear labels
            3. Use bullet points or dashes for details
            4. Separate each list item with a blank line
            """

        system_prompt = f"""
        You are a compassionate AI assistant for "We Are Here," an app that helps people find social services.

        {location_info}

        {search_info}

        {formatting_instructions}

        Your role is to:
        1. Understand the user's needs and respond with empathy and practical information
        2. Provide specific, actionable advice about social services that might help them
        3. Be warm, non-judgmental, and supportive in your tone
        4. If they mention a location, reference services in that area
        5. If they don't mention a location but we have their coordinates, refer to "services near you"
        6. Use the search results I've provided to give specific information about services
        7. Include specific addresses, phone numbers, and websites when available

        Important guidelines:
        - Focus on being helpful rather than just sympathetic
        - Suggest specific types of services when appropriate (shelters, food banks, etc.)
        - For emergency situations, prioritize immediate help resources
        - Be concise but thorough
        - When you mention a service, include its contact information and address if available

        Remember that users may be in vulnerable situations, so respond with sensitivity and respect.
        """

        return system_prompt

    def _classify_emergency(self, message):
        message_lower = message.lower()
        if any(kw in message_lower for kw in ["suicide", "kill myself", "want to die"]):
            return "mental_health_crisis"
        elif any(kw in message_lower for kw in ["domestic violence", "being beaten", "attacked"]):
            return "violence"
        else:
            return "general_emergency"

    def _extract_needs(self, response_text, user_message):
        """Extract likely needs from the response and user message"""
        needs = []

        # Common needs to check for
        need_keywords = {
            "shelter": ["shelter", "housing", "homeless", "place to stay", "sleep"],
            "food": ["food", "hungry", "meal", "eat"],
            "medical": ["medical", "health", "doctor", "sick", "injury", "medicine"],
            "mental health": ["mental health", "depression", "anxiety", "counseling", "therapy"],
            "employment": ["job", "work", "employment", "career", "income"],
            "legal": ["legal", "lawyer", "court", "rights", "law"],
            "transportation": ["transport", "bus", "ride", "car", "travel"]
        }

        # Check both the user message and response
        combined_text = (user_message + " " + response_text).lower()

        for need, keywords in need_keywords.items():
            if any(keyword in combined_text for keyword in keywords):
                needs.append(need)

        return needs if needs else ["assistance"]

    def _extract_service_types(self, response_text):
        """Extract service types from the response"""
        service_types = []

        # Common service types to check for
        service_keywords = {
            "Shelter": ["shelter", "housing", "accommodation"],
            "Food Bank": ["food bank", "food pantry", "meal service"],
            "Medical Clinic": ["clinic", "healthcare", "medical center", "hospital"],
            "Mental Health Services": ["counseling", "therapy", "mental health"],
            "Employment Services": ["job center", "employment office", "career services"],
            "Legal Aid": ["legal aid", "legal services", "lawyer"],
            "Transportation Services": ["transportation", "transit", "bus service"]
        }

        response_lower = response_text.lower()

        for service, keywords in service_keywords.items():
            if any(keyword in response_lower for keyword in keywords):
                service_types.append(service)

        return service_types if service_types else ["General Support"]