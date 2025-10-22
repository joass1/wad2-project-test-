# Backend

basic firebase backend in python

## Requirements

- [uv](https://github.com/astral-sh/uv) (recommended package + venv manager)
- python 3.13

## Setup

```bash
# sync dependencies
cd backend
pip install uv 
uv sync

# activate environment
source .venv/bin/activate   # macos/linux
.venv\Scripts\activate      # windows

# run app
uv run uvicorn app.main:app --reload
```
