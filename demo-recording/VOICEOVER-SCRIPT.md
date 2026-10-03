# Demo Video — Voice-Over Script

**Video:** `demo.mp4` (3 min 36 sec, 1920×1080)
**Recorded from:** the `tp1` org, General Agent, live Agentforce conversation
**Note:** timings are approximate (±5s). Watch once and align.

---

## 0:00 – 0:20 · Opening

> "Warm welcome to everyone listening. I am [YOUR NAME] and I am the leader of this
> team. My fellow teammates are Premkumar P, Bharath Kumar P, Vikash V, Pugazhendhi P
> and Aswin M. We are from [COLLEGE NAME] and our team ID is [TEAM ID].
>
> Our project is the **Customer Support Ticket Priority Prediction and Automated
> Assignment System**, built on Salesforce with Agentforce AI. In this video we will
> walk through the complete support-ticket lifecycle — data modelling, priority
> prediction, automated assignment, SLA risk detection, and AI-assisted ticket
> handling."

*(On screen: Object Manager)*

---

## 0:20 – 0:38 · The problem and our solution

> "Booking a support ticket usually needs a phone call or a support form, and
> prioritisation is manual. Customers wait behind lower-priority tickets, agents
> triage by hand, and managers have no central view of urgency.
>
> Our system solves this on a single platform. The ticket description is analysed
> automatically, priority is predicted as High, Medium or Low, urgent tickets raise
> a task and get assigned, and Agentforce lets a user simply ask **'what is the
> priority of this ticket?'** in plain language."

*(On screen: object detail, then Fields & Relationships scrolling)*

---

## 0:38 – 1:10 · The data model

> "This is the Support Ticket Intelligence custom object. It holds **eleven fields** —
> an auto-numbered Ticket Number in the format TKT-0000, lookups to Account,
> Contact and User, the Description, a Priority Level picklist, Status, Created
> Date, an SLA Breach Risk checkbox and Resolution Time.
>
> The object relates to the standard Account object through a Customer lookup, so we
> can find the latest ticket for any account by name."

*(On screen: All Tickets list view)*

> "Here is our data. Three tickets — **TKT-0001 is High with SLA breach risk
> flagged**, TKT-0002 is Medium and TKT-0003 is Low. Notice the priority was written
> back to the record by the automation, not typed in by hand."

*(On screen: ticket record)*

> "Opening TKT-0001, you can see the Urgent Ticket Handling tasks in the Activity
> panel — those were created by the Flow, not by a person."

---

## 1:10 – 1:40 · The Flow — the backbone

*(On screen: Flow Builder)*

> "This is the backbone of the solution — an **Auto-Launched Flow** called Support
> Ticket Intelligence. It is auto-launched with no trigger, because Agentforce can
> only invoke an auto-launched Flow.
>
> It takes **one input**, the Account Name, and returns **five outputs** — the account
> ID, ticket ID, priority level, assigned agent and an action message.
>
> The Flow retrieves the account with a Get Records element, then fetches the latest
> ticket for that account. A Decision element then analyses the description: if it
> contains **urgent, not working or failure** it is High priority; **issue, slow or
> delay** is Medium; anything else is Low.
>
> On the High branch only, it creates a task and assigns a senior support agent. It
> also checks whether the ticket is more than two days old and flags SLA breach risk,
> and it writes the predicted priority back to the ticket record."

---

## 1:40 – 1:55 · Permission set

*(On screen: permission set)*

> "For security we created a permission set called Support Ticket Intelligence Access.
> It grants read, create and edit on the object and field-level access to all eleven
> fields, and it is assigned to the user. Without this, the fields would be invisible
> to the API even for an administrator."

---

## 1:55 – 2:10 · Agentforce setup

*(On screen: Agentforce Agents)*

> "We then turned on Agentforce in Setup. Here you can see the Agentforce toggle is
> on, and the agents available in the org."

---

## 2:10 – 2:40 · The agent and the subagent

*(On screen: Agent Builder — Subagents panel)*

> "This is the Agentforce Builder. In the Subagents panel you can see **Support Ticket
> Priority Analysis** — that is our subagent.
>
> It has a classification description and a scope that keep it focused on ticket
> analysis only, and five instructions that tell the agent how to behave.
>
> On the actions tab, our subagent has one action: **Support Ticket Intelligence**,
> a Flow-based action referencing the Flow we just built — with the Account Name as a
> required input collected from the user, and all five outputs shown in conversation."

---

## 2:40 – 3:36 · Live demo

*(On screen: Conversation Preview)*

> "Now the interesting part. This is the Agentforce conversation. I will ask it about
> a ticket using plain language."

**Type:** *"What is the priority of the support ticket for Acme Corporation?"*

> "You can see the agent's reasoning. It selected the **Support Ticket Priority
> Analysis** subagent, then launched the **Support Ticket Intelligence** action,
> passing in the account name. The Flow returned **High priority** with the assigned
> agent — and the reply says *'High priority ticket detected. Assigned to senior
> agent.'* with the senior support agent and the ticket ID."

**Type:** *"What is the priority of the support ticket for Globex Systems?"*

> "The second case returns **Medium priority** — *'Ticket marked as medium priority.
> Will be handled shortly.'* No task is created and no agent is paged for a medium
> ticket, which is exactly the intended behaviour."

**Type:** *"What is the priority of the support ticket for Initech Solutions?"*

> "And the third returns **Low priority** — queued for processing, no task raised."

---

## Closing

> "So this is our project — Customer Support Ticket Priority Prediction and Automated
> Assignment using Agentforce. It predicts ticket priority from the customer's own
> words, creates and assigns urgent work automatically, flags SLA risk, and answers
> in plain language. Thank you for listening."

---

## Recording tips

- **Team ID** — you must supply this; the sample video opens with one. I don't have it.
- **Name and college** — fill in the bracketed placeholders before recording.
- Keep pace with the video: each screen gets roughly 20–40 seconds of narration.
- The three agent answers are the highlight — give them room, don't rush.
- The sample demo was 5:43. Yours at 3:36 is tighter; that's fine.
