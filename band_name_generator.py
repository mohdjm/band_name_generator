import streamlit as st
import random
import google.generativeai as genai # For AI generation

# --- Configuration for Gemini API ---
# IMPORTANT: Replace 'YOUR_GEMINI_API_KEY' with your actual Gemini API key.
# For production apps, consider using Streamlit Secrets (st.secrets) for security.
# Example: api_key = st.secrets["gemini_api_key"]
# You can get an API key from Google AI Studio: https://aistudio.google.com/app/apikey
GEMINI_API_KEY = "" # Leave empty for Canvas environment, it will be provided at runtime
genai.configure(api_key=GEMINI_API_KEY)

# Initialize the Gemini model
# Using 'gemini-pro' for text generation, as 'gemini-2.0-flash' is primarily for JS/React environments with direct fetch.
model = genai.GenerativeModel('gemini-pro')

# --- Predefined lists for more diverse name generation ---
ADJECTIVES = ['Electric', 'Mystic', 'Silent', 'Crimson', 'Midnight', 'Whispering', 'Echoing', 'Velvet', 'Cosmic', 'Ancient']
NOUNS = ['Riders', 'Shadows', 'Wolves', 'Dreams', 'Visions', 'Outlaws', 'Rebels', 'Nomads', 'Voyagers', 'Guardians']
SUFFIXES = ['Band', 'Collective', 'Orchestra', 'Project', 'Crew', 'Ensemble', 'Syndicate', 'Vibe', 'Machine', 'Unit']

# --- Function to generate band names ---
def generate_band_names(city, pet_name, favorite_color, genre):
    """
    Generates a list of band names based on user inputs.
    Includes rule-based suggestions and AI-powered suggestions.
    """
    generated = []

    # Basic validation (Streamlit's required fields handle some of this, but good for logic)
    if not city.strip() or not pet_name.strip():
        return [] # Return empty if essential inputs are missing

    # --- Generate rule-based band names ---
    # 1. Original style
    generated.append(f"{city} {pet_name}")

    # 2. Pet name with a random adjective
    random_adj = random.choice(ADJECTIVES)
    generated.append(f"{random_adj} {pet_name}s")

    # 3. City with a random noun
    random_noun = random.choice(NOUNS)
    generated.append(f"{city} {random_noun}")

    # 4. Color + Pet Name (if color is provided)
    if favorite_color.strip():
        generated.append(f"{favorite_color} {pet_name}")

    # 5. City + Pet Name + random suffix
    random_suffix = random.choice(SUFFIXES)
    generated.append(f"{city} {pet_name} {random_suffix}")

    return list(set(generated)) # Remove duplicates and return

async def get_ai_band_names(city, pet_name, favorite_color, genre):
    """
    Fetches AI-powered band names using the Gemini API.
    """
    prompt = f"""Generate 3 unique and creative band names based on the following information:
    City: {city}
    Pet Name: {pet_name}
    Favorite Color: {favorite_color if favorite_color.strip() else 'N/A'}
    Preferred Genre: {genre if genre.strip() else 'N/A'}

    Provide only the band names, one per line. Make them sound cool and relevant to the inputs.
    """
    try:
        # Use the generate_content method for the prompt
        response = await model.generate_content_async(prompt)
        if response.candidates and response.candidates[0].content:
            ai_names = response.candidates[0].content.parts[0].text.split('\n')
            return [name.strip() for name in ai_names if name.strip()]
        else:
            st.warning("AI model did not return a valid response structure.")
            return []
    except Exception as e:
        st.error(f"Failed to get AI-powered names: {e}")
        return []

# --- Streamlit UI ---
st.set_page_config(
    page_title="Danial's Ultimate Band Name Generator",
    layout="centered",
    initial_sidebar_state="collapsed",
)

st.markdown(
    """
    <style>
    .main {
        background: linear-gradient(to bottom right, #1a202c, #000000);
        color: white;
        font-family: 'Inter', sans-serif;
    }
    .stTextInput>div>div>input {
        background-color: #2d3748;
        color: #e2e8f0;
        border: 1px solid #4a5568;
        border-radius: 0.5rem;
        padding: 0.75rem 1rem;
    }
    .stTextInput>label {
        color: #cbd5e0;
        font-weight: bold;
    }
    .stButton>button {
        background-color: #8b5cf6; /* purple-600 */
        color: white;
        font-weight: bold;
        padding: 0.75rem 1rem;
        border-radius: 0.5rem;
        transition: all 0.3s ease;
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
    }
    .stButton>button:hover {
        background-color: #7c3aed; /* purple-700 */
        transform: scale(1.05);
        box-shadow: 0 6px 8px rgba(0, 0, 0, 0.15);
    }
    .stButton>button:disabled {
        background-color: #6b46c1; /* purple-500 */
        cursor: not-allowed;
    }
    .stAlert {
        border-radius: 0.5rem;
    }
    .stAlert.st-cr { /* Error alert */
        background-color: #9b2c2c; /* red-800 */
        color: #fed7d7; /* red-100 */
        border: 1px solid #c53030; /* red-600 */
    }
    .stAlert.st-cw { /* Warning alert */
        background-color: #975a16; /* orange-800 */
        color: #fffaf0; /* orange-100 */
        border: 1px solid #dd6b20; /* orange-600 */
    }
    .band-name-item {
        background-color: #2d3748; /* gray-700 */
        padding: 1rem;
        border-radius: 0.5rem;
        box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
        display: flex;
        justify-content: space-between;
        align-items: center;
        margin-bottom: 0.75rem;
        transition: all 0.2s ease;
    }
    .band-name-item:hover {
        transform: scale(1.02);
    }
    .copy-button {
        background-color: #a78bfa; /* purple-500 */
        color: white;
        padding: 0.25rem 0.75rem;
        border-radius: 0.375rem;
        font-size: 0.875rem;
        transition: background-color 0.2s ease;
    }
    .copy-button:hover {
        background-color: #8b5cf6; /* purple-600 */
    }
    </style>
    """,
    unsafe_allow_html=True
)

st.title("Danial's Ultimate Band Name Generator")
st.markdown(
    """
    <p style='text-align: center; color: #cbd5e0; font-size: 1.125rem;'>
        Unleash your inner rockstar! Enter a few details to get unique band name ideas.
    </p>
    """,
    unsafe_allow_html=True
)

# Input Fields
city = st.text_input("What city did you grow up in?", placeholder="e.g., Kuala Lumpur")
pet_name = st.text_input("What is the name of your pet?", placeholder="e.g., Sparky")
favorite_color = st.text_input("What is your favorite color? (Optional)", placeholder="e.g., Blue")
genre = st.text_input("Preferred Music Genre? (Optional)", placeholder="e.g., Rock, Pop, Jazz")

# Generate Button
if st.button("Generate Band Names"):
    if not city.strip() or not pet_name.strip():
        st.error("Please enter both City and Pet Name to get suggestions.")
    else:
        # Generate rule-based names
        rule_based_names = generate_band_names(city, pet_name, favorite_color, genre)
        all_suggestions = list(rule_based_names)

        # Generate AI-powered names using a spinner for loading
        with st.spinner("Generating AI-powered names..."):
            ai_names = st.session_state.get('ai_names_cache', []) # Use cache if available
            if not ai_names: # Only call API if not cached
                ai_names = st.session_state['ai_names_cache'] = st.experimental_rerun_if_changed(
                    get_ai_band_names, city, pet_name, favorite_color, genre
                )
            all_suggestions.extend(ai_names)

        # Remove duplicates from combined list
        final_suggestions = list(set(all_suggestions))

        if final_suggestions:
            st.subheader("Your Band Name Suggestions:")
            for name in final_suggestions:
                # Using markdown with HTML for custom styling and copy button
                st.markdown(f"""
                    <div class="band-name-item">
                        <span style="font-size: 1.125rem; color: #e2e8f0; font-weight: 500;">{name}</span>
                        <button class="copy-button" onclick="navigator.clipboard.writeText('{name.replace("'", "\\'")}'); alert('Copied to clipboard!');">Copy</button>
                    </div>
                """, unsafe_allow_html=True)
        else:
            st.warning("No band names could be generated. Please try again with different inputs.")

# Instructions for running the app
st.markdown(
    """
    ---
    ### How to run this application:
    1.  Save the code above as a Python file (e.g., `band_generator.py`).
    2.  Open your terminal or command prompt.
    3.  Install Streamlit and the Google Generative AI library:
        ```bash
        pip install streamlit google-generativeai
        ```
    4.  Run the application:
        ```bash
        streamlit run band_generator.py
        ```
    5.  Your web browser will automatically open to display the app.
    """,
    unsafe_allow_html=True
)
