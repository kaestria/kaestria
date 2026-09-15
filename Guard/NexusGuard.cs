using System;
using System.IO;
using System.Text.Json;
using System.Collections.Generic;
using Nexus.FileSystem;

namespace Nexus.Guard;

public class NexusGuard
{
    private string _userDir = string.Empty;
    private GuardConfig _config = new();
    private List<string> _logs = new();

    public NexusGuard(string userDir)
    {
        _userDir = userDir;
        LoadConfig();
        LoadLogs();
    }

    private void LoadConfig()
    {
        string guardPath = Path.Combine(_userDir, "guard.json");
        
        if (File.Exists(guardPath))
        {
            try
            {
                string json = EncryptedFileHandler.ReadEncryptedFile(guardPath);
                var loaded = JsonSerializer.Deserialize<GuardConfig>(json);
                _config = loaded ?? new GuardConfig();
            }
            catch
            {
                _config = new GuardConfig();
            }
        }
        else
        {
            _config = new GuardConfig();
            SaveConfig();
        }
    }

    private void LoadLogs()
    {
        string logsPath = Path.Combine(_userDir, ".guard_logs");
        
        if (File.Exists(logsPath))
        {
            var lines = File.ReadAllLines(logsPath);
            _logs = new List<string>(lines);
        }
    }

    private void SaveConfig()
    {
        string guardPath = Path.Combine(_userDir, "guard.json");
        string json = JsonSerializer.Serialize(_config, new JsonSerializerOptions { WriteIndented = true });
        EncryptedFileHandler.WriteEncryptedFile(guardPath, json);
    }

    private void SaveLogs()
    {
        string logsPath = Path.Combine(_userDir, ".guard_logs");
        File.WriteAllLines(logsPath, _logs);
    }

    public void AddLog(string entry)
    {
        string timestamp = DateTime.Now.ToString("yyyy-MM-dd HH:mm:ss");
        _logs.Add($"[{timestamp}] {entry}");
        
        if (_logs.Count > 1000)
            _logs.RemoveRange(0, _logs.Count - 1000);
        
        SaveLogs();
    }

    public bool IsEnabled()
    {
        return _config.Enabled;
    }

    public void Toggle()
    {
        _config.Enabled = !_config.Enabled;
        SaveConfig();
    }

    public void SetBackupConfig(int maxBackups, int intervalMinutes)
    {
        _config.MaxBackups = maxBackups;
        _config.BackupIntervalMinutes = intervalMinutes;
        SaveConfig();
    }

    public GuardConfig GetConfig()
    {
        return _config;
    }

    public List<string> GetLogs()
    {
        return new List<string>(_logs);
    }

    public void CreateBackup()
    {
        if (!_config.BackupsEnabled)
            return;

        string backupsDir = Path.Combine(_userDir, ".backups");
        Directory.CreateDirectory(backupsDir);

        var backups = new DirectoryInfo(backupsDir).GetDirectories();
        
        if (backups.Length >= _config.MaxBackups)
        {
            var oldest = backups.OrderBy(d => d.CreationTime).First();
            oldest.Delete(true);
        }

        string backupName = $"backup_{DateTime.Now:yyyyMMdd_HHmmss}";
        string backupPath = Path.Combine(backupsDir, backupName);
        Directory.CreateDirectory(backupPath);

        CopyDirectoryContents(_userDir, backupPath);
        
        _config.LastBackup = DateTime.Now;
        SaveConfig();
        
        AddLog($"Backup created: {backupName}");
    }

    private void CopyDirectoryContents(string source, string destination)
    {
        var dir = new DirectoryInfo(source);
        
        foreach (var file in dir.GetFiles())
        {
            if (file.Name != "guard.json" && file.Name != ".guard_logs")
            {
                file.CopyTo(Path.Combine(destination, file.Name), true);
            }
        }

        foreach (var subDir in dir.GetDirectories())
        {
            if (!subDir.Name.StartsWith("."))
            {
                string subDest = Path.Combine(destination, subDir.Name);
                Directory.CreateDirectory(subDest);
                CopyDirectoryContents(subDir.FullName, subDest);
            }
        }
    }

    public bool ShouldBackup()
    {
        if (!_config.BackupsEnabled)
            return false;

        var timeSinceLastBackup = DateTime.Now - _config.LastBackup;
        return timeSinceLastBackup.TotalMinutes >= _config.BackupIntervalMinutes;
    }
}

public class GuardConfig
{
    public bool Enabled { get; set; } = false;
    public bool BackupsEnabled { get; set; } = true;
    public int MaxBackups { get; set; } = 5;
    public int BackupIntervalMinutes { get; set; } = 30;
    public DateTime LastBackup { get; set; } = DateTime.Now;
}
