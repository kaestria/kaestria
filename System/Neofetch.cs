using System;
using System.IO;
using System.Text.Json;
using Nexus.Machine;
using Nexus.FileSystem;

namespace Nexus.Utils;

public static class Neofetch
{
    public static void Display(string machineName)
    {
        Console.OutputEncoding = System.Text.Encoding.UTF8;

        var machineManager = new MachineManager();
        string machinePath = machineManager.GetMachinePath(machineName);
        string configPath = Path.Combine(machinePath, "config.json");

        Console.Clear();

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

        ConsoleColor fetchColor = GetFetchColor(configPath);

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

        Console.WriteLine();
        for (int i = 0; i < logo.Length; i++)
        {
            Console.ForegroundColor = fetchColor;
            Console.Write(logo[i]);
            Console.ResetColor();

            Console.Write("     ");
            if (i < info.Length)
            {
                if (i < 2)
                {
                    Console.Write(info[i]);
                }
                else
                {
                    Console.ForegroundColor = fetchColor;
                    Console.Write(labels[i]);
                    Console.ResetColor();
                    Console.ForegroundColor = ConsoleColor.White;
                    int labelLen = labels[i].Length;
                    Console.Write(info[i].Substring(labelLen));
                    Console.ResetColor();
                }
            }

            Console.WriteLine();
        }

        Console.WriteLine();
    }

    private static ConsoleColor GetFetchColor(string configPath)
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
                            "red" => ConsoleColor.Red,
                            "green" => ConsoleColor.Green,
                            "blue" => ConsoleColor.Blue,
                            "aqua" => ConsoleColor.Cyan,
                            "yellow" => ConsoleColor.Yellow,
                            "gray" => ConsoleColor.Gray,
                            "white" => ConsoleColor.White,
                            "purple" => ConsoleColor.Magenta,
                            _ => ConsoleColor.Red
                        };
                    }
                }
            }
        }
        catch { }
        return ConsoleColor.Red;
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
