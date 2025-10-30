"""
batch_processor.py
Process multiple research papers in batch
"""

import os
import json
import time
from pathlib import Path
from datetime import datetime
from typing import List, Dict
import concurrent.futures

from demo_phase3 import Phase3System

class BatchProcessor:
    """
    Batch process multiple research papers
    
    Features:
    - Process multiple PDFs in sequence or parallel
    - Generate reports for each paper
    - Create comparison summary
    - Export results in various formats
    - Progress tracking
    """

    def __init__(self, max_workers=2):
        """
        Initialize batch processor
        
        Args:
            max_workers: Number of parallel workers (default 2)
                        Be careful with rate limits!
        """
        self.max_workers = max_workers
        self.results = []
        self.system = None
    
    def process_folder(
        self,
        folder_path: str,
        output_dir: str = "batch_results",
        parallel: bool = False
    ) -> Dict:
        """
        Process all PDFs in a folder
        
        Args:
            folder_path: Path to folder containing PDFs
            output_dir: Directory to save results
            parallel: Process in parallel (faster but uses more API calls)
        
        Returns:
            Dictionary with results and summary
        """
        print("="*70)
        print("📁 BATCH PROCESSING")
        print("="*70)
        print(f"Folder: {folder_path}")
        print(f"Output: {output_dir}")
        print(f"Mode: {'Parallel' if parallel else 'Sequential'}")
        print()
    
        # Get all PDF files
        pdf_files = self._get_pdf_files(folder_path)
        
        if not pdf_files:
            print("❌ No PDF files found!")
            return {'error': 'No PDFs found'}
        
        print(f"✅ Found {len(pdf_files)} PDF files")
        print()
        
        # Create output directory
        os.makedirs(output_dir, exist_ok=True)


        # Initialize system
        print("🔧 Initializing system...")
        self.system = Phase3System()
        self.system.start_all_agents()
        time.sleep(2)
        print("✅ System ready")
        print()
        
        # Process papers
        start_time = time.time()
        
        if parallel and len(pdf_files) > 1:
            results = self._process_parallel(pdf_files, output_dir)
        else:
            results = self._process_sequential(pdf_files, output_dir)
        
        elapsed_time = time.time() - start_time
        
        # Stop system
        self.system.stop_all_agents()
        
        # Generate summary
        summary = self._generate_summary(results, elapsed_time, output_dir)
        
        print("\n" + "="*70)
        print("✅ BATCH PROCESSING COMPLETE")
        print("="*70)
        print(f"Total Papers: {len(pdf_files)}")
        print(f"Successful: {summary['successful']}")
        print(f"Failed: {summary['failed']}")
        print(f"Total Time: {elapsed_time/60:.1f} minutes")
        print(f"Avg Time/Paper: {elapsed_time/len(pdf_files):.1f} seconds")
        print(f"Results saved to: {output_dir}/")
        print("="*70)
        
        return summary
    
    def _get_pdf_files(self, folder_path: str) -> List[str]:
        """Get all PDF files in folder"""
        pdf_files = []
        for file in Path(folder_path).glob("*.pdf"):
            pdf_files.append(str(file))
        return sorted(pdf_files)
    
    def _process_sequential(self, pdf_files: List[str], output_dir: str) -> List[Dict]:
        """Process papers one by one"""
        results = []
        
        for i, pdf_path in enumerate(pdf_files, 1):
            print(f"📄 Processing {i}/{len(pdf_files)}: {Path(pdf_path).name}")
            print("-" * 70)
            
            result = self._process_single_paper(pdf_path, output_dir, i)
            results.append(result)
            
            # Rate limiting (respect API limits)
            if i < len(pdf_files):
                print("⏳ Waiting 5 seconds (rate limiting)...")
                time.sleep(5)
            
            print()
        
        return results
    
    def _process_parallel(self, pdf_files: List[str], output_dir: str) -> List[Dict]:
        """Process papers in parallel (use with caution!)"""
        print(f"⚡ Processing {len(pdf_files)} papers in parallel...")
        print("   Warning: May hit API rate limits!")
        print()
        
        results = []
        
        with concurrent.futures.ThreadPoolExecutor(max_workers=self.max_workers) as executor:
            # Submit all tasks
            future_to_pdf = {
                executor.submit(self._process_single_paper, pdf, output_dir, i): pdf 
                for i, pdf in enumerate(pdf_files, 1)
            }
            
            # Collect results as they complete
            for future in concurrent.futures.as_completed(future_to_pdf):
                pdf = future_to_pdf[future]
                try:
                    result = future.result()
                    results.append(result)
                    print(f"✅ Completed: {Path(pdf).name}")
                except Exception as e:
                    print(f"❌ Failed: {Path(pdf).name} - {e}")
                    results.append({
                        'pdf_path': pdf,
                        'success': False,
                        'error': str(e)
                    })
        
        return results
    
    def _process_single_paper(self, pdf_path: str, output_dir: str, index: int) -> Dict:
        """Process a single paper"""
        paper_name = Path(pdf_path).stem
        
        try:
            # Generate proposal
            result = self.system.generate_grant_proposal(pdf_path)
            
            if 'error' in result:
                return {
                    'pdf_path': pdf_path,
                    'paper_name': paper_name,
                    'success': False,
                    'error': result['error']
                }
            
            # Save individual results
            self._save_paper_results(result, paper_name, output_dir, index)
            
            # Extract key metrics
            metrics = {
                'title': result['analysis'].get('title', 'Unknown'),
                'quality_score': result['evaluation'].get('scores', {}).get('overall', 0),
                'novelty_score': result['analysis'].get('novelty_assessment', {}).get('score', 0),
                'funding_potential': result['evaluation'].get('funding_potential', 'UNKNOWN'),
                'commercial_potential': result['innovations'].get('commercial_potential', 'UNKNOWN'),
                'word_count': result['proposal'].get('word_count', 0),
                'conflicts': len(result.get('conflicts', []))
            }
            
            return {
                'pdf_path': pdf_path,
                'paper_name': paper_name,
                'success': True,
                'metrics': metrics
            }
            
        except Exception as e:
            return {
                'pdf_path': pdf_path,
                'paper_name': paper_name,
                'success': False,
                'error': str(e)
            }
        
    def _save_paper_results(self, result: Dict, paper_name: str, output_dir: str, index: int):
        """Save results for individual paper"""
        
        # Create paper-specific folder
        paper_dir = os.path.join(output_dir, f"{index:02d}_{paper_name}")
        os.makedirs(paper_dir, exist_ok=True)
        
        # Save JSON data
        json_path = os.path.join(paper_dir, "data.json")
        with open(json_path, 'w') as f:
            json.dump({
                'analysis': result['analysis'],
                'evaluation': result['evaluation'],
                'innovations': result['innovations'],
                'conflicts': result.get('conflicts', []),
                'metadata': result['proposal'].get('metadata', {})
            }, f, indent=2)
        
        # Save proposal text
        txt_path = os.path.join(paper_dir, "proposal.txt")
        with open(txt_path, 'w', encoding='utf-8') as f:
            f.write(result['proposal'].get('full_text', ''))
        
        # Save summary
        summary_path = os.path.join(paper_dir, "summary.txt")
        with open(summary_path, 'w', encoding='utf-8') as f:
            f.write(self._create_paper_summary(result))

    def _create_paper_summary(self, result: Dict) -> str:
        """Create text summary for paper"""
        
        analysis = result['analysis']
        evaluation = result['evaluation']
        innovations = result['innovations']
        
        summary = f"""
PAPER ANALYSIS SUMMARY
{'='*70}

Title: {analysis.get('title', 'Unknown')}
Authors: {', '.join(analysis.get('authors', [])[:5])}
Year: {analysis.get('year', 'Unknown')}

QUALITY SCORES
{'-'*70}
Overall: {evaluation.get('scores', {}).get('overall', 0)}/10
Originality: {evaluation.get('scores', {}).get('originality', 0)}/10
Methodology: {evaluation.get('scores', {}).get('methodology', 0)}/10
Impact: {evaluation.get('scores', {}).get('impact', 0)}/10
Clarity: {evaluation.get('scores', {}).get('clarity', 0)}/10

ASSESSMENT
{'-'*70}
Novelty: {analysis.get('novelty_assessment', {}).get('score', 0)}/10
Funding Potential: {evaluation.get('funding_potential', 'UNKNOWN')}
Commercial Potential: {innovations.get('commercial_potential', 'UNKNOWN')}

KEY CONTRIBUTIONS
{'-'*70}
"""
        for i, contrib in enumerate(analysis.get('key_contributions', [])[:5], 1):
            summary += f"{i}. {contrib}\n"
        
        summary += f"\nSTRENGTHS\n{'-'*70}\n"
        for i, strength in enumerate(evaluation.get('strengths', [])[:5], 1):
            summary += f"{i}. {strength}\n"
        
        summary += f"\nWEAKNESSES\n{'-'*70}\n"
        for i, weakness in enumerate(evaluation.get('weaknesses', [])[:5], 1):
            summary += f"{i}. {weakness}\n"
        
        summary += f"\nFUTURE DIRECTIONS\n{'-'*70}\n"
        for i, direction in enumerate(innovations.get('future_directions', [])[:3], 1):
            summary += f"{i}. {direction.get('direction', 'N/A')}\n"
            summary += f"   {direction.get('description', '')}\n\n"
        
        return summary
    
    def _generate_summary(self, results: List[Dict], elapsed_time: float, output_dir: str) -> Dict:
        """Generate overall batch summary"""
        
        successful = [r for r in results if r.get('success', False)]
        failed = [r for r in results if not r.get('success', False)]
        
        # Calculate statistics
        if successful:
            quality_scores = [r['metrics']['quality_score'] for r in successful]
            novelty_scores = [r['metrics']['novelty_score'] for r in successful]
            
            avg_quality = sum(quality_scores) / len(quality_scores)
            avg_novelty = sum(novelty_scores) / len(novelty_scores)
            
            # Count funding potential
            funding_counts = {}
            for r in successful:
                funding = r['metrics']['funding_potential']
                funding_counts[funding] = funding_counts.get(funding, 0) + 1
        else:
            avg_quality = 0
            avg_novelty = 0
            funding_counts = {}
        
        # Create summary
        summary = {
            'total_papers': len(results),
            'successful': len(successful),
            'failed': len(failed),
            'elapsed_time': elapsed_time,
            'avg_quality_score': avg_quality,
            'avg_novelty_score': avg_novelty,
            'funding_distribution': funding_counts,
            'successful_papers': successful,
            'failed_papers': failed
        }
        
        # Save summary report
        self._save_summary_report(summary, output_dir)
        
        # Create comparison table
        self._create_comparison_table(successful, output_dir)
        
        return summary
    
    def _save_summary_report(self, summary: Dict, output_dir: str):
        """Save summary report"""
        
        report_path = os.path.join(output_dir, "BATCH_SUMMARY.txt")
        
        with open(report_path, 'w', encoding='utf-8') as f:
            f.write("="*70 + "\n")
            f.write("BATCH PROCESSING SUMMARY\n")
            f.write("="*70 + "\n\n")
            
            f.write(f"Processed: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
            f.write(f"Total Papers: {summary['total_papers']}\n")
            f.write(f"Successful: {summary['successful']}\n")
            f.write(f"Failed: {summary['failed']}\n")
            f.write(f"Total Time: {summary['elapsed_time']/60:.1f} minutes\n")
            f.write(f"Avg Time/Paper: {summary['elapsed_time']/summary['total_papers']:.1f} seconds\n\n")
            
            f.write(f"AVERAGE SCORES\n")
            f.write("-"*70 + "\n")
            f.write(f"Quality: {summary['avg_quality_score']:.1f}/10\n")
            f.write(f"Novelty: {summary['avg_novelty_score']:.1f}/10\n\n")
            
            f.write(f"FUNDING POTENTIAL DISTRIBUTION\n")
            f.write("-"*70 + "\n")
            for funding, count in summary['funding_distribution'].items():
                f.write(f"{funding}: {count} papers\n")
            
            f.write("\n" + "="*70 + "\n")
            f.write("SUCCESSFUL PAPERS\n")
            f.write("="*70 + "\n\n")
            
            for paper in summary['successful_papers']:
                f.write(f"📄 {paper['paper_name']}\n")
                f.write(f"   Title: {paper['metrics']['title']}\n")
                f.write(f"   Quality: {paper['metrics']['quality_score']}/10\n")
                f.write(f"   Novelty: {paper['metrics']['novelty_score']}/10\n")
                f.write(f"   Funding: {paper['metrics']['funding_potential']}\n")
                f.write(f"   Commercial: {paper['metrics']['commercial_potential']}\n\n")
            
            if summary['failed_papers']:
                f.write("\n" + "="*70 + "\n")
                f.write("FAILED PAPERS\n")
                f.write("="*70 + "\n\n")
                
                for paper in summary['failed_papers']:
                    f.write(f"❌ {paper['paper_name']}\n")
                    f.write(f"   Error: {paper.get('error', 'Unknown')}\n\n")
        
        # Also save as JSON
        json_path = os.path.join(output_dir, "batch_summary.json")
        with open(json_path, 'w') as f:
            json.dump(summary, f, indent=2)
    
    def _create_comparison_table(self, successful_results: List[Dict], output_dir: str):
        """Create comparison table"""
        
        if not successful_results:
            return
        
        table_path = os.path.join(output_dir, "COMPARISON_TABLE.txt")
        
        with open(table_path, 'w', encoding='utf-8') as f:
            f.write("PAPER COMPARISON TABLE\n")
            f.write("="*140 + "\n\n")
            
            # Header
            f.write(f"{'Paper':<30} {'Quality':>8} {'Novelty':>8} {'Funding':>10} {'Commercial':>12} {'Words':>8}\n")
            f.write("-"*140 + "\n")
            
            # Sort by quality score
            sorted_results = sorted(successful_results, key=lambda x: x['metrics']['quality_score'], reverse=True)
            
            # Rows
            for result in sorted_results:
                name = result['paper_name'][:28]
                metrics = result['metrics']
                
                f.write(f"{name:<30} ")
                f.write(f"{metrics['quality_score']:>8.1f} ")
                f.write(f"{metrics['novelty_score']:>8.1f} ")
                f.write(f"{metrics['funding_potential']:>10} ")
                f.write(f"{metrics['commercial_potential']:>12} ")
                f.write(f"{metrics['word_count']:>8}\n")
            
            f.write("-"*140 + "\n")
        
        # Create CSV version
        csv_path = os.path.join(output_dir, "comparison.csv")
        with open(csv_path, 'w') as f:
            f.write("Paper,Title,Quality,Novelty,Funding,Commercial,Words\n")
            for result in sorted_results:
                metrics = result['metrics']
                f.write(f"{result['paper_name']},")
                f.write(f"\"{metrics['title']}\",")
                f.write(f"{metrics['quality_score']},")
                f.write(f"{metrics['novelty_score']},")
                f.write(f"{metrics['funding_potential']},")
                f.write(f"{metrics['commercial_potential']},")
                f.write(f"{metrics['word_count']}\n")


# ==================== CLI INTERFACE ====================

def main():
    """Command-line interface for batch processing"""
    import argparse
    
    parser = argparse.ArgumentParser(description="Batch process research papers")
    parser.add_argument("folder", help="Folder containing PDF files")
    parser.add_argument("-o", "--output", default="batch_results", help="Output directory")
    parser.add_argument("-p", "--parallel", action="store_true", help="Process in parallel")
    parser.add_argument("-w", "--workers", type=int, default=2, help="Number of parallel workers")
    
    args = parser.parse_args()
    
    # Create processor
    processor = BatchProcessor(max_workers=args.workers)
    
    # Process folder
    summary = processor.process_folder(
        folder_path=args.folder,
        output_dir=args.output,
        parallel=args.parallel
    )
    
    print(f"\n✅ Results saved to: {args.output}/")
    print(f"   - Individual paper folders")
    print(f"   - BATCH_SUMMARY.txt")
    print(f"   - COMPARISON_TABLE.txt")
    print(f"   - comparison.csv")


if __name__ == "__main__":
    main()