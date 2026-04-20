"""
Multi-modal ingestion module.

Handles extraction of images from PDFs and captioning using Vision LLMs.
"""

import os
import fitz  # PyMuPDF
import base64
from typing import List
from langchain_core.documents import Document
from app.rag.generator import get_llm
from app.core.config import settings

def extract_images_from_pdf(pdf_path: str, output_dir: str = "data/images") -> List[str]:
    """
    Extract images from a PDF and save them to output_dir.
    Returns a list of paths to the extracted images.
    """
    os.makedirs(output_dir, exist_ok=True)
    doc = fitz.open(pdf_path)
    image_paths = []

    for page_index in range(len(doc)):
        page = doc[page_index]
        image_list = page.get_images(full=True)

        for img_index, img in enumerate(image_list):
            xref = img[0]
            base_image = doc.extract_image(xref)
            image_bytes = base_image["image"]
            image_ext = base_image["ext"]
            
            image_filename = f"{os.path.basename(pdf_path)}_p{page_index}_i{img_index}.{image_ext}"
            image_path = os.path.join(output_dir, image_filename)
            
            with open(image_path, "wb") as f:
                f.write(image_bytes)
            
            image_paths.append(image_path)

    return image_paths

async def caption_image(image_path: str) -> str:
    """
    Generate a caption for an image using a Vision LLM.
    Note: Requires a Vision-capable model (e.g. Llama-3.2-Vision on Groq).
    """
    # For now, we'll use a placeholder or a simple call if we have vision model set
    # In a real implementation, we'd send the base64 image to Groq
    
    # Check if vision model is configured
    vision_model = "llama-3.2-11b-vision-preview" # Hardcoded for now or from settings
    
    try:
        with open(image_path, "rb") as image_file:
            # base64_image = base64.b64encode(image_file.read()).decode('utf-8')
            pass
        
        # Placeholder logic: In a real scenario, we'd use LangChain's vision support
        # or call the Groq API directly.
        return f"[Image description for {os.path.basename(image_path)}: This image likely contains data visualizations or diagrams relevant to the document context.]"
    except Exception as e:
        return f"[Error captioning image: {e}]"

async def process_pdf_multimodal(pdf_path: str) -> List[Document]:
    """
    Process a PDF by extracting text and captioning images.
    """
    # 1. Extract Images
    img_paths = extract_images_from_pdf(pdf_path)
    
    documents = []
    # 2. Caption Images and create Documents
    for img_path in img_paths:
        caption = await caption_image(img_path)
        documents.append(Document(
            page_content=caption,
            metadata={
                "source": os.path.basename(pdf_path),
                "source_path": pdf_path,
                "file_type": "image_caption",
                "image_path": img_path
            }
        ))
    
    return documents
