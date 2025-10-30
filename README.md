# 🤖 AI Grant Proposal Generator

[![Python 3.8+](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Gradio](https://img.shields.io/badge/UI-Gradio-orange)](https://gradio.app/)
[![Groq](https://img.shields.io/badge/LLM-Groq-green)](https://groq.com/)

**Production-ready multi-agent AI system that analyzes research papers and generates professional NSF/NIH-style grant proposals in 60-90 seconds.**

![Demo](https://via.placeholder.com/800x400?text=Demo+Screenshot)

---

## 🎯 Features

### Core System
- 🤖 **5 Specialized AI Agents** working collaboratively
- 📄 **Automatic PDF Analysis** - Extract key information from papers
- ⚖️ **Quality Assessment** - Score papers on 5 dimensions (0-10)
- 💡 **Innovation Generation** - Identify future research directions
- ✍️ **Grant Proposal Writing** - Complete NSF/NIH-style proposals
- 🔍 **Conflict Resolution** - Intelligent disagreement handling

### User Interfaces
- 🌐 **Web UI** - Beautiful Gradio interface
- 💻 **CLI** - Command-line tools for power users
- 🔄 **Batch Processing** - Analyze multiple papers simultaneously

### Export Formats
- 📄 **DOCX** - Microsoft Word documents
- 📕 **PDF** - Professional PDF format
- 🌐 **HTML** - Web pages
- 📋 **Markdown** - Plain text with formatting
- 📊 **JSON** - Structured data

### Advanced Features
- 📁 **Batch Processing** - Process 10-100 papers automatically
- 💬 **Human Feedback Loop** - Iterative refinement
- 📊 **Comparison Reports** - Rank and compare papers
- 📚 **Version Control** - Track changes and feedback
- 🎨 **Professional Templates** - NSF/NIH formatting

---

## 🚀 Quick Start

### 1. Clone Repository

```bash
git clone https://github.com/AyobamiMichael/grant-proposal-generator.git
cd grant-proposal-generator
```

### 2. Install Dependencies

```bash
# Create virtual environment
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# Install all dependencies
pip install -r requirements.txt
pip install -r requirements_enhancements.txt
```

### 3. Configure API Key

Create `.env` file:
```bash
GROQ_API_KEY="your_groq_api_key_here"
```

Get free API key: https://console.groq.com/keys

### 4. Run Web Interface

```bash
python app_gradio.py
```

Opens at: http://localhost:7860

### 5. Upload & Generate

1. Upload research paper (PDF)
2. Click "Generate Grant Proposal"
3. Wait 60-90 seconds
4. Download results (JSON, TXT, DOCX, PDF)

---

## 📖 Documentation

- [Phase 1: Core System](docs/PHASE1.md) - Agent architecture & messaging
- [Phase 2: Analysis](docs/PHASE2.md) - Analyst & Evaluator agents
- [Phase 3: Complete System](docs/PHASE3.md) - All 5 agents working together
- [Enhancements Guide](docs/ENHANCEMENTS.md) - Web UI, batch, export, feedback
- [API Documentation](docs/API.md) - Python API reference
- [Deployment Guide](docs/DEPLOYMENT.md) - Cloud deployment instructions

---

## 🏗️ Architecture

```
┌─────────────────────────────────────────────────────┐
│                  USER INTERFACE                      │
│         (Gradio Web UI / CLI / Python API)           │
└─────────────────────────────────────────────────────┘
                         │
┌─────────────────────────────────────────────────────┐
│              SUPERVISOR AGENT                        │
│         (Orchestration & Routing)                    │
└─────────────────────────────────────────────────────┘
         │              │              │              │
    ┌────────┐    ┌─────────┐   ┌──────────┐   ┌────────┐
    │ANALYST │    │EVALUATOR│   │INNOVATOR │   │WRITER  │
    │Extract │    │Assess   │   │Generate  │   │Synth.  │
    │Info    │    │Quality  │   │Futures   │   │Proposal│
    └────────┘    └─────────┘   └──────────┘   └────────┘
         │              │              │              │
         └──────────────┴──────────────┴──────────────┘
                         │
              ┌─────────────────────┐
              │  MESSAGE QUEUE      │
              │  (Async Comm.)      │
              └─────────────────────┘
```

### Agent Roles

| Agent | Role | Output |
|-------|------|--------|
| **Supervisor** | Orchestration | Task routing, conflict resolution |
| **Analyst** | Information Extraction | Paper metadata, contributions, gaps |
| **Evaluator** | Quality Assessment | Scores (0-10), funding potential |
| **Innovator** | Future Directions | Research directions, applications |
| **Writer** | Proposal Synthesis | Complete grant proposal |

---

## 💻 Usage Examples

### Web UI

```bash
python app_gradio.py
```

### CLI - Single Paper

```bash
python demo_phase3.py
# Choose option 1, enter PDF path
```

### CLI - Batch Processing

```bash
python batch_processor.py papers_folder/ -o results/
```

### CLI - Export to DOCX/PDF

```bash
python export_formats.py proposal_data.json -f docx
python export_formats.py proposal_data.json -f pdf
```

### CLI - Interactive Refinement

```bash
python feedback_loop.py proposal_data.json
```

### Python API

```python
from demo_phase3 import Phase3System

# Initialize system
system = Phase3System()
system.start_all_agents()

# Generate proposal
result = system.generate_grant_proposal('paper.pdf')

# Access results
analysis = result['analysis']
evaluation = result['evaluation']
proposal = result['proposal']

# Export
from export_formats import ProposalExporter
exporter = ProposalExporter()
exporter.export_to_docx(result, 'proposal.docx')
```

---

## 📊 Performance

| Metric | Value |
|--------|-------|
| **Processing Time** | 60-90 seconds per paper |
| **Throughput** | ~40 papers/hour (sequential) |
| **API Calls** | 8-12 per paper |
| **Output Size** | 3,000-5,000 words |
| **Accuracy** | Quality scores ±0.5 of human ratings* |
| **Success Rate** | 95%+ on readable PDFs |

*Based on internal testing

---

## 🛠️ Technology Stack

- **Language**: Python 3.8+
- **LLM**: Groq (Llama 3.1, Mixtral)
- **Web UI**: Gradio 4.36
- **PDF Processing**: PyPDF
- **Document Export**: python-docx, reportlab
- **Architecture**: Multi-agent message-passing
- **Async**: Threading-based concurrency

---

## 📁 Project Structure

```
multi-agent-grant-proposal/
├── README.md                       # This file
├── LICENSE                         # MIT License
├── requirements.txt                # Core dependencies
├── requirements_enhancements.txt   # Enhancement dependencies
├── .env.example                    # Environment template
├── .gitignore                      # Git ignore rules
│
├── demo_phase1.py                  # Phase 1: Core system
├── demo_phase2.py                  # Phase 2: Analysis agents
├── demo_phase3.py                  # Phase 3: Complete system
│
├── app_gradio.py                   # Web interface
├── batch_processor.py              # Batch processing
├── export_formats.py               # Document export
├── feedback_loop.py                # Interactive refinement
│
├── tools/
│   ├── __init__.py
│   ├── llm_wrapper.py              # Groq LLM interface
│   └── pdf_reader.py               # PDF extraction
│
├── agents/
│   ├── __init__.py
│   ├── analyst_agent.py            # Paper analysis
│   ├── evaluator_agent.py          # Quality assessment
│   ├── innovator_agent.py          # Future directions
│   └── writer_agent.py             # Proposal generation
│
├── tests/
│   ├── test_multi_agent.py         # Unit tests
│   └── test_phase3.py              # Integration tests
│
├── docs/
│   ├── PHASE1.md
│   ├── PHASE2.md
│   ├── PHASE3.md
│   ├── ENHANCEMENTS.md
│   ├── API.md
│   └── DEPLOYMENT.md
│
└── deployment/
    ├── Dockerfile                  # Docker container
    ├── docker-compose.yml          # Docker compose
    ├── railway.json                # Railway config
    ├── render.yaml                 # Render config
    └── requirements-deploy.txt     # Production deps
```

---

## 🧪 Testing

```bash
# Run all tests
python test_multi_agent.py

# Test Phase 3
python test_phase3.py

# Test Groq connection
python test_groq.py

# Verify setup
python verify_setup.py
```

---





## 🤝 Contributing

Contributions welcome! Please:

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit changes (`git commit -m 'Add amazing feature'`)
4. Push to branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

See [CONTRIBUTING.md](CONTRIBUTING.md) for guidelines.

---

## 📝 License

This project is licensed under the MIT License - see [LICENSE](LICENSE) file.

---

## 🙏 Acknowledgments

- **Groq** - Fast LLM inference
- **Gradio** - Beautiful web interfaces
- **PyPDF** - PDF processing
- **python-docx** - Document generation
- **Anthropic Claude** - Development assistance

---

## 📞 Support

- **Issues**: [GitHub Issues](https://github.com/AyobamiMichael/grant-proposal-generator/issues)
- **Discussions**: [GitHub Discussions](https://github.com/AyobamiMichael/grant-proposal-generator/discussions)
- **Email**: ayobamiwealth@gmail.com

---

## 🗺️ Roadmap

- [ ] Add authentication & user accounts
- [ ] Database integration for proposal storage
- [ ] Support for more funding agencies (EU, NIH, NSF variants)
- [ ] Multi-language support
- [ ] Collaborative editing
- [ ] Template customization
- [ ] Integration with reference managers (Zotero, Mendeley)
- [ ] Mobile app

---

## 📈 Stats

![GitHub stars](https://img.shields.io/github/stars/https://github.com/AyobamiMichael/grant-proposal-generator)
![GitHub forks](https://img.shields.io/github/https://github.com/AyobamiMichael/grant-proposal-generator)
![GitHub issues](https://img.shields.io/github/issues/https://github.com/AyobamiMichael/grant-proposal-generator)
![GitHub pull requests](https://img.shields.io/github/issues-pr/https://github.com/AyobamiMichael/grant-proposal-generator)

---

**Built with ❤️ for researchers worldwide**

Star ⭐ this repo if you find it useful!