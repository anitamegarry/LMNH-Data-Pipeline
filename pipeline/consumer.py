"""
Consumer for LMNH data
"""

from pipeline import get_connection, get_cursor
from confluent_kafka import Consumer
from os import environ, getenv
import json
from dotenv import load_dotenv
from datetime import datetime
import argparse


def is_iso_format(date_str) -> bool:
    """Checks if string is of isoformat"""
    try:
        datetime.fromisoformat(date_str)
        return True
    except ValueError:
        return False


def convert_data_types(data_dict: dict) -> dict:
    data_dict["at"] = datetime.fromisoformat(data_dict["at"])
    data_dict["site"] = int(data_dict["site"])
    data_dict["val"] = int(data_dict["val"])
    if "type" in data_dict:
        data_dict["type"] = float(data_dict["type"])
    return data_dict


def upload_data_to_database(data: dict) -> None:
    """Uploads data from consumer to database"""
    conn = get_connection()
    cursor = get_cursor(conn)

    if data['val'] == int(getenv("request")):
        if data['type'] == float(getenv("assistance")):
            cursor.execute("""INSERT INTO request_interaction
(exhibition_id, request_id, event_at) VALUES (%s, %s, %s)""", (data['site'], 1, data['at'],))
        elif data['type'] == float(getenv("emergency")):
            cursor.execute("""INSERT INTO request_interaction
(exhibition_id, request_id, event_at) VALUES (%s, %s, %s)""", (data['site'], 2, data['at'],))
    else:
        cursor.execute("""
            INSERT INTO rating_interaction (exhibition_id, rating_id, event_at)
            SELECT %s, rating_id, %s
            FROM rating
            WHERE rating_value = %s
        """, (data['site'], data['at'], data['val']))
    conn.commit()


def check_msg_dict_contains_key_values(msg, log_enabled=False) -> bool:
    """Checks if lmnh message is valid"""
    msg_value = msg.value().decode('utf-8')
    msg_dict = json.loads(msg_value)
    if msg_dict.get("at") is None:
        log_invalid_message(msg_value, "Missing at key",
                            msg.offset(), log_enabled)
        return False
    if msg_dict.get("site") is None:
        log_invalid_message(msg_value, "Missing site key",
                            msg.offset(), log_enabled)
        return False
    if msg_dict.get("val") is None:
        log_invalid_message(msg_value, "Missing val key",
                            msg.offset(), log_enabled)
        return False
    return True


def check_value_type(msg, log_enabled=False) -> bool:
    """Checks if value types message are valid"""
    msg_value = msg.value().decode('utf-8')
    msg_dict = json.loads(msg_value)
    sites = environ["sites"].split(',')
    val_review = environ["val_review"].split(',')
    val_request = environ["val_request"]
    type_request = environ["type_request"].split(',')
    if not is_iso_format(str(msg_dict.get("at"))):
        log_invalid_message(msg_value, "Invalid at value",
                            msg.offset(), log_enabled)
        return False
    if str(msg_dict.get("site")) not in sites:
        log_invalid_message(msg_value, "Invalid site value",
                            msg.offset(), log_enabled)
        return False
    if str(msg_dict.get("val")) == val_request:
        if str(msg_dict.get("type")) not in type_request:
            log_invalid_message(msg_value, "Invalid type value",
                                msg.offset(), log_enabled)
            return False
        return True
    if str(msg_dict.get("val")) not in val_review:
        log_invalid_message(msg_value, "Invalid val value",
                            msg.offset(), log_enabled)
        return False
    return True


def consume_messages(cons: Consumer, log_enabled=False) -> None:
    """Processes Kafka messages."""
    while True:
        msg = cons.poll(1)
        if msg is None:
            print("No message")
            continue
        elif msg.error():
            log_invalid_message(msg.value(), "Consumer Error",
                                msg.offset(), log_enabled)
        else:
            msg_value = msg.value().decode('utf-8')
            msg_dict = json.loads(msg_value)
            check1 = check_msg_dict_contains_key_values(msg, log_enabled)
            check2 = check_value_type(msg, log_enabled)
            if check1 and check2:
                print(f"Received message: {msg_value}, Offset: {msg.offset()}")
                msg_dict = convert_data_types(msg_dict)
                upload_data_to_database(msg_dict)


def parse_arguments():
    """Parses arguments to the command line"""
    parser = argparse.ArgumentParser()
    parser.add_argument("--log", action="store_true",
                        help="Enable logging of invalid messages to a .txt file")
    return parser.parse_args()


def log_invalid_message(msg_value, reason, offset, log_enabled=False) -> None:
    """Logs invalid message and reason to file if logging is enabled"""
    if log_enabled:
        with open(environ["log_file"], "a", encoding='utf-8') as f:
            f.write(
                f"""Invalid: {msg_value}, Reason: {reason}, Offset: {offset}\n""")


if __name__ == "__main__":
    load_dotenv()
    args = parse_arguments()
    kafka_config = {
        'bootstrap.servers': environ['BOOTSTRAP_SERVERS'],
        'security.protocol': 'SASL_SSL',
        'sasl.mechanisms': 'PLAIN',
        'sasl.username': environ['USERNAME'],
        'sasl.password': environ['PASSWORD'],
        'group.id': '7',
        'auto.offset.reset': 'earliest'
    }
    consumer = Consumer(kafka_config)
    consumer.subscribe(['lmnh'])
    try:
        consume_messages(consumer, args.log)

    except KeyboardInterrupt:
        print("Consumer interrupted. Closing...")

    except Exception as e:
        print(f"An error occurred: {e}")

    finally:
        consumer.close()
        print("Consumer has closed and left the group.")
