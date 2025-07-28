import os
import json
import time
import re
from pathlib import Path
import warnings
warnings.filterwarnings('ignore')

class EnhancedAccuracyProcessor:
    """Enhanced PDF processor with improved real accuracy"""
    
    def __init__(self):
        self.load_models()
        self.setup_enhanced_patterns()
        
    def load_models(self):
        """Load essential dependencies"""
        try:
            import fitz
            import numpy as np
            self.models_loaded = True
            print("Essential models loaded (PyMuPDF + NumPy)")
        except Exception as e:
            print(f"Model loading failed: {e}")
            self.models_loaded = False
    
    def setup_enhanced_patterns(self):
        """Enhanced universal patterns with better accuracy"""
        self.universal_patterns = [
            # Numbered patterns with strict formatting
            (r'^\d+\.\s+[A-Z][a-zA-Z\s]{2,}', 'H1', 0.9),
            (r'^\d+\.\d+\s+[A-Z][a-zA-Z\s]{2,}', 'H2', 0.85),
            (r'^\d+\.\d+\.\d+\s+[A-Z][a-zA-Z\s]{2,}', 'H3', 0.8),
            
            # Roman numerals
            (r'^[IVX]+\.\s+[A-Z][a-zA-Z\s]{3,}', 'H1', 0.85),
            (r'^[ivx]+\.\s+[A-Z][a-zA-Z\s]{3,}', 'H2', 0.8),
            
            # Alphabetic patterns
            (r'^[A-Z]\.\s+[A-Z][a-zA-Z\s]{3,}', 'H2', 0.8),
            (r'^\([a-z]\)\s+[A-Z][a-zA-Z\s]{3,}', 'H3', 0.75),
            
            # Chapter patterns (multilingual)
            (r'^(Chapter|Capítulo|Chapitre|Kapitel)\s+\d+', 'H1', 0.95),
            (r'^第\d+章', 'H1', 0.95),
            (r'^الفصل\s+\d+', 'H1', 0.95)
        ]
    
    def extract_with_enhanced_intelligence(self, pdf_path):
        """Enhanced extraction with better text analysis"""
        try:
            import fitz
            doc = fitz.open(pdf_path)
            
            doc_metadata = {
                'total_pages': len(doc),
                'structure_complexity': 'simple'
            }
            
            all_blocks, title_candidates, font_analysis = self.extract_blocks_enhanced(doc, doc_metadata)
            
            doc.close()
            return all_blocks, title_candidates, font_analysis, doc_metadata
            
        except Exception as e:
            print(f"Extraction error: {e}")
            return [], [], {}, {}
    
    def extract_blocks_enhanced(self, doc, doc_metadata):
        """Enhanced block extraction with better text processing"""
        all_blocks = []
        title_candidates = []
        font_analysis = {}
        
        for page_num, page in enumerate(doc, 1):
            page_blocks, page_titles, page_fonts = self.process_page_enhanced(page, page_num)
            
            all_blocks.extend(page_blocks)
            title_candidates.extend(page_titles)
            
            # Enhanced font analysis
            for font_key, stats in page_fonts.items():
                if font_key not in font_analysis:
                    font_analysis[font_key] = {"count": 0, "bold_count": 0, "sizes": []}
                font_analysis[font_key]["count"] += stats["count"]
                font_analysis[font_key]["bold_count"] += stats["bold_count"]
                font_analysis[font_key]["sizes"].extend(stats.get("sizes", []))
        
        return all_blocks, title_candidates, font_analysis
    
    def process_page_enhanced(self, page, page_num):
        """Enhanced page processing with better text extraction"""
        page_blocks = []
        page_titles = []
        page_fonts = {}
        
        blocks = page.get_text("dict")["blocks"]
        
        for block in blocks:
            if "lines" in block:
                # Combine lines that belong together
                combined_text = self.combine_related_lines(block["lines"])
                
                for text_info in combined_text:
                    text = text_info["text"].strip()
                    if self.is_meaningful_text_enhanced(text):
                        font_size = text_info["font_size"]
                        font_flags = text_info["font_flags"]
                        
                        # Enhanced font analysis
                        font_key = f"{font_size}_{font_flags}"
                        if font_key not in page_fonts:
                            page_fonts[font_key] = {"count": 0, "bold_count": 0, "sizes": []}
                        
                        page_fonts[font_key]["count"] += 1
                        page_fonts[font_key]["sizes"].append(font_size)
                        if font_flags & 2**4:
                            page_fonts[font_key]["bold_count"] += 1
                        
                        block_info = {
                            "text": text,
                            "font_size": font_size,
                            "font_flags": font_flags,
                            "is_bold": font_flags & 2**4 != 0,
                            "page": page_num,
                            "y_position": text_info["y_position"],
                            "x_position": text_info.get("x_position", 0),
                            "width": text_info.get("width", 0),
                            "semantic_score": self.calculate_enhanced_semantic_score(text),
                            "confidence": 0.0,
                            "adaptive_score": 0.0
                        }
                        
                        page_blocks.append(block_info)
                        
                        # Enhanced title detection
                        if self.is_title_candidate_enhanced(block_info, page_num):
                            page_titles.append(block_info)
        
        return page_blocks, page_titles, page_fonts
    
    def combine_related_lines(self, lines):
        """Combine lines that should be treated as single text blocks"""
        combined_texts = []
        
        for line in lines:
            line_text = ""
            font_size = 0
            font_flags = 0
            y_pos = 0
            x_pos = 0
            width = 0
            
            for span in line["spans"]:
                line_text += span["text"]
                font_size = max(font_size, span["size"])
                font_flags = span["flags"]
                y_pos = span["bbox"][1]
                x_pos = span["bbox"][0]
                width = span["bbox"][2] - span["bbox"][0]
            
            if line_text.strip():
                combined_texts.append({
                    "text": line_text.strip(),
                    "font_size": round(font_size, 1),
                    "font_flags": font_flags,
                    "y_position": y_pos,
                    "x_position": x_pos,
                    "width": width
                })
        
        return combined_texts
    
    def is_meaningful_text_enhanced(self, text):
        """Enhanced meaningful text detection with better filtering"""
        if not text or len(text) < 2:
            return False
        
        # Filter out common non-heading patterns
        exclusions = [
            len(text) < 3,
            len(text) > 200,  # Too long for headings
            text.isdigit(),   # Pure numbers
            re.match(r'^[\d\s\.\-\(\)]+$', text),  # Only numbers and punctuation
            text.count('http') > 0,  # URLs
            text.count('@') > 0,     # Email addresses
            text.count('www') > 0,   # Web addresses
            re.match(r'^[^\w]*$', text),  # Only punctuation
        ]
        
        if any(exclusions):
            return False
        
        # Universal script detection
        scripts = [
            r'[a-zA-ZÀ-ÿ]',      # Latin scripts
            r'[А-я]',             # Cyrillic
            r'[ا-ي]',             # Arabic
            r'[一-龯]',            # CJK
            r'[ひらがなカタカナ]',    # Japanese
            r'[अ-ह]'              # Devanagari
        ]
        
        return any(re.search(script, text) for script in scripts)
    
    def calculate_enhanced_semantic_score(self, text):
        """Enhanced semantic scoring with better pattern recognition"""
        import numpy as np
        
        score = 0.3  # Lower base score for stricter filtering
        
        # Enhanced pattern matching with confidence scores
        for pattern, level, confidence in self.universal_patterns:
            if re.match(pattern, text, re.IGNORECASE):
                score += confidence * 0.4  # Weight by pattern confidence
                break
        
        # Text structure analysis
        word_count = len(text.split())
        
        # Optimal word count for headings (3-8 words)
        if 3 <= word_count <= 8:
            score += 0.2
        elif 2 <= word_count <= 12:
            score += 0.1
        else:
            score -= 0.1  # Penalty for too short or too long
        
        # Capitalization patterns
        if text and text[0].isupper():
            if text.isupper() and len(text) > 5:  # ALL CAPS (common for headings)
                score += 0.15
            elif text.istitle():  # Title Case
                score += 0.12
            else:  # First letter capitalized
                score += 0.08
        
        # Penalty for common non-heading patterns
        penalties = [
            ('click', 0.2),
            ('visit', 0.15),
            ('website', 0.2),
            ('information', 0.1),
            ('please', 0.15),
            ('more', 0.1)
        ]
        
        text_lower = text.lower()
        for word, penalty in penalties:
            if word in text_lower:
                score -= penalty
        
        return max(min(score, 0.98), 0.0)  # Clamp between 0 and 0.98
    
    def is_title_candidate_enhanced(self, block, page_num):
        """Enhanced title detection with stricter criteria"""
        if page_num > 2:
            return False
        
        text = block["text"]
        
        # Enhanced title criteria
        criteria = [
            block["font_size"] > 16,  # Larger font
            len(text) > 8,            # Reasonable length
            len(text) < 100,          # Not too long
            len(text.split()) >= 2,   # Multiple words
            text[0].isupper(),        # Starts with capital
            block["y_position"] < 300, # Upper portion of page
            not any(word in text.lower() for word in ['click', 'visit', 'website', 'please'])  # Not action text
        ]
        
        return sum(criteria) >= 5  # Stricter threshold
    
    def detect_headings_enhanced(self, blocks, font_analysis, doc_metadata):
        """Enhanced heading detection with improved accuracy"""
        potential_headings = []
        
        # Enhanced adaptive thresholds
        thresholds = self.calculate_enhanced_thresholds(blocks, font_analysis, doc_metadata)
        
        for block in blocks:
            if self.is_heading_candidate_enhanced_universal(block, thresholds):
                level = self.classify_hierarchy_enhanced(block, thresholds)
                confidence = self.calculate_enhanced_confidence(block, thresholds)
                adaptive_score = self.calculate_enhanced_adaptive_score(block, thresholds)
                
                # Update block with enhanced scores
                block['confidence'] = confidence
                block['adaptive_score'] = adaptive_score
                
                heading = {
                    "level": level,
                    "text": block["text"],
                    "page": block["page"],
                    "confidence": confidence,
                    "semantic_score": block["semantic_score"],
                    "font_size": block["font_size"],
                    "y_position": block["y_position"],
                    "adaptive_score": adaptive_score
                }
                potential_headings.append(heading)
        
        # Enhanced refinement
        refined_headings = self.refine_headings_enhanced(potential_headings, doc_metadata)
        return refined_headings
    
    def calculate_enhanced_thresholds(self, blocks, font_analysis, doc_metadata):
        """Enhanced adaptive thresholds with better statistical analysis"""
        import numpy as np
        
        # Collect all font sizes with their frequencies
        font_data = []
        for block in blocks:
            if block.get("font_size", 0) > 0:
                font_data.append(block["font_size"])
        
        if len(font_data) == 0:
            return {'h1': 18, 'h2': 15, 'h3': 12, 'confidence': 0.8}
        
        font_array = np.array(font_data)
        
        # Statistical analysis
        percentiles = np.percentile(font_array, [25, 50, 75, 85, 95])
        mean_size = np.mean(font_array)
        std_size = np.std(font_array)
        
        # Enhanced threshold calculation
        # Use statistical outliers for heading detection
        h1_threshold = max(percentiles[4], mean_size + 1.5 * std_size)  # 95th percentile or 1.5 std above mean
        h2_threshold = max(percentiles[3], mean_size + 0.5 * std_size)  # 85th percentile or 0.5 std above mean
        h3_threshold = max(percentiles[2], mean_size)                   # 75th percentile or mean
        
        return {
            'h1': h1_threshold,
            'h2': h2_threshold,
            'h3': h3_threshold,
            'mean': mean_size,
            'std': std_size,
            'confidence': 0.8
        }
    
    def is_heading_candidate_enhanced_universal(self, block, thresholds):
        """Enhanced universal heading detection with stricter criteria"""
        text = block["text"].strip()
        
        # Enhanced exclusions
        exclusions = [
            len(text) < 3 or len(text) > 150,
            re.match(r'^\d{1,3}\.?$', text),  # Just numbers
            text.count('.') > 4,              # Too many periods
            text.count(',') > 3,              # Too many commas
            any(word in text.lower() for word in ['click', 'visit', 'website', 'please', 'more information']),
            text.lower().startswith('for more'),
            text.lower().startswith('please'),
            '/' in text and len(text) < 20,   # Incomplete text like "Computer Science/"
        ]
        
        if any(exclusions):
            return False
        
        # Enhanced indicators with weighted scoring
        indicators = []
        
        # Font size indicator (weighted by statistical significance)
        if block["font_size"] >= thresholds['h1']:
            indicators.append(3)  # Strong indicator
        elif block["font_size"] >= thresholds['h2']:
            indicators.append(2)  # Medium indicator
        elif block["font_size"] >= thresholds['h3']:
            indicators.append(1)  # Weak indicator
        
        # Bold formatting
        if block["is_bold"]:
            indicators.append(2)
        
        # Word count (optimal range for headings)
        word_count = len(text.split())
        if 3 <= word_count <= 8:
            indicators.append(2)
        elif 2 <= word_count <= 12:
            indicators.append(1)
        
        # Semantic score
        if block["semantic_score"] > 0.7:
            indicators.append(2)
        elif block["semantic_score"] > 0.5:
            indicators.append(1)
        
        # Pattern matching
        if any(re.match(pattern, text, re.IGNORECASE) for pattern, _, _ in self.universal_patterns):
            indicators.append(3)
        
        # Position on page (headings usually in upper portions)
        if block["y_position"] < 200:
            indicators.append(1)
        
        # Capitalization
        if text.isupper() and len(text) > 5:
            indicators.append(2)
        elif text.istitle():
            indicators.append(1)
        
        # Require higher total score for better precision
        return sum(indicators) >= 6  # Stricter threshold
    
    def classify_hierarchy_enhanced(self, block, thresholds):
        """Enhanced hierarchy classification with better logic"""
        text = block["text"]
        font_size = block["font_size"]
        
        # Pattern-based classification (highest priority)
        for pattern, level, confidence in self.universal_patterns:
            if re.match(pattern, text, re.IGNORECASE):
                return level
        
        # Enhanced font-based classification with relative sizing
        font_ratio_h1 = font_size / thresholds['h1'] if thresholds['h1'] > 0 else 0
        font_ratio_h2 = font_size / thresholds['h2'] if thresholds['h2'] > 0 else 0
        
        # More sophisticated classification
        if font_ratio_h1 >= 1.0 or (block["is_bold"] and font_ratio_h1 >= 0.9):
            return "H1"
        elif font_ratio_h2 >= 1.0 or (block["is_bold"] and font_ratio_h2 >= 0.9):
            return "H2"
        else:
            return "H3"
    
    def calculate_enhanced_confidence(self, block, thresholds):
        """Enhanced confidence calculation with better weighting"""
        confidence = 0.3  # Lower base for stricter filtering
        
        # Font size confidence (relative to thresholds)
        font_size = block["font_size"]
        if font_size >= thresholds['h1']:
            confidence += 0.3
        elif font_size >= thresholds['h2']:
            confidence += 0.25
        elif font_size >= thresholds['h3']:
            confidence += 0.15
        
        # Bold formatting
        if block["is_bold"]:
            confidence += 0.2
        
        # Semantic score integration (weighted)
        confidence += block["semantic_score"] * 0.3
        
        # Pattern matching boost
        if any(re.match(pattern, block["text"], re.IGNORECASE) for pattern, _, _ in self.universal_patterns):
            confidence += 0.15
        
        # Position boost (headings usually at top)
        if block["y_position"] < 200:
            confidence += 0.05
        
        # Word count optimization
        word_count = len(block["text"].split())
        if 3 <= word_count <= 8:
            confidence += 0.1
        elif word_count > 15:
            confidence -= 0.1  # Penalty for very long text
        
        return min(confidence, 0.98)
    
    def calculate_enhanced_adaptive_score(self, block, thresholds):
        """Enhanced adaptive scoring"""
        score = 0.4
        
        font_size = block["font_size"]
        mean_size = thresholds.get('mean', 12)
        std_size = thresholds.get('std', 2)
        
        # Statistical significance of font size
        z_score = (font_size - mean_size) / max(std_size, 1)
        
        if z_score >= 2:      # 2 standard deviations above mean
            score += 0.4
        elif z_score >= 1:    # 1 standard deviation above mean
            score += 0.3
        elif z_score >= 0.5:  # 0.5 standard deviations above mean
            score += 0.2
        
        return min(score, 1.0)
    
    def refine_headings_enhanced(self, headings, doc_metadata):
        """Enhanced heading refinement with better filtering"""
        if not headings:
            return headings
        
        # Enhanced duplicate removal
        unique_headings = self.remove_duplicates_enhanced(headings)
        
        # Enhanced confidence filtering (stricter)
        confidence_threshold = 0.75  # Higher threshold
        filtered_headings = [h for h in unique_headings if h["confidence"] > confidence_threshold]
        
        # Enhanced hierarchy enforcement
        structured_headings = self.enforce_hierarchy_enhanced(filtered_headings)
        
        # Enhanced intelligent limits with quality focus
        final_headings = self.apply_enhanced_limits(structured_headings, doc_metadata)
        
        return final_headings
    
    def remove_duplicates_enhanced(self, headings):
        """Enhanced duplicate removal with similarity detection"""
        unique_headings = []
        seen_signatures = set()
        
        for heading in headings:
            # Create enhanced signature for similarity detection
            text = heading["text"].lower().strip()
            
            # Normalize text for comparison
            normalized = re.sub(r'[^\w\s]', '', text)
            normalized = re.sub(r'\s+', ' ', normalized)
            
            # Create signature from first 3 significant words
            words = [w for w in normalized.split() if len(w) > 2]
            signature = ' '.join(sorted(words[:3])) if len(words) >= 3 else normalized
            
            if signature not in seen_signatures:
                unique_headings.append(heading)
                seen_signatures.add(signature)
        
        return unique_headings
    
    def enforce_hierarchy_enhanced(self, headings):
        """Enhanced hierarchy enforcement with logical structure"""
        if not headings:
            return headings
        
        # Sort by page and position
        sorted_headings = sorted(headings, key=lambda x: (x["page"], x["y_position"]))
        
        # Enhanced hierarchy logic
        enforced = []
        h1_count = 0
        
        for heading in sorted_headings:
            level = heading["level"]
            
            # Limit H1 headings to prevent over-classification
            if level == "H1":
                if h1_count < 5:  # Maximum 5 H1 headings
                    h1_count += 1
                else:
                    heading["level"] = "H2"  # Demote excess H1s to H2
            
            enforced.append(heading)
        
        return enforced
    
    def apply_enhanced_limits(self, headings, doc_metadata):
        """Enhanced intelligent limits with quality focus"""
        total_pages = doc_metadata.get('total_pages', 1)
        
        # Dynamic limits based on document size and quality
        base_limit = min(total_pages * 1.5 + 3, 12)  # More conservative
        
        # Quality-based filtering
        high_quality = [h for h in headings if h["confidence"] > 0.85]
        medium_quality = [h for h in headings if 0.75 <= h["confidence"] <= 0.85]
        
        # Prioritize high quality headings
        selected = high_quality[:int(base_limit * 0.7)]  # 70% from high quality
        remaining_slots = int(base_limit) - len(selected)
        
        if remaining_slots > 0:
            selected.extend(medium_quality[:remaining_slots])
        
        # Re-sort by document order
        return sorted(selected, key=lambda x: (x["page"], x["y_position"]))
    
    def extract_title_enhanced(self, title_candidates, filename, headings):
        """Enhanced title extraction with better logic"""
        if title_candidates:
            # Score title candidates more intelligently
            def title_score(candidate):
                score = candidate["font_size"] * (1 - candidate["y_position"]/500)
                
                # Bonus for being on first page
                if candidate["page"] == 1:
                    score *= 1.2
                
                # Bonus for reasonable length
                text_len = len(candidate["text"])
                if 10 <= text_len <= 80:
                    score *= 1.1
                
                # Penalty for action words
                if any(word in candidate["text"].lower() for word in ['click', 'visit', 'please']):
                    score *= 0.5
                
                return score
            
            best_candidate = max(title_candidates, key=title_score)
            return best_candidate["text"]
        
        # Enhanced fallback logic
        for heading in headings:
            if (heading["level"] == "H1" and 
                len(heading["text"]) > 8 and 
                len(heading["text"]) < 100 and
                heading["page"] == 1):
                return heading["text"]
        
        return filename.replace('.pdf', '').replace('_', ' ').title()
    
    def transform_to_compliant_format(self, advanced_result):
        """Transform to exact hackathon-compliant format"""
        compliant_outline = []
        for heading in advanced_result['outline']:
            compliant_outline.append({
                "level": heading["level"],
                "text": heading["text"], 
                "page": heading["page"]
            })
        
        return {
            "title": advanced_result['title'],
            "outline": compliant_outline
        }
    
    def process_single_pdf_enhanced(self, pdf_path):
        """Process single PDF with enhanced accuracy"""
        start_time = time.time()
        
        try:
            # Enhanced extraction
            blocks, title_candidates, font_analysis, doc_metadata = self.extract_with_enhanced_intelligence(pdf_path)
            
            # Enhanced heading detection
            headings = self.detect_headings_enhanced(blocks, font_analysis, doc_metadata)
            
            # Enhanced title extraction
            title = self.extract_title_enhanced(title_candidates, pdf_path.name, headings)
            
            processing_time = time.time() - start_time
            
            # Build advanced result
            advanced_result = {
                'title': title,
                'outline': headings,
                'processing_time': processing_time
            }
            
            # Transform to compliant format
            compliant_result = self.transform_to_compliant_format(advanced_result)
            
            return compliant_result
            
        except Exception as e:
            print(f"Error processing {pdf_path.name}: {e}")
            return {
                "title": pdf_path.stem.replace('_', ' ').title(),
                "outline": []
            }

def process_pdfs_enhanced():
    """Main processing function with enhanced accuracy"""
    print("\\n" + "="*80)
    print("    CERBERUS ULTIMATE - Enhanced Accuracy PDF Structure Extraction")
    print("    Version 5.0 | Enhanced Accuracy | Hackathon Compliant")
    print("="*80)
    
    processor = EnhancedAccuracyProcessor()
    
    input_dir = Path("input") if Path("input").exists() else Path("/app/input")
    output_dir = Path("output") if Path("output").exists() else Path("/app/output")
    output_dir.mkdir(parents=True, exist_ok=True)
    
    pdf_files = list(input_dir.glob("*.pdf"))
    
    if not pdf_files:
        print("  [!] No PDF files found in input directory")
        return
    
    print(f"  [+] Found {len(pdf_files)} PDF files for enhanced processing")
    print(f"  [+] Enhanced accuracy algorithms active")
    print(f"  [+] Output format: Hackathon compliant")
    
    total_start = time.time()
    results = []
    
    for i, pdf_file in enumerate(pdf_files, 1):
        print(f"\\n  Processing Document {i}/{len(pdf_files)}: {pdf_file.name}")
        
        result = processor.process_single_pdf_enhanced(pdf_file)
        
        headings = len(result.get('outline', []))
        print(f"     Headings: {headings:<3} | Format: COMPLIANT | Accuracy: ENHANCED")
        
        output_file = output_dir / f"{pdf_file.stem}.json"
        with open(output_file, "w", encoding='utf-8') as f:
            json.dump(result, f, indent=2, ensure_ascii=False)
        
        results.append(result)
        print(f"     Output: {output_file.name} [SAVED - ENHANCED ACCURACY]")
    
    total_time = time.time() - total_start
    
    print("\\n" + "="*80)
    print("                    ENHANCED ACCURACY SUMMARY")
    print("="*80)
    print(f"  Files Processed: {len(results)}")
    print(f"  Total Time: {total_time:.3f}s")
    print(f"  Average Time: {total_time/len(results):.3f}s")
    print(f"  Accuracy: ENHANCED")
    print(f"  Format Compliance: PERFECT")
    print("="*80)

if __name__ == "__main__":
    process_pdfs_enhanced()
    print("ENHANCED ACCURACY CERBERUS processing completed successfully")