"""
Enhanced Law Library with JSON database and external API integration
"""
import json
import os
import requests
from typing import Dict, List, Any, Optional
import google.generativeai as genai
from datetime import datetime

class EnhancedLawLibrary:
    """Comprehensive law library with multiple data sources"""
    
    def __init__(self):
        # Configure Gemini API
        api_key = "AIzaSyB55sz3cuGqePKJlZKolIDzJLRUXAOSeoc"
        genai.configure(api_key=api_key)
        self.model = genai.GenerativeModel('gemini-2.0-flash-exp')
        
        # Load local JSON database
        self.local_laws = self._load_local_database()
        
        # External API endpoints
        self.external_apis = {
            'indian_kanoon': 'https://api.indiankanoon.org/search/',
            'government_acts': 'https://legislative.gov.in/api/acts',
            'case_law': 'https://www.casemine.com/api/search'
        }
    
    def _load_local_database(self) -> List[Dict]:
        """Load laws from local JSON database"""
        try:
            with open('data/laws_database.json', 'r', encoding='utf-8') as f:
                return json.load(f)
        except FileNotFoundError:
            return []
    
    def search_laws(self, query: str, category: Optional[str] = None, state: Optional[str] = None) -> List[Dict]:
        """Search laws from both local database and external sources"""
        results = []
        
        # Search local database first
        local_results = self._search_local_database(query, category, state)
        results.extend(local_results)
        
        # Search external APIs for additional results
        external_results = self._search_external_apis(query, category)
        results.extend(external_results)
        
        # Remove duplicates and sort by relevance
        unique_results = self._deduplicate_results(results)
        return sorted(unique_results, key=lambda x: x.get('relevance_score', 0), reverse=True)
    
    def _search_local_database(self, query: str, category: Optional[str], state: Optional[str]) -> List[Dict]:
        """Search the local JSON database"""
        results = []
        query_lower = query.lower()
        
        for law in self.local_laws:
            # Calculate relevance score
            relevance_score = 0
            
            # Check keywords (highest priority)
            for keyword in law.get('keywords', []):
                if query_lower in keyword.lower():
                    relevance_score += 10
            
            # Check title
            if query_lower in law.get('title', '').lower():
                relevance_score += 8
            
            # Check summary
            if query_lower in law.get('summary', '').lower():
                relevance_score += 5
            
            # Check detailed description
            if query_lower in law.get('detailed_description', '').lower():
                relevance_score += 3
            
            # Apply filters
            if category and law.get('category') != category:
                continue
            if state and state != 'All India' and law.get('state') != state and law.get('state') != 'All India':
                continue
            
            if relevance_score > 0:
                result = {
                    'id': law['id'],
                    'title': law['title'],
                    'act': law['act'],
                    'summary': law['summary'],
                    'category': law['category'],
                    'subcategory': law.get('subcategory', ''),
                    'state': law['state'],
                    'relevance_score': relevance_score,
                    'source': 'local_database'
                }
                results.append(result)
        
        return results
    
    def _search_external_apis(self, query: str, category: Optional[str]) -> List[Dict]:
        """Search external legal databases and APIs"""
        results = []
        
        # Search Indian Kanoon (simulated - would need actual API access)
        indian_kanoon_results = self._search_indian_kanoon(query)
        results.extend(indian_kanoon_results)
        
        # Search Government Acts database (simulated)
        gov_acts_results = self._search_government_acts(query, category)
        results.extend(gov_acts_results)
        
        return results
    
    def _search_indian_kanoon(self, query: str) -> List[Dict]:
        """Search Indian Kanoon database (simulated for demo)"""
        # In production, this would make actual API calls
        # For now, returning simulated results based on common searches
        simulated_results = []
        
        if 'accident' in query.lower():
            simulated_results.append({
                'id': 'ik_motor_vehicle',
                'title': 'Motor Vehicle Accident Compensation - Supreme Court Guidelines',
                'act': 'Motor Vehicle Act, 1988',
                'summary': 'Supreme Court guidelines on compensation calculation for motor vehicle accidents',
                'category': 'Civil',
                'subcategory': 'Road Safety',
                'state': 'All India',
                'relevance_score': 7,
                'source': 'indian_kanoon',
                'case_citation': 'Sarla Verma v. DTC (2009) 6 SCC 121'
            })
        
        if 'property' in query.lower():
            simulated_results.append({
                'id': 'ik_property_rights',
                'title': 'Property Rights and Acquisition - Constitutional Provisions',
                'act': 'Constitution of India, Article 300A',
                'summary': 'Right to property and compensation for acquisition by the state',
                'category': 'Constitutional',
                'subcategory': 'Property',
                'state': 'All India',
                'relevance_score': 6,
                'source': 'indian_kanoon'
            })
        
        return simulated_results
    
    def _search_government_acts(self, query: str, category: Optional[str]) -> List[Dict]:
        """Search government acts database (simulated)"""
        # Simulated government database results
        simulated_results = []
        
        if 'consumer' in query.lower():
            simulated_results.append({
                'id': 'gov_consumer_act_2019',
                'title': 'Consumer Protection Act 2019 - Complete Text',
                'act': 'Consumer Protection Act, 2019',
                'summary': 'Complete act with all sections, rules, and amendments for consumer protection',
                'category': 'Consumer',
                'subcategory': 'Consumer Rights',
                'state': 'All India',
                'relevance_score': 8,
                'source': 'government_database'
            })
        
        if 'cyber' in query.lower() or 'online' in query.lower():
            simulated_results.append({
                'id': 'gov_it_act_2000',
                'title': 'Information Technology Act 2000 - Amended 2021',
                'act': 'Information Technology Act, 2000',
                'summary': 'Latest amendments to IT Act covering digital privacy, cybercrime, and data protection',
                'category': 'Criminal',
                'subcategory': 'Cybercrime',
                'state': 'All India',
                'relevance_score': 7,
                'source': 'government_database'
            })
        
        return simulated_results
    
    def _deduplicate_results(self, results: List[Dict]) -> List[Dict]:
        """Remove duplicate results based on title similarity"""
        unique_results = []
        seen_titles = set()
        
        for result in results:
            title_key = result['title'].lower().strip()
            if title_key not in seen_titles:
                seen_titles.add(title_key)
                unique_results.append(result)
        
        return unique_results
    
    def get_law_details(self, law_id: str) -> Optional[Dict]:
        """Get detailed information about a specific law"""
        # First check local database
        for law in self.local_laws:
            if law['id'] == law_id:
                return law
        
        # If not found locally, try to fetch from external APIs
        return self._fetch_external_law_details(law_id)
    
    def _fetch_external_law_details(self, law_id: str) -> Optional[Dict]:
        """Fetch law details from external APIs"""
        # This would make actual API calls in production
        # For now, return None or simulated data
        return None
    
    def get_related_laws(self, law_id: str, limit: int = 5) -> List[Dict]:
        """Get laws related to the given law"""
        current_law = self.get_law_details(law_id)
        if not current_law:
            return []
        
        related_laws = []
        current_category = current_law.get('category')
        current_keywords = current_law.get('keywords', [])
        
        for law in self.local_laws:
            if law['id'] == law_id:
                continue
            
            relevance_score = 0
            
            # Same category
            if law.get('category') == current_category:
                relevance_score += 3
            
            # Shared keywords
            shared_keywords = set(law.get('keywords', [])) & set(current_keywords)
            relevance_score += len(shared_keywords) * 2
            
            if relevance_score > 0:
                related_laws.append({
                    'id': law['id'],
                    'title': law['title'],
                    'summary': law['summary'],
                    'category': law['category'],
                    'relevance_score': relevance_score
                })
        
        # Sort by relevance and return top results
        related_laws.sort(key=lambda x: x['relevance_score'], reverse=True)
        return related_laws[:limit]
    
    def get_categories(self) -> List[str]:
        """Get all available categories"""
        categories = set()
        for law in self.local_laws:
            categories.add(law.get('category', 'Other'))
        return sorted(list(categories))
    
    def get_subcategories(self, category: str) -> List[str]:
        """Get subcategories for a given category"""
        subcategories = set()
        for law in self.local_laws:
            if law.get('category') == category:
                subcategories.add(law.get('subcategory', 'General'))
        return sorted(list(subcategories))
    
    def get_states(self) -> List[str]:
        """Get all available states"""
        return [
            'All India', 'Andhra Pradesh', 'Arunachal Pradesh', 'Assam', 'Bihar', 
            'Chhattisgarh', 'Delhi', 'Goa', 'Gujarat', 'Haryana', 'Himachal Pradesh', 
            'Jharkhand', 'Karnataka', 'Kerala', 'Madhya Pradesh', 'Maharashtra', 
            'Manipur', 'Meghalaya', 'Mizoram', 'Nagaland', 'Odisha', 'Punjab', 
            'Rajasthan', 'Sikkim', 'Tamil Nadu', 'Telangana', 'Tripura', 
            'Uttar Pradesh', 'Uttarakhand', 'West Bengal'
        ]
    
    def ask_legal_question(self, question: str, context: str = "") -> str:
        """Use AI to answer legal questions with context from law database"""
        try:
            # Search for relevant laws based on the question
            relevant_laws = self.search_laws(question, limit=3)
            
            # Build context from relevant laws
            law_context = ""
            if relevant_laws:
                law_context = "Relevant Indian Laws:\n"
                for law in relevant_laws[:3]:
                    law_details = self.get_law_details(law['id'])
                    if law_details:
                        law_context += f"- {law_details['title']}: {law_details['summary']}\n"
                        if law_details.get('punishment'):
                            law_context += f"  Punishment: {law_details['punishment']}\n"
            
            prompt = f"""
You are a legal AI assistant specializing in Indian law. Answer this question using the provided law context and your knowledge.

Question: {question}

{law_context}

Additional Context: {context}

Guidelines:
- Use simple language that anyone can understand
- Provide practical, actionable advice
- Reference specific Indian laws when applicable
- Mention when to consult a lawyer
- Include relevant punishments or legal consequences
- Be clear about limitations

Provide a comprehensive answer covering:
1. Direct answer to the question
2. Relevant Indian law references
3. Practical next steps
4. When professional legal help is needed
"""

            response = self.model.generate_content(
                prompt,
                generation_config=genai.GenerationConfig(
                    temperature=0.3,
                    max_output_tokens=1200
                )
            )
            
            return response.text
            
        except Exception as e:
            return "I'm unable to answer your question right now. Please consult with a qualified legal professional for assistance."
    
    def get_trending_searches(self) -> List[str]:
        """Get trending legal search topics"""
        return [
            "bike accident compensation",
            "property dispute resolution",
            "consumer complaint online",
            "domestic violence protection",
            "employment rights salary",
            "cybercrime reporting",
            "police FIR procedure",
            "rental agreement dispute",
            "divorce procedure",
            "child custody rights"
        ]
    
    def get_law_statistics(self) -> Dict[str, Any]:
        """Get statistics about the law database"""
        total_laws = len(self.local_laws)
        categories = self.get_categories()
        
        category_counts = {}
        for category in categories:
            category_counts[category] = sum(1 for law in self.local_laws if law.get('category') == category)
        
        return {
            'total_laws': total_laws,
            'total_categories': len(categories),
            'category_distribution': category_counts,
            'last_updated': datetime.now().strftime('%Y-%m-%d'),
            'database_sources': ['Local JSON Database', 'Indian Kanoon API', 'Government Acts Database']
        }