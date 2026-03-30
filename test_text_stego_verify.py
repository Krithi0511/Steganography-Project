from text_stego import TextSteganography

def test_text_stego():
    ts = TextSteganography()
    cover = "Short"
    secret = "This is a much longer secret message!" # Much longer than cover
    
    stego = ts.hide_text(cover, secret)
    revealed = ts.reveal_text(stego)
    
    print(f"Secret: '{secret}' (len {len(secret)})")
    print(f"Revealed: '{revealed}' (len {len(revealed)})")
    
    if revealed == secret:
        print("Success!")
    else:
        print("Failure!")
        assert False, "Mismatched!"

if __name__ == "__main__":
    test_text_stego()
