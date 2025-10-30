"""
app_gradio.py
Beautiful Web UI for Multi-Agent System using Gradio
"""

from typing import Dict
import gradio as gr
import json
import time
from pathlib import Path
import threading

from demo_phase3 import Phase3System
from export_formats import ProposalExporter


class GradioApp:
    """Gradio Web Interface for Grant Proposal Generator"""
    
    def __init__(self):
        self.system = None
        self.system_lock = threading.Lock()
        self.exporter = ProposalExporter()
        self.last_proposal_data = None
    
    def initialize_system(self):
        """Initialize the multi-agent system"""
        if self.system is None:
            with self.system_lock:
                if self.system is None:  # Double-check
                    self.system = Phase3System()
                    self.system.start_all_agents()
                    time.sleep(2)
    
    def analyze_paper(
        self,
        pdf_file,
        progress=gr.Progress()
    ):
        """
        Main function: Analyze paper and generate proposal
        
        Args:
            pdf_file: Uploaded PDF file
            progress: Gradio progress tracker
        
        Returns:
            Tuple of (analysis_html, proposal_text, download_json, download_txt, download_docx, download_pdf)
        """
        if pdf_file is None:
            return "❌ Please upload a PDF file", "", None, None, None, None
        
        # Initialize system
        progress(0, desc="Initializing system...")
        self.initialize_system()
        
        try:
            # Step 1: Validate PDF (10%)
            progress(0.1, desc="Validating PDF...")
            pdf_path = pdf_file.name
            
            validation = self.system.pdf_reader.validate_pdf(pdf_path)
            if not validation['valid']:
                return f"❌ Invalid PDF: {validation['errors']}", "", None, None, None, None
            
            # Step 2: Analysis (30%)
            progress(0.3, desc="🔬 Analyst extracting information...")
            analysis_result = self.system._get_analysis(pdf_path)
            
            if 'error' in analysis_result:
                return f"❌ Analysis failed: {analysis_result['error']}", "", None, None, None, None
            
            # Step 3: Evaluation (50%)
            progress(0.5, desc="⚖️ Evaluator assessing quality...")
            evaluation_result = self.system._get_evaluation(analysis_result)
            
            if 'error' in evaluation_result:
                return f"❌ Evaluation failed: {evaluation_result['error']}", "", None, None, None, None
            
            # Step 4: Innovation (70%)
            progress(0.7, desc="💡 Innovator generating future directions...")
            innovation_result = self.system._get_innovations(analysis_result, evaluation_result)
            
            if 'error' in innovation_result:
                return f"❌ Innovation failed: {innovation_result['error']}", "", None, None, None, None
            
            # Step 5: Detect conflicts (80%)
            progress(0.8, desc="🔍 Detecting conflicts...")
            conflicts = self.system._detect_conflicts(analysis_result, evaluation_result, innovation_result)
            
            # Step 6: Write proposal (90%)
            progress(0.9, desc="✍️ Writer synthesizing proposal...")
            proposal_result = self.system._get_proposal(
                analysis_result,
                evaluation_result,
                innovation_result,
                conflicts
            )
            
            if 'error' in proposal_result:
                return f"❌ Proposal generation failed: {proposal_result['error']}", "", None, None, None, None
            
            # Step 7: Format results & Export (100%)
            progress(1.0, desc="✅ Creating exports...")
            
            # Store proposal data for export functions
            self.last_proposal_data = {
                'analysis': analysis_result,
                'evaluation': evaluation_result,
                'innovations': innovation_result,
                'conflicts': conflicts,
                'proposal': proposal_result
            }
            
            # Create analysis HTML
            analysis_html = self._format_analysis_html(
                analysis_result,
                evaluation_result,
                innovation_result,
                conflicts
            )
            
            # Get proposal text
            proposal_text = proposal_result.get('full_text', '')
            
            # Create downloadable files
            json_data = {
                'analysis': analysis_result,
                'evaluation': evaluation_result,
                'innovations': innovation_result,
                'conflicts': conflicts,
                'metadata': proposal_result.get('metadata', {})
            }
            
            json_file = self._create_json_file(json_data)
            txt_file = self._create_txt_file(proposal_text)
            
            # Auto-generate DOCX and PDF
            docx_file = self._export_docx(self.last_proposal_data)
            pdf_file = self._export_pdf(self.last_proposal_data)
            
            return analysis_html, proposal_text, json_file, txt_file, docx_file, pdf_file
            
        except Exception as e:
            return f"❌ Error: {str(e)}", "", None, None, None, None
    
    def _format_analysis_html(
        self,
        analysis: dict,
        evaluation: dict,
        innovations: dict,
        conflicts: list
    ) -> str:
        """Format analysis results as HTML"""
        
        html = "<div style='font-family: Arial, sans-serif;'>"
        
        # Title
        html += f"<h2>📄 {analysis.get('title', 'Unknown')}</h2>"
        html += f"<p><strong>Authors:</strong> {', '.join(analysis.get('authors', ['Unknown'])[:5])}</p>"
        
        if analysis.get('year'):
            html += f"<p><strong>Year:</strong> {analysis['year']}"
        if analysis.get('venue'):
            html += f" | <strong>Venue:</strong> {analysis['venue']}"
        html += "</p>"
        
        # Scores
        html += "<h3>📊 Quality Assessment</h3>"
        html += "<table style='width:100%; border-collapse: collapse;'>"
        html += "<tr style='background-color: #f0f0f0;'>"
        html += "<th style='padding: 8px; text-align: left; border: 1px solid #ddd;'>Metric</th>"
        html += "<th style='padding: 8px; text-align: left; border: 1px solid #ddd;'>Score</th>"
        html += "</tr>"
        
        scores = evaluation.get('scores', {})
        for metric, score in scores.items():
            color = self._get_score_color(score)
            html += f"<tr>"
            html += f"<td style='padding: 8px; border: 1px solid #ddd;'>{metric.capitalize()}</td>"
            html += f"<td style='padding: 8px; border: 1px solid #ddd; background-color: {color};'><strong>{score}/10</strong></td>"
            html += "</tr>"
        
        html += "</table>"
        
        # Funding potential
        funding = evaluation.get('funding_potential', 'UNKNOWN')
        funding_color = {'HIGH': '#90EE90', 'MEDIUM': '#FFD700', 'LOW': '#FFB6C1', 'UNKNOWN': '#D3D3D3'}.get(funding, '#D3D3D3')
        html += f"<p><strong>💰 Funding Potential:</strong> <span style='background-color: {funding_color}; padding: 4px 8px; border-radius: 4px;'>{funding}</span></p>"
        
        # Key Contributions
        html += "<h3>✨ Key Contributions</h3>"
        html += "<ul>"
        for contrib in analysis.get('key_contributions', [])[:5]:
            html += f"<li>{contrib}</li>"
        html += "</ul>"
        
        # Strengths & Weaknesses
        html += "<div style='display: flex; gap: 20px;'>"
        
        # Strengths
        html += "<div style='flex: 1;'>"
        html += "<h3>✅ Strengths</h3>"
        html += "<ul>"
        for strength in evaluation.get('strengths', [])[:5]:
            html += f"<li>{strength}</li>"
        html += "</ul>"
        html += "</div>"
        
        # Weaknesses
        html += "<div style='flex: 1;'>"
        html += "<h3>⚠️ Weaknesses</h3>"
        html += "<ul>"
        for weakness in evaluation.get('weaknesses', [])[:5]:
            html += f"<li>{weakness}</li>"
        html += "</ul>"
        html += "</div>"
        
        html += "</div>"
        
        # Future Directions
        html += "<h3>💡 Future Research Directions</h3>"
        html += "<ol>"
        for direction in innovations.get('future_directions', [])[:5]:
            html += f"<li><strong>{direction.get('direction', 'N/A')}</strong><br>"
            html += f"<small>{direction.get('description', '')}</small><br>"
            html += f"<small>Feasibility: {direction.get('feasibility', 'N/A')} | "
            html += f"Timeframe: {direction.get('timeframe', 'N/A')}</small></li>"
        html += "</ol>"
        
        # Industry Applications
        html += "<h3>🏭 Industry Applications</h3>"
        html += "<ul>"
        for app in innovations.get('industry_applications', [])[:5]:
            html += f"<li><strong>{app.get('domain', 'N/A')}:</strong> {app.get('application', 'N/A')}</li>"
        html += "</ul>"
        
        # Conflicts
        if conflicts:
            html += "<h3>🔍 Conflicts Resolved</h3>"
            html += "<ul>"
            for conflict in conflicts:
                html += f"<li><strong>{conflict['type']}:</strong> {conflict['description']}<br>"
                html += f"<small>Resolution: {conflict['resolution']}</small></li>"
            html += "</ul>"
        
        # Commercial Potential
        commercial = innovations.get('commercial_potential', 'UNKNOWN')
        commercial_color = {'HIGH': '#90EE90', 'MEDIUM': '#FFD700', 'LOW': '#FFB6C1', 'UNKNOWN': '#D3D3D3'}.get(commercial, '#D3D3D3')
        html += f"<p><strong>💼 Commercial Potential:</strong> <span style='background-color: {commercial_color}; padding: 4px 8px; border-radius: 4px;'>{commercial}</span></p>"
        
        # Vision
        if innovations.get('ten_year_vision'):
            html += "<h3>🔮 10-Year Vision</h3>"
            html += f"<p>{innovations['ten_year_vision']}</p>"
        
        html += "</div>"
        
        return html
    
    def _get_score_color(self, score):
        """Get color based on score"""
        if score >= 8:
            return "#90EE90"  # Light green
        elif score >= 6:
            return "#FFD700"  # Gold
        elif score >= 4:
            return "#FFB6C1"  # Light pink
        else:
            return "#FFB6C1"  # Light red
    
    def _create_json_file(self, data: dict) -> str:
        """Create JSON file for download"""
        filepath = "grant_proposal_data.json"
        with open(filepath, 'w') as f:
            json.dump(data, f, indent=2)
        return filepath
    
    def _create_txt_file(self, text: str) -> str:
        """Create text file for download"""
        filepath = "grant_proposal.txt"
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(text)
        return filepath
    
    def _export_docx(self, proposal_data: Dict) -> str:
        """Export to DOCX"""
        try:
            filepath = "grant_proposal.docx"
            self.exporter.export_to_docx(proposal_data, filepath, template='nsf')
            return filepath
        except Exception as e:
            print(f"⚠️ DOCX export error: {e}")
            return None
    
    def _export_pdf(self, proposal_data: Dict) -> str:
        """Export to PDF"""
        try:
            filepath = "grant_proposal.pdf"
            self.exporter.export_to_pdf(proposal_data, filepath, method='reportlab')
            return filepath
        except Exception as e:
            print(f"⚠️ PDF export error: {e}")
            return None
    
    def _export_html(self, proposal_data: Dict) -> str:
        """Export to HTML"""
        try:
            filepath = "grant_proposal.html"
            self.exporter.export_to_html(proposal_data, filepath)
            return filepath
        except Exception as e:
            print(f"⚠️ HTML export error: {e}")
            return None
    
    def export_docx_callback(self):
        """Callback for DOCX export button"""
        if self.last_proposal_data:
            return self._export_docx(self.last_proposal_data)
        return None
    
    def export_pdf_callback(self):
        """Callback for PDF export button"""
        if self.last_proposal_data:
            return self._export_pdf(self.last_proposal_data)
        return None
    
    def export_html_callback(self):
        """Callback for HTML export button"""
        if self.last_proposal_data:
            return self._export_html(self.last_proposal_data)
        return None
    
    def create_interface(self):
        """Create Gradio interface"""
        
        # Custom CSS
        css = """
        .container {
            max-width: 1200px;
            margin: auto;
        }
        .header {
            text-align: center;
            padding: 20px;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            border-radius: 10px;
            margin-bottom: 20px;
        }
        """
        
        with gr.Blocks(css=css, theme=gr.themes.Soft()) as app:
            gr.HTML("""
                <div class="header">
                    <h1>🤖 AI Grant Proposal Generator</h1>
                    <p>Multi-Agent System for Research Paper Analysis & Grant Writing</p>
                </div>
            """)
            
            with gr.Row():
                with gr.Column(scale=1):
                    gr.Markdown("### 📤 Upload Paper")
                    pdf_input = gr.File(
                        label="Research Paper (PDF)",
                        file_types=[".pdf"],
                        type="filepath"
                    )
                    
                    analyze_btn = gr.Button(
                        "🚀 Generate Grant Proposal",
                        variant="primary",
                        size="lg"
                    )
                    
                    gr.Markdown("""
                    ### ℹ️ How it works
                    
                    1. **Upload** your research paper (PDF)
                    2. **Wait** 60-90 seconds for analysis
                    3. **Review** the analysis and proposal
                    4. **Download** results in JSON/TXT format
                    
                    ### ⚙️ System Features
                    
                    - 5 AI agents working together
                    - Quality assessment (0-10 scores)
                    - Future research directions
                    - Industry applications
                    - Complete grant proposal
                    - Conflict resolution
                    """)
            
                with gr.Column(scale=2):
                    gr.Markdown("### 📊 Analysis Results")
                    
                    with gr.Tabs():
                        with gr.Tab("📄 Analysis"):
                            analysis_output = gr.HTML(
                                label="Paper Analysis",
                                elem_classes="analysis-output"
                            )
                        
                        with gr.Tab("📝 Grant Proposal"):
                            proposal_output = gr.Textbox(
                                label="Complete Proposal",
                                lines=30,
                                max_lines=50,
                                show_copy_button=True
                            )
                        
                        with gr.Tab("💾 Downloads"):
                            gr.Markdown("### Download Results")
                            
                            with gr.Row():
                                with gr.Column():
                                    json_download = gr.File(
                                        label="📊 Structured Data (JSON)"
                                    )
                                    
                                    txt_download = gr.File(
                                        label="📝 Full Proposal (TXT)"
                                    )
                                
                                with gr.Column():
                                    docx_download = gr.File(
                                        label="📄 Word Document (DOCX)"
                                    )
                                    
                                    pdf_download = gr.File(
                                        label="📕 PDF Document"
                                    )
                            
                            gr.Markdown("### Export Options")
                            
                            with gr.Row():
                                export_docx_btn = gr.Button("📄 Export to DOCX", size="sm")
                                export_pdf_btn = gr.Button("📕 Export to PDF", size="sm")
                                export_html_btn = gr.Button("🌐 Export to HTML", size="sm")
                            
                            html_download = gr.File(
                                label="🌐 HTML Document",
                                visible=False
                            )
            
            # Examples
           # gr.Markdown("### 📚 Example Papers")
            #gr.Examples(
               # examples=[
                  #  ["example_papers/transformer.pdf"],
                 #   ["example_papers/resnet.pdf"],
                #    ["example_papers/bert.pdf"]
               # ],
              #  inputs=pdf_input,
             #   label="Try these examples (if available)"
            #)
            
            # Connect button
            analyze_btn.click(
                fn=self.analyze_paper,
                inputs=[pdf_input],
                outputs=[analysis_output, proposal_output, json_download, txt_download, docx_download, pdf_download]
            )
            
            # Connect export buttons
            export_docx_btn.click(
                fn=self.export_docx_callback,
                outputs=[docx_download]
            )
            
            export_pdf_btn.click(
                fn=self.export_pdf_callback,
                outputs=[pdf_download]
            )
            
            export_html_btn.click(
                fn=self.export_html_callback,
                outputs=[html_download]
            ).then(
                lambda: gr.update(visible=True),
                outputs=[html_download]
            )
            
            gr.Markdown("""
            ---
            ### 🎓 About
            
            This system uses 5 specialized AI agents:
            - **Supervisor**: Orchestrates the workflow
            - **Analyst**: Extracts paper information
            - **Evaluator**: Assesses quality and funding potential
            - **Innovator**: Generates future directions
            - **Writer**: Synthesizes grant proposal
            
            Built with: Python, Groq LLM, Multi-Agent Architecture
            """)
        
        return app
    
    def launch(self, share=False, server_port=7860):
        """Launch the Gradio app"""
        app = self.create_interface()
        app.launch(
            share=share,
            server_port=server_port,
            server_name="0.0.0.0"
        )


def main():
    """Main entry point"""
    print("="*70)
    print("🚀 Starting Gradio Web UI...")
    print("="*70)
    print()
    
    app = GradioApp()
    
    print("✅ Initializing multi-agent system...")
    print("   This may take a few seconds...")
    print()
    
    print("🌐 Launching web interface...")
    print("   Local URL: http://localhost:7860")
    print("   Share URL: Use share=True for public link")
    print()
    print("Press Ctrl+C to stop the server")
    print("="*70)
    
    app.launch(share=False)


if __name__ == "__main__":
    main()