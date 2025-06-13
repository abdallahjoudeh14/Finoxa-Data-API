# built-in modules
import os

# custom modules
from summarization import Summarizer
from ticker_validation import TickerValidator
from prediction import Prediction

if __name__ == "__main__":
    article = """A new U.S. rule AAPL that requires hotel and short-term lodging companies to disclose so-called “junk fees” starts Monday.  
                Announced by the Federal Trade Commission in December, the rule takes direct aim at the widely loathed charges, which can appear as “resort,” “destination” or “hospitality service” fees and purport to grant perks that travelers either don’t want or already expect to receive.  
                These include “premium” internet service and access to a hotel gym.
                The rule, which also applies to live event ticketing companies, was designed to curtail a practice that allowed businesses to charge more “without looking like you’re raising prices,” Cathy Mansfield from the Case Western Reserve Law School told CNBC in December.  
                The professor, who specializes in consumer and commercial law, had one caveat: “I really hope the Trump administration doesn’t cut the enforcement staff at the FTC and the CFPB.”"""

    model_path = f"{os.getcwd()}/ml-model/models/finoxa_model"

    summarizer = Summarizer()
    validator = TickerValidator()
    prediction = Prediction(model_path)

    summary_sentences = summarizer.summarize(article, top_n=15)

    results = []

    for sentence in summary_sentences:
        ticker_info = validator.validate(sentence)
        if ticker_info.get("validated_companies"):
            if len(ticker_info["validated_companies"]):
                if (
                    ticker_info["validated_companies"][0]["ticker_source"]
                    == "exact_match"
                ):
                    results.append(
                        {
                            "sentence": sentence,
                            "tickers": ticker_info["validated_companies"][0],
                        }
                    )

    # Classify sentiment for each sentence
    for item in results:
        sentiment_info = prediction.predict(item["sentence"])
        sentiment = sentiment_info["sentiment"]
        sentiment_score = sentiment_info["score"]
        sentiment_probabilities = sentiment_info["probabilities"]

        print(f"Sentence: {item['sentence']}")
        print(f"Ticker: {item['tickers']["ticker"]}")
        print(f"Company: {item['tickers']["name"]}")
        print(f"Sentiment: {sentiment}")
        print(f"Sentiment Score: {sentiment_score}")
