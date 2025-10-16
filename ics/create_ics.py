from icalendar import Calendar, Event
import json
import argparse
from pathlib import Path
from dateutil import parser as dtparse

def parse_dt(value):
    if value is None:
        return None
    if hasattr(value, "year"):
        return value
    return dtparse.parse(value)

class MyCalendar:
    def __init__(self,ics_path: str | Path, cal_id: str, name: str = "My Calendar"):
        self.id = cal_id
        self.ics_path = Path(ics_path)
        if self.ics_path.exists():
            with self.ics_path.open('rb') as f:
                self.c = Calendar.from_ical(f.read())
        else:
            self.c = Calendar()
            self.c.add('prodid', f'-//{cal_id}//')
            self.c.add('version', '2.0')
            self.c.add('X-WR-CALNAME', name)

    def __repr__(self):
        return self.c.to_ical().decode()
    
    def _index_by_uid(self):
        """Return dict: uid (str) -> VEVENT component."""
        
        by_uid = {}
        for comp in self.c.walk("VEVENT"):
            uid = comp.get("uid")
            if uid:
                by_uid[str(uid)] = comp
        return by_uid

    def open_json(self, json_path: str | Path):
        json_path = Path(json_path)
        if not json_path.is_file():
            raise FileNotFoundError(f"JSON file '{json_path}' does not exist.")
        with json_path.open('r') as f:
            return json.load(f)


    def addEvent(self, json_path):
        json_event = self.open_json(json_path)
        for evt in json_event:
            e = Event()
            e.add("uid", evt['id'])
            e.add("summary", evt['title'])

            dtsrart = parse_dt(evt['start'])
            if not dtsrart:
                continue

            e.add("dtstart", dtsrart)

            dtend = parse_dt(evt['end'])
            if dtend:
                e.add("dtend", dtend)

            e.add("location", evt['location'])
            e.add("description", evt['description'])

            self.c.add_component(e)

    def modifyEvent(self, json_path):
        json_event = self.open_json(json_path)
        by_uid = self._index_by_uid()
        for evt in json_event:
            target = by_uid.get(evt["id"])
            if not target:
                continue
            if "title" in evt:
                target["summary"] = evt["title"]
            if "start" in evt:
                target["dtstart"] = parse_dt(evt["start"])
            if "end" in evt:
                target["dtend"] = parse_dt(evt["end"])
            if "location" in evt:
                target["location"] = evt["location"]
            if "description" in evt:
                target["description"] = evt["description"]
                       
    
    def supEvent(self, json_path):
        json_event = self.open_json(json_path)
        uids_to_del = {evt["id"] for evt in json_event}
        to_remove = []
        for comp in self.c.subcomponents:
            if comp.name == "VEVENT":
                uid = comp.get("uid")
                if uid and str(uid) in uids_to_del:
                    to_remove.append(comp)
        for comp in to_remove:
            self.c.subcomponents.remove(comp)

    def save(self):
        with self.ics_path.open('wb') as f:
            f.write(self.c.to_ical())
