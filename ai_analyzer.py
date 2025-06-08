import re
import logging
from typing import Dict, List, Any
import json
import os
import google.generativeai as genai

class AIAnalyzer:
    """AI-powered document analysis for legal compliance using Gemini 2.0 Flash"""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.legal_patterns = self._load_legal_patterns()
        # Configure Gemini 2.0 Flash API
        api_key = "AIzaSyB55sz3cuGqePKJlZKolIDzJLRUXAOSeoc"
        genai.configure(api_key=api_key)
        self.model = genai.GenerativeModel('gemini-2.0-flash-exp')
    
    def _load_legal_patterns(self) -> Dict[str, List[Dict]]:
        """Load predefined legal patterns for Indian law compliance"""
        return {
            'contract_clauses': [
                {
                    'pattern': r'(?i)(termination|terminate|end|expiry|expire)',
                    'requirement': 'termination clause',
                    'description': 'Contract should include clear termination conditions',
                    'severity': 'high'
                },
                {
                    'pattern': r'(?i)(dispute|resolution|arbitration|mediation)',
                    'requirement': 'dispute resolution',
                    'description': 'Contract should specify dispute resolution mechanism',
                    'severity': 'high'
                },
                {
                    'pattern': r'(?i)(governing|law|jurisdiction|courts?)',
                    'requirement': 'governing law',
                    'description': 'Contract should specify governing law and jurisdiction',
                    'severity': 'medium'
                },
                {
                    'pattern': r'(?i)(confidential|non.?disclosure|proprietary)',
                    'requirement': 'confidentiality',
                    'description': 'Consider including confidentiality clauses',
                    'severity': 'medium'
                }
            ],
            'compliance_keywords': [
                {
                    'pattern': r'(?i)(gst|goods.?and.?services.?tax)',
                    'law': 'GST Act',
                    'description': 'GST compliance requirements may apply',
                    'severity': 'high'
                },
                {
                    'pattern': r'(?i)(companies.?act|director|shareholder|board)',
                    'law': 'Companies Act 2013',
                    'description': 'Corporate compliance requirements',
                    'severity': 'high'
                },
                {
                    'pattern': r'(?i)(consumer|customer|warranty|guarantee)',
                    'law': 'Consumer Protection Act',
                    'description': 'Consumer protection laws may apply',
                    'severity': 'medium'
                },
                {
                    'pattern': r'(?i)(labour|employee|wages|working.?hours)',
                    'law': 'Labour Laws',
                    'description': 'Employment law compliance required',
                    'severity': 'high'
                }
            ],
            'risk_indicators': [
                {
                    'pattern': r'(?i)(unlimited.?liability|personal.?guarantee)',
                    'risk': 'Financial Risk',
                    'description': 'Unlimited liability clauses present',
                    'severity': 'critical'
                },
                {
                    'pattern': r'(?i)(penalty|fine|damages|breach)',
                    'risk': 'Legal Risk',
                    'description': 'Penalty clauses identified',
                    'severity': 'high'
                },
                {
                    'pattern': r'(?i)(exclusive|sole|monopoly)',
                    'risk': 'Business Risk',
                    'description': 'Exclusive arrangements may limit options',
                    'severity': 'medium'
                }
            ]
        }
    
    def analyze_document(self, text: str, file_type: str) -> Dict[str, Any]:
        """Perform comprehensive AI-powered analysis of the document"""
        try:
            self.logger.info(f"Starting document analysis for {file_type} file")
            
            # Basic document analysis
            doc_type = self._identify_document_type(text)
            issues = []
            legal_areas = []
            
            # Pattern-based analysis
            contract_analysis = self._analyze_contract_compliance(text)
            legal_compliance = self._analyze_legal_compliance(text)
            risk_analysis = self._analyze_risk_factors(text)
            
            # Combine all issues
            issues.extend(contract_analysis.get('issues', []))
            issues.extend(legal_compliance.get('issues', []))
            issues.extend(risk_analysis.get('issues', []))
            
            # Combine legal areas
            legal_areas.extend(contract_analysis.get('legal_areas', []))
            legal_areas.extend(legal_compliance.get('legal_areas', []))
            
            # AI-powered analysis
            ai_results = self._perform_ai_analysis(text)
            
            # Calculate compliance score
            compliance_score = self._calculate_compliance_score(text, issues)
            
            analysis_result = {
                'document_type': doc_type,
                'compliance_score': compliance_score,
                'issues': issues,
                'legal_areas': list(set(legal_areas)),  # Remove duplicates
                'ai_analysis': ai_results,
                'summary': self._generate_summary({
                    'document_type': doc_type,
                    'compliance_score': compliance_score,
                    'issues': issues,
                    'legal_areas': legal_areas
                }),
                'recommendations': self._generate_recommendations({
                    'document_type': doc_type,
                    'compliance_score': compliance_score,
                    'issues': issues,
                    'legal_areas': legal_areas
                })
            }
            
            self.logger.info(f"Document analysis completed. Score: {compliance_score}")
            return analysis_result
            
        except Exception as e:
            self.logger.error(f"Document analysis failed: {str(e)}")
            return {
                'document_type': 'unknown',
                'compliance_score': 0.0,
                'issues': [],
                'legal_areas': [],
                'ai_analysis': {'ai_summary': 'Analysis failed'},
                'summary': 'Document analysis could not be completed',
                'recommendations': ['Please review document manually with legal counsel']
            }
    
    def _identify_document_type(self, text: str) -> str:
        """Identify the type of legal document"""
        text_lower = text.lower()
        
        if any(word in text_lower for word in ['agreement', 'contract', 'memorandum of understanding']):
            return 'contract'
        elif any(word in text_lower for word in ['policy', 'terms and conditions', 'privacy policy']):
            return 'policy'
        elif any(word in text_lower for word in ['notice', 'notification', 'circular']):
            return 'notice'
        elif any(word in text_lower for word in ['invoice', 'bill', 'receipt']):
            return 'financial'
        elif any(word in text_lower for word in ['lease', 'rent', 'tenancy']):
            return 'property'
        else:
            return 'legal_document'
    
    def _analyze_contract_compliance(self, text: str) -> Dict[str, Any]:
        """Analyze contract-specific compliance requirements"""
        issues = []
        legal_areas = []
        
        for clause in self.legal_patterns['contract_clauses']:
            if not re.search(clause['pattern'], text):
                issues.append({
                    'category': 'contract',
                    'type': clause['requirement'],
                    'severity': clause['severity'],
                    'description': clause['description'],
                    'suggestion': f"Consider adding {clause['requirement']} to the contract"
                })
        
        # Check for essential contract elements
        essential_elements = [
            ('consideration', r'(?i)(payment|consideration|amount|price)'),
            ('parties', r'(?i)(party|parties|between|amongst)'),
            ('obligations', r'(?i)(shall|will|must|obligation|duty)')
        ]
        
        for element, pattern in essential_elements:
            if re.search(pattern, text):
                legal_areas.append(f"Contract {element}")
        
        return {'issues': issues, 'legal_areas': legal_areas}
    
    def _analyze_legal_compliance(self, text: str) -> Dict[str, Any]:
        """Analyze compliance with Indian laws"""
        issues = []
        legal_areas = []
        
        for compliance in self.legal_patterns['compliance_keywords']:
            if re.search(compliance['pattern'], text):
                legal_areas.append(compliance['law'])
                issues.append({
                    'category': 'compliance',
                    'type': compliance['law'],
                    'severity': compliance['severity'],
                    'description': compliance['description'],
                    'suggestion': f"Ensure compliance with {compliance['law']}"
                })
        
        return {'issues': issues, 'legal_areas': legal_areas}
    
    def _analyze_risk_factors(self, text: str) -> Dict[str, Any]:
        """Analyze potential risk factors in the document"""
        issues = []
        legal_areas = []
        
        for risk in self.legal_patterns['risk_indicators']:
            if re.search(risk['pattern'], text):
                legal_areas.append(risk['risk'])
                issues.append({
                    'category': 'risk',
                    'type': risk['risk'],
                    'severity': risk['severity'],
                    'description': risk['description'],
                    'suggestion': f"Review and mitigate {risk['risk'].lower()}"
                })
        
        return {'issues': issues, 'legal_areas': legal_areas}
    
    def _calculate_compliance_score(self, text: str, issues: List[Dict]) -> float:
        """Calculate overall compliance score based on analysis"""
        base_score = 70.0
        
        # Deduct points for issues
        critical_issues = sum(1 for i in issues if i.get('severity') == 'critical')
        high_issues = sum(1 for i in issues if i.get('severity') == 'high')
        medium_issues = sum(1 for i in issues if i.get('severity') == 'medium')
        
        score_deduction = (critical_issues * 20) + (high_issues * 10) + (medium_issues * 5)
        final_score = max(0.0, base_score - score_deduction)
        
        # Add points for good practices
        if re.search(r'(?i)(dispute.?resolution|arbitration)', text):
            final_score += 5
        if re.search(r'(?i)(termination|end|expiry)', text):
            final_score += 5
        if re.search(r'(?i)(governing.?law|jurisdiction)', text):
            final_score += 5
        
        return min(100.0, final_score)
    
    def _generate_summary(self, analysis: Dict[str, Any]) -> str:
        """Generate analysis summary"""
        score = analysis['compliance_score']
        issue_count = len(analysis['issues'])
        doc_type = analysis['document_type']
        
        if score >= 80:
            status = "Good compliance"
        elif score >= 60:
            status = "Moderate compliance"
        else:
            status = "Poor compliance"
        
        summary = f"Document Type: {doc_type.title()}\n"
        summary += f"Compliance Score: {score:.1f}/100 ({status})\n"
        summary += f"Issues Found: {issue_count}\n"
        
        if analysis['legal_areas']:
            summary += f"Legal Areas: {', '.join(analysis['legal_areas'])}\n"
        
        return summary
    
    def _generate_recommendations(self, analysis: Dict[str, Any]) -> List[str]:
        """Generate actionable recommendations"""
        recommendations = []
        
        critical_issues = [i for i in analysis['issues'] if i.get('severity') == 'critical']
        high_issues = [i for i in analysis['issues'] if i.get('severity') == 'high']
        
        if critical_issues:
            recommendations.append("Address critical issues immediately before finalizing the document")
        
        if high_issues:
            recommendations.append("Review high-priority issues with legal counsel")
        
        if analysis['compliance_score'] < 60:
            recommendations.append("Consider comprehensive legal review due to low compliance score")
        
        if not analysis['legal_areas']:
            recommendations.append("Verify if document requires specific legal compliance measures")
        
        # Default recommendations
        recommendations.extend([
            "Review all identified issues with qualified legal counsel",
            "Ensure all parties understand their obligations and rights",
            "Keep updated records of all document versions and amendments"
        ])
        
        return recommendations[:5]  # Limit to top 5 recommendations
    
    def _perform_ai_analysis(self, text: str) -> Dict[str, Any]:
        """Perform AI-powered legal document analysis using Gemini 2.0 Flash"""
        try:
            # Truncate text if too long to avoid token limits
            max_chars = 30000  # Gemini has higher token limits
            analysis_text = text[:max_chars] if len(text) > max_chars else text
            
            prompt = f"""
You are an expert legal analyst specializing in Indian law. Analyze this legal document and provide:

1. A comprehensive summary (2-3 sentences)
2. Document type identification
3. Legal compliance status with Indian laws
4. Key legal issues or missing clauses
5. Risk assessment
6. Specific recommendations

Document text:
{analysis_text}

Respond in JSON format with this structure:
{{
    "ai_summary": "Brief document summary",
    "document_type": "contract/agreement/policy/notice/other",
    "legal_compliance_status": "compliant/partially_compliant/non_compliant",
    "key_clauses": ["clause1", "clause2", "clause3"],
    "issues": [
        {{
            "category": "contract/compliance/risk",
            "type": "specific_issue_type",
            "severity": "critical/high/medium/low",
            "description": "Issue description",
            "suggestion": "Specific recommendation"
        }}
    ],
    "risk_assessment": {{
        "overall_risk": "high/medium/low",
        "financial_risk": "description",
        "legal_risk": "description",
        "compliance_risk": "description"
    }},
    "indian_law_compliance": {{
        "contract_act_1872": "compliant/issues_found/not_applicable",
        "companies_act_2013": "compliant/issues_found/not_applicable",
        "consumer_protection_act": "compliant/issues_found/not_applicable",
        "gst_compliance": "compliant/issues_found/not_applicable"
    }}
}}
"""

            response = self.model.generate_content(
                prompt,
                generation_config=genai.GenerationConfig(
                    temperature=0.1,
                    max_output_tokens=2000,
                    response_mime_type="application/json"
                )
            )
            
            result = json.loads(response.text)
            return result
            
        except Exception as e:
            self.logger.error(f"AI analysis failed: {str(e)}")
            return {
                'ai_summary': 'AI analysis could not be completed',
                'issues': [],
                'risk_assessment': {'overall_risk': 'unknown'}
            }
    
    def generate_document_summary(self, text: str) -> Dict[str, str]:
        """Generate a detailed summary of the legal document"""
        try:
            max_chars = 30000
            summary_text = text[:max_chars] if len(text) > max_chars else text
            
            prompt = f"""
Create a comprehensive summary of this legal document in simple, clear language that non-lawyers can understand.

Include:
1. Main purpose and type of document
2. Key parties involved
3. Important obligations and rights
4. Timeline and deadlines
5. Financial terms (if any)
6. Key risks or benefits
7. Next steps or actions required

Document:
{summary_text}

Provide response in JSON format:
{{
    "executive_summary": "2-3 sentence overview",
    "document_purpose": "Main purpose in simple terms",
    "key_parties": "Who is involved",
    "main_obligations": "What each party must do",
    "important_dates": "Key deadlines and timelines",
    "financial_terms": "Money-related aspects",
    "risks_and_benefits": "Potential issues and advantages",
    "next_steps": "What should happen next"
}}
"""

            response = self.model.generate_content(
                prompt,
                generation_config=genai.GenerationConfig(
                    temperature=0.2,
                    max_output_tokens=1500,
                    response_mime_type="application/json"
                )
            )
            
            return json.loads(response.text)
            
        except Exception as e:
            self.logger.error(f"Document summarization failed: {str(e)}")
            return {
                'executive_summary': 'Document summary could not be generated',
                'document_purpose': 'Please review document manually',
                'next_steps': 'Consult with legal counsel'
            }
    
    def answer_legal_question(self, question: str, document_text: str = "") -> str:
        """Answer legal questions about documents or general Indian law"""
        try:
            context = f"\nDocument context:\n{document_text[:15000]}" if document_text else ""
            
            prompt = f"""
You are a legal AI assistant specializing in Indian law. Answer this legal question clearly and accurately.

Important guidelines:
- Focus on Indian law and regulations
- Provide practical, actionable advice
- Mention when legal counsel is recommended
- Be clear about limitations and when professional help is needed
- Use simple language that non-lawyers can understand

Question: {question}
{context}

Provide a clear, helpful answer that includes:
1. Direct answer to the question
2. Relevant Indian law references
3. Practical next steps
4. When to consult a lawyer
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
            self.logger.error(f"Legal question answering failed: {str(e)}")
            return "I'm unable to answer your question right now. Please consult with a qualified legal professional for assistance."