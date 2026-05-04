"""Card database caching from YGOPRODeck API."""

import json
from pathlib import Path
from datetime import datetime, timedelta
from typing import List, Dict, Optional
import requests
from app.config import (
    YGOPRODECK_API_BASE,
    CARD_CACHE_FILE,
    CACHE_EXPIRY_HOURS
)


class CardCache:
    """Manages local caching of YGOPRODeck card database."""

    @staticmethod
    def fetch_cards_from_api() -> List[Dict]:
        """
        Fetch all cards from YGOPRODeck API.
        
        Returns:
            List of card dictionaries
        """
        try:
            url = f"{YGOPRODECK_API_BASE}/cardinfo.php"
            response = requests.get(url, timeout=30)
            response.raise_for_status()
            
            data = response.json()
            cards = data.get('data', [])
            
            print(f"Fetched {len(cards)} cards from YGOPRODeck API")
            return cards
        except Exception as e:
            print(f"Error fetching cards from API: {e}")
            return []

    @staticmethod
    def save_cache(cards: List[Dict]) -> bool:
        """
        Save card cache to local file.
        
        Args:
            cards: List of card dictionaries
            
        Returns:
            Success status
        """
        try:
            cache_data = {
                'timestamp': datetime.now().isoformat(),
                'cards': cards
            }
            with open(CARD_CACHE_FILE, 'w', encoding='utf-8') as f:
                json.dump(cache_data, f, indent=2)
            print(f"Saved {len(cards)} cards to cache")
            return True
        except Exception as e:
            print(f"Error saving cache: {e}")
            return False

    @staticmethod
    def load_cache() -> Optional[List[Dict]]:
        """
        Load card cache from local file if valid.
        
        Returns:
            List of cards or None if cache invalid/expired
        """
        if not CARD_CACHE_FILE.exists():
            return None

        try:
            with open(CARD_CACHE_FILE, 'r', encoding='utf-8') as f:
                cache_data = json.load(f)
            
            # Check expiry
            timestamp = datetime.fromisoformat(cache_data['timestamp'])
            age = datetime.now() - timestamp
            
            if age > timedelta(hours=CACHE_EXPIRY_HOURS):
                print("Cache expired")
                return None
            
            cards = cache_data.get('cards', [])
            print(f"Loaded {len(cards)} cards from cache (age: {age.total_seconds()/3600:.1f}h)")
            return cards
        except Exception as e:
            print(f"Error loading cache: {e}")
            return None

    @staticmethod
    def get_cards(force_refresh: bool = False) -> List[Dict]:
        """
        Get cards from cache or fetch from API.
        
        Args:
            force_refresh: Force fetch from API
            
        Returns:
            List of card dictionaries
        """
        if not force_refresh:
            cached = CardCache.load_cache()
            if cached:
                return cached
        
        # Fetch fresh data
        cards = CardCache.fetch_cards_from_api()
        if cards:
            CardCache.save_cache(cards)
        
        return cards

    @staticmethod
    def get_card_by_name(card_name: str, cards: List[Dict]) -> Optional[Dict]:
        """
        Find card by exact name match.
        
        Args:
            card_name: Card name to search for
            cards: List of cards
            
        Returns:
            Card dictionary or None
        """
        card_name_lower = card_name.lower()
        for card in cards:
            if card.get('name', '').lower() == card_name_lower:
                return card
        return None

    @staticmethod
    def filter_cards_by_type(cards: List[Dict], card_type: str) -> List[Dict]:
        """
        Filter cards by type.
        
        Args:
            cards: List of cards
            card_type: Type to filter by (e.g., 'Monster Card')
            
        Returns:
            Filtered list
        """
        return [c for c in cards if c.get('type') == card_type]
