import json
import ast
import random
from datetime import datetime
from typing import Dict, Optional, List
from app.utils.openai_client import get_openai_client
from app.utils.vectorstore import load_vectorstore
from app.repositories.booking_repository import BookingRepository


class AutoSphereService:
    """Service for AutoSphere Motors AI operations"""
    
    LLM_MODEL = "gpt-4o"
    
    def __init__(self):
        self.client = get_openai_client()
        self.booking_repo = BookingRepository()
        self.vectorstore = None  # Lazy load
    
    def _get_vectorstore(self):
        """Lazy load vectorstore"""
        if self.vectorstore is None:
            self.vectorstore = load_vectorstore()
        return self.vectorstore
    
    def _ask_llm(self, prompt: str, model: str = None, temperature: float = 0.2) -> str:
        """Helper to call OpenAI LLM"""
        model = model or self.LLM_MODEL
        response = self.client.chat.completions.create(
            model=model,
            messages=[{"role": "user", "content": prompt}],
            temperature=temperature
        )
        return response.choices[0].message.content
    
    def generate_booking_id(self) -> str:
        """Generate unique booking ID"""
        date_part = datetime.now().strftime("%Y%m%d")
        random_part = random.randint(1000, 9999)
        return f"AS-{date_part}-{random_part}"
    
    def classify_intent(self, user_message: str) -> str:
        """Classify user intent"""
        prompt = f"""
        Classify user intent:
        - service_booking
        - test_drive_booking
        - general_question
        
        Message: {user_message}
        Return only intent in lowercase.
        """
        response = self._ask_llm(prompt, temperature=0)
        return response.strip().lower()
    
    def extract_booking_details(self, user_text: str) -> Optional[Dict]:
        """Extract booking details from natural language text"""
        prompt = f"""
        Extract only the booking details from the text and return as JSON with double quotes.
        Do not add extra text.
        
        Fields required:
        - Name
        - Phone
        - Vehicle Model
        - Preferred Date (YYYY-MM-DD)
        
        Text:
        {user_text}
        """
        
        response = self._ask_llm(prompt, temperature=0)
        text = response.strip()
        
        # Try JSON parsing
        try:
            data = json.loads(text)
            if all(k in data for k in ["Name", "Phone", "Vehicle Model", "Preferred Date"]):
                return data
        except:
            try:
                data = ast.literal_eval(text)
                if isinstance(data, dict) and all(k in data for k in ["Name", "Phone", "Vehicle Model", "Preferred Date"]):
                    return data
            except:
                pass
        
        # Fallback: line-by-line parsing
        data = {}
        lines = user_text.splitlines()
        for line in lines:
            if ":" in line:
                key, val = line.split(":", 1)
                key = key.strip().lower()
                val = val.strip()
                if key in ["name", "phone", "vehicle model", "preferred date"]:
                    data[key.title()] = val
        
        if len(data) == 4:
            return data
        
        return None
    
    def chat(self, message: str, chat_history: Optional[List[Dict]] = None) -> Dict:
        """Handle AI assistant chat"""
        chat_history = chat_history or []
        
        # Classify intent
        intent = self.classify_intent(message)
        booking_flow = False
        
        # Handle booking intents
        if intent in ["service_booking", "test_drive_booking"]:
            booking_flow = True
            booking_type = "Service" if intent == "service_booking" else "Test Drive"
            response_text = f"Sure! Let's book your {booking_type}.\nPlease provide Name, Phone, Vehicle Model, Preferred Date (YYYY-MM-DD) in one message."
        else:
            # General question - use RAG
            vectorstore = self._get_vectorstore()
            docs = vectorstore.similarity_search(message, k=3)
            context = "\n".join([doc.page_content for doc in docs])
            
            response = self.client.chat.completions.create(
                model=self.LLM_MODEL,
                messages=[
                    {"role": "system", "content": "You are AutoSphere AI."},
                    {"role": "user", "content": context + "\nUser: " + message}
                ],
                temperature=0.2
            )
            response_text = response.choices[0].message.content
        
        return {
            "response": response_text,
            "intent": intent,
            "booking_flow": booking_flow
        }
    
    def create_booking(self, booking_type: str, name: str, phone: str, 
                      vehicle_model: str, preferred_date: Optional[str] = None,
                      natural_language: Optional[str] = None) -> Dict:
        """Create a booking"""
        # If natural language provided, try to extract details
        if natural_language:
            extracted = self.extract_booking_details(natural_language)
            if extracted:
                name = extracted.get("Name", name)
                phone = extracted.get("Phone", phone)
                vehicle_model = extracted.get("Vehicle Model", vehicle_model)
                preferred_date = extracted.get("Preferred Date", preferred_date)
        
        # Generate booking ID
        booking_id = self.generate_booking_id()
        
        # Parse preferred_date if string
        from datetime import datetime as dt
        preferred_date_obj = None
        if preferred_date:
            try:
                preferred_date_obj = dt.strptime(preferred_date, "%Y-%m-%d").date()
            except:
                pass
        
        # Create booking
        booking = self.booking_repo.create(
            booking_id=booking_id,
            booking_type=booking_type,
            name=name,
            phone=phone,
            vehicle_model=vehicle_model,
            preferred_date=preferred_date_obj
        )
        
        return booking.to_dict()
    
    def search_bookings(self, booking_id: Optional[str] = None,
                       phone: Optional[str] = None,
                       booking_type: Optional[str] = None) -> List[Dict]:
        """Search bookings by filters"""
        bookings = self.booking_repo.search(
            booking_id=booking_id,
            phone=phone,
            booking_type=booking_type
        )
        return [booking.to_dict() for booking in bookings]
    
    def get_booking_by_id(self, booking_id: str) -> Optional[Dict]:
        """Get booking by booking ID"""
        booking = self.booking_repo.get_by_booking_id(booking_id)
        if booking:
            return booking.to_dict()
        return None
