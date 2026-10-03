#!/usr/bin/env python3
"""Build the project documentation .docx.

Mirrors the structure of the supplied sample ("WhatNext Vision Motors.docx"):
a milestone-based walkthrough with a screenshot for each UI action.
"""
import pathlib
import sys

from docx import Document
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.shared import Inches, Pt, RGBColor

SHOTS = pathlib.Path("/home/killermachine/Desktop/study/nm/agentforce-shots")
OUT = pathlib.Path(
    "/home/killermachine/Desktop/study/nm/"
    "Customer Support Ticket Priority Prediction - Project Documentation.docx"
)

TITLE = (
    "Customer Support Ticket Priority Prediction and Automated "
    "Assignment System Using Agentforce"
)


def add_shot(doc: Document, name: str, caption: str, width: float = 6.3) -> None:
    """Insert a screenshot with a caption, if the file exists."""
    path = SHOTS / name
    if not path.exists():
        p = doc.add_paragraph()
        r = p.add_run(f"[screenshot pending: {name}]")
        r.italic = True
        r.font.color.rgb = RGBColor(0x99, 0x33, 0x33)
        return
    doc.add_picture(str(path), width=Inches(width))
    doc.paragraphs[-1].alignment = WD_ALIGN_PARAGRAPH.CENTER
    cap = doc.add_paragraph()
    cap.alignment = WD_ALIGN_PARAGRAPH.CENTER
    run = cap.add_run(caption)
    run.italic = True
    run.font.size = Pt(9)
    run.font.color.rgb = RGBColor(0x55, 0x55, 0x55)


def bullet(doc: Document, text: str) -> None:
    doc.add_paragraph(text, style="List Bullet")


def numbered(doc: Document, text: str) -> None:
    doc.add_paragraph(text, style="List Number")


def build() -> Document:
    doc = Document()

    # ---- Title -------------------------------------------------------------
    t = doc.add_heading(TITLE, level=0)
    t.alignment = WD_ALIGN_PARAGRAPH.CENTER

    # ---- Use Case ----------------------------------------------------------
    doc.add_heading("Use Case", level=1)
    for para in [
        "Customer support teams receive a large number of tickets every day, but "
        "prioritising and assigning them is still largely manual. Critical issues sit "
        "in the same queue as routine questions, so they are resolved late and "
        "customer satisfaction suffers.",
        "This project builds an intelligent ticket triage system on Salesforce. A "
        "custom object stores the support tickets, an auto-launched Flow reads each "
        "ticket description, classifies its priority from the language the customer "
        "used, raises a task for genuinely urgent cases, and hands the result back to "
        "an Agentforce agent that explains what it did in plain language.",
        "The result is faster resolution of critical issues, work routed to the right "
        "agent without a human triaging by hand, and a measurable drop in manual "
        "effort for the support team.",
    ]:
        doc.add_paragraph(para)

    # ---- Requirements ------------------------------------------------------
    doc.add_heading("Requirements", level=1)
    bullet(doc, "Salesforce Developer Edition org with Agentforce enabled")
    bullet(doc, "Custom object: Support Ticket Intelligence")
    bullet(doc, "Fields and relationships for customer, contact, priority and assignment")
    bullet(doc, "Auto-Launched Flow performing keyword-based priority prediction")
    bullet(doc, "Field-level security so the flow and agent can read the fields")
    bullet(doc, "Agentforce agent with a Support Ticket Priority Analysis topic")
    bullet(doc, "Sample data covering High, Medium and Low scenarios")

    doc.add_heading("What you'll learn", level=1)
    for item in [
        "Data modelling — custom objects and lookups",
        "Field-level security and permission sets",
        "Auto-Launched Flows with decisions and record creation",
        "Agentforce agent topics and flow-backed actions",
        "Testing an automated triage system end to end",
    ]:
        bullet(doc, item)

    doc.add_page_break()

    # ---- Milestone 1 -------------------------------------------------------
    doc.add_heading("Milestone 1: Salesforce Developer Org", level=1)
    doc.add_paragraph(
        "Create a Developer Edition org at https://developer.salesforce.com/signup and "
        "log in. Confirm Agentforce is available under Setup — this project cannot be "
        "completed on an org without it."
    )
    add_shot(doc, "10_object_manager_list.png",
             "Setup → Object Manager, the starting point for the data model.")

    # ---- Milestone 2 -------------------------------------------------------
    doc.add_heading("Milestone 2: Objects & Relationships", level=1)
    doc.add_paragraph(
        "The project needs a single custom object to hold support tickets. It looks up "
        "to two standard objects so a ticket always belongs to a real customer and "
        "contact."
    )

    table = doc.add_table(rows=1, cols=3)
    table.style = "Light Grid Accent 1"
    hdr = table.rows[0].cells
    for i, h in enumerate(["Object", "Purpose", "Relationships"]):
        hdr[i].text = h
    for row in [
        ("Support_Ticket_Intelligence__c",
         "Stores support tickets and their predicted priority",
         "Lookup to Account and Contact; lookup to User for assignment"),
    ]:
        cells = table.add_row().cells
        for i, v in enumerate(row):
            cells[i].text = v

    doc.add_paragraph()
    doc.add_heading("Activity 1: Create the Support Ticket Intelligence object", level=2)
    numbered(doc, "From Setup, click Object Manager → Create → Custom Object.")
    numbered(doc, "Label: Support Ticket Intelligence")
    numbered(doc, "Plural Label: Support Ticket Intelligence")
    numbered(doc, "Record Name: Ticket Name, Data Type Text.")
    numbered(doc, "Tick Allow reports and Allow search, then Save.")
    add_shot(doc, "11_object_detail.png",
             "The completed object in Object Manager.")

    # ---- Milestone 3 -------------------------------------------------------
    doc.add_heading("Milestone 3: Fields & Relationships", level=1)
    doc.add_paragraph(
        "With the object in place, add the fields the flow will read and write. Each "
        "field below was added from Fields & Relationships → New."
    )

    fields = [
        ("Ticket Number", "Ticket_Number__c", "Auto Number", "TKT-{0000}"),
        ("Customer", "Customer__c", "Lookup (Account)", "Related account"),
        ("Contact", "Contact__c", "Lookup (Contact)", "Customer contact"),
        ("Issue Type", "Issue_Type__c", "Picklist", "Technical, Billing, General"),
        ("Description", "Description__c", "Long Text Area", "Issue details"),
        ("Priority Level", "Priority_Level__c", "Picklist", "Low, Medium, High"),
        ("Status", "Status__c", "Picklist", "New, In Progress, Resolved"),
        ("Created Date", "Created_Date__c", "Date", "Ticket date"),
        ("Assigned To", "Assigned_To__c", "Lookup (User)", "Support agent"),
        ("SLA Breach Risk", "SLA_Breach_Risk__c", "Checkbox", "Risk flag"),
        ("Resolution Time (hrs)", "Resolution_Time__c", "Number", "Time taken"),
    ]
    ftable = doc.add_table(rows=1, cols=4)
    ftable.style = "Light Grid Accent 1"
    h = ftable.rows[0].cells
    for i, v in enumerate(["Field Label", "API Name", "Data Type", "Description"]):
        h[i].text = v
    for row in fields:
        cells = ftable.add_row().cells
        for i, v in enumerate(row):
            cells[i].text = v

    doc.add_paragraph()
    add_shot(doc, "01_objectmanager_fields.png",
             "Fields & Relationships showing the completed field set.")

    # ---- Milestone 4 -------------------------------------------------------
    doc.add_heading("Milestone 4: Field-Level Security", level=1)
    doc.add_paragraph(
        "This step is easy to forget and costs hours if you do. Fields created through "
        "the Metadata API are NOT automatically visible to any profile — not even "
        "System Administrator. Until field-level security is granted, querying the "
        "field fails with \"No such column\", which looks like a missing field rather "
        "than a permissions problem."
    )
    doc.add_paragraph("Create a permission set and assign it to your user:")
    numbered(doc, "Setup → Permission Sets → New. Label: Support Ticket Intelligence Access.")
    numbered(doc, "Object Settings → Support Ticket Intelligence → grant Read, Create, Edit, Delete.")
    numbered(doc, "Edit each field and tick Readable (and Editable where appropriate).")
    numbered(doc, "Save, then use Manage Assignments to assign it to your user.")

    # ---- Milestone 5 -------------------------------------------------------
    doc.add_heading("Milestone 5: Sample Data", level=1)
    doc.add_paragraph(
        "Create three accounts and one ticket each, so every branch of the flow's "
        "keyword logic has something to match."
    )

    dtable = doc.add_table(rows=1, cols=3)
    dtable.style = "Light Grid Accent 1"
    h = dtable.rows[0].cells
    for i, v in enumerate(["Account", "Ticket", "Description"]):
        h[i].text = v
    for row in [
        ("Acme Corporation", "Production outage",
         "Urgent issue - production system is not working and all orders are failing."),
        ("Globex Systems", "Order processing lag",
         "The system is very slow and there is a delay in processing orders."),
        ("Initech Solutions", "Roadmap question",
         "Just a general query about the product roadmap."),
    ]:
        cells = dtable.add_row().cells
        for i, v in enumerate(row):
            cells[i].text = v

    doc.add_paragraph()
    add_shot(doc, "14_ticket_list_all.png",
             "All Tickets list view. TKT-0001 shows Priority High with SLA Breach Risk "
             "ticked; the newer tickets sit at Medium and Low.")
    add_shot(doc, "12_ticket_record.png",
             "A ticket record. The two Urgent Ticket Handling tasks in the Activity "
             "panel were created by the flow, not by hand.")

    doc.add_page_break()

    # ---- Milestone 6 -------------------------------------------------------
    doc.add_heading("Milestone 6: Auto-Launched Flow", level=1)
    doc.add_paragraph(
        "The flow is the brain of the system. It takes an account name, finds that "
        "customer's latest ticket, reads the description, decides a priority, and acts."
    )

    doc.add_heading("Input and output variables", level=2)
    vtable = doc.add_table(rows=1, cols=3)
    vtable.style = "Light Grid Accent 1"
    h = vtable.rows[0].cells
    for i, v in enumerate(["Variable", "Direction", "Purpose"]):
        h[i].text = v
    for row in [
        ("varAccountName", "Input", "Account name supplied by the agent"),
        ("varAccountId", "Output", "Resolved account Id"),
        ("varTicketId", "Output", "Latest ticket Id"),
        ("varPriorityLevel", "Output", "High / Medium / Low"),
        ("varAssignedTo", "Output", "Agent assigned to the ticket"),
        ("varActionMessage", "Output", "Message returned to the conversation"),
    ]:
        cells = vtable.add_row().cells
        for i, v in enumerate(row):
            cells[i].text = v

    doc.add_paragraph()
    doc.add_heading("Flow logic", level=2)
    numbered(doc, "Get Account — Get Records on Account where Name equals varAccountName.")
    numbered(doc, "Store Account Id — assign varAccountId from Get_Account.Id.")
    numbered(doc, "Get Ticket — Get Records on Support Ticket Intelligence where Customer equals varAccountId, newest first.")
    numbered(doc, "Store Ticket Id — assign varTicketId from Get_Ticket.Id.")
    numbered(doc, "Analyze Description — Decision. High if the description contains "
                  "\"urgent\", \"not working\" or \"failure\"; Medium if it contains "
                  "\"issue\", \"slow\" or \"delay\"; otherwise Low.")
    numbered(doc, "Set Priority Level — assign varPriorityLevel on each branch.")
    numbered(doc, "Is High Priority — Decision on varPriorityLevel.")
    numbered(doc, "Create Task — only on the High branch. Subject \"Urgent Ticket "
                  "Handling\", Priority High, Status Not Started.")
    numbered(doc, "Set Assigned Agent — assign varAssignedTo to \"Senior Support Agent\".")
    numbered(doc, "Set Final Message — assign varActionMessage per priority.")

    doc.add_paragraph()
    doc.add_paragraph(
        "Important: every Get Records element must have \"Only the first record\" "
        "selected. Without it the element returns a collection, and referencing "
        "Get_Ticket.Description__c then fails with a misleading error saying the field "
        "does not exist."
    )

    doc.add_heading("Activity: build the flow", level=2)
    numbered(doc, "Setup → Flows → New Flow → Auto-Launched Flow.")
    numbered(doc, "Create the six variables listed above, marking the outputs as "
                  "Available for output.")
    numbered(doc, "Add the elements in the order shown.")
    numbered(doc, "Save as Support Ticket Intelligence, then click Activate.")
    add_shot(doc, "05_flow_builder_active.png",
             "The completed flow, active, with all elements wired.")

    doc.add_page_break()

    # ---- Milestone 7 -------------------------------------------------------
    doc.add_heading("Milestone 7: Agentforce Configuration", level=1)
    doc.add_paragraph(
        "Finally, expose the flow to an Agentforce agent so a support user can ask a "
        "question in plain language and get the triage decision back."
    )
    numbered(doc, "Setup → Quick Find → Agents. Confirm the Agentforce toggle is On.")
    numbered(doc, "Open an agent in the Builder (this project uses General Agent).")
    numbered(doc, "Deactivate the agent — agent changes are only permitted while it is deactivated.")
    numbered(doc, "In the Subagents panel choose New → New Subagent.")
    numbered(doc, "Describe the job in plain language; the Builder generates the name, "
                  "classification description, scope and instructions.")
    numbered(doc, "Rename it to Support Ticket Priority Analysis (API name "
                  "Support_Ticket_Priority_Analysis).")
    numbered(doc, "On the actions step, do NOT expect the flow in the picker yet — see the "
                  "note below.")
    numbered(doc, "Finish the subagent, then open This Subagent's Actions → New → "
                  "Create New Action.")
    numbered(doc, "Reference Action Type: Flow. Reference Action: Support Ticket Intelligence.")
    numbered(doc, "Set the Loading Text, tick Collect data from user on varAccountName, and "
                  "tick Show in conversation on all five outputs.")
    numbered(doc, "Finish, then Activate the agent.")
    add_shot(doc, "06_agentforce_agents.png",
             "Agentforce Agents in Setup, with the Agentforce toggle switched on.")
    add_shot(doc, "20_agent_active_subagent.png",
             "Support Ticket Priority Analysis configured on General Agent, with the agent active.")
    add_shot(doc, "21_subagent_actions_flow.png",
             "The subagent's actions list showing the Support Ticket Intelligence flow attached.")
    add_shot(doc, "22_subagents_list.png",
             "All four subagents on General Agent, including the new one.")

    doc.add_heading("Note: registering a flow as an agent action", level=2)
    doc.add_paragraph(
        "A Flow does not appear in the subagent's action picker until it has been registered "
        "as an agent action. On the subagent creation wizard, the action list will show "
        "\"0 items\" even for a valid, active flow — including when filtered by name. This is "
        "not a fault in the flow."
    )
    doc.add_paragraph(
        "The registration step is New → Create New Action on the This Subagent's Actions tab. "
        "That dialog accepts Reference Action Type = Flow, and the flow appears there. Once "
        "created, it shows up in the subagent's action list and can be referenced."
    )

    doc.add_paragraph(
        "Topic behaviour: collect the Account Name from the user, call the flow, then report "
        "the priority, the assigned agent and the action message in plain language. The topic "
        "must not update records or send email directly — the flow performs every action."
    )

    # ---- Milestone 8 -------------------------------------------------------
    doc.add_heading("Milestone 8: Testing", level=1)
    doc.add_paragraph(
        "The flow was invoked with each account name and the returned variables "
        "checked. All three keyword scenarios behave as specified."
    )

    rtable = doc.add_table(rows=1, cols=5)
    rtable.style = "Light Grid Accent 1"
    h = rtable.rows[0].cells
    for i, v in enumerate(["Input", "Keywords", "Priority", "Task created", "Message"]):
        h[i].text = v
    for row in [
        ("Acme Corporation", "urgent, not working", "High", "Yes",
         "High priority ticket detected. Assigned to senior agent."),
        ("Globex Systems", "slow, delay", "Medium", "No",
         "Ticket marked as medium priority. Will be handled shortly."),
        ("Initech Solutions", "none", "Low", "No",
         "Tickets are low priority and queued for processing."),
    ]:
        cells = rtable.add_row().cells
        for i, v in enumerate(row):
            cells[i].text = v

    doc.add_paragraph()
    doc.add_paragraph(
        "Only the High priority ticket produced a task, which is the specified "
        "behaviour. Medium and Low tickets are classified and queued without paging an "
        "agent. The flow also writes the predicted priority back to the ticket record and "
        "flags SLA breach risk for anything raised more than two days ago."
    )

    doc.add_heading("End-to-end test through the agent", level=2)
    doc.add_paragraph(
        "The flow was also exercised through the agent conversation, which is the real "
        "test of the system: the agent must pick the right subagent, call the flow with "
        "the user's input, and report the result back in plain language."
    )
    doc.add_paragraph(
        "Asking \"What is the priority of the support ticket for Acme Corporation?\" "
        "produced: Subagent Selected — Support Ticket Priority Analysis, then Action "
        "Launched — Support Ticket Intelligence (0.63 sec) with input "
        "{\"varAccountName\": \"Acme Corporation\"} and output returning "
        "varPriorityLevel \"High\"."
    )
    add_shot(doc, "23_agent_test_high.png",
             "Agent conversation: the High branch, showing subagent and action selection.")
    add_shot(doc, "24_agent_test_low.png",
             "Agent conversation: the Low branch for Initech Solutions.")

    doc.add_heading("Expected outcome", level=2)
    for item in [
        "Critical issues are identified from the customer's own words",
        "Urgent tickets raise a task immediately instead of waiting for manual triage",
        "Assignment happens automatically for high priority work",
        "Support staff spend their time resolving rather than sorting",
    ]:
        bullet(doc, item)

    doc.add_paragraph()
    doc.add_paragraph("Thank you.")
    return doc


def main() -> int:
    doc = build()
    doc.save(str(OUT))
    print("written:", OUT)
    print("size   :", f"{OUT.stat().st_size/1024:.1f} KB")
    return 0


if __name__ == "__main__":
    sys.exit(main())
