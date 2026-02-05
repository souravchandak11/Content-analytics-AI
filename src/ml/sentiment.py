"""
Content Analytics Platform - Sentiment Analysis
================================================
NLP-based sentiment analysis for comments and captions.
"""

import os
import re
from typing import Dict, List, Optional, Any, Tuple

import nltk
from loguru import logger

# Download required NLTK data
try:
    nltk.data.find('vader_lexicon')
except LookupError:
    nltk.download('vader_lexicon', quiet=True)

try:
    nltk.data.find('stopwords')
except LookupError:
    nltk.download('stopwords', quiet=True)

try:
    nltk.data.find('punkt')
except LookupError:
    nltk.download('punkt', quiet=True)

from nltk.sentiment.vader import SentimentIntensityAnalyzer
from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize


class SentimentAnalyzer:
    """
    Sentiment analysis for social media text.
    
    Uses VADER (Valence Aware Dictionary for Sentiment Reasoning)
    which is specifically tuned for social media text.
    """
    
    def __init__(self):
        """Initialize sentiment analyzer."""
        self.vader = SentimentIntensityAnalyzer()
        self.stop_words = set(stopwords.words('english'))
    
    def analyze_text(self, text: str) -> Dict[str, Any]:
        """
        Analyze sentiment of text.
        
        Args:
            text: Text to analyze
            
        Returns:
            Sentiment analysis results
        """
        if not text or not text.strip():
            return {
                'score': 0.0,
                'label': 'neutral',
                'confidence': 0.0,
                'positive': 0.0,
                'negative': 0.0,
                'neutral': 1.0
            }
        
        # Clean text
        cleaned = self._clean_text(text)
        
        # Get VADER scores
        scores = self.vader.polarity_scores(cleaned)
        
        # Determine label
        compound = scores['compound']
        if compound >= 0.05:
            label = 'positive'
        elif compound <= -0.05:
            label = 'negative'
        else:
            label = 'neutral'
        
        # Calculate confidence
        confidence = abs(compound)
        
        return {
            'score': round(compound, 4),
            'label': label,
            'confidence': round(confidence, 4),
            'positive': round(scores['pos'], 4),
            'negative': round(scores['neg'], 4),
            'neutral': round(scores['neu'], 4)
        }
    
    def analyze_comments(
        self, 
        comments: List[Dict]
    ) -> Dict[str, Any]:
        """
        Analyze sentiment of multiple comments.
        
        Args:
            comments: List of comment dictionaries with 'text' key
            
        Returns:
            Aggregated sentiment analysis
        """
        if not comments:
            return {
                'total_comments': 0,
                'avg_sentiment': 0.0,
                'sentiment_distribution': {'positive': 0, 'negative': 0, 'neutral': 0}
            }
        
        sentiments = []
        distribution = {'positive': 0, 'negative': 0, 'neutral': 0}
        
        for comment in comments:
            text = comment.get('text', '')
            result = self.analyze_text(text)
            sentiments.append(result['score'])
            distribution[result['label']] += 1
        
        total = len(comments)
        avg_sentiment = sum(sentiments) / total if total > 0 else 0
        
        # Calculate overall mood
        if avg_sentiment > 0.2:
            overall_mood = 'very_positive'
        elif avg_sentiment > 0.05:
            overall_mood = 'positive'
        elif avg_sentiment < -0.2:
            overall_mood = 'very_negative'
        elif avg_sentiment < -0.05:
            overall_mood = 'negative'
        else:
            overall_mood = 'neutral'
        
        return {
            'total_comments': total,
            'avg_sentiment': round(avg_sentiment, 4),
            'overall_mood': overall_mood,
            'sentiment_distribution': distribution,
            'positive_ratio': round(distribution['positive'] / total * 100, 1),
            'negative_ratio': round(distribution['negative'] / total * 100, 1),
            'neutral_ratio': round(distribution['neutral'] / total * 100, 1)
        }
    
    def extract_topics(
        self, 
        texts: List[str],
        top_n: int = 10
    ) -> List[Tuple[str, int]]:
        """
        Extract common topics/keywords from texts.
        
        Args:
            texts: List of text strings
            top_n: Number of top topics to return
            
        Returns:
            List of (topic, count) tuples
        """
        word_freq = {}
        
        for text in texts:
            words = word_tokenize(self._clean_text(text).lower())
            
            for word in words:
                if (len(word) > 2 and 
                    word not in self.stop_words and 
                    word.isalpha()):
                    word_freq[word] = word_freq.get(word, 0) + 1
        
        sorted_words = sorted(word_freq.items(), key=lambda x: x[1], reverse=True)
        return sorted_words[:top_n]
    
    def _clean_text(self, text: str) -> str:
        """Clean text for analysis."""
        # Remove URLs
        text = re.sub(r'http\S+|www\S+', '', text)
        # Remove mentions
        text = re.sub(r'@\w+', '', text)
        # Remove hashtags but keep the word
        text = re.sub(r'#(\w+)', r'\1', text)
        # Remove extra whitespace
        text = ' '.join(text.split())
        return text
    
    def get_sentiment_summary(
        self,
        comments: List[Dict]
    ) -> Dict[str, Any]:
        """
        Get comprehensive sentiment summary with insights.
        
        Args:
            comments: List of comments
            
        Returns:
            Detailed sentiment summary
        """
        analysis = self.analyze_comments(comments)
        
        # Extract positive and negative samples
        positive_examples = []
        negative_examples = []
        
        for comment in comments[:100]:  # Sample first 100
            result = self.analyze_text(comment.get('text', ''))
            if result['score'] > 0.5 and len(positive_examples) < 3:
                positive_examples.append({
                    'text': comment.get('text', '')[:200],
                    'score': result['score']
                })
            elif result['score'] < -0.5 and len(negative_examples) < 3:
                negative_examples.append({
                    'text': comment.get('text', '')[:200],
                    'score': result['score']
                })
        
        # Extract topics
        texts = [c.get('text', '') for c in comments]
        topics = self.extract_topics(texts, top_n=10)
        
        analysis['top_topics'] = [{'word': w, 'count': c} for w, c in topics]
        analysis['positive_examples'] = positive_examples
        analysis['negative_examples'] = negative_examples
        
        return analysis
