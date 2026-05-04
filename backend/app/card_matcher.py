"""Card matching using fuzzy string matching."""

from typing import List, Dict, Optional, Tuple
from fuzzywuzzy import fuzz
from app.config import FUZZY_MATCH_THRESHOLD, MIN_CONFIDENCE


class CardMatcher:
    """Handles fuzzy matching of OCR results to card database."""

    def __init__(self, cards_database: List[Dict]):
        """
        Initialize matcher with card database.
        
        Args:
            cards_database: List of card dictionaries from YGOPRODeck
        """
        self.cards_database = cards_database
        self.card_names = [card.get('name', '').lower() for card in cards_database]

    def find_best_match(
        self,
        ocr_text: str,
        ocr_confidence: float
    ) -> Optional[Dict]:
        """
        Find best matching card using fuzzy matching.
        
        Args:
            ocr_text: Text extracted from OCR
            ocr_confidence: Confidence of OCR extraction
            
        Returns:
            Matched card dict or None if no good match
        """
        if not ocr_text or not ocr_text.strip():
            return None

        ocr_text = ocr_text.strip().lower()
        best_match = None
        best_score = 0

        for card, card_name in zip(self.cards_database, self.card_names):
            # Token sort ratio handles word reordering
            score = fuzz.token_sort_ratio(ocr_text, card_name)
            
            if score > best_score:
                best_score = score
                best_match = card

        # Combine OCR and fuzzy matching confidence
        fuzzy_confidence = best_score / 100
        combined_confidence = (ocr_confidence * 0.4) + (fuzzy_confidence * 0.6)

        if best_score >= FUZZY_MATCH_THRESHOLD and combined_confidence >= MIN_CONFIDENCE:
            return {
                **best_match,
                'match_score': best_score,
                'confidence': combined_confidence,
                'ocr_confidence': ocr_confidence,
                'fuzzy_confidence': fuzzy_confidence
            }

        return None

    def find_top_n_matches(
        self,
        ocr_text: str,
        ocr_confidence: float,
        n: int = 5
    ) -> List[Dict]:
        """
        Find top N matching cards.
        
        Args:
            ocr_text: Text extracted from OCR
            ocr_confidence: Confidence of OCR extraction
            n: Number of matches to return
            
        Returns:
            List of matched cards sorted by confidence
        """
        if not ocr_text or not ocr_text.strip():
            return []

        ocr_text = ocr_text.strip().lower()
        matches = []

        for card, card_name in zip(self.cards_database, self.card_names):
            score = fuzz.token_sort_ratio(ocr_text, card_name)
            
            if score >= FUZZY_MATCH_THRESHOLD:
                fuzzy_confidence = score / 100
                combined_confidence = (ocr_confidence * 0.4) + (fuzzy_confidence * 0.6)
                
                if combined_confidence >= MIN_CONFIDENCE:
                    matches.append({
                        **card,
                        'match_score': score,
                        'confidence': combined_confidence,
                        'ocr_confidence': ocr_confidence,
                        'fuzzy_confidence': fuzzy_confidence
                    })

        # Sort by combined confidence
        matches.sort(key=lambda x: x['confidence'], reverse=True)
        return matches[:n]

    def batch_match(self, ocr_results: List[Tuple[str, float]]) -> List[Optional[Dict]]:
        """
        Match multiple OCR results at once.
        
        Args:
            ocr_results: List of (ocr_text, confidence) tuples
            
        Returns:
            List of matched cards (or None if no match)
        """
        return [
            self.find_best_match(text, conf)
            for text, conf in ocr_results
        ]
