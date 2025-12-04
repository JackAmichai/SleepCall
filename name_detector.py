"""
Name Detection Module
Detects target names in transcribed text using exact and fuzzy matching
"""
from typing import List
from rapidfuzz import fuzz


class NameDetector:
    """
    Detects when target names are mentioned in text using multiple matching strategies
    """
    
    def __init__(self, target_names: List[str], fuzz_threshold: int = 88):
        """
        Initialize the name detector
        
        Args:
            target_names: List of names to detect
            fuzz_threshold: Fuzzy matching threshold (0-100, higher = stricter)
        """
        self.target_names = [name.strip() for name in target_names if name.strip()]
        self.fuzz_threshold = fuzz_threshold
        
        # Precompute lowercase versions for efficiency
        self.target_names_lower = [name.lower() for name in self.target_names]
    
    def is_name_mentioned(self, text: str) -> bool:
        """
        Check if any target name is mentioned in the text
        
        Args:
            text: Text to search for names
            
        Returns:
            True if a target name is detected, False otherwise
        """
        if not text:
            return False
        
        text_lower = text.lower()
        
        for name, name_lower in zip(self.target_names, self.target_names_lower):
            # Strategy 1: Exact substring match (case-insensitive)
            if name_lower in text_lower:
                return True
            
            # Strategy 2: Fuzzy partial ratio for handling variants, accents, misspellings
            if fuzz.partial_ratio(name_lower, text_lower) >= self.fuzz_threshold:
                return True
        
        return False
    
    def find_mentioned_names(self, text: str) -> List[str]:
        """
        Find which specific names were mentioned
        
        Args:
            text: Text to search for names
            
        Returns:
            List of detected target names
        """
        if not text:
            return []
        
        text_lower = text.lower()
        mentioned = []
        
        for name, name_lower in zip(self.target_names, self.target_names_lower):
            # Check exact match
            if name_lower in text_lower:
                mentioned.append(name)
                continue
            
            # Check fuzzy match
            if fuzz.partial_ratio(name_lower, text_lower) >= self.fuzz_threshold:
                mentioned.append(name)
        
        return mentioned
    
    def update_names(self, new_names: List[str]):
        """
        Update the list of target names to detect
        
        Args:
            new_names: New list of names to detect
        """
        self.target_names = [name.strip() for name in new_names if name.strip()]
        self.target_names_lower = [name.lower() for name in self.target_names]
    
    def update_threshold(self, new_threshold: int):
        """
        Update the fuzzy matching threshold
        
        Args:
            new_threshold: New threshold value (0-100)
        """
        if 0 <= new_threshold <= 100:
            self.fuzz_threshold = new_threshold
        else:
            raise ValueError("Threshold must be between 0 and 100")
    
    def __repr__(self) -> str:
        return f"NameDetector(names={self.target_names}, threshold={self.fuzz_threshold})"
