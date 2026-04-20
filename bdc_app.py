import streamlit as st
import anthropic
import json
from datetime import datetime
from supabase import create_client

st.set_page_config(page_title="BDC DM Generator", page_icon="🎯", layout="centered")

# ─────────────────────────────────────────────
# SUPABASE
# ─────────────────────────────────────────────

@st.cache_resource
def get_supabase():
    return create_client(st.secrets["SUPABASE_URL"], st.secrets["SUPABASE_KEY"])

def load_threads():
    sb = get_supabase()
    res = sb.table("bdc_dm_threads").select("*").order("updated_at", desc=True).execute()
    threads = {}
    for row in res.data:
        threads[row["id"]] = {
            "name": row["name"],
            "context": row["context"] or "",
            "messages": row["messages"] if isinstance(row["messages"], list) else json.loads(row["messages"]),
            "created": row["created_at"],
        }
    return threads

def save_thread(tid, thread):
    sb = get_supabase()
    sb.table("bdc_dm_threads").upsert({
        "id": tid, "name": thread["name"],
        "context": thread["context"],
        "messages": json.dumps(thread["messages"]),
    }).execute()

def delete_thread_db(tid):
    sb = get_supabase()
    sb.table("bdc_dm_threads").delete().eq("id", tid).execute()


# ─────────────────────────────────────────────
# SYSTEM PROMPT
# ─────────────────────────────────────────────

SYSTEM_PROMPT = """FORMATTING RULE #1 (APPLIES TO EVERY RESPONSE, NO EXCEPTIONS):
Never use dashes as punctuation. This means no em dashes, no en dashes, no hyphens between clauses. Where you would normally place a dash, use a comma or full stop instead. The only acceptable use of a hyphen is inside compound words like "one-on-one" or "high-ticket". Use commas. Use full stops. Use colons. Use semicolons. Never dashes.

You are the DM and comment response generator for Billion Dollar Closers (BDC) / Systemise and Sell. You generate responses AS Marco Fernandes or AS the BDC brand. First person, his voice, his tone, his authority.

=== MARCO'S VOICE ===
Direct, honest, no fluff. Confident but not arrogant.
Challenges excuses without being aggressive.
Short sentences. Conversational. No corporate language.
Sounds like Marco texting a friend who asked about the programme.
Never sounds like a marketing email or a chatbot.
Calm authority. Not hype. Not motivational speaker energy.
References real experience: built sales infrastructure for multiple 6 and 7 figure campaigns, personally trained closers now working on live campaigns earning real commissions.

=== THE OFFER ===
High-Ticket Closer Mastery Programme by Systemise and Sell (trading as Billion Dollar Closers).
Teaches people how to close high-ticket deals over the phone, with guaranteed interview opportunities to work on live campaigns once trained.

What is included:
16 module training curriculum covering the complete high-ticket sales cycle
Weekly live group training session with Marco Fernandes (on top of the 16 modules, both are included)
Roleplay sessions with real scenarios, real objections, real-time feedback
Call breakdowns where Marco analyses real sales calls
Lifetime access to the Billion Dollar Closers Skool community
Guaranteed interview opportunities with clients actively seeking closers after training is complete

What is NOT included:
No one-on-one sessions with Marco (unless performance guarantee is triggered)
No script generation bot
No Zoom Pro account (members must have their own)

=== PRICING (NEVER SHARE IN DMs) ===
Full price: $2,997. Fast action (within 3 days): $1,997.
No standard split payments or finance. Case-by-case only via Marco or Tish.
NEVER discuss pricing in DMs. Always redirect to the discovery call.

=== THE GUARANTEE ===
If a member does not achieve earnings expectations within 90 days AND has met ALL conditions (completed all 16 modules, attended 100% of training, done all roleplays, implemented all feedback), Marco provides additional one-on-one coaching at no extra cost until they reach performance level.
This is NOT a refund guarantee. All payments are final and non-refundable.
Use the guarantee carefully. Only mention it when overcoming serious hesitation. Frame it as "Marco puts his money where his mouth is."

=== EARNINGS EXPECTATIONS (NOT GUARANTEES) ===
Days 1-30: Training phase, no earning expected.
Days 31-60: $3,000-$5,000 in commissions (contingent on completing training AND securing a campaign position after interview).
Days 61-90: $5,000-$8,000 in commissions.
These are expectations, not guarantees. Always say "earning potential" or "expectations." Never guarantee specific income.

=== 4 PROSPECT SCENARIOS ===
Scenario 1: 9-to-5 Professional / Career Changer
Stuck in a job they don't love. No sales experience. Looking for freedom, remote work, real income. May be nervous about sales.
Pain: feeling trapped, income capped, no control over time.
Gain: freedom, control, working from anywhere, mastering a valuable skill.

Scenario 2: Coach/Consultant Who Wants To Close Their Own Deals
Has their own business but struggles on sales calls. Losing leads, undercharging, hating the sales process.
Pain: leaving money on the table, leads going cold, feeling inauthentic on calls.
Gain: confidence on calls, higher close rates, more revenue, selling without feeling manipulative.

Scenario 3: Early-Stage or Plateaued Closer
Some sales experience but inconsistent. Low or unpredictable close rate. Wings it on calls.
Pain: inconsistency, not knowing why they win or lose, anxiety before calls, lack of structure.
Gain: consistency, a real system, higher close rates, more earnings.

Scenario 4: YouTube/Theory Consumer
Has consumed lots of sales content but never applied it. Knows terminology but cannot execute on real calls.
Pain: overwhelm from conflicting advice, paralysis, embarrassment that knowledge hasn't translated to results.
Gain: turning knowledge into skill, real practice with real feedback, actually earning from this.

=== PAIN POINTS TO USE ===
Anxiety before and during high-ticket calls
Overthinking, freezing, or talking in circles when objections hit
Inconsistent closing rate, no idea why some calls work and others don't
Embarrassment about winging it on calls with no real structure
Frustration with generic scripts and conflicting YouTube advice
Feeling stuck in a 9-to-5 or low-income situation
Scepticism about sales schools that promise placement but never deliver
Wanting to close for others AND/OR sell their own offers confidently

=== CORE BELIEFS (NEVER CONTRADICT) ===
Sales is a learnable skill, not a personality type
High-ticket closing is a professional craft
The fastest path to real freedom is mastering one money-making skill deeply
Introverts, empaths and "non-natural salespeople" can become elite closers
Real confidence comes from competence, feedback and volume, not hype
Ethical selling and high conversion go hand in hand
Training + standards + real-world reps beat generic scripts and YouTube tactics

=== COMMENT RESPONSE RULES ===
Every comment response MUST do THREE things:
1. VALIDATE their experience or question (show you understand)
2. ADD VALUE (give them something useful, not just acknowledgement)
3. OPEN THE DOOR (invite further conversation via DM or booking a call)
NEVER respond with fewer than 3 sentences.

=== DM CONVERSATION FLOW ===
Phase 1 OPENER: Warm, personal, reference their engagement. No selling.
Phase 2 SITUATION: Understand where they are. Which scenario? Experience level? Current income?
Phase 3 PAIN: Dig into what is holding them back. Use their words. What is the cost of staying stuck?
Phase 4 GAIN: What does success look like? What changes when they can close high-ticket deals?
Phase 5 BRIDGE: "Based on what you've shared, I think it's worth having a proper conversation about whether this is the right fit."
Phase 6 BOOKING: Send the booking link. Confirm they have booked.
Phase 7 FOLLOW-UP: Until they book, block, or opt out.

=== DM RULES ===
Personalise every message. Reference their specific situation.
Ask questions, don't pitch. 80% questions, 20% statements.
Mirror their language back to them.
NEVER discuss pricing in DMs. Always redirect to the discovery call.
NEVER say "guaranteed placement." Always say "guaranteed interview opportunities." Whether they get the role depends on client needs.

=== OBJECTION HANDLING ===
Price: Redirect to discovery call. "I'd rather walk you through it properly on a call so you can see the full picture."
Scepticism: "I get it. Most sales programmes are garbage. That's why we do live training, real roleplays, and real call breakdowns. Not pre-recorded fluff."
Time: "The training is designed for people with jobs. You can do this alongside whatever you're doing now."
Experience: "Most people who join have zero sales experience. That's the whole point."
Other programmes: "Have they got you on calls earning commissions? If not, that tells you everything."

=== BOOKING LINK ===
https://api.leadconnectorhq.com/widget/bookings/systemiseandselldiscoverycall

=== SKOOL COMMUNITY ===
https://www.skool.com/systemiseandsell/about

=== NEVER DO ===
Promise guaranteed income
Promise guaranteed placement (always "guaranteed interview opportunities")
Discuss pricing in DMs
Use hype language, excessive emojis, or motivational speaker energy
Give one-line throwaway responses
Send booking link before qualifying
Say "you either have it or you don't in sales"
Say "you don't need training, just grab a free script online"
Use em dashes or en dashes as punctuation"""


RESPONSE_TYPES = {
    "Comment Response": "Public reply to a comment on a post",
    "Inbound DM": "Someone DMed us first",
    "Outbound DM": "We're reaching out to them first",
    "Post Like": "Someone liked a post, reach out to them",
    "New Follow": "Someone just followed the account",
    "Bridge to Call": "Transition toward a discovery call",
    "Send Booking Link": "They agreed to a call. Send the link",
    "Follow-Up": "They've gone quiet, need to re-engage",
    "Objection Handle": "They've raised a concern or pushback",
}

TYPE_PROMPTS = {
    "Comment Response": 'Generate 3 PUBLIC COMMENT RESPONSES. (1) Validate, (2) Add value, (3) Open door to DMs or call. Min 3 sentences. Different: empathetic, direct/challenging, credentials-led.',
    "Inbound DM": 'Generate 3 INBOUND DM RESPONSES. Acknowledge, qualify their situation, feel personal. Different: warm/curious, direct/qualifying, story-driven.',
    "Outbound DM": 'Generate 3 OUTBOUND DM OPENERS. Reference something specific about them, establish credibility, soft question. Different: curiosity-led, authority-led, results-led.',
    "Post Like": 'Generate 3 DM OPENERS for a post like. Thank, reference post topic, soft question. Different: warm, insight-led, short.',
    "New Follow": 'Generate 3 WELCOME DMs. Thank, explain what BDC shares, ask what brought them. Different: warm, credentials-led, short/punchy.',
    "Bridge to Call": 'Generate 3 BRIDGE MESSAGES toward a discovery call. Reference what they shared. Position call as exploratory, no pressure. Do NOT include booking link yet. Different: soft/conversational, summary-based, direct with urgency.',
    "Send Booking Link": 'Generate 3 BOOKING MESSAGES. They agreed to a call. Include the booking link: https://api.leadconnectorhq.com/widget/bookings/systemiseandselldiscoverycall and encourage booking. Different: warm/encouraging, brief/action-focused, reaffirms value.',
    "Follow-Up": 'Generate 3 FOLLOW-UPS. Re-engage with warmth + subtle urgency. Different: value-add, check-in, gentle nudge.',
    "Objection Handle": 'Generate 3 OBJECTION RESPONSES. Empathy + redirect to call. Different: validate/reframe, social-proof-driven, direct/challenging.',
}

PHASE_PROMPTS = {
    "Auto-detect": "Assess which phase this conversation is in based on the history, and generate the appropriate next message to progress naturally toward a discovery call booking.",
    "Opener": "OPENER phase. Warm, personal opening. No selling, no links.",
    "Situation": "SITUATION phase. Get them talking. What do they do now? Any sales experience? What caught their eye about high-ticket closing?",
    "Pain": "PAIN phase. Dig deeper. What is holding them back? What is the cost of staying where they are? Frustration, financial pressure, feeling stuck.",
    "Gain": "GAIN phase. Get them envisioning success. What changes when they can close high-ticket deals? Freedom, income, confidence, control.",
    "Bridge": "BRIDGE phase. Transition to suggesting a discovery call. Do NOT send the link yet. Frame it as 'let's have a proper conversation about whether this is the right fit.'",
    "Send Booking Link": "They agreed to a call. Send booking link: https://api.leadconnectorhq.com/widget/bookings/systemiseandselldiscoverycall",
    "Follow-Up": "FOLLOW-UP phase. Re-engage. Reference what they said before. Subtle urgency without pressure.",
}

PHASE_HINTS = {
    "Auto-detect": "AI decides based on history",
    "Opener": "Start the conversation",
    "Situation": "Understand where they are",
    "Pain": "What is holding them back?",
    "Gain": "What does success look like?",
    "Bridge": "Move toward the call",
    "Send Booking Link": "Send the link",
    "Follow-Up": "Re-engage",
}

COLOURS = [
    {"bg": "#dbeafe", "text": "#1e40af", "border": "#93c5fd"},
    {"bg": "#d1fae5", "text": "#065f46", "border": "#6ee7b7"},
    {"bg": "#fef3c7", "text": "#92400e", "border": "#fcd34d"},
]


# ─────────────────────────────────────────────
# HELPERS
# ─────────────────────────────────────────────

def strip_dashes(text):
    out = []
    for ch in text:
        code = ord(ch)
        if code in (8212, 8211, 8210, 8213, 65293, 65123, 11834, 11835, 65112):
            out.append(",")
        else:
            out.append(ch)
    result = "".join(out)
    return result.replace(" - ", ", ").replace(" -.", ".").replace(" -,", ",")


def generate_responses_streaming(message, context, response_type, thread_history="", phase="Auto-detect"):
    client = anthropic.Anthropic(api_key=st.secrets["ANTHROPIC_API_KEY"])

    history_block = f"FULL CONVERSATION HISTORY (oldest to newest):\n{thread_history}\n\n" if thread_history else ""
    phase_block = f"\nCONVERSATION PHASE: {PHASE_PROMPTS.get(phase, PHASE_PROMPTS['Auto-detect'])}\n"

    user_prompt = f"""MESSAGE TYPE: {response_type}

{history_block}{phase_block}
THEIR LATEST MESSAGE:
"{message.strip()}"

{f'ADDITIONAL CONTEXT:{chr(10)}{context.strip()}' if context.strip() else ''}

{TYPE_PROMPTS[response_type]}

CRITICAL: Write AS Marco / BDC in first person. No hype. No fluff. NEVER use dashes as punctuation. Use commas and full stops. NEVER discuss pricing. NEVER say "guaranteed placement", say "guaranteed interview opportunities."

Return ONLY a JSON array of exactly 3 objects with "label" and "text" keys. Separate paragraphs with double newlines. No markdown, no backticks. Just JSON. No dashes."""

    collected = ""
    with client.messages.stream(
        model="claude-haiku-4-5-20251001",
        max_tokens=2000,
        system=SYSTEM_PROMPT,
        messages=[{"role": "user", "content": user_prompt}],
    ) as stream:
        for text in stream.text_stream:
            collected += text

    parsed = json.loads(collected.replace("```json", "").replace("```", "").strip())
    for item in parsed:
        item["text"] = strip_dashes(item["text"])
    return parsed


def render_text_html(text):
    parts = []
    for line in text.split("\n"):
        if line.strip() == "":
            parts.append("<div style='height:10px;'></div>")
        else:
            parts.append(f"<p style='margin:0 0 6px 0;font-size:14px;line-height:1.7;color:#1a1a1a !important;'>{line}</p>")
    return "".join(parts)


def suggest_phase(messages):
    n = len(messages)
    if n == 0: return "Opener"
    all_text = " ".join(m["text"].lower() for m in messages)
    if any(w in all_text for w in ["book", "calendar", "discovery call", "link", "booking"]):
        return "Follow-Up"
    if n <= 2: return "Situation"
    if n <= 4: return "Pain"
    if n <= 6: return "Gain"
    if n <= 8: return "Bridge"
    return "Follow-Up"


def show_options(results, prefix, thread=None, tid=None, their_msg=""):
    for i, r in enumerate(results):
        c = COLOURS[i]

        st.markdown(
            f"<div style='display:inline-block;padding:5px 14px;border-radius:20px;font-size:12px;"
            f"font-weight:700;background:{c['bg']};color:{c['text']};margin-bottom:6px;'>"
            f"Option {i+1}: {r['label']}</div>",
            unsafe_allow_html=True,
        )

        st.markdown(
            f"<div class='response-card' style='border:1px solid {c['border']};'>"
            f"{render_text_html(r['text'])}</div>",
            unsafe_allow_html=True,
        )

        with st.expander("📋 Copy text", expanded=False):
            st.code(r["text"], language=None)

        if thread is not None and tid is not None:
            if st.button(f"✅ Use Option {i+1}", key=f"{prefix}_use_{i}", use_container_width=True):
                if not thread["messages"] or thread["messages"][-1].get("text") != their_msg.strip():
                    thread["messages"].append({"role": "them", "text": their_msg.strip()})
                thread["messages"].append({"role": "us", "text": r["text"]})
                try:
                    save_thread(tid, thread)
                except Exception:
                    pass
                st.session_state.thread_results = None
                st.rerun()

        st.markdown("")


# ─────────────────────────────────────────────
# SESSION STATE
# ─────────────────────────────────────────────

if "threads" not in st.session_state:
    try:
        st.session_state.threads = load_threads()
    except Exception:
        st.session_state.threads = {}
if "active_thread" not in st.session_state:
    st.session_state.active_thread = None
if "results" not in st.session_state:
    st.session_state.results = None
if "thread_results" not in st.session_state:
    st.session_state.thread_results = None
if "show_new_form" not in st.session_state:
    st.session_state.show_new_form = False


# ─────────────────────────────────────────────
# STYLES
# ─────────────────────────────────────────────

st.markdown("""<style>
.block-container { max-width: 800px; padding: 1rem 1rem 3rem 1rem; }

.msg-them {
    background: #f3f4f6 !important;
    color: #1a1a1a !important;
    border-radius: 12px;
    padding: 12px 16px;
    margin-bottom: 8px;
    font-size: 14px;
    line-height: 1.6;
}
.msg-them * { color: #1a1a1a !important; }

.msg-us {
    background: #dbeafe !important;
    color: #1a1a1a !important;
    border-radius: 12px;
    padding: 12px 16px;
    margin-bottom: 8px;
    font-size: 14px;
    line-height: 1.6;
}
.msg-us * { color: #1a1a1a !important; }

.msg-label {
    font-size: 11px;
    font-weight: 600;
    margin-bottom: 2px;
    color: #9ca3af;
}

.response-card {
    border-radius: 10px;
    padding: 16px;
    margin: 4px 0 8px 0;
    background: #ffffff !important;
}
.response-card p,
.response-card div,
.response-card span,
.response-card * {
    color: #1a1a1a !important;
}

div[data-testid="stRadio"] > div { flex-wrap: wrap; gap: 4px; }
code { white-space: pre-wrap !important; word-wrap: break-word !important; }
</style>""", unsafe_allow_html=True)


# ─────────────────────────────────────────────
# UI
# ─────────────────────────────────────────────

st.title("🎯 Billion Dollar Closers")
st.caption("DM & Comment Response Generator")

tab_quick, tab_threads = st.tabs(["⚡ Quick", "💬 Threads"])


# ═══════════════ QUICK TAB ═══════════════

with tab_quick:
    response_type = st.radio("Type", list(RESPONSE_TYPES.keys()), horizontal=True, key="qt")
    st.caption(RESPONSE_TYPES[response_type])
    message = st.text_area("Their message / comment", placeholder="Paste the comment or DM here...", height=100, key="qm")
    context = st.text_area("Context (optional)", placeholder="E.g. 'Bio: business coach, 2 years. Liked post about closing objections.'", height=60, key="qc")

    if st.button("**Generate 3 Responses**", type="primary", use_container_width=True, key="qb"):
        if not message.strip():
            st.warning("Paste their message first.")
        else:
            with st.spinner("Generating..."):
                try:
                    st.session_state.results = generate_responses_streaming(message, context, response_type)
                    st.session_state.result_type = response_type
                except Exception as e:
                    st.error(f"Failed: {str(e)}")

    if st.session_state.results:
        st.markdown("---")
        show_options(st.session_state.results, "q")


# ═══════════════ THREADS TAB ═══════════════

with tab_threads:

    thread_names = {tid: f"{t['name']} ({len(t['messages'])} msgs)" for tid, t in st.session_state.threads.items()}

    col_sel, col_new, col_ref = st.columns([3, 1, 1])
    with col_sel:
        options = ["-- Select --"] + list(thread_names.keys())
        labels = ["-- Select a conversation --"] + list(thread_names.values())
        current_idx = 0
        if st.session_state.active_thread in options:
            current_idx = options.index(st.session_state.active_thread)
        selected = st.selectbox(
            "Conversation", options, index=current_idx,
            format_func=lambda x: labels[options.index(x)] if x in options else x,
            key="tsel", label_visibility="collapsed",
        )
        if selected != "-- Select --" and selected != st.session_state.active_thread:
            st.session_state.active_thread = selected
            st.session_state.thread_results = None
            st.rerun()

    with col_new:
        if st.button("➕ New", use_container_width=True, key="new_btn"):
            st.session_state.show_new_form = not st.session_state.show_new_form
            st.rerun()
    with col_ref:
        if st.button("🔄", use_container_width=True, key="ref_btn"):
            try:
                st.session_state.threads = load_threads()
                st.rerun()
            except Exception as e:
                st.error(str(e))

    if st.session_state.show_new_form or not st.session_state.threads:
        with st.container():
            st.markdown("**New Conversation**")
            nn = st.text_input("Name", placeholder="e.g. James T", key="nn")
            nc = st.text_input("Context", placeholder="e.g. Business coach, 3 years, struggles closing on calls", key="nc")
            if st.button("Create", use_container_width=True, key="ncr"):
                if nn.strip():
                    tid = f"t_{datetime.now().strftime('%Y%m%d%H%M%S')}_{len(st.session_state.threads)}"
                    td = {"name": nn.strip(), "context": nc.strip(), "messages": [], "created": datetime.now().isoformat()}
                    st.session_state.threads[tid] = td
                    try:
                        save_thread(tid, td)
                    except Exception:
                        pass
                    st.session_state.active_thread = tid
                    st.session_state.thread_results = None
                    st.session_state.show_new_form = False
                    st.rerun()
            if st.button("Cancel", use_container_width=True, key="ncn"):
                st.session_state.show_new_form = False
                st.rerun()
            st.markdown("---")

    tid = st.session_state.active_thread
    if tid and tid in st.session_state.threads:
        thread = st.session_state.threads[tid]

        st.markdown(f"### {thread['name']}")
        if thread["context"]:
            st.caption(f"Context: {thread['context']}")

        if thread["messages"]:
            for msg in thread["messages"]:
                if msg["role"] == "them":
                    st.markdown(f"<div class='msg-label'>THEM:</div><div class='msg-them'>{msg['text']}</div>", unsafe_allow_html=True)
                else:
                    st.markdown(f"<div class='msg-label'>US:</div><div class='msg-us'>{msg['text']}</div>", unsafe_allow_html=True)
            st.markdown("---")

        suggested = suggest_phase(thread["messages"])
        st.markdown(f"**Phase** (suggested: {suggested})")
        phase = st.radio("Phase", list(PHASE_PROMPTS.keys()), horizontal=True, key=f"ph_{tid}")
        st.caption(PHASE_HINTS.get(phase, ""))

        rtype = st.radio("Message type", list(RESPONSE_TYPES.keys()), horizontal=True, key=f"rt_{tid}")
        their_msg = st.text_area("Their latest message", placeholder="Paste what they said or describe engagement...", height=80, key=f"tm_{tid}")

        col1, col2 = st.columns([2, 1])
        with col1:
            gen = st.button("**Generate**", type="primary", use_container_width=True, key=f"tg_{tid}")
        with col2:
            log = st.button("Log msg only", use_container_width=True, key=f"tl_{tid}")

        if log:
            if not their_msg.strip():
                st.warning("Type their message first.")
            else:
                thread["messages"].append({"role": "them", "text": their_msg.strip()})
                try:
                    save_thread(tid, thread)
                except Exception:
                    pass
                st.rerun()

        if gen:
            if not their_msg.strip():
                st.warning("Type their message first.")
            else:
                history = "\n\n".join([f"{'THEM' if m['role']=='them' else 'US'}: {m['text']}" for m in thread["messages"]])
                with st.spinner("Generating..."):
                    try:
                        st.session_state.thread_results = generate_responses_streaming(their_msg, thread.get("context", ""), rtype, history, phase)
                    except Exception as e:
                        st.error(f"Failed: {str(e)}")

        if st.session_state.thread_results:
            st.markdown("---")
            show_options(st.session_state.thread_results, f"t_{tid}", thread=thread, tid=tid, their_msg=their_msg)

        with st.expander("🗑️ Delete conversation"):
            if st.button("Confirm delete", key=f"del_{tid}"):
                try:
                    delete_thread_db(tid)
                except Exception:
                    pass
                del st.session_state.threads[tid]
                st.session_state.active_thread = None
                st.session_state.thread_results = None
                st.rerun()

    elif not st.session_state.show_new_form and st.session_state.threads:
        st.info("Select a conversation above, or create a new one.")
