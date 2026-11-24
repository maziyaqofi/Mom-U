import re
import string

def tokenize_pregnancy_text(text: str) -> list[str]:
    """
    Membersihkan teks dan melakukan tokenisasi untuk dokumen & kueri kehamilan.
    Mempertahankan istilah trimester/minggu kehamilan.
    """
    if not text:
        return []
    
    text = text.lower()
    text = text.translate(str.maketrans("", "", string.punctuation))
    tokens = text.split()
    
    stopwords = {
        "dan", "yang", "di", "ke", "dari", "ini", "itu", "pada", 
        "untuk", "dengan", "adalah", "atau", "saat", "ketika", "bagi",
        "the", "and", "of", "to", "in", "for", "with", "on", "is", "are"
    }
    
    # Pertahankan angka 1, 2, 3 jika berkaitan dengan trimester, atau token > 1 huruf
    cleaned = [t for t in tokens if t not in stopwords and (len(t) > 1 or t in {"1", "2", "3"})]
    return cleaned

if __name__ == "__main__":
    contoh = "Pemeriksaan USG 12-week scan pada trimester 1 kehamilan"
    print("Input :", contoh)
    print("Tokens:", tokenize_pregnancy_text(contoh))