using System;
using System.Net;
using System.Text;
using System.Text.Json;
using System.Collections.Generic;
using System.IO;
using System.Linq;
using Nexus.Users;
using Nexus.FileSystem;
using Nexus.Encryption;
using Nexus.Machine;
using Nexus.Utils;

namespace Nexus.API;

public class NexusAPI
{
    private readonly HttpListener _listener;
    private readonly Dictionary<string, string> _tokens = new();
    private readonly Dictionary<string, UserContext> _tokenContexts = new();
    private readonly Dictionary<string, NexusSession> _sessions = new();
    private string _machinePath = string.Empty;
    private string _currentMachine = string.Empty;
    private bool _running = false;

    public NexusAPI(string machinePath, string currentMachine)
    {
        _machinePath = machinePath;
        _currentMachine = currentMachine;
        _listener = new HttpListener();
        _listener.Prefixes.Add("http://localhost:6969/");
    }

    public void Start()
    {
        if (_running)
            return;

        _listener.Start();
        _running = true;
        
        _ = Task.Run(() => ProcessRequests());
    }

    public void Stop()
    {
        _running = false;
        _listener?.Stop();
        _listener?.Close();
    }

    private async Task ProcessRequests()
    {
        while (_running)
        {
            try
            {
                HttpListenerContext context = await _listener.GetContextAsync();
                ProcessRequest(context);
            }
            catch { }
        }
    }

    private void ProcessRequest(HttpListenerContext context)
    {
        var request = context.Request;
        var response = context.Response;

        if (!IsLocalhost(request.RemoteEndPoint?.Address?.ToString() ?? ""))
        {
            response.StatusCode = 403;
            response.Close();
            return;
        }

        try
        {
            string path = request.Url?.AbsolutePath ?? "/";
            string method = request.HttpMethod ?? "GET";
            string body = ReadRequestBody(request);

            string responseBody = method switch
            {
                "POST" when path == "/login" => HandleLogin(body),
                "POST" when path == "/cmd" => HandleCmdOpen(body),
                "POST" when path == "/exec" => HandleCmdExec(body),
                "POST" when path == "/read" => HandleCmdRead(body),
                "POST" when path == "/close" => HandleCmdClose(body),
                "GET" when path == "/info/machine" => HandleMachineInfo(),
                "GET" when path == "/info/users" => HandleUsersInfo(),
                "POST" when path == "/crypto/encrypt" => HandleEncrypt(body),
                "POST" when path == "/crypto/decrypt" => HandleDecrypt(body),
                _ => "ERROR Not found"
            };

            response.ContentType = "text/plain";
            byte[] buffer = Encoding.UTF8.GetBytes(responseBody);
            response.ContentLength64 = buffer.Length;
            response.OutputStream.Write(buffer, 0, buffer.Length);
            response.Close();
        }
        catch (Exception ex)
        {
            var errorResponse = $"ERROR {ex.Message}";
            byte[] buffer = Encoding.UTF8.GetBytes(errorResponse);
            response.ContentType = "text/plain";
            response.ContentLength64 = buffer.Length;
            response.OutputStream.Write(buffer, 0, buffer.Length);
            response.Close();
        }
    }

    private string ReadRequestBody(HttpListenerRequest request)
    {
        if (request.ContentLength64 <= 0)
            return string.Empty;

        using var reader = new StreamReader(request.InputStream, Encoding.UTF8);
        return reader.ReadToEnd();
    }

    private bool IsLocalhost(string ip)
    {
        return ip == "127.0.0.1" || ip == "::1" || ip.StartsWith("127.");
    }

    private string HandleLogin(string body)
    {
        var parts = body.Trim().Split(' ', StringSplitOptions.RemoveEmptyEntries).ToList();
        
        Console.WriteLine($"[DEBUG] Body: '{body}'");
        Console.WriteLine($"[DEBUG] Parts count: {parts.Count}");
        foreach (var p in parts)
            Console.WriteLine($"[DEBUG] Part: '{p}'");
        
        if (parts.Count < 3 || parts[0].ToUpper() != "LOGIN")
            return "ERROR LOGIN username password";

        string username = parts[1];
        string password = parts[2];

        Console.WriteLine($"[DEBUG] Username: '{username}', Password: '{password}'");

        var user = UserManager.Instance.AuthenticateUser(username, password);
        Console.WriteLine($"[DEBUG] Auth result: {(user != null ? "OK" : "FAILED")}");
        
        if (user == null)
            return "ERROR Invalid credentials";

        string token = Guid.NewGuid().ToString();
        _tokens[token] = username;
        _tokenContexts[token] = new UserContext
        {
            Username = username,
            Machine = _currentMachine,
            Role = user.Role
        };

        return $"OK {token}";
    }

    private string HandleCmdOpen(string body)
    {
        var parts = body.Trim().Split(' ', StringSplitOptions.RemoveEmptyEntries).ToList();
        
        if (parts.Count < 2 || parts[0].ToUpper() != "CMD")
            return "ERROR CMD token";

        string token = parts[1];
        if (!_tokenContexts.TryGetValue(token, out var context))
            return "ERROR Unauthorized";

        string cmdId = Guid.NewGuid().ToString();
        var session = new NexusSession
        {
            Id = cmdId,
            Username = context.Username,
            Machine = context.Machine,
            Role = context.Role,
            CurrentDir = _machinePath
        };

        string neofetch = NeofetchRender.Render(context.Machine);
        session.OutputBuffer = neofetch;

        _sessions[cmdId] = session;

        return $"OK {cmdId}\n{neofetch}";
    }

    private string HandleCmdExec(string body)
    {
        var parts = body.Trim().Split(new[] { ' ' }, 3, StringSplitOptions.RemoveEmptyEntries).ToList();
        
        if (parts.Count < 3 || parts[0].ToUpper() != "EXEC")
            return "ERROR EXEC cmdid command";

        string cmdId = parts[1];
        string command = parts[2];

        if (!_sessions.TryGetValue(cmdId, out var session))
            return "ERROR Session not found";

        session.ExecuteCommand(command);

        return $"OK\n{session.OutputBuffer}";
    }

    private string HandleCmdRead(string body)
    {
        var parts = body.Trim().Split(' ', StringSplitOptions.RemoveEmptyEntries).ToList();
        
        if (parts.Count < 2 || parts[0].ToUpper() != "READ")
            return "ERROR READ cmdid";

        string cmdId = parts[1];
        if (!_sessions.TryGetValue(cmdId, out var session))
            return "ERROR Session not found";

        return $"OK\n{session.OutputBuffer}";
    }

    private string HandleCmdClose(string body)
    {
        var parts = body.Trim().Split(' ', StringSplitOptions.RemoveEmptyEntries).ToList();
        
        if (parts.Count < 2 || parts[0].ToUpper() != "CLOSE")
            return "ERROR CLOSE cmdid";

        string cmdId = parts[1];
        _sessions.Remove(cmdId);

        return "OK";
    }

    private string HandleMachineInfo()
    {
        var info = new
        {
            os = System.Runtime.InteropServices.RuntimeInformation.OSDescription,
            arch = System.Runtime.InteropServices.RuntimeInformation.OSArchitecture.ToString(),
            dotnet = System.Runtime.InteropServices.RuntimeInformation.FrameworkDescription,
            cpuCores = System.Environment.ProcessorCount,
            hostname = System.Environment.MachineName,
            workingSetMb = System.Environment.WorkingSet / 1024 / 1024,
            totalMemoryMb = GC.GetGCMemoryInfo().TotalAvailableMemoryBytes / 1024 / 1024,
            uptimeSeconds = Environment.TickCount64 / 1000
        };
        
        return $"OK\n{JsonSerializer.Serialize(info)}";
    }

    private string HandleUsersInfo()
    {
        var users = UserManager.Instance.ListUsers().Select(username => new
        {
            username = username,
            role = UserManager.Instance.GetUserRole(username)
        }).ToList();
        
        return $"OK\n{JsonSerializer.Serialize(users)}";
    }

    private string HandleEncrypt(string body)
    {
        var parts = body.Trim().Split(new[] { ' ' }, 2, StringSplitOptions.RemoveEmptyEntries).ToList();
        
        if (parts.Count < 2 || parts[0].ToUpper() != "ENCRYPT")
            return "ERROR ENCRYPT text";
        
        string text = parts[1];
        string encrypted = Encrypt.EncryptText(text);
        
        return $"OK\n{encrypted}";
    }

    private string HandleDecrypt(string body)
    {
        var parts = body.Trim().Split(new[] { ' ' }, 2, StringSplitOptions.RemoveEmptyEntries).ToList();
        
        if (parts.Count < 2 || parts[0].ToUpper() != "DECRYPT")
            return "ERROR DECRYPT encrypted";
        
        string encrypted = parts[1];
        string decrypted = Decrypt.DecryptText(encrypted);
        
        return $"OK\n{decrypted}";
    }
}

public class UserContext
{
    public string Username { get; set; } = string.Empty;
    public string Machine { get; set; } = string.Empty;
    public string Role { get; set; } = "user";
}

public class LoginRequest { public string? Username { get; set; } public string? Password { get; set; } }
public class EncryptRequest { public string? Token { get; set; } public string? Data { get; set; } }
public class DecryptRequest { public string? Token { get; set; } public string? Data { get; set; } }
public class BackupRequest { public string? Token { get; set; } }
public class BackupDeleteRequest { public string? Token { get; set; } public string? BackupName { get; set; } }
public class CmdRequest { public string? Token { get; set; } }
public class CmdExecRequest { public string? CmdId { get; set; } public string? Command { get; set; } }
public class CmdReadRequest { public string? CmdId { get; set; } }
public class CmdCloseRequest { public string? CmdId { get; set; } }
public class CmdListRequest { public string? Token { get; set; } }
public class BootRequest { public string? Token { get; set; } }