from dataclasses import dataclass
import re
import unicodedata

MARKED = re.compile(r"\{([^{}]+)\}")
# A sentence ends at a terminal punctuation mark followed by whitespace
# or the end of the text. Multiple dots/!? and closing quotation marks
# are treated as part of the same ending.
SENTENCE_END = re.compile(r"[.!?…]+[»”\"’')\]]*(?=\s|$)")
TARGET_MARKER = "\ufff0"  # temporary marker for the targeted corpus occurrence


def normalized(text: str) -> str:
    return unicodedata.normalize("NFC", text).casefold()


@dataclass(frozen=True)
class NegationExample:
    id: int
    raw_text: str
    particle: str
    group: str
    source: str

    def is_valid(self) -> bool:
        matches = [
            match for match in MARKED.finditer(self.raw_text)
            if normalized(match.group(1)) == normalized(self.particle)
        ]
        return len(matches) == 1

    def full_text(self) -> str:
        """Full corpus excerpt, with annotation braces removed."""
        return MARKED.sub(lambda match: match.group(1), self.raw_text)

    def _sentence_with_target(self, hide_particle: bool) -> str:
        """Return only the sentence containing the specifically marked particle."""
        target_original = self.particle
        found = False

        def remove_markup(match: re.Match) -> str:
            nonlocal found, target_original
            value = match.group(1)
            if not found and normalized(value) == normalized(self.particle):
                found = True
                target_original = value
                return TARGET_MARKER
            return value

        rendered = MARKED.sub(remove_markup, self.raw_text)
        if not found:
            raise ValueError(f"No target particle annotation in example {self.id}")
        target_pos = rendered.index(TARGET_MARKER)

        start, end = 0, len(rendered)
        for boundary in SENTENCE_END.finditer(rendered):
            if boundary.end() <= target_pos:
                start = boundary.end()
            else:
                end = boundary.end()
                break

        sentence = rendered[start:end].strip().lstrip("—–- ").strip()
        return sentence.replace(TARGET_MARKER, "_____" if hide_particle else target_original)

    def question_text(self) -> str:
        return self._sentence_with_target(hide_particle=True)

    def answer_text(self) -> str:
        return self._sentence_with_target(hide_particle=False)
