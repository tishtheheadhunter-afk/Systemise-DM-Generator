"""
BDC DM Generator (Systemise and Sell)
====================================
Streamlit app that generates DM/comment responses in Marco Fernandes' voice
for the High-Ticket Closer Mastery programme.

The system prompt is built dynamically from markdown files in /context and
/examples at runtime. Edit those files to change the bot's behaviour.

Author: Tish Dave (tishtheheadhunter-afk)
"""

import os
import json
import uuid
from pathlib import Path
from datetime import datetime
from typing import Optional

import streamlit as st
from anthropic import Anthropic
from supabase import create_client, Client


# ============================================================================
# CONFIG
# ============================================================================

st.set_page_config(
    page_title="BDC DM Generator",
    page_icon="💬",
    layout="centered",
    initial_sidebar_state="collapsed",
)

# Repo paths
REPO_ROOT = Path(__file__).parent
CONTEXT_DIR = REPO_ROOT / "context"
EXAMPLES_DIR = REPO_ROOT / "examples"

# Model
MODEL = "claude-sonnet-4-20250514"
MAX_TOKENS = 2500

# Booking links (kept here as constants for reference, also live in context files)
BOOKING_LINK = "https://api.leadconnectorhq.com/widget/bookings/systemiseandselldiscoverycall"
SKOOL_LINK = "https://community.systemiseandsell.com/join"


# ============================================================================
# RESPONSE TYPES
# ============================================================================

RESPONSE_TYPES = {
    "Inbound DM Opener": {
        "description": "First reply to someone who DM'd us cold",
        "example_file": "01_inbound_dm_opener.md",
        "options_count": 3,
        "phase_hint": "Step 1 of qualification arc",
    },
    "Outbound DM Opener": {
        "description": "First message we send to a prospect (cold/warm outreach)",
        "example_file": "02_outbound_dm_opener.md",
        "options_count": 3,
        "phase_hint": "Pre-qualification, getting them to reply",
    },
    "Comment Reply": {
        "description": "Public reply to a comment on a post",
        "example_file": "03_comment_reply.md",
        "options_count": 2,
        "phase_hint": "Public-facing, doubles as content",
    },
    "New Follow Welcome": {
        "description": "DM to someone who just followed",
        "example_file": "04_new_follow_welcome.md",
        "options_count": 2,
        "phase_hint": "Open the door, low pressure",
    },
    "Post Like Outreach": {
        "description": "DM to someone who liked a post",
        "example_file": "05_post_like_outreach.md",
        "options_count": 2,
        "phase_hint": "Reference the post, ask one question",
    },
    "Push to Call": {
        "description": "Bridge them toward booking the discovery call",
        "example_file": "06_push_to_call.md",
        "options_count": 3,
        "phase_hint": "Step 5 of qualification arc",
    },
    "Send Booking Link": {
        "description": "They agreed, send the link cleanly",
        "example_file": "07_send_booking_link.md",
        "options_count": 1,
        "phase_hint": "Step 6 of qualification arc",
    },
    "Skool Fallback": {
        "description": "They declined the call due to investment/timing, pivot to free Skool community",
        "example_file": "08_skool_fallback.md",
        "options_count": 3,
        "phase_hint": "ONLY for money/timing objections, never 'not interested'",
    },
    "Skool Re-engagement": {
        "description": "Skool member hit qualification signals, surface paid programme contextually",
        "example_file": "09_skool_reengagement.md",
        "options_count": 2,
        "phase_hint": "Template 6 style, frames paid programme as separate",
    },
    "General Objection Handle": {
        "description": "Handle objection that ISN'T about money (skepticism, time, fit, etc.)",
        "example_file": "10_objection_handle.md",
        "options_count": 3,
        "phase_hint": "Validate, reframe, redirect to call",
    },
    "Follow-up": {
        "description": "Re-engage a quiet prospect (cadence ladder)",
        "example_file": "11_follow_up.md",
        "options_count": 1,
        "phase_hint": "Light, no pressure, easy out",
    },
    "Send Skool Link": {
        "description": "Deliver the Skool community link",
        "example_file": "12_send_skool_link.md",
        "options_count": 1,
        "phase_hint": "Mechanical delivery",
    },
}


# ============================================================================
# CONTEXT LOADING (single source of truth pattern)
# ============================================================================

@st.cache_data(ttl=60)  # Cache for 60s; refreshes when context files change
def load_context_files() -> str:
    """Load and concatenate all markdown files from /context in order."""
    if not CONTEXT_DIR.exists():
        return ""
    
    files = sorted(CONTEXT_DIR.glob("*.md"))
    parts = []
    for f in files:
        try:
            content = f.read_text(encoding="utf-8")
            parts.append(f"# === {f.name} ===\n\n{content}")
        except Exception as e:
            st.warning(f"Could not read {f.name}: {e}")
    
    return "\n\n".join(parts)


@st.cache_data(ttl=60)
def load_example_file(filename: str) -> str:
    """Load a specific example file from /examples."""
    path = EXAMPLES_DIR / filename
    if not path.exists():
        return ""
    try:
        return path.read_text(encoding="utf-8")
    except Exception as e:
        st.warning(f"Could not read {filename}: {e}")
        return ""


def build_system_prompt(response_type: str) -> str:
    """Build the full system prompt for a given response type."""
    
    rt_config = RESPONSE_TYPES.get(response_type, {})
    example_content = load_example_file(rt_config.get("example_file", ""))
    context_content = load_context_files()
    options_count = rt_config.get("options_count", 3)
    phase_hint = rt_config.get("phase_hint", "")
    
    prompt = f"""You are the DM and comment response generator for Marco Fernandes / Systemise and Sell. You write AS Marco's setter team in his voice, direct, no-BS, tough love mentor, calm authority, never hype.

You will be given:
1. The full system context (Marco's voice, the offer, forbidden angles, etc.)
2. Worked examples for the specific response type being requested
3. The prospect's message and any conversation history

Your job is to generate {options_count} response option(s) that match Marco's voice exactly, fit the conversation context, and follow the patterns in the worked examples.

# === SYSTEM CONTEXT ===

{context_content}

# === WORKED EXAMPLES FOR THIS RESPONSE TYPE ===

The current response type is: **{response_type}**
Phase hint: {phase_hint}

Below are worked examples showing exactly what good output looks like for this response type:

{example_content}

# === OUTPUT FORMAT ===

Generate {options_count} option(s). Format your response as a JSON array. Each object has:
- "label": a 2-4 word descriptor of the angle/style (e.g., "Direct, Authority-led", "Empathy first", "Reframe + bridge")
- "text": the actual message text

Return ONLY the JSON array, no markdown fences, no preamble.

CRITICAL RULES:
1. NEVER use em dashes. Use commas, full stops, colons. Hyphens only inside compound words.
2. NEVER discuss pricing in DMs. Redirect to the call.
3. NEVER say "guaranteed placement". Always "guaranteed interview opportunities".
4. NEVER conflate Marco Fernandes with Sir Marco Robinson. We are Marco Fernandes, the high-ticket closer trainer. Sir Marco Robinson is a different person running a different (book) offer.
5. Sparing emoji use only. One smiley at the end of a softening question is fine. Never on every line. Never stack multiple emojis.
6. Personalise to what the prospect actually said. Generic responses fail.
7. Match the worked examples in tone, length, and structure.
"""
    
    return prompt


# ============================================================================
# ANTHROPIC CLIENT
# ============================================================================

@st.cache_resource
def get_anthropic_client() -> Optional[Anthropic]:
    api_key = st.secrets.get("ANTHROPIC_API_KEY") or os.getenv("ANTHROPIC_API_KEY")
    if not api_key:
        return None
    return Anthropic(api_key=api_key)


def generate_responses(
    response_type: str,
    prospect_message: str,
    additional_context: str = "",
    conversation_history: str = "",
) -> tuple[Optional[list], Optional[str]]:
    """Returns (results, error). results is a list of {label, text} dicts."""
    
    client = get_anthropic_client()
    if not client:
        return None, "ANTHROPIC_API_KEY not configured. Add it to Streamlit secrets."
    
    system_prompt = build_system_prompt(response_type)
    
    # Build user message
    user_parts = []
    if conversation_history.strip():
        user_parts.append(f"## Conversation history so far:\n\n{conversation_history.strip()}")
    
    user_parts.append(f"## The prospect's latest message:\n\n{prospect_message.strip()}")
    
    if additional_context.strip():
        user_parts.append(f"## Additional context the setter wants you to know:\n\n{additional_context.strip()}")
    
    user_message = "\n\n".join(user_parts)
    
    try:
        response = client.messages.create(
            model=MODEL,
            max_tokens=MAX_TOKENS,
            system=system_prompt,
            messages=[{"role": "user", "content": user_message}],
        )
        
        text = response.content[0].text.strip()
        
        # Strip any accidental markdown fences
        if text.startswith("```"):
            text = text.split("```")[1]
            if text.startswith("json"):
                text = text[4:]
            text = text.strip()
        if text.endswith("```"):
            text = text[:-3].strip()
        
        # Parse JSON
        results = json.loads(text)
        
        # Strip any em dashes that slipped through (belt and braces)
        for r in results:
            if "text" in r:
                r["text"] = strip_em_dashes(r["text"])
        
        return results, None
    
    except json.JSONDecodeError as e:
        return None, f"Failed to parse model output as JSON: {e}\n\nRaw output:\n{text[:500]}"
    except Exception as e:
        return None, f"Generation failed: {type(e).__name__}: {e}"


def strip_em_dashes(text: str) -> str:
    """Replace em dashes / en dashes with commas (project-wide rule)."""
    replacements = [
        ("\u2014", ","),  # em dash
        ("\u2013", ","),  # en dash
        ("\u2015", ","),  # horizontal bar
        (" - ", ", "),    # space-dash-space
    ]
    for old, new in replacements:
        text = text.replace(old, new)
    return text


# ============================================================================
# SUPABASE CLIENT (thread persistence)
# ============================================================================

@st.cache_resource
def get_supabase_client() -> Optional[Client]:
    url = st.secrets.get("SUPABASE_URL") or os.getenv("SUPABASE_URL")
    key = st.secrets.get("SUPABASE_ANON_KEY") or os.getenv("SUPABASE_ANON_KEY")
    if not url or not key:
        return None
    try:
        return create_client(url, key)
    except Exception as e:
        st.warning(f"Could not connect to Supabase: {e}")
        return None


def load_threads() -> dict:
    """Load all threads from Supabase. Returns {id: {name, context, messages}}."""
    sb = get_supabase_client()
    if not sb:
        # Fallback: in-memory only (session state)
        return st.session_state.get("threads", {})
    
    try:
        resp = sb.table("bdc_dm_threads").select("*").order("updated_at", desc=True).execute()
        threads = {}
        for row in resp.data:
            threads[row["id"]] = {
                "name": row["name"],
                "context": row.get("context", ""),
                "messages": row.get("messages", []),
            }
        return threads
    except Exception as e:
        st.warning(f"Could not load threads from Supabase: {e}")
        return st.session_state.get("threads", {})


def save_thread(thread_id: str, name: str, context: str, messages: list):
    """Save a thread to Supabase (upsert)."""
    sb = get_supabase_client()
    if not sb:
        # Fallback: store in session state
        if "threads" not in st.session_state:
            st.session_state.threads = {}
        st.session_state.threads[thread_id] = {
            "name": name,
            "context": context,
            "messages": messages,
        }
        return
    
    try:
        sb.table("bdc_dm_threads").upsert({
            "id": thread_id,
            "name": name,
            "context": context,
            "messages": messages,
        }).execute()
    except Exception as e:
        st.warning(f"Could not save thread to Supabase: {e}")


def delete_thread(thread_id: str):
    sb = get_supabase_client()
    if not sb:
        st.session_state.threads.pop(thread_id, None)
        return
    try:
        sb.table("bdc_dm_threads").delete().eq("id", thread_id).execute()
    except Exception as e:
        st.warning(f"Could not delete thread: {e}")


# ============================================================================
# UI
# ============================================================================

def render_header():
    st.markdown(
        """
        <div style="text-align: center; padding: 16px 0 8px 0;">
            <h1 style="margin: 0; font-size: 28px; font-weight: 700;">Billion Dollar Closers</h1>
            <p style="color: #6e7681; font-size: 14px; margin: 4px 0 0 0;">DM &amp; Comment Response Generator</p>
        </div>
        """,
        unsafe_allow_html=True,
    )


def render_response_type_picker(key_prefix: str = "main") -> str:
    """Picker for response type. Returns the selected type."""
    types = list(RESPONSE_TYPES.keys())
    default_idx = 0
    
    selected = st.selectbox(
        "Response type",
        options=types,
        index=default_idx,
        key=f"{key_prefix}_response_type",
        help="Pick the situation. The bot will generate the right kind of response.",
    )
    
    rt_config = RESPONSE_TYPES[selected]
    st.caption(f"{rt_config['description']}")
    
    return selected


def render_results(results: list, key_prefix: str, on_use_callback=None):
    """Render the generated options with copy/use buttons."""
    
    color_palette = [
        {"bg": "#1e3a5f", "border": "#2d6da8", "label": "#6db3f2", "text": "#d0e8ff"},
        {"bg": "#1a3d2e", "border": "#2d8a5e", "label": "#5ec99a", "text": "#c8f0de"},
        {"bg": "#3d3520", "border": "#8a7a3d", "label": "#d4b94e", "text": "#f0e6c0"},
    ]
    
    for i, opt in enumerate(results):
        c = color_palette[i % len(color_palette)]
        
        st.markdown(
            f"""
            <div style="background: {c['bg']}; border: 1px solid {c['border']}; border-radius: 10px; padding: 16px; margin-bottom: 12px;">
                <div style="font-size: 12px; font-weight: 700; color: {c['label']}; margin-bottom: 8px; text-transform: uppercase; letter-spacing: 1px;">
                    Option {i + 1}: {opt.get('label', '')}
                </div>
                <div style="font-size: 14px; line-height: 1.7; color: {c['text']}; white-space: pre-wrap;">{opt.get('text', '')}</div>
            </div>
            """,
            unsafe_allow_html=True,
        )
        
        cols = st.columns([1, 1, 4]) if on_use_callback else st.columns([1, 5])
        with cols[0]:
            if st.button("📋 Copy", key=f"{key_prefix}_copy_{i}"):
                st.session_state[f"{key_prefix}_copied_{i}"] = opt.get("text", "")
                # Fallback display for the user to manually copy
                st.code(opt.get("text", ""), language=None)
        if on_use_callback:
            with cols[1]:
                if st.button("✓ Use", key=f"{key_prefix}_use_{i}"):
                    on_use_callback(i, opt)


def page_quick_generate():
    """Quick generation tab, single-shot, no thread persistence."""
    
    st.markdown("### Quick Generation")
    st.caption("One-off message generation. Use Threads tab to maintain conversation history.")
    
    response_type = render_response_type_picker("quick")
    
    prospect_message = st.text_area(
        "Prospect's message (or comment)",
        height=100,
        placeholder="Paste the prospect's latest message here...",
        key="quick_message",
    )
    
    additional_context = st.text_area(
        "Additional context (optional)",
        height=70,
        placeholder="e.g., 'Bio: 5 years B2B sales, currently at $80k OTE, wants remote.'",
        key="quick_context",
    )
    
    generate = st.button("🎯 Generate Responses", type="primary", use_container_width=True)
    
    if generate:
        if not prospect_message.strip():
            st.error("Please paste a prospect message.")
            return
        
        with st.spinner(f"Generating in Marco's voice..."):
            results, error = generate_responses(
                response_type=response_type,
                prospect_message=prospect_message,
                additional_context=additional_context,
            )
        
        if error:
            st.error(error)
            return
        
        st.session_state["quick_results"] = results
        st.session_state["quick_response_type"] = response_type
    
    if "quick_results" in st.session_state and st.session_state.get("quick_results"):
        st.divider()
        st.markdown(f"#### Generated ({len(st.session_state['quick_results'])} option{'s' if len(st.session_state['quick_results']) > 1 else ''})")
        render_results(st.session_state["quick_results"], key_prefix="quick")


def page_threads():
    """Threads tab, full conversation tracking."""
    
    st.markdown("### Conversation Threads")
    st.caption("Track ongoing prospect conversations. The bot reads the full thread to generate the right next message.")
    
    threads = load_threads()
    
    # Thread selector
    col_select, col_new = st.columns([4, 1])
    with col_select:
        thread_options = ["Select a conversation..."] + [
            f"{t['name']} ({len(t.get('messages', []))} msgs)" for t in threads.values()
        ]
        thread_ids = [None] + list(threads.keys())
        
        idx = st.selectbox(
            "Conversation",
            options=range(len(thread_options)),
            format_func=lambda i: thread_options[i],
            key="thread_selector",
            label_visibility="collapsed",
        )
        active_thread_id = thread_ids[idx]
    with col_new:
        if st.button("+ New", use_container_width=True):
            st.session_state["show_new_form"] = True
    
    # New thread form
    if st.session_state.get("show_new_form"):
        with st.container(border=True):
            st.markdown("**New Conversation**")
            new_name = st.text_input("Name (e.g. James T)", key="new_thread_name")
            new_context = st.text_area(
                "Context (e.g. 'Coach struggling to close own offers')",
                key="new_thread_context",
                height=70,
            )
            cols = st.columns([1, 1])
            with cols[0]:
                if st.button("Create", type="primary", use_container_width=True):
                    if new_name.strip():
                        thread_id = f"t_{uuid.uuid4().hex[:12]}"
                        save_thread(thread_id, new_name.strip(), new_context.strip(), [])
                        st.session_state["show_new_form"] = False
                        st.session_state["new_thread_name"] = ""
                        st.session_state["new_thread_context"] = ""
                        st.rerun()
            with cols[1]:
                if st.button("Cancel", use_container_width=True):
                    st.session_state["show_new_form"] = False
                    st.rerun()
    
    if not active_thread_id:
        st.info("Select a conversation above or create a new one.")
        return
    
    thread = threads[active_thread_id]
    
    # Thread header
    st.markdown(f"#### {thread['name']}")
    if thread.get("context"):
        st.caption(f"Context: {thread['context']}")
    
    # Render message history
    messages = thread.get("messages", [])
    if messages:
        with st.container(border=True):
            for msg in messages:
                role = msg.get("role", "them")
                text = msg.get("text", "")
                if role == "them":
                    st.markdown(f"**THEM:** {text}")
                else:
                    st.markdown(f"**US:** {text}")
                st.caption("─" * 40)
    
    # Generation form
    response_type = render_response_type_picker(f"thread_{active_thread_id}")
    
    new_msg = st.text_area(
        "Their latest message",
        height=80,
        key=f"thread_msg_{active_thread_id}",
        placeholder="Paste what the prospect just sent...",
    )
    
    cols = st.columns([2, 1])
    with cols[0]:
        gen_btn = st.button("🎯 Generate", type="primary", use_container_width=True, key=f"gen_{active_thread_id}")
    with cols[1]:
        log_btn = st.button("📝 Log only", use_container_width=True, key=f"log_{active_thread_id}",
                            help="Add their message to the thread without generating a reply")
    
    if log_btn:
        if new_msg.strip():
            messages.append({"role": "them", "text": new_msg.strip(), "ts": datetime.utcnow().isoformat()})
            save_thread(active_thread_id, thread["name"], thread.get("context", ""), messages)
            st.rerun()
    
    if gen_btn:
        if not new_msg.strip():
            st.error("Please paste their latest message.")
            return
        
        # Build conversation history for the model
        history_lines = []
        for msg in messages:
            role_label = "THEM" if msg.get("role") == "them" else "US"
            history_lines.append(f"{role_label}: {msg.get('text', '')}")
        history_str = "\n\n".join(history_lines)
        
        with st.spinner("Generating in Marco's voice..."):
            results, error = generate_responses(
                response_type=response_type,
                prospect_message=new_msg,
                additional_context=thread.get("context", ""),
                conversation_history=history_str,
            )
        
        if error:
            st.error(error)
            return
        
        st.session_state[f"thread_results_{active_thread_id}"] = results
        st.session_state[f"thread_pending_msg_{active_thread_id}"] = new_msg
    
    # Render thread results
    results_key = f"thread_results_{active_thread_id}"
    if results_key in st.session_state and st.session_state.get(results_key):
        st.divider()
        st.markdown(f"#### Generated ({len(st.session_state[results_key])} option{'s' if len(st.session_state[results_key]) > 1 else ''})")
        
        def use_option(idx, opt):
            pending_msg = st.session_state.get(f"thread_pending_msg_{active_thread_id}", "")
            # Append the prospect's message and our chosen reply to the thread
            if pending_msg and (not messages or messages[-1].get("text") != pending_msg.strip()):
                messages.append({"role": "them", "text": pending_msg.strip(), "ts": datetime.utcnow().isoformat()})
            messages.append({"role": "us", "text": opt.get("text", ""), "ts": datetime.utcnow().isoformat()})
            save_thread(active_thread_id, thread["name"], thread.get("context", ""), messages)
            # Clear results and pending msg
            st.session_state[results_key] = None
            st.session_state[f"thread_msg_{active_thread_id}"] = ""
            st.rerun()
        
        render_results(st.session_state[results_key], key_prefix=f"thread_{active_thread_id}", on_use_callback=use_option)
    
    # Delete option
    st.divider()
    with st.expander("⚠️ Danger zone"):
        if st.button("🗑️ Delete this conversation", type="secondary"):
            delete_thread(active_thread_id)
            st.rerun()


def page_qualification_arc_reference():
    """Sidebar reference card for the 5-step qualification arc."""
    arc_file = CONTEXT_DIR / "05_qualification_arc.md"
    if arc_file.exists():
        with st.expander("📋 Qualification Arc Reference"):
            st.markdown(arc_file.read_text(encoding="utf-8"))


def page_health_check():
    """Diagnostic page for verifying setup."""
    st.markdown("### System Check")
    
    # Anthropic
    client = get_anthropic_client()
    if client:
        st.success("✅ Anthropic API key configured")
    else:
        st.error("❌ ANTHROPIC_API_KEY missing, add to Streamlit secrets")
    
    # Supabase
    sb = get_supabase_client()
    if sb:
        try:
            sb.table("bdc_dm_threads").select("id").limit(1).execute()
            st.success("✅ Supabase connected (bdc_dm_threads table accessible)")
        except Exception as e:
            st.warning(f"⚠️ Supabase reachable but table issue: {e}")
    else:
        st.warning("⚠️ Supabase not configured, threads will be session-only (lost on refresh)")
    
    # Context files
    if CONTEXT_DIR.exists():
        files = list(CONTEXT_DIR.glob("*.md"))
        st.success(f"✅ Context directory: {len(files)} markdown files found")
        for f in sorted(files):
            st.caption(f"  • {f.name}")
    else:
        st.error("❌ /context directory missing")
    
    # Examples files
    if EXAMPLES_DIR.exists():
        files = list(EXAMPLES_DIR.glob("*.md"))
        st.success(f"✅ Examples directory: {len(files)} markdown files found")
        for f in sorted(files):
            st.caption(f"  • {f.name}")
    else:
        st.error("❌ /examples directory missing")


# ============================================================================
# MAIN
# ============================================================================

def main():
    render_header()
    
    tab1, tab2, tab3 = st.tabs(["⚡ Quick", "💬 Threads", "🔧 Setup"])
    
    with tab1:
        page_quick_generate()
        st.divider()
        page_qualification_arc_reference()
    
    with tab2:
        page_threads()
        st.divider()
        page_qualification_arc_reference()
    
    with tab3:
        page_health_check()


if __name__ == "__main__":
    main()
