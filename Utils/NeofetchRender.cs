using System;
using System.IO;
using System.Text.Json;
using Nexus.FileSystem;
using Nexus.Machine;

namespace Nexus.Utils;

public static class NeofetchRender
{
    public static string Render(string machineName)
    {
        var machineManager = new MachineManager();
        string machinePath = machineManager.GetMachinePath(machineName);
        string configPath = Path.Combine(machinePath, "config.json");

        var osName = System.Runtime.InteropServices.RuntimeInformation.OSDescription;
        var arch = System.Runtime.InteropServices.RuntimeInformation.OSArchitecture.ToString();
        var dotnet = System.Runtime.InteropServices.RuntimeInformation.FrameworkDescription;
        var cpuCount = System.Environment.ProcessorCount;
        var hostname = System.Environment.MachineName;
        var username = System.Environment.UserName;
        var uptime = GetUptime();
        var totalRamMb = GC.GetGCMemoryInfo().TotalAvailableMemoryBytes / 1024 / 1024;
        var usedRamMb = System.Environment.WorkingSet / 1024 / 1024;
        var storage = machinePath;

        string[] logo = {
            "  ██╗  ██╗",
            "  ██║  ██║",
            "  ███╗ ██║",
            "  ████╗██║",
            "  ██╔████║",
            "  ██║╠███║",
            "  ██║ ╠██║",
            "  ██║  ██║",
        };

        string colorCode = GetFetchColorCode(configPath);

        string[] info = {
            $"{username}@{hostname}",
            $"{new string('─', (username + hostname).Length + 1)}",
            $"OS {osName} ({arch})",
            $"Runtime {dotnet}",
            $"CPU {cpuCount} logical cores",
            $"Memory {usedRamMb} MiB / {totalRamMb} MiB",
            $"Uptime {uptime}",
            $"Storage {storage}",
        };

        string[] labels = { "", "", "OS", "Runtime", "CPU", "Memory", "Uptime", "Storage" };

        var output = new System.Text.StringBuilder();
        output.AppendLine();

        for (int i = 0; i < logo.Length; i++)
        {
            output.Append(colorCode);
            output.Append(logo[i]);
            output.Append("{RESET}");
            output.Append("     ");

            if (i < info.Length)
            {
                if (i < 2)
                {
                    output.Append(info[i]);
                }
                else
                {
                    output.Append(colorCode);
                    output.Append(labels[i]);
                    output.Append("{RESET}");
                    output.Append("{WHITE}");
                    int labelLen = labels[i].Length;
                    output.Append(info[i].Substring(labelLen));
                    output.Append("{RESET}");
                }
            }

            output.AppendLine();
        }

        output.AppendLine();
        return output.ToString();
    }

    private static string GetFetchColorCode(string configPath)
    {
        try
        {
            if (File.Exists(configPath))
            {
                string json = EncryptedFileHandler.ReadEncryptedFile(configPath);
                using (JsonDocument doc = JsonDocument.Parse(json))
                {
                    if (doc.RootElement.TryGetProperty("fetchColor", out var colorElement))
                    {
                        string color = colorElement.GetString()?.ToLower() ?? "red";
                        return color switch
                        {
                            "red" => "{RED}",
                            "green" => "{GREEN}",
                            "blue" => "{BLUE}",
                            "aqua" => "{CYAN}",
                            "yellow" => "{YELLOW}",
                            "gray" => "{GRAY}",
                            "white" => "{WHITE}",
                            "purple" => "{MAGENTA}",
                            _ => "{RED}"
                        };
                    }
                }
            }
        }
        catch { }
        return "{RED}";
    }

    private static string GetUptime()
    {
        try
        {
            var ts = TimeSpan.FromMilliseconds(Environment.TickCount64);
            return ts.Days > 0
                ? $"{ts.Days}d {ts.Hours}h {ts.Minutes}m"
                : $"{ts.Hours}h {ts.Minutes}m";
        }
        catch { return "unknown"; }
    }
}
