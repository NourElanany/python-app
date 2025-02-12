import os
import re
import heapq
from collections import defaultdict
from typing import List, Dict, Tuple, Union
from nltk.tokenize import sent_tokenize
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.cluster import KMeans
import spacy
from nltk.stem import PorterStemmer
import tkinter as tk
from tkinter import scrolledtext, messagebox

class TextSummarization:
    def __init__(self):
        try:
            self.nlp = spacy.load('en_core_web_sm')
        except OSError:
            print("Downloading spaCy model...")
            os.system("python -m spacy download en_core_web_sm")
            self.nlp = spacy.load('en_core_web_sm')
        self.tfidf_vectorizer = TfidfVectorizer(stop_words='english')
        self.stemmer = PorterStemmer()

    def clean_text(self, text: str) -> Tuple[str, str]:
        """Clean and preprocess the text."""
        text = re.sub(r'[^\w\s.,!?]', '', text)
        cleaned_text = ' '.join(text.split())
        stemmed_text = self.stem_text(cleaned_text)
        return cleaned_text, stemmed_text

    def stem_text(self, text: str) -> str:
        """Stem the words in the text."""
        words = text.split()
        stemmed_words = [self.stemmer.stem(word) for word in words]
        return ' '.join(stemmed_words)

    def score_sentences(self, original_sentences: List[str], stemmed_sentences: List[str]) -> Dict[str, float]:
        """Score sentences based on TF-IDF and structural features."""
        tfidf_matrix = self.tfidf_vectorizer.fit_transform(stemmed_sentences)
        sentence_scores = defaultdict(float)
        for i, original_sentence in enumerate(original_sentences):
            score = sum(tfidf_matrix[i, j] for j in tfidf_matrix[i].indices)
            sent_doc = self.nlp(original_sentence)
            length_factor = min(1.0, len(sent_doc) / 20.0) if len(sent_doc) < 20 else 20.0 / len(sent_doc)
            score *= length_factor
            if i < len(original_sentences) * 0.2:
                score *= 1.2
            elif i > len(original_sentences) * 0.8:
                score *= 1.1
            if sent_doc.ents:
                score *= 1.2
            if any(token.dep_ in ['nsubj', 'dobj'] for token in sent_doc):
                score *= 1.1
            sentence_scores[original_sentence] = score
        return sentence_scores

    def extract_key_points(self, original_sentences: List[str], stemmed_sentences: List[str], num_clusters: int = 5) -> List[str]:
        """Extract key points using K-means clustering."""
        num_clusters = min(num_clusters, len(original_sentences))
        if num_clusters < 1:
            return []
        tfidf_matrix = self.tfidf_vectorizer.fit_transform(stemmed_sentences)
        kmeans = KMeans(n_clusters=num_clusters, random_state=42)
        kmeans.fit(tfidf_matrix)
        labeled_sentences = [(orig, stem, label, idx) for idx, (orig, stem, label) in enumerate(
            zip(original_sentences, stemmed_sentences, kmeans.labels_))]
        key_points = []
        for cluster in range(num_clusters):
            cluster_sentences = [
                item for item in labeled_sentences if item[2] == cluster]
            if cluster_sentences:
                cluster_center = kmeans.cluster_centers_[cluster]
                distances = [np.linalg.norm(tfidf_matrix[item[3]].toarray() - cluster_center) for item in cluster_sentences]
                closest_sentence = cluster_sentences[np.argmin(distances)][0]
                sent_doc = self.nlp(closest_sentence)
                if len(sent_doc) >= 5:
                    point = re.sub(r'\s+', ' ', closest_sentence.strip('., '))
                    if len(point.split()) >= 5:
                        key_points.append((point, cluster_sentences[0][3]))
        key_points.sort(key=lambda x: x[1])
        return [point for point, _ in key_points]

    def summarize(self, text: str, num_sentences: int = 5) -> Dict[str, Union[str, List[str]]]:
        """Generate a comprehensive summary of the text."""
        cleaned_text, stemmed_text = self.clean_text(text)
        original_sentences = sent_tokenize(cleaned_text)
        stemmed_sentences = sent_tokenize(stemmed_text)
        num_sentences = min(num_sentences, len(original_sentences)) if original_sentences else 0
        sentence_scores = self.score_sentences(original_sentences, stemmed_sentences)
        summary_sentences = heapq.nlargest(num_sentences, sentence_scores.items(), key=lambda x: x[1])
        summary_sentences.sort(key=lambda x: original_sentences.index(x[0]))
        summary = ' '.join([sentence for sentence, _ in summary_sentences])
        key_points = self.extract_key_points(original_sentences, stemmed_sentences, num_clusters=min(5, len(original_sentences)))
        return {
            'summary': summary,
            'key_points': key_points,
        }

# GUI Implementation
def generate_summary():
    input_text = text_input.get("1.0", tk.END).strip()
    if not input_text:
        messagebox.showwarning("Warning", "Please enter some text to summarize.")
        return
    summarizer = TextSummarization()
    summary_data = summarizer.summarize(input_text)
    summary_output.config(state=tk.NORMAL)
    summary_output.delete("1.0", tk.END)
    summary_output.insert(tk.END, f"Summary:\n{summary_data['summary']}\n\nKey Points:\n")
    for i, point in enumerate(summary_data["key_points"], start=1):
        summary_output.insert(tk.END, f"{i}. {point}\n")
    summary_output.config(state=tk.DISABLED)

# Create the main window
root = tk.Tk()
root.title("Text Summarizer")
root.geometry("800x600")
root.configure(bg="#f4f4f9")

# Title Label
title_label = tk.Label(root, text="Text Summarizer", font=("Arial", 20, "bold"), bg="#f4f4f9", fg="#333")
title_label.pack(pady=20)

# Input Frame
input_frame = tk.Frame(root, bg="#f4f4f9")
input_frame.pack(pady=10)

text_input = scrolledtext.ScrolledText(input_frame, width=80, height=10, font=("Arial", 12), bg="white", relief=tk.SOLID, borderwidth=1)
text_input.pack(side=tk.LEFT, padx=10)

# Generate Button
generate_button = tk.Button(root, text="Generate Summary", font=("Arial", 14), command=generate_summary,
                            bg="#008CBA", fg="white", relief=tk.RAISED, activebackground="#0077b3", activeforeground="white")
generate_button.pack(pady=20)

# Output Frame
output_frame = tk.Frame(root, bg="#f4f4f9")
output_frame.pack(pady=10)

summary_output = scrolledtext.ScrolledText(output_frame, width=80, height=10, font=("Arial", 12), bg="white", relief=tk.SOLID, borderwidth=1, state=tk.DISABLED)
summary_output.pack(side=tk.LEFT, padx=10)

# Run the GUI
root.mainloop()