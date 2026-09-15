using System;
using System.Text;

namespace Nexus.Encryption;

public static class Decrypt
{
    public static string DecryptText(string encryptedText)
    {
        if (string.IsNullOrEmpty(encryptedText) || encryptedText.Length < 6)
            return string.Empty;

        string seedStr = encryptedText.Substring(0, 6);
        if (!int.TryParse(seedStr, out int seed))
            return string.Empty;

        string cipherText = encryptedText.Substring(6);
        StringBuilder decrypted = new StringBuilder();

        int seedValue = seed;
        
        for (int i = 0; i < cipherText.Length; i += 3)
        {
            if (i + 3 > cipherText.Length)
                break;

            seedValue = ((seedValue * 1103515245 + 12345) & 0x7fffffff);
            int xorKey = seedValue % 256;
            
            string hexPair = cipherText.Substring(i, 3);
            if (int.TryParse(hexPair, System.Globalization.NumberStyles.HexNumber, null, out int charValue))
            {
                int charCode = (int)charValue - 256;
                char decryptedChar = (char)(charCode ^ xorKey);
                decrypted.Append(decryptedChar);
            }
        }

        return decrypted.ToString();
    }
}