from datetime import datetime
# Email class used to fil data when we get the mails


class Email:

    id_mails_already_processed = []
    # This is used for checking time and deciding when to clear the array of "already processed emails"
    dateReference = datetime.now()

    def __init__(self, from_message, message_data, msg_id_data):
        self.msg_id_data = msg_id_data
        self.from_message = from_message
        self.message_data = message_data
