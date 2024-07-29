# TODO: add docstrings

import sqlite3
from sqlite3 import Connection, Cursor
from typing import List, Tuple, Union
from enum import Enum
import logging

from utils import setup_logger


class ApprovalStates(Enum):
    APPROVED = 'approved'
    NOT_APPROVED = 'not approved'
    REJECTED = 'rejected'
    INAPPROPRIATE = 'inappropriate'


class UserStates(Enum):
    ACTIVE = 'active'
    INACTIVE = 'inactive'


class DBTools:
    CREATE_USERS_TABLE_QUERY: str = f'''
        CREATE TABLE if NOT EXISTS users (
            user_id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_name TEXT NOT NULL,
            state TEXT NOT NULL DEFAULT {UserStates.ACTIVE.value}
        )
    '''
    CREATE_PREDICTIONS_TABLE_QUERY: str = f'''
        CREATE TABLE if NOT EXISTS predictions (
            prediction_id INTEGER PRIMARY KEY AUTOINCREMENT,
            prediction_text TEXT,
            approval_state TEXT NOT NULL DEFAULT '{ApprovalStates.NOT_APPROVED.value}',
            user_id INTEGER,
            FOREIGN KEY(user_id) REFERENCES users(user_id)
        )
    '''
    GET_APPROVED_PREDICTION_QUERY: str = '''
        SELECT * FROM predictions
        WHERE approval_state = ?
        ORDER BY random()
        LIMIT 1
    '''
    GET_PREDICTION_BY_ID_QUERY: str = (
        'SELECT * FROM predictions WHERE prediction_id = ?'
    )
    UPDATE_PREDICTION_STATUS_QUERY: str = (
        'UPDATE predictions SET approval_state = ? WHERE prediction_id = ?'
    )
    GET_USER_PREDICTIONS_QUERY: str = (
        'SELECT * FROM predictions WHERE user_id = ?'
    )
    GET_USER_STATISTIC_QUERY: str = (
        'SELECT approval_state, COUNT(*) FROM predictions '
        'WHERE user_id = ? GROUP BY approval_state'
    )

    def __init__(
        self, db_name: str = "kind_predictions.db",
        logging_level: int = logging.INFO
    ):
        self.logging_level = logging_level
        setup_logger(__name__, level=logging_level)
        self.db_name: str = db_name
        self._connection: Connection = sqlite3.connect(db_name)
        self.initialize_tables()

    @property
    def conn(self) -> Connection:
        if self._connection is None:
            self._connection = sqlite3.connect(self.db_name)
        return self._connection

    @conn.setter
    def conn(self, value):
        self._connection = value

    def initialize_tables(self) -> None:
        with self.conn as conn:
            with conn.cursor() as cursor:
                cursor.execute(self.CREATE_USERS_TABLE_QUERY)
                cursor.execute(self.CREATE_PREDICTIONS_TABLE_QUERY)

    def execute_query(self, query: str, parameters: Tuple = ()) -> Cursor:
        with self.conn as conn:
            cursor: Cursor = conn.cursor()
            cursor.execute(query, parameters)

            return cursor

    def fetch_one(
        self, query: str, parameters: Tuple = ()
    ) -> Union[Tuple, None]:
        result_cursor = self.execute_query(query, parameters)
        result = result_cursor.fetchone()
        result_cursor.close()

        return result

    def fetch_all(self, query: str, parameters: Tuple = ()) -> List[Tuple]:
        result_cursor = self.execute_query(query, parameters)
        result = result_cursor.fetchall()
        result_cursor.close()

        return result

    def get_random_approved_prediction(self) -> Union[Tuple, None]:
        return self.fetch_one(
            self.GET_APPROVED_PREDICTION_QUERY,
            (ApprovalStates.APPROVED.value, ))

    def get_prediction_by_id(
        self, prediction_id: int
    ) -> Union[Tuple, None]:
        return self.fetch_one(
            self.GET_PREDICTION_BY_ID_QUERY, (prediction_id, ))

    def update_prediction_status(
        self, prediction_id: int, new_status: str
    ) -> None:
        cursor = self.execute_query(
            self.UPDATE_PREDICTION_STATUS_QUERY,
            (new_status, prediction_id)
        )
        self.conn.commit()
        cursor.close()

    def get_user_predictions(self, user_id: int) -> List[Tuple]:
        return self.fetch_all(
            self.GET_USER_PREDICTIONS_QUERY, (user_id, ))

    def get_user_statistic(self, user_id: int) -> List[Tuple]:
        return self.fetch_all(
            self.GET_USER_STATISTIC_QUERY, (user_id, ))


if __name__ == '__main__':
    db_tools = DBTools("kind_predictions.db")

    # Now you can run the methods of the DBTools object as required.
    # Eg: Initializing tables
    db_tools.initialize_tables()
