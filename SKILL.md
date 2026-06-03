---
name: debug-weather-tests
description: Debug failing pytest tests in the weather app. Use when tests are failing or when asked to fix tests.
---

When pytest tests are failing in this project, follow these steps:

1. Run `pytest tests/ -v` to see which tests are failing and why
2. Check if the test is mocking HTTP calls correctly using the `responses` library
3. Verify the mock response shape matches what `weather.py` functions expect
4. Check that environment variables are set or mocked in the test
5. Fix the test (or the function if the logic is wrong)
6. Re-run pytest to confirm all tests pass