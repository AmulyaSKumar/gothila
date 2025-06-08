"""
Law Library - User-friendly explanations of Indian laws for people with no legal background
"""
import google.generativeai as genai
import os
import json
import random
from dotenv import load_dotenv
load_dotenv()

class LawLibrary:
    """Comprehensive law library with user-friendly explanations"""
    
    def __init__(self):
        # Configure Gemini 2.0 Flash API
        api_key=os.getenv("GENAI_API_KEY")
        genai.configure(api_key=api_key)
        self.model = genai.GenerativeModel('gemini-2.0-flash-exp')
        
        # Load laws from JSON database
        print("Initializing LawLibrary class...")
        self.law_cards = self._load_laws_database()
        
    def _load_laws_database(self):
        """Load laws from the JSON database file"""
        try:
            print("Attempting to load laws_database.json...")
            with open('data/laws_database.json', 'r', encoding='utf-8') as f:
                laws_data = json.load(f)
            
            print(f"Successfully loaded {len(laws_data)} laws from laws_database.json")
                
            # Convert the list of laws to a dictionary with id as key
            law_cards = {}
            for law in laws_data:
                law_id = law.get('id')
                if law_id:
                    # Transform the data structure to match the expected format
                    law_cards[law_id] = {
                        'id': law_id,
                        'title': law.get('title', ''),
                        'category': law.get('category', ''),
                        'state': law.get('state', 'All India'),
                        'summary': law.get('summary', ''),
                        'description': law.get('detailed_description', ''),
                        'punishment': law.get('punishment', ''),
                        'related_sections': [law.get('act', '')],
                        'faqs': law.get('faqs', [])
                    }
            
            print(f"Converted {len(law_cards)} laws to law_cards dictionary")
            print(f"First law ID: {next(iter(law_cards.keys()), 'None')}")
            return law_cards
        except FileNotFoundError:
            print("Warning: laws_database.json file not found")
            print(f"Current working directory: {os.getcwd()}")
            return {
            # Road Safety & Traffic Laws
            'bike_accident': {
                'title': 'Bike Accident Laws',
                'category': 'Road Safety',
                'state': 'All India',
                'summary': 'What to do if you have a bike accident - your rights and responsibilities',
                'description': '''
                If you're in a bike accident, here's what you need to know:
                
                **Immediate Steps:**
                - Call police (dial 100) if there are injuries or major damage
                - Take photos of the accident scene and vehicles
                - Get contact details from other people involved
                - Don't admit fault at the scene
                
                **Your Rights:**
                - Right to medical treatment (emergency treatment cannot be denied)
                - Right to file an insurance claim
                - Right to compensation if the other person was at fault
                
                **Legal Requirements:**
                - You must have valid driving license and bike registration
                - Third-party insurance is mandatory by law
                - Report to police within 24 hours for serious accidents
                ''',
                'punishment': 'Driving without license: ₹5,000 fine. No insurance: ₹2,000 fine + vehicle seizure',
                'related_sections': ['Motor Vehicle Act 1988', 'IPC Section 279 (Rash Driving)', 'IPC Section 337/338 (Causing Hurt)'],
                'faqs': [
                    {'q': 'Do I need to call police for minor accidents?', 'a': 'Not required if no injuries and damage is less than ₹50,000, but recommended for insurance claims.'},
                    {'q': 'Will my insurance cover the accident?', 'a': 'Third-party insurance covers damage to others. Own damage coverage depends on your policy.'},
                    {'q': 'Can I settle without involving insurance?', 'a': 'Yes, but get a written agreement and ensure no hidden injuries.'}
                ]
            },
            
            'property_dispute': {
                'title': 'Property Dispute Resolution',
                'category': 'Property',
                'state': 'All India',
                'summary': 'How to resolve disputes over land, house, or rental properties',
                'description': '''
                Property disputes are common but can be resolved through proper legal channels:
                
                **Common Property Disputes:**
                - Ownership disputes between family members
                - Boundary disputes with neighbors
                - Landlord-tenant disagreements
                - Illegal occupation of property
                
                **Steps to Resolve:**
                1. Gather all property documents (sale deed, title documents)
                2. Try mediation or family settlement first
                3. Send legal notice to the other party
                4. File case in civil court if needed
                
                **Important Documents:**
                - Sale deed or gift deed
                - Property tax receipts
                - Electricity/water bills in your name
                - Survey settlement records
                ''',
                'punishment': 'Illegal occupation: Criminal case + fine. Document forgery: 7 years imprisonment',
                'related_sections': ['Transfer of Property Act 1882', 'Registration Act 1908', 'Indian Easements Act 1882'],
                'faqs': [
                    {'q': 'How long do property cases take?', 'a': 'Civil property cases typically take 5-10 years, but can be faster with good documentation.'},
                    {'q': 'Can I sell property under dispute?', 'a': 'Generally not advisable. Courts may issue stay orders preventing sale.'},
                    {'q': 'What if I don\'t have proper documents?', 'a': 'You can still claim ownership through adverse possession or other evidence.'}
                ]
            },
            
            'consumer_rights': {
                'title': 'Consumer Rights & Protection',
                'category': 'Consumer',
                'state': 'All India',
                'summary': 'Your rights when buying products or services that are defective or unsatisfactory',
                'description': '''
                As a consumer, you have strong legal protection in India:
                
                **Your Basic Rights:**
                - Right to safety (products shouldn't harm you)
                - Right to information (know what you're buying)
                - Right to choose (no forced purchases)
                - Right to be heard (file complaints)
                - Right to redressal (get compensation for problems)
                
                **Common Consumer Problems:**
                - Defective products
                - Poor service quality
                - Overcharging or hidden charges
                - Misleading advertisements
                - Delivery delays
                
                **How to File Complaint:**
                1. Try to resolve with the seller first
                2. File online complaint at consumer.nic.in
                3. Approach local consumer court
                4. No need for lawyer for amounts up to ₹50 lakhs
                ''',
                'punishment': 'Businesses can be fined up to ₹10 lakhs for misleading ads. Repeat offenders: ₹50 lakhs fine',
                'related_sections': ['Consumer Protection Act 2019', 'Indian Contract Act 1872'],
                'faqs': [
                    {'q': 'Is there a time limit to file consumer complaints?', 'a': 'Yes, you must file within 2 years of the problem occurring.'},
                    {'q': 'Do I need to pay fees for consumer court?', 'a': 'Minimal fees: ₹200 for claims up to ₹5 lakhs, ₹500 for higher amounts.'},
                    {'q': 'Can I file online complaints?', 'a': 'Yes, use the National Consumer Helpline (1800-11-4000) or consumer.nic.in portal.'}
                ]
            },
            
            'domestic_violence': {
                'title': 'Domestic Violence Protection',
                'category': 'Criminal',
                'state': 'All India',
                'summary': 'Legal protection available for victims of domestic violence and abuse',
                'description': '''
                The law provides strong protection against domestic violence:
                
                **What is Domestic Violence:**
                - Physical abuse (hitting, slapping, pushing)
                - Mental abuse (threats, insults, controlling behavior)
                - Sexual abuse
                - Economic abuse (controlling money, preventing work)
                
                **Immediate Help Available:**
                - Call Women Helpline: 181 (24x7 free)
                - Call Police: 100
                - Approach local police station
                - Contact Protection Officer in your district
                
                **Legal Remedies:**
                - Protection order (abuser must stay away)
                - Residence order (you can stay in shared home)
                - Monetary relief (maintenance and compensation)
                - Custody order (for children)
                
                **Important:** You don't need to be married to file - live-in partners, sisters, mothers also protected
                ''',
                'punishment': 'Imprisonment up to 1 year + fine. Breach of protection order: additional 1 year imprisonment',
                'related_sections': ['Protection of Women from Domestic Violence Act 2005', 'IPC Section 498A', 'IPC Section 354'],
                'faqs': [
                    {'q': 'Can I file case without evidence?', 'a': 'Yes, your statement is evidence. Medical reports, photos, witness statements help strengthen the case.'},
                    {'q': 'Will I have to leave my home?', 'a': 'No, the law protects your right to live in the shared household.'},
                    {'q': 'Is the process confidential?', 'a': 'Court proceedings are usually in-camera (private) to protect your privacy.'}
                ]
            },
            
            'employment_rights': {
                'title': 'Employee Rights & Labor Laws',
                'category': 'Employment',
                'state': 'All India',
                'summary': 'Your rights as an employee - salary, working hours, leave, and workplace safety',
                'description': '''
                Indian labor laws protect employees from exploitation:
                
                **Basic Employee Rights:**
                - Minimum wage (varies by state, around ₹150-300 per day)
                - Maximum 9 hours work per day, 48 hours per week
                - Overtime pay at double rate for extra hours
                - Weekly holiday and annual leave
                - Safe working conditions
                
                **Salary & Payment Rights:**
                - Salary must be paid by 7th of next month
                - Cannot deduct more than 50% of salary for advances
                - Gratuity after 5 years of service
                - PF and ESI contributions for eligible employees
                
                **If Your Rights Are Violated:**
                1. Raise issue with HR department first
                2. File complaint with Labor Commissioner
                3. Approach labor court
                4. File case for unpaid wages (quick process)
                ''',
                'punishment': 'Employers face ₹20,000-50,000 fine for salary delays. Imprisonment for serious violations',
                'related_sections': ['Payment of Wages Act 1936', 'Minimum Wages Act 1948', 'Factories Act 1948'],
                'faqs': [
                    {'q': 'Can my employer fire me without notice?', 'a': 'For permanent employees, 30 days notice or payment in lieu is required.'},
                    {'q': 'Am I entitled to overtime pay?', 'a': 'Yes, if you work more than 9 hours per day, you should get double wages for extra hours.'},
                    {'q': 'What if my employer doesn\'t pay PF?', 'a': 'File complaint with PF Commissioner. You can also file online at epfindia.gov.in.'}
                ]
            },
            
            'police_complaint': {
                'title': 'How to File Police Complaint (FIR)',
                'category': 'Criminal',
                'state': 'All India',
                'summary': 'Step-by-step guide to file FIR and deal with police procedures',
                'description': '''
                Filing an FIR (First Information Report) is your right:
                
                **When to File FIR:**
                - Any cognizable offense (theft, assault, fraud, etc.)
                - Accidents with injuries
                - Missing person cases
                - Threats or harassment
                
                **How to File FIR:**
                1. Go to nearest police station (any station can take FIR)
                2. Give written complaint or dictate to police
                3. FIR must be read back to you
                4. Sign the FIR and get a copy
                5. Note down FIR number for reference
                
                **Online FIR:**
                - Many states allow online FIR filing
                - Use your state police website
                - Good for non-urgent matters
                
                **Important Rights:**
                - Police cannot refuse to file FIR for cognizable offenses
                - FIR copy must be given free of cost
                - You can complain to SP if police refuses
                ''',
                'punishment': 'Police officer refusing to file FIR: disciplinary action + departmental inquiry',
                'related_sections': ['Criminal Procedure Code Section 154', 'Indian Penal Code', 'Police Act'],
                'faqs': [
                    {'q': 'Can police refuse to file my FIR?', 'a': 'No, they cannot refuse FIR for cognizable offenses. You can complain to higher authorities.'},
                    {'q': 'What is the difference between FIR and complaint?', 'a': 'FIR is for serious crimes, complaint is for non-cognizable offenses requiring court permission.'},
                    {'q': 'Can I file FIR online?', 'a': 'Yes, many states have online FIR facility. Check your state police website.'}
                ]
            },
            
            'cybercrime': {
                'title': 'Cybercrime & Online Fraud Protection',
                'category': 'Criminal',
                'state': 'All India',
                'summary': 'Protection against online fraud, hacking, and digital crimes',
                'description': '''
                Cybercrime is increasing rapidly. Know your protection:
                
                **Common Cybercrimes:**
                - UPI/Bank fraud
                - Online shopping fraud
                - Social media hacking
                - Identity theft
                - Cyberbullying and trolling
                - Fake job/lottery scams
                
                **Immediate Action for Cyber Fraud:**
                1. Call Cyber Crime Helpline: 1930 (24x7)
                2. Report online at cybercrime.gov.in
                3. Block your bank account if money stolen
                4. File FIR at cyber crime police station
                
                **Prevention Tips:**
                - Never share OTP or bank details
                - Use strong passwords and 2-factor authentication
                - Don't click suspicious links
                - Verify before making online payments
                
                **Recovery:** Many victims get money back if reported quickly
                ''',
                'punishment': 'Cyber fraud: 3 years imprisonment + fine. Hacking: up to 3 years jail. Identity theft: 3 years + ₹1 lakh fine',
                'related_sections': ['Information Technology Act 2000', 'IPC Section 420 (Cheating)', 'Banking Regulation Act'],
                'faqs': [
                    {'q': 'Can I get my money back if I\'m scammed online?', 'a': 'Yes, if you report within 24 hours to bank and cyber cell, recovery chances are high.'},
                    {'q': 'How to report fake social media profiles?', 'a': 'Report on cybercrime.gov.in and also to the social media platform directly.'},
                    {'q': 'Is sharing someone\'s private photos illegal?', 'a': 'Yes, it\'s a serious offense with up to 7 years imprisonment under IT Act.'}
                ]
            }
        }
    
    def search_laws(self, query: str, category: str = None, state: str = None) -> list:
        """Search for laws based on user query"""
        results = []
        query_lower = query.lower()
        
        for law_id, law_data in self.law_cards.items():
            # Check if query matches keywords (highest priority)
            keywords_match = False
            if 'keywords' in law_data:
                for keyword in law_data['keywords']:
                    if query_lower in keyword.lower():
                        keywords_match = True
                        break
            
            # Check if query matches title, summary, description, or related sections
            if (keywords_match or
                query_lower in law_data.get('title', '').lower() or 
                query_lower in law_data.get('summary', '').lower() or 
                query_lower in law_data.get('description', '').lower() or
                any(query_lower in section.lower() for section in law_data.get('related_sections', []))):
                
                # Apply filters
                if category and law_data.get('category', '') != category:
                    continue
                if state and state != 'All India' and law_data.get('state', '') != state and law_data.get('state', '') != 'All India':
                    continue
                
                results.append({
                    'id': law_id,
                    'title': law_data.get('title', ''),
                    'category': law_data.get('category', ''),
                    'state': law_data.get('state', 'All India'),
                    'summary': law_data.get('summary', '')
                })
        
        return results
    
    def get_law_details(self, law_id: str) -> dict:
        """Get detailed information about a specific law"""
        law_data = self.law_cards.get(law_id, {})
        
        # Ensure all required fields are present
        if law_data:
            # Make sure the law has an id field
            if 'id' not in law_data:
                law_data['id'] = law_id
                
            # Ensure all required fields have at least empty values
            for field in ['title', 'category', 'state', 'summary', 'description', 'punishment', 'related_sections', 'faqs']:
                if field not in law_data:
                    law_data[field] = '' if field not in ['related_sections', 'faqs'] else []
        
        return law_data
    
    def get_categories(self) -> list:
        """Get all available law categories"""
        categories = set()
        for law_data in self.law_cards.values():
            category = law_data.get('category')
            if category:
                categories.add(category)
        return sorted(list(categories))
    
    def get_states(self) -> list:
        """Get all available states"""
        states = ['All India', 'Andhra Pradesh', 'Assam', 'Bihar', 'Chhattisgarh', 'Delhi', 'Goa', 'Gujarat', 
                 'Haryana', 'Himachal Pradesh', 'Jharkhand', 'Karnataka', 'Kerala', 'Madhya Pradesh', 
                 'Maharashtra', 'Manipur', 'Meghalaya', 'Mizoram', 'Nagaland', 'Odisha', 'Punjab', 
                 'Rajasthan', 'Sikkim', 'Tamil Nadu', 'Telangana', 'Tripura', 'Uttar Pradesh', 
                 'Uttarakhand', 'West Bengal']
        return states
    
    def ask_legal_question(self, question: str) -> str:
        """Use AI to answer specific legal questions"""
        try:
            prompt = f"""
You are a helpful legal AI assistant specializing in Indian law. Answer this question in simple language that anyone can understand.

Guidelines:
- Use everyday language, avoid legal jargon
- Provide practical, actionable advice
- Include relevant Indian law references
- Mention when to consult a lawyer
- Focus on rights and remedies available

Question: {question}

Provide a clear, helpful answer that includes:
1. Direct answer in simple terms
2. What the person can do
3. Important deadlines or requirements
4. When professional legal help is needed
"""

            response = self.model.generate_content(
                prompt,
                generation_config=genai.GenerationConfig(
                    temperature=0.3,
                    max_output_tokens=1000
                )
            )
            
            return response.text
            
        except Exception as e:
            return "I'm unable to answer your question right now. Please consult with a qualified legal professional for assistance."
    
    def generate_legal_document_summary(self, document_type: str, parties: list, key_terms: dict) -> str:
        """Generate a simple summary of legal documents"""
        try:
            prompt = f"""
Create a simple summary of this legal document that anyone can understand:

Document Type: {document_type}
Parties Involved: {', '.join(parties)}
Key Terms: {key_terms}

Write a summary that explains:
1. What this document is for
2. Who are the main parties
3. Main obligations of each party
4. Important dates or deadlines
5. Key risks or benefits
6. What happens if someone doesn't follow the agreement

Use simple language without legal jargon.
"""

            response = self.model.generate_content(
                prompt,
                generation_config=genai.GenerationConfig(
                    temperature=0.2,
                    max_output_tokens=800
                )
            )
            
            return response.text
            
        except Exception:
            return "Unable to generate document summary at this time."