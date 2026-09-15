using System;
using System.IO;
using System.Net.Http;
using System.Text;
using System.Collections.Generic;
using System.Linq;
using Nexus.FileSystem;
using Nexus.Users;
using Nexus.Guard;
using Nexus.Machine;
using Nexus.Encryption;

namespace Nexus.Terminal;

public class TerminalBase
{
    private string _currentMachine = string.Empty;
    private string _currentUser = string.Empty;
    private string _currentUserRole = string.Empty;
    private string _promptColor = "green";
    private bool _running = true;
    private NexusGuard? _guard;
    private MachineManager _machineManager = new();

    public TerminalBase(string machine)
    {
        _currentMachine = machine;
    }

    public void Run()
    {
        _currentUser = "admin";
        _currentUserRole = "admin";
        _promptColor = "green";

        string machinePath = _machineManager.GetMachinePath(_currentMachine);
        string userDir = Path.Combine(machinePath, "Users", "admin");
        
        if (!Directory.Exists(userDir))
        {
            Directory.CreateDirectory(userDir);
            UserManager.Instance.CreateUser("admin", "admin", "admin", "green");
        }

        _guard = new NexusGuard(userDir);

        Console.WriteLine("[Nexus ready. Type 'help' for available commands.]");
        Console.WriteLine();

        while (_running)
        {
            DisplayPrompt();
            string? input = Console.ReadLine();

            if (string.IsNullOrWhiteSpace(input))
                continue;

            ProcessCommand(input);
        }
    }

    private void DisplayPrompt()
    {
        ConsoleColor color = _promptColor switch
        {
            "red" => ConsoleColor.Red,
            "green" => ConsoleColor.Green,
            "blue" => ConsoleColor.Blue,
            "aqua" => ConsoleColor.Cyan,
            "yellow" => ConsoleColor.Yellow,
            "gray" => ConsoleColor.Gray,
            "white" => ConsoleColor.White,
            "purple" => ConsoleColor.Magenta,
            _ => ConsoleColor.Green
        };

        string currentDir = FormatCurrentDir();
        
        Console.ForegroundColor = color;
        Console.Write($"{_currentUser}@{_currentMachine}:{currentDir}");
        Console.ResetColor();
        Console.Write("> ");
    }

    private string FormatCurrentDir()
    {
        string root = _machineManager.GetMachinePath(_currentMachine);
        string current = NexusFS.GetCurrentDir();
        
        if (current == root)
            return "/";
        
        if (current.StartsWith(root))
        {
            return current.Substring(root.Length).Replace("\\", "/");
        }

        return current;
    }

    private void ProcessCommand(string input)
    {
        var (command, args) = CommandParser.Parse(input);

        try
        {
            if (command == "help")
                ExecuteCommand("help");
            else if (command == "clear" || command == "cls")
                Console.Clear();
            else if (command == "exit" || command == "quit")
                _running = false;
            else if (command == "cd")
                ExecuteCd(args);
            else if (command == "dir")
                ExecuteDir(args);
            else if (command == "cat")
                ExecuteCat(args);
            else if (command == "wget")
                ExecuteWget(args);
            else if (command == "import")
                ExecuteImport(args);
            else if (command == "export")
                ExecuteExport(args);
            else if (command == "user")
                ExecuteUser(args);
            else if (command == "vm")
                ExecuteVm(args);
            else if (command == "boot")
                ExecuteBoot(args);
            else if (command == "guard")
                ExecuteGuard(args);
            else if (command == "run")
                ExecuteRun(args);
            else
                Console.WriteLine($"Unknown command: {command}");
        }
        catch (Exception ex)
        {
            Console.WriteLine($"Error: {ex.Message}");
        }
    }

    private void ExecuteCommand(string command)
    {
        if (command == "help")
        {
            Console.WriteLine("Available commands:");
            Console.WriteLine("  cd <path>              - Change directory");
            Console.WriteLine("  dir [path]             - List directory contents");
            Console.WriteLine("  cat <file>             - Display file contents");
            Console.WriteLine("  wget <url> [name]      - Download file");
            Console.WriteLine("  import -F/-D <path>    - Import from Windows");
            Console.WriteLine("  export -F/-D <path>    - Export to Windows");
            Console.WriteLine("  user <action>          - Manage users");
            Console.WriteLine("  vm <action>            - Manage virtual machines");
            Console.WriteLine("  boot                   - Load and execute OS");
            Console.WriteLine("  guard <action>         - Nexus Guard operations");
            Console.WriteLine("  login                  - Login as different user");
            Console.WriteLine("  clear/cls              - Clear screen");
            Console.WriteLine("  run <file.task>        - Execute script file");
            Console.WriteLine("  help                   - Show this help");
            Console.WriteLine("  exit/quit              - Exit Nexus");
        }
    }

    private void ExecuteCd(List<string> args)
    {
        if (args.Count == 0)
        {
            string root = _machineManager.GetMachinePath(_currentMachine);
            NexusFS.ChangeDirectory(root);
            return;
        }

        NexusFS.ChangeDirectory(args[0]);
    }

    private void ExecuteDir(List<string> args)
    {
        string? path = args.Count > 0 ? args[0] : null;
        var items = NexusFS.ListDirectory(path);

        foreach (var (name, isDir) in items)
        {
            string prefix = isDir ? "<DIR>" : "";
            Console.WriteLine($"{prefix,-7} {name}");
        }
    }

    private void ExecuteCat(List<string> args)
    {
        if (args.Count == 0)
        {
            Console.WriteLine("Usage: cat <file>");
            return;
        }

        string filePath = NexusFS.ResolvePath(args[0]);

        if (ProtectedFiles.IsProtectedFile(filePath))
        {
            if (!ProtectedFiles.CanAccessProtectedFile(filePath, _currentUser, _currentUserRole))
            {
                Console.WriteLine("Access denied.");
                return;
            }
        }

        try
        {
            string content = EncryptedFileHandler.ShouldEncrypt(filePath) 
                ? EncryptedFileHandler.ReadEncryptedFile(filePath)
                : NexusFS.ReadFile(args[0]);
            Console.WriteLine(content);
        }
        catch (Exception ex)
        {
            Console.WriteLine($"Error: {ex.Message}");
        }
    }

    private void ExecuteWget(List<string> args)
    {
        if (args.Count == 0)
        {
            Console.WriteLine("Usage: wget <url> [filename]");
            return;
        }

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
                Console.WriteLine($"Downloaded: {filename}");
            }
            else
            {
                Console.WriteLine($"Download failed: {response.StatusCode}");
            }
        }
        catch (Exception ex)
        {
            Console.WriteLine($"Error: {ex.Message}");
        }
    }

    private void ExecuteImport(List<string> args)
    {
        if (args.Count < 2)
        {
            Console.WriteLine("Usage: import -F/-D <windows_path>");
            return;
        }

        string type = args[0];
        string windowsPath = args[1];
        string currentDir = NexusFS.GetCurrentDir();

        if (type == "-F" && File.Exists(windowsPath))
        {
            string filename = Path.GetFileName(windowsPath);
            File.Copy(windowsPath, Path.Combine(currentDir, filename), true);
            Console.WriteLine($"Imported: {filename}");
        }
        else if (type == "-D" && Directory.Exists(windowsPath))
        {
            string dirname = Path.GetFileName(windowsPath);
            string destPath = Path.Combine(currentDir, dirname);
            CopyWindowsDirectory(windowsPath, destPath);
            Console.WriteLine($"Imported: {dirname}");
        }
        else
        {
            Console.WriteLine("Path not found or invalid type.");
        }
    }

    private void ExecuteExport(List<string> args)
    {
        if (args.Count < 2)
        {
            Console.WriteLine("Usage: export -F/-D <vm_path>");
            return;
        }

        string type = args[0];
        string vmPath = args[1];
        string documentPath = Environment.GetFolderPath(Environment.SpecialFolder.MyDocuments);

        try
        {
            if (type == "-F" && NexusFS.FileExists(vmPath))
            {
                string content = NexusFS.ReadFile(vmPath);
                string filename = Path.GetFileName(vmPath);
                string destPath = Path.Combine(documentPath, filename);
                File.WriteAllText(destPath, content);
                Console.WriteLine($"Exported: {filename}");
            }
            else if (type == "-D" && NexusFS.DirectoryExists(vmPath))
            {
                Console.WriteLine("Directory export not yet implemented.");
            }
            else
            {
                Console.WriteLine("Path not found or invalid type.");
            }
        }
        catch (Exception ex)
        {
            Console.WriteLine($"Error: {ex.Message}");
        }
    }

    private void ExecuteUser(List<string> args)
    {
        if (args.Count == 0)
        {
            Console.WriteLine("Usage: user <new|list|delete|exists>");
            return;
        }

        string action = args[0].ToLower();

        if (action == "new")
        {
            if (_currentUserRole != "admin")
            {
                Console.WriteLine("Access denied. Only admins can create users.");
                return;
            }

            Console.Write("Username: ");
            string? newUsername = Console.ReadLine();
            Console.Write("Password: ");
            string newPassword = Console.ReadLine() ?? "";
            Console.Write("Role (admin/user): ");
            string? roleInput = Console.ReadLine();
            string role = roleInput?.ToLower() == "admin" ? "admin" : "user";

            UserManager.Instance.CreateUser(newUsername ?? "", newPassword, role);
            Console.WriteLine($"User '{newUsername}' created.");
        }
        else if (action == "list")
        {
            var users = UserManager.Instance.ListUsers();
            Console.WriteLine();
            Console.WriteLine("Username    Role     Guard");
            Console.WriteLine("────────    ────     ─────");
            
            foreach (var user in users)
            {
                string role = UserManager.Instance.GetUserRole(user);
                string guardStatus = "OFF";
                Console.WriteLine($"{user,-11} {role,-8} {guardStatus}");
            }
            Console.WriteLine();
        }
        else if (action == "delete")
        {
            if (_currentUserRole != "admin")
            {
                Console.WriteLine("Access denied. Only admins can delete users.");
                return;
            }

            Console.Write("Username to delete: ");
            string? deleteUsername = Console.ReadLine();
            Console.Write("Confirm deletion by typing username again: ");
            string? confirm = Console.ReadLine();

            if (deleteUsername == confirm)
            {
                try
                {
                    UserManager.Instance.DeleteUser(deleteUsername ?? "", "admin");
                    Console.WriteLine($"User '{deleteUsername}' deleted.");
                }
                catch
                {
                    Console.WriteLine("Deletion failed.");
                }
            }
            else
            {
                Console.WriteLine("Deletion cancelled.");
            }
        }
        else if (action == "exists")
        {
            if (args.Count < 2)
            {
                Console.WriteLine("Usage: user exists <username>");
                return;
            }

            bool exists = UserManager.Instance.UserExists(args[1]);
            Console.WriteLine(exists ? "User exists." : "User does not exist.");
        }
    }

    private void ExecuteVm(List<string> args)
    {
        if (args.Count == 0)
        {
            Console.WriteLine("Usage: vm <list|new|delete|exists>");
            return;
        }

        string action = args[0].ToLower();

        if (action == "list")
        {
            var machines = _machineManager.ListMachines();
            Console.WriteLine();
            Console.WriteLine("Boot list:");
            Console.WriteLine();
            
            for (int i = 0; i < machines.Count; i++)
            {
                string defaultLabel = machines[i] == "machine" ? " (Default)" : "";
                Console.WriteLine($"({i}) {machines[i]}{defaultLabel}");
            }
            Console.WriteLine();
        }
        else if (action == "new")
        {
            if (_currentUserRole != "admin")
            {
                Console.WriteLine("Access denied. Only admins can create VMs.");
                return;
            }

            if (args.Count < 2)
            {
                Console.WriteLine("Usage: vm new <machine_name>");
                return;
            }

            _machineManager.CreateMachine(args[1]);
            Console.WriteLine($"Machine '{args[1]}' created.");
        }
        else if (action == "delete")
        {
            if (_currentUserRole != "admin")
            {
                Console.WriteLine("Access denied. Only admins can delete VMs.");
                return;
            }

            if (args.Count < 2)
            {
                Console.WriteLine("Usage: vm delete <machine_name>");
                return;
            }

            Console.Write($"Confirm deletion by typing machine name '{args[1]}': ");
            string? confirm = Console.ReadLine();

            if (confirm == args[1])
            {
                _machineManager.DeleteMachine(args[1]);
                Console.WriteLine($"Machine '{args[1]}' deleted.");
            }
            else
            {
                Console.WriteLine("Deletion cancelled.");
            }
        }
        else if (action == "exists")
        {
            if (args.Count < 2)
            {
                Console.WriteLine("Usage: vm exists <machine_name>");
                return;
            }

            bool exists = _machineManager.MachineExists(args[1]);
            Console.WriteLine(exists ? "Machine exists." : "Machine does not exist.");
        }
    }

    private void ExecuteBoot(List<string> args)
    {
        string osPath = Path.Combine(_machineManager.GetMachinePath(_currentMachine), "OS", "os.dll");
        
        if (!File.Exists(osPath))
        {
            Console.WriteLine("Error: OS not found.");
            return;
        }

        Console.WriteLine($"Loading OS from {osPath}...");
        Console.WriteLine("Executing Program.Main()...");
        Console.WriteLine("[nexusOS GUI would start here]");
    }

    private void ExecuteGuard(List<string> args)
    {
        if (_guard == null)
            return;

        if (args.Count == 0)
        {
            Console.WriteLine("Usage: guard <status|toggle|backup>");
            return;
        }

        string action = args[0].ToLower();

        if (action == "status")
        {
            bool enabled = _guard.IsEnabled();
            var config = _guard.GetConfig();
            
            Console.WriteLine();
            Console.WriteLine($"Nexus Guard: {(enabled ? "ON" : "OFF")}");
            Console.WriteLine($"Backups: {(config.BackupsEnabled ? "ON" : "OFF")} (max: {config.MaxBackups}, interval: {config.BackupIntervalMinutes}min)");
            Console.WriteLine($"Last backup: {config.LastBackup:yyyy-MM-dd HH:mm:ss}");
            Console.WriteLine($"Log entries: {_guard.GetLogs().Count}");
            Console.WriteLine();
        }
        else if (action == "toggle")
        {
            _guard.Toggle();
            bool enabled = _guard.IsEnabled();
            Console.WriteLine($"Nexus Guard is now {(enabled ? "ON" : "OFF")}");
        }
        else if (action == "backup")
        {
            if (args.Count > 1 && args[1].ToLower() == "config")
            {
                Console.Write("Max backups: ");
                if (int.TryParse(Console.ReadLine(), out int maxBackups))
                {
                    Console.Write("Backup interval (minutes): ");
                    if (int.TryParse(Console.ReadLine(), out int interval))
                    {
                        _guard.SetBackupConfig(maxBackups, interval);
                        Console.WriteLine("Backup configuration updated.");
                    }
                }
            }
            else
            {
                _guard.CreateBackup();
                Console.WriteLine("Backup created successfully.");
            }
        }
    }

    private void ExecuteRun(List<string> args)
    {
        if (args.Count == 0)
        {
            Console.WriteLine("Usage: run <script.task>");
            return;
        }

        string scriptFile = args[0];

        if (!NexusFS.FileExists(scriptFile))
        {
            Console.WriteLine($"Script not found: {scriptFile}");
            return;
        }

        string content = NexusFS.ReadFile(scriptFile);
        var lines = CommandParser.ParseScriptLines(content);

        if (_guard?.IsEnabled() ?? false)
        {
            bool hasSensitiveCommands = lines.Any(l =>
            {
                var (cmd, _) = CommandParser.Parse(l);
                return cmd == "vm" || cmd == "user" || cmd == "guard";
            });

            if (hasSensitiveCommands)
            {
                Console.WriteLine("⚠ Nexus Guard: This script contains sensitive commands.");
                var sensitiveLines = lines.Where(l =>
                {
                    var (cmd, _) = CommandParser.Parse(l);
                    return cmd == "vm" || cmd == "user" || cmd == "guard";
                });
                
                foreach (var line in sensitiveLines)
                {
                    var (cmd, _) = CommandParser.Parse(line);
                    Console.WriteLine($"  Commands: {cmd}");
                }

                Console.Write("  Continue? (y/n): ");
                string? answer = Console.ReadLine();
                
                if (answer?.ToLower() != "y")
                {
                    Console.WriteLine("Script execution cancelled.");
                    return;
                }
            }
        }

        for (int i = 0; i < lines.Count; i++)
        {
            Console.WriteLine($"Executing line {i + 1}/{lines.Count}: {lines[i]}... OK");
            ProcessCommand(lines[i]);
        }

        Console.WriteLine("Script completed successfully.");
    }

    private void CopyWindowsDirectory(string source, string destination)
    {
        Directory.CreateDirectory(destination);
        var dir = new DirectoryInfo(source);
        
        foreach (var file in dir.GetFiles())
        {
            file.CopyTo(Path.Combine(destination, file.Name), true);
        }

        foreach (var subDir in dir.GetDirectories())
        {
            CopyWindowsDirectory(subDir.FullName, Path.Combine(destination, subDir.Name));
        }
    }
}
