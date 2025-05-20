# REST API of wishlist service: [wishesbook.ru](https://wishesbook.ru)

## Fast run
### First:
```bash  
pip install uv
```
```bash
uv python install
```
```bash
uv sync
```
### Second:
Create a .env file and copy content from .env.example:
```bash
cp .env.example .env
```
### Third:
```bash
uv run huey_consumer main.huey -w 4 
```
```bash
uv run uvicorn main:app --reload
```
