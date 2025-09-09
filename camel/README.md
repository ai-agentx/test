# CAMEL-AI Framework + MCP Integration Demo

This project demonstrates the **CAMEL framework** (Communicative Agents for "Mind" Exploration of Large Language Model Society) with **Model Context Protocol (MCP)** for building intelligent agents.

This implementation uses the actual CAMEL-AI framework from https://github.com/camel-ai/camel with native MCP integration.

## 🚀 Quick Start

### 1. Install Python 3.12

```bash
pyenv install 3.12.0 && pyenv local 3.12.0
```

> **Note**: https://github.com/pyenv-win/pyenv-win

### 2. Install Dependencies

```bash
pip install -r requirements.txt
```

> **Note**: CAMEL-AI requires Python 3.10-3.12. If you're using Python 3.13, consider using pyenv or conda to install a compatible version.

### 3. Configure Environment

Copy and modify the environment file:

```bash
cp env.py.example env.py
```

Edit `env.py` with your API keys and configuration.

### 4. Run the Demo

```bash
python helloworld.py
```

## 🐍 Python Version Compatibility

- **Python 3.10-3.12**: ✅ Fully supported (recommended)
- **Python 3.13**: ❌ Not yet supported by CAMEL-AI

For Python 3.13 users, consider using:
- **pyenv**: `pyenv install 3.12.0 && pyenv local 3.12.0`
- **conda**: `conda create -n camel python=3.12 && conda activate camel`

## 🐫 About CAMEL Framework

CAMEL is an open-source framework for building multi-agent systems. Key features:

- **Scalability**: Support for millions of agents
- **Evolvability**: Continuous learning and adaptation
- **Statefulness**: Persistent memory for complex interactions
- **Code-as-Prompt**: Clear, readable agent definitions

Learn more: [https://github.com/camel-ai/camel](https://github.com/camel-ai/camel)

## 📚 Additional Resources

- [CAMEL Documentation](https://docs.camel-ai.org/)
- [MCP Specification](https://spec.modelcontextprotocol.io/)
- [CAMEL Cookbook](https://docs.camel-ai.org/cookbooks/)
- [MCP Servers Registry](https://github.com/punkpeye/awesome-mcp-servers)

## 📄 License

This project is for educational purposes. Please refer to the respective licenses of CAMEL and MCP components.
