"""Tests for TokenCounter class."""

import sys
from pathlib import Path
from unittest.mock import Mock, patch

import pytest

# Add validation/scripts to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from token_measurement import TokenCounter

try:
    import anthropic
    HAS_ANTHROPIC = True
except ImportError:
    HAS_ANTHROPIC = False

try:
    import tiktoken
    HAS_TIKTOKEN = True
except ImportError:
    HAS_TIKTOKEN = False


class TestTokenCounter:
    """Tests for the TokenCounter class."""

    def test_counter_initializes(self):
        """TokenCounter should initialize without errors."""
        counter = TokenCounter()
        assert counter is not None
        assert isinstance(counter.counters, dict)
        assert isinstance(counter.is_approximate, dict)

    def test_counter_has_at_least_one_model(self):
        """TokenCounter should support at least one model."""
        counter = TokenCounter()
        assert len(counter.counters) > 0, "At least one model should be available"

    @pytest.mark.skipif(not HAS_TIKTOKEN, reason="tiktoken not installed")
    def test_gpt4_counter_available(self):
        """GPT-4 counter should be available when tiktoken is installed."""
        counter = TokenCounter()
        assert "gpt4" in counter.counters

    @pytest.mark.skipif(not HAS_TIKTOKEN, reason="tiktoken not installed")
    def test_gpt4_counts_tokens(self):
        """GPT-4 counter should count tokens for sample text."""
        counter = TokenCounter()
        text = "Hello, world!"
        token_count = counter.count(text, "gpt4")
        assert token_count > 0
        assert isinstance(token_count, int)

    def test_gpt4_approx_counts_tokens(self):
        """GPT-4 approximation should count tokens without tiktoken."""
        counter = TokenCounter()
        text = "Hello, world!"
        token_count = counter._count_gpt4_approx(text)
        assert token_count > 0
        assert isinstance(token_count, int)

    def test_gpt4_approx_empty_string(self):
        """GPT-4 approximation should handle empty strings."""
        counter = TokenCounter()
        assert counter._count_gpt4_approx("") == 0

    def test_gpt4_approx_single_char(self):
        """GPT-4 approximation should return at least 1 for non-empty strings."""
        counter = TokenCounter()
        assert counter._count_gpt4_approx("a") >= 1

    @pytest.mark.skipif(not HAS_ANTHROPIC, reason="anthropic not installed")
    def test_claude_counter_available(self):
        """Claude counter should be available when anthropic is installed."""
        counter = TokenCounter()
        assert "claude" in counter.counters

    @pytest.mark.skipif(not HAS_ANTHROPIC, reason="anthropic not installed")
    def test_claude_does_not_use_old_api(self):
        """Claude counter should not call client.count_tokens (old API)."""
        counter = TokenCounter()
        
        # Mock the anthropic client to ensure we don't call the old API
        with patch("token_measurement.anthropic.Anthropic") as mock_anthropic_class:
            mock_client = Mock()
            mock_anthropic_class.return_value = mock_client
            
            # Set up the new API
            mock_response = Mock()
            mock_response.input_tokens = 10
            mock_client.messages.count_tokens.return_value = mock_response
            
            # Ensure the old API doesn't exist
            delattr(mock_client, "count_tokens")
            
            # This should not raise AttributeError
            text = "Hello, world!"
            try:
                result = counter._count_claude(text)
                # If we got here, either the new API worked or we fell back to approx
                assert result > 0
            except AttributeError as e:
                if "count_tokens" in str(e):
                    pytest.fail(f"Claude counter tried to use old client.count_tokens API: {e}")
                raise

    @pytest.mark.skipif(not HAS_ANTHROPIC, reason="anthropic not installed")
    def test_claude_uses_new_api(self):
        """Claude counter should use client.messages.count_tokens (new API)."""
        counter = TokenCounter()
        
        with patch("token_measurement.anthropic.Anthropic") as mock_anthropic_class:
            mock_client = Mock()
            mock_anthropic_class.return_value = mock_client
            
            # Set up the new API
            mock_response = Mock()
            mock_response.input_tokens = 42
            mock_client.messages.count_tokens.return_value = mock_response
            
            text = "Hello, world!"
            result = counter._count_claude(text)
            
            # Should have called the new API
            mock_client.messages.count_tokens.assert_called_once()
            call_kwargs = mock_client.messages.count_tokens.call_args[1]
            assert "model" in call_kwargs
            assert "messages" in call_kwargs
            assert call_kwargs["messages"] == [{"role": "user", "content": text}]
            assert result == 42

    @pytest.mark.skipif(not HAS_ANTHROPIC, reason="anthropic not installed")
    def test_claude_falls_back_to_approx_on_error(self):
        """Claude counter should fall back to approximation if API fails."""
        counter = TokenCounter()
        
        with patch("token_measurement.anthropic.Anthropic") as mock_anthropic_class:
            mock_client = Mock()
            mock_anthropic_class.return_value = mock_client
            
            # Make the API call fail (e.g., no API key)
            mock_client.messages.count_tokens.side_effect = Exception("API key not found")
            
            text = "Hello, world!"
            result = counter._count_claude(text)
            
            # Should have fallen back to approximation
            assert result > 0
            assert isinstance(result, int)

    def test_claude_approx_counts_tokens(self):
        """Claude approximation should count tokens without API."""
        counter = TokenCounter()
        text = "Hello, world!"
        token_count = counter._count_claude_approx(text)
        assert token_count > 0
        assert isinstance(token_count, int)

    def test_claude_approx_empty_string(self):
        """Claude approximation should handle empty strings."""
        counter = TokenCounter()
        assert counter._count_claude_approx("") == 0

    def test_claude_approx_single_char(self):
        """Claude approximation should return at least 1 for non-empty strings."""
        counter = TokenCounter()
        assert counter._count_claude_approx("a") >= 1

    def test_count_raises_on_unknown_model(self):
        """count() should raise ValueError for unknown models."""
        counter = TokenCounter()
        with pytest.raises(ValueError, match="not available"):
            counter.count("test", "nonexistent_model")

    def test_approximate_flag_set_correctly(self):
        """is_approximate dict should track which models use approximation."""
        counter = TokenCounter()
        for model, is_approx in counter.is_approximate.items():
            assert isinstance(is_approx, bool)
            assert model in counter.counters
