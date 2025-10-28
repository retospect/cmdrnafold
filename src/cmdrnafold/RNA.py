"""
RNA folding interface using ViennaRNA commandline tools.

This module provides a Python wrapper around the ViennaRNA RNAFold command,
offering both synchronous and asynchronous interfaces for RNA secondary
structure prediction.
"""

import asyncio
import subprocess
from typing import Tuple, Optional, Union
import logging

logger = logging.getLogger(__name__)


class RNAFoldError(Exception):
    """Exception raised when RNA folding operations fail."""
    pass


class RNArunner:
    """
    Asynchronous RNA folding runner using ViennaRNA RNAFold command.
    
    This class provides an interface to the ViennaRNA RNAFold commandline tool,
    allowing for minimum free energy (MFE) structure prediction.
    
    Args:
        sequence: RNA sequence string containing only valid nucleotides (A, U, G, C)
        
    Raises:
        RNAFoldError: If the sequence is invalid or RNAFold execution fails
        
    Example:
        >>> fc = RNArunner("CGCAGGGAUACCCGCG")
        >>> structure, mfe = await fc.mfe()
        >>> print(f"{structure} [{mfe:6.2f}]")
    """
    
    def __init__(self, sequence: str) -> None:
        if not sequence or not isinstance(sequence, str):
            raise RNAFoldError("Sequence must be a non-empty string")
            
        # Validate RNA sequence
        valid_nucleotides = set("AUGC")
        if not all(c.upper() in valid_nucleotides for c in sequence):
            raise RNAFoldError(f"Invalid nucleotides in sequence. Only A, U, G, C allowed.")
            
        self.sequence = sequence.upper()
        self.cmd = "RNAFold --noPS"
        self._hash = hash(self.cmd + self.sequence)
        self._proc: Optional[asyncio.subprocess.Process] = None
        
    async def _ensure_process(self) -> asyncio.subprocess.Process:
        """Ensure the subprocess is created and ready."""
        if self._proc is None:
            try:
                self._proc = await asyncio.create_subprocess_shell(
                    self.cmd,
                    stdin=asyncio.subprocess.PIPE,
                    stdout=asyncio.subprocess.PIPE,
                    stderr=asyncio.subprocess.PIPE,
                )
                
                if self._proc.stdin is None:
                    raise RNAFoldError("Failed to create subprocess stdin")
                    
                # Send sequence and termination signal
                control = f"{self.sequence}\n@\n"
                self._proc.stdin.write(control.encode())
                await self._proc.stdin.drain()
                self._proc.stdin.close()
                
            except (OSError, subprocess.SubprocessError) as e:
                raise RNAFoldError(f"Failed to start RNAFold process: {e}")
                
        return self._proc

    async def mfe(self) -> Tuple[str, float]:
        """
        Compute minimum free energy structure.
        
        Returns:
            Tuple containing (structure, mfe) where:
            - structure: Secondary structure in dot-bracket notation
            - mfe: Minimum free energy in kcal/mol
            
        Raises:
            RNAFoldError: If folding computation fails
        """
        proc = await self._ensure_process()
        
        try:
            stdout, stderr = await proc.communicate()
            
            if proc.returncode != 0:
                error_msg = stderr.decode() if stderr else "Unknown error"
                raise RNAFoldError(f"RNAFold failed with return code {proc.returncode}: {error_msg}")
                
            # Parse output
            result_lines = stdout.decode().strip().split('\n')
            
            if len(result_lines) < 3:
                raise RNAFoldError(f"Unexpected RNAFold output format: {stdout.decode()}")
                
            # Find structure and energy lines
            structure_line = None
            energy_line = None
            
            for i, line in enumerate(result_lines):
                if line.strip() and set(line.strip()) <= set('().'):
                    structure_line = line.strip()
                    if i + 1 < len(result_lines):
                        energy_line = result_lines[i + 1].strip()
                    break
                    
            if not structure_line or not energy_line:
                raise RNAFoldError(f"Could not parse structure from output: {stdout.decode()}")
                
            # Extract MFE from energy line
            # Format: " minimum free energy =  -9.80 kcal/mol" or "( -9.80)"
            try:
                if "minimum free energy" in energy_line:
                    mfe_str = energy_line.split("=")[1].split("kcal/mol")[0].strip()
                elif energy_line.startswith("(") and energy_line.endswith(")"):
                    mfe_str = energy_line[1:-1].strip()
                else:
                    # Try to find a number in the line
                    import re
                    match = re.search(r'(-?\d+\.?\d*)', energy_line)
                    if match:
                        mfe_str = match.group(1)
                    else:
                        raise ValueError("No numeric value found")
                        
                mfe = float(mfe_str)
                
            except (ValueError, IndexError) as e:
                raise RNAFoldError(f"Could not parse MFE from: '{energy_line}': {e}")
                
            return structure_line, mfe
            
        except asyncio.TimeoutError:
            raise RNAFoldError("RNAFold process timed out")
        finally:
            if proc.returncode is None:
                proc.terminate()
                await proc.wait()

    def __hash__(self) -> int:
        """Return hash of the sequence and command."""
        return self._hash
        
    def __repr__(self) -> str:
        """Return string representation."""
        return f"RNArunner(sequence='{self.sequence[:20]}{'...' if len(self.sequence) > 20 else ''}')"


def fold_compound(sequence: str) -> RNArunner:
    """
    Create a new RNA fold compound for the given sequence.
    
    This function provides a drop-in replacement for the ViennaRNA Python
    bindings fold_compound function.
    
    Args:
        sequence: RNA sequence string
        
    Returns:
        RNArunner instance for the sequence
        
    Example:
        >>> fc = fold_compound("CGCAGGGAUACCCGCG")
        >>> structure, mfe = await fc.mfe()
    """
    return RNArunner(sequence)


# Synchronous wrapper for compatibility
class SyncRNArunner:
    """Synchronous wrapper for RNArunner."""
    
    def __init__(self, sequence: str) -> None:
        self._runner = RNArunner(sequence)
        
    def mfe(self) -> Tuple[str, float]:
        """Synchronous MFE computation."""
        try:
            loop = asyncio.get_event_loop()
        except RuntimeError:
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            
        return loop.run_until_complete(self._runner.mfe())
        
    def __hash__(self) -> int:
        return hash(self._runner)
        
    def __repr__(self) -> str:
        return f"Sync{repr(self._runner)}"


def fold_compound_sync(sequence: str) -> SyncRNArunner:
    """
    Create a synchronous RNA fold compound.
    
    Args:
        sequence: RNA sequence string
        
    Returns:
        SyncRNArunner instance for synchronous operations
    """
    return SyncRNArunner(sequence)
