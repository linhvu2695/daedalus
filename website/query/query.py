from flask import jsonify, Response
from sqlalchemy import text
from typing import Dict
from .. import db
from ..exception.query_exception import *

class QueryBuilder:
    class Const:
        COMMA_SEPARATOR = ","
        SPACE_SEPARATOR = " "
        AND_SEPARATOR = " AND "

        TAG_FIELDS_QUERY = "FIELDS_QUERY"
        TAG_MAIN_TABLE = "MAIN_TABLE"
        TAG_JOIN_TABLES = "JOIN_TABLES"
        TAG_WHERE_CONDITIONS = "WHERE_CONDITIONS"
        TAG_SORT_FIELDS = "SORT_FIELDS"

        SELECT_CLAUSE = "SELECT_CLAUSE"
        FROM_CLAUSE = "FROM_CLAUSE"
        WHERE_CLAUSE = "WHERE_CLAUSE"
        ORDER_BY_CLAUSE = "ORDER_BY_CLAUSE"

        DEFAULT_POSITIVE_WHERE_CONDITION = "1=1"
        DEFAULT_NEGATIVE_WHERE_CONDITION = "1=0"
        DEFAULT_SORT_COLUMN = "id"

    def __init__(self):
        self.main_table_query = ""
        self.join_tables = []
        self.fields_query = []
        self.where_conditions = []
        self.fields_sort = []

    def add_main_table(self, table_query: str):
        """
        The main table of the query. Use alias for convenient table reference.

        Example: 
            (SELECT KT.id, KT.name FROM keytype KT)
        """
        self.main_table_query = table_query

    def add_join_table(self, join_table: str):
        """
        Add tables to join with the main table. Use alias for convenient table reference.

        Example: 
            JOIN keytype KT ON KT.id = KW.keytype
        """
        self.join_tables.append(join_table)

    def add_field(self, field_query: str):
        """
        Add a field to query. Use alias for convenient table reference.

        Example:
            DO.title AS Title
        """
        self.fields_query.append(field_query)

    def add_where_condition(self, condition: str):
        """
        Add a WHERE condition for the query. Use alias for convenient table reference.
        All conditions are connected together with AND condition.

        Example:
            (DO.doctype IN ('image', 'audio') OR DO.subtype = 'folder')
        """
        self.where_conditions.append(condition)

    def add_sort_field(self, field):
        """
        Add field(s) to sort the query results.

        Example:
            DO.create_date DESC
        """
        if field not in self.fields_sort:
            self.fields_sort.append(field)

    def build_query(self) -> str:
        """
        Get the full query. If required clauses are missing, exceptions will be thrown.
        """
        # Check for missing required clauses
        if len(self.fields_query) == 0:
            raise MissingClauseException("Missing fields for SELECT.")
        
        if len(self.main_table_query) == 0:
            raise MissingClauseException("Missing main table.")
        
        # Building the full query
        full_query = "{SELECT_CLAUSE} {FROM_CLAUSE} {WHERE_CLAUSE} {ORDER_BY_CLAUSE}"
        clause_placeholders = {
            self.Const.SELECT_CLAUSE: self._get_select_clause(),
            self.Const.FROM_CLAUSE: self._get_from_clause(),
            self.Const.WHERE_CLAUSE: self._get_where_clause(),
            self.Const.ORDER_BY_CLAUSE: self._get_order_by_clause()
        }
        return full_query.format(**clause_placeholders).strip()

    def get_query_result(self) -> Dict[str, str]:
        """
        Get the query result. Only call this when all required clauses have been filled.
        """

        try:
            full_query = self.build_query()
        except MissingClauseException as ex:
            print(ex.message)
            return None
        print(f"Full query: {full_query}") 

        with db.engine.connect() as connection:
            result = connection.execute(text(full_query))
        rows = result.fetchall()
        columns = result.keys()
        response = [dict(zip(columns, row)) for row in rows]
        print(response)
        result.close()

        return response

    def _get_fields_query(self) -> str:
        return self.Const.COMMA_SEPARATOR.join(self.fields_query)
    
    def _get_join_tables_query(self) -> str:
        return self.Const.SPACE_SEPARATOR.join(self.join_tables)
    
    def _get_where_conditions(self) -> str:
        return self.Const.AND_SEPARATOR.join(self.where_conditions)
    
    def _get_sort_fields(self) -> str:
        return self.Const.COMMA_SEPARATOR.join(self.fields_sort)
        
    def _get_select_clause(self) -> str:
        select_clause = "SELECT {FIELDS_QUERY}"
        return select_clause.format(**{self.Const.TAG_FIELDS_QUERY: self._get_fields_query()}).strip()

    def _get_from_clause(self) -> str:
        from_clause = "FROM {MAIN_TABLE} {JOIN_TABLES}"
        return  from_clause.format(**{
            self.Const.TAG_MAIN_TABLE: self.main_table_query,
            self.Const.TAG_JOIN_TABLES: self._get_join_tables_query()
            }).strip()

    def _get_where_clause(self) -> str:
        if len(self.where_conditions) == 0:
            return ""
        
        where_clause = "WHERE {WHERE_CONDITIONS}"
        return where_clause.format(**{self.Const.TAG_WHERE_CONDITIONS: self._get_where_conditions()}).strip()
    
    def _get_order_by_clause(self) -> str:
        if len(self.fields_sort) == 0:
            return ""
        
        order_by_clause = "ORDER BY {SORT_FIELDS}"
        return order_by_clause.format(**{self.Const.TAG_SORT_FIELDS: self._get_sort_fields()}).strip()