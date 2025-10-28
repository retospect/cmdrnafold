# cmdrnafold - Professional Python Wrapper for ViennaRNA

[![PyPI version](https://badge.fury.io/py/cmdrnafold.svg)](https://badge.fury.io/py/cmdrnafold)
[![Python versions](https://img.shields.io/pypi/pyversions/cmdrnafold.svg)](https://pypi.org/project/cmdrnafold/)
[![CI](https://github.com/retospect/cmdrnafold/actions/workflows/check.yml/badge.svg)](https://github.com/retospect/cmdrnafold/actions/workflows/check.yml)
[![CodeQL](https://github.com/retospect/cmdrnafold/actions/workflows/codeql.yml/badge.svg)](https://github.com/retospect/cmdrnafold/actions/workflows/codeql.yml)
[![codecov](https://codecov.io/gh/retospect/cmdrnafold/branch/main/graph/badge.svg)](https://codecov.io/gh/retospect/cmdrnafold)
[![License: GPL v3](https://img.shields.io/badge/License-GPLv3-blue.svg)](https://www.gnu.org/licenses/gpl-3.0)
[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)
[![Imports: isort](https://img.shields.io/badge/%20imports-isort-%231674b1?style=flat&labelColor=ef8336)](https://pycqa.github.io/isort/)
[![Type checked: mypy](https://img.shields.io/badge/type%20checked-mypy-blue.svg)](https://mypy-lang.org/)
[![Security: bandit](https://img.shields.io/badge/security-bandit-yellow.svg)](https://github.com/PyCQA/bandit)

A **production-ready**, **type-safe** Python wrapper for [ViennaRNA](https://www.tbi.univie.ac.at/RNA/ViennaRNA/refman/man/RNAfold.html) commandline tools with both **synchronous** and **asynchronous** interfaces.

Perfect for when you need a reliable RNA folding solution but can't get the [official ViennaRNA Python bindings](https://pypi.org/project/ViennaRNA/) to work properly.

## ✨ Features

- 🚀 **Both sync and async interfaces** - Choose what fits your workflow
- 🔒 **Type-safe** - Full type annotations with mypy support
- 🛡️ **Production-ready** - Comprehensive error handling and input validation
- 🧪 **Well-tested** - 90%+ test coverage with unit, integration, and security tests
- 📦 **Modern Python** - Supports Python 3.10+ with modern async/await patterns
- 🔍 **Security-focused** - Input validation prevents command injection attacks
- 📚 **Fully documented** - Comprehensive docstrings and examples
- 🏗️ **Professional CI/CD** - Automated testing, security scanning, and releases

## 🚀 Quick Start

### Installation

```bash
pip install cmdrnafold
```

**Requirements:**
- Python 3.10+
- [ViennaRNA commandline tools](https://www.tbi.univie.ac.at/RNA/) installed and available in PATH

### Basic Usage (Synchronous)

```python
from cmdrnafold import RNA

# Simple drop-in replacement for ViennaRNA Python bindings
sequence = "CGCAGGGAUACCCGCG"

# Create fold compound
fc = RNA.fold_compound(sequence)

# Compute minimum free energy structure
structure, mfe = fc.mfe()

print(f"{structure} [{mfe:6.2f}]")
# Output: ((((.......)))) [ -4.20]
```

### Advanced Usage (Asynchronous)

```python
import asyncio
from cmdrnafold import fold_compound

async def fold_rna_sequences():
    sequences = [
        "CGCAGGGAUACCCGCG",
        "AAAUUUGGGCCCUUUU", 
        "GGGCCCAAAUUUGGGCCC"
    ]
    
    # Process multiple sequences concurrently
    tasks = []
    for seq in sequences:
        fc = fold_compound(seq)
        tasks.append(fc.mfe())
    
    results = await asyncio.gather(*tasks)
    
    for seq, (structure, mfe) in zip(sequences, results):
        print(f"{seq}")
        print(f"{structure} [{mfe:6.2f}]")
        print()

# Run the async function
asyncio.run(fold_rna_sequences())
```

### Error Handling

```python
from cmdrnafold import RNA, RNAFoldError

try:
    # This will raise an error due to invalid nucleotides
    fc = RNA.fold_compound("INVALID_SEQUENCE")
    structure, mfe = fc.mfe()
except RNAFoldError as e:
    print(f"RNA folding failed: {e}")
```

## 📖 API Reference

### Classes

#### `RNA.fold_compound(sequence: str) -> SyncRNArunner`
Creates a synchronous RNA fold compound (backward compatible interface).

#### `fold_compound(sequence: str) -> RNArunner` 
Creates an asynchronous RNA fold compound.

#### `fold_compound_sync(sequence: str) -> SyncRNArunner`
Creates a synchronous RNA fold compound (explicit interface).

### Methods

#### `mfe() -> Tuple[str, float]`
Computes the minimum free energy (MFE) structure.

**Returns:**
- `structure`: Secondary structure in dot-bracket notation
- `mfe`: Minimum free energy in kcal/mol

**Raises:**
- `RNAFoldError`: If folding computation fails

### Input Validation

The library performs strict input validation:
- Only valid RNA nucleotides (A, U, G, C) are allowed
- Empty sequences are rejected
- Command injection attempts are blocked
- Unicode and special characters are filtered

## 🧪 Development

### Setup Development Environment

```bash
# Clone the repository
git clone https://github.com/retospect/cmdrnafold.git
cd cmdrnafold

# Install Poetry (if not already installed)
curl -sSL https://install.python-poetry.org | python3 -

# Install dependencies
poetry install --with dev

# Install pre-commit hooks
poetry run pre-commit install
```

### Running Tests

```bash
# Run all tests
poetry run pytest

# Run with coverage
poetry run pytest --cov=cmdrnafold --cov-report=html

# Run only unit tests
poetry run pytest -m "not integration"

# Run only integration tests (requires ViennaRNA)
poetry run pytest -m "integration"

# Run linting tests
poetry run pytest tests/test_linting.py
```

### Code Quality

```bash
# Format code
poetry run black src/ tests/
poetry run isort src/ tests/

# Type checking
poetry run mypy src/

# Linting
poetry run flake8 src/ tests/

# Security scan
poetry run bandit -r src/
```

## 🔒 Security

This project takes security seriously:

- **Input validation** prevents command injection attacks
- **Bandit** static security analysis in CI
- **CodeQL** security scanning
- **Dependabot** for dependency vulnerability management
- **No hardcoded secrets** or credentials

## 🤝 Contributing

Contributions are welcome! Please see our [Contributing Guidelines](CONTRIBUTING.md) for details.

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Make your changes
4. Run tests (`poetry run pytest`)
5. Commit your changes (`git commit -m 'Add amazing feature'`)
6. Push to the branch (`git push origin feature/amazing-feature`)
7. Open a Pull Request

## 📄 License

This project is licensed under the GNU General Public License v3.0 or later - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- [ViennaRNA Package](https://www.tbi.univie.ac.at/RNA/) - The underlying RNA folding algorithms
- [Poetry](https://python-poetry.org/) - Dependency management and packaging
- [pytest](https://pytest.org/) - Testing framework

## 📚 Citation

If you use cmdrnafold in your research, please cite:

```bibtex
@software{cmdrnafold,
  author = {Stamm, Reto},
  title = {cmdrnafold: Professional Python Wrapper for ViennaRNA},
  url = {https://github.com/retospect/cmdrnafold},
  version = {0.0.6},
  year = {2024}
}
```

---

**Made with ❤️ for the bioinformatics community**
