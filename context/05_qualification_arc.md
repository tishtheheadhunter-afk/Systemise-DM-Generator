# The Qualification Arc

The reference shape of an inbound DM conversation that ends in a booked call. The bot should know this arc as guidance, but **always generate the next single message based on conversation context**, not the entire arc at once.

The setter pastes the thread so far. The bot reads where they are. Generates the right next message. Some prospects skip steps. Some need extra. The arc is a guide, not a script.

## The 5-step qualification arc

### Step 1, Opener (Inbound DM Opener)

Acknowledge the inbound, brief offer summary, permission to ask questions.

**Shape:**
> "Thanks for reaching out [name]. Quick rundown, [1-2 sentences on what HTCM is, anchored on Marco's credentials]. If that's the kind of thing you're looking at, mind if I ask a couple of quick questions to see if it's the right fit?"

### Step 2, Where they're at (Situation)

Get the prospect's current state. Are they closing already, working towards it, or completely fresh?

**Shape:**
> "Great. Where are you at right now with sales, closing already, working towards it, or coming in fresh?"

### Step 3, Why this, why now (Pain / Driver)

Feed back what they shared in 1-2 sentences. Then ask what made them start looking into this.

**Shape:**
> "[Brief feedback of their situation.] Just curious, what made you start looking into high-ticket closing specifically?"

### Step 4, What success looks like (Goals / Future Pace)

Feed back their why. Then ask what success would look like / why now is the right time.

**Shape:**
> "[Brief feedback.] And what was it that made you decide now's the right time to be looking at making this kind of move?"

### Step 5, Bridge to call (Push to Call)

Feed back their goals. Position the call as a deeper conversation with the team, not a sales pitch.

**Shape:**
> "[Brief feedback.] Based on our convo [name], I think it's worth exploring deeper. Mind if I get you a call with our team to dig into where you're at and what you're looking to achieve, and see if it's a fit from both sides? They'll walk you through how the programme works and the next steps. Sound good?"

### Step 6, Send Booking Link

Once they say yes, deliver the link cleanly.

**Shape:**
> "Great, here you go, https://api.leadconnectorhq.com/widget/bookings/systemiseandselldiscoverycall
>
> Drop me a note when you've booked so I can confirm it on our side."

## Variations and flexibility

### Hot prospects can skip steps

Some prospects open with: "I want to learn high-ticket closing, I have $X to invest, when can I start?" That's a Step 5 prospect on Day 1. Don't drag them through Steps 2-4 just to follow the arc. Acknowledge their clarity, send them to the call.

### Cold prospects need more

Some prospects ask vague questions: "What is this?" That's pre-Step-1. Answer with brief offer info, then start Step 1 once they engage.

### Hesitant prospects need lateral moves

Some prospects engage but don't move forward. They ask a question that pulls sideways ("How long does it take?", "What if I've never sold before?"). Answer the lateral question genuinely, then return to the arc at the appropriate step.

## What the bot generates

Per setter request, the bot generates **one message** that fits the current conversation state. The setter says (or implies via the thread):

- "This is reply 1, they just DM'd cold" → Step 1 (Inbound DM Opener)
- "They answered the situation question, here's what they said" → Step 3 (Pain / Driver)
- "They're warm, push to call" → Step 5
- "They said yes to the call" → Step 6 (Send Booking Link)

The bot reads the thread, infers the right step, generates the right message.

## What the setter sees

The setter has this 5-step arc as a reference card in the app sidebar. They know where they're aiming. They use the bot to generate each step's message in Marco Fernandes' voice with full personalisation to what the prospect said.
