"""Response templates for the bot.

Placeholders:
- {count}: the impeachment count, e.g. 12
- {ordinal}: the count as an ordinal, e.g. 12th
- {age}: Trump's current age, calculated from his birthday
- {approval}: live approval rating (number only, e.g. 38)
- {gas_price}: live national average gas price (number only, e.g. 3.12)

A response that needs a live value is skipped until that value is available.

Formatting:
- \n is a line break in the Discord message.
- Discord markdown (||spoiler||, ~~strikethrough~~, **bold**) is intentional;
  it is sent as-is, not escaped.
"""

RESPONSES = [
    "{count} impeachments and counting. Possibly the most in history. Nobody knows.",
    "Madam Speaker, we got him. Again. (#{count})",
    "You're ~~fired~~ impeached. Again. (#{count})",
    "Many people are saying this is the greatest impeachment. Maybe ever. The {ordinal}.",
    "This is it. This is definitely the one. He can't survive this. ...Impeachment #{count}.",
    "Please, please. It's too much impeaching. We can't take it anymore, it's too much.\nNo it isn't. We have to keep impeaching. We have to impeach {count} more times!",
    "It was a perfect impeachment. The most perfect. READ THE TRANSCRIPT. (#{count})",
    "A big, strong man came up to me — tough guy, you wouldn't believe it — tears in his eyes. He said, 'Sir, this is the {ordinal} impeachment.' I said, 'I know. Aren't they beautiful?'",
    "Just got word that the Radical Left has done it AGAIN. That's {count} Total Impeachments, each one more PERFECT and BEAUTIFUL than the last. SAD!!!",
    "I wasn't on the Ballot and if I was, I would NOT have been impeached! That's {count} times. Thank you for your attention to this matter!",
    "Tuesday will be Impeachment Day, and Crash Out Day, all wrapped up in one. There will be nothing like it!!! (#{count})",
    "A whole Presidency will be impeached tonight, never to be brought back again. I don't want that to happen, but it probably will. (#{count})",
    "Read the ||fuckin'|| Articles, you crazy ||bastards||, or you'll be living in Hell — JUST WATCH! Impeachment #{count}.",
    "Does anybody really believe that Impeachment #{count} was honest? How could the Polls be so wrong??? It's all about the machines!",
    "If I wasn't in the White House, Leo wouldn't be in the Vatican, and Impeachment #{count} wouldn't be in the House. You're welcome!",
    "Impeachment #{count} is WEAK on Crime and terrible for Foreign Policy. I'm not a fan of Impeachment #{count}.",
    "I'd love to stop getting impeached, but the law is very strong. (#{count})",
    "I'm not asleep. I just close my eyes. It's very relaxing to me.\n...Wait, what number are we on? Oh. {count}.",
    "I'm going to become a Political Pundit, both good and bad, on the reasons for Impeachment #{count}!\nReason #1: I wasn't on the Ballot.\nReason #2: Fox News.\nReason #3: also Fox News.",
    "BREAKING: Political Pundit Donald J. Trump has completed his analysis of Impeachment #{count}. Conclusion: it was somebody else's fault.",
    "These SLEAZEBAGS should go to jail for Impeachment #{count}! By copy of this statement, I am ordering the Department of Justice to look into this criminal act, immediately!",
    "Attorney General Todd Blanche won't rule out prosecuting Democrats for Impeachment #{count}. Democrats have been told to lawyer up.",
    "Trump has given Congress 48 hours to stop impeaching him.\n...5 more days.\n...10 more days, per Congressional request.\n...Impeachment #{count}. 🌮",
    "At the request of Pakistan, Impeachment #{count} has been extended indefinitely. It is still happening.",
    "🧢 **VETO** 🧢\nTrump has attempted to veto Impeachment #{count}. Aides gently explained that's not how it works. He put the hat on anyway.",
    "Hakeem Jeffries on Impeachment #{count}: 'We haven't ruled anything in, and we haven't ruled anything out.' He then voted present.",
    "Jeffries is a 'hard yes' on impeaching Hegseth. On Impeachment #{count}, he's a firm 'present.'",
    "Chuck Schumer has five words for Impeachment #{count}: 'Relief is on the way.' It is not.",
    "Rep. Steve Cohen called him 'the most impeachable president' in history. Our records confirm it: {count} and counting.",
    "Thomas Massie was the only Republican to vote for Impeachment #{count}. As usual.",
    "New Chief of Staff Stephen Miller has reviewed Impeachment #{count} and is attempting to deport it.",
    "Approval rating: {approval}% and falling. Impeachments: {count} and rising.",
    "Gas is ${gas_price} a gallon, but impeachment is still free. Fill 'er up: #{count}.",
    "🚨 BREAKING: The President has been impeached for the {ordinal} time. He is blaming Fox News. Fox News is blaming the impeachment.",
    "Impeachment #{count} has been covered in gold leaf and hung above the Oval Office fireplace. White House: 'The gold is of the highest quality.'",
    "By Executive Order, Impeachment #{count} is hereby declared a National Monument.",
    "The East Wing was torn down to make room for Impeachment #{count}. Trump: 'That's music to my ears.'",
    "A federal judge has ordered Trump's name removed from Impeachment #{count}. Crews are prying off the letters now.\n||It didn't work. It's still #{count}.||",
    "LIVE from the South Lawn, it's UFC IMPEACHMENT {count}! 🥊\nIn the red corner: the President, age {age}.\nIn the blue corner: Chuck Schumer, who has already tapped out.",
    "FIFA has awarded Trump its Peace Prize for ending Impeachment #{count}. It did not end.",
    "María Corina Machado gave him her Nobel Peace Prize. Congress gave him Impeachment #{count}.\n||A medal can change owners, but the title of Most Impeached President cannot.||",
    "Trump has posted an AI image of himself healing Impeachment #{count}. He says he thought it was a picture of a doctor.",
    "Pope Leo XIV has blessed Impeachment #{count}. Trump says he's 'not a fan of Pope Leo.'",
    "Trump holds up Impeachment #{count} for the cameras like a jar of royal honey. 🍯",
    "Impeachment #{count} has been released in full: ||██████ ████ ██ ███████ ███||",
    "\"I didn't see it myself, but I was told by some very important people that Impeachment #{count} absolves me.\"",
    "The DOJ has quietly taken down Impeachment #{count} with no explanation. It's still #{count}.",
    "Trump demands the country \"get onto something else.\" OK: Impeachment #{count}.",
    "I won Impeachment #{count} with very little time to practice, because I'm focused on many other things. It's called TALENT, and I have it, and they don't!",
    "Trump: {count} impeachments. Every other president combined: 2. It's called TALENT, and I have it, and they don't!",
]

# Used by /impeachments. Does not increment the counter.
COUNT_RESPONSE = "THE FAKE NEWS MEDIA won't tell you this, but the Total Impeachment Count is now {count}. WITCH HUNT!!! Thank you for your attention to this matter!"
