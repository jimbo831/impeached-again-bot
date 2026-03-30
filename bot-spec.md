# Impeached Again Bot — Spec

## Trigger Mechanism
- Keyword detection: case-insensitive regex matching `impeach\w*\s+(\w+\s+){0,3}again` in any message
- Slash command: `/impeach`
- Both increment the counter and respond with a random response from the main pool
- **The bot must ignore its own messages to prevent self-triggering**

## Slash Commands
- `/impeach` — increments the counter, responds with a random response from the main pool (same behavior as keyword detection)
- `/impeachments` — displays the current count using the count check response (no increment)

## Storage
- Counter persists in a JSON file across restarts
- Write atomically (write to temp file, then rename) to prevent corruption on crash

## Ordinal Formatting
All responses using `{count}th` must use properly formatted ordinal suffixes:
- 11, 12, 13 always use "th" (exception cases)
- Numbers ending in 1 → "st"
- Numbers ending in 2 → "nd"
- Numbers ending in 3 → "rd"
- All others → "th"

## Main Response Pool
Used by both keyword detection and `/impeach`. One response is chosen at random each time.

1. "Trump has been impeached again! That's {count} times and counting."
2. "{count} impeachments and counting. Possibly the most in history. Nobody knows."
3. "Another day, another impeachment. Count: {count}"
4. "Madam Speaker, we got him. Again. (#{count})"
5. "Article I, Article II, Article {count}. Impeached. Again."
6. "WITCH HUNT! HOAX! ...Impeachment #{count}."
7. "You're ~~fired~~ impeached. Again. (#{count})"
8. "Many people are saying this is the greatest impeachment. Maybe ever. The {count}th."
9. "This is it. This is definitely the one. He can't survive this. ...Impeachment #{count}."
10. "Please, please. It's too much impeaching. We can't take it anymore, it's too much.\nNo it isn't. We have to keep impeaching. We have to impeach {count} more times!"
11. "It was a perfect impeachment. The most perfect. READ THE TRANSCRIPT. (#{count})"
12. "A big, strong man came up to me — tough guy, you wouldn't believe it — tears in his eyes. He said, 'Sir, this is the {count}th impeachment.' I said, 'I know. Aren't they beautiful?'"
13. "Just got word that the Radical Left has done it AGAIN. That's {count} Total Impeachments, each one more PERFECT and BEAUTIFUL than the last. SAD!!!"

## Count Check Response
Used by `/impeachments`. Does not increment the counter.

"THE FAKE NEWS MEDIA won't tell you this, but the Total Impeachment Count is now {count}. WITCH HUNT!!! Thank you for your attention to this matter!"

## Admin Commands
- A reset/manual adjustment command must be restricted to a specific Discord user ID (to be provided)
- Role-based permission checks are not appropriate — the owner is a regular user with no special roles
