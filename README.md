# ICS Calendar Event Generator

A simple Python script to create `.ics` calendar files that can be imported into any calendar application.

## Features

- Create calendar events with date, time, and timezone
- Add location and description
- Set reminders (5 minutes to 1 day before)
- Create recurring events (daily, weekly, monthly, yearly)

## Usage

1. Run the script:
   ```bash
   python ics_generator.py
   ```

2. Follow the prompts to enter:
   - Event title
   - Date and time
   - Timezone (defaults to Africa/Kampala)
   - Location (optional)
   - Description (optional)
   - Recurrence settings
   - Reminder preferences

3. The script will generate an `.ics` file that you can import into:
   - Google Calendar
   - Outlook
   - Apple Calendar
   - Any other calendar application


- No additional dependencies required

## Example

```
Event title/summary: Team Meeting
Event date (YYYY-MM-DD): 2025-07-10
Start time (HH:MM in 24-hour format): 09:00
End time (HH:MM in 24-hour format): 10:00
```

The script will create a `.ics` file ready for import into your calendar application.

## Note

Files are saved to `C:\temp\` by default. You can change this by modifying the `save_dir` variable in the `save_ics_file()` function.