import json
import re
import time
from google import genai
from google.genai import types
from config import GEMINI_API_KEY

SYSTEM_PROMPT = """You are DocuDiff Legal AI, an elite corporate attorney and legal risk analyst with deep expertise in commercial contracts.

Your goal is to review contract text, identify hidden risks or unfair terms for the reviewing party, translate complex legal jargon into Plain English, and propose balanced redlines/revisions.

ANALYSIS RULES & GUIDELINES:

1. RISK SEVERITY ASSESSMENT:
   - "HIGH": Unilateral termination rights, severe penalty fees/liquidated damages, unlimited liability or indemnification, short auto-renewal opt-out windows, waiver of jury trial/court rights, one-sided intellectual property assignment.
   - "MEDIUM": Unfavorable payment/invoice terms, strict notice periods, ambiguous obligations, moderate late fees, one-sided confidentiality terms.
   - "LOW": Standard boilerplate language, customary terms, balanced mutual rights, minor ambiguities.

2. RISK CATEGORIES:
   Assign exactly one category from this list:
   ["INDEMNIFICATION", "TERMINATION", "LIABILITY_LIMIT", "PAYMENT_TERMS", "INTELLECTUAL_PROPERTY", "CONFIDENTIALITY", "AUTORENEWAL", "GOVERNING_LAW", "OTHER"]

3. PLAIN ENGLISH EXPLANATION:
   Write 1-2 clear, punchy sentences explaining the risk so a business person or non-lawyer immediately understands the practical impact. Avoid legalese.

4. ACTIONABLE ADVICE & REVISION:
   - Actionable Advice: What concrete step or negotiation point should the user take?
   - Suggested Revision: Provide a rewritten version of the clause that mitigates the risk while remaining reasonable for both parties.

OUTPUT REQUIREMENTS:
You MUST respond strictly with a valid JSON object matching the exact structure below. Do not include markdown code block wrappers (like ```json), commentary, or intro/outro text.

EXPECTED JSON SCHEMA:
{
  "clause_id": "<clause_id_or_number>",
  "risk_level": "HIGH" | "MEDIUM" | "LOW",
  "risk_category": "<CATEGORY_NAME>",
  "risk_score": <number_between_1_and_100>,
  "key_issue": "<one_sentence_title_of_the_problem>",
  "plain_english_summary": "<simple_explanation_for_non_lawyers>",
  "actionable_advice": "<what_to_do_or_negotiate>",
  "suggested_revision": "<redlined_or_rewritten_clause_text>"
}"""

FALLBACK_MODELS = [
    "gemini-3.5-flash",
    "gemini-3.8-flash",
    "gemini-flash-latest",
    "gemini-3.1-flash-lite",
    "gemini-2.5-flash-lite",
]


def _call_model(client, model: str, user_message: str) -> str:
    """Single attempt to call a specific model. Returns raw response text."""
    response = client.models.generate_content(
        model=model,
        contents=user_message,
        config=types.GenerateContentConfig(
            system_instruction=SYSTEM_PROMPT,
            temperature=0.2,
            response_mime_type="application/json",
        ),
    )
    return response.text.strip()


def analyze_clause(
    clause_id: str,
    clause_title: str,
    clause_text: str,
    language: str = "en",
    stance: str = "balanced"
) -> dict:
    """
    Sends a contract clause to Gemini and returns a structured risk analysis dict.
    Supports language selection ('en' or 'tr') and reviewer stance ('balanced', 'buyer', 'vendor').
    """
    if not GEMINI_API_KEY or GEMINI_API_KEY == "your_gemini_api_key_here":
        raise ValueError(
            "GEMINI_API_KEY is not set. Please open the .env file and configure your API key."
        )

    client = genai.Client(api_key=GEMINI_API_KEY)

    # Perspective stance modifier
    stance_notes = {
        "buyer": "Reviewer Stance: Review strictly from the perspective of a BUYER / CLIENT. Aggressively flag one-sided vendor protections, automatic fee increases, and harsh penalties against the customer.",
        "vendor": "Reviewer Stance: Review strictly from the perspective of a VENDOR / SERVICE PROVIDER. Ensure intellectual property protection, reasonable payment timing, limited liability exposure, and protection against arbitrary client termination.",
        "balanced": "Reviewer Stance: Review as a balanced corporate counsel seeking commercially reasonable and fair terms for both parties."
    }.get(stance, "Reviewer Stance: Review as a balanced corporate counsel.")

    # Language modifier
    if language == "tr":
        lang_note = (
            "LANGUAGE REQUIREMENT: Output the values of 'key_issue', 'plain_english_summary', "
            "'actionable_advice', and 'suggested_revision' entirely in TURKISH. "
            "Keep the JSON keys, 'risk_level' ('HIGH'/'MEDIUM'/'LOW'), and 'risk_category' in English."
        )
    else:
        lang_note = "LANGUAGE REQUIREMENT: Output all summaries, advice, and revisions in ENGLISH."

    user_message = (
        f"Analyze the following contract clause:\n\n"
        f"Clause ID: {clause_id}\n"
        f"Clause Title: {clause_title}\n"
        f"{stance_notes}\n"
        f"{lang_note}\n\n"
        f'Clause Text:\n"""\n{clause_text}\n"""'
    )

    last_error = None

    for model in FALLBACK_MODELS:
        for attempt in range(2):
            try:
                raw_text = _call_model(client, model, user_message)

                raw_text = re.sub(r"^```(?:json)?\s*", "", raw_text)
                raw_text = re.sub(r"\s*```$", "", raw_text)

                result = json.loads(raw_text)
                result["clause_id"] = clause_id
                result["_model_used"] = model
                return result

            except json.JSONDecodeError as e:
                raise RuntimeError(
                    f"AI returned invalid JSON using {model}: {e}\n\nRaw: {raw_text}"
                )
            except Exception as e:
                err_str = str(e)
                last_error = e

                if "503" in err_str or "UNAVAILABLE" in err_str:
                    if attempt == 0:
                        time.sleep(1.5)
                    else:
                        break
                elif "404" in err_str or "NOT_FOUND" in err_str:
                    break
                elif "400" in err_str or "INVALID" in err_str:
                    raise RuntimeError(f"Invalid request: {err_str}")
                elif "401" in err_str or "403" in err_str or "API_KEY" in err_str:
                    raise ValueError(
                        "API key is invalid or unauthorized. Please verify your GEMINI_API_KEY."
                    )
                else:
                    raise RuntimeError(f"Unexpected API error with {model}: {err_str}")

    raise RuntimeError(
        "All Gemini models are currently experiencing high demand. Please try again in a few moments."
    )
