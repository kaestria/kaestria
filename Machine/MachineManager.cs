using System;
using System.IO;
using System.Text.Json;
using System.Collections.Generic;
using System.Linq;
using Nexus.FileSystem;

namespace Nexus.Machine;

public class MachineManager
{
    private readonly string _nexusRoot = @"C:\nexus";
    
    public MachineManager()
    {
        if (!Directory.Exists(_nexusRoot))
        {
            Directory.CreateDirectory(_nexusRoot);
        }
    }

    public string SelectBoot()
    {
        var machines = GetMachineList();
        
        if (machines.Count == 0)
        {
            CreateDefaultMachine();
            machines = GetMachineList();
        }

        Console.Clear();
        Console.WriteLine("Choose a boot:\n");
        
        for (int i = 0; i < machines.Count; i++)
        {
            string defaultLabel = machines[i].Name == "machine" ? " (Default)" : "";
            Console.WriteLine($"({i}) {machines[i].Name}{defaultLabel}");
        }

        Console.WriteLine();
        string? input;
        int selectedIndex = -1;

        while (true)
        {
            Console.Write("> ");
            input = Console.ReadLine();

            if (int.TryParse(input, out selectedIndex) && selectedIndex >= 0 && selectedIndex < machines.Count)
            {
                break;
            }

            Console.WriteLine("Invalid selection. Try again.");
        }

        string selectedMachine = machines[selectedIndex].Name;
        DisplayBootProgress(selectedMachine);
        return selectedMachine;
    }

    private List<(string Name, DateTime Created)> GetMachineList()
    {
        var machines = new List<(string Name, DateTime Created)>();

        if (!Directory.Exists(_nexusRoot))
            return machines;

        var dirs = Directory.GetDirectories(_nexusRoot);
        
        foreach (var dir in dirs)
        {
            var dirInfo = new DirectoryInfo(dir);
            var name = dirInfo.Name;
            var created = dirInfo.CreationTime;
            machines.Add((name, created));
        }

        machines = machines.OrderBy(m => m.Created).ToList();
        return machines;
    }

    private void CreateDefaultMachine()
    {
        string machinePath = Path.Combine(_nexusRoot, "machine");
        
        if (!Directory.Exists(machinePath))
        {
            Directory.CreateDirectory(machinePath);
            Directory.CreateDirectory(Path.Combine(machinePath, "OS"));
            Directory.CreateDirectory(Path.Combine(machinePath, "Users"));

            var config = new
            {
                machineName = "machine",
                fetchColor = "red",
                created = DateTime.Now
            };

            string configPath = Path.Combine(machinePath, "config.json");
            string configJson = JsonSerializer.Serialize(config, new JsonSerializerOptions { WriteIndented = true });
            EncryptedFileHandler.WriteEncryptedFile(configPath, configJson);
        }
    }

    private void DisplayBootProgress(string machineName)
    {
        Console.WriteLine();
        Console.Write($"Starting {machineName}... ");

        for (int i = 0; i <= 100; i += 10)
        {
            Console.Write($"\r{new string('█', i / 10)}{new string('░', 10 - i / 10)}");
            System.Threading.Thread.Sleep(50);
        }

        Console.WriteLine();
        Console.WriteLine();
    }

    public string GetMachinePath(string machineName)
    {
        return Path.Combine(_nexusRoot, machineName);
    }

    public bool MachineExists(string machineName)
    {
        string path = GetMachinePath(machineName);
        return Directory.Exists(path);
    }

    public void CreateMachine(string machineName)
    {
        if (MachineExists(machineName))
        {
            throw new InvalidOperationException($"Machine '{machineName}' already exists.");
        }

        string machinePath = GetMachinePath(machineName);
        Directory.CreateDirectory(machinePath);
        Directory.CreateDirectory(Path.Combine(machinePath, "OS"));
        Directory.CreateDirectory(Path.Combine(machinePath, "Users"));

        var config = new
        {
            machineName = machineName,
            fetchColor = "red",
            created = DateTime.Now
        };

        string configPath = Path.Combine(machinePath, "config.json");
        string configJson = JsonSerializer.Serialize(config, new JsonSerializerOptions { WriteIndented = true });
        EncryptedFileHandler.WriteEncryptedFile(configPath, configJson);
    }

    public void DeleteMachine(string machineName)
    {
        if (!MachineExists(machineName))
        {
            throw new InvalidOperationException($"Machine '{machineName}' does not exist.");
        }

        string machinePath = GetMachinePath(machineName);
        Directory.Delete(machinePath, true);
    }

    public List<string> ListMachines()
    {
        return GetMachineList().Select(m => m.Name).ToList();
    }
}
