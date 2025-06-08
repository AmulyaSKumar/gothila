"""
Smart Legal Document Generator with AI-powered form generation
Uses the provided consumer complaint and other legal document templates
"""

import os
import json
from datetime import datetime
from typing import Dict, Any, List
import google.generativeai as genai
from dotenv import load_dotenv
load_dotenv() 

class SmartDocumentGenerator:
    """AI-powered legal document generator using Gemini 2.0 Flash"""
    
    def __init__(self):
        # Configure Gemini API
        api_key = os.getenv("GENAI_API_KEY")
        genai.configure(api_key=api_key)
        self.model = genai.GenerativeModel('gemini-2.0-flash-exp')
        
        # Document templates with smart prompts
        self.templates = {
            'consumer_complaint': {
                'name': 'Consumer Complaint Letter',
                'category': 'consumer',
                'prompt': """You are a legal assistant helping a consumer draft a formal Consumer Complaint Letter.
Use the following details to draft a complete and professional complaint:

Complainant Details:
- Name: {complainant_name}
- Address: {complainant_address}
- Contact: {complainant_contact}

Product/Service Info:
- Product/Service Name: {product_name}
- Purchase Date: {purchase_date}
- Invoice Number: {invoice_number}
- Price: {price}

Issue Details:
- Nature of Problem: {problem_description}
- Actions Taken So Far: {actions_taken}
- Relief Sought: {relief_requested}

Generate a full consumer complaint addressed to the seller/manufacturer including all legal and factual details. Format it as a formal letter with date, recipient, subject, body, and signature block. Include relevant consumer protection law references for India.""",
                'fields': [
                    {'name': 'complainant_name', 'label': 'Your Full Name', 'type': 'text', 'required': True},
                    {'name': 'complainant_address', 'label': 'Your Complete Address', 'type': 'textarea', 'required': True},
                    {'name': 'complainant_contact', 'label': 'Phone/Email', 'type': 'text', 'required': True},
                    {'name': 'product_name', 'label': 'Product/Service Name', 'type': 'text', 'required': True},
                    {'name': 'purchase_date', 'label': 'Purchase Date', 'type': 'date', 'required': True},
                    {'name': 'invoice_number', 'label': 'Invoice/Bill Number', 'type': 'text', 'required': False},
                    {'name': 'price', 'label': 'Price Paid (₹)', 'type': 'number', 'required': True},
                    {'name': 'problem_description', 'label': 'Describe the Problem', 'type': 'textarea', 'required': True},
                    {'name': 'actions_taken', 'label': 'Actions Already Taken', 'type': 'textarea', 'required': False},
                    {'name': 'relief_requested', 'label': 'What Solution Do You Want?', 'type': 'textarea', 'required': True}
                ]
            },
            'legal_notice': {
                'name': 'Legal Notice',
                'category': 'legal',
                'prompt': """Draft a formal Legal Notice using the following inputs. The language must be professional and legally binding.

Sender Information:
- Name: {sender_name}
- Address: {sender_address}
- Contact: {sender_contact}

Recipient Information:
- Name: {recipient_name}
- Address: {recipient_address}

Issue Details:
- Incident Description: {incident_details}
- Date of Incident: {incident_date}
- Losses Incurred: {losses}
- Legal Basis: {legal_references}
- Action Required: {remedy_requested}
- Response Deadline: {response_deadline}

Draft the notice with proper subject, background, demand, legal basis, and warning of further action if not resolved. Include relevant Indian legal provisions.""",
                'fields': [
                    {'name': 'sender_name', 'label': 'Your Name', 'type': 'text', 'required': True},
                    {'name': 'sender_address', 'label': 'Your Address', 'type': 'textarea', 'required': True},
                    {'name': 'sender_contact', 'label': 'Your Contact', 'type': 'text', 'required': True},
                    {'name': 'recipient_name', 'label': 'Recipient Name', 'type': 'text', 'required': True},
                    {'name': 'recipient_address', 'label': 'Recipient Address', 'type': 'textarea', 'required': True},
                    {'name': 'incident_details', 'label': 'Describe the Issue', 'type': 'textarea', 'required': True},
                    {'name': 'incident_date', 'label': 'Date of Incident', 'type': 'date', 'required': True},
                    {'name': 'losses', 'label': 'Losses/Damages', 'type': 'textarea', 'required': False},
                    {'name': 'legal_references', 'label': 'Legal Basis (if known)', 'type': 'textarea', 'required': False},
                    {'name': 'remedy_requested', 'label': 'What Action Do You Want?', 'type': 'textarea', 'required': True},
                    {'name': 'response_deadline', 'label': 'Response Deadline (days)', 'type': 'number', 'required': True}
                ]
            },
            'rent_agreement': {
                'name': 'Rent Agreement',
                'category': 'property',
                'prompt': """You are a legal expert helping generate a valid Rent Agreement. Use the details below:

Parties:
- Landlord: {landlord_name}, Address: {landlord_address}
- Tenant: {tenant_name}, Address: {tenant_address}

Property:
- Address: {property_address}
- Type: {property_type}

Terms:
- Rent: {monthly_rent}
- Deposit: {security_deposit}
- Lease Period: {lease_start_date} to {lease_end_date}
- Payment Due Date: {payment_due_date}

Clauses:
- Notice Period: {notice_period}
- Subletting Allowed: {subletting_permission}
- Maintenance By: {maintenance_responsibility}

Create a formal rental agreement ready for signatures with all standard clauses and Indian rental law compliance.""",
                'fields': [
                    {'name': 'landlord_name', 'label': 'Landlord Name', 'type': 'text', 'required': True},
                    {'name': 'landlord_address', 'label': 'Landlord Address', 'type': 'textarea', 'required': True},
                    {'name': 'tenant_name', 'label': 'Tenant Name', 'type': 'text', 'required': True},
                    {'name': 'tenant_address', 'label': 'Tenant Address', 'type': 'textarea', 'required': True},
                    {'name': 'property_address', 'label': 'Property Address', 'type': 'textarea', 'required': True},
                    {'name': 'property_type', 'label': 'Property Type', 'type': 'select', 'options': ['Apartment', 'House', 'Room', 'Commercial'], 'required': True},
                    {'name': 'monthly_rent', 'label': 'Monthly Rent (₹)', 'type': 'number', 'required': True},
                    {'name': 'security_deposit', 'label': 'Security Deposit (₹)', 'type': 'number', 'required': True},
                    {'name': 'lease_start_date', 'label': 'Lease Start Date', 'type': 'date', 'required': True},
                    {'name': 'lease_end_date', 'label': 'Lease End Date', 'type': 'date', 'required': True},
                    {'name': 'payment_due_date', 'label': 'Monthly Payment Due Date', 'type': 'number', 'required': True},
                    {'name': 'notice_period', 'label': 'Notice Period (months)', 'type': 'number', 'required': True},
                    {'name': 'subletting_permission', 'label': 'Subletting Allowed?', 'type': 'select', 'options': ['Yes', 'No'], 'required': True},
                    {'name': 'maintenance_responsibility', 'label': 'Maintenance Responsibility', 'type': 'select', 'options': ['Landlord', 'Tenant', 'Shared'], 'required': True}
                ]
            },
            'employment_contract': {
                'name': 'Employment Contract',
                'category': 'employment',
                'prompt': """Generate a legally compliant Employment Agreement using the following inputs:

Employer Info:
- Name: {employer_name}
- Company: {company_name}, Address: {company_address}

Employee Info:
- Name: {employee_name}, Address: {employee_address}

Job Details:
- Position: {job_title}
- Start Date: {start_date}
- Working Hours: {working_hours}

Compensation:
- Salary: {salary}
- Benefits: {benefits}

Legal Clauses:
- Termination Terms: {termination_terms}
- Notice Period: {notice_period}
- NDA/Confidentiality: {nda_clause}

Format the contract with title, intro, role description, salary terms, conditions, legal obligations, and signature area compliant with Indian labor laws.""",
                'fields': [
                    {'name': 'employer_name', 'label': 'Employer Name', 'type': 'text', 'required': True},
                    {'name': 'company_name', 'label': 'Company Name', 'type': 'text', 'required': True},
                    {'name': 'company_address', 'label': 'Company Address', 'type': 'textarea', 'required': True},
                    {'name': 'employee_name', 'label': 'Employee Name', 'type': 'text', 'required': True},
                    {'name': 'employee_address', 'label': 'Employee Address', 'type': 'textarea', 'required': True},
                    {'name': 'job_title', 'label': 'Job Title/Position', 'type': 'text', 'required': True},
                    {'name': 'start_date', 'label': 'Start Date', 'type': 'date', 'required': True},
                    {'name': 'working_hours', 'label': 'Working Hours', 'type': 'text', 'required': True},
                    {'name': 'salary', 'label': 'Annual Salary (₹)', 'type': 'number', 'required': True},
                    {'name': 'benefits', 'label': 'Benefits Package', 'type': 'textarea', 'required': False},
                    {'name': 'termination_terms', 'label': 'Termination Terms', 'type': 'textarea', 'required': True},
                    {'name': 'notice_period', 'label': 'Notice Period (months)', 'type': 'number', 'required': True},
                    {'name': 'nda_clause', 'label': 'Confidentiality Required?', 'type': 'select', 'options': ['Yes', 'No'], 'required': True}
                ]
            },
            'rti_application': {
                'name': 'RTI Application',
                'category': 'government',
                'prompt': """Draft a Right to Information (RTI) Application in India format using these inputs:

Applicant Details:
- Name: {applicant_name}
- Address: {applicant_address}
- Contact Info: {contact_info}

Public Authority:
- Department Name: {department_name}
- Address of Office: {department_address}

Information Requested:
- Subject Matter: {subject}
- Timeframe: {timeframe}
- Specific Questions/Info Sought: {questions}

Format the RTI application as per Indian RTI Act 2005: include subject, greeting, body, date, signature, and request for information in specified format.""",
                'fields': [
                    {'name': 'applicant_name', 'label': 'Your Name', 'type': 'text', 'required': True},
                    {'name': 'applicant_address', 'label': 'Your Address', 'type': 'textarea', 'required': True},
                    {'name': 'contact_info', 'label': 'Phone/Email', 'type': 'text', 'required': True},
                    {'name': 'department_name', 'label': 'Government Department', 'type': 'text', 'required': True},
                    {'name': 'department_address', 'label': 'Department Address', 'type': 'textarea', 'required': True},
                    {'name': 'subject', 'label': 'Subject of Information', 'type': 'text', 'required': True},
                    {'name': 'timeframe', 'label': 'Time Period', 'type': 'text', 'required': False},
                    {'name': 'questions', 'label': 'Specific Information Required', 'type': 'textarea', 'required': True}
                ]
            },
            'will_testament': {
                'name': 'Will & Testament',
                'category': 'family',
                'prompt': """Draft a legally valid Last Will & Testament using the following details:

Testator (Person Writing the Will):
- Name: {testator_name}
- Address: {testator_address}
- Age: {testator_age}
- Marital Status: {testator_status}

Beneficiaries:
- List: {beneficiaries_list}

Executor of Will:
- Name: {executor_name}, Contact: {executor_contact}

Assets & Wishes:
- Specific Gifts: {specific_bequests}
- Residual Property Instructions: {residual_instructions}

Format the will using standard legal language, include declaration of sound mind, date, signature line, and witness lines as per Indian Succession Act.""",
                'fields': [
                    {'name': 'testator_name', 'label': 'Your Full Name', 'type': 'text', 'required': True},
                    {'name': 'testator_address', 'label': 'Your Address', 'type': 'textarea', 'required': True},
                    {'name': 'testator_age', 'label': 'Your Age', 'type': 'number', 'required': True},
                    {'name': 'testator_status', 'label': 'Marital Status', 'type': 'select', 'options': ['Single', 'Married', 'Divorced', 'Widowed'], 'required': True},
                    {'name': 'beneficiaries_list', 'label': 'Beneficiaries (Name, Relation, Assets)', 'type': 'textarea', 'required': True},
                    {'name': 'executor_name', 'label': 'Executor Name', 'type': 'text', 'required': True},
                    {'name': 'executor_contact', 'label': 'Executor Contact', 'type': 'text', 'required': True},
                    {'name': 'specific_bequests', 'label': 'Specific Gifts/Bequests', 'type': 'textarea', 'required': False},
                    {'name': 'residual_instructions', 'label': 'Remaining Property Instructions', 'type': 'textarea', 'required': True}
                ]
            }
        }
    
    def get_available_templates(self) -> List[Dict[str, Any]]:
        """Get list of available document templates"""
        templates_list = []
        for template_id, template in self.templates.items():
            templates_list.append({
                'id': template_id,
                'name': template['name'],
                'category': template['category'],
                'fields': template['fields']
            })
        return templates_list
    
    def get_template(self, template_id: str) -> Dict[str, Any]:
        """Get specific template details"""
        return self.templates.get(template_id)
    
    def generate_document(self, template_id: str, form_data: Dict[str, str]) -> str:
        """Generate document using AI with provided template and data"""
        try:
            template = self.templates.get(template_id)
            if not template:
                raise ValueError(f"Template {template_id} not found")
            
            # Format the prompt with user data
            formatted_prompt = template['prompt'].format(**form_data)
            
            # Add additional instructions for better formatting
            enhanced_prompt = f"""
{formatted_prompt}

IMPORTANT FORMATTING INSTRUCTIONS:
1. Use proper legal document formatting with headers, sections, and numbering
2. Include today's date: {datetime.now().strftime('%B %d, %Y')}
3. Use formal legal language appropriate for Indian law
4. Include signature blocks and witness lines where applicable
5. Add relevant legal disclaimers if needed
6. Ensure the document is professionally formatted and ready for use

Generate a complete, legally sound document that can be used immediately.
"""
            
            # Generate content using Gemini
            response = self.model.generate_content(
                enhanced_prompt,
                generation_config=genai.GenerationConfig(
                    temperature=0.3,
                    max_output_tokens=8000,
                )
            )
            
            return response.text
            
        except Exception as e:
            raise Exception(f"Document generation failed: {str(e)}")
    
    def validate_form_data(self, template_id: str, form_data: Dict[str, str]) -> Dict[str, List[str]]:
        """Validate form data against template requirements"""
        template = self.templates.get(template_id)
        if not template:
            return {'errors': ['Template not found']}
        
        errors = []
        for field in template['fields']:
            if field['required'] and not form_data.get(field['name']):
                errors.append(f"{field['label']} is required")
        
        return {'errors': errors}
    
    def get_categories(self) -> List[str]:
        """Get all available document categories"""
        categories = set()
        for template in self.templates.values():
            categories.add(template['category'])
        return sorted(list(categories))