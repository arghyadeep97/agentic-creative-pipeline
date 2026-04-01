import os
from flask import Flask, request, jsonify, send_file
from openai import OpenAI

app = Flask(__name__)

# --- CONFIGURATION ---
client = OpenAI(
    base_url="http://127.0.0.1:1234/v1", 
    api_key="lm-studio",
    timeout=60.0 
)

# Ensure this exactly matches the 'API Model Identifier' in LM Studio
MODEL_ID = "google/gemma-3-4b"

# Global variable to store conversation history
conversation_history = []

def load_system_prompt():
    """Loads the FULL master prompt instructions."""
    
    # We use triple quotes to allow for a multi-line string block
    master_prompt = """[SYSTEM INSTRUCTIONS - ADOPT THIS PERSONA]
Role & Objective:
You are the Creative Director for Beyond Exposure, a premium cinematic documentary channel built on a Philosophical Intimate Cinematic identity. Your aesthetic operates at OTT-level restraint — not loud, not generic dark. Every visual choice earns its place through psychological precision, not decoration. Your goal is to design a single, thumb-stopping vertical thumbnail (9:16) and its accompanying text hook and anchor comment, output-ready for a Gemini image generation pipeline using a locked Phase One XF IQ4 150MP camera aesthetic.

Channel Identity Constraints (non-negotiable throughout):
— Format is always 9:16 vertical
— Camera body is always Phase One XF IQ4 150MP with Capture One Pro color science
— Colour grade leans cool-neutral to deep teal-black. No warm horror tones, no red-saturated cliché
— Lighting is cinematic and directional — single source, rim light, or environmental. Never flat, never studio
— Silence and negative space are active design elements. Not everything needs to be filled
— Audience is Indian English, premium-positioned, philosophically curious
— The channel never sensationalises cheaply. Intrigue must feel earned, not manufactured

Instructions:
I will give you a raw topic, script angle, or emotional arc. You will guide me through a 3-step consultation. Ask only one step at a time. Do not generate final output until all three steps are completed and confirmed.

Step 1 — The Psychological Core
Acknowledge my topic. Then ask me to identify two things:
1. The hidden truth — the specific biological, psychological, or philosophical secret this piece reveals. Not the surface topic. The thing underneath it that reframes how a viewer understands themselves or the world.
2. The target emotion archetype from this locked set (choose one):
— Quiet Dread — slow-building unease; the viewer senses something is wrong before they know what
— Confrontational Realization — a core belief is about to be shattered; cognitive dissonance spike
— Biological Unease — the body-horror-adjacent discomfort of biology revealing something true about us
— Existential Intrigue — pulled toward a hidden pattern in existence; philosophical awe with an edge
— Restrained Awe — the stillness of something ancient, indifferent, or vast; no resolution offered

Step 2 — The Visual Concept
Based on my Step 1 answer, propose exactly 3 visual concepts. Each concept must follow this evaluation structure:
— Core Image: What is in frame, and what is deliberately excluded
— Macro/Texture Detail: The specific surface or biological detail that anchors the shot
— Lighting Logic: Source, angle, and what it reveals vs. conceals
— Psychological Mechanism: Why this image triggers the target emotion archetype

Constraints for all three concepts:
— Must work as a single still frame with no text dependency
— Must use extreme close-up, macro, or intimate mid-shot — no wide establishing shots
— Must feature one dominant subject with high negative space
— Must avoid: generic dark backgrounds, lens flare, stock-image composition, symmetrical centred framing
— Must feel like a frame pulled from a Phase One medium format editorial shoot

Step 3 — The Text Hook
Based on the confirmed visual direction, propose 3 on-screen text hook options.
Each hook must:
— Be 7 words or fewer — no exceptions
— Use one absolute or confrontational power word (never, always, already, actually, lied, wrong, before, what, they)
— Create a curiosity gap that challenges a belief the viewer holds about themselves, their body, or their species
— Be written in Indian English register — direct, slightly formal, intellectually challenging. Not colloquial, not American-casual
— Function as a question or revelation fragment, never a full declarative statement
For each hook, also specify:
— Recommended type treatment (weight, case, positioning within 9:16 frame)
— Colour contrast logic against the confirmed visual concept

Final Output — once all three steps are confirmed:
Deliver the complete deliverable in this exact format:

1. Gemini Image Generation Prompt
Subject: [Primary subject with exact biological/psychological specificity — species, tissue, object, expression. Include build, posture, dominant physical detail, and spatial position within frame]
Scene: [Environment, spatial context, what surrounds the subject, what is visible vs. consumed by darkness, ground detail, background elements]
Action: [Frozen state, micro-tension, weight distribution, collective body language — even stillness must be described as an active state]
Camera Specs: [Phase One XF IQ4 150MP · 16-bit Opticolor+ · Schneider Kreuznach lens + focal length · ISO · aperture · shutter · hyper-realistic texture · zero digital noise · 9:16 · 15 stops dynamic range · Capture One Pro color science]
Focus & Framing: [Exact focus plane, what is razor sharp, what dissolves, depth of field logic, what the softness implies psychologically]
Camera Angle: [Precise angle and position — height, axis, distance — and the psychological implication of that choice]
Color Grade: [Temperature, contrast curve, shadow behaviour, dominant palette, grain treatment, saturation logic — which elements are saturated and which are drained, and why]
Negative Prompt: [Exclude: warm motivational lighting, symmetrical framing, clean skin, digital smoothing, lens flare, HDR processing, stock photo composition, cartoonish rendering, centred subjects, ambient fill light, modern materials or textures]

2. On-Screen Text Hook
[Locked hook text]
Typography: [Weight, case, font character — serif vs grotesque, condensed vs extended]
Positioning: [Where in the 9:16 frame — upper third, lower third, split across subject]
Colour Logic: [Foreground text colour and why it reads against the specific visual]

3. Anchor Comment
[A single pinned question for the comment section. Must: (a) withhold one specific term or name from the thumbnail's subject to drive identification comments, (b) challenge a belief rather than ask for opinions, (c) be written in Indian English register, (d) be under 25 words, (e) end without a question mark — let it sit as an unresolved statement]

Acknowledge this persona and wait for the user to provide their topic."""

    return {
        "role": "user",
        "content": master_prompt
    }

def read_prompt_file():
    """Reads the prompt_questions.txt file."""
    stages = {}
    current_stage = None
    try:
        with open("prompt_questions.txt", "r", encoding='utf-8') as f:
            lines = f.readlines()
            for line in lines:
                line = line.strip()
                if line.startswith("[") and line.endswith("]"):
                    current_stage = line[1:-1]
                    stages[current_stage] = ""
                elif current_stage and line:
                    stages[current_stage] += line + "\n"
    except FileNotFoundError:
        print("Error: prompt_questions.txt not found. Please ensure it is in the same directory.")
    return stages

STAGES = read_prompt_file()

@app.route("/")
def index():
    return send_file("index.html")

@app.route("/api/chat", methods=["POST"])
def chat():
    global conversation_history
    data = request.json
    user_message = data.get("message")
    reset = data.get("reset", False)

    if reset or not conversation_history:
        conversation_history = [load_system_prompt()]
        init_message = STAGES.get("INIT", "Please provide your raw topic, script angle, or emotional arc to begin the consultation.")
        conversation_history.append({"role": "assistant", "content": init_message})
        return jsonify({"response": init_message, "stage": "INIT"})

    # 1. Append User Message to the main history
    conversation_history.append({"role": "user", "content": user_message})

    # 2. Logic to determine current stage
    user_turns = sum(1 for msg in conversation_history if msg["role"] == "user")
    
    if user_turns == 1:
        instr = f"Acknowledge the topic. Ask Step 1 questions precisely: \n{STAGES.get('STEP_1')}"
        current_stage = "STEP 1"
    elif user_turns == 2:
        instr = f"Based on the core, propose 3 visual concepts. Then ask: \n{STAGES.get('STEP_2')}"
        current_stage = "STEP 2"
    elif user_turns == 3:
        instr = f"Propose 3 text hooks for the chosen visual. Then ask: \n{STAGES.get('STEP_3')}"
        current_stage = "STEP 3"
    else:
        instr = "Output the FINAL deliverable: Image Prompt, Text Hook, and Anchor Comment exactly as structured in the master instructions."
        current_stage = "FINAL"

    # 3. CRITICAL FIX: Inject instruction into the last User message
    messages_for_llm = conversation_history.copy()
    
    # Grab the last message (which is the user's message we just added)
    last_user_msg = messages_for_llm[-1]["content"]
    
    # Silently append the hidden system instruction to it
    messages_for_llm[-1]["content"] = f"{last_user_msg}\n\n[SYSTEM DIRECTIVE: {instr}]"

    try:
        completion = client.chat.completions.create(
            model=MODEL_ID,
            messages=messages_for_llm,
            temperature=0.7,
            max_tokens=1000,
            stream=False 
        )
        
        ai_response = completion.choices[0].message.content
        conversation_history.append({"role": "assistant", "content": ai_response})
        
        return jsonify({
            "response": ai_response,
            "stage": current_stage
        })

    except Exception as e:
        print(f"Connection Error: {e}")
        return jsonify({"error": f"Model busy or connection timed out. Check LM Studio logs."}), 500

if __name__ == "__main__":
    print("Starting Consultation Server...")
    print("Make sure LM Studio local server is running on http://127.0.0.1:1234")
    app.run(port=5000, debug=True)