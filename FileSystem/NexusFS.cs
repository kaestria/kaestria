using System;
using System.IO;
using System.Collections.Generic;

namespace Nexus.FileSystem;

public static class NexusFS
{
    private static string _root = string.Empty;
    private static string _currentDir = string.Empty;

    public static void SetRoot(string machinePath)
    {
        _root = machinePath;
        _currentDir = machinePath;
    }

    public static string GetRoot()
    {
        return _root;
    }

    public static string GetCurrentDir()
    {
        return _currentDir;
    }

    public static void ChangeDirectory(string path)
    {
        string targetPath = ResolvePath(path);
        
        if (!Directory.Exists(targetPath))
        {
            throw new DirectoryNotFoundException($"Directory not found: {path}");
        }

        _currentDir = targetPath;
    }

    public static string ResolvePath(string path)
    {
        string resolved;

        if (Path.IsPathRooted(path) && path.StartsWith("/"))
        {
            resolved = Path.Combine(_root, path.TrimStart('/'));
        }
        else if (path == "..")
        {
            resolved = Directory.GetParent(_currentDir)?.FullName ?? _root;
        }
        else if (path.StartsWith("../"))
        {
            string parent = Directory.GetParent(_currentDir)?.FullName ?? _root;
            resolved = Path.Combine(parent, path.Substring(3));
        }
        else if (path.StartsWith("./"))
        {
            resolved = Path.Combine(_currentDir, path.Substring(2));
        }
        else if (path == ".")
        {
            resolved = _currentDir;
        }
        else
        {
            resolved = Path.Combine(_currentDir, path);
        }

        return Path.GetFullPath(resolved);
    }

    public static List<(string Name, bool IsDirectory)> ListDirectory(string? path = null)
    {
        string dirPath = path == null ? _currentDir : ResolvePath(path);
        
        if (!Directory.Exists(dirPath))
        {
            throw new DirectoryNotFoundException($"Directory not found: {path}");
        }

        var items = new List<(string, bool)>();
        
        try
        {
            var dirs = Directory.GetDirectories(dirPath);
            foreach (var dir in dirs)
            {
                items.Add((new DirectoryInfo(dir).Name, true));
            }

            var files = Directory.GetFiles(dirPath);
            foreach (var file in files)
            {
                items.Add((new FileInfo(file).Name, false));
            }
        }
        catch { }

        return items;
    }

    public static string ReadFile(string path)
    {
        string filePath = ResolvePath(path);
        
        if (!File.Exists(filePath))
        {
            throw new FileNotFoundException($"File not found: {path}");
        }

        return File.ReadAllText(filePath);
    }

    public static void WriteFile(string path, string content)
    {
        string filePath = ResolvePath(path);
        string? dir = Path.GetDirectoryName(filePath);
        
        if (dir != null && !Directory.Exists(dir))
        {
            Directory.CreateDirectory(dir);
        }

        File.WriteAllText(filePath, content);
    }

    public static void CreateDirectory(string path)
    {
        string dirPath = ResolvePath(path);
        
        if (!Directory.Exists(dirPath))
        {
            Directory.CreateDirectory(dirPath);
        }
    }

    public static void DeleteFile(string path)
    {
        string filePath = ResolvePath(path);
        
        if (!File.Exists(filePath))
        {
            throw new FileNotFoundException($"File not found: {path}");
        }

        File.Delete(filePath);
    }

    public static void DeleteDirectory(string path)
    {
        string dirPath = ResolvePath(path);
        
        if (!Directory.Exists(dirPath))
        {
            throw new DirectoryNotFoundException($"Directory not found: {path}");
        }

        Directory.Delete(dirPath, true);
    }

    public static bool FileExists(string path)
    {
        try
        {
            string filePath = ResolvePath(path);
            return File.Exists(filePath);
        }
        catch
        {
            return false;
        }
    }

    public static bool DirectoryExists(string path)
    {
        try
        {
            string dirPath = ResolvePath(path);
            return Directory.Exists(dirPath);
        }
        catch
        {
            return false;
        }
    }

    public static string FormatPath(string fullPath)
    {
        if (fullPath == _root)
            return "/";
        
        if (fullPath.StartsWith(_root))
        {
            string relative = fullPath.Substring(_root.Length);
            return "/" + relative.Replace("\\", "/").TrimStart('/');
        }

        return fullPath;
    }

    public static List<string> GetAutocompleteCandidates(string partial)
    {
        var candidates = new List<string>();
        string basePath = _currentDir;
        string fileName = partial;

        if (partial.Contains("/") || partial.Contains("\\"))
        {
            string dirPath = Path.GetDirectoryName(partial) ?? "";
            fileName = Path.GetFileName(partial);
            
            if (!string.IsNullOrEmpty(dirPath))
            {
                basePath = ResolvePath(dirPath);
            }
        }

        try
        {
            if (Directory.Exists(basePath))
            {
                var items = ListDirectory(basePath);
                foreach (var item in items)
                {
                    if (item.Name.StartsWith(fileName, StringComparison.OrdinalIgnoreCase))
                    {
                        string suffix = item.IsDirectory ? "/" : "";
                        candidates.Add(item.Name + suffix);
                    }
                }
            }
        }
        catch { }

        return candidates;
    }
}
