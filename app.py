import streamlit as st
import time
import re
import os

from google import genai
from google.genai import types
from google.genai.errors import APIError


# -----------------------------------------------------------------------------
# 1. PAGE CONFIGURATION & THEMING
# -----------------------------------------------------------------------------

st.set_page_config(
    page_title="RoamAcademic | AI Student Travel Planner",
    page_icon="✈️",
    layout="wide",
    initial_sidebar_state="collapsed"
)


# -----------------------------------------------------------------------------
# 2. CUSTOM CSS
# -----------------------------------------------------------------------------

st.markdown("""
    <style>

    .stApp {
        background: linear-gradient(135deg, #0f172a 0%, #1e1b4b 100%);
        color: #f8fafc;
        font-family: 'Inter', sans-serif;
    }

    .crypto-card {
        background: rgba(255, 255, 255, 0.05);
        backdrop-filter: blur(10px);
        border-radius: 16px;
        padding: 25px;
        border: 1px solid rgba(255, 255, 255, 0.1);
        margin-bottom: 20px;
        box-shadow: 0 8px 32px 0 rgba(0, 0, 0, 0.37);
    }

    .gradient-text {
        background: linear-gradient(90deg, #38bdf8, #a855f7);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        font-weight: 800;
    }

    .stButton > button {
        background: linear-gradient(90deg, #6366f1, #a855f7) !important;
        color: white !important;
        border: none !important;
        padding: 10px 24px !important;
        border-radius: 8px !important;
        font-weight: 600 !important;
        transition: all 0.3s ease !important;
        width: 100%;
    }

    .stButton > button:hover {
        transform: translateY(-2px);
        box-shadow: 0 4px 20px rgba(168, 85, 247, 0.4);
    }

    p, li {
        color: #cbd5e1 !important;
        line-height: 1.6;
    }

    h1, h2, h3, h4 {
        color: #ffffff !important;
    }

    table {
        width: 100%;
        border-collapse: collapse;
        margin: 15px 0;
        background: rgba(255, 255, 255, 0.02);
    }

    th, td {
        border: 1px solid rgba(255, 255, 255, 0.1);
        padding: 10px;
        text-align: left;
    }

    th {
        background: rgba(99, 102, 241, 0.2);
    }

    </style>
""", unsafe_allow_html=True)


# -----------------------------------------------------------------------------
# 3. GEMINI API CONFIGURATION
# -----------------------------------------------------------------------------

# Render Environment Variable:
# GEMINI_API_KEY = your_actual_api_key

API_KEY = os.environ.get("GEMINI_API_KEY")


def get_gemini_client():

    if not API_KEY:
        st.error(
            "❌ GEMINI_API_KEY is not configured. "
            "Please add GEMINI_API_KEY in Render → Environment."
        )
        return None

    try:
        return genai.Client(api_key=API_KEY)

    except Exception as e:
        st.error(f"❌ Failed to initialize Gemini API: {e}")
        return None


# -----------------------------------------------------------------------------
# 4. HEADER
# -----------------------------------------------------------------------------

st.markdown(
    '# ✈️ <span class="gradient-text">RoamAcademic</span>',
    unsafe_allow_html=True
)

st.markdown(
    "### Smart, Budget-Friendly Itineraries Designed for Students."
)

st.write("---")


# -----------------------------------------------------------------------------
# 5. MAIN LAYOUT
# -----------------------------------------------------------------------------

col1, col2 = st.columns([1, 2])


# -----------------------------------------------------------------------------
# 6. LEFT SIDE - TRIP PARAMETERS
# -----------------------------------------------------------------------------

with col1:

    st.markdown(
        '<div class="crypto-card"><h4>📍 Trip Parameters</h4>',
        unsafe_allow_html=True
    )

    destination = st.text_input(
        "Where are you heading?",
        placeholder="e.g., Digha, Kerala, Goa, Japan"
    )

    origin = st.text_input(
        "Starting from?",
        placeholder="e.g., Kolkata, Delhi"
    )

    days = st.slider(
        "Trip Duration (Days)",
        min_value=1,
        max_value=10,
        value=3
    )

    budget = st.selectbox(
        "Budget Level (Per Person)",
        [
            "Shoestring (Backpacker/Hostels)",
            "Moderate Student (Budget Hotels/Street Food)",
            "Comfortable"
        ]
    )

    travel_mode = st.multiselect(
        "Preferred Transport",
        [
            "Trains",
            "Buses",
            "Shared Cabs",
            "Walking/Public Metro"
        ],
        default=[
            "Walking/Public Metro",
            "Trains"
        ]
    )

    interests = st.multiselect(
        "Primary Interests",
        [
            "Nature & Hikes",
            "History & Culture",
            "Nightlife & Cafes",
            "Photography Hotspots",
            "Local Food Hidden Gems"
        ],
        default=[
            "History & Culture",
            "Local Food Hidden Gems"
        ]
    )

    submit_btn = st.button(
        "✨ Generate AI Itinerary"
    )

    st.markdown(
        '</div>',
        unsafe_allow_html=True
    )


# -----------------------------------------------------------------------------
# 7. RIGHT SIDE - AI ITINERARY GENERATOR
# -----------------------------------------------------------------------------

with col2:

    if submit_btn:

        # -------------------------------------------------------------
        # Validate inputs
        # -------------------------------------------------------------

        if not destination or not origin:

            st.warning(
                "⚠️ Please fill out both the Destination and Origin fields!"
            )

        else:

            # ---------------------------------------------------------
            # Initialize Gemini
            # ---------------------------------------------------------

            client = get_gemini_client()

            if client:

                # -----------------------------------------------------
                # Prepare values safely
                # -----------------------------------------------------

                selected_transport = (
                    ", ".join(travel_mode)
                    if travel_mode
                    else "Public transportation"
                )

                selected_interests = (
                    ", ".join(interests)
                    if interests
                    else "General sightseeing"
                )

                # -----------------------------------------------------
                # AI Prompt
                # -----------------------------------------------------

                prompt = f"""
Generate a comprehensive, highly detailed {days}-day student travel
itinerary from {origin} to {destination}.

Do not provide a generic summary.

Provide practical, actionable information suitable for college students.

Trip Parameters:

- Origin: {origin}
- Destination: {destination}
- Duration: {days} days
- Budget Strategy: {budget}
- Preferred Transport: {selected_transport}
- Interests: {selected_interests}

IMPORTANT:

Clearly mention that prices, schedules and availability may change.
Avoid inventing exact real-time transport schedules or prices.

Structure the response using these sections:

### 💰 1. Comprehensive Budget Allocation Table

Create a detailed markdown table:

| Expense Category | Estimated Cost | Money-Saving Hacks & Student Discounts |
| :--- | :--- | :--- |
| Accommodation | | |
| Food & Street Food | | |
| Local Transport | | |
| Entry Fees & Attractions | | |
| Emergency Buffer | | |

Provide approximate costs in the appropriate local currency.

### 🗺️ 2. Route Optimization & Logistics

Explain the practical route from {origin} to {destination}.

Include:

- Train options
- Bus options
- Shared transport
- Local transportation
- Approximate travel duration
- How students can save money
- Important booking considerations

Do not claim a specific live schedule unless it is known.

### 📅 3. High-Density Day-by-Day Itinerary

For EACH of the {days} days provide:

#### Morning (8:00 AM - 12:00 PM)

Include:

- Places to visit
- Historical points
- Nature attractions
- How to reach them
- Suggested activities

#### Afternoon (12:00 PM - 5:00 PM)

Include:

- Local attractions
- Markets
- Museums
- Student-friendly food options
- Walking routes

#### Evening & Night (5:00 PM - 10:00 PM)

Include:

- Viewpoints
- Night markets
- Cultural activities
- Cafes
- Student-friendly activities

### 💡 4. Pro Student Safety & Survival Hacks

Provide at least 6 practical tips relevant to {destination}.

Include:

- Transportation safety
- Food and water advice
- Common tourist mistakes
- Money-saving advice
- Emergency preparation
- Important documents

### 🎒 5. Student Packing Checklist

Create a practical checklist for the trip.

### 📱 6. Useful Apps & Resources

Suggest useful categories of apps such as:

- Maps
- Transportation
- Booking
- Translation
- Emergency services

Do not invent app features.

### 💰 7. Final Estimated Trip Cost

Provide:

- Minimum expected budget
- Moderate student budget
- Comfortable budget

Clearly state that these are estimates and may change.
"""


                # -----------------------------------------------------
                # Generation settings
                # -----------------------------------------------------

                success = False
                response_text = ""

                max_attempts = 3

                status_container = st.empty()


                # -----------------------------------------------------
                # Generate response
                # -----------------------------------------------------

                for attempt in range(max_attempts):

                    try:

                        status_container.markdown(
                            "⏳ **AI is compiling your student travel plan...**"
                        )

                        response = client.models.generate_content(

                            model="gemini-2.5-flash",

                            contents=prompt,

                            config=types.GenerateContentConfig(

                                temperature=0.6,

                                max_output_tokens=8192,

                                system_instruction=(
                                    "You are a meticulous professional "
                                    "student travel guide. Create detailed, "
                                    "well-structured, practical itineraries. "
                                    "Never fabricate live schedules. "
                                    "Clearly label estimates."
                                )
                            )
                        )


                        # -------------------------------------------------
                        # Extract response
                        # -------------------------------------------------

                        if response and response.text:

                            response_text = response.text

                            if len(response_text) > 200:

                                success = True
                                break

                            else:

                                if attempt < max_attempts - 1:

                                    status_container.warning(
                                        "⚠️ The AI returned a short response. "
                                        "Retrying..."
                                    )

                                    time.sleep(3)


                    except APIError as e:

                        err_msg = str(e)

                        if (
                            "429" in err_msg
                            or "RESOURCE_EXHAUSTED" in err_msg
                            or "503" in err_msg
                            or "UNAVAILABLE" in err_msg
                        ):

                            wait_match = re.search(
                                r"retry in ([\d\.]+)",
                                err_msg,
                                re.IGNORECASE
                            )

                            wait_time = (
                                float(wait_match.group(1))
                                if wait_match
                                else (attempt + 1) * 8
                            )

                            wait_time = min(
                                wait_time + 1.5,
                                30.0
                            )

                            if attempt < max_attempts - 1:

                                status_container.warning(
                                    f"⚠️ Gemini API is temporarily busy. "
                                    f"Retrying in {wait_time:.1f} seconds... "
                                    f"(Attempt {attempt + 1}/{max_attempts})"
                                )

                                time.sleep(wait_time)

                            else:

                                status_container.error(
                                    "❌ Gemini API is temporarily unavailable. "
                                    "Please try again later."
                                )

                        else:

                            status_container.error(
                                f"❌ Gemini API Error: {err_msg}"
                            )

                            break


                    except Exception as e:

                        status_container.error(
                            f"❌ Unexpected error: {e}"
                        )

                        break


                # ---------------------------------------------------------
                # Clear status
                # ---------------------------------------------------------

                status_container.empty()


                # ---------------------------------------------------------
                # Display successful result
                # ---------------------------------------------------------

                if success and response_text:

                    st.markdown(
                        '<div class="crypto-card">',
                        unsafe_allow_html=True
                    )

                    st.markdown(
                        f"## 🗺️ Detailed Student Plan: "
                        f"{destination.title()}"
                    )

                    st.markdown(response_text)

                    st.markdown(
                        '</div>',
                        unsafe_allow_html=True
                    )


                # ---------------------------------------------------------
                # Display failure
                # ---------------------------------------------------------

                else:

                    st.error(
                        "❌ Generation request did not return a complete "
                        "response. Please wait a moment and try again."
                    )


# -----------------------------------------------------------------------------
# 8. DEFAULT SCREEN
# -----------------------------------------------------------------------------

    else:

        st.markdown(
            '<div class="crypto-card" '
            'style="text-align: center; padding: 50px;">',
            unsafe_allow_html=True
        )

        st.markdown(
            "### 🗺️ Your Customized Plan Will Appear Here"
        )

        st.write(
            "Fill in your parameters on the left, click "
            "**Generate**, and watch the system create your "
            "complete student travel roadmap."
        )

        st.markdown(
            '</div>',
            unsafe_allow_html=True
        )
