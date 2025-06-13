# built-in modules
import re

# pip modules
import requests
import spacy

nlp = spacy.load("en_core_web_lg")


class TickerValidator:
    def __init__(self):
        """
        Initialize the ticker validator with optional ticker data

        Parameters:
        ticker_data_path (str): Path to CSV file containing ticker data
        """
        self.company_to_ticker = {}
        self.ticker_to_company = {}
        self.all_tickers = set()

        # Social sharing text patterns to remove
        self.sharing_patterns = [
            r"Share\s+Share\s+Facebook\s+Copy\s+Link\s+copied\s+Print\s+Email\s+X\s+LinkedIn",
            r"Share on (Facebook|Twitter|LinkedIn|Email)",
            r"(Like|Follow) us on (Facebook|Twitter|LinkedIn)",
            r"Click to share on \w+",
            r"Copyright © \d{4}.*All rights reserved",
            r"Trump",
        ]

        # API endpoint for ticker validation
        self.api_url = "https://stockanalysis.com/api/screener/s/f?m=s&s=desc&c=s,n&sc=industry&cn=6000&p=1&i=stocks"

        self.fetch_ticker_data_from_api()

    def clean_article_text(self, text):
        """Remove social sharing text and clean the article"""
        cleaned_text = text

        # Remove social sharing patterns
        for pattern in self.sharing_patterns:
            cleaned_text = re.sub(pattern, "", cleaned_text, flags=re.IGNORECASE)

        # Remove extra whitespace
        cleaned_text = re.sub(r"\s+", " ", cleaned_text).strip()

        return cleaned_text

    def fetch_ticker_data_from_api(self):
        """
        Fetch ticker data from the stock analysis API
        """
        try:
            # Make API request
            response = requests.get(self.api_url)

            # Check if request was successful
            if response.status_code == 200:
                data = response.json()

                # Process ticker data
                if "data" in data and "data" in data["data"]:
                    ticker_data = data["data"]["data"]

                    # Clear existing data
                    self.company_to_ticker = {}
                    self.ticker_to_company = {}
                    self.all_tickers = set()

                    # Process each ticker entry
                    for entry in ticker_data:
                        ticker = entry["s"]
                        company_name = entry["n"]

                        # Store data in dictionaries
                        self.company_to_ticker[company_name] = ticker
                        self.ticker_to_company[ticker] = company_name
                        self.all_tickers.add(ticker)

                        # Handle shortened company names without Inc, Corp, etc.
                        shortened_name = self._get_shortened_company_name(company_name)
                        if shortened_name and shortened_name != company_name:
                            self.company_to_ticker[shortened_name] = ticker

                    print(
                        f"Successfully loaded {len(self.all_tickers)} tickers from API"
                    )
                else:
                    print("Unexpected API response format")
                    self._load_fallback_data()
            else:
                print(f"API request failed with status code: {response.status_code}")
                self._load_fallback_data()

        except Exception as e:
            print(f"Error fetching ticker data from API: {e}")
            self._load_fallback_data()

    def _get_shortened_company_name(self, company_name):
        """
        Extract shortened company name by removing suffixes like Inc., Corp., etc.
        """
        suffixes = [
            " Inc.",
            " Inc",
            " Corporation",
            " Corp.",
            " Corp",
            " Company",
            " Co.",
            " Co",
            " & Co.",
            " & Co",
            " Ltd.",
            " Ltd",
            " Limited",
            " LLC",
            " Group",
        ]

        shortened = company_name
        for suffix in suffixes:
            if company_name.endswith(suffix):
                shortened = company_name[: -len(suffix)]
                break

        return shortened.strip()

    def is_valid_ticker(self, ticker):
        """
        Check if a ticker is valid by checking against API data

        Parameters:
        ticker (str): The ticker symbol to validate

        Returns:
        bool: True if ticker is valid, False otherwise
        """

        ticker = ticker.strip().upper()

        if ticker in self.all_tickers:
            return True

        if not re.match(r"^[A-Z]{1,5}$", ticker):
            return False

        return False

    def identify_companies(self, text):
        """
        Identify company names in text using SpaCy's NER

        Parameters:
            text (str): Text to analyze

        Returns:
            list: List of identified company entities
        """
        # First clean the text to remove sharing buttons and metadata
        cleaned_text = self.clean_article_text(text)

        doc = nlp(cleaned_text)
        companies = []

        # Extract organizations using SpaCy's NER
        for ent in doc.ents:
            if ent.label_ == "ORG" and len(ent.text) > 2:
                companies.append(
                    {
                        "name": ent.text,
                        "start": ent.start_char,
                        "end": ent.end_char,
                    }
                )

        # Additionally check our predefined list for any companies not caught by NER
        for company_name in self.company_to_ticker.keys():
            # Skip very short company names to avoid false positives
            if len(company_name) <= 2:
                continue

            # Use regex to find whole word matches
            pattern = r"\b" + re.escape(company_name) + r"\b"
            matches = re.finditer(pattern, cleaned_text)

            for match in matches:
                # Check if this match overlaps with any existing company
                overlap = False
                for company in companies:
                    if (
                        match.start() >= company["start"]
                        and match.start() < company["end"]
                    ) or (
                        match.end() > company["start"] and match.end() <= company["end"]
                    ):
                        overlap = True
                        break

                if not overlap:
                    companies.append(
                        {
                            "name": match.group(),
                            "start": match.start(),
                            "end": match.end(),
                        }
                    )

        # Sort companies by their position in text
        companies.sort(key=lambda x: x["start"])
        return companies

    def match_companies_to_tickers(self, companies):
        """
        Match identified company names to their tickers

        Parameters:
            companies (list): List of company dictionaries from identify_companies

        Returns:
            list: List of companies with ticker info added
        """
        for company in companies:
            # Skip if ticker is already added (from direct ticker identification)
            if "ticker" in company and company["ticker"]:
                # Validate the ticker is still valid
                if self.is_valid_ticker(company["ticker"]):
                    continue

            name = company["name"]
            if self._get_shortened_company_name(name) in self.company_to_ticker:
                ticker = self.company_to_ticker[name]
                if self.is_valid_ticker(ticker):
                    company["ticker"] = ticker
                    company["ticker_source"] = "exact_match"
                    continue

            # Try to find the closest match if no exact match
            best_match = None
            best_score = 0

            for company_name in self.company_to_ticker:
                # Using simple containment for now
                if company_name in name or name in company_name:
                    score = len(
                        set(company_name.lower().split()) & set(name.lower().split())
                    )
                    if score > best_score:
                        best_score = score
                        best_match = company_name

            if best_match and best_score > 0:
                ticker = self.company_to_ticker[best_match]
                if self.is_valid_ticker(ticker):
                    company["ticker"] = ticker
                    company["matched_to"] = best_match
                    company["ticker_source"] = "partial_match"
                else:
                    company["ticker"] = None
            else:
                company["ticker"] = None

        return companies

    def analyze_company_context(self, text, companies):
        """
        Analyze the context around mentioned companies using dependency parsing

        Parameters:
            text (str): Text to analyze
            companies (list): List of company dictionaries with position info

        Returns:
            list: List of companies with contextual analysis
        """
        # Clean the text first
        cleaned_text = self.clean_article_text(text)
        doc = nlp(cleaned_text)

        # Map each token's position back to the original text
        token_to_char = {}
        for token in doc:
            token_to_char[token.i] = (token.idx, token.idx + len(token.text))

        # For each company, find sentences mentioning it and analyze the context
        for company in companies:
            company_start = company["start"]
            company_end = company["end"]

            # Find all sentences mentioning this company
            relevant_sentences = []
            for sent in doc.sents:
                sent_start = sent[0].idx
                sent_end = sent[-1].idx + len(sent[-1].text)

                if (company_start >= sent_start and company_start < sent_end) or (
                    company_end > sent_start and company_end <= sent_end
                ):
                    relevant_sentences.append(sent)

            company["mentions"] = []

            for sent in relevant_sentences:
                # Find the token(s) corresponding to the company name
                company_tokens = []
                for token in sent:
                    token_start = token.idx
                    token_end = token.idx + len(token.text)

                    if (token_start >= company_start and token_start < company_end) or (
                        token_end > company_start and token_end <= company_end
                    ):
                        company_tokens.append(token)

                if not company_tokens:
                    continue

                # Find financial verbs and descriptors connected to the company
                financial_actions = self.extract_financial_actions(sent, company_tokens)

                company["mentions"].append(
                    {"sentence": sent.text, "financial_actions": financial_actions}
                )

        return companies

    def extract_financial_actions(self, sentence, company_tokens):
        """
        Extract financial actions related to a company in a sentence

        Parameters:
            sentence (spacy.tokens.span.Span): SpaCy sentence span
            company_tokens (list): List of tokens representing the company

        Returns:
            list: Financial actions and their related entities
        """
        financial_actions = []

        # Define financial action verbs to look for
        financial_verbs = {
            "report",
            "announce",
            "increase",
            "decrease",
            "rise",
            "fall",
            "grow",
            "shrink",
            "launch",
            "acquire",
            "merge",
            "sell",
            "buy",
            "invest",
            "develop",
            "release",
            "cut",
            "raise",
            "expand",
            "reduce",
        }

        # Financial metrics and terms to look for
        financial_metrics = {
            "profit",
            "revenue",
            "sales",
            "earnings",
            "income",
            "margin",
            "share",
            "stock",
            "price",
            "dividend",
            "market",
            "growth",
            "quarter",
            "fiscal",
            "year",
            "forecast",
            "outlook",
            "guidance",
        }

        # Look for connections between company tokens and financial terms
        for token in sentence:
            # Check if the token is a relevant financial verb
            if (
                token.dep_ in {"nsubj", "dobj"}
                and token.lemma_.lower() in financial_verbs
            ):
                # Find connections to company tokens
                is_connected = False
                for company_token in company_tokens:
                    if self._are_tokens_connected(token, company_token):
                        is_connected = True
                        break

                if is_connected:
                    # Extract the subject, object, and modifiers of this verb
                    action = {
                        "verb": token.text,
                        "phrase": self._extract_phrase_around_token(token),
                    }

                    # Extract financial metrics associated with this verb
                    metrics = []
                    for child in token.children:
                        if (
                            child.text.lower() in financial_metrics
                            or child.lemma_.lower() in financial_metrics
                        ):
                            metrics.append(
                                {
                                    "metric": child.text,
                                    "phrase": self._extract_phrase_around_token(child),
                                }
                            )

                        # Look for numbers and percentages
                        if child.pos_ == "NUM" or "%" in child.text:
                            metrics.append(
                                {
                                    "value": child.text,
                                    "phrase": self._extract_phrase_around_token(child),
                                }
                            )

                    if metrics:
                        action["metrics"] = metrics

                    financial_actions.append(action)

        return financial_actions

    def _are_tokens_connected(self, token1, token2):
        """Check if two tokens are connected in the dependency tree"""
        # Check if token1 is an ancestor of token2
        if token1 in [t for t in token2.ancestors]:
            return True

        # Check if token2 is an ancestor of token1
        if token2 in [t for t in token1.ancestors]:
            return True

        # Check if they share a direct dependency
        for child in token1.children:
            if child == token2 or child in [t for t in token2.ancestors]:
                return True

        for child in token2.children:
            if child == token1 or child in [t for t in token1.ancestors]:
                return True

        return False

    def _extract_phrase_around_token(self, token, window=3):
        """Extract a phrase around a token to provide context"""
        start_idx = max(0, token.i - window)
        end_idx = min(len(token.doc), token.i + window + 1)

        return token.doc[start_idx:end_idx].text

    def validate(self, text):
        """
        Main method to validate tickers in news text

        Parameters:
            text (str): Financial news text

        Returns:
            dict: Analysis results including companies, tickers, and context
        """
        # Clean the text first
        cleaned_text = self.clean_article_text(text)

        companies = self.identify_companies(cleaned_text)
        companies_with_tickers = self.match_companies_to_tickers(companies)
        companies_with_context = self.analyze_company_context(
            cleaned_text, companies_with_tickers
        )

        # Organize results
        valid_companies = []
        unknown_companies = []

        for company in companies_with_context:
            if company["ticker"]:
                valid_companies.append(company)
            else:
                unknown_companies.append(company)

        # Create a summary of the analysis
        summary = {
            "identified_companies": len(companies),
            "matched_tickers": len(valid_companies),
            "unmatched_entities": len(unknown_companies),
            "validated_companies": valid_companies,
            "unknown_entities": unknown_companies,
        }

        return summary
