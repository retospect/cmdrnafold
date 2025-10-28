"""
Linting and code quality tests.

This module contains tests that verify code formatting, style, and quality
standards. These tests fail early if code needs formatting or has quality issues.
"""

import subprocess
import sys
import os
from pathlib import Path
import pytest

# Get the project root directory
PROJECT_ROOT = Path(__file__).parent.parent
SRC_DIR = PROJECT_ROOT / "src"
TESTS_DIR = PROJECT_ROOT / "tests"


class TestCodeFormatting:
    """Test code formatting and style compliance."""
    
    def test_black_formatting(self):
        """Test that code is properly formatted with Black."""
        try:
            result = subprocess.run(
                [sys.executable, "-m", "black", "--check", "--diff", str(SRC_DIR), str(TESTS_DIR)],
                cwd=PROJECT_ROOT,
                capture_output=True,
                text=True,
                timeout=60
            )
            
            if result.returncode != 0:
                pytest.fail(
                    f"Code is not properly formatted with Black.\n"
                    f"Run 'black {SRC_DIR} {TESTS_DIR}' to fix formatting issues.\n"
                    f"Output:\n{result.stdout}\n{result.stderr}"
                )
                
        except subprocess.TimeoutExpired:
            pytest.fail("Black formatting check timed out")
        except FileNotFoundError:
            pytest.skip("Black not installed")
    
    def test_isort_import_sorting(self):
        """Test that imports are properly sorted with isort."""
        try:
            result = subprocess.run(
                [sys.executable, "-m", "isort", "--check-only", "--diff", str(SRC_DIR), str(TESTS_DIR)],
                cwd=PROJECT_ROOT,
                capture_output=True,
                text=True,
                timeout=60
            )
            
            if result.returncode != 0:
                pytest.fail(
                    f"Imports are not properly sorted with isort.\n"
                    f"Run 'isort {SRC_DIR} {TESTS_DIR}' to fix import sorting.\n"
                    f"Output:\n{result.stdout}\n{result.stderr}"
                )
                
        except subprocess.TimeoutExpired:
            pytest.fail("isort check timed out")
        except FileNotFoundError:
            pytest.skip("isort not installed")
    
    def test_flake8_style_compliance(self):
        """Test code style compliance with flake8."""
        try:
            result = subprocess.run(
                [sys.executable, "-m", "flake8", str(SRC_DIR), str(TESTS_DIR)],
                cwd=PROJECT_ROOT,
                capture_output=True,
                text=True,
                timeout=60
            )
            
            if result.returncode != 0:
                pytest.fail(
                    f"Code style violations found with flake8.\n"
                    f"Fix the following issues:\n{result.stdout}\n{result.stderr}"
                )
                
        except subprocess.TimeoutExpired:
            pytest.fail("flake8 check timed out")
        except FileNotFoundError:
            pytest.skip("flake8 not installed")
    
    @pytest.mark.skipif(sys.platform == "win32", reason="mypy can be unstable on Windows CI")
    def test_mypy_type_checking(self):
        """Test type checking with mypy."""
        try:
            result = subprocess.run(
                [sys.executable, "-m", "mypy", str(SRC_DIR)],
                cwd=PROJECT_ROOT,
                capture_output=True,
                text=True,
                timeout=120
            )
            
            if result.returncode != 0:
                pytest.fail(
                    f"Type checking errors found with mypy.\n"
                    f"Fix the following type issues:\n{result.stdout}\n{result.stderr}"
                )
                
        except subprocess.TimeoutExpired:
            pytest.fail("mypy check timed out")
        except FileNotFoundError:
            pytest.skip("mypy not installed")


class TestProjectStructure:
    """Test project structure and organization."""
    
    def test_src_directory_exists(self):
        """Test that src directory exists and contains package."""
        assert SRC_DIR.exists(), "src directory must exist"
        assert (SRC_DIR / "cmdrnafold").exists(), "cmdrnafold package must exist in src"
        assert (SRC_DIR / "cmdrnafold" / "__init__.py").exists(), "__init__.py must exist"
    
    def test_tests_directory_exists(self):
        """Test that tests directory exists."""
        assert TESTS_DIR.exists(), "tests directory must exist"
        
    def test_pyproject_toml_exists(self):
        """Test that pyproject.toml exists."""
        assert (PROJECT_ROOT / "pyproject.toml").exists(), "pyproject.toml must exist"
        
    def test_readme_exists(self):
        """Test that README.md exists."""
        assert (PROJECT_ROOT / "README.md").exists(), "README.md must exist"
        
    def test_license_exists(self):
        """Test that LICENSE file exists."""
        assert (PROJECT_ROOT / "LICENSE").exists(), "LICENSE file must exist"


class TestCodeQuality:
    """Test code quality and best practices."""
    
    def test_no_debug_statements(self):
        """Test that no debug statements are left in code."""
        debug_patterns = [
            b"pdb.set_trace()",
            b"breakpoint()",
            b"import pdb",
            b"from pdb import",
            b"print(",  # This might be too strict, but good for production
            b"console.log(",  # In case there's any JS
        ]
        
        violations = []
        
        # Check Python files in src
        for py_file in SRC_DIR.rglob("*.py"):
            content = py_file.read_bytes()
            for pattern in debug_patterns:
                if pattern in content:
                    # Skip print statements in docstrings/comments
                    if pattern == b"print(" and (b'"""' in content or b"'''" in content):
                        continue
                    violations.append(f"{py_file}: contains {pattern.decode()}")
        
        if violations:
            pytest.fail(
                f"Debug statements found in source code:\n" + 
                "\n".join(violations) +
                "\nRemove debug statements before committing."
            )
    
    def test_no_todo_fixme_in_src(self):
        """Test that no TODO/FIXME comments are in source code."""
        todo_patterns = [b"TODO", b"FIXME", b"XXX", b"HACK"]
        violations = []
        
        # Only check source files, not tests
        for py_file in SRC_DIR.rglob("*.py"):
            content = py_file.read_bytes()
            for pattern in todo_patterns:
                if pattern in content:
                    violations.append(f"{py_file}: contains {pattern.decode()}")
        
        if violations:
            pytest.fail(
                f"TODO/FIXME comments found in source code:\n" + 
                "\n".join(violations) +
                "\nResolve or move to issues before release."
            )
    
    def test_proper_docstrings(self):
        """Test that all public functions have docstrings."""
        import ast
        import inspect
        
        violations = []
        
        for py_file in SRC_DIR.rglob("*.py"):
            if py_file.name == "__init__.py":
                continue
                
            try:
                with open(py_file, 'r', encoding='utf-8') as f:
                    tree = ast.parse(f.read(), filename=str(py_file))
                
                for node in ast.walk(tree):
                    if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
                        # Skip private functions
                        if node.name.startswith('_'):
                            continue
                            
                        # Check if function has docstring
                        if (not node.body or 
                            not isinstance(node.body[0], ast.Expr) or
                            not isinstance(node.body[0].value, ast.Constant) or
                            not isinstance(node.body[0].value.value, str)):
                            violations.append(f"{py_file}:{node.lineno}: {node.name}() missing docstring")
                            
                    elif isinstance(node, ast.ClassDef):
                        # Skip private classes
                        if node.name.startswith('_'):
                            continue
                            
                        # Check if class has docstring
                        if (not node.body or 
                            not isinstance(node.body[0], ast.Expr) or
                            not isinstance(node.body[0].value, ast.Constant) or
                            not isinstance(node.body[0].value.value, str)):
                            violations.append(f"{py_file}:{node.lineno}: {node.name} class missing docstring")
                            
            except SyntaxError:
                violations.append(f"{py_file}: Syntax error, cannot parse")
        
        if violations:
            pytest.fail(
                f"Missing docstrings found:\n" + 
                "\n".join(violations) +
                "\nAdd docstrings to all public functions and classes."
            )


class TestSecurityScanning:
    """Test security scanning with bandit."""
    
    def test_bandit_security_scan(self):
        """Test security issues with bandit."""
        try:
            result = subprocess.run(
                [sys.executable, "-m", "bandit", "-r", str(SRC_DIR), "-f", "txt"],
                cwd=PROJECT_ROOT,
                capture_output=True,
                text=True,
                timeout=60
            )
            
            # Bandit returns 1 for issues found, 0 for no issues
            if result.returncode == 1:
                # Parse output to see if there are actual security issues
                if "No issues identified" not in result.stdout:
                    pytest.fail(
                        f"Security issues found with bandit:\n{result.stdout}\n{result.stderr}"
                    )
            elif result.returncode > 1:
                pytest.fail(f"Bandit failed to run: {result.stderr}")
                
        except subprocess.TimeoutExpired:
            pytest.fail("Bandit security scan timed out")
        except FileNotFoundError:
            pytest.skip("bandit not installed")


class TestDependencyManagement:
    """Test dependency management and configuration."""
    
    def test_pyproject_toml_valid(self):
        """Test that pyproject.toml is valid TOML."""
        try:
            import tomllib
        except ImportError:
            try:
                import tomli as tomllib
            except ImportError:
                pytest.skip("No TOML parser available")
        
        pyproject_path = PROJECT_ROOT / "pyproject.toml"
        try:
            with open(pyproject_path, 'rb') as f:
                tomllib.load(f)
        except Exception as e:
            pytest.fail(f"pyproject.toml is not valid TOML: {e}")
    
    def test_version_consistency(self):
        """Test that version is consistent across files."""
        import re
        
        # Read version from pyproject.toml
        pyproject_path = PROJECT_ROOT / "pyproject.toml"
        pyproject_content = pyproject_path.read_text()
        pyproject_match = re.search(r'version = "([^"]+)"', pyproject_content)
        
        if not pyproject_match:
            pytest.fail("Could not find version in pyproject.toml")
        
        pyproject_version = pyproject_match.group(1)
        
        # Read version from __init__.py
        init_path = SRC_DIR / "cmdrnafold" / "__init__.py"
        init_content = init_path.read_text()
        init_match = re.search(r'__version__ = "([^"]+)"', init_content)
        
        if not init_match:
            pytest.fail("Could not find __version__ in __init__.py")
        
        init_version = init_match.group(1)
        
        if pyproject_version != init_version:
            pytest.fail(
                f"Version mismatch: pyproject.toml has {pyproject_version}, "
                f"__init__.py has {init_version}"
            )


if __name__ == "__main__":
    # Allow running this file directly for quick checks
    pytest.main([__file__, "-v"])
