"""
In-memory storage, No database
"""

collections = {}
quotes = {}
transfers = {}


def reset():
    collections.clear()
    quotes.clear()
    transfers.clear()
