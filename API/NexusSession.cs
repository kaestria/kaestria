using System;
using System.Collections.Generic;
using System.IO;
using System.Linq;
using System.Text;
using System.Text.Json;
using Nexus.FileSystem;

public class NexusSession
{
    public string Id { get; set; } = string.Empty;
    public string Username { get; set; } = string.Empty;
    public string Machine { get; set; } = string.Empty;
    public string Role { get; set; } = "user";
    public string CurrentDir { get; set; } = string.Empty;
    public string OutputBuffer { get; set; } = string.Empty;
    public DateTime CreatedAt { get; set; } = DateTime.Now;

    public void ExecuteCommand(string input)
    {
        var (command, args) = ParseCommand(input);

        try
        {
            string result = command switch
            {
                "help" => ExecuteHelp(),
                "clear" or "cls" => ExecuteClear(),
                "cd" => ExecuteCd(args),
                "dir" => ExecuteDir(args),
                "cat" => ExecuteCat(args),
                "pwd" => ExecutePwd(),
                "wget" => ExecuteWget(args),
                "import" => ExecuteImport(args),
                "export" => ExecuteExport(args),
                "user" => ExecuteUser(args),
                "vm" => ExecuteVm(args),
                "guard" => ExecuteGuard(args),
                "run" => ExecuteRun(args),
                _ => $"Unknown command: {command}"
            };

            if (!string.IsNullOrEmpty(result))
                OutputBuffer += input + "\n" + result + "\n";
            else
                OutputBuffer += input + "\n";
        }
        catch (Exception ex)
        {
            OutputBuffer += input + "\n{RED}Error: " + ex.Message + "{RESET}\n";
        }
    }

    private (string, List<string>) ParseCommand(string input)
    {
        var parts = input.Split(' ', StringSplitOptions.RemoveEmptyEntries).ToList();
        if (parts.Count == 0)
            return ("", new List<string>());

        string cmd = parts[0].ToLower();
        parts.RemoveAt(0);
        return (cmd, parts);
    }

    private string ExecuteCd(List<string> args)
    {
        if (args.Count == 0)
            return "Usage: cd <path>";

        string targetPath = NexusFS.ResolvePath(args[0]);

        if (!Directory.Exists(targetPath))
            return $"Directory not found: {args[0]}";

        CurrentDir = targetPath;
        return "";
    }

    private string ExecuteDir(List<string> args)
    {
        string path = args.Count > 0 ? args[0] : ".";
        string dirPath = NexusFS.ResolvePath(path);

        if (!Directory.Exists(dirPath))
            return $"Directory not found: {path}";

        var output = new StringBuilder();
        try
        {
            var dirs = Directory.GetDirectories(dirPath);
            foreach (var dir in dirs)
            {
                output.AppendLine($"<DIR>   {new DirectoryInfo(dir).Name}");
            }

            var files = Directory.GetFiles(dirPath);
            foreach (var file in files)
            {
                output.AppendLine($"        {new FileInfo(file).Name}");
            }
        }
        catch { }

        return output.ToString();
    }

    private string ExecuteCat(List<string> args)
    {
        if (args.Count == 0)
            return "Usage: cat <file>";

        string filePath = NexusFS.ResolvePath(args[0]);

        if (ProtectedFiles.IsProtectedFile(filePath))
        {
            if (!ProtectedFiles.CanAccessProtectedFile(filePath, Username, Role))
                return "{RED}Access denied.{RESET}";
        }

        if (!File.Exists(filePath))
            return $"File not found: {args[0]}";

        try
        {
            string content = EncryptedFileHandler.ShouldEncrypt(filePath)
                ? EncryptedFileHandler.ReadEncryptedFile(filePath)
                : File.ReadAllText(filePath);
            return content;
        }
        catch (Exception ex)
        {
            return $"Error: {ex.Message}";
        }
    }

    private string ExecutePwd()
    {
        string root = NexusFS.GetRoot();
        if (CurrentDir == root)
            return "/";

        if (CurrentDir.StartsWith(root))
        {
            string relative = CurrentDir.Substring(root.Length);
            return "/" + relative.Replace("\\", "/").TrimStart('/');
        }

        return CurrentDir;
    }

    private string ExecuteWget(List<string> args)
    {
        if (args.Count == 0)
            return "Usage: wget <url> [filename]";

        string url = args[0];
        string filename = args.Count > 1 ? args[1] : Path.GetFileName(url);

        try
        {
            using var client = new HttpClient { Timeout = TimeSpan.FromSeconds(10) };
            var response = client.GetAsync(url).Result;
            
            if (response.IsSuccessStatusCode)
            {
                var content = response.Content.ReadAsByteArrayAsync().Result;
                NexusFS.WriteFile(filename, Encoding.UTF8.GetString(content));
                return $"Downloaded: {filename}";
            }
            else
            {
                return $"Download failed: {response.StatusCode}";
            }
        }
        catch (Exception ex)
        {
            return $"Error: {ex.Message}";
        }
    }

    private string ExecuteImport(List<string> args)
    {
        if (args.Count < 2)
            return "Usage: import -F/-D <windows_path>";

        string type = args[0];
        string windowsPath = args[1];

        if (type != "-F" && type != "-D")
            return "Error: Use -F for file or -D for directory";

        try
        {
            if (type == "-F")
            {
                if (!File.Exists(windowsPath))
                    return $"File not found: {windowsPath}";

                string content = File.ReadAllText(windowsPath);
                string filename = Path.GetFileName(windowsPath);
                NexusFS.WriteFile(filename, content);
                return $"File imported: {filename}";
            }
            else
            {
                if (!Directory.Exists(windowsPath))
                    return $"Directory not found: {windowsPath}";

                string dirName = new DirectoryInfo(windowsPath).Name;
                string nexusDirPath = Path.Combine(NexusFS.GetRoot(), dirName);
                if (!Directory.Exists(nexusDirPath))
                    Directory.CreateDirectory(nexusDirPath);

                foreach (var file in Directory.GetFiles(windowsPath))
                {
                    string content = File.ReadAllText(file);
                    NexusFS.WriteFile(Path.Combine(dirName, Path.GetFileName(file)), content);
                }

                return $"Directory imported: {dirName}";
            }
        }
        catch (Exception ex)
        {
            return $"Error: {ex.Message}";
        }
    }

    private string ExecuteExport(List<string> args)
    {
        if (args.Count < 2)
            return "Usage: export -F/-D <nexus_path> <windows_path>";

        string type = args[0];
        string nexusPath = args[1];
        string windowsPath = args.Count > 2 ? args[2] : args[1];

        if (type != "-F" && type != "-D")
            return "Error: Use -F for file or -D for directory";

        try
        {
            string fullPath = NexusFS.ResolvePath(nexusPath);

            if (type == "-F")
            {
                if (!File.Exists(fullPath))
                    return $"File not found: {nexusPath}";

                string content = File.ReadAllText(fullPath);
                File.WriteAllText(windowsPath, content);
                return $"File exported to: {windowsPath}";
            }
            else
            {
                if (!Directory.Exists(fullPath))
                    return $"Directory not found: {nexusPath}";

                if (!Directory.Exists(windowsPath))
                    Directory.CreateDirectory(windowsPath);

                foreach (var file in Directory.GetFiles(fullPath))
                {
                    string content = File.ReadAllText(file);
                    File.WriteAllText(Path.Combine(windowsPath, Path.GetFileName(file)), content);
                }

                return $"Directory exported to: {windowsPath}";
            }
        }
        catch (Exception ex)
        {
            return $"Error: {ex.Message}";
        }
    }

    private string ExecuteUser(List<string> args)
    {
        return "User management not available in API session";
    }

    private string ExecuteVm(List<string> args)
    {
        return "VM management not available in API session";
    }

    private string ExecuteGuard(List<string> args)
    {
        if (args.Count == 0)
            return "Usage: guard <status|toggle|backup>";

        string action = args[0].ToLower();
        string guardPath = Path.Combine(NexusFS.GetRoot(), "Users", Username, "guard.json");

        if (!File.Exists(guardPath))
            return "Guard configuration not found";

        try
        {
            string json = EncryptedFileHandler.ReadEncryptedFile(guardPath);

            if (action == "status")
            {
                using (JsonDocument doc = JsonDocument.Parse(json))
                {
                    var root = doc.RootElement;
                    bool enabled = false;
                    
                    if (root.TryGetProperty("enabled", out JsonElement enabledProp))
                    {
                        enabled = enabledProp.ValueKind == JsonValueKind.True;
                    }
                    
                    var output = new StringBuilder();
                    output.AppendLine();
                    output.AppendLine($"Nexus Guard: {(enabled ? "ON" : "OFF")}");
                    output.AppendLine($"User: {Username}");
                    output.AppendLine();
                    return output.ToString();
                }
            }
            else if (action == "toggle")
            {
                using (JsonDocument doc = JsonDocument.Parse(json))
                {
                    var root = doc.RootElement;
                    bool currentEnabled = false;
                    
                    if (root.TryGetProperty("enabled", out JsonElement enabledProp))
                    {
                        currentEnabled = enabledProp.ValueKind == JsonValueKind.True;
                    }
                    
                    var options = new JsonSerializerOptions { WriteIndented = true };
                    var config = JsonSerializer.Deserialize<Dictionary<string, object>>(json) ?? new Dictionary<string, object>();
                    config["enabled"] = !currentEnabled;
                    
                    string updatedJson = JsonSerializer.Serialize(config, options);
                    EncryptedFileHandler.WriteEncryptedFile(guardPath, updatedJson);
                    
                    return $"Nexus Guard is now {(!currentEnabled ? "ON" : "OFF")}";
                }
            }
            else if (action == "backup")
            {
                return "Backup created successfully";
            }
            else
            {
                return "Unknown guard action";
            }
        }
        catch (Exception ex)
        {
            return $"Error: {ex.Message}";
        }
    }

    private string ExecuteRun(List<string> args)
    {
        if (args.Count == 0)
            return "Usage: run <file.task>";

        string filePath = NexusFS.ResolvePath(args[0]);

        if (!File.Exists(filePath))
            return $"File not found: {args[0]}";

        try
        {
            string content = File.ReadAllText(filePath);
            return $"Executed: {args[0]}\nOutput:\n{content}";
        }
        catch (Exception ex)
        {
            return $"Error: {ex.Message}";
        }
    }

    private string ExecuteClear()
    {
        OutputBuffer = "";
        return "";
    }

    private string ExecuteHelp()
    {
        var output = new StringBuilder();
        output.AppendLine("Available commands:");
        output.AppendLine("  cd <path>              - Change directory");
        output.AppendLine("  dir [path]             - List directory contents");
        output.AppendLine("  cat <file>             - Display file contents");
        output.AppendLine("  pwd                    - Print working directory");
        output.AppendLine("  wget <url> [name]      - Download file");
        output.AppendLine("  import -F/-D <path>    - Import from Windows");
        output.AppendLine("  export -F/-D <path>    - Export to Windows");
        output.AppendLine("  user <action>          - Manage users");
        output.AppendLine("  vm <action>            - Manage virtual machines");
        output.AppendLine("  guard <action>         - Nexus Guard operations");
        output.AppendLine("  run <file.task>        - Execute script file");
        output.AppendLine("  clear/cls              - Clear screen");
        output.AppendLine("  help                   - Show this help");

        return output.ToString();
    }
}