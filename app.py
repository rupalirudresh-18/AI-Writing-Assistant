
import os
import streamlit as st
from dotenv import load_dotenv
from google import genai
from google.genai import types

# Load API key from .env
load_dotenv()

API_KEY = os.getenv("GEMINI_API_KEY")

st.set_page_config(
    page_title="AI Writing Assistant",
    page_icon="✍️",
    layout="wide"
)

# Writing templates
TEMPLATES = {
    "Blog Writing": """
You are an expert blog writer.
Create a well-structured blog post with an engaging title,
introduction, meaningful headings, and conclusion.
Use clear, engaging language.
""",
    "Email Drafting": """
You are a professional email writing assistant.
Write an email with an appropriate subject, greeting,
clear body, and polite closing.
Follow the requested tone and purpose.
""",
    "Code Explanation": """
You are a patient programming tutor.
Explain the supplied code in simple language.
Describe its purpose, important lines, and logic.
Include a small example when useful.
Do not execute the code.
""",
    "Social Media Posts": """
You are a creative social media content writer.
Create an engaging post suitable for the requested platform.
Use an appropriate tone, a strong opening, and relevant hashtags
when requested. Avoid irrelevant hashtags.
"""
}

# Header
st.title("✍️ AI Writing Assistant")
st.write(
    "Your AI-powered tool for blogs, emails, "
    "code explanations, and social media content."
)

# Check API key
if not API_KEY:
    st.error(
        "Gemini API key not found. Add GEMINI_API_KEY "
        "to your .env file and restart the app."
    )
    st.stop()

# Initialize Gemini client
client = genai.Client(api_key=API_KEY)

# Sidebar controls
st.sidebar.header("⚙️ Writing Settings")

task = st.sidebar.selectbox(
    "Choose writing task",
    list(TEMPLATES.keys())
)

tone = st.sidebar.selectbox(
    "Writing tone",
    ["Professional", "Friendly", "Formal", "Creative", "Simple"]
)

temperature = st.sidebar.slider(
    "Creativity (Temperature)",
    min_value=0.0,
    max_value=1.0,
    value=0.7,
    step=0.1,
    help="Lower values are more focused; higher values are more varied."
)

word_count = st.sidebar.slider(
    "Approximate word count",
    min_value=100,
    max_value=1000,
    value=300,
    step=50
)

st.sidebar.caption(
    "Higher creativity can produce more varied responses."
)

# Main input
st.subheader(f"📝 {task}")

user_prompt = st.text_area(
    "Describe what you want the AI to create",
    placeholder=(
        "Example: Write a blog about the benefits "
        "of learning Python..."
    ),
    height=180
)

generate = st.button(
    "✨ Generate Content",
    type="primary",
    use_container_width=True
)

if generate:
    if not user_prompt.strip():
        st.warning("Please enter a prompt first.")

    else:
        instructions = f"""
{TEMPLATES[task]}

Additional instructions:
- Tone: {tone}
- Target length: approximately {word_count} words.
- Format the output clearly using Markdown.
- Follow the user's request carefully.
"""

        with st.spinner("Generating your content..."):
            try:
                response = client.models.generate_content(
                    model="gemini-3.8-flash",
                    contents=(
                        f"{instructions}\n\n"
                        f"User request:\n{user_prompt}"
                    ),
                    config=types.GenerateContentConfig(
                        temperature=temperature
                    )
                )

                result = response.text

                if result:
                    st.session_state["generated_content"] = result
                    st.session_state["generated_task"] = task
                else:
                    st.error("The AI returned an empty response.")

            except Exception as e:
                st.error(
                    "Content generation failed. Check your API key, "
                    "internet connection, model availability, "
                    "and API usage limits."
                )
                st.caption(f"Error details: {e}")

# Display generated content
if st.session_state.get("generated_content"):
    st.divider()
    st.subheader("✨ Generated Content")

    st.markdown(st.session_state["generated_content"])

    st.download_button(
        label="⬇️ Download as Markdown",
        data=st.session_state["generated_content"],
        file_name="ai_generated_content.md",
        mime="text/markdown",
        use_container_width=True
    )

    st.caption(
        f"Task: {st.session_state.get('generated_task', task)}"
    )

st.divider()
st.caption("AI Writing Assistant | Built with Python, Streamlit & Gemini")
