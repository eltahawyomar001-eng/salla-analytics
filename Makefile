.PHONY: install run test lint format clean help

help:
	@echo "Advanced Analysis for Salla - Available Commands"
	@echo "================================================"
	@echo "install  - Install all dependencies"
	@echo "run      - Run the Streamlit application"
	@echo "test     - Run the test suite"
	@echo "lint     - Run code quality checks"
	@echo "format   - Format code with black"
	@echo "clean    - Remove temporary files"

install:
	pip install -r requirements.txt

run:
	streamlit run app/main.py

test:
	pytest tests/ -v --cov=app --cov-report=html

lint:
	ruff check app/
	mypy app/

format:
	black app/
	ruff check app/ --fix

clean:
	rm -rf __pycache__
	rm -rf .pytest_cache
	rm -rf .mypy_cache
	rm -rf .ruff_cache
	rm -rf htmlcov
	rm -rf *.egg-info
	find . -type d -name __pycache__ -exec rm -rf {} +
	find . -type f -name "*.pyc" -delete