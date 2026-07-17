import json
from datetime import datetime

class NotesViewer:
    def __init__(self):
        self.notes = {}

    def create_note(self, nid, title, content, tags=None):
        self.notes[nid] = {
            "id": nid, "title": title, "content": content,
            "tags": tags or [], "created": datetime.now().isoformat(),
            "modified": datetime.now().isoformat()
        }
        return True

    def edit_note(self, nid, content):
        if nid in self.notes:
            self.notes[nid]["content"] = content
            self.notes[nid]["modified"] = datetime.now().isoformat()
            return True
        return False

    def search_notes(self, query):
        q = query.lower()
        return [n for n in self.notes.values()
                if q in n["title"].lower() or q in n["content"].lower()]

    def get_note(self, nid):
        return self.notes.get(nid)

    def list_notes(self):
        return sorted(self.notes.values(), key=lambda x: x["modified"], reverse=True)
