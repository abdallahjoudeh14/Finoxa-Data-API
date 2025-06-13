# pip modules
import torch
import torch.nn.functional as F
from transformers import AutoTokenizer, AutoModelForSequenceClassification


class Prediction:
    def __init__(self, model_path: str):
        self._model_path = model_path
        self._tokenizer = AutoTokenizer.from_pretrained(model_path)
        self._model = AutoModelForSequenceClassification.from_pretrained(model_path)
        self._labels = ["Neutral", "Positive", "Negative"]

    def _compute_sentiment_score(self, probabilities: dict) -> float:
        label_weights = {"Negative": -1, "Neutral": 0, "Positive": 1}
        score = sum(
            probabilities[label] * weight for label, weight in label_weights.items()
        )
        return round(score, 4)

    def predict(self, sentence: str) -> dict:
        inputs = self._tokenizer(
            sentence,
            return_tensors="pt",
            truncation=True,
            padding=True,
            max_length=512,
        )

        with torch.no_grad():
            outputs = self._model(**inputs)
            probs = F.softmax(outputs.logits, dim=-1)
            prediction = torch.argmax(probs, dim=-1).item()
            confidence = probs[0][prediction].item()

        sentiment = self._labels[prediction]

        prob_dict = {
            self._labels[i]: probs[0][i].item() for i in range(len(self._labels))
        }
        sentiment_score = self._compute_sentiment_score(prob_dict)

        return {
            "sentiment": sentiment,
            "score": sentiment_score,
            "confidence": round(confidence, 4),
            "probabilities": {
                self._labels[i]: round(p.item(), 4) for i, p in enumerate(probs[0])
            },
        }
