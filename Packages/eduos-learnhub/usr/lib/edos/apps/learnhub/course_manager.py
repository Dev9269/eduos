import json

class CourseManager:
    def __init__(self):
        self.courses = {}

    def add_course(self, cid, name, description, units=None):
        self.courses[cid] = {
            "id": cid, "name": name, "description": description,
            "units": units or []
        }

    def get_course(self, cid):
        return self.courses.get(cid)

    def list_courses(self):
        return list(self.courses.values())

    def add_unit(self, cid, unit_data):
        if cid in self.courses:
            self.courses[cid]["units"].append(unit_data)
            return True
        return False

    def save_to_file(self, filepath):
        with open(filepath, "w") as f:
            json.dump(self.courses, f, indent=2)

    def load_from_file(self, filepath):
        try:
            with open(filepath) as f:
                self.courses = json.load(f)
        except Exception:
            pass
