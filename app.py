"""Flask web application for AI Tarot Divination System."""
import os
from flask import Flask, render_template, jsonify, request

from dotenv import load_dotenv
from src.models.spread import SpreadType
from src.services.reading import ReadingService
from src.services.ai_interpreter import AIInterpreter

load_dotenv()

app = Flask(__name__)
app.secret_key = os.getenv("SECRET_KEY", "tarot-secret-key-change-in-production")

reading_service = ReadingService()
ai_interpreter = None


def get_ai_interpreter():
    """Create the AI interpreter lazily so the site can run before API setup."""
    global ai_interpreter
    if ai_interpreter is None:
        ai_interpreter = AIInterpreter()
    return ai_interpreter


@app.route("/")
def index():
    """Render the main page."""
    return render_template("index.html")


@app.route("/healthz")
def healthz():
    """Health check endpoint for deployment platforms."""
    return jsonify({"success": True, "status": "ok"})


@app.route("/api/deck", methods=["GET"])
def get_deck():
    """Get all 78 tarot cards info (for display in non-blind mode only)."""
    try:
        deck_info = reading_service.get_deck_info()
        return jsonify({"success": True, "cards": deck_info})
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500


@app.route("/api/spreads", methods=["GET"])
def get_spreads():
    """Get spread metadata for the front end."""
    try:
        return jsonify({"success": True, "spreads": reading_service.get_spread_info()})
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500


@app.route("/api/daily_card", methods=["GET"])
def get_daily_card():
    """Get a deterministic daily card for the current date."""
    try:
        card = reading_service.get_daily_card()
        advice = ""
        try:
            advice = get_ai_interpreter().generate_daily_advice(card) or ""
        except Exception:
            pass
        return jsonify({"success": True, "card": card, "advice": advice})
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500


@app.route("/api/shuffle", methods=["POST"])
def shuffle_deck():
    """Shuffle the deck for blind drawing."""
    try:
        reading_service.shuffle_deck()
        return jsonify({"success": True, "message": "Deck shuffled"})
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500


@app.route("/api/blind_deck", methods=["GET"])
def get_blind_deck():
    """Get blind deck (face-down cards for manual selection)."""
    try:
        blind_deck = reading_service.get_blind_deck()
        return jsonify({"success": True, "cards": blind_deck})
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500


@app.route("/api/draw", methods=["POST"])
def draw_cards():
    """Draw cards either manually (blind) or automatically."""
    try:
        data = request.get_json()
        mode = data.get("mode", "auto")
        spread_type_str = data.get("spread_type", "single_card")

        try:
            spread_type = SpreadType[spread_type_str.upper()]
        except KeyError:
            return jsonify({"success": False, "error": "Invalid spread type"}), 400

        if mode == "manual":
            # Manual mode uses blind_ids (positions in shuffled deck)
            blind_ids = data.get("blind_ids", [])
            if not blind_ids:
                return jsonify({"success": False, "error": "blind_ids required for manual mode"}), 400

            # Reveal cards from blind selections
            cards_data, positions_data = reading_service.reveal_cards(blind_ids)

            return jsonify({
                "success": True,
                "cards": cards_data,
                "positions": positions_data,
                "mode": "manual"
            })
        else:
            # Auto mode
            count = data.get("count", 1)
            cards_data, positions_data = reading_service.draw_cards_auto(spread_type, count)
            return jsonify({
                "success": True,
                "cards": cards_data,
                "positions": positions_data,
                "mode": "auto"
            })

    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500


@app.route("/api/interpret", methods=["POST"])
def interpret_cards():
    """Get AI interpretation for drawn cards."""
    try:
        data = request.get_json()
        cards = data.get("cards", [])
        positions = data.get("positions", [])
        question = data.get("question", "")
        topic = data.get("topic", "general")
        tone = data.get("tone", "warm")
        spread_type = data.get("spread_type", "single_card")

        if not cards:
            return jsonify({"success": False, "error": "No cards provided"}), 400
        if len(question) < 5:
            return jsonify({"success": False, "error": "Question too short (min 5 chars)"}), 400

        interpretation = get_ai_interpreter().interpret(cards, positions, question, spread_type, topic, tone)
        return jsonify({"success": True, "interpretation": interpretation})

    except ValueError as e:
        return jsonify({"success": False, "error": str(e)}), 400
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500


@app.route("/api/journal_reflect", methods=["POST"])
def journal_reflect():
    """Get an AI companion response for a private tarot journal entry."""
    try:
        data = request.get_json() or {}
        journal_text = data.get("text", "").strip()
        daily_card = data.get("daily_card") or {}
        topic = data.get("topic", "自我")

        if len(journal_text) < 4:
            return jsonify({"success": False, "error": "Journal text too short"}), 400

        response = get_ai_interpreter().generate_journal_response(journal_text, daily_card, topic)
        return jsonify({"success": True, "response": response})

    except ValueError as e:
        return jsonify({"success": False, "error": str(e)}), 400
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500


if __name__ == "__main__":
    port = int(os.getenv("PORT", 5000))
    debug = os.getenv("FLASK_DEBUG", "true").lower() == "true"
    app.run(host="0.0.0.0", port=port, debug=debug)
