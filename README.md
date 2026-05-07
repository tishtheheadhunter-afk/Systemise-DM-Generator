# Systemise DM Generator (BDC Bot)

DM and comment response generator for Marco Fernandes / Systemise and Sell, focused on the **High-Ticket Closer Mastery** programme.

## What it does

The setter pastes a prospect's message (or full thread). The bot generates 3 response options in Marco Fernandes' voice, optimised for one of 12 specific situations:

1. Inbound DM Opener
2. Outbound DM Opener
3. Comment Reply
4. New Follow Welcome
5. Post Like Outreach
6. Push to Call
7. Send Booking Link
8. Skool Fallback (when prospect declines call due to investment/timing)
9. Skool Re-engagement (community member hit qualification signals)
10. General Objection Handle
11. Follow-up
12. Send Skool Link

The setter chooses the route. The bot writes the message.

## Architecture

The system prompt is built dynamically from markdown files in `context/` and `examples/` at runtime. Edit a markdown file, refresh the app, the new context is live. There is no separate hardcoded prompt to keep in sync.

```
Systemise-DM-Generator/
├── bdc_app.py                  # Streamlit app
├── requirements.txt
├── .gitignore
├── supabase_setup.sql
├── .streamlit/
│   └── secrets.toml.template
├── context/                    # System prompt source files
│   ├── 01_business_context.md
│   ├── 02_marco_voice.md
│   ├── 03_offer_high_ticket_closer_mastery.md
│   ├── 04_the_closing_room_skool.md
│   ├── 05_qualification_arc.md
│   ├── 06_hook_formulas.md
│   └── 07_forbidden_angles.md
└── examples/                   # Worked examples per response type
    ├── 01_inbound_dm_opener.md
    ├── 02_outbound_dm_opener.md
    ├── 03_comment_reply.md
    ├── 04_new_follow_welcome.md
    ├── 05_post_like_outreach.md
    ├── 06_push_to_call.md
    ├── 07_send_booking_link.md
    ├── 08_skool_fallback.md
    ├── 09_skool_reengagement.md
    ├── 10_objection_handle.md
    ├── 11_follow_up.md
    └── 12_send_skool_link.md
```

## How to iterate

1. Open the repo in Claude Code
2. Edit any file in `context/` or `examples/`
3. Commit and push
4. Streamlit Cloud auto-redeploys
5. Refresh the live app, new behaviour is live

## Deployment

- **Streamlit Cloud**: app deploys from this repo, main branch, `bdc_app.py` as entry point
- **Live URL**: https://systemise-dm-generator-cgexvueejmckltny3uab4h.streamlit.app
- **Supabase**: thread persistence (table `bdc_dm_threads`)
- **Anthropic API**: claude-sonnet-4-20250514 for generation

## Setup

1. Run `supabase_setup.sql` in your Supabase SQL editor
2. Configure secrets in Streamlit Cloud: `ANTHROPIC_API_KEY`, `SUPABASE_URL`, `SUPABASE_ANON_KEY`
3. App is live

## Iteration philosophy

The bot's quality is determined by the markdown files in `context/` and `examples/`, not by the app code. To improve outputs, improve the markdown. The app is just plumbing.
