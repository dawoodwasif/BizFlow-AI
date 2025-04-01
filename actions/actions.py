from typing import Any, Text, Dict, List
from datetime import datetime
import random
import logging
import requests

from rasa_sdk import Action, Tracker
from rasa_sdk.executor import CollectingDispatcher
from rasa_sdk.events import SlotSet
from trello import TrelloClient


import litellm
litellm.set_verbose = True
import os
from dotenv import load_dotenv  
load_dotenv()


logger = logging.getLogger(__name__)


# Initialize TrelloClient using environment variables (assumed to be set in .env)
TRELLO_API_KEY = os.getenv("TRELLO_API_KEY")
TRELLO_API_SECRET = os.getenv("TRELLO_API_SECRET")
TRELLO_OAUTH_TOKEN = os.getenv("TRELLO_OAUTH_TOKEN")
TRELLO_OAUTH_TOKEN_SECRET = os.getenv("TRELLO_OAUTH_TOKEN_SECRET")

trello_client = TrelloClient(
    api_key=TRELLO_API_KEY,
    api_secret=TRELLO_API_SECRET,
    token=TRELLO_OAUTH_TOKEN,
    token_secret=TRELLO_OAUTH_TOKEN_SECRET
)

# Assume a board named "RASA Board" already exists with some important lists.
BOARD_NAME = "RASA Project Board"

def get_board_by_name(board_name: str):
    boards = trello_client.list_boards()
    for board in boards:
        if board.name.lower() == board_name.lower():
            return board
    return None


class ActionCreateNewList(Action):
    def name(self) -> Text:
        return "action_create_new_list"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        """
        Creates a new list on the specified board.
        The new list's name is provided in the slot 'list_name'.
        """
        list_name = tracker.get_slot("list_name")
        board = get_board_by_name(BOARD_NAME)
        if not board:
            dispatcher.utter_message(text="Board not found.")
            return []
        try:
            new_list = board.add_list(list_name)
            dispatcher.utter_message(
                text=f"List '{new_list.name}' created successfully on board '{BOARD_NAME}'."
            )
        except Exception as e:
            logger.error(f"Failed to create list: {str(e)}")
            dispatcher.utter_message(text="Failed to create the list. Please try again.")
        return [SlotSet("list_name", None)]

class ActionAddCardToList(Action):
    def name(self) -> Text:
        return "action_add_card_to_list"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        """
        Adds a new card to a specified list on the board.
        The list name is taken from slot 'list_name' and the card title from 'card_title'.
        """
        list_name = tracker.get_slot("list_name")
        card_title = tracker.get_slot("card_title")
        board = get_board_by_name(BOARD_NAME)
        if not board:
            dispatcher.utter_message(text="Board not found.")
            return []
        target_list = None
        for lst in board.list_lists():
            if lst.name.lower() == list_name.lower():
                target_list = lst
                break
        if not target_list:
            dispatcher.utter_message(
                text=f"List '{list_name}' not found on board '{BOARD_NAME}'."
            )
            return []
        try:
            card = target_list.add_card(card_title, desc="Created via BizFlow AI")
            dispatcher.utter_message(
                text=f"Card '{card.name}' added to list '{target_list.name}'."
            )
        except Exception as e:
            logger.error(f"Failed to add card: {str(e)}")
            dispatcher.utter_message(text="Failed to add the card. Please try again.")
        return [SlotSet("card_title", None), SlotSet("list_name", None)]

class ActionAddChecklistToCard(Action):
    def name(self) -> Text:
        return "action_add_checklist_to_card"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        """
        Adds a checklist to a specified card.
        The card title is taken from 'card_title' and checklist items from 'checklist_items'
        (expected as a comma-separated string).
        """
        card_title = tracker.get_slot("card_title")
        checklist_items_str = tracker.get_slot("checklist_items")
        board = get_board_by_name(BOARD_NAME)
        if not board:
            dispatcher.utter_message(text="Board not found.")
            return []
        target_card = None
        for lst in board.list_lists():
            for card in lst.list_cards():
                if card.name.lower() == card_title.lower():
                    target_card = card
                    break
            if target_card:
                break
        if not target_card:
            dispatcher.utter_message(
                text=f"Card '{card_title}' not found on board '{BOARD_NAME}'."
            )
            return []
        try:
            items = [item.strip() for item in checklist_items_str.split(",") if item.strip()]
            target_card.add_checklist("Checklist", items)
            dispatcher.utter_message(
                text=f"Checklist added to card '{target_card.name}'."
            )
        except Exception as e:
            logger.error(f"Failed to add checklist: {str(e)}")
            dispatcher.utter_message(text="Failed to add the checklist. Please try again.")
        return [SlotSet("checklist_items", None), SlotSet("card_title", None)]


class ActionCreateITTicket(Action):
    def name(self) -> Text:
        return "action_create_it_ticket"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        """
        Creates an IT support ticket using the employee_id and issue provided by the user.
        Generates a unique ticket_id and sets the ticket_created slot to True.
        """
        try:
            employee_id = tracker.get_slot("employee_id")
            issue = tracker.latest_message.get("text") or tracker.get_slot("issue")
            print(f"Employee ID: {employee_id}, Issue: {issue}")
            
            # Validate employee ID and issue details.
            if not employee_id or len(employee_id.strip()) < 5:
                dispatcher.utter_message(
                    text="⚠️ Invalid Employee ID format. Please provide your full employee ID (EMP-XXXXX)."
                )
                return []
                
            if not issue or len(issue.strip()) < 5:
                dispatcher.utter_message(
                    text="❌ Issue description must be at least 5 characters. Please provide more details."
                )
                return []

            # Generate enterprise-style ticket ID.
            timestamp = datetime.now().strftime("%y%m%d")
            ticket_id = f"IT-{employee_id[-4:]}-{timestamp}-{random.randint(1000,9999)}"
            logger.info(f"Created ticket {ticket_id} for employee {employee_id}")
            
            # --- Add issue as a card to the "To Do" list on the board ---
            board = get_board_by_name(BOARD_NAME)
            if board:
                todo_list = None
                for lst in board.list_lists():
                    if lst.name.lower() == "to do":
                        todo_list = lst
                        break
                if todo_list:
                    card = todo_list.add_card(f"IT Ticket: {ticket_id}", desc=issue)
                    logger.info(f"Added IT ticket card '{card.name}' to 'To Do' list on board '{BOARD_NAME}'.")
                else:
                    logger.warning("To Do list not found on board. Skipping card creation.")
            else:
                logger.warning("Board not found. Skipping card creation.")

            # Return events to update the conversation state.
            return [
                SlotSet("ticket_id", ticket_id),
                SlotSet("ticket_created", True),
                SlotSet("issue", None)  # Clear the issue slot for future interactions.
            ]
            
        except Exception as e:
            logger.error(f"Ticket creation failed: {str(e)}")
            dispatcher.utter_message(
                text="🔧 Our ticket system is currently unavailable. Please try again later or contact IT directly."
            )
            return []
            
            

class ActionSubmitExpenseReport(Action):
    def name(self) -> Text:
        return "action_submit_expense_report"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        """
        Submits an expense report using the amount provided by the user.
        Generates a reference ID for the expense report.
        """
        try:

            amount_str = tracker.get_slot("expense_amount") or ""
            if amount_str.startswith("$"):
                amount_str = amount_str[1:]
            try:
                amount = float(amount_str)
            except ValueError:
                dispatcher.utter_message(text=f"❌ {amount_str} is an invalid amount format. Please enter numbers only (e.g., 150.50).")
                return []



            
            if amount <= 0:
                dispatcher.utter_message(
                    text="❌ Invalid amount. Expense must be greater than $0."
                )
                return []
                
            if amount > 10000:
                dispatcher.utter_message(
                    text="⚠️ Expenses over $10,000 require manager approval. Please contact finance."
                )
                return []

            timestamp = datetime.now().strftime("%Y%m%d%H%M")
            reference_id = f"EXP-{timestamp}-{random.randint(100,999)}"
            
            dispatcher.utter_message(
                text=f"✅ Expense ${amount:,.2f} submitted successfully!\n"
                     f"Reference ID: {reference_id}\n"
                     f"Allow 5-7 business days for processing."
            )
            return [SlotSet("expense_report_submitted", True)]
            
        except (ValueError, TypeError):
            dispatcher.utter_message(
                text=f"❌ {amount} is invalid amount format. Please enter numbers only (e.g., 150.50)."
            )
            return []
            
        except Exception as e:
            logger.error(f"Expense submission failed: {str(e)}")
            dispatcher.utter_message(
                text="⚠️ Expense system is currently unavailable. Please try again later."
            )
            return []


class ActionBookMeetingRoom(Action):
    VALID_TIMESLOTS = ["09:00", "10:30", "13:00", "14:30", "16:00"]

    def name(self) -> Text:
        return "action_book_meeting_room"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        """
        Books a meeting room based on the provided meeting_date and meeting_time.
        Validates that the meeting date is in the future and that the time is one of the allowed slots.
        Generates a confirmation code and resets the meeting date/time slots.
        """
        try:
            date_str = tracker.get_slot("meeting_date")
            time_str = tracker.get_slot("meeting_time")
            
            # Validate date format
            try:
                meeting_date = datetime.strptime(date_str, "%Y-%m-%d").date()
                if meeting_date < datetime.today().date():
                    dispatcher.utter_message(
                        text="❌ Cannot book meetings in the past. Please choose a future date."
                    )
                    return []
            except ValueError:
                dispatcher.utter_message(
                    text="❌ Invalid date format. Please use YYYY-MM-DD."
                )
                return []

            # Validate time slot
            if time_str not in self.VALID_TIMESLOTS:
                options = "\n".join(self.VALID_TIMESLOTS)
                dispatcher.utter_message(
                    text=f"⚠️ Available timeslots:\n{options}\nPlease choose from these 90-minute slots."
                )
                return []

            # Generate booking confirmation and confirmation code.
            confirmation_code = f"MR-{meeting_date.strftime('%y%m%d')}-{time_str.replace(':','')}"
            dispatcher.utter_message(
                text=f"🎉 Booking confirmed!\n"
                     f"Date: {meeting_date.strftime('%b %d, %Y')}\n"
                     f"Time: {time_str}\n"
                     f"Confirmation: {confirmation_code}"
            )
            return [
                SlotSet("meeting_room_booked", True),
                SlotSet("confirmation_code", confirmation_code),
                SlotSet("meeting_date", None),
                SlotSet("meeting_time", None)
            ]
        except Exception as e:
            logger.error(f"Booking error: {str(e)}")
            dispatcher.utter_message(
                text="⚠️ Room booking system is currently unavailable. Please try again later."
            )
            return []


class ActionRagSearch(Action):
    def name(self) -> Text:
        return "action_rag_search"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        """
        Calls the RAG API running on port 8000 to retrieve an answer for the user's query.
        If no relevant context is found, a predefined reply is returned.
        """
        query = tracker.latest_message.get("text")
        if not query:
            dispatcher.utter_message(text="I'm sorry, I didn't understand your question. Could you please rephrase?")
            return []

        url = "http://localhost:8000/query"
        payload = {"query": query}
        try:
            response = requests.post(url, json=payload)
            result = response.json()
            answer = result.get("answer", "I'm sorry, I couldn't find any relevant information regarding your query.")
        except Exception as e:
            logger.error(f"RAG API call failed: {str(e)}")
            answer = "I'm sorry, there was an error processing your request. Please try again later."

        dispatcher.utter_message(text=answer)
        return []


class ActionDefaultFallback(Action):
    def name(self) -> Text:
        return "action_default_fallback"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        """
        Provides a generic fallback message when the assistant is unsure how to respond.
        """
        dispatcher.utter_message(
            text="🤖 I'm still learning! Here's what I can help with:\n"
                 "• IT Support Requests\n"
                 "• HR Policy Questions\n"
                 "• Expense Report Submission\n"
                 "• Meeting Room Booking\n"
                 "• General Company Policies\n\n"
                 "How can I assist you today?"
        )
        return []


class ActionEscalateToHR(Action):
    def name(self) -> Text:
        return "action_escalate_to_hr"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        """
        Escalates a complaint to HR by generating a case ID and informing the user.
        The generated case ID is stored in the slot 'case_id'.
        """
        try:
            case_id = f"HR-{datetime.now().year}-{random.randint(1000,9999)}"
            dispatcher.utter_message(
                text=f"🚨 Case Escalated to HR\n"
                     f"Case ID: {case_id}\n"
                     f"You'll receive an update within 24 hours.\n"
                     f"Urgent? Call HR Hotline: 1-800-555-1234"
            )
            return [SlotSet("case_id", case_id)]
        except Exception as e:
            logger.error(f"HR escalation failed: {str(e)}")
            dispatcher.utter_message(
                text="⚠️ HR system is currently unavailable. Please contact hr@company.com directly."
            )
            return []
