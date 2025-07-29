"""Basic tests for AioMost library"""

import pytest
from aiomost import __version__, MattermostBot


def test_version():
    """Test that version is properly set"""
    assert __version__ == "0.1.0"


def test_imports():
    """Test that main classes can be imported"""
    from aiomost import (
        MattermostDispatcher,
        Router,
        MessageFilter,
        StateManager,
        InlineKeyboard,
    )
    
    # Test that MattermostBot is an alias for MattermostDispatcher
    assert MattermostBot is MattermostDispatcher


@pytest.mark.asyncio
async def test_basic_functionality():
    """Test basic bot instantiation"""
    # This is a placeholder test - you'll need to implement actual tests
    # based on your MattermostBot implementation
    pass
