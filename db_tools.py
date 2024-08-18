"""
This module provides a collection of database tools
for working with database for telegram bot with predictions.
"""


import sqlite3
from sqlite3 import Connection, Cursor
from typing import List, Tuple, Union
from enum import Enum
import logging
from contextlib import closing

import constants
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
    """
    DBTools class is a utility class for interacting with a SQLite
    database. It provides methods for creating tables,
    executing queries, fetching data, and modifying data.

    Attributes:
        USERS_TABLE_NAME (str): The name of the users table.
        CREATE_USERS_TABLE_QUERY (str): The query for creating
            the users table.
        PREDICTIONS_TABLE_NAME (str): The name of the predictions table.
        CREATE_PREDICTIONS_TABLE_QUERY (str): The query for creating
            the predictions table.
        GET_APPROVED_PREDICTION_QUERY (str): The query for getting
            a random approved prediction.
        GET_PREDICTION_BY_ID_QUERY (str): The query for getting
            a prediction by ID.
        UPDATE_PREDICTION_STATUS_QUERY (str): The query for updating
            the status of a prediction.
        GET_USER_PREDICTIONS_QUERY (str): The query for getting
            all predictions of a user.
        GET_USER_STATISTIC_QUERY (str): The query for getting
            the statistic of a user.
        CHECK_IF_TABLE_EXISTS_QUERY (str): The query for checking
            if a table exists in the database.

    Methods:
        __init__(
                self, db_name: str = constants.DB_NAME,
                logging_level: int = logging.INFO):
            Initializes an instance of the DBTools class.

            Args:
                db_name (str): The name of the database.
                logging_level (int): The logging level.

        initialize_tables(self) -> None:
            Creates the users and predictions tables
            and initializes them with default data.

        check_if_table_exists(self, table_name: str) -> bool:
            Checks if a table exists in the database.

            Args:
                table_name (str): The name of the table.

            Returns:
                bool: True if the table exists, False otherwise.

        execute_query(
                self, query: str, parameters: Tuple = ()) -> Cursor:
            Executes a query on the database and returns the cursor.

            Args:
                query (str): The query to execute.
                parameters (Tuple): The parameters to pass to the query
                    (optional).

            Returns:
                Cursor: The cursor object.

        fetch_one(
                self, query: str,
                parameters: Tuple = ()) -> Union[Tuple, None]:
            Executes a query on the database and fetches the first row.

            Args:
                query (str): The query to execute.
                parameters (Tuple): The parameters to pass to the query
                    (optional).

            Returns:
                Union[Tuple, None]: The fetched row, or None
                    if no rows were returned.

        fetch_all(
                self, query: str,
                parameters: Tuple = ()) -> List[Tuple]:
            Executes a query on the database and fetches all rows.

            Args:
                query (str): The query to execute.
                parameters (Tuple): The parameters to pass to the query
                    (optional).

            Returns:
                List[Tuple]: The fetched rows.

        get_random_approved_prediction(self) -> Union[str, None]:
            Gets a random approved prediction.

            Returns:
                Union[str, None]: The prediction text, or None
                if no approved prediction is found.

        get_prediction_by_id(
                self, prediction_id: int) -> Union[Tuple, None]:
            Gets a prediction by ID.

            Args:
                prediction_id (int): The ID of the prediction.

            Returns:
                Union[Tuple, None]: The prediction data, or None
                    if no prediction is found.

        update_prediction_status(
                self, prediction_id: int, new_status: str) -> None:
            Updates the status of a prediction.

            Args:
                prediction_id (int): The ID of the prediction.
                new_status (str): The new status of the prediction.

        get_user_predictions(self, user_id: int) -> List[Tuple]:
            Gets all predictions of a user.

            Args:
                user_id (int): The ID of the user.

            Returns:
                List[Tuple]: The predictions of the user.

        get_user_statistic(self, user_id: int) -> List[Tuple]:
            Gets the statistic of a user.

            Args:
                user_id (int): The ID of the user.

            Returns:
                List[Tuple]: The statistic of the user.
    """

    USERS_TABLE_NAME = 'users'
    CREATE_USERS_TABLE_QUERY: str = f'''
        CREATE TABLE IF NOT EXISTS {USERS_TABLE_NAME} (
            user_id INTEGER NOT NULL PRIMARY KEY,
            user_name TEXT NOT NULL,
            state TEXT NOT NULL DEFAULT {UserStates.ACTIVE.value}
        )
    '''
    PREDICTIONS_TABLE_NAME = 'predictions'
    CREATE_PREDICTIONS_TABLE_QUERY: str = f'''
        CREATE TABLE IF NOT EXISTS {PREDICTIONS_TABLE_NAME} (
            prediction_id INTEGER PRIMARY KEY AUTOINCREMENT,
            prediction_text TEXT,
            approval_state TEXT NOT NULL DEFAULT '{ApprovalStates.NOT_APPROVED.value}',
            user_id INTEGER,
            FOREIGN KEY(user_id) REFERENCES USERS_TABLE_NAME(user_id)
        )
    '''
    GET_APPROVED_PREDICTION_QUERY: str = (
        f'SELECT * FROM {PREDICTIONS_TABLE_NAME} '
        'WHERE approval_state = ? '
        'ORDER BY random() '
        'LIMIT 1'
    )
    GET_PREDICTION_BY_ID_QUERY: str = (
        f'SELECT * FROM {PREDICTIONS_TABLE_NAME} WHERE prediction_id = ?'
    )
    UPDATE_PREDICTION_STATUS_QUERY: str = (
        f'UPDATE {PREDICTIONS_TABLE_NAME} SET approval_state = ? WHERE prediction_id = ?'
    )
    GET_USER_PREDICTIONS_QUERY: str = (
        f'SELECT * FROM {PREDICTIONS_TABLE_NAME} WHERE user_id = ?'
    )
    GET_USER_STATISTIC_QUERY: str = (
        f'SELECT approval_state, COUNT(*) FROM {PREDICTIONS_TABLE_NAME} '
        'WHERE user_id = ? GROUP BY approval_state'
    )
    CHECK_IF_TABLE_EXISTS_QUERY = (
        "SELECT name FROM sqlite_master "
        "WHERE type='table' AND name= ?"
    )
    ADD_PREDICTION_QUERY = (
        f"INSERT INTO {PREDICTIONS_TABLE_NAME} "
        "(prediction_text, user_id) "
        "VALUES (?, ?)"
    )
    GET_UNAPPROVED_PREDICTIONS_QUERY = (
        f"SELECT prediction_id, prediction_text "
        f"FROM {PREDICTIONS_TABLE_NAME} "
        f"WHERE approval_state = '{ApprovalStates.NOT_APPROVED.value}'"
    )

    def __init__(
        self, db_name: str = constants.DB_NAME,
        logging_level: int = logging.INFO
    ):
        self.logging_level = logging_level
        setup_logger(__name__, level=logging_level)
        self.db_name: str = db_name
        self._connection: Connection = sqlite3.connect(db_name)
        if (
            not self.check_if_table_exists(self.USERS_TABLE_NAME)
            and not self.check_if_table_exists(self.PREDICTIONS_TABLE_NAME)
        ):
            self.initialize_tables()

    @property
    def conn(self) -> Connection:
        """
        Returns the connection to the SQLite database.

        :return: The connection to the SQLite database.
        """
        if self._connection is None:
            self._connection = sqlite3.connect(self.db_name)
        return self._connection

    @conn.setter
    def conn(self, value):
        self._connection = value

    # def close_connection(self) -> None:
    #     if self._connection is not None:
    #         self._connection.close()
    #         self._connection = None

    def initialize_tables(self) -> None:
        """
        Method to initialize tables by executing SQL queries.

        :return: None
        """
        with closing(self.conn.cursor()) as cursor:
            cursor.execute(self.CREATE_USERS_TABLE_QUERY)
            cursor.execute(self.CREATE_PREDICTIONS_TABLE_QUERY)
            with open('default_predictions.sql', 'r', encoding='utf8') as predictions_file:
                cursor.executescript(predictions_file.read())

    def check_if_table_exists(self, table_name: str) -> bool:
        """
        Check if a table exists in the database.

        :param table_name: The name of the table to check.
        :type table_name: str
        :return: True if the table exists, False otherwise.
        :rtype: bool
        """
        with closing(self.conn.cursor()) as cursor:
            cursor.execute(self.CHECK_IF_TABLE_EXISTS_QUERY, (table_name,))
            data = cursor.fetchall()
        return len(data) > 0

    def execute_query(self, query: str, parameters: Tuple = ()) -> Cursor:
        """
        Execute a database query with optional parameters.

        :param query: The SQL query to be executed.
        :type query: str
        :param parameters: The parameters to be substituted in the query.
            Default is an empty tuple.
        :type parameters: Tuple
        :return: The result cursor after executing the query.
        :rtype: Cursor
        """
        cursor: Cursor = self.conn.cursor()
        cursor.execute(query, parameters)

        return cursor

    def fetch_one(
        self, query: str, parameters: Tuple = ()
    ) -> Union[Tuple, None]:
        """
        Fetch a single row from the database based on the given query
        and parameters.

        :param query: The SQL query to be executed.
        :param parameters: The parameters to be used in the query
            (default empty tuple).
        :return: A tuple representing the fetched row,
            or None if no row was found.
        """
        result_cursor = self.execute_query(query, parameters)
        result = result_cursor.fetchone()
        result_cursor.close()

        return result

    def fetch_all(self, query: str, parameters: Tuple = ()) -> List[Tuple]:
        """
        Fetches all the rows returned by the given SQL query
        with optional parameters.

        :param query: The SQL query to execute.
        :param parameters: The parameters to be passed with the query
            (default is an empty tuple).
        :return: A list of tuples containing the fetched rows.
        """
        result_cursor = self.execute_query(query, parameters)
        result = result_cursor.fetchall()
        result_cursor.close()

        return result

    def get_random_approved_prediction(self) -> Union[str, None]:
        """
        Returns a random approved prediction.

        :return: A randomly selected approved prediction as a string,
            or None if there are no approved predictions.
        """
        return self.fetch_one(
            self.GET_APPROVED_PREDICTION_QUERY,
            (ApprovalStates.APPROVED.value, ))[1]

    def get_prediction_by_id(
        self, prediction_id: int
    ) -> Union[Tuple, None]:
        """
        :param prediction_id: The ID of the prediction to retrieve.
        :return: A tuple representing the prediction with the given ID,
            or None if no prediction is found with the provided ID.
        """
        return self.fetch_one(
            self.GET_PREDICTION_BY_ID_QUERY, (prediction_id, ))

    def update_prediction_status(
        self, prediction_id: int, new_status: str
    ) -> None:
        """
        Updates the status of a prediction with the given prediction ID.

        :param prediction_id: The ID of the prediction to update.
        :param new_status: The new status to set for the prediction.
        :return: None
        """
        cursor = self.execute_query(
            self.UPDATE_PREDICTION_STATUS_QUERY,
            (new_status, prediction_id)
        )
        self.conn.commit()
        cursor.close()

    def get_user_predictions(self, user_id: int) -> List[Tuple]:
        """
        Retrieve all predictions for a given user.

        :param user_id: The ID of the user for whom to retrieve
            the predictions.
        :return: A list of tuples representing the predictions.
        """
        return self.fetch_all(
            self.GET_USER_PREDICTIONS_QUERY, (user_id, ))

    def get_user_statistic(self, user_id: int) -> List[Tuple]:
        """
        Retrieve user statistics for a given user.

        :param user_id: The ID of the user for which to retrieve statistics.
        :return: A list of tuples containing the user statistics.
        """
        return self.fetch_all(
            self.GET_USER_STATISTIC_QUERY, (user_id, ))

    def user_exists(self, user_id: int) -> bool:
        """
        Checks if a user with the given ID exists in the database.

        Args:
            user_id (int): The ID of the user.

        Returns:
            bool: True if the user exists, False otherwise.
        """
        CHECK_USER_EXISTS_QUERY: str = (
            f"SELECT user_id FROM {self.USERS_TABLE_NAME} WHERE  user_id = ?"
        )
        user = self.fetch_one(CHECK_USER_EXISTS_QUERY, (user_id,))

        return user is not None

    def add_user(self, user_id: int, user_name: str) -> None:
        """
        Adds a user to the users table.

        Args:
            user_id (int): The ID of the user.
            user_name (str): Telegram username of the user.
        """
        ADD_USER_QUERY = f"""
            INSERT INTO {self.USERS_TABLE_NAME}
            (user_id, user_name, state)
            VALUES (?, ?, "{UserStates.ACTIVE.value}")
        """
        cursor = self.execute_query(
            ADD_USER_QUERY, (user_id, user_name)
        )
        self.conn.commit()
        cursor.close()

    def add_prediction(self, prediction_text: str, user_id: int) -> None:
        """
        Adds a prediction to the database.

        :param prediction_text: Prediction text to add to the database.
        :type prediction_text: str
        :param user_id: The ID of the user who owns the prediction.
        :type user_id: int
        :return: None
        """

        cursor = self.execute_query(
            self.ADD_PREDICTION_QUERY, (prediction_text, user_id)
        )
        self.conn.commit()
        cursor.close()

    def get_unapproved_predictions(self) -> List[Tuple]:
        """
        Returns all unapproved predictions.

        :return: A list of tuples containing the unapproved predictions.
        """
        return self.fetch_all(self.GET_UNAPPROVED_PREDICTIONS_QUERY)


if __name__ == '__main__':
    db_tools = DBTools(constants.DB_NAME)

    print(db_tools.get_random_approved_prediction())
    unapproved_predictions = db_tools.get_unapproved_predictions()

    for prediction in unapproved_predictions:
        print(prediction)
