# built-in modules
import re

# pip modules
import nltk
from nltk.corpus import stopwords
from nltk.tokenize import sent_tokenize
import numpy as np
import networkx as nx


nltk.download("punkt")
nltk.download("stopwords")


class Summarizer:
    def __init__(self):
        self.stop_words = set(stopwords.words("english"))
        # Add financial domain-specific stop words
        self.financial_stop_words = {"company", "market", "stock", "share", "price"}
        self.stop_words.update(self.financial_stop_words)

        # Finance-related keywords to weight sentences
        self.finance_keywords = {
            "profit",
            "revenue",
            "earnings",
            "growth",
            "dividend",
            "inflation",
            "interest rate",
            "investment",
            "market",
            "stocks",
            "shares",
            "acquisition",
            "merger",
            "quarterly",
            "fiscal",
            "debt",
            "assets",
            "liabilities",
            "bearish",
            "bullish",
            "recession",
            "GDP",
            "economy",
            "portfolio",
            "volatility",
        }

        # Social sharing text patterns to remove
        self.sharing_patterns = [
            r"Share\s+Share\s+Facebook\s+Copy\s+Link\s+copied\s+Print\s+Email\s+X\s+LinkedIn",
            r"Share on (Facebook|Twitter|LinkedIn|Email)",
            r"(Like|Follow) us on (Facebook|Twitter|LinkedIn)",
            r"Click to share on \w+",
            r"Copyright © \d{4}.*All rights reserved",
        ]

    def clean_article_text(self, text):
        """Remove social sharing text and clean the article"""
        cleaned_text = text

        # Remove social sharing patterns
        for pattern in self.sharing_patterns:
            cleaned_text = re.sub(pattern, "", cleaned_text, flags=re.IGNORECASE)

        # Remove extra whitespace
        cleaned_text = re.sub(r"\s+", " ", cleaned_text).strip()

        return cleaned_text

    def preprocess_text(self, text):
        """Clean the text by removing special characters and normalizing"""
        text = re.sub(r"\s+", " ", text)  # Replace multiple spaces with single space
        text = re.sub(r"[^\w\s]", "", text)  # Remove punctuation
        return text.lower()

    def tokenize_sentences(self, text):
        """Split text into sentences"""
        return sent_tokenize(text)

    def create_similarity_matrix(self, sentences):
        """Create similarity matrix between sentences"""
        n = len(sentences)
        similarity_matrix = np.zeros((n, n))

        for i in range(n):
            for j in range(n):
                if i != j:
                    # Calculate similarity based on word overlap
                    similarity_matrix[i][j] = self._sentence_similarity(
                        sentences[i], sentences[j]
                    )

        return similarity_matrix

    def _sentence_similarity(self, sent1, sent2):
        """Calculate similarity between two sentences"""
        # Clean and tokenize
        sent1 = self.preprocess_text(sent1)
        sent2 = self.preprocess_text(sent2)

        words1 = [word for word in sent1.split() if word not in self.stop_words]
        words2 = [word for word in sent2.split() if word not in self.stop_words]

        # Count finance keywords in each sentence to add weight
        finance_weight1 = sum(
            1 for word in words1 if any(kw in word for kw in self.finance_keywords)
        )
        finance_weight2 = sum(
            1 for word in words2 if any(kw in word for kw in self.finance_keywords)
        )

        # Create sets for intersection calculation
        words1_set = set(words1)
        words2_set = set(words2)

        # Calculate Jaccard similarity
        if len(words1_set) == 0 or len(words2_set) == 0:
            return 0

        intersection = words1_set.intersection(words2_set)
        union = words1_set.union(words2_set)
        jaccard = len(intersection) / len(union)

        # Boost similarity if both sentences contain finance keywords
        finance_boost = 0.1 * (finance_weight1 + finance_weight2)

        return min(jaccard + finance_boost, 1.0)

    def text_rank(self, text, top_n=5):
        """Apply TextRank algorithm to extract top sentences"""
        # Clean the article text first
        cleaned_text = self.clean_article_text(text)

        # Tokenize text into sentences
        sentences = self.tokenize_sentences(cleaned_text)
        if len(sentences) <= top_n:
            return sentences

        # Create similarity matrix
        similarity_matrix = self.create_similarity_matrix(sentences)

        # Create graph and apply PageRank
        nx_graph = nx.from_numpy_array(similarity_matrix)
        scores = nx.pagerank(nx_graph)

        # Add extra weight to sentences with finance keywords
        for i, sentence in enumerate(sentences):
            clean_sent = self.preprocess_text(sentence)
            words = clean_sent.split()
            finance_terms = sum(
                1 for word in words if any(kw in word for kw in self.finance_keywords)
            )
            scores[i] = scores[i] * (1 + (0.1 * finance_terms))

        # Rank sentences by score
        ranked_sentences = sorted(
            ((scores[i], sentence) for i, sentence in enumerate(sentences)),
            reverse=True,
        )

        # Return top n sentences
        return [sentence for _, sentence in ranked_sentences[:top_n]]

    def summarize(self, text, top_n=5):
        """Main method to summarize article text"""
        summary = self.text_rank(text, top_n)
        return summary
