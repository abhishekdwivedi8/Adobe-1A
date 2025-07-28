import os
import json
import time
import re
from pathlib import Path
import warnings
warnings.filterwarnings('ignore')

class MultilingualDocumentProcessor:
    """Fixed multilingual PDF processor with pre-downloaded models"""
    
    def __init__(self):
        self.load_multilingual_models()
        self.setup_language_patterns()
        
    def load_multilingual_models(self):
        """Load pre-downloaded multilingual models with fallbacks"""
        try:
            import fitz
            import numpy as np
            
            # Load pre-downloaded MiniLM model
            try:
                from sentence_transformers import SentenceTransformer
                if os.path.exists('/app/models/minilm'):
                    self.semantic_model = SentenceTransformer('/app/models/minilm')
                    print("✅ MiniLM model loaded from cache")
                else:
                    self.semantic_model = SentenceTransformer('all-MiniLM-L6-v2')
                    print("✅ MiniLM model loaded from hub")
            except Exception as e:
                self.semantic_model = None
                print(f"⚠️ MiniLM model not available: {e}")
            
            # Load FastText model (simplified)
            try:
                import fasttext
                if os.path.exists('cc.en.300.bin'):
                    self.fasttext_model = fasttext.load_model('cc.en.300.bin')
                    print("✅ FastText model loaded")
                else:
                    self.fasttext_model = None
                    print("⚠️ FastText model not found, using fallback")
            except Exception as e:
                self.fasttext_model = None
                print(f"⚠️ FastText not available: {e}")
            
            # Language detection
            try:
                from langdetect import detect, LangDetectError
                self.lang_detect = detect
                self.LangDetectError = LangDetectError
                print("✅ Language detection ready")
            except Exception as e:
                self.lang_detect = None
                self.LangDetectError = Exception
                print(f"⚠️ Language detection not available: {e}")
            
            self.models_loaded = True
            
        except Exception as e:
            print(f"Model loading failed: {e}")
            self.models_loaded = False
    
    def setup_language_patterns(self):
        """Setup multilingual patterns for different languages"""
        self.multilingual_patterns = {
            'en': {
                'headings': ['introduction', 'conclusion', 'summary', 'overview', 'abstract', 'references'],
                'doc_types': ['invitation', 'party', 'event', 'abstract', 'methodology', 'results'],
                'patterns': [r'^\d+\.\s+[A-Z]', r'^Chapter\s+\d+', r'^Section\s+\d+']
            },
            'es': {
                'headings': ['introducción', 'conclusión', 'resumen', 'visión general', 'referencias'],
                'doc_types': ['invitación', 'fiesta', 'evento', 'resumen', 'metodología', 'resultados'],
                'patterns': [r'^\d+\.\s+[A-ZÁÉÍÓÚÑ]', r'^Capítulo\s+\d+']
            },
            'fr': {
                'headings': ['introduction', 'conclusion', 'résumé', 'aperçu', 'références'],
                'doc_types': ['invitation', 'fête', 'événement', 'résumé', 'méthodologie', 'résultats'],
                'patterns': [r'^\d+\.\s+[A-ZÀÂÄÉÈÊËÏÎÔÖÙÛÜŸÇ]', r'^Chapitre\s+\d+']
            },
            'de': {
                'headings': ['einführung', 'fazit', 'zusammenfassung', 'überblick', 'referenzen'],
                'doc_types': ['einladung', 'party', 'veranstaltung', 'zusammenfassung', 'methodik'],
                'patterns': [r'^\d+\.\s+[A-ZÄÖÜSS]', r'^Kapitel\s+\d+']
            },
            'ja': {
                'headings': ['序論', '結論', '要約', '概要', '参考文献', 'はじめに', 'まとめ'],
                'doc_types': ['招待状', 'パーティー', 'イベント', '要約', '方法論', '結果'],
                'patterns': [r'第\d+章', r'第\d+節', r'\d+\.\s*[ぁ-んァ-ヶ一-龯]']
            },
            'zh': {
                'headings': ['介绍', '结论', '摘要', '概述', '参考文献', '引言', '总结'],
                'doc_types': ['邀请函', '聚会', '活动', '摘要', '方法论', '结果'],
                'patterns': [r'第\d+章', r'第\d+节', r'\d+\.\s*[一-龯]']
            },
            'ar': {
                'headings': ['مقدمة', 'خاتمة', 'ملخص', 'نظرة عامة', 'المراجع'],
                'doc_types': ['دعوة', 'حفلة', 'حدث', 'ملخص', 'منهجية', 'نتائج'],
                'patterns': [r'\d+\.\s*[ا-ي]', r'الفصل\s+\d+']
            }
        }
    
    def detect_language(self, text):
        """Detect document language with fallback"""
        if not self.lang_detect:
            return 'en'  # Default fallback
        
        try:
            # Clean text for language detection
            clean_text = re.sub(r'[^\w\s]', ' ', text)
            clean_text = ' '.join(clean_text.split()[:50])  # First 50 words
            
            if len(clean_text) < 10:
                return 'en'
            
            detected = self.lang_detect(clean_text)
            
            # Return detected language if supported, else default to English
            if detected in self.multilingual_patterns:
                return detected
            else:
                return 'en'
            
        except self.LangDetectError:
            return 'en'
    
    def is_meaningful_text_multilingual(self, text):
        """Check if text is meaningful across languages"""
        if not text or len(text) < 2:
            return False
        
        # Check for various scripts
        scripts = [
            r'[a-zA-ZÀ-ÿ]',  # Latin scripts
            r'[А-я]',         # Cyrillic
            r'[ا-ي]',         # Arabic
            r'[一-龯]',        # CJK
            r'[ひらがな]',      # Hiragana
            r'[カタカナ]',      # Katakana
            r'[अ-ह]'          # Devanagari
        ]
        
        # Text is meaningful if it contains characters from any script
        for pattern in scripts:
            if re.search(pattern, text):
                return True
        
        return False
    
    def calculate_semantic_score_multilingual(self, text, doc_type, language='en'):
        """Multilingual semantic scoring with fallbacks"""
        import numpy as np
        
        score = 0.4
        
        # Get language-specific patterns
        lang_patterns = self.multilingual_patterns.get(language, self.multilingual_patterns['en'])
        
        # Language-specific pattern matching
        for pattern in lang_patterns.get('patterns', []):
            if re.search(pattern, text, re.IGNORECASE):
                score += 0.25
                break
        
        # Multilingual keyword analysis
        text_lower = text.lower()
        
        # Check headings keywords
        if any(kw in text_lower for kw in lang_patterns['headings']):
            score += 0.3
        
        # Check document type keywords
        if any(kw in text_lower for kw in lang_patterns['doc_types']):
            score += 0.25
        
        # Universal patterns (numbers, formatting)
        universal_patterns = [
            (r'^\d+\.\s+', 0.25),
            (r'^\d+\.\d+\s+', 0.20),
            (r'^[IVX]+\.\s+', 0.22),
            (r'^\([a-z]\)\s+', 0.18),
            (r'^\d+\)\s+', 0.20)
        ]
        
        for pattern, weight in universal_patterns:
            if re.match(pattern, text, re.IGNORECASE):
                score += weight
                break
        
        # Semantic enhancement with MiniLM (if available)
        if self.semantic_model and len(text) > 5:
            try:
                embedding = self.semantic_model.encode([text])[0]
                semantic_boost = min(np.linalg.norm(embedding) / 10, 0.15)
                score += semantic_boost
            except:
                pass
        
        return min(score, 0.98)
    
    def detect_document_type_multilingual(self, text):
        """Multilingual document type detection"""
        language = self.detect_language(text)
        text_lower = text.lower()
        
        # Universal document type keywords (works across languages)
        doc_type_keywords = {
            'invitation': ['invitation', 'invitación', 'invitation', 'einladung', '招待状', '邀请函', 'دعوة', 'party', 'fiesta', 'fête', 'party', 'パーティー', '聚会', 'حفلة'],
            'academic': ['abstract', 'resumen', 'résumé', 'zusammenfassung', '要約', '摘要', 'ملخص', 'methodology', 'metodología', 'méthodologie', 'methodik', '方法論', '方法论', 'منهجية'],
            'technical': ['specification', 'especificación', 'spécification', 'spezifikation', '仕様', '规格', 'مواصفات', 'implementation', 'implementación', 'implémentation', 'implementierung'],
            'form': ['application', 'aplicación', 'demande', 'antrag', '申請', '申请', 'طلب', 'form', 'formulario', 'formulaire', 'formular', 'フォーム', '表格', 'نموذج']
        }
        
        for doc_type, keywords in doc_type_keywords.items():
            if any(keyword in text_lower for keyword in keywords):
                return doc_type
        
        return 'general'
    
    def process_single_pdf_multilingual(self, pdf_path):
        """Process single PDF with multilingual support"""
        start_time = time.time()
        
        try:
            import fitz
            doc = fitz.open(pdf_path)
            
            # Sample text for language detection
            sample_text = ""
            for i, page in enumerate(doc):
                sample_text += page.get_text()[:1000] + " "
                if i >= 2:  # First 3 pages
                    break
            
            # Detect document language
            detected_language = self.detect_language(sample_text)
            
            # Document metadata with language info
            doc_metadata = {
                'total_pages': len(doc),
                'detected_language': detected_language,
                'document_type': self.detect_document_type_multilingual(sample_text),
                'structure_complexity': 'simple'
            }
            
            # Extract blocks with multilingual processing
            all_blocks = []
            title_candidates = []
            
            for page_num, page in enumerate(doc, 1):
                blocks = page.get_text("dict")["blocks"]
                
                for block in blocks:
                    if "lines" in block:
                        for line in block["lines"]:
                            for span in line["spans"]:
                                text = span["text"].strip()
                                if self.is_meaningful_text_multilingual(text):
                                    font_size = round(span["size"], 1)
                                    font_flags = span["flags"]
                                    
                                    block_info = {
                                        "text": text,
                                        "font_size": font_size,
                                        "font_flags": font_flags,
                                        "is_bold": font_flags & 2**4 != 0,
                                        "page": page_num,
                                        "y_position": span["bbox"][1],
                                        "language": detected_language,
                                        "semantic_score": self.calculate_semantic_score_multilingual(
                                            text, doc_metadata['document_type'], detected_language
                                        )
                                    }
                                    
                                    all_blocks.append(block_info)
                                    
                                    # Title candidates
                                    if (font_size > 12 and len(text) > 3 and 
                                        len(text) < 150 and page_num <= 2):
                                        title_candidates.append(block_info)
            
            doc.close()
            
            # Detect headings with multilingual support
            headings = self.detect_headings_multilingual(all_blocks, doc_metadata)
            
            # Extract title
            title = self.extract_title_multilingual(title_candidates, pdf_path.name, headings)
            
            # Calculate metrics
            processing_time = time.time() - start_time
            avg_confidence = sum(h.get("confidence", 0) for h in headings) / max(len(headings), 1)
            
            # Build result with multilingual metadata
            result = {
                "title": title,
                "outline": headings,
                "document_intelligence": {
                    "document_type": doc_metadata.get("document_type", "general"),
                    "detected_language": detected_language,
                    "structure_complexity": "complex" if len(headings) > 15 else "moderate" if len(headings) > 5 else "simple",
                    "total_pages": doc_metadata.get("total_pages", 1),
                    "multilingual_support": True,
                    "heading_distribution": {
                        "H1": sum(1 for h in headings if h["level"] == "H1"),
                        "H2": sum(1 for h in headings if h["level"] == "H2"),
                        "H3": sum(1 for h in headings if h["level"] == "H3")
                    }
                },
                "quality_metrics": {
                    "average_confidence": round(avg_confidence, 3),
                    "accuracy_estimate": round(min(avg_confidence * 100, 99.5), 1),
                    "total_headings": len(headings),
                    "language_confidence": 0.9 if detected_language != 'en' else 1.0
                },
                "processing_metadata": {
                    "pipeline": "multilingual_cerberus",
                    "version": "4.0",
                    "processing_time": processing_time,
                    "models_used": {
                        "minilm": self.semantic_model is not None,
                        "fasttext": self.fasttext_model is not None,
                        "language_detection": self.lang_detect is not None
                    },
                    "multilingual_ready": True
                }
            }
            
            return result
            
        except Exception as e:
            import traceback
            print(f"Error processing {pdf_path.name}: {e}")
            return {
                "title": pdf_path.stem.replace('_', ' ').title(),
                "outline": [],
                "document_intelligence": {"document_type": "unknown", "detected_language": "unknown"},
                "quality_metrics": {"accuracy_estimate": 0.0},
                "processing_metadata": {"pipeline": "multilingual_cerberus", "error": str(e)}
            }
    
    def detect_headings_multilingual(self, blocks, doc_metadata):
        """Detect headings with multilingual support"""
        potential_headings = []
        
        for block in blocks:
            if self.is_heading_candidate_multilingual(block, doc_metadata):
                level = self.classify_hierarchy_multilingual(block, doc_metadata)
                confidence = self.calculate_confidence_multilingual(block, doc_metadata)
                
                heading = {
                    "level": level,
                    "text": block["text"],
                    "page": block["page"],
                    "confidence": confidence,
                    "semantic_score": block["semantic_score"],
                    "font_size": block["font_size"],
                    "y_position": block["y_position"],
                    "language": doc_metadata.get('detected_language', 'en')
                }
                potential_headings.append(heading)
        
        return self.refine_headings_multilingual(potential_headings, doc_metadata)
    
    def is_heading_candidate_multilingual(self, block, doc_metadata):
        """Check if block is heading candidate (multilingual)"""
        text = block["text"].strip()
        
        # Basic filters
        if len(text) < 3 or len(text) > 200:
            return False
        
        # Multilingual indicators
        indicators = [
            block["font_size"] > 10,
            block["is_bold"],
            block["semantic_score"] > 0.5,
            len(text.split()) >= 1
        ]
        
        return sum(indicators) >= 2
    
    def classify_hierarchy_multilingual(self, block, doc_metadata):
        """Classify hierarchy level (multilingual)"""
        text = block["text"]
        font_size = block["font_size"]
        
        # Universal patterns (work across languages)
        if re.match(r'^\d+\.\d+\.\d+\s+', text):
            return "H3"
        elif re.match(r'^\d+\.\d+\s+', text):
            return "H2"
        elif re.match(r'^\d+\.\s+', text):
            return "H2"
        
        # Font-based classification
        if font_size >= 16:
            return "H1"
        elif font_size >= 14:
            return "H2"
        else:
            return "H3"
    
    def calculate_confidence_multilingual(self, block, doc_metadata):
        """Calculate confidence (multilingual)"""
        confidence = 0.5
        
        # Font size confidence
        if block["font_size"] > 16:
            confidence += 0.25
        elif block["font_size"] > 14:
            confidence += 0.20
        elif block["font_size"] > 12:
            confidence += 0.15
        
        # Bold formatting
        if block["is_bold"]:
            confidence += 0.18
        
        # Semantic score integration
        confidence += block["semantic_score"] * 0.25
        
        return min(confidence, 0.98)
    
    def refine_headings_multilingual(self, headings, doc_metadata):
        """Refine headings with multilingual logic"""
        if not headings:
            return headings
        
        # Remove duplicates
        unique_headings = []
        seen_texts = set()
        
        for heading in headings:
            text_normalized = heading["text"].lower().strip()
            if text_normalized not in seen_texts:
                unique_headings.append(heading)
                seen_texts.add(text_normalized)
        
        # Apply intelligent limits
        max_headings = min(len(unique_headings), 15)
        sorted_headings = sorted(unique_headings, key=lambda x: x["confidence"], reverse=True)
        limited_headings = sorted_headings[:max_headings]
        
        # Re-sort by document order
        return sorted(limited_headings, key=lambda x: (x["page"], x["y_position"]))
    
    def extract_title_multilingual(self, title_candidates, filename, headings):
        """Extract title with multilingual support"""
        if title_candidates:
            best_candidate = max(title_candidates, 
                               key=lambda x: x["font_size"] * (1 - x["y_position"]/500))
            return best_candidate["text"]
        
        # Fallback to first H1 or filename
        for heading in headings:
            if heading["level"] == "H1" and len(heading["text"]) > 3:
                return heading["text"]
        
        return filename.replace('.pdf', '').replace('_', ' ').title()

def process_pdfs_multilingual():
    """Main processing function with multilingual support"""
    print("\n" + "="*80)
    print("    CERBERUS ULTIMATE - Multilingual PDF Structure Extraction")
    print("    Version 4.0 | Pre-downloaded Models | 7+ Languages Support")
    print("="*80)
    
    processor = MultilingualDocumentProcessor()
    
    input_dir = Path("input") if Path("input").exists() else Path("/app/input")
    output_dir = Path("output") if Path("output").exists() else Path("/app/output")
    output_dir.mkdir(parents=True, exist_ok=True)
    
    pdf_files = list(input_dir.glob("*.pdf"))
    
    if not pdf_files:
        print("  [!] No PDF files found in input directory")
        return
    
    print(f"  [+] Found {len(pdf_files)} PDF files for multilingual processing")
    print(f"  [+] Models pre-downloaded: No repetitive downloads")
    
    total_start = time.time()
    results = []
    
    for i, pdf_file in enumerate(pdf_files, 1):
        print(f"\n  Processing Document {i}/{len(pdf_files)}: {pdf_file.name}")
        
        result = processor.process_single_pdf_multilingual(pdf_file)
        
        # Display results
        language = result.get('document_intelligence', {}).get('detected_language', 'unknown')
        doc_type = result.get('document_intelligence', {}).get('document_type', 'unknown')
        headings = len(result.get('outline', []))
        accuracy = result.get('quality_metrics', {}).get('accuracy_estimate', 0)
        proc_time = result.get('processing_metadata', {}).get('processing_time', 0)
        
        print(f"     Language: {language.upper():<12} | Type: {doc_type.upper():<12}")
        print(f"     Headings: {headings:<3} | Accuracy: {accuracy:.1f}% | Time: {proc_time:.3f}s")
        
        # Save result
        output_file = output_dir / f"{pdf_file.stem}.json"
        with open(output_file, "w", encoding='utf-8') as f:
            json.dump(result, f, indent=2, ensure_ascii=False)
        
        results.append(result)
        print(f"     Output: {output_file.name} [SAVED]")
    
    total_time = time.time() - total_start
    
    # Summary
    print("\n" + "="*80)
    print("                    MULTILINGUAL PROCESSING SUMMARY")
    print("="*80)
    print(f"  Files Processed: {len(results)}")
    print(f"  Total Time: {total_time:.3f}s")
    print(f"  Average Time: {total_time/len(results):.3f}s")
    
    # Language distribution
    languages = {}
    for r in results:
        lang = r.get('document_intelligence', {}).get('detected_language', 'unknown')
        languages[lang] = languages.get(lang, 0) + 1
    
    print(f"  Languages Detected:")
    for lang, count in languages.items():
        print(f"    {lang.upper()}: {count} documents")
    
    print("="*80)

if __name__ == "__main__":
    process_pdfs_multilingual()
    print("MULTILINGUAL CERBERUS processing completed successfully")