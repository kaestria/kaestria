using System;
using System.IO;
using Nexus.Encryption;

namespace Nexus.FileSystem;

public static class EncryptedFileHandler
{
    private static readonly string[] ProtectedExtensions = { ".json" };
    private static readonly string[] ProtectedPaths = { "config.json", "profile.json", "guard.json" };

    public static bool ShouldEncrypt(string filePath)
    {
        string fileName = Path.GetFileName(filePath);
        
        if (ProtectedPaths.Any(p => fileName.EndsWith(p, StringComparison.OrdinalIgnoreCase)))
            return true;

        string ext = Path.GetExtension(filePath);
        if (ProtectedExtensions.Contains(ext.ToLower()))
            return true;

        return false;
    }

    public static string ReadEncryptedFile(string filePath)
    {
        if (!File.Exists(filePath))
            throw new FileNotFoundException($"File not found: {filePath}");

        string fileContent = File.ReadAllText(filePath);

        if (ShouldEncrypt(filePath))
        {
            return Decrypt.DecryptText(fileContent);
        }

        return fileContent;
    }

    public static void WriteEncryptedFile(string filePath, string content)
    {
        string? dirPath = Path.GetDirectoryName(filePath);
        if (dirPath != null && !Directory.Exists(dirPath))
        {
            Directory.CreateDirectory(dirPath);
        }

        if (ShouldEncrypt(filePath))
        {
            string encrypted = Encrypt.EncryptText(content);
            File.WriteAllText(filePath, encrypted);
        }
        else
        {
            File.WriteAllText(filePath, content);
        }
    }

    public static string? ReadEncryptedFileIfExists(string filePath)
    {
        if (!File.Exists(filePath))
            return null;

        return ReadEncryptedFile(filePath);
    }
}
