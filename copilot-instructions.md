# Weather App — Copilot Instructions

## Stack
- Python 3.12, Streamlit, requests, pytest

## Code Standards
- Use type hints on all functions
- API keys must always come from os.getenv() — never hardcoded
- All external HTTP calls must have a timeout parameter
- Use f-strings for string formatting
- Functions must be small and single-purpose

## Error Handling
- Always use try/except around API calls
- Show user-friendly error messages in Streamlit (st.error)
- Never expose raw exception messages to the UI

## Testing
- Every new function in weather.py needs a pytest test
- Mock all HTTP calls using the `responses` library