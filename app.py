import streamlit as st
import uuid
from interview_coach import InterviewCoach

# ==========================================
# 1. PAGE CONFIGURATION
# ==========================================
# st.set_page_config MUST be the very first Streamlit command in the script.
# It sets the page title in the browser tab, page icon, and layout behavior.
st.set_page_config(page_title="AI Interview Coach", page_icon="🎯", layout="wide")

# ==========================================
# 2. SESSION STATE STATE-MANAGEMENT
# ==========================================
# IMPORTANT CONCEPT FOR INTERVIEWS:
# Streamlit is reactive. It re-runs the entire script from top to bottom on every user interaction (e.g., clicking a button, typing).
# Normal variables get reset on every rerun!
# To persist variables (like our active coach instance or chat history), we MUST store them in `st.session_state`.
# Think of st.session_state as a persistent dictionary for the current user's session.

# Initialize the Coach instance (None until "Start Interview" is pressed)
if "coach" not in st.session_state:
    st.session_state.coach = None

# Unique session ID to pass to LangChain memory history
if "session_id" not in st.session_state:
    st.session_state.session_id = None

# List of messages in the conversation chat transcript
if "messages" not in st.session_state:
    st.session_state.messages = []

# Boolean flag to track if the interview has concluded
if "interview_complete" not in st.session_state:
    st.session_state.interview_complete = False

# ==========================================
# 3. SIDEBAR CONFIGURATION
# ==========================================
# Using `with st.sidebar:` pushes all enclosed UI components into the sidebar panel on the left.
with st.sidebar:
    st.header("🎯 Interview Setup")

    # Inputs for configuring the interview
    position = st.text_input("Position", "Senior Python Developer")
    level = st.selectbox("Level", ["junior", "mid", "senior", "staff"])
    interview_type = st.selectbox("Type", ["technical", "behavioral", "system_design"])

    # RAG input: Candidates can paste a job description here
    job_desc = st.text_area(
        "Job Description (optional)",
        placeholder="Paste job description here to generate highly targeted questions...",
        height=150
    )

    # Number of questions requested for the interview
    num_questions = st.slider("Number of Questions", 3, 10, 5)

    # Action Button to initiate the interview
    if st.button("Start Interview", type="primary"):
        # Create a new InterviewCoach. It dynamically configures Gemini.
        st.session_state.coach = InterviewCoach(
            job_description=job_desc if job_desc.strip() else None,
            interview_type=interview_type,
            level=level,
            position=position
        )
        
        # Generate a unique session ID for LangChain message history
        st.session_state.session_id = str(uuid.uuid4())
        
        # Reset state variables
        st.session_state.messages = []
        st.session_state.interview_complete = False

        # Define high-level topics for our questions based on length
        default_topics = ["core skills", "system design", "problem solving", "experience", "culture fit"]
        selected_topics = default_topics[:num_questions]
        
        # Trigger the coach to start the interview and get the first question
        welcome_message = st.session_state.coach.start_interview(
            st.session_state.session_id,
            topics=selected_topics
        )
        
        # Save the welcome question to our chat history
        st.session_state.messages.append({"role": "assistant", "content": welcome_message})
        
        # st.rerun() tells Streamlit to immediately execute the script from the top again
        # so that the newly created coach and message list display instantly.
        st.rerun()

# ==========================================
# 4. MAIN CONTENT AREA
# ==========================================
st.title("🎯 AI Interview Coach")
st.write("Welcome! This Gemini-powered application conducts mock interviews and provides direct feedback on your answers.")

# If the user has not started an interview, show a helpful call-to-action message
if st.session_state.coach is None:
    st.info("👈 Please configure your mock interview parameters in the sidebar and click 'Start Interview' to begin!")
else:
    # --------------------------------------
    # A. RENDER CONVERSATION HISTORY
    # --------------------------------------
    # Loop over all recorded messages in the state and render them using Streamlit's native chat layout
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.write(message["content"])
            
            # If a question has feedback associated with it, display it in a collapsible expander
            if "feedback" in message:
                with st.expander("📝 View Feedback on This Answer"):
                    fb = message["feedback"]
                    
                    # Renders a neat metric showing the score out of 10
                    st.metric(label="Score", value=f"{fb.score}/10")
                    
                    # Highlight strengths, improvemen
                    # ts, and coach tips
                    st.write(f"**Understanding:** {fb.understanding}")
                    
                    if fb.strengths:
                        st.write("**Strengths:**")
                        for strength in fb.strengths:
                            st.write(f"- {strength}")
                            
                    if fb.improvements:
                        st.write("**Tips for Improvement:**")
                        for tip in fb.improvements:
                            st.write(f"- {tip}")

    # --------------------------------------
    # B. CHAT INPUT FOR ANSWERS
    # --------------------------------------
    # If the interview is ongoing, display the text input box at the bottom of the screen
    if not st.session_state.interview_complete:
        # st.chat_input waits for the user to press Enter
        if prompt := st.chat_input("Type your answer here..."):
            
            # 1. Add user answer to our session chat messages
            st.session_state.messages.append({"role": "user", "content": prompt})

            # 2. Call the coach class to submit answer and retrieve evaluation
            result = st.session_state.coach.submit_answer(
                st.session_state.session_id,
                prompt
            )

            # 3. Check if we have completed all questions
            if result["is_complete"]:
                # Set completion flag to True (disables the chat input)
                st.session_state.interview_complete = True
                
                # Ask the coach coordinator to compile a final, comprehensive report
                report = st.session_state.coach.generate_report(st.session_state.session_id)

                # Format the report using standard Markdown
                report_markdown = f"""
## 🎓 Interview Evaluation Complete! 🎉

### **Overall Score: {report.overall_score}/10**
### **Recommendation: {report.recommendation.upper()}**

---

### **Executive Summary**
{report.summary}

---

### **Demonstrated Strengths**
"""
                for s in report.strengths:
                    report_markdown += f"- {s}\n"

                report_markdown += "\n### **Areas to Improve**\n"
                for a in report.areas_to_improve:
                    report_markdown += f"- {a}\n"

                report_markdown += "\n### **Suggested Study Topics**\n"
                for t in report.suggested_topics_to_study:
                    report_markdown += f"- {t}\n"

                # Append the generated report directly into the chat history as an assistant response
                st.session_state.messages.append({
                    "role": "assistant",
                    "content": report_markdown
                })
            else:
                # If there are still questions remaining, append the next question
                # along with the specific feedback evaluated for the answer just submitted
                st.session_state.messages.append({
                    "role": "assistant",
                    "content": result["next_question"],
                    "feedback": result["feedback"]  # Storing feedback to display in the expander
                })

            # 4. Trigger rerun to update the UI instantly
            st.rerun()
    else:
        # C. COMPLETED INTERVIEW STATUS
        # If the interview is complete, show a success banner and a restart button
        st.success("🎉 You have completed this interview session! Excellent work.")
        
        if st.button("Start a New Mock Interview"):
            # Clear all state variables to return to the welcome landing page
            st.session_state.coach = None
            st.session_state.session_id = None
            st.session_state.messages = []
            st.session_state.interview_complete = False
            st.rerun()