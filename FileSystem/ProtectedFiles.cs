using System;
using System.IO;

namespace Nexus.FileSystem;

public static class ProtectedFiles
{
    private static string[] GetProtectedPaths()
    {
        string root = NexusFS.GetRoot();

        return new[]
        {
            Path.Combine(root, "config.json"),
            Path.Combine(root, "Users"),
            Path.Combine(root, "OS", "Users")
        };
    }

    public static bool IsProtectedFile(string filePath)
    {
        string normalized = Path.GetFullPath(filePath);

        foreach (string protectedPath in GetProtectedPaths())
        {
            string normalizedProtected = Path.GetFullPath(protectedPath);

            if (normalized.Equals(normalizedProtected, StringComparison.OrdinalIgnoreCase))
                return true;

            string dirPrefix = normalizedProtected.TrimEnd(Path.DirectorySeparatorChar)
                               + Path.DirectorySeparatorChar;

            if (normalized.StartsWith(dirPrefix, StringComparison.OrdinalIgnoreCase))
                return true;
        }

        return false;
    }

    public static bool CanAccessProtectedFile(string filePath, string currentUser, string currentUserRole)
    {
        return false; // Nenhum usuário acessa arquivos protegidos pelo terminal
    }
}