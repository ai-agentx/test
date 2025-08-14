## openai-agents test

### Run

```bash
python -m venv .venv
source .venv/Scripts/activate

pip install -r requirements.txt
npm install -g @modelcontextprotocol/server-filesystem

export OPENAI_API_KEY=sk-1234
export OPENAI_API_BASE_URL=http://127.0.0.1:4000
export OPENAI_MODEL=gemini-2.5

python stdio_test.py
```

### Reference

- [openai-agents-python-examples-mcp](https://github.com/openai/openai-agents-python/tree/main/examples/mcp/)
