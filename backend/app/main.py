"""Main FastAPI application for card identification."""

from fastapi import FastAPI, File, UploadFile, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import cv2
import numpy as np
from io import BytesIO
from PIL import Image
import io

from app.image_processor import ImageProcessor
from app.ocr_engine import OCREngine
from app.card_matcher import CardMatcher
from app.card_cache import CardCache
from app.card_code_extractor import CardCodeExtractor
from app.image_quality import ImageQualityAnalyzer
from app.config import (
    FIXED_ROI_WIDTH,
    FIXED_ROI_HEIGHT,
    CARD_NAME_ROI_HEIGHT,
    CARD_CODE_ROI_TOP,
    CARD_CODE_ROI_HEIGHT,
    CARD_CODE_ROI_WIDTH,
    IMAGE_QUALITY_THRESHOLD,
    NAME_OCR_WEIGHT,
    CODE_OCR_WEIGHT,
    FUZZY_MATCH_WEIGHT,
    IMAGE_QUALITY_WEIGHT
)

# Initialize FastAPI app
app = FastAPI(
    title="Yu-Gi-Oh Card Identifier",
    description="Identify Yu-Gi-Oh cards using camera capture",
    version="1.0.0"
)

# Add CORS middleware for frontend access
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize components
image_processor = ImageProcessor()
ocr_engine = OCREngine()
card_code_extractor = CardCodeExtractor()
quality_analyzer = ImageQualityAnalyzer()

# Global state
cards_database = []
card_matcher = None


@app.on_event("startup")
async def startup_event():
    """Initialize card database on startup."""
    global cards_database, card_matcher
    
    print("Loading card database...")
    cards_database = CardCache.get_cards()
    
    if not cards_database:
        print("WARNING: No cards loaded. API will not function properly.")
    else:
        print(f"Initialized with {len(cards_database)} cards")
    
    card_matcher = CardMatcher(cards_database)


@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {
        "status": "healthy",
        "cards_loaded": len(cards_database)
    }


@app.post("/identify_card")
async def identify_card(file: UploadFile = File(...)):
    """
    Identify Yu-Gi-Oh card from image with enhanced OCR pipeline.

    Enhanced pipeline includes:
    1. Card name extraction from top region
    2. Card code extraction from bottom region
    3. Image quality assessment
    4. Fuzzy matching against database
    5. Combined confidence scoring

    POST /identify_card

    Args:
        file: Image file from camera

    Returns:
        JSON with identified card details and comprehensive confidence metrics
    """
    if not card_matcher:
        raise HTTPException(status_code=500, detail="Card database not initialized")

    try:
        # Read image file
        contents = await file.read()
        image_array = np.frombuffer(contents, np.uint8)
        image = cv2.imdecode(image_array, cv2.IMREAD_COLOR)

        if image is None:
            raise HTTPException(status_code=400, detail="Invalid image file")

        # Step 1: Crop fixed ROI (400x600)
        roi = image_processor.crop_fixed_roi(
            image,
            width=FIXED_ROI_WIDTH,
            height=FIXED_ROI_HEIGHT
        )

        # Step 2: Assess image quality
        quality_score = quality_analyzer.assess_quality(roi)

        # Step 3: Extract name region (top 80px)
        name_region = image_processor.extract_name_region(
            roi,
            region_height=CARD_NAME_ROI_HEIGHT
        )

        # Step 4: Preprocess and extract card name
        preprocessed_name = image_processor.preprocess_for_ocr(name_region)
        extracted_name, name_ocr_confidence = ocr_engine.extract_card_name(preprocessed_name)

        if not extracted_name:
            raise HTTPException(
                status_code=400,
                detail="Could not extract card name from image"
            )

        # Step 5: Extract card code (bottom region)
        code_result = card_code_extractor.extract_and_validate(
            roi,
            code_roi_top=CARD_CODE_ROI_TOP,
            code_roi_height=CARD_CODE_ROI_HEIGHT,
            code_roi_width=CARD_CODE_ROI_WIDTH
        )

        # Step 6: Find best match using fuzzy matching
        matched_card = card_matcher.find_best_match(extracted_name, name_ocr_confidence)

        if not matched_card:
            # Return top matches instead
            top_matches = card_matcher.find_top_n_matches(
                extracted_name,
                name_ocr_confidence,
                n=3
            )

            if top_matches:
                return JSONResponse(
                    status_code=200,
                    content={
                        "success": False,
                        "message": "No exact match found, showing top candidates",
                        "extracted_name": extracted_name,
                        "extracted_code": code_result.get("code"),
                        "name_ocr_confidence": round(name_ocr_confidence, 3),
                        "code_ocr_confidence": code_result.get("ocr_confidence"),
                        "code_is_valid": code_result.get("is_valid"),
                        "image_quality": quality_score,
                        "candidates": [
                            {
                                "name": card.get("name"),
                                "type": card.get("type"),
                                "description": card.get("desc", "")[:200],
                                "image_url": card.get("card_images", [{}])[0].get("image_url"),
                                "confidence": round(card.get("confidence", 0), 3),
                                "match_score": card.get("match_score", 0)
                            }
                            for card in top_matches
                        ]
                    }
                )
            else:
                raise HTTPException(
                    status_code=404,
                    detail=f"Card not found: {extracted_name}"
                )

        # Step 7: Calculate combined confidence score
        fuzzy_confidence = matched_card.get("confidence", 0)
        
        combined_confidence = (
            (NAME_OCR_WEIGHT * name_ocr_confidence) +
            (CODE_OCR_WEIGHT * code_result.get("confidence", 0)) +
            (FUZZY_MATCH_WEIGHT * fuzzy_confidence) +
            (IMAGE_QUALITY_WEIGHT * quality_score.get("overall_quality", 0))
        )

        # Determine if review is needed
        needs_review = (
            combined_confidence < 0.80 or
            not code_result.get("is_valid") or
            not quality_score.get("is_acceptable")
        )

        # Generate suggestions
        suggestions = []
        if not quality_score.get("is_acceptable"):
            if quality_score.get("sharpness") < 0.5:
                suggestions.append("Image is blurry. Try again with steadier hand.")
            if quality_score.get("brightness") < 0.4:
                suggestions.append("Image is too dark. Increase lighting.")
            if quality_score.get("brightness") > 0.9:
                suggestions.append("Image is too bright. Reduce glare/lighting.")
            if quality_score.get("noise") < 0.5:
                suggestions.append("Image has too much noise. Clean camera lens.")

        if not code_result.get("is_valid"):
            suggestions.append("Card code could not be identified. Ensure it's clearly visible.")

        if combined_confidence < 0.75:
            suggestions.append("Confidence is low. Try repositioning the card for clearer capture.")

        # Success - return matched card with detailed metrics
        return JSONResponse(
            status_code=200,
            content={
                "success": True,
                "name": matched_card.get("name"),
                "code": code_result.get("code"),
                "card_id": matched_card.get("id"),
                "type": matched_card.get("type"),
                "description": matched_card.get("desc", "")[:500],
                "image_url": matched_card.get("card_images", [{}])[0].get("image_url"),
                "confidence": round(combined_confidence, 3),
                "source": "combined_pipeline",
                "needs_review": needs_review,
                "suggestions": suggestions,
                "metrics": {
                    "name_ocr": round(name_ocr_confidence, 3),
                    "code_ocr": code_result.get("ocr_confidence"),
                    "code_valid": code_result.get("is_valid"),
                    "fuzzy_match": round(fuzzy_confidence, 3),
                    "image_quality": quality_score.get("overall_quality"),
                    "quality_breakdown": {
                        "brightness": quality_score.get("brightness"),
                        "contrast": quality_score.get("contrast"),
                        "sharpness": quality_score.get("sharpness"),
                        "motion_blur": quality_score.get("motion_blur"),
                        "noise": quality_score.get("noise")
                    }
                },
                "extracted_text": {
                    "name": extracted_name,
                    "code": code_result.get("ocr_text")
                },
                "atk": matched_card.get("atk"),
                "def": matched_card.get("def"),
                "level": matched_card.get("level"),
                "race": matched_card.get("race"),
                "attribute": matched_card.get("attribute")
            }
        )

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Internal server error: {str(e)}"
        )


@app.get("/cards")
async def get_cards_list(limit: int = 100, offset: int = 0):
    """
    Get paginated list of available cards.
    
    Args:
        limit: Number of cards to return
        offset: Pagination offset
        
    Returns:
        List of cards with basic info
    """
    cards = cards_database[offset:offset + limit]
    return {
        "total": len(cards_database),
        "limit": limit,
        "offset": offset,
        "cards": [
            {
                "id": card.get("id"),
                "name": card.get("name"),
                "type": card.get("type"),
                "image_url": card.get("card_images", [{}])[0].get("image_url")
            }
            for card in cards
        ]
    }


@app.post("/refresh_cache")
async def refresh_cache():
    """Manually refresh card cache from API."""
    global cards_database, card_matcher
    
    cards_database = CardCache.get_cards(force_refresh=True)
    card_matcher = CardMatcher(cards_database)
    
    return {
        "status": "success",
        "cards_loaded": len(cards_database)
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
