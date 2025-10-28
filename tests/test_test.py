"""
Comprehensive test suite for cmdrnafold package.

This module contains unit tests, integration tests, and security tests
for the RNA folding functionality.
"""

import pytest
import asyncio
from unittest.mock import patch, MagicMock, AsyncMock
from cmdrnafold import RNA, RNArunner, SyncRNArunner, RNAFoldError, fold_compound, fold_compound_sync


class TestRNArunner:
    """Test cases for the RNArunner class."""
    
    def test_init_valid_sequence(self):
        """Test initialization with valid RNA sequence."""
        sequence = "AUGC"
        runner = RNArunner(sequence)
        assert runner.sequence == "AUGC"
        assert runner.cmd == "RNAFold --noPS"
        assert isinstance(hash(runner), int)
        
    def test_init_lowercase_sequence(self):
        """Test initialization converts lowercase to uppercase."""
        sequence = "augc"
        runner = RNArunner(sequence)
        assert runner.sequence == "AUGC"
        
    def test_init_empty_sequence(self):
        """Test initialization with empty sequence raises error."""
        with pytest.raises(RNAFoldError, match="Sequence must be a non-empty string"):
            RNArunner("")
            
    def test_init_none_sequence(self):
        """Test initialization with None sequence raises error."""
        with pytest.raises(RNAFoldError, match="Sequence must be a non-empty string"):
            RNArunner(None)
            
    def test_init_invalid_nucleotides(self):
        """Test initialization with invalid nucleotides raises error."""
        with pytest.raises(RNAFoldError, match="Invalid nucleotides in sequence"):
            RNArunner("AUGCX")
            
    def test_repr(self):
        """Test string representation."""
        runner = RNArunner("AUGC")
        assert repr(runner) == "RNArunner(sequence='AUGC')"
        
    def test_repr_long_sequence(self):
        """Test string representation with long sequence."""
        long_seq = "A" * 30
        runner = RNArunner(long_seq)
        assert "..." in repr(runner)
        assert len(repr(runner)) < len(long_seq) + 50

    @pytest.mark.asyncio
    async def test_mfe_success(self):
        """Test successful MFE computation."""
        runner = RNArunner("CGCAGGGAUACCCGCG")
        
        # Mock the subprocess
        mock_proc = AsyncMock()
        mock_proc.returncode = 0
        mock_proc.communicate.return_value = (
            b"CGCAGGGAUACCCGCG\n((((....))))\n( -4.20)\n",
            b""
        )
        
        with patch('asyncio.create_subprocess_shell', return_value=mock_proc):
            structure, mfe = await runner.mfe()
            
        assert structure == "((((....))))"
        assert mfe == -4.20
        
    @pytest.mark.asyncio
    async def test_mfe_process_error(self):
        """Test MFE computation with process error."""
        runner = RNArunner("AUGC")
        
        mock_proc = AsyncMock()
        mock_proc.returncode = 1
        mock_proc.communicate.return_value = (b"", b"Error message")
        
        with patch('asyncio.create_subprocess_shell', return_value=mock_proc):
            with pytest.raises(RNAFoldError, match="RNAFold failed with return code 1"):
                await runner.mfe()
                
    @pytest.mark.asyncio
    async def test_mfe_parse_error(self):
        """Test MFE computation with parsing error."""
        runner = RNArunner("AUGC")
        
        mock_proc = AsyncMock()
        mock_proc.returncode = 0
        mock_proc.communicate.return_value = (b"Invalid output", b"")
        
        with patch('asyncio.create_subprocess_shell', return_value=mock_proc):
            with pytest.raises(RNAFoldError, match="Unexpected RNAFold output format"):
                await runner.mfe()


class TestSyncRNArunner:
    """Test cases for the SyncRNArunner class."""
    
    def test_init(self):
        """Test initialization."""
        runner = SyncRNArunner("AUGC")
        assert isinstance(runner._runner, RNArunner)
        
    def test_mfe_sync(self):
        """Test synchronous MFE computation."""
        runner = SyncRNArunner("CGCAGGGAUACCCGCG")
        
        # Mock the async runner
        with patch.object(runner._runner, 'mfe', new_callable=AsyncMock) as mock_mfe:
            mock_mfe.return_value = ("((((....))))", -4.20)
            
            structure, mfe = runner.mfe()
            
        assert structure == "((((....))))"
        assert mfe == -4.20
        
    def test_hash(self):
        """Test hash function."""
        runner = SyncRNArunner("AUGC")
        assert isinstance(hash(runner), int)
        
    def test_repr(self):
        """Test string representation."""
        runner = SyncRNArunner("AUGC")
        assert "Sync" in repr(runner)


class TestFoldCompound:
    """Test cases for fold_compound functions."""
    
    def test_fold_compound(self):
        """Test async fold_compound function."""
        fc = fold_compound("AUGC")
        assert isinstance(fc, RNArunner)
        assert fc.sequence == "AUGC"
        
    def test_fold_compound_sync(self):
        """Test sync fold_compound function."""
        fc = fold_compound_sync("AUGC")
        assert isinstance(fc, SyncRNArunner)
        assert fc._runner.sequence == "AUGC"


class TestRNAModule:
    """Test cases for the RNA module interface."""
    
    def test_rna_fold_compound(self):
        """Test RNA.fold_compound backward compatibility."""
        fc = RNA.fold_compound("AUGC")
        assert isinstance(fc, SyncRNArunner)
        assert fc._runner.sequence == "AUGC"


class TestErrorHandling:
    """Test cases for error handling."""
    
    def test_rnafold_error_inheritance(self):
        """Test RNAFoldError is proper exception."""
        error = RNAFoldError("Test error")
        assert isinstance(error, Exception)
        assert str(error) == "Test error"


class TestIntegration:
    """Integration tests (require RNAFold to be installed)."""
    
    @pytest.mark.integration
    @pytest.mark.asyncio
    async def test_real_rnafold_async(self):
        """Test with real RNAFold command (if available)."""
        try:
            runner = RNArunner("CGCAGGGAUACCCGCG")
            structure, mfe = await runner.mfe()
            
            # Basic validation
            assert isinstance(structure, str)
            assert isinstance(mfe, float)
            assert len(structure) == len(runner.sequence)
            assert set(structure) <= set("().")
            
        except RNAFoldError as e:
            if "Failed to start RNAFold process" in str(e):
                pytest.skip("RNAFold not available in test environment")
            else:
                raise
                
    @pytest.mark.integration
    def test_real_rnafold_sync(self):
        """Test with real RNAFold command synchronously (if available)."""
        try:
            runner = SyncRNArunner("CGCAGGGAUACCCGCG")
            structure, mfe = runner.mfe()
            
            # Basic validation
            assert isinstance(structure, str)
            assert isinstance(mfe, float)
            assert len(structure) == len(runner._runner.sequence)
            assert set(structure) <= set("().")
            
        except RNAFoldError as e:
            if "Failed to start RNAFold process" in str(e):
                pytest.skip("RNAFold not available in test environment")
            else:
                raise


class TestSecurityAndValidation:
    """Security and input validation tests."""
    
    def test_sequence_injection_protection(self):
        """Test protection against command injection in sequence."""
        malicious_sequences = [
            "AUGC; rm -rf /",
            "AUGC && echo 'hacked'",
            "AUGC | cat /etc/passwd",
            "AUGC\n@\necho 'injection'",
        ]
        
        for seq in malicious_sequences:
            with pytest.raises(RNAFoldError, match="Invalid nucleotides"):
                RNArunner(seq)
                
    def test_large_sequence_handling(self):
        """Test handling of very large sequences."""
        # Test with a reasonably large sequence
        large_seq = "AUGC" * 1000  # 4000 nucleotides
        runner = RNArunner(large_seq)
        assert runner.sequence == large_seq
        
    def test_unicode_sequence_handling(self):
        """Test handling of unicode characters in sequence."""
        unicode_sequences = [
            "AUGCα",
            "AUGC\u0000",
            "AUGC\n",
            "AUGC\t",
        ]
        
        for seq in unicode_sequences:
            with pytest.raises(RNAFoldError, match="Invalid nucleotides"):
                RNArunner(seq)


# Fixtures for test data
@pytest.fixture
def valid_rna_sequences():
    """Provide valid RNA sequences for testing."""
    return [
        "AUGC",
        "CGCAGGGAUACCCGCG",
        "AAAUUUGGGCCC",
        "UUUUUUUUUUUU",
        "GGGGGGGGGGGG",
    ]


@pytest.fixture
def invalid_rna_sequences():
    """Provide invalid RNA sequences for testing."""
    return [
        "",
        "AUGCX",
        "123456",
        "AUGC-AUGC",
        "AUGC AUGC",
    ]


class TestParameterizedSequences:
    """Parameterized tests with various sequences."""
    
    @pytest.mark.parametrize("sequence", [
        "AUGC",
        "CGCAGGGAUACCCGCG", 
        "AAAUUUGGGCCC",
        "augc",  # lowercase
        "AuGc",  # mixed case
    ])
    def test_valid_sequences(self, sequence):
        """Test various valid sequences."""
        runner = RNArunner(sequence)
        assert runner.sequence == sequence.upper()
        
    @pytest.mark.parametrize("sequence", [
        "",
        "AUGCX",
        "123456",
        "AUGC-AUGC",
        "AUGC AUGC",
        None,
    ])
    def test_invalid_sequences(self, sequence):
        """Test various invalid sequences."""
        with pytest.raises(RNAFoldError):
            RNArunner(sequence)
