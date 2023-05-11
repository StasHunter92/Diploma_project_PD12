from dataclasses import dataclass, field
from typing import List, Optional

import marshmallow_dataclass
from marshmallow import EXCLUDE


# ----------------------------------------------------------------------------------------------------------------------
# Create dataclasses
@dataclass
class Chat:
    """
    Represents a Telegram chat object with an ID
    and optional first name, last name, and username
    """
    id: int
    first_name: Optional[str]
    last_name: Optional[str]
    username: Optional[str]

    class Meta:
        unknown = EXCLUDE


@dataclass
class User:
    """
    Represents a Telegram user object with an ID,
    first name, optional last name, and optional username
    """
    id: int
    first_name: str
    last_name: Optional[str]
    username: Optional[str]

    class Meta:
        unknown = EXCLUDE


@dataclass
class Message:
    """
    Represents a Telegram message object with a message ID,
    sender User object, Chat object, date, and optional text
    """
    message_id: int
    from_: User = field(metadata={'data_key': 'from'})
    chat: Chat
    date: int
    text: Optional[str]

    class Meta:
        unknown = EXCLUDE


@dataclass
class Update:
    """
    Represents a Telegram update object with an update ID
    and optional Message object
    """
    update_id: int
    message: Optional[Message]

    class Meta:
        unknown = EXCLUDE


@dataclass
class GetUpdatesResponse:
    """
    Represents the response from the Telegram Bot API's getUpdates method
    with a boolean indicating success and an optional list of Update objects
    """
    ok: bool
    result: Optional[List[Update]]  # todo

    class Meta:
        unknown = EXCLUDE


@dataclass
class SendMessageResponse:
    """
    Represents the response from the Telegram Bot API's sendMessage method
    with a boolean indicating success and a Message object
    """
    ok: bool
    result: Message  # todo

    class Meta:
        unknown = EXCLUDE


# ----------------------------------------------------------------------------------------------------------------------
# Create schemas
GetUpdatesResponseSchema = marshmallow_dataclass.class_schema(GetUpdatesResponse)
SendMessageResponseSchema = marshmallow_dataclass.class_schema(SendMessageResponse)
