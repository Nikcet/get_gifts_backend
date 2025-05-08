Fast run:
```bash  
pip install uv
``` 
```bash
uv sync
```
```bash
huey_consumer main.huey -w 4 
```
```bash
uv run uvicorn main:app --reload
```
