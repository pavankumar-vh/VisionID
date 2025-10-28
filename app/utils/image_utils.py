"""
Image Utilities - Helper functions for image processing
"""

import cv2
import numpy as np
from PIL import Image
from typing import Optional, Tuple
import io


def read_image_file(file_content: bytes) -> Optional[np.ndarray]:
    """
    Read image from bytes and convert to OpenCV format
    
    Args:
        file_content: Image file content as bytes
        
    Returns:
        Image as numpy array in BGR format or None if failed
    """
    try:
        # Convert bytes to numpy array
        nparr = np.frombuffer(file_content, np.uint8)
        # Decode image
        img = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
        return img
    except Exception as e:
        print(f"Error reading image: {e}")
        return None


def convert_pil_to_cv2(pil_image: Image.Image) -> np.ndarray:
    """
    Convert PIL Image to OpenCV format
    
    Args:
        pil_image: PIL Image object
        
    Returns:
        Image as numpy array in BGR format
    """
    # Convert PIL to RGB numpy array
    img_rgb = np.array(pil_image)
    # Convert RGB to BGR for OpenCV
    img_bgr = cv2.cvtColor(img_rgb, cv2.COLOR_RGB2BGR)
    return img_bgr


def convert_cv2_to_pil(cv2_image: np.ndarray) -> Image.Image:
    """
    Convert OpenCV image to PIL format
    
    Args:
        cv2_image: OpenCV image (BGR format)
        
    Returns:
        PIL Image object
    """
    # Convert BGR to RGB
    img_rgb = cv2.cvtColor(cv2_image, cv2.COLOR_BGR2RGB)
    # Convert to PIL
    pil_image = Image.fromarray(img_rgb)
    return pil_image


def resize_image(image: np.ndarray, max_size: Tuple[int, int] = (1920, 1080)) -> np.ndarray:
    """
    Resize image while maintaining aspect ratio
    
    Args:
        image: Input image
        max_size: Maximum (width, height)
        
    Returns:
        Resized image
    """
    h, w = image.shape[:2]
    max_w, max_h = max_size
    
    # Calculate scaling factor
    scale = min(max_w / w, max_h / h, 1.0)
    
    if scale < 1.0:
        new_w = int(w * scale)
        new_h = int(h * scale)
        resized = cv2.resize(image, (new_w, new_h), interpolation=cv2.INTER_AREA)
        return resized
    
    return image


def crop_face(image: np.ndarray, bbox: Tuple[int, int, int, int], padding: int = 20) -> np.ndarray:
    """
    Crop face region from image with padding
    
    Args:
        image: Input image
        bbox: Bounding box as (x1, y1, x2, y2)
        padding: Padding around face
        
    Returns:
        Cropped face image
    """
    h, w = image.shape[:2]
    x1, y1, x2, y2 = bbox
    
    # Add padding
    x1 = max(0, x1 - padding)
    y1 = max(0, y1 - padding)
    x2 = min(w, x2 + padding)
    y2 = min(h, y2 + padding)
    
    face = image[y1:y2, x1:x2]
    return face


def draw_face_box(
    image: np.ndarray, 
    bbox: Tuple[int, int, int, int], 
    label: str = "", 
    confidence: float = 0.0,
    color: Tuple[int, int, int] = (0, 255, 0)
) -> np.ndarray:
    """
    Draw bounding box and label on image
    
    Args:
        image: Input image
        bbox: Bounding box as (x1, y1, x2, y2)
        label: Label text
        confidence: Confidence score
        color: Box color in BGR format
        
    Returns:
        Image with drawn box
    """
    img = image.copy()
    x1, y1, x2, y2 = [int(coord) for coord in bbox]
    
    # Draw rectangle
    cv2.rectangle(img, (x1, y1), (x2, y2), color, 2)
    
    # Prepare label text
    if label and confidence > 0:
        text = f"{label}: {confidence:.2f}"
    elif label:
        text = label
    else:
        text = f"{confidence:.2f}"
    
    # Draw label background
    if text:
        (text_w, text_h), _ = cv2.getTextSize(text, cv2.FONT_HERSHEY_SIMPLEX, 0.6, 1)
        cv2.rectangle(img, (x1, y1 - text_h - 10), (x1 + text_w, y1), color, -1)
        cv2.putText(img, text, (x1, y1 - 5), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 1)
    
    return img


def save_image(image: np.ndarray, path: str) -> bool:
    """
    Save image to file
    
    Args:
        image: Image to save
        path: Output file path
        
    Returns:
        True if successful, False otherwise
    """
    try:
        cv2.imwrite(path, image)
        return True
    except Exception as e:
        print(f"Error saving image: {e}")
        return False


def encode_image_to_bytes(image: np.ndarray, format: str = ".jpg") -> bytes:
    """
    Encode image to bytes
    
    Args:
        image: Input image
        format: Image format (.jpg, .png, etc.)
        
    Returns:
        Image as bytes
    """
    _, buffer = cv2.imencode(format, image)
    return buffer.tobytes()


def validate_image(file_content: bytes, max_size_mb: int = 10) -> Tuple[bool, str]:
    """
    Validate uploaded image
    
    Args:
        file_content: Image file content
        max_size_mb: Maximum file size in MB
        
    Returns:
        (is_valid, error_message)
    """
    # Check file size
    size_mb = len(file_content) / (1024 * 1024)
    if size_mb > max_size_mb:
        return False, f"File size exceeds {max_size_mb}MB limit"
    
    # Try to read image
    img = read_image_file(file_content)
    if img is None:
        return False, "Invalid image file"
    
    # Check image dimensions
    h, w = img.shape[:2]
    if h < 50 or w < 50:
        return False, "Image too small (minimum 50x50 pixels)"
    
    if h > 10000 or w > 10000:
        return False, "Image too large (maximum 10000x10000 pixels)"
    
    return True, "Valid image"
