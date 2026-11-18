"""Offline emergency safety layer: koi API/network use nahi hota."""
import re

RULES = [
    (r"chest pain|pain in (my )?chest|heart attack|seene (mein|me|main) (shadeed |shiddat se |bohat )?dard|سینے (میں )?(شدید )?درد|دل کا دورہ",
     "Chest pain / possible heart emergency"),
    (r"can'?t breathe|cannot breathe|difficulty breathing|short(ness)? of breath|saans (lene )?(mein|me|main) (takleef|dikkat|mushkil)|saans nahi aa|سانس (لینے )?(میں )?(تکلیف|دشواری)|سانس نہیں",
     "Severe breathing difficulty"),
    (r"stroke|face droop|slurred speech|sudden weakness|arm weakness|munh (tedha|terha)|zubaan (lar|latha)|چہرہ ٹیڑھا|فالج",
     "Possible stroke signs"),
    (r"unconscious|passed out|not responding|faint(ed|ing)|behosh|بے ہوش",
     "Unconsciousness"),
    (r"anaphylaxis|severe allergic|throat (is )?(closing|swelling)|swollen (tongue|throat)|gale (mein|me) soojan|شدید الرجی",
     "Severe allergic reaction"),
    (r"(heavy|severe|uncontrolled) bleeding|bleeding (won'?t|will not|does not) stop|khoon (nahi ruk|bohat beh)|خون نہیں رک",
     "Uncontrolled bleeding"),
    (r"seizure|convulsion|mirgi ka daura|دورہ پڑ",
     "Seizure"),
    (r"suicid|kill myself|want to die|end my life|khud\s?kushi|apni jaan (lena|le)|مرنا چاہتا|خودکشی",
     "Self-harm / suicide risk"),
    (r"overdose|poison(ed|ing)?|zeher|زہر",
     "Overdose / poisoning"),
]
COMPILED = [(re.compile(p, re.IGNORECASE), d) for p, d in RULES]

GUIDANCE = (
    "🚨 EMERGENCY: Abhi foran emergency services ko call karein ya qareeb-tareen "
    "hospital ke emergency department jayein. Pakistan mein Rescue 1122 (apne ilaqe "
    "mein coverage verify kar lein). Intezar na karein, aur is app mein sawalat "
    "jari na rakhein."
)
SELF_HARM_EXTRA = (
    "Agar aap khud ko nuqsan pohanchane ke khayalat rakhte hain, to abhi kisi "
    "bharose-mand shakhs ya emergency service se rabta karein; aap akele nahi hain."
)


def check_emergency(text):
    """Returns {'is_emergency': bool, 'reasons': [...], 'message': str}"""
    reasons = [d for rx, d in COMPILED if rx.search(text or "")]
    if not reasons:
        return {"is_emergency": False, "reasons": [], "message": ""}
    msg = GUIDANCE
    if "Self-harm / suicide risk" in reasons:
        msg += "\n\n" + SELF_HARM_EXTRA
    return {"is_emergency": True, "reasons": reasons, "message": msg}
