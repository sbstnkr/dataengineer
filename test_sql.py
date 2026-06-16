"""
Tests for test.sql

Validates the SQL DDL statement in test.sql, focusing on the
CREATE OR REPLACE TABLE syntax and structure introduced/modified by the PR.
"""

import os
import re
import pytest

SQL_FILE = os.path.join(os.path.dirname(__file__), "test.sql")


@pytest.fixture(scope="module")
def sql_content():
    with open(SQL_FILE, "r") as f:
        return f.read()


@pytest.fixture(scope="module")
def sql_statement(sql_content):
    """Return the first non-empty SQL statement (stripped)."""
    return sql_content.strip()


class TestCreateOrReplaceTableSyntax:
    """Tests for the CREATE OR REPLACE TABLE statement in test.sql."""

    def test_file_exists(self):
        assert os.path.isfile(SQL_FILE), f"SQL file not found: {SQL_FILE}"

    def test_file_is_not_empty(self, sql_content):
        assert sql_content.strip(), "SQL file must not be empty"

    def test_contains_create_keyword(self, sql_statement):
        assert re.search(r"\bCREATE\b", sql_statement, re.IGNORECASE), (
            "Statement must contain the CREATE keyword"
        )

    def test_contains_or_keyword(self, sql_statement):
        assert re.search(r"\bOR\b", sql_statement, re.IGNORECASE), (
            "Statement must contain the OR keyword"
        )

    def test_contains_full_replace_keyword(self, sql_statement):
        """REPLACE must be spelled in full — not truncated to REPLAC or similar."""
        assert re.search(r"\bREPLACE\b", sql_statement, re.IGNORECASE), (
            "Statement must contain the correctly-spelled keyword REPLACE, "
            f"got: {sql_statement!r}"
        )

    def test_no_truncated_replace_keyword(self, sql_statement):
        """Regression: the keyword must not appear as the truncated form 'REPLAC'."""
        # Match REPLAC that is NOT followed by 'E' (i.e. not REPLACE)
        assert not re.search(r"\bREPLAC\b(?!E)", sql_statement, re.IGNORECASE), (
            "Statement contains truncated keyword 'REPLAC' instead of 'REPLACE': "
            f"{sql_statement!r}"
        )

    def test_contains_table_keyword(self, sql_statement):
        assert re.search(r"\bTABLE\b", sql_statement, re.IGNORECASE), (
            "Statement must contain the TABLE keyword"
        )

    def test_create_or_replace_table_phrase(self, sql_statement):
        """Full phrase 'CREATE OR REPLACE TABLE' must appear together."""
        assert re.search(
            r"\bCREATE\s+OR\s+REPLACE\s+TABLE\b", sql_statement, re.IGNORECASE
        ), (
            "Statement must contain the complete phrase 'CREATE OR REPLACE TABLE', "
            f"got: {sql_statement!r}"
        )

    def test_table_name_present(self, sql_statement):
        """The target table STAGING.SCHEMA.TBL must be referenced."""
        assert re.search(
            r"\bSTAGING\.SCHEMA\.TBL\b", sql_statement, re.IGNORECASE
        ), (
            "Statement must reference table STAGING.SCHEMA.TBL, "
            f"got: {sql_statement!r}"
        )

    def test_statement_ends_with_semicolon(self, sql_statement):
        assert sql_statement.endswith(";"), (
            f"SQL statement must end with a semicolon, got: {sql_statement!r}"
        )

    def test_full_statement_structure(self, sql_statement):
        """End-to-end check: the statement matches the expected canonical form."""
        pattern = r"^\s*CREATE\s+OR\s+REPLACE\s+TABLE\s+STAGING\.SCHEMA\.TBL\s*;\s*$"
        assert re.match(pattern, sql_statement, re.IGNORECASE), (
            "Statement does not match expected structure "
            "'CREATE OR REPLACE TABLE STAGING.SCHEMA.TBL;', "
            f"got: {sql_statement!r}"
        )

    def test_no_extra_statements(self, sql_content):
        """The file should contain exactly one SQL statement."""
        statements = [s.strip() for s in sql_content.split(";") if s.strip()]
        assert len(statements) == 1, (
            f"Expected exactly 1 SQL statement, found {len(statements)}: {statements}"
        )

    def test_three_part_table_name_format(self, sql_statement):
        """Table name must follow the three-part format: database.schema.table."""
        match = re.search(
            r"\bCREATE\s+OR\s+REPLACE\s+TABLE\s+(\S+)", sql_statement, re.IGNORECASE
        )
        assert match, "Could not extract table name from statement"
        table_name = match.group(1).rstrip(";")
        parts = table_name.split(".")
        assert len(parts) == 3, (
            f"Table name must have 3 parts (database.schema.table), "
            f"got {len(parts)} part(s): {table_name!r}"
        )
