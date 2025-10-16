from create_ics import MyCalendar

def main():
    cal = MyCalendar("test.ics", "test_cal", name="Test Calendar")
    cal.addEvent("test_add.json")
    cal.save()
    print(cal)
    input("Press Enter to continue...")

    cal.modifyEvent("test_modify.json")
    cal.save()
    print(cal)
    input("Press Enter to continue...")

    cal.supEvent("test_sup.json")
    cal.save()
    print(cal)
    input("Press Enter to continue...")

if __name__ == "__main__":
    main()