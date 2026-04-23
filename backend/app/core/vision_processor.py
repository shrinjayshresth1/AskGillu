"""
vision_processor.py
Handles image encoding and vision-based text extraction using Groq's vision model.
"""
import base64
import os
from typing import Optional


def encode_image_to_base64(file_bytes: bytes) -> str:
    """Encode raw image bytes to a base64 string."""
    return base64.b64encode(file_bytes).decode("utf-8")


def extract_text_from_image(
    image_b64: str,
    question: str,
    groq_client,
    model: str = "llama-3.2-11b-vision-preview",
) -> str:
    """
    Send image + question to Groq vision model and return the response text.
    Falls back to a descriptive message if vision model is unavailable.
    """
    try:
        messages = [
            {
                "role": "user",
                "content": [
                    {
                        "type": "text",
                        "text": (
                            f"You are AskGillu, an AI assistant for Shri Ramswaroop Memorial "
                            f"University (SRMU). A student has uploaded an image and asked:\n\n"
                            f"'{question}'\n\n"
                            f"Please analyse the image carefully and answer the student's question "
                            f"based on what you see. If the image contains text (e.g., a fee receipt, "
                            f"notice, timetable, or form), extract and explain the relevant information. "
                            f"Format your response clearly using markdown."
                        ),
                    },
                    {
                        "type": "image_url",
                        "image_url": {
                            "url": f"data:image/jpeg;base64,{image_b64}",
                        },
                    },
                ],
            }
        ]

        response = groq_client.invoke(messages)
        return response.content

    except Exception as e:
        error_msg = str(e)
        if "model" in error_msg.lower() or "not found" in error_msg.lower():
            return (
                "⚠️ **Vision model unavailable**: The `llama-3.2-11b-vision-preview` model "
                "is not enabled on your Groq account. Please enable it at console.groq.com "
                "or use a text-based question instead."
            )
        raise


def process_image_for_rag(
    file_bytes: bytes,
    question: str,
    groq_client,
) -> dict:
    """
    Full pipeline: encode → vision extract → return structured result.
    Returns: { extracted_text, visual_description, success, error }
    """
    try:
        image_b64 = encode_image_to_base64(file_bytes)
        answer = extract_text_from_image(image_b64, question, groq_client)
        return {
            "extracted_text": answer,
            "visual_description": answer,
            "success": True,
            "error": None,
        }
    except Exception as e:
        return {
            "extracted_text": "",
            "visual_description": "",
            "success": False,
            "error": str(e),
        }
