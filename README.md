# 🚀 AICoder - AI-Powered Code Generation System

AICoder is a sophisticated multi-agent system that generates complete, consistent, and error-free code projects from natural language descriptions. It uses LangGraph to orchestrate multiple AI agents that work together to plan, code, and validate projects.

## 🎯 Features

- **🤖 Multi-Agent Architecture**: Coordinated agents for planning, coding, and testing
- **📋 Contract-Based Design**: Agent capabilities defined in JSON contracts
- **🔧 LangGraph Integration**: Robust workflow orchestration
- **📁 File Generation**: Creates complete projects with multiple files
- **✅ Code Validation**: Syntax checking and consistency validation
- **⚙️ Configurable**: Customizable workflow and agent behavior
- **📊 Logging**: Comprehensive logging and error tracking

## 🏗️ Architecture

```
User Prompt → Planner → Coder → Tester → Generated Files
     ↓           ↓        ↓        ↓           ↓
  Input    Architecture  Code   Validation   Output
```

### Agents

- **🧠 Planner**: Creates project architecture and task breakdown
- **💻 Coder**: Generates code based on requirements
- **🧪 Tester**: Validates code quality and functionality
- **🧠 Memory**: Manages context and knowledge persistence
- **🎭 Orchestrator**: Coordinates workflow (optional)
- **🔧 Toolbox**: Provides utility functions
- **✨ Enhancer**: Optimizes code quality

## 🚀 Quick Start

### 1. Installation

```bash
# Clone the repository
git clone <repository-url>
cd AICoder

# Install dependencies
pip install -r requirements.txt

# Set up environment variables
cp .env.example .env
# Edit .env with your API keys
```

### 2. Configuration

Create a `config.json` file (or use the provided one):

```json
{
  "workflow_type": "simple",
  "agents": ["planner", "coder", "tester"],
  "output_format": "python",
  "file_consistency_check": true,
  "error_handling": "strict"
}
```

### 3. Run the Application

```bash
python main.py
```

### 4. Example Usage

```
🎯 Your request: Create a simple calculator with add, subtract, multiply, and divide functions

✅ Project generated successfully!
📁 Project: project_20241219_143022
📄 Files: main.py, test_main.py, README.md
📂 Files saved to: generated_code/project_20241219_143022
```

## 📁 Project Structure

```
AICoder/
├── agents/                 # Agent implementations
│   ├── planner.py         # Planning agent
│   ├── coder.py           # Code generation agent
│   ├── tester.py          # Testing agent
│   └── ...
├── contracts/             # Agent definitions
│   ├── planner.agent.json
│   ├── coder.agent.json
│   └── ...
├── graph/                 # LangGraph workflow
│   ├── langgraph_builder.py
│   └── __init__.py
├── services/              # Shared services
│   ├── llm.py            # LLM service
│   └── __init__.py
├── generated_code/        # Output directory
├── main.py               # Main application
├── config.json           # Configuration
└── README.md
```

## ⚙️ Configuration

### Workflow Types

- **Simple**: Linear workflow (planner → coder → tester)
- **Conditional**: AI-driven routing with orchestrator

### Agent Configuration

```json
{
  "agent_configs": {
    "planner": {
      "max_tokens": 2000,
      "temperature": 0.7
    },
    "coder": {
      "max_tokens": 4000,
      "temperature": 0.3
    }
  }
}
```

### Validation Rules

```json
{
  "validation_rules": {
    "check_syntax": true,
    "check_imports": true,
    "check_unused_variables": false,
    "check_function_definitions": true
  }
}
```

## 🔧 Customization

### Adding New Agents

1. Create agent implementation in `agents/`:
```python
def my_agent_node(state: Dict[str, Any]) -> Dict[str, Any]:
    # Agent logic here
    return {**state, "my_agent_result": result}
```

2. Create contract in `contracts/`:
```json
{
  "name": "MyAgent",
  "path": "agents.my_agent",
  "entrypoint": "my_agent_node",
  "description": "My custom agent",
  "capabilities": ["custom_functionality"]
}
```

3. Update configuration:
```json
{
  "agents": ["planner", "coder", "my_agent"]
}
```

### Custom File Templates

```json
{
  "file_templates": {
    "javascript": {
      "main_file": "index.js",
      "package_file": "package.json",
      "readme_file": "README.md"
    }
  }
}
```

## 🧪 Testing

Run the test suite:

```bash
# Test contract-based workflow
python test_contracts_workflow.py

# Test real agent implementations
python test_real_agents.py

# Test main application
python test_main_application.py

# Test workflow approaches
python test_workflow_approaches.py
```

## 📊 Logging

The system provides comprehensive logging:

- **File**: `aicoder.log`
- **Console**: Real-time output
- **Levels**: INFO, WARNING, ERROR

Example log output:
```
2024-12-19 14:30:22 - AICoderWorkflow - INFO - Initialized
2024-12-19 14:30:23 - AICoderWorkflow - INFO - Workflow execution completed
2024-12-19 14:30:24 - AICoderWorkflow - INFO - Generated 3 files
```

## 🔍 Troubleshooting

### Common Issues

1. **LangGraph Import Error**
   ```bash
   pip install langgraph
   ```

2. **API Key Issues**
   - Check `.env` file
   - Verify API key permissions
   - Ensure sufficient credits

3. **Workflow Initialization Failed**
   - Check agent contracts
   - Verify agent implementations
   - Review configuration

### Debug Mode

Enable debug logging in `config.json`:
```json
{
  "logging_level": "DEBUG"
}
```

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Add tests for new functionality
4. Ensure all tests pass
5. Submit a pull request

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🙏 Acknowledgments

- LangGraph for workflow orchestration
- OpenAI/Anthropic for LLM services
- The open-source community for inspiration

---

**Happy Coding! 🎉**