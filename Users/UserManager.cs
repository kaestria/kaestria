using System;
using System.IO;
using System.Text.Json;
using System.Collections.Generic;
using System.Linq;
using Nexus.Encryption;
using Nexus.FileSystem;

namespace Nexus.Users;

public class UserManager
{
    private static string _machinePath = string.Empty;
    private static string _usersPath = string.Empty;
    private static UserManager? _instance;
    private Dictionary<string, UserProfile> _users = new();

    private UserManager(string machinePath)
    {
        _machinePath = machinePath;
        _usersPath = Path.Combine(machinePath, "Users");
        LoadUsers();
    }

    public static void Init(string machinePath)
    {
        _instance = new UserManager(machinePath);
    }

    public static UserManager Instance
    {
        get
        {
            if (_instance == null)
                throw new InvalidOperationException("UserManager not initialized");
            return _instance;
        }
    }

    private void LoadUsers()
    {
        if (!Directory.Exists(_usersPath))
            return;

        var userDirs = Directory.GetDirectories(_usersPath);
        
        foreach (var userDir in userDirs)
        {
            var dirName = new DirectoryInfo(userDir).Name;
            var profilePath = Path.Combine(userDir, "profile.json");

            if (File.Exists(profilePath))
            {
                try
                {
                    var profile = LoadUserProfile(profilePath);
                    _users[dirName] = profile;
                }
                catch { }
            }
        }
    }

    private UserProfile LoadUserProfile(string profilePath)
    {
        string json = EncryptedFileHandler.ReadEncryptedFile(profilePath);
        var profile = JsonSerializer.Deserialize<UserProfile>(json);
        return profile ?? throw new InvalidOperationException("Invalid profile");
    }

    public UserProfile? GetUser(string username)
    {
        if (_users.TryGetValue(username, out var user))
            return user;
        return null;
    }

    public bool UserExists(string username)
    {
        return _users.ContainsKey(username);
    }

    public void CreateUser(string username, string password, string role = "user", string promptColor = "green")
    {
        if (UserExists(username))
            throw new InvalidOperationException($"User '{username}' already exists.");

        string userDir = Path.Combine(_usersPath, username);
        Directory.CreateDirectory(userDir);

        string encryptedPassword = Encrypt.EncryptText(password);

        var profile = new UserProfile
        {
            Username = username,
            Password = encryptedPassword,
            Role = role,
            PromptColor = promptColor
        };

        string profilePath = Path.Combine(userDir, "profile.json");
        string json = JsonSerializer.Serialize(profile, new JsonSerializerOptions { WriteIndented = true });
        EncryptedFileHandler.WriteEncryptedFile(profilePath, json);

        var guardConfig = new
        {
            enabled = false,
            backupsEnabled = true,
            maxBackups = 5,
            backupIntervalMinutes = 30,
            lastBackup = DateTime.Now
        };

        string guardPath = Path.Combine(userDir, "guard.json");
        string guardJson = JsonSerializer.Serialize(guardConfig, new JsonSerializerOptions { WriteIndented = true });
        EncryptedFileHandler.WriteEncryptedFile(guardPath, guardJson);

        _users[username] = profile;
    }

    public void DeleteUser(string username, string password)
    {
        if (!UserExists(username))
            throw new InvalidOperationException($"User '{username}' does not exist.");

        var user = GetUser(username);
        if (user == null || !VerifyPassword(password, user.Password))
            throw new InvalidOperationException("Invalid password.");

        string userDir = Path.Combine(_usersPath, username);
        Directory.Delete(userDir, true);
        _users.Remove(username);
    }

    public List<string> ListUsers()
    {
        return _users.Keys.ToList();
    }

    public bool VerifyPassword(string plainPassword, string encryptedPassword)
    {
        string encrypted = Encrypt.EncryptText(plainPassword, 0);
        return encrypted == encryptedPassword;
    }

    public UserProfile? AuthenticateUser(string username, string password)
    {
        if (!UserExists(username))
            return null;

        var user = GetUser(username);
        if (user != null && VerifyPassword(password, user.Password))
            return user;

        return null;
    }

    public string GetUserRole(string username)
    {
        var user = GetUser(username);
        return user?.Role ?? "user";
    }

    public string GetUserPromptColor(string username)
    {
        var user = GetUser(username);
        return user?.PromptColor ?? "green";
    }
}

public class UserProfile
{
    public string Username { get; set; } = string.Empty;
    public string Password { get; set; } = string.Empty;
    public string Role { get; set; } = "user";
    public string PromptColor { get; set; } = "green";
}
