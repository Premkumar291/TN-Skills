# Customer Support Ticket Priority Prediction and Automated Assignment System Using Agentforce

An intelligent ticket-triage system built on Salesforce. A custom object stores support
tickets, an Auto-Launched Flow reads each ticket description, predicts its priority from the
language the customer used, raises a task for genuinely urgent cases, writes the decision
back to the record, and hands the result to an Agentforce agent that explains what it did.

## The problem

Support teams receive a large volume of tickets daily, but prioritisation and assignment are
manual. Critical issues sit in the same queue as routine questions, so they are resolved late
and customer satisfaction suffers.

## What it does

- **Classifies priority automatically** from the ticket description, using keyword analysis
  (`urgent` / `not working` / `failure` → High; `issue` / `slow` / `delay` → Medium; else Low)
- **Raises a task** for High-priority tickets only, so agents are not paged for routine work
- **Assigns an agent** automatically on the High branch
- **Flags SLA breach risk** when a ticket is older than two days
- **Writes the predicted priority back** to the ticket record
- **Reports back in plain language** through an Agentforce agent conversation

## Components

| Component | API Name | Notes |
|---|---|---|
| Custom object | `Support_Ticket_Intelligence__c` | 11 fields incl. lookups to Account, Contact, User |
| Auto-Launched Flow | `Support_Ticket_Intelligence` | Active; invoked by the agent |
| Permission set | `Support_Ticket_Intelligence_Access` | Object + field-level security |
| Page layout | `Support Ticket Intelligence Layout` | All fields visible on the record |
| Tab | `Support_Ticket_Intelligence__c` | Custom object tab |
| Agentforce subagent | `Support_Ticket_Priority_Analysis` | On General Agent |
| Agent action | `Support_Ticket_Intelligence` | Reference Action Type: Flow |

## Flow logic

```
Start
 └─ Get Account (by varAccountName)
     └─ Store Account Id
         └─ Get Ticket (latest for that account)
             └─ Store Ticket Id
                 └─ Check SLA Risk ──(older than 2 days)──> Flag SLA Risk
                     └─ Analyze Description
                         ├─ High   (urgent / not working / failure)
                         ├─ Medium (issue / slow / delay)
                         └─ Low    (default)
                             └─ Update Priority  (writes Priority_Level__c back)
                                 └─ Is High Priority ──(yes)──> Create Task
                                     └─ Set Assigned Agent
                                         └─ Set Final Message
```

**Variables** — input `varAccountName`; outputs `varAccountId`, `varTicketId`,
`varPriorityLevel`, `varAssignedTo`, `varActionMessage`.

## Verified results

| Account | Description keywords | Priority | Task | SLA risk |
|---|---|---|---|---|
| Acme Corporation | urgent, not working | **High** | Created | True |
| Globex Systems | slow, delay | **Medium** | None | False |
| Initech Solutions | *(none)* | **Low** | None | False |

Confirmed both at the flow level (direct invocation) and end-to-end through the Agentforce
agent conversation, where the agent selected the `Support Ticket Priority Analysis` subagent,
launched the `Support Ticket Intelligence` action, and reported
*"High priority ticket detected. Assigned to senior agent."*

## Two gotchas worth knowing

1. **Custom fields deployed via the Metadata API are invisible until field-level security is
   granted** — even to System Administrator. Querying them fails with "No such column", which
   reads like a missing field rather than a permissions problem. The
   `Support_Ticket_Intelligence_Access` permission set is what makes them visible.

2. **A Flow does not appear in an agent's action picker until it is registered as an Agent
   Action.** The subagent wizard shows "0 items" even for a valid, active flow. Registration
   happens via *This Subagent's Actions → New → Create New Action → Reference Action Type:
   Flow*.

## Repository layout

```
.
├── Customer Support Ticket Priority Prediction - Project Documentation.docx
├── Customer Support Ticket Priority Prediction and Automated Assignment System Using Agentforce.docx
├── agentforce-shots/                 # UI evidence captured from the org
└── support-ticket-agentforce/        # Salesforce DX source
    ├── force-app/main/default/
    │   ├── flows/
    │   ├── layouts/
    │   ├── objects/                  # object + all 11 fields
    │   ├── permissionsets/
    │   └── tabs/
    └── tools/                        # screenshot harness + doc generator
```

## Deploying

```bash
cd support-ticket-agentforce
sf org login web --alias myorg
sf project deploy start --source-dir force-app
sf org assign permset --name Support_Ticket_Intelligence_Access --on-behalf-of <username>
```

The permission set assignment is not optional — without it the fields stay invisible.
