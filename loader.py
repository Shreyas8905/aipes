import os

class BatchLoader:
    def __init__(self, source_config="test_ppts"):
        self.source = source_config

    def fetch_files(self):
        if not os.path.exists(self.source):
            os.makedirs(self.source)
            print(f"[AIPES] Created folder '{self.source}'. Please put PDF files inside.")
            return []

        files = [f for f in os.listdir(self.source) if f.lower().endswith(".pdf")]
        processed_files = []
        
        for f in files:
            team_name = os.path.splitext(f)[0]
            full_path = os.path.join(self.source, f)
            
            processed_files.append({
                "path": full_path,
                "team_name": team_name,
                "id": f"local_{team_name}"
            })
            
        return processed_files