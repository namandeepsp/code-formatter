import re
from typing import Optional


class LanguageDetector:
    PATTERNS = {
        "python": [
            r"\bdef\s+\w+\s*\(",
            r"\bclass\s+\w+",
            r"\bimport\s+\w+",
            r"\bfrom\s+\w+\s+import",
            r"print\s*\(",
            r":\s*$",
        ],
        "go": [
            r"\bpackage\s+\w+",
            r"\bfunc\s+\w+\s*\(",
            r"\bimport\s+",
            r":=",
            r"\bgo\s+\w+\(",
            r"\bfmt\.",
        ],
        "javascript": [
            r"\bfunction\s+\w+\s*\(",
            r"\bconst\s+\w+\s*=",
            r"\blet\s+\w+\s*=",
            r"\bvar\s+\w+\s*=",
            r"=>\s*{",
            r"console\.log\(",
        ],
        "java": [
            r"\bpublic\s+class\s+\w+",
            r"\bprivate\s+\w+\s+\w+",
            r"\bSystem\.out\.println",
            r"\bpublic\s+static\s+void\s+main",
        ],
    }

    def detect(self, code: str) -> Optional[str]:
        scores = {lang: 0 for lang in self.PATTERNS}
        
        for lang, patterns in self.PATTERNS.items():
            for pattern in patterns:
                if re.search(pattern, code, re.MULTILINE):
                    scores[lang] += 1
        
        max_score = max(scores.values())
        if max_score == 0:
            return None
        
        detected_lang = max(scores, key=scores.get)
        return detected_lang
