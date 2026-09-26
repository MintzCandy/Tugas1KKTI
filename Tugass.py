import string
import itertools
from collections import Counter

ALPHABET = string.ascii_uppercase

FREQ_ID = {
    'A': 17.0, 'B': 1.8, 'C': 1.4, 'D': 4.0, 'E': 9.5, 'F': 0.2, 'G': 2.0,
    'H': 2.5, 'I': 9.5, 'J': 0.2, 'K': 6.0, 'L': 3.5, 'M': 3.0, 'N': 7.5,
    'O': 1.5, 'P': 2.8, 'Q': 0.05, 'R': 4.5, 'S': 6.0, 'T': 4.5, 'U': 3.5,
    'V': 0.1, 'W': 0.5, 'X': 0.02, 'Y': 1.2, 'Z': 0.05,
}


def only_letters(text):
    return [c for c in text.upper() if c.isalpha()]


def chi_squared(letters, expected_freq=FREQ_ID):
    """Skor chi-squared antara distribusi huruf `letters` dan frekuensi
    bahasa acuan. Semakin kecil skor, semakin mirip teks bahasa alami."""
    n = len(letters)
    if n == 0:
        return float("inf")
    counts = Counter(letters)
    score = 0.0
    for letter, pct in expected_freq.items():
        observed = counts.get(letter, 0)
        expected = pct / 100 * n
        if expected > 0:
            score += (observed - expected) ** 2 / expected
    return score


# CAESAR


CAESAR_CIPHERTEXT = (
    "XJYNFU MZWZK IFQFR UJXFS NSN YJQFM INLJXJW "
    "XJGFSDFP PZSHN WFMFXNF"
)


def caesar_decrypt(ciphertext, shift):
    result = []
    for ch in ciphertext:
        if ch.isalpha():
            idx = (ALPHABET.index(ch.upper()) - shift) % 26
            result.append(ALPHABET[idx])
        else:
            result.append(ch)
    return "".join(result)


def brute_force_caesar(ciphertext):
    """Coba seluruh 26 kemungkinan geseran, urutkan berdasarkan
    skor chi-squared (yang paling kecil = paling mirip Bahasa Indonesia)."""
    hasil = []
    for shift in range(26):
        plaintext = caesar_decrypt(ciphertext, shift)
        score = chi_squared(only_letters(plaintext))
        hasil.append((score, shift, plaintext))
    hasil.sort()
    return hasil


def solve_caesar():
    print("=" * 70)
    print("CAESAR CIPHER")
    print("=" * 70)
    print("Ciphertext:", CAESAR_CIPHERTEXT)
    print()

    hasil = brute_force_caesar(CAESAR_CIPHERTEXT)
    print("Analisis frekuensi (5 kandidat geseran terbaik):")
    for score, shift, plaintext in hasil[:5]:
        print(f"  geseran={shift:2d}  chi2={score:8.2f}  {plaintext}")

    best_score, best_shift, best_plaintext = hasil[0]
    print()
    print("Kunci geser yang ditemukan :", best_shift)
    print("Plaintext                  :", best_plaintext)
    return best_shift, best_plaintext



# VIGENERE


VIGENERE_CIPHERTEXT = (
    "ZEKIFZM WXNBMFAGXSF DVVYFAXPR MNGJO EEATFSK "
    "CPRBAAV OMNPX ZAGRCIJE"
)

VIGENERE_CRIB_WORDS = [
    "KASISKI", "EXAMINATION", "DIGUNAKAN", "MENEBAK", "PANJANG", "VIGENERE"
]


def index_of_coincidence(letters):
    n = len(letters)
    if n <= 1:
        return 0.0
    counts = Counter(letters)
    total = sum(f * (f - 1) for f in counts.values())
    return total / (n * (n - 1))


def guess_key_length(letters, max_len=10):
    """Kasiski/IC test: panjang kunci dengan rata-rata IC tertinggi
    (mendekati IC bahasa alami ~0.065-0.070) adalah kandidat terbaik."""
    scores = []
    for key_len in range(1, max_len + 1):
        groups = [letters[i::key_len] for i in range(key_len)]
        avg_ic = sum(index_of_coincidence(g) for g in groups) / key_len
        scores.append((key_len, avg_ic))
    return scores


def vigenere_decrypt(ciphertext, key):
    result = []
    ki = 0
    for ch in ciphertext:
        if ch.isalpha():
            shift = ALPHABET.index(key[ki % len(key)].upper())
            idx = (ALPHABET.index(ch.upper()) - shift) % 26
            result.append(ALPHABET[idx])
            ki += 1
        else:
            result.append(ch)
    return "".join(result)


def find_vigenere_key(ciphertext, key_len, top_k=10, crib_words=VIGENERE_CRIB_WORDS):
    """Cari kandidat huruf kunci tiap kolom dengan chi-squared, lalu
    verifikasi kombinasi mana yang benar-benar menghasilkan kalimat
    bermakna (dicek lewat kemunculan istilah khas kriptografi)."""
    letters = only_letters(ciphertext)
    columns = [letters[i::key_len] for i in range(key_len)]

    candidates_per_col = []
    for col in columns:
        ranked = sorted(range(26), key=lambda s: chi_squared(
            [ALPHABET[(ALPHABET.index(c) - s) % 26] for c in col]
        ))
        candidates_per_col.append(ranked[:top_k])

    kandidat_valid = []
    for combo in itertools.product(*candidates_per_col):
        key = "".join(ALPHABET[s] for s in combo)
        plaintext = vigenere_decrypt(ciphertext, key)
        hits = sum(1 for w in crib_words if w in plaintext)
        if hits > 0:
            kandidat_valid.append((hits, key, plaintext))

    kandidat_valid.sort(reverse=True)
    return kandidat_valid


def solve_vigenere():
    print()
    print("=" * 70)
    print("BAGIAN 2 - VIGENERE CIPHER")
    print("=" * 70)
    print("Ciphertext:", VIGENERE_CIPHERTEXT)
    print()

    letters = only_letters(VIGENERE_CIPHERTEXT)
    ic_scores = guess_key_length(letters)
    print("Index of Coincidence per kemungkinan panjang kunci:")
    for key_len, ic in ic_scores:
        print(f"  panjang={key_len:2d}  IC={ic:.4f}")
    print("  (petunjuk soal: panjang kunci = 5)")
    print()

    KEY_LEN = 5
    kandidat = find_vigenere_key(VIGENERE_CIPHERTEXT, KEY_LEN)
    print(f"Kombinasi kunci yang cocok dengan istilah kriptografi: {len(kandidat)}")
    for hits, key, plaintext in kandidat[:3]:
        print(f"  key={key}  cocok {hits}/{len(VIGENERE_CRIB_WORDS)} istilah  -> {plaintext}")

    best_key = kandidat[0][1]
    best_plaintext = kandidat[0][2]
    print()
    print("Kata kunci yang ditemukan :", best_key)
    print("Plaintext                :", best_plaintext)
    return best_key, best_plaintext



# ENIGMA


ROTOR_WIRINGS = {
    "I":   "EKMFLGDQVZNTOWYHXUSPAIBRCJ",
    "II":  "AJDKSIRUXBLHWTMCQGZNPYFVOE",
    "III": "BDFHJLCPRTXVZNYEIWGAKMUSQO",
}

ROTOR_NOTCHES = {
    "I": "Q",
    "II": "E",
    "III": "V",
}

REFLECTOR_B = "YRUHQSLDPXNGOKMIEBFZCWVJAT"

ENIGMA_CIPHERTEXT = "CKBTXMURUFTIFRMFPYTLGXEOQIYMMMFZBOJJKKRSL"


class Enigma:
    """Simulasi mesin Enigma (rotor I/II/III, reflector B).

    rotor_order, ring_settings, positions : list [kiri, tengah, kanan]
    plugboard : dict pasangan huruf, mis. {"P": "U", "U": "P", ...}
    """

    def __init__(self, rotor_order, ring_settings, positions, plugboard):
        self.rotor_order = rotor_order
        self.ring = [ALPHABET.index(r) for r in ring_settings]
        self.position = [ALPHABET.index(p) for p in positions]
        self.plugboard = dict(plugboard)

    def plugboard_swap(self, char):
        return self.plugboard.get(char, char)

    def _step_rotors(self):
        left, middle, right = self.position
        rotor_left, rotor_middle, rotor_right = self.rotor_order

        middle_at_notch = ALPHABET[middle] == ROTOR_NOTCHES[rotor_middle]
        right_at_notch = ALPHABET[right] == ROTOR_NOTCHES[rotor_right]

        if middle_at_notch:
            left = (left + 1) % 26
        if middle_at_notch or right_at_notch:
            middle = (middle + 1) % 26
        right = (right + 1) % 26

        self.position = [left, middle, right]

    def _rotor_forward(self, x, rotor, position, ring):
        wiring = ROTOR_WIRINGS[rotor]
        shifted = (x + position - ring) % 26
        output = ALPHABET.index(wiring[shifted])
        return (output - position + ring) % 26

    def _rotor_backward(self, x, rotor, position, ring):
        wiring = ROTOR_WIRINGS[rotor]
        shifted = (x + position - ring) % 26
        output = wiring.index(ALPHABET[shifted])
        return (output - position + ring) % 26

    def process_char(self, char):
        self._step_rotors()

        x = ALPHABET.index(self.plugboard_swap(char))

        # rotor kanan -> tengah -> kiri
        for i in (2, 1, 0):
            x = self._rotor_forward(
                x, self.rotor_order[i], self.position[i], self.ring[i]
            )

        
        x = ALPHABET.index(REFLECTOR_B[x])

       
        for i in (0, 1, 2):
            x = self._rotor_backward(
                x, self.rotor_order[i], self.position[i], self.ring[i]
            )

        return self.plugboard_swap(ALPHABET[x])

    def process(self, text):
        return "".join(
            self.process_char(ch) for ch in text.upper() if ch in ALPHABET
        )


def solve_enigma():
    print()
    print("=" * 70)
    print("ENIGMA MACHINE")
    print("=" * 70)

  
    rotor_order = ["II", "III", "I"]        # kiri, tengah, kanan
    ring_settings = ["H", "R", "E"]         # kiri, tengah, kanan
    positions = ["R", "F", "J"]             # kiri, tengah, kanan
    plugboard = {"P": "U", "U": "P", "T": "Z", "Z": "T"}

    enigma = Enigma(rotor_order, ring_settings, positions, plugboard)
    plaintext = enigma.process(ENIGMA_CIPHERTEXT)

    print("Ciphertext :", ENIGMA_CIPHERTEXT)
    print("Plaintext  :", plaintext)
    return plaintext



##MAIN


if __name__ == "__main__":
    _, caesar_plaintext = solve_caesar()
    _, vigenere_plaintext = solve_vigenere()
    enigma_plaintext = solve_enigma()

    print()
    print("=" * 70)
    print("RINGKASAN HASIL AKHIR")
    print("=" * 70)
    print("Caesar   :", caesar_plaintext)
    print("Vigenere :", vigenere_plaintext)
    print("Enigma   :", enigma_plaintext)
