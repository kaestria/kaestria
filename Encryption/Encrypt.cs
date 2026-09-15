using System;
using System.Text;

namespace Nexus.Encryption;

public static class Encrypt
{
    private static readonly int PASSWORD_SEED = 0;
    
    public static string EncryptText(string plainText, int? seed = null)
    {
        if (string.IsNullOrEmpty(plainText))
            return string.Empty;

        int seedValue = seed ?? PASSWORD_SEED;
        
        StringBuilder encrypted = new StringBuilder();
        encrypted.Append(seedValue.ToString("D6"));

        foreach (char c in plainText)
        {
            seedValue = ((seedValue * 1103515245 + 12345) & 0x7fffffff);
            int xorKey = seedValue % 256;
            char encryptedChar = (char)(c ^ xorKey);
            int charCode = (int)encryptedChar + 256;
            encrypted.Append(charCode.ToString("X3"));
        }

        return encrypted.ToString();
    }
}