# Claude Code Project Instructions: Systemise DM Generator

## What this project is

A Streamlit-based DM/comment response generator for Marco Fernandes (Systemise and Sell). It generates messages for the **High-Ticket Closer Mastery** programme ($1,997 fast action / $2,997 list), with a fallback route to the free Skool community (The Closing Room) when prospects decline the paid call on grounds of investment/timing.

## Critical positioning rules

**Marco Fernandes ≠ Sir Marco Robinson.** They are two different people:

* **Marco Fernandes** = our Marco. CTO of Systemise and Sell. 39 years in sales, $200M+ personal sales. Runs the High-Ticket Closer Mastery programme. This bot is for HIM.
* **Sir Marco Robinson** = bestselling author. Different offer entirely (Co-Author Authority Book). NOT this bot's audience.

If you ever see references to "Sir Marco" or "the book" or "2 million followers" or "international bestseller" in this bot's outputs, that is a bug. Marco Fernandes is high-ticket sales training, not publishing.

## How to iterate on this bot

The system prompt is built dynamically from `context/\\\*.md` and `examples/\\\*.md` at runtime. The app reads them, concatenates them into the prompt, sends to Claude. **Edit the markdown, refresh the app, new behaviour is live.**

To improve outputs:

1. Identify which file controls the behaviour you want to change:

   * Voice/tone issues → `context/02\\\_marco\\\_voice.md`
   * Offer details wrong → `context/03\\\_offer\\\_high\\\_ticket\\\_closer\\\_mastery.md`
   * Skool routing wrong → `context/04\\\_the\\\_closing\\\_room\\\_skool.md`
   * Specific response type weak → `examples/0X\\\_\\\*.md`
2. Edit that file
3. Commit with a clear message ("improve Skool fallback opener", "fix tone in objection handle examples", etc.)
4. Push
5. Refresh the deployed Streamlit app

## What NOT to do

* **Do not modify `bdc\\\_app.py`** unless the app is broken or a feature needs to change. The app is plumbing. Quality lives in the markdown.
* **Do not hardcode the system prompt.** Always edit the source files.
* **Do not use em dashes.** Project-wide rule. Use commas, full stops, colons. Hyphens only inside compound words like "high-ticket" or "1-on-1".
* **Do not invent stats or claims** about Marco Fernandes. Only use the credentials documented in `context/01\\\_business\\\_context.md`.
* **Do not lift Sir Marco specifics** like "2 million followers" or "international bestselling author". Wrong person.

## Voice rules summary

Marco Fernandes' voice is:

* Direct, no-BS, tough love mentor
* "Calm authority, not hype"
* "Data, not emotion"
* 39 years and $200M+ in sales is the credibility anchor, reference it
* Sparing emoji use (one 😊 at end of a softening question is fine; never on every line)
* Never sounds like a guru or motivational speaker
* Sounds like Marco texting a friend who asked about the programme

## Forbidden phrases / claims

See `context/07\\\_forbidden\\\_angles.md` for the full list. Highlights:

* Never say "guaranteed placement", only "guaranteed interview opportunities"
* Never discuss pricing in DMs
* Never imply sales is innate or "you either have it or you don't"
* Never use "guru-speak" or hype language

## Skool fallback rules

The Skool community is **only** offered when the prospect declines the call on grounds of investment/timing/not-ready-to-pay. It is NOT offered when:

* They say "not interested"
* They say "wrong fit"
* They've ghosted (use Follow-up instead)

See `context/04\\\_the\\\_closing\\\_room\\\_skool.md` and `examples/08\\\_skool\\\_fallback.md`.

## Testing changes

Run locally:

```bash
streamlit run bdc\\\_app.py
```

Set environment variables in `.streamlit/secrets.toml` (use `secrets.toml.template` as base).

## Common tasks Claude Code might be asked to do

* "Improve the Skool fallback examples, make them less salesy"
* "Add a new response type for X"
* "The objection handle responses sound robotic, fix them"
* "Update the offer details, Marco's increased price to $2,497"
* "Add a section to marco\_voice.md about how he handles 'I've been burned by other programmes' objections"

