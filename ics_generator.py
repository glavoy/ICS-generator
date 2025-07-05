#!/usr/bin/env python3
"""
ICS Calendar Event Generator
Creates .ics files for importing into calendar applications
"""

import os
import uuid
from datetime import datetime, timedelta
import re

def get_user_input():
    """Get event details from user input"""
    print("=== ICS Calendar Event Generator ===\n")
    
    # Event summary
    summary = input("Event title/summary: ").strip()
    if not summary:
        summary = "New Event"
    
    # Date input
    while True:
        date_str = input("Event date (YYYY-MM-DD): ").strip()
        try:
            event_date = datetime.strptime(date_str, "%Y-%m-%d")
            break
        except ValueError:
            print("Invalid date format. Please use YYYY-MM-DD (e.g., 2025-10-20)")
    
    # Start time
    while True:
        start_time_str = input("Start time (HH:MM in 24-hour format): ").strip()
        try:
            start_time = datetime.strptime(start_time_str, "%H:%M").time()
            break
        except ValueError:
            print("Invalid time format. Please use HH:MM (e.g., 09:00)")
    
    # End time (default to 1 hour after start time)
    default_end_datetime = datetime.combine(event_date, start_time) + timedelta(hours=1)
    default_end_time = default_end_datetime.time()
    default_end_str = default_end_time.strftime("%H:%M")
    
    while True:
        end_time_str = input(f"End time (HH:MM in 24-hour format) [default: {default_end_str}]: ").strip()
        if not end_time_str:
            end_time = default_end_time
            break
        try:
            end_time = datetime.strptime(end_time_str, "%H:%M").time()
            if end_time <= start_time:
                print("End time must be after start time.")
                continue
            break
        except ValueError:
            print("Invalid time format. Please use HH:MM (e.g., 10:00)")
    
    # Timezone
    timezone = input("Timezone (e.g., Africa/Kampala, America/New_York, Europe/London) [default: Africa/Kampala]: ").strip()
    if not timezone:
        timezone = "Africa/Kampala"
    
    # Optional location
    location = input("Event location (optional): ").strip()
    
    # Optional description
    description = input("Event description (optional): ").strip()
    
    # Repeating/Recurrence options
    print("\nRepeating options:")
    print("1. No repeat (single event)")
    print("2. Daily")
    print("3. Weekly")
    print("4. Monthly")
    print("5. Yearly")
    
    while True:
        repeat_choice = input("Select repeat option [default: 1 - No repeat]: ").strip()
        if not repeat_choice:
            repeat_choice = "1"
        
        if repeat_choice in ["1", "2", "3", "4", "5"]:
            repeat_options = {
                "1": ("No repeat", None),
                "2": ("Daily", "DAILY"),
                "3": ("Weekly", "WEEKLY"),
                "4": ("Monthly", "MONTHLY"),
                "5": ("Yearly", "YEARLY")
            }
            
            selected_repeat = repeat_options[repeat_choice]
            has_repeat = selected_repeat[1] is not None
            repeat_freq = selected_repeat[1] if has_repeat else None
            
            print(f"Selected: {selected_repeat[0]}")
            break
        else:
            print("Please enter a number from 1 to 5.")
    
    # If repeating, ask for end date
    repeat_until = None
    if has_repeat:
        print("\nHow long should this repeat?")
        print("1. Forever")
        print("2. Until a specific date")
        print("3. For a specific number of occurrences")
        
        while True:
            until_choice = input("Select option [default: 2 - Until a specific date]: ").strip()
            if not until_choice:
                until_choice = "2"
            
            if until_choice == "1":
                repeat_until = None
                print("Selected: Repeat forever")
                break
            elif until_choice == "2":
                while True:
                    until_date_str = input("End date for repeating (YYYY-MM-DD): ").strip()
                    try:
                        until_date = datetime.strptime(until_date_str, "%Y-%m-%d")
                        if until_date <= event_date:
                            print("End date must be after the event date.")
                            continue
                        # Convert to UTC format for RRULE
                        until_datetime = datetime.combine(until_date, end_time)
                        repeat_until = until_datetime.strftime("%Y%m%dT%H%M%SZ")
                        print(f"Selected: Repeat until {until_date_str}")
                        break
                    except ValueError:
                        print("Invalid date format. Please use YYYY-MM-DD")
                break
            elif until_choice == "3":
                while True:
                    try:
                        count = int(input("Number of occurrences: ").strip())
                        if count <= 0:
                            print("Number of occurrences must be greater than 0.")
                            continue
                        repeat_until = f"COUNT={count}"
                        print(f"Selected: Repeat {count} times")
                        break
                    except ValueError:
                        print("Please enter a valid number.")
                break
            else:
                print("Please enter 1, 2, or 3.")

    # Alarm/reminder options
    print("\nReminder options:")
    print("1. 5 minutes before")
    print("2. 10 minutes before")
    print("3. 1 hour before")
    print("4. 2 hours before")
    print("5. 12 hours before")
    print("6. 1 day before")
    print("7. No reminder")
    
    while True:
        choice = input("Select reminder option [default: 1 - 5 minutes]: ").strip()
        if not choice:
            choice = "1"
        
        if choice in ["1", "2", "3", "4", "5", "6", "7"]:
            reminder_options = {
                "1": ("5 minutes", "-PT5M"),
                "2": ("10 minutes", "-PT10M"),
                "3": ("1 hour", "-PT1H"),
                "4": ("2 hours", "-PT2H"),
                "5": ("12 hours", "-PT12H"),
                "6": ("1 day", "-P1D"),
                "7": ("No reminder", None)
            }
            
            selected_reminder = reminder_options[choice]
            add_alarm = selected_reminder[1] is not None
            alarm_trigger = selected_reminder[1] if add_alarm else None
            
            print(f"Selected: {selected_reminder[0]}")
            break
        else:
            print("Please enter a number from 1 to 7.")

    return {
        'summary': summary,
        'date': event_date,
        'start_time': start_time,
        'end_time': end_time,
        'timezone': timezone,
        'location': location,
        'description': description,
        'add_alarm': add_alarm,
        'alarm_trigger': alarm_trigger,
        'has_repeat': has_repeat,
        'repeat_freq': repeat_freq,
        'repeat_until': repeat_until
    }

def generate_ics_content(event_data):
    """Generate the ICS file content"""
    
    # Combine date and time
    start_datetime = datetime.combine(event_data['date'], event_data['start_time'])
    end_datetime = datetime.combine(event_data['date'], event_data['end_time'])
    
    # Generate timestamps
    now = datetime.utcnow()
    created_stamp = now.strftime("%Y%m%dT%H%M%SZ")
    
    # Generate unique ID
    event_uid = str(uuid.uuid4())
    
    # Format datetime for ICS
    start_formatted = start_datetime.strftime("%Y%m%dT%H%M%S")
    end_formatted = end_datetime.strftime("%Y%m%dT%H%M%S")
    
    # Build ICS content
    ics_content = f"""BEGIN:VCALENDAR
PRODID:-//Custom ICS Generator//EN
VERSION:2.0
BEGIN:VTIMEZONE
TZID:{event_data['timezone']}
BEGIN:STANDARD
TZOFFSETTO:+030000
TZOFFSETFROM:+030000
TZNAME:{event_data['timezone']}
DTSTART:19700101T000000
END:STANDARD
END:VTIMEZONE
BEGIN:VEVENT
CREATED:{created_stamp}
LAST-MODIFIED:{created_stamp}
DTSTAMP:{created_stamp}
UID:{event_uid}
SUMMARY:{event_data['summary']}"""

    # Add recurrence rule if repeating
    if event_data['has_repeat']:
        rrule = f"RRULE:FREQ={event_data['repeat_freq']}"
        if event_data['repeat_until']:
            if event_data['repeat_until'].startswith('COUNT='):
                rrule += f";{event_data['repeat_until']}"
            else:
                rrule += f";UNTIL={event_data['repeat_until']}"
        ics_content += f"\n{rrule}"
    
    ics_content += f"""
DTSTART;TZID={event_data['timezone']}:{start_formatted}
DTEND;TZID={event_data['timezone']}:{end_formatted}
TRANSP:OPAQUE"""

    # Add location if provided
    if event_data['location']:
        ics_content += f"\nLOCATION:{event_data['location']}"
    
    # Add description if provided
    if event_data['description']:
        ics_content += f"\nDESCRIPTION:{event_data['description']}"
    
    # Add alarm if requested
    if event_data['add_alarm']:
        ics_content += f"""
BEGIN:VALARM
ACTION:DISPLAY
TRIGGER:{event_data['alarm_trigger']}
DESCRIPTION:Event reminder
END:VALARM"""
    
    ics_content += """
END:VEVENT
END:VCALENDAR"""
    
    return ics_content

def save_ics_file(content, filename=None):
    """Save the ICS content to a file in C:\\temp"""
    # Create C:\temp directory if it doesn't exist
    save_dir = r"C:\temp"
    os.makedirs(save_dir, exist_ok=True)
    
    if not filename:
        filename = "event.ics"
    
    # Ensure .ics extension
    if not filename.endswith('.ics'):
        filename += '.ics'
    
    # Full path
    full_path = os.path.join(save_dir, filename)
    
    try:
        with open(full_path, 'w', encoding='utf-8') as f:
            f.write(content)
        print(f"\n✓ ICS file saved as: {full_path}")
        return full_path
    except Exception as e:
        print(f"Error saving file: {e}")
        return None

def main():
    """Main program loop"""
    try:
        # Get event details from user
        event_data = get_user_input()
        
        # Generate ICS content
        ics_content = generate_ics_content(event_data)
        
        # Ask for filename
        filename = input(f"\nFilename for the ICS file [default: event.ics]: ").strip()
        if not filename:
            filename = "event.ics"
        
        # Save the file
        saved_file = save_ics_file(ics_content, filename)
        
        if saved_file:
            print(f"\nYou can now import the file into your calendar application.")
            print("The file has been saved in C:\\temp\\.")
        
        # Ask if user wants to create another event
        another = input("\nCreate another event? (y/n): ").strip().lower()
        if another == 'y':
            print("\n" + "="*50 + "\n")
            main()  # Recursive call for another event
        else:
            print("\nGoodbye!")
            
    except KeyboardInterrupt:
        print("\n\nOperation cancelled by user.")
    except Exception as e:
        print(f"\nAn error occurred: {e}")

if __name__ == "__main__":
    main()