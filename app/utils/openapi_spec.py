"""
Generate OpenAPI 3.0 specification for the API
This works without flasgger and can be used on Vercel
"""

def get_openapi_spec(base_url="https://your-vercel-url.vercel.app"):
    """Generate OpenAPI 3.0 specification"""
    return {
        "openapi": "3.0.0",
        "info": {
            "title": "Enterprise AI Dashboard API",
            "description": "Flask REST API for HR AI Platform and AutoSphere Motors AI Assistant",
            "version": "1.0.0"
        },
        "servers": [
            {
                "url": base_url,
                "description": "Production server"
            },
            {
                "url": "http://localhost:5001",
                "description": "Local development server"
            }
        ],
        "components": {
            "securitySchemes": {
                "Bearer": {
                    "type": "http",
                    "scheme": "bearer",
                    "bearerFormat": "JWT",
                    "description": "JWT Authorization header using the Bearer scheme"
                }
            }
        },
        "tags": [
            {
                "name": "Authentication",
                "description": "User authentication endpoints"
            },
            {
                "name": "HR AI Platform",
                "description": "HR AI Platform endpoints"
            },
            {
                "name": "AutoSphere Motors",
                "description": "AutoSphere Motors AI Assistant endpoints"
            }
        ],
        "paths": {
            "/api/auth/login": {
                "post": {
                    "tags": ["Authentication"],
                    "summary": "Authenticate user and receive JWT token",
                    "requestBody": {
                        "required": True,
                        "content": {
                            "application/json": {
                                "schema": {
                                    "type": "object",
                                    "required": ["username", "password"],
                                    "properties": {
                                        "username": {
                                            "type": "string",
                                            "example": "john_doe"
                                        },
                                        "password": {
                                            "type": "string",
                                            "example": "password123"
                                        }
                                    }
                                }
                            }
                        }
                    },
                    "responses": {
                        "200": {
                            "description": "Login successful",
                            "content": {
                                "application/json": {
                                    "schema": {
                                        "type": "object",
                                        "properties": {
                                            "success": {"type": "boolean", "example": True},
                                            "message": {"type": "string", "example": "Login successful"},
                                            "data": {
                                                "type": "object",
                                                "properties": {
                                                    "token": {"type": "string"},
                                                    "user": {
                                                        "type": "object",
                                                        "properties": {
                                                            "id": {"type": "integer"},
                                                            "username": {"type": "string"},
                                                            "role": {"type": "string"}
                                                        }
                                                    }
                                                }
                                            }
                                        }
                                    }
                                }
                            }
                        },
                        "401": {"description": "Invalid credentials"},
                        "422": {"description": "Validation error"}
                    }
                }
            },
            "/api/hr/cv/evaluate": {
                "post": {
                    "tags": ["HR AI Platform"],
                    "summary": "Evaluate Multiple CVs",
                    "description": "Upload multiple candidate CVs and evaluate them against a job description",
                    "security": [{"Bearer": []}],
                    "requestBody": {
                        "required": True,
                        "content": {
                            "multipart/form-data": {
                                "schema": {
                                    "type": "object",
                                    "required": ["job_description", "cv_files"],
                                    "properties": {
                                        "job_description": {
                                            "type": "string",
                                            "description": "Job description text"
                                        },
                                        "cv_files": {
                                            "type": "array",
                                            "items": {"type": "string", "format": "binary"},
                                            "description": "Candidate CV files (PDF or DOCX, multiple allowed)"
                                        }
                                    }
                                }
                            }
                        }
                    },
                    "responses": {
                        "200": {
                            "description": "CV evaluation completed successfully",
                            "content": {
                                "application/json": {
                                    "schema": {
                                        "type": "object",
                                        "properties": {
                                            "success": {"type": "boolean"},
                                            "message": {"type": "string"},
                                            "data": {
                                                "type": "object",
                                                "properties": {
                                                    "results": {
                                                        "type": "array",
                                                        "items": {"type": "object"}
                                                    },
                                                    "executive_kpis": {"type": "object"}
                                                }
                                            }
                                        }
                                    }
                                }
                            }
                        },
                        "400": {"description": "Bad request"},
                        "401": {"description": "Unauthorized"},
                        "500": {"description": "Server error"}
                    }
                }
            },
            "/api/hr/policy/upload": {
                "post": {
                    "tags": ["HR AI Platform"],
                    "summary": "Upload Policy Documents",
                    "description": "Upload multiple HR policy PDF documents (HR Manager only)",
                    "security": [{"Bearer": []}],
                    "requestBody": {
                        "required": True,
                        "content": {
                            "multipart/form-data": {
                                "schema": {
                                    "type": "object",
                                    "required": ["policy_files"],
                                    "properties": {
                                        "policy_files": {
                                            "type": "array",
                                            "items": {"type": "string", "format": "binary"},
                                            "description": "Policy PDF files (multiple allowed)"
                                        }
                                    }
                                }
                            }
                        }
                    },
                    "responses": {
                        "200": {"description": "Policies uploaded successfully"},
                        "400": {"description": "Bad request"},
                        "401": {"description": "Unauthorized"},
                        "500": {"description": "Server error"}
                    }
                }
            },
            "/api/hr/policy/ask": {
                "post": {
                    "tags": ["HR AI Platform"],
                    "summary": "Ask Policy Question",
                    "description": "Ask a question about HR policies (uses uploaded policy documents)",
                    "security": [{"Bearer": []}],
                    "requestBody": {
                        "required": True,
                        "content": {
                            "application/json": {
                                "schema": {
                                    "type": "object",
                                    "required": ["question"],
                                    "properties": {
                                        "question": {
                                            "type": "string",
                                            "example": "What is the leave policy for employees?"
                                        }
                                    }
                                }
                            }
                        }
                    },
                    "responses": {
                        "200": {"description": "Policy question answered"},
                        "401": {"description": "Unauthorized"},
                        "422": {"description": "Validation error"},
                        "500": {"description": "Server error"}
                    }
                }
            },
            "/api/hr/technical/generate-questions": {
                "post": {
                    "tags": ["HR AI Platform"],
                    "summary": "Generate Technical Questions",
                    "description": "Generate technical interview questions based on candidate CV and job description (HR Manager only)",
                    "security": [{"Bearer": []}],
                    "requestBody": {
                        "required": True,
                        "content": {
                            "multipart/form-data": {
                                "schema": {
                                    "type": "object",
                                    "required": ["job_description", "cv_file"],
                                    "properties": {
                                        "job_description": {
                                            "type": "string",
                                            "description": "Job description text"
                                        },
                                        "cv_file": {
                                            "type": "string",
                                            "format": "binary",
                                            "description": "Candidate CV file (PDF or DOCX)"
                                        }
                                    }
                                }
                            }
                        }
                    },
                    "responses": {
                        "200": {"description": "Technical questions generated successfully"},
                        "400": {"description": "Bad request"},
                        "401": {"description": "Unauthorized"},
                        "403": {"description": "Forbidden (HR Manager role required)"},
                        "500": {"description": "Server error"}
                    }
                }
            },
            "/api/hr/technical/evaluate-answers": {
                "post": {
                    "tags": ["HR AI Platform"],
                    "summary": "Evaluate Technical Answers",
                    "description": "Evaluate candidate's answers to technical interview questions (HR Manager only)",
                    "security": [{"Bearer": []}],
                    "requestBody": {
                        "required": True,
                        "content": {
                            "application/json": {
                                "schema": {
                                    "type": "object",
                                    "required": ["questions", "answers"],
                                    "properties": {
                                        "questions": {
                                            "type": "array",
                                            "items": {"type": "string"},
                                            "example": ["Question 1", "Question 2"]
                                        },
                                        "answers": {
                                            "type": "array",
                                            "items": {"type": "string"},
                                            "example": ["Answer 1", "Answer 2"]
                                        }
                                    }
                                }
                            }
                        }
                    },
                    "responses": {
                        "200": {"description": "Technical evaluation completed"},
                        "400": {"description": "Bad request"},
                        "401": {"description": "Unauthorized"},
                        "403": {"description": "Forbidden (HR Manager role required)"},
                        "422": {"description": "Validation error"},
                        "500": {"description": "Server error"}
                    }
                }
            },
            "/api/autosphere/chat": {
                "post": {
                    "tags": ["AutoSphere Motors"],
                    "summary": "AI Assistant Chat",
                    "description": "Chat with AutoSphere AI assistant. Supports intent classification and booking flow.",
                    "security": [{"Bearer": []}],
                    "requestBody": {
                        "required": True,
                        "content": {
                            "application/json": {
                                "schema": {
                                    "type": "object",
                                    "required": ["message"],
                                    "properties": {
                                        "message": {
                                            "type": "string",
                                            "example": "What services do you offer?"
                                        },
                                        "chat_history": {
                                            "type": "array",
                                            "items": {
                                                "type": "object",
                                                "properties": {
                                                    "role": {"type": "string", "example": "user"},
                                                    "content": {"type": "string", "example": "Hello"}
                                                }
                                            }
                                        }
                                    }
                                }
                            }
                        }
                    },
                    "responses": {
                        "200": {"description": "Chat response generated"},
                        "401": {"description": "Unauthorized"},
                        "422": {"description": "Validation error"},
                        "500": {"description": "Server error"}
                    }
                }
            },
            "/api/autosphere/bookings": {
                "post": {
                    "tags": ["AutoSphere Motors"],
                    "summary": "Create Booking",
                    "description": "Create a service or test drive booking. Supports both structured fields and natural language.",
                    "security": [{"Bearer": []}],
                    "requestBody": {
                        "required": True,
                        "content": {
                            "application/json": {
                                "schema": {
                                    "type": "object",
                                    "required": ["booking_type", "name", "phone", "vehicle_model"],
                                    "properties": {
                                        "booking_type": {
                                            "type": "string",
                                            "enum": ["Service", "Test Drive"],
                                            "example": "Service"
                                        },
                                        "name": {"type": "string", "example": "John Doe"},
                                        "phone": {"type": "string", "example": "+1234567890"},
                                        "vehicle_model": {"type": "string", "example": "Toyota Camry"},
                                        "preferred_date": {"type": "string", "format": "date", "example": "2024-12-25"},
                                        "natural_language": {
                                            "type": "string",
                                            "example": "I want to book a service for my Toyota Camry on December 25th",
                                            "description": "Alternative to structured fields - natural language booking text"
                                        }
                                    }
                                }
                            }
                        }
                    },
                    "responses": {
                        "200": {"description": "Booking created successfully"},
                        "400": {"description": "Bad request"},
                        "401": {"description": "Unauthorized"},
                        "422": {"description": "Validation error"},
                        "500": {"description": "Server error"}
                    }
                },
                "get": {
                    "tags": ["AutoSphere Motors"],
                    "summary": "Search Bookings",
                    "description": "Search bookings by booking ID, phone number, or booking type",
                    "security": [{"Bearer": []}],
                    "parameters": [
                        {
                            "name": "booking_id",
                            "in": "query",
                            "schema": {"type": "string"},
                            "description": "Search by booking ID",
                            "example": "AS-20241225-1234"
                        },
                        {
                            "name": "phone",
                            "in": "query",
                            "schema": {"type": "string"},
                            "description": "Search by phone number",
                            "example": "+1234567890"
                        },
                        {
                            "name": "booking_type",
                            "in": "query",
                            "schema": {"type": "string", "enum": ["Service", "Test Drive"]},
                            "description": "Filter by booking type"
                        }
                    ],
                    "responses": {
                        "200": {"description": "Bookings found"},
                        "401": {"description": "Unauthorized"},
                        "500": {"description": "Server error"}
                    }
                }
            },
            "/api/autosphere/bookings/{booking_id}": {
                "get": {
                    "tags": ["AutoSphere Motors"],
                    "summary": "Get Booking by ID",
                    "description": "Retrieve a specific booking by its booking ID",
                    "security": [{"Bearer": []}],
                    "parameters": [
                        {
                            "name": "booking_id",
                            "in": "path",
                            "required": True,
                            "schema": {"type": "string"},
                            "description": "Booking ID",
                            "example": "AS-20241225-1234"
                        }
                    ],
                    "responses": {
                        "200": {"description": "Booking found"},
                        "401": {"description": "Unauthorized"},
                        "404": {"description": "Booking not found"},
                        "500": {"description": "Server error"}
                    }
                }
            }
        }
    }
