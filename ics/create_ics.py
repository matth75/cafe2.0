from ics import Calendar, Event
import json
import argparse
from pathlib import Path

class MyCalendar:
    def __init__(self, id):
        self.id = id
        self.c = Calendar(creator=id)

    def addEvent(self, json_event):
        for evt in json_event:
            e = Event()
            e.uid = evt['id']
            e.name = evt['title']
            e.begin = evt['start']
            if evt.get('end'):
                e.end = evt.get('end')
            e.location = evt['location']
            e.description = evt['description']
            self.c.events.add(e)

    def modifyEvent(self, json_event):
        by_uid = {e.uid: e for e in self.c.events}
        for evt in json_event:
            target = by_uid.get(evt["id"])
            if not target:
                continue
            if "title" in evt:
                target.name = evt["title"]
            if "start" in evt:
                target.begin = evt["start"]
            if "end" in evt:
                target.end = evt["end"]
            if "location" in evt:
                target.location = evt["location"]
            if "description" in evt:
                target.description = evt["description"]
                       
    
    def supEvent(self, json_event):
        uids_to_del = {evt["id"] for evt in json_event}
        for e in list(self.c.events):
            if e.uid in uids_to_del:
                self.c.events.discard(e)

    def save(self, path):
        with open(path, 'w') as f:
            f.writelines(self.c.serialize_iter())


def main():
    parser = argparse.ArgumentParser(description="Create or modify an ICS file from JSON data.")
    parser.add_argument("json_path", type=str, help="Path to the JSON file containing event data.")
    parser.add_argument("id", type=str, help="Calendar ID.")
    parser.add_argument("action", type=str, choices=["add", "modify", "sup"], help="Action to perform: add, modify, or sup.")
    parser.add_argument("ics_path", type=str, help="Path to the output ICS file")

    args = parser.parse_args()
    if not Path(args.json_path).is_file():
        print(f"Error: JSON file '{args.json_path}' does not exist.")
        return
    with open(args.json_path, 'r') as f:
        json_event = json.load(f)
    
    if not Path(args.ics_path).exists():
        cal = MyCalendar(args.id)
    else:
        with open(args.ics_path, 'r') as f:
            cal = MyCalendar(args.id)
            cal.c = Calendar(f.read())

    if args.action == "add":
        cal.addEvent(json_event)
    elif args.action == "modify":
        cal.modifyEvent(json_event)
    elif args.action == "sup":
        cal.supEvent(json_event)

    cal.save(args.ics_path)

        

     

if __name__ == "__main__":
    main()

