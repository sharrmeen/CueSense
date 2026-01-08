from sentence_transformers import SentenceTransformer, util
import torch

class SmartPlanner:
    def __init__(self):
        self.model = SentenceTransformer('all-MiniLM-L6-v2') 
        self.min_confidence = 0.75  #minimum confidence
        self.refractory_period = 5.0 #gap time

    def generate_plan(self, transcript, broll_library):
        plan = []
        last_insertion_end = -self.refractory_period

        #Process transcript segments
        for segment in transcript:
            start = segment['start']
            
            # Pacing Check
            if start < (last_insertion_end + self.refractory_period):
                continue

            # Semantic Matching
            best_match = self._find_best_broll(segment['text'], broll_library)
            
            if best_match and best_match['score'] >= self.min_confidence:
                insertion = {
                    "start_sec": start,
                    "duration_sec": min(segment['end'] - start, best_match['duration']),
                    "broll_id": best_match['id'],
                    "confidence": round(best_match['score'], 2),
                    "reason": f"Matches phrase: '{segment['text']}'"
                }
                plan.append(insertion)
                last_insertion_end = insertion['start_sec'] + insertion['duration_sec']

        return plan

    def _find_best_broll(self, text, library):
        text_emb = self.model.encode(text, convert_to_tensor=True)
        best = None
        max_score = -1

        for broll in library:
            broll_emb = self.model.encode(broll['description'], convert_to_tensor=True)
            score = util.cos_sim(text_emb, broll_emb).item()
            
            if score > max_score:
                max_score = score
                best = {**broll, "score": score}
        
        return best